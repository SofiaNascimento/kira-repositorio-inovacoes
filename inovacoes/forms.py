from django import forms
from django.core.validators import MaxLengthValidator

from inovacoes.models import Categoria, Inovacao, StatusInovacao, Unidade

# INOV-12: titulo e contato herdam 150 do model; os textos longos ganham um
# teto no form. TextField nao impoe max_length, e o form e o unico caminho de
# escrita da Inovacao na F2.
LIMITE_TEXTO_LONGO = 5000
MENSAGEM_TAMANHO = "Use no máximo %(limit_value)d caracteres (você digitou %(show_value)d)."


class InovacaoForm(forms.ModelForm):
    """Cadastro de inovacao (RF02) com as mensagens do RF13.

    Autor, status e data de criacao ficam fora de Meta.fields: valores
    forjados no POST nem sao lidos (INOV-06).
    """

    label_suffix = ""

    class Meta:
        model = Inovacao
        fields = ["titulo", "unidade", "categoria", "problema", "solucao", "resultado", "contato"]
        # INOV-32: a obrigatoriedade vai no texto do rotulo, nao so na cor.
        labels = {
            "titulo": "Título (obrigatório)",
            "unidade": "Unidade de origem (obrigatório)",
            "categoria": "Categoria (obrigatório)",
            "problema": "Problema ou dor (obrigatório)",
            "solucao": "Solução aplicada (obrigatório)",
            "resultado": "Resultado ou impacto",
            "contato": "Contato responsável (obrigatório)",
        }
        # INOV-41 (RF15): uma frase com exemplo por campo.
        help_texts = {
            "titulo": "Nome curto da solução. Ex.: Conciliação bancária automática",
            "unidade": "Unidade onde a solução foi aplicada. Ex.: Sede",
            "categoria": "Área de back office da solução. Ex.: Financeiro",
            "problema": (
                "O que dava errado antes. Ex.: A conciliação era manual e levava dois dias por mês."
            ),
            "solucao": (
                "O que foi feito e como. Ex.: Um script cruza o extrato com os lançamentos."
            ),
            "resultado": "O que mudou depois. Ex.: O fechamento passou a levar duas horas.",
            "contato": "Quem responde pela solução. Ex.: Ana Souza (ana@x.com)",
        }
        error_messages = {
            "titulo": {
                "required": "Informe o título da inovação.",
                "max_length": MENSAGEM_TAMANHO,
            },
            "unidade": {
                "required": "Selecione a unidade de origem.",
                "invalid_choice": "Selecione uma unidade da lista.",
            },
            "categoria": {
                "required": "Selecione a categoria.",
                "invalid_choice": "Selecione uma categoria da lista.",
            },
            "problema": {
                "required": "Descreva o problema ou dor.",
                "max_length": MENSAGEM_TAMANHO,
            },
            "solucao": {
                "required": "Descreva a solução aplicada.",
                "max_length": MENSAGEM_TAMANHO,
            },
            "resultado": {"max_length": MENSAGEM_TAMANHO},
            "contato": {
                "required": "Informe o contato responsável.",
                "max_length": MENSAGEM_TAMANHO,
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # INOV-15: o ModelChoiceField so aceita pk do queryset, que vem em
        # ordem alfabetica pela Meta.ordering das listas.
        for nome in ("unidade", "categoria"):
            self.fields[nome].empty_label = "Selecione…"
        # A ajuda vai abaixo do controle (INOV-41); o padrao do Django a poe acima.
        for campo in self.fields.values():
            campo.template_name = "inovacoes/campo.html"
        for nome in ("problema", "solucao", "resultado"):
            campo = self.fields[nome]
            campo.max_length = LIMITE_TEXTO_LONGO
            campo.validators.append(MaxLengthValidator(LIMITE_TEXTO_LONGO))
            campo.widget.attrs["maxlength"] = str(LIMITE_TEXTO_LONGO)


class BuscaForm(forms.Form):
    """Parametros GET da listagem: busca, categoria, unidade e status (RF05, RF06).

    Sempre vinculado ao request.GET: repopula os controles (CONS-25, CONS-29) e
    recusa valor inexistente em vez de ignora-lo (CONS-30).
    """

    q = forms.CharField(
        label="Buscar",
        required=False,
        max_length=100,
        strip=True,
        widget=forms.SearchInput,
        help_text="Procura em título, problema e solução. Ex.: planilha conciliação",
        error_messages={"max_length": MENSAGEM_TAMANHO},
    )
    categoria = forms.ModelChoiceField(
        Categoria.objects.all(),
        label="Categoria",
        required=False,
        empty_label="Todas as categorias",
        help_text="Área de back office. Ex.: Financeiro",
        error_messages={"invalid_choice": "Selecione uma categoria da lista."},
    )
    unidade = forms.ModelChoiceField(
        Unidade.objects.all(),
        label="Unidade",
        required=False,
        empty_label="Todas as unidades",
        help_text="Sede ou filial que criou a solução. Ex.: Filial Norte",
        error_messages={"invalid_choice": "Selecione uma unidade da lista."},
    )
    status = forms.ChoiceField(
        label="Status",
        required=False,
        choices=[("", "Todos os status"), *StatusInovacao.choices],
        help_text="Estágio da solução. Ex.: Disponível para replicação",
        error_messages={"invalid_choice": "Selecione um status da lista."},
    )

    def __init__(self, *args, **kwargs):
        # SPEC_DEVIATION: o design pede `label_suffix = ""` como atributo de classe.
        # Reason: o Form.__init__ o sobrescreve com ":"; so o argumento do __init__ vale.
        kwargs.setdefault("label_suffix", "")
        super().__init__(*args, **kwargs)
        # A ajuda vai abaixo do controle (CONS-52); o padrao do Django a poe acima.
        for campo in self.fields.values():
            campo.template_name = "inovacoes/campo.html"
