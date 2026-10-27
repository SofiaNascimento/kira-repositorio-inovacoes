"""Carrega config/settings.py com um ambiente controlado.

O ambiente do processo fica so com as variaveis passadas, e o load_dotenv vira no-op: sem isso o
.env do desenvolvedor preencheria o que o teste removeu.
"""

import os
import runpy
from pathlib import Path
from unittest import mock

import dotenv

SETTINGS = Path(__file__).resolve().parent.parent / "settings.py"


def carregar_settings(**ambiente):
    """Executa o settings com exatamente `ambiente` e devolve os nomes que ele define."""
    with (
        mock.patch.dict(os.environ, ambiente, clear=True),
        mock.patch.object(dotenv, "load_dotenv", lambda *args, **kwargs: False),
    ):
        return runpy.run_path(str(SETTINGS))
