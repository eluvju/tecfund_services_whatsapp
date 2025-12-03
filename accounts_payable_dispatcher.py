"""
Módulo de disparo de contas a pagar por WhatsApp
Dispara resumo de todas as contas a pagar com vencimento para hoje
"""
import logging
from datetime import date
from typing import List, Dict
from config import (
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB,
    POSTGRES_USER, POSTGRES_PASSWORD,
    EVOLUTION_API_URL, EVOLUTION_API_KEY, EVOLUTION_INSTANCE,
    WHATSAPP_NUMBER
)
from postgres_client import PostgresClient
from whatsapp_client import WhatsAppClient

logger = logging.getLogger(__name__)


class AccountsPayableDispatcher:
    """Sistema de disparo de contas a pagar"""
    
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
    
    def get_accounts_payable_for_today(self) -> List[Dict]:
        """
        Busca todas as contas a pagar com vencimento para hoje
        
        Returns:
            Lista de contas a pagar
        """
        today = date.today()
        
        query = """
            SELECT 
                aml.id,
                aml.move_id,
                aml.partner_id,
                rp.name as partner_name,
                am.company_id,
                rc.name as company_name,
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
            LEFT JOIN res_company rc ON am.company_id = rc.id
            INNER JOIN account_account aa ON aml.account_id = aa.id
            WHERE aa.account_type = 'liability_payable'
              AND aml.date_maturity = %s
              AND am.state = 'posted'
              AND aml.reconciled = false
              AND aml.credit > 0
            ORDER BY rc.name, aml.date_maturity, rp.name, aml.name
        """
        
        try:
            results = self.postgres_client.execute_query(query, (today,))
            return results
        except Exception as e:
            logger.error(f"Erro ao buscar contas a pagar para hoje: {e}")
            return []
    
    def format_accounts_payable_message(self, accounts: List[Dict]) -> str:
        """
        Formata mensagem de resumo de contas a pagar agrupado por empresa
        
        Args:
            accounts: Lista de contas a pagar
            
        Returns:
            Mensagem formatada (resumo compacto por empresa)
        """
        if not accounts:
            return None
        
        today = date.today()
        data_formatada = today.strftime('%d/%m/%Y')
        
        # Agrupa por company (empresa do Odoo)
        by_company = {}
        for acc in accounts:
            company_name = acc.get('company_name', 'Sem empresa')
            if company_name not in by_company:
                by_company[company_name] = {
                    'count': 0,
                    'total': 0,
                    'partners': set()
                }
            
            amount = abs(acc.get('amount_residual') or acc.get('credit', 0))
            by_company[company_name]['count'] += 1
            by_company[company_name]['total'] += amount
            partner_name = acc.get('partner_name', '')
            if partner_name:
                by_company[company_name]['partners'].add(partner_name)
        
        # Calcula total geral
        total_geral = sum(data['total'] for data in by_company.values())
        total_str = f"R$ {total_geral:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        # Ordena empresas por valor total (maior primeiro)
        sorted_companies = sorted(
            by_company.items(),
            key=lambda x: x[1]['total'],
            reverse=True
        )
        
        # Monta mensagem resumida
        message = f"💰 *Contas a Pagar - Hoje*\n"
        message += f"📅 {data_formatada}\n"
        message += f"📊 {len(accounts)} conta(s) | {len(by_company)} empresa(s)\n"
        message += f"💵 Total: {total_str}\n\n"
        
        message += "*Resumo por Empresa:*\n"
        
        for company_name, data in sorted_companies:
            company_total_str = f"R$ {data['total']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            message += f"• *{company_name}*: {company_total_str} ({data['count']} conta(s))\n"
        
        message += f"\n⚠️ Total: {total_str}"
        
        return message
    
    def send_accounts_payable_summary(self) -> bool:
        """
        Busca e envia resumo de contas a pagar para hoje
        
        Returns:
            True se enviou com sucesso, False caso contrário
        """
        try:
            logger.info("Buscando contas a pagar para hoje")
            
            # Busca contas
            accounts = self.get_accounts_payable_for_today()
            
            if not accounts:
                logger.info("Nenhuma conta a pagar encontrada para hoje")
                return True  # Não é erro, apenas não há contas
            
            logger.info(f"Encontradas {len(accounts)} conta(s) a pagar para hoje")
            
            # Formata mensagem
            message = self.format_accounts_payable_message(accounts)
            
            if not message:
                logger.warning("Mensagem vazia, não enviando notificação")
                return False
            
            # Envia mensagem
            if not WHATSAPP_NUMBER:
                logger.warning("WHATSAPP_NUMBER não configurado. Mensagem não enviada.")
                logger.info(f"Mensagem que seria enviada:\n{message}")
                return False
            
            logger.info(f"Enviando resumo de contas a pagar para {WHATSAPP_NUMBER}")
            self.whatsapp_client.send_message(WHATSAPP_NUMBER, message)
            
            logger.info("Resumo de contas a pagar enviado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar resumo de contas a pagar: {e}", exc_info=True)
            return False
    
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

