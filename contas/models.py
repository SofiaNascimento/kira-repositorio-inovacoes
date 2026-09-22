from django.contrib.auth.models import AbstractUser
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
        max_length=13,
        choices=PerfilUsuario.choices,
        default=PerfilUsuario.USUARIO,
    )

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
        ]

    @property
    def is_administrador(self) -> bool:
        """Ponto unico de consulta do perfil (AUTH-19).

        As demais features perguntam por aqui em vez de comparar o campo.
        """
        return self.perfil == PerfilUsuario.ADMINISTRADOR
