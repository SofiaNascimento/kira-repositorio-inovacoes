# Autenticação (F1) Validation

**Date**: 2026-09-26
**Iteration**: 2
**Spec**: `.specs/features/autenticacao/spec.md`
**Diff range**: `7bd7907..HEAD` em `main` (HEAD = `4d84cdc`). Correções desta iteração: `96d1b15..HEAD` (T26–T30). `2095b21` (arquivos da skill) e `a36971a` (`.DS_Store`) ficaram fora da análise de código.
**Verifier**: independent sub-agent (author ≠ verifier)

**Verdict**: FAIL ❌

Os seis gaps da iteração 1 foram fechados: AUTH-07, 08, 13, 18, 22 e 23 agora têm evidência que bate com a spec, e os dois sobreviventes da iteração 1 (M4, M6) morrem. O gate passa com 81/81. O veredito continua FAIL por um único motivo: o mutante **A5** sobrevive. Trocar `has_delete_permission` por `return True` (`contas/admin.py:50-51`) deixa um `USUARIO` com `is_staff` abrir a tela de exclusão de outra conta e apagá-la, e nenhum teste falha. O probe do Verifier confirmou o efeito (GET 200, POST 302, conta apagada). A tela de exclusão é uma das "user administration screens" da AUTH-22, mas não está em `TELAS_DE_USUARIO` (`contas/tests/test_admin_perfil.py:45`). O código de HEAD está correto (403); o que falta é o teste. O conserto é um teste só (Fix 1).

---

## Iteração 1 → 2

| Gap da iteração 1 | Task | Status agora | Evidência |
| ----------------- | ---- | ------------ | --------- |
| Fix 1: AUTH-22 contrariada (staff comum abria as telas de usuário) | T26 | ✅ Fechado no código e nos testes. ⚠️ Nova lacuna de teste: a tela de exclusão (mutante A5) | `contas/admin.py:38-51`; `test_admin_perfil.py:66` |
| Fix 2: AUTH-08 sem evidência no corpo do login falho e na página 500 (M6 sobreviveu) | T27 | ✅ Fechado. M6 morto | `test_views_login.py:50`; `test_erro_500.py:58` |
| Fix 3: AUTH-18 afirmava `IntegrityError` no lugar de validation error e valor inalterado | T28 | ✅ Fechado | `test_constraints.py:36-40`, `:27-28` |
| Fix 4: AUTH-07 (troca de senha), AUTH-13 (cookie), AUTH-23 (tela) parciais | T29 | ✅ Fechado nos três | `test_models.py:93-96`; `test_views_logout.py:66-67`; `test_views_login.py:59-61` |
| Fix 5: dummy hash sem teste (M4 sobreviveu) | T30 | ✅ Fechado. M4 morto | `test_backends.py:106`, `:114` |
| Observação: ramo `change=False` de `save_model` sem teste | T26 | ✅ Resolvido: o `save_model` saiu. `POST /admin/contas/usuario/add/` por staff comum dá 403 (probe) | `contas/admin.py:44-48` |
| Spec-precision gap AUTH-19 (cláusula de processo) | - | ⚠️ Continua; auditado por grep | ver tabela de ACs |

---

## Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1–T5 | ✅ Done | Config e scaffold; cobertos pelo gate de build |
| T6–T11 | ✅ Done | Modelo, constraints, manager, sincronização de `is_staff` |
| T12 | ✅ Done | O Done-when do dummy hash agora tem teste (T30) |
| T13–T18 | ✅ Done | - |
| T19–T22 | ✅ Done | - |
| T23 | ✅ Done | - |
| T24, T25 | ✅ Done | Revistas na T26: readonly e guarda do `save_model` removidos; o 403 vem de `has_change_permission` |
| T26 | ✅ Done | O Done-when lista "listagem, criação, próprio registro, registro de terceiro, índice". A exclusão ficou de fora (Fix 1) |
| T27–T30 | ✅ Done | Todos os Done-when conferidos contra o código e os testes |

Todas as 30 tasks estão marcadas ✅ em `tasks.md`, sem bloqueio nem conclusão parcial. Deriva de documentação, sem efeito no veredito: o cabeçalho diz `Status: In Progress`; as tabelas "Diagram-Definition Cross-Check", "Test Co-location Validation" e "Cobertura de requisitos por task" não incluem T26–T30; a primeira linha do "Phase Execution Map" para na Phase 5.

