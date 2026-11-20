"""Testes e2e do detalhe da inovacao no redesign da consulta (R2, RCON-28 a RCON-46)."""

import datetime
import re
from pathlib import Path

import pytest
from django.conf import settings

from contas.models import Usuario
from inovacoes.models import Inovacao, MudancaDeStatus, Reaproveitamento, StatusInovacao, Unidade
from inovacoes.tests.test_folha_v2 import _regras_aninhadas, _seletores, _sem_comentarios
from inovacoes.tests.test_views_detalhe import CONSULTAS_DO_DETALHE
from inovacoes.tests.test_views_sistema_design import CSS, _corpos
from inovacoes.tests.visibilidade import CLASSES_OCULTAS, exibido

EM_TESTE = StatusInovacao.EM_TESTE
VALIDADA = StatusInovacao.VALIDADA
DISPONIVEL = StatusInovacao.DISPONIVEL_PARA_REPLICACAO
ICONES = Path(settings.BASE_DIR) / "templates" / "icones"


@pytest.fixture
def logado(client, autor):
    client.force_login(autor)
    return client


def _pagina(client, inovacao):
    resposta = client.get(f"/inovacoes/{inovacao.pk}/")
    assert resposta.status_code == 200
    return resposta.content.decode()


def _main(html):
    return html[html.index('<main id="conteudo">') : html.index("</main>")]


def _textos(fragmento):
    """Os textos do fragmento, na ordem do codigo, sem as tags."""
    return [" ".join(t.split()) for t in re.split(r"<[^>]+>", fragmento) if t.strip()]


def _cabecalho(html):
    """O `div.cabecalho-pagina` do main, ate o fim do h1 e da linha que o segue."""
    main = _main(html)
    inicio = main.index('<div class="cabecalho-pagina">')
    return main[inicio:]


# --- RCON-28: cabecalho do detalhe ---


def test_cabecalho_do_detalhe_tem_trilha_selo_h1_e_linha_nessa_ordem(logado, criar_inovacao):
    """RCON-28: trilha "Inovações › {título}", selo, h1 e a linha de autoria, na ordem do codigo."""
    inovacao = criar_inovacao(status=VALIDADA)
    tela = exibido(_pagina(logado, inovacao), rigoroso=True)

    trilha = re.search(r'<nav class="trilha" aria-label="Você está em">(.*?)</nav>', tela, re.S)
    assert trilha, "sem a trilha exibida"
    assert _textos(trilha.group(1)) == ["Inovações", "Controle de Caixa"]
    assert re.search(r'<a href="/inovacoes/">Inovações</a>', trilha.group(1))
    assert re.search(r'<li aria-current="page">Controle de Caixa</li>', trilha.group(1))

    cabecalho = re.search(
        r'<div class="cabecalho-pagina">\s*'
        r'<span class="selo selo--validada">\s*Validada\s*</span>\s*'
        r"<h1>Controle de Caixa</h1>\s*"
        r"<p>Cadastrada por Ana Souza em [^<]*</p>",
        tela,
    )
    assert cabecalho, "selo, h1 e linha fora de ordem ou nao exibidos"
    assert trilha.end() < cabecalho.start()
    # L-044: nenhuma das pecas e escondida pela folha.
    assert not {"selo", "selo--validada", "cabecalho-pagina", "trilha"} & CLASSES_OCULTAS


@pytest.mark.parametrize(
    ("status", "classe", "rotulo", "icone"),
    [
        (EM_TESTE, "em_teste", "Em teste", "frasco"),
        (VALIDADA, "validada", "Validada", "visto"),
        (DISPONIVEL, "disponivel_para_replicacao", "Disponível para replicação", "caixa-seta"),
    ],
    ids=str,
)
def test_selo_do_cabecalho_tem_o_icone_do_status_e_o_rotulo(
    logado, criar_inovacao, status, classe, rotulo, icone
):
    """RCON-28, RCON-15: o selo acima do h1 traz o SVG decorativo do status e o rotulo."""
    html = _pagina(logado, criar_inovacao(status=status))
    svg = (ICONES / f"{icone}.svg").read_text().strip()
    assert svg.startswith('<svg aria-hidden="true" ')
    assert re.search(
        rf'<div class="cabecalho-pagina">\s*<span class="selo selo--{classe}">'
        rf"{re.escape(svg)}\s*{re.escape(rotulo)}</span>\s*<h1>",
        html,
    )


def test_linha_de_autoria_tem_autor_data_unidade_e_categoria(logado, criar_inovacao):
    """RCON-28, CONS-13: "Cadastrada por {autor} em {dd/mm/aaaa} · {unidade} · {categoria}".

    A data e a do fuso do projeto: 02:30 UTC de 15/09 e 23:30 de 14/09 em America/Sao_Paulo.
    """
    inovacao = criar_inovacao()
    Inovacao.objects.filter(pk=inovacao.pk).update(
        data_criacao=datetime.datetime(2026, 9, 15, 2, 30, tzinfo=datetime.UTC)
    )
    tela = exibido(_pagina(logado, inovacao), rigoroso=True)
    linha = re.search(r"</h1>\s*<p>([^<]*)</p>", _cabecalho(tela))
    assert linha
    assert (
        linha.group(1) == "Cadastrada por Ana Souza em 14/09/2026 · Teste Unidade · Teste Categoria"
    )


