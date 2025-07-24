import json
import logging
from typing import List, Dict, Any

from dao.artigo_dao import ArtigoDAO
from service.semantic_search import SemanticSearchService
from langchain.chains.query_constructor.schema import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_openai import OpenAI
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from config import configuracoes

logger = logging.getLogger(__name__)


class SelfQueryService:
    """
    Serviço para análise e processamento de consultas com self-querying usando LangChain.
    Utiliza SelfQueryRetriever para processar consultas em linguagem natural.
    """
    
    def __init__(self):
        self.artigo_dao = ArtigoDAO()
        self.semantic_service = SemanticSearchService()
        self.metadata_config = self._load_metadata_config()
        
        # Configurar LLM para o SelfQueryRetriever
        self.llm = OpenAI(
            temperature=0,
            api_key=configuracoes.OPENAI_API_KEY,
            model_name="gpt-3.5-turbo-instruct"
        )
        
        # Criar AttributeInfo objects baseados na configuração
        self.attribute_infos = self._build_attribute_infos()
        
        # Configurar o SelfQueryRetriever
        self.self_query_retriever = self._setup_self_query_retriever()
    
    def _setup_self_query_retriever(self) -> SelfQueryRetriever:
        """Configura e retorna um SelfQueryRetriever usando Chroma."""
        # Criar embeddings
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=configuracoes.OPENAI_API_KEY
        )
        
        # Criar documentos a partir dos artigos
        artigos = self.artigo_dao.listar_artigos()[:100]  # Limitar para teste
        documents = []
        
        for artigo in artigos:
            # Criar conteúdo do documento
            content = f"Título: {artigo['title']}\nResumo: {artigo['abstract'] or ''}"
            
            # Criar metadados compatíveis com AttributeInfo
            metadata = {
                "id": artigo['id'],
                "year": artigo['year'],
                "qualis": artigo['qualis'] or "",
                "journal": artigo['journal'] or "",
                "author_name": artigo['authors'][0]['name'] if artigo['authors'] else "",
                "doi": artigo['doi'] or ""
            }
            
            doc = Document(page_content=content, metadata=metadata)
            documents.append(doc)
        
        # Criar Chroma vectorstore
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory="./chroma_db"
        )
        
        # Descrição do conteúdo dos documentos
        document_content_description = self.metadata_config.get(
            "document_content_description", 
            "Artigos científicos com título, resumo e metadados de publicação acadêmica"
        )
        
        # Criar o SelfQueryRetriever
        retriever = SelfQueryRetriever.from_llm(
            llm=self.llm,
            vectorstore=vectorstore,
            document_contents=document_content_description,
            metadata_field_info=self.attribute_infos,
            verbose=True,
            search_kwargs={"k": 10}
        )
        
        return retriever
    
    def _load_metadata_config(self) -> Dict:
        """Carrega configuração de metadados do arquivo JSON."""
        try:
            with open('config/metadata_config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar metadata_config.json: {e}")
            return {"metadata_fields": [], "basic_patterns": {}, "document_content_description": ""}
    
    def _build_attribute_infos(self) -> List[AttributeInfo]:
        """Constrói lista de AttributeInfo objects baseados na configuração."""
        attribute_infos = []
        
        for field_config in self.metadata_config.get("metadata_fields", []):
            name = field_config["name"]
            description = field_config["description"]
            field_type = field_config["type"]
            
            # Mapear tipos para os tipos do AttributeInfo
            if field_type == "integer":
                attr_type = "integer"
            elif field_type == "float":
                attr_type = "float"
            else:
                attr_type = "string"
            
            # Criar AttributeInfo
            attr_info = AttributeInfo(
                name=name,
                description=description,
                type=attr_type
            )
            
            attribute_infos.append(attr_info)
        
        return attribute_infos
    
    def test_self_query_retriever(self, query: str) -> Dict[str, Any]:
        """
        Testa especificamente o SelfQueryRetriever com uma consulta.
        
        Args:
            query: Consulta em linguagem natural
            
        Returns:
            Dict com informações detalhadas sobre o processamento
        """
        try:
            # Testar o retriever diretamente
            docs = self.self_query_retriever.get_relevant_documents(query)
            
            # Informações sobre os documentos retornados
            doc_info = []
            for i, doc in enumerate(docs):
                doc_info.append({
                    "index": i,
                    "content_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "metadata": doc.metadata
                })
            
            return {
                "query": query,
                "success": True,
                "documents_found": len(docs),
                "documents": doc_info,
                "attribute_infos": [
                    {
                        "name": attr.name,
                        "description": attr.description,
                        "type": attr.type
                    }
                    for attr in self.attribute_infos
                ]
            }
            
        except Exception as e:
            return {
                "query": query,
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }

    def get_available_filters(self) -> List[Dict[str, Any]]:
        """Retorna informações sobre os filtros disponíveis baseados nos AttributeInfo."""
        available_filters = []
        
        for attr_info in self.attribute_infos:
            # Encontrar a configuração do campo
            field_config = None
            for config in self.metadata_config.get("metadata_fields", []):
                if config["name"] == attr_info.name:
                    field_config = config
                    break
            
            filter_info = {
                "name": attr_info.name,
                "description": attr_info.description,
                "type": attr_info.type
            }
            
            # Adicionar informações específicas do campo se disponível
            if field_config:
                if field_config.get("hierarchy"):
                    filter_info["possible_values"] = field_config["hierarchy"]
            
            available_filters.append(filter_info)
        
        return available_filters
    
    def process_query(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Processa uma consulta usando SelfQueryRetriever do LangChain.
        
        Args:
            query: Consulta do usuário em linguagem natural
            max_results: Número máximo de resultados
            
        Returns:
            Dict com artigos encontrados e informações da consulta
        """
        try:
            # Usar o SelfQueryRetriever para processar a consulta
            docs = self.self_query_retriever.get_relevant_documents(query)
            
            # Limitar resultados
            docs = docs[:max_results]
            
            # Converter documentos para o formato esperado
            results = []
            for doc in docs:
                # Extrair metadados do documento
                metadata = doc.metadata
                
                # Criar um objeto artigo simulado com os metadados
                content_lines = doc.page_content.split('\n')
                title = content_lines[0].replace('Título: ', '') if content_lines else ''
                abstract = content_lines[1].replace('Resumo: ', '') if len(content_lines) > 1 else ''
                
                article_data = {
                    "id": metadata.get('id', ''),
                    "title": title,
                    "abstract": abstract,
                    "year": metadata.get('year', ''),
                    "qualis": metadata.get('qualis', ''),
                    "journal": metadata.get('journal', ''),
                    "doi": metadata.get('doi', ''),
                    "authors": [{"name": metadata.get('author_name', '')}] if metadata.get('author_name') else []
                }
                
                results.append({
                    "article": article_data,
                    "relevance_score": 1.0,  # SelfQueryRetriever não retorna score
                    "content": doc.page_content,
                    "metadata": metadata
                })
            
            return {
                "query": query,
                "total_found": len(results),
                "results": results,
                "method": "self_query_retriever"
            }
            
        except Exception as e:
            logger.error(f"Erro no SelfQueryRetriever: {e}")
            raise RuntimeError(f"Erro ao processar consulta com SelfQueryRetriever: {e}")
