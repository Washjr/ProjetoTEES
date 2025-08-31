import logging
from re import I
from typing import List, Dict, Any

from service.utils.InterfaceFilterTranslator import InterfaceFilterTranslator
from model.dto.artigo_busca_dto import ArtigoBuscaDTO
from dao.artigo_dao import ArtigoDAO
from service.embedding import EmbeddingService
from service.search.semantic_search import SemanticSearchService
from service.search.self_query_retriever import SelfQueryRetrieverService
from service.utils.PostgreSQLFilterTranslator import PostgreSQLFilterTranslator
from service.utils.SelfQueryFilterTranslator import get_where_clause

logger = logging.getLogger(__name__)


class SelfQueryService:
    """
    Service para lógica de negócio relacionada a self-query e busca híbrida.
    Encapsula todas as operações de busca inteligente com filtros automáticos.
    """

    def __init__(self):
        self.dao = ArtigoDAO()
        self.embedding_service = EmbeddingService()
        self.semantic = SemanticSearchService()
        self.self_query = SelfQueryRetrieverService()
        self.sql_query_translator = PostgreSQLFilterTranslator()
        self.interface_translator = InterfaceFilterTranslator()

    def get_metadata_config(self) -> Dict[str, Any]:
        try:
            return self.self_query.metadata_config
        except Exception as e:
            logger.error(f"Erro ao carregar metadata_config.json: {e}")
            raise RuntimeError(f"Erro ao listar filtros: {str(e)}")

    def buscar_artigos_hibrido(
        self, query: str, max_results: int = 20
    ) -> Dict[str, Any]:
        """
        Realiza busca híbrida combinando busca por termos, semântica e filtros automáticos.

        Args:
            query: Consulta em linguagem natural
            max_results: Número máximo de resultados

        Returns:
            Resultados da busca híbrida com duas listas separadas
        """
        try:
            # Passo 1: Separar query de conteúdo e filtros
            if self.self_query.retriever is None:
                self.self_query.initialize_retriever(limit_documents=1)

            structured_query = self.self_query.query_constructor.invoke(
                {"query": query}
            )
            content_query = (
                structured_query.query
                if hasattr(structured_query, "query") and structured_query.query
                else query
            )
            filters = (
                structured_query.filter if hasattr(structured_query, "filter") else None
            )

            logger.info(
                f"Query separada - Conteúdo: '{content_query}', Filtros: {filters}"
            )

            # Passo  2: Traduzir filtros para SQL
            filter_query = ""
            interface_filter = ""
            if filters:
                filter_query = get_where_clause(str(filters), self.sql_query_translator)
                interface_filter = get_where_clause(str(filters), self.interface_translator)

            # Passo 3: Realizar buscas por termos e semântica com filtros traduzidos
            resultados_termos = self.dao.buscar_por_termo(content_query, filter_query)
            resultados_semanticos = self.semantic.semantic_search(
                content_query, k=max_results, filter=filter_query
            )

            # Passo 4: Remover artigos duplicados que possuem no termo e no semantico.
            resultados_semanticos = self._remove_duplicated(
                resultados_semanticos, resultados_termos
            )

            return {
                "query": query,
                "structured_query": {
                    "content_query": content_query,
                    "filter_interface": interface_filter if filters else None,
                    "filter_selfquery": filter_query if filters else None,
                },
                "search_stats": {
                    "total_resultados": len(resultados_termos)
                    + len(resultados_semanticos)
                },
                "results": {
                    "termos": resultados_termos,
                    "semanticos": resultados_semanticos,
                },
            }

        except Exception as e:
            logger.error(f"Erro na busca híbrida: {e}")
            raise RuntimeError(f"Erro ao processar busca híbrida: {str(e)}")

    def _remove_duplicated(
        self, semantic_result: List[ArtigoBuscaDTO], term_result: List[ArtigoBuscaDTO]
    ) -> List[ArtigoBuscaDTO]:
        term_result_ids = {artigo.id for artigo in term_result if artigo.id is not None}
        term_result_titles = {
            artigo.title.lower().strip() for artigo in term_result if artigo.title
        }
        term_result_dois = {artigo.doi.strip() for artigo in term_result if artigo.doi}

        unique_semantic = []
        for artigo in semantic_result:
            is_duplicate = False

            if (
                (artigo.id is not None and artigo.id in term_result_ids)
                or (artigo.title and artigo.title.lower().strip() in term_result_titles)
                or (artigo.doi and artigo.doi.strip() in term_result_dois)
            ):
                is_duplicate = True

            if not is_duplicate:
                unique_semantic.append(artigo)

        return unique_semantic
