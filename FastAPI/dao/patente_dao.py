import logging
from typing import List, Dict
from psycopg2 import IntegrityError

from banco.conexao_db import Conexao
from model.patente import Patente

logger = logging.getLogger(__name__)

class PatenteDAO:
    """
    DAO para operações de CRUD em patentes.
    Mantém uma conexão ao instanciar e devolve ao destruir.
    """
    def __init__(self):
        self.conexao = Conexao.obter_conexao()

    def __del__(self):
        Conexao.devolver_conexao(self.conexao)


    def listar_patentes(self) -> List[Dict]:
        sql = (
            "SELECT id_patente, nome, ano, data_concessao, id_pesquisador "
            "FROM patente"
        )
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql)
                colunas = [desc[0] for desc in cursor.description]
                linhas = cursor.fetchall()
            return [dict(zip(colunas, linha)) for linha in linhas]
        
        except Exception as e:
            logger.exception("Erro ao listar patentes")
            raise RuntimeError(f"Erro ao listar patentes: {e}")


    def salvar_patente(self, patente: Patente) -> Dict:
        sql = (
            "INSERT INTO patente (nome, ano, data_concessao, id_pesquisador) "
            "VALUES (%s, %s, %s, %s) "
            "RETURNING id_patente, nome, ano, data_concessao, id_pesquisador"
        )
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql, (
                    patente.nome,
                    patente.ano,
                    patente.data_concessao,
                    patente.id_pesquisador
                ))
                colunas = [desc[0] for desc in cursor.description]
                linha = cursor.fetchone()
            self.conexao.commit()
            return dict(zip(colunas, linha))
        
        except IntegrityError as e:
            self.conexao.rollback()
            raise ValueError(f"Conflito ao salvar patente: {e.diag.message_detail or e}")
        except Exception as e:
            self.conexao.rollback()
            logger.exception("Erro ao salvar patente")
            raise RuntimeError(f"Erro ao salvar patente: {e}")


    def atualizar_patente(self, patente: Patente) -> Dict:
        sql = (
            "UPDATE patente "
            "SET nome=%s, ano=%s, data_concessao=%s, id_pesquisador=%s "
            "WHERE id_patente=%s "
            "RETURNING id_patente, nome, ano, data_concessao, id_pesquisador"
        )
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql, (
                    patente.nome,
                    patente.ano,
                    patente.data_concessao,
                    patente.id_pesquisador,
                    patente.id_patente
                ))
                if cursor.rowcount == 0:
                    raise LookupError("Patente não encontrada para atualização.")
                colunas = [desc[0] for desc in cursor.description]
                linha = cursor.fetchone()
            self.conexao.commit()
            return dict(zip(colunas, linha))
        
        except LookupError:
            self.conexao.rollback()
            raise
        except Exception as e:
            self.conexao.rollback()
            logger.exception("Erro ao atualizar patente")
            raise RuntimeError(f"Erro ao atualizar patente: {e}")


    def apagar_patente(self, id_patente: str) -> None:
        sql = (
            "DELETE FROM patente "
            "WHERE id_patente=%s "
        )
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql, (id_patente,))
                if cursor.rowcount == 0:
                    raise LookupError("Patente não encontrada para exclusão.")
            self.conexao.commit()
        except LookupError:
            self.conexao.rollback()
            raise
        except Exception as e:
            self.conexao.rollback()
            logger.exception("Erro ao apagar patente")
            raise RuntimeError(f"Erro ao apagar patente: {e}")