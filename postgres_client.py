"""
Cliente para integração direta com PostgreSQL do Odoo
Busca dados de faturas diretamente do banco de dados
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class PostgresClient:
    """Cliente para buscar dados diretamente do PostgreSQL do Odoo"""
    
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        """
        Inicializa o cliente PostgreSQL
        
        Args:
            host: Host do servidor PostgreSQL
            port: Porta do servidor PostgreSQL
            database: Nome do banco de dados
            user: Usuário do banco de dados
            password: Senha do banco de dados
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.conn = None
        self._connect()
    
    def _connect(self):
        """Conecta ao banco de dados PostgreSQL"""
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                connect_timeout=10
            )
            logger.info(f"Conectado ao PostgreSQL com sucesso ({self.host}:{self.port}/{self.database})")
        except Exception as e:
            logger.error(f"Erro ao conectar ao PostgreSQL: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """
        Executa uma query SQL e retorna os resultados como lista de dicionários
        
        Args:
            query: Query SQL a ser executada
            params: Parâmetros para a query (tupla)
            
        Returns:
            Lista de dicionários com os resultados
        """
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                # Converte para lista de dicionários
                return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Erro ao executar query: {e}")
            logger.error(f"Query: {query[:200]}...")  # Log parcial da query
            raise
    
    def get_recent_moves(self, hours: int = 24, limit: int = 100) -> List[Dict]:
        """
        Busca lançamentos (account_move) recentes do banco
        
        Args:
            hours: Quantas horas para trás buscar
            limit: Limite de registros
            
        Returns:
            Lista de lançamentos
        """
        since_date = datetime.now() - timedelta(hours=hours)
        
        query = """
            SELECT 
                am.id,
                am.name,
                am.date,
                am.ref,
                am.amount_total,
                am.move_type,
                am.state,
                am.create_date,
                am.create_uid,
                rp.id as partner_id,
                rp.name as partner_name
            FROM account_move am
            LEFT JOIN res_partner rp ON am.partner_id = rp.id
            WHERE am.state = 'posted'
              AND am.create_date >= %s
            ORDER BY am.id DESC
            LIMIT %s
        """
        
        try:
            moves = self.execute_query(query, (since_date, limit))
            
            # Formata os dados para manter compatibilidade com o formato esperado
            for move in moves:
                # Garante que partner_id está no formato esperado [id, name]
                if move.get('partner_id'):
                    move['partner_id'] = [move['partner_id'], move.get('partner_name', '')]
                else:
                    move['partner_id'] = None
                
                # Garante que create_uid está no formato correto
                if move.get('create_uid'):
                    move['create_uid'] = [move['create_uid'], '']
            
            return moves
        except Exception as e:
            logger.error(f"Erro ao buscar lançamentos recentes: {e}")
            return []
    
    def get_moves_by_date_range(self, start_date: datetime, end_date: datetime, limit: int = 100) -> List[Dict]:
        """
        Busca lançamentos em um intervalo de datas
        
        Args:
            start_date: Data inicial
            end_date: Data final
            limit: Limite de registros
            
        Returns:
            Lista de lançamentos
        """
        query = """
            SELECT 
                am.id,
                am.name,
                am.date,
                am.ref,
                am.amount_total,
                am.move_type,
                am.state,
                am.create_date,
                am.create_uid,
                rp.id as partner_id,
                rp.name as partner_name
            FROM account_move am
            LEFT JOIN res_partner rp ON am.partner_id = rp.id
            WHERE am.create_date >= %s
              AND am.create_date <= %s
            ORDER BY am.id DESC
            LIMIT %s
        """
        
        try:
            moves = self.execute_query(query, (start_date, end_date, limit))
            
            for move in moves:
                if move.get('partner_id'):
                    move['partner_id'] = [move['partner_id'], move.get('partner_name', '')]
                else:
                    move['partner_id'] = None
            
            return moves
        except Exception as e:
            logger.error(f"Erro ao buscar lançamentos por intervalo: {e}")
            return []
    
    def get_moves_by_type(self, move_type: str, state: str = 'posted', limit: int = 100) -> List[Dict]:
        """
        Busca lançamentos por tipo
        
        Args:
            move_type: Tipo de movimento (out_invoice, in_invoice, etc.)
            state: Estado do lançamento (posted, draft, etc.)
            limit: Limite de registros
            
        Returns:
            Lista de lançamentos
        """
        query = """
            SELECT 
                am.id,
                am.name,
                am.date,
                am.ref,
                am.amount_total,
                am.move_type,
                am.state,
                am.create_date,
                am.create_uid,
                rp.id as partner_id,
                rp.name as partner_name
            FROM account_move am
            LEFT JOIN res_partner rp ON am.partner_id = rp.id
            WHERE am.move_type = %s
              AND am.state = %s
            ORDER BY am.id DESC
            LIMIT %s
        """
        
        try:
            moves = self.execute_query(query, (move_type, state, limit))
            
            for move in moves:
                if move.get('partner_id'):
                    move['partner_id'] = [move['partner_id'], move.get('partner_name', '')]
                else:
                    move['partner_id'] = None
            
            return moves
        except Exception as e:
            logger.error(f"Erro ao buscar lançamentos por tipo: {e}")
            return []
    
    def get_move_by_id(self, move_id: int) -> Optional[Dict]:
        """
        Busca um lançamento específico por ID
        
        Args:
            move_id: ID do lançamento
            
        Returns:
            Dicionário com os dados do lançamento ou None
        """
        query = """
            SELECT 
                am.id,
                am.name,
                am.date,
                am.ref,
                am.amount_total,
                am.amount_untaxed,
                am.amount_tax,
                am.move_type,
                am.state,
                am.create_date,
                am.create_uid,
                rp.id as partner_id,
                rp.name as partner_name
            FROM account_move am
            LEFT JOIN res_partner rp ON am.partner_id = rp.id
            WHERE am.id = %s
        """
        
        try:
            results = self.execute_query(query, (move_id,))
            if results:
                move = results[0]
                if move.get('partner_id'):
                    move['partner_id'] = [move['partner_id'], move.get('partner_name', '')]
                return move
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar lançamento {move_id}: {e}")
            return None
    
    def test_connection(self) -> bool:
        """
        Testa a conexão com o banco de dados
        
        Returns:
            True se conectado, False caso contrário
        """
        try:
            if self.conn is None:
                self._connect()
            
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            return True
        except Exception as e:
            logger.error(f"Erro ao testar conexão: {e}")
            return False
    
    def close(self):
        """Fecha a conexão com o banco de dados"""
        if self.conn:
            self.conn.close()
            logger.info("Conexão PostgreSQL fechada")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()



