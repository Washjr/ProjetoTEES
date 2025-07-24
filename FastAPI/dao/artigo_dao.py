import logging
from typing import List, Dict
from psycopg2 import IntegrityError

from banco.conexao_db import Conexao
from model.artigo import Artigo
from service.openalex import buscar_resumo_openalex

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
            "ORDER BY a.id_artigo"
        )
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql)
                linhas = cursor.fetchall()
            
            # Agrupar resultados por artigo para lidar com múltiplos autores
            artigos_dict = {}
            for linha in linhas:
                (id_artigo, title, journal, year, abstract, doi, qualis, 
                 author_id, author_name) = linha
                
                normalized_title = title.strip().lower()
                normalized_journal = journal.strip().lower() if journal else ""
                normalized_year = str(year).strip() if year else ""
                normalized_doi = (doi.strip().lower() if doi else "")

                key = f"{normalized_title}|{normalized_journal}|{normalized_year}|{normalized_doi}"

                if key  not in artigos_dict:
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
                
                # Adicionar autor se não existir
                author_exists = any(
                    author["id"] == str(author_id) 
                    for author in artigos_dict[key]["authors"]
                )
                if not author_exists:
                    artigos_dict[key ]["authors"].append({
                        "id": str(author_id),
                        "name": author_name
                    })
            
            return list(artigos_dict.values())

        except Exception as e:
            logger.exception("Erro ao listar artigos")
            raise RuntimeError(f"Erro ao listar artigos: {e}")


    def buscar_por_termo(self, termo: str) -> List[Dict]:
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
            "WHERE unaccent(lower(a.nome)) ILIKE unaccent(lower(%s)) "
            "OR unaccent(lower(a.resumo)) ILIKE unaccent(lower(%s)) "
            "ORDER BY a.id_artigo"
        )
        try:
            with self.conexao.cursor() as cursor:
                termo_formatado = f"%{termo.strip()}%"
                
                cursor.execute(sql, (termo_formatado, termo_formatado))
                linhas = cursor.fetchall()
            
            # Agrupar resultados por artigo para lidar com múltiplos autores
            artigos_dict = {}
            for linha in linhas:
                (id_artigo, title, journal, year, abstract, doi, qualis, 
                 author_id, author_name) = linha
                
                normalized_title = title.strip().lower()
                normalized_journal = journal.strip().lower() if journal else ""
                normalized_year = str(year).strip() if year else ""
                normalized_doi = (doi.strip().lower() if doi else "")

                key = f"{normalized_title}|{normalized_journal}|{normalized_year}|{normalized_doi}"

                if key  not in artigos_dict:
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
                
                # Adicionar autor se não existir
                author_exists = any(
                    author["id"] == str(author_id) 
                    for author in artigos_dict[key]["authors"]
                )
                if not author_exists:
                    artigos_dict[key ]["authors"].append({
                        "id": str(author_id),
                        "name": author_name
                    })
            
            return list(artigos_dict.values())
            
        except Exception as e:
            logger.exception(f"Erro ao buscar artigo pelo termo: '{termo}'")
            raise RuntimeError(f"Erro ao buscar artigo por termo: {e}")


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

    def buscar_com_filtros(self, filtros: List[Dict] = None) -> List[Dict]:
        """
        Busca artigos aplicando filtros dinâmicos.
        
        Args:
            filtros: Lista de filtros no formato [{"field": "year", "operator": ">=", "value": 2020}]
        
        Returns:
            Lista de artigos filtrados
        """
        # Query base
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
        )
        
        # Construir condições WHERE dinamicamente
        where_conditions = []
        params = []
        
        if filtros:
            for filtro in filtros:
                field = filtro["field"]
                operator = filtro["operator"]
                value = filtro["value"]
                
                if field == "year":
                    where_conditions.append(f"a.ano {operator} %s")
                    params.append(value)
                elif field == "qualis":
                    if operator in [">=", "<=", ">", "<"]:
                        # Para Qualis, usar hierarquia
                        hierarchy = ["A1", "A2", "B1", "B2", "B3", "B4", "C"]
                        try:
                            value_index = hierarchy.index(value)
                            if operator in [">=", "melhor"]:
                                valid_qualis = hierarchy[:value_index + 1]
                            elif operator in ["<=", "pior"]:
                                valid_qualis = hierarchy[value_index:]
                            else:
                                valid_qualis = [value]
                            
                            placeholders = ", ".join(["%s"] * len(valid_qualis))
                            where_conditions.append(f"per.qualis IN ({placeholders})")
                            params.extend(valid_qualis)
                        except ValueError:
                            # Se valor não encontrado na hierarquia, usar comparação simples
                            where_conditions.append("per.qualis = %s")
                            params.append(value)
                    else:
                        where_conditions.append("per.qualis = %s")
                        params.append(value)
                elif field == "journal":
                    if operator == "contains":
                        where_conditions.append("unaccent(lower(per.nome)) ILIKE unaccent(lower(%s))")
                        params.append(f"%{value}%")
                    else:
                        where_conditions.append("per.nome = %s")
                        params.append(value)
                elif field == "author_name":
                    if operator == "contains":
                        where_conditions.append("unaccent(lower(p.nome)) ILIKE unaccent(lower(%s))")
                        params.append(f"%{value}%")
                    else:
                        where_conditions.append("p.nome = %s")
                        params.append(value)
                elif field == "doi":
                    if operator == "contains":
                        where_conditions.append("lower(a.doi) ILIKE lower(%s)")
                        params.append(f"%{value}%")
                    else:
                        where_conditions.append("a.doi = %s")
                        params.append(value)
        
        # Adicionar WHERE se há condições
        if where_conditions:
            sql += "WHERE " + " AND ".join(where_conditions) + " "
        
        sql += "ORDER BY a.id_artigo"
        
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(sql, params)
                linhas = cursor.fetchall()
            
            # Agrupar resultados por artigo para lidar com múltiplos autores
            artigos_dict = {}
            for linha in linhas:
                (id_artigo, title, journal, year, abstract, doi, qualis, 
                 author_id, author_name) = linha
                
                normalized_title = title.strip().lower()
                normalized_journal = journal.strip().lower() if journal else ""
                normalized_year = str(year).strip() if year else ""
                normalized_doi = (doi.strip().lower() if doi else "")

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
                
                # Adicionar autor se não existir
                author_exists = any(
                    author["id"] == str(author_id) 
                    for author in artigos_dict[key]["authors"]
                )
                if not author_exists:
                    artigos_dict[key]["authors"].append({
                        "id": str(author_id),
                        "name": author_name
                    })
            
            return list(artigos_dict.values())

        except Exception as e:
            logger.exception("Erro ao buscar artigos com filtros")
            raise RuntimeError(f"Erro ao buscar artigos com filtros: {e}")