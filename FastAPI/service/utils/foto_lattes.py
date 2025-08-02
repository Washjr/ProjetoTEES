from http import HTTPStatus
from pathlib import Path
from typing import Optional 

import httpx
import logging
import requests

logger = logging.getLogger(__name__)


def buscar_codigo_lattes(id_lattes: str) -> Optional[str]:
    """
    Busca o “código K” no serviço buscatextual.cnpq.br, a partir do id_lattes.

    Retorna o código de 10 caracteres (K...) ou None se não encontrar.
    """
    url = f'https://buscatextual.cnpq.br/buscatextual/cv?id={id_lattes}'
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/125.0.0.0 Safari/537.36'
        )
    }

    try:
        with httpx.Client(follow_redirects=False, headers=headers) as client:
            resposta = client.get(url, timeout=30.0)
    except Exception as e:
        logger.error(f"Falha na requisição para buscar código K com o id_lattes {id_lattes}: {e}")
        return None

    if resposta.status_code == HTTPStatus.FOUND:
        codigo = resposta.headers.get("Location", "")[-10:]
        logger.info(f"Código K encontrado para {id_lattes}: {codigo}")
        return codigo
        
    logger.warning(f"Código K não encontrado para {id_lattes} (status {resposta.status_code})")
    return None


def baixar_foto_pesquisador(codigo_k: str, id_lattes: str) -> bool:
    """
    Baixa a foto do pesquisador a partir do código K e
    salva em imagens/pesquisadores/{id_lattes}.jpg.

    Retorna True se conseguiu salvar (status 200), False caso contrário.
    Em caso de falha, tenta novamente uma vez antes de desistir.
    """
    
    url = f"http://servicosweb.cnpq.br/wspessoa/servletrecuperafoto?tipo=1&id={codigo_k}"
    max_tentativas = 2

    for tentativa in range(1, max_tentativas + 1):
        try:
            resposta = requests.get(url, timeout=10)
        except Exception as e:           
            logger.error(f"Erro na tentativa {tentativa} ao baixar foto K={codigo_k}: {e}")
            if tentativa == max_tentativas:
                return False
            continue

        if resposta.status_code != HTTPStatus.OK:
            logger.warning(
                f"Falha na tentativa {tentativa} ao baixar foto (K={codigo_k}): "
                f"status {resposta.status_code}"
            )
            if tentativa == max_tentativas:
                return False
            continue

        destino = Path(__file__).parents[1] / "imagens" / "pesquisadores"
        destino.mkdir(parents=True, exist_ok=True)
        arquivo = destino / f"{id_lattes}.jpg"

        try:
            arquivo.write_bytes(resposta.content)
            logger.info(f"Imagem salva em {arquivo}")
            return True
        except Exception as e:
            logger.error(
                f"Erro ao salvar foto na tentativa {tentativa} para {id_lattes}: {e}"
            )
            if tentativa == max_tentativas:
                return False
        
    return False


if __name__ == "__main__":
    teste_lattes = "7401907691814937"
    logger.info(f"Iniciando busca de código K para Lattes {teste_lattes}")
    codigo = buscar_codigo_lattes(teste_lattes)

    if not codigo:
        print(f"Código K não encontrado para {teste_lattes}")
    else:
        sucesso = baixar_foto_pesquisador(codigo, teste_lattes)
        if sucesso:
            print(f"Foto do pesquisador {teste_lattes} baixada com sucesso.")
        else:
            print(f"Falha ao baixar foto para {teste_lattes}.")