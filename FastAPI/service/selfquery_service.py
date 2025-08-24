import logging
from re import I
from typing import List, Dict, Any

from yarg import get

from model.dto.artigo_busca_dto import ArtigoBuscaDTO
from model.mapper.artigo_dto_mapper import ArtigoDTOMapper
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

    def get_metadata_config(self) -> Dict[str, Any]:
        try:
            return self.self_query.metadata_config
        except Exception as e:
            logger.error(f"Erro ao carregar metadata_config.json: {e}")
            raise RuntimeError(f"Erro ao listar filtros: {str(e)}")

    def buscar_artigos_hibrido(
        self, 
        query: str, 
        max_results: int = 20
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
            
            structured_query = self.self_query.query_constructor.invoke({"query": query})
            content_query = structured_query.query if hasattr(structured_query, 'query') and structured_query.query else query
            filters = structured_query.filter if hasattr(structured_query, 'filter') else None

            logger.info(f"Query separada - Conteúdo: '{content_query}', Filtros: {filters}")

            # Passo  2: Traduzir filtros para SQL
            filter_query = ""
            if filters:
                filter_query = get_where_clause(str(filters), self.sql_query_translator)

            # Passo 3: Realizar buscas por termos e semântica com filtros traduzidos
            resultados_termos = self.dao.buscar_por_termo(content_query, filter_query)
            resultados_semanticos = self.semantic.semantic_search(content_query, k=max_results, filter=filter_query)

            # Passo 4: Combinar resultados
            resultados_combinados = self._combinar_resultados(
                resultados_termos, 
                resultados_semanticos
            )
            
            logger.info(f"Total de resultados combinados: {len(resultados_combinados)}")

            return {
                "query": query,
                "structured_query": {
                    "content_query": content_query,
                    "filters": str(filters) if filters else None
                },
                "search_stats": {
                    "total_resultados": len(resultados_combinados)
                },
                "results": {
                    "termos": resultados_termos,
                    "semanticos": resultados_semanticos
                }
            }
            
        except Exception as e:
            logger.error(f"Erro na busca híbrida: {e}")
            raise RuntimeError(f"Erro ao processar busca híbrida: {str(e)}")

    def _combinar_resultados(
        self, 
        resultados_termos: List[ArtigoBuscaDTO], 
        resultados_semanticos: List[ArtigoBuscaDTO]
    ) -> List[ArtigoBuscaDTO]:
        """
        Combina resultados de busca por termos e semântica em uma única lista.
        Remove duplicatas mantendo apenas uma ocorrência de cada artigo.
        
        Args:
            resultados_termos: Resultados da busca por termos
            resultados_semanticos: Resultados da busca semântica
            
        Returns:
            Lista única com todos os resultados sem duplicatas
        """
        ids_vistos = set()
        resultados_combinados = []

        def add_unique(artigos):
            for artigo in artigos:
                artigo_id = artigo.doi or artigo.id
                unique_id = artigo.doi if artigo.doi else artigo_id
                if unique_id not in ids_vistos:
                    ids_vistos.add(unique_id)
                    resultados_combinados.append(artigo)

        add_unique(resultados_termos)
        add_unique(resultados_semanticos)

        logger.debug(f"Combinados {len(resultados_combinados)} artigos únicos de {len(resultados_termos)} termos + {len(resultados_semanticos)} semânticos")
        
        return resultados_combinados