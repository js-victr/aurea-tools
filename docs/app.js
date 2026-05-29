/* ==========================================================================
   AureaTools v2.2 — Web Application JavaScript Engine
   ========================================================================== */

// 1. Tool Database (All 31 Tools)
const TOOLS_DATA = [
    {
        num: "1",
        name: "Advanced MTR with Loss & Jitter",
        category: "diagnostics",
        desc: "Continuous path routing with real-time packet loss, average latency, and jitter tracking.",
        use: "Enter the target IP or hostname. The tool continuously sends packets. Press Ctrl+C to stop.",
        kws: ["mtr", "traceroute", "ping", "latency", "loss", "jitter", "noc"]
    },
    {
        num: "2",
        name: "Path MTU Discovery (DF Ping)",
        category: "diagnostics",
        desc: "Find the exact maximum transmission unit (MTU) size without causing fragmentation on your link.",
        use: "Enter the target. The tool pings with the Don't Fragment (DF) bit set, testing from 1200 to 1500 bytes.",
        kws: ["mtu", "ping", "fragmentation", "df", "mss", "overhead"]
    },
    {
        num: "3",
        name: "Aurea Nmap TCP Port Scanner & Banner Grabbing",
        category: "diagnostics",
        desc: "Fast TCP port scanner that identifies open ports and attempts to capture service banners.",
        use: "Enter the target host. The tool scans the 1000 most common ports and prints open sockets.",
        kws: ["scan", "port", "nmap", "banner", "service", "version", "grab"]
    },
    {
        num: "4",
        name: "Dynamic ISP Latency Matrix",
        category: "diagnostics",
        desc: "Tests latency to major cloud providers (AWS, GCP, Azure, Oracle) and CDN edge networks (Cloudflare, Fastly).",
        use: "Start the tool to see live round-trip time (RTT) measurements to global cloud infrastructure.",
        kws: ["latency", "isp", "rtt", "cloud", "aws", "gcp", "azure", "cdn", "cloudflare"]
    },
    {
        num: "5",
        name: "Subnet Overlay Planner (Conflict Detector)",
        category: "diagnostics",
        desc: "Plan subnets and detect overlay conflicts across IPv4/IPv6 ranges in VPNs, tunnels, or peers.",
        use: "Enter your active subnets and the proposed range. The tool detects overlapping IPs and highlights free blocks.",
        kws: ["subnet", "cidr", "ipam", "overlay", "vpn", "conflict", "ipv4", "ipv6"]
    },
    {
        num: "6",
        name: "Public IP & ASN Lookup",
        category: "services",
        desc: "Identify your current public IP, internet service provider (ISP), transit ASN, and estimated location.",
        use: "Launch the tool to retrieve a clean summary of your current connection metadata.",
        kws: ["ip", "public", "asn", "geolocation", "isp", "myip"]
    },
    {
        num: "7",
        name: "IP Intelligence & Recon",
        category: "services",
        desc: "Lookup geolocation, reverse DNS, hosting carrier, and WHOIS records for any public IP address.",
        use: "Provide any target IP or public domain name to fetch its routing and carrier profile.",
        kws: ["ip", "intel", "recon", "geolocation", "asn", "carrier", "whois"]
    },
    {
        num: "8",
        name: "DNS Hijacking Detector",
        category: "services",
        desc: "Checks for local DNS interception or spoofing by comparing queries against secure DoH resolvers.",
        use: "Select the tool. It verifies NXDOMAIN replies and looks for differences with public secure endpoints.",
        kws: ["dns", "hijack", "security", "spoofing", "doh", "nxdomain", "poisoning"]
    },
    {
        num: "9",
        name: "CGNAT Port Exhaustion Simulator",
        category: "services",
        desc: "Simulate concurrent socket burst requests to check session capacity limits and CGNAT timeouts.",
        use: "Enter target host and number of concurrent connections (e.g., 150) to measure latencies and connection drops.",
        kws: ["cgnat", "exhaustion", "nat", "ports", "sockets", "concurrency", "timeouts"]
    },
    {
        num: "10",
        name: "Local DNS Benchmark",
        category: "services",
        desc: "Benchmark DNS query speeds by comparing your current resolver against Google, Cloudflare, Quad9, and OpenDNS.",
        use: "Enter a test domain (e.g., google.com) to view the response times in milliseconds.",
        kws: ["dns", "benchmark", "resolver", "latency", "resolving", "local"]
    },
    {
        num: "11",
        name: "DNS Propagation Checker",
        category: "services",
        desc: "Query DNS 'A' records across multiple global public resolvers in parallel to verify propagation.",
        use: "Type the domain name and watch responses from global servers update in real-time.",
        kws: ["dns", "propagation", "checker", "parallel", "resolvers", "dig"]
    },
    {
        num: "12",
        name: "DNSSEC Validation",
        category: "services",
        desc: "Verify DNSSEC cryptographic records (DS, DNSKEY) and check if your local resolver validates them.",
        use: "Enter a domain to audit its secure DNS delegation and cryptographic signatures.",
        kws: ["dnssec", "dns", "security", "validation", "cryptography"]
    },
    {
        num: "13",
        name: "SSL/TLS Cryptographic Chain Auditor",
        category: "services",
        desc: "Audit SSL/TLS certificates. Displays validity dates, issuer information, protocol support (TLS 1.0-1.3), and weak ciphers.",
        use: "Provide a domain to query port 443 and download its X.509 certificate metadata.",
        kws: ["ssl", "tls", "certificate", "inspector", "ciphers", "tls13", "validation", "pci-dss"]
    },
    {
        num: "14",
        name: "HTTP Security Headers Scan",
        category: "services",
        desc: "Scan HTTP security response headers like HSTS, CSP, X-Frame-Options, and X-Content-Type-Options.",
        use: "Provide a full URL (e.g., https://cloudflare.com) to audit security configurations.",
        kws: ["http", "security", "headers", "scan", "armor", "clickjacking", "hsts", "csp"]
    },
    {
        num: "15",
        name: "Banner Grabbing",
        category: "services",
        desc: "Connect to custom ports (SSH, FTP, SMTP, HTTP) and display the raw service banner returned by the server.",
        use: "Provide target IP or hostname along with a port. The tool prints the server's reply.",
        kws: ["banner", "grabbing", "fingerprint", "service", "version", "osint"]
    },
    {
        num: "16",
        name: "Email Security Audit (SPF & DMARC)",
        category: "services",
        desc: "Inspect active SPF and DMARC DNS records to verify email domain spoofing defenses.",
        use: "Enter a domain to view its published TXT records and check if it enforces strict policies (reject/quarantine).",
        kws: ["spf", "dmarc", "email", "security", "spoofing", "phishing", "txt"]
    },
    {
        num: "17",
        name: "DNS Zone Recon & OSINT",
        category: "services",
        desc: "Perform comprehensive DNS lookups to extract all core records (A, AAAA, MX, TXT, NS, SOA, DS) at once.",
        use: "Enter the domain name. The tool queries secure endpoints and returns a structured list.",
        kws: ["dns", "zone", "recon", "ns", "mx", "txt", "doh", "osint"]
    },
    {
        num: "18",
        name: "Consolidated BGP Looking Glass",
        category: "bgp",
        desc: "Query real-time BGP routing paths (RIPE RIS), RPKI validation status, and Tier-1 tags for any IP or prefix.",
        use: "Enter an IP address or CIDR prefix. See active global routing paths and RPKI status.",
        kws: ["bgp", "looking", "glass", "ripe", "ris", "route", "asn", "rpki", "propagation"]
    },
    {
        num: "19",
        name: "BGP RPKI Validator",
        category: "bgp",
        desc: "Verify cryptographic BGP RPKI signatures to validate if a specific origin ASN is authorized for a CIDR block.",
        use: "Provide the IP prefix and origin ASN. The tool checks secure ROA registers at RIPE NCC.",
        kws: ["bgp", "rpki", "validation", "hijack", "roa", "security"]
    },
    {
        num: "20",
        name: "PeeringDB Lookup",
        category: "bgp",
        desc: "Query PeeringDB records to view an ASN's presence at internet exchanges (IXPs) and public data centers.",
        use: "Enter the target ASN (e.g., 15169 for Google) to view active public peering points.",
        kws: ["peeringdb", "asn", "peering", "ixp", "datacenter", "policy"]
    },
    {
        num: "21",
        name: "Traffic Flow & ASN Monitor (AureaFlow)",
        category: "bgp",
        desc: "Monitor active local TCP/UDP connection sockets with live ASNs, or run a NetFlow v5 receiver daemon on port 2055.",
        use: "Choose between local connection mapping or running a real-time NetFlow collector.",
        kws: ["traffic", "flow", "asn", "monitor", "connections", "netflow", "noc"]
    },
    {
        num: "22",
        name: "OSINT Subdomain Recon",
        category: "bgp",
        desc: "Discover subdomains using Certificate Transparency (CT) logs from crt.sh and other public datasets.",
        use: "Provide the domain (e.g., github.com) to view a list of registered secure subdomains.",
        kws: ["osint", "subdomain", "recon", "dns", "dnssec", "crtsh", "sonar"]
    },
    {
        num: "23",
        name: "Local Gateway Discovery",
        category: "automation",
        desc: "Automatically detect the current active default gateway and local physical network interfaces.",
        use: "Start the tool to view active local routing tables and interface configuration details.",
        kws: ["gateway", "local", "interfaces", "discovery", "arp", "route"]
    },
    {
        num: "24",
        name: "Local Devices Discovery (ARP)",
        category: "automation",
        desc: "Scan the local subnet via fast ARP checks to discover active IPs, MAC addresses, and hardware vendors.",
        use: "Launch the tool to resolve active local network devices against an offline OUI vendor database.",
        kws: ["arp", "discovery", "devices", "mac", "vendor", "lan"]
    },
    {
        num: "25",
        name: "SNMP Mass Collector",
        category: "automation",
        desc: "Collect system details, system uptime, and interface profiles from network hardware using SNMPv2c.",
        use: "Provide target IP and community string (e.g., public) to query physical port metadata.",
        kws: ["snmp", "mibs", "mass", "collector", "noc", "community"]
    },
    {
        num: "26",
        name: "SSH Command Runner",
        category: "automation",
        desc: "Run a batch of commands concurrently on multiple network devices via SSH.",
        use: "Provide a list of IPs and commands to execute them across hosts.",
        kws: ["ssh", "automation", "netmiko", "commands", "runner", "batch"]
    },
    {
        num: "27",
        name: "Multi-Vendor Auditor",
        category: "automation",
        desc: "Interactive configuration checker with preconfigured templates for Cisco, Juniper, Huawei, and MikroTik routers.",
        use: "Select the tool and enter SSH credentials to run device audits.",
        kws: ["cisco", "juniper", "huawei", "mikrotik", "audit", "netmiko", "noc"]
    },
    {
        num: "28",
        name: "MikroTik API Config Auditor",
        category: "automation",
        desc: "Connects to RouterOS API to verify firewall settings, NAT configurations, and default service ports.",
        use: "Enter target IP and MikroTik API credentials (port 8728) to audit device security.",
        kws: ["mikrotik", "routeros", "api", "firewall", "audit", "security"]
    },
    {
        num: "29",
        name: "IP Address Plan (IPAM Generator)",
        category: "automation",
        desc: "Automatically divide a parent IP subnet into custom smaller CIDR blocks.",
        use: "Enter the parent CIDR prefix (e.g., 192.168.0.0/24) and your target subnet size.",
        kws: ["ipam", "subnetting", "cidr", "planner", "addressing", "generator"]
    },
    {
        num: "30",
        name: "VLAN Planner",
        category: "automation",
        desc: "Document and organize VLAN tags, descriptions, and assignments.",
        use: "Use the interactive prompts to define physical network segments and export structured layouts.",
        kws: ["vlan", "switching", "8021q", "planner", "ids", "tags"]
    },
    {
        num: "31",
        name: "Cisco Config Generator",
        category: "automation",
        desc: "Generate clean configuration blueprints for Cisco routers and switches (SSH, interfaces, routing, DHCP).",
        use: "Answer interactive prompts to generate a standard bootstrap config file.",
        kws: ["cisco", "config", "generator", "ios", "template", "bootstrap"]
    }
];

