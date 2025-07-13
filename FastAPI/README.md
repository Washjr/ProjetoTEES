# Sistema de Produção Acadêmica - API Backend

Este é o backend da aplicação Sistema de Produção Acadêmica, desenvolvido com FastAPI. A API gerencia pesquisadores, produções científicas (artigos, livros, patentes, software) e instituições.

## 📋 Pré-requisitos

- Python 3.8 ou superior
- PostgreSQL (para o banco de dados)
- Git

## 🚀 Configuração e Instalação

### 1. Clone o repositório (se ainda não fez)

```bash
git clone <url-do-repositorio>
cd ProjetoTEES/FastAPI
```

### 2. Crie e ative o ambiente virtual

No Windows (PowerShell):
```powershell
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
venv\Scripts\activate
```

No Linux/macOS:
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
source venv/bin/activate
```

### 3. Instale as dependências dentro do ambiente criado

```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados

Certifique-se de que o PostgreSQL está instalado e rodando. Configure as credenciais do banco no arquivo de configuração apropriado.

### 5. Execute as migrações/criação das tabelas

Execute o script SQL localizado em `../PostgreSQL/1. Criação das Tabelas.sql` no seu banco PostgreSQL.

## 🏃‍♂️ Executando a aplicação

### Modo de desenvolvimento (com reload automático)

```powershell
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Modo de produção

```powershell
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📚 Documentação da API

Após iniciar o servidor, você pode acessar:

- **Documentação interativa (Swagger)**: http://127.0.0.1:8000/docs
- **Documentação alternativa (ReDoc)**: http://127.0.0.1:8000/redoc
- **Health Check**: http://127.0.0.1:8000/health

## 🛠️ Estrutura do projeto

```
FastAPI/
├── banco/                  # Módulos de conexão com banco de dados
│   ├── conexao_db.py      # Configuração da conexão
│   ├── povoar_db.py       # Scripts para popular o banco
│   └── apagar_db.py       # Scripts para limpeza do banco
├── controller/             # Controladores/Routers da API
│   ├── artigo_controller.py
│   ├── pesquisador_controller.py
│   └── ...
├── dao/                   # Data Access Objects
│   ├── artigo_dao.py
│   ├── pesquisador_dao.py
│   └── ...
├── model/                 # Modelos de dados
│   ├── artigo.py
│   ├── pesquisador.py
│   └── ...
├── static/                # Arquivos estáticos
├── imagens/              # Diretório para imagens
│   └── pesquisadores/    # Fotos dos pesquisadores
├── main.py               # Arquivo principal da aplicação
├── config.py             # Configurações da aplicação
├── requirements.txt      # Dependências do projeto
└── README.md            # Este arquivo
```

## 🌐 CORS

A aplicação está configurada para aceitar requisições de:
- `http://localhost:8080`
- `http://127.0.0.1:8080`

Se precisar adicionar outras origens, edite a configuração do CORS no arquivo `main.py`.

## 🔄 Sincronização de dados

A aplicação possui funcionalidades automáticas de sincronização:
- **Resumos de artigos**: Sincronização automática de resumos via IA
- **Fotos de pesquisadores**: Sincronização de fotos do Lattes

## 🔧 Endpoints da API

Todos os endpoints disponíveis podem ser visualizados e testados através da documentação interativa do FastAPI (Swagger UI) em:

**http://127.0.0.1:8000/docs**