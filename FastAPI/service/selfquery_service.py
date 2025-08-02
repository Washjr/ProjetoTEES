import logging
from typing import List, Dict, Any, Tuple, Optional

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain.retrievers.self_query.base import SelfQueryRetriever

from dao.artigo_dao import ArtigoDAO
from service.embedding import EmbeddingService
from service.search.semantic_search import SemanticSearchService
from service.search.self_query_retriever import SelfQueryRetrieverService
from service.search.dto import ArticleDocumentDTO

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

    def buscar_artigos_self_query(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Realiza busca inteligente com filtros automáticos usando SelfQueryRetriever.
        
        Args:
            query: Consulta em linguagem natural
            max_results: Número máximo de resultados
            
        Returns:
            Dicionário com resultados da busca
        """
        try:
            # Inicializar o retriever se necessário
            if self.self_query.retriever is None:
                self.self_query.initialize_retriever()
            
            # Executar a consulta usando o SelfQueryRetriever
            documents = self.self_query.query(query, k=max_results)
            
            # Usar DTO para formatação da resposta
            return ArticleDocumentDTO.format_search_response(
                query=query,
                documents=documents,
                method="self_query_retriever"
            )
            
        except Exception as e:
            logger.error(f"Erro na busca self-query: {e}")
            raise RuntimeError(f"Erro ao processar consulta: {str(e)}")

    def obter_filtros_disponiveis(self) -> Dict[str, Any]:
        """
        Retorna informações sobre os filtros/metadados disponíveis para self-query.
        
        Returns:
            Informações sobre campos disponíveis para filtros
        """
        try:
            # Obter informações dos AttributeInfo configurados
            filters = []
            for attr_info in self.self_query.attribute_infos:
                filter_info = {
                    "name": attr_info.name,
                    "description": attr_info.description,
                    "type": attr_info.type
                }
                
                # Adicionar valores possíveis para campos específicos
                if attr_info.name == "qualis":
                    filter_info["possible_values"] = ["A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4", "C"]
                elif attr_info.name == "qualis_score":
                    filter_info["possible_values"] = "0-7 (A1=7, A2=6, A3=5, A4=4, B1=3, B2=2, B3=1, B4=1, C=0)"
                elif attr_info.name == "year":
                    filter_info["example_usage"] = "ano > 2020, publicado após 2019, antes de 2023"
                
                filters.append(filter_info)
            
            return {
                "available_filters": filters,
                "total_filters": len(filters),
                "document_content_description": self.self_query.document_content_description,
                "usage_examples": [
                    "artigos de machine learning publicados após 2020",
                    "trabalhos em periódicos A1 sobre redes neurais", 
                    "pesquisas com qualis melhor que B1",
                    "artigos do autor João Silva publicados em 2023",
                    "trabalhos sobre COVID-19 antes de 2022"
                ]
            }
            
        except Exception as e:
            logger.error(f"Erro ao listar filtros disponíveis: {e}")
            raise RuntimeError(f"Erro ao listar filtros: {str(e)}")

    def debug_query_constructor(self, query: str) -> Dict[str, Any]:
        """
        Debuga o query_constructor para ver a query estruturada gerada.
        
        Args:
            query: Consulta em linguagem natural para debug
            
        Returns:
            Informações sobre a query estruturada gerada
        """
        try:
            # Inicializar o retriever se necessário
            if self.self_query.retriever is None:
                self.self_query.initialize_retriever(limit_documents=1)
            
            # Executar apenas o query_constructor
            structured_query = self.self_query.query_constructor.invoke({"query": query})
            
            # Preparar resposta detalhada
            response = {
                "original_query": query,
                "success": True,
                "structured_query": {
                    "query": structured_query.query if hasattr(structured_query, 'query') else None,
                    "filter": str(structured_query.filter) if hasattr(structured_query, 'filter') else None,
                    "limit": structured_query.limit if hasattr(structured_query, 'limit') else None
                }
            }
            
            # Adicionar análise de filtros
            if hasattr(structured_query, 'filter') and structured_query.filter:
                response["filter_analysis"] = {
                    "filter_type": type(structured_query.filter).__name__,
                    "has_filters": True,
                    "filter_details": str(structured_query.filter)
                }
            else:
                response["filter_analysis"] = {
                    "has_filters": False,
                    "message": "Nenhum filtro foi extraído da consulta"
                }
            
            return response
            
        except Exception as e:
            logger.error(f"Erro no debug do query constructor: {e}")
            return {
                "original_query": query,
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "message": "Erro ao processar a consulta com o query_constructor"
            }

    def buscar_artigos_hibrido(
        self, 
        query: str, 
        max_results: int = 20, 
        peso_semantico: float = 0.5
    ) -> Dict[str, Any]:
        """
        Realiza busca híbrida combinando busca por termos, semântica e filtros automáticos.
        
        Args:
            query: Consulta em linguagem natural
            max_results: Número máximo de resultados
            peso_semantico: Peso da busca semântica (0-1)
            
        Returns:
            Resultados da busca híbrida
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
                resultados_semanticos, 
                peso_semantico
            )
            
            logger.info(f"Resultados combinados: {len(resultados_combinados)} artigos")
            
            # Passo 4: Aplicar filtros se existirem
            articles_finais = self._aplicar_filtros_nos_resultados(
                resultados_combinados, 
                filters, 
                query, 
                max_results
            )

            #print articles_finais 
            logger.info(f"Resultados finais após filtros: {len(articles_finais)} artigos")
            
            # Passo 5: Reordenar resultados priorizando busca por termos
            articles_finais = self._reordenar_resultados(articles_finais)
                
            return {
                "query": query,
                "structured_query": {
                    "content_query": content_query,
                    "filters": str(filters) if filters else None
                },
                "search_stats": {
                    "resultados_termos": len(resultados_termos),
                    "resultados_semanticos": len(resultados_semanticos),
                    "resultados_combinados": len(resultados_combinados),
                    "peso_semantico": peso_semantico
                },
                "total_found": len(articles_finais),
                "results": articles_finais
            }
            
        except Exception as e:
            logger.error(f"Erro na busca híbrida: {e}")
            raise RuntimeError(f"Erro ao processar busca híbrida: {str(e)}")

    def _create_temporary_retriever(self, documents: List[Document]) -> Optional[Any]:
        """
        Cria um retriever temporário com os documentos fornecidos.
        
        Args:
            documents: Lista de documentos
            
        Returns:
            Retriever temporário ou None se erro
        """
        try:
            embeddings = self.embedding_service.embeddings_client
            
            vectorstore_temp = Chroma.from_documents(
                documents=documents,
                embedding=embeddings,
                persist_directory=None
            )

            retriever_temp = SelfQueryRetriever.from_llm(
                llm=self.self_query.llm,
                vectorstore=vectorstore_temp,
                document_contents=self.self_query.document_content_description,
                metadata_field_info=self.self_query.attribute_infos,
                verbose=True,
                enable_limit=True
            )

            return retriever_temp
            
        except Exception as e:
            logger.error(f"Erro ao criar retriever temporário: {e}")
            return None

    def _format_combined_results_as_articles(self, resultados_combinados: List[Dict], max_results: int) -> List[Dict[str, Any]]:
        """
        Formata os resultados combinados como artigos para retorno na busca.
        
        Args:
            resultados_combinados: Resultados combinados da busca
            max_results: Máximo de resultados a retornar
        
        Returns:
            Lista de artigos formatados
        """
        return [
            {
                "artigo": resultado["artigo"],
                "score": resultado["score"],
                "metadata": {
                    "year": resultado["artigo"].get("year"),
                    "qualis": resultado["artigo"].get("qualis", ""),
                    "journal": resultado["artigo"].get("journal", ""),
                    "doi": resultado["artigo"].get("doi", ""),
                    "author_name": resultado["artigo"].get("author_name", "")
                }
            }
            for resultado in resultados_combinados[:max_results]
        ]

    def _combinar_resultados(
        self, 
        resultados_termos: List[Dict], 
        resultados_semanticos: List[Tuple], 
        peso_semantico: float
    ) -> List[Dict[str, Any]]:
        """
        Combina resultados de busca por termos e semântica com pesos.
        
        Args:
            resultados_termos: Resultados da busca por termos
            resultados_semanticos: Resultados da busca semântica
            peso_semantico: Peso para combinar resultados
            
        Returns:
            Lista de resultados combinados
        """
        artigos_combinados = {}
        
        # Processar resultados de termos
        for artigo in resultados_termos:
            artigo_id = artigo.get('id') or artigo.get('id_artigo') or artigo.get('doi')
            if artigo_id:
                artigos_combinados[artigo_id] = {
                    "artigo": artigo,
                    "score_termos": 1.0,
                    "score_semantico": 0.0,
                    "origem": ["termos"]
                }
        
        # Processar resultados semânticos
        for artigo, score in resultados_semanticos:
            artigo_id = artigo.get('id') or artigo.get('id_artigo') or artigo.get('doi')
            if artigo_id:
                if artigo_id in artigos_combinados:
                    artigos_combinados[artigo_id]["score_semantico"] = score
                    artigos_combinados[artigo_id]["origem"].append("semantica")
                else:
                    artigos_combinados[artigo_id] = {
                        "artigo": artigo,
                        "score_termos": 0.0,
                        "score_semantico": score,
                        "origem": ["semantica"]
                    }
            else:
                # Fallback usando título + autor
                fallback_key = f"{artigo.get('title', '')}_{artigo.get('author_name', '')}"
                if fallback_key not in artigos_combinados:
                    artigos_combinados[fallback_key] = {
                        "artigo": artigo,
                        "score_termos": 0.0,
                        "score_semantico": score,
                        "origem": ["semantica"]
                    }
        
        # Calcular score final combinado
        resultados_finais = []
        for dados in artigos_combinados.values():
            score_final = (
                (1 - peso_semantico) * dados["score_termos"] + 
                peso_semantico * dados["score_semantico"]
            )
            
            resultados_finais.append({
                "artigo": dados["artigo"],
                "score": score_final,
                "scores_detalhados": {
                    "termos": dados["score_termos"],
                    "semantico": dados["score_semantico"],
                    "final": score_final
                },
                "origem": dados["origem"]
            })
        
        # Ordenar por score final (decrescente)
        resultados_finais.sort(key=lambda x: x["score"], reverse=True)
        
        return resultados_finais

    def _aplicar_filtros_nos_resultados(
        self, 
        resultados_combinados: List[Dict], 
        filters: Any, 
        query: str, 
        max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Aplica filtros automáticos nos resultados combinados usando retriever temporário.
        
        Args:
            resultados_combinados: Resultados já combinados
            filters: Filtros extraídos da query
            query: Query original
            max_results: Máximo de resultados
            
        Returns:
            Lista de artigos filtrados
        """
        if resultados_combinados:
            # Usar DTO para converter resultados para documentos
            documents_filtrados = ArticleDocumentDTO.combined_results_to_documents(resultados_combinados)
            
            # Criar retriever temporário
            retriever_temp = self._create_temporary_retriever(documents_filtrados)

            retriever_temp.search_kwargs = {'k': max_results}
            
            # Aplicar filtros se existirem
            if filters and retriever_temp:
                resultados_filtrados = retriever_temp.invoke(query)
                return ArticleDocumentDTO.documents_to_search_results(resultados_filtrados)
            else:
                # Se não há filtros, usar resultados combinados diretamente
                return self._format_combined_results_as_articles(resultados_combinados, max_results)
        else:
            return []

    def _reordenar_resultados(self, articles_finais: List[Dict]) -> List[Dict]:
        """
        Reordena resultados priorizando busca por termos e removendo duplicatas.
        
        Args:
            articles_finais: Lista de artigos a reordenar
            
        Returns:
            Lista reordenada sem duplicatas
        """
        ids_processados = set()
        articles_finais_dedupe = []
        
        # Primeiro, adicionar artigos da busca por termos
        for article in articles_finais:
            artigo_id = (
                article["artigo"].get("id") or 
                article["artigo"].get("id_artigo") or 
                article["artigo"].get("doi") or
                f"{article['artigo'].get('title', '')}_{article['artigo'].get('author_name', '')}"
            )
            
            if artigo_id not in ids_processados and "termos" in article.get("origem", []):
                articles_finais_dedupe.append(article)
                ids_processados.add(artigo_id)
        
        # Depois, adicionar artigos apenas semânticos
        articles_semanticos = []
        for article in articles_finais:
            artigo_id = (
                article["artigo"].get("id") or 
                article["artigo"].get("id_artigo") or 
                article["artigo"].get("doi") or
                f"{article['artigo'].get('title', '')}_{article['artigo'].get('author_name', '')}"
            )
            
            if artigo_id not in ids_processados:
                articles_semanticos.append(article)
                ids_processados.add(artigo_id)
        
        # Ordenar artigos semânticos por score
        articles_semanticos.sort(key=lambda x: x["score"], reverse=True)
        
        return articles_finais_dedupe + articles_semanticos