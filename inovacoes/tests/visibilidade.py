"""O HTML que a pagina de fato exibe (L-028, L-030).

`exibido(html)` devolve o mesmo HTML sem os comentarios e sem a subarvore de todo
elemento que sai da tela, do leitor de tela ou do teclado: `hidden`, `inert`,
`aria-hidden="true"` (em qualquer caixa), `<template>` e o conteudo de um
`<details>` fechado fora do `<summary>`. O que sobra sai com o texto original das
tags, para que os helpers de regex dos testes rodem sobre ele sem mudar.

`exibido(html, rigoroso=True)` esconde tambem (fundacao-do-redesign, T1): controle de
formulario com `disabled`, elemento com `role` `presentation` ou `none` (em qualquer
caixa) e elemento com uma classe que a `kira.css` declara com `display: none` numa regra
de seletor de classe simples, fora de at-rule (`@media` etc.) e fora de
`[data-contraste=alto]`.
"""

import re
from html.parser import HTMLParser
from pathlib import Path

VAZIOS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source"}
VAZIOS |= {"track", "wbr"}

CONTROLES = {"button", "fieldset", "input", "optgroup", "option", "select", "textarea"}
KIRA_CSS = Path(__file__).resolve().parents[2] / "templates" / "kira.css"


def _sem_at_rules(css):
    """O CSS sem nenhum bloco de at-rule (`@media`, `@font-face`...), com o aninhado."""
    saida, i = [], 0
    while (inicio := css.find("@", i)) != -1:
        saida.append(css[i:inicio])
        abre = css.find("{", inicio)
        fim_sem_bloco = css.find(";", inicio)
        if abre == -1 or (fim_sem_bloco != -1 and fim_sem_bloco < abre):
            i = fim_sem_bloco + 1 if fim_sem_bloco != -1 else len(css)
            continue
        nivel, i = 1, abre + 1
        while nivel and i < len(css):
            nivel += {"{": 1, "}": -1}.get(css[i], 0)
            i += 1
    saida.append(css[i:])
    return "".join(saida)


def classes_ocultas(css):
    """Classes que a folha esconde em regra global de seletor de classe simples."""
    css = _sem_at_rules(re.sub(r"/\*.*?\*/", "", css, flags=re.S))
    classes = set()
    for seletores, corpo in re.findall(r"([^{}]+)\{([^}]*)\}", css):
        if re.search(r"(?:^|;)\s*display\s*:\s*none\s*(?:!important\s*)?(?:;|$)", corpo.strip()):
            for seletor in seletores.split(","):
                if simples := re.fullmatch(r"\.(-?[_a-zA-Z][\w-]*)", seletor.strip()):
                    classes.add(simples.group(1))
    return classes


CLASSES_OCULTAS = classes_ocultas(KIRA_CSS.read_text())


def escondido(tag, atributos):
    """O elemento, por si, sai da tela, do leitor de tela ou do teclado."""
    if tag == "template" or "hidden" in atributos or "inert" in atributos:
        return True
    return (atributos.get("aria-hidden") or "").strip().lower() == "true"


def escondido_no_rigoroso(tag, atributos):
    """Vetores que so o modo rigoroso considera (F6, L2 a L4)."""
    if tag in CONTROLES and "disabled" in atributos:
        return True
    if (atributos.get("role") or "").strip().lower() in {"presentation", "none"}:
        return True
    return bool(CLASSES_OCULTAS & set((atributos.get("class") or "").split()))


class Exibido(HTMLParser):
    def __init__(self, rigoroso=False):
        super().__init__(convert_charrefs=False)
        self.rigoroso = rigoroso
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
        oculto = oculto or (self.rigoroso and escondido_no_rigoroso(tag, atributos))
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


def exibido(html, rigoroso=False):
    parser = Exibido(rigoroso)
    parser.feed(html)
    parser.close()
    return "".join(parser.saida)
