<<<<<<< HEAD
# 🛡️ SENTRA - Scanner de Segurança de Redes

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.7+-green.svg)](https://doc.qt.io/qtforpython/)
[![Nmap](https://img.shields.io/badge/Nmap-Integration-orange.svg)](https://nmap.org/)
[![Status](https://img.shields.io/badge/Status-Ativo-brightgreen.svg)](#)

> **SENTRA** é uma aplicação desktop robusta para análise e monitoramento de segurança de redes. Ele oferece uma interface gráfica intuitiva para realizar scans de rede, classificar vulnerabilidades e gerar relatórios detalhados em PDF.

---

## 📋 Índice

- [Características Principais](#-características-principais)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Instalação](#-instalação)
- [Uso](#-uso)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Funcionalidades Implementadas](#-funcionalidades-implementadas)
- [Guia de Uso](#-guia-de-uso)
- [Troubleshooting](#-troubleshooting)
- [Futuras Implementações](#-futuras-implementações)
- [Licença](#-licença)

---

## ✨ Características Principais

### 🔍 Análise de Redes Avançada
- **Scans flexíveis**: Escancie IPs individuais, faixas CIDR ou redes inteiras
- **Múltiplos tipos de scan**: Rápido, Completo, Agressivo, UDP e mais
- **Detecção de SO**: Identifica sistema operacional de hosts alvo
- **Scripts NSE**: Suporte a scripts Nmap para análise aprofundada
- **Detecção de firewall**: Reconhece dispositivos com firewall ativo

### 📊 Classificação de Risco
- **Análise automática**: Classifica portas e serviços por nível de risco
- **Descrições detalhadas**: Contexto de segurança para cada achado
- **Recomendações**: Sugestões de mitigação baseadas em riscos

### 📈 Relatórios Profissionais
- **Relatórios em PDF**: Geração automática de relatórios formatados
- **Histórico completo**: Rastreamento de todas as análises realizadas
- **Exportação de dados**: Salve e compartilhe resultados

### 🎨 Interface Moderna
- **Dashboard intuitivo**: Visualização clara de resultados
- **Abas organizadas**: Análise, Resultados, Vulnerabilidades, Relatórios, Configurações
- **Design responsivo**: Adaptável a diferentes resoluções
- **Dark mode ready**: Paleta de cores profissional

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Versão | Propósito |
|-----------|--------|----------|
| **Python** | 3.10+ | Linguagem principal |
| **PySide6** | 6.7+ | Framework GUI (Qt) |
| **Nmap** | Latest | Engine de scanning de rede |
| **fpdf2** | 2.7+ | Geração de relatórios PDF |
| **psutil** | - | Monitoramento de sistema |
| **SQLAlchemy** | - | ORM para banco de dados (futuro) |

---

## 📥 Instalação

### Pré-requisitos
- Python 3.10 ou superior
- Nmap instalado no sistema
- pip (gerenciador de pacotes Python)

### Windows

1. **Instale o Nmap**:
   ```bash
   winget install Insecure.Nmap
   ```

2. **Clone ou baixe o repositório**:
   ```bash
   git clone https://github.com/seu-usuario/sentra.git
   cd sentra
   ```

3. **Crie um ambiente virtual**:
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

4. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Execute a aplicação**:
   ```bash
   python app/main.py
   ```

### Linux/Mac

1. **Instale o Nmap**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install nmap
   
   # macOS
   brew install nmap
   ```

2. **Clone o repositório**:
   ```bash
   git clone https://github.com/seu-usuario/sentra.git
   cd sentra
   ```

3. **Crie um ambiente virtual**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Execute a aplicação**:
   ```bash
   python app/main.py
   ```

---

## 🚀 Uso

### Iniciando uma Análise

1. **Abra a aplicação** SENTRA
2. **Acesse a aba "Nova Análise"**
3. **Configure o target**:
   - IP individual: `192.168.1.100`
   - Faixa CIDR: `192.168.1.0/24`
   - Rede inteira: `192.168.0.0/16`

4. **Selecione o tipo de scan**:
   - **Rápido**: Scan rápido das portas comuns
   - **Completo**: Análise detalhada com detecção de SO
   - **Agressivo**: Scan intensivo (use com cautela)
   - **UDP**: Escaneia portas UDP
   - **Customizado**: Configure parâmetros específicos

5. **Configure opções avançadas**:
   - ✓ Detectar sistema operacional
   - ✓ Executar scripts NSE
   - ✓ Definir portas específicas
   - ✓ Timeout customizado
   - ✓ Threads paralelas

6. **Inicie o scan** e monitore o progresso

### Analisando Resultados

1. **Acesse a aba "Resultados"**
2. **Visualize**:
   - Hosts descobertos
   - Portas abertas/fechadas
   - Serviços identificados
   - Classificação de risco
   - Descrições e recomendações

3. **Explore vulnerabilidades** na aba dedicada
4. **Gere relatórios** em PDF

### Histórico e Relatórios

- **Aba Histórico**: Veja todas as análises anteriores
- **Aba Relatórios**: Acesse relatórios gerados
- **Auto-report**: Gere PDFs automaticamente após scans

---

## 📁 Estrutura do Projeto

```
sentra/
├── README.md                          # Este arquivo
├── requirements.txt                   # Dependências do projeto
├── app/
│   ├── main.py                        # Ponto de entrada da aplicação
│   ├── core/
│   │   ├── config.py                  # Configurações globais
│   │   └── security.py                # Utilitários de segurança
│   ├── database/
│   │   ├── models.py                  # Modelos de banco de dados
│   │   ├── session.py                 # Gerenciamento de sessão DB
│   │   └── migrations/                # Scripts de migração
│   ├── modules/
│   │   ├── scanner/
│   │   │   ├── scan_service.py        # Orquestração de scans
│   │   │   ├── nmap_runner.py         # Execução do Nmap
│   │   │   ├── parser.py              # Parser de saída Nmap
│   │   │   ├── risk_classifier.py     # Classificação de risco
│   │   │   └── scan_profiles.py       # Perfis de scan
│   │   └── reports/
│   │       ├── report_service.py      # Geração de relatórios
│   │       └── exporter.py            # Exportação de dados
│   ├── schemas/
│   │   └── scan_schema.py             # Schemas de validação
│   └── ui/
│       ├── main_window.py             # Janela principal
│       ├── styles.py                  # Estilos e temas
│       ├── ui_data.py                 # Estado global da UI
│       ├── screens/
│       │   ├── scan_screen.py         # Tela de nova análise
│       │   ├── results_screen.py      # Tela de resultados
│       │   ├── vulnerabilities_screen.py  # Tela de vulnerabilidades
│       │   ├── reports_screen.py      # Tela de relatórios
│       │   ├── history_screen.py      # Tela de histórico
│       │   ├── logs_screen.py         # Tela de logs
│       │   └── settings_screen.py     # Tela de configurações
│       ├── widgets/                   # Componentes reutilizáveis
│       ├── workers/
│       │   └── scan_worker.py         # Worker async para scans
│       └── assets/                    # Recursos (ícones, imagens)
```

---

## 🎯 Funcionalidades Implementadas

### ✅ Sistema de Scanning
- [x] Integração completa com Nmap
- [x] Suporte a múltiplos tipos de scan
- [x] Scan de IP único
- [x] Scan de faixa CIDR
- [x] Detecção de sistema operacional
- [x] Scripts NSE integrados
- [x] Timeout configurável
- [x] Threads paralelas ajustáveis
- [x] Filtro de portas customizado

### ✅ Análise de Resultados
- [x] Parser robusto de saída Nmap
- [x] Classificação automática de risco
- [x] Descrições de segurança
- [x] Recomendações de mitigação
- [x] Histórico de análises
- [x] Rastreamento de achados

### ✅ Interface Gráfica
- [x] Dashboard intuitivo
- [x] Abas organizadas
- [x] Visualização de resultados em tabelas
- [x] Barra de progresso em tempo real
- [x] Paleta de cores profissional
- [x] Responsividade

### ✅ Relatórios
- [x] Geração de PDF automática
- [x] Relatórios com metadados
- [x] Resumo executivo
- [x] Detalhes técnicos completos
- [x] Recomendações incluídas

### ✅ Gerenciamento
- [x] Configurações persistentes
- [x] Histórico de scans
- [x] Logs detalhados
- [x] Exportação de dados

---

## 🔄 Funcionalidades em Andamento (WIP)

Estas features estão em desenvolvimento ativo e serão lançadas em breve:

### ⚙️ Monitor de Conexões Ativas
- [ ] Visualização de conexões TCP/UDP em tempo real
- [ ] Integração com `psutil` para monitoramento local
- [ ] Novo painel dedicado na interface
- [ ] Detecção de processo associado a cada conexão

### 🌍 Geolocalização de IPs
- [ ] Integração com API de geolocalização (ipinfo.io)
- [ ] Cache de resultados para otimização
- [ ] Exibição de país, cidade e provedor
- [ ] Identificação de conexões suspeitas por localização

### 📢 Alertas e Notificações
- [ ] Sistema de alertas em tempo real
- [ ] Notificações para riscos críticos
- [ ] Histórico de alertas
- [ ] Configuração de regras de alerta

### 📊 Dashboard Avançado
- [ ] Monitoramento contínuo da rede
- [ ] Gráficos e estatísticas de risco
- [ ] Tendências de segurança
- [ ] Widget de status em tempo real

---

## 📖 Guia de Uso Detalhado

### 1. Primeiro Scan (Teste Local)

```
Alvo: 127.0.0.1 (seu próprio computador)
Tipo: Rápido
Opções: Nenhuma requerida
```

Este teste vai mostrar as portas abertas no seu PC.

### 2. Scan de Rede Local

```
Alvo: 192.168.1.0/24 (substitua pelo seu range)
Tipo: Completo
Opções:
  ✓ Detectar sistema operacional
  ✓ Executar scripts NSE
```

Mapeará todos os hosts na sua rede local.

### 3. Scan Direcionado com Relatório

```
Alvo: 192.168.1.100
Tipo: Completo
Opções:
  ✓ Auto-gerar relatório em PDF
  Timeout: 300 segundos
  Threads: 4
```

Gerará automaticamente um PDF com os resultados.

---

## 🔧 Troubleshooting

### Erro: "Nmap não encontrado"

**Solução**: Instale o Nmap no seu sistema
- Windows: `winget install Insecure.Nmap`
- Linux: `sudo apt-get install nmap`
- macOS: `brew install nmap`

### Erro: "Permissão negada"

**Solução**: Execute com permissões de administrador
- Windows: Abra o PowerShell como administrador
- Linux/Mac: Use `sudo python app/main.py`

### Scan muito lento ou sem resultados

**Solução**: 
- Reduza o timeout (padrão: 300s)
- Use um tipo de scan mais rápido
- Diminua a faixa de IPs a escanear

### PDF não sendo gerado

**Solução**:
- Verifique permissões de escrita no diretório
- Certifique-se de que `fpdf2` está instalado: `pip install fpdf2`

---

## 🚀 Futuras Implementações

### Em Planejamento para Versões Futuras
- [ ] **Integração com OSINT**: Busque informações sobre IPs alvo
- [ ] **API REST**: Acesso programático às funcionalidades
- [ ] **Autenticação de usuários**: Multi-user support com controle de acesso
- [ ] **Banco de dados persistente**: Armazenamento robusto de histórico com SQLAlchemy
- [ ] **Exportação avançada**: CSV, JSON, XML para integração com outras ferramentas
- [ ] **Agendamento de scans**: Schedule periódico de análises
- [ ] **Comparação de scans**: Visualize mudanças entre análises
- [ ] **Integração com VT/Shodan**: Dados complementares de vulnerabilidades
- [ ] **Suporte a diferentes linguagens**: i18n/l10n
- [ ] **Versão web**: Interface web em paralelo com desktop

---

## 📝 Notas Importantes

### ⚠️ Responsabilidade Legal
- **Use apenas em ambientes onde tem autorização**
- Scanning não autorizado é ilegal em muitas jurisdições
- Sempre obtenha permissão antes de escanear redes terceirizadas
- Este projeto é educacional

### 🔒 Segurança
- O Nmap requer permissões elevadas para certos tipos de scan
- Em Linux/Mac, você pode precisar de `sudo` para scans avançados
- Os dados sensíveis (IPs, portas abertas) são mantidos apenas localmente

---

## 📧 Suporte

Para dúvidas ou problemas, verifique:
1. O Nmap está instalado corretamente
2. As dependências Python estão instaladas (`pip install -r requirements.txt`)
3. Você tem permissões de administrador
4. O alvo está acessível na sua rede

---

## 📄 Licença e Direitos Autorais

### © Copyright & All Rights Reserved

**SENTRA** © 2026. Todos os direitos reservados.

Este projeto, incluindo toda a documentação, código-fonte, arquivos de configuração, ativos visuais e qualquer outro material relacionado, é **propriedade intelectual exclusiva** e está protegido sob as leis de direito autoral internacionais.

### ⚖️ Termos e Restrições

- ✓ **Propriedade**: Este projeto é 100% propriedade do desenvolvedor
- ✓ **Direitos Reservados**: Todos os direitos, deveres e reservas são mantidos
- ✓ **Uso Educacional**: Fornecido como-está para fins de avaliação acadêmica
- ✗ **Reprodução Não Autorizada**: Proibida cópia, modificação ou distribuição sem consentimento explícito
- ✗ **Uso Comercial**: Vedado qualquer uso comercial ou lucrativo sem licença
- ✗ **Revenda**: Proibida a revenda, aluguel ou licenciamento de qualquer parte do projeto

Qualquer violação destes termos resultará em ação legal apropriada.

---

## 👨‍💻 Desenvolvedor

**SENTRA** - Desenvolvido como projeto de segurança de redes

---

## 🙏 Agradecimentos

- [Nmap Project](https://nmap.org) - Ferramenta de scanning de rede
- [PySide6](https://www.qt.io/qt-for-python) - Framework GUI
- [fpdf2](https://py-pdf.github.io/fpdf2/) - Geração de PDFs

---

**Última atualização**: 20 de Abril de 2026

**Versão**: 1.0.0

=======
# Sentra-Sistema-de-Analise-de-Vulnerabilidade-de-Rede
>>>>>>> 05dba6bde8aa434fce5df4066439f81754b017ad
