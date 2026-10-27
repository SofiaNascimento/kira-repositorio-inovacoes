"""Banco de producao pelo pooler do Supabase: DEPL-06 a DEPL-09 e DEPL-15."""

from pathlib import Path

import pytest

from config.tests.settings_isolados import carregar_settings

pytestmark = pytest.mark.unit

CHAVE = {"DJANGO_SECRET_KEY": "chave-de-teste"}
URL_POOLER = "postgresql://postgres.abcd:s%40nha@aws-0-sa-east-1.pooler.supabase.com:6543/postgres"
LOCAL = {
    "POSTGRES_DB": "kira",
    "POSTGRES_USER": "ruan",
    "POSTGRES_PASSWORD": "",
    "POSTGRES_HOST": "localhost",
    "POSTGRES_PORT": "5433",
}


def _banco(**ambiente):
    return carregar_settings(**CHAVE, **ambiente)["DATABASES"]["default"]


def test_conexao_vem_da_database_url():
    """DEPL-06: cada parte da URL do pooler vai para o campo certo, com a senha decodificada."""
    banco = _banco(DATABASE_URL=URL_POOLER)
    assert banco["ENGINE"] == "django.db.backends.postgresql"
    assert banco["NAME"] == "postgres"
    assert banco["USER"] == "postgres.abcd"
    assert banco["PASSWORD"] == "s@nha"
    assert banco["HOST"] == "aws-0-sa-east-1.pooler.supabase.com"
    assert str(banco["PORT"]) == "6543"


def test_database_url_exige_ssl():
    """DEPL-07: sslmode=require com a DATABASE_URL."""
    assert _banco(DATABASE_URL=URL_POOLER)["OPTIONS"]["sslmode"] == "require"


def test_sslmode_da_url_nao_desliga_o_ssl():
    """DEPL-07 (caso de borda): sslmode=disable na query nao vence o require."""
    banco = _banco(DATABASE_URL=URL_POOLER + "?sslmode=disable")
    assert banco["OPTIONS"]["sslmode"] == "require"


def test_database_url_ajusta_o_banco_ao_pooler_em_modo_transacao():
    """DEPL-08: sem cursores do servidor e sem conexao persistente."""
    banco = _banco(DATABASE_URL=URL_POOLER)
    assert banco["DISABLE_SERVER_SIDE_CURSORS"] is True
    assert banco["CONN_MAX_AGE"] == 0


@pytest.mark.parametrize("ambiente", [LOCAL, {**LOCAL, "DATABASE_URL": ""}])
def test_sem_database_url_usa_o_postgres_local(ambiente):
    """DEPL-09: sem DATABASE_URL (ou vazia), POSTGRES_* sem SSL nem ajuste de pooler."""
    banco = _banco(**ambiente)
    assert banco["ENGINE"] == "django.db.backends.postgresql"
    assert banco["NAME"] == "kira"
    assert banco["USER"] == "ruan"
    assert banco["PASSWORD"] == ""
    assert banco["HOST"] == "localhost"
    assert banco["PORT"] == "5433"
    assert "sslmode" not in banco.get("OPTIONS", {})
    assert banco.get("DISABLE_SERVER_SIDE_CURSORS", False) is not True


def test_dj_database_url_na_secao_de_runtime():
    """DEPL-15: a dependencia nova fica antes da secao de desenvolvimento."""
    linhas = (Path(__file__).resolve().parents[2] / "requirements.txt").read_text().splitlines()
    desenvolvimento = linhas.index("# Desenvolvimento e testes")
    runtime = [linha.split(">")[0].split("=")[0].strip() for linha in linhas[:desenvolvimento]]
    assert "dj-database-url" in runtime
