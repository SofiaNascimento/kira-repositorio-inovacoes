# Autenticação (F1) Validation

**Date**: 2026-09-26
**Iteration**: 3
**Spec**: `.specs/features/autenticacao/spec.md`
**Diff range**: `7bd7907..HEAD` em `main` (HEAD = `55a25bf`). Correções desta iteração: `083ccb5..HEAD` (T31: `8b2eca9` teste, `55a25bf` docs). `2095b21` (arquivos da skill) e `a36971a` (`.DS_Store`) ficaram fora da análise de código.
**Verifier**: independent sub-agent (author ≠ verifier)

**Verdict**: PASS ✅

O único gap da iteração 2 foi fechado. A tela de exclusão entrou no teste parametrizado das telas de usuário (`contas/tests/test_admin_perfil.py:51`, `:62`, afirmada em `:74` e `:91`), e um POST de exclusão forjado por staff comum com `delete_usuario` agora exige 403 e a conta preservada (`contas/tests/test_admin_perfil.py:82-83`). O mutante A5 morre, e morrem também duas variantes novas (A9, A10). O gate passa com 84/84. O sensor matou 16 de 18 mutantes; os dois sobreviventes (A3, A4) são equivalentes, reconfirmados por probe nesta iteração. 26 de 27 ACs batem com o resultado da spec; a AUTH-19 segue como spec-precision gap conhecido (cláusula de processo), sem reprovar.

---

## Iteração 2 → 3

| Gap da iteração 2 | Task | Status agora | Evidência |
| ----------------- | ---- | ------------ | --------- |
| Fix 1: tela de exclusão do admin sem teste (mutante A5 sobreviveu; AUTH-22) | T31 | ✅ Fechado. A5 morto (2 testes falham) | `contas/tests/test_admin_perfil.py:62`, `:74`, `:82-83`, `:91` |
| Spec-precision gap AUTH-19 (cláusula de processo) | - | ⚠️ Continua; auditado por grep | `contas/models.py:90` é a única comparação crua de `perfil` fora de testes |
| Deriva das tabelas de controle do `tasks.md` | `55a25bf` | ✅ Fechada: Phase 6 no mapa, no cross-check de dependências, na co-localização e na cobertura por requisito | `.specs/features/autenticacao/tasks.md:1049` |

---

## Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1–T5 | ✅ Done | Config e scaffold; cobertos pelo gate de build |
| T6–T11 | ✅ Done | Modelo, constraints, manager, sincronização de `is_staff` |
| T12–T18 | ✅ Done | Backend, cadeia, form, templates, login, logout, receiver |
| T19–T22 | ✅ Done | Home, default-deny, sessão, página 500 |
| T23–T25 | ✅ Done | Revistas na T26, como registrado no `tasks.md` |
| T26–T30 | ✅ Done | Correções da iteração 1 |
| T31 | ✅ Done | Os quatro Done-when conferidos: `exclusao_de_terceiro` em `TELAS_DE_USUARIO` (`test_admin_perfil.py:51`), POST forjado 403 + conta existe (`:82-83`), A5 morto (sensor abaixo), gate verde (84 passed) |

As 31 tasks estão `✅ Complete` em `tasks.md`, sem bloqueio nem conclusão parcial, e sem checkbox `- [ ]` aberto. Deriva cosmética, sem efeito no veredito: o cabeçalho segue `Status: In Progress` (`tasks.md:13`) e o título da T31 (`tasks.md:1024`) não leva o `✅` que os demais títulos levam.

---

## Spec-Anchored Acceptance Criteria

