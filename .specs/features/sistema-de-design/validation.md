# Sistema de Design Validation

**Date**: 2026-10-11
**Iteration**: 1
**Spec**: `.specs/features/sistema-de-design/spec.md` (DS-01 … DS-16 e 2 edge cases)
**Diff range**: `7f655a0..50b8818` em `main`, 4 commits: `7f90d0d` (docs), `3bbc99b` (base + `kira.css`), `a7b9d9a` (telas), `50b8818` (AD-010). Produção: `templates/base.html`, `templates/kira.css`, `templates/marca.html`, `templates/500.html`, `contas/templates/contas/login.html` e 6 templates de `inovacoes/templates/inovacoes/`. Teste novo: `inovacoes/tests/test_views_sistema_design.py` (76 testes).
**Verifier**: independent sub-agent (author ≠ verifier)

## Validation: sistema-de-design - FAIL ❌

O gate passa com 568 testes (492 + 76) e as 16 ACs têm evidência `file:line`. Dois achados impedem o PASS. Um mutante sobreviveu: `outline: 0px` num componente passa por todos os testes, e a DS-07 diz que o contorno não some em lugar nenhum (S25). E um teste existente ficou mais fraco sem mudar uma linha: o `assert "ana" in html` da AUTH-01 (`contas/tests/test_views_home.py:49`) agora casa com a palavra "engan**ana**ria" do comentário de `templates/kira.css:6`, embutido em toda página. O comportamento continua protegido pela DS-05 (S26 morre), então não há buraco de cobertura na suíte. As duas correções são pequenas e não tocam teste existente.

---

## Testes existentes (pedido prioritário)

### 1. Nenhum teste existente mudou

- `git diff 7f655a0..HEAD --name-status -- contas/tests inovacoes/tests` → só `A inovacoes/tests/test_views_sistema_design.py`. Nenhum `conftest.py`, nenhum outro arquivo de teste, nenhum `pyproject.toml` mudou (`git diff 7f655a0..HEAD --name-status` lista só templates, `.specs/` e `docs/`).
- Os IDs coletados batem: `pytest --collect-only` em `7f655a0` (worktree) e em `HEAD` sem o arquivo novo dão as mesmas 492 linhas (`diff` vazio).

### 2. Contagens

| Execução | Resultado |
| -------- | --------- |
| `7f655a0`, worktree, suíte inteira | 492 passed |
| `HEAD`, árvore real, sem o arquivo novo | 492 passed |
| `HEAD`, só `test_views_sistema_design.py` | 76 passed |
| `HEAD`, gate completo | 568 passed, 0 failed, 0 skipped |

### 3. Risco de passe vazio (CSS embutido e marca)

Três provas:

- **Varredura estática.** Um script percorre o AST dos 39 arquivos de teste existentes e pega todo literal usado em `in`/`not in`, `.index`/`.rindex`/`.find`/`.count`/`startswith` e `re.search`/`findall`/`sub`. Cada um foi conferido contra `kira.css`, a marca renderizada e o `base.html` novo. Os testes que buscam `role="alert"`, `aria-invalid`, `<h1`, `<header>`, `<table`, `<nav aria-label=…>`, `<a href=…>` e `aria-label="Paginação"` não colidem: todos têm `<` ou `="`, e a folha não tem nenhum dos dois (guarda em `test_views_sistema_design.py:104-105`). Os `index('>')`/`rindex('<')` partem de uma posição dentro do `<main>`, depois do `<style>`. As regex de link (`test_views_cadastro.py:349`, `test_views_edicao.py:36`, `test_views_exclusao.py:50`) só rodam sobre o link "Cancelar" já recortado, e a de `test_views_detalhe.py:192` exige `<a href=` logo depois do `<a`, o que a marca (`<a class="marca" href=…>`) não satisfaz.
- **Folha vazia.** No worktree, `kira.css` vazio: 7 falhas nos testes existentes, e são exatamente os de foco (INOV-35, CONS-41 ×3, EDEX-42 ×3). Nenhum outro teste existente depende do texto da folha.
- **Marca vazia.** `marca.html` vazio: 492 passed. Nenhum teste existente depende da marca.

**Colisão encontrada (1):**

| Teste | Asserção | Casa com | Prova |
| ----- | -------- | -------- | ----- |
| `contas/tests/test_views_home.py:49` (AUTH-01) | `assert "ana" in html` | `templates/kira.css:6`: "…um atributo escrito aqui como no HTML engan**ana**ria quem o procura…" | Tirar `{{ user.get_username }}` do `base.html`: em `7f655a0` o teste **falha**; no `HEAD` ele **passa**. O passe agora é vazio. Na suíte inteira o mutante morre pela DS-05 (`test_views_sistema_design.py:152`, `<span>\s*ana\s*</span>`) |

