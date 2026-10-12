# Sistema de Design Validation

**Date**: 2026-10-11
**Iteration**: 2
**Spec**: `.specs/features/sistema-de-design/spec.md` (DS-01 … DS-16 e 2 edge cases)
**Diff range**: feature `7f655a0..4db5be8` em `main` (HEAD = `4db5be8`). Correção desta iteração: `7918c00..4db5be8`, 1 commit (`4db5be8`), só `templates/kira.css` (+2/−2, comentário) e `inovacoes/tests/test_views_sistema_design.py` (+26/−1). Produção da feature: `templates/base.html`, `templates/kira.css`, `templates/marca.html`, `templates/500.html`, `contas/templates/contas/login.html` e 6 templates de `inovacoes/templates/inovacoes/`. Teste novo: `inovacoes/tests/test_views_sistema_design.py` (77 testes).
**Verifier**: independent sub-agent (author ≠ verifier)

## Validation: sistema-de-design - PASS ✅

O gate passa com 569 testes (492 + 77). As 16 ACs têm evidência `file:line` com o valor da spec afirmado. Os dois achados da iteração 1 estão resolvidos. S25 (`outline: 0px`) morre, junto com `outline-width: 0`, `outline-style: none`, `outline-color: transparent` e `outline: 1px`. A AUTH-01 (`contas/tests/test_views_home.py:49`) volta a discriminar: sem o nome do usuário no cabeçalho, ela falha de novo no HEAD, como em `7f655a0`. A guarda nova pega um nome de usuário dos testes posto num comentário da folha (`carla`, `Bruno`) e a volta de "enganaria". O sensor fica em 33/33 mortas no escopo das ACs. Um mutante fora da spec sobreviveu, `outline: thin solid` (S25f): afina o anel sem removê-lo. Fica registrado como observação, não como lacuna.

---

## Testes existentes (pedido prioritário)

### 1. Nenhum teste existente mudou

- `git diff 7f655a0..HEAD --name-status -- contas/tests inovacoes/tests` → só `A inovacoes/tests/test_views_sistema_design.py`. O commit de correção (`7918c00..4db5be8`) toca só `templates/kira.css` e esse arquivo novo.
- Os IDs coletados em `HEAD` sem o arquivo novo são as mesmas 492 linhas de `7f655a0` (`diff` vazio contra a coleta da iteração 1).

### 2. Contagens

| Execução | Resultado |
| -------- | --------- |
| `7f655a0`, worktree, suíte inteira (iteração 1) | 492 passed |
| `HEAD`, árvore real, sem o arquivo novo | 492 passed |
| `HEAD`, gate completo | 569 passed, 0 failed, 0 skipped |

### 3. Risco de passe vazio (CSS embutido e marca)

- **Varredura estática refeita no HEAD.** Mesmo script da iteração 1 (AST dos testes existentes; literais em `in`/`not in`, `index`/`rindex`/`find`/`count`/`startswith`, `re.*`, conferidos contra `kira.css`, a marca e o `base.html`). A colisão `"ana"` sumiu. O que sobra contra a folha são caracteres soltos (`>`, `:`, `/`, `"`, `a`, `on`) usados em recortes que partem de dentro do `<main>`, em caminhos de URL ou em nomes de tag do `HTMLParser`; nenhum é busca sobre o HTML inteiro. Marca e base: iguais à iteração 1, sem colisão.
- **AUTH-01 de volta.** No worktree do HEAD, tirar `{{ user.get_username }}` do cabeçalho (S26) derruba `contas/tests/test_views_home.py::test_home_identifica_a_conta_e_oferece_sair` e os dois testes da DS-05.
- **Guarda contra a recaída.** `test_folha_central_nao_contem_nome_de_usuario_dos_testes` (`inovacoes/tests/test_views_sistema_design.py:119-123`) junta todo `username="…"` e `username=f"…` dos testes de `contas` e `inovacoes` (`:108-115`), confere que `ana` está entre eles (`:122`) e recusa cada um na folha sem diferenciar caixa (`:123`). S27 (`carla`), S28 (`Bruno`) e S29 ("enganaria") morrem nela.
- Limite conhecido da guarda: só cobre nomes de usuário. Um teste existente que buscasse outra palavra solta no HTML inteiro não seria protegido; a varredura estática não acha nenhum hoje.

