# Redesign da Consulta (R2) Tasks

## Execution Protocol (MANDATORY -- do not skip)

Implement these tasks with the `tlc-spec-driven` skill: **activate it by name and follow its Execute flow and Critical Rules.** Do not search for skill files by filesystem path. The skill is the source of truth for the full flow (per-task cycle, sub-agent delegation, adequacy review, Verifier, discrimination sensor).

**If the skill cannot be activated, STOP and tell the user - do not proceed without it.**

---

**Spec**: `.specs/features/redesign-consulta/spec.md`
**Design**: `.specs/features/redesign-consulta/design.md`
**Status**: Approved (2026-11-19) · In Progress

---

## Test Coverage Matrix

> Gerada a partir do código, das diretrizes do projeto e da spec — confirmar antes do Execute.
> **Guidelines encontradas: nenhuma** (sem `AGENTS.md`, `CONTRIBUTING.md` nem CI; o
> `pyproject.toml` só configura o pytest e o Ruff, sem limite de cobertura). Valem os **strong
> defaults**. Estilo e piso: `inovacoes/tests/test_views_lista.py`, `test_views_detalhe.py`,
> `test_consultas.py`, `test_folha_v2.py`, `nucleo/tests/test_casca.py`, `visibilidade.py`.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| ---------- | ------------------ | -------------------- | ---------------- | ----------- |
| QuerySet (`para_listagem`) | integration | Colunas novas com valores exatos (0, 1, 3 reaproveitamentos); número de consultas igual para 1 e 20 itens | `inovacoes/tests/test_consultas.py` | `.venv/bin/pytest -q` |
| Apresentação (`inovacoes/apresentacao.py`) | unit | Todo ramo, 1:1 com as ACs que cada função serve; cada edge case da spec que cai nela | `inovacoes/tests/test_apresentacao.py` | `.venv/bin/pytest -q -m unit` |
| Views + templates (lista e detalhe) | e2e | Cada AC de tela pelo `client` sobre `exibido(html, rigoroso=True)` no DOM parseado; ausências; perfis `USUARIO`, `USUARIO` com `is_staff`, autor e `ADMINISTRADOR` nas ações (L-003); número de consultas | `inovacoes/tests/test_views_lista_*.py`, `inovacoes/tests/test_views_detalhe_v2.py` | `.venv/bin/pytest -q` |
| Folha (`templates/kira.css`) | unit | Cada componente novo com a regra; pares de cor novos no DS-08 (normal e alto contraste); RED-11, RED-12; RCON-47; nenhuma regra morta | `inovacoes/tests/test_folha_v2.py` | `.venv/bin/pytest -q -m unit` |
| Ícones e ilustração | unit | Cada SVG com `aria-hidden="true"`, `focusable="false"`; ícones com `currentColor`; licença presente | `nucleo/tests/test_casca.py` | `.venv/bin/pytest -q -m unit` |

## Gate Check Commands

> Pelo `.venv/`, com o PostgreSQL 16 na porta 5433 em execução.

| Gate Level | When to Use | Command |
| ---------- | ----------- | ------- |
| Quick | Task só com teste unitário | `.venv/bin/pytest -q -m unit` |
| Full | Task com teste e2e ou de integração | `.venv/bin/pytest -q` |
| Build | Ao fechar cada fase e em toda task que mexe no `base.html` ou na `kira.css` | `.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py makemigrations --check --dry-run && .venv/bin/pytest -q` |

**Linha de base:** 1326 testes coletados (`.venv/bin/pytest -q --co`, 2026-11-19). A contagem nunca cai.

**Testes antigos que mudam (autorizados na aprovação da spec e do design):** só T-A a T-P, cada
um na task indicada abaixo. Mudam no mesmo commit da task que os quebra, preservando a garantia da
AC original (docstring com a AC). Se outro teste antigo quebrar, a task para e pergunta.

| # | Task |
| - | ---- |
| T-A, T-E | T9 |
| T-B | T9 (CONS-06), T10 (CONS-38, DS-16) |
| T-C | T7 (lista), T16 (detalhe) |
| T-D | T12 (`LIMPAR`), T14 (CONS-34, CONS-35) |
| T-F | T16 (CONS-12 status), T17 (resto) |
| T-G | T19 |
| T-H | T18 |
| T-I | T20 |
| T-J | T21 |
| T-K | T18 (etapas), T19 (link descrito), T20 (`historico`) |
| T-L | T18 (`.ciclo`), T20 (`.historico`), T21 (`.reaproveitamentos`) |
| T-M | toda task que cria parcial |
| T-N | T14 (ilustração), T21 (`caption`) |
| T-O | T6 (ícones), T16 (cabeçalho) |
| T-P | T7 |

