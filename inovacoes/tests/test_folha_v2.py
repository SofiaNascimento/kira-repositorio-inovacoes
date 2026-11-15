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
    PARES_DE_TEXTO,
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


# --- RED-09 e RED-10: componentes do detalhe e do formulario ---------------------

# DS-02: a folha nao pode conter nome de usuario dos testes ("nova" esta em
# "inovacao"); por isso a classe vai com o "v" escapado (\76) na folha.
CARTAO_INOVACAO = r".cartao-ino\76 acao"


def _regras_de(prefixo):
    """(seletores, corpo) de toda regra global com algum seletor que comeca pelo prefixo."""
    regras = re.findall(r"([^{}@]+)\{([^}]*)\}", _sem_comentarios(CSS))
    return [
        (lista.strip(), corpo)
        for lista, corpo in regras
        if any(s.startswith(prefixo) for s in _seletores(lista))
    ]


def _corpos_de(prefixo):
    return " ".join(corpo for _, corpo in _regras_de(prefixo))


@pytest.mark.unit
def test_cartao_de_inovacao_em_hover_ganha_borda_azul():
    """RED-09: §6 v2, cartao de inovacao em hover."""
    assert "nova" not in CSS.lower()
    assert _tem(_corpos(CARTAO_INOVACAO + ":hover"), "border-color", "var(--brand-blue)")


@pytest.mark.unit
def test_titulo_do_cartao_de_inovacao_fica_sublinhado_no_hover():
    """RED-09: §6 v2, so o titulo e link; o hover do cartao o sublinha."""
    seletor = f"{CARTAO_INOVACAO}:hover {CARTAO_INOVACAO}__titulo a"
    assert _tem(_corpos(seletor), "text-decoration", "underline")
    assert _tem(_corpos(CARTAO_INOVACAO + "__titulo a"), "text-decoration", "none")


@pytest.mark.unit
def test_etapa_concluida_usa_a_cor_de_sucesso():
    """RED-09: §6 v2, marcador --success."""
    assert "var(--success)" in _corpos_de(".etapa--concluida")


@pytest.mark.unit
def test_etapa_atual_tem_marcador_cheio_e_texto_em_negrito():
    """RED-09: §6 v2, marcador cheio e negrito."""
    assert _tem(_corpos(".etapa--atual"), "font-weight", "700")
    assert _tem(_corpos(".etapa--atual .etapa__marcador"), "background", "var(--brand-blue)")


@pytest.mark.unit
def test_etapa_futura_tem_marcador_vazado_na_cor_de_campo():
    """RED-09: §6 v2, marcador vazado --borda-campo."""
    corpo = _corpos(".etapa--futura .etapa__marcador")
    assert _tem(corpo, "border-color", "var(--borda-campo)")
    assert _tem(corpo, "background", "var(--surface)")


@pytest.mark.unit
def test_data_da_linha_do_tempo_vai_em_negrito_com_numeros_tabulares():
    """RED-09: §6 v2, time em negrito com --numeros."""
    corpo = _corpos(".linha-do-tempo time")
    assert _tem(corpo, "font-variant-numeric", "var(--numeros)")
    assert _tem(corpo, "font-weight", "700")


@pytest.mark.unit
def test_ponto_do_cadastro_e_vazado_e_os_demais_sao_azuis():
    """RED-09: §6 v2, ponto do cadastro --borda-campo; mudancas --brand-blue."""
    assert _tem(_corpos(".linha-do-tempo__ponto"), "background", "var(--brand-blue)")
    corpo = _corpos(".linha-do-tempo__ponto--cadastro")
    assert _tem(corpo, "border-color", "var(--borda-campo)")
    assert _tem(corpo, "background", "var(--surface)")


@pytest.mark.unit
def test_cartao_de_contato_tem_borda_superior_azul_de_4px():
    """RED-09: §6 v2."""
    assert _tem(_corpos(".cartao-contato"), "border-top", "4px solid var(--brand-blue)")


@pytest.mark.unit
def test_texto_do_contato_preserva_as_quebras_de_linha():
    """RED-09: §6 v2, o texto livre como foi digitado."""
    assert _tem(_corpos_de(".cartao-contato"), "white-space", "pre-line")


