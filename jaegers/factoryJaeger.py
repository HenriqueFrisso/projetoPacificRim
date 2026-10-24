from util import *
from centroOperacoes.cronometro import Cronometro
from jaegers.ataques import AtaquesJaeger, custo_arma, descrever_arma
from jaegers.categorias import CategoriaJaeger, custo_geracao, descrever_geracao
from jaegers.jaeger import Jaeger
from repositorios.repositorios import RepositorioJaegers, RepositorioPilotos
from pilotos.piloto import selecionar_pilotos  # ajuste se necessário

NOMES_JAEGER = [
    "Gipsy", "Striker", "Crimson", "Cherno", "Coyote", "Horizon", "Romeo", "Tacit",
    "Brawler", "Titan", "Saber", "Guardian", "Bracer", "November", "Valor", "Lucky",
    "Iron", "Echo", "Shaolin", "Matador",
]
SOBRENOMES_JAEGER = [
    "Danger", "Eureka", "Typhoon", "Alpha", "Tango", "Brave", "Blue", "Ronin",
    "Yukon", "Redeemer", "Athena", "Phoenix", "Ajax", "Fury", "Seven", "Avenger",
    "Defiant", "Legion", "Sentinel", "Vanguard",
]


def sugerir_nome():
    """Combina nome e sobrenome sem repetir um Jaeger já construído."""
    usados = {jaeger.nome for jaeger in RepositorioJaegers.listar()}
    livres = [f"{n} {s}" for n in NOMES_JAEGER for s in SOBRENOMES_JAEGER
              if f"{n} {s}" not in usados]
    return choice(livres) if livres else f"{choice(NOMES_JAEGER)} {choice(SOBRENOMES_JAEGER)}"


class FabricaJaeger:

    @registrar_jaeger
    def criar_jaeger(self, verba=None) -> Jaeger:
        """verba limita geração + arma ao que o orçamento cobre além do custo base."""
        verba = float("inf") if verba is None else verba
        cronometro = Cronometro()
        fase = cronometro.obter_categoria_atual()
        pilotos = selecionar_pilotos(2)
        if pilotos is None:
            return None

        piloto1, piloto2 = pilotos

        sugestao = sugerir_nome()
        nome_pergunta = {
            "type": "input",
            "message": "Nome do Jaeger (Enter aceita a sugestão):",
            "default": sugestao,
            "name": "nome"
        }

        geracoes = []
        for geracao in CategoriaJaeger:
            if geracao.value > fase:
                liberacao = cronometro.data_liberacao(geracao.value).strftime("%d/%m/%Y")
                geracoes.append(Separator(f"🔒 {geracao.name} — liberada em {liberacao}"))
            elif custo_geracao(geracao) > verba:
                geracoes.append(Separator(f"💰 {descrever_geracao(geracao)} — créditos insuficientes"))
            else:
                geracoes.append({"name": descrever_geracao(geracao), "value": geracao})

        geracao_pergunta = {
            "type": "list",
            "message": "Escolha a geração do Jaeger:",
            "choices": geracoes,
            "name": "geracao"
        }

        respostas_jaeger = prompt([nome_pergunta, geracao_pergunta])
        nome = respostas_jaeger["nome"].strip() or sugestao
        geracao = respostas_jaeger["geracao"]

        verba_arma = verba - custo_geracao(geracao)
        armas = [ataque for ataque in AtaquesJaeger
                 if ataque.value >= 0 and custo_arma(ataque) <= verba_arma]
        ataque = prompt([{
            "type": "list",
            "message": "Escolha a arma assinatura:",
            "choices": [{"name": descrever_arma(ataque), "value": ataque} for ataque in armas],
            "name": "ataque"
        }])["ataque"]

        return Jaeger(nome, 100, 100, ataque, piloto1, piloto2, geracao)
