from django.apps import AppConfig


class ContasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "contas"

    def ready(self):
        # Conecta o receiver de user_login_failed (AUTH-27).
        from contas import signals  # noqa: F401
