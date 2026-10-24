import json
from pathlib import Path

from pilotos.piloto import Piloto, EstadoPiloto, Personalidade, Nacionalidade

ARQUIVO_CONEXAO = Path(__file__).with_name("conexao.json")


def carregar_configuracao_conexao():
    """Carrega a tabela editável usada no cálculo da ponte neural."""
    with ARQUIVO_CONEXAO.open(encoding="utf-8") as arquivo:
        return json.load(arquivo)


CONFIGURACAO_CONEXAO = carregar_configuracao_conexao()


def compatibilidade_personalidade(p1, p2):
    configuracao = CONFIGURACAO_CONEXAO["personalidade"]
    if Personalidade.REBELDE in (p1, p2):
        return configuracao["rebelde"]

    if p1 == p2:
        return configuracao["mesma_personalidade"]

    par = "|".join(sorted((p1.name, p2.name)))
    return (configuracao["pares_compativeis"].get(par)
            or abs(abs(p1.value - p2.value) - configuracao["referencia_diferenca"]))


def calcular_score_nacionalidade(p1, p2):
    configuracao = CONFIGURACAO_CONEXAO["nacionalidade"]
    dist_nac = abs(p1.nacionalidade.value - p2.nacionalidade.value)
    return max(0, configuracao["distancia_maxima"] - dist_nac) * configuracao["multiplicador"]


def calcular_score_inteligencia(p1, p2):
    configuracao = CONFIGURACAO_CONEXAO["inteligencia"]
    media_inteligencia = (p1.inteligencia + p2.inteligencia) / 2
    return (media_inteligencia / configuracao["divisor_media"]) * configuracao["escala"]


def calcular_multiplicador_estado(p1, p2):
    multiplicador_nao_ativo = CONFIGURACAO_CONEXAO["estado"]["multiplicador_por_piloto_nao_ativo"]
    multiplicador = 1
    if p1.estado != EstadoPiloto.ATIVO:
        multiplicador *= multiplicador_nao_ativo
    if p2.estado != EstadoPiloto.ATIVO:
        multiplicador *= multiplicador_nao_ativo
    return multiplicador


def calcular_bonus_vinculo(p1, p2):
    """Duplas que já lutaram juntas sincronizam melhor, até um limite."""
    configuracao = CONFIGURACAO_CONEXAO["vinculo"]
    batalhas = p1.vinculos.get(p2.id, {}).get("batalhas", 0)
    return min(batalhas * configuracao["bonus_por_batalha"], configuracao["bonus_maximo"])


def calcular_conexao_individual(p1, p2):
    score_nac = calcular_score_nacionalidade(p1, p2)
    score_pers = compatibilidade_personalidade(p1.personalidade, p2.personalidade)
    score_int = calcular_score_inteligencia(p1, p2)
    estado_mult = calcular_multiplicador_estado(p1, p2)

    return (score_nac + score_pers + score_int + calcular_bonus_vinculo(p1, p2)) * estado_mult


def calcular_conexao(*pilotos):
    if not pilotos or len(pilotos) < 2:
        return 0

    total = 0
    combinacoes = 0

    for i in range(len(pilotos)):
        for j in range(i + 1, len(pilotos)):
            total += calcular_conexao_individual(pilotos[i], pilotos[j])
            combinacoes += 1

    score_final = total / combinacoes
    return round(score_final)



def mostrar_conexao_detalhada(*pilotos):
    if not pilotos or len(pilotos) < 2:
        print("É necessário ao menos dois pilotos para avaliar a conexão.")
        return

    for i in range(len(pilotos)):
        for j in range(i + 1, len(pilotos)):
            p1, p2 = pilotos[i], pilotos[j]

            score_nac = calcular_score_nacionalidade(p1, p2)
            score_pers = compatibilidade_personalidade(p1.personalidade, p2.personalidade)
            score_int = calcular_score_inteligencia(p1, p2)
            mult_estado = calcular_multiplicador_estado(p1, p2)
            score_vinculo = calcular_bonus_vinculo(p1, p2)
            score_total = (score_nac + score_pers + score_int + score_vinculo) * mult_estado

            print(f"\n--- Conexão entre {p1.nome} e {p2.nome} ---")
            print(f"Nacionalidades: {p1.nacionalidade.name} x {p2.nacionalidade.name} -> Score: {score_nac:.1f}")
            print(f"Personalidades: {p1.personalidade.name} x {p2.personalidade.name} -> Score: {score_pers}")
            print(f"Inteligência média: {(p1.inteligencia + p2.inteligencia) / 2:.1f} -> Score: {score_int:.1f}")
            print(f"Vínculo: {p1.vinculos.get(p2.id, {}).get('batalhas', 0)} batalhas juntos -> Score: {score_vinculo}")
            print(f"Estados: {p1.estado.name} x {p2.estado.name} -> Multiplicador: {mult_estado:.2f}")
            print(f"Score final da conexão: {score_total:.1f}")
