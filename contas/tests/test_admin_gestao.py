"""Testes e2e da unidade e da senha provisoria no admin (gestao-por-unidade, T5).

Derivados das ACs GEST-04 a GEST-08 (.specs/features/gestao-por-unidade/spec.md,
GEST-07 na versao da emenda E-1) e da AD-007: o admin segue so do ADMINISTRADOR.
"""

import re

import pytest

from contas.models import Usuario
from inovacoes.models import Unidade
from inovacoes.tests.visibilidade import exibido

LISTA = "/admin/contas/usuario/"
GESTOR = Usuario.Perfil.GESTOR_DE_UNIDADE
MENSAGEM = "Gestor de unidade precisa de uma unidade."
SENHA_NOVA = "Nova-senha-forte-2026"


def _editar(conta):
    return f"{LISTA}{conta.pk}/change/"


@pytest.fixture
def sede(db):
    return Unidade.objects.get(nome="Sede")


@pytest.fixture
def cliente_admin(client, db):
    raiz = Usuario.objects.create_superuser(
        username="raiz", email="raiz@x.com", password="senha-da-raiz-123"
    )
    client.force_login(raiz)
    return client


@pytest.fixture
def terceiro(db):
    return Usuario.objects.create_user(username="davi", email="davi@x.com")


def _post_de_edicao(conta, **alteracoes):
    dados = {
        "username": conta.username,
        "email": conta.email,
        "perfil": conta.perfil,
        "unidade": str(conta.unidade_id or ""),
        "is_active": "on",
        "date_joined_0": conta.date_joined.strftime("%d/%m/%Y"),
        "date_joined_1": conta.date_joined.strftime("%H:%M:%S"),
    }
    dados.update(alteracoes)
    return dados


# --- GEST-04: secao "Perfil" -------------------------------------------------------


def test_secao_perfil_tem_perfil_unidade_e_senha_provisoria(cliente_admin, terceiro):
    """GEST-04: na edicao exibida, Unidade e Senha provisoria vem na secao "Perfil",
    logo depois do campo Perfil."""
    html = exibido(cliente_admin.get(_editar(terceiro)).content.decode(), rigoroso=True)
    secoes = re.findall(
        r'<fieldset[^>]*>\s*<h2 id="[^"]*" class="fieldset-heading">([^<]*)</h2>(.*?)</fieldset>',
        html,
        re.S,
    )
    perfil = dict(secoes)["Perfil"]
    assert re.findall(r'<div class="form-row field-([a-z_]+)">', perfil) == [
        "perfil",
        "unidade",
        "senha_provisoria",
    ]
    assert re.search(r'<label for="id_unidade">Unidade:</label>', perfil)
    assert re.search(r'for="id_senha_provisoria">Senha provisória</label>', perfil)
    assert [nome for nome, corpo in secoes if 'name="unidade"' in corpo] == ["Perfil"]


# --- GEST-05: gestor sem unidade ---------------------------------------------------


def test_gestor_sem_unidade_mostra_o_erro_no_campo_uma_vez_e_nao_grava(cliente_admin, terceiro):
    """GEST-05: a mensagem fica no campo Unidade, uma vez so na pagina (a CHECK
    nao a repete como erro geral), e a conta nao muda."""
    resposta = cliente_admin.post(_editar(terceiro), _post_de_edicao(terceiro, perfil=GESTOR))
    assert resposta.status_code == 200
    assert resposta.context["adminform"].form.errors == {"unidade": [MENSAGEM]}
    html = resposta.content.decode()
    assert html.count(MENSAGEM) == 1
    assert re.search(
        r'<div class="form-row errors field-unidade">\s*'
        rf'<ul class="errorlist" id="id_unidade_error"><li>{MENSAGEM}</li></ul>',
        exibido(html, rigoroso=True),
    )
    terceiro.refresh_from_db()
    assert (terceiro.perfil, terceiro.unidade_id) == (Usuario.Perfil.USUARIO, None)


def test_gestor_com_unidade_grava(cliente_admin, terceiro, sede):
    """GEST-05: com a unidade, o ADMINISTRADOR nomeia o gestor."""
    resposta = cliente_admin.post(
        _editar(terceiro), _post_de_edicao(terceiro, perfil=GESTOR, unidade=str(sede.pk))
    )
    assert resposta.status_code == 302
    terceiro.refresh_from_db()
    assert (terceiro.perfil, terceiro.unidade_id) == (GESTOR, sede.pk)


# --- GEST-06: coluna e filtro -------------------------------------------------------


def test_lista_tem_a_coluna_e_o_filtro_unidade(cliente_admin, sede):
    """GEST-06: o cabecalho "Unidade", o nome da unidade na linha e o filtro "Por unidade"."""
    Usuario.objects.create_user(username="bia", email="bia@x.com", unidade=sede)
    resposta = cliente_admin.get(LISTA)
    assert resposta.status_code == 200
    html = exibido(resposta.content.decode(), rigoroso=True)
    assert re.search(
        r'<th scope="col" class="sortable column-unidade">\s*'
        r'<div class="text"><a href="[^"]*">Unidade</a></div>',
        html,
    )
    assert re.search(r'<td class="field-unidade[^"]*">Sede</td>', html)
    assert re.search(r'<details data-filter-title="unidade" open>\s*<summary>\s*Por unidade', html)
    filtro = resposta.context["cl"].filter_specs
    assert [f.title for f in filtro if f.field_path == "unidade"] == ["unidade"]


