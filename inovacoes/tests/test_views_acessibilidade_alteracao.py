"""Testes e2e de acessibilidade da edicao, da confirmacao e do acesso negado (RNF09).

EDEX-41 a EDEX-43, lidos do HTML que o navegador recebe.
"""

import re

import pytest

from inovacoes.models import MudancaDeStatus, StatusInovacao
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


# --- STAT-34 e STAT-37: ciclo de vida, historico e "Avancar status" (F5) ------

# Pagina da F5 -> (status da inovacao, caminho relativo ao detalhe).
PAGINAS_DO_CICLO = {
    "avancar": (StatusInovacao.EM_TESTE, "status/"),
    "ultimo_estagio": (StatusInovacao.DISPONIVEL_PARA_REPLICACAO, "status/"),
    "detalhe": (StatusInovacao.VALIDADA, ""),
}
# Secao do detalhe -> (id do h2, texto do h2, classe da lista).
SECOES_DO_CICLO = {
    "ciclo": ("ciclo-titulo", "Ciclo de vida", "ciclo"),
    "historico": ("historico-titulo", "Histórico de status", "historico"),
}


def _secao(html, titulo_id):
    inicio = html.index(f'<section aria-labelledby="{titulo_id}">')
    return html[inicio : html.index("</section>", inicio) + len("</section>")]


def _registrar_validacao(inovacao, responsavel):
    """Um item no historico, para a secao mostrar a lista e nao o texto de vazio."""
    MudancaDeStatus.objects.create(
        inovacao=inovacao,
        status_anterior=StatusInovacao.EM_TESTE,
        status_novo=StatusInovacao.VALIDADA,
        responsavel=responsavel,
    )


@pytest.fixture
def pagina_do_ciclo(request, client, autor, criar_inovacao):
    """Paginas da F5 vistas pelo autor; o detalhe com link de avancar e um registro."""
    status, sufixo = PAGINAS_DO_CICLO[request.param]
    inovacao = criar_inovacao(status=status)
    if request.param == "detalhe":
        _registrar_validacao(inovacao, autor)
    client.force_login(autor)
    resposta = client.get(f"/inovacoes/{inovacao.pk}/{sufixo}")
    assert resposta.status_code == 200
    parser = _analisar(resposta.content.decode())
    parser.nome = request.param
    parser.inovacao = inovacao
    return parser


def _afirma_so_nativos(pagina):
    """O mesmo criterio da EDEX-42: nenhum papel de controle, nenhum tabindex positivo."""
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


@pytest.mark.parametrize("pagina_do_ciclo", ["avancar", "ultimo_estagio"], indirect=True)
def test_avancar_status_so_tem_controles_nativos(pagina_do_ciclo):
    """STAT-34: a confirmacao e um form com button; o estagio final, so um link."""
    _afirma_so_nativos(pagina_do_ciclo)
    html = pagina_do_ciclo.html
    conteudo = _analisar(html[html.index('<main id="conteudo">') : html.index("</main>")])
    botoes = [
        (atributos, no_form) for tag, atributos, no_form in conteudo.elementos if tag == "button"
    ]
    links = [atributos["href"] for tag, atributos, _ in conteudo.elementos if tag == "a"]
    detalhe = f"/inovacoes/{pagina_do_ciclo.inovacao.pk}/"
    if pagina_do_ciclo.nome == "avancar":
        assert [(a.get("type"), no_form) for a, no_form in botoes] == [("submit", True)]
    else:
        assert botoes == []
    assert links == [detalhe]


@pytest.mark.parametrize("secao", list(SECOES_DO_CICLO))
def test_secoes_do_detalhe_sao_nativas_e_rotuladas_pelo_h2(client, autor, criar_inovacao, secao):
    """STAT-34: cada secao e um section rotulado pelo seu h2, com lista ordenada e links."""
    titulo_id, titulo, classe = SECOES_DO_CICLO[secao]
    inovacao = criar_inovacao(status=StatusInovacao.VALIDADA)
    _registrar_validacao(inovacao, autor)
    client.force_login(autor)
    html = client.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    trecho = _secao(html, titulo_id)
    assert re.findall(r"<h2\b([^>]*)>(.*?)</h2>", trecho, re.S) == [(f' id="{titulo_id}"', titulo)]
    parser = _analisar(trecho)
    _afirma_so_nativos(parser)
    listas = [(tag, a.get("class")) for tag, a, _ in parser.elementos if tag in {"ol", "ul"}]
    assert listas == [("ol", classe)]
    links = [a["href"] for tag, a, _ in parser.elementos if tag == "a"]
    if secao == "ciclo":
        assert links == [f"/inovacoes/{inovacao.pk}/status/"]
    else:
        assert links == []


@pytest.mark.parametrize("pagina_do_ciclo", list(PAGINAS_DO_CICLO), indirect=True)
def test_paginas_do_ciclo_tem_foco_visivel_com_contorno(pagina_do_ciclo):
    """STAT-34: o CSS real da pagina contorna o foco de todo link e botao (EDEX-42)."""
    css = " ".join(re.findall(r"<style>(.*?)</style>", pagina_do_ciclo.html, re.S))
    regra = re.search(r"(^|[\s}]):focus-visible\s*\{([^}]*)\}", css)
    assert regra, "falta a regra :focus-visible"
    assert re.search(r"outline\s*:\s*\d+px\s+solid", regra.group(2))
    assert not re.search(r"outline\s*:\s*(none|0)\b", css)


@pytest.mark.parametrize("pagina_do_ciclo", ["avancar", "ultimo_estagio"], indirect=True)
def test_avancar_status_tem_um_unico_h1_e_title(pagina_do_ciclo):
    """STAT-34: h1 "Avançar status" e <title> que comeca por ele.

    Lacuna de precisao da spec: o base.html acrescenta " · Repositório de Inovações"
    ao <title>; vale o precedente da EDEX-43 (o title comeca pelo nome da pagina).
    """
    html = pagina_do_ciclo.html
    assert re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.S) == ["Avançar status"]
    titulo = re.search(r"<title>(.*?)</title>", html, re.S).group(1).strip()
    assert titulo.startswith("Avançar status")


def test_estagio_atual_e_identificavel_sem_css(client, autor, criar_inovacao):
    """STAT-37: sem estilo, o texto da secao ainda diz qual e o estagio atual."""
    inovacao = criar_inovacao(status=StatusInovacao.VALIDADA)
    client.force_login(autor)
    html = client.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    sem_css = re.sub(r"<style>.*?</style>", "", html, flags=re.S)
    trecho = _secao(sem_css, "ciclo-titulo")
    assert "style=" not in trecho
    itens = [
        " ".join(re.sub(r"<[^>]+>", "", item).split())
        for item in re.findall(r"<li\b[^>]*>(.*?)</li>", trecho, re.S)
    ]
    assert itens == ["Em teste", "Validada (status atual)", "Disponível para replicação"]
