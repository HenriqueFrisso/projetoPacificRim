from util import *
from pilotos.piloto import selecionar_pilotos

class CentroOperacoes:
    def __init__(self):
        ...

    @staticmethod
    def selecionar_acao():
        while True:
            limpar_tela()
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
                CentroOperacoes.gerenciar_pilotos()

            elif escolha == "Gerenciar Jaegers":
                CentroOperacoes.gerenciar_jaegers()

            elif escolha == "Avançar":
                break
    

    @staticmethod
    def gerenciar_pilotos():
        while True:
            limpar_tela()
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
            opcoes.append({
                "name": "Voltar",
                "value": "voltar"
            })

            menu = [
                {
                    "type": "list",
                    "name": "escolha",
                    "message": "==== Central de Jaegers ====",
                    "choices": opcoes
                }
            ]

            resposta = prompt(menu)
            escolha = resposta["escolha"]

            if escolha == "treinar":
                from pilotos.factoryPiloto import FabricaPilotos
                FabricaPilotos().treinar_pilotos()
                input("Piloto treinado com sucesso! Pressione Enter para continuar...")
            elif escolha == "voltar":
                return
            else:
                piloto = escolha
                while True:
                    limpar_tela()
                    print(piloto.info())
                    print("")

                    acoes = [
                        {
                            "type": "list",
                            "name": "acao",
                            "message": f"O que deseja fazer com {piloto.nome}?",
                            "choices": [
                                "Enviar para enfermagem",
                                "Liberar Piloto",
                                "Continuar"
                            ]
                        }
                    ]
                    resposta_acao = prompt(acoes)
                    acao = resposta_acao["acao"]

                    if acao == "Enviar para enfermagem":
                        print(f"{piloto.nome} foi enviado para enfermagem.")
                        input("Pressione Enter para continuar...")
                        break

                    elif acao == "Liberar Piloto":
                        print(f"{piloto.nome} está liberado e ativo.")
                        input("Pressione Enter para continuar...")
                        break

                    elif acao == "Continuar":
                        break
    


    @staticmethod
    def gerenciar_jaegers():
        while True:
            limpar_tela()
            jaegers = RepositorioJaegers.listar()
            texto = "==== Central de Jaegers ===="

            if not jaegers:
                print("Nenhum Jaeger disponível no momento.")

            opcoes = [
                {
                    "name": f"{i}. {j.nome} - Categoria: {j.categoria.name} - Estado: {j.estado.name}",
                    "value": j
                }
                for i, j in enumerate(jaegers)
            ]
            opcoes.append({
                "name": "Construir Jaeger",
                "value": "construir"
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

            if escolha == "construir":
                FabricaJaeger().criar_jaeger()
                input("Pressione Enter para continuar...")
                continue
            elif escolha == "voltar":
                return
            else:
                jaeger = escolha

                while True:
                    limpar_tela()
                    print(jaeger.info())
                    print("")
                    submenu_choices = []

                    # Sempre disponível
                    submenu_choices.append("Enviar para oficina")
                    submenu_choices.append("Continuar")

                    # Adiciona opção condicionalmente
                    if len(jaeger.pilotos) == 0:
                        submenu_choices.insert(1, "Adicionar pilotos")
                    else:
                        submenu_choices.insert(1, "Remover Pilotos")

                    submenu = [
                        {
                            "type": "list",
                            "name": "acao",
                            "message": f"O que deseja fazer com {jaeger.nome}?",
                            "choices": submenu_choices
                        }
                    ]

                    resposta = prompt(submenu)
                    acao = resposta["acao"]

                    if acao == "Enviar para oficina":
                        print(f"{jaeger.nome} foi enviado para a oficina.")
                        input("Pressione Enter para continuar...")

                    elif acao == "Remover Pilotos":
                        jaeger.remover_pilotos()
                        print("Pilotos removidos do Jaeger.")
                        input("Pressione Enter para continuar...")

                    elif acao == "Adicionar pilotos":
                        pilotos = selecionar_pilotos(2)
                        if pilotos == None:
                            print("Quantidade de pilotos insuficiente.") 
                        else:
                            jaeger.adicionar_pilotos(*pilotos)
                            print("Novos pilotos atribuídos com sucesso.")
                        input("Pressione Enter para continuar...")

                    elif acao == "Continuar":
                        break
