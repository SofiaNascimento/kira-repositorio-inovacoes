"""Testes e2e da listagem de inovacoes (/inovacoes/)."""

import datetime
import re

import pytest

from contas.models import Usuario
from inovacoes.models import Categoria, Inovacao, StatusInovacao, Unidade

LISTA = "/inovacoes/"


@pytest.fixture
def logado(client, autor):
    client.force_login(autor)
    return client


def _linhas(html):
    """Cada <tr> do <tbody> como lista do texto de suas celulas."""
    corpo = re.search(r"<tbody>(.*?)</tbody>", html, re.S).group(1)
    linhas = re.findall(r"<tr[^>]*>(.*?)</tr>", corpo, re.S)
    return [
        [re.sub(r"<[^>]+>", "", c).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", linha, re.S)]
        for linha in linhas
    ]


def _forcar_data(inovacao, dia):
    data = datetime.datetime(2026, 9, dia, 12, 0, tzinfo=datetime.UTC)
    Inovacao.objects.filter(pk=inovacao.pk).update(data_criacao=data)


def test_lista_mostra_uma_linha_por_inovacao_com_os_quatro_campos(logado, criar_inovacao):
    """CONS-01, CONS-40: titulo, categoria, unidade e o rotulo do status."""
    criar_inovacao(titulo="Controle de Caixa")
    outra_unidade = Unidade.objects.create(nome="Teste Outra Unidade")
    outra_categoria = Categoria.objects.create(nome="Teste Outra Categoria")
    criar_inovacao(
        titulo="Conciliação",
        unidade=outra_unidade,
        categoria=outra_categoria,
        status=StatusInovacao.DISPONIVEL_PARA_REPLICACAO,
    )
    resposta = logado.get(LISTA)
    assert resposta.status_code == 200
    linhas = _linhas(resposta.content.decode())
    assert sorted(linhas) == [
        [
            "Conciliação",
            "Teste Outra Categoria",
            "Teste Outra Unidade",
            "Disponível para replicação",
        ],
        ["Controle de Caixa", "Teste Categoria", "Teste Unidade", "Em teste"],
    ]


def test_lista_ordena_pela_mais_recente_e_desempata_por_id(logado, criar_inovacao):
    """CONS-02."""
    antiga = criar_inovacao(titulo="Antiga")
    empate_1 = criar_inovacao(titulo="Empate um")
    empate_2 = criar_inovacao(titulo="Empate dois")
    _forcar_data(antiga, 1)
    _forcar_data(empate_1, 9)
    _forcar_data(empate_2, 9)
    titulos = [linha[0] for linha in _linhas(logado.get(LISTA).content.decode())]
    assert titulos == ["Empate dois", "Empate um", "Antiga"]


def test_titulo_de_cada_linha_e_link_para_o_detalhe(logado, criar_inovacao):
    """CONS-06."""
    inovacao = criar_inovacao(titulo="Controle de Caixa")
    html = logado.get(LISTA).content.decode()
    url = re.escape(inovacao.get_absolute_url())
    assert re.search(rf'<td[^>]*>\s*<a href="{url}">\s*Controle de Caixa\s*</a>', html)
    assert inovacao.get_absolute_url() == f"/inovacoes/{inovacao.pk}/"


@pytest.mark.parametrize("perfil", ["USUARIO", "ADMINISTRADOR"])
def test_qualquer_perfil_ve_inovacoes_de_todos_os_autores_e_unidades(
    client, criar_inovacao, perfil
):
    """CONS-08."""
    outro_autor = Usuario.objects.create_user(username="bruno", email="bruno@x.com")
    outra_unidade = Unidade.objects.create(nome="Teste Outra Unidade")
    criar_inovacao(titulo="Da Ana")
    criar_inovacao(titulo="Do Bruno", autor=outro_autor, unidade=outra_unidade)
    leitor = Usuario.objects.create_user(
        username="carla", email="carla@x.com", perfil=perfil, password="senha-forte-123"
    )
    client.force_login(leitor)
    titulos = {linha[0] for linha in _linhas(client.get(LISTA).content.decode())}
    assert titulos == {"Da Ana", "Do Bruno"}


def test_anonimo_vai_ao_login_com_next_e_a_query_string_preservada(client):
    """CONS-07: o next e o do redirect_to_login do Django, com a query string."""
    resposta = client.get(f"{LISTA}?q=caixa")
    assert resposta.status_code == 302
    # Comparacao literal: assertRedirects normalizaria a query string.
    assert resposta["Location"] == "/entrar/?next=/inovacoes/%3Fq%3Dcaixa"


def test_contagem_no_singular(logado, criar_inovacao):
    """CONS-33."""
    criar_inovacao()
    assert "1 inovação encontrada" in logado.get(LISTA).content.decode()


def test_contagem_no_plural(logado, criar_inovacao):
    """CONS-33."""
    criar_inovacao(titulo="Uma")
    criar_inovacao(titulo="Duas")
    html = logado.get(LISTA).content.decode()
    assert "2 inovações encontradas" in html
    assert "1 inovação encontrada" not in html


def test_repositorio_vazio_mostra_mensagem_e_link_de_cadastro_sem_tabela(logado):
    """CONS-34."""
    html = logado.get(LISTA).content.decode()
    conteudo = html[html.index("<h1") :]
    assert "Nenhuma inovação cadastrada ainda." in conteudo
    assert re.search(r'<a href="/inovacoes/nova/">\s*Cadastrar inovação\s*</a>', conteudo)
    assert "<table" not in html
    assert "encontrada" not in html


def test_h1_e_titulo_da_pagina(logado):
    """CONS-01: a tela se identifica como Inovacoes."""
    assert re.search(r"<h1[^>]*>\s*Inovações\s*</h1>", logado.get(LISTA).content.decode())


def test_tabela_tem_caption_e_quatro_cabecalhos_de_coluna(logado, criar_inovacao):
    """CONS-38."""
    criar_inovacao()
    html = logado.get(LISTA).content.decode()
    assert "<caption>Inovações cadastradas</caption>" in html
    cabecalhos = re.findall(r'<th scope="col">(.*?)</th>', html, re.S)
    assert [c.strip() for c in cabecalhos] == ["Título", "Categoria", "Unidade", "Status"]
