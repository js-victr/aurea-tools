"""
aurea.tools.automation — Category 4: NOC Utilities & Automation tools.
"""

import platform
import re
import socket

import time
import subprocess
import urllib.request
import urllib.parse
import ssl
import json
import ipaddress
import concurrent.futures
from datetime import datetime
from pathlib import Path

from aurea.core.colors import blue, green, red, yellow, cyan, bold, dim, c
from aurea.core import platform_info, ui, validators, http_client, network
from aurea.i18n import t
from aurea.core.arp import get_vendor_by_mac, parse_system_arp_table
from aurea.tools import tool


@tool(
    number="23",
    name="LAN Device Scanner",
    category="automation",
    keywords=["arp", "lan", "scanner", "devices", "discovery"],
    tier="free",
    i18n_key="tools.lan_scan.name"
)
def lan_scan():
    ui.header(t("tools.lan_scan.title"))
    print(f"\n{blue(t('tools.lan_scan.searching'))}")
    
    comando = ["arp", "-a"] if platform_info.is_windows() else ["ip", "neigh", "show"]
    resultado = ui.run_command_safe(comando)
    
    if not resultado or resultado.returncode != 0:
        print(f"  {blue('✗')} {t('tools.lan_scan.error')}")
        ui.pause()
        return

    linhas = resultado.stdout.split('\n')
    encontrou = False
    
    ip_col = t('tools.lan_scan.ip_col')
    mac_col = t('tools.lan_scan.mac_col')
    print(f"  {blue(f'{ip_col:<20}')}\t{blue(mac_col)}")
    print("  " + blue("─" * 45))
    
    regex_ip = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    regex_mac = r'\b(?:[0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}\b'

    for linha in linhas:
        linha_lower = linha.lower()
        if "255.255" in linha_lower or "ff-ff-ff-ff-ff-ff" in linha_lower or "ff:ff:ff:ff:ff:ff" in linha_lower or "multicast" in linha_lower:
            continue
            
        ip_match = re.search(regex_ip, linha)
        mac_match = re.search(regex_mac, linha)
        
        if ip_match and mac_match:
            ip = ip_match.group()
            mac = mac_match.group().replace('-', ':').upper()
            print(f"  {green(f'{ip:<20}')}\t{green(mac)}")
            encontrou = True

    if not encontrou:
        print(f"  {blue(t('tools.lan_scan.empty'))}")
        
    ui.pause()


@tool(
    number="24",
    name="Multithreaded Port Scanner",
    category="automation",
    keywords=["port", "scan", "multithread", "thread", "parallel", "services"],
    tier="free",
    i18n_key="tools.port_scanner.name",
    parameters=[
        {"name": "target", "label": "IP / Host / Destino", "default": "127.0.0.1", "type": "text"},
        {"name": "port", "label": "Portas (ex: 22,80,443 ou 1-1024)", "default": "1-1024", "type": "text"}
    ]
)
def port_scanner():
    ui.header(t("tools.port_scanner.title"))
    try:
        host = ui.input_with_default(t("ui.enter_ip"))
        if not host:
            print(f"  {red(t('ui.cancelled'))}")
            ui.pause()
            return
        host = validators.validate_host(host)
    except ValueError as e:
        print(f"  {red(str(e))}")
        ui.pause()
        return

    ports_input = ui.input_with_default(t("ui.enter_port"), "21,22,23,25,53,80,110,143,443,3389,8080")
    
    ports = []
    try:
        if "," in ports_input:
            ports = [validators.validate_port(p) for p in ports_input.split(",")]
        elif "-" in ports_input:
            start_p, end_p = ports_input.split("-")
            start = validators.validate_port(start_p)
            end = validators.validate_port(end_p)
            ports = list(range(start, end + 1))
        else:
            ports = [validators.validate_port(ports_input)]
    except ValueError as e:
        print(f"  {red(str(e))}")
        ui.pause()
        return

    print(f"\n{yellow(t('tools.port_scanner.scanning', host=host, ports=len(ports)))}\n")
    
    open_ports = []
    
    def scan_single_port(port: int):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.5)
            try:
                res = s.connect_ex((host, port))
                if res == 0:
                    service = network.WELL_KNOWN_PORTS.get(str(port), "Unknown")
                    print(f"  {green('✓')} {t('tools.port_scanner.open', port=port, service=service)}")
                    open_ports.append((port, service))
            except Exception:
                pass

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(scan_single_port, ports)
        
    print(f"\n{cyan('─' * 45)}")
    print(f"  {green('✓')} Varredura concluída. {len(open_ports)} portas abertas encontradas.")
    ui.pause()





def _ping_host(ip: str) -> tuple[str, bool]:
    """Ping a single host using platform native ping command."""
    is_win = platform.system() == "Windows"
    cmd = ["ping", "-n" if is_win else "-c", "1", "-w" if is_win else "-W", "600" if is_win else "1", ip]
    
    res = ui.run_command_safe(cmd)
    if res and res.returncode == 0:
        return ip, True
    return ip, False


def _resolve_ptr(ip: str) -> str:
    """Safely resolve IP PTR record locally."""
    try:
        host, _, _ = socket.gethostbyaddr(ip)
        return host
    except Exception:
        return "N/A"


