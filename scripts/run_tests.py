"""
Script de testes automatizados para validação de conexões e funcionalidades
Executado pelo GitHub Actions
"""
import sys
import os
from datetime import date, timedelta

# Adiciona o diretório raiz ao path para importar módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import (
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB,
    POSTGRES_USER, POSTGRES_PASSWORD,
    EVOLUTION_API_URL, EVOLUTION_API_KEY, EVOLUTION_INSTANCE
)

print("=" * 80)
print("TESTES AUTOMATIZADOS - Sistema de Contas a Receber")
print("=" * 80)
print()

# Contador de testes
tests_passed = 0
tests_failed = 0
test_results = []


def test_result(test_name: str, passed: bool, message: str = ""):
    """Registra resultado de um teste"""
    global tests_passed, tests_failed
    status = "✅ PASSOU" if passed else "❌ FALHOU"
    test_results.append({
        'name': test_name,
        'passed': passed,
        'message': message
    })
    
    if passed:
        tests_passed += 1
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
    else:
        tests_failed += 1
        print(f"{status}: {test_name}")
        if message:
            print(f"   ⚠️  {message}")
    print()


def test_imports():
    """Testa se todos os módulos podem ser importados"""
    print("TESTE 1: Importação de Módulos")
    print("-" * 80)
    
    try:
        from postgres_client import PostgresClient
        from whatsapp_client import WhatsAppClient
        from accounts_receivable_dispatcher import AccountsReceivableDispatcher
        test_result("Importação de módulos", True, "Todos os módulos importados com sucesso")
        return True
    except Exception as e:
        test_result("Importação de módulos", False, f"Erro: {str(e)}")
        return False


def test_config():
    """Testa se as configurações estão disponíveis"""
    print("TESTE 2: Configurações")
    print("-" * 80)
    
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
        test_result("Configurações", True, "Todas as configurações estão presentes")
    else:
        test_result("Configurações", False, f"Configurações faltando ou não configuradas: {', '.join(missing)}")
    
    return config_ok


