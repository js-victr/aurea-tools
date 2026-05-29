"""
aurea.core.network — Shared network utilities (DNS discovery, ASN lookup).
"""

import json
import socket
import time

from aurea.core.platform_info import is_windows, is_termux

# --- Well-known org mapping ---

KNOWN_ORGS = {
    "GOOGLE": "Google (YouTube/Services)",
    "FACEBOOK": "Meta (WhatsApp/Instagram)",
    "META": "Meta (WhatsApp/Instagram)",
    "AMAZON": "Amazon AWS",
    "AWS": "Amazon AWS",
    "MICROSOFT": "Microsoft / Azure",
    "AZURE": "Microsoft / Azure",
    "NETFLIX": "Netflix CDN",
    "CLOUDFLARE": "Cloudflare",
    "AKAMAI": "Akamai CDN",
    "APPLE": "Apple",
}

def get_asn_org(ip: str, cache: dict) -> str:
    """
    Lookup ASN organization for an IP address.

    Uses ipapi.co (HTTPS) with caching. Rate limiting handled by http_client.
    """
    if ip.startswith(("192.168.", "10.", "127.", "0.", "169.254.", "[::1]", "fe80:")):
        return "Local Network"

    if ip in cache:
        return cache[ip]

    try:
        from aurea.core.http_client import fetch_json
        data = fetch_json(
            f"http://ip-api.com/json/{ip}",
            timeout=2.0, retries=1,
            user_agent="AureaTools/2.0 (NetworkDiag)",
        )
        if data is None:
            cache[ip] = "Rate Limit"
            return "Rate Limit"

        org = data.get("org", data.get("isp", ""))
        if not org:
            cache[ip] = "Generic ISP"
            return "Generic ISP"

        org_upper = org.upper()
        for term, friendly in KNOWN_ORGS.items():
            if term in org_upper:
                cache[ip] = friendly
                return friendly

        cache[ip] = org
        return org

    except Exception:
        cache[ip] = "Timeout/Error"
        return "Timeout/Error"


def discover_local_dns() -> str:
    """
    Universal DNS discovery engine for Windows, Linux, and Android/Termux.

    Returns the local DNS server IP.
    """
    import subprocess

    # 1. Windows
    if is_windows():
        try:
            ps_cmd = (
                'powershell -Command "'
                "(Get-DnsClientServerAddress -AddressFamily IPv4 | "
                "Where-Object {$_.ServerAddresses -ne $null}).ServerAddresses[0]\""
            )
            res = subprocess.check_output(ps_cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
            dns = res.strip()
            if dns and not dns.startswith("127."):
                return dns
        except Exception:
            try:
                gw_cmd = 'powershell -Command "(Get-NetRoute -DestinationPrefix \'0.0.0.0/0\').NextHop"'
                return subprocess.check_output(gw_cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
            except Exception:
                return "127.0.0.1"

    # 2. Linux & Termux
    else:
        try:
            res = subprocess.check_output(
                "nmcli -t -f IP4.DNS dev show", shell=True, text=True, stderr=subprocess.DEVNULL
            )
            for line in res.split("\n"):
                ip = line.replace("IP4.DNS:", "").strip()
                if ip and not ip.startswith("127."):
                    return ip
        except Exception:
            pass

        import os

        if os.path.exists("/etc/resolv.conf"):
            try:
                with open("/etc/resolv.conf", "r") as f:
                    for line in f:
                        if "nameserver" in line:
                            ip = line.split()[1].strip()
                            if not ip.startswith("127."):
                                return ip
            except Exception:
                pass

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            my_ip = s.getsockname()[0]
            s.close()
            return f"{my_ip.rsplit('.', 1)[0]}.1"
        except Exception:
            return "127.0.0.1"

    return "127.0.0.1"


# --- Well-known ports ---

WELL_KNOWN_PORTS = {
    "80": "HTTP",
    "443": "HTTPS",
    "53": "DNS",
    "22": "SSH",
    "21": "FTP",
    "3389": "RDP",
    "8080": "HTTP-ALT",
    "110": "POP3",
    "993": "IMAP",
    "25": "SMTP",
    "587": "SMTP-TLS",
    "143": "IMAP",
    "8443": "HTTPS-ALT",
    "179": "BGP",
    "161": "SNMP",
    "162": "SNMP-TRAP",
    "514": "SYSLOG",
    "1723": "PPTP",
    "1701": "L2TP",
    "500": "IKE/IPsec",
    "4500": "IPsec-NAT",
}
