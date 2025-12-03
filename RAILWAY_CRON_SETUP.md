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

### ⚠️ Importante: Múltiplos Cron Jobs

O Railway permite apenas **1 cron job** via interface web. Para configurar múltiplos cron jobs, você **deve usar** o arquivo `railway.toml`.

### Método Recomendado: Via Arquivo `railway.toml`

O arquivo `railway.toml` já foi criado na raiz do projeto com os 3 cron jobs configurados. Após fazer commit e push, o Railway detectará automaticamente e criará os cron jobs.

**O arquivo `railway.toml` contém:**

```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "python main.py"

# Cron Jobs - Horários em UTC
# 7:30 AM horário de Brasília (UTC-3) = 10:30 UTC
# 5:30 PM horário de Brasília (UTC-3) = 8:30 PM UTC

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

**Passos:**
1. Faça commit e push do arquivo `railway.toml`
2. O Railway fará um novo deploy automaticamente
3. Os 3 cron jobs serão criados automaticamente
4. Verifique em **Settings** → **Cron Jobs** (ou na seção de cron jobs do projeto)

### Método Alternativo: Via Interface Web (Apenas 1 Cron Job)

**⚠️ Limitação:** O Railway permite apenas **1 cron job** via interface web.

Se precisar configurar apenas 1 cron job temporariamente:

1. Acesse seu projeto no Railway
2. Vá em **Settings** → **Cron Jobs** (ou **Scheduled Tasks**)
3. Clique em **Add Cron Job**
4. Configure o cron job:

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

