# Fundação do Redesign (R1) — Specification

**Status:** Concluída em 2026-11-15 com risco residual de teste aceito (RED-16, RED-22). Aprovada em 2026-11-15 (Discuss fechado; testes antigos T-A a T-D autorizados). Ajustada pelo Design em 2026-11-15 (RED-23, 24, 25, 29, 30, 31, 37; T-E e T-F autorizados com o design).

Fonte do visual: `docs/design-spec.md` **v2** (§1–§9). Passe de design cross-cutting no molde da
`sistema-de-design`: muda a casca comum (tokens, fonte, barra de acessibilidade, cabeçalho do
sistema, menu, cabeçalho de página, rodapé, alto contraste) e põe na `kira.css` os componentes
da v2 com todos os estados. O miolo de cada tela (lista, detalhe, formulários, painel, login) é
refeito nas features seguintes do redesign, que só consomem o que a R1 entrega. Não muda regra
de negócio, model nem migration.

## Testes antigos que mudam (autorização na aprovação)

A R1 mexe no HTML que alguns testes da F1 à F6 fixam por regex. Cada mudança abaixo preserva a
asserção (mesmo texto, mesmo destino, mesma ordem, mesma ausência); muda só a forma de achar o
elemento. Nenhum outro teste antigo pode mudar; se o Execute achar mais um, para e pede.

| # | Teste | Feature / AC | Muda o quê | Por quê |
| - | ----- | ------------ | ---------- | ------- |
| T-A | `inovacoes/tests/test_views_cabecalho.py`: os regex `LINK`, `LINK_INOVACOES`, `LINK_INDICADORES` e o helper `_navegacao_principal` | F2 INOV-38, F3 CONS-10, F6 REAP-28 | Passam a achar o `nav aria-label="Principal"` e cada link pelo DOM parseado (`href` + texto exibido, sem o conteúdo `aria-hidden`), não por `<a href="…">Texto</a>` literal | Os links ganham ícone SVG `aria-hidden` e `aria-current`; o `nav` ganha `id="menu"` (RED-14, RED-15, RED-16) |
| T-B | `contas/tests/test_controle_acesso.py:21` (`ROTAS_PUBLICAS`) | F1 (AD-006, varredura de rotas) | Ganha `/acessibilidade/`, `/acessibilidade/contraste/` e `/ajuda/` | Rotas públicas novas, marcadas com `@login_not_required` (RED-24, RED-30, RED-33) |
| T-C | `inovacoes/tests/test_views_sistema_design.py`: `test_toda_tela_estende_o_base_sem_estilo_proprio` (`len(telas) == 11`) e o conjunto `PECAS` | sistema-de-design DS-01 | 11 → 13 telas (Acessibilidade, Ajuda); `PECAS` ganha os templates parciais da R1 (ícones, barra, cabeçalho de página) | Telas e peças novas, que continuam sem estilo próprio |
| T-D | `inovacoes/tests/test_views_sistema_design.py`: fixture `paginas` | sistema-de-design DS-02 a DS-05 | Ganha as páginas "Acessibilidade" e "Ajuda" (anônimo e autenticado) | As garantias do base (uma folha, link de pular, marcos) passam a valer também nelas |

**Não mudam** (conferido): `<main id="conteudo">` exato (status, reaproveitar, acessibilidade da
alteração), `<header>` e `<footer>` sem atributo e `<a class="marca" href="/">` (DS-04),
`<span>ana</span>` e o `Sair` depois do `nav` (DS-05), `<form method="post" action="/sair/">`
(AUTH), primeiro focável "Ir para o conteúdo principal" → `#conteudo` (DS-03), o `<style>` igual
ao `kira.css` cru (DS-02), o `<title>` "{página} · Repositório de Inovações", os botões dentro de
`<main>` (DS-14, STAT, EDEX, REAP) e o formulário de confirmação da exclusão. Para isso a R1 põe
a barra de acessibilidade fora do `<header>`, a trilha entre o `<header>` e o `<main>` e o `<form>` do
contraste no fim do `<body>` (AD-015).

