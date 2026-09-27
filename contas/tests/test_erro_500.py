"""Testes e2e da pagina 500 com o banco fora do ar durante o login.

AUTH-26. O pytest-django roda com DEBUG=False, como em producao.
"""

import pytest
from django.conf import settings
from django.db import OperationalError
from pytest_django.asserts import assertTemplateUsed

from contas.backends import UsernameOrEmailBackend

DETALHE_DA_CONEXAO = (
    'connection to server at "db.interno.kira" (10.0.0.7), port 5433 failed: '
    'FATAL: password authentication failed for user "kira_app" password=s3gr3d0-do-banco'
)


@pytest.fixture
def banco_fora_do_ar(monkeypatch, client):
    def falhar(*args, **kwargs):
        raise OperationalError(DETALHE_DA_CONEXAO)

    monkeypatch.setattr(UsernameOrEmailBackend, "authenticate", falhar)
    client.raise_request_exception = False
    return client


def _entrar(client):
    return client.post("/entrar/", {"username": "ana", "password": "senha-forte-123"})


@pytest.mark.django_db
def test_banco_indisponivel_no_login_devolve_500_sem_abrir_sessao(banco_fora_do_ar):
    """AUTH-26: pagina de erro e nenhuma sessao autenticada."""
    assert settings.DEBUG is False
    resposta = _entrar(banco_fora_do_ar)
    assert resposta.status_code == 500
    assertTemplateUsed(resposta, "500.html")
    assert "_auth_user_id" not in banco_fora_do_ar.session


@pytest.mark.django_db
def test_pagina_500_nao_expoe_detalhes_da_conexao(banco_fora_do_ar):
    """AUTH-26: nem host, nem usuario, nem senha, nem traceback."""
    html = _entrar(banco_fora_do_ar).content.decode()
    banco = settings.DATABASES["default"]
    proibidos = [
        "db.interno.kira",
        "kira_app",
        "s3gr3d0-do-banco",
        "OperationalError",
        "Traceback",
        *(banco[chave] for chave in ("HOST", "USER", "PASSWORD") if banco[chave]),
    ]
    for trecho in proibidos:
        assert trecho not in html, trecho
