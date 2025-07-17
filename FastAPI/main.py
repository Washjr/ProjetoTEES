import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from controller.artigo_controller import artigo_router
from controller.instituicao_controller import instituicao_router
from controller.livro_controller import livro_router
from controller.patente_controller import patente_router
from controller.periodico_controller import periodico_router
from controller.pesquisador_controller import pesquisador_router
from controller.software_controller import software_router

from dao.artigo_dao import ArtigoDAO
from dao.pesquisador_dao import PesquisadorDAO
from banco.conexao_db import Conexao
from service.semantic_search import SemanticSearchService

# Configuração de logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s %(levelname)s %(message)s"
)

# Definição do ciclo de vida da aplicação
@asynccontextmanager
async def lifespan(app: FastAPI):
    Conexao.inicializar_pool()

    ArtigoDAO().sincronizar_resumos()
    PesquisadorDAO().sincronizar_fotos()
    SemanticSearchService().index_all()

    yield
    Conexao.fechar_todas_conexoes()

# Criação da aplicação FastAPI
app = FastAPI(
    title="Sistema de Produção Acadêmica",
    description="API para gerenciamento de pesquisadores, produções científicas e instituições.",
    version="1.0.0",
    lifespan=lifespan
)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro dos routers
app.include_router(artigo_router)
app.include_router(instituicao_router)
app.include_router(livro_router)
app.include_router(patente_router)
app.include_router(periodico_router)
app.include_router(pesquisador_router)
app.include_router(software_router)

# Montagem de arquivos estáticos (HTML, CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Montagem do diretório de imagens
app.mount("/imagens", StaticFiles(directory="imagens"), name="imagens")

# Endpoint de página inicial
@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    path = Path("static/index.html")
    if not path.is_file():
        raise HTTPException(status_code=500, detail="Página inicial não encontrada")
    return path.read_text(encoding="utf-8")

# Endpoint de health-check
@app.get("/health")
def health() -> dict:
    return {"status": "ok"}