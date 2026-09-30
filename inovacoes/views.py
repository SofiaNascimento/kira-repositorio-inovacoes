from django.urls import reverse_lazy
from django.views.generic import CreateView

from inovacoes.forms import InovacaoForm


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
        return super().form_valid(form)
