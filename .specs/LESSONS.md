# LESSONS - auto-maintained by scripts/lessons.py

> Machine-owned. Do NOT hand-edit. Changes are overwritten on the next `lessons.py` write.
> Canonical state lives in `.specs/lessons.json`. Edit lessons only via the script.
> promote_threshold=2 distinct features · window_days=45 · quarantine_threshold=2

## Confirmed (load these at Specify/Design)

Corroborated across multiple features. Safe to apply as guidance.

### L-003 - When an AC restricts a screen to one role, test that other roles holding framework access are denied the screen, not only that fields are hidden
- signal: `ac_gap` · recurrence: 2 feature(s) · scope: `admin` · harmful: 0
- features: autenticacao, edicao-exclusao
- evidence: AUTH-22 contas/tests/test_admin_perfil.py:46 (admin) (+1 more)
- last seen: 2026-10-11T18:10:26Z

### L-005 - Assert every clause of a compound AC at the layer the AC describes; a backend test does not cover a screen-level outcome
- signal: `ac_gap` · recurrence: 2 feature(s) · scope: `routes` · harmful: 0
- features: autenticacao, edicao-exclusao
- evidence: AUTH-13 AUTH-23 AUTH-07 validation.md Fix 4 (routes) (+1 more)
- last seen: 2026-10-11T18:10:26Z

### L-028 - When asserting that a control or text is displayed, reject hidden, inert and aria-hidden on the element and on every ancestor, not only on the matched tag
- signal: `surviving_mutant` · recurrence: 2 feature(s) · scope: `tests` · harmful: 0
- features: ciclo-de-vida-status, reaproveitamento-indicadores
- evidence: validation.md iteracao 5, E9/E10/E11/E16 (STAT-03, STAT-38, STAT-40), inovacao_detail.html:59-64 (tests) (+1 more)
- last seen: 2026-10-19T17:11:28Z

### L-030 - Assert that content is displayed on the parsed DOM of the whole page, skipping comments, template, closed details and any ancestor with hidden, inert or aria-hidden in any case, not by regex on the raw HTML
- signal: `surviving_mutant` · recurrence: 2 feature(s) · scope: `tests` · harmful: 0
- features: ciclo-de-vida-status, reaproveitamento-indicadores
- evidence: validation.md iteracao 6, F1/F2/F3/F4/F5/F14/F16/F18 (STAT-01, 03, 04, 38, 39, 40, 41), inovacoes/tests/test_views_detalhe.py:438-449 (tests) (+2 more)
- last seen: 2026-10-19T17:39:06Z

### L-044 - When asserting that content is displayed, also forbid display none, visibility hidden and zero opacity in the stylesheet rules that select it, because a DOM check cannot see CSS hiding
- signal: `surviving_mutant` · recurrence: 2 feature(s) · scope: `templates-css` · harmful: 1
- features: reaproveitamento-indicadores, fundacao-do-redesign
- evidence: validation.md iteracao 3, N02/N10 (REAP-30, REAP-31, REAP-36), templates/kira.css:536-565 (templates-css) (+1 more)
- last seen: 2026-11-23T23:33:59Z

## Candidates (under observation - do NOT load as guidance yet)

Seen once or not yet corroborated. Tracked, not trusted.

### L-016 - Select routes for an authorization sweep by any captured URL parameter, not by a literal converter string, so a new route with another parameter name is still swept
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `tests` · harmful: 0
- features: edicao-exclusao
- evidence: validation.md M24 (inovacoes/tests/test_controle_autoria.py:26) (tests)
- last seen: 2026-10-11T18:10:26Z

### L-017 - When a test forbids removing a CSS property, reject every equivalent form (unit-suffixed zero, longhand properties, transparent color), not just the keyword
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `templates-css` · harmful: 0
- features: sistema-de-design
- evidence: S25 inovacoes/tests/test_views_sistema_design.py:210 (templates-css)
- last seen: 2026-10-12T01:01:27Z

### L-018 - Keep content embedded in every page free of any text that existing tests search for in the page, including plain words in comments
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `templates-css` · harmful: 0
- features: sistema-de-design
- evidence: S26 contas/tests/test_views_home.py:49 vs templates/kira.css:6 (templates-css)
- last seen: 2026-10-12T01:01:27Z

