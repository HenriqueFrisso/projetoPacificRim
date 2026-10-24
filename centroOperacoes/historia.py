from util import *

def narrar(texto, velocidade=0.03):  # velocidade menor para simular digitação
    for linha in texto.strip().split("\n"):
        for caractere in linha:
            print(caractere, end='', flush=True)
            time.sleep(velocidade)
        print()  # nova linha após cada linha de texto
        time.sleep(velocidade * 10)  # pausa um pouco maior entre as linhas
    time.sleep(velocidade * 50)

def introducao():
    limpar_tela()
    narrar("""
No começo, pensávamos que fosse um terremoto...
Mas não era.
Em 10 de agosto de 2013, algo emergiu do fundo do Oceano Pacífico.
        """)

    limpar_tela()
    narrar("""
Uma criatura colossal — algo que só existia em filmes de monstros — emergiu próximo à costa de São Francisco.
Chamaram-no de Kaiju.
Em menos de seis dias, destruiu três cidades e matou dezenas de milhares.
        """)

    limpar_tela()
    narrar("""
Pensávamos que era um evento isolado.
Estávamos errados.
Seis meses depois, outro Kaiju atacou Manila.
Depois, Cabo de São Lucas.
E então, cidades inteiras começaram a cair como dominós.
        """)

    limpar_tela()
    narrar("""
Chamamos esse dia de K-Day.
E percebemos que os monstros não vinham do espaço... vinham de uma fenda dimensional no fundo do mar.
        """)

    limpar_tela()
    narrar("""
Para combater monstros, criamos nossos próprios monstros.
Os Jaegers: robôs gigantes controlados por dois pilotos conectados por uma ponte neural.
Lutando como se fossem um só corpo, uma só mente.
        """)

    limpar_tela()
    narrar("""
No começo, vencemos.
O primeiro Jaeger derrotou um Kaiju em menos de 60 segundos.
A humanidade teve sua primeira vitória.
Nós havíamos conseguido... e nos acostumamos a vencer.
        """)

    return inquirer.select(
        message="",
        choices=["Continuar"],
        default="Continuar",
    ).execute()

def final_vitorioso():
    limpar_tela()
    narrar("""
A guerra contra os Kaijus durou anos.
A cada nova geração, eles voltavam maiores, mais letais, mais inteligentes.

Muitos Jaegers tombaram.
Muitos pilotos jamais voltaram.

Mas a humanidade... nunca recuou.
        """)

    limpar_tela()
    narrar("""
Lançamos a Operação Pitfall.

O plano: atravessar a Fenda, com dois Jaegers.
Detonar uma bomba de carga dupla do outro lado.
Fechá-la para sempre.

Era uma missão suicida.
Mas sabíamos que era nossa única chance.
        """)

    limpar_tela()
    narrar("""
Os Jaegers Gipsy Danger e Striker Eureka lideraram o ataque.

No fundo do oceano, enfrentaram dois Kaijus de categoria 5 — colossais, como jamais vistos antes.

A batalha foi brutal.
Corpos de aço contra monstros de carne e fúria.
        """)

    limpar_tela()
    narrar("""
Striker Eureka caiu... mas não em vão.

Gipsy Danger avançou com a bomba em seu núcleo nuclear.

No último instante, o piloto remanescente ativou a sequência de detonação...
...e se lançou de volta pela fenda com um salto de emergência.
        """)

    limpar_tela()
    narrar("""
A explosão foi tão poderosa que rachou o fundo do mar.

A fenda... colapsou.

O portal... foi selado.
        """)

    limpar_tela()
    narrar("""
Os sensores não detectaram mais atividade.

Nenhum Kaiju. Nenhum sinal dimensional.

Pela primeira vez... silêncio.
        """)

    limpar_tela()
    narrar("""
A humanidade venceu.

Não com armas.
Não com ódio.

Mas com coragem, sacrifício... e união.

Jaegers não eram apenas máquinas.
Eram símbolos do que podemos ser quando lutamos juntos.
        """)

    return inquirer.select(
        message="Fim da jornada. O que deseja fazer?",
        choices=["Reiniciar história", "Sair"],
        default="Sair",
    ).execute()

