from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Union, Optional
import re

class Operator(Enum):
    AND = 'and'
    OR = 'or'

class Comparator(Enum):
    EQ = 'eq'
    NE = 'ne'
    LT = 'lt'
    LTE = 'lte'
    GT = 'gt'
    GTE = 'gte'
    IN = 'in'
    NIN = 'nin'
    LIKE = 'like'
    ILIKE = 'ilike'

class Comparison:
    def __init__(self, comparator: Comparator, attribute: str, value: Any):
        self.comparator = comparator
        self.attribute = attribute
        self.value = value

class Operation:
    def __init__(self, operator: Operator, arguments: List[Union['Operation', 'Comparison']]):
        self.operator = operator
        self.arguments = arguments

class FilterTranslator(ABC):
    """Abstract base class for translating SelfQueryRetriever filters to database WHERE clauses."""
    
    def __init__(self, attribute_mapping: Optional[Dict[str, str]] = None):
        self.attribute_mapping = attribute_mapping or {}
    
    def translate_filter(self, filter_obj: Union[Operation, Comparison, None]) -> str:
        if filter_obj is None:
            return self._get_true_clause()
        
        if isinstance(filter_obj, Comparison):
            return self._translate_comparison(filter_obj)
        elif isinstance(filter_obj, Operation):
            return self._translate_operation(filter_obj)
        else:
            raise ValueError(f"Unsupported filter type: {type(filter_obj)}")
    
    @abstractmethod
    def _get_true_clause(self) -> str:
        pass
    
    @abstractmethod
    def _translate_comparison(self, comparison: Comparison) -> str:
        pass
    
    def _translate_operation(self, operation: Operation) -> str:
        if not operation.arguments:
            return self._get_true_clause()
        
        clauses = [f"({self.translate_filter(arg)})" for arg in operation.arguments]
        operator_sql = self._get_operator_sql(operation.operator)
        return f" {operator_sql} ".join(clauses)
    
    @abstractmethod
    def _get_operator_sql(self, operator: Operator) -> str:
        pass
    
    def _get_mapped_column_name(self, attribute: str) -> str:
        return self.attribute_mapping.get(attribute, attribute)
    
    def _validate_column_name(self, column_name: str) -> None:
        if not column_name.replace('_', '').isalnum():
            raise ValueError(f"Invalid column name: {column_name}")

