"""Estado da consulta transformado em dados de exibicao (R2).

Funcoes puras: nao consultam o banco nem leem o request. A view passa o
QueryDict do GET e os objetos ja carregados; o template so itera o resultado.
Mesmo padrao do modulo busca.py (AD-002, AD-008).
"""

from typing import NamedTuple

from django.core.paginator import Paginator
from django.urls import reverse

from inovacoes.models import StatusInovacao


class ItemDoHistorico(NamedTuple):
    """Um ponto da linha do tempo do historico (RCON-43, RCON-44)."""

    data: object
    texto: str
    cadastro: bool


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


# SPEC_DEVIATION: o design manda usar Paginator.get_elided_page_range(on_each_side=2, on_ends=1).
# Reason: esse metodo nao poe "…" no lugar de uma pagina so (na 5 de 25 da 1 2 3 4 5 6 7 … 25),
# e a RCON-22 pede um "…" para cada salto (1 … 3 4 5 6 7 … 25). A janela e calculada aqui.
def paginas(page_obj):
    """Primeira, ultima e a atual +- 2, em ordem, com um "…" por salto (RCON-22)."""
    atual = page_obj.number
    total = page_obj.paginator.num_pages
    numeros = sorted({1, total, *range(max(atual - 2, 1), min(atual + 2, total) + 1)})
    janela = []
    for numero in numeros:
        if janela and numero > janela[-1] + 1:
            janela.append(Paginator.ELLIPSIS)
        janela.append(numero)
    return janela


def _nome(usuario):
    # CONS-13: nome completo ou, sem ele, o username.
    return usuario.get_full_name() or usuario.get_username()


def itens_do_historico(inovacao, mudancas):
    """O cadastro e depois cada mudanca de status, na ordem recebida (RCON-43 a RCON-45).

    O status do cadastro e o status_anterior da primeira mudanca ou, sem mudancas,
    o status atual. Recebe as mudancas ja carregadas: nao consulta o banco.
    """
    inicial = mudancas[0].status_anterior if mudancas else inovacao.status
    itens = [
        ItemDoHistorico(
            inovacao.data_criacao,
            f"Cadastrada como “{StatusInovacao(inicial).label}”, por {_nome(inovacao.autor)}",
            True,
        )
    ]
    for mudanca in mudancas:
        texto = (
            f"De “{mudanca.get_status_anterior_display()}” para "
            f"“{mudanca.get_status_novo_display()}”, por {_nome(mudanca.responsavel)}"
        )
        itens.append(ItemDoHistorico(mudanca.data, texto, False))
    return itens
