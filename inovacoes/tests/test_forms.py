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


OPCOES_INICIAIS = {
    "unidade": ["Filial Leste", "Filial Norte", "Filial Oeste", "Filial Sul", "Sede"],
    "categoria": ["Atendimento interno", "Compras", "Financeiro", "RH", "TI interno"],
}
MENSAGEM_FORA_DA_LISTA = {
    "unidade": "Selecione uma unidade da lista.",
    "categoria": "Selecione uma categoria da lista.",
}


@pytest.mark.django_db
@pytest.mark.parametrize("campo", OPCOES_INICIAIS)
def test_select_lista_so_os_itens_cadastrados_em_ordem_alfabetica(campo):
    """INOV-15: primeiro a opcao vazia, depois os itens do banco."""
    rotulos = [rotulo for _, rotulo in InovacaoForm().fields[campo].choices]
    assert rotulos == ["Selecione…", *OPCOES_INICIAIS[campo]]


@pytest.mark.django_db
@pytest.mark.parametrize("campo", MENSAGEM_FORA_DA_LISTA)
def test_item_inexistente_e_recusado_com_a_mensagem_do_campo(dados_validos, campo):
    """INOV-17: so ocorre com POST adulterado."""
    dados_validos[campo] = "999999"
    form = InovacaoForm(data=dados_validos)
    assert not form.is_valid()
    assert form.errors == {campo: [MENSAGEM_FORA_DA_LISTA[campo]]}


@pytest.mark.django_db
def test_item_apagado_entre_abrir_e_enviar_o_formulario_e_recusado(dados_validos, unidade):
    """INOV-17: a pessoa escolheu um item que deixou de existir."""
    unidade.delete()
    form = InovacaoForm(data=dados_validos)
    assert not form.is_valid()
    assert form.errors == {"unidade": ["Selecione uma unidade da lista."]}


def _atributo(html, id_controle, atributo):
    """Valor de um atributo na tag do controle, ou None se ausente."""
    inicio = html.index(f'id="{id_controle}"')
    tag = html[html.rindex("<", 0, inicio) : html.index(">", inicio)]
    marcador = f'{atributo}="'
    if marcador not in tag:
        return None
    resto = tag[tag.index(marcador) + len(marcador) :]
    return resto[: resto.index('"')]


@pytest.mark.django_db
@pytest.mark.parametrize("campo", CAMPOS)
def test_ajuda_com_exemplo_fica_abaixo_do_controle_e_ligada_a_ele(campo):
    """INOV-41: texto de apoio com exemplo, depois do controle, no aria-describedby."""
    html = InovacaoForm()[campo].as_field_group()
    id_ajuda = f"id_{campo}_helptext"
    assert f'id="{id_ajuda}"' in html
    ajuda = html[html.index(f'id="{id_ajuda}"') :]
    assert "Ex.:" in ajuda[: ajuda.index("</")]
    assert html.index(f'id="id_{campo}"') < html.index(f'id="{id_ajuda}"')
    assert id_ajuda in _atributo(html, f"id_{campo}", "aria-describedby").split()


@pytest.mark.django_db
def test_campo_com_erro_fica_invalido_e_ligado_a_mensagem(dados_validos):
    """INOV-33: aria-invalid e aria-describedby apontando para o erro, que vem
    antes da ajuda (rotulo, controle, erros, ajuda)."""
    dados_validos["titulo"] = ""
    form = InovacaoForm(data=dados_validos)
    form.is_valid()
    html = form["titulo"].as_field_group()
    assert _atributo(html, "id_titulo", "aria-invalid") == "true"
    assert "id_titulo_error" in _atributo(html, "id_titulo", "aria-describedby").split()
    erro = html[html.index('id="id_titulo_error"') :]
    assert "Informe o título da inovação." in erro[: erro.index("</ul>")]
    assert (
        html.index('id="id_titulo"')
        < html.index('id="id_titulo_error"')
        < html.index('id="id_titulo_helptext"')
    )


@pytest.mark.django_db
def test_campo_sem_erro_nao_fica_invalido(dados_validos):
    dados_validos["titulo"] = ""
    form = InovacaoForm(data=dados_validos)
    form.is_valid()
    assert _atributo(form["problema"].as_field_group(), "id_problema", "aria-invalid") is None
