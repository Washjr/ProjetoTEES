from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import FileResponse
from typing import List
from pathlib import Path
import logging

from model.pesquisador import Pesquisador
from dao.pesquisador_dao import PesquisadorDAO

logger = logging.getLogger(__name__)


class PesquisadorController:
    """
    Controller para operações de pesquisadores.
    Encapsula lógica de roteamento e tratamento de erros.
    """
    def __init__(self):
        self.dao = PesquisadorDAO()
        self.router = APIRouter(prefix="/pesquisadores", tags=["pesquisadores"])
        self._register_routes()

    def _register_routes(self):
        self.router.add_api_route(
            "/",
            self.listar,
            response_model=List[Pesquisador],
            methods=["GET"],
            summary="Listar pesquisadores",
            description="Retorna todos os pesquisadores cadastrados no sistema."
        )

        self.router.add_api_route(
            "/buscar",
            self.buscar_por_termo,
            response_model=List[Pesquisador],
            methods=["GET"],
            summary="Buscar pesquisadores por termo",
            description="Retorna os pesquisadores cujo nome contém o termo passado."
        )

        self.router.add_api_route(
            "/",
            self.adicionar,
            response_model=Pesquisador,
            status_code=status.HTTP_201_CREATED,
            methods=["POST"],
            summary="Criar pesquisador",
            description=(
                "Cria um novo pesquisador e retorna o recurso criado com ID gerado. "
                "Retorna 409 em caso de conflito de chave ou 400 em erro genérico."
            )
        )

        self.router.add_api_route(
            "/{id_pesquisador}",
            self.atualizar,
            response_model=Pesquisador,
            methods=["PUT"],
            summary="Atualizar pesquisador",
            description=(
                "Atualiza um pesquisador existente por ID e retorna o recurso atualizado. "
                "Retorna 404 se não encontrado ou 400 em erro."
            )
        )

        self.router.add_api_route(
            "/{id_pesquisador}",
            self.apagar,
            status_code=status.HTTP_204_NO_CONTENT,
            methods=["DELETE"],
            summary="Deletar pesquisador",
            description="Remove um pesquisador existente por ID. Retorna 404 se não encontrado."
        )

        self.router.add_api_route(
            "/{id_pesquisador}/foto",
            self.retornar_foto,
            response_class=FileResponse,
            methods=["GET"],
            summary="Obter foto do pesquisador",
            description="Retorna a foto JPEG do pesquisador, se existir."
        )

    def listar(self):
        return self.dao.listar_pesquisadores()
    
    def buscar_por_termo(self, termo: str = Query(..., min_length=1)) -> List[Pesquisador]:
        try:
            return self.dao.buscar_por_termo(termo)
        
        except Exception as e:
            logger.exception("Erro ao buscar pesquisador pelo termo: {termo}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def adicionar(self, pesquisador: Pesquisador):
        try:
            return self.dao.salvar_pesquisador(pesquisador)
        
        except ValueError as e:
            logger.warning("Conflito ao criar pesquisador: %s", e)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        except RuntimeError as e:
            logger.error("Erro ao criar pesquisador: %s", e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def atualizar(self, id_pesquisador: str, pesquisador: Pesquisador):
        pesquisador.id_pesquisador = id_pesquisador
        try:
            return self.dao.atualizar_pesquisador(pesquisador)
        
        except LookupError as e:
            logger.info("Pesquisador não encontrado para atualização: %s", e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except RuntimeError as e:
            logger.error("Erro ao atualizar pesquisador: %s", e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def apagar(self, id_pesquisador: str):
        try:
            self.dao.apagar_pesquisador(id_pesquisador)

        except LookupError as e:
            logger.info("Pesquisador não encontrado para exclusão: %s", e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except RuntimeError as e:
            logger.error("Erro ao apagar pesquisador: %s", e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    def retornar_foto(self, id_pesquisador: str) -> FileResponse:
        caminho = Path("imagens") / "pesquisadores" / f"{id_pesquisador}.jpg"
        if not caminho.exists():
            logger.warning("Foto não encontrada para pesquisador %s", id_pesquisador)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foto não encontrada")
        return FileResponse(caminho, media_type="image/jpeg")

# Instância do controller e router exportável
pesquisador_controller = PesquisadorController()
pesquisador_router = pesquisador_controller.router