**Acrescentados no Design (autorizados em 2026-11-15):** T-E `indicadores/tests/test_views_painel.py:178`
(`"<svg" not in html` passa a olhar só o `<main>`: os ícones do menu são SVG) e T-F
`inovacoes/tests/test_views_sistema_design.py:177` (DS-05 passa a esperar `<span>Ana Souza</span>`:
a fixture tem nome completo e a RED-20 o mostra).

## Problem Statement

A v2 da `design-spec.md` redefine a casca de todas as telas: barra de acessibilidade do eMAG,
menu com ícone e página atual, cabeçalho de página com trilha, alto contraste e uma família de
componentes novos (cartão de inovação, etapas, linha do tempo, etiquetas de filtro, resumo de
erros, cartão de indicador). Se cada tela do redesign fizer a sua parte da casca, a consistência
(H4) e o AD-010 se perdem. A R1 entrega a fundação uma vez, testada, para as telas consumirem.

## Goals

- [x] Toda tela com a casca da §5 v2: barra de acessibilidade, faixa da marca, cabeçalho com menu de ícones e página atual, cabeçalho de página com trilha, rodapé com links de apoio.
- [x] Recursos do eMAG funcionando sem JavaScript: atalhos 1/2/3, página "Acessibilidade", alto contraste por formulário POST, persistente entre páginas.
- [x] `kira.css` com os tokens, a fonte Inter servida pelo projeto e os componentes da §6 v2 com todos os estados, nos pares de cor do DS-08 (inclusive no alto contraste).
- [x] Só os testes antigos listados acima (T-A a T-F, com os dois acrescentados no Design) mudam; a suíte e o build gate da Vercel (`config/tests`) passam.

## Code Reuse Analysis

| Item | Onde | Situação | Reuso |
| ---- | ---- | -------- | ----- |
| Base | `templates/base.html` | Link de pular, `header` com marca, `nav aria-label="Principal"` (3 links), usuário + Sair, `main#conteudo` com `role=status`, `footer` | Mantido; ganha a barra, a faixa, o menu novo e os blocos do cabeçalho de página |
| Folha | `templates/kira.css` (588 linhas) | Tokens §2–§3 v1, componentes v1, `.ciclo`, `.historico`, gráfico | Mantida e estendida; nada removido que uma tela use |
| Marca | `templates/marca.html` | Texto KIRA + tagline | Mantida |
| Visibilidade | `inovacoes/tests/visibilidade.py` (`exibido()`) | DOM parseado, L-028/L-030 | Toda AC de "exibido" da R1 |
| Testes de tokens e contraste | `inovacoes/tests/test_views_sistema_design.py` (`_regra`, `_token`, `_contraste`) | DS-06 a DS-09 | Estendidos com os tokens e pares novos, sem mudar os existentes |
| Estáticos | `STATIC_URL = "static/"`, `STATIC_ROOT = BASE_DIR / "staticfiles"` | Sem `STATICFILES_DIRS`, sem pasta `static/`; a Vercel serve `/static/` pela CDN depois do `collectstatic` (DEPL-10/11) | Ganha `STATICFILES_DIRS = [BASE_DIR / "static"]` só para a fonte |
| Rotas públicas | `@login_not_required` (AD-006) | Só `/entrar/` | Acessibilidade, contraste e ajuda entram na allowlist |

---

## Out of Scope

