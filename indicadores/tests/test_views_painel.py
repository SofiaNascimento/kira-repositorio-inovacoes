"""Testes e2e do painel de indicadores (RF10, REAP-29 a REAP-40).

Os numeros esperados sao contados no teste, sem os QuerySets do painel.
Os reaproveitamentos nascem pelo metodo do modelo (AD-012).
"""

import re
from html.parser import HTMLParser

import pytest
from django.db import OperationalError
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from inovacoes.models import (
    Categoria,
    CategoriaQuerySet,
    Inovacao,
    Reaproveitamento,
    StatusInovacao,
    Unidade,
    UnidadeQuerySet,
)
from inovacoes.tests.test_views_erro_500 import DETALHE_DA_CONEXAO
from inovacoes.tests.test_views_sistema_design import _elementos
from inovacoes.tests.visibilidade import exibido

URL = "/indicadores/"


@pytest.fixture
def disponivel(criar_inovacao):
    """Cria inovacoes com titulos distintos (o titulo e unico por unidade)."""
    contador = iter(range(1, 1000))

    def criar(**campos):
        campos.setdefault("status", StatusInovacao.DISPONIVEL_PARA_REPLICACAO)
        return criar_inovacao(titulo=f"Inovacao {next(contador)}", **campos)

    return criar


@pytest.fixture
def cenario(disponivel, unidade, autor):
    """TI interno 2, Compras 1, Teste Categoria 1; Sede com 2 de origem e 1 feito."""
    sede = Unidade.objects.get(nome="Sede")
    norte = Unidade.objects.get(nome="Filial Norte")
    ti = Categoria.objects.get(nome="TI interno")
    compras = Categoria.objects.get(nome="Compras")
    primeira = disponivel(categoria=ti)
    disponivel(categoria=ti, status=StatusInovacao.EM_TESTE)
    disponivel(categoria=compras, unidade=sede, status=StatusInovacao.VALIDADA)
    disponivel(unidade=sede)
    primeira.registrar_reaproveitamento(unidade=sede, por=autor)
    primeira.registrar_reaproveitamento(unidade=norte, por=autor)


def _html(client, conta):
    client.force_login(conta)
    resposta = client.get(URL)
    assert resposta.status_code == 200
    return resposta.content.decode()


def _card(html, rotulo):
    valor = _card_no(html, rotulo)
    assert valor is not None, rotulo
    # L-028, L-030: o card e cada ancestral ficam na tela e no leitor de tela.
    assert _card_no(exibido(html), rotulo) == valor, rotulo
    return valor


def _card_no(html, rotulo):
    achado = re.search(rf"<dt>{rotulo}</dt>\s*<dd>([^<]*)</dd>", html)
    return achado and achado.group(1)


def _tabela(html, legenda):
    """(cabecalhos, linhas) da tabela com a legenda dada, so com o texto das celulas."""
    tabela = _tabela_no(html, legenda)
    assert tabela is not None, legenda
    # L-028, L-030: a tabela e cada ancestral ficam na tela e no leitor de tela.
    assert _tabela_no(exibido(html), legenda) == tabela, legenda
    return tabela


