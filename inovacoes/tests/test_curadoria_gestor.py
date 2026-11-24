"""Testes da curadoria pelo gestor da unidade de origem (gestao-por-unidade, T3).

Derivados das ACs GEST-48 a GEST-51, GEST-53 e GEST-54
(.specs/features/gestao-por-unidade/spec.md) e da extensao da AD-009: a regra
continua so em Inovacao.pode_ser_alterada_por, e editar, excluir, avancar e o
detalhe herdam sem mudar as views.
"""

import pytest
from django.contrib.auth.models import AnonymousUser
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from contas.models import Usuario
from inovacoes.models import Inovacao, MudancaDeStatus, StatusInovacao, Unidade
from inovacoes.tests.test_views_detalhe import CONSULTAS_DO_DETALHE
from inovacoes.tests.test_views_detalhe_v2 import _acoes, _esperado
from inovacoes.tests.visibilidade import exibido

GESTOR = Usuario.Perfil.GESTOR_DE_UNIDADE
EM_TESTE = StatusInovacao.EM_TESTE
VALIDADA = StatusInovacao.VALIDADA
DISPONIVEL = StatusInovacao.DISPONIVEL_PARA_REPLICACAO
NEGADO = "Você não tem permissão para alterar esta inovação."


@pytest.fixture
def gestor(unidade):
    """Gestor da unidade de origem das inovacoes do criar_inovacao."""
    return Usuario.objects.create_user(
        username="gil", email="gil@x.com", perfil=GESTOR, unidade=unidade
    )


@pytest.fixture
def gestor_de_outra_unidade(db):
    return Usuario.objects.create_user(
        username="fabi", email="fabi@x.com", perfil=GESTOR, unidade=Unidade.objects.get(nome="Sede")
    )


def _entrar(client, conta):
    client.force_login(conta)
    return client


# --- GEST-48: a regra do modelo -----------------------------------------------------


def _conta(caso, request, unidade):
    if caso in {"autor", "gestor", "gestor_de_outra_unidade", "administrador"}:
        return request.getfixturevalue(caso)
    if caso == "anonimo":
        return AnonymousUser()
    bandeiras = {
        "usuario_da_mesma_unidade": {},
        "usuario_staff_da_mesma_unidade": {"is_staff": True},
        "superusuario_usuario_da_mesma_unidade": {"is_superuser": True},
    }[caso]
    return Usuario.objects.create_user(
        username=f"dora_{caso}", email=f"{caso}@x.com", unidade=unidade, **bandeiras
    )


@pytest.mark.parametrize(
    ("caso", "esperado"),
    [
        ("autor", True),
        ("administrador", True),
        ("gestor", True),
        ("gestor_de_outra_unidade", False),
        ("usuario_da_mesma_unidade", False),
        ("usuario_staff_da_mesma_unidade", False),
        ("superusuario_usuario_da_mesma_unidade", False),
        ("anonimo", False),
    ],
)
def test_pode_ser_alterada_por_cada_papel(request, criar_inovacao, unidade, caso, esperado):
    """GEST-48: autor, ADMINISTRADOR e gestor da unidade de origem; mais ninguem."""
    inovacao = criar_inovacao()
    assert inovacao.pode_ser_alterada_por(_conta(caso, request, unidade)) is esperado


def test_regra_do_gestor_nao_consulta_o_banco(
    gestor, gestor_de_outra_unidade, criar_inovacao, django_assert_num_queries
):
    """GEST-48, AD-009 estendida: le so unidade_id; a inovacao vem sem cache."""
    inovacao = Inovacao.objects.get(pk=criar_inovacao().pk)
    with django_assert_num_queries(0):
        assert inovacao.pode_ser_alterada_por(gestor) is True
        assert inovacao.pode_ser_alterada_por(gestor_de_outra_unidade) is False


# --- GEST-49: o detalhe exibe as acoes ----------------------------------------------


@pytest.mark.parametrize("status", [EM_TESTE, VALIDADA, DISPONIVEL], ids=str)
def test_gestor_da_unidade_ve_as_acoes_de_quem_pode_alterar(client, gestor, criar_inovacao, status):
    """GEST-49: "Editar", "Excluir" e, em Em teste e Validada, "Avançar para …",
    no cabecalho exibido, como para o autor."""
    inovacao = criar_inovacao(status=status)
    html = _entrar(client, gestor).get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert _acoes(exibido(html, rigoroso=True)) == _esperado(status, "autor", inovacao.pk)


def test_detalhe_do_gestor_mantem_o_numero_de_consultas(
    client, gestor, criar_inovacao, django_assert_num_queries
):
    """GEST-48: decidir as acoes do gestor nao custa consulta extra."""
    inovacao = criar_inovacao()
    _entrar(client, gestor)
    with django_assert_num_queries(CONSULTAS_DO_DETALHE):
        assert client.get(f"/inovacoes/{inovacao.pk}/").status_code == 200


# --- GEST-50: o gestor conclui as acoes ---------------------------------------------


