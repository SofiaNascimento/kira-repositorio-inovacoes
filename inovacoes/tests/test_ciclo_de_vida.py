"""Testes do historico de status e da regra do ciclo de vida (F5).

O historico precisa valer mesmo quando o codigo grava direto no banco, sem
passar pela tela: as invariantes aqui vem do PostgreSQL (AD-003, AD-011).
"""

from datetime import timedelta
from itertools import product
from unittest import mock

import pytest
from django.contrib import admin
from django.db import IntegrityError, connection
from django.db.models import ProtectedError
from django.test.utils import CaptureQueriesContext
from django.urls import URLResolver, get_resolver
from django.utils import timezone

from contas.models import Usuario
from inovacoes.busca import texto_de_busca
from inovacoes.models import (
    Inovacao,
    MudancaDeStatus,
    StatusDesatualizado,
    StatusInovacao,
    UltimoEstagioDoCiclo,
)

EM_TESTE = StatusInovacao.EM_TESTE
VALIDADA = StatusInovacao.VALIDADA
DISPONIVEL = StatusInovacao.DISPONIVEL_PARA_REPLICACAO

# RN03: as unicas duas transicoes do ciclo.
TRANSICOES_VALIDAS = [(EM_TESTE, VALIDADA), (VALIDADA, DISPONIVEL)]
# Os 9 pares do produto 3x3 menos os 2 validos: pular, voltar, repetir.
TRANSICOES_INVALIDAS = [
    par for par in product(StatusInovacao.values, repeat=2) if par not in TRANSICOES_VALIDAS
]


def _registrar(inovacao, responsavel, anterior=EM_TESTE, novo=VALIDADA):
    return MudancaDeStatus.objects.create(
        inovacao=inovacao, status_anterior=anterior, status_novo=novo, responsavel=responsavel
    )


def test_ha_sete_transicoes_invalidas():
    # Sanidade da parametrizacao: nenhum par fica de fora.
    assert len(TRANSICOES_INVALIDAS) == 7


@pytest.mark.django_db
@pytest.mark.parametrize(("anterior", "novo"), TRANSICOES_VALIDAS)
def test_transicao_valida_e_gravada(criar_inovacao, autor, anterior, novo):
    inovacao = criar_inovacao()
    _registrar(inovacao, autor, anterior, novo)
    registro = MudancaDeStatus.objects.get()
    assert (registro.inovacao, registro.status_anterior, registro.status_novo) == (
        inovacao,
        anterior,
        novo,
    )
    assert registro.responsavel == autor
    assert registro.data is not None


@pytest.mark.django_db
@pytest.mark.parametrize(("anterior", "novo"), TRANSICOES_INVALIDAS)
def test_transicao_invalida_e_recusada_pelo_banco(criar_inovacao, autor, anterior, novo):
    """STAT-31: pular, voltar ou repetir um estagio nao entra no historico."""
    inovacao = criar_inovacao()
    with pytest.raises(IntegrityError, match="mudanca_de_status_transicao_valida"):
        _registrar(inovacao, autor, anterior, novo)


@pytest.mark.django_db
def test_excluir_a_inovacao_apaga_so_o_historico_dela(criar_inovacao, autor):
    """STAT-28: o historico vai junto com a inovacao, e o de outra fica."""
    inovacao = criar_inovacao()
    outra = criar_inovacao(titulo="Outra Inovacao")
    _registrar(inovacao, autor)
    _registrar(inovacao, autor, VALIDADA, DISPONIVEL)
    da_outra = _registrar(outra, autor)

    inovacao.delete()

    assert list(MudancaDeStatus.objects.all()) == [da_outra]


@pytest.mark.django_db
def test_excluir_a_conta_responsavel_e_recusado(criar_inovacao, administrador):
    """STAT-29: a conta que fez a mudanca nao pode ser apagada."""
    registro = _registrar(criar_inovacao(), administrador)
    with pytest.raises(ProtectedError):
        administrador.delete()
    assert MudancaDeStatus.objects.get().pk == registro.pk
    assert MudancaDeStatus.objects.get().responsavel_id == administrador.pk


