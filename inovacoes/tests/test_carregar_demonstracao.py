"""Testes do comando carregar_demonstracao (CONS-44, CONS-45).

Integracao: o comando grava 500 inovacoes, uma a uma, pelo save().
"""

from collections import Counter
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from contas.models import Usuario
from inovacoes.busca import texto_de_busca
from inovacoes.models import Categoria, Inovacao, StatusInovacao, Unidade

TITULOS = [f"Demonstração {i:03d}" for i in range(1, 501)]


def _carregar():
    saida = StringIO()
    call_command("carregar_demonstracao", stdout=saida)
    return saida.getvalue()


@pytest.fixture
def saida_da_carga(db):
    return _carregar()


def test_cria_as_500_inovacoes_da_conta_demo_sem_senha_utilizavel(saida_da_carga):
    """CONS-44: titulos 001 a 500, autora a conta demo, perfil USUARIO."""
    assert sorted(Inovacao.objects.values_list("titulo", flat=True)) == TITULOS
    demo = Usuario.objects.get(username="demo")
    assert demo.email == "demo@demonstracao.invalid"
    assert demo.perfil == "USUARIO"
    assert demo.has_usable_password() is False
    assert Inovacao.objects.exclude(autor=demo).count() == 0


def test_mensagem_final_conta_as_criadas_e_o_total(saida_da_carga):
    """CONS-44: "N inovações de demonstração criadas (500 no total)."."""
    assert saida_da_carga.strip() == "500 inovações de demonstração criadas (500 no total)."


def test_cada_unidade_categoria_e_status_aparece_em_pelo_menos_20(saida_da_carga):
    """CONS-44."""
    por_unidade = Counter(Inovacao.objects.values_list("unidade__nome", flat=True))
    por_categoria = Counter(Inovacao.objects.values_list("categoria__nome", flat=True))
    por_status = Counter(Inovacao.objects.values_list("status", flat=True))
    assert set(por_unidade) == set(Unidade.objects.values_list("nome", flat=True))
    assert set(por_categoria) == set(Categoria.objects.values_list("nome", flat=True))
    assert set(por_status) == set(StatusInovacao.values)
    assert min(por_unidade.values()) >= 20
    assert min(por_categoria.values()) >= 20
    assert min(por_status.values()) >= 20


def test_toda_inovacao_criada_tem_o_texto_de_busca_do_save(saida_da_carga):
    """AD-008: a carga passa pelo save(), entao a coluna deriva dos tres campos."""
    for inovacao in Inovacao.objects.all():
        esperado = texto_de_busca(inovacao.titulo, inovacao.problema, inovacao.solucao)
        assert inovacao.texto_busca == esperado
    assert Inovacao.objects.buscar("demonstracao 042").count() == 1


def test_textos_sao_variados_e_tem_palavras_acentuadas_achadas_sem_acento(saida_da_carga):
    """CONS-44 (textos variados): a busca sem acento acha o vocabulario com acento."""
    assert len(set(Inovacao.objects.values_list("problema", flat=True))) >= 50
    com_acento = Inovacao.objects.buscar("conciliação")
    assert com_acento.count() >= 1
    assert set(com_acento) == set(Inovacao.objects.buscar("conciliacao"))


def test_segunda_execucao_nao_duplica_inovacoes_nem_a_conta_demo(saida_da_carga):
    """CONS-45."""
    saida = _carregar()
    assert "0 inovações de demonstração criadas" in saida
    assert Inovacao.objects.count() == 500
    assert Usuario.objects.filter(username="demo").count() == 1


def test_execucao_repetida_recria_so_os_ausentes_com_o_mesmo_conteudo(saida_da_carga):
    """CONS-45: termina com 500; o titulo apagado volta igual (carga reproduzivel)."""
    alvo = Inovacao.objects.get(titulo="Demonstração 042")
    antes = (alvo.problema, alvo.solucao, alvo.unidade_id, alvo.categoria_id, alvo.status)
    Inovacao.objects.filter(titulo__in=["Demonstração 042", "Demonstração 300"]).delete()
    saida = _carregar()
    assert saida.strip() == "2 inovações de demonstração criadas (500 no total)."
    assert sorted(Inovacao.objects.values_list("titulo", flat=True)) == TITULOS
    novo = Inovacao.objects.get(titulo="Demonstração 042")
    assert (novo.problema, novo.solucao, novo.unidade_id, novo.categoria_id, novo.status) == antes


@pytest.mark.django_db
@pytest.mark.parametrize("modelo", [Unidade, Categoria])
def test_com_menos_de_5_unidades_ou_categorias_para_com_erro_sem_gravar_nada(modelo):
    """CONS-44: sem 5 valores nao ha como garantir 20 por valor."""
    modelo.objects.get(nome="RH" if modelo is Categoria else "Sede").delete()
    with pytest.raises(CommandError):
        _carregar()
    assert Inovacao.objects.count() == 0
    assert not Usuario.objects.filter(username="demo").exists()
