"""Testes do modelo Usuario.

Derivados das ACs da spec (.specs/features/autenticacao/spec.md), nao da
implementacao. Todos operam sobre instancias nao salvas: nenhum toca o banco.
"""

import pytest

from contas.models import Usuario


@pytest.mark.unit
def test_perfil_tem_exatamente_usuario_e_administrador():
    """AUTH-16: o perfil e restrito a exatamente esses dois valores."""
    assert Usuario.Perfil.values == ["USUARIO", "ADMINISTRADOR"]


@pytest.mark.unit
def test_perfil_padrao_e_usuario():
    """AUTH-17: conta criada sem perfil explicito nasce USUARIO."""
    assert Usuario().perfil == Usuario.Perfil.USUARIO


@pytest.mark.unit
def test_is_administrador_verdadeiro_para_perfil_administrador():
    """AUTH-19: o ponto unico de consulta reporta poderes de administrador."""
    assert Usuario(perfil=Usuario.Perfil.ADMINISTRADOR).is_administrador is True


@pytest.mark.unit
def test_is_administrador_falso_para_perfil_usuario():
    """AUTH-19: e os nega para o perfil comum."""
    assert Usuario(perfil=Usuario.Perfil.USUARIO).is_administrador is False