### L-019 - When a page lists the child records of one parent, seed records of another parent and assert they are not listed
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `views` · harmful: 0
- features: ciclo-de-vida-status
- evidence: validation.md M11 (inovacoes/views.py:132, STAT-24) (views)
- last seen: 2026-10-18T20:17:58Z

### L-020 - Check color contrast on the text and background pair each rule renders, not on each color token's membership in an approved set
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `css` · harmful: 0
- features: ciclo-de-vida-status
- evidence: validation.md M27 (templates/kira.css:510, STAT-37) (css) (+1 more)
- last seen: 2026-10-18T20:31:51Z

### L-021 - When the base layout appends a site suffix to the page title, write title criteria as starting with the page name, not as an exact value
- signal: `spec_precision_gap` · recurrence: 1 feature(s) · scope: `specs` · harmful: 0
- features: ciclo-de-vida-status
- evidence: STAT-06/STAT-34 title, test_views_status.py:50 (specs) (+2 more)
- last seen: 2026-10-18T20:45:23Z

### L-022 - In static CSS color checks, treat every background longhand such as background-image as a background, not only background and background-color
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `css` · harmful: 0
- features: ciclo-de-vida-status
- evidence: validation.md iteracao 3 A1/A2 (templates/kira.css:521, STAT-37; test_views_sistema_design.py:597-599) (css)
- last seen: 2026-10-18T20:45:23Z

### L-023 - Select a component's CSS rules by any selector that contains its class, not only selectors that start with it
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `css` · harmful: 0
- features: ciclo-de-vida-status
- evidence: validation.md iteracao 3 A6/A7 (templates/kira.css:521, STAT-37; test_views_sistema_design.py:536-543) (css)
- last seen: 2026-10-18T20:45:23Z

### L-024 - When an amendment relaxes a page-wide negative assertion for some roles, keep the page-wide assertion for every role whose rule did not change
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `tests` · harmful: 0
- features: ciclo-de-vida-status
- evidence: validation.md Iteração 4 R1 (STAT-05); inovacoes/tests/test_views_detalhe.py:363-376 (tests)
- last seen: 2026-10-18T21:20:47Z

### L-025 - When widening an HTML-matching test helper to accept new attributes, accept only the expected attributes so a hidden or aria-hidden control still fails
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `tests` · harmful: 0
- features: ciclo-de-vida-status
- evidence: validation.md Iteração 4 R2 (STAT-03); inovacoes/tests/test_views_detalhe.py:197 (tests)
- last seen: 2026-10-18T21:20:47Z

### L-026 - When an AC requires a control to stay keyboard reachable, require it in the sequential Tab order, because tabindex -1 keeps it focusable but removes it from Tab
- signal: `spec_precision_gap` · recurrence: 1 feature(s) · scope: `specs` · harmful: 0
- features: ciclo-de-vida-status
- evidence: validation.md Iteração 4 D12 (STAT-41) (specs)
- last seen: 2026-10-18T21:20:47Z

### L-027 - Run every page-wide negative assertion for each account variant of the denied role, including staff and superuser flags, in every state of the screen
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `tests` · harmful: 0
- features: ciclo-de-vida-status
- evidence: validation.md iteracao 5, E2b (STAT-05), inovacao_detail.html:68 (tests)
- last seen: 2026-10-18T21:40:53Z

### L-029 - When an AC requires an action link to be displayed, also require it in the sequential Tab order and exposed to assistive technology
- signal: `spec_precision_gap` · recurrence: 1 feature(s) · scope: `specs` · harmful: 0
- features: ciclo-de-vida-status
- evidence: validation.md iteracao 5, E17 (STAT-03, STAT-34), inovacao_detail.html:63 (specs)
- last seen: 2026-10-18T21:40:53Z

### L-031 - Decode HTML entities before a page-wide negative text assertion, so an encoded label cannot slip past it
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `tests` · harmful: 0
- features: ciclo-de-vida-status
- evidence: validation.md iteracao 6, F17 (STAT-05), inovacoes/tests/test_views_detalhe.py:379,403,415,432 (tests)
- last seen: 2026-10-18T21:57:48Z

