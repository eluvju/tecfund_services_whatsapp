"""
Script de teste para verificar conexão com PostgreSQL do Odoo
Carrega configurações do arquivo .env e testa a conexão
"""
import sys
import os
from dotenv import load_dotenv
from config import (
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, 
    POSTGRES_USER, POSTGRES_PASSWORD
)
from postgres_client import PostgresClient

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()


def test_postgres_connection():
    """Testa conexão com PostgreSQL"""
    print("=" * 80)
    print("TESTANDO CONEXÃO COM POSTGRESQL")
    print("=" * 80)
    
    print(f"\n📋 Configurações do .env:")
    print(f"   Host:        {POSTGRES_HOST}")
    print(f"   Porta:       {POSTGRES_PORT}")
    print(f"   Database:    {POSTGRES_DB}")
    print(f"   Usuário:     {POSTGRES_USER}")
    print(f"   Senha:       {'*' * len(POSTGRES_PASSWORD) if POSTGRES_PASSWORD else '(vazia)'}")
    
    print(f"\n🔌 Tentando conectar ao PostgreSQL...")
    
    try:
        client = PostgresClient(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )
        
        print("✅ Conexão estabelecida com sucesso!\n")
        
        # Testa conexão básica
        if client.test_connection():
            print("✅ Teste de conexão básica: OK")
        else:
            print("❌ Teste de conexão básica: FALHOU")
            return False
        
        # Testa busca de faturas
        print("\n🔍 Buscando faturas recentes...")
        moves = client.get_recent_moves(hours=24, limit=5)
        print(f"✅ Encontradas {len(moves)} fatura(s) nas últimas 24 horas")
        
        if moves:
            print("\n📋 Últimas faturas encontradas:")
            for move in moves:
                print(f"  - ID: {move.get('id')} | {move.get('name')} | {move.get('date')} | R$ {move.get('amount_total', 0):,.2f}")
        
        # Testa query de tabelas
        print("\n🔍 Verificando estrutura do banco...")
        try:
            tables_query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                  AND table_name LIKE 'account%'
                ORDER BY table_name
                LIMIT 10
            """
            tables = client.execute_query(tables_query)
            print(f"✅ Tabelas relacionadas a 'account': {len(tables)} encontradas")
            if tables:
                print("   Tabelas:", ", ".join([t['table_name'] for t in tables[:5]]))
        except Exception as e:
            print(f"⚠️  Não foi possível listar tabelas: {e}")
        
        # Fecha conexão
        client.close()
        
        return True
        
    except Exception as e:
        error_type = type(e).__name__
        
        if 'OperationalError' in error_type or 'connection' in str(e).lower():
            print(f"\n❌ ERRO DE CONEXÃO:")
            print(f"   {str(e)}")
            print("\n💡 Possíveis causas:")
            print("   - Servidor PostgreSQL não está acessível")
            print("   - Porta incorreta ou bloqueada por firewall")
            print("   - Credenciais incorretas (usuário/senha)")
            print("   - Banco de dados não existe")
        elif 'Error' in error_type:
            print(f"\n❌ ERRO DO POSTGRESQL:")
            print(f"   {str(e)}")
        else:
            print(f"\n❌ ERRO INESPERADO:")
            print(f"   {error_type}: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return False


def test_query_sample():
    """Testa uma query de exemplo"""
    print("\n" + "=" * 80)
    print("TESTANDO QUERY DE EXEMPLO")
    print("=" * 80)
    
    try:
        client = PostgresClient(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )
        
        # Query simples para testar
        query = "SELECT COUNT(*) as total FROM account_move WHERE state = 'posted'"
        results = client.execute_query(query)
        
        if results:
            total = results[0].get('total', 0)
            print(f"\n✅ Total de faturas confirmadas no banco: {total}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao executar query de exemplo: {e}")
        return False


def main():
    """Função principal"""
    print("\n" + "🔍 TESTE DE CONEXÃO POSTGRESQL - Sistema Odoo WhatsApp Notifier" + "\n")
    
    # Importa psycopg2 apenas quando necessário
    try:
        import psycopg2
    except ImportError:
        print("❌ ERRO: psycopg2-binary não está instalado!")
        print("   Execute: pip install -r requirements.txt")
        return 1
    
    # Testa conexão
    connection_ok = test_postgres_connection()
    
    if connection_ok:
        # Testa query de exemplo
        query_ok = test_query_sample()
        
        print("\n" + "=" * 80)
        print("RESUMO DOS TESTES")
        print("=" * 80)
        print(f"Conexão PostgreSQL: {'✅ OK' if connection_ok else '❌ FALHOU'}")
        print(f"Query de exemplo:   {'✅ OK' if query_ok else '❌ FALHOU'}")
        print("=" * 80)
        
        if connection_ok and query_ok:
            print("\n✅ Todos os testes passaram! O sistema está pronto para usar PostgreSQL.")
            return 0
        else:
            print("\n⚠️  Alguns testes falharam. Verifique as configurações.")
            return 1
    else:
        print("\n" + "=" * 80)
        print("RESUMO DOS TESTES")
        print("=" * 80)
        print("Conexão PostgreSQL: ❌ FALHOU")
        print("=" * 80)
        print("\n❌ Não foi possível conectar ao PostgreSQL. Verifique:")
        print("   1. As configurações no arquivo .env")
        print("   2. Se o servidor PostgreSQL está acessível")
        print("   3. Se as credenciais estão corretas")
        print("   4. Se o firewall permite conexões na porta", POSTGRES_PORT)
        return 1


if __name__ == "__main__":
    sys.exit(main())

