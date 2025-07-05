from typing import List, Dict
from langchain_core.runnables import Runnable
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter
import logging

from config import configuracoes

logger = logging.getLogger(__name__)

class LangchainService:
    TEMPLATES = {
        "pesquisador": (
            "Você é um assistente de pesquisa. "
            "A seguir está uma lista de pesquisadores com seus nomes e resumos:\n\n"
            "{content}\n\n"
            "Com base nesses dados, gere uma resposta estruturada com os seguintes elementos:\n"
            "1) Um **resumo geral** dos principais temas e áreas de atuação presentes entre os pesquisadores.\n"
            "2) Destaque as **tendências ou linhas de pesquisa mais frequentes**.\n"
            "3) Liste até **5 palavras-chave curtas** que melhor representem os tópicos recorrentes.\n\n"
            "A resposta deve ser clara, objetiva e útil para o usuário que realizou a busca. "
            "Ela será exibida junto aos resultados encontrados."
        ),
        "artigo": (
            "Você é um assistente de pesquisa. "
            "A seguir está uma lista de artigos com seus nomes e resumos:\n\n"
            "{content}\n\n"
            "Com base nesses dados, gere uma resposta estruturada com os seguintes elementos:\n"
            "1) Um **resumo geral** dos principais temas abordados nos artigos.\n"
            "2) Destaque as **tendências ou tópicos de pesquisa mais frequentes**.\n"
            "3) Liste até **5 palavras-chave curtas** que melhor representem o conteúdo dos artigos.\n\n"
            "A resposta deve ser clara, objetiva e útil para o usuário que realizou a busca. "
            "Ela será exibida junto aos resultados encontrados."
        ),
    }


    def __init__(self):
        api_key = configuracoes.OPENAI_API_KEY
        if not api_key:
            raise RuntimeError("Chave da API OpenAI não definida no ambiente.")

        self.llm = OpenAI(api_key=api_key, temperature=0.3)
        self.splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=100)


    def summarize(self, documentos: List[Dict], tipo: str) -> str:
        tpl = self.TEMPLATES.get(tipo)
        if not tpl:
            raise ValueError(f"Tipo desconhecido para resumo: {tipo}")

        prompt = PromptTemplate(input_variables=["content"], template=tpl)

        texts = []
        for doc in documentos:
            if tipo == "pesquisador":
                texts.append(f"{doc['nome']}: {doc.get('resumo','')}")
            elif tipo == "artigo":
                texts.append(f"{doc['nome']}: {doc.get('resumo','')}")
        
        big_text = "\n\n".join(texts)
        chunks = self.splitter.split_text(big_text)
        content = "\n\n".join(chunks)

        logger.info("Gerando resumo do tipo '%s' para %d documentos", tipo, len(documentos))

        runnable: Runnable = prompt | self.llm
        return runnable.invoke({"content": content})