"""Testes e2e da pagina de detalhe da inovacao (/inovacoes/<id>/)."""

import datetime
import re

import pytest
from django.utils.html import escape
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from contas.models import Usuario
from inovacoes.models import Inovacao, StatusInovacao

ROTULOS = [
    "Título",
    "Unidade de origem",
    "Categoria",
    "Problema ou dor",
    "Solução aplicada",
    "Resultado ou impacto",
    "Status",
    "Contato responsável",
]


@pytest.fixture
def logado(client, autor):
    client.force_login(autor)
    return client


def _pares(html):
    """Lista de (rotulo, valor) dos <dt>/<dd> da pagina, na ordem em que aparecem."""
    rotulos = re.findall(r"<dt[^>]*>(.*?)</dt>", html, re.S)
    valores = re.findall(r"<dd[^>]*>(.*?)</dd>", html, re.S)
    return [(r.strip(), v.strip()) for r, v in zip(rotulos, valores, strict=True)]


def test_detalhe_mostra_h1_e_os_oito_campos_em_lista_de_descricao(logado, criar_inovacao):
    """CONS-12, CONS-42."""
    inovacao = criar_inovacao(resultado="Fechamento em duas horas.")
    resposta = logado.get(f"/inovacoes/{inovacao.pk}/")
    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert re.search(r"<h1[^>]*>\s*Controle de Caixa\s*</h1>", html)
    assert _pares(html) == [
        ("Título", "Controle de Caixa"),
        ("Unidade de origem", "Teste Unidade"),
        ("Categoria", "Teste Categoria"),
        ("Problema ou dor", "Fechamento de caixa manual e demorado."),
        ("Solução aplicada", "Planilha compartilhada com conferencia diaria."),
        ("Resultado ou impacto", "Fechamento em duas horas."),
        ("Status", "Em teste"),
        ("Contato responsável", "Ana Souza (ana@x.com)"),
    ]
    assert [r for r, _ in _pares(html)] == ROTULOS
    assert "<dl" in html


def test_detalhe_mostra_o_rotulo_do_status_e_nao_o_valor_interno(logado, criar_inovacao):
    """CONS-12: o status aparece pelo rotulo."""
    inovacao = criar_inovacao(status=StatusInovacao.DISPONIVEL_PARA_REPLICACAO)
    html = logado.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert ("Status", "Disponível para replicação") in _pares(html)


def test_detalhe_mostra_cadastrada_por_com_nome_completo_e_data(logado, criar_inovacao):
    """CONS-13."""
    inovacao = criar_inovacao()
    html = logado.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    data = inovacao.data_criacao.astimezone(datetime.timezone(datetime.timedelta(hours=-3)))
    assert f"Cadastrada por Ana Souza em {data:%d/%m/%Y}" in html


def test_detalhe_mostra_o_username_quando_a_conta_nao_tem_nome(logado, criar_inovacao):
    """CONS-13: sem nome nem sobrenome, o autor e o username."""
    bruno = Usuario.objects.create_user(username="bruno", email="bruno@x.com")
    inovacao = criar_inovacao(autor=bruno)
    html = logado.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert "Cadastrada por bruno em " in html


def test_detalhe_mostra_a_data_no_fuso_de_sao_paulo(logado, criar_inovacao):
    """CONS-13: 02:30 UTC de 15/09 e 23:30 de 14/09 em America/Sao_Paulo."""
    inovacao = criar_inovacao()
    Inovacao.objects.filter(pk=inovacao.pk).update(
        data_criacao=datetime.datetime(2026, 9, 15, 2, 30, tzinfo=datetime.UTC)
    )
    html = logado.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert "Cadastrada por Ana Souza em 14/09/2026" in html
    assert "15/09/2026" not in html


def test_resultado_vazio_mostra_nao_informado(logado, criar_inovacao):
    """CONS-14."""
    inovacao = criar_inovacao(resultado="")
    html = logado.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert ("Resultado ou impacto", "Não informado") in _pares(html)