O quoted selector `[role="alert"]` (S13) não enfraquece em silêncio: além da guarda DS-02, 7 testes existentes falham (os `'role="alert"' not in html` da busca e do cadastro e os de resumo). Com S13 e o resumo do formulário sem `role="alert"` juntos, as 5 falhas do controle (resumo removido com CSS real) continuam todas entre as 7.

### 4. Testes de foco leem a folha real

`test_views_acessibilidade.py:102-108` (INOV-35), `test_views_acessibilidade_consulta.py:61-67` (CONS-41) e `test_views_acessibilidade_alteracao.py:139-145` (EDEX-42) juntam os blocos `<style>` da página e procuram `:focus-visible` com `outline: Npx solid`. A página tem um `<style>` só, igual a `kira.css` (`test_views_sistema_design.py:96-98`). Com a folha vazia os 7 falham; com `button:focus-visible { outline: none; }` (S7) os 7 falham. Eles leem a folha real.

---

## Task Completion

A feature não tem `tasks.md`; o trabalho veio em 3 commits de código e documentação.

| Commit | Status | Notes |
| ------ | ------ | ----- |
| `7f90d0d` | ✅ | spec e `docs/design-spec.md` |
| `3bbc99b` | ✅ | base, `kira.css`, `marca.html`, DS-02 a DS-11 |
| `a7b9d9a` | ✅ | telas, DS-01, DS-12 a DS-16 |
| `50b8818` | ✅ | AD-010 no `STATE.md` |

---

## Spec-Anchored Acceptance Criteria

Caminhos relativos a `inovacoes/tests/test_views_sistema_design.py`, salvo indicação. A fixture `paginas` (`:68-87`) renderiza 9 páginas: login (anônimo), lista, nova, detalhe, editar, excluir, não encontrada, acesso negado e o 500 sem contexto.

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| DS-01 | toda tela estende o base; nenhum outro template com `<style>` ou `style=` | `:366` - `len(telas) == 8`; `:368` - `startswith('{% extends "base.html" %}')`; `:369-370` - sem `<style` e `style=`; `:379-384` - só o base tem `<style>`, igual a `['{% include "kira.css" %}']` | ✅ PASS (S12 morta) |
| DS-02 | um `<style>` por página, conteúdo = `kira.css` | `:97` - `len(estilos) == 1`; `:98` - `estilos[0].strip() == CSS.strip()`, nas 9 páginas | ✅ PASS |
| DS-03 | primeiro focável = "Ir para o conteúdo principal" → `#conteudo`, `id` do único `<main>` | `:116-120` - `(tag, href, texto) == ("a", "#conteudo", "Ir para o conteúdo principal")`; `:122-123` - um `main` com `id == "conteudo"` | ✅ PASS (S1, S2, S3 mortas) |
| DS-04 | `<header>` com "KIRA" → `/`; `<main>`; `<footer>` com "KIRA · Repositório de Inovações" | `:135` - `marca.group(1) == "/"`; `:136` - texto `KIRA`; `:139` - texto no `<footer>` | ✅ PASS (S20, S21 mortas) |
| DS-05 | autenticado: usuário e "Sair" no `<header>`, depois da navegação | `:156` - `fim_da_nav < usuario.start() < sair.start()`; anônimo `:164-165` | ✅ PASS (S22, S26 mortas) |
| DS-06 | todo token de cor da §2 e de tipo da §3 com o valor exato | `:170-192` (21 tokens, conferidos contra `docs/design-spec.md` §2 e §3); `:199` - `_token(nome) == TOKENS_DA_SPEC[nome]` | ✅ PASS (S4, S5, S23 mortas) |
| DS-07 | `:focus-visible` com `2px solid var(--brand-blue)`; contorno nunca removido | `:209` - regex `outline:2px solid var(--brand-blue)`; `:210` - `not re.search(r"outline\s*:\s*(none\|0)\b", CSS)` | ❌ GAP: `outline: 0px` (e `outline-style: none`, `outline-width: 0`) passa pela `:210` (S25 sobreviveu) |
| DS-08 | pares texto/fundo ≥ 4.5:1; `--brand-blue-light` nunca texto nem fundo | `:255` - `_contraste(...) >= 4.5` em 19 pares; `:262` - 3:1 para anel e borda de campo; `:269` - nenhuma propriedade usa `var(--brand-blue-light)` | ✅ PASS (S4, S5, S15 mortas). Observação abaixo |
| DS-09 | reduzir movimento desliga transições e animações | `:278-281` - bloco `@media (prefers-reduced-motion: reduce)` com `transition: none` e `animation: none` | ✅ PASS (S8 morta) |
| DS-10 | mensagem em `role="status"` com `alerta alerta--<tag>` | `:301` - os 4 níveis, `<li class="alerta alerta--{tag}">`; `:309` - logout real → `alerta--success` | ✅ PASS (S14 morta) |
| DS-11 | ícone em `::before` e borda esquerda colorida em cada variante e no `role="alert"` | `:326` - glifo não vazio nas 5 regras; `:333`, `:340` - `border-left` e `border-left-color` por variante | ✅ PASS (S16 morta) |
| DS-12 | status em `selo selo--<status>` na lista e no detalhe | `:405-407` (lista, 3 status); `:418-422` (detalhe, `<dd class="selo selo--…">`, texto puro da CONS-12) | ✅ PASS (S9, S10 mortas) |
| DS-13 | forma distinta por status em `::before` | `:432-434` - forma achada e `len(set(formas)) == 3`; `:435` - `content: ""` | ✅ PASS (S17 morta) |
| DS-14 | "Excluir definitivamente" com `botao--perigo`; demais submits primários | `:451` - `== [("botao--perigo", "Excluir definitivamente")]`; `:452` - fundo `var(--error)`; `:469` - login, busca, nova, editar sem classe; `:470` - `button` com fundo `var(--brand-blue)` | ✅ PASS (S11, S24 mortas) |
| DS-15 | login dentro de `cartao` com a marca no topo | `:481-485` - `cartao cartao--estreito`, ordem marca < `h1` < `form`, texto KIRA | ✅ PASS (S18 morta) |
| DS-16 | tabela num contêiner com rolagem horizontal | `:496-498` - `<div class="tabela"><table>`, `</table></div>`, `overflow-x: auto` | ✅ PASS (S19 morta) |