# --- Senha provisoria de conta criada no admin ---------------------------------------


def test_conta_criada_no_admin_nasce_sem_senha_provisoria(cliente_admin):
    """Assumptions da spec: o fluxo do admin segue igual; a caixa comeca desmarcada."""
    resposta = cliente_admin.post(
        f"{LISTA}add/",
        {
            "username": "bruno",
            "email": "bruno@x.com",
            "usable_password": "true",
            "password1": SENHA_NOVA,
            "password2": SENHA_NOVA,
        },
    )
    assert resposta.status_code == 302
    criada = Usuario.objects.get(username="bruno")
    assert criada.senha_provisoria is False
    edicao = cliente_admin.get(_editar(criada)).content.decode()
    caixa = re.search(r'<input type="checkbox" name="senha_provisoria"[^>]*>', edicao).group(0)
    assert " checked" not in caixa


# --- GEST-07 (E-1): o gestor nao abre o admin (L-003) --------------------------------


@pytest.fixture
def gestor(sede):
    return Usuario.objects.create_user(
        username="gil", email="gil@x.com", perfil=GESTOR, unidade=sede
    )


@pytest.fixture
def gestor_staff(sede):
    """Gestor a quem alguem deu is_staff a mao: o perfil, nao a bandeira, decide."""
    return Usuario.objects.create_user(
        username="fabi", email="fabi@x.com", perfil=GESTOR, unidade=sede, is_staff=True
    )


TELAS = [
    "indice_de_contas",
    "lista_de_usuarios",
    "novo_usuario",
    "proprio_registro",
    "registro_de_terceiro",
    "exclusao_de_terceiro",
    "indice_de_inovacoes",
    "lista_de_unidades",
    "nova_unidade",
    "registro_de_unidade",
    "exclusao_de_unidade",
]


def _tela(nome, proprio, terceiro, unidade):
    return {
        "indice_de_contas": "/admin/contas/",
        "lista_de_usuarios": LISTA,
        "novo_usuario": f"{LISTA}add/",
        "proprio_registro": _editar(proprio),
        "registro_de_terceiro": _editar(terceiro),
        "exclusao_de_terceiro": f"{LISTA}{terceiro.pk}/delete/",
        "indice_de_inovacoes": "/admin/inovacoes/",
        "lista_de_unidades": "/admin/inovacoes/unidade/",
        "nova_unidade": "/admin/inovacoes/unidade/add/",
        "registro_de_unidade": f"/admin/inovacoes/unidade/{unidade.pk}/change/",
        "exclusao_de_unidade": f"/admin/inovacoes/unidade/{unidade.pk}/delete/",
    }[nome]


@pytest.mark.parametrize("tela", TELAS)
def test_gestor_sem_staff_vai_ao_login_do_admin(client, gestor, terceiro, sede, tela):
    """GEST-07 (E-1): sem is_staff, como o USUARIO (AUTH-21), vai ao login do admin."""
    client.force_login(gestor)
    resposta = client.get(_tela(tela, gestor, terceiro, sede))
    assert resposta.status_code == 302
    assert resposta["Location"].startswith("/admin/login/")


@pytest.mark.parametrize("tela", TELAS)
def test_gestor_com_staff_e_negado(client, gestor_staff, terceiro, sede, tela):
    """GEST-07 (E-1): com is_staff, 403 em toda tela, como o USUARIO com staff
    (AUTH-22). No indice do app o Django nega com 404, como faz ao USUARIO."""
    client.force_login(gestor_staff)
    esperado = 404 if tela.startswith("indice_") else 403
    assert client.get(_tela(tela, gestor_staff, terceiro, sede)).status_code == esperado


@pytest.mark.parametrize("alvo", ["proprio", "terceiro"])
def test_post_forjado_do_gestor_com_staff_nao_muda_perfil_nem_unidade(
    client, gestor_staff, terceiro, alvo
):
    """GEST-07, AD-007: o POST de alteracao nem chega ao formulario."""
    conta = gestor_staff if alvo == "proprio" else terceiro
    outra = Unidade.objects.get(nome="Filial Norte")
    client.force_login(gestor_staff)
    resposta = client.post(
        _editar(conta),
        _post_de_edicao(
            conta, perfil=Usuario.Perfil.ADMINISTRADOR, unidade=str(outra.pk), is_staff="on"
        ),
    )
    assert resposta.status_code == 403
    antes = (conta.perfil, conta.unidade_id)
    conta.refresh_from_db()
    assert (conta.perfil, conta.unidade_id) == antes


# --- GEST-08: unidade com conta nao se exclui ---------------------------------------


def test_excluir_unidade_com_conta_vinculada_e_recusado(cliente_admin, sede):
    """GEST-08: a tela de exclusao lista a conta que protege a unidade, e o envio
    da confirmacao nao apaga."""
    Usuario.objects.create_user(username="bia", email="bia@x.com", unidade=sede)
    caminho = f"/admin/inovacoes/unidade/{sede.pk}/delete/"
    tela = cliente_admin.get(caminho)
    assert tela.status_code == 200
    protegidos = [re.sub(r"<[^>]+>", "", str(o)) for o in tela.context["protected"]]
    assert protegidos == ["Usuário: bia"]

    resposta = cliente_admin.post(caminho, {"post": "yes"})
    assert resposta.status_code == 200
    assert Unidade.objects.filter(pk=sede.pk).exists()
    assert Usuario.objects.get(username="bia").unidade_id == sede.pk
