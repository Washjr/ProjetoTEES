from abc import ABC, abstractmethod
from typing import List, Dict, Any


class IEmbeddingService(ABC):
    """
    Interface para serviços de embedding.
    Define o contrato para operações de embedding seguindo o princípio da inversão de dependência.
    """

    @abstractmethod
    def generate_embedding(self, text: str) -> List[float]:
        """
        Gera embedding para um texto.
        
        Args:
            text: Texto para gerar embedding
            
        Returns:
            Lista de floats representando o embedding
            
        Raises:
            ValueError: Se o texto for inválido
            RuntimeError: Se houver erro na geração
        """
        pass

    @abstractmethod
    def store_article_embedding(self, article_id: int, text: str) -> bool:
        """
        Armazena embedding de artigo no banco de dados.
        
        Args:
            article_id: ID do artigo
            text: Conteúdo textual do artigo
            
        Returns:
            True se armazenado com sucesso, False caso contrário
        """
        pass

    @abstractmethod
    def search_similar_articles(
        self, 
        query_text: str, 
        limit: int = 10, 
        threshold: float = 0.7
    ) -> List[Any]:
        """
        Busca artigos similares usando similaridade semântica.
        
        Args:
            query_text: Texto da consulta
            limit: Número máximo de resultados
            threshold: Limiar mínimo de similaridade
            
        Returns:
            Lista de resultados ordenados por similaridade
        """
        pass

    @abstractmethod
    def update_all_article_embeddings(self) -> Dict[str, int]:
        """
        Atualiza embeddings de todos os artigos.
        
        Returns:
            Dicionário com estatísticas do processo
        """
        pass

    @abstractmethod
    def clear_cache(self) -> None:
        """Limpa cache de embeddings"""
        pass

    @abstractmethod
    def get_embedding_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas sobre embeddings armazenados.
        
        Returns:
            Dicionário com estatísticas
        """
        pass