@pytest.mark.django_db
def test_historico_sai_do_mais_antigo_ao_mais_recente(criar_inovacao, autor):
    """STAT-24: a data manda, mesmo contra a ordem do id."""
    inovacao = criar_inovacao()
    primeiro = _registrar(inovacao, autor)
    segundo = _registrar(inovacao, autor, VALIDADA, DISPONIVEL)
    MudancaDeStatus.objects.filter(pk=primeiro.pk).update(data=segundo.data + timedelta(hours=1))
    assert list(MudancaDeStatus.objects.all()) == [segundo, primeiro]


@pytest.mark.django_db
def test_historico_com_a_mesma_data_sai_na_ordem_do_id(criar_inovacao, autor):
    """STAT-24: mesma data, o id desempata do menor para o maior."""
    inovacao = criar_inovacao()
    primeiro = _registrar(inovacao, autor)
    segundo = _registrar(inovacao, autor, VALIDADA, DISPONIVEL)
    MudancaDeStatus.objects.update(data=primeiro.data)
    assert list(MudancaDeStatus.objects.all()) == [primeiro, segundo]


# --- Inovacao.proximo_status e Inovacao.avancar_status (AD-011) ---


def _status_no_banco(inovacao):
    return Inovacao.objects.values_list("status", flat=True).get(pk=inovacao.pk)


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("status", "proximo"), [(EM_TESTE, VALIDADA), (VALIDADA, DISPONIVEL), (DISPONIVEL, None)]
)
def test_proximo_status_segue_o_ciclo(criar_inovacao, status, proximo):
    """RN03: um estagio por vez; o ultimo nao tem proximo."""
    assert criar_inovacao(status=status).proximo_status == proximo


@pytest.mark.django_db
@pytest.mark.parametrize(("anterior", "novo"), TRANSICOES_VALIDAS)
def test_avancar_status_avanca_um_estagio_e_registra(criar_inovacao, autor, anterior, novo):
    """STAT-07, STAT-08, STAT-14: novo status e um registro completo."""
    inovacao = criar_inovacao(status=anterior)
    antes = timezone.now()

    devolvido = inovacao.avancar_status(por=autor, status_visto=anterior)

    assert _status_no_banco(inovacao) == novo
    registro = MudancaDeStatus.objects.get()
    assert devolvido == registro
    assert registro.inovacao_id == inovacao.pk
    assert (registro.status_anterior, registro.status_novo) == (anterior, novo)
    assert registro.responsavel == autor
    assert antes <= registro.data <= timezone.now()


@pytest.mark.django_db
def test_avancar_no_ultimo_estagio_e_recusado_sem_gravar(criar_inovacao, autor):
    """STAT-10 no modelo: o estagio final nao avanca nem registra."""
    inovacao = criar_inovacao(status=DISPONIVEL)
    with pytest.raises(UltimoEstagioDoCiclo):
        inovacao.avancar_status(por=autor, status_visto=DISPONIVEL)
    assert _status_no_banco(inovacao) == DISPONIVEL
    assert MudancaDeStatus.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize("status_visto", [VALIDADA, None, "APROVADA"])
def test_status_visto_diferente_do_gravado_e_recusado_sem_gravar(
    criar_inovacao, autor, status_visto
):
    """STAT-12: diferente, ausente ou fora do enum; nada muda."""
    inovacao = criar_inovacao()
    with pytest.raises(StatusDesatualizado) as erro:
        inovacao.avancar_status(por=autor, status_visto=status_visto)
    assert erro.value.status_atual == EM_TESTE
    assert _status_no_banco(inovacao) == EM_TESTE
    assert MudancaDeStatus.objects.count() == 0


