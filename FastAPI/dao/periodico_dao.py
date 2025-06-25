import logging
from typing import List, Dict
from psycopg2 import IntegrityError

from banco.conexao_db import Conexao
from model.periodico import Periodico

logger = logging.getLogger(__name__)

class PeriodicoDAO:
    """
    DAO para operações de CRUD em periódicos.
    Mantém uma conexão ao instanciar e devolve ao destruir.
    """
    def __init__(self):
        self.conexao = Conexao.obter_conexao()

    def __del__(self):
        Conexao.devolver_conexao(self.conexao)


    def listar_periodicos(self) -> List[Dict]:
        sql = "SELECT id_periodico, nome, qualis, issn FROM periodico"
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql)
                colunas = [desc[0] for desc in cursor.description]
                linhas = cursor.fetchall()
            return [dict(zip(colunas, linha)) for linha in linhas]

        except Exception as e:
            logger.exception("Erro ao listar periódicos")
            raise RuntimeError(f"Erro ao listar periódicos: {e}")


    def salvar_periodico(self, periodico: Periodico) -> Dict:
        sql = (
            "INSERT INTO periodico (nome, qualis, issn) "
            "VALUES (%s, %s, %s) "
            "RETURNING id_periodico, nome, qualis, issn "
        )
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql, (
                    periodico.nome,
                    periodico.qualis,
                    periodico.issn
                ))
                colunas = [desc[0] for desc in cursor.description]
                linha = cursor.fetchone()
            self.conexao.commit()
            return dict(zip(colunas, linha))

        except IntegrityError as e:
            self.conexao.rollback()
            raise ValueError(f"Conflito ao salvar periódico: {e.diag.message_detail or e}")
        except Exception as e:
            self.conexao.rollback()
            logger.exception("Erro ao salvar periódico")
            raise RuntimeError(f"Erro ao salvar periódico: {e}")


    def atualizar_periodico(self, periodico: Periodico) -> Dict:
        sql = (
            "UPDATE periodico SET nome=%s, qualis=%s, issn=%s "
            "WHERE id_periodico=%s "
            "RETURNING id_periodico, nome, qualis, issn "
        )
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql, (
                    periodico.nome,
                    periodico.qualis,
                    periodico.issn,
                    periodico.id_periodico
                ))
                if cursor.rowcount == 0:
                    raise LookupError("Periódico não encontrado para atualização.")
                colunas = [desc[0] for desc in cursor.description]
                linha = cursor.fetchone()
            self.conexao.commit()
            return dict(zip(colunas, linha))

        except LookupError:
            self.conexao.rollback()
            raise
        except Exception as e:
            self.conexao.rollback()
            logger.exception("Erro ao atualizar periódico")
            raise RuntimeError(f"Erro ao atualizar periódico: {e}")


    def apagar_periodico(self, id_periodico: str) -> None:
        sql = "DELETE FROM periodico WHERE id_periodico=%s"
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql, (id_periodico,))
                if cursor.rowcount == 0:
                    raise LookupError("Periódico não encontrado para exclusão.")
            self.conexao.commit()
        except LookupError:
            self.conexao.rollback()
            raise
        except Exception as e:
            self.conexao.rollback()
            logger.exception("Erro ao apagar periódico")
            raise RuntimeError(f"Erro ao apagar periódico: {e}")