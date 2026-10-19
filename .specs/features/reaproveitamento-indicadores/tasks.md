# Reaproveitamento e Indicadores (F6) — Tasks

## Execution Protocol (MANDATORY -- do not skip)

Implement these tasks with the `tlc-spec-driven` skill: **activate it by name and follow its Execute flow and Critical Rules.** Do not search for skill files by filesystem path. The skill is the source of truth for the full flow (per-task cycle, sub-agent delegation, adequacy review, Verifier, discrimination sensor).

**If the skill cannot be activated, STOP and tell the user - do not proceed without it.**

---

**Spec**: `.specs/features/reaproveitamento-indicadores/spec.md`
**Design**: `.specs/features/reaproveitamento-indicadores/design.md`
**Status**: T1–T19 ✅ (865 testes). Tasks aprovadas pelo usuário em 2026-10-18; execução por sub-agentes em 4 lotes, todos concluídos (lotes 3 e 4 retomados em 2026-10-19). Verifier FAIL na iteração 1 só por lacuna de teste (M41, M43, M44, M45); a T19 (Fix 1) reforça as asserções de exibido; re-verificação pendente (iteração 2)

**Stack fixado**: Django 5.2.17 · PostgreSQL 16 (AD-003) · pytest + pytest-django · Ruff — o mesmo da F1 a F5.

**Ordem pedida pelo usuário:** o RF11 (sinalização, RN09, detalhe, admin) vem primeiro, nas Fases 1
a 4 (T1–T10). O painel do RF10 vem por último, nas Fases 5 a 7 (T11–T18).

> **Linha de corte:** depois da T10, o RF11 está completo e verificável sozinho: modelo, regra,
> tela, detalhe, admin, autorização e acessibilidade. Se faltar tempo, as Fases 5–7 podem ser cortadas
> inteiras. Nenhuma task das Fases 1–4 depende delas, e o menu só ganha "Indicadores" na T15. Cortar
> o painel deixa REAP-28 a REAP-42 e REAP-46 a REAP-48 em `Pending` e exige rodar o Verifier sobre
> o RF11 com essas ACs declaradas fora do lote.

**Caso central — "a métrica só conta reuso real" (RN09):** coberto em camadas, cada uma numa task
diferente, para que nenhuma sozinha seja a única prova:

| Camada | Task | O que prova |
| ------ | ---- | ----------- |
| Banco | T1 | A UniqueConstraint recusa o segundo par (inovação, unidade) |
| Regra no modelo | T2 | `registrar_reaproveitamento` recusa status ≠ Disponível, unidade de origem e repetição; trava a linha; não muda a inovação |
| Formulário | T3 | O select mostra só as elegíveis, mas origem e repetida forjadas chegam ao método |
| Rota | T4, T5 | GET e POST de inovação fora de "Disponível" redirecionam com aviso; POST forjado gera o erro de campo específico; corrida termina na REAP-12, não em 500 |
| Admin | T8 | Ninguém inclui nem edita pelo admin |

**Lições aplicadas:** L-003 (T8: `USUARIO` com `is_staff`/`is_superuser` recebe 403 nas páginas do
admin de `Reaproveitamento`, não só fica sem o link) · L-005 (REAP-09/REAP-10 provadas no modelo, na T2,
**e** pela rota, nas T4 e T5; toda AC com efeito em tela é afirmada pelo `client`).

---

## Test Coverage Matrix

> Gerada a partir do código, das diretrizes do projeto e da spec — confirmar antes do Execute.
> **Guidelines encontradas: nenhuma.** Não existe `AGENTS.md`, `CONTRIBUTING.md` nem workflow de CI;
> o `pyproject.toml` só configura o pytest (`DJANGO_SETTINGS_MODULE`, marcador `unit`,
> `--strict-markers`) e o Ruff, sem limite de cobertura e sem `testpaths` (o pytest acha
> `indicadores/tests/` sozinho). Valem os **strong defaults**: toda AC e todo edge case da spec têm
> teste; rotas cobrem happy + edge + erro. Estilo, local e fixtures seguem as amostras de
> `inovacoes/tests/` (`conftest.py`, `test_ciclo_de_vida.py`, `test_views_status.py`,
> `test_views_detalhe.py`, `test_controle_autoria.py`, `test_admin_listas.py`,
> `test_views_sistema_design.py`, `test_views_erro_500.py`, `test_desempenho.py`), que são o piso de
> profundidade.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| ---------- | ------------------ | -------------------- | ---------------- | ----------- |
| Modelo e constraints (`Reaproveitamento`) | integration | Unique contra o PostgreSQL; `CASCADE`, os dois `PROTECT`; ordenação por `data`, `id` (REAP-14, REAP-23 a REAP-25) | `inovacoes/tests/test_reaproveitamento.py` | `.venv/bin/pytest -q` |
| Regra do modelo (`pode_ser_reaproveitada`, `registrar_reaproveitamento`) | integration | Todo ramo 1:1 com as ACs: sucesso, três códigos de recusa, `FOR UPDATE` emitido, inovação apagada, outra `IntegrityError` relançada, inovação inalterada (REAP-05, REAP-07, REAP-10 a REAP-12, REAP-14, REAP-22) | `inovacoes/tests/test_reaproveitamento.py` | `.venv/bin/pytest -q` |
| Agregações (`CategoriaQuerySet`, `UnidadeQuerySet`) | integration | Zeros, ordem com desempate por nome, sem fan-out, sem quebra pelo `Meta.ordering`, número de consultas (REAP-32, REAP-33) | `inovacoes/tests/test_agregacoes.py` | `.venv/bin/pytest -q` |
| Formulário (`ReaproveitamentoForm`) | integration | Opções exibidas, ordem, valores aceitos e as três mensagens de entrada (REAP-04, REAP-13) | `inovacoes/tests/test_forms_reaproveitamento.py` | `.venv/bin/pytest -q` |
| Geometria do gráfico (`indicadores/graficos.py`) | unit | Função pura: proporção, maior = área toda, zero sem barra, tudo zero, posição do valor, altura (REAP-35, REAP-36) | `indicadores/tests/test_graficos.py` | `.venv/bin/pytest -q -m unit` |
| Views, rotas e templates (`inovacoes/views.py`, `indicadores/views.py`, `urls.py`, templates) | e2e | Toda rota que a task adiciona ou altera: happy + todo edge case + erro, pelo `client`, para autor, terceiro `USUARIO` (inclusive staff/superuser), administrador e anônimo; afirmar o banco depois de toda recusa | `inovacoes/tests/test_views_reaproveitar.py`, `test_views_detalhe.py`, `test_controle_autoria.py`, `test_views_acessibilidade_alteracao.py`, `test_views_erro_500.py`, `indicadores/tests/test_views_painel.py`, `inovacoes/tests/test_views_cabecalho.py` | `.venv/bin/pytest -q` |
| Django admin (`ReaproveitamentoAdmin`) | e2e | Listagem e exclusão pelo `ADMINISTRADOR`; 403 para `USUARIO` staff/superuser em toda tela; inclusão e alteração recusadas mesmo forjadas (REAP-24, REAP-26, REAP-27) | `inovacoes/tests/test_admin_reaproveitamento.py` | `.venv/bin/pytest -q` |
| Folha de estilo (`templates/kira.css`) | e2e | Componentes novos presentes, só tokens de pares do DS-08 (`color`, fundo e `fill`), regras da AD-010 (sem `="`, sem `<`) | `inovacoes/tests/test_views_sistema_design.py` | `.venv/bin/pytest -q` |
| Desempenho (RNF08) | e2e | 2 s de servidor com demonstração + 200 reaproveitamentos; número de consultas igual com volumes diferentes (REAP-41 a REAP-43) | `indicadores/tests/test_desempenho_painel.py`, `inovacoes/tests/test_views_detalhe.py` | `.venv/bin/pytest -q` |
| Migration `0008`, `INSTALLED_APPS`, `apps.py` | none | — gerados ou declarativos; `makemigrations --check` e o import da app no gate de build | — | build gate only |

## Gate Check Commands

> Gerados a partir do projeto — confirmar antes do Execute. Todos pelo `.venv/`, com o PostgreSQL 16
> na porta 5433 em execução.

| Gate Level | When to Use | Command |
| ---------- | ----------- | ------- |
| Quick | Task só com teste unitário (T12) | `.venv/bin/pytest -q -m unit` |
| Full | Depois de toda task com teste de integração ou e2e | `.venv/bin/pytest -q` |
| Build | Ao fechar uma fase, e nas tasks que criam migration, app ou mexem em template/CSS compartilhado | `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` |

**Linha de base:** 710 testes coletados antes da T1 (`.venv/bin/pytest -q --co`, 2026-10-18). Rodar
`.venv/bin/pytest -q` no início do Execute para confirmar que todos passam.

**Testes de features anteriores que mudam (autorizados na aprovação da spec):**

