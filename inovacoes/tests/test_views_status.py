"""Testes e2e da confirmacao e do avanco de status (/inovacoes/<id>/status/)."""

import re

import pytest
from pytest_django.asserts import assertTemplateUsed

from inovacoes.models import Inovacao, MudancaDeStatus, StatusInovacao

EM_TESTE = StatusInovacao.EM_TESTE
VALIDADA = StatusInovacao.VALIDADA
DISPONIVEL = StatusInovacao.DISPONIVEL_PARA_REPLICACAO

NEGADO = "Você não tem permissão para alterar esta inovação."
ULTIMO_ESTAGIO = "Esta inovação já está em “Disponível para replicação”, o último estágio do ciclo."


def _status(inovacao):
    return f"/inovacoes/{inovacao.pk}/status/"


def _entrar(client, conta):
    client.force_login(conta)
    return client


def _conteudo(html):
    """O <main> da pagina: o cabecalho tem o form e o botao do "Sair"."""
    return html[html.index('<main id="conteudo">') : html.index("</main>")]


def _status_no_banco(inovacao):
    return Inovacao.objects.values_list("status", flat=True).get(pk=inovacao.pk)


def _formulario_de_confirmacao(html):
    formularios = re.findall(r"<form\b([^>]*)>(.*?)</form>", _conteudo(html), re.S)
    assert len(formularios) == 1, formularios
    return formularios[0]


def _afirma_confirmacao(resposta, inovacao, atual, proximo):
    """STAT-06: 200, "Avancar status", o aviso, o botao, o status visto e o Cancelar."""
    assert resposta.status_code == 200
    assertTemplateUsed(resposta, "inovacoes/inovacao_status.html")
    html = resposta.content.decode()
    titulo = re.search(r"<title>(.*?)</title>", html, re.S).group(1).strip()
    assert titulo.startswith("Avançar status")
    assert re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.S) == ["Avançar status"]
    assert (
        f"Você vai avançar a inovação “Controle de Caixa” de “{atual}” para “{proximo}”. "
        "Depois de avançar, não é possível voltar ao status anterior."
    ) in html
    atributos, corpo = _formulario_de_confirmacao(html)
    assert re.search(r'\bmethod="post"', atributos)
    assert 'name="csrfmiddlewaretoken"' in corpo
    botoes = re.findall(r"<button\b([^>]*)>\s*(.*?)\s*</button>", corpo, re.S)
    assert [texto for _, texto in botoes] == [f"Avançar para “{proximo}”"]
    assert 'type="submit"' in botoes[0][0]
    vistos = re.findall(r'<input\b[^>]*\bname="status_visto"[^>]*>', corpo)
    assert len(vistos) == 1
    assert 'type="hidden"' in vistos[0]
    assert re.search(r'\bvalue="([^"]*)"', vistos[0]).group(1) == inovacao.status
    cancelar = re.findall(r'<a href="([^"]*)">\s*Cancelar\s*</a>', corpo)
    assert cancelar == [f"/inovacoes/{inovacao.pk}/"]


def test_autor_ve_a_confirmacao_de_em_teste_para_validada(client, autor, criar_inovacao):
    """STAT-06, STAT-17: autor USUARIO, inovacao "Em teste"."""
    inovacao = criar_inovacao()
    resposta = _entrar(client, autor).get(_status(inovacao))
    _afirma_confirmacao(resposta, inovacao, "Em teste", "Validada")


def test_autor_ve_a_confirmacao_de_validada_para_disponivel(client, autor, criar_inovacao):
    """STAT-06 no segundo passo do ciclo."""
    inovacao = criar_inovacao(status=VALIDADA)
    resposta = _entrar(client, autor).get(_status(inovacao))
    _afirma_confirmacao(resposta, inovacao, "Validada", "Disponível para replicação")


def test_administrador_ve_a_confirmacao_da_inovacao_de_outro_autor(
    client, administrador, criar_inovacao
):
    """STAT-06 para o administrador (AD-009)."""
    inovacao = criar_inovacao()
    resposta = _entrar(client, administrador).get(_status(inovacao))
    _afirma_confirmacao(resposta, inovacao, "Em teste", "Validada")


@pytest.mark.parametrize("conta", ["autor", "administrador"])
def test_ultimo_estagio_explica_e_nao_oferece_botao(client, criar_inovacao, conta, request):
    """STAT-10 (GET): 200, o texto do estagio final, sem form nem botao, e o Voltar."""
    inovacao = criar_inovacao(status=DISPONIVEL)
    resposta = _entrar(client, request.getfixturevalue(conta)).get(_status(inovacao))
    assert resposta.status_code == 200
    assertTemplateUsed(resposta, "inovacoes/inovacao_status.html")
    conteudo = _conteudo(resposta.content.decode())
    assert ULTIMO_ESTAGIO in conteudo
    assert "<form" not in conteudo
    assert "<button" not in conteudo
    voltar = re.findall(r'<a href="([^"]*)">\s*Voltar para a inovação\s*</a>', conteudo)
    assert voltar == [f"/inovacoes/{inovacao.pk}/"]


@pytest.mark.parametrize("status", [EM_TESTE, VALIDADA, DISPONIVEL])
def test_get_nunca_muda_o_status_nem_registra(client, autor, criar_inovacao, status):
    """STAT-11: um link seguido por engano ou pre-carregado nao avanca."""
    inovacao = criar_inovacao(status=status)
    logado = _entrar(client, autor)
    for _ in range(3):
        assert logado.get(_status(inovacao)).status_code == 200
    assert _status_no_banco(inovacao) == status
    assert MudancaDeStatus.objects.count() == 0


def test_terceiro_recebe_403_na_confirmacao(client, terceiro, criar_inovacao):
    """STAT-19 (GET): a pagina de acesso negado da EDEX-20, e nada muda."""
    inovacao = criar_inovacao()
    resposta = _entrar(client, terceiro).get(_status(inovacao))
    assert resposta.status_code == 403
    assertTemplateUsed(resposta, "inovacoes/acesso_negado.html")
    assert NEGADO in resposta.content.decode()
    assert _status_no_banco(inovacao) == EM_TESTE
    assert MudancaDeStatus.objects.count() == 0


def test_id_sem_inovacao_na_confirmacao_responde_404_com_pagina_propria(client, autor):
    """STAT-22 (GET): o 404 da CONS-15."""
    resposta = _entrar(client, autor).get("/inovacoes/999999/status/")
    assert resposta.status_code == 404
    assertTemplateUsed(resposta, "inovacoes/inovacao_nao_encontrada.html")
    assert re.search(r"<h1[^>]*>\s*Inovação não encontrada\.\s*</h1>", resposta.content.decode())
    assert MudancaDeStatus.objects.count() == 0
