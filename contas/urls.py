from django.urls import path

from contas.views import LoginUsuarioView, LogoutUsuarioView

app_name = "contas"

urlpatterns = [
    path("entrar/", LoginUsuarioView.as_view(), name="entrar"),
    path("sair/", LogoutUsuarioView.as_view(), name="sair"),
]