---

## Execution Plan

### Phase 1: Fundação (sem mudança visível de tela)

```
T1 → T2 → T3 → T4 → T5 → T6 → T7
```

### Phase 2: Lista

```
T8 → T9 → T10 → T11 → T12 → T13 → T14 → T15
```

### Phase 3: Detalhe

```
T16 → T17 → T18 → T19 → T20 → T21
```

### Phase 4: Fechamento da folha

```
T22
```

---

## Task Breakdown

### T1: `para_listagem` com resumo e contagem ✅

**What**: `para_listagem()` passa a carregar `problema` e `total_reaproveitamentos = Count("reaproveitamentos")` na mesma consulta.
**Where**: `inovacoes/models.py`
**Depends on**: None
**Reuses**: `select_related`/`only`/`order_by` atuais
**Requirement**: RCON-13, RCON-14, RCON-16

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] Testes em `test_consultas.py`: `total_reaproveitamentos` 0, 1 e 3 em inovações da mesma página; `problema` acessível sem consulta nova (`assertNumQueries(0)` ao ler); `buscar().filtrar()` sobre o queryset anotado continua com uma consulta; ordem CONS-02 intacta
- [x] Gate full passa; test count ≥ 1326 + 4

**Tests**: integration
**Gate**: full

**Commit**: `feat(inovacoes): carrega o resumo e os reaproveitamentos na listagem`

---

### T2: URL da lista e exibição ✅

**What**: `url_da_lista(consulta, **mudancas)` e `exibicao(consulta)` em `inovacoes/apresentacao.py`.
**Where**: `inovacoes/apresentacao.py` (novo)
**Depends on**: T1
**Reuses**: `QueryDict.copy()`/`urlencode()`
**Requirement**: RCON-05, RCON-06, RCON-18, RCON-20

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] Testes unitários: `None` remove; o último parâmetro saindo dá `/inovacoes/` sem `?`; valores repetidos e acentuados preservados; `exibicao` só aceita `tabela` (ausente, vazio, `TABELA`, `cartoes`, `x` → `cartoes`)
- [x] Gate quick passa; test count ≥ anterior + 8

**Tests**: unit
**Gate**: quick

**Commit**: `feat(inovacoes): monta as urls da lista e a exibicao escolhida`

---

### T3: Etiquetas de filtro ativo ✅

**What**: `etiquetas(dados_validos, consulta) -> list[Etiqueta]`.
**Where**: `inovacoes/apresentacao.py`
**Depends on**: T2
**Reuses**: `url_da_lista`
**Requirement**: RCON-04, RCON-05, RCON-07

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] Testes unitários: ordem Busca, Categoria, Unidade, Status; textos exatos ("Busca: “termo”", "Categoria: {nome}", "Unidade: {nome}", "Status: {rótulo}"); `q` só com espaços não gera etiqueta (CONS-21); cada `href` tira o próprio parâmetro e o `page` e mantém `exibicao`; sem filtro → `[]`
- [x] Gate quick passa; test count ≥ anterior + 7

**Tests**: unit
**Gate**: quick

**Commit**: `feat(inovacoes): monta as etiquetas dos filtros ativos`

---

### T4: Janela de páginas ✅

**What**: `paginas(page_obj) -> list[int | str]` com `get_elided_page_range(on_each_side=2, on_ends=1)`.
**Where**: `inovacoes/apresentacao.py`
**Depends on**: T3
**Reuses**: `Paginator.get_elided_page_range`, `Paginator.ELLIPSIS`
**Requirement**: RCON-22

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] Testes unitários: 25 páginas na 1 (`1 2 3 … 25`), na 5 (`1 … 3 4 5 6 7 … 25`), na 25; 3 páginas sem "…"; 1 página
- [x] Gate quick passa; test count ≥ anterior + 5

**Tests**: unit
**Gate**: quick

**Commit**: `feat(inovacoes): calcula a janela de paginas da lista`

---

