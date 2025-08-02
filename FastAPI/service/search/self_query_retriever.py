import hashlib
import json
import logging
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain.chains.query_constructor.base import (
    StructuredQueryOutputParser,
    get_query_constructor_prompt,
)
from langchain.chains.query_constructor.schema import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_community.vectorstores import PGVector
from langchain_community.query_constructors.pgvector import PGVectorTranslator
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

from dao.artigo_dao import ArtigoDAO
from service.embedding import EmbeddingService
from service.search.dto import ArticleDocumentDTO
from config import configuracoes

COLLECTION_NAME = "artigo"
LLM_MODEL = "gpt-3.5-turbo"
LLM_TEMPERATURE = 0

logger = logging.getLogger(__name__)

class SelfQueryRetrieverService:
    """
    Serviço para realizar busca usando SelfQueryRetriever baseado no PGVector.
    Usa embeddings já armazenados na coluna embedding da tabela artigo.
    """
    
    def __init__(self, connection_string: str = None, collection_name: str = COLLECTION_NAME):
        """
        Inicializa o serviço de Self Query Retriever com PGVector.
        
        Args:
            connection_string: String de conexão PostgreSQL (opcional, usa configurações se None)
            collection_name: Nome da coleção no PGVector
        """
        self.connection_string = connection_string or self._get_connection_string()
        self.collection_name = collection_name
        
        self.artigo_dao = ArtigoDAO()
        self.embedding_service = EmbeddingService()
        self.metadata_config = self._load_metadata_config()
        
        self.llm = ChatOpenAI(
            temperature=LLM_TEMPERATURE,
            openai_api_key=self.embedding_service.embeddings_client.openai_api_key,
            model=LLM_MODEL
        )
        
        self.attribute_infos = self._build_attribute_infos()
        
        self.document_content_description = self.metadata_config.get(
            "document_content_description", 
            "Artigos científicos com título, resumo e metadados de publicação acadêmica"
        )

        prompt = get_query_constructor_prompt(
            self.document_content_description,
            self.attribute_infos,
        )
        output_parser = StructuredQueryOutputParser.from_components()
        self.query_constructor = prompt | self.llm | output_parser
        
        self.retriever = None
        self._vectorstore = None
    
    def _get_connection_string(self) -> str:
        """Obtém a string de conexão usando as configurações da classe Conexao."""
        try:
            # Usar as mesmas configurações da classe Conexao
            return (f"postgresql://{configuracoes.DB_USER}:{configuracoes.DB_PASS}@"
                   f"{configuracoes.DB_HOST}:{configuracoes.DB_PORT}/{configuracoes.DB_NAME}")
        except AttributeError as e:
            logger.error(f"Erro ao acessar configurações do banco: {e}")
            # Fallback para configuração padrão
            return "postgresql://postgres:postgres@localhost:5432/postgres"
    
    def _load_metadata_config(self) -> Dict[str, Any]:
        """Carrega configuração de metadados do arquivo JSON."""
        try:
            config_path = Path("config/metadata_config.json")
            if not config_path.exists():
                # Tentar caminho relativo ao arquivo atual
                config_path = Path(__file__).parent.parent / "config" / "metadata_config.json"
            
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar metadata_config.json: {e}")
            return {
                "metadata_fields": [],
                "document_content_description": "Artigos científicos com título, resumo e metadados de publicação acadêmica"
            }
    
    def _build_attribute_infos(self) -> List[AttributeInfo]:
        """Constrói lista de AttributeInfo objects baseados na configuração."""
        attribute_infos = []
        
        for field_config in self.metadata_config.get("metadata_fields", []):
            name = field_config["name"]
            description = field_config["description"]
            field_type = field_config["type"]
            
            # Mapear tipos para os tipos do AttributeInfo
            if field_type == "integer":
                attr_type = "integer"
            elif field_type == "float":
                attr_type = "float"
            else:
                attr_type = "string"
            
            # Criar AttributeInfo
            attr_info = AttributeInfo(
                name=name,
                description=description,
                type=attr_type
            )
            
            attribute_infos.append(attr_info)
        
        return attribute_infos
        
    def _create_documents_from_artigos(self, limit: Optional[int] = None) -> List[Document]:
        """Cria documentos a partir dos artigos do banco de dados usando DTO."""
        try:
            # Buscar artigos que já possuem embeddings
            artigos = self.artigo_dao.listar_artigos_com_embeddings()
            
            if not artigos:
                logger.warning("Nenhum artigo com embeddings encontrado")
                return []
            
            if limit:
                artigos = artigos[:limit]
            
            # Usar DTO para conversão
            documents = ArticleDocumentDTO.artigos_to_documents(artigos)
            
            logger.info(f"Criados {len(documents)} documentos a partir dos artigos com embeddings")
            return documents
            
        except Exception as e:
            logger.error(f"Erro ao criar documentos: {e}")
            return []
    
    def _setup_vectorstore(self, documents: List[Document], cache_key: str) -> PGVector:
        """Configura o vectorstore com PGVector usando embeddings existentes."""
        logger.info("Criando vectorstore no PGVector usando embeddings existentes da tabela artigo...")
        
        try:
            # Conectar diretamente à tabela artigo existente usando PGVector
            vectorstore = PGVector(
                connection_string=self.connection_string,
                embedding_function=self.embedding_service.embeddings_client,
                collection_name=self.collection_name,  # "artigo"
            )
            
            # Verificar se precisa popular os dados
            try:
                # Tentar fazer uma busca para verificar se já tem dados
                test_results = vectorstore.similarity_search("test", k=1)
                if len(test_results) == 0:
                    logger.info("Tabela existe mas parece estar vazia, populando com dados dos artigos...")
                    self._populate_vectorstore_from_artigos(vectorstore, documents)
                else:
                    logger.info(f"Vectorstore já contém {len(test_results)} documentos (teste)")
            except Exception as e:
                logger.info(f"Criando novo vectorstore com dados dos artigos: {e}")
                self._populate_vectorstore_from_artigos(vectorstore, documents)
            
            logger.info("Vectorstore configurado para usar embeddings da tabela artigo")
            return vectorstore
            
        except Exception as e:
            logger.error(f"Erro ao configurar vectorstore: {e}")
            raise

    def _populate_vectorstore_from_artigos(self, vectorstore: PGVector, documents: List[Document]):
        """Popula o vectorstore usando embeddings já existentes da tabela artigo."""
        try:
            # Buscar artigos que já possuem embeddings
            artigos = self.artigo_dao.listar_artigos_com_embeddings()
            
            if not artigos:
                raise ValueError("Nenhum artigo com embeddings encontrado na tabela artigo")
            
            logger.info(f"Encontrados {len(artigos)} artigos com embeddings")
            
            # Usar DTO para converter artigos para documentos
            documents_to_add = ArticleDocumentDTO.artigos_to_documents(artigos)
            
            # Preparar dados para o vectorstore
            texts = [doc.page_content for doc in documents_to_add]
            metadatas = [doc.metadata for doc in documents_to_add]
            
            # Adicionar documentos ao vectorstore
            # Para PGVector da langchain_community, usamos add_texts
            vectorstore.add_texts(
                texts=texts,
                metadatas=metadatas
            )
            
            logger.info(f"Adicionados {len(texts)} documentos ao vectorstore")
            
        except Exception as e:
            logger.error(f"Erro ao popular vectorstore: {e}")
            raise
    
    def initialize_retriever(self, limit_documents: Optional[int] = None) -> SelfQueryRetriever:
        """
        Inicializa o SelfQueryRetriever usando embeddings da tabela artigo.
        
        Args:
            limit_documents: Limite de documentos para processar (útil para testes)
            
        Returns:
            SelfQueryRetriever configurado
        """
        try:
            # Criar documentos (apenas para estrutura, embeddings vêm da tabela)
            documents = self._create_documents_from_artigos(limit_documents)
            
            if not documents:
                raise ValueError("Nenhum documento foi criado")
            
            # Gerar chave de cache simples
            cache_key = "artigo_table"
            
            # Configurar vectorstore usando embeddings da tabela artigo
            self._vectorstore = self._setup_vectorstore(documents, cache_key)

            # Criar SelfQueryRetriever
            self.retriever = SelfQueryRetriever.from_llm(
                llm=self.llm,
                document_contents=self.document_content_description,
                metadata_field_info=self.attribute_infos,
                vectorstore=self._vectorstore,
                structured_query_translator=PGVectorTranslator(),
                verbose=True
            )
            
            logger.info("SelfQueryRetriever inicializado usando embeddings da tabela artigo")
            return self.retriever
            
        except Exception as e:
            logger.error(f"Erro ao inicializar retriever: {e}")
            raise
    
    def query(self, query_text: str, k: int = 5) -> List[Document]:
        """
        Executa uma consulta usando o SelfQueryRetriever.
        
        Args:
            query_text: Consulta em linguagem natural
            k: Número de documentos a retornar
            
        Returns:
            Lista de documentos relevantes
        """
        if self.retriever is None:
            self.initialize_retriever()
        
        try:
            # Configurar parâmetros de busca
            self.retriever.search_kwargs = {"k": k}
            
            # Executar consulta
            results = self.retriever.invoke(query_text)
            
            logger.info(f"Consulta executada: '{query_text}' - {len(results)} resultados")
            # Salvar consulta e resultados em arquivo
            with open("query_results.txt", "a", encoding="utf-8") as f:
                # Obter a query estruturada gerada pelo retriever
                structured_query = getattr(self.retriever, "last_query", None)
                if structured_query is None and hasattr(self.retriever, "query_constructor"):
                    # Tenta obter a query estruturada do output_parser
                    try:
                        structured_query = self.retriever.query_constructor.invoke(query_text)
                    except Exception:
                        structured_query = None

                f.write(f"Consulta: {query_text}\n")
                f.write(f"Query estruturada: {structured_query}\n")
                for i, doc in enumerate(results, 1):
                    f.write(f"{i}. {doc.page_content[:100]}...\n")
                    f.write(f"   Metadados: {doc.metadata}\n")
                f.write("\n")
            return results
            
        except Exception as e:
            logger.error(f"Erro ao executar consulta: {e}")
            return []