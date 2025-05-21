from util import *
from jaegers.ataques import AtaquesJaeger
from jaegers.jaeger import Jaeger
from repositorios.repositorios import RepositorioPilotos  # ajuste o import conforme sua estrutura
from pilotos.piloto import Piloto  # ajuste se necessário


def selecionar_pilotos(i):
    pilotos = []
    pilotos_disponiveis = RepositorioPilotos.listar()

    if len(pilotos_disponiveis) < i:
        print(f"Não há pilotos suficientes para criar um Jaeger (mínimo: {i}).")
        return None

    # Usar índice ou ID para diferenciar pilotos com o mesmo nome
    opcoes_pilotos = [
        {
            "name": f"{i}. {p.nome} ({p.nacionalidade})",
            "value": i
        }
        for i, p in enumerate(pilotos_disponiveis)
    ]

    pergunta_checkbox = [
        {
            "type": "checkbox",
            "name": "pilotos",
            "message": "Selecione dois pilotos:",
            "choices": opcoes_pilotos
        }
    ]

    while True:
        resposta = prompt(pergunta_checkbox)
        selecionados = resposta["pilotos"]

        if len(selecionados) != i:
            print(f"Necessário {i} pilotos.\n")
            continue
        break

    # Obter os objetos Piloto com base no índice retornado
    for j in range(i):
        pilotos.append(pilotos_disponiveis[selecionados[j]])
    return pilotos


class FabricaJaeger:

    @registrar_jaeger
    def criar_jaeger(self) -> Jaeger:
        piloto1, piloto2 = selecionar_pilotos(2)
        
        # Pergunta nome do Jaeger
        nome_pergunta = {
            "type": "input",
            "message": "Digite o nome do Jaeger:",
            "name": "nome"
        }

        # Selecionar ataque
        ataque_pergunta = {
            "type": "fuzzy",
            "message": "Escolha o ataque do Jaeger:",
            "choices": [ataque.name for ataque in AtaquesJaeger if ataque.value >= 0],
            "name": "ataque"
        }

        respostas_jaeger = prompt([nome_pergunta, ataque_pergunta])

        nome = respostas_jaeger["nome"]
        ataque = AtaquesJaeger[respostas_jaeger["ataque"]]

        return Jaeger(nome, 100, 100, ataque, piloto1, piloto2)