### T5: Itens do histórico ✅

**What**: `itens_do_historico(inovacao, mudancas) -> list[ItemDoHistorico]`.
**Where**: `inovacoes/apresentacao.py`
**Depends on**: T4
**Reuses**: `StatusInovacao`, regra de nome da CONS-13
**Requirement**: RCON-43, RCON-44, RCON-45

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] Testes unitários (objetos em memória, sem banco): sem mudanças → só o cadastro com o status atual; com mudanças → cadastro com o `status_anterior` da primeira + uma por mudança, na ordem recebida; textos exatos; nome completo ou `username`
- [x] Gate quick passa; test count ≥ anterior + 4

**Tests**: unit
**Gate**: quick

**Commit**: `feat(inovacoes): monta os itens da linha do tempo do historico`

---

### T6: Ícones novos ✅

**What**: os 10 SVG Lucide da design (`frasco`, `visto`, `caixa-seta`, `lupa`, `fechar`, `grade`, `tabela`, `predio`, `etiqueta`, `repetir`).
**Where**: `templates/icones/`
**Depends on**: T5
**Reuses**: cabeçalho SVG dos 4 ícones da R1; `LICENSE`
**Requirement**: RCON-15 (suporte a RCON-02, 05, 11, 17)

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] T-O (parte dos ícones): `nucleo/tests/test_casca.py:123` passa a exigir os 4 da R1 mais os 10 da R2; cada um com `aria-hidden="true"`, `focusable="false"`, `stroke="currentColor"`, sem `style`
- [x] Gate quick passa; test count ≥ anterior

**Tests**: unit
**Gate**: quick

**Commit**: `feat(design): adiciona os icones da consulta`

---

### T7: Selo com ícone ✅

**What**: parcial `inovacoes/parciais/selo.html` (ícone por status + rótulo), usada na tabela atual; a folha perde as formas `::before` do `.selo`.
**Where**: `inovacoes/templates/inovacoes/parciais/selo.html`, `inovacao_list.html`, `templates/kira.css`
**Depends on**: T6
**Reuses**: `.selo--*`
**Requirement**: RCON-15

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [x] T-P: DS-13 exige, para cada status, um SVG `aria-hidden` diferente no selo renderizado e nenhum `::before` com forma no `.selo`
- [x] T-C (lista): DS-12 lê o selo com o rótulo depois do SVG
- [x] T-M: `PECAS` + `parciais/selo.html`
- [x] Gate build passa; test count ≥ anterior

**Tests**: e2e
**Gate**: build

**Commit**: `feat(inovacoes): poe o icone do status no selo`

---

### T8: Contexto da lista

**What**: `InovacaoListView.get_context_data` passa `exibicao`, `url_cartoes`, `url_tabela`, `etiquetas` (vazia com form inválido), `url_limpar` e `paginas`.
**Where**: `inovacoes/views.py`
**Depends on**: None (a Fase 1 inteira antes)
**Reuses**: T2–T4; `filtros_ativos` atual
**Requirement**: RCON-04, RCON-06, RCON-08, RCON-18, RCON-20, RCON-22

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Testes e2e em `test_views_lista_filtros.py` sobre `response.context`: cada chave com o valor exato para filtros válidos, form inválido (CONS-30), `exibicao=tabela` e página 2
- [ ] Gate full passa; test count ≥ anterior + 5

**Tests**: e2e
**Gate**: full

**Commit**: `feat(inovacoes): passa o contexto de apresentacao para a lista`

---

### T9: Cartões como exibição padrão

**What**: a lista renderiza os cartões (`parciais/cartao.html`, `ul aria-label="Resultados"`) e só mostra a tabela (`parciais/tabela.html`, sem mudança de conteúdo) com `exibicao=tabela`; CSS `.cartoes`.
**Where**: `inovacao_list.html`, `parciais/cartao.html`, `parciais/tabela.html`, `templates/kira.css`
**Depends on**: T8
**Reuses**: `.cartao-ino\76 acao*`, selo (T7)
**Requirement**: RCON-10, RCON-11, RCON-12, RCON-13, RCON-14, RCON-16, RCON-19

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Testes novos em `test_views_lista_cartoes.py`: ordem dos elementos do cartão; título único link; resumo com 160 e 161 caracteres; "Nenhum/1/3 reaproveitamento(s)"; sem tabela; com `exibicao=tabela` a tabela e sem cartões, mesmos itens e ordem; RCON-16 com 20 cartões de contagens diferentes
- [ ] T-A: `_linhas` e `_titulos` leem os cartões pelo DOM e falham sem a lista (CONS-01 a 05, 08, 19 a 21, 27, 28, 40, 47, 48); T-B (CONS-06); T-E (EDEX-37)
- [ ] T-M: `PECAS` + `cartao.html`, `tabela.html`
- [ ] Gate build passa; test count ≥ anterior + 10

