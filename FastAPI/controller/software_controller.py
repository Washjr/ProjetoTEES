from fastapi import APIRouter, HTTPException, status
from typing import List
from model.software import Software
from dao.software_dao import (
    listar_todos,
    salvar_novo,
    atualizar_por_id,
    apagar_por_id
)

# Router para Softwares
software_router = APIRouter(
    prefix="/softwares",
    tags=["softwares"]
)

@software_router.get(
    "/",
    response_model=List[Software],
    summary="Listar softwares",
    description="Retorna todos os softwares cadastrados no sistema."
)
def listar_softwares():
    return listar_todos()

@software_router.post(
    "/",
    response_model=Software,
    status_code=status.HTTP_201_CREATED,
    summary="Criar software",
    description="Cria um novo software. Retorna 409 em caso de conflito ou 400 em erro genérico."
)
def adicionar_software(software: Software):
    try:
        criado = salvar_novo(software)
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

@software_router.put(
    "/{id_software}",
    response_model=Software,
    summary="Atualizar software",
    description="Atualiza um software existente por ID. Retorna 404 se não encontrado ou 400 em erro."
)
def atualizar_software(id_software: str, software: Software):
    software.id_software = id_software
    try:
        atualizado = atualizar_por_id(software)
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

@software_router.delete(
    "/{id_software}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar software",
    description="Remove um software existente por ID. Retorna 404 se não encontrado."
)
def apagar_software(id_software: str):
    try:
        apagar_por_id(id_software)
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