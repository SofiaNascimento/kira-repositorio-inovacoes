"""Testes unitarios das funcoes de apresentacao da consulta (R2)."""

import pytest
from django.http import QueryDict

from inovacoes.apresentacao import exibicao, url_da_lista

# --- url_da_lista (RCON-05, RCON-06, RCON-18) ---


@pytest.mark.unit
def test_none_tira_o_parametro_e_mantem_os_outros_na_ordem():
    """RCON-05: a etiqueta tira o proprio parametro e o page; os outros ficam."""
    consulta = QueryDict("q=planilha&categoria=3&status=VALIDADA&page=2&exibicao=tabela")

    href = url_da_lista(consulta, categoria=None, page=None)

    assert href == "/inovacoes/?q=planilha&status=VALIDADA&exibicao=tabela"


@pytest.mark.unit
def test_ultimo_parametro_saindo_da_a_lista_sem_interrogacao():
    """RCON-05: sem parametro sobrando o href e /inovacoes/, sem "?"."""
    assert url_da_lista(QueryDict("categoria=3"), categoria=None, page=None) == "/inovacoes/"


@pytest.mark.unit
def test_consulta_vazia_sem_mudanca_da_a_lista_sem_interrogacao():
    """RCON-06: "Limpar filtros" sem exibicao leva a /inovacoes/."""
    assert url_da_lista(QueryDict("")) == "/inovacoes/"


@pytest.mark.unit
def test_tirar_parametro_ausente_nao_muda_nada():
    """RCON-05: a remocao do page quando nao ha page mantem a query string igual."""
    assert url_da_lista(QueryDict("q=planilha"), page=None) == "/inovacoes/?q=planilha"


@pytest.mark.unit
def test_tabela_acrescenta_exibicao_e_mantem_busca_filtros_e_pagina():
    """RCON-18: "Tabela" e a query string atual com exibicao=tabela."""
    consulta = QueryDict("q=planilha&categoria=3&unidade=4&status=VALIDADA&page=2")

    href = url_da_lista(consulta, exibicao="tabela")

    assert href == (
        "/inovacoes/?q=planilha&categoria=3&unidade=4&status=VALIDADA&page=2&exibicao=tabela"
    )


@pytest.mark.unit
def test_cartoes_tira_exibicao_e_mantem_busca_filtros_e_pagina():
    """RCON-18: "Cartoes" e a query string atual sem exibicao."""
    consulta = QueryDict("q=planilha&categoria=3&unidade=4&status=VALIDADA&page=2&exibicao=x")

    href = url_da_lista(consulta, exibicao=None)

    assert href == "/inovacoes/?q=planilha&categoria=3&unidade=4&status=VALIDADA&page=2"


@pytest.mark.unit
def test_trocar_valor_substitui_o_atual_sem_repetir():
    """RCON-18: exibicao=tabela ja presente nao vira dois parametros."""
    href = url_da_lista(QueryDict("exibicao=cartoes&page=2"), exibicao="tabela")

    assert href == "/inovacoes/?exibicao=tabela&page=2"


@pytest.mark.unit
def test_valores_repetidos_e_acentuados_sao_preservados():
    """RCON-05, RCON-18: o que sobra volta igual ao que veio."""
    consulta = QueryDict("q=solução+rápida&status=EM_TESTE&status=VALIDADA&page=3")

    href = url_da_lista(consulta, page=None)

    assert href == "/inovacoes/?q=solu%C3%A7%C3%A3o+r%C3%A1pida&status=EM_TESTE&status=VALIDADA"
    caminho, query = href.split("?")
    devolvida = QueryDict(query)
    assert devolvida["q"] == "solução rápida"
    assert devolvida.getlist("status") == ["EM_TESTE", "VALIDADA"]


@pytest.mark.unit
def test_nao_altera_a_consulta_recebida():
    """RCON-18: os dois links do alternador saem da mesma consulta sem se contaminar."""
    consulta = QueryDict("q=planilha&exibicao=tabela")

    url_da_lista(consulta, exibicao=None)

    assert url_da_lista(consulta) == "/inovacoes/?q=planilha&exibicao=tabela"


# --- exibicao (RCON-20) ---


@pytest.mark.unit
def test_exibicao_tabela_escolhe_a_tabela():
    """RCON-19: exibicao=tabela mostra a tabela."""
    assert exibicao(QueryDict("exibicao=tabela")) == "tabela"


@pytest.mark.unit
@pytest.mark.parametrize(
    "query", ["", "exibicao=", "exibicao=TABELA", "exibicao=cartoes", "exibicao=x"]
)
def test_qualquer_outro_valor_de_exibicao_da_cartoes(query):
    """RCON-20: ausente, vazio, outra caixa ou valor desconhecido -> cartoes, sem erro."""
    assert exibicao(QueryDict(query)) == "cartoes"
