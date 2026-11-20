"""Casca do sistema (fundacao-do-redesign, RED-13 a RED-22, RED-29 a RED-31, RED-41).

Fonte: docs/design-spec.md v2 §5 e .specs/features/fundacao-do-redesign/spec.md.
Toda AC de "exibido" usa `exibido(html, rigoroso=True)` sobre a pagina inteira (L-028, L-030).
"""

import re
from html.parser import HTMLParser
from pathlib import Path

import pytest
from django.conf import settings
from django.template import Context, Template
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

NOMES_DOS_ICONES_DA_CASCA = ["lampada", "circulo-mais", "grafico-barras", "contraste"]

# R2 (redesign-consulta, RCON-15): status no selo (frasco, visto, caixa-seta), busca,
# remocao de etiqueta, alternador (grade, tabela), metadados do cartao (predio,
# etiqueta, repetir).
NOMES_DOS_ICONES_DA_CONSULTA = [
    "frasco",
    "visto",
    "caixa-seta",
    "lupa",
    "fechar",
    "grade",
    "tabela",
    "predio",
    "etiqueta",
    "repetir",
]

NOMES_DOS_ICONES = NOMES_DOS_ICONES_DA_CASCA + NOMES_DOS_ICONES_DA_CONSULTA


@pytest.mark.unit
def test_pasta_traz_os_icones_da_casca_e_da_consulta():
    """RED-16, RED-23: lampada, circulo com mais, grafico e meio circulo.

    T-O (redesign-consulta, T6): a pasta deixa de ter exatamente os 4 da R1 e passa a ter
    os 4 da R1 mais os 10 da R2 (RCON-15), nem mais nem menos. A garantia da RED-16 e da
    RED-23 continua: os 4 da casca estao la.
    """
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
    # T-O (redesign-consulta, T6): nenhum estilo embutido no icone (AD-010).
    assert "style" not in fonte
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


# --- T10: menu com icones, pagina atual e area do usuario (RED-16 a RED-18, RED-20) --

MENU = [
    ("/inovacoes/", "Inovações"),
    ("/inovacoes/nova/", "Cadastrar inovação"),
    ("/indicadores/", "Indicadores"),
]
ABRE_MENU = re.compile(r'<nav id="menu" aria-label="Principal">')


def _texto(trecho):
    return " ".join(re.sub(r"<[^>]*>", " ", trecho).split())


def _menu_da_tela(html):
    """(href, aria-current, texto exibido) de cada link do menu, sobre o exibido rigoroso."""
    tela = exibido(html, rigoroso=True)
    cabecalho = tela[tela.index("<header>") : tela.index("</header>")]
    inicio = ABRE_MENU.search(cabecalho).start()
    trecho = cabecalho[inicio : cabecalho.index("</nav>", inicio)]
    itens = []
    for abertura, conteudo in re.findall(r"(<a\b[^>]*>)(.*?)</a>", trecho, re.S):
        (tag, atributos, _), *_ = _elementos(abertura)
        itens.append((atributos.get("href"), atributos.get("aria-current"), _texto(conteudo)))
    return itens


@pytest.mark.parametrize("pagina", ["/inovacoes/", "/inovacoes/{id}/"])
def test_menu_tem_os_tres_itens_em_ordem_cada_um_com_icone_antes_do_texto(
    client, autor, criar_inovacao, pagina
):
    """RED-16: nav#menu "Principal", icone SVG decorativo antes de cada texto."""
    client.force_login(autor)
    html = client.get(pagina.format(id=criar_inovacao().pk)).content.decode()
    assert [(href, texto) for href, _, texto in _menu_da_tela(html)] == MENU
    cabecalho = html[html.index("<header>") : html.index("</header>")]
    inicio = ABRE_MENU.search(cabecalho).start()
    trecho = cabecalho[inicio : cabecalho.index("</nav>", inicio)]
    conteudos = re.findall(r"<a\b[^>]*>(.*?)</a>", trecho, re.S)
    assert len(conteudos) == 3
    for conteudo, (_, rotulo) in zip(conteudos, MENU, strict=True):
        svg = re.match(
            r'\s*<svg aria-hidden="true" focusable="false"[^>]*>.*?</svg>', conteudo, re.S
        )
        assert svg, rotulo
        assert _texto(conteudo[svg.end() :]) == rotulo


FORMAS = {"path", "circle", "rect", "line", "polyline", "polygon", "ellipse"}


