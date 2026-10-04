"""Testes e2e de acessibilidade por teclado da listagem e do detalhe (CONS-41, RNF09).

Lidos do HTML da pagina inteira; a T18 acrescenta a pagina com o formulario de busca.
"""

import re

import pytest

from inovacoes.tests.test_views_acessibilidade import PAPEIS_DE_CONTROLE, Pagina

NATIVOS = {"a", "button", "input", "select", "textarea"}
PAGINAS = ["lista_paginada", "lista_com_busca", "detalhe"]


@pytest.fixture
def pagina(request, client, autor, criar_inovacao):
    client.force_login(autor)
    if request.param == "lista_paginada":
        for n in range(21):
            criar_inovacao(titulo=f"Inovacao {n}")
        url = "/inovacoes/"
    elif request.param == "lista_com_busca":
        criar_inovacao(titulo="Caixa x", status="VALIDADA")
        url = "/inovacoes/?q=x&status=VALIDADA"
    else:
        url = f"/inovacoes/{criar_inovacao().pk}/"
    html = client.get(url).content.decode()
    if request.param == "lista_paginada":
        assert 'aria-label="Paginação"' in html, "a evidencia exige paginacao ativa"
    parser = Pagina()
    parser.feed(html)
    parser.html = html
    return parser


@pytest.mark.parametrize("pagina", PAGINAS, indirect=True)
def test_pagina_sem_tabindex_positivo(pagina):
    """CONS-41: a ordem do teclado e a ordem do documento."""
    for tag, atributos, _ in pagina.elementos:
        if "tabindex" in atributos:
            assert int(atributos["tabindex"]) <= 0, tag


@pytest.mark.parametrize("pagina", PAGINAS, indirect=True)
def test_pagina_so_tem_controles_nativos(pagina):
    """CONS-41: todo elemento interativo e a[href], button, input, select ou textarea."""
    for tag, atributos, _ in pagina.elementos:
        if atributos.get("role") in PAPEIS_DE_CONTROLE:
            raise AssertionError(f"controle nao nativo: <{tag} role={atributos['role']}>")
        if "onclick" in atributos or "contenteditable" in atributos:
            raise AssertionError(f"controle nao nativo: <{tag}>")
        if tag == "a":
            assert "href" in atributos, "a sem href nao e um link nativo"
        if "tabindex" in atributos:
            assert tag in NATIVOS, f"<{tag} tabindex> torna interativo um elemento nao nativo"
    tags = {tag for tag, _, _ in pagina.elementos}
    assert "a" in tags


@pytest.mark.parametrize("pagina", PAGINAS, indirect=True)
def test_pagina_tem_foco_visivel_com_contorno(pagina):
    """CONS-41: regra :focus-visible com outline na folha de estilo da pagina."""
    css = " ".join(re.findall(r"<style>(.*?)</style>", pagina.html, re.S))
    regra = re.search(r"(^|[\s}]):focus-visible\s*\{([^}]*)\}", css)
    assert regra, "falta a regra :focus-visible"
    assert re.search(r"outline\s*:\s*\d+px\s+solid", regra.group(2))
    assert not re.search(r"outline\s*:\s*(none|0)\b", css)
