import json
from pathlib import Path

from util import *
import dificuldade

# === Enum de Ataques Jaeger ===
class AtaquesJaeger(Enum):
    LAMINAS_STING = -4 #Striker Eureka
    PUNHO_TESLA = -3 #Cherno Alpha
    LAMINAS_GIRATORIAS = -2 #Crimson Typhoon
    SOCO_NUCLEAR = -1 #Gipsy Danger
    PUNHO_ENERGIZADO = auto()
    LAMINA_DE_PLASMA = auto()
    RAIO_DE_ENERGIA = auto()
    PULSO_ELETRICO = auto()

ARQUIVO_ATAQUES = Path(__file__).with_name("ataques.json")


def carregar_atributos_ataques():
    """Carrega a tabela editável de ataques Jaeger."""
    with ARQUIVO_ATAQUES.open(encoding="utf-8") as arquivo:
        configuracao = json.load(arquivo)
    return {
        AtaquesJaeger[nome]: atributos
        for nome, atributos in configuracao.items()
    }


atributos_ataques_jaeger = carregar_atributos_ataques()


def custo_arma(tipo: AtaquesJaeger):
    """Custo extra da arma na construção, ajustado pela dificuldade."""
    return round(atributos_ataques_jaeger[tipo].get("custo", 0) * dificuldade.atual["precos"])


def descrever_arma(tipo: AtaquesJaeger):
    atb = atributos_ataques_jaeger[tipo]
    # Precisão com ponte neural de 70; a força do Jaeger multiplica o dano.
    precisao = min(atb["prob_base"] + atb["bonus"], 1.0)
    custo = f"{custo_arma(tipo):,}".replace(",", ".")
    return (f"{atb['nome']} | dano {atb['dano_min']}–{atb['dano_max']} | "
            f"precisão {precisao:.0%} | +₡ {custo} — {atb['descricao']}")

# === Função de ataque Jaeger ===
def executar_ataque(tipo: AtaquesJaeger, forca, inteligencia, atacante, alvo):
    atributos = atributos_ataques_jaeger[tipo]
    
    dano = int(uniform(atributos["dano_min"], atributos["dano_max"]) * (forca / 100))
    prob_acerto = min((inteligencia / 70.0) * atributos["prob_base"] + atributos["bonus"], 1.0)

    nome_ataque = ataques_jaeger[tipo][0]

    if random() <= prob_acerto:
        print(f"{atacante}({atacante.saude}) usa {nome_ataque} contra {alvo}({alvo.saude})!", end=" ")
        return dano
    else:
        print(f"{atacante}({atacante.saude}) tenta usar {nome_ataque} em {alvo}({alvo.saude}), mas falha!", end=" ")
        return 0
    
def criar_ataques_jaeger():
    return {
        tipo: (
            atributos["nome"],
            lambda forca, inteligencia, atacante, alvo, tipo=tipo:
            executar_ataque(tipo, forca, inteligencia, atacante, alvo),
        )
        for tipo, atributos in atributos_ataques_jaeger.items()
    }


ataques_jaeger = criar_ataques_jaeger()
