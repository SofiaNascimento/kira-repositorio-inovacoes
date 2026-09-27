from django.contrib.auth.forms import AdminUserCreationForm, AuthenticationForm, UserChangeForm

from contas.models import Usuario


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
