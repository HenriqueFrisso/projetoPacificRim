import hashlib
import json
import select
import threading
from pathlib import Path

from audio import tocar

import util
from util import *

PASTA_NARRACAO = Path(__file__).resolve().parent.parent / "assets" / "narracao"
ARQUIVO_DURACOES = PASTA_NARRACAO / "duracoes.json"

# Momentos de história, narrados por um piloto veterano. Cada bloco é uma tela e um
# arquivo de áudio; depois de mudar um texto, rode gerar_narracao.py para refazer a voz.
NARRACOES = {
    "prologo": [
        """Quando eu era criança, achei que fosse um terremoto.
Mas não era.
Em 10 de agosto de 2013, algo saiu do fundo do Pacífico.""",
        """Era uma criatura colossal, coisa de filme de monstro.
Ela atingiu São Francisco.
Em seis dias, três cidades tinham sumido do mapa.
Chamamos aquilo de Kaiju.""",
        """Achamos que seria o único.
Estávamos errados.
Seis meses depois, Manila. Depois, Cabo San Lucas.
As cidades começaram a cair como dominós.""",
        """Eles não vinham do espaço.
Vinham de uma fenda entre dimensões, no fundo do mar.
Era uma porta. E ela não ia se fechar sozinha.""",
        """Para enfrentar monstros, nós construímos os nossos.
Os Jaegers.
Dois pilotos, uma ponte neural, uma só mente.
Eu fui um desses pilotos.""",
        """No começo, nós vencíamos.
E nos acostumamos a vencer.
Agora o próximo alerta pode soar a qualquer momento...
e o comando do Shatterdome é seu.""",
    ],
    "desativacao": [
        """Com os anos, os Kaijus ficaram maiores. Mais rápidos.
Os Jaegers que pareciam invencíveis começaram a cair.
Eu vi amigos que nunca voltaram.""",
        """Os líderes do mundo perderam a fé em nós.
Encerraram o Programa Jaeger.
No lugar, ergueram a Muralha da Vida: concreto e aço ao longo de todo o Pacífico.""",
        """Chamaram de solução definitiva.
Quem já tinha olhado um Kaiju nos olhos sabia que não era.
Os Jaegers foram deixados para enferrujar em hangares vazios.""",
        """Fui dispensado, como tantos outros pilotos.
Mas alguns de nós continuavam esperando o alarme.
Porque sabíamos... eles iam voltar.""",
    ],
    "reativacao": [
        """E eles voltaram.
A Muralha da Vida caiu na primeira onda.
Milhões morreram em uma única noite.""",
        """Não havia mais escolha.
O último Shatterdome foi reaberto.
Veteranos como eu foram chamados de volta.
Os recrutas começaram a treinar no mesmo dia.""",
        """Remendamos Jaegers esquecidos com o que tínhamos.
Não era muito.
Mas era o suficiente para lutar mais uma vez.""",
        """Não importa o tamanho do monstro.
Enquanto houver um piloto disposto a entrar no Jaeger...
a humanidade ainda tem uma chance.""",
    ],
    "pitfall": [
        """O relógio do fim do mundo zerou.
A Fenda está instável demais para esperar.
Só resta uma saída: descer até o fundo do Pacífico...
e fechar aquela porta para sempre.""",
    ],
    "final_vitorioso": [
        """A guerra durou anos.
A cada fase, eles voltavam maiores, mais letais.
Perdemos Jaegers. Perdemos pilotos.
Mas nunca recuamos.""",
        """Então veio a Operação Pitfall.
Descer até a Fenda e detoná-la por dentro.
Todos nós sabíamos que podia ser só ida.""",
        """No fundo do oceano, a escuridão era total.
O Kaiju que guardava a passagem era o maior que eu já tinha visto.
Aço contra carne. Cada golpe parecia o último.""",
        """Quando a bomba disparou, eu ainda estava na ponte neural.
Senti o oceano inteiro tremer.
E a Fenda... colapsou.""",
        """Os sensores ficaram em silêncio.
Nenhum Kaiju. Nenhum sinal.
Pela primeira vez em doze anos... silêncio.""",
        """Nós vencemos.
Não porque éramos mais fortes.
Mas porque lutamos juntos.
Os Jaegers nunca foram só máquinas.""",
    ],
    "final_derrota": [
        """Mandamos tudo o que tínhamos.
Os últimos Jaegers. Os melhores pilotos.
Não foi o suficiente.""",
        """Eles aprenderam.
Vinham mais fortes, mais rápidos, coordenados...
como se conhecessem cada movimento nosso.""",
        """Numa noite, a costa inteira caiu.
Cidades engolidas em horas.
Jaegers tombando, um a um.
E as vozes no rádio... foram se apagando.""",
        """Depois, só estática.
Nenhuma vitória. Nenhum herói.
Só o silêncio do Pacífico.""",
        """Talvez tenhamos confiado demais nas máquinas.
Talvez tenhamos subestimado o inimigo.
Não importa mais.""",
        """Mas se alguém estiver ouvindo isto...
em algum abrigo, em alguma ilha esquecida...
não desista.
Um dia, nós vamos lutar de novo.""",
    ],
}


