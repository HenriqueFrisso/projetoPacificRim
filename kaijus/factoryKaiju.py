from util import *
from kaijus.kaiju import Kaiju
from kaijus.kaijusBase import kaijusBase
from kaijus.categorias import CategoriaKaiju


class FabricaKaiju:

    # === criar kaiju ===
    def criarKaiju(cls, nome: str = "KAIJU DESCONHECIDO") -> Kaiju:
        if nome not in kaijusBase:
            raise ValueError(f"Kaiju '{nome}' não encontrado na base de dados.")
        return Kaiju(nome)

    # === criar kaiju aleatório ===
    def criarKaijuAleatorio(cls) -> Kaiju:
        nome_aleatorio = choice(list(kaijusBase.keys()))
        return Kaiju(nome_aleatorio)

    # === criar kaiju por categoria ===
    def criarKaijuCategoria(cls, categoria: CategoriaKaiju) -> Kaiju:
        nomes_filtrados = [
            nome for nome, dados in kaijusBase.items()
            if dados["categoria"] == categoria
        ]

        if not nomes_filtrados:
            raise ValueError(f"Nenhum Kaiju encontrado na categoria '{categoria.name}'.")

        nome_escolhido = choice(nomes_filtrados)
        return Kaiju(nome_escolhido)