---

## Spec-Anchored Acceptance Criteria

Todos os caminhos são relativos a `contas/tests/`. Cada linha foi relida no HEAD `4d84cdc`.

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| AUTH-01 | username + senha: autentica, abre sessão, redireciona à home interna | `test_views_login.py:26` - `assertRedirects(resposta, "/", ...)`; `:27` - `int(client.session["_auth_user_id"]) == ana.pk`; `test_backends.py:71` pela cadeia | ✅ PASS |
| AUTH-02 | e-mail, case-insensitive, autentica a mesma conta | `test_views_login.py:32-34` - `"ANA@X.com"` → redirect `/` e `_auth_user_id == ana.pk`; `test_backends.py:37` - `autenticar("AnA@X.CoM").pk == ana.pk` | ✅ PASS |
| AUTH-03 | continua anônimo, HTTP 200, exatamente uma mensagem "Usuário ou senha inválidos." | `test_views_login.py:40` - `status_code == 200`; `:41` - `"_auth_user_id" not in client.session`; `:42` - `content.count(MENSAGEM) == 1`; `test_forms.py:41` - `erro.messages == ["Usuário ou senha inválidos."]` | ✅ PASS |
| AUTH-04 | rejeita, erro preso ao campo, identificador preservado | `test_forms.py:18` - `set(form.errors) == {"username", "password"}`; `:26` - `== {"password"}`; `:34` - `'value="ana@x.com"' in str(form["username"])` | ✅ PASS (só no nível do form, como na iteração 1) |
| AUTH-05 | chave de sessão rotacionada; a anterior deixa de valer | `test_views_login.py:82` - `chave_depois != chave_antes`; `:83` - `SessionStore().exists(chave_antes) is False` | ✅ PASS |
| AUTH-06 | senha só como hash dos hashers do Django | `test_admin.py:60` - `criada.password != SENHA_NOVA`; `:61` - `startswith("pbkdf2_sha256$")` (linha relida por `objects.get`) | ✅ PASS |
| AUTH-07 | na criação **ou na troca**, persiste só o hash | Criação: `test_admin.py:60-61`. Troca: `test_models.py:92` - `refresh_from_db()`; `:93` - `u.password != "Nova-senha-forte-2026"`; `:94` - `startswith("pbkdf2_sha256$")`; `:95-96` - nova confere, antiga não | ✅ PASS |
| AUTH-08 | nenhuma senha em texto puro no log, em corpo HTTP ou em página de erro, inclusive no login falho | Log: `test_signals.py:50-51` - `SENHA not in caplog.text`. Login falho: `test_views_login.py:50` - `senha_errada not in resposta.content.decode()`. Página 500: `test_erro_500.py:58,61-62` - `SENHA_SUBMETIDA` na lista `proibidos`, `trecho not in html`. Admin: `test_admin.py:75-78` | ✅ PASS (M6 morto) |
| AUTH-09 | anônimo: toda tela interna redireciona ao login com `next` | `test_controle_acesso.py:71` - varredura, `assertRedirects(resposta, _login_com_next(caminho))` para toda rota fora da allowlist; `:78` - `"/entrar/?next=/"` | ✅ PASS (o admin fica fora da varredura e manda a `/admin/login/?next=`) |
| AUTH-10 | `next` interno tem precedência sobre a home | `test_controle_acesso.py:87` - `assertRedirects(resposta, "/inovacoes/42/", ...)` | ✅ PASS |
| AUTH-11 | sessão ativa acessa as telas de consulta, qualquer perfil | `test_controle_acesso.py:91-98` - parametrizado por `USUARIO`/`ADMINISTRADOR`, `client.get("/").status_code == 200` | ✅ PASS (só `/` existe; F3 precisa estender a parametrização) |
| AUTH-12 | autenticado pedindo login vai para a home | `test_views_login.py:90` - `assertRedirects(resposta, "/", ...)` | ✅ PASS |
| AUTH-13 | encerra a sessão no servidor, limpa o cookie, redireciona ao login com "Sessão encerrada." | `test_views_logout.py:27` - `assertRedirects(resposta, "/entrar/")`; `:28` - `"_auth_user_id" not in client.session`; `:29` - `"Sessão encerrada." in ...`; `:66` - `cookie.value == ""`; `:67` - `cookie["max-age"] == 0` | ✅ PASS |
| AUTH-14 | cookie de sessão encerrada é tratado como anônimo | `test_views_logout.py:48` - `outro.get("/entrar/").status_code == 200`; `:49` - `SessionStore().exists(chave_antiga) is False` | ✅ PASS |
| AUTH-15 | expira após 8 h sem requisições | `test_sessao.py:40` - sessão vencida → `"/entrar/?next=/"`; `:52` - `now + 8h - 30s <= expira <= now + 8h` | ✅ PASS |
| AUTH-16 | campo único restrito a exatamente `USUARIO` e `ADMINISTRADOR` | `test_models.py:15` - `Usuario.Perfil.values == ["USUARIO", "ADMINISTRADOR"]`; `test_migracoes.py:20` - `{"perfil", "email"} <= colunas`; `test_constraints.py:52` | ✅ PASS |
| AUTH-17 | sem perfil explícito nasce `USUARIO` | `test_models.py:21` (instância), `:53` (persistido); `test_admin.py:59` (criada pelo admin) | ✅ PASS |
| AUTH-18 | perfil fora do enum: rejeita com validation error e mantém o valor gravado | `test_constraints.py:36-37` - `pytest.raises(ValidationError)` em `full_clean()`; `:38` - `"perfil" in erro.value.error_dict`; `:39-40` - `refresh_from_db()`, `perfil == USUARIO`. Pelo banco: `:25-28` - `IntegrityError` no `update()` e valor inalterado; `:17` no `create()` | ✅ PASS |
| AUTH-19 | um ponto de consulta; as demais features o usam | `test_models.py:27` - `is_administrador is True`; `:33` - `is False`. Cláusula "every other feature SHALL use it": grep por comparação crua de `perfil` fora dos testes só acha `contas/models.py:90`, o próprio ponto de consulta. `contas/admin.py:39-51` usa `is_administrador` | ⚠️ Spec-precision gap (a cláusula 2 é regra de processo, sem resultado observável por teste) |
| AUTH-20 | `createsuperuser` → `ADMINISTRADOR` | `test_models.py:43` - `admin.perfil == ADMINISTRADOR` (após `refresh_from_db`) | ✅ PASS |
| AUTH-21 | `USUARIO` que altera perfil (próprio ou alheio): 403 no handler; redirect ao login sem acesso ao admin | `test_admin_perfil.py:133` - `403` e `:135` perfil inalterado (própria conta); `:144` - `403` e `:146` inalterado (terceiro); `:104-105` - `302` e `Location.startswith("/admin/login/")` | ✅ PASS |
| AUTH-22 | **só** `ADMINISTRADOR` abre as telas de administração de usuários e muda o perfil de outra conta | Negativo: `test_admin_perfil.py:66` - parametrizado em 5 telas, `status_code == esperado` (403 em lista, criação, próprio registro, registro de terceiro; 404 no índice do app). Positivo: `:74` - 200 nas 5 telas para ADMINISTRADOR sem permissão de modelo; `:83-84` - `perfil` no form; `:95-97` - promoção persiste. **Sem evidência** para a tela de exclusão (`/<pk>/delete/`): mutante A5 sobrevive, e o probe mostra staff comum apagando conta alheia | ❌ GAP (evidência incompleta; comportamento do HEAD correto) |
| AUTH-23 | conta inativa: mesma mensagem genérica e sem sessão | `test_views_login.py:59` - `status_code == 200`; `:60` - `"_auth_user_id" not in client.session`; `:61` - `content.count(MENSAGEM) == 1`; `test_backends.py:56` | ✅ PASS |
| AUTH-24 | sem CSRF: 403, sem tentativa de autenticação | `test_views_login.py:68` - `status_code == 403`; `:69` - sem `_auth_user_id` (com a senha correta) | ✅ PASS |
| AUTH-25 | e-mail que só difere na caixa: rejeita com erro de unicidade | `test_constraints.py:59-60` - `IntegrityError`; `:78` - `"Já existe uma conta com este e-mail." in str(erro.value)` (`ValidationError` via `full_clean`) | ✅ PASS |
| AUTH-26 | banco indisponível: página de erro, sem sessão, sem detalhes de conexão | `test_erro_500.py:41` - `status_code == 500`; `:42` - `assertTemplateUsed(resposta, "500.html")`; `:43` - sem `_auth_user_id`; `:52-62` - host, usuário, senha, `OperationalError`, `Traceback` ausentes | ✅ PASS (a falha é simulada no backend, não no driver) |
| AUTH-27 | falha de login loga timestamp e identificador, sem a senha | `test_signals.py:36` - `levelno == WARNING`; `:38` - `"ana@x.com" in mensagem`; `:40-41` - horário ISO dentro da janela; `:50` - `SENHA not in caplog.text` | ✅ PASS |

