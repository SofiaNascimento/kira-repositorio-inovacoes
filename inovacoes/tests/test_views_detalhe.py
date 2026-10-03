"""Testes e2e da pagina de detalhe da inovacao (/inovacoes/<id>/)."""

import datetime
import re

import pytest
from django.utils.html import escape
from pytest_django.asserts import assertRedirects

from contas.models import Usuario
from inovacoes.models import Inovacao, StatusInovacao

ROTULOS = [
    "Título",
    "Unidade de origem",
    "Categoria",
    "Problema ou dor",
    "Solução aplicada",
    "Resultado ou impacto",
    "Status",
    "Contato responsável",
]


@pytest.fixture
def logado(client, autor):
    client.force_login(autor)
    return client


def _pares(html):
    """Lista de (rotulo, valor) dos <dt>/<dd> da pagina, na ordem em que aparecem."""
    rotulos = re.findall(r"<dt[^>]*>(.*?)</dt>", html, re.S)
    valores = re.findall(r"<dd[^>]*>(.*?)</dd>", html, re.S)
    return [(r.strip(), v.strip()) for r, v in zip(rotulos, valores, strict=True)]


def test_detalhe_mostra_h1_e_os_oito_campos_em_lista_de_descricao(logado, criar_inovacao):
    """CONS-12, CONS-42."""
    inovacao = criar_inovacao(resultado="Fechamento em duas horas.")
    resposta = logado.get(f"/inovacoes/{inovacao.pk}/")
    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert re.search(r"<h1[^>]*>\s*Controle de Caixa\s*</h1>", html)
    assert _pares(html) == [
        ("Título", "Controle de Caixa"),
        ("Unidade de origem", "Teste Unidade"),
        ("Categoria", "Teste Categoria"),
        ("Problema ou dor", "Fechamento de caixa manual e demorado."),
        ("Solução aplicada", "Planilha compartilhada com conferencia diaria."),
        ("Resultado ou impacto", "Fechamento em duas horas."),
        ("Status", "Em teste"),
        ("Contato responsável", "Ana Souza (ana@x.com)"),
    ]
    assert [r for r, _ in _pares(html)] == ROTULOS
    assert "<dl" in html


def test_detalhe_mostra_o_rotulo_do_status_e_nao_o_valor_interno(logado, criar_inovacao):
    """CONS-12: o status aparece pelo rotulo."""
    inovacao = criar_inovacao(status=StatusInovacao.DISPONIVEL_PARA_REPLICACAO)
    html = logado.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert ("Status", "Disponível para replicação") in _pares(html)


def test_detalhe_mostra_cadastrada_por_com_nome_completo_e_data(logado, criar_inovacao):
    """CONS-13."""
    inovacao = criar_inovacao()
    html = logado.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    data = inovacao.data_criacao.astimezone(datetime.timezone(datetime.timedelta(hours=-3)))
    assert f"Cadastrada por Ana Souza em {data:%d/%m/%Y}" in html


def test_detalhe_mostra_o_username_quando_a_conta_nao_tem_nome(logado, criar_inovacao):
    """CONS-13: sem nome nem sobrenome, o autor e o username."""
    bruno = Usuario.objects.create_user(username="bruno", email="bruno@x.com")
    inovacao = criar_inovacao(autor=bruno)
    html = logado.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert "Cadastrada por bruno em " in html


def test_detalhe_mostra_a_data_no_fuso_de_sao_paulo(logado, criar_inovacao):
    """CONS-13: 02:30 UTC de 15/09 e 23:30 de 14/09 em America/Sao_Paulo."""
    inovacao = criar_inovacao()
    Inovacao.objects.filter(pk=inovacao.pk).update(
        data_criacao=datetime.datetime(2026, 9, 15, 2, 30, tzinfo=datetime.UTC)
    )
    html = logado.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert "Cadastrada por Ana Souza em 14/09/2026" in html
    assert "15/09/2026" not in html


def test_resultado_vazio_mostra_nao_informado(logado, criar_inovacao):
    """CONS-14."""
    inovacao = criar_inovacao(resultado="")
    html = logado.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert ("Resultado ou impacto", "Não informado") in _pares(html)


def test_quebras_de_linha_dos_textos_longos_viram_br(logado, criar_inovacao):
    """CONS-16: problema, solucao e resultado."""
    inovacao = criar_inovacao(problema="a\nb", solucao="c\nd", resultado="e\nf")
    pares = dict(_pares(logado.get(f"/inovacoes/{inovacao.pk}/").content.decode()))
    assert pares["Problema ou dor"] == "a<br>b"
    assert pares["Solução aplicada"] == "c<br>d"
    assert pares["Resultado ou impacto"] == "e<br>f"


def test_html_digitado_sai_como_texto_literal(logado, criar_inovacao):
    """CONS-17."""
    inovacao = criar_inovacao(solucao="<b>x</b>", titulo="<i>t</i>", contato="<u>c</u>")
    html = logado.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert "&lt;b&gt;x&lt;/b&gt;" in html
    assert "&lt;i&gt;t&lt;/i&gt;" in html
    assert "&lt;u&gt;c&lt;/u&gt;" in html
    assert "<b>x</b>" not in html
    assert "<i>t</i>" not in html
    assert "<u>c</u>" not in html


def test_detalhe_tem_link_de_volta_para_a_lista(logado, criar_inovacao):
    """CONS-18."""
    inovacao = criar_inovacao()
    html = logado.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert re.search(r'<a href="/inovacoes/">\s*Voltar para a lista de inovações\s*</a>', html)


def test_get_absolute_url_aponta_para_o_detalhe(criar_inovacao):
    """CONS-06: URL canonica do detalhe."""
    inovacao = criar_inovacao()
    assert inovacao.get_absolute_url() == f"/inovacoes/{inovacao.pk}/"


@pytest.mark.parametrize("perfil", ["USUARIO", "ADMINISTRADOR"])
def test_qualquer_perfil_abre_inovacao_de_outro_autor(client, criar_inovacao, perfil):
    """CONS-08."""
    inovacao = criar_inovacao()
    outro = Usuario.objects.create_user(
        username="carla", email="carla@x.com", perfil=perfil, password="senha-forte-123"
    )
    client.force_login(outro)
    resposta = client.get(f"/inovacoes/{inovacao.pk}/")
    assert resposta.status_code == 200
    assert escape("Controle de Caixa") in resposta.content.decode()


def test_anonimo_vai_para_o_login_com_next_do_detalhe(client, criar_inovacao):
    """CONS-07."""
    inovacao = criar_inovacao()
    caminho = f"/inovacoes/{inovacao.pk}/"
    resposta = client.get(caminho)
    assertRedirects(resposta, f"/entrar/?next={caminho}", fetch_redirect_response=False)
