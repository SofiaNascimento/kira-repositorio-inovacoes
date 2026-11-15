"""Estaticos coletaveis para a CDN da Vercel: DEPL-10, DEPL-11 e a fonte (RED-05 a RED-07)."""

import re
from pathlib import Path

import pytest
from django.conf import settings
from django.contrib.staticfiles import finders
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


# --- Fonte Inter servida pelo projeto (fundacao-do-redesign: RED-05 a RED-07, AD-013) ---

FONTE = "fontes/inter-latin-wght-normal.woff2"


def test_finders_acha_o_arquivo_da_fonte():
    """RED-06: a fonte mora em static/ (STATICFILES_DIRS) e o finder a acha."""
    achado = finders.find(FONTE)
    assert achado
    assert Path(achado) == RAIZ / "static" / FONTE


def test_collectstatic_copia_a_fonte(tmp_path):
    """RED-06: collectstatic grava fontes/inter-latin-wght-normal.woff2 sob STATIC_ROOT."""
    with override_settings(STATIC_ROOT=tmp_path):
        call_command("collectstatic", interactive=False, verbosity=0)
    copia = tmp_path / FONTE
    assert copia.is_file()
    assert copia.read_bytes() == (RAIZ / "static" / FONTE).read_bytes()


def test_url_da_fonte_na_folha_e_a_do_static_url():
    """RED-06: a URL literal do @font-face e "/" + STATIC_URL + o caminho da fonte."""
    css = (RAIZ / "templates" / "kira.css").read_text()
    urls = re.findall(r"src\s*:\s*url\(([^)]*)\)", css)
    # O Django prefixa o STATIC_URL relativo com o SCRIPT_NAME ("/"); o valor cru e "static/".
    assert urls == ["/" + settings.STATIC_URL.lstrip("/") + FONTE]


def test_licenca_da_fonte_vai_ao_lado_do_arquivo():
    """RED-07: static/fontes/OFL.txt com a SIL Open Font License."""
    licenca = RAIZ / "static" / "fontes" / "OFL.txt"
    assert licenca.is_file()
    assert "SIL Open Font License" in licenca.read_text()