**Tests**: e2e
**Gate**: build

**Commit**: `feat(inovacoes): mostra os resultados da lista em cartoes`

---

### T10: Barra de resultados e alternador

**What**: contador `p.total role="status"` e o grupo "Exibição" com "Cartões"/"Tabela"; CSS `.resultados`, `.alternador` (+ par navy/on-brand no DS-08).
**Where**: `inovacao_list.html`, `templates/kira.css`
**Depends on**: T9
**Reuses**: `url_cartoes`, `url_tabela` (T8)
**Requirement**: RCON-09, RCON-17, RCON-18, RCON-20

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Testes novos: contador singular/plural com total de todas as páginas; links com `href` exato mantendo `q`, filtros e `page`; `aria-current="true"` só no atual; valor desconhecido → Cartões atual, sem erro; CONS-41 intacto
- [ ] T-B: CONS-38 e DS-16 abrem `?exibicao=tabela`
- [ ] Gate build passa; test count ≥ anterior + 6

**Tests**: e2e
**Gate**: build

**Commit**: `feat(inovacoes): adiciona o alternador entre cartoes e tabela`

---

### T11: Busca em destaque e filtros em linha

**What**: `form.busca` com `.busca__principal` (lupa, campo de 52px, botão) e `.busca__filtros` (três selects em grade).
**Where**: `inovacao_list.html`, `templates/kira.css`
**Depends on**: T10
**Reuses**: `BuscaForm` e `campo.html` (os campos seguem renderizados pelo Django: `id_q`, `id_q_error`, `aria-invalid`)
**Requirement**: RCON-02, RCON-03

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Testes novos: ordem lupa → `q` → ajuda → "Buscar" → selects; lupa `aria-hidden`; sem `onchange` nem `<script>`; regra CSS de 52px e 17px; CONS-31, CONS-37, CONS-43, DS-14 e RED-14 intactos
- [ ] Gate build passa; test count ≥ anterior + 4

**Tests**: e2e
**Gate**: build

**Commit**: `feat(inovacoes): destaca a busca e alinha os filtros`

---

### T12: Etiquetas na tela

**What**: `parciais/etiquetas.html` dentro do `div role="search"`, depois do form.
**Where**: `parciais/etiquetas.html`, `inovacao_list.html`
**Depends on**: T11
**Reuses**: `.filtros-ativos`, `.etiqueta-filtro`; ícone `fechar`
**Requirement**: RCON-04, RCON-05, RCON-06, RCON-07, RCON-08

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Testes novos: rótulo "Filtros ativos:", etiquetas na ordem e com o texto, nome acessível "Remover filtro …" e `href` exato; "Limpar filtros" por último; nenhuma etiqueta sem filtro; form inválido → só as válidas + "Limpar filtros"; um só `<form>`
- [ ] T-D: `LIMPAR` aceita classe e `?exibicao=tabela`
- [ ] T-M: `PECAS` + `etiquetas.html`
- [ ] Gate full passa; test count ≥ anterior + 7

**Tests**: e2e
**Gate**: full

**Commit**: `feat(inovacoes): mostra os filtros ativos como etiquetas`

---

### T13: Paginação numerada

**What**: `parciais/paginacao.html` com pontas desabilitadas, números, "…" e "Página X de Y"; CSS `.paginacao`.
**Where**: `parciais/paginacao.html`, `inovacao_list.html`, `templates/kira.css`
**Depends on**: T12
**Reuses**: `paginas` (T4), `{% querystring %}`
**Requirement**: RCON-21, RCON-22, RCON-23, RCON-24

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Testes novos: janela na página 1, 5 e última com 25 páginas; atual sem link com `aria-current="page"`; pontas como texto `aria-disabled`; links mantêm `q`, filtros e `exibicao`; CONS-03 a 05 e CONS-41 intactos
- [ ] T-M: `PECAS` + `paginacao.html`
- [ ] Gate build passa; test count ≥ anterior + 6

