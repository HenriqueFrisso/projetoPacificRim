from util import *
from jaegers.ataques import AtaquesJaeger, ataques_jaeger
from pilotos.piloto import Piloto
from pilotos.conexaoPilotos import calcular_conexao

# === Classe Jaeger ===
class Jaeger:
    def __init__(self, nome: str,
                 forca: int,
                 durabilidade: int,
                 ataque_assinatura: AtaquesJaeger,
                 piloto1: Piloto,
                 piloto2: Piloto):
        
        self._nome = nome
        self._forca = forca
        self._durabilidade = durabilidade
        self._ataque_assinatura = ataque_assinatura
        self._piloto1 = piloto1
        self._piloto2 = piloto2
        self._inteligencia = calcular_conexao(piloto1, piloto2)
        self._vida = 100
        self._ativo = True
    # === Propriedades protegidas ===
    @property
    def nome(self): return self._nome

    @property
    def forca(self): return self._forca

    @property
    def durabilidade(self): return self._durabilidade

    @property
    def ataque_assinatura(self): return self._ataque_assinatura

    @property
    def vida(self): return self._vida

    @property
    def ativo(self): return self._ativo

    @property
    def inteligencia(self): return self._inteligencia
    
    @property
    def piloto1(self): return self._piloto1
    
    @property
    def piloto2(self): return self._piloto2

    # === Métodos de combate ===
    def atacar(self, alvo):
        _, ataque_func = ataques_jaeger[self._ataque_assinatura]
        dano = ataque_func(self._forca,self._inteligencia, self, alvo)
        alvo.atacado(dano)

    def atacado(self, dano):
        dano_total = int(dano / (self._durabilidade / 100))
        print(f"Dano: {dano_total}")
        self._vida -= dano_total
        if self._vida <= 0:
            self._vida = 0
            self._ativo = False

    # === Impressão de informações ===
    def info(self):
        return (
            f"Jaeger: {self._nome}\n"
            f"Força: {self._forca}\n"
            f"Durabilidade: {self._durabilidade}\n"
            f"Inteligencia: {self._inteligencia}\n"
            f"Ataque assinatura: {self._ataque_assinatura.name}\n"
            f"Vida atual: {self._vida}\n"
            f"Pilotos: {self._piloto1}, {self._piloto2}\n"
            f"Ativo: {'Sim' if self._ativo else 'Não'}"
        )

    def __str__(self):
        return self._nome

@singleton
class GipsyDanger(Jaeger):
    def __init__(self, p1, p2):
        super().__init__(
            nome = "Gipsy Danger",
            forca = 270,
            durabilidade = 150,
            ataque_assinatura = AtaquesJaeger.SOCO_NUCLEAR,
            piloto1 = p1,
            piloto2 = p2
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
            piloto2 = p2
        )
        self._piloto3 = p3
        self._inteligencia = calcular_conexao(p1, p2, p3)
    
    @property
    def piloto3(self): return self.__piloto3

    def info(self):
        return (
            f"Jaeger: {self._nome}\n"
            f"Força: {self._forca}\n"
            f"Durabilidade: {self._durabilidade}\n"
            f"Inteligencia: {self._inteligencia}\n"
            f"Ataque assinatura: {self._ataque_assinatura.name}\n"
            f"Vida atual: {self._vida}\n"
            f"Pilotos: {self._piloto1}, {self._piloto2}, {self._piloto3}\n"
            f"Ativo: {'Sim' if self._ativo else 'Não'}"
        )