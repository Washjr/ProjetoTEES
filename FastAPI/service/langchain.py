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
    }


    def __init__(self):
        api_key = configuracoes.OPENAI_API_KEY
        if not api_key:
            raise RuntimeError("Chave da API OpenAI não definida no ambiente.")

        # Usar gpt-3.5-turbo que tem limite maior de tokens
        self.llm = OpenAI(api_key=api_key, temperature=0.3, model_name="gpt-3.5-turbo-instruct", max_tokens=500)
        self.splitter = CharacterTextSplitter(chunk_size=3000, chunk_overlap=50)


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
                texts.append(f"{doc['title']}: {doc.get('abstract','')}")
        
        big_text = "\n\n".join(texts)
        chunks = self.splitter.split_text(big_text)
        content = "\n\n".join(chunks)

        logger.info("Gerando resumo do tipo '%s' para %d documentos", tipo, len(documentos))

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
            # Limitar a 10 produções para evitar excesso de tokens
            producoes_limitadas = producoes[:10] if len(producoes) > 10 else producoes
            
            for i, producao in enumerate(producoes_limitadas, 1):
                # Formato mais conciso
                titulo_producao = producao.get('title', 'Sem título')[:100]  # Limitar título
                ano = producao.get('year', 'N/A')
                journal = producao.get('journal', '')[:50] if producao.get('journal') else ''  # Limitar journal
                
                texto_producao = f"{i}. {titulo_producao} ({ano})"
                if journal:
                    texto_producao += f" - {journal}"
                
                producoes_texto.append(texto_producao)

            producoes_formatadas = "\n".join(producoes_texto) if producoes_texto else "Nenhuma produção encontrada."
            
            # Limitar o resumo pessoal também
            resumo_limitado = (resumo_pessoal[:300] + "...") if resumo_pessoal and len(resumo_pessoal) > 300 else (resumo_pessoal or "Não informado")

            logger.info("Gerando resumo de perfil para pesquisador: %s", nome)

            runnable: Runnable = prompt | self.llm
            return runnable.invoke({
                "nome": nome[:100],  # Limitar nome também por segurança
                "titulo": titulo[:100],  # Limitar título
                "resumo_pessoal": resumo_limitado,
                "producoes": producoes_formatadas
            })

        except Exception as e:
            logger.exception("Erro ao gerar resumo do perfil do pesquisador")
            return f"Erro ao gerar resumo do perfil: {str(e)}"

    def gerar_tags_pesquisador(self, producoes: List[Dict]) -> List[str]:
        """
        Gera tags (palavras-chave) baseadas nas produções acadêmicas do pesquisador.
        """
        try:
            if not producoes:
                return ["Pesquisa Acadêmica", "Ciência", "Produção Científica"]

            template = self.TEMPLATES["tags_pesquisador"]
            prompt = PromptTemplate(input_variables=["producoes"], template=template)

            # Formatar produções de forma mais concisa - limitar a 8 produções
            producoes_limitadas = producoes[:8] if len(producoes) > 8 else producoes
            producoes_texto = []
            
            for producao in producoes_limitadas:
                titulo = producao.get('title', 'Sem título')[:80]  # Limitar título
                journal = producao.get('journal', '')[:30] if producao.get('journal') else ''  # Limitar journal
                
                texto = f"• {titulo}"
                if journal:
                    texto += f" ({journal})"
                producoes_texto.append(texto)

            producoes_formatadas = "\n".join(producoes_texto)

            logger.info("Gerando tags para %d produções acadêmicas", len(producoes_limitadas))

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