**Status**: ❌ 1 gap (AUTH-22, tela de exclusão) · ⚠️ 1 spec-precision gap (AUTH-19). 25/27 ACs batem com o resultado da spec.

### Notas

1. **404 no índice do app, conferido no Django.** `.venv/lib/python3.13/site-packages/django/contrib/admin/sites.py:488-490`: `_build_app_dict` pula o modelo quando `has_module_permission` é falso. `:578-582`: `app_index` faz `raise Http404` quando a lista fica vazia. `Usuario` é o único modelo registrado da app `contas`, então o 404 é a forma do Django negar essa tela. A AUTH-22 não fixa código de status. O independent test fala em "observar o 403" na tela de usuários, e as telas de usuário propriamente ditas dão 403. Aceito.
2. **Criação exige `has_change_permission`.** `django/contrib/auth/admin.py:133-143`: `UserAdmin._add_view` nega com `PermissionDenied` quando falta permissão de alteração, antes mesmo de olhar `has_add_permission`. Por isso o caso `novo` de `test_admin_perfil.py:66` não discrimina `has_add_permission` (mutante A4, equivalente).
3. **`/admin/` responde 200 a staff comum.** É o índice do site, vazio para essa conta. Não é tela de administração de usuários e não vaza nada. Sem fix.
4. **Fallback do `ModelBackend`** (risco aceito no design): segue como na iteração 1, sem violar AC.

