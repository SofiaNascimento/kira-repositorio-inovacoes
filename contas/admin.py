from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from contas.forms import UsuarioAlteracaoForm, UsuarioCriacaoForm
from contas.models import Usuario


class AcessoSomenteAdministradorMixin:
    """Abre o ModelAdmin so para o perfil ADMINISTRADOR (AD-007).

    Todo ModelAdmin do projeto herda este mixin antes do ModelAdmin, para que
    ele venca na MRO.
    """

    # AUTH-22 e RN11: o perfil, e nao as permissoes de modelo do Django,
    # decide quem abre as telas do admin. Um ADMINISTRADOR promovido nao e
    # superusuario; um USUARIO com is_staff recebe 403 em todas elas, e um
    # POST de alteracao nem chega ao formulario (AUTH-21).
    def _is_administrador(self, request):
        # O login do admin monta a lista de apps com o AnonymousUser, que nao
        # tem perfil: anonimo nunca e administrador.
        return request.user.is_authenticated and request.user.is_administrador

    def has_module_permission(self, request):
        return self._is_administrador(request)

    def has_view_permission(self, request, obj=None):
        return self._is_administrador(request)

    def has_add_permission(self, request):
        return self._is_administrador(request)

    def has_change_permission(self, request, obj=None):
        return self._is_administrador(request)

    def has_delete_permission(self, request, obj=None):
        return self._is_administrador(request)


@admin.register(Usuario)
class UsuarioAdmin(AcessoSomenteAdministradorMixin, UserAdmin):
    """Unica superficie de criacao de contas e de troca de perfil no MVP (RN11).

    A senha continua tratada pelo UserAdmin: resumo mascarado do hash na
    edicao, troca por formulario proprio (AUTH-08).
    """

    form = UsuarioAlteracaoForm
    add_form = UsuarioCriacaoForm

    fieldsets = (
        UserAdmin.fieldsets[:2] + (("Perfil", {"fields": ("perfil",)}),) + UserAdmin.fieldsets[2:]
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "usable_password", "password1", "password2"),
            },
        ),
    )
    list_display = ("username", "email", "perfil", "is_active")
    list_filter = ("perfil", "is_active", "is_staff", "is_superuser")
