from django.contrib import messages
from django.db import IntegrityError, transaction
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from inovacoes.forms import BuscaForm, InovacaoForm
from inovacoes.models import Inovacao, StatusDesatualizado, StatusInovacao, UltimoEstagioDoCiclo

CONSTRAINT_TITULO = "inovacao_titulo_unico_por_unidade"


def _mensagem_de_titulo_duplicado():
    (constraint,) = (c for c in Inovacao._meta.constraints if c.name == CONSTRAINT_TITULO)
    return constraint.get_violation_error_message()


def _inovacao_nao_encontrada(request):
    # CONS-15: 404 proprio da inovacao, igual com e sem DEBUG. Um
    # templates/404.html global nao serviria a qualquer URL inexistente.
    return render(request, "inovacoes/inovacao_nao_encontrada.html", status=404)


class AlteracaoDeInovacaoMixin:
    """AD-009: toda view que altera uma Inovacao herda este mixin.

    Busca a inovacao e aplica a regra de autoria no dispatch(), antes de
    qualquer metodo HTTP: o POST negado nunca chega ao form_valid.
    """

    queryset = Inovacao.objects.select_related("unidade", "categoria")
    context_object_name = "inovacao"

    def dispatch(self, request, *args, **kwargs):
        # EDEX-27, EDEX-28: id inexistente primeiro (404), depois a autoria (403).
        try:
            self.object = super().get_object()
        except Http404:
            return _inovacao_nao_encontrada(request)
        if not self.object.pode_ser_alterada_por(request.user):
            # EDEX-20 a EDEX-23: pagina propria; o 403.html global e do admin.
            return render(
                request, "inovacoes/acesso_negado.html", {"inovacao": self.object}, status=403
            )
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        # O get()/post() das views genericas pedem de novo o que o dispatch() buscou.
        return self.object


class GravacaoComTituloUnicoMixin:
    """Grava o formulario numa transacao e trata a corrida no titulo (INOV-25, EDEX-14).

    Cada view define a mensagem_de_sucesso, com {titulo}, e pode trocar gravar().
    """

    mensagem_de_sucesso = ""

    def gravar(self, form):
        return form.save()

    def form_valid(self, form):
        try:
            with transaction.atomic():
                self.object = self.gravar(form)
        except IntegrityError as erro:
            # INOV-25: dois envios simultaneos passam juntos pela validacao e o
            # segundo bate na constraint. So esse caso vira erro de campo;
            # qualquer outra violacao sobe e vira 500.
            diag = getattr(erro.__cause__, "diag", None)
            if getattr(diag, "constraint_name", None) != CONSTRAINT_TITULO:
                raise
            form.add_error("titulo", _mensagem_de_titulo_duplicado())
            return self.form_invalid(form)
        # INOV-28, EDEX-06: diz o que aconteceu e com qual registro (RF12).
        messages.success(self.request, self.mensagem_de_sucesso.format(titulo=self.object.titulo))
        return HttpResponseRedirect(self.get_success_url())


# Sem decorator: o LoginRequiredMiddleware ja nega o anonimo (AD-006, INOV-07).
class InovacaoCreateView(GravacaoComTituloUnicoMixin, CreateView):
    """Cadastro de inovacao (RF02), aberto a qualquer perfil (INOV-08)."""

    form_class = InovacaoForm
    template_name = "inovacoes/inovacao_form.html"
    mensagem_de_sucesso = "Inovação “{titulo}” cadastrada com sucesso."

    def get_initial(self):
        # INOV-39: pre-preenchido e editavel; o responsavel nem sempre e o autor.
        usuario = self.request.user
        nome = usuario.get_full_name() or usuario.get_username()
        return {"contato": f"{nome} ({usuario.email})"}

    def get_context_data(self, **kwargs):
        # O template do formulario serve ao cadastro e a edicao (EDEX-01).
        return super().get_context_data(
            titulo_pagina="Cadastrar inovação",
            rotulo_botao="Salvar",
            url_cancelar=reverse("inovacoes:lista"),
            **kwargs,
        )

    def gravar(self, form):
        # INOV-04: o autor vem da sessao, nunca do formulario.
        form.instance.autor = self.request.user
        return super().gravar(form)


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
            return _inovacao_nao_encontrada(request)

    def get_context_data(self, **kwargs):
        # EDEX-03, EDEX-24: as acoes so aparecem para quem pode alterar (AD-009).
        # STAT-01: a ordem do enum ja e a ordem do ciclo.
        return super().get_context_data(
            pode_alterar=self.object.pode_ser_alterada_por(self.request.user),
            etapas=StatusInovacao.choices,
            # STAT-24, STAT-25: uma consulta so, com o responsavel junto (sem N+1).
            mudancas=self.object.mudancas_de_status.select_related("responsavel"),
            **kwargs,
        )


