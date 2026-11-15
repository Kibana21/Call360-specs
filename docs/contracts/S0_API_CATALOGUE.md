# Call360 — Stage 0 API catalogue (descriptive)

**Status:** CP0.0 draft, 2026-11-15
**Contract rules:** ADR-0006, `API_CONTRACT_POLICY.md`
**Authority:** this catalogue states the **intended** S0 surface: permissions, scope and owning checkpoint. The backend's generated `contracts/generated/openapi.json` is the executable schema. CP0.1–CP0.4 implementation must match this catalogue; any difference is raised and the catalogue updated through a specs change, never silently.

**Conventions (all rows):**
- Paths are under `/api/v1` unless they begin with `/health` or `/mock-internal`.
- The error envelope and list shape are as in ADR-0006.
- Unsafe methods require `X-CSRF-Token` and an allowed `Origin`.
- `Idem` means the endpoint requires an `Idempotency-Key`; `If-Match` means it requires a `row_version`.
- Scope rules: **M** = rows filtered to the caller's markets; an object outside scope returns 404. **Own** = owner-only. **—** = no business object.
- Standard errors on every authenticated route: `401 AUTH_REQUIRED | AUTH_SESSION_INVALID`, `403 FORBIDDEN`, `422 VALIDATION_FAILED`, `429 RATE_LIMITED`. Row-specific errors are listed in addition.

## 1. Health, authentication and session (CP0.1A; API-007 and API-009 in CP0.1B-3)

| ID | Method | Path | Permission | Scope | Main response | Additional errors | CP |
|---|---|---|---|---|---|---|---|
| API-001 | GET | `/health/live` | PUBLIC | — | `{status}` (no detail) | — | CP0.1A |
| API-002 | GET | `/health/ready` | PUBLIC | — | `{status}`. The DB, migrations at head and the data-policy check must pass; no detail is exposed | `503 NOT_READY` | CP0.1A |
| API-003 | GET | `/auth/csrf` | PUBLIC | — | Sets the pre-session CSRF cookie; `{csrf_token}` | — | CP0.1A |
| API-004 | POST | `/auth/login` | PUBLIC | — | Sets the access, refresh and CSRF cookies; `{principal, permissions, markets, session_expires_at}` | `401 AUTH_INVALID_CREDENTIALS`, `403 CSRF_INVALID` | CP0.1A |
| API-005 | POST | `/auth/refresh` | PUBLIC (refresh cookie) | — | Rotates the cookies; `{session_expires_at}` | `401 AUTH_REFRESH_INVALID` (reuse revokes the family) | CP0.1A |
| API-006 | POST | `/auth/logout` | AUTHENTICATED | — | `204`; clears the cookies and revokes the session | — | CP0.1A |
| API-007 | GET | `/auth/session` | AUTHENTICATED | — | `{session_id, created_at, idle_expires_at, absolute_expires_at}` | — | CP0.1B |
| API-008 | GET | `/me` | AUTHENTICATED | — | `{principal_id, display_name, roles, permissions, markets, environment:{app_env, data_policy}}` | — | CP0.1A |
| API-009 | POST | `/me/password` | AUTHENTICATED (LOCAL) | Own | `204`; changes the own local password and revokes the other sessions | `422 PASSWORD_POLICY` | CP0.1B |

## 2. Administration (API-010, 012, 021 in CP0.1A; API-022…025 in CP0.1B-1; others in CP0.1B-3)

