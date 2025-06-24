from typing import List, Dict
from banco.conexao_db import Conexao
from model.livro import Livro
from psycopg2 import IntegrityError


def listar_todos() -> List[Dict]:
    """
    Busca e retorna todos os livros cadastrados no banco.

    Raises:
        RuntimeError: em caso de erro genérico de banco.

    Returns:
        List[Dict]: lista de livros.
    """
    sql = "SELECT id_livro, nome_livro, ano, nome_editora, isbn, id_pesquisador FROM livro"
    conn = Conexao.obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            cols = [d[0] for d in cursor.description]
            rows = cursor.fetchall()
        return [dict(zip(cols, row)) for row in rows]
    except Exception as e:
        raise RuntimeError(f"Erro ao listar livros: {e}")
    finally:
        Conexao.devolver_conexao(conn)


def salvar_novo_livro(livro: Livro) -> Dict:
    """
    Insere um novo livro no banco.

    Args:
        livro (Livro): dados do livro.

    Raises:
        ValueError: em caso de conflito (ex: ISBN duplicado).
        RuntimeError: em outros erros de banco.

    Returns:
        Dict: livro inserido, incluindo id.
    """
    sql = (
        "INSERT INTO livro (nome_livro, ano, nome_editora, isbn, id_pesquisador) "
        "VALUES (%s, %s, %s, %s, %s) "
        "RETURNING id_livro, nome_livro, ano, nome_editora, isbn, id_pesquisador"
    )
    conn = Conexao.obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (
                livro.nome_livro,
                livro.ano,
                livro.nome_editora,
                livro.isbn,
                livro.id_pesquisador
            ))
            cols = [d[0] for d in cursor.description]
            row = cursor.fetchone()
        conn.commit()
        return dict(zip(cols, row))
    except IntegrityError as e:
        conn.rollback()
        raise ValueError(f"Conflito ao salvar livro: {e.diag.message_detail or e}")
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Erro ao salvar livro: {e}")
    finally:
        Conexao.devolver_conexao(conn)


def atualizar_por_id(livro: Livro) -> Dict:
    """
    Atualiza um livro existente pelo ID.

    Raises:
        LookupError: se não encontrar o livro.
        RuntimeError: em outros erros de banco.

    Returns:
        Dict: livro atualizado.
    """
    sql = (
        "UPDATE livro SET nome_livro=%s, ano=%s, nome_editora=%s, isbn=%s, id_pesquisador=%s "
        "WHERE id_livro=%s "
        "RETURNING id_livro, nome_livro, ano, nome_editora, isbn, id_pesquisador"
    )
    conn = Conexao.obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (
                livro.nome_livro,
                livro.ano,
                livro.nome_editora,
                livro.isbn,
                livro.id_pesquisador,
                livro.id_livro
            ))
            if cursor.rowcount == 0:
                raise LookupError("Livro não encontrado para atualização.")
            cols = [d[0] for d in cursor.description]
            row = cursor.fetchone()
        conn.commit()
        return dict(zip(cols, row))
    except LookupError:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Erro ao atualizar livro: {e}")
    finally:
        Conexao.devolver_conexao(conn)


def apagar_por_id(id_livro: str) -> None:
    """
    Remove um livro pelo ID.

    Raises:
        LookupError: se não encontrar o livro.
        RuntimeError: em outros erros.
    """
    sql = "DELETE FROM livro WHERE id_livro=%s"
    conn = Conexao.obter_conexao()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (id_livro,))
            if cursor.rowcount == 0:
                raise LookupError("Livro não encontrado para exclusão.")
        conn.commit()
    except LookupError:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Erro ao apagar livro: {e}")
    finally:
        Conexao.devolver_conexao(conn)