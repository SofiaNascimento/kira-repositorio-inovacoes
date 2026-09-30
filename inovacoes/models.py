from django.conf import settings
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower


class StatusInovacao(models.TextChoices):
    """Enumeracao StatusInovacao do diagrama de classes (RN03).

    Fica no nivel de modulo pelo mesmo motivo do PerfilUsuario: a Meta de
    Inovacao precisa referencia-la ao montar a CheckConstraint.
    """

    EM_TESTE = "EM_TESTE", "Em teste"
    VALIDADA = "VALIDADA", "Validada"
    DISPONIVEL_PARA_REPLICACAO = "DISPONIVEL_PARA_REPLICACAO", "Disponível para replicação"


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


class Inovacao(models.Model):
    """A entidade central do dominio (RF02).

    Autor, status e data de criacao sao do sistema (RN03, RN08): nenhum deles
    entra no formulario de cadastro.
    """

    titulo = models.CharField("título", max_length=150)
    # PROTECT: item de lista em uso nao pode ser apagado (INOV-19).
    unidade = models.ForeignKey(Unidade, on_delete=models.PROTECT, verbose_name="unidade de origem")
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, verbose_name="categoria")
    problema = models.TextField("problema ou dor")
    solucao = models.TextField("solução aplicada")
    resultado = models.TextField("resultado ou impacto", blank=True)
    contato = models.CharField("contato responsável", max_length=150)
    status = models.CharField(
        "status", max_length=26, choices=StatusInovacao.choices, default=StatusInovacao.EM_TESTE
    )
    # Excluir uma conta nao apaga o conhecimento que ela registrou.
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="inovacoes",
        verbose_name="autor",
    )
    data_criacao = models.DateTimeField("data de criação", auto_now_add=True)

    class Meta:
        verbose_name = "inovação"
        verbose_name_plural = "inovações"
        constraints = [
            # RN10: mesmo titulo na mesma unidade, sem distinguir caixa. Acentos
            # contam: lower() do PostgreSQL nao os remove (INOV-27).
            models.UniqueConstraint(
                Lower("titulo"),
                "unidade",
                name="inovacao_titulo_unico_por_unidade",
                violation_error_code="titulo_duplicado",
                violation_error_message=(
                    "Já existe uma inovação com este título nesta unidade. Escolha outro título."
                ),
            ),
            # choices so e checado em full_clean(); a regra desce para o banco.
            models.CheckConstraint(
                condition=Q(status__in=StatusInovacao.values),
                name="inovacao_status_valido",
            ),
        ]

    def __str__(self):
        return self.titulo

    def validate_constraints(self, exclude=None):
        """Leva o erro de titulo duplicado para o campo titulo (INOV-22).

        Uma UniqueConstraint sobre expressao nao sabe a que campo pertence e o
        Django a acusa como erro geral. Resolver aqui, e nao no formulario, faz
        a regra valer para qualquer full_clean().
        """
        try:
            super().validate_constraints(exclude=exclude)
        except ValidationError as erro:
            erros = erro.error_dict
            gerais = erros.pop(NON_FIELD_ERRORS, [])
            duplicados = [e for e in gerais if e.code == "titulo_duplicado"]
            outros = [e for e in gerais if e.code != "titulo_duplicado"]
            if duplicados:
                erros.setdefault("titulo", []).extend(duplicados)
            if outros:
                erros[NON_FIELD_ERRORS] = outros
            raise ValidationError(erros) from erro
