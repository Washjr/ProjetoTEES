# Importa a conexão Singleton do banco de dados
from banco import conexao_singleton as cs

# Obtém uma instância de conexão com o banco de dados
conexao = cs.Conexao().get_conexao()

# Função para salvar um novo pesquisador no banco de dados
def salvar_novo_pesquisador(nome: str, lattes_id: str, articles: int, abstract: str) -> str:
    # SQL para inserir um novo registro na tabela "pesquisadores"
    sql = """
            INSERT INTO pesquisadores (lattes_id, nome, articles, abstract)
            VALUES (%s, %s, %s, %s)
        """
    
    try:
        # Utiliza a conexão para abrir um cursor e executar o SQL
        with conexao.cursor() as cursor:
            cursor.execute(sql, (lattes_id, nome, articles, abstract))
            # Confirma a transação no banco
            conexao.commit()
            
            return "Novo pesquisador salvo com sucesso!"
    except Exception as e:
        # Se ocorrer uma exceção, reverte a transação
        conexao.rollback()
        return f"Erro ao salvar: {e}"
    
# Função para listar todos os pesquisadores do banco de dados
def listar_todos() -> str:
    # SQL para selecionar todos os registros da tabela "pesquisadores"
    sql: str = "SELECT * FROM pesquisadores"
    
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
def atualizar_por_id(nome: str, pesquisadores_id: str, lattes_id: str, articles: int, abstract: str) -> str:
    # SQL para atualizar os dados de um pesquisador específico
    sql = """
            UPDATE pesquisadores
            SET nome = %s, pesquisadores_id = %s, articles = %s, abstract = %s
            WHERE lattes_id = %s
        """
    
    try:
        # Utiliza a conexão para abrir um cursor e executar o SQL
        with conexao.cursor() as cursor:
            cursor.execute(sql, (nome, pesquisadores_id, articles, abstract, lattes_id))
            
            if (cursor.rowcount < 0):
                raise Exception()
            
            # Confirma a transação no banco
            conexao.commit()
            
            return "Pesquisador atualizado com sucesso!"
    except Exception as e:
        # Se ocorrer uma exceção, reverte a transação
        conexao.rollback()
        return f"Erro ao atualizar pesquisador: {e}"

# Função para apagar um pesquisador do banco de dados com base no "lattes_id"
def apagar_por_lattes_id(lattes_id: str) -> str:
    
    # SQL para excluir um pesquisador específico com base no "lattes_id"

    sql = """
            DELETE FROM pesquisadores
            WHERE lattes_id = %s
        """
    
    try:
        # Utiliza a conexão para abrir um cursor e executar o SQL
        with conexao.cursor() as cursor:
            
            cursor.execute(sql, (lattes_id, ))
            
            if (cursor.rowcount > 0):
                # Confirma a transação no banco
                conexao.commit()
            else:
                raise Exception()
            
            return "Pesquisador apagado com sucesso!"
    except Exception as e:
        # Se ocorrer uma exceção, reverte a transação
        conexao.rollback()
        return f"Erro ao apagar pesquisador. Pesquisador inexistente ou ID inválido."