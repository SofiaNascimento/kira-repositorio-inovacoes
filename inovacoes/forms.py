from django import forms

from inovacoes.models import Inovacao


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
            "titulo": {"required": "Informe o título da inovação."},
            "unidade": {"required": "Selecione a unidade de origem."},
            "categoria": {"required": "Selecione a categoria."},
            "problema": {"required": "Descreva o problema ou dor."},
            "solucao": {"required": "Descreva a solução aplicada."},
            "contato": {"required": "Informe o contato responsável."},
        }
