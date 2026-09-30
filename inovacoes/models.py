from django.db import models
from django.db.models.functions import Lower


class ItemDeLista(models.Model):
    """Base das listas controladas da RN07: um nome, unico sem distinguir caixa.

    Duas "Sede" em caixa diferente quebrariam os filtros da F3, que sao a
    razao de a lista ser controlada.
    """

    nome = models.CharField("nome", max_length=100)

    class Meta:
        abstract = True
        # INOV-15: o select do formulario lista as opcoes em ordem alfabetica.
        ordering = ["nome"]
        constraints = [
            models.UniqueConstraint(
                Lower("nome"),
                name="%(class)s_nome_unico_ci",
                violation_error_message="Já existe um item com este nome.",
            ),
        ]

    def __str__(self):
        return self.nome


class Unidade(ItemDeLista):
    class Meta(ItemDeLista.Meta):
        verbose_name = "unidade"
        verbose_name_plural = "unidades"


class Categoria(ItemDeLista):
    class Meta(ItemDeLista.Meta):
        verbose_name = "categoria"
        verbose_name_plural = "categorias"
