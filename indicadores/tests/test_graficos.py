"""Testes unitarios da geometria das barras (REAP-35, REAP-36), sem banco."""

from types import SimpleNamespace

import pytest

from indicadores.graficos import Barra, Grafico, barras


def _itens(*pares):
    return [SimpleNamespace(nome=nome, total=total) for nome, total in pares]


@pytest.mark.unit
def test_o_maior_valor_ocupa_a_area_toda():
    """REAP-35: o maior valor enche 100% da largura do grafico (480)."""
    resultado = barras(_itens(("A", 2), ("B", 7), ("C", 3)), "total")
    assert resultado[1].comprimento == 480


@pytest.mark.unit
def test_os_outros_valores_sao_proporcionais_ao_maior_com_duas_casas():
    """REAP-35: comprimento = valor / maior x 480, arredondado em 2 casas."""
    resultado = barras(_itens(("A", 3), ("B", 1), ("C", 2), ("D", 7)), "total")
    assert [b.comprimento for b in resultado[:3]] == [205.71, 68.57, 137.14]
    assert barras(_itens(("A", 3), ("B", 1)), "total")[1].comprimento == 160.0


@pytest.mark.unit
def test_valor_zero_nao_tem_barra_e_o_numero_fica_no_inicio():
    """REAP-35, REAP-36: 0 sem barra; o valor ainda tem posicao para o texto."""
    zero = barras(_itens(("A", 5), ("B", 0)), "total")[1]
    assert zero.comprimento == 0
    assert zero.x_valor == 8
    assert zero.valor == 0


@pytest.mark.unit
def test_todos_zero_nao_desenha_barra_nem_divide_por_zero():
    """REAP-35: com todos os valores em 0, nenhuma barra."""
    resultado = barras(_itens(("A", 0), ("B", 0)), "total")
    assert [b.comprimento for b in resultado] == [0, 0]
    assert [b.x_valor for b in resultado] == [8, 8]


@pytest.mark.unit
def test_lista_vazia_nao_tem_barras():
    assert barras([], "total") == []


@pytest.mark.unit
def test_linhas_descem_44_e_o_valor_fica_8_depois_da_barra():
    """REAP-36: nome e valor de cada linha; o valor logo depois da barra."""
    resultado = barras(_itens(("A", 4), ("B", 2), ("C", 1)), "total")
    assert [b.y for b in resultado] == [0, 44, 88]
    assert [b.x_valor for b in resultado] == [488, 248, 128]


@pytest.mark.unit
def test_ordem_de_entrada_nome_e_valor_sao_preservados():
    """REAP-34: as barras seguem a ordem das linhas da tabela, que e a da consulta."""
    resultado = barras(_itens(("Zeta", 1), ("Alfa", 9), ("Meio", 0)), "total")
    assert [(b.nome, b.valor) for b in resultado] == [("Zeta", 1), ("Alfa", 9), ("Meio", 0)]


@pytest.mark.unit
def test_le_o_atributo_pedido():
    itens = [SimpleNamespace(nome="Sede", origem=2, feitos=4)]
    assert barras(itens, "feitos")[0] == Barra("Sede", 4, 0, 480, 488)


@pytest.mark.unit
@pytest.mark.parametrize("linhas", [0, 1, 6])
def test_altura_do_grafico_e_44_por_linha(linhas):
    lista = barras(_itens(*[(str(i), i) for i in range(linhas)]), "total")
    grafico = Grafico.de("grafico-x", "Titulo", lista)
    assert grafico == Grafico("grafico-x", "Titulo", lista, linhas * 44)
