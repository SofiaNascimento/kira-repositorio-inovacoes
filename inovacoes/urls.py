from django.urls import path

from inovacoes.views import InovacaoCreateView

app_name = "inovacoes"

urlpatterns = [
    path("nova/", InovacaoCreateView.as_view(), name="nova"),
]
