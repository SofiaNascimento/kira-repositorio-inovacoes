"""Paginas de apoio: Acessibilidade e Ajuda (fundacao-do-redesign, RED-33 a RED-36).

Fonte: docs/design-spec.md v2 §5.4 e .specs/features/fundacao-do-redesign/spec.md.
Toda AC de "exibido" usa `exibido(html, rigoroso=True)` sobre a pagina inteira (L-028, L-030).
"""

import re
from html.parser import HTMLParser

import pytest

from inovacoes.tests.test_views_sistema_design import paginas  # noqa: F401
from inovacoes.tests.visibilidade import exibido
from nucleo.tests.test_casca import (
    CABECALHO_DE_PAGINA,
    MENU,
    NAV_ATALHOS,
    _main,
    _menu_da_tela,
    _texto,
    _trilha,
)

pytestmark = pytest.mark.django_db

AUTENTICADO = pytest.mark.parametrize("autenticado", [False, True], ids=["anonimo", "autenticado"])


def _pagina(client, autor, autenticado, caminho):
    if autenticado:
        client.force_login(autor)
    resposta = client.get(caminho)
    assert resposta.status_code == 200
    return resposta.content.decode()


def _secoes(html):
    """[(h2, texto exibido ate o proximo h2)] do main exibido."""
    main = _main(exibido(html, rigoroso=True))
    partes = re.split(r"<h2\b[^>]*>(.*?)</h2>", main, flags=re.S)
    return [(_texto(partes[i]), _texto(partes[i + 1])) for i in range(1, len(partes), 2)]


def _cabecalho_so_com_a_marca(html):
    """RED-36: o header exibido tem so o link da marca; sem menu nem area do usuario."""
    tela = exibido(html, rigoroso=True)
    cabecalho = tela[tela.index("<header>") : tela.index("</header>")]
    assert "<nav" not in cabecalho
    assert 'class="usuario"' not in cabecalho
    assert re.findall(r'<a\b[^>]*href="([^"]*)"', cabecalho) == ["/"]


# --- RED-33, RED-34, RED-36: Acessibilidade ------------------------------------------

SECOES_ACESSIBILIDADE = [
    "Compromisso",
    "Atalhos de teclado",
    "Alto contraste",
    "Ampliação",
    "Relatar uma barreira",
]
AVISO_DE_CONFLITO = (
    "Se o leitor de tela ou o sistema operacional já usa a mesma combinação, "
    "o atalho dele prevalece."
)


@AUTENTICADO
def test_acessibilidade_responde_com_a_trilha_e_o_h1(client, autor, autenticado):
    """RED-33: publica, 200, trilha "Acessibilidade" e h1 "Acessibilidade"."""
    html = _pagina(client, autor, autenticado, "/acessibilidade/")
    assert _trilha(html) == [("Acessibilidade", None, "page")]
    assert len(re.findall(r"<h1\b", html)) == 1
    assert CABECALHO_DE_PAGINA.search(_main(exibido(html, rigoroso=True))).group(1) == (
        "Acessibilidade"
    )
    assert "<title>Acessibilidade · Repositório de Inovações</title>" in html


@AUTENTICADO
def test_acessibilidade_tem_as_cinco_secoes_em_ordem_com_texto(client, autor, autenticado):
    """RED-33: os h2 da §5.4, nessa ordem, cada um com conteudo exibido."""
    secoes = _secoes(_pagina(client, autor, autenticado, "/acessibilidade/"))
    assert [titulo for titulo, _ in secoes] == SECOES_ACESSIBILIDADE
    for titulo, texto in secoes:
        assert texto, titulo


class Tabela(HTMLParser):
    """Legenda e linhas da primeira tabela: cada celula como (tag, scope, texto)."""

    def __init__(self):
        super().__init__()
        self.legenda = None
        self.linhas = []
        self._celula = None
        self._na_legenda = False

    def handle_starttag(self, tag, attrs):
        if tag == "caption":
            self._na_legenda, self.legenda = True, ""
        elif tag == "tr":
            self.linhas.append([])
        elif tag in {"th", "td"}:
            self._celula = [tag, dict(attrs).get("scope"), ""]
            self.linhas[-1].append(self._celula)

    def handle_endtag(self, tag):
        if tag == "caption":
            self._na_legenda = False
        elif tag in {"th", "td"}:
            self._celula = None

    def handle_data(self, data):
        if self._na_legenda:
            self.legenda += data
        elif self._celula is not None:
            self._celula[2] += data


def _tabela_de_atalhos(html):
    """A tabela exibida da secao "Atalhos de teclado"."""
    main = _main(exibido(html, rigoroso=True))
    inicio = main.index(">Atalhos de teclado</h2>")
    trecho = main[inicio : main.index("<h2", inicio)]
    assert trecho.count("<table") == 1
    tabela = Tabela()
    tabela.feed(trecho)
    linhas = [[(t, s, " ".join(x.split())) for t, s, x in linha] for linha in tabela.linhas]
    return " ".join(tabela.legenda.split()), linhas


