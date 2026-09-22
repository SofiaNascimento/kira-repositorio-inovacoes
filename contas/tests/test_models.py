"""Testes do modelo Usuario.

Derivados das ACs da spec (.specs/features/autenticacao/spec.md), nao da
implementacao. Todos operam sobre instancias nao salvas: nenhum toca o banco.
"""

import pytest

from contas.models import Usuario


@pytest.mark.unit
def test_perfil_tem_exatamente_usuario_e_administrador():
    """AUTH-16: o perfil e restrito a exatamente esses dois valores."""
    assert Usuario.Perfil.values == ["USUARIO", "ADMINISTRADOR"]


@pytest.mark.unit
def test_perfil_padrao_e_usuario():
    """AUTH-17: conta criada sem perfil explicito nasce USUARIO."""
    assert Usuario().perfil == Usuario.Perfil.USUARIO


@pytest.mark.unit
def test_is_administrador_verdadeiro_para_perfil_administrador():
    """AUTH-19: o ponto unico de consulta reporta poderes de administrador."""
    assert Usuario(perfil=Usuario.Perfil.ADMINISTRADOR).is_administrador is True


@pytest.mark.unit
def test_is_administrador_falso_para_perfil_usuario():
    """AUTH-19: e os nega para o perfil comum."""
    assert Usuario(perfil=Usuario.Perfil.USUARIO).is_administrador is False


@pytest.mark.django_db
def test_createsuperuser_nasce_administrador():
    """AUTH-20: o primeiro admin do MVP vem daqui, sem passar argumento."""
    admin = Usuario.objects.create_superuser(
        username="raiz", email="raiz@x.com", password="senha-forte-123"
    )
    admin.refresh_from_db()
    assert admin.perfil == Usuario.Perfil.ADMINISTRADOR


@pytest.mark.django_db
def test_create_user_nasce_usuario_comum():
    """AUTH-17: a conta comum continua nascendo USUARIO."""
    comum = Usuario.objects.create_user(
        username="ana", email="ana@x.com", password="senha-forte-123"
    )
    comum.refresh_from_db()
    assert comum.perfil == Usuario.Perfil.USUARIO


@pytest.mark.django_db
def test_promover_a_administrador_concede_is_staff():
    """AUTH-22: sem is_staff o administrador nao abre o admin, unica
    superficie de troca de perfil no MVP, e a RN11 fica inexequivel."""
    u = Usuario.objects.create_user(username="ana", email="ana@x.com")
    u.perfil = Usuario.Perfil.ADMINISTRADOR
    u.save()
    u.refresh_from_db()
    assert u.is_staff is True


@pytest.mark.django_db
def test_usuario_comum_nao_ganha_is_staff():
    """AUTH-22: a sincronizacao nao pode promover quem nao foi promovido."""
    u = Usuario.objects.create_user(username="bruno", email="bruno@x.com")
    u.refresh_from_db()
    assert u.is_staff is False


@pytest.mark.django_db
def test_is_staff_concedido_manualmente_nao_e_revogado():
    """A sincronizacao concede, nunca revoga: um USUARIO com acesso ao admin
    dado de proposito continua com ele depois de qualquer save()."""
    u = Usuario.objects.create_user(username="carla", email="carla@x.com", is_staff=True)
    u.save()
    u.refresh_from_db()
    assert u.is_staff is True
    assert u.perfil == Usuario.Perfil.USUARIO
