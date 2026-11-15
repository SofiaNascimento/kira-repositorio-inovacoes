"""Modo rigoroso do `exibido()` (fundacao-do-redesign, T1; regra de teste da feature).

Fonte: .specs/features/fundacao-do-redesign/design.md (Testes) e tasks.md (T1). O modo
rigoroso esconde tambem os vetores que o padrao deixava passar na F6 (L2 a L4): controle
`disabled`, `role` `presentation`/`none` e classe que a folha declara com `display: none`.
O modo padrao nao muda.
"""

import pytest

from inovacoes.tests import visibilidade
from inovacoes.tests.visibilidade import classes_ocultas, exibido

pytestmark = pytest.mark.unit

# Folha de teste: uma classe escondida em regra simples, e tres que nao contam.
FOLHA = """
.sumida { display: none; }
.composta .filha { display: none; }
@media (max-width: 30rem) { .so-no-celular { display: none; } }
:root[data-contraste=alto] .so-no-contraste { display: none; }
"""


@pytest.fixture
def folha(monkeypatch):
    monkeypatch.setattr(visibilidade, "CLASSES_OCULTAS", classes_ocultas(FOLHA))


VETORES = {
    "disabled num button": "<p>antes</p><button disabled>Enviar agora</button><p>depois</p>",
    "role presentation": '<p>antes</p><div role="presentation">Enviar agora</div><p>depois</p>',
    "role NONE": '<p>antes</p><div role="NONE">Enviar agora</div><p>depois</p>',
    "classe com display none": '<p>antes</p><div class="x sumida">Enviar agora</div><p>depois</p>',
}


@pytest.mark.usefixtures("folha")
@pytest.mark.parametrize("vetor", VETORES)
def test_modo_rigoroso_esconde_o_vetor(vetor):
    resultado = exibido(VETORES[vetor], rigoroso=True)
    assert "Enviar agora" not in resultado
    assert resultado == "<p>antes</p><p>depois</p>"


@pytest.mark.usefixtures("folha")
@pytest.mark.parametrize("vetor", VETORES)
def test_modo_padrao_continua_exibindo_o_vetor(vetor):
    assert exibido(VETORES[vetor]) == VETORES[vetor]


@pytest.mark.usefixtures("folha")
@pytest.mark.parametrize("rigoroso", [False, True])
@pytest.mark.parametrize(
    "html",
    [
        "<div hidden>Enviar agora</div>",
        "<div inert>Enviar agora</div>",
        '<span aria-hidden="TRUE">Enviar agora</span>',
        "<template>Enviar agora</template>",
        "<details><summary>Resumo</summary>Enviar agora</details>",
        "<!-- Enviar agora -->",
    ],
)
def test_o_que_o_padrao_ja_escondia_continua_escondido_nos_dois_modos(html, rigoroso):
    assert "Enviar agora" not in exibido(html, rigoroso=rigoroso)


@pytest.mark.usefixtures("folha")
@pytest.mark.parametrize("classe", ["filha", "so-no-celular", "so-no-contraste"])
def test_classe_fora_de_regra_simples_global_continua_exibida(classe):
    """Design: so seletor de classe simples, fora de @media e de [data-contraste=alto]."""
    html = f'<div class="{classe}">Enviar agora</div>'
    assert exibido(html, rigoroso=True) == html


def test_classes_ocultas_le_so_as_regras_simples_globais():
    assert classes_ocultas(FOLHA) == {"sumida"}


@pytest.mark.usefixtures("folha")
def test_descendente_de_um_vetor_tambem_some():
    html = "<button disabled><span>Enviar agora</span></button><p>depois</p>"
    assert exibido(html, rigoroso=True) == "<p>depois</p>"
