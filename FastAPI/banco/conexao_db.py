import threading
import logging
from psycopg2.pool import SimpleConnectionPool
from psycopg2 import OperationalError
from typing import Optional

from config import configuracoes

# Logger do módulo de conexão
logger = logging.getLogger(__name__)

class Conexao:
    """
    Gerencia um pool de conexões PostgreSQL usando psycopg2.
    Singleton thread-safe com verificação de conexões ativas.
    """
    _pool: Optional[SimpleConnectionPool] = None
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

        if cls._pool is None:
            raise RuntimeError("Pool de conexões não foi inicializado corretamente.")

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
                
        raise RuntimeError(
            f"Não foi possível obter conexão ativa após {max_tentativas} tentativas."
        )

    @classmethod
    def devolver_conexao(cls, conexao, fechar: bool = False):
        """
        Devolve a conexão ao pool.
        Se fechar=True, descarta a conexão.
        """
        if not conexao:
            logger.debug("Conexão ausente. Nada a devolver.")
            return
            
        if not cls._pool or cls._pool.closed:
            logger.debug("Pool fechado. Fechando conexão diretamente.")
            try:
                conexao.close()
            except Exception:
                pass  # Ignorar erros ao fechar conexão órfã
            return

        try:
            # Verificar se a conexão está em estado válido
            if hasattr(conexao, 'closed') and conexao.closed:
                logger.warning("Conexão já fechada, forçando descarte")
                fechar = True
            
            # Tentar rollback se houver transação pendente
            if not fechar and hasattr(conexao, 'get_transaction_status'):
                status = conexao.get_transaction_status()
                if status != 0:  # TRANSACTION_STATUS_IDLE
                    logger.warning("Transação pendente detectada, fazendo rollback")
                    conexao.rollback()
            
            cls._pool.putconn(conexao, close=fechar)
            logger.debug("Conexão devolvida ao pool: fechar=%s", fechar)
            
        except Exception as e:
            logger.warning("Falha ao devolver conexão ao pool (%s): %s", type(e).__name__, str(e))
            # Em caso de erro, tentar fechar a conexão diretamente
            try:
                conexao.close()
                logger.debug("Conexão fechada diretamente após erro")
            except Exception:
                logger.error("Falha crítica: não foi possível fechar conexão")

    @classmethod
    def fechar_todas_conexoes(cls):
        """
        Fecha todas as conexões do pool e limpa o recurso.
        """
        if cls._pool:
            cls._pool.closeall()
            logger.info("Todas as conexões do pool foram fechadas.")

    @classmethod
    def get_connection_string(cls) -> str:
        """
        Retorna a string de conexão formatada.
        """
        return (
            f"postgresql://{configuracoes.DB_USER}:{configuracoes.DB_PASS}@"
            f"{configuracoes.DB_HOST}:{configuracoes.DB_PORT}/{configuracoes.DB_NAME}"
        )