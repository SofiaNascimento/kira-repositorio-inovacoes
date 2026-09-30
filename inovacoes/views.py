from django.contrib import messages
from django.db import IntegrityError, transaction
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from inovacoes.forms import InovacaoForm
from inovacoes.models import Inovacao

CONSTRAINT_TITULO = "inovacao_titulo_unico_por_unidade"


def _mensagem_de_titulo_duplicado():
    (constraint,) = (c for c in Inovacao._meta.constraints if c.name == CONSTRAINT_TITULO)
    return constraint.get_violation_error_message()


# Sem decorator: o LoginRequiredMiddleware ja nega o anonimo (AD-006, INOV-07).
class InovacaoCreateView(CreateView):
    """Cadastro de inovacao (RF02), aberto a qualquer perfil (INOV-08)."""

    form_class = InovacaoForm
    template_name = "inovacoes/inovacao_form.html"
    # PROVISORIO: a home interna e o destino ate a F3 trazer a pagina de detalhe.
    success_url = reverse_lazy("nucleo:home")

    def form_valid(self, form):
        # INOV-04: o autor vem da sessao, nunca do formulario.
        form.instance.autor = self.request.user
        try:
            with transaction.atomic():
                self.object = form.save()
        except IntegrityError as erro:
            # INOV-25: dois envios simultaneos passam juntos pela validacao e o
            # segundo bate na constraint. So esse caso vira erro de campo;
            # qualquer outra violacao sobe e vira 500.
            diag = getattr(erro.__cause__, "diag", None)
            if getattr(diag, "constraint_name", None) != CONSTRAINT_TITULO:
                raise
            form.add_error("titulo", _mensagem_de_titulo_duplicado())
            return self.form_invalid(form)
        # INOV-28: diz o que aconteceu e com qual registro (RF12).
        messages.success(self.request, f"Inovação “{self.object.titulo}” cadastrada com sucesso.")
        return HttpResponseRedirect(self.get_success_url())
