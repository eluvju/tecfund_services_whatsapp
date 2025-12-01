"""
Script de validação completo do módulo de contas a receber
Testa todas as funcionalidades e valida os resultados
"""
import sys
from datetime import date, timedelta, datetime
from accounts_receivable_dispatcher import AccountsReceivableDispatcher
from config import WHATSAPP_NUMBER
import logging

# Configura logging para o teste
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)


def format_valor(valor):
    """Formata valor monetário"""
    if valor:
        return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    return "R$ 0,00"


def test_connection():
    """Testa conexão com PostgreSQL"""
    print("\n" + "=" * 80)
    print("TESTE 1: CONEXÃO COM POSTGRESQL")
    print("=" * 80)
    
    try:
        dispatcher = AccountsReceivableDispatcher()
        
        if dispatcher.postgres_client.test_connection():
            print("✅ Conexão com PostgreSQL: OK")
            return dispatcher, True
        else:
            print("❌ Conexão com PostgreSQL: FALHOU")
            return None, False
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        import traceback
        traceback.print_exc()
        return None, False


def test_query_structure(dispatcher):
    """Testa estrutura da query e campos retornados"""
    print("\n" + "=" * 80)
    print("TESTE 2: ESTRUTURA DA QUERY E CAMPOS")
    print("=" * 80)
    
    try:
        # Busca para uma data qualquer (pode não ter resultados, mas testa a query)
        test_date = date.today()
        accounts = dispatcher.get_accounts_receivable_by_due_date(test_date)
        
        print(f"✅ Query executada com sucesso")
        print(f"   Data testada: {test_date.strftime('%d/%m/%Y')}")
        print(f"   Resultados encontrados: {len(accounts)}")
        
        if accounts:
            print(f"\n   Campos disponíveis no resultado:")
            first_acc = accounts[0]
            for key in sorted(first_acc.keys()):
                value = first_acc[key]
                value_str = str(value)[:50] if value else 'None'
                print(f"   - {key:30s}: {value_str}")
            
            return True
        else:
            print("   ⚠️  Nenhum resultado encontrado para validar campos")
            print("   (Isso é normal se não houver contas com vencimento hoje)")
            return True  # Não é erro, apenas não há dados
            
    except Exception as e:
        print(f"❌ Erro ao executar query: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_search_today(dispatcher):
    """Testa busca de contas com vencimento para hoje"""
    print("\n" + "=" * 80)
    print("TESTE 3: BUSCA DE CONTAS COM VENCIMENTO PARA HOJE")
    print("=" * 80)
    
    try:
        today = date.today()
        accounts = dispatcher.get_accounts_receivable_by_due_date(today)
        
        print(f"📅 Data: {today.strftime('%d/%m/%Y')}")
        print(f"📊 Contas encontradas: {len(accounts)}")
        
        if accounts:
            total = sum(
                (acc.get('amount_residual') or acc.get('debit', 0) or 0)
                for acc in accounts
            )
            
            print(f"💰 Total: {format_valor(total)}")
            print(f"\n   Detalhes das contas:")
            print("   " + "-" * 76)
            
            for idx, acc in enumerate(accounts[:10], 1):  # Mostra até 10
                partner = acc.get('partner_name') or 'Sem cliente'
                move_name = acc.get('move_name') or acc.get('line_name') or 'N/A'
                amount = acc.get('amount_residual') or acc.get('debit', 0) or 0
                due_date = acc.get('date_maturity')
                
                print(f"   {idx:2d}. {partner[:30]:30s} | {move_name[:15]:15s} | {format_valor(amount):>15s}")
            
            if len(accounts) > 10:
                print(f"   ... e mais {len(accounts) - 10} conta(s)")
            
            print("   " + "-" * 76)
            
            return True, accounts
        else:
            print("   ⚠️  Nenhuma conta encontrada com vencimento para hoje")
            print("   (Isso é normal se não houver contas a receber vencendo hoje)")
            return True, []
            
    except Exception as e:
        print(f"❌ Erro ao buscar contas: {e}")
        import traceback
        traceback.print_exc()
        return False, []


def test_search_tomorrow(dispatcher):
    """Testa busca de contas com vencimento para amanhã"""
    print("\n" + "=" * 80)
    print("TESTE 4: BUSCA DE CONTAS COM VENCIMENTO PARA AMANHÃ")
    print("=" * 80)
    
    try:
        tomorrow = date.today() + timedelta(days=1)
        accounts = dispatcher.get_accounts_receivable_by_due_date(tomorrow)
        
        print(f"📅 Data: {tomorrow.strftime('%d/%m/%Y')}")
        print(f"📊 Contas encontradas: {len(accounts)}")
        
        if accounts:
            total = sum(
                (acc.get('amount_residual') or acc.get('debit', 0) or 0)
                for acc in accounts
            )
            
            print(f"💰 Total: {format_valor(total)}")
            print(f"\n   Detalhes das contas:")
            print("   " + "-" * 76)
            
            for idx, acc in enumerate(accounts[:10], 1):  # Mostra até 10
                partner = acc.get('partner_name') or 'Sem cliente'
                move_name = acc.get('move_name') or acc.get('line_name') or 'N/A'
                amount = acc.get('amount_residual') or acc.get('debit', 0) or 0
                
                print(f"   {idx:2d}. {partner[:30]:30s} | {move_name[:15]:15s} | {format_valor(amount):>15s}")
            
            if len(accounts) > 10:
                print(f"   ... e mais {len(accounts) - 10} conta(s)")
            
            print("   " + "-" * 76)
            
            return True, accounts
        else:
            print("   ⚠️  Nenhuma conta encontrada com vencimento para amanhã")
            print("   (Isso é normal se não houver contas a receber vencendo amanhã)")
            return True, []
            
    except Exception as e:
        print(f"❌ Erro ao buscar contas: {e}")
        import traceback
        traceback.print_exc()
        return False, []


def test_message_formatting(dispatcher, accounts_today, accounts_tomorrow):
    """Testa formatação das mensagens"""
    print("\n" + "=" * 80)
    print("TESTE 5: FORMATAÇÃO DE MENSAGENS")
    print("=" * 80)
    
    try:
        # Testa mensagem para hoje
        if accounts_today:
            print("\n📱 Mensagem para HOJE:")
            print("   " + "-" * 76)
            today = date.today()
            message_today = dispatcher.format_accounts_receivable_message(
                accounts_today, today, is_today=True
            )
            
            if message_today:
                for line in message_today.split('\n'):
                    print(f"   {line}")
                print("   " + "-" * 76)
                print(f"   ✅ Mensagem formatada: {len(message_today)} caracteres")
            else:
                print("   ❌ Mensagem não foi gerada")
                return False
        else:
            print("\n📱 Mensagem para HOJE:")
            print("   ⚠️  Nenhuma conta para formatar (normal se não houver contas)")
        
        # Testa mensagem para amanhã
        if accounts_tomorrow:
            print("\n📱 Mensagem para AMANHÃ:")
            print("   " + "-" * 76)
            tomorrow = date.today() + timedelta(days=1)
            message_tomorrow = dispatcher.format_accounts_receivable_message(
                accounts_tomorrow, tomorrow, is_today=False
            )
            
            if message_tomorrow:
                for line in message_tomorrow.split('\n'):
                    print(f"   {line}")
                print("   " + "-" * 76)
                print(f"   ✅ Mensagem formatada: {len(message_tomorrow)} caracteres")
            else:
                print("   ❌ Mensagem não foi gerada")
                return False
        else:
            print("\n📱 Mensagem para AMANHÃ:")
            print("   ⚠️  Nenhuma conta para formatar (normal se não houver contas)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao formatar mensagens: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_whatsapp_connection(dispatcher):
    """Testa conexão com WhatsApp"""
    print("\n" + "=" * 80)
    print("TESTE 6: CONEXÃO COM WHATSAPP")
    print("=" * 80)
    
    try:
        status = dispatcher.whatsapp_client.check_instance_status()
        
        if status:
            print("✅ Instância WhatsApp está ativa e conectada")
        else:
            print("⚠️  Instância WhatsApp não está ativa ou não foi encontrada")
        
        if not WHATSAPP_NUMBER:
            print("⚠️  WHATSAPP_NUMBER não configurado no .env")
            print("   As mensagens não serão enviadas, mas o módulo funcionará")
        else:
            print(f"✅ Número configurado: {WHATSAPP_NUMBER}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar WhatsApp: {e}")
        return False


def test_scheduling():
    """Testa agendamento"""
    print("\n" + "=" * 80)
    print("TESTE 7: CONFIGURAÇÃO DE AGENDAMENTO")
    print("=" * 80)
    
    try:
        dispatcher = AccountsReceivableDispatcher()
        dispatcher.schedule_dispatches()
        
        print("✅ Agendamentos configurados:")
        print("   - 07:00: Contas a receber com vencimento para HOJE")
        print("   - 17:30: Contas a receber com vencimento para AMANHÃ")
        
        dispatcher.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao configurar agendamentos: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Função principal de validação"""
    print("\n" + "🔍 VALIDAÇÃO COMPLETA DO MÓDULO DE CONTAS A RECEBER" + "\n")
    print("=" * 80)
    
    results = []
    
    # Teste 1: Conexão
    dispatcher, conn_ok = test_connection()
    results.append(("Conexão PostgreSQL", conn_ok))
    
    if not conn_ok:
        print("\n❌ Não foi possível continuar sem conexão. Verifique as configurações.")
        return 1
    
    # Teste 2: Estrutura da Query
    query_ok = test_query_structure(dispatcher)
    results.append(("Estrutura da Query", query_ok))
    
    # Teste 3: Busca hoje
    today_ok, accounts_today = test_search_today(dispatcher)
    results.append(("Busca contas hoje", today_ok))
    
    # Teste 4: Busca amanhã
    tomorrow_ok, accounts_tomorrow = test_search_tomorrow(dispatcher)
    results.append(("Busca contas amanhã", tomorrow_ok))
    
    # Teste 5: Formatação
    format_ok = test_message_formatting(dispatcher, accounts_today, accounts_tomorrow)
    results.append(("Formatação de mensagens", format_ok))
    
    # Teste 6: WhatsApp
    whatsapp_ok = test_whatsapp_connection(dispatcher)
    results.append(("Conexão WhatsApp", whatsapp_ok))
    
    # Teste 7: Agendamento
    schedule_ok = test_scheduling()
    results.append(("Configuração agendamento", schedule_ok))
    
    # Fecha conexões
    dispatcher.close()
    
    # Resumo final
    print("\n" + "=" * 80)
    print("RESUMO DA VALIDAÇÃO")
    print("=" * 80)
    
    all_ok = True
    for name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{name:30s}: {status}")
        if not success:
            all_ok = False
    
    print("=" * 80)
    
    if all_ok:
        print("\n✅ Todos os testes passaram! O módulo está pronto para uso.")
        print("\n💡 Próximos passos:")
        print("   1. Configure WHATSAPP_NUMBER no .env para receber notificações")
        print("   2. Integre o módulo ao main.py")
        print("   3. Execute o sistema para disparos automáticos")
        return 0
    else:
        print("\n❌ Alguns testes falharam. Verifique os erros acima.")
        return 1


if __name__ == "__main__":
    sys.exit(main())


