import logging
from typing import List, Dict
from psycopg2 import IntegrityError

from banco.conexao_db import Conexao
from model.instituicao import Instituicao

logger = logging.getLogger(__name__)

class InstituicaoDAO:
    """
    DAO para operações de CRUD em instituições.
    Mantém uma conexão ao instanciar e devolve ao destruir.
    """
    def __init__(self):
        self.conexao = Conexao.obter_conexao()

    def __del__(self):
        Conexao.devolver_conexao(self.conexao)


    def listar_instituicoes(self) -> List[Dict]: 
        sql = "SELECT id_instituicao, nome FROM instituicao"
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql)
                colunas = [desc[0] for desc in cursor.description]
                linhas = cursor.fetchall()
            return [dict(zip(colunas, linha)) for linha in linhas]

        except Exception as e:
            logger.exception("Erro ao listar instituições")
            raise RuntimeError(f"Erro ao listar instituições: {e}")


    def salvar_instituicao(self, instituicao: Instituicao) -> Dict:
        sql = (
            "INSERT INTO instituicao (nome) VALUES (%s) "
            "RETURNING id_instituicao, nome"
        )
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql, (instituicao.nome,))
                colunas = [desc[0] for desc in cursor.description]
                linha = cursor.fetchone()
            self.conexao.commit()
            return dict(zip(colunas, linha))

        except IntegrityError as e:
            self.conexao.rollback()
            raise ValueError(f"Conflito ao salvar instituição: {e.diag.message_detail or e}")
        except Exception as e:
            self.conexao.rollback()
            logger.exception("Erro ao salvar instituição")
            raise RuntimeError(f"Erro ao salvar instituição: {e}")


    def atualizar_instituicao(self, instituicao: Instituicao) -> Dict:
        sql = (
            "UPDATE instituicao SET nome=%s "
            "WHERE id_instituicao=%s "
            "RETURNING id_instituicao, nome"
        )        
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql, (instituicao.nome, instituicao.id_instituicao))
                if cursor.rowcount == 0:
                    raise LookupError("Instituição não encontrada para atualização.")
                colunas = [desc[0] for desc in cursor.description]
                linha = cursor.fetchone()
            self.conexao.commit()
            return dict(zip(colunas, linha))

        except LookupError:
            self.conexao.rollback()
            raise
        except Exception as e:
            self.conexao.rollback()
            logger.exception("Erro ao atualizar instituição")
            raise RuntimeError(f"Erro ao atualizar instituição: {e}")


    def apagar_instituicao(self, id_instituicao: str) -> None:
        sql = (
            "DELETE FROM instituicao "
            "WHERE id_instituicao=%s "
        )        
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql, (id_instituicao,))
                if cursor.rowcount == 0:                    
                    raise LookupError("Instituição não encontrada para exclusão.")
            self.conexao.commit()

        except LookupError:
            self.conexao.rollback()
            raise
        except Exception as e:
            self.conexao.rollback()
            logger.exception("Erro ao apagar instituição")
            raise RuntimeError(f"Erro ao apagar instituição: {e}")