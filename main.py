import historia
from kaijus import *
from jaegers import *
from pilotos import *
from repositorios import *

if __name__ == "__main__":
    ...
    #historia.introducao()
    treino = FabricaPilotos()
    treino.treinar_pilotos()
    treino.treinar_pilotos()
    treino.treinar_pilotos()
    treino.treinar_pilotos()
    fabrica = FabricaJaeger()
    fabrica.criar_jaeger()
    repositorio_jaeger = RepositorioJaegers()
    lista = repositorio_jaeger.listar()
    for jaeger in lista:
        print(jaeger.info())
