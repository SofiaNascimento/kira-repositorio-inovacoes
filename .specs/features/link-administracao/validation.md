# Link da Administração Validation

**Date**: 2026-11-23
**Spec**: `.specs/features/link-administracao/spec.md`
**Diff range**: `c22cc1e..0b6fef1` (46c8ca8 spec, 6bfe0a9 ícone, a53814f link no cabeçalho, 0b6fef1 título/site_url do admin; 0b6fef1 é o amend só de mensagem de 300952f, mesma árvore `19e2305`)
**Verifier**: independent sub-agent (author ≠ verifier)

**Verdict**: FAIL

---

## Task Completion

Escopo Small/Medium, sem tasks.md (plano inline). Os 4 commits do diff cobrem as 7 requisições
(ADM-01..ADM-07); nenhuma parcial.

---

## Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --------- | -------------------- | ----------------------- | ------ |
| ADM-01: ADMINISTRADOR vê "Administração" → `/admin/` na área do usuário, antes do Sair, em toda página interna | texto exato "Administração", `href="/admin/"`, dentro de `div.usuario`, depois do nome e antes do Sair, exibido | `inovacoes/tests/test_link_administracao.py:65` - `[_texto(exibido(conteudo)) ...] == [TEXTO]` (DOM `exibido(rigoroso=True)` do `<header>`); `:71` - `nome.end() < link.start() < sair.start()`; parametrizado em 8 páginas internas (`:23-32`) | ❌ GAP - o "exibido" não alcança o CSS: `.usuario a { display: none }` e `visibility: hidden` sobrevivem (M17, M18; L-044) |
| ADM-02: USUARIO (com ou sem `is_staff`) não tem link para `/admin/` | nenhum `href="/admin/` no HTML | `test_link_administracao.py:82` - `f'href="{ADMIN}' not in ...` (USUARIO comum, 8 páginas); `:90` - idem para `nao_autor_usuario` [terceiro, staff, superusuario] (`inovacoes/tests/conftest.py:60-73`) | ✅ PASS |
| ADM-03: sem sessão, nenhum link para `/admin/` | nenhum `href="/admin/` no HTML | `test_link_administracao.py:99` - `f'href="{ADMIN}' not in ...` em `/entrar/`, `/acessibilidade/`, `/ajuda/` | ✅ PASS |
| ADM-04: ícone `aria-hidden="true"`; nome acessível exatamente "Administração" | SVG com `aria-hidden="true"`, `<a>` sem `aria-label`/`aria-labelledby`/`title`, texto exibido == "Administração" | `test_link_administracao.py:113` - `not {"aria-label","aria-labelledby","title"} & set(atributos)`; `:118` - `aria-hidden == "true"`; `:119` - formas == `engrenagem.svg`; `:120` - `_texto(exibido(conteudo)) == TEXTO` | ✅ PASS |
| ADM-05: `/admin/` mostra "KIRA — Administração" e "Ver o site" → `/inovacoes/` | `#site-name` == "KIRA — Administração"; único "Ver o site" com `href="/inovacoes/"` | `test_link_administracao.py:169` - `_texto(marca.group(1)) == "KIRA — Administração"`; `:175` - `ver_o_site == ["/inovacoes/"]` | ✅ PASS |
| ADM-06: ADMINISTRADOR rebaixado deixa de ver o link na próxima página | link presente antes; ausente na próxima página da mesma sessão | `test_link_administracao.py:126` - link presente; `:130` - `f'href="{ADMIN}' not in html` após `update(perfil=USUARIO)` (is_staff continua True) | ✅ PASS |
| ADM-07: no alto contraste, o link usa os pares de cor dos links da casca | nenhuma regra de cor/fundo/sublinhado própria para o link; vale `a` e `:root[data-contraste=alto] a` | `test_link_administracao.py:155` - `not COR.search(corpo)` para as regras de `_regras_que_alcancam_o_link()` (`:133-141`); `:157-158` - regras da casca presentes | ❌ GAP - `_regras_que_alcancam_o_link` só reconhece os seletores `.usuario a` / `.usuario > a` literais; `header .usuario a { color }` (M19) e `:root[data-contraste=alto] .usuario a { text-decoration: none }` (M20) sobrevivem |

**Status**: ❌ Gaps present (ADM-01, ADM-07). Sem spec-precision gap: todas as ACs têm resultado preciso.

### Verificações pedidas pelo orquestrador

- Condição do link: `templates/base.html:56` - `{% if user.is_administrador %}`; nenhum `is_staff` no diff de template. ✅
- Ícone: `templates/icones/engrenagem.svg:2` tem exatamente o `d` do Lucide `settings` informado, e `:3` `<circle cx="12" cy="12" r="3"/>`; só 2 formas. Conferido por comparação de string. ✅ (o teste não fixa isso, ver M22)
- `nucleo/tests/test_casca.py:137-143`: única mudança é acrescentar `engrenagem` à lista esperada, como a spec autoriza. ✅
- DS-05 (`inovacoes/tests/test_views_sistema_design.py`): sem diff em `c22cc1e..0b6fef1`, e os testes passam. ✅

