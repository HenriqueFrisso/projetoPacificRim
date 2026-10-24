import pilotos.factoryPiloto as fabrica_pilotos
import pilotos.piloto as modulo_piloto
from pilotos.conexaoPilotos import calcular_bonus_vinculo, calcular_conexao_individual
from pilotos.factoryPiloto import FabricaPilotos
from pilotos.piloto import (INTELIGENCIA_MAXIMA, EstadoPiloto, Personalidade,
                            selecionar_pilotos)
from repositorios.repositorios import RepositorioPilotos


def test_recuperacao_depende_da_personalidade(novo_piloto):
    calmo = novo_piloto("Calmo", Personalidade.CALMO)
    rebelde = novo_piloto("Rebelde", Personalidade.REBELDE)
    calmo.saude = rebelde.saude = 40

    assert calmo.recuperar(45) == 27   # 45 dias * 0,4 * 1,5
    assert rebelde.recuperar(45) == 11  # 45 dias * 0,4 * 0,6
    assert calmo.estado == EstadoPiloto.FERIDO


def test_recuperacao_para_em_100_e_reativa(novo_piloto):
    piloto = novo_piloto(personalidade=Personalidade.CALMO)
    piloto.saude = 95
    assert piloto.recuperar(100) == 5
    assert piloto.saude == 100 and piloto.estado == EstadoPiloto.ATIVO


def test_saudavel_ou_fora_de_combate_nao_recupera(novo_piloto):
    saudavel, caido = novo_piloto("Ok"), novo_piloto("Caído")
    caido.saude = 0
    assert saudavel.recuperar(100) == 0
    assert caido.recuperar(100) == 0 and caido.saude == 0


def test_experiencia_sobe_nivel_e_inteligencia(novo_piloto):
    piloto = novo_piloto(inteligencia=90)
    assert piloto.ganhar_experiencia(99) == 0 and piloto.nivel == 1
    assert piloto.ganhar_experiencia(1) == 1
    assert piloto.nivel == 2 and piloto.inteligencia == 94


def test_inteligencia_tem_limite(novo_piloto):
    piloto = novo_piloto(inteligencia=128)
    piloto.ganhar_experiencia(500)
    assert piloto.inteligencia == INTELIGENCIA_MAXIMA


def test_vinculo_fortalece_a_ponte_neural(novo_piloto):
    a, b = novo_piloto("A", Personalidade.CALMO), novo_piloto("B")
    antes = calcular_conexao_individual(a, b)
    for _ in range(3):
        a.registrar_batalha([a, b])
    assert a.vinculos[b.id]["batalhas"] == 3
    assert calcular_conexao_individual(a, b) - antes == 6


def test_bonus_de_vinculo_tem_limite(novo_piloto):
    a, b = novo_piloto("A"), novo_piloto("B")
    for _ in range(50):
        a.registrar_batalha([a, b])
    assert calcular_bonus_vinculo(a, b) == 20


def test_treinamento_pode_reprovar(monkeypatch, responder):
    responder(fabrica_pilotos, lambda pergunta: pergunta["choices"][0]["value"])
    monkeypatch.setattr(fabrica_pilotos, "random", lambda: 0.99)
    assert FabricaPilotos().treinar_pilotos() is None
    assert RepositorioPilotos.listar() == []

    monkeypatch.setattr(fabrica_pilotos, "random", lambda: 0.0)
    piloto = FabricaPilotos().treinar_pilotos()
    assert RepositorioPilotos.listar() == [piloto]


def test_previa_da_ponte_permite_trocar_e_cancelar(novo_piloto, responder):
    a, b, c = novo_piloto("A"), novo_piloto("B"), novo_piloto("C")
    perguntas = responder(modulo_piloto, [[c, a], "trocar", [a, b], "confirmar", [a, b], "cancelar"])

    assert selecionar_pilotos(2) == [a, b]
    assert selecionar_pilotos(2) is None
    assert "Ponte neural prevista" in perguntas[1]["message"]


def test_previa_usa_o_parceiro_que_ja_esta_no_jaeger(novo_piloto, responder):
    parceiro, novo = novo_piloto("Parceiro"), novo_piloto("Novo")
    parceiro.jaeger = object()  # ocupado: não aparece entre os livres
    perguntas = responder(modulo_piloto, [[novo], "confirmar"])
    assert selecionar_pilotos(1, parceiro=parceiro) == [novo]
    assert len(perguntas[0]["choices"]) == 1
