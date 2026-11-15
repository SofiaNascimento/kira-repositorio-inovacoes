from django.urls import path
from django.views.generic import RedirectView

from nucleo import views

app_name = "nucleo"

# CONS-09: a raiz leva a listagem; o nome "home" segue sendo o destino do login.
urlpatterns = [
    path(
        "",
        RedirectView.as_view(pattern_name="inovacoes:lista", permanent=False),
        name="home",
    ),
    # RED-33: pagina publica de acessibilidade (eMAG).
    path("acessibilidade/", views.AcessibilidadeView.as_view(), name="acessibilidade"),
    # RED-35: pagina publica de ajuda.
    path("ajuda/", views.AjudaView.as_view(), name="ajuda"),
    # RED-24, RED-25: alto contraste por POST, sem JavaScript (AD-014).
    path("acessibilidade/contraste/", views.definir_contraste, name="contraste"),
]