**Tests**: e2e
**Gate**: build

**Commit**: `feat(inovacoes): numera as paginas da lista`

---

### T14: Estados vazios com ilustração

**What**: `parciais/vazio.html` e `parciais/ilustracao_vazio.svg`, nas duas variantes; ilustração escondida no alto contraste.
**Where**: `parciais/vazio.html`, `parciais/ilustracao_vazio.svg`, `inovacao_list.html`, `templates/kira.css`
**Depends on**: T13
**Reuses**: `.vazio`
**Requirement**: RCON-25, RCON-26, RCON-27

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Testes novos: textos e ações exatos de cada variante; etiquetas visíveis na variante sem resultado; nada de contador, cartões, tabela ou paginação; ilustração `aria-hidden`; regra `display: none` só sob `[data-contraste=alto]`
- [ ] T-D: CONS-34 e CONS-35 com os textos da §10; T-N (ilustração); T-M (`vazio.html`)
- [ ] Gate build passa; test count ≥ anterior + 5

**Tests**: e2e
**Gate**: build

**Commit**: `feat(inovacoes): ilustra os estados vazios da lista`

---

### T15: Cabeçalho da lista

**What**: blocos `descricao` e `acao_principal` da lista.
**Where**: `inovacao_list.html`
**Depends on**: T14
**Reuses**: blocos do base (R1)
**Requirement**: RCON-01

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Testes novos: trilha, h1, descrição e "Cadastrar inovação" → `/inovacoes/nova/`, na ordem; RED-29/31 intactos
- [ ] Gate build passa (fecha a Fase 2); test count ≥ anterior + 2

**Tests**: e2e
**Gate**: build

**Commit**: `feat(inovacoes): completa o cabecalho da lista`

---

### T16: Cabeçalho do detalhe

**What**: bloco `sobretitulo` no base; no detalhe, selo acima do h1 e a linha "Cadastrada por … · {unidade} · {categoria}"; o status sai da ficha.
**Where**: `templates/base.html`, `inovacao_detail.html`
**Depends on**: None (a Fase 2 inteira antes)
**Reuses**: selo (T7)
**Requirement**: RCON-28

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Testes novos em `test_views_detalhe_v2.py`: ordem trilha → selo → h1 → linha; texto exato da linha; outras telas sem mudança no cabeçalho
- [ ] T-C (detalhe): DS-12 lê o selo do cabeçalho; T-F (CONS-12 status); T-O (`CABECALHO_DE_PAGINA` aceita o selo antes do h1)
- [ ] Gate build passa; test count ≥ anterior + 3

**Tests**: e2e
**Gate**: build

**Commit**: `feat(inovacoes): poe o selo e a linha de autoria no cabecalho do detalhe`

---

### T17: Narrativa, contato e ficha na grade

**What**: `div.detalhe` com a seção "Como a inovação funciona", o `aside` (contato, ficha) e a grade de duas colunas; CSS `.detalhe`, `.narrativa`, `.ficha-resumo`; saem `.ficha dd.selo` e `.ficha .destaque`.
**Where**: `inovacao_detail.html`, `templates/kira.css`
**Depends on**: T16
**Reuses**: `.cartao-contato*`
**Requirement**: RCON-29, RCON-30, RCON-31, RCON-32, RCON-33, RCON-50

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Testes novos: três `h3` na ordem com o texto completo e `<br>`; "Resultado ainda não informado."; `aside` depois da narrativa e antes dos reaproveitamentos; contato com quebras e a nota; ficha com 5 pares exatos; HTML escapado (CONS-17); grade só a partir de 45rem
- [ ] T-F: `ROTULOS`/`_pares` lêem a ficha nova e a narrativa (CONS-12, 14, 16, 42)
- [ ] Gate build passa; test count ≥ anterior + 7

**Tests**: e2e
**Gate**: build

**Commit**: `feat(inovacoes): conta o detalhe como narrativa com resumo lateral`

---

### T18: Ciclo de vida no resumo

