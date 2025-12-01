<<<<<<< HEAD
# Sistema de Notificação WhatsApp para Odoo

Sistema automatizado que monitora lançamentos no Odoo e envia notificações via WhatsApp usando a Evolution API.

## 🚀 Funcionalidades

- ✅ Monitoramento automático de lançamentos do Odoo (account.move)
- ✅ Envio de notificações via WhatsApp usando Evolution API
- ✅ Notificações formatadas com informações detalhadas
- ✅ Sistema de persistência para evitar notificações duplicadas
- ✅ Configurado para deploy no Railway
- ✅ Logging completo de todas as operações

## 📋 Pré-requisitos

- Python 3.11+
- Acesso ao servidor Odoo
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
# Configurações do Odoo
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

# Intervalo de verificação em segundos (padrão: 300 = 5 minutos)
POLLING_INTERVAL=300

# Modelo do Odoo para monitorar (padrão: account.move)
ODOO_MODEL=account.move
```

**⚠️ IMPORTANTE:** O arquivo `.env` não deve ser commitado no Git (já está no .gitignore).

## 🏃 Execução Local

### Testar Conexão e Buscar Faturas

Antes de executar o sistema principal, você pode testar a conexão com o Odoo e visualizar as faturas:

```bash
python test_odoo_faturas.py
```

Este script permite:
- Testar conexão com Odoo
- Buscar faturas por diferentes critérios (período, tipo, status)
- Visualizar detalhes das faturas
- Ver resumo estatístico

### Executar Sistema Principal

Execute o sistema de monitoramento:

```bash
python main.py
```

O sistema irá:
1. Conectar ao Odoo
2. Verificar o status da instância WhatsApp
3. Executar uma verificação inicial
4. Monitorar novos lançamentos periodicamente

## 🚂 Deploy no Railway

### 1. Preparação

Certifique-se de que todos os arquivos estão no repositório:
- `main.py`
- `config.py`
- `odoo_client.py`
- `whatsapp_client.py`
- `requirements.txt`
- `Procfile`
- `runtime.txt`

### 2. Deploy no Railway

1. Acesse [Railway.app](https://railway.app)
2. Crie um novo projeto
3. Conecte seu repositório GitHub ou faça deploy via CLI
4. Configure as variáveis de ambiente no painel do Railway (seção "Variables")

**Variáveis de Ambiente Obrigatórias:**
- `ODOO_URL`
- `ODOO_DB`
- `ODOO_USERNAME`
- `ODOO_PASSWORD`
- `EVOLUTION_API_KEY`
- `EVOLUTION_API_URL`
- `EVOLUTION_INSTANCE`
- `WHATSAPP_NUMBER`

**Variáveis Opcionais:**
- `POLLING_INTERVAL` (padrão: 300 segundos)
- `ODOO_MODEL` (padrão: account.move)

### 3. Railway CLI (Alternativa)

```bash
# Instale o Railway CLI
npm i -g @railway/cli

# Login
railway login

# Inicialize o projeto
railway init

# Configure as variáveis de ambiente
railway variables set ODOO_URL="http://62.72.8.92:5432"
railway variables set ODOO_USERNAME="XYZ"
railway variables set ODOO_PASSWORD="XYZ"
# ... adicione todas as outras variáveis

# Faça o deploy
railway up
```

## 📱 Formato das Notificações

As notificações enviadas via WhatsApp seguem este formato:

```
*Novo Lançamento no Odoo*

📋 *Documento:* INV/2024/0001
📅 *Data:* 2024-01-15
💰 *Valor:* R$ 1.500,00
👤 *Parceiro:* Cliente Exemplo
📝 *Tipo:* Fatura de Venda

🔗 ID: 12345
```

## 🔍 Monitoramento

O sistema mantém logs detalhados:
- Logs são salvos em `odoo_whatsapp_notifier.log`
- Também são exibidos no console
- No Railway, os logs podem ser visualizados no painel

### Verificar Status

O sistema verifica automaticamente:
- Conexão com o Odoo na inicialização
- Status da instância WhatsApp antes de enviar mensagens
- Logs de todos os lançamentos processados

## ⚙️ Configurações Avançadas

### Intervalo de Verificação

Ajuste o intervalo de verificação alterando `POLLING_INTERVAL`:
- 60 = 1 minuto
- 300 = 5 minutos (padrão)
- 600 = 10 minutos

### Modelo do Odoo

Por padrão, o sistema monitora `account.move`. Para monitorar outro modelo, ajuste `ODOO_MODEL` no `.env`.

### Persistência

O sistema mantém um arquivo `processed_ids.txt` com os IDs dos lançamentos já notificados, evitando notificações duplicadas mesmo após reinicializações.

## 🐛 Solução de Problemas

### Erro de Conexão com Odoo

- Verifique se a URL do Odoo está correta
- Confirme as credenciais (usuário e senha)
- Verifique se o XML-RPC está habilitado no Odoo
- Teste a conexão manualmente

### Erro ao Enviar WhatsApp

- Verifique se a instância está ativa na Evolution API
- Confirme se a chave de API está correta
- Verifique o formato do número (deve ser: 5511999999999, sem espaços ou caracteres especiais)
- Confirme que a instância está conectada ao WhatsApp

### Notificações Duplicadas

- Verifique se o arquivo `processed_ids.txt` está sendo mantido
- No Railway, certifique-se de que o volume está persistindo

## 📝 Estrutura do Projeto

```
tecfund_services/
├── main.py              # Sistema principal de monitoramento
├── config.py            # Configurações e variáveis de ambiente
├── odoo_client.py       # Cliente para integração com Odoo
├── whatsapp_client.py   # Cliente para Evolution API
├── requirements.txt     # Dependências Python
├── Procfile            # Configuração para Railway
├── runtime.txt         # Versão do Python
├── .env                # Arquivo de configuração (não commitado)
├── .gitignore          # Arquivos ignorados pelo Git
└── README.md           # Esta documentação
```

## 📄 Licença

Este projeto foi desenvolvido para uso interno.

## 👤 Suporte

Para problemas ou dúvidas, verifique os logs do sistema ou entre em contato com a equipe de desenvolvimento.

=======
# tecfund_services_whatsapp
>>>>>>> 694a47d07d6bd7d4d6c05c1bb48beebbf7fed695
