import logging
from typing import List, Dict, Optional
from psycopg2 import IntegrityError

from model.mapper.artigo_dto_mapper import ArtigoDTOMapper
from banco.conexao_db import Conexao
from model.artigo import Artigo
from service.utils.openalex import buscar_resumo_openalex
from model.dto.artigo_busca_dto import ArtigoBuscaDTO

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

    def _executar_consulta_artigos(self, sql: str) -> Dict[str, Dict]:
        """
        Executa consulta SQL e agrupa resultados por artigo para lidar com múltiplos autores.
        
        Args:
            sql: Query SQL a ser executada
            
        Returns:
            Dicionário com artigos agrupados por chave única
        """
        try:
            logger.info(f"Executando SQL: {sql}")
            with self.conexao.cursor() as cursor:
                cursor.execute(sql)
                linhas = cursor.fetchall()
            
            artigos_dict = {}
            for linha in linhas:
                (id_artigo, title, journal, year, abstract, doi, qualis, 
                    author_id, authors) = linha
                
                normalized_title = title.strip().lower() if title else ""
                normalized_journal = journal.strip().lower() if journal else ""
                normalized_year = str(year).strip() if year else ""
                normalized_doi = doi.strip().lower() if doi else ""

                key = f"{normalized_title}|{normalized_journal}|{normalized_year}|{normalized_doi}"

                if key not in artigos_dict:
                    artigos_dict[key] = {
                        "id": str(id_artigo),
                        "title": title,
                        "journal": journal,
                        "year": year,
                        "abstract": abstract or "",
                        "doi": doi,
                        "qualis": qualis,
                        "authors": []
                    }
                
                if authors and not any(author == authors for author in artigos_dict[key]["authors"]):
                    artigos_dict[key]["authors"].append(authors)

            return artigos_dict
        except Exception as e:
            logger.exception("Erro ao executar consulta de artigos")
            raise RuntimeError(f"Erro ao executar consulta de artigos: {e}")
    
    def listar_artigos(self) -> List[ArtigoBuscaDTO]: 
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
            "p.nome as authors "
            "FROM artigo a "
            "JOIN periodico per ON a.id_periodico = per.id_periodico "
            "JOIN pesquisador p ON a.id_pesquisador = p.id_pesquisador "
            "ORDER BY a.id_artigo"
        )
        
        artigos_dict = self._executar_consulta_artigos(sql)
        return ArtigoDTOMapper.to_artigo_busca_dto_list_from_dict(artigos_dict)

    def buscar_por_termo(self, termo: str, filtro: Optional[str] = None) -> List[ArtigoBuscaDTO]:
        termo_formatado = f"%{termo.strip()}%"
        
        sql = (
            "WITH base AS ("
            "    SELECT "
            "        a.id_artigo as id, "
            "        a.nome as title, "
            "        per.nome as journal, "
            "        a.ano as year, "
            "        a.resumo as abstract, "
            "        a.doi, "
            "        per.qualis, "
            "        p.id_pesquisador as author_id, "
            "        p.nome as authors "
            "    FROM artigo a "
            "    JOIN periodico per ON a.id_periodico = per.id_periodico "
            "    JOIN pesquisador p ON a.id_pesquisador = p.id_pesquisador "
            ") "
            f"SELECT * FROM base "
            f"WHERE ((unaccent(lower(title)) ILIKE unaccent(lower('{termo_formatado}')) "
            f"   OR unaccent(lower(abstract)) ILIKE unaccent(lower('{termo_formatado}')))) "
        )

        if filtro:
            sql += f" AND ({filtro})"

        sql += " ORDER BY year DESC, title ASC"

        artigos_dict = self._executar_consulta_artigos(sql)
        return ArtigoDTOMapper.to_artigo_busca_dto_list_from_dict(artigos_dict)

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
    
    def sincronizar_resumos(self) -> None:
        """
        Atualiza os campos de resumo dos artigos com DOI nulo, 
        consultando a API do OpenAlex.
        """
        sql_consulta = """
            SELECT id_artigo, doi 
            FROM artigo 
            WHERE doi IS NOT NULL AND resumo_sincronizado = FALSE
        """
        sql_atualizacao = """
            UPDATE artigo 
            SET resumo = %s, resumo_sincronizado = TRUE
            WHERE id_artigo = %s
        """
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql_consulta)
                artigos = cursor.fetchall()

            logger.info(f"{len(artigos)} artigos sem resumo sincronizado encontrados.")

            for id_artigo, doi in artigos:
                try:
                    resumo = buscar_resumo_openalex(doi)
                except Exception:
                    resumo = None
                    logger.exception(f"Erro ao buscar resumo do DOI {doi}")

                try:
                    with self.conexao.cursor() as cursor:
                        cursor.execute(sql_atualizacao, (resumo, id_artigo))
                        self.conexao.commit()
                    if resumo:
                        logger.info(f"Resumo atualizado com sucesso para o artigo {id_artigo}")
                    else:
                        logger.info(f"Marcação de `resumo_sincronizado` para o artigo {id_artigo} (sem resumo)")

                except Exception:
                    self.conexao.rollback()
                    logger.exception(f"Erro ao atualizar resumo do artigo {id_artigo}")
        except Exception as e:
            logger.exception("Erro ao sincronizar resumos dos artigos")
            raise RuntimeError(f"Erro ao sincronizar resumos: {e}")

    def listar_artigos_com_embeddings(self) -> List[ArtigoBuscaDTO]:
        """
        Lista artigos que possuem embeddings na coluna embedding.
        
        Returns:
            Lista de objetos ArtigoBuscaDTO com dados dos artigos que possuem embeddings
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
            "p.nome as authors "
            "FROM artigo a "
            "JOIN periodico per ON a.id_periodico = per.id_periodico "
            "JOIN pesquisador p ON a.id_pesquisador = p.id_pesquisador "
            "WHERE a.embedding IS NOT NULL "
            "ORDER BY a.id_artigo"
        )
        
        artigos_dict = self._executar_consulta_artigos(sql)
        artigos_dto = ArtigoDTOMapper.to_artigo_busca_dto_list_from_dict(artigos_dict)
        
        logger.info(f"Encontrados {len(artigos_dto)} artigos com embeddings")
        return artigos_dto