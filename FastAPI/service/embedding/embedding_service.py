import hashlib
import logging
from typing import List, Dict, Any

from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr

from banco.conexao_db import Conexao
from config import configuracoes
from .interface import IEmbeddingService
from dao.artigo_dao import ArtigoDAO

OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536
SIMILARITY_THRESHOLD = 0.3
CACHE_SIZE = 1000

logger = logging.getLogger(__name__)

class EmbeddingService(IEmbeddingService):
    """
    Serviço centralizado para gerenciamento de embeddings usando PGVector.
    Responsável por criar, armazenar e buscar embeddings de documentos.
    """

    def __init__(self):
        self._validate_configuration()
        self.embeddings_client = self._create_embeddings_client()
        self.connection = Conexao.obter_conexao()
        self._cache = {}

    def _validate_configuration(self) -> None:
        """Valida se as configurações necessárias estão presentes"""
        if not configuracoes.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY não configurada")

    def _create_embeddings_client(self) -> OpenAIEmbeddings:
        return OpenAIEmbeddings(
            model=OPENAI_EMBEDDING_MODEL,
            api_key=SecretStr(configuracoes.OPENAI_API_KEY),
        )

    def generate_embedding(self, text: str) -> List[float]:
        """
        Gera embedding para um texto.
        Utiliza cache para otimizar performance.
        """
        if not text or not text.strip():
            raise ValueError("Texto não pode ser vazio")

        text_hash = self._generate_text_hash(text)

        if text_hash in self._cache:
            return self._cache[text_hash]

        try:
            embedding = self.embeddings_client.embed_query(text)
            self._update_cache(text_hash, embedding)
            return embedding

        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            raise RuntimeError(f"Falha na geração de embedding: {str(e)}")

    def store_article_embedding(self, article_id: int, text: str) -> bool:
        """
        Armazena embedding de artigo no banco de dados.
        """
        try:
            embedding = self.generate_embedding(text)
            return self._save_embedding_to_database(article_id, embedding)

        except Exception as e:
            logger.error(f"Erro ao armazenar embedding do artigo {article_id}: {e}")
            return False

    def update_all_article_embeddings(self) -> Dict[str, int]:
        """
        Atualiza embeddings de todos os artigos no banco.
        Retorna estatísticas do processo.
        """
        
        stats = {"success": 0, "errors": 0, "skipped": 0}

        try:
            artigo_dao = ArtigoDAO()
            articles = artigo_dao.listar_artigos_sem_embeddings()

            for article in articles:
                if self._process_article_embedding(article):
                    stats["success"] += 1
                else:
                    stats["errors"] += 1

        except Exception as e:
            logger.error(f"Erro ao atualizar embeddings: {e}")
            stats["errors"] += 1

        return stats

    def _process_article_embedding(self, article: Dict[str, Any]) -> bool:
        """Processa embedding de um artigo específico"""
        
        try:
            content = self.build_article_content(article)
            embedding = self.generate_embedding(content)
            
            artigo_dao = ArtigoDAO()
            return artigo_dao.atualizar_embedding_artigo(article["id_artigo"], embedding)

        except Exception as e:
            logger.error(f"Erro ao processar artigo {article.get('id_artigo')}: {e}")
            return False

    def clear_cache(self) -> None:
        """Limpa o cache de embeddings"""
        self._cache.clear()
        logger.info("Cache de embeddings limpo")

    def build_article_content(self, article: Dict[str, Any]) -> str:
        """Constrói conteúdo textual do artigo para embedding"""
        title = (article.get("nome") or "").strip()
        abstract = (article.get("resumo") or "").strip()

        if not title and not abstract:
            raise ValueError("Artigo sem título ou resumo")

        content_parts = []
        if title:
            content_parts.append(f"Título: {title}")
        if abstract:
            content_parts.append(f"Resumo: {abstract}")

        return " | ".join(content_parts)

    def _generate_text_hash(self, text: str) -> str:
        """Gera hash único para o texto"""
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    def _update_cache(self, text_hash: str, embedding: List[float]) -> None:
        """Atualiza cache mantendo tamanho máximo"""
        if len(self._cache) >= CACHE_SIZE:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

        self._cache[text_hash] = embedding

    def _save_embedding_to_database(
        self, article_id: int, embedding: List[float]
    ) -> bool:
        """Salva embedding no banco de dados"""
        
        try:
            artigo_dao = ArtigoDAO()
            return artigo_dao.atualizar_embedding_artigo(article_id, embedding)
        except Exception as e:
            logger.error(f"Erro ao salvar embedding no banco: {e}")
            return False

    def __del__(self):
        """Devolve conexão ao pool"""
        if hasattr(self, "connection"):
            Conexao.devolver_conexao(self.connection)
