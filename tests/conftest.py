import builtins
import os
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import audio  # noqa: E402
import main  # noqa: E402
import util  # noqa: E402
from centroOperacoes.cronometro import Cronometro  # noqa: E402
from jaegers.ataques import AtaquesJaeger  # noqa: E402
from jaegers.jaeger import Jaeger  # noqa: E402
from pilotos.piloto import Nacionalidade, Personalidade, Piloto  # noqa: E402
from repositorios.repositorios import (RepositorioJaegers, RepositorioKaijusDerrotados,  # noqa: E402
                                       RepositorioPilotos)


@pytest.fixture(autouse=True)
def estado_limpo(monkeypatch, tmp_path):
    """Cada teste começa numa campanha nova, sem pausas, animações nem save real."""
    monkeypatch.setattr(time, "sleep", lambda *_: None)
    monkeypatch.setattr(main, "sleep", lambda *_: None)
    monkeypatch.setattr(os, "system", lambda *_: 0)
    monkeypatch.setattr(builtins, "input", lambda *_: "")
    monkeypatch.setattr(main, "ARQUIVO_SAVE", tmp_path / "campanha.sav")
    monkeypatch.setattr(util, "_interface", None)
    monkeypatch.setattr(audio, "ativo", False)
    for repositorio in (RepositorioPilotos, RepositorioJaegers, RepositorioKaijusDerrotados):
        repositorio.listar().clear()
    Cronometro().iniciar_cronometro()
    main.aplicar_dificuldade("normal")
    main.campanha_atual = None


@pytest.fixture
def novo_piloto():
    def criar(nome="Piloto", personalidade=Personalidade.LIDER, inteligencia=90,
              nacionalidade=Nacionalidade.BRA, registrar=True):
        piloto = Piloto(nome, 25, inteligencia, nacionalidade, personalidade)
        if registrar:
            RepositorioPilotos.adicionar(piloto)
        return piloto
    return criar


@pytest.fixture
def novo_jaeger(novo_piloto):
    def criar(nome="Teste", forca=100, durabilidade=100, geracao=1,
              ataque=AtaquesJaeger.PUNHO_ENERGIZADO, pilotos=None):
        p1, p2 = pilotos or (novo_piloto("A", Personalidade.CALMO), novo_piloto("B"))
        jaeger = Jaeger(nome, forca, durabilidade, ataque, p1, p2, geracao)
        RepositorioJaegers.adicionar(jaeger)
        return jaeger
    return criar


@pytest.fixture
def responder(monkeypatch):
    """Troca o prompt de um módulo por respostas prontas (lista ou função da pergunta)."""
    def configurar(modulo, respostas):
        perguntas = []
        fila = iter(respostas) if isinstance(respostas, list) else None

        def prompt(lista):
            perguntas.append(lista[0])
            valor = next(fila) if fila else respostas(lista[0])
            return {lista[0]["name"]: valor}

        monkeypatch.setattr(modulo, "prompt", prompt)
        return perguntas
    return configurar
