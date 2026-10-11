"""Testes e2e da tela de edicao de inovacao (/inovacoes/<id>/editar/)."""

import re

import pytest
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from contas.models import Usuario
from inovacoes.models import Inovacao

CAMPOS = ["titulo", "unidade", "categoria", "problema", "solucao", "resultado", "contato"]
NEGADO = "Você não tem permissão para alterar esta inovação."
SO_AUTOR = "Só quem cadastrou a inovação ou um administrador pode editá-la ou excluí-la."


def _editar(inovacao):
    return f"/inovacoes/{inovacao.pk}/editar/"


def _entrar(client, conta):
    client.force_login(conta)
    return client


def _formulario(html):
    """O formulario da pagina, sem o cabecalho (que tem o botao "Sair")."""
    return re.search(r"<form[^>]*novalidate[^>]*>(.*?)</form>", html, re.S).group(1)


def _link_cancelar(html):
    links = re.findall(r"<a\b([^>]*)>\s*Cancelar\s*</a>", html)
    assert len(links) == 1, links
    return re.search(r'\bhref="([^"]*)"', links[0]).group(1)


def _afirma_formulario_de_edicao(resposta):
    """EDEX-01: 200, titulo "Editar inovação" e exatamente os sete campos."""
    assert resposta.status_code == 200
    assertTemplateUsed(resposta, "inovacoes/inovacao_form.html")
    html = resposta.content.decode()
    titulo = re.search(r"<title>(.*?)</title>", html, re.S).group(1).strip()
    assert titulo.startswith("Editar inovação")
    assert re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.S) == ["Editar inovação"]
    assert list(resposta.context["form"].fields) == CAMPOS
    nomes = re.findall(r'\bname="([^"]+)"', _formulario(html))
    assert sorted(set(nomes) - {"csrfmiddlewaretoken"}) == sorted(CAMPOS)
    for campo in ["autor", "status", "data_criacao"]:
        assert f'name="{campo}"' not in html


def _afirma_acesso_negado(resposta, inovacao):
    """EDEX-20, EDEX-21: 403 com a pagina propria, os dois textos e o link de volta."""
    assert resposta.status_code == 403
    assertTemplateUsed(resposta, "inovacoes/acesso_negado.html")
    html = resposta.content.decode()
    assert NEGADO in html
    assert SO_AUTOR in html
    links = re.findall(r'<a href="([^"]*)">\s*Voltar para a inovação\s*</a>', html)
    assert links == [f"/inovacoes/{inovacao.pk}/"]


def test_autor_abre_o_formulario_de_edicao_com_os_sete_campos(client, autor, criar_inovacao):
    """EDEX-01: autor USUARIO; o status fica de fora (F5)."""
    inovacao = criar_inovacao()
    resposta = _entrar(client, autor).get(_editar(inovacao))
    _afirma_formulario_de_edicao(resposta)
    assert re.findall(r"<button[^>]*>(.*?)</button>", _formulario(resposta.content.decode())) == [
        "Salvar alterações"
    ]


def test_formulario_vem_preenchido_com_os_valores_salvos(client, autor, criar_inovacao):
    """EDEX-02: inclusive o contato salvo, e nao o pre-preenchimento da INOV-39."""
    inovacao = criar_inovacao(
        resultado="Fechamento em duas horas.", contato="Setor Financeiro (fin@x.com)"
    )
    resposta = _entrar(client, autor).get(_editar(inovacao))
    form = resposta.context["form"]
    assert form.instance.pk == inovacao.pk
    assert {campo: form[campo].value() for campo in CAMPOS} == {
        "titulo": "Controle de Caixa",
        "unidade": inovacao.unidade_id,
        "categoria": inovacao.categoria_id,
        "problema": "Fechamento de caixa manual e demorado.",
        "solucao": "Planilha compartilhada com conferencia diaria.",
        "resultado": "Fechamento em duas horas.",
        "contato": "Setor Financeiro (fin@x.com)",
    }
    html = resposta.content.decode()
    assert 'value="Setor Financeiro (fin@x.com)"' in html
    # O pre-preenchimento da INOV-39 seria "Ana Souza (ana@x.com)" (a ajuda o cita como exemplo).
    assert 'value="Ana Souza (ana@x.com)"' not in html
    assert re.search(rf'<option value="{inovacao.unidade_id}" selected>', html)
    assert re.search(rf'<option value="{inovacao.categoria_id}" selected>', html)


def test_cancelar_leva_ao_detalhe_sem_alterar_a_inovacao(client, autor, criar_inovacao):
    """EDEX-16: link comum, sem confirmacao, para /inovacoes/<id>/."""
    inovacao = criar_inovacao()
    antes = Inovacao.objects.values().get(pk=inovacao.pk)
    logado = _entrar(client, autor)
    href = _link_cancelar(logado.get(_editar(inovacao)).content.decode())
    assert href == f"/inovacoes/{inovacao.pk}/"
    resposta = logado.get(href)
    assert resposta.status_code == 200
    assertTemplateUsed(resposta, "inovacoes/inovacao_detail.html")
    assert Inovacao.objects.values().get(pk=inovacao.pk) == antes


def test_administrador_abre_a_edicao_da_inovacao_de_outro_autor(
    client, administrador, criar_inovacao
):
    """EDEX-17."""
    inovacao = criar_inovacao()
    _afirma_formulario_de_edicao(_entrar(client, administrador).get(_editar(inovacao)))


def test_autor_administrador_abre_a_edicao(client, administrador, criar_inovacao):
    """EDEX-19: o autor com perfil ADMINISTRADOR edita como o autor USUARIO."""
    inovacao = criar_inovacao(autor=administrador)
    _afirma_formulario_de_edicao(_entrar(client, administrador).get(_editar(inovacao)))


def test_terceiro_recebe_403_com_a_pagina_de_acesso_negado(client, terceiro, criar_inovacao):
    """EDEX-20, EDEX-21: USUARIO que nao e o autor, pela barra de endereco."""
    inovacao = criar_inovacao()
    resposta = _entrar(client, terceiro).get(_editar(inovacao))
    _afirma_acesso_negado(resposta, inovacao)
    assert "form" not in resposta.context


def test_administrador_rebaixado_recebe_403_na_requisicao_seguinte(
    client, administrador, criar_inovacao
):
    """EDEX-25: o perfil e lido a cada requisicao, nunca guardado na sessao."""
    inovacao = criar_inovacao()
    logado = _entrar(client, administrador)
    assert logado.get(_editar(inovacao)).status_code == 200
    Usuario.objects.filter(pk=administrador.pk).update(perfil=Usuario.Perfil.USUARIO)
    _afirma_acesso_negado(logado.get(_editar(inovacao)), inovacao)


def test_id_sem_inovacao_responde_404_com_pagina_propria(client, autor):
    """EDEX-27 (GET): o 404 da CONS-15."""
    resposta = _entrar(client, autor).get("/inovacoes/999999/editar/")
    assert resposta.status_code == 404
    assertTemplateUsed(resposta, "inovacoes/inovacao_nao_encontrada.html")
    assert re.search(r"<h1[^>]*>\s*Inovação não encontrada\.\s*</h1>", resposta.content.decode())


@pytest.mark.django_db
def test_anonimo_vai_ao_login_com_next_da_edicao(client, criar_inovacao):
    """EDEX-26 (GET)."""
    inovacao = criar_inovacao()
    caminho = _editar(inovacao)
    resposta = client.get(caminho)
    assertRedirects(resposta, f"/entrar/?next={caminho}", fetch_redirect_response=False)
