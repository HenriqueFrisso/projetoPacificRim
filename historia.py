from InquirerPy import inquirer
import time

def narrar(texto):
    for linha in texto.split("\n"):
        print(linha)
        time.sleep(1.5)

def introducao():
        narrar("No começo, pensávamos que fosse um terremoto...\n"
                "Mas não era.\n"
                "Em 10 de agosto de 2013, algo emergiu do fundo do Oceano Pacífico.")
        narrar("\nUma criatura colossal — algo que só existia em filmes de monstros — emergiu próximo à costa de São Francisco.\n"
                "Chamaram-no de Kaiju.\n"
                "Em menos de seis dias, destruiu três cidades e matou dezenas de milhares.")
        narrar("\nPensávamos que era um evento isolado.\n"
                "Estávamos errados.\n"
                "Seis meses depois, outro Kaiju atacou Manila.\n"
                "Depois, Cabo de São Lucas.\n"
                "E então, cidades inteiras começaram a cair como dominós.")
        narrar("\nChamamos esse dia de K-Day.\n"
                "E percebemos que os monstros não vinham do espaço... vinham de uma fenda dimensional no fundo do mar.")

        narrar("\nPara combater monstros, criamos nossos próprios monstros.\n"
                "Os Jaegers: robôs gigantes controlados por dois pilotos conectados por uma ponte neural.\n"
                "Lutando como se fossem um só corpo, uma só mente.")

        narrar("\nNo começo, vencemos.\n"
                "O primeiro Jaeger derrotou um Kaiju em menos de 60 segundos.\n"
                "A humanidade teve sua primeira vitória.\n"
                "Nós havíamos conseguido... e nos acostumamos a vencer.")

        inquirer.select(
        message="",
        choices=["Continuar"],
        default="Continuar",
        ).execute()