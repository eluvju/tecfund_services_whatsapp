# Guia de Deploy no Railway

Este guia fornece instruções passo a passo para fazer deploy do sistema de notificação WhatsApp Odoo no Railway.

## 📋 Pré-requisitos

1. Conta no [Railway](https://railway.app)
2. Repositório Git (GitHub, GitLab, etc.) ou acesso ao Railway CLI
3. Todas as credenciais necessárias (Odoo, Evolution API)

## 🚀 Método 1: Deploy via GitHub (Recomendado)

### Passo 1: Preparar o Repositório

1. Certifique-se de que todos os arquivos estão no repositório:
   - `main.py`
   - `config.py`
   - `odoo_client.py`
   - `whatsapp_client.py`
   - `requirements.txt`
   - `Procfile`
   - `runtime.txt`
   - `README.md`

2. Faça commit e push para o GitHub:
```bash
git add .
git commit -m "Sistema de notificação WhatsApp Odoo"
git push origin main
```

### Passo 2: Conectar ao Railway

1. Acesse [Railway Dashboard](https://railway.app/dashboard)
2. Clique em "New Project"
3. Selecione "Deploy from GitHub repo"
4. Autorize o Railway a acessar seus repositórios
5. Selecione o repositório `tecfund_services`
6. Railway detectará automaticamente que é um projeto Python

### Passo 3: Configurar Variáveis de Ambiente

1. No projeto Railway, vá em "Variables"
2. Adicione as seguintes variáveis de ambiente:

**Variáveis Obrigatórias:**

```
ODOO_URL=http://62.72.8.92:5432
ODOO_DB=odoo
ODOO_USERNAME=XYZ
ODOO_PASSWORD=XYZ
EVOLUTION_API_KEY=1B68D5DA-A8FA-43E9-8D8A-6F6963AE4B11
EVOLUTION_API_URL=https://api.omnigalaxy.brainesscompany.com.br/manager/instance
EVOLUTION_INSTANCE=brainess
WHATSAPP_NUMBER=5511999999999
```

**Variáveis Opcionais:**

```
POLLING_INTERVAL=300
ODOO_MODEL=account.move
```

**⚠️ IMPORTANTE:** Substitua os valores pelos seus dados reais!

### Passo 4: Deploy

1. Railway iniciará o deploy automaticamente
2. Acompanhe os logs em tempo real na aba "Deployments"
3. Aguarde a conclusão do deploy

### Passo 5: Verificar

1. Verifique os logs em "View Logs"
2. Você deve ver mensagens como:
   - "Sistema de Notificação WhatsApp Odoo iniciado"
   - "Conectado ao Odoo com sucesso"
   - "Instância WhatsApp está ativa"

## 🚀 Método 2: Deploy via CLI

### Passo 1: Instalar Railway CLI

```bash
npm i -g @railway/cli
```

### Passo 2: Login

```bash
railway login
```

### Passo 3: Inicializar Projeto

```bash
cd tecfund_services
railway init
```

### Passo 4: Configurar Variáveis de Ambiente

```bash
railway variables set ODOO_URL="http://62.72.8.92:5432"
railway variables set ODOO_DB="odoo"
railway variables set ODOO_USERNAME="XYZ"
railway variables set ODOO_PASSWORD="XYZ"
railway variables set EVOLUTION_API_KEY="1B68D5DA-A8FA-43E9-8D8A-6F6963AE4B11"
railway variables set EVOLUTION_API_URL="https://api.omnigalaxy.brainesscompany.com.br/manager/instance"
railway variables set EVOLUTION_INSTANCE="brainess"
railway variables set WHATSAPP_NUMBER="5511999999999"
railway variables set POLLING_INTERVAL="300"
```

### Passo 5: Deploy

```bash
railway up
```

## 📊 Monitoramento

### Ver Logs

No dashboard do Railway:
1. Vá para o projeto
2. Clique em "View Logs"
3. Os logs são atualizados em tempo real

Via CLI:
```bash
railway logs
```

### Status do Serviço

O Railway mostra automaticamente:
- Status do serviço (Running/Stopped)
- Uso de recursos (CPU, Memória)
- Tráfego de rede

## ⚙️ Configurações Avançadas

### Configurar Recursos

No Railway, você pode configurar:
- **Memory**: Memória disponível (mínimo recomendado: 512MB)
- **CPU**: Limite de CPU
- **Scaling**: Auto-scaling (não necessário para este projeto)

### Variáveis de Ambiente Secretas

Para proteger credenciais:
1. Use variáveis de ambiente no Railway (não commite no código)
2. Railway criptografa automaticamente variáveis sensíveis
3. Nunca compartilhe suas credenciais

### Persistência de Dados

O arquivo `processed_ids.txt` é criado automaticamente. No Railway:
- Dados são mantidos entre reinicializações
- Se usar volumes, configure um volume persistente para garantir que os IDs não sejam perdidos

### Configurar Domínio Personalizado

1. No projeto Railway, vá em "Settings"
2. Clique em "Generate Domain" ou configure um domínio customizado
3. O sistema não precisa de domínio público (é um worker), mas você pode configurar se necessário

## 🔧 Troubleshooting

### Erro: "No module named 'xxx'"

- Verifique se todas as dependências estão no `requirements.txt`
- Railway instala automaticamente ao fazer deploy

### Erro: "Connection refused"

- Verifique se as URLs estão corretas
- Verifique se os serviços externos (Odoo, Evolution API) estão acessíveis
- Verifique firewall e permissões

### O sistema não está enviando notificações

1. Verifique os logs: `railway logs`
2. Verifique se `WHATSAPP_NUMBER` está configurado
3. Verifique se a instância Evolution está ativa
4. Verifique se há novos lançamentos no Odoo

### Service não inicia

1. Verifique o `Procfile` - deve conter: `web: python main.py`
2. Verifique se `runtime.txt` especifica uma versão válida do Python
3. Verifique os logs para mensagens de erro específicas

## 💰 Custos

Railway oferece:
- **Plano Hobby**: $5/mês com créditos incluídos
- **Uso**: Este sistema usa poucos recursos, adequado para o plano Hobby

## 📚 Recursos Adicionais

- [Documentação Railway](https://docs.railway.app)
- [Railway Discord](https://discord.gg/railway)
- [Pricing Railway](https://railway.app/pricing)

## ✅ Checklist de Deploy

- [ ] Repositório configurado no GitHub
- [ ] Todos os arquivos commitados
- [ ] Projeto criado no Railway
- [ ] Repositório conectado
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy concluído com sucesso
- [ ] Logs mostram sistema funcionando
- [ ] Teste de notificação realizado