---

## Discrimination Sensor

Worktree temporária em `0b6fef1`/`300952f` (mesma árvore) no scratchpad, com o `.venv` do repo
principal e o `.env` copiado. Testes executados: `test_link_administracao.py`, `nucleo/tests/test_casca.py`,
`test_views_sistema_design.py`, `contas/tests` (311 verdes sem mutação).

| Mutation | File:line | Description | Killed? |
| -------- | --------- | ----------- | ------- |
| M01 | `templates/base.html:56` | `user.is_administrador` → `user.is_staff` | ✅ Killed (`:90` [staff]) |
| M02 | `templates/base.html:56` | → `user.is_authenticated` | ✅ Killed (`:82`) |
| M03 | `templates/base.html:56` | → `is_administrador or user.is_superuser` | ✅ Killed (`:90` [superusuario]) |
| M04 | `templates/base.html:55-58` | link movido para depois do `</form>` do Sair | ✅ Killed (`:71`) |
| M05 | `templates/base.html:55-58` | link movido para antes do nome | ✅ Killed (`:71`) |
| M06 | `templates/icones/engrenagem.svg:1` | SVG sem `aria-hidden="true"` | ✅ Killed (`:118`) |
| M07 | `templates/base.html:57` | `aria-label="Admin"` no `<a>` | ✅ Killed (`:113`) |
| M08 | `templates/base.html:57` | `title="Administração"` no `<a>` | ✅ Killed (`:113`) |
| M09 | `templates/base.html:57` | link dentro de `<span aria-hidden="true">` | ✅ Killed (`:65`) |
| M10 | `templates/base.html:57` | link dentro de `<span hidden>` | ✅ Killed (`:65`) |
| M11 | `config/urls.py:26` | `site_url = "/"` | ✅ Killed (`:175`) |
| M12 | `config/urls.py:23` | `site_header` trocado | ✅ Killed (`:169`) |
| M13 | `templates/kira.css:258` | `.usuario a { color: #ff0000; }` | ✅ Killed (`:155`) |
| M14 | `templates/base.html:57` | `href` → `/admin/login/` | ✅ Killed (`:65`) |
| M15 | `templates/base.html:57` | texto → "Admin" | ✅ Killed (`:65`) |
| M16 | `templates/base.html:57` | ícone trocado por `lupa.svg` | ✅ Killed (`:119`) |
| M17 | `templates/kira.css:258` | `.usuario a { display: none; }` | ❌ Survived |
| M18 | `templates/kira.css:258` | `.usuario a { visibility: hidden; }` | ❌ Survived |
| M19 | `templates/kira.css:258` | `header .usuario a { color: #ff0000; }` | ❌ Survived |
| M20 | `templates/kira.css:258` | `:root[data-contraste=alto] .usuario a { text-decoration: none; }` | ❌ Survived |
| M21 | `templates/base.html:57` | ícone depois do texto | ✅ Killed (`:115`) |
| M22 | `templates/icones/engrenagem.svg:2` | `d` do path alterado (`M9.671` → `M9.0`) | ❌ Survived (o teste compara o HTML com o próprio arquivo; nenhuma AC fixa o desenho) |

**Sensor depth**: lightweight ampliado (22 mutações, todos os ramos novos)
**Result**: 17/22 killed - FAIL ❌

---

## Code Quality

| Principle | Status |
| --------- | ------ |
| Minimum code | ✅ (4 linhas de template, 4 de config, 9 de CSS, 1 ícone) |
| Surgical changes | ✅ |
| No scope creep | ✅ (`site_title`/`index_title` estão nas decisões aprovadas da spec) |
| Matches patterns | ✅ (ícone no padrão RED-16, comentários com IDs de requisito) |
| Spec-anchored outcome check | ✅ valores exatos ("Administração", `/admin/`, "KIRA — Administração", `/inovacoes/`) |
| Per-layer Coverage Expectation | ❌ ADM-01 e ADM-07: asserções não discriminam ocultação/troca de cor por CSS |
| Every test maps to a spec requirement | ✅ cada teste nomeia sua ADM no docstring |
| Documented guidelines followed: `.specs/LESSONS.md` (L-003, L-028, L-030, L-044) | ⚠️ L-003/L-028/L-030 aplicadas; L-044 citada na spec mas não aplicada (M17/M18) |

Lint: `ruff check .` - All checks passed; `ruff format --check .` - 177 files already formatted.

---

## Edge Cases

