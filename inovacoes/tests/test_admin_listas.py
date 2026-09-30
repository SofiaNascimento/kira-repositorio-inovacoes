"""Testes e2e do admin das listas controladas (RN07, AD-007).

INOV-19, INOV-20 e INOV-21: so o ADMINISTRADOR mantem Unidade e Categoria, e
um item em uso nao pode ser excluido.
"""

import pytest
from django.contrib import admin
from django.contrib.auth.models import Permission

from contas.models import Usuario
from inovacoes.models import Categoria, Inovacao, Unidade

LISTAS = [Unidade, Categoria]


def _lista(modelo):
    return f"/admin/inovacoes/{modelo._meta.model_name}/"


def _tela(nome, modelo, item):
    return {
        "lista": _lista(modelo),
        "novo": f"{_lista(modelo)}add/",
        "alteracao": f"{_lista(modelo)}{item.pk}/change/",
        "exclusao": f"{_lista(modelo)}{item.pk}/delete/",
    }[nome]


@pytest.fixture
def usuario_staff(db):
    """USUARIO com acesso ao admin e todas as permissoes de modelo sobre as
    listas: o perfil, e nao a permissao, e que decide (AD-007)."""
    conta = Usuario.objects.create_user(username="carla", email="carla@x.com", is_staff=True)
    conta.user_permissions.set(
        Permission.objects.filter(
            content_type__app_label="inovacoes",
            content_type__model__in=["unidade", "categoria"],
        )
    )
    return conta


@pytest.fixture
def administrador_promovido(db):
    """ADMINISTRADOR que nao e superuser: nenhuma permissao de modelo."""
    return Usuario.objects.create_user(
        username="elis", email="elis@x.com", perfil=Usuario.Perfil.ADMINISTRADOR
    )


def _item(modelo):
    return modelo.objects.create(nome="Teste Item")


@pytest.mark.django_db
@pytest.mark.parametrize("modelo", LISTAS)
@pytest.mark.parametrize("tela", ["lista", "novo", "alteracao", "exclusao"])
def test_usuario_com_staff_recebe_403_nas_telas_da_lista(client, usuario_staff, modelo, tela):
    """INOV-20: nem com is_staff e todas as permissoes de modelo."""
    client.force_login(usuario_staff)
    assert client.get(_tela(tela, modelo, _item(modelo))).status_code == 403


def test_usuario_com_staff_nao_ve_o_indice_da_app(client, usuario_staff):
    """INOV-20: sem modelo acessivel, o Django nega o indice da app com 404."""
    client.force_login(usuario_staff)
    assert client.get("/admin/inovacoes/").status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize("modelo", LISTAS)
def test_usuario_com_staff_forjando_inclusao_recebe_403(client, usuario_staff, modelo):
    client.force_login(usuario_staff)
    resposta = client.post(f"{_lista(modelo)}add/", {"nome": "Teste Forjado"})
    assert resposta.status_code == 403
    assert not modelo.objects.filter(nome="Teste Forjado").exists()


@pytest.mark.django_db
@pytest.mark.parametrize("modelo", LISTAS)
def test_usuario_com_staff_forjando_renomeacao_recebe_403(client, usuario_staff, modelo):
    item = _item(modelo)
    client.force_login(usuario_staff)
    resposta = client.post(_tela("alteracao", modelo, item), {"nome": "Teste Forjado"})
    assert resposta.status_code == 403
    item.refresh_from_db()
    assert item.nome == "Teste Item"


@pytest.mark.django_db
@pytest.mark.parametrize("modelo", LISTAS)
def test_usuario_com_staff_forjando_exclusao_recebe_403(client, usuario_staff, modelo):
    item = _item(modelo)
    client.force_login(usuario_staff)
    resposta = client.post(_tela("exclusao", modelo, item), {"post": "yes"})
    assert resposta.status_code == 403
    assert modelo.objects.filter(pk=item.pk).exists()


@pytest.mark.django_db
@pytest.mark.parametrize("modelo", LISTAS)
def test_administrador_lista_os_itens(client, administrador_promovido, modelo):
    """INOV-21: a lista abre e mostra os itens cadastrados."""
    _item(modelo)
    client.force_login(administrador_promovido)
    resposta = client.get(_lista(modelo))
    assert resposta.status_code == 200
    assert "Teste Item" in resposta.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize("modelo", LISTAS)
def test_administrador_inclui_item(client, administrador_promovido, modelo):
    """INOV-21."""
    client.force_login(administrador_promovido)
    resposta = client.post(f"{_lista(modelo)}add/", {"nome": "Teste Novo"})
    assert resposta.status_code == 302
    assert modelo.objects.filter(nome="Teste Novo").exists()


@pytest.mark.django_db
@pytest.mark.parametrize("modelo", LISTAS)
def test_administrador_renomeia_item(client, administrador_promovido, modelo):
    """INOV-21: renomear e permitido mesmo com o item em uso."""
    item = _item(modelo)
    client.force_login(administrador_promovido)
    resposta = client.post(_tela("alteracao", modelo, item), {"nome": "Teste Renomeado"})
    assert resposta.status_code == 302
    item.refresh_from_db()
    assert item.nome == "Teste Renomeado"


@pytest.mark.django_db
@pytest.mark.parametrize("campo", ["unidade", "categoria"])
def test_administrador_nao_exclui_item_em_uso(
    client, administrador_promovido, criar_inovacao, campo
):
    """INOV-19: o admin recusa a exclusao, diz o motivo e o item fica."""
    inovacao = criar_inovacao()
    item = getattr(inovacao, campo)
    client.force_login(administrador_promovido)
    resposta = client.post(_tela("exclusao", type(item), item), {"post": "yes"})
    assert resposta.status_code == 200
    assert list(resposta.context["protected"]) != []
    assert inovacao.titulo in str(resposta.context["protected"])
    assert type(item).objects.filter(pk=item.pk).exists()


def test_inovacao_nao_esta_no_admin():
    """Out of Scope: o admin contornaria a autoria (RN08)."""
    assert not admin.site.is_registered(Inovacao)
