"""Simula campanhas inteiras com um comandante automático para medir o equilíbrio do jogo.

Uso: python simular.py [campanhas_por_dificuldade]

O comandante joga pelo mesmo painel() da campanha real, respondendo aos menus com uma
estratégia razoável (não ótima): treina pilotos, mantém até MAX_JAEGERS Jaegers tripulados,
repara os danificados e sempre defende a costa com o Jaeger mais forte disponível.
"""
import builtins
import contextlib
import io
import os
import random
import re
import sys
import tempfile
import time
from collections import Counter
from itertools import combinations
from pathlib import Path
from statistics import mean

import audio
import centroOperacoes.historia as historia
import jaegers.factoryJaeger as fabrica_jaeger
import main
import pilotos.factoryPiloto as fabrica_pilotos
import pilotos.piloto as modulo_piloto
from centroOperacoes.cronometro import Cronometro
from jaegers.categorias import CategoriaJaeger, custo_geracao
from jaegers.historicos import JAEGERS_HISTORICOS
from pilotos.conexaoPilotos import calcular_conexao
from pilotos.piloto import EstadoPiloto
from repositorios.repositorios import RepositorioJaegers, RepositorioPilotos
from util import Separator

MAX_JAEGERS = 2
LIMITE_PERGUNTAS = 20000  # trava de segurança contra laços infinitos


class Travou(Exception):
    pass


def livres():
    return [p for p in RepositorioPilotos.listar()
            if p.jaeger is None and p.estado in (EstadoPiloto.ATIVO, EstadoPiloto.FERIDO)]


def vivos():
    return [j for j in RepositorioJaegers.listar() if j.saude > 0]


def operacionais():
    return [j for j in vivos() if j.tripulacao_completa]


def proxima_ordem(campanha):
    saldo, dias = campanha.orcamento.saldo, campanha.dias_ate_ataque()
    if any(not j.tripulacao_completa for j in vivos()) and livres():
        return "tripulacao"
    if (any(j.saude < 70 for j in vivos()) and dias > main.DIAS_POR_ACAO["reparo"]
            and saldo >= 20 * main.CUSTO_REPARO_POR_INTEGRIDADE):
        return "enfermaria"
    fase = max(Cronometro().obter_categoria_atual(), 1)
    obsoletos = all(j.categoria.value < fase for j in vivos())
    # Com a frota obsoleta, junta créditos para um Jaeger da geração atual.
    custo_minimo = main.CUSTO_JAEGER + (custo_geracao(CategoriaJaeger(fase)) if vivos() else 0)
    if vivos():  # além do primeiro Jaeger, guarda reserva para reparos e emergências
        custo_minimo += 50 * main.CUSTO_REPARO_POR_INTEGRIDADE + main.CUSTO_DERROTA
    if len(vivos()) < MAX_JAEGERS or (obsoletos and len(vivos()) < MAX_JAEGERS + 1):
        if len(livres()) >= 2 and saldo >= custo_minimo and dias > main.DIAS_POR_ACAO["construcao"]:
            return "construir"
        if (len(livres()) < 2 and saldo >= main.CUSTO_TREINAMENTO
                and dias > main.DIAS_POR_ACAO["treinamento"]):
            return "treinar"
    return "aguardar"


def forca(jaeger):
    return jaeger.saude * jaeger.forca * (jaeger.inteligencia + 1)


def responder(pergunta, nivel):
    mensagem, tipo = pergunta.get("message", ""), pergunta.get("type")
    opcoes = [c for c in pergunta.get("choices", []) if not isinstance(c, Separator)]
    valores = [c.get("value", c.get("name")) if isinstance(c, dict) else c for c in opcoes]

    if tipo == "input":
        return pergunta.get("default", "")
    if tipo == "checkbox":
        quantidade = int(re.search(r"exatamente (\d+)", mensagem).group(1))
        if quantidade == 1:
            return [max(valores, key=lambda p: p.inteligencia)]
        return list(max(combinations(valores, 2), key=lambda dupla: calcular_conexao(*dupla)))
    if "Como deseja começar" in mensagem:
        return False
    if "dificuldade" in mensagem:
        return nivel
    if "próxima ordem" in mensagem:
        return proxima_ordem(main.campanha_atual)
    if "candidato" in mensagem:
        if "lendarios" in valores:
            return "lendarios"
        return max((v for v in valores if v), key=lambda p: p.inteligencia)
    if "modelo do Jaeger" in mensagem:
        # Só vale um histórico que ainda não esteja obsoleto para a fase atual.
        fase = max(Cronometro().obter_categoria_atual(), 1)
        atuais = [v for v in valores if v and JAEGERS_HISTORICOS[v]["geracao"] >= fase - 1]
        return atuais[-1] if atuais else None
    if "Confirmar a dupla" in mensagem:
        return "confirmar"
    if "geração" in mensagem or "arma" in mensagem:
        return valores[-1]  # a mais forte que o saldo cobre
    if "missão" in mensagem:
        jaegers = [v for v in valores if v is not None]
        return max(jaegers, key=forca) if jaegers else None
    if "unidade para reparar" in mensagem:
        return min((v for v in valores if v), key=lambda j: j.saude)
    if "Escolha o reparo" in mensagem:
        return max(valores)
    if "Selecione um Jaeger" in mensagem:
        return next((v for v in valores if v and not v.tripulacao_completa), None)
    if "O que deseja fazer" in mensagem:
        return "alocar" if "alocar" in valores else None
    if "Fim da" in mensagem:
        return "Sair"
    return valores[0]  # "Continuar" nas narrações e qualquer outra pergunta


