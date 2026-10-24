"""Sintetiza os efeitos sonoros do jogo em assets/efeitos/ com o ffmpeg.

Uso: python gerar_efeitos.py
Nenhum som vem de fora: cada efeito é uma fórmula de onda (notas, ruído e varreduras)
renderizada pelo filtro aevalsrc do ffmpeg.
"""
import subprocess

from audio import PASTA_EFEITOS


def tom(freq, decai, amp, inicio=0):
    """Senoide que começa em `inicio` e decai exponencialmente."""
    return f"{amp}*sin(2*PI*{freq}*(t-{inicio}))*exp(-{decai}*(t-{inicio}))*gte(t,{inicio})"


def nota(freq, inicio, decai, amp):
    """Nota com harmônicos, para soar como metal/sopro em vez de apito."""
    return "+".join(tom(freq * h, decai * h, amp / h, inicio) for h in (1, 2, 3))


def ruido(decai, amp, inicio=0):
    return f"{amp}*(random(0)*2-1)*exp(-{decai}*(t-{inicio}))*gte(t,{inicio})"


def varredura(f0, f1, duracao, amp):
    """Frequência indo de f0 a f1 ao longo da duração."""
    return f"{amp}*sin(2*PI*({f0}*t+({f1}-{f0})*t*t/(2*{duracao})))*lt(t,{duracao})"


def janela(inicio, fim):
    """Envelope em arco entre inicio e fim, para golpes de ruído."""
    return f"between(t,{inicio},{fim})*sin(PI*(t-{inicio})/({fim}-{inicio}))"


ROSNADO = "(2*PI*75*t-3*cos(2*PI*5*t))"  # 75 Hz oscilando ±15 Hz
SIRENE = "(2*PI*800*t-250*cos(2*PI*0.8*t))"  # 800 Hz oscilando ±200 Hz