| Teste | Mudança | Task |
| ----- | ------- | ---- |
| `inovacoes/tests/test_controle_autoria.py` | Conjunto novo `ROTAS_SEM_AUTORIA = {"inovacoes:reaproveitar"}`, excluído de `ROTAS_DE_ALTERACAO`; a sanidade passa a exigir que a rota seja achada | T4 |
| `inovacoes/tests/test_views_sistema_design.py` | DS-01 9 → 10 telas; fixture `paginas` ganha "reaproveitar" | T4 |
| `inovacoes/tests/test_ciclo_de_vida.py` | `test_nenhuma_rota_de_inovacoes_altera_o_historico` (STAT-30): o conjunto de rotas ganha `"reaproveitar"` e a docstring passa de "seis" para "sete"; a checagem de que nenhuma view serve `MudancaDeStatus` fica igual (autorizado pelo usuário em 2026-10-18, durante o Execute) | T4 |
| `inovacoes/tests/test_views_detalhe.py` | `CONSULTAS_DO_DETALHE` 7 → 8 | T6 |
| `inovacoes/tests/test_views_sistema_design.py` | Teste de cores do componente ganha `.reaproveitamentos` | T7 |
| `inovacoes/tests/test_views_sistema_design.py` | `RAIZES` ganha `indicadores/templates`; DS-01 10 → 11; fixture `paginas` ganha "painel" | T13 |
| `inovacoes/tests/test_views_sistema_design.py` | `PECAS` ganha `indicadores/grafico.html` | T14 |
| `inovacoes/tests/test_views_sistema_design.py` | Leitura de `fill` nos seletores `.grafico__*`; teste de cores ganha `.metrica` e `.grafico` | T16 |

Nenhum outro teste da F1 a F5 pode mudar; se precisar, é erro na task. Nenhum teste existente perde
asserção. As contagens abaixo são estimativas; a regra dura é que a contagem nunca cai.

---

## Execution Plan

As fases são ordenadas e rodam em sequência — cada fase termina antes de a próxima começar, e as
tasks dentro de uma fase executam em ordem.

### Phase 1: Fundação do reaproveitamento (RF11)

O modelo com a unicidade e o método da AD-012. Nenhuma tela.

```
T1 → T2
```

### Phase 2: Tela de sinalização (RF11)

O formulário e a rota `/inovacoes/<pk>/reaproveitar/`: GET e POST.

```
T3 → T4 → T5
```

### Phase 3: Detalhe, estilo e admin (RF11)

A seção "Reaproveitamentos" e o link no detalhe, o componente na `kira.css` e a correção pelo admin.

```
T6 → T7 → T8
```

### Phase 4: Evidências transversais da sinalização (RF11)

Autorização, integridade, banco indisponível, CSRF e acessibilidade. O comportamento vem das tasks
anteriores, do middleware ou do Django; se a evidência acusar falta, o ajuste entra na mesma task.

```
T9 → T10
```

**— Linha de corte: RF11 completo. —**

### Phase 5: Painel — dados e página (RF10)

Agregações, a app `indicadores` com a geometria das barras, e a página com cards e tabelas.

```
T11 → T12 → T13
```

### Phase 6: Painel — gráficos, menu e estilo (RF10)

Os três gráficos SVG, o link "Indicadores" no menu e os componentes na `kira.css`.

```
T14 → T15 → T16
```

### Phase 7: Painel — evidências (RF10, RNF08)

Desempenho e acessibilidade do painel, e banco indisponível no painel.

```
T17 → T18
```

### Phase 8: Correção da validação, iteração 1

Fix task do `validation.md` (iteração 1, FAIL): quatro mutantes sobreviveram por lacuna de teste
(M41, M43, M44, M45), todos com o elemento exigido ainda no HTML, mas escondido. Nenhum defeito de
produção. Só arquivos de teste mudam, e só ficam mais fortes.

```
T19
```

---

## Task Breakdown

### T1: `Reaproveitamento` e a migration 0008 ✅

