import logging
from typing import List, Dict, Any

from model.dto.artigo_busca_dto import ArtigoBuscaDTO
from model.mapper.artigo_dto_mapper import ArtigoDTOMapper
from dao.artigo_dao import ArtigoDAO
from service.embedding import EmbeddingService
from service.search.semantic_search import SemanticSearchService
from service.search.self_query_retriever import SelfQueryRetrieverService
import json
import os

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

    def obter_filtros_disponiveis(self) -> Dict[str, Any]:
        """
        Retorna informações sobre os filtros/metadados disponíveis para self-query,
        diretamente do arquivo metadata_config.json.
        
        Returns:
            Informações sobre campos disponíveis para filtros
        """

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
            
            # Passo 2: Realizar buscas por termos e semântica
            resultados_termos = self.dao.buscar_por_termo(content_query)
            resultados_semanticos = self.semantic.semantic_search(content_query, k=max_results, tipo="artigo")
            
            # Passo 3: Combinar resultados
            resultados_combinados = self._combinar_resultados(
                resultados_termos, 
                resultados_semanticos
            )
            
            logger.info(f"Total de resultados combinados: {len(resultados_combinados)}")
            
            # Passo 4: Aplicar filtros se existirem
            if filters:
                resultados_combinados = self._aplicar_filtros_nas_listas(
                    resultados_combinados, 
                    filters, 
                    query, 
                    max_results
                )

            return {
                "query": query,
                "structured_query": {
                    "content_query": content_query,
                    "filters": str(filters) if filters else None
                },
                "search_stats": {
                    "total_resultados": len(resultados_combinados)
                },
                "results": resultados_combinados
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

    def _aplicar_filtros_nas_listas(
        self, 
        resultados_combinados: List[ArtigoBuscaDTO], 
        filters: Any, 
        query: str, 
        max_results: int
    ) -> List[ArtigoBuscaDTO]:
        """
        Aplica filtros automáticos na lista de resultados.
        
        Args:
            resultados_combinados: Lista com todos os resultados combinados
            filters: Filtros extraídos da query
            query: Query original
            max_results: Máximo de resultados
            
        Returns:
            Lista filtrada
        """
        if not filters or not resultados_combinados:
            return resultados_combinados
        
        try:
            documents = ArtigoDTOMapper.to_document_list(resultados_combinados)
            if documents:
                retriever = self.self_query.create_temporary_retriever(documents)
                if retriever:
                    retriever.search_kwargs = {'k': max_results}
                    docs_filtrados = retriever.invoke(query)
                    return ArtigoDTOMapper.to_artigo_busca_dto_list(docs_filtrados)
                    
        except Exception as e:
            logger.warning(f"Erro ao aplicar filtros: {e}. Retornando resultados sem filtros.")
        
        return resultados_combinados