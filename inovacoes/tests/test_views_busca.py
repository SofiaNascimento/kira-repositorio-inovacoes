"""Testes e2e da busca e dos filtros na listagem (/inovacoes/?q=...&categoria=...)."""

import html as html_lib
import re
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlsplit

import pytest

from inovacoes.models import Categoria, StatusInovacao, Unidade
from inovacoes.tests.test_views_lista import LISTA, _linhas
from inovacoes.tests.visibilidade import exibido


@pytest.fixture
def logado(client, autor):
    client.force_login(autor)
    return client


def _titulos(resposta):
    """Titulos dos resultados, em ordem alfabetica.

    T-A (redesign-consulta, T9, RCON-10): le os cartoes da lista de resultados. Sem a
    lista, so devolve [] quando a pagina exibe o estado vazio (CONS-34, CONS-35); em
    qualquer outro caso falha, em vez de devolver [] sem testar nada.
    """
    assert resposta.status_code == 200
    html = resposta.content.decode()
    if 'aria-label="Resultados"' not in html:
        assert '<div class="vazio">' in exibido(html, rigoroso=True)
        return []
    return sorted(linha[0] for linha in _linhas(html))


@pytest.fixture
def tres(criar_inovacao):
    """Financeiro/Sede/Validada, Financeiro/Filial Norte/Em teste, RH/Sede/Validada."""
    financeiro = Categoria.objects.get(nome="Financeiro")
    rh = Categoria.objects.get(nome="RH")
    sede = Unidade.objects.get(nome="Sede")
    norte = Unidade.objects.get(nome="Filial Norte")
    criar_inovacao(
        titulo="Primeira",
        categoria=financeiro,
        unidade=sede,
        status=StatusInovacao.VALIDADA,
        problema="Conciliacao sem ferramenta.",
    )
    criar_inovacao(
        titulo="Segunda",
        categoria=financeiro,
        unidade=norte,
        status=StatusInovacao.EM_TESTE,
        problema="Relatorio mensal manual.",
    )
    criar_inovacao(
        titulo="Terceira",
        categoria=rh,
        unidade=sede,
        status=StatusInovacao.VALIDADA,
        problema="Admissao em papel.",
    )
    return {"financeiro": financeiro, "rh": rh, "sede": sede, "norte": norte}


def test_busca_por_varias_palavras_sem_acento_e_sem_caixa_lista_so_a_esperada(
    logado, criar_inovacao
):
    """CONS-19, CONS-20: todas as palavras, caixa e acento ignorados."""
    criar_inovacao(titulo="Conciliação bancária", problema="Planilha manual de lançamentos.")
    criar_inovacao(titulo="Só planilha", problema="Apenas uma planilha.")
    criar_inovacao(titulo="Controle de caixa")
    resposta = logado.get(LISTA, {"q": "CONCILIACAO planilha"})
    assert _titulos(resposta) == ["Conciliação bancária"]
    assert "1 inovação encontrada" in resposta.content.decode()


def test_campo_de_busca_mostra_o_termo_enviado(logado, criar_inovacao):
    """CONS-25: o valor volta no controle, com a grafia digitada."""
    criar_inovacao()
    html = logado.get(LISTA, {"q": "CONCILIACAO planilha"}).content.decode()
    entrada = re.search(r'<input[^>]*name="q"[^>]*>', html).group(0)
    assert 'value="CONCILIACAO planilha"' in entrada


@pytest.mark.parametrize(
    ("parametro", "esperado"),
    [
        ("categoria=financeiro", ["Primeira", "Segunda"]),
        ("unidade=sede", ["Primeira", "Terceira"]),
        ("status=VALIDADA", ["Primeira", "Terceira"]),
    ],
)
def test_cada_filtro_isolado_lista_so_os_que_tem_o_valor(logado, tres, parametro, esperado):
    """CONS-27."""
    nome, valor = parametro.split("=")
    if nome != "status":
        valor = tres[valor].pk
    assert _titulos(logado.get(LISTA, {nome: valor})) == esperado


def test_filtros_combinados_listam_so_os_que_satisfazem_todos(logado, tres):
    """CONS-28: dois, tres e tres mais a busca."""
    dois = {"categoria": tres["financeiro"].pk, "unidade": tres["sede"].pk}
    assert _titulos(logado.get(LISTA, dois)) == ["Primeira"]
    tres_filtros = {**dois, "status": "VALIDADA"}
    assert _titulos(logado.get(LISTA, tres_filtros)) == ["Primeira"]
    assert _titulos(logado.get(LISTA, {**tres_filtros, "q": "conciliacao"})) == ["Primeira"]
    assert _titulos(logado.get(LISTA, {**tres_filtros, "q": "admissao"})) == []
    assert _titulos(logado.get(LISTA, {"unidade": tres["sede"].pk, "q": "admissao"})) == [
        "Terceira"
    ]


