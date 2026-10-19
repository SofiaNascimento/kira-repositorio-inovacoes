"""Agregacoes do painel por categoria e por unidade (REAP-32, REAP-33).

Integracao: as contagens sao feitas pelo PostgreSQL. As listas iniciais da
migration 0004 (cinco categorias e cinco unidades) estao no banco de teste.
Os reaproveitamentos nascem pelo metodo do modelo (AD-012).
"""

import datetime

import pytest

from inovacoes.models import Categoria, Reaproveitamento, StatusInovacao, Unidade

CATEGORIAS_INICIAIS = ["Atendimento interno", "Compras", "Financeiro", "RH", "TI interno"]
UNIDADES_INICIAIS = ["Filial Leste", "Filial Norte", "Filial Oeste", "Filial Sul", "Sede"]


def _categorias():
    return [(c.nome, c.total) for c in Categoria.objects.com_total_de_inovacoes()]


def _unidades():
    return [
        (u.nome, u.inovacoes_de_origem, u.reaproveitamentos_feitos)
        for u in Unidade.objects.com_indicadores()
    ]


@pytest.fixture
def disponivel(criar_inovacao):
    """Cria inovacoes ja disponiveis, com titulos distintos (unico por unidade)."""
    contador = iter(range(1, 1000))

    def criar(**campos):
        campos.setdefault("status", StatusInovacao.DISPONIVEL_PARA_REPLICACAO)
        return criar_inovacao(titulo=f"Inovacao {next(contador)}", **campos)

    return criar


@pytest.mark.django_db
def test_sem_inovacoes_as_listas_iniciais_aparecem_com_zero():
    """REAP-32, REAP-33: os itens da migration 0004 entram, com zero, em ordem de nome."""
    assert _categorias() == [(nome, 0) for nome in CATEGORIAS_INICIAIS]
    assert _unidades() == [(nome, 0, 0) for nome in UNIDADES_INICIAIS]


@pytest.mark.django_db
def test_categorias_contam_inovacoes_por_total_e_nome_no_empate(disponivel, categoria):
    """REAP-32: uma linha por categoria, inclusive zero; total desc, nome asc."""
    compras = Categoria.objects.get(nome="Compras")
    ti = Categoria.objects.get(nome="TI interno")
    for _ in range(2):
        disponivel(categoria=ti)
        disponivel(categoria=compras)
    disponivel(categoria=categoria, status=StatusInovacao.EM_TESTE)

    assert _categorias() == [
        ("Compras", 2),
        ("TI interno", 2),
        ("Teste Categoria", 1),
        ("Atendimento interno", 0),
        ("Financeiro", 0),
        ("RH", 0),
    ]


@pytest.mark.django_db
def test_categorias_contam_os_tres_status(disponivel):
    """REAP-32: a contagem nao filtra por status."""
    rh = Categoria.objects.get(nome="RH")
    for status in StatusInovacao.values:
        disponivel(categoria=rh, status=status)
    assert _categorias()[0] == ("RH", 3)


@pytest.mark.django_db
def test_unidade_com_origem_e_reaproveitamentos_nao_multiplica_as_contagens(
    disponivel, unidade, autor
):
    """REAP-33: 2 inovacoes de origem e 3 reaproveitamentos feitos dao 2 e 3, nao 6."""
    sede = Unidade.objects.get(nome="Sede")
    disponivel(unidade=sede)
    disponivel(unidade=sede)
    for _ in range(3):
        disponivel(unidade=unidade).registrar_reaproveitamento(unidade=sede, por=autor)

    linhas = {nome: (origem, feitos) for nome, origem, feitos in _unidades()}
    assert linhas["Sede"] == (2, 3)
    assert linhas["Teste Unidade"] == (3, 0)


@pytest.mark.django_db
def test_unidades_por_origem_e_nome_no_empate_com_zeros(disponivel, unidade, autor):
    """REAP-33: uma linha por unidade, inclusive 0 e 0; origem desc, nome asc."""
    sede = Unidade.objects.get(nome="Sede")
    norte = Unidade.objects.get(nome="Filial Norte")
    sul = Unidade.objects.get(nome="Filial Sul")
    leste = Unidade.objects.get(nome="Filial Leste")
    origem_1, origem_2, _ = (disponivel(unidade=unidade) for _ in range(3))
    disponivel(unidade=sede)
    disponivel(unidade=sede)
    disponivel(unidade=sul)
    disponivel(unidade=leste, status=StatusInovacao.EM_TESTE)
    origem_1.registrar_reaproveitamento(unidade=sede, por=autor)
    origem_1.registrar_reaproveitamento(unidade=norte, por=autor)
    origem_2.registrar_reaproveitamento(unidade=norte, por=autor)

    assert _unidades() == [
        ("Teste Unidade", 3, 0),
        ("Sede", 2, 1),
        ("Filial Leste", 1, 0),
        ("Filial Sul", 1, 0),
        ("Filial Norte", 0, 2),
        ("Filial Oeste", 0, 0),
    ]


@pytest.mark.django_db
def test_reaproveitamentos_da_mesma_unidade_em_datas_diferentes(disponivel, unidade, autor):
    """REAP-33: o Meta.ordering por data nao quebra a subconsulta em varias linhas."""
    sede = Unidade.objects.get(nome="Sede")
    for dias in (1, 30):
        registro = disponivel(unidade=unidade).registrar_reaproveitamento(unidade=sede, por=autor)
        Reaproveitamento.objects.filter(pk=registro.pk).update(
            data=datetime.datetime(2026, 1, dias, tzinfo=datetime.UTC)
        )

    linhas = {nome: (origem, feitos) for nome, origem, feitos in _unidades()}
    assert linhas["Sede"] == (0, 2)


@pytest.mark.django_db
def test_cada_agregacao_e_uma_consulta(disponivel, unidade, autor, django_assert_num_queries):
    """REAP-33 e REAP-32 sem N+1: o numero de linhas nao gera consultas extras."""
    sede = Unidade.objects.get(nome="Sede")
    for _ in range(3):
        disponivel(unidade=unidade).registrar_reaproveitamento(unidade=sede, por=autor)

    with django_assert_num_queries(1):
        _categorias()
    with django_assert_num_queries(1):
        _unidades()
