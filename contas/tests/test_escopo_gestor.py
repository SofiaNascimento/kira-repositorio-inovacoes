"""Testes da situacao da conta e do alcance do gestor no modelo Usuario.

Derivados das ACs GEST-14, GEST-15, GEST-17, GEST-18, GEST-32 e GEST-61
(.specs/features/gestao-por-unidade/spec.md) e da AD-016.
"""

import pytest

from contas.models import TRANSICOES, SituacaoConta, Usuario
from inovacoes.models import Unidade

USUARIO = Usuario.Perfil.USUARIO
ADMINISTRADOR = Usuario.Perfil.ADMINISTRADOR
GESTOR = Usuario.Perfil.GESTOR_DE_UNIDADE


def _conta(username, perfil=USUARIO, unidade=None, first_name="", last_name="", **extra):
    return Usuario.objects.create_user(
        username=username,
        email=f"{username}@x.com",
        perfil=perfil,
        unidade=unidade,
        first_name=first_name,
        last_name=last_name,
        **extra,
    )


@pytest.fixture
def sede(db):
    return Unidade.objects.get(nome="Sede")


@pytest.fixture
def norte(db):
    return Unidade.objects.get(nome="Filial Norte")


@pytest.fixture
def cenario(sede, norte):
    """Uma conta de cada caso que a GEST-61 separa, todas em volta da Sede."""
    return {
        "gestor": _conta("gil", GESTOR, sede, "Gil", "Souza"),
        "usuario_ativo": _conta("bia", USUARIO, sede, "Bia", "Lima"),
        "usuario_desativado": _conta("caio", USUARIO, sede, "Caio", "Reis", is_active=False),
        "outra_unidade": _conta("davi", USUARIO, norte, "Davi", "Melo"),
        "sem_unidade": _conta("elis", USUARIO, None, "Elis", "Prado"),
        "outro_gestor": _conta("fabi", GESTOR, sede, "Fabi", "Rocha"),
        "administrador_da_unidade": _conta("hugo", ADMINISTRADOR, sede, "Hugo", "Dias"),
    }


DENTRO = {"usuario_ativo", "usuario_desativado"}
FORA = {"gestor", "outra_unidade", "sem_unidade", "outro_gestor", "administrador_da_unidade"}


# --- Situacao (AD-016) -----------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize(
    ("ativa", "esperado"),
    [(True, SituacaoConta.ATIVA), (False, SituacaoConta.DESATIVADA)],
    ids=["ativa", "desativada"],
)
def test_situacao_sai_do_is_active(ativa, esperado):
    """AD-016: situacao derivada, sem coluna."""
    assert Usuario(is_active=ativa).situacao == esperado


@pytest.mark.unit
def test_rotulos_da_situacao_sao_por_escrito():
    """GEST-16 e AD-016: "Ativa" e "Desativada", os textos da tabela."""
    assert SituacaoConta.choices == [("ATIVA", "Ativa"), ("DESATIVADA", "Desativada")]


@pytest.mark.unit
def test_transicoes_sao_so_desativar_e_reativar():
    """AD-016: a tabela unica das mudancas de situacao."""
    assert TRANSICOES == {
        SituacaoConta.ATIVA: {SituacaoConta.DESATIVADA},
        SituacaoConta.DESATIVADA: {SituacaoConta.ATIVA},
    }


@pytest.mark.django_db
def test_mudar_situacao_para_desativada_grava_so_o_is_active(sede):
    """GEST-30: a conta fica inativa; outro campo alterado em memoria nao vai ao banco."""
    bia = _conta("bia", USUARIO, sede, "Bia")
    bia.first_name = "Outro nome"
    bia.mudar_situacao(SituacaoConta.DESATIVADA)
    bia.refresh_from_db()
    assert (bia.is_active, bia.situacao, bia.first_name) == (
        False,
        SituacaoConta.DESATIVADA,
        "Bia",
    )


