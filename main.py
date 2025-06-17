from util import *

if __name__ == "__main__":
    ...

    FabricaPilotos().treinar_pilotos()
    p1 = FabricaPilotos().treinar_pilotos()
    p1.saude = 70
    # centroOperacoes = CentroOperacoes()
    # centroOperacoes.selecionar_acao()
    # FabricaPilotos().treinar_pilotos()
    # FabricaPilotos().treinar_pilotos()
    FabricaJaeger().criar_jaeger()
    # FabricaJaeger().criar_jaeger()
    # j1.vida = 0
    # FabricaJaeger().criar_jaeger()

    for jaeger in RepositorioJaegers.listar():
        print(jaeger.info())
        print("----------")
    # for piloto in RepositorioPilotos.listar():
    #     print(piloto.info())
    #     print("----------")
