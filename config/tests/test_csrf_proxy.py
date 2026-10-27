"""POST atras do proxy HTTPS da Vercel: DEPL-05.

A Vercel encaminha a requisicao por HTTP com Host e Origin do dominio publico em HTTPS. Sem a
origem em CSRF_TRUSTED_ORIGINS, o Django ve "http://..." contra "https://..." e responde 403.
"""

import pytest
from django.test import Client, override_settings

from contas.models import Usuario

HOST = "kira.vercel.app"
SENHA = "senha-forte-123"


@pytest.fixture
def ana(db):
    return Usuario.objects.create_user(username="ana", email="ana@x.com", password=SENHA)


def _post_de_login(origem):
    cliente = Client(enforce_csrf_checks=True)
    cliente.get("/entrar/", HTTP_HOST=HOST)
    token = cliente.cookies["csrftoken"].value
    return cliente.post(
        "/entrar/",
        {"username": "ana", "password": SENHA, "csrfmiddlewaretoken": token},
        HTTP_HOST=HOST,
        HTTP_ORIGIN=origem,
    )


@override_settings(
    DEBUG=False, ALLOWED_HOSTS=[HOST], CSRF_TRUSTED_ORIGINS=["https://kira.vercel.app"]
)
def test_origem_confiavel_passa_pelo_csrf(ana):
    """DEPL-05: com a origem na lista, o login nao cai em 403 e abre a sessao."""
    resposta = _post_de_login("https://kira.vercel.app")
    assert resposta.status_code != 403
    assert resposta.status_code == 302


@override_settings(
    DEBUG=False, ALLOWED_HOSTS=[HOST], CSRF_TRUSTED_ORIGINS=["https://kira.vercel.app"]
)
def test_origem_fora_da_lista_recebe_403(ana):
    """DEPL-05 (caso de borda): origem fora da lista continua barrada."""
    assert _post_de_login("https://outro.vercel.app").status_code == 403
