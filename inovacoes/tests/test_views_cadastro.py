"""Testes e2e da tela de cadastro de inovacao (/inovacoes/nova/)."""

import re
from unittest import mock

import pytest
from django.utils import timezone
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from contas.models import Usuario
from inovacoes.models import Inovacao, StatusInovacao, Unidade

NOVA = "/inovacoes/nova/"
CAMPOS = ["titulo", "unidade", "categoria", "problema", "solucao", "resultado", "contato"]


@pytest.fixture
def logado(client, autor):
    client.force_login(autor)
    return client


@pytest.fixture
def dados(unidade, categoria):
    return {
        "titulo": "Conciliação bancária automática",
        "unidade": str(unidade.pk),
        "categoria": str(categoria.pk),
        "problema": "Conciliação manual levava dois dias por mês.",
        "solucao": "Script que cruza o extrato com os lançamentos.",
        "resultado": "Fechamento em duas horas.",
        "contato": "Ana Souza (ana@x.com)",
    }


def test_formulario_abre_com_os_sete_campos_editaveis(logado):
    """INOV-01."""
    resposta = logado.get(NOVA)
    assert resposta.status_code == 200
    assert list(resposta.context["form"].fields) == CAMPOS
    html = resposta.content.decode()
    for campo in CAMPOS:
        assert f'name="{campo}"' in html
    for campo in ["autor", "status", "data_criacao"]:
        assert f'name="{campo}"' not in html


def test_envio_valido_grava_uma_inovacao_com_os_valores_sem_espacos(logado, dados):
    """INOV-02."""
    enviados = {k: f"  {v}  " if k not in ("unidade", "categoria") else v for k, v in dados.items()}
    logado.post(NOVA, enviados)
    assert Inovacao.objects.count() == 1
    inovacao = Inovacao.objects.get()
    for campo in ["titulo", "problema", "solucao", "resultado", "contato"]:
        assert getattr(inovacao, campo) == dados[campo]
    assert str(inovacao.unidade_id) == dados["unidade"]
    assert str(inovacao.categoria_id) == dados["categoria"]


def test_envio_valido_redireciona_ao_detalhe_da_nova_inovacao(logado, dados):
    """INOV-03, alterado pela CONS-49: redirect ao detalhe apos o POST; recarregar nao reenvia."""
    resposta = logado.post(NOVA, dados)
    assertRedirects(
        resposta, f"/inovacoes/{Inovacao.objects.get().pk}/", fetch_redirect_response=False
    )


def test_autor_e_a_conta_logada(logado, dados, autor):
    """INOV-04."""
    logado.post(NOVA, dados)
    assert Inovacao.objects.get().autor == autor


@pytest.mark.django_db
def test_autor_e_quem_enviou_e_nao_outra_conta_do_banco(client, dados):
    """INOV-04: com contas criadas antes e depois, o autor continua sendo a
    conta logada, nao a mais antiga nem a mais nova."""
    antiga = Usuario.objects.create_user(username="antiga", email="antiga@x.com")
    quem_envia = Usuario.objects.create_user(username="carla", email="carla@x.com")
    nova = Usuario.objects.create_user(username="nova", email="nova@x.com")
    client.force_login(quem_envia)
    client.post(NOVA, dados)
    autor = Inovacao.objects.get().autor
    assert autor == quem_envia
    assert autor not in (antiga, nova)


def test_status_e_data_de_criacao_sao_do_sistema(logado, dados):
    """INOV-05."""
    antes = timezone.now()
    logado.post(NOVA, dados)
    depois = timezone.now()
    inovacao = Inovacao.objects.get()
    assert inovacao.status == StatusInovacao.EM_TESTE
    assert antes <= inovacao.data_criacao <= depois


