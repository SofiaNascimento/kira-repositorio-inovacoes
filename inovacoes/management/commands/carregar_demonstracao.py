"""Carrega o conjunto de 500 inovacoes de demonstracao do RNF08 (CONS-44, CONS-45).

Reproduzivel: unidade, categoria e status saem do numero da inovacao e os
textos de um Random semeado por ele. Idempotente: so cria os titulos ausentes.
"""

import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from inovacoes.models import Categoria, Inovacao, StatusInovacao, Unidade

TOTAL = 500
MINIMO_DE_VALORES = 5

# Vocabulario de back office, com palavras acentuadas para exercitar a busca sem acento.
VOCABULARIO = (
    "conciliação",
    "aprovação",
    "planilha",
    "orçamento",
    "fornecedor",
    "requisição",
    "relatório",
    "pagamento",
    "contratação",
    "admissão",
    "férias",
    "inventário",
    "cadastro",
    "chamado",
    "automação",
    "prestação de contas",
)


class Command(BaseCommand):
    help = f"Cria {TOTAL} inovações de demonstração da conta demo, sem duplicar."

    @transaction.atomic
    def handle(self, *args, **options):
        unidades = list(Unidade.objects.all())
        categorias = list(Categoria.objects.all())
        if len(unidades) < MINIMO_DE_VALORES or len(categorias) < MINIMO_DE_VALORES:
            raise CommandError(
                f"São necessárias ao menos {MINIMO_DE_VALORES} unidades e "
                f"{MINIMO_DE_VALORES} categorias para distribuir a demonstração."
            )

        demo, criada = get_user_model().objects.get_or_create(
            username="demo",
            defaults={"email": "demo@demonstracao.invalid", "perfil": "USUARIO"},
        )
        if criada:
            demo.set_unusable_password()
            demo.save()

        existentes = set(Inovacao.objects.filter(autor=demo).values_list("titulo", flat=True))
        novas = 0
        for i in range(1, TOTAL + 1):
            titulo = f"Demonstração {i:03d}"
            if titulo in existentes:
                continue
            a, b, c, d = random.Random(i).sample(VOCABULARIO, 4)
            # save() um a um: bulk_create pularia o texto de busca (AD-008).
            Inovacao(
                titulo=titulo,
                unidade=unidades[i % 5],
                categoria=categorias[(i // 5) % 5],
                status=StatusInovacao.values[i % 3],
                problema=f"O processo de {a} e {b} é manual e gera retrabalho em {c}.",
                solucao=f"Automação de {a} com conferência diária de {d}.",
                contato="Equipe de demonstração (demo@demonstracao.invalid)",
                autor=demo,
            ).save()
            novas += 1

        self.stdout.write(f"{novas} inovações de demonstração criadas ({TOTAL} no total).")
