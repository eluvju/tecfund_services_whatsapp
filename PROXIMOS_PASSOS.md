# 🚀 Próximos Passos - Guia de Deploy

Este documento lista os próximos passos para finalizar e fazer o deploy do sistema no Railway.

## ✅ Checklist de Preparação

### 1. Testes Locais (Recomendado)

Antes de fazer o deploy, teste os scripts localmente para garantir que tudo está funcionando:

```bash
# Teste 1: Contas a Receber
python scripts/dispatch_receivables_today.py

# Teste 2: Contas a Pagar
python scripts/dispatch_payables_today.py

# Teste 3: Compras
python scripts/dispatch_purchases.py
```

**O que verificar:**
- ✅ Conexão com PostgreSQL funcionando
- ✅ Queries retornando dados corretos
- ✅ Mensagens formatadas corretamente
- ✅ WhatsApp enviando mensagens (se configurado)

---

### 2. Commit e Push para o Repositório

Certifique-se de que todas as mudanças estão commitadas:

```bash
# Verificar status
git status

# Adicionar arquivos
git add .

# Fazer commit
git commit -m "feat: Sistema completo de notificações Odoo via WhatsApp com cron jobs"

# Fazer push
git push origin main  # ou master, dependendo da sua branch
```

---

### 3. Configurar Secrets no GitHub (Para Testes Automatizados)

Se ainda não configurou, adicione os secrets no GitHub:

1. Vá em **Settings** → **Secrets and variables** → **Actions**
2. Adicione os secrets conforme [.github/README.md](.github/README.md)

**Secrets necessários:**
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `EVOLUTION_API_URL`
- `EVOLUTION_API_KEY`
- `EVOLUTION_INSTANCE`
- `DISCORD_WEBHOOK_URL`
- `WHATSAPP_NUMBER` (opcional)

---

### 4. Criar Projeto no Railway

