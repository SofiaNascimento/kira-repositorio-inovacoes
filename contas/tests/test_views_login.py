"""Testes e2e da tela de login em /entrar/.

AUTH-01 a AUTH-05, AUTH-12 e AUTH-24, pelo cliente HTTP do Django.
"""

import pytest
from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from django.test import Client
from pytest_django.asserts import assertRedirects

from contas.models import Usuario

SENHA = "senha-forte-123"
MENSAGEM = "Usuário ou senha inválidos."


@pytest.fixture
def ana(db):
    return Usuario.objects.create_user(username="ana", email="ana@x.com", password=SENHA)


def test_login_por_username_abre_sessao_e_vai_para_a_home(client, ana):
    """AUTH-01: sessao aberta para a conta e redirecionamento a home interna."""
    resposta = client.post("/entrar/", {"username": "ana", "password": SENHA})
    assertRedirects(resposta, "/", fetch_redirect_response=False)
    assert int(client.session["_auth_user_id"]) == ana.pk


def test_login_por_email_abre_sessao_da_mesma_conta(client, ana):
    """AUTH-02: o e-mail, em qualquer caixa, autentica a mesma conta."""
    resposta = client.post("/entrar/", {"username": "ANA@X.com", "password": SENHA})
    assertRedirects(resposta, "/", fetch_redirect_response=False)
    assert int(client.session["_auth_user_id"]) == ana.pk


def test_credencial_invalida_rerenderiza_com_mensagem_unica(client, ana):
    """AUTH-03: 200, visitante segue anonimo, uma unica mensagem generica."""
    resposta = client.post("/entrar/", {"username": "ana", "password": "errada-456"})
    assert resposta.status_code == 200
    assert "_auth_user_id" not in client.session
    assert resposta.content.decode().count(MENSAGEM) == 1


def test_login_recusado_nao_devolve_a_senha_submetida(client, ana):
    """AUTH-08: a senha digitada nao volta no HTML re-renderizado."""
    senha_errada = "senha-errada-que-nao-volta-321"
    resposta = client.post("/entrar/", {"username": "ana", "password": senha_errada})
    assert resposta.status_code == 200
    assert senha_errada not in resposta.content.decode()


def test_post_sem_token_csrf_e_recusado_com_403(ana):
    """AUTH-24: 403 e nenhuma sessao autenticada."""
    cliente = Client(enforce_csrf_checks=True)
    resposta = cliente.post("/entrar/", {"username": "ana", "password": SENHA})
    assert resposta.status_code == 403
    assert "_auth_user_id" not in cliente.session


def test_login_troca_a_chave_de_sessao(client, ana):
    """AUTH-05: a chave anterior ao login deixa de valer."""
    sessao_anonima = client.session
    sessao_anonima["visitou"] = True
    sessao_anonima.save()
    chave_antes = client.cookies[settings.SESSION_COOKIE_NAME].value

    client.post("/entrar/", {"username": "ana", "password": SENHA})

    chave_depois = client.cookies[settings.SESSION_COOKIE_NAME].value
    assert chave_depois != chave_antes
    assert SessionStore().exists(chave_antes) is False


def test_usuario_autenticado_pedindo_login_e_redirecionado(client, ana):
    """AUTH-12: nao renderiza o formulario de novo."""
    client.force_login(ana)
    resposta = client.get("/entrar/")
    assertRedirects(resposta, "/", fetch_redirect_response=False)
