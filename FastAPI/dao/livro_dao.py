import logging
from typing import List, Dict
from psycopg2 import IntegrityError

from banco.conexao_db import Conexao
from model.livro import Livro

logger = logging.getLogger(__name__)

class LivroDAO:
    """
    DAO para operações de CRUD em livros.
    Mantém uma conexão ao instanciar e devolve ao destruir.
    """
    def __init__(self):
        self.conexao = Conexao.obter_conexao()

    def __del__(self):
        Conexao.devolver_conexao(self.conexao)

    def listar_livros(self) -> List[Dict]:
        sql = "SELECT id_livro, nome_livro, ano, nome_editora, isbn, id_pesquisador FROM livro"
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql)
                colunas = [desc[0] for desc in cursor.description]
                linhas = cursor.fetchall()
            return [dict(zip(colunas, linha)) for linha in linhas]
        
        except Exception as e:
            logger.exception("Erro ao listar livros")
            raise RuntimeError(f"Erro ao listar livros: {e}")


    def salvar_livro(self, livro: Livro) -> Dict:
        sql = (
            "INSERT INTO livro (nome_livro, ano, nome_editora, isbn, id_pesquisador) "
            "VALUES (%s, %s, %s, %s, %s) "
            "RETURNING id_livro, nome_livro, ano, nome_editora, isbn, id_pesquisador"
        )
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql, (
                    livro.nome_livro,
                    livro.ano,
                    livro.nome_editora,
                    livro.isbn,
                    livro.id_pesquisador
                ))
                colunas = [desc[0] for desc in cursor.description]
                linha = cursor.fetchone()
            self.conexao.commit()
            return dict(zip(colunas, linha))
        
        except IntegrityError as e:
            self.conexao.rollback()
            raise ValueError(f"Conflito ao salvar livro: {e.diag.message_detail or e}")
        except Exception as e:
            self.conexao.rollback()
            logger.exception("Erro ao salvar livro")
            raise RuntimeError(f"Erro ao salvar livro: {e}")


    def atualizar_livro(self, livro: Livro) -> Dict:
        sql = (
            "UPDATE livro "
            "SET nome_livro=%s, ano=%s, nome_editora=%s, isbn=%s, id_pesquisador=%s "
            "WHERE id_livro=%s "
            "RETURNING id_livro, nome_livro, ano, nome_editora, isbn, id_pesquisador"
        )
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql, (
                    livro.nome_livro,
                    livro.ano,
                    livro.nome_editora,
                    livro.isbn,
                    livro.id_pesquisador,
                    livro.id_livro
                ))
                if cursor.rowcount == 0:
                    raise LookupError("Livro não encontrado para atualização.")
                colunas = [desc[0] for desc in cursor.description]
                linha = cursor.fetchone()
            self.conexao.commit()
            return dict(zip(colunas, linha))
        
        except LookupError:
            self.conexao.rollback()
            raise
        except Exception as e:
            self.conexao.rollback()
            logger.exception("Erro ao atualizar livro")
            raise RuntimeError(f"Erro ao atualizar livro: {e}")


    def apagar_livro(self, id_livro: str) -> None:
        sql = (
            "DELETE FROM livro "
            "WHERE id_livro=%s "
        )
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql, (id_livro,))
                if cursor.rowcount == 0:
                    raise LookupError("Livro não encontrado para exclusão.")
            self.conexao.commit()

        except LookupError:
            self.conexao.rollback()
            raise
        except Exception as e:
            self.conexao.rollback()
            logger.exception("Erro ao apagar livro")
            raise RuntimeError(f"Erro ao apagar livro: {e}")