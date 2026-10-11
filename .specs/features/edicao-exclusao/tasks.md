# Edição e Exclusão de Inovações (F4) — Tasks

## Execution Protocol (MANDATORY -- do not skip)

Implement these tasks with the `tlc-spec-driven` skill: **activate it by name and follow its Execute flow and Critical Rules.** Do not search for skill files by filesystem path. The skill is the source of truth for the full flow (per-task cycle, sub-agent delegation, adequacy review, Verifier, discrimination sensor).

**If the skill cannot be activated, STOP and tell the user - do not proceed without it.**

---

**Spec**: `.specs/features/edicao-exclusao/spec.md`
**Design**: `.specs/features/edicao-exclusao/design.md`
**Status**: In Progress — T1–T14 ✅; Verifier iteração 1 FAIL (lacunas só de teste) → Fase 5 (T15–T18) de correção

**Stack fixado**: Django 5.2.17 · PostgreSQL 16 (AD-003) · pytest + pytest-django · Ruff — o mesmo da F1, F2 e F3.

**Caso central do RNF07 — "usuário comum tenta alterar registro de terceiro":** coberto em quatro
camadas, cada uma numa task diferente, para que nenhuma sozinha seja a única prova:

| Camada | Task | O que prova |
| ------ | ---- | ----------- |
| Regra no modelo | T1 | `pode_ser_alterada_por` é falso para `USUARIO` terceiro, inclusive com `is_staff`/`is_superuser` e logo depois de um rebaixamento |
| Rota de edição | T4 (GET), T5 (POST) | 403 com a página própria; o POST não altera nenhum campo |
| Rota de exclusão | T9 (GET), T10 (POST) | 403 com a página própria; o POST não apaga |
| Varredura de rotas (AD-009) | T11 | Toda rota de `inovacoes` com `pk`, menos o detalhe, responde 403 a GET e POST de um terceiro e não muda o banco — inclusive as rotas que a F5 criar |
| Tela | T8, T9 | O terceiro não vê "Editar" nem "Excluir" no detalhe |

---

## Test Coverage Matrix

> Gerada a partir do código, das diretrizes do projeto e da spec — confirmar antes do Execute.
> **Guidelines encontradas: nenhuma.** Não existe `AGENTS.md`, `CONTRIBUTING.md` nem workflow de CI;
> o `pyproject.toml` só configura o pytest (marcador `unit`, `--strict-markers`) e o Ruff, sem limite
> de cobertura. Valem os **strong defaults**: toda AC e todo edge case da spec têm teste; rotas cobrem
> happy + edge + erro. Estilo, local e fixtures seguem as amostras de `inovacoes/tests/`
> (`conftest.py`, `test_models.py`, `test_views_cadastro.py`, `test_views_detalhe.py`,
> `test_views_acessibilidade.py`, `test_views_erro_500.py`) e `contas/tests/test_controle_acesso.py`
> (varredura de rotas) e `contas/tests/test_views_login.py:66` (`enforce_csrf_checks`), que são o piso
> de profundidade.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| ---------- | ------------------ | -------------------- | ---------------- | ----------- |
| Regra do modelo (`Inovacao.pode_ser_alterada_por`) | integration | Todo ramo: autor × terceiro × `USUARIO`/`ADMINISTRADOR`, `AnonymousUser`, `is_staff`/`is_superuser` sem perfil, rebaixamento, zero consultas (EDEX-17, EDEX-19, EDEX-25). Integration porque usa contas e inovações gravadas | `inovacoes/tests/test_permissoes.py` | `.venv/bin/pytest -q` |
| Views, rotas e templates de página (`inovacoes/views.py`, `inovacoes/urls.py`, `inovacoes/templates/inovacoes/*.html`) | e2e | Toda rota que a task adiciona ou altera: happy + todo edge case listado + caminho de erro, pelo `client`, para os três papéis (autor, administrador, terceiro `USUARIO`) e o anônimo; afirmar o estado do banco depois de toda recusa | `inovacoes/tests/test_views_edicao.py`, `test_views_exclusao.py`, `test_views_detalhe.py`, `test_views_cadastro.py`, `test_controle_autoria.py`, `test_views_acessibilidade_alteracao.py`, `test_views_erro_500.py` | `.venv/bin/pytest -q` |
| Formulário (`InovacaoForm`) | none | — sem mudança; as mensagens da F2 são reafirmadas pela rota de edição (T6) | — | — |
| Migrations | none | — nenhuma migration nova; `makemigrations --check` no gate de build | — | build gate only |

## Gate Check Commands

> Gerados a partir do projeto — confirmar antes do Execute. Todos pelo `.venv/`, com o PostgreSQL 16
> na porta 5433 em execução.

| Gate Level | When to Use | Command |
| ---------- | ----------- | ------- |
| Quick | Não usado nesta feature (nenhuma task só com teste unitário) | `.venv/bin/pytest -q -m unit` |
| Full | Depois de toda task com teste de integração ou e2e | `.venv/bin/pytest -q` |
| Build | Ao fechar uma fase, e nas tasks que mexem em template compartilhado ou refatoram código da F2 | `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` |

**Linha de base:** 380 testes passando antes da T1 (`.venv/bin/pytest -q`, 2026-10-11).

**Testes da F2 e da F3 que mudam:** nenhum. As refatorações da T2 (mixin de gravação), da T3 (template
parametrizado) e da T4 (`_inovacao_nao_encontrada` no detalhe) são provadas pela suíte existente
**sem alteração**: se um teste da F2 ou da F3 precisar mudar, a refatoração está errada. As contagens
abaixo são estimativas; a regra dura é que a contagem nunca cai.

---

## Execution Plan

As fases são ordenadas e rodam em sequência — cada fase termina antes de a próxima começar, e as
tasks dentro de uma fase executam em ordem.

### Phase 1: Fundação — a regra de autoria e as refatorações sem mudança de comportamento

