from util import *

@singleton
class Cronometro:
    def __init__(self):
        self.iniciar_cronometro()

    def iniciar_cronometro(self, data_inicio="2013-08-10", data_fim="2025-01-17"):
        self.data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
        self.data_fim = datetime.strptime(data_fim, "%Y-%m-%d")
        self.data_atual = self.data_inicio

    def calcular_contagem_cronometro(self, dias_passados: int = 1) -> int:
        ...
        if dias_passados <= 20:
            return 1
        elif dias_passados <= 50:
            return 3
        elif dias_passados <= 100:
            return 6
        elif dias_passados <= 200:
            return 8
        elif dias_passados <= 300:
            return 14
        elif dias_passados <= 400:
            return 25
        elif dias_passados <= 600:
            return 40
        elif dias_passados <= 800:
            return 60
        else:
            return 85

    def atualizar_tempo(self, dias_passados: int, animar: bool = True):
        dias_anteriores = (self.data_fim - self.data_atual).days
        dias_finais = max(dias_anteriores - dias_passados, 0)

        for dias in [] if not animar else range(dias_anteriores, dias_finais - 1, -self.calcular_contagem_cronometro(dias_passados)):
            limpar_tela()
            display = f"""
            
            
            ╔══════════════════════╗
            ║  TEMPO RESTANTE      ║
            ╠══════════════════════╣
            ║      {str(dias).zfill(4)} dias       ║
            ╚══════════════════════╝
            """
            print(display)
            time.sleep(0.1)

        self.data_atual += timedelta(days=dias_passados)
        if self.data_atual > self.data_fim:
            self.data_atual = self.data_fim
        if animar:
            limpar_tela()
    

    def mostrar_tempo_restante(self):
        restante = self.data_fim - self.data_atual
        dias = restante.days
        semanas = dias // 7
        meses = dias // 30
        anos = dias // 365
        print(f"Data atual: {self.data_atual.strftime('%d/%m/%Y')}")
        print(f"Tempo restante até fim do mundo:")
        print(f"- Dias: {dias}")
        print(f"- Semanas: {semanas}")
        print(f"- Meses: {meses}")
        print(f"- Anos: {anos}")

    def data_liberacao(self, categoria):
        """Data em que a guerra entra na fase da categoria (cada fase = 20% do tempo)."""
        total_dias = (self.data_fim - self.data_inicio).days
        if categoria <= 1:
            return self.data_inicio
        # obter_categoria_atual só troca de fase depois de ultrapassar o limite.
        return self.data_inicio + timedelta(days=int(total_dias * 0.2 * (categoria - 1)) + 1)

    def obter_categoria_atual(self):
        total_dias = (self.data_fim - self.data_inicio).days
        dias_passados = (self.data_atual - self.data_inicio).days
        progresso = dias_passados / total_dias

        if progresso <= 0.2:
            return 1
        elif progresso <= 0.4:
            return 2
        elif progresso <= 0.6:
            return 3
        elif progresso <= 0.8:
            return 4
        else:
            return 5