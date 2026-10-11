"""Testes e2e da tela de edicao de inovacao (/inovacoes/<id>/editar/)."""

import datetime
import re
from unittest import mock

import pytest
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from contas.models import Usuario
from inovacoes.models import Categoria, Inovacao, StatusInovacao, Unidade

CAMPOS = ["titulo", "unidade", "categoria", "problema", "solucao", "resultado", "contato"]
NEGADO = "Você não tem permissão para alterar esta inovação."
SO_AUTOR = "Só quem cadastrou a inovação ou um administrador pode editá-la ou excluí-la."


def _editar(inovacao):
    return f"/inovacoes/{inovacao.pk}/editar/"


def _entrar(client, conta):
    client.force_login(conta)
    return client


def _formulario(html):
    """O formulario da pagina, sem o cabecalho (que tem o botao "Sair")."""
    return re.search(r"<form[^>]*novalidate[^>]*>(.*?)</form>", html, re.S).group(1)


def _link_cancelar(html):
    links = re.findall(r"<a\b([^>]*)>\s*Cancelar\s*</a>", html)
    assert len(links) == 1, links
    return re.search(r'\bhref="([^"]*)"', links[0]).group(1)


def _afirma_formulario_de_edicao(resposta):
    """EDEX-01: 200, titulo "Editar inovação" e exatamente os sete campos."""
    assert resposta.status_code == 200
    assertTemplateUsed(resposta, "inovacoes/inovacao_form.html")
    html = resposta.content.decode()
    titulo = re.search(r"<title>(.*?)</title>", html, re.S).group(1).strip()
    assert titulo.startswith("Editar inovação")
    assert re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.S) == ["Editar inovação"]
    assert list(resposta.context["form"].fields) == CAMPOS
    nomes = re.findall(r'\bname="([^"]+)"', _formulario(html))
    assert sorted(set(nomes) - {"csrfmiddlewaretoken"}) == sorted(CAMPOS)
    for campo in ["autor", "status", "data_criacao"]:
        assert f'name="{campo}"' not in html


def _afirma_acesso_negado(resposta, inovacao):
    """EDEX-20, EDEX-21: 403 com a pagina propria, os dois textos e o link de volta."""
    assert resposta.status_code == 403
    assertTemplateUsed(resposta, "inovacoes/acesso_negado.html")
    html = resposta.content.decode()
    assert NEGADO in html
    assert SO_AUTOR in html
    links = re.findall(r'<a href="([^"]*)">\s*Voltar para a inovação\s*</a>', html)
    assert links == [f"/inovacoes/{inovacao.pk}/"]


def test_autor_abre_o_formulario_de_edicao_com_os_sete_campos(client, autor, criar_inovacao):
    """EDEX-01: autor USUARIO; o status fica de fora (F5)."""
    inovacao = criar_inovacao()
    resposta = _entrar(client, autor).get(_editar(inovacao))
    _afirma_formulario_de_edicao(resposta)
    assert re.findall(r"<button[^>]*>(.*?)</button>", _formulario(resposta.content.decode())) == [
        "Salvar alterações"
    ]


def test_formulario_vem_preenchido_com_os_valores_salvos(client, autor, criar_inovacao):
    """EDEX-02: inclusive o contato salvo, e nao o pre-preenchimento da INOV-39."""
    inovacao = criar_inovacao(
        resultado="Fechamento em duas horas.", contato="Setor Financeiro (fin@x.com)"
    )
    resposta = _entrar(client, autor).get(_editar(inovacao))
    form = resposta.context["form"]
    assert form.instance.pk == inovacao.pk
    assert {campo: form[campo].value() for campo in CAMPOS} == {
        "titulo": "Controle de Caixa",
        "unidade": inovacao.unidade_id,
        "categoria": inovacao.categoria_id,
        "problema": "Fechamento de caixa manual e demorado.",
        "solucao": "Planilha compartilhada com conferencia diaria.",
        "resultado": "Fechamento em duas horas.",
        "contato": "Setor Financeiro (fin@x.com)",
    }
    html = resposta.content.decode()
    assert 'value="Setor Financeiro (fin@x.com)"' in html
    # O pre-preenchimento da INOV-39 seria "Ana Souza (ana@x.com)" (a ajuda o cita como exemplo).
    assert 'value="Ana Souza (ana@x.com)"' not in html
    assert re.search(rf'<option value="{inovacao.unidade_id}" selected>', html)
    assert re.search(rf'<option value="{inovacao.categoria_id}" selected>', html)


