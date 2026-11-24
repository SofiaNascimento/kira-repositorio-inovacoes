"""Testes e2e de "Criar conta" na area do gestor (gestao-por-unidade, T10).

Derivados das ACs GEST-20 a GEST-29, GEST-68 e GEST-69
(.specs/features/gestao-por-unidade/spec.md). O exibido e lido do DOM parseado
(L-028, L-030).
"""

import re

import pytest
from django.test import Client
from pytest_django.asserts import assertRedirects

from contas.models import Usuario
from contas.tests.conftest import SENHA_NOVA
from inovacoes.tests.visibilidade import exibido
from nucleo.tests.test_casca import _menu_da_tela, _trilha

URL = "/minha-unidade/contas/nova/"
ALERTA = (
    "Conta “pedro” criada. Informe a senha provisória à pessoa: ela vai trocá-la no "
    "primeiro acesso."
)
CAMPOS = ["username", "first_name", "last_name", "email", "password1", "password2"]
ROTULOS = ["Usuário", "Nome", "Sobrenome", "E-mail", "Senha provisória"]
ROTULOS.append("Confirmação da senha provisória")


def _dados(**troca):
    dados = {
        "username": "pedro",
        "first_name": "Pedro",
        "last_name": "Alves",
        "email": "pedro@x.com",
        "password1": SENHA_NOVA,
        "password2": SENHA_NOVA,
    }
    dados.update(troca)
    return dados


def _tela(html):
    return exibido(html, rigoroso=True)


def _main(html):
    tela = _tela(html)
    return tela[tela.index('<main id="conteudo">') : tela.index("</main>")]


def _texto(trecho):
    return " ".join(re.sub(r"<[^>]+>", " ", trecho).split())


def _controles(main):
    """name de cada input exibido do formulario, sem o csrf."""
    return [
        nome
        for nome in re.findall(r'<input[^>]*name="([^"]+)"', main)
        if nome != "csrfmiddlewaretoken"
    ]


def _envio_invalido(client, **troca):
    resposta = client.post(URL, _dados(**troca))
    assert resposta.status_code == 200
    return resposta.content.decode()


# --- GEST-20: a tela ---


def test_formulario_tem_os_seis_campos_obrigatorios_sem_perfil_nem_unidade(gestor_logado):
    """GEST-20: Usuario, Nome, Sobrenome, E-mail e as duas senhas, todos obrigatorios."""
    main = _main(gestor_logado.get(URL).content.decode())
    assert _controles(main) == CAMPOS
    rotulos = [_texto(r) for r in re.findall(r"<label[^>]*>(.*?)</label>", main, re.S)]
    assert rotulos == [f"{rotulo} (obrigatório)" for rotulo in ROTULOS]
    assert "<select" not in main
    assert "perfil" not in main.lower() and 'name="unidade"' not in main


def test_campos_vem_em_dois_grupos(gestor_logado):
    """Design (Telas): fieldset "Identificação" e fieldset "Senha provisória"."""
    main = _main(gestor_logado.get(URL).content.decode())
    grupos = re.findall(r'<fieldset class="grupo">(.*?)</fieldset>', main, re.S)
    assert [_texto(re.search(r"<legend>(.*?)</legend>", g, re.S).group(1)) for g in grupos] == [
        "Identificação",
        "Senha provisória",
    ]
    assert [_controles(g) for g in grupos] == [CAMPOS[:4], CAMPOS[4:]]


def test_cabecalho_trilha_e_menu(gestor_logado):
    """Design (Telas), GEST-11: h1, descricao, trilha "Minha unidade › Criar conta" e o
    item do menu como secao."""
    html = gestor_logado.get(URL).content.decode()
    assert re.search(
        r"<h1>Criar conta</h1>\s*<p>A conta nasce como Usuário da unidade Sede\.</p>", _main(html)
    )
    assert _trilha(html) == [
        ("Minha unidade", "/minha-unidade/", None),
        ("Criar conta", None, "page"),
    ]
    menu = {texto: corrente for _, corrente, texto in _menu_da_tela(html) if corrente}
    assert menu == {"Minha unidade": "true"}


