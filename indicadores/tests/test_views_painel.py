"""Testes e2e do painel de indicadores (RF10, REAP-29 a REAP-40).

Os numeros esperados sao contados no teste, sem os QuerySets do painel.
Os reaproveitamentos nascem pelo metodo do modelo (AD-012).
"""

import re

import pytest
from pytest_django.asserts import assertRedirects

from inovacoes.models import Categoria, Inovacao, Reaproveitamento, StatusInovacao, Unidade

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
    return re.search(rf"<dt>{rotulo}</dt>\s*<dd>([^<]*)</dd>", html).group(1)


def _tabela(html, legenda):
    """(cabecalhos, linhas) da tabela com a legenda dada, so com o texto das celulas."""
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
    assert "<p>Nenhuma inovação cadastrada ainda.</p>" in vazio
    assert re.search(r'<a href="/inovacoes/nova/">Cadastrar inovação</a>', vazio)
    assert "<table" not in html
    assert "<svg" not in html


@pytest.mark.django_db
def test_com_inovacao_nao_mostra_o_convite_ao_cadastro(client, disponivel, terceiro):
    """REAP-37 ao contrario: com uma inovacao, as tabelas aparecem no lugar do convite."""
    disponivel()
    html = _html(client, terceiro)
    assert "Nenhuma inovação cadastrada ainda." not in html
    assert html.count("<table") == 2


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
