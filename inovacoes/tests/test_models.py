"""Testes dos modelos da app inovacoes."""

import pytest
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.db.models import ProtectedError
from django.utils import timezone

from inovacoes.models import Categoria, Inovacao, StatusInovacao, Unidade

LISTAS = [Unidade, Categoria]


@pytest.mark.django_db
@pytest.mark.parametrize("modelo", LISTAS)
def test_itens_da_lista_saem_em_ordem_alfabetica(modelo):
    """INOV-15: a consulta padrao, que alimenta o select, e alfabetica."""
    for nome in ["Teste Gama", "Teste Alfa", "Teste Beta"]:
        modelo.objects.create(nome=nome)
    nomes = list(modelo.objects.filter(nome__startswith="Teste ").values_list("nome", flat=True))
    assert nomes == ["Teste Alfa", "Teste Beta", "Teste Gama"]


@pytest.mark.django_db
def test_inovacao_nasce_em_teste(criar_inovacao):
    """INOV-05: o status inicial e do sistema, nao de quem cadastra."""
    inovacao = criar_inovacao()
    inovacao.refresh_from_db()
    assert inovacao.status == StatusInovacao.EM_TESTE


@pytest.mark.django_db
def test_inovacao_recebe_a_data_de_criacao_do_momento(criar_inovacao):
    """INOV-05: data de criacao = instante do servidor em que o registro nasce."""
    antes = timezone.now()
    inovacao = criar_inovacao()
    depois = timezone.now()
    inovacao.refresh_from_db()
    assert antes <= inovacao.data_criacao <= depois


@pytest.mark.django_db
def test_inovacao_sem_resultado_e_valida(criar_inovacao):
    """INOV-14: resultado/impacto e o unico texto opcional."""
    inovacao = criar_inovacao(resultado="")
    inovacao.full_clean()


@pytest.mark.django_db
@pytest.mark.parametrize("campo", ["unidade", "categoria"])
def test_item_de_lista_em_uso_nao_pode_ser_apagado(criar_inovacao, campo):
    """INOV-19: excluir um item usado por uma inovacao e recusado e ele fica."""
    item = getattr(criar_inovacao(), campo)
    with pytest.raises(ProtectedError):
        item.delete()
    assert type(item).objects.filter(pk=item.pk).exists()


MENSAGEM_DUPLICADO = "Já existe uma inovação com este título nesta unidade. Escolha outro título."


@pytest.mark.django_db
def test_titulo_duplicado_acusa_o_erro_no_campo_titulo(criar_inovacao, autor, unidade, categoria):
    """INOV-22: a constraint sobre expressao daria erro geral; o erro vai ao campo."""
    criar_inovacao(titulo="Controle de Caixa")
    repetida = Inovacao(
        titulo="controle de caixa",
        unidade=unidade,
        categoria=categoria,
        problema="p",
        solucao="s",
        contato="c",
        autor=autor,
    )
    with pytest.raises(ValidationError) as erro:
        repetida.full_clean()
    assert erro.value.message_dict == {"titulo": [MENSAGEM_DUPLICADO]}
    assert [e.code for e in erro.value.error_dict["titulo"]] == ["titulo_duplicado"]


@pytest.mark.django_db
def test_titulo_novo_passa_na_validacao(criar_inovacao, autor, unidade, categoria):
    criar_inovacao(titulo="Controle de Caixa")
    Inovacao(
        titulo="Conciliação bancária",
        unidade=unidade,
        categoria=categoria,
        problema="p",
        solucao="s",
        contato="c",
        autor=autor,
    ).full_clean()


@pytest.mark.django_db
def test_outro_erro_de_constraint_continua_geral(criar_inovacao):
    """O remapeamento so move o erro de titulo duplicado."""
    inovacao = criar_inovacao()
    inovacao.status = "APROVADA"
    with pytest.raises(ValidationError) as erro:
        inovacao.validate_constraints()
    assert list(erro.value.error_dict) == [NON_FIELD_ERRORS]
    (mensagem,) = erro.value.message_dict[NON_FIELD_ERRORS]
    assert "inovacao_status_valido" in mensagem
