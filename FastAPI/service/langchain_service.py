from typing import List, Dict
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
import logging
from config import configuracoes

# Importar módulos refatorados
from .langchain_config import LangchainConfig, TemplateManager
from .langchain_formatters import EmbeddingCache, DocumentFormatter
from .langchain_processors import ChunkProcessor
from .langchain_filters import SimilarityFilter
from .langchain_generators import ContentGenerator

logger = logging.getLogger(__name__)


class LangchainService:
    """Serviço principal refatorado com responsabilidades bem definidas"""

    def __init__(self):
        self.config = LangchainConfig()
        self._validate_api_key()

        # Inicializar componentes
        self.template_manager = TemplateManager()
        self.embedding_cache = EmbeddingCache()
        self.formatter = DocumentFormatter(self.config)
        self.chunk_processor = ChunkProcessor(self.config)

        # Inicializar APIs
        self.llm = self._create_llm()
        self.embedder = self._create_embedder()
        self.splitter = CharacterTextSplitter(chunk_size=3000, chunk_overlap=50)

        # Inicializar filtro e gerador
        self.similarity_filter = SimilarityFilter(self.config, self.embedding_cache)
        self.content_generator = ContentGenerator(self.llm, self.template_manager)

    def _validate_api_key(self):
        """Valida se a API key está configurada"""
        api_key = configuracoes.OPENAI_API_KEY
        if not api_key:
            raise RuntimeError("Chave da API OpenAI não definida no ambiente.")
        self.api_key = api_key

    def _create_llm(self) -> OpenAI:
        """Cria instância do LLM"""
        return OpenAI(
            api_key=self.api_key,
            temperature=0.3,
            model_name="gpt-3.5-turbo-instruct",
            max_tokens=500,
        )

    def _create_embedder(self) -> OpenAIEmbeddings:
        """Cria instância do embedder"""
        return OpenAIEmbeddings(model="text-embedding-3-small", api_key=self.api_key)

    def _should_use_chunking(self, user_query: str) -> bool:
        """Determina se deve usar chunking baseado na query"""
        return user_query and len(user_query.strip()) > self.config.MIN_QUERY_LENGTH

    def summarize(self, documentos: List[Dict], tipo: str, user_query: str = "") -> str:
        """Método principal de resumo"""
        if self._should_use_chunking(user_query):
            return self._summarize_with_chunks(documentos, tipo, user_query)
        return self._summarize_traditional(documentos, tipo, user_query)

    def _summarize_with_chunks(
        self, documentos: List[Dict], tipo: str, user_query: str
    ) -> str:
        """Resumo otimizado usando chunks semânticos"""
        relevant_chunks = self.similarity_filter.filter_relevant_chunks(
            user_query,
            documentos,
            tipo,
            self.embedder,
            self.formatter,
            self.chunk_processor,
            max_chunks=8,
        )

        content = self._build_chunk_content(relevant_chunks, tipo)

        logger.info(
            f"Gerando resumo com chunking para tipo '{tipo}' usando {len(relevant_chunks)} chunks"
        )

        return self.content_generator.generate_summary(
            content, "resumo_otimizado", tipo=tipo
        )

    def _summarize_traditional(
        self, documentos: List[Dict], tipo: str, user_query: str
    ) -> str:
        """Resumo tradicional sem chunking"""
        if user_query:
            documentos_relevantes = self.similarity_filter.filter_relevant_documents(
                user_query,
                documentos,
                tipo,
                self.embedder,
                self.formatter,
                max_docs=self.config.MAX_DOCS_FOR_SUMMARY,
            )
        else:
            documentos_relevantes = documentos[: self.config.MAX_DOCS_FOR_SUMMARY]

        content = self._build_traditional_content(documentos_relevantes, tipo)

        logger.info(
            f"Gerando resumo tradicional do tipo '{tipo}' para {len(documentos_relevantes)} documentos"
        )

        return self.content_generator.generate_summary(content, tipo)

    def _build_chunk_content(self, chunks: List[Dict], tipo: str) -> str:
        """Constrói conteúdo a partir dos chunks"""
        chunk_texts = []
        for chunk in chunks:
            doc = chunk["original_doc"]
            if tipo == "pesquisador":
                context = f"Pesquisador {doc.get('nome', '')}: {chunk['text']}"
            elif tipo == "artigo":
                context = f"Artigo '{doc.get('title', '')}': {chunk['text']}"
            else:
                context = chunk["text"]

            chunk_texts.append(context)

        return "\n\n".join(chunk_texts)

    def _build_traditional_content(self, documentos: List[Dict], tipo: str) -> str:
        """Constrói conteúdo tradicional"""
        texts = []
        for doc in documentos:
            if tipo == "pesquisador":
                texts.append(f"{doc['nome']}: {doc.get('resumo', '')}")
            elif tipo == "artigo":
                texts.append(f"{doc['title']}: {doc.get('abstract', '')}")

        big_text = "\n\n".join(texts)
        chunks = self.splitter.split_text(big_text)
        return "\n\n".join(chunks)

    def gerar_resumo_perfil_pesquisador(
        self, nome: str, titulo: str, resumo_pessoal: str, producoes: List[Dict]
    ) -> str:
        """Gera resumo do perfil de pesquisador"""
        try:
            producoes_formatadas = self.formatter.format_producoes_for_profile(
                producoes
            )
            resumo_limitado = self.formatter._truncate_text(
                resumo_pessoal, self.config.MAX_RESUMO_CHARS
            )

            if resumo_limitado and len(resumo_pessoal) > self.config.MAX_RESUMO_CHARS:
                resumo_limitado += "..."

            resumo_limitado = resumo_limitado or "Não informado"

            logger.info(f"Gerando resumo de perfil para pesquisador: {nome}")

            return self.content_generator.generate_summary(
                producoes_formatadas,
                "perfil_pesquisador",
                nome=self.formatter._truncate_text(nome, self.config.MAX_TITULO_CHARS),
                titulo=self.formatter._truncate_text(
                    titulo, self.config.MAX_TITULO_CHARS
                ),
                resumo_pessoal=resumo_limitado,
                producoes=producoes_formatadas,
            )

        except Exception as e:
            logger.exception("Erro ao gerar resumo do perfil do pesquisador")
            return f"Erro ao gerar resumo do perfil: {str(e)}"

    def gerar_tags_pesquisador(
        self, producoes: List[Dict], user_query: str = ""
    ) -> List[str]:
        """Gera tags para pesquisador"""
        try:
            if not producoes:
                return ["Pesquisa Acadêmica", "Ciência", "Produção Científica"]

            if self._should_use_chunking(user_query):
                content = self._build_tags_content_with_chunks(
                    producoes, user_query, "artigo"
                )
            else:
                content = self._build_tags_content_traditional(
                    producoes, user_query, "artigo"
                )

            return self.content_generator.generate_tags(
                content, "tags_pesquisador", max_tags=8
            )

        except Exception:
            logger.exception("Erro ao gerar tags do pesquisador")
            return ["Pesquisa Acadêmica", "Ciência", "Produção Científica"]

    def gerar_tags_artigo(
        self, documentos: List[Dict], user_query: str = ""
    ) -> List[str]:
        """Gera tags para artigos"""
        try:
            if not documentos:
                return ["Pesquisa Científica", "Artigo Acadêmico"]

            if self._should_use_chunking(user_query):
                content = self._build_tags_content_with_chunks(
                    documentos, user_query, "artigo"
                )
            else:
                content = self._build_tags_content_traditional(
                    documentos, user_query, "artigo"
                )

            return self.content_generator.generate_tags(
                content, "tags_artigo", max_tags=5
            )

        except Exception:
            logger.exception("Erro ao gerar tags dos artigos")
            return ["Pesquisa Científica", "Artigo Acadêmico", "Ciência"]

    def _build_tags_content_with_chunks(
        self, documentos: List[Dict], user_query: str, doc_type: str
    ) -> str:
        """Constrói conteúdo para tags usando chunks"""
        relevant_chunks = self.similarity_filter.filter_relevant_chunks(
            user_query,
            documentos,
            doc_type,
            self.embedder,
            self.formatter,
            self.chunk_processor,
            max_chunks=6,
        )

        texts = []
        for chunk in relevant_chunks:
            doc = chunk["original_doc"]
            if doc_type == "artigo":
                titulo = self.formatter._truncate_text(
                    doc.get("title", "Sem título"),
                    self.config.MAX_TITULO_PRODUCAO_CHARS,
                )
                texto_chunk = self.formatter._truncate_text(
                    chunk["text"], self.config.MAX_ABSTRACT_CHARS
                )
                texts.append(f"{titulo}: {texto_chunk}")
            else:
                texts.append(self.formatter.format_for_tags(doc, doc_type))

        logger.info(f"Gerando tags com chunking para {len(relevant_chunks)} chunks")
        return "\n\n".join(texts)

    def _build_tags_content_traditional(
        self, documentos: List[Dict], user_query: str, doc_type: str
    ) -> str:
        """Constrói conteúdo para tags de forma tradicional"""
        if user_query:
            documentos_relevantes = self.similarity_filter.filter_relevant_documents(
                user_query,
                documentos,
                doc_type,
                self.embedder,
                self.formatter,
                max_docs=self.config.MAX_PRODUCOES_FOR_TAGS,
            )
        else:
            documentos_relevantes = documentos[: self.config.MAX_PRODUCOES_FOR_TAGS]

        texts = [
            self.formatter.format_for_tags(doc, doc_type)
            for doc in documentos_relevantes
        ]

        logger.info(f"Gerando tags para {len(documentos_relevantes)} documentos")
        return "\n".join(texts)