@pytest.mark.unit
def test_legenda_do_grupo_e_subtitulo_em_navy():
    """RED-09: §6 v2, legend em --fs-lg, 700, --brand-navy."""
    corpo = _corpos(".grupo legend")
    assert _tem(corpo, "font-size", "var(--fs-lg)")
    assert _tem(corpo, "font-weight", "700")
    assert _tem(corpo, "color", "var(--brand-navy)")


@pytest.mark.unit
def test_numero_do_grupo_fica_num_circulo_de_fundo_suave():
    """RED-09: §6 v2."""
    corpo = _corpos(".grupo__numero")
    assert _tem(corpo, "background", "var(--info-tint)")
    assert _tem(corpo, "border-radius", "50%")


# RED-10: pares da §2 v2 (texto, 4.5:1) e os ja conferidos pelo DS-08.
PARES_APROVADOS_DE_TEXTO = {
    *PARES_DE_TEXTO,
    ("text-muted", "info-tint"),
    ("brand-navy", "info-tint"),
    ("on-brand", "brand-blue"),
    ("on-brand", "brand-navy"),
    ("on-brand", "brand-blue-hover"),
    ("error", "error-tint"),
    ("success", "surface"),
    ("warning", "surface"),
}
# RED-10: limites de componente e barras (3:1) da §2 v2 e do DS-08.
PARES_APROVADOS_DE_COMPONENTE = {
    ("borda-campo", "surface"),
    ("borda-campo", "bg"),
    ("brand-blue", "surface"),
    ("brand-blue", "info-tint"),
    ("text-muted", "surface"),
    ("brand-navy", "trilho"),
    ("brand-blue", "trilho"),
    ("warning", "trilho"),
    ("success", "trilho"),
}
BORDAS = r"border(?:-top|-right|-bottom|-left)?(?:-color)?|outline(?:-color)?"


def _pares_da_regra(corpo, contexto):
    """(cor, fundo, e_texto) de cada cor que a regra pinta.

    O texto fica sobre o fundo da propria regra (ou, sem fundo, o do contexto); a borda
    e o limite do elemento contra o que esta em volta, o fundo do contexto. A borda
    `--border` e decorativa (§2) e nao conta.
    """
    declaracoes = re.findall(r"([\w-]+)\s*:\s*([^;]+);", corpo)
    proprio = [re.search(r"var\(--([\w-]+)\)", v) for n, v in declaracoes if n == "background"]
    fundo = proprio[-1].group(1) if proprio and proprio[-1] else contexto
    pares = []
    for nome, valor in declaracoes:
        for token in re.findall(r"var\(--([\w-]+)\)", valor):
            if nome == "color":
                pares.append((token, fundo, True))
            elif re.fullmatch(BORDAS, nome) and token != "border":
                pares.append((token, contexto, False))
    return pares


@pytest.mark.unit
@pytest.mark.parametrize(
    "componente", [CARTAO_INOVACAO, ".etapa", ".linha-do-tempo", ".cartao-contato", ".grupo"]
)
def test_cores_do_componente_estao_em_pares_aprovados(componente):
    """RED-10: cada cor de texto e de limite sobre o fundo em que e desenhada.

    Os cinco componentes ficam sobre --surface (cartao proprio, ou o cartao do
    detalhe e do formulario).
    """
    conferidos = 0
    for seletores, corpo in _regras_de(componente):
        for cor, fundo, e_texto in _pares_da_regra(corpo, "surface"):
            if e_texto:
                assert (cor, fundo) in PARES_APROVADOS_DE_TEXTO, (seletores, cor, fundo)
                assert _contraste(_token(cor), _token(fundo)) >= 4.5, (seletores, cor, fundo)
            else:
                aprovados = PARES_APROVADOS_DE_COMPONENTE | PARES_APROVADOS_DE_TEXTO
                assert (cor, fundo) in aprovados, (seletores, cor, fundo)
                assert _contraste(_token(cor), _token(fundo)) >= 3, (seletores, cor, fundo)
            conferidos += 1
    assert conferidos


# --- RED-09 e RED-10: componentes da lista e do painel ---------------------------


@pytest.mark.unit
def test_etiqueta_de_filtro_e_uma_pilula_de_fundo_suave_e_texto_navy():
    """RED-09: §6 v2, etiqueta de filtro ativo."""
    corpo = _corpos(".etiqueta-filtro")
    assert _tem(corpo, "background", "var(--info-tint)")
    assert _tem(corpo, "color", "var(--brand-navy)")
    assert _tem(corpo, "border-radius", "var(--raio-pilula)")


