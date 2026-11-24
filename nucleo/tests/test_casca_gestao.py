"""Item "Minha unidade" do menu e a pagina atual da area do gestor (gestao-por-unidade, T9).

Derivados das ACs GEST-09, GEST-10 e GEST-11 (.specs/features/gestao-por-unidade/spec.md).
O menu e lido do DOM parseado (L-028, L-030).
"""

import re
from pathlib import Path
from types import SimpleNamespace

import pytest
from django.conf import settings

from contas.models import Usuario
from inovacoes.models import Unidade
from nucleo.context_processors import casca
from nucleo.tests.test_casca import (
    ABRE_MENU,
    MENU,
    _formas,
    _formas_do_icone_inicial,
    _menu,
    _menu_da_tela,
    _texto,
)

ICONES = Path(settings.BASE_DIR) / "templates" / "icones"
MENU_DO_GESTOR = [*MENU, ("/minha-unidade/", "Minha unidade")]


@pytest.fixture
def gestor(db):
    return Usuario.objects.create_user(
        username="gil",
        email="gil@x.com",
        perfil=Usuario.Perfil.GESTOR_DE_UNIDADE,
        unidade=Unidade.objects.get(nome="Sede"),
    )


def _itens_do_menu(html):
    cabecalho = html[html.index("<header>") : html.index("</header>")]
    inicio = ABRE_MENU.search(cabecalho).start()
    trecho = cabecalho[inicio : cabecalho.index("</nav>", inicio)]
    return re.findall(r"<a\b[^>]*>(.*?)</a>", trecho, re.S)


# --- GEST-11: a pagina atual pela rota ---


@pytest.mark.unit
def test_lista_da_area_e_a_pagina_atual():
    """GEST-11: "page" no destino exato do item."""
    assert _menu("/minha-unidade/") == ("unidade", "page")


@pytest.mark.unit
@pytest.mark.parametrize("url_name", ["criar_conta", "situacao", "redefinir_senha"])
def test_demais_rotas_da_area_marcam_a_secao(url_name):
    """GEST-11: "true" nas outras rotas do namespace gestao (as da T10 a T12)."""
    requisicao = SimpleNamespace(
        resolver_match=SimpleNamespace(namespace="gestao", url_name=url_name), COOKIES={}
    )
    contexto = casca(requisicao)
    assert (contexto["menu_atual"], contexto["menu_estado"]) == ("unidade", "true")


# --- GEST-09, GEST-11: o item exibido ao gestor ---


@pytest.mark.parametrize(
    ("pagina", "atual"),
    [
        ("/minha-unidade/", {"Minha unidade": "page"}),
        ("/inovacoes/", {"Inovações": "page"}),
    ],
)
def test_gestor_ve_minha_unidade_depois_de_indicadores(client, gestor, pagina, atual):
    """GEST-09, GEST-11: quatro itens, o novo por ultimo, com aria-current so na pagina."""
    client.force_login(gestor)
    resposta = client.get(pagina)
    assert resposta.status_code == 200
    itens = _menu_da_tela(resposta.content.decode())
    assert [(href, texto) for href, _, texto in itens] == MENU_DO_GESTOR
    assert {texto: corrente for _, corrente, texto in itens if corrente} == atual


def test_item_minha_unidade_tem_o_icone_de_usuarios_antes_do_texto(client, gestor):
    """GEST-09: SVG decorativo (usuarios.svg) e depois o texto."""
    client.force_login(gestor)
    conteudo = _itens_do_menu(client.get("/minha-unidade/").content.decode())[-1]
    svg = re.match(r'\s*<svg aria-hidden="true" focusable="false"[^>]*>.*?</svg>', conteudo, re.S)
    assert svg
    assert _texto(conteudo[svg.end() :]) == "Minha unidade"
    assert _formas_do_icone_inicial(conteudo) == _formas((ICONES / "usuarios.svg").read_text())


# --- GEST-10: quem nao e gestor nao tem o item ---


@pytest.mark.parametrize(
    "campos",
    [
        {},
        {"is_staff": True},
        {"is_superuser": True},
        {"perfil": Usuario.Perfil.ADMINISTRADOR},
        {"perfil": Usuario.Perfil.ADMINISTRADOR, "is_superuser": True, "is_staff": True},
    ],
    ids=["usuario", "usuario_staff", "usuario_superusuario", "administrador", "superusuario"],
)
def test_quem_nao_e_gestor_nao_tem_o_item_nem_o_href(client, db, campos):
    """GEST-10: nem exibido nem no HTML, para todo papel que nao e gestor (L-003)."""
    conta = Usuario.objects.create_user(
        username="outra", email="outra@x.com", unidade=Unidade.objects.get(nome="Sede"), **campos
    )
    client.force_login(conta)
    html = client.get("/inovacoes/").content.decode()
    assert [(href, texto) for href, _, texto in _menu_da_tela(html)] == MENU
    assert "/minha-unidade/" not in html
    assert "Minha unidade" not in html
