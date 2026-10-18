"""Testes do Reaproveitamento e da regra da RN09 (F6).

As invariantes do banco (unicidade, CASCADE, PROTECT) sao provadas com
registros criados direto pelo ORM. Fora deste bloco, todo reaproveitamento
nasce por Inovacao.registrar_reaproveitamento (AD-012).
"""

from datetime import timedelta
from types import SimpleNamespace
from unittest import mock

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.db.models import ProtectedError
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from contas.models import Usuario
from inovacoes.models import Inovacao, Reaproveitamento, StatusInovacao, Unidade

UNICA = "reaproveitamento_unico_por_unidade"

EM_TESTE = StatusInovacao.EM_TESTE
VALIDADA = StatusInovacao.VALIDADA
DISPONIVEL = StatusInovacao.DISPONIVEL_PARA_REPLICACAO


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


# --- Inovacao.pode_ser_reaproveitada e registrar_reaproveitamento (AD-012, T2) ---


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("status", "esperado"), [(EM_TESTE, False), (VALIDADA, False), (DISPONIVEL, True)]
)
def test_pode_ser_reaproveitada_so_quando_disponivel(criar_inovacao, status, esperado):
    """RN09: so "Disponivel para replicacao" aceita sinalizacao."""
    assert criar_inovacao(status=status).pode_ser_reaproveitada() is esperado


@pytest.mark.django_db
@pytest.mark.parametrize("conta", ["autor", "terceiro"])
def test_registrar_cria_um_registro_completo(request, criar_inovacao, outra_unidade, conta):
    """REAP-05, REAP-22: inovacao, unidade, quem registrou e a hora do servidor."""
    por = request.getfixturevalue(conta)
    inovacao = criar_inovacao(status=DISPONIVEL)
    antes = timezone.now()

    devolvido = inovacao.registrar_reaproveitamento(unidade=outra_unidade, por=por)

    registro = Reaproveitamento.objects.get()
    assert devolvido == registro
    assert registro.inovacao_id == inovacao.pk
    assert registro.unidade_id == outra_unidade.pk
    assert registro.registrado_por_id == por.pk
    assert antes <= registro.data <= timezone.now()


@pytest.mark.django_db
@pytest.mark.parametrize(("status", "rotulo"), [(EM_TESTE, "Em teste"), (VALIDADA, "Validada")])
def test_registrar_fora_de_disponivel_e_recusado(
    criar_inovacao, outra_unidade, autor, status, rotulo
):
    """REAP-10: erro de validacao com o status gravado, e nada e criado."""
    inovacao = criar_inovacao(status=status)
    with pytest.raises(ValidationError) as erro:
        inovacao.registrar_reaproveitamento(unidade=outra_unidade, por=autor)
    assert erro.value.code == "status_indisponivel"
    assert erro.value.messages == [
        "Só uma inovação “Disponível para replicação” pode ser sinalizada como reaproveitada. "
        f"Status atual: “{rotulo}”."
    ]
    assert Reaproveitamento.objects.count() == 0


@pytest.mark.django_db
def test_registrar_recusa_pelo_status_gravado_e_nao_pelo_da_instancia(
    criar_inovacao, outra_unidade, autor
):
    """REAP-10: a instancia diz Disponivel, mas o banco diz Validada."""
    inovacao = criar_inovacao(status=DISPONIVEL)
    Inovacao.objects.filter(pk=inovacao.pk).update(status=VALIDADA)
    assert inovacao.status == DISPONIVEL
    with pytest.raises(ValidationError) as erro:
        inovacao.registrar_reaproveitamento(unidade=outra_unidade, por=autor)
    assert erro.value.code == "status_indisponivel"
    assert "Status atual: “Validada”." in erro.value.messages[0]
    assert Reaproveitamento.objects.count() == 0


@pytest.mark.django_db
def test_registrar_aceita_pelo_status_gravado_e_nao_pelo_da_instancia(
    criar_inovacao, outra_unidade, autor
):
    """REAP-05: a instancia ficou velha em "Em teste", o banco ja diz Disponivel."""
    inovacao = criar_inovacao(status=EM_TESTE)
    Inovacao.objects.filter(pk=inovacao.pk).update(status=DISPONIVEL)
    assert inovacao.status == EM_TESTE
    inovacao.registrar_reaproveitamento(unidade=outra_unidade, por=autor)
    assert Reaproveitamento.objects.get().unidade_id == outra_unidade.pk


