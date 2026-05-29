"""
aurea.tools.descriptions — Descriptions and usage manuals for all 31 Aurea tools.
"""

TOOL_GUIDES = {
    "1": {
        "pt": {
            "desc": "Traçado de rotas contínuo com estatísticas de perda de pacotes e jitter (variação de latência) em tempo real.",
            "use": "Insira o IP/host de destino. O MTR enviará pacotes consecutivamente. Pressione Ctrl+C para encerrar."
        },
        "en": {
            "desc": "Continuous traceroute with real-time packet loss and jitter (latency variation) statistics.",
            "use": "Enter the destination IP/host. The MTR will probe hops consecutively. Press Ctrl+C to stop."
        }
    },
    "2": {
        "pt": {
            "desc": "Busca binária automatizada para descobrir o MTU (Maximum Transmission Unit) exato sem fragmentação no enlace físico.",
            "use": "Insira o host de destino. A ferramenta executará ping com bit Don't Fragment (DF) ativo de 1200 a 1500 bytes."
        },
        "en": {
            "desc": "Automated binary search to discover the exact path MTU (Maximum Transmission Unit) without packet fragmentation.",
            "use": "Enter the destination host. The tool will run pings with the Don't Fragment (DF) bit set from 1200 to 1500 bytes."
        }
    },
    "3": {
        "pt": {
            "desc": "Scanner de portas TCP de alta velocidade (modelo NMAP) para identificar portas abertas e mapear serviços/banners em tempo real.",
            "use": "Digite o IP/host de destino. O sistema varrerá automaticamente as 1000 portas mais comuns de redes e tentará obter as versões dos serviços rodando."
        },
        "en": {
            "desc": "High-speed TCP port scanner (NMAP model) to identify open ports and map services/banners in real-time.",
            "use": "Enter the target IP/host. The system will automatically scan the 1000 most common network ports and attempt to grab running service versions."
        }
    },
    "4": {
        "pt": {
            "desc": "Matriz dinâmica de latência e qualidade de rota para principais nuvens globais (AWS, GCP, Azure, Oracle) e CDNs (Cloudflare, Akamai, Fastly).",
            "use": "Inicie a ferramenta para medir em tempo real o RTT e a perda de pacotes para os backbones globais de nuvem e borda de rede."
        },
        "en": {
            "desc": "Dynamic ISP latency matrix and routing quality analyzer for major global clouds (AWS, GCP, Azure, Oracle) and CDNs (Cloudflare, Akamai, Fastly).",
            "use": "Launch the tool to measure real-time RTT and packet loss concurrently to global cloud and edge backbones."
        }
    },
    "5": {
        "pt": {
            "desc": "Planejador de sub-redes e detector de conflito overlay para faixas IPv4/IPv6 em túneis, VPNs ou peers de rede.",
            "use": "Insira suas sub-redes existentes e a sub-rede proposta. O sistema auditará colisões/sobreposições e sugerirá faixas livres."
        },
        "en": {
            "desc": "Subnet planner and overlay conflict detector for IPv4/IPv6 ranges across tunnels, VPNs, or network peers.",
            "use": "Enter your existing subnets and the proposed subnet. The system will audit collisions/overlaps and suggest conflict-free ranges."
        }
    },
    "6": {
        "pt": {
            "desc": "Mapeia o seu IP público atual, Provedor de Internet (ISP), ASN de trânsito e localização geográfica aproximada.",
            "use": "Selecione a ferramenta e o sistema consultará de forma segura o dossiê da sua conexão atual via HTTPS."
        },
        "en": {
            "desc": "Maps your current public IP, Internet Service Provider (ISP), transit ASN, and approximate geographical location.",
            "use": "Select the tool and the system will securely fetch your current connection dossier via HTTPS."
        }
    },
    "7": {
        "pt": {
            "desc": "Consulta de inteligência (OSINT) e geolocalização detalhada para qualquer IP público de trânsito global.",
            "use": "Insira o endereço IP de destino ou nome de host público e aguarde o retorno das coordenadas e operadora."
        },
        "en": {
            "desc": "Intelligence query (OSINT) and detailed geolocation for any public global transit IP address.",
            "use": "Enter the target IP address or public host name and wait for the coordinates and carrier details."
        }
    },
    "8": {
        "pt": {
            "desc": "Detector de interceptações e sequestros de DNS locais usando validação trilateral (3-way) contra Cloudflare e Quad9 DoH.",
            "use": "Selecione a ferramenta. Ela simulará falhas de NXDOMAIN e divergências de DoH para auditar se há proxy/interceptação."
        },
        "en": {
            "desc": "Local DNS interception and hijacking detector using 3-way validation against Cloudflare and Quad9 DoH.",
            "use": "Select the tool. It will simulate NXDOMAIN failures and DoH divergences to audit for proxying or interception."
        }
    },
    "9": {
        "pt": {
            "desc": "Simulador NOC de rajada paralela de sockets para auditar limites de conexões simultâneas e esgotamento de CGNAT.",
            "use": "Insira o host e o número de sockets paralelos (ex: 150). O sistema calculará a latência média e a taxa de perda/timeout."
        },
        "en": {
            "desc": "NOC socket burst simulator to audit concurrent connection limits and CGNAT port exhaustion.",
            "use": "Enter the host and number of concurrent sockets (e.g. 150). The system will compute average latency and loss/timeout rates."
        }
    },
    "10": {
        "pt": {
            "desc": "Benchmark de latência e resolução DNS local comparando o seu roteador com Google, Cloudflare, Quad9 e OpenDNS.",
            "use": "Digite o domínio de teste (ex: google.com) e observe o tempo exato de resposta UDP de cada servidor DNS em milissegundos."
        },
        "en": {
            "desc": "Latency and resolution benchmark for local DNS comparing your gateway with Google, Cloudflare, Quad9, and OpenDNS.",
            "use": "Enter the test domain (e.g. google.com) and observe the exact UDP response time of each DNS server in milliseconds."
        }
    },
    "11": {
        "pt": {
            "desc": "Audita o tempo de propagação global e resolução de registros 'A' de um domínio em servidores DNS mundiais em paralelo.",
            "use": "Insira o nome de domínio e veja em tempo real as respostas convergentes ou divergentes nos servidores mundiais."
        },
        "en": {
            "desc": "Audits global propagation time and 'A' record resolution for a domain across worldwide DNS servers in parallel.",
            "use": "Enter the domain name and view in real-time the convergent or divergent responses across global servers."
        }
    },
    "12": {
        "pt": {
            "desc": "Verificador de assinaturas criptográficas DNSSEC ativas e autenticação segura AD (Authenticated Data) de domínios.",
            "use": "Insira o domínio para auditar e veja se ele possui registros DS publicados e suporte a chaves criptográficas DNSKEY."
        },
        "en": {
            "desc": "Cryptographic DNSSEC active signatures and AD (Authenticated Data) secure validation checker for domains.",
            "use": "Enter the domain to audit and see if it has DS records published and supports DNSKEY cryptographic keys."
        }
    },
    "13": {
        "pt": {
            "desc": "Scanner e inspetor estrito de certificados SSL/TLS para verificar validade, entidade emissora (CA) e dias para expiração.",
            "use": "Insira o domínio na porta 443 e aguarde o download e parse do certificado X.509 transmitido na sessão."
        },
        "en": {
            "desc": "SSL/TLS certificate scanner and strict inspector to verify validity, Certificate Authority (CA), and days to expiration.",
            "use": "Enter the domain on port 443 and wait for the download and parsing of the transmitted X.509 certificate."
        }
    },
    "14": {
        "pt": {
            "desc": "Scaneia cabeçalhos de segurança HTTP (HSTS, CSP, X-Frame-Options, X-Content-Type) de servidores web.",
            "use": "Insira a URL completa (ex: https://registro.br) e o sistema avaliará os níveis de proteção contra injeções de script."
        },
        "en": {
            "desc": "Scans web server HTTP security headers (HSTS, CSP, X-Frame-Options, X-Content-Type) to evaluate vulnerability levels.",
            "use": "Enter the complete URL (e.g. https://registro.br) and the system will score protections against script injections."
        }
    },
    "15": {
        "pt": {
            "desc": "Conecta em soquetes de serviços comuns para capturar banners e assinaturas de versão (SSH, FTP, SMTP, HTTP, etc.).",
            "use": "Insira o IP/host de destino e a porta de rede. O sistema exibirá o payload bruto retornado pelo daemon."
        },
        "en": {
            "desc": "Connects to common service sockets to capture raw daemon banners and version signatures (SSH, FTP, SMTP, HTTP, etc.).",
            "use": "Enter the target IP/host and port. The system will display the raw payload returned by the daemon."
        }
    },
    "16": {
        "pt": {
            "desc": "Auditoria de registros de segurança DNS SPF e DMARC contra spoofing de e-mail e campanhas de phishing.",
            "use": "Insira o domínio corporativo e veja se ele possui políticas duras (reject, softfail) ou permissivas."
        },
        "en": {
            "desc": "Auditing of DNS SPF and DMARC security records to prevent email spoofing and phishing campaigns.",
            "use": "Enter the corporate domain and see if it has strict (reject, softfail) or permissive policies."
        }
    },
    "17": {
        "pt": {
            "desc": "Inspetor aprofundado de zona DNS que extrai todos os registros essenciais (A, AAAA, MX, TXT, NS, SOA, DS) de uma vez.",
            "use": "Insira o domínio. A ferramenta consultará a API DoH de forma abrangente e estruturará os registros."
        },
        "en": {
            "desc": "Deep DNS zone inspector that extracts all essential records (A, AAAA, MX, TXT, NS, SOA, DS) at once.",
            "use": "Enter the domain name. The tool will comprehensively query DoH APIs and structure the records."
        }
    },
    "18": {
        "pt": {
            "desc": "Consultor global Looking Glass que consolida caminhos de trânsito AS-Path (RIPE RIS) e validação RPKI para qualquer IP/bloco.",
            "use": "Insira o IP ou prefixo CIDR. Veja os caminhos de anúncios globais e a integridade ROA de trânsito de rede."
        },
        "en": {
            "desc": "Global Looking Glass aggregator that consolidates AS-Path transit routes (RIPE RIS) and RPKI validation for any IP/CIDR block.",
            "use": "Enter the IP or CIDR block. View global route announcements and transit ROA integrity."
        }
    },
    "19": {
        "pt": {
            "desc": "Validador criptográfico estrito de anúncios BGP RPKI para verificar a legitimidade do ASN de origem de blocos CIDR.",
            "use": "Insira o prefixo e o ASN de origem correspondente. O sistema consultará as assinaturas digitais ROA do RIPE NCC."
        },
        "en": {
            "desc": "Strict BGP RPKI cryptographic validator to check the legitimacy of the origin ASN for CIDR blocks.",
            "use": "Enter the prefix and corresponding origin ASN. The system will query ROA digital signatures from RIPE NCC."
        }
    },
    "20": {
        "pt": {
            "desc": "Consulta detalhes de conexões de peering, servidores IXP públicos e presença em data centers de operadoras no PeeringDB.",
            "use": "Digite o número do ASN de trânsito (ex: 15169 para Google, 264321) e veja os pontos de troca de tráfego ativos."
        },
        "en": {
            "desc": "Queries peering connections, public IXP exchange layers, and datacenter footprints for networks in PeeringDB.",
            "use": "Enter the transit ASN number (e.g. 15169 for Google, 264321) and view active exchange points."
        }
    },
    "21": {
        "pt": {
            "desc": "Monitor em tempo real de fluxos de conexões TCP/UDP locais ou receptor daemon NOC de pacotes NetFlow v5 (porta 2055).",
            "use": "Escolha entre monitor de conexões locais (ss/netstat com ASN) ou coletor daemon NOC NetFlow v5 em tempo real."
        },
        "en": {
            "desc": "Real-time monitor of local TCP/UDP connection flows or NOC daemon collector of NetFlow v5 UDP packets (port 2055).",
            "use": "Choose between monitoring active local connections (ss/netstat with ASN lookup) or the real-time NOC NetFlow v5 daemon."
        }
    },
    "22": {
        "pt": {
            "desc": "Reconhecimento OSINT avançado de subdomínios públicos ativos usando crt.sh, Omnisint e HackerTarget.",
            "use": "Insira o domínio corporativo e aguarde a indexação paralela dos subdomínios descobertos."
        },
        "en": {
            "desc": "Advanced OSINT subdomain reconnaissance using public certificate logs from crt.sh, Omnisint, and HackerTarget.",
            "use": "Enter the target domain and wait for the parallel indexing of discovered subdomains."
        }
    },
    "23": {
        "pt": {
            "desc": "Scanner de rede local (LAN) ultrarrápido que envia varreduras ARP para listar dispositivos conectados e fabricantes.",
            "use": "Selecione a ferramenta e o sistema detectará as sub-redes ativas e enviará requisições ARP em threads paralelas."
        },
        "en": {
            "desc": "Ultrarapid local network (LAN) scanner using parallel ARP requests to discover active devices and MAC vendors.",
            "use": "Select the tool and the system will detect active subnets and run ARP probes across parallel threads."
        }
    },
    "24": {
        "pt": {
            "desc": "Scanner de portas TCP multithreaded para identificar serviços abertos em hosts de forma rápida.",
            "use": "Insira o IP/host de destino e especifique o número de threads. O sistema varrerá as portas mais comuns."
        },
        "en": {
            "desc": "Multithreaded TCP port scanner to rapidly identify open services on hosts.",
            "use": "Enter the target IP/host and specify the thread count. The system will scan well-known ports."
        }
    },
    "25": {
        "pt": {
            "desc": "Varre a rede LAN local para descobrir dispositivos ativos e envia automaticamente novos registros de IPs e MACs para o NetBox.",
            "use": "Configure o token do NetBox e o sistema efetuará a varredura e sincronização dinâmica do IPAM de forma automatizada."
        },
        "en": {
            "desc": "Scans your local LAN to discover active devices and automatically syncs new IP and MAC records directly into NetBox.",
            "use": "Configure your NetBox credentials, and the system will scan and dynamically sync the IPAM database."
        }
    },
    "26": {
        "pt": {
            "desc": "Comparador visual de arquivos de configuração de roteadores e switches com marcação colorida de linhas alteradas (diff).",
            "use": "Insira o caminho absoluto dos dois arquivos de configuração. O sistema renderizará o diff colorido formatado."
        },
        "en": {
            "desc": "Visual config file diff comparator for routers and switches with color-coded syntax highlighting of differences.",
            "use": "Enter the absolute paths of both configuration files. The system will output a clean side-by-side color diff."
        }
    },
    "27": {
        "pt": {
            "desc": "Conecta via SSH em múltiplos roteadores e switches corporativos (Cisco, Juniper, Huawei) para extrair inventário e sincronizar no NetBox.",
            "use": "Selecione para processar os dispositivos do parque de rede configurados e gerar relatórios de auditoria."
        },
        "en": {
            "desc": "Connects via SSH to enterprise routers and switches (Cisco, Juniper, Huawei) to collect inventory data and sync to NetBox.",
            "use": "Trigger to process network inventory, execute SSH commands, audit settings, and update NetBox databases."
        }
    },
    "28": {
        "pt": {
            "desc": "Agrega e resume sub-redes IP consecutivas ou sobrepostas nas menores faixas CIDR possíveis de roteamento.",
            "use": "Insira a lista de sub-redes separadas por vírgulas (ex: 192.168.1.0/24, 192.168.2.0/24) e obtenha os supernets agregados."
        },
        "en": {
            "desc": "Aggregates and summarizes consecutive or overlapping IP subnets into the minimal routing CIDR prefixes.",
            "use": "Enter subnets separated by commas (e.g. 192.168.1.0/24, 192.168.2.0/24) and obtain the aggregated supernet prefixes."
        }
    },
    "29": {
        "pt": {
            "desc": "Monitor gráfico em tempo real de força de sinal Wi-Fi (RSSI em dBm) com alertas de atenuação e limites.",
            "use": "Inicie a ferramenta e veja em streaming a oscilação do sinal da placa de rede ativa em milissegundos."
        },
        "en": {
            "desc": "Real-time graphic monitor of Wi-Fi signal strength (RSSI in dBm) with attenuation thresholds and warnings.",
            "use": "Start the tool and view in streaming the active interface signal oscillation in milliseconds."
        }
    },
    "30": {
        "pt": {
            "desc": "Cliente WHOIS nativo para consultar registro e titularidade de domínios diretamente via portas de sockets TCP 43.",
            "use": "Insira o domínio (ex: google.com) e o sistema descobrirá o servidor WHOIS autoritativo e capturará o registro."
        },
        "en": {
            "desc": "Native WHOIS client to query domain registration and ownership directly using TCP socket port 43 connections.",
            "use": "Enter the domain name (e.g. google.com) and the system will locate the TLD server and fetch the record."
        }
    },
    "31": {
        "pt": {
            "desc": "Calculadora de alta disponibilidade que converte 'noves de SLA' (ex: 99.999%) em tolerância exata de tempo de inatividade.",
            "use": "Insira a porcentagem de SLA desejada e o sistema gerará a janela permitida de downtime por ano/mês/dia."
        },
        "en": {
            "desc": "High availability SLA calculator that translates 'SLA nines' (e.g. 99.999%) into exact permitted downtime thresholds.",
            "use": "Enter the desired SLA percentage and the system will output downtime tolerances per year/month/day."
        }
    }
}
