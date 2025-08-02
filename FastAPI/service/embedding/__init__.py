from .embedding_service import EmbeddingService
from .interface import IEmbeddingService

# Evitar importação circular - EmbeddingResult será importado diretamente quando necessário
__all__ = [
    "EmbeddingService",
    "IEmbeddingService"
]
