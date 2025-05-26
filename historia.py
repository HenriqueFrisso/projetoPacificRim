from InquirerPy import inquirer
import time
import os

def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")

def narrar(texto, velocidade=1.5):
    for linha in texto.strip().split("\n"):
        print(linha)
        time.sleep(velocidade)

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

    inquirer.select(
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

    inquirer.select(
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

    inquirer.select(
        message="Fim da humanidade. O que deseja fazer?",
        choices=["Reiniciar história", "Sair"],
        default="Sair",
    ).execute()


final_derrota()