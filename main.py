"""Ponto de entrada da campanha interativa de Pacific Rim."""

import json
from pathlib import Path
from time import sleep

from centroOperacoes.cronometro import Cronometro
from centroOperacoes.historia import (desativacao_jaegers, final_derrota, final_vitorioso,
                                      narrar, reativacao_jaegers)
from jaegers.ataques import custo_arma
from jaegers.categorias import custo_geracao
from jaegers.factoryJaeger import FabricaJaeger
from jaegers.jaeger import EstadoJaeger
from kaijus.categorias import CategoriaKaiju
from kaijus.factoryKaiju import FabricaKaiju
from pilotos.factoryPiloto import FabricaPilotos
from pilotos.piloto import selecionar_pilotos
from repositorios.repositorios import (RepositorioJaegers, RepositorioKaijusDerrotados,
                                       RepositorioPilotos)
from util import limpar_tela, prompt
import dificuldade

ARQUIVO_PRECOS = Path(__file__).with_name("precos.json")


def carregar_precos():
    """Lê a tabela editável de custos usada pela campanha."""
    with ARQUIVO_PRECOS.open(encoding="utf-8") as arquivo:
        return json.load(arquivo)


PRECOS = carregar_precos()
INTERVALO_ENTRE_GOLPES = PRECOS["intervalo_entre_golpes_segundos"]


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


def mostrar_creditos(orcamento):
    print(f"\nCRÉDITOS DO SHATTERDOME: ₡ {orcamento.saldo:,}".replace(",", "."))