class FilterParser:
    
    def parse_filter_string(self, filter_string: str) -> Union[Operation, Comparison, None]:
        if not filter_string or filter_string.strip() == "":
            return None
            
        filter_string = filter_string.strip()
        
        if filter_string.startswith("operator="):
            return self._parse_operation_string(filter_string)
        elif filter_string.startswith(("Comparison(", "comparator=")):
            return self._parse_comparison_string(filter_string)
        else:
            raise ValueError(f"Unknown filter format: {filter_string}")
    
    def _parse_operation_string(self, op_string: str) -> Operation:
        operator_match = re.search(r"operator=<Operator\.(\w+):", op_string)
        if not operator_match:
            raise ValueError(f"Could not extract operator from: {op_string}")
        
        operator_name = operator_match.group(1)
        operator = Operator.AND if operator_name == "AND" else Operator.OR
        
        args_match = re.search(r"arguments=\[(.*)\]", op_string, re.DOTALL)
        if not args_match:
            raise ValueError(f"Could not extract arguments from: {op_string}")
        
        args_string = args_match.group(1)
        arguments = self._parse_arguments_list(args_string)
        
        return Operation(operator=operator, arguments=arguments)
    
    def _parse_arguments_list(self, args_string: str) -> List[Union[Operation, Comparison]]:
        arguments = []
        current_arg = ""
        paren_count = 0
        bracket_count = 0
        
        for char in args_string:
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
            elif char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
            elif char == ',' and paren_count == 0 and bracket_count == 0:
                if current_arg.strip():
                    arguments.append(self._parse_single_argument(current_arg.strip()))
                current_arg = ""
                continue
            
            current_arg += char
        
        if current_arg.strip():
            arguments.append(self._parse_single_argument(current_arg.strip()))
        
        return arguments
    
    def _parse_single_argument(self, arg_string: str) -> Union[Operation, Comparison]:
        arg_string = arg_string.strip()
        
        if arg_string.startswith("operator="):
            return self._parse_operation_string(arg_string)
        elif arg_string.startswith("Comparison("):
            return self._parse_comparison_string(arg_string)
        elif arg_string.startswith("Operation("):
            return self._parse_nested_operation(arg_string)
        else:
            raise ValueError(f"Unknown argument format: {arg_string}")
    
    def _parse_nested_operation(self, op_string: str) -> Operation:
        content = op_string[10:]
        last_paren = content.rfind(')')
        if last_paren == -1:
            raise ValueError(f"Could not find closing parenthesis in: {op_string}")
        
        content = content[:last_paren]
        return self._parse_operation_string(content)
    
    def _parse_comparison_string(self, comp_string: str) -> Comparison:
        comparator_match = re.search(r"comparator=<Comparator\.(\w+):", comp_string)
        if not comparator_match:
            raise ValueError(f"Could not extract comparator from: {comp_string}")
        
        comparator_name = comparator_match.group(1)
        
        comparator_map = {
            'EQ': Comparator.EQ, 'NE': Comparator.NE, 'LT': Comparator.LT, 'LTE': Comparator.LTE,
            'GT': Comparator.GT, 'GTE': Comparator.GTE, 'IN': Comparator.IN, 'NIN': Comparator.NIN,
            'LIKE': Comparator.LIKE, 'ILIKE': Comparator.ILIKE
        }
        
        if comparator_name not in comparator_map:
            raise ValueError(f"Unknown comparator: {comparator_name}")
        
        comparator = comparator_map[comparator_name]
        
        attr_match = re.search(r"attribute='([^']+)'", comp_string)
        if not attr_match:
            raise ValueError(f"Could not extract attribute from: {comp_string}")
        
        attribute = attr_match.group(1)
        
        value_match = re.search(r"value=(.+?)(?:\)|$)", comp_string)
        if not value_match:
            raise ValueError(f"Could not extract value from: {comp_string}")
        
        value_string = value_match.group(1)
        value = self._parse_value(value_string)
        
        return Comparison(comparator=comparator, attribute=attribute, value=value)
    
    def _parse_value(self, value_string: str) -> Any:
        value_string = value_string.strip()
        
        if value_string.startswith('[') and value_string.endswith(']'):
            list_content = value_string[1:-1]
            if not list_content.strip():
                return []
            
            items = []
            current_item = ""
            in_quotes = False
            quote_char = None
            
            for char in list_content:
                if char in ['"', "'"] and not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char and in_quotes:
                    in_quotes = False
                    quote_char = None
                elif char == ',' and not in_quotes:
                    items.append(self._clean_value(current_item.strip()))
                    current_item = ""
                    continue
                
                current_item += char
            
            if current_item.strip():
                items.append(self._clean_value(current_item.strip()))
            
            return items
        
        return self._clean_value(value_string)
    
    def _clean_value(self, value: str) -> Any:
        value = value.strip()
        
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return value[1:-1]
        
        try:
            return float(value) if '.' in value else int(value)
        except ValueError:
            pass
        
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        elif value.lower() in ('null', 'none'):
            return None
        
        return value

SelfQueryFilterTranslator = FilterTranslator

def get_where_clause(filter_string: str, translator: Optional[FilterTranslator] = None) -> str:
    if translator is None:
        from .PostgreSQLFilterTranslator import PostgreSQLFilterTranslator
        translator = PostgreSQLFilterTranslator()
    
    parser = FilterParser()
    try:
        print(filter_string)
        parsed_filter = parser.parse_filter_string(filter_string)
        sql_clause = translator.translate_filter(parsed_filter)
    except Exception as e:
        print(f"Não foi possível traduzir o filtro: {filter_string}. Erro: {e}")
        return ""
    return f"{sql_clause}"