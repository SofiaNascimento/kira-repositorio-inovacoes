"""Testes das invariantes que o banco impoe sobre as listas e a inovacao.

Regras que precisam valer mesmo quando o codigo grava direto no banco, sem
passar por formulario ou full_clean() (AD-003).
"""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from inovacoes.models import Categoria, Unidade

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
