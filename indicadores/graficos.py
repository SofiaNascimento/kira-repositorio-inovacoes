"""Geometria dos graficos de barras do painel (REAP-35, REAP-36).

Funcoes puras, sem banco: o template so desenha o que sai daqui, porque a
linguagem de template do Django nao multiplica nem divide.
"""

from typing import NamedTuple

# Unidades do viewBox (0 0 600 altura): a barra do maior valor ocupa a area toda.
AREA = 480
ALTURA_DA_LINHA = 44
# O valor fica logo depois da barra, ou no inicio quando o valor e 0.
AFASTAMENTO_DO_VALOR = 8


class Barra(NamedTuple):
    nome: str
    valor: int
    y: int
    comprimento: float
    x_valor: float


class Grafico(NamedTuple):
    id: str
    titulo: str
    barras: list[Barra]
    altura: int

    @classmethod
    def de(cls, id, titulo, barras):
        """Monta o grafico com a altura do SVG calculada pelas linhas."""
        return cls(id, titulo, barras, len(barras) * ALTURA_DA_LINHA)


def barras(itens, atributo):
    """Uma barra por item, na ordem recebida, proporcional ao maior valor.

    REAP-35: o maior valor ocupa a area toda e o valor 0 nao tem barra; com
    todos em zero nenhum comprimento passa de 0 (e nao ha divisao por zero).
    """
    valores = [getattr(item, atributo) for item in itens]
    maior = max(valores, default=0)
    resultado = []
    for i, (item, valor) in enumerate(zip(itens, valores, strict=True)):
        comprimento = round(valor * AREA / maior, 2) if valor and maior else 0
        resultado.append(
            Barra(
                nome=item.nome,
                valor=valor,
                y=i * ALTURA_DA_LINHA,
                comprimento=comprimento,
                x_valor=comprimento + AFASTAMENTO_DO_VALOR,
            )
        )
    return resultado
