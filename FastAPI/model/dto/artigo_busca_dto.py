from pydantic import BaseModel, ConfigDict
from typing import Optional, List


class ArtigoBuscaDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: Optional[str]
    abstract: Optional[str]
    doi: Optional[str]
    year: Optional[int]
    journal: Optional[str]
    qualis: Optional[str]
    authors: Optional[List[str]] = None
    score: Optional[float] = None

    def __init__(self, id: str, title: Optional[str] = None, abstract: Optional[str] = None,
                 doi: Optional[str] = None, year: Optional[int] = None,
                 journal: Optional[str] = None, qualis: Optional[str] = None,
                 authors: Optional[List[str]] = None, score: Optional[float] = None,
                 embedding: Optional[str] = None):
        super().__init__(id=id, title=title, abstract=abstract, doi=doi,
                         year=year, journal=journal, qualis=qualis, authors=authors, score=score)

