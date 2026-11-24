from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower


class PerfilUsuario(models.TextChoices):
    """Enumeracao PerfilUsuario do diagrama de classes (AD-004).

    Fica no nivel de modulo, e nao aninhada em Usuario, porque a Meta do
    modelo precisa referencia-la ao montar a CheckConstraint: uma classe
    aninhada ainda nao existe no escopo quando o corpo da Meta e avaliado.
    Usuario.Perfil continua valendo como alias.
    """

    USUARIO = "USUARIO", "Usuário"
    ADMINISTRADOR = "ADMINISTRADOR", "Administrador"
    GESTOR_DE_UNIDADE = "GESTOR_DE_UNIDADE", "Gestor de unidade"


class UsuarioManager(UserManager):
    """Manager de Usuario.

    Existe por um motivo so: garantir que a conta criada por createsuperuser
    nasca ADMINISTRADOR (AUTH-20). No MVP e assim que o primeiro
    administrador passa a existir, e ele precisa dos poderes de curadoria.
    """

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("perfil", PerfilUsuario.ADMINISTRADOR)
        return super().create_superuser(username, email, password, **extra_fields)


class Usuario(AbstractUser):
    """Usuario do sistema.

    O perfil e um campo deste modelo, nao uma segunda classe de usuario nem um
    modelo a parte (AD-004). A senha e a do AbstractUser, guardada como hash
    pelos hashers do Django (RNF02): nao existe campo de senha proprio.
    """

    Perfil = PerfilUsuario

    email = models.EmailField("e-mail", unique=True)
    perfil = models.CharField(
        "perfil",
        max_length=17,
        choices=PerfilUsuario.choices,
        default=PerfilUsuario.USUARIO,
    )
    # Opcional: contas atuais, autores do acervo e ADMINISTRADORES vivem sem
    # unidade. So o gestor precisa dela (CHECK abaixo, AD-004 estendida).
    unidade = models.ForeignKey(
        "inovacoes.Unidade",
        verbose_name="unidade",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="usuarios",
    )
    senha_provisoria = models.BooleanField("senha provisória", default=False)

    objects = UsuarioManager()

    class Meta:
        verbose_name = "usuário"
        verbose_name_plural = "usuários"
        constraints = [
            # choices so e checado em full_clean(); um create() ou update()
            # direto gravaria lixo. A regra desce para o banco (AD-003).
            models.CheckConstraint(
                condition=Q(perfil__in=PerfilUsuario.values),
                name="usuario_perfil_valido",
            ),
            # unique=True sozinho e case-sensitive no PostgreSQL: ana@x.com e
            # Ana@X.com conviveriam e o login por e-mail ficaria ambiguo.
            models.UniqueConstraint(
                Lower("email"),
                name="usuario_email_unico_ci",
                violation_error_message="Já existe uma conta com este e-mail.",
            ),
            # GEST-03: gestor sem unidade nao teria escopo. O formulario do
            # admin avisa no campo (GEST-05); a CHECK e a rede do banco.
            models.CheckConstraint(
                condition=~Q(perfil=PerfilUsuario.GESTOR_DE_UNIDADE) | Q(unidade__isnull=False),
                name="usuario_gestor_tem_unidade",
                violation_error_message="Gestor de unidade precisa de uma unidade.",
            ),
        ]

    def save(self, *args, **kwargs):
        """Mantem is_staff coerente com o perfil.

        Concede, nunca revoga: o admin e a unica superficie de troca de perfil
        no MVP, entao um ADMINISTRADOR sem is_staff nao conseguiria exercer a
        RN11. Revogar seria pior: tiraria acesso concedido de proposito a um
        USUARIO por outro motivo.
        """
        if self.is_administrador:
            self.is_staff = True
        return super().save(*args, **kwargs)

    @property
    def is_administrador(self) -> bool:
        """Ponto unico de consulta do perfil (AUTH-19).

        As demais features perguntam por aqui em vez de comparar o campo.
        """
        return self.perfil == PerfilUsuario.ADMINISTRADOR

    @property
    def is_gestor_de_unidade(self) -> bool:
        """Ponto unico de consulta do papel de gestor (AD-004 estendida)."""
        return self.perfil == PerfilUsuario.GESTOR_DE_UNIDADE
