"""Testes e2e do detalhe da inovacao no redesign da consulta (R2, RCON-28 a RCON-46)."""

import datetime
import re
from pathlib import Path

import pytest
from django.conf import settings

from contas.models import Usuario
from inovacoes.models import Inovacao, StatusInovacao, Unidade
from inovacoes.tests.test_folha_v2 import _regras_aninhadas, _seletores, _sem_comentarios
from inovacoes.tests.test_views_sistema_design import CSS, _corpos
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


# --- RCON-29 a RCON-33, RCON-50: narrativa, resumo lateral e grade ---


def _secao_narrativa(tela):
    inicio = tela.index('<section class="narrativa" aria-labelledby="narrativa-titulo">')
    return tela[inicio : tela.index("</section>", inicio) + len("</section>")]


def _aside(tela):
    inicio = tela.index('<aside aria-label="Resumo da inovação">')
    return tela[inicio : tela.index("</aside>", inicio) + len("</aside>")]


def test_narrativa_tem_os_tres_passos_em_ordem_com_o_texto_completo(logado, criar_inovacao):
    """RCON-29: h2 "Como a inovação funciona"; ol com tres h3 na ordem e o texto inteiro."""
    longo = "Conferencia manual " * 30
    inovacao = criar_inovacao(problema=f"{longo}\nfim", solucao="c\nd", resultado="e\nf")
    secao = _secao_narrativa(exibido(_pagina(logado, inovacao), rigoroso=True))
    assert re.findall(r"<h2[^>]*>(.*?)</h2>", secao) == ["Como a inovação funciona"]
    passos = re.findall(
        r"<li>\s*<h3>(.*?)</h3>\s*<p[^>]*>(.*?)</p>\s*</li>",
        re.search(r"</h2>\s*<ol>(.*?)</ol>", secao, re.S).group(1),
        re.S,
    )
    assert passos == [
        ("Problema ou dor", f"{longo}<br>fim"),
        ("Solução aplicada", "c<br>d"),
        ("Resultado ou impacto", "e<br>f"),
    ]


def test_resultado_vazio_le_resultado_ainda_nao_informado(logado, criar_inovacao):
    """RCON-30: o terceiro passo le "Resultado ainda não informado." em --text-muted."""
    secao = _secao_narrativa(exibido(_pagina(logado, criar_inovacao(resultado="")), rigoroso=True))
    assert re.search(
        r"<h3>Resultado ou impacto</h3>\s*"
        r'<p class="narrativa__vazio">Resultado ainda não informado\.</p>',
        secao,
    )
    assert re.search(r"color\s*:\s*var\(--text-muted\)", _corpos(".narrativa__vazio"))


def test_aside_vem_depois_da_narrativa_e_antes_dos_reaproveitamentos(logado, criar_inovacao):
    """RCON-31: o aside fica entre a narrativa e os reaproveitamentos; contato antes da ficha."""
    tela = exibido(_pagina(logado, criar_inovacao()), rigoroso=True)
    narrativa = tela.index('<section class="narrativa"')
    aside = tela.index('<aside aria-label="Resumo da inovação">')
    reaproveitamentos = tela.index('<section aria-labelledby="reaproveitamentos-titulo">')
    assert narrativa < aside < reaproveitamentos
    lateral = _aside(tela)
    assert lateral.index('<div class="cartao-contato">') < lateral.index(
        '<dl class="ficha-resumo">'
    )
    assert tela.count("<aside") == 1