A regra no modelo e as duas extrações do cadastro que a edição vai reaproveitar. Nenhuma tela nova.

```
T1 → T2 → T3
```

### Phase 2: Edição (P1)

A tela de edição com o mixin de autoria, a gravação, a validação e a proteção contra recriar
inovação excluída.

```
T4 → T5 → T6 → T7
```

### Phase 3: Detalhe e exclusão (P1 nos links, P2 na exclusão)

Os links no detalhe, a confirmação e a exclusão.

```
T8 → T9 → T10
```

### Phase 4: Evidências transversais

Varredura da AD-009, acessibilidade, banco indisponível e CSRF. O comportamento vem das tasks
anteriores ou do Django; se a evidência acusar falta, o ajuste entra na mesma task.

```
T11 → T12 → T13 → T14
```

### Phase 5: Correções da validação, iteração 1

Fix tasks do `validation.md` (iteração 1, FAIL): quatro mutantes sobreviveram por lacuna de teste;
nenhum defeito de produção. Só arquivos de teste mudam, e os testes existentes só ficam mais fortes
(mais contas, mais cláusulas), nunca mais fracos.

```
T15 → T16 → T17 → T18
```

---

## Task Breakdown

### T1: `Inovacao.pode_ser_alterada_por` — a regra de autoria ✅

**What**: O método do modelo que diz se uma conta pode editar ou excluir a inovação (RN05, RNF07, AD-009).
**Where**: `inovacoes/models.py`
**Depends on**: None
**Reuses**: `Usuario.is_administrador` (`contas/models.py:85`, AD-004); fixtures `autor`, `criar_inovacao` de `inovacoes/tests/conftest.py`
**Requirement**: EDEX-17, EDEX-19, EDEX-25 (núcleo da regra; as rotas provam nas T4, T5, T9, T10)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `pode_ser_alterada_por(self, usuario) -> bool` = `usuario.is_authenticated and (usuario.is_administrador or self.autor_id == usuario.pk)`, com comentário citando RN05 e AD-009
- [x] `inovacoes/tests/conftest.py` ganha as fixtures `terceiro` (`USUARIO`, username `bruno`, sem nome) e `administrador` (`ADMINISTRADOR`, username `carla`), que as tasks seguintes usam
- [x] Testes de integração em `inovacoes/tests/test_permissoes.py`: autor `USUARIO` → True; autor `ADMINISTRADOR` → True; terceiro `USUARIO` → False; terceiro `ADMINISTRADOR` → True; `AnonymousUser()` → False sem `AttributeError`; `USUARIO` terceiro com `is_staff=True` e com `is_superuser=True` → False (AD-009: o perfil é o único critério); `ADMINISTRADOR` terceiro rebaixado a `USUARIO` e recarregado do banco → False (EDEX-25); a chamada com a inovação carregada executa 0 consultas (`django_assert_num_queries(0)`)
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: ~389 testes passam (+9)

**Tests**: integration
**Gate**: full

**Commit**: `feat(inovacoes): adiciona a regra de autoria para alterar inovacoes`

**Status**: ✅ Complete — 389 passed (+9); is_staff e is_superuser parametrizados num teste só; o teste de zero consultas recarrega a inovação do banco para não usar o autor em cache

---

### T2: `GravacaoComTituloUnicoMixin` extraído do cadastro ✅

**What**: O tratamento da gravação em transação, da corrida na constraint de título (INOV-25) e da mensagem de sucesso sai de `InovacaoCreateView.form_valid` para um mixin, sem mudança de comportamento.
**Where**: `inovacoes/views.py`
**Depends on**: T1
**Reuses**: corpo atual de `InovacaoCreateView.form_valid` e `_mensagem_de_titulo_duplicado()` (`inovacoes/views.py:13-50`)
**Requirement**: INOV-25, INOV-28 (mantidos); base de EDEX-06 e EDEX-14

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `GravacaoComTituloUnicoMixin` com `mensagem_de_sucesso` (formato com `{titulo}`), `gravar(form)` (padrão `form.save()`) e `form_valid(form)` como no design: `transaction.atomic()`, `IntegrityError` só da `inovacao_titulo_unico_por_unidade` vira erro de campo, as demais sobem
- [x] `InovacaoCreateView` herda o mixin com `mensagem_de_sucesso = "Inovação “{titulo}” cadastrada com sucesso."`; autor atribuído antes da gravação (INOV-04); `get_initial()` intacto (INOV-39)
- [x] Nenhum teste existente alterado: `test_views_cadastro.py` e `test_constraints.py` (INOV-25, INOV-28, INOV-43) passam como estão
- [x] Gate check passa: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q`
- [x] Test count: ~389 testes passam (+0: refatoração provada pela suíte da F2)

**Tests**: e2e
**Gate**: build

**Commit**: `refactor(inovacoes): extrai a gravacao com titulo unico do cadastro`

**Status**: ✅ Complete — 389 passed (+0); refatoração provada pela suíte da F2 sem alteração (INOV-25, INOV-28); o autor é atribuído num gravar() próprio do cadastro. Build gate verde. EDEX-06 e EDEX-14 seguem Pending na traceability até a T5 e a T6, que as provam

---

### T3: Template do formulário parametrizado ✅

**What**: `inovacao_form.html` passa a ler título da página, texto do botão e alvo do "Cancelar" do contexto; o cadastro os fornece com os valores atuais.
**Where**: `inovacoes/templates/inovacoes/inovacao_form.html`
**Depends on**: T2
**Reuses**: `InovacaoCreateView.get_context_data` (acrescenta `titulo_pagina`, `rotulo_botao`, `url_cancelar`)
**Requirement**: base de EDEX-01 e EDEX-16; INOV-36/INOV-37 (mantidos)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `{% block title %}` e `h1` = `{{ titulo_pagina }}`; botão = `{{ rotulo_botao }}`; "Cancelar" → `{{ url_cancelar }}`; resumo da INOV-30 e o loop de campos inalterados
- [x] `InovacaoCreateView.get_context_data` passa `"Cadastrar inovação"`, `"Salvar"` e `reverse("inovacoes:lista")`
- [x] Teste e2e novo em `inovacoes/tests/test_views_cadastro.py`: `<title>` começa com "Cadastrar inovação" e o `h1` é "Cadastrar inovação" (o `<title>` não tinha prova); os testes existentes do botão "Salvar" e do "Cancelar" (`href="/inovacoes/"`) passam sem alteração
- [x] Gate check passa: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q`
- [x] Test count: ~390 testes passam (+1)