Todos os caminhos são relativos a `contas/tests/`. Cada linha foi relida no HEAD `55a25bf`.

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| AUTH-01 | username + senha: autentica, abre sessão, redireciona à home interna | `test_views_login.py:26` - `assertRedirects(resposta, "/", ...)`; `:27` - `int(client.session["_auth_user_id"]) == ana.pk`; `test_backends.py:71` - `authenticate(...).pk == ana.pk` pela cadeia | ✅ PASS |
| AUTH-02 | e-mail, case-insensitive, autentica a mesma conta | `test_views_login.py:32-34` - `"ANA@X.com"` → redirect `/` e `_auth_user_id == ana.pk`; `test_backends.py:37` - `autenticar("AnA@X.CoM").pk == ana.pk`; `:76` pela cadeia | ✅ PASS |
| AUTH-03 | continua anônimo, HTTP 200, exatamente uma mensagem "Usuário ou senha inválidos." | `test_views_login.py:40` - `status_code == 200`; `:41` - `"_auth_user_id" not in client.session`; `:42` - `content.count(MENSAGEM) == 1`; `test_forms.py:41` - `erro.messages == ["Usuário ou senha inválidos."]` | ✅ PASS |
| AUTH-04 | rejeita, erro preso ao campo, identificador preservado | `test_forms.py:18` - `set(form.errors) == {"username", "password"}`; `:26` - `== {"password"}`; `:34` - `'value="ana@x.com"' in str(form["username"])` | ✅ PASS (nível do form; a view só repassa o form do `AuthenticationForm`) |
| AUTH-05 | chave de sessão rotacionada; a anterior deixa de valer | `test_views_login.py:82` - `chave_depois != chave_antes`; `:83` - `SessionStore().exists(chave_antes) is False` | ✅ PASS |
| AUTH-06 | senha só como hash dos hashers do Django | `test_admin.py:60` - `criada.password != SENHA_NOVA`; `:61` - `startswith("pbkdf2_sha256$")` (linha relida por `objects.get`) | ✅ PASS |
| AUTH-07 | na criação ou na troca, persiste só o hash | Criação: `test_admin.py:60-61`. Troca: `test_models.py:92` - `refresh_from_db()`; `:93` - `u.password != "Nova-senha-forte-2026"`; `:94` - `startswith("pbkdf2_sha256$")`; `:95-96` - nova confere, antiga não | ✅ PASS |
| AUTH-08 | nenhuma senha em texto puro no log, em corpo HTTP ou em página de erro, inclusive no login falho | Log: `test_signals.py:50-51` - `SENHA not in caplog.text`. Login falho: `test_views_login.py:50` - `senha_errada not in resposta.content.decode()`. Página 500: `test_erro_500.py:58,61-62` - `SENHA_SUBMETIDA` em `proibidos`, `trecho not in html`. Admin: `test_admin.py:75-78` | ✅ PASS |
| AUTH-09 | anônimo: toda tela interna redireciona ao login com `next` | `test_controle_acesso.py:71` - varredura, `assertRedirects(resposta, _login_com_next(caminho))` em toda rota fora da allowlist; `:78` - `"/entrar/?next=/"` | ✅ PASS (o admin fica fora da varredura e manda a `/admin/login/?next=`, porteiro próprio) |
| AUTH-10 | `next` interno tem precedência sobre a home | `test_controle_acesso.py:87` - `assertRedirects(resposta, "/inovacoes/42/", ...)` | ✅ PASS |
| AUTH-11 | sessão ativa acessa as telas de consulta, qualquer perfil | `test_controle_acesso.py:91-98` - parametrizado em `USUARIO`/`ADMINISTRADOR`, `client.get("/").status_code == 200` | ✅ PASS (só `/` existe; F3 precisa estender a parametrização) |
| AUTH-12 | autenticado pedindo login vai para a home | `test_views_login.py:90` - `assertRedirects(resposta, "/", ...)` | ✅ PASS |
| AUTH-13 | encerra no servidor, limpa o cookie, redireciona ao login com "Sessão encerrada." | `test_views_logout.py:27` - `assertRedirects(resposta, "/entrar/")`; `:28` - `"_auth_user_id" not in client.session`; `:29` - `"Sessão encerrada." in ...`; `:66` - `cookie.value == ""`; `:67` - `cookie["max-age"] == 0` | ✅ PASS |
| AUTH-14 | cookie de sessão encerrada é tratado como anônimo | `test_views_logout.py:48` - `outro.get("/entrar/").status_code == 200`; `:49` - `SessionStore().exists(chave_antiga) is False` | ✅ PASS |
| AUTH-15 | expira após 8 h sem requisições | `test_sessao.py:40` - sessão vencida → `"/entrar/?next=/"`; `:52` - `now + 8h - 30s <= expira <= now + 8h` | ✅ PASS |
| AUTH-16 | campo único restrito a exatamente `USUARIO` e `ADMINISTRADOR` | `test_models.py:15` - `Usuario.Perfil.values == ["USUARIO", "ADMINISTRADOR"]`; `test_migracoes.py:20` - `{"perfil", "email"} <= colunas`; `test_constraints.py:52` - os dois valores gravam | ✅ PASS |
| AUTH-17 | sem perfil explícito nasce `USUARIO` | `test_models.py:21` (instância), `:53` (persistido); `test_admin.py:59` (criada pelo admin) | ✅ PASS |
| AUTH-18 | perfil fora do enum: validation error e valor gravado inalterado | `test_constraints.py:36-37` - `pytest.raises(ValidationError)` em `full_clean()`; `:38` - `"perfil" in erro.value.error_dict`; `:39-40` - `refresh_from_db()`, `perfil == USUARIO`. Pelo banco: `:17` (`create`), `:25-28` (`update` + valor inalterado) | ✅ PASS |
| AUTH-19 | um ponto de consulta; as demais features o usam | `test_models.py:27` - `is_administrador is True`; `:33` - `is False`. Cláusula "every other feature SHALL use it": grep por comparação crua de `perfil` fora de testes e migrations só acha `contas/models.py:90`, o próprio ponto. `contas/admin.py:39-51` usa `is_administrador` | ⚠️ Spec-precision gap (a cláusula 2 é regra de processo, sem resultado observável por teste) |
| AUTH-20 | `createsuperuser` → `ADMINISTRADOR` | `test_models.py:43` - `admin.perfil == ADMINISTRADOR` (após `refresh_from_db`) | ✅ PASS |
| AUTH-21 | `USUARIO` que altera perfil (próprio ou alheio): 403 no handler; redirect ao login sem acesso ao admin | `test_admin_perfil.py:150` - `403` e `:152` perfil inalterado (própria conta); `:161` - `403` e `:163` inalterado (terceiro); `:121-122` - `302` e `Location.startswith("/admin/login/")` | ✅ PASS |
| AUTH-22 | só `ADMINISTRADOR` abre as telas de administração de usuários e muda o perfil de outra conta | Negativo: `test_admin_perfil.py:74` - parametrizado em 6 telas (`:45-52`), `status_code == esperado`: 403 em lista, criação, próprio registro, registro de terceiro e **exclusão de terceiro**; 404 no índice do app. POST de exclusão forjado: `:82` - `status_code == 403`; `:83` - `Usuario.objects.filter(pk=terceiro.pk).exists()`. Positivo: `:91` - 200 nas 6 telas para ADMINISTRADOR sem permissão de modelo; `:101` - `perfil` no form; `:112-114` e `:176-178` - promoção persiste | ✅ PASS |
| AUTH-23 | conta inativa: mesma mensagem genérica e sem sessão | `test_views_login.py:59` - `status_code == 200`; `:60` - `"_auth_user_id" not in client.session`; `:61` - `content.count(MENSAGEM) == 1`; `test_backends.py:56` - `is None` | ✅ PASS |
| AUTH-24 | sem CSRF: 403, sem tentativa de autenticação | `test_views_login.py:68` - `status_code == 403`; `:69` - sem `_auth_user_id` (com a senha correta) | ✅ PASS |
| AUTH-25 | e-mail que só difere na caixa: rejeita com erro de unicidade | `test_constraints.py:59-60` - `IntegrityError`; `:78` - `"Já existe uma conta com este e-mail." in str(erro.value)` (`ValidationError` via `full_clean`) | ✅ PASS |
| AUTH-26 | banco indisponível: página de erro, sem sessão, sem detalhes de conexão | `test_erro_500.py:41` - `status_code == 500`; `:42` - `assertTemplateUsed(resposta, "500.html")`; `:43` - sem `_auth_user_id`; `:52-62` - host, usuário, senha, `OperationalError`, `Traceback` ausentes | ✅ PASS (falha simulada no backend, não no driver) |
| AUTH-27 | falha de login loga timestamp e identificador, sem a senha | `test_signals.py:36` - `levelno == WARNING`; `:38` - `"ana@x.com" in mensagem`; `:40-41` - horário ISO dentro da janela; `:50` - `SENHA not in caplog.text` | ✅ PASS |

