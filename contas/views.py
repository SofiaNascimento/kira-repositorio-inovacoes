from django.contrib.auth.views import LoginView

from contas.forms import LoginForm


class LoginUsuarioView(LoginView):
    """Tela de login (AUTH-01 a AUTH-05, AUTH-12).

    O LoginView ja trata o next com validacao de host e chama login(), que
    troca a chave de sessao. Aqui entram so o formulario e o redirecionamento
    de quem ja esta autenticado.
    """

    template_name = "contas/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True