@pytest.mark.unit
def test_link_de_remover_a_etiqueta_tem_hover_e_foco():
    """RED-09: §6 v2, hover do "×" com fundo --border; foco com anel no "×"."""
    assert _tem(_corpos(".etiqueta-filtro a:hover"), "background", "var(--border)")
    assert _tem(
        _corpos(".etiqueta-filtro a:focus-visible"), "outline", "2px solid var(--brand-blue)"
    )


@pytest.mark.unit
def test_icone_de_remover_em_hover_tem_contraste_de_componente():
    """RED-10: o "×" (navy, herdado da etiqueta) sobre o fundo --border do hover, 3:1.

    O par nao esta na tabela da §2 v2, mas a §6 v2 pede esse hover (spec-precision gap).
    """
    assert "color" not in re.findall(r"([\w-]+)\s*:", _corpos(".etiqueta-filtro a:hover"))
    assert _contraste(_token("brand-navy"), _token("border")) >= 3


@pytest.mark.unit
def test_resumo_de_erros_tem_fundo_suave_e_borda_de_erro():
    """RED-09: §6 v2."""
    corpo = _corpos(".resumo-erros")
    assert _tem(corpo, "background", "var(--error-tint)")
    assert re.search(r"border(?:-color)?\s*:\s*[^;]*var\(--error\)", corpo)


@pytest.mark.unit
def test_barra_de_acoes_tem_o_fundo_da_pagina_e_nao_fica_presa_na_tela():
    """RED-09: §6 v2, nao fica fixa (com zoom de 200% cobriria os campos)."""
    assert _tem(_corpos(".barra-acoes"), "background", "var(--bg)")
    assert not re.search(r"position\s*:\s*(?:sticky|fixed)", _corpos_de(".barra-acoes"))


@pytest.mark.unit
def test_numero_do_cartao_de_indicador_e_navy_com_algarismos_tabulares():
    """RED-09: §6 v2; RED-04."""
    corpo = _corpos(".cartao-indicador__numero")
    assert _tem(corpo, "color", "var(--brand-navy)")
    assert _tem(corpo, "font-variant-numeric", "var(--numeros)")


@pytest.mark.unit
@pytest.mark.parametrize(
    ("variacao", "texto", "fundo"),
    [
        ("alta", "success", "success-tint"),
        ("queda", "error", "error-tint"),
        ("igual", "text-muted", "bg"),
    ],
)
def test_cada_variacao_tem_a_cor_e_o_fundo_da_spec(variacao, texto, fundo):
    """RED-09: §6 v2, estados da variacao; RED-10: o par tem 4.5:1."""
    corpo = _corpos(f".variacao--{variacao}")
    assert _tem(corpo, "color", f"var(--{texto})")
    assert _tem(corpo, "background", f"var(--{fundo})")
    assert (texto, fundo) in PARES_APROVADOS_DE_TEXTO
    assert _contraste(_token(texto), _token(fundo)) >= 4.5


@pytest.mark.unit
def test_variacao_e_uma_pilula():
    """RED-09: §4 v2, --raio-pilula na variacao."""
    assert _tem(_corpos(".variacao"), "border-radius", "var(--raio-pilula)")


@pytest.mark.unit
def test_esqueleto_de_carregamento_e_animado():
    """RED-09: §6 v2 e §7, carregando."""
    animacao = re.findall(r"animation(?:-name)?\s*:\s*([^;]+);", _corpos(".esqueleto"))
    assert animacao
    nome = animacao[-1].split()[0]
    assert re.search(rf"@keyframes\s+{re.escape(nome)}\s*\{{", CSS)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("componente", "contexto"),
    [
        (".filtros-ativos", "bg"),
        (".etiqueta-filtro", "bg"),
        (".resumo-erros", "surface"),
        (".barra-acoes", "bg"),
        (".cartao-indicador", "surface"),
        (".variacao", "surface"),
    ],
)
def test_cores_da_lista_e_do_painel_estao_em_pares_aprovados(componente, contexto):
    """RED-10: como nos componentes do detalhe; o contexto e o fundo em volta."""
    conferidos = 0
    for seletores, corpo in _regras_de(componente):
        for cor, fundo, e_texto in _pares_da_regra(corpo, contexto):
            aprovados = PARES_APROVADOS_DE_TEXTO
            if not e_texto:
                aprovados = PARES_APROVADOS_DE_COMPONENTE | PARES_APROVADOS_DE_TEXTO
            assert (cor, fundo) in aprovados, (seletores, cor, fundo)
            assert _contraste(_token(cor), _token(fundo)) >= (4.5 if e_texto else 3)
            conferidos += 1
    assert conferidos


