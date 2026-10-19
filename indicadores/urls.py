from django.urls import path

from indicadores.views import PainelView

app_name = "indicadores"

urlpatterns = [
    path("", PainelView.as_view(), name="painel"),
]
