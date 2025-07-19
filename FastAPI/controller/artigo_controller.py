from fastapi import APIRouter, HTTPException, Query, status
import logging

from dao.artigo_dao import ArtigoDAO
from model.artigo import Artigo
from service.langchain import LangchainService
from service.semantic_search import SemanticSearchService

logger = logging.getLogger(__name__)


class ArtigoController:
    """
    Controller para operações de artigos.
    Encapsula lógica de roteamento e tratamento de erros.
    """
    def __init__(self):
        self.dao = ArtigoDAO()
        self.summarizer = LangchainService()
        self.semantic = SemanticSearchService()
        self.router = APIRouter(prefix="/artigos", tags=["artigos"])
        self._register_routes()

    def _register_routes(self):
        self.router.add_api_route(
            "/",
            self.listar,
            # response_model=List[Artigo],
            response_model=None,
            methods=["GET"],
            summary="Listar artigos",
            description="Retorna todos os artigos cadastrados no sistema."
        )

        self.router.add_api_route(
            "/buscar",
            self.buscar_por_termo,
            response_model=None,
            methods=["GET"],
            summary="Buscar artigos por termo",
            description=(
                "Retorna os artigos cujo nome ou resumo contém o termo passado. "
                "Pode também incluir um resumo geral dos resultados e tags separadas se `incluir_resumo=true`."
            )
        )

        self.router.add_api_route(
            "/busca_semantica",
            self.busca_semantica_artigos,
            response_model=None,
            methods=["GET"],
            summary="Busca semântica em artigos",
            description=(
                "Realiza busca semântica usando embeddings para retornar artigos "
                "ordenados por relevância no contexto da consulta."
            )
        )

        self.router.add_api_route(
            "/",
            self.adicionar,
            response_model=Artigo,
            status_code=status.HTTP_201_CREATED,
            methods=["POST"],
            summary="Criar artigo",
            description=(
                "Cria um novo artigo e retorna o recurso criado com ID gerado. "
                "Retorna 409 em caso de conflito de chave ou 400 em erro genérico."
            )
        )

        self.router.add_api_route(
            "/{id_artigo}",
            self.atualizar,
            response_model=Artigo,
            methods=["PUT"],
            summary="Atualizar artigo",
            description=(
                "Atualiza um artigo existente por ID e retorna o recurso atualizado. "
                "Retorna 404 se não encontrado ou 400 em erro."
            )
        )

        self.router.add_api_route(
            "/{id_artigo}",
            self.apagar,
            status_code=status.HTTP_204_NO_CONTENT,
            methods=["DELETE"],
            summary="Deletar artigo",
            description="Remove um artigo existente por ID. Retorna 404 se não encontrado."
        )

    def listar(self):
        return self.dao.listar_artigos()

    def buscar_por_termo(
        self, 
        termo: str = Query(..., min_length=1), 
        incluir_resumo: bool = Query(False)
    ):
        try:
            resultados = self.dao.buscar_por_termo(termo)

            if incluir_resumo and resultados:
                resumo = self.summarizer.summarize(resultados, tipo="artigo")
                tags = self.summarizer.gerar_tags_artigo(resultados)
                return {
                    "resultados": resultados, 
                    "resumo_ia": resumo,
                    "tags": tags
                }

            return resultados
        
        except Exception as e:
            logger.exception("Erro ao buscar artigo pelo termo: {termo}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def busca_semantica_artigos(
        self,
        termo: str = Query(..., min_length=1),
        k: int = Query(10, ge=1, le=50)
    ):        
        try:
            resultados = self.semantic.semantic_search(termo, k, tipo="artigo")
            
            return {
                "query": termo,
                "resultados": [
                    {"documento": doc, "score": score} for doc, score in resultados
                ]
            }
        
        except Exception as e:
            logger.error(f"Erro na busca semântica de artigos: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def adicionar(self, artigo: Artigo):
        try:
            return self.dao.salvar_artigo(artigo)
        
        except ValueError as e:
            logger.warning("Conflito ao criar artigo: %s", e)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        except RuntimeError as e:
            logger.error("Erro ao criar artigo: %s", e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def atualizar(self, id_artigo: str, artigo: Artigo):
        artigo.id_artigo = id_artigo
        try:
            return self.dao.atualizar_artigo(artigo)
        
        except LookupError as e:
            logger.info("Artigo não encontrado para atualização: %s", e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except RuntimeError as e:
            logger.error("Erro ao atualizar artigo: %s", e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def apagar(self, id_artigo: str):
        try:
            self.dao.apagar_artigo(id_artigo)

        except LookupError as e:
            logger.info("Artigo não encontrado para exclusão: %s", e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except RuntimeError as e:
            logger.error("Erro ao apagar artigo: %s", e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        
# Instância do controller e router exportável
artigo_controller = ArtigoController()
artigo_router = artigo_controller.router