@pytest.mark.django_db
def test_segundo_avanco_com_o_mesmo_status_visto_e_recusado(criar_inovacao, autor):
    """STAT-13: reenvio da mesma confirmacao avanca um estagio so."""
    inovacao = criar_inovacao()
    inovacao.avancar_status(por=autor, status_visto=EM_TESTE)
    with pytest.raises(StatusDesatualizado) as erro:
        inovacao.avancar_status(por=autor, status_visto=EM_TESTE)
    assert erro.value.status_atual == VALIDADA
    assert _status_no_banco(inovacao) == VALIDADA
    assert MudancaDeStatus.objects.count() == 1


@pytest.mark.django_db
def test_recusa_pelo_status_gravado_e_nao_pelo_da_instancia(criar_inovacao, autor):
    """STAT-13: outra pessoa avancou depois que a instancia foi carregada."""
    inovacao = criar_inovacao()
    Inovacao.objects.filter(pk=inovacao.pk).update(status=VALIDADA)
    assert inovacao.status == EM_TESTE
    with pytest.raises(StatusDesatualizado) as erro:
        inovacao.avancar_status(por=autor, status_visto=EM_TESTE)
    assert erro.value.status_atual == VALIDADA
    assert _status_no_banco(inovacao) == VALIDADA
    assert MudancaDeStatus.objects.count() == 0


@pytest.mark.django_db
def test_avancar_trava_a_linha_ao_ler_o_status(criar_inovacao, autor):
    """STAT-13: o SELECT ... FOR UPDATE serializa dois envios simultaneos."""
    inovacao = criar_inovacao()
    with CaptureQueriesContext(connection) as consultas:
        inovacao.avancar_status(por=autor, status_visto=EM_TESTE)
    leituras = [c["sql"] for c in consultas if c["sql"].startswith("SELECT")]
    assert '"inovacoes_inovacao"."status"' in leituras[0]
    assert leituras[0].endswith("FOR UPDATE")


@pytest.mark.django_db
def test_falha_ao_registrar_desfaz_o_novo_status(criar_inovacao, autor):
    """STAT-15: status e historico na mesma transacao; um nao existe sem o outro."""
    inovacao = criar_inovacao()
    falha = IntegrityError("falha forcada")
    with (
        mock.patch.object(MudancaDeStatus.objects, "create", side_effect=falha),
        pytest.raises(IntegrityError),
    ):
        inovacao.avancar_status(por=autor, status_visto=EM_TESTE)
    assert _status_no_banco(inovacao) == EM_TESTE
    assert MudancaDeStatus.objects.count() == 0


@pytest.mark.django_db
def test_responsavel_e_quem_avanca_e_o_autor_nao_muda(criar_inovacao, autor, administrador):
    """STAT-18: o administrador fica no historico; a autoria continua."""
    inovacao = criar_inovacao()
    inovacao.avancar_status(por=administrador, status_visto=EM_TESTE)
    assert MudancaDeStatus.objects.get().responsavel == administrador
    assert Inovacao.objects.get(pk=inovacao.pk).autor == autor


@pytest.mark.django_db
def test_avancar_inovacao_apagada_levanta_does_not_exist(criar_inovacao, autor):
    """STAT-22: a inovacao sumiu entre carregar e avancar; nada e criado."""
    inovacao = criar_inovacao()
    Inovacao.objects.filter(pk=inovacao.pk).delete()
    with pytest.raises(Inovacao.DoesNotExist):
        inovacao.avancar_status(por=autor, status_visto=EM_TESTE)
    assert Inovacao.objects.count() == 0
    assert MudancaDeStatus.objects.count() == 0


@pytest.mark.django_db
def test_avancar_grava_so_o_status(criar_inovacao, autor):
    """AD-008: o avanco nao reescreve titulo nem texto_busca com a instancia velha."""
    inovacao = criar_inovacao()
    novo_titulo = "Caixa Conferido"
    Inovacao.objects.filter(pk=inovacao.pk).update(
        titulo=novo_titulo,
        texto_busca=texto_de_busca(novo_titulo, inovacao.problema, inovacao.solucao),
    )
    inovacao.avancar_status(por=autor, status_visto=EM_TESTE)
    gravada = Inovacao.objects.get(pk=inovacao.pk)
    assert gravada.status == VALIDADA
    assert gravada.titulo == novo_titulo
    assert gravada.texto_busca == texto_de_busca(novo_titulo, inovacao.problema, inovacao.solucao)


