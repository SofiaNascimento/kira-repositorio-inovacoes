"""Testes e2e da sinalizacao de reaproveitamento (/inovacoes/<id>/reaproveitar/).

Os registros de preparo nascem pelo metodo do modelo (AD-012).
"""

import re

import pytest
from django.db import OperationalError
from django.test import Client
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from inovacoes.models import Inovacao, Reaproveitamento, StatusInovacao, Unidade
from inovacoes.tests.visibilidade import exibido
from inovacoes.views import InovacaoReaproveitarView

EM_TESTE = StatusInovacao.EM_TESTE
VALIDADA = StatusInovacao.VALIDADA
DISPONIVEL = StatusInovacao.DISPONIVEL_PARA_REPLICACAO

TODAS_SINALIZARAM = "Todas as outras unidades já sinalizaram o reaproveitamento desta inovação."


def _aviso_de_status(rotulo):
    return (
        "Só uma inovação “Disponível para replicação” pode ser sinalizada como reaproveitada. "
        f"Status atual: “{rotulo}”."
    )


def _reaproveitar(inovacao):
    return f"/inovacoes/{inovacao.pk}/reaproveitar/"


def _entrar(client, conta):
    client.force_login(conta)
    return client


def _conteudo(html):
    """O <main> da pagina: o cabecalho tem o form e o botao do "Sair"."""
    return html[html.index('<main id="conteudo">') : html.index("</main>")]


def _mensagens(html):
    """Itens da regiao role="status" do base, com o nivel de cada um."""
    mensagens = _mensagens_no(html)
    assert mensagens is not None, "sem a regiao role=status"
    # L-028, L-030: a regiao e cada mensagem ficam na tela e no leitor de tela.
    assert _mensagens_no(exibido(html)) == mensagens
    return mensagens


def _mensagens_no(html):
    if '<div role="status">' not in html:
        return None
    inicio = html.index('<div role="status">')
    regiao = html[inicio : html.index("</div>", inicio)]
    return re.findall(r'<li class="alerta alerta--(\w+)">(.*?)</li>', regiao, re.S)


def _opcoes(html):
    """Textos das <option> com valor do select "unidade"."""
    select = re.search(r'<select name="unidade"[^>]*>(.*?)</select>', html, re.S).group(1)
    return re.findall(r'<option value="[^"]+"[^>]*>([^<]*)</option>', select)


@pytest.fixture
def disponivel(criar_inovacao):
    return criar_inovacao(status=DISPONIVEL)


# --- Formulario (GET) -----------------------------------------------------------


def test_get_mostra_o_formulario_de_sinalizacao(client, autor, disponivel):
    """REAP-03: titulo, texto com inovacao e origem, select rotulado, botao e Cancelar."""
    resposta = _entrar(client, autor).get(_reaproveitar(disponivel))
    assert resposta.status_code == 200
    assertTemplateUsed(resposta, "inovacoes/inovacao_reaproveitar.html")
    html = resposta.content.decode()
    titulo = re.search(r"<title>(.*?)</title>", html, re.S).group(1).strip()
    assert titulo.startswith("Sinalizar reaproveitamento")
    conteudo = _conteudo(html)
    # L-028, L-030: nada do <main>, formulario incluido, sai da tela ou do leitor de tela.
    assert _conteudo(exibido(html)) == conteudo
    assert (
        "Registre a unidade que reaproveitou a inovação “Controle de Caixa”, "
        "criada na unidade “Teste Unidade”."
    ) in conteudo
    select = re.search(r"<select\b([^>]*)>", conteudo).group(1)
    assert 'name="unidade"' in select
    assert re.search(r"\brequired\b", select)
    id_select = re.search(r'\bid="([^"]+)"', select).group(1)
    assert re.findall(rf'<label for="{id_select}">([^<]*)</label>', conteudo) == [
        "Unidade que reaproveitou"
    ]
    formulario = re.search(r"<form\b([^>]*)>(.*?)</form>", conteudo, re.S)
    assert re.search(r'\bmethod="post"', formulario.group(1))
    corpo = formulario.group(2)
    assert 'name="csrfmiddlewaretoken"' in corpo
    botoes = re.findall(r"<button\b([^>]*)>\s*(.*?)\s*</button>", corpo, re.S)
    assert [texto for _, texto in botoes] == ["Sinalizar reaproveitamento"]
    assert 'type="submit"' in botoes[0][0]
    cancelar = re.findall(r'<a href="([^"]*)">\s*Cancelar\s*</a>', corpo)
    assert cancelar == [f"/inovacoes/{disponivel.pk}/"]


