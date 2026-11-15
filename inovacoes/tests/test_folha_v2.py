"""Folha central v2 (fundacao-do-redesign, RED-01 a RED-12).

Fonte: docs/design-spec.md v2 §2 a §6 e .specs/features/fundacao-do-redesign/spec.md.
Os helpers da folha sao os do sistema de design (DS-06 a DS-09), importados sem mudanca.
"""

import re
from html.parser import HTMLParser

import pytest

# `paginas` e a fixture do DS-02 a DS-05, reusada sem mudanca.
from inovacoes.tests.test_views_sistema_design import (
    CSS,
    paginas,  # noqa: F401
)

URL_DA_FONTE = "/static/fontes/inter-latin-wght-normal.woff2"


def _sem_comentarios(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


# --- RED-05: @font-face da Inter ------------------------------------------------


def _font_face():
    blocos = re.findall(r"@font-face\s*\{([^}]*)\}", _sem_comentarios(CSS))
    assert len(blocos) == 1
    return dict(
        (nome.strip(), valor.strip())
        for nome, valor in re.findall(r"([\w-]+)\s*:\s*([^;]+);", blocos[0])
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    ("propriedade", "valor"),
    [
        ("font-family", "Inter"),
        ("font-display", "swap"),
        ("font-weight", "400 800"),
        ("src", f"url({URL_DA_FONTE}) format(woff2)"),
    ],
)
def test_font_face_declara_a_inter_servida_pelo_projeto(propriedade, valor):
    """RED-05."""
    assert _font_face()[propriedade] == valor


# --- RED-08: nenhum recurso de outra origem --------------------------------------


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lista = []

    def handle_starttag(self, tag, attrs):
        self.lista.append((tag, dict(attrs), self.get_starttag_text()))


def _tags(html):
    parser = Tags()
    parser.feed(html)
    return parser.lista


EXTERNO = re.compile(r"https?://", re.I)


@pytest.mark.unit
def test_folha_nao_importa_nem_aponta_para_outra_origem():
    """RED-08: nenhum @import nem url( com http:// ou https:// na folha."""
    css = _sem_comentarios(CSS)
    for chamada in re.findall(r"@import[^;]*;|url\([^)]*\)", css, re.I):
        assert not EXTERNO.search(chamada), chamada


def test_nenhuma_pagina_carrega_recurso_de_outra_origem(paginas):  # noqa: F811
    """RED-08: link, script e img sem http(s)://; o unico style e a folha (DS-02)."""
    for nome, html in paginas.items():
        for tag, _, texto in _tags(html):
            if tag in ("link", "script", "img"):
                assert not EXTERNO.search(texto), (nome, texto)
        for estilo in re.findall(r"<style>(.*?)</style>", html, re.S):
            for chamada in re.findall(r"@import[^;]*;|url\([^)]*\)", estilo, re.I):
                assert not EXTERNO.search(chamada), (nome, chamada)


def test_toda_pagina_faz_preload_da_fonte_na_mesma_url(paginas):  # noqa: F811
    """RED-05, RED-06: o preload aponta para a URL do @font-face, com crossorigin."""
    for nome, html in paginas.items():
        preloads = [a for t, a, _ in _tags(html) if t == "link" and a.get("rel") == "preload"]
        assert len(preloads) == 1, nome
        assert preloads[0] == {
            "rel": "preload",
            "href": URL_DA_FONTE,
            "as": "font",
            "type": "font/woff2",
            "crossorigin": None,
        }, nome