**What**: O modelo `Reaproveitamento` com as três FKs, a ordenação e a UniqueConstraint `reaproveitamento_unico_por_unidade`, e a migration gerada.
**Where**: `inovacoes/models.py`
**Depends on**: None
**Reuses**: `MudancaDeStatus` como modelo de FK + `ordering` (`inovacoes/models.py`); `on_delete=PROTECT` de `Inovacao.unidade`/`Inovacao.autor`; fixtures `autor`, `unidade`, `criar_inovacao` de `inovacoes/tests/conftest.py`
**Requirement**: REAP-14 (banco), REAP-23, REAP-24 (ORM), REAP-25

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `Reaproveitamento` exatamente como no design (Data Models): `inovacao` (CASCADE, `related_name="reaproveitamentos"`), `unidade` (PROTECT, `related_name="reaproveitamentos"`), `registrado_por` (`settings.AUTH_USER_MODEL`, PROTECT, `related_name="reaproveitamentos_registrados"`), `data` (`auto_now_add`), `ordering = ["data", "id"]`, `UniqueConstraint(fields=["inovacao", "unidade"], name="reaproveitamento_unico_por_unidade")`, `__str__`, docstring citando AD-012
- [x] `inovacoes/migrations/0008_reaproveitamento.py` gerada por `makemigrations`; só cria a tabela
- [x] Testes de integração em `inovacoes/tests/test_reaproveitamento.py` (registros criados pelo ORM, só nesta task, para provar o banco): o segundo par (inovação, unidade) igual levanta `IntegrityError` com `constraint_name == "reaproveitamento_unico_por_unidade"`; a mesma unidade em **outra** inovação e outra unidade na **mesma** inovação gravam (REAP-14); excluir a inovação apaga os reaproveitamentos dela e não os de outra (REAP-23); excluir a unidade referenciada levanta `ProtectedError` e unidade e registro continuam (REAP-24); excluir a conta `registrado_por` levanta `ProtectedError` e conta e registro continuam (REAP-25); dois registros com a mesma `data` saem na ordem do `id`
- [x] Gate check passa: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q`
- [x] Test count: ~717 testes passam (+7)

**Tests**: integration
**Gate**: build

**Commit**: `feat(inovacoes): adiciona o modelo de reaproveitamento`

**Status**: ✅ Complete — 717 passed (+7); unicidade, CASCADE, os dois PROTECT e a ordenação provados com registros criados pelo ORM, só nesta task; a migration 0008 foi formatada pelo Ruff como a 0007; os blocos Python do `design.md` foram formatados pelo Ruff, porque o `ruff format --check` do gate falhava neles. Build gate verde

---

### T2: `Inovacao.pode_ser_reaproveitada` e `Inovacao.registrar_reaproveitamento` ✅

**What**: O método de consulta da RN09 e o método único de criação da AD-012, com as três mensagens como constantes de módulo.
**Where**: `inovacoes/models.py`
**Depends on**: T1
**Reuses**: esqueleto de `Inovacao.avancar_status` (trava + `values_list("status").get`); tradução de `IntegrityError` por `diag.constraint_name` de `GravacaoComTituloUnicoMixin.form_valid` (`inovacoes/views.py`)
**Requirement**: REAP-05 (modelo), REAP-07, REAP-10, REAP-11 (modelo), REAP-12 (modelo), REAP-14, REAP-22 (modelo)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `pode_ser_reaproveitada()` devolve `True` só para `DISPONIVEL_PARA_REPLICACAO`
- [x] `registrar_reaproveitamento(self, *, unidade, por)` como no design (algoritmo), com comentário citando AD-012; constantes `MENSAGEM_REAPROVEITAMENTO_STATUS`, `MENSAGEM_REAPROVEITAMENTO_ORIGEM`, `MENSAGEM_REAPROVEITAMENTO_REPETIDO` com o texto exato da spec (REAP-09, REAP-11, REAP-12)
- [x] Testes de integração em `inovacoes/tests/test_reaproveitamento.py`:
  - `pode_ser_reaproveitada` nos três status.
  - Sucesso: um registro com inovação, unidade, `registrado_por` = `por` (inclusive quando `por` não é o autor) e `data` preenchida; o retorno é esse registro (REAP-05, REAP-22).
  - "Em teste" e "Validada" → `ValidationError` com `code == "status_indisponivel"` e a mensagem com o rótulo do status gravado; zero registros (REAP-10).
  - Status mudado no banco depois de carregar a instância: recusa ou aceita pelo valor **gravado**, não pelo da instância.
  - Unidade de origem → `code == "unidade_de_origem"`, zero registros (REAP-11).
  - Segunda chamada com a mesma unidade → `code == "unidade_ja_reaproveitou"` e mensagem com o nome da unidade; um registro só; a transação externa continua usável depois do erro (savepoint) (REAP-12, REAP-14).
  - `IntegrityError` de outra constraint (forçada com `mock`) é relançada, não traduzida.
  - `CaptureQueriesContext` mostra `FOR UPDATE` na leitura do status.
  - Inovação apagada antes da chamada → `Inovacao.DoesNotExist`.
  - Todos os campos da inovação (`values()` antes × depois, inclusive `status`, `autor_id`, `data_criacao`, `texto_busca`) iguais depois do sucesso (REAP-07).
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: ~732 testes passam (+15)

**Tests**: integration
**Gate**: full

**Commit**: `feat(inovacoes): adiciona o registro de reaproveitamento com trava`

**Status**: ✅ Complete — 732 passed (+15); a trava é provada pela primeira leitura capturada (`SELECT` do status terminando em `FOR UPDATE`); o status gravado decide nos dois sentidos (instância velha em "Disponível" recusa, instância velha em "Em teste" aceita); a outra `IntegrityError` é forjada com `__cause__.diag.constraint_name`, como o psycopg entrega. Limite: o teste do savepoint roda dentro da transação do pytest-django, onde o `atomic` externo do método já é um savepoint, então ele prova que a transação de quem chama segue usável, mas não discrimina a ausência do savepoint interno. REAP-11, 12, 14 e 22 seguem para as rotas (T5)

---

### T3: `ReaproveitamentoForm` com `UnidadeElegivelField` ✅

**What**: O formulário de uma escolha que exibe só as unidades elegíveis e aceita qualquer unidade existente, com a mensagem única de entrada.
**Where**: `inovacoes/forms.py`
**Depends on**: T2
**Reuses**: `forms.ModelChoiceField`; padrão de `error_messages` do `InovacaoForm`; consulta Q6 do design
**Requirement**: REAP-04, REAP-13

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `UnidadeElegivelField(ModelChoiceField)` com `to_python` buscando em `Unidade.objects.all()` e docstring do porquê (REAP-11/REAP-12 chegam ao método)
- [x] `ReaproveitamentoForm(data=None, *, inovacao)` com `queryset` = Q6, `label="Unidade que reaproveitou"`, `empty_label="Selecione a unidade"`, `required` e `invalid_choice` = "Selecione a unidade que reaproveitou a inovação."
- [x] Testes de integração em `inovacoes/tests/test_forms_reaproveitamento.py`:
  - Opções exibidas = todas as unidades menos a origem e menos as já registradas, em ordem alfabética; a primeira opção é a vazia "Selecione a unidade" e nenhuma vem selecionada (REAP-04).
  - Unidade elegível → válido, com `cleaned_data["unidade"]` = a instância.
  - Origem e unidade já registrada → **válido** no form (a recusa é do método).
  - Vazio, id inexistente e `"abc"` → inválido com exatamente a mensagem da REAP-13.
  - Unidade sinalizada para **outra** inovação continua elegível.
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: ~741 testes passam (+9)

**Tests**: integration
**Gate**: full

**Commit**: `feat(inovacoes): adiciona o formulario de sinalizacao de reaproveitamento`

**Status**: ✅ Complete — 741 passed (+9); as opções são conferidas no select renderizado contra uma lista literal (unidades da migration 0004 mais "Almoxarifado", criada por último para separar a ordem do nome da ordem do id); "nenhuma vem selecionada" é lido como nenhuma unidade com `selected`: o Django marca a opção vazia "Selecione a unidade" como `selected` no form não vinculado; os registros de teste nascem pelo `registrar_reaproveitamento` (AD-012)

---

### T4: Formulário de sinalização (GET) em `/inovacoes/<pk>/reaproveitar/` ✅

**What**: A rota `reaproveitar`, a `InovacaoReaproveitarView` com `dispatch` e GET, e o template `inovacao_reaproveitar.html` com o formulário e a variante sem unidade elegível.
**Where**: `inovacoes/views.py`
**Depends on**: T3
**Reuses**: `_inovacao_nao_encontrada`; `FormView`; parcial `inovacoes/campo.html`; `inovacao_status.html` como modelo de página com "Cancelar"; `MENSAGEM_REAPROVEITAMENTO_STATUS` (T2)
**Requirement**: REAP-03, REAP-04 (tela), REAP-08, REAP-09 (GET), REAP-15, REAP-16, REAP-19 (GET)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `path("<int:pk>/reaproveitar/", …, name="reaproveitar")` em `inovacoes/urls.py`
- [x] `InovacaoReaproveitarView(FormView)` **sem** `AlteracaoDeInovacaoMixin`, com `dispatch`, `get_form_kwargs` e `get_context_data` como no design; comentário citando REAP-19 e AD-012
- [x] `inovacoes/templates/inovacoes/inovacao_reaproveitar.html` estende o base; `title` "Sinalizar reaproveitamento"; texto, select, botão "Sinalizar reaproveitamento", "Cancelar" e o ramo `sem_elegiveis` com o texto da REAP-15 e "Voltar para a inovação"
- [x] `test_controle_autoria.py`: `ROTAS_SEM_AUTORIA = {"inovacoes:reaproveitar"}` fora de `ROTAS_DE_ALTERACAO`, com comentário citando REAP-19; a sanidade exige `inovacoes:reaproveitar` em `ROTAS_COM_PK`
- [x] `test_views_sistema_design.py`: DS-01 passa de 9 para 10 telas (comentário citando REAP-03); a fixture `paginas` ganha "reaproveitar" (inovação criada em "Disponível para replicação")
- [x] Testes e2e em `inovacoes/tests/test_views_reaproveitar.py`:
  - GET de inovação "Disponível" → 200, `<title>` começando por "Sinalizar reaproveitamento", texto da REAP-03 com título e unidade de origem, `<select>` com `<label>` "Unidade que reaproveitou", botão e link "Cancelar" com `href="/inovacoes/<pk>/"` (REAP-03).
  - As `<option>` renderizadas são exatamente as elegíveis, em ordem, sem a origem e sem as já registradas (REAP-04).
  - GET nunca cria registro (REAP-08).
  - GET de "Em teste" e "Validada" → 302 para o detalhe; o detalhe seguido mostra o aviso exato da REAP-09 uma vez; zero registros.
  - Todas as outras unidades já registradas, e cenário com só a unidade de origem cadastrada → 200, texto da REAP-15, link "Voltar para a inovação", sem `<select>` nem botão (REAP-15).
  - Id inexistente → 404 com "Inovação não encontrada." (REAP-16).
  - Terceiro `USUARIO` (fixture `nao_autor_usuario`: comum, staff, superuser) e administrador → 200 no GET, nunca 403 (REAP-19).
- [x] Gate check passa: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q`
- [x] Test count: ~756 testes passam (+15)

**Tests**: e2e
**Gate**: build

**Commit**: `feat(inovacoes): adiciona a tela de sinalizacao de reaproveitamento`

**Status**: ✅ Complete — 753 passed (+12); testes antigos alterados como autorizado: `ROTAS_SEM_AUTORIA` em `test_controle_autoria.py`, DS-01 9 → 10 e `paginas` com "reaproveitar" em `test_views_sistema_design.py`, e o conjunto de rotas da STAT-30 em `test_ciclo_de_vida.py` (autorizado pelo usuário durante o Execute); SPEC_DEVIATION em `get_form_kwargs`: monta só `data` e `inovacao`, porque o `FormView` manda `initial` e `prefix`, que a assinatura do form da T3 não aceita; o REAP-19 do GET cobre `USUARIO` comum, staff, superuser e administrador. Build gate verde

---

### T5: Registro do reaproveitamento (POST) com mensagens ✅

