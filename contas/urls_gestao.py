from django.urls import path

from contas.views_gestao import MinhaUnidadeView

# Namespace proprio: o PAGINA_ATUAL marca a secao inteira por ele (AD-015).
app_name = "gestao"

urlpatterns = [
    path("", MinhaUnidadeView.as_view(), name="painel"),
]