| ID | Method | Path | Permission | Scope | Main response | Additional errors | CP |
|---|---|---|---|---|---|---|---|
| API-010 | GET | `/admin/users` | `admin.users.read` | — | Users with status, bindings, groups and last login | — | CP0.1A |
| API-011 | POST | `/admin/users` | `admin.users.manage` | — | Creates a LOCAL user with a one-time password (Idem) | `409 USERNAME_TAKEN` | CP0.1B |
| API-012 | PATCH | `/admin/users/{principal_id}` | `admin.users.manage` | — | Enable or disable, display name; `reason` required (If-Match) | `409 CONFLICT_ROW_VERSION`, `409 LAST_ADMIN_GUARD` | CP0.1A |
| API-013 | POST | `/admin/users/{principal_id}/password-reset` | `admin.users.manage` | — | Sets a one-time password and revokes sessions | — | CP0.1B |
| API-014 | GET | `/admin/groups` | `admin.users.read` | — | Groups with role and scope mappings and member counts | — | CP0.1B |
| API-015 | PUT | `/admin/groups/{group_id}/members/{principal_id}` | `admin.groups.manage` | — | Adds a membership; `reason` required | `409 LAST_ADMIN_GUARD` | CP0.1B |
| API-016 | DELETE | `/admin/groups/{group_id}/members/{principal_id}` | `admin.groups.manage` | — | Ends a membership (history kept); `reason` required | `409 LAST_ADMIN_GUARD` | CP0.1B |
| API-017 | GET | `/admin/roles` | `admin.users.read` | — | Roles with permissions, reserved flags and aliases | — | CP0.1B |
| API-018 | PUT | `/admin/groups/{group_id}/mappings` | `admin.groups.manage` | — | Replaces the role and scope mappings (new effective-dated rows); `reason` required (If-Match) | `422 RESERVED_PERMISSION` | CP0.1B |
| API-019 | GET | `/admin/sessions` | `admin.sessions.manage` | — | Active sessions (no token material) | — | CP0.1B |
| API-020 | POST | `/admin/sessions/{session_id}/revoke` | `admin.sessions.manage` | — | `204`; `reason` required | — | CP0.1B |
| API-021 | GET | `/admin/audit-events` | `audit.read` | — | Cursor list; filters: actor, action, entity, outcome, time range | — | CP0.1A |
| API-022 | GET | `/admin/code-lists` | `config.read` | — | Lists with their active version, values and governed flag | — | CP0.1B |
| API-023 | POST | `/admin/code-lists/{code}/versions` | `config.manage` | — | Activates a new version of a **non-governed** list; `reason` required (Idem) | `403 GOVERNED_LIST_READ_ONLY` | CP0.1B |
| API-024 | GET | `/admin/feature-flags` | `config.read` | — | Flags with stage gate | — | CP0.1B |
| API-025 | PATCH | `/admin/feature-flags/{code}` | `config.manage` | — | Toggles; `reason` required (If-Match); stage-gated flags cannot be enabled before their stage | `422 STAGE_GATED` | CP0.1B |
| API-026 | GET | `/admin/system-health` | `system.health.read` | — | DB, migration head, data policy, mock-upstream reachability, audit chain head digest, OpenAPI SHA | — | CP0.1B |
| API-027 | GET | `/admin/integrations` | `intake.read` | — | Configured connectors, environment availability, last run | — | CP0.4 |

## 3. Overview, explorer, case and evidence (CP0.3)

