from typing import List, Dict
from banco.conexao_db import Conexao
from model.patente import Patente
from psycopg2 import IntegrityError


def listar_todas() -> List[Dict]:
    """
    Busca e retorna todas as patentes cadastradas no banco.

    Raises:
        RuntimeError: em caso de erro genérico de banco.

    Returns:
        List[Dict]: lista de patentes.
    """
    sql = (
        "SELECT id_patente, nome, ano, data_concessao, id_pesquisador "
        "FROM patente"
    )
    conn = Conexao.obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            cols = [d[0] for d in cursor.description]
            rows = cursor.fetchall()
        return [dict(zip(cols, row)) for row in rows]
    except Exception as e:
        raise RuntimeError(f"Erro ao listar patentes: {e}")
    finally:
        Conexao.devolver_conexao(conn)


def salvar_nova(patente: Patente) -> Dict:
    """
    Insere uma nova patente no banco.

    Args:
        patente (Patente): dados da patente para salvar.

    Raises:
        ValueError: em caso de conflito de integridade.
        RuntimeError: em outros erros de banco.

    Returns:
        Dict: patente inserida, incluindo id.
    """
    sql = (
        "INSERT INTO patente (nome, ano, data_concessao, id_pesquisador) "
        "VALUES (%s, %s, %s, %s) "
        "RETURNING id_patente, nome, ano, data_concessao, id_pesquisador"
    )
    conn = Conexao.obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (
                patente.nome,
                patente.ano,
                patente.data_concessao,
                patente.id_pesquisador
            ))
            cols = [d[0] for d in cursor.description]
            row = cursor.fetchone()
        conn.commit()
        return dict(zip(cols, row))
    except IntegrityError as e:
        conn.rollback()
        raise ValueError(f"Conflito ao salvar patente: {e.diag.message_detail or e}")
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Erro ao salvar patente: {e}")
    finally:
        Conexao.devolver_conexao(conn)


def atualizar_por_id(patente: Patente) -> Dict:
    """
    Atualiza uma patente existente pelo ID.

    Args:
        patente (Patente): objeto contendo id_patente e novos valores.

    Raises:
        LookupError: se não encontrar a patente.
        RuntimeError: em outros erros de banco.

    Returns:
        Dict: patente atualizada.
    """
    sql = (
        "UPDATE patente SET nome=%s, ano=%s, data_concessao=%s, id_pesquisador=%s "
        "WHERE id_patente=%s "
        "RETURNING id_patente, nome, ano, data_concessao, id_pesquisador"
    )
    conn = Conexao.obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (
                patente.nome,
                patente.ano,
                patente.data_concessao,
                patente.id_pesquisador,
                patente.id_patente
            ))
            if cursor.rowcount == 0:
                raise LookupError("Patente não encontrada para atualização.")
            cols = [d[0] for d in cursor.description]
            row = cursor.fetchone()
        conn.commit()
        return dict(zip(cols, row))
    except LookupError:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Erro ao atualizar patente: {e}")
    finally:
        Conexao.devolver_conexao(conn)


def apagar_por_id(id_patente: str) -> None:
    """
    Remove uma patente pelo ID.

    Args:
        id_patente (str): UUID da patente.

    Raises:
        LookupError: se não encontrar a patente.
        RuntimeError: em outros erros.
    """
    sql = "DELETE FROM patente WHERE id_patente=%s"
    conn = Conexao.obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (id_patente,))
            if cursor.rowcount == 0:
                raise LookupError("Patente não encontrada para exclusão.")
        conn.commit()
    except LookupError:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Erro ao apagar patente: {e}")
    finally:
        Conexao.devolver_conexao(conn)