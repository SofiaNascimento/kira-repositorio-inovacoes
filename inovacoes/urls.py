from django.urls import path

from inovacoes.views import InovacaoCreateView, InovacaoDetailView

app_name = "inovacoes"

urlpatterns = [
    path("nova/", InovacaoCreateView.as_view(), name="nova"),
    path("<int:pk>/", InovacaoDetailView.as_view(), name="detalhe"),
]