def test_linha_de_autoria_usa_o_username_sem_nome(logado, criar_inovacao):
    """RCON-28 (autor como na CONS-13): sem nome nem sobrenome, o autor e o username."""
    bruno = Usuario.objects.create_user(username="bruno", email="bruno@x.com")
    inovacao = criar_inovacao(autor=bruno)
    tela = exibido(_pagina(logado, inovacao), rigoroso=True)
    linha = re.search(r"</h1>\s*<p>([^<]*)</p>", _cabecalho(tela)).group(1)
    assert re.fullmatch(
        r"Cadastrada por bruno em \d\d/\d\d/\d{4} · Teste Unidade · Teste Categoria", linha
    )


def test_status_nao_aparece_mais_na_ficha(logado, criar_inovacao):
    """RCON-28: o status fica so no selo acima do h1, nao como par da ficha."""
    html = _pagina(logado, criar_inovacao(status=VALIDADA))
    assert not re.search(r"<dt>\s*Status\s*</dt>", html)
    assert html.count('class="selo ') == 1


@pytest.mark.parametrize(
    "url", ["/inovacoes/", "/inovacoes/nova/", "editar", "excluir", "status", "/indicadores/"]
)
def test_outras_telas_nao_ganham_nada_antes_do_h1(logado, criar_inovacao, url):
    """RCON-28: o bloco novo do base e vazio fora do detalhe; o h1 abre o cabecalho de pagina."""
    inovacao = criar_inovacao()
    if not url.startswith("/"):
        url = f"/inovacoes/{inovacao.pk}/{url}/"
    html = logado.get(url).content.decode()
    assert re.search(r'<div class="cabecalho-pagina">\s*<h1>', html), url
    assert 'class="selo ' not in html[: html.index("<h1>")]


# --- RCON-29 a RCON-33, RCON-50: narrativa, resumo lateral e grade ---


def _secao_narrativa(tela):
    inicio = tela.index('<section class="narrativa" aria-labelledby="narrativa-titulo">')
    return tela[inicio : tela.index("</section>", inicio) + len("</section>")]


def _aside(tela):
    inicio = tela.index('<aside aria-label="Resumo da inovação">')
    return tela[inicio : tela.index("</aside>", inicio) + len("</aside>")]


def test_narrativa_tem_os_tres_passos_em_ordem_com_o_texto_completo(logado, criar_inovacao):
    """RCON-29: h2 "Como a inovação funciona"; ol com tres h3 na ordem e o texto inteiro."""
    longo = "Conferencia manual " * 30
    inovacao = criar_inovacao(problema=f"{longo}\nfim", solucao="c\nd", resultado="e\nf")
    secao = _secao_narrativa(exibido(_pagina(logado, inovacao), rigoroso=True))
    assert re.findall(r"<h2[^>]*>(.*?)</h2>", secao) == ["Como a inovação funciona"]
    passos = re.findall(
        r"<li>\s*<h3>(.*?)</h3>\s*<p[^>]*>(.*?)</p>\s*</li>",
        re.search(r"</h2>\s*<ol>(.*?)</ol>", secao, re.S).group(1),
        re.S,
    )
    assert passos == [
        ("Problema ou dor", f"{longo}<br>fim"),
        ("Solução aplicada", "c<br>d"),
        ("Resultado ou impacto", "e<br>f"),
    ]


def test_resultado_vazio_le_resultado_ainda_nao_informado(logado, criar_inovacao):
    """RCON-30: o terceiro passo le "Resultado ainda não informado." em --text-muted."""
    secao = _secao_narrativa(exibido(_pagina(logado, criar_inovacao(resultado="")), rigoroso=True))
    assert re.search(
        r"<h3>Resultado ou impacto</h3>\s*"
        r'<p class="narrativa__vazio">Resultado ainda não informado\.</p>',
        secao,
    )
    assert re.search(r"color\s*:\s*var\(--text-muted\)", _corpos(".narrativa__vazio"))


def test_aside_vem_depois_da_narrativa_e_antes_dos_reaproveitamentos(logado, criar_inovacao):
    """RCON-31: o aside fica entre a narrativa e os reaproveitamentos; contato antes da ficha."""
    tela = exibido(_pagina(logado, criar_inovacao()), rigoroso=True)
    narrativa = tela.index('<section class="narrativa"')
    aside = tela.index('<aside aria-label="Resumo da inovação">')
    reaproveitamentos = tela.index('<section aria-labelledby="reaproveitamentos-titulo">')
    assert narrativa < aside < reaproveitamentos
    lateral = _aside(tela)
    assert lateral.index('<div class="cartao-contato">') < lateral.index(
        '<dl class="ficha-resumo">'
    )
    assert tela.count("<aside") == 1


