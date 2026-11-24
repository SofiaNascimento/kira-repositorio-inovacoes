"""Testes e2e da troca obrigatoria da senha provisoria (gestao-por-unidade, T14).

Derivados das ACs GEST-40 e GEST-66, do edge case "senha provisoria antes do
papel" e do Independent Test da historia de senha
(.specs/features/gestao-por-unidade/spec.md); AD-017. A varredura le as rotas do
resolver, como a da AD-006, e inclui o admin.
"""

import re

import pytest
from django.test import Client
from django.urls import URLPattern, URLResolver, get_resolver
from django.urls.resolvers import RoutePattern
from pytest_django.asserts import assertRedirects

from contas.models import Usuario
from contas.tests.conftest import GESTOR, SENHA_NOVA
from contas.tests.test_controle_acesso import ROTAS_PUBLICAS, _preencher
from inovacoes.models import Inovacao

TROCA = "/conta/senha/"
SENHA = "provisoria-Senha-41"
# A tela de login do admin e publica (@login_not_required do proprio Django).
PUBLICAS = ROTAS_PUBLICAS | {"/admin/login/"}
LIBERADAS = {TROCA, "/sair/"}


def _preencher_regex(regex):
    """Troca cada grupo nomeado por uma amostra: a primeira alternativa ou "x"."""

    def amostra(grupo):
        corpo = grupo.group(1)
        return corpo.split("|")[0] if re.fullmatch(r"[\w|]+", corpo) else "x"

    return re.sub(r"\(\?P<\w+>([^)]*)\)", amostra, regex).lstrip("^").rstrip("$")


def _parte(padrao):
    if isinstance(padrao.pattern, RoutePattern):
        return _preencher(str(padrao.pattern))
    return _preencher_regex(str(padrao.pattern))


def _rotas(padroes, prefixo="/"):
    """Toda rota do resolver, inclusive as do admin (re_path com amostra)."""
    for padrao in padroes:
        if isinstance(padrao, URLResolver):
            yield from _rotas(padrao.url_patterns, prefixo + _parte(padrao))
        elif isinstance(padrao, URLPattern):
            yield prefixo + _parte(padrao)


def _internas():
    return sorted(set(_rotas(get_resolver().url_patterns)) - PUBLICAS - LIBERADAS)


@pytest.fixture
def provisoria(criar_conta):
    return criar_conta("vivi", password=SENHA, senha_provisoria=True)


@pytest.fixture
def com_provisoria(client, provisoria):
    client.force_login(provisoria)
    return client


# --- GEST-40: a varredura ---


def test_toda_rota_interna_vai_para_a_troca(com_provisoria):
    """GEST-40, AD-017: fora da troca, do sair e das publicas, todas redirecionam."""
    internas = _internas()
    for esperada in (
        "/",
        "/inovacoes/",
        "/minha-unidade/",
        "/admin/",
        "/admin/auth/",
        "/admin/contas/usuario/",
    ):
        assert esperada in internas, "a varredura precisa enxergar a casca, a area e o admin"
    for caminho in internas:
        resposta = com_provisoria.get(caminho)
        assertRedirects(resposta, TROCA, fetch_redirect_response=False, msg_prefix=caminho)


def test_a_troca_abre_com_senha_provisoria(com_provisoria):
    """GEST-40: /conta/senha/ e a excecao; a tela abre."""
    assert com_provisoria.get(TROCA).status_code == 200


def test_sair_por_post_encerra_a_sessao(com_provisoria):
    """GEST-40: /sair/ e a outra excecao; o POST encerra a sessao."""
    assertRedirects(com_provisoria.post("/sair/"), "/entrar/", fetch_redirect_response=False)
    assertRedirects(
        com_provisoria.get("/inovacoes/"),
        "/entrar/?next=/inovacoes/",
        fetch_redirect_response=False,
    )


@pytest.mark.parametrize("caminho", sorted(PUBLICAS))
def test_rota_publica_responde_como_sem_senha_provisoria(criar_conta, provisoria, caminho):
    """GEST-40, AD-006: as rotas publicas respondem como para a conta sem senha provisoria."""
    definitiva = criar_conta("ivo", password=SENHA)
    respostas = []
    for conta in (provisoria, definitiva):
        cliente = Client()
        cliente.force_login(conta)
        resposta = cliente.get(caminho)
        respostas.append((resposta.status_code, resposta.headers.get("Location")))
    assert respostas[0] == respostas[1]
    assert respostas[0][1] != TROCA


