from typing import List, Dict
import logging
import os

import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

from config import configuracoes
from dao.artigo_dao import ArtigoDAO
from dao.pesquisador_dao import PesquisadorDAO


logger = logging.getLogger(__name__)

# Diretório comum para todos os índices semânticos
EMBEDDING_INDEX_DIR = os.getenv("SEMANTIC_INDEX_DIR", "semantic_indexes")
os.makedirs(EMBEDDING_INDEX_DIR, exist_ok=True)


class SemanticSearchService:
    def __init__(self):        
        self.embedder = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=configuracoes.OPENAI_API_KEY
        )

        # Carrega ou cria dois índices distintos em disco: pesquisadores e artigos
        self.indices = {
            "artigo": self._load_or_create_index("faiss_artigo_index"),
            "pesquisador": self._load_or_create_index("faiss_pesquisador_index"),
        }


    def _get_path(self, name: str) -> str:
        return os.path.join(EMBEDDING_INDEX_DIR, name)


    def _load_or_create_index(self, name: str) -> FAISS:
        path = self._get_path(name)

        try:
            return FAISS.load_local(
                path,
                embeddings=self.embedder,
                allow_dangerous_deserialization=True
            )
        except Exception:
            faiss_index = faiss.IndexFlatL2(len(self.embedder.embed_query("hello world")))

            return FAISS(
                embedding_function=self.embedder,
                index=faiss_index,
                docstore=InMemoryDocstore(),
                index_to_docstore_id={}
            )


    def index_documents(self, docs: List[Dict], tipo: str):
        index = self.indices[tipo]
        name = f"faiss_{tipo}_index"
        
        existing_docs = {d.metadata["doc"]["id"] for d in index.docstore._dict.values()}

        faiss_docs = []
        for doc in docs:
            if doc['id'] not in existing_docs:
                text = (
                    f"{doc['name']}: {doc.get('title','')}"
                    if tipo == "pesquisador"
                    else f"{doc['title']} - {doc.get('abstract','')}"
                )
                faiss_docs.append(Document(page_content=text, metadata={"doc": doc}))

        if faiss_docs:
            index.add_documents(faiss_docs)
            index.save_local(self._get_path(name))


    def index_all(self):
        # Recria e indexa todos os artigos e pesquisadores
        artigos = ArtigoDAO().listar_artigos()
        pesquisadores = PesquisadorDAO().listar_pesquisadores()

        self.index_documents(artigos, tipo="artigo")        
        self.index_documents(pesquisadores, tipo="pesquisador")

        logger.info(f"{len(artigos)} artigos e {len(pesquisadores)} pesquisadores indexados para busca semântica.")


    def semantic_search(self, query: str, k: int = 10, tipo: str = 'artigo'):
        index = self.indices.get(tipo)
        resultados  = index.similarity_search_with_score(query, k=k)

        # Define um limiar de corte
        SCORE_THRESHOLD = 0.0

        resultados_filtrados = []
        for doc, score in resultados:
            score = float(score)
            score_similaridade = 1 / (1 + score)

            if score_similaridade >= SCORE_THRESHOLD:
                resultados_filtrados.append((doc, score_similaridade))
                # resultados_filtrados.append((doc, round(score_similaridade, 4)))

        return [(doc.metadata['doc'], score) for doc, score in resultados_filtrados]