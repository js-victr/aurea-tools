# Aurea Tools

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Termux%20%7C%20macOS-orange)](https://github.com/js-victr/aurea-tools)

**Aurea** is an interactive, modular command-line suite for BGP routing, SSL/TLS checks, NetFlow monitoring, and daily network troubleshooting. 

It is completely free and open-source, bringing clean and useful network utilities directly to your terminal.

---

## 💖 Support the Project

AureaTools is a community-driven, free open-source project. If it has saved you time in your network operations, consider supporting our development!

* **🔗 Donation Portal:** [https://js-victr.github.io/aurea-tools/#donate](https://js-victr.github.io/aurea-tools/#donate)
* **🔑 Pix Key (Brazil):** `45984313318`
* **⭐ GitHub Sponsors:** [https://github.com/sponsors/js-victr](https://github.com/sponsors/js-victr)

---

## 🌟 Key Features (31 Built-in Tools)

The suite is organized into **4 focused categories** designed to streamline your daily network workflow:

* **Diagnostics & Connectivity**: Active network testing engines including hop-by-hop MTR, Path MTU discovery, TCP port checking, and cloud latency checks.
* **IP Services & Security**: Domain health audits, DNSSEC verification, global DNS propagation checks, HTTP security header scans, and SSL/TLS cryptographic chain auditing.
* **BGP Engineering & Routing**: Consolidated Looking Glass with real-time AS-path visual flows, RPKI validation status, PeeringDB queries, and active NetFlow v5 traffic collection.
* **Automation & Utilities**: Subnet calculations, SLA calculators, concurrency CLI runners, multi-vendor device checkers, and local LAN ARP scanning.

👉 **Explore the full interactive directory and how to use each tool on our [Web Portal](https://js-victr.github.io/aurea-tools/).**

---

## 🚀 Installation & Setup

You can install Aurea directly using pip:

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

# Directly execute a specific tool by its index (e.g., Public IP & ASN)
aurea --run 8

# Disable ANSI color escape codes
aurea --no-color

# List all available tools
aurea --list

# Show version information
aurea --version
```

---

## 🧪 Running Tests

To execute the automated unit test suite:

```bash
python -m unittest discover tests
```

---

## 🌐 Web Documentation Portal (GitHub Pages)

To host the interactive web landing page and documentation portal on your own GitHub fork:

1. Go to your repository settings on GitHub.
2. Navigate to **Pages** on the left menu.
3. Under **Build and deployment**, select **Deploy from a branch**.
4. Set the branch to `main` (or your active branch) and change the folder option from `/ (root)` to `/docs`.
5. Click **Save** and wait for GitHub to publish your live web documentation!

---

## 📄 License

Distributed under the Apache 2.0 License. See `LICENSE` for more information.
