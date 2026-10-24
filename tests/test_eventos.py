from datetime import timedelta

import main
from repositorios.repositorios import RepositorioPilotos


def test_doacao_e_corte_mexem_no_saldo_sem_negativar():
    campanha = main.Campanha(saldo=500)
    main.evento_doacao(campanha, fase=2)
    assert campanha.orcamento.saldo == 500 + 2000
    main.evento_corte(campanha, fase=5)  # corte de 4000 limitado ao saldo
    assert campanha.orcamento.saldo == 0


def test_veterano_entra_na_reserva_com_nivel():
    main.evento_veterano(main.Campanha(), fase=1)
    veterano, = RepositorioPilotos.listar()
    assert veterano.nivel == 2 and veterano.jaeger is None


def test_eventos_mudam_a_data_do_proximo_ataque():
    campanha = main.Campanha()
    data = campanha.proximo_ataque
    main.evento_ataque_adiantado(campanha, fase=1)
    assert campanha.proximo_ataque == data - timedelta(days=20)
    main.evento_descoberta(campanha, fase=1)
    assert campanha.proximo_ataque == data + timedelta(days=10)


def test_acidente_danifica_jaeger_e_moral_cura_feridos(novo_jaeger, novo_piloto):
    jaeger = novo_jaeger()
    ferido = novo_piloto("Ferido")
    ferido.saude = 50
    main.evento_acidente(main.Campanha(), fase=1)
    main.evento_moral(main.Campanha(), fase=1)
    assert jaeger.saude == 85
    assert ferido.saude == 70


def test_sorteio_respeita_chance_e_condicoes(monkeypatch):
    campanha = main.Campanha(evento_pendente=True)
    monkeypatch.setattr(main, "random", lambda: 0.99)
    main.sortear_evento(campanha)
    assert not campanha.evento_pendente  # passou a vez sem evento

    possiveis = []
    monkeypatch.setattr(main, "random", lambda: 0.0)
    monkeypatch.setattr(main, "choice", lambda lista: possiveis.extend(lista) or lista[0])
    main.sortear_evento(campanha)
    # sem Jaegers nem pilotos feridos, acidente e moral não podem acontecer
    assert main.evento_acidente not in possiveis and main.evento_moral not in possiveis
    assert main.evento_doacao in possiveis
