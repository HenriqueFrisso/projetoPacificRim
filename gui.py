"""Interface gráfica (tkinter) da campanha de Pacific Rim.

Reaproveita toda a lógica do main.py: a campanha roda numa thread própria e
print/input/prompt/limpar_tela são redirecionados para a janela. Como o tkinter
só pode ser tocado pela thread principal, a campanha envia pedidos por uma fila
e espera a resposta do jogador em outra.
"""
import builtins
import queue
import re
import sys
import threading
import tkinter as tk
from pathlib import Path

import dificuldade
import main
import util
from centroOperacoes.cronometro import Cronometro
from repositorios.repositorios import RepositorioJaegers, RepositorioPilotos

FUNDO = "#0b1622"
PAINEL = "#12263a"
TEXTO = "#d6e9ff"
DESTAQUE = "#ff8c1a"
BOTAO = "#1d3d5e"
BOTAO_ATIVO = "#2d5a87"
FONTE = ("DejaVu Sans Mono", 11)
FONTE_BOTAO = ("DejaVu Sans", 11)

# Cores ANSI usadas pelo jogo (info de Jaegers e Kaijus) viram tags de texto.
CORES_ANSI = {"33": "#ff9f43", "90": "#8a96a3", "91": "#ff5c5c", "92": "#5cff8f",
              "93": "#ffe066", "94": "#6cb6ff", "95": "#ff79e1", "96": "#5ce1ff"}
ANSI = re.compile(r"\x1b\[(\d+)m")
# A fonte da janela não tem emojis; troca pelos símbolos equivalentes que ela desenha.
EMOJIS = str.maketrans({"🔒": "✖", "💰": "✖", "🩹": "✚", "✅": "✔", "❌": "✖", "️": ""})

# Recortes (x0, y0, x1, y1) de cada quadro nas folhas de sprites de assets/.
PASTA_ASSETS = Path(__file__).with_name("assets")
SPRITES_JAEGER = ("pixellab-Crie-um---Jaeger-original-insp-1792831001850.png", {
    "parado": (10, 10, 69, 84), "soco": (79, 12, 155, 84), "lamina": (164, 13, 247, 84),
    "pulso": (10, 97, 92, 167), "raio": (97, 97, 185, 167), "dano": (16, 178, 61, 247),
    "vitoria": (132, 167, 185, 247), "destruido": (195, 190, 242, 245),
})
SPRITES_KAIJU = ("pixellab-Crie-um---kaiju-original-inspi-1792830676332.png", {
    "parado": (7, 101, 82, 166), "rugido": (179, 16, 253, 81), "garras": (87, 104, 169, 167),
    "acido": (171, 98, 256, 167), "explosao": (175, 188, 252, 252), "dano": (4, 184, 82, 251),
    "derrota": (87, 206, 170, 250),
})
QUADRO_ATAQUE = {
    "PUNHO_ENERGIZADO": "soco", "SOCO_NUCLEAR": "soco", "LAMINA_DE_PLASMA": "lamina",
    "LAMINAS_GIRATORIAS": "lamina", "RAIO_DE_ENERGIA": "raio", "PULSO_ELETRICO": "pulso",
    "GARRAS": "garras", "ACIDO": "acido", "EXPLOSAO": "explosao",
}
ESCALA_SPRITE = 3
ALTURA_CENA = 320


class Saida:
    """Substitui sys.stdout: tudo que o jogo imprime vai para a janela."""

    def __init__(self, janela):
        self.janela = janela

    def write(self, texto):
        self.janela.na_tela(self.janela.escrever, texto)

    def flush(self):
        pass


