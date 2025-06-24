from fastapi import APIRouter, HTTPException, status
from typing import List
from model.artigo import Artigo
from dao.artigo_dao import (    
    listar_todos,
    salvar_novo_artigo,
    atualizar_por_id,
    apagar_por_id
)

artigo_router = APIRouter(prefix="/artigos", tags=["artigos"])

@artigo_router.get(
    "/", 
    response_model = List[Artigo],
    summary="Listar artigos",
    description="Retorna todos os artigos cadastrados no sistema."
)
def listar():
    return listar_todos()


@artigo_router.post(
    "/",
    response_model=Artigo,
    status_code=status.HTTP_201_CREATED,
    summary="Criar artigo",
    description="Cria um novo artigo e retorna o recurso criado com ID gerado. Retorna 409 em caso de conflito de chave ou 400 em erro genérico."
)
def adicionar(artigo: Artigo):
    try:
        artigo_criado = salvar_novo_artigo(artigo)
    except ValueError as e:        
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except RuntimeError as e:        
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return artigo_criado


@artigo_router.put(
    "/{id_artigo}",
    response_model=Artigo,
    summary="Atualizar artigo",
    description="Atualiza um artigo existente por ID e retorna o recurso atualizado. Retorna 404 se não encontrado ou 400 em erro."
)
def atualizar(id_artigo: str, artigo: Artigo):   
    artigo.id_artigo = id_artigo 
    try:
        artigo_atualizado = atualizar_por_id(artigo)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return artigo_atualizado

@artigo_router.delete(
    "/{id_artigo}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar artigo",
    description="Remove um artigo existente por ID. Retorna 404 se não encontrado."
)
def apagar(id_artigo: str):
    try:
        apagar_por_id(id_artigo)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))