# --- Integridade do ciclo fora da rota de status (STAT-30, STAT-32, STAT-33) ---


def _envio(unidade, categoria, **extra):
    """POST valido do formulario de cadastro e edicao, com campos a mais."""
    return {
        "titulo": "Conciliação de caixa diária",
        "unidade": str(unidade.pk),
        "categoria": str(categoria.pk),
        "problema": "Diferenças de caixa descobertas só no fim do mês.",
        "solucao": "Conferência diária com planilha compartilhada.",
        "resultado": "Diferenças achadas no mesmo dia.",
        "contato": "Ana Souza (ana@x.com)",
        **extra,
    }


def test_cadastro_nasce_em_teste_sem_historico(client, autor, unidade, categoria):
    """STAT-32: nem um status forjado no envio muda o inicio do ciclo."""
    client.force_login(autor)
    resposta = client.post("/inovacoes/nova/", _envio(unidade, categoria, status=DISPONIVEL))
    assert resposta.status_code == 302
    inovacao = Inovacao.objects.get()
    assert inovacao.status == EM_TESTE
    assert MudancaDeStatus.objects.count() == 0


@pytest.mark.parametrize("enviado", [VALIDADA, DISPONIVEL])
def test_edicao_com_status_nao_muda_o_ciclo(
    client, autor, unidade, categoria, criar_inovacao, enviado
):
    """STAT-33 (EDEX-08 estendida ao historico): a edicao grava, o status e o historico nao."""
    inovacao = criar_inovacao()
    client.force_login(autor)
    resposta = client.post(
        f"/inovacoes/{inovacao.pk}/editar/", _envio(unidade, categoria, status=enviado)
    )
    assert resposta.status_code == 302
    gravada = Inovacao.objects.get(pk=inovacao.pk)
    assert gravada.titulo == "Conciliação de caixa diária"
    assert gravada.status == EM_TESTE
    assert MudancaDeStatus.objects.count() == 0


def test_historico_fica_fora_do_admin(client, criar_inovacao, autor):
    """STAT-30, AD-007: nem um administrador superusuario acha tela do historico."""
    registro = _registrar(criar_inovacao(), autor)
    assert MudancaDeStatus not in admin.site._registry
    conta = Usuario.objects.create_superuser(
        username="gil", email="gil@x.com", password="x", perfil=Usuario.Perfil.ADMINISTRADOR
    )
    client.force_login(conta)
    assert client.get("/admin/").status_code == 200
    lista = "/admin/inovacoes/mudancadestatus/"
    for caminho in (lista, f"{lista}{registro.pk}/change/", f"{lista}{registro.pk}/delete/"):
        assert client.get(caminho).status_code == 404
    assert MudancaDeStatus.objects.filter(pk=registro.pk).exists()


def test_nenhuma_rota_de_inovacoes_altera_o_historico():
    """STAT-30: as rotas de inovacoes sao as sete conhecidas e nenhuma serve MudancaDeStatus."""
    (namespace,) = (
        p
        for p in get_resolver().url_patterns
        if isinstance(p, URLResolver) and p.namespace == "inovacoes"
    )
    rotas = {p.name: p.callback.view_class for p in namespace.url_patterns}
    # REAP-03: a F6 acrescenta a sinalizacao de reaproveitamento.
    assert set(rotas) == {
        "lista",
        "nova",
        "detalhe",
        "editar",
        "excluir",
        "status",
        "reaproveitar",
    }
    for view in rotas.values():
        modelos = {getattr(view, "model", None)}
        if getattr(view, "queryset", None) is not None:
            modelos.add(view.queryset.model)
        assert MudancaDeStatus not in modelos, view