**Status**: ✅ 26/27 ACs batem com o resultado da spec · ⚠️ 1 spec-precision gap (AUTH-19, cláusula de processo, não reprova).

### Notas

1. **404 no índice do app** (decisão já validada; reconferida): `django/contrib/admin/sites.py` pula o modelo em `_build_app_dict` quando `has_module_permission` é falso, e `app_index` levanta `Http404` com a lista vazia. `Usuario` é o único modelo da app `contas`.
2. **A3 e A4 seguem equivalentes.** Probe desta iteração, staff comum com as quatro permissões de modelo, em HEAD, com A3 e com A4: `GET /admin/contas/` = 404, `GET add/` = 403, `POST add/` = 403, conta não criada, `contas` ausente do índice `/admin/`. Os três estados são idênticos. A3 é mascarado porque `sites.py` ainda exige uma `has_*` de modelo verdadeira; A4 porque `UserAdmin._add_view` exige `has_change_permission`.
3. **`/admin/` responde 200 a staff comum**: é o índice do site, vazio para essa conta. Não é tela de usuário. Sem fix.

---

## Discrimination Sensor

Worktree temporário `/private/tmp/claude-502/verifier-scratch-3` a partir de `HEAD` (`55a25bf`), com `.env` copiado. O pytest do `.venv` da raiz rodou com cwd no scratch; `import contas` resolveu para `/private/tmp/claude-502/verifier-scratch-3/contas/__init__.py`. Baseline no scratch: 84 passaram. Cada mutante foi aplicado por substituição exata de texto (contagem 1 conferida), a suíte inteira rodou, e o arquivo original voltou do backup em memória.

