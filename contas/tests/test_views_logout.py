"""Testes e2e do encerramento de sessao em /sair/.

AUTH-13 e AUTH-14.
"""

import pytest
from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from django.template.loader import render_to_string
from django.test import Client
from pytest_django.asserts import assertRedirects

from contas.models import Usuario


@pytest.fixture
def ana(db):
    return Usuario.objects.create_user(
        username="ana", email="ana@x.com", password="senha-forte-123"
    )


def test_post_em_sair_encerra_a_sessao_e_volta_ao_login_com_mensagem(client, ana):
    """AUTH-13: sessao encerrada no servidor, login e mensagem de confirmacao."""
    client.force_login(ana)
    resposta = client.post("/sair/", follow=True)
    assertRedirects(resposta, "/entrar/")
    assert "_auth_user_id" not in client.session
    assert "Sessão encerrada." in resposta.content.decode()


def test_get_em_sair_nao_encerra_a_sessao(client, ana):
    """AUTH-13: so a acao explicita de logout (POST) encerra a sessao."""
    client.force_login(ana)
    client.get("/sair/")
    assert int(client.session["_auth_user_id"]) == ana.pk


def test_cookie_de_sessao_encerrada_vira_requisicao_anonima(client, ana):
    """AUTH-14: reenviar o cookie antigo nao devolve o acesso."""
    client.force_login(ana)
    chave_antiga = client.cookies[settings.SESSION_COOKIE_NAME].value
    client.post("/sair/")

    outro = Client()
    outro.cookies[settings.SESSION_COOKIE_NAME] = chave_antiga
    # Autenticado seria redirecionado para fora do login (AUTH-12).
    assert outro.get("/entrar/").status_code == 200
    assert SessionStore().exists(chave_antiga) is False


def test_template_base_oferece_logout_por_formulario_post(rf, ana):
    """AUTH-13: a acao de sair e um formulario POST, nao um link."""
    request = rf.get("/")
    request.user = ana
    html = render_to_string("base.html", request=request)
    assert '<form method="post" action="/sair/">' in html
    assert 'name="csrfmiddlewaretoken"' in html


def test_logout_expira_o_cookie_de_sessao(client, ana):
    """AUTH-13: a resposta do logout limpa o cookie de sessao do navegador."""
    client.force_login(ana)
    resposta = client.post("/sair/")
    cookie = resposta.cookies[settings.SESSION_COOKIE_NAME]
    assert cookie.value == ""
    assert cookie["max-age"] == 0
