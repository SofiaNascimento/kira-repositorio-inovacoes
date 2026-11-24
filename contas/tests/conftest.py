"""Contas e unidades da area do gestor (gestao-por-unidade, T8 a T12)."""

import pytest

from contas.models import Usuario
from inovacoes.models import Unidade

GESTOR = Usuario.Perfil.GESTOR_DE_UNIDADE
SENHA_NOVA = "Kira-provisoria-2026"


@pytest.fixture
def sede(db):
    return Unidade.objects.get(nome="Sede")


@pytest.fixture
def norte(db):
    return Unidade.objects.get(nome="Filial Norte")


@pytest.fixture
def criar_conta(db):
    """Cria uma conta com e-mail derivado do usuario; cada campo pode ser trocado."""

    def criar(username, perfil=Usuario.Perfil.USUARIO, unidade=None, **campos):
        campos.setdefault("email", f"{username}@x.com")
        return Usuario.objects.create_user(
            username=username, perfil=perfil, unidade=unidade, **campos
        )

    return criar


@pytest.fixture
def gestor(criar_conta, sede):
    """Gestor da Sede, com nome completo."""
    return criar_conta("gil", GESTOR, sede, first_name="Gil", last_name="Souza")


@pytest.fixture
def gestor_logado(client, gestor):
    client.force_login(gestor)
    return client
