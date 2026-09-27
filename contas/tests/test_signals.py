"""Testes do log de tentativa de login malsucedida.

AUTH-27 e AUTH-08. O sinal e emitido direto, sem banco.
"""

import logging
from datetime import datetime, timedelta

import pytest
from django.contrib.auth.signals import user_login_failed
from django.utils import timezone

SENHA = "segredo-que-nao-vaza-789"


def emitir_falha(identificador, senha=SENHA):
    # Senha em claro de proposito: o receiver nao pode registra-la nem se o
    # Django deixar de sanitizar as credenciais antes de emitir o sinal.
    user_login_failed.send(
        sender=__name__,
        credentials={"username": identificador, "password": senha},
        request=None,
    )


@pytest.mark.unit
def test_login_recusado_gera_warning_com_identificador_e_horario(caplog):
    """AUTH-27: um warning com o identificador submetido e o timestamp."""
    antes = timezone.now()
    with caplog.at_level(logging.WARNING, logger="contas"):
        emitir_falha("ana@x.com")

    registros = [r for r in caplog.records if r.name.startswith("contas")]
    assert len(registros) == 1
    registro = registros[0]
    assert registro.levelno == logging.WARNING
    mensagem = registro.getMessage()
    assert "ana@x.com" in mensagem

    horario = datetime.fromisoformat(mensagem.rsplit(" em ", 1)[1])
    assert antes - timedelta(seconds=1) <= horario <= timezone.now()


@pytest.mark.unit
def test_senha_submetida_nao_aparece_no_log(caplog):
    """AUTH-08 e AUTH-27: nenhum registro carrega a senha."""
    with caplog.at_level(logging.DEBUG):
        emitir_falha("ana")
    assert caplog.records, "o receiver precisa ter registrado a tentativa"
    assert SENHA not in caplog.text
    assert all(SENHA not in r.getMessage() for r in caplog.records)
