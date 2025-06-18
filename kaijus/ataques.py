from util import *

# === Enum de Ataques Kaiju ===
class AtaquesKaiju(Enum):
    GARRAS = auto()
    ACIDO = auto()
    EXPLOSAO = auto()

# === Dicionário de atributos de ataques Kaiju ===
atributos_ataques_kaiju = {
    AtaquesKaiju.GARRAS: {
        "dano_min": 5,
        "dano_max": 10,
        "forca_peso": 0.6,
        "agressividade_peso": 0.4,
        "prob_divisor": 130.0,
        "mensagem_sucesso": "dilacera {alvo}({alvo.saude}) com suas Garras!",
        "mensagem_falha": "tenta dilacerar {alvo}({alvo.saude}), mas erra o ataque!"
    },
    AtaquesKaiju.ACIDO: {
        "dano_min": 15,
        "dano_max": 23,
        "forca_peso": 0.5,
        "agressividade_peso": 0.5,
        "prob_divisor": 150.0,
        "mensagem_sucesso": "cospe um jato de ÁCIDO corrosivo em {alvo}({alvo.saude})!",
        "mensagem_falha": "tenta cuspir ÁCIDO em {alvo}({alvo.saude}), mas erra o alvo!"
    },
    AtaquesKaiju.EXPLOSAO: {
        "dano_min": 20,
        "dano_max": 32,
        "forca_peso": 0.5,
        "agressividade_peso": 0.6,
        "prob_divisor": 180.0,
        "mensagem_sucesso": "provoca uma EXPLOSÃO devastadora dentro de {alvo}({alvo.saude})!",
        "mensagem_falha": "tenta causar uma EXPLOSÃO interna em {alvo}({alvo.saude}), mas falha!"
    }
}


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

# === Dicionário de ataques Kaiju ===
ataques_kaiju = {
    AtaquesKaiju.GARRAS: ("Garras Cortantes", lambda f, ag, i, a, al: executar_ataque_kaiju(AtaquesKaiju.GARRAS, f, ag, i, a, al)),
    AtaquesKaiju.ACIDO: ("Cuspe Ácido", lambda f, ag, i, a, al: executar_ataque_kaiju(AtaquesKaiju.ACIDO, f, ag, i, a, al)),
    AtaquesKaiju.EXPLOSAO: ("Explosão Interna", lambda f, ag, i, a, al: executar_ataque_kaiju(AtaquesKaiju.EXPLOSAO, f, ag, i, a, al)),
}