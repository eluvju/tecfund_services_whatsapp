"""
Script de Health Check para Railway
Executa validações do sistema e envia notificações Discord em caso de falha
Executado via cron job diariamente no Railway
"""
import sys
import os
import logging
from datetime import datetime, date
import subprocess

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB,
    POSTGRES_USER, POSTGRES_PASSWORD,
    EVOLUTION_API_URL, EVOLUTION_API_KEY, EVOLUTION_INSTANCE
)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Contador de testes
tests_passed = 0
tests_failed = 0
test_results = []
test_output_lines = []


def log_test_result(test_name: str, passed: bool, message: str = ""):
    """Registra resultado de um teste e adiciona à saída"""
    global tests_passed, tests_failed
    
    status = "✅ PASSOU" if passed else "❌ FALHOU"
    test_results.append({
        'name': test_name,
        'passed': passed,
        'message': message
    })
    
    output_line = f"{status}: {test_name}"
    if message:
        output_line += f"\n   {message}"
    
    test_output_lines.append(output_line)
    
    if passed:
        tests_passed += 1
        logger.info(f"{status}: {test_name}")
        if message:
            logger.info(f"   {message}")
    else:
        tests_failed += 1
        logger.error(f"{status}: {test_name}")
        if message:
            logger.error(f"   ⚠️  {message}")


def test_imports():
    """Testa se todos os módulos podem ser importados"""
    logger.info("TESTE 1: Importação de Módulos")
    
    try:
        from postgres_client import PostgresClient
        from whatsapp_client import WhatsAppClient
        from accounts_receivable_dispatcher import AccountsReceivableDispatcher
        from accounts_payable_dispatcher import AccountsPayableDispatcher
        from purchases_dispatcher import PurchasesDispatcher
        
        log_test_result("Importação de módulos", True, "Todos os módulos importados com sucesso")
        return True
    except Exception as e:
        log_test_result("Importação de módulos", False, f"Erro: {str(e)}")
        return False


def test_config():
    """Testa se as configurações estão disponíveis"""
    logger.info("TESTE 2: Configurações")
    
    config_ok = True
    missing = []
    
    required_configs = [
        ('POSTGRES_HOST', POSTGRES_HOST),
        ('POSTGRES_PORT', POSTGRES_PORT),
        ('POSTGRES_DB', POSTGRES_DB),
        ('POSTGRES_USER', POSTGRES_USER),
        ('POSTGRES_PASSWORD', POSTGRES_PASSWORD),
        ('EVOLUTION_API_URL', EVOLUTION_API_URL),
        ('EVOLUTION_API_KEY', EVOLUTION_API_KEY),
        ('EVOLUTION_INSTANCE', EVOLUTION_INSTANCE),
    ]
    
    for name, value in required_configs:
        if not value or value == 'XYZ':
            missing.append(name)
            config_ok = False
    
    if config_ok:
        log_test_result("Configurações", True, "Todas as configurações estão presentes")
    else:
        log_test_result("Configurações", False, f"Configurações faltando: {', '.join(missing)}")
    
    return config_ok


