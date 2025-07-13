# Projeto TEES

Este repositório contém o backend (PostgreSQL com pgvector) e o frontend (Next.js) do Projeto Final da Discicplina TEES.

## Configuração Inicial

### 1. Inicie o Docker Desktop

Certifique-se de que o Docker Desktop está em execução antes de prosseguir.

---

### 2. Suba o banco de dados (PostgreSQL)

Navegue até o diretório `PostgreSQL`:

```cd PostgreSQL```

Construa a imagem Docker:

```docker build -t projeto-tees .```

Execute o container:

```docker run -d --name projeto-tees-container -p 5445:5432 projeto-tees```

Isso criará e executará um container PostgreSQL na porta 5445. É possivel visualiza-lo pelo HeidiSQL a partir das configuraçoes definidas no Dockerfile

---

 ## 3. Inicie o Frontend (Next.js)

 Navegue até o diretório `Next.js`:

```cd ..\Next.js```

Instale as dependências:

```npm install```
Inicie o servidor de desenvolvimento:

```npm run dev```
O frontend estará disponível em: http://localhost:3000