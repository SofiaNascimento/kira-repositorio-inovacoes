"""Testes da carga inicial das listas controladas (INOV-18).

O pytest-django aplica as migrations ao criar o banco de teste, entao a carga
existe em todo teste, exatamente como num banco novo.
"""

from importlib import import_module

import pytest
from django.apps import apps

from inovacoes.models import Categoria, Unidade

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
