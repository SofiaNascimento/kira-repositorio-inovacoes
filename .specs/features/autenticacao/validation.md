# Autenticação (F1) Validation

**Date**: 2026-09-26
**Spec**: `.specs/features/autenticacao/spec.md`
**Diff range**: `7bd7907..HEAD` em `main` (HEAD = `3f7bc98`). `2095b21` (arquivos da skill, remoção do README) e `a36971a` (`.DS_Store`) ficaram fora da análise de código.
**Verifier**: independent sub-agent (author ≠ verifier)

**Verdict**: FAIL ❌

O gate passa limpo (66/66) e 19 de 22 mutantes morrem. O veredito é FAIL por dois motivos. Primeiro, a AUTH-22, como está escrita, é contrariada por um teste: `test_admin_perfil.py:46` afirma HTTP 200 para uma conta `USUARIO` abrindo a tela de administração de usuários. Segundo, a AUTH-08 não tem evidência para o corpo da resposta de login falho. O mutante M6 devolve a senha submetida no HTML e sobrevive. Outras quatro ACs têm evidência parcial.

---

## Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1–T5 | ✅ Done | Config e scaffold; cobertas pelo gate de build |
| T6–T11 | ✅ Done | Modelo, constraints, manager, sincronização de `is_staff` |
| T12 | ✅ Done | O Done-when "caminho não encontrado executa `set_password` descartável" não tem teste (mutante M4 sobreviveu) |
| T13–T18 | ✅ Done | - |
| T19–T22 | ✅ Done | - |
| T23–T25 | ✅ Done | - |

Todas as 25 tasks estão marcadas ✅ em `tasks.md`, sem bloqueio nem conclusão parcial. O cabeçalho do `tasks.md` ainda diz `Status: In Progress`.

---

## Spec-Anchored Acceptance Criteria

