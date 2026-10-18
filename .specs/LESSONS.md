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

## Candidates (under observation - do NOT load as guidance yet)

Seen once or not yet corroborated. Tracked, not trusted.

### L-001 - Assert that a submitted password is absent from every response body that re-renders a form, not only from logs
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `forms` · harmful: 0
- features: autenticacao
- evidence: validation.md M6 contas/forms.py:21 (forms)
- last seen: 2026-09-27T03:25:06Z

### L-002 - Cover the dummy password hash on the not-found path of a custom auth backend with a test that observes the call
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `auth-backend` · harmful: 0
- features: autenticacao
- evidence: validation.md M4 contas/backends.py:32 (auth-backend)
- last seen: 2026-09-27T03:25:06Z

### L-004 - Assert the error type the AC names and that the stored value stays unchanged, not just that the write fails
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `models` · harmful: 0
- features: autenticacao
- evidence: AUTH-18 contas/tests/test_constraints.py:17 (models)
- last seen: 2026-09-27T03:25:06Z

### L-006 - Test every admin screen a permission hook guards, including delete, not only list, add and change
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `admin` · harmful: 0
- features: autenticacao
- evidence: validation.md iteracao 2 A5 contas/admin.py:51 (admin)
- last seen: 2026-09-27T03:45:12Z

### L-007 - When asserting that a record is attributed to the requesting user, create another account before that user so the assertion cannot pass by picking the oldest or any fixed account
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `views` · harmful: 0
- features: cadastro-inovacao
- evidence: validation.md mutante V2b; INOV-04; inovacoes/tests/test_views_cadastro.py:68 (views)
- last seen: 2026-09-30T00:34:12Z

### L-008 - When testing that a rejected form preserves input, trigger the error in a different field than the one whose preserved value you assert, and assert every field
- signal: `surviving_mutant` · recurrence: 1 feature(s) · scope: `forms` · harmful: 0
- features: cadastro-inovacao
- evidence: validation.md mutante T4; INOV-11; inovacoes/tests/test_views_cadastro.py:170 (forms)
- last seen: 2026-09-30T00:34:12Z

### L-009 - Guard every permission hook that reads a custom attribute of request.user with is_authenticated, and test the hook's page as an anonymous visitor, because Django calls admin hooks with AnonymousUser on the login page
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `admin` · harmful: 0
- features: cadastro-inovacao
- evidence: UAT achado 1; contas/admin.py:22; contas/tests/test_admin_perfil.py:125 (admin)
- last seen: 2026-10-02T13:43:06Z

### L-010 - When an AC promises a redirect to a login page, state and test that the target page opens with 200 for a visitor without a session
- signal: `spec_precision_gap` · recurrence: 1 feature(s) · scope: `auth` · harmful: 0
- features: cadastro-inovacao
- evidence: AUTH-21 (autenticacao/spec.md:196); validation.md iteracao 3, Sugestao 1 (auth)
- last seen: 2026-10-02T13:43:06Z

### L-011 - When an AC bounds a numeric query parameter, state the outcome for zero and negative values, not only for non-numeric and above-range values
- signal: `spec_precision_gap` · recurrence: 1 feature(s) · scope: `routes` · harmful: 0
- features: consulta-inovacoes
- evidence: validation.md SPG-1 / CONS-05 (inovacoes/views.py:101-107) (routes)
- last seen: 2026-10-04T03:09:55Z

### L-012 - When an AC limits the length of a text input that is trimmed, state whether the limit counts before or after trimming and test the boundary with edge whitespace
- signal: `spec_precision_gap` · recurrence: 1 feature(s) · scope: `forms` · harmful: 0
- features: consulta-inovacoes
- evidence: validation.md SPG-2 / CONS-24 (inovacoes/forms.py:100-108) (forms)
- last seen: 2026-10-04T03:09:55Z

### L-013 - Before designing an AC around a framework helper, check the helper on every boundary value, because Django Paginator.get_page sends page 0 to the last page
- signal: `spec_deviation` · recurrence: 1 feature(s) · scope: `routes` · harmful: 0
- features: consulta-inovacoes
- evidence: SPEC_DEVIATION inovacoes/views.py:101 (T5) (routes)
- last seen: 2026-10-04T03:09:55Z

### L-014 - Set label_suffix on a Django Form through the __init__ keyword, because Form.__init__ overwrites a class-level label_suffix
- signal: `spec_deviation` · recurrence: 1 feature(s) · scope: `forms` · harmful: 0
- features: consulta-inovacoes
- evidence: SPEC_DEVIATION inovacoes/forms.py:134 (T17) (forms)
- last seen: 2026-10-04T03:09:55Z

### L-015 - When a task changes what a route returns, grep every test that requests that route before listing any of them as unchanged
- signal: `spec_deviation` · recurrence: 1 feature(s) · scope: `tests` · harmful: 0
- features: consulta-inovacoes
- evidence: tasks.md T8 Done when; contas/tests/test_controle_acesso.py:98 (tests)
- last seen: 2026-10-04T03:09:55Z

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
- evidence: STAT-06/STAT-34 title, test_views_status.py:50 (specs) (+1 more)
- last seen: 2026-10-18T20:31:51Z

## Quarantined (failed when applied - ignore)

A confirmed lesson that recurred alongside failure. Kept for the maintainer to review.

_none_