**What**: a view passa `etapas` com a situação; o bloco "Ciclo de vida" vai para o `aside` com `ol.etapas`, explicações e o botão desabilitado; sai a regra `.ciclo`.
**Where**: `inovacoes/views.py`, `inovacao_detail.html`, `templates/kira.css`
**Depends on**: T17
**Reuses**: `.etapas`, `.etapa--*`
**Requirement**: RCON-34, RCON-41 (texto), RCON-42

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Testes novos: textos "· concluída" / "(status atual)" / "· próxima etapa" nos três status; `aria-current="step"` só no atual; marcadores `aria-hidden`; explicações exatas por status e perfil (inclusive `USUARIO` com `is_staff`); botão `aria-disabled` só para quem pode alterar no último estágio
- [ ] T-H, T-K (etapas), T-L (`.ciclo` → `.etapas`)
- [ ] Gate build passa; test count ≥ anterior + 6

**Tests**: e2e
**Gate**: build

**Commit**: `feat(inovacoes): mostra o ciclo de vida como indicador de etapas`

---

### T19: Ações em hierarquia

**What**: bloco `acao_principal` do detalhe com `div.acoes-pagina` (primária por status, Editar, Excluir separado); CSS `.acoes-pagina`.
**Where**: `inovacao_detail.html`, `templates/kira.css`
**Depends on**: T18
**Reuses**: `.botao`, `.botao--secundario`, `.botao--perigo`; `pode_alterar` (AD-009)
**Requirement**: RCON-37, RCON-38, RCON-39, RCON-40, RCON-41

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Testes novos: matriz status × perfil (autor, `ADMINISTRADOR`, `USUARIO`, `USUARIO` com `is_staff`): no máximo uma primária, a certa; Editar depois; Excluir por último no grupo separado; `aria-describedby` do Avançar aponta para a explicação do bloco; nenhuma ação a quem não pode
- [ ] T-G (`_links`), T-K (link descrito)
- [ ] Gate build passa; test count ≥ anterior + 8

**Tests**: e2e
**Gate**: build

**Commit**: `feat(inovacoes): organiza as acoes do detalhe por hierarquia`

---

### T20: Histórico como linha do tempo

**What**: a view passa `historico` (T5) com `mudancas` em lista; o template renderiza `ol.linha-do-tempo`; sai a regra `.historico`.
**Where**: `inovacoes/views.py`, `inovacao_detail.html`, `templates/kira.css`
**Depends on**: T19
**Reuses**: `.linha-do-tempo*`; `itens_do_historico`
**Requirement**: RCON-43, RCON-44, RCON-45, RCON-46

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Testes novos: item de cadastro com data/hora no fuso e status inicial certo (com e sem mudanças); mudanças na ordem; pontos `aria-hidden`; `CONSULTAS_DO_DETALHE = 8` com 0 e 3 mudanças
- [ ] T-I, T-K (`historico`), T-L (`.historico`)
- [ ] Gate build passa; test count ≥ anterior + 4

**Tests**: e2e
**Gate**: build

**Commit**: `feat(inovacoes): mostra o historico de status como linha do tempo`

---

### T21: Reaproveitamentos em tabela

**What**: seção "Reaproveitamentos ({n})" com tabela Unidade, Registrado por, Data (`caption.visualmente-oculto`); `select_related("unidade", "registrado_por")`; sai a regra `.reaproveitamentos`.
**Where**: `inovacoes/views.py`, `inovacao_detail.html`, `templates/kira.css`
**Depends on**: T20
**Reuses**: `.tabela`
**Requirement**: RCON-35, RCON-36

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Testes novos: título com a contagem; colunas e linhas na ordem (REAP-18); vazio sem tabela; caption oculto só visualmente; `CONSULTAS_DO_DETALHE = 8` com 0 e 3 reaproveitamentos
- [ ] T-J, T-L (`.reaproveitamentos`), T-N (`caption`)
- [ ] Gate build passa (fecha a Fase 3); test count ≥ anterior + 4

**Tests**: e2e
**Gate**: build

**Commit**: `feat(inovacoes): lista os reaproveitamentos do detalhe em tabela`

---

### T22: Garantias da folha da R2

**What**: testes de folha para as regras acrescentadas pela R2: ordem de leitura (RCON-47), AD-010 nos templates (RCON-48), pares de cor no DS-08 inclusive alto contraste, reduced motion e reflow (RCON-49), uma coluna abaixo de 720px (RCON-50); ajusta a folha onde algum falhar.
**Where**: `inovacoes/tests/test_folha_v2.py`
**Depends on**: None (a Fase 3 inteira antes)
**Reuses**: helpers de folha da R1 (`_regra`, `_corpos`, DS-08)
**Requirement**: RCON-47, RCON-48, RCON-49, RCON-50