class Formas(HTMLParser):
    """(tag, atributos) de cada elemento de forma de um SVG, em ordem."""

    def __init__(self):
        super().__init__()
        self.formas = []

    def handle_starttag(self, tag, attrs):
        if tag in FORMAS:
            self.formas.append((tag, tuple(sorted(attrs))))

    handle_startendtag = handle_starttag


def _formas(svg):
    parser = Formas()
    parser.feed(svg)
    return parser.formas


def _formas_do_icone_inicial(conteudo):
    """Formas do SVG que abre o conteudo; o texto so vem depois dele."""
    svg = re.match(r"\s*<svg\b[^>]*>.*?</svg>", conteudo, re.S)
    assert svg
    return _formas(svg.group())


ICONE_DO_ITEM = {
    "Inovações": "lampada",
    "Cadastrar inovação": "circulo-mais",
    "Indicadores": "grafico-barras",
}


def test_cada_item_do_menu_tem_o_seu_icone(client, autor):
    """RED-16: lampada em Inovacoes, circulo com mais em Cadastrar, grafico em Indicadores."""
    client.force_login(autor)
    html = client.get("/inovacoes/").content.decode()
    cabecalho = html[html.index("<header>") : html.index("</header>")]
    inicio = ABRE_MENU.search(cabecalho).start()
    trecho = cabecalho[inicio : cabecalho.index("</nav>", inicio)]
    itens = re.findall(r"<a\b[^>]*>(.*?)</a>", trecho, re.S)
    assert len(itens) == len(ICONE_DO_ITEM)
    for conteudo, (rotulo, nome) in zip(itens, ICONE_DO_ITEM.items(), strict=True):
        arquivo = _formas((ICONES / f"{nome}.svg").read_text())
        assert arquivo, nome
        assert _formas_do_icone_inicial(conteudo) == arquivo, rotulo


@pytest.mark.parametrize("autenticado", [False, True])
def test_botao_de_contraste_tem_o_icone_de_meio_circulo(client, autor, autenticado):
    """RED-23: o botao "Alto contraste" abre com o icone de meio circulo (contraste.svg)."""
    if autenticado:
        client.force_login(autor)
    html = client.get("/inovacoes/" if autenticado else "/entrar/").content.decode()
    barra = html[html.index('<div class="barra-acessibilidade">') : html.index("<header>")]
    botoes = re.findall(r'<button\b[^>]*name="contraste"[^>]*>(.*?)</button>', barra, re.S)
    assert len(botoes) == 1
    arquivo = _formas((ICONES / "contraste.svg").read_text())
    assert arquivo
    assert _formas_do_icone_inicial(botoes[0]) == arquivo


@pytest.mark.parametrize(
    ("pagina", "conta", "atual"),
    [
        ("/inovacoes/", "autor", {"Inovações": "page"}),
        ("/inovacoes/nova/", "autor", {"Cadastrar inovação": "page"}),
        ("/indicadores/", "autor", {"Indicadores": "page"}),
        ("/inovacoes/{id}/", "autor", {"Inovações": "true"}),
        ("/inovacoes/{id}/editar/", "autor", {"Inovações": "true"}),
        ("/inovacoes/{id}/excluir/", "autor", {"Inovações": "true"}),
        ("/inovacoes/{id}/status/", "autor", {"Inovações": "true"}),
        ("/inovacoes/{disponivel}/reaproveitar/", "autor", {"Inovações": "true"}),
        ("/inovacoes/999999/", "autor", {"Inovações": "true"}),
        ("/inovacoes/{id}/editar/", "terceiro", {"Inovações": "true"}),
    ],
)
def test_menu_marca_a_pagina_atual_ou_a_secao(
    client, autor, terceiro, criar_inovacao, pagina, conta, atual
):
    """RED-17 (page no destino exato), RED-18 (true na secao, 404 e 403), nada fora disso."""
    inovacao = criar_inovacao()
    disponivel = criar_inovacao(titulo="Disponivel", status="DISPONIVEL_PARA_REPLICACAO")
    client.force_login({"autor": autor, "terceiro": terceiro}[conta])
    resposta = client.get(pagina.format(id=inovacao.pk, disponivel=disponivel.pk))
    esperado = 404 if pagina == "/inovacoes/999999/" else 200
    if conta == "terceiro":
        esperado = 403
    assert resposta.status_code == esperado
    itens = _menu_da_tela(resposta.content.decode())
    assert [(href, texto) for href, _, texto in itens] == MENU
    assert {texto: corrente for _, corrente, texto in itens if corrente} == atual


