"""Testes do comando carregar_demonstracao com o acervo realista (ACER-01 a ACER-20).

Integracao: o comando grava 500 inovacoes, uma a uma, pelo save(). Supersede os
testes da CONS-44 e da CONS-45.
"""

import re
from collections import Counter
from datetime import timedelta
from io import StringIO
from unittest import mock

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils import timezone

from contas.models import Usuario
from inovacoes.busca import normalizar, texto_de_busca
from inovacoes.models import (
    Categoria,
    Inovacao,
    MudancaDeStatus,
    Reaproveitamento,
    StatusInovacao,
    Unidade,
)
from inovacoes.tests.visibilidade import exibido

TOTAL = 500
VETADAS = ("demonstracao", "lorem", "ficticio", "teste de carga", "exemplo")
CAMPOS_VISIVEIS = ("titulo", "problema", "solucao", "resultado", "contato")


def _carregar():
    saida = StringIO()
    call_command("carregar_demonstracao", stdout=saida)
    return saida.getvalue()


@pytest.fixture
def saida_da_carga(db):
    return _carregar()


@pytest.fixture
def carga_cronometrada(db):
    """A carga entre dois instantes: as datas geradas tem de cair dentro da janela."""
    antes = timezone.now()
    _carregar()
    return antes, timezone.now()


@pytest.fixture
def carga_espionada(db):
    """A carga com os dois metodos do modelo espionados (AD-011, AD-012)."""
    with (
        mock.patch.object(
            Inovacao, "avancar_status", autospec=True, side_effect=Inovacao.avancar_status
        ) as avancar,
        mock.patch.object(
            Inovacao,
            "registrar_reaproveitamento",
            autospec=True,
            side_effect=Inovacao.registrar_reaproveitamento,
        ) as registrar,
    ):
        _carregar()
    return avancar, registrar


def _autores_da_carga():
    return Usuario.objects.filter(inovacoes__isnull=False).distinct()


def test_cria_500_inovacoes_com_pares_titulo_unidade_unicos(saida_da_carga):
    """ACER-01."""
    pares = list(Inovacao.objects.values_list("titulo", "unidade_id"))
    assert len(pares) == TOTAL
    assert len(set(pares)) == TOTAL


def test_ao_menos_90_titulos_e_nenhum_em_mais_de_5_inovacoes(saida_da_carga):
    """ACER-02."""
    por_titulo = Counter(Inovacao.objects.values_list("titulo", flat=True))
    assert len(por_titulo) >= 90
    assert max(por_titulo.values()) <= 5


def test_problemas_e_solucoes_sao_todos_diferentes(saida_da_carga):
    """ACER-03."""
    assert Inovacao.objects.values("problema").distinct().count() == TOTAL
    assert Inovacao.objects.values("solucao").distinct().count() == TOTAL


def test_nenhum_texto_visivel_tem_marca_de_dado_de_teste(saida_da_carga):
    """ACER-04: comparacao sem acento e sem caixa."""
    achados = [
        (inovacao["titulo"], campo, vetada)
        for inovacao in Inovacao.objects.values(*CAMPOS_VISIVEIS)
        for campo in CAMPOS_VISIVEIS
        for vetada in VETADAS
        if vetada in normalizar(inovacao[campo])
    ]
    assert achados == []


def test_validadas_e_disponiveis_tem_resultado(saida_da_carga):
    """ACER-05."""
    com_resultado_exigido = Inovacao.objects.exclude(status=StatusInovacao.EM_TESTE)
    assert com_resultado_exigido.exists()
    assert [i.titulo for i in com_resultado_exigido if not i.resultado.strip()] == []


def test_contato_e_setor_unidade_e_ramal_da_propria_unidade(saida_da_carga):
    """ACER-06: "<setor>, <unidade> — ramal <4 digitos>"."""
    for inovacao in Inovacao.objects.select_related("unidade"):
        padrao = rf"[^,]+, {re.escape(inovacao.unidade.nome)} — ramal \d{{4}}"
        assert re.fullmatch(padrao, inovacao.contato), inovacao.contato


def test_cada_unidade_categoria_e_status_aparece_em_pelo_menos_20(saida_da_carga):
    """ACER-07."""
    por_unidade = Counter(Inovacao.objects.values_list("unidade__nome", flat=True))
    por_categoria = Counter(Inovacao.objects.values_list("categoria__nome", flat=True))
    por_status = Counter(Inovacao.objects.values_list("status", flat=True))
    assert set(por_unidade) == set(Unidade.objects.values_list("nome", flat=True))
    assert set(por_categoria) == set(Categoria.objects.values_list("nome", flat=True))
    assert set(por_status) == set(StatusInovacao.values)
    assert min(por_unidade.values()) >= 20
    assert min(por_categoria.values()) >= 20
    assert min(por_status.values()) >= 20


def test_busca_sem_acento_acha_o_mesmo_que_com_acento(saida_da_carga):
    """ACER-08."""
    com_acento = set(Inovacao.objects.buscar("conciliação"))
    assert com_acento
    assert set(Inovacao.objects.buscar("conciliacao")) == com_acento


def test_toda_inovacao_criada_tem_o_texto_de_busca_do_save(saida_da_carga):
    """AD-008: a carga passa pelo save(), entao a coluna deriva dos tres campos."""
    for inovacao in Inovacao.objects.all():
        esperado = texto_de_busca(inovacao.titulo, inovacao.problema, inovacao.solucao)
        assert inovacao.texto_busca == esperado


