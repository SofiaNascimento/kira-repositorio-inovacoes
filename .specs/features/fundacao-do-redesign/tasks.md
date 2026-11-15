# Fundação do Redesign (R1) — Tasks

## Execution Protocol (MANDATORY -- do not skip)

Implement these tasks with the `tlc-spec-driven` skill: **activate it by name and follow its Execute flow and Critical Rules.** Do not search for skill files by filesystem path. The skill is the source of truth for the full flow (per-task cycle, sub-agent delegation, adequacy review, Verifier, discrimination sensor).

**If the skill cannot be activated, STOP and tell the user - do not proceed without it.**

---

**Spec**: `.specs/features/fundacao-do-redesign/spec.md`
**Design**: `.specs/features/fundacao-do-redesign/design.md` (aprovado em 2026-11-15)
**Status**: In Progress — aprovadas em 2026-11-15; Execute por 3 sub-agentes (um por fase). Lote 1 (T1–T6) ✅, 1062 testes; lote 2 (T7–T12) ✅, 1147 testes; lote 3 (T13–T17) em seguida.

**Stack fixado**: Django 5.2.17 · PostgreSQL 16 na porta 5433 (AD-003) · pytest + pytest-django · Ruff.
Decisões que valem em toda task: AD-006, AD-010, AD-013, AD-014, AD-015.

**Lições aplicadas:** L-028 e L-030 (toda AC de "exibido" usa `exibido(html, rigoroso=True)` sobre
a página inteira, desde a T1) · L-005 (o que é de tela se afirma na resposta do `client`; o que é
de folha, na `kira.css`; a regra da página atual se afirma no processor **e** na tela).

---

## Test Coverage Matrix

> Gerada a partir do código, das diretrizes do projeto e da spec — confirmar antes do Execute.
> **Guidelines encontradas: nenhuma** (sem `AGENTS.md`, `CONTRIBUTING.md` nem CI; o
> `pyproject.toml` só configura o pytest e o Ruff, sem limite de cobertura nem `testpaths`). Valem os
> **strong defaults**. Estilo e piso de profundidade: `inovacoes/tests/test_views_sistema_design.py`,
> `inovacoes/tests/test_views_cabecalho.py`, `inovacoes/tests/visibilidade.py`,
> `config/tests/test_estaticos.py`, `contas/tests/test_controle_acesso.py`.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| ---------- | ------------------ | -------------------- | ---------------- | ----------- |
| Folha (`templates/kira.css`) | unit | Cada token com o valor exato; cada estado da §6 com a regra; cada par de cor no limiar (normal e alto contraste); restrições da AD-010 | `inovacoes/tests/test_folha_v2.py` | `.venv/bin/pytest -q -m unit` |
| Helper de teste (`exibido`) | unit | Cada vetor novo esconde; o modo padrão fica igual | `inovacoes/tests/test_visibilidade.py` | `.venv/bin/pytest -q -m unit` |
| Estáticos e settings | integration | `finders` acha a fonte; `collectstatic` copia; URL da folha = `STATIC_URL`; nenhuma origem externa | `config/tests/test_estaticos.py` | `.venv/bin/pytest -q` |
| Context processor | unit | Todo ramo da tabela de página atual (cada rota de `inovacoes`, painel, rotas fora, `resolver_match` nulo); cookie `alto`, ausente e outro valor; `busca_href` | `nucleo/tests/test_casca.py` | `.venv/bin/pytest -q -m unit` |
| View de contraste | e2e | Happy (alto, normal), cada edge (RED-37 a RED-42), atributos do cookie | `nucleo/tests/test_contraste.py` | `.venv/bin/pytest -q` |
| Templates (base, telas, páginas de apoio) | e2e | Cada AC de tela pelo `client`, anônimo e autenticado, sobre `exibido(…, rigoroso=True)`; ordem no DOM; ausências | `nucleo/tests/test_casca.py`, `nucleo/tests/test_paginas_apoio.py` | `.venv/bin/pytest -q` |
| Ícones e licenças | unit | Cada ícone com `aria-hidden="true"`, `focusable="false"`, `currentColor`; licenças presentes | `nucleo/tests/test_casca.py` | `.venv/bin/pytest -q -m unit` |

## Gate Check Commands

> Gerados a partir do projeto — confirmar antes do Execute. Pelo `.venv/`, com o PostgreSQL 16 na
> porta 5433 em execução.

| Gate Level | When to Use | Command |
| ---------- | ----------- | ------- |
| Quick | Task só com teste unitário | `.venv/bin/pytest -q -m unit` |
| Full | Task com teste e2e ou de integração | `.venv/bin/pytest -q` |
| Build | Ao fechar cada fase e em toda task que mexe no `base.html`, na `kira.css` ou em settings | `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` |

**Linha de base:** 943 testes passando (`.venv/bin/pytest -q`, 2026-11-15). A contagem nunca cai.