**What**: O `form_valid` que chama `registrar_reaproveitamento` e traduz cada resultado em mensagem, erro de campo ou 404.
**Where**: `inovacoes/views.py`
**Depends on**: T4
**Reuses**: `registrar_reaproveitamento` (T2); `messages.success`/`messages.warning` como em `InovacaoStatusView.post`
**Requirement**: REAP-05, REAP-06, REAP-09 (POST), REAP-11, REAP-12, REAP-13, REAP-14 (rota), REAP-16 (POST), REAP-19 (POST), REAP-22

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `form_valid` como no design: sucesso → `messages.success` com o texto exato da REAP-06 e 302 ao detalhe; `unidade_de_origem`/`unidade_ja_reaproveitou` → `add_error("unidade", …)` e 200; `status_indisponivel` → aviso e 302; `Inovacao.DoesNotExist` → 404 da CONS-15
- [x] Testes e2e em `inovacoes/tests/test_views_reaproveitar.py`:
  - POST com unidade elegível → 302 para `/inovacoes/<pk>/`; um registro com a unidade, `registrado_por` = conta logada e `data` preenchida (REAP-05).
  - O detalhe seguido mostra a mensagem exata da REAP-06 **uma vez**, e a página depois dele não a repete.
  - POST de "Em teste"/"Validada" → 302 com o aviso da REAP-09 e zero registros.
  - POST com a origem → 200, erro exato da REAP-11 junto do select, zero registros.
  - POST com unidade já registrada → 200, erro exato da REAP-12 com o nome da unidade, um registro só.
  - POST vazio, com id inexistente e com `"abc"` → 200 e erro da REAP-13, zero registros.
  - Corrida: unidade registrada por outra conexão entre o `is_valid` e a chamada do método (via `mock` do `queryset` elegível ou inserção no `form_valid` anterior) → 200 com o erro da REAP-12, um registro só, nunca 500 (REAP-14).
  - Inovação apagada entre o `dispatch` e o método (`mock`) → 404, zero registros (REAP-16).
  - POST com `registrado_por`, `data` e `inovacao` forjados no corpo → ignorados (REAP-22).
  - Terceiro `USUARIO` (comum, staff, superuser) e administrador registram com sucesso (REAP-19).
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: ~772 testes passam (+16)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(inovacoes): registra o reaproveitamento pela tela de sinalizacao`

**Status**: ✅ Complete — 769 passed (+16); toda recusa confere a contagem de registros no banco, e todo erro de campo é lido na lista `id_unidade_error` do select; a corrida (REAP-14) e a exclusão no meio do envio (REAP-16) usam monkeypatch no `form_valid`, que grava ou apaga antes de chamar o original, no padrão da STAT-13/STAT-22; o aviso de status no `form_valid` reusa a mensagem da `ValidationError` do método; o REAP-19 do POST cobre `USUARIO` comum, staff, superuser e administrador

---

### T6: Link de sinalização e seção "Reaproveitamentos" no detalhe ✅

**What**: O contexto `reaproveitamentos` na `InovacaoDetailView` e, no template do detalhe, o link condicionado ao status e a seção com contagem e lista.
**Where**: `inovacoes/templates/inovacoes/inovacao_detail.html`
**Depends on**: T5
**Reuses**: seção "Histórico de status" como modelo; `.vazio`; `pode_ser_reaproveitada` (T2); helper `_links` de `test_views_detalhe.py`
**Requirement**: REAP-01, REAP-02, REAP-17, REAP-18, REAP-43

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `InovacaoDetailView.get_context_data` ganha `reaproveitamentos=self.object.reaproveitamentos.select_related("unidade")`
- [x] Template: link "Sinalizar reaproveitamento" só com `pode_ser_reaproveitada`; `<section aria-labelledby="reaproveitamentos-titulo">` com `h2` "Reaproveitamentos", os três textos da REAP-17 e `<ol class="reaproveitamentos">`
- [x] `CONSULTAS_DO_DETALHE` 7 → 8, com comentário citando REAP-43
- [x] Testes e2e em `inovacoes/tests/test_views_detalhe.py`:
  - "Disponível" → exatamente um link "Sinalizar reaproveitamento" com `href="/inovacoes/<pk>/reaproveitar/"` para autor, terceiro `USUARIO` (comum, staff, superuser) e administrador (REAP-01).
  - "Em teste" e "Validada" → nenhum `href` para `/reaproveitar/` e nenhum texto "Sinalizar reaproveitamento" na página inteira, para todos esses perfis (REAP-02).
  - 0, 1 e 2 reaproveitamentos → "Nenhum reaproveitamento registrado.", "Reaproveitada por 1 unidade.", "Reaproveitada por 2 unidades." (REAP-17).
  - Lista com "<unidade> — <dd/mm/aaaa>" do mais antigo ao mais recente, com `data` forçada fora da ordem do `id`; reaproveitamentos de outra inovação não aparecem (REAP-18).
  - Número de consultas igual com 1 e com 4 reaproveitamentos (REAP-43).
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: ~786 testes passam (+14)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(inovacoes): mostra os reaproveitamentos no detalhe da inovacao`

**Status**: ✅ Complete — 784 passed (+15); teste antigo alterado como autorizado: `CONSULTAS_DO_DETALHE` 7 → 8 em `test_views_detalhe.py`, com comentário citando REAP-43; REAP-01 e REAP-02 percorrem autor, administrador e `nao_autor_usuario` (comum, staff, superuser) dentro do teste; REAP-18 força a `data` contra a ordem do `id`; registros de teste nascem pelo `registrar_reaproveitamento` (AD-012); contagem e plural no template a partir da lista já carregada

---

### T7: Componente `.reaproveitamentos` na `kira.css` ✅

**What**: O estilo da lista de reaproveitamentos do detalhe, no mesmo desenho da `.historico`, só com tokens de pares do DS-08.
**Where**: `templates/kira.css`
**Depends on**: T6
**Reuses**: regras `.historico` da F5; `test_ciclo_e_historico_so_usam_cores_de_pares_conferidos` e `CADEIA_DO_COMPONENTE`
**Requirement**: REAP-48 (detalhe)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Regras `.reaproveitamentos` (e itens) na `kira.css`, sem `="`, sem `<`, sem cor literal
- [x] `test_views_sistema_design.py`: o teste de cores do componente passa a cobrir `.reaproveitamentos` (parametrize + entradas em `CADEIA_DO_COMPONENTE`); todo par desenhado está em `PARES_DE_TEXTO`
- [x] Gate check passa: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q`
- [x] Test count: ~787 testes passam (+1)

**Tests**: e2e
**Gate**: build

**Commit**: `style(inovacoes): estiliza a lista de reaproveitamentos do detalhe`

**Status**: ✅ Complete — 785 passed (+1); teste antigo alterado como autorizado: o teste de cores do componente em `test_views_sistema_design.py` ganha `.reaproveitamentos` no parametrize e quatro entradas em `CADEIA_DO_COMPONENTE`; o componente repete o desenho da `.historico` (`text` e `text-muted` sobre `bg`, pares já no DS-08), sem cor nova. REAP-48 segue para o painel (T16). Build gate verde

---

### T8: `ReaproveitamentoAdmin` só para listar e excluir ✅

**What**: O admin de `Reaproveitamento` com o mixin da AD-007, sem inclusão nem alteração.
**Where**: `inovacoes/admin.py`
**Depends on**: T7
**Reuses**: `AcessoSomenteAdministradorMixin` (`contas/admin.py`); `inovacoes/tests/test_admin_listas.py` como modelo (fixture `usuario_staff`, telas forjadas)
**Requirement**: REAP-24 (admin), REAP-26, REAP-27

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `ReaproveitamentoAdmin` como no design: `list_display`, `list_select_related`, `has_add_permission`/`has_change_permission` → `False`
- [x] Testes e2e em `inovacoes/tests/test_admin_reaproveitamento.py`:
  - `ADMINISTRADOR` vê a listagem com inovação, unidade, responsável e data, e exclui um registro pela confirmação do admin (REAP-26).
  - `USUARIO` com `is_staff` e `USUARIO` com `is_superuser` recebem 403 na listagem, na tela de um registro e na exclusão, e o registro continua (REAP-26, L-003).
  - Para o `ADMINISTRADOR`: a URL de adicionar responde 403 e POST nela não cria registro; POST na URL de alteração responde 403 e não muda o registro (REAP-27).
  - A tela de exclusão de uma unidade referenciada (admin de `Unidade`) não a apaga e a lista como protegida (REAP-24).
- [x] Gate check passa: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q`
- [x] Test count: ~798 testes passam (+11)

**Tests**: e2e
**Gate**: build

**Commit**: `feat(inovacoes): permite ao administrador corrigir reaproveitamentos no admin`

**Status**: ✅ Complete — 801 passed (+16); o L-003 usa um `USUARIO` com `is_staff` e todas as permissões do modelo e um `USUARIO` com `is_staff` + `is_superuser`: o admin só dá 403 a quem tem `is_staff`; o superusuário sem `is_staff` é mandado ao login do admin (302), coberto por teste próprio sem exclusão; a tela do registro abre só para leitura (sem `_save`) e o POST nela dá 403; depois da exclusão o admin volta ao índice, não à lista (fora das ACs, não afirmado); REAP-24 pela tela de exclusão do admin de `Unidade` já passava (evidência). Build gate verde

---

### T9: Acesso e integridade da sinalização ✅

**What**: Evidências de anônimo, CSRF, banco indisponível e exclusão da inovação pela rota da F4 na sinalização.
**Where**: `inovacoes/tests/test_views_reaproveitar.py`
**Depends on**: T8
**Reuses**: padrões de `test_controle_autoria.py` (CSRF com `Client(enforce_csrf_checks=True)`) e `test_views_erro_500.py` (`OperationalError` forçado, `DETALHE_DA_CONEXAO`)
**Requirement**: REAP-20, REAP-21, REAP-23 (pela rota), REAP-49 (sinalização)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Anônimo, GET e POST em `/inovacoes/<pk>/reaproveitar/` → redirect ao login com `next`, zero registros (REAP-20)
- [x] POST sem token CSRF, do autor e de um terceiro → 403, zero registros (REAP-21)
- [x] Inovação com reaproveitamentos excluída pelo POST de `/inovacoes/<pk>/excluir/` (autor) → os registros dela somem e os de outra inovação ficam (REAP-23)
- [x] `OperationalError` forçado no método durante o POST → 500 do projeto sem o detalhe da conexão, zero registros (REAP-49)
- [x] Se alguma evidência falhar, a correção entra nesta task e o commit muda de tipo para `fix`
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: ~805 testes passam (+7)

**Tests**: e2e
**Gate**: full

**Commit**: `test(inovacoes): cobre acesso e integridade da sinalizacao de reaproveitamento`