| ID | Method | Path | Permission | Scope | Main response | Additional errors | CP |
|---|---|---|---|---|---|---|---|
| API-030 | GET | `/dashboard/kpis` | `dashboard.read` | M | KPI objects per `S0_KPI_DEFINITIONS.md` (definition, numerator, denominator, value, cohort, exclusions, time zone, data freshness, synthetic badge, typed drilldowns) | `422 INVALID_RANGE` | CP0.3 |
| API-031 | GET | `/dashboard/trend` | `dashboard.read` | M | Daily series for one KPI (7 or 30 days), with the same definition metadata | — | CP0.3 |
| API-032 | GET | `/dashboard/attention` | `dashboard.read` | M | Priority work items with reason and typed route | — | CP0.3 |
| API-033 | GET | `/dashboard/activity` | `dashboard.read` | M | Recent `case_event` items (scoped, masked) | — | CP0.3 |
| API-034 | GET | `/dashboard/risk-distribution` | `dashboard.read` | M | Open cases by effective SBQ band, with drilldown | — | CP0.3 |
| API-035 | GET | `/cases` | `case.read` | M | Call Explorer register. `grain=case\|attempt\|session`; facets: market, product family, ILP, risk band, channel, FSC, owner, state, hold reason, script version, due/created date range, `kpi`+`kpi_set` (numerator or denominator predicate); sort; cursor | `422 INVALID_FILTER` | CP0.3 |
| API-036 | GET | `/cases/facets` | `case.read` | M | Facet counts computed after scope | — | CP0.3 |
| API-037 | GET | `/cases/{case_id}` | `case.read` | M | Case header: derived `outcome_category` and `sla{due_at, breached, exemption_rule}` (S0_KPI_DEFINITIONS §1–§2); sale, policy (masked), contact selection, effective risk (origin, version), holds + `callable` + `callable_blockers`, state, owner, due | `404 NOT_FOUND` | CP0.3 |
| API-038 | GET | `/cases/{case_id}/attempts` | `case.read` | M | All attempts incl. no-answer, with contact snapshot (masked) and session links | `404` | CP0.3 |
| API-039 | GET | `/cases/{case_id}/script-assignment` | `case.read` | M | Assignment history: version, manifest SHA, rule trace, input snapshot, rationale | `404` | CP0.3 |
| API-040 | GET | `/cases/{case_id}/timeline` | `case.read` | M | `case_event` items with typed related-entity routes | `404` | CP0.3 |
| API-041 | GET | `/cases/{case_id}/findings` | `case.read` | M | Findings with severity, status, evidence refs, `record_origin`, review timestamps (no review decisions in S0) | `404` | CP0.3 |
| API-042 | GET | `/cases/{case_id}/holds` | `case.read` | M | Active and released holds with actors and reasons | `404` | CP0.3 |
| API-043 | GET | `/attempts/{attempt_id}` | `case.read` | M (via case) | Attempt detail | `404` | CP0.3 |
| API-044 | GET | `/sessions/{session_id}` | `case.read` | M (via case) | Session state, pins (script version + SHA, risk assessment + SHA, fact snapshot + SHA, contacted party), `record_origin` | `404` | CP0.3 |
| API-045 | GET | `/sessions/{session_id}/transcript` | `case.read` | M (via case) | `availability: NOT_AVAILABLE / NO_CAPTURE_BEFORE_S1`; no segments in S0 (`transcript_segment` deferred to S1) | `404` | CP0.3 |
| API-046 | GET | `/sessions/{session_id}/media` | `case.read` | M (via case) | `availability: NOT_AVAILABLE / NO_CAPTURE_BEFORE_S1`; never a URL in S0 | `404` | CP0.3 |
| API-047 | GET | `/survey-runs/{survey_run_id}` | `case.read` | M (via case) | Question executions with revision wording, expected-answer policy, answer observations, rule evaluations | `404` | CP0.3 |

## 4. Policy, party, sale and risk (CP0.3)

| ID | Method | Path | Permission | Scope | Main response | Additional errors | CP |
|---|---|---|---|---|---|---|---|
| API-050 | GET | `/policies` | `policy.read` | M | Policy Explorer list: masked owner/insured labels, product, ILP, premium, FSC, sale date and channel, effective risk, script, latest case state; facets; cursor | `422` | CP0.3 |
| API-051 | GET | `/policies/{policy_id}` | `policy.read` | M | Policy header with provenance and as-of for each material field | `404` | CP0.3 |
| API-052 | GET | `/policies/{policy_id}/parties` | `party.read` | M | Party role edges plus masked contact cards and eligibility | `404` | CP0.3 |
| API-053 | GET | `/policies/{policy_id}/sales` | `policy.read` | M | Sale events (multi-sale) | `404` | CP0.3 |
| API-054 | GET | `/sales/{sale_event_id}` | `policy.read` | M | Sale context: FSC, channel, location, campaign, product snapshot, fact snapshots, risk history, cases | `404` | CP0.3 |
| API-055 | GET | `/policies/{policy_id}/history` | `policy.read` | M | `field_change` and intake lineage (source, actor, reason, before/after redacted) | `404` | CP0.3 |
| API-056 | GET | `/risk-assessments` | `risk.read` | M | SBQ Risk Workbench list; facets: band, factor, origin, rule-set version, product, channel, FSC, status | `422` | CP0.3 |
| API-057 | GET | `/risk-assessments/{assessment_id}` | `risk.read` | M | Assessment with factors, input snapshot hash, rule-set version, supersedes chain, source original value | `404` | CP0.3 |
| API-058 | GET | `/risk-factors` | `risk.read` | — | Active factor vocabulary (code-list version) | — | CP0.3 |

