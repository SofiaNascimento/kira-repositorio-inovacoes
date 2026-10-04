import unicodedata

from django.db import migrations

# AD-008: preenche texto_busca das inovacoes gravadas antes da 0005.
#
# Copia local da regra de inovacoes.busca, de proposito: uma migration precisa
# reproduzir para sempre o que fazia quando foi escrita, e importar o modulo
# vivo faria esta migration mudar junto com ele. O teste em
# inovacoes/tests/test_migracoes.py compara o resultado com a regra atual, e
# quebra se as duas divergirem.


def _normalizar(texto):
    decomposto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in decomposto if not unicodedata.combining(c)).casefold()


def _texto_de_busca(titulo, problema, solucao):
    return "\n".join(_normalizar(campo) for campo in (titulo, problema, solucao))


def preencher(apps, schema_editor):
    # O model historico nao tem o save() da AD-008: o valor e calculado aqui.
    Inovacao = apps.get_model("inovacoes", "Inovacao")
    for inovacao in Inovacao.objects.only("id", "titulo", "problema", "solucao").iterator():
        inovacao.texto_busca = _texto_de_busca(inovacao.titulo, inovacao.problema, inovacao.solucao)
        inovacao.save(update_fields=["texto_busca"])


class Migration(migrations.Migration):
    dependencies = [
        ("inovacoes", "0005_inovacao_texto_busca"),
    ]

    operations = [
        migrations.RunPython(preencher, migrations.RunPython.noop),
    ]
