"""
aurea.tools.bgp — Category 3: BGP Engineering & Routing tools.
"""

import sys
import urllib.parse
from collections import deque
import re
import time
from datetime import datetime

from aurea.core.colors import blue, green, red, yellow, cyan, bold, dim, c
from aurea.core import platform_info, ui, validators, http_client, network
from aurea.i18n import t
from aurea.tools import tool


TIER1_ASNS = {
    "2914": "NTT",
    "3356": "Lumen/Level3",
    "1299": "Arelion/Telia",
    "3257": "GTT",
    "6453": "Tata",
    "7018": "AT&T",
    "6762": "Sparkle",
    "1239": "Sprint",
    "3320": "Deutsche Telekom",
    "5511": "Orange",
    "701": "Verizon",
    "209": "CenturyLink",
    "3549": "Global Crossing",
    "174": "Cogent",
    "6939": "Hurricane Electric",
}

def _render_visual_as_path(as_path_str: str) -> str:
    from aurea.core.colors import green, yellow, cyan, bold
    if not as_path_str or as_path_str == "N/A":
        return "N/A"
    
    parts = as_path_str.split()
    rendered_hops = []
    
    for idx, asn in enumerate(parts):
        name = TIER1_ASNS.get(asn, "")
        if idx == len(parts) - 1:
            tag = f"AS{asn}"
            if name:
                tag += f" ({name})"
            rendered_hops.append(green(f"[{tag}]"))
        elif asn in TIER1_ASNS:
            rendered_hops.append(yellow(f"[AS{asn} ({name} - Tier-1)]"))
        else:
            rendered_hops.append(cyan(f"[AS{asn}]"))
            
    return f" {bold('➔')} ".join(rendered_hops)


