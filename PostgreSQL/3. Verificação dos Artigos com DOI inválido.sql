SELECT 
  a.nome, a.ano, a.doi, 
  p.nome
FROM artigo AS a
JOIN pesquisador AS p
  ON a.id_pesquisador = p.id_pesquisador
WHERE 
     a.doi = '10.1186/s12939-2023-01857-y'
 OR  a.doi = '10.9771/cp.v12i5 Especial.34453'
 OR  a.doi = '10.37118/ijdr.19134.06.2020'
 OR  a.doi = '10.9771/cp.v13i2%20COVID-19.36174'
 OR  a.doi = '10.9771/cp.v12i5%20Especial.32674'
 OR  a.doi = '10.22278/2318-2660.2021.v45.NEspecial_1.a32';