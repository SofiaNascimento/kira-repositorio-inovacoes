"""Pecas de formulario da §6 v2 da design-spec (GEST-68).

Servem aos formularios novos (contas e senhas da gestao por unidade) e ao
redesign futuro dos formularios de inovacao, que hoje seguem com o
inovacoes/campo.html (INOV-41).
"""

from functools import cached_property
from pathlib import Path

import django.forms
from django.conf import settings
from django.forms import BoundField
from django.forms.renderers import DjangoTemplates

TEMPLATE_DO_CAMPO = "paginas/campo.html"


class RenderizadorV2(DjangoTemplates):
    """Renderizador de formulario que acha tambem a pasta templates/ do projeto.

    O padrao do Django so le os templates das apps e os dele: o
    paginas/campo.html, ao lado da paginas/trilha.html, ficaria de fora. Trocar
    o FORM_RENDERER do projeto mudaria todos os formularios; este vale so para
    quem usa o FormularioV2Mixin.
    """

    @cached_property
    def engine(self):
        return self.backend(
            {
                "APP_DIRS": True,
                "DIRS": [
                    Path(django.forms.__file__).parent / "templates",
                    Path(settings.BASE_DIR) / "templates",
                ],
                "NAME": "formularios_v2",
                "OPTIONS": {},
            }
        )


class CampoV2(BoundField):
    """BoundField com o aria-describedby da §6 v2: o erro antes da ajuda.

    O Django poe a ajuda antes do erro; quem usa leitor de tela precisa ouvir
    primeiro o que corrigir.
    """

    @property
    def aria_describedby(self):
        if self.field.widget.attrs.get("aria-describedby"):
            return None
        ids = []
        if self.auto_id and not self.is_hidden:
            if self.errors:
                ids.append(f"{self.auto_id}_error")
            if self.help_text:
                ids.append(f"{self.auto_id}_helptext")
        return " ".join(ids)


class FormularioV2Mixin:
    """Campos no template da §6 v2, rotulo sem dois-pontos e o resumo de erros.

    Vai antes da classe de formulario do Django na lista de bases.
    """

    bound_field_class = CampoV2
    default_renderer = RenderizadorV2()

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("label_suffix", "")
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.template_name = TEMPLATE_DO_CAMPO

    @property
    def campos_com_erro(self):
        """Os campos visiveis com erro, na ordem do formulario (resumo de erros)."""
        return [campo for campo in self if campo.errors and not campo.is_hidden]