**Tests**: e2e
**Gate**: build

**Commit**: `refactor(inovacoes): parametriza titulo, botao e cancelar do formulario`

**Status**: ✅ Complete — 390 passed (+1); não existia teste do texto do botão "Salvar", então o teste novo também afirma o único botão do formulário (o cabeçalho tem o "Sair"); os testes do "Cancelar" (INOV-36, INOV-37) passam sem alteração. Build gate verde. EDEX-01 e EDEX-16 seguem Pending até a T4

---

### T4: Tela de edição com o mixin de autoria (GET) ✅

**What**: A rota `editar`, o `AlteracaoDeInovacaoMixin` (404 → 403 no `dispatch()`), a página de acesso negado e o GET da `InovacaoUpdateView`.
**Where**: `inovacoes/views.py`
**Depends on**: T3
**Reuses**: `Inovacao.pode_ser_alterada_por` (T1); template parametrizado (T3); `inovacao_nao_encontrada.html` (F3); `UpdateView`
**Requirement**: EDEX-01, EDEX-02, EDEX-16, EDEX-17, EDEX-19 (editar), EDEX-20 (rota de edição), EDEX-21, EDEX-25, EDEX-26 (GET), EDEX-27 (GET)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `_inovacao_nao_encontrada(request)` extraída; `InovacaoDetailView.get()` passa a usá-la (testes da CONS-15 sem alteração)
- [x] `AlteracaoDeInovacaoMixin` como no design: `queryset` com `select_related("unidade", "categoria")`, `context_object_name = "inovacao"`, `dispatch()` com 404 e depois 403 (`render(..., "inovacoes/acesso_negado.html", {"inovacao": ...}, status=403)`), `get_object()` reaproveitando o `self.object`
- [x] `inovacoes/templates/inovacoes/acesso_negado.html`: `<title>`/`h1` "Acesso negado", os dois textos da EDEX-20 e o link "Voltar para a inovação" → detalhe
- [x] `InovacaoUpdateView(AlteracaoDeInovacaoMixin, GravacaoComTituloUnicoMixin, UpdateView)` com `form_class = InovacaoForm`, o template parametrizado e o contexto "Editar inovação" / "Salvar alterações" / `get_absolute_url()`; `path("<int:pk>/editar/", ..., name="editar")` em `inovacoes/urls.py`
- [x] Testes e2e em `inovacoes/tests/test_views_edicao.py`: autor `USUARIO` → 200, `<title>` e `h1` "Editar inovação", exatamente os sete campos e nenhum `status` (EDEX-01); os sete valores salvos pré-preenchidos, inclusive um contato diferente do pré-preenchimento da INOV-39 (EDEX-02); "Cancelar" com `href` do detalhe e, seguido, o detalhe 200 com a inovação intacta (EDEX-16); `administrador` na inovação do `autor` → 200 (EDEX-17); autor `ADMINISTRADOR` → 200 (EDEX-19); **`terceiro` → 403, template `acesso_negado.html`, os dois textos e o link "Voltar para a inovação" (EDEX-20, EDEX-21)**; administrador rebaixado a `USUARIO` → 403 na requisição seguinte (EDEX-25); id inexistente → 404 com "Inovação não encontrada." (EDEX-27); anônimo → login com `next=/inovacoes/<id>/editar/` (EDEX-26)
- [x] A varredura de `contas/tests/test_controle_acesso.py` passa sem alteração e já inclui `/inovacoes/1/editar/`
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: ~399 testes passam (+9)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(inovacoes): adiciona a tela de edicao restrita ao autor e ao administrador`

**Status**: ✅ Complete — 399 passed (+9); recusa renderizada pela view com status=403, sem PermissionDenied nem 403.html global; testes da CONS-15 sem alteração; a varredura da AD-006 já pega /inovacoes/1/editar/. O teste da EDEX-02 afirma o value do contato, porque a ajuda do campo cita "Ana Souza (ana@x.com)" como exemplo

---

### T5: Gravação da edição (POST válido) e POST negado ✅

**What**: O POST válido da edição atualiza a mesma inovação e termina no detalhe com a mensagem; o POST de terceiro e o do anônimo não alteram nada.
**Where**: `inovacoes/views.py`
**Depends on**: T4
**Reuses**: `GravacaoComTituloUnicoMixin` (T2); `UpdateView.get_success_url()` → `get_absolute_url()`
**Requirement**: EDEX-04, EDEX-05, EDEX-06, EDEX-07, EDEX-08, EDEX-15, EDEX-18, EDEX-19 (POST), EDEX-22, EDEX-26 (POST)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `InovacaoUpdateView.mensagem_de_sucesso = "Inovação “{titulo}” atualizada com sucesso."`; nenhum `success_url` (usa `get_absolute_url()`)
- [x] Testes e2e em `inovacoes/tests/test_views_edicao.py`: POST válido com espaços nas pontas atualiza a mesma linha, com os valores aparados, e `Inovacao.objects.count()` não muda (EDEX-04); resposta 302 para `/inovacoes/<id>/` (EDEX-05); seguindo o redirect, "Inovação “<título novo>” atualizada com sucesso." dentro de `role="status"` (EDEX-06); recarregar o detalhe não mostra a mensagem (EDEX-07); POST com `autor`, `status` e `data_criacao` forjados mantém os três (EDEX-08); `administrador` edita a inovação do `autor`: valores mudam, autor e `data_criacao` iguais e o detalhe diz "Cadastrada por Ana Souza em <data original>" (EDEX-18); autor `ADMINISTRADOR` grava (EDEX-19); duas edições em sequência → valem as da segunda (EDEX-15); **`terceiro` faz POST com dados válidos → 403 e todos os campos da linha iguais aos de antes, comparados campo a campo (EDEX-22)**; anônimo faz POST → login e linha intacta (EDEX-26)
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: ~409 testes passam (+10)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(inovacoes): grava a edicao e nega o envio de terceiros`

