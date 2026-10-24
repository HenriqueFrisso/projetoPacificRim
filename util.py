from enum import Enum, IntEnum, auto
from random import uniform, randint, random, choice
try:
    from InquirerPy import inquirer, prompt
    from InquirerPy.separator import Separator
except ModuleNotFoundError:
    # Mantém a campanha utilizável em terminais onde a dependência opcional
    # InquirerPy ainda não foi instalada.
    class Separator:
        def __init__(self, *args, **kwargs):
            pass

    def _escolher(pergunta):
        escolhas = [item for item in pergunta.get("choices", [])
                    if not isinstance(item, Separator)]
        if pergunta.get("type") == "input":
            padrao = pergunta.get("default", "")
            sugestao = f" [{padrao}]" if padrao else ""
            return input(f"{pergunta.get('message', '')}{sugestao} ") or padrao
        for indice, item in enumerate(escolhas, start=1):
            nome = item.get("name", item) if isinstance(item, dict) else item
            print(f"{indice}. {nome}")
        while True:
            try:
                resposta = int(input(f"{pergunta.get('message', 'Escolha uma opção:')} ")) - 1
                item = escolhas[resposta]
                return item.get("value", item.get("name")) if isinstance(item, dict) else item
            except (ValueError, IndexError):
                print("Opção inválida.")

    def prompt(perguntas):
        resultado = {}
        for pergunta in perguntas:
            if pergunta.get("type") == "checkbox":
                escolhas = [item for item in pergunta.get("choices", [])
                            if not isinstance(item, Separator)]
                for indice, item in enumerate(escolhas, start=1):
                    print(f"{indice}. {item.get('name', item) if isinstance(item, dict) else item}")
                while True:
                    try:
                        indices = input(f"{pergunta.get('message', 'Escolha opções')} (ex.: 1,2): ")
                        valores = [int(valor.strip()) - 1 for valor in indices.split(",")]
                        if len(set(valores)) != len(valores):
                            raise ValueError
                        resultado[pergunta["name"]] = [
                            escolhas[indice].get("value", escolhas[indice].get("name"))
                            if isinstance(escolhas[indice], dict) else escolhas[indice]
                            for indice in valores
                        ]
                        break
                    except (ValueError, IndexError):
                        print("Seleção inválida.")
            else:
                resultado[pergunta["name"]] = _escolher(pergunta)
        return resultado

    class _Selecao:
        def __init__(self, **pergunta):
            self.pergunta = pergunta

        def execute(self):
            return _escolher(self.pergunta)

    class _Inquirer:
        select = _Selecao

    inquirer = _Inquirer()
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
from centroOperacoes import *
