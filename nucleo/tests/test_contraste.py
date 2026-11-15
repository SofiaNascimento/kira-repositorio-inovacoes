"""Alto contraste: rota, cookie e botao (fundacao-do-redesign, RED-23 a RED-26, RED-37 a RED-42).

Fonte: docs/design-spec.md v2 §5.1 e §5.5; .specs/features/fundacao-do-redesign/spec.md.
Toda AC de "exibido" usa `exibido(html, rigoroso=True)` sobre a pagina inteira (L-028, L-030).
"""

import re

import pytest
from django.template.loader import render_to_string
from django.test import Client, override_settings

from inovacoes.tests.test_views_sistema_design import _elementos
from inovacoes.tests.visibilidade import exibido

pytestmark = pytest.mark.django_db

ROTA = "/acessibilidade/contraste/"
UM_ANO = 31536000
ABRE_FORM = '<form id="form-contraste" method="post" action="/acessibilidade/contraste/">'


def _cookie(resposta):
    """Os atributos do Set-Cookie do contraste que a spec fixa (sem o expires, que e a hora)."""
    morsel = resposta.cookies["kira_contraste"]
    return (
        morsel.value,
        str(morsel["max-age"]),
        morsel["httponly"],
        morsel["samesite"],
        morsel["secure"],
        morsel["path"],
    )


# --- RED-24, RED-25: gravar e apagar ---------------------------------------------


@pytest.mark.parametrize("autenticado", [False, True])
def test_alto_grava_o_cookie_de_um_ano_e_volta_a_pagina(client, autor, autenticado):
    """RED-24: anonimo ou autenticado; 302 para voltar_para, cookie HttpOnly e Lax."""
    if autenticado:
        client.force_login(autor)
    resposta = client.post(ROTA, {"contraste": "alto", "voltar_para": "/entrar/"})
    assert resposta.status_code == 302
    assert resposta["Location"] == "/entrar/"
    valor, max_age, httponly, samesite, _, path = _cookie(resposta)
    assert (valor, max_age, httponly, samesite, path) == ("alto", str(UM_ANO), True, "Lax", "/")


@pytest.mark.parametrize(("debug", "secure"), [(False, True), (True, "")])
def test_secure_do_cookie_segue_o_debug_desligado(client, debug, secure):
    """RED-24: Secure quando DEBUG esta desligado, como o cookie de sessao."""
    with override_settings(DEBUG=debug):
        resposta = client.post(ROTA, {"contraste": "alto", "voltar_para": "/entrar/"})
    assert resposta.cookies["kira_contraste"]["secure"] == secure


@pytest.mark.parametrize("autenticado", [False, True])
def test_normal_apaga_o_cookie_e_volta_a_pagina(client, autor, autenticado):
    """RED-25: o cookie sai (valor vazio, max-age 0) e a pagina volta."""
    if autenticado:
        client.force_login(autor)
    client.cookies["kira_contraste"] = "alto"
    resposta = client.post(ROTA, {"contraste": "normal", "voltar_para": "/inovacoes/?q=x&page=2"})
    assert resposta.status_code == 302
    assert resposta["Location"] == "/inovacoes/?q=x&page=2"
    morsel = resposta.cookies["kira_contraste"]
    assert morsel.value == ""
    assert str(morsel["max-age"]) == "0"
    # Depois de apagado, a pagina volta ao tema normal.
    html = client.get("/inovacoes/" if autenticado else "/entrar/").content.decode()
    assert re.findall(r"<html\b[^>]*>", html) == ['<html lang="pt-br">']


# --- RED-37: voltar_para so local -------------------------------------------------


@pytest.mark.parametrize(
    "dados",
    [
        {"voltar_para": "https://outro.example/"},
        {"voltar_para": "//outro.example/"},
        {"voltar_para": ""},
        {},
    ],
    ids=["externo", "sem-esquema", "vazio", "ausente"],
)
def test_voltar_para_fora_do_site_vazio_ou_ausente_vai_a_raiz(client, dados):
    """RED-37: so URL local segura; o resto redireciona a /."""
    resposta = client.post(ROTA, {"contraste": "alto", **dados})
    assert resposta.status_code == 302
    assert resposta["Location"] == "/"
    assert resposta.cookies["kira_contraste"].value == "alto"


