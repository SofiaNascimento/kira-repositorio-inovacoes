"""Folha central v2 (fundacao-do-redesign, RED-01 a RED-12).

Fonte: docs/design-spec.md v2 §2 a §6 e .specs/features/fundacao-do-redesign/spec.md.
Os helpers da folha sao os do sistema de design (DS-06 a DS-09), importados sem mudanca.
"""

import re
from html.parser import HTMLParser

import pytest

# `paginas` e a fixture do DS-02 a DS-05, reusada sem mudanca.
from inovacoes.tests.test_views_sistema_design import (
    CSS,
    _contraste,
    _corpos,
    _token,
    paginas,  # noqa: F401
)

URL_DA_FONTE = "/static/fontes/inter-latin-wght-normal.woff2"


def _sem_comentarios(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def _seletores(lista):
    """Separa uma lista de seletores pelas virgulas de fora dos parenteses."""
    partes, nivel, atual = [], 0, ""
    for caractere in lista:
        nivel += {"(": 1, ")": -1}.get(caractere, 0)
        if caractere == "," and nivel == 0:
            partes.append(atual.strip())
            atual = ""
        else:
            atual += caractere
    return [*partes, atual.strip()]


def _corpos_com_parenteses(seletor):
    """Como `_corpos`, mas aceita seletor com virgula dentro de :not(...) ou :is(...)."""
    regras = re.findall(r"([^{}]+)\{([^}]*)\}", _sem_comentarios(CSS))
    return " ".join(corpo for lista, corpo in regras if seletor in _seletores(lista))


# --- RED-05: @font-face da Inter ------------------------------------------------


def _font_face():
    blocos = re.findall(r"@font-face\s*\{([^}]*)\}", _sem_comentarios(CSS))
    assert len(blocos) == 1
    return dict(
        (nome.strip(), valor.strip())
        for nome, valor in re.findall(r"([\w-]+)\s*:\s*([^;]+);", blocos[0])
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    ("propriedade", "valor"),
    [
        ("font-family", "Inter"),
        ("font-display", "swap"),
        ("font-weight", "400 800"),
        ("src", f"url({URL_DA_FONTE}) format(woff2)"),
    ],
)
def test_font_face_declara_a_inter_servida_pelo_projeto(propriedade, valor):
    """RED-05."""
    assert _font_face()[propriedade] == valor


# --- RED-08: nenhum recurso de outra origem --------------------------------------


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lista = []

    def handle_starttag(self, tag, attrs):
        self.lista.append((tag, dict(attrs), self.get_starttag_text()))


def _tags(html):
    parser = Tags()
    parser.feed(html)
    return parser.lista


EXTERNO = re.compile(r"https?://", re.I)


@pytest.mark.unit
def test_folha_nao_importa_nem_aponta_para_outra_origem():
    """RED-08: nenhum @import nem url( com http:// ou https:// na folha."""
    css = _sem_comentarios(CSS)
    for chamada in re.findall(r"@import[^;]*;|url\([^)]*\)", css, re.I):
        assert not EXTERNO.search(chamada), chamada


def test_nenhuma_pagina_carrega_recurso_de_outra_origem(paginas):  # noqa: F811
    """RED-08: link, script e img sem http(s)://; o unico style e a folha (DS-02)."""
    for nome, html in paginas.items():
        for tag, _, texto in _tags(html):
            if tag in ("link", "script", "img"):
                assert not EXTERNO.search(texto), (nome, texto)
        for estilo in re.findall(r"<style>(.*?)</style>", html, re.S):
            for chamada in re.findall(r"@import[^;]*;|url\([^)]*\)", estilo, re.I):
                assert not EXTERNO.search(chamada), (nome, chamada)


def test_toda_pagina_faz_preload_da_fonte_na_mesma_url(paginas):  # noqa: F811
    """RED-05, RED-06: o preload aponta para a URL do @font-face, com crossorigin."""
    for nome, html in paginas.items():
        preloads = [a for t, a, _ in _tags(html) if t == "link" and a.get("rel") == "preload"]
        assert len(preloads) == 1, nome
        assert preloads[0] == {
            "rel": "preload",
            "href": URL_DA_FONTE,
            "as": "font",
            "type": "font/woff2",
            "crossorigin": None,
        }, nome


# --- RED-01: tokens v2 ----------------------------------------------------------

TOKENS_V2 = {
    "brand-blue-hover": "#28529A",
    "borda-campo": "#7A879B",
    "on-brand": "#FFFFFF",
    "info-tint": "#E8EFFA",
    "success-tint": "#EDF7F1",
    "warning-tint": "#FBF3E0",
    "error-tint": "#FBEAE9",
    "trilho": "#EEF2F8",
    "raio-cartao": "16px",
    "raio-pilula": "999px",
    "numeros": "tabular-nums",
}


@pytest.mark.unit
@pytest.mark.parametrize("nome", TOKENS_V2)
def test_root_declara_o_token_v2_com_o_valor_exato(nome):
    """RED-01: §2 e §4 v2. Os tokens da v1 seguem vigiados pelo DS-06."""
    assert _token(nome) == TOKENS_V2[nome]


# --- RED-02: cartao -------------------------------------------------------------


def _alfas(valor):
    """Alfa de cada cor de um valor de CSS; cor sem alfa conta como 1."""
    alfas = []
    for cor in re.findall(r"rgba?\([^)]*\)|hsla?\([^)]*\)|#[0-9a-fA-F]{3,8}\b", valor):
        if cor.startswith("#"):
            digitos = cor[1:]
            alfa = {4: digitos[3] * 2, 8: digitos[6:]}.get(len(digitos))
            alfas.append(int(alfa, 16) / 255 if alfa else 1.0)
            continue
        partes = re.split(r"\s*/\s*|\s*,\s*", cor[cor.index("(") + 1 : -1].strip())
        separado = "/" in cor or len(partes) == 4
        if not separado:
            alfas.append(1.0)
            continue
        alfa = partes[-1]
        alfas.append(float(alfa[:-1]) / 100 if alfa.endswith("%") else float(alfa))
    return alfas


@pytest.mark.unit
def test_cartao_tem_o_raio_de_cartao():
    """RED-02."""
    assert re.search(r"border-radius\s*:\s*var\(--raio-cartao\)", _corpos(".cartao"))


@pytest.mark.unit
def test_sombra_do_cartao_e_discreta():
    """RED-02: toda cor do box-shadow (resolvido pelo token) tem alfa <= 0.12."""
    sombra = re.findall(r"box-shadow\s*:\s*([^;]+);", _corpos(".cartao"))[-1].strip()
    token = re.fullmatch(r"var\(--([\w-]+)\)", sombra)
    if token:
        sombra = _token(token.group(1))
    alfas = _alfas(sombra)
    assert alfas
    assert all(alfa <= 0.12 for alfa in alfas), sombra


# --- RED-03: campos -------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize(
    "seletor", ["input:not([type=hidden], [type=checkbox], [type=radio])", "select", "textarea"]
)
def test_campo_tem_borda_de_1_5px_na_cor_de_campo(seletor):
    """RED-03."""
    bordas = re.findall(r"border\s*:\s*([^;]+);", _corpos_com_parenteses(seletor))
    assert bordas
    assert re.fullmatch(r"1\.5px\s+solid\s+var\(--borda-campo\)", bordas[-1].strip())


