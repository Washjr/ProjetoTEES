import logging
from typing import List, Dict
from psycopg2 import IntegrityError

from banco.conexao_db import Conexao
from model.software import Software

logger = logging.getLogger(__name__)

class SoftwareDAO:
    """
    DAO para operações de CRUD em softwares.
    Mantém uma conexão ao instanciar e devolve ao destruir.
    """
    def __init__(self):
        self.conexao = Conexao.obter_conexao()

    def __del__(self):
        Conexao.devolver_conexao(self.conexao)


    def listar_softwares(self) -> List[Dict]:
        sql = (
            "SELECT id_software, nome, ano, plataforma, finalidade, id_pesquisador "
            "FROM software"
        )
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql)
                colunas = [desc[0] for desc in cursor.description]
                linhas = cursor.fetchall()
            return [dict(zip(colunas, linha)) for linha in linhas]
        
        except Exception as e:
            logger.exception("Erro ao listar softwares")
            raise RuntimeError(f"Erro ao listar softwares: {e}")


    def salvar_software(self, software: Software) -> Dict:
        sql = (
            "INSERT INTO software (nome, ano, plataforma, finalidade, id_pesquisador) "
            "VALUES (%s, %s, %s, %s, %s) "
            "RETURNING id_software, nome, ano, plataforma, finalidade, id_pesquisador"
        )
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql, (
                    software.nome,
                    software.ano,
                    software.plataforma,
                    software.finalidade,
                    software.id_pesquisador
                ))
                colunas = [desc[0] for desc in cursor.description]
                linha = cursor.fetchone()
            self.conexao.commit()
            return dict(zip(colunas, linha))
        
        except IntegrityError as e:
            self.conexao.rollback()
            raise ValueError(f"Conflito ao salvar software: {e.diag.message_detail or e}")
        except Exception as e:
            self.conexao.rollback()
            logger.exception("Erro ao salvar software")
            raise RuntimeError(f"Erro ao salvar software: {e}")


    def atualizar_software(self, software: Software) -> Dict:
        sql = (
            "UPDATE software "
            "SET nome=%s, ano=%s, plataforma=%s, finalidade=%s, id_pesquisador=%s "
            "WHERE id_software=%s "
            "RETURNING id_software, nome, ano, plataforma, finalidade, id_pesquisador"
        )
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql, (
                    software.nome,
                    software.ano,
                    software.plataforma,
                    software.finalidade,
                    software.id_pesquisador,
                    software.id_software
                ))
                if cursor.rowcount == 0:
                    raise LookupError("Software não encontrado para atualização.")
                colunas = [desc[0] for desc in cursor.description]
                linha = cursor.fetchone()
            self.conexao.commit()
            return dict(zip(colunas, linha))
        
        except LookupError:
            self.conexao.rollback()
            raise
        except Exception as e:
            self.conexao.rollback()
            logger.exception("Erro ao atualizar software")
            raise RuntimeError(f"Erro ao atualizar software: {e}")


    def apagar_software(self, id_software: str) -> None:
        sql = (
            "DELETE FROM software "
            "WHERE id_software=%s "
        )
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql, (id_software,))
                if cursor.rowcount == 0:
                    raise LookupError("Software não encontrado para exclusão.")
            self.conexao.commit()
        except LookupError:
            self.conexao.rollback()
            raise
        except Exception as e:
            self.conexao.rollback()
            logger.exception("Erro ao apagar software")
            raise RuntimeError(f"Erro ao apagar software: {e}")