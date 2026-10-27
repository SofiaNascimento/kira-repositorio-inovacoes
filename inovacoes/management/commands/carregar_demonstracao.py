"""Carrega o acervo realista de 500 inovacoes (acervo-realista; RNF08).

O conteudo sai de inovacoes.acervo, deterministico. Idempotente: so cria os pares
(titulo, unidade) ausentes, e as contas dos autores nao duplicam.
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from inovacoes import acervo
from inovacoes.models import (
    Categoria,
    Inovacao,
    MudancaDeStatus,
    Reaproveitamento,
    StatusInovacao,
    Unidade,
)

MINIMO_DE_VALORES = 5


class Command(BaseCommand):
    help = f"Cria as {acervo.TOTAL} inovações do acervo de demonstração, sem duplicar."

    @transaction.atomic
    def handle(self, *args, **options):
        unidades = list(Unidade.objects.order_by("nome"))
        categorias = {c.nome: c for c in Categoria.objects.all()}
        if len(unidades) < MINIMO_DE_VALORES or len(categorias) < MINIMO_DE_VALORES:
            raise CommandError(
                f"São necessárias ao menos {MINIMO_DE_VALORES} unidades e "
                f"{MINIMO_DE_VALORES} categorias para distribuir a demonstração."
            )
        registros = acervo.montar_registros([u.nome for u in unidades])
        faltando = {r["categoria"] for r in registros} - set(categorias)
        if faltando:
            raise CommandError(f"Categorias ausentes no banco: {', '.join(sorted(faltando))}.")

        autores = self._autores()
        existentes = set(Inovacao.objects.values_list("titulo", "unidade_id"))
        agora = timezone.now()
        novas = 0
        for r in registros:
            unidade = unidades[r["unidade"]]
            if (r["titulo"], unidade.pk) in existentes:
                continue
            autor = autores[r["autor"]]
            tempo = acervo.linha_do_tempo(r, agora, len(unidades))
            # save() um a um: bulk_create pularia o texto de busca (AD-008). Nasce
            # "Em teste" e chega ao status do registro pelo avancar_status (AD-011).
            inovacao = Inovacao(
                titulo=r["titulo"],
                unidade=unidade,
                categoria=categorias[r["categoria"]],
                status=StatusInovacao.EM_TESTE,
                problema=r["problema"],
                solucao=r["solucao"],
                resultado=r["resultado"],
                contato=r["contato"],
                autor=autor,
            )
            inovacao.save()
            # As datas sao auto_now_add: retroagidas depois, fora dos campos da busca.
            Inovacao.objects.filter(pk=inovacao.pk).update(data_criacao=tempo["criacao"])
            for data in tempo["mudancas"]:
                mudanca = inovacao.avancar_status(por=autor, status_visto=inovacao.status)
                MudancaDeStatus.objects.filter(pk=mudanca.pk).update(data=data)
            # AD-012: o reuso nasce pelo metodo do modelo, sinalizado por alguem da unidade.
            for u, data, quem in tempo["reusos"]:
                reuso = inovacao.registrar_reaproveitamento(unidade=unidades[u], por=autores[quem])
                Reaproveitamento.objects.filter(pk=reuso.pk).update(data=data)
            novas += 1

        self.stdout.write(f"{novas} inovações de demonstração criadas ({acervo.TOTAL} no total).")

    def _autores(self):
        """As contas dos AUTORES, criadas sem senha utilizavel na primeira execucao."""
        Usuario = get_user_model()
        contas = {}
        for nome, sobrenome in acervo.AUTORES:
            login = acervo.username(nome, sobrenome)
            conta, criada = Usuario.objects.get_or_create(
                username=login,
                defaults={
                    "first_name": nome,
                    "last_name": sobrenome,
                    "email": f"{login}@{acervo.DOMINIO_DOS_AUTORES}",
                    "perfil": "USUARIO",
                },
            )
            if criada:
                conta.set_unusable_password()
                conta.save()
            contas[(nome, sobrenome)] = conta
        return contas
