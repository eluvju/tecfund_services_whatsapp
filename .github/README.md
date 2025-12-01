# Configuração do GitHub Actions

## Secrets Necessários

Para que os testes automatizados funcionem, você precisa configurar os seguintes secrets no repositório GitHub:

### Configuração dos Secrets

1. Vá em **Settings** > **Secrets and variables** > **Actions**
2. Clique em **New repository secret**
3. Adicione os seguintes secrets:

#### Secrets Obrigatórios:

| Secret | Descrição | Exemplo |
|--------|-----------|---------|
| `POSTGRES_HOST` | Host do servidor PostgreSQL | `62.72.8.92` |
| `POSTGRES_PORT` | Porta do PostgreSQL | `5432` |
| `POSTGRES_DB` | Nome do banco de dados | `odoo` |
| `POSTGRES_USER` | Usuário do banco | `usuario` |
| `POSTGRES_PASSWORD` | Senha do banco | `senha123` |
| `EVOLUTION_API_URL` | URL da API Evolution | `https://api.omnigalaxy.brainesscompany.com.br/manager/instance` |
| `EVOLUTION_API_KEY` | Chave da API | `1B68D5DA-A8FA-43E9-8D8A-6F6963AE4B11` |
| `EVOLUTION_INSTANCE` | Nome da instância | `brainess` |
| `DISCORD_WEBHOOK_URL` | URL do webhook Discord | `https://discord.com/api/webhooks/1445099446370041887/SG7HrdeEVpzEnvzGLYRym3T9lTStDd1T-rYOwTa-hF79HkBhjHFRc-ObOhayThl6FrMX` |
| `WHATSAPP_NUMBER` | Número WhatsApp (opcional) | `5511999999999` |

### Como Obter o Webhook do Discord

1. Abra o Discord e vá até o servidor/canal onde deseja receber as notificações
2. Vá em **Configurações do Canal** > **Integrações** > **Webhooks**
3. Clique em **Novo Webhook**
4. Dê um nome ao webhook (ex: "GitHub Actions")
5. Copie a **URL do Webhook**
6. Cole a URL no secret `DISCORD_WEBHOOK_URL`

### Quando os Testes são Executados

Os testes são executados automaticamente:
- ✅ A cada push para `main`, `master` ou `develop`
- ✅ A cada pull request para essas branches
- ✅ Diariamente às 6h UTC (3h BRT)
- ✅ Manualmente via **Actions** > **Testes Automatizados** > **Run workflow**

### Resultados dos Testes

- ✅ **Sucesso**: Os testes passaram e nenhuma notificação é enviada
- ❌ **Falha**: Os testes falharam e uma notificação é enviada para o Discord com `@everyone` incluindo:
  - Informações do commit (hash, autor, data, mensagem)
  - Resumo completo dos testes
  - Detalhes dos erros

### Testes Executados

1. Importação de módulos
2. Validação de configurações
3. Conexão PostgreSQL
4. Execução de queries PostgreSQL
5. Busca de contas a receber
6. Formatação de mensagens
7. Cliente WhatsApp
8. Configuração do agendador

### Visualizar Resultados

1. Vá em **Actions** no repositório GitHub
2. Clique no workflow **Testes Automatizados**
3. Veja os logs detalhados de cada teste

