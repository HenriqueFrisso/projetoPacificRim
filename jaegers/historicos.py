"""Jaegers históricos do filme: mais fortes, mas só com a tripulação original."""
import json
from pathlib import Path
from random import choice, random

import dificuldade
from jaegers.ataques import AtaquesJaeger, ataques_jaeger
from jaegers.categorias import CategoriaJaeger, estrategias_jaeger
from pilotos.piloto import Nacionalidade, Personalidade, Piloto
from repositorios.repositorios import RepositorioJaegers, RepositorioPilotos

DADOS = json.loads(Path(__file__).with_name("historicos.json").read_text(encoding="utf-8"))
JAEGERS_HISTORICOS = DADOS["jaegers"]


def custo_historico(nome):
    """Custo extra do modelo histórico, além do custo base e da geração."""
    return round(JAEGERS_HISTORICOS[nome]["custo"] * dificuldade.atual["precos"])


def nomes_tripulacao(nome):
    return [piloto["nome"] for piloto in JAEGERS_HISTORICOS[nome]["pilotos"]]


def tripulacao_original(nome):
    """Pilotos originais que estão no efetivo, na ordem do filme (None = não recrutado)."""
    lendas = {p.nome: p for p in RepositorioPilotos.listar() if getattr(p, "lendario", False)}
    return [lendas.get(nome_piloto) for nome_piloto in nomes_tripulacao(nome)]


def equipes_para_recrutar(fase, caidos=()):
    """Equipes com a geração já liberada e nenhum membro recrutado ou morto em combate."""
    indisponiveis = {p.nome for p in RepositorioPilotos.listar()} | set(caidos)
    return [nome for nome, dados in JAEGERS_HISTORICOS.items()
            if dados["geracao"] <= fase and not indisponiveis & set(nomes_tripulacao(nome))]


def sortear_oferta(fase, caidos=()):
    """Às vezes uma equipe lendária aparece entre os candidatos da Academia."""
    equipes = equipes_para_recrutar(fase, caidos)
    return choice(equipes) if equipes and random() < DADOS["chance_na_academia"] else None


def recrutar(nome):
    """Cria a tripulação lendária: experiente e com a ponte neural já afinada entre si."""
    tripulacao = []
    for dados in JAEGERS_HISTORICOS[nome]["pilotos"]:
        piloto = Piloto(dados["nome"], dados["idade"], dados["inteligencia"],
                        Nacionalidade[dados["nacionalidade"]], Personalidade[dados["personalidade"]])
        piloto.lendario = True
        piloto.experiencia = DADOS["experiencia_inicial"]
        tripulacao.append(piloto)
    for piloto in tripulacao:
        for parceiro in tripulacao:
            if parceiro is not piloto:
                piloto.vinculos[parceiro.id] = {"nome": parceiro.nome, "batalhas": DADOS["vinculo_inicial"]}
    return tripulacao


def motivo_bloqueio(nome, fase, verba):
    """Por que o Jaeger histórico não pode ser construído agora; None se pode."""
    dados = JAEGERS_HISTORICOS[nome]
    if dados["geracao"] > fase:
        return f"liberado na fase {dados['geracao']}"
    if any(j.nome == nome and j.saude > 0 for j in RepositorioJaegers.listar()):
        return "já está em serviço"
    tripulacao = tripulacao_original(nome)
    faltam = [n for n, piloto in zip(nomes_tripulacao(nome), tripulacao) if piloto is None]
    if faltam:
        return "requer " + ", ".join(faltam[:-1]) + (" e " if len(faltam) > 1 else "") + faltam[-1]
    ocupados = [piloto.nome for piloto in tripulacao if piloto.jaeger is not None]
    if ocupados:
        return f"{', '.join(ocupados)} já pilota outro Jaeger"
    if custo_historico(nome) > verba:
        return "créditos insuficientes"
    return None


def descrever(nome):
    dados = JAEGERS_HISTORICOS[nome]
    geracao = CategoriaJaeger(dados["geracao"])

    class _Base:  # aplica o bônus da geração sobre os atributos do modelo
        _forca, _durabilidade = dados["forca"], dados["durabilidade"]

    forca, durabilidade = estrategias_jaeger[geracao](_Base)
    arma = ataques_jaeger[AtaquesJaeger[dados["ataque"]]][0]
    custo = f"{custo_historico(nome):,}".replace(",", ".")
    tripulacao = f"{len(dados['pilotos'])} pilotos | " if len(dados["pilotos"]) != 2 else ""
    return (f"★ {nome} | {geracao.name} | força {forca} | durabilidade {durabilidade} | {arma} | "
            f"{tripulacao}+₡ {custo}")
