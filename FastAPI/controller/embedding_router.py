import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from controller.embedding_controller import EmbeddingController

logger = logging.getLogger(__name__)

embedding_router = APIRouter(prefix="/embeddings", tags=["embeddings"])


def get_embedding_controller() -> EmbeddingController:
    """Factory function para criar EmbeddingController"""
    return EmbeddingController()


class ArticleEmbeddingRequest(BaseModel):
    """Request para gerar embedding de artigo específico"""
    article_id: int
    title: str
    abstract: str


class SearchRequest(BaseModel):
    """Request para busca por similaridade"""
    query: str
    limit: Optional[int] = 10
    threshold: Optional[float] = 0.7


@embedding_router.post("/search")
def search_similar_articles(request: SearchRequest):
    """
    Busca artigos similares usando embeddings e PGVector.
    
    Args:
        request: Dados da consulta de busca
        
    Returns:
        Lista de artigos similares com scores de similaridade
    """
    try:
        embedding_controller = get_embedding_controller()
        return embedding_controller.search_similar_articles(
            query=request.query,
            limit=request.limit,
            threshold=request.threshold
        )
    except Exception as e:
        logger.error(f"Erro na busca por similaridade: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@embedding_router.get("/search")
def search_similar_articles_get(
    query: str = Query(..., description="Texto da consulta"),
    limit: int = Query(10, description="Número máximo de resultados"),
    threshold: float = Query(0.7, description="Limiar mínimo de similaridade")
):
    """
    Busca artigos similares usando embeddings (versão GET).
    
    Args:
        query: Texto da consulta
        limit: Número máximo de resultados
        threshold: Limiar mínimo de similaridade
        
    Returns:
        Lista de artigos similares com scores de similaridade
    """
    try:
        embedding_controller = get_embedding_controller()
        return embedding_controller.search_similar_articles(
            query=query,
            limit=limit,
            threshold=threshold
        )
    except Exception as e:
        logger.error(f"Erro na busca por similaridade: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@embedding_router.post("/update-all")
def update_all_embeddings():
    """
    Atualiza embeddings de todos os artigos no banco de dados.
    
    Returns:
        Estatísticas do processo de atualização
    """
    try:
        embedding_controller = get_embedding_controller()
        return embedding_controller.update_article_embeddings()
    except Exception as e:
        logger.error(f"Erro ao atualizar embeddings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@embedding_router.post("/article")
def generate_article_embedding(request: ArticleEmbeddingRequest):
    """
    Gera e armazena embedding para um artigo específico.
    
    Args:
        request: Dados do artigo para gerar embedding
        
    Returns:
        Resultado da operação
    """
    try:
        embedding_controller = get_embedding_controller()
        return embedding_controller.generate_article_embedding(
            article_id=request.article_id,
            title=request.title,
            abstract=request.abstract
        )
    except Exception as e:
        logger.error(f"Erro ao gerar embedding: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@embedding_router.get("/statistics")
def get_embedding_statistics():
    """
    Obtém estatísticas sobre embeddings armazenados.
    
    Returns:
        Estatísticas dos embeddings
    """
    try:
        embedding_controller = get_embedding_controller()
        return embedding_controller.get_embedding_statistics()
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@embedding_router.delete("/cache")
def clear_embedding_cache():
    """
    Limpa cache de embeddings em memória.
    
    Returns:
        Resultado da operação
    """
    try:
        embedding_controller = get_embedding_controller()
        return embedding_controller.clear_embedding_cache()
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))
