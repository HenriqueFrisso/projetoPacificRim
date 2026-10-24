from datetime import timedelta

import dificuldade
import jaegers.factoryJaeger as fabrica_jaeger
import jaegers.jaeger as modulo_jaeger
import main
from centroOperacoes.cronometro import Cronometro
from jaegers.ataques import AtaquesJaeger, custo_arma
from jaegers.categorias import CategoriaJaeger, custo_geracao
from jaegers.factoryJaeger import FabricaJaeger, sugerir_nome
from repositorios.repositorios import RepositorioJaegers
from util import Separator


def test_dano_recebido_segue_a_dificuldade(novo_jaeger):
    for nivel, config in dificuldade.NIVEIS.items():
        main.aplicar_dificuldade(nivel)
        jaeger = novo_jaeger()  # MARK_I com durabilidade 100: dano chega inteiro
        jaeger.atacado(20)
        assert jaeger.saude == 100 - int(20 * config["dano_recebido_jaeger"]), nivel


def test_precos_de_arma_e_geracao_seguem_a_dificuldade():
    main.aplicar_dificuldade("facil")
    multiplicador = dificuldade.NIVEIS["facil"]["precos"]
    assert custo_arma(AtaquesJaeger.PULSO_ELETRICO) == round(2250 * multiplicador)
    assert custo_geracao(CategoriaJaeger.MARK_V) == round(5000 * multiplicador)


def test_data_de_liberacao_coincide_com_a_troca_de_fase():
    cronometro = Cronometro()
    for geracao in range(2, 6):
        cronometro.data_atual = cronometro.data_liberacao(geracao)
        assert cronometro.obter_categoria_atual() == geracao
        cronometro.data_atual -= timedelta(days=1)
        assert cronometro.obter_categoria_atual() == geracao - 1


def test_hangar_bloqueia_geracoes_futuras_e_armas_caras(novo_piloto, monkeypatch):
    pilotos = [novo_piloto("A"), novo_piloto("B")]
    monkeypatch.setattr(fabrica_jaeger, "selecionar_pilotos", lambda n: pilotos)

    def escolher(pergunta):
        if pergunta["type"] == "input":
            return pergunta["default"]
        return next(c["value"] for c in pergunta["choices"] if isinstance(c, dict))

    perguntas = []  # o hangar pergunta nome e geração na mesma chamada
    monkeypatch.setattr(fabrica_jaeger, "prompt", lambda lista: {
        q["name"]: (perguntas.append(q), escolher(q))[1] for q in lista})

    jaeger = FabricaJaeger().criar_jaeger(verba=800)
    geracoes, armas = perguntas[1]["choices"], perguntas[2]["choices"]
    assert sum(isinstance(g, Separator) for g in geracoes) == 4  # fase 1: só MARK_I liberada
    assert [a["value"] for a in armas] == [AtaquesJaeger.PUNHO_ENERGIZADO,
                                           AtaquesJaeger.LAMINA_DE_PLASMA]
    assert jaeger.categoria == CategoriaJaeger.MARK_I and jaeger in RepositorioJaegers.listar()


def test_nome_sugerido_nao_repete_jaeger_existente_nem_historico(novo_jaeger):
    todos = [f"{n} {s}" for n in fabrica_jaeger.NOMES_JAEGER for s in fabrica_jaeger.SOBRENOMES_JAEGER
             if f"{n} {s}" not in fabrica_jaeger.JAEGERS_HISTORICOS]
    for nome in todos[1:]:
        RepositorioJaegers.listar().append(type("J", (), {"nome": nome})())
    assert sugerir_nome() == todos[0]


def test_jaeger_destruido_pode_matar_ou_ferir_os_pilotos(novo_jaeger, monkeypatch):
    monkeypatch.setattr(modulo_jaeger, "random", lambda: 0.0)  # cai na chance de morte
    jaeger = novo_jaeger()
    jaeger.saude = 0
    assert [p.saude for p in jaeger.pilotos] == [0, 0]

    monkeypatch.setattr(modulo_jaeger, "random", lambda: 0.99)  # sobrevive ferido
    jaeger = novo_jaeger()
    jaeger.saude = 0
    assert all(40 <= p.saude <= 80 for p in jaeger.pilotos)
