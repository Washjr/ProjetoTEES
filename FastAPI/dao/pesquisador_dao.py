from typing import List
from banco.conexao_singleton import Conexao
from model.pesquisador import Pesquisador
from psycopg2 import IntegrityError

# Obtém uma instância de conexão com o banco de dados
conexao = Conexao().get_conexao()

def listar_todos() -> List[Pesquisador]:
    """
    Busca e retorna todos os pesquisadores cadastrados no banco.

    Raises:
        RuntimeError: se ocorrer erro genérico de banco de dados.

    Returns:
        List[Pesquisador]: lista de dicionários representando pesquisadores.
    """  
    sql: str = "SELECT id_pesquisador, nome, grau_academico, resumo, citacoes, id_orcid, id_lattes FROM pesquisador"
    
    try:
        with conexao.cursor() as cursor:
            cursor.execute(sql)
            colunas = [desc[0] for desc in cursor.description]
            resultado = cursor.fetchall()
    except Exception as e:
        raise RuntimeError(f"Erro ao listar pesquisadores: {e}")

    return [dict(zip(colunas, linha)) for linha in resultado]


def salvar_novo_pesquisador(pesquisador:Pesquisador) -> Pesquisador:
    """
    Insere um novo pesquisador no banco de dados.

    Args:
        pesquisador (Pesquisador): objeto contendo os dados do pesquisador a ser salvo.

    Raises:
        ValueError: se ocorrer conflito de integridade (ex: chave duplicada).
        RuntimeError: para outros erros de banco de dados.
    """
    sql = """
        INSERT INTO pesquisador (nome, grau_academico, resumo, citacoes, id_orcid, id_lattes)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id_pesquisador, nome, grau_academico, resumo, citacoes, id_orcid, id_lattes
    """
    try:        
        with conexao.cursor() as cursor:
            cursor.execute(sql, (
                pesquisador.nome, 
                pesquisador.grau_academico, 
                pesquisador.resumo, 
                pesquisador.citacoes, 
                pesquisador.id_orcid, 
                pesquisador.id_lattes
            ))
            colunas = [desc[0] for desc in cursor.description]
            resultado = cursor.fetchone()
        conexao.commit()            
        return dict(zip(colunas, resultado))

    except IntegrityError as e:
        conexao.rollback()
        raise ValueError(f"Conflito ao salvar pesquisador: {e.diag.message_detail or e}")          
    except Exception as e:
        conexao.rollback()
        raise RuntimeError(f"Erro ao salvar pesquisador: {e}")
    

def atualizar_por_id(pesquisador:Pesquisador) -> Pesquisador:
    """
    Atualiza um pesquisador existente com base no seu ID.

    Args:
        pesquisador (Pesquisador): objeto contendo dados atualizados; deve ter id_pesquisador.

    Raises:
        LookupError: se não encontrar o pesquisador para atualizar.
        RuntimeError: para outros erros de banco de dados.
    """

    sql = """
        UPDATE pesquisador
        SET nome=%s, grau_academico=%s, resumo=%s, citacoes=%s, id_orcid=%s, id_lattes=%s
        WHERE id_pesquisador=%s
        RETURNING id_pesquisador, nome, grau_academico, resumo, citacoes, id_orcid, id_lattes
    """
    try:        
        with conexao.cursor() as cursor:
            cursor.execute(sql, (
                pesquisador.nome, 
                pesquisador.grau_academico, 
                pesquisador.resumo, 
                pesquisador.citacoes, 
                pesquisador.id_orcid, 
                pesquisador.id_lattes,
                pesquisador.id_pesquisador
            ))
            if cursor.rowcount == 0:
                raise LookupError("Pesquisador não encontrado para atualização.")
            colunas = [d[0] for d in cursor.description]
            resultado = cursor.fetchone()  
        conexao.commit()            
        return dict(zip(colunas, resultado))   

    except LookupError:
        conexao.rollback()
        raise
    except Exception as e:
        conexao.rollback()
        raise RuntimeError(f"Erro ao atualizar pesquisador: {e}")


def apagar_por_id(id_pesquisador: str) -> None:
    """
    Remove um pesquisador do banco de dados dado seu ID.

    Args:
        id_pesquisador (str): UUID do pesquisador a ser excluído.

    Raises:
        LookupError: se não encontrar o pesquisador para exclusão.
        RuntimeError: para outros erros de banco de dados.
    """

    sql = """
            DELETE FROM pesquisador
            WHERE id_pesquisador=%s
        """
    try:        
        with conexao.cursor() as cursor:            
            cursor.execute(sql, (id_pesquisador,))            
            if cursor.rowcount == 0:
                raise LookupError("Pesquisador não encontrado para exclusão.") 
        conexao.commit()            

    except LookupError:
        conexao.rollback()
        raise
    except Exception as e:        
        conexao.rollback()
        raise RuntimeError(f"Erro ao apagar pesquisador: {e}")