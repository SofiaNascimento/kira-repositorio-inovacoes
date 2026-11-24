"""Testes do campo e do resumo de erros da §6 v2 (gestao-por-unidade, T7, GEST-68).

Derivados da GEST-68 (emenda E-2) e da §6 da docs/design-spec.md ("Campo de
formulário" e "Resumo de erros (v2)"), sobre um formulario de teste de dois
campos, sem banco.
"""

import re

import pytest
from django import forms
from django.template.loader import render_to_string

from inovacoes.tests.visibilidade import exibido
from nucleo.formularios import FormularioV2Mixin

pytestmark = pytest.mark.unit


class FormularioDeTeste(FormularioV2Mixin, forms.Form):
    nome = forms.CharField(label="Nome", help_text="Como a pessoa quer ser chamada.")
    apelido = forms.CharField(label="Apelido", required=False, help_text="Opcional.")
    email = forms.EmailField(label="E-mail")

    def clean(self):
        dados = super().clean()
        if dados.get("apelido") == "geral":
            raise forms.ValidationError("Erro sem campo.")
        return dados


def _campo(form, nome):
    return exibido(form[nome].as_field_group(), rigoroso=True)


def _resumo(form, acao="criar a conta"):
    return exibido(
        render_to_string("paginas/resumo_erros.html", {"form": form, "acao": acao}),
        rigoroso=True,
    )


def _texto(trecho):
    return " ".join(re.sub(r"<[^>]+>", " ", trecho).split())


def test_campo_com_erro_vem_na_ordem_rotulo_ajuda_campo_erro():
    """§6: rotulo -> ajuda -> campo -> erro."""
    form = FormularioDeTeste(data={"nome": "", "email": "a@x.com"})
    html = _campo(form, "nome")
    posicoes = [
        html.index('<label for="id_nome">'),
        html.index('id="id_nome_helptext"'),
        html.index('<input type="text" name="nome"'),
        html.index('id="id_nome_error"'),
    ]
    assert posicoes == sorted(posicoes)


@pytest.mark.parametrize(
    ("campo", "rotulo"),
    [("nome", "Nome (obrigatório)"), ("apelido", "Apelido")],
    ids=["obrigatorio", "opcional"],
)
def test_rotulo_diz_obrigatorio_por_escrito_sem_dois_pontos(campo, rotulo):
    """§6: "(obrigatório)" por escrito no rotulo do campo obrigatorio, e so nele."""
    html = _campo(FormularioDeTeste(), campo)
    label = re.search(rf'<label for="id_{campo}">(.*?)</label>', html, re.S).group(1)
    assert _texto(label) == rotulo


def test_campo_com_erro_tem_aria_invalid_e_descreve_erro_antes_da_ajuda():
    """§6: aria-invalid e aria-describedby="{erro} {ajuda}"."""
    form = FormularioDeTeste(data={"nome": "", "email": "a@x.com"})
    controle = re.search(r'<input type="text" name="nome"[^>]*>', _campo(form, "nome")).group(0)
    assert 'aria-invalid="true"' in controle
    assert 'aria-describedby="id_nome_error id_nome_helptext"' in controle


def test_campo_sem_erro_so_descreve_a_ajuda():
    """§6: sem erro, nem aria-invalid nem id de erro."""
    form = FormularioDeTeste(data={"nome": "Ana", "email": "a@x.com"})
    html = _campo(form, "nome")
    controle = re.search(r'<input type="text" name="nome"[^>]*>', html).group(0)
    assert "aria-invalid" not in controle
    assert 'aria-describedby="id_nome_helptext"' in controle
    assert "id_nome_error" not in html


@pytest.mark.parametrize(
    "dados",
    [None, {"nome": "Ana", "email": "a@x.com"}],
    ids=["sem_envio", "envio_valido"],
)
def test_sem_erro_nao_ha_resumo_no_dom(dados):
    """§6 v2: sem erro, o resumo nao existe no DOM."""
    form = FormularioDeTeste(data=dados)
    if dados:
        assert form.is_valid()
    assert _resumo(form).strip() == ""


def test_resumo_com_dois_erros_lista_os_campos_na_ordem_com_link():
    """GEST-68, §6 v2: titulo com a acao e o numero, um link por campo, na
    ordem do formulario, "{rotulo}: {mensagem}", role="alert" e tabindex="-1"."""
    form = FormularioDeTeste(data={"nome": "", "email": "nao-e-email"})
    assert not form.is_valid()
    html = _resumo(form)
    caixa = re.fullmatch(
        r'\s*<div class="resumo-erros" role="alert" tabindex="-1">(.*)</div>\s*', html, re.S
    )
    assert caixa
    titulo = re.search(r"<p>(.*?)</p>", caixa.group(1), re.S).group(1)
    assert titulo == "Não foi possível criar a conta. Corrija 2 campo(s):"
    itens = re.findall(r"<li>(.*?)</li>", caixa.group(1), re.S)
    assert itens == [
        '<a href="#id_nome">Nome: Este campo é obrigatório.</a>',
        '<a href="#id_email">E-mail: Informe um endereço de email válido.</a>',
    ]


def test_erro_sem_campo_entra_como_texto_sem_link():
    """§6 v2: o erro geral fica na lista, sem link, e nao conta como campo."""
    form = FormularioDeTeste(data={"nome": "", "apelido": "geral", "email": "a@x.com"})
    assert not form.is_valid()
    html = _resumo(form, acao="redefinir a senha")
    assert "Não foi possível redefinir a senha. Corrija 1 campo(s):" in html
    itens = re.findall(r"<li>(.*?)</li>", html, re.S)
    assert itens == ["Erro sem campo.", '<a href="#id_nome">Nome: Este campo é obrigatório.</a>']
