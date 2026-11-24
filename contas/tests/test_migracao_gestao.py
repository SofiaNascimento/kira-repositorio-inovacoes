"""Teste da migration contas 0005 (gestao-por-unidade).

A 0005 so muda o esquema: as contas que ja existem continuam validas nas duas
CHECKs, com unidade nula e senha provisoria falsa (design.md, Migration).
"""

import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

from contas.models import Usuario

ANTES = [("contas", "0004_alter_usuario_managers")]
CAMPOS = ("username", "email", "perfil", "is_staff", "is_superuser", "is_active", "password")


def _migrar(alvo):
    # Executor novo a cada passo: o grafo e o estado aplicado mudam entre eles.
    executor = MigrationExecutor(connection)
    executor.migrate(alvo)
    return executor


@pytest.fixture
def antes_da_gestao(db):
    """Banco em contas 0004; no fim, volta ao estado final."""
    executor = _migrar(ANTES)
    try:
        yield executor.loader.project_state(ANTES).apps
    finally:
        _migrar(MigrationExecutor(connection).loader.graph.leaf_nodes())


def test_contas_existentes_continuam_iguais_sem_unidade(antes_da_gestao):
    """GEST-01, GEST-03: USUARIO e ADMINISTRADOR de antes da 0005 seguem validos."""
    historico = antes_da_gestao.get_model("contas", "Usuario")
    contas = [
        historico.objects.create(username="ana", email="ana@x.com", password="hash-ana"),
        historico.objects.create(
            username="raiz",
            email="raiz@x.com",
            password="hash-raiz",
            perfil="ADMINISTRADOR",
            is_staff=True,
            is_superuser=True,
        ),
    ]
    antes = [tuple(getattr(c, campo) for campo in CAMPOS) for c in contas]

    _migrar(MigrationExecutor(connection).loader.graph.leaf_nodes())

    depois = Usuario.objects.filter(pk__in=[c.pk for c in contas]).order_by("pk")
    assert [tuple(getattr(c, campo) for campo in CAMPOS) for c in depois] == antes
    assert [(c.unidade_id, c.senha_provisoria) for c in depois] == [(None, False), (None, False)]