def test_cartao_de_contato_tem_titulo_texto_com_quebras_e_a_nota(logado, criar_inovacao):
    """RCON-32: titulo, o contato como digitado (quebras preservadas) e a nota."""
    contato = "Ana Souza\nRamal 1234\nana@x.com"
    lateral = _aside(exibido(_pagina(logado, criar_inovacao(contato=contato)), rigoroso=True))
    cartao = re.search(r'<div class="cartao-contato">(.*?)</div>', lateral, re.S).group(1)
    assert re.findall(r"<h2>(.*?)</h2>", cartao) == ["Contato responsável"]
    assert f'<p class="cartao-contato__texto">{contato}</p>' in cartao
    nota = "Procure esta pessoa para tirar dúvidas antes de replicar."
    assert f'<p class="cartao-contato__nota">{nota}</p>' in cartao
    # As quebras digitadas so aparecem na tela porque a folha as preserva.
    assert re.search(r"white-space\s*:\s*pre-line", _corpos(".cartao-contato__texto"))


def test_ficha_tem_os_cinco_pares_na_ordem(logado, autor, terceiro, criar_inovacao):
    """RCON-33: Unidade de origem, Categoria, Cadastrada por, Cadastrada em e Reaproveitamentos."""
    inovacao = criar_inovacao(status=DISPONIVEL)
    Inovacao.objects.filter(pk=inovacao.pk).update(
        data_criacao=datetime.datetime(2026, 9, 15, 2, 30, tzinfo=datetime.UTC)
    )
    for nome in ["Sede", "Filial Norte"]:
        inovacao.registrar_reaproveitamento(unidade=Unidade.objects.get(nome=nome), por=terceiro)
    lateral = _aside(exibido(_pagina(logado, inovacao), rigoroso=True))
    ficha = re.search(r'<dl class="ficha-resumo">(.*?)</dl>', lateral, re.S).group(1)
    pares = re.findall(r"<dt>(.*?)</dt>\s*<dd>(.*?)</dd>", ficha, re.S)
    assert pares == [
        ("Unidade de origem", "Teste Unidade"),
        ("Categoria", "Teste Categoria"),
        ("Cadastrada por", "Ana Souza"),
        ("Cadastrada em", "14/09/2026"),
        ("Reaproveitamentos", "2"),
    ]
    assert len(re.findall(r"<dt>", ficha)) == 5


def test_narrativa_e_contato_saem_escapados(logado, criar_inovacao):
    """CONS-17 (edge case da R2): HTML digitado no problema e no contato sai como texto."""
    inovacao = criar_inovacao(problema="<b>p</b>", contato="<u>c</u>")
    html = _pagina(logado, inovacao)
    assert "&lt;b&gt;p&lt;/b&gt;" in _secao_narrativa(html)
    assert '<p class="cartao-contato__texto">&lt;u&gt;c&lt;/u&gt;</p>' in _aside(html)
    assert "<b>p</b>" not in html
    assert "<u>c</u>" not in html


def _regras_no_contexto(contexto):
    return {
        seletor: corpo
        for ctx, lista, corpo in _regras_aninhadas(_sem_comentarios(CSS))
        if ctx == contexto
        for seletor in _seletores(lista)
    }


def test_grade_de_duas_colunas_so_a_partir_de_45rem():
    """RCON-50, RCON-31: abaixo de 720px uma coluna; a partir de 45rem o aside vai a direita.

    O aside fica na coluna 2, linhas 1 a 3, ao lado da narrativa que o precede (RCON-47).
    """
    globais = _regras_no_contexto(())
    assert re.search(r"display\s*:\s*grid", globais[".detalhe"])
    assert "grid-template-columns" not in globais[".detalhe"]
    assert not any(
        "grid-template-columns" in corpo or "grid-column" in corpo
        for seletor, corpo in globais.items()
        if seletor.startswith(".detalhe")
    )
    larga = _regras_no_contexto(("@media (min-width: 45rem)",))
    assert re.search(
        r"grid-template-columns\s*:\s*minmax\(0,\s*2fr\)\s+minmax\(0,\s*1fr\)",
        larga[".detalhe"],
    )
    assert re.search(r"grid-column\s*:\s*1\s*;", larga[".detalhe > *"])
    assert re.search(r"grid-column\s*:\s*2\s*;", larga[".detalhe > aside"])
    assert re.search(r"grid-row\s*:\s*1\s*/\s*span\s+3\s*;", larga[".detalhe > aside"])


def test_passos_da_narrativa_sao_numerados_pela_folha_como_decoracao():
    """RCON-29: o numero do passo vem do counter no ::before, com texto alternativo vazio."""
    assert re.search(r"counter-reset\s*:\s*passo", _corpos(".narrativa ol"))
    assert re.search(r"counter-increment\s*:\s*passo", _corpos(".narrativa li"))
    antes = _corpos(".narrativa li::before")
    assert re.search(r'content\s*:\s*counter\(passo\)\s*/\s*""', antes)


def test_regras_da_ficha_antiga_sairam_da_folha():
    """RCON-33: a ficha antiga, o selo no dd e o destaque do contato nao tem mais uso."""
    sem_comentarios = _sem_comentarios(CSS)
    seletores = [
        s
        for lista, _ in re.findall(r"([^{}]+)\{([^}]*)\}", sem_comentarios)
        for s in _seletores(lista)
    ]
    assert [s for s in seletores if re.search(r"\.ficha(?![\w-])|\.destaque\b", s)] == []


# --- RCON-34, RCON-41 (texto), RCON-42: ciclo de vida no resumo ---

AJUDA_DO_AVANCO = "O status avança um estágio por vez e não volta ao anterior."
QUEM_PODE_AVANCAR = "Só quem cadastrou a inovação ou um administrador pode avançar o status."
ULTIMO_ESTAGIO = "Último estágio do ciclo. O status avança um estágio por vez e não volta."
PERFIS = ["autor", "administrador", "terceiro", "staff"]
PODEM_ALTERAR = {"autor", "administrador"}


@pytest.fixture
def staff(db):
    """USUARIO com is_staff que nao e o autor: nao pode alterar (AD-009, L-003)."""
    return Usuario.objects.create_user(username="dora_staff", email="ds@x.com", is_staff=True)


def _como(client, request, perfil, inovacao):
    client.force_login(request.getfixturevalue(perfil))
    return _pagina(client, inovacao)


def _ciclo_exibido(html):
    """O bloco "Ciclo de vida" do aside, como a tela o exibe."""
    lateral = _aside(exibido(html, rigoroso=True))
    inicio = lateral.index('<section aria-labelledby="ciclo-titulo">')
    return lateral[inicio : lateral.index("</section>", inicio)]


def _etapas(bloco):
    lista = re.search(r'<ol class="etapas">(.*?)</ol>', bloco, re.S).group(1)
    return [
        (atributos, " ".join(re.sub(r"<[^>]+>", "", item).split()))
        for atributos, item in re.findall(r"<li\b([^>]*)>(.*?)</li>", lista, re.S)
    ]


@pytest.mark.parametrize(
    ("status", "esperado"),
    [
        (
            EM_TESTE,
            [
                "Em teste (status atual)",
                "Validada · próxima etapa",
                "Disponível para replicação · próxima etapa",
            ],
        ),
        (
            VALIDADA,
            [
                "Em teste · concluída",
                "Validada (status atual)",
                "Disponível para replicação · próxima etapa",
            ],
        ),
        (
            DISPONIVEL,
            [
                "Em teste · concluída",
                "Validada · concluída",
                "Disponível para replicação (status atual)",
            ],
        ),
    ],
    ids=str,
)
def test_etapas_dizem_a_situacao_em_texto_e_so_a_atual_tem_aria_current(
    logado, criar_inovacao, status, esperado
):
    """RCON-34: h2 "Ciclo de vida", ol com as tres etapas na ordem e a situacao em texto."""
    bloco = _ciclo_exibido(_pagina(logado, criar_inovacao(status=status)))
    assert re.findall(r"<h2[^>]*>(.*?)</h2>", bloco) == ["Ciclo de vida"]
    etapas = _etapas(bloco)
    assert [texto for _, texto in etapas] == esperado
    atuais = [texto for atributos, texto in etapas if 'aria-current="step"' in atributos]
    assert atuais == [t for t in esperado if t.endswith("(status atual)")]


def test_marcadores_das_etapas_sao_decorativos(logado, criar_inovacao):
    """RCON-34: cada etapa tem um marcador `aria-hidden="true"`, fora do texto lido."""
    html = _pagina(logado, criar_inovacao(status=VALIDADA))
    lateral = _aside(html)
    itens = re.findall(r'<li class="etapa etapa--(\w+)"[^>]*>(.*?)</li>', lateral, re.S)
    assert [situacao for situacao, _ in itens] == ["concluida", "atual", "futura"]
    for _, item in itens:
        assert re.match(r'\s*<span class="etapa__marcador" aria-hidden="true">', item)
    # O texto da situacao, fora do marcador, continua exibido (L-028, L-044).
    assert not {"etapas", "etapa", "etapa--atual"} & CLASSES_OCULTAS


def test_ciclo_fica_entre_o_contato_e_a_ficha(logado, criar_inovacao):
    """RCON-31: dentro do aside, contato, ciclo de vida e ficha, nessa ordem."""
    lateral = _aside(exibido(_pagina(logado, criar_inovacao()), rigoroso=True))
    contato = lateral.index('<div class="cartao-contato">')
    ciclo = lateral.index('<section aria-labelledby="ciclo-titulo">')
    ficha = lateral.index('<dl class="ficha-resumo">')
    assert contato < ciclo < ficha


def _explicacao(bloco):
    achado = re.search(r'<p\b[^>]*\bid="ciclo-explicacao"[^>]*>(.*?)</p>', bloco, re.S)
    assert achado, "sem a explicacao exibida"
    return achado.group(1).strip()


@pytest.mark.parametrize("perfil", PERFIS)
@pytest.mark.parametrize("status", [EM_TESTE, VALIDADA, DISPONIVEL], ids=str)
def test_explicacao_do_ciclo_por_status_e_perfil(
    client, request, criar_inovacao, staff, status, perfil
):
    """RCON-41, RCON-42: o texto exato por status e por quem pode ou nao alterar (L-003)."""
    bloco = _ciclo_exibido(_como(client, request, perfil, criar_inovacao(status=status)))
    if status == DISPONIVEL:
        esperado = ULTIMO_ESTAGIO
    elif perfil in PODEM_ALTERAR:
        esperado = AJUDA_DO_AVANCO
    else:
        esperado = QUEM_PODE_AVANCAR
    assert _explicacao(bloco) == esperado
    outros = {ULTIMO_ESTAGIO, AJUDA_DO_AVANCO, QUEM_PODE_AVANCAR} - {esperado}
    assert [texto for texto in outros if texto in bloco] == []


@pytest.mark.parametrize("perfil", PERFIS)
@pytest.mark.parametrize("status", [EM_TESTE, VALIDADA, DISPONIVEL], ids=str)
def test_botao_desabilitado_so_no_ultimo_estagio_para_quem_pode_alterar(
    client, request, criar_inovacao, staff, status, perfil
):
    """RCON-42: "Avançar status" com aria-disabled, descrito pelo texto, so para quem pode."""
    bloco = _ciclo_exibido(_como(client, request, perfil, criar_inovacao(status=status)))
    botoes = re.findall(r"<button\b([^>]*)>(.*?)</button>", bloco, re.S)
    if status == DISPONIVEL and perfil in PODEM_ALTERAR:
        assert [texto.strip() for _, texto in botoes] == ["Avançar status"]
        atributos = botoes[0][0]
        assert 'aria-disabled="true"' in atributos
        assert re.search(r"\sdisabled\b", atributos.replace("aria-disabled", "")) is None
        assert 'aria-describedby="ciclo-explicacao"' in atributos
    else:
        assert botoes == []


# --- RCON-37 a RCON-41: acoes em hierarquia no cabecalho ---


def _acoes(tela):
    """([(classe, texto, href)] fora do grupo de perigo, [...] dentro dele) do cabecalho exibido.

    Devolve None quando o cabecalho nao tem o grupo de acoes.
    """
    cabecalho = _cabecalho(tela)
    cabecalho = cabecalho[: cabecalho.index('<div class="detalhe">')]
    inicio = cabecalho.find('<div class="acoes-pagina">')
    if inicio == -1:
        return None
    grupo = cabecalho[inicio:]
    corte = grupo.find('<div class="acoes-pagina__perigo">')
    principal, perigo = (grupo, "") if corte == -1 else (grupo[:corte], grupo[corte:])

    def links(trecho):
        return [
            (
                re.search(r'\bclass="([^"]*)"', atributos).group(1),
                " ".join(texto.split()),
                re.search(r'\bhref="([^"]*)"', atributos).group(1),
            )
            for atributos, texto in re.findall(r"<a\b([^>]*)>([^<]*)</a>", trecho)
        ]

    return links(principal), links(perigo)


def _esperado(status, perfil, pk):
    pode = perfil in PODEM_ALTERAR
    primaria = []
    if status == DISPONIVEL:
        primaria = [("botao", "Sinalizar reaproveitamento", f"/inovacoes/{pk}/reaproveitar/")]
    elif pode:
        proximo = "Validada" if status == EM_TESTE else "Disponível para replicação"
        primaria = [("botao", f"Avançar para “{proximo}”", f"/inovacoes/{pk}/status/")]
    if not pode:
        return (primaria, []) if primaria else None
    editar = ("botao botao--secundario", "Editar", f"/inovacoes/{pk}/editar/")
    excluir = ("botao botao--perigo", "Excluir", f"/inovacoes/{pk}/excluir/")
    return [*primaria, editar], [excluir]


@pytest.mark.parametrize("perfil", PERFIS)
@pytest.mark.parametrize("status", [EM_TESTE, VALIDADA, DISPONIVEL], ids=str)
def test_acoes_do_cabecalho_por_status_e_perfil(
    client, request, criar_inovacao, staff, status, perfil
):
    """RCON-37 a RCON-40: a primaria certa, Editar depois e Excluir por ultimo no grupo separado."""
    inovacao = criar_inovacao(status=status)
    tela = exibido(_como(client, request, perfil, inovacao), rigoroso=True)
    acoes = _acoes(tela)
    assert acoes == _esperado(status, perfil, inovacao.pk)
    if acoes:
        # RCON-40: no maximo uma acao primaria (botao sem variante).
        principal, perigo = acoes
        assert len([classe for classe, _, _ in principal + perigo if classe == "botao"]) <= 1
    assert not {"acoes-pagina", "acoes-pagina__perigo", "botao"} & CLASSES_OCULTAS


@pytest.mark.parametrize("perfil", ["terceiro", "staff"])
@pytest.mark.parametrize("status", [EM_TESTE, VALIDADA, DISPONIVEL], ids=str)
def test_quem_nao_pode_alterar_nao_ve_avancar_editar_nem_excluir(
    client, request, criar_inovacao, staff, status, perfil
):
    """RCON-41: sem "Avançar para …", "Editar" e "Excluir" a USUARIO, com is_staff ou nao."""
    inovacao = criar_inovacao(status=status)
    html = _como(client, request, perfil, inovacao)
    tela = exibido(html, rigoroso=True)
    textos = [" ".join(t.split()) for t in re.findall(r"<a\b[^>]*>([^<]*)</a>", tela)]
    assert [t for t in textos if t.startswith("Avançar para") or t in ("Editar", "Excluir")] == []
    for sufixo in ("status", "editar", "excluir"):
        assert f"/inovacoes/{inovacao.pk}/{sufixo}/" not in html


@pytest.mark.parametrize("perfil", ["autor", "administrador"])
@pytest.mark.parametrize("status", [EM_TESTE, VALIDADA], ids=str)
def test_avancar_e_descrito_pela_explicacao_do_bloco_do_ciclo(
    client, request, criar_inovacao, status, perfil
):
    """RCON-37: o link do cabecalho aponta, por aria-describedby, para a explicacao do ciclo."""
    inovacao = criar_inovacao(status=status)
    tela = exibido(_como(client, request, perfil, inovacao), rigoroso=True)
    link = re.search(
        rf'<a class="botao" href="/inovacoes/{inovacao.pk}/status/"[^>]*>', _cabecalho(tela)
    )
    assert link
    alvo = re.search(r'aria-describedby="([^"]*)"', link.group(0)).group(1)
    bloco = _ciclo_exibido(tela)
    assert re.search(rf'<p\b[^>]*\bid="{alvo}"[^>]*>(.*?)</p>', bloco).group(1) == AJUDA_DO_AVANCO
    assert tela.count(f'id="{alvo}"') == 1


def test_acoes_ficam_depois_da_linha_de_autoria(logado, criar_inovacao):
    """RCON-39: as acoes vem no cabecalho, depois do h1 e da linha "Cadastrada por"."""
    tela = exibido(_pagina(logado, criar_inovacao()), rigoroso=True)
    assert re.search(
        r"<h1>Controle de Caixa</h1>\s*<p>Cadastrada por [^<]*</p>\s*"
        r'<div class="acoes-pagina">',
        tela,
    )


def test_grupo_de_perigo_e_separado_por_divisor_e_32px():
    """RCON-39: o Excluir fica afastado (divisor vertical e 32px); os botoes quebram de linha."""
    assert re.search(r"flex-wrap\s*:\s*wrap", _corpos(".acoes-pagina"))
    perigo = _corpos(".acoes-pagina__perigo")
    assert re.search(r"padding-left\s*:\s*32px", perigo)
    assert re.search(r"border-left\s*:\s*1px solid var\(--border\)", perigo)


# --- RCON-43 a RCON-46: historico como linha do tempo ---


def _utc(*args):
    return datetime.datetime(*args, tzinfo=datetime.UTC)


def _mudanca(inovacao, responsavel, anterior, novo, data):
    """Grava direto, so para preparar o historico; o caminho da aplicacao e o metodo (AD-011)."""
    mudanca = MudancaDeStatus.objects.create(
        inovacao=inovacao, status_anterior=anterior, status_novo=novo, responsavel=responsavel
    )
    MudancaDeStatus.objects.filter(pk=mudanca.pk).update(data=data)


def _linha_do_tempo(html):
    """(data e hora, frase) de cada item exibido do `ol.linha-do-tempo`."""
    tela = exibido(html, rigoroso=True)
    inicio = tela.index('<section aria-labelledby="historico-titulo">')
    secao = tela[inicio : tela.index("</section>", inicio)]
    assert re.findall(r"<h2[^>]*>(.*?)</h2>", secao) == ["Histórico de status"]
    lista = re.search(r'<ol class="linha-do-tempo">(.*?)</ol>', secao, re.S).group(1)
    return [
        (data, " ".join(frase.split()))
        for data, frase in re.findall(r"<li>\s*<time>(.*?)</time>(.*?)</li>", lista, re.S)
    ]


@pytest.mark.parametrize(
    ("status", "mudancas", "cadastro"),
    [
        (DISPONIVEL, [], "Cadastrada como “Disponível para replicação”, por Ana Souza"),
        (DISPONIVEL, [(VALIDADA, DISPONIVEL)], "Cadastrada como “Validada”, por Ana Souza"),
        (VALIDADA, [(EM_TESTE, VALIDADA)], "Cadastrada como “Em teste”, por Ana Souza"),
    ],
    ids=["sem_mudancas", "nasceu_validada", "nasceu_em_teste"],
)
def test_primeiro_item_e_o_cadastro_com_data_hora_e_status_inicial(
    logado, autor, criar_inovacao, status, mudancas, cadastro
):
    """RCON-43, RCON-45: data e hora no fuso; status anterior da 1a mudanca ou o atual."""
    inovacao = criar_inovacao(status=status)
    Inovacao.objects.filter(pk=inovacao.pk).update(data_criacao=_utc(2026, 9, 15, 2, 30))
    for anterior, novo in mudancas:
        _mudanca(inovacao, autor, anterior, novo, _utc(2026, 10, 1, 12, 5))
    itens = _linha_do_tempo(_pagina(logado, inovacao))
    assert itens[0] == ("14/09/2026 23:30", cadastro)
    assert len(itens) == len(mudancas) + 1


def test_cadastro_usa_o_username_do_autor_sem_nome(logado, criar_inovacao):
    """RCON-43 (autor como na CONS-13): sem nome completo, o username."""
    bruno = Usuario.objects.create_user(username="bruno", email="bruno@x.com")
    inovacao = criar_inovacao(autor=bruno)
    [(_, frase)] = _linha_do_tempo(_pagina(logado, inovacao))
    assert frase == "Cadastrada como “Em teste”, por bruno"


def test_mudancas_seguem_o_cadastro_da_mais_antiga_a_mais_recente(
    logado, autor, administrador, criar_inovacao
):
    """RCON-44: cada mudanca com data e hora e "De “X” para “Y”, por {responsável}"."""
    inovacao = criar_inovacao(status=DISPONIVEL)
    Inovacao.objects.filter(pk=inovacao.pk).update(data_criacao=_utc(2026, 9, 30, 12, 0))
    # Criada primeiro, mas com a data mais recente.
    _mudanca(inovacao, administrador, VALIDADA, DISPONIVEL, _utc(2026, 10, 2, 18, 45))
    _mudanca(inovacao, autor, EM_TESTE, VALIDADA, _utc(2026, 10, 1, 12, 5))
    assert _linha_do_tempo(_pagina(logado, inovacao)) == [
        ("30/09/2026 09:00", "Cadastrada como “Em teste”, por Ana Souza"),
        ("01/10/2026 09:05", "De “Em teste” para “Validada”, por Ana Souza"),
        ("02/10/2026 15:45", "De “Validada” para “Disponível para replicação”, por carla"),
    ]


def test_pontos_da_linha_do_tempo_sao_decorativos(logado, autor, criar_inovacao):
    """RCON-46: cada item tem o ponto `aria-hidden="true"`; o do cadastro e o vazado."""
    inovacao = criar_inovacao(status=VALIDADA)
    _mudanca(inovacao, autor, EM_TESTE, VALIDADA, _utc(2026, 10, 1, 12, 5))
    html = _pagina(logado, inovacao)
    lista = re.search(r'<ol class="linha-do-tempo">(.*?)</ol>', html, re.S).group(1)
    pontos = re.findall(r"<li>\s*<span ([^>]*)></span>\s*<time>", lista)
    assert pontos == [
        'class="linha-do-tempo__ponto linha-do-tempo__ponto--cadastro" aria-hidden="true"',
        'class="linha-do-tempo__ponto" aria-hidden="true"',
    ]
    assert not {"linha-do-tempo", "linha-do-tempo__ponto"} & CLASSES_OCULTAS
    assert ".historico" not in _sem_comentarios(CSS)


@pytest.mark.parametrize("quantidade", [0, 3])
def test_linha_do_tempo_mantem_as_consultas_do_detalhe(
    logado, autor, administrador, terceiro, criar_inovacao, django_assert_num_queries, quantidade
):
    """RCON-36: CONSULTAS_DO_DETALHE = 8 com 0 e 3 mudancas de responsaveis diferentes."""
    inovacao = criar_inovacao(status=VALIDADA)
    for conta in [autor, administrador, terceiro][:quantidade]:
        _mudanca(inovacao, conta, EM_TESTE, VALIDADA, _utc(2026, 10, 1, 12, 5))
    with django_assert_num_queries(CONSULTAS_DO_DETALHE):
        resposta = logado.get(f"/inovacoes/{inovacao.pk}/")
    assert len(_linha_do_tempo(resposta.content.decode())) == quantidade + 1


def test_reaproveitamentos_e_historico_fecham_a_pagina_antes_do_link_de_volta(
    logado, criar_inovacao
):
    """RCON-31 e a ordem de leitura do detalhe: aside, reaproveitamentos, historico, Voltar."""
    tela = exibido(_pagina(logado, criar_inovacao()), rigoroso=True)
    aside = tela.index("<aside")
    reaproveitamentos = tela.index('<section aria-labelledby="reaproveitamentos-titulo">')
    historico = tela.index('<section aria-labelledby="historico-titulo">')
    voltar = tela.index('<a href="/inovacoes/">Voltar para a lista de inovações</a>')
    assert aside < reaproveitamentos < historico < voltar


# --- RCON-35, RCON-36: reaproveitamentos em tabela ---


def _reaproveitar(inovacao, nome, por, data):
    """Registra pelo metodo do modelo (AD-012) e fixa a data."""
    registro = inovacao.registrar_reaproveitamento(unidade=Unidade.objects.get(nome=nome), por=por)
    Reaproveitamento.objects.filter(pk=registro.pk).update(data=data)


def _secao_reaproveitamentos(tela):
    inicio = tela.index('<section aria-labelledby="reaproveitamentos-titulo">')
    return tela[inicio : tela.index("</section>", inicio)]


