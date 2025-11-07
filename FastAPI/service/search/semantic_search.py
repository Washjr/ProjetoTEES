import logging
from typing import List, Optional

from dao.artigo_dao import ArtigoDAO
from dao.pesquisador_dao import PesquisadorDAO
from service.embedding import EmbeddingService
from model.dto.artigo_busca_dto import ArtigoBuscaDTO

SIMILARITY_THRESHOLD = 0.4

logger = logging.getLogger(__name__)

class SemanticSearchService:
    """
    Facade para busca semântica que coordena entre EmbeddingService e ArtigoDAO.
    EmbeddingService: responsável por gerar embeddings
    ArtigoDAO: responsável por operações de banco de dados e busca por similaridade
    """
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        # Não mantém instâncias de DAOs para evitar esgotamento do pool de conexões

    def index_all(self):
        """
        Indexa todos os documentos disponíveis.
        Com PGVector, os documentos são automaticamente indexados quando armazenados no banco.
        """
        artigo_dao = ArtigoDAO()
        pesquisador_dao = PesquisadorDAO()
        
        artigos = artigo_dao.listar_artigos()
        pesquisadores = pesquisador_dao.listar_pesquisadores()
        
        logger.info(f"{len(artigos)} artigos e {len(pesquisadores)} pesquisadores disponíveis para busca semântica.")

    def semantic_search(self, query: str, k: int, filter: Optional[str] = None) -> List[ArtigoBuscaDTO]:
        """
        Realiza busca semântica de artigos.
        
        Args:
            query: Texto da consulta
            k: Número máximo de resultados
            filter: Filtro SQL adicional opcional
            
        Returns:
            Lista de artigos similares
        """
        try:
            query_embedding = self.embedding_service.generate_embedding(query)
            
            artigo_dao = ArtigoDAO()
            results = artigo_dao.buscar_artigos_similares(
                query_embedding=query_embedding,
                limit=k,
                threshold=SIMILARITY_THRESHOLD,
                filtro=filter
            )

            logger.info(f"Busca semântica retornou {len(results)} resultados para consulta: '{query}' com filtro: '{filter}'")
            return results
            
        except Exception as e:
            logger.error(f"Erro na busca semântica: {e}")
            return []

    def update_embeddings(self) -> dict:
        """
        Atualiza embeddings de todos os artigos.
        
        Returns:
            Estatísticas do processo de atualização
        """
        return self.embedding_service.update_all_article_embeddings()

    def get_embedding_stats(self) -> dict:
        """
        Obtém estatísticas sobre embeddings armazenados.
        
        Returns:
            Dicionário com estatísticas de embeddings
        """
        artigo_dao = ArtigoDAO()
        return artigo_dao.obter_estatisticas_embeddings()