---

## Discrimination Sensor

Worktree temporário `/private/tmp/claude-502/verifier-scratch-2` a partir de `HEAD` (`4d84cdc`), com `.env` copiado. O pytest do `.venv` da raiz rodou no scratch, e o import de `contas` resolveu para o scratch. Baseline no scratch: 81 passaram. Cada mutante foi aplicado por substituição exata de texto (contagem 1 conferida), a suíte inteira rodou, e o arquivo voltou com `git checkout -- <arquivo>` dentro do scratch.

| # | File:line | Description | Killed? |
| - | --------- | ----------- | ------- |
| M4 | `contas/backends.py:32` | removido `UserModel().set_password(password)` (sobrevivente da iteração 1) | ✅ Killed (`test_identificador_inexistente_gasta_o_hash_descartavel`, `..._ambiguo_...`) |
| M6 | `contas/forms.py:21` | `self.fields["password"].widget.render_value = True` no `__init__` (sobrevivente da iteração 1) | ✅ Killed (`test_login_recusado_nao_devolve_a_senha_submetida`) |
| A1 | `contas/admin.py:48` | `has_change_permission` → `return True` | ✅ Killed (5 testes) |
| A2 | `contas/admin.py:42` | `has_view_permission` → `return request.user.is_staff` | ✅ Killed (3 testes) |
| A3 | `contas/admin.py:39` | `has_module_permission` → `return request.user.is_staff` | ⚪ Survived, **equivalente**: `sites.py:492-497` ainda exige ao menos uma permissão de modelo verdadeira, e todas as outras `has_*` negam. Probe: índice do app segue 404, todas as telas seguem 403 |
| A4 | `contas/admin.py:45` | `has_add_permission` → `return True` | ⚪ Survived, **equivalente**: `UserAdmin._add_view` exige `has_change_permission` (`auth/admin.py:133-143`), e o módulo continua oculto. Probe: GET e POST em `add/` seguem 403 |
| A5 | `contas/admin.py:51` | `has_delete_permission` → `return True` | ❌ **Survived** → Fix 1. Probe: staff comum faz GET em `/<pk>/delete/` = 200, POST = 302, conta de terceiro apagada |
| A6 | `contas/admin.py:48` | `has_change_permission` → `return request.user.is_staff` | ✅ Killed (5 testes) |
| A7 | `contas/admin.py:48` | `has_change_permission` → `is_administrador or obj == request.user` (volta o acesso ao próprio registro) | ✅ Killed (2 testes) |
| A8 | `contas/admin.py:42` | `has_view_permission` → `is_administrador or obj == request.user` | ✅ Killed (`[proprio_registro]`) |
| B1 | `contas/backends.py:29` | `len(candidatos) != 1` → `== 0` (ambiguidade aceita a 1ª conta) | ✅ Killed (2 testes) |
| B2 | `contas/backends.py:36` | removido `and self.user_can_authenticate(usuario)` | ✅ Killed (backend e tela) |
| B3 | `contas/backends.py:26` | `email__iexact` → `email` (caixa sensível) | ✅ Killed (3 testes) |
| B4 | `contas/backends.py:32` | dummy hash com `'x'` no lugar da senha submetida | ✅ Killed (2 testes) |
| F1 | `contas/forms.py:16` | mensagem vira "Senha incorreta para %(username)s." | ✅ Killed (3 testes) |
| V1 | `contas/views.py:22` | `redirect_authenticated_user = False` | ✅ Killed |
| V2 | `contas/views.py:35` | logout só redireciona, sem `LogoutView.post` (sem `logout()`) | ✅ Killed (3 testes, incluindo o do cookie) |
| V3 | `contas/views.py:36` | removido `messages.success(... "Sessão encerrada.")` | ✅ Killed |
| S1 | `config/settings.py` (MIDDLEWARE) | removido `LoginRequiredMiddleware` (default-deny) | ✅ Killed (3 testes) |
| S2 | `config/settings.py` | `SESSION_SAVE_EVERY_REQUEST = False` | ✅ Killed |
| S3 | `config/settings.py` | `SESSION_COOKIE_AGE` = 9 h | ✅ Killed |
| S4 | `config/settings.py` (AUTHENTICATION_BACKENDS) | removido `UsernameOrEmailBackend` da cadeia | ✅ Killed (3 testes) |
| G1 | `contas/signals.py:20` | log carrega o dict `credentials` (com a senha) | ✅ Killed |
| G2 | `contas/apps.py:10` | receiver não é conectado em `ready()` | ✅ Killed (2 testes) |
| D1 | `contas/models.py:81` | removida a sincronização `is_staff = True` | ✅ Killed (7 testes) |
| D2 | `contas/models.py:29` | `create_superuser` não força `ADMINISTRADOR` | ✅ Killed (4 testes) |
| D3 | `contas/models.py:90` | `is_administrador` → `perfil != USUARIO or is_staff` | ✅ Killed (7 testes) |
| D4 | `contas/models.py:47` | removido `choices=` do campo `perfil` (sem validation error) | ✅ Killed (`test_perfil_invalido_e_rejeitado_com_validation_error_e_valor_inalterado`) |

