"""Testes de integracao do InovacaoQuerySet (consulta da F3)."""

import datetime

from inovacoes.models import Inovacao


def _forcar_data(inovacao, data):
    # data_criacao e auto_now_add: so update() direto permite escolher o valor.
    Inovacao.objects.filter(pk=inovacao.pk).update(data_criacao=data)


def _utc(dia, hora=12):
    return datetime.datetime(2026, 9, dia, hora, 0, tzinfo=datetime.UTC)


def test_listagem_ordena_por_data_de_criacao_decrescente(criar_inovacao):
    """CONS-02."""
    antiga = criar_inovacao(titulo="Antiga")
    recente = criar_inovacao(titulo="Recente")
    meio = criar_inovacao(titulo="Meio")
    _forcar_data(antiga, _utc(1))
    _forcar_data(meio, _utc(10))
    _forcar_data(recente, _utc(20))

    ids = [i.pk for i in Inovacao.objects.para_listagem()]

    assert ids == [recente.pk, meio.pk, antiga.pk]


def test_listagem_desempata_datas_iguais_por_id_decrescente(criar_inovacao):
    """CONS-02: para a mesma data de criacao, o id maior vem primeiro."""
    primeira = criar_inovacao(titulo="Primeira")
    segunda = criar_inovacao(titulo="Segunda")
    outra = criar_inovacao(titulo="Outra data")
    _forcar_data(primeira, _utc(5))
    _forcar_data(segunda, _utc(5))
    _forcar_data(outra, _utc(1))

    ids = [i.pk for i in Inovacao.objects.para_listagem()]

    assert segunda.pk > primeira.pk
    assert ids == [segunda.pk, primeira.pk, outra.pk]


def test_listagem_le_unidade_e_categoria_em_uma_consulta(criar_inovacao, django_assert_num_queries):
    """CONS-48 (base): sem N+1 ao ler unidade e categoria de cada linha."""
    for numero in range(3):
        criar_inovacao(titulo=f"Inovacao {numero}")

    with django_assert_num_queries(1):
        nomes = [(i.unidade.nome, i.categoria.nome) for i in Inovacao.objects.para_listagem()]

    assert nomes == [("Teste Unidade", "Teste Categoria")] * 3