### L-032 - When an AC says a control or text SHALL be displayed, state whether it must also be exposed to assistive technology
- signal: `spec_precision_gap` · recurrence: 1 feature(s) · scope: `specs` · harmful: 0
- features: ciclo-de-vida-status
- evidence: validation.md iteracao 6, F15/F19 (STAT-38, STAT-40) (specs)
- last seen: 2026-10-18T21:57:48Z

### L-033 - Do not add defensive branches for states the spec declares impossible, because no test can reach them and they survive mutation
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `views` · harmful: 0
- features: reaproveitamento-indicadores
- evidence: validation.md M09 (inovacoes/views.py InovacaoReaproveitarView.form_valid) (views)
- last seen: 2026-10-19T17:11:28Z

### L-034 - Do not add an empty order_by() to clear Meta.ordering in a Django GROUP BY subquery, because Django 3.1 and later already ignore Meta.ordering there
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `models` · harmful: 0
- features: reaproveitamento-indicadores
- evidence: validation.md M17 (inovacoes/models.py UnidadeQuerySet.com_indicadores) (models)
- last seen: 2026-10-19T17:11:28Z

### L-035 - Do not nest a savepoint inside a method's own atomic block when the caught database error is re-raised as another exception, because the outer block already rolls back
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `models` · harmful: 0
- features: reaproveitamento-indicadores
- evidence: validation.md M06 (inovacoes/models.py registrar_reaproveitamento) (models)
- last seen: 2026-10-19T17:11:28Z

### L-036 - When an AC says a select has no preselected option, state whether the empty placeholder option that Django renders as selected counts
- signal: `spec_precision_gap` · recurrence: 1 feature(s) · scope: `specs` · harmful: 0
- features: reaproveitamento-indicadores
- evidence: validation.md G1 (REAP-04) (specs)
- last seen: 2026-10-19T17:11:28Z

### L-037 - When an AC denies Django admin pages to a role, state the expected response per account flag, because staff accounts get 403 and non-staff accounts are redirected to the admin login
- signal: `spec_precision_gap` · recurrence: 1 feature(s) · scope: `specs` · harmful: 0
- features: reaproveitamento-indicadores
- evidence: validation.md G2 (REAP-26) (specs)
- last seen: 2026-10-19T17:11:28Z

### L-038 - When an AC fixes chart geometry, state the plot width in drawing units and the numeric format of the rendered attributes
- signal: `spec_precision_gap` · recurrence: 1 feature(s) · scope: `specs` · harmful: 0
- features: reaproveitamento-indicadores
- evidence: validation.md G4 (REAP-35) (specs)
- last seen: 2026-10-19T17:11:28Z

### L-039 - When an AC requires a visible label for every chart item, state the truncation rule for long labels and where the full text stays available
- signal: `spec_precision_gap` · recurrence: 1 feature(s) · scope: `specs` · harmful: 0
- features: reaproveitamento-indicadores
- evidence: validation.md G5 (REAP-36) (specs)
- last seen: 2026-10-19T17:11:28Z

### L-040 - When fixing a weak assertion pattern, apply the fix to every test of the feature that asserts the same kind of outcome, not only to the tests named by the surviving mutants
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `tests` · harmful: 0
- features: reaproveitamento-indicadores
- evidence: validation.md iteracao 2, X01/Y01 (REAP-28, REAP-29) left out of Fix 1 (tests)
- last seen: 2026-10-19T17:39:06Z

### L-041 - Do not add a conjunct to a guard when another conjunct already implies it, because the redundant condition survives mutation
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `domain` · harmful: 0
- features: reaproveitamento-indicadores
- evidence: validation.md iteracao 2, C07 (indicadores/graficos.py:46) (domain)
- last seen: 2026-10-19T17:39:06Z

### L-042 - When asserting that a form control is offered, reject disabled on the control and on every ancestor fieldset, because a disabled control still renders but cannot be used
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `tests` · harmful: 0
- features: reaproveitamento-indicadores
- evidence: validation.md iteracao 3, N04/N13 (REAP-03), inovacao_reaproveitar.html:18-22 (tests)
- last seen: 2026-10-19T18:41:08Z

