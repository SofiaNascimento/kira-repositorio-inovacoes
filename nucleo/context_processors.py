"""Estado da casca de cada pagina (fundacao-do-redesign, AD-014, AD-015)."""

# RED-17: o destino exato de cada item do menu. Tabela unica: rota nova fora do
# namespace "inovacoes" precisa entrar aqui para marcar o menu (AD-015).
PAGINA_ATUAL = {
    ("inovacoes", "lista"): ("inovacoes", "page"),
    ("inovacoes", "nova"): ("nova", "page"),
    ("indicadores", "painel"): ("indicadores", "page"),
}


def casca(request):
    rota = getattr(request, "resolver_match", None)
    chave = (rota.namespace, rota.url_name) if rota else (None, None)
    if chave in PAGINA_ATUAL:
        menu_atual, menu_estado = PAGINA_ATUAL[chave]
    elif chave[0] == "inovacoes":
        # RED-18: o resto da secao (detalhe, editar, excluir, status, reaproveitar),
        # inclusive a 404 e a 403 que essas views renderizam.
        menu_atual, menu_estado = "inovacoes", "true"
    else:
        menu_atual, menu_estado = None, None
    return {
        # RED-26, RED-40: so o valor exato "alto" liga o tema.
        "contraste_alto": request.COOKIES.get("kira_contraste") == "alto",
        "menu_atual": menu_atual,
        "menu_estado": menu_estado,
        # RED-14: o campo de busca so existe na lista.
        "busca_href": "#id_q" if chave == ("inovacoes", "lista") else "/inovacoes/#id_q",
    }
