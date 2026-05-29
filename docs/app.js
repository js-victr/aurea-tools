/* ==========================================================================
   AureaTools v2.2 — Web Application JavaScript Engine
   ========================================================================== */

// 1. Tool Database (All 31 Tools)
const TOOLS_DATA = [
    {
        num: "1",
        name: "Advanced MTR with Loss & Jitter",
        category: "diagnostics",
        desc: "Traçado de rotas contínuo com estatísticas de perda de pacotes e jitter (variação de latência) em tempo real.",
        use: "Insira o IP/host de destino. O MTR enviará pacotes consecutivamente. Pressione Ctrl+C para encerrar.",
        kws: ["mtr", "traceroute", "ping", "latency", "loss", "jitter", "noc"]
    },
    {
        num: "2",
        name: "Path MTU Discovery (DF Ping)",
        category: "diagnostics",
        desc: "Busca binária automatizada para descobrir o MTU (Maximum Transmission Unit) exato sem fragmentação no enlace físico.",
        use: "Insira o host de destino. A ferramenta executará ping com bit Don't Fragment (DF) ativo de 1200 a 1500 bytes.",
        kws: ["mtu", "ping", "fragmentation", "df", "mss", "overhead"]
    },
    {
        num: "3",
        name: "Aurea Nmap TCP Port Scanner & Banner Grabbing",
        category: "diagnostics",
        desc: "Scanner de portas TCP de alta velocidade (modelo NMAP) para identificar portas abertas e mapear serviços/banners em tempo real.",
        use: "Digite o IP/host de destino. O sistema varrerá automaticamente as 1000 portas mais comuns de redes e tentará obter as versões dos serviços rodando.",
        kws: ["scan", "port", "nmap", "banner", "service", "version", "grab"]
    },
    {
        num: "4",
        name: "Dynamic ISP Latency Matrix",
        category: "diagnostics",
        desc: "Matriz dinâmica de latência e qualidade de rota para principais nuvens globais (AWS, GCP, Azure, Oracle) e CDNs (Cloudflare, Akamai, Fastly).",
        use: "Inicie a ferramenta para medir em tempo real o RTT e a perda de pacotes para os backbones globais de nuvem e borda de rede.",
        kws: ["latency", "isp", "rtt", "cloud", "aws", "gcp", "azure", "cdn", "cloudflare"]
    },
    {
        num: "5",
        name: "Subnet Overlay Planner (Conflict Detector)",
        category: "diagnostics",
        desc: "Planejador de sub-redes e detector de conflito overlay para faixas IPv4/IPv6 em túneis, VPNs ou peers de rede.",
        use: "Insira suas sub-redes existentes e a sub-rede proposta. O sistema auditará colisões/sobreposições e sugerirá faixas livres.",
        kws: ["subnet", "cidr", "ipam", "overlay", "vpn", "conflict", "ipv4", "ipv6"]
    },
    {
        num: "6",
        name: "Public IP & ASN Lookup",
        category: "services",
        desc: "Mapeia o seu IP público atual, Provedor de Internet (ISP), ASN de trânsito e localização geográfica aproximada.",
        use: "Selecione a ferramenta e o sistema consultará de forma segura o dossiê da sua conexão atual via HTTPS.",
        kws: ["ip", "public", "asn", "geolocation", "isp", "myip"]
    },
    {
        num: "7",
        name: "IP Intelligence & Recon",
        category: "services",
        desc: "Consulta de inteligência (OSINT) e geolocalização detalhada para qualquer IP público de trânsito global.",
        use: "Insira o endereço IP de destino ou nome de host público e aguarde o retorno das coordenadas e operadora.",
        kws: ["ip", "intel", "recon", "geolocation", "asn", "carrier", "whois"]
    },
    {
        num: "8",
        name: "DNS Hijacking Detector",
        category: "services",
        desc: "Detector de interceptações e sequestros de DNS locais usando validação trilateral (3-way) contra Cloudflare e Quad9 DoH.",
        use: "Selecione a ferramenta. Ela simulará falhas de NXDOMAIN e divergências de DoH para auditar se há proxy/interceptação.",
        kws: ["dns", "hijack", "security", "spoofing", "doh", "nxdomain", "poisoning"]
    },
    {
        num: "9",
        name: "CGNAT Port Exhaustion Simulator",
        category: "services",
        desc: "Simulador NOC de rajada paralela de sockets para auditar limites de conexões simultâneas e esgotamento de CGNAT.",
        use: "Insira o host e o número de sockets paralelos (ex: 150). O sistema calculará a latência média e a taxa de perda/timeout.",
        kws: ["cgnat", "exhaustion", "nat", "ports", "sockets", "concurrency", "timeouts"]
    },
    {
        num: "10",
        name: "Local DNS Benchmark",
        category: "services",
        desc: "Benchmark de latência e resolução DNS local comparando o seu roteador com Google, Cloudflare, Quad9 e OpenDNS.",
        use: "Digite o domínio de teste (ex: google.com) e observe o tempo exato de resposta UDP de cada servidor DNS em milissegundos.",
        kws: ["dns", "benchmark", "resolver", "latency", "resolving", "local"]
    },
    {
        num: "11",
        name: "DNS Propagation Checker",
        category: "services",
        desc: "Audita o tempo de propagação global e resolução de registros 'A' de um domínio em servidores DNS mundiais em paralelo.",
        use: "Insira o nome de domínio e veja em tempo real as respostas convergentes ou divergentes nos servidores mundiais.",
        kws: ["dns", "propagation", "checker", "parallel", "resolvers", "dig"]
    },
    {
        num: "12",
        name: "DNSSEC Validation",
        category: "services",
        desc: "Verificador de assinaturas criptográficas DNSSEC ativas e autenticação segura AD (Authenticated Data) de domínios.",
        use: "Insira o domínio para auditar e veja se ele possui registros DS publicados e suporte a chaves criptográficas DNSKEY.",
        kws: ["dnssec", "dns", "security", "validation", "cryptography"]
    },
    {
        num: "13",
        name: "SSL/TLS Cryptographic Chain Auditor",
        category: "services",
        desc: "Scanner e inspetor estrito de certificados SSL/TLS para verificar validade, entidade emissora (CA) e dias para expiração.",
        use: "Insira o domínio na porta 443 e aguarde o download e parse do certificado X.509 transmitido na sessão.",
        kws: ["ssl", "tls", "certificate", "inspector", "ciphers", "tls13", "validation", "pci-dss"]
    },
    {
        num: "14",
        name: "HTTP Security Headers Scan",
        category: "services",
        desc: "Scaneia cabeçalhos de segurança HTTP (HSTS, CSP, X-Frame-Options, X-Content-Type) de servidores web.",
        use: "Insira a URL completa (ex: https://registro.br) e o sistema avaliará os níveis de proteção contra injeções de script.",
        kws: ["http", "security", "headers", "scan", "armor", "clickjacking", "hsts", "csp"]
    },
    {
        num: "15",
        name: "Banner Grabbing",
        category: "services",
        desc: "Conecta em soquetes de serviços comuns para capturar banners e assinaturas de versão (SSH, FTP, SMTP, HTTP, etc.).",
        use: "Insira o IP/host de destino e a porta de rede. O sistema exibirá o payload bruto retornado pelo daemon.",
        kws: ["banner", "grabbing", "fingerprint", "service", "version", "osint"]
    },
    {
        num: "16",
        name: "Email Security Audit (SPF & DMARC)",
        category: "services",
        desc: "Auditoria de registros de segurança DNS SPF e DMARC contra spoofing de e-mail e campanhas de phishing.",
        use: "Insira o domínio corporativo e veja se ele possui políticas duras (reject, softfail) ou permissivas.",
        kws: ["spf", "dmarc", "email", "security", "spoofing", "phishing", "txt"]
    },
    {
        num: "17",
        name: "DNS Zone Recon & OSINT",
        category: "services",
        desc: "Inspetor aprofundado de zona DNS que extrai todos os registros essenciais (A, AAAA, MX, TXT, NS, SOA, DS) de uma vez.",
        use: "Insira o domínio. A ferramenta consultará a API DoH de forma abrangente e estruturará os registros.",
        kws: ["dns", "zone", "recon", "ns", "mx", "txt", "doh", "osint"]
    },
    {
        num: "18",
        name: "BGP Looking Glass Consolidado",
        category: "bgp",
        desc: "Consultor global Looking Glass que consolida caminhos de trânsito AS-Path (RIPE RIS) e validação RPKI para qualquer IP/bloco.",
        use: "Insira o IP ou prefixo CIDR. Veja os caminhos de anúncios globais e a integridade ROA de trânsito de rede.",
        kws: ["bgp", "looking", "glass", "ripe", "ris", "route", "asn", "rpki", "propagation"]
    },
    {
        num: "19",
        name: "BGP RPKI Validator",
        category: "bgp",
        desc: "Validador criptográfico estrito de anúncios BGP RPKI para verificar a legitimidade do ASN de origem de blocos CIDR.",
        use: "Insira o prefixo e o ASN de origem correspondente. O sistema consultará as assinaturas digitais ROA do RIPE NCC.",
        kws: ["bgp", "rpki", "validation", "hijack", "roa", "security"]
    },
    {
        num: "20",
        name: "PeeringDB Lookup",
        category: "bgp",
        desc: "Consulta detalhes de conexões de peering, servidores IXP públicos e presença em data centers de operadoras no PeeringDB.",
        use: "Digite o número do ASN de trânsito (ex: 15169 para Google, 264321) e veja os pontos de troca de tráfego ativos.",
        kws: ["peeringdb", "asn", "peering", "ixp", "datacenter", "policy"]
    },
    {
        num: "21",
        name: "Traffic Flow & ASN Monitor (AureaFlow)",
        category: "bgp",
        desc: "Monitor em tempo real de fluxos de conexões TCP/UDP locais ou receptor daemon NOC de pacotes NetFlow v5 (porta 2055).",
        use: "Escolha entre monitor de conexões locais (ss/netstat com ASN) ou coletor daemon NOC NetFlow v5 em tempo real.",
        kws: ["traffic", "flow", "asn", "monitor", "connections", "netflow", "noc"]
    },
    {
        num: "22",
        name: "OSINT Subdomain Recon",
        category: "bgp",
        desc: "Busca de subdomínios via DNS Certificate Transparency (CT) consultando crt.sh, Sonar Omnisint e HackerTarget.",
        use: "Insira o domínio (ex: google.com) e veja a listagem de subdomínios indexados em certificados SSL.",
        kws: ["osint", "subdomain", "recon", "dns", "dnssec", "crtsh", "sonar"]
    },
    {
        num: "23",
        name: "Local Gateway discovery",
        category: "automation",
        desc: "Pesquisa automatizada por gateway padrão ativo e interfaces físicas locais.",
        use: "Inicie a ferramenta para obter informações imediatas sobre tabela de rotas locais e IPs do enlace.",
        kws: ["gateway", "local", "interfaces", "discovery", "arp", "route"]
    },
    {
        num: "24",
        name: "Local Devices Discovery (ARP)",
        category: "automation",
        desc: "Escaneamento ARP passivo de alta velocidade para descobrir IPs, MACs e fabricantes de dispositivos na subrede local.",
        use: "Inicie a ferramenta e veja a tabela ARP resolvida de forma síncrona contra base OUI de fabricantes offline.",
        kws: ["arp", "discovery", "devices", "mac", "vendor", "lan"]
    },
    {
        num: "25",
        name: "SNMP Mass Collector",
        category: "automation",
        desc: "Coleta massiva de informações via SNMPv2c (descrição do sistema, uptime, interfaces de roteador).",
        use: "Digite o IP e a comunidade SNMP (default: public) para auditar portas físicas e descrições MIB nativas.",
        kws: ["snmp", "mibs", "mass", "collector", "noc", "community"]
    },
    {
        num: "26",
        name: "SSH Command Runner",
        category: "automation",
        desc: "Execução automatizada de comandos em múltiplos equipamentos via SSH concorrente usando Netmiko/Paramiko.",
        use: "Insira a lista de hosts e comandos a disparar em lote para automações rápidas de NOC e segurança.",
        kws: ["ssh", "automation", "netmiko", "commands", "runner", "batch"]
    },
    {
        num: "27",
        name: "Multi-Vendor Auditor",
        category: "automation",
        desc: "Auditor interativo de comandos multi-vendor com suporte de templates Netmiko para roteadores Cisco, Juniper, Huawei, Mikrotik.",
        use: "Selecione a ferramenta e especifique as credenciais de auditoria SSH de roteadores principais.",
        kws: ["cisco", "juniper", "huawei", "mikrotik", "audit", "netmiko", "noc"]
    },
    {
        num: "28",
        name: "MikroTik API Config Auditor",
        category: "automation",
        desc: "Conecta na API nativa do RouterOS (MikroTik) para validar integridade de firewall, NAT e portas de serviços padrão abertas.",
        use: "Insira IP e credenciais API da MikroTik (porta 8728) e aguarde o relatório estruturado de segurança do NOC.",
        kws: ["mikrotik", "routeros", "api", "firewall", "audit", "security"]
    },
    {
        num: "29",
        name: "IP Address Plan (IPAM Generator)",
        category: "automation",
        desc: "Gerador e planejador automatizado de sub-redes CIDR com calculadora de máscaras, hosts livres e prefixos.",
        use: "Digite o bloco CIDR pai (ex: 192.168.0.0/24) e o tamanho das sub-redes filhas desejadas.",
        kws: ["ipam", "subnetting", "cidr", "planner", "addressing", "generator"]
    },
    {
        num: "30",
        name: "VLAN Planner",
        category: "automation",
        desc: "Planejador de domínios de colisão VLAN com IDs numéricos (802.1Q), descrições de subnets e diagramas NOC.",
        use: "Selecione a ferramenta para criar layouts hierárquicos e estruturados de tags de switches e roteadores.",
        kws: ["vlan", "switching", "8021q", "planner", "ids", "tags"]
    },
    {
        num: "31",
        name: "Cisco Config Generator",
        category: "automation",
        desc: "Gerador automatizado de arquivos de configuração base Cisco IOS (SSH, VTY, interfaces, roteamento, DHCP).",
        use: "Responda às perguntas interativas sobre IPs e interfaces e obtenha o arquivo de configuração de borda limpo.",
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
            "<span class='cyan'>[BASTIDORES] Carregando subsistemas do Core, cores ANSI e verificando chaves de API...</span>",
            "╔══════════════════════════════════════════════════════════════════════════════╗",
            "║  <span class='green'>:: A U R E A ::</span>  |                 PAINEL DE FERRAMENTAS PRINCIPAL              ║",
            "╚══════════════════════════════════════════════════════════════════════════════╝",
            "  Selecione a ferramenta desejada no menu..."
        ]
    },
    {
        cmd: "bgp_looking_glass --target 8.8.8.8",
        delay: 2000,
        output: [
            "<span class='yellow'>Minerando dados BGP globais via RIPE RIS e RPKI...</span> (Aguarde)",
            "  <span class='green'>✓</span> Prefixo BGP:  <span class='green'>8.8.8.0/24</span>",
            "  <span class='green'>✓</span> Origin ASN:  <span class='yellow'>AS15169</span> (Google LLC)",
            "  <span class='green'>✓</span> RPKI Status: <span class='green'>VALID (Assinado digitalmente)</span>",
            "",
            "<span class='cyan'>CAMINHOS DE PROPAGAÇÃO AS-PATH (GLOBAL SAMPLES):</span>",
            "  <span class='bold'>[RRC01]</span> via AS2914 | NextHop: 5.57.80.113",
            "    └─ Flow: <span class='cyan'>[AS2914 (NTT - Tier-1)]</span> <span class='bold'>➔</span> <span class='green'>[AS15169 (Google)]</span>"
        ]
    },
    {
        cmd: "ssl_inspector --domain google.com",
        delay: 2000,
        output: [
            "<span class='yellow'>Iniciando auditoria criptográfica profunda do canal SSL/TLS...</span>",
            "  • TLSv1.2   | Status: <span class='green'>SUPORTADO</span>            | Seguro (Padrão)",
            "  • TLSv1.3   | Status: <span class='green'>SUPORTADO</span>            | Recomendado (Ultra-Seguro)",
            "",
            "<span class='cyan'>2. Canal Criptográfico Ativo & Cipher Audit:</span>",
            "  • Status de Validação: <span class='green'>VÁLIDO / CONFIÁVEL</span>",
            "  • Cipher Ativa:   <span class='green'>TLS_AES_256_GCM_SHA384 (FORTE)</span>",
            "  • TLS Negociado:  <span class='cyan'>TLSv1.3</span>"
        ]
    },
    {
        cmd: "netflow --port 2055 --filter-ip 192.168.1.100",
        delay: 2500,
        output: [
            "<span class='cyan'>✓ Coletor NetFlow v5 ativo na porta UDP 2055...</span>",
            "<span class='yellow'>  Preparando painel interativo... (Aguarde)</span>",
            "  • Filtro NOC Ativo:  <span class='yellow'>Filtrando por IP: 192.168.1.100</span>",
            "  • Velocímetro (30s): [<span class='green'>▄▆█▆▄▃      █</span>] (Max: 800.00 Kbps)",
            "  • Throughput Total:  <span class='yellow'>800.00 Kbps</span> | Down: 500.00 Kbps | Up: 300.00 Kbps",
            "",
            "<span class='cyan'> [2] ROTEADORES EXPORTADORES / ROUTERS EMITTING FLOWS</span>",
            "  192.168.1.1        | <span class='yellow'>800.00 Kbps</span>  | <span class='green'>Cisco Systems</span>                | 120",
            "",
            "<span class='cyan'> [5] CONGESTIONAMENTO DE INTERFACES SNMP / SNMP INTERFACE PROFILER</span>",
            "  IfIndex 1  |      1.50 MB |      0.00 MB | <span class='red'>CONGESTIONADO              (60.0%)</span>",
            "  IfIndex 2  |      0.00 MB |      1.00 MB | <span class='yellow'>CARGA ALTA                 (40.0%)</span>"
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
                <p>Nenhuma ferramenta encontrada com os filtros e termos inseridos.</p>
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
            <p><strong>Propósito:</strong> ${tool.desc}</p>
            <p><strong>Como usar:</strong> <em>${tool.use}</em></p>
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
    btn.innerHTML = `<i class="fa-solid fa-circle-check"></i> Copiado!`;
    btn.style.borderColor = "var(--green)";
    
    setTimeout(() => {
        btn.innerHTML = `<i id="pix-icon" class="fa-regular fa-copy"></i> Copiar`;
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