| Feature | Reason |
| ------- | ------ |
| Miolo das telas do §10 (login dividido, busca em destaque, cartões de inovação na lista, detalhe em duas colunas, fieldsets do formulário, cartões com variação do painel) | Features seguintes do redesign. A R1 só põe os componentes na folha e a casca nas telas. |
| Ação principal preenchida nas telas | O bloco existe na R1; cada tela o preenche no seu passe (a lista ganharia "Cadastrar inovação", texto novo na tela). |
| Descrição de página preenchida | Idem: o bloco existe, as telas o preenchem depois. |
| Título "Erro: … · KIRA" e troca do sufixo do `<title>` | O pedido mantém os textos atuais; o sufixo segue "· Repositório de Inovações". |
| Texto "Ir para o conteúdo" da v2 | Mantido "Ir para o conteúdo principal" (texto atual, DS-03). |
| Preferência de contraste gravada no perfil | Decisão do Discuss (cookie); nenhuma migration, nada no Neon. |
| Logo em imagem | Segue o texto KIRA (sistema-de-design). |
| Modo escuro | A spec de design não define. |
| Auditoria WCAG completa e SUS | Validação transversal no fim (RNF09, RNF01). |

---

## Assumptions & Open Questions

Propostas do Discuss confirmadas pelo usuário em 2026-11-15 (ver `context.md`).

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --------------------- | -------------- | --------- | ---------- |
| Onde mora o alto contraste | Cookie `kira_contraste=alto` (1 ano, `HttpOnly`, `SameSite=Lax`, `Secure` com `DEBUG` desligado), lido pelo base no servidor; "normal" apaga o cookie | Vale para quem não entrou (a barra está no login, §5.1); sobrevive ao logout, que limpa a sessão; sem migration nem passo no Neon. É o que a §5.5 descreve | y |
| Atalhos | `accesskey` 1, 2, 3 nos links da barra, como o eMAG prescreve; sem ouvinte de teclado. A página Acessibilidade traz a tabela de combinações (Alt+n no Chrome/Edge do Windows, Alt+Shift+n no Firefox, Control+Option+n no macOS) e o aviso de que um leitor de tela ou o sistema pode ter o mesmo atalho, e aí o dele vale | Nenhuma combinação é livre de conflito em todo navegador e tecnologia assistiva; o navegador escolhe o modificador, e o leitor de tela costuma ter precedência (WebAIM). A tabela é conferida na UAT | y |
| Ícones | Lucide, SVG embutido em parciais `templates/icones/*.html`, traço `currentColor`, `aria-hidden="true"` e `focusable="false"`; licença copiada em `templates/icones/LICENSE` | Lucide é ISC (permissiva; parte vem do Feather, MIT); o aviso de licença precisa acompanhar os arquivos copiados. Desenhar à mão não traz ganho | y |
| Página Acessibilidade e Ajuda públicas | `@login_not_required`; sem sessão, cabeçalho só com a marca | O login aponta para elas (§5.4); quem não consegue entrar precisa delas | y |
| Fonte na folha embutida | `kira.css` declara `@font-face` com `src: url(/static/fontes/inter-latin-wght-normal.woff2)`, literal; um teste amarra o caminho ao `STATIC_URL` e exige o arquivo achável pelo `finders` e copiado pelo `collectstatic`. O base faz `<link rel="preload">` com `{% static %}` | O `kira.css` cru é comparado ao `<style>` (DS-02); `{% static %}` dentro dele quebraria essa igualdade e misturaria template no CSS | y |
| Arquivo da fonte | Inter variável, subconjunto latino (pesos 400–800), woff2, com `OFL.txt` ao lado em `static/fontes/`; `font-display: swap` | Cobre o português; um arquivo só; a pilha da §3 segue de reserva | y |
| Menu no celular | **Itens quebram de linha (§5.2), sem `<details>`** | Um `<details>` sem JS fica fechado também no desktop (só `open` no servidor o mostraria, e aí abre aberto no celular); escondê-lo por CSS no desktop depende de `::details-content`, ainda sem suporte uniforme, e o leitor de tela anunciaria "recolhido". O teste REAP-28 (via `exibido()`) também reprovaria o menu num `details` fechado. Diverge do pedido | y |
| Link "Ajuda" do rodapé | Página pública `/ajuda/` curta: como buscar, como cadastrar, como avançar status e a quem recorrer (administrador do sistema) | Não existe página de ajuda; um link sem destino seria pior (H10) | y |
| Escopo nas telas existentes | Todas as telas passam a preencher o bloco do h1; as nove da tabela da §5.3 ganham a trilha; login, 403, 404 e 500 ficam sem trilha | A forma do cabeçalho fica igual em todas (H4) sem trocar texto de tela | y |
| Foco no alvo do atalho | Sem `tabindex` em `main` e `nav`; o salto pela âncora move o ponto de partida da navegação sequencial nos navegadores atuais | `<main id="conteudo">` exato é fixado por 3 arquivos de teste; diverge da §5.1 (`tabindex="-1"`) | y |
| Número do atalho | `<kbd aria-hidden="true">1</kbd>` logo depois do link, fora dele | O texto do link segue exato (DS-03); o leitor de tela já anuncia o `accesskey` | y |
| Barra fora do `header` | A barra de acessibilidade é um `div.barra-acessibilidade` antes do `<header>`, com o `nav aria-label="Atalhos de acessibilidade"` e o botão de contraste; o `<form>` fica no fim do `<body>` (ajuste do Design, AD-015) | O `<header>` segue sem atributo (DS-04) e os testes que buscam `href` dentro dele para o anônimo seguem valendo | y |
| Seletor do alto contraste | `:root[data-contraste=alto]`, sem aspas | AD-010: a folha não tem `="` | y |
| Página atual do menu | `aria-current="page"` no destino exato (lista, cadastro, painel); `aria-current="true"` em Inovações nas telas da seção (detalhe, editar, excluir, avançar status, sinalizar, não encontrada, acesso negado); nenhum nas outras | §5.2 v2 | y |
| Nome no cabeçalho | `get_full_name` ou, vazio, o `username`, num `<span>` sem atributo; as iniciais num `span` `aria-hidden` | §5 v2; mantém o `<span>ana</span>` do DS-05 | y |
| Idioma dos critérios | EARS em inglês, restante em português | Padrão das features anteriores | y |