## 5. Scripts and regulatory register (CP0.3)

| ID | Method | Path | Permission | Scope | Main response | Additional errors | CP |
|---|---|---|---|---|---|---|---|
| API-060 | GET | `/scripts` | `script.read` | M (`market_code` or ALL) | Script Studio library; filters: product, risk band, channel, status, effective date, language | `422` | CP0.3 |
| API-061 | GET | `/scripts/{script_family_id}` | `script.read` | M | Family with versions summary | `404` | CP0.3 |
| API-062 | GET | `/scripts/{script_family_id}/versions` | `script.read` | M | Versions with status, effective dates, manifest SHA | `404` | CP0.3 |
| API-063 | GET | `/script-versions/{script_version_id}` | `script.read` | M | Ordered sections → modules → question revisions (wording, delivery mode, answer type, expected-answer policy, mandatory), controls, regulatory links, `content_approval_status` | `404` | CP0.3 |
| API-064 | GET | `/script-assignment-rules` | `script.read` | M | Seeded rule versions (predicate, priority, target, effective dates); read-only | — | CP0.3 |
| API-065 | GET | `/regulatory-references` | `script.read` | M | Register with jurisdiction, version and interpretation status | — | CP0.3 |
| API-066 | GET | `/controls` | `script.read` | M | Controls with linked questions and optional regulatory references | — | CP0.3 |

## 6. Search, saved views and queues (CP0.3)