@tool(
    number="18",
    name="BGP Looking Glass Consolidado",
    category="bgp",
    keywords=["bgp", "looking", "glass", "ripe", "ris", "route", "asn", "rpki", "propagation"],
    tier="free",
    i18n_key="tools.looking_glass.name",
    parameters=[
        {"name": "target", "label": "IP ou Prefixo CIDR", "default": "8.8.8.0/24", "type": "text"}
    ]
)
def bgp_looking_glass():
    ui.header("BGP LOOKING GLASS CONSOLIDADO")
    print(cyan("Consulta unificada a coletores globais RIS, caminhos AS-Path e validação RPKI.\n"))
    
    try:
        alvo = ui.input_with_default("IP ou Prefixo CIDR", "8.8.8.0/24")
        if not alvo:
            print(f"  {red(t('ui.cancelled'))}")
            ui.pause()
            return
        alvo = validators.validate_host(alvo)
    except ValueError as e:
        print(f"  {red(str(e))}")
        ui.pause()
        return

    alvo_enc = urllib.parse.quote(alvo, safe='/')
    print(f"\n{yellow('Minerando dados BGP globais via RIPE RIS e RPKI...')} (Aguarde)\n")
    
    # 1. Query Prefix Overview to find Origin ASN
    url_overview = f"https://stat.ripe.net/data/prefix-overview/data.json?resource={alvo_enc}"
    overview = http_client.fetch_json(url_overview, timeout=6.0)
    
    origin_asn = None
    prefix = alvo
    holder = "Desconhecido"
    
    if overview and overview.get("status") == "ok":
        data = overview.get("data", {})
        prefix = data.get("prefix", alvo)
        asns = data.get("asns", [])
        if asns:
            origin_asn = asns[0].get("asn")
            holder = asns[0].get("holder", "Desconhecido")
            print(f"  {green('✓')} Prefixo BGP:  {green(prefix)}")
            print(f"  {green('✓')} Origin ASN:  {yellow(f'AS{origin_asn}')} ({holder})")
        else:
            print(f"  {yellow('⚠')} Prefixo sem ASN de origem ativo nas tabelas públicas do RIPE RIS.")
            
    if not origin_asn:
        # Fallback to BGPKIT ASN resolution
        print(yellow("  Tentando base secundária BGPKIT para resolução de ASN..."))
        ip_for_bgpkit = alvo.split("/")[0]
        bgpkit_url = f"https://api.bgpkit.com/v3/utils/ip/{ip_for_bgpkit}"
        bgpkit_res = http_client.fetch_json(bgpkit_url, timeout=5.0)
        if bgpkit_res and isinstance(bgpkit_res, dict) and bgpkit_res.get("data"):
            bk_data = bgpkit_res["data"]
            origin_asn = bk_data.get("asn")
            holder = bk_data.get("as_org", "Desconhecido")
            prefix = bk_data.get("prefix", prefix)
            print(f"  {green('✓')} Prefixo BGP:  {green(prefix)} (via BGPKIT)")
            print(f"  {green('✓')} Origin ASN:  {yellow(f'AS{origin_asn}')} ({holder})")
        elif not overview:
            print(f"  {red('✗ Falha geral na resolução do ASN por RIPE RIS e BGPKIT.')}")
    
    # 2. Query RPKI status
    if origin_asn:
        url_rpki = f"https://stat.ripe.net/data/rpki-validation/data.json?resource=AS{origin_asn}&prefix={urllib.parse.quote(prefix, safe='/')}"
        rpki_res = http_client.fetch_json(url_rpki, timeout=5.0)
        if rpki_res and rpki_res.get("status") == "ok":
            rpki_status = rpki_res.get("data", {}).get("status", "UNKNOWN").upper()
            if rpki_status == "VALID":
                print(f"  {green('✓')} RPKI Status: {green('VALID')} (Assinado digitalmente)")
            elif "INVALID" in rpki_status:
                print(f"  {red('✗')} RPKI Status: {red(rpki_status)} (Rota potencialmente sequestrada/inválida!)")
            else:
                print(f"  {yellow('⚠')} RPKI Status: {yellow('UNKNOWN')} (Prefixo sem assinatura ROA)")
                
    # 3. Query Looking Glass for Global Propagation Paths
    url_lg = f"https://stat.ripe.net/data/looking-glass/data.json?resource={alvo_enc}"
    lg_res = http_client.fetch_json(url_lg, timeout=8.0)
    
    if lg_res and lg_res.get("status") == "ok":
        rrcs = lg_res.get("data", {}).get("rrcs", [])
        print(f"  {green('✓')} Visibilidade: {green(f'Divulgado em {len(rrcs)} coletores globais RIS')}")
        
        print(f"\n{cyan('═' * 70)}")
        print(bold("CAMINHOS DE PROPAGAÇÃO AS-PATH (GLOBAL SAMPLES):"))
        print(cyan('═' * 70))
        
        for rrc in rrcs[:5]:  # limit to top 5 route collectors
            rrc_name = rrc.get("rrc", "N/A")
            peers = rrc.get("peers", [])
            if peers:
                peer = peers[0]
                as_path = peer.get("as_path", "N/A")
                next_hop = peer.get("next_hop", "N/A")
                peer_asn = peer.get("asn", "N/A")
                
                print(f"  {bold(f'[{rrc_name}]')} via AS{peer_asn} | NextHop: {next_hop}")
                print(f"    └─ Path: {yellow(as_path)}")
                print(f"    └─ Flow: {_render_visual_as_path(as_path)}")
                
        if len(rrcs) > 5:
            print(f"\n  ... e outros {len(rrcs) - 5} coletores públicos de trânsito.")
            print(cyan('═' * 70))
            resp = ui.input_with_default("Deseja visualizar os caminhos de TODOS os outros coletores? (s/n)", "n")
            if resp.lower() in ("s", "y", "sim", "yes"):
                print(cyan('\n' + '═' * 70))
                print(bold("OUTROS CAMINHOS DE PROPAGAÇÃO AS-PATH:"))
                print(cyan('═' * 70))
                for rrc in rrcs[5:]:
                    rrc_name = rrc.get("rrc", "N/A")
                    peers = rrc.get("peers", [])
                    if peers:
                        peer = peers[0]
                        as_path = peer.get("as_path", "N/A")
                        next_hop = peer.get("next_hop", "N/A")
                        peer_asn = peer.get("asn", "N/A")
                        
                        print(f"  {bold(f'[{rrc_name}]')} via AS{peer_asn} | NextHop: {next_hop}")
                        print(f"    └─ Path: {yellow(as_path)}")
                        print(f"    └─ Flow: {_render_visual_as_path(as_path)}")
                print(cyan('═' * 70) + "\n")
            else:
                print()
        else:
            print(cyan('═' * 70) + "\n")
    else:
        print(f"  {red('✗ Não foi possível carregar os caminhos de roteamento dos coletores RIS.')}")
        
    ui.pause()


