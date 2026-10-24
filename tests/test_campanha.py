import random

import pytest

import centroOperacoes.historia as historia
import main
from centroOperacoes.cronometro import Cronometro
from jaegers.ataques import AtaquesJaeger
from repositorios.repositorios import RepositorioKaijusDerrotados, RepositorioPilotos


@pytest.mark.parametrize("nivel", ["facil", "normal", "dificil"])
def test_inicio_permite_dois_pilotos_e_um_jaeger(nivel):
    main.aplicar_dificuldade(nivel)
    assert main.Orcamento().saldo >= 2 * main.CUSTO_TREINAMENTO + main.CUSTO_JAEGER


def test_ataque_agendado_pelo_intervalo_da_fase_e_ritmo():
    main.aplicar_dificuldade("dificil")
    assert main.Campanha().dias_ate_ataque() == round(200 * 0.8)
    cronometro = Cronometro()
    cronometro.data_atual = cronometro.data_liberacao(5)
    assert main.Campanha().dias_ate_ataque() == round(80 * 0.8)


def test_alerta_sem_defesa_custa_cidade_e_reagenda(responder):
    campanha = main.Campanha()
    saldo = campanha.orcamento.saldo
    Cronometro().data_atual = campanha.proximo_ataque
    responder(main, [None])

    main.alerta_kaiju(campanha)

    assert campanha.cidades_perdidas == 1
    assert campanha.orcamento.saldo == saldo - main.CUSTO_DERROTA
    assert campanha.historico[-1]["resultado"] == "desprotegida"
    assert campanha.dias_ate_ataque() > 0 and campanha.evento_pendente


def test_vitoria_paga_recompensa_e_da_experiencia(novo_jaeger, responder):
    random.seed(1)
    jaeger = novo_jaeger(forca=600, durabilidade=600, geracao=5, ataque=AtaquesJaeger.PULSO_ELETRICO)
    campanha = main.Campanha()
    saldo = campanha.orcamento.saldo
    responder(main, [jaeger])

    main.alerta_kaiju(campanha)

    assert campanha.historico[-1]["resultado"] == "vitoria"
    assert campanha.orcamento.saldo == saldo + main.RECOMPENSA_POR_CATEGORIA  # categoria I
    assert all(p.experiencia == main.EXPERIENCIA_BATALHA["vitoria"] for p in jaeger.pilotos)
    assert len(RepositorioKaijusDerrotados.listar()) == 1


def test_piloto_morto_vai_para_o_memorial(novo_jaeger, responder):
    random.seed(3)
    jaeger = novo_jaeger(forca=1, durabilidade=50)
    for piloto in jaeger.pilotos:
        piloto.saude = 1
    tripulacao = list(jaeger.pilotos)
    campanha = main.Campanha()
    responder(main, [jaeger])

    main.alerta_kaiju(campanha)

    assert campanha.historico[-1]["resultado"] == "derrota"
    assert campanha.cidades_perdidas == 1
    assert [caido["nome"] for caido in campanha.memorial] == [p.nome for p in tripulacao]
    assert not any(p in RepositorioPilotos.listar() for p in tripulacao)


def test_reparo_oferece_pacotes_ate_o_saldo(novo_jaeger, responder):
    jaeger = novo_jaeger()
    jaeger.saude = 40
    perguntas = responder(main, [0, 0])
    saldo_curto = 40 * main.CUSTO_REPARO_POR_INTEGRIDADE  # cobre só 40 pontos
    main.escolher_integridade_reparo(jaeger, main.Orcamento(100000))
    main.escolher_integridade_reparo(jaeger, main.Orcamento(saldo_curto))
    rico, pobre = ([c["value"] for c in p["choices"]] for p in perguntas)
    assert rico == [10, 25, 50, 60, 0]
    assert pobre == [10, 25, 40, 0]


def test_perder_cidades_demais_encerra_em_derrota(monkeypatch, responder):
    campanha = main.Campanha(cidades_perdidas=main.dificuldade.atual["cidades_toleradas"])
    monkeypatch.setattr(main, "iniciar_campanha", lambda: campanha)
    responder(historia, ["Sair"])
    main.salvar_campanha(campanha)

    assert main.painel() == "Sair"
    assert not main.ARQUIVO_SAVE.exists()


def test_operacao_pitfall_vencida_leva_ao_final_vitorioso(novo_jaeger, monkeypatch, responder):
    jaeger = novo_jaeger()
    monkeypatch.setattr(main, "iniciar_campanha", lambda: main.Campanha())
    monkeypatch.setattr(main, "escolher_jaeger", lambda: jaeger)
    monkeypatch.setattr(main, "batalha_por_turnos", lambda j, k: True)
    perguntas = responder(historia, ["Reiniciar história"])
    cronometro = Cronometro()
    cronometro.data_atual = cronometro.data_fim

    assert main.painel() == "Reiniciar história"
    assert perguntas[0]["message"] == "Fim da jornada. O que deseja fazer?"
