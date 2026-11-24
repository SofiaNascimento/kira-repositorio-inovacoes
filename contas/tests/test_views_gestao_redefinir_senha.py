"""Testes e2e de "Redefinir senha" na area do gestor (gestao-por-unidade, T12).

Derivados das ACs GEST-37 a GEST-39, GEST-62, GEST-68 e GEST-69 e do edge case
de alvo fora do escopo (.specs/features/gestao-por-unidade/spec.md). O exibido
e lido do DOM parseado (L-028, L-030).
"""

import re

import pytest
from django.test import Client
from pytest_django.asserts import assertRedirects

from contas.models import Usuario
from contas.tests.conftest import GESTOR, SENHA_NOVA
from inovacoes.tests.visibilidade import exibido
from nucleo.tests.test_casca import _menu_da_tela, _trilha

SENHA_ANTIGA = "antiga-Senha-99"
ALERTA = "Senha de “bia” redefinida. Informe a senha provisória à pessoa."


def _url(conta_ou_pk):
    pk = getattr(conta_ou_pk, "pk", conta_ou_pk)
    return f"/minha-unidade/contas/{pk}/senha/"


def _main(html):
    tela = exibido(html, rigoroso=True)
    return tela[tela.index('<main id="conteudo">') : tela.index("</main>")]


def _texto(trecho):
    return " ".join(re.sub(r"<[^>]+>", " ", trecho).split())


def _senha_mantida(conta):
    conta.refresh_from_db()
    return conta.check_password(SENHA_ANTIGA) and not conta.senha_provisoria


@pytest.fixture
def bia(criar_conta, sede):
    return criar_conta(
        "bia", unidade=sede, first_name="Bia", last_name="Lima", password=SENHA_ANTIGA
    )


# --- A tela ---


def test_cabecalho_descricao_trilha_e_menu(gestor_logado, bia):
    """Design (Telas), GEST-11: h1, descricao com o usuario e o nome, trilha
    "Minha unidade › Redefinir senha" e o menu na secao."""
    html = gestor_logado.get(_url(bia)).content.decode()
    assert re.search(
        r"<h1>Redefinir senha</h1>\s*<p>Conta “bia” \(Bia Lima\)\. A pessoa troca a senha no "
        r"próximo acesso\.</p>",
        _main(html),
    )
    assert re.search(r"<title>Redefinir senha · ", html)
    assert _trilha(html) == [
        ("Minha unidade", "/minha-unidade/", None),
        ("Redefinir senha", None, "page"),
    ]
    assert {t: c for _, c, t in _menu_da_tela(html) if c} == {"Minha unidade": "true"}


def test_formulario_tem_os_dois_campos_e_a_barra_de_acoes(gestor_logado, bia):
    """GEST-37, GEST-69: as duas senhas, depois "Redefinir senha", Cancelar e a nota."""
    main = _main(gestor_logado.get(_url(bia)).content.decode())
    rotulos = [_texto(r) for r in re.findall(r"<label[^>]*>(.*?)</label>", main, re.S)]
    assert rotulos == [
        "Nova senha provisória (obrigatório)",
        "Confirmação da nova senha provisória (obrigatório)",
    ]
    barra = re.search(r'<div class="barra-acoes">(.*?)</div>', main, re.S)
    assert barra
    assert re.fullmatch(
        r'\s*<button type="submit">Redefinir senha</button>\s*'
        r'<a class="botao botao--secundario" href="/minha-unidade/">Cancelar</a>\s*'
        r'<p class="barra-acoes__nota">Nada é gravado se você cancelar\.</p>\s*',
        barra.group(1),
    )
    assert main.index('name="new_password2"') < main.index('<div class="barra-acoes">')
    assert 'class="resumo-erros"' not in main


def test_link_redefinir_senha_da_tabela_leva_a_tela(gestor_logado, bia):
    """GEST-17: o link da linha aponta para a rota da conta."""
    tela = _main(gestor_logado.get("/minha-unidade/").content.decode())
    assert f'<a class="botao botao--secundario" href="{_url(bia)}">Redefinir senha</a>' in tela


# --- GEST-37: o envio valido ---


def test_envio_valido_troca_a_senha_marca_provisoria_e_volta_com_o_alerta(gestor_logado, bia):
    """GEST-37."""
    resposta = gestor_logado.post(
        _url(bia), {"new_password1": SENHA_NOVA, "new_password2": SENHA_NOVA}
    )
    assertRedirects(resposta, "/minha-unidade/", fetch_redirect_response=False)
    bia.refresh_from_db()
    assert bia.check_password(SENHA_NOVA)
    assert bia.senha_provisoria is True
    lista = _main(gestor_logado.get("/minha-unidade/").content.decode())
    assert re.findall(r'<li class="alerta alerta--success">(.*?)</li>', lista) == [ALERTA]