**Open questions:** none — todas resolvidas no Discuss de 2026-11-15 e registradas acima.

---

## User Stories

### P1: Tokens, fonte e componentes da v2 na folha ⭐ MVP

**User Story**: Como quem constrói as telas do redesign, quero os tokens e os componentes da v2
prontos na `kira.css`, com todos os estados, para nenhuma tela recriar estilo (AD-010, H4).

**Why P1**: As features seguintes do redesign dependem disto.

**Acceptance Criteria**:

1. RED-01: The stylesheet SHALL declare on `:root` the v2 tokens with the exact values of §2 and §4: `--brand-blue-hover: #28529A`, `--borda-campo: #7A879B`, `--on-brand: #FFFFFF`, `--info-tint: #E8EFFA`, `--success-tint: #EDF7F1`, `--warning-tint: #FBF3E0`, `--error-tint: #FBEAE9`, `--trilho: #EEF2F8`, `--raio-cartao: 16px`, `--raio-pilula: 999px`, `--numeros: tabular-nums`, keeping every v1 token value of DS-06.
2. RED-02: The stylesheet SHALL give `.cartao` `border-radius: var(--raio-cartao)` and a `box-shadow` whose every color has alpha ≤ 0.12.
3. RED-03: The stylesheet SHALL give text fields, selects and textareas a `1.5px solid var(--borda-campo)` border, and the test SHALL confirm `--borda-campo` reaches 3:1 against `--surface` and `--bg`.
4. RED-04: The stylesheet SHALL apply `font-variant-numeric: var(--numeros)` to `time`, `.total`, `.numero`, the pagination (`[aria-label=Paginação]`), `.cartao-indicador__numero`, `.variacao` and `.linha-do-tempo time`.
5. RED-05: The stylesheet SHALL declare an `@font-face` for `Inter` with `font-display: swap`, a `font-weight` range `400 800` and `src: url(/static/fontes/inter-latin-wght-normal.woff2)`, and `--font-sans` SHALL keep the §3 value.
6. RED-06: WHEN `collectstatic` runs THEN the system SHALL copy `fontes/inter-latin-wght-normal.woff2` under `STATIC_ROOT`, and the URL in the `@font-face` SHALL equal `/` + `STATIC_URL` + that path.
7. RED-07: The system SHALL ship the font's license (`static/fontes/OFL.txt`) and the icon set's license (`templates/icones/LICENSE`) next to the copied files.
8. RED-08: The system SHALL NOT load any stylesheet, font, script or image from another origin (no `http://` or `https://` in `<link>`, `<script>`, `<img>`, `@import` or `url(`).
9. RED-09: The stylesheet SHALL define the v2 components of §6 under these classes, each with every state the §6 lists: button (`:hover` with `--brand-blue-hover`, `:focus-visible`, `:active`, `[aria-disabled=true]` and `:disabled` with `--bg`/`--text-muted` and `cursor: not-allowed`), field (`[aria-invalid=true]` with a `2px solid var(--error)` border), `.selo` (pill, `--raio-pilula`), `.cartao-inovacao` (`:hover` border `--brand-blue`), `.etapas` (`--concluida`, `--atual`, `--futura`), `.linha-do-tempo`, `.cartao-contato` (4px top border `--brand-blue`), `.grupo` (fieldset with numbered legend), `.etiqueta-filtro` (and its remove link `:hover`/`:focus-visible`), `.resumo-erros`, `.barra-acoes`, `.cartao-indicador` with `.variacao--alta`, `--queda`, `--igual`, and `.esqueleto` (loading).
10. RED-10: The system SHALL use in the components only text/background and component/background pairs listed in §2 v2, each verified by the DS-08 contrast test (4.5:1 for text, 3:1 for component boundaries and bars).
11. RED-11: WHERE the user prefers reduced motion the stylesheet SHALL disable the transitions and animations of the new components, including `.esqueleto` (DS-09 extended).
12. RED-12: The stylesheet SHALL NOT declare `position: fixed`, and SHALL NOT declare a `width` or `min-width` above `320px` outside a `max-width` context, so the layout reflows at 200% zoom (WCAG 1.4.4, 1.4.10).

