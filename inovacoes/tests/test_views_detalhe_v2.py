"""Testes e2e do detalhe da inovacao no redesign da consulta (R2, RCON-28 a RCON-46)."""

import datetime
import re
from pathlib import Path

import pytest
from django.conf import settings

from contas.models import Usuario
from inovacoes.models import Inovacao, StatusInovacao
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
