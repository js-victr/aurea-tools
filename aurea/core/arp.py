"""
aurea.core.arp — ARP table parsing and OUI vendor lookup.

Moved from tools/automation to core to fix architectural layer violation.
"""

import re
import subprocess

from aurea.core.platform_info import is_windows


# Expanded OUI database (~50 common network equipment vendors)
OUI_DATABASE = {
    # Cisco
    "00:1A:A1": "Cisco", "00:1B:D4": "Cisco", "00:26:CB": "Cisco",
    "00:0C:29": "VMware", "00:50:56": "VMware", "00:0C:30": "Cisco",
    "00:1C:58": "Cisco", "00:23:04": "Cisco", "00:25:45": "Cisco",
    # MikroTik
    "48:8F:5A": "MikroTik", "48:A9:8A": "MikroTik", "64:D1:54": "MikroTik",
    "CC:2D:E0": "MikroTik", "E4:8D:8C": "MikroTik", "74:4D:28": "MikroTik",
    "2C:C8:1B": "MikroTik", "6C:3B:6B": "MikroTik", "B8:69:F4": "MikroTik",
    "D4:CA:6D": "MikroTik", "18:FD:74": "MikroTik",
    # Ubiquiti
    "FC:EC:DA": "Ubiquiti", "04:18:D6": "Ubiquiti", "24:5A:4C": "Ubiquiti",
    "68:72:51": "Ubiquiti", "78:8A:20": "Ubiquiti", "80:2A:A8": "Ubiquiti",
    "F0:9F:C2": "Ubiquiti", "44:D9:E7": "Ubiquiti",
    # TP-Link
    "50:C7:BF": "TP-Link", "54:C8:0F": "TP-Link", "E8:48:B8": "TP-Link",
    "C0:25:E9": "TP-Link", "14:EB:B6": "TP-Link",
    # Huawei
    "48:46:FB": "Huawei", "88:66:A5": "Huawei", "E0:24:7F": "Huawei",
    "00:E0:FC": "Huawei", "AC:85:3D": "Huawei",
    # Juniper
    "00:05:85": "Juniper", "00:12:1E": "Juniper", "00:1F:12": "Juniper",
    "28:C0:DA": "Juniper", "40:B4:F0": "Juniper",
    # Dell / Dell EMC
    "00:14:22": "Dell", "24:6E:96": "Dell", "F8:DB:88": "Dell",
    # HP / Aruba
    "00:1E:0B": "HP", "3C:D9:2B": "HP/Aruba", "00:0B:86": "HP/Aruba",
    "94:57:A5": "HP/Aruba", "D8:C7:C8": "HP/Aruba",
    # Arista
    "00:1C:73": "Arista", "28:99:3A": "Arista",
    # Fortinet
    "00:09:0F": "Fortinet", "70:4C:A5": "Fortinet",
    # Intel
    "00:1B:21": "Intel", "68:05:CA": "Intel",
    # Realtek
    "52:54:00": "QEMU/KVM", "00:E0:4C": "Realtek",
    # Apple
    "A4:83:E7": "Apple", "3C:22:FB": "Apple",
    # Samsung
    "00:16:32": "Samsung", "D0:22:BE": "Samsung",
    # Ruckus
    "00:25:C4": "Ruckus", "C4:10:8A": "Ruckus",
    # Extreme
    "00:04:96": "Extreme",
    # ZTE
    "00:19:C6": "ZTE", "00:1E:73": "ZTE",
    # Datacom
    "00:04:2B": "Datacom",
    # Intelbras
    "28:30:AC": "Intelbras",
    # Palo Alto
    "00:1B:17": "Palo Alto",
}


def get_vendor_by_mac(mac: str) -> str:
    """Lookup vendor name from MAC address using local OUI database."""
    if not mac or len(mac) < 8:
        return "Unknown"
    prefix = mac.upper().replace("-", ":")[:8]
    vendor = OUI_DATABASE.get(prefix, "Unknown")
    try:
        from aurea.core.ui import verbose
        verbose(f"Consulta OUI: MAC prefixo {prefix} -> Fabricante: {vendor}")
    except Exception:
        pass
    return vendor


def parse_system_arp_table() -> dict[str, str]:
    """
    Parse the OS ARP table and return {ip: mac} mapping.
    Cross-platform: Windows (arp -a) and Linux (ip neigh / arp -a).
    """
    try:
        from aurea.core.ui import verbose
        verbose("Lendo tabela ARP nativa do sistema operacional para indexar vizinhos locais...")
    except Exception:
        pass
        
    arp_map = {}
    try:
        if is_windows():
            output = subprocess.check_output(
                ["arp", "-a"], text=True, stderr=subprocess.DEVNULL, timeout=5
            )
            for line in output.splitlines():
                parts = line.split()
                if len(parts) >= 3:
                    ip, mac = parts[0], parts[1]
                    if re.match(r"\d+\.\d+\.\d+\.\d+", ip) and ":" in mac or "-" in mac:
                        arp_map[ip] = mac.upper().replace("-", ":")
        else:
            # Try 'ip neigh' first (modern Linux), fall back to 'arp -a'
            try:
                output = subprocess.check_output(
                    ["ip", "neigh"], text=True, stderr=subprocess.DEVNULL, timeout=5
                )
                for line in output.splitlines():
                    parts = line.split()
                    if len(parts) >= 5 and parts[3] == "lladdr":
                        arp_map[parts[0]] = parts[4].upper()
            except Exception:
                output = subprocess.check_output(
                    ["arp", "-a"], text=True, stderr=subprocess.DEVNULL, timeout=5
                )
                for line in output.splitlines():
                    m = re.search(r"\((\d+\.\d+\.\d+\.\d+)\)\s+at\s+([0-9a-fA-F:]+)", line)
                    if m:
                        arp_map[m.group(1)] = m.group(2).upper()
    except Exception as e:
        try:
            from aurea.core.ui import verbose
            verbose(f"Falha ao ler tabela ARP: {e}")
        except Exception:
            pass
            
    try:
        from aurea.core.ui import verbose
        verbose(f"Tabela ARP processada: {len(arp_map)} vizinhos IP/MAC mapeados localmente.")
    except Exception:
        pass
    return arp_map
