# Ciclo de Vida do Status (F5) — Tasks

## Execution Protocol (MANDATORY -- do not skip)

Implement these tasks with the `tlc-spec-driven` skill: **activate it by name and follow its Execute flow and Critical Rules.** Do not search for skill files by filesystem path. The skill is the source of truth for the full flow (per-task cycle, sub-agent delegation, adequacy review, Verifier, discrimination sensor).

**If the skill cannot be activated, STOP and tell the user - do not proceed without it.**

---

**Spec**: `.specs/features/ciclo-de-vida-status/spec.md`
**Design**: `.specs/features/ciclo-de-vida-status/design.md`
**Status**: Approved (2026-10-18)

**Stack fixado**: Django 5.2.17 · PostgreSQL 16 (AD-003) · pytest + pytest-django · Ruff — o mesmo da F1 a F4.

**Caso central — "nenhum caminho pula, repete ou desfaz um estágio":** coberto em camadas, cada uma
numa task diferente, para que nenhuma sozinha seja a única prova:

| Camada | Task | O que prova |
| ------ | ---- | ----------- |
| Banco | T1 | O CHECK recusa todo par (anterior, novo) fora das duas transições |
| Regra no modelo | T2 | `avancar_status` avança um passo, recusa status visto desatualizado e estágio final, trava a linha (`FOR UPDATE`) e grava status e histórico juntos |
| Rota | T4 | Reenvio, duplo clique e mudança entre o `dispatch()` e a trava terminam em aviso, sem gravar |
| Edição e cadastro | T9 | O formulário de edição e o cadastro não mexem no ciclo |

**Lições aplicadas:** L-003 (T8: `USUARIO` com `is_staff`/`is_superuser` recebe 403 na rota e não vê
o link) · L-005 (toda AC com efeito em tela é afirmada pelo `client`, não só no modelo: T3 a T7).

---

## Test Coverage Matrix

> Gerada a partir do código, das diretrizes do projeto e da spec — confirmar antes do Execute.
> **Guidelines encontradas: nenhuma.** Não existe `AGENTS.md`, `CONTRIBUTING.md` nem workflow de CI;
> o `pyproject.toml` só configura o pytest (marcadores, `--strict-markers`) e o Ruff, sem limite de
> cobertura. Valem os **strong defaults**: toda AC e todo edge case da spec têm teste; rotas cobrem
> happy + edge + erro. Estilo, local e fixtures seguem as amostras de `inovacoes/tests/`
> (`conftest.py`, `test_constraints.py`, `test_permissoes.py`, `test_views_edicao.py`,
> `test_views_exclusao.py`, `test_views_detalhe.py`, `test_controle_autoria.py`,
> `test_views_sistema_design.py`, `test_views_erro_500.py`), que são o piso de profundidade.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| ---------- | ------------------ | -------------------- | ---------------- | ----------- |
| Modelo e constraints (`MudancaDeStatus`, `PROXIMO_STATUS`) | integration | Todo par de transição válido e inválido contra o PostgreSQL; `CASCADE` e `PROTECT`; ordenação (STAT-28, STAT-29, STAT-31) | `inovacoes/tests/test_ciclo_de_vida.py` | `.venv/bin/pytest -q` |
| Regra do modelo (`Inovacao.proximo_status`, `avancar_status`) | integration | Todo ramo 1:1 com as ACs: dois avanços, estágio final, status visto diferente/ausente/inválido, inovação apagada, `FOR UPDATE` emitido, atomicidade (STAT-07 a STAT-09, STAT-12 a STAT-15, STAT-18) | `inovacoes/tests/test_ciclo_de_vida.py` | `.venv/bin/pytest -q` |
| Views, rotas e templates (`inovacoes/views.py`, `urls.py`, `templates/inovacoes/*.html`) | e2e | Toda rota que a task adiciona ou altera: happy + todo edge case + erro, pelo `client`, para autor, administrador, terceiro `USUARIO` (inclusive staff/superuser) e anônimo; afirmar status e histórico no banco depois de toda recusa | `inovacoes/tests/test_views_status.py`, `test_views_detalhe.py`, `test_controle_autoria.py`, `test_views_acessibilidade_alteracao.py`, `test_views_erro_500.py` | `.venv/bin/pytest -q` |
| Folha de estilo (`templates/kira.css`) | e2e | Componentes novos presentes, sem cor nova fora do DS-08, regras da AD-010 (sem `="`, sem `<`) | `inovacoes/tests/test_views_sistema_design.py` | `.venv/bin/pytest -q` |
| Migration `0007` | none | — gerada por `makemigrations`; `makemigrations --check` no gate de build | — | build gate only |

