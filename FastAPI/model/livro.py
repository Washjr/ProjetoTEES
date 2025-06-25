from pydantic import BaseModel, Field
from typing import Optional

class Livro(BaseModel):
    id_livro: Optional[str] = Field(None, min_length=36, max_length=36)
    nome_livro: str = Field(...)
    ano: int = Field(..., ge=1000, le=2100)   
    nome_editora: Optional[str] = Field(...) 
    isbn: str = Field(..., min_length=10, max_length=13)
    id_pesquisador: str = Field(..., min_length=36, max_length=36)