def test_menu_sem_rota_resolvida_nao_marca_nenhum_item(autor):
    """RED-17, RED-18: sem rota resolvida, nenhum aria-current.

    A tela autenticada fora da secao (/acessibilidade/) e testada pelo client em
    test_paginas_apoio. A requisicao sem rota nao chega ao base pelo client (a 404 de
    URL inexistente e a do Django), entao o base e renderizado com ela.
    """
    requisicao = _requisicao("/entrar/", resolvida=False)
    requisicao.user = autor
    html = render_to_string("base.html", request=requisicao)
    itens = _menu_da_tela(html)
    assert [(href, texto) for href, _, texto in itens] == MENU
    assert [corrente for _, corrente, _ in itens] == [None, None, None]
    assert "aria-current" not in html[html.index("<header>") : html.index("</header>")]


def _area_do_usuario(html):
    cabecalho = html[html.index("<header>") : html.index("</header>")]
    inicio = cabecalho.index('<div class="usuario">')
    return cabecalho, cabecalho[inicio:]


@pytest.mark.parametrize(
    ("conta", "nome", "iniciais"), [("autor", "Ana Souza", "AS"), ("terceiro", "bruno", "B")]
)
def test_area_do_usuario_mostra_o_nome_e_as_iniciais_decorativas(
    client, autor, terceiro, conta, nome, iniciais
):
    """RED-20: nome completo (ou username) num span sem atributo; iniciais aria-hidden; Sair."""
    client.force_login({"autor": autor, "terceiro": terceiro}[conta])
    html = client.get("/inovacoes/").content.decode()
    _, usuario = _area_do_usuario(html)
    assert f'<span class="usuario__iniciais" aria-hidden="true">{iniciais}</span>' in usuario
    # Na tela e no leitor de tela: o nome, depois do menu e antes do Sair; as iniciais, nao.
    tela_cabecalho, tela_usuario = _area_do_usuario(exibido(html, rigoroso=True))
    nome_exibido = re.search(rf"<span>{re.escape(nome)}</span>", tela_usuario)
    sair = re.search(r"<button[^>]*>\s*Sair\s*</button>", tela_usuario)
    assert nome_exibido and sair
    assert nome_exibido.start() < sair.start()
    assert tela_cabecalho.index("</nav>") < tela_cabecalho.index('<div class="usuario">')
    assert _texto(tela_usuario.split("<form")[0]) == nome


# --- T11: cabecalho de pagina e h1 pelo bloco (RED-29, RED-31) --------------------

# Texto de hoje do h1 de cada tela da fixture `paginas` (RED-31: o mesmo texto).
H1_DE_HOJE = {
    "lista": "Inovações",
    "nova": "Cadastrar inovação",
    "detalhe": "Controle de Caixa",
    "editar": "Editar inovação",
    "excluir": "Excluir inovação",
    "status": "Avançar status",
    "reaproveitar": "Sinalizar reaproveitamento",
    "painel": "Painel de indicadores",
    "nao_encontrada": "Inovação não encontrada.",
    "acesso_negado": "Acesso negado",
    "erro_500": "Algo deu errado do nosso lado",
}
# T-O (redesign-consulta, estendido a lista, T15, RCON-01): depois do h1, dentro do
# cabecalho de pagina, podem vir a descricao (um p) e a acao principal (um link), nessa
# ordem e nada mais. A garantia do RED-29/RED-31 continua: o h1 unico e o primeiro titulo
# do main, logo depois do status.
CABECALHO_DE_PAGINA = re.compile(
    r'^<main id="conteudo">\s*<div role="status">.*?</div>\s*'
    r'<div class="cabecalho-pagina">\s*<h1>(.*?)</h1>\s*'
    r"(?:<p>[^<]*</p>\s*)?(?:<a\b[^>]*>[^<]*</a>\s*)?</div>",
    re.S,
)


def _main(html):
    return html[html.index('<main id="conteudo">') : html.index("</main>")]


@pytest.mark.parametrize("nome", H1_DE_HOJE)
def test_h1_unico_abre_o_main_no_cabecalho_de_pagina(paginas, nome):  # noqa: F811
    """RED-29, RED-31: depois do status, antes do conteudo, com o texto de hoje."""
    html = paginas[nome]
    assert len(re.findall(r"<h1\b", html)) == 1
    cabecalho = CABECALHO_DE_PAGINA.search(_main(exibido(html, rigoroso=True)))
    assert cabecalho
    assert cabecalho.group(1) == H1_DE_HOJE[nome]


