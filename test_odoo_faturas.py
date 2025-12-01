"""
Script de teste para buscar dados de faturas do Odoo
Carrega configurações do arquivo .env e exibe informações das faturas
Suporta conexão via PostgreSQL direto ou XML-RPC
"""
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from config import (
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB,
    POSTGRES_USER, POSTGRES_PASSWORD, ODOO_URL
)

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Tenta usar PostgreSQL primeiro, depois XML-RPC como fallback
try:
    from postgres_client import PostgresClient
    USE_POSTGRES = True
except ImportError:
    USE_POSTGRES = False
    from odoo_client import OdooClient

def formatar_valor(valor):
    """Formata valor monetário"""
    if valor:
        return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    return "R$ 0,00"

def formatar_data(data):
    """Formata data para exibição"""
    if data:
        try:
            # Tenta parsear diferentes formatos de data
            if isinstance(data, str):
                # Remove informações de timezone se existirem
                data = data.split('.')[0].split('+')[0]
                dt = datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
            else:
                dt = data
            return dt.strftime('%d/%m/%Y %H:%M')
        except:
            return str(data)
    return "N/A"

def exibir_faturas(faturas, limite=None):
    """Exibe faturas de forma formatada"""
    if not faturas:
        print("\n❌ Nenhuma fatura encontrada.")
        return
    
    total = len(faturas)
    if limite:
        faturas = faturas[:limite]
        print(f"\n📋 Exibindo {len(faturas)} de {total} fatura(s) encontrada(s):\n")
    else:
        print(f"\n📋 {total} fatura(s) encontrada(s):\n")
    
    print("=" * 100)
    
    for i, fatura in enumerate(faturas, 1):
        print(f"\n{'─' * 100}")
        print(f"FATURA #{i}")
        print(f"{'─' * 100}")
        
        print(f"ID:                    {fatura.get('id', 'N/A')}")
        print(f"Número/Documento:      {fatura.get('name', 'N/A')}")
        print(f"Data:                  {formatar_data(fatura.get('date'))}")
        print(f"Data de Criação:       {formatar_data(fatura.get('create_date'))}")
        
        # Tipo de movimento
        tipo_map = {
            'out_invoice': 'Fatura de Venda',
            'in_invoice': 'Fatura de Compra',
            'out_refund': 'Reembolso de Venda',
            'in_refund': 'Reembolso de Compra',
            'entry': 'Lançamento Manual'
        }
        tipo = fatura.get('move_type', 'N/A')
        tipo_desc = tipo_map.get(tipo, tipo)
        print(f"Tipo:                  {tipo_desc} ({tipo})")
        
        # Status
        status_map = {
            'draft': 'Rascunho',
            'posted': 'Confirmado',
            'cancel': 'Cancelado'
        }
        status = fatura.get('state', 'N/A')
        status_desc = status_map.get(status, status)
        print(f"Status:                {status_desc} ({status})")
        
        # Valores
        print(f"\nValores:")
        print(f"  Total:               {formatar_valor(fatura.get('amount_total', 0))}")
        
        # Referência
        ref = fatura.get('ref', '')
        if ref:
            print(f"Referência:            {ref}")
        
        # Parceiro
        partner = fatura.get('partner_name', 'N/A')
        if partner and partner != 'N/A':
            partner_id = fatura.get('partner_id', [])
            if isinstance(partner_id, list) and len(partner_id) > 0:
                print(f"Parceiro ID:           {partner_id[0]}")
            print(f"Parceiro:              {partner}")
        
        print()

def buscar_faturas_por_periodo(client, dias=7):
    """Busca faturas dos últimos N dias"""
    print(f"\n🔍 Buscando faturas dos últimos {dias} dias...")
    
    try:
        if USE_POSTGRES:
            start_date = datetime.now() - timedelta(days=dias)
            end_date = datetime.now()
            faturas = client.get_moves_by_date_range(start_date, end_date, limit=100)
        else:
            since_date = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d %H:%M:%S')
            domain = [('create_date', '>=', since_date)]
            fields = ['id', 'name', 'date', 'ref', 'amount_total', 'partner_id', 'move_type', 'state', 'create_date', 'create_uid']
            faturas = client.search_read('account.move', domain, fields, limit=100, order="id desc")
            
            # Expande informações do parceiro
            for fatura in faturas:
                if fatura.get('partner_id'):
                    fatura['partner_name'] = fatura['partner_id'][1] if isinstance(fatura['partner_id'], list) else None
                else:
                    fatura['partner_name'] = None
        
        return faturas
    except Exception as e:
        print(f"❌ Erro ao buscar faturas: {e}")
        return []