### 4. Testes de foco leem a folha real

`test_views_acessibilidade.py:102-108` (INOV-35), `test_views_acessibilidade_consulta.py:61-67` (CONS-41) e `test_views_acessibilidade_alteracao.py:139-145` (EDEX-42) leem os blocos `<style>` da página. S7 (`outline: none`) derruba os 7 no HEAD. Com a folha vazia eles também caíam (iteração 1).

---

## Task Completion

A feature não tem `tasks.md`.

| Commit | Status | Notes |
| ------ | ------ | ----- |
| `7f90d0d`, `3bbc99b`, `a7b9d9a`, `50b8818` | ✅ | Inalterados desde a iteração 1 |
| `4db5be8` (Fix 1 e Fix 2) | ✅ | DS-07 em `:229-235`; guarda de nomes em `:108-123`; comentário de `templates/kira.css:6-7` |

---

## Spec-Anchored Acceptance Criteria

Caminhos relativos a `inovacoes/tests/test_views_sistema_design.py`, relidos no HEAD `4db5be8`. A fixture `paginas` (`:68-87`) renderiza 9 páginas: login (anônimo), lista, nova, detalhe, editar, excluir, não encontrada, acesso negado e o 500 sem contexto.

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| DS-01 | toda tela estende o base; nenhum outro template com `<style>` ou `style=` | `:391` - `len(telas) == 8`; `:393-395` - `startswith('{% extends "base.html" %}')`, sem `<style` e `style=`; `:404-409` - só o base tem `<style>`, igual a `['{% include "kira.css" %}']` | ✅ PASS (S12 morta) |
| DS-02 | um `<style>` por página, conteúdo = `kira.css` | `:97-98` - `len(estilos) == 1` e `estilos[0].strip() == CSS.strip()`, nas 9 páginas; guardas `:104-105` (sem `="` nem `<`) e `:122-123` (sem nome de usuário dos testes) | ✅ PASS (S13, S27, S28, S29 mortas) |
| DS-03 | primeiro focável = "Ir para o conteúdo principal" → `#conteudo`, `id` do único `<main>` | `:134-138` - `(tag, href, texto) == ("a", "#conteudo", "Ir para o conteúdo principal")`; `:140-141` - um `main` com `id == "conteudo"` | ✅ PASS (S1, S2, S3 mortas) |
| DS-04 | `<header>` com "KIRA" → `/`; `<main>`; `<footer>` com "KIRA · Repositório de Inovações" | `:153` - `marca.group(1) == "/"`; `:154` - texto `KIRA`; `:157` - texto no `<footer>` | ✅ PASS (S20, S21 mortas) |
| DS-05 | autenticado: usuário e "Sair" no `<header>`, depois da navegação | `:174` - `fim_da_nav < usuario.start() < sair.start()`; anônimo `:182-183` | ✅ PASS (S22, S26 mortas) |
| DS-06 | todo token de cor da §2 e de tipo da §3 com o valor exato | `:188-210` (21 tokens, conferidos contra `docs/design-spec.md` §2 e §3); `:217` - `_token(nome) == TOKENS_DA_SPEC[nome]` | ✅ PASS (S4, S5, S23 mortas) |
| DS-07 | `:focus-visible` com `2px solid var(--brand-blue)`; contorno nunca removido | `:227` - regex `outline:2px solid var(--brand-blue)` na regra `:focus-visible`; `:229-235` - toda declaração `outline`/`outline-*` da folha: `:231` recusa `none`/`hidden`/`transparent`, `:232` recusa valor que começa em zero com qualquer unidade, `:235` exige `px >= 2` em `outline`/`outline-width` | ✅ PASS (S6, S7, S25, S25b–e mortas; Fix 1 resolvido) |
| DS-08 | pares texto/fundo ≥ 4.5:1; `--brand-blue-light` nunca texto nem fundo | `:280` - `_contraste(...) >= 4.5` em 19 pares; `:287` - 3:1 para anel e borda de campo; `:294` - nenhuma propriedade usa `var(--brand-blue-light)` | ✅ PASS (S4, S5, S15 mortas). Observação abaixo |
| DS-09 | reduzir movimento desliga transições e animações | `:303-306` - bloco `@media (prefers-reduced-motion: reduce)` com `transition: none` e `animation: none` | ✅ PASS (S8 morta) |
| DS-10 | mensagem em `role="status"` com `alerta alerta--<tag>` | `:326` - os 4 níveis, `<li class="alerta alerta--{tag}">`; `:334` - logout real → `alerta--success` | ✅ PASS (S14 morta) |
| DS-11 | ícone em `::before` e borda esquerda colorida em cada variante e no `role="alert"` | `:351` - glifo não vazio nas 5 regras; `:358`, `:365` - `border-left` e `border-left-color` por variante | ✅ PASS (S16 morta) |
| DS-12 | status em `selo selo--<status>` na lista e no detalhe | `:430-432` (lista, 3 status); `:443-447` (detalhe, `<dd class="selo selo--…">`, texto puro da CONS-12) | ✅ PASS (S9, S10 mortas) |
| DS-13 | forma distinta por status em `::before` | `:457-460` - forma achada, `len(set(formas)) == 3`, `content: ""` | ✅ PASS (S17 morta) |
| DS-14 | "Excluir definitivamente" com `botao--perigo`; demais submits primários | `:476` - `== [("botao--perigo", "Excluir definitivamente")]`; `:477` - fundo `var(--error)`; `:494` - login, busca, nova, editar sem classe; `:495` - `button` com fundo `var(--brand-blue)` | ✅ PASS (S11, S24 mortas) |
| DS-15 | login dentro de `cartao` com a marca no topo | `:506-510` - `cartao cartao--estreito`, ordem marca < `h1` < `form`, texto KIRA | ✅ PASS (S18 morta) |
| DS-16 | tabela num contêiner com rolagem horizontal | `:521-523` - `<div class="tabela"><table>`, `</table></div>`, `overflow-x: auto` | ✅ PASS (S19 morta) |