def test_login_mantem_o_h1_entrar_no_cartao_sem_cabecalho_de_pagina(paginas):  # noqa: F811
    """RED-31: a excecao do login, ate o passe dele."""
    tela = exibido(paginas["login"], rigoroso=True)
    assert re.findall(r"<h1[^>]*>(.*?)</h1>", paginas["login"], re.S) == ["Entrar"]
    assert 'class="cabecalho-pagina"' not in paginas["login"]
    main = _main(tela)
    assert main.index('<div class="cartao cartao--estreito">') < main.index("<h1>Entrar</h1>")
    assert main.index("<h1>Entrar</h1>") < main.index("<form")


def _estendendo_o_base(blocos):
    return Template('{% extends "base.html" %}' + blocos).render(Context())


@pytest.mark.unit
def test_descricao_e_acao_principal_vem_nessa_ordem_depois_do_h1():
    """RED-29: titulo, descricao e acao_principal, nessa ordem, no cabecalho de pagina."""
    html = _estendendo_o_base(
        "{% block titulo %}Título de teste{% endblock %}"
        "{% block descricao %}<p>Descrição de teste.</p>{% endblock %}"
        '{% block acao_principal %}<a class="botao" href="/inovacoes/nova/">Ação</a>{% endblock %}'
    )
    assert re.search(
        r'<div class="cabecalho-pagina">\s*<h1>Título de teste</h1>\s*'
        r"<p>Descrição de teste\.</p>\s*"
        r'<a class="botao" href="/inovacoes/nova/">Ação</a>\s*</div>',
        _main(exibido(html, rigoroso=True)),
    )


@pytest.mark.unit
def test_sem_descricao_nem_acao_o_cabecalho_de_pagina_so_tem_o_h1():
    """RED-29: blocos vazios nao renderizam nada."""
    html = _estendendo_o_base("{% block titulo %}Título de teste{% endblock %}")
    assert CABECALHO_DE_PAGINA.search(_main(html)).group(1) == "Título de teste"


# --- T12: trilha de navegacao (RED-29, RED-30) -------------------------------------

ABRE_TRILHA = '<nav class="trilha" aria-label="Você está em">'


class Trilha(HTMLParser):
    """(texto, href do link ou None, aria-current) de cada li da ol da trilha."""

    def __init__(self):
        super().__init__()
        self.itens = []
        self.dentro = False

    def handle_starttag(self, tag, attrs):
        atributos = dict(attrs)
        if tag == "li":
            self.itens.append(["", None, atributos.get("aria-current")])
            self.dentro = True
        elif tag == "a" and self.dentro:
            self.itens[-1][1] = atributos.get("href")

    def handle_endtag(self, tag):
        if tag == "li":
            self.dentro = False

    def handle_data(self, data):
        if self.dentro:
            self.itens[-1][0] += data


def _trilha(html):
    """Itens da trilha exibida; a nav fica depois do header e antes do main."""
    tela = exibido(html, rigoroso=True)
    assert tela.count(ABRE_TRILHA) == 1
    inicio = tela.index(ABRE_TRILHA)
    assert tela.index("</header>") < inicio < tela.index('<main id="conteudo">')
    trecho = tela[inicio : tela.index("</nav>", inicio)]
    assert re.search(r"<nav[^>]*>\s*<div[^>]*>\s*<ol>", trecho)
    parser = Trilha()
    parser.feed(trecho)
    return [(" ".join(texto.split()), href, corrente) for texto, href, corrente in parser.itens]


RAIZ = ("Inovações", "/inovacoes/", None)


