"""Ponto de entrada da campanha interativa de Pacific Rim."""

import json
import pickle
from collections import Counter
from datetime import timedelta
from pathlib import Path
from random import choice, random
from time import sleep

from centroOperacoes.cronometro import Cronometro
from centroOperacoes.historia import (contar, desativacao_jaegers, final_derrota,
                                      final_vitorioso, narrar, reativacao_jaegers)
from jaegers.ataques import custo_arma
from jaegers.categorias import CategoriaJaeger, custo_geracao
from jaegers.historicos import (JAEGERS_HISTORICOS, custo_historico, equipes_para_recrutar,
                                motivo_bloqueio, recrutar, sortear_oferta)
from jaegers.historicos import DADOS as DADOS_HISTORICOS
from jaegers.historicos import descrever as descrever_historico
from jaegers.factoryJaeger import FabricaJaeger
from jaegers.jaeger import EstadoJaeger
from kaijus.categorias import CategoriaKaiju
from kaijus.factoryKaiju import FabricaKaiju
from pilotos.factoryPiloto import FabricaPilotos
from pilotos.piloto import selecionar_pilotos
from repositorios.repositorios import (RepositorioJaegers, RepositorioKaijusDerrotados,
                                       RepositorioPilotos)
from audio import efeito
from util import Separator, evento_batalha, limpar_tela, prompt
import dificuldade

ARQUIVO_PRECOS = Path(__file__).with_name("precos.json")
ARQUIVO_SAVE = Path(__file__).with_name("campanha.sav")


def carregar_precos():
    """Lê a tabela editável de custos usada pela campanha."""
    with ARQUIVO_PRECOS.open(encoding="utf-8") as arquivo:
        return json.load(arquivo)


PRECOS = carregar_precos()
INTERVALO_ENTRE_GOLPES = PRECOS["intervalo_entre_golpes_segundos"]
DIAS_POR_ACAO = PRECOS["dias_por_acao"]
INTERVALO_ATAQUES = PRECOS["intervalo_ataques_dias"]
EXPERIENCIA_BATALHA = PRECOS["experiencia"]


def aplicar_dificuldade(chave):
    """Recalcula créditos, custos e recompensas conforme o nível escolhido."""
    global CREDITOS_INICIAIS, CUSTO_SELECAO_PILOTO, CUSTO_CONCLUSAO_TREINAMENTO
    global CUSTO_TREINAMENTO, CUSTO_JAEGER, CUSTO_REPARO_POR_INTEGRIDADE
    global CUSTO_DERROTA, RECOMPENSA_POR_CATEGORIA
    dificuldade.definir(chave)
    nivel = dificuldade.atual

    def preco(valor):
        return round(valor * nivel["precos"])

    CREDITOS_INICIAIS = round(PRECOS["creditos_iniciais"] * nivel["creditos"])
    CUSTO_SELECAO_PILOTO = preco(PRECOS["treinamento"]["selecao"])
    CUSTO_CONCLUSAO_TREINAMENTO = preco(PRECOS["treinamento"]["conclusao"])
    CUSTO_TREINAMENTO = CUSTO_SELECAO_PILOTO + CUSTO_CONCLUSAO_TREINAMENTO
    CUSTO_JAEGER = preco(PRECOS["jaeger"])
    CUSTO_REPARO_POR_INTEGRIDADE = preco(PRECOS["reparo_por_integridade"])
    CUSTO_DERROTA = preco(PRECOS["penalidade_derrota"])
    RECOMPENSA_POR_CATEGORIA = round(PRECOS["recompensa_por_categoria_kaiju"] * nivel["recompensa"])


aplicar_dificuldade("normal")


def escolher_dificuldade():
    cabecalho("NÍVEL DE AMEAÇA")
    chave = prompt([{
        "type": "list", "name": "nivel", "message": "Escolha a dificuldade da campanha:",
        "choices": [
            {"name": (f"{n['nome']} | créditos x{n['creditos']} | preços x{n['precos']} | "
                      f"dano recebido x{n['dano_recebido_jaeger']} | "
                      f"aprovação {n['chance_treinamento']:.0%}"),
             "value": chave}
            for chave, n in dificuldade.NIVEIS.items()
        ],
    }])["nivel"]
    aplicar_dificuldade(chave)


class Orcamento:
    """Controla os créditos do Shatterdome durante a campanha atual."""

    def __init__(self, saldo=None):
        self.saldo = CREDITOS_INICIAIS if saldo is None else saldo

    def possui(self, valor):
        return self.saldo >= valor

    def debitar(self, valor):
        if not self.possui(valor):
            return False
        self.saldo -= valor
        return True

    def creditar(self, valor):
        self.saldo += valor


class Campanha:
    """Estado da campanha além do efetivo: créditos, próximo ataque e cidades perdidas."""

    def __init__(self, saldo=None, cidades_perdidas=0, programa_reativado=False,
                 proximo_ataque=None, historico=None, memorial=None, evento_pendente=False):
        self.orcamento = Orcamento(saldo)
        self.cidades_perdidas = cidades_perdidas
        self.programa_reativado = programa_reativado
        self.historico = historico or []  # uma entrada por ataque Kaiju
        self.memorial = memorial or []  # pilotos mortos em combate
        self.evento_pendente = evento_pendente  # sorteia um evento após cada ataque
        self.proximo_ataque = proximo_ataque
        if proximo_ataque is None:
            self.agendar_proximo_ataque()

    def agendar_proximo_ataque(self):
        """Os ataques ficam mais frequentes a cada fase da guerra."""
        cronometro = Cronometro()
        fase = max(cronometro.obter_categoria_atual(), 1)
        dias = round(INTERVALO_ATAQUES[fase - 1] * dificuldade.atual["ritmo_ataques"])
        self.proximo_ataque = cronometro.data_atual + timedelta(days=dias)

    def dias_ate_ataque(self):
        return max((self.proximo_ataque - Cronometro().data_atual).days, 0)