**Testes antigos que mudam (autorizados na aprovação da spec e do design):**

| # | Teste | Mudança | Task |
| - | ----- | ------- | ---- |
| T-A | `inovacoes/tests/test_views_cabecalho.py` (`LINK`, `LINK_INOVACOES`, `LINK_INDICADORES`, `_navegacao_principal`) | Busca pelo DOM parseado: `nav` com `aria-label="Principal"`, link por `href` e texto exibido; mesmas asserções | T10 |
| T-B | `contas/tests/test_controle_acesso.py:21` (`ROTAS_PUBLICAS`) | `+ "/acessibilidade/contraste/"` (T13), `+ "/acessibilidade/"` (T15), `+ "/ajuda/"` (T16) | T13, T15, T16 |
| T-C | `inovacoes/tests/test_views_sistema_design.py` (DS-01: `len(telas)`, `PECAS`) | `PECAS` + `paginas/trilha.html` (T12); 11 → 12 (T15) → 13 (T16) | T12, T15, T16 |
| T-D | `inovacoes/tests/test_views_sistema_design.py` (fixture `paginas`) | + "acessibilidade" (T15) e "ajuda" (T16), anônimo e autenticado | T15, T16 |
| T-E | `indicadores/tests/test_views_painel.py:178` | `"<svg" not in` só o `<main>` | T10 |
| T-F | `inovacoes/tests/test_views_sistema_design.py:177` (DS-05) | Espera `<span>Ana Souza</span>` | T10 |

Nenhum outro teste antigo pode mudar nem perder asserção. Se um quebrar, a task para e pergunta.

---

## Execution Plan

Fases em sequência; tasks em ordem dentro da fase. 17 tasks → 3 lotes de sub-agente (uma fase cada).

### Phase 1: Folha, fonte e helper

```
T1
T2
T3 → T4 → T5 → T6
```

### Phase 2: Casca do sistema

```
T7 → T9 → T10
T7 → T10
T8 → T10
T11 → T12
```

### Phase 3: Alto contraste e páginas de apoio

```
T7 → T13
T8 → T13
T9 → T13
T13 → T14
T6 → T14
T12 → T15
T13 → T15
T12 → T16
T15 → T17
T16 → T17
```

(As setas que partem de T6, T7, T8, T9 e T12 vêm de fases anteriores.)

---

## Task Breakdown

### T1: Modo rigoroso do `exibido()` ✅

**What**: `exibido(html, rigoroso=False)` ganha o modo `rigoroso=True`, que também esconde controles com `disabled`, elementos com `role` `presentation`/`none` (qualquer caixa) e os que têm uma classe declarada na `kira.css` com `display: none` numa regra de seletor de classe simples, fora de `@media` e de `[data-contraste=alto]`.
**Where**: `inovacoes/tests/visibilidade.py`
**Depends on**: None
**Reuses**: o parser `Exibido` e a função `escondido` do próprio arquivo
**Requirement**: regra de teste da feature (spec, Requirement Traceability); suporte a RED-13 a RED-36

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] Testes unitários novos em `inovacoes/tests/test_visibilidade.py`: cada vetor (`disabled` num `button`, `role="presentation"`, `role="NONE"`, classe com `display:none` na folha) some no modo rigoroso e continua no modo padrão; o que o modo padrão já escondia continua escondido nos dois
- [x] Nenhum teste existente muda; a suíte inteira passa
- [x] Gate check passa: `.venv/bin/pytest -q -m unit` e `.venv/bin/pytest -q`
- [x] Test count: ≥ 943 + 6

**Tests**: unit
**Gate**: quick

**Commit**: `test(nucleo): adiciona o modo rigoroso ao exibido`

---

### T2: Fonte Inter servida pelo projeto ✅

**What**: O arquivo `inter-latin-wght-normal.woff2` (de `@fontsource-variable/inter`, versão publicada há mais de duas semanas) e o `OFL.txt` em `static/fontes/`, `STATICFILES_DIRS = [BASE_DIR / "static"]`, o `@font-face` na `kira.css` e o `preload` no `base.html`.
**Where**: `static/fontes/` (arquivos), `config/settings.py`, `templates/kira.css`, `templates/base.html`
**Depends on**: None
**Reuses**: `config/tests/test_estaticos.py` (padrão de `collectstatic` com `override_settings(STATIC_ROOT=tmp_path)`)
**Requirement**: RED-05, RED-06, RED-07 (fonte), RED-08

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] Versão do pacote e SHA-256 do `.woff2` registrados no `design.md` (seção Fonte)
- [x] `@font-face` com `font-family: Inter`, `font-display: swap`, `font-weight: 400 800`, `src: url(/static/fontes/inter-latin-wght-normal.woff2) format(woff2)`; `--font-sans` igual ao da §3
- [x] Testes: `finders.find("fontes/inter-latin-wght-normal.woff2")` acha o arquivo; `collectstatic` num `tmp_path` o copia; a URL da folha é `"/" + settings.STATIC_URL + "fontes/inter-latin-wght-normal.woff2"`; `OFL.txt` existe e cita "SIL Open Font License"; nenhuma página da fixture `paginas` nem a folha tem `http://` ou `https://` em `<link`, `<script`, `<img`, `@import` ou `url(` (RED-08); o `preload` aponta para a mesma URL com `crossorigin`
- [x] DS-02 continua passando (folha crua == `<style>`)
- [x] Gate check passa: build
- [x] Test count: ≥ anterior + 7