# Sem decorator: o LoginRequiredMiddleware ja nega o anonimo (AD-006, EDEX-26).
class InovacaoUpdateView(AlteracaoDeInovacaoMixin, GravacaoComTituloUnicoMixin, UpdateView):
    """Edicao dos sete campos do cadastro pelo autor ou por um administrador (RF07).

    Sem get_initial(): o formulario parte dos valores salvos (EDEX-02).
    """

    form_class = InovacaoForm
    template_name = "inovacoes/inovacao_form.html"
    # EDEX-05, EDEX-06: sem success_url, o UpdateView volta ao get_absolute_url().
    mensagem_de_sucesso = "Inovação “{titulo}” atualizada com sucesso."

    def gravar(self, form):
        # EDEX-29: o Model.save() faz INSERT quando o UPDATE nao acha a linha.
        # Travar a linha na transacao do mixin impede recriar uma inovacao
        # excluida depois do dispatch().
        if not Inovacao.objects.select_for_update().filter(pk=self.object.pk).exists():
            raise Http404
        return super().gravar(form)

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Http404:
            # EDEX-27, EDEX-29: o 404 da CONS-15, sem gravar nada.
            return _inovacao_nao_encontrada(self.request)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            titulo_pagina="Editar inovação",
            rotulo_botao="Salvar alterações",
            # EDEX-16: cancelar volta ao detalhe sem gravar.
            url_cancelar=self.object.get_absolute_url(),
            **kwargs,
        )


# Sem decorator: o LoginRequiredMiddleware ja nega o anonimo (AD-006, EDEX-26).
class InovacaoDeleteView(AlteracaoDeInovacaoMixin, DeleteView):
    """Confirmacao e exclusao definitiva pelo autor ou por um administrador (RF08, RN12).

    O GET herdado so renderiza inovacao_confirm_delete.html; apagar exige o POST
    da confirmacao (EDEX-36).
    """

    success_url = reverse_lazy("inovacoes:lista")

    def form_valid(self, form):
        # EDEX-40: o titulo e guardado antes, porque o super() apaga a linha.
        titulo = self.object.titulo
        resposta = super().form_valid(form)
        messages.success(self.request, f"Inovação “{titulo}” excluída com sucesso.")
        return resposta


# STAT-10: o GET e o aviso do POST dizem o mesmo texto.
MENSAGEM_ULTIMO_ESTAGIO = (
    "Esta inovação já está em “Disponível para replicação”, o último estágio do ciclo."
)


# Sem decorator: o LoginRequiredMiddleware ja nega o anonimo (AD-006, STAT-23).
class InovacaoStatusView(AlteracaoDeInovacaoMixin, DetailView):
    """Confirmacao e avanco do status um estagio pelo autor ou administrador (RF09, RN03).

    O GET herdado so renderiza a confirmacao e nunca grava (STAT-11).
    """

    template_name = "inovacoes/inovacao_status.html"

    def get_context_data(self, **kwargs):
        # STAT-06, STAT-10: sem proximo, a pagina explica em vez de oferecer o botao.
        return super().get_context_data(
            proximo=self.object.proximo_status,
            mensagem_ultimo_estagio=MENSAGEM_ULTIMO_ESTAGIO,
            **kwargs,
        )

    def post(self, request, *args, **kwargs):
        # O mixin ja negou o terceiro (403) e o id inexistente (404) no dispatch().
        inovacao = self.object
        try:
            mudanca = inovacao.avancar_status(
                por=request.user, status_visto=request.POST.get("status_visto")
            )
        except StatusDesatualizado as recusa:
            # STAT-12, STAT-13: reenvio, duplo clique ou outra pessoa avancou antes.
            atual = StatusInovacao(recusa.status_atual).label
            messages.warning(
                request,
                f"O status desta inovação já foi alterado para “{atual}”. "
                "Confira o status atual antes de avançar.",
            )
        except UltimoEstagioDoCiclo:
            # STAT-10 (POST): o mesmo texto do GET, como aviso.
            messages.warning(request, MENSAGEM_ULTIMO_ESTAGIO)
        except Inovacao.DoesNotExist:
            # STAT-22: apagada entre o dispatch() e a trava; o 404 da CONS-15.
            return _inovacao_nao_encontrada(request)
        else:
            # STAT-16: diz o que mudou e em qual inovacao (RF12).
            messages.success(
                request,
                f"Status da inovação “{inovacao.titulo}” alterado de "
                f"“{mudanca.get_status_anterior_display()}” para "
                f"“{mudanca.get_status_novo_display()}”.",
            )
        return HttpResponseRedirect(inovacao.get_absolute_url())


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
        # CONS-32, CONS-35: pelo GET cru, e nao pelo form, para valer tambem com erro.
        # A busca so com espacos nao conta (CONS-21).
        busca = self.request.GET
        ativos = (
            busca.get("q", "").strip(),
            busca.get("categoria"),
            busca.get("unidade"),
            busca.get("status"),
        )
        return super().get_context_data(form=self.form, filtros_ativos=any(ativos), **kwargs)

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
