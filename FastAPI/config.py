from pydantic_settings import BaseSettings
import os

class Configuracoes(BaseSettings):
    # Banco de dados
    DB_HOST: str
    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    DB_PORT: int = 5445
    DB_MIN_CONEXOES: int = 1
    DB_MAX_CONEXOES: int = 10

    # OpenAI / LangChain
    OPENAI_API_KEY: str
    
    # Servidor
    BASE_URL: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Instância única para toda a aplicação
configuracoes = Configuracoes()
configuracoes.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY_IKEDA")

# Verificação de debug
print(f"Arquivo .env existe: {os.path.exists('.env')}")
print(f"Diretório atual: {os.getcwd()}")
print(f"Valor da API Key (primeiros 10 chars): {configuracoes.OPENAI_API_KEY[:14]}...")
print("Configurações carregadas com sucesso!")