"""Estado da consulta transformado em dados de exibicao (R2).

Funcoes puras: nao consultam o banco nem leem o request. A view passa o
QueryDict do GET e os objetos ja carregados; o template so itera o resultado.
Mesmo padrao do modulo busca.py (AD-002, AD-008).
"""

from typing import NamedTuple

from django.urls import reverse

from inovacoes.models import StatusInovacao


class Etiqueta(NamedTuple):
    """Um filtro ativo: o texto exibido e o link que o remove (RCON-04, RCON-05)."""

    texto: str
    href: str


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


def etiquetas(dados_validos, consulta):
    """Uma etiqueta por filtro valido, na ordem Busca, Categoria, Unidade, Status.

    Recebe o cleaned_data do BuscaForm: so valores validos chegam aqui. Busca so
    com espacos nao conta (CONS-21). O link tira o proprio parametro e o page e
    mantem o resto, inclusive exibicao (RCON-04, RCON-05, RCON-07).
    """
    textos = []
    termo = (dados_validos.get("q") or "").strip()
    if termo:
        textos.append(("q", f"Busca: “{termo}”"))
    if dados_validos.get("categoria") is not None:
        textos.append(("categoria", f"Categoria: {dados_validos['categoria'].nome}"))
    if dados_validos.get("unidade") is not None:
        textos.append(("unidade", f"Unidade: {dados_validos['unidade'].nome}"))
    if dados_validos.get("status"):
        textos.append(("status", f"Status: {StatusInovacao(dados_validos['status']).label}"))
    return [
        Etiqueta(texto, url_da_lista(consulta, **{parametro: None, "page": None}))
        for parametro, texto in textos
    ]