campanha_atual = None  # campanha em andamento, lida pelo painel da interface gráfica


def mostrar_creditos(orcamento):
    print(f"\nCRÉDITOS DO SHATTERDOME: ₡ {orcamento.saldo:,}".replace(",", "."))


def ha_jaeger_operacional():
    """Um Jaeger só protege a costa se estiver íntegro o bastante e tripulado."""
    return any(
        jaeger.estado in (EstadoJaeger.ATIVO, EstadoJaeger.DANIFICADO)
        and jaeger.saude > 0
        and jaeger.tripulacao_completa
        for jaeger in RepositorioJaegers.listar()
    )


def campanha_sem_recursos(orcamento):
    sem_opcao_de_recrutamento = orcamento.saldo < CUSTO_TREINAMENTO
    sem_opcao_de_construcao = orcamento.saldo < CUSTO_JAEGER
    return (sem_opcao_de_recrutamento
            and sem_opcao_de_construcao
            and not ha_jaeger_operacional())


def pausar(mensagem="Pressione Enter para continuar..."):
    input(f"\n{mensagem}")


def cabecalho(titulo):
    limpar_tela()
    print("=" * 58)
    print(f"  {titulo}")
    print("=" * 58)


def prologo():
    contar("prologo")
    pausar("Assuma o comando pressionando Enter...")


def treinar_piloto(orcamento):
    cabecalho("ACADEMIA DE PILOTOS")
    print(f"Custo do treinamento: ₡ {CUSTO_TREINAMENTO:,}".replace(",", "."))
    mostrar_creditos(orcamento)
    if not orcamento.possui(CUSTO_TREINAMENTO):
        print("Créditos insuficientes para financiar um novo piloto.")
        pausar()
        return
    # A simulação e a triagem dos candidatos já consomem recursos, mesmo que
    # o comandante decida não contratar ninguém ao final.
    orcamento.debitar(CUSTO_SELECAO_PILOTO)
    passar_dias(DIAS_POR_ACAO["treinamento"], animar=False)
    equipe = sortear_oferta(fase_atual(), caidos(campanha_atual))
    piloto = FabricaPilotos().treinar_pilotos(equipe and (equipe, recrutar(equipe)))
    if piloto:
        orcamento.debitar(CUSTO_CONCLUSAO_TREINAMENTO)
        efeito("treino_ok")
        novos = piloto if isinstance(piloto, list) else [piloto]
        print(f"\n{', '.join(p.nome for p in novos)} agora faz parte do programa Jaeger.")
        print(f"₡ {CUSTO_TREINAMENTO:,} debitados pela seleção e treinamento.".replace(",", "."))
    else:
        efeito("treino_falha")
        print("Treinamento não concluído. Os créditos da seleção já foram utilizados.")
    pausar()


def construir_jaeger(orcamento):
    cabecalho("HANGAR DE CONSTRUÇÃO")
    print(f"Custo de construção: ₡ {CUSTO_JAEGER:,} + geração + arma assinatura".replace(",", "."))
    mostrar_creditos(orcamento)
    if not orcamento.possui(CUSTO_JAEGER):
        print("Créditos insuficientes para construir um Jaeger.")
        pausar()
        return
    if len(RepositorioPilotos.listar()) < 2:
        print("São necessários pelo menos dois pilotos para iniciar a construção.")
        pausar()
        return
    print("Novas gerações são liberadas com o avanço da guerra.")
    print("Jaegers históricos (★) exigem a tripulação original do filme.")
    modelo = escolher_modelo(orcamento)
    if modelo:
        jaeger = FabricaJaeger().criar_historico(modelo)
        extra = custo_historico(modelo)
    else:
        print("Armas mais caras do que o saldo permite não aparecem na lista.")
        jaeger = FabricaJaeger().criar_jaeger(verba=orcamento.saldo - CUSTO_JAEGER)
        extra = custo_arma(jaeger.ataque_assinatura) if jaeger else 0
    if jaeger:
        custo = CUSTO_JAEGER + custo_geracao(jaeger.categoria) + extra
        orcamento.debitar(custo)
        passar_dias(DIAS_POR_ACAO["construcao"], animar=False)
        efeito("construcao")
        print("\nLançamento concluído. Um novo defensor está pronto.")
        print(jaeger.info())
        print(f"₡ {custo:,} debitados.".replace(",", "."))
    else:
        print("Construção cancelada. Nenhum crédito foi gasto.")
    pausar()


def fase_atual():
    return max(Cronometro().obter_categoria_atual(), 1)


def caidos(campanha):
    """Nomes dos pilotos mortos: uma lenda morta nunca volta a ser recrutada."""
    return [caido["nome"] for caido in campanha.memorial] if campanha else []


