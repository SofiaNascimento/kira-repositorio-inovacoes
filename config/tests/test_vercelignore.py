"""Deploy pela Vercel CLI sem vazar o .env: DEPL-18 e DEPL-19.

O .vercelignore e lido com a semantica do .gitignore num repositorio temporario vazio, para que o
.gitignore do projeto (que ja ignora o .env) nao faca o teste passar por engano.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

RAIZ = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def repositorio_vazio(tmp_path_factory):
    pasta = tmp_path_factory.mktemp("vercelignore")
    subprocess.run(["git", "init", "-q", str(pasta)], check=True)
    shutil.copyfile(RAIZ / ".vercelignore", pasta / ".gitignore")
    return pasta


def _ignorado(repositorio, caminho):
    resultado = subprocess.run(
        ["git", "-C", str(repositorio), "check-ignore", "--no-index", "-q", caminho]
    )
    assert resultado.returncode in (0, 1), f"git check-ignore falhou para {caminho}"
    return resultado.returncode == 0


@pytest.mark.parametrize(
    "caminho",
    [
        ".env",
        ".env.producao",
        ".specs/STATE.md",
        ".claude/skills/x.md",
        ".agents/x.json",
        "docs/requisitos.md",
    ],
)
def test_vercelignore_barra_segredos_e_arquivos_de_desenvolvimento(repositorio_vazio, caminho):
    """DEPL-18: o .env e o que so serve ao desenvolvimento nao sobem pela CLI."""
    assert _ignorado(repositorio_vazio, caminho)


@pytest.mark.parametrize(
    "caminho",
    [
        "manage.py",
        "config/settings.py",
        "config/wsgi.py",
        "inovacoes/views.py",
        "templates/kira.css",
        "requirements.txt",
        ".python-version",
        "vercel.json",
    ],
)
def test_vercelignore_mantem_o_que_a_vercel_precisa(repositorio_vazio, caminho):
    """DEPL-18: codigo, templates e arquivos de build continuam no upload."""
    assert not _ignorado(repositorio_vazio, caminho)


def test_pasta_de_vinculo_da_cli_fora_do_git():
    """DEPL-19: a .vercel/ criada pelo `vercel link` nao entra no repositorio."""
    linhas = (RAIZ / ".gitignore").read_text().splitlines()
    assert ".vercel/" in [linha.strip() for linha in linhas]
