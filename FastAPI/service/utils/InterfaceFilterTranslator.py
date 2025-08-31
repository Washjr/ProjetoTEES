from typing import Any, Optional, Dict
from .SelfQueryFilterTranslator import FilterTranslator, Comparator, Comparison, Operator

class InterfaceFilterTranslator(FilterTranslator):
    """
    Classe concreta do SelfQueryFilterTranslator para retornar 
    filtros formatados para exibição na interface do usuário.
    
    Exemplo de uso:
    translator = InterfaceFilterTranslator()
    result = get_where_clause(filter_string, translator)
    # Retorna: "Qualis: A1, A2, A3, A4", "Ano >= 2020"
    """
    
    def __init__(self, attribute_mapping: Optional[Dict[str, str]] = None):
        super().__init__(attribute_mapping)
    
    def _get_true_clause(self) -> str:
        """Retorna string indicando nenhum filtro aplicado"""
        return "Nenhum filtro aplicado"
    
    def _get_operator_sql(self, operator: Operator) -> str:
        """Converte operadores para representação em texto"""
        operator_map = {
            Operator.AND: " E ", 
            Operator.OR: " OU "
        }
        if operator not in operator_map:
            raise ValueError(f"Operador não suportado: {operator}")
        return operator_map[operator]
    
    def _translate_comparison(self, comparison: Comparison) -> str:
        """Traduz uma comparação para formato de exibição na interface"""
        attribute = comparison.attribute
        comparator = comparison.comparator
        value = comparison.value
        
        # Usar o nome do atributo diretamente, capitalizando a primeira letra
        display_name = attribute.title()
        
        # Processar diferentes tipos de comparação
        return self._format_filter(display_name, comparator, value)
    
    def _format_filter(self, display_name: str, comparator: Comparator, value: Any) -> str:
        """Formata filtros de forma genérica baseado no comparador"""
        if comparator == Comparator.EQ:
            return f"{display_name}: {value}"
        elif comparator == Comparator.IN:
            if isinstance(value, list):
                # Para listas, mostrar os valores separados por vírgula
                return f"{display_name}: {', '.join(map(str, value))}"
            return f"{display_name}: {value}"
        elif comparator == Comparator.NE:
            return f"{display_name} ≠ {value}"
        elif comparator == Comparator.NIN:
            if isinstance(value, list):
                return f"{display_name} exceto: {', '.join(map(str, value))}"
            return f"{display_name} ≠ {value}"
        elif comparator in [Comparator.LIKE, Comparator.ILIKE]:
            return f"{display_name} contém '{value}'"
        else:
            symbol = self._get_comparator_symbol(comparator)
            return f"{display_name} {symbol} {value}"
    
    def _get_comparator_symbol(self, comparator: Comparator) -> str:
        """Converte comparadores para símbolos de exibição"""
        comparator_symbols = {
            Comparator.EQ: "=",
            Comparator.NE: "≠",
            Comparator.LT: "<",
            Comparator.LTE: "≤",
            Comparator.GT: ">",
            Comparator.GTE: "≥",
            Comparator.IN: "em",
            Comparator.NIN: "não em",
            Comparator.LIKE: "contém",
            Comparator.ILIKE: "contém"
        }
        return comparator_symbols.get(comparator, str(comparator.value))
