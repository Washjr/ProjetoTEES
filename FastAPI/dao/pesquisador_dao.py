import logging
from typing import List, Dict
from pathlib import Path
from psycopg2 import IntegrityError

from banco.conexao_db import Conexao
from model.pesquisador import Pesquisador
from service.foto_lattes import buscar_codigo_lattes, baixar_foto_pesquisador
from config import configuracoes

logger = logging.getLogger(__name__)

class PesquisadorDAO:
    """
    DAO para operações CRUD em pesquisadores.
    Mantém uma conexão ao instanciar e devolve ao destruir.
    """
    def __init__(self):
        self.conexao = Conexao.obter_conexao()

    def __del__(self):
        Conexao.devolver_conexao(self.conexao)


    def listar_pesquisadores(self) -> List[Dict]:
        sql = (
            "SELECT id_pesquisador, nome, grau_academico, resumo, citacoes, id_orcid, id_lattes "
            "FROM pesquisador "
        )
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql)
                colunas = [desc[0] for desc in cursor.description]
                linhas = cursor.fetchall()
                
                # Converte para formato compatível com ResearcherData
                resultado = []
                for linha in linhas:
                    pesquisador = dict(zip(colunas, linha))
                    researcher_data = {
                        "id": str(pesquisador["id_pesquisador"]),
                        "name": pesquisador["nome"],
                        "title": pesquisador["grau_academico"],
                        "photo": self._gerar_url_foto(pesquisador["id_lattes"])
                    }
                    resultado.append(researcher_data)
                
            return resultado
        
        except Exception as e:
            logger.exception("Erro ao listar pesquisadores")
            raise RuntimeError(f"Erro ao listar pesquisadores: {e}")


    def buscar_por_termo(self, termo: str) -> List[Dict]:
        sql = (
            "SELECT id_pesquisador, nome, grau_academico, resumo, citacoes, id_orcid, id_lattes "
            "FROM pesquisador "
            "WHERE unaccent(lower(nome)) ILIKE unaccent(lower(%s)) "
        )
        try:
            with self.conexao.cursor() as cursor:
                termo_formatado = f"%{termo.strip()}%"

                cursor.execute(sql, (termo_formatado,))
                colunas = [desc[0] for desc in cursor.description]
                linhas = cursor.fetchall()
                
                # Converte para formato compatível com ResearcherData
                resultado = []
                for linha in linhas:
                    pesquisador = dict(zip(colunas, linha))
                    researcher_data = {
                        "id": str(pesquisador["id_pesquisador"]),
                        "name": pesquisador["nome"],
                        "title": pesquisador["grau_academico"],
                        "photo": self._gerar_url_foto(pesquisador["id_lattes"])
                    }
                    resultado.append(researcher_data)
                
            return resultado
        except Exception as e:
            logger.exception(f"Erro ao buscar pesquisador pelo termo: '{termo}'")
            raise RuntimeError(f"Erro ao buscar pesquisador por termo: {e}")


    def obter_pesquisador_por_id(self, id_pesquisador: str) -> Pesquisador:
        """
        Obtém um pesquisador específico pelo ID.
        Retorna o objeto Pesquisador completo.
        """
        sql = (
            "SELECT id_pesquisador, nome, grau_academico, resumo, citacoes, id_orcid, id_lattes "
            "FROM pesquisador "
            "WHERE id_pesquisador = %s"
        )
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql, (id_pesquisador,))
                linha = cursor.fetchone()
                
                if not linha:
                    raise LookupError(f"Pesquisador com ID {id_pesquisador} não encontrado")
                
                (id_pesq, nome, grau_academico, resumo, citacoes, id_orcid, id_lattes) = linha
                
                return Pesquisador(
                    id_pesquisador=str(id_pesq),
                    nome=nome,
                    grau_academico=grau_academico,
                    resumo=resumo,
                    citacoes=citacoes,
                    id_orcid=id_orcid,
                    id_lattes=id_lattes
                )
                
        except LookupError:
            raise
        except Exception as e:
            logger.exception(f"Erro ao obter pesquisador por ID: {id_pesquisador}")
            raise RuntimeError(f"Erro ao obter pesquisador por ID: {e}")


    def salvar_pesquisador(self, pesquisador:Pesquisador) -> Dict:
        sql = (
            "INSERT INTO pesquisador (nome, grau_academico, resumo, citacoes, id_orcid, id_lattes) "
            "VALUES (%s, %s, %s, %s, %s, %s) "
            "RETURNING id_pesquisador, nome, grau_academico, resumo, citacoes, id_orcid, id_lattes "
        )
        try:        
            with self.conexao.cursor() as cursor:
                cursor.execute(sql, (
                    pesquisador.nome, 
                    pesquisador.grau_academico, 
                    pesquisador.resumo, 
                    pesquisador.citacoes, 
                    pesquisador.id_orcid, 
                    pesquisador.id_lattes
                ))
                colunas = [desc[0] for desc in cursor.description]
                linha = cursor.fetchone()
            self.conexao.commit()            
            return dict(zip(colunas, linha))

        except IntegrityError as e:
            self.conexao.rollback()
            raise ValueError(f"Conflito ao salvar pesquisador: {e.diag.message_detail or e}")          
        except Exception as e:
            self.conexao.rollback()
            logger.exception("Erro ao salvar pesquisador")
            raise RuntimeError(f"Erro ao salvar pesquisador: {e}")
        

    def atualizar_pesquisador(self, pesquisador:Pesquisador) -> Dict:
        sql = (
            "UPDATE pesquisador "
            "SET nome=%s, grau_academico=%s, resumo=%s, citacoes=%s, id_orcid=%s, id_lattes=%s "
            "WHERE id_pesquisador=%s "
            "RETURNING id_pesquisador, nome, grau_academico, resumo, citacoes, id_orcid, id_lattes "
        )
        try:        
            with self.conexao.cursor() as cursor:
                cursor.execute(sql, (
                    pesquisador.nome, 
                    pesquisador.grau_academico, 
                    pesquisador.resumo, 
                    pesquisador.citacoes, 
                    pesquisador.id_orcid, 
                    pesquisador.id_lattes,
                    pesquisador.id_pesquisador
                ))
                if cursor.rowcount == 0:
                    raise LookupError("Pesquisador não encontrado para atualização.")
                colunas = [desc[0] for desc in cursor.description]
                linha = cursor.fetchone()  
            self.conexao.commit()            
            return dict(zip(colunas, linha))   

        except LookupError:
            self.conexao.rollback()
            raise
        except Exception as e:
            self.conexao.rollback()
            logger.exception("Erro ao atualizar pesquisador")
            raise RuntimeError(f"Erro ao atualizar pesquisador: {e}")


    def apagar_pesquisador(self, id_pesquisador: str) -> None:
        sql = (
            "DELETE FROM pesquisador "
            "WHERE id_pesquisador=%s "
        )
        try:        
            with self.conexao.cursor() as cursor:            
                cursor.execute(sql, (id_pesquisador,))            
                if cursor.rowcount == 0:
                    raise LookupError("Pesquisador não encontrado para exclusão.") 
            self.conexao.commit()            

        except LookupError:
            self.conexao.rollback()
            raise
        except Exception as e:        
            self.conexao.rollback()
            logger.exception("Erro ao apagar pesquisador")
            raise RuntimeError(f"Erro ao apagar pesquisador: {e}")
        

    def buscar_artigos_por_pesquisador(self, id_pesquisador: str) -> List[Dict]:
        """
        Busca todos os artigos de um pesquisador específico.
        Retorna no formato compatível com ArticleData.
        """
        sql = (
            "SELECT "
            "a.id_artigo as id, "
            "a.nome as title, "
            "per.nome as journal, "
            "a.ano as year, "
            "a.resumo as abstract, "
            "a.doi, "
            "per.qualis, "
            "p.id_pesquisador as author_id, "
            "p.nome as author_name "
            "FROM artigo a "
            "JOIN periodico per ON a.id_periodico = per.id_periodico "
            "JOIN pesquisador p ON a.id_pesquisador = p.id_pesquisador "
            "WHERE a.id_pesquisador = %s "
            "ORDER BY a.ano DESC, a.nome"
        )
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql, (id_pesquisador,))
                linhas = cursor.fetchall()
            
            # Converter para formato ArticleData
            artigos = []
            for linha in linhas:
                (id_artigo, title, journal, year, abstract, doi, qualis,
                 author_id, author_name) = linha
                
                artigo = {
                    "id": str(id_artigo),
                    "title": title,
                    "journal": journal,
                    "year": year,
                    "abstract": abstract or "",
                    "doi": doi,
                    "qualis": qualis,
                    "authors": [{
                        "id": str(author_id),
                        "name": author_name
                    }]
                }
                artigos.append(artigo)
            
            return artigos
            
        except Exception as e:
            logger.exception(f"Erro ao buscar artigos do pesquisador {id_pesquisador}")
            raise RuntimeError(f"Erro ao buscar artigos do pesquisador: {e}")


    def obter_perfil_pesquisador(self, id_pesquisador: str) -> Dict:
        """
        Obtém dados completos do perfil do pesquisador (dados básicos + artigos).
        Retorna no formato compatível com ResearcherProfileData.
        """
        # Buscar dados básicos do pesquisador
        sql_pesquisador = (
            "SELECT id_pesquisador, nome, grau_academico, resumo, citacoes, id_orcid, id_lattes "
            "FROM pesquisador "
            "WHERE id_pesquisador = %s"
        )
        
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql_pesquisador, (id_pesquisador,))
                linha = cursor.fetchone()
                
                if not linha:
                    raise LookupError(f"Pesquisador com ID {id_pesquisador} não encontrado")
                
                # Converter dados do pesquisador para formato ResearcherData
                (id_pesq, nome, grau_academico, resumo, citacoes, id_orcid, id_lattes) = linha
                
                researcher_data = {
                    "id": str(id_pesq),
                    "name": nome,
                    "title": grau_academico,
                    "photo": self._gerar_url_foto(id_lattes)
                }
                
                # Buscar artigos do pesquisador
                artigos = self.buscar_artigos_por_pesquisador(id_pesquisador)
                
                # Retornar no formato ResearcherProfileData
                return {
                    "researcher": researcher_data,
                    "productions": artigos
                }
                
        except LookupError:
            raise  # Repassar erro de não encontrado
        except Exception as e:
            logger.exception(f"Erro ao obter perfil do pesquisador {id_pesquisador}")
            raise RuntimeError(f"Erro ao obter perfil do pesquisador: {e}")


    def sincronizar_fotos(self) -> None:
        """
        Para cada pesquisador com id_lattes e sem foto sincronizada,
        tenta obter o código K, baixar a foto e, em qualquer caso,
        marca foto_sincronizado = TRUE para não tentar de novo.
        """
        sql_consulta = """
            SELECT id_pesquisador, id_lattes
            FROM pesquisador
            WHERE id_lattes IS NOT NULL AND foto_sincronizada = FALSE
        """
        sql_atualizacao = """
            UPDATE pesquisador
            SET foto_sincronizada = TRUE
            WHERE id_pesquisador = %s
        """
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql_consulta)
                pesquisadores = cursor.fetchall()

            logger.info(f"{len(pesquisadores)} pesquisadores sem foto sincronizada encontrados.")

            for id_pesq, id_lattes in pesquisadores:
                try:
                    codigo_k = buscar_codigo_lattes(id_lattes)
                except Exception:
                    codigo_k = None
                    logger.exception(f"Erro ao buscar código K para Lattes {id_lattes}")

                if codigo_k:
                    try:
                        sucesso = baixar_foto_pesquisador(codigo_k, id_lattes)
                        if not sucesso:
                            logger.warning(f"Falha ao baixar foto para pesquisador {id_pesq}")
                    except Exception:
                        logger.exception(f"Erro ao baixar foto para pesquisador {id_pesq}")
                else:
                    logger.warning(f"Código K não encontrado para pesquisador {id_pesq}")

                try:
                    with self.conexao.cursor() as cursor:
                        cursor.execute(sql_atualizacao, (id_pesq,))
                    self.conexao.commit()
                except Exception:
                    self.conexao.rollback()
                    logger.exception(f"Erro ao atualizar flag de sincronização para {id_pesq}")

        except Exception:
            logger.exception("Erro inesperado na sincronização de fotos")
            raise RuntimeError("Erro ao sincronizar fotos de pesquisadores")
    

    def _gerar_url_foto(self, id_lattes: str) -> str:
        """
        Gera a URL completa da foto do pesquisador.
        Verifica se o arquivo existe fisicamente, caso contrário retorna URL de imagem padrão.
        """
        if not id_lattes:
            logger.warning("ID Lattes não fornecido. Usando imagem padrão.")
            return f"{configuracoes.BASE_URL}/imagens/pesquisadores/default.jpg"
        
        caminho_foto = Path(__file__).parent.parent / "imagens" / "pesquisadores" / f"{id_lattes}.jpg"
        
        if caminho_foto.exists():
            return f"{configuracoes.BASE_URL}/imagens/pesquisadores/{id_lattes}.jpg"
        else:
            logger.warning(f"Foto não encontrada para id_lattes: {id_lattes}. Usando imagem padrão.")
            return f"{configuracoes.BASE_URL}/imagens/pesquisadores/default.jpg"