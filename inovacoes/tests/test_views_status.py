"""Testes e2e da confirmacao e do avanco de status (/inovacoes/<id>/status/)."""

import re

import pytest
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from inovacoes.models import Inovacao, MudancaDeStatus, StatusInovacao
from inovacoes.views import InovacaoStatusView

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


# --- Avanco do status (POST) ---------------------------------------------------


def _conflito(rotulo):
    return (
        f"O status desta inovação já foi alterado para “{rotulo}”. "
        "Confira o status atual antes de avançar."
    )


def _sucesso(anterior, novo):
    return f"Status da inovação “Controle de Caixa” alterado de “{anterior}” para “{novo}”."


def _mensagens(html):
    """Itens da regiao role="status" do base, com o nivel de cada um."""
    inicio = html.index('<div role="status">')
    regiao = html[inicio : html.index("</div>", inicio)]
    return re.findall(r'<li class="alerta alerta--(\w+)">(.*?)</li>', regiao, re.S)


def _avancar(logado, inovacao, status_visto):
    dados = {} if status_visto is None else {"status_visto": status_visto}
    return logado.post(_status(inovacao), dados, follow=True)


def _afirma_volta_ao_detalhe(resposta, inovacao):
    assert resposta.redirect_chain == [(f"/inovacoes/{inovacao.pk}/", 302)]
    assertTemplateUsed(resposta, "inovacoes/inovacao_detail.html")


def test_autor_avanca_de_em_teste_para_validada(client, autor, criar_inovacao):
    """STAT-07, STAT-14, STAT-16, STAT-17: 302 ao detalhe, novo status, registro e mensagem."""
    inovacao = criar_inovacao()
    logado = _entrar(client, autor)
    resposta = logado.post(_status(inovacao), {"status_visto": EM_TESTE})
    assertRedirects(resposta, f"/inovacoes/{inovacao.pk}/", fetch_redirect_response=False)
    assert _status_no_banco(inovacao) == VALIDADA
    registro = MudancaDeStatus.objects.get()
    assert (registro.inovacao_id, registro.status_anterior, registro.status_novo) == (
        inovacao.pk,
        EM_TESTE,
        VALIDADA,
    )
    assert registro.responsavel == autor
    detalhe = logado.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert _mensagens(detalhe) == [("success", _sucesso("Em teste", "Validada"))]


def test_mensagem_de_sucesso_nao_reaparece_ao_recarregar(client, autor, criar_inovacao):
    """STAT-16: a mensagem aparece uma vez so."""
    inovacao = criar_inovacao()
    logado = _entrar(client, autor)
    resposta = _avancar(logado, inovacao, EM_TESTE)
    _afirma_volta_ao_detalhe(resposta, inovacao)
    assert _mensagens(resposta.content.decode()) == [("success", _sucesso("Em teste", "Validada"))]
    recarregado = logado.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert _mensagens(recarregado) == []
    assert "alterado de" not in recarregado


def test_autor_avanca_de_validada_para_disponivel(client, autor, criar_inovacao):
    """STAT-08, STAT-17: o segundo passo do ciclo."""
    inovacao = criar_inovacao(status=VALIDADA)
    resposta = _avancar(_entrar(client, autor), inovacao, VALIDADA)
    _afirma_volta_ao_detalhe(resposta, inovacao)
    assert _status_no_banco(inovacao) == DISPONIVEL
    registro = MudancaDeStatus.objects.get()
    assert (registro.status_anterior, registro.status_novo) == (VALIDADA, DISPONIVEL)
    assert _mensagens(resposta.content.decode()) == [
        ("success", _sucesso("Validada", "Disponível para replicação"))
    ]


def test_administrador_avanca_a_inovacao_de_outro_autor(
    client, autor, administrador, criar_inovacao
):
    """STAT-18: avanca, o autor continua e o administrador fica como responsavel."""
    inovacao = criar_inovacao()
    resposta = _avancar(_entrar(client, administrador), inovacao, EM_TESTE)
    _afirma_volta_ao_detalhe(resposta, inovacao)
    gravada = Inovacao.objects.get(pk=inovacao.pk)
    assert gravada.status == VALIDADA
    assert gravada.autor == autor
    assert MudancaDeStatus.objects.get().responsavel == administrador
    assert _mensagens(resposta.content.decode()) == [("success", _sucesso("Em teste", "Validada"))]


