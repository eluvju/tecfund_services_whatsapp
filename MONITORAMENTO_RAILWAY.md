# 🔍 Monitoramento e Testes no Railway

## 📊 Visão Geral

O sistema agora utiliza o Railway para testes e monitoramento, garantindo que os testes sejam executados no mesmo ambiente de produção onde o sistema realmente roda.

## 🎯 Estratégia de Monitoramento

### 1. Health Check Diário

Um cron job executa diariamente às **6:00 AM** (horário de Brasília) para validar todo o sistema antes dos outros jobs começarem.

**O que o Health Check valida:**
- ✅ Importação de todos os módulos
- ✅ Configurações de variáveis de ambiente
- ✅ Conexão com PostgreSQL
- ✅ Execução de queries PostgreSQL
- ✅ Queries dos dispatchers (Contas a Receber, Contas a Pagar, Compras)
- ✅ Cliente WhatsApp e status da instância

### 2. Monitoramento dos Cron Jobs

Todos os cron jobs geram logs que podem ser visualizados no Railway:
- Logs de sucesso/falha de cada execução
- Tempo de execução
- Detalhes de erros (se houver)

### 3. Notificações Discord

Em caso de falha no Health Check, uma notificação é enviada automaticamente para o Discord com:
- 📊 Resumo dos testes (passou/falhou)
- 🔍 Lista de testes que falharam
- 📋 Saída completa dos testes
- ⏰ Timestamp da execução

## 🚀 Como Funciona

### Health Check Cron Job

O cron job está configurado no `railway.toml`:

```toml
[[cron]]
schedule = "0 9 * * *"  # 6:00 AM horário de Brasília = 9:00 UTC
command = "python scripts/health_check.py"
```

### Horários dos Cron Jobs

Todos os cron jobs estão configurados em UTC:

| Job | Horário BRT | Horário UTC | Schedule |
|-----|-------------|-------------|----------|
| Health Check | 6:00 AM | 9:00 AM | `0 9 * * *` |
| Contas a Receber | 7:30 AM | 10:30 AM | `30 10 * * *` |
| Contas a Pagar | 7:30 AM | 10:30 AM | `30 10 * * *` |
| Compras | 5:30 PM | 8:30 PM | `30 20 * * *` |

**⚠️ Importante:** Durante horário de verão (UTC-2), ajuste os horários:
- 6:00 AM BRT = 8:00 UTC → `0 8 * * *`
- 7:30 AM BRT = 9:30 UTC → `30 9 * * *`
- 5:30 PM BRT = 7:30 PM UTC → `30 19 * * *`

## 📋 Configuração

### Variáveis de Ambiente Necessárias

Certifique-se de que todas estas variáveis estão configuradas no Railway:

