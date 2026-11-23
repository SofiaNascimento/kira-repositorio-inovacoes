"""Testes e2e do link da administracao no cabecalho (link-administracao, ADM-01 a ADM-07).

Toda AC de "exibido" roda sobre o DOM parseado de `exibido()` (L-028, L-030, L-044).
"""

import re
from pathlib import Path

import pytest
from django.conf import settings

from contas.models import Usuario
from inovacoes.tests.test_views_sistema_design import CSS, _elementos
from inovacoes.tests.visibilidade import exibido

ADMIN = "/admin/"
TEXTO = "Administração"
ICONE = Path(settings.BASE_DIR) / "templates" / "icones" / "engrenagem.svg"
LINK = re.compile(rf'<a\b[^>]*\bhref="{re.escape(ADMIN)}"[^>]*>(.*?)</a>', re.S)
COR = re.compile(r"(?:^|;)\s*(?:color|background[\w-]*|text-decoration[\w-]*)\s*:")
SAIR = re.compile(r"<button\b[^>]*>\s*Sair\s*</button>")

PAGINAS_INTERNAS = [
    "/inovacoes/",
    "/inovacoes/nova/",
    "/inovacoes/{id}/",
    "/inovacoes/{id}/editar/",
    "/inovacoes/999999/",
    "/indicadores/",
    "/acessibilidade/",
    "/ajuda/",
]


def _texto(trecho):
    return " ".join(re.sub(r"<[^>]*>", " ", trecho).split())


def _area_do_usuario(html):
    """O `div.usuario` do cabecalho, ate o fim do `form` do Sair."""
    cabecalho = html[html.index("<header>") : html.index("</header>")]
    inicio = cabecalho.index('<div class="usuario">')
    return cabecalho[inicio : cabecalho.index("</form>", inicio)]


def _links_para_o_admin(html):
    """Conteudo de cada `<a href="/admin/">` exibido no cabecalho."""
    tela = exibido(html, rigoroso=True)
    return LINK.findall(tela[tela.index("<header>") : tela.index("</header>")])


def _formas(svg):
    """(tag, atributos) de cada forma do SVG, em ordem."""
    return [(tag, sorted(atributos.items())) for tag, atributos, _ in _elementos(svg)][1:]


@pytest.mark.parametrize("pagina", PAGINAS_INTERNAS)
def test_administrador_ve_o_link_na_area_do_usuario_entre_o_nome_e_o_sair(
    client, administrador, criar_inovacao, pagina
):
    """ADM-01: "Administração" -> /admin/ em toda pagina interna, no div.usuario, antes do Sair."""
    client.force_login(administrador)
    html = client.get(pagina.format(id=criar_inovacao().pk)).content.decode()
    conteudos = _links_para_o_admin(html)
    assert [_texto(exibido(conteudo)) for conteudo in conteudos] == [TEXTO]
    area = _area_do_usuario(exibido(html, rigoroso=True))
    nome = re.search(r"<span>\s*carla\s*</span>", area)
    link = LINK.search(area)
    sair = SAIR.search(area)
    assert nome and link and sair
    assert nome.end() < link.start() < sair.start()


@pytest.mark.parametrize("pagina", PAGINAS_INTERNAS)
def test_usuario_sem_perfil_administrador_nao_tem_link_para_o_admin(
    client, autor, criar_inovacao, pagina
):
    """ADM-02: USUARIO comum; nenhum href para /admin/ no HTML, nem escondido."""
    client.force_login(autor)
    resposta = client.get(pagina.format(id=criar_inovacao().pk))
    assert resposta.status_code in (200, 404)
    assert f'href="{ADMIN}' not in resposta.content.decode()


def test_usuario_com_is_staff_ou_superusuario_nao_tem_link_para_o_admin(client, nao_autor_usuario):
    """ADM-02 (AD-007, L-003): is_staff e is_superuser nao sao perfil ADMINISTRADOR."""
    client.force_login(nao_autor_usuario)
    html = client.get("/inovacoes/").content.decode()
    assert '<div class="usuario">' in html
    assert f'href="{ADMIN}' not in html


@pytest.mark.django_db
@pytest.mark.parametrize("pagina", ["/entrar/", "/acessibilidade/", "/ajuda/"])
def test_sem_sessao_nao_ha_link_para_o_admin(client, pagina):
    """ADM-03."""
    resposta = client.get(pagina)
    assert resposta.status_code == 200
    assert f'href="{ADMIN}' not in resposta.content.decode()


