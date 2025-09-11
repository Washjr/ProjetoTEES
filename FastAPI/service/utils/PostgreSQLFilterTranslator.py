from typing import Any
import json
from .SelfQueryFilterTranslator import FilterTranslator, Comparator, Comparison, Operator

class PostgreSQLFilterTranslator(FilterTranslator):
    
    def _get_true_clause(self) -> str:
        return "TRUE"
    
    def _get_operator_sql(self, operator: Operator) -> str:
        operator_map = {Operator.AND: "AND", Operator.OR: "OR"}
        if operator not in operator_map:
            raise ValueError(f"Unsupported operator: {operator}")
        return operator_map[operator]
    
    def _translate_comparison(self, comparison: Comparison) -> str:
        column_name = self._get_mapped_column_name(comparison.attribute)
        self._validate_column_name(column_name)
        return self._build_comparison_clause(column_name, comparison.comparator, comparison.value)
    
    def _build_comparison_clause(self, column_name: str, comparator: Comparator, value: Any) -> str:
        comparison_builders = {
            Comparator.EQ: lambda c, v: f"{c} = {self._quote_value(v)}",
            Comparator.NE: lambda c, v: f"{c} != {self._quote_value(v)}",
            Comparator.LT: lambda c, v: f"{c} < {v}",
            Comparator.LTE: lambda c, v: f"{c} <= {v}",
            Comparator.GT: lambda c, v: f"{c} > {v}",
            Comparator.GTE: lambda c, v: f"{c} >= {v}",
            Comparator.IN: self._build_in_clause,
            Comparator.NIN: self._build_not_in_clause,
            Comparator.LIKE: self._build_like_clause,
            Comparator.ILIKE: self._build_ilike_clause
        }
        
        builder = comparison_builders.get(comparator)
        if not builder:
            raise ValueError(f"Unsupported comparator: {comparator}")
        
        return builder(column_name, value)
    
    def _build_in_clause(self, column_name: str, value: Any) -> str:
        if not isinstance(value, list):
            raise ValueError("IN operator requires a list of values")
        values_str = ",".join([self._quote_value(v) for v in value])
        return f"{column_name} IN ({values_str})"
    
    def _build_not_in_clause(self, column_name: str, value: Any) -> str:
        if not isinstance(value, list):
            raise ValueError("NIN operator requires a list of values")
        values_str = ",".join([self._quote_value(v) for v in value])
        return f"{column_name} NOT IN ({values_str})"
    
    def _build_like_clause(self, column_name: str, value: Any) -> str:
        return f"unaccent(lower({column_name})) LIKE unaccent(lower({self._quote_value(f'%{value}%')}))"
    
    def _build_ilike_clause(self, column_name: str, value: Any) -> str:
        return f"unaccent(lower({column_name})) ILIKE unaccent(lower({self._quote_value(f'%{value}%')}))"

    def _quote_value(self, value: Any) -> str:
        if isinstance(value, str):
            if '%' in value:
                if ' ' in value:
                    value = value.replace(' ', '%')
                return f"$${value}$$"
            else:
                escaped_value = value.replace("'", "''")
                return f"'{escaped_value}'"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        elif value is None:
            return "NULL"
        else:
            escaped_value = json.dumps(value).replace("'", "''")
            return f"'{escaped_value}'"

# Legacy compatibility
SelfQueryFilterTranslator = PostgreSQLFilterTranslator