// 2. Interactive CLI Emulator Logic
const cliScreen = document.getElementById("cli-screen");

const SIMULATION_STEPS = [
    {
        cmd: "python -m aurea",
        delay: 1500,
        output: [
            "<span class='cyan'>[BACKGROUND] Loading core modules, ANSI colors, and checking API keys...</span>",
            "╔══════════════════════════════════════════════════════════════════════════════╗",
            "║  <span class='green'>:: A U R E A ::</span>  |                   MAIN INTERACTIVE CONSOLE                   ║",
            "╚══════════════════════════════════════════════════════════════════════════════╝",
            "  Select a tool from the menu to begin..."
        ]
    },
    {
        cmd: "bgp_looking_glass --target 8.8.8.8",
        delay: 2000,
        output: [
            "<span class='yellow'>Fetching BGP data from RIPE RIS and checking RPKI...</span>",
            "  <span class='green'>✓</span> Prefix:      <span class='green'>8.8.8.0/24</span>",
            "  <span class='green'>✓</span> Origin ASN:  <span class='yellow'>AS15169</span> (Google LLC)",
            "  <span class='green'>✓</span> RPKI Status: <span class='green'>VALID (Digitally Signed)</span>",
            "",
            "<span class='cyan'>BGP AS-PATH PROPAGATION PATHS:</span>",
            "  <span class='bold'>[RRC01]</span> via AS2914 | NextHop: 5.57.80.113",
            "    └─ Flow: <span class='cyan'>[AS2914 (NTT - Tier-1)]</span> <span class='bold'>➔</span> <span class='green'>[AS15169 (Google)]</span>"
        ]
    },
    {
        cmd: "ssl_inspector --domain google.com",
        delay: 2000,
        output: [
            "<span class='yellow'>Auditing SSL/TLS certificate chain...</span>",
            "  • TLSv1.2   | Status: <span class='green'>SUPPORTED</span>            | Secure",
            "  • TLSv1.3   | Status: <span class='green'>SUPPORTED</span>            | Recommended",
            "",
            "<span class='cyan'>Active Cryptographic Channel:</span>",
            "  • Certificate Trust: <span class='green'>VALID & TRUSTED</span>",
            "  • Negotiated Cipher: <span class='green'>TLS_AES_256_GCM_SHA384 (STRONG)</span>",
            "  • Protocol Version:  <span class='cyan'>TLSv1.3</span>"
        ]
    },
    {
        cmd: "netflow --port 2055 --filter-ip 192.168.1.100",
        delay: 2500,
        output: [
            "<span class='cyan'>✓ NetFlow v5 collector listening on UDP port 2055...</span>",
            "<span class='yellow'>  Building dashboard view...</span>",
            "  • Active Filter:     <span class='yellow'>IP: 192.168.1.100</span>",
            "  • Speedometer (30s): [<span class='green'>▄▆█▆▄▃      █</span>] (Peak: 800.00 Kbps)",
            "  • Total Throughput:  <span class='yellow'>800.00 Kbps</span> | Down: 500.00 Kbps | Up: 300.00 Kbps",
            "",
            "<span class='cyan'> [2] EXPORTING ROUTERS</span>",
            "  192.168.1.1        | <span class='yellow'>800.00 Kbps</span>  | <span class='green'>Cisco Systems</span>                | 120",
            "",
            "<span class='cyan'> [5] SNMP PHYSICAL INTERFACE PROFILES</span>",
            "  IfIndex 1  |      1.50 MB |      0.00 MB | <span class='red'>HIGH CONGESTION             (60.0%)</span>",
            "  IfIndex 2  |      0.00 MB |      1.00 MB | <span class='yellow'>MODERATE LOAD               (40.0%)</span>"
        ]
    }
];

