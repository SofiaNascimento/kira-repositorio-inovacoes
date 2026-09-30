"""Testes e2e da pagina 500 com o banco fora do ar durante o cadastro.

INOV-42. O pytest-django roda com DEBUG=False, como em producao.
"""

import pytest
from django.conf import settings
from django.db import OperationalError
from pytest_django.asserts import assertTemplateUsed

from inovacoes.models import Inovacao

DETALHE_DA_CONEXAO = (
    'connection to server at "db.interno.kira" (10.0.0.7), port 5433 failed: '
    'FATAL: password authentication failed for user "kira_app" password=s3gr3d0-do-banco'
)


@pytest.fixture
def banco_fora_do_ar(monkeypatch, client, autor):
    def falhar(*args, **kwargs):
        raise OperationalError(DETALHE_DA_CONEXAO)

    monkeypatch.setattr(Inovacao, "save", falhar)
    client.force_login(autor)
    client.raise_request_exception = False
    return client


@pytest.fixture
def dados(unidade, categoria):
    return {
        "titulo": "Conciliação bancária automática",
        "unidade": str(unidade.pk),
        "categoria": str(categoria.pk),
        "problema": "Conciliação manual levava dois dias por mês.",
        "solucao": "Script que cruza o extrato com os lançamentos.",
        "contato": "Ana Souza (ana@x.com)",
    }


def test_banco_indisponivel_no_cadastro_devolve_500_sem_gravar(banco_fora_do_ar, dados):
    """INOV-42: pagina de erro do projeto e nenhuma inovacao."""
    assert settings.DEBUG is False
    resposta = banco_fora_do_ar.post("/inovacoes/nova/", dados)
    assert resposta.status_code == 500
    assertTemplateUsed(resposta, "500.html")
    assert not Inovacao.objects.exists()


def test_pagina_500_do_cadastro_nao_expoe_detalhes_da_conexao(banco_fora_do_ar, dados):
    """INOV-42: nem host, usuario ou senha do banco, nem traceback."""
    html = banco_fora_do_ar.post("/inovacoes/nova/", dados).content.decode()
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
