import json
import re
import logging
from typing import List, Dict, Any, Tuple, Optional

from langchain_openai import OpenAIEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from config import configuracoes
from dao.artigo_dao import ArtigoDAO
from service.semantic_search import SemanticSearchService

logger = logging.getLogger(__name__)


class SelfQueryService:
    """
    Serviço para análise e processamento de consultas com self-querying.
    Identifica filtros usando patterns e análise semântica.
    """
    
    def __init__(self):
        self.artigo_dao = ArtigoDAO()
        self.semantic_service = SemanticSearchService()
        self.embedder = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=configuracoes.OPENAI_API_KEY
        )
        self.metadata_config = self._load_metadata_config()
    
    def _load_metadata_config(self) -> Dict:
        """Carrega configuração de metadados do arquivo JSON."""
        try:
            with open('config/metadata_config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar metadata_config.json: {e}")
            return {"metadata_fields": [], "search_settings": {}}
    
    def process_query(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Processa uma consulta usando self-querying.
        
        Args:
            query: Consulta do usuário
            max_results: Número máximo de resultados
            
        Returns:
            Dict com artigos encontrados e filtros aplicados
        """
        # 1. Extrair filtros da consulta
        extracted_filters = self._extract_filters(query)
        
        # 2. Limpar query removendo os filtros identificados
        clean_query = self._clean_query(query, extracted_filters)
        
        # 3. Realizar busca com filtros
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
        """Extrai filtros da consulta usando patterns e análise semântica."""
        filters = []
        
        for field_config in self.metadata_config.get("metadata_fields", []):
            # 1. Tentar patterns regex primeiro
            pattern_filters = self._extract_with_patterns(query, field_config)
            filters.extend(pattern_filters)
            
            # 2. Se não encontrou com patterns, tentar análise semântica
            if not pattern_filters:
                semantic_filters = self._extract_with_semantics(query, field_config)
                filters.extend(semantic_filters)
        
        return filters
    
    def _extract_with_patterns(self, query: str, field_config: Dict) -> List[Dict[str, Any]]:
        """Extrai filtros usando patterns regex."""
        filters = []
        patterns = field_config.get("comparison_operators", {}).get("patterns", [])
        
        for pattern in patterns:
            matches = re.finditer(pattern, query, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 2:
                    operator = match.group(1) if match.group(1) else "="
                    value = match.group(2)
                    
                    # Converter operadores textuais
                    operator = self._normalize_operator(operator, field_config)
                    
                    filters.append({
                        "field": field_config["name"],
                        "operator": operator,
                        "value": self._convert_value(value, field_config["type"]),
                        "source": "pattern",
                        "pattern_used": pattern
                    })
                elif len(match.groups()) == 1:
                    # Pattern com apenas valor (ex: "após 2020")
                    value = match.group(1)
                    operator = self._infer_operator_from_pattern(pattern)
                    
                    filters.append({
                        "field": field_config["name"],
                        "operator": operator,
                        "value": self._convert_value(value, field_config["type"]),
                        "source": "pattern",
                        "pattern_used": pattern
                    })
        
        return filters
    
    def _extract_with_semantics(self, query: str, field_config: Dict) -> List[Dict[str, Any]]:
        """Extrai filtros usando análise semântica."""
        if not field_config.get("nlp_processing", {}).get("enable_fuzzy_matching", False):
            return []
        
        filters = []
        semantic_keywords = field_config.get("semantic_keywords", [])
        
        if not semantic_keywords:
            return []
        
        try:
            # Criar embeddings para a query e keywords
            query_embedding = np.array(self.embedder.embed_query(query)).reshape(1, -1)
            
            for keyword in semantic_keywords:
                keyword_embedding = np.array(self.embedder.embed_query(keyword)).reshape(1, -1)
                similarity = cosine_similarity(query_embedding, keyword_embedding)[0][0]
                
                threshold = field_config.get("nlp_processing", {}).get("similarity_threshold", 0.7)
                
                if similarity >= threshold:
                    # Campo identificado semanticamente, tentar extrair valor
                    extracted_value = self._extract_value_from_semantic_context(
                        query, field_config, keyword
                    )
                    
                    if extracted_value:
                        filters.append({
                            "field": field_config["name"],
                            "operator": extracted_value["operator"],
                            "value": extracted_value["value"],
                            "source": "semantic",
                            "keyword_matched": keyword,
                            "similarity_score": similarity
                        })
                        break  # Primeira correspondência semântica encontrada
        
        except Exception as e:
            logger.warning(f"Erro na análise semântica para {field_config['name']}: {e}")
        
        return filters
    
    def _extract_value_from_semantic_context(self, query: str, field_config: Dict, keyword: str) -> Optional[Dict]:
        """Extrai valor do contexto semântico."""
        field_type = field_config["type"]
        
        if field_type == "integer" and field_config["name"] == "year":
            # Buscar anos na query
            year_matches = re.findall(r'\b(19|20)\d{2}\b', query)
            if year_matches:
                year = int(year_matches[0])
                
                # Inferir operador do contexto
                if any(word in query.lower() for word in ["após", "depois", "desde", "from", "after"]):
                    operator = ">="
                elif any(word in query.lower() for word in ["antes", "até", "before", "until"]):
                    operator = "<="
                else:
                    operator = "="
                
                return {"operator": operator, "value": year}
        
        elif field_type == "string" and field_config["name"] == "qualis":
            # Buscar classificações Qualis
            qualis_matches = re.findall(r'\b([A-C][1-4]?)\b', query.upper())
            if qualis_matches:
                qualis = qualis_matches[0]
                
                # Inferir operador do contexto
                if any(word in query.lower() for word in ["melhor", "acima", "above", "better"]):
                    operator = ">="
                elif any(word in query.lower() for word in ["pior", "abaixo", "below", "worse"]):
                    operator = "<="
                else:
                    operator = "="
                
                return {"operator": operator, "value": qualis}
        
        elif field_type == "string" and field_config["name"] in ["journal", "author_name"]:
            # Para campos de texto, usar busca por proximidade
            return {"operator": "contains", "value": keyword}
        
        return None
    
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
        """Verifica se um artigo atende a uma condição específica."""
        # Mapear campos do metadata_config para campos do artigo
        field_mapping = {
            "year": "year",
            "qualis": "qualis",
            "journal": "journal",
            "author_name": "authors",
            "doi": "doi"
        }
        
        article_field = field_mapping.get(field)
        if not article_field:
            return True
        
        article_value = article.get(article_field)
        
        if article_value is None:
            return False
        
        try:
            if field == "year":
                return self._compare_numeric(article_value, operator, value)
            elif field == "qualis":
                return self._compare_qualis(article_value, operator, value)
            elif field == "author_name":
                return self._compare_authors(article_value, operator, value)
            elif field in ["journal", "doi"]:
                return self._compare_string(article_value, operator, value)
        except Exception as e:
            logger.warning(f"Erro na comparação do filtro {field}: {e}")
            return False
        
        return True
    
    def _compare_numeric(self, article_value: Any, operator: str, filter_value: Any) -> bool:
        """Compara valores numéricos."""
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
        except (ValueError, TypeError):
            return False
        
        return False
    
    def _compare_qualis(self, article_value: str, operator: str, filter_value: str) -> bool:
        """Compara classificações Qualis."""
        hierarchy = ["A1", "A2", "B1", "B2", "B3", "B4", "C"]
        
        try:
            article_index = hierarchy.index(article_value)
            filter_index = hierarchy.index(filter_value)
            
            if operator == "=":
                return article_index == filter_index
            elif operator == ">=" or operator == "melhor":
                return article_index <= filter_index  # Menor índice = melhor
            elif operator == "<=" or operator == "pior":
                return article_index >= filter_index
        except ValueError:
            return False
        
        return False
    
    def _compare_authors(self, authors_list: List[Dict], operator: str, filter_value: str) -> bool:
        """Compara autores."""
        if operator == "contains" or operator == "=":
            for author in authors_list:
                if filter_value.lower() in author.get("name", "").lower():
                    return True
        
        return False
    
    def _compare_string(self, article_value: str, operator: str, filter_value: str) -> bool:
        """Compara strings."""
        if operator == "contains":
            return filter_value.lower() in article_value.lower()
        elif operator == "=":
            return article_value.lower() == filter_value.lower()
        
        return False
