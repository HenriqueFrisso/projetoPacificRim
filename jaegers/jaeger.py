from util import *
from jaegers.ataques import AtaquesJaeger, ataques_jaeger
from jaegers.categorias import estrategias_jaeger, CategoriaJaeger
from pilotos.piloto import Piloto
from pilotos.conexaoPilotos import calcular_conexao


class EstadoJaeger(Enum):
    ATIVO = 0
    INATIVO = 1
    DANIFICADO = 2
    REFORMANDO = 3
    DESTRUIDO = 4


cores = {
    "MARK_I": "\033[94m",   # azul claro
    "MARK_II": "\033[96m",  # ciano
    "MARK_III": "\033[92m", # verde
    "MARK_IV": "\033[93m",  # amarelo
    "MARK_V": "\033[91m",   # vermelho
}
    

# === Classe Jaeger ===
class Jaeger:
    def __init__(self, nome: str,
                 forca: int,
                 durabilidade: int,
                 ataque_assinatura: AtaquesJaeger,
                 piloto1: Piloto,
                 piloto2: Piloto,
                 categoria: CategoriaJaeger):

        categoria = CategoriaJaeger(categoria)
        self._nome = nome
        self._forca = forca
        self._durabilidade = durabilidade
        self._ataque_assinatura = ataque_assinatura
        self._piloto1 = piloto1
        self._piloto2 = piloto2
        self._pilotos = [piloto1, piloto2]
        self._inteligencia = calcular_conexao(piloto1, piloto2)
        self._categoria = categoria
        self._estrategia = estrategias_jaeger[self._categoria]
        if categoria in estrategias_jaeger:
            self._forca, self._durabilidade = estrategias_jaeger[categoria](self)

        self._saude = 100
        self._estado = EstadoJaeger.ATIVO  # Novo atributo

        self.piloto1.jaeger = self
        self.piloto2.jaeger = self

    # === Propriedades ===
    @property
    def nome(self): return self._nome

    @property
    def forca(self): return self._forca

    @property
    def durabilidade(self): return self._durabilidade

    @property
    def ataque_assinatura(self): return self._ataque_assinatura

    @property
    def saude(self): return self._saude

    @saude.setter
    def saude(self, nova_saude):
        self._saude = nova_saude
        if nova_saude <= 0:
            self._saude = 0
            self._estado = EstadoJaeger.DESTRUIDO
            for piloto in self._pilotos:
                piloto.jaeger = None
                piloto.saude -= randint(20, 60)
        elif self._saude >= 100:
            if self.pilotos == []:
                self._estado = EstadoJaeger.INATIVO
            else:
                self._estado = EstadoJaeger.ATIVO
        else:
            self._estado = EstadoJaeger.DANIFICADO

    @property
    def inteligencia(self): return self._inteligencia

    @property
    def categoria(self): return self._categoria

    @property
    def estado(self): return self._estado

    @estado.setter
    def estado(self, novo_estado):
        self._estado = novo_estado

    @property
    def piloto1(self): return self._piloto1

    @property
    def piloto2(self): return self._piloto2

    @property
    def pilotos(self): return self._pilotos
    
    # === Métodos de gerenciamento de pilotos ===
    def remover_pilotos(self):
        if self._pilotos == []:
            print("Jaeger não possui pilotos associados a ele.")
            return
        self._piloto1.jaeger = None
        self._piloto2.jaeger = None
        self._piloto1 = None
        self._piloto2 = None
        self._pilotos = []
        self._inteligencia = 0
        self.estado = EstadoJaeger.INATIVO

    def adicionar_pilotos(self, piloto1, piloto2):
        if self.saude == 0:
            print("Jaeger está destruido e não pode receber novos pilotos.")
        self._piloto1 = piloto1
        self._piloto2 = piloto2
        self._pilotos = [piloto1, piloto2]
        self._piloto1.jaeger = self
        self._piloto2.jaeger = self
        self._inteligencia = calcular_conexao(piloto1, piloto2)
        self._estado = EstadoJaeger.ATIVO

    # === Métodos de combate ===
    def atacar(self, alvo):
        _, ataque_func = ataques_jaeger[self._ataque_assinatura]
        dano = ataque_func(self._forca, self._inteligencia, self, alvo)
        alvo.atacado(dano)

    def atacado(self, dano):
        dano_total = int(dano / (self._durabilidade / 100))
        print(f"Dano: {dano_total}")
        self.saude -= dano_total

    # === Impressão de informações ===
    def info(self):
        cor = cores.get(self._categoria.name, "\033[0m")
        reset = "\033[0m"

        return (
            f"============================================\n"
            f"  Jaeger: {cor}{self._nome}{reset}\n"
            f"  Categoria: {self._categoria.name}\n"
            f"  Força: {self._forca}\n"
            f"  Durabilidade: {self._durabilidade}\n"
            f"  Inteligência: {self._inteligencia}\n"
            f"  Ataque assinatura: {self._ataque_assinatura.name}\n"
            f"  Saude atual: {self._saude}\n"
            f"  Pilotos: {self._piloto1}, {self._piloto2}\n"
            f"  Estado: {self._estado.name}\n"
            f"============================================\n"
        )

    def __str__(self):
        cor = cores.get(self._categoria.name, "\033[0m")
        reset = "\033[0m"
        return f"{cor}{self._nome}{reset}"
    


@singleton
class GipsyDanger(Jaeger):
    def __init__(self, p1, p2):
        super().__init__(
            nome = "Gipsy Danger",
            forca = 270,
            durabilidade = 150,
            ataque_assinatura = AtaquesJaeger.SOCO_NUCLEAR,
            piloto1 = p1,
            piloto2 = p2,
            categoria = 3
        )

@singleton
class CrimsonTyphoon(Jaeger):
    def __init__(self, p1, p2, p3):
        super().__init__(
            nome = "Crimson Typhoon",
            forca = 310,
            durabilidade = 110,
            ataque_assinatura = AtaquesJaeger.LAMINAS_GIRATORIAS,
            piloto1 = p1,
            piloto2 = p2,
            categoria = 4
        )
        self._piloto3 = p3
        self._pilotos = [self.piloto1, self.piloto2, self.piloto3]
        self._inteligencia = calcular_conexao(p1, p2, p3)
    
    @property
    def piloto3(self): return self.__piloto3

    def remover_pilotos(self):
        super().remover_pilotos()
        self._piloto3.jaeger = None
        self._piloto3 = None
    
    def adicionar_pilotos(self, piloto1, piloto2, piloto3):
        super().adicionar_pilotos(piloto1, piloto2)
        self._piloto3 = piloto3
        self._pilotos.append(piloto3)
        self._piloto3.jaeger = self
        self._inteligencia = calcular_conexao(piloto1, piloto2, piloto3)

    @property
    def piloto3(self): return self._piloto3

    def info(self):
        cor = cores.get(self._categoria.name, "\033[0m")
        reset = "\033[0m"

        return (
            f"Jaeger: {cor}{self._nome}{reset}\n"
            f"Categoria: {self._categoria.name}\n"
            f"Força: {self._forca}\n"
            f"Durabilidade: {self._durabilidade}\n"
            f"Inteligência: {self._inteligencia}\n"
            f"Ataque assinatura: {self._ataque_assinatura.name}\n"
            f"Saude atual: {self._saude}\n"
            f"Pilotos: {self._piloto1}, {self._piloto2}, {self._piloto3}\n"
            f"Estado: {self._estado.name}"
        )