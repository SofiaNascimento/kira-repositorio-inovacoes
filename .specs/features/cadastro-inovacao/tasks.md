# Cadastro de Inovação (F2) — Tasks

## Execution Protocol (MANDATORY -- do not skip)

Implement these tasks with the `tlc-spec-driven` skill: **activate it by name and follow its Execute flow and Critical Rules.** Do not search for skill files by filesystem path. The skill is the source of truth for the full flow (per-task cycle, sub-agent delegation, adequacy review, Verifier, discrimination sensor).

**If the skill cannot be activated, STOP and tell the user - do not proceed without it.**

---

**Spec**: `.specs/features/cadastro-inovacao/spec.md`
**Design**: `.specs/features/cadastro-inovacao/design.md`
**Status**: ✅ Concluída — PASS na iteração 3 (`validation.md`); UAT concluído em 2026-10-03 (21/21); T24 corrigiu o único achado do UAT

**Stack fixado**: Django 5.2 LTS · PostgreSQL 16 (AD-003) · pytest + pytest-django · Ruff — o mesmo da F1.

**Desvio do design, já decidido aqui:** o design previa duas migrations (`0001_initial` com as três
tabelas e `0002_listas_iniciais`). Como os modelos nascem em tasks separadas, cada uma gera a sua:
`0001_initial` (Unidade e Categoria, T3), `0002_inovacao` (T4), `0003_titulo_unico_por_unidade` (T5)
e `0004_listas_iniciais` (T7). O esquema final é o mesmo; nenhuma migration foi publicada ainda.

---

## Test Coverage Matrix

> Gerada a partir do código, das diretrizes do projeto e da spec — confirmar antes do Execute.
> **Guidelines encontradas: nenhuma.** Não existe `AGENTS.md`, `CONTRIBUTING.md` nem workflow de CI;
> o `pyproject.toml` só configura o pytest (marcador `unit`, `--strict-markers`) e o Ruff, sem limite
> de cobertura. Valem os **strong defaults**: toda AC e todo edge case da spec têm teste; rotas cobrem
> happy + edge + erro. Estilo, local e fixtures seguem as amostras de `contas/tests/`
> (`test_constraints.py`, `test_admin_perfil.py`, `test_controle_acesso.py`, `test_erro_500.py`,
> `test_migracoes.py`), que são o piso de profundidade.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| ---------- | ------------------ | -------------------- | ---------------- | ----------- |
| Modelos (`inovacoes/models.py`: defaults, FKs, `validate_constraints`) | integration | 1:1 com as ACs de modelo (INOV-05, 14, 16, 19, 22); todo ramo do remapeamento de erro | `inovacoes/tests/test_models.py` | `.venv/bin/pytest -q` |
| Constraints de banco (`Meta.constraints`) | integration | Cada constraint com um caso que a viola e um que a respeita, gravando direto no banco (INOV-26, 27, status) | `inovacoes/tests/test_constraints.py` | `.venv/bin/pytest -q` |
| Data migration (`0004_listas_iniciais`) | integration | Exatamente os 10 nomes; carga idempotente (INOV-18) | `inovacoes/tests/test_migracoes.py` | `.venv/bin/pytest -q` |
| Formulário e template de campo (`inovacoes/forms.py`, `campo.html`) | integration | Todo campo × toda mensagem da spec (obrigatório, tamanho, fora da lista); ordem e ligação ARIA de ajuda e erro. Integration porque os `ModelChoiceField` consultam o banco | `inovacoes/tests/test_forms.py` | `.venv/bin/pytest -q` |
| Views, rotas e templates de página (`inovacoes/views.py`, `inovacao_form.html`, `base.html`) | e2e | Toda rota que a task adiciona: happy + todo edge case listado + caminho de erro, pelo `client` | `inovacoes/tests/test_views_*.py` | `.venv/bin/pytest -q` |
| Admin (`inovacoes/admin.py`, `contas/admin.py`) | e2e | Cada perfil × cada tela (lista, inclusão, alteração, exclusão) de cada modelo (INOV-19, 20, 21) | `inovacoes/tests/test_admin_listas.py`, `contas/tests/test_admin*.py` | `.venv/bin/pytest -q` |
| Configuração, scaffold, migrations de esquema | none | — (apenas gate de build) | — | build gate only |

## Gate Check Commands

> Gerados a partir do projeto — confirmar antes do Execute. Todos pelo `.venv/`, com o PostgreSQL 16
> na porta 5433 em execução.

| Gate Level | When to Use | Command |
| ---------- | ----------- | ------- |
| Quick | Depois de tasks só com teste unitário (nenhuma na F2: todo teste toca o banco) | `.venv/bin/pytest -q -m unit` |
| Full | Depois de tasks com teste de integração ou e2e | `.venv/bin/pytest -q` |
| Build | Ao fechar uma fase, e em tasks de config/migration/template | `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` |

**Linha de base:** 84 testes passando antes da T1 (`.venv/bin/pytest -q`, 2026-09-29).

---

## Execution Plan

As fases são ordenadas e rodam em sequência — cada fase termina antes de a próxima começar, e as
tasks dentro de uma fase executam em ordem.

### Phase 1: Fundação

A refatoração da F1 exigida pela AD-007 e a app nova, ainda vazia.

```
T1 → T2
```

### Phase 2: Modelo de domínio

Listas, entidade central, constraints e carga inicial. Nada de tela.

```
T3 → T4 → T5 → T6 → T7
```

### Phase 3: Admin das listas e formulário

A manutenção das listas pelo `ADMINISTRADOR` e o `InovacaoForm` completo, testado sem view.

```
T8 → T9 → T10 → T11 → T12
```

### Phase 4: Tela de cadastro

