import psycopg2
from psycopg2 import OperationalError

class Conexao:
    _instancia_bd = None  # Atributo de classe para armazenar a instância única da conexão

    def __new__(cls, *args, **kwargs):
        # Cria uma nova instância da classe se ainda não existir
        if cls._instancia_bd is None:
            cls._instancia_bd = super(Conexao, cls).__new__(cls)
        return cls._instancia_bd

    def __init__(
        self,
        host: str = "localhost",      # Endereço do servidor de banco de dados
        database: str = "BD_PROJETO",   # Nome do banco de dados
        user: str = "postgres",       # Nome de usuário para autenticação no banco de dados
        password: str = "1234",       # Senha para autenticação no banco de dados
        port: int = 5445,             # Porta do servidor de banco de dados
    ):
        # Inicializa a conexão apenas uma vez
        if not hasattr(self, "__inicializado"):
            self.__host = host
            self.__database = database
            self.__user = user
            self.__password = password
            self.__port = port
            self.__conexao = None
            self.__inicializado = True
            print("Classe Conexao inicializada!")  # Mensagem de debug para verificar a inicialização

    def conectar_ao_banco(self):
        # Conecta ao banco de dados se a conexão ainda não estiver estabelecida
        if self.__conexao is None:
            try:
                # Estabelece a conexão com o banco de dados usando psycopg2
                self.__conexao = psycopg2.connect(
                    host=self.__host,
                    database=self.__database,
                    user=self.__user,
                    password=self.__password,
                    port=self.__port
                )

                print("Conexão estabelecida!")  # Mensagem de sucesso na conexão

            except OperationalError as erro:
                # Mensagem de erro se a conexão falhar
                print(f"Erro ao conectar ao banco: {erro}")

    def get_conexao(self):
        # Retorna a conexão estabelecida, criando-a se necessário
        if self.__conexao is None:
            self.conectar_ao_banco()
        return self.__conexao

