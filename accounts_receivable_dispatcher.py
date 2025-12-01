"""
Módulo de disparo de contas a receber por WhatsApp
Dispara notificações de contas a receber com vencimento próximo
"""
import logging
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional
import schedule
import time

from config import (
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB,
    POSTGRES_USER, POSTGRES_PASSWORD,
    EVOLUTION_API_URL, EVOLUTION_API_KEY, EVOLUTION_INSTANCE,
    WHATSAPP_NUMBER
)
from postgres_client import PostgresClient
from whatsapp_client import WhatsAppClient

logger = logging.getLogger(__name__)


class AccountsReceivableDispatcher:
    """Sistema de disparo de contas a receber"""
    
    def __init__(self):
        """Inicializa o dispatcher"""
        self.postgres_client = PostgresClient(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )
        self.whatsapp_client = WhatsAppClient(
            api_url=EVOLUTION_API_URL,
            api_key=EVOLUTION_API_KEY,
            instance=EVOLUTION_INSTANCE
        )
    
    def get_accounts_receivable_by_due_date(self, due_date: date) -> List[Dict]:
        """
        Busca contas a receber com vencimento em uma data específica
        
        Args:
            due_date: Data de vencimento para buscar
            
        Returns:
            Lista de contas a receber
        """
        query = """
            SELECT 
                aml.id,
                aml.move_id,
                aml.partner_id,
                rp.name as partner_name,
                aml.date_maturity,
                aml.date,
                aml.name as line_name,
                aml.debit,
                aml.credit,
                aml.amount_residual,
                aml.amount_residual_currency,
                am.name as move_name,
                am.move_type,
                am.state as move_state,
                am.ref as move_ref,
                am.invoice_date
            FROM account_move_line aml
            INNER JOIN account_move am ON aml.move_id = am.id
            LEFT JOIN res_partner rp ON aml.partner_id = rp.id
            INNER JOIN account_account aa ON aml.account_id = aa.id
            WHERE aa.account_type = 'asset_receivable'
              AND aml.date_maturity = %s
              AND am.state = 'posted'
              AND aml.reconciled = false
              AND aml.debit > 0
            ORDER BY aml.date_maturity, rp.name, aml.name
        """
        
        try:
            results = self.postgres_client.execute_query(query, (due_date,))
            return results
        except Exception as e:
            logger.error(f"Erro ao buscar contas a receber para vencimento {due_date}: {e}")
            return []
    
    def format_accounts_receivable_message(self, accounts: List[Dict], due_date: date, is_today: bool = True) -> str:
        """
        Formata mensagem de contas a receber
        
        Args:
            accounts: Lista de contas a receber
            due_date: Data de vencimento
            is_today: Se True, vencimento é hoje; se False, é amanhã
            
        Returns:
            Mensagem formatada
        """
        if not accounts:
            return None
        
        data_text = "hoje" if is_today else "amanhã"
        data_formatada = due_date.strftime('%d/%m/%Y')
        
        # Calcula total
        total = sum(
            (acc.get('amount_residual') or acc.get('debit', 0)) 
            for acc in accounts
        )
        
        # Formata valor
        total_str = f"R$ {total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        # Monta mensagem
        message = f"📋 *Contas a Receber - Vencimento {data_text.upper()}*\n"
        message += f"📅 Data: {data_formatada}\n"
        message += f"💰 Total: {total_str}\n"
        message += f"📊 Quantidade: {len(accounts)} conta(s)\n\n"
        
        message += "*Detalhes:*\n"
        message += "─" * 30 + "\n"
        
        for idx, acc in enumerate(accounts, 1):
            partner = acc.get('partner_name', 'N/A')
            move_name = acc.get('move_name', acc.get('line_name', 'N/A'))
            amount = acc.get('amount_residual') or acc.get('debit', 0)
            amount_str = f"R$ {amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            
            # Referência se houver
            ref = acc.get('move_ref', '')
            ref_text = f" ({ref})" if ref else ""
            
            message += f"{idx}. *{partner}*\n"
            message += f"   Doc: {move_name}{ref_text}\n"
            message += f"   Valor: {amount_str}\n\n"
        
        message += "─" * 30 + "\n"
        message += f"⚠️ Total a receber {data_text}: {total_str}"
        
        return message
    
    def send_accounts_receivable_notification(self, due_date: date, is_today: bool = True) -> bool:
        """
        Busca e envia notificação de contas a receber
        
        Args:
            due_date: Data de vencimento
            is_today: Se True, vencimento é hoje; se False, é amanhã
            
        Returns:
            True se enviou com sucesso, False caso contrário
        """
        try:
            logger.info(f"Buscando contas a receber com vencimento em {due_date}")
            
            # Busca contas
            accounts = self.get_accounts_receivable_by_due_date(due_date)
            
            if not accounts:
                logger.info(f"Nenhuma conta a receber encontrada com vencimento em {due_date}")
                return True  # Não é erro, apenas não há contas
            
            logger.info(f"Encontradas {len(accounts)} conta(s) a receber com vencimento em {due_date}")
            
            # Formata mensagem
            message = self.format_accounts_receivable_message(accounts, due_date, is_today)
            
            if not message:
                logger.warning("Mensagem vazia, não enviando notificação")
                return False
            
            # Envia mensagem
            if not WHATSAPP_NUMBER:
                logger.warning("WHATSAPP_NUMBER não configurado. Mensagem não enviada.")
                logger.info(f"Mensagem que seria enviada:\n{message}")
                return False
            
            logger.info(f"Enviando notificação de contas a receber para {WHATSAPP_NUMBER}")
            self.whatsapp_client.send_message(WHATSAPP_NUMBER, message)
            
            logger.info("Notificação enviada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de contas a receber: {e}", exc_info=True)
            return False
    
    def dispatch_today_receivables(self):
        """Dispara notificação de contas a receber com vencimento para hoje (7h)"""
        today = date.today()
        logger.info(f"Disparando contas a receber com vencimento para hoje ({today})")
        self.send_accounts_receivable_notification(today, is_today=True)
    
    def dispatch_tomorrow_receivables(self):
        """Dispara notificação de contas a receber com vencimento para amanhã (17:30)"""
        tomorrow = date.today() + timedelta(days=1)
        logger.info(f"Disparando contas a receber com vencimento para amanhã ({tomorrow})")
        self.send_accounts_receivable_notification(tomorrow, is_today=False)
    
    def schedule_dispatches(self):
        """
        Agenda os disparos automáticos
        - 7h: contas a receber com vencimento para hoje
        - 17:30: contas a receber com vencimento para amanhã
        """
        logger.info("Agendando disparos de contas a receber...")
        
        # Agenda disparo das 7h (contas que vencem hoje)
        schedule.every().day.at("07:00").do(self.dispatch_today_receivables)
        logger.info("Disparo das 7h agendado: contas a receber com vencimento para hoje")
        
        # Agenda disparo das 17:30 (contas que vencem amanhã)
        schedule.every().day.at("17:30").do(self.dispatch_tomorrow_receivables)
        logger.info("Disparo das 17:30 agendado: contas a receber com vencimento para amanhã")
        
        logger.info("Agendamentos configurados com sucesso")
    
    def run_scheduler(self):
        """
        Executa o agendador em loop
        Deve ser executado em thread separada ou processo separado
        """
        logger.info("Iniciando agendador de contas a receber...")
        
        # Agenda os disparos
        self.schedule_dispatches()
        
        logger.info("Agendador rodando. Verificando agendamentos a cada minuto...")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verifica a cada minuto
        except KeyboardInterrupt:
            logger.info("Agendador interrompido pelo usuário")
        except Exception as e:
            logger.error(f"Erro no agendador: {e}", exc_info=True)
    
    def close(self):
        """Fecha conexões"""
        if self.postgres_client:
            self.postgres_client.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


