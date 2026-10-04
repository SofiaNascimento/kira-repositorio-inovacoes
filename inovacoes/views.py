from django.contrib import messages
from django.db import IntegrityError, transaction
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import CreateView, DetailView, ListView

from inovacoes.forms import BuscaForm, InovacaoForm
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

    def get_initial(self):
        # INOV-39: pre-preenchido e editavel; o responsavel nem sempre e o autor.
        usuario = self.request.user
        nome = usuario.get_full_name() or usuario.get_username()
        return {"contato": f"{nome} ({usuario.email})"}

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


# Sem decorator: o LoginRequiredMiddleware ja nega o anonimo (AD-006, CONS-07).
class InovacaoDetailView(DetailView):
    """Detalhe de uma inovacao com o contato responsavel (RF04, RN06)."""

    queryset = Inovacao.objects.select_related("unidade", "categoria", "autor")
    context_object_name = "inovacao"
    template_name = "inovacoes/inovacao_detail.html"

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            # CONS-15: 404 proprio da inovacao, igual com e sem DEBUG. Um
            # templates/404.html global nao serviria a qualquer URL inexistente.
            return render(request, "inovacoes/inovacao_nao_encontrada.html", status=404)


# Sem decorator: o LoginRequiredMiddleware ja nega o anonimo (AD-006, CONS-07).
class InovacaoListView(ListView):
    """Listagem de todas as inovacoes, para qualquer perfil (RF03, CONS-08)."""

    template_name = "inovacoes/inovacao_list.html"
    context_object_name = "inovacoes"

    paginate_by = 20

    def get_queryset(self):
        # Sempre vinculado ao GET: repopula os controles (CONS-25, CONS-29).
        self.form = BuscaForm(self.request.GET)
        consulta = Inovacao.objects.para_listagem()
        if not self.form.is_valid():
            # CONS-24, CONS-30: parametro invalido nao lista nada.
            return consulta.none()
        dados = self.form.cleaned_data
        return consulta.buscar(dados["q"]).filtrar(
            categoria=dados["categoria"], unidade=dados["unidade"], status=dados["status"]
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(form=self.form, **kwargs)

    # SPEC_DEVIATION: o design chama get_page() com o valor cru de ?page=.
    # Reason: get_page() manda page=0 para a ultima pagina; a T5 pede a primeira.
    def paginate_queryset(self, queryset, page_size):
        # CONS-05: o ListView padrao daria 404 para pagina invalida.
        paginator = self.get_paginator(queryset, page_size)
        try:
            numero = max(int(self.request.GET.get("page", 1)), 1)
        except ValueError:
            numero = 1
        pagina = paginator.get_page(numero)
        return (paginator, pagina, pagina.object_list, pagina.has_other_pages())
