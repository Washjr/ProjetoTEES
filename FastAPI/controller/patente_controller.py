from fastapi import APIRouter, HTTPException, status
from typing import List
import logging

from model.patente import Patente
from dao.patente_dao import PatenteDAO

logger = logging.getLogger(__name__)

class PatenteController:
    """
    Controller para operações de patentes.
    Encapsula lógica de roteamento e tratamento de erros.
    """
    def __init__(self):
        self.dao = PatenteDAO()
        self.router = APIRouter(prefix="/patentes", tags=["patentes"])
        self._register_routes()

    def _register_routes(self):
        self.router.add_api_route(
            "/",
            self.listar,
            response_model=List[Patente],
            methods=["GET"],
            summary="Listar patentes",
            description="Retorna todas as patentes cadastradas no sistema."
        )

        self.router.add_api_route(
            "/",
            self.adicionar,
            response_model=Patente,
            status_code=status.HTTP_201_CREATED,
            methods=["POST"],
            summary="Criar patente",
            description="Cria uma nova patente. Retorna 409 em caso de conflito ou 400 em erro genérico."
        )

        self.router.add_api_route(
            "/{id_patente}",
            self.atualizar,
            response_model=Patente,
            methods=["PUT"],
            summary="Atualizar patente",
            description="Atualiza uma patente existente por ID. Retorna 404 se não encontrada ou 400 em erro."
        )

        self.router.add_api_route(
            "/{id_patente}",
            self.apagar,
            status_code=status.HTTP_204_NO_CONTENT,
            methods=["DELETE"],
            summary="Deletar patente",
            description="Remove uma patente existente por ID. Retorna 404 se não encontrada."
        )

    def listar(self):
        return self.dao.listar_patentes()

    def adicionar(self, patente: Patente):
        try:
            return self.dao.salvar_patente(patente)
        
        except ValueError as e:
            logger.warning("Conflito ao criar patente: %s", e)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        except RuntimeError as e:
            logger.error("Erro ao criar patente: %s", e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def atualizar(self, id_patente: str, patente: Patente):
        patente.id_patente = id_patente
        try:
            return self.dao.atualizar_patente(patente)
        
        except LookupError as e:
            logger.info("Patente não encontrada para atualização: %s", e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except RuntimeError as e:
            logger.error("Erro ao atualizar patente: %s", e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def apagar(self, id_patente: str):
        try:
            self.dao.apagar_patente(id_patente)

        except LookupError as e:
            logger.info("Patente não encontrada para exclusão: %s", e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except RuntimeError as e:
            logger.error("Erro ao apagar patente: %s", e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Instância do controller e router exportável
patente_controller = PatenteController()
patente_router = patente_controller.router