"""
Cliente para integração com Odoo via XML-RPC
"""
import xmlrpc.client
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class OdooClient:
    """Cliente para buscar dados do Odoo"""
    
    def __init__(self, url: str, db: str, username: str, password: str):
        """
        Inicializa o cliente Odoo
        
        Args:
            url: URL do servidor Odoo
            db: Nome do banco de dados
            username: Usuário para autenticação
            password: Senha para autenticação
        """
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.common = None
        self.models = None
        self.uid = None
        self._connect()
    
    def _connect(self):
        """Conecta ao Odoo e autentica"""
        try:
            # Conecta ao endpoint comum
            self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            
            # Autentica
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})
            
            if not self.uid:
                raise Exception("Falha na autenticação com o Odoo")
            
            # Conecta ao endpoint de modelos
            self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
            
            logger.info("Conectado ao Odoo com sucesso")
        except Exception as e:
            logger.error(f"Erro ao conectar ao Odoo: {e}")
            raise
    
    def search_read(self, model: str, domain: list, fields: list, limit: int = 100, order: str = "id desc") -> List[Dict]:
        """
        Busca e lê registros do Odoo
        
        Args:
            model: Nome do modelo (ex: 'account.move')
            domain: Domínio de busca (filtros)
            fields: Lista de campos para retornar
            limit: Limite de registros
            order: Ordenação
            
        Returns:
            Lista de dicionários com os registros
        """
        try:
            ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                model, 'search',
                [domain],
                {'limit': limit, 'order': order}
            )
            
            if not ids:
                return []
            
            records = self.models.execute_kw(
                self.db, self.uid, self.password,
                model, 'read',
                [ids],
                {'fields': fields}
            )
            
            return records
        except Exception as e:
            logger.error(f"Erro ao buscar registros do modelo {model}: {e}")
            return []
    
    def get_recent_moves(self, hours: int = 24, limit: int = 100) -> List[Dict]:
        """
        Busca lançamentos recentes (account.move)
        
        Args:
            hours: Quantas horas para trás buscar
            limit: Limite de registros
            
        Returns:
            Lista de lançamentos
        """
        # Busca lançamentos criados nas últimas X horas
        since_date = (datetime.now() - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
        
        domain = [
            ('state', '=', 'posted'),  # Apenas lançamentos confirmados
            ('create_date', '>=', since_date)
        ]
        
        fields = [
            'id', 'name', 'date', 'ref', 'amount_total', 'partner_id',
            'move_type', 'state', 'create_date', 'create_uid'
        ]
        
        moves = self.search_read('account.move', domain, fields, limit=limit)
        
        # Expande informações do parceiro
        for move in moves:
            if move.get('partner_id'):
                move['partner_name'] = move['partner_id'][1] if isinstance(move['partner_id'], list) else None
            else:
                move['partner_name'] = None
        
        return moves
    
    def get_move_details(self, move_id: int) -> Optional[Dict]:
        """
        Busca detalhes completos de um lançamento
        
        Args:
            move_id: ID do lançamento
            
        Returns:
            Dicionário com os detalhes do lançamento
        """
        try:
            records = self.models.execute_kw(
                self.db, self.uid, self.password,
                'account.move', 'read',
                [[move_id]],
                {'fields': [
                    'id', 'name', 'date', 'ref', 'amount_total', 'amount_untaxed',
                    'amount_tax', 'partner_id', 'move_type', 'state', 'create_date',
                    'invoice_line_ids', 'line_ids'
                ]}
            )
            
            if records:
                move = records[0]
                # Expande informações do parceiro
                if move.get('partner_id'):
                    move['partner_name'] = move['partner_id'][1] if isinstance(move['partner_id'], list) else None
                return move
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar detalhes do lançamento {move_id}: {e}")
            return None