let stepIndex = 0;

function appendLine(text, className = "") {
    const p = document.createElement("p");
    p.className = `cli-line ${className}`;
    p.innerHTML = text;
    cliScreen.appendChild(p);
    cliScreen.scrollTop = cliScreen.scrollHeight;
}

async function typeCommand(text) {
    const p = document.createElement("p");
    p.className = "cli-line";
    p.innerHTML = `<span class='user'>aurea@noc</span>:<span class='dir'>~</span>$ `;
    cliScreen.appendChild(p);
    
    for (let char of text) {
        p.innerHTML += char;
        cliScreen.scrollTop = cliScreen.scrollHeight;
        await new Promise(r => setTimeout(r, 60));
    }
}

async function runCLIEmulator() {
    while (true) {
        const step = SIMULATION_STEPS[stepIndex];
        
        await typeCommand(step.cmd);
        await new Promise(r => setTimeout(r, 400));
        
        for (let line of step.output) {
            appendLine(line);
            await new Promise(r => setTimeout(r, 100));
        }
        
        await new Promise(r => setTimeout(r, step.delay));
        
        // Reset console screen occasionally to prevent cluttering
        if (stepIndex === SIMULATION_STEPS.length - 1) {
            await new Promise(r => setTimeout(r, 2000));
            cliScreen.innerHTML = `<span class="cli-line comment"># AureaTools CLI Simulator v2.2</span>\n<span class="cli-line"><span class="user">aurea@noc</span>:<span class="dir">~</span>$ clear</span>`;
            await new Promise(r => setTimeout(r, 800));
            cliScreen.innerHTML = `<span class="cli-line comment"># AureaTools CLI Simulator v2.2</span>`;
            stepIndex = 0;
        } else {
            stepIndex++;
            appendLine("");
        }
    }
}

