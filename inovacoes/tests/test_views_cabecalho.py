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


@pytest.mark.parametrize("pagina", ["/", "/inovacoes/nova/"])
def test_cabecalho_autenticado_leva_ao_cadastro(client, autor, pagina):
    client.force_login(autor)
    html = client.get(pagina).content.decode()
    assert LINK.search(_navegacao_principal(html))


@pytest.mark.django_db
def test_cabecalho_anonimo_nao_mostra_o_link(client):
    html = client.get("/entrar/").content.decode()
    assert not LINK.search(html)
    assert "Cadastrar inovação" not in _cabecalho(html)
