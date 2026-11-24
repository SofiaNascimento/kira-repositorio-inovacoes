"""Testes e2e de desativar e reativar conta (gestao-por-unidade, T11).

Derivados das ACs GEST-30 a GEST-36, GEST-62, GEST-63 e GEST-67 e dos edge cases
de alvo fora do escopo (.specs/features/gestao-por-unidade/spec.md), e da AD-016.
"""

import re

import pytest
from django.test import Client
from pytest_django.asserts import assertRedirects

from contas.models import Usuario
from contas.tests.conftest import GESTOR, SENHA_NOVA
from inovacoes.models import Categoria, Inovacao, MudancaDeStatus, Reaproveitamento
from inovacoes.tests.visibilidade import exibido

DESATIVADA = "Conta “bia” desativada."
REATIVADA = "Conta “bia” reativada."


def _url(conta_ou_pk):
    pk = getattr(conta_ou_pk, "pk", conta_ou_pk)
    return f"/minha-unidade/contas/{pk}/situacao/"


def _alertas(client):
    html = exibido(client.get("/minha-unidade/").content.decode(), rigoroso=True)
    return re.findall(r'<li class="alerta alerta--success">(.*?)</li>', html)


def _ativa(conta):
    conta.refresh_from_db()
    return conta.is_active


@pytest.fixture
def bia(criar_conta, sede):
    return criar_conta("bia", unidade=sede, first_name="Bia", last_name="Lima", password=SENHA_NOVA)


# --- GEST-30 a GEST-32: as acoes ---


def test_desativar_grava_inativa_e_volta_com_o_alerta(gestor_logado, bia):
    """GEST-30."""
    resposta = gestor_logado.post(_url(bia), {"situacao": "DESATIVADA"})
    assertRedirects(resposta, "/minha-unidade/", fetch_redirect_response=False)
    assert _ativa(bia) is False
    assert _alertas(gestor_logado) == [DESATIVADA]


def test_reativar_grava_ativa_e_volta_com_o_alerta(gestor_logado, bia):
    """GEST-31."""
    Usuario.objects.filter(pk=bia.pk).update(is_active=False)
    resposta = gestor_logado.post(_url(bia), {"situacao": "ATIVA"})
    assertRedirects(resposta, "/minha-unidade/", fetch_redirect_response=False)
    assert _ativa(bia) is True
    assert _alertas(gestor_logado) == [REATIVADA]


@pytest.mark.parametrize(
    ("situacao", "ativa", "alerta"),
    [("DESATIVADA", False, DESATIVADA), ("ATIVA", True, REATIVADA)],
    ids=["desativar", "reativar"],
)
def test_repetir_o_envio_mantem_o_estado_e_o_alerta(gestor_logado, bia, situacao, ativa, alerta):
    """GEST-32: o destino vai no POST; o segundo envio nao inverte."""
    for _ in range(2):
        resposta = gestor_logado.post(_url(bia), {"situacao": situacao})
        assertRedirects(resposta, "/minha-unidade/", fetch_redirect_response=False)
        assert _ativa(bia) is ativa
        assert _alertas(gestor_logado) == [alerta]


@pytest.mark.parametrize(
    "dados", [{}, {"situacao": ""}, {"situacao": "ativa"}, {"situacao": "PENDENTE"}]
)
def test_valor_invalido_responde_400_sem_gravar(gestor_logado, bia, dados):
    """AD-016, design: destino fora de TRANSICOES -> 400."""
    assert gestor_logado.post(_url(bia), dados).status_code == 400
    assert _ativa(bia) is True


def test_get_responde_405(gestor_logado, bia):
    """GEST-33."""
    assert gestor_logado.get(_url(bia)).status_code == 405
    assert _ativa(bia) is True


# --- GEST-34 a GEST-36: efeitos da desativacao ---


def test_conta_desativada_nao_entra(client, gestor_logado, bia):
    """GEST-34: a mensagem atual de credencial invalida."""
    gestor_logado.post(_url(bia), {"situacao": "DESATIVADA"})
    resposta = Client().post("/entrar/", {"username": "bia", "password": SENHA_NOVA})
    assert resposta.status_code == 200
    assert "Usuário ou senha inválidos." in exibido(resposta.content.decode(), rigoroso=True)
    assert "_auth_user_id" not in resposta.wsgi_request.session


def test_sessao_aberta_da_conta_desativada_vira_anonima(gestor_logado, bia):
    """GEST-35: a requisicao seguinte da pessoa vai ao login."""
    pessoa = Client()
    assert pessoa.login(username="bia", password=SENHA_NOVA)
    assert pessoa.get("/inovacoes/").status_code == 200
    gestor_logado.post(_url(bia), {"situacao": "DESATIVADA"})
    assertRedirects(
        pessoa.get("/inovacoes/"), "/entrar/?next=/inovacoes/", fetch_redirect_response=False
    )


