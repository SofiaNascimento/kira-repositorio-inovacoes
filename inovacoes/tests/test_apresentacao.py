"""Testes unitarios das funcoes de apresentacao da consulta (R2)."""

import pytest
from django.core.paginator import Paginator
from django.http import QueryDict

from inovacoes.apresentacao import Etiqueta, etiquetas, exibicao, paginas, url_da_lista
from inovacoes.models import Categoria, Unidade

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


# --- etiquetas (RCON-04, RCON-05, RCON-07, CONS-21) ---

# Objetos em memoria: a funcao so le o nome, nao consulta o banco.
FINANCEIRO = Categoria(pk=3, nome="Financeiro")
NORTE = Unidade(pk=4, nome="Filial Norte")

TODOS = {"q": "planilha", "categoria": FINANCEIRO, "unidade": NORTE, "status": "VALIDADA"}
CONSULTA_TODOS = "q=planilha&categoria=3&unidade=4&status=VALIDADA&page=2&exibicao=tabela"


@pytest.mark.unit
def test_etiquetas_na_ordem_busca_categoria_unidade_status_com_os_textos_da_spec():
    """RCON-04: ordem e textos exatos."""
    textos = [e.texto for e in etiquetas(TODOS, QueryDict(CONSULTA_TODOS))]

    assert textos == [
        "Busca: “planilha”",
        "Categoria: Financeiro",
        "Unidade: Filial Norte",
        "Status: Validada",
    ]


@pytest.mark.unit
def test_cada_link_tira_o_proprio_parametro_e_o_page_e_mantem_exibicao():
    """RCON-05: o href de cada etiqueta, com exibicao=tabela mantida."""
    hrefs = [e.href for e in etiquetas(TODOS, QueryDict(CONSULTA_TODOS))]

    assert hrefs == [
        "/inovacoes/?categoria=3&unidade=4&status=VALIDADA&exibicao=tabela",
        "/inovacoes/?q=planilha&unidade=4&status=VALIDADA&exibicao=tabela",
        "/inovacoes/?q=planilha&categoria=3&status=VALIDADA&exibicao=tabela",
        "/inovacoes/?q=planilha&categoria=3&unidade=4&exibicao=tabela",
    ]


@pytest.mark.unit
def test_unico_filtro_removido_leva_a_lista_sem_interrogacao():
    """RCON-05: com so a categoria e a pagina, remover a categoria da /inovacoes/."""
    dados = {"q": "", "categoria": FINANCEIRO, "unidade": None, "status": ""}

    resultado = etiquetas(dados, QueryDict("categoria=3&page=2"))

    assert resultado == [Etiqueta("Categoria: Financeiro", "/inovacoes/")]


@pytest.mark.unit
@pytest.mark.parametrize(
    ("dados", "query", "esperada"),
    [
        ({"q": "planilha"}, "q=planilha", Etiqueta("Busca: “planilha”", "/inovacoes/")),
        ({"unidade": NORTE}, "unidade=4", Etiqueta("Unidade: Filial Norte", "/inovacoes/")),
        (
            {"status": "DISPONIVEL_PARA_REPLICACAO"},
            "status=DISPONIVEL_PARA_REPLICACAO",
            Etiqueta("Status: Disponível para replicação", "/inovacoes/"),
        ),
    ],
)
def test_cada_filtro_sozinho_gera_so_a_propria_etiqueta(dados, query, esperada):
    """RCON-04, RCON-05: um filtro valido, uma etiqueta."""
    vazios = {"q": "", "categoria": None, "unidade": None, "status": ""}

    assert etiquetas({**vazios, **dados}, QueryDict(query)) == [esperada]


@pytest.mark.unit
def test_busca_so_com_espacos_nao_gera_etiqueta():
    """CONS-21: q so com espacos nao e filtro."""
    dados = {"q": "   ", "categoria": None, "unidade": None, "status": "VALIDADA"}

    resultado = etiquetas(dados, QueryDict("q=+++&status=VALIDADA"))

    assert [e.texto for e in resultado] == ["Status: Validada"]
    assert resultado[0].href == "/inovacoes/?q=+++"


@pytest.mark.unit
def test_termo_da_busca_aparece_sem_os_espacos_das_pontas():
    """RCON-04: "Busca: “{termo}”" com o termo aparado, como o form o entrega."""
    dados = {"q": "  planilha  ", "categoria": None, "unidade": None, "status": ""}

    assert [e.texto for e in etiquetas(dados, QueryDict("q=planilha"))] == ["Busca: “planilha”"]


@pytest.mark.unit
@pytest.mark.parametrize("query", ["", "exibicao=tabela&page=3"])
def test_sem_filtro_valido_nao_ha_etiqueta(query):
    """RCON-07: sem filtro, lista vazia; exibicao e page nao sao filtros."""
    dados = {"q": "", "categoria": None, "unidade": None, "status": ""}

    assert etiquetas(dados, QueryDict(query)) == []


# --- paginas (RCON-22) ---


def _pagina(total_de_paginas, numero):
    # 20 por pagina, como a lista (paginate_by = 20).
    return Paginator(range(total_de_paginas * 20), 20).page(numero)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("numero", "esperada"),
    [
        (1, [1, 2, 3, "…", 25]),
        (4, [1, 2, 3, 4, 5, 6, "…", 25]),
        (5, [1, "…", 3, 4, 5, 6, 7, "…", 25]),
        (21, [1, "…", 19, 20, 21, 22, 23, "…", 25]),
        (25, [1, "…", 23, 24, 25]),
    ],
)
def test_janela_de_25_paginas(numero, esperada):
    """RCON-22: primeira, ultima e a atual +- 2, com um "…" para cada salto, ate de uma pagina."""
    assert paginas(_pagina(25, numero)) == esperada


@pytest.mark.unit
@pytest.mark.parametrize("numero", [1, 2, 3])
def test_tres_paginas_sem_reticencias(numero):
    """RCON-22: sem salto, sem "…"."""
    assert paginas(_pagina(3, numero)) == [1, 2, 3]


@pytest.mark.unit
def test_uma_pagina_so():
    """RCON-22: a primeira e a ultima sao a mesma, sem repetir."""
    assert paginas(_pagina(1, 1)) == [1]
