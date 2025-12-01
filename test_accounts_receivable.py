"""
Script de teste para o módulo de contas a receber
Testa busca e formatação de mensagens
"""
from datetime import date, timedelta
from accounts_receivable_dispatcher import AccountsReceivableDispatcher
import logging

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def main():
    """Função principal de teste"""
    print("\n" + "=" * 80)
    print("TESTE DO MÓDULO DE CONTAS A RECEBER")
    print("=" * 80)
    
    try:
        dispatcher = AccountsReceivableDispatcher()
        
        # Testa busca para hoje
        print("\n📋 Testando busca de contas a receber para HOJE...")
        today = date.today()
        accounts_today = dispatcher.get_accounts_receivable_by_due_date(today)
        print(f"✅ Encontradas {len(accounts_today)} conta(s) com vencimento para hoje")
        
        if accounts_today:
            print("\n   Detalhes:")
            for acc in accounts_today[:5]:
                partner = acc.get('partner_name', 'N/A')
                amount = acc.get('amount_residual') or acc.get('debit', 0)
                move_name = acc.get('move_name', acc.get('line_name', 'N/A'))
                print(f"   - {partner} | {move_name} | R$ {amount:,.2f}")
        
        # Testa busca para amanhã
        print("\n📋 Testando busca de contas a receber para AMANHÃ...")
        tomorrow = date.today() + timedelta(days=1)
        accounts_tomorrow = dispatcher.get_accounts_receivable_by_due_date(tomorrow)
        print(f"✅ Encontradas {len(accounts_tomorrow)} conta(s) com vencimento para amanhã")
        
        if accounts_tomorrow:
            print("\n   Detalhes:")
            for acc in accounts_tomorrow[:5]:
                partner = acc.get('partner_name', 'N/A')
                amount = acc.get('amount_residual') or acc.get('debit', 0)
                move_name = acc.get('move_name', acc.get('line_name', 'N/A'))
                print(f"   - {partner} | {move_name} | R$ {amount:,.2f}")
        
        # Testa formatação de mensagem
        if accounts_today:
            print("\n📱 Testando formatação de mensagem (HOJE)...")
            message = dispatcher.format_accounts_receivable_message(accounts_today, today, is_today=True)
            if message:
                print("\n   Mensagem formatada:")
                print("   " + "-" * 76)
                for line in message.split('\n'):
                    print(f"   {line}")
                print("   " + "-" * 76)
        
        if accounts_tomorrow:
            print("\n📱 Testando formatação de mensagem (AMANHÃ)...")
            message = dispatcher.format_accounts_receivable_message(accounts_tomorrow, tomorrow, is_today=False)
            if message:
                print("\n   Mensagem formatada:")
                print("   " + "-" * 76)
                for line in message.split('\n'):
                    print(f"   {line}")
                print("   " + "-" * 76)
        
        dispatcher.close()
        print("\n✅ Teste concluído com sucesso!")
        print("\n💡 Para testar o envio real, configure WHATSAPP_NUMBER no .env")
        
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

