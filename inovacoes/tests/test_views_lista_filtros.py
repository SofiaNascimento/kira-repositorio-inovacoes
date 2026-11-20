"""Testes e2e dos filtros ativos e do contexto de apresentacao da lista (R2)."""

import re
from pathlib import Path

import pytest
from django.conf import settings

from inovacoes.apresentacao import Etiqueta
from inovacoes.models import Categoria, StatusInovacao, Unidade
from inovacoes.tests.test_folha_v2 import _em_px
from inovacoes.tests.test_views_sistema_design import _corpos
from inovacoes.tests.visibilidade import CLASSES_OCULTAS, exibido

LISTA = "/inovacoes/"


@pytest.fixture
def logado(client, autor):
    client.force_login(autor)
    return client


@pytest.fixture
def financeiro(db):
    return Categoria.objects.get(nome="Financeiro")


@pytest.fixture
def sede(db):
    return Unidade.objects.get(nome="Sede")


# --- T8: contexto da lista (RCON-04, 06, 08, 18, 20, 22) ---


def test_contexto_com_filtros_validos(logado, financeiro, sede):
    """RCON-04, RCON-05, RCON-06, RCON-18, RCON-20: cada chave com o valor exato."""
    c = financeiro.pk
    u = sede.pk
    contexto = logado.get(f"{LISTA}?q=planilha&categoria={c}&unidade={u}&status=VALIDADA").context

    assert contexto["exibicao"] == "cartoes"
    assert contexto["url_cartoes"] == (
        f"/inovacoes/?q=planilha&categoria={c}&unidade={u}&status=VALIDADA"
    )
    assert contexto["url_tabela"] == (
        f"/inovacoes/?q=planilha&categoria={c}&unidade={u}&status=VALIDADA&exibicao=tabela"
    )
    assert contexto["etiquetas"] == [
        Etiqueta("Busca: “planilha”", f"/inovacoes/?categoria={c}&unidade={u}&status=VALIDADA"),
        Etiqueta("Categoria: Financeiro", f"/inovacoes/?q=planilha&unidade={u}&status=VALIDADA"),
        Etiqueta("Unidade: Sede", f"/inovacoes/?q=planilha&categoria={c}&status=VALIDADA"),
        Etiqueta("Status: Validada", f"/inovacoes/?q=planilha&categoria={c}&unidade={u}"),
    ]
    assert contexto["url_limpar"] == "/inovacoes/"
    assert contexto["paginas"] == [1]


def test_contexto_sem_filtro_nao_tem_etiqueta(logado, criar_inovacao):
    """RCON-07: sem filtro valido, nenhuma etiqueta."""
    criar_inovacao()
    contexto = logado.get(LISTA).context

    assert contexto["etiquetas"] == []
    assert contexto["exibicao"] == "cartoes"
    assert contexto["url_cartoes"] == "/inovacoes/"
    assert contexto["url_tabela"] == "/inovacoes/?exibicao=tabela"
    assert contexto["url_limpar"] == "/inovacoes/"


@pytest.mark.parametrize("parametro", ["categoria=999999", "status=INEXISTENTE", "unidade=abc"])
def test_contexto_com_form_invalido_nao_tem_etiqueta_do_invalido(logado, parametro):
    """RCON-08 (CONS-30): o parametro invalido nao vira etiqueta; Limpar leva a /inovacoes/."""
    resposta = logado.get(f"{LISTA}?{parametro}")

    assert resposta.context["form"].errors
    assert resposta.context["etiquetas"] == []
    assert resposta.context["url_limpar"] == "/inovacoes/"


def test_contexto_com_form_invalido_mantem_so_as_etiquetas_validas(logado, financeiro):
    """RCON-08: so o parametro invalido fica sem etiqueta; o valido continua com a sua."""
    resposta = logado.get(f"{LISTA}?q=planilha&categoria={financeiro.pk}&status=INEXISTENTE")

    assert resposta.context["form"].errors
    assert resposta.context["etiquetas"] == [
        Etiqueta("Busca: “planilha”", f"/inovacoes/?categoria={financeiro.pk}&status=INEXISTENTE"),
        Etiqueta("Categoria: Financeiro", "/inovacoes/?q=planilha&status=INEXISTENTE"),
    ]


def test_contexto_com_exibicao_tabela(logado, criar_inovacao):
    """RCON-06, RCON-18, RCON-19: tabela escolhida; Cartoes tira exibicao; Limpar a mantem."""
    criar_inovacao()
    contexto = logado.get(f"{LISTA}?status=EM_TESTE&exibicao=tabela").context

    assert contexto["exibicao"] == "tabela"
    assert contexto["url_cartoes"] == "/inovacoes/?status=EM_TESTE"
    assert contexto["url_tabela"] == "/inovacoes/?status=EM_TESTE&exibicao=tabela"
    assert contexto["etiquetas"] == [
        Etiqueta("Status: Em teste", "/inovacoes/?exibicao=tabela"),
    ]
    assert contexto["url_limpar"] == "/inovacoes/?exibicao=tabela"


@pytest.mark.parametrize("valor", ["", "TABELA", "cartoes", "x"])
def test_contexto_com_exibicao_desconhecida_fica_em_cartoes(logado, criar_inovacao, valor):
    """RCON-20: qualquer valor que nao seja tabela mostra cartoes, sem erro."""
    criar_inovacao()
    resposta = logado.get(f"{LISTA}?exibicao={valor}")

    assert resposta.status_code == 200
    assert resposta.context["exibicao"] == "cartoes"
    assert resposta.context["url_limpar"] == "/inovacoes/"
    assert not resposta.context["form"].errors


