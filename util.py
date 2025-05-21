from enum import Enum, IntEnum, auto
from random import uniform, randint, random, choice
from InquirerPy import inquirer, prompt
from InquirerPy.separator import Separator
from functools import wraps
import questionary

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




