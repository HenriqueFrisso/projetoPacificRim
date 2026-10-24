import json
from pathlib import Path

from util import *

# === Enum de Ataques Kaiju ===
class AtaquesKaiju(Enum):
    GARRAS = auto()
    ACIDO = auto()
    EXPLOSAO = auto()

ARQUIVO_ATAQUES = Path(__file__).with_name("ataques.json")


def carregar_atributos_ataques():
    """Carrega a tabela editável de ataques Kaiju."""
    with ARQUIVO_ATAQUES.open(encoding="utf-8") as arquivo:
        configuracao = json.load(arquivo)
    return {
        AtaquesKaiju[nome]: atributos
        for nome, atributos in configuracao.items()
    }


# A chave do Enum mantém compatibilidade com o restante do combate.
atributos_ataques_kaiju = carregar_atributos_ataques()


# === Funções de Ataque Kaiju ===
def executar_ataque_kaiju(tipo: AtaquesKaiju, forca, agressividade, inteligencia, atacante, alvo):
    atb = atributos_ataques_kaiju[tipo]

    dano_base = randint(atb["dano_min"], atb["dano_max"])
    modificador = (forca * atb["forca_peso"] + agressividade * atb["agressividade_peso"]) / 100.0
    dano_total = round(dano_base * (1 + modificador), 2)

    prob_acerto = min((inteligencia + (agressividade/3)) / atb["prob_divisor"], 1.0)

    if random() <= prob_acerto:
        print(f"{atacante}({atacante.saude}) {atb['mensagem_sucesso'].format(alvo=alvo)}", end=" ")
        return dano_total
    else:
        print(f"{atacante}({atacante.saude}) {atb['mensagem_falha'].format(alvo=alvo)}", end=" ")
        return 0

def criar_ataques_kaiju():
    return {
        tipo: (
            atributos["nome"],
            lambda forca, agressividade, inteligencia, atacante, alvo, tipo=tipo:
            executar_ataque_kaiju(tipo, forca, agressividade, inteligencia, atacante, alvo),
        )
        for tipo, atributos in atributos_ataques_kaiju.items()
    }


ataques_kaiju = criar_ataques_kaiju()