def test_select_oferece_so_as_unidades_elegiveis_em_ordem(client, autor, disponivel):
    """REAP-04: sem a origem e sem as ja registradas, em ordem alfabetica."""
    Unidade.objects.create(nome="Almoxarifado")
    disponivel.registrar_reaproveitamento(
        unidade=Unidade.objects.get(nome="Filial Norte"), por=autor
    )
    html = _entrar(client, autor).get(_reaproveitar(disponivel)).content.decode()
    elegiveis = ["Almoxarifado", "Filial Leste", "Filial Oeste", "Filial Sul", "Sede"]
    assert _opcoes(html) == elegiveis
    # L-028, L-030: o select e cada opcao ficam na tela e no leitor de tela.
    assert _opcoes(exibido(html)) == elegiveis


def test_get_nunca_cria_reaproveitamento(client, autor, disponivel):
    """REAP-08: um link seguido ou pre-carregado nao registra nada."""
    logado = _entrar(client, autor)
    for _ in range(3):
        assert logado.get(_reaproveitar(disponivel)).status_code == 200
    assert Reaproveitamento.objects.count() == 0


@pytest.mark.parametrize(("status", "rotulo"), [(EM_TESTE, "Em teste"), (VALIDADA, "Validada")])
def test_get_fora_de_disponivel_volta_ao_detalhe_com_aviso(
    client, autor, criar_inovacao, status, rotulo
):
    """REAP-09 (GET): 302 ao detalhe, o aviso uma vez e nada gravado."""
    inovacao = criar_inovacao(status=status)
    logado = _entrar(client, autor)
    resposta = logado.get(_reaproveitar(inovacao), follow=True)
    assert resposta.redirect_chain == [(f"/inovacoes/{inovacao.pk}/", 302)]
    assertTemplateUsed(resposta, "inovacoes/inovacao_detail.html")
    assert _mensagens(resposta.content.decode()) == [("warning", _aviso_de_status(rotulo))]
    assert _mensagens(logado.get(f"/inovacoes/{inovacao.pk}/").content.decode()) == []
    assert Reaproveitamento.objects.count() == 0


def _afirma_sem_elegiveis(resposta, inovacao):
    assert resposta.status_code == 200
    conteudo = _conteudo(resposta.content.decode())
    # L-028, L-030: o texto e o link ficam na tela e no leitor de tela.
    assert _conteudo(exibido(resposta.content.decode())) == conteudo
    assert TODAS_SINALIZARAM in conteudo
    voltar = re.findall(r'<a href="([^"]*)">\s*Voltar para a inovação\s*</a>', conteudo)
    assert voltar == [f"/inovacoes/{inovacao.pk}/"]
    assert "<select" not in conteudo
    assert "<button" not in conteudo


def test_todas_as_outras_unidades_ja_sinalizaram(client, autor, unidade, disponivel):
    """REAP-15: a pagina explica, sem select nem botao."""
    for outra in Unidade.objects.exclude(pk=unidade.pk):
        disponivel.registrar_reaproveitamento(unidade=outra, por=autor)
    resposta = _entrar(client, autor).get(_reaproveitar(disponivel))
    _afirma_sem_elegiveis(resposta, disponivel)


def test_so_existe_a_unidade_de_origem(client, autor, unidade, disponivel):
    """REAP-15: nenhuma outra unidade cadastrada."""
    Unidade.objects.exclude(pk=unidade.pk).delete()
    assert list(Unidade.objects.all()) == [unidade]
    resposta = _entrar(client, autor).get(_reaproveitar(disponivel))
    _afirma_sem_elegiveis(resposta, disponivel)


def test_id_sem_inovacao_responde_404_com_pagina_propria(client, autor):
    """REAP-16 (GET): o 404 da CONS-15."""
    resposta = _entrar(client, autor).get("/inovacoes/999999/reaproveitar/")
    assert resposta.status_code == 404
    assertTemplateUsed(resposta, "inovacoes/inovacao_nao_encontrada.html")
    assert re.search(r"<h1[^>]*>\s*Inovação não encontrada\.\s*</h1>", resposta.content.decode())
    # L-028, L-030: o titulo fica na tela e no leitor de tela.
    visivel = exibido(resposta.content.decode())
    assert re.search(r"<h1[^>]*>\s*Inovação não encontrada\.\s*</h1>", visivel)