**Observação DS-08** (mantida da iteração 1): a lista de pares (`:253-273`) é mantida à mão e não tem `--error` sobre `--error-tint` (ícone `✕` de `kira.css:351-352`). O valor real é 5.62:1; não é lacuna.

**Observação DS-07**: palavras-chave de largura (`thin`, `medium`) não passam pela checagem de `px` (`:233-235`). `outline: thin solid` sobrevive (S25f). A DS-07 proíbe *remover* o contorno, e `thin` não remove; a §6 pede 2px só na regra `:focus-visible`, e essa continua conferida em `:227`. Fica como endurecimento opcional, não como lacuna.

**Status**: ✅ 16/16 ACs com o valor da spec afirmado. Nenhum spec-precision gap.

---

## Edge Cases

| Caso | Evidência | Result |
| ---- | --------- | ------ |
| 500 sem contexto: link de pular, marca e folha | `:86` - `render_to_string("500.html")` na fixture; `:97-98` (DS-02), `:134-141` (DS-03), `:153-157` (DS-04) | ✅ |
| Anônimo sem navegação nem menu | `:182-183` (menu); `inovacoes/tests/test_views_cabecalho.py:27-31` (INOV-38, navegação) | ✅ |

---

## Discrimination Sensor

Executado num `git worktree add --detach` em `4db5be8` no scratchpad da sessão, com o `.env` copiado e o PostgreSQL de teste (porta 5433). Uma mutação por vez, por substituição exata (cada trecho conferido como único), `pytest -q` da suíte inteira e `git checkout -- .` depois de cada uma. Os 24 mutantes da iteração 1 foram rodados de novo, mais 10 novos. No fim: `git worktree remove --force` e `git worktree prune`. `git status --porcelain` da árvore real: vazio antes e vazio depois; HEAD inalterado (`4db5be8`).

