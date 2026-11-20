"""Testes de integracao do InovacaoQuerySet (consulta da F3)."""

import datetime

import pytest

from inovacoes.models import Categoria, Inovacao, Reaproveitamento, StatusInovacao, Unidade


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


# R2: resumo e contagem de reaproveitamentos no cartao (RCON-13, RCON-14, RCON-16).


def _reaproveitar(inovacao, vezes):
    """Grava direto, so para preparar a contagem; o caminho da aplicacao e o metodo (AD-012)."""
    for numero in range(vezes):
        unidade = Unidade.objects.create(nome=f"Teste Reuso {inovacao.pk}-{numero}")
        Reaproveitamento.objects.create(
            inovacao=inovacao, unidade=unidade, registrado_por=inovacao.autor
        )


@pytest.fixture
def tres_com_reusos(criar_inovacao):
    """Tres inovacoes da mesma pagina com 0, 1 e 3 reaproveitamentos, da mais antiga a recente.

    A sem reuso fica noutra categoria, para o filtro ter o que tirar.
    """
    outra = Categoria.objects.create(nome="Teste Outra Categoria")
    nenhum = criar_inovacao(titulo="Nenhum", problema="Problema sem reuso.", categoria=outra)
    um = criar_inovacao(titulo="Um", problema="Problema com um reuso.")
    tres = criar_inovacao(titulo="Tres", problema="Problema com tres reusos.")
    _forcar_data(nenhum, _utc(1))
    _forcar_data(um, _utc(2))
    _forcar_data(tres, _utc(3))
    _reaproveitar(um, 1)
    _reaproveitar(tres, 3)
    return nenhum, um, tres


def test_listagem_conta_os_reaproveitamentos_de_cada_inovacao(tres_com_reusos):
    """RCON-14: a contagem de cada item da pagina e 0, 1 e 3, sem misturar inovacoes."""
    nenhum, um, tres = tres_com_reusos

    contagens = {i.pk: i.total_reaproveitamentos for i in Inovacao.objects.para_listagem()}

    assert contagens == {nenhum.pk: 0, um.pk: 1, tres.pk: 3}


def test_listagem_le_resumo_e_contagem_sem_consulta_nova(
    tres_com_reusos, django_assert_num_queries
):
    """RCON-13, RCON-16: problema e contagem vem na mesma consulta da pagina."""
    with django_assert_num_queries(1):
        itens = list(Inovacao.objects.para_listagem())

    with django_assert_num_queries(0):
        lidos = [(i.problema, i.total_reaproveitamentos) for i in itens]

    assert lidos == [
        ("Problema com tres reusos.", 3),
        ("Problema com um reuso.", 1),
        ("Problema sem reuso.", 0),
    ]


def test_busca_e_filtro_sobre_a_listagem_anotada_seguem_em_uma_consulta(
    tres_com_reusos, categoria, django_assert_num_queries
):
    """RCON-16, CONS-48: buscar().filtrar() encadeia sobre a anotacao, numa consulta so."""
    _, um, tres = tres_com_reusos

    with django_assert_num_queries(1):
        achadas = [
            (i.pk, i.problema, i.total_reaproveitamentos)
            for i in Inovacao.objects.para_listagem().buscar("reuso").filtrar(categoria=categoria)
        ]

    # "reuso" casa as tres; o filtro de categoria tira a sem reuso.
    assert achadas == [
        (tres.pk, "Problema com tres reusos.", 3),
        (um.pk, "Problema com um reuso.", 1),
    ]


def test_contagem_nao_duplica_nem_reordena_a_listagem(tres_com_reusos):
    """CONS-02 com a anotacao: cada inovacao uma vez, mais recentes primeiro."""
    nenhum, um, tres = tres_com_reusos

    ids = [i.pk for i in Inovacao.objects.para_listagem()]

    assert ids == [tres.pk, um.pk, nenhum.pk]
    assert Inovacao.objects.para_listagem().count() == 3


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


# Filtros (CONS-27, CONS-28) sobre as listas da carga inicial (0004).


