from kaijus.kaijusBase import kaijusBase
from kaijus.categorias import estrategias_kaiju
from kaijus.ataques import ataques_kaiju

# === Classe Kaiju ===
class Kaiju:
    def __init__(self, nome: str):
        if nome not in kaijusBase:
            raise ValueError(f"Kaiju '{nome}' não encontrado na base de dados.")

        self.__nome = nome
        dados = kaijusBase[nome]

        self.__categoria = dados["categoria"]
        self.__estrategia = estrategias_kaiju[self.__categoria]
        self.__ataque_assinatura = dados["ataque_assinatura"]
        self.__forca = int(dados["forca"])
        self.__durabilidade = int(dados["durabilidade"])
        self.__inteligencia = int(dados["inteligencia"])
        self.__agressividade = int(dados["agressividade"])

        self.__inteligencia, self.__agressividade = self.__estrategia(self)

        self.__vida = 100
        self.__ativo = True

    # === Propriedades protegidas ===
    @property
    def nome(self): return self.__nome

    @property
    def categoria(self): return self.__categoria

    @property
    def vida(self): return self.__vida

    @property
    def ativo(self): return self.__ativo

    @property
    def forca(self): return self.__forca

    @property
    def durabilidade(self): return self.__durabilidade

    @property
    def inteligencia(self): return self.__inteligencia

    @property
    def agressividade(self): return self.__agressividade

    @property
    def ataque_assinatura(self): return self.__ataque_assinatura

    # === Métodos de combate ===
    def atacar(self, alvo):
        _, func_ataque = ataques_kaiju[self.__ataque_assinatura]
        dano = func_ataque(self.__forca, self.__agressividade, self.__inteligencia, self.__nome, alvo.nome)
        alvo.atacado(dano)

    def atacado(self, dano):
        dano_total = int(dano / (self.__durabilidade / 100))
        print(f"Dano: {dano_total}")
        self.__vida -= dano_total
        if self.__vida <= 0:
            self.__vida = 0
            self.__ativo = False

    # === Impressão de informações ===
    def info(self):
        return (
            f"Kaiju: {self.__nome}\n"
            f"Categoria: {self.__categoria.name}\n"
            f"Força: {self.__forca}\n"
            f"Durabilidade: {self.__durabilidade}\n"
            f"Inteligência: {self.__inteligencia}\n"
            f"Agressividade: {self.__agressividade}\n"
            f"Ataque assinatura: {self.__ataque_assinatura.name}\n"
            f"Vida atual: {self.__vida}\n"
            f"Ativo: {'Sim' if self.__ativo else 'Não'}"
        )

    def __str__(self):
        cores = {
            "DESCONHECIDA": "\033[90m",  # cinza
            "I": "\033[92m",             # verde
            "II": "\033[93m",            # amarelo
            "III": "\033[33m",           # laranja (amarelo escuro)
            "IV": "\033[91m",            # vermelho
            "V": "\033[95m",             # roxo/magenta
        }
        cor = cores.get(self.__categoria.name, "\033[0m")
        reset = "\033[0m"
        return f"{cor}{self.__nome}{reset}"