@pytest.mark.parametrize(
    ("pagina", "itens"),
    [
        ("/inovacoes/", [("Inovações", None, "page")]),
        ("/inovacoes/{id}/", [RAIZ, ("{titulo}", None, "page")]),
        ("/inovacoes/nova/", [RAIZ, ("Cadastrar inovação", None, "page")]),
        (
            "/inovacoes/{id}/editar/",
            [RAIZ, ("{titulo}", "{detalhe}", None), ("Editar", None, "page")],
        ),
        (
            "/inovacoes/{id}/status/",
            [RAIZ, ("{titulo}", "{detalhe}", None), ("Avançar status", None, "page")],
        ),
        (
            "/inovacoes/{id}/reaproveitar/",
            [RAIZ, ("{titulo}", "{detalhe}", None), ("Sinalizar reaproveitamento", None, "page")],
        ),
        (
            "/inovacoes/{id}/excluir/",
            [RAIZ, ("{titulo}", "{detalhe}", None), ("Excluir", None, "page")],
        ),
        ("/indicadores/", [("Indicadores", None, "page")]),
    ],
)
def test_tela_mostra_a_trilha_da_tabela(client, autor, criar_inovacao, pagina, itens):
    """RED-30: itens da §5.3 em ordem; os do meio com link, o ultimo com aria-current."""
    # REAP-03: a sinalizacao so abre em inovacao "Disponível para replicação".
    inovacao = criar_inovacao(titulo="Caixa Rapido", status="DISPONIVEL_PARA_REPLICACAO")
    client.force_login(autor)
    resposta = client.get(pagina.format(id=inovacao.pk))
    assert resposta.status_code == 200
    valores = {"titulo": "Caixa Rapido", "detalhe": f"/inovacoes/{inovacao.pk}/"}
    esperado = [
        (texto.format(**valores), href and href.format(**valores), corrente)
        for texto, href, corrente in itens
    ]
    assert _trilha(resposta.content.decode()) == esperado


@pytest.mark.parametrize("nome", ["login", "acesso_negado", "nao_encontrada", "erro_500"])
def test_login_e_paginas_de_erro_nao_tem_trilha(paginas, nome):  # noqa: F811
    """RED-30: login, 403, 404 e 500 ficam sem trilha."""
    assert 'aria-label="Você está em"' not in paginas[nome]


def test_separador_da_trilha_nao_esta_no_html(paginas):  # noqa: F811
    """RED-30: o "›" vem da folha (escapado), nunca do HTML."""
    for nome, html in paginas.items():
        assert "›" not in html, nome
        assert "&rsaquo;" not in html and "&#8250;" not in html, nome


def test_titulo_com_aspas_e_e_comercial_sai_escapado_na_trilha(client, autor, criar_inovacao):
    """RED-30: o titulo da inovacao entra na trilha escapado."""
    inovacao = criar_inovacao(titulo='Caixa "rápido" & cia')
    client.force_login(autor)
    html = client.get(f"/inovacoes/{inovacao.pk}/editar/").content.decode()
    assert (
        f'<a href="/inovacoes/{inovacao.pk}/">Caixa &quot;rápido&quot; &amp; cia</a>'
        in html[html.index(ABRE_TRILHA) : html.index('<main id="conteudo">')]
    )
    assert _trilha(html)[1] == ('Caixa "rápido" & cia', f"/inovacoes/{inovacao.pk}/", None)


# --- T17: rodape com links de apoio (RED-32) ----------------------------------------

PAGINAS_DA_FIXTURE = [
    "login",
    "acessibilidade_anonimo",
    "ajuda_anonimo",
    "acessibilidade",
    "ajuda",
    "lista",
    "nova",
    "detalhe",
    "editar",
    "excluir",
    "status",
    "reaproveitar",
    "painel",
    "nao_encontrada",
    "acesso_negado",
    "erro_500",
]


def test_lista_de_paginas_do_rodape_cobre_a_fixture(paginas):  # noqa: F811
    """RED-32: o teste do rodape passa por toda pagina da fixture, inclusive a 500."""
    assert sorted(paginas) == sorted(PAGINAS_DA_FIXTURE)


@pytest.mark.parametrize("nome", PAGINAS_DA_FIXTURE)
def test_rodape_tem_a_identificacao_e_os_links_de_apoio(paginas, nome):  # noqa: F811
    """RED-32: texto atual e os links Acessibilidade e Ajuda, exibidos no footer."""
    tela = exibido(paginas[nome], rigoroso=True)
    rodapes = re.findall(r"<footer>(.*?)</footer>", tela, re.S)
    assert len(rodapes) == 1
    assert "<p>KIRA · Repositório de Inovações · uso interno</p>" in rodapes[0]
    links = [
        (atributos.get("href"), texto.strip())
        for tag, atributos, texto in _elementos(rodapes[0])
        if tag == "a"
    ]
    assert links == [("/acessibilidade/", "Acessibilidade"), ("/ajuda/", "Ajuda")]
