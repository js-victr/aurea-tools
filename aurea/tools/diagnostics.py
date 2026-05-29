"""
aurea.tools.diagnostics — Category 1: Network Diagnostics & Connectivity tools.
"""

import platform
import re
import socket
import time
import concurrent.futures

from aurea.core.colors import blue, green, red, yellow, cyan, bold, dim
from aurea.core import platform_info, ui, validators, http_client, network
from aurea.i18n import t
from aurea.tools import tool

# Speedtest optional dependency
try:
    import speedtest
    HAS_SPEEDTEST = True
except ImportError:
    HAS_SPEEDTEST = False


@tool(
    number="1",
    name="Advanced MTR with Loss & Jitter",
    category="diagnostics",
    keywords=["mtr", "traceroute", "ping", "latency", "loss", "jitter", "noc"],
    tier="free",
    i18n_key="tools.mtr.name",
    parameters=[
        {"name": "target", "label": "IP / Host / Destino", "default": "8.8.8.8", "type": "text"}
    ]
)
def mtr_tool():
    from datetime import datetime, timezone
    ui.header(t("tools.mtr.title"))
    try:
        target = ui.input_with_default(t("ui.enter_ip"), "8.8.8.8")
        if not target:
            print(f"  {red(t('ui.cancelled'))}")
            ui.pause()
            return
        target = validators.validate_host(target)
    except ValueError as e:
        print(f"  {red(str(e))}")
        ui.pause()
        return

    print(f"\n{yellow(t('ui.ctrl_c_stop'))}\n")
    time.sleep(1.0)
    
    # Simple continuous traceroute hops builder
    flag = "-n" if platform_info.is_windows() else "-c"
    
    # We will discover intermediate hops first
    print(cyan("Iniciando MTR - descobrindo rota..."))
    
    hops_ips = []
    if platform_info.is_windows():
        cmd = ["tracert", "-d", "-h", "10", target]
    else:
        cmd = ["traceroute", "-n", "-m", "10", target]
        
    res = ui.run_command_safe(cmd)
    if res and res.stdout:
        regex_ip = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        for line in res.stdout.splitlines():
            ip_match = re.search(regex_ip, line)
            if ip_match:
                ip = ip_match.group()
                if ip != target and ip not in hops_ips:
                    hops_ips.append(ip)
    hops_ips.append(target)
    
    # Stats dict: {ip: [sent, received, rtts]}
    stats = {ip: [0, 0, []] for ip in hops_ips}
    
    try:
        iteration = 1
        while True:
            if ui.is_cancelled():
                break
            if getattr(ui.web_context, "active", False) and iteration > 10:
                print(cyan("\n[MTR] Limite de 10 rodadas atingido no modo web."))
                break
                
            platform_info.clear_screen()
            print(cyan("═" * 80))
            print(green(f"  AUREA ADVANCED MTR  | Target: {target} | Sent: {iteration}"))
            print(cyan("═" * 80))
            print(f" {bold(t('tools.mtr.header'))}")
            print("-" * 80)
            
            for idx, hop_ip in enumerate(hops_ips):
                if ui.is_cancelled():
                    break
                stats[hop_ip][0] += 1  # sent
                
                # Ping single packet
                ping_cmd = ["ping", flag, "1", "-w", "1000" if platform_info.is_windows() else "1", hop_ip]
                start_time = time.time()
                res_ping = ui.run_command_safe(ping_cmd)
                rtt = (time.time() - start_time) * 1000
                
                if res_ping and res_ping.returncode == 0:
                    stats[hop_ip][1] += 1  # received
                    stats[hop_ip][2].append(rtt)
                
                sent, recv, rtts = stats[hop_ip]
                loss_pct = ((sent - recv) / sent) * 100
                
                if rtts:
                    min_r = min(rtts)
                    avg_r = sum(rtts) / len(rtts)
                    max_r = max(rtts)
                    jitter = sum(abs(rtts[i+1] - rtts[i]) for i in range(len(rtts)-1)) / (len(rtts)-1) if len(rtts) > 1 else 0.0
                    rtt_str = f"{min_r:.1f} | {avg_r:.1f} | {max_r:.1f} | {jitter:.1f}"
                else:
                    rtt_str = "* | * | * | *"
                
                loss_fmt = red(f"{loss_pct:.1f}%") if loss_pct > 10 else green(f"{loss_pct:.1f}%")
                print(f" [{idx+1:<2}] {hop_ip:<18} | {loss_fmt:<6} | {rtt_str}")
                
            if ui.is_cancelled():
                break
            time.sleep(1.0)
            iteration += 1
            
    except KeyboardInterrupt:
        print(f"\n{yellow(t('tools.mtr.stopped'))}")
        ui.pause()


