from pydantic import BaseModel, Field
from typing import Optional

class Artigo(BaseModel):
    id_artigo: Optional[str] = Field(None, min_length=36, max_length=36)
    nome: str = Field(..., min_length=2)
    ano: int = Field(..., ge=1000, le=2100)
    resumo: Optional[str] = None
    doi: Optional[str] = Field(..., min_length=2, max_length=100)
    id_pesquisador: str = Field(..., min_length=36, max_length=36)
    id_periodico: str = Field(..., min_length=36, max_length=36)