**Status**: ✅ Complete — 807 passed (+6); todas as evidências passaram sem correção de produção, então o commit fica `test`; anônimo em GET e POST vai ao login com `next`; CSRF recusado para autor e terceiro; a exclusão pela rota da F4 leva os registros da inovação e deixa o da outra; o `OperationalError` é forçado no `Reaproveitamento.objects.create` dentro do método, e a página 500 não mostra host, usuário, senha nem traceback

---

### T10: Acessibilidade da sinalização ✅

**What**: Evidências de rótulo associado, erro com `aria-invalid`/`aria-describedby`, título e ordem de foco na tela de sinalização.
**Where**: `inovacoes/tests/test_views_acessibilidade_alteracao.py`
**Depends on**: T9
**Reuses**: helpers e asserções de ARIA da F2/F4/F5 no mesmo arquivo
**Requirement**: REAP-44, REAP-45

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `<label for>` do select aponta para o `id` do `<select>` (REAP-44)
- [x] Depois de POST inválido (REAP-11, REAP-12, REAP-13): o select tem `aria-invalid="true"` e `aria-describedby` com o `id` do elemento que contém a mensagem exata (REAP-45); sem erro, não há `aria-invalid`
- [x] Ordem dos focáveis do `main`: select → botão "Sinalizar reaproveitamento" → "Cancelar"
- [x] Se alguma evidência falhar, a correção entra nesta task e o commit muda de tipo para `fix`
- [x] Gate check passa: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q`
- [x] Test count: ~811 testes passam (+6)

**Tests**: e2e
**Gate**: build

**Commit**: `test(inovacoes): cobre a acessibilidade da sinalizacao de reaproveitamento`

**Status**: ✅ Complete — 813 passed (+6); todas as evidências passaram sem correção de produção, então o commit fica `test`; o `aria-describedby` do select é seguido até o elemento e o texto dele precisa conter a mensagem exata da REAP-11, REAP-12 e REAP-13; a ordem de foco é lida do `<main>` (o cabeçalho tem o "Sair") e o `main` não tem `tabindex`. Build gate verde. RF11 completo (linha de corte)

---

### T11: Agregações de `Categoria` e `Unidade` ✅

**What**: `CategoriaQuerySet.com_total_de_inovacoes` (Q3) e `UnidadeQuerySet.com_indicadores` (Q4), ligados como managers.
**Where**: `inovacoes/models.py`
**Depends on**: T10
**Reuses**: `InovacaoQuerySet` como modelo de QuerySet (AD-002); `registrar_reaproveitamento` (T2) para criar os dados de teste (AD-012)
**Requirement**: REAP-32, REAP-33 (dados)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `Categoria.objects = CategoriaQuerySet.as_manager()` e `Unidade.objects = UnidadeQuerySet.as_manager()`; Q3 e Q4 exatamente como no design, com o comentário do `.order_by()` vazio; `makemigrations --check` sem migration nova
- [x] Testes de integração em `inovacoes/tests/test_agregacoes.py`:
  - Categoria sem inovação aparece com `total == 0`; contagens corretas; ordem por total decrescente e nome no empate (REAP-32).
  - Unidade sem nada aparece com `0` e `0`; uma unidade com 2 inovações de origem e 3 reaproveitamentos feitos dá **2 e 3**, não 6 (fan-out).
  - Dois reaproveitamentos da mesma unidade em datas diferentes não quebram a subconsulta.
  - Ordem por inovações de origem decrescente e nome no empate (REAP-33).
  - Cada agregação é **uma** consulta (`django_assert_num_queries(1)`).
  - Os registros das listas iniciais da migration 0004 entram na contagem.
- [x] Gate check passa: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q`
- [x] Test count: ~820 testes passam (+9)

**Tests**: integration
**Gate**: build

**Commit**: `feat(inovacoes): adiciona as agregacoes por categoria e por unidade`

**Status**: ✅ Complete — 820 passed (+7); Q3 e Q4 exatamente como no design, sem migration nova; as contagens esperadas são listas literais montadas no teste, com as cinco categorias e as cinco unidades da migration 0004 dentro; o fan-out é provado com 2 de origem e 3 feitos (2 e 3, não 6); empates por nome cobertos nas duas agregações; cada agregação é uma consulta. Achado: o mutante sem o `.order_by()` vazio da Q4 sobrevive, porque o Django 5.2 já ignora o `Meta.ordering` em consultas com `GROUP BY` (desde o 3.1); o `.order_by()` fica, como no design, e o teste das duas datas fica como evidência do resultado, sem discriminar o `.order_by()`. Registros de teste pelo `registrar_reaproveitamento` (AD-012); a `data` é forçada por `update()` depois, como na T6. Build gate verde

---

### T12: App `indicadores` e a geometria das barras ✅

**What**: A app `indicadores` registrada em `INSTALLED_APPS` e o módulo `graficos.py` com `Barra`, `Grafico` e `barras()` puros.
**Where**: `indicadores/graficos.py`
**Depends on**: T11
**Reuses**: estrutura de app de `nucleo/` (`apps.py`, `__init__.py`); constantes do design (`AREA = 480`, `ALTURA_DA_LINHA = 44`)
**Requirement**: REAP-35, REAP-36 (geometria)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `indicadores/__init__.py`, `indicadores/apps.py` (`IndicadoresConfig`), `indicadores/tests/__init__.py`; `"indicadores"` em `INSTALLED_APPS` depois de `"inovacoes"`
- [x] `graficos.py`: `Barra(nome, valor, y, comprimento, x_valor)`, `Grafico(id, titulo, barras, altura)`, `barras(itens, atributo)` como no design
- [x] Testes unitários (`@pytest.mark.unit`, sem banco) em `indicadores/tests/test_graficos.py`:
  - O maior valor tem `comprimento == 480`; os outros são proporcionais com 2 casas (ex.: 1 de 3 → 160.0).
  - Valor 0 → `comprimento == 0` e `x_valor == 8`; todos zero → nenhum comprimento > 0 e sem `ZeroDivisionError`; lista vazia → `[]`.
  - `y` cresce 44 por linha; `x_valor = comprimento + 8`; ordem de entrada preservada.
  - `altura == len(barras) * 44`.
- [x] Gate check passa: `.venv/bin/pytest -q -m unit`
- [x] Test count: ~828 testes passam (+8)

**Tests**: unit
**Gate**: quick

**Commit**: `feat(indicadores): cria a app e a geometria dos graficos de barras`

**Status**: ✅ Complete — 831 passed (+11; 100 no gate quick `-m unit`); `Barra` e `Grafico` são `NamedTuple`; desvio pequeno do design: a altura vem de `Grafico.de(id, titulo, barras)`, porque o design chama `Grafico` com três argumentos e define quatro campos, e a função pública chama `barras` (nome do `tasks.md`), não `_barras`; as proporções esperadas são contas feitas à mão (3/7, 1/7, 2/7 de 480 com 2 casas, e 1 de 3 = 160.0); app registrada depois de `inovacoes` em `INSTALLED_APPS`

---

### T13: Página do painel com cards e tabelas ✅

**What**: A `PainelView`, a rota `/indicadores/` e o template `painel.html` com os dois cards, as duas tabelas e o estado vazio.
**Where**: `indicadores/views.py`
**Depends on**: T12
**Reuses**: Q1–Q4 (T11); `Grafico`/`barras` (T12); componentes `cartao`, `tabela`, `vazio`; padrão de `TemplateView` sem decorator (AD-006)
**Requirement**: REAP-29, REAP-30, REAP-31, REAP-32 (tela), REAP-33 (tela), REAP-37, REAP-38, REAP-39, REAP-40

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `indicadores/urls.py` (`app_name = "indicadores"`, `name="painel"`) e `path("indicadores/", include("indicadores.urls"))` em `config/urls.py`
- [x] `PainelView.get_context_data` como no design (já monta `graficos`, que a T14 desenha)
- [x] `indicadores/templates/indicadores/painel.html` estende o base: `title`/`h1` "Painel de indicadores", `dl.metricas` com os dois cards, seções com as tabelas e o ramo vazio
- [x] `test_views_sistema_design.py`: `RAIZES` ganha `indicadores/templates`; DS-01 10 → 11; `paginas` ganha "painel"
- [x] Testes e2e em `indicadores/tests/test_views_painel.py`:
  - 200, `<title>` começando por "Painel de indicadores" e `h1` (REAP-29).
  - Card "Inovações cadastradas" = total de inovações nos três status (REAP-30); card "Reaproveitamentos registrados" = total de registros (REAP-31).
  - Tabela "Inovações por categoria": cabeçalhos, uma linha por categoria inclusive zero, na ordem da REAP-32, conferida contra contagem feita no teste sem o QuerySet novo.
  - Tabela "Inovações por unidade": três colunas e os valores da REAP-33.
  - Sem inovação → os dois cards com "0", "Nenhuma inovação cadastrada ainda.", link "Cadastrar inovação" para `/inovacoes/nova/`, sem `<table>` nem `<svg>` (REAP-37).
  - Sinalizar e criar uma inovação entre duas requisições muda os números da segunda (REAP-38).
  - Nenhuma linha de `Inovacao`, `Reaproveitamento`, `Categoria` ou `Unidade` muda com o GET (REAP-39).
  - Anônimo → login com `next` (REAP-40).
  - `USUARIO` comum e administrador → 200.
