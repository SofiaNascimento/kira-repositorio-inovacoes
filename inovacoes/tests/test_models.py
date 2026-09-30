"""Testes dos modelos da app inovacoes."""

import pytest

from inovacoes.models import Categoria, Unidade

LISTAS = [Unidade, Categoria]


@pytest.mark.django_db
@pytest.mark.parametrize("modelo", LISTAS)
def test_itens_da_lista_saem_em_ordem_alfabetica(modelo):
    """INOV-15: a consulta padrao, que alimenta o select, e alfabetica."""
    for nome in ["Teste Gama", "Teste Alfa", "Teste Beta"]:
        modelo.objects.create(nome=nome)
    nomes = list(modelo.objects.filter(nome__startswith="Teste ").values_list("nome", flat=True))
    assert nomes == ["Teste Alfa", "Teste Beta", "Teste Gama"]
