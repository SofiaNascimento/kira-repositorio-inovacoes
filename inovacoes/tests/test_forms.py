"""Testes do formulario de cadastro de inovacao, sem passar pela view.

Integracao: os campos de unidade e categoria consultam o banco.
"""

import pytest

from inovacoes.forms import InovacaoForm
from inovacoes.models import StatusInovacao

CAMPOS = ["titulo", "unidade", "categoria", "problema", "solucao", "resultado", "contato"]

MENSAGEM_OBRIGATORIO = {
    "titulo": "Informe o título da inovação.",
    "unidade": "Selecione a unidade de origem.",
    "categoria": "Selecione a categoria.",
    "problema": "Descreva o problema ou dor.",
    "solucao": "Descreva a solução aplicada.",
    "contato": "Informe o contato responsável.",
}

ROTULOS = {
    "titulo": "Título (obrigatório)",
    "unidade": "Unidade de origem (obrigatório)",
    "categoria": "Categoria (obrigatório)",
    "problema": "Problema ou dor (obrigatório)",
    "solucao": "Solução aplicada (obrigatório)",
    "resultado": "Resultado ou impacto",
    "contato": "Contato responsável (obrigatório)",
}


@pytest.fixture
def dados_validos(unidade, categoria):
    return {
        "titulo": "Conciliação bancária automática",
        "unidade": str(unidade.pk),
        "categoria": str(categoria.pk),
        "problema": "Conciliação manual levava dois dias por mês.",
        "solucao": "Script que cruza o extrato com os lançamentos.",
        "resultado": "Fechamento em duas horas.",
        "contato": "Ana Souza (ana@x.com)",
    }


def test_formulario_tem_exatamente_os_sete_campos_editaveis_na_ordem():
    """INOV-01."""
    assert list(InovacaoForm().fields) == CAMPOS


@pytest.mark.django_db
@pytest.mark.parametrize("campo", MENSAGEM_OBRIGATORIO)
def test_campo_obrigatorio_vazio_traz_a_sua_mensagem(dados_validos, campo):
    """INOV-09: a mensagem fica no campo vazio e diz como corrigir."""
    dados_validos[campo] = ""
    form = InovacaoForm(data=dados_validos)
    assert not form.is_valid()
    assert form.errors == {campo: [MENSAGEM_OBRIGATORIO[campo]]}


@pytest.mark.django_db
def test_campo_de_texto_so_com_espacos_conta_como_vazio(dados_validos):
    """INOV-10."""
    for campo in ["titulo", "problema", "solucao", "contato"]:
        dados_validos[campo] = "   \t  "
    form = InovacaoForm(data=dados_validos)
    assert not form.is_valid()
    assert form.errors == {
        campo: [MENSAGEM_OBRIGATORIO[campo]]
        for campo in ["titulo", "problema", "solucao", "contato"]
    }


@pytest.mark.django_db
def test_espacos_nas_pontas_sao_removidos(dados_validos):
    """INOV-02: todo campo de texto chega sem espacos nas pontas."""
    textos = ["titulo", "problema", "solucao", "resultado", "contato"]
    for campo in textos:
        dados_validos[campo] = f"  {dados_validos[campo]}  "
    form = InovacaoForm(data=dados_validos)
    assert form.is_valid(), form.errors
    for campo in textos:
        assert form.cleaned_data[campo] == dados_validos[campo].strip()


@pytest.mark.django_db
def test_resultado_vazio_e_aceito(dados_validos):
    """INOV-14."""
    dados_validos["resultado"] = ""
    form = InovacaoForm(data=dados_validos)
    assert form.is_valid(), form.errors
    assert form.cleaned_data["resultado"] == ""


@pytest.mark.django_db
def test_autor_status_e_data_enviados_sao_ignorados(dados_validos):
    """INOV-06: os campos do sistema nem sao lidos do cliente."""
    dados_validos.update(
        {"autor": "999", "status": StatusInovacao.VALIDADA, "data_criacao": "2020-01-01 00:00"}
    )
    form = InovacaoForm(data=dados_validos)
    assert form.is_valid(), form.errors
    assert not {"autor", "status", "data_criacao"} & set(form.cleaned_data)
    assert form.instance.autor_id is None
    assert form.instance.status == StatusInovacao.EM_TESTE
    assert form.instance.data_criacao is None


def test_rotulos_marcam_obrigatorio_so_nos_seis_campos_obrigatorios():
    """INOV-32: a obrigatoriedade esta no texto, nao so na cor."""
    form = InovacaoForm()
    assert {campo: form.fields[campo].label for campo in CAMPOS} == ROTULOS


LIMITES = {"titulo": 150, "contato": 150, "problema": 5000, "solucao": 5000, "resultado": 5000}


@pytest.mark.django_db
@pytest.mark.parametrize("campo", LIMITES)
def test_texto_acima_do_limite_informa_limite_e_tamanho_digitado(dados_validos, campo):
    """INOV-12: a mensagem traz o limite real e quanto a pessoa digitou."""
    limite = LIMITES[campo]
    dados_validos[campo] = "x" * (limite + 1)
    form = InovacaoForm(data=dados_validos)
    assert not form.is_valid()
    assert form.errors == {
        campo: [f"Use no máximo {limite} caracteres (você digitou {limite + 1})."]
    }


@pytest.mark.django_db
@pytest.mark.parametrize("campo", LIMITES)
def test_texto_exatamente_no_limite_e_aceito(dados_validos, campo):
    dados_validos[campo] = "x" * LIMITES[campo]
    form = InovacaoForm(data=dados_validos)
    assert form.is_valid(), form.errors
