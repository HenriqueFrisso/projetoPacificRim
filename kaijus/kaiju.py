from kaijus.kaijusBase import kaijusBase
from kaijus.categorias import estrategias_kaiju
from kaijus.ataques import ataques_kaiju
from util import registrar_kaiju_derrotado
import dificuldade



cores = {
    "DESCONHECIDA": "\033[90m",  # cinza
    "I": "\033[92m",             # verde
    "II": "\033[93m",            # amarelo
    "III": "\033[33m",           # laranja (amarelo escuro)
    "IV": "\033[91m",            # vermelho
    "V": "\033[95m",             # roxo/magenta
}

# === Classe Kaiju ===
class Kaiju:
    def __init__(self, nome: str):
        if nome not in kaijusBase:
            raise ValueError(f"Kaiju '{nome}' não encontrado na base de dados.")

        self._nome = nome
        dados = kaijusBase[nome]

        self._categoria = dados["categoria"]
        self._estrategia = estrategias_kaiju[self._categoria]
        self._ataque_assinatura = dados["ataque_assinatura"]
        self._forca = int(dados["forca"])
        self._durabilidade = int(dados["durabilidade"])
        self._inteligencia = int(dados["inteligencia"])
        self._agressividade = int(dados["agressividade"])

        self._inteligencia, self._agressividade = self._estrategia(self)

        self._saude = 100
        self._ativo = True

    # === Propriedades protegidas ===
    @property
    def nome(self): return self._nome

    @property
    def categoria(self): return self._categoria

    @property
    def saude(self): return self._saude

    @saude.setter
    @registrar_kaiju_derrotado
    def saude(self, nova_saude):
        self._saude = nova_saude
        if self._saude <= 0:
            self._saude = 0
            self._ativo = False
        return self
    
    @property
    def ativo(self): return self._ativo

    @property
    def forca(self): return self._forca

    @property
    def durabilidade(self): return self._durabilidade

    @property
    def inteligencia(self): return self._inteligencia

    @property
    def agressividade(self): return self._agressividade

    @property
    def ataque_assinatura(self): return self._ataque_assinatura

    # === Métodos de combate ===
    def atacar(self, alvo):
        _, func_ataque = ataques_kaiju[self._ataque_assinatura]
        dano = func_ataque(self._forca, self._agressividade, self._inteligencia, self, alvo)
        alvo.atacado(dano)

    def atacado(self, dano):
        dano *= dificuldade.atual["dano_recebido_kaiju"]
        dano_total = int(dano / (self._durabilidade / 100))
        print(f"Dano: {dano_total}")
        self.saude -= dano_total

    # === Impressão de informações ===
    def info(self):
        cor = cores.get(self._categoria.name, "\033[0m")
        reset = "\033[0m"
        return (
            f"============================================\n"
            f"Kaiju: {cor}{self._nome}{reset}\n"
            f"Categoria: {self._categoria.name}\n"
            f"Força: {self._forca}\n"
            f"Durabilidade: {self._durabilidade}\n"
            f"Inteligência: {self._inteligencia}\n"
            f"Agressividade: {self._agressividade}\n"
            f"Ataque assinatura: {self._ataque_assinatura.name}\n"
            f"Saude atual: {self._saude}\n"
            f"Ativo: {'Sim' if self._ativo else 'Não'}\n"
            f"============================================\n"
        )

    def __str__(self):

        cor = cores.get(self._categoria.name, "\033[0m")
        reset = "\033[0m"
        return f"{cor}{self._nome}{reset}"

