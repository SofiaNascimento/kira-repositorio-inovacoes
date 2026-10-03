"""Testes do ciclo de vida da sessao.

AUTH-15 (8 horas sem requisicoes) e o endurecimento dos cookies (RNF02).
Os de expiracao manipulam a linha da sessao no banco, sem navegar telas.
"""

import importlib.util
from datetime import timedelta
from pathlib import Path

import pytest
from django.conf import settings
from django.contrib.sessions.models import Session
from django.utils import timezone
from pytest_django.asserts import assertRedirects

from contas.models import Usuario

OITO_HORAS = timedelta(hours=8)
FOLGA = timedelta(seconds=30)


@pytest.fixture
def cliente_autenticado(client, db):
    ana = Usuario.objects.create_user(username="ana", email="ana@x.com", password="x-123-abc")
    client.force_login(ana)
    return client


def _sessao(client):
    return Session.objects.get(session_key=client.cookies[settings.SESSION_COOKIE_NAME].value)


def test_sessao_expirada_vira_anonima_e_volta_ao_login(cliente_autenticado):
    """AUTH-15: passado o prazo, o visitante volta ao estado anonimo."""
    Session.objects.filter(pk=_sessao(cliente_autenticado).pk).update(
        expire_date=timezone.now() - timedelta(seconds=1)
    )
    resposta = cliente_autenticado.get("/")
    assertRedirects(resposta, "/entrar/?next=/", fetch_redirect_response=False)


def test_requisicao_dentro_da_janela_renova_por_mais_oito_horas(cliente_autenticado):
    """AUTH-15: o prazo conta da ultima requisicao, nao do login."""
    # Como se 7 horas tivessem passado desde a ultima requisicao.
    Session.objects.filter(pk=_sessao(cliente_autenticado).pk).update(
        expire_date=timezone.now() + timedelta(hours=1)
    )
    assert cliente_autenticado.get("/inovacoes/").status_code == 200

    expira = _sessao(cliente_autenticado).expire_date
    assert timezone.now() + OITO_HORAS - FOLGA <= expira <= timezone.now() + OITO_HORAS


def _carregar_settings(monkeypatch, debug):
    monkeypatch.setenv("DJANGO_DEBUG", debug)
    arquivo = Path(settings.BASE_DIR) / "config" / "settings.py"
    spec = importlib.util.spec_from_file_location("settings_isolado", arquivo)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


@pytest.mark.unit
def test_cookies_endurecidos_fora_de_debug(monkeypatch):
    """RNF02: fora de DEBUG, cookies de sessao e CSRF so trafegam por HTTPS,
    e o de sessao fica fora do alcance de JavaScript. Em DEBUG, o HTTP local
    continua funcionando."""
    producao = _carregar_settings(monkeypatch, "False")
    assert producao.SESSION_COOKIE_HTTPONLY is True
    assert producao.SESSION_COOKIE_SECURE is True
    assert producao.CSRF_COOKIE_SECURE is True

    desenvolvimento = _carregar_settings(monkeypatch, "True")
    assert desenvolvimento.SESSION_COOKIE_SECURE is False
    assert desenvolvimento.CSRF_COOKIE_SECURE is False
