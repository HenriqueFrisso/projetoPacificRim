from util import *

if __name__ == "__main__":
    ...
    # historia.introducao()
    # CentroOperacoes.selecionar_acao()
    # FabricaPilotos().treinar_pilotos()
    # p1 = FabricaPilotos().treinar_pilotos()
    # p1.saude = 70
    # FabricaPilotos().treinar_pilotos()
    # FabricaPilotos().treinar_pilotos()
    # FabricaJaeger().criar_jaeger()
    # FabricaJaeger().criar_jaeger()
    # j1.vida = 0
    # FabricaJaeger().criar_jaeger()

    # for jaeger in RepositorioJaegers.listar():
    #     print(jaeger.info())
    #     print("----------")

    Cronometro().atualizar_tempo(4500)
    FabricaPilotos().treinar_pilotos()
    FabricaPilotos().treinar_pilotos()
    j1 = FabricaJaeger().criar_jaeger()
    k1 = FabricaKaiju().criarKaijuCategoria(5)
    print(j1.info())
    print(k1.info())
    batalha(j1, k1)
    print("")
    print(j1.info())
    for kaiju in RepositorioKaijusDerrotados.listar():
        print(kaiju.info())

    for piloto in RepositorioPilotos.listar():
        print(piloto.info())
        print("----------")