| # | File:line | Description | Killed? |
| - | --------- | ----------- | ------- |
| A5 | `contas/admin.py:51` | `has_delete_permission` → `return True` (sobrevivente da iteração 2) | ✅ Killed (`test_usuario_com_staff_nao_abre_as_telas_de_usuario[exclusao_de_terceiro]`, `test_usuario_com_staff_forjando_exclusao_recebe_403`) |
| M4 | `contas/backends.py:32` | removido `UserModel().set_password(password)` (regressão, iteração 1) | ✅ Killed (2 testes do hash descartável) |
| M6 | `contas/forms.py:21` | `password.widget.render_value = True` (regressão, iteração 1) | ✅ Killed (`test_login_recusado_nao_devolve_a_senha_submetida`) |
| A9 | `contas/admin.py:51` | `has_delete_permission` → `return request.user.is_staff` (novo) | ✅ Killed (2 testes) |
| A10 | `contas/admin.py:51` | `has_delete_permission` → `is_administrador or obj is not None` (novo: libera a exclusão de registro específico) | ✅ Killed (2 testes) |
| A3 | `contas/admin.py:39` | `has_module_permission` → `return request.user.is_staff` | ⚪ Survived, **equivalente** (nota 2, probe idêntico ao HEAD) |
| A4 | `contas/admin.py:45` | `has_add_permission` → `return True` | ⚪ Survived, **equivalente** (nota 2, probe idêntico ao HEAD) |
| B5 | `contas/backends.py:36` | `check_password(...) and user_can_authenticate(...)` → `or` (novo) | ✅ Killed (6 testes: senha errada, conta inativa, tela) |
| B6 | `contas/backends.py:26` | `username__iexact` → `username` (novo) | ✅ Killed (2 testes de ambiguidade) |
| B7 | `contas/backends.py:27` | `[:2]` → `[:1]` (ambiguidade não detectada; novo) | ✅ Killed (2 testes) |
| F2 | `contas/forms.py:21` | `password.required = False` (novo) | ✅ Killed (`test_formulario_vazio_...`, `test_senha_vazia_...`) |
| V4 | `contas/views.py:32` | `next_page = "/"` no logout (novo) | ✅ Killed (`test_post_em_sair_encerra_...`) |
| V5 | `contas/views.py:35` | logout só redireciona, sem `LogoutView.post` / `logout()`; a mensagem continua | ✅ Killed (3 testes, incluindo cookie e sessão revogada) |
| S5 | `nucleo/views.py:6` | `@login_not_required` na home (fura o default-deny; novo) | ✅ Killed (varredura, `next`, sessão expirada) |
| S6 | `config/settings.py:148` | `SESSION_COOKIE_AGE` = 7 h (novo) | ✅ Killed (`test_requisicao_dentro_da_janela_...`) |
| G3 | `contas/signals.py:18` | `logger.warning` → `logger.info` (novo) | ✅ Killed (`test_login_recusado_gera_warning_...`) |
| G4 | `contas/signals.py:20` | identificador substituído por `"***"` no log (novo) | ✅ Killed (`test_login_recusado_gera_warning_...`) |
| D5 | `contas/models.py:90` | `is_administrador` → `perfil in PerfilUsuario.values` (todo mundo é admin; novo) | ✅ Killed (12 testes) |

