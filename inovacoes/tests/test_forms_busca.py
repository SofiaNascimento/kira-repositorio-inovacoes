"""Testes do formulario de busca e filtros (BuscaForm), sem passar pela view.

Integracao: categoria e unidade consultam o banco.
"""

import re

import pytest

from inovacoes.forms import BuscaForm
from inovacoes.models import Categoria, StatusInovacao, Unidade

CAMPOS = ["q", "categoria", "unidade", "status"]

AJUDA = {
    "q": "Procura em título, problema e solução. Ex.: planilha conciliação",
    "categoria": "Área de back office. Ex.: Financeiro",
    "unidade": "Sede ou filial que criou a solução. Ex.: Filial Norte",
    "status": "Estágio da solução. Ex.: Disponível para replicação",
}

ROTULOS = {"q": "Buscar", "categoria": "Categoria", "unidade": "Unidade", "status": "Status"}


def test_formulario_tem_os_quatro_campos_na_ordem():
    """CONS-26, CONS-31: busca, categoria, unidade e status."""
    assert list(BuscaForm().fields) == CAMPOS


@pytest.mark.django_db
def test_formulario_vazio_e_valido_e_nao_filtra_nada():
    """CONS-21, CONS-26: sem parametros, nenhum filtro."""
    form = BuscaForm(data={})
    assert form.is_valid(), form.errors
    assert form.cleaned_data == {"q": "", "categoria": None, "unidade": None, "status": ""}


@pytest.mark.django_db
def test_busca_so_com_espacos_vira_vazia_e_espacos_nas_pontas_saem():
    """CONS-21: termo em branco nao filtra; as pontas sao aparadas."""
    em_branco = BuscaForm(data={"q": "   "})
    em_branco.is_valid()
    assert em_branco.cleaned_data["q"] == ""
    aparado = BuscaForm(data={"q": "  caixa  "})
    aparado.is_valid()
    assert aparado.cleaned_data["q"] == "caixa"


@pytest.mark.django_db
def test_filtros_validos_devolvem_o_registro_e_o_valor_do_status(unidade, categoria):
    """CONS-27, CONS-28: o form entrega o que o filtrar() espera."""
    form = BuscaForm(
        data={"categoria": str(categoria.pk), "unidade": str(unidade.pk), "status": "VALIDADA"}
    )
    assert form.is_valid(), form.errors
    assert form.cleaned_data["categoria"] == categoria
    assert form.cleaned_data["unidade"] == unidade
    assert form.cleaned_data["status"] == StatusInovacao.VALIDADA


@pytest.mark.django_db
def test_busca_com_101_caracteres_informa_limite_e_tamanho_digitado():
    """CONS-24."""
    form = BuscaForm(data={"q": "x" * 101})
    assert not form.is_valid()
    assert form.errors == {"q": ["Use no máximo 100 caracteres (você digitou 101)."]}


@pytest.mark.django_db
def test_busca_com_exatamente_100_caracteres_e_aceita():
    """CONS-24: o limite e 100, inclusive."""
    form = BuscaForm(data={"q": "x" * 100})
    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_opcoes_de_categoria_e_unidade_sao_todas_em_ordem_alfabetica():
    """CONS-26: "Todas ..." primeiro, depois os registros por nome.

    Um registro criado depois da carga, mas alfabeticamente antes, prova que a
    ordem e por nome e nao por id.
    """
    Categoria.objects.create(nome="Administração")
    Unidade.objects.create(nome="Almoxarifado")
    form = BuscaForm()
    rotulos_categoria = [rotulo for _, rotulo in form.fields["categoria"].choices]
    rotulos_unidade = [rotulo for _, rotulo in form.fields["unidade"].choices]
    assert rotulos_categoria == [
        "Todas as categorias",
        "Administração",
        "Atendimento interno",
        "Compras",
        "Financeiro",
        "RH",
        "TI interno",
    ]
    assert rotulos_unidade == [
        "Todas as unidades",
        "Almoxarifado",
        "Filial Leste",
        "Filial Norte",
        "Filial Oeste",
        "Filial Sul",
        "Sede",
    ]


def test_opcoes_de_status_seguem_o_ciclo_depois_de_todos_os_status():
    """CONS-26."""
    rotulos = [rotulo for _, rotulo in BuscaForm().fields["status"].choices]
    assert rotulos == ["Todos os status", "Em teste", "Validada", "Disponível para replicação"]
    valores = [valor for valor, _ in BuscaForm().fields["status"].choices]
    assert valores == ["", "EM_TESTE", "VALIDADA", "DISPONIVEL_PARA_REPLICACAO"]


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("campo", "valor", "mensagem"),
    [
        ("categoria", "999999", "Selecione uma categoria da lista."),
        ("categoria", "abc", "Selecione uma categoria da lista."),
        ("unidade", "999999", "Selecione uma unidade da lista."),
        ("unidade", "abc", "Selecione uma unidade da lista."),
        ("status", "X", "Selecione um status da lista."),
    ],
)
def test_filtro_fora_da_lista_traz_a_mensagem_do_campo(campo, valor, mensagem):
    """CONS-30: pk inexistente, pk nao numerico e status fora do enum."""
    form = BuscaForm(data={campo: valor})
    assert not form.is_valid()
    assert form.errors == {campo: [mensagem]}


@pytest.mark.django_db
@pytest.mark.parametrize("campo", CAMPOS)
def test_campo_tem_rotulo_visivel_ligado_ao_controle_pelo_for(campo):
    """CONS-36: <label for> com o id do controle."""
    form = BuscaForm()
    html = form[campo].as_field_group()
    rotulo = re.search(r'<label for="([^"]+)"[^>]*>(.*?)</label>', html, re.S)
    assert rotulo, campo
    assert rotulo.group(2).strip() == ROTULOS[campo]
    # O controle e o unico elemento com esse id e vem depois do rotulo.
    assert html.count(f'id="{rotulo.group(1)}"') == 1
    assert re.search(rf'<(input|select)[^>]*id="{rotulo.group(1)}"', html)
    assert rotulo.group(1) == form[campo].id_for_label


@pytest.mark.django_db
@pytest.mark.parametrize("campo", CAMPOS)
def test_ajuda_com_exemplo_fica_abaixo_do_controle_e_ligada_a_ele(campo):
    """CONS-52: o texto da spec, depois do controle, no aria-describedby."""
    html = BuscaForm()[campo].as_field_group()
    id_ajuda = f"id_{campo}_helptext"
    assert re.search(
        rf'<div class="helptext" id="{id_ajuda}">{re.escape(AJUDA[campo])}</div>', html
    )
    assert html.index(f'id="id_{campo}"') < html.index(f'id="{id_ajuda}"')
    controle = re.search(rf'<[^>]*id="id_{campo}"[^>]*>', html).group(0)
    descrito_por = re.search(r'aria-describedby="([^"]*)"', controle).group(1).split()
    assert id_ajuda in descrito_por


@pytest.mark.django_db
def test_busca_usa_o_controle_de_busca_sem_sufixo_no_rotulo():
    """CONS-31: type=search; o rotulo e "Buscar", sem dois-pontos."""
    html = BuscaForm()["q"].as_field_group()
    assert re.search(r'<input[^>]*type="search"', html)
    assert ">Buscar</label>" in html
