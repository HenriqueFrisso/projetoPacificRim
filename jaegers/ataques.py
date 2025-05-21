from util import *

# === Enum de Ataques Jaeger ===
class AtaquesJaeger(Enum):
    LAMINAS_GIRATORIAS = -2 #Crimson Typhoon
    SOCO_NUCLEAR = -1 #Gipsy Danger
    PUNHO_ENERGIZADO = auto()
    LAMINA_DE_PLASMA = auto()
    RAIO_DE_ENERGIA = auto()
    PULSO_ELETRICO = auto()

# === Funções de ataque Jaeger ===
def ataque_punho_energizado(forca, inteligencia, atacante, alvo):
    dano = int(uniform(17, 25) * (forca / 100))
    prob_acerto = 1.2
    prob_acerto = min((inteligencia / 100.0) * prob_acerto, 1.0)

    if random() <= prob_acerto:
        print(f"{atacante} desfere um Punho Energizado contra {alvo}!", end=" ")
        return dano
    else:
        print(f"{atacante} tenta desferir um Punho Energizado em {alvo}, mas erra!", end=" ")
        return 0

def ataque_lamina_de_plasma(forca, inteligencia, atacante, alvo):
    dano = int(uniform(20, 30) * (forca / 100))
    prob_acerto = 1.0
    prob_acerto = min((inteligencia / 100.0) * prob_acerto, 1.0)

    if random() <= prob_acerto:
        print(f"{atacante} corta com a Lâmina de Plasma {alvo}!", end=" ")
        return dano
    else:
        print(f"{atacante} tenta cortar {alvo} com a Lâmina de Plasma, mas erra!", end=" ")
        return 0

def ataque_raio_de_energia(forca, inteligencia, atacante, alvo):
    dano = int(uniform(15, 22) * (forca / 100))
    prob_acerto = 0.85
    prob_acerto = min((inteligencia / 100.0) * prob_acerto, 1.0)

    if random() <= prob_acerto:
        print(f"{atacante} dispara um Raio de Energia em {alvo}!", end=" ")
        return dano
    else:
        print(f"{atacante} dispara um Raio de Energia em {alvo}, mas erra!", end=" ")
        return 0

def ataque_pulso_eletrico(forca, inteligencia, atacante, alvo):
    dano = int(uniform(18, 28) * (forca / 100))
    prob_acerto = 0.9
    prob_acerto = min((inteligencia / 100.0) * prob_acerto, 1.0)

    if random() <= prob_acerto:
        print(f"{atacante} lança um Pulso Elétrico contra {alvo}!", end=" ")
        return dano
    else:
        print(f"{atacante} tenta lançar um Pulso Elétrico em {alvo}, mas erra!", end=" ")
        return 0

def ataque_soco_nuclear(forca, inteligencia, atacante, alvo):
    dano = int(uniform(35, 50) * (forca / 100))
    prob_acerto = 0.75
    prob_acerto = min(((inteligencia / 100.0) * prob_acerto) + 0.2, 1.0)

    if random() <= prob_acerto:
        print(f"{atacante} carrega seu reator e desfere um SOCO NUCLEAR em {alvo}!", end=" ")
        return dano
    else:
        print(f"{atacante} tenta usar o SOCO NUCLEAR em {alvo}, mas a carga falha!", end=" ")
        return 0

def ataque_laminas_giratorias(forca, inteligencia, atacante, alvo):
    dano = int(uniform(28, 62) * (forca / 100))
    prob_acerto = 0.9
    prob_acerto = min(((inteligencia / 100.0) * prob_acerto) + 0.2, 1.0)

    if random() <= prob_acerto:
        print(f"{atacante} ativa suas LÂMINAS GIRATÓRIAS e ataca {alvo} com precisão!", end=" ")
        return dano
    else:
        print(f"{atacante} tenta atacar com as LÂMINAS GIRATÓRIAS em {alvo}, mas erra o golpe!", end=" ")
        return 0
      
# === Dicionário de ataques Jaeger ===
ataques_jaeger = {
    AtaquesJaeger.PUNHO_ENERGIZADO: ("Punho Energizado", ataque_punho_energizado),
    AtaquesJaeger.LAMINA_DE_PLASMA: ("Lâmina de Plasma", ataque_lamina_de_plasma),
    AtaquesJaeger.RAIO_DE_ENERGIA: ("Raio de Energia", ataque_raio_de_energia),
    AtaquesJaeger.PULSO_ELETRICO: ("Pulso Elétrico", ataque_pulso_eletrico),
    AtaquesJaeger.SOCO_NUCLEAR: ("Soco Nuclear", ataque_soco_nuclear),
    AtaquesJaeger.LAMINAS_GIRATORIAS: ("Lâminas Giratórias", ataque_laminas_giratorias)
}
