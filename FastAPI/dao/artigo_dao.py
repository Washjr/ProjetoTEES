from typing import List
from banco.conexao import Conexao
from model.artigo import Artigo
from psycopg2 import IntegrityError

# Obtém uma instância de conexão com o banco de dados
conexao = Conexao().obter_conexao()

def listar_todos() -> List[Artigo]:  
    """
    Busca e retorna todos os artigos cadastrados no banco.

    Raises:
        RuntimeError: se ocorrer erro genérico de banco de dados.

    Returns:
        List[Artigo]: lista de dicionários representando artigos.
    """  

    sql: str = "SELECT id_artigo, nome, ano, doi, id_pesquisador, id_periodico FROM artigo"
    try:
        with conexao.cursor() as cursor:
            cursor.execute(sql)
            colunas = [desc[0] for desc in cursor.description]
            resultados = cursor.fetchall()

    except Exception as e:
        raise RuntimeError(f"Erro ao listar artigos: {e}")

    return [dict(zip(colunas, linha)) for linha in resultados]

def salvar_novo_artigo(artigo:Artigo) -> Artigo:
    """
    Insere um novo artigo no banco de dados.

    Args:
        artigo (Artigo): objeto contendo os dados do artigo a ser salvo.

    Raises:
        ValueError: se ocorrer conflito de integridade (ex: chave duplicada).
        RuntimeError: para outros erros de banco de dados.
    """

    sql = """
        INSERT INTO artigo (nome, ano, doi, id_pesquisador, id_periodico)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id_artigo, nome, ano, doi, id_pesquisador, id_periodico
    """
    try:
        with conexao.cursor() as cursor:
            cursor.execute(sql, (
                artigo.nome, 
                artigo.ano, 
                artigo.doi, 
                artigo.id_pesquisador, 
                artigo.id_periodico
            ))  
            colunas = [desc[0] for desc in cursor.description]
            resultado = cursor.fetchone()
        conexao.commit()
        return dict(zip(colunas, resultado))
    
    except IntegrityError as e:
        conexao.rollback()
        raise ValueError(f"Conflito ao salvar artigo: {e.diag.message_detail or e}")
    except Exception as e:
        conexao.rollback()
        raise RuntimeError(f"Erro ao salvar artigo: {e}")
    
def atualizar_por_id(artigo:Artigo) -> Artigo:
    """
    Atualiza um artigo existente com base no seu ID.

    Args:
        artigo (Artigo): objeto contendo dados atualizados; deve ter id_artigo.

    Raises:
        LookupError: se não encontrar o artigo para atualizar.
        RuntimeError: para outros erros de banco de dados.
    """

    sql = """
        UPDATE artigo
        SET nome=%s, ano=%s, doi=%s, id_pesquisador=%s, id_periodico=%s
        WHERE id_artigo=%s
        RETURNING id_artigo, nome, ano, doi, id_pesquisador, id_periodico
    """
    try:
        with conexao.cursor() as cursor:
            cursor.execute(sql, (
                artigo.nome, 
                artigo.ano, 
                artigo.doi, 
                artigo.id_pesquisador, 
                artigo.id_periodico,
                artigo.id_artigo
            ))     
            if cursor.rowcount == 0:
                raise LookupError("Artigo não encontrado para atualização.")
            colunas = [d[0] for d in cursor.description]
            resultado = cursor.fetchone()  
        conexao.commit() 
        return dict(zip(colunas, resultado))   
     
    except LookupError:
        conexao.rollback()
        raise
    except Exception as e:
        conexao.rollback()
        raise RuntimeError(f"Erro ao atualizar artigo: {e}")

def apagar_por_id(id_artigo: str) -> None:
    """
    Remove um artigo do banco de dados dado seu ID.

    Args:
        id_artigo (str): UUID do artigo a ser excluído.

    Raises:
        LookupError: se não encontrar o artigo para exclusão.
        RuntimeError: para outros erros de banco de dados.
    """

    sql = """
        DELETE FROM artigo
        WHERE id_artigo=%s
    """
    try:        
        with conexao.cursor() as cursor:            
            cursor.execute(sql, (id_artigo,))            
            if cursor.rowcount == 0:
                raise LookupError("Artigo não encontrado para exclusão.")
        conexao.commit()

    except LookupError:
        conexao.rollback()
        raise
    except Exception as e:        
        conexao.rollback()
        raise RuntimeError(f"Erro ao apagar artigo: {e}")