def test_quebras_de_linha_dos_textos_longos_viram_br(logado, criar_inovacao):
    """CONS-16: problema, solucao e resultado."""
    inovacao = criar_inovacao(problema="a\nb", solucao="c\nd", resultado="e\nf")
    pares = dict(_pares(logado.get(f"/inovacoes/{inovacao.pk}/").content.decode()))
    assert pares["Problema ou dor"] == "a<br>b"
    assert pares["Solução aplicada"] == "c<br>d"
    assert pares["Resultado ou impacto"] == "e<br>f"


def test_html_digitado_sai_como_texto_literal(logado, criar_inovacao):
    """CONS-17."""
    inovacao = criar_inovacao(solucao="<b>x</b>", titulo="<i>t</i>", contato="<u>c</u>")
    html = logado.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert "&lt;b&gt;x&lt;/b&gt;" in html
    assert "&lt;i&gt;t&lt;/i&gt;" in html
    assert "&lt;u&gt;c&lt;/u&gt;" in html
    assert "<b>x</b>" not in html
    assert "<i>t</i>" not in html
    assert "<u>c</u>" not in html


def test_detalhe_tem_link_de_volta_para_a_lista(logado, criar_inovacao):
    """CONS-18."""
    inovacao = criar_inovacao()
    html = logado.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert re.search(r'<a href="/inovacoes/">\s*Voltar para a lista de inovações\s*</a>', html)


def test_get_absolute_url_aponta_para_o_detalhe(criar_inovacao):
    """CONS-06: URL canonica do detalhe."""
    inovacao = criar_inovacao()
    assert inovacao.get_absolute_url() == f"/inovacoes/{inovacao.pk}/"


@pytest.mark.parametrize("perfil", ["USUARIO", "ADMINISTRADOR"])
def test_qualquer_perfil_abre_inovacao_de_outro_autor(client, criar_inovacao, perfil):
    """CONS-08."""
    inovacao = criar_inovacao()
    outro = Usuario.objects.create_user(
        username="carla", email="carla@x.com", perfil=perfil, password="senha-forte-123"
    )
    client.force_login(outro)
    resposta = client.get(f"/inovacoes/{inovacao.pk}/")
    assert resposta.status_code == 200
    assert escape("Controle de Caixa") in resposta.content.decode()


def test_anonimo_vai_para_o_login_com_next_do_detalhe(client, criar_inovacao):
    """CONS-07."""
    inovacao = criar_inovacao()
    caminho = f"/inovacoes/{inovacao.pk}/"
    resposta = client.get(caminho)
    assertRedirects(resposta, f"/entrar/?next={caminho}", fetch_redirect_response=False)


def _afirma_pagina_nao_encontrada(resposta):
    assert resposta.status_code == 404
    assertTemplateUsed(resposta, "inovacoes/inovacao_nao_encontrada.html")
    html = resposta.content.decode()
    assert re.search(r"<h1[^>]*>\s*Inovação não encontrada\.\s*</h1>", html)
    assert re.search(r'<a href="/inovacoes/">\s*Voltar para a lista de inovações\s*</a>', html)


def test_id_sem_inovacao_responde_404_com_pagina_propria(logado):
    """CONS-15."""
    _afirma_pagina_nao_encontrada(logado.get("/inovacoes/999999/"))


def test_id_sem_inovacao_responde_o_mesmo_404_com_debug_ligado(logado, settings):
    """CONS-15: sem a pagina tecnica do Django, igual a producao."""
    settings.DEBUG = True
    resposta = logado.get("/inovacoes/999999/")
    _afirma_pagina_nao_encontrada(resposta)
    assert "URLconf" not in resposta.content.decode()


def test_id_nao_numerico_nao_mostra_a_mensagem_de_inovacao(logado):
    """Fora da CONS-15: a rota nao casa e o 404 e o padrao do Django."""
    resposta = logado.get("/inovacoes/abc/")
    assert resposta.status_code == 404
    assert "Inovação não encontrada." not in resposta.content.decode()


# --- F4: acoes de alteracao no detalhe (EDEX-03, EDEX-24) ---------------------

# Consultas do detalhe antes da F4 (sessao, conta, inovacao com select_related e
# a gravacao da sessao): o pode_alterar le autor_id e o perfil ja carregados.
CONSULTAS_DO_DETALHE = 6


def _links(html, rotulo):
    """hrefs de todos os links com o texto exato do rotulo."""
    return re.findall(rf'<a href="([^"]*)">\s*{rotulo}\s*</a>', html)