- [x] Gate check passa: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q`
- [x] Test count: ~843 testes passam (+15)

**Tests**: e2e
**Gate**: build

**Commit**: `feat(indicadores): adiciona o painel com totais e distribuicoes`

**Status**: ✅ Complete — 841 passed (+10); teste antigo alterado como autorizado: `RAIZES` ganha `indicadores/templates`, DS-01 10 → 11 e `paginas` ganha "painel" em `test_views_sistema_design.py`; as tabelas são conferidas duas vezes, contra a contagem feita no teste por `filter().count()` e contra uma lista literal; REAP-38 cobre sinalizar, criar e apagar entre requisições; REAP-39 compara `values()` dos quatro modelos antes e depois do GET; REAP-37 confere o link "Cadastrar inovação" dentro do `.vazio`, porque o menu tem um link igual; o `painel.html` ainda não inclui os gráficos (a peça nasce na T14), mas a view já monta `graficos`; as fixtures de `inovacoes/tests/conftest.py` são reexportadas por `indicadores/tests/conftest.py`, sem cópia. Build gate verde

---

### T14: Gráficos de barras em SVG ✅

**What**: A peça `indicadores/grafico.html` com o SVG e a inclusão dos três gráficos no painel.
**Where**: `indicadores/templates/indicadores/grafico.html`
**Depends on**: T13
**Reuses**: `Grafico`/`Barra` (T12); contexto `graficos` (T13)
**Requirement**: REAP-34, REAP-35 (tela), REAP-36, REAP-47

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Peça como no design, com `{% localize off %}` nos atributos numéricos e `truncatechars:70` no nome; incluída em `painel.html` antes de cada tabela
- [x] `test_views_sistema_design.py`: `PECAS` ganha `indicadores/grafico.html`
- [x] Testes e2e em `indicadores/tests/test_views_painel.py`:
  - Três `<figure>` com `figcaption` "Inovações por categoria", "Inovações de origem por unidade" e "Reaproveitamentos feitos por unidade" (REAP-34).
  - Cada `<svg>` com `role="img"` e `aria-labelledby` apontando para o `figcaption` do mesmo título (REAP-47).
  - Os nomes no SVG estão na mesma ordem das linhas da tabela correspondente (REAP-34).
  - A barra do maior valor tem `width="480"`; uma proporcional sai com ponto decimal (ex.: `width="160.0"` ou `"160"`), nunca vírgula, com `LANGUAGE_CODE` `pt-BR` ativo (REAP-35).
  - Item com 0 tem nome e "0" em `<text>` e nenhum `<rect>`; gráfico todo zero (sem reaproveitamentos) não tem `<rect>` (REAP-35, REAP-36).
  - Nome com mais de 70 caracteres aparece truncado no SVG e inteiro na tabela.
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: ~852 testes passam (+9)

**Tests**: e2e
**Gate**: full

**Commit**: `feat(indicadores): desenha os graficos de barras do painel`

**Status**: ✅ Complete — 848 passed (+7); teste antigo alterado como autorizado: `PECAS` ganha `indicadores/grafico.html` em `test_views_sistema_design.py`; a peça segue o design, com `{% localize off %}` em volta do `<svg>`; as barras são lidas do SVG e conferidas, nome e valor, contra as linhas da tabela correspondente; mutantes conferidos à mão: sem o `localize off` (sai `160,0`) e com barra para o valor 0, ambos mortos. Spec-precision gaps: (1) a barra do maior valor sai `width="480.0"`, porque o comprimento é `float`; o `Done when` escreve `width="480"`, e o teste afirma o número (`float == 480`, 100% da área da REAP-35), não o literal; (2) a tradução pt-BR do Django para o texto truncado é `" %(truncated_text)s…"`, com espaço na frente, então o nome longo sai com um espaço inicial (o SVG o descarta) e cabe 68 caracteres mais "…"; o teste afirma o resultado da truncagem (termina em "…", até 70 caracteres, prefixo do nome, nome inteiro ausente do SVG e presente na tabela), não um tamanho literal

---

### T15: Link "Indicadores" no menu principal ✅

**What**: O link "Indicadores" no `nav` "Principal" do base, depois de "Cadastrar inovação".
**Where**: `templates/base.html`
**Depends on**: T14
**Reuses**: `_navegacao_principal` e `LINK` de `inovacoes/tests/test_views_cabecalho.py`
**Requirement**: REAP-28

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] `<a href="{% url 'indicadores:painel' %}">Indicadores</a>` dentro do `nav` "Principal"
- [x] Testes e2e em `inovacoes/tests/test_views_cabecalho.py`: o link `href="/indicadores/"` com texto "Indicadores" está no `nav` "Principal" da listagem, do detalhe, da sinalização e do próprio painel, depois de "Cadastrar inovação"; anônimo (tela de login) não vê o link (REAP-28)
- [x] Gate check passa: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q`
- [x] Test count: ~857 testes passam (+5)

**Tests**: e2e
**Gate**: build

**Commit**: `feat(nucleo): adiciona o link do painel de indicadores ao menu`

**Status**: ✅ Complete — 853 passed (+5); testes novos acrescentados ao fim de `test_views_cabecalho.py`, sem mudar os antigos; o link é procurado só dentro do `nav` "Principal" de quatro telas (listagem, detalhe, sinalização e o próprio painel), cada uma com 200 conferido, e sua posição é comparada com a de "Cadastrar inovação"; anônimo na tela de login não tem o link nem o `href` no cabeçalho. Nenhum teste antigo de foco ou de cabeçalho precisou mudar. Build gate verde

---

### T16: Componentes `.metricas`, `.metrica` e `.grafico` na `kira.css` ✅

**What**: O estilo dos cards de métrica e dos gráficos, com `fill` por token, e a conferência de contraste do `fill`.
**Where**: `templates/kira.css`
**Depends on**: T15
**Reuses**: tokens `--text`, `--text-muted`, `--brand-navy`, `--brand-blue`, `--surface`; `_corpos`, `_cor_desenhada`, `CADEIA_DO_COMPONENTE` e `PARES_DE_TEXTO` de `test_views_sistema_design.py`
**Requirement**: REAP-48

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Regras da tabela "CSS" do design; sem `="`, sem `<`, sem cor literal
- [x] `test_views_sistema_design.py`: o teste de cores do componente cobre `.metrica` e `.grafico`; teste novo lê `fill` de `.grafico__nome`/`.grafico__valor` (par com o fundo do `.cartao` em `PARES_DE_TEXTO`, ≥ 4.5:1) e de `.grafico__barra` (≥ 3:1 contra o fundo do `.cartao`); `fill` literal derruba o teste
- [x] Gate check passa: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q`
- [x] Test count: ~862 testes passam (+5)

**Tests**: e2e
**Gate**: build

**Commit**: `style(indicadores): estiliza os cards e os graficos do painel`

**Status**: ✅ Complete — 858 passed (+5); teste antigo alterado como autorizado em `test_views_sistema_design.py`: o teste de cores do componente ganha `.metrica` e `.grafico` no parametrize e cinco entradas em `CADEIA_DO_COMPONENTE` (com o `.cartao` como ancestral, de onde vem o fundo `surface`), e um teste novo lê o `fill` de `.grafico__nome`, `.grafico__valor` (par do DS-08, 4.5:1) e `.grafico__barra` (3:1) contra o fundo do cartão; regras da tabela "CSS" do design, mais `.metrica` e `.grafico` com `color: var(--text)`, porque o teste de cores exige uma regra com o seletor exato da classe, e `.metricas .metrica { margin-top: 0 }`, que anula o `.cartao + .cartao` dentro do grid; nenhuma cor nova, sem `="` e sem `<`; mutantes conferidos à mão: `fill` literal na barra e `.metrica dt` com `brand-blue-light`, ambos mortos. Build gate verde

---

### T17: Desempenho do painel (RNF08) ✅

**What**: Evidências de 2 s com o conjunto de demonstração e de número fixo de consultas no painel.
**Where**: `indicadores/tests/test_desempenho_painel.py`
**Depends on**: T16
**Reuses**: fixture `demonstracao`, `_medir` e `LIMITE_EM_SEGUNDOS` de `inovacoes/tests/test_desempenho.py`; `registrar_reaproveitamento` (AD-012)
**Requirement**: REAP-41, REAP-42

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Fixture cria 200 reaproveitamentos pelo `registrar_reaproveitamento` sobre inovações "Disponível" da demonstração, com unidades ≠ origem, fora da medição
- [x] GET autenticado de `/indicadores/` → 200, card com 500 inovações (ou o total da carga) e 200 reaproveitamentos, em menos de 2 s de servidor (REAP-41)
- [x] Número de consultas do GET igual com volume pequeno (1 inovação, 1 reaproveitamento) e com a demonstração + 200 (REAP-42)
- [x] Se alguma evidência falhar, a correção entra nesta task e o commit muda de tipo para `fix`
- [x] Gate check passa: `.venv/bin/pytest -q`
- [x] Test count: ~864 testes passam (+2)

