import random
import re
from pathlib import Path

import audio
import gerar_efeitos
import main
from jaegers.ataques import AtaquesJaeger
from kaijus.ataques import AtaquesKaiju
from kaijus.categorias import CategoriaKaiju
from kaijus.factoryKaiju import FabricaKaiju


def test_todo_efeito_usado_existe():
    codigo = Path(main.__file__).read_text(encoding="utf-8")
    usados = set(re.findall(r'efeito\("(\w+)"', codigo)) | set(main.SOM_ATAQUE.values())
    for nome in usados:
        assert nome in gerar_efeitos.EFEITOS, nome
        assert (audio.PASTA_EFEITOS / f"{nome}.wav").exists(), f"rode gerar_efeitos.py: falta {nome}"


def test_todo_ataque_tem_som():
    ataques = {a.name for a in AtaquesJaeger} | {a.name for a in AtaquesKaiju}
    assert ataques <= set(main.SOM_ATAQUE)


def test_batalha_toca_rugido_golpes_e_desfecho(novo_jaeger, monkeypatch):
    sons = []
    monkeypatch.setattr(main, "efeito", lambda nome, atraso=0: sons.append(nome))
    random.seed(2)
    jaeger = novo_jaeger(forca=600, durabilidade=600, ataque=AtaquesJaeger.LAMINA_DE_PLASMA)

    main.batalha_por_turnos(jaeger, FabricaKaiju().criarKaijuCategoria(CategoriaKaiju.I))

    assert sons[0] == "rugido" and sons[-1] == "vitoria"
    assert sons[1] == "lamina" and sons[2] in ("impacto", "erro")


def test_som_desligado_nao_toca_nada():
    # o conftest desliga o som em todos os testes
    assert audio.tocar(audio.PASTA_EFEITOS / "soco.wav") is None
