"""Testes e2e da tela "Minha unidade" (gestao-por-unidade, T8).

Derivados das ACs GEST-13 a GEST-19, GEST-64 e GEST-65
(.specs/features/gestao-por-unidade/spec.md). O exibido e lido do DOM parseado
(L-028, L-030).
"""

import datetime
import re

import pytest
from django.template.loader import render_to_string
from django.test import RequestFactory
from django.utils import timezone

from contas.models import Usuario
from contas.tests.conftest import GESTOR
from inovacoes.tests.visibilidade import exibido
from nucleo.tests.test_casca import _trilha

ADMINISTRADOR = Usuario.Perfil.ADMINISTRADOR
CABECALHOS = ["Nome", "Usuário", "E-mail", "Perfil", "Situação", "Último acesso", "Ações"]


def _tela(client):
    resposta = client.get("/minha-unidade/")
    assert resposta.status_code == 200
    return resposta.content.decode()


def _main(html):
    tela = exibido(html, rigoroso=True)
    return tela[tela.index('<main id="conteudo">') : tela.index("</main>")]


def _texto(trecho):
    return " ".join(re.sub(r"<[^>]+>", " ", trecho).split())


def _linhas(html):
    """Cada linha exibida da tabela: o texto das celulas e as acoes da ultima."""
    tabela = re.search(r'<div class="tabela">(.*?)</div>\s*</section>', _main(html), re.S)
    assert tabela, "sem a tabela exibida"
    corpo = re.search(r"<tbody>(.*?)</tbody>", tabela.group(1), re.S).group(1)
    linhas = []
    for linha in re.findall(r"<tr>(.*?)</tr>", corpo, re.S):
        celulas = re.findall(r"<td>(.*?)</td>", linha, re.S)
        acoes = re.findall(r"<(?:a|button)\b[^>]*>(.*?)</(?:a|button)>", celulas[-1], re.S)
        linhas.append(([_texto(c) for c in celulas[:-1]], [_texto(a) for a in acoes]))
    return linhas


@pytest.fixture
def unidade_povoada(gestor, criar_conta, sede, norte):
    """Contas da Sede fora da ordem de criacao, mais as de fora dela."""
    criar_conta("zeca", unidade=sede, first_name="Zeca", last_name="Alves")
    criar_conta("caio", unidade=sede, first_name="Caio", last_name="Reis", is_active=False)
    criar_conta("bia2", unidade=sede, first_name="Bia", last_name="Lima")
    criar_conta("bia1", unidade=sede, first_name="Bia", last_name="Lima")
    criar_conta("fabi", GESTOR, sede, first_name="Fabi", last_name="Rocha")
    criar_conta("hugo", ADMINISTRADOR, sede, first_name="Hugo", last_name="Dias")
    criar_conta("davi", unidade=norte, first_name="Davi", last_name="Melo")
    criar_conta("elis", first_name="Elis", last_name="Prado")


def test_cabecalho_tem_h1_nome_da_unidade_e_criar_conta(gestor_logado):
    """GEST-13, GEST-19: h1, o nome da unidade e a acao principal com o href."""
    main = _main(_tela(gestor_logado))
    cabecalho = re.search(r'<div class="cabecalho-pagina">(.*?)</div>', main, re.S).group(1)
    assert re.search(r"<h1>Minha unidade</h1>\s*<p>Sede</p>", cabecalho)
    criar = re.findall(r'<a class="botao" href="([^"]*)">Criar conta</a>', cabecalho)
    assert criar == ["/minha-unidade/contas/nova/"]


def test_tabela_tem_legenda_e_cabecalhos_de_coluna(gestor_logado):
    """GEST-13: caption "Contas da unidade {nome}" e as colunas, com th scope="col"."""
    main = _main(_tela(gestor_logado))
    secao = re.search(r'<section aria-labelledby="titulo-contas">(.*?)</section>', main, re.S)
    assert secao
    assert '<h2 id="titulo-contas">Contas da unidade</h2>' in secao.group(1)
    assert re.findall(r"<caption>(.*?)</caption>", secao.group(1)) == ["Contas da unidade Sede"]
    assert re.findall(r'<th scope="col">(.*?)</th>', secao.group(1)) == CABECALHOS


