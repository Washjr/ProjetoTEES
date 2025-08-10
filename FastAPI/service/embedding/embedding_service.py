import hashlib
import logging
from typing import List, Dict, Any
from dataclasses import dataclass

import psycopg2
from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr
from psycopg2.extras import RealDictCursor

from banco.conexao_db import Conexao
from config import configuracoes
from .interface import IEmbeddingService


OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536
SIMILARITY_THRESHOLD = 0.7
CACHE_SIZE = 1000

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingResult:
    """Resultado de busca por similaridade"""
    id: int
    content: str
    similarity_score: float
    metadata: Dict[str, Any]


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
            api_key=SecretStr(configuracoes.OPENAI_API_KEY)
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

    def search_similar_articles(
        self, 
        query_text: str, 
        limit: int = 10, 
        threshold: float = SIMILARITY_THRESHOLD
    ) -> List[EmbeddingResult]:
        """
        Busca artigos similares usando similaridade por cosseno.
        """
        try:
            query_embedding = self.generate_embedding(query_text)
            return self._execute_similarity_search(query_embedding, limit, threshold)
            
        except Exception as e:
            logger.error(f"Erro na busca por similaridade: {e}")
            return []

    def update_all_article_embeddings(self) -> Dict[str, int]:
        """
        Atualiza embeddings de todos os artigos no banco.
        Retorna estatísticas do processo.
        """
        stats = {"success": 0, "errors": 0, "skipped": 0}
        
        try:
            articles = self._fetch_articles_without_embeddings()
            
            for article in articles:
                if self._process_article_embedding(article):
                    stats["success"] += 1
                else:
                    stats["errors"] += 1
                    
        except Exception as e:
            logger.error(f"Erro ao atualizar embeddings: {e}")
            stats["errors"] += 1

        return stats

    def clear_cache(self) -> None:
        """Limpa o cache de embeddings"""
        self._cache.clear()
        logger.info("Cache de embeddings limpo")

    def get_embedding_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas sobre embeddings armazenados"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_articles,
                        COUNT(embedding) as articles_with_embeddings,
                        COUNT(*) - COUNT(embedding) as articles_without_embeddings
                    FROM artigo
                """)
                
                result = cursor.fetchone()
                return dict(result) if result else {}
                
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {}

    def _generate_text_hash(self, text: str) -> str:
        """Gera hash único para o texto"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def _update_cache(self, text_hash: str, embedding: List[float]) -> None:
        """Atualiza cache mantendo tamanho máximo"""
        if len(self._cache) >= CACHE_SIZE:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        
        self._cache[text_hash] = embedding

    def _save_embedding_to_database(self, article_id: int, embedding: List[float]) -> bool:
        """Salva embedding no banco de dados"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE artigo SET embedding = %s WHERE id_artigo = %s",
                    (embedding, article_id)
                )
                self.connection.commit()
                return cursor.rowcount > 0
                
        except psycopg2.Error as e:
            logger.error(f"Erro ao salvar embedding no banco: {e}")
            self.connection.rollback()
            return False

    def _execute_similarity_search(
        self, 
        query_embedding: List[float], 
        limit: int, 
        threshold: float
    ) -> List[EmbeddingResult]:
        """Executa busca por similaridade usando PGVector"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        a.id_artigo as id,
                        a.nome as title,
                        a.resumo as abstract,
                        a.doi,
                        a.ano as year,
                        per.nome as journal,
                        per.qualis,
                        p.id_pesquisador as author_id,
                        p.nome as author_name,
                        (1 - (a.embedding <=> %s::vector)) as similarity_score
                    FROM artigo a
                    JOIN periodico per ON a.id_periodico = per.id_periodico  
                    JOIN pesquisador p ON a.id_pesquisador = p.id_pesquisador
                    WHERE a.embedding IS NOT NULL 
                        AND (1 - (a.embedding <=> %s::vector)) >= %s
                    ORDER BY a.embedding <=> %s::vector
                    LIMIT %s
                """, (query_embedding, query_embedding, threshold, query_embedding, limit))
                
                results = cursor.fetchall()
                return self._convert_to_embedding_results(results)
                
        except psycopg2.Error as e:
            logger.error(f"Erro na busca por similaridade: {e}")
            return []

    def _fetch_articles_without_embeddings(self) -> List[Dict[str, Any]]:
        """Busca artigos que não possuem embeddings"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id_artigo, nome, resumo 
                    FROM artigo 
                    WHERE embedding IS NULL 
                        AND nome IS NOT NULL
                """)
                
                return cursor.fetchall()
                
        except psycopg2.Error as e:
            logger.error(f"Erro ao buscar artigos sem embeddings: {e}")
            return []

    def _process_article_embedding(self, article: Dict[str, Any]) -> bool:
        """Processa embedding de um artigo específico"""
        try:
            content = self._build_article_content(article)
            return self.store_article_embedding(article["id_artigo"], content)
            
        except Exception as e:
            logger.error(f"Erro ao processar artigo {article.get('id_artigo')}: {e}")
            return False

    def _build_article_content(self, article: Dict[str, Any]) -> str:
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

    def _convert_to_embedding_results(self, raw_results: List[Dict]) -> List[EmbeddingResult]:
        """Converte resultados do banco para objetos EmbeddingResult"""
        results = []
        
        for row in raw_results:
            metadata = {
                "title": row.get("title"),
                "abstract": row.get("abstract"),
                "doi": row.get("doi"),
                "year": row.get("year"),
                "journal": row.get("journal"),
                "qualis": row.get("qualis"),
                "author_id": row.get("author_id"),
                "author_name": row.get("author_name")
            }
            
            result = EmbeddingResult(
                id=row["id"],
                content=f"{row.get('title', '')} - {row.get('abstract', '')}",
                similarity_score=float(row["similarity_score"]),
                metadata=metadata
            )
            
            results.append(result)
        
        return results

    def __del__(self):
        """Devolve conexão ao pool"""
        if hasattr(self, 'connection'):
            Conexao.devolver_conexao(self.connection)
