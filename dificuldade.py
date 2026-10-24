"""Nível de dificuldade da campanha atual, lido por combate, academia e orçamento."""
import json
from pathlib import Path

NIVEIS = json.loads(Path(__file__).with_name("precos.json").read_text(encoding="utf-8"))["dificuldades"]
chave = "normal"
atual = NIVEIS[chave]


def definir(nova_chave):
    global chave, atual
    chave, atual = nova_chave, NIVEIS[nova_chave]