**Tests**: integration
**Gate**: build

**Commit**: `feat(estaticos): serve a fonte Inter pelo projeto`

---

### T3: Tokens v2, cartão, campo e números ✅

**What**: Os tokens novos da §2 e §4 v2 no `:root`, o raio e a sombra do `.cartao`, a borda `--borda-campo` dos campos e o `font-variant-numeric: var(--numeros)` nos seletores da RED-04.
**Where**: `templates/kira.css`
**Depends on**: None
**Reuses**: `CSS`, `_regra`, `_corpos`, `_token`, `_contraste` de `inovacoes/tests/test_views_sistema_design.py` (importados)
**Requirement**: RED-01, RED-02, RED-03, RED-04

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] Testes em `inovacoes/tests/test_folha_v2.py` (marcados `unit`): cada token da RED-01 com o valor exato (parametrizado), os 23 tokens do DS-06 inalterados; `.cartao` com `border-radius: var(--raio-cartao)` e toda cor do `box-shadow` com alfa ≤ 0.12 (a sombra resolvida pelo token); `input`, `select`, `textarea` com `1.5px solid var(--borda-campo)`; `--borda-campo` ≥ 3:1 sobre `--surface` e `--bg`; cada seletor da RED-04 com `font-variant-numeric: var(--numeros)`
- [x] Folha sem `="`, sem `<`, sem nome de usuário dos testes (DS-02 continua)
- [x] Gate check passa: build
- [x] Test count: ≥ anterior + 20

**Tests**: unit
**Gate**: build

**Commit**: `feat(design): adiciona os tokens da v2 a folha central`

---

### T4: Botão, campo, selo e estados de interação ✅

**What**: Os estados da §6 v2 de botão (primário, secundário, perigo, hover, ativo, desabilitado), campo inválido e selo em pílula.
**Where**: `templates/kira.css`
**Depends on**: T3
**Reuses**: regras `.botao`, `.botao--perigo`, `.botao[aria-disabled=true]`, `.selo` existentes
**Requirement**: RED-09 (botão, campo, selo), RED-10

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] Testes `unit` em `test_folha_v2.py`: `button:hover`/`.botao:hover` com `var(--brand-blue-hover)`; `:active` existe; `:disabled` e `[aria-disabled=true]` com `var(--bg)`, `var(--text-muted)` e `cursor: not-allowed`; `.botao--secundario:hover` com `var(--info-tint)`; `.botao--perigo:hover` com `var(--error-tint)`; `[aria-invalid=true]` com `2px solid var(--error)`; `.selo` com `var(--raio-pilula)`; pares novos no limiar (texto 4.5:1: `on-brand`/`brand-blue-hover`, `text-muted`/`bg`, `brand-navy`/`info-tint`)
- [x] Testes de botão, alerta e selo do DS (DS-11 a DS-14) continuam passando
- [x] Gate check passa: build
- [x] Test count: ≥ anterior + 10

**Tests**: unit
**Gate**: build

**Commit**: `feat(design): define os estados de botao, campo e selo da v2`

---

### T5: Componentes do detalhe e do formulário ✅

**What**: `.cartao-inovacao`, `.etapas` (três estados), `.linha-do-tempo`, `.cartao-contato` e `.grupo`, conforme a tabela de componentes do design.
**Where**: `templates/kira.css`
**Depends on**: T4
**Reuses**: `.ciclo` e `.historico` como referência de forma (não removidos)
**Requirement**: RED-09 (esses componentes), RED-10

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] Testes `unit`: `.cartao-inovacao:hover` com borda `var(--brand-blue)` e título sublinhado; `.etapa--concluida` com `var(--success)`, `.etapa--atual`, `.etapa--futura` com `var(--borda-campo)`; `.linha-do-tempo time` com `var(--numeros)`; `.cartao-contato` com `border-top: 4px solid var(--brand-blue)` e `white-space: pre-line`; `.grupo legend` com `var(--fs-lg)`, `700`, `var(--brand-navy)`; `.grupo__numero` com fundo `var(--info-tint)`; toda cor de texto dessas regras está num par aprovado (RED-10)
- [x] Gate check passa: build
- [x] Test count: ≥ anterior + 9