def test_desativar_mantem_a_autoria(gestor_logado, bia, sede, norte):
    """GEST-36: inovacao, mudanca de status e reaproveitamento seguem da conta."""
    inovacao = Inovacao.objects.create(
        titulo="Caixa Rapido",
        unidade=sede,
        categoria=Categoria.objects.create(nome="Teste Categoria"),
        problema="Fila.",
        solucao="Senha.",
        contato="Bia",
        autor=bia,
    )
    inovacao.avancar_status(por=bia, status_visto=inovacao.status)
    inovacao.avancar_status(por=bia, status_visto=Inovacao.objects.get(pk=inovacao.pk).status)
    inovacao.registrar_reaproveitamento(unidade=norte, por=bia)
    gestor_logado.post(_url(bia), {"situacao": "DESATIVADA"})
    assert _ativa(bia) is False
    assert Inovacao.objects.get(pk=inovacao.pk).autor_id == bia.pk
    assert list(MudancaDeStatus.objects.values_list("responsavel_id", flat=True)) == [bia.pk] * 2
    assert list(Reaproveitamento.objects.values_list("registrado_por_id", flat=True)) == [bia.pk]


# --- Edge cases: escopo, CSRF e concorrencia ---


@pytest.mark.parametrize(
    "caso",
    ["outra_unidade", "sem_unidade", "proprio_gestor", "outro_gestor", "admin", "inexistente"],
)
def test_alvo_fora_do_escopo_responde_404_sem_gravar(
    gestor_logado, gestor, criar_conta, sede, norte, caso
):
    """GEST-61, GEST-62: a mesma 404 propria; is_active intacto."""
    contas = {
        "outra_unidade": lambda: criar_conta("davi", unidade=norte),
        "sem_unidade": lambda: criar_conta("elis"),
        "proprio_gestor": lambda: gestor,
        "outro_gestor": lambda: criar_conta("fabi", GESTOR, sede),
        "admin": lambda: criar_conta("hugo", Usuario.Perfil.ADMINISTRADOR, sede),
    }
    alvo = contas[caso]() if caso in contas else None
    resposta = gestor_logado.post(_url(alvo or 999999), {"situacao": "DESATIVADA"})
    assert resposta.status_code == 404
    assert "Esta conta não existe ou não pertence à sua unidade." in exibido(
        resposta.content.decode(), rigoroso=True
    )
    if alvo:
        assert _ativa(alvo) is True


def test_csrf_invalido_responde_403_sem_gravar(gestor, bia):
    """GEST-67."""
    client = Client(enforce_csrf_checks=True)
    client.force_login(gestor)
    assert client.post(_url(bia), {"situacao": "DESATIVADA"}).status_code == 403
    assert _ativa(bia) is True


def test_dois_gestores_desativando_terminam_com_a_conta_desativada(
    gestor_logado, criar_conta, sede, bia
):
    """GEST-63: os dois veem o alerta de desativacao."""
    outro = Client()
    outro.force_login(criar_conta("fabi", GESTOR, sede))
    for client in (gestor_logado, outro):
        resposta = client.post(_url(bia), {"situacao": "DESATIVADA"})
        assertRedirects(resposta, "/minha-unidade/", fetch_redirect_response=False)
    assert _ativa(bia) is False
    assert _alertas(gestor_logado) == [DESATIVADA]
    assert _alertas(outro) == [DESATIVADA]


# --- Design: os botoes da tabela ---


@pytest.mark.parametrize(
    ("ativa", "rotulo", "valor"),
    [(True, "Desativar", "DESATIVADA"), (False, "Reativar", "ATIVA")],
    ids=["ativa", "desativada"],
)
def test_botao_da_linha_e_secundario_e_posta_o_destino(gestor_logado, bia, ativa, rotulo, valor):
    """GEST-17, GEST-32, design: um form POST por linha para a rota, botao secundario
    (sem classe de perigo) com o destino no corpo."""
    Usuario.objects.filter(pk=bia.pk).update(is_active=ativa)
    tela = exibido(gestor_logado.get("/minha-unidade/").content.decode(), rigoroso=True)
    formulario = re.search(rf'<form method="post" action="{_url(bia)}">(.*?)</form>', tela, re.S)
    assert formulario
    botoes = re.findall(r"<button([^>]*)>(.*?)</button>", formulario.group(1), re.S)
    assert len(botoes) == 1
    atributos, texto = botoes[0]
    assert texto.strip() == rotulo
    assert 'class="botao--secundario"' in atributos
    assert "perigo" not in atributos
    assert f'name="situacao" value="{valor}"' in atributos
    assert 'name="csrfmiddlewaretoken"' in formulario.group(1)