def _selecionadas(html, nome):
    """Valores das <option selected> do <select name=...>."""
    select = re.search(rf'<select[^>]*name="{nome}"[^>]*>(.*?)</select>', html, re.S).group(1)
    return re.findall(r'<option value="([^"]*)"[^>]*\bselected\b', select)


def test_valores_enviados_continuam_selecionados_nos_controles(logado, tres):
    """CONS-29: categoria, unidade e status."""
    html = logado.get(
        LISTA,
        {"categoria": tres["rh"].pk, "unidade": tres["norte"].pk, "status": "EM_TESTE"},
    ).content.decode()
    assert _selecionadas(html, "categoria") == [str(tres["rh"].pk)]
    assert _selecionadas(html, "unidade") == [str(tres["norte"].pk)]
    assert _selecionadas(html, "status") == ["EM_TESTE"]


class Estrutura(HTMLParser):
    """Forms, botoes e atributos on* da pagina, com o ancestral role=search."""

    def __init__(self):
        super().__init__()
        self.pilha = []
        self.forms = []  # (atributos, dentro de role=search?)
        self.botoes = []  # (atributos, texto, dentro de um form?)
        self.atributos_on = []
        self.scripts = 0
        self._botao = None

    def handle_starttag(self, tag, attrs):
        atributos = dict(attrs)
        self.atributos_on += [(tag, a) for a in atributos if a.startswith("on")]
        if tag == "script":
            self.scripts += 1
        if tag == "form":
            busca = any(a.get("role") == "search" for t, a in self.pilha)
            self.forms.append((atributos, busca))
        if tag == "button":
            self._botao = [atributos, "", any(t == "form" for t, _ in self.pilha)]
        if tag not in {"input", "meta", "link", "br", "img", "hr"}:
            self.pilha.append((tag, atributos))

    def handle_endtag(self, tag):
        if tag == "button" and self._botao:
            self.botoes.append(tuple(self._botao))
            self._botao = None
        for i in range(len(self.pilha) - 1, -1, -1):
            if self.pilha[i][0] == tag:
                del self.pilha[i:]
                break

    def handle_data(self, data):
        if self._botao:
            self._botao[1] += data


@pytest.fixture
def estrutura(logado, criar_inovacao):
    criar_inovacao()
    parser = Estrutura()
    parser.feed(logado.get(LISTA).content.decode())
    return parser


def test_um_unico_formulario_get_com_o_botao_buscar_e_sem_aplicar_ao_mudar(estrutura):
    """CONS-31: um form GET, botao "Buscar", nenhum on* nem script na pagina."""
    gets = [a for a, _ in estrutura.forms if a.get("method") == "get"]
    assert len(gets) == 1
    assert gets[0]["action"] == "/inovacoes/"
    submits = [
        texto.strip()
        for atributos, texto, em_form in estrutura.botoes
        if em_form and atributos.get("type") == "submit"
    ]
    assert "Buscar" in submits
    assert estrutura.atributos_on == []
    assert estrutura.scripts == 0


def test_formulario_de_busca_fica_dentro_de_role_search(estrutura):
    """CONS-37."""
    (busca,) = [dentro for atributos, dentro in estrutura.forms if atributos.get("method") == "get"]
    assert busca is True


def test_quatro_controles_ficam_dentro_do_form_de_busca(logado):
    """CONS-31: busca e os tres filtros viajam juntos, no mesmo form."""
    html = logado.get(LISTA).content.decode()
    form = re.search(r'<form method="get".*?</form>', html, re.S).group(0)
    for nome in ("q", "categoria", "unidade", "status"):
        assert f'name="{nome}"' in form


