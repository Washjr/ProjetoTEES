from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import FileResponse
from pathlib import Path
import logging

from dao.pesquisador_dao import PesquisadorDAO
from model.pesquisador import Pesquisador
from service.langchain_service import LangchainService
from service.semantic_search import SemanticSearchService

logger = logging.getLogger(__name__)


class PesquisadorController:
    """
    Controller para operações de pesquisadores.
    Encapsula lógica de roteamento e tratamento de erros.
    """
    def __init__(self):
        self.dao = PesquisadorDAO()
        self.summarizer = LangchainService()
        self.semantic = SemanticSearchService()
        self.router = APIRouter(prefix="/pesquisadores", tags=["pesquisadores"])
        self._register_routes()

    def _register_routes(self):
        self.router.add_api_route(
            "/",
            self.listar,
            # response_model=List[Pesquisador],
            response_model=None,
            methods=["GET"],
            summary="Listar pesquisadores",
            description="Retorna todos os pesquisadores cadastrados no sistema."
        )

        self.router.add_api_route(
            "/buscar",
            self.buscar_por_termo,
            response_model=None,
            methods=["GET"],
            summary="Buscar pesquisadores por termo",
            description=(
                "Retorna os pesquisadores cujo nome contém o termo passado. "
                "Pode também incluir um resumo geral dos resultados se `incluir_resumo=true`."
            )
        )

        self.router.add_api_route(
            "/busca_semantica",
            self.busca_semantica_pesquisadores,
            response_model=None,
            methods=["GET"],
            summary="Busca semântica em pesquisadores",
            description=(
                "Realiza busca semântica usando embeddings para retornar pesquisadores "
                "ordenados por relevância no contexto da consulta."
            )
        )

        self.router.add_api_route(
            "/",
            self.adicionar,
            response_model=Pesquisador,
            status_code=status.HTTP_201_CREATED,
            methods=["POST"],
            summary="Criar pesquisador",
            description=(
                "Cria um novo pesquisador e retorna o recurso criado com ID gerado. "
                "Retorna 409 em caso de conflito de chave ou 400 em erro genérico."
            )
        )

        self.router.add_api_route(
            "/{id_pesquisador}",
            self.atualizar,
            response_model=Pesquisador,
            methods=["PUT"],
            summary="Atualizar pesquisador",
            description=(
                "Atualiza um pesquisador existente por ID e retorna o recurso atualizado. "
                "Retorna 404 se não encontrado ou 400 em erro."
            )
        )

        self.router.add_api_route(
            "/{id_pesquisador}",
            self.apagar,
            status_code=status.HTTP_204_NO_CONTENT,
            methods=["DELETE"],
            summary="Deletar pesquisador",
            description="Remove um pesquisador existente por ID. Retorna 404 se não encontrado."
        )

        self.router.add_api_route(
            "/{id_pesquisador}/foto",
            self.retornar_foto,
            response_class=FileResponse,
            methods=["GET"],
            summary="Obter foto do pesquisador",
            description="Retorna a foto JPEG do pesquisador, se existir."
        )

        self.router.add_api_route(
            "/{id_pesquisador}/perfil",
            self.obter_perfil,
            response_model=None,
            methods=["GET"],
            summary="Obter perfil completo do pesquisador",
            description=(
                "Retorna dados completos do pesquisador incluindo informações básicas e lista de artigos. "
                "Formato compatível com ResearcherProfileData do frontend."
            )
        )

        self.router.add_api_route(
            "/{id_pesquisador}/resumo",
            self.obter_resumo,
            response_model=None,
            methods=["GET"],
            summary="Obter resumo e tags do pesquisador",
            description=(
                "Retorna um resumo gerado por IA e tags baseadas no perfil e produções do pesquisador. "
                "Formato compatível com ResumeData do frontend."
            )
        )
        

    def listar(self):
        return self.dao.listar_pesquisadores()
    
    def buscar_por_termo(
        self, 
        termo: str = Query(..., min_length=1), 
        incluir_resumo: bool = Query(False)
    ):
        try:
            resultados = self.dao.buscar_por_termo(termo)

            if incluir_resumo and resultados:
                resumo = self.summarizer.summarize(resultados, tipo="pesquisador")
                return {"resultados": resultados, "resumo_ia": resumo}

            return resultados
        
        except Exception as e:
            logger.exception("Erro ao buscar pesquisador pelo termo: {termo}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def busca_semantica_pesquisadores(
        self,
        termo: str = Query(..., min_length=1),
        k: int = Query(10, ge=1, le=50)
    ):        
        try:
            resultados = self.semantic.semantic_search(termo, k, tipo="pesquisador")

            return {
                "query": termo,
                "resultados": [
                    {"documento": doc, "score": score} for doc, score in resultados
                ]
            }
        
        except Exception as e:
            logger.error(f"Erro na busca semântica de pesquisadores: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def adicionar(self, pesquisador: Pesquisador):
        try:
            return self.dao.salvar_pesquisador(pesquisador)
        
        except ValueError as e:
            logger.warning("Conflito ao criar pesquisador: %s", e)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        except RuntimeError as e:
            logger.error("Erro ao criar pesquisador: %s", e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def atualizar(self, id_pesquisador: str, pesquisador: Pesquisador):
        pesquisador.id_pesquisador = id_pesquisador
        try:
            return self.dao.atualizar_pesquisador(pesquisador)
        
        except LookupError as e:
            logger.info("Pesquisador não encontrado para atualização: %s", e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except RuntimeError as e:
            logger.error("Erro ao atualizar pesquisador: %s", e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def apagar(self, id_pesquisador: str):
        try:
            self.dao.apagar_pesquisador(id_pesquisador)

        except LookupError as e:
            logger.info("Pesquisador não encontrado para exclusão: %s", e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except RuntimeError as e:
            logger.error("Erro ao apagar pesquisador: %s", e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    def obter_perfil(self, id_pesquisador: str):
        """
        Retorna o perfil completo do pesquisador (dados básicos + artigos).
        Compatível com o tipo ResearcherProfileData do frontend.
        """
        try:
            return self.dao.obter_perfil_pesquisador(id_pesquisador)
        
        except LookupError as e:
            logger.info("Pesquisador não encontrado para perfil: %s", e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except RuntimeError as e:
            logger.error("Erro ao obter perfil do pesquisador: %s", e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    def retornar_foto(self, id_pesquisador: str) -> FileResponse:
        caminho = Path("imagens") / "pesquisadores" / f"{id_pesquisador}.jpg"
        if not caminho.exists():
            logger.warning("Foto não encontrada para pesquisador %s", id_pesquisador)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foto não encontrada")
        return FileResponse(caminho, media_type="image/jpeg")

    def obter_resumo(self, id_pesquisador: str):
        """
        Retorna resumo gerado por IA e tags baseadas no perfil e produções do pesquisador.
        Compatível com o tipo ResumeData do frontend.
        """
        try:
            # Obter perfil completo do pesquisador
            perfil = self.dao.obter_perfil_pesquisador(id_pesquisador)
            
            # Extrair dados básicos do pesquisador
            researcher_data = perfil["researcher"]
            productions = perfil["productions"]
            
            # Buscar dados completos do pesquisador para o resumo pessoal
            pesquisador_completo = self.dao.obter_pesquisador_por_id(id_pesquisador)
            
            # Gerar resumo usando IA com tratamento de erro
            try:
                resumo_ia = self.summarizer.gerar_resumo_perfil_pesquisador(
                    nome=researcher_data["name"],
                    titulo=researcher_data["title"],
                    resumo_pessoal=pesquisador_completo.resumo if pesquisador_completo else "",
                    producoes=productions
                )
            except Exception as e:
                logger.warning(f"Erro ao gerar resumo com IA: {e}")
                resumo_ia = f"Pesquisador especializado em {researcher_data['title']} com {len(productions)} publicações acadêmicas."
            
            # Gerar tags usando IA com fallback
            try:
                tags = self.summarizer.gerar_tags_pesquisador(productions)
            except Exception as e:
                logger.warning(f"Erro ao gerar tags com IA: {e}")
                tags = ["Pesquisa Acadêmica", "Ciência", "Produção Científica"]
            
            return {
                "resumo_ia": resumo_ia,
                "tags": tags
            }
        
        except LookupError as e:
            logger.info("Pesquisador não encontrado para resumo: %s", e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except RuntimeError as e:
            logger.error("Erro ao obter resumo do pesquisador: %s", e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Instância do controller e router exportável
pesquisador_controller = PesquisadorController()
pesquisador_router = pesquisador_controller.router