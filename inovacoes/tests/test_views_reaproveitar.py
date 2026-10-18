"""Testes e2e da sinalizacao de reaproveitamento (/inovacoes/<id>/reaproveitar/).

Os registros de preparo nascem pelo metodo do modelo (AD-012).
"""

import re

import pytest
from pytest_django.asserts import assertTemplateUsed

from inovacoes.models import Reaproveitamento, StatusInovacao, Unidade

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
    assert _opcoes(html) == ["Almoxarifado", "Filial Leste", "Filial Oeste", "Filial Sul", "Sede"]


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


def _afirma_formulario_aberto(resposta):
    assert resposta.status_code == 200
    assertTemplateUsed(resposta, "inovacoes/inovacao_reaproveitar.html")
    assert '<select name="unidade"' in resposta.content.decode()


def test_usuario_que_nao_e_o_autor_abre_o_formulario(client, disponivel, nao_autor_usuario):
    """REAP-19 (GET): USUARIO comum, com is_staff e com is_superuser; nunca 403."""
    _afirma_formulario_aberto(_entrar(client, nao_autor_usuario).get(_reaproveitar(disponivel)))


def test_administrador_abre_o_formulario(client, disponivel, administrador):
    """REAP-19 (GET): o administrador, sem ser o autor."""
    _afirma_formulario_aberto(_entrar(client, administrador).get(_reaproveitar(disponivel)))
