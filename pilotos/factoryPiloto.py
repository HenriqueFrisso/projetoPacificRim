from util import *
from pilotos.piloto import Piloto, EstadoPiloto, Nacionalidade, Personalidade


class FabricaPilotos:

    @registrar_piloto
    def treinar_pilotos(self):
        p1 = self.__criar_piloto_aleatorio()
        p2 = self.__criar_piloto_aleatorio()
        p3 = self.__criar_piloto_aleatorio()
        return self.__escolher_piloto(p1,p2,p3)


    def __criar_piloto_aleatorio(self):
        nomes_por_nacionalidade = {
            Nacionalidade.USA: ["Alex", "Jake", "Emily", "Sarah", "John", "Liam"],
            Nacionalidade.UK: ["Arthur", "Charlotte", "Oliver", "Isla", "George"],
            Nacionalidade.AUS: ["Mason", "Zoe", "Cooper", "Chloe", "Hudson"],
            Nacionalidade.CAN: ["Aiden", "Sophie", "Logan", "Emma", "Lucas"],
            Nacionalidade.NZL: ["Finn", "Ruby", "Leo", "Amelia", "Hunter"],

            Nacionalidade.GER: ["Hans", "Greta", "Lukas", "Anna", "Karl"],
            Nacionalidade.NLD: ["Daan", "Tess", "Bram", "Sophie", "Luuk"],
            Nacionalidade.SWE: ["Erik", "Lina", "Nils", "Freja", "Oskar"],
            Nacionalidade.FRA: ["Jean", "Camille", "Louis", "Chloé", "Émile"],
            Nacionalidade.ITA: ["Luca", "Giulia", "Marco", "Alessia", "Enzo"],
            Nacionalidade.ESP: ["Carlos", "Lucia", "Mateo", "Sofia", "Diego"],
            Nacionalidade.POR: ["Tiago", "Beatriz", "João", "Inês", "Rafael"],

            Nacionalidade.BRA: ["Henrique", "Ana", "Gabriel", "Camila", "Pedro"],
            Nacionalidade.MEX: ["Luis", "Maria", "Jose", "Valentina", "Diego"],

            Nacionalidade.JPN: ["Hiro", "Yuki", "Takashi", "Sakura", "Ren"],
            Nacionalidade.KOR: ["Jin", "Hana", "Minho", "Soo", "Jisoo"],
            Nacionalidade.CHN: ["Wei", "Mei", "Li", "Xiao", "Chen"],

            Nacionalidade.IND: ["Arjun", "Priya", "Rahul", "Ananya", "Ravi"],
            Nacionalidade.RUS: ["Ivan", "Olga", "Dmitri", "Nina", "Yuri"],
            Nacionalidade.IRN: ["Ali", "Zahra", "Reza", "Leila", "Hassan"],
            Nacionalidade.KSA: ["Faisal", "Amina", "Omar", "Fatima", "Salim"],
        }

        sobrenomes_por_nacionalidade = {
            Nacionalidade.USA: ["Smith", "Johnson", "Brown", "Williams", "Jones"],
            Nacionalidade.UK: ["Smith", "Jones", "Taylor", "Brown", "Williams"],
            Nacionalidade.AUS: ["Smith", "Brown", "Wilson", "Jones", "Clark"],
            Nacionalidade.CAN: ["Smith", "Brown", "Tremblay", "Wilson", "Johnson"],
            Nacionalidade.NZL: ["Smith", "Wilson", "Taylor", "Brown", "Johnson"],

            Nacionalidade.GER: ["Müller", "Schmidt", "Schneider", "Fischer", "Weber"],
            Nacionalidade.NLD: ["de Jong", "Jansen", "de Vries", "van den Berg", "Bakker"],
            Nacionalidade.SWE: ["Johansson", "Andersson", "Karlsson", "Nilsson", "Eriksson"],
            Nacionalidade.FRA: ["Martin", "Bernard", "Thomas", "Petit", "Robert"],
            Nacionalidade.ITA: ["Rossi", "Russo", "Ferrari", "Esposito", "Bianchi"],
            Nacionalidade.ESP: ["García", "Martínez", "López", "Sánchez", "Pérez"],
            Nacionalidade.POR: ["Silva", "Santos", "Ferreira", "Pereira", "Oliveira"],

            Nacionalidade.BRA: ["Silva", "Santos", "Oliveira", "Souza", "Pereira"],
            Nacionalidade.MEX: ["Hernández", "González", "López", "Martínez", "García"],

            Nacionalidade.JPN: ["Takahashi", "Kobayashi", "Tanaka", "Saito", "Yamamoto"],
            Nacionalidade.KOR: ["Kim", "Lee", "Park", "Choi", "Jung"],
            Nacionalidade.CHN: ["Wang", "Li", "Zhang", "Liu", "Chen"],

            Nacionalidade.IND: ["Sharma", "Patel", "Singh", "Kumar", "Gupta"],
            Nacionalidade.RUS: ["Ivanov", "Petrov", "Sidorov", "Smirnov", "Volkov"],
            Nacionalidade.IRN: ["Hosseini", "Mohammadi", "Ahmadi", "Kazemi", "Rahimi"],
            Nacionalidade.KSA: ["Al-Saud", "Al-Faisal", "Al-Mutairi", "Al-Rashid", "Al-Qahtani"],
        }

        nacionalidade = choice(list(Nacionalidade))
        nome = choice(nomes_por_nacionalidade[nacionalidade])
        sobrenome = choice(sobrenomes_por_nacionalidade[nacionalidade])
        nome_completo = f"{nome} {sobrenome}"

        idade = randint(20, 40)
        inteligencia = randint(60, 100)
        personalidade = choice(list(Personalidade))
        estado = EstadoPiloto.ATIVO

        return Piloto(
            nome=nome_completo,
            idade=idade,
            inteligencia=inteligencia,
            nacionalidade=nacionalidade,
            personalidade=personalidade,
            estado=estado
        )


    def __escolher_piloto(self, *pilotos):
        while True:
            escolhas = [piloto.nome for piloto in pilotos] + [Separator(), "Confirmar escolha", "Cancelar"]
            escolha = inquirer.select(
                message="Selecione um piloto para visualizar ou confirmar sua escolha:",
                choices=escolhas,
                default=pilotos[0].nome,
            ).execute()

            if escolha == "Confirmar escolha":
                while True:
                    sub_escolha = inquirer.select(
                        message="Escolha qual piloto deseja confirmar:",
                        choices=[piloto.nome for piloto in pilotos] + [Separator(), "🔙 Voltar"]
                    ).execute()

                    if sub_escolha == "🔙 Voltar":
                        break
                    else:
                        piloto_confirmado = next(p for p in pilotos if p.nome == sub_escolha)
                        print(f"\n✅ Piloto '{piloto_confirmado.nome}' selecionado!")
                        return piloto_confirmado

            elif escolha == "Cancelar":
                print("❌ Cancelado.")
                return None

            else:
                piloto = next(p for p in pilotos if p.nome == escolha)
                print(f"\n=== Informações de {piloto.nome} ===")
                print(piloto.info())
                input("\nPressione Enter para continuar...")
