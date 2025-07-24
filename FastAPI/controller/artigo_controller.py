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

    def busca_hibrida_artigos(
        self,
        query: str = Query(..., min_length=1, description="Consulta em linguagem natural"),
        max_results: int = Query(20, ge=1, le=100, description="Número máximo de resultados"),
        peso_semantico: float = Query(0.5, ge=0.0, le=1.0, description="Peso da busca semântica (0-1)")
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
            # Passo 1: Inicializar o retriever para acessar o query_constructor
            if self.self_query.retriever is None:
                self.self_query.initialize_retriever(limit_documents=1)
            
            # Extrair query estruturada usando o query_constructor
            structured_query = self.self_query.query_constructor.invoke({"query": query})
            
            # Extrair a query de conteúdo e filtros separadamente
            content_query = structured_query.query if hasattr(structured_query, 'query') and structured_query.query else query
            filters = structured_query.filter if hasattr(structured_query, 'filter') else None
            
            logger.info(f"Query separada - Conteúdo: '{content_query}', Filtros: {filters}")
            
            # Passo 2: Realizar busca por termos e busca semântica
            # Busca por termos
            resultados_termos = self.dao.buscar_por_termo(content_query)
            
            # Busca semântica
            resultados_semanticos = self.semantic.semantic_search(content_query, k=max_results, tipo="artigo")
            
            # Combinar resultados de ambas as buscas
            resultados_combinados = self._combinar_resultados(
                resultados_termos, 
                resultados_semanticos, 
                peso_semantico
            )
            
            logger.info(f"Resultados combinados: {len(resultados_combinados)} artigos")
            
            # Passo 3: Criar retriever temporário com os resultados combinados
            if resultados_combinados:
                # Converter resultados para documentos
                documents_filtrados = self._criar_documentos_temporarios(resultados_combinados)
                
                # Criar retriever temporário com os documentos filtrados
                retriever_temp = self._criar_retriever_temporario(documents_filtrados)
                
                # Aplicar filtros usando o retriever temporário
                if filters and retriever_temp:
                    # Executar consulta com filtros no retriever temporário
                    resultados_filtrados = retriever_temp.invoke(query)
                    
                    # Converter de volta para formato do frontend
                    articles_finais = self._converter_documentos_para_artigos(resultados_filtrados)
                else:
                    # Se não há filtros, usar os resultados combinados diretamente
                    articles_finais = [
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
            else:
                articles_finais = []

            # Reordena os artigos filtrados para priorizar os que vieram da busca por termos
            ids_termos = {artigo.get('id') for artigo in resultados_termos if artigo.get('id')}
            articles_termos = [a for a in articles_finais if a["artigo"].get("id") in ids_termos]
            articles_semanticos = [a for a in articles_finais if a["artigo"].get("id") not in ids_termos]
            # Ordena os artigos semânticos por score decrescente
            articles_semanticos.sort(key=lambda x: x["score"], reverse=True)
            articles_finais = articles_termos + articles_semanticos
                
            return {
                "query": query,
                "method": "hybrid_search",
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao processar busca híbrida: {str(e)}"
            )

    def _combinar_resultados(self, resultados_termos, resultados_semanticos, peso_semantico):
        """
        Combina resultados de busca por termos e semântica com pesos.
        """
        # Criar dicionário para combinar resultados por ID
        artigos_combinados = {}
        
        # Processar resultados de termos
        for artigo in resultados_termos:
            artigo_id = artigo.get('id')
            if artigo_id:
                artigos_combinados[artigo_id] = {
                    "artigo": artigo,
                    "score_termos": 1.0,  # Score fixo para busca por termos
                    "score_semantico": 0.0,
                    "origem": ["termos"]
                }
        
        # Processar resultados semânticos
        for artigo, score in resultados_semanticos:
            artigo_id = artigo.get('id')
            if artigo_id:
                if artigo_id in artigos_combinados:
                    # Artigo já existe, atualizar score semântico
                    artigos_combinados[artigo_id]["score_semantico"] = score
                    artigos_combinados[artigo_id]["origem"].append("semantica")
                else:
                    # Novo artigo apenas da busca semântica
                    artigos_combinados[artigo_id] = {
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

    def _criar_documentos_temporarios(self, resultados_combinados):
        """
        Converte resultados combinados em documentos para o retriever temporário.
        """
        documents = []
        
        for resultado in resultados_combinados:
            artigo = resultado["artigo"]
            
            # Criar conteúdo do documento
            title = artigo.get('title', '') or ''
            abstract = artigo.get('abstract', '') or ''
            content = f"Título: {title}\nResumo: {abstract}"
            
            # Criar metadados
            qualis_str = artigo.get('qualis', '') or ''
            metadata = {
                "year": artigo.get('year'),
                "qualis": qualis_str,
                "qualis_score": self.self_query._qualis_to_numeric(qualis_str),
                "journal": artigo.get('journal', ''),
                "author_name": artigo.get('author_name', ''),
                "doi": artigo.get('doi', ''),
                "hybrid_score": resultado["score"]
            }
            
            # Filtrar valores None
            metadata = {k: v for k, v in metadata.items() if v is not None}
            
            from langchain_core.documents import Document
            doc = Document(page_content=content, metadata=metadata)
            documents.append(doc)
        
        return documents

    def _criar_retriever_temporario(self, documents):
        """
        Cria um retriever temporário com os documentos fornecidos.
        """
        try:
            from langchain_chroma import Chroma
            from langchain_openai import OpenAIEmbeddings
            from langchain.retrievers.self_query.base import SelfQueryRetriever
            
            # Usar embeddings do OpenAI
            embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",
                api_key=self.self_query.api_key
            )
            
            # Criar vectorstore temporário em memória
            vectorstore_temp = Chroma.from_documents(
                documents=documents,
                embedding=embeddings,
                persist_directory=None  # Em memória
            )
            
            # Criar retriever temporário com os mesmos AttributeInfo
            retriever_temp = SelfQueryRetriever.from_llm(
                llm=self.self_query.llm,
                vectorstore=vectorstore_temp,
                document_contents=self.self_query.document_content_description,
                metadata_field_info=self.self_query.attribute_infos,
                verbose=True
            )
            
            return retriever_temp
            
        except Exception as e:
            logger.error(f"Erro ao criar retriever temporário: {e}")
            return None

    def _converter_documentos_para_artigos(self, documents):
        """
        Converte documentos do retriever de volta para formato de artigos.
        """
        articles = []
        
        for doc in documents:
            # Extrair informações do conteúdo
            content_lines = doc.page_content.split('\n')
            title = content_lines[0].replace('Título: ', '') if content_lines else ''
            abstract = content_lines[1].replace('Resumo: ', '') if len(content_lines) > 1 else ''
            
            # Construir objeto artigo
            article_data = {
                "title": title,
                "abstract": abstract,
                "year": doc.metadata.get('year'),
                "qualis": doc.metadata.get('qualis', ''),
                "journal": doc.metadata.get('journal', ''),
                "doi": doc.metadata.get('doi', ''),
                "author_name": doc.metadata.get('author_name', '')
            }
            
            articles.append({
                "artigo": article_data,
                "score": doc.metadata.get('hybrid_score', 1.0),
                "metadata": doc.metadata
            })
        
        return articles
        
# Instância do controller e router exportável
artigo_controller = ArtigoController()
artigo_router = artigo_controller.router