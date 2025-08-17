from fastapi import APIRouter, HTTPException, Query, status
import logging

from service.selfquery_service import SelfQueryService

logger = logging.getLogger(__name__)


class SelfQueryController:
    """
    Controller para operações de self-query e busca híbrida.
    Encapsula lógica de busca inteligente com filtros automáticos.
    """
    def __init__(self):
        self.service = SelfQueryService()
        self.router = APIRouter(prefix="/self_query", tags=["self-query"])
        self._register_routes()

    def _register_routes(self):
        self.router.add_api_route(
            "/",
            self.get_available_filters,
            response_model=None,
            methods=["GET"],
            summary="Listar filtros disponíveis",
            description=(
                "Retorna informações sobre os filtros/metadados disponíveis "
                "para uso nas consultas self-query."
            )
        )

        self.router.add_api_route(
            "/busca_hibrida",
            self.busca_hibrida_artigos,
            response_model=None,
            methods=["GET"],
            summary="Busca híbrida inteligente",
            description=(
                "Realiza busca híbrida combinando busca por termos, busca semântica "
                "e filtros automáticos extraídos da consulta. Retorna resultados "
                "unificados e filtrados usando SelfQueryRetriever."
            )
        )

    def get_available_filters(self):
        """
        Endpoint para listar os filtros/metadados disponíveis para self-query.
        
        Retorna informações sobre os campos que podem ser usados em consultas
        como ano, qualis, periódico, autor, etc.
        """
        try:
            return self.service.obter_filtros_disponiveis()
        
        except Exception as e:
            logger.error(f"Erro ao listar filtros disponíveis: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao listar filtros: {str(e)}"
            )

    def busca_hibrida_artigos(
        self,
        query: str = Query(..., min_length=1, description="Consulta em linguagem natural"),
        max_results: int = Query(20, ge=1, le=100, description="Número máximo de resultados")
    ):
        """
        Endpoint para busca híbrida que combina:
        1. Query constructor para separar query de filtros
        2. Busca por termos + busca semântica
        3. Self-query para filtrar os resultados combinados
        
        Args:
            query: Consulta em linguagem natural
            max_results: Número máximo de resultados
            peso_semantico: Peso para combinar resultados (0=só termos, 1=só semântica)
        
        Exemplos:
        - "artigos de machine learning publicados após 2020"
        - "trabalhos em periódicos A1 sobre redes neurais"
        - "pesquisas com qualis melhor que B1 sobre COVID-19"
        """
        try:
            return self.service.buscar_artigos_hibrido(query, max_results)
        
        except Exception as e:
            logger.error(f"Erro na busca híbrida: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao processar busca híbrida endpoint: {str(e)}"
            )

# Instância do controller e router exportável
selfquery_controller = SelfQueryController()
selfquery_router = selfquery_controller.router