def test_barra_de_acoes_tem_criar_cancelar_e_a_nota(gestor_logado):
    """GEST-29, GEST-69: botao de envio, Cancelar -> /minha-unidade/ e a nota."""
    main = _main(gestor_logado.get(URL).content.decode())
    barra = re.search(r'<div class="barra-acoes">(.*?)</div>', main, re.S)
    assert barra
    assert re.fullmatch(
        r'\s*<button type="submit">Criar conta</button>\s*'
        r'<a class="botao botao--secundario" href="/minha-unidade/">Cancelar</a>\s*'
        r'<p class="barra-acoes__nota">Nada é gravado se você cancelar\.</p>\s*',
        barra.group(1),
    )
    assert main.index('<div class="barra-acoes">') > main.index('name="password2"')
    assert main.index("</form>") > main.index('<div class="barra-acoes">')


def test_sem_erro_nao_ha_resumo_nem_erro_no_titulo(gestor_logado):
    """GEST-68: o resumo e o "Erro:" so com erro."""
    html = gestor_logado.get(URL).content.decode()
    assert 'class="resumo-erros"' not in html
    assert 'role="alert"' not in html
    assert re.search(r"<title>Criar conta · ", html)


def test_link_criar_conta_da_lista_leva_a_tela(gestor_logado):
    """GEST-19: o href da acao principal e a rota desta tela."""
    html = gestor_logado.get("/minha-unidade/").content.decode()
    assert f'<a class="botao" href="{URL}">Criar conta</a>' in _main(html)
    assert gestor_logado.get(URL).status_code == 200


# --- GEST-21 a GEST-23: o envio valido ---


def test_envio_valido_cria_usuario_da_unidade_com_senha_provisoria(gestor_logado, gestor):
    """GEST-21, GEST-22: USUARIO da unidade do gestor, ativa, senha provisoria, senha em
    hash; volta a /minha-unidade/ com o alerta exato."""
    resposta = gestor_logado.post(URL, _dados())
    assertRedirects(resposta, "/minha-unidade/", fetch_redirect_response=False)
    conta = Usuario.objects.get(username="pedro")
    assert (conta.perfil, conta.unidade_id, conta.is_active, conta.senha_provisoria) == (
        Usuario.Perfil.USUARIO,
        gestor.unidade_id,
        True,
        True,
    )
    assert (conta.first_name, conta.last_name, conta.email) == ("Pedro", "Alves", "pedro@x.com")
    assert conta.password != SENHA_NOVA and conta.check_password(SENHA_NOVA)
    lista = gestor_logado.get("/minha-unidade/").content.decode()
    assert f'<li class="alerta alerta--success">{ALERTA}</li>' in _main(lista)


def test_campos_de_papel_no_post_sao_ignorados(gestor_logado, gestor, norte):
    """GEST-23: perfil, unidade, is_staff e is_superuser forjados nao chegam a conta."""
    forjado = _dados(
        perfil=Usuario.Perfil.ADMINISTRADOR,
        unidade=norte.pk,
        is_staff="on",
        is_superuser="on",
        senha_provisoria="",
        is_active="",
    )
    assertRedirects(
        gestor_logado.post(URL, forjado), "/minha-unidade/", fetch_redirect_response=False
    )
    conta = Usuario.objects.get(username="pedro")
    assert (
        conta.perfil,
        conta.unidade_id,
        conta.is_staff,
        conta.is_superuser,
        conta.is_active,
        conta.senha_provisoria,
    ) == (Usuario.Perfil.USUARIO, gestor.unidade_id, False, False, True, True)


# --- GEST-24 a GEST-28, GEST-68: o envio invalido ---