**Independent Test**: rodar os testes da folha; abrir qualquer tela no navegador e ver a Inter
carregada de `/static/` (aba Rede), sem nenhuma requisição a outro domínio.

---

### P1: Barra de acessibilidade e cabeçalho do sistema ⭐ MVP

**User Story**: Como usuário que navega por teclado ou leitor de tela, quero atalhos para o
conteúdo, o menu e a busca, e um menu que diga onde estou (eMAG, H1, H7).

**Why P1**: Recurso obrigatório do eMAG (§8) e base da navegação de toda tela.

**Acceptance Criteria**:

1. RED-13: The system SHALL render on every page, before the `<header>`, a `nav aria-label="Atalhos de acessibilidade"` whose first link is the current skip link ("Ir para o conteúdo principal" → `#conteudo`, `accesskey="1"`), followed by a visible `<kbd aria-hidden="true">1</kbd>`; it SHALL remain the first focusable element (DS-03).
2. RED-14: WHILE the user is authenticated the system SHALL also render the links "Ir para o menu" (`#menu`, `accesskey="2"`) and "Ir para a busca" (`accesskey="3"`; `#id_q` on the list, `/inovacoes/#id_q` elsewhere), each followed by its `kbd`.
3. RED-15: IF the user is anonymous THEN the system SHALL render no `accesskey="2"` nor `accesskey="3"`.
4. RED-16: WHILE the user is authenticated the system SHALL render the main navigation as `nav id="menu" aria-label="Principal"` with, in order, "Inovações" (`/inovacoes/`), "Cadastrar inovação" (`/inovacoes/nova/`) and "Indicadores" (`/indicadores/`), each with an inline `<svg aria-hidden="true" focusable="false">` icon (lightbulb, circle-plus, chart) before its text.
5. RED-17: WHEN the page is the exact destination of a menu item THEN the system SHALL set `aria-current="page"` on that item only.
6. RED-18: WHEN the page belongs to the Inovações section (detail, edit, delete, advance status, signal reuse, not found, access denied) THEN the system SHALL set `aria-current="true"` on "Inovações" only.
7. RED-19: The stylesheet SHALL mark the current item with the `--info-tint` background and a `3px` bottom bar in `--brand-blue`, so the current page is not conveyed by color alone.
8. RED-20: WHILE the user is authenticated the system SHALL render in the user area, after the menu, the full name (or the username when the name is empty) in a `<span>` with no attribute, the decorative initials in an `aria-hidden` element, and the current "Sair" form.
9. RED-21: The system SHALL render a decorative 4px band with `--brand-gradient` between the accessibility bar and the `<header>`, with no text and `aria-hidden="true"`.
10. RED-22: The stylesheet SHALL let the menu items wrap on narrow screens without becoming icon-only, with a 44px minimum height for menu items, bar links and buttons.