def test_gestor_edita_a_inovacao_de_outro_autor(client, gestor, autor, criar_inovacao, unidade):
    """GEST-50: a edicao grava e volta ao detalhe, com o autor original."""
    inovacao = criar_inovacao()
    dados = {
        "titulo": "Conciliação de caixa diária",
        "unidade": str(unidade.pk),
        "categoria": str(inovacao.categoria_id),
        "problema": "Diferenças de caixa descobertas só no fim do mês.",
        "solucao": "Conferência diária com planilha compartilhada.",
        "resultado": "",
        "contato": "Setor Financeiro (fin@x.com)",
    }
    resposta = _entrar(client, gestor).post(f"/inovacoes/{inovacao.pk}/editar/", dados)
    assertRedirects(resposta, f"/inovacoes/{inovacao.pk}/", fetch_redirect_response=False)
    gravada = Inovacao.objects.get(pk=inovacao.pk)
    assert (gravada.titulo, gravada.contato, gravada.autor_id) == (
        "Conciliação de caixa diária",
        "Setor Financeiro (fin@x.com)",
        autor.pk,
    )


def test_gestor_exclui_com_confirmacao(client, gestor, criar_inovacao):
    """GEST-50: a confirmacao abre e o envio dela apaga."""
    inovacao = criar_inovacao()
    logado = _entrar(client, gestor)
    confirmacao = logado.get(f"/inovacoes/{inovacao.pk}/excluir/")
    assert confirmacao.status_code == 200
    assertTemplateUsed(confirmacao, "inovacoes/inovacao_confirm_delete.html")
    resposta = logado.post(f"/inovacoes/{inovacao.pk}/excluir/")
    assertRedirects(resposta, "/inovacoes/", fetch_redirect_response=False)
    assert not Inovacao.objects.filter(pk=inovacao.pk).exists()


def test_gestor_avanca_o_status(client, gestor, criar_inovacao):
    """GEST-50: o avanco grava o status e o registro em nome do gestor."""
    inovacao = criar_inovacao()
    resposta = _entrar(client, gestor).post(
        f"/inovacoes/{inovacao.pk}/status/", {"status_visto": EM_TESTE}
    )
    assertRedirects(resposta, f"/inovacoes/{inovacao.pk}/", fetch_redirect_response=False)
    assert Inovacao.objects.get(pk=inovacao.pk).status == VALIDADA
    registro = MudancaDeStatus.objects.get()
    assert (registro.status_anterior, registro.status_novo, registro.responsavel) == (
        EM_TESTE,
        VALIDADA,
        gestor,
    )


# --- GEST-51: gestor de outra unidade -----------------------------------------------


@pytest.mark.parametrize("acao", ["editar", "excluir", "status"])
@pytest.mark.parametrize("metodo", ["get", "post"])
def test_gestor_de_outra_unidade_recebe_403_e_nada_muda(
    client, gestor_de_outra_unidade, criar_inovacao, acao, metodo
):
    """GEST-51: 403 com a pagina propria da AD-009, sem gravar."""
    inovacao = criar_inovacao()
    antes = Inovacao.objects.values().get(pk=inovacao.pk)
    logado = _entrar(client, gestor_de_outra_unidade)
    caminho = f"/inovacoes/{inovacao.pk}/{acao}/"
    if metodo == "get":
        resposta = logado.get(caminho)
    else:
        resposta = logado.post(caminho, {"status_visto": EM_TESTE, "titulo": "Outro"})
    assert resposta.status_code == 403
    assertTemplateUsed(resposta, "inovacoes/acesso_negado.html")
    assert NEGADO in resposta.content.decode()
    assert Inovacao.objects.values().get(pk=inovacao.pk) == antes
    assert MudancaDeStatus.objects.count() == 0


# --- GEST-53 e GEST-54: vale o perfil e a unidade atuais ----------------------------


def test_troca_de_unidade_vale_na_requisicao_seguinte(
    client, gestor, criar_inovacao, gestor_de_outra_unidade
):
    """GEST-53: movido para a Sede, o gestor perde a inovacao da unidade antiga
    e ganha a da Sede."""
    da_unidade_antiga = criar_inovacao()
    da_sede = criar_inovacao(titulo="Outra", unidade=gestor_de_outra_unidade.unidade)
    logado = _entrar(client, gestor)
    assert logado.get(f"/inovacoes/{da_unidade_antiga.pk}/editar/").status_code == 200
    assert logado.get(f"/inovacoes/{da_sede.pk}/editar/").status_code == 403

    Usuario.objects.filter(pk=gestor.pk).update(unidade=gestor_de_outra_unidade.unidade)

    assert logado.get(f"/inovacoes/{da_unidade_antiga.pk}/editar/").status_code == 403
    assert logado.get(f"/inovacoes/{da_sede.pk}/editar/").status_code == 200


def test_perda_do_perfil_de_gestor_vale_na_requisicao_seguinte(client, gestor, criar_inovacao):
    """GEST-54: rebaixado a USUARIO, o gestor perde a curadoria."""
    inovacao = criar_inovacao()
    logado = _entrar(client, gestor)
    assert logado.get(f"/inovacoes/{inovacao.pk}/editar/").status_code == 200

    Usuario.objects.filter(pk=gestor.pk).update(perfil=Usuario.Perfil.USUARIO)

    resposta = logado.post(f"/inovacoes/{inovacao.pk}/excluir/")
    assert resposta.status_code == 403
    assertTemplateUsed(resposta, "inovacoes/acesso_negado.html")
    assert Inovacao.objects.filter(pk=inovacao.pk).exists()
