from dataclasses import dataclass


@dataclass
class LangchainConfig:
    """Configurações centralizadas para o serviço Langchain"""
    # Configuração de quantidade de documentos
    MAX_DOCS_FOR_SUMMARY: int = 5
    MAX_DOCS_FOR_TAGS: int = 5
    MAX_PRODUCOES_FOR_TAGS: int = 5
    MAX_PRODUCOES_FOR_PROFILE: int = 10
    
    # Limites de caracteres
    MAX_TITULO_CHARS: int = 100
    MAX_TITULO_PRODUCAO_CHARS: int = 80
    MAX_JOURNAL_CHARS: int = 50
    MAX_JOURNAL_TAGS_CHARS: int = 30
    MAX_ABSTRACT_CHARS: int = 200
    MAX_RESUMO_CHARS: int = 300
    
    # Chunking semântico
    MAX_CHUNK_SIZE: int = 300
    MAX_CHUNKS_PER_DOC: int = 3
    CHUNK_OVERLAP: int = 50
    SIMILARITY_THRESHOLD: float = 0.3
    MAX_CHUNKS_TOTAL: int = 10
    
    # Query mínima para chunking
    MIN_QUERY_LENGTH: int = 10


class TemplateManager:
    """Gerencia os templates de prompts do sistema"""
    
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
        "resumo_otimizado": (
            "Analise estes trechos relevantes sobre {tipo}:\n\n"
            "{content}\n\n"
            "Gere um resumo em 2 parágrafos:\n"
            "1) Principais temas identificados\n"
            "2) Tendências ou padrões observados\n\n"
            "Seja conciso e informativo."
        )
    }
    
    @classmethod
    def get_template(cls, template_type: str) -> str:
        template = cls.TEMPLATES.get(template_type)
        if not template:
            raise ValueError(f"Template '{template_type}' não encontrado")
        return template
