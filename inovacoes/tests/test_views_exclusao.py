"""Testes e2e da confirmacao e da exclusao de inovacao (/inovacoes/<id>/excluir/)."""

import re

import pytest
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from contas.models import Usuario
from inovacoes.models import Inovacao
from inovacoes.tests.test_views_lista import _linhas

NEGADO = "Você não tem permissão para alterar esta inovação."
# T-1 (gestao-por-unidade, T4, GEST-52): a regra da EDEX-20 ganha o gestor da unidade de origem.
SO_AUTOR = (
    "Só quem cadastrou a inovação, um gestor da unidade de origem ou um administrador "
    "pode editá-la ou excluí-la."
)
AVISO = (
    "Você vai excluir a inovação “Controle de Caixa” (Teste Unidade · Teste Categoria). "
    "Esta ação não pode ser desfeita."
)


def _excluir(inovacao):
    return f"/inovacoes/{inovacao.pk}/excluir/"


def _entrar(client, conta):
    client.force_login(conta)
    return client


def _formulario_de_confirmacao(html):
    """O form POST da pagina, fora do cabecalho (que tem o form do "Sair")."""
    formularios = re.findall(r"<form\b([^>]*)>(.*?)</form>", html, re.S)
    com_botao = [f for f in formularios if "Excluir definitivamente" in f[1]]
    assert len(com_botao) == 1, formularios
    return com_botao[0]


def _afirma_confirmacao(resposta):
    """EDEX-30: 200, titulo "Excluir inovação" e o aviso com titulo, unidade e categoria."""
    assert resposta.status_code == 200
    assertTemplateUsed(resposta, "inovacoes/inovacao_confirm_delete.html")
    html = resposta.content.decode()
    titulo = re.search(r"<title>(.*?)</title>", html, re.S).group(1).strip()
    assert titulo.startswith("Excluir inovação")
    assert re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.S) == ["Excluir inovação"]
    assert AVISO in html


def _link_cancelar(html):
    links = re.findall(r"<a\b([^>]*)>\s*Cancelar\s*</a>", html)
    assert len(links) == 1, links
    return re.search(r'\bhref="([^"]*)"', links[0]).group(1)


def test_autor_ve_a_confirmacao_com_o_aviso(client, autor, criar_inovacao):
    """EDEX-30: autor USUARIO."""
    inovacao = criar_inovacao()
    _afirma_confirmacao(_entrar(client, autor).get(_excluir(inovacao)))


def test_administrador_ve_a_confirmacao_da_inovacao_de_outro_autor(
    client, administrador, criar_inovacao
):
    """EDEX-30: o administrador na inovacao da Ana."""
    inovacao = criar_inovacao()
    _afirma_confirmacao(_entrar(client, administrador).get(_excluir(inovacao)))


def test_autor_administrador_ve_a_confirmacao(client, administrador, criar_inovacao):
    """EDEX-19: o autor ADMINISTRADOR exclui como o autor USUARIO."""
    inovacao = criar_inovacao(autor=administrador)
    _afirma_confirmacao(_entrar(client, administrador).get(_excluir(inovacao)))


def test_confirmacao_tem_o_botao_que_envia_post_a_propria_rota(client, autor, criar_inovacao):
    """EDEX-32: botao "Excluir definitivamente" num form POST para /inovacoes/<id>/excluir/."""
    inovacao = criar_inovacao()
    html = _entrar(client, autor).get(_excluir(inovacao)).content.decode()
    atributos, corpo = _formulario_de_confirmacao(html)
    assert re.search(r'\bmethod="post"', atributos)
    acao = re.search(r'\baction="([^"]*)"', atributos)
    assert acao is None or acao.group(1) in ("", _excluir(inovacao))
    assert 'name="csrfmiddlewaretoken"' in corpo
    botoes = re.findall(r"<button\b([^>]*)>\s*(.*?)\s*</button>", corpo, re.S)
    assert [texto for _, texto in botoes] == ["Excluir definitivamente"]
    assert 'type="button"' not in botoes[0][0]


