import threading
import logging
from psycopg2.pool import SimpleConnectionPool
from psycopg2 import OperationalError

from config import configuracoes

# Logger do módulo de conexão
logger = logging.getLogger(__name__)

class Conexao:
    """
    Gerencia um pool de conexões PostgreSQL usando psycopg2.
    Singleton thread-safe com verificação de conexões ativas.
    """

    _pool: SimpleConnectionPool = None
    _trava = threading.Lock()
    
    @classmethod
    def inicializar_pool(cls):
        """
        Inicializa o pool de conexões se ainda não existir.
        """
        with cls._trava:
            if cls._pool is None:
                try:                    
                    cls._pool = SimpleConnectionPool(
                        configuracoes.DB_MIN_CONEXOES,
                        configuracoes.DB_MAX_CONEXOES,
                        host=configuracoes.DB_HOST,
                        database=configuracoes.DB_NAME,
                        user=configuracoes.DB_USER,
                        password=configuracoes.DB_PASS,
                        port=configuracoes.DB_PORT
                    )                    
                    logger.info(
                        "Pool de conexões criado: %d a %d conexões.",
                        configuracoes.DB_MIN_CONEXOES,
                        configuracoes.DB_MAX_CONEXOES
                    )

                except OperationalError as erro:
                    logger.error("Falha ao criar pool de conexões: %s", erro)
                    raise RuntimeError("Não foi possível inicializar o pool de conexões.") from erro
                
        return cls._pool

    @classmethod
    def obter_conexao(cls, max_tentativas: int = 3):
        """
        Retorna uma conexão do pool. Inicializa o pool se necessário.
        Se a conexão estiver fechada, descarta e obtém outra até max_tentativas.
        """
        if cls._pool is None:
            cls.inicializar_pool()

        tentativa = 0
        while tentativa < max_tentativas:
            tentativa += 1
            try:
                conexao = cls._pool.getconn()
                if getattr(conexao, 'closed', False):
                    logger.warning(
                        "Tentativa %d: conexão fechada detectada, descartando e obtendo nova.",
                        tentativa
                    )
                    cls._pool.putconn(conexao, close=True)
                    continue
                logger.debug(
                    "Conexão ativa obtida no pool na tentativa %d.",
                    tentativa
                )
                return conexao
            except Exception as erro:
                logger.error(
                    "Erro ao obter conexão do pool na tentativa %d: %s",
                    tentativa, erro
                )
                
        # Se não obteve conexão válida em max_tentativas
        raise RuntimeError(
            f"Não foi possível obter conexão ativa após {max_tentativas} tentativas."
        )

    @classmethod
    def devolver_conexao(cls, conexao, fechar: bool = False):
        """
        Devolve a conexão ao pool.
        Se fechar=True, descarta a conexão.
        """
        if cls._pool and not cls._pool.closed and conexao:
            try:
                cls._pool.putconn(conexao, close=fechar)
                logger.debug("Conexão devolvida ao pool: fechar=%s", fechar)
            except Exception as e:
                logger.warning("Falha ao devolver conexão ao pool: %s", str(e))
        else:
            logger.debug("Pool fechado ou conexão ausente. Conexão não devolvida.")

    @classmethod
    def fechar_todas_conexoes(cls):
        """
        Fecha todas as conexões do pool e limpa o recurso.
        """
        if cls._pool:
            cls._pool.closeall()
            logger.info("Todas as conexões do pool foram fechadas.")