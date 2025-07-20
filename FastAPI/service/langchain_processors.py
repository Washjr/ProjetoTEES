from typing import List, Dict
import re
from .langchain_config import LangchainConfig


class ChunkProcessor:
    """Responsável por dividir textos em chunks semânticos"""
    
    def __init__(self, config: LangchainConfig):
        self.config = config
    
    def create_semantic_chunks(self, text: str, doc_id: str = "") -> List[Dict]:
        """Divide texto em chunks semânticos por sentenças"""
        if not text or len(text) < 50:
            return [{"text": text, "doc_id": doc_id, "chunk_id": 0}]
        
        sentences = self._split_into_sentences(text)
        return self._build_chunks(sentences, doc_id)
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Divide texto em sentenças"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _build_chunks(self, sentences: List[str], doc_id: str) -> List[Dict]:
        """Constrói chunks a partir das sentenças"""
        chunks = []
        current_chunk = ""
        chunk_id = 0
        
        for sentence in sentences:
            if self._should_create_new_chunk(current_chunk, sentence):
                if current_chunk:
                    chunks.append(self._create_chunk(current_chunk, doc_id, chunk_id))
                    chunk_id += 1
                
                current_chunk = self._start_new_chunk(current_chunk, sentence)
            else:
                current_chunk = self._add_to_chunk(current_chunk, sentence)
        
        # Adicionar último chunk
        if current_chunk.strip():
            chunks.append(self._create_chunk(current_chunk, doc_id, chunk_id))
        
        return chunks[:self.config.MAX_CHUNKS_PER_DOC]
    
    def _should_create_new_chunk(self, current_chunk: str, sentence: str) -> bool:
        """Verifica se deve criar um novo chunk"""
        return (len(current_chunk + sentence) > self.config.MAX_CHUNK_SIZE and 
                current_chunk)
    
    def _create_chunk(self, text: str, doc_id: str, chunk_id: int) -> Dict:
        """Cria um objeto chunk"""
        return {
            "text": text.strip(),
            "doc_id": doc_id,
            "chunk_id": chunk_id
        }
    
    def _start_new_chunk(self, current_chunk: str, sentence: str) -> str:
        """Inicia novo chunk com overlap se necessário"""
        if len(current_chunk) > self.config.CHUNK_OVERLAP:
            return current_chunk[-self.config.CHUNK_OVERLAP:] + " " + sentence
        return sentence
    
    def _add_to_chunk(self, current_chunk: str, sentence: str) -> str:
        """Adiciona sentença ao chunk atual"""
        return current_chunk + " " + sentence