**Observação DS-08**: a lista de pares (`:228-248`) é mantida à mão. O par `--error` sobre `--error-tint` (ícone `✕` de `.alerta--error::before` e `[role=alert]::before`, `kira.css:351-352`) não está nela. O valor real é 5.62:1, então passa; não é lacuna, mas o teste não acompanha a folha sozinho.

**Status**: ❌ 15/16 ACs com o valor da spec afirmado; DS-07 com lacuna de discriminação. Nenhum spec-precision gap.

---

## Edge Cases

| Caso | Evidência | Result |
| ---- | --------- | ------ |
| 500 sem contexto: link de pular, marca e folha | `:86` - `render_to_string("500.html")` entra na fixture; `:97-98` (DS-02), `:116-123` (DS-03), `:135-139` (DS-04) | ✅ |
| Anônimo sem navegação nem menu | `:164-165` (menu); `inovacoes/tests/test_views_cabecalho.py:27-31` (INOV-38, navegação) | ✅ |

---

## Discrimination Sensor

Executado num `git worktree add --detach` em `50b8818` no scratchpad da sessão, com o `.env` copiado e o PostgreSQL de teste (porta 5433). Linha de base no worktree: 568 passed. Uma mutação por vez, por substituição exata (cada trecho conferido como único), `pytest -q` da suíte inteira e `git checkout -- .` depois de cada uma. Um segundo worktree em `7f655a0` serviu para a linha de base de 492 e para o mutante de controle da AUTH-01. No fim: `git worktree remove --force` nos dois e `git worktree prune`. `git status --porcelain` da árvore real: vazio antes e vazio depois; HEAD inalterado (`50b8818`).

