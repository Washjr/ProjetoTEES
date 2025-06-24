from fastapi import APIRouter, HTTPException, status
from typing import List
from model.patente import Patente
from dao.patente_dao import (
    listar_todas,
    salvar_nova,
    atualizar_por_id,
    apagar_por_id
)

# Router para Patentes
patente_router = APIRouter(
    prefix="/patentes",
    tags=["patentes"]
)

@patente_router.get(
    "/",
    response_model=List[Patente],
    summary="Listar patentes",
    description="Retorna todas as patentes cadastradas no sistema."
)
def listar_patentes():
    return listar_todas()

@patente_router.post(
    "/",
    response_model=Patente,
    status_code=status.HTTP_201_CREATED,
    summary="Criar patente",
    description="Cria uma nova patente. Retorna 409 em caso de conflito ou 400 em erro genérico."
)
def adicionar_patente(patente: Patente):
    try:
        nova = salvar_nova(patente)
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
    return nova

@patente_router.put(
    "/{id_patente}",
    response_model=Patente,
    summary="Atualizar patente",
    description="Atualiza uma patente existente por ID. Retorna 404 se não encontrada ou 400 em erro."
)
def atualizar_patente(id_patente: str, patente: Patente):
    patente.id_patente = id_patente
    try:
        atualizada = atualizar_por_id(patente)
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
    return atualizada

@patente_router.delete(
    "/{id_patente}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar patente",
    description="Remove uma patente existente por ID. Retorna 404 se não encontrada."
)
def apagar_patente(id_patente: str):
    try:
        apagar_por_id(id_patente)
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