- [x] Rebaixamento (ADM-06): tratado e testado (`:123-130`).
- [ ] Alto contraste (ADM-07): o código está correto hoje (`templates/kira.css:261-267` não mexe em cor), mas o teste só pega uma regra com o seletor literal `.usuario a`.

---

## Gate Check

- **Gate command**: `.venv/bin/python -m pytest -q -p no:cacheprovider`
- **Result**: 1594 passed, 0 failed, 0 skipped (72.7s)
- **Test count**: 1594 esperados, 1594 obtidos; 26 casos em `test_link_administracao.py`
- **Skipped tests**: nenhum
- **Failures**: nenhuma

---

## Fix Plans

### Fix 1: ADM-01 não percebe o link escondido pelo CSS (M17, M18) - Major

- **Root cause**: `exibido(rigoroso=True)` só considera `display: none` em seletor de classe simples; `.usuario a` não entra. O teste de ADM-01 não confere as regras da folha que alcançam o link (L-044).
- **Fix task**: em `inovacoes/tests/test_link_administracao.py`, afirmar que nenhuma regra da `kira.css` que alcança o link (incluindo `@media` e `[data-contraste=alto]`) declara `display: none`, `visibility: hidden` ou `opacity: 0`.
- **Done when**: M17 e M18 são mortos; a suíte continua verde.

### Fix 2: ADM-07 só reconhece o seletor literal `.usuario a` (M19, M20) - Major

- **Root cause**: `_regras_que_alcancam_o_link` (`:133-141`) usa `re.fullmatch(r"\.usuario\s+(?:>\s*)?a(?::[\w-]+)?")`, então um seletor com prefixo (`header .usuario a`, `:root[data-contraste=alto] .usuario a`) passa sem ser checado.
- **Fix task**: considerar todo seletor cujo último composto é `a` (com pseudo-classe opcional) e que contém `.usuario` como ancestral, inclusive com prefixo `:root[data-contraste=alto]` e dentro de `@media`.
- **Done when**: M19 e M20 são mortos; M13 continua morto.

### Fix 3 (Minor): o desenho do ícone não é fixado (M22)

- **Root cause**: `:119` compara o SVG renderizado com `engrenagem.svg`, então o teste aceita qualquer mudança no arquivo.
- **Fix task**: fixar no teste o `d` do Lucide `settings` e o `circle cx=12 cy=12 r=3`.
- **Done when**: M22 é morto.

---

## Requirement Traceability Update

| Requirement | Previous Status | New Status |
| ----------- | --------------- | ---------- |
| ADM-01 | Implemented | ❌ Needs Fix (test) |
| ADM-02 | Implemented | ✅ Verified |
| ADM-03 | Implemented | ✅ Verified |
| ADM-04 | Implemented | ✅ Verified (Minor: M22) |
| ADM-05 | Implemented | ✅ Verified |
| ADM-06 | Implemented | ✅ Verified |
| ADM-07 | Implemented | ❌ Needs Fix (test) |

---

## Summary

**Overall**: ❌ Not Ready (tests only; no production defect found)

**Spec-anchored check**: 5/7 ACs matched with discriminating tests; 0 spec-precision gaps
**Sensor**: 17/22 mutations killed
**Gate**: 1594 passed; ruff clean

**What works**: perfil-only condition (`is_administrador`), order name → link → Sair, decorative icon and accessible name, admin header and "Ver o site", demotion on next page, the icon matches Lucide `settings`.

**Issues found**: CSS hiding of the link (ADM-01) and prefixed CSS selectors overriding link colors (ADM-07) go undetected; the icon drawing is not pinned.

**Next steps**: route Fix 1 and Fix 2 (and optionally Fix 3) to the implementer, then re-verify. Alternatively, close with the risk on record, since the production code is correct.

---

## Decisão do usuário (2026-11-23)

**Risco residual aceito; feature fechada sem iteração 2.** O usuário escolheu fechar após a
iteração 1, sem corrigir os testes. O veredito FAIL fica mantido como registro. O código de
produção está conforme às 7 ACs; o risco está só na capacidade dos testes de flagrar regressão:

- ADM-01 (M17, M18): uma regra da folha que esconda o link (`display: none`, `visibility: hidden`) passa.
- ADM-07 (M19, M20): regra de cor ou sublinhado com seletor prefixado, do tema alto ou em `@media` passa.
- ADM-04 (M22, menor): o desenho do ícone não está fixado contra o Lucide no teste (conferido à mão).

As correções (Fix 1 a Fix 3 acima) ficam como ideia adiada. ADM-01, ADM-04 e ADM-07 ficam
`Implementing (risco residual aceito)`; ADM-02, ADM-03, ADM-05 e ADM-06 `Verified`.
`validate_state.py` sai com 1 de propósito.
