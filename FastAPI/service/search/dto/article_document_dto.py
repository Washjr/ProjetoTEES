"""
DTO (Data Transfer Object) para conversão entre artigos e documentos LangChain.
Centraliza toda a lógica de transformação de dados entre diferentes formatos.
"""

import logging
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class ArticleDocumentDTO:
    """
    DTO responsável por conversões entre artigos (dados do banco) e documentos LangChain.
    Centraliza toda a lógica de transformação e formatação de dados.
    """
    
    # Mapeamento de classificação Qualis para valores numéricos
    QUALIS_NUMERIC_MAP = {
        'A1': 9,
        'A2': 8,
        'A3': 7,
        'A4': 6,
        'B1': 5,
        'B2': 4,
        'B3': 3,
        'B4': 2,
        'C': 1,
        '': 0
    }
    
    @classmethod
    def artigo_to_document(cls, artigo: Dict[str, Any]) -> Document:
        """
        Converte um artigo (dados do banco) para um documento LangChain.
        
        Args:
            artigo: Dicionário com dados do artigo do banco
            
        Returns:
            Document: Documento LangChain formatado
        """
        try:
            # Construir conteúdo do documento
            title = artigo.get('title', '') or ''
            abstract = artigo.get('abstract', '') or ''
            content = f"Título: {title}\nResumo: {abstract}"
            
            # Construir metadados
            metadata = cls._build_metadata_from_artigo(artigo)
            
            return Document(page_content=content, metadata=metadata)
            
        except Exception as e:
            logger.error(f"Erro ao converter artigo para documento: {e}")
            raise ValueError(f"Erro na conversão artigo->documento: {str(e)}")
    
    @classmethod
    def document_to_artigo(cls, document: Document) -> Dict[str, Any]:
        """
        Extrai dados de artigo a partir de um documento LangChain.
        
        Args:
            document: Documento LangChain
            
        Returns:
            Dict: Dados do artigo extraídos
        """
        try:
            # Extrair título e resumo do conteúdo
            content_lines = document.page_content.split('\n')
            title = content_lines[0].replace('Título: ', '') if content_lines else ''
            abstract = content_lines[1].replace('Resumo: ', '') if len(content_lines) > 1 else ''
            
            # Extrair dados dos metadados
            artigo_data = {
                "title": title,
                "abstract": abstract,
                "year": document.metadata.get('year'),
                "qualis": document.metadata.get('qualis', ''),
                "qualis_score": document.metadata.get('qualis_score'),
                "journal": document.metadata.get('journal', ''),
                "doi": document.metadata.get('doi', ''),
                "author_name": document.metadata.get('author_name', ''),
                "id": document.metadata.get('artigo_id'),
                "id_artigo": document.metadata.get('artigo_id')
            }
            
            # Filtrar valores None
            return {k: v for k, v in artigo_data.items() if v is not None}
            
        except Exception as e:
            logger.error(f"Erro ao converter documento para artigo: {e}")
            raise ValueError(f"Erro na conversão documento->artigo: {str(e)}")
    
    @classmethod
    def artigos_to_documents(cls, artigos: List[Dict[str, Any]]) -> List[Document]:
        """
        Converte uma lista de artigos para documentos LangChain.
        
        Args:
            artigos: Lista de artigos
            
        Returns:
            List[Document]: Lista de documentos LangChain
        """
        documents = []
        
        for artigo in artigos:
            try:
                document = cls.artigo_to_document(artigo)
                documents.append(document)
            except Exception as e:
                logger.warning(f"Erro ao converter artigo {artigo.get('id', 'unknown')}: {e}")
                continue
        
        logger.info(f"Convertidos {len(documents)} artigos para documentos")
        return documents
    
    @classmethod
    def documents_to_artigos(cls, documents: List[Document]) -> List[Dict[str, Any]]:
        """
        Converte uma lista de documentos LangChain para artigos.
        
        Args:
            documents: Lista de documentos LangChain
            
        Returns:
            List[Dict]: Lista de artigos
        """
        artigos = []
        
        for document in documents:
            try:
                artigo = cls.document_to_artigo(document)
                artigos.append(artigo)
            except Exception as e:
                logger.warning(f"Erro ao converter documento: {e}")
                continue
        
        logger.info(f"Convertidos {len(artigos)} documentos para artigos")
        return artigos
    
    @classmethod
    def documents_to_search_results(cls, documents: List[Document], scores: Optional[List[float]] = None) -> List[Dict[str, Any]]:
        """
        Converte documentos LangChain para formato de resultados de busca.
        
        Args:
            documents: Lista de documentos LangChain
            scores: Lista opcional de scores para cada documento
            
        Returns:
            List[Dict]: Lista de resultados formatados para busca
        """
        results = []
        
        for i, document in enumerate(documents):
            try:
                artigo = cls.document_to_artigo(document)
                
                # Priorizar score fornecido, depois combined_score dos metadados, depois padrão
                if scores and i < len(scores):
                    score = scores[i]
                elif "combined_score" in document.metadata:
                    score = document.metadata["combined_score"]
                else:
                    score = 1.0
                
                result = {
                    "artigo": artigo,
                    "score": score,
                    "metadata": document.metadata
                }
                
                # Preservar scores detalhados se existirem
                if "scores_detalhados" in document.metadata or any(k.startswith("score_") for k in document.metadata.keys()):
                    result["scores_detalhados"] = {
                        "termos": document.metadata.get("score_termos", 0.0),
                        "semantico": document.metadata.get("score_semantico", 0.0),
                        "final": document.metadata.get("score_final", score)
                    }
                
                results.append(result)
                
            except Exception as e:
                logger.warning(f"Erro ao converter documento {i} para resultado: {e}")
                continue
        
        return results
    
    @classmethod
    def combined_results_to_documents(cls, resultados_combinados: List[Dict[str, Any]]) -> List[Document]:
        """
        Converte resultados combinados (híbridos) de volta para documentos.
        Útil para aplicar filtros posteriormente.
        
        Args:
            resultados_combinados: Lista de resultados da busca híbrida
            
        Returns:
            List[Document]: Documentos com scores preservados nos metadados
        """
        documents = []
        
        for resultado in resultados_combinados:
            try:
                artigo = resultado["artigo"]

                document = cls.artigo_to_document(artigo)
                
                # Preservar scores nos metadados do documento
                document.metadata["combined_score"] = resultado.get("score", 0.0)
                if "scores_detalhados" in resultado:
                    document.metadata["score_termos"] = resultado["scores_detalhados"].get("termos", 0.0)
                    document.metadata["score_semantico"] = resultado["scores_detalhados"].get("semantico", 0.0)
                    document.metadata["score_final"] = resultado["scores_detalhados"].get("final", 0.0)
                
                documents.append(document)
                
            except Exception as e:
                logger.warning(f"Erro ao converter resultado combinado: {e}")
                continue
        
        return documents
    
    @classmethod
    def _build_metadata_from_artigo(cls, artigo: Dict[str, Any]) -> Dict[str, Any]:
        """
        Constrói metadados para documento LangChain a partir dos dados do artigo.
        
        Args:
            artigo: Dados do artigo
            
        Returns:
            Dict: Metadados formatados
        """
        # Extrair nome do primeiro autor
        author_name = ''
        if artigo.get('authors'):
            if isinstance(artigo['authors'], list) and len(artigo['authors']) > 0:
                first_author = artigo['authors'][0]
                if isinstance(first_author, dict):
                    author_name = first_author.get('name', '')
                else:
                    author_name = str(first_author)
        
        # Processar classificação Qualis
        qualis_str = artigo.get('qualis', '') or ''
        
        metadata = {
            "year": artigo.get('year'),
            "qualis": qualis_str,
            "qualis_score": cls._qualis_to_numeric(qualis_str),
            "journal": artigo.get('journal', ''),
            "author_name": author_name,
            "doi": artigo.get('doi', ''),
            "artigo_id": artigo.get('id') or artigo.get('id_artigo')
        }
        
        # Filtrar valores None dos metadados
        return {k: v for k, v in metadata.items() if v is not None}
    
    @classmethod
    def _qualis_to_numeric(cls, qualis: str) -> int:
        return cls.QUALIS_NUMERIC_MAP.get(qualis.upper(), 0)
    
    @classmethod
    def format_search_response(
        cls, 
        query: str, 
        documents: List[Document], 
        method: str = "self_query",
        additional_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Formata resposta completa de busca no padrão esperado pelo controller.
        
        Args:
            query: Consulta original
            documents: Documentos encontrados
            method: Método de busca utilizado
            additional_info: Informações adicionais opcionais
            
        Returns:
            Dict: Resposta formatada para o controller
        """
        # Converter documentos para resultados
        results = cls.documents_to_search_results(documents)
        
        response = {
            "query": query,
            "method": method,
            "total_found": len(results),
            "results": results
        }
        
        # Adicionar informações extras se fornecidas
        if additional_info:
            response.update(additional_info)
        
        return response
    
    @classmethod
    def validate_artigo_data(cls, artigo: Dict[str, Any]) -> bool:
        """
        Valida se os dados do artigo são suficientes para conversão.
        
        Args:
            artigo: Dados do artigo a validar
            
        Returns:
            bool: True se válido, False caso contrário
        """
        # Verificar campos obrigatórios mínimos
        required_fields = ['title']
        
        for field in required_fields:
            if not artigo.get(field):
                logger.warning(f"Artigo inválido: campo '{field}' ausente ou vazio")
                return False
        
        return True
    
    @classmethod
    def extract_unique_identifiers(cls, artigos: List[Dict[str, Any]]) -> List[str]:
        """
        Extrai identificadores únicos de uma lista de artigos.
        Útil para deduplicação.
        
        Args:
            artigos: Lista de artigos
            
        Returns:
            List[str]: Lista de identificadores únicos
        """
        identifiers = []
        
        for artigo in artigos:
            # Tentar diferentes tipos de ID
            identifier = (
                artigo.get('id') or 
                artigo.get('id_artigo') or 
                artigo.get('doi') or
                f"{artigo.get('title', '')}_{artigo.get('author_name', '')}"
            )
            
            if identifier:
                identifiers.append(str(identifier))
        
        return identifiers
