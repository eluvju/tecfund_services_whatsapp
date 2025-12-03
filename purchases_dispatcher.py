"""
Módulo de disparo de compras atualizadas no dia por WhatsApp
Dispara resumo de compras atualizadas no dia com seus status
"""
import logging
from datetime import date, datetime
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


class PurchasesDispatcher:
    """Sistema de disparo de compras atualizadas"""
    
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
    
    def get_purchases_updated_today(self) -> List[Dict]:
        """
        Busca compras atualizadas no dia de hoje
        
        Returns:
            Lista de compras atualizadas
        """
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        
        query = """
            SELECT 
                po.id,
                po.name,
                po.date_order,
                po.date_approve,
                po.state,
                po.partner_id,
                rp.name as partner_name,
                po.amount_total,
                po.amount_untaxed,
                po.amount_tax,
                po.create_date,
                po.write_date,
                po.user_id,
                ru.login as user_name,
                po.currency_id,
                po.origin,
                po.notes
            FROM purchase_order po
            LEFT JOIN res_partner rp ON po.partner_id = rp.id
            LEFT JOIN res_users ru ON po.user_id = ru.id
            WHERE DATE(po.write_date) = CURRENT_DATE
               OR DATE(po.create_date) = CURRENT_DATE
            ORDER BY po.write_date DESC, po.create_date DESC
        """
        
        try:
            results = self.postgres_client.execute_query(query)
            return results
        except Exception as e:
            logger.error(f"Erro ao buscar compras atualizadas no dia: {e}")
            return []
    
    def format_purchase_status(self, state: str) -> str:
        """Traduz status da compra para português"""
        status_map = {
            'draft': '📝 Rascunho',
            'sent': '📤 Enviado',
            'to approve': '⏳ Aguardando Aprovação',
            'purchase': '✅ Aprovado',
            'done': '✅ Recebido',
            'cancel': '❌ Cancelado'
        }
        return status_map.get(state, state)
    
    def format_purchases_message(self, purchases: List[Dict]) -> str:
        """
        Formata mensagem de compras atualizadas
        
        Args:
            purchases: Lista de compras
            
        Returns:
            Mensagem formatada
        """
        if not purchases:
            return None
        
        today = date.today()
        data_formatada = today.strftime('%d/%m/%Y')
        
        # Agrupa por status
        by_status = {}
        for purchase in purchases:
            state = purchase.get('state', 'unknown')
            if state not in by_status:
                by_status[state] = []
            by_status[state].append(purchase)
        
        # Calcula total
        total = sum(
            (purchase.get('amount_total') or 0)
            for purchase in purchases
        )
        total_str = f"R$ {total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        # Monta mensagem
        message = f"🛒 *Compras Atualizadas - Hoje*\n"
        message += f"📅 Data: {data_formatada}\n"
        message += f"📊 Total de compras: {len(purchases)}\n"
        message += f"💰 Valor total: {total_str}\n\n"
        
        # Lista compras por status
        for state, state_purchases in by_status.items():
            status_label = self.format_purchase_status(state)
            message += f"*{status_label}: {len(state_purchases)} compra(s)*\n"
            message += "─" * 30 + "\n"
            
            for idx, purchase in enumerate(state_purchases[:10], 1):  # Limita a 10 por status
                partner = purchase.get('partner_name', 'N/A')
                order_name = purchase.get('name', 'N/A')
                amount = purchase.get('amount_total', 0) or 0
                amount_str = f"R$ {amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                
                # Data da compra
                date_order = purchase.get('date_order')
                date_str = ""
                if date_order:
                    try:
                        if isinstance(date_order, str):
                            date_order = datetime.strptime(date_order.split('.')[0], '%Y-%m-%d %H:%M:%S')
                        date_str = date_order.strftime('%d/%m/%Y')
                    except:
                        date_str = str(date_order)[:10]
                
                message += f"{idx}. *{order_name}*\n"
                message += f"   Fornecedor: {partner}\n"
                if date_str:
                    message += f"   Data: {date_str}\n"
                message += f"   Valor: {amount_str}\n\n"
            
            if len(state_purchases) > 10:
                message += f"   ... e mais {len(state_purchases) - 10} compra(s)\n\n"
            
            message += "\n"
        
        return message
    
    def send_purchases_summary(self) -> bool:
        """
        Busca e envia resumo de compras atualizadas no dia
        
        Returns:
            True se enviou com sucesso, False caso contrário
        """
        try:
            logger.info("Buscando compras atualizadas no dia")
            
            # Busca compras
            purchases = self.get_purchases_updated_today()
            
            if not purchases:
                logger.info("Nenhuma compra atualizada encontrada no dia")
                return True  # Não é erro, apenas não há compras
            
            logger.info(f"Encontradas {len(purchases)} compra(s) atualizada(s) no dia")
            
            # Formata mensagem
            message = self.format_purchases_message(purchases)
            
            if not message:
                logger.warning("Mensagem vazia, não enviando notificação")
                return False
            
            # Envia mensagem
            if not WHATSAPP_NUMBER:
                logger.warning("WHATSAPP_NUMBER não configurado. Mensagem não enviada.")
                logger.info(f"Mensagem que seria enviada:\n{message}")
                return False
            
            logger.info(f"Enviando resumo de compras para {WHATSAPP_NUMBER}")
            self.whatsapp_client.send_message(WHATSAPP_NUMBER, message)
            
            logger.info("Resumo de compras enviado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar resumo de compras: {e}", exc_info=True)
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

