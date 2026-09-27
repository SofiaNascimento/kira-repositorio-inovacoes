from django.urls import path

from contas.views import LoginUsuarioView

app_name = "contas"

urlpatterns = [
    path("entrar/", LoginUsuarioView.as_view(), name="entrar"),
]