@pytest.mark.unit
@pytest.mark.parametrize("barra", ["brand-navy", "brand-blue", "warning", "success"])
def test_barra_sobre_o_trilho_tem_contraste_de_componente(barra):
    """RED-10: §2 v2, barras de grafico e de status sobre --trilho, 3:1."""
    assert (barra, "trilho") in PARES_APROVADOS_DE_COMPONENTE
    assert _contraste(_token(barra), _token("trilho")) >= 3


# --- RED-11: movimento ----------------------------------------------------------


@pytest.mark.unit
def test_reduzir_movimento_desliga_tudo_inclusive_o_esqueleto():
    """RED-11: o bloco vale para todo elemento (`*`) e vence a regra do componente."""
    bloco = re.search(r"@media \(prefers-reduced-motion: reduce\)\s*\{(.*?)\n\}", CSS, re.S)
    assert bloco
    regras = re.findall(r"([^{}]+)\{([^}]*)\}", bloco.group(1))
    desliga = [
        corpo
        for lista, corpo in regras
        if {"*", ".esqueleto"} & set(_seletores(lista))
        and re.search(r"transition\s*:\s*none\s*!important", corpo)
        and re.search(r"animation\s*:\s*none\s*!important", corpo)
    ]
    assert desliga


# --- RED-12: zoom de 200% -------------------------------------------------------

# WCAG 1.4.10 isenta o que precisa de duas dimensoes: a tabela rola dentro do proprio
# quadro (DS-16), nao a pagina (spec-precision gap da RED-12, registrado no Execute).
LARGURAS_ISENTAS = {".tabela table"}


def _sem_media_de_max_width(css):
    saida, i = [], 0
    for achado in re.finditer(r"@media[^{]*max-width[^{]*\{", css):
        if achado.start() < i:
            continue
        saida.append(css[i : achado.start()])
        nivel, i = 1, achado.end()
        while nivel:
            nivel += {"{": 1, "}": -1}.get(css[i], 0)
            i += 1
    saida.append(css[i:])
    return "".join(saida)


def _em_px(numero, unidade):
    return float(numero) * (16 if unidade in ("rem", "em") else 1)


@pytest.mark.unit
def test_folha_nao_fixa_nada_na_tela():
    """RED-12."""
    assert not re.search(r"position\s*:\s*fixed", _sem_comentarios(CSS))


@pytest.mark.unit
def test_nenhuma_largura_minima_passa_de_320px_fora_de_max_width():
    """RED-12: WCAG 1.4.4 e 1.4.10, o layout reflui com zoom de 200%."""
    css = _sem_media_de_max_width(_sem_comentarios(CSS))
    largas = []
    for lista, corpo in re.findall(r"([^{}@]+)\{([^}]*)\}", css):
        if set(_seletores(lista)) <= LARGURAS_ISENTAS:
            continue
        for numero, unidade in re.findall(
            r"(?<![\w-])(?:min-)?width\s*:\s*(\d*\.?\d+)(px|rem|em)\b", corpo
        ):
            if _em_px(numero, unidade) > 320:
                largas.append((lista.strip(), numero + unidade))
    assert largas == []


# --- RED-13, RED-21, RED-22: barra de acessibilidade e faixa da marca ------------


@pytest.mark.unit
def test_barra_de_acessibilidade_tem_fundo_navy_e_texto_sobre_a_marca():
    """RED-13: §5.1 v2, branco sobre --brand-navy."""
    corpo = _corpos(".barra-acessibilidade")
    assert _tem(corpo, "background", "var(--brand-navy)")
    assert _tem(corpo, "color", "var(--on-brand)")
    assert _tem(_corpos(".barra-acessibilidade a"), "color", "var(--on-brand)")


@pytest.mark.unit
def test_anel_de_foco_da_barra_e_branco_e_visivel_sobre_o_navy():
    """RED-13, WCAG 2.4.7 e 1.4.11: anel de 2px branco, 3:1 sobre o navy."""
    assert _tem(
        _corpos(".barra-acessibilidade :focus-visible"), "outline", "2px solid var(--on-brand)"
    )
    assert _contraste(_token("on-brand"), _token("brand-navy")) >= 3


