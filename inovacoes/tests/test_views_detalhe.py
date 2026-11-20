"""Testes e2e da pagina de detalhe da inovacao (/inovacoes/<id>/)."""

import datetime
import re

import pytest
from django.utils.html import escape
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from contas.models import Usuario
from inovacoes.models import Inovacao, MudancaDeStatus, Reaproveitamento, StatusInovacao, Unidade
from inovacoes.tests.visibilidade import exibido

ROTULOS = [
    "Título",
    "Unidade de origem",
    "Categoria",
    "Problema ou dor",
    "Solução aplicada",
    "Resultado ou impacto",
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


def _selo_do_cabecalho(html):
    """(classe de status, rotulo) do selo exibido logo antes do h1 (RCON-28)."""
    achado = re.search(
        r'<div class="cabecalho-pagina">\s*<span class="selo selo--(\w+)">\s*([^<]*?)\s*</span>'
        r"\s*<h1>",
        exibido(html, rigoroso=True),
    )
    assert achado, "sem o selo exibido antes do h1"
    return achado.groups()


def test_detalhe_mostra_h1_e_os_oito_campos_em_lista_de_descricao(logado, criar_inovacao):
    """CONS-12, CONS-42.

    T-F (redesign-consulta, T16, RCON-28): o status sai da ficha e vai para o selo acima do
    h1. A garantia da CONS-12 continua: os oito campos aparecem, o status pelo rotulo.
    """
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
        ("Contato responsável", "Ana Souza (ana@x.com)"),
    ]
    assert [r for r, _ in _pares(html)] == ROTULOS
    assert _selo_do_cabecalho(html) == ("em_teste", "Em teste")
    assert "<dl" in html


def test_detalhe_mostra_o_rotulo_do_status_e_nao_o_valor_interno(logado, criar_inovacao):
    """CONS-12: o status aparece pelo rotulo.

    T-F (redesign-consulta, T16, RCON-28): lido no selo acima do h1, e nao mais na ficha.
    """
    inovacao = criar_inovacao(status=StatusInovacao.DISPONIVEL_PARA_REPLICACAO)
    html = logado.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert _selo_do_cabecalho(html) == ("disponivel_para_replicacao", "Disponível para replicação")
    assert "DISPONIVEL_PARA_REPLICACAO" not in exibido(html, rigoroso=True)


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
# STAT-24: a F5 acrescenta uma, o historico de status com o responsavel junto.
# REAP-43: a F6 acrescenta uma, os reaproveitamentos com a unidade junto.
CONSULTAS_DO_DETALHE = 8


def _links(html, rotulo):
    """hrefs de todos os links com o texto exato do rotulo.

    Depois do href, so um aria-describedby opcional (STAT-41): hidden ou
    aria-hidden fazem o link nao contar como exibido.
    """
    return re.findall(rf'<a href="([^"]*)"(?: aria-describedby="[^"]*")?>\s*{rotulo}\s*</a>', html)


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


AJUDA_DO_AVANCO = "O status avança um estágio por vez e não volta ao anterior."
QUEM_PODE_AVANCAR = "Só quem cadastrou a inovação ou um administrador pode avançar o status."


def _explicacao(secao):
    """Texto do elemento #ciclo-explicacao da secao do ciclo."""
    achado = re.search(r'<p\b[^>]*\bid="ciclo-explicacao"[^>]*>(.*?)</p>', secao, re.S)
    assert achado, "falta o #ciclo-explicacao"
    return achado.group(1).strip()


def _botoes(secao):
    """(atributos, texto) de cada button da secao."""
    return re.findall(r"<button\b([^>]*)>(.*?)</button>", secao, re.S)


