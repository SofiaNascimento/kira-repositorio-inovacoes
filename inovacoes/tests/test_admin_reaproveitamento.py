"""Testes e2e do admin de reaproveitamentos (REAP-24, REAP-26, REAP-27, AD-007).

So o ADMINISTRADOR lista e exclui; ninguem inclui nem altera. Os registros de
preparo nascem pelo metodo do modelo (AD-012).
"""

import re

import pytest
from django.contrib.auth.models import Permission
from django.utils import formats, timezone

from contas.models import Usuario
from inovacoes.models import Reaproveitamento, StatusInovacao, Unidade
from inovacoes.tests.visibilidade import exibido

LISTA = "/admin/inovacoes/reaproveitamento/"


def _tela(nome, registro):
    return {
        "lista": LISTA,
        "registro": f"{LISTA}{registro.pk}/change/",
        "exclusao": f"{LISTA}{registro.pk}/delete/",
    }[nome]


@pytest.fixture
def registro(criar_inovacao, terceiro):
    inovacao = criar_inovacao(status=StatusInovacao.DISPONIVEL_PARA_REPLICACAO)
    return inovacao.registrar_reaproveitamento(
        unidade=Unidade.objects.get(nome="Sede"), por=terceiro
    )


def _permissoes():
    return Permission.objects.filter(
        content_type__app_label="inovacoes", content_type__model="reaproveitamento"
    )


# L-003: as duas contas que o framework deixaria entrar no admin. Com is_staff
# e todas as permissoes do modelo, e com is_superuser; o perfil e que decide.
@pytest.fixture(params=["staff", "superusuario"])
def usuario_com_acesso_ao_admin(request, db):
    extra = {"is_staff": True}
    if request.param == "superusuario":
        extra["is_superuser"] = True
    conta = Usuario.objects.create_user(
        username=f"dora_{request.param}", email=f"dora_{request.param}@x.com", **extra
    )
    conta.user_permissions.set(_permissoes())
    conta.refresh_from_db()
    assert conta.perfil == Usuario.Perfil.USUARIO
    assert conta.is_superuser is (request.param == "superusuario")
    return conta


@pytest.fixture
def logado_como_administrador(client, administrador):
    client.force_login(administrador)
    return client


def _celula(html, campo):
    """Texto da celula da coluna `campo` na primeira linha da listagem."""
    achado = re.search(rf'<t[dh] class="field-{campo}[^"]*">(.*?)</t[dh]>', html, re.S)
    assert achado, f"sem coluna {campo}"
    return re.sub(r"<[^>]+>", "", achado.group(1)).strip()


def test_administrador_ve_a_listagem_com_os_quatro_campos(logado_como_administrador, registro):
    """REAP-26: inovacao, unidade, responsavel e data de cada registro."""
    resposta = logado_como_administrador.get(LISTA)
    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert _celula(html, "inovacao") == str(registro.inovacao)
    assert _celula(html, "unidade") == "Sede"
    assert _celula(html, "registrado_por") == "bruno"
    data = formats.localize(timezone.template_localtime(registro.data))
    assert _celula(html, "data") == data
    # L-028, L-030: as quatro celulas ficam na tela e no leitor de tela.
    visivel = exibido(html)
    for campo in ["inovacao", "unidade", "registrado_por", "data"]:
        assert _celula(visivel, campo) == _celula(html, campo), campo


def test_administrador_exclui_pela_confirmacao_do_admin(logado_como_administrador, registro):
    """REAP-26: a tela de confirmacao abre e o POST apaga o registro."""
    assert logado_como_administrador.get(_tela("exclusao", registro)).status_code == 200
    resposta = logado_como_administrador.post(_tela("exclusao", registro), {"post": "yes"})
    assert resposta.status_code == 302
    assert not Reaproveitamento.objects.filter(pk=registro.pk).exists()


