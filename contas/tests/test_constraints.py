"""Testes das invariantes que o banco impoe sobre Usuario.

AUTH-18 e AUTH-25: regras que precisam valer mesmo quando o codigo escreve
direto no banco, sem passar por formulario ou full_clean().
"""

import pytest
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
