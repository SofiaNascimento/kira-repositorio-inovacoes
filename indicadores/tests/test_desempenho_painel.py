"""Testes e2e de desempenho do painel com o conjunto de demonstracao (RNF08).

Mesmo metodo da CONS-46: so o client.get entra na medicao, sem a carga, sem rede
e sem navegador (REAP-41). O numero de consultas nao cresce com o volume
(REAP-42). Os reaproveitamentos nascem pelo metodo do modelo (AD-012).
"""

import re
import time
from io import StringIO

import pytest
from django.core.management import call_command
from django.db import connection
from django.test.utils import CaptureQueriesContext

from inovacoes.models import Categoria, Inovacao, Reaproveitamento, StatusInovacao, Unidade
from inovacoes.tests.test_desempenho import LIMITE_EM_SEGUNDOS, demonstracao  # noqa: F401

URL = "/indicadores/"
REAPROVEITAMENTOS_DA_CARGA = 200


def _reaproveitar_a_demonstracao(por):
    """200 reaproveitamentos sobre inovacoes "Disponivel" da demonstracao, em unidades != origem."""
    unidades = list(Unidade.objects.order_by("nome"))
    disponiveis = Inovacao.objects.filter(
        autor__username="demo", status=StatusInovacao.DISPONIVEL_PARA_REPLICACAO
    ).order_by("titulo")
    criados = 0
    for inovacao in disponiveis:
        for unidade in unidades:
            if unidade.pk == inovacao.unidade_id:
                continue
            inovacao.registrar_reaproveitamento(unidade=unidade, por=por)
            criados += 1
            if criados == REAPROVEITAMENTOS_DA_CARGA:
                return
    raise AssertionError("a demonstracao nao tem inovacoes disponiveis suficientes")


@pytest.fixture
def demonstracao_com_reaproveitamentos(demonstracao, autor):  # noqa: F811
    """Carga fora da medicao: 500 inovacoes e 200 reaproveitamentos."""
    _reaproveitar_a_demonstracao(autor)


def _card(html, rotulo):
    return re.search(rf"<dt>{rotulo}</dt>\s*<dd>([^<]*)</dd>", html).group(1)


def _medir(client):
    inicio = time.perf_counter()
    resposta = client.get(URL)
    return resposta, time.perf_counter() - inicio


def test_painel_com_a_demonstracao_e_200_reaproveitamentos_responde_em_menos_de_2_segundos(
    client, terceiro, demonstracao_com_reaproveitamentos
):
    """REAP-41."""
    assert Inovacao.objects.count() == 500
    assert Reaproveitamento.objects.count() == REAPROVEITAMENTOS_DA_CARGA
    client.force_login(terceiro)

    resposta, segundos = _medir(client)

    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert _card(html, "Inovações cadastradas") == "500"
    assert _card(html, "Reaproveitamentos registrados") == "200"
    assert segundos < LIMITE_EM_SEGUNDOS


def test_numero_de_consultas_do_painel_nao_cresce_com_o_volume(
    client, terceiro, autor, criar_inovacao
):
    """REAP-42: 1 inovacao e 1 reaproveitamento custam o mesmo que a demonstracao + 200.

    O volume grande tambem ganha uma categoria e uma unidade a mais, para que as
    quatro tabelas da AC cresçam.
    """
    criar_inovacao(status=StatusInovacao.DISPONIVEL_PARA_REPLICACAO).registrar_reaproveitamento(
        unidade=Unidade.objects.get(nome="Sede"), por=autor
    )
    client.force_login(terceiro)
    client.get(URL)  # aquece a sessao, para medir so a pagina
    with CaptureQueriesContext(connection) as pequeno:
        resposta = client.get(URL)
    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert _card(html, "Inovações cadastradas") == "1"
    assert _card(html, "Reaproveitamentos registrados") == "1"

    categorias, unidades = Categoria.objects.count(), Unidade.objects.count()
    call_command("carregar_demonstracao", stdout=StringIO())
    _reaproveitar_a_demonstracao(autor)
    Categoria.objects.create(nome="Categoria extra")
    Unidade.objects.create(nome="Unidade extra")
    assert (Categoria.objects.count(), Unidade.objects.count()) == (categorias + 1, unidades + 1)

    with CaptureQueriesContext(connection) as grande:
        resposta = client.get(URL)
    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert _card(html, "Inovações cadastradas") == "501"
    assert _card(html, "Reaproveitamentos registrados") == "201"
    assert len(grande) == len(pequeno)
