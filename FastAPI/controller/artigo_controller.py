from fastapi import APIRouter, HTTPException, Query, status
import logging

from dao.artigo_dao import ArtigoDAO
from model.artigo import Artigo
from service.langchain_service import LangchainService
from service.semantic_search import SemanticSearchService
from service.self_query_retriever import SelfQueryRetrieverService

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
        self.self_query = SelfQueryRetrieverService()
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
            "/self_query",
            self.self_query_artigos,
            response_model=None,
            methods=["GET"],
            summary="Busca inteligente com filtros automáticos",
            description=(
                "Realiza busca combinando análise semântica e filtros extraídos "
                "automaticamente da consulta usando SelfQueryRetriever do LangChain. "
                "Retorna artigos relevantes com base na consulta em linguagem natural."
            )
        )

        self.router.add_api_route(
            "/self_query/test",
            self.test_self_query_retriever,
            response_model=None,
            methods=["GET"],
            summary="Testar SelfQueryRetriever",
            description=(
                "Endpoint para testar o SelfQueryRetriever e ver informações detalhadas "
                "sobre o processamento da consulta, incluindo metadados e documentos retornados."
            )
        )

        self.router.add_api_route(
            "/self_query/filters",
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
            "/self_query/debug_query",
            self.debug_query_constructor,
            response_model=None,
            methods=["GET"],
            summary="Debug do Query Constructor",
            description=(
                "Endpoint para verificar a query estruturada gerada pelo query_constructor "
                "a partir de uma consulta em linguagem natural, sem executar a busca."
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

    def self_query_artigos(
        self,
        query: str = Query(..., min_length=1, description="Consulta com filtros automáticos"),
        max_results: int = Query(10, ge=1, le=50, description="Número máximo de resultados")
    ):
        """
        Endpoint para busca inteligente com filtros automáticos (self-querying).
        
        Exemplos de consultas suportadas:
        - "artigos de machine learning publicados após 2020"
        - "trabalhos em periódicos A1 sobre redes neurais"
        - "pesquisas de João Silva em qualis melhor que B1"
        - "artigos sobre COVID-19 publicados antes de 2022"
        """
        try:
            # Inicializar o retriever se necessário
            if self.self_query.retriever is None:
                self.self_query.initialize_retriever()
            
            # Executar a consulta usando o SelfQueryRetriever
            documents = self.self_query.query(query, k=max_results)
            
            # Converter documentos para o formato esperado pelo frontend
            articles = []
            for doc in documents:
                # Extrair informações do conteúdo do documento
                content_lines = doc.page_content.split('\n')
                title = content_lines[0].replace('Título: ', '') if content_lines else ''
                abstract = content_lines[1].replace('Resumo: ', '') if len(content_lines) > 1 else ''
                
                # Construir o objeto artigo
                article_data = {
                    "title": title,
                    "abstract": abstract,
                    "year": doc.metadata.get('year'),
                    "qualis": doc.metadata.get('qualis', ''),
                    "qualis_score": doc.metadata.get('qualis_score'),
                    "journal": doc.metadata.get('journal', ''),
                    "doi": doc.metadata.get('doi', ''),
                    "author_name": doc.metadata.get('author_name', '')
                }
                
                articles.append({
                    "artigo": article_data,
                    "score": 1.0,  # SelfQueryRetriever não retorna score de relevância
                    "metadata": doc.metadata
                })
            
            return {
                "query": query,
                "method": "self_query_retriever",
                "total_found": len(articles),
                "results": articles
            }
        
        except Exception as e:
            logger.error(f"Erro na busca self-query: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Erro ao processar consulta: {str(e)}"
            )

    def test_self_query_retriever(
        self,
        query: str = Query(..., min_length=1, description="Consulta para teste do SelfQueryRetriever")
    ):
        """
        Endpoint para testar o SelfQueryRetriever com informações detalhadas.
        
        Retorna informações sobre:
        - Documentos encontrados
        - Metadados processados
        - AttributeInfo configurados
        - Preview do conteúdo
        """
        try:
            # Inicializar o retriever se necessário
            if self.self_query.retriever is None:
                self.self_query.initialize_retriever(limit_documents=20)  # Limite para teste
            
            # Executar consulta de teste
            documents = self.self_query.query(query, k=5)
            
            # Preparar informações detalhadas
            doc_info = []
            for i, doc in enumerate(documents):
                doc_info.append({
                    "index": i,
                    "content_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "metadata": doc.metadata
                })
            
            return {
                "query": query,
                "success": True,
                "documents_found": len(documents),
                "documents": doc_info,
                "attribute_infos": [
                    {
                        "name": attr.name,
                        "description": attr.description,
                        "type": attr.type
                    }
                    for attr in self.self_query.attribute_infos
                ],
                "document_content_description": self.self_query.document_content_description
            }
        
        except Exception as e:
            logger.error(f"Erro no teste do SelfQueryRetriever: {e}")
            return {
                "query": query,
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }

    def get_available_filters(self):
        """
        Endpoint para listar os filtros/metadados disponíveis para self-query.
        
        Retorna informações sobre os campos que podem ser usados em consultas
        como ano, qualis, periódico, autor, etc.
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao listar filtros: {str(e)}"
            )

    def debug_query_constructor(
        self,
        query: str = Query(..., min_length=1, description="Consulta em linguagem natural para debug")
    ):
        """
        Endpoint para debugar o query_constructor e ver a query estruturada gerada.
        
        Retorna informações sobre:
        - Query original
        - Query estruturada gerada
        - Filtros aplicados
        - Metadados extraídos
        
        Exemplos de uso:
        - "artigos de machine learning publicados após 2020"
        - "trabalhos em periódicos A1 sobre redes neurais"
        - "pesquisas com qualis melhor que B1"
        """
        try:
            # Inicializar o retriever se necessário (apenas para ter acesso ao query_constructor)
            if self.self_query.retriever is None:
                self.self_query.initialize_retriever(limit_documents=1)  # Mínimo necessário
            
            # Executar apenas o query_constructor para ver a query estruturada
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
            
            # Adicionar informações extras se disponíveis
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
        
# Instância do controller e router exportável
artigo_controller = ArtigoController()
artigo_router = artigo_controller.router