"""Testes e2e de "Trocar senha" (gestao-por-unidade, T13).

Derivados das ACs GEST-41 a GEST-47, GEST-68 e GEST-69
(.specs/features/gestao-por-unidade/spec.md). O exibido e lido do DOM parseado
(L-028, L-030).
"""

import re

import pytest
from pytest_django.asserts import assertRedirects

from contas.tests.conftest import SENHA_NOVA
from inovacoes.tests.visibilidade import exibido
from nucleo.tests.test_casca import _trilha

URL = "/conta/senha/"
SENHA_ATUAL = "atual-Senha-77"
AVISO = "Sua senha é provisória. Defina uma nova senha para continuar."
NOTA = "Nada é gravado se você cancelar."


def _main(html):
    tela = exibido(html, rigoroso=True)
    return tela[tela.index('<main id="conteudo">') : tela.index("</main>")]


def _texto(trecho):
    return " ".join(re.sub(r"<[^>]+>", " ", trecho).split())


def _barra(main):
    barra = re.search(r'<div class="barra-acoes">(.*?)</div>', main, re.S)
    assert barra
    return barra.group(1)


@pytest.fixture
def zeca(criar_conta):
    return criar_conta("zeca", first_name="Zeca", last_name="Pires", password=SENHA_ATUAL)


@pytest.fixture
def logado(client, zeca):
    client.force_login(zeca)
    return client


def _provisoria(conta):
    conta.senha_provisoria = True
    conta.save()


def _senha_mantida(conta, provisoria):
    conta.refresh_from_db()
    return conta.check_password(SENHA_ATUAL) and conta.senha_provisoria is provisoria


# --- GEST-41, GEST-47: a tela ---


def test_cabecalho_trilha_e_os_tres_campos(logado):
    """GEST-41, GEST-47: abre sem senha provisoria; h1, trilha de primeiro nivel e os
    tres campos obrigatorios, em ordem."""
    resposta = logado.get(URL)
    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert re.search(r"<title>Trocar senha · ", html)
    assert _trilha(html) == [("Trocar senha", None, "page")]
    main = _main(html)
    assert re.search(r"<h1>Trocar senha</h1>", main)
    rotulos = [_texto(r) for r in re.findall(r"<label[^>]*>(.*?)</label>", main, re.S)]
    assert rotulos == [
        "Senha atual (obrigatório)",
        "Nova senha (obrigatório)",
        "Confirmação da nova senha (obrigatório)",
    ]
    nomes = re.findall(r'<input type="password" name="([^"]+)"', main)
    assert nomes == ["old_password", "new_password1", "new_password2"]
    assert 'class="resumo-erros"' not in main


def test_sem_senha_provisoria_sem_aviso_e_com_cancelar_e_a_nota(logado):
    """GEST-42, GEST-69: sem senha provisoria, nenhum aviso; a barra tem o envio,
    "Cancelar" para /inovacoes/ e a nota."""
    main = _main(logado.get(URL).content.decode())
    assert AVISO not in main
    assert "alerta--warning" not in main
    assert re.fullmatch(
        r'\s*<button type="submit">Trocar senha</button>\s*'
        r'<a class="botao botao--secundario" href="/inovacoes/">Cancelar</a>\s*'
        r'<p class="barra-acoes__nota">Nada é gravado se você cancelar\.</p>\s*',
        _barra(main),
    )


def test_com_senha_provisoria_aviso_e_barra_sem_cancelar_nem_nota(logado, zeca):
    """GEST-42, GEST-69: o aviso exato, como alerta de aviso exibido; a barra so tem o
    envio, sem "Cancelar" e sem a nota."""
    _provisoria(zeca)
    main = _main(logado.get(URL).content.decode())
    avisos = re.findall(r'<p class="alerta alerta--warning">(.*?)</p>', main, re.S)
    assert [_texto(a) for a in avisos] == [AVISO]
    assert re.fullmatch(r'\s*<button type="submit">Trocar senha</button>\s*', _barra(main))
    assert "Cancelar" not in main
    assert NOTA not in main


# --- GEST-43: a troca valida ---