A `CreateView` e os fluxos de sucesso, erro e corrida.

```
T13 → T14 → T15 → T16 → T17
```

### Phase 5: Acessibilidade, navegação e falha de banco

O que a spec pede da página além do fluxo principal.

```
T18 → T19 → T20 → T21
```

### Phase 6: Correções da validação (iteração 1)

Gaps do Verifier em `validation.md` (FAIL de 2026-09-29): dois mutantes sobreviventes, ambos por teste fraco. Nenhum código de produção muda.

```
T22 → T23
```

### Phase 7: Correções do UAT

Achados do UAT no navegador (2026-10-02).

```
T24
```

---

## Task Breakdown

### T1: Extrair `AcessoSomenteAdministradorMixin` do `UsuarioAdmin` ✅

**What**: Mover os cinco `has_*_permission` do `UsuarioAdmin` para um mixin reutilizável, sem mudar comportamento (AD-007).
**Where**: `contas/admin.py`
**Depends on**: None
**Reuses**: O próprio código de `contas/admin.py:34-51` (comentário AUTH-22 + métodos)
**Requirement**: AD-007 (pré-requisito da INOV-20)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `class AcessoSomenteAdministradorMixin` em `contas/admin.py` com `has_module_permission`, `has_view_permission`, `has_add_permission`, `has_change_permission` e `has_delete_permission` → `request.user.is_administrador`; o comentário AUTH-22/RN11 acompanha o código
- [x] `UsuarioAdmin(AcessoSomenteAdministradorMixin, UserAdmin)` — o mixin vem antes, para vencer a MRO
- [x] `git diff --stat contas/tests/` vazio: `test_admin_perfil.py` e `test_admin.py` passam **sem alteração**
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 84 testes passam (nenhum novo, nenhum removido)

**Tests**: e2e (a suíte existente de `contas/tests/test_admin*.py` é a rede da refatoração)
**Gate**: full

**Commit**: `refactor(contas): extrai o mixin de acesso somente administrador do admin`

**Status**: ✅ Complete — 84 passed, `contas/tests/` sem alteração

---

### T2: Criar a app `inovacoes` ✅

**What**: Gerar a app `inovacoes` e registrá-la no projeto.
**Where**: `config/settings.py`
**Depends on**: T1
**Reuses**: `python manage.py startapp inovacoes`; arranjo da app `contas`
**Requirement**: AD-002 (estrutura MVT); abordagem A do design

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `inovacoes/` com `apps.py` (`verbose_name = "Inovações"`), `models.py`, `admin.py`, `migrations/__init__.py` e `tests/__init__.py`; sem `tests.py` nem `views.py` de exemplo
- [x] `"inovacoes"` em `INSTALLED_APPS`, depois de `contas`
- [x] `.venv/bin/python manage.py check` sem erro
- [x] Gate check passa (build)
- [x] Test count: 84 testes passam

**Tests**: none
**Gate**: build

**Commit**: `chore(inovacoes): cria a app de inovacoes`

**Status**: ✅ Complete — build gate verde, 84 passed

---

### T3: Modelos `Unidade` e `Categoria` ✅

**What**: As duas listas controladas, com ordem alfabética e nome único sem distinção de caixa.
**Where**: `inovacoes/models.py`
**Depends on**: T2
**Reuses**: `UniqueConstraint(Lower(...))` com `violation_error_message` de `contas/models.py:65-69`
**Requirement**: INOV-15 (ordem), design › Tech Decisions (nome único)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `Unidade` e `Categoria` com `nome = CharField(max_length=100)`, `__str__` → `nome`, `Meta.ordering = ["nome"]`, `verbose_name` em português
- [x] Constraints `unidade_nome_unico_ci` e `categoria_nome_unico_ci` (`Lower("nome")`) com a mensagem "Já existe um item com este nome."
- [x] Migration `inovacoes/migrations/0001_initial.py` gerada
- [x] Testes de integração, parametrizados pelos dois modelos: a consulta padrão sai em ordem alfabética; nomes que diferem só na caixa violam a constraint no `create()`; `full_clean()` acusa a mensagem da constraint. Os testes usam nomes próprios (ex.: "Teste Beta"), que não colidem com a carga da T7
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 90 testes passam (+6)

**Tests**: integration
**Gate**: full

**Commit**: `feat(inovacoes): adiciona as listas de unidade e categoria`

**Status**: ✅ Complete — 90 passed (+6); base abstrata `ItemDeLista` registrada no design

---

### T4: `StatusInovacao` e modelo `Inovacao` ✅

**What**: O enum do ciclo de vida e a entidade central, com FKs `PROTECT`, defaults do sistema e `CheckConstraint` de status.
**Where**: `inovacoes/models.py`
**Depends on**: T3
**Reuses**: `PerfilUsuario` no nível de módulo + `CheckConstraint` de `contas/models.py:7-17, 58-61`; `settings.AUTH_USER_MODEL` (AD-005)
**Requirement**: INOV-05, INOV-14, INOV-16, INOV-19

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `StatusInovacao(TextChoices)` no nível de módulo com `EM_TESTE`, `VALIDADA`, `DISPONIVEL_PARA_REPLICACAO` e os rótulos do design
- [x] `Inovacao` com os campos de *Data Models* do design: `titulo` (150), `unidade` e `categoria` (`PROTECT`), `problema`, `solucao`, `resultado` (`blank=True`), `contato` (150), `status` (default `EM_TESTE`), `autor` (`settings.AUTH_USER_MODEL`, `PROTECT`, `related_name="inovacoes"`), `data_criacao` (`auto_now_add`); `__str__` → `titulo`
- [x] Constraint `inovacao_status_valido`
- [x] Migration `0002_inovacao` gerada
- [x] Testes de integração: registro criado sem status nem data nasce `EM_TESTE` e com `data_criacao` entre o instante antes e depois do `create()` (INOV-05); `unidade=None` e `categoria=None` violam `NOT NULL` (INOV-16); status fora do enum viola a constraint no `create()` e no `update()` em massa; apagar Unidade ou Categoria em uso levanta `ProtectedError` e o item continua no banco (INOV-19); `full_clean()` aceita `resultado` vazio (INOV-14)
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 99 testes passam (+9)

