from fastapi import APIRouter, HTTPException, status
from typing import List
import logging

from model.livro import Livro
from dao.livro_dao import LivroDAO

logger = logging.getLogger(__name__)

class LivroController:
    """
    Controller para operações de livros.
    Encapsula lógica de roteamento e tratamento de erros.
    """
    def __init__(self):
        self.dao = LivroDAO()
        self.router = APIRouter(prefix="/livros", tags=["livros"])
        self._register_routes()

    def _register_routes(self):
        self.router.add_api_route(
            "/",
            self.listar,
            response_model=List[Livro],
            methods=["GET"],
            summary="Listar livros",
            description="Retorna todos os livros cadastrados no sistema."
        )

        self.router.add_api_route(
            "/",
            self.adicionar,
            response_model=Livro,
            status_code=status.HTTP_201_CREATED,
            methods=["POST"],
            summary="Criar livro",
            description="Cria um novo livro. Retorna 409 em caso de conflito ou 400 em erro genérico."
        )

        self.router.add_api_route(
            "/{id_livro}",
            self.atualizar,
            response_model=Livro,
            methods=["PUT"],
            summary="Atualizar livro",
            description="Atualiza um livro existente por ID. Retorna 404 se não encontrado ou 400 em erro."
        )

        self.router.add_api_route(
            "/{id_livro}",
            self.apagar,
            status_code=status.HTTP_204_NO_CONTENT,
            methods=["DELETE"],
            summary="Deletar livro",
            description="Remove um livro existente por ID. Retorna 404 se não encontrado."
        )

    def listar(self):
        return self.dao.listar_livros()

    def adicionar(self, livro: Livro):
        try:
            return self.dao.salvar_livro(livro)
        
        except ValueError as e:
            logger.warning("Conflito ao criar livro: %s", e)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        except RuntimeError as e:
            logger.error("Erro ao criar livro: %s", e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def atualizar(self, id_livro: str, livro: Livro):
        livro.id_livro = id_livro
        try:
            return self.dao.atualizar_livro(livro)
        
        except LookupError as e:
            logger.info("Livro não encontrado para atualização: %s", e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except RuntimeError as e:
            logger.error("Erro ao atualizar livro: %s", e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def apagar(self, id_livro: str):
        try:
            self.dao.apagar_livro(id_livro)

        except LookupError as e:
            logger.info("Livro não encontrado para exclusão: %s", e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except RuntimeError as e:
            logger.error("Erro ao apagar livro: %s", e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Instância do controller e router exportável
livro_controller = LivroController()
livro_router = livro_controller.router