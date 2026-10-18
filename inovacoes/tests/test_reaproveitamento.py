"""Testes do Reaproveitamento e da regra da RN09 (F6).

As invariantes do banco (unicidade, CASCADE, PROTECT) sao provadas com
registros criados direto pelo ORM. Fora deste bloco, todo reaproveitamento
nasce por Inovacao.registrar_reaproveitamento (AD-012).
"""

from datetime import timedelta

import pytest
from django.db import IntegrityError
from django.db.models import ProtectedError

from contas.models import Usuario
from inovacoes.models import Reaproveitamento, Unidade

UNICA = "reaproveitamento_unico_por_unidade"


@pytest.fixture
def outra_unidade(db):
    return Unidade.objects.create(nome="Teste Outra Unidade")


def _gravar(inovacao, unidade, por):
    """So para provar o banco; o caminho da aplicacao e o metodo (AD-012)."""
    return Reaproveitamento.objects.create(inovacao=inovacao, unidade=unidade, registrado_por=por)


# --- Banco: unicidade, CASCADE, PROTECT e ordenacao (T1) ---


@pytest.mark.django_db
def test_mesmo_par_inovacao_unidade_e_recusado_pelo_banco(criar_inovacao, outra_unidade, autor):
    """REAP-14: o segundo registro do mesmo par bate na UniqueConstraint."""
    inovacao = criar_inovacao()
    _gravar(inovacao, outra_unidade, autor)
    with pytest.raises(IntegrityError) as erro:
        _gravar(inovacao, outra_unidade, autor)
    assert erro.value.__cause__.diag.constraint_name == UNICA


@pytest.mark.django_db
def test_mesma_unidade_em_outra_inovacao_e_outra_unidade_na_mesma_gravam(
    criar_inovacao, outra_unidade, autor
):
    """REAP-14: a unicidade e do par, nao da unidade nem da inovacao."""
    inovacao = criar_inovacao()
    outra = criar_inovacao(titulo="Outra Inovacao")
    terceira_unidade = Unidade.objects.create(nome="Teste Terceira Unidade")
    _gravar(inovacao, outra_unidade, autor)
    _gravar(outra, outra_unidade, autor)
    _gravar(inovacao, terceira_unidade, autor)
    pares = set(Reaproveitamento.objects.values_list("inovacao_id", "unidade_id"))
    assert pares == {
        (inovacao.pk, outra_unidade.pk),
        (outra.pk, outra_unidade.pk),
        (inovacao.pk, terceira_unidade.pk),
    }


@pytest.mark.django_db
def test_excluir_a_inovacao_apaga_so_os_reaproveitamentos_dela(
    criar_inovacao, outra_unidade, autor
):
    """REAP-23: os registros vao junto com a inovacao, e os de outra ficam."""
    inovacao = criar_inovacao()
    outra = criar_inovacao(titulo="Outra Inovacao")
    _gravar(inovacao, outra_unidade, autor)
    da_outra = _gravar(outra, outra_unidade, autor)

    inovacao.delete()

    assert list(Reaproveitamento.objects.all()) == [da_outra]


@pytest.mark.django_db
def test_excluir_a_unidade_que_reaproveitou_e_recusado(criar_inovacao, outra_unidade, autor):
    """REAP-24: unidade referenciada fica, e o registro tambem."""
    registro = _gravar(criar_inovacao(), outra_unidade, autor)
    with pytest.raises(ProtectedError):
        outra_unidade.delete()
    assert Unidade.objects.filter(pk=outra_unidade.pk).exists()
    assert Reaproveitamento.objects.get().pk == registro.pk
    assert Reaproveitamento.objects.get().unidade_id == outra_unidade.pk


@pytest.mark.django_db
def test_excluir_a_conta_que_registrou_e_recusado(criar_inovacao, outra_unidade, administrador):
    """REAP-25: a conta registrado_por fica, e o registro tambem."""
    registro = _gravar(criar_inovacao(), outra_unidade, administrador)
    with pytest.raises(ProtectedError):
        administrador.delete()
    assert Usuario.objects.filter(pk=administrador.pk).exists()
    assert Reaproveitamento.objects.get().pk == registro.pk
    assert Reaproveitamento.objects.get().registrado_por_id == administrador.pk


@pytest.mark.django_db
def test_reaproveitamentos_saem_do_mais_antigo_ao_mais_recente(
    criar_inovacao, outra_unidade, autor
):
    """REAP-18: a data manda, mesmo contra a ordem do id."""
    inovacao = criar_inovacao()
    primeiro = _gravar(inovacao, outra_unidade, autor)
    segundo = _gravar(inovacao, Unidade.objects.create(nome="Teste Terceira Unidade"), autor)
    Reaproveitamento.objects.filter(pk=primeiro.pk).update(data=segundo.data + timedelta(hours=1))
    assert list(Reaproveitamento.objects.all()) == [segundo, primeiro]


@pytest.mark.django_db
def test_reaproveitamentos_com_a_mesma_data_saem_na_ordem_do_id(
    criar_inovacao, outra_unidade, autor
):
    """REAP-18: mesma data, o id desempata do menor para o maior."""
    inovacao = criar_inovacao()
    primeiro = _gravar(inovacao, outra_unidade, autor)
    segundo = _gravar(inovacao, Unidade.objects.create(nome="Teste Terceira Unidade"), autor)
    Reaproveitamento.objects.filter(pk=segundo.pk).update(data=primeiro.data)
    assert list(Reaproveitamento.objects.all()) == [primeiro, segundo]