**Independent Test**: entrar, apertar a combinação do atalho 2 e cair no menu; na lista, ver
"Inovações" marcado; no detalhe, ver "Inovações" marcado como seção.

---

### P1: Alto contraste ⭐ MVP

**User Story**: Como usuário com baixa visão, quero ligar um tema de alto contraste que valha em
todas as páginas, inclusive antes de entrar (eMAG).

**Why P1**: Recurso do eMAG listado na §8.

**Acceptance Criteria**:

1. RED-23: The system SHALL render, on every page with a request, a `form id="form-contraste" method="post"` at the end of the `<body>` with the CSRF token and a hidden `voltar_para` with the current path and query, and in the accessibility bar a button "Alto contraste" (`form="form-contraste"`, `name="contraste"`, value opposite to the current state) with a half-circle icon and `aria-pressed` equal to the current state (`"true"` or `"false"`).
2. RED-24: WHEN `/acessibilidade/contraste/` receives a POST with `contraste=alto` THEN the system SHALL set the cookie `kira_contraste=alto` (`max_age` one year, `HttpOnly`, `SameSite=Lax`, `Secure` when `DEBUG` is off) and redirect with 302 to `voltar_para`.
3. RED-25: WHEN it receives `contraste=normal` THEN the system SHALL delete the cookie and redirect with 302 to `voltar_para`.
4. RED-26: WHILE the request carries `kira_contraste=alto` the system SHALL render `<html lang="pt-br" data-contraste="alto">` on the first response, with no client script.
5. RED-27: The stylesheet SHALL redefine under `:root[data-contraste=alto]` every token with the exact §2 v2 high-contrast value, and every text and component pair of RED-10 SHALL reach the same thresholds with those values.
6. RED-28: WHILE high contrast is on the stylesheet SHALL underline links, hide every `.decorativo` element and the gradient band, and give `.selo`, `.alerta`, `.variacao` and the chart bars a `1px solid` border in the text color.

**Independent Test**: no login, clicar "Alto contraste", ver o fundo preto; entrar e navegar:
continua; clicar de novo: volta ao normal.

---

### P1: Cabeçalho de página e rodapé ⭐ MVP

**User Story**: Como usuário, quero que toda tela abra com a trilha e o título no mesmo lugar e
feche com os links de apoio (H1, H4, H10).

**Why P1**: §5.3 e §5; base das telas do redesign.

**Acceptance Criteria**:

1. RED-29: The base SHALL render the `trilha` block between the `<header>` and `<main id="conteudo">`, and SHALL open the `main` with the messages `role="status"` and then a page header with the blocks `titulo` (inside the single `h1`), `descricao` and `acao_principal`, in this DOM order (AD-015).
2. RED-30: The system SHALL render, on the nine screens of §5.3 and on "Ajuda" (trail "Ajuda"), a `nav aria-label="Você está em"` with an `ol` whose items follow the §5.3 table, the intermediate items as links and the last as text with `aria-current="page"`; the separator "›" SHALL come from CSS, not from the HTML.
3. RED-31: The system SHALL render the `h1` of every screen except the login through the `titulo` block, with the same text as today, and exactly one `h1` per page; the login keeps "Entrar" inside its card until its own pass.
4. RED-32: The system SHALL render in the `<footer>` the current text "KIRA · Repositório de Inovações · uso interno" and the links "Acessibilidade" (`/acessibilidade/`) and "Ajuda" (`/ajuda/`).

