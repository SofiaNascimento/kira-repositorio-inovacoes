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


CARREGA_NEON = """export DATABASE_URL="$(sed -n 's/^DATABASE_URL=//p' ~/.kira-neon.env)\""""


def test_readme_roda_os_comandos_na_conexao_direta_do_neon():
    """DEPL-17: os comandos de banco leem a URL direta do ~/.kira-neon.env, entre export e unset."""
    linhas = [linha.strip() for linha in _secao_de_deploy().splitlines()]
    comandos = [
        i
        for i, linha in enumerate(linhas)
        if "python manage.py migrate" in linha or "python manage.py createsuperuser" in linha
    ]
    assert comandos
    cargas = [i for i, linha in enumerate(linhas) if linha == CARREGA_NEON]
    assert cargas and cargas[0] < comandos[0]
    assert "unset DATABASE_URL" in linhas[comandos[-1] + 1 :]
    for i in comandos:
        assert "postgresql://" not in linhas[i], linhas[i]


def test_readme_mostra_o_arquivo_do_neon_com_a_conexao_direta():
    """DEPL-17: o exemplo do ~/.kira-neon.env e uma URL direta do Neon, sem -pooler."""
    secao = _secao_de_deploy()
    exemplos = re.findall(r"`DATABASE_URL=(postgresql://[^`]*)`", secao)
    assert exemplos
    for url in exemplos:
        host = urlsplit(url.replace("<", "").replace(">", "")).hostname
        assert host.endswith(".neon.tech"), host
        assert "-pooler" not in host, host
    assert "~/.kira-neon.env" in secao


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
