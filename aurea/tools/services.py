"""
aurea.tools.services — Category 2: IP Services & Web Security tools.
"""

import platform
import re
import socket
import json
import time
import concurrent.futures
import struct
import ssl
from datetime import datetime, timezone
from typing import Any

from aurea.core.colors import blue, green, red, yellow, cyan, bold, dim, c
from aurea.core import platform_info, ui, validators, http_client, network
from aurea.i18n import t
from aurea.tools import tool


def _build_dns_query(domain: str) -> bytes:
    """Build a standard DNS A query payload (RFC 1035)."""
    header = struct.pack("!HHHHHH", 0x1234, 0x0100, 1, 0, 0, 0)
    qname = b""
    for part in domain.split("."):
        qname += struct.pack("!B", len(part)) + part.encode()
    qname += b"\x00"
    return header + qname + struct.pack("!HH", 1, 1)


def _query_doh(domain: str, provider_url: str) -> list[str]:
    """Query DoH provider for A records."""
    ips = []
    try:
        url = f"{provider_url}?name={domain}&type=A"
        headers = {"Accept": "application/dns-json"}
        data = http_client.fetch_json(url, headers=headers, timeout=4.0)
        if data and isinstance(data, dict) and "Answer" in data:
            for ans in data["Answer"]:
                if ans.get("type") == 1:  # A record
                    ips.append(ans.get("data"))
    except Exception:
        pass
    return sorted(ips)


@tool(
    number="6",
    name="Public IP & ASN Lookup",
    category="services",
    keywords=["ip", "public", "asn", "geolocation", "carrier"],
    tier="free",
    i18n_key="tools.asn_lookup.name"
)
def asn_lookup():
    ui.header(t("tools.asn_lookup.title"))
    print(f"  {yellow(t('tools.asn_lookup.searching'))}")
    
    dados = http_client.fetch_json("https://ipapi.co/json/", timeout=5.0)
    if dados:
        if "error" not in dados:
            print(f"\n  {green(t('tools.asn_lookup.pub_ip'))}  {dados.get('ip')}")
            print(f"  {green(t('tools.asn_lookup.isp'))}  {dados.get('org')}")
            print(f"  {green(t('tools.asn_lookup.asn'))}  {dados.get('asn')}")
            print(f"  {green(t('tools.asn_lookup.location'))}  {dados.get('city')} - {dados.get('region')} ({dados.get('country_name')})")
        else:
            msg = dados.get("reason", "Desconhecido")
            print("  " + red(t('tools.asn_lookup.fail', msg=msg)))
    else:
        print("  " + red(t('tools.asn_lookup.error', error="Timeout/API Rate Limited")))
    ui.pause()


@tool(
    number="7",
    name="IP Intelligence & Recon",
    category="services",
    keywords=["ip", "intel", "recon", "geolocation", "asn", "carrier"],
    tier="free",
    i18n_key="tools.ip_intel.name",
    parameters=[
        {"name": "target", "label": "IP / Host / Destino", "default": "8.8.8.8", "type": "text"}
    ]
)
def ip_intelligence():
    ui.header(t("tools.ip_intel.title"))
    print(t("tools.ip_intel.desc") + "\n")
    
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

    if alvo.startswith(("192.168.", "10.", "172.16.", "172.17.", "127.", "fe80::")):
        print(f"\n  {yellow(t('tools.ip_intel.private_warning', ip=alvo))}")
        ui.pause()
        return
        
    print(f"\n{cyan(t('tools.ip_intel.querying'))}")
    try:
        url = f"https://ipapi.co/{alvo}/json/"
        dados = http_client.fetch_json(url, timeout=5.0)
        
        if dados and "error" not in dados:
            print(f"\n{cyan('═' * 50)}")
            print(green(t('tools.ip_intel.dossier', ip=dados.get('ip'))))
            print(cyan('═' * 50))
            print(f"  {yellow(t('tools.ip_intel.isp'))} {dados.get('org')}")
            print(f"  {yellow(t('tools.ip_intel.org'))}     {dados.get('org')}")
            print(f"  {yellow(t('tools.ip_intel.asn'))}       {dados.get('asn')} ({dados.get('asn')})")
            print(f"  {yellow(t('tools.ip_intel.location'))}     {dados.get('city')} - {dados.get('region')} ({dados.get('country_name')})")
        else:
            msg = dados.get("reason", "Desconhecido") if dados else "API Error"
            print("  " + red(t('tools.ip_intel.fail', msg=msg)))
    except Exception as e:
        print("  " + red(t('tools.ip_intel.error', error=str(e))))
    ui.pause()


