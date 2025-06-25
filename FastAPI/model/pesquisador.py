from pydantic import BaseModel, Field
from typing import Optional

class Pesquisador(BaseModel):
    id_pesquisador: Optional[str] = Field(None, min_length=36, max_length=36)
    nome: str = Field(..., min_length=2, max_length=200)
    grau_academico: str = Field(..., min_length=2, max_length=30)
    resumo: Optional[str] = Field(..., min_length=2)
    citacoes: Optional[str] = Field(..., min_length=2, max_length=1000)
    id_orcid: Optional[str] = Field(..., min_length=19, max_length=19)
    id_lattes: str = Field(..., min_length=15, max_length=16)
