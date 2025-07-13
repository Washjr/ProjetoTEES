from pydantic_settings import BaseSettings

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