import conexao_singleton as cs

banco = cs.Conexao().get_conexao()

script_sql = """
    DROP TABLE IF EXISTS producoes;
    DROP TABLE IF EXISTS pesquisadores;
    DROP EXTENSION IF EXISTS "uuid-ossp";
"""

try:
    with banco.cursor() as cursor:
        print("Executando o script SQL...")
        cursor.execute(script_sql)
        banco.commit()  # Confirma as alterações
        print("Tabelas e extensões removidas com sucesso!")
except Exception as e:
    print(f"Erro ao executar script SQL: {e}")
finally:
    if banco:
        banco.close()  # Fecha a conexão para liberar recursos
        print("Conexão com o banco de dados encerrada.")