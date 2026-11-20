"""Testes e2e dos cartoes da lista e da tabela alternativa (R2, RCON-10 a RCON-20)."""

import datetime
import html as html_lib
import re
from html.parser import HTMLParser

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from inovacoes.models import Categoria, Inovacao, Reaproveitamento, StatusInovacao, Unidade
from inovacoes.tests.test_views_lista import _linhas
from inovacoes.tests.visibilidade import CLASSES_OCULTAS, VAZIOS, exibido

LISTA = "/inovacoes/"


@pytest.fixture
def logado(client, autor):
    client.force_login(autor)
    return client


def _forcar_data(inovacao, dia):
    data = datetime.datetime(2026, 9, dia, 12, 0, tzinfo=datetime.UTC)
    Inovacao.objects.filter(pk=inovacao.pk).update(data_criacao=data)


def _reaproveitar(inovacao, vezes):
    """Grava direto, so para preparar a contagem; o caminho da aplicacao e o metodo (AD-012)."""
    for numero in range(vezes):
        unidade = Unidade.objects.create(nome=f"Teste Reuso {inovacao.pk}-{numero}")
        Reaproveitamento.objects.create(
            inovacao=inovacao, unidade=unidade, registrado_por=inovacao.autor
        )


def _exibida(resposta):
    assert resposta.status_code == 200
    return exibido(resposta.content.decode(), rigoroso=True)


def _artigos(html):
    """O HTML de cada `article` dentro do `ul aria-label="Resultados"`, em ordem."""
    lista = re.search(r'<ul[^>]*aria-label="Resultados"[^>]*>', html)
    assert lista, 'sem o ul aria-label="Resultados"'
    return re.findall(r"<article\b[^>]*>(.*?)</article>", html[lista.end() :], re.S)


def _textos(fragmento):
    """Os textos do fragmento, na ordem do codigo, sem as tags."""
    return [" ".join(t.split()) for t in re.split(r"<[^>]+>", fragmento) if t.strip()]


def _resumo(artigo):
    return " ".join(re.search(r"</h2>\s*<p[^>]*>(.*?)</p>", artigo, re.S).group(1).split())


# --- RCON-10 a RCON-12: estrutura e ordem do cartao ---


def test_cartao_mostra_selo_data_titulo_resumo_e_metadados_nessa_ordem(logado, criar_inovacao):
    """RCON-10, RCON-11, RCON-15: li > article; selo, data, h2, resumo e metadados, nessa ordem."""
    inovacao = criar_inovacao(
        titulo="Controle de Caixa",
        problema="Fechamento de caixa manual e demorado.",
        status=StatusInovacao.VALIDADA,
    )
    _forcar_data(inovacao, 9)
    html = _exibida(logado.get(LISTA))

    assert re.search(r'<ul[^>]*aria-label="Resultados"[^>]*>\s*<li>\s*<article\b[^>]*>', html), (
        "cada resultado e um li > article dentro da lista"
    )
    (artigo,) = _artigos(html)
    assert _textos(artigo) == [
        "Validada",
        "Cadastrada em",
        "09/09/2026",
        "Controle de Caixa",
        "Fechamento de caixa manual e demorado.",
        "Teste Unidade",
        "Teste Categoria",
        "Nenhum reaproveitamento",
    ]
    # O selo e o span do status, com o rotulo em texto (RCON-15).
    assert re.search(r'<span class="selo selo--validada">\s*Validada\s*</span>', artigo)
    # "Cadastrada em" e a data formam uma frase so.
    assert re.search(r">\s*Cadastrada em\s*<time>09/09/2026</time>", artigo)
    # Os metadados sao uma lista, um item por informacao.
    meta = re.search(r"<ul\b[^>]*>(.*?)</ul>", artigo, re.S).group(1)
    itens = re.findall(r"<li>(.*?)</li>", meta, re.S)
    assert [" ".join(_textos(i)) for i in itens] == [
        "Teste Unidade",
        "Teste Categoria",
        "Nenhum reaproveitamento",
    ]


def test_titulo_e_h2_com_so_o_link_para_o_detalhe(logado, criar_inovacao):
    """RCON-11, RCON-12: o h2 so contem o link; ele e o unico link do article."""
    inovacao = criar_inovacao(titulo="Controle de Caixa")
    bruto = logado.get(LISTA).content.decode()
    url = re.escape(inovacao.get_absolute_url())

    (artigo,) = _artigos(exibido(bruto, rigoroso=True))
    assert re.search(rf'<h2[^>]*>\s*<a href="{url}">Controle de Caixa</a>\s*</h2>', artigo)
    # Unico link no HTML enviado, exibido ou nao.
    (artigo_bruto,) = _artigos(bruto)
    assert len(re.findall(r"<a\b", artigo_bruto)) == 1


