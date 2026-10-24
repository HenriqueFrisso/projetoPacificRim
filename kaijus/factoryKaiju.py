from util import *
from kaijus.kaiju import Kaiju
from kaijus.kaijusBase import kaijusBase
from kaijus.categorias import CategoriaKaiju


class FabricaKaiju:

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
