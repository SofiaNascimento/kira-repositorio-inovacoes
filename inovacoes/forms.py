from django import forms
from django.core.validators import MaxLengthValidator

from inovacoes.models import Inovacao

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
        error_messages = {
            "titulo": {
                "required": "Informe o título da inovação.",
                "max_length": MENSAGEM_TAMANHO,
            },
            "unidade": {"required": "Selecione a unidade de origem."},
            "categoria": {"required": "Selecione a categoria."},
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
        for nome in ("problema", "solucao", "resultado"):
            campo = self.fields[nome]
            campo.max_length = LIMITE_TEXTO_LONGO
            campo.validators.append(MaxLengthValidator(LIMITE_TEXTO_LONGO))
            campo.widget.attrs["maxlength"] = str(LIMITE_TEXTO_LONGO)
