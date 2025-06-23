from pydantic import BaseModel, Field
from typing import Optional

class Instituicao(BaseModel):
    id_instituicao: Optional[str] = Field(None, min_length=36, max_length=36)
    nome: str = Field(..., min_length=2, max_length=200)