**Status**: ✅ Complete — 409 passed (+10); a inovação dos testes tem data_criacao fixa (01/09/2026 15:00 UTC) para provar que a data não muda; a recusa do terceiro compara Inovacao.objects.values() antes e depois

---

### T6: Validação e unicidade de título na edição ✅

**What**: A edição rejeita dados inválidos com as mensagens do cadastro, aceita o próprio título, recusa o título de outra inovação da unidade, trata a corrida sem 500 e mantém a busca coerente.
**Where**: `inovacoes/tests/test_views_edicao.py`
**Depends on**: T5
**Reuses**: `InovacaoForm`, `Inovacao.validate_constraints` e `Inovacao.save()` da F2/F3 (AD-008); `GravacaoComTituloUnicoMixin` (T2); o padrão de simulação de `IntegrityError` dos testes da INOV-25
**Requirement**: EDEX-09, EDEX-10, EDEX-11, EDEX-12, EDEX-13, EDEX-14

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Testes e2e: título e problema vazios → 200, as mensagens da INOV-09 em cada campo e o resumo "Não foi possível salvar a inovação. Corrija os campos indicados." em `role="alert"` (EDEX-09); os demais campos voltam com o valor enviado e a linha no banco fica igual (EDEX-09, EDEX-10); unidade inexistente → "Selecione uma unidade da lista." (EDEX-09); título com 151 caracteres → "Use no máximo 150 caracteres (você digitou 151)." (EDEX-09); salvar com o mesmo título e com o título só em caixa diferente → aceito (EDEX-12, parametrizado); título de outra inovação da mesma unidade, em caixa diferente → recusado com a mensagem da INOV-22 (EDEX-13); título de inovação de outra unidade → aceito; título que difere só por acento → aceito (INOV-27); `IntegrityError` da constraint simulado na gravação → 200 com a mensagem da EDEX-13, nunca 500 (EDEX-14); trocar o problema e buscar pela palavra nova acha a inovação e pela palavra só do texto antigo não acha (`/inovacoes/?q=…`, EDEX-11)
- [x] Se algum teste falhar, o ajuste entra nesta task, na view ou no mixin
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: ~420 testes passam (+11)

**Tests**: e2e
**Gate**: full

**Commit**: `test(inovacoes): prova a validacao e a unicidade de titulo na edicao`

**Status**: ✅ Complete — 419 passed (+10); nenhum ajuste de código: a F2, a T2 e o UpdateView já cumpriam as ACs. A corrida da EDEX-14 é simulada neutralizando validate_constraints, como na INOV-25; a busca da EDEX-11 usa o context da listagem

---

### T7: Edição de inovação excluída não a recria ✅

**What**: `InovacaoUpdateView.gravar()` trava a linha com `select_for_update` antes do `save()`; linha ausente responde com o 404 da CONS-15.
**Where**: `inovacoes/views.py`
**Depends on**: T6
**Reuses**: `_inovacao_nao_encontrada` (T4); a transação aberta pelo `GravacaoComTituloUnicoMixin` (T2)
**Requirement**: EDEX-27 (POST), EDEX-29

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `gravar(form)` faz `Inovacao.objects.select_for_update().filter(pk=self.object.pk).exists()` dentro da transação; ausente → a view responde `_inovacao_nao_encontrada(request)` sem chamar `form.save()`
- [x] Testes e2e: POST para id inexistente → 404 com "Inovação não encontrada." (EDEX-27); abrir o formulário, apagar a inovação e enviar → 404 e `Inovacao.objects.count() == 0` (EDEX-29, sequencial); inovação apagada entre o `dispatch()` e a gravação, simulada com `monkeypatch` no `form_valid` para apagar a linha antes do `super()` → 404 e nenhuma linha recriada com o mesmo `pk` (EDEX-29, mesma requisição)
- [x] Gate check passa: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` (fecha a Fase 2)
- [x] Test count: ~423 testes passam (+3)

**Tests**: e2e
**Gate**: build

**Commit**: `fix(inovacoes): impede que a edicao recrie uma inovacao excluida`

**Status**: ✅ Complete — 422 passed (+3); gravar() levanta Http404 quando a linha travada não existe e o form_valid() da edição responde com _inovacao_nao_encontrada; nenhum DatabaseError é capturado (EDEX-44). O teste da mesma requisição falhou antes da trava (a inovação era recriada com o mesmo pk). Build gate verde, fecha a Fase 2

---

### T8: Link "Editar" no detalhe só para quem pode alterar ✅

**What**: O detalhe recebe `pode_alterar` e mostra "Editar" ao autor e ao administrador.
**Where**: `inovacoes/templates/inovacoes/inovacao_detail.html`
**Depends on**: T7
**Reuses**: `Inovacao.pode_ser_alterada_por` (T1); `InovacaoDetailView.get_context_data`
**Requirement**: EDEX-03, EDEX-24 (Editar)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `InovacaoDetailView.get_context_data` acrescenta `pode_alterar`; o template mostra `<a href="{% url 'inovacoes:editar' inovacao.pk %}">Editar</a>` logo após "Cadastrada por…" só com ele verdadeiro
- [x] Testes e2e em `inovacoes/tests/test_views_detalhe.py`: autor vê "Editar" com `href="/inovacoes/<id>/editar/"` (EDEX-03); `administrador` vê na inovação do `autor`; **`terceiro` não vê o link (EDEX-24)**; o detalhe continua com o mesmo número de consultas (o `autor` já vem no `select_related`)
- [x] Testes existentes do detalhe (CONS-12 a CONS-18) passam sem alteração
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: ~426 testes passam (+3)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(inovacoes): mostra o link de edicao no detalhe para quem pode alterar`