### L-043 - Whitelist the attributes of every SVG element a test asserts as visible text, because display, visibility and opacity presentation attributes hide it without hidden or aria-hidden
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `tests` · harmful: 0
- features: reaproveitamento-indicadores
- evidence: validation.md iteracao 3, N01/N12 (REAP-36), indicadores/templates/indicadores/grafico.html:10-12 (tests)
- last seen: 2026-10-19T18:41:08Z

### L-045 - When asserting table semantics, reject a role attribute on the table or its cells that overrides the native role
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `tests` · harmful: 0
- features: reaproveitamento-indicadores
- evidence: validation.md iteracao 3, N05 (REAP-46), indicadores/templates/indicadores/painel.html:20 (tests)
- last seen: 2026-10-19T18:41:08Z

### L-046 - When an AC binds a documented command to a target environment, assert the command and its target on the same line, not only that both terms appear in the section
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `docs` · harmful: 0
- features: deploy-producao
- evidence: validation.md M13 README.md:43-44 (DEPL-17) config/tests/test_documentacao_deploy.py:83 (docs)
- last seen: 2026-10-27T18:29:58Z

### L-047 - When a test shells out to git or another configurable tool, isolate the user's global and system config so the result does not depend on who runs it
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `tests` · harmful: 0
- features: deploy-producao
- evidence: validation.md iteracao 3 probe P1, config/tests/test_vercelignore.py:21-29 (DEPL-18) (tests)
- last seen: 2026-10-27T19:01:23Z

### L-048 - When an AC requires backdated records, bound each generated date below the start of the run, not only by order and an upper limit, because dates stamped at load time still satisfy the order
- signal: `spec_precision_gap` · recurrence: 1 feature(s) · scope: `seed-data` · harmful: 0
- features: acervo-realista
- evidence: validation.md G1: ACER-14/ACER-16, mutants M07 and M18 (seed-data)
- last seen: 2026-10-27T20:12:21Z

### L-049 - When a spec assumption fixes who performs a generated action, turn it into an AC with a test, because an assumption without an AC is never checked
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `seed-data` · harmful: 0
- features: acervo-realista
- evidence: validation.md G2: M15 at inovacoes/acervo.py:1441 (seed-data)
- last seen: 2026-10-27T20:12:21Z

### L-050 - When an AC names which icon each item shows, assert each item's icon against its source file, not only that some decorative icon is present
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `tests` · harmful: 0
- features: fundacao-do-redesign
- evidence: RED-16, M43 (validation.md) (tests)
- last seen: 2026-11-15T16:26:31Z

### L-051 - When an AC sets a minimum size for every element of a kind, check existing variants such as compact buttons against it and either exempt them in the spec or test them
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `specs` · harmful: 0
- features: fundacao-do-redesign
- evidence: RED-22, M42; templates/kira.css:389-392 (specs)
- last seen: 2026-11-15T16:26:31Z

### L-052 - When an AC forbids a responsive state such as icon-only menu items, assert that no media query rule hides or shrinks the item text
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `css` · harmful: 0
- features: fundacao-do-redesign
- evidence: RED-22, M41 (validation.md) (css) (+1 more)
- last seen: 2026-11-15T18:15:04Z

### L-053 - When the design source lists a component state without a value, state in the AC what the state must change, so the test asserts a value rather than any declaration
- signal: `spec_precision_gap` · recurrence: 1 feature(s) · scope: `specs` · harmful: 0
- features: fundacao-do-redesign
- evidence: RED-09 :active (inovacoes/tests/test_folha_v2.py:265) (specs)
- last seen: 2026-11-15T16:26:31Z

### L-054 - When asserting a minimum target size in the stylesheet, check every rule that can match the element, including attribute, child and universal selectors and max-height, not only rules whose selector names the element
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `css` · harmful: 0
- features: fundacao-do-redesign
- evidence: N02, N03, N04 (RED-22) (css)
- last seen: 2026-11-15T18:15:04Z

