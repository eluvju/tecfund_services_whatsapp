"""
Script para enviar notificação de falha de testes para Discord
"""
import sys
import json
import requests
from datetime import datetime

def send_discord_webhook(webhook_url: str, commit_info: dict, test_output: str):
    """
    Envia notificação de falha para Discord
    
    Args:
        webhook_url: URL do webhook do Discord
        commit_info: Dicionário com informações do commit
        test_output: Saída dos testes
    """
    # Limita o tamanho da saída dos testes (Discord tem limite de 2000 caracteres)
    max_output_length = 1500
    if len(test_output) > max_output_length:
        test_output = test_output[:max_output_length] + f"\n... (truncado, {len(test_output) - max_output_length} caracteres restantes)"
    
    # Formata a mensagem do commit
    commit_message = commit_info.get('message', 'N/A')
    if len(commit_message) > 200:
        commit_message = commit_message[:200] + "..."
    
    # Cria embed do Discord
    embed = {
        "title": "❌ Testes Falharam - Sistema de Contas a Receber",
        "description": f"Os testes automatizados falharam após o commit mais recente.",
        "color": 15158332,  # Vermelho
        "fields": [
            {
                "name": "📋 Commit",
                "value": f"`{commit_info.get('hash', 'N/A')}`",
                "inline": True
            },
            {
                "name": "👤 Autor",
                "value": commit_info.get('author', 'N/A'),
                "inline": True
            },
            {
                "name": "📅 Data",
                "value": commit_info.get('date', 'N/A'),
                "inline": True
            },
            {
                "name": "💬 Mensagem do Commit",
                "value": f"```\n{commit_message}\n```",
                "inline": False
            },
            {
                "name": "📊 Resumo dos Testes",
                "value": f"```\n{test_output}\n```",
                "inline": False
            }
        ],
        "footer": {
            "text": "GitHub Actions - Sistema de Contas a Receber",
            "icon_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    payload = {
        "content": "@everyone",
        "embeds": [embed],
        "username": "GitHub Actions"
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        print(f"✅ Notificação enviada para Discord com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao enviar notificação para Discord: {e}")
        return False


def main():
    """Função principal"""
    if len(sys.argv) < 4:
        print("Uso: python send_discord_notification.py <webhook_url> <test_output_file> <commit_hash> <commit_message> <commit_author> <commit_date>")
        sys.exit(1)
    
    webhook_url = sys.argv[1]
    test_output_file = sys.argv[2]
    
    # Lê saída dos testes
    try:
        with open(test_output_file, 'r', encoding='utf-8') as f:
            test_output = f.read()
    except Exception as e:
        test_output = f"Erro ao ler arquivo de testes: {e}"
    
    # Informações do commit
    commit_info = {
        'hash': sys.argv[3] if len(sys.argv) > 3 else 'N/A',
        'message': sys.argv[4] if len(sys.argv) > 4 else 'N/A',
        'author': sys.argv[5] if len(sys.argv) > 5 else 'N/A',
        'date': sys.argv[6] if len(sys.argv) > 6 else 'N/A'
    }
    
    # Envia notificação
    success = send_discord_webhook(webhook_url, commit_info, test_output)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

