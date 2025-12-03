# Sistema de Notificações Odoo via WhatsApp

Sistema automatizado que dispara notificações via WhatsApp sobre contas a receber, contas a pagar e compras do Odoo usando a Evolution API. As tarefas são executadas via cron jobs do Railway.

## 🚀 Funcionalidades

- ✅ **Contas a Receber**: Disparo automático de contas com vencimento para hoje (07:30)
- ✅ **Contas a Pagar**: Resumo de contas com vencimento para hoje, agrupado por empresa (07:30)
- ✅ **Compras**: Resumo de compras atualizadas no dia com status (17:30)
- ✅ Integração direta com PostgreSQL do Odoo
- ✅ Notificações formatadas com informações detalhadas
- ✅ Configurado para deploy no Railway com cron jobs
- ✅ Logging completo de todas as operações
- ✅ Health Check diário com testes automatizados no Railway
- ✅ Notificações Discord em caso de falha

## 📋 Pré-requisitos

- Python 3.11+
- Acesso ao banco PostgreSQL do Odoo
- Conta na Evolution API com instância configurada
- Número de WhatsApp para receber notificações
- Conta no Railway para hospedagem e cron jobs

## 🔧 Instalação

1. Clone o repositório ou baixe os arquivos

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Crie um arquivo `.env` na raiz do projeto com suas configurações:

```env
# Configurações PostgreSQL/Odoo
ODOO_URL=http://62.72.8.92:5432
ODOO_DB=odoo
ODOO_USERNAME=seu_usuario
ODOO_PASSWORD=sua_senha

# Configurações da Evolution API
EVOLUTION_API_KEY=sua_chave_api
EVOLUTION_API_URL=https://api.omnigalaxy.brainesscompany.com.br/manager/instance
EVOLUTION_INSTANCE=nome_da_instancia

# Número do WhatsApp para receber notificações (formato: 5511999999999)
WHATSAPP_NUMBER=5511999999999
```

**⚠️ IMPORTANTE:** O arquivo `.env` não deve ser commitado no Git (já está no .gitignore).

## 🏃 Execução Local

### Testar Scripts Individualmente

Você pode testar cada script separadamente:

```bash
# Contas a receber (vencimento hoje)
python scripts/dispatch_receivables_today.py

# Contas a pagar (vencimento hoje)
python scripts/dispatch_payables_today.py

# Compras atualizadas no dia
python scripts/dispatch_purchases.py
```

### Executar Serviço Principal

O `main.py` mantém o processo rodando (útil para o Railway):

```bash
python main.py
```

## 🚂 Deploy no Railway

### Configuração Básica