def test_icone_do_link_e_a_engrenagem_decorativa_e_o_nome_acessivel_e_o_texto(
    client, administrador
):
    """ADM-04: SVG da engrenagem aria-hidden antes do texto; nome acessivel "Administração"."""
    client.force_login(administrador)
    html = client.get("/inovacoes/").content.decode()
    abertura, conteudo = re.search(
        rf'(<a\b[^>]*\bhref="{re.escape(ADMIN)}"[^>]*>)(.*?)</a>', html, re.S
    ).groups()
    (_, atributos, _), *_ = _elementos(abertura)
    # Nada que troque o nome acessivel pelo de outra fonte.
    assert not {"aria-label", "aria-labelledby", "title"} & set(atributos)
    svg = re.match(r"\s*(<svg\b[^>]*>.*?</svg>)", conteudo, re.S)
    assert svg
    (tag, atributos_do_svg, _), *_ = _elementos(svg.group(1))
    assert tag == "svg"
    assert atributos_do_svg.get("aria-hidden") == "true"
    assert _formas(svg.group(1)) == _formas(ICONE.read_text())
    assert _texto(exibido(conteudo)) == TEXTO


def test_administrador_rebaixado_deixa_de_ver_o_link_na_proxima_pagina(client, administrador):
    """ADM-06: a troca de perfil vale na proxima pagina, com a mesma sessao."""
    client.force_login(administrador)
    assert _links_para_o_admin(client.get("/inovacoes/").content.decode())
    Usuario.objects.filter(pk=administrador.pk).update(perfil=Usuario.Perfil.USUARIO)
    html = client.get("/inovacoes/").content.decode()
    assert '<div class="usuario">' in html
    assert f'href="{ADMIN}' not in html


def _regras_que_alcancam_o_link():
    """Corpos das regras da folha cujo seletor alcanca um `a` dentro do div.usuario."""
    css = re.sub(r"/\*.*?\*/", "", CSS, flags=re.S)
    corpos = []
    for seletores, corpo in re.findall(r"([^{}]+)\{([^}]*)\}", css):
        for seletor in seletores.split(","):
            if re.fullmatch(r"\.usuario\s+(?:>\s*)?a(?::[\w-]+)?", seletor.strip()):
                corpos.append(corpo)
    return corpos


def test_no_alto_contraste_o_link_usa_os_pares_dos_links_da_casca(client, administrador):
    """ADM-07: link exibido no tema alto, sem estilo proprio de cor; vale `a` do tema alto."""
    client.force_login(administrador)
    client.cookies["kira_contraste"] = "alto"
    html = client.get("/inovacoes/").content.decode()
    assert '<html lang="pt-br" data-contraste="alto">' in html
    assert [_texto(exibido(conteudo)) for conteudo in _links_para_o_admin(html)] == [TEXTO]
    abertura = re.search(rf'<a\b[^>]*\bhref="{re.escape(ADMIN)}"[^>]*>', html).group()
    assert "style=" not in abertura
    # Nenhuma regra da area do usuario troca cor, fundo ou sublinhado do link.
    for corpo in _regras_que_alcancam_o_link():
        assert not COR.search(corpo)
    # Os pares da casca: o link segue o `a` do tema alto (sublinhado, --brand-blue amarelo).
    assert re.search(r":root\[data-contraste=alto\] a \{ text-decoration: underline; \}", CSS)
    assert re.search(r"(?:^|\n)a \{ color: var\(--brand-blue\);", CSS)


def test_admin_se_identifica_como_kira_e_volta_ao_sistema_pelo_ver_o_site(client, administrador):
    """ADM-05: cabecalho "KIRA — Administração" e "Ver o site" -> /inovacoes/."""
    client.force_login(administrador)
    resposta = client.get(ADMIN)
    assert resposta.status_code == 200
    tela = exibido(resposta.content.decode())
    marca = re.search(r'<div id="site-name">(.*?)</div>', tela, re.S)
    assert marca
    assert _texto(marca.group(1)) == "KIRA — Administração"
    ver_o_site = [
        href
        for href, conteudo in re.findall(r'<a\b[^>]*\bhref="([^"]*)"[^>]*>(.*?)</a>', tela, re.S)
        if _texto(conteudo) == "Ver o site"
    ]
    assert ver_o_site == ["/inovacoes/"]
