"""Casca do sistema (fundacao-do-redesign, RED-13 a RED-22, RED-29 a RED-31, RED-41).

Fonte: docs/design-spec.md v2 §5 e .specs/features/fundacao-do-redesign/spec.md.
Toda AC de "exibido" usa `exibido(html, rigoroso=True)` sobre a pagina inteira (L-028, L-030).
"""

import re
from pathlib import Path

import pytest
from django.conf import settings
from django.template.loader import render_to_string
from django.test import RequestFactory
from django.urls import resolve

# `paginas` e a fixture do DS-02 a DS-05, reusada sem mudanca.
from inovacoes.tests.test_views_sistema_design import (
    _elementos,
    _focavel,
    paginas,  # noqa: F401
)
from inovacoes.tests.visibilidade import exibido
from nucleo.context_processors import casca

# --- T7: context processor da casca (RED-17, RED-18, RED-26, RED-40, RED-14) ------


def _requisicao(caminho, cookies=None, resolvida=True):
    requisicao = RequestFactory().get(caminho)
    requisicao.COOKIES.update(cookies or {})
    requisicao.resolver_match = resolve(caminho) if resolvida else None
    return requisicao


def _menu(caminho, resolvida=True):
    contexto = casca(_requisicao(caminho, resolvida=resolvida))
    return contexto["menu_atual"], contexto["menu_estado"]


@pytest.mark.unit
@pytest.mark.parametrize(
    ("caminho", "esperado"),
    [
        ("/inovacoes/", ("inovacoes", "page")),
        ("/inovacoes/nova/", ("nova", "page")),
        ("/indicadores/", ("indicadores", "page")),
    ],
)
def test_destino_exato_do_menu_e_a_pagina_atual(caminho, esperado):
    """RED-17: aria-current="page" so no destino exato."""
    assert _menu(caminho) == esperado


@pytest.mark.unit
@pytest.mark.parametrize(
    "caminho",
    [
        "/inovacoes/7/",
        "/inovacoes/7/editar/",
        "/inovacoes/7/excluir/",
        "/inovacoes/7/status/",
        "/inovacoes/7/reaproveitar/",
    ],
)
def test_telas_da_secao_marcam_inovacoes_como_secao(caminho):
    """RED-18: aria-current="true" em Inovacoes nas telas da secao."""
    assert _menu(caminho) == ("inovacoes", "true")


@pytest.mark.unit
def test_rota_fora_do_menu_nao_tem_pagina_atual():
    """RED-17, RED-18: o login nao marca nenhum item."""
    assert _menu("/entrar/") == (None, None)


@pytest.mark.unit
def test_sem_rota_resolvida_nao_tem_pagina_atual():
    """RED-17: a 404 de URL inexistente chega sem resolver_match."""
    assert _menu("/nao-existe/", resolvida=False) == (None, None)


@pytest.mark.unit
def test_cookie_alto_liga_o_alto_contraste():
    """RED-26."""
    requisicao = _requisicao("/inovacoes/", {"kira_contraste": "alto"})
    assert casca(requisicao)["contraste_alto"] is True


@pytest.mark.unit
@pytest.mark.parametrize(
    "cookies", [{}, {"kira_contraste": "ALTO"}, {"kira_contraste": "sim"}, {"kira_contraste": ""}]
)
def test_outro_valor_ou_cookie_ausente_deixa_o_tema_normal(cookies):
    """RED-40: so o valor exato "alto" liga o tema."""
    assert casca(_requisicao("/inovacoes/", cookies))["contraste_alto"] is False


@pytest.mark.unit
@pytest.mark.parametrize(
    ("caminho", "esperado"),
    [
        ("/inovacoes/", "#id_q"),
        ("/inovacoes/7/", "/inovacoes/#id_q"),
        ("/indicadores/", "/inovacoes/#id_q"),
        ("/inovacoes/nova/", "/inovacoes/#id_q"),
    ],
)
def test_atalho_da_busca_aponta_para_o_campo_da_lista(caminho, esperado):
    """RED-14: #id_q na lista, /inovacoes/#id_q nas outras telas."""
    assert casca(_requisicao(caminho))["busca_href"] == esperado


# --- T8: icones do Lucide (RED-07, RED-16) ---------------------------------------

ICONES = Path(settings.BASE_DIR) / "templates" / "icones"

NOMES_DOS_ICONES = ["lampada", "circulo-mais", "grafico-barras", "contraste"]


@pytest.mark.unit
def test_pasta_traz_os_quatro_icones_da_casca():
    """RED-16, RED-23: lampada, circulo com mais, grafico e meio circulo."""
    assert sorted(a.stem for a in ICONES.glob("*.svg")) == sorted(NOMES_DOS_ICONES)