# nome: (expressão, duração em segundos, filtros extras)
EFEITOS = {
    # --- armas dos Jaegers ---
    "soco": (f"{tom(85, 14, 0.9)}+{tom(160, 25, 0.4)}+{ruido(45, 0.5)}", 0.45, "lowpass=f=2500"),
    "lamina": (f"0.6*(random(0)*2-1)*{janela(0, 0.25)}+{tom(2600, 10, 0.25, 0.12)}+{tom(3900, 14, 0.15, 0.12)}",
               0.6, "highpass=f=1200"),
    "raio": (f"{varredura(1400, 300, 0.7, 0.45)}*(1+0.5*sin(2*PI*30*t))*exp(-2*t)+{tom(220, 4, 0.3)}",
             0.8, "aecho=0.8:0.5:60:0.3"),
    "pulso": (f"0.25*sgn(sin(2*PI*110*t))*exp(-3*t)+0.5*(random(0)*2-1)*lt(mod(t,0.07),0.015)*exp(-2*t)"
              f"+{varredura(3000, 600, 0.3, 0.2)}", 0.6, "lowpass=f=6000"),
    # --- ataques dos Kaijus ---
    "garras": (f"0.6*(random(0)*2-1)*({janela(0, 0.12)}+{janela(0.14, 0.26)})", 0.35,
               "highpass=f=1800,lowpass=f=6000"),
    "acido": ("0.4*(random(0)*2-1)*min(1,t*8)*exp(-1.5*t)+0.2*sin(2*PI*(180+60*sin(2*PI*9*t))*t)*exp(-2*t)",
              1.0, "highpass=f=300"),
    "explosao": (f"{ruido(3, 0.9)}+{tom(55, 3, 0.8)}", 1.4, "lowpass=f=600"),
    # --- combate ---
    "impacto": (f"{tom(310, 9, 0.5)}+{tom(747, 12, 0.35)}+{tom(1312, 16, 0.25)}+{tom(2120, 22, 0.15)}"
                f"+{ruido(60, 0.4)}", 0.8, ""),
    "erro": (f"0.35*(random(0)*2-1)*{janela(0, 0.35)}", 0.4, "highpass=f=400,lowpass=f=2200"),
    "rugido": (f"0.3*(sin{ROSNADO}+0.5*sin(2*{ROSNADO})+0.33*sin(3*{ROSNADO})+0.25*sin(4*{ROSNADO})"
               f"+(random(0)*2-1))*min(1,t*3)*min(1,(1.8-t)*2)", 1.8, "lowpass=f=1200,aecho=0.8:0.6:80:0.3"),
    "vitoria": ("+".join(nota(f, inicio, 3, 0.35) for f, inicio in
                         ((523.25, 0), (659.25, 0.15), (784, 0.3), (1046.5, 0.45))), 1.6, ""),
    "derrota": ("+".join(nota(f, inicio, 1.5, 0.35) for f, inicio in ((392, 0), (329.6, 0.35), (261.6, 0.7)))
                + f"+{tom(65, 1, 0.3)}", 2.0, "lowpass=f=3000"),
    "destruido": (f"{ruido(2, 0.8)}+{tom(55, 2, 0.7)}+{tom(240, 5, 0.4, 0.1)}+{tom(613, 7, 0.3, 0.1)}"
                  f"+{ruido(8, 0.3, 0.1)}", 2.0, "lowpass=f=3000"),
    # --- campanha ---
    "sirene": (f"0.35*(sin{SIRENE}+0.3*sin(2*{SIRENE}))*min(1,t*4)*min(1,(2.6-t)*3)", 2.6, ""),
    "construcao": ("+".join(f"{tom(520, 14, 0.4, i)}+{tom(1240, 18, 0.25, i)}+{tom(2010, 24, 0.15, i)}"
                            f"+{ruido(50, 0.3, i)}" for i in (0, 0.3, 0.6)) + "+0.1*sin(2*PI*60*t)",
                   1.0, ""),
    "reparo": (f"0.5*(random(0)*2-1)*lt(mod(t,0.045),0.006)*lt(t,0.5)+{tom(900, 20, 0.3, 0.55)}"
               f"+{tom(1700, 25, 0.2, 0.55)}", 0.9, "highpass=f=500"),
    "treino_ok": (f"{nota(880, 0, 6, 0.4)}+{nota(1318.5, 0.12, 4, 0.4)}", 0.8, ""),
    "treino_falha": ("0.25*sgn(sin(2*PI*330*t))*lt(t,0.18)+0.25*sgn(sin(2*PI*247*t))*between(t,0.2,0.5)",
                     0.55, "lowpass=f=2000"),
    "creditos": ("+".join(tom(f, 9, 0.35, i) for f, i in ((1568, 0), (2093, 0.08), (1568, 0.2), (2093, 0.28))),
                 0.7, ""),
    "nivel": ("+".join(tom(f, 6, 0.3, i) for f, i in ((660, 0), (880, 0.07), (1100, 0.14), (1320, 0.21)))
              + f"+{tom(2640, 8, 0.12, 0.21)}", 0.9, ""),
    "cidade": (f"{ruido(1.6, 0.9)}+{tom(42, 1.2, 0.7)}", 2.4, "lowpass=f=500"),
    "morte": ("+".join(tom(f, d, a) for f, d, a in
                       ((196, 1.2, 0.4), (392, 1.6, 0.25), (466, 2, 0.15), (588, 2.4, 0.12), (784, 3, 0.08))),
              3.0, ""),
    "evento": ("0.35*sin(2*PI*1000*t)*(between(t,0,0.12)+between(t,0.2,0.32))+0.08*(random(0)*2-1)*lt(t,0.5)",
               0.55, "highpass=f=300,lowpass=f=3500"),
}


# Volume médio de cada efeito (dB); os grandes impactos soam mais alto, o erro mais baixo.
VOLUME_PADRAO = -17
VOLUME = {"erro": -23, "rugido": -13, "explosao": -13, "destruido": -12, "cidade": -12, "sirene": -15}


def volume_medio(arquivo):
    saida = subprocess.run(["ffmpeg", "-i", str(arquivo), "-af", "volumedetect", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    return float(saida.split("mean_volume:")[1].split("dB")[0])


def gerar(nome, expressao, duracao, filtros):
    destino = PASTA_EFEITOS / f"{nome}.wav"
    bruto = PASTA_EFEITOS / f"{nome}.bruto.wav"
    filtros = ",".join(f for f in (filtros, f"afade=t=out:st={duracao - 0.05}:d=0.05") if f)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi",
                    "-i", f"aevalsrc='{expressao}':s=44100:d={duracao}", "-af", filtros,
                    "-ac", "1", "-c:a", "pcm_f32le", str(bruto)], check=True)
    # Ajusta o volume médio e segura os picos sem o limitador reamplificar o resultado.
    ganho = VOLUME.get(nome, VOLUME_PADRAO) - volume_medio(bruto)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(bruto),
                    "-af", f"volume={ganho}dB,alimiter=limit=0.9:level=false",
                    "-c:a", "pcm_s16le", str(destino)], check=True)
    bruto.unlink()


if __name__ == "__main__":
    PASTA_EFEITOS.mkdir(parents=True, exist_ok=True)
    for nome, (expressao, duracao, filtros) in EFEITOS.items():
        gerar(nome, expressao, duracao, filtros)
        print(f"gerado {nome}.wav")
