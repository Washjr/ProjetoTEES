import logging
from typing import List, Dict, Tuple

from dao.artigo_dao import ArtigoDAO
from dao.pesquisador_dao import PesquisadorDAO
from service.embedding import EmbeddingService
from service.embedding.embedding_service import EmbeddingResult

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

    def semantic_search(self, query: str, k: int = 10, tipo: str = 'artigo') -> List[Tuple]:
        if tipo == 'artigo':
            return self._search_articles_with_pgvector(query, k)
        else:
            return self._search_researchers_with_pgvector(query, k)

    def _search_articles_with_pgvector(self, query: str, k: int) -> List[Tuple]:
        results = self.embedding_service.search_similar_articles(
            query_text=query, 
            limit=k, 
            threshold=SIMILARITY_THRESHOLD
        )
        
        return [(self._convert_embedding_result_to_dict(result), result.similarity_score) 
                for result in results]

    def _search_researchers_with_pgvector(self, query: str, k: int) -> List[Tuple]:
        # Implement researcher search using pgvector if available in embedding service
        # For now, return empty list as fallback
        logger.warning("Researcher search with pgvector not implemented yet")
        return []

    def _convert_embedding_result_to_dict(self, result: EmbeddingResult) -> Dict:
        return {
            'id': result.id,
            'title': result.metadata.get('title'),
            'abstract': result.metadata.get('abstract'),
            'doi': result.metadata.get('doi'),
            'year': result.metadata.get('year'),
            'journal': result.metadata.get('journal'),
            'qualis': result.metadata.get('qualis'),
            'author_name': result.metadata.get('author_name')
        }