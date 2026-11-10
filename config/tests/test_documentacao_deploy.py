"""Variaveis e passo a passo de deploy documentados: DEPL-16, DEPL-17, DEPL-22 e DEPL-23."""

import os
import re
import runpy
from pathlib import Path
from unittest import mock
from urllib.parse import urlsplit

import dotenv
import pytest

from config.tests.settings_isolados import SETTINGS

pytestmark = pytest.mark.unit

RAIZ = Path(__file__).resolve().parents[2]


class _AmbienteRegistrado(dict):
    """Ambiente que anota cada nome que o settings consulta."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lidos = set()

    def __getitem__(self, nome):
        self.lidos.add(nome)
        return super().__getitem__(nome)

    def __contains__(self, nome):
        self.lidos.add(nome)
        return super().__contains__(nome)

    def get(self, nome, padrao=None):
        self.lidos.add(nome)
        return super().get(nome, padrao)


def _nomes_lidos_pelo_settings():
    lidos = set()
    for ambiente in ({}, {"DATABASE_URL": "postgresql://u:p@h:6543/postgres"}):
        registro = _AmbienteRegistrado(DJANGO_SECRET_KEY="chave-de-teste", **ambiente)
        with (
            mock.patch.object(os, "environ", registro),
            mock.patch.object(dotenv, "load_dotenv", lambda *args, **kwargs: False),
        ):
            runpy.run_path(str(SETTINGS))
        lidos |= registro.lidos
    return lidos


def _secao_de_deploy():
    readme = (RAIZ / "README.md").read_text()
    inicio = re.search(r"^## .*[Dd]eploy.*$", readme, re.MULTILINE)
    assert inicio, "README sem secao de deploy"
    fim = re.search(r"^## ", readme[inicio.end() :], re.MULTILINE)
    return readme[inicio.start() : inicio.end() + fim.start()] if fim else readme[inicio.start() :]


def test_env_example_lista_toda_variavel_lida_pelo_settings():
    """DEPL-16: cada nome lido do ambiente aparece como chave no .env.example."""
    exemplo = (RAIZ / ".env.example").read_text()
    chaves = set(re.findall(r"^#?\s*([A-Z][A-Z0-9_]*)=", exemplo, re.MULTILINE))
    lidos = _nomes_lidos_pelo_settings()
    assert {"DJANGO_CSRF_TRUSTED_ORIGINS", "DATABASE_URL"} <= lidos
    assert lidos <= chaves


@pytest.mark.parametrize(
    "termo",
    [
        "DJANGO_SECRET_KEY",
        "DJANGO_DEBUG",
        "DJANGO_ALLOWED_HOSTS",
        "DJANGO_CSRF_TRUSTED_ORIGINS",
        "DATABASE_URL",
        "manage.py migrate",
        "manage.py createsuperuser",
    ],
)
def test_readme_tem_o_passo_a_passo_de_deploy(termo):
    """DEPL-17: a secao de deploy nomeia as variaveis e os comandos de banco."""
    assert termo in _secao_de_deploy()


@pytest.mark.parametrize(
    "comando", ["python manage.py migrate", "python manage.py createsuperuser"]
)
def test_readme_roda_os_comandos_na_conexao_direta_do_neon(comando):
    """DEPL-17: cada linha da secao de deploy que roda o comando usa a URL direta do Neon."""
    linhas = [linha for linha in _secao_de_deploy().splitlines() if comando in linha]
    assert linhas
    for linha in linhas:
        url = re.search(r"DATABASE_URL='(postgresql://[^']*)'", linha)
        assert url, linha
        host = urlsplit(url.group(1).replace("<", "").replace(">", "")).hostname
        assert host.endswith(".neon.tech"), host
        assert "-pooler" not in host, host


@pytest.mark.parametrize("termo", ["neon.tech", "aws-sa-east-1", "-pooler"])
def test_roteiro_descreve_o_banco_no_neon(termo):
    """DEPL-23: o roteiro cita o dominio, a regiao e o host pooled do Neon."""
    assert termo in (RAIZ / "docs" / "roteiro-deploy.md").read_text()


@pytest.mark.parametrize(
    "arquivo",
    [
        "README.md",
        "docs/roteiro-deploy.md",
        "docs/mapa-de-features.md",
        ".env.example",
        "config/settings.py",
    ],
)
def test_documentacao_nao_cita_o_supabase(arquivo):
    """DEPL-22: o provedor abandonado nao aparece, em nenhuma caixa de letra."""
    assert "supabase" not in (RAIZ / arquivo).read_text().lower()
