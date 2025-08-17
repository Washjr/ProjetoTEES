import logging
from math import log
from typing import List, Dict

from dao.artigo_dao import ArtigoDAO
from dao.pesquisador_dao import PesquisadorDAO
from service.embedding import EmbeddingService
from service.embedding.embedding_service import EmbeddingResult
from model.dto.artigo_busca_dto import ArtigoBuscaDTO
from model.mapper.artigo_dto_mapper import ArtigoDTOMapper

SIMILARITY_THRESHOLD = 0.4

logger = logging.getLogger(__name__)


class SemanticSearchService:
    def __init__(self):
        self.embedding_service = EmbeddingService()

    def index_documents(self, docs: List[Dict], tipo: str):
        # Documents are automatically indexed in pgvector when added to database
        # This method is kept for compatibility but doesn't need FAISS operations
        pass

    def index_all(self):
        # pgvector automatically indexes when documents are stored in database
        # This ensures all existing documents are available for search
        artigos = ArtigoDAO().listar_artigos()
        pesquisadores = PesquisadorDAO().listar_pesquisadores()
        
        logger.info(f"{len(artigos)} artigos e {len(pesquisadores)} pesquisadores disponíveis para busca semântica.")

    def semantic_search(self, query: str, k: int = 10, tipo: str = 'artigo') -> List[ArtigoBuscaDTO]:
        if tipo == 'artigo':
            return self._search_articles_with_pgvector(query, k)
        else:
            # Para pesquisadores, retorna lista vazia por enquanto
            logger.warning("Researcher search with pgvector not implemented yet")
            return []

    def _search_articles_with_pgvector(self, query: str, k: int) -> List[ArtigoBuscaDTO]:
        results = self.embedding_service.search_similar_articles(
            query_text=query, 
            limit=k, 
            threshold=SIMILARITY_THRESHOLD
        )
        
        artigos_dto = []
        for result in results:
            artigo_dto = ArtigoDTOMapper.to_artigo_busca_dto_from_embedding_result(result)
            artigo_dto.score = result.similarity_score
            artigos_dto.append(artigo_dto)
        
        return artigos_dto
