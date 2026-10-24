from util import *
import dificuldade
from jaegers.ataques import AtaquesJaeger, ataques_jaeger
from jaegers.categorias import estrategias_jaeger, CategoriaJaeger
from pilotos.piloto import Piloto
from pilotos.conexaoPilotos import calcular_conexao


CHANCE_MORTE_PILOTO = 0.1  # por piloto, quando o Jaeger é destruído


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
                 categoria: CategoriaJaeger,
                 piloto3: Piloto = None):

        categoria = CategoriaJaeger(categoria)
        self._nome = nome
        self._forca = forca
        self._durabilidade = durabilidade
        self._ataque_assinatura = ataque_assinatura
        self._pilotos = [p for p in (piloto1, piloto2, piloto3) if p]
        self._tripulacao = len(self._pilotos)  # 2, ou 3 no Crimson Typhoon
        self._inteligencia = calcular_conexao(*self._pilotos)
        self._categoria = categoria
        self._estrategia = estrategias_jaeger[self._categoria]
        if categoria in estrategias_jaeger:
            self._forca, self._durabilidade = estrategias_jaeger[categoria](self)

        self._saude = 100
        self._estado = EstadoJaeger.ATIVO  # Novo atributo

        for piloto in self._pilotos:
            piloto.jaeger = self

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
                # Destruição do Jaeger: chance de morte; senão, ferimento grave.
                piloto.saude = 0 if random() < CHANCE_MORTE_PILOTO else piloto.saude - randint(20, 60)
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
    def pilotos(self): return self._pilotos

    @property
    def tripulacao_necessaria(self):
        return getattr(self, "_tripulacao", 2)  # saves antigos não têm o atributo

    @property
    def tripulacao_completa(self):
        return len(self._pilotos) >= self.tripulacao_necessaria

    # === Métodos de gerenciamento de pilotos ===
    def remover_piloto(self, piloto):
        """Remove um membro da tripulação e deixa o Jaeger indisponível."""
        if piloto not in self._pilotos:
            return False

        piloto.jaeger = None
        self._pilotos.remove(piloto)

        # A ponte neural exige a tripulação completa; sem ela o Jaeger não opera.
        self._inteligencia = 0
        self._estado = EstadoJaeger.INATIVO
        return True

    def adicionar_piloto(self, piloto):
        """Aloca um substituto; o Jaeger só volta a operar com a tripulação completa."""
        if self.saude <= 0 or piloto.jaeger is not None or self.tripulacao_completa:
            return False

        self._pilotos.append(piloto)
        piloto.jaeger = self
        if self.tripulacao_completa:
            self._inteligencia = calcular_conexao(*self._pilotos)
            self._estado = EstadoJaeger.ATIVO if self.saude == 100 else EstadoJaeger.DANIFICADO
        return True

    def recalcular_conexao(self):
        """Atualiza a ponte neural depois que os pilotos evoluem."""
        if self.tripulacao_completa:
            self._inteligencia = calcular_conexao(*self._pilotos)

    # === Métodos de combate ===
    def atacar(self, alvo):
        _, ataque_func = ataques_jaeger[self._ataque_assinatura]
        dano = ataque_func(self._forca, self._inteligencia, self, alvo)
        alvo.atacado(dano)

    def atacado(self, dano):
        dano *= dificuldade.atual["dano_recebido_jaeger"]
        dano_total = int(dano / (self._durabilidade / 100))
        print(f"Dano: {dano_total}")
        self.saude -= dano_total

    # === Impressão de informações ===
    def info(self):
        cor = cores.get(self._categoria.name, "\033[0m")
        reset = "\033[0m"
        pilotos = ", ".join(
            f"{piloto.nome} ({piloto.nacionalidade})" for piloto in self._pilotos
        ) or "Nenhum"

        return (
            f"============================================\n"
            f"  Jaeger: {cor}{self._nome}{reset}\n"
            f"  Categoria: {self._categoria.name}\n"
            f"  Força: {self._forca}\n"
            f"  Durabilidade: {self._durabilidade}\n"
            f"  Inteligência: {self._inteligencia}\n"
            f"  Ataque assinatura: {self._ataque_assinatura.name}\n"
            f"  Saude atual: {self._saude}\n"
            f"  Pilotos: {pilotos}\n"
            f"  Estado: {self._estado.name}\n"
            f"============================================\n"
        )

    def __str__(self):
        cor = cores.get(self._categoria.name, "\033[0m")
        reset = "\033[0m"
        return f"{cor}{self._nome}{reset}"