# --- RED-38, RED-39: valor invalido, metodo e CSRF --------------------------------


@pytest.mark.parametrize("dados", [{}, {"contraste": "ALTO"}, {"contraste": "escuro"}])
def test_contraste_fora_de_alto_e_normal_responde_400_sem_cookie(client, dados):
    """RED-38: 400 e nenhum Set-Cookie; a preferencia que existia continua."""
    client.cookies["kira_contraste"] = "alto"
    resposta = client.post(ROTA, {"voltar_para": "/entrar/", **dados})
    assert resposta.status_code == 400
    assert "Set-Cookie" not in str(resposta.serialize_headers(), "latin-1")
    assert len(resposta.cookies) == 0
    html = client.get("/entrar/").content.decode()
    assert '<html lang="pt-br" data-contraste="alto">' in html


def test_get_na_rota_de_contraste_responde_405(client):
    """RED-39: so POST."""
    resposta = client.get(ROTA, {"contraste": "alto"})
    assert resposta.status_code == 405
    assert len(resposta.cookies) == 0


def test_post_sem_token_csrf_responde_403():
    """RED-39: CSRF padrao do Django."""
    cliente = Client(enforce_csrf_checks=True)
    resposta = cliente.post(ROTA, {"contraste": "alto", "voltar_para": "/entrar/"})
    assert resposta.status_code == 403
    assert "kira_contraste" not in resposta.cookies


def test_token_do_form_da_pagina_autoriza_o_post():
    """RED-23, RED-39: o form#form-contraste da pagina leva um token CSRF valido."""
    cliente = Client(enforce_csrf_checks=True)
    html = cliente.get("/entrar/").content.decode()
    campos = _campos_do_form(html)
    assert set(campos) == {"csrfmiddlewaretoken", "voltar_para"}
    resposta = cliente.post(ROTA, {**campos, "contraste": "alto"})
    assert resposta.status_code == 302
    assert resposta["Location"] == "/entrar/"
    assert resposta.cookies["kira_contraste"].value == "alto"


# --- RED-42: idempotente ------------------------------------------------------------


@pytest.mark.parametrize("valor", ["alto", "normal"])
def test_mesmo_post_duas_vezes_responde_igual(client, valor):
    """RED-42: o valor e explicito; reenviar nao alterna."""
    dados = {"contraste": valor, "voltar_para": "/entrar/"}
    primeira = client.post(ROTA, dados)
    segunda = client.post(ROTA, dados)
    assert primeira.status_code == segunda.status_code == 302
    assert primeira["Location"] == segunda["Location"] == "/entrar/"
    assert _cookie(primeira) == _cookie(segunda)
    assert _cookie(segunda)[0] == ("alto" if valor == "alto" else "")


# --- RED-26, RED-40: o tema na primeira resposta ----------------------------------


@pytest.mark.parametrize(
    ("cookie", "abertura"),
    [
        ("alto", '<html lang="pt-br" data-contraste="alto">'),
        ("ALTO", '<html lang="pt-br">'),
        ("sim", '<html lang="pt-br">'),
        ("", '<html lang="pt-br">'),
    ],
)
@pytest.mark.parametrize("autenticado", [False, True])
def test_html_marca_o_alto_contraste_so_com_o_cookie_alto(
    client, autor, cookie, abertura, autenticado
):
    """RED-26 (data-contraste no html, sem script); RED-40 (outro valor: tema normal)."""
    if autenticado:
        client.force_login(autor)
    client.cookies["kira_contraste"] = cookie
    html = client.get("/inovacoes/" if autenticado else "/entrar/").content.decode()
    assert re.findall(r"<html\b[^>]*>", html) == [abertura]
    assert "<script" not in html


# --- RED-23: o botao na barra e o form no fim do body ----------------------------


def _na_barra(html):
    """(abertura, conteudo) do unico botao de contraste entre o inicio da barra e o header."""
    barra = html[html.index('<div class="barra-acessibilidade">') : html.index("<header>")]
    achados = re.findall(r'(<button\b[^>]*name="contraste"[^>]*>)(.*?)</button>', barra, re.S)
    assert len(achados) == 1
    return achados[0]