**Tests**: integration
**Gate**: full

**Commit**: `feat(inovacoes): adiciona o modelo de inovacao e o enum de status`

**Status**: ✅ Complete — 99 passed (+9)

---

### T5: Título único por unidade no banco ✅

**What**: `UniqueConstraint(Lower("titulo"), "unidade")` com código e mensagem de duplicado.
**Where**: `inovacoes/models.py`
**Depends on**: T4
**Reuses**: Padrão de constraint case-insensitive da F1
**Requirement**: INOV-24, INOV-26, INOV-27

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Constraint `inovacao_titulo_unico_por_unidade` com `violation_error_code="titulo_duplicado"` e a mensagem "Já existe uma inovação com este título nesta unidade. Escolha outro título."
- [x] Migration `0003_titulo_unico_por_unidade` gerada
- [x] Testes de integração gravando direto no banco (`objects.create`, sem form): mesmo título em caixa diferente na mesma unidade → `IntegrityError` (INOV-26); mesmo título em unidade diferente → aceito (INOV-24); "Solução" e "Solucao" na mesma unidade → aceitos (INOV-27)
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 102 testes passam (+3)

**Tests**: integration
**Gate**: full

**Commit**: `feat(inovacoes): impede titulo repetido na mesma unidade`

**Status**: ✅ Complete — 102 passed (+3)

---

### T6: Erro de título duplicado no campo `titulo` ✅

**What**: `Inovacao.validate_constraints` move o erro de código `titulo_duplicado` de `NON_FIELD_ERRORS` para `titulo`.
**Where**: `inovacoes/models.py`
**Depends on**: T5
**Reuses**: `Model.validate_constraints` do Django (a constraint sobre expressão levanta erro geral — design › Risks)
**Requirement**: INOV-22

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `validate_constraints(exclude=None)` chama o do Django e remapeia só os erros de código `titulo_duplicado`; qualquer outro erro sai como veio
- [x] Testes de integração: `full_clean()` de um duplicado (caixa diferente, mesma unidade) traz a mensagem exata em `error_dict["titulo"]` e nada em `NON_FIELD_ERRORS`; um título novo passa sem erro; outro erro de constraint da própria `Inovacao` (status fora do enum, via `validate_constraints()`) continua em `NON_FIELD_ERRORS` e não vai para `titulo`
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 105 testes passam (+3)

**Tests**: integration
**Gate**: full

**Commit**: `feat(inovacoes): associa o erro de titulo duplicado ao campo titulo`

**Status**: ✅ Complete — 105 passed (+3); o caso "outro erro" usa a CheckConstraint de status da própria Inovacao

---

### T7: Carga inicial das listas ✅

**What**: Data migration que cria as 5 categorias e as 5 unidades provisórias.
**Where**: `inovacoes/migrations/0004_listas_iniciais.py`
**Depends on**: T6
**Reuses**: `RunPython` com `apps.get_model` e `get_or_create`
**Requirement**: INOV-18

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Função direta cria Atendimento interno, Compras, Financeiro, RH, TI interno (categorias) e Filial Leste, Filial Norte, Filial Oeste, Filial Sul, Sede (unidades) com `get_or_create`; a reversa apaga só esses nomes
- [x] Testes de integração: o banco de teste (migrations aplicadas) tem exatamente esses 5 + 5 nomes, na ordem alfabética (INOV-18, INOV-15); rodar a função direta de novo não duplica nada
- [x] Os testes das T3–T6 continuam verdes com a carga presente
- [x] Gate check passa (build)
- [x] Test count: 108 testes passam (+3)

**Tests**: integration
**Gate**: build

**Commit**: `feat(inovacoes): carrega as unidades e categorias iniciais`

**Status**: ✅ Complete — 108 passed (+3), build gate verde

---

### T8: Admin de `Unidade` e `Categoria` só para `ADMINISTRADOR` ✅

