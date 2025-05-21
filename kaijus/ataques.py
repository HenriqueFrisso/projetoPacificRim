from util import *

# === Enum de Ataques Kaiju ===
class AtaquesKaiju(Enum):
    GARRAS = auto()
    ACIDO = auto()
    EXPLOSAO = auto()

# === Funções de Ataque Kaiju ===
def ataqueGarras(forca, agressividade, inteligencia, atacante, alvo):
    dano_base = randint(20, 35)
    modificador = (forca * 0.6 + agressividade * 0.4) / 100.0
    dano_total = int(dano_base * (1 + modificador))

    probAcerto = min((inteligencia + agressividade) / 200.0, 1.0)

    if random() <= probAcerto:
        print(f"{atacante} dilacera {alvo} com suas Garras!", end=" ")
        return dano_total
    else:
        print(f"{atacante} tenta dilacerar {alvo}, mas erra o ataque!", end=" ")
        return 0

def ataqueAcido(forca, agressividade, inteligencia, atacante, alvo):
    dano_base = randint(40, 60)
    modificador = (forca * 0.5 + agressividade * 0.5) / 100.0
    dano_total = round(dano_base * (1 + modificador), 2)

    prob_acerto = min((inteligencia + agressividade) / 200.0, 1.0)

    if random() <= prob_acerto:
        print(f"{atacante} cospe um jato de ÁCIDO corrosivo em {alvo}!", end=" ")
        return dano_total
    else:
        print(f"{atacante} tenta cuspir ÁCIDO em {alvo}, mas erra o alvo!", end=" ")
        return 0

def ataqueExplosao(forca, agressividade, inteligencia, atacante, alvo):
    dano_base = randint(40, 60)
    modificador = (forca * 0.5 + agressividade * 0.5) / 100.0
    dano_total = round(dano_base * (1 + modificador), 2)

    prob_acerto = min((inteligencia + agressividade) / 200.0, 1.0)

    if random() <= prob_acerto:
        print(f"{atacante} provoca uma EXPLOSÃO devastadora dentro de {alvo}!", end=" ")
        return dano_total
    else:
        print(f"{atacante} tenta causar uma EXPLOSÃO interna em {alvo}, mas falha!", end=" ")
        return 0

# === Dicionário de ataques Kaiju ===
ataques_kaiju = {
    AtaquesKaiju.GARRAS: ("Garras Cortantes", ataqueGarras),
    AtaquesKaiju.ACIDO: ("Cuspe Ácido", ataqueAcido),
    AtaquesKaiju.EXPLOSAO: ("Explosão Interna", ataqueExplosao),
}