def _tabela_no(html, legenda):
    if f"<caption>{legenda}</caption>" not in html:
        return None
    corpo = re.search(rf"<caption>{legenda}</caption>(.*?)</table>", html, re.S).group(1)
    linhas = [
        [texto.strip() for texto in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", linha, re.S)]
        for linha in re.findall(r"<tr>(.*?)</tr>", corpo, re.S)
    ]
    return linhas[0], linhas[1:]


def _esperado(itens):
    """Ordem da REAP-32/REAP-33: contagem decrescente, nome no empate."""
    return sorted(itens, key=lambda linha: (-int(linha[1]), linha[0]))


@pytest.mark.django_db
@pytest.mark.parametrize("perfil", ["terceiro", "administrador"])
def test_painel_abre_com_titulo_e_h1(client, request, perfil):
    """REAP-29: USUARIO comum e administrador abrem o painel."""
    html = _html(client, request.getfixturevalue(perfil))
    assert re.search(r"<title>Painel de indicadores", html)
    assert re.search(r"<h1>Painel de indicadores</h1>", html)
    # L-028, L-030: o titulo fica na tela e no leitor de tela.
    assert re.search(r"<h1>Painel de indicadores</h1>", exibido(html))


@pytest.mark.django_db
def test_cards_contam_todas_as_inovacoes_e_todos_os_reaproveitamentos(client, cenario, terceiro):
    """REAP-30: inovacoes dos tres status; REAP-31: todos os reaproveitamentos."""
    assert set(Inovacao.objects.values_list("status", flat=True)) == set(StatusInovacao.values)
    html = _html(client, terceiro)
    assert _card(html, "Inovações cadastradas") == "4"
    assert _card(html, "Reaproveitamentos registrados") == "2"


@pytest.mark.django_db
def test_tabela_por_categoria_tem_uma_linha_por_categoria_na_ordem(client, cenario, terceiro):
    """REAP-32: inclusive as categorias com 0; total desc, nome asc."""
    esperado = _esperado(
        [c.nome, str(Inovacao.objects.filter(categoria=c).count())] for c in Categoria.objects.all()
    )
    cabecalhos, linhas = _tabela(_html(client, terceiro), "Inovações por categoria")
    assert cabecalhos == ["Categoria", "Inovações"]
    assert linhas == esperado
    assert linhas == [
        ["TI interno", "2"],
        ["Compras", "1"],
        ["Teste Categoria", "1"],
        ["Atendimento interno", "0"],
        ["Financeiro", "0"],
        ["RH", "0"],
    ]


@pytest.mark.django_db
def test_tabela_por_unidade_tem_origem_e_reaproveitamentos_feitos(client, cenario, terceiro):
    """REAP-33: tres colunas, inclusive unidades com 0 e 0; origem desc, nome asc."""
    esperado = _esperado(
        [
            u.nome,
            str(Inovacao.objects.filter(unidade=u).count()),
            str(Reaproveitamento.objects.filter(unidade=u).count()),
        ]
        for u in Unidade.objects.all()
    )
    cabecalhos, linhas = _tabela(_html(client, terceiro), "Inovações por unidade")
    assert cabecalhos == ["Unidade", "Inovações de origem", "Reaproveitamentos feitos"]
    assert linhas == esperado
    assert linhas == [
        ["Sede", "2", "1"],
        ["Teste Unidade", "2", "0"],
        ["Filial Leste", "0", "0"],
        ["Filial Norte", "0", "1"],
        ["Filial Oeste", "0", "0"],
        ["Filial Sul", "0", "0"],
    ]


@pytest.mark.django_db
def test_sem_inovacao_mostra_zeros_e_o_convite_ao_cadastro(client, terceiro):
    """REAP-37: cards com 0, texto e link de cadastro, sem tabela nem grafico."""
    html = _html(client, terceiro)
    assert _card(html, "Inovações cadastradas") == "0"
    assert _card(html, "Reaproveitamentos registrados") == "0"
    vazio = re.search(r'<div class="vazio">(.*?)</div>', html, re.S).group(1)
    # L-028, L-030: o texto e o link ficam na tela e no leitor de tela.
    visivel = re.search(r'<div class="vazio">(.*?)</div>', exibido(html), re.S)
    assert visivel and visivel.group(1) == vazio
    assert "<p>Nenhuma inovação cadastrada ainda.</p>" in vazio
    assert re.search(r'<a href="/inovacoes/nova/">Cadastrar inovação</a>', vazio)
    assert "<table" not in html
    # T-E (fundacao-do-redesign): os icones do menu sao SVG; o painel vazio nao tem grafico.
    assert "<svg" not in html[html.index('<main id="conteudo">') : html.index("</main>")]


@pytest.mark.django_db
def test_com_inovacao_nao_mostra_o_convite_ao_cadastro(client, disponivel, terceiro):
    """REAP-37 ao contrario: com uma inovacao, as tabelas aparecem no lugar do convite."""
    disponivel()
    html = _html(client, terceiro)
    assert "Nenhuma inovação cadastrada ainda." not in html
    assert html.count("<table") == 2
    # L-028, L-030: as duas tabelas ficam na tela e no leitor de tela.
    assert exibido(html).count("<table") == 2


@pytest.mark.django_db
def test_numeros_saem_do_banco_a_cada_requisicao(client, disponivel, unidade, autor, terceiro):
    """REAP-38: o que foi gravado ou apagado antes aparece na resposta seguinte."""
    primeira = disponivel()
    html = _html(client, terceiro)
    assert (_card(html, "Inovações cadastradas"), _card(html, "Reaproveitamentos registrados")) == (
        "1",
        "0",
    )

    primeira.registrar_reaproveitamento(unidade=Unidade.objects.get(nome="Sede"), por=autor)
    segunda = disponivel()
    html = _html(client, terceiro)
    assert (_card(html, "Inovações cadastradas"), _card(html, "Reaproveitamentos registrados")) == (
        "2",
        "1",
    )
    assert ["Teste Unidade", "2", "0"] in _tabela(html, "Inovações por unidade")[1]

    segunda.delete()
    html = _html(client, terceiro)
    assert _card(html, "Inovações cadastradas") == "1"
    assert ["Teste Unidade", "1", "0"] in _tabela(html, "Inovações por unidade")[1]


@pytest.mark.django_db
def test_painel_nao_altera_nada(client, cenario, terceiro):
    """REAP-39: nenhuma linha de Inovacao, Reaproveitamento, Categoria ou Unidade muda."""
    modelos = [Inovacao, Reaproveitamento, Categoria, Unidade]

    def retrato():
        return [list(modelo.objects.order_by("pk").values()) for modelo in modelos]

    antes = retrato()
    _html(client, terceiro)
    assert retrato() == antes


@pytest.mark.django_db
def test_anonimo_vai_ao_login(client):
    """REAP-40."""
    resposta = client.get(URL)
    assertRedirects(resposta, f"/entrar/?next={URL}", fetch_redirect_response=False)


# --- T14: graficos de barras em SVG (REAP-34 a REAP-36, REAP-47) ----------------

TITULOS = [
    "Inovações por categoria",
    "Inovações de origem por unidade",
    "Reaproveitamentos feitos por unidade",
]


def _graficos(html):
    """{titulo: grafico} com figcaption, atributos do svg e linhas (nome, valor, barra)."""
    graficos = _graficos_no(html)
    # L-028, L-030: cada grafico e seus ancestrais ficam na tela e no leitor de tela.
    assert _graficos_no(exibido(html)) == graficos
    return graficos


def _graficos_no(html):
    graficos = {}
    for figura in re.findall(r'<figure class="cartao grafico">(.*?)</figure>', html, re.S):
        id_legenda, titulo = re.search(
            r'<figcaption id="([^"]+)">([^<]*)</figcaption>', figura
        ).groups()
        svg = re.search(r"<svg([^>]*)>(.*?)</svg>", figura, re.S)
        linhas = []
        for tag, atributos, texto in re.findall(
            r"<(text|rect)\s([^>]*?)/?>(?:([^<]*)</text>)?", svg.group(2)
        ):
            classe = re.search(r'class="([^"]+)"', atributos).group(1)
            if classe == "grafico__nome":
                linhas.append({"nome": texto, "barra": None})
            elif classe == "grafico__barra":
                linhas[-1]["barra"] = re.search(r'width="([^"]*)"', atributos).group(1)
            else:
                linhas[-1]["valor"] = texto
                linhas[-1]["x_valor"] = re.search(r'x="([^"]*)"', atributos).group(1)
        graficos[titulo] = {"id": id_legenda, "svg": svg.group(1), "linhas": linhas}
    return graficos


@pytest.mark.django_db
def test_painel_tem_os_tres_graficos_com_titulo(client, cenario, terceiro):
    """REAP-34."""
    graficos = _graficos(_html(client, terceiro))
    assert list(graficos) == TITULOS


@pytest.mark.django_db
def test_cada_svg_e_imagem_nomeada_pelo_proprio_titulo(client, cenario, terceiro):
    """REAP-47: role=img e aria-labelledby apontando para o figcaption do mesmo grafico."""
    graficos = _graficos(_html(client, terceiro))
    assert len({g["id"] for g in graficos.values()}) == 3
    for titulo, grafico in graficos.items():
        assert 'role="img"' in grafico["svg"], titulo
        assert f'aria-labelledby="{grafico["id"]}"' in grafico["svg"], titulo


@pytest.mark.django_db
def test_barras_seguem_as_linhas_e_os_valores_da_tabela(client, cenario, terceiro):
    """REAP-34, REAP-36: uma barra por linha da coluna, na ordem da tabela, com nome e valor."""
    html = _html(client, terceiro)
    graficos = _graficos(html)
    _, categorias = _tabela(html, "Inovações por categoria")
    _, unidades = _tabela(html, "Inovações por unidade")
    pares = {
        TITULOS[0]: [(nome, total) for nome, total in categorias],
        TITULOS[1]: [(nome, origem) for nome, origem, _ in unidades],
        TITULOS[2]: [(nome, feitos) for nome, _, feitos in unidades],
    }
    for titulo, esperado in pares.items():
        linhas = graficos[titulo]["linhas"]
        assert [(linha["nome"], linha["valor"]) for linha in linhas] == esperado, titulo


@pytest.mark.django_db
def test_maior_valor_ocupa_a_area_e_os_outros_saem_proporcionais_com_ponto(
    client, disponivel, terceiro, settings
):
    """REAP-35: o maior vale 480 (100% da area); 1 de 3 vale 160, com ponto e nao virgula."""
    assert settings.LANGUAGE_CODE == "pt-br"
    ti = Categoria.objects.get(nome="TI interno")
    for _ in range(3):
        disponivel(categoria=ti)
    disponivel(categoria=Categoria.objects.get(nome="Compras"))

    html = _html(client, terceiro)
    linhas = {linha["nome"]: linha for linha in _graficos(html)[TITULOS[0]]["linhas"]}
    assert float(linhas["TI interno"]["barra"]) == 480
    assert linhas["Compras"]["barra"] in {"160.0", "160"}
    for atributo in re.findall(r'(?:width|x|y|viewBox)="([^"]*)"', html):
        assert "," not in atributo


@pytest.mark.django_db
def test_valor_zero_tem_nome_e_zero_sem_barra(client, cenario, terceiro):
    """REAP-35, REAP-36: o item com 0 aparece por texto, sem retangulo."""
    linhas = {
        linha["nome"]: linha for linha in _graficos(_html(client, terceiro))[TITULOS[0]]["linhas"]
    }
    assert linhas["RH"]["valor"] == "0"
    assert linhas["RH"]["barra"] is None
    assert linhas["TI interno"]["barra"] is not None


@pytest.mark.django_db
def test_grafico_todo_zero_nao_tem_barra(client, disponivel, terceiro):
    """REAP-35: sem reaproveitamentos, o grafico deles nao desenha nenhum retangulo."""
    disponivel()
    html = _html(client, terceiro)
    figuras = re.findall(r'<figure class="cartao grafico">(.*?)</figure>', html, re.S)
    reaproveitamentos = next(f for f in figuras if TITULOS[2] in f)
    assert "<rect" not in reaproveitamentos
    linhas = _graficos(html)[TITULOS[2]]["linhas"]
    assert linhas and all(linha["valor"] == "0" for linha in linhas)


@pytest.mark.django_db
def test_nome_longo_e_truncado_no_svg_e_inteiro_na_tabela(client, disponivel, terceiro):
    """Risco do design: o nome longo nao passa do viewBox; a tabela traz o nome inteiro."""
    nome = "Categoria " + "x" * 70
    assert len(nome) == 80
    disponivel(categoria=Categoria.objects.create(nome=nome))

    html = _html(client, terceiro)
    nomes = [linha["nome"].strip() for linha in _graficos(html)[TITULOS[0]]["linhas"]]
    # A traducao pt-BR do Django poe um espaco antes do texto truncado; o SVG o descarta.
    truncado = next(n for n in nomes if n.startswith("Categoria x"))
    assert truncado.endswith("…")
    assert len(truncado) <= 70
    assert nome.startswith(truncado.removesuffix("…"))
    assert nome not in nomes
    assert [nome, "1"] in _tabela(html, "Inovações por categoria")[1]


# --- T18: acessibilidade e falha de banco do painel (REAP-46, REAP-47, REAP-49) --

VAZIOS = {"area", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "wbr"}


class Arvore(HTMLParser):
    """Arvore de elementos {tag, atributos, filhos, texto} com o aninhamento do HTML.

    O Elementos do DS-01 e plano; aqui a pergunta e "esta dentro de qual secao".
    """

    def __init__(self):
        super().__init__()
        self.raiz = {"tag": None, "atributos": {}, "filhos": [], "texto": ""}
        self.pilha = [self.raiz]

    def handle_starttag(self, tag, attrs):
        no = {"tag": tag, "atributos": dict(attrs), "filhos": [], "texto": ""}
        self.pilha[-1]["filhos"].append(no)
        if tag not in VAZIOS:
            self.pilha.append(no)

    def handle_startendtag(self, tag, attrs):
        self.pilha[-1]["filhos"].append(
            {"tag": tag, "atributos": dict(attrs), "filhos": [], "texto": ""}
        )

    def handle_endtag(self, tag):
        while len(self.pilha) > 1:
            if self.pilha.pop()["tag"] == tag:
                break

    def handle_data(self, data):
        self.pilha[-1]["texto"] += data


def _arvore(html):
    parser = Arvore()
    parser.feed(html)
    return parser.raiz


def _todos(no, tag):
    """Descendentes de `no` com a tag dada, em ordem de documento."""
    achados = []
    for filho in no["filhos"]:
        if filho["tag"] == tag:
            achados.append(filho)
        achados.extend(_todos(filho, tag))
    return achados


def _texto(no):
    return (no["texto"] + "".join(_texto(filho) for filho in no["filhos"])).strip()


def _celulas(linha):
    return [filho for filho in linha["filhos"] if filho["tag"] in {"th", "td"}]


@pytest.mark.django_db
def test_tabelas_tem_caption_e_cabecalhos_com_scope(client, cenario, terceiro):
    """REAP-46: caption, th scope=col nas colunas e th scope=row na primeira celula."""
    html = _html(client, terceiro)
    tabelas = _todos(_arvore(html), "table")
    # L-028, L-030: cada tabela, caption e celula incluidos, fica na tela e no leitor de tela.
    visiveis = _todos(_arvore(exibido(html)), "table")
    assert [_texto(t) for t in visiveis] == [_texto(t) for t in tabelas]
    assert [_texto(_todos(t, "caption")[0]) for t in tabelas] == [
        "Inovações por categoria",
        "Inovações por unidade",
    ]
    for tabela in tabelas:
        legenda = _texto(_todos(tabela, "caption")[0])
        (cabecalho,) = _todos(_todos(tabela, "thead")[0], "tr")
        assert [(c["tag"], c["atributos"].get("scope")) for c in _celulas(cabecalho)] == [
            ("th", "col")
        ] * len(_celulas(cabecalho)), legenda
        linhas = _todos(_todos(tabela, "tbody")[0], "tr")
        assert len(linhas) == 6, legenda
        for linha in linhas:
            primeira, *resto = _celulas(linha)
            assert (primeira["tag"], primeira["atributos"].get("scope")) == ("th", "row"), legenda
            assert resto and all(c["tag"] == "td" for c in resto), legenda


@pytest.mark.django_db
def test_cada_grafico_fica_na_secao_da_tabela_com_os_mesmos_numeros(client, cenario, terceiro):
    """REAP-47: a tabela da mesma secao e a alternativa textual de cada grafico.

    Todo par (nome, valor) do grafico e uma linha da coluna correspondente da tabela.
    """
    html = _html(client, terceiro)
    secoes = _todos(_arvore(html), "section")
    # L-028, L-030: cada secao, grafico e tabela incluidos, fica na tela e no leitor de tela.
    visiveis = _todos(_arvore(exibido(html)), "section")
    assert [_texto(s) for s in visiveis] == [_texto(s) for s in secoes]
    colunas = {TITULOS[0]: 1, TITULOS[1]: 1, TITULOS[2]: 2}
    vistos = []
    for secao in secoes:
        (tabela,) = _todos(secao, "table")
        linhas = [
            [_texto(c) for c in _celulas(linha)]
            for linha in _todos(_todos(tabela, "tbody")[0], "tr")
        ]
        for figura in _todos(secao, "figure"):
            titulo = _texto(_todos(figura, "figcaption")[0])
            (svg,) = _todos(figura, "svg")
            assert svg["atributos"]["role"] == "img", titulo
            nomes = [
                _texto(t) for t in _todos(svg, "text") if "grafico__nome" in t["atributos"]["class"]
            ]
            valores = [
                _texto(t)
                for t in _todos(svg, "text")
                if "grafico__valor" in t["atributos"]["class"]
            ]
            assert list(zip(nomes, valores)) == [
                (linha[0], linha[colunas[titulo]]) for linha in linhas
            ], titulo
            vistos.append(titulo)
    assert vistos == TITULOS


@pytest.mark.django_db
def test_cards_usam_lista_de_definicao_com_rotulo_e_numero(client, cenario, terceiro):
    """Cards: rotulo em dt e numero em dd, dentro do dl.metricas."""
    html = _html(client, terceiro)
    esperado = [
        ("dt", "Inovações cadastradas"),
        ("dd", "4"),
        ("dt", "Reaproveitamentos registrados"),
        ("dd", "2"),
    ]
    assert _pares_dos_cards(html) == esperado
    # L-028, L-030: o dl e cada card ficam na tela e no leitor de tela.
    assert _pares_dos_cards(exibido(html)) == esperado


def _pares_dos_cards(html):
    elementos = _elementos(html)
    inicio = next(
        (
            i
            for i, (tag, atributos, _) in enumerate(elementos)
            if tag == "dl" and "metricas" in atributos.get("class", "").split()
        ),
        None,
    )
    if inicio is None:
        return None
    return [
        (tag, texto.strip()) for tag, _, texto in elementos[inicio + 1 :] if tag in {"dt", "dd"}
    ][:4]


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("alvo", "atributo"),
    [
        (CategoriaQuerySet, "com_total_de_inovacoes"),
        (UnidadeQuerySet, "com_indicadores"),
    ],
    ids=["por-categoria", "por-unidade"],
)
def test_banco_indisponivel_no_painel_devolve_500_sem_detalhes(
    monkeypatch, client, cenario, terceiro, alvo, atributo
):
    """REAP-49: pagina 500 do projeto, sem host, usuario, senha nem traceback; nada gravado."""

    def falhar(*args, **kwargs):
        raise OperationalError(DETALHE_DA_CONEXAO)

    reaproveitamentos = Reaproveitamento.objects.count()
    monkeypatch.setattr(alvo, atributo, falhar)
    client.force_login(terceiro)
    client.raise_request_exception = False
    resposta = client.get(URL)
    assert resposta.status_code == 500
    assertTemplateUsed(resposta, "500.html")
    html = resposta.content.decode()
    for trecho in [
        "db.interno.kira",
        "kira_app",
        "s3gr3d0-do-banco",
        "OperationalError",
        "Traceback",
    ]:
        assert trecho not in html, trecho
    assert DETALHE_DA_CONEXAO not in html
    assert Reaproveitamento.objects.count() == reaproveitamentos
