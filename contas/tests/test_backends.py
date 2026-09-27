"""Testes do UsernameOrEmailBackend chamado diretamente.

AUTH-01, AUTH-02 e AUTH-23: o mesmo campo aceita username ou e-mail, e toda
recusa devolve None, sem distinguir o motivo.
"""

import pytest
from django.contrib.auth import authenticate

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


# Cadeia configurada em AUTHENTICATION_BACKENDS, via authenticate() do Django.


def test_authenticate_do_django_aceita_username(ana):
    """AUTH-01: o fluxo real de login passa pela cadeia configurada."""
    assert authenticate(None, username="ana", password=SENHA).pk == ana.pk


def test_authenticate_do_django_aceita_email(ana):
    """AUTH-02: sem o backend do projeto na cadeia, o e-mail nao autenticaria."""
    assert authenticate(None, username="ANA@x.com", password=SENHA).pk == ana.pk


def test_authenticate_do_django_recusa_credencial_invalida(ana):
    """AUTH-03: nenhum backend da cadeia aceita a senha errada."""
    assert authenticate(None, username="ana@x.com", password="outra-senha-456") is None


# Anti-enumeracao: sem conta unica, o backend gasta o mesmo hash que gastaria
# conferindo uma senha real. O requisito e o proprio efeito colateral, entao
# o teste observa a chamada.


@pytest.fixture
def hashes(monkeypatch):
    chamadas = []
    original = Usuario.set_password

    def espiao(self, senha):
        chamadas.append(senha)
        return original(self, senha)

    monkeypatch.setattr(Usuario, "set_password", espiao)
    return chamadas


@pytest.mark.django_db
def test_identificador_inexistente_gasta_o_hash_descartavel(hashes):
    """AUTH-03: a resposta nao pode ser mais rapida para conta inexistente."""
    assert autenticar("fantasma@x.com", senha="qualquer-senha-1") is None
    assert hashes == ["qualquer-senha-1"]


def test_identificador_ambiguo_gasta_o_hash_descartavel(ana, hashes):
    """AUTH-03: o mesmo vale quando o identificador casa com mais de uma conta."""
    Usuario.objects.create_user(username="ANA", email="outra@x.com")
    hashes.clear()
    assert autenticar("ana", senha="qualquer-senha-2") is None
    assert hashes == ["qualquer-senha-2"]
