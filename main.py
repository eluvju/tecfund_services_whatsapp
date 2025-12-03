"""
Sistema de disparo de notificações via WhatsApp para Odoo
Notificações são executadas via cron jobs do Railway
"""
import logging
import time

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """
    Função principal
    Mantém o processo rodando enquanto os cron jobs executam as tarefas agendadas
    """
    logger.info("=" * 80)
    logger.info("Sistema de Notificação Odoo - Serviço Iniciado")
    logger.info("=" * 80)
    logger.info("Os disparos são executados via cron jobs do Railway:")
    logger.info("  - 07:30: Contas a receber (vencimento hoje)")
    logger.info("  - 07:30: Contas a pagar (vencimento hoje)")
    logger.info("  - 17:30: Compras atualizadas no dia")
    logger.info("=" * 80)
    logger.info("Serviço mantendo processo ativo...")
    
    try:
        # Mantém o processo rodando
        while True:
            time.sleep(60)  # Dorme por 60 segundos
            
    except KeyboardInterrupt:
        logger.info("\nServiço interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
