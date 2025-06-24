import logging
from banco.conexao_db import Conexao

# Logging
logger = logging.getLogger(__name__)

# Script para remoção de tabelas e extensões
script_sql = """
DROP TABLE IF EXISTS software;
DROP TABLE IF EXISTS patente;
DROP TABLE IF EXISTS livro;
DROP TABLE IF EXISTS artigo;
DROP TABLE IF EXISTS periodico;
DROP TABLE IF EXISTS instituicao;
DROP TABLE IF EXISTS pesquisador;
DROP EXTENSION IF EXISTS "uuid-ossp";
"""

def main():
    conexao = Conexao.obter_conexao()
    try:
        with conexao.cursor() as cursor:
            logger.info("Executando script de teardown no banco de dados...")
            cursor.execute(script_sql)
            conexao.commit()
            logger.info("Tabelas e extensões removidas com sucesso!")
    except Exception as e:
        conexao.rollback()
        logger.exception("Erro ao executar script SQL")
    finally:
        Conexao.devolver_conexao(conexao)
        Conexao.fechar_todas_conexoes()
        logger.info("Conexões com o banco encerradas.")

if __name__ == "__main__":
    main()