def test_autor_status_e_data_forjados_no_post_sao_ignorados(logado, dados, autor):
    """INOV-06."""
    outro = Usuario.objects.create_user(username="bruno", email="bruno@x.com")
    dados.update(
        {"autor": str(outro.pk), "status": StatusInovacao.VALIDADA, "data_criacao": "2020-01-01"}
    )
    antes = timezone.now()
    logado.post(NOVA, dados)
    inovacao = Inovacao.objects.get()
    assert inovacao.autor == autor
    assert inovacao.status == StatusInovacao.EM_TESTE
    assert inovacao.data_criacao >= antes


@pytest.mark.django_db
@pytest.mark.parametrize("perfil", [Usuario.Perfil.USUARIO, Usuario.Perfil.ADMINISTRADOR])
def test_qualquer_perfil_cadastra(client, dados, perfil):
    """INOV-08: o cadastro nao depende do perfil."""
    conta = Usuario.objects.create_user(
        username=f"c-{perfil}", email=f"{perfil}@x.com", perfil=perfil
    )
    client.force_login(conta)
    resposta = client.post(NOVA, dados)
    nova = Inovacao.objects.get()
    assertRedirects(resposta, f"/inovacoes/{nova.pk}/", fetch_redirect_response=False)
    assert nova.autor == conta


@pytest.mark.django_db
def test_anonimo_pedindo_o_formulario_vai_ao_login(client):
    """INOV-07."""
    assertRedirects(
        client.get(NOVA), "/entrar/?next=/inovacoes/nova/", fetch_redirect_response=False
    )


@pytest.mark.django_db
def test_anonimo_enviando_o_formulario_vai_ao_login_sem_gravar(client, dados):
    """INOV-07."""
    resposta = client.post(NOVA, dados)
    assertRedirects(resposta, "/entrar/?next=/inovacoes/nova/", fetch_redirect_response=False)
    assert not Inovacao.objects.exists()


RESUMO = "Não foi possível salvar a inovação. Corrija os campos indicados."
MENSAGEM_DUPLICADO = "Já existe uma inovação com este título nesta unidade. Escolha outro título."
MENSAGEM_OBRIGATORIO = {
    "titulo": "Informe o título da inovação.",
    "unidade": "Selecione a unidade de origem.",
    "categoria": "Selecione a categoria.",
    "problema": "Descreva o problema ou dor.",
    "solucao": "Descreva a solução aplicada.",
    "contato": "Informe o contato responsável.",
}


def _trecho_do_alerta(html):
    inicio = html.index('role="alert"')
    return html[inicio : html.index("</div>", inicio)]


def test_envio_com_obrigatorios_vazios_mostra_as_seis_mensagens_e_nao_grava(logado):
    """INOV-09 e INOV-13."""
    resposta = logado.post(NOVA, {campo: "" for campo in CAMPOS})
    assert resposta.status_code == 200
    assert resposta.context["form"].errors == {
        campo: [mensagem] for campo, mensagem in MENSAGEM_OBRIGATORIO.items()
    }
    html = resposta.content.decode()
    for campo, mensagem in MENSAGEM_OBRIGATORIO.items():
        erro = html[html.index(f'id="id_{campo}_error"') :]
        assert mensagem in erro[: erro.index("</ul>")]
    assert not Inovacao.objects.exists()


def test_envio_invalido_mostra_o_resumo_antes_do_primeiro_campo(logado, dados):
    """INOV-30: role=alert, texto fixo, antes do primeiro campo."""
    dados["solucao"] = ""
    html = logado.post(NOVA, dados).content.decode()
    assert RESUMO in _trecho_do_alerta(html)
    assert html.index('role="alert"') < html.index('id="id_titulo"')


def test_formulario_sem_erro_nao_mostra_o_resumo(logado):
    html = logado.get(NOVA).content.decode()
    assert 'role="alert"' not in html
    assert RESUMO not in html


def test_envio_invalido_preserva_tudo_o_que_foi_digitado(logado, dados, unidade, categoria):
    """INOV-11: inclusive a unidade e a categoria selecionadas."""
    dados["titulo"] = ""
    html = logado.post(NOVA, dados).content.decode()
    assert f'<option value="{unidade.pk}" selected>' in html
    assert f'<option value="{categoria.pk}" selected>' in html
    assert f'value="{dados["contato"]}"' in html
    for campo in ["problema", "solucao", "resultado"]:
        assert f">\n{dados[campo]}</textarea>" in html
    assert not Inovacao.objects.exists()


