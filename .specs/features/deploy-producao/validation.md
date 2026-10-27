# Deploy em Produção Validation

**Date**: 2026-10-27
**Iteration**: 2
**Spec**: `.specs/features/deploy-producao/spec.md`
**Diff range**: `894d31a..56e934c` em `main` (implementação: `f014e94`, `f272ad2`, `8046e7b`, `c701f35`, `088d7d7`; correção da iteração 2: `56e934c`). `c0e6457` só registra a validação da iteração 1.
**Verifier**: independent sub-agent (author ≠ verifier)

**Verdict**: PASS ✅

O único gap da iteração 1 foi fechado. O teste novo da DEPL-17
(`config/tests/test_documentacao_deploy.py:86-95`) exige o `DATABASE_URL` do Supabase em toda
linha que roda `python manage.py migrate` ou `createsuperuser`. M13 morre agora, e as três
variantes novas também (M13b, M18, M19), além do corte de seção (M20). O gate passa com 904/904.
No total, o sensor matou 21 de 21 mutantes nas duas iterações. As 17 ACs batem com o resultado
da spec.

---

## Iteração 1 → 2

| Gap da iteração 1 | Commit | Status agora | Evidência |
| ----------------- | ------ | ------------ | --------- |
| Fix 1: DEPL-17 sem asserção de "contra o Supabase" (M13 sobreviveu) | `56e934c` | ✅ Fechado. M13 morto (2 testes falham) | `config/tests/test_documentacao_deploy.py:91-95` - `assert linhas` e `all(re.search(r"DATABASE_URL='postgresql://[^']*supabase\.com[^']*'", linha) ...)` |

**O teste novo depende de algo acidental?** Não, com duas ressalvas de formato.

- Ele filtra linhas por `python manage.py <comando>`. A frase em prosa de `README.md:55`
  ("repita o `manage.py migrate`") fica fora do filtro, porque não tem `python ` antes. Por isso
  o `all(...)` não reprova a prosa, e o `assert linhas` impede que o filtro fique vazio e passe à
  toa.
- A regex exige a URL na mesma linha, entre aspas simples, com host `supabase.com`. Um host local
  reprova (M18). Ressalva: um README correto escrito com `export DATABASE_URL=...` numa linha
  separada, ou com aspas duplas, também reprovaria. Isso é falso negativo de formato, não de
  comportamento; aceito, porque o README atual usa o formato inline.
- Ressalva: uma linha extra `python3 manage.py migrate` sem a URL escaparia do filtro. É um
  cenário artificial; não vira gap.

---

## Task Completion

Plano inline, sem `tasks.md` (spec: "17 mapeadas aos 5 passos do Execute").

| Passo | Commit | Status | Notes |
| ----- | ------ | ------ | ----- |
| 1. Ambiente e CSRF | `f014e94` | ✅ Done | DEPL-01 a DEPL-05 |
| 2. Banco pela `DATABASE_URL` | `f272ad2` | ✅ Done | DEPL-06 a DEPL-09, DEPL-15 |
| 3. `STATIC_ROOT` | `8046e7b` | ✅ Done | DEPL-10, DEPL-11 |
| 4. Runtime da Vercel | `c701f35` | ✅ Done | DEPL-12 a DEPL-14 |
| 5. Documentação | `088d7d7`, `56e934c` | ✅ Done | DEPL-16, DEPL-17 (teste reforçado na iteração 2) |

---

## Isolamento dos testes de settings

`config/tests/settings_isolados.py:19-23` roda `config/settings.py` por `runpy.run_path` com
`mock.patch.dict(os.environ, ambiente, clear=True)` e `dotenv.load_dotenv` trocado por no-op.
O settings faz `from dotenv import load_dotenv` em `config/settings.py:17`; como o `run_path`
reexecuta o import a cada chamada, ele pega o atributo já trocado. Prova empírica: o `.env` local
define `DJANGO_SECRET_KEY`, e o teste da DEPL-01 (`test_settings_ambiente.py:14`) passa com
`KeyError`. Logo o `.env` não vazou. O `run_path` não toca em `django.conf.settings`, e o
`patch.dict` restaura o ambiente. Isolamento correto.

---