@tool(
    number="19",
    name="BGP RPKI Validator",
    category="bgp",
    keywords=["bgp", "rpki", "validation", "hijack", "roa"],
    tier="free",
    i18n_key="tools.rpki.name",
    parameters=[
        {"name": "target", "label": "Prefixo CIDR", "default": "138.122.152.0/22", "type": "text"},
        {"name": "asn", "label": "Origin ASN (número)", "default": "264321", "type": "number"}
    ]
)
def rpki_validator():
    ui.header(t("tools.rpki.title"))
    try:
        prefix_input = ui.input_with_default(t("ui.enter_prefix"), "138.122.152.0/22")
        if not prefix_input:
            print(f"  {red(t('ui.cancelled'))}")
            ui.pause()
            return
        prefix_input = validators.validate_cidr(prefix_input)
        
        asn = ui.input_with_default(t("ui.enter_asn"), "264321")
        asn = validators.validate_asn(asn)
    except ValueError as e:
        print(f"\n {red(str(e))}")
        ui.pause()
        return

    prefix_enc = urllib.parse.quote(prefix_input, safe='/')
    print(f"\n{blue('Consultando infraestrutura RPKI do RIPE NCC...')}")

    url_ripe = f"https://stat.ripe.net/data/rpki-validation/data.json?resource=AS{asn}&prefix={prefix_enc}"
    dados = http_client.fetch_json(url_ripe, timeout=6.0)

    print(f"\n{blue('--- RELATÓRIO RPKI -------------------------------------------')}")
    print(f"  {green('Alvo Analisado:')} {prefix_input} originado por AS{asn}")

    if dados and dados.get("status") == "ok":
        estado = dados.get("data", {}).get("status", "UNKNOWN").upper()
        
        if estado == "VALID":
            print(f"  {green('Status RPKI   ')}: VÁLIDO (Assinatura criptográfica confirmada)")
            roas = dados["data"].get("validating_roas", [])
            for roa in roas:
                roa_pref = roa.get("prefix")
                max_len = roa.get("max_length")
                orig = roa.get("origin")
                print(f"  {blue('→ Objeto ROA  ')}: {roa_pref} (Max: /{max_len}) -> AS{orig}")
                
        elif "INVALID" in estado:
            print(f"  {blue(f'Status RPKI   ')}: {estado} (Conflito de ROA ou Rota Sequestrada!)")
        elif estado == "UNKNOWN":
            print(f"  {green('Status RPKI   ')}: UNKNOWN (Prefixo sem assinatura ROA registrada)")
        else:
            print(f"  {green('Status RPKI   ')}: {estado}")
    else:
        print(f"  {blue('Status RPKI   ')}: Falha de comunicação ou limite de requisições na API.")

    print(f"\n{blue('------------------------------------------------------------')}")
    ui.pause()


@tool(
    number="20",
    name="PeeringDB Lookup",
    category="bgp",
    keywords=["peeringdb", "asn", "peering", "ixp", "datacenter", "policy"],
    tier="free",
    i18n_key="tools.peeringdb.name",
    parameters=[
        {"name": "asn", "label": "Número ASN (ex: 15169)", "default": "15169", "type": "number"}
    ]
)
def peeringdb_lookup():
    ui.header(t("tools.peeringdb.title"))
    try:
        asn_str = ui.input_with_default(t("ui.enter_asn"), "15169")
        if not asn_str:
            print(f"  {red(t('ui.cancelled'))}")
            ui.pause()
            return
        asn = validators.validate_asn(asn_str)
    except ValueError as e:
        print(f"  {red(str(e))}")
        ui.pause()
        return

    print(f"\n{cyan(f'Consultando API do PeeringDB para AS{asn}...')}\n")
    
    url = f"https://www.peeringdb.com/api/net?asn={asn}"
    res = http_client.fetch_json(url, timeout=6.0)
    
    if res and res.get('data'):
        net_data = res['data'][0]
        name = net_data.get('name', 'N/A')
        policy = net_data.get('policy_general', 'N/A')
        website = net_data.get('website', 'N/A')
        phone = net_data.get('phone', 'N/A')
        
        print(f"  {green('✓')} {t('tools.ip_intel.org')}     {yellow(name)}")
        print(f"  {green('✓')} {t('tools.peeringdb.policy')}  {cyan(policy)}")
        print(f"  {green('✓')} Website:          {cyan(website)}")
        print(f"  {green('✓')} Phone/Contact:    {cyan(phone)}")
        
        ix_url = f"https://www.peeringdb.com/api/netixlan?asn={asn}"
        ix_res = http_client.fetch_json(ix_url, timeout=5.0)
        
        print(f"\n  {green(t('tools.peeringdb.ixps'))}")
        if ix_res and ix_res.get('data'):
            for ix in ix_res['data'][:5]:
                ix_name = ix.get('name', 'N/A')
                speed = ix.get('speed', 0) / 1000
                ip4 = ix.get('ipaddr4', 'N/A')
                print(f"    - {ix_name} ({speed}G) | IPv4: {ip4}")
            if len(ix_res['data']) > 5:
                print(f"    ... e mais {len(ix_res['data']) - 5} IXPs.")
        else:
            print("    Nenhuma informação pública de IXP encontrada.")
            
    else:
        print(f"  {red(t('tools.peeringdb.not_found', asn=asn))}")
        
    ui.pause()


