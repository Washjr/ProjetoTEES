import logging
from banco.conexao_db import Conexao

# Logging
logger = logging.getLogger(__name__)

# Script para criar as tabelas e extensões
script_sql_criacao = """
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS instituicao (
    id_instituicao UUID NOT NULL DEFAULT uuid_generate_v4(),
    nome VARCHAR(200) NOT NULL,
    PRIMARY KEY (id_instituicao)
);

CREATE TABLE IF NOT EXISTS periodico (
    id_periodico UUID NOT NULL DEFAULT uuid_generate_v4(),
    nome VARCHAR(200) NOT NULL,
    qualis VARCHAR(2) NOT NULL,
    issn VARCHAR(8) NOT NULL,
    PRIMARY KEY (id_periodico)
);

CREATE TABLE IF NOT EXISTS pesquisador (
    id_pesquisador UUID NOT NULL DEFAULT uuid_generate_v4(),
    nome VARCHAR(200) NOT NULL,
    grau_academico VARCHAR(30) NOT NULL,
    resumo TEXT,
    citacoes TEXT,
    id_orcid VARCHAR(19),
    id_lattes VARCHAR(16) NOT NULL,
    PRIMARY KEY (id_pesquisador)
);

CREATE TABLE IF NOT EXISTS artigo (
    id_artigo UUID NOT NULL DEFAULT uuid_generate_v4(),
    nome TEXT NOT NULL,
    ano INTEGER NOT NULL, 
    doi VARCHAR(100),
    id_pesquisador UUID NOT NULL,
    id_periodico UUID NOT NULL,
    PRIMARY KEY (id_artigo), 
    CONSTRAINT fk_artigo_pesquisador 
        FOREIGN KEY (id_pesquisador)
        REFERENCES pesquisador (id_pesquisador) 
        ON UPDATE NO ACTION 
        ON DELETE NO ACTION,
    CONSTRAINT fk_artigo_periodico
        FOREIGN KEY (id_periodico)
        REFERENCES periodico (id_periodico) 
        ON UPDATE NO ACTION 
        ON DELETE NO ACTION
);

CREATE TABLE IF NOT EXISTS livro (
    id_livro UUID NOT NULL DEFAULT uuid_generate_v4(),
    nome_livro TEXT NOT NULL,
    ano INTEGER NOT NULL,
    nome_editora TEXT, 
    isbn VARCHAR(13) NOT NULL,
    id_pesquisador UUID NOT NULL,
    PRIMARY KEY (id_livro), 
    CONSTRAINT fk_livro_pesquisador 
        FOREIGN KEY (id_pesquisador)
        REFERENCES pesquisador (id_pesquisador) 
        ON UPDATE NO ACTION 
        ON DELETE NO ACTION
);
    
CREATE TABLE IF NOT EXISTS patente (
    id_patente UUID NOT NULL DEFAULT uuid_generate_v4(),
    nome TEXT NOT NULL,
    ano INTEGER NOT NULL,
    data_concessao DATE, 
    id_pesquisador UUID NOT NULL,
    PRIMARY KEY (id_patente), 
    CONSTRAINT fk_patente_pesquisador 
        FOREIGN KEY (id_pesquisador)
        REFERENCES pesquisador (id_pesquisador) 
        ON UPDATE NO ACTION 
        ON DELETE NO ACTION
);
    
CREATE TABLE IF NOT EXISTS software (
    id_software UUID NOT NULL DEFAULT uuid_generate_v4(),
    nome TEXT NOT NULL,
    ano INTEGER NOT NULL,
    plataforma TEXT,
    finalidade TEXT,
    id_pesquisador UUID NOT NULL,
    PRIMARY KEY (id_software), 
    CONSTRAINT fk_software_pesquisador 
        FOREIGN KEY (id_pesquisador)
        REFERENCES pesquisador (id_pesquisador) 
        ON UPDATE NO ACTION 
        ON DELETE NO ACTION
);
"""

# Script para inserir dados nas tabelas
script_sql_insercao = """
-- Instituições
INSERT INTO instituicao (nome) VALUES
('Universidade de São Paulo'),
('Universidade Federal da Bahia')
ON CONFLICT DO NOTHING;

-- Periódicos
INSERT INTO periodico (nome, qualis, issn) VALUES
('Revista Brasileira de Ciência', 'A1', '1234-5678'),
('Journal of Data Science', 'B1', '2345-6789')
ON CONFLICT DO NOTHING;

-- Pesquisadores
INSERT INTO pesquisador (nome, grau_academico, resumo, citacoes, id_orcid, id_lattes) VALUES
('Ana Maria Silva', 'Doutor', 'Pesquisa em biodiversidade', '150', '0000-0001-2345-6789', 'L12345678901234'),
('Carlos Eduardo Santos', 'Mestre', 'Inteligência Artificial', '200', '0000-0002-3456-7890', 'L23456789012345')
ON CONFLICT DO NOTHING;

-- Artigos
INSERT INTO artigo (nome, ano, doi, id_pesquisador, id_periodico) VALUES
('Estudo sobre a Biodiversidade na Amazônia', 2022, '10.1234/bioamazonia.2022.001',
(SELECT id_pesquisador FROM pesquisador WHERE nome='Ana Maria Silva'),
(SELECT id_periodico FROM periodico WHERE issn='1234-5678'))
ON CONFLICT DO NOTHING;
"""

def main():
    conexao = Conexao.obter_conexao()
    try:
        with conexao.cursor() as cursor:
            logger.info("Criando tabelas e extensões...")
            cursor.execute(script_sql_criacao)
            conexao.commit()
            logger.info("Tabelas e extensões criadas com sucesso.")

            logger.info("Inserindo dados de exemplo...")
            cursor.execute(script_sql_insercao)
            conexao.commit()
            logger.info("Dados inseridos com sucesso.")

    except Exception as e:
        conexao.rollback()
        logger.exception("Erro ao povoar o banco de dados")

    finally:
        Conexao.devolver_conexao(conexao)
        Conexao.fechar_todas_conexoes()
        logger.info("Conexões com o banco encerradas.")

if __name__ == '__main__':
    main()