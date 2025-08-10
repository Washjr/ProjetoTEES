import json
import logging
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

from model.dto.artigo_busca_dto import ArtigoBuscaDTO
from model.mapper.artigo_dto_mapper import ArtigoDTOMapper

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain.chains.query_constructor.base import (
    StructuredQueryOutputParser,
    get_query_constructor_prompt,
)
from langchain.chains.query_constructor.schema import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_community.vectorstores import PGVector
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

from dao.artigo_dao import ArtigoDAO
from service.embedding import EmbeddingService
from banco.conexao_db import Conexao

COLLECTION_NAME = "artigo"
LLM_MODEL = "gpt-3.5-turbo"
LLM_TEMPERATURE = 0

logger = logging.getLogger(__name__)


class SelfQueryRetrieverService:
    """
    Serviço para realizar busca usando SelfQueryRetriever baseado no PGVector.
    Usa embeddings já armazenados na coluna embedding da tabela artigo.
    """

    def __init__(
        self,
        connection_string: str = Conexao.get_connection_string(),
        collection_name: str = COLLECTION_NAME,
    ):
        """
        Inicializa o serviço de Self Query Retriever com PGVector.

        Args:
            connection_string: String de conexão PostgreSQL (opcional, usa configurações se None)
            collection_name: Nome da coleção no PGVector
        """
        self.connection_string = connection_string
        self.collection_name = collection_name

        self.artigo_dao = ArtigoDAO()
        self.embedding_service = EmbeddingService()
        self.metadata_config = self._load_metadata_config()

        self.llm = ChatOpenAI(
            temperature=LLM_TEMPERATURE,
            api_key=self.embedding_service.embeddings_client.openai_api_key,
            model=LLM_MODEL,
        )

        self.attribute_infos = self._build_attribute_infos()

        self.document_content_description = self.metadata_config.get(
            "document_content_description",
            "Artigos científicos com título, resumo e metadados de publicação acadêmica",
        )

        prompt = get_query_constructor_prompt(
            self.document_content_description,
            self.attribute_infos,
        )
        output_parser = StructuredQueryOutputParser.from_components()
        self.query_constructor = prompt | self.llm | output_parser

        self.retriever = None
        self._vectorstore = None

    def _load_metadata_config(self) -> Dict[str, Any]:
        """Carrega configuração de metadados do arquivo JSON."""
        try:
            config_path = Path("config/metadata_config.json")
            if not config_path.exists():
                config_path = (
                    Path(__file__).parent.parent / "config" / "metadata_config.json"
                )

            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar metadata_config.json: {e}")
            return {
                "metadata_fields": [],
                "document_content_description": "Artigos científicos com título, resumo e metadados de publicação acadêmica",
            }

    def _build_attribute_infos(self) -> List[AttributeInfo]:
        """Constrói lista de AttributeInfo objects baseados na configuração."""
        attribute_infos = []

        for field_config in self.metadata_config.get("metadata_fields", []):
            name = field_config["name"]
            description = field_config["description"]
            field_type = field_config["type"]

            attr_type = field_type

            attr_info = AttributeInfo(
                name=name, description=description, type=attr_type
            )

            attribute_infos.append(attr_info)

        return attribute_infos

    def _create_vectorstore_with_embeddings(
        self, documents: List[Document]
    ) -> PGVector:
        """Configura o vectorstore com PGVector usando embeddings existentes."""
        logger.info(
            "Criando vectorstore no PGVector usando embeddings existentes da tabela artigo..."
        )

        try:
            vectorstore = PGVector(
                connection_string=self.connection_string,
                embedding_function=self.embedding_service.embeddings_client,
                collection_name=self.collection_name,
            )

            try:
                test_results = vectorstore.similarity_search("test", k=1)
                if len(test_results) == 0:
                    logger.info(
                        "Tabela existe mas parece estar vazia, populando com dados dos artigos..."
                    )
                    self._refresh_vectorstore_with_docs(vectorstore, documents)
                else:
                    logger.info(
                        f"Vectorstore já contém {len(test_results)} documentos (teste)"
                    )
            except Exception as e:
                logger.info(f"Criando novo vectorstore com dados dos artigos: {e}")
                self._refresh_vectorstore_with_docs(vectorstore, documents)

            logger.info("Vectorstore configurado para usar embeddings da tabela artigo")
            return vectorstore

        except Exception as e:
            logger.error(f"Erro ao configurar vectorstore: {e}")
            raise

    def _refresh_vectorstore_with_docs(
        self, vectorstore: PGVector, documents: List[Document]
    ):
        try:
            texts = [doc.page_content for doc in documents]
            metadatas = [doc.metadata for doc in documents]

            vectorstore.delete_collection()
            vectorstore.add_texts(texts=texts, metadatas=metadatas)

            logger.info(f"Adicionados {len(texts)} documentos ao vectorstore")

        except Exception as e:
            logger.error(f"Erro ao popular vectorstore: {e}")
            raise

    def initialize_retriever(
        self, limit_documents: Optional[int] = None
    ) -> SelfQueryRetriever:
        """
        Inicializa o SelfQueryRetriever usando embeddings da tabela artigo.

        Args:
            limit_documents: Limite de documentos para processar (útil para testes)

        Returns:
            SelfQueryRetriever configurado
        """
        try:
            documents = self._get_document_list_from_articles_database(limit_documents)

            if not documents:
                raise ValueError("Nenhum documento foi criado")

            self._vectorstore = self._create_vectorstore_with_embeddings(documents)

            self.retriever = SelfQueryRetriever.from_llm(
                llm=self.llm,
                document_contents=self.document_content_description,
                metadata_field_info=self.attribute_infos,
                vectorstore=self._vectorstore,
                verbose=True,
            )

            logger.info(
                "SelfQueryRetriever inicializado usando embeddings da tabela artigo"
            )
            return self.retriever

        except Exception as e:
            logger.error(f"Erro ao inicializar retriever: {e}")
            raise

    def _get_document_list_from_articles_database(
        self, limit_documents: Optional[int] = None
    ) -> List[Document]:
        """
        Cria documentos a partir dos artigos com embeddings.

        Args:
            limit_documents: Limite de documentos a processar (útil para testes)

        Returns:
            Lista de documentos criados
        """
        artigos = self.artigo_dao.listar_artigos_com_embeddings()

        if not artigos:
            logger.warning("Nenhum artigo encontrado com embeddings")
            return []

        if limit_documents is not None:
            artigos = artigos[:limit_documents]

        logger.info(f"Convertendo {len(artigos)} artigos em documentos")
        return ArtigoDTOMapper.to_document_list(
            [ArtigoBuscaDTO.from_orm(artigo) for artigo in artigos]
        )

    def create_temporary_retriever(
        self, documents: List[Document]
    ) -> Optional[SelfQueryRetriever]:
        """
        Cria um retriever temporário usando Chroma com os documentos fornecidos.
        Deve ser usado para consultas com self-query.

        Args:
            documents (List[Document]): Lista de documentos a serem usados no retriever.

        Returns:
            Optional[SelfQueryRetriever]: Um retriever temporário configurado com os documentos fornecidos, None se ocorrer um erro.
        """
        try:
            vectorstore_temp = self._create_vectorstore_with_embeddings(documents)

            retriever_temp = SelfQueryRetriever.from_llm(
                llm=self.llm,
                document_contents=self.document_content_description,
                metadata_field_info=self.attribute_infos,
                vectorstore=vectorstore_temp,
                verbose=True,
                enable_limit=False,
            )
            return retriever_temp

        except Exception as e:
            logger.error(f"Erro ao criar retriever temporário: {e}")
            return None

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
            if self.retriever is None:
                raise RuntimeError(
                    "Retriever não inicializado. Chame initialize_retriever primeiro."
                )

            self.retriever.search_kwargs = {"k": k}
            results = self.retriever.invoke(query_text)

            logger.info(
                f"Consulta executada: '{query_text}' - {len(results)} resultados"
            )
            return results

        except Exception as e:
            logger.error(f"Erro ao executar consulta: {e}")
            return []