| # | File | Mutação | Killed? (testes que falharam) |
| - | ---- | ------- | ----------------------------- |
| S1 | `templates/base.html:12` | link de pular removido | ✅ `test_primeiro_focavel_e_o_link_de_pular_para_o_main` |
| S2 | `templates/base.html:12` | link de pular movido para depois do `</header>` | ✅ idem |
| S3 | `templates/base.html:36` | `<main>` sem `id="conteudo"` | ✅ idem |
| S4 | `templates/kira.css:19` | `--text-muted` → `#A0A7B4` | ✅ 4: token, dois pares 4.5:1 e a borda 3:1 |
| S5 | `templates/kira.css:26` | `--error` → `#E06A63` | ✅ 3: token, `surface-error`, `error-surface` |
| S6 | `templates/kira.css:88` | `:focus-visible` com 1px | ✅ `test_foco_visivel_e_um_anel_de_2px_na_cor_de_acao` |
| S7 | `templates/kira.css:163` | `button:focus-visible { outline: none; }` | ✅ 8: DS-07 e os 7 de foco (INOV-35, CONS-41, EDEX-42) |
| S8 | `templates/kira.css:498` | bloco de movimento reduzido trocado por `min-width: 9999px` | ✅ `test_reduzir_movimento_desliga_transicoes_e_animacoes` |
| S9 | `inovacao_list.html:58` | status sem o `span.selo` | ✅ 3: `test_lista_mostra_o_status_num_selo_com_o_rotulo[…]` |
| S10 | `inovacao_detail.html:36` | `<dd>` sem `selo` | ✅ 3: `test_detalhe_mostra_o_status_num_selo_com_o_rotulo[…]` |
| S11 | `inovacao_confirm_delete.html:16` | sem `botao--perigo` | ✅ `test_excluir_definitivamente_usa_o_botao_de_perigo` |
| S12 | `inovacao_detail.html:36` | `style="color:red"` na tela | ✅ 5: as duas guardas da DS-01 e os 3 do selo do detalhe |
| S13 | `templates/kira.css:338` | `[role="alert"]` com aspas | ✅ 8: guarda DS-02 e 7 testes existentes (busca, cadastro, edição) |
| S14 | `templates/base.html:42` | variante fixa `alerta--info` | ✅ 4: três níveis e o logout real |
| S15 | `templates/kira.css:399` | `.total` com fundo `var(--brand-blue-light)` | ✅ `test_azul_claro_nunca_e_cor_de_texto_nem_fundo_de_componente` |
| S16 | `templates/kira.css:347` | `.alerta--warning::before` sem glifo | ✅ `test_cada_alerta_tem_icone_alem_da_cor[.alerta--warning::before]` |
| S17 | `templates/kira.css:468` | selo `validada` com o círculo do `em_teste` | ✅ `test_cada_status_tem_uma_forma_propria_alem_da_cor` |
| S18 | `contas/templates/contas/login.html:7` | login fora do `cartao` | ✅ `test_login_fica_num_card_com_a_marca_no_topo` |
| S19 | `templates/kira.css:371` | `.tabela` sem `overflow-x: auto` | ✅ `test_tabela_fica_num_quadro_que_rola_na_horizontal` |
| S20 | `templates/base.html:53` | rodapé só "uso interno" | ✅ `test_toda_pagina_tem_header_com_a_marca_main_e_footer` |
| S21 | `templates/marca.html:5` | marca sem link para `/` | ✅ idem |
| S22 | `templates/base.html:17` | "Sair" e usuário antes da navegação | ✅ 2: `test_cabecalho_autenticado_mostra_usuario_e_sair_depois_da_navegacao[…]` |
| S23 | `templates/kira.css:38` | `--fs-base` → `1.125rem` | ✅ `test_root_declara_o_token_da_spec_com_o_valor_exato[fs-base]` |
| S24 | `inovacao_form.html` | "Salvar" com `class="botao--secundario"` | ✅ `test_demais_envios_das_telas_tem_o_estilo_primario` |
| S25 | `templates/kira.css:163` | `button:focus-visible { outline: 0px; }` | ❌ **Sobreviveu**: 568 passed. A regex `outline\s*:\s*(none\|0)\b` não casa `0px` (não há `\b` entre `0` e `p`) e não olha `outline-style`/`outline-width` |
| S26 | `templates/base.html:24` | nome do usuário some do cabecalho | ✅ 2 (DS-05). Os testes existentes **não** a pegam mais (ver colisão da AUTH-01); em `7f655a0` a AUTH-01 a pegava |

**Sensor depth**: expandido (≥5 pedido): 26 mutações, cobrindo layout, tokens, foco, movimento, mensagens, selos, botões, cartão, tabela e as guardas de estilo.
**Result**: 25/26 mortas, 1 sobrevivente (S25).

---

## Code Quality