Todos os caminhos são relativos a `contas/tests/`.

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| AUTH-01 | username + senha: autentica, abre sessão, redireciona à home interna | `test_views_login.py:26` - `assertRedirects(resposta, "/", ...)`; `:27` - `int(client.session["_auth_user_id"]) == ana.pk` | ✅ PASS |
| AUTH-02 | e-mail case-insensitive autentica a mesma conta | `test_views_login.py:33-34` - `"ANA@X.com"` → redirect `/` e `_auth_user_id == ana.pk`; `test_backends.py:37` - `autenticar("AnA@X.CoM").pk == ana.pk` | ✅ PASS |
| AUTH-03 | continua anônimo, 200, exatamente uma mensagem "Usuário ou senha inválidos." | `test_views_login.py:40` - `status_code == 200`; `:41` - `"_auth_user_id" not in client.session`; `:42` - `content.count(MENSAGEM) == 1`; `test_forms.py:41` - `erro.messages == ["Usuário ou senha inválidos."]` | ✅ PASS |
| AUTH-04 | rejeita, erro preso ao campo, identificador preservado | `test_forms.py:18` - `set(form.errors) == {"username", "password"}`; `:26` - `== {"password"}`; `:34` - `'value="ana@x.com"' in str(form["username"])` | ✅ PASS (só no nível do form; o template usa `as_field_group`) |
| AUTH-05 | chave de sessão rotacionada; a anterior deixa de valer | `test_views_login.py:63` - `chave_depois != chave_antes`; `:64` - `SessionStore().exists(chave_antes) is False` | ✅ PASS |
| AUTH-06 | senha só como hash dos hashers do Django | `test_admin.py:60` - `criada.password != SENHA_NOVA`; `:61` - `criada.password.startswith("pbkdf2_sha256$")` (linha relida do banco por `objects.get`) | ✅ PASS (evidência real, só pelo caminho de criação no admin) |
| AUTH-07 | na criação **ou na troca** de senha, persiste só o hash | Criação: `test_admin.py:60-61`. Troca: **sem evidência**, nenhum teste troca a senha de uma conta | ❌ GAP (parcial) |
| AUTH-08 | nenhuma senha em texto puro no log, em corpo HTTP ou em página de erro, **inclusive no login falho** | Log: `test_signals.py:50-51` - `SENHA not in caplog.text`. Tela de edição do admin: `test_admin.py:75` - `SENHA_NOVA not in html`, `:78` - `'name="password"' not in html`. Corpo do login falho: **sem evidência** (`test_views_login.py:37-42` não verifica a senha). Página 500: `test_erro_500.py:48-57` proíbe detalhes do banco, mas não a senha submetida `"senha-forte-123"` | ❌ GAP (mutante M6 sobreviveu) |
| AUTH-09 | anônimo: toda tela interna redireciona ao login com `next` | `test_controle_acesso.py:71` - varredura, `assertRedirects(resposta, _login_com_next(caminho))` para toda rota fora da allowlist; `:78` - `"/entrar/?next=/"` | ✅ PASS (o admin fica fora da varredura; seu porteiro próprio manda a `/admin/login/?next=`) |
| AUTH-10 | `next` interno tem precedência sobre a home | `test_controle_acesso.py:87` - `assertRedirects(resposta, "/inovacoes/42/", ...)` | ✅ PASS |
| AUTH-11 | sessão ativa acessa telas de consulta, qualquer perfil | `test_controle_acesso.py:91-98` - parametrizado por `USUARIO`/`ADMINISTRADOR`, `client.get("/").status_code == 200` | ✅ PASS (evidência real, mas `/` é a única tela interna; F3 precisa estender a parametrização às telas de consulta) |
| AUTH-12 | autenticado pedindo login é redirecionado à home | `test_views_login.py:71` - `assertRedirects(resposta, "/", ...)` | ✅ PASS |
| AUTH-13 | encerra a sessão no servidor, **limpa o cookie de sessão**, redireciona ao login com "Sessão encerrada." | `test_views_logout.py:27` - `assertRedirects(resposta, "/entrar/")`; `:28` - `"_auth_user_id" not in client.session`; `:29` - `"Sessão encerrada." in ...`. Limpeza do cookie: **sem asserção** (um probe do Verifier mostrou `Set-Cookie` com `max-age=0`, mas nenhum teste afirma isso) | ❌ GAP (parcial) |
| AUTH-14 | cookie de sessão encerrada é tratado como anônimo | `test_views_logout.py:48` - `outro.get("/entrar/").status_code == 200`; `:49` - `SessionStore().exists(chave_antiga) is False` | ✅ PASS |
| AUTH-15 | expira após 8 h sem requisições | `test_sessao.py:40` - sessão vencida → `"/entrar/?next=/"`; `:52` - `now + 8h - 30s <= expira <= now + 8h` | ✅ PASS |
| AUTH-16 | campo único restrito a exatamente `USUARIO` e `ADMINISTRADOR` | `test_models.py:15` - `Usuario.Perfil.values == ["USUARIO", "ADMINISTRADOR"]`; `test_migracoes.py:20` - `{"perfil", "email"} <= colunas`; `test_constraints.py:38` | ✅ PASS |
| AUTH-17 | sem perfil explícito nasce `USUARIO` | `test_models.py:21` - `Usuario().perfil == USUARIO`; `:53` (persistido); `test_admin.py:59` (criada pelo admin) | ✅ PASS |
| AUTH-18 | perfil fora do enum: rejeita **com validation error** e **mantém o valor gravado** | `test_constraints.py:17-18` e `:25-26` - `pytest.raises(IntegrityError)`. Não há asserção de `ValidationError` para `perfil`. O independent test da spec pede "observar o `ValidationError`". Também não há asserção de que o valor gravado não mudou | ❌ GAP (o resultado afirmado difere do definido na spec) |
| AUTH-19 | um ponto de consulta; as demais features o usam | `test_models.py:27` - `is_administrador is True`; `:33` - `is False`. Cláusula "every other feature SHALL use it": auditada por grep. Toda decisão de autorização em `contas/admin.py:41,48,57` usa `is_administrador`. `admin.py:58-60` compara o campo cru só para detectar mudança | ⚠️ Spec-precision gap (a cláusula 2 é regra de processo, sem resultado observável por teste) |
| AUTH-20 | `createsuperuser` → `ADMINISTRADOR` | `test_models.py:43` - `admin.perfil == Usuario.Perfil.ADMINISTRADOR` (após `refresh_from_db`) | ✅ PASS |
| AUTH-21 | `USUARIO` que altera perfil (próprio ou alheio): 403 no handler; redirect ao login sem acesso ao admin | `test_admin_perfil.py:115` - `status_code == 403` e `:117` perfil inalterado (própria conta); `:126` - `403` e `:128` inalterado (terceiro); `:86-87` - `302` e `Location.startswith("/admin/login/")` | ✅ PASS (ver notas 1 e 2) |
| AUTH-22 | **só** `ADMINISTRADOR` abre as telas de administração de usuários e muda o perfil de outra conta | Ramo positivo: `test_admin_perfil.py:65-66` (200, `perfil` no form), `:77-79` e `:141-143` (promoção persiste). Ramo negativo: **contrariado**. `test_admin_perfil.py:46` afirma `status_code == 200` para um `USUARIO` com `is_staff` abrindo a tela de edição de usuário. `:56` abre a tela de um terceiro (só leitura) | ❌ GAP (o comportamento viola a AC como escrita) |
| AUTH-23 | conta inativa: **mesma mensagem genérica** e sem sessão | `test_backends.py:56` - `autenticar("ana", senha=SENHA) is None`. Mensagem e sessão pela view: **sem asserção** (um probe mostrou 200, sem sessão e 1 mensagem, mas nenhum teste afirma isso) | ❌ GAP (parcial) |
| AUTH-24 | sem CSRF: 403, sem tentativa de autenticação | `test_views_login.py:49` - `status_code == 403`; `:50` - `"_auth_user_id" not in cliente.session` (com a senha correta) | ✅ PASS |
| AUTH-25 | e-mail que só difere na caixa: rejeita com erro de unicidade | `test_constraints.py:45-46` - `IntegrityError`; `:64` - `"Já existe uma conta com este e-mail." in str(erro.value)` (via `full_clean`, `ValidationError`) | ✅ PASS |
| AUTH-26 | banco indisponível: página de erro, sem sessão, sem detalhes de conexão | `test_erro_500.py:38` - `status_code == 500`; `:39` - `assertTemplateUsed(resposta, "500.html")`; `:40` - sem `_auth_user_id`; `:56-57` - host, usuário, senha, `OperationalError` e `Traceback` ausentes | ✅ PASS (a falha é simulada no backend, não no driver) |
| AUTH-27 | falha de login loga timestamp e identificador, sem a senha | `test_signals.py:36` - `levelno == WARNING`; `:38` - `"ana@x.com" in mensagem`; `:40-41` - horário ISO dentro da janela; `:50` - `SENHA not in caplog.text` | ✅ PASS |