@pytest.mark.parametrize("provisoria", [True, False], ids=["provisoria", "definitiva"])
def test_troca_valida_desliga_provisoria_mantem_a_sessao_e_vai_a_lista(logado, zeca, provisoria):
    """GEST-43, GEST-47: troca a senha, desmarca a senha provisoria, a sessao segue
    aberta e a lista mostra "Senha alterada."."""
    if provisoria:
        _provisoria(zeca)
    resposta = logado.post(
        URL,
        {"old_password": SENHA_ATUAL, "new_password1": SENHA_NOVA, "new_password2": SENHA_NOVA},
    )
    assertRedirects(resposta, "/inovacoes/", fetch_redirect_response=False)
    zeca.refresh_from_db()
    assert zeca.check_password(SENHA_NOVA)
    assert zeca.senha_provisoria is False
    lista = logado.get("/inovacoes/")
    assert lista.status_code == 200
    main = _main(lista.content.decode())
    assert re.findall(r'<li class="alerta alerta--success">(.*?)</li>', main) == ["Senha alterada."]


# --- GEST-44 a GEST-46, GEST-68: o envio invalido ---


@pytest.mark.parametrize(
    ("dados", "campo", "rotulo", "mensagem"),
    [
        (
            {"old_password": "errada-Senha-1", "new_password1": SENHA_NOVA},
            "old_password",
            "Senha atual",
            "Senha atual incorreta.",
        ),
        (
            {"old_password": SENHA_ATUAL, "new_password1": SENHA_ATUAL},
            "new_password1",
            "Nova senha",
            "A nova senha precisa ser diferente da atual.",
        ),
        (
            {"old_password": SENHA_ATUAL, "new_password1": "83920571"},
            "new_password1",
            "Nova senha",
            "Esta senha é inteiramente numérica.",
        ),
        (
            {
                "old_password": SENHA_ATUAL,
                "new_password1": SENHA_NOVA,
                "new_password2": SENHA_NOVA + "x",
            },
            "new_password2",
            "Confirmação da nova senha",
            "As duas senhas não são iguais.",
        ),
    ],
    ids=["senha_atual", "igual_a_atual", "validador", "confirmacao"],
)
def test_erro_no_campo_com_resumo_e_titulo_sem_trocar(logado, zeca, dados, campo, rotulo, mensagem):
    """GEST-44, GEST-45, GEST-46, GEST-68: o erro so no campo certo, uma vez na
    pagina, o resumo com o link e "Erro:" no titulo; a senha nao muda."""
    dados.setdefault("new_password2", dados["new_password1"])
    resposta = logado.post(URL, dados)
    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert re.search(r"<title>Erro: Trocar senha · ", html)
    main = _main(html)
    erros = re.findall(r'<ul class="errorlist" id="id_(\w+)_error">(.*?)</ul>', main, re.S)
    assert [(nome, _texto(lista)) for nome, lista in erros] == [(campo, mensagem)]
    resumo = re.search(
        r'<div class="resumo-erros" role="alert" tabindex="-1" autofocus>(.*?)</div>', main, re.S
    )
    assert resumo
    assert "<p>Não foi possível trocar a senha. Corrija 1 campo(s):</p>" in resumo.group(1)
    links = re.findall(r'<a href="#([^"]+)">([^<]*)</a>', resumo.group(1))
    assert links == [(f"id_{campo}", f"{rotulo}: {mensagem}")]
    assert _texto(main).count(mensagem) == 2  # no resumo e no campo
    assert re.findall(r"<(\w+)[^>]*\bautofocus\b", main) == ["div"]
    assert _senha_mantida(zeca, provisoria=False)


def test_erro_com_senha_provisoria_mantem_o_aviso_e_a_barra_sem_cancelar(logado, zeca):
    """GEST-42, GEST-69: o envio que falha nao tira a senha provisoria nem devolve o
    "Cancelar"."""
    _provisoria(zeca)
    main = _main(
        logado.post(
            URL,
            {
                "old_password": "errada-Senha-1",
                "new_password1": SENHA_NOVA,
                "new_password2": SENHA_NOVA,
            },
        ).content.decode()
    )
    assert AVISO in _texto(main)
    assert re.fullmatch(r'\s*<button type="submit">Trocar senha</button>\s*', _barra(main))
    assert _senha_mantida(zeca, provisoria=True)
