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

## Quarantined (failed when applied - ignore)

A confirmed lesson that recurred alongside failure. Kept for the maintainer to review.

_none_