**Independent Test**: abrir o detalhe e ler "Inovações › {título}" acima do h1; no rodapé,
seguir "Ajuda".

---

### P1: Páginas "Acessibilidade" e "Ajuda" ⭐ MVP

**User Story**: Como qualquer pessoa, logada ou não, quero saber o compromisso de
acessibilidade, os atalhos e a quem recorrer (eMAG, H10).

**Why P1**: §5.4; o rodapé e a barra apontam para elas.

**Acceptance Criteria**:

1. RED-33: WHEN anyone (anonymous or authenticated) requests `/acessibilidade/` THEN the system SHALL answer 200 with the trail "Acessibilidade", the `h1` "Acessibilidade" and the `h2` sections "Compromisso", "Atalhos de teclado", "Alto contraste", "Ampliação" and "Relatar uma barreira".
2. RED-34: The "Atalhos de teclado" section SHALL contain a table (`caption`, `th scope`) with the three shortcuts and the combination per browser (Chrome e Edge no Windows: Alt + n; Firefox: Alt + Shift + n; macOS: Control + Option + n), and the note that a screen reader or the system may own the same combination.
3. RED-35: WHEN anyone requests `/ajuda/` THEN the system SHALL answer 200 with the `h1` "Ajuda" and the `h2` sections "Buscar uma inovação", "Cadastrar uma inovação", "Avançar o status" and "Precisa de ajuda?".
4. RED-36: WHILE the user is anonymous the pages SHALL render the header with the brand only, without the main menu nor the user area.

**Independent Test**: sem login, abrir `/acessibilidade/` pelo link da barra do login.

---

## Edge Cases

- RED-37: IF `voltar_para` is missing, empty or not a safe local URL (`url_has_allowed_host_and_scheme`) THEN the contrast view SHALL redirect to `/`.
- RED-38: IF `contraste` is missing or not in {`alto`, `normal`} THEN the contrast view SHALL answer 400 and SHALL NOT change the cookie.
- RED-39: IF the contrast view receives GET THEN it SHALL answer 405; IF the CSRF token is missing THEN 403 (CSRF padrão).
- RED-40: IF the cookie `kira_contraste` holds any value other than `alto` THEN the system SHALL render the normal theme and `aria-pressed="false"`.
- RED-41: IF the 500 page renders without a request THEN the system SHALL still render the skip link with `accesskey="1"`, the band, the brand and the stylesheet, and SHALL omit the contrast form (no CSRF token).
- RED-42: WHEN the same contrast value is posted twice THEN the system SHALL answer the same way both times (idempotent: the value is explicit, not a toggle).

## Implicit-requirement dimensions