def test_cancelar_leva_ao_detalhe_e_a_inovacao_continua(client, autor, criar_inovacao):
    """EDEX-33, EDEX-34."""
    inovacao = criar_inovacao()
    logado = _entrar(client, autor)
    href = _link_cancelar(logado.get(_excluir(inovacao)).content.decode())
    assert href == f"/inovacoes/{inovacao.pk}/"
    resposta = logado.get(href)
    assert resposta.status_code == 200
    assertTemplateUsed(resposta, "inovacoes/inovacao_detail.html")
    assert Inovacao.objects.filter(pk=inovacao.pk).exists()


def test_get_na_exclusao_nunca_apaga_nem_repetido(client, autor, criar_inovacao):
    """EDEX-36: um link seguido por engano ou pre-carregado nao exclui."""
    inovacao = criar_inovacao()
    antes = Inovacao.objects.values().get(pk=inovacao.pk)
    logado = _entrar(client, autor)
    for _ in range(3):
        assert logado.get(_excluir(inovacao)).status_code == 200
    assert Inovacao.objects.values().get(pk=inovacao.pk) == antes


def test_terceiro_recebe_403_na_confirmacao(client, terceiro, criar_inovacao):
    """EDEX-20, EDEX-21: GET de um USUARIO que nao e o autor."""
    inovacao = criar_inovacao()
    resposta = _entrar(client, terceiro).get(_excluir(inovacao))
    assert resposta.status_code == 403
    assertTemplateUsed(resposta, "inovacoes/acesso_negado.html")
    html = resposta.content.decode()
    assert NEGADO in html
    assert SO_AUTOR in html
    assert re.findall(r'<a href="([^"]*)">\s*Voltar para a inovação\s*</a>', html) == [
        f"/inovacoes/{inovacao.pk}/"
    ]
    assert "Excluir definitivamente" not in html
    assert Inovacao.objects.filter(pk=inovacao.pk).exists()


def test_id_sem_inovacao_na_confirmacao_responde_404_com_pagina_propria(client, autor):
    """EDEX-28: o 404 da CONS-15."""
    resposta = _entrar(client, autor).get("/inovacoes/999999/excluir/")
    assert resposta.status_code == 404
    assertTemplateUsed(resposta, "inovacoes/inovacao_nao_encontrada.html")
    assert re.search(r"<h1[^>]*>\s*Inovação não encontrada\.\s*</h1>", resposta.content.decode())


# --- Exclusao definitiva (POST) ------------------------------------------------

SUCESSO = "Inovação “Controle de Caixa” excluída com sucesso."


def _regiao_de_status(html):
    inicio = html.index('role="status"')
    return html[inicio : html.index("</div>", inicio)]


def _afirma_pagina_nao_encontrada(resposta):
    assert resposta.status_code == 404
    assertTemplateUsed(resposta, "inovacoes/inovacao_nao_encontrada.html")


def test_autor_confirma_e_a_inovacao_sai_do_banco(client, autor, criar_inovacao):
    """EDEX-35, EDEX-37: 302 para /inovacoes/ e a linha nao existe mais."""
    inovacao = criar_inovacao()
    resposta = _entrar(client, autor).post(_excluir(inovacao))
    assertRedirects(resposta, "/inovacoes/", fetch_redirect_response=False)
    assert not Inovacao.objects.filter(pk=inovacao.pk).exists()


def test_inovacao_excluida_some_da_lista_da_busca_e_da_contagem(client, autor, criar_inovacao):
    """EDEX-37: listagem, busca pelo titulo e contagem da CONS-33."""
    inovacao = criar_inovacao()
    criar_inovacao(titulo="Planilha de Compras")
    logado = _entrar(client, autor)
    assert "2 inovações encontradas" in logado.get("/inovacoes/").content.decode()
    logado.post(_excluir(inovacao))
    lista = logado.get("/inovacoes/")
    assert [i.titulo for i in lista.context["inovacoes"]] == ["Planilha de Compras"]
    html = lista.content.decode()
    assert "1 inovação encontrada" in html
    # T-E (redesign-consulta, T9, RCON-10): os resultados sao os cartoes da lista, nao a
    # tabela; a garantia continua: a excluida nao aparece entre os resultados exibidos.
    assert [linha[0] for linha in _linhas(html)] == ["Planilha de Compras"]
    busca = logado.get("/inovacoes/?q=Controle de Caixa")
    assert list(busca.context["inovacoes"]) == []
    # T-R (redesign-consulta, T14, RCON-26): o texto do vazio sem resultado e o da §10.
    assert "Nenhuma inovação encontrada para esta busca." in busca.content.decode()