# --- AUREAFLOW NETFLOW V5 CLI DISPATCHER ---
from aurea.core.engines.netflow import NetFlowCollector


def _run_netflow_cli_dashboard():
    try:
        port_str = ui.input_with_default("Digite a porta UDP do NetFlow v5 / NetFlow Port", "2055")
        port = int(port_str)
    except Exception:
        port = 2055

    print(cyan("\nSelecione um Filtro NOC Inteligente / Select NOC Filter:"))
    print(green("  [1] Sem Filtro (Monitorar Tudo)"))
    print(green("  [2] Filtrar por Host/IP Específico (ex: 192.168.1.100)"))
    print(green("  [3] Filtrar por Porta de Serviço (ex: 443, 80)"))
    print(green("  [4] Filtrar por Protocolo (TCP)"))
    print(green("  [5] Filtrar por Protocolo (UDP)"))
    
    opcao = ui.input_with_default("Escolha a opção (1-5)", "1")
    
    ip_filter = None
    port_filter = None
    proto_filter = None
    filter_desc = "Sem Filtros Ativos (Monitorando Tudo)"
    
    if opcao == "2":
        ip_filter = ui.input_with_default("Digite o IP de Origem ou Destino", "")
        if ip_filter:
            filter_desc = f"Filtrando por IP: {ip_filter}"
    elif opcao == "3":
        try:
            p_str = ui.input_with_default("Digite a Porta de Destino", "443")
            port_filter = int(p_str)
            filter_desc = f"Filtrando por Porta: {port_filter}"
        except Exception:
            pass
    elif opcao == "4":
        proto_filter = "tcp"
        filter_desc = "Filtrando por Protocolo: TCP"
    elif opcao == "5":
        proto_filter = "udp"
        filter_desc = "Filtrando por Protocolo: UDP"
        
    collector = NetFlowCollector(
        port=port,
        ip_filter=ip_filter,
        port_filter=port_filter,
        proto_filter=proto_filter
    )
    
    try:
        collector.start()
    except OSError as e:
        print(red(f"\n  ✗ {e}"))
        ui.pause()
        return

    print(cyan(f"\n  ✓ Coletor NetFlow v5 ativo na porta UDP {port}..."))
    print(yellow("  Preparando painel interativo... (Aguarde 2 segundos)"))
    time.sleep(2.0)
    
    history = deque(maxlen=15)
    
    try:
        while True:
            snapshot = collector.get_snapshot()
            
            # Render Screen using ANSI escapes
            sys.stdout.write("\033[H\033[J")
            sys.stdout.flush()
            
            width = max(platform_info.terminal_width(), 40)
            top_line = "═" * min(width - 4, 76)
            
            # Draw header
            print(cyan(f" ╔{top_line}╗"))
            title_text = f" AUREAFLOW   —   NETFLOW V5 LIVE DASHBOARD   —   UDP PORT {port}"
            print(f" {cyan('║')} {bold(green(f'{title_text:^{min(width - 4, 76)}}'))} {cyan('║')}")
            print(cyan(f" ╚{top_line}╝"))
            
            total_mbytes = snapshot["total_bytes"] / (1024 * 1024)
            down_rate = snapshot["down_rate_kbps"]
            up_rate = snapshot["up_rate_kbps"]
            tot_rate = down_rate + up_rate
            
            history.append(tot_rate)
            
            exporters = list(snapshot["exporters"].items())
            talkers = snapshot["talkers"]
            protocols = snapshot["protocols"]
            alerts = snapshot["alerts"]
                
            def fmt_rate(kbps: float) -> str:
                if kbps >= 1024:
                    return f"{kbps/1024:.2f} Mbps"
                return f"{kbps:.2f} Kbps"
            
            # Sparkline graph calculation
            max_val = max(history) if history else 0
            sparkline = ""
            if max_val <= 0:
                sparkline = " " * len(history)
            else:
                spark_chars = [" ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
                for val in history:
                    idx = int((val / max_val) * (len(spark_chars) - 1))
                    idx = max(0, min(idx, len(spark_chars) - 1))
                    sparkline += spark_chars[idx]
            
            sparkline_padded = sparkline.rjust(15, " ")
                
            # Traffic Overview Card
            print(cyan("\n [1] TELEMETRIA GERAL DE FLUXO / SYSTEM THROUGHPUT"))
            print(f"  • Filtro NOC Ativo:  {bold(yellow(filter_desc))}")
            print(f"  • Velocímetro (30s): [{green(sparkline_padded)}] (Max: {fmt_rate(max_val)})")
            print(f"  • Throughput Total:  {bold(yellow(fmt_rate(tot_rate)))} | Down: {fmt_rate(down_rate)} | Up: {fmt_rate(up_rate)}")
            print(f"  • Volume Consolidado: {bold(green(f'{total_mbytes:.2f} MB'))} processados no socket")
            
            # Exporters/Routers Table
            print(cyan("\n [2] ROTEADORES EXPORTADORES / ROUTERS EMITTING FLOWS"))
            if not exporters:
                print(dim("  (Aguardando datagramas NetFlow v5... certifique-se de apontar o fluxo do roteador para este IP)"))
            else:
                print(f"  {'IP DO ROTEADOR':<18} | {'TAXA ATIVA':<12} | {'VETOR / FABRICANTE (OUI)':<28} | {'PACOTES':<10}")
                print(f"  {'-'*18}-+-{'-'*12}-+-{'-'*28}-+-{'-'*10}")
                for exp_ip_addr, exp_data_obj in exporters[:4]:
                    vendor = exp_data_obj.get("vendor", "N/A")
                    if len(vendor) > 26:
                        vendor = vendor[:24] + ".."
                    print(f"  {exp_ip_addr:<18} | {bold(yellow(fmt_rate(exp_data_obj['rate_kbps']))):<12} | {green(f'{vendor:<28}')} | {exp_data_obj['packets']:<10}")
                    
            # Top Talkers
            print(cyan("\n [3] PRINCIPAIS CONSUMIDORES / TOP NETWORK TALKERS"))
            if not talkers:
                print(dim("  (Nenhum tráfego IP registrado ainda)"))
            else:
                print(f"  {'IP DO CLIENTE / HOST':<22} | {'VOLUME':<15} | {'SHARE':<10}")
                print(f"  {'-'*22}-+-{'-'*15}-+-{'-'*10}")
                total_talker_bytes = sum(b for ip, b in talkers) or 1
                for talker_ip_addr, b in talkers[:5]:
                    pct = (b / total_talker_bytes) * 100
                    b_mb = b / (1024 * 1024)
                    print(f"  {talker_ip_addr:<22} | {bold(green(f'{b_mb:.2f} MB')):<15} | {pct:.1f}%")
                    
            # Protocol Shares & DPI Services
            print(cyan("\n [4] COMPARTILHAMENTO DE PROTOCOLOS & DPI / PROTOCOL & DPI SERVICES"))
            total_proto_bytes = sum(protocols.values()) or 1
            for proto_name, bytes_cnt in protocols.items():
                pct = (bytes_cnt / total_proto_bytes) * 100
                bar_len = int(pct / 4) # Max 25 chars
                bar = "█" * bar_len + "░" * (25 - bar_len)
                print(f"  • {proto_name.upper():<6} [{cyan(bar)}] {bold(green(f'{pct:>5.1f}%'))} ({bytes_cnt/(1024*1024):.1f} MB)")
            
            ports_list = snapshot.get("ports", [])
            if ports_list:
                print(dim("  --- Top Serviços DPI (Port-to-Service) ---"))
                total_port_bytes = sum(b for p, b in ports_list) or 1
                for port_str, bytes_cnt in ports_list[:4]:
                    pct = (bytes_cnt / total_port_bytes) * 100
                    service_name = network.WELL_KNOWN_PORTS.get(port_str, f"Porta {port_str}")
                    service_label = f"{service_name} ({port_str})"
                    bar_len = int(pct / 4) # Max 25 chars
                    bar = "█" * bar_len + "░" * (25 - bar_len)
                    bytes_mb = bytes_cnt / (1024 * 1024)
                    print(f"  • {service_label:<18} [{cyan(bar)}] {bold(green(f'{pct:>5.1f}%'))} ({bytes_mb:.2f} MB)")

            # SNMP Interface Congestion Profiler
            interfaces = snapshot.get("interfaces", [])
            print(cyan("\n [5] CONGESTIONAMENTO DE INTERFACES SNMP / SNMP INTERFACE PROFILER"))
            if not interfaces:
                print(dim("  (Nenhum tráfego de interface SNMP registrado ainda)"))
            else:
                print(f"  {'IFINDEX':<10} | {'IN_VOLUME':<12} | {'OUT_VOLUME':<12} | {'CARGA / NOC STATUS':<24}")
                print(f"  {'-'*10}-+-{'-'*12}-+-{'-'*12}-+-{'-'*24}")
                total_int_bytes = sum(data["in_bytes"] + data["out_bytes"] for idx, data in interfaces) or 1
                for idx, data in interfaces[:4]:
                    in_mb = data["in_bytes"] / (1024 * 1024)
                    out_mb = data["out_bytes"] / (1024 * 1024)
                    total_node_bytes = data["in_bytes"] + data["out_bytes"]
                    pct_load = (total_node_bytes / total_int_bytes) * 100
                    
                    if pct_load > 50:
                        status_lbl = red("CONGESTIONADO")
                    elif pct_load > 20:
                        status_lbl = yellow("CARGA ALTA")
                    else:
                        status_lbl = green("NORMAL")
                        
                    print(f"  IfIndex {idx:<2} | {in_mb:>9.2f} MB | {out_mb:>9.2f} MB | {status_lbl:<26} ({pct_load:>4.1f}%)")
                
            # Alerts & Threats
            if alerts:
                print(red("\n [!] ANOMALIAS E AMEAÇAS DE NOC / SECURITY THREATS DETECTED"))
                for a in alerts[-3:]:
                    print(f"  {red('🚨')} [{a['timestamp']}] {bold(yellow(a['desc']))}")
                    
            print(dim(f"\n Pressione CTRL+C a qualquer momento para desligar o coletor e voltar..."))
            time.sleep(2.0)
            
    except KeyboardInterrupt:
        print(red("\n\n [!] Desligando coletor e liberando porta socket UDP..."))
    finally:
        collector.stop()
        time.sleep(0.5)
        print(green(" ✓ Socket liberado com sucesso. Retornando ao menu."))
        ui.pause()


def _run_local_connections_monitor():
    sistema = platform_info.system()
    is_termux = platform_info.is_termux()
    
    conexoes_conhecidas = set()
    cache_ips = {}
    LIMITE_CACHE = 5000 
    
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_csv = f"aurea_captura_{ts}.csv"
    contador_pacotes = 0

    try:
        platform_info.clear_screen()
        print(cyan("═" * 90))
        print(green(t("tools.traffic_monitor.header_active", file=nome_csv)))
        if is_termux:
            print(yellow(t("tools.traffic_monitor.mobile_warning")))
        print(cyan("═" * 90))
        
        hora_lbl = "HORA" if t("ui.press_enter").startswith("Pres") else "TIME"
        proto_lbl = "PROTO"
        orig_lbl = "ORIGEM" if t("ui.press_enter").startswith("Pres") else "ORIGIN"
        dest_lbl = "DESTINO" if t("ui.press_enter").startswith("Pres") else "DESTINATION"
        info_lbl = "INFO / ASN"
        
        print(f"{hora_lbl:<10} {proto_lbl:<5} {orig_lbl:<22} {dest_lbl:<22} {info_lbl:<30}")
        print("-" * 90)

        import csv
        with open(nome_csv, mode='w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['Horario', 'Protocolo', 'Origem', 'Destino', 'Porta', 'Servico', 'ASN_Organizacao', 'Estado', 'PID'])

            while True:
                novas_conexoes = []
                
                if platform_info.is_windows():
                    res = ui.run_command_safe(["netstat", "-ano"])
                    if res and res.stdout:
                        for linha in res.stdout.splitlines():
                            if "TCP" in linha or "UDP" in linha:
                                partes = linha.split()
                                if len(partes) >= 4:
                                    proto   = partes[0]
                                    origem  = partes[1]
                                    destino = partes[2]
                                    estado  = partes[3] if proto == "TCP" else "UDP_FLOW"
                                    pid     = partes[4] if len(partes) > 4 and proto == "TCP" else (partes[3] if len(partes) > 3 and proto == "UDP" else "N/A")
                                    
                                    if not destino.startswith(("0.0.0.0", "*:*", "[::]:0", "127.0.0.1")):
                                        chave = f"{proto}|{origem}|{destino}"
                                        if chave not in conexoes_conhecidas:
                                            novas_conexoes.append((proto, origem, destino, estado, pid))
                
                else:
                    res = ui.run_command_safe(["ss", "-tuna"])
                    
                    if not res or res.returncode != 0:
                        if is_termux and contador_pacotes == 0:
                            print(f"\n{red(t('tools.traffic_monitor.iproute_error'))} Execute: {green('pkg install iproute2')}")
                            time.sleep(5)
                            break
                    
                    if res and res.stdout:
                        for linha in res.stdout.splitlines():
                            linha_min = linha.lower()
                            if "tcp" in linha_min or "udp" in linha_min:
                                partes = linha.split()
                                if len(partes) >= 5:
                                    proto   = partes[0].upper()
                                    estado  = partes[1] if proto == "TCP" else "UDP_FLOW"
                                    origem  = partes[4]
                                    destino = partes[5]
                                    pid     = "N/A"
                                    
                                    if not destino.startswith(("0.0.0.0", "127.0.0.", "[::]")):
                                        chave = f"{proto}|{origem}|{destino}"
                                        if chave not in conexoes_conhecidas:
                                            novas_conexoes.append((proto, origem, destino, estado, pid))

                for conn in novas_conexoes:
                    proto, origem, destino, estado, pid = conn
                    
                    if len(conexoes_conhecidas) > LIMITE_CACHE:
                        conexoes_conhecidas.clear()
                    
                    chave = f"{proto}|{origem}|{destino}"
                    conexoes_conhecidas.add(chave)

                    if ':' in destino and destino.count(':') == 1:
                        ip_dst, porta_dst = destino.rsplit(':', 1)
                    elif ']' in destino:
                        ip_dst    = destino.split(']')[0].replace('[', '')
                        porta_dst = destino.split(']:')[1] if ']:' in destino else ""
                    else:
                        ip_dst, porta_dst = destino, ""

                    servico = network.WELL_KNOWN_PORTS.get(porta_dst, f"P:{porta_dst}")
                    org_destino = network.get_asn_org(ip_dst, cache_ips)
                    
                    horario_curto = datetime.now().strftime("%H:%M:%S")
                    horario_full = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cor_proto = green if proto == "TCP" else cyan
                    
                    str_origem = origem[:20]
                    str_destino = destino[:20]
                    str_info = f"{servico} | {org_destino[:15]}"
                    
                    print(f"{yellow(horario_curto):<10} {cor_proto(proto):<14} {str_origem:<22} {str_destino:<22} {str_info}")

                    writer.writerow([horario_full, proto, origem, destino, porta_dst, servico, org_destino, estado, pid])
                    f.flush()
                    contador_pacotes += 1

                time.sleep(1)

    except KeyboardInterrupt:
        print(f"\n\n{yellow(t('tools.traffic_monitor.stopped'))}")
        print(f"  {green('✓')} {t('tools.traffic_monitor.total', count=contador_pacotes)}")
        print(f"  {green('✓')} {t('tools.traffic_monitor.file_saved', file=nome_csv)}")
        ui.pause()
    except Exception as e:
        print(f"\n{red(f'✗ Erro: {e}')}")
        ui.pause()


@tool(
    number="21",
    name="Traffic Flow & ASN Monitor",
    category="bgp",
    keywords=["traffic", "flow", "asn", "monitor", "connections", "network"],
    tier="free",
    i18n_key="tools.traffic_monitor.name"
)
def traffic_monitor():
    ui.header(t("tools.traffic_monitor.title"))
    print(cyan("\nEscolha o Modo de Monitoramento / Select Monitoring Mode:"))
    print(green("  [1] Capturar Conexões Ativas Locais (netstat/ss + OSINT ASN)"))
    print(green("  [2] Coletor AureaFlow NetFlow v5 (NOC Carrier-Grade Daemon - Porta 2055)"))
    
    modo = ui.input_with_default("Escolha a opção / Choose option", "1")
    if modo == "2":
        _run_netflow_cli_dashboard()
    else:
        _run_local_connections_monitor()


@tool(
    number="22",
    name="OSINT Subdomain Recon",
    category="bgp",
    keywords=["osint", "subdomain", "recon", "dns", "dnssec", "crtsh"],
    tier="free",
    i18n_key="tools.osint_sub.name",
    parameters=[
        {"name": "domain", "label": "Nome de Domínio", "default": "exemplo.com.br", "type": "text"}
    ]
)
def osint_subdomain_recon():
    ui.header(t("tools.osint_sub.title"))
    try:
        dominio = ui.input_with_default(t("ui.enter_domain"), "exemplo.com.br")
        if not dominio:
            print(f"  {red(t('ui.cancelled'))}")
            ui.pause()
            return
        dominio = validators.validate_domain(dominio)
    except ValueError as e:
        print(f"  {red(str(e))}")
        ui.pause()
        return
    
    print(yellow("\nConsultando bases de dados OSINT (Aguarde)..."))
    
    subdominios = set()
    engine_used = ""
    
    # Provider 1: crt.sh (comprehensive but sometimes slow)
    try:
        url_crt = f"https://crt.sh/?q=%25.{dominio}&output=json"
        dados_crt = http_client.fetch_json(url_crt, timeout=8.0)
        if dados_crt and isinstance(dados_crt, list):
            for item in dados_crt:
                name_val = item.get('name_value', '')
                if name_val:
                    for part in name_val.split('\n'):
                        part = part.lower().strip()
                        if part and '*' not in part:
                            if part.endswith(f".{dominio}") or part == dominio:
                                subdominios.add(part)
            if subdominios:
                engine_used = "crt.sh"
    except Exception:
        pass
        
    # Provider 2: Sonar Omnisint (Fast and clean)
    if not subdominios:
        print(yellow("Serviço crt.sh lento/indisponível. Consultando Omnisint Sonar..."))
        try:
            url_sonar = f"https://sonar.omnisint.io/subdomains/{dominio}"
            dados_sonar = http_client.fetch_json(url_sonar, timeout=6.0)
            if dados_sonar and isinstance(dados_sonar, list):
                for s in dados_sonar:
                    s = s.lower().strip()
                    if s and '*' not in s:
                        if s.endswith(f".{dominio}") or s == dominio:
                            subdominios.add(s)
                if subdominios:
                    engine_used = "Omnisint Sonar"
        except Exception:
            pass

    # Provider 3: HackerTarget (Fallback)
    if not subdominios:
        print(yellow("Consultando base de contingência HackerTarget..."))
        try:
            url_ht = f"https://api.hackertarget.com/hostsearch/?q={dominio}"
            res_text = http_client.fetch_text(url_ht, timeout=6.0)
            if res_text and "error" not in res_text.lower() and "api count exceeded" not in res_text.lower():
                for line in res_text.splitlines():
                    parts = line.split(",")
                    if parts:
                        s = parts[0].lower().strip()
                        if s and '*' not in s:
                            if s.endswith(f".{dominio}") or s == dominio:
                                subdominios.add(s)
                if subdominios:
                    engine_used = "HackerTarget"
        except Exception:
            pass
            
    if subdominios:
        print(f"\n {green(f'✓ Encontrados {len(subdominios)} subdomínios via {engine_used}.')}\n")
        sub_list = sorted(list(subdominios))
        for s in sub_list[:30]:
            print(f"  - {s}")
        if len(sub_list) > 30:
            print(dim(f"  ... e mais {len(sub_list) - 30} subdomínios omitidos."))
    else:
        print(f"\n  {red('✗ Falha ao obter dados OSINT de subdomínios. Todas as bases (crt.sh, Omnisint Sonar e HackerTarget) falharam ou retornaram limite atingido.')}")
        
    ui.pause()
