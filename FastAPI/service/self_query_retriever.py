import json
import os
import pickle
import hashlib
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dao.artigo_dao import ArtigoDAO

from langchain.chains.query_constructor.schema import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_community.query_constructors.chroma import ChromaTranslator

logger = logging.getLogger(__name__)


class SelfQueryRetrieverService:
    """
    Serviço para realizar busca usando SelfQueryRetriever baseado no LangChain.
    Implementa cache para embeddings para otimizar performance.
    """
    
    def __init__(self, cache_dir: str = "./embeddings_cache"):
        """
        Inicializa o serviço de Self Query Retriever.
        
        Args:
            cache_dir: Diretório onde os embeddings serão armazenados em cache
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.artigo_dao = ArtigoDAO()
        self.metadata_config = self._load_metadata_config()

        self.api_key = os.getenv("OPENAI_API_KEY_IKEDA")
        
        # Configurar LLM
        self.llm = ChatOpenAI(
            temperature=0,
            openai_api_key=self.api_key,
            model="gpt-3.5-turbo"
        )
        
        # Configurar embeddings
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=self.api_key,
        )
        
        # Criar AttributeInfo objects baseados na configuração
        self.attribute_infos = self._build_attribute_infos()
        
        # Descrição do conteúdo dos documentos
        self.document_content_description = self.metadata_config.get(
            "document_content_description", 
            "Artigos científicos com título, resumo e metadados de publicação acadêmica"
        )
        
        # Inicializar o retriever
        self.retriever = None
        self._vectorstore = None
    
    def _load_metadata_config(self) -> Dict[str, Any]:
        """Carrega configuração de metadados do arquivo JSON."""
        try:
            config_path = Path("config/metadata_config.json")
            if not config_path.exists():
                # Tentar caminho relativo ao arquivo atual
                config_path = Path(__file__).parent.parent / "config" / "metadata_config.json"
            
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar metadata_config.json: {e}")
            return {
                "metadata_fields": [],
                "document_content_description": "Artigos científicos com título, resumo e metadados de publicação acadêmica"
            }
    
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
    
    def _get_cache_key(self, documents: List[Document]) -> str:
        """Gera uma chave de cache baseada no conteúdo dos documentos."""
        # Criar hash baseado no conteúdo e metadados dos documentos
        content_hash = hashlib.md5()
        for doc in documents:
            content_hash.update(doc.page_content.encode('utf-8'))
            content_hash.update(str(doc.metadata).encode('utf-8'))
        
        return content_hash.hexdigest()
    
    def _save_vectorstore_cache(self, vectorstore: Chroma, cache_key: str):
        """Salva o vectorstore em cache."""
        try:
            cache_file = self.cache_dir / f"vectorstore_{cache_key}.pkl"
            
            # Salvar usando pickle (para metadados e configuração)
            cache_data = {
                'vectorstore_path': f"./chroma_db_{cache_key}",
                'attribute_infos': [attr.__dict__ for attr in self.attribute_infos],
                'document_content_description': self.document_content_description
            }
            
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
                
            logger.info(f"Vectorstore salvo em cache: {cache_file}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar cache do vectorstore: {e}")
    
    def _load_vectorstore_cache(self, cache_key: str) -> Optional[Chroma]:
        """Carrega o vectorstore do cache."""
        try:
            cache_file = self.cache_dir / f"vectorstore_{cache_key}.pkl"
            
            if not cache_file.exists():
                return None
            
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            vectorstore_path = cache_data['vectorstore_path']
            
            # Verificar se o diretório do Chroma existe
            if not os.path.exists(vectorstore_path):
                logger.warning(f"Diretório do vectorstore não encontrado: {vectorstore_path}")
                return None
            
            # Carregar vectorstore do Chroma
            vectorstore = Chroma(
                persist_directory=vectorstore_path,
                embedding_function=self.embeddings
            )
            
            logger.info(f"Vectorstore carregado do cache: {cache_file}")
            return vectorstore
            
        except Exception as e:
            logger.error(f"Erro ao carregar cache do vectorstore: {e}")
            return None
    
    def _qualis_to_numeric(self, qualis: str) -> int:
        """Converte classificação Qualis para valor numérico para comparações."""
        qualis_map = {
            'A1': 7,
            'A2': 6,
            'A3': 5,
            'A4': 4,
            'B1': 3,
            'B2': 2,
            'B3': 1,
            'B4': 1,
            'C': 0,
            '': 0
        }
        return qualis_map.get(qualis.upper(), 0)
    
    def _create_documents_from_artigos(self, limit: Optional[int] = None) -> List[Document]:
        """Cria documentos a partir dos artigos do banco de dados."""
        try:
            artigos = self.artigo_dao.listar_artigos()
            
            if limit:
                artigos = artigos[:limit]
            
            documents = []
            
            for artigo in artigos:
                # Criar conteúdo do documento
                title = artigo.get('title', '') or ''
                abstract = artigo.get('abstract', '') or ''
                content = f"Título: {title}\nResumo: {abstract}"
                
                # Criar metadados compatíveis com AttributeInfo
                qualis_str = artigo.get('qualis', '') or ''
                metadata = {
                    "year": artigo.get('year'),
                    "qualis": qualis_str,
                    "qualis_score": self._qualis_to_numeric(qualis_str),
                    "journal": artigo.get('journal', ''),
                    "author_name": artigo.get('authors', [{}])[0].get('name', '') if artigo.get('authors') else '',
                    "doi": artigo.get('doi', '')
                }
                
                # Filtrar valores None dos metadados
                metadata = {k: v for k, v in metadata.items() if v is not None}
                
                doc = Document(page_content=content, metadata=metadata)
                documents.append(doc)
            
            logger.info(f"Criados {len(documents)} documentos a partir dos artigos")
            return documents
            
        except Exception as e:
            logger.error(f"Erro ao criar documentos: {e}")
            return []
    
    def _setup_vectorstore(self, documents: List[Document], cache_key: str) -> Chroma:
        """Configura o vectorstore com cache."""
        # Tentar carregar do cache primeiro
        cached_vectorstore = self._load_vectorstore_cache(cache_key)
        if cached_vectorstore is not None:
            return cached_vectorstore
        
        # Criar novo vectorstore
        logger.info("Criando novo vectorstore...")
        vectorstore_path = f"./chroma_db_{cache_key}"
        
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=vectorstore_path
        )
        
        # Salvar em cache
        self._save_vectorstore_cache(vectorstore, cache_key)
        
        return vectorstore
    
    def initialize_retriever(self, limit_documents: Optional[int] = None) -> SelfQueryRetriever:
        """
        Inicializa o SelfQueryRetriever com cache para embeddings.
        
        Args:
            limit_documents: Limite de documentos para processar (útil para testes)
            
        Returns:
            SelfQueryRetriever configurado
        """
        try:
            # Criar documentos
            documents = self._create_documents_from_artigos()
            
            if not documents:
                raise ValueError("Nenhum documento foi criado")
            
            # Gerar chave de cache
            cache_key = self._get_cache_key(documents)
            
            # Configurar vectorstore com cache
            self._vectorstore = self._setup_vectorstore(documents, cache_key)
            
            # Criar SelfQueryRetriever
            self.retriever = SelfQueryRetriever.from_llm(
                llm=self.llm,
                vectorstore=self._vectorstore,
                document_contents=self.document_content_description,
                metadata_field_info=self.attribute_infos,
                structured_query_translator=ChromaTranslator(),
                verbose=True
            )
            
            logger.info("SelfQueryRetriever inicializado com sucesso")
            return self.retriever
            
        except Exception as e:
            logger.error(f"Erro ao inicializar retriever: {e}")
            raise
    
    def query(self, query_text: str, k: int = 5) -> List[Document]:
        """
        Executa uma consulta usando o SelfQueryRetriever.
        
        Args:
            query_text: Consulta em linguagem natural
            k: Número de documentos a retornar
            
        Returns:
            Lista de documentos relevantes
        """
        if self.retriever is None:
            self.initialize_retriever()
        
        try:
            # Configurar parâmetros de busca
            self.retriever.search_kwargs = {"k": k}
            
            # Executar consulta
            results = self.retriever.invoke(query_text)
            
            logger.info(f"Consulta executada: '{query_text}' - {len(results)} resultados")
            with open("query_results.txt", "a", encoding="utf-8") as f:
                f.write(f"Consulta: {query_text}\n")
                for i, doc in enumerate(results, 1):
                    f.write(f"{i}. {doc.page_content[:100]}...\n")
                    f.write(f"   Metadados: {doc.metadata}\n")
                f.write("\n")
            return results
            
        except Exception as e:
            logger.error(f"Erro ao executar consulta: {e}")
            return []
    
    def get_retriever(self) -> Optional[SelfQueryRetriever]:
        """Retorna o retriever atual."""
        return self.retriever
    
    def clear_cache(self):
        """Remove todos os arquivos de cache."""
        try:
            import shutil
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(exist_ok=True)
                logger.info("Cache limpo com sucesso")
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")


# Exemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Criar instância do serviço
    service = SelfQueryRetrieverService()
    
    # Inicializar com poucos documentos para teste
    service.initialize_retriever(limit_documents=10)
    
    # Exemplos de consultas
    queries = [
        "Artigos sobre inteligência artificial publicados após 2020",
        "Pesquisas do autor João Silva",
        "Trabalhos publicados em periódicos Qualis A1",
        "Artigos sobre machine learning com classificação B1 ou superior"
    ]
    
    for query in queries:
        print(f"\nConsulta: {query}")
        results = service.query(query, k=3)
        
        for i, doc in enumerate(results, 1):
            print(f"\n{i}. {doc.page_content[:100]}...")
            print(f"   Metadados: {doc.metadata}")