@tool(
    number="8",
    name="DNS Hijacking Detector",
    category="services",
    keywords=["dns", "hijack", "security", "spoofing", "doh", "nxdomain", "poisoning"],
    tier="free",
    i18n_key="tools.dns_hijack.name",
    parameters=[]
)
def dns_hijacking_detector():
    ui.header("DNS HIJACKING & REDIRECT DETECTOR")
    print(cyan("Validação estrita do resolvedor local contra consultas criptografadas DoH.\n"))
    
    local_resolver = network.discover_local_dns()
    print(f"  Resolvedor DNS Local configurado: {yellow(local_resolver)}\n")
    
    print(f"  {blue('1. Efetuando teste de Sequestro NXDOMAIN (Domínio Inexistente)...')}")
    # Generate unique random sub-domain
    import time
    fake_domain = f"aurea-security-check-{int(time.time())}.xyz"
    try:
        ips_fake = socket.gethostbyname_ex(fake_domain)[2]
        print(f"  {red('✗ ALERTA DE SEQUESTRADO NXDOMAIN!')}")
        print(f"    O domínio inexistente {cyan(fake_domain)} resolveu para os IPs: {red(', '.join(ips_fake))}")
        print(f"    {yellow('Nota: Seu provedor está sequestrando falhas de DNS (NXDOMAIN) para exibir anúncios ou portais.')}")
        nxdomain_hijacked = True
    except socket.gaierror:
        print(f"  {green('✓ NXDOMAIN íntegro.')} Domínio inexistente corretamente não resolvido.")
        nxdomain_hijacked = False
        
    print(f"\n  {blue('2. Efetuando teste de Divergência via DoH (DNS-over-HTTPS)...')}")
    target_domain = "one.one.one.one"
    
    # Resolve locally
    local_ips = []
    try:
        local_ips = sorted(socket.gethostbyname_ex(target_domain)[2])
    except Exception as e:
        print(f"    {red(f'Falha ao resolver localmente: {e}')}")
        
    # Resolve via secure DoH (Cloudflare and Quad9)
    cf_ips = _query_doh(target_domain, "https://cloudflare-dns.com/dns-query")
    q9_ips = _query_doh(target_domain, "https://dns.quad9.net/dns-query")
    
    # Compare results
    if local_ips and (cf_ips or q9_ips):
        # We can construct the authoritative set from secure providers
        auth_ips = set(cf_ips + q9_ips)
        # Intersection between local and authoritative
        intersection = set(local_ips).intersection(auth_ips)
        
        print(f"    - IP Local:       {cyan(', '.join(local_ips))}")
        if cf_ips:
            print(f"    - IP Cloudflare:  {green(', '.join(cf_ips))}")
        if q9_ips:
            print(f"    - IP Quad9:       {green(', '.join(q9_ips))}")
            
        if not intersection:
            print(f"\n  {red('✗ ALERTA DE DIVERGÊNCIA / DNS HIJACKING DETECTADO!')}")
            print(f"    {yellow('Nota: As respostas DNS divergem totalmente! As consultas DNS da porta 53 estão sendo interceptadas ou modificadas.')}")
            divergence_hijacked = True
        else:
            print(f"  {green('✓ Resolução íntegra.')} IPs locais equivalentes às consultas DoH seguras.")
            divergence_hijacked = False
    else:
        print(f"  {yellow('⚠ Teste de DoH inconclusivo por indisponibilidade de internet/rede.')}")
        divergence_hijacked = False
        
    print(f"\n{cyan('═' * 60)}")
    if nxdomain_hijacked or divergence_hijacked:
        print(red(f"  STATUS FINAL: {bold('VULNERÁVEL / HIJACKED')}"))
        print(f"  Recomendação: Altere as configurações de DNS do roteador para DoH ou servidores seguros (1.1.1.1 / 8.8.8.8).")
    else:
        print(green(f"  STATUS FINAL: {bold('SEGURO / ÍNTEGRO')}"))
        print(f"  Nenhum sequestro ou redirecionamento de DNS foi detectado no enlace atual.")
    print(cyan("═" * 60) + "\n")
    
    ui.pause()