def test_icones_do_cartao_sao_decorativos(logado, criar_inovacao):
    """RCON-11, RCON-15: todo SVG do cartao e aria-hidden; o texto fica sem ele."""
    criar_inovacao()
    (artigo,) = _artigos(logado.get(LISTA).content.decode())
    svgs = re.findall(r"<svg\b[^>]*>", artigo)
    # O icone do selo e um por metadado (unidade, categoria, reaproveitamentos).
    assert len(svgs) == 4
    assert all('aria-hidden="true"' in svg for svg in svgs)


@pytest.mark.parametrize(
    ("problema", "esperado"),
    [
        ("a" * 160, "a" * 160),
        ("b" * 161, "b" * 159 + "…"),
    ],
)
def test_resumo_e_o_problema_cortado_em_160_caracteres(logado, criar_inovacao, problema, esperado):
    """RCON-13: ate 160 caracteres o texto inteiro; acima, 159 e "…"."""
    criar_inovacao(problema=problema)
    (artigo,) = _artigos(_exibida(logado.get(LISTA)))
    assert _resumo(artigo) == esperado


def test_resumo_escapa_html(logado, criar_inovacao):
    """Edge case (CONS-17): o problema com HTML sai escapado no cartao."""
    criar_inovacao(problema="<b>negrito</b>")
    (artigo,) = _artigos(logado.get(LISTA).content.decode())
    assert "&lt;b&gt;negrito&lt;/b&gt;" in artigo
    assert "<b>" not in artigo


def test_contagem_de_reaproveitamentos_no_singular_e_no_plural(logado, criar_inovacao):
    """RCON-14: 0, 1 e 3 reaproveitamentos, cada um no seu cartao."""
    nenhum = criar_inovacao(titulo="Nenhum")
    um = criar_inovacao(titulo="Um")
    tres = criar_inovacao(titulo="Tres")
    _forcar_data(nenhum, 3)
    _forcar_data(um, 2)
    _forcar_data(tres, 1)
    _reaproveitar(um, 1)
    _reaproveitar(tres, 3)

    artigos = _artigos(_exibida(logado.get(LISTA)))
    assert [_textos(a)[3] for a in artigos] == ["Nenhum", "Um", "Tres"]
    assert [_textos(a)[-1] for a in artigos] == [
        "Nenhum reaproveitamento",
        "1 reaproveitamento",
        "3 reaproveitamentos",
    ]


def test_sem_exibicao_nao_ha_tabela(logado, criar_inovacao):
    """RCON-10: os cartoes sao o padrao e a tabela nao e renderizada."""
    criar_inovacao()
    bruto = logado.get(LISTA).content.decode()
    assert "<table" not in bruto
    assert len(_artigos(exibido(bruto, rigoroso=True))) == 1


def test_folha_nao_esconde_a_lista_nem_o_cartao():
    """RCON-10 (L-044): nenhuma classe da lista e do cartao some por regra da folha."""
    for classe in ("cartoes", "cartao-inovacao", "cartao-inovacao__titulo"):
        assert classe not in CLASSES_OCULTAS
    for classe in ("cartao-inovacao__resumo", "cartao-inovacao__meta", "selo"):
        assert classe not in CLASSES_OCULTAS


# --- RCON-19: tabela como alternativa ---


def _linhas_da_tabela(html):
    corpo = re.search(r"<tbody>(.*?)</tbody>", html, re.S).group(1)
    return [_textos(linha) for linha in re.findall(r"<tr[^>]*>(.*?)</tr>", corpo, re.S)]


def test_exibicao_tabela_mostra_a_tabela_com_os_mesmos_itens_e_ordem_e_sem_cartoes(
    logado, criar_inovacao
):
    """RCON-19: legenda, colunas, mesmos itens e ordem dos cartoes; nenhum cartao."""
    outra_unidade = Unidade.objects.create(nome="Teste Outra Unidade")
    outra_categoria = Categoria.objects.create(nome="Teste Outra Categoria")
    antiga = criar_inovacao(titulo="Antiga")
    recente = criar_inovacao(
        titulo="Recente",
        unidade=outra_unidade,
        categoria=outra_categoria,
        status=StatusInovacao.DISPONIVEL_PARA_REPLICACAO,
    )
    _forcar_data(antiga, 1)
    _forcar_data(recente, 2)

    cartoes = _linhas(logado.get(LISTA).content.decode())
    bruto = logado.get(f"{LISTA}?exibicao=tabela").content.decode()
    html = exibido(bruto, rigoroso=True)

    assert 'aria-label="Resultados"' not in bruto
    assert "<article" not in bruto
    assert "<caption>Inovações cadastradas</caption>" in html
    cabecalhos = [c.strip() for c in re.findall(r'<th scope="col">(.*?)</th>', html, re.S)]
    assert cabecalhos == ["Título", "Categoria", "Unidade", "Status"]
    assert (
        _linhas_da_tabela(html)
        == cartoes
        == [
            [
                "Recente",
                "Teste Outra Categoria",
                "Teste Outra Unidade",
                "Disponível para replicação",
            ],
            ["Antiga", "Teste Categoria", "Teste Unidade", "Em teste"],
        ]
    )


