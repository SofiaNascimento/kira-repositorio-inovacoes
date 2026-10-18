"""Testes e2e da regra de autoria em todas as rotas de alteracao (AD-009, RNF07).

A varredura acha as rotas pelo resolver, como a da AD-006: toda rota nova de
inovacoes que capture parametro (a troca de status da F5, por exemplo) nasce
coberta e precisa negar o terceiro, salvo a allowlist de leitura.
"""

import pytest
from django.test import Client
from django.urls import URLPattern, URLResolver, get_resolver, include, path, re_path, reverse

from inovacoes.models import Inovacao

# Unica rota com pk que um terceiro pode abrir: o detalhe e de leitura (CONS-08).
ROTAS_DE_LEITURA = {"inovacoes:detalhe"}
# REAP-19, AD-012: a sinalizacao nao altera a Inovacao; todo autenticado pode.
# O teste proprio fica em test_views_reaproveitar.py.
ROTAS_SEM_AUTORIA = {"inovacoes:reaproveitar"}


def _rotas_com_pk(padroes, namespace=None):
    """Nome qualificado de toda rota do namespace inovacoes que captura parametro.

    Le os parametros capturados do padrao, nao o texto: uma rota com outro
    conversor entra na varredura, e uma com parametro que nao seja exatamente
    pk faz a coleta falhar, para que alguem decida como cobri-la.
    """
    for padrao in padroes:
        if isinstance(padrao, URLResolver):
            yield from _rotas_com_pk(padrao.url_patterns, padrao.namespace or namespace)
        elif isinstance(padrao, URLPattern) and namespace == "inovacoes":
            regex = padrao.pattern.regex
            parametros = set(getattr(padrao.pattern, "converters", {})) | set(regex.groupindex)
            if not parametros and not regex.groups:
                continue
            if parametros != {"pk"} or regex.groups != 1 or padrao.name is None:
                raise AssertionError(
                    f"Rota de inovacoes {str(padrao.pattern)!r} (name={padrao.name!r}) captura "
                    f"{sorted(parametros)} em {regex.groups} grupo(s): a varredura da AD-009 so "
                    "sabe montar rotas nomeadas com exatamente o parametro pk. Renomeie o "
                    "parametro para pk ou estenda a varredura."
                )
            yield f"inovacoes:{padrao.name}"


ROTAS_COM_PK = sorted(set(_rotas_com_pk(get_resolver().url_patterns)))
ROTAS_DE_ALTERACAO = [
    rota for rota in ROTAS_COM_PK if rota not in ROTAS_DE_LEITURA | ROTAS_SEM_AUTORIA
]


def test_varredura_encontra_as_rotas_de_alteracao():
    """Sanidade: uma coleta vazia nao pode passar em silencio."""
    assert "inovacoes:detalhe" in ROTAS_COM_PK
    assert "inovacoes:reaproveitar" in ROTAS_COM_PK
    assert {"inovacoes:editar", "inovacoes:excluir", "inovacoes:status"} <= set(ROTAS_DE_ALTERACAO)


def _view_qualquer(request, **kwargs):
    raise AssertionError("a coleta nao chama a view")


def _urls_de_inovacoes(*rotas):
    return [path("inovacoes/", include((list(rotas), "inovacoes")))]


@pytest.mark.parametrize(
    "rota",
    [
        path("<int:id>/status/", _view_qualquer, name="status"),
        re_path(r"^(?P<inovacao>[0-9]+)/status/$", _view_qualquer, name="status"),
        re_path(r"^([0-9]+)/status/$", _view_qualquer, name="status"),
        path("<int:pk>/anexos/<int:anexo>/", _view_qualquer, name="anexo"),
        path("<int:pk>/status/", _view_qualquer),
    ],
    ids=["outro-nome", "regex-nomeado", "regex-sem-nome", "dois-parametros", "sem-name"],
)
def test_coleta_falha_com_rota_que_a_varredura_nao_sabe_montar(rota):
    """AD-009: rota de alteracao com parametro que nao e pk nao escapa em silencio."""
    with pytest.raises(AssertionError, match="exatamente o parametro pk"):
        list(_rotas_com_pk(_urls_de_inovacoes(rota)))


def test_coleta_pega_o_pk_com_qualquer_conversor():
    """AD-009: a coleta le o parametro capturado, nao o texto <int:pk>."""
    urls = _urls_de_inovacoes(
        path("", _view_qualquer, name="lista"),
        path("<str:pk>/status/", _view_qualquer, name="status"),
        re_path(r"^(?P<pk>[0-9]+)/arquivo/$", _view_qualquer, name="arquivo"),
    )
    assert sorted(_rotas_com_pk(urls)) == ["inovacoes:arquivo", "inovacoes:status"]


@pytest.fixture
def envio_valido(unidade, categoria):
    """POST que gravaria se a regra falhasse: dados validos e diferentes dos salvos."""
    return {
        "titulo": "Titulo trocado por terceiro",
        "unidade": str(unidade.pk),
        "categoria": str(categoria.pk),
        "problema": "Problema trocado por terceiro.",
        "solucao": "Solucao trocada por terceiro.",
        "resultado": "Resultado trocado por terceiro.",
        "contato": "Bruno (bruno@x.com)",
    }


@pytest.mark.parametrize("metodo", ["get", "post"])
@pytest.mark.parametrize("rota", ROTAS_DE_ALTERACAO)
def test_terceiro_recebe_403_e_nada_muda(
    client, nao_autor_usuario, criar_inovacao, envio_valido, rota, metodo
):
    """EDEX-20, EDEX-22, EDEX-23: USUARIO que nao e o autor, em toda rota de alteracao.

    AD-009: vale tambem para o USUARIO com is_staff ou is_superuser.
    """
    inovacao = criar_inovacao()
    antes = Inovacao.objects.values().get(pk=inovacao.pk)
    client.force_login(nao_autor_usuario)
    caminho = reverse(rota, kwargs={"pk": inovacao.pk})
    if metodo == "post":
        resposta = client.post(caminho, envio_valido)
    else:
        resposta = client.get(caminho)
    assert resposta.status_code == 403
    assert Inovacao.objects.values().get(pk=inovacao.pk) == antes
    assert Inovacao.objects.count() == 1


@pytest.mark.parametrize("acao", ["editar", "excluir"])
def test_post_sem_token_csrf_e_recusado_e_nada_muda(autor, criar_inovacao, envio_valido, acao):
    """EDEX-45: o proprio autor, sem token CSRF, recebe 403 e nada muda nem e apagado."""
    inovacao = criar_inovacao()
    antes = Inovacao.objects.values().get(pk=inovacao.pk)
    cliente = Client(enforce_csrf_checks=True)
    cliente.force_login(autor)
    resposta = cliente.post(f"/inovacoes/{inovacao.pk}/{acao}/", envio_valido)
    assert resposta.status_code == 403
    # O autor pode alterar: a recusa e do CSRF, nao a pagina de acesso negado.
    assert "Você não tem permissão para alterar esta inovação." not in resposta.content.decode()
    assert Inovacao.objects.values().get(pk=inovacao.pk) == antes