@pytest.mark.parametrize("tela", ["lista", "registro", "exclusao"])
def test_usuario_com_acesso_ao_admin_recebe_403(
    client, usuario_com_acesso_ao_admin, registro, tela
):
    """REAP-26, L-003: USUARIO com is_staff ou is_superuser e negado em toda tela."""
    client.force_login(usuario_com_acesso_ao_admin)
    assert client.get(_tela(tela, registro)).status_code == 403
    assert Reaproveitamento.objects.filter(pk=registro.pk).exists()


def test_usuario_com_acesso_ao_admin_forjando_exclusao_recebe_403(
    client, usuario_com_acesso_ao_admin, registro
):
    """REAP-26: o POST de exclusao nao chega a apagar."""
    client.force_login(usuario_com_acesso_ao_admin)
    resposta = client.post(_tela("exclusao", registro), {"post": "yes"})
    assert resposta.status_code == 403
    assert Reaproveitamento.objects.filter(pk=registro.pk).exists()


def test_superusuario_sem_staff_nao_entra_no_admin(client, registro):
    """REAP-26: sem is_staff, o proprio admin manda ao login dele; nada e apagado."""
    conta = Usuario.objects.create_user(username="eva", email="eva@x.com", is_superuser=True)
    client.force_login(conta)
    for tela in ["lista", "registro", "exclusao"]:
        resposta = client.get(_tela(tela, registro))
        assert resposta.status_code == 302, tela
        assert resposta["Location"].startswith("/admin/login/"), tela
    client.post(_tela("exclusao", registro), {"post": "yes"})
    assert Reaproveitamento.objects.filter(pk=registro.pk).exists()


def test_listagem_nao_oferece_adicionar(logado_como_administrador, registro):
    """REAP-27: nem o administrador ve o link de inclusao."""
    html = logado_como_administrador.get(LISTA).content.decode()
    assert f'href="{LISTA}add/"' not in html


def test_url_de_adicionar_responde_403_e_nao_cria(
    logado_como_administrador, registro, criar_inovacao, administrador
):
    """REAP-27: GET e POST forjado na inclusao; nenhum registro novo."""
    outra = criar_inovacao(
        titulo="Outra Inovacao", status=StatusInovacao.DISPONIVEL_PARA_REPLICACAO
    )
    assert logado_como_administrador.get(f"{LISTA}add/").status_code == 403
    resposta = logado_como_administrador.post(
        f"{LISTA}add/",
        {
            "inovacao": outra.pk,
            "unidade": Unidade.objects.get(nome="Filial Norte").pk,
            "registrado_por": administrador.pk,
        },
    )
    assert resposta.status_code == 403
    assert list(Reaproveitamento.objects.values_list("pk", flat=True)) == [registro.pk]


def test_registro_abre_so_para_leitura(logado_como_administrador, registro):
    """REAP-27: a tela do registro nao tem botao de salvar."""
    resposta = logado_como_administrador.get(_tela("registro", registro))
    assert resposta.status_code == 200
    assert 'name="_save"' not in resposta.content.decode()


def test_post_na_alteracao_responde_403_e_nao_muda(logado_como_administrador, registro):
    """REAP-27: POST forjado na URL de alteracao nao troca a unidade."""
    antes = Reaproveitamento.objects.values().get(pk=registro.pk)
    resposta = logado_como_administrador.post(
        _tela("registro", registro),
        {
            "inovacao": registro.inovacao_id,
            "unidade": Unidade.objects.get(nome="Filial Norte").pk,
            "registrado_por": registro.registrado_por_id,
        },
    )
    assert resposta.status_code == 403
    assert Reaproveitamento.objects.values().get(pk=registro.pk) == antes


def test_unidade_referenciada_fica_protegida_no_admin(logado_como_administrador, registro):
    """REAP-24: a exclusao da unidade e recusada e lista o reaproveitamento."""
    sede = registro.unidade
    resposta = logado_como_administrador.post(
        f"/admin/inovacoes/unidade/{sede.pk}/delete/", {"post": "yes"}
    )
    assert resposta.status_code == 200
    assert str(registro) in str(resposta.context["protected"])
    assert Unidade.objects.filter(pk=sede.pk).exists()
    assert Reaproveitamento.objects.filter(pk=registro.pk).exists()
