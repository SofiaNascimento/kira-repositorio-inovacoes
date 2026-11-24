from django.urls import path

from contas.views_gestao import (
    CriarContaView,
    MinhaUnidadeView,
    RedefinirSenhaView,
    SituacaoDaContaView,
)

# Namespace proprio: o PAGINA_ATUAL marca a secao inteira por ele (AD-015).
app_name = "gestao"

urlpatterns = [
    path("", MinhaUnidadeView.as_view(), name="painel"),
    path("contas/nova/", CriarContaView.as_view(), name="criar_conta"),
    path("contas/<int:pk>/situacao/", SituacaoDaContaView.as_view(), name="situacao"),
    path("contas/<int:pk>/senha/", RedefinirSenhaView.as_view(), name="redefinir_senha"),
]