**Status**: ❌ Gaps presentes. 20/27 ACs batem com o resultado da spec, 6 têm gap e 1 tem spec-precision gap.

### Notas sobre as observações do autor

1. **AUTH-21 emendada.** O texto atual da spec já traz a emenda (403 no handler, redirect sem acesso ao admin), e os três testes a cobrem. O 403 sobre a conta de terceiro (`:126`) vem de `has_change_permission` falso, não de `save_model`: o mutante M15 só é morto pelo teste da própria conta. O ramo `change=False` de `save_model` (`admin.py:58`, POST forjado na tela de criação) não tem teste.
2. **Risco aceito: staff comum edita os próprios `groups`/`user_permissions`.** Não viola a AUTH-21: o perfil continua travado e esses campos não são campos de perfil. Viola a **AUTH-22** como escrita. A AC diz que *só* `ADMINISTRADOR` abre as telas de administração de usuários, e esse risco só existe porque um `USUARIO` com `is_staff` abre e salva a própria tela. O teste `test_admin_perfil.py:42-49` fixa exatamente esse comportamento. O independent test da spec também pede 403 para um `USUARIO` que tenta abrir a tela de usuários, e isso nunca acontece: o resultado é 200 com `is_staff` e 302 sem ele. Das duas uma: o código muda ou a spec é emendada. Hoje as duas coisas se contradizem.
3. **Risco aceito: fallback do `ModelBackend`.** Um probe do Verifier confirmou `authenticate(None, username="ana", ...)` → conta `ana` mesmo existindo `ANA`. **Não viola nenhuma AC.** A spec não define ambiguidade, e o match exato de username satisfaz a AUTH-01. A consequência é que o Done-when da T12 ("mais de uma linha ⇒ recusa") só vale para o backend isolado (`test_backends.py:59-63`), não para o sistema. O teste chama o backend direto e não pela cadeia.
4. **AUTH-06/07.** A evidência da AUTH-06 é real: a linha é relida do banco e o prefixo `pbkdf2_sha256$` é afirmado. A AUTH-07 não tem evidência para a troca de senha.
5. **AUTH-11.** A evidência é real (um mutante que negasse acesso por perfil morreria no parametrizado), mas se limita a `/`.

