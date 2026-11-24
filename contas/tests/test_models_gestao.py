"""Testes do gestor de unidade e da unidade da conta no modelo Usuario.

Derivados das ACs GEST-01 a GEST-03 (.specs/features/gestao-por-unidade/spec.md)
e da extensao da AD-004: o gestor e um terceiro valor do perfil, a unidade e
opcional e so o gestor precisa dela, com a regra no banco.
"""

import pytest
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError

from contas.models import Usuario
from inovacoes.models import Unidade

GESTOR = Usuario.Perfil.GESTOR_DE_UNIDADE


@pytest.fixture
def sede(db):
    return Unidade.objects.get(nome="Sede")


@pytest.mark.unit
def test_rotulo_do_gestor_e_gestor_de_unidade():
    """GEST-02: o valor novo e rotulado "Gestor de unidade"."""
    assert Usuario.Perfil.GESTOR_DE_UNIDADE.label == "Gestor de unidade"


@pytest.mark.unit
@pytest.mark.parametrize(
    ("perfil", "superusuario", "esperado"),
    [
        (GESTOR, False, True),
        (Usuario.Perfil.USUARIO, False, False),
        (Usuario.Perfil.ADMINISTRADOR, False, False),
        (Usuario.Perfil.USUARIO, True, False),
    ],
    ids=["gestor", "usuario", "administrador", "superusuario_usuario"],
)
def test_is_gestor_de_unidade_so_para_o_perfil_gestor(perfil, superusuario, esperado):
    """AD-004 estendida: o perfil e o unico criterio, is_superuser nao conta."""
    conta = Usuario(perfil=perfil, is_superuser=superusuario, is_staff=superusuario)
    assert conta.is_gestor_de_unidade is esperado


@pytest.mark.django_db
def test_gestor_sem_unidade_e_recusado_no_create():
    """GEST-03: a CHECK usuario_gestor_tem_unidade barra o create() direto."""
    with pytest.raises(IntegrityError, match="usuario_gestor_tem_unidade"), transaction.atomic():
        Usuario.objects.create(username="gil", email="gil@x.com", perfil=GESTOR)
    assert not Usuario.objects.filter(username="gil").exists()


@pytest.mark.django_db
def test_gestor_sem_unidade_e_recusado_no_update_em_massa():
    """GEST-03: update() em massa nao passa por validacao nenhuma; o banco recusa."""
    ana = Usuario.objects.create(username="ana", email="ana@x.com")
    with pytest.raises(IntegrityError, match="usuario_gestor_tem_unidade"), transaction.atomic():
        Usuario.objects.filter(pk=ana.pk).update(perfil=GESTOR)
    ana.refresh_from_db()
    assert ana.perfil == Usuario.Perfil.USUARIO


@pytest.mark.django_db
def test_tirar_a_unidade_do_gestor_em_massa_e_recusado(sede):
    """GEST-03: a regra vale tambem quando muda a unidade, nao so o perfil."""
    gil = Usuario.objects.create(username="gil", email="gil@x.com", perfil=GESTOR, unidade=sede)
    with pytest.raises(IntegrityError, match="usuario_gestor_tem_unidade"), transaction.atomic():
        Usuario.objects.filter(pk=gil.pk).update(unidade=None)
    gil.refresh_from_db()
    assert gil.unidade_id == sede.pk


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("perfil", "com_unidade"),
    [
        (GESTOR, True),
        (Usuario.Perfil.USUARIO, False),
        (Usuario.Perfil.ADMINISTRADOR, False),
    ],
    ids=["gestor_com_unidade", "usuario_sem_unidade", "administrador_sem_unidade"],
)
def test_contas_validas_gravam(sede, perfil, com_unidade):
    """GEST-01 e GEST-03: so o gestor precisa de unidade; o valor de 17
    caracteres cabe na coluna e volta igual do banco."""
    unidade = sede if com_unidade else None
    with transaction.atomic():
        conta = Usuario.objects.create(
            username="nina", email="nina@x.com", perfil=perfil, unidade=unidade
        )
    conta.refresh_from_db()
    assert conta.perfil == perfil
    assert conta.unidade == unidade


@pytest.mark.django_db
def test_unidade_com_conta_vinculada_nao_e_excluida(sede):
    """GEST-01: on_delete=PROTECT; a unidade e a conta continuam."""
    Usuario.objects.create(username="ana", email="ana@x.com", unidade=sede)
    with pytest.raises(ProtectedError), transaction.atomic():
        sede.delete()
    assert Unidade.objects.filter(pk=sede.pk).exists()
    assert Usuario.objects.get(username="ana").unidade_id == sede.pk


@pytest.mark.django_db
def test_unidade_e_opcional_e_o_reverso_e_usuarios(sede):
    """GEST-01: campo opcional, ligado a Unidade pelo reverso usuarios."""
    campo = Usuario._meta.get_field("unidade")
    assert (campo.null, campo.blank) == (True, True)
    ana = Usuario.objects.create(username="ana", email="ana@x.com", unidade=sede)
    assert list(sede.usuarios.all()) == [ana]


@pytest.mark.django_db
def test_senha_provisoria_comeca_desmarcada():
    """Conta criada sem dizer nada nao tem senha provisoria (fluxo atual do admin)."""
    ana = Usuario.objects.create_user(username="ana", email="ana@x.com", password="x")
    ana.refresh_from_db()
    assert ana.senha_provisoria is False


@pytest.mark.django_db
def test_gestor_nao_ganha_is_staff_no_save(sede):
    """AD-004 estendida e AD-007: o save() so concede is_staff ao ADMINISTRADOR."""
    gil = Usuario.objects.create_user(
        username="gil", email="gil@x.com", perfil=GESTOR, unidade=sede
    )
    gil.refresh_from_db()
    assert gil.is_staff is False