@tool(
    number="9",
    name="CGNAT Port Exhaustion Simulator",
    category="services",
    keywords=["cgnat", "exhaustion", "nat", "ports", "sockets", "concurrency", "timeouts"],
    tier="free",
    i18n_key="tools.cgnat_sim.name",
    parameters=[
        {"name": "target", "label": "Host de Teste (IP/Domínio)", "default": "google.com", "type": "text"},
        {"name": "connections", "label": "Número de Sockets Simultâneos", "default": "150", "type": "number"}
    ]
)
def cgnat_exhaustion_simulator():
    ui.header("CGNAT PORT EXHAUSTION SIMULATOR")
    print(cyan("Simulação controlada de rajada de sockets para teste de limites de portas e CGNAT.\n"))
    
    try:
        host = ui.input_with_default("Host de Teste", "google.com")
        if not host:
            print(f"  {red(t('ui.cancelled'))}")
            ui.pause()
            return
        host = validators.validate_host(host)
        
        conns_str = ui.input_with_default("Número de Sockets Simultâneos (máx: 300)", "150")
        conns = int(conns_str)
        if conns < 10 or conns > 300:
            conns = 150
    except ValueError as e:
        print(f"  {red(str(e))}")
        ui.pause()
        return

    print(f"\n{yellow(f'Iniciando simulação de {conns} sockets paralelos rápidos para {host}:80...')}\n")
    
    success_count = 0
    fail_count = 0
    rtts = []
    
    def probe_socket():
        nonlocal success_count, fail_count
        start = time.time()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2.0)
                res = s.connect_ex((host, 80))
                if res == 0:
                    rtts.append((time.time() - start) * 1000)
                    success_count += 1
                else:
                    fail_count += 1
        except Exception:
            fail_count += 1

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(probe_socket) for _ in range(conns)]
        concurrent.futures.wait(futures)
        
    total = success_count + fail_count
    fail_pct = (fail_count / total * 100) if total > 0 else 0.0
    avg_rtt = (sum(rtts) / len(rtts)) if rtts else 0.0
    
    print(f"\n{cyan('═' * 60)}")
    print(green("✓ SIMULAÇÃO DE EXAUSTÃO CONCLUÍDA"))
    print(cyan('═' * 60))
    print(f"  - Conexões Iniciadas:  {total}")
    print(f"  - Conexões Bem-Sucedidas: {green(str(success_count))}")
    print(f"  - Conexões Falhas/Timeout: {red(str(fail_count))} ({fail_pct:.1f}%)")
    if rtts:
        print(f"  - Latência Média Sockets: {cyan(f'{avg_rtt:.1f} ms')}")
        
    print(f"\n  {bold('Diagnóstico Operacional:')}")
    if fail_pct > 15.0:
        print(f"  - {red('SINAL DE EXAUSTÃO OU BLOQUEIO ATIVO!')}")
        print(f"    Uma taxa de falha de {fail_pct:.1f}% indica que o roteador de borda, CGNAT do provedor ou")
        print(f"    firewall do destino está limitando a alocação rápida de portas efêmeras.")
    else:
        print(f"  - {green('Sistemas de NAT e Conectividade íntegros.')}")
        print(f"    A rede tolerou perfeitamente a rajada sem sofrer esgotamento de portas ou drop de pacotes.")
    print(cyan("═" * 60) + "\n")
    
    ui.pause()


@tool(
    number="10",
    name="Local DNS Benchmark",
    category="services",
    keywords=["dns", "benchmark", "resolver", "latency", "resolving"],
    tier="free",
    i18n_key="tools.dns_benchmark.name",
    parameters=[
        {"name": "domain", "label": "Domínio para Teste", "default": "google.com", "type": "text"}
    ]
)
def dns_benchmark():
    ui.header(t("tools.dns_benchmark.title"))
    print(t("tools.dns_benchmark.desc") + "\n")
    
    dominio = ui.input_with_default(t("ui.test_domain"), "google.com")
    
    servidores = {
        "Google DNS":  "8.8.8.8",
        "Cloudflare":  "1.1.1.1",
        "Quad9":       "9.9.9.9",
        "OpenDNS":     "208.67.222.222",
    }
    
    dns_atual = network.discover_local_dns()
    
    if not re.match(r'^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$', dns_atual):
        dns_atual = "127.0.0.1"

    servidores[t("tools.dns_benchmark.gateway_label")] = dns_atual
    
    print(f"\n  {bold(t('tools.dns_benchmark.server')):<22} | {bold(t('tools.dns_benchmark.time'))}")
    print("  " + "─" * 42)
    
    payload = _build_dns_query(dominio)
    
    for nome, ip_dns in servidores.items():
        s = None
        nome_padded = f"{nome:<22}"
        nome_formatado = cyan(nome_padded) if t("tools.dns_benchmark.gateway_label") in nome else nome_padded
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(2.0)
            
            inicio = time.time()
            s.sendto(payload, (ip_dns, 53))
            s.recvfrom(1024)
            tempo = (time.time() - inicio) * 1000
            
            cor_t = green if tempo < 20 else (yellow if tempo < 50 else red)
            sufixo = f" {cyan(f'({ip_dns})')}" if t("tools.dns_benchmark.gateway_label") in nome else ""
            
            print(f"  {nome_formatado} | {cor_t(f'{tempo:.2f} ms')}{sufixo}")
            
        except Exception:
            print(f"  {nome_formatado} | {red(t('tools.dns_benchmark.timeout'))}")
            
        finally:
            if s:
                s.close()
                
    print(f"\n  {cyan(t('tools.dns_benchmark.tip'))}")
    ui.pause()


