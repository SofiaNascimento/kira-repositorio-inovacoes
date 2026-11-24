from django import forms
from django.contrib.auth.forms import (
    AdminUserCreationForm,
    AuthenticationForm,
    BaseUserCreationForm,
    PasswordChangeForm,
    SetPasswordForm,
    UserChangeForm,
)
from django.core.exceptions import ValidationError

from contas.models import PerfilUsuario, Usuario
from nucleo.formularios import FormularioV2Mixin

SENHAS_DIFERENTES = "As duas senhas não são iguais."


class LoginForm(AuthenticationForm):
    """Formulario de login do projeto (AUTH-03, AUTH-04).

    Campos obrigatorios e repopulacao do identificador ja vem do
    AuthenticationForm. Aqui mudam so o rotulo e a mensagem de credencial
    invalida, que nao pode indicar qual campo falhou.
    """

    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "Usuário ou senha inválidos.",
    }

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields["username"].label = "Usuário ou e-mail"


class UsuarioCriacaoForm(AdminUserCreationForm):
    """Criacao de conta no admin.

    Os formularios do Django apontam para auth.User, que o AD-005 substituiu.
    O e-mail entra porque e obrigatorio e unico: sem ele, a segunda conta
    criada colidiria no e-mail vazio.
    """

    class Meta(AdminUserCreationForm.Meta):
        model = Usuario
        fields = ("username", "email")


class UsuarioAlteracaoForm(UserChangeForm):
    """Edicao de conta no admin; a senha segue como resumo mascarado do hash."""

    class Meta(UserChangeForm.Meta):
        model = Usuario

    def clean(self):
        """GEST-05: gestor sem unidade e erro no campo Unidade.

        Com o campo em erro, o ModelForm tira a unidade da validacao do modelo,
        e a CHECK usuario_gestor_tem_unidade nao repete a mensagem como erro
        geral; ela fica como rede do banco (GEST-03).
        """
        dados = super().clean()
        if dados.get("perfil") == PerfilUsuario.GESTOR_DE_UNIDADE and not dados.get("unidade"):
            self.add_error("unidade", "Gestor de unidade precisa de uma unidade.")
        return dados


class ContaDaUnidadeForm(FormularioV2Mixin, BaseUserCreationForm):
    """Criar conta na unidade (GEST-20, GEST-24 a GEST-28).

    So os seis campos: perfil, unidade e as bandeiras saem da view, nunca do
    POST (GEST-23). Usuario e e-mail duplicados acusam no proprio campo, sem
    diferenciar caixa; com o campo em erro, a validacao do modelo nao repete a
    mensagem.
    """

    error_messages = {"password_mismatch": SENHAS_DIFERENTES}

    class Meta:
        model = Usuario
        fields = ("username", "first_name", "last_name", "email")
        labels = {
            "username": "Usuário",
            "first_name": "Nome",
            "last_name": "Sobrenome",
            "email": "E-mail",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for nome in ("first_name", "last_name"):
            self.fields[nome].required = True
        self.fields["password1"].label = "Senha provisória"
        self.fields["password2"].label = "Confirmação da senha provisória"

    def clean_username(self):
        username = self.cleaned_data["username"]
        if Usuario.objects.filter(username__iexact=username).exists():
            raise ValidationError("Já existe uma conta com este usuário.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if Usuario.objects.filter(email__iexact=email).exists():
            raise ValidationError("Já existe uma conta com este e-mail.")
        return email

    def _post_clean(self):
        # GEST-26: a mensagem do validador vai no campo Senha provisória; o
        # BaseUserCreationForm a poria na confirmacao.
        forms.ModelForm._post_clean(self)
        self.validate_password_for_user(self.instance, password_field_name="password1")

    def full_clean(self):
        super().full_clean()
        if self._errors:
            # §6 v2: com erro, o foco vai ao resumo, nao ao primeiro campo.
            self.fields["username"].widget.attrs.pop("autofocus", None)


class SenhaProvisoriaForm(FormularioV2Mixin, SetPasswordForm):
    """Redefinir a senha de uma conta da unidade (GEST-37, GEST-38).

    A senha nova volta a ser provisoria: a pessoa troca no proximo acesso.
    """

    error_messages = {"password_mismatch": SENHAS_DIFERENTES}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].label = "Nova senha provisória"
        self.fields["new_password2"].label = "Confirmação da nova senha provisória"

    def clean(self):
        # GEST-38: como na criacao, o validador acusa no campo da senha, nao na
        # confirmacao (o SetPasswordForm usaria o new_password2).
        self.validate_passwords("new_password1", "new_password2")
        self.validate_password_for_user(self.user, "new_password1")
        return forms.Form.clean(self)

    def save(self, commit=True):
        self.user.senha_provisoria = True
        return super().save(commit=commit)


class TrocarSenhaForm(FormularioV2Mixin, PasswordChangeForm):
    """Trocar a propria senha (GEST-41, GEST-43 a GEST-47).

    A senha nova e definitiva: o save() desliga a senha provisoria.
    """

    error_messages = {
        **PasswordChangeForm.error_messages,
        "password_incorrect": "Senha atual incorreta.",
        "password_mismatch": SENHAS_DIFERENTES,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].label = "Senha atual"
        self.fields["new_password1"].label = "Nova senha"
        self.fields["new_password2"].label = "Confirmação da nova senha"

    def clean_new_password1(self):
        senha = self.cleaned_data["new_password1"]
        if self.user.check_password(senha):
            raise ValidationError("A nova senha precisa ser diferente da atual.")
        return senha

    def clean(self):
        # GEST-46: como na criacao, o validador acusa no campo da nova senha, nao na
        # confirmacao (o SetPasswordForm usaria o new_password2).
        self.validate_passwords("new_password1", "new_password2")
        self.validate_password_for_user(self.user, "new_password1")
        return forms.Form.clean(self)

    def full_clean(self):
        super().full_clean()
        if self._errors:
            # §6 v2: com erro, o foco vai ao resumo, nao ao campo Senha atual.
            self.fields["old_password"].widget.attrs.pop("autofocus", None)

    def save(self, commit=True):
        self.user.senha_provisoria = False
        return super().save(commit=commit)
