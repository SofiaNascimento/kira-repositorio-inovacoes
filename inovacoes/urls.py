from django.urls import path

from inovacoes.views import (
    InovacaoCreateView,
    InovacaoDeleteView,
    InovacaoDetailView,
    InovacaoListView,
    InovacaoUpdateView,
)

app_name = "inovacoes"

urlpatterns = [
    path("", InovacaoListView.as_view(), name="lista"),
    path("nova/", InovacaoCreateView.as_view(), name="nova"),
    path("<int:pk>/", InovacaoDetailView.as_view(), name="detalhe"),
    path("<int:pk>/editar/", InovacaoUpdateView.as_view(), name="editar"),
    path("<int:pk>/excluir/", InovacaoDeleteView.as_view(), name="excluir"),
]
