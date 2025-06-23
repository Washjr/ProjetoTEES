from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class Patente(BaseModel):
    id_patente: Optional[str] = Field(None, min_length=36, max_length=36)
    nome: str = Field(..., min_length=2, max_length=200)
    ano: int = Field(..., ge=1000, le=2100)    
    data_concessao: Optional[date] = Field(None)
    id_pesquisador: str = Field(..., min_length=36, max_length=36)