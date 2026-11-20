from functools import reduce
from operator import or_

from django.conf import settings
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.db import IntegrityError, models, transaction
from django.db.models import Count, OuterRef, Q, Subquery
from django.db.models.functions import Coalesce, Lower
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


class UnidadeQuerySet(models.QuerySet):
    """Agregacoes do painel por unidade (AD-002, REAP-33)."""

    def com_indicadores(self):
        """Inovacoes de origem e reaproveitamentos feitos, com zeros.

        Uma subconsulta correlacionada por contagem: duas Count() no mesmo
        annotate fariam dois JOINs e multiplicariam as linhas (fan-out).
        """

        def contagem(modelo):
            return Coalesce(
                Subquery(
                    modelo.objects.filter(unidade=OuterRef("pk"))
                    .order_by()  # limpa o Meta.ordering do GROUP BY
                    .values("unidade")
                    .annotate(n=Count("pk"))
                    .values("n")
                ),
                0,
            )

        return self.annotate(
            inovacoes_de_origem=contagem(Inovacao),
            reaproveitamentos_feitos=contagem(Reaproveitamento),
        ).order_by("-inovacoes_de_origem", "nome")


class CategoriaQuerySet(models.QuerySet):
    """Agregacoes do painel por categoria (AD-002, REAP-32)."""

    def com_total_de_inovacoes(self):
        # LEFT OUTER JOIN: categoria sem inovacao sai com total 0.
        return self.annotate(total=Count("inovacao")).order_by("-total", "nome")


class Unidade(ItemDeLista):
    objects = UnidadeQuerySet.as_manager()

    class Meta(ItemDeLista.Meta):
        verbose_name = "unidade"
        verbose_name_plural = "unidades"


class Categoria(ItemDeLista):
    objects = CategoriaQuerySet.as_manager()

    class Meta(ItemDeLista.Meta):
        verbose_name = "categoria"
        verbose_name_plural = "categorias"


