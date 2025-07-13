CREATE EXTENSION IF NOT EXISTS unaccent;
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
	foto_sincronizada BOOLEAN NOT NULL DEFAULT FALSE,
	id_orcid VARCHAR(19),
	id_lattes VARCHAR(16) NOT NULL,
	id_instituicao UUID NOT NULL,
	PRIMARY KEY (id_pesquisador),
	CONSTRAINT fk_pesquisador_instituicao
		FOREIGN KEY (id_instituicao)
		REFERENCES instituicao (id_instituicao)
		ON UPDATE NO ACTION 
		ON DELETE NO ACTION
);

CREATE TABLE IF NOT EXISTS artigo (
	id_artigo UUID NOT NULL DEFAULT uuid_generate_v4(),
	nome TEXT NOT NULL,
	ano INTEGER NOT NULL, 
	doi VARCHAR(100),
	resumo TEXT,
	resumo_sincronizado BOOLEAN NOT NULL DEFAULT FALSE,
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