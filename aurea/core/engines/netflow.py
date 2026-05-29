"""
aurea.core.engines.netflow — Decoupled NetFlow v5 Parser and Collector Daemon.
"""

import time
import socket
import struct
import threading
import queue
import ipaddress
from datetime import datetime


def _is_private_ip(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
        return ip.is_private
    except Exception:
        return False


class NetFlowCollector:
    """
    High-performance, thread-safe, decoupled NetFlow v5 Collector Daemon.
    Handles background socket ingestion, binary parsing, heuristics, and snapshots.
    """

    def __init__(self, port: int = 2055, ip_filter: str | None = None, port_filter: int | None = None, proto_filter: str | None = None):
        self.port = port
        self.ip_filter = ip_filter
        self.port_filter = port_filter
        self.proto_filter = proto_filter.lower() if proto_filter else None
        self.active = False
        self.lock = threading.Lock()
        self.packet_queue = queue.Queue(maxsize=10000)
        self.scan_tracker = {}
        self.scan_tracker_lock = threading.Lock()
        
        # Core metrics snapshot
        self.stats = {
            "total_bytes": 0,
            "down_bytes": 0,
            "up_bytes": 0,
            "talkers": {},
            "protocols": {
                "tcp": 0,
                "udp": 0,
                "icmp": 0,
                "other": 0
            },
            "ports": {},
            "interfaces": {},
            "alerts": [],
            "down_rate_kbps": 0.0,
            "up_rate_kbps": 0.0,
            "last_reset": time.time(),
            "window_down_bytes": 0,
            "window_up_bytes": 0,
            "exporters": {}
        }

        self._listener_thread = None
        self._parser_thread = None
        self._arp_cache = {}
        self._last_arp_update = 0.0

    def start(self) -> bool:
        """Start the background collector threads."""
        self.active = True
        
        # Create and bind socket here (fail fast and avoid race conditions)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024 * 1024 * 4) # 4MB buffer
            sock.bind(("0.0.0.0", self.port))
        except Exception as e:
            self.active = False
            sock.close()
            raise OSError(f"Failed to bind UDP port {self.port}: {e}")

        self._parser_thread = threading.Thread(target=self._parser_worker, daemon=True)
        self._parser_thread.start()

        self._listener_thread = threading.Thread(target=self._udp_listener, args=(sock,), daemon=True)
        self._listener_thread.start()
        
        return True

    def stop(self):
        """Shut down the background collector cleanly."""
        self.active = False
        # Clear queue to wake up parser thread if blocked
        while not self.packet_queue.empty():
            try:
                self.packet_queue.get_nowait()
                self.packet_queue.task_done()
            except queue.Empty:
                break
        
        # Wait briefly for threads to settle
        if self._listener_thread:
            self._listener_thread.join(timeout=0.2)
        if self._parser_thread:
            self._parser_thread.join(timeout=0.2)

    def get_snapshot(self) -> dict:
        """Return a thread-safe deep snapshot of current stats with calculated throughput rates."""
        now = time.time()
        
        # Update rates & ARP cache
        with self.lock:
            dt = now - self.stats["last_reset"]
            if dt > 0.5:
                self.stats["down_rate_kbps"] = (self.stats["window_down_bytes"] * 8) / (dt * 1024)
                self.stats["up_rate_kbps"] = (self.stats["window_up_bytes"] * 8) / (dt * 1024)
                self.stats["window_down_bytes"] = 0
                self.stats["window_up_bytes"] = 0
                self.stats["last_reset"] = now
                
                # Dynamic exporter rate calculations
                for exp_ip, exp_data in self.stats["exporters"].items():
                    w_bytes = exp_data.get("window_bytes", 0)
                    exp_data["rate_kbps"] = (w_bytes * 8) / (dt * 1024)
                    exp_data["window_bytes"] = 0
                    
                    # Lazy-load/OUI-lookup for newly registered exporters
                    if exp_data.get("vendor") in ("Desconhecido", "Unknown", "Network Device", "N/A"):
                        if now - self._last_arp_update > 15.0:
                            try:
                                from aurea.core.arp import parse_system_arp_table
                                self._arp_cache = parse_system_arp_table()
                                self._last_arp_update = now
                            except Exception:
                                pass
                        
                        if exp_ip in self._arp_cache:
                            mac = self._arp_cache[exp_ip]
                            try:
                                from aurea.core.arp import get_vendor_by_mac
                                exp_data["vendor"] = get_vendor_by_mac(mac)
                            except Exception:
                                exp_data["vendor"] = "Local Device"
                        else:
                            exp_data["vendor"] = "Network Device"

            # Create deep/safe snapshot copy
            snapshot = {
                "total_bytes": self.stats["total_bytes"],
                "down_bytes": self.stats["down_bytes"],
                "up_bytes": self.stats["up_bytes"],
                "down_rate_kbps": self.stats["down_rate_kbps"],
                "up_rate_kbps": self.stats["up_rate_kbps"],
                "protocols": dict(self.stats["protocols"]),
                "alerts": list(self.stats["alerts"]),
                "exporters": {
                    ip: dict(data) for ip, data in self.stats["exporters"].items()
                },
                "talkers": sorted(
                    self.stats["talkers"].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10],
                "ports": sorted(
                    self.stats["ports"].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:6],
                "interfaces": sorted(
                    self.stats["interfaces"].items(),
                    key=lambda x: x[1]["in_bytes"] + x[1]["out_bytes"],
                    reverse=True
                )[:5]
            }
            
        return snapshot

    def _udp_listener(self, sock: socket.socket):
        sock.settimeout(0.5)

        while self.active:
            try:
                payload, client_addr = sock.recvfrom(2048)
                if not self.active:
                    break
                try:
                    self.packet_queue.put_nowait((payload, client_addr))
                except queue.Full:
                    pass
            except socket.timeout:
                continue
            except Exception:
                continue

        sock.close()

    def _parser_worker(self):
        while self.active:
            try:
                payload, client_addr = self.packet_queue.get(timeout=0.5)
            except queue.Empty:
                continue
                
            if len(payload) < 24:
                self.packet_queue.task_done()
                continue
                
            try:
                exp_ip = client_addr[0]
                header = struct.unpack("!HHIIIIBBH", payload[:24])
                version = header[0]
                count = header[1]
                
                if version != 5:
                    self.packet_queue.task_done()
                    continue
                    
                offset = 24
                record_size = 48
                
                with self.lock:
                    if exp_ip not in self.stats["exporters"]:
                        self.stats["exporters"][exp_ip] = {
                            "bytes": 0,
                            "packets": 0,
                            "last_seen": time.time(),
                            "vendor": "Unknown",
                            "rate_kbps": 0.0,
                            "window_bytes": 0
                        }
                        
                    self.stats["exporters"][exp_ip]["last_seen"] = time.time()
                    self.stats["exporters"][exp_ip]["packets"] += count
                    
                    for _ in range(count):
                        if offset + record_size > len(payload):
                            break
                            
                        record_bytes = payload[offset : offset + record_size]
                        offset += record_size
                        
                        r = struct.unpack("!IIIHHIIIIHHBBBBHHBBH", record_bytes)
                        
                        src_ip = str(ipaddress.IPv4Address(r[0]))
                        dst_ip = str(ipaddress.IPv4Address(r[1]))
                        bytes_cnt = r[6]
                        dst_port = r[10]
                        dst_port_int = int(dst_port)
                        prot = r[13]
                        
                        # Apply NOC Filters
                        if self.ip_filter and self.ip_filter not in (src_ip, dst_ip):
                            continue
                        if self.port_filter and self.port_filter != dst_port_int:
                            continue
                        if self.proto_filter:
                            if self.proto_filter == "tcp" and prot != 6:
                                continue
                            elif self.proto_filter == "udp" and prot != 17:
                                continue
                            elif self.proto_filter == "icmp" and prot != 1:
                                continue
                        
                        self.stats["total_bytes"] += bytes_cnt
                        self.stats["exporters"][exp_ip]["bytes"] += bytes_cnt
                        self.stats["exporters"][exp_ip]["window_bytes"] += bytes_cnt
                        
                        input_if = int(r[3])
                        output_if = int(r[4])
                        
                        if input_if not in self.stats["interfaces"]:
                            self.stats["interfaces"][input_if] = {"in_bytes": 0, "out_bytes": 0}
                        if output_if not in self.stats["interfaces"]:
                            self.stats["interfaces"][output_if] = {"in_bytes": 0, "out_bytes": 0}
                            
                        self.stats["interfaces"][input_if]["in_bytes"] += bytes_cnt
                        self.stats["interfaces"][output_if]["out_bytes"] += bytes_cnt
                        
                        is_down = _is_private_ip(dst_ip)
                        if is_down:
                            self.stats["down_bytes"] += bytes_cnt
                            self.stats["window_down_bytes"] += bytes_cnt
                        else:
                            self.stats["up_bytes"] += bytes_cnt
                            self.stats["window_up_bytes"] += bytes_cnt
                            
                        talker_ip = dst_ip if is_down else src_ip
                        if talker_ip != "0.0.0.0":
                            self.stats["talkers"][talker_ip] = self.stats["talkers"].get(talker_ip, 0) + bytes_cnt
                            
                        if prot == 6:
                            self.stats["protocols"]["tcp"] += bytes_cnt
                        elif prot == 17:
                            self.stats["protocols"]["udp"] += bytes_cnt
                        elif prot == 1:
                            self.stats["protocols"]["icmp"] += bytes_cnt
                        else:
                            self.stats["protocols"]["other"] += bytes_cnt
                            
                        port_key = str(dst_port)
                        self.stats["ports"][port_key] = self.stats["ports"].get(port_key, 0) + bytes_cnt
                        
                        # Heuristics: Port Scan Detector
                        if _is_private_ip(src_ip):
                            with self.scan_tracker_lock:
                                if src_ip not in self.scan_tracker:
                                    self.scan_tracker[src_ip] = {"ports": set(), "timestamp": time.time()}
                                
                                tracker = self.scan_tracker[src_ip]
                                if time.time() - tracker["timestamp"] > 10.0:
                                    tracker["ports"] = set()
                                    tracker["timestamp"] = time.time()
                                    
                                tracker["ports"].add(dst_port_int)
                                
                                if len(tracker["ports"]) > 15:
                                    alert_desc = f"Varredura local de {src_ip} em {len(tracker['ports'])} portas em <10s!"
                                    exists = any(a["desc"] == alert_desc for a in self.stats["alerts"])
                                    if not exists:
                                        self.stats["alerts"].append({
                                            "desc": alert_desc,
                                            "timestamp": datetime.now().strftime("%H:%M:%S")
                                        })
                                        if len(self.stats["alerts"]) > 8:
                                            self.stats["alerts"].pop(0)
                                    tracker["ports"] = set()
                                    
                    # Cap top talkers list size in memory
                    if len(self.stats["talkers"]) > 100:
                        sorted_t = sorted(self.stats["talkers"].items(), key=lambda x: x[1], reverse=True)[:50]
                        self.stats["talkers"] = dict(sorted_t)
                        
            except Exception:
                pass
                
            self.packet_queue.task_done()