def final_derrota():
    limpar_tela()
    narrar("""
Enviamos tudo o que nos restava.

Os últimos Jaegers.
Os melhores pilotos.
A última esperança da humanidade.

Mas... não foi o suficiente.
        """)

    limpar_tela()
    narrar("""
Os Kaijus evoluíram.

Vieram mais fortes.
Mais rápidos.
Mais coordenados.

Como se já soubessem cada movimento nosso.
Como se... esperassem.
        """)

    limpar_tela()
    narrar("""
Na noite mais escura, as defesas da Muralha do Pacífico caíram.

Cidades costeiras foram engolidas em questão de horas.

Jaegers tombaram um a um.

E os pilotos... foram silenciados.
        """)

    limpar_tela()
    narrar("""
Os governos cessaram comunicações.

As estações orbitais pararam de responder.

As últimas transmissões mostravam luzes azuis cobrindo o céu... e gritos.
        """)

    limpar_tela()
    narrar("""
Então, o mundo ficou em silêncio.

Nenhuma vitória.
Nenhum herói.
Nenhum final feliz.
        """)

    limpar_tela()
    narrar("""
A raça humana perdeu a guerra.

Não por fraqueza... mas por arrogância.
Subestimamos o inimigo.
Confiamos demais nas máquinas.

E agora... somos apenas uma memória.
        """)

    limpar_tela()
    narrar("""
Mas talvez...

Em algum abrigo subterrâneo.
Em alguma ilha esquecida.

Alguém tenha sobrevivido.

Alguém que ainda sonha com o dia em que lutaremos de novo.
E venceremos.
        """)

    return inquirer.select(
        message="Fim da humanidade. O que deseja fazer?",
        choices=["Reiniciar história", "Sair"],
        default="Sair",
    ).execute()


def desativacao_jaegers():
    limpar_tela()
    narrar("""
Com o passar dos anos, os Kaijus ficaram mais poderosos.
Os Jaegers, antes invencíveis, começaram a tombar um por um.
As vitórias deram lugar à dúvida.
E a confiança da humanidade... começou a ruir.
    """)

    limpar_tela()
    narrar("""
Em meio ao caos, os líderes mundiais tomaram uma decisão drástica:
Encerrar o Programa Jaeger.

Em seu lugar, ergueriam uma nova linha de defesa:
A Muralha da Vida — um colosso de concreto e aço, construído ao longo de todo o litoral do Pacífico.
    """)

    limpar_tela()
    narrar("""
Chamaram de solução definitiva.

Mas muitos sabiam que era apenas uma tentativa desesperada de conter o inevitável.

Os Jaegers, nossos maiores símbolos de resistência, foram desativados.
Deixados para enferrujar em hangares vazios.
    """)

    limpar_tela()
    narrar("""
Pilotos foram dispensados.
Bases, desativadas.
O sonho... adormecido.

Mas nas sombras, alguns ainda acreditavam.
Alguns sabiam... que os Kaijus voltariam.
    """)

    return inquirer.select(
        message="O Programa Jaeger foi encerrado. O que deseja fazer?",
        choices=["Continuar", "Sair"],
        default="Continuar",
    ).execute()


def reativacao_jaegers():
    limpar_tela()
    narrar("""
E então... como previsto, os Kaijus voltaram.
Mais poderosos. Mais frequentes.

A Muralha da Vida... caiu na primeira onda.
Milhões pereceram.
E o mundo, mais uma vez, se viu à beira do colapso.
    """)

    limpar_tela()
    narrar("""
Diante da catástrofe, os líderes não tiveram escolha.

A última base Jaeger — Shatterdome — foi reativada.

Pilotos veteranos foram convocados.
Novos recrutas começaram o treinamento.

Era hora de lutar novamente.
    """)

    limpar_tela()
    narrar("""
Jaegers esquecidos foram restaurados.
Peças foram remendadas.
Tecnologias antigas, revisitadas.

Era tudo o que restava.
E mesmo assim... havia esperança.
    """)

    limpar_tela()
    narrar("""
Porque não importava o tamanho do monstro...
...ou a profundidade do medo.

Enquanto existisse um piloto disposto a lutar,
a humanidade ainda teria chance.
    """)

    return inquirer.select(
        message="Os Jaegers foram reativados. O que deseja fazer?",
        choices=["Continuar", "Sair"],
        default="Continuar",
    ).execute()