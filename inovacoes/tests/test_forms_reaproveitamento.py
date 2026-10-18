"""Testes do formulario de sinalizacao de reaproveitamento, sem passar pela view.

Integracao: o select consulta as unidades e os reaproveitamentos no banco.
Os registros nascem pelo metodo do modelo (AD-012).
"""

import re

import pytest

from inovacoes.forms import ReaproveitamentoForm
from inovacoes.models import StatusInovacao, Unidade

MENSAGEM = "Selecione a unidade que reaproveitou a inovação."


@pytest.fixture
def inovacao(criar_inovacao):
    return criar_inovacao(status=StatusInovacao.DISPONIVEL_PARA_REPLICACAO)


def _opcoes(form):
    """(valor, texto, selecionada) de cada <option> do select renderizado."""
    return [
        (valor, texto, " selected" in atributos)
        for valor, atributos, texto in re.findall(
            r'<option value="([^"]*)"([^>]*)>([^<]*)</option>', str(form["unidade"])
        )
    ]


@pytest.mark.django_db
def test_opcoes_sao_as_elegiveis_em_ordem_alfabetica(inovacao, autor):
    """REAP-04: sem a origem e sem as ja registradas, por nome."""
    # Criada por ultimo, mas primeira no alfabeto: a ordem e do nome, nao do id.
    Unidade.objects.create(nome="Almoxarifado")
    norte = Unidade.objects.get(nome="Filial Norte")
    inovacao.registrar_reaproveitamento(unidade=norte, por=autor)

    form = ReaproveitamentoForm(inovacao=inovacao)

    campo = form.fields["unidade"]
    assert campo.label == "Unidade que reaproveitou"
    assert campo.required is True
    # A origem ("Teste Unidade") e a "Filial Norte" ficam de fora.
    assert [texto for _, texto, _ in _opcoes(form)[1:]] == [
        "Almoxarifado",
        "Filial Leste",
        "Filial Oeste",
        "Filial Sul",
        "Sede",
    ]


@pytest.mark.django_db
def test_primeira_opcao_e_a_vazia_e_nenhuma_unidade_vem_selecionada(inovacao):
    """REAP-04: o select abre sem escolha."""
    opcoes = _opcoes(ReaproveitamentoForm(inovacao=inovacao))
    assert opcoes[0][:2] == ("", "Selecione a unidade")
    assert [valor for valor, _, selecionada in opcoes if selecionada and valor] == []


@pytest.mark.django_db
def test_unidade_elegivel_e_valida(inovacao):
    sede = Unidade.objects.get(nome="Sede")
    form = ReaproveitamentoForm({"unidade": str(sede.pk)}, inovacao=inovacao)
    assert form.is_valid(), form.errors
    assert form.cleaned_data["unidade"] == sede


@pytest.mark.django_db
@pytest.mark.parametrize("caso", ["origem", "ja_registrada"])
def test_origem_e_ja_registrada_passam_pelo_form(inovacao, unidade, autor, caso):
    """REAP-11, REAP-12: a recusa e do metodo do modelo, com a mensagem especifica."""
    if caso == "origem":
        escolhida = unidade
    else:
        escolhida = Unidade.objects.get(nome="Sede")
        inovacao.registrar_reaproveitamento(unidade=escolhida, por=autor)
    form = ReaproveitamentoForm({"unidade": str(escolhida.pk)}, inovacao=inovacao)
    assert form.is_valid(), form.errors
    assert form.cleaned_data["unidade"] == escolhida


@pytest.mark.django_db
@pytest.mark.parametrize("valor", ["", "999999", "abc"])
def test_unidade_ausente_inexistente_ou_nao_numerica_e_invalida(inovacao, valor):
    """REAP-13: a mesma mensagem nos tres casos."""
    form = ReaproveitamentoForm({"unidade": valor}, inovacao=inovacao)
    assert not form.is_valid()
    assert form.errors == {"unidade": [MENSAGEM]}


@pytest.mark.django_db
def test_unidade_sinalizada_para_outra_inovacao_continua_elegivel(inovacao, criar_inovacao, autor):
    """REAP-04: a exclusao e por inovacao, nao por unidade."""
    outra = criar_inovacao(
        titulo="Outra Inovacao", status=StatusInovacao.DISPONIVEL_PARA_REPLICACAO
    )
    sul = Unidade.objects.get(nome="Filial Sul")
    outra.registrar_reaproveitamento(unidade=sul, por=autor)
    textos = [texto for _, texto, _ in _opcoes(ReaproveitamentoForm(inovacao=inovacao))]
    assert "Filial Sul" in textos
