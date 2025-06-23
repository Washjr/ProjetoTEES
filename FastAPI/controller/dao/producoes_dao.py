# Importa a conexão Singleton do banco de dados
from typing import Dict, List
from banco import conexao_singleton as cs
from model.artigo import Artigo

# Obtém uma instância de conexão com o banco de dados
conexao = cs.Conexao().get_conexao()

# Função para salvar um novo pesquisador no banco de dados
def salvar_nova_producao(producao:Artigo) -> str:
    # SQL para inserir um novo registro na tabela "pesquisadores"
    sql = """
            INSERT INTO producoes (nomeartigo, anoartigo, pesquisadores_id, issn, doi, qualis, nomepesquisador)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
    
    try:
        # Utiliza a conexão para abrir um cursor e executar o SQL
        with conexao.cursor() as cursor:
            cursor.execute(sql, (producao.nomeartigo, producao.anoartigo, producao.pesquisadores_id, producao.issn, producao.doi, producao.qualis, producao.nomepesquisador))
            # Confirma a transação no banco
            conexao.commit()
            
            return "Nova Produção salva com sucesso!"
    except Exception as e:
        # Se ocorrer uma exceção, reverte a transação
        conexao.rollback()
        return f"Erro ao salvar: {e}"
    
# Função para listar todos os pesquisadores do banco de dados
def listar_todos() -> List[Dict]:
    # SQL para selecionar todos os registros da tabela "pesquisadores"
    sql: str = "SELECT * FROM producoes"
    
    # Utiliza a conexão para abrir um cursor e executar o SQL
    with conexao.cursor() as cursor:
        cursor.execute(sql)
        # Obtém todos os resultados da consulta
        resultado = cursor.fetchall()
        
        # Cria uma lista das colunas retornadas pela consulta
        colunas = [desc[0] for desc in cursor.description]
        # Mapeia os resultados em dicionários com chave-valor
        dados = [dict(zip(colunas, linha)) for linha in resultado]
        
        return dados

# Função para atualizar um pesquisador no banco de dados com base no "lattes_id"
def atualizar_por_id(producao:Artigo) -> str:
    # SQL para atualizar os dados de um pesquisador específico
    sql = """
            UPDATE producoes
            SET nomeartigo = %s, issn=%s, anoartigo=%s, doi=%s, qualis=%s, nomepesquisador=%s
            WHERE producoes_id = %s
        """
    
    try:
        # Utiliza a conexão para abrir um cursor e executar o SQL
        with conexao.cursor() as cursor:
            cursor.execute(sql, ( producao.nomeartigo, producao.issn, producao.anoartigo, producao.doi, producao.qualis, producao.nomepesquisador, producao.producoes_id))
            
            if (cursor.rowcount < 0):
                raise Exception()
            
            # Confirma a transação no banco
            conexao.commit()
            
            return "Produção atualizada com sucesso!"
    except Exception as e:
        # Se ocorrer uma exceção, reverte a transação
        conexao.rollback()
        return f"Erro ao atualizar produção: {e}"

# Função para apagar um pesquisador do banco de dados com base no "lattes_id"
def apagar_por_producao_id(producao_id: str) -> str:
    
    # SQL para excluir um pesquisador específico com base no "lattes_id"

    sql = """
            DELETE FROM producoes
            WHERE producoes_id = %s
        """
    
    try:
        # Utiliza a conexão para abrir um cursor e executar o SQL
        with conexao.cursor() as cursor:
            
            cursor.execute(sql, (producao_id, ))
            
            if (cursor.rowcount > 0):
                # Confirma a transação no banco
                conexao.commit()
            else:
                raise Exception()
            
            return "Produção apagada com sucesso!"
    except Exception as e:
        # Se ocorrer uma exceção, reverte a transação
        conexao.rollback()
        return f"Erro ao apagar produção. Produção inexistente ou ID inválido."