@pytest.mark.parametrize("conta", ["autor", "administrador", "terceiro"])
def test_ultimo_estagio_explica_e_ninguem_ve_o_link(client, criar_inovacao, request, conta):
    """STAT-04 (emendada): "Ultimo estagio do ciclo." e nenhum link para /status/."""
    inovacao = criar_inovacao(status=DISPONIVEL)
    client.force_login(request.getfixturevalue(conta))
    html = client.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    secao = _secao(html, "ciclo-titulo")
    assert _explicacao(secao) == "Último estágio do ciclo."
    assert "<a " not in secao
    assert f"/inovacoes/{inovacao.pk}/status/" not in html
    assert "Avançar para" not in html
    assert AJUDA_DO_AVANCO not in html
    assert QUEM_PODE_AVANCAR not in html
    if conta == "terceiro":
        # STAT-05: quem nao pode alterar nao ve controle "Avancar" em lugar nenhum da pagina.
        assert "Avançar" not in html


@pytest.mark.parametrize("conta", ["autor", "administrador"])
def test_ultimo_estagio_mostra_avancar_desabilitado_a_quem_pode_alterar(
    client, criar_inovacao, request, conta
):
    """STAT-38: botao "Avancar status" com aria-disabled, sem link para /status/."""
    inovacao = criar_inovacao(status=DISPONIVEL)
    secao = _ciclo(client, request.getfixturevalue(conta), inovacao)
    botoes = _botoes(secao)
    assert [texto.strip() for _, texto in botoes] == ["Avançar status"]
    assert 'aria-disabled="true"' in botoes[0][0]


def test_ultimo_estagio_nao_mostra_botao_a_quem_nao_pode_alterar(
    client, nao_autor_usuario, criar_inovacao
):
    """STAT-04, STAT-05: no estagio final, quem nao pode alterar nao ve controle algum."""
    inovacao = criar_inovacao(status=DISPONIVEL)
    client.force_login(nao_autor_usuario)
    html = client.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    secao = _secao(html, "ciclo-titulo")
    assert _botoes(secao) == []
    assert "Avançar" not in html
    assert _explicacao(secao) == "Último estágio do ciclo."


@pytest.mark.parametrize("status", [EM_TESTE, VALIDADA], ids=str)
def test_terceiro_nao_ve_o_link_de_avancar(client, terceiro, criar_inovacao, status):
    """STAT-05 (emendada): quem nao pode alterar ve o ciclo sem link nem botao de avancar."""
    inovacao = criar_inovacao(status=status)
    client.force_login(terceiro)
    html = client.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    secao = _secao(html, "ciclo-titulo")
    assert len(_itens_do_ciclo(secao)) == 3
    assert "Avançar" not in html
    assert _botoes(secao) == []
    assert f"/inovacoes/{inovacao.pk}/status/" not in html
    assert "Último estágio do ciclo." not in html


@pytest.mark.parametrize("status", [EM_TESTE, VALIDADA], ids=str)
def test_quem_nao_pode_alterar_le_quem_pode_avancar(
    client, nao_autor_usuario, criar_inovacao, status
):
    """STAT-39, STAT-05: a acao nao aparece, mas a explicacao sim (L-003: staff e superuser)."""
    inovacao = criar_inovacao(status=status)
    client.force_login(nao_autor_usuario)
    html = client.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    secao = _secao(html, "ciclo-titulo")
    assert _explicacao(secao) == QUEM_PODE_AVANCAR
    # STAT-05: nenhum controle "Avancar" em lugar nenhum da pagina, para as tres contas.
    assert "Avançar" not in html
    assert _botoes(secao) == []
    assert AJUDA_DO_AVANCO not in secao


# Atributos que tiram um elemento da tela, do leitor de tela ou do teclado.
ESCONDE = re.compile(r'\s(?:hidden|inert)(?=[\s=/>])|\saria-hidden="true"')


@pytest.mark.parametrize("conta", ["autor", "terceiro"])
@pytest.mark.parametrize("status", [EM_TESTE, VALIDADA, DISPONIVEL], ids=str)
def test_nada_na_secao_do_ciclo_fica_escondido(client, criar_inovacao, request, conta, status):
    """STAT-03, STAT-38 a STAT-40 exibidos de fato; STAT-34: inert tira o link do teclado."""
    inovacao = criar_inovacao(status=status)
    secao = _ciclo(client, request.getfixturevalue(conta), inovacao)
    tags = re.findall(r"<[a-z][^>]*>", secao)
    assert tags, "secao vazia"
    assert [tag for tag in tags if ESCONDE.search(tag)] == []


