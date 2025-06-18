import time
def batalha(Desafiante, Desafiado):
    while True:
        Desafiante.atacar(Desafiado)
        if Desafiado.saude <= 0:
            print(f"{Desafiado} foi derrotado!")
            return True
        else:
            time.sleep(0.1)
            Desafiado.atacar(Desafiante)
            if Desafiante.saude <= 0:
                print(f"{Desafiante} foi derrotado!")
                return False
        time.sleep(0.1)