**Tests**: unit
**Gate**: build

**Commit**: `feat(design): adiciona os componentes de detalhe e formulario da v2`

---

### T6: Componentes da lista e do painel, movimento e zoom ✅

**What**: `.filtros-ativos`/`.etiqueta-filtro`, `.resumo-erros`, `.barra-acoes`, `.cartao-indicador` com `.variacao--alta|--queda|--igual`, `.esqueleto` e `.decorativo`; o bloco de `prefers-reduced-motion` cobrindo tudo; as restrições de zoom da RED-12.
**Where**: `templates/kira.css`
**Depends on**: T5
**Reuses**: bloco `@media (prefers-reduced-motion: reduce)` existente (estendido, não duplicado)
**Requirement**: RED-09 (esses componentes), RED-10, RED-11, RED-12

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] Testes `unit`: `.etiqueta-filtro` com `var(--info-tint)`, `var(--brand-navy)`, `var(--raio-pilula)`, e regras `:hover` (fundo `var(--border)`) e `:focus-visible` no link de remover; `.resumo-erros` com `var(--error-tint)` e borda `var(--error)`; `.barra-acoes` com fundo `var(--bg)` e sem `position: sticky|fixed`; `.cartao-indicador__numero` com `var(--brand-navy)` e `var(--numeros)`; `.variacao--alta` (`--success`/`--success-tint`), `--queda` (`--error`/`--error-tint`), `--igual` (`--text-muted`/`--bg`); `.esqueleto` com `animation`; o bloco de reduzir movimento contém `transition: none` e `animation: none` aplicados a `*` (ou lista que inclui `.esqueleto`); nenhum `position: fixed` na folha; nenhum `width`/`min-width` acima de `320px` fora de `max-width`
- [x] Pares da RED-10 desta task conferidos (variações, barras sobre `--trilho`)
- [x] Gate check passa: build
- [x] Test count: ≥ anterior + 12

**Tests**: unit
**Gate**: build

**Commit**: `feat(design): adiciona os componentes de lista e painel da v2`

---

### T7: Context processor da casca ✅

**What**: `nucleo.context_processors.casca(request)` com `contraste_alto`, `menu_atual`, `menu_estado` e `busca_href`, registrado em `TEMPLATES[0]["OPTIONS"]["context_processors"]`.
**Where**: `nucleo/context_processors.py` (+ uma linha em `config/settings.py`)
**Depends on**: None
**Reuses**: `request.resolver_match` (namespace e `url_name`)
**Requirement**: RED-17, RED-18 (regra), RED-26 (leitura), RED-40, RED-14 (`busca_href`)

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] `nucleo/tests/__init__.py` e `nucleo/tests/test_casca.py` com testes `unit` usando `RequestFactory` + `resolve()`: lista → (`inovacoes`, `page`); nova → (`nova`, `page`); painel → (`indicadores`, `page`); cada uma de detalhe, editar, excluir, status, reaproveitar → (`inovacoes`, `true`); `/entrar/` → (None, None); `resolver_match` None → (None, None); cookie `alto` → `True`; ausente, `ALTO`, `sim`, vazio → `False`; `busca_href` `#id_q` só na lista
- [x] Gate check passa: build
- [x] Test count: ≥ anterior + 14

**Tests**: unit
**Gate**: build

**Commit**: `feat(nucleo): calcula o estado da casca por requisicao`

---

### T8: Ícones do Lucide ✅

**What**: `lampada.svg`, `circulo-mais.svg`, `grafico-barras.svg` e `contraste.svg` em `templates/icones/`, copiados do Lucide (`lightbulb`, `circle-plus`, `chart-column`, `contrast`), e o `LICENSE` com o ISC do Lucide e o MIT do Feather.
**Where**: `templates/icones/`
**Depends on**: None
**Reuses**: —
**Requirement**: RED-07 (ícones), RED-16 (forma do ícone)

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] Versão do Lucide registrada no `design.md` (seção Ícones)
- [x] Testes `unit` em `test_casca.py`: cada `.svg` abre com `<svg` e tem `aria-hidden="true"`, `focusable="false"`, `stroke="currentColor"`, `fill="none"`, sem `<title>` nem `id`; `LICENSE` existe e contém "ISC" e "MIT"
- [x] Gate check passa: quick
- [x] Test count: ≥ anterior + 6

**Tests**: unit
**Gate**: quick

**Commit**: `feat(design): adiciona os icones do menu e do contraste`

---

### T9: Barra de acessibilidade e faixa da marca ✅