def test_cartao_de_contato_tem_titulo_texto_com_quebras_e_a_nota(logado, criar_inovacao):
    """RCON-32: titulo, o contato como digitado (quebras preservadas) e a nota."""
    contato = "Ana Souza\nRamal 1234\nana@x.com"
    lateral = _aside(exibido(_pagina(logado, criar_inovacao(contato=contato)), rigoroso=True))
    cartao = re.search(r'<div class="cartao-contato">(.*?)</div>', lateral, re.S).group(1)
    assert re.findall(r"<h2>(.*?)</h2>", cartao) == ["Contato responsável"]
    assert f'<p class="cartao-contato__texto">{contato}</p>' in cartao
    nota = "Procure esta pessoa para tirar dúvidas antes de replicar."
    assert f'<p class="cartao-contato__nota">{nota}</p>' in cartao
    # As quebras digitadas so aparecem na tela porque a folha as preserva.
    assert re.search(r"white-space\s*:\s*pre-line", _corpos(".cartao-contato__texto"))


def test_ficha_tem_os_cinco_pares_na_ordem(logado, autor, terceiro, criar_inovacao):
    """RCON-33: Unidade de origem, Categoria, Cadastrada por, Cadastrada em e Reaproveitamentos."""
    inovacao = criar_inovacao(status=DISPONIVEL)
    Inovacao.objects.filter(pk=inovacao.pk).update(
        data_criacao=datetime.datetime(2026, 9, 15, 2, 30, tzinfo=datetime.UTC)
    )
    for nome in ["Sede", "Filial Norte"]:
        inovacao.registrar_reaproveitamento(unidade=Unidade.objects.get(nome=nome), por=terceiro)
    lateral = _aside(exibido(_pagina(logado, inovacao), rigoroso=True))
    ficha = re.search(r'<dl class="ficha-resumo">(.*?)</dl>', lateral, re.S).group(1)
    pares = re.findall(r"<dt>(.*?)</dt>\s*<dd>(.*?)</dd>", ficha, re.S)
    assert pares == [
        ("Unidade de origem", "Teste Unidade"),
        ("Categoria", "Teste Categoria"),
        ("Cadastrada por", "Ana Souza"),
        ("Cadastrada em", "14/09/2026"),
        ("Reaproveitamentos", "2"),
    ]
    assert len(re.findall(r"<dt>", ficha)) == 5


def test_narrativa_e_contato_saem_escapados(logado, criar_inovacao):
    """CONS-17 (edge case da R2): HTML digitado no problema e no contato sai como texto."""
    inovacao = criar_inovacao(problema="<b>p</b>", contato="<u>c</u>")
    html = _pagina(logado, inovacao)
    assert "&lt;b&gt;p&lt;/b&gt;" in _secao_narrativa(html)
    assert '<p class="cartao-contato__texto">&lt;u&gt;c&lt;/u&gt;</p>' in _aside(html)
    assert "<b>p</b>" not in html
    assert "<u>c</u>" not in html


def _regras_no_contexto(contexto):
    return {
        seletor: corpo
        for ctx, lista, corpo in _regras_aninhadas(_sem_comentarios(CSS))
        if ctx == contexto
        for seletor in _seletores(lista)
    }


def test_grade_de_duas_colunas_so_a_partir_de_45rem():
    """RCON-50, RCON-31: abaixo de 720px uma coluna; a partir de 45rem o aside vai a direita.

    O aside fica na coluna 2, linhas 1 a 3, ao lado da narrativa que o precede (RCON-47).
    """
    globais = _regras_no_contexto(())
    assert re.search(r"display\s*:\s*grid", globais[".detalhe"])
    assert "grid-template-columns" not in globais[".detalhe"]
    assert not any(
        "grid-template-columns" in corpo or "grid-column" in corpo
        for seletor, corpo in globais.items()
        if seletor.startswith(".detalhe")
    )
    larga = _regras_no_contexto(("@media (min-width: 45rem)",))
    assert re.search(
        r"grid-template-columns\s*:\s*minmax\(0,\s*2fr\)\s+minmax\(0,\s*1fr\)",
        larga[".detalhe"],
    )
    assert re.search(r"grid-column\s*:\s*1\s*;", larga[".detalhe > *"])
    assert re.search(r"grid-column\s*:\s*2\s*;", larga[".detalhe > aside"])
    assert re.search(r"grid-row\s*:\s*1\s*/\s*span\s+3\s*;", larga[".detalhe > aside"])


