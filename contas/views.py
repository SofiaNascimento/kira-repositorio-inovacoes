from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView

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


class LogoutUsuarioView(LogoutView):
    """Encerra a sessao no servidor e volta ao login (AUTH-13, AUTH-14).

    O LogoutView so aceita POST e o logout() descarta a sessao no banco,
    entao o cookie antigo deixa de valer.
    """

    next_page = settings.LOGIN_URL

    def post(self, request, *args, **kwargs):
        resposta = super().post(request, *args, **kwargs)
        messages.success(request, "Sessão encerrada.")
        return resposta