def _afirma_formulario_aberto(resposta):
    assert resposta.status_code == 200
    assertTemplateUsed(resposta, "inovacoes/inovacao_reaproveitar.html")
    assert '<select name="unidade"' in resposta.content.decode()
    # L-028, L-030: nada do <main>, formulario incluido, sai da tela ou do leitor de tela.
    html = resposta.content.decode()
    assert _conteudo(exibido(html)) == _conteudo(html)


def test_usuario_que_nao_e_o_autor_abre_o_formulario(client, disponivel, nao_autor_usuario):
    """REAP-19 (GET): USUARIO comum, com is_staff e com is_superuser; nunca 403."""
    _afirma_formulario_aberto(_entrar(client, nao_autor_usuario).get(_reaproveitar(disponivel)))


def test_administrador_abre_o_formulario(client, disponivel, administrador):
    """REAP-19 (GET): o administrador, sem ser o autor."""
    _afirma_formulario_aberto(_entrar(client, administrador).get(_reaproveitar(disponivel)))


# --- Registro (POST) ------------------------------------------------------------

ORIGEM = "A unidade de origem não pode reaproveitar a própria inovação."
SELECIONE = "Selecione a unidade que reaproveitou a inovação."


def _repetida(nome):
    return f"A unidade “{nome}” já sinalizou o reaproveitamento desta inovação."


def _sucesso(nome):
    return f"Reaproveitamento da inovação “Controle de Caixa” pela unidade “{nome}” registrado."


def _erros_do_select(html):
    """Mensagens da lista de erro ligada ao select (id_unidade_error)."""
    lista = re.search(r'<ul class="errorlist" id="id_unidade_error">(.*?)</ul>', html, re.S)
    assert lista, "sem lista de erro do select"
    return re.findall(r"<li>(.*?)</li>", lista.group(1), re.S)


def _afirma_formulario_com_erro(resposta, mensagem):
    """REAP-11 a REAP-13: 200, o formulario refeito e o erro junto do select."""
    assert resposta.status_code == 200
    assertTemplateUsed(resposta, "inovacoes/inovacao_reaproveitar.html")
    conteudo = _conteudo(resposta.content.decode())
    assert '<select name="unidade"' in conteudo
    assert _erros_do_select(conteudo) == [mensagem]
    # L-028, L-030: o select e o erro ficam na tela e no leitor de tela.
    assert _conteudo(exibido(resposta.content.decode())) == conteudo


@pytest.fixture
def sede(db):
    return Unidade.objects.get(nome="Sede")


def test_post_com_unidade_elegivel_registra_e_volta_ao_detalhe(client, terceiro, disponivel, sede):
    """REAP-05: um registro com a unidade, a conta logada e a hora; 302 ao detalhe."""
    resposta = _entrar(client, terceiro).post(_reaproveitar(disponivel), {"unidade": sede.pk})
    assert resposta.status_code == 302
    assert resposta["Location"] == f"/inovacoes/{disponivel.pk}/"
    registro = Reaproveitamento.objects.get()
    assert registro.inovacao_id == disponivel.pk
    assert registro.unidade_id == sede.pk
    assert registro.registrado_por_id == terceiro.pk
    assert registro.data is not None


def test_mensagem_de_sucesso_aparece_uma_vez(client, autor, disponivel, sede):
    """REAP-06: o detalhe seguido mostra a mensagem, e o seguinte nao a repete."""
    logado = _entrar(client, autor)
    resposta = logado.post(_reaproveitar(disponivel), {"unidade": sede.pk}, follow=True)
    assert resposta.redirect_chain == [(f"/inovacoes/{disponivel.pk}/", 302)]
    assertTemplateUsed(resposta, "inovacoes/inovacao_detail.html")
    assert _mensagens(resposta.content.decode()) == [("success", _sucesso("Sede"))]
    recarregado = logado.get(f"/inovacoes/{disponivel.pk}/").content.decode()
    assert _mensagens(recarregado) == []
    assert _sucesso("Sede") not in recarregado