def test_exclusao_confirma_na_lista_uma_vez_so(client, autor, criar_inovacao):
    """EDEX-40: mensagem com o titulo excluido no role=status, e nao reaparece."""
    inovacao = criar_inovacao()
    logado = _entrar(client, autor)
    resposta = logado.post(_excluir(inovacao), follow=True)
    assert resposta.redirect_chain == [("/inovacoes/", 302)]
    assert SUCESSO in _regiao_de_status(resposta.content.decode())
    assert "excluída com sucesso" not in logado.get("/inovacoes/").content.decode()


def test_administrador_exclui_a_inovacao_de_outro_autor(client, administrador, criar_inovacao):
    """EDEX-35: o administrador na inovacao da Ana."""
    inovacao = criar_inovacao()
    resposta = _entrar(client, administrador).post(_excluir(inovacao))
    assertRedirects(resposta, "/inovacoes/", fetch_redirect_response=False)
    assert not Inovacao.objects.filter(pk=inovacao.pk).exists()


def test_autor_administrador_exclui(client, administrador, criar_inovacao):
    """EDEX-19: o autor ADMINISTRADOR exclui como o autor USUARIO."""
    inovacao = criar_inovacao(autor=administrador)
    resposta = _entrar(client, administrador).post(_excluir(inovacao))
    assertRedirects(resposta, "/inovacoes/", fetch_redirect_response=False)
    assert not Inovacao.objects.filter(pk=inovacao.pk).exists()


def test_segundo_envio_da_confirmacao_responde_404(client, autor, criar_inovacao):
    """EDEX-38: Voltar ou duplo clique recebem o 404 da CONS-15, nunca 500."""
    inovacao = criar_inovacao()
    logado = _entrar(client, autor)
    assert logado.post(_excluir(inovacao)).status_code == 302
    _afirma_pagina_nao_encontrada(logado.post(_excluir(inovacao)))


def test_detalhe_da_inovacao_excluida_responde_404(client, autor, criar_inovacao):
    """EDEX-39."""
    inovacao = criar_inovacao()
    logado = _entrar(client, autor)
    logado.post(_excluir(inovacao))
    _afirma_pagina_nao_encontrada(logado.get(f"/inovacoes/{inovacao.pk}/"))


def test_terceiro_que_envia_a_exclusao_recebe_403_e_a_inovacao_continua(
    client, terceiro, criar_inovacao
):
    """EDEX-23: o POST forjado de um USUARIO que nao e o autor nao apaga."""
    inovacao = criar_inovacao()
    antes = Inovacao.objects.values().get(pk=inovacao.pk)
    resposta = _entrar(client, terceiro).post(_excluir(inovacao))
    assert resposta.status_code == 403
    assertTemplateUsed(resposta, "inovacoes/acesso_negado.html")
    assert NEGADO in resposta.content.decode()
    assert Inovacao.objects.values().get(pk=inovacao.pk) == antes


def test_administrador_rebaixado_nao_exclui_a_inovacao_de_outro_autor(
    client, administrador, criar_inovacao
):
    """EDEX-25: o perfil e lido na requisicao do POST."""
    inovacao = criar_inovacao()
    logado = _entrar(client, administrador)
    assert logado.get(_excluir(inovacao)).status_code == 200
    Usuario.objects.filter(pk=administrador.pk).update(perfil=Usuario.Perfil.USUARIO)
    resposta = logado.post(_excluir(inovacao))
    assert resposta.status_code == 403
    assertTemplateUsed(resposta, "inovacoes/acesso_negado.html")
    assert Inovacao.objects.filter(pk=inovacao.pk).exists()


@pytest.mark.django_db
def test_anonimo_que_envia_a_exclusao_vai_ao_login_e_a_inovacao_continua(client, criar_inovacao):
    """EDEX-26 (POST e GET)."""
    inovacao = criar_inovacao()
    caminho = _excluir(inovacao)
    for metodo in (client.get, client.post):
        resposta = metodo(caminho)
        assertRedirects(resposta, f"/entrar/?next={caminho}", fetch_redirect_response=False)
    assert Inovacao.objects.filter(pk=inovacao.pk).exists()
