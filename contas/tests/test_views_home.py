"""Testes e2e da raiz / (nucleo:home), que leva a listagem de inovacoes.

Destino padrao do login (AUTH-01) e primeira tela protegida (AUTH-11); a F3
(CONS-09, CONS-11) faz da raiz um redirect para /inovacoes/.
"""

import pytest
from pytest_django.asserts import assertRedirects

from contas.models import Usuario


@pytest.fixture
def ana(db):
    return Usuario.objects.create_user(
        username="ana", email="ana@x.com", password="senha-forte-123"
    )


def test_usuario_autenticado_abre_a_home(client, ana):
    """AUTH-01, alterado pela CONS-09: o destino padrao do login, seguido o
    redirect, responde 200 a quem esta autenticado."""
    client.force_login(ana)
    resposta = client.get("/", follow=True)
    assert resposta.redirect_chain == [("/inovacoes/", 302)]
    assert resposta.status_code == 200


def test_raiz_autenticada_redireciona_a_listagem(client, ana):
    """CONS-09: GET / autenticado responde 302 para /inovacoes/."""
    client.force_login(ana)
    assertRedirects(client.get("/"), "/inovacoes/", fetch_redirect_response=False)


def test_login_sem_next_termina_na_listagem(client, ana):
    """CONS-11: login sem next, seguidos os redirects, termina em /inovacoes/."""
    resposta = client.post(
        "/entrar/", {"username": "ana", "password": "senha-forte-123"}, follow=True
    )
    assert resposta.redirect_chain[-1] == ("/inovacoes/", 302)
    assert resposta.status_code == 200


def test_home_identifica_a_conta_e_oferece_sair(client, ana):
    """AUTH-01 e AUTH-13, alterados pela CONS-09: a pagina a que a raiz leva
    mostra quem esta autenticado e o formulario de logout."""
    client.force_login(ana)
    html = client.get("/", follow=True).content.decode()
    assert "ana" in html
    assert '<form method="post" action="/sair/">' in html