def escolher_modelo(orcamento):
    """Jaeger padrão ou histórico; os históricos bloqueados aparecem com o motivo."""
    opcoes = [{"name": "Jaeger padrão (escolha pilotos, geração e arma)", "value": None}]
    for nome, dados in JAEGERS_HISTORICOS.items():
        verba = orcamento.saldo - CUSTO_JAEGER - custo_geracao(CategoriaJaeger(dados["geracao"]))
        motivo = motivo_bloqueio(nome, fase_atual(), verba)
        descricao = descrever_historico(nome)
        opcoes.append({"name": descricao, "value": nome} if motivo is None
                      else Separator(f"{descricao} — {motivo}"))
    return prompt([{"type": "list", "name": "modelo", "message": "Escolha o modelo do Jaeger:",
                    "choices": opcoes}])["modelo"]


def custo_reparo(jaeger):
    """O reparo custa créditos proporcionais à integridade perdida."""
    return (100 - jaeger.saude) * CUSTO_REPARO_POR_INTEGRIDADE


def escolher_integridade_reparo(jaeger, orcamento):
    """Retorna a quantidade de integridade a restaurar, ou zero ao cancelar."""
    dano = 100 - jaeger.saude
    maximo_por_saldo = orcamento.saldo // CUSTO_REPARO_POR_INTEGRIDADE
    maximo_reparo = min(dano, maximo_por_saldo)
    if maximo_reparo <= 0:
        return 0

    # Pacotes fixos menores que o máximo, mais o maior reparo que o saldo cobre.
    pacotes = sorted({p for p in (10, 25, 50) if p < maximo_reparo} | {maximo_reparo})

    def rotulo(pontos):
        titulo = "Reparo completo" if pontos == dano else f"+{pontos}% de integridade"
        custo = f"{pontos * CUSTO_REPARO_POR_INTEGRIDADE:,}".replace(",", ".")
        return f"{titulo} → {min(100, jaeger.saude + pontos)}% | ₡ {custo}"

    return prompt([{
        "type": "list", "name": "integridade", "message": "Escolha o reparo:",
        "choices": [{"name": rotulo(p), "value": p} for p in pacotes]
                   + [{"name": "Cancelar", "value": 0}],
    }])["integridade"]


def enfermaria_jaegers(orcamento):
    cabecalho("ENFERMARIA — OFICINA DE REPAROS")
    danificados = [j for j in RepositorioJaegers.listar()
                   if j.estado == EstadoJaeger.DANIFICADO and 0 < j.saude < 100]
    mostrar_creditos(orcamento)
    if not danificados:
        print("Nenhum Jaeger danificado aguarda reparos.")
        pausar()
        return

    resposta = prompt([{
        "type": "list", "name": "jaeger", "message": "Selecione uma unidade para reparar:",
        "choices": [
            {
                "name": (f"{j.nome} | integridade: {j.saude}% | "
                         f"máximo: ₡ {custo_reparo(j):,}").replace(",", "."),
                "value": j,
            }
            for j in danificados
        ] + [{"name": "Voltar sem reparar", "value": None}],
    }])
    jaeger = resposta["jaeger"]
    if jaeger is None:
        return

    integridade = escolher_integridade_reparo(jaeger, orcamento)
    if integridade == 0:
        print("Reparo cancelado.")
        pausar()
        return
    custo = integridade * CUSTO_REPARO_POR_INTEGRIDADE
    orcamento.debitar(custo)
    passar_dias(DIAS_POR_ACAO["reparo"], animar=False)
    efeito("reparo")
    jaeger.saude = min(100, jaeger.saude + integridade)
    print(f"{jaeger.nome} recuperou {integridade}% de integridade.")
    print(f"Integridade atual: {jaeger.saude}%.")
    print(f"₡ {custo:,} debitados da oficina.".replace(",", "."))
    pausar()


def desalocar_piloto(piloto):
    jaeger = piloto.jaeger
    jaeger.remover_piloto(piloto)
    print(f"{piloto.nome} foi desalocado. {jaeger.nome} está indisponível até completar a dupla.")


def ver_pilotos():
    while True:
        cabecalho("PILOTOS TREINADOS")
        pilotos = RepositorioPilotos.listar()
        if not pilotos:
            print("Nenhum piloto registrado.")
            pausar()
            return
        piloto = prompt([{
            "type": "list", "name": "piloto", "message": "Selecione um piloto:",
            "choices": [
                {"name": (f"{p.rotulo} ({p.nacionalidade}) | {p.personalidade} | {p.estado.name} | "
                          f"saúde {p.saude}% | Jaeger: {p.jaeger.nome if p.jaeger else 'nenhum'}"),
                 "value": p}
                for p in pilotos
            ] + [{"name": "Voltar", "value": None}],
        }])["piloto"]
        if piloto is None:
            return

        cabecalho(f"FICHA — {piloto.nome}")
        print(piloto.info())
        opcoes = [{"name": "Voltar à lista", "value": None}]
        if piloto.jaeger:
            opcoes.insert(0, {"name": f"Desalocar de {piloto.jaeger.nome}", "value": "desalocar"})
        if prompt([{"type": "list", "name": "acao", "message": "O que deseja fazer?",
                    "choices": opcoes}])["acao"] == "desalocar":
            desalocar_piloto(piloto)
            pausar()