**Sensor depth**: P0-full (auth). Sem ferramenta de mutação instalada; 18 mutações manuais cobrindo admin (as três variantes de exclusão, módulo, criação), backend (busca, ambiguidade, conta inativa, dummy hash), form, logout, default-deny, sessão, receiver e ponto de consulta do perfil. As 28 mutações da iteração 2 não foram todas repetidas; o código de produção não mudou desde `083ccb5` (só teste e docs), então os mutantes mortos na iteração 2 continuam mortos por construção, e as regressões obrigatórias (A5, M4, M6) foram reexecutadas.
**Result**: 16/18 killed, 0 sobreviventes reais, 2 equivalentes (A3, A4). PASS ✅

**Isolamento**: `git status --porcelain` do worktree real antes = vazio; depois de `git worktree remove --force` e `git worktree prune` = vazio. **Idêntico** (`diff` sem saída). `git worktree list` mostra só o worktree principal; o diretório do scratch não existe mais. O arquivo de probe foi criado e apagado só no scratch. `git stash list` vazio; nenhum `git stash` usado.

---

## Interactive UAT Results

O Verifier roda sem usuário. O UAT foi feito depois, em 2026-09-27, pelo orquestrador, a pedido do usuário. Foi executado contra o `runserver` local (PostgreSQL 16, `DJANGO_DEBUG=True`) por um cliente HTTP com cookies e CSRF reais, sem navegador gráfico. O estado final foi conferido direto no banco.

**Resultado: 24 de 24 checagens PASS.**