def test_cancelar_leva_ao_detalhe_sem_alterar_a_inovacao(client, autor, criar_inovacao):
    """EDEX-16: link comum, sem confirmacao, para /inovacoes/<id>/."""
    inovacao = criar_inovacao()
    antes = Inovacao.objects.values().get(pk=inovacao.pk)
    logado = _entrar(client, autor)
    href = _link_cancelar(logado.get(_editar(inovacao)).content.decode())
    assert href == f"/inovacoes/{inovacao.pk}/"
    resposta = logado.get(href)
    assert resposta.status_code == 200
    assertTemplateUsed(resposta, "inovacoes/inovacao_detail.html")
    assert Inovacao.objects.values().get(pk=inovacao.pk) == antes


def test_administrador_abre_a_edicao_da_inovacao_de_outro_autor(
    client, administrador, criar_inovacao
):
    """EDEX-17."""
    inovacao = criar_inovacao()
    _afirma_formulario_de_edicao(_entrar(client, administrador).get(_editar(inovacao)))


def test_autor_administrador_abre_a_edicao(client, administrador, criar_inovacao):
    """EDEX-19: o autor com perfil ADMINISTRADOR edita como o autor USUARIO."""
    inovacao = criar_inovacao(autor=administrador)
    _afirma_formulario_de_edicao(_entrar(client, administrador).get(_editar(inovacao)))


def test_terceiro_recebe_403_com_a_pagina_de_acesso_negado(client, terceiro, criar_inovacao):
    """EDEX-20, EDEX-21: USUARIO que nao e o autor, pela barra de endereco."""
    inovacao = criar_inovacao()
    resposta = _entrar(client, terceiro).get(_editar(inovacao))
    _afirma_acesso_negado(resposta, inovacao)
    assert "form" not in resposta.context


def test_administrador_rebaixado_recebe_403_na_requisicao_seguinte(
    client, administrador, criar_inovacao
):
    """EDEX-25: o perfil e lido a cada requisicao, nunca guardado na sessao."""
    inovacao = criar_inovacao()
    logado = _entrar(client, administrador)
    assert logado.get(_editar(inovacao)).status_code == 200
    Usuario.objects.filter(pk=administrador.pk).update(perfil=Usuario.Perfil.USUARIO)
    _afirma_acesso_negado(logado.get(_editar(inovacao)), inovacao)


def test_id_sem_inovacao_responde_404_com_pagina_propria(client, autor):
    """EDEX-27 (GET): o 404 da CONS-15."""
    resposta = _entrar(client, autor).get("/inovacoes/999999/editar/")
    assert resposta.status_code == 404
    assertTemplateUsed(resposta, "inovacoes/inovacao_nao_encontrada.html")
    assert re.search(r"<h1[^>]*>\s*Inovação não encontrada\.\s*</h1>", resposta.content.decode())


@pytest.mark.django_db
def test_anonimo_vai_ao_login_com_next_da_edicao(client, criar_inovacao):
    """EDEX-26 (GET)."""
    inovacao = criar_inovacao()
    caminho = _editar(inovacao)
    resposta = client.get(caminho)
    assertRedirects(resposta, f"/entrar/?next={caminho}", fetch_redirect_response=False)


# --- Gravacao (POST) ----------------------------------------------------------

CAMPOS_DE_TEXTO = ["titulo", "problema", "solucao", "resultado", "contato"]
DATA_ORIGINAL = datetime.datetime(2026, 9, 1, 15, 0, tzinfo=datetime.UTC)


@pytest.fixture
def inovacao(criar_inovacao):
    """Inovacao da Ana com data de criacao fixa, para provar que ela nao muda."""
    criada = criar_inovacao()
    Inovacao.objects.filter(pk=criada.pk).update(data_criacao=DATA_ORIGINAL)
    criada.refresh_from_db()
    return criada


@pytest.fixture
def dados(unidade, categoria):
    """Envio valido com valores diferentes dos salvos em todos os campos de texto."""
    outra_unidade = Unidade.objects.create(nome="Teste Outra Unidade")
    outra_categoria = Categoria.objects.create(nome="Teste Outra Categoria")
    return {
        "titulo": "Conciliação de caixa diária",
        "unidade": str(outra_unidade.pk),
        "categoria": str(outra_categoria.pk),
        "problema": "Diferenças de caixa descobertas só no fim do mês.",
        "solucao": "Conferência diária com planilha compartilhada.",
        "resultado": "Diferenças achadas no mesmo dia.",
        "contato": "Setor Financeiro (fin@x.com)",
    }


def _linha(inovacao):
    """Todos os campos gravados da inovacao, para comparar campo a campo."""
    return Inovacao.objects.values().get(pk=inovacao.pk)