**What**: No `base.html`, a `div.barra-acessibilidade` antes do `<header>` com o `nav aria-label="Atalhos de acessibilidade"` (atalho 1 sempre; 2 e 3 só autenticado, com `busca_href`) e cada `<kbd aria-hidden="true">`; a `div.faixa-marca.decorativo aria-hidden="true"`; o estilo da barra (branco sobre `--brand-navy`, anel de foco branco, 44px) e da faixa na `kira.css`, sem o `body > header::before`.
**Where**: `templates/base.html` (+ regras em `templates/kira.css`)
**Depends on**: T7
**Reuses**: o link `.pular` atual (passa a ficar visível na barra)
**Requirement**: RED-13, RED-14, RED-15, RED-21, RED-22 (barra)

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] Testes e2e em `test_casca.py` (sobre `exibido(html, rigoroso=True)`): em todas as páginas da fixture `paginas` (importada), o primeiro focável é o link de pular com `accesskey="1"`, seguido do `kbd` "1" `aria-hidden`; a barra vem antes do `<header>`; autenticado (lista, detalhe, painel): links "Ir para o menu" (`#menu`, `accesskey="2"`) e "Ir para a busca" (`accesskey="3"`; `#id_q` na lista, `/inovacoes/#id_q` no detalhe e no painel); anônimo (`/entrar/`): nenhum `accesskey="2"`/`"3"`; faixa `aria-hidden="true"` sem texto entre a barra e o `<header>`; a 500 (`render_to_string`) tem o atalho 1 e a faixa
- [x] Testes `unit` da folha: `.barra-acessibilidade` com fundo `var(--brand-navy)`; anel de foco branco nela (≥ 3:1 sobre o navy); `.faixa-marca` com `var(--brand-gradient)` e `height: 4px`; `min-height: 44px` nos links da barra
- [x] DS-03 e DS-04 passam sem mudança
- [x] Gate check passa: build
- [x] Test count: ≥ anterior + 12

**Tests**: e2e
**Gate**: build

**Commit**: `feat(design): adiciona a barra de acessibilidade do eMAG`

---

### T10: Menu com ícones, página atual e área do usuário ✅

**What**: No `base.html`, o `nav id="menu" aria-label="Principal"` com ícone antes de cada texto e `aria-current` pelo processor; a área do usuário com o nome completo (ou `username`) num `<span>` sem atributo e as iniciais `aria-hidden`; o estilo do item atual (fundo `--info-tint`, barra de 3px `--brand-blue`), do hover e do menu quebrando linha. Ajusta T-A, T-E e T-F.
**Where**: `templates/base.html` (+ `templates/kira.css`; testes antigos T-A, T-E, T-F)
**Depends on**: T7, T8, T9
**Reuses**: `nav[aria-label=Principal]` e `.usuario` da folha; formulário do "Sair" intacto
**Requirement**: RED-16, RED-17, RED-18, RED-19, RED-20, RED-22 (menu)

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] Testes e2e em `test_casca.py` (sobre `exibido(…, rigoroso=True)`): ordem Inovações → Cadastrar → Indicadores, cada um com `<svg aria-hidden="true" focusable="false">` antes do texto; `aria-current="page"` só em Inovações na lista, só em Cadastrar no cadastro, só em Indicadores no painel; `aria-current="true"` só em Inovações no detalhe, editar, excluir, status, sinalizar, 404 de inovação e 403 de inovação; nenhum `aria-current` no menu fora disso; nome completo "Ana Souza" no `<span>` e "AS" no elemento `aria-hidden`; conta sem nome mostra o `username`; o "Sair" continua depois do `nav`
- [x] Testes `unit` da folha: item atual com `var(--info-tint)` e `3px solid var(--brand-blue)` (seletor por `[aria-current]`); `flex-wrap: wrap` no menu; `min-height: 44px` nos itens
- [x] T-A, T-E e T-F feitos exatamente como na tabela de testes antigos; nenhuma asserção perdida
- [x] Gate check passa: build
- [x] Test count: ≥ anterior + 16

**Tests**: e2e
**Gate**: build

**Commit**: `feat(design): marca a pagina atual no menu com icones`

---

### T11: Cabeçalho de página e h1 pelo bloco ✅

**What**: No `base.html`, o bloco `cabecalho_pagina` (padrão: `div.cabecalho-pagina` com `<h1>{% block titulo %}{% endblock %}</h1>`, `descricao`, `acao_principal`) logo depois do `role="status"`; cada tela (menos o login, que sobrescreve `cabecalho_pagina` com vazio) passa o h1 para o bloco `titulo`, com o mesmo texto; estilo `.cabecalho-pagina` na folha.
**Where**: `templates/base.html` (+ as 11 telas com h1 e `templates/kira.css`)
**Depends on**: None
**Reuses**: textos de h1 atuais
**Requirement**: RED-29 (parte do `main`), RED-31

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] Testes e2e em `test_casca.py`: em cada página da fixture `paginas` (menos login e 500), exatamente um `h1`, dentro de `.cabecalho-pagina`, depois do `role="status"` e antes do conteúdo, com o texto de hoje (tabela no teste); o login tem um `h1` "Entrar", dentro do cartão; a 500 tem um `h1` "Algo deu errado do nosso lado"; um template de teste (`Template` em string) que estende o base e preenche `descricao` e `acao_principal` os mostra nessa ordem depois do `h1`, e sem preencher não renderiza nada deles
- [x] Todos os testes antigos de h1 e título passam sem mudança
- [x] Gate check passa: build
- [x] Test count: ≥ anterior + 14

