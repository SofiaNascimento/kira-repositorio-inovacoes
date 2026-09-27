"""Testes e2e do Usuario no Django admin.

AUTH-22 e AUTH-08, com a RN11 de pano de fundo: o admin e a unica
superficie de criacao de contas e de troca de perfil no MVP.
"""

import pytest

from contas.models import Usuario

SENHA_NOVA = "Nova-senha-forte-2026"
LISTA = "/admin/contas/usuario/"
NOVO = "/admin/contas/usuario/add/"


@pytest.fixture
def administrador(db):
    return Usuario.objects.create_superuser(
        username="raiz", email="raiz@x.com", password="senha-da-raiz-123"
    )


@pytest.fixture
def cliente_admin(client, administrador):
    client.force_login(administrador)
    return client


def _criar_conta(client, username="bruno", email="bruno@x.com"):
    return client.post(
        NOVO,
        {
            "username": username,
            "email": email,
            "usable_password": "true",
            "password1": SENHA_NOVA,
            "password2": SENHA_NOVA,
        },
    )


def test_administrador_lista_e_cria_contas_com_perfil_visivel(cliente_admin):
    """AUTH-22: o ADMINISTRADOR abre a gestao de contas, ve o perfil na
    listagem e no filtro, e cria uma conta."""
    lista = cliente_admin.get(LISTA)
    assert lista.status_code == 200
    assert "perfil" in lista.context["cl"].list_display
    assert "perfil" in lista.context["cl"].list_filter

    resposta = _criar_conta(cliente_admin)
    assert resposta.status_code == 302
    assert Usuario.objects.filter(username="bruno", email="bruno@x.com").exists()


def test_conta_criada_pelo_admin_nasce_usuario_com_senha_em_hash(cliente_admin):
    """AUTH-17 e AUTH-06: perfil USUARIO e so o hash da senha no banco."""
    _criar_conta(cliente_admin)
    criada = Usuario.objects.get(username="bruno")
    assert criada.perfil == Usuario.Perfil.USUARIO
    assert criada.password != SENHA_NOVA
    assert criada.password.startswith("pbkdf2_sha256$")
    assert criada.check_password(SENHA_NOVA) is True


def test_tela_de_edicao_nao_expoe_a_senha_nem_o_hash(cliente_admin):
    """AUTH-08: a edicao traz o perfil, e a senha aparece so como resumo
    mascarado do hash, sem campo que a aceite em texto puro."""
    _criar_conta(cliente_admin)
    criada = Usuario.objects.get(username="bruno")
    resposta = cliente_admin.get(f"{LISTA}{criada.pk}/change/")
    assert resposta.status_code == 200
    assert "perfil" in resposta.context["adminform"].form.fields

    html = resposta.content.decode()
    assert SENHA_NOVA not in html
    assert criada.password not in html
    assert criada.password.split("$")[-1] not in html
    assert 'name="password"' not in html