def gerenciar_tripulacao():
    cabecalho("GESTÃO DE TRIPULAÇÃO")
    jaegers = [j for j in RepositorioJaegers.listar() if j.saude > 0]
    if not jaegers:
        print("Não há Jaegers que possam receber tripulação.")
        pausar()
        return

    resposta = prompt([{
        "type": "list", "name": "jaeger", "message": "Selecione um Jaeger:",
        "choices": [
            {
                "name": f"{j.nome} | {j.estado.name} | pilotos: {len(j.pilotos)}/{j.tripulacao_necessaria}",
                "value": j,
            }
            for j in jaegers
        ] + [{"name": "Voltar", "value": None}],
    }])
    jaeger = resposta["jaeger"]
    if jaeger is None:
        return

    cabecalho(f"TRIPULAÇÃO — {jaeger.nome}")
    print(jaeger.info())
    opcoes = [{"name": f"Desalocar {p.nome} ({p.nacionalidade}) | saúde {p.saude}%", "value": p}
              for p in jaeger.pilotos]
    if not jaeger.tripulacao_completa:
        opcoes.insert(0, {"name": "Alocar piloto", "value": "alocar"})
    opcoes.append({"name": "Voltar", "value": None})
    acao = prompt([{
        "type": "list", "name": "acao", "message": "O que deseja fazer?", "choices": opcoes,
    }])["acao"]

    if acao not in ("alocar", None):
        desalocar_piloto(acao)
    elif acao == "alocar":
        vagas = jaeger.tripulacao_necessaria - len(jaeger.pilotos)
        parceiro = jaeger.pilotos[0] if len(jaeger.pilotos) == 1 else None
        pilotos = selecionar_pilotos(vagas, parceiro=parceiro)
        if pilotos is None:
            print("Nenhum piloto foi alocado.")
        else:
            for piloto in pilotos:
                jaeger.adicionar_piloto(piloto)
            print(f"Tripulação atualizada: {len(jaeger.pilotos)}/{jaeger.tripulacao_necessaria} pilotos.")
            if jaeger.tripulacao_completa:
                print(f"Ponte neural sincronizada. {jaeger.nome} voltou a ficar disponível.")
            else:
                print(f"{jaeger.nome} continua indisponível até receber outro piloto.")
    pausar()


def escolher_jaeger(permitir_recusa=False):
    disponiveis = [j for j in RepositorioJaegers.listar()
                   if j.estado in (EstadoJaeger.ATIVO, EstadoJaeger.DANIFICADO)
                   and j.saude > 0 and j.tripulacao_completa]
    if not disponiveis and not permitir_recusa:
        return None
    if not disponiveis:
        print("\nNão há Jaegers operacionais para responder ao ataque.")
    recusa = [{"name": "Não enviar nenhum Jaeger (a cidade ficará desprotegida)", "value": None}]
    resposta = prompt([{
        "type": "list", "name": "jaeger", "message": "Escolha o Jaeger para a missão:",
        "choices": [{"name": (f"{j.nome} | {j.categoria.name} | Integridade: {j.saude}% | "
                              f"Ponte neural: {j.inteligencia}"), "value": j}
                    for j in disponiveis] + (recusa if permitir_recusa else []),
    }])
    return resposta["jaeger"]


def categoria_ameaca():
    """A ameaça acompanha a fase atual da guerra, sem gerar categoria zero."""
    return CategoriaKaiju(min(max(Cronometro().obter_categoria_atual(), 1), 5))


# Som de cada ataque assinatura (Jaegers e Kaijus).
SOM_ATAQUE = {
    "PUNHO_ENERGIZADO": "soco", "SOCO_NUCLEAR": "soco", "LAMINA_DE_PLASMA": "lamina",
    "LAMINAS_GIRATORIAS": "lamina", "RAIO_DE_ENERGIA": "raio", "PULSO_ELETRICO": "pulso",
    "PUNHO_TESLA": "pulso", "LAMINAS_STING": "lamina",
    "GARRAS": "garras", "ACIDO": "acido", "EXPLOSAO": "explosao",
}


def batalha_por_turnos(jaeger, kaiju):
    """Simula a batalha inteira após o comandante iniciar a missão."""
    turno = 1
    efeito("rugido")
    evento_batalha("inicio", jaeger=jaeger, kaiju=kaiju)
    sleep(INTERVALO_ENTRE_GOLPES)  # o rugido não atropela o primeiro golpe
    while jaeger.saude > 0 and kaiju.saude > 0:
        print(f"\n--- TURNO {turno} ---")
        print(f"{jaeger.nome}: {jaeger.saude:3d}% | {kaiju.nome}: {kaiju.saude:3d}%")
        print(f"{jaeger.nome} usa {jaeger.ataque_assinatura.name}!")
        saude_antes = kaiju.saude
        efeito(SOM_ATAQUE[jaeger.ataque_assinatura.name])
        jaeger.atacar(kaiju)
        efeito("impacto" if kaiju.saude < saude_antes else "erro", atraso=0.25)
        evento_batalha("golpe", atacante="jaeger", ataque=jaeger.ataque_assinatura.name,
                       dano=saude_antes - kaiju.saude)
        sleep(INTERVALO_ENTRE_GOLPES)
        if kaiju.saude <= 0:
            print(f"\n{kaiju.nome} caiu. A costa está segura.")
            efeito("vitoria")
            evento_batalha("fim", vencedor="jaeger")
            return True
        print(f"\n{kaiju.nome} responde com {kaiju.ataque_assinatura.name}!")
        saude_antes = jaeger.saude
        efeito(SOM_ATAQUE[kaiju.ataque_assinatura.name])
        kaiju.atacar(jaeger)
        efeito("impacto" if jaeger.saude < saude_antes else "erro", atraso=0.25)
        evento_batalha("golpe", atacante="kaiju", ataque=kaiju.ataque_assinatura.name,
                       dano=saude_antes - jaeger.saude)
        sleep(INTERVALO_ENTRE_GOLPES)
        if jaeger.saude <= 0:
            print(f"\n{jaeger.nome} foi destruído. O Shatterdome perdeu um defensor.")
            efeito("destruido")
            efeito("derrota", atraso=1.2)
            evento_batalha("fim", vencedor="kaiju")
            return False
        turno += 1


