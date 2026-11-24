"""Testes da unidade pre-preenchida no cadastro e no reaproveitamento.

gestao-por-unidade, T15: derivados das ACs GEST-55 a GEST-60
(.specs/features/gestao-por-unidade/spec.md). O select e lido do exibido rigoroso
(L-028, L-030): um select desabilitado sairia dele.
"""

import re

import pytest

from inovacoes.forms import ReaproveitamentoForm
from inovacoes.models import Inovacao, StatusInovacao, Unidade
from inovacoes.tests.visibilidade import exibido

DISPONIVEL = StatusInovacao.DISPONIVEL_PARA_REPLICACAO


def _opcoes(html):
    """(valor, texto, selecionada) de cada <option> do select "unidade" exibido."""
    tela = exibido(html, rigoroso=True)
    select = re.search(r'<select name="unidade"[^>]*>(.*?)</select>', tela, re.S)
    assert select, "o select de unidade precisa estar exibido e editavel"
    return [
        (valor, texto, " selected" in atributos)
        for valor, atributos, texto in re.findall(
            r'<option value="([^"]*)"([^>]*)>([^<]*)</option>', select.group(1)
        )
    ]


def _selecionadas(opcoes):
    """As unidades escolhidas: a opcao vazia ("Selecione…") nao e unidade."""
    return [texto for valor, texto, selecionada in opcoes if selecionada and valor]


@pytest.fixture
def sede(db):
    return Unidade.objects.get(nome="Sede")


@pytest.fixture
def autor_da_sede(autor, sede):
    autor.unidade = sede
    autor.save()
    return autor


@pytest.fixture
def logado(client, autor_da_sede):
    client.force_login(autor_da_sede)
    return client


# --- Cadastro ---


def test_cadastro_vem_com_a_unidade_do_usuario_e_editavel(logado):
    """GEST-55: "Sede" selecionada; as outras unidades seguem no select."""
    resposta = logado.get("/inovacoes/nova/")
    opcoes = _opcoes(resposta.content.decode())
    assert _selecionadas(opcoes) == ["Sede"]
    assert {"Filial Norte", "Filial Sul"} <= {texto for _, texto, _ in opcoes}


def test_cadastro_grava_a_unidade_escolhida_no_formulario(logado, unidade, categoria):
    """GEST-57: o usuario da Sede cadastra para outra unidade; vale a escolhida."""
    resposta = logado.post(
        "/inovacoes/nova/",
        {
            "titulo": "Triagem de chamados",
            "unidade": str(unidade.pk),
            "categoria": str(categoria.pk),
            "problema": "Chamados sem prioridade.",
            "solucao": "Fila por gravidade.",
            "contato": "Ana Souza (ana@x.com)",
        },
    )
    assert resposta.status_code == 302
    assert Inovacao.objects.get(titulo="Triagem de chamados").unidade == unidade


def test_cadastro_sem_unidade_do_usuario_vem_em_selecione(client, autor):
    """GEST-56: como hoje (INOV-15), nada selecionado e "Selecione…" primeiro."""
    client.force_login(autor)
    opcoes = _opcoes(client.get("/inovacoes/nova/").content.decode())
    assert opcoes[0][:2] == ("", "Selecione…")
    assert _selecionadas(opcoes) == []


def test_edicao_mostra_a_unidade_da_inovacao_e_nao_a_do_usuario(logado, criar_inovacao):
    """GEST-58: a inovacao e da "Teste Unidade"; o autor e da Sede."""
    inovacao = criar_inovacao()
    opcoes = _opcoes(logado.get(f"/inovacoes/{inovacao.pk}/editar/").content.decode())
    assert _selecionadas(opcoes) == ["Teste Unidade"]


# --- Reaproveitamento ---


def test_reaproveitamento_vem_com_a_unidade_elegivel_do_usuario(logado, criar_inovacao):
    """GEST-59: a inovacao e da "Teste Unidade"; a Sede e elegivel e vem escolhida."""
    inovacao = criar_inovacao(status=DISPONIVEL)
    opcoes = _opcoes(logado.get(f"/inovacoes/{inovacao.pk}/reaproveitar/").content.decode())
    assert _selecionadas(opcoes) == ["Sede"]


@pytest.mark.parametrize("caso", ["origem", "ja_reaproveitou"])
def test_reaproveitamento_sem_selecao_quando_a_unidade_nao_e_elegivel(
    logado, autor_da_sede, sede, criar_inovacao, caso
):
    """GEST-60: a unidade do usuario e a de origem ou ja sinalizou: nada selecionado."""
    if caso == "origem":
        inovacao = criar_inovacao(status=DISPONIVEL, unidade=sede)
    else:
        inovacao = criar_inovacao(status=DISPONIVEL)
        inovacao.registrar_reaproveitamento(unidade=sede, por=autor_da_sede)
    opcoes = _opcoes(logado.get(f"/inovacoes/{inovacao.pk}/reaproveitar/").content.decode())
    assert "Sede" not in {texto for _, texto, _ in opcoes}
    assert _selecionadas(opcoes) == []


@pytest.mark.django_db
def test_formulario_sem_unidade_sugerida_igual_a_hoje(criar_inovacao, sede):
    """GEST-59, GEST-60: sem o argumento, sem initial e sem selecao; com a Sede
    elegivel, ela vira o initial do campo; com a origem, nao."""
    inovacao = criar_inovacao(status=DISPONIVEL)
    sem = ReaproveitamentoForm(inovacao=inovacao)
    assert sem.initial == {}
    assert re.findall(r'<option value="([^"]*)" selected>', str(sem["unidade"])) == [""]
    com = ReaproveitamentoForm(inovacao=inovacao, unidade_sugerida=sede.pk)
    assert com.initial == {"unidade": sede.pk}
    origem = ReaproveitamentoForm(inovacao=inovacao, unidade_sugerida=inovacao.unidade_id)
    assert origem.initial == {}
