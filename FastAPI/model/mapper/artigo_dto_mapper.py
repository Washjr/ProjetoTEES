from model.dto.artigo_busca_dto import ArtigoBuscaDTO
from langchain_core.documents import Document

class ArtigoDTOMapper:
    @staticmethod
    def to_artigo_busca_dto(document: Document) -> ArtigoBuscaDTO:
        titulo, resumo = document.page_content.split('\n', 1) if '\n' in document.page_content else (document.page_content, "")
        return ArtigoBuscaDTO(
            id=document.metadata.get('id', 0),
            title=titulo,
            abstract=resumo,
            doi=document.metadata.get('doi', ""),
            year=document.metadata.get('year', 0),
            journal=document.metadata.get('journal', ""),
            qualis=document.metadata.get('qualis', ""),
            authors=document.metadata.get('authors', []),
            score=document.metadata.get('score', None)
        )

    @staticmethod
    def to_artigo_selfquery_dto(artigo: ArtigoBuscaDTO) -> Document:
        return Document(
            page_content=f"{artigo.title}\n{artigo.abstract}",
            metadata={
                "id": artigo.id,
                "doi": artigo.doi,
                "year": artigo.year,
                "journal": artigo.journal,
                "qualis": artigo.qualis,
                "authors": artigo.authors,
                "score": artigo.score
            }
        )
    
    @staticmethod
    def to_artigo_busca_dto_list(documents: list[Document]) -> list[ArtigoBuscaDTO]:
        return [ArtigoDTOMapper.to_artigo_busca_dto(doc) for doc in documents]
    
    @staticmethod
    def to_document_list(artigos: list[ArtigoBuscaDTO]) -> list[Document]:
        return [ArtigoDTOMapper.to_artigo_selfquery_dto(artigo) for artigo in artigos]