def passar_dias(dias, animar=True):
    """Avança o relógio e deixa os pilotos feridos se recuperarem nesse período."""
    Cronometro().atualizar_tempo(dias, animar)
    if not animar:
        print(f"{dias} dias se passaram.")
    for piloto in RepositorioPilotos.listar():
        pontos = piloto.recuperar(dias)
        if pontos:
            print(f"🩹 {piloto.nome} ({piloto.personalidade}) recuperou {pontos}% "
                  f"de saúde e está com {piloto.saude}%.")


def evoluir_pilotos(jaeger, tripulacao, venceu):
    """Pilotos ganham experiência e a dupla fortalece o vínculo a cada batalha."""
    experiencia = EXPERIENCIA_BATALHA["vitoria" if venceu else "derrota"]
    for piloto in tripulacao:
        piloto.registrar_batalha(tripulacao)
        if piloto.saude > 0 and piloto.ganhar_experiencia(experiencia):
            efeito("nivel", atraso=2.5)
            print(f"⭐ {piloto.nome} subiu para o nível {piloto.nivel}! "
                  f"Inteligência: {piloto.inteligencia}.")
    if jaeger.saude > 0:
        ponte_anterior = jaeger.inteligencia
        jaeger.recalcular_conexao()
        if jaeger.inteligencia != ponte_anterior:
            print(f"Ponte neural de {jaeger.nome}: {ponte_anterior} → {jaeger.inteligencia}.")


def perder_cidade(campanha):
    efeito("cidade")
    campanha.cidades_perdidas += 1
    penalidade = min(CUSTO_DERROTA, campanha.orcamento.saldo)
    campanha.orcamento.debitar(penalidade)
    print(f"\nUma cidade costeira foi devastada "
          f"({campanha.cidades_perdidas}/{dificuldade.atual['cidades_toleradas']}).")
    print(f"Custo da reconstrução: ₡ {penalidade:,}.".replace(",", "."))
    if penalidade < CUSTO_DERROTA:
        print("As reservas do Shatterdome foram completamente esgotadas.")


def alerta_kaiju(campanha):
    """Os Kaijus atacam na data marcada; ignorar ou perder custa uma cidade."""
    cabecalho("ALERTA KAIJU")
    efeito("sirene")
    categoria = categoria_ameaca()
    kaiju = FabricaKaiju().criarKaijuCategoria(categoria)
    print(f"Uma assinatura biológica foi detectada: {kaiju.nome} (categoria {categoria.name}).")
    jaeger = escolher_jaeger(permitir_recusa=True)
    registro = {"data": Cronometro().data_atual, "kaiju": kaiju.nome,
                "categoria": categoria.name, "jaeger": jaeger.nome if jaeger else None}
    campanha.historico.append(registro)
    if jaeger is None:
        registro["resultado"] = "desprotegida"
        print(f"\n{kaiju.nome} avança sem resistência.")
        passar_dias(DIAS_POR_ACAO["batalha"], animar=False)
        perder_cidade(campanha)
    else:
        pausar("Mobilize o Jaeger pressionando Enter...")
        tripulacao = list(jaeger.pilotos)
        venceu = batalha_por_turnos(jaeger, kaiju)
        registro["resultado"] = "vitoria" if venceu else "derrota"
        passar_dias(DIAS_POR_ACAO["batalha"])
        evoluir_pilotos(jaeger, tripulacao, venceu)
        for piloto in tripulacao:
            if piloto.saude <= 0:
                homenagear(campanha, piloto, jaeger, kaiju)
        if venceu:
            recompensa = categoria.value * RECOMPENSA_POR_CATEGORIA
            campanha.orcamento.creditar(recompensa)
            efeito("creditos", atraso=1.5)  # depois da fanfarra de vitória
            print(f"{kaiju.nome} foi derrotado. A costa está segura.")
            print(f"Recompensa da defesa costeira: ₡ {recompensa:,}.".replace(",", "."))
        else:
            perder_cidade(campanha)
    campanha.agendar_proximo_ataque()
    campanha.evento_pendente = True
    print(f"\nPróximo ataque Kaiju previsto em {campanha.dias_ate_ataque()} dias.")
    pausar()


def homenagear(campanha, piloto, jaeger, kaiju):
    """Piloto que chega a saúde zero morre: sai do efetivo e entra no memorial."""
    campanha.memorial.append({
        "nome": piloto.nome, "nacionalidade": str(piloto.nacionalidade),
        "personalidade": str(piloto.personalidade), "nivel": piloto.nivel,
        "jaeger": jaeger.nome, "kaiju": kaiju.nome, "data": Cronometro().data_atual,
    })
    RepositorioPilotos.listar().remove(piloto)
    efeito("morte", atraso=2.5)
    print(f"† {piloto.nome} morreu em combate a bordo de {jaeger.nome}.")


