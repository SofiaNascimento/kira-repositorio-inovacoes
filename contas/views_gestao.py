"""Area "Minha unidade" do gestor de unidade (gestao-por-unidade).

Toda view daqui herda o GestaoDeUnidadeMixin, o porteiro do papel, como as
views que alteram inovacao herdam o AlteracaoDeInovacaoMixin (AD-009).
"""

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from contas.forms import ContaDaUnidadeForm
from contas.models import PerfilUsuario, Usuario


class GestaoDeUnidadeMixin:
    """Porteiro de toda view sob /minha-unidade/ (GEST-12, GEST-61, GEST-62).

    O perfil e o unico criterio: is_staff e is_superuser nao abrem a area. Nas
    rotas com pk, a conta-alvo sai de administraveis_por; fora do escopo ou
    inexistente, a resposta e a mesma 404 propria, antes de qualquer metodo HTTP.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_gestor_de_unidade:
            return render(request, "contas/gestao/acesso_restrito.html", status=403)
        if "pk" in kwargs:
            try:
                self.conta = Usuario.objects.administraveis_por(request.user).get(pk=kwargs["pk"])
            except Usuario.DoesNotExist:
                return render(request, "contas/gestao/conta_nao_encontrada.html", status=404)
        return super().dispatch(request, *args, **kwargs)


class MinhaUnidadeView(GestaoDeUnidadeMixin, ListView):
    """As contas da unidade do gestor (GEST-13 a GEST-19, GEST-64, GEST-65)."""

    template_name = "contas/gestao/minha_unidade.html"
    context_object_name = "contas"

    def get_queryset(self):
        return Usuario.objects.da_unidade(self.request.user.unidade_id)

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contas = list(contexto["contas"])
        for conta in contas:
            # GEST-17, GEST-18: a regra do modelo, sem consulta por linha.
            conta.administravel = conta.pode_ser_administrada_por(self.request.user)
        contexto["contas"] = contas
        # GEST-64: a unidade relida a cada requisicao, com o nome atual. Outro nome
        # que "unidade": esse e o parametro da trilha (raiz "Minha unidade").
        contexto["unidade_do_gestor"] = self.request.user.unidade
        return contexto


class CriarContaView(GestaoDeUnidadeMixin, CreateView):
    """Criar conta na unidade do gestor (GEST-20 a GEST-29)."""

    form_class = ContaDaUnidadeForm
    template_name = "contas/gestao/conta_form.html"
    success_url = reverse_lazy("gestao:painel")

    def get_context_data(self, **kwargs):
        return super().get_context_data(unidade_do_gestor=self.request.user.unidade, **kwargs)

    def form_valid(self, form):
        conta = form.save(commit=False)
        # GEST-21, GEST-23: o papel e a unidade vem do gestor, nunca do POST.
        conta.perfil = PerfilUsuario.USUARIO
        conta.unidade_id = self.request.user.unidade_id
        conta.senha_provisoria = True
        conta.is_active = True
        conta.is_staff = False
        conta.is_superuser = False
        conta.save()
        self.object = conta
        messages.success(
            self.request,
            f"Conta “{conta.username}” criada. Informe a senha provisória à pessoa: "
            "ela vai trocá-la no primeiro acesso.",
        )
        return HttpResponseRedirect(self.get_success_url())