def _regiao_de_status(html):
    inicio = html.index('role="status"')
    return html[inicio : html.index("</div>", inicio)]


def _afirma_gravado(inovacao, dados):
    gravada = Inovacao.objects.get(pk=inovacao.pk)
    for campo in CAMPOS_DE_TEXTO:
        assert getattr(gravada, campo) == dados[campo].strip()
    assert str(gravada.unidade_id) == dados["unidade"]
    assert str(gravada.categoria_id) == dados["categoria"]
    return gravada


def test_envio_valido_atualiza_a_mesma_inovacao_sem_espacos_nas_pontas(
    client, autor, inovacao, dados
):
    """EDEX-04: mesma linha, valores aparados, nenhuma inovacao nova."""
    enviados = {k: f"  {v}  " if k in CAMPOS_DE_TEXTO else v for k, v in dados.items()}
    _entrar(client, autor).post(_editar(inovacao), enviados)
    assert Inovacao.objects.count() == 1
    _afirma_gravado(inovacao, dados)


def test_envio_valido_redireciona_ao_detalhe(client, autor, inovacao, dados):
    """EDEX-05."""
    resposta = _entrar(client, autor).post(_editar(inovacao), dados)
    assertRedirects(resposta, f"/inovacoes/{inovacao.pk}/", fetch_redirect_response=False)


def test_edicao_bem_sucedida_confirma_com_o_titulo_salvo(client, autor, inovacao, dados):
    """EDEX-06: no detalhe, dentro do role=status, com o titulo salvo (aparado)."""
    dados["titulo"] = "  Conciliação de caixa diária  "
    resposta = _entrar(client, autor).post(_editar(inovacao), dados, follow=True)
    assert resposta.redirect_chain == [(f"/inovacoes/{inovacao.pk}/", 302)]
    regiao = _regiao_de_status(resposta.content.decode())
    assert "Inovação “Conciliação de caixa diária” atualizada com sucesso." in regiao


def test_mensagem_da_edicao_nao_reaparece_ao_recarregar(client, autor, inovacao, dados):
    """EDEX-07."""
    logado = _entrar(client, autor)
    primeira = logado.post(_editar(inovacao), dados, follow=True)
    assert "atualizada com sucesso" in primeira.content.decode()
    html = logado.get(f"/inovacoes/{inovacao.pk}/").content.decode()
    assert "atualizada com sucesso" not in html


def test_autor_status_e_data_forjados_na_edicao_sao_ignorados(
    client, autor, terceiro, inovacao, dados
):
    """EDEX-08."""
    dados.update(
        {
            "autor": str(terceiro.pk),
            "status": StatusInovacao.VALIDADA,
            "data_criacao": "2020-01-01 10:00",
        }
    )
    resposta = _entrar(client, autor).post(_editar(inovacao), dados)
    assert resposta.status_code == 302
    gravada = _afirma_gravado(inovacao, dados)
    assert gravada.autor_id == autor.pk
    assert gravada.status == StatusInovacao.EM_TESTE
    assert gravada.data_criacao == DATA_ORIGINAL


def test_administrador_edita_a_inovacao_de_outro_autor_e_mantem_autor_e_data(
    client, administrador, autor, inovacao, dados
):
    """EDEX-18: aplica EDEX-04 a EDEX-06 e o detalhe segue com o autor e a data originais."""
    resposta = _entrar(client, administrador).post(_editar(inovacao), dados, follow=True)
    assert resposta.redirect_chain == [(f"/inovacoes/{inovacao.pk}/", 302)]
    gravada = _afirma_gravado(inovacao, dados)
    assert gravada.autor_id == autor.pk
    assert gravada.data_criacao == DATA_ORIGINAL
    html = resposta.content.decode()
    assert "Inovação “Conciliação de caixa diária” atualizada com sucesso." in _regiao_de_status(
        html
    )
    # 15:00 UTC de 01/09 e 12:00 de 01/09 em America/Sao_Paulo.
    assert "Cadastrada por Ana Souza em 01/09/2026" in html


def test_autor_administrador_grava_a_edicao(client, administrador, criar_inovacao, dados):
    """EDEX-19: o autor ADMINISTRADOR grava como o autor USUARIO."""
    inovacao = criar_inovacao(autor=administrador)
    resposta = _entrar(client, administrador).post(_editar(inovacao), dados)
    assertRedirects(resposta, f"/inovacoes/{inovacao.pk}/", fetch_redirect_response=False)
    assert _afirma_gravado(inovacao, dados).autor_id == administrador.pk