def test_dispatcher():
    """Função de teste para o dispatcher"""
    print("\n" + "=" * 80)
    print("TESTE DO DISPATCHER DE CONTAS A RECEBER")
    print("=" * 80)
    
    try:
        dispatcher = AccountsReceivableDispatcher()
        
        # Testa busca de contas para hoje
        print("\n1. Testando busca de contas a receber para HOJE...")
        today = date.today()
        accounts_today = dispatcher.get_accounts_receivable_by_due_date(today)
        print(f"   Encontradas: {len(accounts_today)} conta(s)")
        
        if accounts_today:
            print("\n   Contas encontradas:")
            for acc in accounts_today[:5]:  # Mostra as 5 primeiras
                partner = acc.get('partner_name', 'N/A')
                amount = acc.get('amount_residual') or acc.get('debit', 0)
                print(f"   - {partner}: R$ {amount:,.2f}")
        
        # Testa busca de contas para amanhã
        print("\n2. Testando busca de contas a receber para AMANHÃ...")
        tomorrow = date.today() + timedelta(days=1)
        accounts_tomorrow = dispatcher.get_accounts_receivable_by_due_date(tomorrow)
        print(f"   Encontradas: {len(accounts_tomorrow)} conta(s)")
        
        if accounts_tomorrow:
            print("\n   Contas encontradas:")
            for acc in accounts_tomorrow[:5]:  # Mostra as 5 primeiras
                partner = acc.get('partner_name', 'N/A')
                amount = acc.get('amount_residual') or acc.get('debit', 0)
                print(f"   - {partner}: R$ {amount:,.2f}")
        
        # Testa formatação de mensagem
        print("\n3. Testando formatação de mensagem...")
        if accounts_today:
            message = dispatcher.format_accounts_receivable_message(accounts_today, today, is_today=True)
            print("\n   Mensagem formatada:")
            print("   " + "-" * 76)
            for line in message.split('\n'):
                print(f"   {line}")
            print("   " + "-" * 76)
        
        dispatcher.close()
        print("\n✅ Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Configura logging para teste
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Executa teste
    test_dispatcher()

