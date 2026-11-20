"""Testes e2e da paginacao numerada da lista (R2, RCON-21 a RCON-24)."""

import html as html_lib
import re
from urllib.parse import parse_qs, urlsplit

import pytest

from inovacoes.models import Categoria, Inovacao, StatusInovacao, Unidade
from inovacoes.tests.test_folha_v2 import (
    PARES_APROVADOS_DE_COMPONENTE,
    _contraste,
    _pares_da_regra,
    _regras_de,
    _token,
    _token_alto,
)
from inovacoes.tests.test_views_sistema_design import PARES_DE_TEXTO
from inovacoes.tests.visibilidade import CLASSES_OCULTAS, exibido

LISTA = "/inovacoes/"


@pytest.fixture
def logado(client, autor):
    client.force_login(autor)
    return client


@pytest.fixture
def vinte_e_cinco_paginas(autor, unidade, categoria):
    """481 inovacoes: 25 paginas de 20 (a ultima com 1). Sem busca, o texto_busca nao conta."""
    Inovacao.objects.bulk_create(
        Inovacao(
            titulo=f"I{numero:03d}",
            unidade=unidade,
            categoria=categoria,
            problema="Problema.",
            solucao="Solucao.",
            contato="Contato.",
            autor=autor,
        )
        for numero in range(481)
    )


def _nav(html):
    achado = re.search(r'<nav aria-label="Paginação">(.*?)</nav>', html, re.S)
    assert achado, 'sem o nav aria-label="Paginação"'
    return achado.group(1)


def _itens(html):
    """Cada li do nav exibido como (tipo, texto): link, atual, desabilitado ou texto."""
    itens = []
    for li in re.findall(r"<li>(.*?)</li>", _nav(exibido(html, rigoroso=True)), re.S):
        texto = " ".join(re.sub(r"<[^>]+>", "", li).split())
        if re.match(r"\s*<a href=", li):
            tipo = "link"
        elif 'aria-current="page"' in li:
            tipo = "atual"
        elif 'aria-disabled="true"' in li:
            tipo = "desabilitado"
        else:
            tipo = "texto"
        itens.append((tipo, texto))
    return itens


def _janela(itens):
    return " ".join(texto for _, texto in itens)


def test_janela_na_primeira_pagina(logado, vinte_e_cinco_paginas):
    """RCON-21, RCON-22, RCON-23: Anterior desabilitado, 1 2 3 … 25, Próxima link."""
    itens = _itens(logado.get(LISTA).content.decode())
    assert _janela(itens) == "Anterior 1 2 3 … 25 Próxima"
    assert itens == [
        ("desabilitado", "Anterior"),
        ("atual", "1"),
        ("link", "2"),
        ("link", "3"),
        ("texto", "…"),
        ("link", "25"),
        ("link", "Próxima"),
    ]


def test_janela_na_pagina_5(logado, vinte_e_cinco_paginas):
    """RCON-22: 1 … 3 4 5 6 7 … 25, com a 5 atual e um "…" por salto."""
    itens = _itens(logado.get(f"{LISTA}?page=5").content.decode())
    assert _janela(itens) == "Anterior 1 … 3 4 5 6 7 … 25 Próxima"
    assert [t for t, texto in itens if texto == "…"] == ["texto", "texto"]
    assert [texto for tipo, texto in itens if tipo == "atual"] == ["5"]
    assert itens[0] == ("link", "Anterior")


def test_janela_na_ultima_pagina(logado, vinte_e_cinco_paginas):
    """RCON-22, RCON-23: 1 … 23 24 25, Próxima desabilitado."""
    itens = _itens(logado.get(f"{LISTA}?page=25").content.decode())
    assert _janela(itens) == "Anterior 1 … 23 24 25 Próxima"
    assert itens[-1] == ("desabilitado", "Próxima")
    assert [texto for tipo, texto in itens if tipo == "atual"] == ["25"]


def test_pagina_alem_do_fim_marca_a_pagina_mostrada(logado, vinte_e_cinco_paginas):
    """Edge case (CONS-05): a paginacao marca a pagina de fato mostrada."""
    html = logado.get(f"{LISTA}?page=99").content.decode()
    itens = _itens(html)
    assert [texto for tipo, texto in itens if tipo == "atual"] == ["25"]
    assert "Página 25 de 25" in _nav(html)