### Rodados de novo (iteração 1)

| # | Mutação | Killed? |
| - | ------- | ------- |
| S1–S3 | link de pular removido, movido para depois do `</header>`; `<main>` sem `id` | ✅ DS-03 |
| S4, S5, S23 | `--text-muted` `#A0A7B4`, `--error` `#E06A63`, `--fs-base` `1.125rem` | ✅ DS-06 e DS-08 |
| S6 | `:focus-visible` com 1px | ✅ DS-07 |
| S7 | `button:focus-visible { outline: none; }` | ✅ DS-07 e os 7 testes de foco existentes |
| S8 | sem bloco de movimento reduzido | ✅ DS-09 |
| S9, S10 | lista e detalhe sem `selo` | ✅ DS-12 |
| S11, S24 | sem `botao--perigo`; "Salvar" com `botao--secundario` | ✅ DS-14 |
| S12 | `style=` numa tela | ✅ DS-01 |
| S13 | `[role="alert"]` com aspas | ✅ guarda DS-02 e 7 testes existentes |
| S14 | nível da mensagem fixo em `info` | ✅ DS-10 |
| S15 | `--brand-blue-light` como fundo | ✅ DS-08 |
| S16, S17 | alerta sem ícone; dois selos com a mesma forma | ✅ DS-11, DS-13 |
| S18, S19 | login fora do cartão; tabela sem `overflow-x` | ✅ DS-15, DS-16 |
| S20, S21, S22 | rodapé, marca sem link, "Sair" antes da navegação | ✅ DS-04, DS-05 |

### Ex-sobrevivente e mutações novas

| # | File | Mutação | Killed? (testes que falharam) |
| - | ---- | ------- | ----------------------------- |
| S25 | `templates/kira.css:163` | `button:focus-visible { outline: 0px; }` | ✅ `test_foco_visivel_e_um_anel_de_2px_na_cor_de_acao` (sobrevivia na iteração 1) |
| S25b | idem | `outline-width: 0` | ✅ idem |
| S25c | idem | `outline-style: none` | ✅ idem |
| S25d | idem | `outline-color: transparent` | ✅ idem |
| S25e | idem | `outline: 1px solid red` | ✅ idem |
| S25f | idem | `outline: thin solid` | ⚪ Sobreviveu. Fora da DS-07 (não remove o anel); ver observação |
| S26 | `templates/base.html:24` | nome do usuário some do cabeçalho | ✅ `contas/tests/test_views_home.py::test_home_identifica_a_conta_e_oferece_sair` (AUTH-01, que na iteração 1 passava vazio) e os 2 da DS-05 |
| S27 | `templates/kira.css` | `/* revisado por carla */` | ✅ `test_folha_central_nao_contem_nome_de_usuario_dos_testes` |
| S28 | `templates/kira.css` | `/* ver com Bruno */` (caixa diferente) | ✅ idem |
| S29 | `templates/kira.css:6` | "confundiria" → "enganaria" | ✅ idem |

**Sensor depth**: expandido: 34 mutações (24 repetidas, 10 novas).
**Result**: 33/33 mortas no escopo das ACs - PASS ✅. S25f (fora da spec) registrada como observação.

---

## Code Quality

| Principle | Status |
| --------- | ------ |
| Minimum code | ✅ A correção é uma palavra de comentário e duas checagens no teste novo |
| Surgical changes | ✅ `4db5be8` só toca `templates/kira.css` (comentário) e `test_views_sistema_design.py` |
| No scope creep | ✅ |
| Matches patterns | ✅ HTML fixado por testes mantido; estilo por papel ARIA e contêiner (AD-010) |
| Spec-anchored outcome check | ✅ 16/16 |
| Per-layer Coverage Expectation met | ✅ Template (9 páginas renderizadas) e folha (regras, tokens, guardas) |
| Every test maps to a spec requirement | ✅ Cada teste novo cita a DS na docstring; a guarda nova cita DS-02 e AD-010 |
| Documented guidelines followed | ✅ `docs/design-spec.md` e AD-010 |
| Testes existentes não enfraquecidos | ✅ Nenhum arquivo existente mudou; a AUTH-01 voltou a discriminar (S26) |