# --- RCON-16: numero de consultas ---


def test_cartoes_custam_o_mesmo_numero_de_consultas_com_1_e_com_20(
    logado, criar_inovacao, unidade, categoria
):
    """RCON-16: 20 cartoes de unidades, categorias e contagens diferentes custam o mesmo que 1."""
    criar_inovacao(titulo="Unica")
    logado.get(LISTA)  # aquece sessao e caches, para medir so a pagina
    with CaptureQueriesContext(connection) as com_um:
        resposta = logado.get(LISTA)
    assert len(_artigos(_exibida(resposta))) == 1

    outras_unidades = list(Unidade.objects.exclude(pk=unidade.pk)[:4])
    outras_categorias = list(Categoria.objects.exclude(pk=categoria.pk)[:4])
    for n in range(19):
        outra = criar_inovacao(
            titulo=f"Outra {n:02d}",
            unidade=outras_unidades[n % 4],
            categoria=outras_categorias[n % 4],
        )
        _reaproveitar(outra, n + 1)
    with CaptureQueriesContext(connection) as com_vinte:
        resposta = logado.get(LISTA)
    artigos = _artigos(_exibida(resposta))
    assert len(artigos) == 20
    contagens = sorted(_textos(a)[-1] for a in artigos)
    assert len(set(contagens)) == 20
    assert len(com_vinte) == len(com_um)


# --- RCON-09: contador ---


def _contador(html):
    """O texto do p role="status" da barra de resultados."""
    barra = re.search(r'<div class="resultados">(.*?)</p>', html, re.S)
    assert barra, "sem a barra de resultados"
    achado = re.search(r'<p class="total" role="status">(.*)', barra.group(1), re.S)
    assert achado, 'o contador e um p role="status" na barra'
    return " ".join(achado.group(1).split())


def test_contador_no_singular(logado, criar_inovacao):
    """RCON-09: "{n} inovação encontrada" num role="status"."""
    criar_inovacao()
    assert _contador(_exibida(logado.get(LISTA))) == "1 inovação encontrada"


def test_contador_no_plural_conta_todas_as_paginas(logado, criar_inovacao):
    """RCON-09 (CONS-33): o total vale para todas as paginas, tambem na segunda."""
    for numero in range(25):
        criar_inovacao(titulo=f"I{numero:02d}")
    assert _contador(_exibida(logado.get(f"{LISTA}?page=2"))) == "25 inovações encontradas"


def test_primeiro_role_status_continua_o_do_base(logado, criar_inovacao):
    """RCON-09 e EDEX: o contador vem depois do h1; o primeiro role="status" e o do base."""
    criar_inovacao()
    html = logado.get(LISTA).content.decode()
    assert html.count('role="status"') == 2
    assert html.index('role="status"') < html.index("<h1") < html.index('class="total"')


# --- RCON-17, RCON-18, RCON-20: alternador ---


class _Alternador(HTMLParser):
    """O grupo do alternador: o rotulo (pelo aria-labelledby) e cada link com seus atributos."""

    def __init__(self):
        super().__init__()
        self.ids = {}
        self.grupo = None
        self.links = []
        self._pilha = []
        self._id = None

    def handle_starttag(self, tag, attrs):
        atributos = dict(attrs)
        if atributos.get("id"):
            self._id = atributos["id"]
            self.ids[self._id] = ""
        if tag == "div" and "alternador" in (atributos.get("class") or "").split():
            self.grupo = atributos
            self._pilha = ["div"]
            return
        if self._pilha:
            if tag not in VAZIOS:
                self._pilha.append(tag)
            if tag == "a":
                self.links.append([atributos, ""])

    def handle_endtag(self, tag):
        if tag == "span":
            self._id = None
        if self._pilha and tag in self._pilha:
            while self._pilha.pop() != tag:
                pass

    def handle_data(self, data):
        if self._id:
            self.ids[self._id] += data
        if self._pilha and "a" in self._pilha:
            self.links[-1][1] += data


def _alternador(html):
    leitor = _Alternador()
    leitor.feed(html)
    leitor.close()
    assert leitor.grupo is not None, "sem o grupo do alternador"
    return leitor


