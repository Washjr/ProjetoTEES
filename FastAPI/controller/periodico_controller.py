from fastapi import APIRouter, HTTPException, status
from typing import List
from model.periodico import Periodico
from dao.periodico_dao import (
    listar_todos,
    salvar_novo,
    atualizar_por_id,
    apagar_por_id
)

# Router para Periódicos
periodico_router = APIRouter(
    prefix="/periodicos",
    tags=["periodicos"]
)

@periodico_router.get(
    "/",
    response_model=List[Periodico],
    summary="Listar periódicos",
    description="Retorna todos os periódicos cadastrados no sistema."
)
def listar_periodicos():
    return listar_todos()

@periodico_router.post(
    "/",
    response_model=Periodico,
    status_code=status.HTTP_201_CREATED,
    summary="Criar periódico",
    description="Cria um novo periódico. Retorna 409 se ISSN duplicado ou 400 em erro genérico."
)
def adicionar_periodico(periodico: Periodico):
    try:
        criado = salvar_novo(periodico)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return criado

@periodico_router.put(
    "/{id_periodico}",
    response_model=Periodico,
    summary="Atualizar periódico",
    description="Atualiza um periódico existente por ID. Retorna 404 se não encontrado ou 400 em erro."
)
def atualizar_periodico(id_periodico: str, periodico: Periodico):
    periodico.id_periodico = id_periodico
    try:
        atualizado = atualizar_por_id(periodico)
    except LookupError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return atualizado

@periodico_router.delete(
    "/{id_periodico}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar periódico",
    description="Remove um periódico existente por ID. Retorna 404 se não encontrado."
)
def apagar_periodico(id_periodico: str):
    try:
        apagar_por_id(id_periodico)
    except LookupError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )