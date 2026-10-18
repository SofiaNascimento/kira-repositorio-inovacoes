"""Testes do sistema de design: template base e folha central (DS-02 a DS-11).

Fonte: docs/design-spec.md §2 a §8 e .specs/features/sistema-de-design/spec.md.
"""

import re
from html.parser import HTMLParser
from pathlib import Path

import pytest
from django.conf import settings
from django.contrib.messages import constants
from django.contrib.messages.storage.base import Message
from django.template.loader import render_to_string

CSS = (Path(settings.BASE_DIR) / "templates" / "kira.css").read_text()
FOCAVEIS = {"a", "button", "input", "select", "textarea"}


class Elementos(HTMLParser):
    """Elementos de abertura em ordem, com o texto que vem logo dentro de cada um."""

    def __init__(self):
        super().__init__()
        self.lista = []  # [tag, atributos, texto]

    def handle_starttag(self, tag, attrs):
        self.lista.append([tag, dict(attrs), ""])

    def handle_data(self, data):
        if self.lista:
            self.lista[-1][2] += data


def _elementos(html):
    parser = Elementos()
    parser.feed(html)
    return parser.lista


def _focavel(tag, atributos):
    if tag == "a":
        return "href" in atributos
    return tag in FOCAVEIS and atributos.get("type") != "hidden"


def _regra(seletor):
    """Corpo da primeira regra cujo seletor e exatamente `seletor`."""
    achado = re.search(rf"(?:^|[\s}}]){re.escape(seletor)}\s*\{{([^}}]*)\}}", CSS)
    assert achado, f"falta a regra {seletor}"
    return achado.group(1)


def _corpos(seletor):
    """Corpos de todas as regras cuja lista de seletores contem `seletor`."""
    corpos = []
    sem_comentarios = re.sub(r"/\*.*?\*/", "", CSS, flags=re.S)
    for seletores, corpo in re.findall(r"([^{}]+)\{([^}]*)\}", sem_comentarios):
        if seletor in [s.strip() for s in seletores.split(",")]:
            corpos.append(corpo)
    return " ".join(corpos)


def _token(nome):
    return re.search(rf"--{nome}:\s*([^;]+);", _regra(":root")).group(1).strip()


@pytest.fixture
def paginas(client, autor, terceiro, criar_inovacao):
    """HTML de cada tela que estende o base: anonimo, autenticado, erro e 500."""
    inovacao = criar_inovacao()
    html = {"login": client.get("/entrar/").content.decode()}
    client.force_login(autor)
    for nome, url in {
        "lista": "/inovacoes/",
        "nova": "/inovacoes/nova/",
        "detalhe": f"/inovacoes/{inovacao.pk}/",
        "editar": f"/inovacoes/{inovacao.pk}/editar/",
        "excluir": f"/inovacoes/{inovacao.pk}/excluir/",
        "nao_encontrada": "/inovacoes/999999/",
    }.items():
        html[nome] = client.get(url).content.decode()
    client.force_login(terceiro)
    html["acesso_negado"] = client.get(f"/inovacoes/{inovacao.pk}/editar/").content.decode()
    # AUTH-26: o server_error renderiza o 500.html sem contexto.
    html["erro_500"] = render_to_string("500.html")
    return html


# --- DS-02: uma folha central, embutida pelo base ------------------------------


def test_toda_pagina_tem_um_unico_style_com_a_folha_central(paginas):
    """DS-02."""
    for nome, html in paginas.items():
        estilos = re.findall(r"<style>(.*?)</style>", html, re.S)
        assert len(estilos) == 1, nome
        assert estilos[0].strip() == CSS.strip(), nome


@pytest.mark.unit
def test_folha_central_nao_repete_atributos_do_html():
    """DS-02, AD-010: o CSS embutido nao pode casar com buscas de atributo no HTML."""
    assert '="' not in CSS
    assert "<" not in CSS


def _nomes_de_usuario_dos_testes():
    """Usernames que os testes criam; um teste pode procurar qualquer um no HTML."""
    pastas = [Path(settings.BASE_DIR) / app / "tests" for app in ("contas", "inovacoes")]
    nomes = set()
    for arquivo in (a for pasta in pastas for a in pasta.glob("*.py")):
        for nome in re.findall(r'username=f?"([^"{]+)', arquivo.read_text()):
            nomes.add(nome.lower())
    return nomes


@pytest.mark.unit
def test_folha_central_nao_contem_nome_de_usuario_dos_testes():
    """DS-02, AD-010: o CSS embutido nao satisfaz um `"ana" in html` (AUTH-01) por acaso."""
    nomes = _nomes_de_usuario_dos_testes()
    assert "ana" in nomes
    assert [nome for nome in sorted(nomes) if nome in CSS.lower()] == []


# --- DS-03: link de pular -------------------------------------------------------


def test_primeiro_focavel_e_o_link_de_pular_para_o_main(paginas):
    """DS-03, WCAG 2.4.1."""
    for nome, html in paginas.items():
        elementos = _elementos(html)
        tag, atributos, texto = next(e for e in elementos if _focavel(e[0], e[1]))
        assert (tag, atributos.get("href"), texto.strip()) == (
            "a",
            "#conteudo",
            "Ir para o conteúdo principal",
        ), nome
        mains = [a for t, a, _ in elementos if t == "main"]
        assert len(mains) == 1, nome
        assert mains[0].get("id") == "conteudo", nome


# --- DS-04: marcos e marca ------------------------------------------------------


def test_toda_pagina_tem_header_com_a_marca_main_e_footer(paginas):
    """DS-04."""
    for nome, html in paginas.items():
        cabecalho = html[html.index("<header>") : html.index("</header>")]
        marca = re.search(r'<a class="marca" href="([^"]*)">(.*?)</a>', cabecalho, re.S)
        assert marca, nome
        assert marca.group(1) == "/", nome
        assert re.search(r">\s*KIRA\s*<", marca.group(2)), nome
        rodape = re.search(r"<footer>(.*?)</footer>", html, re.S)
        assert rodape, nome
        assert "KIRA · Repositório de Inovações" in rodape.group(1), nome


# --- DS-05: menu do usuario ------------------------------------------------------


@pytest.mark.parametrize("pagina", ["/inovacoes/", "/inovacoes/nova/"])
def test_cabecalho_autenticado_mostra_usuario_e_sair_depois_da_navegacao(client, autor, pagina):
    """DS-05."""
    client.force_login(autor)
    html = client.get(pagina).content.decode()
    cabecalho = html[html.index("<header>") : html.index("</header>")]
    fim_da_nav = cabecalho.index("</nav>")
    usuario = re.search(r"<span>\s*ana\s*</span>", cabecalho)
    sair = re.search(r"<button[^>]*>\s*Sair\s*</button>", cabecalho)
    assert usuario
    assert sair
    assert fim_da_nav < usuario.start() < sair.start()


@pytest.mark.django_db
def test_cabecalho_anonimo_nao_mostra_o_menu_do_usuario(client):
    """DS-05, edge case: sem sessao, sem menu do usuario."""
    html = client.get("/entrar/").content.decode()
    cabecalho = html[html.index("<header>") : html.index("</header>")]
    assert 'class="usuario"' not in cabecalho
    assert "Sair" not in cabecalho


# --- DS-06: tokens --------------------------------------------------------------

TOKENS_DA_SPEC = {
    "brand-navy": "#1E3A6E",
    "brand-blue": "#2E5EAA",
    "brand-blue-light": "#6AA0E0",
    "brand-gradient": "linear-gradient(90deg, #1E3A6E 0%, #6AA0E0 100%)",
    "text": "#1A2332",
    "text-muted": "#566072",
    "border": "#D4DEEC",
    "bg": "#F0F5FC",
    "surface": "#FFFFFF",
    "success": "#1E7D46",
    "warning": "#8A5A00",
    "error": "#B3261E",
    "info": "#2E5EAA",
    "font-sans": '"Inter", "Segoe UI", system-ui, -apple-system, Arial, sans-serif',
    "fs-xs": "0.75rem",
    "fs-sm": "0.875rem",
    "fs-base": "1rem",
    "fs-lg": "1.25rem",
    "fs-xl": "1.5rem",
    "fs-2xl": "2rem",
    "lh-body": "1.5",
}


@pytest.mark.unit
@pytest.mark.parametrize("nome", TOKENS_DA_SPEC)
def test_root_declara_o_token_da_spec_com_o_valor_exato(nome):
    """DS-06: §2 e §3."""
    assert _token(nome) == TOKENS_DA_SPEC[nome]


# --- DS-07: foco ----------------------------------------------------------------


@pytest.mark.unit
def test_foco_visivel_e_um_anel_de_2px_na_cor_de_acao():
    """DS-07: §6, anel de 2px; contraste do anel conferido no DS-08."""
    regra = _regra(":focus-visible")
    assert re.search(r"outline\s*:\s*2px\s+solid\s+var\(--brand-blue\)", regra)
    # Nenhuma regra apaga ou afina o anel, nem pelas propriedades longas.
    for propriedade, valor in re.findall(r"(outline(?:-[a-z]+)?)\s*:\s*([^;}]+)", CSS):
        valor = valor.strip().lower()
        assert not re.search(r"\bnone\b|\bhidden\b|\btransparent\b", valor), (propriedade, valor)
        assert not re.fullmatch(r"0(\.0+)?[a-z%]*", valor.split()[0]), (propriedade, valor)
        if propriedade in ("outline", "outline-width"):
            for numero in re.findall(r"(\d*\.?\d+)px", valor):
                assert float(numero) >= 2, (propriedade, valor)


# --- DS-08: contraste -----------------------------------------------------------


def _luminancia(hexa):
    canais = [int(hexa.lstrip("#")[i : i + 2], 16) / 255 for i in (0, 2, 4)]
    r, g, b = (c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in canais)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contraste(a, b):
    claro, escuro = sorted((_luminancia(a), _luminancia(b)), reverse=True)
    return (claro + 0.05) / (escuro + 0.05)


# Pares texto/fundo que os componentes usam (WCAG 1.4.3: 4.5:1).
PARES_DE_TEXTO = [
    ("text", "surface"),
    ("text", "bg"),
    ("text-muted", "surface"),
    ("text-muted", "bg"),
    ("brand-navy", "surface"),
    ("brand-navy", "bg"),
    ("brand-blue", "surface"),
    ("brand-blue", "bg"),
    ("brand-blue", "info-tint"),
    ("surface", "brand-blue"),
    ("surface", "error"),
    ("error", "surface"),
    ("text", "success-tint"),
    ("text", "warning-tint"),
    ("text", "error-tint"),
    ("text", "info-tint"),
    ("warning", "warning-tint"),
    ("info", "info-tint"),
    ("success", "success-tint"),
]


@pytest.mark.unit
@pytest.mark.parametrize(("texto", "fundo"), PARES_DE_TEXTO)
def test_pares_de_texto_dos_componentes_tem_contraste_aa(texto, fundo):
    """DS-08."""
    assert _contraste(_token(texto), _token(fundo)) >= 4.5


@pytest.mark.unit
@pytest.mark.parametrize(("borda", "fundo"), [("brand-blue", "surface"), ("text-muted", "surface")])
def test_anel_de_foco_e_borda_de_campo_tem_contraste_de_componente(borda, fundo):
    """DS-08 e DS-07: WCAG 1.4.11, 3:1 para foco e limite de campo."""
    assert _contraste(_token(borda), _token(fundo)) >= 3


@pytest.mark.unit
def test_azul_claro_nunca_e_cor_de_texto_nem_fundo_de_componente():
    """DS-08: §2, --brand-blue-light so no gradiente da marca."""
    usos = re.findall(r"([\w-]+)\s*:[^;]*var\(--brand-blue-light\)", CSS)
    assert usos == []


# --- DS-09: movimento -----------------------------------------------------------


@pytest.mark.unit
def test_reduzir_movimento_desliga_transicoes_e_animacoes():
    """DS-09."""
    bloco = re.search(r"@media \(prefers-reduced-motion: reduce\)\s*\{(.*?)\n\}", CSS, re.S)
    assert bloco
    assert re.search(r"transition\s*:\s*none", bloco.group(1))
    assert re.search(r"animation\s*:\s*none", bloco.group(1))


# --- DS-10 e DS-11: mensagens de feedback ----------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize(
    ("nivel", "tag"),
    [
        (constants.SUCCESS, "success"),
        (constants.INFO, "info"),
        (constants.WARNING, "warning"),
        (constants.ERROR, "error"),
    ],
)
def test_mensagem_ganha_a_variante_do_seu_nivel_dentro_do_status(nivel, tag):
    """DS-10."""
    html = render_to_string("base.html", {"messages": [Message(nivel, "Texto do aviso.")]})
    status = html[html.index('role="status"') : html.index("</div>", html.index('role="status"'))]
    assert re.search(rf'<li class="alerta alerta--{tag}">\s*Texto do aviso\.\s*</li>', status)


def test_mensagem_de_sucesso_real_chega_com_a_variante_de_sucesso(client, autor):
    """DS-10, na tela: o "Sessão encerrada." do logout (AUTH) vira alerta de sucesso."""
    client.force_login(autor)
    html = client.post("/sair/", follow=True).content.decode()
    status = html[html.index('role="status"') : html.index("</div>", html.index('role="status"'))]
    assert re.search(r'<li class="alerta alerta--success">\s*Sessão encerrada\.\s*</li>', status)


@pytest.mark.unit
@pytest.mark.parametrize(
    "seletor",
    [
        ".alerta--info::before",
        ".alerta--success::before",
        ".alerta--warning::before",
        ".alerta--error::before",
        "[role=alert]::before",
    ],
)
def test_cada_alerta_tem_icone_alem_da_cor(seletor):
    """DS-11: WCAG 1.4.1, a cor e reforco, nao a unica pista."""
    glifos = re.findall(r'content:\s*"([^"]+)"', _corpos(seletor))
    assert glifos and all(g.strip() for g in glifos)


@pytest.mark.unit
def test_alertas_tem_borda_esquerda_colorida():
    """DS-11: borda colorida a esquerda em toda variante."""
    for seletor in [".alerta", "[role=alert]"]:
        assert re.search(r"border-left\s*:\s*4px solid var\(--info\)", _corpos(seletor))
    for seletor, cor in [
        (".alerta--success", "success"),
        (".alerta--warning", "warning"),
        (".alerta--error", "error"),
        ("[role=alert]", "error"),
    ]:
        assert re.search(rf"border-left-color\s*:\s*var\(--{cor}\)", _corpos(seletor)), seletor


# --- DS-01: as telas so estendem o base -----------------------------------------

RAIZES = [
    Path(settings.BASE_DIR) / "templates",
    Path(settings.BASE_DIR) / "contas" / "templates",
    Path(settings.BASE_DIR) / "inovacoes" / "templates",
]
# Pecas incluidas, nao telas: o proprio base, a marca e o grupo de campo.
PECAS = {"base.html", "marca.html", "inovacoes/campo.html"}


def _telas():
    for raiz in RAIZES:
        for arquivo in sorted(raiz.rglob("*.html")):
            nome = arquivo.relative_to(raiz).as_posix()
            if nome not in PECAS:
                yield nome, arquivo.read_text()


@pytest.mark.unit
def test_toda_tela_estende_o_base_sem_estilo_proprio():
    """DS-01."""
    telas = dict(_telas())
    # STAT-06, STAT-34: a F5 acrescenta a tela "Avançar status".
    assert len(telas) == 9
    for nome, fonte in telas.items():
        assert fonte.lstrip().startswith('{% extends "base.html" %}'), nome
        assert "<style" not in fonte, nome
        assert "style=" not in fonte, nome


@pytest.mark.unit
def test_pecas_e_base_nao_tem_estilo_inline_alem_da_folha_central():
    """DS-01: o unico style do projeto e o do base, que embute kira.css."""
    for raiz in RAIZES:
        for arquivo in raiz.rglob("*.html"):
            fonte = arquivo.read_text()
            assert "style=" not in fonte, arquivo
            estilos = re.findall(r"<style>(.*?)</style>", fonte, re.S)
            if arquivo.name == "base.html":
                assert estilos == ['{% include "kira.css" %}']
            else:
                assert estilos == [], arquivo


# --- DS-12 e DS-13: selo de status ----------------------------------------------

STATUS = [
    ("EM_TESTE", "em_teste", "Em teste"),
    ("VALIDADA", "validada", "Validada"),
    ("DISPONIVEL_PARA_REPLICACAO", "disponivel_para_replicacao", "Disponível para replicação"),
]