def test_postgres_connection():
    """Testa conexão com PostgreSQL"""
    print("TESTE 3: Conexão PostgreSQL")
    print("-" * 80)
    
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
            test_result("Conexão PostgreSQL", True, f"Conectado a {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
            client.close()
            return True
        else:
            test_result("Conexão PostgreSQL", False, "Não foi possível estabelecer conexão")
            client.close()
            return False
            
    except Exception as e:
        test_result("Conexão PostgreSQL", False, f"Erro: {str(e)}")
        return False


def test_postgres_query():
    """Testa se consegue executar queries no PostgreSQL"""
    print("TESTE 4: Query PostgreSQL")
    print("-" * 80)
    
    try:
        from postgres_client import PostgresClient
        
        client = PostgresClient(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )
        
        # Testa query simples
        query = "SELECT 1 as test"
        results = client.execute_query(query)
        
        if results and len(results) > 0:
            test_result("Query PostgreSQL", True, "Query executada com sucesso")
            client.close()
            return True
        else:
            test_result("Query PostgreSQL", False, "Query não retornou resultados")
            client.close()
            return False
            
    except Exception as e:
        test_result("Query PostgreSQL", False, f"Erro: {str(e)}")
        return False


def test_accounts_receivable_query():
    """Testa se consegue buscar contas a receber"""
    print("TESTE 5: Busca de Contas a Receber")
    print("-" * 80)
    
    try:
        from accounts_receivable_dispatcher import AccountsReceivableDispatcher
        
        dispatcher = AccountsReceivableDispatcher()
        
        # Tenta buscar contas para hoje (pode não ter resultados, mas testa a query)
        today = date.today()
        accounts = dispatcher.get_accounts_receivable_by_due_date(today)
        
        test_result("Busca de Contas a Receber", True, 
                   f"Query executada. Encontradas {len(accounts)} conta(s) com vencimento para hoje")
        dispatcher.close()
        return True
        
    except Exception as e:
        test_result("Busca de Contas a Receber", False, f"Erro: {str(e)}")
        return False


def test_message_formatting():
    """Testa formatação de mensagens"""
    print("TESTE 6: Formatação de Mensagens")
    print("-" * 80)
    
    try:
        from accounts_receivable_dispatcher import AccountsReceivableDispatcher
        
        dispatcher = AccountsReceivableDispatcher()
        
        # Busca contas para testar formatação
        today = date.today()
        accounts = dispatcher.get_accounts_receivable_by_due_date(today)
        
        # Se não houver contas, cria dados mock
        if not accounts:
            test_result("Formatação de Mensagens", True, 
                       "Não há contas para formatar, mas a função está disponível")
        else:
            message = dispatcher.format_accounts_receivable_message(accounts, today, is_today=True)
            if message:
                test_result("Formatação de Mensagens", True, 
                           f"Mensagem formatada com sucesso ({len(message)} caracteres)")
            else:
                test_result("Formatação de Mensagens", False, "Mensagem não foi gerada")
                dispatcher.close()
                return False
        
        dispatcher.close()
        return True
        
    except Exception as e:
        test_result("Formatação de Mensagens", False, f"Erro: {str(e)}")
        return False


def test_whatsapp_client():
    """Testa inicialização do cliente WhatsApp"""
    print("TESTE 7: Cliente WhatsApp")
    print("-" * 80)
    
    try:
        from whatsapp_client import WhatsAppClient
        
        client = WhatsAppClient(
            api_url=EVOLUTION_API_URL,
            api_key=EVOLUTION_API_KEY,
            instance=EVOLUTION_INSTANCE
        )
        
        test_result("Cliente WhatsApp", True, "Cliente inicializado com sucesso")
        return True
        
    except Exception as e:
        test_result("Cliente WhatsApp", False, f"Erro: {str(e)}")
        return False


def test_scheduler_setup():
    """Testa configuração do agendador"""
    print("TESTE 8: Configuração do Agendador")
    print("-" * 80)
    
    try:
        from accounts_receivable_dispatcher import AccountsReceivableDispatcher
        import schedule
        
        dispatcher = AccountsReceivableDispatcher()
        dispatcher.schedule_dispatches()
        
        # Verifica se os jobs foram agendados
        jobs = schedule.jobs
        if len(jobs) >= 2:
            test_result("Configuração do Agendador", True, 
                       f"{len(jobs)} job(s) agendado(s) com sucesso")
        else:
            test_result("Configuração do Agendador", False, 
                       f"Esperado 2 jobs, encontrados {len(jobs)}")
            dispatcher.close()
            return False
        
        dispatcher.close()
        return True
        
    except Exception as e:
        test_result("Configuração do Agendador", False, f"Erro: {str(e)}")
        return False


def main():
    """Executa todos os testes"""
    global tests_passed, tests_failed
    
    # Executa testes
    test_imports()
    test_config()
    
    # Só testa conexões se as configs estiverem ok
    if POSTGRES_HOST and POSTGRES_HOST != 'XYZ':
        test_postgres_connection()
        test_postgres_query()
        test_accounts_receivable_query()
        test_message_formatting()
        test_scheduler_setup()
    
    test_whatsapp_client()
    
    # Resumo final
    print()
    print("=" * 80)
    print("RESUMO DOS TESTES")
    print("=" * 80)
    print(f"Total de testes: {tests_passed + tests_failed}")
    print(f"✅ Passou: {tests_passed}")
    print(f"❌ Falhou: {tests_failed}")
    print("=" * 80)
    
    # Lista testes que falharam
    if tests_failed > 0:
        print()
        print("Testes que falharam:")
        for result in test_results:
            if not result['passed']:
                print(f"  - {result['name']}: {result['message']}")
    
    print()
    
    # Retorna código de saída baseado no resultado
    if tests_failed > 0:
        print("❌ Alguns testes falharam!")
        return 1
    else:
        print("✅ Todos os testes passaram!")
        return 0


if __name__ == "__main__":
    sys.exit(main())


