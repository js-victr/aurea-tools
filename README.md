# Aurea Tools

[![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Termux%20%7C%20macOS-orange)](https://github.com/js-victr/aurea-tools)

**Aurea** is an Advanced Network Diagnostics, BGP Engineering & Cybersecurity Console designed specifically for ISP engineers, network administrators, and NOC professionals. 

Re-architected from a monolithic script into a modern modular package, Aurea is **100% Free and Open-Source**, bringing professional-grade network CLI tools to any terminal with zero complex dependencies.

---

## 💖 Support the Project / Donations

AureaTools is a community-driven, free open-source project. If Aurea has saved you time in your NOC operations or internet routing troubleshooting, consider supporting our development! 

* **🔗 Donation Hub / Linktree:** [https://js-victr.github.io/aurea-tools/donate](https://js-victr.github.io/aurea-tools/donate)
* **🔑 Pix Key (Brazil):** `apoio@aureatools.com`
* **⭐ GitHub Sponsors:** [https://github.com/sponsors/js-victr](https://github.com/sponsors/js-victr)

---

## 🌟 Key Features (35 Built-in Tools)

The console is organized into **4 dynamic submenus** to streamline your troubleshooting workflow:

### 1. Diagnostics & Connectivity (`diagnostics`)
* **Local IP & Interfaces:** Mapping of IPv4 & IPv6 outbound interface paths and border NAT.
* **ICMP Ping (v4/v6):** Fast, clean ping engines with precise round-trip measurements.
* **Network Traceroute:** Route mapping identifying autonomous systems (AS) and packet paths.
* **Advanced MTR:** Continuous hop-by-hop traceroute with real-time packet loss, average latency, and jitter.
* **TCP Port Checker:** Standard TCP connection test on custom target ports.
* **Bandwidth Speedtest:** Network performance benchmark directly from the CLI.
* **MTU Path Discovery:** Fragmentation threshold checker to pinpoint routing MTU constraints.
* **HTTP Captive Portal Check:** Inspects captive networks, detecting HTTP redirection URLs.

### 2. IP Services & Web Security (`services`)
* **Public IP & ASN Lookup:** Real-time external IP geolocation, ISP metadata, and ASN information.
* **IP Intelligence & Recon:** Complete threat dossier mapping ISP, org, carrier, and reverse lookup metadata.
* **Local DNS Benchmark:** Lookup latency comparisons between global public resolvers and the local gateway.
* **DNS Propagation Checker:** Query domain records across global public resolvers in parallel to inspect DNS caching.
* **DNSSEC Validator:** Double-layered verification of resolver security and DNS cryptographic records.
* **SSL/TLS Cryptographic Chain Auditor:** Detailed expiry tracker mapping CN, Issuer, validity, and remaining days with active TLS 1.0-1.3 protocol checking, weak cipher suites audit, and unverified validation fallbacks.
* **HTTP Security Headers Scan:** Evaluates server defenses (HSTS, CSP, Clickjacking, MIME sniffing).
* **Banner Grabbing:** Service fingerprinting and version detection on raw target port sockets.
* **DNS Spoofing Auditor:** Inspects SPF and DMARC zone alignments to analyze phishing and spoofing exposure.

### 3. BGP Engineering & Routing (`bgp`)
* **BGP Route Auditor:** Prefix visibility overview, upstream/downstream peering mapping, and RADB object WHOIS mining.
* **BGP RPKI Validator:** Validates ROA cryptographic registry directly against RIPE NCC records.
* **BGP Looking Glass:** Live visibility check, AS-path mappings, and public BGP community announcements via RIPE RIS with dynamic ASCII AS-Path top-hop flow mapping, Tier-1 carrier tagging, and interactive collector expansion.
* **BGP Community Decoder:** Decodes standard/large communities for NTT, HE, Lumen, Telia, etc.
* **PeeringDB Lookup:** Inspects IXP presence, datacenter footprint, and peering policy rules.
* **Traffic Flow & ASN Monitor (AureaFlow):** Captures local socket connections to CSV with ASN carrier tags, or starts NetFlow v5 NOC daemon collector with active band speedometer sparklines, DPI port-to-service mapping, physical SNMP IfIndex load profiling, and custom active filters.
* **OSINT Subdomain Recon:** Searches certificate transparency logs (crt.sh) and Hackertarget engines to map subdomains.

### 4. Utilities & NOC Automation (`automation`)
* **LAN Device Scanner:** Instant ARP table parsing to discover local MAC addresses and network segments.
* **Multithreaded Port Scanner:** Concurrent parallel scanning of multiple TCP ports.
* **[NEW] LAN Auto-Discovery & NetBox Sync:** Threaded ping sweep across CIDR, resolves PTR hostnames, maps MAC/OUI manufacturers, exports CSV inventories, and syncs hosts dynamically to **NetBox IPAM** REST APIs!
* **[NEW] MikroTik SSH Auditor & NetBox Sync:** Connects to RouterOS via native SSH, parses interfaces, active IPs, VLANs, LLDP/CDP neighbors, and syncs dynamically with NetBox IPAM!
* **[NEW] BGP Route Aggregator & Optimizer:** Mathematically collapses adjacent or overlapping subnets into the minimal set of optimal routing blocks to reduce BGP routing table size.
* **IPAM & Subnet Calculator:** Resolves subnet bounds, hosts capacity, PTR notations, and splits prefix ranges.
* **SLA & Uptime Calculator:** Computes allowable contract downtime limits on daily, monthly, and yearly levels.
* **Live Wi-Fi RSSI Monitor:** Continuously monitors Wi-Fi signal strength, channel ranges, and BSSID link speeds.
* **CDN & App Latency Test:** Benchmarks latency against global platforms (Google, Netflix, WhatsApp, Cloudflare).
* **MAC OUI Vendor Lookup:** Maps MAC prefixes to registered hardware manufacturers.
* **Native WHOIS Client:** Socket-based WHOIS registry query.
* **Secure Password Generator:** High-entropy local generation of device and access credentials.

---

## 🚀 Installation & Setup

You can install Aurea directly in development mode:

```bash
# Clone the repository
git clone https://github.com/js-victr/aurea-tools.git
cd aurea-tools

# Install in development mode
pip install -e .
```

---

## 💻 Command Line Usage

Once installed, the `aurea` command will be globally available on your shell path:

```bash
# Open the dynamic interactive console
aurea

# Directly execute a specific tool by its index (e.g. Public IP & ASN)
aurea --run 8

# Force specific language translation (PT-BR)
aurea --lang pt

# Disable ANSI color escape codes
aurea --no-color

# List all available tools
aurea --list

# Show version information
aurea --version
```

---

## 🌍 Internationalization (i18n)

Aurea is completely bilingual! It automatically auto-detects the host system locale (supporting English and Portuguese out-of-the-box). 

You can also dynamically toggle the language directly from the interactive menu by pressing **`[L]`**, or via CLI flags using `--lang pt` / `--lang en`.

---

## 🧪 Running Tests

Aurea is fully covered by robust unit tests. To execute the tests:

```bash
python -m unittest discover tests
```

---

## 🌐 Web Documentation Portal (GitHub Pages)

AureaTools features a premium, interactive web landing page and documentation portal. It showcases responsive terminal emulators, interactive tools browser, installation steps, and support features:

* **🔗 Active Portal:** `https://js-victr.github.io/aurea-tools`
* **📁 Source Folder:** Located under `docs/` in the repository root.

To host this on your own GitHub fork:
1. Go to your repository settings on GitHub.
2. Navigate to **Pages** on the left menu.
3. Under **Build and deployment**, select **Deploy from a branch**.
4. Set the branch to `main` (or your active branch) and change the folder option from `/ (root)` to `/docs`.
5. Click **Save** and wait for GitHub to publish your live NOC web documentation!

---

## 📄 License

Distributed under the Apache 2.0 License. See `LICENSE` for more information.