@pytest.mark.parametrize(
    ("troca", "campo", "mensagem"),
    [
        ({"email": "ANA@x.com"}, "email", "Já existe uma conta com este e-mail."),
        ({"username": "Ana"}, "username", "Já existe uma conta com este usuário."),
        (
            {"password2": SENHA_NOVA + "x"},
            "password2",
            "As duas senhas não são iguais.",
        ),
    ],
    ids=["email", "usuario", "confirmacao"],
)
def test_erro_aparece_no_campo_e_no_resumo_uma_vez_cada(
    gestor_logado, criar_conta, troca, campo, mensagem
):
    """GEST-24, GEST-25, GEST-27: a mensagem no campo certo e no resumo, e so ali; nada criado."""
    criar_conta("ana", email="ana@x.com")
    antes = Usuario.objects.count()
    main = _main(_envio_invalido(gestor_logado, **troca))
    assert Usuario.objects.count() == antes
    erro = re.search(rf'<ul class="errorlist" id="id_{campo}_error">(.*?)</ul>', main, re.S)
    assert erro and _texto(erro.group(1)) == mensagem
    resumo = re.search(r'<div class="resumo-erros"[^>]*>(.*?)</div>', main, re.S).group(1)
    assert re.findall(r"<li>(.*?)</li>", resumo, re.S) == [
        f'<a href="#id_{campo}">{ROTULOS[CAMPOS.index(campo)]}: {mensagem}</a>'
    ]
    assert main.count(mensagem) == 2


def test_senha_recusada_pelo_validador_acusa_no_campo_senha_provisoria(gestor_logado):
    """GEST-26: a mensagem do validador no campo Senha provisoria; nada criado."""
    main = _main(_envio_invalido(gestor_logado, password1="12345678", password2="12345678"))
    assert not Usuario.objects.filter(username="pedro").exists()
    erro = re.search(r'<ul class="errorlist" id="id_password1_error">(.*?)</ul>', main, re.S)
    assert erro and "Esta senha é inteiramente numérica." in _texto(erro.group(1))
    assert 'id="id_password2_error"' not in main


def test_envio_vazio_resume_os_seis_campos_com_erro_no_titulo(gestor_logado):
    """GEST-68 (teste independente): resumo com os seis campos, na ordem, e "Erro:"."""
    resposta = gestor_logado.post(URL, {})
    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert re.search(r"<title>Erro: Criar conta · ", html)
    main = _main(html)
    resumo = re.search(
        r'<div class="resumo-erros" role="alert" tabindex="-1" autofocus>(.*?)</div>', main, re.S
    )
    assert resumo
    assert "<p>Não foi possível criar a conta. Corrija 6 campo(s):</p>" in resumo.group(1)
    links = re.findall(r'<a href="#([^"]+)">([^:<]+):', resumo.group(1))
    assert links == [(f"id_{campo}", rotulo) for campo, rotulo in zip(CAMPOS, ROTULOS, strict=True)]
    assert main.index("resumo-erros") < main.index("<form")


def test_com_erro_o_foco_vai_so_ao_resumo(gestor_logado):
    """§6 v2: o resumo recebe o foco ao carregar; o campo Usuario perde o autofocus."""
    sem_erro = gestor_logado.get(URL).content.decode()
    assert re.search(r'<input[^>]*name="username"[^>]*autofocus', sem_erro)
    com_erro = _envio_invalido(gestor_logado, email="")
    assert re.findall(r"<(\w+)[^>]*\bautofocus\b", _main(com_erro)) == ["div"]


def test_envio_invalido_devolve_os_dados_e_esvazia_as_senhas(gestor_logado):
    """GEST-28 (RF13)."""
    main = _main(_envio_invalido(gestor_logado, password2="outra-senha-qualquer"))
    valores = dict(re.findall(r'<input type="\w+" name="(\w+)"(?:[^>]*?value="([^"]*)")?', main))
    assert {nome: valores.get(nome, "") for nome in CAMPOS} == {
        "username": "pedro",
        "first_name": "Pedro",
        "last_name": "Alves",
        "email": "pedro@x.com",
        "password1": "",
        "password2": "",
    }


def test_csrf_invalido_responde_403_sem_criar(gestor):
    """GEST-67: POST sem token valido nao cria nada."""
    client = Client(enforce_csrf_checks=True)
    client.force_login(gestor)
    resposta = client.post(URL, _dados())
    assert resposta.status_code == 403
    assert not Usuario.objects.filter(username="pedro").exists()
