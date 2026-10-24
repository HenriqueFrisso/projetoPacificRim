from util import *
from uuid import uuid4


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

RECUPERACAO_BASE_POR_DIA = 0.4  # pontos de saúde por dia
XP_POR_NIVEL = 100
INTELIGENCIA_POR_NIVEL = 4
INTELIGENCIA_MAXIMA = 130

# Temperamento influencia o repouso: os calmos se recuperam melhor que os impulsivos.
RECUPERACAO_POR_PERSONALIDADE = {
    Personalidade.CALMO: 1.5,
    Personalidade.DETERMINADO: 1.3,
    Personalidade.ESTRATEGISTA: 1.2,
    Personalidade.TECNICO: 1.1,
    Personalidade.LIDER: 1.0,
    Personalidade.IMPULSIVO: 0.7,
    Personalidade.REBELDE: 0.6,
}


class EstadoPiloto(Enum):
    ATIVO = 0
    FERIDO = 1
    DESCANSANDO = 2
    INATIVO = 3

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

        self.estado = estado
        self.__saude = 100
        self._jaeger = None
        self.id = uuid4().hex  # nomes podem se repetir; o vínculo usa o id do parceiro
        self.experiencia = 0
        self.vinculos = {}  # id do parceiro -> {"nome": ..., "batalhas": ...}
        self.lendario = False  # tripulação original de um Jaeger do filme

    @property
    def rotulo(self):
        """Nome com ★ para os pilotos lendários (saves antigos não têm o atributo)."""
        return f"★ {self.__nome}" if getattr(self, "lendario", False) else self.__nome

    @property
    def nivel(self):
        return 1 + self.experiencia // XP_POR_NIVEL

    def ganhar_experiencia(self, pontos):
        """Soma experiência; cada nível novo aumenta a inteligência. Retorna os níveis ganhos."""
        nivel_anterior = self.nivel
        self.experiencia += pontos
        niveis = self.nivel - nivel_anterior
        self.__inteligencia = min(INTELIGENCIA_MAXIMA,
                                  self.__inteligencia + niveis * INTELIGENCIA_POR_NIVEL)
        return niveis

    def registrar_batalha(self, tripulacao):
        """Fortalece o vínculo com cada parceiro que lutou na mesma batalha."""
        for parceiro in tripulacao:
            if parceiro is not self:
                vinculo = self.vinculos.setdefault(parceiro.id, {"nome": parceiro.nome, "batalhas": 0})
                vinculo["batalhas"] += 1

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
        novo_estado = EstadoPiloto(novo_estado) if not isinstance(novo_estado, EstadoPiloto) else novo_estado
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
        self.__saude = valor
        if self.__saude <= 0:
            self.__saude = 0
            self.estado = EstadoPiloto.INATIVO
        elif self.__saude >= 100:
            self.__saude = 100
            self.estado = EstadoPiloto.ATIVO
        else:
            self.estado = EstadoPiloto.FERIDO

    def recuperar(self, dias):
        """Cura feridos com o passar dos dias; retorna os pontos recuperados."""
        if not 0 < self.__saude < 100:  # saudável ou fora de combate (saúde 0)
            return 0
        taxa = RECUPERACAO_POR_PERSONALIDADE.get(self.__personalidade, 1.0)
        pontos = min(round(dias * RECUPERACAO_BASE_POR_DIA * taxa), 100 - self.__saude)
        self.saude = self.__saude + pontos
        return pontos


    @property
    def jaeger(self):
        return self._jaeger

    @jaeger.setter
    def jaeger(self, novo_jaeger):
        self._jaeger = novo_jaeger



    def info(self):
        jaeger_nome = self._jaeger.nome if self._jaeger else "Nenhum"
        vinculos = ", ".join(f"{v['nome']} ({v['batalhas']} batalhas)"
                             for v in self.vinculos.values()) or "nenhum"
        return (
            f"Piloto: {self.rotulo}\n"
            f"Idade: {self.__idade}\n"
            f"Nacionalidade: {self.__nacionalidade or 'N/A'}\n"
            f"Inteligência: {self.__inteligencia}\n"
            f"Personalidade: {self.__personalidade or 'N/A'}\n"
            f"Estado: {self.__estado}\n"
            f"Saúde: {self.__saude}\n"
            f"Recuperação: x{RECUPERACAO_POR_PERSONALIDADE.get(self.__personalidade, 1.0)}\n"
            f"Nível: {self.nivel} ({self.experiencia % XP_POR_NIVEL}/{XP_POR_NIVEL} XP)\n"
            f"Vínculos: {vinculos}\n"
            f"Jaeger: {jaeger_nome}"
        )

    def __str__(self):
        return f"{self.__nome}"



def selecionar_pilotos(i, parceiro=None):
    """Escolhe i pilotos livres; com uma dupla formada, mostra a ponte neural prevista."""
    # Filtra pilotos que não têm jaeger e estão ATIVO ou FERIDO
    pilotos_disponiveis = [
        p for p in RepositorioPilotos.listar() 
        if p.jaeger is None and p.estado in (EstadoPiloto.ATIVO, EstadoPiloto.FERIDO)
    ]

    if len(pilotos_disponiveis) < i:
        print(f"Não há pilotos suficientes para criar um Jaeger (mínimo: {i}).")
        return None

    # Os atributos relevantes ficam na própria opção, sem telas extras.
    opcoes_pilotos = []
    for p in pilotos_disponiveis:
        inteligencia_efetiva = p.inteligencia
        if p.estado == EstadoPiloto.FERIDO:
            inteligencia_efetiva = round(p.inteligencia * (p.saude / 100), 2)
        
        opcoes_pilotos.append({
            "name": (
                f"{p.rotulo} ({p.nacionalidade}) | Nv {p.nivel} | INT {inteligencia_efetiva} | "
                f"{p.personalidade} | {p.estado.name} | Saúde {p.saude}%"
            ),
            "value": p
        })

    pergunta_checkbox = [
        {
            "type": "checkbox",
            "name": "pilotos",
            "message": f"Selecione exatamente {i} piloto(s) e confirme:",
            "choices": opcoes_pilotos
        }
    ]

    while True:
        resposta = prompt(pergunta_checkbox)
        selecionados = resposta.get("pilotos", [])

        if len(selecionados) != i:
            print(f"Necessário {i} pilotos.\n")
            continue

        dupla = selecionados + ([parceiro] if parceiro else [])
        if len(dupla) != 2:
            return selecionados
        # Importado aqui: conexaoPilotos já importa este módulo.
        from pilotos.conexaoPilotos import calcular_conexao, mostrar_conexao_detalhada
        mostrar_conexao_detalhada(*dupla)
        decisao = prompt([{
            "type": "list", "name": "decisao",
            "message": f"Ponte neural prevista: {calcular_conexao(*dupla)}. Confirmar a dupla?",
            "choices": [{"name": "Confirmar dupla", "value": "confirmar"},
                        {"name": "Escolher outros pilotos", "value": "trocar"},
                        {"name": "Cancelar", "value": "cancelar"}],
        }])["decisao"]
        if decisao == "confirmar":
            return selecionados
        if decisao == "cancelar":
            return None
