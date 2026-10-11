"""Testes de integracao da regra de autoria (Inovacao.pode_ser_alterada_por).

RN05, RNF07, AD-009: so o autor e o perfil ADMINISTRADOR alteram uma inovacao.
"""

import pytest
from django.contrib.auth.models import AnonymousUser

from contas.models import Usuario
from inovacoes.models import Inovacao


def test_autor_usuario_pode_alterar(autor, criar_inovacao):
    """EDEX-19: autor com perfil USUARIO."""
    assert criar_inovacao().pode_ser_alterada_por(autor) is True


def test_autor_administrador_pode_alterar(administrador, criar_inovacao):
    """EDEX-19: autor com perfil ADMINISTRADOR."""
    inovacao = criar_inovacao(autor=administrador)
    assert inovacao.pode_ser_alterada_por(administrador) is True


def test_terceiro_usuario_nao_pode_alterar(terceiro, criar_inovacao):
    """RNF07: USUARIO que nao e o autor."""
    assert criar_inovacao().pode_ser_alterada_por(terceiro) is False


def test_administrador_pode_alterar_inovacao_de_outro_autor(administrador, criar_inovacao):
    """EDEX-17."""
    assert criar_inovacao().pode_ser_alterada_por(administrador) is True


def test_anonimo_nao_pode_alterar(criar_inovacao):
    """AnonymousUser nao tem is_administrador: a regra nega sem AttributeError."""
    assert criar_inovacao().pode_ser_alterada_por(AnonymousUser()) is False


@pytest.mark.parametrize("bandeira", ["is_staff", "is_superuser"])
def test_staff_ou_superuser_sem_perfil_de_administrador_nao_pode_alterar(criar_inovacao, bandeira):
    """AD-009: o perfil e o unico criterio; is_staff e is_superuser nao contam."""
    conta = Usuario.objects.create_user(username="dora", email="dora@x.com", **{bandeira: True})
    assert conta.perfil == Usuario.Perfil.USUARIO
    assert getattr(conta, bandeira) is True
    assert criar_inovacao().pode_ser_alterada_por(conta) is False


def test_administrador_rebaixado_perde_o_acesso(administrador, criar_inovacao):
    """EDEX-25: vale o perfil atual da conta, relido do banco."""
    inovacao = criar_inovacao()
    assert inovacao.pode_ser_alterada_por(administrador) is True
    Usuario.objects.filter(pk=administrador.pk).update(perfil=Usuario.Perfil.USUARIO)
    administrador.refresh_from_db()
    assert inovacao.pode_ser_alterada_por(administrador) is False


def test_regra_nao_consulta_o_banco(
    autor, terceiro, administrador, criar_inovacao, django_assert_num_queries
):
    """A regra le autor_id e o perfil ja carregados: zero consultas.

    A inovacao vem do banco sem o autor em cache, como nas views.
    """
    inovacao = Inovacao.objects.get(pk=criar_inovacao().pk)
    with django_assert_num_queries(0):
        assert inovacao.pode_ser_alterada_por(autor) is True
        assert inovacao.pode_ser_alterada_por(terceiro) is False
        assert inovacao.pode_ser_alterada_por(administrador) is True
