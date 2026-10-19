"""O HTML que a pagina de fato exibe (L-028, L-030).

`exibido(html)` devolve o mesmo HTML sem os comentarios e sem a subarvore de todo
elemento que sai da tela, do leitor de tela ou do teclado: `hidden`, `inert`,
`aria-hidden="true"` (em qualquer caixa), `<template>` e o conteudo de um
`<details>` fechado fora do `<summary>`. O que sobra sai com o texto original das
tags, para que os helpers de regex dos testes rodem sobre ele sem mudar.
"""

from html.parser import HTMLParser

VAZIOS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source"}
VAZIOS |= {"track", "wbr"}


def escondido(tag, atributos):
    """O elemento, por si, sai da tela, do leitor de tela ou do teclado."""
    if tag == "template" or "hidden" in atributos or "inert" in atributos:
        return True
    return (atributos.get("aria-hidden") or "").strip().lower() == "true"


class Exibido(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.saida = []
        # Um item por elemento aberto: (tag, escondido com os ancestrais, details fechado).
        self.pilha = []

    def _escondendo(self):
        return bool(self.pilha) and self.pilha[-1][1]

    def _fora_do_summary(self, tag):
        return bool(self.pilha) and self.pilha[-1][2] and tag != "summary"

    def _abrir(self, tag, attrs):
        atributos = {nome: valor for nome, valor in attrs}
        oculto = self._escondendo() or self._fora_do_summary(tag) or escondido(tag, atributos)
        if not oculto:
            self.saida.append(self.get_starttag_text())
        return oculto, tag == "details" and "open" not in atributos

    def handle_starttag(self, tag, attrs):
        oculto, fechado = self._abrir(tag, attrs)
        if tag not in VAZIOS:
            self.pilha.append((tag, oculto, fechado))

    def handle_startendtag(self, tag, attrs):
        self._abrir(tag, attrs)

    def handle_endtag(self, tag):
        if tag not in [aberta for aberta, _, _ in self.pilha]:
            if not self._escondendo():
                self.saida.append(f"</{tag}>")
            return
        while True:
            aberta, oculto, _ = self.pilha.pop()
            if aberta == tag:
                break
        if not oculto:
            self.saida.append(f"</{tag}>")

    def _texto(self, texto):
        if not self._escondendo() and not (self.pilha and self.pilha[-1][2]):
            self.saida.append(texto)

    def handle_data(self, data):
        self._texto(data)

    def handle_entityref(self, name):
        self._texto(f"&{name};")

    def handle_charref(self, name):
        self._texto(f"&#{name};")

    def handle_decl(self, decl):
        self.saida.append(f"<!{decl}>")


def exibido(html):
    parser = Exibido()
    parser.feed(html)
    parser.close()
    return "".join(parser.saida)