@pytest.mark.django_db
def test_registrar_pela_unidade_de_origem_e_recusado(criar_inovacao, unidade, autor):
    """REAP-11: a origem nao reaproveita a propria inovacao."""
    inovacao = criar_inovacao(status=DISPONIVEL)
    with pytest.raises(ValidationError) as erro:
        inovacao.registrar_reaproveitamento(unidade=unidade, por=autor)
    assert erro.value.code == "unidade_de_origem"
    assert erro.value.messages == ["A unidade de origem não pode reaproveitar a própria inovação."]
    assert Reaproveitamento.objects.count() == 0


@pytest.mark.django_db
def test_registrar_duas_vezes_a_mesma_unidade_e_recusado(criar_inovacao, outra_unidade, autor):
    """REAP-12, REAP-14: um registro so, e a transacao de quem chamou continua usavel."""
    inovacao = criar_inovacao(status=DISPONIVEL)
    primeiro = inovacao.registrar_reaproveitamento(unidade=outra_unidade, por=autor)
    with transaction.atomic():
        with pytest.raises(ValidationError) as erro:
            inovacao.registrar_reaproveitamento(unidade=outra_unidade, por=autor)
        # Uma transacao abortada recusaria esta consulta.
        assert list(Reaproveitamento.objects.all()) == [primeiro]
    assert erro.value.code == "unidade_ja_reaproveitou"
    assert erro.value.messages == [
        "A unidade “Teste Outra Unidade” já sinalizou o reaproveitamento desta inovação."
    ]
    assert Reaproveitamento.objects.count() == 1


@pytest.mark.django_db
def test_registrar_relanca_violacao_de_outra_constraint(criar_inovacao, outra_unidade, autor):
    """REAP-14: so a unicidade vira recusa; outra violacao sobe (500, REAP-49)."""
    inovacao = criar_inovacao(status=DISPONIVEL)
    falha = IntegrityError("outra violacao")
    # O psycopg poe o nome da constraint em __cause__.diag.
    causa = Exception("violacao do banco")
    causa.diag = SimpleNamespace(constraint_name="outra_constraint")
    falha.__cause__ = causa
    with (
        mock.patch.object(Reaproveitamento.objects, "create", side_effect=falha),
        pytest.raises(IntegrityError) as erro,
    ):
        inovacao.registrar_reaproveitamento(unidade=outra_unidade, por=autor)
    assert erro.value is falha
    assert Reaproveitamento.objects.count() == 0


@pytest.mark.django_db
def test_registrar_trava_a_linha_ao_ler_o_status(criar_inovacao, outra_unidade, autor):
    """REAP-14: o SELECT ... FOR UPDATE serializa duas sinalizacoes."""
    inovacao = criar_inovacao(status=DISPONIVEL)
    with CaptureQueriesContext(connection) as consultas:
        inovacao.registrar_reaproveitamento(unidade=outra_unidade, por=autor)
    leituras = [c["sql"] for c in consultas if c["sql"].startswith("SELECT")]
    assert '"inovacoes_inovacao"."status"' in leituras[0]
    assert leituras[0].endswith("FOR UPDATE")


@pytest.mark.django_db
def test_registrar_em_inovacao_apagada_levanta_does_not_exist(criar_inovacao, outra_unidade, autor):
    """REAP-16: a inovacao sumiu entre carregar e registrar; nada e criado."""
    inovacao = criar_inovacao(status=DISPONIVEL)
    Inovacao.objects.filter(pk=inovacao.pk).delete()
    with pytest.raises(Inovacao.DoesNotExist):
        inovacao.registrar_reaproveitamento(unidade=outra_unidade, por=autor)
    assert Reaproveitamento.objects.count() == 0


@pytest.mark.django_db
def test_registrar_nao_muda_nenhum_campo_da_inovacao(criar_inovacao, outra_unidade, terceiro):
    """REAP-07: status, autor, data de criacao e texto de busca intactos."""
    inovacao = criar_inovacao(status=DISPONIVEL)
    antes = Inovacao.objects.filter(pk=inovacao.pk).values().get()
    inovacao.registrar_reaproveitamento(unidade=outra_unidade, por=terceiro)
    depois = Inovacao.objects.filter(pk=inovacao.pk).values().get()
    assert depois == antes
    assert depois["status"] == DISPONIVEL
    assert depois["texto_busca"] != ""
