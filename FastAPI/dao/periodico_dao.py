from typing import List, Dict
from banco.conexao_db import Conexao
from model.periodico import Periodico
from psycopg2 import IntegrityError
import logging

logger = logging.getLogger(__name__)


def listar_todos() -> List[Dict]:
    """
    Busca e retorna todos os periódicos cadastrados no banco.

    Raises:
        RuntimeError: se ocorrer erro genérico de banco de dados.

    Returns:
        List[Dict]: lista de dicionários representando periódicos.
    """
    sql = "SELECT id_periodico, nome, qualis, issn FROM periodico"
    conn = Conexao.obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            cols = [d[0] for d in cursor.description]
            rows = cursor.fetchall()
        return [dict(zip(cols, row)) for row in rows]

    except Exception as e:
        logger.exception("Erro ao listar periódicos")
        raise RuntimeError(f"Erro ao listar periódicos: {e}")
    finally:
        Conexao.devolver_conexao(conn)


def salvar_novo(periodico: Periodico) -> Dict:
    """
    Insere um novo periódico no banco de dados.

    Args:
        periodico (Periodico): dados do periódico para salvar.

    Raises:
        ValueError: em caso de conflito de integridade (e.g., ISSN duplicado).
        RuntimeError: para outros erros de banco.

    Returns:
        Dict: dicionário representando o periódico inserido.
    """
    sql = (
        "INSERT INTO periodico (nome, qualis, issn) VALUES (%s, %s, %s) "
        "RETURNING id_periodico, nome, qualis, issn"
    )
    conn = Conexao.obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (
                periodico.nome,
                periodico.qualis,
                periodico.issn
            ))
            cols = [d[0] for d in cursor.description]
            row = cursor.fetchone()
        conn.commit()
        return dict(zip(cols, row))

    except IntegrityError as e:
        conn.rollback()
        raise ValueError(f"Conflito ao salvar periódico: {e.diag.message_detail or e}")
    except Exception as e:
        conn.rollback()
        logger.exception("Erro ao salvar periódico")
        raise RuntimeError(f"Erro ao salvar periódico: {e}")
    finally:
        Conexao.devolver_conexao(conn)


def atualizar_por_id(periodico: Periodico) -> Dict:
    """
    Atualiza um periódico existente pelo ID.

    Args:
        periodico (Periodico): objeto contendo id_periodico e novos valores.

    Raises:
        LookupError: se não encontrar o periódico.
        RuntimeError: para outros erros de banco.

    Returns:
        Dict: periódico atualizado.
    """
    sql = (
        "UPDATE periodico SET nome=%s, qualis=%s, issn=%s "
        "WHERE id_periodico=%s "
        "RETURNING id_periodico, nome, qualis, issn"
    )
    conn = Conexao.obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (
                periodico.nome,
                periodico.qualis,
                periodico.issn,
                periodico.id_periodico
            ))
            if cursor.rowcount == 0:
                raise LookupError("Periódico não encontrado para atualização.")
            cols = [d[0] for d in cursor.description]
            row = cursor.fetchone()
        conn.commit()
        return dict(zip(cols, row))

    except LookupError:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        logger.exception("Erro ao atualizar periódico")
        raise RuntimeError(f"Erro ao atualizar periódico: {e}")
    finally:
        Conexao.devolver_conexao(conn)


def apagar_por_id(id_periodico: str) -> None:
    """
    Remove um periódico do banco pelo ID.

    Args:
        id_periodico (str): UUID do periódico.

    Raises:
        LookupError: se não encontrar o periódico.
        RuntimeError: para outros erros.
    """
    sql = "DELETE FROM periodico WHERE id_periodico=%s"
    conn = Conexao.obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (id_periodico,))
            if cursor.rowcount == 0:
                raise LookupError("Periódico não encontrado para exclusão.")
        conn.commit()
    except LookupError:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        logger.exception("Erro ao apagar periódico")
        raise RuntimeError(f"Erro ao apagar periódico: {e}")
    finally:
        Conexao.devolver_conexao(conn)