**Tests**: e2e
**Gate**: build

**Commit**: `feat(design): padroniza o cabecalho de pagina no base`

---

### T12: Trilha de navegação ✅

**What**: A parcial `templates/paginas/trilha.html` (`atual`, `secao`, `inovacao`) e o bloco `trilha` do base entre o `<header>` e o `<main>`; as nove telas da §5.3 existentes hoje (lista, detalhe, cadastrar, editar, avançar status, sinalizar, excluir, painel) chamam a parcial; separador "›" por CSS. Ajusta T-C (`PECAS`).
**Where**: `templates/paginas/trilha.html` (+ `templates/base.html`, 8 telas, `templates/kira.css`, T-C)
**Depends on**: T11
**Reuses**: `inovacao.get_absolute_url`
**Requirement**: RED-29 (posição), RED-30

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] Testes e2e em `test_casca.py` (sobre `exibido(…, rigoroso=True)`): para cada uma das oito telas, `nav aria-label="Você está em"` com `ol` cujos itens, em ordem, são os da §5.3 (links com o `href` certo; último sem link, com `aria-current="page"`); a `nav` fica depois de `</header>` e antes de `<main id="conteudo">`; login, 403, 404 e 500 sem trilha; nenhum "›" no HTML; título com aspas e `&` sai escapado
- [x] Teste `unit` da folha: `li + li::before` da trilha com `content: "›"` e texto alternativo vazio
- [x] T-C: `PECAS` ganha `paginas/trilha.html`; contagem de telas segue 11
- [x] Os testes de links do `main` da F5/F6 (`test_views_acessibilidade_alteracao.py:237`, `:442`) passam sem mudança
- [x] Gate check passa: build
- [x] Test count: ≥ anterior + 12

**Tests**: e2e
**Gate**: build

**Commit**: `feat(design): adiciona a trilha de navegacao as telas`

---

### T13: Alto contraste: rota, cookie e botão ✅

**What**: `nucleo.views.definir_contraste` em `/acessibilidade/contraste/` (`nucleo:contraste`); no `base.html`, o `data-contraste="alto"` no `<html>`, o botão "Alto contraste" na barra (`form="form-contraste"`, `name="contraste"`, valor oposto, `aria-pressed`, ícone) e o `form#form-contraste` no fim do `body`, ambos só com `request`. Ajusta T-B.
**Where**: `nucleo/views.py` (+ `nucleo/urls.py`, `templates/base.html`, T-B)
**Depends on**: T7, T8, T9 (fases anteriores)
**Reuses**: `url_has_allowed_host_and_scheme`, `require_POST`, `login_not_required`
**Requirement**: RED-23, RED-24, RED-25, RED-26, RED-37, RED-38, RED-39, RED-40, RED-41, RED-42

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] Testes e2e em `nucleo/tests/test_contraste.py`: POST `alto` (anônimo e autenticado) → 302 para `voltar_para`, cookie `kira_contraste=alto` com `max-age` 31536000, `httponly`, `samesite=Lax` e `secure` igual a `not DEBUG` (os dois valores com `override_settings`); POST `normal` → 302 e cookie apagado (`max-age=0`); `voltar_para` externo (`https://outro.example/`), `//outro.example/`, vazio e ausente → `/`; `contraste` ausente, `ALTO`, `escuro` → 400 sem `Set-Cookie`; GET → 405; sem CSRF (`Client(enforce_csrf_checks=True)`) → 403; o mesmo POST duas vezes → respostas iguais; com cookie `alto` a página responde `<html lang="pt-br" data-contraste="alto">`, com outro valor `<html lang="pt-br">`; o botão tem `aria-pressed="true"` e `value="normal"` com o cookie, `"false"`/`"alto"` sem; o `form#form-contraste` é o último `<form>` do `body`, tem o CSRF e `voltar_para` igual a `request.get_full_path()` (com query); no login, o primeiro `<form>` continua o do login; a 500 sem request não tem botão nem form
- [x] T-B: `ROTAS_PUBLICAS` ganha `/acessibilidade/contraste/`
- [x] Gate check passa: build
- [x] Test count: ≥ anterior + 22

**Tests**: e2e
**Gate**: build

**Commit**: `feat(nucleo): liga e desliga o alto contraste sem javascript`

---

### T14: Tema de alto contraste na folha ✅

