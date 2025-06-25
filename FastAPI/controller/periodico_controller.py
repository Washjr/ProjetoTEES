from fastapi import APIRouter, HTTPException, status
from typing import List
import logging

from model.periodico import Periodico
from dao.periodico_dao import PeriodicoDAO

logger = logging.getLogger(__name__)

class PeriodicoController:
    """
    Controller para operações de periódicos.
    Encapsula lógica de roteamento e tratamento de erros.
    """
    def __init__(self):
        self.dao = PeriodicoDAO()
        self.router = APIRouter(prefix="/periodicos", tags=["periodicos"])
        self._register_routes()

    def _register_routes(self):
        self.router.add_api_route(
            "/",
            self.listar,
            response_model=List[Periodico],
            methods=["GET"],
            summary="Listar periódicos",
            description="Retorna todos os periódicos cadastrados no sistema."
        )

        self.router.add_api_route(
            "/",
            self.adicionar,
            response_model=Periodico,
            status_code=status.HTTP_201_CREATED,
            methods=["POST"],
            summary="Criar periódico",
            description=(
                "Cria um novo periódico. Retorna 409 se ISSN duplicado ou 400 em erro genérico."
            )
        )

        self.router.add_api_route(
            "/{id_periodico}",
            self.atualizar,
            response_model=Periodico,
            methods=["PUT"],
            summary="Atualizar periódico",
            description="Atualiza um periódico existente por ID. Retorna 404 se não encontrado ou 400 em erro."
        )

        self.router.add_api_route(
            "/{id_periodico}",
            self.apagar,
            status_code=status.HTTP_204_NO_CONTENT,
            methods=["DELETE"],
            summary="Deletar periódico",
            description="Remove um periódico existente por ID. Retorna 404 se não encontrado."
        )

    def listar(self):
        return self.dao.listar_periodicos()

    def adicionar(self, periodico: Periodico):
        try:
            return self.dao.salvar_periodico(periodico)
        
        except ValueError as e:
            logger.warning("Conflito ao criar periódico: %s", e)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        except RuntimeError as e:
            logger.error("Erro ao criar periódico: %s", e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def atualizar(self, id_periodico: str, periodico: Periodico):
        periodico.id_periodico = id_periodico
        try:
            return self.dao.atualizar_periodico(periodico)
        
        except LookupError as e:
            logger.info("Periódico não encontrado para atualização: %s", e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except RuntimeError as e:
            logger.error("Erro ao atualizar periódico: %s", e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def apagar(self, id_periodico: str):
        try:
            self.dao.apagar_periodico(id_periodico)

        except LookupError as e:
            logger.info("Periódico não encontrado para exclusão: %s", e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except RuntimeError as e:
            logger.error("Erro ao apagar periódico: %s", e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Instância do controller e router exportável
periodico_controller = PeriodicoController()
periodico_router = periodico_controller.router