from typing import List, Dict
from banco.conexao_db import Conexao
from model.software import Software
from psycopg2 import IntegrityError


def listar_todos() -> List[Dict]:
    """
    Busca e retorna todos os softwares cadastrados no banco.

    Raises:
        RuntimeError: em caso de erro genérico de banco.

    Returns:
        List[Dict]: lista de softwares.
    """
    sql = (
        "SELECT id_software, nome, ano, plataforma, finalidade, id_pesquisador "
        "FROM software"
    )
    conn = Conexao.obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            cols = [d[0] for d in cursor.description]
            rows = cursor.fetchall()
        return [dict(zip(cols, row)) for row in rows]
    except Exception as e:
        raise RuntimeError(f"Erro ao listar softwares: {e}")
    finally:
        Conexao.devolver_conexao(conn)


def salvar_novo(software: Software) -> Dict:
    """
    Insere um novo software no banco.

    Args:
        software (Software): dados do software a inserir.

    Raises:
        ValueError: em caso de conflito de integridade.
        RuntimeError: em outros erros de banco.

    Returns:
        Dict: software inserido, com id.
    """
    sql = (
        "INSERT INTO software (nome, ano, plataforma, finalidade, id_pesquisador) "
        "VALUES (%s, %s, %s, %s, %s) "
        "RETURNING id_software, nome, ano, plataforma, finalidade, id_pesquisador"
    )
    conn = Conexao.obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (
                software.nome,
                software.ano,
                software.plataforma,
                software.finalidade,
                software.id_pesquisador
            ))
            cols = [d[0] for d in cursor.description]
            row = cursor.fetchone()
        conn.commit()
        return dict(zip(cols, row))
    except IntegrityError as e:
        conn.rollback()
        raise ValueError(f"Conflito ao salvar software: {e.diag.message_detail or e}")
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Erro ao salvar software: {e}")
    finally:
        Conexao.devolver_conexao(conn)


def atualizar_por_id(software: Software) -> Dict:
    """
    Atualiza um software existente pelo ID.

    Args:
        software (Software): objeto contendo id_software e valores atualizados.

    Raises:
        LookupError: se não encontrar o software.
        RuntimeError: em outros erros de banco.

    Returns:
        Dict: software atualizado.
    """
    sql = (
        "UPDATE software SET nome=%s, ano=%s, plataforma=%s, finalidade=%s, id_pesquisador=%s "
        "WHERE id_software=%s "
        "RETURNING id_software, nome, ano, plataforma, finalidade, id_pesquisador"
    )
    conn = Conexao.obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (
                software.nome,
                software.ano,
                software.plataforma,
                software.finalidade,
                software.id_pesquisador,
                software.id_software
            ))
            if cursor.rowcount == 0:
                raise LookupError("Software não encontrado para atualização.")
            cols = [d[0] for d in cursor.description]
            row = cursor.fetchone()
        conn.commit()
        return dict(zip(cols, row))
    except LookupError:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Erro ao atualizar software: {e}")
    finally:
        Conexao.devolver_conexao(conn)


def apagar_por_id(id_software: str) -> None:
    """
    Remove um software pelo ID.

    Args:
        id_software (str): UUID do software.

    Raises:
        LookupError: se não encontrar o software.
        RuntimeError: em outros erros.
    """
    sql = "DELETE FROM software WHERE id_software=%s"
    conn = Conexao.obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (id_software,))
            if cursor.rowcount == 0:
                raise LookupError("Software não encontrado para exclusão.")
        conn.commit()
    except LookupError:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Erro ao apagar software: {e}")
    finally:
        Conexao.devolver_conexao(conn)