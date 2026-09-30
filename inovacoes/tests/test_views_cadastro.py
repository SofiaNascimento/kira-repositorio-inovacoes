"""Testes e2e da tela de cadastro de inovacao (/inovacoes/nova/)."""

import pytest
from django.utils import timezone
from pytest_django.asserts import assertRedirects

from contas.models import Usuario
from inovacoes.models import Inovacao, StatusInovacao

NOVA = "/inovacoes/nova/"
CAMPOS = ["titulo", "unidade", "categoria", "problema", "solucao", "resultado", "contato"]


@pytest.fixture
def logado(client, autor):
    client.force_login(autor)
    return client


@pytest.fixture
def dados(unidade, categoria):
    return {
        "titulo": "Conciliação bancária automática",
        "unidade": str(unidade.pk),
        "categoria": str(categoria.pk),
        "problema": "Conciliação manual levava dois dias por mês.",
        "solucao": "Script que cruza o extrato com os lançamentos.",
        "resultado": "Fechamento em duas horas.",
        "contato": "Ana Souza (ana@x.com)",
    }


def test_formulario_abre_com_os_sete_campos_editaveis(logado):
    """INOV-01."""
    resposta = logado.get(NOVA)
    assert resposta.status_code == 200
    assert list(resposta.context["form"].fields) == CAMPOS
    html = resposta.content.decode()
    for campo in CAMPOS:
        assert f'name="{campo}"' in html
    for campo in ["autor", "status", "data_criacao"]:
        assert f'name="{campo}"' not in html


def test_envio_valido_grava_uma_inovacao_com_os_valores_sem_espacos(logado, dados):
    """INOV-02."""
    enviados = {k: f"  {v}  " if k not in ("unidade", "categoria") else v for k, v in dados.items()}
    logado.post(NOVA, enviados)
    assert Inovacao.objects.count() == 1
    inovacao = Inovacao.objects.get()
    for campo in ["titulo", "problema", "solucao", "resultado", "contato"]:
        assert getattr(inovacao, campo) == dados[campo]
    assert str(inovacao.unidade_id) == dados["unidade"]
    assert str(inovacao.categoria_id) == dados["categoria"]


def test_envio_valido_redireciona_a_home(logado, dados):
    """INOV-03: redirect depois do POST; recarregar nao reenvia."""
    assertRedirects(logado.post(NOVA, dados), "/", fetch_redirect_response=False)


def test_autor_e_a_conta_logada(logado, dados, autor):
    """INOV-04."""
    logado.post(NOVA, dados)
    assert Inovacao.objects.get().autor == autor


def test_status_e_data_de_criacao_sao_do_sistema(logado, dados):
    """INOV-05."""
    antes = timezone.now()
    logado.post(NOVA, dados)
    depois = timezone.now()
    inovacao = Inovacao.objects.get()
    assert inovacao.status == StatusInovacao.EM_TESTE
    assert antes <= inovacao.data_criacao <= depois


def test_autor_status_e_data_forjados_no_post_sao_ignorados(logado, dados, autor):
    """INOV-06."""
    outro = Usuario.objects.create_user(username="bruno", email="bruno@x.com")
    dados.update(
        {"autor": str(outro.pk), "status": StatusInovacao.VALIDADA, "data_criacao": "2020-01-01"}
    )
    antes = timezone.now()
    logado.post(NOVA, dados)
    inovacao = Inovacao.objects.get()
    assert inovacao.autor == autor
    assert inovacao.status == StatusInovacao.EM_TESTE
    assert inovacao.data_criacao >= antes


@pytest.mark.django_db
@pytest.mark.parametrize("perfil", [Usuario.Perfil.USUARIO, Usuario.Perfil.ADMINISTRADOR])
def test_qualquer_perfil_cadastra(client, dados, perfil):
    """INOV-08: o cadastro nao depende do perfil."""
    conta = Usuario.objects.create_user(
        username=f"c-{perfil}", email=f"{perfil}@x.com", perfil=perfil
    )
    client.force_login(conta)
    assertRedirects(client.post(NOVA, dados), "/", fetch_redirect_response=False)
    assert Inovacao.objects.get().autor == conta


@pytest.mark.django_db
def test_anonimo_pedindo_o_formulario_vai_ao_login(client):
    """INOV-07."""
    assertRedirects(
        client.get(NOVA), "/entrar/?next=/inovacoes/nova/", fetch_redirect_response=False
    )


@pytest.mark.django_db
def test_anonimo_enviando_o_formulario_vai_ao_login_sem_gravar(client, dados):
    """INOV-07."""
    resposta = client.post(NOVA, dados)
    assertRedirects(resposta, "/entrar/?next=/inovacoes/nova/", fetch_redirect_response=False)
    assert not Inovacao.objects.exists()
