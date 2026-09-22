"""Testes das invariantes que o banco impoe sobre Usuario.

AUTH-18 e AUTH-25: regras que precisam valer mesmo quando o codigo escreve
direto no banco, sem passar por formulario ou full_clean().
"""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from contas.models import Usuario


@pytest.mark.django_db
def test_perfil_invalido_e_rejeitado_no_create():
    """AUTH-18: valor fora do enum nao entra, mesmo sem full_clean()."""
    with pytest.raises(IntegrityError):
        Usuario.objects.create(username="chefe", email="chefe@x.com", perfil="CHEFE")


@pytest.mark.django_db
def test_perfil_invalido_e_rejeitado_no_update_em_massa():
    """AUTH-18: update() em massa nao passa por validacao de modelo nenhuma."""
    Usuario.objects.create(username="ana", email="ana@x.com")
    with pytest.raises(IntegrityError):
        Usuario.objects.filter(username="ana").update(perfil="CHEFE")


@pytest.mark.django_db
@pytest.mark.parametrize("perfil", ["USUARIO", "ADMINISTRADOR"])
def test_perfis_validos_sao_gravados(perfil):
    """AUTH-16: os dois valores do enum gravam sem erro."""
    with transaction.atomic():
        u = Usuario.objects.create(
            username=f"user-{perfil}", email=f"{perfil}@x.com", perfil=perfil
        )
    u.refresh_from_db()
    assert u.perfil == perfil


@pytest.mark.django_db
def test_email_duplicado_por_diferenca_de_caixa_e_rejeitado():
    """AUTH-25: sem isso, o login por e-mail (AUTH-02) ficaria ambiguo."""
    Usuario.objects.create(username="ana", email="ana@x.com")
    with pytest.raises(IntegrityError):
        Usuario.objects.create(username="ana2", email="Ana@X.com")


@pytest.mark.django_db
def test_emails_distintos_convivem():
    """AUTH-25: a constraint nao pode barrar enderecos realmente diferentes."""
    Usuario.objects.create(username="ana", email="ana@x.com")
    Usuario.objects.create(username="bruno", email="bruno@x.com")
    assert Usuario.objects.count() == 2


@pytest.mark.django_db
def test_mensagem_de_violacao_de_email_e_em_portugues():
    """AUTH-25: a mensagem chega ao formulario do admin (RF13)."""
    Usuario.objects.create(username="ana", email="ana@x.com")
    duplicado = Usuario(username="ana2", email="ANA@x.com")
    with pytest.raises(ValidationError) as erro:
        duplicado.full_clean()
    assert "Já existe uma conta com este e-mail." in str(erro.value)
