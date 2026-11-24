"""Texto de permissao da Ajuda com o gestor (gestao-por-unidade, T4, GEST-52)."""

import pytest

from nucleo.tests.test_paginas_apoio import AUTENTICADO, _pagina, _secoes

pytestmark = pytest.mark.django_db

QUEM_PODE_AVANCAR = (
    "Só quem cadastrou a inovação, um gestor da unidade de origem ou um administrador "
    "pode avançar o status."
)


@AUTENTICADO
def test_ajuda_exibe_quem_pode_avancar_com_o_gestor(client, autor, autenticado):
    """GEST-52: a secao "Avançar o status" exibe o texto novo, e o antigo saiu."""
    secoes = dict(_secoes(_pagina(client, autor, autenticado, "/ajuda/")))
    assert QUEM_PODE_AVANCAR in secoes["Avançar o status"]
    assert "inovação ou um administrador" not in secoes["Avançar o status"]
