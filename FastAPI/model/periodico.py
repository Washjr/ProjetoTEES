from pydantic import BaseModel, Field
from typing import Optional

class Periodico(BaseModel):
    id_periodico: Optional[str] = Field(None, min_length=36, max_length=36)
    nome: str = Field(..., min_length=2, max_length=200)
    qualis: str = Field(..., min_length=2, max_length=2)
    issn: str = Field(..., min_length=8, max_length=8)