@tool(
    number="25",
    name="LAN Auto-Discovery & NetBox Sync",
    category="automation",
    keywords=["discovery", "lan", "netbox", "sync", "subnet", "arp", "active"],
    tier="premium",
    i18n_key="tools.lan_discovery.name",
    parameters=[
        {"name": "cidr", "label": "Faixa CIDR de Varredura", "default": "192.168.0.0/24", "type": "text"}
    ]
)
def lan_discovery():
    ui.header(t("tools.lan_discovery.title"))
    print(cyan(t("tools.lan_discovery.desc") + "\n"))
    
    try:
        network_str = ui.input_with_default(t("ui.enter_cidr"), "192.168.0.0/24")
        if not network_str:
            print(f"  {red(t('ui.cancelled'))}")
            ui.pause()
            return
        network_str = validators.validate_cidr(network_str)
    except ValueError as e:
        print(f"  {red(str(e))}")
        ui.pause()
        return

    try:
        net = ipaddress.ip_network(network_str, strict=False)
    except Exception as e:
        print(f"  {red(str(e))}")
        ui.pause()
        return

    print(f"\n{yellow('Minerando cache ARP do sistema local...')}")
    arp_table = parse_system_arp_table()
    
    hosts_to_ping = [str(ip) for ip in net.hosts()]
    print(f"{yellow('Iniciando Ping Sweep paralelo em')} {len(hosts_to_ping)} endereços...")
    
    discovered_ips = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(_ping_host, ip) for ip in hosts_to_ping]
        for future in concurrent.futures.as_completed(futures):
            ip, is_online = future.result()
            if is_online:
                mac = arp_table.get(ip, "N/A")
                vendor = get_vendor_by_mac(mac) if mac != "N/A" else "Desconhecido"
                ptr = _resolve_ptr(ip)
                discovered_ips.append({
                    "ip": ip,
                    "mac": mac,
                    "vendor": vendor,
                    "ptr": ptr
                })
                print(f"  {green('✓')} Encontrado: {green(f'{ip:<15}')} | MAC: {cyan(mac)} | {yellow(vendor[:20])}")

    print(f"\n{green('✓ Varredura concluída!')} {len(discovered_ips)} IPs ativos encontrados.")
    
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_csv = f"aurea_inventario_{ts}.csv"
    try:
        import csv
        with open(nome_csv, mode='w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['IP', 'MAC', 'Fabricante', 'DNS_PTR'])
            for item in discovered_ips:
                writer.writerow([item["ip"], item["mac"], item["vendor"], item["ptr"]])
        print(f"  {green('✓')} Inventário de rede salvo: {yellow(nome_csv)}")
    except Exception as e:
        print(f"  {red(f'Erro ao gravar arquivo de inventário: {e}')}")

    sync_nb = ui.input_with_default("\nDeseja enviar/sincronizar estes IPs com o NetBox IPAM? (y/N)", "n").strip().lower()
    if sync_nb == "y":
        nb_url = ui.input_with_default("URL do NetBox (ex: http://localhost:8000)", "http://localhost:8000").strip()
        nb_token = ui.input_with_default("API Token do NetBox", "0123456789abcdef0123456789abcdef0123457").strip()
        
        if not nb_url or not nb_token:
            print(f"  {red('✗ URL ou Token ausentes. Cancelado.')}")
            ui.pause()
            return
            
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        endpoint = f"{nb_url.rstrip('/')}/api/ipam/ip-addresses/"
        headers = {
            "Authorization": f"Token {nb_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "AureaNOCDiscoverySync/2.2"
        }
        
        print(f"\n{blue('Sincronizando com o NetBox IPAM...')}")
        for item in discovered_ips:
            payload = {
                "address": f"{item['ip']}/{net.prefixlen}",
                "status": "active",
                "description": f"Imported via Aurea LAN Discovery. MAC: {item['mac']} ({item['vendor']})"
            }
            if item["ptr"] != "N/A":
                payload["dns_name"] = item["ptr"]
                
            try:
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(endpoint, data=data, headers=headers, method="POST")
                with urllib.request.urlopen(req, context=ctx, timeout=3.0) as resp:
                    if resp.status in (200, 201):
                        print(f"    {green('✓')} IP {item['ip']} enviado com sucesso!")
            except Exception as e:
                err_str = str(e)
                if "HTTP Error 400" in err_str:
                    print(f"    {yellow('⚠')} IP {item['ip']} já cadastrado no NetBox (Ignorado)")
                else:
                    print(f"    {red('✗')} Falha ao sincronizar IP {item['ip']}: {e}")
                    
        print(f"\n  {green('✓')} Sincronização com NetBox concluída!")
        
    ui.pause()


@tool(
    number="26",
    name="Config Diff Comparator",
    category="automation",
    keywords=["diff", "config", "compare", "router", "switch", "sidebyside"],
    tier="free",
    i18n_key="tools.config_diff.name",
    parameters=[
        {"name": "file1", "label": "Caminho do Arquivo A (Original)", "default": "", "type": "text"},
        {"name": "file2", "label": "Caminho do Arquivo B (Modificado)", "default": "", "type": "text"}
    ]
)
def config_diff():
    import difflib
    ui.header(t("tools.config_diff.title"))
    print(cyan(t("tools.config_diff.desc") + "\n"))
    
    f1_path = ui.input_with_default("Caminho do Arquivo A (Original)", "").strip()
    if not f1_path:
        print(f"  {red(t('ui.cancelled'))}")
        ui.pause()
        return
        
    f2_path = ui.input_with_default("Caminho do Arquivo B (Modificado)", "").strip()
    if not f2_path:
        print(f"  {red(t('ui.cancelled'))}")
        ui.pause()
        return
        
    try:
        with open(f1_path, "r", encoding="utf-8", errors="ignore") as f1:
            lines1 = f1.readlines()
        with open(f2_path, "r", encoding="utf-8", errors="ignore") as f2:
            lines2 = f2.readlines()
    except Exception as e:
        print(f"  {red(f'Erro ao ler arquivos: {e}')}")
        ui.pause()
        return
        
    print(f"\n{yellow('Gerando comparação de linhas...')}\n")
    
    diff = list(difflib.unified_diff(
        lines1, lines2, 
        fromfile=f1_path, tofile=f2_path, 
        n=3
    ))
    
    if not diff:
        print(f"  {green('✓ Os arquivos são 100% IDÊNTICOS. Nenhuma diferença encontrada.')}")
    else:
        print(cyan("═" * 80))
        print(bold("RELATÓRIO DE DIFERENÇAS (DIFF):"))
        print(cyan("═" * 80))
        for line in diff:
            line_str = line.rstrip("\r\n")
            if line.startswith("+") and not line.startswith("+++"):
                print(green(line_str))
            elif line.startswith("-") and not line.startswith("---"):
                print(red(line_str))
            elif line.startswith("@@"):
                print(cyan(line_str))
            else:
                print(line_str)
        print(cyan("═" * 80))
        
    ui.pause()


class TelnetClient:
    """Reusable clientless Telnet helper that correctly negotiates options and handles socket closure."""
    def __init__(self, host: str, port: int, timeout: float = 4.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.s = None

    def __enter__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(self.timeout)
        try:
            self.s.connect((self.host, self.port))
        except Exception as e:
            if self.s:
                self.s.close()
            raise ConnectionError(f"Falha de conexão Telnet: {e}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.s:
            self.s.close()

    def negotiate(self, cmd_bytes):
        if len(cmd_bytes) < 3:
            return
        cmd = cmd_bytes[1]
        opt = cmd_bytes[2]
        resp = bytearray()
        if cmd == 253:  # DO
            if opt in (1, 3):  # ECHO, SGA
                resp.extend([255, 251, opt])  # WILL
            else:
                resp.extend([255, 252, opt])  # WONT
        elif cmd == 254:  # DONT
            resp.extend([255, 252, opt])  # WONT
        elif cmd == 251:  # WILL
            if opt in (1, 3):  # ECHO, SGA
                resp.extend([255, 253, opt])  # DO
            else:
                resp.extend([255, 254, opt])  # DONT
        elif cmd == 252:  # WONT
            resp.extend([255, 254, opt])  # DONT
        if resp:
            try:
                self.s.sendall(resp)
            except Exception:
                pass

    def read_until(self, expected_list: list[bytes], timeout_msg: str, timeout: float = 4.0) -> bytes:
        self.s.settimeout(timeout)
        buf = b""
        while not any(exp in buf for exp in expected_list):
            try:
                b = self.s.recv(1)
                if not b:
                    raise ConnectionError("Conexão fechada pelo roteador.")
                if b[0] == 255:
                    cmd = self.s.recv(1)
                    opt = self.s.recv(1)
                    self.negotiate([255, cmd[0], opt[0]])
                    continue
                buf += b
            except socket.timeout:
                raise TimeoutError(timeout_msg)
        return buf

    def read_response(self, timeout: float = 1.2, respond_dsr: bool = False) -> bytes:
        buf = b""
        self.s.settimeout(timeout)
        while True:
            try:
                b = self.s.recv(1)
                if not b:
                    break
                if b[0] == 255:
                    cmd = self.s.recv(1)
                    opt = self.s.recv(1)
                    self.negotiate([255, cmd[0], opt[0]])
                    continue
                buf += b
                if respond_dsr and b"\x1b[6n" in buf:
                    self.s.sendall(b"\x1b[40;150R")
                    buf = buf.replace(b"\x1b[6n", b"")
            except socket.timeout:
                break
        return buf


def _run_telnet_generic(vendor: str, host: str, port: int, user: str, password: str, cmds: list[str]) -> dict[str, str]:
    """Pure Python generic clientless Telnet runner for multi-vendor network devices."""
    results = {}
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    with TelnetClient(host, port) as client:
        client.read_until(
            [b"login:", b"username:", b"user name:", b"login as:", b"username"],
            "Timeout aguardando prompt de usuário/login."
        )
        client.s.sendall(user.encode() + b"\r\n")

        client.read_until(
            [b"password:", b"senha:", b"password"],
            "Timeout aguardando prompt de senha."
        )
        client.s.sendall(password.encode() + b"\r\n")

        client.read_response(timeout=1.2, respond_dsr=(vendor == "mikrotik"))

        for cmd in cmds:
            client.s.sendall(cmd.encode() + b"\r\n")
            
            buf = b""
            client.s.settimeout(2.0)
            while True:
                try:
                    b = client.s.recv(1)
                    if not b:
                        break
                    if b[0] == 255:
                        cmd_opt = client.s.recv(2)
                        client.negotiate([255, cmd_opt[0], cmd_opt[1]])
                        continue
                    buf += b
                    
                    lower_buf = buf.lower()
                    if b"--- more" in lower_buf or b"--more--" in lower_buf or b"more <" in lower_buf:
                        client.s.sendall(b" ")
                        
                    if vendor == "mikrotik" and b"\x1b[6n" in buf:
                        client.s.sendall(b"\x1b[40;150R")
                        buf = buf.replace(b"\x1b[6n", b"")
                        
                except socket.timeout:
                    break
                    
            cleaned = ansi_escape.sub('', buf.decode("utf-8", errors="ignore"))
            cleaned = cleaned.replace('\r\n', '\n').replace('\r', '\n')
            results[cmd] = cleaned

    return results


def _run_ssh_command(host: str, port: str, user: str, key_path: str, cmd: str) -> str:
    """Pure subprocess proxy to execute remote SSH commands cleanly."""
    options = [
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "ConnectTimeout=5",
        "-o", "LogLevel=ERROR",
        "-p", port
    ]
    if key_path:
        options += ["-i", key_path]
    ssh_cmd = ["ssh"] + options + [f"{user}@{host}", cmd]
    res = ui.run_command_safe(ssh_cmd)
    if res and res.returncode == 0:
        return res.stdout
    return ""


def _generate_topology_html(nodes: list[dict], edges: list[dict], timestamp: str) -> str:
    """Generate high-end interactive network map using Vis.js inside HTML."""
    nodes_json = json.dumps(nodes, indent=2)
    edges_json = json.dumps(edges, indent=2)
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Aurea Topology Dashboard</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style type="text/css">
        body {{
            background-color: #0b0f19;
            color: #f3f4f6;
            font-family: 'Outfit', 'Inter', sans-serif;
            margin: 0;
            padding: 0;
            overflow: hidden;
        }}
        #header {{
            background: linear-gradient(90deg, #1e293b, #0f172a);
            padding: 15px 30px;
            border-bottom: 2px solid #0284c7;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }}
        #header h1 {{
            margin: 0;
            font-size: 20px;
            color: #0284c7;
            letter-spacing: 1px;
            text-transform: uppercase;
        }}
        #header .meta {{
            font-size: 13px;
            color: #9ca3af;
        }}
        #mynetwork {{
            width: 100vw;
            height: calc(100vh - 60px);
            background-color: #070a13;
        }}
    </style>
