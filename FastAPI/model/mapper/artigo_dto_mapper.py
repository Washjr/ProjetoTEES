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
            id=document.metadata.get("id", 0),
            title=titulo,
            abstract=resumo,
            doi=document.metadata.get("doi", ""),
            year=document.metadata.get("year", 0),
            journal=document.metadata.get("journal", ""),
            qualis=document.metadata.get("qualis", ""),
            authors=document.metadata.get("authors", []),
            score=document.metadata.get("score", None),
        )

    @staticmethod
    def to_artigo_selfquery_dto(artigo: ArtigoBuscaDTO) -> Document:
        return Document(
            page_content=f"{artigo.title}\n{artigo.abstract}",
            metadata={
                "id": getattr(artigo, "id", 0),
                "doi": getattr(artigo, "doi", ""),
                "year": getattr(artigo, "year", 0),
                "journal": getattr(artigo, "journal", ""),
                "qualis": getattr(artigo, "qualis", ""),
                "authors": getattr(artigo, "authors", []),
                "score": getattr(artigo, "score", None),
            },
        )

    @staticmethod
    def to_artigo_busca_dto_list(documents: list[Document]) -> list[ArtigoBuscaDTO]:
        return [ArtigoDTOMapper.to_artigo_busca_dto(doc) for doc in documents]

    @staticmethod
    def to_document_list(artigos: list[ArtigoBuscaDTO]) -> list[Document]:
        return [ArtigoDTOMapper.to_artigo_selfquery_dto(artigo) for artigo in artigos]

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
            authors=[author["name"] for author in data.get("authors", [])],
            score=data.get("score")
        )

    @staticmethod
    def to_artigo_busca_dto_list_from_dict(artigos_dict: Dict[str, Dict]) -> List[ArtigoBuscaDTO]:
        artigos_dto = []
        for artigo_id, artigo_data in artigos_dict.items():
            artigo_data['id'] = artigo_id
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
            "authors": [{"name": author} for author in (artigo.authors or [])],
            "score": artigo.score,
        }

    @staticmethod
    def to_dict_list_from_artigo_busca_dto(
        artigos: List[ArtigoBuscaDTO],
    ) -> List[Dict[str, Dict]]:
        return [
            ArtigoDTOMapper.to_dict_from_artigo_busca_dto(artigo) for artigo in artigos
        ]
