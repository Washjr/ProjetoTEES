from typing import List
from langchain_core.runnables import Runnable
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from .langchain_config import TemplateManager


class ContentGenerator:
    """Responsável por gerar conteúdo usando LLM"""
    
    def __init__(self, llm: OpenAI, template_manager: TemplateManager):
        self.llm = llm
        self.template_manager = template_manager
    
    def generate_summary(self, content: str, template_type: str, **kwargs) -> str:
        """Gera resumo baseado no template"""
        template = self.template_manager.get_template(template_type)
        prompt = PromptTemplate(
            input_variables=list(kwargs.keys()) + ["content"], 
            template=template
        )
        
        runnable: Runnable = prompt | self.llm
        return runnable.invoke({"content": content, **kwargs})
    
    def generate_tags(self, content: str, template_type: str, max_tags: int = 5) -> List[str]:
        """Gera tags baseadas no conteúdo"""
        template = self.template_manager.get_template(template_type)
        prompt = PromptTemplate(input_variables=["content"], template=template)
        
        runnable: Runnable = prompt | self.llm
        resultado = runnable.invoke({"content": content})
        
        # Processar resultado
        tags = [tag.strip() for tag in resultado.split(",")]
        tags = [tag for tag in tags if tag][:max_tags]
        
        return tags if tags else self._get_default_tags(template_type)
    
    def _get_default_tags(self, template_type: str) -> List[str]:
        """Retorna tags padrão baseadas no tipo"""
        defaults = {
            "tags_pesquisador": ["Pesquisa Acadêmica", "Ciência", "Produção Científica"],
            "tags_artigo": ["Pesquisa Científica", "Artigo Acadêmico", "Ciência"]
        }
        return defaults.get(template_type, ["Ciência", "Pesquisa"])