def test_duas_edicoes_em_sequencia_mantem_a_ultima(client, autor, administrador, inovacao, dados):
    """EDEX-15: a ultima gravacao vence; nao ha checagem de versao."""
    _entrar(client, autor).post(_editar(inovacao), dados)
    segunda = dict(dados, titulo="Caixa conferido toda tarde", problema="Outro problema.")
    _entrar(client, administrador).post(_editar(inovacao), segunda)
    _afirma_gravado(inovacao, segunda)


def test_terceiro_que_envia_a_edicao_recebe_403_e_nada_muda(client, terceiro, inovacao, dados):
    """EDEX-22: o POST forjado de um USUARIO que nao e o autor nao grava nenhum campo."""
    antes = _linha(inovacao)
    resposta = _entrar(client, terceiro).post(_editar(inovacao), dados)
    _afirma_acesso_negado(resposta, inovacao)
    assert _linha(inovacao) == antes
    assert Inovacao.objects.count() == 1


def test_anonimo_que_envia_a_edicao_vai_ao_login_e_nada_muda(client, inovacao, dados):
    """EDEX-26 (POST)."""
    antes = _linha(inovacao)
    caminho = _editar(inovacao)
    resposta = client.post(caminho, dados)
    assertRedirects(resposta, f"/entrar/?next={caminho}", fetch_redirect_response=False)
    assert _linha(inovacao) == antes


# --- Validacao e unicidade de titulo (T6) --------------------------------------

RESUMO = "Não foi possível salvar a inovação. Corrija os campos indicados."
MENSAGEM_DUPLICADO = "Já existe uma inovação com este título nesta unidade. Escolha outro título."


def _trecho_do_alerta(html):
    inicio = html.index('role="alert"')
    return html[inicio : html.index("</div>", inicio)]


def _valor_do_input(html, campo):
    tag = html[html.rindex("<", 0, html.index(f'id="id_{campo}"')) :]
    tag = tag[: tag.index(">")]
    return re.search(r'\bvalue="([^"]*)"', tag).group(1)


def _mensagem_do_campo(html, campo):
    erro = html[html.index(f'id="id_{campo}_error"') :]
    return erro[: erro.index("</ul>")]


def test_edicao_com_titulo_e_problema_vazios_mostra_as_mensagens_e_preserva_o_resto(
    client, autor, inovacao, dados
):
    """EDEX-09, EDEX-10: mensagens da INOV-09, resumo da INOV-30, valores enviados
    de volta (INOV-11) e nada gravado."""
    antes = _linha(inovacao)
    dados.update({"titulo": "", "problema": ""})
    resposta = _entrar(client, autor).post(_editar(inovacao), dados)
    assert resposta.status_code == 200
    assert resposta.context["form"].errors == {
        "titulo": ["Informe o título da inovação."],
        "problema": ["Descreva o problema ou dor."],
    }
    html = resposta.content.decode()
    assert "Informe o título da inovação." in _mensagem_do_campo(html, "titulo")
    assert "Descreva o problema ou dor." in _mensagem_do_campo(html, "problema")
    assert RESUMO in _trecho_do_alerta(html)
    assert html.index('role="alert"') < html.index('id="id_titulo"')
    assert _valor_do_input(html, "contato") == dados["contato"]
    assert f'<option value="{dados["unidade"]}" selected>' in html
    assert f'<option value="{dados["categoria"]}" selected>' in html
    for campo in ["solucao", "resultado"]:
        assert f">\n{dados[campo]}</textarea>" in html
    assert _linha(inovacao) == antes


def test_edicao_com_unidade_inexistente_e_recusada(client, autor, inovacao, dados):
    """EDEX-09 (INOV-17): POST adulterado com unidade fora da lista."""
    antes = _linha(inovacao)
    dados["unidade"] = "999999"
    resposta = _entrar(client, autor).post(_editar(inovacao), dados)
    assert resposta.status_code == 200
    assert resposta.context["form"].errors == {"unidade": ["Selecione uma unidade da lista."]}
    assert _linha(inovacao) == antes


def test_edicao_com_titulo_longo_demais_e_recusada(client, autor, inovacao, dados):
    """EDEX-09 (INOV-12): 151 caracteres no titulo."""
    antes = _linha(inovacao)
    dados["titulo"] = "x" * 151
    resposta = _entrar(client, autor).post(_editar(inovacao), dados)
    assert resposta.status_code == 200
    assert resposta.context["form"].errors == {
        "titulo": ["Use no máximo 150 caracteres (você digitou 151)."]
    }
    assert _linha(inovacao) == antes


