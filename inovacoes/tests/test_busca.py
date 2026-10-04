"""Testes unitarios da normalizacao de texto para busca (AD-008)."""

import pytest

from inovacoes.busca import normalizar, palavras, texto_de_busca


@pytest.mark.unit
def test_normalizar_tira_acento_e_caixa():
    """CONS-20: "SOLUÇÃO" e "solucao" ficam iguais."""
    assert normalizar("SOLUÇÃO") == "solucao"


@pytest.mark.unit
@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        ("Conciliação", "conciliacao"),
        ("AÇÃO", "acao"),
        ("pão", "pao"),
        ("Über", "uber"),
        # Mesmo texto em forma decomposta (letra + acento combinante), como o macOS grava.
        ("Solução", "solucao"),
    ],
)
def test_normalizar_ignora_acentos_e_caixa(texto, esperado):
    """CONS-20."""
    assert normalizar(texto) == esperado


@pytest.mark.unit
def test_normalizar_usa_casefold():
    """CONS-20: casefold, e nao lower, iguala "Straße" a "strasse"."""
    assert normalizar("Straße") == "strasse"


@pytest.mark.unit
def test_palavras_separa_por_espaco_sem_palavra_vazia():
    """CONS-19: espacos repetidos e nas pontas nao geram palavra."""
    assert palavras("  Planilha   CAIXA ") == ["planilha", "caixa"]


@pytest.mark.unit
def test_palavras_normaliza_cada_palavra():
    """CONS-20: o termo passa pela mesma normalizacao do texto gravado."""
    assert palavras("Conciliação BANCÁRIA") == ["conciliacao", "bancaria"]


@pytest.mark.unit
@pytest.mark.parametrize("termo", ["", "   "])
def test_palavras_de_termo_em_branco_e_lista_vazia(termo):
    """CONS-21: termo vazio ou so de espacos nao gera filtro."""
    assert palavras(termo) == []


@pytest.mark.unit
def test_texto_de_busca_une_os_tres_campos_normalizados_por_quebra_de_linha():
    """CONS-19: titulo, problema e solucao, nessa ordem, separados por \\n."""
    assert texto_de_busca("Conciliação", "Planilha MANUAL", "Script de conferência") == (
        "conciliacao\nplanilha manual\nscript de conferencia"
    )


@pytest.mark.unit
def test_nenhuma_palavra_contem_o_separador_dos_campos():
    """CONS-19: uma palavra nunca atravessa dois campos de texto_busca."""
    resultado = palavras("caixa\nplanilha\tbanco")
    assert resultado == ["caixa", "planilha", "banco"]
    assert all("\n" not in palavra for palavra in resultado)
