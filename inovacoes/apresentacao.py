"""Estado da consulta transformado em dados de exibicao (R2).

Funcoes puras: nao consultam o banco nem leem o request. A view passa o
QueryDict do GET e os objetos ja carregados; o template so itera o resultado.
Mesmo padrao do modulo busca.py (AD-002, AD-008).
"""

from django.urls import reverse


def url_da_lista(consulta, **mudancas):
    """URL da lista com a query string atual mais as mudancas; None tira o parametro.

    Sem parametro sobrando devolve so o caminho, sem "?" (RCON-05, RCON-06).
    Os demais parametros, inclusive os repetidos, ficam como estavam (RCON-18).
    """
    parametros = consulta.copy()
    for nome, valor in mudancas.items():
        if valor is None:
            parametros.pop(nome, None)
        else:
            parametros[nome] = str(valor)
    caminho = reverse("inovacoes:lista")
    query = parametros.urlencode()
    return f"{caminho}?{query}" if query else caminho


def exibicao(consulta):
    """So o valor exato "tabela" escolhe a tabela; o resto e cartoes, sem erro (RCON-20)."""
    return "tabela" if consulta.get("exibicao") == "tabela" else "cartoes"