class InovacaoQuerySet(models.QuerySet):
    """Unico ponto que sabe como consultar e ordenar inovacoes (AD-002)."""

    def para_listagem(self):
        # CONS-02: mais recentes primeiro, id desempata. Uma consulta so, sem N+1:
        # o resumo (problema) e a contagem de reaproveitamentos do cartao vem juntos
        # (RCON-13, RCON-14, RCON-16).
        return (
            self.select_related("unidade", "categoria")
            .only(
                "id",
                "titulo",
                "problema",
                "status",
                "data_criacao",
                "unidade__nome",
                "categoria__nome",
            )
            .annotate(total_reaproveitamentos=Count("reaproveitamentos"))
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


class TransicaoDeStatusRecusada(Exception):
    """O avanco de status foi recusado e nada foi gravado (STAT-10, STAT-12)."""


class StatusDesatualizado(TransicaoDeStatusRecusada):
    """O status que a pessoa viu nao e mais o gravado (STAT-12, STAT-13)."""

    def __init__(self, status_atual):
        super().__init__(status_atual)
        self.status_atual = status_atual


class UltimoEstagioDoCiclo(TransicaoDeStatusRecusada):
    """A inovacao ja esta no estagio final do ciclo (STAT-10)."""


# Campos de que texto_busca deriva (AD-008).
CAMPOS_DA_BUSCA = {"titulo", "problema", "solucao"}

# RN09: as tres recusas da sinalizacao, com o texto exato da spec.
# REAP-09: {status} e o rotulo do status gravado.
MENSAGEM_REAPROVEITAMENTO_STATUS = (
    "Só uma inovação “Disponível para replicação” pode ser sinalizada como reaproveitada. "
    "Status atual: “{status}”."
)
# REAP-11
MENSAGEM_REAPROVEITAMENTO_ORIGEM = "A unidade de origem não pode reaproveitar a própria inovação."
# REAP-12: {unidade} e o nome da unidade repetida.
MENSAGEM_REAPROVEITAMENTO_REPETIDO = (
    "A unidade “{unidade}” já sinalizou o reaproveitamento desta inovação."
)


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

    @property
    def proximo_status(self):
        """Proximo estagio do ciclo, ou None no ultimo (RN03)."""
        return PROXIMO_STATUS.get(self.status)

    def avancar_status(self, *, por, status_visto):
        """AD-011: unico caminho para mudar o status depois do cadastro.

        Avanca um estagio e cria o MudancaDeStatus na mesma transacao (STAT-15).
        A trava da linha serializa envios simultaneos, e o status visto faz o
        segundo cair em StatusDesatualizado em vez de pular um estagio
        (STAT-13). Nao decide autorizacao: a view ja passou pelo mixin (AD-009).
        Inovacao.DoesNotExist sobe se a inovacao foi apagada (STAT-22).
        """
        with transaction.atomic():
            # O valor gravado, e nao o da instancia: ela pode estar velha.
            gravado = (
                Inovacao.objects.select_for_update()
                .values_list("status", flat=True)
                .get(pk=self.pk)
            )
            if status_visto != gravado:
                raise StatusDesatualizado(gravado)
            novo = PROXIMO_STATUS.get(gravado)
            if novo is None:
                raise UltimoEstagioDoCiclo()
            # AD-008: grava pelo save(), so o status; ele nao entra em texto_busca.
            self.status = novo
            self.save(update_fields=["status"])
            return MudancaDeStatus.objects.create(
                inovacao=self, status_anterior=gravado, status_novo=novo, responsavel=por
            )

    def pode_ser_reaproveitada(self) -> bool:
        """RN09: so uma inovacao disponivel para replicacao aceita sinalizacao.

        Le o status desta instancia; a garantia final e a releitura travada em
        registrar_reaproveitamento.
        """
        return self.status == StatusInovacao.DISPONIVEL_PARA_REPLICACAO

    def registrar_reaproveitamento(self, *, unidade, por):
        """AD-012: unico caminho para criar um Reaproveitamento (RN09).

        Trava a linha, confere o status gravado (REAP-10) e a unidade de origem
        (REAP-11) e cria o registro. A repeticao fica com a UniqueConstraint
        (REAP-12, REAP-14). Nao decide autorizacao (REAP-19) e nao grava nenhum
        campo da inovacao (REAP-07). Inovacao.DoesNotExist sobe se a inovacao
        foi apagada (REAP-16).
        """
        with transaction.atomic():
            # O valor gravado, e nao o da instancia: ela pode estar velha.
            # A trava serializa duas sinalizacoes da mesma inovacao.
            gravado = (
                Inovacao.objects.select_for_update()
                .values_list("status", flat=True)
                .get(pk=self.pk)
            )
            if gravado != StatusInovacao.DISPONIVEL_PARA_REPLICACAO:
                raise ValidationError(
                    MENSAGEM_REAPROVEITAMENTO_STATUS.format(status=StatusInovacao(gravado).label),
                    code="status_indisponivel",
                )
            if unidade.pk == self.unidade_id:
                raise ValidationError(MENSAGEM_REAPROVEITAMENTO_ORIGEM, code="unidade_de_origem")
            try:
                # Savepoint: a transacao de quem chamou sobrevive ao erro.
                with transaction.atomic():
                    return Reaproveitamento.objects.create(
                        inovacao=self, unidade=unidade, registrado_por=por
                    )
            except IntegrityError as erro:
                # REAP-14: so a unicidade vira recusa; outra violacao sobe e vira 500.
                diag = getattr(erro.__cause__, "diag", None)
                if getattr(diag, "constraint_name", None) != "reaproveitamento_unico_por_unidade":
                    raise
                raise ValidationError(
                    MENSAGEM_REAPROVEITAMENTO_REPETIDO.format(unidade=unidade.nome),
                    code="unidade_ja_reaproveitou",
                ) from erro

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


class Reaproveitamento(models.Model):
    """Uma unidade reaproveitou uma inovacao de outra (RF11, RN09).

    AD-012: so nasce por Inovacao.registrar_reaproveitamento.
    """

    # REAP-23: apagar a inovacao apaga os reaproveitamentos dela.
    inovacao = models.ForeignKey(
        Inovacao,
        on_delete=models.CASCADE,
        related_name="reaproveitamentos",
        verbose_name="inovação",
    )
    # REAP-24: unidade em uso nao pode ser apagada (mesmo criterio da INOV-19).
    unidade = models.ForeignKey(
        Unidade,
        on_delete=models.PROTECT,
        related_name="reaproveitamentos",
        verbose_name="unidade que reaproveitou",
    )
    # REAP-25: excluir a conta nao apaga o registro do que ela sinalizou.
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reaproveitamentos_registrados",
        verbose_name="registrado por",
    )
    data = models.DateTimeField("data", auto_now_add=True)

    class Meta:
        verbose_name = "reaproveitamento"
        verbose_name_plural = "reaproveitamentos"
        # REAP-18: do mais antigo ao mais recente; o id desempata.
        ordering = ["data", "id"]
        constraints = [
            # REAP-14: uma sinalizacao por unidade, garantida pelo banco.
            models.UniqueConstraint(
                fields=["inovacao", "unidade"],
                name="reaproveitamento_unico_por_unidade",
            ),
        ]

    def __str__(self):
        return f"{self.inovacao} — {self.unidade}"
