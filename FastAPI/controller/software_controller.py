from fastapi import APIRouter, HTTPException, status
from typing import List
import logging

from model.software import Software
from dao.software_dao import SoftwareDAO

logger = logging.getLogger(__name__)

class SoftwareController:
    """
    Controller para operações de softwares.
    Encapsula lógica de roteamento e tratamento de erros.
    """
    def __init__(self):
        self.dao = SoftwareDAO()
        self.router = APIRouter(prefix="/softwares", tags=["softwares"])
        self._register_routes()

    def _register_routes(self):
        self.router.add_api_route(
            "/",
            self.listar,
            response_model=List[Software],
            methods=["GET"],
            summary="Listar softwares",
            description="Retorna todos os softwares cadastrados no sistema."
        )

        self.router.add_api_route(
            "/",
            self.adicionar,
            response_model=Software,
            status_code=status.HTTP_201_CREATED,
            methods=["POST"],
            summary="Criar software",
            description="Cria um novo software. Retorna 409 em caso de conflito ou 400 em erro genérico."
        )

        self.router.add_api_route(
            "/{id_software}",
            self.atualizar,
            response_model=Software,
            methods=["PUT"],
            summary="Atualizar software",
            description="Atualiza um software existente por ID. Retorna 404 se não encontrado ou 400 em erro."
        )

        self.router.add_api_route(
            "/{id_software}",
            self.apagar,
            status_code=status.HTTP_204_NO_CONTENT,
            methods=["DELETE"],
            summary="Deletar software",
            description="Remove um software existente por ID. Retorna 404 se não encontrado."
        )

    def listar(self):
        return self.dao.listar_softwares()

    def adicionar(self, software: Software):
        try:
            return self.dao.salvar_software(software)
        
        except ValueError as e:
            logger.warning("Conflito ao criar software: %s", e)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        except RuntimeError as e:
            logger.error("Erro ao criar software: %s", e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def atualizar(self, id_software: str, software: Software):
        software.id_software = id_software
        try:
            return self.dao.atualizar_software(software)
        
        except LookupError as e:
            logger.info("Software não encontrado para atualização: %s", e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except RuntimeError as e:
            logger.error("Erro ao atualizar software: %s", e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def apagar(self, id_software: str):
        try:
            self.dao.apagar_software(id_software)

        except LookupError as e:
            logger.info("Software não encontrado para exclusão: %s", e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except RuntimeError as e:
            logger.error("Erro ao apagar software: %s", e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Instância do controller e router exportável
software_controller = SoftwareController()
software_router = software_controller.router