1. Acesse [Railway.app](https://railway.app)
2. Crie um novo projeto e conecte seu repositório
3. Configure as variáveis de ambiente no painel do Railway

**Variáveis de Ambiente Obrigatórias:**
- `ODOO_URL` - URL do PostgreSQL (ex: http://62.72.8.92:5432)
- `ODOO_DB` ou `POSTGRES_DB` - Nome do banco de dados
- `ODOO_USERNAME` ou `POSTGRES_USER` - Usuário do banco
- `ODOO_PASSWORD` ou `POSTGRES_PASSWORD` - Senha do banco
- `EVOLUTION_API_KEY` - Chave da API Evolution
- `EVOLUTION_API_URL` - URL da API Evolution
- `EVOLUTION_INSTANCE` - Nome da instância
- `WHATSAPP_NUMBER` - Número para receber notificações

### Configuração de Cron Jobs

O Railway usa cron jobs para executar tarefas agendadas. Veja detalhes completos em [RAILWAY_CRON_SETUP.md](RAILWAY_CRON_SETUP.md).

**Resumo rápido:**

1. Acesse **Settings** → **Cron Jobs** no Railway
2. Configure 3 cron jobs:

   **Cron Job 1: Contas a Receber**
   - **Schedule**: `30 10 * * *` (7:30 AM horário de Brasília = 10:30 UTC)
   - **Command**: `python scripts/dispatch_receivables_today.py`

   **Cron Job 2: Contas a Pagar**
   - **Schedule**: `30 10 * * *` (7:30 AM horário de Brasília = 10:30 UTC)
   - **Command**: `python scripts/dispatch_payables_today.py`

   **Cron Job 3: Compras**
   - **Schedule**: `30 20 * * *` (5:30 PM horário de Brasília = 8:30 PM UTC)
   - **Command**: `python scripts/dispatch_purchases.py`

**⚠️ Importante:** Os horários estão em UTC. Ajuste conforme o fuso horário do Railway.

### Arquivo railway.toml (Opcional)

Você pode criar um arquivo `railway.toml` na raiz do projeto. Veja exemplo em `railway.toml.example`.

## 📱 Formato das Notificações

### Contas a Receber

```
📋 *Contas a Receber - Vencimento HOJE*
📅 Data: 15/01/2024
💰 Total: R$ 5.000,00
📊 Quantidade: 3 conta(s)

*Detalhes:*
──────────────────────────────
1. *Cliente Exemplo*
   Doc: INV/2024/0001
   Valor: R$ 2.000,00

2. *Outro Cliente*
   Doc: INV/2024/0002
   Valor: R$ 3.000,00

──────────────────────────────
⚠️ Total a receber hoje: R$ 5.000,00
```

### Contas a Pagar

```
💰 *Contas a Pagar - Hoje*
📅 03/12/2024
📊 15 conta(s) | 3 empresa(s)
💵 Total: R$ 25.000,00

*Resumo por Empresa:*
• *Empresa A*: R$ 15.000,00 (8 contas)
• *Empresa B*: R$ 7.500,00 (5 contas)
• *Empresa C*: R$ 2.500,00 (2 contas)

⚠️ Total: R$ 25.000,00
```

### Compras Atualizadas

```
🛒 *Compras Atualizadas - Hoje*
📅 Data: 03/12/2024
📊 Total de compras: 5
💰 Valor total: R$ 10.500,00

*✅ Aprovado: 3 compra(s)*
──────────────────────────────
1. *P04303*
   Fornecedor: LOJA DO EPI
   Data: 26/11/2024
   Valor: R$ 626,35

...
```

## ⏰ Horários dos Disparos

- **07:30** (horário de Brasília): 
  - Contas a receber com vencimento para HOJE
  - Contas a pagar com vencimento para HOJE
- **17:30** (horário de Brasília): 
  - Compras atualizadas no dia

## 🔍 Monitoramento e Testes

O sistema utiliza o Railway para testes e monitoramento, garantindo que os testes sejam executados no mesmo ambiente de produção.

### Health Check Diário

Um cron job executa diariamente às **6:00 AM** (horário de Brasília) para validar todo o sistema:

- ✅ Importação de todos os módulos
- ✅ Configurações de variáveis de ambiente
- ✅ Conexão com PostgreSQL
- ✅ Execução de queries PostgreSQL
- ✅ Queries dos dispatchers (Contas a Receber, Contas a Pagar, Compras)
- ✅ Cliente WhatsApp e status da instância

### Logs e Monitoramento

- **Logs detalhados** de todas as execuções
- **Visualização em tempo real** no dashboard do Railway
- **Status de sucesso/falha** de cada cron job
- **Notificações Discord** em caso de falha no Health Check

### Notificações Discord

Em caso de falha no Health Check, uma notificação é enviada automaticamente para o Discord com:
- 📊 Resumo dos testes (passou/falhou)
- 🔍 Lista de testes que falharam
- 📋 Saída completa dos testes
- ⏰ Timestamp da execução

**Configuração:** Adicione a variável `DISCORD_WEBHOOK_URL` no Railway.

### Visualizar Logs

1. Acesse seu projeto no Railway
2. Vá em **Deployments** ou clique no serviço
3. Veja os logs em tempo real
4. Para logs de cron jobs, vá em **Cron Jobs** ou **Scheduled Tasks**

### Testar Manualmente

Você pode executar o Health Check manualmente:

```bash
python scripts/health_check.py
```

Ou no Railway: vá em **Cron Jobs** → **Health Check** → **Run Now**

**📚 Veja o guia completo em:** [MONITORAMENTO_RAILWAY.md](MONITORAMENTO_RAILWAY.md)

## 🐛 Solução de Problemas

### Erro de Conexão com PostgreSQL

- Verifique se o host e porta estão corretos
- Confirme as credenciais (usuário e senha)
- Verifique se o firewall permite conexões
- Teste a conexão manualmente

### Erro ao Enviar WhatsApp

- Verifique se a instância está ativa na Evolution API
- Confirme se a chave de API está correta
- Verifique o formato do número (deve ser: 5511999999999, sem espaços)
- Confirme que a instância está conectada ao WhatsApp

### Cron Jobs Não Executando

- Verifique os logs do cron job no Railway
- Confirme que o horário está correto (lembre-se do fuso UTC)
- Verifique se o comando está correto
- Teste o script localmente primeiro

## 📝 Estrutura do Projeto

```
tecfund_services/
├── main.py                          # Serviço principal (mantém processo ativo)
├── config.py                        # Configurações e variáveis de ambiente
├── postgres_client.py               # Cliente PostgreSQL
├── whatsapp_client.py               # Cliente Evolution API
├── accounts_receivable_dispatcher.py # Módulo de disparo de contas a receber
├── accounts_payable_dispatcher.py   # Módulo de disparo de contas a pagar
├── purchases_dispatcher.py          # Módulo de disparo de compras
├── scripts/                         # Scripts executáveis e utilitários
│   ├── dispatch_receivables_today.py # Script para cron: contas a receber
│   ├── dispatch_payables_today.py    # Script para cron: contas a pagar
│   ├── dispatch_purchases.py         # Script para cron: compras
│   ├── run_tests.py                  # Script de testes automatizados
│   └── send_discord_notification.py  # Script de notificação Discord
├── .github/
│   ├── workflows/
│   │   └── test.yml                  # Workflow do GitHub Actions
│   └── README.md                     # Documentação dos testes
├── requirements.txt                  # Dependências Python
├── Procfile                          # Configuração para Railway
├── runtime.txt                       # Versão do Python
├── railway.toml.example              # Exemplo de configuração Railway
├── RAILWAY_CRON_SETUP.md            # Guia de configuração dos cron jobs
├── .env                             # Arquivo de configuração (não commitado)
├── .gitignore                       # Arquivos ignorados pelo Git
└── README.md                        # Esta documentação
```

## 📄 Licença

Este projeto foi desenvolvido para uso interno.
