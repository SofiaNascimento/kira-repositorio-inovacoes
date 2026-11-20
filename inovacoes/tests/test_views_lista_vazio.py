"""Testes e2e dos estados vazios da lista (R2, RCON-25 a RCON-27)."""

import re

import pytest

from inovacoes.models import Categoria
from inovacoes.tests.test_folha_v2 import ALTO, _tem
from inovacoes.tests.test_views_sistema_design import _corpos
from inovacoes.tests.visibilidade import CLASSES_OCULTAS, exibido

LISTA = "/inovacoes/"
ILUSTRACAO = re.compile(r'<svg class="vazio__ilustracao" aria-hidden="true" focusable="false"')


@pytest.fixture
def logado(client, autor):
    client.force_login(autor)
    return client


def _main(html):
    return html[html.index("<main") : html.index("</main>")]


def _vazio(html):
    achado = re.search(r'<div class="vazio">(.*?)\n</div>', _main(html), re.S)
    assert achado, "sem o estado vazio"
    return achado.group(1)


def _textos(fragmento):
    return [" ".join(t.split()) for t in re.split(r"<[^>]+>", fragmento) if t.strip()]


def _sem_resultados(main):
    """Nenhum contador, lista de cartoes, tabela nem paginacao (RCON-25, RCON-26)."""
    assert 'class="total"' not in main
    assert "encontrada" not in main.replace("Nenhuma inovação encontrada para esta busca.", "")
    assert 'aria-label="Resultados"' not in main
    assert "<article" not in main
    assert "<table" not in main
    assert 'aria-label="Paginação"' not in main


def test_acervo_vazio_tem_ilustracao_texto_e_botao_de_cadastro(logado):
    """RCON-25: ilustracao, "Nenhuma inovação cadastrada ainda." e o link com estilo de botao."""
    html = logado.get(LISTA).content.decode()
    vazio = _vazio(html)
    assert ILUSTRACAO.search(vazio)
    assert _textos(_vazio(exibido(html, rigoroso=True))) == [
        "Nenhuma inovação cadastrada ainda.",
        "Cadastrar a primeira inovação",
    ]
    assert re.search(
        r'<p class="acoes acoes--primaria"><a href="/inovacoes/nova/">'
        r"Cadastrar a primeira inovação</a></p>",
        vazio,
    )
    _sem_resultados(_main(html))


def test_link_do_vazio_tem_estilo_de_botao_primario():
    """RCON-25: o link em .acoes--primaria e pintado como o botao primario."""
    assert _tem(_corpos(".acoes--primaria > a"), "background", "var(--brand-blue)")


def test_busca_sem_resultado_tem_ilustracao_textos_limpar_e_etiquetas(logado, criar_inovacao):
    """RCON-26: ilustracao, os dois textos, "Limpar filtros" -> /inovacoes/ e a etiqueta."""
    criar_inovacao()
    html = logado.get(LISTA, {"q": "xyzxyz"}).content.decode()
    vazio = _vazio(html)
    assert ILUSTRACAO.search(vazio)
    assert _textos(_vazio(exibido(html, rigoroso=True))) == [
        "Nenhuma inovação encontrada para esta busca.",
        "Tente outras palavras ou remova algum filtro.",
        "Limpar filtros",
    ]
    assert re.search(r'<a href="/inovacoes/">Limpar filtros</a>', vazio)
    exibida = exibido(_main(html), rigoroso=True)
    assert "Filtros ativos:" in exibida
    assert re.search(r'<span class="etiqueta-filtro">Busca: “xyzxyz”', exibida)
    _sem_resultados(_main(html))


def test_filtro_valido_sem_resultado_mantem_a_etiqueta(logado, criar_inovacao):
    """Edge case (RCON-26): um valor valido que nao casa com nada continua com a etiqueta."""
    criar_inovacao()
    rh = Categoria.objects.get(nome="RH")
    html = logado.get(LISTA, {"categoria": rh.pk}).content.decode()
    exibida = exibido(_main(html), rigoroso=True)
    assert "Nenhuma inovação encontrada para esta busca." in exibida
    assert re.search(r'<span class="etiqueta-filtro">Categoria: RH', exibida)


def test_ilustracao_e_decorativa(logado):
    """RCON-25: SVG aria-hidden e focusable="false"; nao sobra no que a pagina exibe."""
    html = logado.get(LISTA).content.decode()
    assert len(re.findall(r"<svg\b", _vazio(html))) == 1
    assert "<svg" not in _vazio(exibido(html, rigoroso=True))


def test_alto_contraste_esconde_so_a_ilustracao():
    """RCON-27: display none so sob [data-contraste=alto]; no tema normal ela aparece."""
    assert _tem(_corpos(f"{ALTO} .vazio__ilustracao"), "display", "none")
    assert "vazio__ilustracao" not in CLASSES_OCULTAS
    assert "vazio" not in CLASSES_OCULTAS
    assert _tem(_corpos(".vazio__ilustracao"), "max-width", "160px")


# --- Correcao da iteracao 1 (M27): a lista e o vazio se excluem ---

TEXTOS_DO_VAZIO = (
    "Nenhuma inovação cadastrada ainda.",
    "Cadastrar a primeira inovação",
    "Nenhuma inovação encontrada para esta busca.",
    "Tente outras palavras ou remova algum filtro.",
)


@pytest.mark.parametrize(
    "consulta", ["", "?exibicao=tabela", "?q=Planilha", "?q=Planilha&exibicao=tabela"]
)
def test_com_resultados_o_estado_vazio_nao_existe(logado, criar_inovacao, consulta):
    """RCON-10, RCON-19, RCON-25, RCON-26: havendo resultados, nenhum pedaco do vazio aparece."""
    criar_inovacao(titulo="Planilha de reembolso")
    html = logado.get(f"{LISTA}{consulta}").content.decode()
    main = _main(html)
    assert 'class="vazio"' not in main
    assert not ILUSTRACAO.search(main)
    exibido_main = _main(exibido(html, rigoroso=True))
    for texto in TEXTOS_DO_VAZIO:
        assert texto not in exibido_main
    # Os resultados estao la, na exibicao pedida.
    assert ("<table" in exibido_main) == ("exibicao=tabela" in consulta)
    assert ('aria-label="Resultados"' in exibido_main) == ("exibicao=tabela" not in consulta)
