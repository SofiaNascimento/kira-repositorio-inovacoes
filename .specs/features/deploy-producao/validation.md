# Deploy em Produção Validation

**Date**: 2026-10-27
**Iteration**: 1
**Spec**: `.specs/features/deploy-producao/spec.md`
**Diff range**: `894d31a..088d7d7` em `main` (implementação: `f014e94`, `f272ad2`, `8046e7b`, `c701f35`, `088d7d7`)
**Verifier**: independent sub-agent (author ≠ verifier)

**Verdict**: FAIL ❌

O código de produção está correto e as 17 ACs têm evidência. O gate passa com 902/902. O sensor
matou 16 de 17 mutantes. Um sobreviveu (M13): o README pode perder o `DATABASE_URL=...` dos
comandos `migrate` e `createsuperuser`, e o teste da DEPL-17 continua verde. A DEPL-17 pede os
comandos "run against the Supabase database"; o teste só confere que os nomes aparecem na seção.
Gap menor, P2, uma linha de correção no teste.

---

## Task Completion

Plano inline, sem `tasks.md` (spec: "17 mapeadas aos 5 passos do Execute").

| Passo | Commit | Status | Notes |
| ----- | ------ | ------ | ----- |
| 1. Ambiente e CSRF | `f014e94` | ✅ Done | DEPL-01 a DEPL-05 |
| 2. Banco pela `DATABASE_URL` | `f272ad2` | ✅ Done | DEPL-06 a DEPL-09, DEPL-15 |
| 3. `STATIC_ROOT` | `8046e7b` | ✅ Done | DEPL-10, DEPL-11 |
| 4. Runtime da Vercel | `c701f35` | ✅ Done | DEPL-12 a DEPL-14 |
| 5. Documentação | `088d7d7` | ⚠️ Partial | DEPL-16 ok; DEPL-17 com teste não discriminante (M13) |

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
| DEPL-17 | Seção de deploy nomeia as 5 variáveis e os comandos `migrate` e `createsuperuser` **contra o Supabase** | `config/tests/test_documentacao_deploy.py:69-83` - `termo in _secao_de_deploy()` | ❌ GAP: a cláusula "run against the Supabase database" não é afirmada (M13 sobreviveu) |

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

**Status**: ❌ 16/17 ACs com o resultado da spec afirmado; DEPL-17 parcial.

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
| M13 | `README.md:43-44` | Tira o `DATABASE_URL='...'` dos comandos `migrate` e `createsuperuser` (rodariam no banco local) | ❌ Survived → Fix 1 |
| M14 | `config/settings.py:32` | `DEBUG` aceita `true`/`1` | ✅ Killed (2) |
| M15 | `requirements.txt:5` | Move `dj-database-url` para a seção de desenvolvimento | ✅ Killed (1) |
| M16 | `config/settings.py:115` | `PORT` local fixo em `5432` | ✅ Killed (2) |
| M17 | `vercel.json:4` | Chave da função `api/index.py` em vez de `config/wsgi.py` | ✅ Killed (5 erros) |

**Sensor depth**: expandido (≥5; configuração de produção)
**Result**: 16/17 killed - FAIL ❌
**Isolamento**: `git worktree remove --force` + `git worktree prune`; `git status --porcelain` do
repositório real igual ao baseline (vazio) antes e depois.

---

## Code Quality

| Principle | Status |
| --------- | ------ |
| Minimum code | ✅ Um helper `_lista_do_ambiente` usado duas vezes; um `if` para o banco |
| Surgical changes | ✅ Só os arquivos da spec; `SECRET_KEY`, `DEBUG`, cookies e WSGI intocados |
| No scope creep | ✅ Sem WhiteNoise, sem HSTS/SSL redirect, sem CI (Out of Scope respeitado) |
| Matches patterns | ✅ Mesmo formato de lista do `ALLOWED_HOSTS`; marcador `unit` nos testes sem banco |
| Spec-anchored outcome check | ❌ DEPL-17: cláusula "contra o Supabase" sem asserção |
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
- **Result**: ruff ok, format ok (141 arquivos), sem migrations pendentes; 902 passed, 0 failed, 0 skipped
- **Test count before feature**: 865
- **Test count after feature**: 902
- **Delta**: +37 testes novos (todos em `config/tests`)
- **Skipped tests**: nenhum
- **Failures**: nenhuma

---

## Fix Plans

### Fix 1: DEPL-17 não afirma que os comandos rodam contra o Supabase

- **Root cause**: `config/tests/test_documentacao_deploy.py:83` só confere `termo in secao`. O
  `DATABASE_URL` já aparece na tabela de variáveis, então tirá-lo dos comandos (M13) não quebra
  nada, e o README passaria a mandar migrar o banco local.
- **Fix task**: em `config/tests/test_documentacao_deploy.py`, para `migrate` e `createsuperuser`,
  exigir pelo menos uma linha da seção de deploy que contenha `manage.py <comando>` **e**
  `DATABASE_URL=` na mesma linha. Não mudar o README (ele já está certo).
- **Verify**: aplicar M13 (tirar `DATABASE_URL='...' ` das linhas 43-44 do `README.md`) num
  scratch: o teste novo falha. No README real, passa.
- **Done when**: M13 morto; gate de build verde.
- **Priority**: Minor

---

## Requirement Traceability Update

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| DEPL-01 a DEPL-16 | Implementing | ✅ Verified |
| DEPL-17 | Implementing | ❌ Needs Fix (Fix 1) |

---

## Summary

**Overall**: ⚠️ Issues (FAIL por um mutante sobrevivente em P2)

**Spec-anchored check**: 16/17 ACs com o resultado da spec afirmado; DEPL-17 parcial
**Sensor**: 16/17 mutações mortas
**Gate**: 902 passed

**What works**: settings lidas do ambiente com limpeza de listas; CSRF atrás do proxy; banco do
pooler com SSL forçado, sem cursores do servidor e sem conexão persistente; ramo local intacto;
`STATIC_ROOT`; `.python-version`; `vercel.json`; `.env.example` completo.

**Issues found**: Fix 1 (teste da DEPL-17).

**Next steps**: implementar o Fix 1 e redespachar o Verifier (iteração 2 de 3). Depois, o roteiro
de UAT manual na nuvem, com go-ahead do usuário.