## Spec-Anchored Acceptance Criteria

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| DEPL-01 | Sem `DJANGO_SECRET_KEY`, `KeyError` com o nome | `config/tests/test_settings_ambiente.py:14` - `pytest.raises(KeyError, match="DJANGO_SECRET_KEY")`; `:20` - `["SECRET_KEY"] == "chave-de-teste"` | ✅ PASS |
| DEPL-02 | Ausente, `true`, `1`, vazio → `DEBUG = False` | `config/tests/test_settings_ambiente.py:23,27` - parametrize `[None, "true", "1", ""]`, `["DEBUG"] is False`; `:32` - `"True"` → `is True` | ✅ PASS |
| DEPL-03 | `"kira.vercel.app, localhost,"` → `["kira.vercel.app", "localhost"]` | `config/tests/test_settings_ambiente.py:38` - `settings["ALLOWED_HOSTS"] == ["kira.vercel.app", "localhost"]` | ✅ PASS |
| DEPL-04 | Lista exata com as duas origens; sem a variável, `[]` | `config/tests/test_settings_ambiente.py:47-50` - `== ["https://kira.vercel.app", "https://kira-git-main.vercel.app"]`; `:55` - `== []` | ✅ PASS |
| DEPL-05 | POST com token válido, `DEBUG=False`, Host/Origin da Vercel por HTTP → não 403 | `config/tests/test_csrf_proxy.py:33-40` - `override_settings(DEBUG=False, CSRF_TRUSTED_ORIGINS=["https://kira.vercel.app"])`, `Client(enforce_csrf_checks=True)`, `status_code != 403` e `== 302` | ✅ PASS |
| DEPL-06 | ENGINE, NAME `postgres`, USER `postgres.abcd`, PASSWORD `s@nha`, HOST do pooler, PORT `6543` | `config/tests/test_settings_banco.py:29-34` - um `assert ==` por campo; `str(banco["PORT"]) == "6543"` | ✅ PASS |
| DEPL-07 | `OPTIONS["sslmode"] == "require"`, inclusive com `sslmode=disable` | `config/tests/test_settings_banco.py:39` e `:45` - `["OPTIONS"]["sslmode"] == "require"` | ✅ PASS |
| DEPL-08 | `DISABLE_SERVER_SIDE_CURSORS is True`, `CONN_MAX_AGE == 0` | `config/tests/test_settings_banco.py:51-52` | ✅ PASS |
| DEPL-09 | `POSTGRES_*` com PORT `5433`, sem `sslmode`, sem cursores desligados | `config/tests/test_settings_banco.py:55-66` - parametrize sem e com `DATABASE_URL=""`; `PORT == "5433"`, `"sslmode" not in OPTIONS`, `DISABLE_SERVER_SIDE_CURSORS is not True` | ✅ PASS |
| DEPL-10 | `STATIC_ROOT == BASE_DIR / "staticfiles"`; `.gitignore` com `staticfiles/` | `config/tests/test_estaticos.py:17` - `Path(settings.STATIC_ROOT) == RAIZ / "staticfiles"`; `:23` - `"staticfiles/" in [...]` | ✅ PASS |
| DEPL-11 | `collectstatic --noinput` grava `admin/css/base.css` sob `STATIC_ROOT` | `config/tests/test_estaticos.py:28-30` - `override_settings(STATIC_ROOT=tmp_path)`, `(tmp_path / "admin" / "css" / "base.css").is_file()` | ✅ PASS (ver nota) |
| DEPL-12 | `.python-version` stripped == `3.13` | `config/tests/test_vercel.py:29` | ✅ PASS |
| DEPL-13 | `WSGI_APPLICATION == "config.wsgi.application"`; `application` chamável | `config/tests/test_vercel.py:34-35` | ✅ PASS |
| DEPL-14 | `vercel.json` válido; exclui os 3 caminhos; mantém `inovacoes/views.py` e `templates/kira.css` | `config/tests/test_vercel.py:40-41` - `json.loads`, chave `functions["config/wsgi.py"]["excludeFiles"]`; `:49` - `assert _casa(...)`; `:55` - `assert not _casa(...)` | ✅ PASS (ver nota) |
| DEPL-15 | `dj-database-url` antes de `# Desenvolvimento e testes` | `config/tests/test_settings_banco.py:72-74` - `"dj-database-url" in runtime` | ✅ PASS |
| DEPL-16 | Todo nome lido por `config/settings.py` está no `.env.example`, inclusive os dois novos | `config/tests/test_documentacao_deploy.py:65-66` - `{"DJANGO_CSRF_TRUSTED_ORIGINS", "DATABASE_URL"} <= lidos` e `lidos <= chaves` (nomes lidos rastreados nos dois ramos do banco, `:41`) | ✅ PASS |
| DEPL-17 | Seção de deploy nomeia as 5 variáveis e os comandos `migrate` e `createsuperuser` **contra o Supabase** | `config/tests/test_documentacao_deploy.py:69-83` - `termo in _secao_de_deploy()`; `:86-95` - `assert linhas` e `all(re.search(r"DATABASE_URL='postgresql://[^']*supabase\.com[^']*'", linha) ...)` | ✅ PASS (iteração 1: ❌ GAP, M13 sobreviveu) |

**Notas de julgamento:**