**What**: Registrar `UnidadeAdmin` e `CategoriaAdmin` herdando o mixin da T1; `Inovacao` fica fora do admin.
**Where**: `inovacoes/admin.py`
**Depends on**: T7
**Reuses**: `contas.admin.AcessoSomenteAdministradorMixin` (T1, AD-007); fixtures de `contas/tests/test_admin_perfil.py`; delete view do admin, que trata `ProtectedError`
**Requirement**: INOV-19, INOV-20, INOV-21

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `UnidadeAdmin` e `CategoriaAdmin` com `list_display = ("nome",)` e `search_fields = ("nome",)`, ambos `(AcessoSomenteAdministradorMixin, admin.ModelAdmin)`
- [x] `admin.site.is_registered(Inovacao)` é falso
- [x] Testes e2e, parametrizados pelos dois modelos: `USUARIO` com `is_staff` e todas as permissões de modelo recebe 403 na lista, na inclusão, na alteração e na exclusão, e 404 no índice da app (mesmo comportamento documentado na F1) (INOV-20); `ADMINISTRADOR` sem superusuário lista, inclui e renomeia (INOV-21); `ADMINISTRADOR` tentando excluir item usado por uma inovação vê a recusa e o item continua no banco (INOV-19); `Inovacao` não está registrada
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 132 testes passam (+24, com parametrização: inclui POST forjado de inclusão, renomeação e exclusão, como a F1)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(inovacoes): restringe o admin das listas ao administrador`

**Status**: ✅ Complete — 132 passed (+24)

---

### T9: `InovacaoForm` — campos, rótulos e obrigatoriedade ✅

**What**: O `ModelForm` com os sete campos na ordem da spec, rótulos com "(obrigatório)" e as mensagens de campo vazio.
**Where**: `inovacoes/forms.py`
**Depends on**: T8
**Reuses**: `ModelForm`; `CharField(strip=True)` padrão do Django
**Requirement**: INOV-01, INOV-02, INOV-06, INOV-09, INOV-10, INOV-14, INOV-32

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `Meta.fields` = `titulo, unidade, categoria, problema, solucao, resultado, contato`, nessa ordem; `autor`, `status`, `data_criacao` fora
- [x] `labels` do design, com "(obrigatório)" nos seis obrigatórios e não em "Resultado ou impacto"; `label_suffix = ""`
- [x] `error_messages["required"]` com os seis textos da tabela de Assumptions da spec
- [x] Testes de integração: o form expõe exatamente os sete campos na ordem (INOV-01); cada obrigatório vazio traz a sua mensagem (INOV-09, parametrizado pelos seis); só espaços conta como vazio (INOV-10); espaços nas pontas saem do `cleaned_data` (INOV-02); `resultado` vazio é aceito (INOV-14); `autor`, `status` e `data_criacao` enviados nos dados não aparecem em `cleaned_data` nem na instância (INOV-06); rótulos trazem "(obrigatório)" só nos seis (INOV-32)
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 144 testes passam (+12, com parametrização)

**Tests**: integration
**Gate**: full

**Commit**: `feat(inovacoes): adiciona o formulario de cadastro de inovacao`

**Status**: ✅ Complete — 144 passed (+12)

---

### T10: Mensagens de tamanho excedido ✅

**What**: Limite de 5.000 caracteres nos textos longos e a mensagem com limite e tamanho digitado em todos os campos de texto.
**Where**: `inovacoes/forms.py`
**Depends on**: T9
**Reuses**: `error_messages["max_length"]` com `%(limit_value)d` e `%(show_value)d` do `MaxLengthValidator`
**Requirement**: INOV-12

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `problema`, `solucao` e `resultado` com `max_length=5000` no form; `titulo` e `contato` herdam 150 do model
- [x] Mensagem "Use no máximo N caracteres (você digitou M)." nos cinco campos
- [x] Testes de integração, parametrizados pelos cinco campos: limite + 1 é recusado com a mensagem e os valores reais (ex.: "Use no máximo 150 caracteres (você digitou 151)."); exatamente o limite é aceito
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 154 testes passam (+10)

**Tests**: integration
**Gate**: full

**Commit**: `feat(inovacoes): informa o limite de caracteres nos campos de texto`

**Status**: ✅ Complete — 154 passed (+10)

---

### T11: Seleção de unidade e categoria ✅

**What**: `ModelChoiceField` de unidade e categoria com "Selecione…" e as mensagens de valor fora da lista.
**Where**: `inovacoes/forms.py`
**Depends on**: T10
**Reuses**: `ModelChoiceField` (aceita só pk do queryset); `Meta.ordering` da T3
**Requirement**: INOV-15, INOV-17

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `empty_label="Selecione…"` nos dois campos; `error_messages["invalid_choice"]` = "Selecione uma unidade da lista." / "Selecione uma categoria da lista."
- [x] Testes de integração: as opções de cada select são exatamente os registros do banco em ordem alfabética, depois da opção vazia (INOV-15); pk inexistente é recusado com a mensagem do campo certo (INOV-17, parametrizado pelos dois); item apagado entre montar e enviar o form cai na mesma mensagem
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 159 testes passam (+5)

**Tests**: integration
**Gate**: full

**Commit**: `feat(inovacoes): restringe unidade e categoria as listas controladas`

**Status**: ✅ Complete — 159 passed (+5)

---

### T12: Ajuda contextual abaixo do campo ✅

**What**: `help_texts` com exemplo em cada campo e o template de campo que põe a ajuda abaixo do controle.
**Where**: `inovacoes/templates/inovacoes/campo.html`
**Depends on**: T11
**Reuses**: Cópia de `django/forms/templates/django/forms/field.html` do Django instalado; ids `<auto_id>_helptext` e `<auto_id>_error` do próprio Django
**Requirement**: INOV-33, INOV-41

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `help_texts` no `InovacaoForm` com uma frase e um "Ex.:" por campo; `__init__` aplica `template_name = "inovacoes/campo.html"` a todos os campos
- [x] `campo.html` renderiza rótulo → controle → erros → ajuda
- [x] Testes de integração sobre o HTML renderizado: para cada um dos sete campos, a ajuda com "Ex.:" aparece depois do controle e o `aria-describedby` do controle inclui `id_<campo>_helptext`, que existe no HTML (INOV-41); num form inválido, o campo com erro tem `aria-invalid="true"` e o `aria-describedby` inclui `id_<campo>_error`, que existe e contém a mensagem (INOV-33); campo sem erro não tem `aria-invalid`
- [x] Gate check passa (build)
- [x] Test count: 168 testes passam (+9, com parametrização)

**Tests**: integration
**Gate**: build

**Commit**: `feat(inovacoes): mostra ajuda com exemplo abaixo de cada campo`

**Status**: ✅ Complete — 168 passed (+9), build gate verde

---

### T13: Tela de cadastro (`InovacaoCreateView`, rota e template) ✅

**What**: A rota `/inovacoes/nova/` com GET do form vazio e POST que grava com o autor da sessão e redireciona à home.
**Where**: `inovacoes/views.py`
**Depends on**: T12
**Reuses**: `CreateView`; `LoginRequiredMiddleware` e a varredura de `contas/tests/test_controle_acesso.py` (AD-006); `HomeInternaView` como destino
**Requirement**: INOV-01, INOV-02, INOV-03, INOV-04, INOV-05, INOV-06, INOV-07, INOV-08

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `InovacaoCreateView` com `form_class = InovacaoForm`, `form_valid` que fixa `form.instance.autor = request.user` e `success_url` = `nucleo:home`; sem decorator (AD-006)
- [x] `inovacoes/urls.py` com `app_name = "inovacoes"` e `nova/` → `name="nova"`, incluído em `config/urls.py` sob `inovacoes/`
- [x] `inovacao_form.html` estende `base.html`: `<h1>Cadastrar inovação</h1>`, `<form method="post" novalidate>`, `{% csrf_token %}`, `{{ campo.as_field_group }}` por campo e `<button type="submit">Salvar</button>`
- [x] Testes e2e: GET autenticado → 200 com exatamente os sete campos editáveis (INOV-01); POST válido grava exatamente uma inovação com os valores sem espaços nas pontas (INOV-02) e responde 302 para `/` (INOV-03); autor = conta logada (INOV-04); status `EM_TESTE` e `data_criacao` do momento (INOV-05); `autor`, `status` e `data_criacao` forjados no POST são ignorados (INOV-06); `USUARIO` e `ADMINISTRADOR` cadastram igual (INOV-08, parametrizado); anônimo em GET e em POST vai a `/entrar/?next=/inovacoes/nova/` e nada é gravado (INOV-07)
- [x] O teste de varredura de `contas/tests/test_controle_acesso.py` passa sem alteração e já inclui `/inovacoes/nova/`
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 178 testes passam (+10)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(inovacoes): adiciona a tela de cadastro de inovacao`

