"""
aurea.tools.descriptions — Simplified English-only descriptions and usage manuals for all 31 Aurea tools.
"""

TOOL_GUIDES = {
    "1": {
        "desc": "Continuous path routing with real-time packet loss, average latency, and jitter tracking.",
        "use": "Enter the target <ip> or <domain>. The tool continuously sends packets. Press Ctrl+C to stop."
    },
    "2": {
        "desc": "Find the exact maximum transmission unit (MTU) size without causing fragmentation on your link.",
        "use": "Enter the target <ip> or <domain>. The tool pings with the Don't Fragment (DF) bit set, testing from 1200 to 1500 bytes."
    },
    "3": {
        "desc": "Fast TCP port scanner that identifies open ports and attempts to capture service banners.",
        "use": "Enter the target <ip> or <domain>. The tool scans the 1000 most common ports and prints open sockets."
    },
    "4": {
        "desc": "Tests latency to major cloud providers and CDN edge networks.",
        "use": "Start the tool to see live round-trip time (RTT) measurements to global cloud infrastructure."
    },
    "5": {
        "desc": "Plan subnets and detect overlay conflicts across IPv4/IPv6 ranges in VPNs, tunnels, or peers.",
        "use": "Enter your active <subnets> and the proposed <subnet> in CIDR format. The tool detects overlapping IPs and highlights free blocks."
    },
    "6": {
        "desc": "Identify your current public IP, internet service provider (ISP), transit ASN, and estimated location.",
        "use": "Launch the tool to retrieve a clean summary of your current connection metadata."
    },
    "7": {
        "desc": "Lookup geolocation, reverse DNS, hosting carrier, and WHOIS records for any public IP address.",
        "use": "Provide any target <ip> or public <domain> to fetch its routing and carrier profile."
    },
    "8": {
        "desc": "Checks for local DNS interception or spoofing by comparing queries against secure DoH resolvers.",
        "use": "Select the tool. It verifies NXDOMAIN replies and looks for differences with public secure endpoints."
    },
    "9": {
        "desc": "Simulate concurrent socket burst requests to check session capacity limits and CGNAT timeouts.",
        "use": "Enter target <ip> or <domain> and the number of concurrent connections in <integer> format to measure latencies and connection drops."
    },
    "10": {
        "desc": "Benchmark DNS query speeds by comparing your current resolver against global public resolvers.",
        "use": "Enter a test <domain> to view the response times in milliseconds."
    },
    "11": {
        "desc": "Query DNS 'A' records across multiple global public resolvers in parallel to verify propagation.",
        "use": "Type the <domain> and watch responses from global servers update in real-time."
    },
    "12": {
        "desc": "Verify DNSSEC cryptographic records (DS, DNSKEY) and check if your local resolver validates them.",
        "use": "Enter a <domain> to audit its secure DNS delegation and cryptographic signatures."
    },
    "13": {
        "desc": "Audit SSL/TLS certificates. Displays validity dates, issuer information, protocol support, and weak ciphers.",
        "use": "Provide a <domain> to query port 443 and download its X.509 certificate metadata."
    },
    "14": {
        "desc": "Scan HTTP security response headers like HSTS, CSP, X-Frame-Options, and X-Content-Type-Options.",
        "use": "Provide a full <url> with protocol to audit security configurations."
    },
    "15": {
        "desc": "Connect to custom ports and display the raw service banner returned by the server.",
        "use": "Provide target <ip> or <domain> along with a <port> number. The tool prints the server's reply."
    },
    "16": {
        "desc": "Inspect active SPF and DMARC DNS records to verify email domain spoofing defenses.",
        "use": "Enter a <domain> to view its published TXT records and check if it enforces strict policies."
    },
    "17": {
        "desc": "Perform comprehensive DNS lookups to extract all core records (A, AAAA, MX, TXT, NS, SOA, DS) at once.",
        "use": "Enter the <domain> name. The tool queries secure endpoints and returns a structured list."
    },
    "18": {
        "desc": "Query real-time BGP routing paths (RIPE RIS), RPKI validation status, and Tier-1 tags for any IP or prefix.",
        "use": "Enter an <ip> or <cidr> prefix. See active global routing paths and RPKI status."
    },
    "19": {
        "desc": "Verify cryptographic BGP RPKI signatures to validate if a specific origin ASN is authorized for a CIDR block.",
        "use": "Provide the <cidr> prefix and origin <asn>. The tool checks secure ROA registers at RIPE NCC."
    },
    "20": {
        "desc": "Query PeeringDB records to view an ASN's presence at internet exchanges (IXPs) and public data centers.",
        "use": "Enter the target <asn> to view active public peering points."
    },
    "21": {
        "desc": "Monitor active local TCP/UDP connection sockets with live ASNs, or run a NetFlow v5 receiver daemon.",
        "use": "Choose between local connection mapping or running a real-time NetFlow collector."
    },
    "22": {
        "desc": "Discover subdomains using Certificate Transparency (CT) logs from crt.sh and other public datasets.",
        "use": "Provide the <domain> to view a list of registered secure subdomains."
    },
    "23": {
        "desc": "Automatically detect the current active default gateway and local physical network interfaces.",
        "use": "Start the tool to view active local routing tables and interface configuration details."
    },
    "24": {
        "desc": "Scan the local subnet via fast ARP checks to discover active IPs, MAC addresses, and hardware vendors.",
        "use": "Launch the tool to resolve active local network devices against an offline OUI vendor database."
    },
    "25": {
        "desc": "Collect system details, system uptime, and interface profiles from network hardware using SNMPv2c.",
        "use": "Provide target <ip> and community string to query physical port metadata."
    },
    "26": {
        "desc": "Run a batch of commands concurrently on multiple network devices via SSH.",
        "use": "Provide a list of <ips> and <commands> to execute them across hosts."
    },
    "27": {
        "desc": "Interactive configuration checker with preconfigured templates for multi-vendor routers.",
        "use": "Select the tool and enter SSH credentials to run device audits."
    },
    "28": {
        "desc": "Automatically divide a parent IP subnet into custom smaller CIDR blocks.",
        "use": "Enter the parent <cidr> prefix and your target subnet size in CIDR format."
    },
    "29": {
        "desc": "Real-time graphic monitor of Wi-Fi signal strength (RSSI in dBm) with attenuation thresholds and warnings.",
        "use": "Start the tool and view in streaming the active interface signal oscillation in milliseconds."
    },
    "30": {
        "desc": "Native WHOIS client to query domain registration and ownership directly using TCP socket port 43 connections.",
        "use": "Enter the <domain> name and the system will locate the TLD server and fetch the record."
    },
    "31": {
        "desc": "High availability SLA calculator that translates 'SLA nines' into exact permitted downtime thresholds.",
        "use": "Enter the desired <sla> percentage and the system will output downtime tolerances."
    }
}