def test_sessao_aberta_da_conta_vira_anonima(gestor_logado, bia):
    """GEST-39."""
    pessoa = Client()
    assert pessoa.login(username="bia", password=SENHA_ANTIGA)
    assert pessoa.get("/inovacoes/").status_code == 200
    gestor_logado.post(_url(bia), {"new_password1": SENHA_NOVA, "new_password2": SENHA_NOVA})
    assertRedirects(
        pessoa.get("/inovacoes/"), "/entrar/?next=/inovacoes/", fetch_redirect_response=False
    )


# --- GEST-38, GEST-68: o envio invalido ---


@pytest.mark.parametrize(
    ("dados", "campo", "rotulo", "mensagem"),
    [
        (
            {"new_password1": "12345678", "new_password2": "12345678"},
            "new_password1",
            "Nova senha provisória",
            "Esta senha é inteiramente numérica.",
        ),
        (
            {"new_password1": SENHA_NOVA, "new_password2": SENHA_NOVA + "x"},
            "new_password2",
            "Confirmação da nova senha provisória",
            "As duas senhas não são iguais.",
        ),
    ],
    ids=["validador", "confirmacao"],
)
def test_erro_no_campo_com_resumo_e_titulo_sem_trocar(
    gestor_logado, bia, dados, campo, rotulo, mensagem
):
    """GEST-38, GEST-68: erro no campo, resumo com o link, "Erro:" no titulo, foco no
    resumo; a senha nao muda."""
    resposta = gestor_logado.post(_url(bia), dados)
    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert re.search(r"<title>Erro: Redefinir senha · ", html)
    main = _main(html)
    erro = re.search(rf'<ul class="errorlist" id="id_{campo}_error">(.*?)</ul>', main, re.S)
    assert erro and mensagem in _texto(erro.group(1))
    resumo = re.search(
        r'<div class="resumo-erros" role="alert" tabindex="-1" autofocus>(.*?)</div>', main, re.S
    )
    assert resumo
    assert "<p>Não foi possível redefinir a senha. Corrija 1 campo(s):</p>" in resumo.group(1)
    links = re.findall(r'<a href="#([^"]+)">([^<]*)</a>', resumo.group(1))
    assert len(links) == 1
    assert links[0][0] == f"id_{campo}" and links[0][1].startswith(f"{rotulo}: ")
    assert mensagem in links[0][1]
    assert re.findall(r"<(\w+)[^>]*\bautofocus\b", main) == ["div"]
    assert _senha_mantida(bia)


# --- GEST-61, GEST-62: escopo ---


@pytest.mark.parametrize("metodo", ["get", "post"])
@pytest.mark.parametrize(
    "caso",
    ["outra_unidade", "sem_unidade", "proprio_gestor", "outro_gestor", "admin", "inexistente"],
)
def test_alvo_fora_do_escopo_responde_404_sem_trocar(
    gestor_logado, gestor, criar_conta, sede, norte, caso, metodo
):
    """GEST-61, GEST-62: a mesma 404 propria em GET e POST; a senha intacta."""
    contas = {
        "outra_unidade": lambda: criar_conta("davi", unidade=norte, password=SENHA_ANTIGA),
        "sem_unidade": lambda: criar_conta("elis", password=SENHA_ANTIGA),
        "proprio_gestor": lambda: gestor,
        "outro_gestor": lambda: criar_conta("fabi", GESTOR, sede, password=SENHA_ANTIGA),
        "admin": lambda: criar_conta(
            "hugo", Usuario.Perfil.ADMINISTRADOR, sede, password=SENHA_ANTIGA
        ),
    }
    alvo = contas[caso]() if caso in contas else None
    if caso == "proprio_gestor":
        gestor.set_password(SENHA_ANTIGA)
        gestor.save()
        gestor_logado.force_login(gestor)
    caminho = _url(alvo or 999999)
    dados = {"new_password1": SENHA_NOVA, "new_password2": SENHA_NOVA}
    resposta = (
        gestor_logado.post(caminho, dados) if metodo == "post" else gestor_logado.get(caminho)
    )
    assert resposta.status_code == 404
    assert "<p>Esta conta não existe ou não pertence à sua unidade.</p>" in _main(
        resposta.content.decode()
    )
    if alvo:
        assert _senha_mantida(alvo)


def test_csrf_invalido_responde_403_sem_trocar(gestor, bia):
    """GEST-67."""
    client = Client(enforce_csrf_checks=True)
    client.force_login(gestor)
    resposta = client.post(_url(bia), {"new_password1": SENHA_NOVA, "new_password2": SENHA_NOVA})
    assert resposta.status_code == 403
    assert _senha_mantida(bia)