@pytest.mark.parametrize("titulo", ["Controle de Caixa", "CONTROLE DE CAIXA"])
def test_salvar_com_o_proprio_titulo_e_aceito(client, autor, inovacao, unidade, dados, titulo):
    """EDEX-12: o mesmo titulo, com ou sem mudanca de caixa, na mesma unidade."""
    dados.update({"titulo": titulo, "unidade": str(unidade.pk)})
    resposta = _entrar(client, autor).post(_editar(inovacao), dados)
    assertRedirects(resposta, f"/inovacoes/{inovacao.pk}/", fetch_redirect_response=False)
    assert Inovacao.objects.get(pk=inovacao.pk).titulo == titulo


def test_titulo_de_outra_inovacao_da_unidade_e_recusado(
    client, autor, inovacao, unidade, criar_inovacao, dados
):
    """EDEX-13: caixa diferente nao escapa da unicidade."""
    criar_inovacao(titulo="Planilha de Compras")
    antes = _linha(inovacao)
    dados.update({"titulo": "planilha de COMPRAS", "unidade": str(unidade.pk)})
    resposta = _entrar(client, autor).post(_editar(inovacao), dados)
    assert resposta.status_code == 200
    assert resposta.context["form"].errors == {"titulo": [MENSAGEM_DUPLICADO]}
    assert MENSAGEM_DUPLICADO in _mensagem_do_campo(resposta.content.decode(), "titulo")
    assert _linha(inovacao) == antes


def test_titulo_de_inovacao_de_outra_unidade_e_aceito(
    client, autor, inovacao, criar_inovacao, dados
):
    """INOV-24 na edicao (por EDEX-13): a unicidade e por unidade."""
    sede = Unidade.objects.get(nome="Sede")
    criar_inovacao(titulo="Planilha de Compras", unidade=sede)
    dados["titulo"] = "Planilha de Compras"
    resposta = _entrar(client, autor).post(_editar(inovacao), dados)
    assertRedirects(resposta, f"/inovacoes/{inovacao.pk}/", fetch_redirect_response=False)
    assert Inovacao.objects.get(pk=inovacao.pk).titulo == "Planilha de Compras"


def test_titulo_que_difere_so_no_acento_e_aceito(
    client, autor, inovacao, unidade, criar_inovacao, dados
):
    """INOV-27 na edicao (por EDEX-13): acentos contam."""
    criar_inovacao(titulo="Solução de Caixa")
    dados.update({"titulo": "Solucao de Caixa", "unidade": str(unidade.pk)})
    resposta = _entrar(client, autor).post(_editar(inovacao), dados)
    assertRedirects(resposta, f"/inovacoes/{inovacao.pk}/", fetch_redirect_response=False)
    assert Inovacao.objects.get(pk=inovacao.pk).titulo == "Solucao de Caixa"


def test_corrida_no_titulo_da_edicao_responde_erro_no_campo_e_nao_500(
    client, autor, inovacao, unidade, criar_inovacao, dados
):
    """EDEX-14: as duas gravacoes passam pela validacao antes de qualquer uma gravar.

    Neutralizar a validacao reproduz a janela, como nos testes da INOV-25: o
    save() bate na constraint real do PostgreSQL.
    """
    criar_inovacao(titulo="Planilha de Compras")
    antes = _linha(inovacao)
    dados.update({"titulo": "Planilha de Compras", "unidade": str(unidade.pk)})
    with mock.patch.object(Inovacao, "validate_constraints", lambda self, exclude=None: None):
        resposta = _entrar(client, autor).post(_editar(inovacao), dados)
    assert resposta.status_code == 200
    assert resposta.context["form"].errors == {"titulo": [MENSAGEM_DUPLICADO]}
    assert RESUMO in _trecho_do_alerta(resposta.content.decode())
    assert _linha(inovacao) == antes
    assert Inovacao.objects.filter(titulo="Planilha de Compras").count() == 1


def _titulos_da_busca(client, termo):
    resposta = client.get("/inovacoes/", {"q": termo})
    assert resposta.status_code == 200
    return [i.titulo for i in resposta.context["inovacoes"]]


def test_busca_acha_pelo_texto_novo_e_nao_pelo_texto_substituido(client, autor, inovacao, dados):
    """EDEX-11: a edicao passa pelo Inovacao.save(), que refaz o texto de busca (AD-008)."""
    logado = _entrar(client, autor)
    assert _titulos_da_busca(logado, "manual") == ["Controle de Caixa"]
    dados["problema"] = "Divergências descobertas tarde demais."
    logado.post(_editar(inovacao), dados)
    assert _titulos_da_busca(logado, "divergencias") == [dados["titulo"]]
    assert _titulos_da_busca(logado, "manual") == []
