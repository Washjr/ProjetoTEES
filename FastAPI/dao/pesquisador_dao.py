import logging
from typing import List, Dict
from psycopg2 import IntegrityError

from banco.conexao_db import Conexao
from model.pesquisador import Pesquisador

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