class Janela:
    def __init__(self):
        self.raiz = tk.Tk()
        self.raiz.title("Pacific Rim — Shatterdome")
        self.raiz.geometry("1200x760")
        self.raiz.minsize(900, 600)
        self.raiz.configure(bg=FUNDO)
        self.tarefas = queue.Queue()
        self.cor_atual = None

        lateral = tk.Frame(self.raiz, bg=PAINEL, width=320)
        lateral.pack(side="right", fill="y")
        lateral.pack_propagate(False)
        tk.Label(lateral, text="STATUS DO SHATTERDOME", bg=PAINEL, fg=DESTAQUE,
                 font=("DejaVu Sans", 12, "bold")).pack(pady=(12, 4))
        self.status = tk.Canvas(lateral, bg=PAINEL, highlightthickness=0)
        self.status.pack(fill="both", expand=True, padx=12, pady=4)

        principal = tk.Frame(self.raiz, bg=FUNDO)
        principal.pack(side="left", fill="both", expand=True)
        self.texto = tk.Text(principal, bg=FUNDO, fg=TEXTO, font=FONTE, wrap="word",
                             relief="flat", padx=16, pady=12, state="disabled",
                             insertbackground=TEXTO)
        self.texto.pack(fill="both", expand=True)
        for codigo, cor in CORES_ANSI.items():
            self.texto.tag_configure(codigo, foreground=cor)

        # Cena de batalha: aparece acima do texto só durante os combates.
        self.cena = tk.Canvas(principal, bg=FUNDO, height=ALTURA_CENA, highlightthickness=0)
        self.sprites = {"jaeger": self._carregar_sprites(*SPRITES_JAEGER, espelhar=False),
                        "kaiju": self._carregar_sprites(*SPRITES_KAIJU, espelhar=True)}

        # Área de ações: botões, campo de texto ou caixas de seleção.
        self.acoes = tk.Frame(principal, bg=PAINEL)
        self.acoes.pack(fill="x")

        self.raiz.after(30, self._processar_tarefas)
        self.raiz.after(300, self._atualizar_status)

    # === Comunicação entre threads ===
    def na_tela(self, funcao, *args):
        """Agenda uma função para rodar na thread da janela."""
        self.tarefas.put((funcao, args))

    def _processar_tarefas(self):
        try:
            while True:
                funcao, args = self.tarefas.get_nowait()
                funcao(*args)
        except queue.Empty:
            pass
        self.raiz.after(30, self._processar_tarefas)

    def _perguntar(self, montar, *args):
        """Chamado pela thread do jogo: monta a pergunta e espera o jogador."""
        resposta = queue.Queue()
        self.na_tela(montar, resposta.put, *args)
        return resposta.get()

    # === Saída de texto ===
    def escrever(self, texto):
        self.texto.configure(state="normal")
        partes = ANSI.split(texto.translate(EMOJIS))
        # split alterna texto e código: [texto, código, texto, ...]
        for indice, parte in enumerate(partes):
            if indice % 2:
                self.cor_atual = parte if parte in CORES_ANSI else None
            elif parte:
                self.texto.insert("end", parte, self.cor_atual or ())
        self.texto.see("end")
        self.texto.configure(state="disabled")

    def limpar_tela(self):
        self.na_tela(self._limpar)

    def _limpar(self):
        self.cena.pack_forget()
        self.texto.configure(state="normal")
        self.texto.delete("1.0", "end")
        self.texto.configure(state="disabled")

    # === Entrada do jogador (chamadas pela thread do jogo) ===
    def input(self, mensagem=""):
        return self._perguntar(self._montar_pausa, str(mensagem).strip())

    def prompt(self, perguntas):
        resultado = {}
        for pergunta in perguntas:
            montar = {"input": self._montar_texto,
                      "checkbox": self._montar_caixas}.get(pergunta.get("type"), self._montar_lista)
            resultado[pergunta["name"]] = self._perguntar(montar, pergunta)
        return resultado

    # === Montagem dos controles (thread da janela) ===
    def _limpar_acoes(self, mensagem=""):
        for filho in self.acoes.winfo_children():
            filho.destroy()
        self.raiz.unbind("<Return>")
        if mensagem:
            tk.Label(self.acoes, text=mensagem, bg=PAINEL, fg=DESTAQUE, anchor="w",
                     font=("DejaVu Sans", 11, "bold")).pack(fill="x", padx=12, pady=(10, 4))

    def _botao(self, pai, texto, acao):
        botao = tk.Button(pai, text=texto, command=acao, bg=BOTAO, fg=TEXTO, font=FONTE_BOTAO,
                          activebackground=BOTAO_ATIVO, activeforeground="white",
                          relief="flat", anchor="w", padx=12, pady=5, cursor="hand2")
        botao.bind("<Enter>", lambda _: botao.configure(bg=BOTAO_ATIVO))
        botao.bind("<Leave>", lambda _: botao.configure(bg=BOTAO))
        return botao

    def _area_rolavel(self):
        """Lista de opções com rolagem, para menus com muitos pilotos ou Jaegers."""
        caixa = tk.Frame(self.acoes, bg=PAINEL)
        caixa.pack(fill="x", padx=12, pady=(0, 10))
        tela = tk.Canvas(caixa, bg=PAINEL, highlightthickness=0, height=10)
        barra = tk.Scrollbar(caixa, orient="vertical", command=tela.yview)
        interno = tk.Frame(tela, bg=PAINEL)
        janela_interna = tela.create_window((0, 0), window=interno, anchor="nw")

        def ajustar(_=None):
            altura = min(interno.winfo_reqheight(), 300)
            tela.configure(scrollregion=tela.bbox("all"), height=altura)
            if interno.winfo_reqheight() > 300:
                barra.pack(side="right", fill="y")

        interno.bind("<Configure>", ajustar)
        tela.bind("<Configure>", lambda e: tela.itemconfigure(janela_interna, width=e.width))
        tela.configure(yscrollcommand=barra.set)
        tela.pack(side="left", fill="x", expand=True)
        rolar = lambda e: tela.yview_scroll(-1 if (e.num == 4 or e.delta > 0) else 1, "units")
        for evento in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            tela.bind_all(evento, rolar)
        return interno

    @staticmethod
    def _opcao(item):
        """Normaliza uma opção: (texto, valor, selecionável)."""
        if isinstance(item, util.Separator):
            return getattr(item, "_line", str(item)).translate(EMOJIS), None, False
        if isinstance(item, dict):
            return str(item["name"]).translate(EMOJIS), item.get("value", item["name"]), True
        return str(item).translate(EMOJIS), item, True

    def _montar_lista(self, responder, pergunta):
        self._limpar_acoes(pergunta.get("message") or "Escolha:")
        area = self._area_rolavel()

        def escolher(valor):
            self._limpar_acoes()
            responder(valor)

        primeiro = None
        for item in pergunta.get("choices", []):
            texto, valor, selecionavel = self._opcao(item)
            if not selecionavel:
                tk.Label(area, text=texto, bg=PAINEL, fg="#6b7c8f", anchor="w",
                         font=FONTE_BOTAO, padx=12).pack(fill="x", pady=1)
                continue
            botao = self._botao(area, texto, lambda v=valor: escolher(v))
            botao.pack(fill="x", pady=2)
            primeiro = primeiro or botao
        if primeiro:
            primeiro.focus_set()
            self.raiz.bind("<Return>", lambda _: self.raiz.focus_get().invoke()
                           if isinstance(self.raiz.focus_get(), tk.Button) else None)

    def _montar_texto(self, responder, pergunta):
        self._limpar_acoes(pergunta.get("message", ""))
        linha = tk.Frame(self.acoes, bg=PAINEL)
        linha.pack(fill="x", padx=12, pady=(0, 10))
        campo = tk.Entry(linha, bg=FUNDO, fg=TEXTO, insertbackground=TEXTO, font=FONTE,
                         relief="flat")
        campo.insert(0, pergunta.get("default", ""))
        campo.pack(side="left", fill="x", expand=True, ipady=5)
        campo.focus_set()
        campo.select_range(0, "end")

        def confirmar(_=None):
            valor = campo.get()
            self._limpar_acoes()
            responder(valor)

        self._botao(linha, "Confirmar", confirmar).pack(side="left", padx=(8, 0))
        self.raiz.bind("<Return>", confirmar)

    def _montar_caixas(self, responder, pergunta):
        self._limpar_acoes(pergunta.get("message", ""))
        area = self._area_rolavel()
        marcadas = []
        for item in pergunta.get("choices", []):
            texto, valor, selecionavel = self._opcao(item)
            if not selecionavel:
                continue
            marcada = tk.BooleanVar()
            tk.Checkbutton(area, text=texto, variable=marcada, bg=PAINEL, fg=TEXTO,
                           selectcolor=FUNDO, activebackground=PAINEL, activeforeground=TEXTO,
                           font=FONTE_BOTAO, anchor="w").pack(fill="x", pady=1)
            marcadas.append((marcada, valor))

        def confirmar(_=None):
            selecionados = [valor for marcada, valor in marcadas if marcada.get()]
            self._limpar_acoes()
            responder(selecionados)

        self._botao(self.acoes, "Confirmar seleção", confirmar).pack(anchor="e", padx=12, pady=(0, 10))
        self.raiz.bind("<Return>", confirmar)

    def _montar_pausa(self, responder, mensagem):
        self._limpar_acoes()

        def continuar(_=None):
            self._limpar_acoes()
            responder("")

        botao = self._botao(self.acoes, f"▶  {mensagem or 'Continuar'}", continuar)
        botao.pack(fill="x", padx=12, pady=10)
        botao.focus_set()
        self.raiz.bind("<Return>", continuar)

    # === Cena de batalha ===
    def _carregar_sprites(self, arquivo, quadros, espelhar):
        folha = tk.PhotoImage(file=str(PASTA_ASSETS / arquivo))
        sprites = {}
        for nome, caixa in quadros.items():
            sprite = tk.PhotoImage()
            sprite.tk.call(sprite, "copy", folha, "-from", *caixa,
                           "-zoom", ESCALA_SPRITE, ESCALA_SPRITE)
            if espelhar:  # o Kaiju fica à direita, olhando para o Jaeger
                espelhado = tk.PhotoImage()
                espelhado.tk.call(espelhado, "copy", sprite, "-subsample", -1, 1)
                sprite = espelhado
            sprites[nome] = sprite
        return sprites

    def batalha(self, tipo, **dados):
        """Chamado pela thread do jogo; espera a animação terminar."""
        self._perguntar(self._animar_batalha, tipo, dados)

    def _animar_batalha(self, terminar, tipo, dados):
        if tipo == "inicio":
            self._montar_cena(dados["jaeger"], dados["kaiju"])
            self.raiz.after(700, terminar, None)
        elif tipo == "golpe":
            self._animar_golpe(dados["atacante"], dados["ataque"], dados["dano"], terminar)
        else:
            self._animar_fim(dados["vencedor"], terminar)

    def _montar_cena(self, jaeger, kaiju):
        self.lutadores = {"jaeger": jaeger, "kaiju": kaiju}
        cena = self.cena
        cena.pack(before=self.texto, fill="x")
        cena.update_idletasks()
        largura = max(cena.winfo_width(), 600)
        self.chao = ALTURA_CENA - 20
        cena.delete("all")

        # Céu em faixas, lua, cidade costeira e mar.
        for faixa in range(12):
            tom = 22 + faixa * 4
            cena.create_rectangle(0, faixa * 24, largura, (faixa + 1) * 24, outline="",
                                  fill=f"#{tom // 3:02x}{tom:02x}{tom + 30:02x}")
        cena.create_oval(largura - 170, 80, largura - 120, 130, fill="#e8eef5", outline="")
        for x, altura in ((0.05, 70), (0.12, 110), (0.2, 85), (0.42, 120), (0.5, 90),
                          (0.58, 140), (0.66, 75), (0.85, 100), (0.93, 130)):
            cena.create_rectangle(largura * x, self.chao - altura, largura * x + 46, self.chao,
                                  fill="#0a1520", outline="")
        cena.create_rectangle(0, self.chao - 30, largura, ALTURA_CENA, fill="#0e2f44", outline="")
        for onda in range(0, largura, 60):
            cena.create_line(onda, self.chao - 12, onda + 30, self.chao - 12, fill="#2a6f8f")

        self.posicao = {"jaeger": largura * 0.27, "kaiju": largura * 0.73}
        self.figuras = {
            lado: cena.create_image(self.posicao[lado], self.chao, anchor="s",
                                    image=self.sprites[lado]["parado"])
            for lado in ("jaeger", "kaiju")
        }
        self.barras = {}
        for lado, x0, cor in (("jaeger", 20, "#5cff8f"), ("kaiju", largura / 2 + 20, "#ff5c5c")):
            cena.create_text(x0, 12, text=str(self.lutadores[lado].nome), anchor="nw",
                             fill=TEXTO, font=("DejaVu Sans", 12, "bold"))
            cena.create_rectangle(x0, 36, x0 + largura / 2 - 40, 50, fill="#081018", outline="#2d5a87")
            self.barras[lado] = (cena.create_rectangle(x0, 36, x0 + largura / 2 - 40, 50,
                                                       fill=cor, outline=""), x0, largura / 2 - 40)
        cena.create_text(largura / 2, 70, text="VS", fill=DESTAQUE, font=("DejaVu Sans", 20, "bold"))
        self._atualizar_barras()

    def _atualizar_barras(self):
        for lado, (barra, x0, largura) in self.barras.items():
            saude = max(self.lutadores[lado].saude, 0)
            self.cena.coords(barra, x0, 36, x0 + largura * saude / 100, 50)

    def _sequencia(self, passos, terminar):
        """Executa (espera_ms, ação) em ordem sem travar a janela."""
        if not passos:
            return terminar(None)
        espera, acao = passos[0]
        acao()
        self.raiz.after(espera, self._sequencia, passos[1:], terminar)

    def _quadro(self, lado, nome):
        self.cena.itemconfigure(self.figuras[lado], image=self.sprites[lado][nome])

    def _mover(self, lado, dx):
        self.cena.coords(self.figuras[lado], self.posicao[lado] + dx, self.chao)

    def _animar_golpe(self, atacante, ataque, dano, terminar):
        defensor = "kaiju" if atacante == "jaeger" else "jaeger"
        avanco = 50 if atacante == "jaeger" else -50
        recuo = 10 if atacante == "jaeger" else -10
        x_texto = self.posicao[defensor]
        texto = []

        def golpear():
            self._quadro(atacante, QUADRO_ATAQUE.get(ataque, "parado"))
            self._mover(atacante, avanco)

        def impacto():
            if dano > 0:
                self._quadro(defensor, "dano")
                self._mover(defensor, recuo)
                texto.append(self.cena.create_text(x_texto, self.chao - 200, text=f"-{dano}",
                                                   fill="#ff5c5c", font=("DejaVu Sans", 22, "bold")))
            else:
                texto.append(self.cena.create_text(x_texto, self.chao - 200, text="ERROU",
                                                   fill="#8a96a3", font=("DejaVu Sans", 18, "bold")))
            self._atualizar_barras()

        def tremer():
            self._mover(defensor, -recuo if dano > 0 else 0)
            self.cena.move(texto[0], 0, -12)

        def voltar():
            self.cena.delete(texto[0])
            self._mover(atacante, 0)
            self._mover(defensor, 0)
            self._quadro(atacante, "parado")
            if self.lutadores[defensor].saude > 0:
                self._quadro(defensor, "parado")

        self._sequencia([(220, golpear), (110, impacto), (110, tremer),
                         (260, lambda: self.cena.move(texto[0], 0, -12)), (0, voltar)], terminar)

    def _animar_fim(self, vencedor, terminar):
        perdedor = "kaiju" if vencedor == "jaeger" else "jaeger"
        self._quadro(vencedor, "vitoria" if vencedor == "jaeger" else "rugido")
        self._quadro(perdedor, "destruido" if perdedor == "jaeger" else "derrota")
        self._atualizar_barras()
        largura = max(self.cena.winfo_width(), 600)
        mensagem, cor = (("VITÓRIA", "#5cff8f") if vencedor == "jaeger" else ("DERROTA", "#ff5c5c"))
        self.cena.create_text(largura / 2 + 3, ALTURA_CENA / 2 + 3, text=mensagem, fill="#000000",
                              font=("DejaVu Sans", 44, "bold"))
        self.cena.create_text(largura / 2, ALTURA_CENA / 2, text=mensagem, fill=cor,
                              font=("DejaVu Sans", 44, "bold"))
        self.raiz.after(2200, terminar, None)

    # === Painel de status ===
    def _atualizar_status(self):
        try:
            self._desenhar_status()
        except Exception:
            pass  # o estado pode mudar no meio do desenho; o próximo ciclo corrige
        self.raiz.after(500, self._atualizar_status)

    def _desenhar_status(self):
        tela = self.status
        tela.delete("all")
        largura = max(tela.winfo_width(), 200)
        y = 4

        def linha(texto, cor=TEXTO, negrito=False, salto=20):
            nonlocal y
            tela.create_text(0, y, text=texto, anchor="nw", fill=cor,
                             font=("DejaVu Sans", 10, "bold" if negrito else "normal"))
            y += salto

        def barra(valor, cor):
            nonlocal y
            tela.create_rectangle(0, y, largura - 4, y + 10, fill=FUNDO, outline="")
            tela.create_rectangle(0, y, (largura - 4) * max(valor, 0) / 100, y + 10,
                                  fill=cor, outline="")
            y += 18

        def cor_saude(valor):
            return "#5cff8f" if valor >= 70 else "#ffe066" if valor >= 35 else "#ff5c5c"

        cronometro = Cronometro()
        dias = (cronometro.data_fim - cronometro.data_atual).days
        linha(f"Data: {cronometro.data_atual.strftime('%d/%m/%Y')}")
        linha(f"Dias até o fim do mundo: {dias}", DESTAQUE, True)
        linha(f"Ameaça atual: categoria {max(cronometro.obter_categoria_atual(), 1)}")
        linha(f"Dificuldade: {dificuldade.atual['nome']}")
        if main.orcamento_atual:
            linha(f"Créditos: ₡ {main.orcamento_atual.saldo:,}".replace(",", "."), "#5cff8f", True)
        y += 10

        linha("JAEGERS", DESTAQUE, True)
        jaegers = RepositorioJaegers.listar()
        if not jaegers:
            linha("Nenhum construído", "#6b7c8f")
        for jaeger in jaegers:
            linha(f"{jaeger.nome} · {jaeger.categoria.name} · {jaeger.estado.name}", salto=16)
            linha(f"Pilotos {len(jaeger.pilotos)}/2 · integridade {jaeger.saude}%", "#8a96a3",
                  salto=16)
            barra(jaeger.saude, cor_saude(jaeger.saude))
        y += 10

        linha("PILOTOS", DESTAQUE, True)
        pilotos = RepositorioPilotos.listar()
        if not pilotos:
            linha("Nenhum treinado", "#6b7c8f")
        for piloto in pilotos:
            local = piloto.jaeger.nome if piloto.jaeger else "reserva"
            linha(f"{piloto.nome} · {piloto.personalidade} · {local}", salto=16)
            barra(piloto.saude, cor_saude(piloto.saude))

    def fechar(self):
        self.na_tela(self.raiz.destroy)


def jogar(janela):
    try:
        main.prologo()
        while main.painel() == "Reiniciar história":
            main.nova_campanha()
    finally:
        janela.fechar()


if __name__ == "__main__":
    janela = Janela()
    util.usar_interface(janela)
    sys.stdout = Saida(janela)
    builtins.input = janela.input
    threading.Thread(target=jogar, args=(janela,), daemon=True).start()
    janela.raiz.mainloop()