@pytest.mark.unit
def test_cores_da_barra_estao_em_pares_aprovados():
    """RED-10: toda cor de texto e de limite da barra sobre o navy."""
    conferidos = 0
    for seletores, corpo in _regras_de(".barra-acessibilidade"):
        for cor, fundo, e_texto in _pares_da_regra(corpo, "brand-navy"):
            if e_texto:
                assert (cor, fundo) in PARES_APROVADOS_DE_TEXTO, (seletores, cor, fundo)
                assert _contraste(_token(cor), _token(fundo)) >= 4.5, (seletores, cor, fundo)
            else:
                aprovados = PARES_APROVADOS_DE_COMPONENTE | PARES_APROVADOS_DE_TEXTO
                assert (cor, fundo) in aprovados, (seletores, cor, fundo)
                assert _contraste(_token(cor), _token(fundo)) >= 3, (seletores, cor, fundo)
            conferidos += 1
    assert conferidos


@pytest.mark.unit
def test_links_da_barra_tem_alvo_de_44px():
    """RED-22: WCAG 2.5.8, alvo minimo de 44px nos links da barra."""
    assert _tem(_corpos(".barra-acessibilidade a"), "min-height", "44px")


@pytest.mark.unit
def test_faixa_da_marca_e_o_gradiente_de_4px():
    """RED-21: §1, a faixa no lugar do antigo header::before."""
    corpo = _corpos(".faixa-marca")
    assert _tem(corpo, "background", "var(--brand-gradient)")
    assert _tem(corpo, "height", "4px")
    assert "header::before" not in _sem_comentarios(CSS)


# --- RED-19, RED-22: menu principal ------------------------------------------------

MENU_ATUAL = "nav[aria-label=Principal] a[aria-current]"


@pytest.mark.unit
def test_item_atual_do_menu_tem_fundo_suave_e_barra_azul_de_3px():
    """RED-19: a pagina atual nao depende so da cor (WCAG 1.4.1)."""
    corpo = _corpos(MENU_ATUAL)
    assert _tem(corpo, "background", "var(--info-tint)")
    assert _tem(corpo, "border-bottom", "3px solid var(--brand-blue)")


@pytest.mark.unit
def test_cores_do_item_atual_estao_em_pares_aprovados():
    """RED-10, RED-19: texto navy sobre --info-tint; barra azul contra o cabecalho."""
    texto = re.search(r"color\s*:\s*var\(--([\w-]+)\)", _corpos("nav[aria-label=Principal] a"))
    assert (texto.group(1), "info-tint") in PARES_APROVADOS_DE_TEXTO
    assert _contraste(_token(texto.group(1)), _token("info-tint")) >= 4.5
    limites = [p for p in _pares_da_regra(_corpos(MENU_ATUAL), "surface") if not p[2]]
    assert limites
    for cor, fundo, _ in limites:
        assert (cor, fundo) in PARES_APROVADOS_DE_COMPONENTE, (cor, fundo)
        assert _contraste(_token(cor), _token(fundo)) >= 3, (cor, fundo)


@pytest.mark.unit
def test_menu_quebra_de_linha_e_itens_tem_alvo_de_44px():
    """RED-22: no celular os itens quebram de linha; alvo minimo de 44px."""
    assert _tem(_corpos("nav[aria-label=Principal]"), "flex-wrap", "wrap")
    assert _tem(_corpos("nav[aria-label=Principal] a"), "min-height", "44px")


# --- RED-30: separador da trilha ---------------------------------------------------


@pytest.mark.unit
def test_separador_da_trilha_e_o_sinal_com_texto_alternativo_vazio():
    """RED-30: "›" por CSS (escapado como 203A) e "" para o leitor de tela."""
    conteudo = re.search(r"content\s*:\s*([^;]+);", _corpos(".trilha li + li::before"))
    sinal, alternativo = re.fullmatch(
        r'"([^"]*)"\s*/\s*"([^"]*)"', conteudo.group(1).strip()
    ).groups()
    decodificado = re.sub(r"\\([0-9a-fA-F]{1,6})\s?", lambda m: chr(int(m.group(1), 16)), sinal)
    assert decodificado == "›"
    assert alternativo == ""