---

## Discrimination Sensor

Worktree temporário `/private/tmp/claude-502/verifier-scratch` a partir de `HEAD`, com `.env` copiado, pytest do `.venv` da raiz rodado a partir do scratch (import de `contas` confirmado no scratch). Baseline no scratch: 66 passaram. Cada mutante foi revertido com `git checkout -- <arquivo>` dentro do scratch.

| # | File:line | Description | Killed? |
| - | --------- | ----------- | ------- |
| M1 | `contas/backends.py:29` | `len(candidatos) != 1` → `== 0` (ambiguidade aceita a 1ª conta) | ✅ Killed (`test_backends.py::test_identificador_ambiguo_e_recusado`) |
| M2 | `contas/backends.py:36` | removido `and self.user_can_authenticate(usuario)` | ✅ Killed (`test_conta_inativa_e_recusada`) |
| M3 | `contas/backends.py:26` | busca só por `username__iexact` | ✅ Killed (4 testes) |
| M4 | `contas/backends.py:32` | removido o `set_password` descartável (dummy hash) | ❌ Survived → Fix 5 |
| M5 | `contas/forms.py:16` | mensagem vira "Senha incorreta para este usuário." | ✅ Killed (`test_views_login`, `test_forms`) |
| M6 | `contas/forms.py:21` | `password.widget.render_value = True`: a senha submetida volta no HTML do login falho (efeito confirmado por probe) | ❌ Survived → Fix 2 |
| M7 | `contas/views.py:22` | `redirect_authenticated_user = False` | ✅ Killed |
| M8 | `contas/views.py:36` | removido `messages.success(... "Sessão encerrada.")` | ✅ Killed |
| M9 | `contas/views.py:35` | logout só redireciona, sem `logout()` no servidor | ✅ Killed (2 testes) |
| M10 | `config/settings.py:56` | removido `LoginRequiredMiddleware` | ✅ Killed (3 testes) |
| M11 | `config/settings.py:149` | `SESSION_SAVE_EVERY_REQUEST = False` | ✅ Killed |
| M12 | `config/settings.py:148` | `SESSION_COOKIE_AGE` = 9 h | ✅ Killed |
| M13 | `contas/admin.py:41` | `get_readonly_fields` devolve os campos base para todos (`perfil` editável por staff) | ✅ Killed |
| M14 | `contas/admin.py:50` | removido o `return False` sobre conta de terceiro em `has_change_permission` | ✅ Killed |
| M15 | `contas/admin.py:61` | `raise PermissionDenied` → `pass` em `save_model` | ✅ Killed |
| M16 | `contas/admin.py:48` | removido o `return True` para `is_administrador` em `has_change_permission` | ✅ Killed (3 testes) |
| M17 | `contas/signals.py:20` | log sem o identificador | ✅ Killed |
| M18 | `contas/signals.py:20` | log carrega o dict `credentials` (com a senha) | ✅ Killed |
| M19 | `contas/apps.py:10` | receiver não é conectado em `ready()` | ✅ Killed (2 testes) |
| M20 | `contas/models.py:81` | removida a sincronização `is_staff = True` | ✅ Killed (3 testes) |
| M21 | `contas/models.py:29` | `create_superuser` não força `ADMINISTRADOR` | ✅ Killed |
| M22 | `contas/views.py:11` | `csrf_exempt` no `dispatch` do login | ⚪ Survived, **equivalente**: `LoginView.dispatch` já traz `@csrf_protect` (`django/contrib/auth/views.py:78`) e o 403 continua. Não é fraqueza de teste |
| M23 | `contas/admin.py:60` | `save_model` ignora o `perfil` do POST (só compara `obj.perfil`) | ✅ Killed |

