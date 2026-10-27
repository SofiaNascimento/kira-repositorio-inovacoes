"""Projeto reconhecido pelo runtime Python da Vercel: DEPL-12 a DEPL-14 e DEPL-20."""

import glob
import importlib
import json
import re
import tomllib
from pathlib import Path

import pytest
from django.conf import settings

pytestmark = pytest.mark.unit

RAIZ = Path(__file__).resolve().parents[2]


def _casa(padrao, caminho):
    """Casamento no estilo do glob da Vercel: chaves {a,b} de um nivel, ** e arquivos com ponto."""
    chaves = re.fullmatch(r"\{(.*)\}", padrao)
    alternativas = chaves.group(1).split(",") if chaves else [padrao]
    return any(
        re.fullmatch(glob.translate(alt, recursive=True, include_hidden=True), caminho)
        for alt in alternativas
    )


def test_python_version_fixa_3_13():
    """DEPL-12: .python-version pede 3.13 (sem ele a Vercel usa 3.12)."""
    assert (RAIZ / ".python-version").read_text().strip() == "3.13"


def test_entrada_wsgi_expoe_application():
    """DEPL-13: a Vercel resolve a entrada pelo WSGI_APPLICATION."""
    assert settings.WSGI_APPLICATION == "config.wsgi.application"
    assert callable(importlib.import_module("config.wsgi").application)


@pytest.fixture
def exclusao():
    configuracao = json.loads((RAIZ / "vercel.json").read_text())
    return configuracao["functions"]["config/wsgi.py"]["excludeFiles"]


@pytest.mark.parametrize(
    "caminho", ["inovacoes/tests/test_models.py", "docs/requisitos.md", ".specs/STATE.md"]
)
def test_vercel_json_tira_do_bundle_o_que_nao_roda(exclusao, caminho):
    """DEPL-14: testes, docs e .specs ficam fora da funcao."""
    assert _casa(exclusao, caminho)


@pytest.mark.parametrize("caminho", ["inovacoes/views.py", "templates/kira.css"])
def test_vercel_json_mantem_o_que_roda(exclusao, caminho):
    """DEPL-14: codigo e templates continuam no bundle."""
    assert not _casa(exclusao, caminho)


def _runtime_do_requirements():
    linhas = (RAIZ / "requirements.txt").read_text().splitlines()
    runtime = linhas[: linhas.index("# Desenvolvimento e testes")]
    return [linha.strip() for linha in runtime if linha.strip() and not linha.startswith("#")]


def test_pyproject_declara_as_mesmas_dependencias_de_runtime():
    """DEPL-20: a Vercel instala do pyproject.toml se for ele o escolhido."""
    projeto = tomllib.loads((RAIZ / "pyproject.toml").read_text())["project"]
    assert projeto["dependencies"] == _runtime_do_requirements()
    assert "Django>=5.2,<5.3" in projeto["dependencies"]
    assert projeto["requires-python"] == ">=3.13,<3.14"
