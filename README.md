# Extrator de Dados - Investidor10

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Selenium](https://img.shields.io/badge/Selenium-4.33.0-yellow.svg)](https://selenium-python.readthedocs.io/)
[![Release](https://img.shields.io/github/v/release/andrelanzieri/scraping_investidor10?color=brightgreen)](https://github.com/andrelanzieri/scraping_investidor10/releases)

> Ferramenta automatizada para extrair dados de ações do site Investidor10 com interface gráfica moderna e arquitetura modular.

**📥 Download do Executável:**
<https://github.com/andrelanzieri/scraping_investidor10/releases>

## 📋 Índice

- [✨ Características](#-características)
- [📸 Screenshots](#-screenshots)
- [🏗️ Versão 2.0 - Arquitetura Modular](#️-versão-20---arquitetura-modular)
- [📦 Instalação](#-instalação)
- [🚀 Uso](#-uso)
- [⚙️ Configuração](#️-configuração)
- [🔧 Características Técnicas](#-características-técnicas)
- [⚠️ Observações Importantes](#️-observações-importantes)
- [❓ FAQ - Perguntas Frequentes](#-faq---perguntas-frequentes)
- [🔧 Solução de Problemas](#-solução-de-problemas)
- [🤝 Contribuição](#-contribuição)
- [☕ Apoie o Projeto](#-apoie-o-projeto)
- [📄 Licença](#-licença)
- [🙏 Agradecimentos](#-agradecimentos)

## ✨ Características

- 🔄 **Extração Automatizada**: Coleta dados de ações individuais e carteiras recomendadas
- 🎨 **Interface Moderna**: GUI com temas claro/escuro e design responsivo
- ⚙️ **Configurações Flexíveis**: Colunas personalizadas e configurações persistentes
- 📊 **Exportação Excel**: Relatórios formatados com dados estruturados (xlsxwriter)
- 🚫 **Sistema de Cancelamento**: Interrupção segura de extrações em andamento
- 🔧 **Arquitetura Modular**: Código organizado e de fácil manutenção
- 🛡️ **Extração Robusta**: Sistema de múltiplas tentativas e tratamento de erros
- 📦 **Executável Standalone**: Todas as dependências incluídas (~52MB)
- ⚡ **Performance Otimizada**: Extração de ~10-15 ações por minuto
- 🔒 **Seguro e Confiável**: Sem coleta de dados pessoais ou senhas

## 📸 Screenshots

### Interface Principal

![Tela Inicial](screenshots/telainicial.png)

![Interface Principal](screenshots/interface_principal.png)

*Interface principal da aplicação com tema escuro, mostrando a lista de ações configuradas e botões de ação.*

### Configuração de Ações

![Configuração de Ações](screenshots/configuracao_acoes.png)

*Tela de configuração onde você pode adicionar/remover ações e personalizar colunas de dados.*

### Resultado Excel

![Resultado Excel](screenshots/resultado_excel.png)

*Exemplo de arquivo Excel gerado com dados formatados e organizados.*

## 🏗️ Versão 2.0 - Arquitetura Modular

A aplicação foi completamente refatorada para uma arquitetura modular com separação clara de responsabilidades:

### 📁 Estrutura do Projeto

```
├── main.py                 # 🚀 Arquivo principal para inicialização
├── interface_app.py        # 🖥️ Classe InvestidorApp (Interface gráfica)
├── data_extractor.py       # 🔍 Classe DataExtractor (Extração de dados)
├── config.json            # ⚙️ Configurações persistentes
├── requirements.txt       # 📦 Dependências do projeto
├── run.bat               # 🪟 Script de inicialização (Windows)
├── build_executable.py   # 🔨 Script para gerar executável
├── build_executable.bat  # 🪟 Script auxiliar para build
└── README.md             # 📖 Documentação
```

### 🔧 Classes Principais

#### 🖥️ InvestidorApp (`interface_app.py`)

**Responsabilidades:**

- Gerenciamento da interface gráfica Tkinter
- Controle de temas (claro/escuro)
- Configurações de ações e colunas personalizadas
- Coordenação com o extrator de dados
- Sistema de atalhos de teclado (Ctrl+S, Ctrl+E, etc.)

#### 🔍 DataExtractor (`data_extractor.py`)

**Responsabilidades:**

- Configuração automática do WebDriver Chrome
- Extração de dados de ações individuais
- Extração de dados de carteiras recomendadas
- Processamento de seletores CSS complexos
- Exportação para Excel com formatação profissional

## 📦 Instalação

### Pré-requisitos

- 🐍 **Python 3.8 ou superior** (recomendado Python 3.9+)
- 🌐 **Google Chrome** ou Chromium instalado
- 🔗 **Conexão estável com a internet**
- 💾 **~500MB de espaço livre** (para dependências e dados)

### Passos de Instalação

1. **Clone o repositório**:

   ```bash
   git clone https://github.com/andrelanzieri/scraping_investidor10.git
   cd scraping_investidor10
   ```

2. **Crie um ambiente virtual (recomendado)**:

   ```bash
   python -m venv .venv

   # Windows
   .venv\Scripts\activate

   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Instale as dependências**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Verifique a instalação**:

   ```bash
   python main.py
   ```

### 📋 Dependências

| Pacote | Versão | Descrição |
|--------|--------|-----------|
| `selenium` | 4.33.0 | Automação do navegador web |
| `pandas` | 2.2.3 | Manipulação e análise de dados |
| `openpyxl` | 3.1.5 | Leitura/escrita de arquivos Excel |
| `xlsxwriter` | ≥3.0.0 | Engine para escrita de Excel com formatação |
| `webdriver-manager` | 4.0.2 | Gerenciamento automático do ChromeDriver |
| `requests` | ≥2.31.0 | Requisições HTTP (dependência adicional) |
| `lxml` | ≥4.9.0 | Parser XML/HTML mais rápido para pandas |
| `Pillow` | ≥10.0.0 | Processamento de imagens (capturas de tela) |

## 🚀 Uso

### Inicialização

**Método 1 - Python**:

```bash
python main.py
```

**Método 2 - Script Windows**:

```bash
run.bat
```

### 📝 Fluxo de Trabalho

1. **📈 Configuração de Ações**
   - Adicione os tickers das ações (ex: PETR4, VALE3, ITUB4)
   - Use o formato padrão da B3

2. **📊 Colunas Personalizadas**
   - Configure os dados específicos a extrair
   - Exemplos: P/L, ROE, Dividend Yield, etc.

3. **💾 Salvamento**
   - Use `Ctrl+S` ou clique em "Salvar Configurações"
   - Configurações são salvas em `config.json`

4. **🔍 Extração**
   - Use `Ctrl+E` ou clique em "Extrair Dados"
   - **Para extração de carteiras**: Desative a opção "Headless" para fazer login manual
   - Acompanhe o progresso na barra de status
   - Aguarde a conclusão do processo

### 📊 Tipos de Extração

#### 🏢 Dados de Ações Individuais

```
URL: https://investidor10.com.br/acoes/[TICKER]/
Dados: Indicadores fundamentalistas personalizáveis
Formato: Uma linha por ação no Excel
```

#### 🎯 Carteiras Recomendadas

```
URL: https://investidor10.com.br/carteiras/resumo/
Dados: Ticker, nome, preço, variação, setor
Formato: Tabela completa no Excel
```

## ⚙️ Configuração

### 📄 Arquivo config.json

Exemplo de configuração:

```json
{
  "acoes": ["PETR4", "VALE3", "ITUB4"],
  "colunas_personalizadas": [
    {
      "nome": "P/L",
      "seletor": ".indicator[data-name='pl'] .value"
    },
    {
      "nome": "ROE",
      "seletor": ".indicator[data-name='roe'] .value"
    }
  ],
  "tema": "claro"
}
```

### 🎨 Personalização de Interface

- **Temas**: Alterne entre claro e escuro
- **Atalhos**: `Ctrl+S` (Salvar), `Ctrl+E` (Extrair)
- **Configurações**: Persistem entre sessões

## 🔧 Características Técnicas

### 🏗️ Arquitetura Modular

| Característica | Benefício |
|---------------|-----------|
| **Separação de Responsabilidades** | Interface e extração independentes |
| **Baixo Acoplamento** | Fácil manutenção e extensão |
| **Alta Coesão** | Cada módulo tem propósito específico |

### 🚀 Recursos Avançados

- **🔒 Thread Safety**: Atualizações seguras da interface
- **⏹️ Sistema de Cancelamento**: Interrupção limpa de processos
- **💾 Configurações Persistentes**: Estado mantido entre execuções
- **🛡️ Tratamento de Erros**: Recuperação graceful de falhas
- **📊 Progress Tracking**: Acompanhamento em tempo real

### 🌐 WebDriver

- **🔄 Configuração Automática**: ChromeDriver baixado automaticamente via webdriver-manager
- **💾 Perfil Persistente**: Mantém login e configurações entre sessões
- **👻 Modo Headless**: Execução em background disponível (desative para login manual)
- **🛡️ Tratamento de Falhas**: Recuperação automática em caso de erros

## ⚠️ Observações Importantes

| ⚠️ Avisos | 📋 Descrição |
|----------|-------------|
| **Login Necessário** | Faça login no Investidor10 quando solicitado |
| **Dependência de Internet** | Requer conexão estável |
| **Conformidade Legal** | Respeite os termos de uso do site |
| **Backup Regular** | Faça backup do `config.json` |

## ❓ FAQ - Perguntas Frequentes

### 🤔 Questões Gerais

**Q: O aplicativo é gratuito?**
A: Sim, completamente gratuito e open source.

**Q: Preciso de conta no Investidor10?**
A: Para dados básicos de ações, não. Para carteiras personalizadas, sim.

**Q: Quantas ações posso extrair por vez?**
A: Não há limite técnico, mas recomenda-se até 50 ações por extração.

**Q: Os dados são atualizados em tempo real?**
A: Os dados são do site Investidor10, atualizados conforme disponibilidade deles.

**Q: Posso usar em Linux/Mac?**
A: Sim, desde que tenha Python e Chrome instalados.

### 🛠️ Questões Técnicas

**Q: Por que o Chrome abre durante a extração?**
A: É necessário para navegar no site. Use modo headless para execução em background.

**Q: Como adicionar novos indicadores?**
A: Configure na seção "Colunas Personalizadas" com seletores CSS apropriados.

**Q: O app funciona offline?**
A: Não, é necessária conexão com internet para acessar o site.

## 🔧 Solução de Problemas

### ❌ Problemas Comuns

| Problema | Solução |
|----------|---------|
| **Chrome não encontrado** | Instale o Google Chrome ou Chromium |
| **Erro de conexão** | Verifique sua conexão com a internet |
| **Dados não carregam** | Aguarde o login completo no site |
| **Selenium TimeoutException** | Aumente o tempo limite nas configurações |
| **Arquivo config.json corrompido** | Delete o arquivo para resetar configurações |

### 🐛 Debug e Logs

- **Interface**: Mensagens de status na barra inferior
- **Pop-ups**: Erros detalhados em janelas de diálogo
- **Terminal**: Execute `python main.py` para logs completos
- **Arquivo de Log**: Considere implementar logging para arquivos

### 🆘 Comandos de Diagnóstico

```bash
# Verificar versão do Python
python --version

# Verificar dependências instaladas
pip list

# Testar importações essenciais
python -c "import selenium, pandas, openpyxl, xlsxwriter; print('✅ Todas as dependências OK')"

# Verificar versão do Chrome
# Windows
chrome --version
"C:\Program Files\Google\Chrome\Application\chrome.exe" --version

# Linux
google-chrome --version

# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version

# Testar WebDriver
python -c "from selenium import webdriver; from webdriver_manager.chrome import ChromeDriverManager; print('✅ WebDriver OK')"
```

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. 🍴 Faça um fork do projeto
2. 🌟 Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push para a branch (`git push origin feature/AmazingFeature`)
5. 🔄 Abra um Pull Request

### 💡 Ideias para Contribuição

- 📈 **Novos indicadores financeiros**: P/VP, EBIT, ROIC, etc.
- 🎨 **Melhorias na interface**: Novos temas, layouts responsivos
- 🔧 **Otimizações de performance**: Paralelização, cache inteligente
- 📊 **Novos formatos de exportação**: CSV, JSON, PDF
- 🧪 **Testes automatizados**: Unit tests, integration tests
- 🌐 **Suporte a outros sites**: Fundamentus, Status Invest
- 📱 **Interface mobile**: App móvel ou PWA
- 🔔 **Sistema de alertas**: Notificações por email/push

## ☕ Apoie o Projeto

Se este projeto foi útil para você e você gostaria de apoiar o desenvolvimento contínuo, considere me comprar um café! ☕

![Buy Me A Coffee](screenshots/coffee.png)

Seu apoio ajuda a:

- 🚀 Manter o projeto atualizado
- 🐛 Corrigir bugs rapidamente
- ✨ Adicionar novas funcionalidades
- 📚 Melhorar a documentação
- 🔧 Manter a compatibilidade com novas versões

**Outras formas de apoiar:**

- ⭐ Dê uma estrela no projeto
- 🐛 Reporte bugs e problemas
- 💡 Sugira melhorias
- 🤝 Contribua com código
- 📢 Compartilhe com outros desenvolvedores

## 📄 Licença

Este projeto está licenciado sob a **Licença MIT** - veja o arquivo [LICENSE](LICENSE) para detalhes.

**Resumo da Licença:**

- ✅ Uso comercial permitido
- ✅ Modificação permitida
- ✅ Distribuição permitida
- ✅ Uso privado permitido
- ❌ Nenhuma garantia fornecida
- ❌ Autor não é responsável por danos

## 🙏 Agradecimentos

- 🌐 [**Investidor10**](https://investidor10.com.br/) - Fonte dos dados fundamentalistas
- 🤖 [**Selenium**](https://selenium-python.readthedocs.io/) - Automação web robusta
- 📊 [**Pandas**](https://pandas.pydata.org/) - Manipulação e análise de dados
- 📈 [**XlsxWriter**](https://xlsxwriter.readthedocs.io/) - Geração de Excel formatado
- 🔧 [**WebDriver Manager**](https://github.com/SergeyPirogov/webdriver_manager) - Gerenciamento automático de drivers
- 🐍 **Comunidade Python** - Suporte e bibliotecas excepcionais
- 💡 **Contribuidores** - Todos que reportaram bugs e sugeriram melhorias

**Tecnologias e Ferramentas:**

- 🖥️ **Tkinter** - Interface gráfica nativa
- 🎨 **ttkthemes** - Temas modernos para interface
- 🔄 **Threading** - Processamento assíncrono
- 📁 **JSON** - Armazenamento de configurações