def simular_campanha(nivel, semente):
    random.seed(semente)
    main.nova_campanha()
    perguntas = 0
    resultado = {}

    def prompt(lista):
        nonlocal perguntas
        perguntas += len(lista)
        if perguntas > LIMITE_PERGUNTAS:
            raise Travou
        return {p["name"]: responder(p, nivel) for p in lista}

    def final(vitoria):
        def registrar():
            campanha, cronometro = main.campanha_atual, Cronometro()
            if cronometro.data_atual >= cronometro.data_fim:
                causa = "pitfall"
            elif campanha.cidades_perdidas >= main.dificuldade.atual["cidades_toleradas"]:
                causa = "cidades"
            else:
                causa = "recursos"
            resultado.update(vitoria=vitoria, causa=causa)
            return "Sair"
        return registrar

    for modulo in (main, modulo_piloto, fabrica_pilotos, fabrica_jaeger, historia):
        modulo.prompt = prompt
    main.final_vitorioso, main.final_derrota = final(True), final(False)
    try:
        main.painel()
    except Travou:
        resultado.update(vitoria=False, causa="travou")

    campanha = main.campanha_atual
    contagem = Counter(b["resultado"] for b in campanha.historico)
    resultado.update(
        cidades=campanha.cidades_perdidas, ataques=len(campanha.historico),
        vitorias=contagem["vitoria"], derrotas=contagem["derrota"],
        sem_defesa=contagem["desprotegida"], mortos=len(campanha.memorial),
        saldo=campanha.orcamento.saldo, fase=max(Cronometro().obter_categoria_atual(), 1),
    )
    return resultado


def relatorio(nivel, resultados):
    total = len(resultados)
    causas = Counter((r["vitoria"], r["causa"]) for r in resultados)
    pitfall = [r for r in resultados if r["causa"] == "pitfall"]
    print(f"\n=== {main.dificuldade.NIVEIS[nivel]['nome'].upper()} ({total} campanhas) ===")
    print(f"Vitórias: {sum(r['vitoria'] for r in resultados) / total:.0%}")
    for (vitoria, causa), quantidade in sorted(causas.items()):
        print(f"  {'vitória' if vitoria else 'derrota'} por {causa}: {quantidade / total:.0%}")
    if pitfall:
        print(f"Chegaram à Pitfall: {len(pitfall) / total:.0%} | "
              f"venceram a Pitfall: {mean(r['vitoria'] for r in pitfall):.0%}")
    print(f"Ataques por campanha: {mean(r['ataques'] for r in resultados):.1f} | "
          f"vitórias {mean(r['vitorias'] for r in resultados):.1f} | "
          f"derrotas {mean(r['derrotas'] for r in resultados):.1f} | "
          f"sem defesa {mean(r['sem_defesa'] for r in resultados):.1f}")
    print(f"Cidades perdidas: {mean(r['cidades'] for r in resultados):.1f} | "
          f"pilotos mortos: {mean(r['mortos'] for r in resultados):.1f} | "
          f"fase alcançada: {mean(r['fase'] for r in resultados):.1f} | "
          f"saldo final: ₡ {mean(r['saldo'] for r in resultados):,.0f}".replace(",", "."))


def main_simulacao():
    campanhas = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    time.sleep = lambda *_: None
    main.sleep = lambda *_: None
    os.system = lambda *_: 0
    builtins.input = lambda *_: ""
    main.ARQUIVO_SAVE = Path(tempfile.mkdtemp()) / "simulacao.sav"
    audio.ativo = False
    saida = sys.stdout
    for nivel in main.dificuldade.NIVEIS:
        with contextlib.redirect_stdout(io.StringIO()):
            resultados = [simular_campanha(nivel, semente) for semente in range(campanhas)]
        with contextlib.redirect_stdout(saida):
            relatorio(nivel, resultados)


if __name__ == "__main__":
    main_simulacao()
