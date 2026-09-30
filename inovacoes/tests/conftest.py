import pytest

from contas.models import Usuario
from inovacoes.models import Categoria, Inovacao, Unidade


@pytest.fixture
def autor(db):
    return Usuario.objects.create_user(
        username="ana", email="ana@x.com", first_name="Ana", last_name="Souza"
    )


# Nomes proprios de teste: a carga inicial ja cria "Sede", "Compras" etc.
@pytest.fixture
def unidade(db):
    return Unidade.objects.create(nome="Teste Unidade")


@pytest.fixture
def categoria(db):
    return Categoria.objects.create(nome="Teste Categoria")


@pytest.fixture
def criar_inovacao(autor, unidade, categoria):
    """Grava direto no banco, sem formulario; cada campo pode ser trocado."""

    def criar(**campos):
        dados = {
            "titulo": "Controle de Caixa",
            "unidade": unidade,
            "categoria": categoria,
            "problema": "Fechamento de caixa manual e demorado.",
            "solucao": "Planilha compartilhada com conferencia diaria.",
            "contato": "Ana Souza (ana@x.com)",
            "autor": autor,
        }
        dados.update(campos)
        return Inovacao.objects.create(**dados)

    return criar