| ID | Method | Path | Permission | Scope | Main response | Additional errors | CP |
|---|---|---|---|---|---|---|---|
| API-070 | GET | `/search` | `search.use` | M | Hits `{entity_type, id, ref, masked_display, matched_field, match_kind (EXACT\|PREFIX\|FUZZY), route}`; `types=`; cursor; length-bounded `q` | `422 QUERY_TOO_LONG` | CP0.3 |
| API-071 | GET | `/search/suggest` | `search.use` | M | Up to 8 typed suggestions (scoped before ranking) | — | CP0.3 |
| API-072 | GET | `/saved-views` | `saved_view.manage_own` | Own | The caller's views | — | CP0.3 |
| API-073 | POST | `/saved-views` | `saved_view.manage_own` | Own | Creates; `filter_json` is validated against the view-type schema (Idem) | `409 NAME_TAKEN` | CP0.3 |
| API-074 | PATCH | `/saved-views/{view_id}` | `saved_view.manage_own` | Own | Rename or update filter (If-Match) | `404` (another user's view) | CP0.3 |
| API-075 | DELETE | `/saved-views/{view_id}` | `saved_view.manage_own` | Own | `204` | `404` | CP0.3 |
| API-076 | GET | `/work-queues` | `queue.read` | M | Operational queues: due today, on hold by reason, awaiting callback, overdue; typed routes | — | CP0.3 |
| API-077 | GET | `/review-queue` | `queue.read` | M | Findings awaiting review (seeded); read-only | — | CP0.3 |
| API-078 | GET | `/voice/preflight` | `voice.preflight.read` | — | `{status: NOT_AVAILABLE, reason: "Browser voice is introduced in Stage S1"}` | — | CP0.3 |

## 7. Intake (CP0.4)

| ID | Method | Path | Permission | Scope | Main response | Additional errors | CP |
|---|---|---|---|---|---|---|---|
| API-080 | GET | `/intake/sources` | `intake.read` | — | Available sources in this environment (`MOCK_API`, `MANUAL`); `BULK` and `INTERNAL_API` shown as not available in S0 | — | CP0.4 |
| API-081 | POST | `/intake/import-runs` | `intake.mock.sync` | — | Starts a `MOCK_API` import over HTTP from the mock upstream; returns the run with reconciliation counts (Idem) | `503 SOURCE_UNAVAILABLE`, `422 INGEST_*` | CP0.4 |
| API-082 | GET | `/intake/import-runs` | `intake.read` | — | Runs (mock and manual) with status and counts | — | CP0.4 |
| API-083 | GET | `/intake/import-runs/{run_id}` | `intake.read` | — | Run detail with per-item status and errors (no raw PII) | `404` | CP0.4 |
| API-084 | POST | `/intake/manual/preview` | `intake.manual.submit` | M (target market must be in scope) | Validation result, normalised preview, duplicate detection, contact eligibility, risk as supplied, `script_routing: NOT_EVALUATED_IN_S0`, holds that would apply. **Persists nothing except an audit event** | `422 INGEST_VALIDATION_FAILED` (field details) | CP0.4 |
| API-085 | POST | `/intake/manual` | `intake.manual.submit` | M | Commits `source_type=MANUAL` with reason and source reference; creates policy, sale, parties and risk as supplied and a case with `AWAITING_SCRIPT_ASSIGNMENT` hold (and other applicable holds); returns typed routes (Idem) | `409 INGEST_DUPLICATE_SOURCE_EVENT`, `422 INGEST_NON_SYNTHETIC_REJECTED`, `422 INGEST_CONTACT_NOT_SYNTHETIC` | CP0.4 |
| API-086 | POST | `/intake/corrections` | `intake.manual.submit` | M | POL-007 correction of a policy, sale or party field: `{entity_type, entity_id, row_version, changes, reason, source_reference}`. Writes `field_change` and audit. Never alters fact snapshots; open cases get an impact flag | `409 CONFLICT_ROW_VERSION`, `422 FIELD_NOT_CORRECTABLE` | CP0.4 |

## 8. Mock upstream application (separate ASGI app, port 8100; `APP_ENV ∈ {local, test}` only; service token)

Not part of the product OpenAPI. It has its own generated OpenAPI. Payloads carry `schema_version`, `source_event_id` and `is_synthetic: true`.

| ID | Method | Path | Permission | Scope | Main response | Additional errors | CP |
|---|---|---|---|---|---|---|---|
| API-090 | GET | `/mock-internal/v1/sales` | SERVICE_TOKEN | — | Cursor list of synthetic sale events with policy and parties | `401` | CP0.4 |
| API-091 | GET | `/mock-internal/v1/sales/{id}` | SERVICE_TOKEN | — | One sale | `404` | CP0.4 |
| API-092 | GET | `/mock-internal/v1/sales/{id}/risk` | SERVICE_TOKEN | — | Synthetic source SBQ risk (band, factors, source original value) | `404` | CP0.4 |

## 9. Explicitly not in S0

These are documented so that their absence is deliberate:
- script draft, submit, review and publish (`POST /scripts/{id}/drafts`, `…/submit`, `…/review`, `…/publish`): S2;
- `POST /script-assignments/preview`: S2;
- `POST /risk-assessments/{id}/override-request`: S2;
- `POST /reviews/{id}/decision`: S3;
- evidence export: S3/S4;
- `POST /demo/sessions` and any provider session or token endpoint: S1;
- `/events/stream`: S1/S4;
- bulk import: S4.

No placeholder routes are created for these.
