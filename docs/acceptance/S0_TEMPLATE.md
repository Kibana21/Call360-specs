# Call360 Stage 0 — Acceptance report TEMPLATE (not approved)

**Status:** NOT_STARTED (change only after evidence and owner review)  
**Owner:** AIA Standards & Compliance (proposed; pending confirmation)  
**Date:** TBD

## Source revisions (all required)

Use commit SHAs when commits are authorised; otherwise record the base SHA plus the `scripts/evidence_manifest.py` SHA-256 (ADR-0003 §6).

| Repo / artifact | Exact value | Evidence link |
|---|---|---|
| `Call360-specs` commit SHA | TBD | TBD |
| `Call360-backend` commit SHA | TBD | TBD |
| `Call360-frontend` commit SHA | TBD | TBD |
| Backend OpenAPI SHA-256 | TBD | TBD |
| Alembic migration head | TBD | TBD |
| Test environment and seed version | TBD | TBD |

## Requirement coverage

List each S0/P0 requirement ID, test case and pass/fail evidence. Do not copy a blanket PASS without executing tests. Include `APP-*`, `CASE-*`, `SUR-*`, `GOV-*` applicable to S0, and explicit naming/route requirements.

## Integrated scenario and commands

- Fresh PostgreSQL database → migrations → deterministic seed (>=250 synthetic cases).
- Backend API unit/integration/security tests, lint/types, OpenAPI determinism and drift.
- Frontend build/unit/accessibility tests and generated-client parity.
- Playwright against **real running backend/Postgres**, including Overview → Call Explorer → **Call Detail** (three attempts, one connected session) and back/refresh behavior.
- Verify product branding is `Call360`, detail page and breadcrumb are `Call Detail`, and no screen is labelled “Call 360”.
- Verify unauthorized access, loading, empty, partial, failed artifact, 1280px/1440px desktop, keyboard navigation.

Commands run, timestamps, output paths and test counts (local run logs; no CI in local development): TBD.

## Open defects / risks / owner decisions

TBD. For blocked P0 requirement, state BLOCKED; do not claim Stage 0 accepted.

## Approvals

| Role | Name | Date | Decision |
|---|---|---|---|
| Product Owner / S&C | TBD | TBD | PENDING |
| Engineering Lead | TBD | TBD | PENDING |
| Security / Privacy as appropriate | TBD | TBD | PENDING |

**Final stage gate:** NOT_ACCEPTED until evidence and required approvals are complete.

## v0.3 S0 expansion sign-off

- [ ] Policy/sale/risk/party/contact records populated from deterministic **synthetic** fixtures and browsable from UI.
- [ ] Mock API and manual injection show validation, provenance, idempotent import and auditable correction.
- [ ] Policy Detail / Sale Detail / Call Detail linked; risk assessment and script-assignment rationale discoverable.
- [ ] Authenticated search across allowed policy number, customer, FSC, risk, survey and call facets, with scoped backend filtering.
- [ ] Local login/logout, ADMIN/USER assignment, server-side authorization, secure cookie/session/token controls and audit tests proven.
- [ ] New required negative scenarios T-31 onward mapped to stage tests and pass or have explicit approved deferral.
- [ ] All business process assumptions pending SBQ/S&C signoff are identified; no unapproved MAS/AIA script wording presented as official.