**Tests**: e2e
**Gate**: full

**Commit**: `test(indicadores): mede o desempenho do painel com a demonstracao`

**Status**: ✅ Complete — 860 passed (+2); as evidências passaram sem mudança de produção, então o commit fica `test`; reusa `LIMITE_EM_SEGUNDOS` e a fixture `demonstracao` de `inovacoes/tests/test_desempenho.py`, mas não o `_medir`, que tem a URL da listagem fixa: o arquivo tem um `_medir` próprio para `/indicadores/`; os 200 reaproveitamentos nascem pelo `registrar_reaproveitamento` (AD-012), em inovações "Disponível" da demonstração e unidades ≠ origem, fora da medição; os cards conferem 500 e 200; a REAP-42 compara 1 inovação + 1 reaproveitamento com a demonstração + 200, mais uma categoria e uma unidade extras, para que as quatro tabelas da AC cresçam; mutante conferido à mão: um `count()` por unidade na view (N+1) derruba a REAP-42

---

### T18: Acessibilidade e falha de banco do painel ✅

**What**: Evidências de tabela semântica, alternativa textual dos gráficos, ordem de leitura e 500 sem detalhe no painel.
**Where**: `indicadores/tests/test_views_painel.py`
**Depends on**: T17
**Reuses**: `Elementos`/`_elementos` de `test_views_sistema_design.py`; padrão de `test_views_erro_500.py`
**Requirement**: REAP-46, REAP-47 (alternativa), REAP-49 (painel)

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Cada tabela tem `caption`; todo cabeçalho de coluna é `th scope="col"`; a primeira célula de cada linha é `th scope="row"` (REAP-46)
- [x] Cada `<figure>` de gráfico está na mesma `<section>` que a tabela com os mesmos números; todo valor de barra aparece também como célula da tabela (REAP-47)
- [x] Os cards usam `dl`/`dt`/`dd`, com o rótulo em `dt` e o número em `dd`
- [x] `OperationalError` forçado numa agregação → 500 do projeto sem o detalhe da conexão (REAP-49)
- [x] Se alguma evidência falhar, a correção entra nesta task e o commit muda de tipo para `fix`
- [x] Gate check passa: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q`
- [x] Test count: ~869 testes passam (+5)

**Tests**: e2e
**Gate**: build

**Commit**: `test(indicadores): cobre a acessibilidade e a falha de banco do painel`

**Status**: ✅ Complete — 865 passed (+5); as evidências passaram sem mudança de produção, então o commit fica `test`; testes novos no fim de `test_views_painel.py`; das linhas existentes, só o bloco de imports mudou (ganhou `HTMLParser`, `OperationalError`, `assertTemplateUsed`, os dois QuerySets, `DETALHE_DA_CONEXAO` e `_elementos`), sem tocar asserção; o `Elementos` do DS-01 é plano, sem fechamento de tag, e serve só para os cards; a REAP-46 e a REAP-47 usam uma árvore `Arvore` (HTMLParser com aninhamento) no próprio arquivo, para provar "primeira célula da linha" e "mesma `<section>`"; a REAP-47 confere que todo par (nome, valor) de cada gráfico é uma linha da coluna certa da tabela da mesma seção; a REAP-49 força o `OperationalError` em `com_total_de_inovacoes` e em `com_indicadores` (parametrizado), com 500 do projeto, sem host, usuário, senha, `OperationalError` nem traceback, e nenhum reaproveitamento a mais; mutantes conferidos à mão: `th scope=row` → `td`, `caption` removido, `scope=col` removido, `dt` trocado por `span` e um gráfico fora da seção, todos mortos. Spec-precision gap: o `What` cita "ordem de leitura", mas nem a REAP-46/47 nem o `Done when` definem uma ordem; não há teste de ordem além da ordem dos gráficos (REAP-34, T14). Build gate verde

### T19: Asserções de exibido rejeitam elementos escondidos (Fix 1, M41/M43/M44/M45) ✅

**What**: As asserções de "exibido" da F6 passam a valer também sobre o HTML que a página de fato exibe: o elemento exigido e cada ancestral não podem ter `hidden`, `inert` nem `aria-hidden="true"`, em qualquer caixa (L-028, L-030).
**Where**: `inovacoes/tests/visibilidade.py` (novo), `inovacoes/tests/test_views_detalhe.py`, `inovacoes/tests/test_views_reaproveitar.py`, `indicadores/tests/test_views_painel.py`
**Depends on**: T18
**Reuses**: os helpers de regex `_links`, `_secao`, `_conteudo`, `_card`, `_tabela` e `_graficos`, que rodam sem mudança sobre o HTML exibido; o critério de atributos do `ESCONDE` (F5), estendido para qualquer caixa e qualquer aspas
**Requirement**: REAP-01, REAP-03, REAP-15, REAP-17, REAP-18, REAP-30, REAP-31, REAP-33, REAP-34, REAP-37

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Um helper comum em `inovacoes/tests/` (já importado pelos testes de `indicadores`, sem dependência nova) devolve o HTML sem comentários e sem a subárvore de todo elemento com `hidden`, `inert`, `aria-hidden="true"` (qualquer caixa), `<template>` ou conteúdo de `<details>` fechado fora do `<summary>`
- [x] REAP-01: o link "Sinalizar reaproveitamento" com o `href` exato é achado também no HTML exibido, para autor, administrador e terceiro
- [x] REAP-17, REAP-18: a seção "Reaproveitamentos" exibida é idêntica à do HTML cru (texto da contagem, `<ol>` e itens)
- [x] REAP-03, REAP-15: o `<main>` exibido da sinalização é idêntico ao cru, com o formulário, ou com o texto da REAP-15 e o link "Voltar para a inovação"
- [x] REAP-30, REAP-31, REAP-33, REAP-34, REAP-37: `_card`, `_tabela` e `_graficos` dão o mesmo resultado no HTML cru e no exibido; o `.vazio` da REAP-37 também
- [x] Nenhuma asserção antiga removida, enfraquecida ou pulada; nenhum teste da F1 a F5 tocado; código de produção intacto
- [x] Morrem numa worktree temporária: M41, M43, M44, M45, `hidden` no `<section>` "Reaproveitamentos", no `<ol class="reaproveitamentos">`, no `<form>` da sinalização e em `<section aria-labelledby="por-categoria">`, mais as variantes com `aria-hidden="true"` e com `inert` num ancestral
- [x] Gate check passa: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q`
- [x] Test count: 865 testes passam (+0: reforça testes existentes)

**Tests**: e2e
**Gate**: build

**Commit**: `test(inovacoes): exige elementos visiveis nas assercoes de exibido da F6`

**Status**: ✅ Complete — 865 passed (+0: só reforço); novo `inovacoes/tests/visibilidade.py` com `exibido(html)`, um `HTMLParser` que devolve o HTML com o texto original das tags, menos comentários e subárvores escondidas, para que os helpers de regex rodem sem mudança sobre ele; numa página sem nada escondido o resultado é idêntico ao cru (154 testes das três suítes passam sem diferença). Asserções novas: REAP-01 `_links(exibido(html), SINALIZAR)`; `_reaproveitamentos` exige a seção exibida igual à crua; o teste da REAP-03 e o `_afirma_sem_elegiveis` exigem o `<main>` exibido igual ao cru; `_card`, `_tabela` e `_graficos` exigem o mesmo resultado nos dois HTMLs, e `_card`/`_tabela` agora dizem explicitamente quando não acham o elemento (antes, `AttributeError`); o `.vazio` da REAP-37 também. Nenhuma asserção antiga mudou; o `Arvore` da T18 e o `ESCONDE` da F5 ficam como estão, porque o filtro reaproveita os helpers de regex inteiros em vez de reescrevê-los sobre a árvore. Mutações numa worktree temporária, todas mortas (16): M41 (3 falhas), M43 (9), M44 (3), M45 (2), `hidden` na seção "Reaproveitamentos" (6), no `<ol class="reaproveitamentos">` (5), no `<form>` (1), na seção "Por categoria" (8), no `<li>` do item (5) e no `<p>` da contagem (5), `aria-hidden="TRUE"` no `<p class="acoes">` do M41 (3), `aria-hidden="true"` no `<dl class="metricas">` (3) e no "Nenhum reaproveitamento registrado." (1), `inert` na seção "Por unidade" (9) e `INERT` no `.cartao` da sinalização sem unidade elegível (3); worktree removida e árvore real limpa. Build gate verde

---

## Phase Execution Map

```
Phase 1 → Phase 2 → Phase 3 → Phase 4 ║ Phase 5 → Phase 6 → Phase 7 → Phase 8
                       RF11            ║ (linha de corte)   RF10       correção

Phase 1:  T1 → T2
Phase 2:  T3 → T4 → T5
Phase 3:  T6 → T7 → T8
Phase 4:  T9 → T10
Phase 5:  T11 → T12 → T13
Phase 6:  T14 → T15 → T16
Phase 7:  T17 → T18
Phase 8:  T19
```