- **DEPL-05 e `override_settings`.** O teste fixa `CSRF_TRUSTED_ORIGINS` por override, então não
  prova sozinho que o settings lê a variável. Esse elo é da DEPL-04 (o mutante M2, que apaga a
  linha do settings, morre lá). A DEPL-05 prova o outro elo: com a origem na lista, o Django aceita
  `Origin: https://...` numa requisição HTTP. O caso negativo (`test_csrf_proxy.py:46-48`, origem
  `https://outro.vercel.app` → 403) mostra que o 302 não vem por acidente. Juntas, cobrem a cadeia.
  A spec prescreve esse desenho ("Independent Test").
- **DEPL-11 e `collectstatic` do Django.** Com `override_settings(STATIC_ROOT=tmp_path)`, o teste
  passaria também antes da feature. Ele prova que o projeto tem o que coletar (admin e
  `staticfiles` instalados), não o valor do `STATIC_ROOT`. O valor é da DEPL-10 (M7 morre lá).
  Desenho prescrito pela spec; aceito.
- **DEPL-14 e o glob.** `_casa` (`test_vercel.py:17-24`) emula o glob da Vercel com
  `glob.translate`. É uma aproximação: o casamento real só o build mostra. Risco residual coberto
  pelo passo 4 do roteiro de UAT.
- **DEPL-16 e a linha comentada.** `DATABASE_URL` aparece comentada no `.env.example:17`, e o
  regex (`test_documentacao_deploy.py:63`) aceita `#`. Leitura razoável de "list": deixá-la ativa
  ligaria o modo produção no desenvolvimento local.

**Status**: ✅ 17/17 ACs com o resultado da spec afirmado (iteração 1: 16/17).

---

## Discrimination Sensor

Worktree temporário em HEAD no scratchpad, interpretador do `.venv` do repositório, ambiente
passado na linha de comando (sem `.env`). Confirmado que o `config.settings` importado era o do
worktree. Cada mutante rodou `config/tests` (37 testes) e foi revertido com `git checkout`.

| Mutation | File:line | Description | Killed? |
| -------- | --------- | ----------- | ------- |
| M1 | `config/settings.py:37` | `item.strip()` → `item` (mantém o filtro de vazios) | ✅ Killed (2) |
| M2 | `config/settings.py:43` | Remove `CSRF_TRUSTED_ORIGINS` | ✅ Killed (3) |
| M3 | `config/settings.py:103` | `ssl_require=False` | ✅ Killed (2) |
| M4 | `config/settings.py:104` | `disable_server_side_cursors=False` | ✅ Killed (1) |
| M5 | `config/settings.py:101` | `conn_max_age=600` | ✅ Killed (1) |
| M6 | `config/settings.py:96` | `if "DATABASE_URL" in os.environ` (vazia conta como definida) | ✅ Killed (1) |
| M7 | `config/settings.py:157` | `STATIC_ROOT = BASE_DIR / "static"` | ✅ Killed (1) |
| M8 | `.python-version:1` | `3.12` | ✅ Killed (1) |
| M9 | `vercel.json:5` | Acrescenta `templates/**` à exclusão | ✅ Killed (1) |
| M10 | `vercel.json:5` | Tira `.specs/**` da exclusão | ✅ Killed (1) |
| M11 | `.env.example:6` | Remove `DJANGO_CSRF_TRUSTED_ORIGINS=` | ✅ Killed (1) |
| M12 | `README.md:44` | Remove a linha do `createsuperuser` | ✅ Killed (1) |
| M13 | `README.md:43-44` | Tira o `DATABASE_URL='...'` dos comandos `migrate` e `createsuperuser` (rodariam no banco local) | Iteração 1: ❌ Survived → Fix 1. Iteração 2: ✅ Killed (2) |
| M14 | `config/settings.py:32` | `DEBUG` aceita `true`/`1` | ✅ Killed (2) |
| M15 | `requirements.txt:5` | Move `dj-database-url` para a seção de desenvolvimento | ✅ Killed (1) |
| M16 | `config/settings.py:115` | `PORT` local fixo em `5432` | ✅ Killed (2) |
| M17 | `vercel.json:4` | Chave da função `api/index.py` em vez de `config/wsgi.py` | ✅ Killed (5 erros) |

**Mutações novas da iteração 2** (worktree novo em `56e934c`, mesmo processo; baseline com 39/39
verdes antes de mutar):

| Mutation | File:line | Description | Killed? |
| -------- | --------- | ----------- | ------- |
| M13b | `README.md:44` | Tira o `DATABASE_URL='...'` só do `createsuperuser` | ✅ Killed (1) |
| M18 | `README.md:43` | `migrate` com `DATABASE_URL` apontando para `localhost:5433` | ✅ Killed (1) |
| M19 | `config/settings.py:43` | `CSRF_TRUSTED_ORIGINS` sem o helper, sem descartar item vazio | ✅ Killed (1) |
| M20 | `README.md:3` | Comandos movidos para outra seção `##`, fora da de deploy | ✅ Killed (9) |