## Gate Check Commands

> Gerados a partir do projeto — confirmar antes do Execute. Todos pelo `.venv/`, com o PostgreSQL 16
> na porta 5433 em execução.

| Gate Level | When to Use | Command |
| ---------- | ----------- | ------- |
| Quick | Não usado nesta feature (nenhuma task só com teste unitário) | `.venv/bin/pytest -q -m unit` |
| Full | Depois de toda task com teste de integração ou e2e | `.venv/bin/pytest -q` |
| Build | Ao fechar uma fase, e nas tasks que criam migration ou mexem em template/CSS compartilhado | `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` |

**Linha de base:** 574 testes coletados antes da T1 (`.venv/bin/pytest -q --co`, 2026-10-18). Rodar
`.venv/bin/pytest -q` no início do Execute para confirmar que todos passam.

**Testes de features anteriores que mudam:** **dois**, de propósito: `CONSULTAS_DO_DETALHE` em
`inovacoes/tests/test_views_detalhe.py` sobe de 6 para 7 (T6, design → Risks); e a contagem de telas
do DS-01 em `inovacoes/tests/test_views_sistema_design.py` sobe de 8 para 9 (T3, a tela nova
"Avançar status"; autorizada pelo usuário em 2026-10-18). Os testes de
sanidade da varredura (T8) e a fixture `paginas` do sistema de design (T7, T10) **ganham** a rota
nova, sem perder nada. Qualquer outro teste da F1 a F4 que precise mudar indica erro na task. As
contagens abaixo são estimativas; a regra dura é que a contagem nunca cai.

---

## Execution Plan

As fases são ordenadas e rodam em sequência — cada fase termina antes de a próxima começar, e as
tasks dentro de uma fase executam em ordem.

### Phase 1: Fundação — histórico e regra do ciclo no modelo

O modelo `MudancaDeStatus` com as constraints e o método que avança. Nenhuma tela.

```
T1 → T2
```

### Phase 2: Tela de avanço

A rota `/inovacoes/<pk>/status/`: confirmação (GET) e avanço (POST).

```
T3 → T4
```

### Phase 3: Detalhe e estilo

As seções "Ciclo de vida" e "Histórico de status" no detalhe, e os componentes na `kira.css`.

```
T5 → T6 → T7
```

### Phase 4: Evidências transversais

Autorização, integridade, acessibilidade, banco indisponível e CSRF. O comportamento vem das tasks
anteriores, do mixin da AD-009 ou do Django; se a evidência acusar falta, o ajuste entra na mesma task.

```
T8 → T9 → T10 → T11
```

---

## Task Breakdown

### T1: `MudancaDeStatus`, `PROXIMO_STATUS` e a migration 0007 ✅

