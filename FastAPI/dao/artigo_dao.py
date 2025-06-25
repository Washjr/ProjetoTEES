from typing import List, Dict
from banco.conexao_db import Conexao
from model.artigo import Artigo
from psycopg2 import IntegrityError
import logging

logger = logging.getLogger(__name__)

class ArtigoDAO:
    """
    DAO para operações de CRUD em artigos.
    Mantém uma conexão ao instanciar e devolve ao destruir.
    """
    def __init__(self):
        self.conexao = Conexao.obter_conexao()

    def __del__(self):
        Conexao.devolver_conexao(self.conexao)


    def listar_artigos(self) -> List[Dict]: 
        sql = "SELECT id_artigo, nome, ano, doi, id_pesquisador, id_periodico FROM artigo"
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql)
                colunas = [desc[0] for desc in cursor.description]
                linhas = cursor.fetchall()
            return [dict(zip(colunas, linha)) for linha in linhas]

        except Exception as e:
            logger.exception("Erro ao listar artigos")
            raise RuntimeError(f"Erro ao listar artigos: {e}")


    def salvar_artigo(self, artigo: Artigo) -> Dict:
        sql = (
            "INSERT INTO artigo (nome, ano, doi, id_pesquisador, id_periodico) "
            "VALUES (%s, %s, %s, %s, %s) "
            "RETURNING id_artigo, nome, ano, doi, id_pesquisador, id_periodico "
        )
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql, (
                    artigo.nome, 
                    artigo.ano, 
                    artigo.doi, 
                    artigo.id_pesquisador, 
                    artigo.id_periodico
                ))  
                colunas = [desc[0] for desc in cursor.description]
                linha = cursor.fetchone()
            self.conexao.commit()
            return dict(zip(colunas, linha))
        
        except IntegrityError as e:
            self.conexao.rollback()
            raise ValueError(f"Conflito ao salvar artigo: {e.diag.message_detail or e}")
        except Exception as e:
            self.conexao.rollback()
            logger.exception("Erro ao salvar artigo")
            raise RuntimeError(f"Erro ao salvar artigo: {e}")
        
        
    def atualizar_artigo(self, artigo:Artigo) -> Dict:
        sql = (
            "UPDATE artigo "
            "SET nome=%s, ano=%s, doi=%s, id_pesquisador=%s, id_periodico=%s "
            "WHERE id_artigo=%s "
            "RETURNING id_artigo, nome, ano, doi, id_pesquisador, id_periodico "
        )
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql, (
                    artigo.nome, 
                    artigo.ano, 
                    artigo.doi, 
                    artigo.id_pesquisador, 
                    artigo.id_periodico,
                    artigo.id_artigo
                ))     
                if cursor.rowcount == 0:
                    raise LookupError("Artigo não encontrado para atualização.")
                colunas = [desc[0] for desc in cursor.description]
                linha = cursor.fetchone()  
            self.conexao.commit() 
            return dict(zip(colunas, linha))   
        
        except LookupError:
            self.conexao.rollback()
            raise
        except Exception as e:
            self.conexao.rollback()
            logger.exception("Erro ao atualizar artigo")
            raise RuntimeError(f"Erro ao atualizar artigo: {e}")
        

    def apagar_artigo(self, id_artigo: str) -> None:
        sql = (
            "DELETE FROM artigo "
            "WHERE id_artigo=%s "
        )
        try:        
            with self.conexao.cursor() as cursor:            
                cursor.execute(sql, (id_artigo,))            
                if cursor.rowcount == 0:
                    raise LookupError("Artigo não encontrado para exclusão.")
            self.conexao.commit()
            
        except LookupError:
            self.conexao.rollback()
            raise
        except Exception as e:        
            self.conexao.rollback()
            logger.exception("Erro ao apagar artigo")
            raise RuntimeError(f"Erro ao apagar artigo: {e}")