def test_proxima_e_anterior_carregam_busca_filtros_e_pagina(logado, criar_inovacao):
    """CONS-04: com busca e filtros ativos, os links de pagina os repetem."""
    financeiro = Categoria.objects.get(nome="Financeiro")
    sede = Unidade.objects.get(nome="Sede")
    for n in range(25):
        criar_inovacao(titulo=f"Tarefa {n:02d}", categoria=financeiro, unidade=sede)
    criar_inovacao(titulo="Sem a palavra buscada", categoria=financeiro, unidade=sede)
    for n in range(2):
        criar_inovacao(titulo=f"Tarefa validada {n}", status=StatusInovacao.VALIDADA)
    parametros = {
        "q": "tarefa",
        "categoria": str(financeiro.pk),
        "unidade": str(sede.pk),
        "status": "EM_TESTE",
    }
    html = logado.get(LISTA, parametros).content.decode()
    assert "25 inovações encontradas" in html
    nav = re.search(r'<nav aria-label="Paginação">(.*?)</nav>', html, re.S).group(1)
    proxima = re.search(r'<a href="([^"]*)">\s*Próxima\s*</a>', nav).group(1)
    assert parse_qs(urlsplit(html_lib.unescape(proxima)).query) == {
        **{k: [v] for k, v in parametros.items()},
        "page": ["2"],
    }
    pagina_2 = logado.get(LISTA + html_lib.unescape(proxima))
    assert len(_linhas(pagina_2.content.decode())) == 5
    nav_2 = re.search(r'<nav aria-label="Paginação">(.*?)</nav>', pagina_2.content.decode(), re.S)
    anterior = re.search(r'<a href="([^"]*)">\s*Anterior\s*</a>', nav_2.group(1)).group(1)
    assert parse_qs(urlsplit(html_lib.unescape(anterior)).query) == {
        **{k: [v] for k, v in parametros.items()},
        "page": ["1"],
    }


ALERTA = "Não foi possível buscar. Corrija os campos indicados."
INVALIDOS = [
    (
        {"q": "a" * 100 + "b"},
        "q",
        "Use no máximo 100 caracteres (você digitou 101).",
    ),
    ({"categoria": "999999"}, "categoria", "Selecione uma categoria da lista."),
    ({"unidade": "abc"}, "unidade", "Selecione uma unidade da lista."),
    ({"status": "X"}, "status", "Selecione um status da lista."),
]


@pytest.fixture
def invalida(request, logado, criar_inovacao):
    """Resposta a um parametro invalido, com inovacoes que casariam se ele fosse ignorado."""
    parametros, campo, mensagem = request.param
    # O titulo casa com os 100 primeiros caracteres da busca longa; as demais
    # consultas, se o parametro invalido fosse ignorado, listariam tudo.
    criar_inovacao(titulo="a" * 100)
    criar_inovacao(titulo="Outra")
    resposta = logado.get(LISTA, parametros)
    return resposta, resposta.content.decode(), campo, mensagem


@pytest.mark.parametrize("invalida", INVALIDOS, indirect=True)
def test_parametro_invalido_mostra_200_mensagem_no_campo_alerta_e_nenhuma_linha(invalida):
    """CONS-24, CONS-30."""
    resposta, html, campo, mensagem = invalida
    assert resposta.status_code == 200
    erro = re.search(rf'id="id_{campo}_error"[^>]*>(.*?)</ul>', html, re.S).group(1)
    assert mensagem in erro
    assert re.search(rf'<div role="alert">\s*<p>{re.escape(ALERTA)}</p>\s*</div>', html)
    assert "<table" not in html
    assert "<tbody" not in html


@pytest.mark.parametrize("invalida", INVALIDOS, indirect=True)
def test_parametro_invalido_nao_mostra_contagem_nem_mensagem_de_vazio(invalida):
    """CONS-30: form invalido nao e "nenhuma encontrada" nem "nenhuma cadastrada"."""
    _, html, _, _ = invalida
    conteudo = html[html.index("<h1") :]
    assert "encontrada" not in conteudo
    assert "Nenhuma inovação" not in conteudo


@pytest.mark.parametrize("invalida", INVALIDOS, indirect=True)
def test_controle_com_erro_fica_invalido_e_ligado_a_mensagem(invalida):
    """CONS-43: aria-invalid="true" e o id do erro no aria-describedby."""
    _, html, campo, _ = invalida
    controle = re.search(rf'<[^>]*\bid="id_{campo}"[^>]*>', html).group(0)
    assert 'aria-invalid="true"' in controle
    descrito_por = re.search(r'aria-describedby="([^"]*)"', controle).group(1).split()
    assert f"id_{campo}_error" in descrito_por


def test_consulta_valida_nao_mostra_o_alerta_nem_marca_controle_invalido(logado, criar_inovacao):
    """CONS-30, CONS-43: o alerta so existe com erro."""
    criar_inovacao()
    html = logado.get(LISTA, {"q": "caixa", "status": "EM_TESTE"}).content.decode()
    assert 'role="alert"' not in html
    assert "aria-invalid" not in html


