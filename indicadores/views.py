from django.views.generic import TemplateView

from indicadores.graficos import Grafico, barras
from inovacoes.models import Categoria, Inovacao, Reaproveitamento, Unidade


class PainelView(TemplateView):
    """Painel de indicadores do RF10: so le, a cada requisicao (REAP-38, REAP-39).

    Sem decorator: o LoginRequiredMiddleware protege a rota (AD-006, REAP-40).
    """

    template_name = "indicadores/painel.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        total_inovacoes = Inovacao.objects.count()
        contexto["total_inovacoes"] = total_inovacoes
        contexto["total_reaproveitamentos"] = Reaproveitamento.objects.count()
        # REAP-37: sem inovacao, nem tabelas nem graficos; as distribuicoes nem sao consultadas.
        if total_inovacoes:
            categorias = list(Categoria.objects.com_total_de_inovacoes())
            unidades = list(Unidade.objects.com_indicadores())
            contexto["categorias"] = categorias
            contexto["unidades"] = unidades
            contexto["graficos"] = [
                Grafico.de(
                    "grafico-categorias",
                    "Inovações por categoria",
                    barras(categorias, "total"),
                ),
                Grafico.de(
                    "grafico-unidades-origem",
                    "Inovações de origem por unidade",
                    barras(unidades, "inovacoes_de_origem"),
                ),
                Grafico.de(
                    "grafico-unidades-reaproveitamentos",
                    "Reaproveitamentos feitos por unidade",
                    barras(unidades, "reaproveitamentos_feitos"),
                ),
            ]
        return contexto