def _parse_first_a_record(data: bytes) -> str | None:
    try:
        idx = 12
        while idx < len(data):
            length = data[idx]
            if length == 0:
                idx += 1
                break
            elif (length & 0xC0) == 0xC0:
                idx += 2
                break
            idx += 1 + length
        
        idx += 4
        
        num_answers = struct.unpack("!H", data[6:8])[0]
        
        for _ in range(num_answers):
            if idx >= len(data):
                break
            while idx < len(data):
                val = data[idx]
                if (val & 0xC0) == 0xC0:
                    idx += 2
                    break
                elif val == 0:
                    idx += 1
                    break
                idx += 1 + val
            
            if idx + 10 > len(data):
                break
                
            rtype, rclass, ttl, rdlength = struct.unpack("!HHIH", data[idx:idx+10])
            idx += 10
            
            if idx + rdlength > len(data):
                break
                
            if rtype == 1 and rdlength == 4:
                ip_bytes = data[idx:idx+4]
                return f"{ip_bytes[0]}.{ip_bytes[1]}.{ip_bytes[2]}.{ip_bytes[3]}"
                
            idx += rdlength
    except Exception:
        pass
    return None


@tool(
    number="11",
    name="DNS Propagation Checker",
    category="services",
    keywords=["dns", "propagation", "checker", "parallel", "resolvers", "dig"],
    tier="free",
    i18n_key="tools.dns_prop.name",
    parameters=[
        {"name": "domain", "label": "Nome de Domínio", "default": "google.com", "type": "text"}
    ]
)
def dns_propagation():
    ui.header(t("tools.dns_prop.title"))
    try:
        domain = ui.input_with_default(t("ui.enter_domain"), "google.com")
        if not domain:
            print(f"  {red(t('ui.cancelled'))}")
            ui.pause()
            return
        domain = validators.validate_domain(domain)
    except ValueError as e:
        print(f"  {red(str(e))}")
        ui.pause()
        return

    dns_servers = {
        "Google DNS": "8.8.8.8",
        "Cloudflare": "1.1.1.1",
        "Quad9": "9.9.9.9",
        "OpenDNS": "208.67.222.222",
        "Level3": "4.2.2.2"
    }
    
    print(f"\n{yellow(t('tools.dns_benchmark.time'))} - verificando propagação global em paralelo...\n")
    
    def query_dns_server(server_name: str, server_ip: str):
        try:
            payload = _build_dns_query(domain)
            
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.settimeout(2.0)
                s.sendto(payload, (server_ip, 53))
                data, _ = s.recvfrom(1024)
            
            ip_resp = _parse_first_a_record(data)
            if ip_resp:
                return server_name, ip_resp
            return server_name, "N/A"
        except Exception:
            return server_name, "Timeout/No Answer"

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(query_dns_server, name, ip) for name, ip in dns_servers.items()]
        for future in concurrent.futures.as_completed(futures):
            name, res = future.result()
            print(f"  {green('✓')} {t('tools.dns_prop.result', server=name, type='A', result=res)}")
            
    ui.pause()


@tool(
    number="12",
    name="DNSSEC Validation",
    category="services",
    keywords=["dnssec", "dns", "security", "validation", "cryptography"],
    tier="free",
    i18n_key="tools.dnssec.name",
    parameters=[
        {"name": "domain", "label": "Nome de Domínio", "default": "registro.br", "type": "text"}
    ]
)
def dnssec_validation():
    ui.header(t("tools.dnssec.title"))
    print(f"\n{cyan(t('tools.dnssec.test_local'))}")
    
    try:
        socket.gethostbyname("google.com")
    except socket.gaierror:
        print(f"  {red(t('tools.dnssec.no_internet'))}")
        ui.pause()
        return

    try:
        socket.gethostbyname("sigok.verteiltesysteme.net")
        try:
            socket.gethostbyname("sigfail.verteiltesysteme.net")
            print(f"  {red(t('tools.dnssec.no_validate'))}")
        except socket.gaierror:
            print(f"  {green(t('tools.dnssec.validates'))}")
    except socket.gaierror:
        print(f"  {yellow(t('tools.dnssec.comm_fail'))}")

    print(f"\n{cyan(t('tools.dnssec.test_external'))}")
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

    url = f"https://dns.google/resolve?name={dominio}&type=DS"
    try:
        dados = http_client.fetch_json(url, timeout=5.0)
        if dados and dados.get("Status") == 0 and "Answer" in dados:
            print(f"  {green(t('tools.dnssec.has_ds', domain=dominio))}")
            if dados.get("AD"):
                print(f"  {green(t('tools.dnssec.authenticated'))}")
        else:
            print(f"  {yellow(t('tools.dnssec.no_dnssec'))}")
    except Exception as e:
        print(f"  {red(t('tools.dnssec.api_fail', error=str(e)))}")
    ui.pause()