def test_passos_da_narrativa_sao_numerados_pela_folha_como_decoracao():
    """RCON-29: o numero do passo vem do counter no ::before, com texto alternativo vazio."""
    assert re.search(r"counter-reset\s*:\s*passo", _corpos(".narrativa ol"))
    assert re.search(r"counter-increment\s*:\s*passo", _corpos(".narrativa li"))
    antes = _corpos(".narrativa li::before")
    assert re.search(r'content\s*:\s*counter\(passo\)\s*/\s*""', antes)


def test_regras_da_ficha_antiga_sairam_da_folha():
    """RCON-33: a ficha antiga, o selo no dd e o destaque do contato nao tem mais uso."""
    sem_comentarios = _sem_comentarios(CSS)
    seletores = [
        s
        for lista, _ in re.findall(r"([^{}]+)\{([^}]*)\}", sem_comentarios)
        for s in _seletores(lista)
    ]
    assert [s for s in seletores if re.search(r"\.ficha(?![\w-])|\.destaque\b", s)] == []


# --- RCON-34, RCON-41 (texto), RCON-42: ciclo de vida no resumo ---

AJUDA_DO_AVANCO = "O status avança um estágio por vez e não volta ao anterior."
QUEM_PODE_AVANCAR = "Só quem cadastrou a inovação ou um administrador pode avançar o status."
ULTIMO_ESTAGIO = "Último estágio do ciclo. O status avança um estágio por vez e não volta."
PERFIS = ["autor", "administrador", "terceiro", "staff"]
PODEM_ALTERAR = {"autor", "administrador"}


@pytest.fixture
def staff(db):
    """USUARIO com is_staff que nao e o autor: nao pode alterar (AD-009, L-003)."""
    return Usuario.objects.create_user(username="dora_staff", email="ds@x.com", is_staff=True)


def _como(client, request, perfil, inovacao):
    client.force_login(request.getfixturevalue(perfil))
    return _pagina(client, inovacao)


def _ciclo_exibido(html):
    """O bloco "Ciclo de vida" do aside, como a tela o exibe."""
    lateral = _aside(exibido(html, rigoroso=True))
    inicio = lateral.index('<section aria-labelledby="ciclo-titulo">')
    return lateral[inicio : lateral.index("</section>", inicio)]


def _etapas(bloco):
    lista = re.search(r'<ol class="etapas">(.*?)</ol>', bloco, re.S).group(1)
    return [
        (atributos, " ".join(re.sub(r"<[^>]+>", "", item).split()))
        for atributos, item in re.findall(r"<li\b([^>]*)>(.*?)</li>", lista, re.S)
    ]


@pytest.mark.parametrize(
    ("status", "esperado"),
    [
        (
            EM_TESTE,
            [
                "Em teste (status atual)",
                "Validada · próxima etapa",
                "Disponível para replicação · próxima etapa",
            ],
        ),
        (
            VALIDADA,
            [
                "Em teste · concluída",
                "Validada (status atual)",
                "Disponível para replicação · próxima etapa",
            ],
        ),
        (
            DISPONIVEL,
            [
                "Em teste · concluída",
                "Validada · concluída",
                "Disponível para replicação (status atual)",
            ],
        ),
    ],
    ids=str,
)
def test_etapas_dizem_a_situacao_em_texto_e_so_a_atual_tem_aria_current(
    logado, criar_inovacao, status, esperado
):
    """RCON-34: h2 "Ciclo de vida", ol com as tres etapas na ordem e a situacao em texto."""
    bloco = _ciclo_exibido(_pagina(logado, criar_inovacao(status=status)))
    assert re.findall(r"<h2[^>]*>(.*?)</h2>", bloco) == ["Ciclo de vida"]
    etapas = _etapas(bloco)
    assert [texto for _, texto in etapas] == esperado
    atuais = [texto for atributos, texto in etapas if 'aria-current="step"' in atributos]
    assert atuais == [t for t in esperado if t.endswith("(status atual)")]


