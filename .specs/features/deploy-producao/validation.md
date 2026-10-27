# Deploy em Produção Validation

**Date**: 2026-10-27
**Iteration**: 3 (emenda da spec: DEPL-18 e DEPL-19)
**Spec**: `.specs/features/deploy-producao/spec.md`
**Diff range**: `894d31a..c1cbc63` em `main`. Iterações 1 e 2: `894d31a..56e934c`. Emenda: `bc2997f..c1cbc63` (`29195da` spec e context, `6645eef` `.vercelignore` + `.gitignore` + teste, `c1cbc63` README e `docs/roteiro-deploy.md`). `c0e6457` e `bc2997f` só registram validações.
**Verifier**: independent sub-agent (author ≠ verifier)

**Verdict**: FAIL ❌ na iteração 3 (HEAD `c1cbc63`), **com risco residual de teste aceito pelo usuário em 2026-10-27**: ver [Decisão do usuário](#decisão-do-usuário-2026-10-27). O veredito do Verifier não foi reescrito; a feature foi fechada por decisão, não por PASS.

A emenda está correta no que entrega. O `.vercelignore` barra o `.env` e mantém o que a Vercel
precisa, e o `.gitignore` ignora `.vercel/`. As 19 ACs têm evidência. O gate passa com 919/919. No
ambiente desta máquina, o sensor matou 11 de 11 mutantes novos. O problema está no teste da
DEPL-18: ele não é hermético em relação à configuração global do git. O `git check-ignore` do
repositório temporário herda o `core.excludesFile` do usuário. Com um `.env` no ignore global,
coisa comum, o mutante N1 (tirar `.env` do `.vercelignore`) sobrevive (probe P1). Gap de teste
Minor, sem defeito de produção, correção de uma linha.

---

## Iteração 2 → 3 (emenda)

| Item | Commit | Status | Evidência |
| ---- | ------ | ------ | --------- |
| DEPL-18 `.vercelignore` | `6645eef` | ✅ Conteúdo certo; ⚠️ teste depende do git global (Fix 2) | `.vercelignore:3-13`; `config/tests/test_vercelignore.py:19-31,35-63` |
| DEPL-19 `.vercel/` no `.gitignore` | `6645eef` | ✅ | `.gitignore:227`; `config/tests/test_vercelignore.py:66-70` |
| Regressão DEPL-17 (README editado) | `c1cbc63` | ✅ Comandos de `README.md:43-44` intactos; N11 morre (2) | `config/tests/test_documentacao_deploy.py:86-95` |
| Produção (DEPL-01..16) | - | ✅ `git diff bc2997f..c1cbc63` não toca `config/settings.py`, `requirements.txt`, `vercel.json`, `.python-version` nem `.env.example` | gate 919 |

**A emulação por `git check-ignore --no-index` é sólida?** Em parte.

- A ideia é boa. A spec registra que a Vercel descreve o `.vercelignore` como "similar a um
  `.gitignore`". Copiar o arquivo para o `.gitignore` de um repositório vazio isola o
  `.gitignore` do projeto, que já ignora o `.env`. O `--no-index` dispensa arquivos reais. O
  `returncode in (0, 1)` (`test_vercelignore.py:30`) impede que um erro do git (128) conte como
  "não ignorado".
- Furo: o subprocess herda `~/.gitconfig` e o `core.excludesFile`. Probe P1: com
  `GIT_CONFIG_GLOBAL` apontando para um `excludesFile` que contém `.env`, o mutante N1 passa (15/15
  verdes). Nesta máquina o ignore global só tem `**/.claude/settings.local.json`, então o sensor
  normal discrimina. Mas o resultado do teste depende de quem roda. Isso é exatamente o "passar por
  motivo acidental" que o docstring diz evitar.
- Risco residual, fora do alcance de teste offline: a semântica real do `.vercelignore` na CLI
  (por exemplo, se os ignores padrão da CLI continuam valendo). Coberto pelo passo 4 do UAT (aba
  Source sem `.env`).

**Observações sem gap:**
- `.env.*` (`.vercelignore:4`) também barra o `.env.example` no upload. É inofensivo, porque o
  runtime não lê o arquivo.
- `README.md:55-56`: o parágrafo "O roteiro detalhado..." entra entre os itens 4 e 5 e quebra a
  lista numerada (o item 5 vira uma lista nova). Cosmético; não toca a DEPL-17.
- `docs/roteiro-deploy.md` (338 linhas) é só documentação, sem AC própria. Não auditei o
  conteúdo linha a linha.

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
| 5. Documentação | `088d7d7`, `56e934c`, `c1cbc63` | ✅ Done | DEPL-16, DEPL-17 (teste reforçado na iteração 2; README trocado para a CLI na emenda) |
| 6. Deploy pela CLI (emenda) | `6645eef` | ⚠️ Partial | DEPL-18 com teste não hermético (Fix 2); DEPL-19 ok |

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

| DEPL-18 | `.vercelignore`, com semântica de `.gitignore`, ignora `.env`, `.env.producao`, `.specs/STATE.md`, `.claude/skills/x.md`, `.agents/x.json`, `docs/requisitos.md`; não ignora `manage.py`, `config/settings.py`, `config/wsgi.py`, `inovacoes/views.py`, `templates/kira.css`, `requirements.txt`, `.python-version`, `vercel.json` | `config/tests/test_vercelignore.py:35-47` - parametrize com os 6 caminhos, `assert _ignorado(...)`; `:50-63` - os 8 caminhos, `assert not _ignorado(...)`; `_ignorado` em `:26-31` (`git check-ignore --no-index -q`) | ⚠️ Valores certos; ❌ GAP de hermeticidade: o teste herda o `core.excludesFile` global (probe P1) |
| DEPL-19 | `.gitignore` ignora `.vercel/` | `config/tests/test_vercelignore.py:68-70` - `".vercel/" in [linha.strip() for linha in linhas]` | ✅ PASS |

**Status**: ❌ 18/19 ACs com o resultado da spec afirmado de forma confiável; DEPL-18 depende do git global (iteração 2: 17/17; iteração 1: 16/17).

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

**Mutações da iteração 3** (worktree novo em `c1cbc63`, 54/54 verdes antes de mutar):

| Mutation | File:line | Description | Killed? |
| -------- | --------- | ----------- | ------- |
| N1 | `.vercelignore:3` | Remove `.env` | ✅ Killed (1) |
| N2 | `.vercelignore:3` | `.env` → `.env.local` | ✅ Killed (1) |
| N3 | `.vercelignore:4` | Remove `.env.*` | ✅ Killed (1) |
| N4 | `.vercelignore` | Acrescenta `templates/` | ✅ Killed (1) |
| N5 | `.vercelignore` | Acrescenta `config/` | ✅ Killed (2) |
| N6 | `.vercelignore:10` | `docs/` → `doc/` | ✅ Killed (1) |
| N7 | `.gitignore:227` | Remove `.vercel/` | ✅ Killed (1) |
| N8 | `.vercelignore` | Acrescenta `*.py` | ✅ Killed (4) |
| N9 | `.vercelignore` | Acrescenta `.*` (barra todo dotfile, inclusive `.python-version`) | ✅ Killed (1) |
| N10 | `.vercelignore:8` | Remove `.claude/` | ✅ Killed (1) |
| N11 | `README.md:43-44` | Regressão DEPL-17: tira o `DATABASE_URL='...'` dos comandos | ✅ Killed (2) |
| P1 (probe) | `.vercelignore:3` + ambiente | N1 rodado com `GIT_CONFIG_GLOBAL` apontando para um `core.excludesFile` que contém `.env` | ❌ Survived (15/15 verdes) → Fix 2 |

**Sensor depth**: expandido (≥5; configuração de produção)
**Result**: iteração 1: 16/17; iteração 2: 5/5; iteração 3: 11/11 no ambiente local, mas o probe P1 sobrevive sob uma configuração global de git comum - FAIL ❌
**Isolamento**: nas três iterações, `git worktree remove --force` + `git worktree prune`;
`git status --porcelain` do repositório real igual ao baseline (vazio) antes e depois. O probe P1
usou um `GIT_CONFIG_GLOBAL` temporário no scratchpad; o `~/.gitconfig` real não foi tocado.

---

## Code Quality

| Principle | Status |
| --------- | ------ |
| Minimum code | ✅ Um helper `_lista_do_ambiente` usado duas vezes; um `if` para o banco |
| Surgical changes | ✅ Só os arquivos da spec; `SECRET_KEY`, `DEBUG`, cookies e WSGI intocados |
| No scope creep | ✅ Sem WhiteNoise, sem HSTS/SSL redirect, sem CI (Out of Scope respeitado) |
| Matches patterns | ✅ Mesmo formato de lista do `ALLOWED_HOSTS`; marcador `unit` nos testes sem banco |
| Spec-anchored outcome check | ❌ 18/19: DEPL-18 com teste não hermético (Fix 2); DEPL-17 corrigida em `56e934c` |
| Per-layer Coverage Expectation | ✅ Settings 1:1 com as ACs; rota de login com caso feliz e de erro (403) |
| Every test maps to a spec requirement | ✅ Todo teste em `config/tests` cita uma DEPL-xx |
| Documented guidelines followed | ✅ Sem guia de testes do projeto; padrões da skill e o marcador `unit` do `pyproject.toml` |

---

## Edge Cases

- [x] `DATABASE_URL=""` usa o ramo `POSTGRES_*`: `config/tests/test_settings_banco.py:55` (parametrize com `"DATABASE_URL": ""`); M6 morre.
- [x] `sslmode=disable` na query não vence: `config/tests/test_settings_banco.py:44-45`.
- [x] Origem fora da lista recebe 403: `config/tests/test_csrf_proxy.py:46-48`.
- [x] (emenda) `.env.producao` barrado pelo `.env.*`: `config/tests/test_vercelignore.py:38`; N3 morre.
- [x] Espaços e vírgula final descartados: `config/tests/test_settings_ambiente.py:38` e `:45-50`; M1 morre. O caso de vírgula final só é exercitado em `ALLOWED_HOSTS`; como as duas listas usam o mesmo helper (`config/settings.py:40,43`), aceito.

---

## Gate Check

- **Gate command**: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q`
- **Result**: ruff ok, format ok (144 arquivos), sem migrations pendentes; 919 passed, 0 failed, 0 skipped (iteração 2: 904; iteração 1: 902)
- **Test count before feature**: 865
- **Test count after feature**: 919
- **Delta**: +54 testes novos, todos em `config/tests` (37 na iteração 1, +2 no Fix 1, +15 em `test_vercelignore.py` na emenda)
- **Skipped tests**: nenhum
- **Failures**: nenhuma

---

## Fix Plans

### Fix 1: DEPL-17 não afirma que os comandos rodam contra o Supabase - ✅ Fechado em `56e934c`

- **Root cause (iteração 1)**: `config/tests/test_documentacao_deploy.py:83` só conferia
  `termo in secao`; tirar o `DATABASE_URL` dos comandos (M13) não quebrava nada.
- **Correção**: `test_readme_roda_os_comandos_contra_o_supabase`
  (`config/tests/test_documentacao_deploy.py:86-95`).
- **Verificado**: M13, M13b, M18 (iteração 2) e N11 (iteração 3) morrem.

### Fix 2: teste da DEPL-18 herda a configuração global do git (iteração 3)

- **Root cause**: `config/tests/test_vercelignore.py:21` e `:27-29` rodam `git` sem isolar a
  configuração do usuário. O `core.excludesFile` global entra na resposta do `check-ignore`. Com
  `.env` no ignore global, tirar `.env` do `.vercelignore` não quebra o teste (probe P1).
- **Fix task**: nos dois `subprocess.run` de `config/tests/test_vercelignore.py`, passar um
  ambiente com `GIT_CONFIG_GLOBAL=os.devnull` e `GIT_CONFIG_NOSYSTEM=1`. Alternativa: passar
  `-c core.excludesFile=` ao `check-ignore`. Não mudar o `.vercelignore`.
- **Verify**: refazer P1 num scratch (`GIT_CONFIG_GLOBAL` com `.env` no `excludesFile` e N1
  aplicado): o teste falha. Sem mutação, 15/15 verdes.
- **Done when**: P1 morto; gate de build verde.
- **Priority**: Minor (sem defeito de produção; o `.vercelignore` real está correto)

---

## Requirement Traceability Update

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| DEPL-01 a DEPL-17 | Verified | ✅ Verified (sem regressão) |
| DEPL-18 | Implementing | ❌ Needs Fix (Fix 2, só o teste) |
| DEPL-19 | Implementing | ✅ Verified |

---

## Summary

**Overall**: ⚠️ Issues (FAIL por um teste não hermético na DEPL-18; produção correta)

**Spec-anchored check**: 18/19 ACs confiáveis; DEPL-18 com valores certos, mas o teste depende do git global
**Sensor**: iteração 3: 11/11 mortos no ambiente local; probe P1 sobrevive (total histórico 32/33)
**Gate**: 919 passed

**What works**: tudo das iterações 1 e 2, sem regressão; `.vercelignore` barra `.env`, `.env.*`,
`.specs/`, `.claude/`, `.agents/` e `docs/`, e mantém código, templates e arquivos de build;
`.vercel/` fora do git; README da CLI com os comandos ainda apontados para o Supabase.

**Issues found**: Fix 2 (hermeticidade do teste da DEPL-18). Cosmético: lista numerada quebrada
em `README.md:55-56`.

**Next steps**: aplicar o Fix 2 e reverificar. Se o loop de correções estiver esgotado, fechar com o
risco registrado (o `.vercelignore` real está certo). Depois, o UAT na nuvem, com o passo 4
conferindo a ausência do `.env` na aba Source.

---

## Decisão do usuário (2026-10-27)

Registrada pelo orquestrador depois da escalada (limite de 3 iterações atingido). Não é uma
iteração do Verifier.

- **Fix 2 aplicado depois da iteração 3**, sem reverificação independente: `04b8a35` passa
  `GIT_CONFIG_GLOBAL=os.devnull`, `GIT_CONFIG_NOSYSTEM=1` e `XDG_CONFIG_HOME=os.devnull` ao `git
  init` e ao `git check-ignore` (`config/tests/test_vercelignore.py:18-27`).
- **Conferência do autor** (não independente): com o N1 aplicado (`.env` fora do
  `.vercelignore`), P1 (`.env` no ignore global via `GIT_CONFIG_GLOBAL`) e P2 (`.env` em
  `$XDG_CONFIG_HOME/git/ignore`, caminho que o Fix 2 sugerido não cobria) dão 1 failed, 14 passed.
  Restaurado, 15 passed. Gate: 919 passed.
- **Decisão**: fechar com o risco residual aceito, em vez de uma 4ª rodada. DEPL-18 fica
  `Implementing (risco residual aceito)`; DEPL-19 e DEPL-01 a DEPL-17 ficam `Verified`.
  `validate_state.py` sai com 1 de propósito (veredito registrado FAIL).
- **Também depois da iteração 3**: `1901ad0` (só documentação) corrige a lista numerada do README
  apontada em "Observações" e ajusta o passo 1.3 do roteiro à janela "Conectar" do Supabase.
- **Risco que sobra**: a semântica real do `.vercelignore` na CLI só aparece no deploy. O passo
  3.8 do roteiro e o passo 4 do UAT conferem a ausência do `.env` na aba Source.