**What**: O modelo do histórico com o CHECK de transição, `CASCADE` na inovação e `PROTECT` no responsável, a constante `PROXIMO_STATUS` e a migration gerada.
**Where**: `inovacoes/models.py`
**Depends on**: None
**Reuses**: `StatusInovacao` (`inovacoes/models.py:11`); padrão da `CheckConstraint inovacao_status_valido`; `on_delete=PROTECT` de `Inovacao.autor`; fixtures `autor`, `administrador`, `criar_inovacao` de `inovacoes/tests/conftest.py`
**Requirement**: STAT-28, STAT-29, STAT-31

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `PROXIMO_STATUS = {EM_TESTE: VALIDADA, VALIDADA: DISPONIVEL_PARA_REPLICACAO}` no nível de módulo, depois de `StatusInovacao`
- [x] `MudancaDeStatus` como no design (Data Models): `inovacao` (CASCADE, `related_name="mudancas_de_status"`), `status_anterior`, `status_novo` (choices de `StatusInovacao`), `responsavel` (`settings.AUTH_USER_MODEL`, PROTECT), `data` (`auto_now_add`), `ordering = ["data", "id"]`, CHECK `mudanca_de_status_transicao_valida` montado a partir de `PROXIMO_STATUS`
- [x] `inovacoes/migrations/0007_mudancadestatus.py` gerada por `makemigrations`; só cria a tabela
- [x] `MudancaDeStatus` **não** é registrado em `inovacoes/admin.py` (AD-007)
- [x] Testes de integração em `inovacoes/tests/test_ciclo_de_vida.py`: os dois pares válidos gravam; **cada um dos sete pares inválidos** (os 9 pares do produto 3×3 menos os 2 válidos) levanta `IntegrityError` ao gravar pelo ORM (STAT-31); excluir a inovação apaga os registros dela e não os de outra (STAT-28); excluir a conta responsável levanta `ProtectedError` e o registro continua (STAT-29); dois registros com a mesma `data` saem na ordem do `id`
- [x] Gate check passa: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q`
- [x] Test count: ~587 testes passam (+13)

**Tests**: integration
**Gate**: build

**Commit**: `feat(inovacoes): adiciona o historico de mudancas de status`

**Status**: ✅ Complete — 588 passed (+14); os sete pares inválidos parametrizados, mais um teste de sanidade da contagem; `__str__` acrescentado ao modelo (exigido pelo DJ008 do Ruff); o bloco Python do `design.md` foi formatado pelo Ruff, porque o `ruff format --check` do gate já falhava nele antes da T1. Build gate verde

---

### T2: `Inovacao.proximo_status` e `Inovacao.avancar_status` ✅

**What**: A propriedade do próximo estágio e o método que avança numa transação com trava, conferência do status visto e criação do histórico, com as exceções de recusa.
**Where**: `inovacoes/models.py`
**Depends on**: T1
**Reuses**: `PROXIMO_STATUS` e `MudancaDeStatus` (T1); `Inovacao.save(update_fields=...)` (AD-008)
**Requirement**: STAT-07, STAT-08, STAT-09, STAT-12, STAT-13, STAT-14, STAT-15, STAT-18 (núcleo; as rotas provam na T4)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `TransicaoDeStatusRecusada(Exception)`, `StatusDesatualizado(TransicaoDeStatusRecusada)` com `status_atual`, `UltimoEstagioDoCiclo(TransicaoDeStatusRecusada)`
- [x] `proximo_status` devolve `PROXIMO_STATUS.get(self.status)`
- [x] `avancar_status(self, *, por, status_visto)` como no design (passos 1 a 6), com comentário citando AD-011
- [x] Testes de integração em `inovacoes/tests/test_ciclo_de_vida.py`: `proximo_status` nos três estágios (`None` no último); "Em teste" → "Validada" e "Validada" → "Disponível para replicação", cada um com **um** registro com anterior, novo, `responsavel` e `data` preenchida (STAT-07, STAT-08, STAT-14); estágio final → `UltimoEstagioDoCiclo`, status igual e zero registros (STAT-10 no modelo); `status_visto` diferente, `None` e valor fora do enum → `StatusDesatualizado` com `status_atual` = gravado, nada gravado (STAT-12); dois `avancar_status` seguidos com o mesmo `status_visto` → o segundo recusa, status avançou **um** estágio e há **um** registro (STAT-13); status mudado no banco depois de carregar a instância → recusa pelo valor gravado, não pelo da instância; `CaptureQueriesContext` mostra `FOR UPDATE` na leitura do status (STAT-13); falha forçada ao criar o registro (`mock` em `MudancaDeStatus.objects.create`) → status no banco inalterado (STAT-15); `responsavel` = conta passada em `por` quando ela não é o autor, e `autor` inalterado (STAT-18); inovação apagada antes da chamada → `Inovacao.DoesNotExist`; `texto_busca` inalterado depois do avanço (AD-008)
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: ~603 testes passam (+16)

**Tests**: integration
**Gate**: full

**Commit**: `feat(inovacoes): adiciona o avanco de status com trava e historico`

**Status**: ✅ Complete — 604 passed (+16); a trava é provada pela primeira leitura capturada (`SELECT` do status terminando em `FOR UPDATE`); o teste da AD-008 muda título e `texto_busca` no banco depois de carregar a instância e confere que o avanço não os reescreve. STAT-07, 08, 10, 12, 13 e 18 ficam In Tasks até as rotas (T3, T4)

---

### T3: Confirmação do avanço (GET) em `/inovacoes/<pk>/status/` ✅

**What**: A rota `status`, a `InovacaoStatusView` com o mixin da AD-009 e o GET, e o template `inovacao_status.html` com a confirmação e a variante de estágio final.
**Where**: `inovacoes/views.py`
**Depends on**: T2
**Reuses**: `AlteracaoDeInovacaoMixin` (`inovacoes/views.py:25`); `DetailView`; `inovacao_confirm_delete.html` como modelo; `Inovacao.proximo_status` (T2)
**Requirement**: STAT-06, STAT-10 (GET), STAT-11, STAT-17 (GET), STAT-19 (GET), STAT-22 (GET)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `MENSAGEM_ULTIMO_ESTAGIO` e `InovacaoStatusView(AlteracaoDeInovacaoMixin, DetailView)` com `template_name = "inovacoes/inovacao_status.html"` e o contexto do próximo status; `path("<int:pk>/status/", ..., name="status")` em `inovacoes/urls.py`
- [x] `inovacoes/templates/inovacoes/inovacao_status.html` como no design: `<title>`/`h1` "Avançar status"; com próximo, o texto da STAT-06, `form method="post"` com `csrf_token`, `status_visto` oculto, botão "Avançar para “<próximo>”" e "Cancelar" → detalhe; sem próximo, `MENSAGEM_ULTIMO_ESTAGIO`, link "Voltar para a inovação" e nenhum `form`
- [x] Testes e2e em `inovacoes/tests/test_views_status.py`: autor `USUARIO` com "Em teste" → 200, `<title>` e `h1`, o texto exato da STAT-06, botão "Avançar para “Validada”", `status_visto` = `EM_TESTE`, "Cancelar" com `href` do detalhe (STAT-06, STAT-17); com "Validada" → texto e botão para "Disponível para replicação"; com "Disponível para replicação" → 200, `MENSAGEM_ULTIMO_ESTAGIO`, link "Voltar para a inovação", sem `<form` nem `<button` (STAT-10); o GET não muda status nem cria registro (STAT-11); `administrador` na inovação do autor → 200; `terceiro` → 403 com `acesso_negado.html` (STAT-19); id inexistente → 404 com "Inovação não encontrada." (STAT-22)
- [x] A varredura de `contas/tests/test_controle_acesso.py` (AD-006) passa sem alteração e já inclui a rota nova
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: ~613 testes passam (+10, mais os casos que a varredura da AD-009 gera sozinha para a rota nova)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(inovacoes): adiciona a confirmacao do avanco de status`