**What**: `:root[data-contraste=alto]` com todos os valores da §2 v2; links sublinhados; `.decorativo` e a faixa escondidos; `.selo`, `.alerta`, `[role=alert]`, `.variacao` e as barras do gráfico com borda de 1px na cor do texto.
**Where**: `templates/kira.css`
**Depends on**: T13, T6
**Reuses**: `PARES_DE_TEXTO` do DS-08 (importado) e os pares da T3–T6
**Requirement**: RED-27, RED-28, RED-10 (no tema)

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] Testes `unit` em `test_folha_v2.py`: cada token do bloco `:root[data-contraste=alto]` com o valor exato da §2 v2 (parametrizado); todo par de texto (DS-08 + T3–T6) ≥ 4.5:1 e todo par de componente ≥ 3:1 com os valores do tema; `a` sublinhado no tema; `.decorativo` e `.faixa-marca` com `display: none`; borda `1px solid` nos seletores da RED-28
- [x] Teste e2e: com o cookie `alto`, o `<style>` da página é a mesma folha (o tema vem só do atributo no `<html>`, sem CSS extra)
- [x] Gate check passa: build
- [x] Test count: ≥ anterior + 30

**Tests**: unit
**Gate**: build

**Commit**: `feat(design): adiciona o tema de alto contraste`

---

### T15: Página "Acessibilidade" ✅

**What**: `/acessibilidade/` (`nucleo:acessibilidade`, `TemplateView` com `login_not_required`), template `templates/paginas/acessibilidade.html` com trilha, h1 e as cinco seções com h2, a tabela de atalhos e o aviso de conflito; o link "Acessibilidade" na barra. Ajusta T-B, T-C (12) e T-D.
**Where**: `templates/paginas/acessibilidade.html` (+ `nucleo/views.py`, `nucleo/urls.py`, barra no `base.html`, T-B, T-C, T-D)
**Depends on**: T12, T13 (fase anterior e esta)
**Reuses**: parcial da trilha; `.tabela`
**Requirement**: RED-33, RED-34, RED-36

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] Testes e2e em `nucleo/tests/test_paginas_apoio.py` (sobre `exibido(…, rigoroso=True)`), anônimo e autenticado: 200; trilha "Acessibilidade"; h1 "Acessibilidade"; h2 "Compromisso", "Atalhos de teclado", "Alto contraste", "Ampliação", "Relatar uma barreira", nessa ordem; a tabela tem `caption`, `th scope`, as três linhas (1 conteúdo, 2 menu, 3 busca) e as combinações "Alt + n", "Alt + Shift + n", "Control + Option + n" com os navegadores; o texto do aviso de conflito com leitor de tela; anônimo sem `nav id="menu"` nem área do usuário; autenticado sem `aria-current` no menu; a barra de toda página tem o link "Acessibilidade" → `/acessibilidade/`
- [x] T-B (`/acessibilidade/`), T-C (12 telas), T-D (fixture com "acessibilidade" anônima e autenticada)
- [x] Gate check passa: build
- [x] Test count: ≥ anterior + 14

**Tests**: e2e
**Gate**: build

**Commit**: `feat(nucleo): adiciona a pagina de acessibilidade`

---

### T16: Página "Ajuda"

**What**: `/ajuda/` (`nucleo:ajuda`, `TemplateView` com `login_not_required`), template `templates/paginas/ajuda.html` com trilha "Ajuda", h1 e as quatro seções. Ajusta T-B, T-C (13) e T-D.
**Where**: `templates/paginas/ajuda.html` (+ `nucleo/views.py`, `nucleo/urls.py`, T-B, T-C, T-D)
**Depends on**: T12 (fase anterior)
**Reuses**: parcial da trilha
**Requirement**: RED-30 (Ajuda), RED-35, RED-36

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Testes e2e em `test_paginas_apoio.py`, anônimo e autenticado: 200; trilha "Ajuda"; h1 "Ajuda"; h2 "Buscar uma inovação", "Cadastrar uma inovação", "Avançar o status", "Precisa de ajuda?", em ordem, cada um seguido de texto exibido; anônimo sem menu nem usuário
- [ ] T-B (`/ajuda/`), T-C (13 telas), T-D (fixture com "ajuda")
- [ ] Gate check passa: build
- [ ] Test count: ≥ anterior + 8

**Tests**: e2e
**Gate**: build

**Commit**: `feat(nucleo): adiciona a pagina de ajuda`

---

### T17: Rodapé com links de apoio

**What**: No `<footer>` (sem atributo), o texto atual e a lista com os links "Acessibilidade" e "Ajuda"; estilo na folha.
**Where**: `templates/base.html` (+ `templates/kira.css`)
**Depends on**: T15, T16
**Reuses**: regras `body > footer` existentes
**Requirement**: RED-32

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Testes e2e em `test_casca.py`: em toda página da fixture `paginas` e na 500, o `<footer>` tem "KIRA · Repositório de Inovações · uso interno" e os links "Acessibilidade" → `/acessibilidade/` e "Ajuda" → `/ajuda/`, exibidos (`exibido(…, rigoroso=True)`)
- [ ] DS-04 passa sem mudança
- [ ] Gate check passa: build
- [ ] Test count: ≥ anterior + 4