def buscar_faturas_confirmadas(client, horas=24):
    """Busca faturas confirmadas das últimas N horas"""
    print(f"\n🔍 Buscando faturas confirmadas das últimas {horas} horas...")
    
    try:
        faturas = client.get_recent_moves(hours=horas, limit=100)
        return faturas
    except Exception as e:
        print(f"❌ Erro ao buscar faturas: {e}")
        return []

def buscar_faturas_por_tipo(client, tipo='out_invoice'):
    """Busca faturas por tipo"""
    tipo_map = {
        'venda': 'out_invoice',
        'compra': 'in_invoice',
        'reembolso_venda': 'out_refund',
        'reembolso_compra': 'in_refund',
        'manual': 'entry'
    }
    
    tipo_odoo = tipo_map.get(tipo.lower(), tipo)
    tipo_desc_map = {
        'out_invoice': 'Faturas de Venda',
        'in_invoice': 'Faturas de Compra',
        'out_refund': 'Reembolsos de Venda',
        'in_refund': 'Reembolsos de Compra',
        'entry': 'Lançamentos Manuais'
    }
    
    print(f"\n🔍 Buscando {tipo_desc_map.get(tipo_odoo, tipo)}...")
    
    try:
        if USE_POSTGRES:
            faturas = client.get_moves_by_type(tipo_odoo, state='posted', limit=50)
        else:
            domain = [('move_type', '=', tipo_odoo), ('state', '=', 'posted')]
            fields = ['id', 'name', 'date', 'ref', 'amount_total', 'partner_id', 'move_type', 'state', 'create_date']
            faturas = client.search_read('account.move', domain, fields, limit=50, order="id desc")
            
            # Expande informações do parceiro
            for fatura in faturas:
                if fatura.get('partner_id'):
                    fatura['partner_name'] = fatura['partner_id'][1] if isinstance(fatura['partner_id'], list) else None
                else:
                    fatura['partner_name'] = None
        
        return faturas
    except Exception as e:
        print(f"❌ Erro ao buscar faturas: {e}")
        return []

def resumo_faturas(faturas):
    """Exibe resumo estatístico das faturas"""
    if not faturas:
        return
    
    print("\n" + "=" * 100)
    print("📊 RESUMO ESTATÍSTICO")
    print("=" * 100)
    
    total_faturas = len(faturas)
    total_valor = sum(f.get('amount_total', 0) or 0 for f in faturas)
    
    # Contagem por tipo
    tipos = {}
    for fatura in faturas:
        tipo = fatura.get('move_type', 'unknown')
        tipos[tipo] = tipos.get(tipo, 0) + 1
    
    # Contagem por status
    status_count = {}
    for fatura in faturas:
        status = fatura.get('state', 'unknown')
        status_count[status] = status_count.get(status, 0) + 1
    
    print(f"\nTotal de Faturas:       {total_faturas}")
    print(f"Valor Total:            {formatar_valor(total_valor)}")
    
    print(f"\nPor Tipo:")
    tipo_map = {
        'out_invoice': 'Faturas de Venda',
        'in_invoice': 'Faturas de Compra',
        'out_refund': 'Reembolsos de Venda',
        'in_refund': 'Reembolsos de Compra',
        'entry': 'Lançamentos Manuais'
    }
    for tipo, count in tipos.items():
        desc = tipo_map.get(tipo, tipo)
        print(f"  {desc:30s}: {count}")
    
    print(f"\nPor Status:")
    status_map = {
        'draft': 'Rascunho',
        'posted': 'Confirmado',
        'cancel': 'Cancelado'
    }
    for status, count in status_count.items():
        desc = status_map.get(status, status)
        print(f"  {desc:30s}: {count}")

