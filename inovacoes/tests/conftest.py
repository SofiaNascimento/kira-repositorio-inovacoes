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


# F4: as duas outras contas da regra de autoria (RN05, AD-009).
@pytest.fixture
def terceiro(db):
    """USUARIO que nao e o autor e nao tem nome: o caso central do RNF07."""
    return Usuario.objects.create_user(username="bruno", email="bruno@x.com")


@pytest.fixture
def administrador(db):
    return Usuario.objects.create_user(
        username="carla", email="carla@x.com", perfil=Usuario.Perfil.ADMINISTRADOR
    )


# AD-009: is_staff e is_superuser nao dao acesso; o perfil e o unico criterio.
@pytest.fixture(params=["terceiro", "staff", "superusuario"])
def nao_autor_usuario(request, db):
    """USUARIO que nao e o autor: sem bandeiras, com is_staff e com is_superuser."""
    if request.param == "terceiro":
        return request.getfixturevalue("terceiro")
    bandeira = "is_staff" if request.param == "staff" else "is_superuser"
    conta = Usuario.objects.create_user(
        username=f"dora_{request.param}", email=f"dora_{request.param}@x.com", **{bandeira: True}
    )
    conta.refresh_from_db()
    assert conta.perfil == Usuario.Perfil.USUARIO
    assert getattr(conta, bandeira) is True
    assert (conta.is_staff, conta.is_superuser) == (
        bandeira == "is_staff",
        bandeira == "is_superuser",
    )
    return conta