def test_contexto_na_pagina_2(logado, criar_inovacao):
    """RCON-18, RCON-22: os links de exibicao mantem a pagina; a janela marca as paginas."""
    for numero in range(25):
        criar_inovacao(titulo=f"I{numero:02d}", status=StatusInovacao.EM_TESTE)
    contexto = logado.get(f"{LISTA}?status=EM_TESTE&page=2").context

    assert contexto["page_obj"].number == 2
    assert contexto["paginas"] == [1, 2]
    assert contexto["url_cartoes"] == "/inovacoes/?status=EM_TESTE&page=2"
    assert contexto["url_tabela"] == "/inovacoes/?status=EM_TESTE&page=2&exibicao=tabela"
    # RCON-05: a etiqueta tira o page junto com o proprio parametro.
    assert contexto["etiquetas"] == [Etiqueta("Status: Em teste", "/inovacoes/")]


# --- T11: busca em destaque e filtros em linha (RCON-02, RCON-03) ---


def _formulario(html):
    """O HTML do form GET da busca, dentro do role="search"."""
    busca = re.search(r'<div role="search"[^>]*>(.*?)</form>', html, re.S)
    assert busca, 'sem o form dentro do role="search"'
    return busca.group(1) + "</form>"


def test_busca_tem_lupa_campo_ajuda_botao_e_selects_nessa_ordem(logado):
    """RCON-02, RCON-03: lupa -> q -> ajuda -> "Buscar" -> Categoria, Unidade, Status."""
    form = _formulario(logado.get(LISTA).content.decode())
    lupa = (Path(settings.BASE_DIR) / "templates" / "icones" / "lupa.svg").read_text().strip()
    posicoes = [
        form.index(lupa),
        form.index('id="id_q"'),
        form.index('id="id_q_helptext"'),
        form.index('<button type="submit">Buscar</button>'),
        form.index('name="categoria"'),
        form.index('name="unidade"'),
        form.index('name="status"'),
    ]
    assert posicoes == sorted(posicoes)
    # O primeiro controle do form e o campo "Buscar" (name="q").
    primeiro = re.search(r"<(input|select|button|textarea)\b[^>]*>", form).group(0)
    assert 'name="q"' in primeiro
    assert re.search(r'<label for="id_q">Buscar</label>', form)


def test_lupa_e_decorativa(logado):
    """RCON-02: a lupa e um SVG aria-hidden; o form exibido nao a tem."""
    html = logado.get(LISTA).content.decode()
    form = _formulario(html)
    svgs = re.findall(r"<svg\b[^>]*>", form)
    assert len(svgs) == 1
    assert 'aria-hidden="true"' in svgs[0]
    assert "<svg" not in _formulario(exibido(html, rigoroso=True))


@pytest.mark.parametrize(
    ("nome", "rotulo", "vazio", "ajuda"),
    [
        ("categoria", "Categoria", "Todas as categorias", "Área de back office. Ex.: Financeiro"),
        (
            "unidade",
            "Unidade",
            "Todas as unidades",
            "Sede ou filial que criou a solução. Ex.: Filial Norte",
        ),
        (
            "status",
            "Status",
            "Todos os status",
            "Estágio da solução. Ex.: Disponível para replicação",
        ),
    ],
)
def test_cada_select_tem_rotulo_opcao_vazia_e_ajuda_exibidos(logado, nome, rotulo, vazio, ajuda):
    """RCON-03: rotulo, a opcao "Todas/Todos", a ajuda atual; nenhum on* no select."""
    form = _formulario(exibido(logado.get(LISTA).content.decode(), rigoroso=True))
    assert re.search(rf'<label for="id_{nome}">{rotulo}</label>', form)
    select = re.search(rf'<select name="{nome}"[^>]*>(.*?)</select>', form, re.S)
    assert select
    assert re.search(rf'<option value=""[^>]*>{vazio}</option>', select.group(1))
    assert re.search(
        rf'<div class="helptext" id="id_{nome}_helptext">{re.escape(ajuda)}</div>', form
    )
    controle = re.search(rf'<select name="{nome}"[^>]*>', form).group(0)
    assert not re.search(r"\son\w+=", controle)


def test_trocar_um_select_nao_envia_nada(logado):
    """RCON-03: sem script e sem atributo on* em toda a pagina."""
    html = logado.get(LISTA).content.decode()
    assert "<script" not in html
    assert not re.search(r"<[^>]+\son[a-z]+=", html)


def test_campo_de_busca_em_destaque_tem_52px_e_17px():
    """RCON-02 (design): o campo da linha principal tem 52px de altura e texto de 17px."""
    corpo = _corpos(".busca__principal input")
    altura = re.search(r"min-height\s*:\s*(\d*\.?\d+)(px|rem)\s*;", corpo)
    fonte = re.search(r"font-size\s*:\s*(\d*\.?\d+)(px|rem)\s*;", corpo)
    assert altura and fonte
    assert _em_px(*altura.groups()) == 52
    assert _em_px(*fonte.groups()) == 17


def test_filtros_em_linha_viram_uma_coluna_na_tela_estreita():
    """RCON-03, RCON-49: grade de selects com min(); a 320px cabe uma coluna sem rolagem."""
    corpo = _corpos(".busca__filtros")
    assert re.search(r"grid-template-columns\s*:\s*repeat\(auto-fit,\s*minmax\(min\(", corpo)


def test_folha_nao_esconde_a_busca():
    """RCON-02, RCON-03 (L-044): a linha principal e os filtros nao somem pela folha."""
    for classe in ("busca", "busca__principal", "busca__filtros", "campo", "helptext"):
        assert classe not in CLASSES_OCULTAS