| Dimension | Resolução |
| --------- | --------- |
| Input validation & bounds | RED-37, RED-38, RED-40 |
| Failure / partial-failure states | RED-41 (500 sem request); fonte ausente cai na pilha da §3 (`font-display: swap`, RED-05) |
| Idempotency / retry | RED-42 |
| Auth boundaries & rate limits | RED-15, RED-36; rotas públicas explícitas (AD-006, T-B). Rate limit N/A: a rota só grava um cookie no próprio cliente |
| Concurrency / ordering | N/A: nenhum estado no servidor |
| Data lifecycle / expiry | Cookie de 1 ano; "normal" apaga (RED-24, RED-25) |
| Observability | N/A: preferência de apresentação, sem evento de negócio |
| External-dependency failure | RED-08: nenhum recurso externo |
| State-transition integrity | RED-26, RED-40: só dois estados, valor explícito |

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| -------------- | ----- | ----- | ------ |
| RED-01 | P1: Folha | Execute | Verified |
| RED-02 | P1: Folha | Execute | Verified |
| RED-03 | P1: Folha | Execute | Verified |
| RED-04 | P1: Folha | Execute | Verified |
| RED-05 | P1: Folha | Execute | Verified |
| RED-06 | P1: Folha | Execute | Verified |
| RED-07 | P1: Folha | Execute | Verified |
| RED-08 | P1: Folha | Execute | Verified |
| RED-09 | P1: Folha | Execute | Verified |
| RED-10 | P1: Folha | Execute | Verified |
| RED-11 | P1: Folha | Execute | Verified |
| RED-12 | P1: Folha | Execute | Verified |
| RED-13 | P1: Barra e cabeçalho | Execute | Verified |
| RED-14 | P1: Barra e cabeçalho | Execute | Verified |
| RED-15 | P1: Barra e cabeçalho | Execute | Verified |
| RED-16 | P1: Barra e cabeçalho | Execute | Implementing (risco residual aceito) |
| RED-17 | P1: Barra e cabeçalho | Execute | Verified |
| RED-18 | P1: Barra e cabeçalho | Execute | Verified |
| RED-19 | P1: Barra e cabeçalho | Execute | Verified |
| RED-20 | P1: Barra e cabeçalho | Execute | Verified |
| RED-21 | P1: Barra e cabeçalho | Execute | Verified |
| RED-22 | P1: Barra e cabeçalho | Execute | Implementing (risco residual aceito) |
| RED-23 | P1: Alto contraste | Execute | Verified |
| RED-24 | P1: Alto contraste | Execute | Verified |
| RED-25 | P1: Alto contraste | Execute | Verified |
| RED-26 | P1: Alto contraste | Execute | Verified |
| RED-27 | P1: Alto contraste | Execute | Verified |
| RED-28 | P1: Alto contraste | Execute | Verified |
| RED-29 | P1: Cabeçalho de página | Execute | Verified |
| RED-30 | P1: Cabeçalho de página | Execute | Verified |
| RED-31 | P1: Cabeçalho de página | Execute | Verified |
| RED-32 | P1: Cabeçalho de página | Execute | Verified |
| RED-33 | P1: Páginas de apoio | Execute | Verified |
| RED-34 | P1: Páginas de apoio | Execute | Verified |
| RED-35 | P1: Páginas de apoio | Execute | Verified |
| RED-36 | P1: Páginas de apoio | Execute | Verified |
| RED-37 | Edge | Execute | Verified |
| RED-38 | Edge | Execute | Verified |
| RED-39 | Edge | Execute | Verified |
| RED-40 | Edge | Execute | Verified |
| RED-41 | Edge | Execute | Verified |
| RED-42 | Edge | Execute | Verified |

**Coverage:** 42 total, 42 mapped to tasks (T1–T20), 0 unmapped. 40 `Verified`; RED-16 e RED-22 com risco residual de teste aceito pelo usuário em 2026-11-15 (`validation.md`, Decisão do usuário). A regra de teste da feature (exibição) tem o mesmo risco.

**Regras de teste para a feature toda:** toda AC de "está exibido" usa `exibido()` de
`inovacoes/tests/visibilidade.py` sobre a página inteira (L-028, L-030) e já cobre `disabled`,
CSS `display: none` em seletor da própria folha e `role="presentation"` (vetores da F6); toda AC
afirmada na camada que descreve (L-005): o que é de tela, na tela; o que é de folha, na folha.

---

## Success Criteria

- [x] Só os testes T-A a T-F mudaram, e a suíte inteira passa (943 → 1326).
- [x] `config/tests` (build gate da Vercel) passa e o `collectstatic` copia a fonte.
- [x] Nenhuma requisição a outro domínio em nenhuma tela (RED-08, por teste e na conferência local).
- [x] Conferência no navegador: atalhos, menu atual, alto contraste do login ao painel, zoom de 200% sem rolagem horizontal (feita pelo usuário no servidor local em 2026-11-15, tudo certo).
- [ ] O Verifier dá PASS em `validation.md` — não: FAIL na iteração 2 só por lacuna de teste, risco aceito pelo usuário.
