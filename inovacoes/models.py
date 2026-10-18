from functools import reduce
from operator import or_

from django.conf import settings
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower
from django.urls import reverse

from inovacoes.busca import palavras, texto_de_busca


class StatusInovacao(models.TextChoices):
    """Enumeracao StatusInovacao do diagrama de classes (RN03).

    Fica no nivel de modulo pelo mesmo motivo do PerfilUsuario: a Meta de
    Inovacao precisa referencia-la ao montar a CheckConstraint.
    """

    EM_TESTE = "EM_TESTE", "Em teste"
    VALIDADA = "VALIDADA", "Validada"
    DISPONIVEL_PARA_REPLICACAO = "DISPONIVEL_PARA_REPLICACAO", "Disponível para replicação"


# RN03: fonte unica da sequencia do ciclo. Sem chave = estagio final.
PROXIMO_STATUS = {
    StatusInovacao.EM_TESTE: StatusInovacao.VALIDADA,
    StatusInovacao.VALIDADA: StatusInovacao.DISPONIVEL_PARA_REPLICACAO,
}


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


class InovacaoQuerySet(models.QuerySet):
    """Unico ponto que sabe como consultar e ordenar inovacoes (AD-002)."""

    def para_listagem(self):
        # CONS-02: mais recentes primeiro, id desempata. Uma consulta so, sem N+1.
        return (
            self.select_related("unidade", "categoria")
            .only("id", "titulo", "status", "data_criacao", "unidade__nome", "categoria__nome")
            .order_by("-data_criacao", "-id")
        )

    def buscar(self, termo):
        """CONS-19 a CONS-23: toda palavra do termo aparece no texto de busca.

        Um filter por palavra (E). O lookup contains escapa %, _ e \\ do LIKE,
        entao eles casam como texto (CONS-23). Termo em branco nao filtra.
        """
        qs = self
        for palavra in palavras(termo or ""):
            qs = qs.filter(texto_busca__contains=palavra)
        return qs

    def filtrar(self, *, categoria=None, unidade=None, status=""):
        """CONS-27, CONS-28: cada filtro informado restringe; os vazios sao ignorados."""
        filtros = {}
        if categoria is not None:
            filtros["categoria"] = categoria
        if unidade is not None:
            filtros["unidade"] = unidade
        if status:
            filtros["status"] = status
        return self.filter(**filtros)


# Campos de que texto_busca deriva (AD-008).
CAMPOS_DA_BUSCA = {"titulo", "problema", "solucao"}


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
    # AD-008: titulo + problema + solucao sem acento e em minusculas, mantido
    # pelo save(). Toda escrita desses tres campos precisa passar pelo save():
    # update(), bulk_create e bulk_update deixam a busca errada.
    texto_busca = models.TextField(editable=False, default="")

    objects = InovacaoQuerySet.as_manager()

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

    def save(self, *args, update_fields=None, **kwargs):
        self.texto_busca = texto_de_busca(self.titulo, self.problema, self.solucao)
        if update_fields is not None:
            # Copia: nao altera o iteravel de quem chamou.
            update_fields = set(update_fields)
            if update_fields & CAMPOS_DA_BUSCA:
                update_fields.add("texto_busca")
        super().save(*args, update_fields=update_fields, **kwargs)

    def get_absolute_url(self):
        # CONS-06: URL canonica do detalhe; o CreateView a usa como destino (CONS-49).
        return reverse("inovacoes:detalhe", args=[self.pk])

    def pode_ser_alterada_por(self, usuario) -> bool:
        """RN05, AD-009: so o autor ou um ADMINISTRADOR edita ou exclui.

        O perfil e o unico criterio: is_staff e is_superuser nao contam. Le
        autor_id, e nao autor, para nao consultar o banco. A guarda de
        is_authenticated cobre o AnonymousUser, que nao tem is_administrador.
        """
        return usuario.is_authenticated and (
            usuario.is_administrador or self.autor_id == usuario.pk
        )

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


class MudancaDeStatus(models.Model):
    """Registro de um avanco de status (STAT-14): quem, quando, de qual para qual.

    So o Inovacao.avancar_status cria registros (AD-011); nenhuma tela, rota ou
    admin os edita ou apaga (STAT-30, AD-007).
    """

    # STAT-28: apagar a inovacao apaga o historico dela.
    inovacao = models.ForeignKey(
        Inovacao,
        on_delete=models.CASCADE,
        related_name="mudancas_de_status",
        verbose_name="inovação",
    )
    status_anterior = models.CharField(
        "status anterior", max_length=26, choices=StatusInovacao.choices
    )
    status_novo = models.CharField("status novo", max_length=26, choices=StatusInovacao.choices)
    # STAT-29: excluir a conta responsavel nao apaga a trilha.
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="mudancas_de_status",
        verbose_name="responsável",
    )
    data = models.DateTimeField("data da mudança", auto_now_add=True)

    class Meta:
        verbose_name = "mudança de status"
        verbose_name_plural = "mudanças de status"
        # STAT-24: do mais antigo ao mais recente; o id desempata.
        ordering = ["data", "id"]
        constraints = [
            # STAT-31: o banco so aceita as transicoes de PROXIMO_STATUS.
            models.CheckConstraint(
                condition=reduce(
                    or_,
                    (Q(status_anterior=a, status_novo=n) for a, n in PROXIMO_STATUS.items()),
                ),
                name="mudanca_de_status_transicao_valida",
            ),
        ]

    def __str__(self):
        return f"{self.get_status_anterior_display()} → {self.get_status_novo_display()}"