@tool(
    number="2",
    name="Automatic MTU Discovery (PMTUD)",
    category="diagnostics",
    keywords=["mtu", "pmtud", "binary search", "fragmentation", "ping", "df"],
    tier="free",
    i18n_key="tools.mtu_test.name",
    parameters=[
        {"name": "target", "label": "IP / Host / Destino", "default": "8.8.8.8", "type": "text"}
    ]
)
def mtu_test():
    ui.header("AUTOMATIC MTU DISCOVERY (PMTUD)")
    print(cyan("Descobridor automatizado de MTU exato do enlace via busca binária.\n"))
    
    try:
        alvo = ui.input_with_default(t("ui.enter_ip"), "8.8.8.8")
        if not alvo:
            print(f"  {red(t('ui.cancelled'))}")
            ui.pause()
            return
        alvo = validators.validate_host(alvo)
    except ValueError as e:
        print(f"  {red(str(e))}")
        ui.pause()
        return

    print(f"\n{yellow('Iniciando busca binária de MTU (faixa 1200 a 1500 bytes)...')}\n")
    
    low = 1200 - 28 # ICMP payload size for MTU 1200
    high = 1500 - 28 # ICMP payload size for MTU 1500
    best_payload = None
    
    is_win = platform_info.is_windows()
    
    while low <= high:
        if ui.is_cancelled():
            break
        mid = (low + high) // 2
        mtu_check = mid + 28
        
        print(f"  Probing payload: {cyan(f'{mid:<4} bytes')} (MTU: {yellow(f'{mtu_check} bytes')}) ... ", end="", flush=True)
        
        if is_win:
            comando = ["ping", "-n", "1", "-f", "-l", str(mid), alvo]
        else:
            comando = ["ping", "-c", "1", "-M", "do", "-s", str(mid), alvo]
            
        resultado = ui.run_command_safe(comando)
        
        if resultado and resultado.returncode == 0:
            print(green("SUCCESS"))
            best_payload = mid
            low = mid + 1
        else:
            print(red("FRAGMENTED / TIMEOUT"))
            high = mid - 1
            
        time.sleep(0.1)
        
    if best_payload is not None:
        final_mtu = best_payload + 28
        print(f"\n{cyan('═' * 60)}")
        print(green(f"✓ MTU MÁXIMO DESCOBERTO: {bold(f'{final_mtu} bytes')}"))
        print(f"  - Payload ICMP: {best_payload} bytes")
        print(f"  - Cabeçalhos (IP + ICMP): 28 bytes")
        
        if final_mtu == 1500:
            print(f"  - {green('Configuração padrão (Ethernet/Fibra) recomendada.')}")
        elif 1480 <= final_mtu < 1500:
            print(f"  - {yellow('Link possivelmente encapsulado com PPPoE ou túnel leve.')}")
        else:
            print(f"  - {red('MTU baixo. Verifique configurações de VLAN/PPPoE/VPN no trajeto.')}")
        print(cyan("═" * 60) + "\n")
    else:
        print(f"\n  {red('✗ Não foi possível determinar o MTU do enlace. O destino pode estar bloqueando ICMP.')}")
        
    ui.pause()


