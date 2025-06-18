from util import *

# === Enum de Ataques Jaeger ===
class AtaquesJaeger(Enum):
    LAMINAS_GIRATORIAS = -2 #Crimson Typhoon
    SOCO_NUCLEAR = -1 #Gipsy Danger
    PUNHO_ENERGIZADO = auto()
    LAMINA_DE_PLASMA = auto()
    RAIO_DE_ENERGIA = auto()
    PULSO_ELETRICO = auto()

# === Dicionário de atributos de ataques Jaeger ===
atributos_ataques_jaeger = {
    AtaquesJaeger.PUNHO_ENERGIZADO: {
        "dano_min": 12,
        "dano_max": 18,
        "prob_base": 1.2,
        "bonus": 0.0
    },
    AtaquesJaeger.LAMINA_DE_PLASMA: {
        "dano_min": 20,
        "dano_max": 30,
        "prob_base": 1.0,
        "bonus": 0.0
    },
    AtaquesJaeger.RAIO_DE_ENERGIA: {
        "dano_min": 25,
        "dano_max": 32,
        "prob_base": 0.85,
        "bonus": 0.0
    },
    AtaquesJaeger.PULSO_ELETRICO: {
        "dano_min": 28,
        "dano_max": 35,
        "prob_base": 0.8,
        "bonus": 0.0
    },
    AtaquesJaeger.SOCO_NUCLEAR: {
        "dano_min": 35,
        "dano_max": 50,
        "prob_base": 0.75,
        "bonus": 0.2
    },
    AtaquesJaeger.LAMINAS_GIRATORIAS: {
        "dano_min": 28,
        "dano_max": 62,
        "prob_base": 0.9,
        "bonus": 0.2
    }
}

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
    
# === Dicionário de ataques Jaeger ===
ataques_jaeger = {
    AtaquesJaeger.PUNHO_ENERGIZADO: ("Punho Energizado", lambda f, i, a, al: executar_ataque(AtaquesJaeger.PUNHO_ENERGIZADO, f, i, a, al)),
    AtaquesJaeger.LAMINA_DE_PLASMA: ("Lâmina de Plasma", lambda f, i, a, al: executar_ataque(AtaquesJaeger.LAMINA_DE_PLASMA, f, i, a, al)),
    AtaquesJaeger.RAIO_DE_ENERGIA: ("Raio de Energia", lambda f, i, a, al: executar_ataque(AtaquesJaeger.RAIO_DE_ENERGIA, f, i, a, al)),
    AtaquesJaeger.PULSO_ELETRICO: ("Pulso Elétrico", lambda f, i, a, al: executar_ataque(AtaquesJaeger.PULSO_ELETRICO, f, i, a, al)),
    AtaquesJaeger.SOCO_NUCLEAR: ("Soco Nuclear", lambda f, i, a, al: executar_ataque(AtaquesJaeger.SOCO_NUCLEAR, f, i, a, al)),
    AtaquesJaeger.LAMINAS_GIRATORIAS: ("Lâminas Giratórias", lambda f, i, a, al: executar_ataque(AtaquesJaeger.LAMINAS_GIRATORIAS, f, i, a, al))
}