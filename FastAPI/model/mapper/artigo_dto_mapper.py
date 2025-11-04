from typing import List, Dict
from model.dto.artigo_busca_dto import ArtigoBuscaDTO
from langchain_core.documents import Document

class ArtigoDTOMapper:
    @staticmethod
    def to_artigo_busca_dto(document: Document) -> ArtigoBuscaDTO:
        titulo, resumo = (
            document.page_content.split("\n", 1)
            if "\n" in document.page_content
            else (document.page_content, "")
        )
        return ArtigoBuscaDTO(
            id=document.metadata.get("id", "id Not Found on Document"),
            title=titulo,
            abstract=resumo,
            doi=document.metadata.get("doi", "doi Not Found on Document"),
            year=document.metadata.get("year", 0),
            journal=document.metadata.get("journal", "journal Not Found on Document"),
            qualis=document.metadata.get("qualis", "qualis Not Found on Document"),
            authors=document.metadata.get("authors", ["authors Not Found on Document"]),
            score=document.metadata.get("score", None),
        )

    @staticmethod
    def to_artigo_selfquery_dto(artigo: ArtigoBuscaDTO) -> Document:
        return Document(
            id=artigo.id,
            page_content=f"{artigo.title}\n{artigo.abstract}",
            metadata={
                "id": getattr(artigo, "id", "id Not Found on ArtigoBuscaDTO"),
                "doi": getattr(artigo, "doi", "doi Not Found on ArtigoBuscaDTO"),
                "year": getattr(artigo, "year", 0),
                "journal": getattr(artigo, "journal", "journal Not Found on ArtigoBuscaDTO"),
                "qualis": getattr(artigo, "qualis", "qualis Not Found on ArtigoBuscaDTO"),
                "authors": getattr(artigo, "authors", ["authors Not Found on ArtigoBuscaDTO"]),
                "score": getattr(artigo, "score", None),
            },
        )

    @staticmethod
    def to_artigo_busca_dto_from_dict(data: Dict) -> ArtigoBuscaDTO:
        return ArtigoBuscaDTO(
            id=str(data.get("id")),
            title=data.get("title"),
            abstract=data.get("abstract"),
            doi=data.get("doi"),
            year=data.get("year"),
            journal=data.get("journal"),
            qualis=data.get("qualis"),
            authors=data.get("authors", []),
            score=data.get("score")
        )
    
    @staticmethod
    def to_artigo_busca_dto_list_from_dict(artigos_dict: Dict[str, Dict]) -> List[ArtigoBuscaDTO]:
        artigos_dto = []
        for artigo_data in artigos_dict.values():
            dto = ArtigoDTOMapper.to_artigo_busca_dto_from_dict(artigo_data)
            artigos_dto.append(dto)
        return artigos_dto

    @staticmethod
    def to_dict_from_artigo_busca_dto(artigo: ArtigoBuscaDTO) -> Dict:
        return {
            "id": artigo.id,
            "title": artigo.title,
            "abstract": artigo.abstract,
            "doi": artigo.doi,
            "year": artigo.year,
            "journal": artigo.journal,
            "qualis": artigo.qualis,
            "authors": artigo.authors,
            "score": artigo.score,
        }

    @staticmethod
    def to_dict_list_from_artigo_busca_dto(
        artigos: List[ArtigoBuscaDTO],
    ) -> List[Dict[str, Dict]]:
        return [
            ArtigoDTOMapper.to_dict_from_artigo_busca_dto(artigo) for artigo in artigos
        ]

    @staticmethod
    def _normalize_str(value: str) -> str:
        return value.strip().lower() if value else ""

    @staticmethod
    def _make_key(title, journal, year, doi) -> str:
        normalized_title = ArtigoDTOMapper._normalize_str(title)
        normalized_journal = ArtigoDTOMapper._normalize_str(journal)
        normalized_year = str(year).strip() if year else ""
        normalized_doi = ArtigoDTOMapper._normalize_str(doi)
        return f"{normalized_title}|{normalized_journal}|{normalized_year}|{normalized_doi}"

    @staticmethod
    def _append_authors(entry: ArtigoBuscaDTO, authors) -> None:
        if (not authors):
            return

        if entry.authors is None:
            entry.authors = []

        if isinstance(authors, (list, tuple)):
            for a in authors:
                if a and a not in entry.authors:
                    entry.authors.append(a)
        else:
            if authors and authors not in entry.authors:
                entry.authors.append(authors)

    @staticmethod
    def to_artigo_busca_dto_from_sql_rows(linhas: List[Dict]) -> List[ArtigoBuscaDTO]:
        """
        Agrupa linhas SQL que representam possivelmente o mesmo artigo (mesmo título, journal, year, doi)
        e converte para uma lista de ArtigoBuscaDTO, agregando autores únicos.
        """
        if not linhas:
            return []

        artigos_map: Dict[str, ArtigoBuscaDTO] = {}
        for linha in linhas:
            id_artigo = linha.get('id')
            title = linha.get('title')
            journal = linha.get('journal')
            year = linha.get('year')
            abstract = linha.get('abstract')
            doi = linha.get('doi')
            qualis = linha.get('qualis')
            authors = linha.get('authors')
            score = linha.get('similarity_score', None)

            key = ArtigoDTOMapper._make_key(title, journal, year, doi)

            if key not in artigos_map:
                artigos_map[key] = ArtigoBuscaDTO(
                    id=str(id_artigo),
                    title=title,
                    journal=journal,
                    year=year,
                    abstract=abstract or "",
                    doi=doi,
                    qualis=qualis,
                    authors=[],
                    score=score
                )

            ArtigoDTOMapper._append_authors(artigos_map[key], authors)

        return list(artigos_map.values())
