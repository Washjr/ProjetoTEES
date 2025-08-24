import logging
from typing import List, Dict, Optional

from dao.artigo_dao import ArtigoDAO
from dao.pesquisador_dao import PesquisadorDAO
from service.embedding import EmbeddingService
from model.dto.artigo_busca_dto import ArtigoBuscaDTO
from model.mapper.artigo_dto_mapper import ArtigoDTOMapper

SIMILARITY_THRESHOLD = 0.4

logger = logging.getLogger(__name__)

class SemanticSearchService:
    def __init__(self):
        self.embedding_service = EmbeddingService()

    def index_all(self):
        # pgvector automatically indexes when documents are stored in database
        # This ensures all existing documents are available for search
        artigos = ArtigoDAO().listar_artigos()
        pesquisadores = PesquisadorDAO().listar_pesquisadores()
        
        logger.info(f"{len(artigos)} artigos e {len(pesquisadores)} pesquisadores disponíveis para busca semântica.")

    def semantic_search(self, query: str, k: int, filter: Optional[str] = None) -> List[ArtigoBuscaDTO]:
        results = self.embedding_service.search_similar_articles(
            query_text=query, 
            limit=k,
            filter=filter
        )
        
        artigos_dto = []
        for result in results:
            artigo_dto = ArtigoDTOMapper.to_artigo_busca_dto_from_embedding_result(result)
            artigo_dto.score = result.similarity_score
            artigos_dto.append(artigo_dto)
        
        return artigos_dto