def _valor_do_input(html, campo):
    tag = html[html.rindex("<", 0, html.index(f'id="id_{campo}"')) :]
    tag = tag[: tag.index(">")]
    return re.search(r'\bvalue="([^"]*)"', tag).group(1)


def test_erro_em_outro_campo_preserva_o_titulo_e_os_demais(logado, dados, unidade, categoria):
    """INOV-11: o erro fica na solucao; o titulo e todo o resto voltam como
    foram digitados."""
    dados["solucao"] = ""
    resposta = logado.post(NOVA, dados)
    assert resposta.context["form"].errors == {"solucao": ["Descreva a solução aplicada."]}
    html = resposta.content.decode()
    assert _valor_do_input(html, "titulo") == dados["titulo"]
    assert _valor_do_input(html, "contato") == dados["contato"]
    assert f'<option value="{unidade.pk}" selected>' in html
    assert f'<option value="{categoria.pk}" selected>' in html
    for campo in ["problema", "resultado"]:
        assert f">\n{dados[campo]}</textarea>" in html
    assert not Inovacao.objects.exists()


def test_titulo_repetido_na_mesma_unidade_e_recusado_no_campo_titulo(logado, dados, criar_inovacao):
    """INOV-22 e INOV-23: caixa diferente e espacos nas pontas nao escapam."""
    criar_inovacao(titulo="Controle de Caixa")
    dados["titulo"] = "  controle de caixa  "
    resposta = logado.post(NOVA, dados)
    assert resposta.status_code == 200
    assert resposta.context["form"].errors == {"titulo": [MENSAGEM_DUPLICADO]}
    assert Inovacao.objects.count() == 1


def test_mesmo_titulo_em_outra_unidade_e_aceito(logado, dados, criar_inovacao):
    """INOV-24."""
    criar_inovacao(titulo="Controle de Caixa")
    dados.update(
        {"titulo": "Controle de Caixa", "unidade": str(Unidade.objects.get(nome="Sede").pk)}
    )
    resposta = logado.post(NOVA, dados)
    nova = Inovacao.objects.order_by("-id").first()
    assertRedirects(resposta, f"/inovacoes/{nova.pk}/", fetch_redirect_response=False)
    assert Inovacao.objects.count() == 2


def test_segundo_envio_identico_e_recusado_como_duplicado(logado, dados):
    """INOV-43: duplo clique grava uma vez so."""
    primeira = logado.post(NOVA, dados)
    assertRedirects(
        primeira, f"/inovacoes/{Inovacao.objects.get().pk}/", fetch_redirect_response=False
    )
    resposta = logado.post(NOVA, dados)
    assert resposta.status_code == 200
    assert resposta.context["form"].errors == {"titulo": [MENSAGEM_DUPLICADO]}
    assert Inovacao.objects.count() == 1


def test_corrida_com_o_mesmo_titulo_responde_erro_no_campo_e_nao_500(logado, dados, criar_inovacao):
    """INOV-25: os dois envios passam na validacao antes de qualquer um gravar.

    Neutralizar a validacao reproduz a janela: o save() bate na constraint real
    do PostgreSQL, como faria o segundo de dois envios simultaneos.
    """
    criar_inovacao(titulo=dados["titulo"])
    with mock.patch.object(Inovacao, "validate_constraints", lambda self, exclude=None: None):
        resposta = logado.post(NOVA, dados)
    assert resposta.status_code == 200
    assert resposta.context["form"].errors == {"titulo": [MENSAGEM_DUPLICADO]}
    assert RESUMO in _trecho_do_alerta(resposta.content.decode())
    assert Inovacao.objects.count() == 1