@pytest.mark.parametrize(("status", "classe", "rotulo"), STATUS)
def test_lista_mostra_o_status_num_selo_com_o_rotulo(
    client, autor, criar_inovacao, status, classe, rotulo
):
    """DS-12, na listagem."""
    criar_inovacao(status=status)
    client.force_login(autor)
    html = client.get("/inovacoes/").content.decode()
    corpo = re.search(r"<tbody>(.*?)</tbody>", html, re.S).group(1)
    assert re.search(
        rf'<td>\s*<span class="selo selo--{classe}">\s*{re.escape(rotulo)}\s*</span>\s*</td>', corpo
    )


@pytest.mark.parametrize(("status", "classe", "rotulo"), STATUS)
def test_detalhe_mostra_o_status_num_selo_com_o_rotulo(
    client, autor, criar_inovacao, status, classe, rotulo
):
    """DS-12, no detalhe: o selo vai no proprio dd, com o texto puro (CONS-12)."""
    inovacao = criar_inovacao(status=status)
    client.force_login(autor)
    html = client.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert re.search(
        rf"<dt>\s*Status\s*</dt>\s*"
        rf'<dd class="selo selo--{classe}">\s*{re.escape(rotulo)}\s*</dd>',
        html,
    )


@pytest.mark.unit
def test_cada_status_tem_uma_forma_propria_alem_da_cor():
    """DS-13: a forma distingue o status sem depender da cor (WCAG 1.4.1)."""
    formas = []
    for _, classe, _ in STATUS:
        regra = _corpos(f".selo--{classe}::before")
        forma = re.search(r"(border-radius|transform)\s*:\s*([^;]+);", regra)
        assert forma, classe
        formas.append(forma.groups())
    assert len(set(formas)) == len(STATUS)
    assert re.search(r'content:\s*""', _corpos(".selo::before"))


# --- DS-14: botoes --------------------------------------------------------------


def _botoes_de_envio(html):
    conteudo = html[html.index("<main") :]
    return re.findall(r'<button type="submit"(?: class="([^"]*)")?>\s*(.*?)\s*</button>', conteudo)


def test_excluir_definitivamente_usa_o_botao_de_perigo(client, autor, criar_inovacao):
    """DS-14."""
    inovacao = criar_inovacao()
    client.force_login(autor)
    html = client.get(f"/inovacoes/{inovacao.pk}/excluir/").content.decode()
    assert _botoes_de_envio(html) == [("botao--perigo", "Excluir definitivamente")]
    assert re.search(r"background\s*:\s*var\(--error\)", _corpos(".botao--perigo"))


def test_demais_envios_das_telas_tem_o_estilo_primario(client, autor, criar_inovacao):
    """DS-14: os outros submits nao trocam o estilo primario do elemento button."""
    inovacao = criar_inovacao()
    envios = {"/entrar/": "Entrar"}
    html = {"/entrar/": client.get("/entrar/").content.decode()}
    client.force_login(autor)
    envios |= {
        "/inovacoes/": "Buscar",
        "/inovacoes/nova/": "Salvar",
        f"/inovacoes/{inovacao.pk}/editar/": "Salvar alterações",
    }
    for url in list(envios)[1:]:
        html[url] = client.get(url).content.decode()
    for url, rotulo in envios.items():
        assert _botoes_de_envio(html[url]) == [("", rotulo)], url
    assert re.search(r"background\s*:\s*var\(--brand-blue\)", _corpos("button"))


# --- DS-15: login ---------------------------------------------------------------


@pytest.mark.django_db
def test_login_fica_num_card_com_a_marca_no_topo(client):
    """DS-15."""
    html = client.get("/entrar/").content.decode()
    conteudo = html[html.index("<main") :]
    card = re.search(r'<div class="cartao cartao--estreito">(.*)</form>', conteudo, re.S)
    assert card
    dentro = card.group(1)
    assert dentro.index('<div class="marca">') < dentro.index("<h1>") < dentro.index("<form")
    assert re.search(r">\s*KIRA\s*<", dentro)


# --- DS-16: tabela responsiva ---------------------------------------------------


def test_tabela_fica_num_quadro_que_rola_na_horizontal(client, autor, criar_inovacao):
    """DS-16."""
    criar_inovacao()
    client.force_login(autor)
    html = client.get("/inovacoes/").content.decode()
    assert re.search(r'<div class="tabela">\s*<table>', html)
    assert re.search(r"</table>\s*</div>", html)
    assert re.search(r"overflow-x\s*:\s*auto", _corpos(".tabela"))
