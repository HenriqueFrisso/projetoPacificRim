from kaijus.categorias import CategoriaKaiju
from kaijus.ataques import AtaquesKaiju

# === Dicionário de Kaijus ===
kaijusBase = {
    "KAIJU DESCONHECIDO": {
        "categoria": CategoriaKaiju.DESCONHECIDA,
        "forca": 80,
        "durabilidade": 100,
        "inteligencia": 80,
        "agressividade": 80,
        "ataque_assinatura": AtaquesKaiju.ACIDO
    },
    "TARANAIS": {
        "categoria": CategoriaKaiju.DESCONHECIDA,
        "forca": 70,
        "durabilidade": 100,
        "inteligencia": 68,
        "agressividade": 49,
        "ataque_assinatura": AtaquesKaiju.GARRAS
    },
    "BELOBOG": {
        "categoria": CategoriaKaiju.DESCONHECIDA,
        "forca": 85,
        "durabilidade": 110,
        "inteligencia": 86,
        "agressividade": 92,
        "ataque_assinatura": AtaquesKaiju.EXPLOSAO
    },
    "KARLOFF": {
        "categoria": CategoriaKaiju.I,
        "forca": 55,
        "durabilidade": 90,
        "inteligencia": 42,
        "agressividade": 63,
        "ataque_assinatura": AtaquesKaiju.GARRAS
    },
    "TENGU": {
        "categoria": CategoriaKaiju.I,
        "forca": 60,
        "durabilidade": 80,
        "inteligencia": 44,
        "agressividade": 59,
        "ataque_assinatura": AtaquesKaiju.GARRAS
    },
    "ITAK": {
        "categoria": CategoriaKaiju.II,
        "forca": 65,
        "durabilidade": 85,
        "inteligencia": 62,
        "agressividade": 70,
        "ataque_assinatura": AtaquesKaiju.GARRAS
    },
    "HUNDUN": {
        "categoria": CategoriaKaiju.II,
        "forca": 70,
        "durabilidade": 90,
        "inteligencia": 50,
        "agressividade": 75,
        "ataque_assinatura": AtaquesKaiju.ACIDO
    },
    "KNIFEHEAD": {
        "categoria": CategoriaKaiju.III,
        "forca": 78,
        "durabilidade": 100,
        "inteligencia": 60,
        "agressividade": 80,
        "ataque_assinatura": AtaquesKaiju.EXPLOSAO
    },
    "HUO-DA": {
        "categoria": CategoriaKaiju.III,
        "forca": 82,
        "durabilidade": 110,
        "inteligencia": 68,
        "agressividade": 85,
        "ataque_assinatura": AtaquesKaiju.ACIDO
    },
    "YAMARASHI": {
        "categoria": CategoriaKaiju.III,
        "forca": 88,
        "durabilidade": 130,
        "inteligencia": 55,
        "agressividade": 87,
        "ataque_assinatura": AtaquesKaiju.GARRAS
    },
    "LEATHERBACK": {
        "categoria": CategoriaKaiju.IV,
        "forca": 90,
        "durabilidade": 160,
        "inteligencia": 80,
        "agressividade": 83,
        "ataque_assinatura": AtaquesKaiju.EXPLOSAO
    },
    "RAIJU": {
        "categoria": CategoriaKaiju.IV,
        "forca": 85,
        "durabilidade": 140,
        "inteligencia": 65,
        "agressividade": 90,
        "ataque_assinatura": AtaquesKaiju.ACIDO
    },
    "OTACHI": {
        "categoria": CategoriaKaiju.IV,
        "forca": 80,
        "durabilidade": 160,
        "inteligencia": 70,
        "agressividade": 88,
        "ataque_assinatura": AtaquesKaiju.EXPLOSAO
    },
    "SLATTERN": {
        "categoria": CategoriaKaiju.V,
        "forca": 95,
        "durabilidade": 170,
        "inteligencia": 75,
        "agressividade": 85,
        "ataque_assinatura": AtaquesKaiju.EXPLOSAO
    }
}