def _botao(html):
    """(atributos, texto exibido, comeca com o icone decorativo) do botao de contraste."""
    abertura, conteudo = _na_barra(html)
    (_, atributos, _), *_ = _elementos(abertura)
    icone = re.match(r'\s*<svg aria-hidden="true" focusable="false"[^>]*>.*?</svg>', conteudo, re.S)
    # O texto vale como exibido: o icone e aria-hidden e o botao nao pode estar escondido.
    _, conteudo_exibido = _na_barra(exibido(html, rigoroso=True))
    texto = " ".join(re.sub(r"<[^>]*>", " ", conteudo_exibido).split())
    return atributos, texto, bool(icone)


@pytest.mark.parametrize(
    ("cookie", "pressionado", "valor"),
    [(None, "false", "alto"), ("alto", "true", "normal"), ("escuro", "false", "alto")],
)
@pytest.mark.parametrize("autenticado", [False, True])
def test_botao_da_barra_mostra_o_estado_e_pede_o_oposto(
    client, autor, cookie, pressionado, valor, autenticado
):
    """RED-23: "Alto contraste" com icone, form=form-contraste, valor oposto e aria-pressed."""
    if autenticado:
        client.force_login(autor)
    if cookie is not None:
        client.cookies["kira_contraste"] = cookie
    html = client.get("/inovacoes/" if autenticado else "/entrar/").content.decode()
    atributos, texto, com_icone = _botao(html)
    assert texto == "Alto contraste"
    assert com_icone
    assert atributos["form"] == "form-contraste"
    assert atributos["name"] == "contraste"
    assert atributos["value"] == valor
    assert atributos["aria-pressed"] == pressionado
    assert atributos.get("type", "submit") == "submit"
    assert html.count('id="form-contraste"') == 1


def _form(html):
    inicio = html.index(ABRE_FORM)
    return html[inicio : html.index("</form>", inicio) + len("</form>")]


def _campos_do_form(html):
    return {
        atributos["name"]: atributos.get("value")
        for tag, atributos, _ in _elementos(_form(html))
        if tag == "input"
    }


@pytest.mark.parametrize(
    ("autenticado", "caminho"),
    [(False, "/entrar/?next=/inovacoes/"), (True, "/inovacoes/?q=caixa&page=1")],
)
def test_form_do_contraste_e_o_ultimo_do_body_so_com_csrf_e_voltar_para(
    client, autor, autenticado, caminho
):
    """RED-23, AD-015: depois do footer; so CSRF e voltar_para (hidden), com caminho e query."""
    if autenticado:
        client.force_login(autor)
    html = client.get(caminho).content.decode()
    assert html.count(ABRE_FORM) == 1
    inicio = html.index(ABRE_FORM)
    assert html.index("</footer>") < inicio
    assert html.rindex("<form") == inicio
    assert html.index("</body>") > html.index("</form>", inicio)
    form = _form(html)
    elementos = [(tag, atributos) for tag, atributos, _ in _elementos(form)][1:]
    assert [(tag, atributos.get("type")) for tag, atributos in elementos] == [
        ("input", "hidden"),
        ("input", "hidden"),
    ]
    campos = _campos_do_form(html)
    assert campos["voltar_para"] == caminho
    assert re.fullmatch(r"[A-Za-z0-9]{64}", campos["csrfmiddlewaretoken"])


def test_no_login_o_primeiro_form_continua_o_do_login(client):
    """AD-015: o form do contraste fica no fim para nao passar a frente do login."""
    html = client.get("/entrar/").content.decode()
    primeiro = re.search(r"<form\b[^>]*>(.*?)</form>", html, re.S)
    assert 'id="form-contraste"' not in primeiro.group(0)
    assert 'name="username"' in primeiro.group(1)
    assert 'name="password"' in primeiro.group(1)


@pytest.mark.unit
def test_500_sem_request_nao_tem_botao_nem_form_do_contraste():
    """RED-41: a 500 renderiza sem request; sem CSRF, sem botao e sem form."""
    html = render_to_string("500.html")
    assert "form-contraste" not in html
    assert 'name="contraste"' not in html
    assert "csrfmiddlewaretoken" not in html
    assert "Alto contraste" not in html[html.index("</head>") :]
    assert re.findall(r"<html\b[^>]*>", html) == ['<html lang="pt-br">']