**PostgreSQL:**
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`

**Evolution API:**
- `EVOLUTION_API_URL`
- `EVOLUTION_API_KEY`
- `EVOLUTION_INSTANCE`

**Notificações:**
- `DISCORD_WEBHOOK_URL` - Para notificações de falha no Health Check
- `WHATSAPP_NUMBER` - Para envio de mensagens

## 🔍 Como Verificar Logs

### No Railway Dashboard:

1. Acesse seu projeto no Railway
2. Vá em **Deployments** ou clique no serviço
3. Veja os logs em tempo real
4. Para logs de cron jobs específicos, vá em **Cron Jobs** ou **Scheduled Tasks**

### Logs do Health Check:

O Health Check gera logs detalhados mostrando:
- Cada teste executado
- Resultado (passou/falhou)
- Mensagens de erro (se houver)
- Resumo final

**Exemplo de saída:**
```
========================================
HEALTH CHECK - Sistema de Notificações Odoo
========================================
✅ PASSOU: Importação de módulos
✅ PASSOU: Configurações
✅ PASSOU: Conexão PostgreSQL
...
========================================
RESUMO DO HEALTH CHECK
========================================
Total de testes: 7
✅ Passou: 7
❌ Falhou: 0
========================================
✅ Health check passou! Todos os testes estão OK.
```

## 🔔 Notificações Discord

### Configuração

1. No Railway, adicione a variável de ambiente:
   - **Key**: `DISCORD_WEBHOOK_URL`
   - **Value**: URL do webhook do Discord

2. O Health Check enviará automaticamente uma notificação se algum teste falhar

### Formato da Notificação

Quando o Health Check falha, você recebe no Discord:
- **Título**: ⚠️ Health Check Falhou - Sistema Odoo
- **Resumo**: Quantidade de testes que passaram/falharam
- **Lista de Falhas**: Testes que falharam com detalhes
- **Saída Completa**: Logs completos do Health Check
- **Menciona**: `@everyone` para alertar imediatamente

## 🧪 Testar Manualmente

Você pode executar o Health Check manualmente:

1. No Railway, vá em **Cron Jobs**
2. Encontre o job "Health Check"
3. Clique em **Run Now** ou **Execute**
4. Veja os logs em tempo real

Ou localmente:
```bash
python scripts/health_check.py
```

## 📊 Monitoramento Contínuo

### Recomendações:

1. **Verifique os logs diariamente** (ou configure alertas)
2. **Monitore após deploys** para garantir que tudo está funcionando
3. **Acompanhe as notificações Discord** para falhas críticas
4. **Revise métricas** do Railway (CPU, memória, etc.)

### Alertas do Railway (Se Disponível):

O Railway pode enviar alertas nativos para:
- Falha de deploy
- Serviço offline
- Alto uso de recursos
- Cron jobs que falharam

Configure esses alertas nas configurações do projeto no Railway.

## 🆚 Vantagens vs GitHub Actions

### ✅ Vantagens de usar Railway:

- **Mesmo ambiente**: Testa onde o sistema realmente roda
- **Mesmas variáveis**: Usa as mesmas configs de produção
- **Menos duplicação**: Não precisa configurar secrets duas vezes
- **Logs integrados**: Tudo em um só lugar
- **Monitoramento real**: Vê o que realmente acontece
- **Custo eficiente**: Não consome minutos do GitHub Actions

### ⚠️ Quando usar GitHub Actions:

GitHub Actions ainda pode ser útil para:
- Validação de código (linter, formatação)
- Testes unitários básicos (sem conexões externas)
- CI/CD de pull requests

Mas testes de integração devem ser no Railway.

## 🔧 Solução de Problemas

### Health Check Falhando

1. **Verifique os logs** do Health Check no Railway
2. **Confirme variáveis de ambiente** estão corretas
3. **Teste conexões manualmente**:
   - PostgreSQL acessível?
   - Evolution API respondendo?
4. **Verifique notificações Discord** para detalhes

### Notificações Discord Não Funcionam

1. Confirme que `DISCORD_WEBHOOK_URL` está configurado
2. Teste o webhook manualmente
3. Verifique os logs do Health Check para erros

### Cron Jobs Não Executando

1. Verifique o schedule no `railway.toml`
2. Confirme o fuso horário (UTC)
3. Veja logs de erro no Railway
4. Teste o comando manualmente

## 📝 Checklist de Configuração

- [ ] Variáveis de ambiente configuradas no Railway
- [ ] `DISCORD_WEBHOOK_URL` configurado
- [ ] Health Check adicionado ao `railway.toml`
- [ ] Cron jobs configurados corretamente
- [ ] Testado Health Check manualmente
- [ ] Verificado que notificações Discord funcionam
- [ ] Logs sendo monitorados

---

## 🎯 Próximos Passos

1. **Monitore por alguns dias** para garantir estabilidade
2. **Configure alertas** no Railway (se disponível)
3. **Ajuste horários** se necessário
4. **Documente** qualquer configuração específica

---

**Dúvidas?** Consulte:
- [README.md](README.md) - Documentação principal
- [RAILWAY_CRON_SETUP.md](RAILWAY_CRON_SETUP.md) - Configuração de cron jobs
- [PROXIMOS_PASSOS.md](PROXIMOS_PASSOS.md) - Guia de deploy

