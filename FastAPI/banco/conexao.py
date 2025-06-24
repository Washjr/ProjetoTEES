import threading
import logging
from psycopg2.pool import SimpleConnectionPool
from psycopg2 import OperationalError
from pydantic import BaseSettings

# Configuração de ambiente para credenciais do banco (.env)
class Configuracoes(BaseSettings):
    DB_HOST: str
    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    DB_PORT: int = 5445

    class Config:
        env_file = ".env"

configuracoes = Configuracoes()

# Logger do módulo de conexão
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Conexao:
    """
    Gerencia um pool de conexões PostgreSQL usando psycopg2.
    Singleton thread-safe.
    """

    _pool: SimpleConnectionPool = None
    _trava = threading.Lock()
    
    @classmethod
    def inicializar_pool(cls, min_conexoes: int = 1, max_conexoes: int = 10):
        """
        Inicializa o pool de conexões se ainda não existir.
        """
        with cls._trava:
            if cls._pool is None:
                try:                    
                    cls._pool = SimpleConnectionPool(
                        min_conexoes, max_conexoes,
                        host=configuracoes.DB_HOST,
                        database=configuracoes.DB_NAME,
                        user=configuracoes.DB_USER,
                        password=configuracoes.DB_PASS,
                        port=configuracoes.DB_PORT
                    )
                    logger.info("Pool de conexões criado: %d a %d conexões.", min_conexoes, max_conexoes)

                except OperationalError as erro:
                    logger.error("Falha ao criar pool de conexões: %s", erro)
                    raise RuntimeError("Não foi possível inicializar o pool de conexões.") from erro
                
        return cls._pool

    @classmethod
    def obter_conexao(cls):
        """
        Retorna uma conexão do pool. Inicializa o pool se necessário.
        """
        if cls._pool is None:
            cls.inicializar_pool()
        try:
            conexao = cls._pool.getconn()
            logger.debug("Conexão obtida do pool.")
            return conexao
        except Exception as erro:
            logger.error("Erro ao obter conexão do pool: %s", erro)
            raise

    @classmethod
    def devolver_conexao(cls, conexao):
        """
        Devolve a conexão ao pool.
        """
        if cls._pool and conexao:
            cls._pool.putconn(conexao)
            logger.debug("Conexão devolvida ao pool.")

    @classmethod
    def fechar_todas_conexoes(cls):
        """
        Fecha todas as conexões do pool.
        """
        if cls._pool:
            cls._pool.closeall()
            logger.info("Todas as conexões do pool foram fechadas.")