# --- GEST-66: antes da checagem de papel ---


@pytest.mark.parametrize(
    ("perfil", "staff", "caminho"),
    [
        (GESTOR, False, "/minha-unidade/"),
        (Usuario.Perfil.USUARIO, False, "/minha-unidade/"),
        (Usuario.Perfil.USUARIO, False, "/admin/"),
        (Usuario.Perfil.USUARIO, True, "/admin/contas/usuario/"),
        (Usuario.Perfil.ADMINISTRADOR, False, "/admin/"),
    ],
    ids=["gestor_area", "usuario_area", "usuario_admin", "usuario_staff_admin", "admin_admin"],
)
def test_senha_provisoria_vem_antes_do_papel(client, criar_conta, sede, perfil, staff, caminho):
    """GEST-66: a area do gestor e o admin mandam para a troca, nao ao 403 nem ao
    login do admin."""
    conta = criar_conta(
        "vivi", perfil, sede if perfil == GESTOR else None, senha_provisoria=True, is_staff=staff
    )
    client.force_login(conta)
    assertRedirects(client.get(caminho), TROCA, fetch_redirect_response=False)


def test_post_tambem_redireciona_sem_gravar(client, criar_conta, sede):
    """GEST-40: o POST de criar conta e o de cadastrar inovacao nao gravam nada."""
    gestor = criar_conta("gil", GESTOR, sede, senha_provisoria=True)
    client.force_login(gestor)
    contas = Usuario.objects.count()
    dados = {
        "username": "nova",
        "first_name": "Nova",
        "last_name": "Conta",
        "email": "nova@x.com",
        "password1": SENHA_NOVA,
        "password2": SENHA_NOVA,
    }
    resposta = client.post("/minha-unidade/contas/nova/", dados)
    assertRedirects(resposta, TROCA, fetch_redirect_response=False)
    assert Usuario.objects.count() == contas
    resposta = client.post("/inovacoes/nova/", {"titulo": "Nao grava"})
    assertRedirects(resposta, TROCA, fetch_redirect_response=False)
    assert not Inovacao.objects.filter(titulo="Nao grava").exists()


@pytest.mark.parametrize(
    ("perfil", "caminho"),
    [(Usuario.Perfil.USUARIO, "/inovacoes/"), (GESTOR, "/minha-unidade/")],
    ids=["usuario_lista", "gestor_area"],
)
def test_sem_senha_provisoria_nada_muda(client, criar_conta, sede, perfil, caminho):
    """GEST-47: sem senha provisoria, a tela abre."""
    conta = criar_conta("ivo", perfil, sede if perfil == GESTOR else None)
    client.force_login(conta)
    assert client.get(caminho).status_code == 200


# --- Independent Test da historia de senha: o fluxo completo ---


def test_fluxo_criar_entrar_trocar_e_chegar_a_lista(client, criar_conta, sede):
    """GEST-21, GEST-40, GEST-43: o gestor cria a conta; a pessoa entra, cai em
    "Trocar senha", nao abre a lista pela URL, troca e chega a lista."""
    gestor = criar_conta("gil", GESTOR, sede)
    client.force_login(gestor)
    client.post(
        "/minha-unidade/contas/nova/",
        {
            "username": "pedro",
            "first_name": "Pedro",
            "last_name": "Alves",
            "email": "pedro@x.com",
            "password1": SENHA,
            "password2": SENHA,
        },
    )
    assert Usuario.objects.get(username="pedro").senha_provisoria is True

    pessoa = Client()
    entrada = pessoa.post("/entrar/", {"username": "pedro", "password": SENHA}, follow=True)
    assert entrada.redirect_chain[-1] == (TROCA, 302)
    assert re.search(r"<h1>Trocar senha</h1>", entrada.content.decode())
    assertRedirects(pessoa.get("/inovacoes/"), TROCA, fetch_redirect_response=False)

    troca = pessoa.post(
        TROCA, {"old_password": SENHA, "new_password1": SENHA_NOVA, "new_password2": SENHA_NOVA}
    )
    assertRedirects(troca, "/inovacoes/", fetch_redirect_response=False)
    lista = pessoa.get("/inovacoes/")
    assert lista.status_code == 200
    assert "Senha alterada." in lista.content.decode()
