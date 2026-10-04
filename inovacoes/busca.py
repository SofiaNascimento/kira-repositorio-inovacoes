"""Normalizacao de texto para a busca sem acento e sem caixa (AD-008).

Funcoes puras: nao conhecem model, request nem banco. O termo buscado e o
texto gravado em Inovacao.texto_busca passam pela mesma regra.
"""

import unicodedata


def normalizar(texto):
    """Tira acentos e caixa: "SOLUÇÃO" -> "solucao" (CONS-20)."""
    decomposto = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in decomposto if not unicodedata.combining(c))
    return sem_acento.casefold()


def palavras(termo):
    """Palavras normalizadas do termo; termo em branco -> [] (CONS-21)."""
    return normalizar(termo).split()


def texto_de_busca(titulo, problema, solucao):
    # O "\n" separa os campos: uma palavra nunca contem espaco em branco, entao
    # nao casa atravessando dois campos (CONS-19).
    return "\n".join(normalizar(campo) for campo in (titulo, problema, solucao))
