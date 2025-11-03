import json
import logging
import os
import sys
from typing import List, Dict, Any


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain.chains.query_constructor.base import (
    StructuredQueryOutputParser,
    get_query_constructor_prompt,
)
from langchain.chains.query_constructor.schema import AttributeInfo
from langchain_openai import ChatOpenAI

from dao.artigo_dao import ArtigoDAO
from service.embedding import EmbeddingService
from banco.conexao_db import Conexao

COLLECTION_NAME = "artigo"
LLM_MODEL = "gpt-5-mini-2025-08-07"
LLM_TEMPERATURE = 0

logger = logging.getLogger(__name__)


class SelfQueryRetrieverService:
    """
    Serviço para realizar busca usando SelfQueryRetriever baseado no PGVector.
    Usa embeddings já armazenados na coluna embedding da tabela artigo.
    """

    def __init__(
        self
    ):
        """
        Inicializa o serviço de Self Query Retriever com PGVector.

        Args:
            connection_string: String de conexão PostgreSQL (opcional, usa configurações se None)
            collection_name: Nome da coleção no PGVector
        """

        self.embedding_service = EmbeddingService()

        self.llm = ChatOpenAI(
            api_key=self.embedding_service.embeddings_client.openai_api_key,
            model=LLM_MODEL,
        )

        self.reload_query_constructor()

    def reload_query_constructor(self):
        self.metadata_config = self._load_metadata_config()
        self.attribute_infos = self._build_attribute_infos()

        self.document_content_description = (
            self.metadata_config.get("document_content_description")
            or "Artigos científicos com título, resumo e metadados de publicação acadêmica"
        )

        prompt = get_query_constructor_prompt(
            self.document_content_description,
            self.attribute_infos,
        )
        output_parser = StructuredQueryOutputParser.from_components()
        self.query_constructor = prompt | self.llm | output_parser

    def _load_metadata_config(self) -> Dict[str, Any]:
        """Carrega configuração de metadados do arquivo JSON."""
        relative_config_dir = "../../config"
        config_filename = "metadata_config.json"
        base_dir = os.path.dirname(__file__)
        try:
            config_path = os.path.join(base_dir, relative_config_dir, config_filename)
            if not os.path.exists(config_path):
                logger.warning(
                    f"Arquivo de configuração não encontrado em {config_path}"
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

        logger.info(f"Found {len(attribute_infos)} attribute infos")
        logger.info(f"Attribute infos: {attribute_infos}")

        return attribute_infos
