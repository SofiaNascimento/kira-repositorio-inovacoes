"""Varredura por papel da area "Minha unidade" (gestao-por-unidade, T8, L-003).

Derivada da GEST-12 (so o gestor abre a area), da GEST-61 e da GEST-62 (conta
fora do escopo ou inexistente -> 404 propria, sem gravar). As rotas saem do
resolver: toda rota nova do namespace "gestao" entra sozinha e precisa passar.
"""

import re

import pytest
from django.http import HttpResponse
from django.test import RequestFactory
from django.urls import URLResolver, get_resolver, reverse
from django.views import View
from pytest_django.asserts import assertRedirects

from contas.models import Usuario
from contas.tests.conftest import GESTOR, SENHA_NOVA
from contas.views_gestao import GestaoDeUnidadeMixin
from inovacoes.tests.visibilidade import exibido

RECUSA = "Acesso restrito a gestores de unidade."
NAO_ENCONTRADA = "Esta conta não existe ou não pertence à sua unidade."

# Um envio valido para qualquer formulario da area: se a recusa falhar, algo grava.
POST_VALIDO = {
    "username": "nova",
    "first_name": "Nova",
    "last_name": "Pessoa",
    "email": "nova@x.com",
    "password1": SENHA_NOVA,
    "password2": SENHA_NOVA,
    "new_password1": SENHA_NOVA,
    "new_password2": SENHA_NOVA,
    "situacao": "DESATIVADA",
}


def _rotas_da_gestao():
    """(nome, tem pk) de cada rota do namespace gestao, lidas do resolver."""
    (area,) = [
        padrao
        for padrao in get_resolver().url_patterns
        if isinstance(padrao, URLResolver) and padrao.namespace == "gestao"
    ]
    return [(padrao.name, "pk" in padrao.pattern.converters) for padrao in area.url_patterns]


def _caminho(nome, tem_pk, pk):
    return reverse(f"gestao:{nome}", kwargs={"pk": pk} if tem_pk else None)


def _enviar(client, metodo, caminho):
    return client.post(caminho, POST_VALIDO) if metodo == "post" else client.get(caminho)


def _estado_do_banco():
    return list(
        Usuario.objects.order_by("pk").values_list(
            "pk", "username", "password", "is_active", "senha_provisoria", "perfil", "unidade_id"
        )
    )


def _main(resposta):
    tela = exibido(resposta.content.decode(), rigoroso=True)
    return tela[tela.index('<main id="conteudo">') : tela.index("</main>")]


@pytest.fixture
def alvo(criar_conta, sede):
    """Conta USUARIO da Sede: alvo das rotas com pk."""
    return criar_conta("bia", unidade=sede, first_name="Bia", last_name="Lima")


@pytest.fixture(
    params=["usuario", "usuario_staff", "usuario_superusuario", "admin", "superusuario"]
)
def nao_gestor(request, criar_conta, sede):
    """Todo papel que nao e gestor, inclusive com is_staff, is_superuser e unidade."""
    if request.param == "superusuario":
        conta = Usuario.objects.create_superuser("root", "root@x.com", SENHA_NOVA)
        assert conta.perfil == Usuario.Perfil.ADMINISTRADOR
        return conta
    campos = {
        "usuario": {},
        "usuario_staff": {"is_staff": True},
        "usuario_superusuario": {"is_superuser": True},
        "admin": {"perfil": Usuario.Perfil.ADMINISTRADOR},
    }[request.param]
    return criar_conta(f"conta_{request.param}", unidade=sede, **campos)


def test_varredura_enxerga_a_area(db):
    """Sanidade: a varredura le ao menos a tela da unidade."""
    assert ("painel", False) in _rotas_da_gestao()


@pytest.mark.parametrize("metodo", ["get", "post"])
def test_quem_nao_e_gestor_recebe_403_propria_em_toda_rota(client, nao_gestor, alvo, metodo):
    """GEST-12: 403 com a pagina propria, exibida, e nada gravado."""
    client.force_login(nao_gestor)
    for nome, tem_pk in _rotas_da_gestao():
        caminho = _caminho(nome, tem_pk, alvo.pk)
        antes = _estado_do_banco()
        resposta = _enviar(client, metodo, caminho)
        assert resposta.status_code == 403, caminho
        assert "contas/gestao/acesso_restrito.html" in [t.name for t in resposta.templates]
        main = _main(resposta)
        assert "<h1>Acesso restrito</h1>" in main, caminho
        assert f"<p>{RECUSA}</p>" in main, caminho
        assert '<a href="/inovacoes/">Voltar para as inovações</a>' in main, caminho
        assert _estado_do_banco() == antes, caminho