@tool(
    number="13",
    name="SSL/TLS Cryptographic Chain Auditor",
    category="services",
    keywords=["ssl", "tls", "certificate", "inspector", "ciphers", "tls13", "validation", "pci-dss"],
    tier="free",
    i18n_key="tools.ssl_inspector.name",
    parameters=[
        {"name": "domain", "label": "Nome de Domínio", "default": "google.com", "type": "text"}
    ]
)
def ssl_inspector():
    import ssl
    ui.header("AUREA SSL/TLS CRYPTOGRAPHIC PROTOCOL & CHAIN AUDITOR")
    
    try:
        host = ui.input_with_default(t("ui.enter_domain"), "google.com")
        if not host:
            print(f"  {red(t('ui.cancelled'))}")
            ui.pause()
            return
        host = validators.validate_domain(host)
    except ValueError as e:
        print(f"  {red(str(e))}")
        ui.pause()
        return

    print(f"\n{yellow('Iniciando auditoria criptográfica profunda do canal SSL/TLS...')} (Aguarde)\n")
    
    # 1. Check TLS versions support
    tls_versions = [
        ("TLSv1.0", ssl.TLSVersion.TLSv1, "PCI-DSS Vulnerável"),
        ("TLSv1.1", ssl.TLSVersion.TLSv1_1, "PCI-DSS Depreciado"),
        ("TLSv1.2", ssl.TLSVersion.TLSv1_2, "Seguro (Padrão)"),
        ("TLSv1.3", ssl.TLSVersion.TLSv1_3, "Recomendado (Ultra-Seguro)")
    ]
    
    print(cyan("1. Auditoria de Versões do Protocolo TLS:"))
    print(cyan("─" * 60))
    for name, enum_val, desc in tls_versions:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        try:
            ctx.minimum_version = enum_val
            ctx.maximum_version = enum_val
            with socket.create_connection((host, 443), timeout=2.0) as sock:
                with ctx.wrap_socket(sock, server_hostname=host) as ss:
                    status = green("SUPORTADO") if "Seguro" in desc else yellow("SUPORTADO (DEPRECIADO)")
                    print(f"  • {name:<10} | Status: {status:<24} | {desc}")
        except Exception:
            print(f"  • {name:<10} | Status: {red('NÃO SUPORTADO'):<24} | Bloqueado com segurança")
            
    print()

    # 2. Main connection to grab active cert and cipher details
    cert_valid = True
    parsed_cert = None
    cipher_info = None
    
    # Try with validation first
    ctx = ssl.create_default_context()
    ssl_sock = None
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(4.0)
    
    try:
        ssl_sock = ctx.wrap_socket(s, server_hostname=host)
        ssl_sock.connect((host, 443))
        parsed_cert = ssl_sock.getpeercert()
        cipher_info = ssl_sock.cipher()
    except Exception:
        cert_valid = False
    finally:
        if ssl_sock:
            try:
                ssl_sock.close()
            except Exception:
                pass
        else:
            try:
                s.close()
            except Exception:
                pass

    # If verification failed, connect without verification for cipher audit
    if not parsed_cert:
        ctx_none = ssl.create_default_context()
        ctx_none.check_hostname = False
        ctx_none.verify_mode = ssl.CERT_NONE
        s_none = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s_none.settimeout(4.0)
        ssl_sock_none = None
        try:
            ssl_sock_none = ctx_none.wrap_socket(s_none, server_hostname=host)
            ssl_sock_none.connect((host, 443))
            cipher_info = ssl_sock_none.cipher()
        except Exception as e:
            print(f"  {red(f'Falha ao conectar via SSL/TLS: {e}')}")
            ui.pause()
            return
        finally:
            if ssl_sock_none:
                try:
                    ssl_sock_none.close()
                except Exception:
                    pass
            else:
                try:
                    s_none.close()
                except Exception:
                    pass

    # Render active cipher info
    if cipher_info:
        cipher_name, tls_version, secret_bits = cipher_info
        is_weak = any(x in cipher_name.upper() for x in ("RC4", "3DES", "DES", "MD5", "NULL", "EXPORT", "anon"))
        cipher_fmt = red(f"{cipher_name} (FRACA/VULNERÁVEL)") if is_weak else green(f"{cipher_name} (FORTE)")
        
        print(cyan("2. Canal Criptográfico Ativo & Cipher Audit:"))
        print(cyan("─" * 60))
        print(f"  • Status de Validação: {green('VÁLIDO / CONFIÁVEL') if cert_valid else red('INVÁLIDO, EXPIRADO OU NÃO CONFIÁVEL!')}")
        print(f"  • Cipher Ativa:   {cipher_fmt}")
        print(f"  • TLS Negociado:  {cyan(tls_version)}")
        print(f"  • Força de Chave: {cyan(f'{secret_bits} bits')}")
        print()

    # Render X.509 cert info
    if parsed_cert:
        try:
            subject = dict(x[0] for x in parsed_cert['subject'])
            issuer = dict(x[0] for x in parsed_cert['issuer'])
            
            cn = subject.get('commonName', 'N/A')
            issuer_cn = issuer.get('commonName', 'N/A')
            
            not_before = parsed_cert.get('notBefore')
            not_after = parsed_cert.get('notAfter')
            
            fmt = "%b %d %H:%M:%S %Y %Z"
            date_to = datetime.strptime(not_after, fmt).replace(tzinfo=timezone.utc)
            date_from = datetime.strptime(not_before, fmt).replace(tzinfo=timezone.utc)
            
            now = datetime.now(timezone.utc)
            days_left = (date_to - now).days
            
            sans = [x[1] for x in parsed_cert.get('subjectAltName', []) if x[0] == 'DNS']
            sans_str = ", ".join(sans[:5]) + ("..." if len(sans) > 5 else "")
            
            print(cyan("3. Dossiê de Certificação X.509:"))
            print(cyan("─" * 60))
            print(f"  • CN (Common Name):  {yellow(cn)}")
            print(f"  • Entidade Emissora: {yellow(issuer_cn)}")
            print(f"  • Alternativos (SAN): {cyan(sans_str if sans_str else 'Nenhum')}")
            print(f"  • Válido De:         {cyan(not_before)}")
            print(f"  • Válido Até:        {cyan(not_after)}")
            
            if days_left < 0:
                print(f"  • Dias Restantes:    {red('EXPIRADO')}")
            elif days_left < 30:
                print(f"  • Dias Restantes:    {yellow(f'{days_left} (EXPIRA EM BREVE)')}")
            else:
                print(f"  • Dias Restantes:    {green(str(days_left))}")
        except Exception as e:
            print(f"  {red(f'Falha ao extrair metadados do certificado: {e}')}")
    else:
        print(cyan("3. Dossiê de Certificação X.509:"))
        print(cyan("─" * 60))
        print(f"  {red('✗ Não foi possível extrair metadados X.509 porque o certificado não passou na validação de confiança.')}")
            
    ui.pause()


