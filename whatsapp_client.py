"""
Cliente para integração com Evolution API para envio de mensagens WhatsApp
"""
import requests
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class WhatsAppClient:
    """Cliente para enviar mensagens via Evolution API"""
    
    def __init__(self, api_url: str, api_key: str, instance: str):
        """
        Inicializa o cliente WhatsApp
        
        Args:
            api_url: URL base da API Evolution
            api_key: Chave de API
            instance: Nome da instância
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.instance = instance
        self.headers = {
            'apikey': api_key,
            'Content-Type': 'application/json'
        }
    
    def send_message(self, number: str, message: str) -> Dict:
        """
        Envia uma mensagem de texto via WhatsApp
        
        Args:
            number: Número do destinatário (formato: 5511999999999)
            message: Texto da mensagem
            
        Returns:
            Resposta da API
        """
        # Tenta diferentes formatos de URL da Evolution API
        url_variants = [
            f"{self.api_url}/{self.instance}/message/sendText",
            f"{self.api_url}/{self.instance}/sendText",
            f"{self.api_url}/message/sendText/{self.instance}",
        ]
        
        payload = {
            "number": number,
            "text": message
        }
        
        last_error = None
        for url in url_variants:
            try:
                logger.debug(f"Tentando enviar mensagem via: {url}")
                response = requests.post(url, json=payload, headers=self.headers, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Mensagem enviada com sucesso para {number}")
                return result
            except requests.exceptions.RequestException as e:
                last_error = e
                logger.debug(f"Tentativa falhou com URL {url}: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    logger.debug(f"Resposta da API: {e.response.text}")
                continue
        
        # Se todas as tentativas falharam, lança o último erro
        logger.error(f"Erro ao enviar mensagem para {number} após tentar todas as URLs: {last_error}")
        if hasattr(last_error, 'response') and last_error.response is not None:
            logger.error(f"Resposta da API: {last_error.response.text}")
        raise last_error or Exception("Falha ao enviar mensagem")
    
    def send_formatted_message(self, number: str, title: str, body: str) -> Dict:
        """
        Envia uma mensagem formatada (pode ser usada para templates)
        
        Args:
            number: Número do destinatário
            title: Título da mensagem
            body: Corpo da mensagem
            
        Returns:
            Resposta da API
        """
        message = f"*{title}*\n\n{body}"
        return self.send_message(number, message)
    
    def check_instance_status(self) -> bool:
        """
        Verifica se a instância está ativa
        
        Returns:
            True se a instância está ativa, False caso contrário
        """
        # Tenta diferentes endpoints para verificar status
        url_variants = [
            f"{self.api_url}/fetchInstances",
            f"{self.api_url}/{self.instance}/status",
            f"{self.api_url}/instance/fetchInstances",
        ]
        
        for url in url_variants:
            try:
                response = requests.get(url, headers=self.headers, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                # Se a resposta é uma lista de instâncias
                if isinstance(data, list):
                    for instance in data:
                        instance_name = instance.get('instanceName') or instance.get('name') or instance.get('instance')
                        if instance_name == self.instance:
                            status = (instance.get('status') or instance.get('state') or '').lower()
                            return status in ['open', 'connected', 'ready']
                
                # Se a resposta é um objeto único
                if isinstance(data, dict):
                    status = (data.get('status') or data.get('state') or '').lower()
                    if status:
                        return status in ['open', 'connected', 'ready']
                
                return False
            except Exception as e:
                logger.debug(f"Erro ao verificar status da instância com URL {url}: {e}")
                continue
        
        # Se não conseguiu verificar, assume que está ok para não bloquear envios
        logger.warning("Não foi possível verificar o status da instância. Continuando...")
        return True

