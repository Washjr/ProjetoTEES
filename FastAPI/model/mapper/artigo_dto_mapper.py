from typing import List, Dict
from model.dto.artigo_busca_dto import ArtigoBuscaDTO
from langchain_core.documents import Document
from service.embedding.embedding_service import EmbeddingResult

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
    def to_artigo_busca_dto_from_embedding_result(result: EmbeddingResult) -> ArtigoBuscaDTO:
        authors = result.metadata.get("authors")
        if authors is None:
            authors = ["authors Not Found on EmbeddingResult"]

        return ArtigoBuscaDTO(
            id=str(result.id),
            title=result.metadata.get("title", "Title Not Found on EmbeddingResult"),
            abstract=result.metadata.get("abstract", "Abstract Not Found on EmbeddingResult"),
            doi=result.metadata.get("doi", "DOI Not Found on EmbeddingResult"),
            year=result.metadata.get("year", 0),
            journal=result.metadata.get("journal", "Journal Not Found on EmbeddingResult"),
            qualis=result.metadata.get("qualis", "Qualis Not Found on EmbeddingResult"),
            authors=authors,
            score=result.metadata.get("score", None),
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
    def to_artigo_busca_dto_list(documents: list[Document]) -> list[ArtigoBuscaDTO]:
        return [ArtigoDTOMapper.to_artigo_busca_dto(doc) for doc in documents]

    @staticmethod
    def to_document_list(artigos: list[ArtigoBuscaDTO]) -> list[Document]:
        return [ArtigoDTOMapper.to_artigo_selfquery_dto(artigo) for artigo in artigos]