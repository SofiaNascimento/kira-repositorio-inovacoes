from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from contas.forms import UsuarioAlteracaoForm, UsuarioCriacaoForm
from contas.models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
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

    # RN11: so administrador atribui perfil ou poderes de superusuario.
    campos_so_do_administrador = ("perfil", "is_superuser")

    def get_readonly_fields(self, request, obj=None):
        # Readonly tira o campo do formulario e o mostra so como texto.
        campos = super().get_readonly_fields(request, obj)
        if request.user.is_administrador:
            return campos
        return (*campos, *self.campos_so_do_administrador)

    def has_change_permission(self, request, obj=None):
        # O perfil, e nao as permissoes de modelo, decide quem administra
        # contas (AUTH-22): um ADMINISTRADOR promovido nao e superusuario.
        if request.user.is_administrador:
            return True
        if obj is not None and obj.pk != request.user.pk:
            return False
        return super().has_change_permission(request, obj)
