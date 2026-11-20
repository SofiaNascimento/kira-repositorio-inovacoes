"""Testes e2e da listagem de inovacoes (/inovacoes/)."""

import datetime
import re
from html.parser import HTMLParser

import pytest

from contas.models import Usuario
from inovacoes.models import Categoria, Inovacao, StatusInovacao, Unidade
from inovacoes.tests.visibilidade import VAZIOS, exibido

LISTA = "/inovacoes/"


@pytest.fixture
def logado(client, autor):
    client.force_login(autor)
    return client


class _Cartoes(HTMLParser):
    """Cada `article` do `ul aria-label="Resultados"`: o titulo (h2), o selo e os metadados."""

    def __init__(self):
        super().__init__()
        self.achou_lista = False
        self.pilha = []  # (tag, classes) abertas dentro da lista
        self.cartoes = []

    def handle_starttag(self, tag, attrs):
        atributos = dict(attrs)
        if not self.pilha:
            if tag == "ul" and atributos.get("aria-label") == "Resultados":
                self.achou_lista = True
                self.pilha.append((tag, []))
            return
        if tag in VAZIOS:
            return
        self.pilha.append((tag, (atributos.get("class") or "").split()))
        if tag == "article":
            self.cartoes.append({"titulo": "", "selo": "", "meta": []})
        elif tag == "li" and self._dentro_do_cartao():
            self.cartoes[-1]["meta"].append("")

    def handle_endtag(self, tag):
        if tag in [aberta for aberta, _ in self.pilha]:
            while self.pilha.pop()[0] != tag:
                pass

    def _dentro_do_cartao(self):
        return any(aberta == "article" for aberta, _ in self.pilha)

    def handle_data(self, data):
        if not self._dentro_do_cartao():
            return
        tags = [aberta for aberta, _ in self.pilha]
        dentro = self.pilha[tags.index("article") + 1 :]
        cartao = self.cartoes[-1]
        if any(aberta == "h2" for aberta, _ in dentro):
            cartao["titulo"] += data
        elif any("selo" in classes for _, classes in dentro):
            cartao["selo"] += data
        elif any(aberta == "li" for aberta, _ in dentro):
            cartao["meta"][-1] += data


def _texto(valor):
    return " ".join(valor.split())


def _linhas(html):
    """Cada cartao da lista de resultados como [titulo, categoria, unidade, status].

    T-A (redesign-consulta, T9, RCON-10): os resultados sao cartoes do
    `ul aria-label="Resultados"`, lidos no DOM do que a pagina exibe (L-028, L-030), e nao
    mais as linhas da tabela. A garantia das CONS-01 a 05, 08, 19 a 21, 27, 28, 40, 47 e 48
    continua: os mesmos quatro campos de cada item, na ordem da pagina. Sem a lista o
    helper falha, em vez de devolver uma lista vazia que passaria sem testar nada.
    """
    leitor = _Cartoes()
    leitor.feed(exibido(html, rigoroso=True))
    leitor.close()
    assert leitor.achou_lista, 'a pagina nao exibe o ul aria-label="Resultados"'
    # RCON-11: os metadados vem na ordem unidade, categoria, reaproveitamentos.
    return [
        [_texto(c["titulo"]), _texto(c["meta"][1]), _texto(c["meta"][0]), _texto(c["selo"])]
        for c in leitor.cartoes
    ]


def _forcar_data(inovacao, dia):
    data = datetime.datetime(2026, 9, dia, 12, 0, tzinfo=datetime.UTC)
    Inovacao.objects.filter(pk=inovacao.pk).update(data_criacao=data)


def test_lista_mostra_uma_linha_por_inovacao_com_os_quatro_campos(logado, criar_inovacao):
    """CONS-01, CONS-40: titulo, categoria, unidade e o rotulo do status."""
    criar_inovacao(titulo="Controle de Caixa")
    outra_unidade = Unidade.objects.create(nome="Teste Outra Unidade")
    outra_categoria = Categoria.objects.create(nome="Teste Outra Categoria")
    criar_inovacao(
        titulo="Conciliação",
        unidade=outra_unidade,
        categoria=outra_categoria,
        status=StatusInovacao.DISPONIVEL_PARA_REPLICACAO,
    )
    resposta = logado.get(LISTA)
    assert resposta.status_code == 200
    linhas = _linhas(resposta.content.decode())
    assert sorted(linhas) == [
        [
            "Conciliação",
            "Teste Outra Categoria",
            "Teste Outra Unidade",
            "Disponível para replicação",
        ],
        ["Controle de Caixa", "Teste Categoria", "Teste Unidade", "Em teste"],
    ]


