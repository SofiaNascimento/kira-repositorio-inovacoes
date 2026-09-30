"""Testes das invariantes que o banco impoe sobre as listas e a inovacao.

Regras que precisam valer mesmo quando o codigo grava direto no banco, sem
passar por formulario ou full_clean() (AD-003).
"""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from inovacoes.models import Categoria, Inovacao, StatusInovacao, Unidade

LISTAS = [Unidade, Categoria]


@pytest.mark.django_db
@pytest.mark.parametrize("modelo", LISTAS)
def test_nome_de_item_repetido_em_outra_caixa_e_recusado_pelo_banco(modelo):
    """Duas "Sede" em caixa diferente quebrariam os filtros da F3 (RN07)."""
    modelo.objects.create(nome="Teste Repetido")
    with pytest.raises(IntegrityError):
        modelo.objects.create(nome="TESTE REPETIDO")


@pytest.mark.django_db
@pytest.mark.parametrize("modelo", LISTAS)
def test_nome_de_item_repetido_acusa_a_mensagem_da_constraint(modelo):
    modelo.objects.create(nome="Teste Repetido")
    with pytest.raises(ValidationError) as erro:
        modelo(nome="teste repetido").full_clean()
    assert erro.value.messages == ["Já existe um item com este nome."]


@pytest.mark.django_db
@pytest.mark.parametrize("campo", ["unidade", "categoria"])
def test_inovacao_sem_unidade_ou_categoria_e_recusada_pelo_banco(criar_inovacao, campo):
    """INOV-16: FK NOT NULL; nenhuma inovacao existe sem unidade e categoria."""
    with pytest.raises(IntegrityError):
        criar_inovacao(**{campo: None})


@pytest.mark.django_db
def test_status_invalido_e_recusado_no_create(criar_inovacao):
    """choices sozinho so vale no full_clean(); o banco barra o resto."""
    with pytest.raises(IntegrityError):
        criar_inovacao(status="APROVADA")


@pytest.mark.django_db
def test_status_invalido_e_recusado_no_update_em_massa(criar_inovacao):
    inovacao = criar_inovacao()
    with pytest.raises(IntegrityError), transaction.atomic():
        Inovacao.objects.filter(pk=inovacao.pk).update(status="APROVADA")
    inovacao.refresh_from_db()
    assert inovacao.status == StatusInovacao.EM_TESTE
