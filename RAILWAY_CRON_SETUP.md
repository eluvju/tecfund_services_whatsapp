# Configuração de Cron Jobs no Railway

Este projeto usa cron jobs do Railway para executar tarefas agendadas. Cada script é executado em um horário específico.

## Scripts Disponíveis

1. **Contas a Receber (Hoje)** - `scripts/dispatch_receivables_today.py`
   - Horário: 07:30 (horário de Brasília - UTC-3)
   - Cron: `30 10 * * *` (UTC) ou `30 7 * * *` (se configurado para horário local)

2. **Contas a Pagar (Hoje)** - `scripts/dispatch_payables_today.py`
   - Horário: 07:30 (horário de Brasília - UTC-3)
   - Cron: `30 10 * * *` (UTC) ou `30 7 * * *` (se configurado para horário local)

3. **Compras Atualizadas** - `scripts/dispatch_purchases.py`
   - Horário: 17:30 (horário de Brasília - UTC-3)
   - Cron: `30 20 * * *` (UTC) ou `30 17 * * *` (se configurado para horário local)

## Como Configurar no Railway

### Opção 1: Via Interface Web do Railway (Recomendado)

1. Acesse seu projeto no Railway
2. Vá em **Settings** → **Cron Jobs** (ou **Scheduled Tasks**)
3. Clique em **Add Cron Job**
4. Configure cada cron job:

   **Cron Job 1: Contas a Receber**
   - **Name**: `Contas a Receber - 7:30`
   - **Schedule**: `30 10 * * *` (7:30 AM horário de Brasília = 10:30 UTC)
   - **Command**: `python scripts/dispatch_receivables_today.py`
   
   **Cron Job 2: Contas a Pagar**
   - **Name**: `Contas a Pagar - 7:30`
   - **Schedule**: `30 10 * * *` (7:30 AM horário de Brasília = 10:30 UTC)
   - **Command**: `python scripts/dispatch_payables_today.py`
   
   **Cron Job 3: Compras**
   - **Name**: `Compras Atualizadas - 17:30`
   - **Schedule**: `30 20 * * *` (5:30 PM horário de Brasília = 8:30 PM UTC)
   - **Command**: `python scripts/dispatch_purchases.py`

### Opção 2: Via Arquivo `railway.toml`

Crie um arquivo `railway.toml` na raiz do projeto:

```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "python main.py"

[[cron]]
schedule = "30 10 * * *"
command = "python scripts/dispatch_receivables_today.py"

[[cron]]
schedule = "30 10 * * *"
command = "python scripts/dispatch_payables_today.py"

[[cron]]
schedule = "30 20 * * *"
command = "python scripts/dispatch_purchases.py"
```

## Importante: Horário UTC vs Horário de Brasília

O Railway usa UTC por padrão. Para horário de Brasília (UTC-3):

- **7:30 AM (Brasília)** = **10:30 UTC** → Cron: `30 10 * * *`
- **5:30 PM (Brasília)** = **8:30 PM UTC** → Cron: `30 20 * * *`

### Durante Horário de Verão (UTC-2)

Se houver horário de verão, ajuste para UTC-2:

- **7:30 AM (Brasília)** = **9:30 UTC** → Cron: `30 9 * * *`
- **5:30 PM (Brasília)** = **7:30 PM UTC** → Cron: `30 19 * * *`

## Variáveis de Ambiente

Certifique-se de que todas as variáveis de ambiente necessárias estão configuradas no Railway:

- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `EVOLUTION_API_KEY`
- `EVOLUTION_API_URL`
- `EVOLUTION_INSTANCE`
- `WHATSAPP_NUMBER`

## Testando Localmente

Para testar os scripts localmente antes de configurar no Railway:

```bash
# Contas a receber
python scripts/dispatch_receivables_today.py

# Contas a pagar
python scripts/dispatch_payables_today.py

# Compras
python scripts/dispatch_purchases.py
```

## Logs

Os logs de cada execução dos cron jobs aparecerão no dashboard do Railway em **Logs** ou **Cron Jobs** → **Logs** do job específico.