### L-055 - When a test parses CSS declarations, decode CSS escapes in property names and values before matching, because escaped display none still hides content
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `css` · harmful: 0
- features: fundacao-do-redesign
- evidence: N17, N18 (regra de teste) (css)
- last seen: 2026-11-15T18:15:04Z

### L-056 - When a stylesheet guard lists ways to hide content, also catch near-zero values, every clip-path inset form, overflow set in another rule, transparent or background-colored text, off-screen positioning and content-visibility
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `css` · harmful: 0
- features: fundacao-do-redesign
- evidence: N07, N08, N10, N11, N19, N20, N21 (regra de teste) (css)
- last seen: 2026-11-15T18:15:04Z

### L-057 - When a test compares rendered output with a production asset file, also pin a fixed property of that asset from the spec, because a wrong asset file is its own oracle
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `tests` · harmful: 0
- features: fundacao-do-redesign
- evidence: N27 (RED-16) (tests)
- last seen: 2026-11-15T18:15:04Z

### L-058 - When a page has mutually exclusive states such as results and an empty state, assert in each state that the content of the other state is absent
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `tests` · harmful: 0
- features: redesign-consulta
- evidence: M27 inovacoes/templates/inovacoes/inovacao_list.html:70 (tests)
- last seen: 2026-11-20T03:16:36Z

### L-059 - When an AC writes a value in parentheses after a field label, state whether the value is shown beside the label or as the field value
- signal: `spec_precision_gap` · recurrence: 1 feature(s) · scope: `specs` · harmful: 0
- features: redesign-consulta
- evidence: RCON-33 (specs)
- last seen: 2026-11-20T03:16:36Z

### L-060 - When an AC requires a caption or other text only for assistive technology, state its exact text
- signal: `spec_precision_gap` · recurrence: 1 feature(s) · scope: `specs` · harmful: 0
- features: redesign-consulta
- evidence: RCON-35 (specs)
- last seen: 2026-11-20T03:16:36Z

### L-061 - Before a design names a framework helper, check its output against the literal example in the AC
- signal: `spec_deviation` · recurrence: 1 feature(s) · scope: `design` · harmful: 0
- features: redesign-consulta
- evidence: SPEC_DEVIATION inovacoes/apresentacao.py:76 (design)
- last seen: 2026-11-20T03:16:36Z

### L-062 - When display data comes from a Django form, state whether the valid fields of an invalid form still count, because cleaned_data keeps them
- signal: `spec_deviation` · recurrence: 1 feature(s) · scope: `specs` · harmful: 0
- features: redesign-consulta
- evidence: SPEC_DEVIATION inovacoes/views.py:373 (specs)
- last seen: 2026-11-20T03:16:36Z

### L-063 - When an edge case names a concrete input such as a long title, render that input in a test, not only check the stylesheet statically
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `tests` · harmful: 0
- features: redesign-consulta
- evidence: edge case titulo de 150 caracteres (spec.md:303) (tests)
- last seen: 2026-11-20T03:16:36Z

### L-064 - When a test proves a layout behavior by the presence of a CSS property, also assert that no rule on the same element declares a property that cancels it
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `tests` · harmful: 0
- features: redesign-consulta
- evidence: N10 templates/kira.css:804 (tests)
- last seen: 2026-11-20T03:29:33Z

### L-065 - When asserting that no stylesheet rule restyles an element, match every selector whose subject reaches it, including prefixed ancestors, theme attribute prefixes and media blocks, not only the literal selector
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `templates-css` · harmful: 0
- features: link-administracao
- evidence: validation.md M19/M20 (ADM-07), inovacoes/tests/test_link_administracao.py:133-141 (templates-css)
- last seen: 2026-11-23T23:33:59Z

### L-066 - When a test compares rendered markup to a project file, also pin that file's content to the external reference, or the comparison accepts any edit to the file
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `tests` · harmful: 0
- features: link-administracao
- evidence: validation.md M22 (ADM-04), inovacoes/tests/test_link_administracao.py:119 (tests)
- last seen: 2026-11-23T23:33:59Z

## Quarantined (failed when applied - ignore)

A confirmed lesson that recurred alongside failure. Kept for the maintainer to review.

_none_