Arcos de fronteira entre fases (a primeira task de cada fase depende da última da anterior):

```
T2 → T3
T5 → T6
T8 → T9
T10 → T11
T13 → T14
T16 → T17
T18 → T19
```

A execução é estritamente sequencial — não há paralelismo dentro de uma fase.

**Empacotamento previsto no Execute:** 18 tasks, com orçamento de ~7 por lote e corte apenas em
fronteira de fase:

| Lote | Fases | Tasks | Conteúdo |
| ---- | ----- | ----- | -------- |
| 1 | 1 + 2 | 5 | Modelo, regra e tela de sinalização |
| 2 | 3 + 4 | 5 | Detalhe, estilo, admin e evidências do RF11 |
| 3 | 5 + 6 | 6 | Painel: dados, página, gráficos, menu, estilo |
| 4 | 7 | 2 | Evidências do painel |
| Correção | 8 | 1 | Fix 1 da iteração 1 (T19), um worker só |

Os lotes 1 e 2 fecham o RF11. O corte por prazo cai exatamente entre os lotes 2 e 3. Mais de um lote
⇒ o Execute deve **oferecer** sub-agentes antes de começar.

---

## Task Granularity Check

| Task | Scope | Status |
| ---- | ----- | ------ |
| T1 | 1 modelo (+ migration gerada) | ✅ Granular |
| T2 | 1 método de consulta + 1 método de criação + 3 constantes, mesmo arquivo | ⚠️ 2-3 coisas coesas, mesmo arquivo |
| T3 | 1 campo + 1 formulário, mesmo arquivo | ⚠️ coeso, mesmo arquivo |
| T4 | 1 tela = view (GET) + rota + template (+ ajustes de varredura) | ⚠️ coeso — ver nota |
| T5 | 1 método da view | ✅ Granular |
| T6 | 1 trecho de template + 1 chave de contexto (+ 1 constante de teste) | ✅ Granular |
| T7 | 1 componente de CSS | ✅ Granular |
| T8 | 1 `ModelAdmin` | ✅ Granular |
| T9, T10 | 1 arquivo de teste cada (o código já existe) | ✅ Granular |
| T11 | 2 QuerySets da mesma natureza, mesmo arquivo | ⚠️ coeso, mesmo arquivo |
| T12 | 1 módulo puro (+ esqueleto de app declarativo) | ⚠️ coeso — ver nota |
| T13 | 1 tela = view + rota + template | ⚠️ coeso — ver nota |
| T14 | 1 peça de template (+ 3 includes) | ✅ Granular |
| T15 | 1 link no base | ✅ Granular |
| T16 | 1 grupo de componentes de CSS | ✅ Granular |
| T17, T18 | 1 arquivo de teste cada | ✅ Granular |
| T19 | 1 helper de teste + reforço de 3 arquivos de teste (correção da validação) | ⚠️ coeso, uma só lacuna |

**Nota sobre T4 e T13:** uma view Django não é testável sem rota e template. O `Where` nomeia o
arquivo principal; os demais estão no `Done when` e cobertos pelos mesmos testes. É o mesmo merge
backward da T3 da F5. Na T4, a varredura AD-009 e o DS-01 quebram no instante em que a rota e o
template existem, então ajustá-los é parte da mesma entrega, não uma task à parte.

**Nota sobre T12:** `apps.py`, `__init__.py` e a linha em `INSTALLED_APPS` são declarativos (matriz:
`none`). Vão junto do primeiro módulo testável da app, para que a T12 não produza código sem teste.

**Nota sobre T9, T10, T17 e T18:** o comportamento vem de tasks anteriores, do middleware ou do Django.
A task é a evidência das ACs; se a evidência acusar falta, o ajuste entra na mesma task.

---

## Diagram-Definition Cross-Check

| Task | Depends On (task body) | Diagram Shows | Status |
| ---- | ---------------------- | ------------- | ------ |
| T1 | None | (início da Fase 1) | ✅ Match |
| T2 | T1 | T1 → T2 | ✅ Match |
| T3 | T2 | T2 → T3 (arco de fronteira) | ✅ Match |
| T4 | T3 | T3 → T4 | ✅ Match |
| T5 | T4 | T4 → T5 | ✅ Match |
| T6 | T5 | T5 → T6 (arco de fronteira) | ✅ Match |
| T7 | T6 | T6 → T7 | ✅ Match |
| T8 | T7 | T7 → T8 | ✅ Match |
| T9 | T8 | T8 → T9 (arco de fronteira) | ✅ Match |
| T10 | T9 | T9 → T10 | ✅ Match |
| T11 | T10 | T10 → T11 (arco de fronteira) | ✅ Match |
| T12 | T11 | T11 → T12 | ✅ Match |
| T13 | T12 | T12 → T13 | ✅ Match |
| T14 | T13 | T13 → T14 (arco de fronteira) | ✅ Match |
| T15 | T14 | T14 → T15 | ✅ Match |
| T16 | T15 | T15 → T16 | ✅ Match |
| T17 | T16 | T16 → T17 (arco de fronteira) | ✅ Match |
| T18 | T17 | T17 → T18 | ✅ Match |
| T19 | T18 | T18 → T19 (arco de fronteira) | ✅ Match |

Nenhuma dependência aponta para uma fase posterior. Nenhuma task das Fases 1–4 depende das Fases 5–7.

---

## Test Co-location Validation

| Task | Code Layer Created/Modified | Matrix Requires | Task Says | Status |
| ---- | --------------------------- | --------------- | --------- | ------ |
| T1: modelo e migration | Modelo e constraints + Migration | integration | integration | ✅ OK |
| T2: regra no modelo | Regra do modelo | integration | integration | ✅ OK |
| T3: formulário | Formulário | integration | integration | ✅ OK |
| T4: tela (GET) | Views, rotas, templates | e2e | e2e | ✅ OK |
| T5: registro (POST) | Views | e2e | e2e | ✅ OK |
| T6: detalhe | Template + view do detalhe | e2e | e2e | ✅ OK |
| T7: CSS do detalhe | Folha de estilo | e2e | e2e | ✅ OK |
| T8: admin | Django admin | e2e | e2e | ✅ OK |
| T9: acesso e integridade | Views (evidência) | e2e | e2e | ✅ OK |
| T10: acessibilidade | Templates (evidência) | e2e | e2e | ✅ OK |
| T11: agregações | Agregações | integration | integration | ✅ OK |
| T12: app + geometria | Geometria do gráfico + config da app | unit (+ none) | unit | ✅ OK |
| T13: painel | Views, rotas, templates | e2e | e2e | ✅ OK |
| T14: gráficos | Templates | e2e | e2e | ✅ OK |
| T15: menu | Template base | e2e | e2e | ✅ OK |
| T16: CSS do painel | Folha de estilo | e2e | e2e | ✅ OK |
| T17: desempenho | Desempenho | e2e | e2e | ✅ OK |
| T18: acessibilidade e 500 | Templates (evidência) | e2e | e2e | ✅ OK |
| T19: exibido sem escondidos | Templates (evidência) | e2e | e2e | ✅ OK |

Nenhuma task tem `Tests: none`.

---

## Requirement Coverage

| Requisito | Tasks |
| --------- | ----- |
| REAP-01 | T6, T19 |
| REAP-02 | T6 |
| REAP-03 | T4, T19 |
| REAP-04 | T3, T4 |
| REAP-05 | T2, T5 |
| REAP-06 | T5 |
| REAP-07 | T2 |
| REAP-08 | T4 |
| REAP-09 | T4, T5 |
| REAP-10 | T2 |
| REAP-11, REAP-12 | T2, T5 |
| REAP-13 | T3, T5 |
| REAP-14 | T1, T2, T5 |
| REAP-15 | T4, T19 |
| REAP-16 | T4, T5 |
| REAP-17, REAP-18 | T6, T19 |
| REAP-19 | T4, T5 |
| REAP-20, REAP-21 | T9 |
| REAP-22 | T2, T5 |
| REAP-23 | T1, T9 |
| REAP-24 | T1, T8 |
| REAP-25 | T1 |
| REAP-26, REAP-27 | T8 |
| REAP-28 | T15 |
| REAP-29 | T13 |
| REAP-30, REAP-31 | T13, T19 |
| REAP-32 | T11, T13 |
| REAP-33 | T11, T13, T19 |
| REAP-34 | T14, T19 |
| REAP-35, REAP-36 | T12, T14 |
| REAP-37 | T13, T19 |
| REAP-38, REAP-39, REAP-40 | T13 |
| REAP-41, REAP-42 | T17 |
| REAP-43 | T6 |
| REAP-44, REAP-45 | T10 |
| REAP-46 | T18 |
| REAP-47 | T14, T18 |
| REAP-48 | T7, T16 |
| REAP-49 | T9, T18 |

**Coverage:** 49 total, 49 mapeados para tasks, 0 sem task. RF11 (Fases 1–4): REAP-01 a REAP-27,
REAP-43 a REAP-45 e a parte de sinalização da REAP-48/REAP-49.