@AUTENTICADO
def test_tabela_de_atalhos_tem_legenda_e_cabecalhos_de_coluna(client, autor, autenticado):
    """RED-34: caption e th scope="col" com os navegadores da §5.1."""
    legenda, linhas = _tabela_de_atalhos(_pagina(client, autor, autenticado, "/acessibilidade/"))
    assert legenda
    assert linhas[0] == [
        ("th", "col", "Atalho"),
        ("th", "col", "Leva a"),
        ("th", "col", "Chrome e Edge no Windows"),
        ("th", "col", "Firefox"),
        ("th", "col", "macOS"),
    ]
    assert len(linhas) == 4


@AUTENTICADO
@pytest.mark.parametrize(
    ("numero", "destino"),
    [("1", "Conteúdo principal"), ("2", "Menu principal"), ("3", "Busca de inovações")],
)
def test_cada_atalho_tem_a_combinacao_de_cada_navegador(
    client, autor, autenticado, numero, destino
):
    """RED-34: Alt + n; Alt + Shift + n; Control + Option + n."""
    _, linhas = _tabela_de_atalhos(_pagina(client, autor, autenticado, "/acessibilidade/"))
    assert linhas[int(numero)] == [
        ("th", "row", numero),
        ("td", None, destino),
        ("td", None, f"Alt + {numero}"),
        ("td", None, f"Alt + Shift + {numero}"),
        ("td", None, f"Control + Option + {numero}"),
    ]


@AUTENTICADO
def test_atalhos_avisam_que_o_leitor_de_tela_ou_o_sistema_prevalece(client, autor, autenticado):
    """RED-34: o aviso generico de conflito, exibido na secao dos atalhos."""
    secoes = dict(_secoes(_pagina(client, autor, autenticado, "/acessibilidade/")))
    assert AVISO_DE_CONFLITO in secoes["Atalhos de teclado"]


def test_acessibilidade_anonima_tem_so_a_marca_no_cabecalho(client, autor):
    """RED-36: sem sessao, nem menu nem area do usuario."""
    _cabecalho_so_com_a_marca(_pagina(client, autor, False, "/acessibilidade/"))


def test_acessibilidade_autenticada_tem_o_menu_sem_pagina_atual(client, autor):
    """RED-17, RED-18: tela autenticada fora da secao; nenhum aria-current no menu."""
    html = _pagina(client, autor, True, "/acessibilidade/")
    itens = _menu_da_tela(html)
    assert [(href, texto) for href, _, texto in itens] == MENU
    assert [corrente for _, corrente, _ in itens] == [None, None, None]
    assert "aria-current" not in html[html.index("<header>") : html.index("</header>")]


def test_barra_de_toda_pagina_leva_a_acessibilidade(paginas):  # noqa: F811
    """RED-33, §5.1: o link "Acessibilidade" exibido na barra, depois dos atalhos."""
    for nome, html in paginas.items():
        tela = exibido(html, rigoroso=True)
        barra = tela[tela.index(NAV_ATALHOS) : tela.index("<header>")]
        depois_dos_atalhos = barra[barra.index("</nav>") :]
        assert re.findall(r'<a href="/acessibilidade/">([^<]*)</a>', depois_dos_atalhos) == [
            "Acessibilidade"
        ], nome


# --- RED-30, RED-35, RED-36: Ajuda ---------------------------------------------------

SECOES_AJUDA = [
    "Buscar uma inovação",
    "Cadastrar uma inovação",
    "Avançar o status",
    "Precisa de ajuda?",
]


@AUTENTICADO
def test_ajuda_responde_com_a_trilha_e_o_h1(client, autor, autenticado):
    """RED-35, RED-30: publica, 200, trilha "Ajuda" e h1 "Ajuda"."""
    html = _pagina(client, autor, autenticado, "/ajuda/")
    assert _trilha(html) == [("Ajuda", None, "page")]
    assert len(re.findall(r"<h1\b", html)) == 1
    assert CABECALHO_DE_PAGINA.search(_main(exibido(html, rigoroso=True))).group(1) == "Ajuda"
    assert "<title>Ajuda · Repositório de Inovações</title>" in html


@AUTENTICADO
def test_ajuda_tem_as_quatro_secoes_em_ordem(client, autor, autenticado):
    """RED-35: os h2 da Ajuda, nessa ordem, e nenhum outro."""
    secoes = _secoes(_pagina(client, autor, autenticado, "/ajuda/"))
    assert [titulo for titulo, _ in secoes] == SECOES_AJUDA


@AUTENTICADO
@pytest.mark.parametrize("secao", SECOES_AJUDA)
def test_cada_secao_da_ajuda_e_seguida_de_texto_exibido(client, autor, autenticado, secao):
    """RED-35: cada h2 com uma explicacao que aparece na tela."""
    secoes = dict(_secoes(_pagina(client, autor, autenticado, "/ajuda/")))
    assert len(secoes[secao].split()) >= 5, secao


def test_ajuda_anonima_tem_so_a_marca_no_cabecalho(client, autor):
    """RED-36: sem sessao, nem menu nem area do usuario."""
    _cabecalho_so_com_a_marca(_pagina(client, autor, False, "/ajuda/"))


def test_ajuda_autenticada_tem_o_menu_sem_pagina_atual(client, autor):
    """RED-17, RED-18: fora da secao do menu, nenhum aria-current."""
    html = _pagina(client, autor, True, "/ajuda/")
    itens = _menu_da_tela(html)
    assert [(href, texto) for href, _, texto in itens] == MENU
    assert [corrente for _, corrente, _ in itens] == [None, None, None]
