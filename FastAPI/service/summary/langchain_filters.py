from typing import List, Dict, Optional
from langchain_openai import OpenAIEmbeddings
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging
from .langchain_config import LangchainConfig
from .langchain_formatters import EmbeddingCache, DocumentFormatter
from .langchain_processors import ChunkProcessor

logger = logging.getLogger(__name__)


class SimilarityFilter:
    """Responsável por filtrar conteúdo baseado em similaridade"""
    
    def __init__(self, config: LangchainConfig, embedding_cache: EmbeddingCache):
        self.config = config
        self.embedding_cache = embedding_cache
    
    def filter_relevant_chunks(self, user_query: str, documentos: List[Dict], 
                             doc_type: str, embedder: OpenAIEmbeddings,
                             formatter: DocumentFormatter, 
                             chunk_processor: ChunkProcessor,
                             max_chunks: Optional[int] = None) -> List[Dict]:
        """Filtra chunks mais relevantes usando embeddings"""
        max_chunks = max_chunks or self.config.MAX_CHUNKS_TOTAL
        
        if not documentos or not user_query:
            return documentos
        
        try:
            query_embedding = self.embedding_cache.get_or_create_embedding(user_query, embedder)
            all_chunks = self._create_all_chunks(documentos, doc_type, formatter, chunk_processor)
            
            if not all_chunks:
                return documentos
            
            relevant_chunks = self._find_most_similar_chunks(query_embedding, all_chunks, embedder, max_chunks)
            
            logger.info(f"Filtrados {len(relevant_chunks)} chunks mais relevantes de {len(all_chunks)} totais")
            return relevant_chunks
            
        except Exception as e:
            logger.warning(f"Erro ao filtrar chunks: {e}")
            return documentos
    
    def filter_relevant_documents(self, user_query: str, documentos: List[Dict], 
                                doc_type: str, embedder: OpenAIEmbeddings,
                                formatter: DocumentFormatter,
                                max_docs: Optional[int] = None) -> List[Dict]:
        """Filtra documentos mais relevantes usando embeddings"""
        max_docs = max_docs or self.config.MAX_DOCS_FOR_TAGS
        
        if not documentos or not user_query:
            return documentos[:max_docs]
        
        try:
            query_embedding = embedder.embed_query(user_query)
            doc_texts = [formatter.format_for_display(doc, doc_type) for doc in documentos]
            doc_embeddings = embedder.embed_documents(doc_texts)
            
            similarities = self._calculate_similarities(query_embedding, doc_embeddings)
            relevant_docs = self._get_top_documents(documentos, similarities, max_docs)
            
            logger.info(f"Filtrados {len(relevant_docs)} documentos mais relevantes de {len(documentos)} totais")
            return relevant_docs
            
        except Exception as e:
            logger.warning(f"Erro ao filtrar documentos: {e}")
            return documentos[:max_docs]
    
    def _create_all_chunks(self, documentos: List[Dict], doc_type: str, 
                          formatter: DocumentFormatter, 
                          chunk_processor: ChunkProcessor) -> List[Dict]:
        """Cria chunks para todos os documentos"""
        all_chunks = []
        
        for doc_idx, doc in enumerate(documentos):
            text = formatter.format_for_display(doc, doc_type)
            chunks = chunk_processor.create_semantic_chunks(text, str(doc_idx))
            
            for chunk in chunks:
                chunk['original_doc'] = doc
                chunk['doc_type'] = doc_type
                all_chunks.append(chunk)
        
        return all_chunks
    
    def _find_most_similar_chunks(self, query_embedding: List[float], 
                                 all_chunks: List[Dict], 
                                 embedder: OpenAIEmbeddings,
                                 max_chunks: int) -> List[Dict]:
        """Encontra os chunks mais similares à query"""
        chunk_embeddings = [
            self.embedding_cache.get_or_create_embedding(chunk['text'], embedder)
            for chunk in all_chunks
        ]
        
        similarities = self._calculate_similarities(query_embedding, chunk_embeddings)
        
        # Filtrar por threshold
        chunk_similarity_pairs = [
            (chunk, sim) for chunk, sim in zip(all_chunks, similarities)
            if sim >= self.config.SIMILARITY_THRESHOLD
        ]
        
        # Se não houver chunks acima do threshold, usar todos
        if not chunk_similarity_pairs:
            chunk_similarity_pairs = list(zip(all_chunks, similarities))
        
        # Ordenar por relevância e pegar os top
        chunk_similarity_pairs.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in chunk_similarity_pairs[:max_chunks]]
    
    def _calculate_similarities(self, query_embedding: List[float], 
                               doc_embeddings: List[List[float]]) -> np.ndarray:
        """Calcula similaridades de cosseno"""
        query_emb = np.array(query_embedding).reshape(1, -1)
        doc_embs = np.array(doc_embeddings)
        return cosine_similarity(query_emb, doc_embs)[0]
    
    def _get_top_documents(self, documentos: List[Dict], similarities: np.ndarray, 
                          max_docs: int) -> List[Dict]:
        """Obtém os documentos com maior similaridade"""
        doc_similarity_pairs = list(zip(documentos, similarities))
        doc_similarity_pairs.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in doc_similarity_pairs[:max_docs]]