@tool(
    number="3",
    name="NMAP TCP Port Scanner",
    category="diagnostics",
    keywords=["port", "tcp", "scanner", "nmap", "services", "fingerprint"],
    tier="free",
    i18n_key="tools.nmap_scan.name",
    parameters=[
        {"name": "target", "label": "IP / Host / Destino", "default": "127.0.0.1", "type": "text"}
    ]
)
def port_check():
    ui.header("AUREA NMAP TCP PORT SCANNER")
    print(cyan("Varredura automatizada das 1000 portas mais comuns e banner grabbing.\n"))
    
    try:
        host = ui.input_with_default(t("ui.enter_ip"), "127.0.0.1")
        if not host:
            print(f"  {red(t('ui.cancelled'))}")
            ui.pause()
            return
        host = validators.validate_host(host)
    except ValueError as e:
        print(f"  {red(str(e))}")
        ui.pause()
        return

    print(f"\n{yellow(f'Iniciando varredura rápida de 1000 portas comuns em {host}...')} (Aguarde)\n")
    
    # 1000 most common ports (ports 1 to 1000)
    ports = list(range(1, 1001))
    
    open_ports = []
    scanned_count = 0
    
    def scan_single_port(port: int):
        nonlocal scanned_count
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.0)
            res = s.connect_ex((host, port))
            if res == 0:
                service = network.WELL_KNOWN_PORTS.get(str(port), "Unknown")
                banner = ""
                try:
                    # Quick banner grabbing based on port
                    s.settimeout(1.0)
                    if port in (21, 22, 23, 25, 110, 143):
                        banner_bytes = s.recv(256)
                        banner = banner_bytes.decode('utf-8', errors='ignore').strip()
                    elif port in (80, 8080):
                        s.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
                        resp = s.recv(512).decode('utf-8', errors='ignore')
                        for line in resp.splitlines():
                            if line.lower().startswith("server:"):
                                banner = line.split(":", 1)[1].strip()
                                break
                    elif port in (443, 8443):
                        import ssl
                        ctx = ssl.create_default_context()
                        ctx.check_hostname = False
                        ctx.verify_mode = ssl.CERT_NONE
                        with ctx.wrap_socket(s, server_hostname=host) as ss:
                            ss.settimeout(1.0)
                            ss.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
                            resp = ss.recv(512).decode('utf-8', errors='ignore')
                            for line in resp.splitlines():
                                if line.lower().startswith("server:"):
                                    banner = line.split(":", 1)[1].strip()
                                    break
                except Exception:
                    pass
                
                service_fmt = f"{service} [{banner}]" if banner else service
                print(f"  Porta {green(f'{port:<5}')} | Status: {green('ABERTA'):<10} | Serviço: {cyan(service_fmt)}")
                open_ports.append((port, service_fmt))
            scanned_count += 1
            if scanned_count % 100 == 0:
                ui.verbose(f"Progresso da varredura: {scanned_count}/1000 portas analisadas.")

    # Using 100 workers for high performance
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        executor.map(scan_single_port, ports)
        
    print(f"\n{cyan('═' * 60)}")
    print(green(f"✓ VARREDURA NMAP CONCLUÍDA"))
    print(f"  - Total de portas varridas: 1000")
    print(f"  - Portas abertas encontradas: {green(str(len(open_ports)))}")
    print(cyan("═" * 60) + "\n")
    
    ui.pause()


