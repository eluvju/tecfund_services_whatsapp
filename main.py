"""
Sistema de disparo de contas a receber via WhatsApp
Dispara notificações automáticas de contas a receber com vencimento próximo
"""
import logging
from accounts_receivable_dispatcher import AccountsReceivableDispatcher

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('accounts_receivable_notifier.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Função principal"""
    logger.info("=" * 80)
    logger.info("Sistema de Notificação de Contas a Receber - Iniciado")
    logger.info("=" * 80)
    
    try:
        # Inicializa o dispatcher
        dispatcher = AccountsReceivableDispatcher()
        
        logger.info("Agendamentos configurados:")
        logger.info("  - 07:00: Contas a receber com vencimento para HOJE")
        logger.info("  - 17:30: Contas a receber com vencimento para AMANHÃ")
        logger.info("=" * 80)
        
        # Inicia o agendador
        dispatcher.run_scheduler()
        
    except KeyboardInterrupt:
        logger.info("\nSistema interrompido pelo usuário")
        if 'dispatcher' in locals():
            dispatcher.close()
    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
        if 'dispatcher' in locals():
            dispatcher.close()
        raise


if __name__ == "__main__":
    main()