**Sensor depth**: P0-full (auth). Sem ferramenta de mutação instalada; 22 mutações manuais cobrindo backend, form, views/logout, middleware, sessão, admin (os três ganchos), receiver de sinal, `apps.ready`, modelo e manager.
**Result**: 19/22 killed. Sobreviventes: 2 reais (M4, M6) e 1 equivalente (M22). FAIL ❌

**Isolamento**: `git status --porcelain` do worktree real antes = vazio; depois de `git worktree remove --force` e `git worktree prune` = vazio. **Idêntico.** Nenhum `git stash` foi usado.

---

## Interactive UAT Results

Não realizado: o Verifier roda sem usuário. Recomendado depois das correções para as telas de login, logout e admin.

---

## Code Quality

| Principle | Status |
| --------- | ------ |
| Minimum code | ✅ Backend, form, views e admin são subclasses finas dos componentes do Django. Uma redundância: `contas/views.py:11` aplica `@login_not_required`, que o `LoginView` do Django 5.2 já traz (`django/contrib/auth/views.py:65`). Inofensivo, e o comentário "única exceção" documenta a intenção |
| Surgical changes | ✅ Cada commit toca os arquivos da task. `config/urls.py` mantém o docstring do `startproject` |
| No scope creep | ✅ Sem autocadastro, throttling ou recuperação de senha. O endurecimento de cookies (T21) tem lastro em RNF02 |
| Matches patterns | ✅ Ruff limpo; nomes em português consistentes; comentários explicam o porquê |
| Spec-anchored outcome check (asserted values match spec) | ❌ AUTH-18 afirma `IntegrityError` onde a spec pede validation error; AUTH-22 afirma 200 onde a spec restringe |
| Per-layer Coverage Expectation met | ⚠️ Modelo 1:1 ✅; backend ✅; views sem o caminho de erro "senha não volta no corpo" (AUTH-08) nem o de conta inativa pela tela (AUTH-23); admin sem o ramo de criação de `save_model` |
| Every test maps to a spec requirement - no unclaimed tests | ✅ Os testes sem AC (`test_is_staff_concedido_manualmente_nao_e_revogado`, `test_identificador_ambiguo_e_recusado`, `test_campo_de_identificador_rotulado_e_acessivel`, `test_get_em_sair_nao_encerra_a_sessao`, `test_cookies_endurecidos_fora_de_debug`) mapeiam para Done-when de T11, T12, T14, T17 e T21 |
| Documented guidelines followed: none - strong defaults applied (`tasks.md`, Test Coverage Matrix) | ✅ |

Por arquivo:

| Arquivo | Observação |
| ------- | ---------- |
| `contas/models.py` | Limpo. O `TextChoices` no nível do módulo tem justificativa documentada. |
| `contas/backends.py` | Limpo. A recusa por ambiguidade é anulada no nível do sistema pelo fallback (nota 3). |
| `contas/forms.py` | Limpo. |
| `contas/views.py` | `@login_not_required` redundante (acima). |
| `contas/admin.py` | Lógica correta para o perfil. Não impede `USUARIO` staff de abrir as telas (AUTH-22) nem de editar `groups`/`user_permissions`/`is_staff`. |
| `contas/signals.py`, `contas/apps.py` | Limpos. |
| `config/settings.py` | Limpo. `SECRET_KEY` sem default força o `.env`, o que é intencional. |
| `templates/base.html`, `templates/500.html`, `contas/templates/contas/login.html`, `nucleo/*` | Limpos. |

---

## Edge Cases