def ver_memorial(campanha):
    cabecalho("MEMORIAL DOS PILOTOS")
    if not campanha.memorial:
        print("Nenhum piloto caiu em combate. Que continue assim.")
    for caido in campanha.memorial:
        print(f"† {caido['nome']} ({caido['nacionalidade']}) — {caido['personalidade']}, "
              f"nível {caido['nivel']}")
        print(f"  Caiu em {caido['data'].strftime('%d/%m/%Y')} a bordo de {caido['jaeger']}, "
              f"contra {caido['kaiju']}.\n")
    pausar()


# === Eventos aleatórios entre ataques ===
EVENTOS = PRECOS["eventos"]


def formatar_creditos(valor):
    return f"₡ {valor:,}".replace(",", ".")


def evento_doacao(campanha, fase):
    valor = EVENTOS["doacao_por_fase"] * fase
    campanha.orcamento.creditar(valor)
    return f"Os governos do Pacífico aprovaram uma verba extra: +{formatar_creditos(valor)}."


def evento_corte(campanha, fase):
    valor = min(EVENTOS["corte_por_fase"] * fase, campanha.orcamento.saldo)
    campanha.orcamento.debitar(valor)
    return f"Um comitê da ONU cortou parte do orçamento do Shatterdome: -{formatar_creditos(valor)}."


def evento_veterano(campanha, fase):
    piloto = FabricaPilotos().criar_piloto_aleatorio()
    piloto.ganhar_experiencia(EVENTOS["xp_veterano"])
    RepositorioPilotos.adicionar(piloto)
    return (f"{piloto.nome} ({piloto.nacionalidade}), piloto veterano de nível {piloto.nivel}, "
            f"se apresentou como voluntário. Já está na reserva.")


def evento_ataque_adiantado(campanha, fase):
    campanha.proximo_ataque -= timedelta(days=EVENTOS["dias_adiantamento"])
    return (f"Os sensores da Fenda detectaram atividade anormal: o próximo ataque virá "
            f"{EVENTOS['dias_adiantamento']} dias antes do previsto.")


def evento_descoberta(campanha, fase):
    campanha.proximo_ataque += timedelta(days=EVENTOS["dias_atraso"])
    return (f"Os cientistas do Shatterdome desestabilizaram a Fenda por um tempo: o próximo "
            f"ataque foi adiado em {EVENTOS['dias_atraso']} dias.")


def evento_acidente(campanha, fase):
    jaeger = choice([j for j in RepositorioJaegers.listar() if j.saude > EVENTOS["dano_acidente"]])
    jaeger.saude -= EVENTOS["dano_acidente"]
    return (f"Uma pane no hangar danificou {jaeger.nome}: -{EVENTOS['dano_acidente']}% de "
            f"integridade.")


def evento_moral(campanha, fase):
    for piloto in RepositorioPilotos.listar():
        if 0 < piloto.saude < 100:
            piloto.saude = min(100, piloto.saude + EVENTOS["cura_moral"])
    return (f"Uma transmissão de agradecimento das cidades salvas elevou a moral: pilotos "
            f"feridos recuperam {EVENTOS['cura_moral']}% de saúde.")


def evento_lendas(campanha, fase):
    equipe = choice(equipes_para_recrutar(fase, caidos(campanha)))
    tripulacao = recrutar(equipe)
    for piloto in tripulacao:
        RepositorioPilotos.adicionar(piloto)
    return (f"★ {' e '.join(p.nome for p in tripulacao)}, a tripulação original do {equipe}, "
            f"se apresentou ao Shatterdome. Construa o {equipe} no hangar!")


# (evento, condição para poder acontecer agora)
EVENTOS_ALEATORIOS = [
    (evento_doacao, lambda campanha: True),
    (evento_corte, lambda campanha: campanha.orcamento.saldo > 0),
    (evento_veterano, lambda campanha: True),
    (evento_ataque_adiantado, lambda campanha: campanha.dias_ate_ataque() > EVENTOS["dias_adiantamento"]),
    (evento_descoberta, lambda campanha: True),
    (evento_acidente, lambda campanha: any(j.saude > EVENTOS["dano_acidente"]
                                           for j in RepositorioJaegers.listar())),
    (evento_moral, lambda campanha: any(0 < p.saude < 100 for p in RepositorioPilotos.listar())),
    # Lendas são raras: mesmo com equipe disponível, o evento só entra no sorteio às vezes.
    (evento_lendas, lambda campanha: random() < DADOS_HISTORICOS["chance_no_evento"]
                                     and bool(equipes_para_recrutar(fase_atual(), caidos(campanha)))),
]


def sortear_evento(campanha):
    """Depois de cada ataque, há uma chance de algo acontecer no Shatterdome."""
    campanha.evento_pendente = False
    if random() > EVENTOS["chance"]:
        return
    possiveis = [evento for evento, pode in EVENTOS_ALEATORIOS if pode(campanha)]
    mensagem = choice(possiveis)(campanha, max(Cronometro().obter_categoria_atual(), 1))
    cabecalho("NOTÍCIAS DO SHATTERDOME")
    efeito("evento")
    print(mensagem)
    pausar()