**Status**: ✅ Complete — 620 passed (+16); a contagem de telas do DS-01 subiu de 8 para 9 (`test_views_sistema_design.py`) por causa da tela nova, com autorização do usuário; a varredura da AD-006 e a da AD-009 já cobrem `/status/` sem alteração; o `<title>` é conferido pelo prefixo "Avançar status", como na F4; o estágio final é testado para o autor e o administrador

---

### T4: Avanço do status (POST) com mensagens de sucesso e de aviso ✅

**What**: O `post()` da `InovacaoStatusView`: chama `avancar_status` e traduz sucesso, status desatualizado, estágio final e inovação apagada em redirect com mensagem ou 404.
**Where**: `inovacoes/views.py`
**Depends on**: T3
**Reuses**: `Inovacao.avancar_status` e as exceções (T2); `messages.success`/`messages.warning`; `_inovacao_nao_encontrada` (`inovacoes/views.py:19`); padrão do teste da EDEX-29 (`test_views_edicao.py:543`)
**Requirement**: STAT-07, STAT-08, STAT-10 (POST), STAT-12, STAT-13, STAT-16, STAT-17, STAT-18, STAT-22 (POST)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `post()` como no design: sucesso → `messages.success` com os rótulos; `StatusDesatualizado` → `messages.warning` com o rótulo gravado; `UltimoEstagioDoCiclo` → `messages.warning(MENSAGEM_ULTIMO_ESTAGIO)`; os três → 302 para o detalhe; `Inovacao.DoesNotExist` → `_inovacao_nao_encontrada`
- [x] Testes e2e em `inovacoes/tests/test_views_status.py`: autor `USUARIO` envia `status_visto=EM_TESTE` → 302 para o detalhe, status "Validada", um registro com o autor como responsável, e no detalhe seguido a mensagem "Status da inovação “<título>” alterado de “Em teste” para “Validada”." dentro de `role="status"` (STAT-07, STAT-16, STAT-17); recarregar o detalhe → a mensagem some (STAT-16); de "Validada" → "Disponível para replicação" (STAT-08); `administrador` na inovação de outro autor → avança, autor inalterado, administrador como responsável (STAT-18); POST no estágio final → status igual, zero registros, aviso com `MENSAGEM_ULTIMO_ESTAGIO` (STAT-10); `status_visto` ausente e diferente → status igual, zero registros novos, aviso "O status desta inovação já foi alterado para “<rótulo gravado>”. Confira o status atual antes de avançar." (STAT-12); **reenvio do mesmo POST** → o segundo cai no aviso, status avançou um estágio e há um registro (STAT-13); status mudado entre o `dispatch()` e o método (monkeypatch, padrão da EDEX-29) → aviso, nada gravado (STAT-13); inovação apagada entre o `dispatch()` e o método → 404 da CONS-15, nada criado (STAT-22)
- [x] Gate check passa: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q`
- [x] Test count: ~625 testes passam (+12)

**Tests**: e2e
**Gate**: build

**Commit**: `feat(inovacoes): avanca o status com confirmacao e feedback`

**Status**: ✅ Complete — 632 passed (+12); toda recusa confere o status e a contagem de registros no banco e o nível da mensagem (`alerta--success`/`alerta--warning`) dentro de `role="status"`; a corrida e a exclusão no meio do envio usam monkeypatch no `post()`, padrão da EDEX-29; o `status_visto` fora do enum entra na parametrização da STAT-12. Build gate verde

---

### T5: Seção "Ciclo de vida" no detalhe ✅

**What**: A lista ordenada dos três estágios com o atual marcado por texto, o link "Avançar para “<próximo>”" para quem pode alterar e "Último estágio do ciclo." no final.
**Where**: `inovacoes/templates/inovacoes/inovacao_detail.html`
**Depends on**: T4
**Reuses**: `pode_alterar` do `InovacaoDetailView.get_context_data` (`inovacoes/views.py:125`); `Inovacao.proximo_status` (T2); `StatusInovacao.choices`
**Requirement**: STAT-01, STAT-02, STAT-03, STAT-04, STAT-05

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `InovacaoDetailView.get_context_data` acrescenta `etapas`; o template ganha a `section` com `h2` "Ciclo de vida", `ol.ciclo`, `aria-current="step"` e `<strong>… (status atual)</strong>` na etapa atual, e o link ou o texto do estágio final, como no design; a `p.acoes` de Editar/Excluir não muda
- [x] Testes e2e em `inovacoes/tests/test_views_detalhe.py`: `h2` "Ciclo de vida" e os três rótulos na ordem do ciclo dentro de um `ol` (STAT-01); para cada um dos três status, "(status atual)" aparece **uma** vez e junto do rótulo certo (STAT-02); autor e `administrador` veem "Avançar para “Validada”" com `href` `/inovacoes/<id>/status/` em "Em teste" e "Avançar para “Disponível para replicação”" em "Validada" (STAT-03); em "Disponível para replicação", "Último estágio do ciclo." e nenhum link para `/status/` para autor, administrador e terceiro (STAT-04); terceiro em "Em teste" não vê link para `/status/` (STAT-05)
- [x] Os testes existentes do detalhe (CONS-12, EDEX-03, EDEX-24) passam sem alteração
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: ~634 testes passam (+9)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(inovacoes): mostra o ciclo de vida do status no detalhe`