def ha_jaeger_operacional():
    """Um Jaeger só protege a costa se estiver íntegro o bastante e tripulado."""
    return any(
        jaeger.estado in (EstadoJaeger.ATIVO, EstadoJaeger.DANIFICADO)
        and jaeger.saude > 0
        and len(jaeger.pilotos) >= 2
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
    cabecalho("PACIFIC RIM — ÚLTIMA LINHA DE DEFESA")
    narrar("""
Ano de 2013. Uma fenda se abriu no fundo do Pacífico.
De lá vieram os Kaijus — criaturas grandes demais para qualquer exército.

Para enfrentar monstros, a humanidade construiu monstros de aço: os Jaegers.
Dois pilotos, uma ponte neural e uma única chance de proteger a costa.

Você acaba de assumir o comando do Shatterdome. O próximo alerta pode soar
a qualquer momento.
    """, velocidade=0.004)
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
    piloto = FabricaPilotos().treinar_pilotos()
    if piloto:
        orcamento.debitar(CUSTO_CONCLUSAO_TREINAMENTO)
        print(f"\n{piloto.nome} agora faz parte do programa Jaeger.")
        print(f"₡ {CUSTO_TREINAMENTO:,} debitados pela seleção e treinamento.".replace(",", "."))
    else:
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
    print("Selecione dois pilotos e defina a arma assinatura do novo Jaeger.")
    print("Novas gerações são liberadas com o avanço da guerra.")
    print("Armas mais caras do que o saldo permite não aparecem na lista.")
    jaeger = FabricaJaeger().criar_jaeger(verba=orcamento.saldo - CUSTO_JAEGER)
    if jaeger:
        custo = (CUSTO_JAEGER + custo_geracao(jaeger.categoria)
                 + custo_arma(jaeger.ataque_assinatura))
        orcamento.debitar(custo)
        print("\nLançamento concluído. Um novo defensor está pronto.")
        print(jaeger.info())
        print(f"₡ {custo:,} debitados.".replace(",", "."))
    else:
        print("Construção cancelada. Nenhum crédito foi gasto.")
    pausar()


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
                {"name": (f"{p.nome} ({p.nacionalidade}) | {p.personalidade} | {p.estado.name} | "
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
                "name": f"{j.nome} | {j.estado.name} | pilotos: {len(j.pilotos)}/2",
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
    if len(jaeger.pilotos) < 2:
        opcoes.insert(0, {"name": "Alocar piloto", "value": "alocar"})
    opcoes.append({"name": "Voltar", "value": None})
    acao = prompt([{
        "type": "list", "name": "acao", "message": "O que deseja fazer?", "choices": opcoes,
    }])["acao"]

    if acao not in ("alocar", None):
        desalocar_piloto(acao)
    elif acao == "alocar":
        vagas = 2 - len(jaeger.pilotos)
        pilotos = selecionar_pilotos(vagas)
        if pilotos is None:
            print("Não há pilotos disponíveis em quantidade suficiente.")
        else:
            for piloto in pilotos:
                jaeger.adicionar_piloto(piloto)
            print(f"Tripulação atualizada: {len(jaeger.pilotos)}/2 pilotos.")
            if len(jaeger.pilotos) == 2:
                print(f"Ponte neural sincronizada. {jaeger.nome} voltou a ficar disponível.")
            else:
                print(f"{jaeger.nome} continua indisponível até receber outro piloto.")
    pausar()


def escolher_jaeger():
    disponiveis = [j for j in RepositorioJaegers.listar()
                   if j.estado in (EstadoJaeger.ATIVO, EstadoJaeger.DANIFICADO)
                   and j.saude > 0 and len(j.pilotos) >= 2]
    if not disponiveis:
        return None
    resposta = prompt([{
        "type": "list", "name": "jaeger", "message": "Escolha o Jaeger para a missão:",
        "choices": [{"name": f"{j.nome} | {j.categoria.name} | Integridade: {j.saude}%", "value": j}
                    for j in disponiveis],
    }])
    return resposta["jaeger"]


def categoria_ameaca():
    """A ameaça acompanha a fase atual da guerra, sem gerar categoria zero."""
    return CategoriaKaiju(min(max(Cronometro().obter_categoria_atual(), 1), 5))


def batalha_por_turnos(jaeger, kaiju):
    """Simula a batalha inteira após o comandante iniciar a missão."""
    turno = 1
    while jaeger.saude > 0 and kaiju.saude > 0:
        print(f"\n--- TURNO {turno} ---")
        print(f"{jaeger.nome}: {jaeger.saude:3d}% | {kaiju.nome}: {kaiju.saude:3d}%")
        print(f"{jaeger.nome} usa {jaeger.ataque_assinatura.name}!")
        jaeger.atacar(kaiju)
        sleep(INTERVALO_ENTRE_GOLPES)
        if kaiju.saude <= 0:
            print(f"\n{kaiju.nome} caiu. A costa está segura.")
            return True
        print(f"\n{kaiju.nome} responde com {kaiju.ataque_assinatura.name}!")
        kaiju.atacar(jaeger)
        sleep(INTERVALO_ENTRE_GOLPES)
        if jaeger.saude <= 0:
            print(f"\n{jaeger.nome} foi destruído. O Shatterdome perdeu um defensor.")
            return False
        turno += 1


def passar_dias(dias):
    """Avança o relógio e deixa os pilotos feridos se recuperarem nesse período."""
    Cronometro().atualizar_tempo(dias)
    for piloto in RepositorioPilotos.listar():
        pontos = piloto.recuperar(dias)
        if pontos:
            print(f"🩹 {piloto.nome} ({piloto.personalidade}) recuperou {pontos}% "
                  f"de saúde e está com {piloto.saude}%.")


def iniciar_missao(orcamento):
    cabecalho("ALERTA KAIJU")
    jaeger = escolher_jaeger()
    if not jaeger:
        print("Não há Jaegers operacionais. Treine pilotos e construa um defensor primeiro.")
        pausar()
        return
    categoria = categoria_ameaca()
    kaiju = FabricaKaiju().criarKaijuCategoria(categoria)
    print(f"Uma assinatura biológica foi detectada: {kaiju.nome} (categoria {categoria.name}).")
    pausar("Mobilize o Jaeger pressionando Enter...")
    resultado = batalha_por_turnos(jaeger, kaiju)
    if resultado is True:
        recompensa = categoria.value * RECOMPENSA_POR_CATEGORIA
        orcamento.creditar(recompensa)
        passar_dias(120)
        print("A vitória comprou mais 120 dias para a resistência.")
        print(f"Recompensa da defesa costeira: ₡ {recompensa:,}.".replace(",", "."))
    elif resultado is False:
        penalidade = min(CUSTO_DERROTA, orcamento.saldo)
        orcamento.debitar(penalidade)
        passar_dias(45)
        print("A guerra continua. Reconstrua as defesas antes do próximo ataque.")
        print(f"Penalidade pela derrota: ₡ {penalidade:,}.".replace(",", "."))
        if penalidade < CUSTO_DERROTA:
            print("As reservas do Shatterdome foram completamente esgotadas.")
    pausar()


def operacao_pitfall():
    """Batalha final quando o relógio do fim do mundo zera; decide o desfecho."""
    cabecalho("OPERAÇÃO PITFALL")
    narrar("""
O relógio do fim do mundo zerou. A Fenda está instável demais para esperar.
Resta uma única ofensiva: descer até o fundo do Pacífico e selar a passagem.
    """, 0.006)
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


def painel():
    """Executa a campanha e retorna a escolha final ("Reiniciar história" ou "Sair")."""
    escolher_dificuldade()
    orcamento = Orcamento()
    programa_reativado = False
    while True:
        cronometro = Cronometro()
        if cronometro.data_atual >= cronometro.data_fim:
            return operacao_pitfall()
        if campanha_sem_recursos(orcamento):
            cabecalho("FIM DA CAMPANHA")
            print("O Shatterdome não possui Jaegers operacionais nem créditos para reagir.")
            pausar()
            return final_derrota()
        # A última fase da guerra começa com o encerramento e a volta do programa Jaeger.
        if not programa_reativado and cronometro.obter_categoria_atual() == 5:
            programa_reativado = True
            if desativacao_jaegers() == "Sair" or reativacao_jaegers() == "Sair":
                return "Sair"
        cabecalho(f"SHATTERDOME — CENTRAL DE OPERAÇÕES ({dificuldade.atual['nome']})")
        Cronometro().mostrar_tempo_restante()
        mostrar_creditos(orcamento)
        escolha = prompt([{
            "type": "list", "name": "opcao", "message": "Qual é a sua próxima ordem?",
            "choices": ["Treinar piloto", "Construir Jaeger", "Responder ao alerta Kaiju",
                        "Enfermaria de Jaegers", "Gerenciar tripulação", "Ver pilotos",
                        "Ver Jaegers", "Encerrar campanha"],
        }])["opcao"]
        if escolha == "Treinar piloto":
            treinar_piloto(orcamento)
        elif escolha == "Construir Jaeger":
            construir_jaeger(orcamento)
        elif escolha == "Responder ao alerta Kaiju":
            iniciar_missao(orcamento)
        elif escolha == "Enfermaria de Jaegers":
            enfermaria_jaegers(orcamento)
        elif escolha == "Gerenciar tripulação":
            gerenciar_tripulacao()
        elif escolha == "Ver pilotos":
            ver_pilotos()
        elif escolha == "Ver Jaegers":
            cabecalho("JAEGERS DO SHATTERDOME")
            jaegers = RepositorioJaegers.listar()
            if not jaegers:
                print("Nenhum Jaeger construído.")
            for jaeger in jaegers:
                print(jaeger.info())
            pausar()
        else:
            cabecalho("TRANSMISSÃO ENCERRADA")
            narrar("A humanidade continua de pé enquanto alguém estiver disposto a pilotar.", 0.006)
            return "Sair"


if __name__ == "__main__":
    prologo()
    while painel() == "Reiniciar história":
        nova_campanha()
