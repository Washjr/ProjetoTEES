from fastapi import APIRouter, HTTPException, status
from typing import List
from model.instituicao import Instituicao
from dao.instituicao_dao import (
    listar_todas,
    salvar_nova,
    atualizar_por_id,
    apagar_por_id
)

# Router para Instituição
instituicao_router = APIRouter(
    prefix="/instituicoes",
    tags=["instituicoes"]
)

@instituicao_router.get(
    "/",
    response_model=List[Instituicao],
    summary="Listar instituições",
    description="Retorna todas as instituições cadastradas no sistema."
)
def listar_instituicoes():
    return listar_todas()

@instituicao_router.post(
    "/",
    response_model=Instituicao,
    status_code=status.HTTP_201_CREATED,
    summary="Criar instituição",
    description="Cria uma nova instituição e retorna o recurso criado com ID gerado. Retorna 409 em caso de conflito ou 400 em erro genérico."
)
def adicionar_instituicao(instituicao: Instituicao):
    try:
        inst_criada = salvar_nova(instituicao)
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
    return inst_criada

@instituicao_router.put(
    "/{id_instituicao}",
    response_model=Instituicao,
    summary="Atualizar instituição",
    description="Atualiza uma instituição existente por ID e retorna o recurso atualizado. Retorna 404 se não encontrado ou 400 em erro."
)
def atualizar_instituicao(id_instituicao: str, instituicao: Instituicao):
    instituicao.id_instituicao = id_instituicao
    try:
        inst_atualizada = atualizar_por_id(instituicao)
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
    return inst_atualizada

@instituicao_router.delete(
    "/{id_instituicao}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar instituição",
    description="Remove uma instituição existente por ID. Retorna 404 se não encontrado."
)
def apagar_instituicao(id_instituicao: str):
    try:
        apagar_por_id(id_instituicao)
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