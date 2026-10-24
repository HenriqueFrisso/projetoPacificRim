import pilotos.factoryPiloto as fabrica_pilotos
import main
from centroOperacoes.cronometro import Cronometro
from jaegers.categorias import CategoriaJaeger, custo_geracao
from jaegers.factoryJaeger import FabricaJaeger
from jaegers.historicos import (custo_historico, equipes_para_recrutar, motivo_bloqueio,
                                recrutar)
from pilotos.factoryPiloto import FabricaPilotos
from repositorios.repositorios import RepositorioJaegers, RepositorioPilotos


def alistar(nome):
    tripulacao = recrutar(nome)
    RepositorioPilotos.listar().extend(tripulacao)
    return tripulacao


def ir_para_fase(fase):
    cronometro = Cronometro()
    cronometro.data_atual = cronometro.data_liberacao(fase)


def test_tripulacao_lendaria_chega_experiente_e_sincronizada():
    raleigh, mako = recrutar("Gipsy Danger")
    assert (raleigh.nome, mako.nome) == ("Raleigh Becket", "Mako Mori")
    assert raleigh.lendario and raleigh.nivel == 3 and raleigh.rotulo == "★ Raleigh Becket"
    assert raleigh.vinculos[mako.id]["batalhas"] == 5


def test_motivos_de_bloqueio_do_hangar(novo_piloto):
    assert motivo_bloqueio("Gipsy Danger", 2, 99999) == "liberado na fase 3"
    assert motivo_bloqueio("Gipsy Danger", 3, 99999) == "requer Raleigh Becket e Mako Mori"
    raleigh, mako = alistar("Gipsy Danger")
    assert motivo_bloqueio("Gipsy Danger", 3, 0) == "créditos insuficientes"
    assert motivo_bloqueio("Gipsy Danger", 3, 99999) is None
    mako.jaeger = object()
    assert motivo_bloqueio("Gipsy Danger", 3, 99999) == "Mako Mori já pilota outro Jaeger"
    mako.jaeger = None
    FabricaJaeger().criar_historico("Gipsy Danger")
    assert motivo_bloqueio("Gipsy Danger", 3, 99999) == "já está em serviço"


def test_crimson_typhoon_precisa_dos_tres_irmaos(novo_piloto):
    alistar("Crimson Typhoon")
    crimson = FabricaJaeger().criar_historico("Crimson Typhoon")
    assert [p.nome for p in crimson.pilotos] == ["Cheung Wei", "Hu Wei", "Jin Wei"]
    assert crimson.tripulacao_necessaria == 3 and crimson.tripulacao_completa

    hu = crimson.pilotos[1]
    crimson.remover_piloto(hu)
    assert not crimson.tripulacao_completa and crimson not in [main.escolher_jaeger()]
    assert crimson.adicionar_piloto(novo_piloto("Substituto"))
    assert crimson.tripulacao_completa and crimson.inteligencia > 0


def test_lenda_morta_ou_ja_recrutada_nao_volta():
    assert "Cherno Alpha" in equipes_para_recrutar(1)
    assert "Gipsy Danger" not in equipes_para_recrutar(2)  # geração ainda bloqueada
    assert "Cherno Alpha" not in equipes_para_recrutar(1, caidos=["Sasha Kaidanovsky"])
    alistar("Cherno Alpha")
    assert "Cherno Alpha" not in equipes_para_recrutar(1)


def test_academia_oferece_a_equipe_sem_reprovar(monkeypatch, responder):
    monkeypatch.setattr(fabrica_pilotos, "random", lambda: 0.99)  # reprovaria um candidato comum
    perguntas = responder(fabrica_pilotos, ["lendarios"])
    equipe = ("Cherno Alpha", recrutar("Cherno Alpha"))

    novos = FabricaPilotos().treinar_pilotos(equipe)

    assert perguntas[0]["choices"][0]["value"] == "lendarios"
    assert RepositorioPilotos.listar() == novos and len(novos) == 2


def test_evento_traz_a_tripulacao_lendaria():
    mensagem = main.evento_lendas(main.Campanha(), fase=1)
    assert "Cherno Alpha" in mensagem
    assert {p.nome for p in RepositorioPilotos.listar()} == {"Aleksis Kaidanovsky", "Sasha Kaidanovsky"}


def test_hangar_constroi_historico_e_cobra_o_modelo(responder):
    ir_para_fase(3)
    alistar("Gipsy Danger")
    orcamento = main.Orcamento(50000)
    perguntas = responder(main, ["Gipsy Danger"])

    main.construir_jaeger(orcamento)

    gipsy = RepositorioJaegers.listar()[0]
    assert gipsy.nome == "Gipsy Danger" and gipsy.categoria == CategoriaJaeger.MARK_III
    custo = main.CUSTO_JAEGER + custo_geracao(CategoriaJaeger.MARK_III) + custo_historico("Gipsy Danger")
    assert orcamento.saldo == 50000 - custo
    bloqueados = [str(getattr(c, "_line", "")) for c in perguntas[0]["choices"] if not isinstance(c, dict)]
    assert any("Crimson Typhoon" in b and "liberado na fase 4" in b for b in bloqueados)