@pytest.mark.unit
@pytest.mark.parametrize("nome", NOMES_DOS_ICONES)
def test_icone_e_um_svg_decorativo_no_traco_do_texto(nome):
    """RED-16: SVG aria-hidden, fora do Tab, na cor do texto, sem nome acessivel."""
    fonte = (ICONES / f"{nome}.svg").read_text()
    assert fonte.startswith("<svg ")
    abertura = fonte[: fonte.index(">") + 1]
    for atributo in [
        'aria-hidden="true"',
        'focusable="false"',
        'stroke="currentColor"',
        'fill="none"',
    ]:
        assert atributo in abertura, atributo
    assert "<title" not in fonte
    assert not re.search(r"\sid=", fonte)
    assert fonte.rstrip().endswith("</svg>")


@pytest.mark.unit
def test_licenca_dos_icones_acompanha_os_arquivos():
    """RED-07: o ISC do Lucide e o MIT do Feather."""
    licenca = (ICONES / "LICENSE").read_text()
    assert "ISC License" in licenca
    assert "Lucide" in licenca
    assert "The MIT License (MIT)" in licenca
    assert "Cole Bemis" in licenca


# --- T9: barra de acessibilidade e faixa da marca (RED-13 a RED-15, RED-21, RED-41) --

NAV_ATALHOS = '<nav aria-label="Atalhos de acessibilidade">'
FAIXA = '<div class="faixa-marca decorativo" aria-hidden="true"></div>'
ATALHO_1 = ("#conteudo", "1", "Ir para o conteúdo principal")


def _atalhos(html):
    """(href, accesskey, texto) de cada link exibido do nav de atalhos, que vem antes do header."""
    tela = exibido(html, rigoroso=True)
    inicio = tela.index(NAV_ATALHOS)
    assert inicio < tela.index("<header>")
    trecho = tela[inicio : tela.index("</nav>", inicio)]
    return [
        (atributos.get("href"), atributos.get("accesskey"), texto.strip())
        for tag, atributos, texto in _elementos(trecho)
        if tag == "a"
    ]


def _seguido_do_numero(html, href, numero):
    """O link do atalho e logo depois o kbd com o numero, decorativo (fora do link)."""
    return re.search(
        rf'<a href="{re.escape(href)}" accesskey="{numero}">[^<]*</a>\s*'
        rf'<kbd aria-hidden="true">{numero}</kbd>',
        html,
    )


def test_primeiro_focavel_exibido_e_o_atalho_1_na_barra(paginas):  # noqa: F811
    """RED-13, RED-41: em toda pagina (inclusive a 500 sem request), antes do header."""
    for nome, html in paginas.items():
        tela = exibido(html, rigoroso=True)
        tag, atributos, texto = next(e for e in _elementos(tela) if _focavel(e[0], e[1]))
        assert (tag, atributos.get("href"), atributos.get("accesskey"), texto.strip()) == (
            "a",
            *ATALHO_1,
        ), nome
        assert _atalhos(html)[0] == ATALHO_1, nome
        assert _seguido_do_numero(html, "#conteudo", "1"), nome
        assert html.index(NAV_ATALHOS) < html.index("<header>"), nome


@pytest.mark.parametrize(
    ("pagina", "busca"),
    [
        ("/inovacoes/", "#id_q"),
        ("/inovacoes/{id}/", "/inovacoes/#id_q"),
        ("/indicadores/", "/inovacoes/#id_q"),
    ],
)
def test_autenticado_tem_os_atalhos_do_menu_e_da_busca(
    client, autor, criar_inovacao, pagina, busca
):
    """RED-14: atalhos 2 (#menu) e 3 (busca: #id_q na lista, /inovacoes/#id_q fora dela)."""
    client.force_login(autor)
    resposta = client.get(pagina.format(id=criar_inovacao().pk))
    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert _atalhos(html) == [
        ATALHO_1,
        ("#menu", "2", "Ir para o menu"),
        (busca, "3", "Ir para a busca"),
    ]
    assert _seguido_do_numero(html, "#menu", "2")
    assert _seguido_do_numero(html, busca, "3")


@pytest.mark.django_db
def test_anonimo_so_tem_o_atalho_do_conteudo(client):
    """RED-15: sem sessao, nenhum accesskey 2 ou 3."""
    html = client.get("/entrar/").content.decode()
    assert _atalhos(html) == [ATALHO_1]
    assert 'accesskey="2"' not in html
    assert 'accesskey="3"' not in html


def test_faixa_da_marca_e_decorativa_entre_a_barra_e_o_header(paginas):  # noqa: F811
    """RED-21, RED-41: a faixa, sem texto e aria-hidden, entre a barra e o header."""
    for nome, html in paginas.items():
        fim_da_barra = html.index("</nav>", html.index(NAV_ATALHOS))
        faixa = html.index(FAIXA)
        assert fim_da_barra < faixa < html.index("<header>"), nome
        assert html.count('class="faixa-marca') == 1, nome
        assert FAIXA not in exibido(html, rigoroso=True), nome


@pytest.mark.unit
def test_500_sem_request_tem_o_atalho_1_e_a_faixa():
    """RED-41: o server_error renderiza o 500.html sem request nem usuario."""
    html = render_to_string("500.html")
    assert _atalhos(html) == [ATALHO_1]
    assert _seguido_do_numero(html, "#conteudo", "1")
    assert FAIXA in html
