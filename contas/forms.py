from django.contrib.auth.forms import AuthenticationForm


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
