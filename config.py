"""
Configurações do sistema de notificação WhatsApp para Odoo
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Configurações do PostgreSQL/Odoo
# Se ODOO_URL for fornecido, extrai o host e porta
odoo_url = os.getenv("ODOO_URL", "http://62.72.8.92:5432")
# Remove http:// ou https:// e separa host:porta
if "://" in odoo_url:
    odoo_url = odoo_url.split("://")[1]
if ":" in odoo_url:
    host, port = odoo_url.split(":")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", host)
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", port))
else:
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", odoo_url)
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))

POSTGRES_DB = os.getenv("POSTGRES_DB", os.getenv("ODOO_DB", "odoo"))
POSTGRES_USER = os.getenv("POSTGRES_USER", os.getenv("ODOO_USERNAME", "XYZ"))
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", os.getenv("ODOO_PASSWORD", "XYZ"))

# Configurações da Evolution API
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "1B68D5DA-A8FA-43E9-8D8A-6F6963AE4B11")
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "https://api.omnigalaxy.brainesscompany.com.br/manager/instance").rstrip('/')
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE", "brainess")

# Número do WhatsApp para receber notificações
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "")