@pytest.mark.parametrize(("status", "rotulo"), [(EM_TESTE, "Em teste"), (VALIDADA, "Validada")])
def test_post_fora_de_disponivel_volta_ao_detalhe_com_aviso(
    client, autor, criar_inovacao, sede, status, rotulo
):
    """REAP-09 (POST): 302, o aviso uma vez e nada gravado."""
    inovacao = criar_inovacao(status=status)
    resposta = _entrar(client, autor).post(
        _reaproveitar(inovacao), {"unidade": sede.pk}, follow=True
    )
    assert resposta.redirect_chain == [(f"/inovacoes/{inovacao.pk}/", 302)]
    assert _mensagens(resposta.content.decode()) == [("warning", _aviso_de_status(rotulo))]
    assert Reaproveitamento.objects.count() == 0


def test_post_com_a_unidade_de_origem_e_recusado(client, autor, unidade, disponivel):
    """REAP-11: POST forjado com a origem; erro de campo e nada gravado."""
    resposta = _entrar(client, autor).post(_reaproveitar(disponivel), {"unidade": unidade.pk})
    _afirma_formulario_com_erro(resposta, ORIGEM)
    assert Reaproveitamento.objects.count() == 0


def test_post_com_unidade_ja_registrada_e_recusado(client, autor, disponivel, sede):
    """REAP-12: o erro cita a unidade, e o registro continua um so."""
    disponivel.registrar_reaproveitamento(unidade=sede, por=autor)
    resposta = _entrar(client, autor).post(_reaproveitar(disponivel), {"unidade": sede.pk})
    _afirma_formulario_com_erro(resposta, _repetida("Sede"))
    assert Reaproveitamento.objects.count() == 1


@pytest.mark.parametrize("valor", ["", "999999", "abc"])
def test_post_sem_unidade_valida_e_recusado(client, autor, disponivel, valor):
    """REAP-13: vazio, id inexistente e nao numerico; a mesma mensagem."""
    resposta = _entrar(client, autor).post(_reaproveitar(disponivel), {"unidade": valor})
    _afirma_formulario_com_erro(resposta, SELECIONE)
    assert Reaproveitamento.objects.count() == 0


def test_corrida_na_mesma_unidade_termina_no_erro_de_repetida(
    client, autor, terceiro, disponivel, sede, monkeypatch
):
    """REAP-14: outra sinalizacao grava entre a validacao e o metodo; nunca 500."""
    original = InovacaoReaproveitarView.form_valid

    def outra_conexao_grava_antes(self, form):
        disponivel.registrar_reaproveitamento(unidade=sede, por=terceiro)
        return original(self, form)

    monkeypatch.setattr(InovacaoReaproveitarView, "form_valid", outra_conexao_grava_antes)
    resposta = _entrar(client, autor).post(_reaproveitar(disponivel), {"unidade": sede.pk})
    _afirma_formulario_com_erro(resposta, _repetida("Sede"))
    assert Reaproveitamento.objects.get().registrado_por_id == terceiro.pk


def test_inovacao_excluida_durante_o_envio_responde_404(
    client, autor, disponivel, sede, monkeypatch
):
    """REAP-16 (POST): apagada entre o dispatch() e o metodo; nada gravado."""
    original = InovacaoReaproveitarView.form_valid

    def apagar_antes(self, form):
        Inovacao.objects.filter(pk=disponivel.pk).delete()
        return original(self, form)

    monkeypatch.setattr(InovacaoReaproveitarView, "form_valid", apagar_antes)
    resposta = _entrar(client, autor).post(_reaproveitar(disponivel), {"unidade": sede.pk})
    assert resposta.status_code == 404
    assertTemplateUsed(resposta, "inovacoes/inovacao_nao_encontrada.html")
    assert Reaproveitamento.objects.count() == 0


def test_post_ignora_responsavel_data_e_inovacao_forjados(
    client, autor, terceiro, criar_inovacao, disponivel, sede
):
    """REAP-22: so a unidade vem do corpo; o resto e da sessao e do servidor."""
    outra = criar_inovacao(titulo="Outra Inovacao", status=DISPONIVEL)
    resposta = _entrar(client, terceiro).post(
        _reaproveitar(disponivel),
        {
            "unidade": sede.pk,
            "registrado_por": autor.pk,
            "data": "2001-01-01T00:00:00",
            "inovacao": outra.pk,
        },
    )
    assert resposta.status_code == 302
    registro = Reaproveitamento.objects.get()
    assert registro.registrado_por_id == terceiro.pk
    assert registro.inovacao_id == disponivel.pk
    assert registro.data.year != 2001


