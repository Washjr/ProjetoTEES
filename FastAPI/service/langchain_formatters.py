from typing import List, Dict
from langchain_openai import OpenAIEmbeddings
import hashlib
from .langchain_config import LangchainConfig


class EmbeddingCache:
    """Gerencia cache de embeddings para otimização de performance"""
    
    def __init__(self):
        self._cache: Dict[str, List[float]] = {}
    
    def _get_text_hash(self, text: str) -> str:
        """Gera hash MD5 do texto para usar como chave do cache"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def get_or_create_embedding(self, text: str, embedder: OpenAIEmbeddings) -> List[float]:
        """Obtém embedding do cache ou gera novo se não existir"""
        text_hash = self._get_text_hash(text)
        
        if text_hash in self._cache:
            return self._cache[text_hash]
        
        embedding = embedder.embed_query(text)
        self._cache[text_hash] = embedding
        return embedding


class DocumentFormatter:
    """Responsável por formatar documentos para diferentes contextos"""
    
    def __init__(self, config: LangchainConfig):
        self.config = config
    
    def format_for_display(self, doc: Dict, doc_type: str) -> str:
        """Formata documento para exibição baseado no tipo"""
        if doc_type == "pesquisador":
            return self._format_pesquisador(doc)
        elif doc_type == "artigo":
            return self._format_artigo(doc)
        else:
            return str(doc)
    
    def format_for_tags(self, doc: Dict, doc_type: str) -> str:
        """Formata documento para geração de tags"""
        if doc_type == "artigo":
            titulo = self._truncate_text(doc.get('title', 'Sem título'), self.config.MAX_TITULO_PRODUCAO_CHARS)
            journal = self._truncate_text(doc.get('journal', ''), self.config.MAX_JOURNAL_TAGS_CHARS)
            
            texto = f"• {titulo}"
            if journal:
                texto += f" ({journal})"
            return texto
        
        return self.format_for_display(doc, doc_type)
    
    def format_producoes_for_profile(self, producoes: List[Dict]) -> str:
        """Formata produções para perfil de pesquisador"""
        if not producoes:
            return "Nenhuma produção encontrada."
        
        producoes_texto = []
        for i, producao in enumerate(producoes[:self.config.MAX_PRODUCOES_FOR_PROFILE], 1):
            titulo = self._truncate_text(producao.get('title', 'Sem título'), self.config.MAX_TITULO_PRODUCAO_CHARS)
            ano = producao.get('year', 'N/A')
            journal = self._truncate_text(producao.get('journal', ''), self.config.MAX_JOURNAL_CHARS)
            
            texto = f"{i}. {titulo} ({ano})"
            if journal:
                texto += f" - {journal}"
            
            producoes_texto.append(texto)
        
        return "\n".join(producoes_texto)
    
    def _format_pesquisador(self, doc: Dict) -> str:
        """Formata dados de pesquisador"""
        nome = doc.get('nome', '')
        titulo = doc.get('titulo', '')
        resumo = doc.get('resumo', '')
        return f"{nome} {titulo} {resumo}"
    
    def _format_artigo(self, doc: Dict) -> str:
        """Formata dados de artigo"""
        title = doc.get('title', '')
        abstract = doc.get('abstract', '')
        return f"{title} {abstract}"
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Trunca texto respeitando limite de caracteres"""
        if not text:
            return ""
        return text[:max_length] if len(text) > max_length else text