def test_atual_e_pontas_sao_texto_sem_link_e_sem_role(logado, vinte_e_cinco_paginas):
    """RCON-22, RCON-23 (CONS-41): span com aria-current/aria-disabled, sem role nem tabindex."""
    nav = _nav(logado.get(LISTA).content.decode())
    assert re.search(r'<span aria-current="page">1</span>', nav)
    assert re.search(r'<span aria-disabled="true">Anterior</span>', nav)
    assert not re.search(r"<a\b[^>]*>\s*1\s*</a>", nav)
    assert "role=" not in nav
    assert "tabindex" not in nav
    assert all(re.search(r'\shref="', a) for a in re.findall(r"<a\b[^>]*>", nav))


def test_pagina_x_de_y_vem_depois_dos_numeros(logado, vinte_e_cinco_paginas):
    """RCON-21: "Página {atual} de {total}" abaixo da lista de paginas."""
    nav = _nav(exibido(logado.get(f"{LISTA}?page=5").content.decode(), rigoroso=True))
    assert nav.index("</ul>") < nav.index("Página 5 de 25")


def test_links_mantem_busca_filtros_e_exibicao(logado, criar_inovacao):
    """RCON-24: todo link de pagina mantem q, categoria, unidade, status e exibicao."""
    financeiro = Categoria.objects.get(nome="Financeiro")
    sede = Unidade.objects.get(nome="Sede")
    for numero in range(45):
        criar_inovacao(
            titulo=f"Planilha {numero:02d}",
            categoria=financeiro,
            unidade=sede,
            status=StatusInovacao.VALIDADA,
        )
    parametros = {
        "q": "planilha",
        "categoria": str(financeiro.pk),
        "unidade": str(sede.pk),
        "status": "VALIDADA",
        "exibicao": "tabela",
    }
    html = logado.get(LISTA, {**parametros, "page": "2"}).content.decode()
    hrefs = re.findall(r'<a href="([^"]*)">\s*([^<]*?)\s*</a>', _nav(html))
    assert [texto for _, texto in hrefs] == ["Anterior", "1", "3", "Próxima"]
    esperado_por_texto = {"Anterior": "1", "1": "1", "3": "3", "Próxima": "3"}
    for href, texto in hrefs:
        consulta = parse_qs(urlsplit(html_lib.unescape(href)).query)
        assert consulta == {
            **{k: [v] for k, v in parametros.items()},
            "page": [esperado_por_texto[texto]],
        }


def test_uma_pagina_so_nao_tem_paginacao(logado, criar_inovacao):
    """RCON-21: so com mais de uma pagina."""
    criar_inovacao()
    html = logado.get(LISTA).content.decode()
    assert 'aria-label="Paginação"' not in html
    assert 'class="paginacao"' not in html


def test_folha_nao_esconde_a_paginacao():
    """RCON-21 (L-044): a paginacao nao some por regra da folha."""
    assert "paginacao" not in CLASSES_OCULTAS


@pytest.mark.unit
def test_cores_da_paginacao_estao_no_ds08_nos_dois_temas():
    """RCON-48: atual navy com texto sobre a marca; pontas em texto secundario; links azuis."""
    aprovados = set(PARES_DE_TEXTO)
    conferidos = 0
    for seletores, corpo in _regras_de(".paginacao"):
        for cor, fundo, e_texto in _pares_da_regra(corpo, "bg"):
            minimo = 4.5 if e_texto else 3
            permitidos = aprovados if e_texto else aprovados | PARES_APROVADOS_DE_COMPONENTE
            assert (cor, fundo) in permitidos, (seletores, cor, fundo)
            assert _contraste(_token(cor), _token(fundo)) >= minimo
            assert _contraste(_token_alto(cor), _token_alto(fundo)) >= minimo
            conferidos += 1
    assert conferidos >= 4


@pytest.mark.parametrize("pagina", ["0", "-3", "abc"])
def test_pagina_invalida_marca_a_primeira_pagina(logado, vinte_e_cinco_paginas, pagina):
    """Edge case (CONS-05, RCON-22): page invalida mostra e marca a pagina 1."""
    html = logado.get(f"{LISTA}?page={pagina}").content.decode()
    itens = _itens(html)
    assert [texto for tipo, texto in itens if tipo == "atual"] == ["1"]
    assert itens[0] == ("desabilitado", "Anterior")
    assert "Página 1 de 25" in _nav(html)
