from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

UserModel = get_user_model()


class UsernameOrEmailBackend(ModelBackend):
    """Autentica pelo username ou pelo e-mail, no mesmo campo (AUTH-01, AUTH-02).

    Troca apenas a busca do ModelBackend. Continuam herdados o
    user_can_authenticate(), que recusa conta inativa (AUTH-23), e o
    comportamento do dummy hash descrito abaixo.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return None

        # Uma busca so. Pega ate duas linhas para detectar ambiguidade sem
        # confiar na constraint de e-mail: mais de uma conta, nenhuma entra.
        candidatos = list(
            UserModel._default_manager.filter(
                Q(username__iexact=username) | Q(email__iexact=username)
            )[:2]
        )
        if len(candidatos) != 1:
            # Hash descartavel, como o ModelBackend faz: sem ele, a resposta
            # rapida denunciaria que o identificador nao existe.
            UserModel().set_password(password)
            return None

        usuario = candidatos[0]
        if usuario.check_password(password) and self.user_can_authenticate(usuario):
            return usuario
        return None