| Principle | Status |
| --------- | ------ |
| Minimum code | ✅ Uma folha, um parcial de marca; as telas só trocam marcação e classes |
| Surgical changes | ✅ Nenhuma view, form, model, URL ou migração mudou; `makemigrations --check` limpo |
| No scope creep | ✅ Itens fora de escopo da spec (logo, Inter, modal, `aria-current`) ficaram fora |
| Matches patterns | ✅ HTML fixado por testes mantido; estilo por papel ARIA e contêiner, como a AD-010 diz |
| Spec-anchored outcome check | ⚠️ 15/16; DS-07 com lacuna (S25) |
| Per-layer Coverage Expectation met | ✅ Template (renderização das 9 páginas) e folha (regras e tokens) |
| Every test maps to a spec requirement | ✅ Cada teste novo cita a DS na docstring |
| Documented guidelines followed | ✅ `docs/design-spec.md` e AD-010; testes existentes intactos |
| Testes existentes não enfraquecidos | ❌ AUTH-01 (`contas/tests/test_views_home.py:49`) passa vazio pela palavra "enganaria" em `templates/kira.css:6` |

---

## Gate Check

- **Gate command**: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` (árvore real, HEAD `50b8818`)
- **Result**: exit 0. `ruff check`: All checks passed · `ruff format --check`: 101 files already formatted · `makemigrations --check`: No changes detected · `pytest -q`: 568 passed, 0 failed, 0 skipped (14.53 s)
- **Test count before feature**: 492 (`7f655a0`, conferido no worktree)
- **Test count after feature**: 568
- **Delta**: +76, todos em `test_views_sistema_design.py`. Nenhum teste removido nem alterado
- **Skipped tests**: nenhum
- **Failures**: nenhuma

---

## Fix Plans

### Fix 1: DS-07 não pega contorno zerado em px nem por propriedade longa (S25)

- **Root cause**: `test_views_sistema_design.py:210` usa `outline\s*:\s*(none|0)\b`. `outline: 0px`, `outline-width: 0`, `outline-style: none` e `outline-color: transparent` removem o anel e passam.
- **Fix task**: em `test_foco_visivel_e_um_anel_de_2px_na_cor_de_acao`, recusar na folha toda `outline(-style)?\s*:\s*none`, `outline(-width)?\s*:\s*0(px|em|rem)?\b` e `outline-color\s*:\s*transparent`. Só o teste novo muda; os de foco da F2–F4 ficam como estão.
- **Verify**: S25 e as três variantes morrem; 568 passed.
- **Priority**: Major (RNF09, WCAG 2.4.7)

### Fix 2: o comentário da folha contém o nome de usuário dos testes (AUTH-01 vazio)

- **Root cause**: `templates/kira.css:6` diz "enganaria", que contém `ana`, o usuário da fixture `autor`/`ana`. O CSS vai em toda página, então `assert "ana" in html` (`contas/tests/test_views_home.py:49`) sempre passa.
- **Fix task**: trocar a palavra no comentário (por exemplo "confundiria"). Para não voltar, estender `test_folha_central_nao_repete_atributos_do_html` (`:104-105`) com os nomes de usuário das fixtures (`ana`, `bruno`, `carla`, `davi`, `raiz`) ausentes do CSS, ou proibir comentários com texto livre na folha. Não mexer em `test_views_home.py`.
- **Verify**: com `{{ user.get_username }}` removido do base, `contas/tests/test_views_home.py::test_home_identifica_a_conta_e_oferece_sair` volta a falhar, como em `7f655a0`.
- **Priority**: Minor (a DS-05 cobre o comportamento; é perda de discriminação de um teste existente)

---

## Requirement Traceability Update

Proposta (o `spec.md` não foi editado pelo Verifier):

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| DS-01 … DS-06, DS-08 … DS-16 | Implemented | ✅ Verified |
| DS-07 | Implemented | ❌ Needs Fix (Fix 1) |

---

## Summary

**Overall**: ❌ Not Ready (evidência: `inovacoes/tests/test_views_sistema_design.py:210`, `contas/tests/test_views_home.py:49`, `templates/kira.css:6`)

**Spec-anchored check**: 15/16 ACs com o valor da spec afirmado e discriminante; DS-07 com lacuna; edge cases 2/2
**Sensor**: 25/26 mortas (S25 sobreviveu)
**Gate**: 568 passed, 0 failed

**What works**: os 492 testes da F1 à F4 passam sem nenhuma alteração. A folha embutida não engana as buscas de atributo (`role="alert"`, `aria-invalid`, `<h1`, `<table`, `<nav …>`): a guarda de `="` e `<` funciona, e S13 é pega também pelos testes existentes. Os testes de foco da F2–F4 leem a folha real. Layout, tokens, contraste, movimento, mensagens, selos, botões, cartão e tabela têm teste que discrimina.

**Issues found**: Fix 1 (regex de contorno removido) e Fix 2 (palavra do comentário que esvazia a AUTH-01).

**Next steps**: rotear os dois fixes a um implementador e redespachar o Verifier (iteração 2 de no máximo 3).