**Status**: ✅ Complete — 427 passed (+5); pode_alterar vem de Inovacao.pode_ser_alterada_por no get_context_data do detalhe; a contagem de consultas foi medida antes da mudança (6) e é afirmada para o autor e o terceiro; testes da CONS-12 a CONS-18 sem alteração

---

### T9: Confirmação da exclusão (GET) e link "Excluir" ✅

**What**: A rota `excluir`, a `InovacaoDeleteView` com o mixin de autoria, a página de confirmação e o link "Excluir" no detalhe.
**Where**: `inovacoes/views.py`
**Depends on**: T8
**Reuses**: `AlteracaoDeInovacaoMixin` (T4); `DeleteView`; `pode_alterar` (T8)
**Requirement**: EDEX-19 (excluir), EDEX-20 (rota de exclusão), EDEX-24 (Excluir), EDEX-28, EDEX-30, EDEX-31, EDEX-32, EDEX-33, EDEX-34, EDEX-36

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `InovacaoDeleteView(AlteracaoDeInovacaoMixin, DeleteView)` com `success_url = reverse_lazy("inovacoes:lista")`; `path("<int:pk>/excluir/", ..., name="excluir")`
- [x] `inovacoes/templates/inovacoes/inovacao_confirm_delete.html` como no design: `<title>`/`h1` "Excluir inovação", o texto da EDEX-30, `<form method="post">` com `{% csrf_token %}` e o botão "Excluir definitivamente", link "Cancelar" → detalhe
- [x] `inovacao_detail.html` mostra `<a href="{% url 'inovacoes:excluir' inovacao.pk %}">Excluir</a>` junto de "Editar", sob o mesmo `pode_alterar`
- [x] Testes e2e em `inovacoes/tests/test_views_exclusao.py`: autor → 200, `h1` "Excluir inovação" e "Você vai excluir a inovação “Controle de Caixa” (Teste Unidade · Teste Categoria). Esta ação não pode ser desfeita." (EDEX-30); `administrador` na inovação do `autor` → 200; autor `ADMINISTRADOR` → 200 (EDEX-19); formulário com `method="post"`, sem `action` ou com `action` da própria rota, e o botão "Excluir definitivamente" (EDEX-32); "Cancelar" com `href` do detalhe e, seguido, a inovação continua (EDEX-33, EDEX-34); o GET não apaga, nem repetido (EDEX-36); **`terceiro` → 403 com a página de acesso negado (EDEX-20)**; id inexistente → 404 (EDEX-28)
- [x] Testes e2e em `inovacoes/tests/test_views_detalhe.py`: autor e `administrador` veem "Excluir" com `href="/inovacoes/<id>/excluir/"` (EDEX-31); **`terceiro` não vê (EDEX-24)**
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: ~435 testes passam (+9)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(inovacoes): adiciona a confirmacao de exclusao de inovacao`

**Status**: ✅ Complete — 438 passed (+11); InovacaoDeleteView só declara success_url, o mixin faz o 404 e o 403; o teste da EDEX-32 isola o form da confirmação do form do "Sair" do cabeçalho; a varredura da AD-006 já pega /inovacoes/1/excluir/ sem alteração

---

### T10: Exclusão definitiva (POST) e POST negado ✅

**What**: O POST da confirmação apaga a inovação e leva à lista com a mensagem; o POST de terceiro e o do anônimo não apagam.
**Where**: `inovacoes/views.py`
**Depends on**: T9
**Reuses**: `DeleteView.form_valid`; região `role="status"` do `base.html`; 404 da CONS-15
**Requirement**: EDEX-19 (POST), EDEX-23, EDEX-25 (POST), EDEX-26 (POST), EDEX-35, EDEX-37, EDEX-38, EDEX-39, EDEX-40

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `InovacaoDeleteView.form_valid` guarda o título, chama `super().form_valid(form)` e publica "Inovação “{titulo}” excluída com sucesso."
- [x] Testes e2e em `inovacoes/tests/test_views_exclusao.py`: autor faz POST → 302 para `/inovacoes/` e a linha não existe mais (EDEX-35, EDEX-37); a lista, a busca pelo título e a contagem da CONS-33 já não a incluem (EDEX-37); seguindo o redirect, a mensagem aparece em `role="status"` e some ao recarregar (EDEX-40); `administrador` apaga a inovação do `autor`; autor `ADMINISTRADOR` apaga (EDEX-19); segundo POST para o mesmo id → 404, nunca 500 (EDEX-38); o detalhe da apagada → 404 (EDEX-39); **`terceiro` faz POST → 403 e a inovação continua no banco (EDEX-23)**; administrador rebaixado faz POST na inovação do `autor` → 403 e ela continua (EDEX-25); anônimo faz POST → login e ela continua (EDEX-26)
- [x] Gate check passa: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` (fecha a Fase 3)
- [x] Test count: ~445 testes passam (+10)

**Tests**: e2e
**Gate**: build

**Commit**: `feat(inovacoes): exclui a inovacao confirmada e nega o envio de terceiros`

**Status**: ✅ Complete — 448 passed (+10); o form_valid guarda o título antes do super(), que apaga e redireciona; o segundo POST cai no 404 do mixin; o teste da EDEX-37 olha só a tabela, porque a lista mostra a mensagem com o título; o anônimo é provado em GET e POST. Build gate verde, fecha a Fase 3

---

### T11: Varredura de autoria das rotas de alteração (AD-009) ✅