def test_alternador_e_um_grupo_exibicao_com_cartoes_e_tabela(logado, criar_inovacao):
    """RCON-17: grupo rotulado "Exibição", os links "Cartões" e "Tabela", cada um com icone."""
    criar_inovacao()
    bruto = logado.get(LISTA).content.decode()
    alternador = _alternador(exibido(bruto, rigoroso=True))

    assert alternador.grupo["role"] == "group"
    rotulo = alternador.ids[alternador.grupo["aria-labelledby"]]
    assert rotulo.strip() == "Exibição"
    assert [texto.strip() for _, texto in alternador.links] == ["Cartões", "Tabela"]
    # Cada link com um icone decorativo antes do texto (no HTML enviado).
    for texto in ("Cartões", "Tabela"):
        assert re.search(
            rf'<a href="[^"]*"[^>]*>\s*<svg aria-hidden="true"[^>]*>.*?</svg>\s*{texto}</a>',
            bruto,
            re.S,
        )


def _hrefs(alternador):
    return {
        texto.strip(): html_lib.unescape(atributos["href"]) for atributos, texto in alternador.links
    }


def _atuais(alternador):
    return [texto.strip() for atributos, texto in alternador.links if "aria-current" in atributos]


def test_links_do_alternador_mantem_busca_filtros_e_pagina(logado, criar_inovacao):
    """RCON-18: Tabela = query string atual + exibicao=tabela; Cartoes = sem exibicao."""
    financeiro = Categoria.objects.get(nome="Financeiro")
    sede = Unidade.objects.get(nome="Sede")
    for numero in range(21):
        criar_inovacao(
            titulo=f"Planilha {numero:02d}",
            categoria=financeiro,
            unidade=sede,
            status=StatusInovacao.VALIDADA,
        )
    consulta = f"q=planilha&categoria={financeiro.pk}&unidade={sede.pk}&status=VALIDADA&page=2"

    cartoes = _alternador(_exibida(logado.get(f"{LISTA}?{consulta}")))
    assert _hrefs(cartoes) == {
        "Cartões": f"/inovacoes/?{consulta}",
        "Tabela": f"/inovacoes/?{consulta}&exibicao=tabela",
    }
    tabela = _alternador(_exibida(logado.get(f"{LISTA}?{consulta}&exibicao=tabela")))
    assert _hrefs(tabela) == {
        "Cartões": f"/inovacoes/?{consulta}",
        "Tabela": f"/inovacoes/?{consulta}&exibicao=tabela",
    }


@pytest.mark.parametrize(
    ("parametro", "atual"),
    [("", "Cartões"), ("?exibicao=tabela", "Tabela")],
)
def test_so_a_exibicao_atual_tem_aria_current(logado, criar_inovacao, parametro, atual):
    """RCON-17: o atual marcado com aria-current="true"; o outro sem."""
    criar_inovacao()
    alternador = _alternador(_exibida(logado.get(f"{LISTA}{parametro}")))
    assert _atuais(alternador) == [atual]
    marcado = [a for a, texto in alternador.links if texto.strip() == atual][0]
    assert marcado["aria-current"] == "true"


@pytest.mark.parametrize("valor", ["x", "TABELA", "cartoes", ""])
def test_exibicao_desconhecida_mostra_cartoes_como_atual_sem_erro(logado, criar_inovacao, valor):
    """RCON-20: qualquer outro valor mostra os cartoes, marca Cartoes e nao mostra erro."""
    criar_inovacao()
    resposta = logado.get(f"{LISTA}?exibicao={valor}")
    html = _exibida(resposta)
    assert _atuais(_alternador(html)) == ["Cartões"]
    assert len(_artigos(html)) == 1
    assert 'role="alert"' not in html
    assert "<table" not in html


def test_links_do_alternador_tem_href_e_nenhum_role(logado, criar_inovacao):
    """RCON-17 (CONS-41): o alternador e feito de links com href, sem role de controle."""
    criar_inovacao()
    alternador = _alternador(logado.get(LISTA).content.decode())
    for atributos, _ in alternador.links:
        assert atributos.get("href")
        assert "role" not in atributos


def test_sem_resultado_nao_ha_barra_de_resultados(logado):
    """RCON-09, RCON-17: a barra so existe quando a lista tem resultados."""
    html = logado.get(LISTA).content.decode()
    assert 'class="resultados"' not in html
    assert 'class="alternador"' not in html


def test_folha_nao_esconde_a_barra_de_resultados():
    """RCON-09, RCON-17 (L-044): a barra e o alternador nao somem por regra da folha."""
    for classe in ("resultados", "alternador", "total"):
        assert classe not in CLASSES_OCULTAS
