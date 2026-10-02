# LESSONS - auto-maintained by scripts/lessons.py

> Machine-owned. Do NOT hand-edit. Changes are overwritten on the next `lessons.py` write.
> Canonical state lives in `.specs/lessons.json`. Edit lessons only via the script.
> promote_threshold=2 distinct features · window_days=45 · quarantine_threshold=2

## Confirmed (load these at Specify/Design)

Corroborated across multiple features. Safe to apply as guidance.

_none_

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

### L-003 - When an AC restricts a screen to one role, test that other roles holding framework access are denied the screen, not only that fields are hidden
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `admin` · harmful: 0
- features: autenticacao
- evidence: AUTH-22 contas/tests/test_admin_perfil.py:46 (admin)
- last seen: 2026-09-27T03:25:06Z

### L-004 - Assert the error type the AC names and that the stored value stays unchanged, not just that the write fails
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `models` · harmful: 0
- features: autenticacao
- evidence: AUTH-18 contas/tests/test_constraints.py:17 (models)
- last seen: 2026-09-27T03:25:06Z

### L-005 - Assert every clause of a compound AC at the layer the AC describes; a backend test does not cover a screen-level outcome
- signal: `ac_gap` · recurrence: 1 feature(s) · scope: `routes` · harmful: 0
- features: autenticacao
- evidence: AUTH-13 AUTH-23 AUTH-07 validation.md Fix 4 (routes)
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

## Quarantined (failed when applied - ignore)

A confirmed lesson that recurred alongside failure. Kept for the maintainer to review.

_none_
