from fastapi import APIRouter, HTTPException, status
from typing import List
import logging

from model.instituicao import Instituicao
from dao.instituicao_dao import InstituicaoDAO

logger = logging.getLogger(__name__)

class InstituicaoController:
    """
    Controller para operações de instituições.
    Encapsula lógica de roteamento e tratamento de erros.
    """
    def __init__(self):
        self.dao = InstituicaoDAO()
        self.router = APIRouter(prefix="/instituicoes", tags=["instituicoes"])
        self._register_routes()

    def _register_routes(self):
        self.router.add_api_route(
            "/",
            self.listar,
            response_model=List[Instituicao],
            methods=["GET"],
            summary="Listar instituições",
            description="Retorna todas as instituições cadastradas no sistema."
        )

        self.router.add_api_route(
            "/",
            self.adicionar,
            response_model=Instituicao,
            status_code=status.HTTP_201_CREATED,
            methods=["POST"],
            summary="Criar instituição",
            description=(
                "Cria uma nova instituição e retorna o recurso criado com ID gerado. "
                "Retorna 409 em caso de conflito ou 400 em erro genérico."
            )
        )

        self.router.add_api_route(
            "/{id_instituicao}",
            self.atualizar,
            response_model=Instituicao,
            methods=["PUT"],
            summary="Atualizar instituição",
            description=(
                "Atualiza uma instituição existente por ID e retorna o recurso atualizado. "
                "Retorna 404 se não encontrado ou 400 em erro."
            )
        )

        self.router.add_api_route(
            "/{id_instituicao}",
            self.apagar,
            status_code=status.HTTP_204_NO_CONTENT,
            methods=["DELETE"],
            summary="Deletar instituição",
            description="Remove uma instituição existente por ID. Retorna 404 se não encontrado."
        )

    def listar(self):
        return self.dao.listar_instituicoes()

    def adicionar(self, instituicao: Instituicao):
        try:
            return self.dao.salvar_instituicao(instituicao)
        
        except ValueError as e:
            logger.warning("Conflito ao criar instituição: %s", e)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        except RuntimeError as e:
            logger.error("Erro ao criar instituição: %s", e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def atualizar(self, id_instituicao: str, instituicao: Instituicao):
        instituicao.id_instituicao = id_instituicao
        try:
            return self.dao.atualizar_instituicao(instituicao)
        
        except LookupError as e:
            logger.info("Instituição não encontrada para atualização: %s", e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except RuntimeError as e:
            logger.error("Erro ao atualizar instituição: %s", e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def apagar(self, id_instituicao: str):
        try:
            self.dao.apagar_instituicao(id_instituicao)

        except LookupError as e:
            logger.info("Instituição não encontrada para exclusão: %s", e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except RuntimeError as e:
            logger.error("Erro ao apagar instituição: %s", e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Instância do controller e router exportável
instituicao_controller = InstituicaoController()
instituicao_router = instituicao_controller.router