**Sensor depth**: P0-full (auth). Sem ferramenta de mutação instalada; 28 mutações manuais cobrindo backend (busca, ambiguidade, conta inativa, dummy hash), form, login e logout, default-deny, sessão, cadeia de backends, as cinco `has_*` do admin, receiver de sinal, `apps.ready`, modelo, manager e `choices`.
**Result**: 25/28 killed. Sobreviventes: 1 real (A5) e 2 equivalentes (A3, A4). FAIL ❌

**Isolamento**: `git status --porcelain` do worktree real antes = vazio; depois de `git worktree remove --force` e `git worktree prune` = vazio. **Idêntico.** `git worktree list` mostra só o worktree principal. O arquivo de probe foi criado e apagado só no scratch. Nenhum `git stash` foi usado.

---

## Interactive UAT Results

Não realizado: o Verifier roda sem usuário. Recomendado depois do Fix 1, para login, logout e admin.

---

## Code Quality

Escopo: arquivos alterados em `96d1b15..HEAD`.

| Principle | Status |
| --------- | ------ |
| Minimum code | ✅ `contas/admin.py` encolheu: cinco `has_*` de uma linha no lugar de readonly, guarda de `save_model` e lógica de terceiro. O import de `PermissionDenied` saiu junto |
| Surgical changes | ✅ `fix(contas)` toca só `admin.py`, o teste do admin e os docs. Os `test(contas)` só acrescentam testes; a única alteração em teste existente é a reescrita aprovada da T24 |
| No scope creep | ✅ |
| Matches patterns | ✅ Ruff limpo, nomes em português, comentário explica o porquê (`admin.py:34-37`) |
| Spec-anchored outcome check (asserted values match spec) | ✅ Os valores afirmados batem com a spec em todas as ACs cobertas; o gap da AUTH-22 é de falta de caso, não de valor errado |
| Per-layer Coverage Expectation met | ❌ Matriz do admin: "cada perfil × cada operação". A operação de exclusão não tem teste para nenhum dos perfis (Fix 1) |
| Every test maps to a spec requirement - no unclaimed tests | ✅ Todo teste novo cita AC no docstring (AUTH-07, 08, 13, 18, 22, 23, 03) |
| Documented guidelines followed: none - strong defaults applied (`tasks.md`, Test Coverage Matrix) | ✅ |