- [ ] AUTH-23 conta inativa: o comportamento está correto (confirmado por probe: 200, sem sessão, 1 mensagem genérica), mas a mensagem e a ausência de sessão não são afirmadas pela tela. Só o backend é testado.
- [x] AUTH-24 CSRF ausente: 403 e sem sessão.
- [x] AUTH-25 e-mail duplicado por caixa: `IntegrityError` e `ValidationError` com mensagem em português.
- [x] AUTH-26 banco indisponível: 500, `500.html`, sem sessão, sem detalhes.
- [x] AUTH-27 log de tentativa malsucedida: identificador e horário, sem a senha.

---

## Gate Check

- **Gate command**: `ruff check . && ruff format --check . && python manage.py makemigrations --check --dry-run && pytest -q` (binários do `.venv` da raiz, worktree real, `-p no:cacheprovider` para não escrever `.pytest_cache`)
- **Result**: `ruff check`: All checks passed · `ruff format --check`: 46 files already formatted · `makemigrations --check`: No changes detected · `pytest -q`: **66 passed, 0 failed, 0 skipped** (9.74 s)
- **Test count before feature**: 0 (o repositório não tinha testes antes de `7bd7907..HEAD`)
- **Test count after feature**: 66
- **Delta**: +66
- **Skipped tests**: nenhum
- **Failures**: nenhuma

---

## Fix Plans

### Fix 1: AUTH-22 contrariada. `USUARIO` com `is_staff` abre as telas de administração de usuários

- **Root cause**: `UsuarioAdmin` só restringe o *campo* `perfil` e a edição de terceiros. `has_view_permission` e `has_module_permission` seguem as permissões de modelo, então um `USUARIO` com `is_staff` e `view/change_usuario` abre a listagem e a própria tela (e ainda edita `groups`/`user_permissions`, o risco aceito no design). `test_admin_perfil.py:42-49` fixa esse comportamento com `status_code == 200`.
- **Fix task** (escolher uma via, com aval do usuário):
  - **(a) Código segue a spec**: em `contas/admin.py`, `has_module_permission`, `has_view_permission`, `has_change_permission`, `has_add_permission` e `has_delete_permission` devolvem `request.user.is_administrador`. Reescrever `test_admin_perfil.py:42-56` para afirmar 403 (tela de edição, listagem) para `USUARIO` com `is_staff`. O risco dos `groups`/`user_permissions` some junto.
  - **(b) Spec segue o código**: emendar a AUTH-22 para "only `ADMINISTRADOR` SHALL change profile or superuser fields; other staff accounts MAY open their own record read-only for those fields", e corrigir o independent test. Registrar a decisão em STATE.md.
- **Verify**: `pytest -q contas/tests/test_admin_perfil.py`; o mutante M13/M14 continua morto.
- **Done when**: nenhum teste afirma um resultado que a AUTH-22 proíbe.
- **Priority**: Major

### Fix 2: AUTH-08 sem evidência no corpo da resposta de login falho e na página 500 (M6 sobreviveu)

- **Root cause**: `test_views_login.py:37-42` e `test_erro_500.py:46-57` não verificam a senha submetida.
- **Fix task**: em `test_views_login.py::test_credencial_invalida_rerenderiza_com_mensagem_unica`, afirmar `"errada-456" not in resposta.content.decode()`. Em `test_erro_500.py:48`, incluir `"senha-forte-123"` na lista `proibidos`.
- **Verify**: reaplicar M6 (`self.fields["password"].widget.render_value = True` em `contas/forms.py:21`) e confirmar que o teste falha.
- **Done when**: M6 morto; gate verde.
- **Priority**: Major (RNF02, Essencial)

### Fix 3: AUTH-18 afirma `IntegrityError`; a spec pede validation error e valor gravado inalterado

- **Fix task**: em `test_constraints.py`, acrescentar um teste que parte de uma conta salva, atribui `perfil = "CHEFE"`, afirma `pytest.raises(ValidationError)` em `full_clean()` com `"perfil" in erro.value.message_dict`, e depois de `refresh_from_db()` afirma `perfil == USUARIO`. No teste de `update()` em massa, envolver em `transaction.atomic()` e afirmar o valor persistido depois.
- **Priority**: Minor

### Fix 4: evidência parcial de AUTH-07, AUTH-13 e AUTH-23

