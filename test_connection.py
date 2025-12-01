"""
Script de teste para verificar conexões com PostgreSQL/Odoo e Evolution API
Execute este script antes de iniciar o sistema principal para validar as configurações
"""
import sys
from config import (
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB,
    POSTGRES_USER, POSTGRES_PASSWORD,
    EVOLUTION_API_URL, EVOLUTION_API_KEY, EVOLUTION_INSTANCE,
    WHATSAPP_NUMBER
)
from postgres_client import PostgresClient
from whatsapp_client import WhatsAppClient


def test_odoo_connection():
    """Testa conexão com PostgreSQL/Odoo"""
    print("=" * 60)
    print("Testando conexão com PostgreSQL/Odoo...")
    print("=" * 60)
    
    try:
        client = PostgresClient(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )
        print(f"✅ Conexão com PostgreSQL estabelecida com sucesso!")
        print(f"   Host: {POSTGRES_HOST}:{POSTGRES_PORT}")
        print(f"   Database: {POSTGRES_DB}")
        print(f"   Usuário: {POSTGRES_USER}")
        
        # Testa busca de lançamentos
        print("\nBuscando lançamentos recentes...")
        moves = client.get_recent_moves(hours=24, limit=5)
        print(f"✅ Encontrados {len(moves)} lançamento(s) nas últimas 24 horas")
        
        if moves:
            print("\nÚltimos lançamentos:")
            for move in moves[:3]:
                amount = move.get('amount_total', 0) or 0
                print(f"  - {move.get('name')} | {move.get('date')} | R$ {amount:,.2f}")
        
        # Fecha conexão
        client.close()
        
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar com PostgreSQL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_whatsapp_connection():
    """Testa conexão com Evolution API"""
    print("\n" + "=" * 60)
    print("Testando conexão com Evolution API...")
    print("=" * 60)
    
    try:
        client = WhatsAppClient(EVOLUTION_API_URL, EVOLUTION_API_KEY, EVOLUTION_INSTANCE)
        print(f"✅ Cliente WhatsApp inicializado!")
        print(f"   API URL: {EVOLUTION_API_URL}")
        print(f"   Instância: {EVOLUTION_INSTANCE}")
        
        # Testa status da instância
        print("\nVerificando status da instância...")
        status = client.check_instance_status()
        if status:
            print("✅ Instância está ativa e conectada!")
        else:
            print("⚠️  Instância não está ativa ou não foi encontrada")
            print("   (O sistema pode não funcionar corretamente)")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar com Evolution API: {e}")
        return False


def test_whatsapp_send():
    """Testa envio de mensagem WhatsApp (apenas se WHATSAPP_NUMBER estiver configurado)"""
    if not WHATSAPP_NUMBER:
        print("\n" + "=" * 60)
        print("⚠️  WHATSAPP_NUMBER não configurado. Pulando teste de envio.")
        print("=" * 60)
        return True
    
    print("\n" + "=" * 60)
    print("Testando envio de mensagem WhatsApp...")
    print("=" * 60)
    
    try:
        client = WhatsAppClient(EVOLUTION_API_URL, EVOLUTION_API_KEY, EVOLUTION_INSTANCE)
        
        message = "🔔 *Teste do Sistema*\n\nEsta é uma mensagem de teste do sistema de notificação Odoo."
        
        print(f"Enviando mensagem de teste para {WHATSAPP_NUMBER}...")
        result = client.send_message(WHATSAPP_NUMBER, message)
        
        print(f"✅ Mensagem enviada com sucesso!")
        print(f"   Resposta: {result}")
        return True
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")
        return False


def main():
    """Executa todos os testes"""
    print("\n" + "🔍 TESTE DE CONEXÕES - Sistema Odoo WhatsApp Notifier" + "\n")
    
    results = []
    
    # Testa PostgreSQL/Odoo
    results.append(("PostgreSQL/Odoo", test_odoo_connection()))
    
    # Testa Evolution API
    results.append(("Evolution API", test_whatsapp_connection()))
    
    # Testa envio (opcional)
    if WHATSAPP_NUMBER:
        results.append(("Envio WhatsApp", test_whatsapp_send()))
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    all_ok = True
    for name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{name:20s}: {status}")
        if not success:
            all_ok = False
    
    print("=" * 60)
    
    if all_ok:
        print("\n✅ Todos os testes passaram! O sistema está pronto para uso.")
        return 0
    else:
        print("\n❌ Alguns testes falharam. Verifique as configurações.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