def operacao_pitfall():
    """Batalha final quando o relógio do fim do mundo zera; decide o desfecho."""
    contar("pitfall")
    cabecalho("OPERAÇÃO PITFALL")
    jaeger = escolher_jaeger()
    if not jaeger:
        print("\nNenhum Jaeger operacional pode descer até a Fenda.")
        pausar()
        return final_derrota()
    kaiju = FabricaKaiju().criarKaijuCategoria(CategoriaKaiju.V)
    print(f"{kaiju.nome} (categoria V) guarda a entrada da Fenda.")
    pausar("Inicie a descida pressionando Enter...")
    venceu = batalha_por_turnos(jaeger, kaiju)
    pausar()
    return final_vitorioso() if venceu else final_derrota()


def nova_campanha():
    RepositorioPilotos.listar().clear()
    RepositorioJaegers.listar().clear()
    RepositorioKaijusDerrotados.listar().clear()
    Cronometro().iniciar_cronometro()


RESULTADOS = {"vitoria": "VITÓRIA", "derrota": "DERROTA", "desprotegida": "SEM DEFESA"}


def ver_estatisticas(campanha):
    cabecalho("ESTATÍSTICAS E HISTÓRICO")
    historico = campanha.historico
    contagem = Counter(batalha["resultado"] for batalha in historico)
    print(f"Ataques Kaiju enfrentados: {len(historico)}")
    print(f"Vitórias: {contagem['vitoria']} | Derrotas: {contagem['derrota']} | "
          f"Cidades sem defesa: {contagem['desprotegida']}")
    print(f"Cidades perdidas: {campanha.cidades_perdidas}/{dificuldade.atual['cidades_toleradas']}")
    lutas = contagem["vitoria"] + contagem["derrota"]
    if lutas:
        print(f"Taxa de vitória em combate: {contagem['vitoria'] / lutas:.0%}")

    print("\nKAIJUS DERROTADOS")
    kaijus = RepositorioKaijusDerrotados.listar()
    if not kaijus:
        print("Nenhum ainda.")
    por_categoria = Counter(kaiju.categoria.name for kaiju in kaijus)
    for categoria, total in sorted(por_categoria.items(), key=lambda item: CategoriaKaiju[item[0]]):
        nomes = Counter(kaiju.nome for kaiju in kaijus if kaiju.categoria.name == categoria)
        lista = ", ".join(f"{nome} x{n}" if n > 1 else nome for nome, n in nomes.items())
        print(f"Categoria {categoria}: {total} — {lista}")

    vitorias_jaeger = Counter(b["jaeger"] for b in historico if b["resultado"] == "vitoria")
    if vitorias_jaeger:
        print("\nJAEGERS MAIS VITORIOSOS")
        for nome, total in vitorias_jaeger.most_common(3):
            print(f"{nome}: {total} vitória(s)")

    pilotos = sorted(RepositorioPilotos.listar(), key=lambda p: p.experiencia, reverse=True)[:3]
    if pilotos:
        print("\nPILOTOS MAIS EXPERIENTES")
        for piloto in pilotos:
            print(f"{piloto.nome}: nível {piloto.nivel} ({piloto.experiencia} XP)")

    print("\nÚLTIMAS BATALHAS")
    if not historico:
        print("Nenhum ataque registrado.")
    for batalha in reversed(historico[-10:]):
        print(f"{batalha['data'].strftime('%d/%m/%Y')} | {RESULTADOS[batalha['resultado']]:<10} | "
              f"{batalha['kaiju']} (cat. {batalha['categoria']}) x {batalha['jaeger'] or '—'}")
    pausar()


def salvar_campanha(campanha):
    # shortcut: pickle guarda os objetos do jogo como estão; saves antigos podem não
    # abrir se as classes mudarem. Trocar por JSON se o formato precisar durar.
    estado = {
        "dificuldade": dificuldade.chave,
        "data_atual": Cronometro().data_atual,
        "campanha": {"saldo": campanha.orcamento.saldo,
                     "cidades_perdidas": campanha.cidades_perdidas,
                     "programa_reativado": campanha.programa_reativado,
                     "proximo_ataque": campanha.proximo_ataque,
                     "historico": campanha.historico,
                     "memorial": campanha.memorial,
                     "evento_pendente": campanha.evento_pendente},
        "pilotos": RepositorioPilotos.listar(),
        "jaegers": RepositorioJaegers.listar(),
        "kaijus_derrotados": RepositorioKaijusDerrotados.listar(),
    }
    with ARQUIVO_SAVE.open("wb") as arquivo:
        pickle.dump(estado, arquivo)


def ler_save():
    """Retorna o estado salvo, ou None se não houver save legível."""
    try:
        with ARQUIVO_SAVE.open("rb") as arquivo:
            return pickle.load(arquivo)
    except FileNotFoundError:
        return None
    except Exception:
        print("O arquivo de save está corrompido ou é de uma versão antiga e foi ignorado.")
        return None


def restaurar_campanha(estado):
    aplicar_dificuldade(estado["dificuldade"])
    Cronometro().data_atual = estado["data_atual"]
    RepositorioPilotos.listar()[:] = estado["pilotos"]
    RepositorioJaegers.listar()[:] = estado["jaegers"]
    RepositorioKaijusDerrotados.listar()[:] = estado["kaijus_derrotados"]
    return Campanha(**estado["campanha"])


def apagar_save():
    ARQUIVO_SAVE.unlink(missing_ok=True)


