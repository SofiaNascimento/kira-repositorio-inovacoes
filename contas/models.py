from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """Usuario do sistema.

    O perfil e um campo deste modelo, nao uma segunda classe de usuario nem um
    modelo a parte (AD-004). A senha e a do AbstractUser, guardada como hash
    pelos hashers do Django (RNF02): nao existe campo de senha proprio.
    """

    class Perfil(models.TextChoices):
        USUARIO = "USUARIO", "Usuário"
        ADMINISTRADOR = "ADMINISTRADOR", "Administrador"

    email = models.EmailField("e-mail", unique=True)
    perfil = models.CharField(
        "perfil",
        max_length=13,
        choices=Perfil.choices,
        default=Perfil.USUARIO,
    )

    class Meta:
        verbose_name = "usuário"
        verbose_name_plural = "usuários"

    @property
    def is_administrador(self) -> bool:
        """Ponto unico de consulta do perfil (AUTH-19).

        As demais features perguntam por aqui em vez de comparar o campo.
        """
        return self.perfil == self.Perfil.ADMINISTRADOR