**What**: Um teste que varre as rotas de `inovacoes` com `pk` e exige 403 a GET e POST de um terceiro `USUARIO`, sem mudança no banco, salvo a allowlist do detalhe.
**Where**: `inovacoes/tests/test_controle_autoria.py`
**Depends on**: T10
**Reuses**: o desenho de `contas/tests/test_controle_acesso.py` (`get_resolver`, `_rotas`, allowlist explícita); fixtures `terceiro` e `criar_inovacao`
**Requirement**: EDEX-20, EDEX-22, EDEX-23 (todas as rotas); mitigação da AD-009 (*Risks & Concerns* do design)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Coleta, pelo resolver, toda rota do namespace `inovacoes` cujo padrão tem `<int:pk>`; `ROTAS_DE_LEITURA = {"inovacoes:detalhe"}` é a única allowlist
- [x] Teste parametrizado (rota × GET/POST): `terceiro` logado recebe 403 e a linha da inovação, comparada campo a campo, fica igual (e continua existindo)
- [x] Teste de sanidade: a varredura encontra pelo menos `inovacoes:editar` e `inovacoes:excluir`, para que uma coleta vazia não passe em silêncio
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: ~450 testes passam (+5)

**Tests**: e2e
**Gate**: full

**Commit**: `test(inovacoes): varre as rotas de alteracao exigindo a regra de autoria`

**Status**: ✅ Complete — 453 passed (+5); as rotas vêm do resolver na coleta (namespace inovacoes, padrão com <int:pk>), sem lista fixa; o POST manda dados válidos e diferentes dos salvos, para que uma regra quebrada gravasse; a sanidade exige que o detalhe seja visto e que editar e excluir estejam na varredura

---

### T12: Acessibilidade da edição, da confirmação e do acesso negado ✅

**What**: Evidência de EDEX-41 a EDEX-43 nas três páginas novas.
**Where**: `inovacoes/tests/test_views_acessibilidade_alteracao.py`
**Depends on**: T11
**Reuses**: os helpers e o padrão de `inovacoes/tests/test_views_acessibilidade.py` e `test_views_acessibilidade_consulta.py`
**Requirement**: EDEX-41, EDEX-42, EDEX-43

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Formulário de edição: todo campo com `label[for]` igual ao `id`; os obrigatórios com `required` e "(obrigatório)" no rótulo; texto de ajuda ligado por `aria-describedby`; com erro, `aria-invalid="true"` e o id da mensagem no `aria-describedby` (EDEX-41)
- [x] Nas três páginas (edição, confirmação, acesso negado; parametrizado): nenhum `tabindex` positivo e só controles nativos (`a`, `button`, `input`, `select`, `textarea`) como interativos; o `base.html` mantém a regra `:focus-visible` (EDEX-42)
- [x] Nas três páginas: um único `h1` e o `<title>` começando por "Editar inovação", "Excluir inovação" e "Acesso negado" (EDEX-43)
- [x] Se a evidência acusar falta, o ajuste no template entra nesta task
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: ~459 testes passam (+9)

**Tests**: e2e
**Gate**: full

**Commit**: `test(inovacoes): prova a acessibilidade da edicao e da exclusao`

**Status**: ✅ Complete — 466 passed (+13); nenhum ajuste de template: as três páginas já cumpriam as ACs. Reusa Pagina e PAPEIS_DE_CONTROLE de test_views_acessibilidade.py; o acesso negado é aberto pelo terceiro (403); EDEX-41 em quatro testes (rótulo, obrigatório, ajuda, erro)

---

### T13: Banco indisponível na edição e na exclusão ✅

**What**: Evidência da EDEX-44: página 500 sem detalhes da conexão e nada alterado ou apagado.
**Where**: `inovacoes/tests/test_views_erro_500.py`
**Depends on**: T12
**Reuses**: fixture `banco_fora_do_ar` e `DETALHE_DA_CONEXAO` do mesmo arquivo (variante que derruba `Inovacao.delete` para a exclusão)
**Requirement**: EDEX-44

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Edição: `Inovacao.save` levantando `OperationalError` no POST válido do autor → 500, página do projeto sem `DETALHE_DA_CONEXAO`, linha com os valores antigos
- [x] Exclusão: `Inovacao.delete` levantando `OperationalError` no POST do autor → 500, sem detalhes, inovação ainda no banco
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: ~461 testes passam (+2)

**Tests**: e2e
**Gate**: full

**Commit**: `test(inovacoes): prova a pagina 500 na edicao e na exclusao com o banco fora do ar`

**Status**: ✅ Complete — 468 passed (+2); nenhum ajuste de código; um teste parametrizado (edição derruba Inovacao.save, exclusão derruba Inovacao.delete). Não usa a fixture banco_fora_do_ar, que derruba o save() no setup e impediria o criar_inovacao; repete o padrão do teste da CONS-53 com o mesmo DETALHE_DA_CONEXAO

---

### T14: CSRF na edição e na exclusão ✅