</head>
<body>
    <div id="header">
        <h1>Aurea Topology Network Map</h1>
        <div class="meta">Captured on: {timestamp} | Right-click/Drag to explore</div>
    </div>
    <div id="mynetwork"></div>

    <script type="text/javascript">
        const nodes = new vis.DataSet({nodes_json});
        const edges = new vis.DataSet({edges_json});

        const container = document.getElementById('mynetwork');
        const data = {{ nodes: nodes, edges: edges }};
        
        const options = {{
            nodes: {{
                shape: 'dot',
                size: 24,
                font: {{
                    size: 14,
                    color: '#ffffff',
                    face: 'sans-serif'
                }},
                borderWidth: 2,
                shadow: true
            }},
            edges: {{
                width: 2,
                font: {{
                    size: 11,
                    color: '#9ca3af',
                    align: 'middle'
                }},
                color: {{
                    color: '#0284c7',
                    highlight: '#38bdf8',
                    hover: '#38bdf8'
                }},
                smooth: {{
                    type: 'continuous'
                }}
            }},
            physics: {{
                stabilization: true,
                barnesHut: {{
                    gravitationalConstant: -8000,
                    springConstant: 0.04,
                    springLength: 120
                }}
            }},
            interaction: {{
                hover: true,
                navigationButtons: true,
                keyboard: true
            }}
        }};
        
        const network = new vis.Network(container, data, options);
    </script>