**Status**: ✅ Complete — 645 passed (+13); a seção é lida pela `section aria-labelledby="ciclo-titulo"`; a STAT-02 confere a lista inteira, com "(status atual)" uma vez na página, nos três status; o link usa `inovacao.proximo_status.label` e não acrescenta consulta (`CONSULTAS_DO_DETALHE` continua 6 até a T6); testes da CONS-12, EDEX-03 e EDEX-24 sem alteração. STAT-05 fica In Tasks até a T8 (staff/superuser)

---

### T6: Seção "Histórico de status" no detalhe ✅

**What**: A lista cronológica das mudanças com data, transição e responsável, o texto de histórico vazio e o ajuste deliberado da contagem de consultas do detalhe.
**Where**: `inovacoes/templates/inovacoes/inovacao_detail.html`
**Depends on**: T5
**Reuses**: `mudancas_de_status` (T1); critério de nome da CONS-13 (`get_full_name|default:get_username`); `CONSULTAS_DO_DETALHE` (`inovacoes/tests/test_views_detalhe.py`)
**Requirement**: STAT-24, STAT-25, STAT-26, STAT-27

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `get_context_data` acrescenta `mudancas` com `select_related("responsavel")`; o template ganha a `section` com `h2` "Histórico de status", `ol.historico` ou `<p class="vazio">Nenhuma mudança de status registrada.</p>`, item no formato da STAT-25
- [x] `CONSULTAS_DO_DETALHE` passa de 6 para 7 com comentário citando STAT-24 — **única alteração em teste existente da feature**
- [x] Testes e2e em `inovacoes/tests/test_views_detalhe.py`: duas mudanças aparecem na ordem cronológica (STAT-24); item exato "dd/mm/aaaa HH:MM — de “Em teste” para “Validada”, por <nome completo>" no fuso de São Paulo, com data fixada para o teste não depender do relógio (STAT-25); responsável sem nome sai pelo username (STAT-25); sem registros → "Nenhuma mudança de status registrada." (STAT-26); terceiro vê o histórico (STAT-27); o número de consultas é o mesmo com 0 e com 3 registros de responsáveis diferentes (sem N+1)
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: ~641 testes passam (+7)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(inovacoes): mostra o historico de status no detalhe`

**Status**: ✅ Complete — 651 passed (+6); `CONSULTAS_DO_DETALHE` 6 → 7 com comentário citando STAT-24 (a única alteração prevista em teste existente nesta task); a ordem é provada com o registro criado primeiro levando a data mais recente; datas fixadas por `update()` em UTC e conferidas no fuso de São Paulo; responsável sem nome sai pelo username (`carla`); o teste de N+1 roda com 0 e 3 registros de três responsáveis. A data do item vai num `<time>` para a T7 estilizar

---

### T7: Componentes `.ciclo` e `.historico` na `kira.css` ✅

**What**: As regras de estilo do controle do ciclo e do histórico, sem cor nova, e a página de confirmação nas checagens do sistema de design.
**Where**: `templates/kira.css`
**Depends on**: T6
**Reuses**: tokens `--border`, `--brand-blue`, `--brand-navy`, `--text-muted` (já no DS-08); fixture `paginas` e DS-14 de `inovacoes/tests/test_views_sistema_design.py`
**Requirement**: STAT-37 (estilo); base da STAT-34

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `.ciclo`, `.ciclo li + li::before`, `.ciclo [aria-current=step]` e `.historico` como no design; nenhuma cor literal nova, nenhum `="` nem `<` na folha (AD-010)
- [x] `inovacoes/tests/test_views_sistema_design.py`: a fixture `paginas` ganha `"status": f"/inovacoes/{inovacao.pk}/status/"` (herda as checagens de base, `style` único e cabeçalho); o DS-14 ganha o botão "Avançar para “Validada”" como envio primário; teste novo: as regras `.ciclo` e `.historico` existem e todas as cores que usam são `var(--…)` de tokens presentes em `PARES_DE_TEXTO` (STAT-37)
- [x] Gate check passa: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q`
- [x] Test count: ~650 testes passam (+9, a maioria herdada da parametrização de `paginas`)

**Tests**: e2e
**Gate**: build

**Commit**: `feat(design): estiliza o ciclo de vida e o historico de status`

**Status**: ✅ Complete — 654 passed (+3); a fixture `paginas` ganhou `status` e o DS-14 ganhou "Avançar para “Validada”" (acréscimos previstos); o teste novo exige as regras `.ciclo` e `.historico`, nenhuma cor literal e que todo `color`/`background` delas seja token de `PARES_DE_TEXTO` (bordas como `--border` não são par de texto e só precisam existir no `:root`); a data do histórico sai em `--text-muted` pelo `<time>`. O comentário da folha não repete "(status atual)", porque o CSS vai embutido na página. STAT-34 e STAT-37 ficam In Tasks até a T10. Build gate verde

---

### T8: Autorização da rota de status (AD-009, L-003)

**What**: A evidência de que só autor e administrador avançam, pela varredura e por testes dirigidos à rota nova, incluindo staff/superuser, rebaixamento e anônimo.
**Where**: `inovacoes/tests/test_views_status.py`
**Depends on**: T7
**Reuses**: fixture `nao_autor_usuario` (terceiro, staff, superusuário) de `inovacoes/tests/conftest.py:60`; varredura de `inovacoes/tests/test_controle_autoria.py`
**Requirement**: STAT-05 (staff/superuser), STAT-19, STAT-20, STAT-21, STAT-23

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [ ] `test_varredura_encontra_as_rotas_de_alteracao` passa a exigir `inovacoes:status` em `ROTAS_DE_ALTERACAO` (acréscimo à sanidade, nada removido)
- [ ] Testes e2e: `nao_autor_usuario` (três variantes) com GET e com POST de `status_visto` **correto** → 403, `acesso_negado.html`, status igual e zero registros (STAT-19, STAT-20); as mesmas três contas não veem link para `/status/` no detalhe (STAT-05, L-003); `administrador` rebaixado a `USUARIO` → 403 no POST seguinte, nada gravado (STAT-21); anônimo com GET e POST → login com `next=/inovacoes/<id>/status/`, status igual (STAT-23)
- [ ] Gate check passa: `.venv/bin/pytest -q`
- [ ] Test count: ~661 testes passam (+11)

**Tests**: e2e
**Gate**: full

**Commit**: `test(inovacoes): prova a autorizacao da troca de status`

---

### T9: Integridade do ciclo fora da rota de status

**What**: A evidência de que cadastro, edição e admin não mexem no ciclo nem no histórico.
**Where**: `inovacoes/tests/test_ciclo_de_vida.py`
**Depends on**: T8
**Reuses**: `InovacaoForm` e as rotas `nova`/`editar` (F2, F4); `test_admin_listas.py` como padrão de checagem do admin
**Requirement**: STAT-30, STAT-32, STAT-33

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [ ] Testes e2e: cadastro pela rota `nova` → status "Em teste" e zero registros (STAT-32); POST de edição com `status=DISPONIVEL_PARA_REPLICACAO` → status igual e zero registros (STAT-33); `MudancaDeStatus` não está em `admin.site._registry` e `/admin/inovacoes/mudancadestatus/` responde 404 para o `admin` (STAT-30); nenhuma rota do namespace `inovacoes` tem nome ou view que edite ou apague `MudancaDeStatus` (lista das rotas = `lista`, `nova`, `detalhe`, `editar`, `excluir`, `status`) (STAT-30)
- [ ] Gate check passa: `.venv/bin/pytest -q`
- [ ] Test count: ~665 testes passam (+4)

**Tests**: e2e
**Gate**: full

**Commit**: `test(inovacoes): prova que cadastro, edicao e admin nao mexem no ciclo`

---

### T10: Acessibilidade do ciclo, do histórico e da confirmação

**What**: A evidência da STAT-34 e da parte textual da STAT-37 nas três telas novas.
**Where**: `inovacoes/tests/test_views_acessibilidade_alteracao.py`
**Depends on**: T9
**Reuses**: helpers de foco e `tabindex` dos testes da EDEX-42 no mesmo arquivo
**Requirement**: STAT-34, STAT-37 (texto)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [ ] Testes e2e: página "Avançar status" com um único `h1` e `<title>` "Avançar status"; ciclo, histórico e confirmação só com `ol`/`ul`, `a`, `form` e `button` nativos, sem `tabindex` positivo; o CSS real da página tem indicador de foco para os links e o botão (mesma checagem da EDEX-42); as seções "Ciclo de vida" e "Histórico de status" são `section` rotuladas pelo seu `h2` (`aria-labelledby`); sem o CSS, o estágio atual continua identificável pelo texto "(status atual)" (STAT-37)
- [ ] Gate check passa: `.venv/bin/pytest -q`
- [ ] Test count: ~671 testes passam (+6)

**Tests**: e2e
**Gate**: full

**Commit**: `test(inovacoes): prova a acessibilidade do ciclo de vida do status`

---

### T11: Banco indisponível e CSRF na troca de status

**What**: A evidência da STAT-35 e da STAT-36.
**Where**: `inovacoes/tests/test_views_erro_500.py`
**Depends on**: T10
**Reuses**: `test_banco_indisponivel_na_alteracao_devolve_500_sem_mudar_nada` (`test_views_erro_500.py:104`); `enforce_csrf_checks` de `contas/tests/test_views_login.py:66`
**Requirement**: STAT-35, STAT-36

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [ ] Testes e2e: `OperationalError` na gravação do status e, em outro caso, na criação do registro → 500 com `500.html`, sem detalhes da conexão, status igual e zero registros (STAT-35); POST com `Client(enforce_csrf_checks=True)` sem token → 403, status igual e zero registros (STAT-36)
- [ ] Gate check passa: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q`
- [ ] Test count: ~674 testes passam (+3)

