"""Toca a voz do narrador e os efeitos sonoros com um player de linha de comando."""
import os
import shutil
import subprocess
import threading
from pathlib import Path

PASTA_EFEITOS = Path(__file__).resolve().parent / "assets" / "efeitos"
# Testes e simulação desligam o som; PACIFIC_RIM_SEM_SOM=1 desliga para o jogador.
ativo = not os.environ.get("PACIFIC_RIM_SEM_SOM")


def tocar(arquivo):
    """Toca em segundo plano e devolve o processo; sem arquivo ou sem player, não faz nada."""
    if not ativo or not arquivo.exists():
        return None
    # shortcut: depende de um player de linha de comando (ffplay, afplay ou mpg123);
    # no Windows sem ffplay o jogo fica sem som.
    for comando in (["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"], ["afplay"], ["mpg123", "-q"]):
        if shutil.which(comando[0]):
            return subprocess.Popen(comando + [str(arquivo)],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return None


def efeito(nome, atraso=0):
    """Toca assets/efeitos/<nome>.wav, opcionalmente depois de alguns segundos."""
    if not ativo:
        return
    arquivo = PASTA_EFEITOS / f"{nome}.wav"
    if atraso:
        threading.Timer(atraso, tocar, [arquivo]).start()
    else:
        tocar(arquivo)
