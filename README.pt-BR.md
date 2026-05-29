# Aurea Tools

[![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Termux%20%7C%20macOS-orange)](https://github.com/js-victr/aurea-tools)

**Aurea** é um console avançado de diagnóstico de rede, engenharia BGP e segurança cibernética projetado especificamente para engenheiros de provedores (ISPs), administradores de rede e profissionais de NOC.

Reestruturado de um script monolítico para um pacote modular moderno, o Aurea é **100% Gratuito e Open-Source (Código Aberto)**, trazendo ferramentas de CLI de nível profissional para qualquer terminal, com zero dependências complexas.

---

## 💖 Apoie o Projeto / Contribuições

O AureaTools é um projeto livre e mantido voluntariamente pela comunidade. Se o Aurea economizou seu tempo em operações de NOC, troubleshooting de rotas ou auditorias BGP, considere apoiar nosso desenvolvimento!

* **🔗 Linktree de Doações:** [https://js-victr.github.io/aurea-tools/donate](https://js-victr.github.io/aurea-tools/donate)
* **🔑 Chave Pix (Brasil):** `apoio@aureatools.com`
* **⭐ GitHub Sponsors:** [https://github.com/sponsors/js-victr](https://github.com/sponsors/js-victr)

---

## 🌟 Recursos Principais (35 Ferramentas Inclusas)

O console é organizado em **4 submenus dinâmicos** para agilizar sua rotina de troubleshooting:

### 1. Diagnóstico & Conectividade (`diagnostics`)
* **IP Local & Interfaces:** Mapeamento detalhado das interfaces de saída IPv4/IPv6 e NAT de borda.
* **ICMP Ping (v4/v6):** Motores de ping rápidos e limpos com estatísticas de latência precisas.
* **Traceroute de Rede:** Mapeamento de rotas identificando sistemas autônomos (AS) e saltos dos pacotes.
* **MTR Avançado:** Traceroute contínuo com perda de pacotes, latência média e jitter em tempo real por salto.
* **Teste de Porta TCP:** Valida conexões TCP simples em portas e hosts customizados.
* **Teste de Banda (Speedtest):** Medição de performance de download, upload e ping direto da CLI.
* **Teste de MTU & Fragmentação:** Identifica limites de fragmentação (Path MTU Discovery) nas rotas.
* **Teste de Portal Cativo HTTP:** Inspeciona redes cativas capturando URLs de redirecionamento HTTP.

### 2. Serviços IP & Segurança Web (`services`)
* **IP Público & ASN Lookup:** Geolocalização de IP externo, provedor de internet e metadados de ASN.
* **IP Intelligence & Recon:** Dossiê completo mapeando reputação de IP, operadora, organização e DNS reverso.
* **DNS Benchmark Local:** Comparação em tempo real de latência de resolução entre resolvedores globais e o gateway local.
* **Verificador de Propagação DNS:** Consulta registros de domínio em múltiplos servidores globais simultaneamente para validar propagação.
* **Validação DNSSEC:** Verificação de segurança criptográfica de registros de zona DNS e do resolvedor local.
* **Inspetor de Certificados SSL/TLS:** Mapeia CN, Emissor, datas de validade e alertas de expiração do certificado do site com suporte a verificação ativa de protocolos TLS 1.0-1.3, auditoria de suítes de criptografia fracas e fallback seguro de validação não verificada em caso de falha de confiança.
* **Scanner de Cabeçalhos HTTP:** Avalia a blindagem do servidor web (HSTS, CSP, proteção contra Clickjacking).
* **Banner Grabbing:** Coleta de fingerprint de serviços e versões através de conexões em sockets crus.
* **Auditor de Spoofing DNS:** Valida alinhamentos e existência de políticas SPF e DMARC para avaliar exposição a phishing.

### 3. Engenharia BGP & Roteamento (`bgp`)
* **Auditor de Rotas BGP:** Prefix overview global, vizinhanças upstream/downstream e mineração de objetos de política no RADB WHOIS.
* **Validador RPKI (BGP):** Validação criptográfica de assinaturas ROA de prefixos diretamente no RIPE NCC.
* **Looking Glass BGP:** Visibilidade global de prefixos, caminhos de AS (AS-path) e anúncios de comunidades BGP via coletores RIPE RIS com fluxo de hops AS-Path dinâmico em ASCII, marcação de operadoras Tier-1 e expansão interativa para visualizar todos os coletores de rotas RIS ativos.
* **Decodificador de Communities BGP:** Traduz comunidades standard/large de grandes operadoras (NTT, HE, Lumen, Telia, etc.).
* **Consulta PeeringDB:** Verifica presença em IXPs, datacenters e regras de política de peering registradas da rede.
* **Monitor de Tráfego & ASN (AureaFlow):** Captura conexões de soquetes locais para CSV com tags de operadora/ASN ou inicia o coletor de NOC daemon NetFlow v5 ativo com velocímetro de banda dinâmico (gráficos sparkline), mapeamento de serviço DPI, perfil de carga SNMP IfIndex físico e filtros ativos customizados.
* **OSINT Subdomínios:** Consulta registros públicos de transparência de certificados (crt.sh) para listar subdomínios expostos.

### 4. Utilitários & Automação de NOC (`automation`)
* **Varredura de Dispositivos LAN:** Mapeamento instantâneo do cache ARP local com IPs e MACs adjacentes.
* **Escaneador de Portas Multithread:** Escaneamento concorrente ultra-rápido de múltiplas portas TCP comuns.
* **[NOVO] Auto-Descoberta LAN & NetBox Sync:** Ping sweep concorrente em CIDR, resolve DNS reverso (PTR), resolve fabricantes de hardware locais (OUI), exporta planilhas CSV de inventário e sincroniza os IPs descobertos nativamente no **NetBox IPAM** via REST!
* **[NOVO] MikroTik SSH Auditor & NetBox Sync:** Conecta a roteadores RouterOS via SSH nativo, mapeia interfaces, IPs ativos, VLANs, vizinhos LLDP/CDP e envia dinamicamente ao NetBox IPAM!
* **[NOVO] Agregador e Otimizador BGP CIDR:** Consolida matematicamente sub-redes adjacentes ou sobrepostas no menor conjunto possível de blocos IP ótimos para economizar TCAM BGP.
* **Calculadora IPAM & Subnetting:** Dimensionamento de blocos IP, capacidade de hosts, notação reversa PTR e divisão de sub-redes.
* **Calculadora de SLA & Uptime:** Calcula tempos permitidos de queda contratual diários, mensais e anuais.
* **Monitor Wi-Fi RSSI ao Vivo:** Monitoramento contínuo da potência de sinal de rádio Wi-Fi, BSSID, canal e velocidades.
* **Teste de Latência CDN & Apps:** Medição de latência contra grandes plataformas de CDN (Google, Netflix, WhatsApp, Cloudflare).
* **Consulta MAC & OUI:** Identifica fabricante de placas de rede através do prefixo OUI do MAC address.
* **Cliente WHOIS Nativo:** Consulta de metadados de registro de domínios diretamente via socket na porta 43.
* **Gerador de Senhas Seguras:** Geração local de senhas de alta entropia para equipamentos e clientes.

---

## 🚀 Instalação & Configuração

Você pode instalar o Aurea diretamente em modo de desenvolvimento:

```bash
# Clonar o repositório
git clone https://github.com/js-victr/aurea-tools.git
cd aurea-tools

# Instalar em modo de desenvolvimento
pip install -e .
```

---

## 💻 Utilização via CLI

Uma vez instalado, o comando `aurea` estará disponível no PATH global do seu terminal:

```bash
# Abrir o console interativo dinâmico
aurea

# Executar uma ferramenta diretamente pelo seu índice (ex: IP Público & ASN)
aurea --run 8

# Forçar a tradução para português (Brasil)
aurea --lang pt

# Desativar os códigos de escape de cores ANSI
aurea --no-color

# Listar todas as ferramentas
aurea --list

# Exibir informações de versão
aurea --version
```

---

## 🌍 Internacionalização (i18n)

O Aurea é completamente bilíngue! Ele auto-detecta o idioma do sistema operacional host (suportando inglês e português de fábrica).

Você também pode alternar dinamicamente o idioma diretamente no menu interativo pressionando a tecla **`[L]`**, ou via argumentos de linha de comando usando `--lang pt` ou `--lang en`.

---

## 🧪 Executando Testes

O Aurea possui cobertura de testes unitários robustos. Para executar a suíte de testes:

```bash
python -m unittest discover tests
```

---

## 🌐 Portal de Documentação Web (GitHub Pages)

O AureaTools possui uma página de apresentação interativa e um portal de documentação web premium. O portal apresenta emulação de terminal responsivo, visualizador interativo de ferramentas, passos de instalação e suporte a doações:

* **🔗 Portal Ativo:** [https://js-victr.github.io/aurea-tools](https://js-victr.github.io/aurea-tools)
* **📁 Pasta de Origem:** Localizada em `docs/` na raiz do repositório.

Para hospedar este portal em seu próprio fork do GitHub:
1. Vá até as configurações (**Settings**) do seu repositório no GitHub.
2. Navegue até a seção **Pages** no menu lateral esquerdo.
3. Sob **Build and deployment**, selecione **Deploy from a branch**.
4. Defina a branch para `main` (ou sua branch ativa) e altere a opção da pasta de `/ (root)` para `/docs`.
5. Clique em **Save** e aguarde o GitHub publicar sua documentação web de NOC interativa!

---

## 📄 Licença

Distribuído sob a licença Apache 2.0. Consulte o arquivo `LICENSE` para mais detalhes.