**Tests**: e2e
**Gate**: build

**Commit**: `test(inovacoes): prova falha de banco e CSRF na troca de status`

---

## Phase Execution Map

```
Phase 1 → Phase 2 → Phase 3 → Phase 4

Phase 1:  T1 → T2
Phase 2:  T3 → T4
Phase 3:  T5 → T6 → T7
Phase 4:  T8 → T9 → T10 → T11
```

Arcos de fronteira entre fases (a primeira task de cada fase depende da última da anterior):

```
T2 → T3
T4 → T5
T7 → T8
```

A execução é estritamente sequencial — não há paralelismo dentro de uma fase.

**Empacotamento previsto no Execute:** 11 tasks ⇒ com orçamento de ~7 por lote e corte apenas em
fronteira de fase: **lote 1** = Fases 1+2+3 (7 tasks: modelo, tela e detalhe), **lote 2** = Fase 4
(4 tasks: evidências). Mais de um lote ⇒ o Execute deve **oferecer** sub-agentes antes de começar.

---

## Task Granularity Check

| Task | Scope | Status |
| ---- | ----- | ------ |
| T1 | 1 modelo + 1 constante (+ migration gerada) | ✅ Granular |
| T2 | 1 propriedade + 1 método + 3 exceções, mesmo arquivo | ⚠️ 2-3 coisas coesas, mesmo arquivo |
| T3 | 1 tela = view + rota + template | ⚠️ 3 arquivos, coeso — ver nota |
| T4 | 1 método da view | ✅ Granular |
| T5 | 1 trecho de template + 1 chave de contexto | ✅ Granular |
| T6 | 1 trecho de template + 1 chave de contexto (+ 1 constante de teste) | ✅ Granular |
| T7 | 1 folha de estilo (+ checagens do sistema de design) | ✅ Granular |
| T8, T9, T10, T11 | 1 arquivo de teste cada (o código já existe) | ✅ Granular |