- **AUTH-07**: teste que troca a senha (`set_password` + `save`, ou o formulário de troca do admin) e afirma o prefixo `pbkdf2_sha256$` e `!= senha` na linha relida.
- **AUTH-13**: em `test_views_logout.py:23`, fazer POST sem `follow` e afirmar `resposta.cookies[settings.SESSION_COOKIE_NAME]["max-age"] == 0` e valor vazio.
- **AUTH-23**: teste e2e com conta inativa em `/entrar/`: `status_code == 200`, `content.count("Usuário ou senha inválidos.") == 1`, `"_auth_user_id" not in client.session`.
- **Priority**: Minor

### Fix 5: dummy hash anti-timing sem teste (M4 sobreviveu; Done-when da T12)

- **Fix task**: em `test_backends.py`, com `monkeypatch`/`mock.patch.object(Usuario, "set_password")`, afirmar que o caminho "identificador inexistente" e o caminho "ambíguo" chamam `set_password` uma vez.
- **Verify**: reaplicar M4 (remover `contas/backends.py:32`) e confirmar a falha.
- **Priority**: Minor

### Observação sem fix obrigatório

- `save_model` com `change=False` (`contas/admin.py:58`) não tem teste. Um POST forjado na tela de criação por staff com `add_usuario` é recusado pelo código, mas nada prova isso. Se a via (a) do Fix 1 for escolhida, o ramo fica inalcançável para não administrador.

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
| AUTH-07 | Implementing | ❌ Needs Fix (Fix 4) |
| AUTH-08 | Implementing | ❌ Needs Fix (Fix 2) |
| AUTH-09 | Implementing | ✅ Verified |
| AUTH-10 | Implementing | ✅ Verified |
| AUTH-11 | Implementing | ✅ Verified |
| AUTH-12 | Implementing | ✅ Verified |
| AUTH-13 | Implementing | ❌ Needs Fix (Fix 4) |
| AUTH-14 | Implementing | ✅ Verified |
| AUTH-15 | Implementing | ✅ Verified |
| AUTH-16 | Implementing | ✅ Verified |
| AUTH-17 | Implementing | ✅ Verified |
| AUTH-18 | Implementing | ❌ Needs Fix (Fix 3) |
| AUTH-19 | Implementing | ✅ Verified (⚠️ cláusula 2 auditada por grep) |
| AUTH-20 | Implementing | ✅ Verified |
| AUTH-21 | Implementing | ✅ Verified |
| AUTH-22 | Implementing | ❌ Needs Fix (Fix 1) |
| AUTH-23 | Implementing | ❌ Needs Fix (Fix 4) |
| AUTH-24 | Implementing | ✅ Verified |
| AUTH-25 | Implementing | ✅ Verified |
| AUTH-26 | Implementing | ✅ Verified |
| AUTH-27 | Implementing | ✅ Verified |

---

## Summary

**Overall**: ❌ Not Ready

**Spec-anchored check**: 20/27 ACs matched spec outcome · 6 gaps (AUTH-07, 08, 13, 18, 22, 23) · 1 spec-precision gap (AUTH-19)
**Sensor**: 19/22 mutations killed (2 sobreviventes reais: M4, M6; 1 equivalente: M22)
**Gate**: 66 passed, 0 failed

**What works**: login por username e por e-mail case-insensitive, mensagem única, rotação de sessão, negação por padrão com varredura de rotas, `next`, logout no servidor, expiração de 8 h, perfil com constraint no banco, `createsuperuser` → `ADMINISTRADOR`, bloqueio de alteração de perfil com 403, log de falha sem senha, página 500 sem vazamento.

**Issues found**: AUTH-22 contrariada por comportamento e por teste (Fix 1, decisão de código ou de spec). AUTH-08 sem prova no corpo do login falho (Fix 2). Evidência parcial em AUTH-07, 13, 18, 23 (Fix 3, 4). Dummy hash sem teste (Fix 5).

**Next steps**: decidir a via do Fix 1 com o usuário; rotear os Fix 1–5 a um implementer; re-verificar (iteração 1 de 3).
