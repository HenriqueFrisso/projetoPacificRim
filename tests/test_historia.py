import centroOperacoes.historia as historia


def test_todo_momento_de_historia_tem_voz_gerada():
    tempos = historia.duracoes()
    for chave, blocos in historia.NARRACOES.items():
        for indice, texto in enumerate(blocos):
            arquivo = historia.arquivo_narracao(chave, indice, texto)
            assert arquivo.exists(), f"rode gerar_narracao.py: falta {arquivo.name}"
            assert tempos[arquivo.name] > 0


def test_texto_mudado_invalida_o_audio_antigo():
    assert (historia.arquivo_narracao("prologo", 0, "texto antigo")
            != historia.arquivo_narracao("prologo", 0, "texto novo"))


def test_texto_acompanha_a_duracao_da_fala(monkeypatch):
    esperas, ritmos = [], []

    class AudioFalso:
        def poll(self):
            esperas.append(True)
            return 0  # a fala já acabou

    monkeypatch.setattr(historia, "tocar", lambda arquivo: AudioFalso())
    monkeypatch.setattr(historia, "narrar", lambda texto, ritmo: ritmos.append(ritmo))
    historia.contar("pitfall")

    texto = historia.NARRACOES["pitfall"][0]
    duracao = historia.duracoes()[historia.arquivo_narracao("pitfall", 0, texto).name]
    linhas = texto.count("\n") + 1
    tempo_digitando = ritmos[0] * (len(texto) + 10 * linhas + 50)
    assert abs(tempo_digitando - duracao * 0.9) < 0.01  # o texto termina junto com a fala
    assert esperas == [True]  # e a tela só avança quando a fala acaba


def test_sem_voz_o_texto_usa_o_ritmo_padrao(monkeypatch):
    ritmos = []
    monkeypatch.setattr(historia, "narrar", lambda texto, ritmo: ritmos.append(ritmo))
    historia.contar("pitfall")
    assert ritmos == [0.03]


def test_pular_encerra_a_historia_inteira(monkeypatch):
    telas = []

    def narrar(texto, ritmo):
        telas.append(texto)
        historia.pular.set()  # o jogador aperta "Pular" na primeira tela

    monkeypatch.setattr(historia, "narrar", narrar)
    historia.contar("prologo")
    assert len(telas) == 1
    assert not historia.pular.is_set()  # a próxima história começa normal
