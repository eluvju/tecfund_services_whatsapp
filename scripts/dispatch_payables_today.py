"""
Script para disparar resumo de contas a pagar com vencimento para hoje
Executado via cron do Railway às 7:30 da manhã
"""
import sys
import os
import logging

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from accounts_payable_dispatcher import AccountsPayableDispatcher

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
    logger.info("Disparo de Contas a Pagar - Vencimento HOJE")
    logger.info("=" * 80)
    
    dispatcher = None
    try:
        # Inicializa o dispatcher
        dispatcher = AccountsPayableDispatcher()
        
        # Busca e envia resumo de contas a pagar para hoje
        logger.info("Buscando contas a pagar com vencimento para hoje")
        
        success = dispatcher.send_payable_summary()
        
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