**What**: Evidência da EDEX-45: POST sem token CSRF válido responde 403 e não altera nem apaga.
**Where**: `inovacoes/tests/test_controle_autoria.py`
**Depends on**: T13
**Reuses**: `Client(enforce_csrf_checks=True)` como em `contas/tests/test_views_login.py:66`
**Requirement**: EDEX-45

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Autor logado num `Client(enforce_csrf_checks=True)`, POST sem token em `/editar/` → 403 e linha igual; em `/excluir/` → 403 e inovação no banco
- [x] Gate check passa: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` (fecha a Fase 4 e a feature)
- [x] Test count: ~463 testes passam (+2)

**Tests**: e2e
**Gate**: build

**Commit**: `test(inovacoes): prova a protecao csrf na edicao e na exclusao`

**Status**: ✅ Complete — 470 passed (+2); nenhum ajuste de código: o CsrfViewMiddleware recusa antes da view. O teste parametrizado (editar, excluir) usa o próprio autor, então o 403 só pode vir do CSRF, e afirma que não é a página de acesso negado. Build gate verde, fecha a Fase 4

---

### T15: Varredura da AD-009 também para `USUARIO` com `is_staff` e `is_superuser` (Fix 1)

**What**: O teste de recusa da varredura passa a rodar para três contas não autoras sem perfil de administrador: `terceiro`, `USUARIO` com `is_staff=True` e `USUARIO` com `is_superuser=True`.
**Where**: `inovacoes/tests/test_controle_autoria.py`
**Depends on**: T14
**Reuses**: `test_terceiro_recebe_403_e_nada_muda` (T11); a comparação `values()` antes/depois
**Requirement**: EDEX-20, EDEX-22, EDEX-23 (AD-009: `is_staff`/`is_superuser` não contam)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [ ] A recusa é parametrizada por conta (3) × rota × método, com 403 e a linha igual campo a campo depois de cada requisição
- [ ] Mutante M23b (`AlteracaoDeInovacaoMixin.dispatch` aceita `request.user.is_superuser`) aplicado num rascunho falha a suíte; descartado em seguida
- [ ] Gate check passa: `.venv/bin/pytest -q`
- [ ] Test count: ~478 testes passam (+8)

**Tests**: e2e
**Gate**: full

**Commit**: `test(inovacoes): varre as rotas de alteracao com contas staff e superusuario`

---

### T16: Links do detalhe escondidos de staff, superusuário e administrador rebaixado (Fix 2)

**What**: Os testes que escondem "Editar" e "Excluir" passam a cobrir as mesmas três contas da T15 e o administrador rebaixado.
**Where**: `inovacoes/tests/test_views_detalhe.py`
**Depends on**: T15
**Reuses**: os testes de link da T8 e da T9
**Requirement**: EDEX-24, EDEX-25

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [ ] Nenhum dos dois links aparece para `terceiro`, `USUARIO` com `is_staff=True` e `USUARIO` com `is_superuser=True` (parametrizado)
- [ ] Um `ADMINISTRADOR` não autor vê os links e, depois de rebaixado a `USUARIO`, deixa de vê-los na requisição seguinte
- [ ] Mutantes M22 e M22b (`pode_alterar` também para `is_staff` / `is_superuser`) aplicados num rascunho falham a suíte; descartados em seguida
- [ ] Gate check passa: `.venv/bin/pytest -q`
- [ ] Test count: ~483 testes passam (+5)

**Tests**: e2e
**Gate**: full

**Commit**: `test(inovacoes): esconde as acoes do detalhe de staff e superusuario sem perfil`

---

### T17: Campo só com espaços e busca por título e solução na edição (Fix 3)

**What**: As cláusulas da EDEX-09 (INOV-10) e da EDEX-11 (título e solução) ganham teste na rota de edição.
**Where**: `inovacoes/tests/test_views_edicao.py`
**Depends on**: T16
**Reuses**: os testes da T6
**Requirement**: EDEX-09, EDEX-10, EDEX-11

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [ ] Edição com `solucao="   "` → 200, "Descreva a solução aplicada." no campo e a linha intacta (EDEX-09 via INOV-10, EDEX-10)
- [ ] Trocar o título e, em outro caso, a solução: a busca acha pela palavra nova e não acha pela palavra só do texto antigo (EDEX-11; parametrizado com o caso do problema que já existe, sem enfraquecê-lo)
- [ ] Gate check passa: `.venv/bin/pytest -q`
- [ ] Test count: ~486 testes passam (+3)

**Tests**: e2e
**Gate**: full

**Commit**: `test(inovacoes): prova o campo so com espacos e a busca apos editar titulo e solucao`

---

### T18: Varredura da AD-009 independente do texto `<int:pk>` (Fix 4)

**What**: A coleta da varredura passa a pegar toda rota do namespace `inovacoes` que capture parâmetro e falha quando o parâmetro não é `pk`.
**Where**: `inovacoes/tests/test_controle_autoria.py`
**Depends on**: T17
**Reuses**: `_rotas_com_pk` e o teste de sanidade da T11
**Requirement**: EDEX-20, EDEX-22, EDEX-23 (AD-009: rota nova de alteração não escapa da varredura)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [ ] A coleta usa os conversores capturados do padrão (`pattern.converters`), não o texto literal; rota de `inovacoes` com parâmetro diferente de `pk` faz a coleta falhar com mensagem clara
- [ ] Mutante M24 (rota `<int:id>/status/` sem guarda) e mutante M18 (rota `<int:pk>/...` sem guarda) aplicados num rascunho falham a suíte; descartados em seguida
- [ ] Gate check passa: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` (fecha a Fase 5)
- [ ] Test count: ~487 testes passam (+1 ou mais)

**Tests**: e2e
**Gate**: build

**Commit**: `test(inovacoes): coleta as rotas da varredura pelos parametros capturados`

---

## Phase Execution Map

```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5

Phase 1:  T1 → T2 → T3
Phase 2:  T4 → T5 → T6 → T7
Phase 3:  T8 → T9 → T10
Phase 4:  T11 → T12 → T13 → T14
Phase 5:  T15 → T16 → T17 → T18
```

Arcos de fronteira entre fases (a primeira task de cada fase depende da última da anterior):

```
T3  → T4
T7  → T8
T10 → T11
T14 → T15
```

A execução é estritamente sequencial — não há paralelismo dentro de uma fase.

**Empacotamento previsto no Execute:** 14 tasks ⇒ com orçamento de ~7 por lote e corte apenas em
fronteira de fase: **lote 1** = Fases 1+2 (7 tasks: fundação e edição), **lote 2** = Fases 3+4 (7
tasks: exclusão e evidências). Mais de um lote ⇒ o Execute deve **oferecer** sub-agentes antes de
começar.

---

## Task Granularity Check