@pytest.mark.django_db
def test_mudar_situacao_para_ativa_reativa(sede):
    """GEST-31: a conta desativada volta a ativa."""
    caio = _conta("caio", USUARIO, sede, is_active=False)
    caio.mudar_situacao(SituacaoConta.ATIVA)
    caio.refresh_from_db()
    assert caio.situacao == SituacaoConta.ATIVA


@pytest.mark.django_db
def test_repetir_o_destino_mantem_o_estado(sede):
    """GEST-32: o destino e explicito; repetir deixa a conta como esta."""
    bia = _conta("bia", USUARIO, sede)
    bia.mudar_situacao(SituacaoConta.DESATIVADA)
    bia.mudar_situacao(SituacaoConta.DESATIVADA)
    bia.refresh_from_db()
    assert bia.situacao == SituacaoConta.DESATIVADA


# --- da_unidade (GEST-14, GEST-15) ------------------------------------------------


@pytest.mark.django_db
def test_da_unidade_lista_toda_conta_da_unidade_por_nome_e_usuario(sede, norte):
    """GEST-14 e GEST-15: inclusive desativada e o gestor; ordem por nome
    completo e depois por usuario; sem outra unidade nem unidade nula."""
    _conta("zeca", USUARIO, sede, "Ana", "Souza")
    _conta("aldo", USUARIO, sede, "Ana", "Souza")
    _conta("lia", USUARIO, sede, "Ana", "Alves", is_active=False)
    _conta("gil", GESTOR, sede, "Bruno", "")
    _conta("hugo", ADMINISTRADOR, sede, "Ana", "Barros")
    _conta("davi", USUARIO, norte, "Ana", "Aaa")
    _conta("elis", USUARIO, None, "Ana", "Aaa")

    usernames = list(Usuario.objects.da_unidade(sede).values_list("username", flat=True))
    assert usernames == ["lia", "hugo", "aldo", "zeca", "gil"]


# --- administraveis_por e pode_ser_administrada_por (GEST-17, GEST-18, GEST-61) ----


@pytest.mark.django_db
def test_administraveis_por_so_usuario_da_unidade_do_gestor(cenario):
    """GEST-61: fora ficam outra unidade, sem unidade, o proprio gestor,
    outro gestor e o ADMINISTRADOR da unidade."""
    alcance = set(Usuario.objects.administraveis_por(cenario["gestor"]))
    assert alcance == {cenario[nome] for nome in DENTRO}


@pytest.mark.django_db
@pytest.mark.parametrize(
    "quem",
    ["usuario_ativo", "administrador_da_unidade", "superusuario"],
)
def test_administraveis_por_e_vazio_para_quem_nao_e_gestor(cenario, quem):
    """GEST-61: sem o perfil de gestor, nenhuma conta, nem com is_superuser."""
    if quem == "superusuario":
        pessoa = Usuario.objects.create_superuser(
            username="raiz", email="raiz@x.com", password="x", perfil=USUARIO
        )
    else:
        pessoa = cenario[quem]
    assert list(Usuario.objects.administraveis_por(pessoa)) == []


@pytest.mark.django_db
@pytest.mark.parametrize("alvo", sorted(DENTRO | FORA))
def test_pode_ser_administrada_por_segue_o_queryset_sem_consulta(
    cenario, alvo, django_assert_num_queries
):
    """GEST-17 e GEST-18: a mesma resposta do queryset, lendo so a instancia."""
    gestor, conta = cenario["gestor"], cenario[alvo]
    with django_assert_num_queries(0):
        resposta = conta.pode_ser_administrada_por(gestor)
    assert resposta is (alvo in DENTRO)
    assert resposta is Usuario.objects.administraveis_por(gestor).filter(pk=conta.pk).exists()


@pytest.mark.django_db
def test_pode_ser_administrada_por_e_falso_para_quem_nao_e_gestor(cenario):
    """GEST-61: um USUARIO da mesma unidade nao administra a conta vizinha."""
    vizinha, usuario = cenario["usuario_desativado"], cenario["usuario_ativo"]
    assert vizinha.pode_ser_administrada_por(usuario) is False