@pytest.mark.parametrize("conta", ["autor", "administrador"])
@pytest.mark.parametrize("status", [EM_TESTE, VALIDADA], ids=str)
def test_quem_pode_alterar_le_a_ajuda_de_um_estagio_por_vez(
    client, criar_inovacao, request, conta, status
):
    """STAT-40: a ajuda acompanha o link; nem botao desabilitado nem a explicacao de permissao."""
    inovacao = criar_inovacao(status=status)
    secao = _ciclo(client, request.getfixturevalue(conta), inovacao)
    assert _explicacao(secao) == AJUDA_DO_AVANCO
    assert _botoes(secao) == []
    assert QUEM_PODE_AVANCAR not in secao


# --- F5: secao "Historico de status" ---------------------------------------------


def _historico(html):
    secao = _secao(html, "historico-titulo")
    assert re.findall(r"<h2[^>]*>(.*?)</h2>", secao) == ["Histórico de status"]
    itens = re.findall(r"<li\b[^>]*>(.*?)</li>", secao, re.S)
    return [re.sub(r"<[^>]+>", "", item).strip() for item in itens]


def _mudanca(inovacao, responsavel, anterior, novo, data):
    mudanca = MudancaDeStatus.objects.create(
        inovacao=inovacao, status_anterior=anterior, status_novo=novo, responsavel=responsavel
    )
    MudancaDeStatus.objects.filter(pk=mudanca.pk).update(data=data)
    return mudanca


def _utc(*args):
    return datetime.datetime(*args, tzinfo=datetime.UTC)


def test_historico_lista_as_mudancas_do_mais_antigo_ao_mais_recente(
    logado, autor, administrador, criar_inovacao
):
    """STAT-24, STAT-25: a data manda, mesmo contra a ordem de criacao."""
    inovacao = criar_inovacao(status=DISPONIVEL)
    # Criada primeiro, mas com a data mais recente.
    _mudanca(inovacao, administrador, VALIDADA, DISPONIVEL, _utc(2026, 10, 2, 18, 45))
    _mudanca(inovacao, autor, EM_TESTE, VALIDADA, _utc(2026, 10, 1, 12, 5))
    html = logado.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert _historico(html) == [
        "01/10/2026 09:05 — de “Em teste” para “Validada”, por Ana Souza",
        "02/10/2026 15:45 — de “Validada” para “Disponível para replicação”, por carla",
    ]


def test_historico_mostra_a_data_no_fuso_de_sao_paulo(logado, autor, criar_inovacao):
    """STAT-25: 02:30 UTC de 15/09 e 23:30 de 14/09 em America/Sao_Paulo."""
    inovacao = criar_inovacao(status=VALIDADA)
    _mudanca(inovacao, autor, EM_TESTE, VALIDADA, _utc(2026, 9, 15, 2, 30))
    html = logado.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert _historico(html) == ["14/09/2026 23:30 — de “Em teste” para “Validada”, por Ana Souza"]


def test_historico_sem_registros_diz_que_nao_ha_mudancas(logado, criar_inovacao):
    """STAT-26: inovacao sem historico, inclusive a ja avancada antes da F5."""
    inovacao = criar_inovacao(status=VALIDADA)
    secao = _secao(logado.get(f"/inovacoes/{inovacao.pk}/").content.decode(), "historico-titulo")
    assert '<p class="vazio">Nenhuma mudança de status registrada.</p>' in secao
    assert "<li" not in secao


def test_terceiro_ve_o_historico(client, autor, terceiro, criar_inovacao):
    """STAT-27: quem nao pode alterar tambem ve o historico."""
    inovacao = criar_inovacao(status=VALIDADA)
    _mudanca(inovacao, autor, EM_TESTE, VALIDADA, _utc(2026, 10, 1, 12, 5))
    client.force_login(terceiro)
    html = client.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert _historico(html) == ["01/10/2026 09:05 — de “Em teste” para “Validada”, por Ana Souza"]


