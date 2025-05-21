from util import *


class Nacionalidade(Enum):
    # Anglófonos
    USA = 10     # Estados Unidos
    UK = 11      # Reino Unido
    AUS = 12     # Austrália
    CAN = 13     # Canadá
    NZL = 14     # Nova Zelândia

    # Europa Ocidental
    GER = 18     # Alemanha
    NLD = 19     # Países Baixos
    SWE = 20     # Suécia
    FRA = 21     # França
    ITA = 22     # Itália
    ESP = 24     # Espanha
    POR = 25     # Portugal

    # Países latinos
    BRA = 26     # Brasil
    MEX = 27     # México

    # Ásia Oriental
    JPN = 30     # Japão
    KOR = 31     # Coreia do Sul
    CHN = 32     # China

    # Outros
    IND = 35     # Índia
    RUS = 40     # Rússia
    IRN = 45     # Irã
    KSA = 48     # Arábia Saudita


    def __str__(self):
        nomes = {
            Nacionalidade.USA: "Estados Unidos",
            Nacionalidade.UK: "Reino Unido",
            Nacionalidade.AUS: "Austrália",
            Nacionalidade.CAN: "Canadá",
            Nacionalidade.NZL: "Nova Zelândia",
            Nacionalidade.GER: "Alemanha",
            Nacionalidade.NLD: "Países Baixos",
            Nacionalidade.SWE: "Suécia",
            Nacionalidade.FRA: "França",
            Nacionalidade.ITA: "Itália",
            Nacionalidade.BRA: "Brasil",
            Nacionalidade.ESP: "Espanha",
            Nacionalidade.MEX: "México",
            Nacionalidade.JPN: "Japão",
            Nacionalidade.KOR: "Coreia do Sul",
            Nacionalidade.IND: "Índia",
            Nacionalidade.CHN: "China",
            Nacionalidade.RUS: "Rússia",
            Nacionalidade.IRN: "Irã",
            Nacionalidade.KSA: "Arábia Saudita",
            Nacionalidade.POR: "Portugal",
        }
        return f"{self.name}"
    

class Personalidade(Enum):
    LIDER = 10
    ESTRATEGISTA = 11
    DETERMINADO = 12
    TECNICO = 13
    CALMO = 14
    IMPULSIVO = 18
    REBELDE = 20

    def __str__(self):
        return self.name.capitalize()

class EstadoPiloto(Enum):
    ATIVO = auto()
    FERIDO = auto()
    DESCANSANDO = auto()
    INATIVO = auto()

    def __str__(self):
        return self.name.lower()


class Piloto:
    def __init__(self, nome, idade, inteligencia, nacionalidade: Nacionalidade = None,
                 personalidade: Personalidade = None, estado: EstadoPiloto = EstadoPiloto.ATIVO):
        self.__nome = nome
        self.__idade = idade

        self.__nacionalidade = nacionalidade

        self.__inteligencia = inteligencia

        self.__personalidade = personalidade

        self.estado = estado  # usa o setter
        self.__saude = 100

    @property
    def personalidade(self):
        return self.__personalidade

    @property
    def nacionalidade(self):
        return self.__nacionalidade
    
    @property
    def estado(self):
        return self.__estado

    @estado.setter
    def estado(self, novo_estado):
        if not isinstance(novo_estado, EstadoPiloto):
            raise ValueError(f"Estado deve ser do tipo EstadoPiloto, recebeu {type(novo_estado)}")
        self.__estado = novo_estado

    @property
    def nome(self):
        return self.__nome

    @property
    def idade(self):
        return self.__idade

    @property
    def nacionalidade(self):
        return self.__nacionalidade

    @property
    def inteligencia(self):
        return self.__inteligencia

    @property
    def saude(self):
        return self.__saude

    @saude.setter
    def saude(self, valor):
        if 0 <= valor <= 100:
            self.__saude = valor
        else:
            raise ValueError("Saúde deve estar entre 0 e 100")

    def info(self):
        return (
            f"Piloto: {self.__nome}\n"
            f"Idade: {self.__idade}\n"
            f"Nacionalidade: {self.__nacionalidade or 'N/A'}\n"
            f"Inteligência: {self.__inteligencia}\n"
            f"Personalidade: {self.__personalidade or 'N/A'}\n"
            f"Estado: {self.__estado}\n"
            f"Saúde: {self.__saude}"
        )

    def __str__(self):
        return self.__nome
