"""Testes das data migrations da app inovacoes.

O pytest-django aplica as migrations ao criar o banco de teste, entao a carga
existe em todo teste, exatamente como num banco novo.
"""

from importlib import import_module

import pytest
from django.apps import apps
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

from contas.models import Usuario
from inovacoes.busca import texto_de_busca
from inovacoes.models import Categoria, Inovacao, Unidade

CATEGORIAS = ["Atendimento interno", "Compras", "Financeiro", "RH", "TI interno"]
UNIDADES = ["Filial Leste", "Filial Norte", "Filial Oeste", "Filial Sul", "Sede"]


def _nomes(modelo):
    return list(modelo.objects.values_list("nome", flat=True))


@pytest.mark.django_db
def test_banco_novo_tem_exatamente_as_categorias_iniciais():
    assert _nomes(Categoria) == CATEGORIAS


@pytest.mark.django_db
def test_banco_novo_tem_exatamente_as_unidades_iniciais():
    assert _nomes(Unidade) == UNIDADES


@pytest.mark.django_db
def test_carga_rodada_de_novo_nao_duplica_itens():
    migracao = import_module("inovacoes.migrations.0004_listas_iniciais")
    migracao.criar_listas_iniciais(apps, None)
    assert _nomes(Categoria) == CATEGORIAS
    assert _nomes(Unidade) == UNIDADES


ANTES_DO_PREENCHIMENTO = [("inovacoes", "0005_inovacao_texto_busca")]
PREENCHIMENTO = [("inovacoes", "0006_preenche_texto_busca")]


def _migrar(alvo):
    # Executor novo a cada passo: o grafo e o estado aplicado mudam entre eles.
    executor = MigrationExecutor(connection)
    executor.migrate(alvo)
    return executor


@pytest.fixture
def antes_do_preenchimento(db):
    """Banco em 0005 (coluna existe, vazia); no fim, volta ao estado final."""
    executor = _migrar(ANTES_DO_PREENCHIMENTO)
    try:
        yield executor.loader.project_state(ANTES_DO_PREENCHIMENTO).apps
    finally:
        _migrar(MigrationExecutor(connection).loader.graph.leaf_nodes())


def _criar_pelo_model_historico(apps_historicos, titulo, problema, solucao):
    """Linha gravada como antes da 0006: o model historico nao tem o save() da AD-008."""
    autor = Usuario.objects.get_or_create(username="ana")[0]
    return apps_historicos.get_model("inovacoes", "Inovacao").objects.create(
        titulo=titulo,
        problema=problema,
        solucao=solucao,
        contato="Ana Souza (ana@x.com)",
        unidade_id=Unidade.objects.get(nome="Sede").pk,
        categoria_id=Categoria.objects.get(nome="Financeiro").pk,
        autor_id=autor.pk,
    )


def test_preenchimento_grava_o_texto_de_busca_com_a_regra_atual(antes_do_preenchimento):
    """AD-008, CONS-19, CONS-20: linhas antigas ficam buscaveis sem acento."""
    textos = [
        ("Conciliação Bancária", "Planilha MANUAL", "Script de CONFERÊNCIA"),
        ("Straße da Ação", "Pão de cada dia", "Über rápido"),
    ]
    pks = [_criar_pelo_model_historico(antes_do_preenchimento, *t).pk for t in textos]
    assert list(
        Inovacao.objects.filter(pk__in=pks).order_by("pk").values_list("texto_busca", flat=True)
    ) == ["", ""]

    _migrar(PREENCHIMENTO)

    gravados = Inovacao.objects.filter(pk__in=pks).order_by("pk")
    assert [i.texto_busca for i in gravados] == [texto_de_busca(*t) for t in textos]
    assert gravados[0].texto_busca == "conciliacao bancaria\nplanilha manual\nscript de conferencia"


def test_reverter_o_preenchimento_nao_falha_nem_apaga_dados(antes_do_preenchimento):
    """A volta para 0005 e noop: o texto de busca ja gravado continua la."""
    pk = _criar_pelo_model_historico(antes_do_preenchimento, "Conciliação", "Planilha", "Script").pk
    _migrar(PREENCHIMENTO)

    _migrar(ANTES_DO_PREENCHIMENTO)

    assert Inovacao.objects.get(pk=pk).texto_busca == "conciliacao\nplanilha\nscript"
