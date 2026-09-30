"""Testes e2e de acessibilidade do formulario de cadastro (RNF09).

INOV-31, INOV-32, INOV-34 e INOV-35, lidos do HTML que o navegador recebe.
"""

import re
from html.parser import HTMLParser

import pytest

NOVA = "/inovacoes/nova/"
OBRIGATORIOS = ["titulo", "unidade", "categoria", "problema", "solucao", "contato"]
CONTROLES_DE_ENTRADA = {"input", "select", "textarea"}
PAPEIS_DE_CONTROLE = {"button", "link", "textbox", "combobox", "listbox", "checkbox", "option"}


class Pagina(HTMLParser):
    """Guarda cada elemento (tag, atributos, dentro do form?) e o texto dos labels."""

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
        self.elementos.append((tag, atributos, self._no_form))
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


@pytest.fixture
def pagina(client, autor):
    client.force_login(autor)
    resposta = client.get(NOVA)
    parser = Pagina()
    parser.feed(resposta.content.decode())
    parser.html = resposta.content.decode()
    return parser


def _controles(pagina):
    return {
        atributos["name"]: atributos
        for tag, atributos, no_form in pagina.elementos
        if no_form and tag in CONTROLES_DE_ENTRADA and atributos.get("type") != "hidden"
    }


def test_todo_campo_tem_rotulo_visivel_ligado_pelo_for(pagina):
    """INOV-31."""
    controles = _controles(pagina)
    assert len(controles) == 7
    for nome, atributos in controles.items():
        assert atributos.get("id"), nome
        assert pagina.rotulos.get(atributos["id"], "").strip(), nome
    for tag, atributos, _ in pagina.elementos:
        if tag == "label":
            assert "hidden" not in atributos and "visually-hidden" not in atributos.get("class", "")


def test_obrigatorios_tem_required_e_o_texto_obrigatorio_no_rotulo(pagina):
    """INOV-32: a obrigatoriedade nao depende da cor."""
    for nome, atributos in _controles(pagina).items():
        rotulo = pagina.rotulos[atributos["id"]]
        if nome in OBRIGATORIOS:
            assert "required" in atributos, nome
            assert "(obrigatório)" in rotulo, nome
        else:
            assert "required" not in atributos, nome
            assert "(obrigatório)" not in rotulo, nome


def test_formulario_so_usa_controles_nativos_sem_tabindex_positivo(pagina):
    """INOV-34: a ordem do teclado e a ordem do documento."""
    for tag, atributos, no_form in pagina.elementos:
        if no_form and atributos.get("role") in PAPEIS_DE_CONTROLE:
            raise AssertionError(f"controle nao nativo: <{tag} role={atributos['role']}>")
        if no_form and ("onclick" in atributos or "contenteditable" in atributos):
            raise AssertionError(f"controle nao nativo: <{tag}>")
        if "tabindex" in atributos:
            assert int(atributos["tabindex"]) <= 0, tag
    tags_do_form = {tag for tag, _, no_form in pagina.elementos if no_form}
    assert {"input", "select", "textarea", "button"} <= tags_do_form


def test_foco_visivel_alcanca_todo_controle(pagina):
    """INOV-35: seletor universal :focus-visible com contorno, sem outline removido."""
    css = " ".join(re.findall(r"<style>(.*?)</style>", pagina.html, re.S))
    regra = re.search(r"(^|[\s}]):focus-visible\s*\{([^}]*)\}", css)
    assert regra, "falta a regra :focus-visible"
    assert re.search(r"outline\s*:\s*\d+px\s+solid", regra.group(2))
    assert not re.search(r"outline\s*:\s*(none|0)\b", css)