**Status**: ✅ Complete — 178 passed (+10); a varredura da F1 já enxerga `/inovacoes/nova/`

---

### T14: Resposta a envio inválido ✅

**What**: O resumo de erro no topo do form e a prova, pela tela, de que envio inválido preserva os dados e não grava nada.
**Where**: `inovacoes/templates/inovacoes/inovacao_form.html`
**Depends on**: T13
**Reuses**: Re-render com o form vinculado do `CreateView`; validação das T6, T9–T11
**Requirement**: INOV-09, INOV-11, INOV-13, INOV-22, INOV-23, INOV-24, INOV-30, INOV-43

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Com `form.errors`, `<div role="alert">` com "Não foi possível salvar a inovação. Corrija os campos indicados." antes do primeiro campo
- [x] Testes e2e: envio com todos os obrigatórios vazios → 200, as seis mensagens, o resumo antes do primeiro campo e nenhum registro (INOV-09, INOV-13, INOV-30); envio inválido preserva todo valor digitado, inclusive a unidade e a categoria selecionadas (INOV-11); " controle de caixa " na unidade em que "Controle de Caixa" existe → mensagem de duplicado no título (INOV-22, INOV-23); o mesmo título em outra unidade → 302 (INOV-24); o mesmo POST válido enviado duas vezes grava um e responde 200 com a mensagem de duplicado ao segundo (INOV-43); form válido não mostra o resumo
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 185 testes passam (+7)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(inovacoes): resume os erros no topo do formulario de cadastro`

**Status**: ✅ Complete — 185 passed (+7)

---

### T15: Corrida entre dois envios com o mesmo título ✅

**What**: `form_valid` grava em `transaction.atomic()` e converte em erro de campo só o `IntegrityError` da constraint de título.
**Where**: `inovacoes/views.py`
**Depends on**: T14
**Reuses**: `IntegrityError.__cause__.diag.constraint_name` do psycopg 3; mensagem da constraint da T5
**Requirement**: INOV-25

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `IntegrityError` com `constraint_name == "inovacao_titulo_unico_por_unidade"` → `form.add_error("titulo", <mensagem da constraint>)` e `form_invalid` (200); qualquer outro `IntegrityError` sobe
- [x] Testes e2e: com `Inovacao.validate_constraints` neutralizado por `mock.patch` e um registro igual já no banco, o POST responde 200 com a mensagem de duplicado no título, o resumo, e segue existindo um único registro (INOV-25); um `IntegrityError` de outra constraint sobe (com `raise_request_exception = False`, 500) em vez de virar "título duplicado"
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 187 testes passam (+2)

**Tests**: e2e
**Gate**: full

**Commit**: `fix(inovacoes): trata a corrida entre cadastros com o mesmo titulo`

**Status**: ✅ Complete — 187 passed (+2); o ramo "outra violação" usa a CheckConstraint real de status

---

### T16: Mensagem de sucesso ✅

**What**: `messages.success` com o título salvo, lida uma vez na home.
**Where**: `inovacoes/views.py`
**Depends on**: T15
**Reuses**: `django.contrib.messages`; região `role="status"` do `templates/base.html`
**Requirement**: INOV-28, INOV-29

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Depois do `save()`, `messages.success(request, "Inovação “<título>” cadastrada com sucesso.")` com o título já sem espaços
- [x] Testes e2e: seguindo o redirect, a mensagem exata, com aspas curvas e o título salvo, está dentro do `role="status"` (INOV-28); recarregar a home não a mostra de novo (INOV-29)
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 189 testes passam (+2)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(inovacoes): confirma o cadastro com mensagem de sucesso`

**Status**: ✅ Complete — 189 passed (+2)

---

### T17: Contato responsável pré-preenchido ✅