def test_autor_ve_o_link_editar_no_detalhe(logado, criar_inovacao):
    """EDEX-03."""
    inovacao = criar_inovacao()
    html = logado.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert _links(html, "Editar") == [f"/inovacoes/{inovacao.pk}/editar/"]


def test_administrador_ve_o_link_editar_na_inovacao_de_outro_autor(
    client, administrador, criar_inovacao
):
    """EDEX-03: o administrador pode alterar qualquer inovacao (EDEX-17)."""
    inovacao = criar_inovacao()
    client.force_login(administrador)
    html = client.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert _links(html, "Editar") == [f"/inovacoes/{inovacao.pk}/editar/"]


def test_terceiro_nao_ve_o_link_editar(client, nao_autor_usuario, criar_inovacao):
    """EDEX-24: USUARIO que nao e o autor, inclusive com is_staff ou is_superuser (AD-009)."""
    inovacao = criar_inovacao()
    client.force_login(nao_autor_usuario)
    html = client.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert _links(html, "Editar") == []
    assert f"/inovacoes/{inovacao.pk}/editar/" not in html


@pytest.mark.parametrize("conta", ["autor", "terceiro"])
def test_detalhe_mantem_o_numero_de_consultas(
    client, criar_inovacao, django_assert_num_queries, request, conta
):
    """EDEX-03, EDEX-24: decidir os links nao custa consulta extra."""
    inovacao = criar_inovacao()
    client.force_login(request.getfixturevalue(conta))
    with django_assert_num_queries(CONSULTAS_DO_DETALHE):
        assert client.get(f"/inovacoes/{inovacao.pk}/").status_code == 200


def test_autor_ve_o_link_excluir_no_detalhe(logado, criar_inovacao):
    """EDEX-31."""
    inovacao = criar_inovacao()
    html = logado.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert _links(html, "Excluir") == [f"/inovacoes/{inovacao.pk}/excluir/"]


def test_administrador_ve_o_link_excluir_na_inovacao_de_outro_autor(
    client, administrador, criar_inovacao
):
    """EDEX-31: o administrador pode excluir qualquer inovacao."""
    inovacao = criar_inovacao()
    client.force_login(administrador)
    html = client.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert _links(html, "Excluir") == [f"/inovacoes/{inovacao.pk}/excluir/"]


def test_terceiro_nao_ve_o_link_excluir(client, nao_autor_usuario, criar_inovacao):
    """EDEX-24: USUARIO que nao e o autor, inclusive com is_staff ou is_superuser (AD-009)."""
    inovacao = criar_inovacao()
    client.force_login(nao_autor_usuario)
    html = client.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert _links(html, "Excluir") == []
    assert f"/inovacoes/{inovacao.pk}/excluir/" not in html


def test_administrador_rebaixado_deixa_de_ver_os_links_na_requisicao_seguinte(
    client, administrador, criar_inovacao
):
    """EDEX-24, EDEX-25: o perfil e lido de novo a cada requisicao."""
    inovacao = criar_inovacao()
    client.force_login(administrador)
    html = client.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert _links(html, "Editar") == [f"/inovacoes/{inovacao.pk}/editar/"]
    assert _links(html, "Excluir") == [f"/inovacoes/{inovacao.pk}/excluir/"]

    # update() nao passa pelo save(): o rebaixado mantem o is_staff (AD-009).
    Usuario.objects.filter(pk=administrador.pk).update(perfil=Usuario.Perfil.USUARIO)
    rebaixado = Usuario.objects.get(pk=administrador.pk)
    assert (rebaixado.perfil, rebaixado.is_staff) == (Usuario.Perfil.USUARIO, True)

    html = client.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert _links(html, "Editar") == []
    assert _links(html, "Excluir") == []
    assert f"/inovacoes/{inovacao.pk}/editar/" not in html
    assert f"/inovacoes/{inovacao.pk}/excluir/" not in html


# --- F5: secao "Ciclo de vida" ---------------------------------------------------