| # | Roteiro | Resultado observado | AC | Status |
| - | ------- | ------------------- | -- | ------ |
| 1 | `GET /` sem sessão | 302 → `/entrar/?next=/` | AUTH-09, AUTH-10 | ✅ |
| 2 | Login por username | POST 302 → `/`; `GET /` 200 | AUTH-01 | ✅ |
| 3 | Login por `ADMIN@KIRA.LOCAL` | 302 → `/` | AUTH-02 | ✅ |
| 4 | Senha errada (`admin`) e usuário inexistente | 200 nos dois, mesmo alerta "Usuário ou senha inválidos.", sem cookie de sessão; identificador repopulado, senha ausente do HTML | AUTH-03, AUTH-04 | ✅ |
| 5 | Log do servidor | Três linhas `Tentativa de login malsucedida para '<identificador>' em <timestamp>`; zero ocorrências das senhas usadas no log | AUTH-27, AUTH-08 | ✅ |
| 6 | `GET /entrar/` já autenticado | 302 → `/` | AUTH-12 | ✅ |
| 7 | `POST /sair/`, depois reuso do `sessionid` antigo | 302 → `/entrar/`; cookie antigo em `GET /` → 302 → `/entrar/?next=/` | AUTH-13, AUTH-14 | ✅ |
| 8 | Admin cria `uat_usuario` sem perfil | Formulário de criação sem campo `perfil`; conta criada com `USUARIO`, senha `pbkdf2_sha256` | AUTH-17, AUTH-06 | ✅ |
| 9 | Admin desativa a conta; login com ela | Antes de desativar, entra (302 → `/`). Depois: 200, mesma mensagem genérica, sem sessão; `is_active=False` no banco | AUTH-23 | ✅ |
| 10 | `USUARIO` com `is_staff` no admin | Índice sem o módulo de usuários; 403 em changelist, add, change e delete; POST forjado de promoção → 403 e perfil continua `USUARIO` no banco | AUTH-21, AUTH-22 | ✅ |

Limite: o botão "voltar" de um navegador gráfico não foi exercitado. O item 7 prova a invalidação da sessão no servidor, que é o que o recarregamento da página depende. Uma cópia em cache exibida pelo navegador sem nova requisição fica fora deste UAT.

Limpeza: o `uat_usuario` foi apagado depois do UAT. No banco local de desenvolvimento fica só o `admin` (`ADMINISTRADOR`).

---

## Code Quality

Escopo: arquivos alterados em `083ccb5..HEAD` (`contas/tests/test_admin_perfil.py`, `.specs/features/autenticacao/tasks.md`). Nenhum arquivo de produção mudou.

| Principle | Status |
| --------- | ------ |
| Minimum code | ✅ +1 item na lista e no dicionário, +1 teste de 5 linhas |
| Surgical changes | ✅ Só o arquivo de teste do admin e o `tasks.md`; nenhum teste existente enfraquecido |
| No scope creep | ✅ A tela de troca de senha de terceiro (opcional no Fix 1) não foi somada; aceitável, ela depende de `has_change_permission`, já discriminado |
| Matches patterns | ✅ Reusa fixtures e parametrização da T26; docstring cita AUTH-22; ruff limpo |
| Spec-anchored outcome check (asserted values match spec) | ✅ 403 e conta preservada é o resultado exato da AUTH-22 para quem não é `ADMINISTRADOR` |
| Per-layer Coverage Expectation met | ✅ Matriz do admin "perfil × operação" agora cobre exclusão para os dois perfis (`test_admin_perfil.py:74`, `:91`) |
| Every test maps to a spec requirement - no unclaimed tests | ✅ Os testes novos citam AUTH-22 |
| Documented guidelines followed: none - strong defaults applied (`tasks.md`, Test Coverage Matrix) | ✅ |

Observação: o parametrizado positivo (`test_admin_perfil.py:91`) faz GET na tela de confirmação de exclusão, não apaga. Não há teste de POST de exclusão aceito pelo ADMINISTRADOR; a spec não pede exclusão de contas, então não é gap.

---

## Edge Cases

- [x] AUTH-23 conta inativa: 200, mensagem genérica única, sem sessão (`test_views_login.py:59-61`), e o backend devolve `None` (`test_backends.py:56`).
- [x] AUTH-24 CSRF ausente: 403 e sem sessão (`test_views_login.py:68-69`).
- [x] AUTH-25 e-mail duplicado por caixa: `IntegrityError` e `ValidationError` com mensagem em português (`test_constraints.py:59-60`, `:78`).
- [x] AUTH-26 banco indisponível: 500, `500.html`, sem sessão, sem detalhes nem a senha submetida (`test_erro_500.py:41-43`, `:61-62`).
- [x] AUTH-27 log de tentativa malsucedida: identificador e horário, sem a senha (`test_signals.py:36-41`, `:50`).

---

## Gate Check

