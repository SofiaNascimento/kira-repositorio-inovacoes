"""Troca obrigatoria da senha provisoria (AD-017, GEST-40, GEST-66)."""

from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

# As unicas rotas internas abertas durante a troca: a propria troca e o sair.
ROTAS_LIBERADAS = {"contas:trocar_senha", "contas:sair"}


class SenhaProvisoriaMiddleware(MiddlewareMixin):
    """Com a senha provisoria, toda rota interna vai para /conta/senha/.

    Fica logo depois do LoginRequiredMiddleware: o anonimo ja foi tratado la. No
    process_view, antes de qualquer view, vale para "Minha unidade" e para o
    admin antes da checagem de papel (GEST-66). As views publicas seguem, pela
    mesma marca do @login_not_required que o LoginRequiredMiddleware le. So le o
    request.user, ja carregado: nenhuma consulta nova.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        # A view publica primeiro: nela o request.user pode nem ter sido carregado.
        if getattr(view_func, "login_required", True) is False:
            return None
        usuario = request.user
        if not usuario.is_authenticated or not usuario.senha_provisoria:
            return None
        if request.resolver_match.view_name in ROTAS_LIBERADAS:
            return None
        return redirect("contas:trocar_senha")
