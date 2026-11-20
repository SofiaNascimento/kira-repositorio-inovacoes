"""Testes e2e dos filtros ativos e do contexto de apresentacao da lista (R2)."""

import pytest

from inovacoes.apresentacao import Etiqueta
from inovacoes.models import Categoria, StatusInovacao, Unidade

LISTA = "/inovacoes/"


@pytest.fixture
def logado(client, autor):
    client.force_login(autor)
    return client


@pytest.fixture
def financeiro(db):
    return Categoria.objects.get(nome="Financeiro")


@pytest.fixture
def sede(db):
    return Unidade.objects.get(nome="Sede")


# --- T8: contexto da lista (RCON-04, 06, 08, 18, 20, 22) ---


def test_contexto_com_filtros_validos(logado, financeiro, sede):
    """RCON-04, RCON-05, RCON-06, RCON-18, RCON-20: cada chave com o valor exato."""
    c = financeiro.pk
    u = sede.pk
    contexto = logado.get(f"{LISTA}?q=planilha&categoria={c}&unidade={u}&status=VALIDADA").context

    assert contexto["exibicao"] == "cartoes"
    assert contexto["url_cartoes"] == (
        f"/inovacoes/?q=planilha&categoria={c}&unidade={u}&status=VALIDADA"
    )
    assert contexto["url_tabela"] == (
        f"/inovacoes/?q=planilha&categoria={c}&unidade={u}&status=VALIDADA&exibicao=tabela"
    )
    assert contexto["etiquetas"] == [
        Etiqueta("Busca: “planilha”", f"/inovacoes/?categoria={c}&unidade={u}&status=VALIDADA"),
        Etiqueta("Categoria: Financeiro", f"/inovacoes/?q=planilha&unidade={u}&status=VALIDADA"),
        Etiqueta("Unidade: Sede", f"/inovacoes/?q=planilha&categoria={c}&status=VALIDADA"),
        Etiqueta("Status: Validada", f"/inovacoes/?q=planilha&categoria={c}&unidade={u}"),
    ]
    assert contexto["url_limpar"] == "/inovacoes/"
    assert contexto["paginas"] == [1]


def test_contexto_sem_filtro_nao_tem_etiqueta(logado, criar_inovacao):
    """RCON-07: sem filtro valido, nenhuma etiqueta."""
    criar_inovacao()
    contexto = logado.get(LISTA).context

    assert contexto["etiquetas"] == []
    assert contexto["exibicao"] == "cartoes"
    assert contexto["url_cartoes"] == "/inovacoes/"
    assert contexto["url_tabela"] == "/inovacoes/?exibicao=tabela"
    assert contexto["url_limpar"] == "/inovacoes/"


@pytest.mark.parametrize("parametro", ["categoria=999999", "status=INEXISTENTE", "unidade=abc"])
def test_contexto_com_form_invalido_nao_tem_etiqueta_do_invalido(logado, parametro):
    """RCON-08 (CONS-30): o parametro invalido nao vira etiqueta; Limpar leva a /inovacoes/."""
    resposta = logado.get(f"{LISTA}?{parametro}")

    assert resposta.context["form"].errors
    assert resposta.context["etiquetas"] == []
    assert resposta.context["url_limpar"] == "/inovacoes/"


def test_contexto_com_form_invalido_mantem_so_as_etiquetas_validas(logado, financeiro):
    """RCON-08: so o parametro invalido fica sem etiqueta; o valido continua com a sua."""
    resposta = logado.get(f"{LISTA}?q=planilha&categoria={financeiro.pk}&status=INEXISTENTE")

    assert resposta.context["form"].errors
    assert resposta.context["etiquetas"] == [
        Etiqueta("Busca: “planilha”", f"/inovacoes/?categoria={financeiro.pk}&status=INEXISTENTE"),
        Etiqueta("Categoria: Financeiro", "/inovacoes/?q=planilha&status=INEXISTENTE"),
    ]


def test_contexto_com_exibicao_tabela(logado, criar_inovacao):
    """RCON-06, RCON-18, RCON-19: tabela escolhida; Cartoes tira exibicao; Limpar a mantem."""
    criar_inovacao()
    contexto = logado.get(f"{LISTA}?status=EM_TESTE&exibicao=tabela").context

    assert contexto["exibicao"] == "tabela"
    assert contexto["url_cartoes"] == "/inovacoes/?status=EM_TESTE"
    assert contexto["url_tabela"] == "/inovacoes/?status=EM_TESTE&exibicao=tabela"
    assert contexto["etiquetas"] == [
        Etiqueta("Status: Em teste", "/inovacoes/?exibicao=tabela"),
    ]
    assert contexto["url_limpar"] == "/inovacoes/?exibicao=tabela"


@pytest.mark.parametrize("valor", ["", "TABELA", "cartoes", "x"])
def test_contexto_com_exibicao_desconhecida_fica_em_cartoes(logado, criar_inovacao, valor):
    """RCON-20: qualquer valor que nao seja tabela mostra cartoes, sem erro."""
    criar_inovacao()
    resposta = logado.get(f"{LISTA}?exibicao={valor}")

    assert resposta.status_code == 200
    assert resposta.context["exibicao"] == "cartoes"
    assert resposta.context["url_limpar"] == "/inovacoes/"
    assert not resposta.context["form"].errors


def test_contexto_na_pagina_2(logado, criar_inovacao):
    """RCON-18, RCON-22: os links de exibicao mantem a pagina; a janela marca as paginas."""
    for numero in range(25):
        criar_inovacao(titulo=f"I{numero:02d}", status=StatusInovacao.EM_TESTE)
    contexto = logado.get(f"{LISTA}?status=EM_TESTE&page=2").context

    assert contexto["page_obj"].number == 2
    assert contexto["paginas"] == [1, 2]
    assert contexto["url_cartoes"] == "/inovacoes/?status=EM_TESTE&page=2"
    assert contexto["url_tabela"] == "/inovacoes/?status=EM_TESTE&page=2&exibicao=tabela"
    # RCON-05: a etiqueta tira o page junto com o proprio parametro.
    assert contexto["etiquetas"] == [Etiqueta("Status: Em teste", "/inovacoes/")]
