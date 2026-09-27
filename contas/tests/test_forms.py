"""Testes do LoginForm.

AUTH-03 e AUTH-04. Nenhum toca o banco: o AuthenticationForm so chama
authenticate() quando os dois campos chegam preenchidos, e a mensagem de
credencial invalida e lida direto do formulario.
"""

import pytest

from contas.forms import LoginForm


@pytest.mark.unit
def test_formulario_vazio_acusa_os_dois_campos():
    """AUTH-04: cada campo vazio recebe o proprio erro."""
    form = LoginForm(data={"username": "", "password": ""})
    assert form.is_valid() is False
    assert set(form.errors) == {"username", "password"}


@pytest.mark.unit
def test_senha_vazia_acusa_so_a_senha():
    """AUTH-04: o erro fica preso ao campo que faltou."""
    form = LoginForm(data={"username": "ana", "password": ""})
    assert form.is_valid() is False
    assert set(form.errors) == {"password"}


@pytest.mark.unit
def test_identificador_digitado_e_repopulado_apos_erro():
    """AUTH-04: o que foi digitado volta no campo re-renderizado."""
    form = LoginForm(data={"username": "ana@x.com", "password": ""})
    form.is_valid()
    assert 'value="ana@x.com"' in str(form["username"])


@pytest.mark.unit
def test_mensagem_de_credencial_invalida_e_unica():
    """AUTH-03: a mensagem nao cita campo nenhum."""
    erro = LoginForm().get_invalid_login_error()
    assert erro.messages == ["Usuário ou senha inválidos."]


@pytest.mark.unit
def test_campo_de_identificador_rotulado_e_acessivel():
    """RNF09 e RF01: o rotulo diz que o campo aceita os dois, com foco
    inicial e preenchimento automatico de username."""
    campo = LoginForm()["username"]
    assert campo.label == "Usuário ou e-mail"
    html = str(campo)
    assert "autofocus" in html
    assert 'autocomplete="username"' in html