@tool(
    number="14",
    name="HTTP Security Headers Scan",
    category="services",
    keywords=["http", "security", "headers", "scan", "armor", "clickjacking"],
    tier="free",
    i18n_key="tools.sec_headers.name",
    parameters=[
        {"name": "target", "label": "URL Completa (ex: https://registro.br)", "default": "https://registro.br", "type": "text"}
    ]
)
def security_headers_scan():
    ui.header(t("tools.sec_headers.title"))
    print(t("tools.sec_headers.desc") + "\n")
    try:
        alvo = ui.input_with_default(t("ui.enter_url"), "https://registro.br")
        if not alvo:
            print(f"  {red(t('ui.cancelled'))}")
            ui.pause()
            return
        alvo = validators.validate_url(alvo)
    except ValueError as e:
        print(f"  {red(str(e))}")
        ui.pause()
        return

    print(f"\n{cyan(t('tools.sec_headers.analyzing', url=alvo))}\n")
    
    headers_esperados = {
        "Strict-Transport-Security": "Força navegadores a usarem apenas HTTPS (HSTS)",
        "Content-Security-Policy":   "Previne injeção de scripts maliciosos (XSS)",
        "X-Frame-Options":           "Protege contra roubo de cliques (Clickjacking)",
        "X-Content-Type-Options":    "Evita detecção de tipos de arquivo forjados (MIME Sniffing)",
        "Referrer-Policy":           "Controla o vazamento da origem do tráfego",
    }
    
    res = http_client.fetch_headers(alvo, timeout=8.0)
    if res:
        headers_recv, status_code = res
        print(cyan("═" * 50))
        print(green(t("tools.sec_headers.report")))
        print(cyan("═" * 50) + "\n")
        
        server = headers_recv.get("server", t("tools.sec_headers.server_hidden"))
        if server != t("tools.sec_headers.server_hidden"):
            print(f"  {yellow(t('tools.sec_headers.server_exposed', server=server))}")
        else:
            print(f"  {green(t('tools.sec_headers.server_hidden'))}")
        print()
        
        score = 0
        for header, descricao in headers_esperados.items():
            if header.lower() in headers_recv:
                print(f"  {green(f'✓ {header}')}")
                print(f"      └─ {cyan(descricao)}")
                score += 1
            else:
                print(f"  {red(f'✗ {header}')} ({t('tools.sec_headers.vulnerable')})")
                print(f"      └─ {yellow(t('tools.sec_headers.missing', desc=descricao))}")
                
        print(f"\n  {cyan(t('tools.sec_headers.score', score=score, total=len(headers_esperados)))}")
        if score == len(headers_esperados):
            print(f"  {green(t('tools.sec_headers.excellent'))}")
        elif score >= 3:
            print(f"  {yellow(t('tools.sec_headers.regular'))}")
        else:
            print(f"  {red(t('tools.sec_headers.critical'))}")
    else:
        print(f"  {red(t('tools.sec_headers.fail', error='Connection failed'))}")
    ui.pause()


