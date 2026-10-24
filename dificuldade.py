"""Nível de dificuldade da campanha atual, lido por combate, academia e orçamento."""
import json
from pathlib import Path

NIVEIS = json.loads(Path(__file__).with_name("precos.json").read_text(encoding="utf-8"))["dificuldades"]
atual = NIVEIS["normal"]


def definir(chave):
    global atual
    atual = NIVEIS[chave]