**What**: `get_initial` preenche o contato com o nome (ou username) e o e-mail de quem está logado.
**Where**: `inovacoes/views.py`
**Depends on**: T16
**Reuses**: `Usuario.get_full_name()`, `get_username()`, `email`
**Requirement**: INOV-39, INOV-40

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `get_initial()` → `{"contato": "<nome completo> (<e-mail>)"}`, com `username` no lugar do nome quando `first_name` e `last_name` estão vazios
- [x] Testes e2e: conta com nome vê "Ana Souza (ana@x.com)" no campo; conta sem nome vê "ana (ana@x.com)" (INOV-39); trocar o contato antes de salvar grava o valor digitado (INOV-40)
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 192 testes passam (+3)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(inovacoes): pre-preenche o contato responsavel com o autor`

**Status**: ✅ Complete — 192 passed (+3), build gate verde

---

### T18: Formulário acessível por teclado e leitor de tela ✅

**What**: Prova, sobre o HTML da página, das ACs de acessibilidade; ajusta o template onde faltar.
**Where**: `inovacoes/tests/test_views_acessibilidade.py`
**Depends on**: T17
**Reuses**: `label_tag` e atributo `required` do Django; `:focus-visible` do `base.html`
**Requirement**: INOV-31, INOV-32, INOV-34, INOV-35

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Testes e2e com `html.parser` da biblioteca padrão sobre `/inovacoes/nova/`: todo controle tem um `<label for>` visível com o mesmo `id` (INOV-31); os seis obrigatórios têm `required` e "(obrigatório)" no rótulo, e `resultado` não tem (INOV-32); os controles do form são só `input`, `select`, `textarea`, `button` e `a`, e nenhum elemento tem `tabindex` positivo (INOV-34); a página carrega a regra `:focus-visible` com contorno, que alcança os controles e o link de cancelar (INOV-35)
- [x] Se algum teste acusar falta, o ajuste vai no template da T13 dentro desta task
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 196 testes passam (+4)

**Tests**: e2e
**Gate**: full

**Commit**: `test(inovacoes): cobre a acessibilidade do formulario de cadastro`

**Status**: ✅ Complete — 196 passed (+4); nenhum ajuste no template foi necessário; faltas injetadas (tabindex positivo, role=button, outline: none) derrubaram os testes

---

### T19: Cancelar sem salvar ✅

**What**: Link "Cancelar" para a home, fora do envio do form.
**Where**: `inovacoes/templates/inovacoes/inovacao_form.html`
**Depends on**: T18
**Reuses**: Rota `nucleo:home`
**Requirement**: INOV-36, INOV-37

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `<a href="{% url 'nucleo:home' %}">Cancelar</a>` ao lado do botão Salvar
- [x] Testes e2e: a página tem um `<a>` com o texto "Cancelar" e `href="/"` (INOV-36); seguir esse `href` com GET responde 200 na home, sem nenhuma inovação nova e sem página de confirmação no caminho (INOV-37)
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 198 testes passam (+2)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(inovacoes): permite cancelar o cadastro sem salvar`

**Status**: ✅ Complete — 198 passed (+2)

---

### T20: Link "Cadastrar inovação" no cabeçalho ✅

**What**: `<nav aria-label="Principal">` com o link para o cadastro no cabeçalho autenticado.
**Where**: `templates/base.html`
**Depends on**: T19
**Reuses**: Bloco `{% if user.is_authenticated %}` do cabeçalho
**Requirement**: INOV-38

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Link `<a href="{% url 'inovacoes:nova' %}">Cadastrar inovação</a>` dentro de `<nav aria-label="Principal">` no `<header>`, só para usuário autenticado
- [x] Testes e2e: na home e no próprio formulário, autenticado, o `<header>` tem o link com o texto e `href="/inovacoes/nova/"` (INOV-38); na tela de login, anônima, o link não aparece
- [x] Os testes existentes de `contas/tests/` que leem o `base.html` continuam verdes
- [x] Gate check passa (build)
- [x] Test count: 201 testes passam (+3)

**Tests**: e2e
**Gate**: build

**Commit**: `feat(inovacoes): adiciona o cadastro de inovacao ao cabecalho`

**Status**: ✅ Complete — 201 passed (+3), build gate verde

---

### T21: Banco indisponível durante o cadastro ✅

**What**: Prova de que a queda do PostgreSQL no cadastro cai na página 500 do projeto, sem gravar nem vazar.
**Where**: `inovacoes/tests/test_views_erro_500.py`
**Depends on**: T20
**Reuses**: Fixture e lista de trechos proibidos de `contas/tests/test_erro_500.py`; `templates/500.html` (AUTH-26)
**Requirement**: INOV-42

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Testes e2e com `Inovacao.save` forçado a levantar `OperationalError` com detalhes de conexão falsos e `raise_request_exception = False`: o POST válido responde 500 com `500.html` e nenhuma inovação existe no banco; o HTML não contém host, usuário, senha, `OperationalError` nem `Traceback` (INOV-42)
- [x] Gate check passa (build) — fechamento da feature
- [x] Test count: 203 testes passam (+2)

**Tests**: e2e
**Gate**: build

**Commit**: `test(inovacoes): cobre o cadastro com o banco indisponivel`

**Status**: ✅ Complete — 203 passed (+2), build gate verde

---

### T22: Autor distinto da conta mais antiga (mutante V2b) ✅

**What**: Teste que prova que o autor é quem enviou o formulário, e não uma conta qualquer do banco.
**Where**: `inovacoes/tests/test_views_cadastro.py`
**Depends on**: T21
**Reuses**: Fixtures `dados` e `client` do próprio arquivo
**Requirement**: INOV-04

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Novo teste e2e: uma conta criada antes e outra depois de quem envia; o autor gravado é a conta logada e não é nenhuma das outras duas (mata "menor `pk`" e "maior `pk`")
- [x] Os testes existentes ficam como estão
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: 204 testes passam (+1)

