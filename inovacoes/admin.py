from django.contrib import admin

from contas.admin import AcessoSomenteAdministradorMixin
from inovacoes.models import Categoria, Reaproveitamento, Unidade

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


@admin.register(Reaproveitamento)
class ReaproveitamentoAdmin(AcessoSomenteAdministradorMixin, admin.ModelAdmin):
    """Correcao de sinalizacoes erradas pelo ADMINISTRADOR (REAP-26).

    So listar e excluir: incluir ou alterar por aqui contornaria a RN09, que so
    vale em Inovacao.registrar_reaproveitamento (AD-012).
    """

    list_display = ("inovacao", "unidade", "registrado_por", "data")
    list_select_related = True

    # REAP-27: ninguem inclui nem altera, nem o ADMINISTRADOR. A tela do
    # registro abre so para leitura, e um POST nela recebe 403.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
