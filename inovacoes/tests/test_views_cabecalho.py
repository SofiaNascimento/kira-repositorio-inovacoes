"""Testes e2e do ponto de entrada do cadastro no cabecalho (INOV-38)."""

import re

import pytest

LINK = re.compile(r'<a href="/inovacoes/nova/">\s*Cadastrar inovação\s*</a>')


def _cabecalho(html):
    return html[html.index("<header>") : html.index("</header>")]


def _navegacao_principal(html):
    cabecalho = _cabecalho(html)
    inicio = cabecalho.index('<nav aria-label="Principal">')
    return cabecalho[inicio : cabecalho.index("</nav>", inicio)]


@pytest.mark.parametrize("pagina", ["/inovacoes/", "/inovacoes/nova/"])
def test_cabecalho_autenticado_leva_ao_cadastro(client, autor, pagina):
    client.force_login(autor)
    html = client.get(pagina).content.decode()
    assert LINK.search(_navegacao_principal(html))


@pytest.mark.django_db
def test_cabecalho_anonimo_nao_mostra_o_link(client):
    html = client.get("/entrar/").content.decode()
    assert not LINK.search(html)
    assert "Cadastrar inovação" not in _cabecalho(html)


LINK_INOVACOES = re.compile(r'<a href="/inovacoes/">\s*Inovações\s*</a>')


@pytest.mark.parametrize("pagina", ["/inovacoes/", "/inovacoes/nova/", "/inovacoes/{id}/"])
def test_cabecalho_autenticado_leva_a_listagem_antes_do_cadastro(
    client, autor, criar_inovacao, pagina
):
    """CONS-10: link "Inovações" -> /inovacoes/ em toda pagina, antes de "Cadastrar inovação"."""
    client.force_login(autor)
    html = client.get(pagina.format(id=criar_inovacao().pk)).content.decode()
    navegacao = _navegacao_principal(html)
    link = LINK_INOVACOES.search(navegacao)
    assert link
    assert link.start() < LINK.search(navegacao).start()


@pytest.mark.django_db
def test_cabecalho_anonimo_nao_mostra_o_link_de_inovacoes(client):
    """CONS-10: o link so existe com usuario autenticado."""
    html = client.get("/entrar/").content.decode()
    assert not LINK_INOVACOES.search(html)
    assert 'href="/inovacoes/"' not in _cabecalho(html)


LINK_INDICADORES = re.compile(r'<a href="/indicadores/">\s*Indicadores\s*</a>')


@pytest.mark.parametrize(
    "pagina",
    ["/inovacoes/", "/inovacoes/{id}/", "/inovacoes/{id}/reaproveitar/", "/indicadores/"],
)
def test_cabecalho_autenticado_leva_ao_painel_depois_do_cadastro(
    client, autor, criar_inovacao, pagina
):
    """REAP-28: link "Indicadores" -> /indicadores/ no nav "Principal", depois do cadastro."""
    client.force_login(autor)
    inovacao = criar_inovacao(status="DISPONIVEL_PARA_REPLICACAO")
    resposta = client.get(pagina.format(id=inovacao.pk))
    assert resposta.status_code == 200
    navegacao = _navegacao_principal(resposta.content.decode())
    link = LINK_INDICADORES.search(navegacao)
    assert link
    assert link.start() > LINK.search(navegacao).start()


@pytest.mark.django_db
def test_cabecalho_anonimo_nao_mostra_o_link_do_painel(client):
    """REAP-28: o link so existe com usuario autenticado."""
    html = client.get("/entrar/").content.decode()
    assert not LINK_INDICADORES.search(html)
    assert 'href="/indicadores/"' not in _cabecalho(html)
