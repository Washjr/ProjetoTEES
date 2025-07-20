from typing import List, Dict
from langchain_core.runnables import Runnable
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter
import logging
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from config import configuracoes

logger = logging.getLogger(__name__)

class LangchainService:
    # Constantes para configuração de quantidade de documentos
    MAX_DOCS_FOR_SUMMARY = 5  # Máximo de documentos para resumo
    MAX_DOCS_FOR_TAGS = 5     # Máximo de documentos para geração de tags
    MAX_PRODUCOES_FOR_TAGS = 5  # Máximo de produções para tags de pesquisador
    MAX_PRODUCOES_FOR_PROFILE = 10  # Máximo de produções para perfil de pesquisador
    
    # Constantes para limites de caracteres
    MAX_TITULO_CHARS = 100      # Máximo de caracteres para títulos
    MAX_TITULO_PRODUCAO_CHARS = 80  # Máximo de caracteres para títulos de produções
    MAX_JOURNAL_CHARS = 50      # Máximo de caracteres para nome do journal
    MAX_JOURNAL_TAGS_CHARS = 30 # Máximo de caracteres para journal em tags
    MAX_ABSTRACT_CHARS = 200    # Máximo de caracteres para abstracts
    MAX_RESUMO_CHARS = 300      # Máximo de caracteres para resumo pessoal
    
    TEMPLATES = {
        "pesquisador": (
            "Você é um assistente de pesquisa. "
            "A seguir está uma lista de pesquisadores com seus nomes e resumos:\n\n"
            "{content}\n\n"
            "Com base nesses dados, gere uma resposta estruturada com os seguintes elementos:\n"
            "1) Um **resumo geral** dos principais temas e áreas de atuação presentes entre os pesquisadores.\n"
            "2) Destaque as **tendências ou linhas de pesquisa mais frequentes**.\n\n"
            "A resposta deve ser clara, objetiva e útil para o usuário que realizou a busca. "
            "Ela será exibida junto aos resultados encontrados."
        ),
        "artigo": (
            "Você é um assistente de pesquisa. "
            "A seguir está uma lista de artigos com seus nomes e resumos:\n\n"
            "{content}\n\n"
            "Com base nesses dados, gere uma resposta estruturada com os seguintes elementos:\n"
            "1) Um **resumo geral** dos principais temas abordados nos artigos.\n"
            "2) Destaque as **tendências ou tópicos de pesquisa mais frequentes**.\n\n"
            "A resposta deve ser clara, objetiva e útil para o usuário que realizou a busca. "
            "Ela será exibida junto aos resultados encontrados."
        ),
        "perfil_pesquisador": (
            "Analise o perfil do pesquisador:\n"
            "Nome: {nome}\n"
            "Título: {titulo}\n"
            "Resumo: {resumo_pessoal}\n\n"
            "Principais publicações:\n{producoes}\n\n"
            "Gere um resumo acadêmico em até 200 palavras destacando:\n"
            "1) Áreas de expertise\n"
            "2) Principais temas de pesquisa\n"
            "3) Características do trabalho acadêmico\n"
            "Seja conciso e informativo."
        ),
        "tags_pesquisador": (
            "Analise as publicações do pesquisador:\n{producoes}\n\n"
            "Gere exatamente 8 tags curtas (máximo 3 palavras cada) que representem:\n"
            "- Áreas de conhecimento\n"
            "- Temas de pesquisa\n"
            "- Metodologias\n\n"
            "Retorne apenas as tags separadas por vírgula."
        ),
        "tags_artigo": (
            "Analise os seguintes artigos científicos:\n{content}\n\n"
            "Gere exatamente 5 tags curtas (máximo 3 palavras cada) que representem:\n"
            "- Principais temas de pesquisa\n"
            "- Áreas de conhecimento\n"
            "- Metodologias\n\n"
            "Retorne apenas as tags separadas por vírgula."
        ),
    }


    def __init__(self):
        api_key = configuracoes.OPENAI_API_KEY
        if not api_key:
            raise RuntimeError("Chave da API OpenAI não definida no ambiente.")

        # Usar gpt-3.5-turbo que tem limite maior de tokens
        self.llm = OpenAI(api_key=api_key, temperature=0.3, model_name="gpt-3.5-turbo-instruct", max_tokens=500)
        self.embedder = OpenAIEmbeddings(api_key=api_key)
        self.splitter = CharacterTextSplitter(chunk_size=3000, chunk_overlap=50)

    def _filter_relevant_content(self, user_query: str, documentos: List[Dict], tipo: str, max_docs: int = None) -> List[Dict]:
        """
        Filtra documentos usando embedding da query do usuário para manter apenas os mais relevantes.
        """
        if max_docs is None:
            max_docs = self.MAX_DOCS_FOR_TAGS  # Valor padrão configurável
            
        if not documentos or not user_query:
            return documentos[:max_docs]
        
        try:
            # Gerar embedding da query do usuário
            query_embedding = self.embedder.embed_query(user_query)
            
            # Preparar textos dos documentos e calcular embeddings
            doc_texts = []
            for doc in documentos:
                if tipo == "pesquisador":
                    text = f"{doc.get('nome', '')} {doc.get('titulo', '')} {doc.get('resumo', '')}"
                elif tipo == "artigo":
                    text = f"{doc.get('title', '')} {doc.get('abstract', '')}"
                else:
                    text = str(doc)
                doc_texts.append(text)
            
            # Calcular embeddings dos documentos
            doc_embeddings = self.embedder.embed_documents(doc_texts)
            
            # Calcular similaridade de cosseno
            query_emb = np.array(query_embedding).reshape(1, -1)
            doc_embs = np.array(doc_embeddings)
            
            similarities = cosine_similarity(query_emb, doc_embs)[0]
            
            # Ordenar documentos por similaridade e pegar os top N
            doc_similarity_pairs = list(zip(documentos, similarities))
            doc_similarity_pairs.sort(key=lambda x: x[1], reverse=True)
            
            # Retornar apenas os documentos mais relevantes
            relevant_docs = [doc for doc, _ in doc_similarity_pairs[:max_docs]]
            
            logger.info(f"Filtrados {len(relevant_docs)} documentos mais relevantes de {len(documentos)} totais para query: '{user_query[:50]}...'")
            return relevant_docs
            
        except Exception as e:
            logger.warning(f"Erro ao filtrar documentos por relevância: {e}. Usando método original.")
            return documentos[:max_docs]


    def summarize(self, documentos: List[Dict], tipo: str, user_query: str = "") -> str:
        tpl = self.TEMPLATES.get(tipo)
        if not tpl:
            raise ValueError(f"Tipo desconhecido para resumo: {tipo}")

        prompt = PromptTemplate(input_variables=["content"], template=tpl)

        # Filtrar documentos por relevância usando embedding da query do usuário
        if user_query:
            documentos_relevantes = self._filter_relevant_content(user_query, documentos, tipo, max_docs=self.MAX_DOCS_FOR_SUMMARY)
        else:
            documentos_relevantes = documentos[:self.MAX_DOCS_FOR_SUMMARY]  # Limitar usando constante se não houver query

        texts = []
        for doc in documentos_relevantes:
            if tipo == "pesquisador":
                texts.append(f"{doc['nome']}: {doc.get('resumo','')}")
            elif tipo == "artigo":
                texts.append(f"{doc['title']}: {doc.get('abstract','')}")
        
        big_text = "\n\n".join(texts)
        chunks = self.splitter.split_text(big_text)
        content = "\n\n".join(chunks)

        logger.info("Gerando resumo do tipo '%s' para %d documentos mais relevantes de %d totais", tipo, len(documentos_relevantes), len(documentos))

        runnable: Runnable = prompt | self.llm
        return runnable.invoke({"content": content})

    def gerar_resumo_perfil_pesquisador(self, nome: str, titulo: str, resumo_pessoal: str, producoes: List[Dict]) -> str:
        """
        Gera um resumo inteligente do perfil acadêmico do pesquisador baseado em seus dados e produções.
        """
        try:
            template = self.TEMPLATES["perfil_pesquisador"]
            prompt = PromptTemplate(
                input_variables=["nome", "titulo", "resumo_pessoal", "producoes"], 
                template=template
            )

            # Limitar e formatar produções de forma mais concisa
            producoes_texto = []
            # Limitar usando constante para evitar excesso de tokens
            producoes_limitadas = producoes[:self.MAX_PRODUCOES_FOR_PROFILE] if len(producoes) > self.MAX_PRODUCOES_FOR_PROFILE else producoes
            
            for i, producao in enumerate(producoes_limitadas, 1):
                # Formato mais conciso usando constantes
                titulo_producao = producao.get('title', 'Sem título')[:self.MAX_TITULO_PRODUCAO_CHARS]  # Limitar título
                ano = producao.get('year', 'N/A')
                journal = producao.get('journal', '')[:self.MAX_JOURNAL_CHARS] if producao.get('journal') else ''  # Limitar journal
                
                texto_producao = f"{i}. {titulo_producao} ({ano})"
                if journal:
                    texto_producao += f" - {journal}"
                
                producoes_texto.append(texto_producao)

            producoes_formatadas = "\n".join(producoes_texto) if producoes_texto else "Nenhuma produção encontrada."
            
            # Limitar o resumo pessoal usando constante
            resumo_limitado = (resumo_pessoal[:self.MAX_RESUMO_CHARS] + "...") if resumo_pessoal and len(resumo_pessoal) > self.MAX_RESUMO_CHARS else (resumo_pessoal or "Não informado")

            logger.info("Gerando resumo de perfil para pesquisador: %s", nome)

            runnable: Runnable = prompt | self.llm
            return runnable.invoke({
                "nome": nome[:self.MAX_TITULO_CHARS],  # Limitar nome usando constante
                "titulo": titulo[:self.MAX_TITULO_CHARS],  # Limitar título usando constante
                "resumo_pessoal": resumo_limitado,
                "producoes": producoes_formatadas
            })

        except Exception as e:
            logger.exception("Erro ao gerar resumo do perfil do pesquisador")
            return f"Erro ao gerar resumo do perfil: {str(e)}"

    def gerar_tags_pesquisador(self, producoes: List[Dict], user_query: str = "") -> List[str]:
        """
        Gera tags (palavras-chave) baseadas nas produções acadêmicas do pesquisador, usando embedding para filtrar por relevância.
        """
        try:
            if not producoes:
                return ["Pesquisa Acadêmica", "Ciência", "Produção Científica"]

            template = self.TEMPLATES["tags_pesquisador"]
            prompt = PromptTemplate(input_variables=["producoes"], template=template)

            # Filtrar produções por relevância usando embedding da query do usuário
            if user_query:
                producoes_relevantes = self._filter_relevant_content(user_query, producoes, "artigo", max_docs=self.MAX_PRODUCOES_FOR_TAGS)
            else:
                producoes_relevantes = producoes[:self.MAX_PRODUCOES_FOR_TAGS]  # Limitar usando constante se não houver query

            # Formatar produções de forma mais concisa
            producoes_texto = []
            
            for producao in producoes_relevantes:
                titulo = producao.get('title', 'Sem título')[:self.MAX_TITULO_PRODUCAO_CHARS]  # Limitar título usando constante
                journal = producao.get('journal', '')[:self.MAX_JOURNAL_TAGS_CHARS] if producao.get('journal') else ''  # Limitar journal usando constante
                
                texto = f"• {titulo}"
                if journal:
                    texto += f" ({journal})"
                producoes_texto.append(texto)

            producoes_formatadas = "\n".join(producoes_texto)

            logger.info("Gerando tags para %d produções mais relevantes de %d totais", len(producoes_relevantes), len(producoes))

            runnable: Runnable = prompt | self.llm
            resultado = runnable.invoke({"producoes": producoes_formatadas})

            # Processar resultado para extrair as tags
            tags = [tag.strip() for tag in resultado.split(",")]
            # Limitar a 8 tags e remover vazias
            tags = [tag for tag in tags if tag][:8]
            
            return tags if tags else ["Pesquisa Acadêmica", "Ciência"]

        except Exception:
            logger.exception("Erro ao gerar tags do pesquisador")
            return ["Pesquisa Acadêmica", "Ciência", "Produção Científica"]

    def gerar_tags_artigo(self, documentos: List[Dict], user_query: str = "") -> List[str]:
        """
        Gera tags (palavras-chave) baseadas nos artigos fornecidos, usando embedding para filtrar por relevância.
        """
        try:
            if not documentos:
                return ["Pesquisa Científica", "Artigo Acadêmico"]

            template = self.TEMPLATES["tags_artigo"]
            prompt = PromptTemplate(input_variables=["content"], template=template)

            # Filtrar artigos por relevância usando embedding da query do usuário
            if user_query:
                documentos_relevantes = self._filter_relevant_content(user_query, documentos, "artigo", max_docs=self.MAX_DOCS_FOR_TAGS)
            else:
                documentos_relevantes = documentos[:self.MAX_DOCS_FOR_TAGS]  # Limitar usando constante se não houver query

            # Formatar artigos de forma concisa
            texts = []            
            for doc in documentos_relevantes:
                titulo = doc.get('title', 'Sem título')[:self.MAX_TITULO_PRODUCAO_CHARS]  # Limitar título usando constante
                abstract = doc.get('abstract', '')[:self.MAX_ABSTRACT_CHARS]  # Limitar resumo usando constante
                
                if abstract:
                    texts.append(f"{titulo}: {abstract}")
                else:
                    texts.append(titulo)

            content = "\n\n".join(texts)

            logger.info("Gerando tags para %d artigos mais relevantes de %d totais", len(documentos_relevantes), len(documentos))

            runnable: Runnable = prompt | self.llm
            resultado = runnable.invoke({"content": content})

            # Processar resultado para extrair as tags
            tags = [tag.strip() for tag in resultado.split(",")]
            # Limitar a 5 tags e remover vazias
            tags = [tag for tag in tags if tag][:5]
            
            return tags if tags else ["Pesquisa Científica", "Artigo Acadêmico"]

        except Exception:
            logger.exception("Erro ao gerar tags dos artigos")
            return ["Pesquisa Científica", "Artigo Acadêmico", "Ciência"]