# T-D (redesign-consulta, T14, RCON-26): o texto do vazio com filtro passa a ser o da §10,
# com a sugestao logo depois. A garantia da CONS-35 continua: diz o que houve e oferece limpar.
MENSAGEM_VAZIO_COM_FILTRO = "Nenhuma inovação encontrada para esta busca."
SUGESTAO_VAZIO_COM_FILTRO = "Tente outras palavras ou remova algum filtro."
MENSAGEM_REPOSITORIO_VAZIO = "Nenhuma inovação cadastrada ainda."
LIMPAR = re.compile(r'<a href="/inovacoes/">\s*Limpar filtros\s*</a>')


def test_sem_parametros_nao_mostra_limpar_filtros(logado, criar_inovacao):
    """CONS-32: nada a limpar."""
    criar_inovacao()
    assert "Limpar filtros" not in logado.get(LISTA).content.decode()


def test_busca_so_com_espacos_nao_conta_como_ativa_e_lista_tudo(logado, criar_inovacao):
    """CONS-21, CONS-32: espacos nas pontas nao ativam nada."""
    criar_inovacao(titulo="Uma")
    criar_inovacao(titulo="Duas")
    resposta = logado.get(LISTA, {"q": "   "})
    assert "Limpar filtros" not in resposta.content.decode()
    assert _titulos(resposta) == ["Duas", "Uma"]


@pytest.mark.parametrize("parametro", ["q", "categoria", "unidade", "status"])
def test_qualquer_busca_ou_filtro_ativo_mostra_limpar_filtros_para_a_lista_sem_query(
    logado, tres, parametro
):
    """CONS-32: o link aponta para /inovacoes/ sem parametros."""
    valores = {
        "q": "conciliacao",
        "categoria": tres["financeiro"].pk,
        "unidade": tres["sede"].pk,
        "status": "VALIDADA",
    }
    html = logado.get(LISTA, {parametro: valores[parametro]}).content.decode()
    assert LIMPAR.search(html)


def test_consulta_sem_resultado_diz_o_que_houve_e_oferece_limpar_sem_tabela(logado, tres):
    """CONS-35: com inovacoes no banco, a busca "inexistente" nao acha nenhuma.

    T-D (redesign-consulta, T14, RCON-26): texto da §10 e a sugestao; "sem tabela" vira sem
    lista de resultados nem tabela (os cartoes sao o padrao, RCON-10).
    """
    html = logado.get(LISTA, {"q": "inexistente"}).content.decode()
    assert "<table" not in html
    assert 'aria-label="Resultados"' not in html
    assert MENSAGEM_REPOSITORIO_VAZIO not in html
    posicao = html.index(MENSAGEM_VAZIO_COM_FILTRO)
    assert html.index(SUGESTAO_VAZIO_COM_FILTRO, posicao) > posicao
    assert LIMPAR.search(html, posicao)


def test_filtro_sem_resultado_tambem_cai_no_estado_vazio_com_filtro(logado, tres):
    """CONS-35: filtro combinado sem correspondencia (Filial Norte + Validada).

    T-D (redesign-consulta, T14, RCON-26): sem lista de resultados nem tabela.
    """
    html = logado.get(LISTA, {"unidade": tres["norte"].pk, "status": "VALIDADA"}).content.decode()
    assert MENSAGEM_VAZIO_COM_FILTRO in html
    assert "<table" not in html
    assert 'aria-label="Resultados"' not in html


def test_banco_vazio_com_busca_mostra_a_mensagem_de_filtro_e_nao_a_do_repositorio(logado):
    """CONS-35, CONS-34: filtro ativo vence o repositorio vazio.

    T-D (redesign-consulta, T14, RCON-26): sem lista de resultados nem tabela.
    """
    html = logado.get(LISTA, {"q": "x"}).content.decode()
    assert MENSAGEM_VAZIO_COM_FILTRO in html
    assert MENSAGEM_REPOSITORIO_VAZIO not in html
    assert "<table" not in html
    assert 'aria-label="Resultados"' not in html


def test_banco_vazio_sem_parametros_continua_com_a_mensagem_do_repositorio(logado):
    """CONS-34: sem regressao."""
    html = logado.get(LISTA).content.decode()
    assert MENSAGEM_REPOSITORIO_VAZIO in html
    assert MENSAGEM_VAZIO_COM_FILTRO not in html
    assert "Limpar filtros" not in html
