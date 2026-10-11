"""Testes e2e de acessibilidade da edicao, da confirmacao e do acesso negado (RNF09).

EDEX-41 a EDEX-43, lidos do HTML que o navegador recebe.
"""

import re

import pytest

from inovacoes.tests.test_views_acessibilidade import PAPEIS_DE_CONTROLE, Pagina

CAMPOS = ["titulo", "unidade", "categoria", "problema", "solucao", "resultado", "contato"]
OBRIGATORIOS = ["titulo", "unidade", "categoria", "problema", "solucao", "contato"]
CONTROLES_DE_ENTRADA = {"input", "select", "textarea"}
NATIVOS = {"a", "button", "input", "select", "textarea"}
# Pagina -> inicio do <title> e texto do unico h1 (EDEX-43).
TITULOS = {
    "edicao": "Editar inovação",
    "confirmacao": "Excluir inovação",
    "acesso_negado": "Acesso negado",
}


def _analisar(html):
    parser = Pagina()
    parser.feed(html)
    parser.html = html
    return parser


def _controles(pagina):
    return {
        atributos["name"]: atributos
        for tag, atributos, no_form in pagina.elementos
        if no_form and tag in CONTROLES_DE_ENTRADA and atributos.get("type") != "hidden"
    }


@pytest.fixture
def edicao(client, autor, criar_inovacao):
    client.force_login(autor)
    inovacao = criar_inovacao()
    return _analisar(client.get(f"/inovacoes/{inovacao.pk}/editar/").content.decode())


@pytest.fixture
def pagina(request, client, autor, terceiro, criar_inovacao):
    inovacao = criar_inovacao()
    if request.param == "edicao":
        conta, url = autor, f"/inovacoes/{inovacao.pk}/editar/"
    elif request.param == "confirmacao":
        conta, url = autor, f"/inovacoes/{inovacao.pk}/excluir/"
    else:
        conta, url = terceiro, f"/inovacoes/{inovacao.pk}/editar/"
    client.force_login(conta)
    resposta = client.get(url)
    assert resposta.status_code == (403 if request.param == "acesso_negado" else 200)
    parser = _analisar(resposta.content.decode())
    parser.nome = request.param
    return parser


# --- EDEX-41: formulario de edicao ---------------------------------------------


def test_todo_campo_da_edicao_tem_rotulo_ligado_pelo_for(edicao):
    """EDEX-41 (INOV-31)."""
    controles = _controles(edicao)
    assert sorted(controles) == sorted(CAMPOS)
    for nome, atributos in controles.items():
        assert atributos.get("id") == f"id_{nome}", nome
        assert edicao.rotulos.get(atributos["id"], "").strip(), nome


def test_obrigatorios_da_edicao_tem_required_e_o_texto_no_rotulo(edicao):
    """EDEX-41 (INOV-32)."""
    for nome, atributos in _controles(edicao).items():
        rotulo = edicao.rotulos[atributos["id"]]
        if nome in OBRIGATORIOS:
            assert "required" in atributos, nome
            assert "(obrigatório)" in rotulo, nome
        else:
            assert "required" not in atributos, nome
            assert "(obrigatório)" not in rotulo, nome


def test_ajuda_da_edicao_esta_ligada_ao_campo(edicao):
    """EDEX-41 (INOV-41): o texto de ajuda existe e esta no aria-describedby."""
    for nome, atributos in _controles(edicao).items():
        id_ajuda = f"id_{nome}_helptext"
        assert f'id="{id_ajuda}"' in edicao.html, nome
        assert id_ajuda in atributos.get("aria-describedby", "").split(), nome


def test_campo_com_erro_na_edicao_fica_invalido_e_ligado_a_mensagem(
    client, autor, criar_inovacao, unidade, categoria
):
    """EDEX-41 (INOV-33): aria-invalid so no campo com erro e o id da mensagem no
    aria-describedby."""
    inovacao = criar_inovacao()
    client.force_login(autor)
    dados = {
        "titulo": "",
        "unidade": str(unidade.pk),
        "categoria": str(categoria.pk),
        "problema": "Problema.",
        "solucao": "Solucao.",
        "contato": "Ana Souza (ana@x.com)",
    }
    resposta = client.post(f"/inovacoes/{inovacao.pk}/editar/", dados)
    assert resposta.status_code == 200
    controles = _controles(_analisar(resposta.content.decode()))
    assert controles["titulo"].get("aria-invalid") == "true"
    assert "id_titulo_error" in controles["titulo"]["aria-describedby"].split()
    assert "aria-invalid" not in controles["problema"]


# --- EDEX-42 e EDEX-43: as tres paginas ----------------------------------------

PAGINAS = list(TITULOS)


@pytest.mark.parametrize("pagina", PAGINAS, indirect=True)
def test_pagina_so_tem_controles_nativos_sem_tabindex_positivo(pagina):
    """EDEX-42: a ordem do teclado e a do documento; todo interativo e nativo."""
    for tag, atributos, _ in pagina.elementos:
        if atributos.get("role") in PAPEIS_DE_CONTROLE:
            raise AssertionError(f"controle nao nativo: <{tag} role={atributos['role']}>")
        if "onclick" in atributos or "contenteditable" in atributos:
            raise AssertionError(f"controle nao nativo: <{tag}>")
        if tag == "a":
            assert "href" in atributos, "a sem href nao e um link nativo"
        if "tabindex" in atributos:
            assert tag in NATIVOS, f"<{tag} tabindex> torna interativo um elemento nao nativo"
            assert int(atributos["tabindex"]) <= 0, tag
    assert "a" in {tag for tag, _, _ in pagina.elementos}


@pytest.mark.parametrize("pagina", PAGINAS, indirect=True)
def test_pagina_tem_foco_visivel_com_contorno(pagina):
    """EDEX-42: regra :focus-visible com outline na folha de estilo da pagina."""
    css = " ".join(re.findall(r"<style>(.*?)</style>", pagina.html, re.S))
    regra = re.search(r"(^|[\s}]):focus-visible\s*\{([^}]*)\}", css)
    assert regra, "falta a regra :focus-visible"
    assert re.search(r"outline\s*:\s*\d+px\s+solid", regra.group(2))
    assert not re.search(r"outline\s*:\s*(none|0)\b", css)


@pytest.mark.parametrize("pagina", PAGINAS, indirect=True)
def test_pagina_tem_um_unico_h1_e_title_com_o_nome_da_pagina(pagina):
    """EDEX-43."""
    nome = TITULOS[pagina.nome]
    assert re.findall(r"<h1[^>]*>(.*?)</h1>", pagina.html, re.S) == [nome]
    titulo = re.search(r"<title>(.*?)</title>", pagina.html, re.S).group(1).strip()
    assert titulo.startswith(nome)
