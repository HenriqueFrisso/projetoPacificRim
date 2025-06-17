from util import *

class CentroOperacoes:
    def __init__(self):
        ...

    @staticmethod
    def selecionar_acao(self):
        menu = [
            {
                "type": "list",
                "name": "opcao",
                "message": "Escolha uma opção:",
                "choices": [
                    "Gerenciar Pilotos",
                    "Gerenciar Jaegers",
                    "Avançar"
                ]
            }
        ]

        resposta = prompt(menu)
        escolha = resposta["opcao"]

        if escolha == "Gerenciar Pilotos":
            self.gerenciar_pilotos()

        elif escolha == "Gerenciar Jaegers":
            self.gerenciar_jaegers()

        elif escolha == "Avançar":
            # avançar na simulação
            ...
    

    @staticmethod
    def gerenciar_pilotos(self):
        pilotos = RepositorioPilotos.listar()

        opcoes = [
            {
                "name": f"{i}. {p.nome} ({p.nacionalidade}) - Estado: {p.estado.name}",
                "value": p
            }
            for i, p in enumerate(pilotos)
        ]

        opcoes.append({
            "name": "Treinar Piloto",
            "value": "treinar"
        })

        menu = [
            {
                "type": "list",
                "name": "escolha",
                "message": "Selecione um piloto ou treine um novo:",
                "choices": opcoes
            }
        ]

        resposta = prompt(menu)
        escolha = resposta["escolha"]

        if escolha == "treinar":
            # Chamar a função para treinar piloto
            from pilotos.factoryPiloto import FabricaPilotos
            novo_piloto = FabricaPilotos().treinar_pilotos()
            print(f"Novo piloto treinado: {novo_piloto.nome}")
            return novo_piloto
        else:
            # Retorna o piloto selecionado
            piloto = escolha
            print(piloto.info())
            return piloto
    
    def gerenciar_jaegers(self):
        jaegers = RepositorioJaegers.listar()
        texto = "Selecione o Jaeger para ver detalhes:"

        if not jaegers:
            texto = "Nenhum Jaeger disponível no momento."

        opcoes = [
            {
                "name": f"{i}. {j.nome} - Categoria: {j.categoria.name} - Estado: {j.estado.name}",
                "value": j
            }
            for i, j in enumerate(jaegers)
        ]
        opcoes.append({
            "name": "Construir Jaeger",
            "value": "treinar"
        })
        opcoes.append({
            "name": "Voltar",
            "value": "voltar"
        })

        menu = [
            {
                "type": "list",
                "name": "escolha",
                "message": texto,
                "choices": opcoes
            }
        ]

        resposta = prompt(menu)
        escolha = resposta["escolha"]

        if escolha == "treinar":
            FabricaJaeger().criar_jaeger()
            return
        elif escolha == "voltar":
            return
        else:
            jaeger = escolha
            print(jaeger.info())