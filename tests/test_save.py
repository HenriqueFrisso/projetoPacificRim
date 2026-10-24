import dificuldade
import main
from centroOperacoes.cronometro import Cronometro
from repositorios.repositorios import RepositorioJaegers, RepositorioPilotos


def test_salvar_e_carregar_preserva_a_campanha(novo_jaeger):
    main.aplicar_dificuldade("dificil")
    jaeger = novo_jaeger()
    a, b = jaeger.pilotos
    a.registrar_batalha([a, b])
    campanha = main.Campanha(cidades_perdidas=2, historico=[{"resultado": "vitoria"}],
                             memorial=[{"nome": "Caído"}])
    data = Cronometro().data_atual
    main.salvar_campanha(campanha)

    RepositorioPilotos.listar().clear()
    RepositorioJaegers.listar().clear()
    main.aplicar_dificuldade("normal")
    restaurada = main.restaurar_campanha(main.ler_save())

    jaeger2 = RepositorioJaegers.listar()[0]
    a2, b2 = RepositorioPilotos.listar()
    assert dificuldade.chave == "dificil" and Cronometro().data_atual == data
    assert restaurada.cidades_perdidas == 2 and restaurada.orcamento.saldo == campanha.orcamento.saldo
    assert restaurada.historico == campanha.historico and restaurada.memorial == campanha.memorial
    assert jaeger2.pilotos == [a2, b2] and a2.jaeger is jaeger2  # ligações mantidas
    assert a2.vinculos[b2.id]["batalhas"] == 1


def test_save_corrompido_e_ignorado(capsys):
    main.ARQUIVO_SAVE.write_bytes(b"isto nao e um save")
    assert main.ler_save() is None
    assert "corrompido" in capsys.readouterr().out


def test_continuar_campanha_salva(novo_jaeger, responder):
    novo_jaeger()
    main.salvar_campanha(main.Campanha(cidades_perdidas=1))
    RepositorioJaegers.listar().clear()
    perguntas = responder(main, [True])

    campanha = main.iniciar_campanha()

    assert "Continuar campanha" in perguntas[0]["choices"][0]["name"]
    assert campanha.cidades_perdidas == 1 and len(RepositorioJaegers.listar()) == 1
