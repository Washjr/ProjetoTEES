from fastapi import APIRouter, HTTPException
from typing import List
from model.artigo import Artigo
from controller.dao.producoes_dao import (
    apagar_por_producao_id,
    listar_todos,
    salvar_nova_producao,
    atualizar_por_id
)

# Criação de um router chamado 'pesquisador_router'
artigo_router = APIRouter()

# Rota para listar todos os artigos
@artigo_router.get("/artigo", response_model = List[Artigo])
def listar():
    producoes = listar_todos()
    return producoes

# Rota para salvar um novo artigo
@artigo_router.post("/artigo", response_model = Artigo)
def adicionar(artigo: Artigo):
    resposta = salvar_nova_producao(artigo)
    
    if 'duplicate' in resposta:
        raise HTTPException(status_code=409, detail=resposta)
    if 'Erro' in resposta:
        raise HTTPException(status_code=400, detail=resposta)
    
    return artigo

# Rota para atualizar um artigo com base em ID
@artigo_router.put("/artigo/", response_model=Artigo)
def atualizar(artigo: Artigo):
    resposta = atualizar_por_id(artigo)
    
    if 'Erro' in resposta:
        raise HTTPException(status_code=400, detail=resposta)
    
    return artigo

# Rota para apagar um artigo com base em ID
@artigo_router.delete("/artigo/{id_artigo}", response_model=str)
def apagar(id_artigo: str):
    resposta = apagar_por_producao_id(id_artigo)
    
    if 'inválido' in resposta:
        raise HTTPException(status_code=400, detail=resposta)
    
    return resposta