Por arquivo:

| Arquivo | Observação |
| ------- | ---------- |
| `contas/admin.py` | Correto e mínimo. As `has_*` supõem `request.user` autenticado; o `AdminSite.admin_view` garante isso (`sites.py:202-207`) antes de chamá-las |
| `contas/tests/test_admin_perfil.py` | A fixture concede `delete_usuario`, mas nenhuma tela de exclusão é pedida. É o buraco do A5 |
| `contas/tests/test_backends.py` | O espião do `set_password` é o jeito certo de observar um efeito colateral que é o próprio requisito |
| `contas/tests/test_constraints.py` | `transaction.atomic()` no `update()` permite reler o valor depois do `IntegrityError` |
| `contas/tests/test_erro_500.py` | Senha submetida na lista `proibidos`. Como o backend é trocado por um que só levanta erro, a asserção protege contra a página 500 ecoar o POST, que é o risco real |
| `contas/tests/test_models.py`, `test_views_login.py`, `test_views_logout.py` | Limpos, asserções no valor exato da spec |
| `.specs/.../tasks.md`, `design.md` | `design.md` atualizado de forma coerente. `tasks.md` com deriva de tabelas (ver Task Completion) |

---

## Edge Cases

- [x] AUTH-23 conta inativa: 200, mensagem genérica única, sem sessão, pela tela e pelo backend.
- [x] AUTH-24 CSRF ausente: 403 e sem sessão.
- [x] AUTH-25 e-mail duplicado por caixa: `IntegrityError` e `ValidationError` com mensagem em português.
- [x] AUTH-26 banco indisponível: 500, `500.html`, sem sessão, sem detalhes nem a senha submetida.
- [x] AUTH-27 log de tentativa malsucedida: identificador e horário, sem a senha.

---

## Gate Check

- **Gate command**: `ruff check . && ruff format --check . && python manage.py makemigrations --check --dry-run && pytest -q` (binários do `.venv` da raiz, worktree real, `-p no:cacheprovider` para não escrever `.pytest_cache`)
- **Result**: `ruff check`: All checks passed · `ruff format --check`: 48 files already formatted · `makemigrations --check`: No changes detected · `pytest -q`: **81 passed, 0 failed, 0 skipped** (12.08 s), exit 0
- **Test count before feature**: 0
- **Test count after feature**: 81 (iteração 1: 66)
- **Delta**: +81 no total; +15 nesta iteração. Dois testes da T24 foram removidos e substituídos por dois parametrizados (10 casos), com aprovação do autor. Nenhuma asserção foi enfraquecida: as que afirmavam 200 para staff comum viraram 403, o que é mais estrito
- **Skipped tests**: nenhum
- **Failures**: nenhuma

---

## Fix Plans

### Fix 1: tela de exclusão do admin sem teste (mutante A5 sobreviveu; AUTH-22)

