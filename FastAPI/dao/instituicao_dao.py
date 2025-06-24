from typing import List, Dict
from banco.conexao_db import Conexao
from model.instituicao import Instituicao
from psycopg2 import IntegrityError

def listar_todas() -> List[Dict]:  
    """
    Busca e retorna todas as instituições cadastradas no banco.

    Raises:
        RuntimeError: se ocorrer erro genérico de banco de dados.

    Returns:
        List[Dict]: lista de dicionários representando instituições.
    """
    sql = "SELECT id_instituicao, nome FROM instituicao"
    conn = Conexao.obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            cols = [d[0] for d in cursor.description]
            rows = cursor.fetchall()
        return [dict(zip(cols, row)) for row in rows]

    except Exception as e:
        raise RuntimeError(f"Erro ao listar instituições: {e}")
    finally:
        Conexao.devolver_conexao(conn)


def salvar_nova(instituicao: Instituicao) -> Dict:
    """
    Insere uma nova instituição no banco de dados.

    Args:
        instituicao (Instituicao): objeto contendo os dados da instituição.

    Raises:
        ValueError: se ocorrer conflito de integridade (ex: nome duplicado).
        RuntimeError: para outros erros de banco de dados.

    Returns:
        Dict: dicionário representando a instituição inserida (com id).  
    """
    sql = (
        "INSERT INTO instituicao (nome) VALUES (%s) "
        "RETURNING id_instituicao, nome"
    )
    conn = Conexao.obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (instituicao.nome,))
            cols = [d[0] for d in cursor.description]
            row = cursor.fetchone()
        conn.commit()
        return dict(zip(cols, row))

    except IntegrityError as e:
        conn.rollback()
        raise ValueError(f"Conflito ao salvar instituição: {e.diag.message_detail or e}")
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Erro ao salvar instituição: {e}")
    finally:
        Conexao.devolver_conexao(conn)


def atualizar_por_id(inst: Instituicao) -> Dict:
    """
    Atualiza uma instituição existente com base no seu ID.

    Args:
        inst (Instituicao): objeto com id_instituicao e nome.

    Raises:
        LookupError: se não encontrar a instituição para atualização.
        RuntimeError: para outros erros de banco de dados.

    Returns:
        Dict: dicionário representando a instituição atualizada.
    """
    sql = (
        "UPDATE instituicao SET nome=%s "
        "WHERE id_instituicao=%s "
        "RETURNING id_instituicao, nome"
    )
    conn = Conexao.obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (inst.nome, inst.id_instituicao))
            if cursor.rowcount == 0:
                raise LookupError("Instituição não encontrada para atualização.")
            cols = [d[0] for d in cursor.description]
            row = cursor.fetchone()
        conn.commit()
        return dict(zip(cols, row))

    except LookupError:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Erro ao atualizar instituição: {e}")
    finally:
        Conexao.devolver_conexao(conn)


def apagar_por_id(id_instituicao: str) -> None:
    """
    Remove uma instituição do banco de dados dado seu ID.

    Args:
        id_instituicao (str): UUID da instituição a ser excluída.

    Raises:
        LookupError: se não encontrar a instituição para exclusão.
        RuntimeError: para outros erros de banco de dados.
    """
    sql = "DELETE FROM instituicao WHERE id_instituicao=%s"
    conn = Conexao.obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (id_instituicao,))
            if cursor.rowcount == 0:
                raise LookupError("Instituição não encontrada para exclusão.")
        conn.commit()
    except LookupError:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Erro ao apagar instituição: {e}")
    finally:
        Conexao.devolver_conexao(conn)