@pytest.mark.unit
@pytest.mark.parametrize("fundo", ["surface", "bg"])
def test_borda_de_campo_tem_contraste_de_componente(fundo):
    """RED-03: WCAG 1.4.11, 3:1."""
    assert _contraste(_token("borda-campo"), _token(fundo)) >= 3


# --- RED-04: numeros tabulares --------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize(
    "seletor",
    [
        "time",
        ".total",
        ".numero",
        "nav[aria-label=Paginação]",
        ".cartao-indicador__numero",
        ".variacao",
        ".linha-do-tempo time",
    ],
)
def test_numeros_que_se_comparam_usam_algarismos_tabulares(seletor):
    """RED-04."""
    assert re.search(r"font-variant-numeric\s*:\s*var\(--numeros\)", _corpos(seletor))


# --- RED-09 e RED-10: botao, campo e selo ---------------------------------------

# AD-010: `"aria-invalid" not in html` (CONS-30) le a pagina inteira, com a folha
# embutida; por isso a folha escreve o nome do atributo com o "i" escapado (\69).
INVALIDO = r"[aria-\69 nvalid=true]"


def _tem(corpo, propriedade, valor):
    return re.search(
        rf"(?:^|;|\s){propriedade}\s*:\s*{re.escape(valor)}\s*(?:!important\s*)?;", corpo
    )


