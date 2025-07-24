import json
import re
import logging
from typing import List, Dict, Any, Tuple

from dao.artigo_dao import ArtigoDAO
from service.semantic_search import SemanticSearchService
from langchain.chains.query_constructor.schema import AttributeInfo

logger = logging.getLogger(__name__)


class SelfQueryService:
    """
    Serviço para análise e processamento de consultas com self-querying.
    Identifica filtros usando patterns e análise semântica.
    """
    
    def __init__(self):
        self.artigo_dao = ArtigoDAO()
        self.semantic_service = SemanticSearchService()
        self.metadata_config = self._load_metadata_config()
        # Construir patterns de busca básicos a partir da configuração dos campos
        self.basic_patterns = self._build_patterns_from_config()
    
    def _load_metadata_config(self) -> Dict:
        """Carrega configuração de metadados do arquivo JSON."""
        try:
            with open('config/metadata_config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar metadata_config.json: {e}")
            return {"metadata_fields": [], "basic_patterns": {}, "document_content_description": ""}
    
    def _build_patterns_from_config(self) -> Dict[str, List[str]]:
        """Constrói dicionário de patterns a partir da configuração dos campos."""
        patterns = {}
        
        for field_config in self.metadata_config.get("metadata_fields", []):
            field_name = field_config["name"]
            field_patterns = field_config.get("patterns", [])
            
            if field_patterns:
                patterns[field_name] = field_patterns
        
        return patterns
    
    def process_query(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Processa uma consulta usando self-querying.
        
        Args:
            query: Consulta do usuário
            max_results: Número máximo de resultados
            
        Returns:
            Dict com artigos encontrados e filtros aplicados
        """
        extracted_filters = self._extract_filters(query)
        clean_query = self._clean_query(query, extracted_filters)
        
        # Realizar busca com filtros
        if clean_query.strip():
            # Busca semântica para a query limpa
            semantic_results = self.semantic_service.semantic_search(
                clean_query, k=max_results * 3, tipo="artigo"
            )
            
            # Aplicar filtros aos resultados semânticos
            filtered_results = self._apply_filters(semantic_results, extracted_filters)
        else:
            # Apenas filtros, buscar diretamente no banco com filtros SQL
            if extracted_filters:
                db_results = self.artigo_dao.buscar_com_filtros(extracted_filters)
                filtered_results = [(article, 1.0) for article in db_results]
            else:
                # Sem filtros e sem query, buscar todos
                all_articles = self.artigo_dao.listar_artigos()
                filtered_results = [(article, 1.0) for article in all_articles]
        
        # 4. Limitar resultados
        final_results = filtered_results[:max_results]
        
        return {
            "query": query,
            "clean_query": clean_query,
            "filters_applied": extracted_filters,
            "total_found": len(filtered_results),
            "results": [
                {
                    "article": result[0],
                    "relevance_score": result[1]
                }
                for result in final_results
            ]
        }
    
    def _extract_filters(self, query: str) -> List[Dict[str, Any]]:
        """Extrai filtros da consulta usando patterns básicos."""
        filters = []
        
        for field_config in self.metadata_config.get("metadata_fields", []):
            field_name = field_config["name"]
            field_type = field_config["type"]
            
            # Usar patterns básicos para cada campo
            patterns = self.basic_patterns.get(field_name, [])
            
            for pattern in patterns:
                matches = re.finditer(pattern, query, re.IGNORECASE)
                for match in matches:
                    if len(match.groups()) >= 2:
                        operator = match.group(1) if match.group(1) else "="
                        value = match.group(2)
                    elif len(match.groups()) == 1:
                        value = match.group(1)
                        operator = self._infer_operator_from_pattern(pattern)
                    else:
                        continue
                    
                    # Normalizar operador e converter valor
                    operator = self._normalize_operator(operator, field_config)
                    converted_value = self._convert_value(value, field_type)
                    
                    filters.append({
                        "field": field_name,
                        "operator": operator,
                        "value": converted_value,
                        "source": "pattern",
                        "pattern_used": pattern
                    })
        
        return filters
    
    def _normalize_operator(self, operator: str, field_config: Dict) -> str:
        """Normaliza operadores textuais para símbolos."""
        operator_map = {
            "maior": ">",
            "maior que": ">",
            "greater": ">",
            "maior igual": ">=",
            "maior ou igual": ">=",
            "greater equal": ">=",
            "menor": "<",
            "menor que": "<",
            "less": "<",
            "menor igual": "<=",
            "menor ou igual": "<=",
            "less equal": "<=",
            "igual": "=",
            "equal": "=",
            "": "="
        }
        
        return operator_map.get(operator.lower().strip(), operator)
    
    def _infer_operator_from_pattern(self, pattern: str) -> str:
        """Infere operador baseado no pattern usado."""
        if any(word in pattern.lower() for word in ["após", "after", "desde", "from"]):
            return ">="
        elif any(word in pattern.lower() for word in ["antes", "before", "até", "until"]):
            return "<="
        elif any(word in pattern.lower() for word in ["acima", "above", "melhor", "better"]):
            return ">="
        elif any(word in pattern.lower() for word in ["abaixo", "below", "pior", "worse"]):
            return "<="
        else:
            return "="
    
    def _convert_value(self, value: str, value_type: str) -> Any:
        """Converte valor para o tipo apropriado."""
        try:
            if value_type == "integer":
                return int(value)
            elif value_type == "float":
                return float(value)
            else:
                return value.strip()
        except ValueError:
            return value.strip()
    
    def _clean_query(self, query: str, extracted_filters: List[Dict]) -> str:
        """Remove partes da query que foram identificadas como filtros."""
        clean_query = query
        
        for filter_info in extracted_filters:
            if filter_info["source"] == "pattern":
                pattern = filter_info["pattern_used"]
                clean_query = re.sub(pattern, "", clean_query, flags=re.IGNORECASE)
        
        # Limpar espaços extras
        clean_query = re.sub(r'\s+', ' ', clean_query).strip()
        
        return clean_query
    
    def _apply_filters(self, results: List[Tuple], filters: List[Dict]) -> List[Tuple]:
        """Aplica filtros aos resultados."""
        if not filters:
            return results
        
        filtered_results = []
        
        for article, score in results:
            if self._article_matches_filters(article, filters):
                filtered_results.append((article, score))
        
        return filtered_results
    
    def _article_matches_filters(self, article: Dict, filters: List[Dict]) -> bool:
        """Verifica se um artigo atende a todos os filtros."""
        for filter_info in filters:
            field = filter_info["field"]
            operator = filter_info["operator"]
            value = filter_info["value"]
            
            if not self._check_filter_condition(article, field, operator, value):
                return False
        
        return True
    
    def _check_filter_condition(self, article: Dict, field: str, operator: str, value: Any) -> bool:
        """Verifica se um artigo atende a uma condição específica de forma dinâmica."""
        # Buscar configuração do campo no metadata_config
        field_config = self._get_field_config(field)
        if not field_config:
            return True
        
        # Mapear campo do metadata_config para campo do artigo
        article_field = self._get_article_field_name(field)
        if not article_field:
            return True
        
        article_value = article.get(article_field)
        if article_value is None:
            return False
        
        try:
            return self._compare_values(article_value, operator, value, field_config)
        except Exception as e:
            logger.warning(f"Erro na comparação do filtro {field}: {e}")
            return False
    
    def _get_field_config(self, field_name: str) -> Dict:
        """Obtém a configuração de um campo do metadata_config."""
        for field_config in self.metadata_config.get("metadata_fields", []):
            if field_config["name"] == field_name:
                return field_config
        return {}
    
    def _get_article_field_name(self, metadata_field: str) -> str:
        """Mapeia campo do metadata_config para campo do artigo usando configuração."""
        field_config = self._get_field_config(metadata_field)
        return field_config.get("article_field", metadata_field)
    
    def _compare_values(self, article_value: Any, operator: str, filter_value: Any, field_config: Dict) -> bool:
        """Compara valores de forma dinâmica baseada na configuração do campo."""
        field_type = field_config.get("type", "string")
        
        if field_type == "integer" or field_type == "float":
            return self._compare_numeric_values(article_value, operator, filter_value)
        elif field_type == "string":
            # Verificar se é um campo hierárquico
            if field_config.get("hierarchy"):
                return self._compare_hierarchical_values(
                    article_value, operator, filter_value, field_config.get("hierarchy")
                )
            # Verificar se é um campo de lista
            elif field_config.get("is_list", False):
                return self._compare_list_values(
                    article_value, operator, filter_value, field_config.get("list_search_field", "")
                )
            else:
                return self._compare_string_values(article_value, operator, filter_value)
        
        return False
    
    def _compare_numeric_values(self, article_value: Any, operator: str, filter_value: Any) -> bool:
        """Compara valores numéricos de forma genérica."""
        try:
            article_num = float(article_value)
            filter_num = float(filter_value)
            
            if operator == "=":
                return article_num == filter_num
            elif operator == ">":
                return article_num > filter_num
            elif operator == ">=":
                return article_num >= filter_num
            elif operator == "<":
                return article_num < filter_num
            elif operator == "<=":
                return article_num <= filter_num
            elif operator == "contains":
                return str(filter_value) in str(article_value)
        except (ValueError, TypeError):
            return False
        
        return False
    
    def _compare_string_values(self, article_value: str, operator: str, filter_value: str) -> bool:
        """Compara strings de forma genérica."""
        if operator == "contains" or operator == "=":
            if operator == "contains":
                return filter_value.lower() in article_value.lower()
            else:  # operator == "="
                return article_value.lower() == filter_value.lower()
        
        return False
    
    def _compare_hierarchical_values(self, article_value: str, operator: str, filter_value: str, hierarchy: List[str]) -> bool:
        """Compara valores hierárquicos de forma genérica usando configuração."""
        try:
            article_index = hierarchy.index(article_value)
            filter_index = hierarchy.index(filter_value)
            
            if operator == "=":
                return article_index == filter_index
            elif operator == ">=" or operator == "melhor":
                return article_index <= filter_index  # Menor índice = melhor
            elif operator == "<=" or operator == "pior":
                return article_index >= filter_index
            elif operator == ">":
                return article_index < filter_index
            elif operator == "<":
                return article_index > filter_index
        except ValueError:
            return False
        
        return False
    
    def _compare_list_values(self, article_list: List[Dict], operator: str, filter_value: str, search_field: str) -> bool:
        """Compara valores em listas usando configuração do campo de busca."""
        if operator == "contains" or operator == "=":
            for item in article_list:
                if isinstance(item, dict):
                    # Usar o campo configurado para busca
                    item_value = item.get(search_field, "") if search_field else str(item)
                else:
                    item_value = str(item)
                
                if filter_value.lower() in item_value.lower():
                    return True
        
        return False