@pytest.mark.parametrize("metodo", ["get", "post"])
def test_gestor_de_outra_unidade_recebe_404_propria_nas_rotas_com_pk(
    client, criar_conta, norte, alvo, metodo
):
    """GEST-61, GEST-62: a conta de outra unidade "nao existe" para ele; nada gravado."""
    client.force_login(criar_conta("nina", GESTOR, norte))
    for nome, tem_pk in _rotas_da_gestao():
        if not tem_pk:
            continue
        caminho = _caminho(nome, tem_pk, alvo.pk)
        antes = _estado_do_banco()
        resposta = _enviar(client, metodo, caminho)
        assert resposta.status_code == 404, caminho
        main = _main(resposta)
        assert "<h1>Conta não encontrada</h1>" in main, caminho
        assert f"<p>{NAO_ENCONTRADA}</p>" in main, caminho
        assert _estado_do_banco() == antes, caminho


@pytest.mark.parametrize("metodo", ["get", "post"])
def test_anonimo_vai_ao_login_em_toda_rota(client, alvo, metodo):
    """AD-006: o anonimo nao chega ao porteiro do papel."""
    for nome, tem_pk in _rotas_da_gestao():
        caminho = _caminho(nome, tem_pk, alvo.pk)
        antes = _estado_do_banco()
        resposta = _enviar(client, metodo, caminho)
        assertRedirects(resposta, f"/entrar/?next={caminho}", fetch_redirect_response=False)
        assert _estado_do_banco() == antes, caminho


class _ViewComConta(GestaoDeUnidadeMixin, View):
    def get(self, request, pk):
        return HttpResponse(self.conta.username)


@pytest.mark.parametrize(
    "caso",
    ["outra_unidade", "sem_unidade", "proprio_gestor", "outro_gestor", "admin", "inexistente"],
)
def test_porteiro_responde_404_propria_para_conta_fora_do_escopo(
    gestor, criar_conta, sede, norte, caso
):
    """GEST-61, GEST-62: toda conta fora de administraveis_por e o id inexistente."""
    contas = {
        "outra_unidade": lambda: criar_conta("davi", unidade=norte),
        "sem_unidade": lambda: criar_conta("elis"),
        "proprio_gestor": lambda: gestor,
        "outro_gestor": lambda: criar_conta("fabi", GESTOR, sede),
        "admin": lambda: criar_conta("hugo", Usuario.Perfil.ADMINISTRADOR, sede),
    }
    pk = contas[caso]().pk if caso in contas else 999999
    requisicao = RequestFactory().get("/")
    requisicao.user = gestor
    resposta = _ViewComConta.as_view()(requisicao, pk=pk)
    assert resposta.status_code == 404
    html = resposta.content.decode()
    assert "<h1>Conta não encontrada</h1>" in html
    assert re.search(rf"<p>{NAO_ENCONTRADA}</p>", exibido(html, rigoroso=True))
    assert '<a href="/minha-unidade/">Voltar para Minha unidade</a>' in exibido(html, rigoroso=True)


def test_porteiro_entrega_a_conta_do_escopo_a_view(gestor, criar_conta, sede):
    """GEST-61: a conta USUARIO da unidade chega a view."""
    conta = criar_conta("bia", unidade=sede)
    requisicao = RequestFactory().get("/")
    requisicao.user = gestor
    resposta = _ViewComConta.as_view()(requisicao, pk=conta.pk)
    assert (resposta.status_code, resposta.content) == (200, b"bia")


@pytest.mark.parametrize("nome", ["acesso_restrito", "conta_nao_encontrada"])
def test_paginas_de_recusa_nao_tem_trilha(client, nao_gestor, gestor, criar_conta, norte, nome):
    """RED-30 (decisao do usuario, 2026-11-23): a 403 e a 404 do gestor sem trilha."""
    if nome == "acesso_restrito":
        client.force_login(nao_gestor)
        html = client.get("/minha-unidade/").content.decode()
    else:
        requisicao = RequestFactory().get("/")
        requisicao.user = gestor
        html = _ViewComConta.as_view()(requisicao, pk=criar_conta("davi", unidade=norte).pk)
        html = html.content.decode()
    assert 'aria-label="Você está em"' not in html
