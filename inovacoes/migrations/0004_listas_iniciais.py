from django.db import migrations

# INOV-18. As unidades sao provisorias: o administrador as renomeia quando a
# lista real existir.
CATEGORIAS = ["Atendimento interno", "Compras", "Financeiro", "RH", "TI interno"]
UNIDADES = ["Filial Leste", "Filial Norte", "Filial Oeste", "Filial Sul", "Sede"]


def criar_listas_iniciais(apps, schema_editor):
    Categoria = apps.get_model("inovacoes", "Categoria")
    Unidade = apps.get_model("inovacoes", "Unidade")
    for nome in CATEGORIAS:
        Categoria.objects.get_or_create(nome=nome)
    for nome in UNIDADES:
        Unidade.objects.get_or_create(nome=nome)


def apagar_listas_iniciais(apps, schema_editor):
    apps.get_model("inovacoes", "Categoria").objects.filter(nome__in=CATEGORIAS).delete()
    apps.get_model("inovacoes", "Unidade").objects.filter(nome__in=UNIDADES).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("inovacoes", "0003_titulo_unico_por_unidade"),
    ]

    operations = [
        migrations.RunPython(criar_listas_iniciais, apagar_listas_iniciais),
    ]