def test_historico_lista_so_as_mudancas_da_inovacao_aberta(
    logado, autor, administrador, criar_inovacao
):
    """STAT-24, STAT-26: o historico de outra inovacao nao aparece no detalhe."""
    primeira = criar_inovacao(titulo="Planilha de Caixa", status=VALIDADA)
    segunda = criar_inovacao(titulo="Robo de Conciliacao", status=DISPONIVEL)
    sem_historico = criar_inovacao(titulo="Fila de Reembolso", status=EM_TESTE)
    _mudanca(primeira, autor, EM_TESTE, VALIDADA, _utc(2026, 10, 1, 12, 5))
    _mudanca(segunda, administrador, EM_TESTE, VALIDADA, _utc(2026, 10, 3, 13, 0))
    _mudanca(segunda, administrador, VALIDADA, DISPONIVEL, _utc(2026, 10, 4, 14, 30))

    html = logado.get(f"/inovacoes/{primeira.pk}/").content.decode()
    assert _historico(html) == ["01/10/2026 09:05 — de “Em teste” para “Validada”, por Ana Souza"]

    html = logado.get(f"/inovacoes/{segunda.pk}/").content.decode()
    assert _historico(html) == [
        "03/10/2026 10:00 — de “Em teste” para “Validada”, por carla",
        "04/10/2026 11:30 — de “Validada” para “Disponível para replicação”, por carla",
    ]

    secao = _secao(
        logado.get(f"/inovacoes/{sem_historico.pk}/").content.decode(), "historico-titulo"
    )
    assert '<p class="vazio">Nenhuma mudança de status registrada.</p>' in secao
    assert "<li" not in secao


@pytest.mark.parametrize("quantidade", [0, 3])
def test_historico_nao_cresce_em_consultas_com_os_registros(
    logado, autor, administrador, terceiro, criar_inovacao, django_assert_num_queries, quantidade
):
    """STAT-24, STAT-25: tres responsaveis diferentes nao custam consulta a mais (sem N+1)."""
    inovacao = criar_inovacao(status=VALIDADA)
    for conta in [autor, administrador, terceiro][:quantidade]:
        _mudanca(inovacao, conta, EM_TESTE, VALIDADA, _utc(2026, 10, 1, 12, 5))
    with django_assert_num_queries(CONSULTAS_DO_DETALHE):
        resposta = logado.get(f"/inovacoes/{inovacao.pk}/")
    assert len(_historico(resposta.content.decode())) == quantidade


# --- F6: sinalizacao e secao "Reaproveitamentos" ---------------------------------

SINALIZAR = "Sinalizar reaproveitamento"


def _reaproveitamento(inovacao, nome, por, data=None):
    """Registra pelo metodo do modelo (AD-012) e, se pedido, forca a data."""
    registro = inovacao.registrar_reaproveitamento(unidade=Unidade.objects.get(nome=nome), por=por)
    if data is not None:
        Reaproveitamento.objects.filter(pk=registro.pk).update(data=data)
    return registro


def _reaproveitamentos(html):
    """(textos fora de lista, itens da lista) da secao "Reaproveitamentos"."""
    secao = _secao(html, "reaproveitamentos-titulo")
    # L-028, L-030: nada da secao, nem ela, sai da tela ou do leitor de tela.
    assert _secao(exibido(html), "reaproveitamentos-titulo") == secao
    assert re.findall(r"<h2[^>]*>(.*?)</h2>", secao) == ["Reaproveitamentos"]
    lista = re.search(r'<ol class="reaproveitamentos">(.*?)</ol>', secao, re.S)
    itens = re.findall(r"<li\b[^>]*>(.*?)</li>", lista.group(1), re.S) if lista else []
    return secao, [re.sub(r"<[^>]+>", "", item).strip() for item in itens]


