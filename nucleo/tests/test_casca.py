"""Casca do sistema (fundacao-do-redesign, RED-13 a RED-22, RED-29 a RED-31, RED-41).

Fonte: docs/design-spec.md v2 §5 e .specs/features/fundacao-do-redesign/spec.md.
Toda AC de "exibido" usa `exibido(html, rigoroso=True)` sobre a pagina inteira (L-028, L-030).
"""

import pytest
from django.test import RequestFactory
from django.urls import resolve

from nucleo.context_processors import casca

# --- T7: context processor da casca (RED-17, RED-18, RED-26, RED-40, RED-14) ------


def _requisicao(caminho, cookies=None, resolvida=True):
    requisicao = RequestFactory().get(caminho)
    requisicao.COOKIES.update(cookies or {})
    requisicao.resolver_match = resolve(caminho) if resolvida else None
    return requisicao


def _menu(caminho, resolvida=True):
    contexto = casca(_requisicao(caminho, resolvida=resolvida))
    return contexto["menu_atual"], contexto["menu_estado"]


@pytest.mark.unit
@pytest.mark.parametrize(
    ("caminho", "esperado"),
    [
        ("/inovacoes/", ("inovacoes", "page")),
        ("/inovacoes/nova/", ("nova", "page")),
        ("/indicadores/", ("indicadores", "page")),
    ],
)
def test_destino_exato_do_menu_e_a_pagina_atual(caminho, esperado):
    """RED-17: aria-current="page" so no destino exato."""
    assert _menu(caminho) == esperado


@pytest.mark.unit
@pytest.mark.parametrize(
    "caminho",
    [
        "/inovacoes/7/",
        "/inovacoes/7/editar/",
        "/inovacoes/7/excluir/",
        "/inovacoes/7/status/",
        "/inovacoes/7/reaproveitar/",
    ],
)
def test_telas_da_secao_marcam_inovacoes_como_secao(caminho):
    """RED-18: aria-current="true" em Inovacoes nas telas da secao."""
    assert _menu(caminho) == ("inovacoes", "true")


@pytest.mark.unit
def test_rota_fora_do_menu_nao_tem_pagina_atual():
    """RED-17, RED-18: o login nao marca nenhum item."""
    assert _menu("/entrar/") == (None, None)


@pytest.mark.unit
def test_sem_rota_resolvida_nao_tem_pagina_atual():
    """RED-17: a 404 de URL inexistente chega sem resolver_match."""
    assert _menu("/nao-existe/", resolvida=False) == (None, None)


@pytest.mark.unit
def test_cookie_alto_liga_o_alto_contraste():
    """RED-26."""
    requisicao = _requisicao("/inovacoes/", {"kira_contraste": "alto"})
    assert casca(requisicao)["contraste_alto"] is True


@pytest.mark.unit
@pytest.mark.parametrize(
    "cookies", [{}, {"kira_contraste": "ALTO"}, {"kira_contraste": "sim"}, {"kira_contraste": ""}]
)
def test_outro_valor_ou_cookie_ausente_deixa_o_tema_normal(cookies):
    """RED-40: so o valor exato "alto" liga o tema."""
    assert casca(_requisicao("/inovacoes/", cookies))["contraste_alto"] is False


@pytest.mark.unit
@pytest.mark.parametrize(
    ("caminho", "esperado"),
    [
        ("/inovacoes/", "#id_q"),
        ("/inovacoes/7/", "/inovacoes/#id_q"),
        ("/indicadores/", "/inovacoes/#id_q"),
        ("/inovacoes/nova/", "/inovacoes/#id_q"),
    ],
)
def test_atalho_da_busca_aponta_para_o_campo_da_lista(caminho, esperado):
    """RED-14: #id_q na lista, /inovacoes/#id_q nas outras telas."""
    assert casca(_requisicao(caminho))["busca_href"] == esperado
