"""Testes e2e do controle de acesso por negacao padrao (AD-006).

AUTH-09 a AUTH-11. O teste de varredura e o que sustenta a AUTH-09 nas
features seguintes: toda rota nova nasce coberta por ele.
"""

from urllib.parse import urlencode

import pytest
from django.conf import settings
from django.urls import URLPattern, URLResolver, get_resolver
from django.urls.resolvers import RoutePattern
from pytest_django.asserts import assertRedirects

from contas.models import Usuario

SENHA = "senha-forte-123"

# Unicas rotas que respondem a anonimos. O admin tem porteiro proprio e usa
# re_path, que a varredura nao sabe preencher.
# T-B (fundacao-do-redesign): o alto contraste vale antes do login (RED-24, AD-014).
ROTAS_PUBLICAS = {"/entrar/", "/acessibilidade/contraste/"}
NAMESPACES_FORA_DA_VARREDURA = {"admin"}

VALOR_DE_EXEMPLO = {
    "int": "1",
    "str": "x",
    "slug": "x",
    "uuid": "00000000-0000-0000-0000-000000000000",
    "path": "x",
}


def _preencher(rota):
    """Troca cada <conversor:nome> por um valor de exemplo."""
    caminho = rota
    while "<" in caminho:
        inicio, fim = caminho.index("<"), caminho.index(">")
        conversor = caminho[inicio + 1 : fim].split(":")[0] if ":" in caminho[inicio:fim] else "str"
        caminho = caminho[:inicio] + VALOR_DE_EXEMPLO[conversor] + caminho[fim + 1 :]
    return caminho


def _rotas(padroes, prefixo="/"):
    for padrao in padroes:
        if isinstance(padrao, URLResolver):
            if padrao.namespace in NAMESPACES_FORA_DA_VARREDURA:
                continue
            assert isinstance(padrao.pattern, RoutePattern), f"re_path fora da varredura: {padrao}"
            yield from _rotas(padrao.url_patterns, prefixo + _preencher(str(padrao.pattern)))
        elif isinstance(padrao, URLPattern):
            assert isinstance(padrao.pattern, RoutePattern), f"re_path fora da varredura: {padrao}"
            yield prefixo + _preencher(str(padrao.pattern))


def _login_com_next(caminho):
    return f"{settings.LOGIN_URL}?{urlencode({'next': caminho}, safe='/')}"


@pytest.fixture
def ana(db):
    return Usuario.objects.create_user(username="ana", email="ana@x.com", password=SENHA)


@pytest.mark.django_db
def test_toda_rota_interna_redireciona_anonimo_ao_login(client):
    """AUTH-09: varre as rotas registradas; fora da allowlist, todas negam."""
    internas = sorted(set(_rotas(get_resolver().url_patterns)) - ROTAS_PUBLICAS)
    assert "/" in internas, "a varredura precisa enxergar ao menos a home"
    for caminho in internas:
        resposta = client.get(caminho)
        assertRedirects(resposta, _login_com_next(caminho), fetch_redirect_response=False)


@pytest.mark.django_db
def test_anonimo_pedindo_a_home_vai_ao_login_com_next(client):
    """AUTH-09: o caminho pedido segue no parametro next."""
    resposta = client.get("/")
    assertRedirects(resposta, "/entrar/?next=/", fetch_redirect_response=False)


def test_login_com_next_leva_ao_destino_original(client, ana):
    """AUTH-10: o next tem precedencia sobre a home."""
    resposta = client.post(
        "/entrar/?next=/inovacoes/42/",
        {"username": "ana", "password": SENHA, "next": "/inovacoes/42/"},
    )
    assertRedirects(resposta, "/inovacoes/42/", fetch_redirect_response=False)


@pytest.mark.django_db
@pytest.mark.parametrize("perfil", [Usuario.Perfil.USUARIO, Usuario.Perfil.ADMINISTRADOR])
def test_qualquer_perfil_autenticado_acessa_a_consulta(client, perfil):
    """AUTH-11 (alterado pela CONS-09: a tela de consulta e a listagem): o
    acesso as telas de consulta nao depende do perfil."""
    conta = Usuario.objects.create_user(
        username=f"conta-{perfil}", email=f"{perfil}@x.com", perfil=perfil
    )
    client.force_login(conta)
    assert client.get("/inovacoes/").status_code == 200