**Tests**: e2e
**Gate**: full

**Commit**: `test(inovacoes): distingue o autor das demais contas no cadastro`

**Status**: ✅ Complete — 204 passed (+1); mata os mutantes "menor pk" (V2b) e "maior pk"

---

### T23: Título preservado quando o erro está em outro campo (mutante T4) ✅

**What**: Teste que provoca o erro em `solucao` e confirma que os outros seis campos, inclusive o título, voltam com o valor digitado.
**Where**: `inovacoes/tests/test_views_cadastro.py`
**Depends on**: T22
**Reuses**: Fixture `dados`; mesmas asserções de HTML do teste de preservação da T14
**Requirement**: INOV-11

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Novo teste e2e: `solucao` vazia; o `input` do título traz `value="<título digitado>"`, e unidade, categoria, problema, resultado e contato voltam preenchidos; nada é gravado
- [x] Os testes existentes ficam como estão
- [x] Gate check passa (build) — fechamento da iteração
- [x] Test count: 205 testes passam (+1)

**Tests**: e2e
**Gate**: build

**Commit**: `test(inovacoes): prova que o titulo volta preenchido apos erro`

**Status**: ✅ Complete — 205 passed (+1), build gate verde; mata o mutante T4

---

### T24: Login do admin abre para o visitante anônimo (achado do UAT) ✅

**What**: `AcessoSomenteAdministradorMixin` trata o `AnonymousUser` como não administrador. O login do admin monta a lista de apps com o visitante anônimo e chamava `request.user.is_administrador`, que o `AnonymousUser` não tem: `GET /admin/login/` respondia 500. O defeito vem da F1 (`c28430c`) e foi achado no UAT, item de criação das contas.
**Where**: `contas/admin.py`, `contas/tests/test_admin_perfil.py`
**Depends on**: T23
**Reuses**: Mixin da T1 (AD-007)
**Requirement**: AUTH-28 (acrescentada à F1 em 2026-10-03 a partir deste achado; antes, lida como parte da AUTH-21); INOV-20 e INOV-21 continuam como estavam

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Novo teste e2e: anônimo em `/admin/` é redirecionado a `/admin/login/?next=/admin/`, que responde 200 com o campo `username`; o teste falha antes da correção
- [x] Os cinco `has_*_permission` do mixin passam por `_is_administrador`, que exige `is_authenticated` antes de consultar o perfil
- [x] Os testes de admin existentes passam sem alteração
- [x] Gate check passa (build)
- [x] Test count: 206 testes passam (+1)

**Tests**: e2e
**Gate**: build

**Commit**: `fix(contas): abre o login do admin para o visitante anonimo`

**Status**: ✅ Complete — 206 passed (+1), build gate verde

---

## Phase Execution Map

```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Phase 7

Phase 1:  T1 → T2
Phase 2:  T3 → T4 → T5 → T6 → T7
Phase 3:  T8 → T9 → T10 → T11 → T12
Phase 4:  T13 → T14 → T15 → T16 → T17
Phase 5:  T18 → T19 → T20 → T21
Phase 6:  T22 → T23
Phase 7:  T24
```

Arcos de fronteira entre fases (a primeira task de cada fase depende da última da anterior):

```
T2  → T3
T7  → T8
T12 → T13
T17 → T18
T21 → T22
T23 → T24
```

A execução é estritamente sequencial — não há paralelismo dentro de uma fase.

**Empacotamento previsto no Execute:** 21 tasks ⇒ com orçamento de ~7 por lote e corte apenas em
fronteira de fase: **lote 1** = Fases 1+2 (7 tasks), **lote 2** = Fase 3 (5), **lote 3** = Fase 4
(5), **lote 4** = Fase 5 (4). Mais de um lote ⇒ o Execute deve **oferecer** sub-agentes antes de
começar.

---

## Task Granularity Check

| Task | Scope | Status |
| ---- | ----- | ------ |
| T1 | 1 refatoração em `contas/admin.py` | ✅ Granular |
| T2 | 1 scaffold + 1 linha de settings | ✅ Granular |
| T3, T4, T5, T6 | 1 conceito cada em `inovacoes/models.py` (+ a migration que ele gera) | ✅ Granular (coeso, mesmo arquivo) |
| T7 | 1 data migration | ✅ Granular |
| T8 | 2 `ModelAdmin` idênticos em 1 arquivo | ✅ Granular (coeso) |
| T9, T10, T11 | 1 comportamento cada em `inovacoes/forms.py` | ✅ Granular |
| T12 | 1 template de campo + `help_texts` | ⚠️ 2 arquivos, coeso — ver nota |
| T13 | 1 tela = view + rota + template | ⚠️ 3 arquivos, coeso — ver nota |
| T14, T19 | 1 trecho do template da tela | ✅ Granular |
| T15, T16, T17 | 1 método cada em `inovacoes/views.py` | ✅ Granular |
| T18, T21, T22, T23 | 1 arquivo de teste (o código já existe) | ✅ Granular |
| T20 | 1 trecho do `base.html` | ✅ Granular |
| T24 | 1 helper em `contas/admin.py` + o teste que o prova | ✅ Granular |

**Nota sobre T12 e T13:** o `campo.html` não tem efeito sem o `template_name` aplicado no form, e a
ajuda não tem onde aparecer sem o template; uma view Django não é testável sem rota e template. Separar
deixaria código não verificado, o que a co-locação de testes proíbe. O `Where` nomeia o arquivo
principal; os demais estão no `Done when` e cobertos pelos mesmos testes. É merge backward
deliberado, como a T16 da F1.

