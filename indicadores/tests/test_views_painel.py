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