**Sensor depth**: expandido (≥5; configuração de produção)
**Result**: iteração 1: 16/17; iteração 2: M13 + 4 novos, 5/5. Total 21/21 killed - PASS ✅
**Isolamento**: nas duas iterações, `git worktree remove --force` + `git worktree prune`;
`git status --porcelain` do repositório real igual ao baseline (vazio) antes e depois.

---

## Code Quality

| Principle | Status |
| --------- | ------ |
| Minimum code | ✅ Um helper `_lista_do_ambiente` usado duas vezes; um `if` para o banco |
| Surgical changes | ✅ Só os arquivos da spec; `SECRET_KEY`, `DEBUG`, cookies e WSGI intocados |
| No scope creep | ✅ Sem WhiteNoise, sem HSTS/SSL redirect, sem CI (Out of Scope respeitado) |
| Matches patterns | ✅ Mesmo formato de lista do `ALLOWED_HOSTS`; marcador `unit` nos testes sem banco |
| Spec-anchored outcome check | ✅ 17/17 (DEPL-17 corrigida em `56e934c`) |
| Per-layer Coverage Expectation | ✅ Settings 1:1 com as ACs; rota de login com caso feliz e de erro (403) |
| Every test maps to a spec requirement | ✅ Todo teste em `config/tests` cita uma DEPL-xx |
| Documented guidelines followed | ✅ Sem guia de testes do projeto; padrões da skill e o marcador `unit` do `pyproject.toml` |

---

## Edge Cases

- [x] `DATABASE_URL=""` usa o ramo `POSTGRES_*`: `config/tests/test_settings_banco.py:55` (parametrize com `"DATABASE_URL": ""`); M6 morre.
- [x] `sslmode=disable` na query não vence: `config/tests/test_settings_banco.py:44-45`.
- [x] Origem fora da lista recebe 403: `config/tests/test_csrf_proxy.py:46-48`.
- [x] Espaços e vírgula final descartados: `config/tests/test_settings_ambiente.py:38` e `:45-50`; M1 morre. O caso de vírgula final só é exercitado em `ALLOWED_HOSTS`; como as duas listas usam o mesmo helper (`config/settings.py:40,43`), aceito.

---

## Gate Check

- **Gate command**: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q`
- **Result**: ruff ok, format ok (142 arquivos), sem migrations pendentes; 904 passed, 0 failed, 0 skipped (iteração 1: 902)
- **Test count before feature**: 865
- **Test count after feature**: 904
- **Delta**: +39 testes novos, todos em `config/tests` (37 na iteração 1, mais 2 do parametrize do Fix 1)
- **Skipped tests**: nenhum
- **Failures**: nenhuma

---

## Fix Plans

### Fix 1: DEPL-17 não afirma que os comandos rodam contra o Supabase - ✅ Fechado em `56e934c`

- **Root cause (iteração 1)**: `config/tests/test_documentacao_deploy.py:83` só conferia
  `termo in secao`. O `DATABASE_URL` já aparece na tabela de variáveis, então tirá-lo dos comandos
  (M13) não quebrava nada.
- **Correção**: `test_readme_roda_os_comandos_contra_o_supabase`
  (`config/tests/test_documentacao_deploy.py:86-95`). README e produção não mudaram.
- **Verificado**: M13, M13b e M18 morrem; gate de build verde (904).

Nenhum fix novo nesta iteração.

---

## Requirement Traceability Update

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| DEPL-01 a DEPL-17 | Implementing | ✅ Verified |

A DEPL-17 estava como ❌ Needs Fix na iteração 1.

---

## Summary

**Overall**: ✅ Ready (falta só o UAT manual na nuvem)

**Spec-anchored check**: 17/17 ACs com o resultado da spec afirmado
**Sensor**: 21/21 mutações mortas (iteração 1: 16/17; iteração 2: 5/5)
**Gate**: 904 passed

**What works**: settings lidas do ambiente com limpeza de listas; CSRF atrás do proxy; banco do
pooler com SSL forçado, sem cursores do servidor e sem conexão persistente; ramo local intacto;
`STATIC_ROOT`; `.python-version`; `vercel.json`; `.env.example` completo; README com os comandos
apontados para o Supabase.

**Issues found**: nenhum aberto. Riscos residuais registrados, sem bloquear: o glob da DEPL-14 é
emulado (o build da Vercel confirma); o teste da DEPL-17 depende do formato inline com aspas
simples.

**Next steps**: atualizar a rastreabilidade da spec para Verified e rodar o roteiro de UAT manual na
nuvem, com go-ahead do usuário para cada operação remota.