**Nota sobre T18 e T21:** o comportamento vem do Django e da F1 (rótulos, `required`, `:focus-visible`,
handler 500). A task é a evidência das ACs; se a evidência acusar falta, o ajuste entra na mesma task.

---

## Diagram-Definition Cross-Check

| Task | Depends On (task body) | Diagram Shows | Status |
| ---- | ---------------------- | ------------- | ------ |
| T1 | None | (início da Fase 1) | ✅ Match |
| T2 | T1 | T1 → T2 | ✅ Match |
| T3 | T2 | T2 → T3 (arco de fronteira) | ✅ Match |
| T4 | T3 | T3 → T4 | ✅ Match |
| T5 | T4 | T4 → T5 | ✅ Match |
| T6 | T5 | T5 → T6 | ✅ Match |
| T7 | T6 | T6 → T7 | ✅ Match |
| T8 | T7 | T7 → T8 (arco de fronteira) | ✅ Match |
| T9 | T8 | T8 → T9 | ✅ Match |
| T10 | T9 | T9 → T10 | ✅ Match |
| T11 | T10 | T10 → T11 | ✅ Match |
| T12 | T11 | T11 → T12 | ✅ Match |
| T13 | T12 | T12 → T13 (arco de fronteira) | ✅ Match |
| T14 | T13 | T13 → T14 | ✅ Match |
| T15 | T14 | T14 → T15 | ✅ Match |
| T16 | T15 | T15 → T16 | ✅ Match |
| T17 | T16 | T16 → T17 | ✅ Match |
| T18 | T17 | T17 → T18 (arco de fronteira) | ✅ Match |
| T19 | T18 | T18 → T19 | ✅ Match |
| T20 | T19 | T19 → T20 | ✅ Match |
| T21 | T20 | T20 → T21 | ✅ Match |
| T22 | T21 | T21 → T22 (arco de fronteira) | ✅ Match |
| T23 | T22 | T22 → T23 | ✅ Match |
| T24 | T23 | T23 → T24 (arco de fronteira) | ✅ Match |

Nenhuma dependência aponta para fase posterior.

---

## Test Co-location Validation

| Task | Code Layer Created/Modified | Matrix Requires | Task Says | Status |
| ---- | --------------------------- | --------------- | --------- | ------ |
| T1 | Admin (`contas/admin.py`) | e2e | e2e (suíte existente) | ✅ OK |
| T2 | Configuração (scaffold) | none | none | ✅ OK |
| T3 | Modelos + constraints | integration | integration | ✅ OK |
| T4 | Modelos + constraints | integration | integration | ✅ OK |
| T5 | Constraints de banco | integration | integration | ✅ OK |
| T6 | Modelos (`validate_constraints`) | integration | integration | ✅ OK |
| T7 | Data migration | integration | integration | ✅ OK |
| T8 | Admin | e2e | e2e | ✅ OK |
| T9 | Formulário | integration | integration | ✅ OK |
| T10 | Formulário | integration | integration | ✅ OK |
| T11 | Formulário | integration | integration | ✅ OK |
| T12 | Formulário + template de campo | integration | integration | ✅ OK |
| T13 | Views, rotas e template de página | e2e | e2e | ✅ OK |
| T14 | Template de página | e2e | e2e | ✅ OK |
| T15 | Views | e2e | e2e | ✅ OK |
| T16 | Views | e2e | e2e | ✅ OK |
| T17 | Views | e2e | e2e | ✅ OK |
| T18 | Template de página (só testes, ajuste se faltar) | e2e | e2e | ✅ OK |
| T19 | Template de página | e2e | e2e | ✅ OK |
| T20 | Template de página (`base.html`) | e2e | e2e | ✅ OK |
| T21 | Views (só testes) | e2e | e2e | ✅ OK |
| T22 | Views (só testes) | e2e | e2e | ✅ OK |
| T23 | Views (só testes) | e2e | e2e | ✅ OK |
| T24 | Admin (`contas/admin.py`) | e2e | e2e | ✅ OK |

Nenhuma violação. O único `Tests: none` (T2) é scaffold, que a matriz cobre pelo gate de build.

---

## Cobertura de requisitos por task

| Requirement | Task(s) |
| ----------- | ------- |
| INOV-01 | T9, T13 |
| INOV-02 | T9, T13 |
| INOV-03 | T13 |
| INOV-04 | T13, T22 |
| INOV-05 | T4, T13 |
| INOV-06 | T9, T13 |
| INOV-07 | T13 |
| INOV-08 | T13 |
| INOV-09 | T9, T14 |
| INOV-10 | T9 |
| INOV-11 | T14, T23 |
| INOV-12 | T10 |
| INOV-13 | T14 |
| INOV-14 | T4, T9 |
| INOV-15 | T3, T7, T11 |
| INOV-16 | T4 |
| INOV-17 | T11 |
| INOV-18 | T7 |
| INOV-19 | T4, T8 |
| INOV-20 | T1, T8 |
| INOV-21 | T8 |
| INOV-22 | T6, T14 |
| INOV-23 | T14 |
| INOV-24 | T5, T14 |
| INOV-25 | T15 |
| INOV-26 | T5 |
| INOV-27 | T5 |
| INOV-28 | T16 |
| INOV-29 | T16 |
| INOV-30 | T14 |
| INOV-31 | T18 |
| INOV-32 | T9, T18 |
| INOV-33 | T12 |
| INOV-34 | T18 |
| INOV-35 | T18 |
| INOV-36 | T19 |
| INOV-37 | T19 |
| INOV-38 | T20 |
| INOV-39 | T17 |
| INOV-40 | T17 |
| INOV-41 | T12 |
| INOV-42 | T21 |
| INOV-43 | T14 |

43 requisitos, 43 mapeados, 0 órfãos.