**Nota sobre T1 e T3:** a migration é gerada pelo `makemigrations`, não escrita à mão, e o gate de
build (`--check`) falharia sem ela. Uma view Django não é testável sem rota e template. O `Where`
nomeia o arquivo principal; os demais estão no `Done when` e cobertos pelos mesmos testes — o mesmo
merge backward da T4 e da T9 da F4.

**Nota sobre T8 a T11:** o comportamento vem do mixin da AD-009, do Django ou das tasks anteriores.
A task é a evidência das ACs; se a evidência acusar falta, o ajuste entra na mesma task.

---

## Diagram-Definition Cross-Check

| Task | Depends On (task body) | Diagram Shows | Status |
| ---- | ---------------------- | ------------- | ------ |
| T1 | None | (início da Fase 1) | ✅ Match |
| T2 | T1 | T1 → T2 | ✅ Match |
| T3 | T2 | T2 → T3 (arco de fronteira) | ✅ Match |
| T4 | T3 | T3 → T4 | ✅ Match |
| T5 | T4 | T4 → T5 (arco de fronteira) | ✅ Match |
| T6 | T5 | T5 → T6 | ✅ Match |
| T7 | T6 | T6 → T7 | ✅ Match |
| T8 | T7 | T7 → T8 (arco de fronteira) | ✅ Match |
| T9 | T8 | T8 → T9 | ✅ Match |
| T10 | T9 | T9 → T10 | ✅ Match |
| T11 | T10 | T10 → T11 | ✅ Match |