def test_envio_no_ultimo_estagio_avisa_e_nao_grava(client, autor, criar_inovacao):
    """STAT-10 (POST): status igual, nenhum registro e o aviso do estagio final."""
    inovacao = criar_inovacao(status=DISPONIVEL)
    resposta = _avancar(_entrar(client, autor), inovacao, DISPONIVEL)
    _afirma_volta_ao_detalhe(resposta, inovacao)
    assert _status_no_banco(inovacao) == DISPONIVEL
    assert MudancaDeStatus.objects.count() == 0
    assert _mensagens(resposta.content.decode()) == [("warning", ULTIMO_ESTAGIO)]


@pytest.mark.parametrize("status_visto", [None, VALIDADA, "APROVADA"])
def test_status_visto_ausente_ou_diferente_avisa_e_nao_grava(
    client, autor, criar_inovacao, status_visto
):
    """STAT-12: o aviso cita o status gravado; nada muda."""
    inovacao = criar_inovacao()
    resposta = _avancar(_entrar(client, autor), inovacao, status_visto)
    _afirma_volta_ao_detalhe(resposta, inovacao)
    assert _status_no_banco(inovacao) == EM_TESTE
    assert MudancaDeStatus.objects.count() == 0
    assert _mensagens(resposta.content.decode()) == [("warning", _conflito("Em teste"))]


def test_reenvio_da_mesma_confirmacao_avanca_um_estagio_so(client, autor, criar_inovacao):
    """STAT-13: duplo clique ou Voltar e reenviar."""
    inovacao = criar_inovacao()
    logado = _entrar(client, autor)
    _avancar(logado, inovacao, EM_TESTE)
    resposta = _avancar(logado, inovacao, EM_TESTE)
    _afirma_volta_ao_detalhe(resposta, inovacao)
    assert _status_no_banco(inovacao) == VALIDADA
    assert MudancaDeStatus.objects.count() == 1
    assert _mensagens(resposta.content.decode()) == [("warning", _conflito("Validada"))]


def test_status_mudado_durante_o_envio_avisa_e_nao_grava(
    client, autor, criar_inovacao, monkeypatch
):
    """STAT-13, mesma requisicao: outra pessoa avanca entre o dispatch() e a trava."""
    inovacao = criar_inovacao()
    post = InovacaoStatusView.post

    def avancar_antes(self, request, *args, **kwargs):
        Inovacao.objects.filter(pk=self.object.pk).update(status=VALIDADA)
        return post(self, request, *args, **kwargs)

    monkeypatch.setattr(InovacaoStatusView, "post", avancar_antes)
    resposta = _avancar(_entrar(client, autor), inovacao, EM_TESTE)
    _afirma_volta_ao_detalhe(resposta, inovacao)
    assert _status_no_banco(inovacao) == VALIDADA
    assert MudancaDeStatus.objects.count() == 0
    assert _mensagens(resposta.content.decode()) == [("warning", _conflito("Validada"))]


def test_inovacao_excluida_durante_o_envio_responde_404(client, autor, criar_inovacao, monkeypatch):
    """STAT-22, mesma requisicao: a linha some entre o dispatch() e a trava."""
    inovacao = criar_inovacao()
    post = InovacaoStatusView.post

    def apagar_antes(self, request, *args, **kwargs):
        Inovacao.objects.filter(pk=self.object.pk).delete()
        return post(self, request, *args, **kwargs)

    monkeypatch.setattr(InovacaoStatusView, "post", apagar_antes)
    resposta = _entrar(client, autor).post(_status(inovacao), {"status_visto": EM_TESTE})
    assert resposta.status_code == 404
    assertTemplateUsed(resposta, "inovacoes/inovacao_nao_encontrada.html")
    assert Inovacao.objects.count() == 0
    assert MudancaDeStatus.objects.count() == 0


def test_envio_para_id_sem_inovacao_responde_404(client, autor):
    """STAT-22 (POST): o 404 da CONS-15, sem registro."""
    resposta = _entrar(client, autor).post("/inovacoes/999999/status/", {"status_visto": EM_TESTE})
    assert resposta.status_code == 404
    assertTemplateUsed(resposta, "inovacoes/inovacao_nao_encontrada.html")
    assert MudancaDeStatus.objects.count() == 0
