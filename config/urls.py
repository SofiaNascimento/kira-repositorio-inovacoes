"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path

# ADM-05: o admin se identifica como KIRA; "Ver o site" leva a lista, a pagina inicial real
# (a raiz so redireciona para ela, CONS-09).
admin.site.site_header = "KIRA — Administração"
admin.site.site_title = "KIRA"
admin.site.index_title = "Administração do KIRA"
admin.site.site_url = "/inovacoes/"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("contas.urls")),
    path("inovacoes/", include("inovacoes.urls")),
    path("indicadores/", include("indicadores.urls")),
    # gestao-por-unidade: a area do gestor (namespace "gestao").
    path("minha-unidade/", include("contas.urls_gestao")),
    path("", include("nucleo.urls")),
]
