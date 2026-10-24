"""Gera a voz do piloto para os momentos de história em assets/narracao/.

Uso: python gerar_narracao.py
Precisa de internet (voz neural pt-BR da Microsoft, via edge-tts) e do ffmpeg.
Só gera os blocos que faltam e apaga os áudios de textos que mudaram.
"""
import asyncio
import json
import subprocess
import tempfile
from pathlib import Path

import edge_tts

from centroOperacoes.historia import ARQUIVO_DURACOES, NARRACOES, PASTA_NARRACAO, arquivo_narracao

VOZ = "pt-BR-AntonioNeural"
RITMO, TOM = "-12%", "-10Hz"  # mais lento e mais grave, como um veterano cansado
# Grave reforçado, eco curto de cabine e um corte nos agudos: soa como narração de filme.
FILTRO = "bass=g=4:f=110,aecho=0.8:0.6:45|90:0.22|0.12,lowpass=f=7000,volume=1.4"
# Como o filme pronuncia os termos em inglês (plurais antes dos singulares).
PRONUNCIA = {"Jaegers": "Iêguers", "Jaeger": "Iêguer", "Kaijus": "Cáijus", "Kaiju": "Cáiju",
             "Shatterdome": "Xáterdoum", "Pitfall": "Pitfól"}


def para_fala(texto):
    """Junta as linhas da tela numa fala contínua, com pausa onde a linha não tem pontuação."""
    linhas = [linha if linha[-1] in ".!?:,…" else linha + ","
              for linha in texto.strip().split("\n") if linha.strip()]
    fala = " ".join(linhas)
    for escrita, falada in PRONUNCIA.items():
        fala = fala.replace(escrita, falada)
    return fala


def duracao(arquivo):
    saida = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                            "-of", "csv=p=0", str(arquivo)], capture_output=True, text=True, check=True)
    return float(saida.stdout)


async def gerar(texto, destino):
    with tempfile.TemporaryDirectory() as pasta:
        bruto = Path(pasta) / "bruto.mp3"
        await edge_tts.Communicate(para_fala(texto), VOZ, rate=RITMO, pitch=TOM).save(str(bruto))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(bruto), "-af", FILTRO,
                        str(destino)], check=True)


async def principal():
    PASTA_NARRACAO.mkdir(parents=True, exist_ok=True)
    esperados = {}
    for chave, blocos in NARRACOES.items():
        for indice, texto in enumerate(blocos):
            esperados[arquivo_narracao(chave, indice, texto)] = texto

    for antigo in set(PASTA_NARRACAO.glob("*.mp3")) - set(esperados):
        antigo.unlink()
        print(f"removido {antigo.name}")
    for arquivo, texto in esperados.items():
        if not arquivo.exists():
            await gerar(texto, arquivo)
            print(f"gerado {arquivo.name}")

    tempos = {arquivo.name: round(duracao(arquivo), 2) for arquivo in sorted(esperados)}
    ARQUIVO_DURACOES.write_text(json.dumps(tempos, indent=2), encoding="utf-8")
    print(f"{len(tempos)} narrações prontas, {sum(tempos.values()) / 60:.1f} minutos de voz.")


if __name__ == "__main__":
    asyncio.run(principal())