def test_lista_ordena_pela_mais_recente_e_desempata_por_id(logado, criar_inovacao):
    """CONS-02."""
    antiga = criar_inovacao(titulo="Antiga")
    empate_1 = criar_inovacao(titulo="Empate um")
    empate_2 = criar_inovacao(titulo="Empate dois")
    _forcar_data(antiga, 1)
    _forcar_data(empate_1, 9)
    _forcar_data(empate_2, 9)
    titulos = [linha[0] for linha in _linhas(logado.get(LISTA).content.decode())]
    assert titulos == ["Empate dois", "Empate um", "Antiga"]


def test_titulo_de_cada_linha_e_link_para_o_detalhe(logado, criar_inovacao):
    """CONS-06.

    T-B (redesign-consulta, T9, RCON-11): o link fica no `h2` do cartao, e nao mais na
    celula da tabela. A garantia continua: o titulo exibido e o link para o detalhe.
    """
    inovacao = criar_inovacao(titulo="Controle de Caixa")
    html = exibido(logado.get(LISTA).content.decode(), rigoroso=True)
    url = re.escape(inovacao.get_absolute_url())
    assert re.search(rf'<h2[^>]*>\s*<a href="{url}">\s*Controle de Caixa\s*</a>\s*</h2>', html)
    assert inovacao.get_absolute_url() == f"/inovacoes/{inovacao.pk}/"


@pytest.mark.parametrize("perfil", ["USUARIO", "ADMINISTRADOR"])
def test_qualquer_perfil_ve_inovacoes_de_todos_os_autores_e_unidades(
    client, criar_inovacao, perfil
):
    """CONS-08."""
    outro_autor = Usuario.objects.create_user(username="bruno", email="bruno@x.com")
    outra_unidade = Unidade.objects.create(nome="Teste Outra Unidade")
    criar_inovacao(titulo="Da Ana")
    criar_inovacao(titulo="Do Bruno", autor=outro_autor, unidade=outra_unidade)
    leitor = Usuario.objects.create_user(
        username="carla", email="carla@x.com", perfil=perfil, password="senha-forte-123"
    )
    client.force_login(leitor)
    titulos = {linha[0] for linha in _linhas(client.get(LISTA).content.decode())}
    assert titulos == {"Da Ana", "Do Bruno"}


def test_anonimo_vai_ao_login_com_next_e_a_query_string_preservada(client):
    """CONS-07: o next e o do redirect_to_login do Django, com a query string."""
    resposta = client.get(f"{LISTA}?q=caixa")
    assert resposta.status_code == 302
    # Comparacao literal: assertRedirects normalizaria a query string.
    assert resposta["Location"] == "/entrar/?next=/inovacoes/%3Fq%3Dcaixa"


def test_contagem_no_singular(logado, criar_inovacao):
    """CONS-33."""
    criar_inovacao()
    assert "1 inovação encontrada" in logado.get(LISTA).content.decode()


def test_contagem_no_plural(logado, criar_inovacao):
    """CONS-33."""
    criar_inovacao(titulo="Uma")
    criar_inovacao(titulo="Duas")
    html = logado.get(LISTA).content.decode()
    assert "2 inovações encontradas" in html
    assert "1 inovação encontrada" not in html


def test_repositorio_vazio_mostra_mensagem_e_link_de_cadastro_sem_tabela(logado):
    """CONS-34."""
    html = logado.get(LISTA).content.decode()
    conteudo = html[html.index("<h1") :]
    assert "Nenhuma inovação cadastrada ainda." in conteudo
    assert re.search(r'<a href="/inovacoes/nova/">\s*Cadastrar inovação\s*</a>', conteudo)
    assert "<table" not in html
    assert "encontrada" not in html