EM_TESTE = StatusInovacao.EM_TESTE
VALIDADA = StatusInovacao.VALIDADA
DISPONIVEL = StatusInovacao.DISPONIVEL_PARA_REPLICACAO
ETAPAS = ["Em teste", "Validada", "Disponível para replicação"]


def _secao(html, titulo_id):
    """A <section> rotulada pelo h2 de id titulo_id."""
    inicio = html.index(f'<section aria-labelledby="{titulo_id}">')
    return html[inicio : html.index("</section>", inicio)]


def _ciclo(client, conta, inovacao):
    client.force_login(conta)
    return _secao(client.get(f"/inovacoes/{inovacao.pk}/").content.decode(), "ciclo-titulo")


def _itens_do_ciclo(secao):
    lista = re.search(r'<ol class="ciclo">(.*?)</ol>', secao, re.S).group(1)
    itens = re.findall(r"<li\b[^>]*>(.*?)</li>", lista, re.S)
    return [re.sub(r"<[^>]+>", "", item).strip() for item in itens]


def test_ciclo_de_vida_lista_os_tres_estagios_em_ordem(client, autor, criar_inovacao):
    """STAT-01: h2 "Ciclo de vida" e uma lista ordenada na ordem do ciclo."""
    secao = _ciclo(client, autor, criar_inovacao())
    assert re.findall(r"<h2[^>]*>(.*?)</h2>", secao) == ["Ciclo de vida"]
    itens = _itens_do_ciclo(secao)
    assert [item.removesuffix(" (status atual)") for item in itens] == ETAPAS


@pytest.mark.parametrize(
    ("status", "atual"), [(EM_TESTE, 0), (VALIDADA, 1), (DISPONIVEL, 2)], ids=str
)
def test_ciclo_marca_so_o_estagio_atual_com_texto(client, autor, criar_inovacao, status, atual):
    """STAT-02: "(status atual)" uma vez, junto do rotulo do estagio gravado."""
    inovacao = criar_inovacao(status=status)
    client.force_login(autor)
    html = client.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert html.count("(status atual)") == 1
    esperado = list(ETAPAS)
    esperado[atual] = f"{ETAPAS[atual]} (status atual)"
    assert _itens_do_ciclo(_secao(html, "ciclo-titulo")) == esperado


@pytest.mark.parametrize("conta", ["autor", "administrador"])
@pytest.mark.parametrize(
    ("status", "proximo"),
    [(EM_TESTE, "Validada"), (VALIDADA, "Disponível para replicação")],
    ids=["em_teste", "validada"],
)
def test_quem_pode_alterar_ve_o_link_de_avancar(
    client, criar_inovacao, request, conta, status, proximo
):
    """STAT-03: autor e administrador veem "Avancar para" o proximo, para /status/."""
    inovacao = criar_inovacao(status=status)
    secao = _ciclo(client, request.getfixturevalue(conta), inovacao)
    assert _links(secao, f"Avançar para “{proximo}”") == [f"/inovacoes/{inovacao.pk}/status/"]
    assert "Último estágio do ciclo." not in secao


@pytest.mark.parametrize("conta", ["autor", "administrador", "terceiro"])
def test_ultimo_estagio_explica_e_ninguem_ve_o_link(client, criar_inovacao, request, conta):
    """STAT-04: "Ultimo estagio do ciclo." e nenhum link para /status/, para qualquer conta."""
    inovacao = criar_inovacao(status=DISPONIVEL)
    client.force_login(request.getfixturevalue(conta))
    html = client.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert "<p>Último estágio do ciclo.</p>" in _secao(html, "ciclo-titulo")
    assert "Avançar" not in html
    assert f"/inovacoes/{inovacao.pk}/status/" not in html


@pytest.mark.parametrize("status", [EM_TESTE, VALIDADA], ids=str)
def test_terceiro_nao_ve_o_link_de_avancar(client, terceiro, criar_inovacao, status):
    """STAT-05: quem nao pode alterar ve o ciclo sem a acao."""
    inovacao = criar_inovacao(status=status)
    client.force_login(terceiro)
    html = client.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert len(_itens_do_ciclo(_secao(html, "ciclo-titulo"))) == 3
    assert "Avançar" not in html
    assert f"/inovacoes/{inovacao.pk}/status/" not in html
    assert "Último estágio do ciclo." not in html
