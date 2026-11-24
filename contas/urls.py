from django.urls import path

from contas.views import LoginUsuarioView, LogoutUsuarioView, TrocarSenhaView

app_name = "contas"

urlpatterns = [
    path("entrar/", LoginUsuarioView.as_view(), name="entrar"),
    path("sair/", LogoutUsuarioView.as_view(), name="sair"),
    # gestao-por-unidade (GEST-41): a troca da propria senha, obrigatoria com a provisoria.
    path("conta/senha/", TrocarSenhaView.as_view(), name="trocar_senha"),
]
