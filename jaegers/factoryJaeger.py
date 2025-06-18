from util import *
from centroOperacoes.cronometro import Cronometro
from jaegers.ataques import AtaquesJaeger
from jaegers.jaeger import Jaeger
from repositorios.repositorios import RepositorioPilotos  # ajuste o import conforme sua estrutura
from pilotos.piloto import selecionar_pilotos  # ajuste se necessário

class FabricaJaeger:

    @registrar_jaeger
    def criar_jaeger(self) -> Jaeger:
        pilotos = selecionar_pilotos(2)
        if pilotos is None:
            return None

        piloto1, piloto2 = pilotos

        nome_pergunta = {
            "type": "input",
            "message": "Digite o nome do Jaeger:",
            "name": "nome"
        }

        ataque_pergunta = {
            "type": "fuzzy",
            "message": "Escolha o ataque do Jaeger:",
            "choices": [ataque.name for ataque in AtaquesJaeger if ataque.value >= 0],
            "name": "ataque"
        }

        respostas_jaeger = prompt([nome_pergunta, ataque_pergunta])

        nome = respostas_jaeger["nome"]
        ataque = AtaquesJaeger[respostas_jaeger["ataque"]]

        return Jaeger(nome, 100, 100, ataque, piloto1, piloto2, Cronometro().obter_categoria_atual())