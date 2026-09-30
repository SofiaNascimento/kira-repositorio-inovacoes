from django.contrib import admin

from contas.admin import AcessoSomenteAdministradorMixin
from inovacoes.models import Categoria, Unidade

# Inovacao fica fora do admin de proposito: o cadastro por aqui contornaria a
# autoria (RN08) e, na F4, a regra de quem edita (RN05).


@admin.register(Unidade)
class UnidadeAdmin(AcessoSomenteAdministradorMixin, admin.ModelAdmin):
    """Lista controlada de unidades (RN07), mantida so pelo ADMINISTRADOR.

    Excluir um item em uso e recusado pela propria tela de exclusao do admin,
    que lista as inovacoes que o protegem (on_delete=PROTECT, INOV-19).
    """

    list_display = ("nome",)
    search_fields = ("nome",)


@admin.register(Categoria)
class CategoriaAdmin(AcessoSomenteAdministradorMixin, admin.ModelAdmin):
    """Lista controlada de categorias (RN07), mantida so pelo ADMINISTRADOR."""

    list_display = ("nome",)
    search_fields = ("nome",)
