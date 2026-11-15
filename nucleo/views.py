from django.conf import settings
from django.contrib.auth.decorators import login_not_required
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

COOKIE_CONTRASTE = "kira_contraste"
UM_ANO = 365 * 24 * 60 * 60


# AD-006: publica, porque a barra de acessibilidade esta tambem no login (AD-014).
@login_not_required
@require_POST
def definir_contraste(request):
    """Grava ou apaga a preferencia de alto contraste e volta a pagina (RED-24, RED-25).

    O valor e explicito (alto ou normal), nao uma alternancia: o mesmo POST duas
    vezes da a mesma resposta (RED-42).
    """
    contraste = request.POST.get("contraste")
    if contraste not in {"alto", "normal"}:
        # RED-38: nada muda.
        return HttpResponseBadRequest("Valor de contraste invalido.")
    voltar_para = request.POST.get("voltar_para", "")
    # RED-37: so caminhos locais; o resto volta a raiz.
    if not url_has_allowed_host_and_scheme(
        voltar_para, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        voltar_para = "/"
    resposta = HttpResponseRedirect(voltar_para)
    if contraste == "alto":
        resposta.set_cookie(
            COOKIE_CONTRASTE,
            "alto",
            max_age=UM_ANO,
            httponly=True,
            samesite="Lax",
            # Mesma regra do cookie de sessao (settings.SESSION_COOKIE_SECURE).
            secure=not settings.DEBUG,
        )
    else:
        resposta.delete_cookie(COOKIE_CONTRASTE, samesite="Lax")
    return resposta