# Ligado pelo botão "Pular" da janela ou por Enter no terminal; contar() desliga ao terminar.
pular = threading.Event()


def _enter_no_terminal():
    """Checa, sem bloquear, se o jogador apertou Enter no terminal."""
    try:
        if os.name == "nt":
            import msvcrt
            return msvcrt.kbhit() and msvcrt.getwch() in "\r\n"
        if sys.stdin.isatty() and select.select([sys.stdin], [], [], 0)[0]:
            sys.stdin.readline()
            return True
    except (OSError, ValueError):
        pass
    return False


def pulou():
    if not pular.is_set() and not util._interface and _enter_no_terminal():
        pular.set()
    return pular.is_set()


def _esperar(segundos):
    """Dorme em pedacinhos para atender o pulo na hora; devolve True se pulou."""
    passos = max(1, round(segundos / 0.05))
    for _ in range(passos):
        if pulou():
            return True
        time.sleep(segundos / passos)
    return pulou()


def narrar(texto, velocidade=0.03):  # velocidade menor para simular digitação
    for linha in texto.strip().split("\n"):
        for caractere in linha:
            print(caractere, end='', flush=True)
            if _esperar(velocidade):
                print()
                return
        print()  # nova linha após cada linha de texto
        if _esperar(velocidade * 10):  # pausa um pouco maior entre as linhas
            return
    _esperar(velocidade * 50)


def arquivo_narracao(chave, indice, texto):
    """O nome leva um resumo do texto: se o texto mudar, o áudio antigo deixa de valer."""
    resumo = hashlib.sha1(texto.strip().encode("utf-8")).hexdigest()[:8]
    return PASTA_NARRACAO / f"{chave}_{indice}_{resumo}.mp3"


def duracoes():
    try:
        return json.loads(ARQUIVO_DURACOES.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return {}


def contar(chave, velocidade=0.03):
    """Narra um momento de história: cada bloco numa tela, com a voz do piloto."""
    tempos = duracoes()
    pular.clear()
    if util._interface:
        util._interface.mostrar_pular(pular.set)
    else:
        print("(Enter para pular a história)")
    try:
        for indice, texto in enumerate(NARRACOES[chave]):
            limpar_tela()
            arquivo = arquivo_narracao(chave, indice, texto)
            audio = tocar(arquivo)
            ritmo = velocidade
            if audio and arquivo.name in tempos:
                # O texto termina de aparecer junto com a fala (narrar soma pausas por linha).
                linhas = texto.strip().count("\n") + 1
                ritmo = tempos[arquivo.name] * 0.9 / (len(texto.strip()) + 10 * linhas + 50)
            narrar(texto, ritmo)
            while audio and audio.poll() is None and not _esperar(0.1):
                pass
            if pulou():
                if audio:
                    audio.terminate()
                break
    finally:
        pular.clear()
        if util._interface:
            util._interface.esconder_pular()


def final_vitorioso():
    contar("final_vitorioso")
    return prompt([{"type": "list", "name": "escolha", "message": "Fim da jornada. O que deseja fazer?", "choices": ["Reiniciar história", "Sair"]}])["escolha"]


def final_derrota():
    contar("final_derrota")
    return prompt([{"type": "list", "name": "escolha", "message": "Fim da humanidade. O que deseja fazer?", "choices": ["Reiniciar história", "Sair"]}])["escolha"]


def desativacao_jaegers():
    contar("desativacao")
    return prompt([{"type": "list", "name": "escolha", "message": "O Programa Jaeger foi encerrado. O que deseja fazer?", "choices": ["Continuar", "Sair"]}])["escolha"]


def reativacao_jaegers():
    contar("reativacao")
    return prompt([{"type": "list", "name": "escolha", "message": "Os Jaegers foram reativados. O que deseja fazer?", "choices": ["Continuar", "Sair"]}])["escolha"]
