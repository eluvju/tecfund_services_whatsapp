"""
Script para disparar resumo de compras atualizadas no dia
Executado via cron do Railway às 17:30
"""
import sys
import os
import logging

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purchases_dispatcher import PurchasesDispatcher

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
    logger.info("Disparo de Compras Atualizadas - Hoje")
    logger.info("=" * 80)
    
    dispatcher = None
    try:
        # Inicializa o dispatcher
        dispatcher = PurchasesDispatcher()
        
        # Busca e envia resumo de compras atualizadas no dia
        logger.info("Buscando compras atualizadas no dia")
        
        success = dispatcher.send_purchases_summary()
        
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