def main():
    """Função principal"""
    print("\n" + "=" * 100)
    print("🧪 TESTE DE BUSCA DE FATURAS DO ODOO")
    print("=" * 100)
    
    # Carrega configurações do .env
    print(f"\n📋 Configurações carregadas do .env:")
    
    # Conecta ao banco de dados
    print(f"\n🔌 Conectando ao banco de dados...")
    try:
        if USE_POSTGRES:
            print(f"   Modo: PostgreSQL direto")
            print(f"   Host: {POSTGRES_HOST}:{POSTGRES_PORT}")
            print(f"   Database: {POSTGRES_DB}")
            print(f"   Usuário: {POSTGRES_USER}")
            client = PostgresClient(
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                database=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD
            )
        else:
            print(f"   Modo: XML-RPC (Odoo API)")
            print(f"   URL: {ODOO_URL}")
            print(f"   Database: {POSTGRES_DB}")
            print(f"   Usuário: {POSTGRES_USER}")
            client = OdooClient(ODOO_URL, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD)
        
        print("✅ Conectado com sucesso!\n")
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Menu de opções
    print("=" * 100)
    print("OPÇÕES DE BUSCA:")
    print("=" * 100)
    print("1. Faturas confirmadas das últimas 24 horas")
    print("2. Faturas confirmadas das últimas 7 dias")
    print("3. Faturas dos últimos 7 dias (todas)")
    print("4. Faturas dos últimos 30 dias (todas)")
    print("5. Faturas de Venda (confirmadas)")
    print("6. Faturas de Compra (confirmadas)")
    print("7. Todas as faturas confirmadas")
    print("=" * 100)
    
    escolha = input("\nEscolha uma opção (1-7) ou Enter para opção 1: ").strip()
    
    faturas = []
    
    if escolha == "" or escolha == "1":
        faturas = buscar_faturas_confirmadas(client, horas=24)
    elif escolha == "2":
        faturas = buscar_faturas_confirmadas(client, horas=168)  # 7 dias
    elif escolha == "3":
        faturas = buscar_faturas_por_periodo(client, dias=7)
    elif escolha == "4":
        faturas = buscar_faturas_por_periodo(client, dias=30)
    elif escolha == "5":
        faturas = buscar_faturas_por_tipo(client, tipo='venda')
    elif escolha == "6":
        faturas = buscar_faturas_por_tipo(client, tipo='compra')
    elif escolha == "7":
        print("\n🔍 Buscando todas as faturas confirmadas...")
        try:
            if USE_POSTGRES:
                faturas = client.get_moves_by_type('out_invoice', state='posted', limit=100)
                # Também busca outros tipos
                faturas.extend(client.get_moves_by_type('in_invoice', state='posted', limit=50))
                faturas.extend(client.get_moves_by_type('entry', state='posted', limit=50))
            else:
                domain = [('state', '=', 'posted')]
                fields = ['id', 'name', 'date', 'ref', 'amount_total', 'partner_id', 'move_type', 'state', 'create_date']
                faturas = client.search_read('account.move', domain, fields, limit=100, order="id desc")
                for fatura in faturas:
                    if fatura.get('partner_id'):
                        fatura['partner_name'] = fatura['partner_id'][1] if isinstance(fatura['partner_id'], list) else None
        except Exception as e:
            print(f"❌ Erro ao buscar faturas: {e}")
            faturas = []
    else:
        print("❌ Opção inválida!")
        return
    
    # Exibe resumo
    resumo_faturas(faturas)
    
    # Exibe faturas (limitado a 10 para não ficar muito longo)
    exibir_faturas(faturas, limite=10)
    
    if len(faturas) > 10:
        print(f"\n⚠️  Mostrando apenas as 10 primeiras faturas de {len(faturas)} encontradas.")
        ver_todas = input("\nDeseja ver todas as faturas? (s/n): ").strip().lower()
        if ver_todas == 's':
            exibir_faturas(faturas, limite=None)
    
    # Fecha conexão se for PostgreSQL
    if USE_POSTGRES and hasattr(client, 'close'):
        try:
            client.close()
        except:
            pass
    
    print("\n" + "=" * 100)
    print("✅ Teste concluído!")
    print("=" * 100 + "\n")

if __name__ == "__main__":
    main()

