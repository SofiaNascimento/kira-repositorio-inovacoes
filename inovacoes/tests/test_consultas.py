"""Testes de integracao do InovacaoQuerySet (consulta da F3)."""

import datetime

import pytest

from inovacoes.models import Categoria, Inovacao, Unidade


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


# Busca por palavras (CONS-19 a CONS-23). Os textos padrao do conftest falam de
# caixa e planilha; os testes partem de NEUTRO, sem nenhuma palavra buscada.

NEUTRO = {"titulo": "Rotina de arquivo", "problema": "Papelada.", "solucao": "Pastas etiquetadas."}


def _achadas(termo):
    return set(Inovacao.objects.buscar(termo).values_list("pk", flat=True))


def test_busca_exige_todas_as_palavras_em_qualquer_dos_tres_campos(criar_inovacao):
    """CONS-19: cada palavra pode estar num campo diferente; todas precisam aparecer."""
    as_duas = criar_inovacao(
        **{**NEUTRO, "titulo": "Conciliação Bancária", "problema": "Planilha manual de extrato."}
    )
    criar_inovacao(**{**NEUTRO, "titulo": "Conciliação de cartões", "problema": "Extrato."})
    criar_inovacao(**{**NEUTRO, "titulo": "Controle de estoque", "problema": "Planilha."})

    assert _achadas("conciliacao planilha") == {as_duas.pk}


@pytest.mark.parametrize("campo", ["titulo", "problema", "solucao"])
def test_busca_procura_em_titulo_problema_e_solucao(criar_inovacao, campo):
    """CONS-19: os tres campos de texto da busca."""
    alvo = criar_inovacao(**{**NEUTRO, campo: "Uso de planilha compartilhada"})
    criar_inovacao(titulo="Outra rotina", problema=NEUTRO["problema"], solucao=NEUTRO["solucao"])

    assert _achadas("planilha") == {alvo.pk}


def test_busca_casa_trecho_de_palavra(criar_inovacao):
    """CONS-19: a palavra aparece como trecho, e nao so como palavra inteira."""
    alvo = criar_inovacao(**{**NEUTRO, "titulo": "Fechamento de Caixa"})
    criar_inovacao(**NEUTRO)

    assert _achadas("caix") == {alvo.pk}


@pytest.mark.parametrize(
    ("termo", "titulo"),
    [("SOLUÇÃO", "Nova solucao de pagamento"), ("solucao", "Nova Solução de pagamento")],
)
def test_busca_ignora_caixa_e_acento_no_termo_e_no_texto(criar_inovacao, termo, titulo):
    """CONS-20."""
    alvo = criar_inovacao(**{**NEUTRO, "titulo": titulo})
    criar_inovacao(**NEUTRO)

    assert _achadas(termo) == {alvo.pk}


@pytest.mark.parametrize("termo", [None, "", "   "])
def test_busca_em_branco_nao_filtra(criar_inovacao, termo):
    """CONS-21."""
    pks = {criar_inovacao(titulo=f"Inovacao {n}").pk for n in range(3)}

    assert _achadas(termo) == pks


@pytest.mark.parametrize("onde", ["resultado", "contato", "categoria", "unidade"])
def test_palavra_so_fora_dos_tres_campos_nao_acha(criar_inovacao, onde):
    """CONS-22: resultado, contato, categoria e unidade ficam fora da busca."""
    campos = {
        "resultado": {"resultado": "Zeladoria em dia."},
        "contato": {"contato": "Zeladoria (zeladoria@x.com)"},
        "categoria": {"categoria": Categoria.objects.create(nome="Zeladoria")},
        "unidade": {"unidade": Unidade.objects.create(nome="Zeladoria Central")},
    }[onde]
    inovacao = criar_inovacao(**NEUTRO, **campos)

    assert _achadas("arquivo") == {inovacao.pk}  # a inovacao e buscavel pelo titulo
    assert _achadas("zeladoria") == set()


@pytest.mark.parametrize(
    ("termo", "com_o_literal", "sem_o_literal"),
    [
        ("100%", "Meta de 100% de acerto", "Lote de 1000 itens"),
        ("a_b", "Campo a_b do relatorio", "Campo axb do relatorio"),
        ("c:\\temp", "Pasta c:\\temp do servidor", "Pasta c:temp do servidor"),
    ],
)
def test_curingas_do_like_valem_como_texto(criar_inovacao, termo, com_o_literal, sem_o_literal):
    """CONS-23: %, _ e \\ casam literalmente."""
    alvo = criar_inovacao(**{**NEUTRO, "titulo": com_o_literal})
    criar_inovacao(**{**NEUTRO, "titulo": sem_o_literal})

    assert _achadas(termo) == {alvo.pk}
