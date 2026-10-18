"""Testes do historico de status e da regra do ciclo de vida (F5).

O historico precisa valer mesmo quando o codigo grava direto no banco, sem
passar pela tela: as invariantes aqui vem do PostgreSQL (AD-003, AD-011).
"""

from datetime import timedelta
from itertools import product

import pytest
from django.db import IntegrityError
from django.db.models import ProtectedError

from inovacoes.models import MudancaDeStatus, StatusInovacao

EM_TESTE = StatusInovacao.EM_TESTE
VALIDADA = StatusInovacao.VALIDADA
DISPONIVEL = StatusInovacao.DISPONIVEL_PARA_REPLICACAO

# RN03: as unicas duas transicoes do ciclo.
TRANSICOES_VALIDAS = [(EM_TESTE, VALIDADA), (VALIDADA, DISPONIVEL)]
# Os 9 pares do produto 3x3 menos os 2 validos: pular, voltar, repetir.
TRANSICOES_INVALIDAS = [
    par for par in product(StatusInovacao.values, repeat=2) if par not in TRANSICOES_VALIDAS
]


def _registrar(inovacao, responsavel, anterior=EM_TESTE, novo=VALIDADA):
    return MudancaDeStatus.objects.create(
        inovacao=inovacao, status_anterior=anterior, status_novo=novo, responsavel=responsavel
    )


def test_ha_sete_transicoes_invalidas():
    # Sanidade da parametrizacao: nenhum par fica de fora.
    assert len(TRANSICOES_INVALIDAS) == 7


@pytest.mark.django_db
@pytest.mark.parametrize(("anterior", "novo"), TRANSICOES_VALIDAS)
def test_transicao_valida_e_gravada(criar_inovacao, autor, anterior, novo):
    inovacao = criar_inovacao()
    _registrar(inovacao, autor, anterior, novo)
    registro = MudancaDeStatus.objects.get()
    assert (registro.inovacao, registro.status_anterior, registro.status_novo) == (
        inovacao,
        anterior,
        novo,
    )
    assert registro.responsavel == autor
    assert registro.data is not None


@pytest.mark.django_db
@pytest.mark.parametrize(("anterior", "novo"), TRANSICOES_INVALIDAS)
def test_transicao_invalida_e_recusada_pelo_banco(criar_inovacao, autor, anterior, novo):
    """STAT-31: pular, voltar ou repetir um estagio nao entra no historico."""
    inovacao = criar_inovacao()
    with pytest.raises(IntegrityError, match="mudanca_de_status_transicao_valida"):
        _registrar(inovacao, autor, anterior, novo)


@pytest.mark.django_db
def test_excluir_a_inovacao_apaga_so_o_historico_dela(criar_inovacao, autor):
    """STAT-28: o historico vai junto com a inovacao, e o de outra fica."""
    inovacao = criar_inovacao()
    outra = criar_inovacao(titulo="Outra Inovacao")
    _registrar(inovacao, autor)
    _registrar(inovacao, autor, VALIDADA, DISPONIVEL)
    da_outra = _registrar(outra, autor)

    inovacao.delete()

    assert list(MudancaDeStatus.objects.all()) == [da_outra]


@pytest.mark.django_db
def test_excluir_a_conta_responsavel_e_recusado(criar_inovacao, administrador):
    """STAT-29: a conta que fez a mudanca nao pode ser apagada."""
    registro = _registrar(criar_inovacao(), administrador)
    with pytest.raises(ProtectedError):
        administrador.delete()
    assert MudancaDeStatus.objects.get().pk == registro.pk
    assert MudancaDeStatus.objects.get().responsavel_id == administrador.pk


@pytest.mark.django_db
def test_historico_sai_do_mais_antigo_ao_mais_recente(criar_inovacao, autor):
    """STAT-24: a data manda, mesmo contra a ordem do id."""
    inovacao = criar_inovacao()
    primeiro = _registrar(inovacao, autor)
    segundo = _registrar(inovacao, autor, VALIDADA, DISPONIVEL)
    MudancaDeStatus.objects.filter(pk=primeiro.pk).update(data=segundo.data + timedelta(hours=1))
    assert list(MudancaDeStatus.objects.all()) == [segundo, primeiro]


@pytest.mark.django_db
def test_historico_com_a_mesma_data_sai_na_ordem_do_id(criar_inovacao, autor):
    """STAT-24: mesma data, o id desempata do menor para o maior."""
    inovacao = criar_inovacao()
    primeiro = _registrar(inovacao, autor)
    segundo = _registrar(inovacao, autor, VALIDADA, DISPONIVEL)
    MudancaDeStatus.objects.update(data=primeiro.data)
    assert list(MudancaDeStatus.objects.all()) == [primeiro, segundo]
