"""Testes e2e da regra de autoria em todas as rotas de alteracao (AD-009, RNF07).

A varredura acha as rotas pelo resolver, como a da AD-006: toda rota nova de
inovacoes com <int:pk> (a troca de status da F5, por exemplo) nasce coberta e
precisa negar o terceiro, salvo a allowlist de leitura.
"""

import pytest
from django.test import Client
from django.urls import URLPattern, URLResolver, get_resolver, reverse

from inovacoes.models import Inovacao

# Unica rota com pk que um terceiro pode abrir: o detalhe e de leitura (CONS-08).
ROTAS_DE_LEITURA = {"inovacoes:detalhe"}


def _rotas_com_pk(padroes, namespace=None):
    """Nome qualificado de toda rota do namespace inovacoes cujo padrao tem <int:pk>."""
    for padrao in padroes:
        if isinstance(padrao, URLResolver):
            yield from _rotas_com_pk(padrao.url_patterns, padrao.namespace or namespace)
        elif (
            isinstance(padrao, URLPattern)
            and namespace == "inovacoes"
            and "<int:pk>" in str(padrao.pattern)
        ):
            yield f"inovacoes:{padrao.name}"


ROTAS_COM_PK = sorted(set(_rotas_com_pk(get_resolver().url_patterns)))
ROTAS_DE_ALTERACAO = [rota for rota in ROTAS_COM_PK if rota not in ROTAS_DE_LEITURA]


def test_varredura_encontra_as_rotas_de_alteracao():
    """Sanidade: uma coleta vazia nao pode passar em silencio."""
    assert "inovacoes:detalhe" in ROTAS_COM_PK
    assert {"inovacoes:editar", "inovacoes:excluir"} <= set(ROTAS_DE_ALTERACAO)


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
    client, terceiro, criar_inovacao, envio_valido, rota, metodo
):
    """EDEX-20, EDEX-22, EDEX-23: USUARIO que nao e o autor, em toda rota de alteracao."""
    inovacao = criar_inovacao()
    antes = Inovacao.objects.values().get(pk=inovacao.pk)
    client.force_login(terceiro)
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
