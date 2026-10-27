"""Estaticos do admin coletaveis para a CDN da Vercel: DEPL-10 e DEPL-11."""

from pathlib import Path

import pytest
from django.conf import settings
from django.core.management import call_command
from django.test import override_settings

pytestmark = pytest.mark.unit

RAIZ = Path(__file__).resolve().parents[2]


def test_static_root_e_a_pasta_staticfiles():
    """DEPL-10: STATIC_ROOT definido em BASE_DIR / "staticfiles"."""
    assert Path(settings.STATIC_ROOT) == RAIZ / "staticfiles"


def test_staticfiles_fora_do_git():
    """DEPL-10: a saida do collectstatic nao entra no repositorio."""
    linhas = (RAIZ / ".gitignore").read_text().splitlines()
    assert "staticfiles/" in [linha.strip() for linha in linhas]


def test_collectstatic_inclui_o_css_do_admin(tmp_path):
    """DEPL-11: collectstatic grava admin/css/base.css sob STATIC_ROOT."""
    with override_settings(STATIC_ROOT=tmp_path):
        call_command("collectstatic", interactive=False, verbosity=0)
    assert (tmp_path / "admin" / "css" / "base.css").is_file()
