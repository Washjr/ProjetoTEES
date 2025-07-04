import logging
from typing import List, Dict
from psycopg2 import IntegrityError

from banco.conexao_db import Conexao
from model.pesquisador import Pesquisador
from foto_lattes import buscar_codigo_lattes, baixar_foto_pesquisador

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
        sql = "SELECT id_pesquisador, nome, grau_academico, resumo, citacoes, id_orcid, id_lattes FROM pesquisador"
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql)
                colunas = [desc[0] for desc in cursor.description]
                linhas = cursor.fetchall()
            return [dict(zip(colunas, linha)) for linha in linhas]
        
        except Exception as e:
            logger.exception("Erro ao listar pesquisadores")
            raise RuntimeError(f"Erro ao listar pesquisadores: {e}")


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