def test_marcadores_das_etapas_sao_decorativos(logado, criar_inovacao):
    """RCON-34: cada etapa tem um marcador `aria-hidden="true"`, fora do texto lido."""
    html = _pagina(logado, criar_inovacao(status=VALIDADA))
    lateral = _aside(html)
    itens = re.findall(r'<li class="etapa etapa--(\w+)"[^>]*>(.*?)</li>', lateral, re.S)
    assert [situacao for situacao, _ in itens] == ["concluida", "atual", "futura"]
    for _, item in itens:
        assert re.match(r'\s*<span class="etapa__marcador" aria-hidden="true">', item)
    # O texto da situacao, fora do marcador, continua exibido (L-028, L-044).
    assert not {"etapas", "etapa", "etapa--atual"} & CLASSES_OCULTAS


def test_ciclo_fica_entre_o_contato_e_a_ficha(logado, criar_inovacao):
    """RCON-31: dentro do aside, contato, ciclo de vida e ficha, nessa ordem."""
    lateral = _aside(exibido(_pagina(logado, criar_inovacao()), rigoroso=True))
    contato = lateral.index('<div class="cartao-contato">')
    ciclo = lateral.index('<section aria-labelledby="ciclo-titulo">')
    ficha = lateral.index('<dl class="ficha-resumo">')
    assert contato < ciclo < ficha


def _explicacao(bloco):
    achado = re.search(r'<p\b[^>]*\bid="ciclo-explicacao"[^>]*>(.*?)</p>', bloco, re.S)
    assert achado, "sem a explicacao exibida"
    return achado.group(1).strip()


@pytest.mark.parametrize("perfil", PERFIS)
@pytest.mark.parametrize("status", [EM_TESTE, VALIDADA, DISPONIVEL], ids=str)
def test_explicacao_do_ciclo_por_status_e_perfil(
    client, request, criar_inovacao, staff, status, perfil
):
    """RCON-41, RCON-42: o texto exato por status e por quem pode ou nao alterar (L-003)."""
    bloco = _ciclo_exibido(_como(client, request, perfil, criar_inovacao(status=status)))
    if status == DISPONIVEL:
        esperado = ULTIMO_ESTAGIO
    elif perfil in PODEM_ALTERAR:
        esperado = AJUDA_DO_AVANCO
    else:
        esperado = QUEM_PODE_AVANCAR
    assert _explicacao(bloco) == esperado
    outros = {ULTIMO_ESTAGIO, AJUDA_DO_AVANCO, QUEM_PODE_AVANCAR} - {esperado}
    assert [texto for texto in outros if texto in bloco] == []


@pytest.mark.parametrize("perfil", PERFIS)
@pytest.mark.parametrize("status", [EM_TESTE, VALIDADA, DISPONIVEL], ids=str)
def test_botao_desabilitado_so_no_ultimo_estagio_para_quem_pode_alterar(
    client, request, criar_inovacao, staff, status, perfil
):
    """RCON-42: "Avançar status" com aria-disabled, descrito pelo texto, so para quem pode."""
    bloco = _ciclo_exibido(_como(client, request, perfil, criar_inovacao(status=status)))
    botoes = re.findall(r"<button\b([^>]*)>(.*?)</button>", bloco, re.S)
    if status == DISPONIVEL and perfil in PODEM_ALTERAR:
        assert [texto.strip() for _, texto in botoes] == ["Avançar status"]
        atributos = botoes[0][0]
        assert 'aria-disabled="true"' in atributos
        assert re.search(r"\sdisabled\b", atributos.replace("aria-disabled", "")) is None
        assert 'aria-describedby="ciclo-explicacao"' in atributos
    else:
        assert botoes == []
