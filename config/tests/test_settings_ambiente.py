"""Settings de producao lidas do ambiente: DEPL-01 a DEPL-04."""

import pytest

from config.tests.settings_isolados import carregar_settings

pytestmark = pytest.mark.unit

CHAVE = {"DJANGO_SECRET_KEY": "chave-de-teste"}


def test_sem_secret_key_o_carregamento_falha():
    """DEPL-01: sem DJANGO_SECRET_KEY, KeyError com o nome da variavel."""
    with pytest.raises(KeyError, match="DJANGO_SECRET_KEY"):
        carregar_settings()


def test_secret_key_vem_do_ambiente():
    """DEPL-01: a chave usada e a do ambiente."""
    assert carregar_settings(**CHAVE)["SECRET_KEY"] == "chave-de-teste"


@pytest.mark.parametrize("valor", [None, "true", "1", ""])
def test_debug_desligado_sem_o_valor_exato_true(valor):
    """DEPL-02: ausente ou qualquer valor diferente de "True" deixa DEBUG = False."""
    ambiente = dict(CHAVE) if valor is None else {**CHAVE, "DJANGO_DEBUG": valor}
    assert carregar_settings(**ambiente)["DEBUG"] is False


def test_debug_ligado_so_com_true():
    """DEPL-02: "True" e o unico valor que liga DEBUG."""
    assert carregar_settings(**CHAVE, DJANGO_DEBUG="True")["DEBUG"] is True


def test_allowed_hosts_sem_espacos_nem_item_vazio():
    """DEPL-03: "kira.vercel.app, localhost," vira dois hosts limpos."""
    settings = carregar_settings(**CHAVE, DJANGO_ALLOWED_HOSTS="kira.vercel.app, localhost,")
    assert settings["ALLOWED_HOSTS"] == ["kira.vercel.app", "localhost"]


def test_csrf_trusted_origins_vem_do_ambiente():
    """DEPL-04: a lista de origens confiaveis vem de DJANGO_CSRF_TRUSTED_ORIGINS."""
    settings = carregar_settings(
        **CHAVE,
        DJANGO_CSRF_TRUSTED_ORIGINS="https://kira.vercel.app, https://kira-git-main.vercel.app",
    )
    assert settings["CSRF_TRUSTED_ORIGINS"] == [
        "https://kira.vercel.app",
        "https://kira-git-main.vercel.app",
    ]


def test_csrf_trusted_origins_vazio_sem_a_variavel():
    """DEPL-04: sem a variavel, nenhuma origem confiavel."""
    assert carregar_settings(**CHAVE)["CSRF_TRUSTED_ORIGINS"] == []
