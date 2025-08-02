import logging
from typing import Dict, Any, List

from service.embedding import EmbeddingService
from service.embedding.embedding_service import EmbeddingResult

logger = logging.getLogger(__name__)


class EmbeddingController:
    """
    Controller para operações relacionadas a embeddings.
    Responsável por gerenciar requests relacionados a busca semântica e embeddings.
    """

    def __init__(self):
        self.embedding_service = EmbeddingService()

    def search_similar_articles(
        self, 
        query: str, 
        limit: int = 10, 
        threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Busca artigos similares ao texto da consulta.
        
        Args:
            query: Texto da consulta
            limit: Número máximo de resultados
            threshold: Limiar mínimo de similaridade
            
        Returns:
            Dicionário com resultados da busca
        """
        try:
            if not query or not query.strip():
                return {
                    "success": False,
                    "error": "Query não pode ser vazia",
                    "results": []
                }

            results = self.embedding_service.search_similar_articles(
                query_text=query,
                limit=limit,
                threshold=threshold
            )

            return {
                "success": True,
                "query": query,
                "total_found": len(results),
                "results": [self._format_result(result) for result in results],
                "parameters": {
                    "limit": limit,
                    "threshold": threshold
                }
            }

        except Exception as e:
            logger.error(f"Erro na busca por similaridade: {e}")
            return {
                "success": False,
                "error": f"Erro interno: {str(e)}",
                "results": []
            }

    def update_article_embeddings(self) -> Dict[str, Any]:
        """
        Atualiza embeddings de todos os artigos.
        
        Returns:
            Dicionário com estatísticas do processo
        """
        try:
            stats = self.embedding_service.update_all_article_embeddings()
            
            return {
                "success": True,
                "message": "Embeddings atualizados com sucesso",
                "statistics": stats
            }

        except Exception as e:
            logger.error(f"Erro ao atualizar embeddings: {e}")
            return {
                "success": False,
                "error": f"Erro interno: {str(e)}",
                "statistics": {"success": 0, "errors": 1, "skipped": 0}
            }

    def get_embedding_statistics(self) -> Dict[str, Any]:
        """
        Obtém estatísticas sobre embeddings armazenados.
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            stats = self.embedding_service.get_embedding_stats()
            
            return {
                "success": True,
                "statistics": stats
            }

        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {
                "success": False,
                "error": f"Erro interno: {str(e)}",
                "statistics": {}
            }

    def generate_article_embedding(self, article_id: int, title: str, abstract: str) -> Dict[str, Any]:
        """
        Gera e armazena embedding para um artigo específico.
        
        Args:
            article_id: ID do artigo
            title: Título do artigo
            abstract: Resumo do artigo
            
        Returns:
            Dicionário com resultado da operação
        """
        try:
            if not title and not abstract:
                return {
                    "success": False,
                    "error": "Título ou resumo devem ser fornecidos",
                    "article_id": article_id
                }

            content = self._build_content(title, abstract)
            success = self.embedding_service.store_article_embedding(article_id, content)

            return {
                "success": success,
                "message": "Embedding gerado com sucesso" if success else "Falha ao gerar embedding",
                "article_id": article_id
            }

        except Exception as e:
            logger.error(f"Erro ao gerar embedding para artigo {article_id}: {e}")
            return {
                "success": False,
                "error": f"Erro interno: {str(e)}",
                "article_id": article_id
            }

    def clear_embedding_cache(self) -> Dict[str, Any]:
        """
        Limpa cache de embeddings.
        
        Returns:
            Dicionário com resultado da operação
        """
        try:
            self.embedding_service.clear_cache()
            
            return {
                "success": True,
                "message": "Cache limpo com sucesso"
            }

        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
            return {
                "success": False,
                "error": f"Erro interno: {str(e)}"
            }

    def _format_result(self, result: EmbeddingResult) -> Dict[str, Any]:
        """
        Formata resultado de busca para resposta da API.
        
        Args:
            result: Resultado da busca
            
        Returns:
            Dicionário formatado
        """
        return {
            "id": result.id,
            "title": result.metadata.get("title"),
            "abstract": result.metadata.get("abstract"),
            "doi": result.metadata.get("doi"),
            "year": result.metadata.get("year"),
            "journal": result.metadata.get("journal"),
            "qualis": result.metadata.get("qualis"),
            "author_name": result.metadata.get("author_name"),
            "similarity_score": round(result.similarity_score, 4)
        }

    def _build_content(self, title: str, abstract: str) -> str:
        """
        Constrói conteúdo textual para embedding.
        
        Args:
            title: Título do artigo
            abstract: Resumo do artigo
            
        Returns:
            Conteúdo formatado
        """
        content_parts = []
        
        if title and title.strip():
            content_parts.append(f"Título: {title.strip()}")
            
        if abstract and abstract.strip():
            content_parts.append(f"Resumo: {abstract.strip()}")
            
        return " | ".join(content_parts)
