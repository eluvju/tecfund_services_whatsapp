"""
Sistema de notificação WhatsApp para lançamentos do Odoo
Monitora lançamentos e envia notificações via Evolution API
"""
import time
import logging
from datetime import datetime
from typing import Set
import schedule

from config import (
    ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD,
    EVOLUTION_API_URL, EVOLUTION_API_KEY, EVOLUTION_INSTANCE,
    POLLING_INTERVAL, WHATSAPP_NUMBER, ODOO_MODEL
)
from odoo_client import OdooClient
from whatsapp_client import WhatsAppClient

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('odoo_whatsapp_notifier.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class OdooWhatsAppNotifier:
    """Sistema principal de monitoramento e notificação"""
    
    def __init__(self):
        """Inicializa o sistema"""
        self.odoo_client = OdooClient(ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD)
        self.whatsapp_client = WhatsAppClient(EVOLUTION_API_URL, EVOLUTION_API_KEY, EVOLUTION_INSTANCE)
        self.processed_ids: Set[int] = set()
        self._load_processed_ids()
    
    def _load_processed_ids(self):
        """Carrega IDs já processados de um arquivo (persistência básica)"""
        try:
            with open('processed_ids.txt', 'r') as f:
                self.processed_ids = {int(line.strip()) for line in f if line.strip()}
            logger.info(f"Carregados {len(self.processed_ids)} IDs já processados")
        except FileNotFoundError:
            logger.info("Nenhum ID processado anteriormente")
            self.processed_ids = set()
    
    def _save_processed_id(self, move_id: int):
        """Salva um ID processado no arquivo"""
        try:
            with open('processed_ids.txt', 'a') as f:
                f.write(f"{move_id}\n")
            self.processed_ids.add(move_id)
        except Exception as e:
            logger.error(f"Erro ao salvar ID processado: {e}")
    
    def format_move_message(self, move: dict) -> str:
        """
        Formata uma mensagem sobre um lançamento
        
        Args:
            move: Dicionário com dados do lançamento
            
        Returns:
            Mensagem formatada
        """
        move_name = move.get('name', 'N/A')
        move_date = move.get('date', 'N/A')
        amount = move.get('amount_total', 0)
        partner = move.get('partner_name', 'N/A')
        move_type = move.get('move_type', 'N/A')
        
        # Traduz tipo de movimento
        type_map = {
            'out_invoice': 'Fatura de Venda',
            'in_invoice': 'Fatura de Compra',
            'out_refund': 'Reembolso de Venda',
            'in_refund': 'Reembolso de Compra',
            'entry': 'Lançamento Manual'
        }
        move_type_pt = type_map.get(move_type, move_type)
        
        # Formata valor
        amount_str = f"R$ {amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        message = f"""*Novo Lançamento no Odoo*

📋 *Documento:* {move_name}
📅 *Data:* {move_date}
💰 *Valor:* {amount_str}
👤 *Parceiro:* {partner}
📝 *Tipo:* {move_type_pt}

🔗 ID: {move.get('id', 'N/A')}"""
        
        return message
    
    def check_and_notify(self):
        """Verifica novos lançamentos e envia notificações"""
        try:
            logger.info("Verificando novos lançamentos...")
            
            # Busca lançamentos das últimas 24 horas
            recent_moves = self.odoo_client.get_recent_moves(hours=24, limit=100)
            
            new_moves = [
                move for move in recent_moves
                if move.get('id') not in self.processed_ids
            ]
            
            if not new_moves:
                logger.info("Nenhum novo lançamento encontrado")
                return
            
            logger.info(f"Encontrados {len(new_moves)} novo(s) lançamento(s)")
            
            # Verifica se a instância WhatsApp está ativa
            if not self.whatsapp_client.check_instance_status():
                logger.warning("Instância WhatsApp não está ativa. Pulando envio de notificações.")
                return
            
            # Envia notificação para cada novo lançamento
            for move in new_moves:
                try:
                    message = self.format_move_message(move)
                    
                    if WHATSAPP_NUMBER:
                        self.whatsapp_client.send_message(WHATSAPP_NUMBER, message)
                        logger.info(f"Notificação enviada para lançamento {move.get('id')}")
                    else:
                        logger.warning("WHATSAPP_NUMBER não configurado. Mensagem não enviada.")
                        logger.info(f"Mensagem que seria enviada:\n{message}")
                    
                    # Marca como processado
                    self._save_processed_id(move.get('id'))
                    
                    # Pequena pausa entre envios
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Erro ao processar lançamento {move.get('id')}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Erro ao verificar lançamentos: {e}", exc_info=True)
    
    def run(self):
        """Inicia o sistema de monitoramento"""
        logger.info("=" * 60)
        logger.info("Sistema de Notificação WhatsApp Odoo iniciado")
        logger.info("=" * 60)
        logger.info(f"Odoo URL: {ODOO_URL}")
        logger.info(f"Evolution API: {EVOLUTION_API_URL}")
        logger.info(f"Instância: {EVOLUTION_INSTANCE}")
        logger.info(f"Intervalo de verificação: {POLLING_INTERVAL} segundos")
        logger.info("=" * 60)
        
        # Verifica conexão inicial
        try:
            logger.info("Testando conexão com Odoo...")
            test_moves = self.odoo_client.get_recent_moves(hours=1, limit=1)
            logger.info(f"Conexão com Odoo OK. Encontrados {len(test_moves)} lançamento(s) na última hora.")
        except Exception as e:
            logger.error(f"Erro ao conectar com Odoo: {e}")
            logger.warning("Sistema iniciará, mas pode não funcionar corretamente.")
        
        # Verifica status da instância WhatsApp
        try:
            logger.info("Verificando instância WhatsApp...")
            if self.whatsapp_client.check_instance_status():
                logger.info("Instância WhatsApp está ativa")
            else:
                logger.warning("Instância WhatsApp não está ativa ou não encontrada")
        except Exception as e:
            logger.warning(f"Erro ao verificar instância WhatsApp: {e}")
        
        # Executa verificação inicial
        self.check_and_notify()
        
        # Agenda verificação periódica
        schedule.every(POLLING_INTERVAL).seconds.do(self.check_and_notify)
        
        logger.info(f"Monitoramento agendado para executar a cada {POLLING_INTERVAL} segundos")
        logger.info("Pressione Ctrl+C para parar")
        
        # Loop principal
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\nSistema interrompido pelo usuário")
        except Exception as e:
            logger.error(f"Erro no loop principal: {e}", exc_info=True)


def main():
    """Função principal"""
    try:
        notifier = OdooWhatsAppNotifier()
        notifier.run()
    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()