@tool(
    number="15",
    name="Banner Grabbing",
    category="services",
    keywords=["banner", "grabbing", "fingerprint", "service", "version"],
    tier="free",
    i18n_key="tools.banner_grab.name",
    parameters=[
        {"name": "target", "label": "IP / Host / Destino", "default": "8.8.8.8", "type": "text"},
        {"name": "port", "label": "Porta de Conexão", "default": "80", "type": "number"}
    ]
)
def banner_grabbing():
    ui.header(t("tools.banner_grab.title"))
    print(t("tools.banner_grab.desc") + "\n")
    try:
        alvo = ui.input_with_default(t("ui.enter_ip"))
        if not alvo:
            print(f"  {red(t('ui.cancelled'))}")
            ui.pause()
            return
        alvo = validators.validate_host(alvo)
        
        porta_str = ui.input_with_default(t("ui.enter_port"))
        porta = validators.validate_port(porta_str)
    except ValueError as e:
        print(f"  {red(str(e))}")
        ui.pause()
        return

    s = None
    try:
        print(f"\n{cyan(t('tools.banner_grab.scanning', host=alvo, port=porta))}")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3.0)
        if porta in (443, 8443):
            print("  Envelopando socket com TLS/SSL...")
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            s = ctx.wrap_socket(s, server_hostname=alvo)
        resultado = s.connect_ex((alvo, porta))
        if resultado != 0:
            print(f"  {red(t('tools.banner_grab.closed'))}")
            return
        print(f"  {green(t('tools.banner_grab.connected'))}")
        banner = b""
        if porta in (22, 21, 25, 110, 23):
            try:
                banner = s.recv(1024)
            except socket.timeout:
                pass
        if not banner:
            try:
                gatilho = f"HEAD / HTTP/1.0\r\nHost: {alvo}\r\n\r\n"
                s.sendall(gatilho.encode())
                banner = s.recv(2048)
            except Exception:
                pass
        if banner:
            texto_limpo = banner.decode('utf-8', errors='ignore').strip()
            print(f"\n{yellow(t('tools.banner_grab.captured'))}")
            for linha in texto_limpo.split('\n')[:5]:
                print(f"  {linha.strip()}")
            print(yellow("─" * 24))
        else:
            print(f"  {yellow(t('tools.banner_grab.no_banner'))}")
    except Exception as e:
        print(f"  {red(t('tools.banner_grab.fail', error=str(e)))}")
    finally:
        if s:
            s.close()
    ui.pause()


