"""Testes e2e do passe visual da tela de login (docs/design-spec.md §6, §8, §10 F1).

O card com a marca e a folha central ja sao cobertos pelo DS-15 e pelo DS-02
(inovacoes/tests/test_views_sistema_design.py); aqui entram o formulario
minimo, a indicacao de obrigatorio, o erro de credencial e o teclado.
"""

import re
from html.parser import HTMLParser

import pytest

from contas.models import Usuario

SENHA = "senha-forte-123"
CONTROLES = {"input", "select", "textarea", "button"}


class Formulario(HTMLParser):
    """Elementos dentro do <form> de login, em ordem, e o texto de cada <label>."""

    def __init__(self):
        super().__init__()
        self.elementos = []
        self.rotulos = {}
        self._no_form = False
        self._label = None

    def handle_starttag(self, tag, attrs):
        atributos = dict(attrs)
        if tag == "form":
            self._no_form = True
        elif self._no_form:
            self.elementos.append((tag, atributos))
        if tag == "label":
            self._label = atributos.get("for")
            self.rotulos[self._label] = ""

    def handle_endtag(self, tag):
        if tag == "form":
            self._no_form = False
        if tag == "label":
            self._label = None

    def handle_data(self, data):
        if self._label is not None:
            self.rotulos[self._label] += data


def _formulario(html):
    parser = Formulario()
    parser.feed(html)
    return parser


def _visiveis(formulario):
    return [
        (tag, atributos)
        for tag, atributos in formulario.elementos
        if tag in CONTROLES and atributos.get("type") != "hidden"
    ]


@pytest.fixture
def conta(db):
    return Usuario.objects.create_user(username="elis", email="elis@x.com", password=SENHA)


@pytest.mark.django_db
def test_formulario_minimo_com_usuario_senha_e_um_botao(client):
    """§10 F1: so identificador, senha e "Entrar", nessa ordem (ordem do teclado)."""
    visiveis = _visiveis(_formulario(client.get("/entrar/").content.decode()))
    assert [(t, a.get("name"), a.get("type")) for t, a in visiveis] == [
        ("input", "username", "text"),
        ("input", "password", "password"),
        ("button", None, "submit"),
    ]


@pytest.mark.django_db
def test_cada_campo_tem_rotulo_visivel_ligado_pelo_for(client):
    """§6, WCAG 1.3.1 e 3.3.2: rotulo visivel, associado por for/id."""
    formulario = _formulario(client.get("/entrar/").content.decode())
    textos = {
        a["name"]: formulario.rotulos.get(a.get("id"), "").strip()
        for t, a in _visiveis(formulario)
        if t == "input"
    }
    assert textos == {"username": "Usuário ou e-mail:", "password": "Senha:"}
    for tag, atributos in formulario.elementos:
        if tag == "label":
            assert "hidden" not in atributos
            assert "visually-hidden" not in atributos.get("class", "")


@pytest.mark.django_db
def test_obrigatoriedade_dita_em_texto_e_no_atributo_required(client):
    """§6: campo obrigatorio indicado por texto, nao so por cor."""
    html = client.get("/entrar/").content.decode()
    form = re.search(r"<form[^>]*>(.*?)</form>", html, re.S).group(1)
    legenda = re.search(r'<p class="legenda">\s*(.*?)\s*</p>', form, re.S)
    assert legenda
    assert legenda.group(1) == "Os dois campos são obrigatórios."
    assert form.index('class="legenda"') < form.index('id="id_username"')
    for tag, atributos in _visiveis(_formulario(html)):
        if tag == "input":
            assert "required" in atributos, atributos["name"]


def test_credencial_invalida_avisa_em_texto_sem_marcar_nenhum_campo(client, conta):
    """§10 F1: erro em texto, antes dos campos, sem apontar qual campo falhou."""
    html = client.post("/entrar/", {"username": "elis", "password": "errada-456"}).content.decode()
    form = re.search(r"<form[^>]*>(.*?)</form>", html, re.S).group(1)
    alerta = re.search(r'<div role="alert">\s*<p>(.*?)</p>\s*</div>', form, re.S)
    assert alerta
    assert alerta.group(1) == "Usuário ou senha inválidos."
    assert form.index('role="alert"') < form.index('id="id_username"')
    assert "errorlist" not in form
    for _, atributos in _visiveis(_formulario(html)):
        assert "aria-invalid" not in atributos


@pytest.mark.django_db
def test_teclado_so_controles_nativos_sem_tabindex_positivo(client):
    """§8 Operavel: tudo pelo teclado, na ordem do documento, sem armadilha."""
    formulario = _formulario(client.get("/entrar/").content.decode())
    for tag, atributos in formulario.elementos:
        assert "onclick" not in atributos and "contenteditable" not in atributos, tag
        assert "role" not in atributos or tag == "div", (tag, atributos.get("role"))
        if "tabindex" in atributos:
            assert int(atributos["tabindex"]) <= 0, tag
    primeiro = _visiveis(formulario)[0][1]
    assert primeiro["name"] == "username"
    assert "autofocus" in primeiro