def test_disponivel_mostra_o_link_de_sinalizar_a_todo_perfil(
    client, autor, administrador, nao_autor_usuario, criar_inovacao
):
    """REAP-01: autor, terceiro USUARIO (comum, staff, superuser) e administrador."""
    inovacao = criar_inovacao(status=DISPONIVEL)
    for conta in [autor, administrador, nao_autor_usuario]:
        client.force_login(conta)
        html = client.get(f"/inovacoes/{inovacao.pk}/").content.decode()
        assert _links(html, SINALIZAR) == [f"/inovacoes/{inovacao.pk}/reaproveitar/"], conta
        # L-028, L-030: o link e cada ancestral ficam na tela e no leitor de tela.
        assert _links(exibido(html), SINALIZAR) == [f"/inovacoes/{inovacao.pk}/reaproveitar/"], (
            conta
        )


@pytest.mark.parametrize("status", [EM_TESTE, VALIDADA], ids=str)
def test_fora_de_disponivel_nao_ha_link_nem_texto_de_sinalizar(
    client, autor, administrador, nao_autor_usuario, criar_inovacao, status
):
    """REAP-02: nenhum href para /reaproveitar/ nem o texto, para nenhum perfil."""
    inovacao = criar_inovacao(status=status)
    for conta in [autor, administrador, nao_autor_usuario]:
        client.force_login(conta)
        html = client.get(f"/inovacoes/{inovacao.pk}/").content.decode()
        assert "/reaproveitar/" not in html, conta
        assert SINALIZAR not in html, conta


@pytest.mark.parametrize(
    ("nomes", "texto"),
    [
        ([], "Nenhum reaproveitamento registrado."),
        (["Sede"], "Reaproveitada por 1 unidade."),
        (["Sede", "Filial Norte"], "Reaproveitada por 2 unidades."),
    ],
    ids=["zero", "um", "dois"],
)
def test_secao_reaproveitamentos_mostra_a_contagem(logado, autor, criar_inovacao, nomes, texto):
    """REAP-17: o texto muda com zero, um e N reaproveitamentos."""
    inovacao = criar_inovacao(status=DISPONIVEL)
    for nome in nomes:
        _reaproveitamento(inovacao, nome, autor)
    secao, itens = _reaproveitamentos(logado.get(f"/inovacoes/{inovacao.pk}/").content.decode())
    textos = [
        "Nenhum reaproveitamento registrado.",
        "Reaproveitada por 1 unidade.",
        "Reaproveitada por 2 unidades.",
    ]
    assert [t for t in textos if t in secao] == [texto]
    assert len(itens) == len(nomes)


def test_secao_lista_unidade_e_data_do_mais_antigo_ao_mais_recente(
    logado, autor, terceiro, criar_inovacao
):
    """REAP-18: a data manda, mesmo contra a ordem do id; outra inovacao nao aparece."""
    inovacao = criar_inovacao(status=DISPONIVEL)
    outra = criar_inovacao(titulo="Robo de Conciliacao", status=DISPONIVEL)
    # Criado primeiro, mas com a data mais recente.
    _reaproveitamento(inovacao, "Sede", autor, _utc(2026, 10, 5, 15, 0))
    _reaproveitamento(inovacao, "Filial Norte", terceiro, _utc(2026, 10, 2, 15, 0))
    _reaproveitamento(outra, "Filial Sul", autor, _utc(2026, 10, 3, 15, 0))
    _, itens = _reaproveitamentos(logado.get(f"/inovacoes/{inovacao.pk}/").content.decode())
    assert itens == ["Filial Norte — 02/10/2026", "Sede — 05/10/2026"]


@pytest.mark.parametrize("quantidade", [1, 4])
def test_reaproveitamentos_nao_crescem_em_consultas(
    logado, autor, criar_inovacao, django_assert_num_queries, quantidade
):
    """REAP-43: 1 e 4 reaproveitamentos custam o mesmo numero de consultas."""
    inovacao = criar_inovacao(status=DISPONIVEL)
    for nome in ["Sede", "Filial Norte", "Filial Sul", "Filial Leste"][:quantidade]:
        _reaproveitamento(inovacao, nome, autor)
    with django_assert_num_queries(CONSULTAS_DO_DETALHE):
        resposta = logado.get(f"/inovacoes/{inovacao.pk}/")
    assert len(_reaproveitamentos(resposta.content.decode())[1]) == quantidade
