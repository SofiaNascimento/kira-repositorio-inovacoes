"""Testes e2e da home interna provisoria em /.

Destino padrao do login (AUTH-01) e primeira tela protegida (AUTH-11).
"""

import pytest

from contas.models import Usuario


@pytest.fixture
def ana(db):
    return Usuario.objects.create_user(
        username="ana", email="ana@x.com", password="senha-forte-123"
    )


def test_usuario_autenticado_abre_a_home(client, ana):
    """AUTH-01: o destino padrao do login responde a quem esta autenticado."""
    client.force_login(ana)
    assert client.get("/").status_code == 200


def test_home_identifica_a_conta_e_oferece_sair(client, ana):
    """AUTH-01 e AUTH-13: a home mostra quem esta autenticado e o
    formulario de logout."""
    client.force_login(ana)
    html = client.get("/").content.decode()
    assert "ana" in html
    assert '<form method="post" action="/sair/">' in html
