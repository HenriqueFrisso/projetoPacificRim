from util import *

# === Enum de Categorias Kaiju ===
class CategoriaKaiju(IntEnum):
    DESCONHECIDA = 0
    I = 1
    II = 2
    III = 3
    IV = 4
    V = 5

# === Funções de Categorias Kaiju ===
def estrategiaDesconhecida(kaiju): return int(kaiju.inteligencia), int(kaiju.agressividade)
def estrategiaCategoria_I(kaiju): return int(kaiju.inteligencia * 0.8), int(kaiju.agressividade * 0.7)
def estrategiaCategoria_II(kaiju): return int(kaiju.inteligencia * 0.8), int(kaiju.agressividade * 0.9)
def estrategiaCategoria_III(kaiju): return int(kaiju.inteligencia * 1.1), int(kaiju.agressividade * 0.8)
def estrategiaCategoria_IV(kaiju): return int(kaiju.inteligencia * 1.0), int(kaiju.agressividade * 1.1)
def estrategiaCategoria_V(kaiju): return int(kaiju.inteligencia * 1.2), int(kaiju.agressividade * 1.2)

# === Dicionário de Categorias Kaiju ===
estrategias_kaiju = {
    CategoriaKaiju.DESCONHECIDA: estrategiaDesconhecida,
    CategoriaKaiju.I: estrategiaCategoria_I,
    CategoriaKaiju.II: estrategiaCategoria_II,
    CategoriaKaiju.III: estrategiaCategoria_III,
    CategoriaKaiju.IV: estrategiaCategoria_IV,
    CategoriaKaiju.V: estrategiaCategoria_V,
}
