from django.views.generic import TemplateView


# PROVISORIA: andaime da F1. Destino padrao do login e primeira tela
# protegida enquanto a F3 nao existe; a listagem de inovacoes a substitui.
class HomeInternaView(TemplateView):
    template_name = "nucleo/home.html"