@pytest.mark.unit
@pytest.mark.parametrize("seletor", ["button:hover", ".botao:hover"])
def test_hover_do_botao_primario_usa_o_azul_de_hover(seletor):
    """RED-09: §6, primario em hover com --brand-blue-hover."""
    assert _tem(_corpos(seletor), "background", "var(--brand-blue-hover)")


@pytest.mark.unit
def test_texto_do_botao_primario_e_a_cor_sobre_a_marca():
    """RED-10: o par do hover (on-brand sobre brand-blue-hover) e o que a folha pinta."""
    assert _tem(_corpos("button"), "color", "var(--on-brand)")


@pytest.mark.unit
@pytest.mark.parametrize("seletor", ["button:active", ".botao:active"])
def test_botao_tem_estado_ativo(seletor):
    """RED-09: §6, estado ativo."""
    assert re.search(r"[\w-]+\s*:\s*[^;]+;", _corpos(seletor))


@pytest.mark.unit
@pytest.mark.parametrize(
    "seletor", ["button:disabled", "button[aria-disabled=true]", ".botao[aria-disabled=true]"]
)
def test_botao_desabilitado_usa_fundo_da_pagina_texto_secundario_e_cursor_bloqueado(seletor):
    """RED-09: §6, desabilitado; RED-10: sem opacidade, o par text-muted/bg vale como e."""
    corpo = _corpos(seletor)
    assert _tem(corpo, "background", "var(--bg)")
    assert _tem(corpo, "color", "var(--text-muted)")
    assert _tem(corpo, "cursor", "not-allowed")
    assert "opacity" not in corpo


@pytest.mark.unit
def test_hover_do_botao_secundario_usa_o_fundo_suave_de_informacao():
    """RED-09: §6."""
    assert _tem(_corpos(".botao--secundario:hover"), "background", "var(--info-tint)")


@pytest.mark.unit
def test_hover_do_botao_de_perigo_usa_o_fundo_suave_de_erro_com_texto_de_erro():
    """RED-09: §6; RED-10: o texto sobre --error-tint e --error (par da §2)."""
    corpo = _corpos(".botao--perigo:hover")
    assert _tem(corpo, "background", "var(--error-tint)")
    assert _tem(corpo, "color", "var(--error)")


@pytest.mark.unit
@pytest.mark.parametrize("controle", ["input", "select", "textarea"])
def test_campo_invalido_tem_borda_de_2px_de_erro(controle):
    """RED-09: §6, campo com erro."""
    assert "aria-invalid" not in CSS
    assert _tem(_corpos(controle + INVALIDO), "border", "2px solid var(--error)")


@pytest.mark.unit
def test_selo_e_uma_pilula():
    """RED-09: §6, selo em pilula."""
    assert _tem(_corpos(".selo"), "border-radius", "var(--raio-pilula)")


@pytest.mark.unit
@pytest.mark.parametrize(
    ("texto", "fundo"),
    [
        ("on-brand", "brand-blue-hover"),
        ("text-muted", "bg"),
        ("brand-navy", "info-tint"),
        ("error", "error-tint"),
    ],
)
def test_pares_de_texto_dos_estados_tem_contraste_aa(texto, fundo):
    """RED-10: §2 v2, 4.5:1."""
    assert _contraste(_token(texto), _token(fundo)) >= 4.5