- **Root cause**: `TELAS_DE_USUARIO` (`contas/tests/test_admin_perfil.py:45`) lista índice, lista, criação, próprio registro e registro de terceiro. Falta a exclusão. Ela é a única tela de usuário que depende só de `has_delete_permission`. As outras `has_*` negam no HEAD, mas nenhuma delas protege a exclusão.
- **Fix task** (T31): em `test_admin_perfil.py`, acrescentar a tela `"exclusao_de_terceiro": f"{LISTA}{terceiro.pk}/delete/"` ao parametrizado (403 para staff comum, 200 para o ADMINISTRADOR promovido) e um teste de POST forjado: `client.post(f"{LISTA}{terceiro.pk}/delete/", {"post": "yes"})` por `usuario_staff` → `status_code == 403` e `Usuario.objects.filter(pk=terceiro.pk).exists() is True`. Opcionalmente, a tela de troca de senha de terceiro (`/<pk>/password/`), que depende de `has_change_permission` e hoje dá 403 sem teste próprio.
- **Verify**: reaplicar A5 (`has_delete_permission` → `return True`) em worktree descartável e confirmar a falha.
- **Done when**: A5 morto; gate verde.
- **Priority**: Major (sem o teste, uma regressão deixaria staff comum apagar contas)

### Observação sem fix obrigatório

- A3 e A4 são equivalentes hoje porque outras camadas os mascaram (notas 1 e 2). Não pedem teste.
- Deriva de tabelas no `tasks.md` (Task Completion). Documentação, não gate.

---

## Requirement Traceability Update

Proposta. O Verifier **não** edita `spec.md`.

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| AUTH-01 | Implementing | ✅ Verified |
| AUTH-02 | Implementing | ✅ Verified |
| AUTH-03 | Implementing | ✅ Verified |
| AUTH-04 | Implementing | ✅ Verified |
| AUTH-05 | Implementing | ✅ Verified |
| AUTH-06 | Implementing | ✅ Verified |
| AUTH-07 | Implementing | ✅ Verified |
| AUTH-08 | Implementing | ✅ Verified |
| AUTH-09 | Implementing | ✅ Verified |
| AUTH-10 | Implementing | ✅ Verified |
| AUTH-11 | Implementing | ✅ Verified |
| AUTH-12 | Implementing | ✅ Verified |
| AUTH-13 | Implementing | ✅ Verified |
| AUTH-14 | Implementing | ✅ Verified |
| AUTH-15 | Implementing | ✅ Verified |
| AUTH-16 | Implementing | ✅ Verified |
| AUTH-17 | Implementing | ✅ Verified |
| AUTH-18 | Implementing | ✅ Verified |
| AUTH-19 | Implementing | ✅ Verified (⚠️ cláusula 2 auditada por grep) |
| AUTH-20 | Implementing | ✅ Verified |
| AUTH-21 | Implementing | ✅ Verified |
| AUTH-22 | Implementing | ❌ Needs Fix (Fix 1) |
| AUTH-23 | Implementing | ✅ Verified |
| AUTH-24 | Implementing | ✅ Verified |
| AUTH-25 | Implementing | ✅ Verified |
| AUTH-26 | Implementing | ✅ Verified |
| AUTH-27 | Implementing | ✅ Verified |

---

## Summary

**Overall**: ❌ Not Ready (um teste de distância)

**Spec-anchored check**: 25/27 ACs matched spec outcome · 1 gap (AUTH-22, tela de exclusão) · 1 spec-precision gap (AUTH-19)
**Sensor**: 25/28 mutations killed (1 sobrevivente real: A5; 2 equivalentes: A3, A4)
**Gate**: 81 passed, 0 failed

**What works**: tudo o que funcionava na iteração 1, e mais: telas de usuário do admin fechadas para staff comum, senha ausente do corpo do login falho e da página 500, validation error e valor inalterado para perfil inválido, hash na troca de senha, cookie zerado no logout, conta inativa recusada pela tela, dummy hash observado.

**Issues found**: A5 sobrevive porque a tela de exclusão não é testada (Fix 1).

**Next steps**: rotear o Fix 1 (T31) a um implementer e re-verificar na iteração 3 de 3.