**Tools**: MCP: NONE · Skill: NONE

**Done when**:

- [ ] Testes novos: nenhuma regra da R2 com `order` ou posicionamento que ponha um elemento antes de um irmão anterior; nenhum `style` nos templates novos; cada par novo no DS-08 normal e alto; transições novas no `prefers-reduced-motion`; nenhuma largura acima de 320px fora de `min()`/`max-width`
- [ ] Gate build passa; test count ≥ anterior + 5

**Tests**: unit
**Gate**: build

**Commit**: `test(design): garante as regras da folha no redesign da consulta`

---

## Phase Execution Map

```
Phase 1 → Phase 2 → Phase 3 → Phase 4

Phase 1:  T1 → T2 → T3 → T4 → T5 → T6 → T7
Phase 2:  T8 → T9 → T10 → T11 → T12 → T13 → T14 → T15
Phase 3:  T16 → T17 → T18 → T19 → T20 → T21
Phase 4:  T22
```

Lotes de sub-agente (~7 tasks, fases inteiras): **Lote 1** Fase 1 (T1–T7) · **Lote 2** Fase 2
(T8–T15) · **Lote 3** Fases 3 e 4 (T16–T22). Depois do T22, o Verifier.

---

## Task Granularity Check

| Task | Scope | Status |
| ---- | ----- | ------ |
| T1 | 1 método | ✅ |
| T2–T5 | 1 a 2 funções cada, no mesmo módulo | ✅ |
| T6 | 10 arquivos de dado de um tipo só (ícones), sem lógica | ⚠️ coeso |
| T7 | 1 parcial + a regra do selo que ela substitui | ⚠️ coeso |
| T8 | 1 método | ✅ |
| T9 | trocar a exibição padrão exige o cartão e a tabela juntos; separar deixaria a lista sem resultados num commit | ⚠️ coeso |
| T10–T21 | 1 componente de tela + a regra CSS dele | ⚠️ coeso |
| T22 | 1 arquivo de teste | ✅ |

## Diagram-Definition Cross-Check

| Task | Depends On (task body) | Diagram Shows | Status |
| ---- | ---------------------- | ------------- | ------ |
| T1 | None | — | ✅ |
| T2 | T1 | T1 → T2 | ✅ |
| T3 | T2 | T2 → T3 | ✅ |
| T4 | T3 | T3 → T4 | ✅ |
| T5 | T4 | T4 → T5 | ✅ |
| T6 | T5 | T5 → T6 | ✅ |
| T7 | T6 | T6 → T7 | ✅ |
| T8 | None (Fase 1 antes) | início da Fase 2 | ✅ |
| T9 | T8 | T8 → T9 | ✅ |
| T10 | T9 | T9 → T10 | ✅ |
| T11 | T10 | T10 → T11 | ✅ |
| T12 | T11 | T11 → T12 | ✅ |
| T13 | T12 | T12 → T13 | ✅ |
| T14 | T13 | T13 → T14 | ✅ |
| T15 | T14 | T14 → T15 | ✅ |
| T16 | None (Fase 2 antes) | início da Fase 3 | ✅ |
| T17 | T16 | T16 → T17 | ✅ |
| T18 | T17 | T17 → T18 | ✅ |
| T19 | T18 | T18 → T19 | ✅ |
| T20 | T19 | T19 → T20 | ✅ |
| T21 | T20 | T20 → T21 | ✅ |
| T22 | None (Fase 3 antes) | início da Fase 4 | ✅ |

## Test Co-location Validation

| Task | Code Layer Created/Modified | Matrix Requires | Task Says | Status |
| ---- | --------------------------- | --------------- | --------- | ------ |
| T1 | QuerySet | integration | integration | ✅ |
| T2–T5 | Apresentação | unit | unit | ✅ |
| T6 | Ícones | unit | unit | ✅ |
| T7 | Template + folha | e2e (maior) | e2e | ✅ |
| T8 | View | e2e | e2e | ✅ |
| T9–T21 | Views/templates + folha | e2e (maior) | e2e | ✅ |
| T22 | Folha | unit | unit | ✅ |
