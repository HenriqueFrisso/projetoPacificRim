from enum import Enum, IntEnum, auto
from random import uniform, randint, random, choice
from InquirerPy import inquirer, prompt
from InquirerPy.separator import Separator
from functools import wraps
from datetime import datetime, timedelta
import time
import os
import sys




def singleton(cls):
    instancias = {}

    def get_instance(*args, **kwargs):
        if cls not in instancias:
            instancias[cls] = cls(*args, **kwargs)
        return instancias[cls]

    return get_instance


from repositorios import *

def registrar_piloto(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        piloto = func(*args, **kwargs)
        if piloto:
            RepositorioPilotos.adicionar(piloto)
        return piloto
    return wrapper

def registrar_jaeger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        jaeger = func(*args, **kwargs)
        if jaeger:
            RepositorioJaegers.adicionar(jaeger)
        return jaeger
    return wrapper

def registrar_kaiju_derrotado(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        kaiju = func(*args, **kwargs)
        if not kaiju.ativo:
            RepositorioKaijusDerrotados.adicionar(kaiju)
        return kaiju
    return wrapper



def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")



from kaijus import *
from jaegers import *
from pilotos import *
from repositorios import *
import centroOperacoes.historia as historia
from centroOperacoes.cronometro import Cronometro
from centroOperacoes.centroOperacoes import CentroOperacoes