@tool(
    number="16",
    name="DNS Spoofing Auditor",
    category="services",
    keywords=["dns", "spoofing", "spf", "dmarc", "phishing", "email"],
    tier="free",
    i18n_key="tools.spoofing_audit.name",
    parameters=[
        {"name": "domain", "label": "Nome de Domínio", "default": "gmail.com", "type": "text"}
    ]
)
def spoofing_audit():
    ui.header(t("tools.spoofing_audit.title"))
    print(t("tools.spoofing_audit.desc") + "\n")
    try:
        dominio = ui.input_with_default(t("ui.enter_domain"), "gmail.com")
        if not dominio:
            print(f"  {red(t('ui.cancelled'))}")
            ui.pause()
            return
        dominio = validators.validate_domain(dominio)
    except ValueError as e:
        print(f"  {red(str(e))}")
        ui.pause()
        return

    print(f"\n{cyan(t('tools.spoofing_audit.querying'))}\n")
    
    url_spf  = f"https://dns.google/resolve?name={dominio}&type=TXT"
    spf_reg  = ""
    try:
        dados = http_client.fetch_json(url_spf, timeout=5.0)
        if dados and "Answer" in dados:
            for ans in dados["Answer"]:
                txt = ans.get('data', '')
                if "v=spf1" in txt:
                    spf_reg = txt.strip('"')
                    break
        if spf_reg:
            print(f"  {green(t('tools.spoofing_audit.spf_found'))} {spf_reg}")
            if "-all" in spf_reg:
                print(f"      └─ {green(t('tools.spoofing_audit.spf_hard'))}")
            elif "~all" in spf_reg:
                print(f"      └─ {yellow(t('tools.spoofing_audit.spf_soft'))}")
            else:
                print(f"      └─ {red(t('tools.spoofing_audit.spf_neutral'))}")
        else:
            print(f"  {red(t('tools.spoofing_audit.spf_missing'))}")
    except Exception as e:
        print(f"  {red(t('tools.spoofing_audit.spf_fail', error=str(e)))}")
        
    print()
    url_dmarc = f"https://dns.google/resolve?name=_dmarc.{dominio}&type=TXT"
    dmarc_reg = ""
    try:
        dados = http_client.fetch_json(url_dmarc, timeout=5.0)
        if dados and "Answer" in dados:
            for ans in dados["Answer"]:
                txt = ans.get('data', '')
                if "v=DMARC1" in txt:
                    dmarc_reg = txt.strip('"')
                    break
        if dmarc_reg:
            print(f"  {green(t('tools.spoofing_audit.dmarc_found'))} {dmarc_reg}")
            if "p=reject" in dmarc_reg:
                print(f"      └─ {green(t('tools.spoofing_audit.dmarc_reject'))}")
            elif "p=quarantine" in dmarc_reg:
                print(f"      └─ {yellow(t('tools.spoofing_audit.dmarc_quarantine'))}")
            elif "p=none" in dmarc_reg:
                print(f"      └─ {red(t('tools.spoofing_audit.dmarc_none'))}")
        else:
            print(f"  {red(t('tools.spoofing_audit.dmarc_missing'))}")
    except Exception as e:
        print(f"  {red(t('tools.spoofing_audit.dmarc_fail', error=str(e)))}")
        
    print(f"\n  {cyan(t('tools.spoofing_audit.dkim_note'))}")
    ui.pause()


@tool(
    number="17",
    name="DNS Record Deep Inspector",
    category="services",
    keywords=["dns", "zone", "records", "dig", "bind", "mx", "txt", "dmarc", "dnssec"],
    tier="free",
    i18n_key="tools.dns_deep_inspector.name",
    parameters=[
        {"name": "domain", "label": "Nome de Domínio", "default": "google.com", "type": "text"}
    ]
)
def dns_deep_inspector():
    ui.header("DNS RECORD DEEP INSPECTOR")
    print(cyan(t("tools.dns_deep_inspector.desc") + "\n"))
    
    try:
        domain = ui.input_with_default(t("ui.enter_domain"), "google.com")
        if not domain:
            print(f"  {red(t('ui.cancelled'))}")
            ui.pause()
            return
        domain = validators.validate_domain(domain)
    except ValueError as e:
        print(f"  {red(str(e))}")
        ui.pause()
        return
        
    print(f"\n{yellow('Consultando registros via Google DoH API...')} (Aguarde)\n")
    
    record_types = ["A", "AAAA", "MX", "TXT", "NS", "SOA", "DS", "DNSKEY"]
    
    print(cyan("═" * 80))
    print(bold(f"RELATÓRIO DNS COMPLETO PARA: {domain.upper()}"))
    print(cyan("═" * 80))
    
    for rtype in record_types:
        url = f"https://dns.google/resolve?name={domain}&type={rtype}"
        try:
            res = http_client.fetch_json(url, timeout=5.0)
            if res and "Answer" in res:
                print(f"\n  {bold(green(f'» Registros {rtype}:'))}")
                for ans in res["Answer"]:
                    data = ans.get("data", "").strip('"')
                    ttl = ans.get("TTL", 0)
                    print(f"    - {yellow(data)} (TTL: {cyan(str(ttl))}s)")
            else:
                print(f"  {dim(f'- Nenhum registro {rtype} encontrado.')}")
        except Exception as e:
            print(f"  {red(f'Erro ao consultar {rtype}: {e}')}")
            
    dmarc_url = f"https://dns.google/resolve?name=_dmarc.{domain}&type=TXT"
    try:
        res = http_client.fetch_json(dmarc_url, timeout=5.0)
        if res and "Answer" in res:
            print(f"\n  {bold(green('» Diretriz DMARC:'))}")
            for ans in res["Answer"]:
                data = ans.get("data", "").strip('"')
                if "v=DMARC1" in data:
                    print(f"    - {yellow(data)}")
    except Exception:
        pass
        
    print(cyan("\n" + "═" * 80))
    ui.pause()