@pytest.fixture
def tres_inovacoes(criar_inovacao):
    """Financeiro/Sede/Validada, Financeiro/Filial Norte/Em teste, RH/Sede/Validada."""
    financeiro = Categoria.objects.get(nome="Financeiro")
    rh = Categoria.objects.get(nome="RH")
    sede = Unidade.objects.get(nome="Sede")
    norte = Unidade.objects.get(nome="Filial Norte")
    primeira = criar_inovacao(
        **{**NEUTRO, "titulo": "Conciliação bancária"},
        categoria=financeiro,
        unidade=sede,
        status=StatusInovacao.VALIDADA,
    )
    segunda = criar_inovacao(
        **{**NEUTRO, "titulo": "Reembolso de despesas"},
        categoria=financeiro,
        unidade=norte,
        status=StatusInovacao.EM_TESTE,
    )
    terceira = criar_inovacao(
        **{**NEUTRO, "titulo": "Admissão digital"},
        categoria=rh,
        unidade=sede,
        status=StatusInovacao.VALIDADA,
    )
    return {
        "inovacoes": (primeira, segunda, terceira),
        "financeiro": financeiro,
        "sede": sede,
    }


def _pks(queryset):
    return set(queryset.values_list("pk", flat=True))


@pytest.mark.parametrize(
    ("filtro", "esperadas"),
    [("categoria", (0, 1)), ("unidade", (0, 2)), ("status", (0, 2))],
)
def test_um_filtro_lista_so_as_inovacoes_com_aquele_valor(tres_inovacoes, filtro, esperadas):
    """CONS-27: Financeiro -> 1a e 2a; Sede -> 1a e 3a; Validada -> 1a e 3a."""
    valor = {
        "categoria": tres_inovacoes["financeiro"],
        "unidade": tres_inovacoes["sede"],
        "status": StatusInovacao.VALIDADA,
    }[filtro]
    inovacoes = tres_inovacoes["inovacoes"]

    resultado = _pks(Inovacao.objects.filtrar(**{filtro: valor}))

    assert resultado == {inovacoes[i].pk for i in esperadas}


def test_categoria_e_unidade_juntas_restringem_as_duas(tres_inovacoes):
    """CONS-28: Financeiro + Sede -> so a primeira."""
    resultado = Inovacao.objects.filtrar(
        categoria=tres_inovacoes["financeiro"], unidade=tres_inovacoes["sede"]
    )
    assert _pks(resultado) == {tres_inovacoes["inovacoes"][0].pk}


def test_os_tres_filtros_juntos(tres_inovacoes):
    """CONS-28: Financeiro + Sede + Validada -> so a primeira."""
    resultado = Inovacao.objects.filtrar(
        categoria=tres_inovacoes["financeiro"],
        unidade=tres_inovacoes["sede"],
        status=StatusInovacao.VALIDADA,
    )
    assert _pks(resultado) == {tres_inovacoes["inovacoes"][0].pk}


@pytest.mark.parametrize(("termo", "esperadas"), [("conciliacao", {0}), ("admissao", set())])
def test_os_tres_filtros_com_a_busca(tres_inovacoes, termo, esperadas):
    """CONS-28: a palavra da primeira acha a primeira; a da terceira, que e de RH, nada."""
    resultado = Inovacao.objects.buscar(termo).filtrar(
        categoria=tres_inovacoes["financeiro"],
        unidade=tres_inovacoes["sede"],
        status=StatusInovacao.VALIDADA,
    )
    assert _pks(resultado) == {tres_inovacoes["inovacoes"][i].pk for i in esperadas}


def test_unidade_status_e_busca_juntos(tres_inovacoes):
    """CONS-28 (teste independente da spec): Sede + Validada + palavra da terceira -> a terceira."""
    resultado = Inovacao.objects.filtrar(
        unidade=tres_inovacoes["sede"], status=StatusInovacao.VALIDADA
    ).buscar("admissao")
    assert _pks(resultado) == {tres_inovacoes["inovacoes"][2].pk}


def test_filtrar_sem_valores_nao_restringe(tres_inovacoes):
    """CONS-27, CONS-28: categoria None, unidade None e status "" sao ignorados."""
    resultado = Inovacao.objects.filtrar(categoria=None, unidade=None, status="")
    assert _pks(resultado) == {i.pk for i in tres_inovacoes["inovacoes"]}
    assert _pks(Inovacao.objects.filtrar()) == {i.pk for i in tres_inovacoes["inovacoes"]}