</body>
</html>
"""


def _write_config_backup(vendor_label: str, host: str, content: str) -> str:
    """Save config backup in backups/ directory."""
    backups_dir = Path("backups")
    backups_dir.mkdir(exist_ok=True)
    
    clean_host = host.replace(":", "_").replace(".", "_")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = backups_dir / f"config_{vendor_label.lower().replace(' ', '_')}_{clean_host}_{ts}.conf"
    
    try:
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(content)
        return str(file_name)
    except Exception:
        return ""


def _parse_vendor_data(vendor: str, addr_out: str, vlan_out: str, neigh_out: str, ident_out: str, host: str) -> tuple[list, list, list, str]:
    ips, vlans, neighbors = [], [], []
    seed_name = f"{vendor.capitalize()}_{host}"

    if vendor == "mikrotik":
        for line in addr_out.splitlines():
            if "address=" in line and "interface=" in line:
                addr_m = re.search(r'address=([^\s]+)', line)
                intf_m = re.search(r'(?:\s|^)interface=([^\s]+)', line)
                if addr_m and intf_m:
                    ips.append((addr_m.group(1), intf_m.group(1)))
                    
        for line in vlan_out.splitlines():
            if "vlan-id=" in line and "interface=" in line:
                name_m = re.search(r'name="([^"]+)"', line)
                if not name_m:
                    name_m = re.search(r'name=([^\s]+)', line)
                vid_m = re.search(r'vlan-id=(\d+)', line)
                intf_m = re.search(r'(?:\s|^)interface=([^\s]+)', line)
                if vid_m and intf_m:
                    v_name = name_m.group(1) if name_m else f"VLAN-{vid_m.group(1)}"
                    vlans.append((vid_m.group(1), v_name, intf_m.group(1)))
                    
        for line in neigh_out.splitlines():
            if "interface=" in line and "identity=" in line:
                intf_m = re.search(r'(?:\s|^)interface=([^\s]+)', line)
                addr_m = re.search(r'address=([^\s]+)', line)
                ident_m = re.search(r'identity="([^"]+)"', line)
                if not ident_m:
                    ident_m = re.search(r'identity=([^\s]+)', line)
                if intf_m and ident_m:
                    n_ip = addr_m.group(1) if addr_m else "N/A"
                    neighbors.append((intf_m.group(1), n_ip, ident_m.group(1)))
                    
        id_match = re.search(r'name:\s*([^\s]+)', ident_out)
        if id_match:
            seed_name = id_match.group(1)
            
    elif vendor == "huawei":
        for line in addr_out.splitlines():
            m = re.search(r'^([A-Za-z0-9/.-]+)\s+((?:[0-9]{1,3}\.){3}[0-9]{1,3}/\d+)', line.strip())
            if m:
                ips.append((m.group(2), m.group(1)))
                
        for line in vlan_out.splitlines():
            m = re.search(r'^(\d+)\s+(\S+)', line.strip())
            if m:
                v_id = m.group(1)
                vlans.append((v_id, f"VLAN-{v_id}", f"Vlanif{v_id}"))
                
        for line in neigh_out.splitlines():
            parts = line.strip().split()
            if len(parts) >= 4 and not parts[0].startswith("Local") and not parts[0].startswith("---"):
                neighbors.append((parts[0], "N/A", parts[-1]))
                
        if ident_out.strip() and not ident_out.startswith("Error"):
            seed_name = ident_out.strip().split()[-1].replace("<", "").replace(">", "").replace("[", "").replace("]", "")

    elif vendor == "cisco":
        for line in addr_out.splitlines():
            parts = line.strip().split()
            if len(parts) >= 5 and re.match(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', parts[1]):
                ips.append((f"{parts[1]}/24", parts[0]))
                
        for line in vlan_out.splitlines():
            parts = line.strip().split()
            if len(parts) >= 3 and parts[0].isdigit():
                vlans.append((parts[0], parts[1], f"Vlan{parts[0]}"))
                
        for line in neigh_out.splitlines():
            parts = line.strip().split()
            if len(parts) >= 5 and not parts[0].lower().startswith(("device", "capability", "total", "hold-time", "-")):
                neighbors.append((parts[1], "N/A", parts[0]))
                
        id_match = re.search(r'hostname\s+(\S+)', ident_out, re.IGNORECASE)
        if id_match:
            seed_name = id_match.group(1)

    elif vendor == "juniper":
        for line in addr_out.splitlines():
            parts = line.strip().split()
            if len(parts) >= 5 and parts[2] == "up" and parts[3] in ("inet", "inet6"):
                ips.append((parts[4], parts[0]))
                
        for line in vlan_out.splitlines():
            parts = line.strip().split()
            if len(parts) >= 2 and parts[1].isdigit():
                vlans.append((parts[1], parts[0], f"irb.{parts[1]}"))
                
        for line in neigh_out.splitlines():
            parts = line.strip().split()
            if len(parts) >= 5 and not parts[0].lower().startswith(("local", "parent", "total", "-")):
                neighbors.append((parts[0], "N/A", parts[-1]))
                
        id_match = re.search(r'host-name\s+(\S+);', ident_out)
        if id_match:
            seed_name = id_match.group(1)

    return ips, vlans, neighbors, seed_name


def _sync_to_netbox(nb_url: str, nb_token: str, vlans: list, ips: list, vendor_label: str, host: str):
    import ssl, json, urllib.request
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    base_url = nb_url.rstrip("/")
    vlan_endpoint = f"{base_url}/api/ipam/vlans/"
    ip_endpoint = f"{base_url}/api/ipam/ip-addresses/"
    
    headers = {
        "Authorization": f"Token {nb_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "AureaNOCRouterSync/2.2"
    }
    
    print(f"\n{blue('Sincronizando VLANs com o NetBox IPAM...')}")
    for vid, name, intf in vlans:
        payload = {
            "vid": int(vid),
            "name": name,
            "description": f"VLAN imported from {vendor_label} {host} on interface {intf}"
        }
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(vlan_endpoint, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, context=ctx, timeout=3.0) as resp:
                if resp.status in (200, 201):
                    print(f"    {green('✓')} VLAN {vid} ({name}) Sincronizada!")
        except Exception as e:
            err = str(e)
            if "HTTP Error 400" in err:
                print(f"    {yellow('⚠')} VLAN {vid} já existente no NetBox (Ignorada)")
            else:
                print(f"    {red('✗')} Falha ao sincronizar VLAN {vid}: {e}")
                
    print(f"\n{blue('Sincronizando Endereços IP com o NetBox IPAM...')}")
    for ip, intf in ips:
        payload = {
            "address": ip,
            "status": "active",
            "description": f"IP configured on interface {intf} of {vendor_label} {host}"
        }
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(ip_endpoint, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, context=ctx, timeout=3.0) as resp:
                if resp.status in (200, 201):
                    print(f"    {green('✓')} IP {ip} Sincronizado!")
        except Exception as e:
            err = str(e)
            if "HTTP Error 400" in err:
                print(f"    {yellow('⚠')} IP {ip} já cadastrado no NetBox (Ignorado)")
            else:
                print(f"    {red('✗')} Falha ao sincronizar IP {ip}: {e}")
                
    print(f"\n  {green('✓')} Sincronização de equipamentos concluída!")


@tool(
    number="27",
    name="Multi-Vendor Device Auditor & NetBox Sync",
    category="automation",
    keywords=["audit", "routeros", "cisco", "huawei", "juniper", "ssh", "telnet", "netbox", "topology"],
    tier="premium",
    i18n_key="tools.device_auditor.name",
    parameters=[
        {"name": "ip", "label": "IP do Equipamento", "default": "192.168.0.1", "type": "text"},
        {"name": "vendor", "label": "Fabricante (mikrotik/huawei/cisco/juniper)", "default": "mikrotik", "type": "text"},
        {"name": "protocol", "label": "Protocolo (ssh/telnet)", "default": "ssh", "type": "text"},
        {"name": "port", "label": "Porta de Acesso", "default": "22", "type": "number"},
        {"name": "login", "label": "Login / Usuário", "default": "admin", "type": "text"},
        {"name": "password", "label": "Senha (se Telnet)", "default": "", "type": "password"},
        {"name": "save_backup", "label": "Efetuar Config Backup? (y/n)", "default": "y", "type": "text"}
    ]
)
def device_auditor():
    ui.header("MULTI-VENDOR DEVICE AUDITOR & NETBOX SYNC")
    print(cyan("Coleta remota estruturada de inventário e mapeamento físico CDP/LLDP.\n"))
    
    host = ui.input_with_default("Endereço IP do Equipamento", "192.168.0.1").strip()
    if not host:
        print(f"  {red(t('ui.cancelled'))}")
        ui.pause()
        return
        
    vendor = ui.input_with_default("Fabricante (mikrotik/huawei/cisco/juniper)", "mikrotik").strip().lower()
    if vendor not in ("mikrotik", "huawei", "cisco", "juniper"):
        print(f"  {red('Fabricante inválido. Escolha: mikrotik, huawei, cisco ou juniper.')}")
        ui.pause()
        return
        
    vendor_labels = {
        "mikrotik": "MikroTik RouterOS",
        "huawei": "Huawei VRP",
        "cisco": "Cisco IOS",
        "juniper": "Juniper Junos"
    }
    vendor_label = vendor_labels[vendor]
    
    protocol = ui.input_with_default("Protocolo de Acesso (ssh/telnet)", "ssh").strip().lower()
    if protocol not in ("ssh", "telnet"):
        print(f"  {red('Protocolo inválido.')}")
        ui.pause()
        return
        
    port_default = "22" if protocol == "ssh" else "23"
    port = ui.input_with_default(f"Porta {protocol.upper()}", port_default).strip()
    user = ui.input_with_default("Usuário do Equipamento", "admin").strip()
    
    save_backup = ui.input_with_default("\nDeseja salvar o backup de configuração do equipamento? (y/N)", "y").strip().lower()
    
    cmds_dict = {
        "mikrotik": {
            "ips": "/ip address print detail without-paging",
            "vlans": "/interface vlan print detail without-paging",
            "neighbors": "/ip neighbor print detail without-paging",
            "identity": "/system identity print",
            "backup": "/export"
        },
        "huawei": {
            "paging": "screen-length 0 temporary",
            "ips": "display ip interface brief",
            "vlans": "display vlan",
            "neighbors": "display lldp neighbor brief",
            "identity": "display sysname",
            "backup": "display current-configuration"
        },
        "cisco": {
            "paging": "terminal length 0",
            "ips": "show ip interface brief",
            "vlans": "show vlan brief",
            "neighbors": "show lldp neighbors",
            "identity": "show running-config | include hostname",
            "backup": "show running-config"
        },
        "juniper": {
            "paging": "set cli screen-length 0",
            "ips": "show interfaces terse",
            "vlans": "show vlans",
            "neighbors": "show lldp neighbors",
            "identity": "show configuration system host-name",
            "backup": "show configuration"
        }
    }
    
    addr_out = ""
    vlan_out = ""
    neigh_out = ""
    ident_out = ""
    backup_out = ""
    
    if protocol == "ssh":
        default_key = str(Path.home() / ".ssh" / "id_rsa")
        if not Path(default_key).exists():
            default_key = ""
        key_path = ui.input_with_default("Caminho da Chave SSH Privada (Vazio para senha interativa)", default_key).strip()
        
        print(f"\n{blue(f'Conectando ao roteador {vendor_label} em {host}:{port} via SSH...')}")
        
        v_cmds = cmds_dict[vendor]
        addr_out = _run_ssh_command(host, port, user, key_path, v_cmds["ips"])
        if not addr_out:
            print(f"\n  {red('✗ Falha na conexão SSH. Verifique as credenciais ou chave SSH.')}")
            ui.pause()
            return
            
        vlan_out = _run_ssh_command(host, port, user, key_path, v_cmds["vlans"])
        neigh_out = _run_ssh_command(host, port, user, key_path, v_cmds["neighbors"])
        ident_out = _run_ssh_command(host, port, user, key_path, v_cmds["identity"])
        if save_backup == "y":
            backup_out = _run_ssh_command(host, port, user, key_path, v_cmds["backup"])
            
    else:
        password = ui.input_with_default("Senha do Equipamento", "").strip()
        print(f"\n{blue(f'Conectando ao roteador {vendor_label} em {host}:{port} via Telnet...')}")
        
        try:
            v_cmds = cmds_dict[vendor]
            cmds_to_run = []
            
            if "paging" in v_cmds:
                cmds_to_run.append(v_cmds["paging"])
                
            cmds_to_run.extend([v_cmds["ips"], v_cmds["vlans"], v_cmds["neighbors"], v_cmds["identity"]])
            
            if save_backup == "y":
                cmds_to_run.append(v_cmds["backup"])
                
            outputs = _run_telnet_generic(vendor, host, int(port), user, password, cmds_to_run)
            
            addr_out = outputs.get(v_cmds["ips"], "")
            vlan_out = outputs.get(v_cmds["vlans"], "")
            neigh_out = outputs.get(v_cmds["neighbors"], "")
            ident_out = outputs.get(v_cmds["identity"], "")
            if save_backup == "y":
                backup_out = outputs.get(v_cmds["backup"], "")
                
        except Exception as e:
            print(f"\n  {red(f'✗ Falha de Auditoria via Telnet: {e}')}")
            ui.pause()
            return

    # Parsing outputs based on Vendor
    ips, vlans, neighbors, seed_name = _parse_vendor_data(vendor, addr_out, vlan_out, neigh_out, ident_out, host)

    print(f"\n{cyan('═' * 60)}")
    print(green(f"✓ DADOS EXTRAÍDOS DO EQUIPAMENTO ({vendor_label})"))
    print(cyan('═' * 60))
    
    print(f"\n  {bold('IPs Configurados:')}")
    if not ips:
        print("    Nenhum IP encontrado.")
    for ip, intf in ips:
        print(f"    - {green(ip):<20} na interface {yellow(intf)}")
        
    print(f"\n  {bold('VLANs Descobertas:')}")
    if not vlans:
        print("    Nenhuma VLAN encontrada.")
    for vid, name, intf in vlans:
        print(f"    - {cyan(f'ID {vid}')} | {green(name):<18} na interface {yellow(intf)}")
        
    print(f"\n  {bold('Vizinhos LLDP/CDP Mapeados:')}")
    if not neighbors:
        print("    Nenhum vizinho de rede detectado.")
    for intf, n_ip, ident in neighbors:
        print(f"    - Interface {yellow(intf):<10} conectada a {green(ident)} (IP: {cyan(n_ip)})")
    print(f"{cyan('═' * 60)}\n")

    if save_backup == "y" and backup_out:
        print(f"{blue('Gravando arquivo de backup de configuração...')}")
        backup_file = _write_config_backup(vendor_label, host, backup_out)
        if backup_file:
            print(f"  {green('✓')} Backup salvo com sucesso: {yellow(backup_file)}")

    # Generate Topology HTML
    print(f"\n{blue('Gerando Dashboard de Topologia de Rede Interativo...')}")
    nodes_list = []
    edges_list = []
    
    nodes_list.append({
        "id": 0,
        "label": seed_name,
        "title": f"IP: {host}\\nVendor: {vendor_label}\\nRole: Seed/Gateway",
        "color": "#10b981" if vendor == "mikrotik" else "#f59e0b",
        "borderWidth": 4
    })
    
    for idx, (intf, n_ip, ident) in enumerate(neighbors, 1):
        node_id = None
        for n in nodes_list:
            if n["label"] == ident:
                node_id = n["id"]
                break
        if node_id is None:
            node_id = idx
            nodes_list.append({
                "id": node_id,
                "label": ident,
                "title": f"IP: {n_ip}\\nDiscovered via: {intf}",
                "color": "#0284c7"
            })
        edges_list.append({
            "from": 0,
            "to": node_id,
            "label": intf,
            "color": {"color": "rgba(255, 255, 255, 0.4)"}
        })
        
    topo_html = _generate_topology_html(nodes_list, edges_list, datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    try:
        with open("aurea_topology.html", "w", encoding="utf-8") as f:
            f.write(topo_html)
        print(f"  {green('✓')} Dashboard interativo gerado: {yellow('aurea_topology.html')}")
    except Exception as e:
        print(f"  {red(f'Erro ao gravar arquivo de topologia: {e}')}")

    sync_nb = ui.input_with_default("\nDeseja sincronizar estes dados com o NetBox? (y/N)", "n").strip().lower()
    if sync_nb == "y":
        nb_url = ui.input_with_default("URL do NetBox IPAM", "http://localhost:8000").strip()
        nb_token = ui.input_with_default("API Token", "0123456789abcdef0123456789abcdef0123457").strip()
        
        if not nb_url or not nb_token:
            print(f"  {red('✗ URL ou Token ausentes. Cancelado.')}")
            ui.pause()
            return
            
        _sync_to_netbox(nb_url, nb_token, vlans, ips, vendor_label, host)
        
    ui.pause()


@tool(
    number="28",
    name="BGP CIDR Route Aggregator",
    category="automation",
    keywords=["bgp", "cidr", "aggregator", "collapse", "ipaddress", "routing"],
    tier="free",
    i18n_key="tools.bgp_agg.name",
    parameters=[
        {"name": "prefixes", "label": "Redes/CIDRs separadas por vírgula", "default": "192.168.0.0/24, 192.168.1.0/24, 10.0.0.0/24, 10.0.1.0/24, 10.0.2.0/24, 10.0.3.0/24", "type": "text"}
    ]
)
def bgp_route_aggregator():
    ui.header("OTIMIZADOR E AGREGADOR BGP CIDR")
    print(cyan("Consolidação matemática de prefixos IPv4 sobrepostos ou adjacentes.\n"))
    
    raw_input = ui.input_with_default(
        "Digite as Redes/CIDRs separadas por vírgula\n(ex: 192.168.0.0/24, 192.168.1.0/24, 10.0.0.0/22)", 
        "192.168.0.0/24, 192.168.1.0/24, 10.0.0.0/24, 10.0.1.0/24, 10.0.2.0/24, 10.0.3.0/24"
    ).strip()
    
    if not raw_input:
        print(f"  {red(t('ui.cancelled'))}")
        ui.pause()
        return
        
    raw_prefixes = [x.strip() for x in re.split(r'[\s,;]+', raw_input) if x.strip()]
    
    networks = []
    invalid_prefixes = []
    
    for pref in raw_prefixes:
        try:
            net = ipaddress.ip_network(pref, strict=False)
            networks.append(net)
        except Exception:
            invalid_prefixes.append(pref)
            
    if invalid_prefixes:
        print(f"\n  {red('⚠ ALERTA:')} Os seguintes prefixos são inválidos e foram ignorados: {', '.join(invalid_prefixes)}")
        
    if not networks:
        print(f"\n  {red('Nenhum prefixo válido para processar.')}")
        ui.pause()
        return

    print(f"\n{blue(f'Calculando agregação ótima para {len(networks)} prefixos...')}")
    
    start_time = time.time()
    collapsed = list(ipaddress.collapse_addresses(networks))
    elapsed = (time.time() - start_time) * 1000

    print(f"\n{cyan('═' * 60)}")
    print(green("✓ RELATÓRIO DE CONSOLIDAÇÃO CIDR"))
    print(cyan('═' * 60))
    print(f"  {bold('Prefixos Originais:')} {len(networks)}")
    print(f"  {bold('Prefixos Agregados:')} {len(collapsed)}")
    reduction = ((len(networks) - len(collapsed)) / len(networks)) * 100
    print(f"  {bold('Redução na TCAM BGP:')} {green(f'{reduction:.1f}%')}")
    print(f"  {bold('Tempo de Cálculo:')}    {cyan(f'{elapsed:.2f} ms')}")
    print(f"{cyan('═' * 60)}")
    
    print(f"\n  {bold('Prefixos Otimizados de Borda:')}")
    for idx, net in enumerate(collapsed, 1):
        print(f"    [{idx:>2}] {green(str(net))}")
        
    print(f"\n  {bold('Sugestão de Bloco de Anúncio BGP:')}")
    for net in collapsed:
        print(f"    {yellow(f'network {net.network_address} mask {net.netmask}')}")
    print(f"{cyan('═' * 60)}\n")
    
    ui.pause()


@tool(
    number="29",
    name="Live Wi-Fi RSSI Monitor",
    category="automation",
    keywords=["wifi", "rssi", "monitor", "walktest", "signal"],
    tier="free",
    i18n_key="tools.wifi_monitor.name"
)
def wifi_monitor():
    ui.header(t("tools.wifi_monitor.title"))
    print(f"\n{blue(t('tools.wifi_monitor.running'))}")
    print(f"{t('ui.ctrl_c_stop')}\n")
    time.sleep(1.5)
    
    web_iteration = 0
    try:
        while True:
            if ui.is_cancelled():
                break
            if getattr(ui.web_context, "active", False) and web_iteration >= 7:
                print(cyan("\n[Wifi RSSI] Limite de 10 segundos atingido no modo web."))
                break
            sinal_pct = 0
            dbm = None
            bssid = frequencia = canal = "N/A"
            
            if platform_info.is_termux():
                try:
                    res = ui.run_command_safe(["termux-wifi-connectioninfo"])
                    if res and res.returncode == 0:
                        import json
                        dados = json.loads(res.stdout)
                        bssid_raw = dados.get("bssid", "N/A")
                        if bssid_raw and "unknown" not in bssid_raw.lower():
                            bssid = bssid_raw.upper()
                        rssi_bruto = dados.get("rssi")
                        if rssi_bruto is not None and rssi_bruto < 0:
                            dbm = int(rssi_bruto)
                        freq_mhz = dados.get("frequency_mhz")
                        if freq_mhz:
                            if 2400 <= freq_mhz < 2500: frequencia = "2.4 GHz"
                            elif 5000 <= freq_mhz < 6000: frequencia = "5 GHz"
                            elif freq_mhz >= 6000: frequencia = "6 GHz (Wi-Fi 6E)"
                except Exception:
                    bssid = "ERRO: Instale a termux-api"
            
            elif platform_info.is_windows():
                try:
                    saida_bytes = subprocess.check_output("netsh wlan show interfaces", shell=True, stderr=subprocess.DEVNULL)
                    texto = saida_bytes.decode('cp850', errors='ignore')
                except Exception:
                    texto = ""
                for linha in texto.split('\n'):
                    if ":" not in linha:
                        continue
                    partes = linha.split(':', 1)
                    chave  = partes[0].strip().upper()
                    valor  = partes[1].strip()
                    if "BSSID" in chave:
                        bssid = valor.upper()
                    elif any(k in chave for k in ("SIGNAL", "SINAL", "SEÑAL")):
                        m = re.search(r'\d+', valor)
                        if m:
                            sinal_pct = int(m.group())
                    elif any(k in chave for k in ("CHANNEL", "CANAL")):
                        m = re.search(r'\d+', valor)
                        if m:
                            canal = m.group()
                if canal != "N/A":
                    try:
                        ch = int(canal)
                        if 1 <= ch <= 14:   frequencia = "2.4 GHz"
                        elif 36 <= ch <= 177: frequencia = "5 GHz"
                        elif ch > 177:       frequencia = "6 GHz (Wi-Fi 6E)"
                    except Exception:
                        pass
                if sinal_pct > 0:
                    dbm = int((sinal_pct / 2) - 100)
                    
            else:
                res = ui.run_command_safe(["nmcli", "-t", "-f", "active,bssid,signal,freq", "dev", "wifi"])
                if res and res.stdout:
                    for linha in res.stdout.split('\n'):
                        if linha.startswith(("yes:", "sim:")):
                            linha_limpa = linha.replace(r'\:', '-')
                            partes = linha_limpa.split(':')
                            if len(partes) >= 4:
                                bssid = partes[1].replace('-', ':').upper()
                                m = re.search(r'\d+', partes[2])
                                if m:
                                    sinal_pct = int(m.group())
                                freq_mhz = partes[3]
                                if "5" in freq_mhz:   frequencia = "5 GHz"
                                elif "2" in freq_mhz: frequencia = "2.4 GHz"
                                elif "6" in freq_mhz: frequencia = "6 GHz"
                            break
                if sinal_pct > 0:
                    dbm = int((sinal_pct / 2) - 100)

            if dbm is not None and dbm < 0:
                if dbm >= -65:
                    sinal_fmt = green(f"{dbm} dBm ({t('tools.wifi_monitor.excellent')})")
                elif -75 <= dbm < -65:
                    sinal_fmt = yellow(f"{dbm} dBm ({t('tools.wifi_monitor.moderate')})")
                else:
                    sinal_fmt = red(f"{dbm} dBm ({t('tools.wifi_monitor.critical')})")
            else:
                sinal_fmt = red(t("tools.wifi_monitor.disconnected"))
                bssid = frequencia = "N/A"
                
            platform_info.clear_screen()
            print(cyan("═" * 53))
            print(green(f"  {t('tools.wifi_monitor.header')}"))
            print(cyan("═" * 53) + "\n")
            print(f"  [+] {t('tools.wifi_monitor.bssid')} {yellow(bssid)}")
            print(f"  [+] {t('tools.wifi_monitor.freq')}      {cyan(frequencia)}")
            print(f"  [+] {t('tools.wifi_monitor.signal')}   {sinal_fmt}\n")
            print(cyan("─" * 53))
            
            if ui.is_cancelled():
                break
            time.sleep(1.5)
            web_iteration += 1
            
    except KeyboardInterrupt:
        print(f"\n{yellow(t('tools.wifi_monitor.stopped'))}")
        ui.pause()


@tool(
    number="30",
    name="Native WHOIS Client",
    category="automation",
    keywords=["whois", "domain", "registry", "native", "port43"],
    tier="free",
    i18n_key="tools.whois.name",
    parameters=[
        {"name": "domain", "label": "Nome de Domínio", "default": "registro.br", "type": "text"}
    ]
)
def whois_client():
    ui.header(t("tools.whois.title"))
    print(t("tools.whois.desc") + "\n")
    try:
        dominio = ui.input_with_default(t("ui.enter_domain"), "registro.br")
        if not dominio:
            print(f"  {red(t('ui.cancelled'))}")
            ui.pause()
            return
        dominio = validators.validate_domain(dominio)
    except ValueError as e:
        print(f"  {red(str(e))}")
        ui.pause()
        return

    tld = dominio.split('.')[-1]
    servidor_whois = f"{tld}.whois-servers.net"
    print(f"\n{cyan(t('tools.whois.connecting', server=servidor_whois))}\n")
    
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5.0)
        s.connect((servidor_whois, 43))
        s.sendall((dominio + "\r\n").encode())
        resposta = b""
        while True:
            dados = s.recv(4096)
            if not dados:
                break
            resposta += dados
        texto = resposta.decode('utf-8', errors='ignore')
        
        print(yellow("─" * 30 + f"  {t('tools.whois.data')}  " + "─" * 30))
        for linha in texto.split('\n'):
            if linha.strip() and not linha.startswith(('%', '#', '>>>')):
                print(f"  {linha.strip()}")
        print(yellow("─" * 81))
    except Exception as e:
        print(f"  {red(t('tools.whois.fail', error=str(e)))}")
    finally:
        if s:
            s.close()
    ui.pause()


@tool(
    number="31",
    name="SLA & Uptime Calculator",
    category="automation",
    keywords=["sla", "uptime", "downtime", "calculator", "availability", "contract"],
    tier="free",
    i18n_key="tools.sla_calc.name",
    parameters=[
        {"name": "sla", "label": "Porcentagem de SLA (ex: 99.9)", "default": "99.9", "type": "text"}
    ]
)
def sla_calculator():
    ui.header(t("tools.sla_calc.title"))
    print(cyan(t("tools.sla_calc.desc") + "\n"))
    
    try:
        sla_str = ui.input_with_default("Porcentagem de SLA (ex: 99.9 ou 99.99)", "99.9").strip()
        if not sla_str:
            print(f"  {red(t('ui.cancelled'))}")
            ui.pause()
            return
        sla = float(sla_str.replace(",", "."))
        if sla < 0.0 or sla > 100.0:
            raise ValueError("Porcentagem de SLA deve ser entre 0 e 100.")
    except ValueError as e:
        print(f"\n  {red(str(e))}")
        ui.pause()
        return

    print(f"\n{yellow(t('tools.sla_calc.allowed', sla=sla))}\n")
    
    factor = (100.0 - sla) / 100.0
    
    daily_sec = int(86400 * factor)
    monthly_sec = int(86400 * 30.4375 * factor)
    yearly_sec = int(86400 * 365.25 * factor)
    
    def format_duration(seconds: int) -> str:
        if seconds <= 0:
            return "0s"
        
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, secs = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")
            
        return " ".join(parts)

    print(t("tools.sla_calc.daily", time=green(format_duration(daily_sec))))
    print(t("tools.sla_calc.monthly", time=yellow(format_duration(monthly_sec))))
    print(t("tools.sla_calc.yearly", time=red(format_duration(yearly_sec))))
    print()
    ui.pause()