- **Gate command**: `ruff check . && ruff format --check . && python manage.py makemigrations --check --dry-run && pytest -q` (binários do `.venv` da raiz, worktree real, `-p no:cacheprovider`)
- **Result**: `ruff check`: All checks passed · `ruff format --check`: 48 files already formatted · `makemigrations --check`: No changes detected · `pytest -q`: 84 passed, 0 failed, 0 skipped (12.20 s), exit 0
- **Test count before feature**: 0
- **Test count after feature**: 84 (iteração 1: 66; iteração 2: 81)
- **Delta**: +84 no total; +3 nesta iteração (1 caso novo em cada parametrizado e 1 teste de POST). Nenhum teste removido nem enfraquecido
- **Skipped tests**: nenhum
- **Failures**: nenhuma

---

## Fix Plans

Nenhum fix obrigatório.

Observações sem fix:

- A3 e A4 são equivalentes enquanto `sites.py` e `UserAdmin._add_view` mascararem essas `has_*`. Não pedem teste.
- `tasks.md:13` ainda diz `Status: In Progress`, e o título da T31 (`tasks.md:1024`) não leva `✅`. Documentação, a cargo do orquestrador.
- AUTH-19, cláusula 2: se a spec quiser torná-la verificável, pode virar um teste de arquitetura (grep por `perfil ==` fora de `contas/models.py`). Decisão da spec, não do Verifier.

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
| AUTH-22 | Implementing | ✅ Verified |
| AUTH-23 | Implementing | ✅ Verified |
| AUTH-24 | Implementing | ✅ Verified |
| AUTH-25 | Implementing | ✅ Verified |
| AUTH-26 | Implementing | ✅ Verified |
| AUTH-27 | Implementing | ✅ Verified |
| AUTH-28 | — | ✅ Verified na validação da F2, iteração 3 (`cadastro-inovacao/validation.md`): `contas/tests/test_admin_perfil.py:132-134`. AC acrescentada em 2026-10-03, depois deste relatório |

---

## Histórico de iterações

| Iteração | Data | HEAD | Veredito | Gate | Sensor | Gaps |
| -------- | ---- | ---- | -------- | ---- | ------ | ---- |
| 1 | 2026-09-26 | - | Reprovada | 66 passed | 2 sobreviventes reais (M4, M6) | 6 fixes: AUTH-22 contrariada; AUTH-08, 18, 07/13/23 com evidência parcial; dummy hash sem teste (T26–T30) |
| 2 | 2026-09-26 | `4d84cdc` | Reprovada | 81 passed | 25/28; 1 sobrevivente real (A5), 2 equivalentes | 1 fix: tela de exclusão do admin sem teste (T31) |
| 3 | 2026-09-26 | `55a25bf` | Aprovada | 84 passed | 16/18; 0 sobreviventes reais, 2 equivalentes | nenhum; AUTH-19 segue como spec-precision gap |

---

## Summary

**Overall**: ✅ Ready - PASS (evidência: `contas/tests/test_admin_perfil.py:82-83`, `contas/tests/test_admin_perfil.py:74`)

**Spec-anchored check**: 26/27 ACs matched spec outcome · 1 spec-precision gap (AUTH-19, cláusula de processo)
**Sensor**: 16/18 mutations killed (0 sobreviventes reais; 2 equivalentes: A3, A4)
**Gate**: 84 passed, 0 failed

**What works**: login por username e por e-mail em qualquer caixa, mensagem única, rotação de sessão, hash na criação e na troca, nenhuma senha no log, no login falho, no admin nem na página 500, default-deny com `next`, logout com cookie zerado e sessão revogada, expiração em 8 h deslizantes, perfil com enum, default, constraint e validation error, `createsuperuser` como `ADMINISTRADOR`, e todas as telas de usuário do admin, incluindo a exclusão, fechadas para quem não é `ADMINISTRADOR`.

**Issues found**: nenhum bloqueante. Deriva cosmética no `tasks.md` (Fix Plans, observações).

**Next steps**: o orquestrador atualiza a rastreabilidade do `spec.md` e o status do `tasks.md`; UAT interativo opcional.