def iniciar_campanha():
    """Oferece continuar a campanha salva; senão começa uma nova."""
    estado = ler_save()
    if estado:
        cabecalho("CAMPANHA SALVA ENCONTRADA")
        nivel = dificuldade.NIVEIS[estado["dificuldade"]]["nome"]
        continuar = prompt([{
            "type": "list", "name": "opcao", "message": "Como deseja começar?",
            "choices": [
                {"name": (f"Continuar campanha ({estado['data_atual'].strftime('%d/%m/%Y')}, "
                          f"{nivel}, {len(estado['jaegers'])} Jaegers, "
                          f"{len(estado['pilotos'])} pilotos)"), "value": True},
                {"name": "Nova campanha (a campanha salva será substituída)", "value": False},
            ],
        }])["opcao"]
        if continuar:
            return restaurar_campanha(estado)
    escolher_dificuldade()
    return Campanha()


def painel():
    """Executa a campanha e retorna a escolha final ("Reiniciar história" ou "Sair")."""
    global campanha_atual
    campanha = campanha_atual = iniciar_campanha()
    orcamento = campanha.orcamento
    while True:
        cronometro = Cronometro()
        if cronometro.data_atual >= cronometro.data_fim:
            apagar_save()
            return operacao_pitfall()
        if campanha.cidades_perdidas >= dificuldade.atual["cidades_toleradas"]:
            apagar_save()
            cabecalho("A COSTA CAIU")
            print("Cidades demais foram devastadas. Os governos retiram o apoio ao Shatterdome.")
            pausar()
            return final_derrota()
        if campanha_sem_recursos(orcamento):
            apagar_save()
            cabecalho("FIM DA CAMPANHA")
            print("O Shatterdome não possui Jaegers operacionais nem créditos para reagir.")
            pausar()
            return final_derrota()
        # A última fase da guerra começa com o encerramento e a volta do programa Jaeger.
        if not campanha.programa_reativado and cronometro.obter_categoria_atual() == 5:
            campanha.programa_reativado = True
            if desativacao_jaegers() == "Sair" or reativacao_jaegers() == "Sair":
                salvar_campanha(campanha)
                return "Sair"
        if cronometro.data_atual >= campanha.proximo_ataque:
            alerta_kaiju(campanha)
            continue
        if campanha.evento_pendente:
            sortear_evento(campanha)
            continue

        salvar_campanha(campanha)
        cabecalho(f"SHATTERDOME — CENTRAL DE OPERAÇÕES ({dificuldade.atual['nome']})")
        Cronometro().mostrar_tempo_restante()
        mostrar_creditos(orcamento)
        print(f"PRÓXIMO ATAQUE KAIJU: em {campanha.dias_ate_ataque()} dias")
        print(f"CIDADES PERDIDAS: {campanha.cidades_perdidas}/"
              f"{dificuldade.atual['cidades_toleradas']}")
        escolha = prompt([{
            "type": "list", "name": "opcao", "message": "Qual é a sua próxima ordem?",
            "choices": [
                {"name": f"Treinar piloto ({DIAS_POR_ACAO['treinamento']} dias)", "value": "treinar"},
                {"name": f"Construir Jaeger ({DIAS_POR_ACAO['construcao']} dias)", "value": "construir"},
                {"name": f"Aguardar o próximo ataque ({campanha.dias_ate_ataque()} dias)",
                 "value": "aguardar"},
                {"name": f"Enfermaria de Jaegers ({DIAS_POR_ACAO['reparo']} dias)", "value": "enfermaria"},
                {"name": "Gerenciar tripulação", "value": "tripulacao"},
                {"name": "Ver pilotos", "value": "pilotos"},
                {"name": "Ver Jaegers", "value": "jaegers"},
                {"name": "Estatísticas e histórico", "value": "estatisticas"},
                {"name": f"Memorial dos pilotos ({len(campanha.memorial)})", "value": "memorial"},
                {"name": "Salvar e sair", "value": "sair"},
            ],
        }])["opcao"]
        if escolha == "treinar":
            treinar_piloto(orcamento)
        elif escolha == "construir":
            construir_jaeger(orcamento)
        elif escolha == "aguardar":
            cabecalho("AGUARDANDO")
            passar_dias(campanha.dias_ate_ataque())
            pausar("Sirenes disparadas! Pressione Enter...")
        elif escolha == "enfermaria":
            enfermaria_jaegers(orcamento)
        elif escolha == "tripulacao":
            gerenciar_tripulacao()
        elif escolha == "pilotos":
            ver_pilotos()
        elif escolha == "estatisticas":
            ver_estatisticas(campanha)
        elif escolha == "memorial":
            ver_memorial(campanha)
        elif escolha == "jaegers":
            cabecalho("JAEGERS DO SHATTERDOME")
            jaegers = RepositorioJaegers.listar()
            if not jaegers:
                print("Nenhum Jaeger construído.")
            for jaeger in jaegers:
                print(jaeger.info())
            pausar()
        else:
            salvar_campanha(campanha)
            cabecalho("TRANSMISSÃO ENCERRADA")
            print("Campanha salva. Escolha \"Continuar campanha\" na próxima vez.\n")
            narrar("A humanidade continua de pé enquanto alguém estiver disposto a pilotar.", 0.006)
            return "Sair"


if __name__ == "__main__":
    prologo()
    while painel() == "Reiniciar história":
        nova_campanha()
