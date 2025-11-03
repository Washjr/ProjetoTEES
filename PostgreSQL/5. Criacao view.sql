CREATE OR REPLACE VIEW vw_artigos_completos AS
SELECT
    a.id_artigo as id,
    a.nome as title,
    per.nome as journal,
    a.ano as year,
    a.resumo as abstract,
    a.doi,
    per.qualis,
    p.id_pesquisador as author_id,
    p.nome as authors,
    a.embedding  -- Importante: inclua o embedding na view
FROM artigo a
JOIN periodico per ON a.id_periodico = per.id_periodico
JOIN pesquisador p ON a.id_pesquisador = p.id_pesquisador;