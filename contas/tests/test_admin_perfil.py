"""Testes e2e da restricao do campo de perfil no admin.

AUTH-21 (ramo de redirecionamento) e AUTH-22, pela RN11: so administrador
atribui perfil.
"""

import pytest
from django.contrib.auth.models import Permission

from contas.models import Usuario

LISTA = "/admin/contas/usuario/"


def _editar(conta):
    return f"{LISTA}{conta.pk}/change/"


@pytest.fixture
def usuario_staff(db):
    """USUARIO com acesso ao admin concedido a mao, para outro fim."""
    conta = Usuario.objects.create_user(username="carla", email="carla@x.com", is_staff=True)
    conta.user_permissions.set(
        Permission.objects.filter(codename__in=["view_usuario", "change_usuario"])
    )
    return conta


@pytest.fixture
def terceiro(db):
    return Usuario.objects.create_user(username="davi", email="davi@x.com")


@pytest.fixture
def administrador_promovido(db):
    """ADMINISTRADOR que nao e superuser: nenhuma permissao de modelo."""
    return Usuario.objects.create_user(
        username="elis", email="elis@x.com", perfil=Usuario.Perfil.ADMINISTRADOR
    )


def test_usuario_com_staff_abre_o_proprio_registro_sem_o_campo_perfil(client, usuario_staff):
    """AUTH-22: o perfil nao e editavel por quem nao e administrador."""
    client.force_login(usuario_staff)
    resposta = client.get(_editar(usuario_staff))
    assert resposta.status_code == 200
    campos = resposta.context["adminform"].form.fields
    assert "perfil" not in campos
    assert "is_superuser" not in campos


def test_usuario_com_staff_nao_altera_conta_de_terceiro(client, usuario_staff, terceiro):
    """AUTH-22: a conta alheia abre, no maximo, em modo leitura."""
    client.force_login(usuario_staff)
    resposta = client.get(_editar(terceiro))
    assert resposta.context["has_change_permission"] is False


def test_administrador_ve_e_altera_o_perfil_de_outra_conta(
    client, administrador_promovido, terceiro
):
    """AUTH-22: o ADMINISTRADOR abre a tela e promove outra conta."""
    client.force_login(administrador_promovido)
    tela = client.get(_editar(terceiro))
    assert tela.status_code == 200
    assert "perfil" in tela.context["adminform"].form.fields

    dados = {
        "username": terceiro.username,
        "email": terceiro.email,
        "perfil": Usuario.Perfil.ADMINISTRADOR,
        "is_active": "on",
        "date_joined_0": terceiro.date_joined.strftime("%d/%m/%Y"),
        "date_joined_1": terceiro.date_joined.strftime("%H:%M:%S"),
    }
    resposta = client.post(_editar(terceiro), dados)
    assert resposta.status_code == 302, resposta.context["adminform"].form.errors
    terceiro.refresh_from_db()
    assert terceiro.perfil == Usuario.Perfil.ADMINISTRADOR


def test_usuario_sem_staff_e_mandado_ao_login_do_admin(client, terceiro):
    """AUTH-21, ramo de redirecionamento: sem acesso a area de administracao."""
    client.force_login(terceiro)
    resposta = client.get(LISTA)
    assert resposta.status_code == 302
    assert resposta["Location"].startswith("/admin/login/")


# POST forjado: o campo perfil nao esta no formulario de quem nao e
# administrador, mas nada impede alguem de envia-lo na mao.


def _post_de_edicao(conta, **alteracoes):
    dados = {
        "username": conta.username,
        "email": conta.email,
        "is_active": "on",
        "is_staff": "on" if conta.is_staff else "",
        "user_permissions": [str(p.pk) for p in conta.user_permissions.all()],
        "date_joined_0": conta.date_joined.strftime("%d/%m/%Y"),
        "date_joined_1": conta.date_joined.strftime("%H:%M:%S"),
    }
    dados.update(alteracoes)
    return dados


def test_usuario_forjando_a_propria_promocao_recebe_403(client, usuario_staff):
    """AUTH-21, ramo 403: e o perfil persistido nao muda."""
    client.force_login(usuario_staff)
    resposta = client.post(
        _editar(usuario_staff),
        _post_de_edicao(usuario_staff, perfil=Usuario.Perfil.ADMINISTRADOR),
    )
    assert resposta.status_code == 403
    usuario_staff.refresh_from_db()
    assert usuario_staff.perfil == Usuario.Perfil.USUARIO


def test_usuario_forjando_a_promocao_de_terceiro_recebe_403(client, usuario_staff, terceiro):
    """AUTH-21, ramo 403: vale tambem sobre a conta alheia."""
    client.force_login(usuario_staff)
    resposta = client.post(
        _editar(terceiro), _post_de_edicao(terceiro, perfil=Usuario.Perfil.ADMINISTRADOR)
    )
    assert resposta.status_code == 403
    terceiro.refresh_from_db()
    assert terceiro.perfil == Usuario.Perfil.USUARIO


def test_o_mesmo_post_feito_por_administrador_e_aceito(
    client, administrador_promovido, usuario_staff
):
    """AUTH-22: a promocao que foi recusada ao USUARIO passa para o
    ADMINISTRADOR."""
    client.force_login(administrador_promovido)
    resposta = client.post(
        _editar(usuario_staff),
        _post_de_edicao(usuario_staff, perfil=Usuario.Perfil.ADMINISTRADOR),
    )
    assert resposta.status_code == 302
    usuario_staff.refresh_from_db()
    assert usuario_staff.perfil == Usuario.Perfil.ADMINISTRADOR