// 3. Documentation Explorer Logic (Filter & Search)
const toolsGrid = document.getElementById("tools-grid");
const searchInput = document.getElementById("search-input");
const filterButtons = document.querySelectorAll(".filter-btn");

let activeCategory = "all";
let searchQuery = "";

function renderTools() {
    toolsGrid.innerHTML = "";
    
    const filtered = TOOLS_DATA.filter(tool => {
        const matchesCategory = activeCategory === "all" || tool.category === activeCategory;
        
        const text = (tool.name + " " + tool.desc + " " + tool.use + " " + tool.kws.join(" ")).toLowerCase();
        const matchesSearch = text.includes(searchQuery.toLowerCase()) || tool.num === searchQuery;
        
        return matchesCategory && matchesSearch;
    });
    
    if (filtered.length === 0) {
        toolsGrid.innerHTML = `
            <div class="glass-panel" style="grid-column: 1 / -1; padding: 40px; text-align: center; color: var(--text-secondary);">
                <i class="fa-solid fa-face-frown" style="font-size: 2.5rem; color: var(--text-muted); margin-bottom: 16px;"></i>
                <p>No tools matched your search criteria.</p>
            </div>
        `;
        return;
    }
    
    filtered.forEach(tool => {
        const card = document.createElement("div");
        card.className = "tool-card";
        
        const kwHTML = tool.kws.map(kw => `<span class="tool-kw">${kw}</span>`).join("");
        
        card.innerHTML = `
            <div class="tool-card-header">
                <span class="tool-num-badge">#${tool.num.padStart(2, '0')}</span>
                <span class="tool-category-badge cat-${tool.category}">${tool.category}</span>
            </div>
            <h3>${tool.name}</h3>
            <p><strong>Purpose:</strong> ${tool.desc}</p>
            <p><strong>Usage:</strong> <em>${tool.use}</em></p>
            <div class="tool-keyword-list">
                ${kwHTML}
            </div>
        `;
        toolsGrid.appendChild(card);
    });
}