def test_h1_e_titulo_da_pagina(logado):
    """CONS-01: a tela se identifica como Inovacoes."""
    assert re.search(r"<h1[^>]*>\s*Inovações\s*</h1>", logado.get(LISTA).content.decode())


def test_tabela_tem_caption_e_quatro_cabecalhos_de_coluna(logado, criar_inovacao):
    """CONS-38.

    T-B (redesign-consulta, T9, RCON-19): a tabela so aparece na exibicao em tabela; o
    teste abre `?exibicao=tabela`. A garantia continua: legenda e os quatro cabecalhos.
    """
    criar_inovacao()
    html = logado.get(f"{LISTA}?exibicao=tabela").content.decode()
    assert "<caption>Inovações cadastradas</caption>" in html
    cabecalhos = re.findall(r'<th scope="col">(.*?)</th>', html, re.S)
    assert [c.strip() for c in cabecalhos] == ["Título", "Categoria", "Unidade", "Status"]


@pytest.fixture
def vinte_e_cinco(criar_inovacao):
    """Titulos I00 a I24, criados em ordem: a mais nova (I24) abre a pagina 1."""
    for numero in range(25):
        criar_inovacao(titulo=f"I{numero:02d}")


def _paginacao(html):
    achado = re.search(r'<nav aria-label="Paginação">(.*?)</nav>', html, re.S)
    return achado.group(1) if achado else None


def test_primeira_pagina_tem_20_linhas_pagina_x_de_y_e_so_proxima(logado, vinte_e_cinco):
    """CONS-03."""
    html = logado.get(LISTA).content.decode()
    titulos = [linha[0] for linha in _linhas(html)]
    assert titulos == [f"I{n:02d}" for n in range(24, 4, -1)]
    nav = _paginacao(html)
    assert "Página 1 de 2" in nav
    assert re.search(r'<a href="\?page=2">\s*Próxima\s*</a>', nav)
    assert "Anterior" not in nav


def test_ultima_pagina_tem_o_restante_e_so_anterior(logado, vinte_e_cinco):
    """CONS-03."""
    html = logado.get(f"{LISTA}?page=2").content.decode()
    titulos = [linha[0] for linha in _linhas(html)]
    assert titulos == [f"I{n:02d}" for n in range(4, -1, -1)]
    nav = _paginacao(html)
    assert "Página 2 de 2" in nav
    assert re.search(r'<a href="\?page=1">\s*Anterior\s*</a>', nav)
    assert "Próxima" not in nav


def test_vinte_inovacoes_cabem_numa_pagina_sem_navegacao(logado, criar_inovacao):
    """CONS-03: com uma pagina so, nao ha <nav> de paginacao."""
    for numero in range(20):
        criar_inovacao(titulo=f"I{numero:02d}")
    html = logado.get(LISTA).content.decode()
    assert len(_linhas(html)) == 20
    assert _paginacao(html) is None
    assert "Página 1 de" not in html


@pytest.mark.parametrize("pagina", ["abc", "0"])
def test_pagina_invalida_mostra_a_primeira(logado, vinte_e_cinco, pagina):
    """CONS-05: nao inteiro cai na pagina 1; o zero tambem (Done-when da T5), com 200."""
    resposta = logado.get(f"{LISTA}?page={pagina}")
    assert resposta.status_code == 200
    assert "Página 1 de 2" in _paginacao(resposta.content.decode())


def test_pagina_alem_da_ultima_mostra_a_ultima(logado, vinte_e_cinco):
    """CONS-05."""
    resposta = logado.get(f"{LISTA}?page=99")
    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert "Página 2 de 2" in _paginacao(html)
    assert len(_linhas(html)) == 5


@pytest.mark.parametrize("pagina", ["1", "2"])
def test_contagem_e_o_total_de_todas_as_paginas(logado, vinte_e_cinco, pagina):
    """CONS-33."""
    html = logado.get(f"{LISTA}?page={pagina}").content.decode()
    assert "25 inovações encontradas" in html


def test_paginacao_fica_num_nav_rotulado(logado, vinte_e_cinco):
    """CONS-39."""
    html = logado.get(LISTA).content.decode()
    assert html.count('<nav aria-label="Paginação">') == 1
    assert _paginacao(html) is not None
