"""Verifica que o modelo de usuario do projeto chegou ao banco.

AUTH-16 / AD-005: a tabela de usuarios e a de contas.Usuario, com a coluna
perfil, e nao a auth_user padrao do Django.
"""

import pytest
from django.contrib.auth import get_user_model
from django.db import connection


@pytest.mark.django_db
def test_tabela_de_usuario_existe_com_perfil_e_email():
    tabela = get_user_model()._meta.db_table
    assert tabela == "contas_usuario"

    with connection.cursor() as cursor:
        colunas = {c.name for c in connection.introspection.get_table_description(cursor, tabela)}

    assert {"perfil", "email"} <= colunas