def test_postgres_connection():
    """Testa conexão com PostgreSQL"""
    logger.info("TESTE 3: Conexão PostgreSQL")
    
    try:
        from postgres_client import PostgresClient
        
        client = PostgresClient(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )
        
        if client.test_connection():
            log_test_result("Conexão PostgreSQL", True, 
                          f"Conectado a {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
            client.close()
            return True
        else:
            log_test_result("Conexão PostgreSQL", False, "Não foi possível estabelecer conexão")
            client.close()
            return False
            
    except Exception as e:
        log_test_result("Conexão PostgreSQL", False, f"Erro: {str(e)}")
        return False


def test_postgres_query():
    """Testa se consegue executar queries no PostgreSQL"""
    logger.info("TESTE 4: Query PostgreSQL")
    
    try:
        from postgres_client import PostgresClient
        
        client = PostgresClient(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )
        
        query = "SELECT 1 as test"
        results = client.execute_query(query)
        
        if results and len(results) > 0:
            log_test_result("Query PostgreSQL", True, "Query executada com sucesso")
            client.close()
            return True
        else:
            log_test_result("Query PostgreSQL", False, "Query não retornou resultados")
            client.close()
            return False
            
    except Exception as e:
        log_test_result("Query PostgreSQL", False, f"Erro: {str(e)}")
        return False


def test_dispatchers_queries():
    """Testa se os dispatchers conseguem buscar dados"""
    logger.info("TESTE 5: Queries dos Dispatchers")
    
    all_passed = True
    
    try:
        # Testa Accounts Receivable
        from accounts_receivable_dispatcher import AccountsReceivableDispatcher
        dispatcher_receivable = AccountsReceivableDispatcher()
        today = date.today()
        accounts = dispatcher_receivable.get_accounts_receivable_by_due_date(today)
        log_test_result("Query Contas a Receber", True, 
                       f"Query executada. Encontradas {len(accounts)} conta(s)")
        dispatcher_receivable.close()
    except Exception as e:
        log_test_result("Query Contas a Receber", False, f"Erro: {str(e)}")
        all_passed = False
    
    try:
        # Testa Accounts Payable
        from accounts_payable_dispatcher import AccountsPayableDispatcher
        dispatcher_payable = AccountsPayableDispatcher()
        accounts = dispatcher_payable.get_accounts_payable_for_today()
        log_test_result("Query Contas a Pagar", True, 
                       f"Query executada. Encontradas {len(accounts)} conta(s)")
        dispatcher_payable.close()
    except Exception as e:
        log_test_result("Query Contas a Pagar", False, f"Erro: {str(e)}")
        all_passed = False
    
    try:
        # Testa Purchases
        from purchases_dispatcher import PurchasesDispatcher
        dispatcher_purchases = PurchasesDispatcher()
        purchases = dispatcher_purchases.get_purchases_updated_today()
        log_test_result("Query Compras", True, 
                       f"Query executada. Encontradas {len(purchases)} compra(s)")
        dispatcher_purchases.close()
    except Exception as e:
        log_test_result("Query Compras", False, f"Erro: {str(e)}")
        all_passed = False
    
    return all_passed


def test_whatsapp_client():
    """Testa inicialização do cliente WhatsApp"""
    logger.info("TESTE 6: Cliente WhatsApp")
    
    try:
        from whatsapp_client import WhatsAppClient
        
        client = WhatsAppClient(
            api_url=EVOLUTION_API_URL,
            api_key=EVOLUTION_API_KEY,
            instance=EVOLUTION_INSTANCE
        )
        
        # Testa se consegue verificar o status da instância
        status = client.check_instance_status()
        if status:
            log_test_result("Cliente WhatsApp", True, "Cliente inicializado e instância verificada")
        else:
            log_test_result("Cliente WhatsApp", False, "Instância não está ativa ou acessível")
            return False
        
        return True
        
    except Exception as e:
        log_test_result("Cliente WhatsApp", False, f"Erro: {str(e)}")
        return False


def send_discord_notification_on_failure():
    """Envia notificação Discord em caso de falha"""
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    
    if not webhook_url:
        logger.warning("DISCORD_WEBHOOK_URL não configurado. Notificação Discord não será enviada.")
        return False
    
    try:
        import requests
        from datetime import datetime
        
        # Formata saída dos testes
        test_output = "\n".join(test_output_lines)
        
        # Limita tamanho (Discord tem limite)
        max_length = 1500
        if len(test_output) > max_length:
            test_output = test_output[:max_length] + f"\n... (truncado)"
        
        # Cria embed
        failed_tests = [r for r in test_results if not r['passed']]
        failed_list = "\n".join([f"• {r['name']}: {r['message']}" for r in failed_tests[:10]])
        if len(failed_tests) > 10:
            failed_list += f"\n... e mais {len(failed_tests) - 10} teste(s)"
        
        embed = {
            "title": "⚠️ Health Check Falhou - Sistema Odoo",
            "description": f"O health check diário detectou falhas no sistema.",
            "color": 15158332,  # Vermelho
            "fields": [
                {
                    "name": "📊 Resumo",
                    "value": f"✅ Passou: {tests_passed}\n❌ Falhou: {tests_failed}\n📝 Total: {tests_passed + tests_failed}",
                    "inline": True
                },
                {
                    "name": "🔍 Testes que Falharam",
                    "value": f"```\n{failed_list}\n```" if failed_list else "Nenhum teste falhou",
                    "inline": False
                },
                {
                    "name": "📋 Saída Completa",
                    "value": f"```\n{test_output}\n```",
                    "inline": False
                }
            ],
            "footer": {
                "text": "Railway Health Check - Sistema Odoo",
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        payload = {
            "content": "@everyone",
            "embeds": [embed],
            "username": "Railway Health Check"
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info("✅ Notificação Discord enviada com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao enviar notificação Discord: {e}")
        return False


def main():
    """Função principal"""
    logger.info("=" * 80)
    logger.info("HEALTH CHECK - Sistema de Notificações Odoo")
    logger.info("=" * 80)
    logger.info(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    
    # Executa testes
    test_imports()
    test_config()
    
    # Só testa conexões se as configs estiverem ok
    if POSTGRES_HOST and POSTGRES_HOST != 'XYZ':
        test_postgres_connection()
        test_postgres_query()
        test_dispatchers_queries()
    
    test_whatsapp_client()
    
    # Resumo final
    logger.info("")
    logger.info("=" * 80)
    logger.info("RESUMO DO HEALTH CHECK")
    logger.info("=" * 80)
    logger.info(f"Total de testes: {tests_passed + tests_failed}")
    logger.info(f"✅ Passou: {tests_passed}")
    logger.info(f"❌ Falhou: {tests_failed}")
    logger.info("=" * 80)
    
    # Lista testes que falharam
    if tests_failed > 0:
        logger.error("")
        logger.error("Testes que falharam:")
        for result in test_results:
            if not result['passed']:
                logger.error(f"  - {result['name']}: {result['message']}")
        
        # Envia notificação Discord em caso de falha
        logger.info("")
        logger.info("Enviando notificação Discord...")
        send_discord_notification_on_failure()
        
        logger.error("")
        logger.error("❌ Health check falhou! Alguns testes não passaram.")
        return 1
    else:
        logger.info("")
        logger.info("✅ Health check passou! Todos os testes estão OK.")
        return 0


if __name__ == "__main__":
    sys.exit(main())

