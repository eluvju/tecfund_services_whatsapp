"""
Script para disparar contas a receber com vencimento para hoje
Executado via cron do Railway às 7:30 da manhã
"""
import sys
import os
import logging
from datetime import date

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from accounts_receivable_dispatcher import AccountsReceivableDispatcher

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Função principal"""
    logger.info("=" * 80)
    logger.info("Disparo de Contas a Receber - Vencimento HOJE")
    logger.info("=" * 80)
    
    dispatcher = None
    try:
        # Inicializa o dispatcher
        dispatcher = AccountsReceivableDispatcher()
        
        # Busca e envia notificação de contas a receber para hoje
        today = date.today()
        logger.info(f"Buscando contas a receber com vencimento para hoje ({today})")
        
        success = dispatcher.send_accounts_receivable_notification(today, is_today=True)
        
        if success:
            logger.info("✅ Disparo concluído com sucesso")
            sys.exit(0)
        else:
            logger.error("❌ Falha no disparo")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if dispatcher:
            dispatcher.close()


if __name__ == "__main__":
    main()

