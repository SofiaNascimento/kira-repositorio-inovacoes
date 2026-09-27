"""Testes do UsernameOrEmailBackend chamado diretamente.

AUTH-01, AUTH-02 e AUTH-23: o mesmo campo aceita username ou e-mail, e toda
recusa devolve None, sem distinguir o motivo.
"""

import pytest

from contas.backends import UsernameOrEmailBackend
from contas.models import Usuario

SENHA = "senha-forte-123"


@pytest.fixture
def ana(db):
    return Usuario.objects.create_user(username="ana", email="ana@x.com", password=SENHA)


def autenticar(identificador, senha=SENHA):
    return UsernameOrEmailBackend().authenticate(None, username=identificador, password=senha)


def test_autentica_pelo_username(ana):
    """AUTH-01: username existente com a senha correta."""
    assert autenticar("ana").pk == ana.pk


def test_autentica_pelo_email(ana):
    """AUTH-02: o e-mail da conta autentica a mesma conta."""
    assert autenticar("ana@x.com").pk == ana.pk


def test_email_e_comparado_sem_diferenciar_caixa(ana):
    """AUTH-02: a comparacao do e-mail e case-insensitive."""
    assert autenticar("AnA@X.CoM").pk == ana.pk


@pytest.mark.django_db
def test_identificador_inexistente_e_recusado():
    """AUTH-03: nenhuma conta corresponde ao identificador."""
    Usuario.objects.create_user(username="bruno", email="bruno@x.com", password=SENHA)
    assert autenticar("fantasma@x.com") is None


def test_senha_errada_e_recusada(ana):
    """AUTH-03: identificador certo, senha errada."""
    assert autenticar("ana@x.com", senha="outra-senha-456") is None


def test_conta_inativa_e_recusada(ana):
    """AUTH-23: credencial correta de conta inativa nao autentica."""
    ana.is_active = False
    ana.save()
    assert autenticar("ana", senha=SENHA) is None


def test_identificador_ambiguo_e_recusado(ana):
    """O backend nao confia na constraint: se o identificador casa com mais
    de uma conta, recusa em vez de escolher uma."""
    Usuario.objects.create_user(username="ANA", email="outra@x.com", password=SENHA)
    assert autenticar("ana") is None