def test_usuario_que_nao_e_o_autor_registra(client, disponivel, sede, nao_autor_usuario):
    """REAP-19 (POST): USUARIO comum, com is_staff e com is_superuser; nunca 403."""
    resposta = _entrar(client, nao_autor_usuario).post(
        _reaproveitar(disponivel), {"unidade": sede.pk}
    )
    assert resposta.status_code == 302
    assert Reaproveitamento.objects.get().registrado_por_id == nao_autor_usuario.pk


def test_administrador_registra(client, disponivel, sede, administrador):
    """REAP-19 (POST): o administrador, sem ser o autor."""
    resposta = _entrar(client, administrador).post(_reaproveitar(disponivel), {"unidade": sede.pk})
    assert resposta.status_code == 302
    assert Reaproveitamento.objects.get().registrado_por_id == administrador.pk


# --- Acesso e integridade (REAP-20, REAP-21, REAP-23, REAP-49) --------------------


@pytest.mark.parametrize("metodo", ["get", "post"])
def test_anonimo_vai_para_o_login_com_next(client, disponivel, sede, metodo):
    """REAP-20: GET e POST anonimos levam ao login, e nada e gravado."""
    caminho = _reaproveitar(disponivel)
    if metodo == "get":
        resposta = client.get(caminho)
    else:
        resposta = client.post(caminho, {"unidade": sede.pk})
    assertRedirects(resposta, f"/entrar/?next={caminho}", fetch_redirect_response=False)
    assert Reaproveitamento.objects.count() == 0


@pytest.mark.parametrize("conta", ["autor", "terceiro"])
def test_post_sem_token_csrf_e_recusado(request, disponivel, sede, conta):
    """REAP-21: o autor e um terceiro, com unidade elegivel e sem token: 403, nada gravado."""
    cliente = Client(enforce_csrf_checks=True)
    cliente.force_login(request.getfixturevalue(conta))
    resposta = cliente.post(_reaproveitar(disponivel), {"unidade": sede.pk})
    assert resposta.status_code == 403
    assert Reaproveitamento.objects.count() == 0


def test_excluir_a_inovacao_pela_rota_apaga_os_reaproveitamentos_dela(
    client, autor, terceiro, criar_inovacao, disponivel, sede
):
    """REAP-23: a exclusao da F4 leva os registros da inovacao, e so os dela."""
    outra = criar_inovacao(titulo="Outra Inovacao", status=DISPONIVEL)
    filial = Unidade.objects.get(nome="Filial Norte")
    disponivel.registrar_reaproveitamento(unidade=sede, por=autor)
    disponivel.registrar_reaproveitamento(unidade=filial, por=terceiro)
    da_outra = outra.registrar_reaproveitamento(unidade=sede, por=terceiro)
    resposta = _entrar(client, autor).post(f"/inovacoes/{disponivel.pk}/excluir/")
    assert resposta.status_code == 302
    assert not Inovacao.objects.filter(pk=disponivel.pk).exists()
    assert list(Reaproveitamento.objects.values_list("pk", flat=True)) == [da_outra.pk]


DETALHE_DA_CONEXAO = (
    'connection to server at "db.interno.kira" (10.0.0.7), port 5433 failed: '
    'FATAL: password authentication failed for user "kira_app" password=s3gr3d0-do-banco'
)


def test_banco_indisponivel_no_registro_devolve_500_sem_gravar(
    client, autor, disponivel, sede, monkeypatch
):
    """REAP-49: o banco cai no INSERT do metodo; pagina 500 do projeto, sem detalhes."""

    def falhar(*args, **kwargs):
        raise OperationalError(DETALHE_DA_CONEXAO)

    monkeypatch.setattr(Reaproveitamento.objects, "create", falhar)
    logado = _entrar(client, autor)
    logado.raise_request_exception = False
    resposta = logado.post(_reaproveitar(disponivel), {"unidade": sede.pk})
    assert resposta.status_code == 500
    assertTemplateUsed(resposta, "500.html")
    html = resposta.content.decode()
    for trecho in ["db.interno.kira", "kira_app", "s3gr3d0-do-banco", "Traceback"]:
        assert trecho not in html, trecho
    assert DETALHE_DA_CONEXAO not in html
    monkeypatch.undo()
    assert Reaproveitamento.objects.count() == 0