1. Acesse [railway.app](https://railway.app)
2. Faça login ou crie uma conta
3. Clique em **New Project**
4. Selecione **Deploy from GitHub repo**
5. Escolha o repositório `tecfund_services`
6. Aguarde o deploy inicial

---

### 5. Configurar Variáveis de Ambiente no Railway

No projeto criado no Railway:

1. Vá em **Variables**
2. Adicione as seguintes variáveis:

```
ODOO_URL=http://62.72.8.92:5432
POSTGRES_HOST=62.72.8.92
POSTGRES_PORT=5432
POSTGRES_DB=odoo
POSTGRES_USER=XYZ
POSTGRES_PASSWORD=XYZ

EVOLUTION_API_KEY=1B68D5DA-A8FA-43E9-8D8A-6F6963AE4B11
EVOLUTION_API_URL=https://api.omnigalaxy.brainesscompany.com.br/manager/instance
EVOLUTION_INSTANCE=brainess

WHATSAPP_NUMBER=5511999999999
```

**⚠️ IMPORTANTE:** Substitua os valores pelos seus dados reais!

---

### 6. Configurar Cron Jobs no Railway

O Railway permite configurar cron jobs de duas formas. Veja o guia completo em [RAILWAY_CRON_SETUP.md](RAILWAY_CRON_SETUP.md).

#### Opção A: Via Interface Web (Recomendado)

1. No projeto Railway, vá em **Settings**
2. Procure por **Cron Jobs** ou **Scheduled Tasks**
3. Clique em **Add Cron Job** ou **New Cron**
4. Configure os 3 cron jobs:

   **Cron Job 1: Contas a Receber**
   - **Name**: `Contas a Receber - 7:30`
   - **Schedule**: `30 10 * * *` (7:30 AM BRT = 10:30 UTC)
   - **Command**: `python scripts/dispatch_receivables_today.py`

   **Cron Job 2: Contas a Pagar**
   - **Name**: `Contas a Pagar - 7:30`
   - **Schedule**: `30 10 * * *` (7:30 AM BRT = 10:30 UTC)
   - **Command**: `python scripts/dispatch_payables_today.py`

   **Cron Job 3: Compras**
   - **Name**: `Compras Atualizadas - 17:30`
   - **Schedule**: `30 20 * * *` (5:30 PM BRT = 8:30 PM UTC)
   - **Command**: `python scripts/dispatch_purchases.py`

#### Opção B: Via arquivo railway.toml

1. Copie o arquivo `railway.toml.example` para `railway.toml`
2. Ajuste os horários se necessário
3. Faça commit e push
4. O Railway detectará automaticamente

**⚠️ Nota sobre horários:** O Railway usa UTC. Se estiver em horário de verão (UTC-2), ajuste:
- 7:30 BRT = 9:30 UTC → `30 9 * * *`
- 17:30 BRT = 19:30 UTC → `30 19 * * *`

---

### 7. Configurar o Serviço Principal (Opcional)

O `main.py` mantém o processo rodando. Se quiser que ele rode como serviço web:

1. Vá em **Settings** → **Service**
2. Certifique-se de que o **Start Command** está como `python main.py`
3. Ou use o `Procfile` (já configurado)

**Nota:** Isso não é necessário para os cron jobs funcionarem, mas pode ser útil para manter o serviço ativo.

---

### 8. Testar o Deploy

#### Teste 1: Verificar Logs

1. No Railway, vá em **Deployments**
2. Clique no último deploy
3. Veja os logs para verificar se não há erros

#### Teste 2: Executar Cron Jobs Manualmente

1. Vá em **Cron Jobs**
2. Para cada cron job, clique em **Run Now** ou **Execute**
3. Verifique os logs de execução
4. Verifique se as mensagens chegaram no WhatsApp

#### Teste 3: Verificar Conexões

Os logs devem mostrar:
- ✅ Conexão com PostgreSQL estabelecida
- ✅ Queries executadas com sucesso
- ✅ Mensagens formatadas
- ✅ WhatsApp enviando mensagens

---

### 9. Monitoramento e Ajustes

#### Monitorar Logs

- Acesse os logs de cada cron job no Railway
- Configure alertas se o Railway oferecer essa opção
- Monitore os logs do GitHub Actions para testes

#### Ajustar Horários

Se precisar mudar os horários dos cron jobs:
- Edite no Railway ou no `railway.toml`
- Faça novo deploy se necessário
- Verifique o fuso horário (UTC vs horário local)

---

## 🐛 Solução de Problemas

### Cron Job Não Executa

- Verifique se o schedule está correto (formato cron)
- Confirme o fuso horário (UTC)
- Verifique os logs do cron job
- Teste o comando manualmente

### Erro de Conexão PostgreSQL

- Verifique as variáveis de ambiente
- Confirme se o IP está acessível do Railway
- Verifique credenciais
- Teste a conexão localmente primeiro

### WhatsApp Não Envia

- Verifique se a instância está ativa na Evolution API
- Confirme a chave de API
- Verifique o formato do número (sem espaços)
- Teste enviar mensagem manualmente via API

### Testes GitHub Actions Falhando

- Verifique se todos os secrets estão configurados
- Veja os logs do workflow
- Teste localmente primeiro
- Verifique as variáveis de ambiente

---

## 📋 Checklist Final

Antes de considerar o deploy completo:

- [ ] Testes locais passando
- [ ] Código commitado e no GitHub
- [ ] Secrets do GitHub configurados
- [ ] Projeto criado no Railway
- [ ] Variáveis de ambiente configuradas
- [ ] Cron jobs configurados (3 jobs)
- [ ] Serviço principal rodando (opcional)
- [ ] Testes manuais dos cron jobs funcionando
- [ ] Mensagens chegando no WhatsApp
- [ ] Logs sendo monitorados

---

## 📞 Próximos Passos Após Deploy

1. **Monitorar por alguns dias** para garantir estabilidade
2. **Ajustar horários** se necessário
3. **Adicionar notificações** quando não houver resultados (opcional)
4. **Documentar** qualquer configuração específica da empresa
5. **Backup** das configurações importantes

---

## 🎉 Pronto!

Depois de completar todos os passos, seu sistema estará rodando automaticamente no Railway, enviando notificações diárias via WhatsApp sobre contas a receber, contas a pagar e compras atualizadas!

Para dúvidas ou problemas, consulte:
- [README.md](README.md) - Documentação principal
- [RAILWAY_CRON_SETUP.md](RAILWAY_CRON_SETUP.md) - Guia de cron jobs
- [.github/README.md](.github/README.md) - Configuração de testes
