from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.http import Http404, HttpResponseRedirect, QueryDict
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
)

from inovacoes import apresentacao
from inovacoes.forms import BuscaForm, InovacaoForm, ReaproveitamentoForm
from inovacoes.models import (
    MENSAGEM_REAPROVEITAMENTO_STATUS,
    Inovacao,
    StatusDesatualizado,
    StatusInovacao,
    UltimoEstagioDoCiclo,
)

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
        # STAT-01: a ordem do enum ja e a ordem do ciclo. RCON-34: cada etapa vem com a
        # situacao pela posicao do status atual; o template nao compara posicoes.
        atual = StatusInovacao.values.index(self.object.status)
        etapas = [
            (valor, rotulo, "concluida" if i < atual else "atual" if i == atual else "futura")
            for i, (valor, rotulo) in enumerate(StatusInovacao.choices)
        ]
        return super().get_context_data(
            pode_alterar=self.object.pode_ser_alterada_por(self.request.user),
            etapas=etapas,
            # STAT-24, STAT-25, RCON-43 a RCON-45: uma consulta so, com o responsavel junto
            # (sem N+1), avaliada aqui em lista; o cadastro abre a linha do tempo (RCON-36).
            historico=apresentacao.itens_do_historico(
                self.object, list(self.object.mudancas_de_status.select_related("responsavel"))
            ),
            # REAP-18, REAP-43, RCON-35, RCON-36: uma consulta so, com a unidade e quem
            # registrou junto (sem N+1), avaliada aqui em lista.
            reaproveitamentos=list(
                self.object.reaproveitamentos.select_related("unidade", "registrado_por")
            ),
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


# Sem decorator: o LoginRequiredMiddleware ja nega o anonimo (AD-006, REAP-20).
class InovacaoReaproveitarView(FormView):
    """Sinalizacao de que uma unidade reaproveitou a inovacao (RF11, RN09).

    REAP-19: sem AlteracaoDeInovacaoMixin. A sinalizacao nao altera a Inovacao
    (AD-009), entao todo autenticado pode, autor ou nao. O registro nasce so por
    Inovacao.registrar_reaproveitamento (AD-012).
    """

    form_class = ReaproveitamentoForm
    template_name = "inovacoes/inovacao_reaproveitar.html"

    def dispatch(self, request, *args, **kwargs):
        try:
            self.inovacao = Inovacao.objects.select_related("unidade").get(pk=kwargs["pk"])
        except Inovacao.DoesNotExist:
            # REAP-16: o 404 da CONS-15.
            return _inovacao_nao_encontrada(request)
        if not self.inovacao.pode_ser_reaproveitada():
            # REAP-09: GET e POST voltam ao detalhe com o aviso, sem formulario.
            self._avisar_status_indisponivel(self.inovacao.get_status_display())
            return HttpResponseRedirect(self.inovacao.get_absolute_url())
        return super().dispatch(request, *args, **kwargs)

    def _avisar_status_indisponivel(self, rotulo):
        messages.warning(self.request, MENSAGEM_REAPROVEITAMENTO_STATUS.format(status=rotulo))

    # SPEC_DEVIATION: o design acrescenta inovacao aos kwargs do super().
    # Reason: o FormView manda initial e prefix, que a assinatura
    # ReaproveitamentoForm(data=None, *, inovacao) da T3 nao aceita.
    def get_form_kwargs(self):
        dados = self.request.POST if self.request.method == "POST" else None
        return {"data": dados, "inovacao": self.inovacao}

    def form_valid(self, form):
        unidade = form.cleaned_data["unidade"]
        try:
            self.inovacao.registrar_reaproveitamento(unidade=unidade, por=self.request.user)
        except ValidationError as recusa:
            if recusa.code == "status_indisponivel":
                # REAP-09: o status mudou depois do dispatch(); o mesmo aviso e 302.
                messages.warning(self.request, recusa.messages[0])
                return HttpResponseRedirect(self.inovacao.get_absolute_url())
            # REAP-11, REAP-12, REAP-14: erro de campo junto do select, com 200.
            form.add_error("unidade", recusa)
            return self.form_invalid(form)
        except Inovacao.DoesNotExist:
            # REAP-16: apagada entre o dispatch() e a trava; o 404 da CONS-15.
            return _inovacao_nao_encontrada(self.request)
        # REAP-06: diz o que foi registrado, em qual inovacao e por qual unidade (RF12).
        messages.success(
            self.request,
            f"Reaproveitamento da inovação “{self.inovacao.titulo}” pela unidade "
            f"“{unidade.nome}” registrado.",
        )
        # REAP-05: volta ao detalhe.
        return HttpResponseRedirect(self.inovacao.get_absolute_url())

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(inovacao=self.inovacao, **kwargs)
        # REAP-15: sem unidade elegivel, a pagina explica em vez de mostrar o select.
        contexto["sem_elegiveis"] = not contexto["form"].fields["unidade"].queryset.exists()
        return contexto


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
        contexto = super().get_context_data(form=self.form, filtros_ativos=any(ativos), **kwargs)
        # R2: o template so itera; a montagem fica em apresentacao.py (RCON-04 a 08, 18, 20, 22).
        # SPEC_DEVIATION: o design pede etiquetas vazias com o form invalido.
        # Reason: a T12 pede "so as validas" com o form invalido; o cleaned_data guarda so os
        # campos validos, e a RCON-08 so proibe a etiqueta do parametro invalido.
        escolhida = apresentacao.exibicao(busca)
        contexto.update(
            exibicao=escolhida,
            url_cartoes=apresentacao.url_da_lista(busca, exibicao=None),
            url_tabela=apresentacao.url_da_lista(busca, exibicao="tabela"),
            etiquetas=apresentacao.etiquetas(self.form.cleaned_data, busca),
            url_limpar=apresentacao.url_da_lista(
                QueryDict(), exibicao="tabela" if escolhida == "tabela" else None
            ),
            paginas=apresentacao.paginas(contexto["page_obj"]),
        )
        return contexto

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
