from pilotos.piloto import Piloto, EstadoPiloto, Personalidade, Nacionalidade


def compatibilidade_personalidade(p1, p2):
    if Personalidade.REBELDE in (p1, p2):
        return 8

    pares_bons = {
        (Personalidade.LIDER, Personalidade.ESTRATEGISTA): 20,
        (Personalidade.CALMO, Personalidade.LIDER): 18,
        (Personalidade.DETERMINADO, Personalidade.ESTRATEGISTA): 18,
        (Personalidade.CALMO, Personalidade.IMPULSIVO): 10,
        (Personalidade.TECNICO, Personalidade.ESTRATEGISTA): 18,
    }

    if p1 == p2:
        return 10

    return pares_bons.get((p1, p2)) or pares_bons.get((p2, p1)) or 15


def calcular_score_nacionalidade(p1, p2):
    dist_nac = abs(p1.nacionalidade.value - p2.nacionalidade.value)
    return max(0, 30 - dist_nac) * 2  # Peso máximo 60


def calcular_score_inteligencia(p1, p2):
    media_inteligencia = (p1.inteligencia + p2.inteligencia) / 2
    return (media_inteligencia / 200) * 10  # Assume inteligência máx 100


def calcular_multiplicador_estado(p1, p2):
    multiplicador = 1
    if p1.estado != EstadoPiloto.ATIVO:
        multiplicador *= 0.85
    if p2.estado != EstadoPiloto.ATIVO:
        multiplicador *= 0.85
    return multiplicador


def calcular_conexao_individual(p1, p2):
    score_nac = calcular_score_nacionalidade(p1, p2)
    score_pers = compatibilidade_personalidade(p1.personalidade, p2.personalidade)
    score_int = calcular_score_inteligencia(p1, p2)
    estado_mult = calcular_multiplicador_estado(p1, p2)

    return (score_nac + score_pers + score_int) * estado_mult


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
    return min(100, round(score_final))



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
            score_total = (score_nac + score_pers + score_int) * mult_estado

            print(f"\n--- Conexão entre {p1.nome} e {p2.nome} ---")
            print(f"Nacionalidades: {p1.nacionalidade.name} x {p2.nacionalidade.name} -> Score: {score_nac:.1f}")
            print(f"Personalidades: {p1.personalidade.name} x {p2.personalidade.name} -> Score: {score_pers}")
            print(f"Inteligência média: {(p1.inteligencia + p2.inteligencia) / 2:.1f} -> Score: {score_int:.1f}")
            print(f"Estados: {p1.estado.name} x {p2.estado.name} -> Multiplicador: {mult_estado:.2f}")
            print(f"Score final da conexão: {score_total:.1f}")
