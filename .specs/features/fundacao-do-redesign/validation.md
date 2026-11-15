# Fundação do Redesign (R1) Validation

**Date**: 2026-11-15
**Iteration**: 2 (final; o usuário limitou a feature a 1 iteração de correção)
**Spec**: `.specs/features/fundacao-do-redesign/spec.md` (RED-01 … RED-42; regras de teste da feature; T-A a T-F)
**Diff range**: `a3799f7..e1f255d` em `main` (iteração 1: `a3799f7..23b7565`; correções: T18 `64b9495`, T19 `878db23`, T20 `e1f255d`)
**Verifier**: independent sub-agent (author ≠ verifier)

**Verdict**: FAIL ❌ (iteração 2), **com risco residual de teste aceito pelo usuário em 2026-11-15** — ver [Decisão do usuário](#decisão-do-usuário-2026-11-15). O veredito do Verifier não foi reescrito; a feature foi fechada por decisão, não por PASS.

Os 5 sobreviventes da iteração 1 morrem, as 42 ACs têm evidência e o gate passa (1326). O FAIL vem de 16 sobreviventes em 31 mutantes novos, todos **lacunas de teste**: nenhum defeito de produção foi achado (a folha e o HTML atuais cumprem RED-16, RED-22 e a regra de teste). Detalhes na seção "Iteração 2" logo abaixo; o relatório da iteração 1 segue intacto depois dela.

---

## Decisão do usuário (2026-11-15)

Com o limite de 1 iteração de correção esgotado e nenhum defeito de produção, o usuário escolheu **aceitar o risco residual e fechar**. Riscos aceitos (todos lacuna de teste): gaps 1 e 2 da iteração 2 (RED-22: menu encolhido por largura/`font-size` quase zero, N22/N30; altura de botão por seletor genérico ou `max-height`, N02–N04); gap 3 (escapes CSS na guarda de esconder, N17/N18); gap 4 (outras formas de esconder: N07–N11, N19–N21); gap 5 (RED-16: oráculo do ícone é o próprio arquivo, N27). RED-16 e RED-22 ficam `Implementing (risco residual aceito)` na spec. Ideia de correção em Deferred Ideas do `context.md`.

---

## Iteração 2

### Correções conferidas (T18–T20)

| Task | O que conferi | Resultado |
| ---- | ------------- | --------- |
| T18 `64b9495` | `templates/kira.css:389-392`: `.botao--compacto, .usuario button { min-height: 44px }`; fonte e padding seguem pequenos. Testes `inovacoes/tests/test_folha_v2.py:788-792` (`button`, `.botao`, `.botao--compacto`, `.usuario button` com `min-height` ≥ 44) e `:796-805` (nenhuma regra de seletor com `button`/`.botao` declara `height`/`min-height` < 44px, inclusive em `@media`). | ✅ RED-22 (botões) cumprida na produção. ⚠️ A guarda só vê seletor que contém `button` ou `.botao` (`_e_botao`, `:776`) e ignora `max-height`: N02, N03, N04 sobrevivem. |
| T19 `878db23` | Allowlist `ESCONDIDOS_PELA_SPEC` (`test_folha_v2.py:943`) tem só as 2 entradas da RED-28 (`.decorativo` e `.faixa-marca` sob `:root[data-contraste=alto]`, contexto vazio), nada além. `_regras_aninhadas` guarda o contexto de cada regra: lê seletor composto, de atributo, `:where()`/`:is()` e regras dentro de `@media`, `@supports`, `@layer`, `@container` (M27, M28, M41, N12–N16 morrem). `test_guarda_acha_cada_forma_de_esconder` (`:1039`) mostra que os 10 vetores listados são achados. | ✅ escopo correto. ⚠️ Só acha os 10 vetores da lista, na grafia literal: escape CSS, `clip-path` com outro `inset`, `overflow` em outra regra, quase-zero, cor e deslocamento sobrevivem (N07–N11, N17–N22, N30). |
| T20 `e1f255d` | `nucleo/tests/test_casca.py:338-350` compara as formas (`path`, `circle`…) do SVG que abre cada item com `templates/icones/{lampada,circulo-mais,grafico-barras}.svg`; `:354-364` faz o mesmo com `contraste.svg` no botão. `aria-hidden`/`focusable` seguem cobertos por `test_casca.py:294-298` (N25, N26, N28 morrem). | ✅ M43 morre. ⚠️ O oráculo é o próprio arquivo de produção: trocar o conteúdo de `lampada.svg` pelo do gráfico passa (N27). |

Testes antigos: T18–T20 só acrescentam testes; nenhum teste foi removido ou afrouxado (`git diff 23b7565..e1f255d`). Contagem 1297 → 1326 (+29).

### Spec-anchored check (it. 2)

As 38 ACs aprovadas na iteração 1 seguem como estavam (o código delas não mudou; regressão 14/14 abaixo). As cláusulas abertas:

| AC | Cláusula | Evidência nova | Resultado |
| -- | -------- | -------------- | --------- |
| RED-16 | qual ícone em cada item (lâmpada, círculo com mais, gráfico) | `nucleo/tests/test_casca.py:350` `_formas_do_icone_inicial(conteudo) == arquivo` | ✅ (oráculo autorreferente, N27) |
| RED-22 | 44px em botões | `inovacoes/tests/test_folha_v2.py:792` `_altura_em_px(alturas[-1]) >= 44`; `:805` `baixas == []` | ✅ (guarda presa ao nome do seletor, N02–N04) |
| RED-22 | sem virar só ícone | `inovacoes/tests/test_folha_v2.py:1013` `_declaracoes_que_escondem(CSS) == ESCONDIDOS_PELA_SPEC` | ✅ para `font-size: 0`/`display`/`visibility` etc.; N22 (largura + `overflow`) e N30 (`font-size: 1px`) sobrevivem |
| RED-23 | ícone de meio círculo | `nucleo/tests/test_casca.py:364` | ✅ |
| Regra de teste (`display: none` em seletor da folha) | seletor composto/atributo | `inovacoes/tests/test_folha_v2.py:1013` | ✅ (M27, M28 morrem); `display: none` escrito com escape sobrevive (N17, N18) |

**Status**: 42/42 ACs com evidência `file:line` que afirma o valor da spec. Lacunas de precisão da spec da iteração 1 (RED-09 `:active`, RED-10, RED-12, RED-35) seguem sinalizadas, sem reprovar.

### Discrimination Sensor (it. 2)

Worktree isolada em `e1f255d` no scratchpad (`.env` por symlink, ignorado pelo git). Baseline na worktree: 1326 passed. Cada mutante rodou a suíte inteira com `-x` e o arquivo foi restaurado (`git checkout`) em seguida; `git status --porcelain` da worktree vazio no fim. Worktree removida e `git worktree prune` rodado; a árvore real ficou com ` M .specs/LESSONS.md` e ` M .specs/lessons.json`, igual ao baseline.

**Reinjeção dos 5 sobreviventes da iteração 1** (como descritos abaixo, no catálogo):

| # | Mutação | Resultado |
| - | ------- | --------- |
| M27 | `.rodape__links li { display: none }` | ✅ morto, `test_folha_so_esconde_o_que_a_spec_manda` |
| M28 | `nav[aria-label=Principal] { display: none }` | ✅ morto, idem |
| M41 | `@media (max-width: 40rem) { nav[aria-label=Principal] a { font-size: 0 } }` | ✅ morto, idem |
| M42 | `button { min-height: 28px }` | ✅ morto, `test_botao_tem_altura_minima_de_44px[button]` |
| M43 | gráfico no lugar da lâmpada em "Inovações" (`base.html:46`) | ✅ morto, `test_cada_item_do_menu_tem_o_seu_icone` |

**Mutantes novos** (todos acrescentados ao fim de `templates/kira.css`, salvo indicação):

| # | Mutação | Cláusula | Resultado |
| - | ------- | -------- | --------- |
| N01 | `kira.css:391` volta a `min-height: 36px` (Sair) | RED-22 | ✅ morto, `test_botao_tem_altura_minima_de_44px[.botao--compacto]` |
| N02 | `.usuario form > * { min-height: 0; height: 30px; }` (Sair a 30px sem citar `button`) | RED-22 | ❌ **sobreviveu** |
| N03 | `[type=submit] { min-height: 32px }` (todo botão de envio a 32px) | RED-22 | ❌ **sobreviveu** |
| N04 | `.usuario > form :last-child { max-height: 30px; min-height: 0 }` | RED-22 | ❌ **sobreviveu** |
| N05 | `nav[aria-label=Principal] a { clip-path: inset(50%); }` | regra de teste | ✅ morto, `test_folha_so_esconde_o_que_a_spec_manda` |
| N06 | `nav[aria-label=Principal] { max-height: 0; overflow: hidden; }` | regra de teste | ✅ morto, idem |
| N07 | `.rodape__links { height: 0 }` + `footer ul { overflow: hidden }` (overflow em outra regra) | RED-32 / regra | ❌ **sobreviveu** |
| N08 | `nav[aria-label=Principal] a { color: transparent }` | RED-16 / regra | ❌ **sobreviveu** |
| N09 | `nav[aria-label=Principal] a { color: var(--surface) }` (cor igual ao fundo) | RED-16 / RED-10 | ❌ **sobreviveu** |
| N10 | `.rodape__links { position: absolute; left: -9999px; }` | RED-32 / regra | ❌ **sobreviveu** |
| N11 | `.rodape__links { content-visibility: hidden; }` | RED-32 / regra | ❌ **sobreviveu** |
| N12 | `@supports (display: grid) { .rodape__links li { display: none } }` | regra | ✅ morto, `test_folha_so_esconde_o_que_a_spec_manda` |
| N13 | `@layer extra { nav[aria-label=Principal] a { visibility: hidden } }` | regra | ✅ morto, idem |
| N14 | `@container (min-width: 0px) { .rodape__links { display: none } }` | regra | ✅ morto, idem |
| N15 | `:where(.rodape__links) { display: none }` | regra | ✅ morto, idem |
| N16 | `:is(footer) ul { opacity: 0 }` | regra | ✅ morto, idem |
| N17 | `.rodape__links { dis\70 lay: none; }` (escape no nome da propriedade) | regra (`display: none`) | ❌ **sobreviveu** |
| N18 | `.rodape__links { display: n\6f ne; }` (escape no valor) | regra (`display: none`) | ❌ **sobreviveu** |
| N19 | `.rodape__links { opacity: 0.01 }` | regra | ❌ **sobreviveu** |
| N20 | `.rodape__links { transform: translateX(-200vw) }` | regra | ❌ **sobreviveu** |
| N21 | `.rodape__links { clip-path: inset(0 0 100% 0) }` ("clip-path que zera", da própria T19) | regra | ❌ **sobreviveu** |
| N22 | `@media (max-width: 40rem) { nav[aria-label=Principal] a { width: 2.5rem; overflow: hidden; white-space: nowrap; } }` (menu só ícone) | RED-22 | ❌ **sobreviveu** |
| N23 | `base.html`: `style="display: none"` no `ul.rodape__links` | regra | ✅ morto, `test_com_o_cookie_alto_a_pagina_traz_a_mesma_folha[False]` |
| N24 | `base.html`: segundo `<style>` com `.rodape__links{display:none}` | regra | ✅ morto, idem |
| N25 | `icones/lampada.svg` sem `aria-hidden` | RED-16 | ✅ morto, `test_menu_tem_os_tres_itens_em_ordem_cada_um_com_icone_antes_do_texto` |
| N26 | `icones/circulo-mais.svg` sem `focusable="false"` | RED-16 | ✅ morto, idem |
| N27 | `icones/lampada.svg` com o conteúdo de `grafico-barras.svg` | RED-16 | ❌ **sobreviveu** |
| N28 | `base.html:46`: ícone depois do texto | RED-16 | ✅ morto, `test_menu_tem_os_tres_itens_em_ordem_cada_um_com_icone_antes_do_texto` |
| N29 | `nav[aria-label=Principal] svg { display: none }` | RED-16 | ✅ morto, `test_folha_so_esconde_o_que_a_spec_manda` |
| N30 | `nav[aria-label=Principal] a { font-size: 1px }` | RED-22 | ❌ **sobreviveu** |

**Regressão** (amostra do catálogo da iteração 1 que tinha morrido):

| # | Resultado |
| - | --------- |
| M01 | ✅ morto, `test_html_marca_o_alto_contraste_so_com_o_cookie_alto` |
| M02 | ✅ morto, `test_menu_marca_a_pagina_atual_ou_a_secao` |
| M05 | ✅ morto, `test_alto_grava_o_cookie_de_um_ano_e_volta_a_pagina` |
| M09 | ✅ morto, `test_voltar_para_fora_do_site_vazio_ou_ausente_vai_a_raiz[externo]` |
| M10 | ✅ morto, `test_contraste_fora_de_alto_e_normal_responde_400_sem_cookie` |
| M13 | ✅ morto, `test_normal_apaga_o_cookie_e_volta_a_pagina` |
| M17 | ✅ morto, `test_500_sem_request_nao_tem_botao_nem_form_do_contraste` |
| M20 | ✅ morto, `test_botao_da_barra_mostra_o_estado_e_pede_o_oposto` |
| M26 | ✅ morto, `test_rodape_tem_a_identificacao_e_os_links_de_apoio[login]` |
| M32 | ✅ morto, `test_separador_da_trilha_e_o_sinal_com_texto_alternativo_vazio` |
| M36 | ✅ morto, `test_reduzir_movimento_desliga_tudo_inclusive_o_esqueleto` |
| M40 | ✅ morto, `test_item_atual_do_menu_tem_fundo_suave_e_barra_azul_de_3px` |
| M44 | ✅ morto, `test_com_o_cookie_alto_a_pagina_traz_a_mesma_folha` |
| M48 | ✅ morto, `test_toda_pagina_faz_preload_da_fonte_na_mesma_url` |

**Result**: reinjeção 5/5 mortos; novos 14/30 mortos (16 sobreviventes); regressão 14/14. FAIL ❌

### Gate Check (it. 2, árvore real)

- `.venv/bin/ruff check .` → All checks passed; `ruff format --check .` → 161 files already formatted; `makemigrations --check --dry-run` → No changes detected; `pytest -q` → **1326 passed**, 0 failed, 0 skipped.

### Gaps restantes (todos lacunas de teste; nenhum defeito de produção)

1. **RED-22, "sem virar só ícone"** (Major): N22 (`width` + `overflow: hidden` no item, em `@media`) e N30 (`font-size: 1px`). A guarda (`inovacoes/tests/test_folha_v2.py:968-995`) só conhece valor zero. Falta exigir que nenhuma regra do item do menu, em nenhum contexto, limite `width`/`max-width` ou mude `font-size` para baixo de um piso.
2. **RED-22, 44px em botões** (Major): N02, N03, N04. `_e_botao` (`test_folha_v2.py:776`) decide pelo texto do seletor e `ALTURA` ignora `max-height`; uma regra que pega o Sair por `.usuario form > *` ou `[type=submit]` baixa a altura sem ser vista.
3. **Regra de teste, `display: none` na folha** (Major): N17, N18. O parser lê nome e valor sem decodificar escapes CSS, e a folha já usa escapes (`\69 `, `\76 `, `\203A`).
4. **Guarda de esconder, vetores fora da lista ou fora da grafia** (Minor): N21 (`clip-path: inset(0 0 100% 0)`, que a própria T19 promete pegar), N07 (`overflow` em outra regra), N19 (opacidade quase zero), N08/N09 (cor transparente ou igual ao fundo), N10/N20 (fora da tela), N11 (`content-visibility`).
5. **RED-16, oráculo autorreferente** (Minor): N27. `test_casca.py:338-350` compara o ícone renderizado com o arquivo de produção; trocar o desenho de `lampada.svg` passa.

Como este era o último ciclo, os gaps ficam como risco registrado para decisão do usuário.

### validate_state.py (it. 2)

`python3 .claude/skills/tlc-spec-driven/scripts/validate_state.py fundacao-do-redesign` → exit 1 (verdict FAIL), como esperado num FAIL.

### Lições (it. 2)

L-052 reafirmada (N22, N30; mesma feature, sem recorrência nova). Novas candidatas: L-054 (alvo de 44px por seletor), L-055 (escapes CSS), L-056 (vetores de esconder), L-057 (oráculo autorreferente).

---

# Iteração 1 (histórico)

**Diff range (it. 1)**: `a3799f7..23b7565` (T1 `083f19d` … T17 `23b7565`; 45 arquivos, +3454/−210)
**Verdict (it. 1)**: FAIL ❌

O código de produção cumpre a casca, o contraste, as páginas de apoio e a folha em quase tudo, e o gate passa (1297 passed). O FAIL vem de 5 mutantes sobreviventes em 50 e de duas cláusulas sem evidência:

1. **RED-22, cláusula "buttons" (44px):** nenhum teste afirma `min-height: 44px` em botões. M42 (`button { min-height: 28px }`) sobrevive. Além disso, `templates/kira.css:389-392` (`.botao--compacto, .usuario button { min-height: 36px }`, anterior à R1) deixa o "Sair" de toda tela autenticada com 36px. Isso contraria a letra da RED-22, e a §5 da design-spec pede o Sair "pequeno". Há conflito na spec e uma AC sem teste.
2. **RED-22, cláusula "without becoming icon-only":** sem evidência. M41 (`@media (max-width: 40rem) { nav[aria-label=Principal] a { font-size: 0 } }`) sobrevive.
3. **RED-16, qual ícone em cada item (lâmpada, círculo com mais, gráfico):** sem evidência. Os testes só exigem *um* `<svg aria-hidden focusable=false>` antes do texto. M43 (gráfico no lugar da lâmpada em "Inovações") sobrevive.
4. **Regra de teste da feature (L-028/L-030, spec:297-299):** a spec diz que o `exibido()` "já cobre CSS `display: none` em seletor da própria folha". O modo rigoroso só lê seletores de **classe simples** (`inovacoes/tests/visibilidade.py:45-54`, `classes_ocultas`). M27 (`.rodape__links li { display: none }`) e M28 (`nav[aria-label=Principal] { display: none }`) sobrevivem: o rodapé perde os links e o menu some da tela com a suíte verde. O design restringiu o escopo (design.md:228-230), mas a spec promete mais. É lacuna de precisão e de discriminação.

---

## Task Completion

| Task | Status | Notes |
| ---- | ------ | ----- |
| T1–T17 | ✅ Done (17/17 marcadas ✅ em `tasks.md`) | Commits `083f19d` … `23b7565` |

---

## Spec-Anchored Acceptance Criteria

Arquivos: `F` = `inovacoes/tests/test_folha_v2.py`, `C` = `nucleo/tests/test_casca.py`, `X` = `nucleo/tests/test_contraste.py`, `P` = `nucleo/tests/test_paginas_apoio.py`, `E` = `config/tests/test_estaticos.py`, `DS` = `inovacoes/tests/test_views_sistema_design.py`.

| AC | Spec-defined outcome | `file:line` + assertion | Result |
| -- | -------------------- | ----------------------- | ------ |
| RED-01 | 11 tokens v2 com valor exato; v1 mantidos | `F:150` `_token(nome) == TOKENS_V2[nome]` (F:131-143, valores da AC); v1: `DS:232` `_token(nome) == TOKENS_DA_SPEC[nome]` | ✅ |
| RED-02 | `.cartao` `border-radius: var(--raio-cartao)`; alfa da sombra ≤ 0.12 | `F:178` regex `border-radius:var(--raio-cartao)`; `F:189-190` `all(alfa <= 0.12)` | ✅ |
| RED-03 | borda `1.5px solid var(--borda-campo)` em input/select/textarea; ≥ 3:1 sobre surface e bg | `F:204` `fullmatch(1.5px solid var(--borda-campo))`; `F:211` `_contraste(...) >= 3` | ✅ |
| RED-04 | `font-variant-numeric: var(--numeros)` nos 7 seletores | `F:232` (parametrizado F:218-229) | ✅ |
| RED-05 | `@font-face` Inter, swap, `400 800`, src literal; `--font-sans` da §3 | `F:72` `_font_face()[prop] == valor` (F:61-69); `DS:232` (`font-sans`) | ✅ |
| RED-06 | collectstatic copia a fonte; URL = `/`+STATIC_URL+caminho | `E:52-53` `copia.is_file()` e bytes iguais; `E:61` `urls == ["/" + STATIC_URL + FONTE]`; `E:44` finder | ✅ |
| RED-07 | `static/fontes/OFL.txt` e `templates/icones/LICENSE` | `E:67-68`; `C:151-154` (ISC/Lucide, MIT/Feather) | ✅ |
| RED-08 | nada de `http(s)://` em link/script/img/@import/url( | `F:101`, `F:109`, `F:112` `not EXTERNO.search(...)` em toda página da fixture | ✅ |
| RED-09 | componentes e estados da §6 | `F:252` hover `--brand-blue-hover`; foco global `DS:241-242` (2px `--brand-blue`); `F:265` `:active` (só "existe declaração"); `F:275-278` desabilitado (bg, text-muted, not-allowed, sem opacity); `F:300` `[aria-\69 nvalid=true]` 2px error; `F:306` selo pílula; `F:349` cartão de inovação hover; `F:363-378` etapas; `F:385-395` linha do tempo; `F:401` contato 4px; `F:414-424` grupo; `F:505-516` etiqueta e "×"; `F:533-534` resumo; `F:540` barra de ações; `F:548-573` indicador e variação; `F:579-582` esqueleto | ⚠️ `:active` sem valor na §6 ("ativo"): lacuna de precisão da spec; o resto ✅ |
| RED-10 | só pares da §2 v2, 4.5:1 texto / 3:1 componente | `F:488-493`, `F:605-606`, `F:713-718`, `F:755-761` (par na lista aprovada **e** razão); `F:321`, `F:616` | ⚠️ lacunas de precisão já registradas pelo Execute: hover do "×" (`--brand-navy` sobre `--border`) fora da §2 (`F:525-526` exige 3:1); fundo de cada componente assumido (surface/bg) |
| RED-11 | reduzir movimento desliga transições e animações, inclusive `.esqueleto` | `F:625-635` bloco `@media (prefers-reduced-motion: reduce)` com `*` e `transition/animation: none !important` | ✅ |
| RED-12 | sem `position: fixed`; nenhuma largura > 320px fora de max-width | `F:666` `not re.search(position:fixed)`; `F:682` `largas == []` | ⚠️ isenção `.tabela table` (WCAG 1.4.10, tabelas), já registrada no Execute |
| RED-13 | nav de atalhos antes do header; 1º link = pular, accesskey 1, `kbd aria-hidden` 1; primeiro focável | `C:191-197` (exibido rigoroso, toda página da fixture, inclusive a 500) | ✅ |
| RED-14 | autenticado: atalho 2 `#menu`, 3 `#id_q` na lista ou `/inovacoes/#id_q` fora | `C:216-222`; `C:112` | ✅ |
| RED-15 | anônimo sem accesskey 2/3 | `C:229-231` | ✅ |
| RED-16 | `nav#menu` "Principal", 3 itens em ordem, ícone lâmpada / círculo com mais / gráfico `aria-hidden focusable=false` antes do texto | `C:287` ordem e texto; `C:294-298` "um svg aria-hidden antes do texto"; `C:125` pasta tem os 4 nomes | ❌ cláusula "qual ícone em cada item" sem evidência (M43 sobrevive) |
| RED-17 | `aria-current="page"` só no destino exato | `C:330` `{texto: corrente} == atual` (lista, cadastro, painel); `C:345-346`, `P:184-185`, `P:244` nenhum fora | ✅ |
| RED-18 | `aria-current="true"` só em Inovações na seção (inclusive 404 e 403) | `C:330` (detalhe, editar, excluir, status, reaproveitar, 999999 → 404, terceiro → 403) | ✅ |
| RED-19 | item atual: fundo `--info-tint`, barra 3px `--brand-blue` | `F:747-748` | ✅ |
| RED-20 | nome completo (ou username) em `<span>` sem atributo, depois do menu; iniciais `aria-hidden`; Sair | `C:365` iniciais `aria-hidden`; `C:368-373` nome exibido antes do Sair, `</nav>` antes da área | ✅ |
| RED-21 | faixa 4px `--brand-gradient`, sem texto, `aria-hidden`, entre a barra e o header | `C:237-241`; `F:733-734` | ✅ |
| RED-22 | itens quebram linha sem virar só ícone; 44px em itens do menu, links da barra **e botões** | `F:767-768` flex-wrap e 44px no menu; `F:726` 44px na barra | ❌ botões sem evidência (M42 sobrevive; `.usuario button` 36px em `templates/kira.css:389-392`); "sem virar só ícone" sem evidência (M41 sobrevive) |
| RED-23 | form `#form-contraste` POST no fim do body com CSRF e `voltar_para` (caminho+query); botão "Alto contraste" com ícone, `form=`, `name`, valor oposto, `aria-pressed` | `X:216-223` (exibido rigoroso); `X:250-263`; `X:132-136` token válido | ✅ |
| RED-24 | POST alto → cookie `alto`, 1 ano, HttpOnly, Lax, Secure sem DEBUG; 302 para `voltar_para` | `X:45-48`; `X:56` | ✅ |
| RED-25 | normal → apaga o cookie; 302 | `X:66-73` (valor vazio, max-age 0, tema normal depois) | ✅ |
| RED-26 | cookie `alto` → `<html lang="pt-br" data-contraste="alto">` na 1ª resposta, sem script | `X:175-176`; `F:894` | ✅ |
| RED-27 | tema alto redefine cada token com o valor da §2 v2; pares seguem nos limites | `F:832`, `F:838` (bloco == TOKENS_ALTO); `F:845`, `F:852` | ✅ |
| RED-28 | no tema: links sublinhados; `.decorativo` e faixa somem; selo/alerta/variação/barras com borda 1px na cor do texto | `F:858`; `F:865-867`; `F:874`; `F:881-883` | ✅ |
| RED-29 | trilha entre header e main; main abre com status e depois cabeçalho de página (titulo, descricao, acao_principal) | `C:485`; `C:408-410`; `C:435-440` | ✅ |
| RED-30 | trilha nas telas da §5.3 e na Ajuda; ol, intermediários com link, último com `aria-current="page"`; "›" por CSS | `C:533` (8 telas); `P:72` (Acessibilidade); `P:213` (Ajuda); `C:539`; `C:545-546`; `F:777-783` decodifica o escape | ✅ |
| RED-31 | h1 pelo bloco `titulo`, texto de hoje, um por página; login mantém "Entrar" no cartão | `C:407-410`; `C:416-420` | ✅ |
| RED-32 | footer com o texto atual e links Acessibilidade e Ajuda | `C:592-600` (16 páginas, exibido rigoroso); `C:585` lista == fixture | ✅ |
| RED-33 | `/acessibilidade/` 200, trilha, h1, 5 h2 em ordem | `P:72-77`; `P:84-86` | ✅ |
| RED-34 | tabela com caption, `th scope`, 3 atalhos × combinações; aviso de conflito | `P:137-145`; `P:158-164`; `P:171` | ✅ |
| RED-35 | `/ajuda/` 200, h1, 4 h2 | `P:213-216`; `P:223`; `P:231` | ⚠️ texto das seções não fixado na spec (≥ 5 palavras exibidas), já registrado no Execute |
| RED-36 | anônimo: header só com a marca | `P:48-50` (anônimo nas duas páginas) | ✅ |
| RED-37 | `voltar_para` ausente, vazio ou externo → `/` | `X:92-94` (externo, `//`, vazio, ausente) | ✅ |
| RED-38 | `contraste` ausente ou inválido → 400, cookie inalterado | `X:105-109` | ✅ |
| RED-39 | GET → 405; sem CSRF → 403 | `X:115`; `X:123-124` | ✅ |
| RED-40 | outro valor do cookie → tema normal e `aria-pressed="false"` | `X:175` (ALTO, sim, vazio); `X:221` (`escuro` → false); `C:97` | ✅ |
| RED-41 | 500 sem request: atalho 1, faixa, marca, folha; sem form | `C:248-250`; `X:279-283`; marca e folha pela fixture (`DS:107`, `DS:161`, inclui `erro_500`) | ✅ |
| RED-42 | mesmo valor duas vezes → mesma resposta | `X:148-151` | ✅ |

**Status**: ❌ 38/42 ACs com o valor da spec afirmado. RED-16 e RED-22 têm cláusulas sem evidência. RED-09, RED-10, RED-12 e RED-35 têm lacunas de precisão da spec, sinalizadas e não reprovadas.

---

## Discrimination Sensor

Nível ampliado: casca usada em todas as telas. Worktree isolada em `HEAD=23b7565` no scratchpad. A suíte inteira rodou com `-x` por mutante, e o arquivo foi restaurado por `git checkout` depois de cada um. Antes dos mutantes, a worktree deu 1297 passed. Depois, a worktree foi removida e o `git worktree prune` rodou. O `git status --porcelain` da árvore real ficou igual ao de antes (` M .specs/LESSONS.md`, ` M .specs/lessons.json`).

| # | Alvo | Mutação | Resultado (primeiro teste que falhou) |
| - | ---- | ------- | ------------------------------------- |
| M01 | `nucleo/context_processors.py:25` | qualquer valor do cookie liga o tema (RED-40) | ✅ morto, `test_html_marca_o_alto_contraste_so_com_o_cookie_alto` |
| M02 | `context_processors.py:20` | seção marca `page` em vez de `true` (RED-18) | ✅ morto, `test_menu_marca_a_pagina_atual_ou_a_secao` |
| M03 | `context_processors.py:7` | cadastro sai da tabela (RED-17) | ✅ morto, idem |
| M04 | `context_processors.py:29` | atalho 3 sempre `/inovacoes/#id_q` (RED-14) | ✅ morto, `test_autenticado_tem_os_atalhos_do_menu_e_da_busca` |
| M05 | `nucleo/views.py:37` | `max_age` de 1 mês (RED-24) | ✅ morto, `test_alto_grava_o_cookie_de_um_ano_e_volta_a_pagina` |
| M06 | `views.py:38` | sem HttpOnly | ✅ morto, idem |
| M07 | `views.py:39` | SameSite=Strict | ✅ morto, idem |
| M08 | `views.py:41` | Secure sempre | ✅ morto, `test_secure_do_cookie_segue_o_debug_desligado` |
| M09 | `views.py:28-30` | aceita `voltar_para` externo (RED-37) | ✅ morto, `test_voltar_para_fora_do_site_vazio_ou_ausente_vai_a_raiz[externo]` |
| M10 | `views.py:23` | valor inválido vira "normal" (RED-38) | ✅ morto, `test_contraste_fora_de_alto_e_normal_responde_400_sem_cookie` |
| M11 | `views.py:15` | sem `@require_POST` (RED-39) | ✅ morto, `test_get_na_rota_de_contraste_responde_405` |
| M12 | `views.py:33` | alterna pelo cookie em vez do valor (RED-42) | ✅ morto, `test_mesmo_post_duas_vezes_responde_igual[alto]` |
| M13 | `views.py:44` | "normal" grava cookie em vez de apagar (RED-25) | ✅ morto, `test_normal_apaga_o_cookie_e_volta_a_pagina` |
| M14 | `templates/base.html:94` | form do contraste antes do footer (AD-015) | ✅ morto, `test_botao_da_barra_mostra_o_estado_e_pede_o_oposto` |
| M15 | `base.html:20` | atalhos 2/3 para anônimo (RED-15) | ✅ morto, `test_anonimo_so_tem_o_atalho_do_conteudo` |
| M16 | `base.html:47` | `aria-current` em dois itens (RED-17) | ✅ morto, `test_menu_marca_a_pagina_atual_ou_a_secao` |
| M17 | `base.html:30` | botão sem `{% if request %}` (RED-41) | ✅ morto, `test_500_sem_request_nao_tem_botao_nem_form_do_contraste` |
| M18 | `base.html:31` | `aria-pressed` fixo "false" (RED-23) | ✅ morto, `test_botao_da_barra_mostra_o_estado_e_pede_o_oposto` |
| M19 | `base.html:109` | `voltar_para` sem query (RED-23) | ✅ morto, `test_form_do_contraste_e_o_ultimo_do_body_so_com_csrf_e_voltar_para` |
| M20 | `base.html:26` | `hidden` no ancestral do botão e do link Acessibilidade | ✅ morto, `test_botao_da_barra_mostra_o_estado_e_pede_o_oposto` |
| M21 | `base.html:97` | `inert` no `ul` do rodapé | ✅ morto, `test_rodape_tem_a_identificacao_e_os_links_de_apoio` |
| M22 | `templates/paginas/trilha.html:7` | `aria-hidden` no ancestral da trilha | ✅ morto, `test_tela_mostra_a_trilha_da_tabela` |
| M23 | `base.html:45` | menu dentro de `<details>` fechado | ✅ morto, `test_cabecalho_autenticado_leva_ao_painel_depois_do_cadastro` (T-A) |
| M24 | `base.html:99` | link Ajuda em comentário HTML | ✅ morto, `test_rodape_tem_a_identificacao_e_os_links_de_apoio` |
| M25 | `base.html:31` | botão de contraste `disabled` | ✅ morto, `test_botao_da_barra_mostra_o_estado_e_pede_o_oposto` |
| M26 | `templates/kira.css` (fim) | `.rodape__links { display: none }` | ✅ morto, `test_rodape_tem_a_identificacao_e_os_links_de_apoio` |
| M27 | `kira.css` (fim) | `.rodape__links li { display: none }` (seletor composto) | ❌ **sobreviveu** |
| M28 | `kira.css` (fim) | `nav[aria-label=Principal] { display: none }` (seletor de atributo) | ❌ **sobreviveu** |
| M29 | `base.html:45` | `role="presentation"` no menu | ✅ morto, `test_menu_tem_os_tres_itens_em_ordem_cada_um_com_icone_antes_do_texto` |
| M30 | `base.html:19` | `<template>` + `hidden` no atalho 1 | ✅ morto, `test_primeiro_focavel_exibido_e_o_atalho_1_na_barra` |
| M31 | `trilha.html:11` | último item sem `aria-current` (RED-30) | ✅ morto, `test_tela_mostra_a_trilha_da_tabela` |
| M32 | `kira.css:283` | escape do separador `\203A` → `\203B` | ✅ morto, `test_separador_da_trilha_e_o_sinal_com_texto_alternativo_vazio` |
| M33 | `kira.css:452` | `[aria-\69 nvalid=true]` → `[aria-\6a nvalid=true]` | ✅ morto, `test_campo_invalido_tem_borda_de_2px_de_erro[input]` |
| M34 | `kira.css:755` | `.cartao-ino\76 acao` → `.cartao-ino\77 acao` | ✅ morto, `test_cartao_de_inovacao_em_hover_ganha_borda_azul` |
| M35 | `kira.css:1018` | `--on-brand` do tema alto → `#FFFFFF` (par amarelo/branco) | ✅ morto, `test_tema_alto_redefine_o_token_com_o_valor_exato[on-brand]` |
| M36 | `kira.css:1054` | reduzir movimento sem `animation: none` (RED-11) | ✅ morto, `test_reduzir_movimento_desliga_tudo_inclusive_o_esqueleto` |
| M37 | `kira.css` (fim) | `.barra-acoes { position: fixed }` (RED-12) | ✅ morto, `test_barra_de_acoes_tem_o_fundo_da_pagina_e_nao_fica_presa_na_tela` |
| M38 | `kira.css:37` | `--borda-campo` claro, abaixo de 3:1 | ✅ morto, `test_root_declara_o_token_v2_com_o_valor_exato[borda-campo]` |
| M39 | `kira.css:1031` | link sem sublinhado no tema (RED-28) | ✅ morto, `test_links_ficam_sublinhados_no_tema_alto` |
| M40 | `kira.css:234` | barra do item atual de 1px (RED-19) | ✅ morto, `test_item_atual_do_menu_tem_fundo_suave_e_barra_azul_de_3px` |
| M41 | `kira.css` (fim) | `@media (max-width: 40rem)` menu `font-size: 0`, só ícone (RED-22) | ❌ **sobreviveu** |
| M42 | `kira.css` (fim) | `button { min-height: 28px }` (RED-22) | ❌ **sobreviveu** |
| M43 | `base.html:46` | ícone de gráfico em "Inovações" (RED-16) | ❌ **sobreviveu** |
| M44 | `base.html:2` | `data-contraste="sim"` (RED-26) | ✅ morto, `test_com_o_cookie_alto_a_pagina_traz_a_mesma_folha` |
| M45 | `base.html:53` | iniciais sem `aria-hidden` (RED-20) | ✅ morto, `test_area_do_usuario_mostra_o_nome_e_as_iniciais_decorativas` |
| M46 | `base.html:67-69` | trilha dentro do `main` (RED-29, AD-015) | ✅ morto, `test_avancar_status_so_tem_controles_nativos` |
| M47 | `base.html:19` | `kbd` 1 sem `aria-hidden` (RED-13) | ✅ morto, `test_primeiro_focavel_exibido_e_o_atalho_1_na_barra` |
| M48 | `nucleo/views.py:55` | Ajuda deixa de ser pública (RED-35/36) | ✅ morto, `test_toda_pagina_faz_preload_da_fonte_na_mesma_url` |
| M49 | `templates/paginas/acessibilidade.html:48` | combinação do Firefox errada (RED-34) | ✅ morto, `test_cada_atalho_tem_a_combinacao_de_cada_navegador` |
| M50 | `base.html:98` | link do rodapé com destino errado (RED-32) | ✅ morto, `test_rodape_tem_a_identificacao_e_os_links_de_apoio` |

**Sensor depth**: ampliado (50 mutantes: processor, view, base, trilha, páginas de apoio, folha, visibilidade e escapes)
**Result**: 45/50 mortos, 5 sobreviventes. FAIL ❌

Os vetores de visibilidade do HTML (`hidden`, `inert`, `aria-hidden` no ancestral, comentário, `<template>`, `<details>` fechado, `disabled`, `role="presentation"`) e o CSS em classe simples morrem. Sobrevive o CSS `display: none` em seletor composto ou de atributo. Um `display` em SVG não foi exercitado como vetor de visibilidade: os ícones já são `aria-hidden` e o texto do link fica fora deles. Os três escapes da folha (`\69 `, `\76 `, `\203A`) discriminam: um seletor quebrado falha.

---

## Testes antigos alterados

Arquivos de teste que já existiam em `a3799f7` e mudaram em `a3799f7..23b7565`:

| Arquivo | Mudança | Autorização | Perdeu asserção? |
| ------- | ------- | ----------- | ---------------- |
| `inovacoes/tests/test_views_cabecalho.py` | `LINK`, `LINK_INOVACOES` e `LINK_INDICADORES` viram `Link(href, texto exibido)`; `_navegacao_principal` acha o `nav` por regex de atributos; REAP-28 compara `_links(...)` | T-A | Não. Ver a nota abaixo. |
| `contas/tests/test_controle_acesso.py:21` | `ROTAS_PUBLICAS` ganha 3 rotas | T-B | Não |
| `inovacoes/tests/test_views_sistema_design.py` | `len(telas) == 13`; `PECAS` + `paginas/trilha.html` | T-C | Não |
| idem, fixture `paginas` | + acessibilidade e ajuda (anônimo e autenticado) | T-D | Não (amplia) |
| `indicadores/tests/test_views_painel.py:178` | `"<svg" not in` só no `<main>` | T-E | Não |
| `inovacoes/tests/test_views_sistema_design.py:185` | `<span>Ana Souza</span>` | T-F | Não |
| `config/tests/test_estaticos.py` | só acréscimos (4 testes novos, RED-05 a RED-07) | testes novos em escopo | Não |
| `inovacoes/tests/visibilidade.py` (helper, não teste) | modo `rigoroso=True` aditivo; o padrão não muda (`test_visibilidade.py:48-49`) | T1 | Não |

Só T-A a T-F mudaram. **T-A / REAP-28:** antes se comparava a string do `nav` crua com a do `nav` exibido, e qualquer trecho escondido dentro do `nav` reprovava. Agora se compara a lista `(href, texto exibido)` dos links. Isso é mais estreito só para conteúdo do `nav` que não é link, e o menu não tem nenhum. Um link escondido ou fora do exibido continua reprovando: M23 (`<details>`) morre justamente nesse teste. Não enfraquece o que a REAP-28 afirma. A comparação usa o `exibido()` padrão, mas o `test_casca.py` cobre o menu com o modo rigoroso (M29 morre).

---

## Gate Check

- **Gate command**: `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q`
- **Result**: ruff: All checks passed. Format: 160 files already formatted. Migrations: No changes detected. **1297 passed**, 0 failed, 0 skipped.
- **Test count before feature** (`a3799f7`, mesma worktree): 943
- **Test count after feature**: 1297
- **Delta**: +354

---

## Code Quality

| Principle | Status |
| --------- | ------ |
| Minimum code / surgical changes | ✅ |
| No scope creep | ✅ (ajustes fora da letra registrados em design.md, lotes 1–3) |
| Matches patterns (AD-006, AD-010, AD-013–AD-015) | ✅ |
| Spec-anchored outcome check | ❌ RED-16 e RED-22 incompletos |
| Every test maps to a spec requirement | ✅ |

---

## Fix Plans

### Fix 1: RED-22, 44px em botões (Major)

- **Root cause**: nenhum teste da folha afirma `min-height: 44px` em `button`/`.botao`. `.botao--compacto, .usuario button { min-height: 36px }` (`templates/kira.css:389-392`) contradiz a letra da AC. A §5 da design-spec pede o Sair "pequeno".
- **Fix task**: decidir com o usuário (emendar a RED-22 para isentar o compacto, ou subir o Sair a 44px). Depois, um teste `unit` em `test_folha_v2.py` que exija `min-height: 44px` em `button`, `.botao` e `.barra-acessibilidade button` e que nenhuma regra de botão declare menos que isso, salvo a isenção acordada.

### Fix 2: RED-22, não virar só ícone (Minor)

- **Fix task**: teste da folha que, em toda `@media`, nenhuma regra sobre `nav[aria-label=Principal] a` (ou descendentes de texto) zere `font-size`, esconda o texto ou mude `display` do rótulo.

### Fix 3: RED-16, ícone certo em cada item (Minor)

- **Fix task**: em `test_casca.py`, comparar o SVG de cada item do menu com o conteúdo de `templates/icones/{lampada,circulo-mais,grafico-barras}.svg`, na ordem do MENU. Fazer o mesmo com `contraste.svg` no botão da barra (RED-23, "half-circle icon").

### Fix 4: `exibido(rigoroso=True)` e `display: none` em seletor composto ou de atributo (Major, transversal)

- **Root cause**: `classes_ocultas` (`inovacoes/tests/visibilidade.py:45-54`) só reconhece `.classe` simples. A regra de teste da spec (spec.md:297-299) promete "display: none em seletor da própria folha".
- **Fix task**: emendar a regra da spec ao escopo real, ou acrescentar um teste de folha que proíba `display: none` (e `visibility: hidden`) fora de classe simples, `@media` aprovada e `[data-contraste=alto] .decorativo`/`.faixa-marca`. Assim, M27 e M28 passam a falhar na folha.

---

## Summary

**Overall**: ❌ Not Ready

**Spec-anchored check**: 38/42 ACs ok. RED-16 e RED-22 têm cláusulas sem evidência. 4 lacunas de precisão da spec (RED-09 `:active`, RED-10, RED-12, RED-35).
**Sensor**: 45/50 mortos (M27, M28, M41, M42, M43 sobrevivem)
**Gate**: 1297 passed
**Testes antigos**: só T-A a T-F, sem perda de asserção

**What works**: rota e cookie do contraste (todas as edges RED-37 a RED-42), página atual do menu, atalhos, ordem do DOM da AD-015, trilha, páginas de apoio, tokens e pares do tema alto, escapes da folha e todos os vetores de visibilidade no HTML.

---

## validate_state.py

`python3 .claude/skills/tlc-spec-driven/scripts/validate_state.py fundacao-do-redesign` → exit 1 (`validation.md verdict is FAIL`), como esperado num FAIL.

## Lições

L-044 recorreu (M27, M28) e foi promovida a confirmed. Novas candidatas: L-050 (RED-16), L-051 (RED-22, botões), L-052 (RED-22, só ícone) e L-053 (RED-09, `:active`).
