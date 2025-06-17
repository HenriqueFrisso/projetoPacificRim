from util import *
from centroOperacoes.cronometro import Cronometro
from jaegers.ataques import AtaquesJaeger
from jaegers.jaeger import Jaeger
from repositorios.repositorios import RepositorioPilotos  # ajuste o import conforme sua estrutura
from pilotos.piloto import Piloto, EstadoPiloto  # ajuste se necessário


def selecionar_pilotos(i):
    # Filtra pilotos que não têm jaeger e estão ATIVO ou FERIDO
    pilotos_disponiveis = [
        p for p in RepositorioPilotos.listar() 
        if p.jaeger is None and p.estado in (EstadoPiloto.ATIVO, EstadoPiloto.FERIDO)
    ]

    if len(pilotos_disponiveis) < i:
        print(f"Não há pilotos suficientes para criar um Jaeger (mínimo: {i}).")
        return None

    # Cria opções de escolha com inteligência ajustada, estado e personalidade
    opcoes_pilotos = []
    for idx, p in enumerate(pilotos_disponiveis):
        inteligencia_efetiva = p.inteligencia
        if p.estado == EstadoPiloto.FERIDO:
            inteligencia_efetiva = round(p.inteligencia * (p.saude / 100), 2)
        
        opcoes_pilotos.append({
            "name": (
                f"{idx}. {p.nome} ({p.nacionalidade})\n"
                f"   Estado: {p.estado.name} | Inteligência: {inteligencia_efetiva} | "
                f"Personalidade: {p.personalidade or 'N/A'}"
            ),
            "value": idx
        })

    pergunta_checkbox = [
        {
            "type": "checkbox",
            "name": "pilotos",
            "message": f"Selecione {i} pilotos:",
            "choices": opcoes_pilotos
        }
    ]

    while True:
        resposta = prompt(pergunta_checkbox)
        selecionados = resposta.get("pilotos", [])

        if len(selecionados) != i:
            print(f"Necessário {i} pilotos.\n")
            continue
        break

    pilotos_selecionados = [pilotos_disponiveis[idx] for idx in selecionados]
    return pilotos_selecionados


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