import logging
from typing import List, Dict, Optional
from psycopg2.extras import RealDictCursor

from model.mapper.artigo_dto_mapper import ArtigoDTOMapper
from banco.conexao_db import Conexao
from model.artigo import Artigo
from service.utils.openalex import buscar_resumo_openalex
from model.dto.artigo_busca_dto import ArtigoBuscaDTO

logger = logging.getLogger(__name__)

class ArtigoDAO:
    """
    DAO para operações de CRUD em artigos.
    Usa context managers para gerenciar conexões de forma segura.
    """
    
    def __init__(self):
        # Não mantém conexão persistente para evitar esgotamento do pool
        pass

    def _obter_conexao(self):
        """Context manager para obter e devolver conexão automaticamente"""
        class ConexaoContext:
            def __init__(self):
                self.conexao = None
                
            def __enter__(self):
                self.conexao = Conexao.obter_conexao()
                return self.conexao
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                if self.conexao:
                    Conexao.devolver_conexao(self.conexao)
                    
        return ConexaoContext()

    def _executar_consulta_artigos(self, sql: str) -> List[ArtigoBuscaDTO]:
        """
        Executa consulta SQL e agrupa resultados por artigo para lidar com múltiplos autores.
        
        Args:
            sql: Query SQL a ser executada
            
        Returns:
            Dicionário com artigos agrupados por chave única
        """
        try:
            logger.info(f"Executando SQL: {sql}")
            with self._obter_conexao() as conexao:
                with conexao.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(sql)
                    linhas = cursor.fetchall()
            
            return ArtigoDTOMapper.to_artigo_busca_dto_from_sql_rows(linhas)
        except Exception as e:
            logger.exception("Erro ao executar consulta de artigos")
            raise RuntimeError(f"Erro ao executar consulta de artigos: {e}")
    
    def listar_artigos(self) -> List[ArtigoBuscaDTO]: 
        sql = (
            "SELECT * FROM vw_artigos_completos "
            "ORDER BY id"
        )
        
        return self._executar_consulta_artigos(sql)

    def buscar_por_termo(self, termo: str, filtro: Optional[str] = None) -> List[ArtigoBuscaDTO]:
        termo_formatado = f"%{termo.strip()}%"
        
        sql = (
            f"SELECT * FROM vw_artigos_completos "
            f"WHERE ((unaccent(lower(title)) ILIKE unaccent(lower('{termo_formatado}')) "
            f"   OR unaccent(lower(abstract)) ILIKE unaccent(lower('{termo_formatado}')))) "
        )

        if filtro:
            sql += f" AND ({filtro})"

        sql += " ORDER BY year DESC, title ASC"

        return self._executar_consulta_artigos(sql)
        
    def atualizar_artigo(self, artigo: Artigo) -> Dict:
        sql = (
            "UPDATE artigo "
            "SET nome=%s, ano=%s, doi=%s, id_pesquisador=%s, id_periodico=%s "
            "WHERE id_artigo=%s "
            "RETURNING id_artigo, nome, ano, doi, id_pesquisador, id_periodico "
        )
        try:
            with self._obter_conexao() as conexao:
                with conexao.cursor() as cursor:
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
                conexao.commit() 
            return dict(zip(colunas, linha))   
        
        except LookupError:
            raise
        except Exception as e:
            logger.exception("Erro ao atualizar artigo")
            raise RuntimeError(f"Erro ao atualizar artigo: {e}")
        
    def apagar_artigo(self, id_artigo: str) -> None:
        sql = (
            "DELETE FROM artigo "
            "WHERE id_artigo=%s "
        )
        try:        
            with self._obter_conexao() as conexao:
                with conexao.cursor() as cursor:            
                    cursor.execute(sql, (id_artigo,))            
                    if cursor.rowcount == 0:
                        raise LookupError("Artigo não encontrado para exclusão.")
                conexao.commit()
            
        except LookupError:
            raise
        except Exception as e:        
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
            with self._obter_conexao() as conexao:
                with conexao.cursor() as cursor:
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
                        with conexao.cursor() as cursor:
                            cursor.execute(sql_atualizacao, (resumo, id_artigo))
                            conexao.commit()
                        if resumo:
                            logger.info(f"Resumo atualizado com sucesso para o artigo {id_artigo}")
                        else:
                            logger.info(f"Marcação de `resumo_sincronizado` para o artigo {id_artigo} (sem resumo)")

                    except Exception:
                        conexao.rollback()
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
            "SELECT * FROM vw_artigos_completos "
            "WHERE embedding IS NOT NULL "
            "ORDER BY id"
        )
        
        artigos_dto = self._executar_consulta_artigos(sql)        
        logger.info(f"Encontrados {len(artigos_dto)} artigos com embeddings")
        return artigos_dto

    def buscar_artigos_similares(
        self,
        query_embedding: List[float],
        limit: int = 10,
        threshold: float = 0.3,
        filtro: Optional[str] = None,
    ) -> List[ArtigoBuscaDTO]:
        """
        Busca artigos similares usando similaridade por cosseno com PGVector.
        
        Args:
            query_embedding: Embedding da consulta
            limit: Número máximo de resultados
            threshold: Limite mínimo de similaridade
            filtro: Filtro SQL adicional opcional
            
        Returns:
            Lista de artigos similares ordenados por similaridade
        """
        try:
            with self._obter_conexao() as conexao:
                with conexao.cursor(cursor_factory=RealDictCursor) as cursor:
                    embedding_str = str(query_embedding)
                    
                    base_query = (
                        "SELECT "
                        "    *, "
                        f"    (1 - (embedding <=> '{embedding_str}'::vector)) AS similarity_score "
                        "FROM vw_artigos_completos "
                        "WHERE embedding IS NOT NULL "
                        f"    AND (1 - (embedding <=> '{embedding_str}'::vector)) >= {threshold} "
                    )

                    if filtro:
                        base_query += f"AND ({filtro}) "

                    base_query += f"ORDER BY similarity_score DESC LIMIT {limit}"

                    logger.info(f"Executando busca por similaridade com threshold: {threshold}, limit: {limit}")
                    cursor.execute(base_query)
                    results = cursor.fetchall()
                    logger.info(f"Resultados encontrados: {len(results)}")
                    
                    return ArtigoDTOMapper.to_artigo_busca_dto_from_sql_rows(results)

        except Exception as e:
            logger.exception("Erro na busca por similaridade")
            raise RuntimeError(f"Erro na busca por similaridade: {e}")

    def atualizar_embedding_artigo(self, id_artigo: int, embedding: List[float]) -> bool:
        """
        Atualiza o embedding de um artigo específico.
        
        Args:
            id_artigo: ID do artigo
            embedding: Vetor de embedding
            
        Returns:
            True se a atualização foi bem-sucedida
        """
        try:
            with self._obter_conexao() as conexao:
                with conexao.cursor() as cursor:
                    cursor.execute(
                        "UPDATE artigo SET embedding = %s WHERE id_artigo = %s",
                        (embedding, id_artigo),
                    )
                    conexao.commit()
                    sucesso = cursor.rowcount > 0
                    if sucesso:
                        logger.info(f"Embedding atualizado para o artigo {id_artigo}")
                    else:
                        logger.warning(f"Nenhum artigo encontrado com ID {id_artigo}")
                    return sucesso

        except Exception as e:
            logger.exception(f"Erro ao atualizar embedding do artigo {id_artigo}")
            raise RuntimeError(f"Erro ao atualizar embedding: {e}")

    def listar_artigos_sem_embeddings(self) -> List[Dict]:
        """
        Lista artigos que não possuem embeddings.
        
        Returns:
            Lista de dicionários com dados dos artigos sem embeddings
        """
        try:
            with self._obter_conexao() as conexao:
                with conexao.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT id_artigo, nome, resumo 
                        FROM artigo 
                        WHERE embedding IS NULL 
                            AND nome IS NOT NULL
                    """)
                    results = cursor.fetchall()
                    logger.info(f"Encontrados {len(results)} artigos sem embeddings")
                    return [dict(row) for row in results]

        except Exception as e:
            logger.exception("Erro ao listar artigos sem embeddings")
            raise RuntimeError(f"Erro ao listar artigos sem embeddings: {e}")

    def obter_estatisticas_embeddings(self) -> Dict[str, int]:
        """
        Retorna estatísticas sobre embeddings armazenados.
        
        Returns:
            Dicionário com contadores de artigos com/sem embeddings
        """
        try:
            with self._obter_conexao() as conexao:
                with conexao.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_artigos,
                            COUNT(embedding) as artigos_com_embeddings,
                            COUNT(*) - COUNT(embedding) as artigos_sem_embeddings
                        FROM artigo
                    """)

                    result = cursor.fetchone()
                    stats = dict(result) if result else {}
                    logger.info(f"Estatísticas de embeddings: {stats}")
                    return stats

        except Exception as e:
            logger.exception("Erro ao obter estatísticas de embeddings")
            raise RuntimeError(f"Erro ao obter estatísticas: {e}")