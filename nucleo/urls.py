from django.urls import path
from django.views.generic import RedirectView

app_name = "nucleo"

# CONS-09: a raiz leva a listagem; o nome "home" segue sendo o destino do login.
urlpatterns = [
    path(
        "",
        RedirectView.as_view(pattern_name="inovacoes:lista", permanent=False),
        name="home",
    ),
]
