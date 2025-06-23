from pydantic import BaseModel, Field
from typing import Optional

class Software(BaseModel):
    id_software: Optional[str] = Field(None, min_length=36, max_length=36)
    nome: str = Field(..., min_length=2, max_length=200)
    ano: int = Field(..., ge=1000, le=2100)   
    plataforma: Optional[str] = Field(..., min_length=2, max_length=200)
    finalidade: Optional[str] = Field(..., min_length=2, max_length=200)
    id_pesquisador: str = Field(..., min_length=36, max_length=36)