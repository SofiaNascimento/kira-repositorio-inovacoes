"""Testes e2e de desempenho da listagem com o conjunto de demonstracao (RNF08).

Mede o tempo de resposta do servidor no ambiente local: so o client.get, sem a
carga, sem rede e sem navegador (CONS-46, CONS-47). O numero de consultas por
pagina nao depende do numero de linhas (CONS-48).
"""

import re
import time
from io import StringIO

import pytest
from django.core.management import call_command
from django.db import connection
from django.test.utils import CaptureQueriesContext

from inovacoes.busca import normalizar
from inovacoes.management.commands.carregar_demonstracao import VOCABULARIO
from inovacoes.models import Categoria, Inovacao, StatusInovacao, Unidade
from inovacoes.tests.test_views_lista import LISTA, _linhas

LIMITE_EM_SEGUNDOS = 2.0


@pytest.fixture
def logado(client, autor):
    client.force_login(autor)
    return client


@pytest.fixture
def demonstracao(db):
    """500 inovacoes carregadas pelo comando; a carga fica fora da medicao."""
    call_command("carregar_demonstracao", stdout=StringIO())


def _medir(client, parametros=None):
    inicio = time.perf_counter()
    resposta = client.get(LISTA, parametros)
    return resposta, time.perf_counter() - inicio


def test_listagem_com_500_inovacoes_responde_em_menos_de_2_segundos(logado, demonstracao):
    """CONS-46."""
    resposta, segundos = _medir(logado)
    assert resposta.status_code == 200
    assert "500 inovações encontradas" in resposta.content.decode()
    assert segundos < LIMITE_EM_SEGUNDOS


def test_busca_de_duas_palavras_com_tres_filtros_responde_em_menos_de_2_segundos(
    logado, demonstracao
):
    """CONS-47: duas palavras do vocabulario + categoria + unidade + status."""
    # A distribuicao da carga (CONS-44): i % 5 escolhe a unidade, (i // 5) % 5 a
    # categoria e i % 3 o status. Todo trio cuja conta fecha tem resultado.
    unidades = list(Unidade.objects.all())
    categorias = list(Categoria.objects.all())
    unidade, categoria, status = unidades[2], categorias[1], StatusInovacao.values[1]
    numeros = [i for i in range(1, 501) if i % 5 == 2 and (i // 5) % 5 == 1 and i % 3 == 1]
    assert numeros, "o trio escolhido precisa ter ao menos uma inovacao na carga"
    # Duas palavras do vocabulario que a primeira inovacao do trio contem.
    alvo = Inovacao.objects.get(titulo=f"Demonstração {numeros[0]:03d}")
    texto = normalizar(f"{alvo.problema} {alvo.solucao}")
    palavras = [p for p in VOCABULARIO if " " not in p and normalizar(p) in texto][:2]
    assert len(palavras) == 2
    # Resultado esperado, sem passar pelo buscar() nem pelo filtrar().
    esperados = sorted(
        x.titulo
        for x in Inovacao.objects.filter(unidade=unidade, categoria=categoria, status=status)
        if all(
            normalizar(p) in normalizar(f"{x.titulo} {x.problema} {x.solucao}") for p in palavras
        )
    )
    assert alvo.titulo in esperados

    resposta, segundos = _medir(
        logado,
        {
            "q": " ".join(palavras),
            "categoria": categoria.pk,
            "unidade": unidade.pk,
            "status": status,
        },
    )
    html = resposta.content.decode()
    assert resposta.status_code == 200
    assert segundos < LIMITE_EM_SEGUNDOS
    linhas = _linhas(html)
    assert sorted(linha[0] for linha in linhas) == esperados
    assert {tuple(linha[1:]) for linha in linhas} == {
        (categoria.nome, unidade.nome, StatusInovacao(status).label)
    }
    assert re.search(rf"{len(esperados)} inovaç(ão|ões) encontrada", html)


def test_numero_de_consultas_nao_cresce_com_as_linhas_da_pagina(
    logado, criar_inovacao, categoria, unidade
):
    """CONS-48: 1 inovacao e 20 (de unidades e categorias diferentes) custam o mesmo."""
    criar_inovacao(titulo="Unica")
    logado.get(LISTA)  # aquece sessao e caches, para medir so a pagina
    with CaptureQueriesContext(connection) as com_uma:
        resposta = logado.get(LISTA)
    assert len(_linhas(resposta.content.decode())) == 1

    outras_unidades = Unidade.objects.exclude(pk=unidade.pk)[:4]
    outras_categorias = Categoria.objects.exclude(pk=categoria.pk)[:4]
    for n in range(19):
        criar_inovacao(
            titulo=f"Outra {n:02d}",
            unidade=outras_unidades[n % 4],
            categoria=outras_categorias[n % 4],
        )
    with CaptureQueriesContext(connection) as com_vinte:
        resposta = logado.get(LISTA)
    assert len(_linhas(resposta.content.decode())) == 20
    assert len(com_vinte) == len(com_uma)