| Task | Scope | Status |
| ---- | ----- | ------ |
| T1 | 1 método do modelo (+ 2 fixtures no `conftest.py`) | ✅ Granular |
| T2 | 1 mixin extraído de 1 view, mesmo arquivo | ✅ Granular |
| T3 | 1 template (+ 3 chaves de contexto na view do cadastro) | ✅ Granular |
| T4 | 1 tela = mixin + view + rota + template de acesso negado | ⚠️ 4 arquivos, coeso — ver nota |
| T5 | 1 atributo da view (a gravação vem do mixin) + testes | ✅ Granular |
| T6 | 1 arquivo de teste (o comportamento vem da F2 e da T2) | ✅ Granular |
| T7 | 1 método da view | ✅ Granular |
| T8 | 1 trecho de template + 1 chave de contexto | ✅ Granular |
| T9 | 1 tela = view + rota + template (+ 1 link no detalhe) | ⚠️ 4 arquivos, coeso — ver nota |
| T10 | 1 método da view | ✅ Granular |
| T11, T12, T13, T14 | 1 arquivo de teste cada (o código já existe) | ✅ Granular |
| T15, T16, T17, T18 | 1 arquivo de teste cada (correções da validação) | ✅ Granular |

**Nota sobre T4 e T9:** uma view Django não é testável sem rota e template. Na T4, o mixin também não
é testável sem uma view que o use, e separar a checagem de autoria da tela deixaria um commit em que
a edição abre para qualquer usuário. O `Where` nomeia o arquivo principal; os demais estão no `Done
when` e cobertos pelos mesmos testes. É o mesmo merge backward da T2 e da T4 da F3.

**Nota sobre T6, T11, T12, T13 e T14:** o comportamento vem do Django, da F2 ou das tasks anteriores.
A task é a evidência das ACs; se a evidência acusar falta, o ajuste entra na mesma task.

---

## Diagram-Definition Cross-Check

| Task | Depends On (task body) | Diagram Shows | Status |
| ---- | ---------------------- | ------------- | ------ |
| T1 | None | (início da Fase 1) | ✅ Match |
| T2 | T1 | T1 → T2 | ✅ Match |
| T3 | T2 | T2 → T3 | ✅ Match |
| T4 | T3 | T3 → T4 (arco de fronteira) | ✅ Match |
| T5 | T4 | T4 → T5 | ✅ Match |
| T6 | T5 | T5 → T6 | ✅ Match |
| T7 | T6 | T6 → T7 | ✅ Match |
| T8 | T7 | T7 → T8 (arco de fronteira) | ✅ Match |
| T9 | T8 | T8 → T9 | ✅ Match |
| T10 | T9 | T9 → T10 | ✅ Match |
| T11 | T10 | T10 → T11 (arco de fronteira) | ✅ Match |
| T12 | T11 | T11 → T12 | ✅ Match |
| T13 | T12 | T12 → T13 | ✅ Match |
| T14 | T13 | T13 → T14 | ✅ Match |
| T15 | T14 | T14 → T15 (arco de fronteira) | ✅ Match |
| T16 | T15 | T15 → T16 | ✅ Match |
| T17 | T16 | T16 → T17 | ✅ Match |
| T18 | T17 | T17 → T18 | ✅ Match |

Nenhuma dependência aponta para uma fase posterior.

---

## Test Co-location Validation

| Task | Code Layer Created/Modified | Matrix Requires | Task Says | Status |
| ---- | --------------------------- | --------------- | --------- | ------ |
| T1: regra de autoria | Regra do modelo | integration | integration | ✅ OK |
| T2: mixin de gravação | Views | e2e | e2e (suíte da F2) | ✅ OK |
| T3: template parametrizado | Templates + view do cadastro | e2e | e2e | ✅ OK |
| T4: tela de edição (GET) | Views, rotas, templates | e2e | e2e | ✅ OK |
| T5: gravação da edição | Views | e2e | e2e | ✅ OK |
| T6: validação na edição | Views (evidência) | e2e | e2e | ✅ OK |
| T7: edição de inovação excluída | Views | e2e | e2e | ✅ OK |
| T8: link "Editar" | Template + view do detalhe | e2e | e2e | ✅ OK |
| T9: confirmação da exclusão | Views, rotas, templates | e2e | e2e | ✅ OK |
| T10: exclusão definitiva | Views | e2e | e2e | ✅ OK |
| T11: varredura AD-009 | Views (evidência) | e2e | e2e | ✅ OK |
| T12: acessibilidade | Templates (evidência) | e2e | e2e | ✅ OK |
| T13: banco indisponível | Views (evidência) | e2e | e2e | ✅ OK |
| T14: CSRF | Views (evidência) | e2e | e2e | ✅ OK |
| T15–T18: correções da iteração 1 | Views (evidência) | e2e | e2e | ✅ OK |

Nenhuma task tem `Tests: none`.

---

## Requirement Coverage

| Requisito | Tasks |
| --------- | ----- |
| EDEX-01, 02, 16 | T4 |
| EDEX-03 | T8 |
| EDEX-04 … 08, 15, 18 | T5 |
| EDEX-09 … 14 | T6 |
| EDEX-17 | T1, T4 |
| EDEX-19 | T1, T4, T5, T9, T10 |
| EDEX-20 | T4, T9, T11 |
| EDEX-21 | T4 |
| EDEX-22 | T5, T11 |
| EDEX-23 | T10, T11 |
| EDEX-24 | T8, T9 |
| EDEX-25 | T1, T4, T10 |
| EDEX-26 | T4, T5, T10 (+ varredura da AD-006, sem alteração) |
| EDEX-27 | T4 (GET), T7 (POST) |
| EDEX-28, 30 … 34, 36 | T9 |
| EDEX-29 | T7 |
| EDEX-35, 37 … 40 | T10 |
| EDEX-41 … 43 | T12 |
| EDEX-44 | T13 |
| EDEX-45 | T14 |

**Coverage:** 45 de 45 requisitos mapeados para tasks.