**Tests**: e2e
**Gate**: build

**Commit**: `feat(design): adiciona os links de apoio ao rodape`

---

## Phase Execution Map

```
Phase 1 → Phase 2 → Phase 3

Phase 1:  T1, T2, T3, T4, T5, T6 (nesta ordem)
Phase 2:  T7, T8, T9, T10, T11, T12 (nesta ordem)
Phase 3:  T13, T14, T15, T16, T17 (nesta ordem)
```

Execução sequencial. Lotes: Fase 1 (6), Fase 2 (6), Fase 3 (5) → 3 sub-agentes, se aceitos.
Depois da T17: Verifier automático.

---

## Task Granularity Check

| Task | Scope | Status |
| ---- | ----- | ------ |
| T1 | 1 função (`exibido`) | ✅ |
| T2 | 1 recurso (fonte: arquivo + setting + `@font-face` + preload) | ⚠️ Coeso: um recurso só não funciona sem as quatro peças |
| T3 | Tokens e 3 regras na folha | ✅ |
| T4 | Estados de 3 componentes na folha | ✅ |
| T5 | 5 componentes de uma família | ⚠️ Coeso: só CSS, mesma família (detalhe/formulário) |
| T6 | 6 componentes + movimento + zoom | ⚠️ Coeso: só CSS, mesma família (lista/painel); restrições globais da folha |
| T7 | 1 função | ✅ |
| T8 | 4 arquivos de ícone + licença | ⚠️ Coeso: cópia de um conjunto |
| T9 | 1 região do base + estilo | ✅ |
| T10 | 1 região do base + estilo + testes antigos | ✅ |
| T11 | 1 bloco do base + migração do h1 nas telas | ⚠️ Coeso: o bloco não se testa sem as telas o usarem |
| T12 | 1 parcial + chamadas | ⚠️ Coeso: idem |
| T13 | 1 view + o controle que a aciona | ✅ |
| T14 | 1 bloco da folha | ✅ |
| T15 | 1 página | ✅ |
| T16 | 1 página | ✅ |
| T17 | 1 região do base | ✅ |

## Diagram-Definition Cross-Check

| Task | Depends On (task body) | Diagram Shows | Status |
| ---- | ---------------------- | ------------- | ------ |
| T1 | None | — | ✅ |
| T2 | None | — | ✅ |
| T3 | None | — | ✅ |
| T4 | T3 | T3 → T4 | ✅ |
| T5 | T4 | T4 → T5 | ✅ |
| T6 | T5 | T5 → T6 | ✅ |
| T7 | None | — | ✅ |
| T8 | None | — | ✅ |
| T9 | T7 | T7 → T9 | ✅ |
| T10 | T7, T8, T9 | T7 → T10, T8 → T10, T9 → T10 | ✅ |
| T11 | None | — | ✅ |
| T12 | T11 | T11 → T12 | ✅ |
| T13 | T7, T8, T9 (Fase 2) | T7 → T13, T8 → T13, T9 → T13 | ✅ |
| T14 | T13, T6 (Fase 1) | T13 → T14, T6 → T14 | ✅ |
| T15 | T12 (Fase 2), T13 | T12 → T15, T13 → T15 | ✅ |
| T16 | T12 (Fase 2) | T12 → T16 | ✅ |
| T17 | T15, T16 | T15 → T17, T16 → T17 | ✅ |

## Test Co-location Validation

| Task | Code Layer Created/Modified | Matrix Requires | Task Says | Status |
| ---- | --------------------------- | --------------- | --------- | ------ |
| T1 | Helper de teste | unit | unit | ✅ |
| T2 | Estáticos e settings, folha | integration | integration | ✅ |
| T3 | Folha | unit | unit | ✅ |
| T4 | Folha | unit | unit | ✅ |
| T5 | Folha | unit | unit | ✅ |
| T6 | Folha | unit | unit | ✅ |
| T7 | Context processor | unit | unit | ✅ |
| T8 | Ícones e licenças | unit | unit | ✅ |
| T9 | Templates + folha | e2e | e2e | ✅ |
| T10 | Templates + folha | e2e | e2e | ✅ |
| T11 | Templates | e2e | e2e | ✅ |
| T12 | Templates + folha | e2e | e2e | ✅ |
| T13 | View + templates | e2e | e2e | ✅ |
| T14 | Folha | unit | unit | ✅ |
| T15 | View + templates | e2e | e2e | ✅ |
| T16 | View + templates | e2e | e2e | ✅ |
| T17 | Templates | e2e | e2e | ✅ |
