# Sistema de Notificação de Contas a Receber via WhatsApp

Sistema automatizado que dispara notificações via WhatsApp sobre contas a receber com vencimento próximo usando a Evolution API.

## 🚀 Funcionalidades

- ✅ Disparo automático de contas a receber com vencimento para hoje (07:00)
- ✅ Disparo automático de contas a receber com vencimento para amanhã (17:30)
- ✅ Notificações formatadas com informações detalhadas
- ✅ Integração direta com PostgreSQL do Odoo
- ✅ Configurado para deploy no Railway
- ✅ Logging completo de todas as operações
- ✅ Testes automatizados via GitHub Actions
- ✅ Notificações Discord em caso de falha dos testes

## 📋 Pré-requisitos

- Python 3.11+
- Acesso ao banco PostgreSQL do Odoo
- Conta na Evolution API com instância configurada
- Número de WhatsApp para receber notificações

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

Execute o sistema:

```bash
python main.py
```

O sistema irá:
1. Conectar ao PostgreSQL do Odoo
2. Verificar o status da instância WhatsApp
3. Agendar os disparos automáticos:
   - 07:00: Contas a receber com vencimento para HOJE
   - 17:30: Contas a receber com vencimento para AMANHÃ

## 🚂 Deploy no Railway

### Configuração

1. Acesse [Railway.app](https://railway.app)
2. Crie um novo projeto e conecte seu repositório
3. Configure as variáveis de ambiente no painel do Railway

**Variáveis de Ambiente Obrigatórias:**
- `ODOO_URL` - URL do PostgreSQL (ex: http://62.72.8.92:5432)
- `ODOO_DB` - Nome do banco de dados
- `ODOO_USERNAME` - Usuário do banco
- `ODOO_PASSWORD` - Senha do banco
- `EVOLUTION_API_KEY` - Chave da API Evolution
- `EVOLUTION_API_URL` - URL da API Evolution
- `EVOLUTION_INSTANCE` - Nome da instância
- `WHATSAPP_NUMBER` - Número para receber notificações

O Railway detectará automaticamente que é um projeto Python e fará o deploy.

## 📱 Formato das Notificações

As notificações enviadas via WhatsApp seguem este formato:

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

## ⏰ Horários dos Disparos

- **07:00**: Envia notificação de contas a receber com vencimento para HOJE
- **17:30**: Envia notificação de contas a receber com vencimento para AMANHÃ

## 🔍 Monitoramento

O sistema mantém logs detalhados:
- Logs são salvos em `accounts_receivable_notifier.log`
- Também são exibidos no console
- No Railway, os logs podem ser visualizados no painel

## 🧪 Testes Automatizados

O projeto inclui testes automatizados executados via GitHub Actions:

### Execução Automática

Os testes são executados automaticamente:
- ✅ A cada push para `main`, `master` ou `develop`
- ✅ A cada pull request para essas branches
- ✅ Diariamente às 6h UTC (3h BRT)
- ✅ Manualmente via **Actions** > **Testes Automatizados** > **Run workflow**

### Testes Executados

1. Importação de módulos
2. Validação de configurações
3. Conexão PostgreSQL
4. Execução de queries PostgreSQL
5. Busca de contas a receber
6. Formatação de mensagens
7. Cliente WhatsApp
8. Configuração do agendador

### Notificações Discord

Em caso de falha dos testes, uma notificação é enviada automaticamente para o Discord com:
- 📋 Hash do commit
- 👤 Autor e data do commit
- 💬 Mensagem do commit
- 📊 Resumo completo dos testes e erros

**Webhook Discord:** Configurado para enviar notificações com `@everyone` em caso de falha.

### Configuração dos Secrets

Para que os testes funcionem, configure os seguintes secrets no GitHub:

1. Vá em **Settings** > **Secrets and variables** > **Actions**
2. Adicione os secrets necessários (veja detalhes em [.github/README.md](.github/README.md))

**Secrets Obrigatórios:**
- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `EVOLUTION_API_URL`, `EVOLUTION_API_KEY`, `EVOLUTION_INSTANCE`
- `DISCORD_WEBHOOK_URL` - URL do webhook Discord
- `WHATSAPP_NUMBER` (opcional)

### Visualizar Resultados

1. Vá em **Actions** no repositório GitHub
2. Clique no workflow **Testes Automatizados**
3. Veja os logs detalhados de cada teste
4. Baixe os artefatos com os resultados completos

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

## 📝 Estrutura do Projeto

```
tecfund_services/
├── main.py                          # Sistema principal
├── config.py                        # Configurações e variáveis de ambiente
├── postgres_client.py               # Cliente PostgreSQL
├── whatsapp_client.py               # Cliente Evolution API
├── accounts_receivable_dispatcher.py # Módulo de disparo de contas a receber
├── scripts/                         # Scripts de teste e utilitários
│   ├── run_tests.py                # Script de testes automatizados
│   └── send_discord_notification.py # Script de notificação Discord
├── .github/
│   ├── workflows/
│   │   └── test.yml                # Workflow do GitHub Actions
│   └── README.md                   # Documentação dos testes
├── requirements.txt                 # Dependências Python
├── Procfile                        # Configuração para Railway
├── runtime.txt                     # Versão do Python
├── .env                            # Arquivo de configuração (não commitado)
├── .gitignore                      # Arquivos ignorados pelo Git
└── README.md                       # Esta documentação
```

## 📄 Licença

Este projeto foi desenvolvido para uso interno.
