import logging

from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver
from django.utils import timezone

logger = logging.getLogger("contas.autenticacao")


@receiver(user_login_failed)
def registrar_tentativa_malsucedida(sender, credentials, request=None, **kwargs):
    """Deixa rastro de cada login recusado (AUTH-27).

    Registra so o identificador: a senha nunca entra, mesmo que chegue nas
    credenciais (AUTH-08). O horario vai na propria mensagem porque o projeto
    nao configura formatter de log.
    """
    logger.warning(
        "Tentativa de login malsucedida para %r em %s",
        credentials.get("username"),
        timezone.now().isoformat(),
    )
