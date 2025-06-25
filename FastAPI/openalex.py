import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

def buscar_resumo_openalex(doi: str) -> Optional[str]:
    url = f"https://api.openalex.org/works/https://doi.org/{doi}"

    try:
        resposta = requests.get(url, timeout=10)
        resposta.raise_for_status()
        dados = resposta.json()
        indice_invertido = dados.get("abstract_inverted_index")

        if indice_invertido is None:
            logger.warning(f"Resumo do artigo não encontrado no OpenAlex: {doi}")
            return None

        # Reconstrução do resumo a partir do índice invertido
        tamanho_resumo = max(posicao for posicoes in indice_invertido.values() for posicao in posicoes)
        palavras = [''] * (tamanho_resumo + 1)

        for palavra, posicoes in indice_invertido.items():
            for posicao in posicoes:
                palavras[posicao] = palavra

        return ' '.join(palavras)

    except requests.exceptions.HTTPError as erro_http:
        if erro_http.response.status_code == 404:
            logger.warning(f"DOI não encontrado no OpenAlex: {doi}")
        else:
            logger.error(f"Erro HTTP ao buscar DOI {doi}: {erro_http}")
    except Exception as erro:
        logger.error(f"Erro inesperado ao buscar DOI {doi}: {erro}")
    return None