---

## Gate Check

- **Gate command**: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` (árvore real, HEAD `4db5be8`)
- **Result**: exit 0. `ruff check`: All checks passed · `ruff format --check`: 102 files already formatted · `makemigrations --check`: No changes detected · `pytest -q`: 569 passed, 0 failed, 0 skipped (14.60 s)
- **Test count before feature**: 492 (`7f655a0`)
- **Test count after iteration 1**: 568
- **Test count after feature**: 569
- **Delta**: +77, todos em `test_views_sistema_design.py` (+1 nesta iteração). Nenhum teste removido nem alterado fora desse arquivo
- **Skipped tests**: nenhum
- **Failures**: nenhuma

---

## Spec-Precision Gaps

Nenhum.

---

## Fix Plans

Nenhum aberto. Situação dos planos da iteração 1:

| Fix | Resolvido? | Evidência |
| --- | ---------- | --------- |
| Fix 1 (DS-07, contorno zerado em px ou por propriedade longa, S25) | ✅ | `inovacoes/tests/test_views_sistema_design.py:229-235`. S25 e S25b–e morrem |
| Fix 2 (comentário com "ana" esvaziava a AUTH-01) | ✅ | `templates/kira.css:6-7` sem "enganaria"; guarda em `inovacoes/tests/test_views_sistema_design.py:108-123`. S26 morre na AUTH-01; S27–S29 morrem na guarda |

Endurecimento opcional (não bloqueia): recusar as palavras-chave `thin`/`medium` em `outline`/`outline-width` na checagem da DS-07 (S25f).

---

## Requirement Traceability Update

Proposta (o `spec.md` não foi editado pelo Verifier):

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| DS-01 … DS-16 | Implemented | ✅ Verified |

---

## Histórico

- **Iteração 1** (HEAD `50b8818`): FAIL ❌. 15/16 ACs (DS-07 com lacuna), 25/26 mutantes mortos. Sobreviveu S25 (`button:focus-visible { outline: 0px; }`): a regex `outline\s*:\s*(none|0)\b` não casava `0px` nem as propriedades longas. E a AUTH-01 (`contas/tests/test_views_home.py:49`, `"ana" in html`) passava vazio pela palavra "enganaria" do comentário de `templates/kira.css:6`; sem o nome do usuário ela falhava em `7f655a0` e passava no HEAD (só a DS-05 pegava). Lições L-017 e L-018 registradas como candidatas. Corrigido em `4db5be8`, sem tocar teste existente.
- **Iteração 2** (HEAD `4db5be8`): PASS ✅. 16/16 ACs, S25 e as variantes mortas, AUTH-01 de volta, guarda de nomes de usuário com 3/3 mutantes mortos, 33/33 no escopo das ACs.

---

## Summary

**Overall**: ✅ Ready (evidência: `inovacoes/tests/test_views_sistema_design.py:229-235`, `inovacoes/tests/test_views_sistema_design.py:119-123`, `contas/tests/test_views_home.py:49`)

**Spec-anchored check**: 16/16 ACs com o valor da spec afirmado; 0 spec-precision gaps; edge cases 2/2
**Sensor**: 33/33 mortas no escopo das ACs (S25f fora da spec, observação)
**Gate**: 569 passed, 0 failed

**What works**: os 492 testes da F1 à F4 passam sem nenhuma alteração e nenhum deles passa vazio por causa da folha ou da marca. A folha embutida não repete atributos (`="`, `<`) nem nomes de usuário dos testes, e as duas regras têm teste. Os testes de foco da F2–F4 leem a folha real. A DS-07 agora pega contorno removido por qualquer forma equivalente. Layout, tokens, contraste, movimento, mensagens, selos, botões, cartão e tabela têm teste que discrimina.

**Issues found**: nenhum bloqueante.

**Next steps**: o orquestrador atualiza a rastreabilidade do `spec.md` e o `STATE.md`; conferência visual no navegador, se desejada.
