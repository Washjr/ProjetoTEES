from fastapi import APIRouter, HTTPException, status
from typing import List
from model.livro import Livro
from dao.livro_dao import (
    listar_todos,
    salvar_novo_livro,
    atualizar_por_id,
    apagar_por_id
)

# Router para Livros
livro_router = APIRouter(
    prefix="/livros",
    tags=["livros"]
)

@livro_router.get(
    "/",
    response_model=List[Livro],
    summary="Listar livros",
    description="Retorna todos os livros cadastrados no sistema."
)
def listar_livros():
    return listar_todos()

@livro_router.post(
    "/",
    response_model=Livro,
    status_code=status.HTTP_201_CREATED,
    summary="Criar livro",
    description="Cria um novo livro. Retorna 409 em caso de conflito ou 400 em erro genérico."
)
def adicionar_livro(livro: Livro):
    try:
        novo = salvar_novo_livro(livro)
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
    return novo

@livro_router.put(
    "/{id_livro}",
    response_model=Livro,
    summary="Atualizar livro",
    description="Atualiza um livro existente por ID. Retorna 404 se não encontrado ou 400 em erro."
)
def atualizar_livro(id_livro: str, livro: Livro):
    livro.id_livro = id_livro
    try:
        atualizado = atualizar_por_id(livro)
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

@livro_router.delete(
    "/{id_livro}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar livro",
    description="Remove um livro existente por ID. Retorna 404 se não encontrado."
)
def apagar_livro(id_livro: str):
    try:
        apagar_por_id(id_livro)
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