@tool(
    number="4",
    name="Dynamic ISP Latency Matrix",
    category="diagnostics",
    keywords=["latency", "isp", "rtt", "cloud", "cdn", "noc", "matrix"],
    tier="free",
    i18n_key="tools.isp_latency.name"
)
def isp_latency_matrix():
    ui.header("DYNAMIC ISP LATENCY & ROUTING QUALITY MATRIX")
    print(cyan("Medição simultânea de latência e perda de pacotes para os maiores backbones mundiais.\n"))
    
    endpoints = {
        "AWS Cloud (US-East)": ("dynamodb.us-east-1.amazonaws.com", 443),
        "Google Cloud Edge": ("dns.google", 443),
        "Microsoft Azure Hub": ("management.azure.com", 443),
        "Oracle Cloud Infrastructure": ("objectstorage.us-ashburn-1.oraclecloud.com", 443),
        "Cloudflare CDN": ("1.1.1.1", 443),
        "Akamai Edge Network": ("www.akamai.com", 443),
        "Fastly Global Edge": ("www.fastly.com", 443),
    }
    
    print(f"{yellow('Iniciando disparos paralelos de teste de latência...')} (Aguarde)\n")
    
    results = []
    
    def probe_endpoint(name: str, host: str, port: int):
        rtts = []
        loss = 0
        ui.verbose(f"Testando conectividade e rota para {name} ({host}:{port})...")
        for _ in range(3):
            start = time.time()
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1.2)
                    res = s.connect_ex((host, port))
                    if res == 0:
                        rtts.append((time.time() - start) * 1000)
                    else:
                        loss += 1
            except Exception:
                loss += 1
            time.sleep(0.02)
            
        loss_pct = (loss / 3) * 100
        if rtts:
            min_r = min(rtts)
            avg_r = sum(rtts) / len(rtts)
            max_r = max(rtts)
            # Route Quality Score calculation (based on average latency and packet loss)
            quality = max(0, 100 - (avg_r * 0.25) - (loss_pct * 2.0))
        else:
            min_r, avg_r, max_r = 0.0, 0.0, 0.0
            quality = 0.0
            
        results.append({
            "name": name,
            "min": min_r,
            "avg": avg_r,
            "max": max_r,
            "loss": loss_pct,
            "quality": quality
        })

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(endpoints)) as executor:
        futures = [executor.submit(probe_endpoint, name, h[0], h[1]) for name, h in endpoints.items()]
        concurrent.futures.wait(futures)
        
    # Render gorgeous NOC matrix
    print(cyan("═" * 80))
    print(f"  {bold('Destino / backbone'):<30} | {bold('Perda%'):<6} | {bold('Lat Mín/Méd/Máx'):<20} | {bold('Qualidade')}")
    print(cyan("═" * 80))
    
    for r in sorted(results, key=lambda x: x["avg"] if x["avg"] > 0 else 9999):
        name_str = r["name"][:30]
        loss_fmt = red(f"{r['loss']:.0f}%") if r["loss"] > 0 else green("0%")
        
        if r["avg"] > 0:
            lat_fmt = cyan(f"{r['min']:.1f}/{r['avg']:.1f}/{r['max']:.1f} ms")
            q = r["quality"]
            if q >= 85:
                q_fmt = green(f"{q:.0f}% (EXCELENTE)")
            elif q >= 60:
                q_fmt = yellow(f"{q:.0f}% (MODERADA)")
            else:
                q_fmt = red(f"{q:.0f}% (CRÍTICA)")
        else:
            lat_fmt = dim("*/*/* ms")
            q_fmt = red("0% (OFFLINE)")
            
        print(f"  {name_str:<30} | {loss_fmt:<6} | {lat_fmt:<20} | {q_fmt}")
        
    print(cyan("═" * 80) + "\n")
    ui.pause()