def test_outra_violacao_de_integridade_nao_vira_titulo_duplicado(logado, dados):
    """So a constraint de titulo e tratada; o resto sobe e vira 500."""
    salvar = Inovacao.save

    def salvar_com_status_invalido(self, *args, **kwargs):
        self.status = "APROVADA"
        return salvar(self, *args, **kwargs)

    logado.raise_request_exception = False
    with mock.patch.object(Inovacao, "save", salvar_com_status_invalido):
        resposta = logado.post(NOVA, dados)
    assert resposta.status_code == 500
    assert not Inovacao.objects.exists()


def _regiao_de_status(html):
    inicio = html.index('role="status"')
    return html[inicio : html.index("</div>", inicio)]


def test_cadastro_bem_sucedido_confirma_com_o_titulo_salvo(logado, dados):
    """INOV-28, na pagina do redirect (CONS-50): o detalhe, dentro do role=status."""
    dados["titulo"] = "  Conciliação bancária automática  "
    resposta = logado.post(NOVA, dados, follow=True)
    assert resposta.redirect_chain == [(f"/inovacoes/{Inovacao.objects.get().pk}/", 302)]
    regiao = _regiao_de_status(resposta.content.decode())
    assert "Inovação “Conciliação bancária automática” cadastrada com sucesso." in regiao


def test_mensagem_de_sucesso_nao_reaparece_ao_recarregar(logado, dados):
    """INOV-29, com o detalhe como pagina do redirect (CONS-49)."""
    primeira = logado.post(NOVA, dados, follow=True)
    assert "cadastrada com sucesso" in primeira.content.decode()
    detalhe = primeira.redirect_chain[-1][0]
    html = logado.get(detalhe).content.decode()
    assert "cadastrada com sucesso" not in html


def _valor_do_contato(html):
    tag = html[html.rindex("<", 0, html.index('id="id_contato"')) :]
    tag = tag[: tag.index(">")]
    return tag[tag.index('value="') + len('value="') :].split('"')[0]


def test_contato_vem_preenchido_com_nome_e_email(logado):
    """INOV-39: conta com nome."""
    assert _valor_do_contato(logado.get(NOVA).content.decode()) == "Ana Souza (ana@x.com)"


@pytest.mark.django_db
def test_contato_usa_o_username_quando_a_conta_nao_tem_nome(client):
    """INOV-39: conta sem nome nem sobrenome."""
    client.force_login(Usuario.objects.create_user(username="bruno", email="bruno@x.com"))
    assert _valor_do_contato(client.get(NOVA).content.decode()) == "bruno (bruno@x.com)"


def test_contato_trocado_pela_pessoa_e_o_que_fica_gravado(logado, dados):
    """INOV-40."""
    dados["contato"] = "Equipe de Tesouraria (tesouraria@x.com)"
    logado.post(NOVA, dados)
    assert Inovacao.objects.get().contato == "Equipe de Tesouraria (tesouraria@x.com)"


def _link_cancelar(html):
    links = re.findall(r"<a\b([^>]*)>\s*Cancelar\s*</a>", html)
    assert len(links) == 1, links
    return links[0]


def test_formulario_tem_link_cancelar_para_a_listagem(logado):
    """INOV-36, alterado pela CONS-51: um link, nao um botao, para /inovacoes/."""
    atributos = _link_cancelar(logado.get(NOVA).content.decode())
    assert re.search(r'\bhref="/inovacoes/"', atributos)


def test_cancelar_leva_a_listagem_sem_gravar_nem_pedir_confirmacao(logado):
    """INOV-37, alterado pela CONS-51: GET comum, sem confirmacao, que chega a listagem."""
    atributos = _link_cancelar(logado.get(NOVA).content.decode())
    assert "onclick" not in atributos
    href = re.search(r'\bhref="([^"]*)"', atributos).group(1)
    resposta = logado.get(href)
    assert resposta.status_code == 200
    assert href == "/inovacoes/"
    assertTemplateUsed(resposta, "inovacoes/inovacao_list.html")
    assert not Inovacao.objects.exists()
