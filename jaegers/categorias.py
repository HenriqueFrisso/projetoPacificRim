from util import *

class CategoriaJaeger(Enum):
    MARK_I = 1
    MARK_II = 2
    MARK_III = 3
    MARK_IV = 4
    MARK_V = 5


# Estratégias que modificam atributos
def estrategia_mark_i(jaeger): return int(jaeger._forca), int(jaeger._durabilidade)

def estrategia_mark_ii(jaeger): return (jaeger._forca + 12), (jaeger._durabilidade + 11)

def estrategia_mark_iii(jaeger): return (jaeger._forca + 25), (jaeger._durabilidade + 34)

def estrategia_mark_iv(jaeger): return (jaeger._forca + 46), (jaeger._durabilidade + 53)

def estrategia_mark_v(jaeger): return (jaeger._forca + 58), (jaeger._durabilidade + 78)

estrategias_jaeger = {
    CategoriaJaeger.MARK_I: estrategia_mark_i,
    CategoriaJaeger.MARK_II: estrategia_mark_ii,
    CategoriaJaeger.MARK_III: estrategia_mark_iii,
    CategoriaJaeger.MARK_IV: estrategia_mark_iv,
    CategoriaJaeger.MARK_V: estrategia_mark_v,
}