Nenhuma dependência aponta para uma fase posterior.

---

## Test Co-location Validation

| Task | Code Layer Created/Modified | Matrix Requires | Task Says | Status |
| ---- | --------------------------- | --------------- | --------- | ------ |
| T1: histórico e migration | Modelo e constraints + Migration | integration | integration | ✅ OK |
| T2: avanço no modelo | Regra do modelo | integration | integration | ✅ OK |
| T3: confirmação (GET) | Views, rotas, templates | e2e | e2e | ✅ OK |
| T4: avanço (POST) | Views | e2e | e2e | ✅ OK |
| T5: ciclo no detalhe | Template + view do detalhe | e2e | e2e | ✅ OK |
| T6: histórico no detalhe | Template + view do detalhe | e2e | e2e | ✅ OK |
| T7: CSS | Folha de estilo | e2e | e2e | ✅ OK |
| T8: autorização | Views (evidência) | e2e | e2e | ✅ OK |
| T9: integridade | Views (evidência) | e2e | e2e | ✅ OK |
| T10: acessibilidade | Templates (evidência) | e2e | e2e | ✅ OK |
| T11: banco e CSRF | Views (evidência) | e2e | e2e | ✅ OK |

Nenhuma task tem `Tests: none`.

---

## Requirement Coverage

| Requisito | Tasks |
| --------- | ----- |
| STAT-01, 02, 03, 04 | T5 |
| STAT-05 | T5, T8 |
| STAT-06, 11 | T3 |
| STAT-07, 08 | T2, T4 |
| STAT-09 | T1, T2 |
| STAT-10 | T2, T3 (GET), T4 (POST) |
| STAT-12, 13 | T2, T4 |
| STAT-14, 15 | T2 |
| STAT-16 | T4 |
| STAT-17 | T3, T4 |
| STAT-18 | T2, T4 |
| STAT-19 | T3, T8 |
| STAT-20, 21, 23 | T8 |
| STAT-22 | T3 (GET), T4 (POST) |
| STAT-24 … 27 | T6 |
| STAT-28, 29, 31 | T1 |
| STAT-30, 32, 33 | T9 |
| STAT-34 | T7, T10 |
| STAT-35, 36 | T11 |
| STAT-37 | T7, T10 |

**Coverage:** 37 de 37 requisitos mapeados para tasks.
