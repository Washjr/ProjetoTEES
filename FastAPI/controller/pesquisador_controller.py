from fastapi import APIRouter, HTTPException, status
from typing import List
from model.pesquisador import Pesquisador
from dao.pesquisador_dao import (
    listar_todos,
    salvar_novo_pesquisador,
    atualizar_por_id,
    apagar_por_id
)

pesquisador_router = APIRouter(prefix="/pesquisadores", tags=["pesquisadores"])


@pesquisador_router.get(
    "/", 
    response_model = List[Pesquisador],
    summary="Listar pesquisadores",
    description="Retorna todos os pesquisadores cadastrados no sistema."
)
def listar():
    return listar_todos()


@pesquisador_router.post(
    "/",
    response_model=Pesquisador,
    status_code=status.HTTP_201_CREATED,
    summary="Criar pesquisador",
    description="Cria um novo pesquisador e retorna o recurso criado com ID gerado. Retorna 409 em caso de conflito de chave ou 400 em erro genérico."
)
def adicionar(pesquisador: Pesquisador):
    try:
        pesquisador_criado = salvar_novo_pesquisador(pesquisador)
    except ValueError as e:        
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except RuntimeError as e:        
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return pesquisador_criado


@pesquisador_router.put(
    "/{id_pesquisador}",
    response_model=Pesquisador,
    summary="Atualizar pesquisador",
    description="Atualiza um pesquisador existente por ID e retorna o recurso atualizado. Retorna 404 se não encontrado ou 400 em erro."
)
def atualizar(id_pesquisador: str, pesquisador: Pesquisador):
    pesquisador.id_pesquisador = id_pesquisador 
    try:
        pesquisador_atualizado = atualizar_por_id(pesquisador)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return pesquisador_atualizado


@pesquisador_router.delete(
    "/{id_pesquisador}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar pesquisador",
    description="Remove um pesquisador existente por ID. Retorna 404 se não encontrado."
)
def apagar(id_pesquisador: str):
    try:
        apagar_por_id(id_pesquisador)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))