def test_15_autores_colaboradores_sem_senha_e_todos_com_inovacao(saida_da_carga):
    """ACER-09."""
    autores = list(_autores_da_carga())
    assert len(autores) == 15
    for conta in autores:
        assert conta.first_name.strip() and conta.last_name.strip()
        assert conta.perfil == "USUARIO"
        assert conta.has_usable_password() is False
        assert conta.email.endswith("@acervo.invalid")
    assert Usuario.objects.filter(email__endswith="@acervo.invalid").count() == 15


def test_nao_cria_nem_usa_a_conta_demo(saida_da_carga):
    """ACER-10."""
    assert not Usuario.objects.filter(username="demo").exists()
    assert not Inovacao.objects.filter(autor__username="demo").exists()


def test_detalhe_mostra_o_nome_completo_de_quem_cadastrou(saida_da_carga, client, terceiro):
    """ACER-11: "Cadastrada por <nome completo>", visivel (L-028, L-030)."""
    inovacao = Inovacao.objects.select_related("autor").order_by("titulo", "pk").first()
    client.force_login(terceiro)
    html = exibido(client.get(inovacao.get_absolute_url()).content.decode())
    assert f"Cadastrada por {inovacao.autor.get_full_name()} em" in html
    assert inovacao.autor.get_full_name() == (
        f"{inovacao.autor.first_name} {inovacao.autor.last_name}"
    )


def test_mensagem_final_conta_as_criadas_e_o_total(saida_da_carga):
    """ACER-19."""
    assert saida_da_carga.strip() == "500 inovações de demonstração criadas (500 no total)."


@pytest.mark.django_db
@pytest.mark.parametrize("modelo", [Unidade, Categoria])
def test_com_menos_de_5_unidades_ou_categorias_para_com_erro_sem_gravar_nada(modelo):
    """ACER-20: nem inovacao nem conta."""
    contas_antes = Usuario.objects.count()
    modelo.objects.get(nome="RH" if modelo is Categoria else "Sede").delete()
    with pytest.raises(CommandError):
        _carregar()
    assert Inovacao.objects.count() == 0
    assert Usuario.objects.count() == contas_antes


def test_cadastros_nos_540_dias_antes_da_carga_em_ao_menos_12_meses(carga_cronometrada):
    """ACER-12."""
    antes, depois = carga_cronometrada
    datas = list(Inovacao.objects.values_list("data_criacao", flat=True))
    assert all(antes - timedelta(days=540) <= d <= depois for d in datas)
    meses = {(d.year, d.month) for d in (timezone.localtime(x) for x in datas)}
    assert len(meses) >= 12


def test_historico_tem_uma_mudanca_por_estagio_avancado(saida_da_carga):
    """ACER-13."""
    esperado = {
        StatusInovacao.EM_TESTE: [],
        StatusInovacao.VALIDADA: [(StatusInovacao.EM_TESTE, StatusInovacao.VALIDADA)],
        StatusInovacao.DISPONIVEL_PARA_REPLICACAO: [
            (StatusInovacao.EM_TESTE, StatusInovacao.VALIDADA),
            (StatusInovacao.VALIDADA, StatusInovacao.DISPONIVEL_PARA_REPLICACAO),
        ],
    }
    for inovacao in Inovacao.objects.prefetch_related("mudancas_de_status"):
        transicoes = [(m.status_anterior, m.status_novo) for m in inovacao.mudancas_de_status.all()]
        assert transicoes == esperado[inovacao.status], inovacao.titulo


def test_mudancas_pelo_avancar_status_do_autor_em_ordem_e_ate_a_carga(carga_espionada):
    """ACER-14."""
    avancar, _ = carga_espionada
    assert MudancaDeStatus.objects.exists()
    assert avancar.call_count == MudancaDeStatus.objects.count()
    agora = timezone.now()
    for inovacao in Inovacao.objects.prefetch_related("mudancas_de_status"):
        anterior = inovacao.data_criacao
        for mudanca in inovacao.mudancas_de_status.all():
            assert mudanca.responsavel_id == inovacao.autor_id
            assert anterior < mudanca.data <= agora
            anterior = mudanca.data


def test_reaproveitamentos_pelo_metodo_em_disponiveis_e_fora_da_origem(carga_espionada):
    """ACER-15."""
    _, registrar = carga_espionada
    reusos = Reaproveitamento.objects.select_related("inovacao")
    assert reusos.count() >= 60
    assert registrar.call_count == reusos.count()
    for reuso in reusos:
        assert reuso.inovacao.status == StatusInovacao.DISPONIVEL_PARA_REPLICACAO
        assert reuso.unidade_id != reuso.inovacao.unidade_id
    assert reusos.values("inovacao").distinct().count() >= 30


def test_reaproveitamento_depois_de_ficar_disponivel_e_ate_a_carga(carga_cronometrada):
    """ACER-16."""
    _, depois = carga_cronometrada
    for reuso in Reaproveitamento.objects.select_related("inovacao"):
        disponivel = reuso.inovacao.mudancas_de_status.get(
            status_novo=StatusInovacao.DISPONIVEL_PARA_REPLICACAO
        )
        assert disponivel.data < reuso.data <= depois