// Event Listeners for Filters
filterButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        filterButtons.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        
        activeCategory = btn.getAttribute("data-category");
        renderTools();
    });
});

// Event Listener for Search Input
searchInput.addEventListener("input", (e) => {
    searchQuery = e.target.value;
    renderTools();
});

// 4. Utility Copy Functions
function copyInstallCmd() {
    const copyText = document.getElementById("install-command");
    copyText.select();
    copyText.setSelectionRange(0, 99999);
    navigator.clipboard.writeText(copyText.value);
    
    const icon = document.getElementById("copy-icon");
    icon.className = "fa-solid fa-circle-check";
    icon.style.color = "var(--green)";
    
    setTimeout(() => {
        icon.className = "fa-regular fa-copy";
        icon.style.color = "";
    }, 2000);
}

function copyPixKey() {
    const copyText = document.getElementById("pix-key");
    copyText.select();
    copyText.setSelectionRange(0, 99999);
    navigator.clipboard.writeText(copyText.value);
    
    const icon = document.getElementById("pix-icon");
    const btn = document.querySelector(".btn-copy-pix");
    btn.innerHTML = `<i class="fa-solid fa-circle-check"></i> Copied!`;
    btn.style.borderColor = "var(--green)";
    
    setTimeout(() => {
        btn.innerHTML = `<i id="pix-icon" class="fa-regular fa-copy"></i> Copy`;
        btn.style.borderColor = "";
    }, 2000);
}

function copyCrypto(elementId) {
    const copyText = document.getElementById(elementId);
    copyText.select();
    copyText.setSelectionRange(0, 99999);
    navigator.clipboard.writeText(copyText.value);
    
    const btn = copyText.nextElementSibling;
    const oldIcon = btn.innerHTML;
    btn.innerHTML = `<i class="fa-solid fa-circle-check" style="color: var(--green);"></i>`;
    
    setTimeout(() => {
        btn.innerHTML = oldIcon;
    }, 2000);
}

// 5. Initial Execution
renderTools();
runCLIEmulator();