def test_linhas_sao_so_da_unidade_na_ordem_de_nome_e_usuario(gestor_logado, unidade_povoada):
    """GEST-14, GEST-15: todas as da Sede (inclusive a do gestor e a desativada), por
    nome completo e depois usuario; nenhuma de outra unidade nem sem unidade."""
    usuarios = [celulas[1] for celulas, _ in _linhas(_tela(gestor_logado))]
    assert usuarios == ["bia1", "bia2", "caio", "fabi", "gil", "hugo", "zeca"]


def test_celulas_mostram_nome_email_perfil_situacao_e_acesso(gestor_logado, unidade_povoada):
    """GEST-13, GEST-16: situacao por escrito; "Nunca" sem acesso."""
    Usuario.objects.filter(username="bia1").update(
        last_login=timezone.make_aware(datetime.datetime(2026, 11, 20, 9, 5))
    )
    linhas = {celulas[1]: celulas for celulas, _ in _linhas(_tela(gestor_logado))}
    assert linhas["bia1"] == [
        "Bia Lima",
        "bia1",
        "bia1@x.com",
        "Usuário",
        "Ativa",
        "20/11/2026 09:05",
    ]
    assert linhas["caio"] == ["Caio Reis", "caio", "caio@x.com", "Usuário", "Desativada", "Nunca"]
    assert linhas["fabi"][3:5] == ["Gestor de unidade", "Ativa"]
    assert linhas["hugo"][3:5] == ["Administrador", "Ativa"]


def test_acoes_so_nas_contas_usuario(gestor_logado, unidade_povoada):
    """GEST-17, GEST-18: Redefinir senha + Desativar (ativa) ou Reativar (desativada) nas
    contas USUARIO; nada no proprio gestor, no outro gestor e no ADMINISTRADOR."""
    acoes = {celulas[1]: botoes for celulas, botoes in _linhas(_tela(gestor_logado))}
    assert acoes == {
        "bia1": ["Redefinir senha", "Desativar"],
        "bia2": ["Redefinir senha", "Desativar"],
        "caio": ["Redefinir senha", "Reativar"],
        "fabi": [],
        "gil": [],
        "hugo": [],
        "zeca": ["Redefinir senha", "Desativar"],
    }


def test_unidade_renomeada_aparece_com_o_nome_novo(gestor_logado, sede):
    """GEST-64: o nome novo na requisicao seguinte."""
    assert "<p>Sede</p>" in _main(_tela(gestor_logado))
    sede.nome = "Sede Central"
    sede.save()
    main = _main(_tela(gestor_logado))
    assert re.search(r"<h1>Minha unidade</h1>\s*<p>Sede Central</p>", main)
    assert "<caption>Contas da unidade Sede Central</caption>" in main


def test_unidade_so_com_o_gestor_lista_ele_sem_acao_e_mantem_criar_conta(gestor_logado, gestor):
    """GEST-65. O login do gestor grava o ultimo acesso dele."""
    html = _tela(gestor_logado)
    gestor.refresh_from_db()
    acesso = timezone.localtime(gestor.last_login).strftime("%d/%m/%Y %H:%M")
    assert _linhas(html) == [
        (["Gil Souza", "gil", "gil@x.com", "Gestor de unidade", "Ativa", acesso], [])
    ]
    assert '<a class="botao" href="/minha-unidade/contas/nova/">Criar conta</a>' in _main(html)


def test_trilha_e_minha_unidade_como_pagina_atual(gestor_logado):
    """§5.3, T8: tela de primeiro nivel, so o item atual com aria-current="page"."""
    assert _trilha(_tela(gestor_logado)) == [("Minha unidade", None, "page")]


@pytest.mark.unit
def test_trilha_com_unidade_poe_minha_unidade_na_raiz():
    """T8: o parametro unidade da raiz "Minha unidade" -> /minha-unidade/."""
    requisicao = RequestFactory().get("/")
    html = render_to_string(
        "paginas/trilha.html", {"unidade": True, "atual": "Criar conta"}, request=requisicao
    )
    assert _trilha("</header>" + html + '<main id="conteudo">') == [
        ("Minha unidade", "/minha-unidade/", None),
        ("Criar conta", None, "page"),
    ]
