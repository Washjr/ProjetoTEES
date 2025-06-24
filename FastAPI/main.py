import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from controller.artigo_controller import artigo_router
from controller.pesquisador_controller import pesquisador_router
from banco.conexao_db import Conexao

# Configuração de logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s %(levelname)s %(message)s"
)

# Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    Conexao.inicializar_pool()
    yield
    Conexao.fechar_todas_conexoes()

# Cria a aplicação FastAPI com lifespan
app = FastAPI(lifespan=lifespan)

# Routers
app.include_router(pesquisador_router, prefix="/pesquisadores")
app.include_router(artigo_router, prefix="/artigos")

# Montagem de arquivos estáticos (css, js, imagens, index.html)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Página inicial
@app.get("/", response_class=HTMLResponse)
async def index():
    path = Path("static/index.html")
    if not path.is_file():
        raise HTTPException(status_code=500, detail="Página inicial não encontrada")
    return path.read_text(encoding="utf-8")

# Health-check
@app.get("/health")
def health():
    return {"status": "ok"}