"""Testes dos formularios da area do gestor (gestao-por-unidade, T10 e T12).

Derivados das ACs GEST-20, GEST-24 a GEST-27 e GEST-38
(.specs/features/gestao-por-unidade/spec.md): cada mensagem no campo certo, uma
vez so, sem erro geral.
"""

import pytest
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError

from contas.forms import ContaDaUnidadeForm, SenhaProvisoriaForm
from contas.models import Usuario
from contas.tests.conftest import SENHA_NOVA


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


def _mensagens_do_validador(senha, **atributos):
    try:
        password_validation.validate_password(senha, Usuario(**atributos))
    except ValidationError as erro:
        return erro.messages
    raise AssertionError("a senha deveria ser recusada")


def test_campos_sao_os_seis_da_spec_todos_obrigatorios(db):
    """GEST-20: rotulos e obrigatoriedade; nenhum campo de perfil ou unidade."""
    form = ContaDaUnidadeForm()
    assert [(nome, campo.label, campo.required) for nome, campo in form.fields.items()] == [
        ("username", "Usuário", True),
        ("first_name", "Nome", True),
        ("last_name", "Sobrenome", True),
        ("email", "E-mail", True),
        ("password1", "Senha provisória", True),
        ("password2", "Confirmação da senha provisória", True),
    ]


def test_envio_valido_passa(db):
    assert ContaDaUnidadeForm(data=_dados()).is_valid()


@pytest.mark.parametrize("email", ["ana@x.com", "ANA@X.COM"], ids=["igual", "outra_caixa"])
def test_email_existente_acusa_no_campo_email(criar_conta, email):
    """GEST-24: sem diferenciar maiusculas; so no campo E-mail, uma vez."""
    criar_conta("ana")
    form = ContaDaUnidadeForm(data=_dados(email=email))
    assert not form.is_valid()
    assert form.errors == {"email": ["Já existe uma conta com este e-mail."]}


@pytest.mark.parametrize("username", ["ana", "ANA"], ids=["igual", "outra_caixa"])
def test_usuario_existente_acusa_no_campo_usuario(criar_conta, username):
    """GEST-25: so no campo Usuario, uma vez."""
    criar_conta("ana", email="outro@x.com")
    form = ContaDaUnidadeForm(data=_dados(username=username))
    assert not form.is_valid()
    assert form.errors == {"username": ["Já existe uma conta com este usuário."]}


@pytest.mark.parametrize("senha", ["12345678", "curta", "pedro12x"])
def test_senha_recusada_pelo_validador_acusa_no_campo_senha_provisoria(db, senha):
    """GEST-26: a mensagem do validador, no campo Senha provisoria."""
    form = ContaDaUnidadeForm(data=_dados(password1=senha, password2=senha))
    assert not form.is_valid()
    esperado = _mensagens_do_validador(
        senha, username="pedro", first_name="Pedro", last_name="Alves", email="pedro@x.com"
    )
    assert form.errors == {"password1": esperado}


def test_confirmacao_diferente_acusa_no_campo_de_confirmacao(db):
    """GEST-27."""
    form = ContaDaUnidadeForm(data=_dados(password2=SENHA_NOVA + "x"))
    assert not form.is_valid()
    assert form.errors == {"password2": ["As duas senhas não são iguais."]}


# --- SenhaProvisoriaForm (T12) ---


def _senha(conta, **troca):
    dados = {"new_password1": SENHA_NOVA, "new_password2": SENHA_NOVA}
    dados.update(troca)
    return SenhaProvisoriaForm(conta, data=dados)


def test_redefinir_tem_os_dois_campos_obrigatorios(criar_conta):
    """GEST-37: os rotulos da senha provisoria nova."""
    form = SenhaProvisoriaForm(criar_conta("bia"))
    assert [(nome, campo.label, campo.required) for nome, campo in form.fields.items()] == [
        ("new_password1", "Nova senha provisória", True),
        ("new_password2", "Confirmação da nova senha provisória", True),
    ]


def test_redefinir_grava_a_senha_e_a_marca_provisoria(criar_conta):
    """GEST-37."""
    conta = criar_conta("bia", password="antiga-Senha-99")
    form = _senha(conta)
    assert form.is_valid()
    form.save()
    conta.refresh_from_db()
    assert conta.check_password(SENHA_NOVA)
    assert conta.senha_provisoria is True


def test_redefinir_com_senha_recusada_acusa_no_campo_da_senha(criar_conta):
    """GEST-38: a mensagem do validador, no campo da senha nova, como na criacao."""
    conta = criar_conta("bia")
    form = _senha(conta, new_password1="12345678", new_password2="12345678")
    assert not form.is_valid()
    assert form.errors == {"new_password1": _mensagens_do_validador("12345678", username="bia")}


def test_redefinir_com_confirmacao_diferente_acusa_na_confirmacao(criar_conta):
    """GEST-38."""
    form = _senha(criar_conta("bia"), new_password2=SENHA_NOVA + "x")
    assert not form.is_valid()
    assert form.errors == {"new_password2": ["As duas senhas não são iguais."]}
