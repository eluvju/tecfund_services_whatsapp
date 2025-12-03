"""
Configurações do sistema de notificação WhatsApp para Odoo
Todas as configurações são obtidas de variáveis de ambiente
Sem valores hardcoded - falha se variáveis não estiverem configuradas
"""
import os
from dotenv import load_dotenv

load_dotenv()


class ConfigurationError(Exception):
    """Exceção para erros de configuração"""
    pass


def get_required_env(key: str, description: str = None) -> str:
    """
    Obtém variável de ambiente obrigatória
    Lança exceção se não existir ou estiver vazia
    
    Args:
        key: Nome da variável de ambiente
        description: Descrição da variável para mensagem de erro
        
    Returns:
        Valor da variável de ambiente
        
    Raises:
        ConfigurationError: Se a variável não estiver configurada
    """
    value = os.getenv(key)
    if not value or not value.strip():
        desc = description or key
        raise ConfigurationError(
            f"❌ Variável de ambiente obrigatória não configurada: {key}\n"
            f"   {desc}\n"
            f"   Configure esta variável no Railway ou no arquivo .env"
        )
    return value.strip()


def get_required_env_int(key: str, description: str = None) -> int:
    """
    Obtém variável de ambiente obrigatória como inteiro
    Lança exceção se não existir ou estiver vazia
    
    Args:
        key: Nome da variável de ambiente
        description: Descrição da variável para mensagem de erro
        
    Returns:
        Valor da variável de ambiente como inteiro
        
    Raises:
        ConfigurationError: Se a variável não estiver configurada ou for inválida
    """
    value = get_required_env(key, description)
    try:
        return int(value)
    except ValueError:
        desc = description or key
        raise ConfigurationError(
            f"❌ Variável de ambiente inválida: {key}\n"
            f"   {desc}\n"
            f"   Valor recebido: '{value}' (deve ser um número inteiro)"
        )


def get_optional_env(key: str, default: str = "") -> str:
    """
    Obtém variável de ambiente opcional
    
    Args:
        key: Nome da variável de ambiente
        default: Valor padrão se não existir ou estiver vazia
        
    Returns:
        Valor da variável de ambiente ou default
    """
    value = os.getenv(key)
    if not value or not value.strip():
        return default
    return value.strip()


# Configurações do PostgreSQL/Odoo
# Extrai host e porta do ODOO_URL (formato: http://IP:PORTA)
odo_url = get_required_env("ODOO_URL", "URL do PostgreSQL no formato http://IP:PORTA")

# Remove http:// ou https://
if "://" in odo_url:
    odo_url = odo_url.split("://")[1]

# Extrai host e porta
if ":" in odo_url:
    extracted_host, extracted_port = odo_url.split(":", 1)
    # Valida porta
    try:
        extracted_port_int = int(extracted_port)
    except ValueError:
        raise ConfigurationError(
            f"❌ Porta inválida no ODOO_URL: '{extracted_port}'\n"
            f"   ODOO_URL deve estar no formato: http://IP:PORTA\n"
            f"   Exemplo: http://62.72.8.92:5432"
        )
    
    # Permite override via POSTGRES_HOST e POSTGRES_PORT
    POSTGRES_HOST = get_optional_env("POSTGRES_HOST") or extracted_host
    postgres_port_override = get_optional_env("POSTGRES_PORT")
    POSTGRES_PORT = int(postgres_port_override) if postgres_port_override else extracted_port_int
else:
    # Se não tem porta no ODOO_URL, usa o host e pede POSTGRES_PORT
    extracted_host = odo_url
    POSTGRES_HOST = get_optional_env("POSTGRES_HOST") or extracted_host
    POSTGRES_PORT = get_required_env_int("POSTGRES_PORT", "Porta do PostgreSQL")

# Configurações do banco de dados
# Permite POSTGRES_DB ou ODOO_DB como alternativa
POSTGRES_DB = get_optional_env("POSTGRES_DB") or get_optional_env("ODOO_DB")
if not POSTGRES_DB:
    raise ConfigurationError(
        "❌ Nome do banco de dados não configurado\n"
        "   Configure POSTGRES_DB ou ODOO_DB"
    )

# Permite POSTGRES_USER ou ODOO_USERNAME como alternativa
POSTGRES_USER = get_optional_env("POSTGRES_USER") or get_optional_env("ODOO_USERNAME")
if not POSTGRES_USER:
    raise ConfigurationError(
        "❌ Usuário do banco de dados não configurado\n"
        "   Configure POSTGRES_USER ou ODOO_USERNAME"
    )

# Permite POSTGRES_PASSWORD ou ODOO_PASSWORD como alternativa
POSTGRES_PASSWORD = get_optional_env("POSTGRES_PASSWORD") or get_optional_env("ODOO_PASSWORD")
if not POSTGRES_PASSWORD:
    raise ConfigurationError(
        "❌ Senha do banco de dados não configurada\n"
        "   Configure POSTGRES_PASSWORD ou ODOO_PASSWORD"
    )

# Configurações da Evolution API
EVOLUTION_API_KEY = get_required_env("EVOLUTION_API_KEY", "Chave da API Evolution")
EVOLUTION_API_URL = get_required_env("EVOLUTION_API_URL", "URL da API Evolution").rstrip('/')
EVOLUTION_INSTANCE = get_required_env("EVOLUTION_INSTANCE", "Nome da instância Evolution API")

# Número do WhatsApp para receber notificações (opcional)
WHATSAPP_NUMBER = get_optional_env("WHATSAPP_NUMBER", "")