@tool(
    number="5",
    name="Subnet Overlay Planner & Conflict Detector",
    category="diagnostics",
    keywords=["subnet", "cidr", "overlay", "planner", "conflict", "ipv4", "ipv6", "ipaddress"],
    tier="free",
    i18n_key="tools.subnet_planner.name"
)
def subnet_overlay_planner():
    import ipaddress
    ui.header("SUBNET OVERLAY PLANNER & CONFLICT DETECTOR (IPv4/IPv6)")
    print(cyan("Mapeador matemático de colisões e gerador de sub-redes livres (conflict-free).\n"))
    
    print(yellow("1. Configuração do Cenário de Sub-redes"))
    
    subnets_input = ui.input_with_default(
        "Digite as sub-redes existentes (separadas por vírgula)",
        "10.0.0.0/24, 10.0.1.0/24, 2001:db8:1::/48"
    ).strip()
    
    if not subnets_input:
        print(f"  {red(t('ui.cancelled'))}")
        ui.pause()
        return
        
    existing_nets = []
    for s in subnets_input.split(","):
        s = s.strip()
        if not s:
            continue
        try:
            net = ipaddress.ip_network(s, strict=False)
            existing_nets.append(net)
        except ValueError as e:
            print(f"  {red(f'Sub-rede existente inválida ({s}): {e}')}")
            ui.pause()
            return
            
    proposed_input = ui.input_with_default(
        "Digite a proposta de supernet/faixa CIDR",
        "10.0.0.0/22"
    ).strip()
    
    if not proposed_input:
        print(f"  {red(t('ui.cancelled'))}")
        ui.pause()
        return
        
    try:
        proposed_net = ipaddress.ip_network(proposed_input, strict=False)
    except ValueError as e:
        print(f"  {red(f'Sub-rede proposta inválida: {e}')}")
        ui.pause()
        return
        
    is_v6 = (proposed_net.version == 6)
    default_prefix = "64" if is_v6 else "26"
    
    prefix_input = ui.input_with_default(
        f"Qual tamanho de sub-rede deseja planejar/alocar? (ex: /{default_prefix})",
        default_prefix
    ).strip().replace("/", "")
    
    try:
        target_prefix = int(prefix_input)
        if is_v6:
            if target_prefix < proposed_net.prefixlen or target_prefix > 128:
                raise ValueError("Prefixo IPv6 fora dos limites válidos.")
        else:
            if target_prefix < proposed_net.prefixlen or target_prefix > 32:
                raise ValueError("Prefixo IPv4 fora dos limites válidos.")
    except ValueError as e:
        print(f"  {red(f'Prefixo inválido: {e}')}")
        ui.pause()
        return
        
    print(f"\n{yellow('Analisando overlaps e disponibilidade de alocação...')} (Aguarde)\n")
    
    overlaps = []
    non_overlaps = []
    
    for net in existing_nets:
        # Check overlaps
        if net.overlaps(proposed_net):
            overlaps.append(net)
        else:
            non_overlaps.append(net)
            
    print(cyan("═" * 70))
    print(bold("RELATÓRIO DE AUDITORIA DE OVERLAPS IPAM:"))
    print(cyan("═" * 70))
    print(f"  Supernet Proposto: {green(str(proposed_net))}")
    print(f"  Total de sub-redes existentes inseridas: {len(existing_nets)}")
    
    if overlaps:
        print(f"\n  {red('✗ CONFLITOS DE OVERLAP DETECTADOS!')}")
        for net in overlaps:
            print(f"    - A sub-rede existente {red(str(net))} colide/sobrepõe o bloco {yellow(str(proposed_net))}")
    else:
        print(f"\n  {green('✓ NENHUMA COLISÃO DETECTADA!')}")
        print(f"    O bloco proposto {green(str(proposed_net))} está completamente livre de overlaps no parque atual.")
        
    print(f"\n  {bold('Planejamento de Alocações Disponíveis (/' + str(target_prefix) + '):')}")
    
    available_subnets = []
    
    try:
        # Iterate over subnets of target_prefix size in proposed_net
        sub_generator = proposed_net.subnets(new_prefix=target_prefix)
        
        count = 0
        for sub in sub_generator:
            # Check if this candidate subnet overlaps with any existing net
            has_overlap = False
            for exist in existing_nets:
                if sub.overlaps(exist):
                    has_overlap = True
                    break
            if not has_overlap:
                available_subnets.append(sub)
                count += 1
            if count >= 12: # limit recommendations to avoid overflow
                break
    except Exception as e:
        ui.verbose(f"Erro no cálculo de subnets: {e}")
        
    if available_subnets:
        print(f"    Foram identificados blocos conflict-free de tamanho /{target_prefix}:")
        for idx, sub in enumerate(available_subnets, 1):
            print(f"      [{idx:>2}] {green(str(sub))}")
        if len(available_subnets) >= 12:
            print(f"      (Exibindo as primeiras 12 recomendações calculadas)")
    else:
        print(f"    {red('✗ Nenhum bloco livre de tamanho /' + str(target_prefix) + ' disponível neste supernet.')}")
        
    print(cyan("═" * 70) + "\n")
    ui.pause()