def test_tabela_de_reaproveitamentos_tem_titulo_colunas_e_linhas_em_ordem(
    logado, autor, administrador, terceiro, criar_inovacao
):
    """RCON-35, REAP-18: titulo com 3; colunas Unidade, Registrado por, Data; mais antigo antes."""
    inovacao = criar_inovacao(status=DISPONIVEL)
    _reaproveitar(inovacao, "Sede", autor, _utc(2026, 10, 5, 15, 0))
    _reaproveitar(inovacao, "Filial Norte", terceiro, _utc(2026, 10, 2, 15, 0))
    _reaproveitar(inovacao, "Filial Sul", administrador, _utc(2026, 10, 3, 15, 0))
    secao = _secao_reaproveitamentos(exibido(_pagina(logado, inovacao), rigoroso=True))
    assert re.findall(r"<h2[^>]*>(.*?)</h2>", secao) == ["Reaproveitamentos (3)"]
    assert re.findall(r"<th\b[^>]*>(.*?)</th>", secao) == ["Unidade", "Registrado por", "Data"]
    linhas = [
        [re.sub(r"<[^>]+>", "", celula) for celula in re.findall(r"<td>(.*?)</td>", linha)]
        for linha in re.findall(r"<tr>(.*?)</tr>", secao.split("<tbody>")[1], re.S)
    ]
    assert linhas == [
        ["Filial Norte", "bruno", "02/10/2026"],
        ["Filial Sul", "carla", "03/10/2026"],
        ["Sede", "Ana Souza", "05/10/2026"],
    ]
    assert "Nenhum reaproveitamento registrado." not in secao


def test_sem_reaproveitamento_le_a_frase_e_nao_tem_tabela(logado, criar_inovacao):
    """RCON-35: n = 0 le "Nenhum reaproveitamento registrado." e nao renderiza tabela."""
    secao = _secao_reaproveitamentos(
        exibido(_pagina(logado, criar_inovacao(status=DISPONIVEL)), rigoroso=True)
    )
    assert re.findall(r"<h2[^>]*>(.*?)</h2>", secao) == ["Reaproveitamentos (0)"]
    assert '<p class="vazio">Nenhum reaproveitamento registrado.</p>' in secao
    assert "<table" not in secao


def test_legenda_da_tabela_fica_so_para_o_leitor_de_tela(logado, autor, criar_inovacao):
    """RCON-35: o caption existe para o leitor de tela e sai so da tela (clip + 1px)."""
    inovacao = criar_inovacao(status=DISPONIVEL)
    _reaproveitar(inovacao, "Sede", autor, _utc(2026, 10, 5, 15, 0))
    secao = _secao_reaproveitamentos(exibido(_pagina(logado, inovacao), rigoroso=True))
    assert re.search(
        r'<table>\s*<caption class="visualmente-oculto">'
        r"Unidades que reaproveitaram a inovação</caption>",
        secao,
    )
    corpo = _corpos(".visualmente-oculto")
    assert re.search(r"position\s*:\s*absolute", corpo)
    assert re.search(r"(?<![\w-])width\s*:\s*1px", corpo)
    assert re.search(r"(?<![\w-])height\s*:\s*1px", corpo)
    assert re.search(r"overflow\s*:\s*hidden", corpo)
    assert re.search(r"clip\s*:\s*rect\(0 0 0 0\)", corpo)
    # So da tela: nada que tire do leitor de tela.
    assert not re.search(r"display\s*:\s*none|visibility\s*:\s*hidden", corpo)
    assert "visualmente-oculto" not in CLASSES_OCULTAS


@pytest.mark.parametrize("quantidade", [0, 3])
def test_tabela_mantem_as_consultas_do_detalhe(
    logado, autor, administrador, terceiro, criar_inovacao, django_assert_num_queries, quantidade
):
    """RCON-36: CONSULTAS_DO_DETALHE = 8 com 0 e 3 reaproveitamentos de quem registrou diferente."""
    inovacao = criar_inovacao(status=DISPONIVEL)
    contas = [autor, administrador, terceiro]
    for nome, conta in list(zip(["Sede", "Filial Norte", "Filial Sul"], contas))[:quantidade]:
        _reaproveitar(inovacao, nome, conta, _utc(2026, 10, 5, 15, 0))
    with django_assert_num_queries(CONSULTAS_DO_DETALHE):
        resposta = logado.get(f"/inovacoes/{inovacao.pk}/")
    secao = _secao_reaproveitamentos(resposta.content.decode())
    assert re.findall(r"<h2[^>]*>(.*?)</h2>", secao) == [f"Reaproveitamentos ({quantidade})"]
    assert len(re.findall(r"<tr>\s*<td>", secao)) == quantidade


def test_regras_da_lista_antiga_de_reaproveitamentos_sairam_da_folha():
    """RCON-35: o `ol.reaproveitamentos` deu lugar a tabela; a regra antiga nao tem mais uso."""
    assert ".reaproveitamentos" not in _sem_comentarios(CSS)
