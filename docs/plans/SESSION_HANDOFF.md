# Call360 — Session handoff

**Written:** 2026-11-15, at the end of a Claude Code session.
**Updated:** 2026-11-17: S1-A, S1-B and S1-C ACCEPTED (D-45…D-48 decided; D-48 KPI correction implemented); S1-D IMPLEMENTED AND VERIFIED (`IMPLEMENT S1-D`, D-49…D-53), awaiting owner acceptance; Stage 0 governance acceptance and SEC-008 PENDING. Current state: §22.
**Authorization:** F0–F5 **ACCEPTED**. CP0.4a (`IMPLEMENT CP0.4a`, split approved as D-41) **ACCEPTED 2026-11-16** with its documented limitations. CP0.4b Manual Intake portal (D-42) **ACCEPTED 2026-11-16** (UI portion only; CP0.4b not complete); the rest of CP0.4b (mock upstream, scheduling, corrections, saved drafts, Admin Integrations) is deferred and not authorised. Not authorised: CP0.4b, saved views, B-3, commits, pushes. No real customer data. **Stage 0:** CP0.1B-3 ACCEPTED; CP0.6 technical verification ACCEPTED; Stage 0 governance acceptance PENDING (SEC-008 security review, named approvers). **Stage 1:** S1-A and S1-B ACCEPTED 2026-11-17; S1-C ACCEPTED 2026-11-17 (D-48 correction implemented with the acceptance). S1-D implemented and verified 2026-11-17 (`IMPLEMENT S1-D`), awaiting owner acceptance. Not authorised:, S1-E, S2, S3, CP0.4b remainder.
**Process:** strict specification-driven development (workspace `CLAUDE.md` §10). Each checkpoint is implemented and accepted before the next one starts. Checkpoints never advance automatically.
**Secrets:** this document contains none. Credentials live only in gitignored local files (§4).

## 1. Checkpoint status

| Checkpoint | Status | Record |
|---|---|---|
| CP0.0 Specification foundation | **ACCEPTED** 2026-11-15 | `docs/acceptance/CP0.0.md` |
| CP0.1A Core authentication and application shell | **ACCEPTED** 2026-11-15 (after UI-1…4 and scanner corrections) | `docs/acceptance/CP0.1A.md` |
| CP0.1B-1 Configuration foundation | **ACCEPTED** 2026-11-15 (local development; uncommitted) | `docs/acceptance/CP0.1B-1.md` |
| CP0.1B-2 Market scope → **F0** (Singapore-only, D-39) | **ACCEPTED** 2026-11-15 | `docs/acceptance/S0.md`, `evidence/F0-F1/` |
| **F1** Overview (API-030…034, `/`) | **ACCEPTED** 2026-11-15 (limitations accepted: OPS-06 N/A, KPI-11 N/A, click-throughs in F2/F3, 7-day activity may be empty) | `evidence/F0-F1/` |
| CP0.1B-3 Administration completion | superseded by the CP0.1B-3 row below (ACCEPTED 2026-11-17) | — |
| CP0.2 Domain schema and seed | **ACCEPTED** 2026-11-15 (local synthetic-data development; deployed to `call360` at `0007`); password rotation deferred (RR-12); Singapore-only scope decision D-39 recorded | `docs/acceptance/CP0.2.md` |
| **F3** Call Detail | **ACCEPTED** 2026-11-15 | §8 below, `evidence/F3/` |
| **F4** Policy Explorer | **ACCEPTED** 2026-11-15 | §9 below, `evidence/F4/` |
| **F5** SBQ Risk Workbench | **ACCEPTED** 2026-11-16 | §10 below, `evidence/F5/` |
| **F2** Work Queues and search | **ACCEPTED** 2026-11-15 (AWAITING_CALLBACK queue definition approved; saved views, register grain modes, nonessential search filters deferred) | §7 below, `evidence/F2/` |
| **CP0.4a** Insurance transaction intake | **ACCEPTED** 2026-11-16 (limitations accepted) | §11 below, `evidence/CP0.4a/` |
| **CP0.4b-UI** Manual Intake portal | **ACCEPTED** 2026-11-16 (UI portion only; single-page form accepted) | §12 below, `evidence/CP0.4b-UI/` |
| **F6** Script Studio and Assignment Rules (read-only) | **ACCEPTED** 2026-11-16 (limitations accepted) | §13 below, `evidence/F6/` |
| **F7** Review Workbench and Voice Studio (read-only) | **ACCEPTED** 2026-11-16 (limitations accepted) | §14 below, `evidence/F7/` |
| **CP0.1B-3** Administration completion | **ACCEPTED** 2026-11-17 (limitations accepted) | §15 below, `evidence/CP0.1B-3/` |
| **CP0.6** Integrated Stage 0 verification | **ACCEPTED (technical)** 2026-11-17; Stage 0 governance acceptance PENDING (SEC-008, approvers) | `S0.md` "CP0.6 integrated verification", `evidence/CP0.6/` |
| CP0.4b remainder | NOT_STARTED (deferred) | `docs/plans/S0_IMPLEMENTATION_PLAN.md` |
| **S1-A** Full-duplex browser voice POC (mock provider) | **ACCEPTED** 2026-11-17 (owner real-microphone test) | §17 below, `docs/acceptance/S1.md`, `evidence/S1-A/` |
| **S1-B** Voice-session lifecycle and event persistence | **ACCEPTED** 2026-11-17 (limitations accepted) | §18 below, `docs/acceptance/S1.md`, `evidence/S1-B/` |
| **S1-C** Consent-gated recording | **ACCEPTED** 2026-11-17 (owner real-microphone test; D-45…D-48 decided; D-48 KPI correction implemented) | §20–§21 below, `docs/acceptance/S1.md`, `evidence/S1-C/` |
| S1-D Transcript and playback | **IMPLEMENTED AND VERIFIED** 2026-11-17, awaiting owner acceptance (D-49…D-53 approved) | §22 below, `docs/acceptance/S1.md` "S1-D as built", `evidence/S1-D/` |
| S1-E Real provider (GPT-Live) | NOT_STARTED, deferred by the owner | `docs/acceptance/S1.md` |

Stage 0 overview: `docs/acceptance/S0.md`.

## 2. What is built

**CP0.1A (accepted)**
- **Backend:**
  - local login with Argon2id passwords;
  - EdDSA access JWTs (10 min) in HttpOnly cookies;
  - rotating refresh tokens stored as HMACs, with reuse detection. A benign multi-tab duplicate gets a `409 REFRESH_SUPERSEDED` and no token is minted;
  - server-side sessions, CSRF plus Origin checks, login throttling;
  - group → role → permission authorization resolved on every request;
  - hash-chained, append-only audit;
  - `bootstrap-admin` and `create-local-user` CLIs.
- **API:** 10 endpoints: health ×2, csrf, login, refresh, logout, `/me`, `GET/PATCH /admin/users`, `GET /admin/audit-events`.
- **Frontend:** a React shell reproducing the mockup (grouped sidebar; unbuilt items disabled with clock or "S4" indicators). Screens:
  - login, session expired, unauthorized;
  - a landing page showing real session data;
  - ADMIN Users (enable/disable with reason);
  - ADMIN Audit.

**CP0.1B-1 (accepted 2026-11-15)**
- **Tables (migration `0002_config_foundation`):** `code_list`, `code_list_version` (DRAFT → ACTIVE → SUPERSEDED, trigger-enforced, one ACTIVE per list), `code_value` (immutable unless its version is DRAFT), `feature_flag` (database CHECK stage lock), `feature_flag_change` (append-only).
- **APIs:**

  | ID | Endpoint |
  |---|---|
  | API-022 | `GET /admin/code-lists` (with full version history) |
  | API-023 | `POST /admin/code-lists/{code}/versions` (`based_on_version` + reason; atomic supersede/activate) |
  | API-024 | `GET /admin/feature-flags` |
  | API-025 | `PATCH /admin/feature-flags/{code}` (If-Match + reason) |

- **Seed (idempotent):** ten list definitions.
  - `market` is non-governed: labels editable, code set fixed (D-25).
  - Nine governed and read-only: `sbq_risk_band`, `risk_factor`, `case_hold_reason`, `case_closure_reason`, `case_cancellation_reason`, `finding_materiality_policy`, `kpi_sla_exemption_rule`, `callable_party_roles`, `synthetic_contact_ranges`.
  - `market` v1: `SG`, `MY`, marked synthetic.
  - Governed values are deliberately empty; CP0.2 seeds them.
  - Four flags, all off and stage-locked: `voice.browser_sessions` S1, `scripts.authoring` S2, `reviews.decisions` S3, `exports.evidence` S4.
- **UI:** Administration → Configuration:
  - lists with governance badges;
  - a version-history drawer;
  - a market label "New version" form;
  - flags with disabled, explained toggles for locked stages.

## 3. Latest verification (2026-11-15; `docs/acceptance/evidence/F0-F1/`)

| Check | Result |
|---|---|
| Backend tests | **193 passed** |
| Frontend unit and component tests | **35 passed** |
| **Playwright** against the real stack | **16 passed**; axe zero serious/critical and no overflow at 1280 and 1440 px |
| ruff, mypy `--strict`, ESLint, tsc, build | Clean |
| Secret scans | Self-test 13 formats × 50; repos and bundle clean |
| Development database (`call360`) | Both dev accounts log in; 195 SG cases visible, 0 MY leaked; readiness OK; audit chain verified |
| Specs validator | PASS |

OpenAPI SHA-256: `5da1f16d98b2adc2dbbbb1e78fe15566f8a0fd1f933cef9d445413976c205724`.

## 4. Repositories and environment

| Repo | HEAD (owner commit) | Uncommitted work (none committed since; committing needs owner authorisation) |
|---|---|---|
| Call360-specs | `de5926b` | CP0.2 specs, acceptance and evidence; D-39 (Singapore-only); D-40 (vertical slices); F0/F1 records and evidence; deployment runbook; this handoff |
| Call360-backend | `08c139e` | CP0.2 (migrations 0003–0007, `app/domain/`, seed, tests), corrections, F0 (migration 0008, `app/security/scope.py`), F1 (`app/api/dashboard.py`, `app/domain/kpis.py`), tests, OpenAPI. Manifest `evidence/F0-F1/manifest_backend.txt` (52 files) |
| Call360-frontend | `9f86ce0` | Audit-table fix, F1 Overview (`OverviewPage.tsx` and tests, `e2e/overview.spec.ts`), regenerated client, scanner fixes, DV-13. Manifest `evidence/F0-F1/manifest_frontend.txt` (18 files) |

**Database:** local PostgreSQL 15, database `Call360_db`.

| Schema | Owner / login role | Migration head | Notes |
|---|---|---|---|
| `call360` (development) | `Call360_db_user` (**superuser**, RR-11) | `0008_market_scope` | 55 tables + `alembic_version`; S0-SEED-1 (195 SG cases visible, 55 MY retained and hidden). Accounts: `dev.admin` (ADMIN), `dev.user` (USER). Backups: `~/call360-backups/pre_cp02_20261115_173043/` (includes `env.post_keys`, the only copy of the dev data-protection keys besides `.env`), `~/call360-backups/pre_f0_*` |
| `call360_test` (automated tests) | `call360_test_user` (no superuser; no access to `call360`) | `0008_market_scope` | Reset and seeded only by the guarded test harness and E2E setup |

**Local configuration (all gitignored; never commit):**

| Path | Holds |
|---|---|
| `Call360-backend/.env` | Development database URL and secrets |
| `Call360-backend/.env.test` | Test role credentials (generated, never displayed) |
| `Call360-backend/.env.local` | Dev account passwords |
| `Call360-backend/.secrets/` | Ed25519 signing keys |
| `Call360-frontend/e2e/.auth/` | E2E accounts |

**Run commands:**
- `cd Call360-backend && make dev` → http://127.0.0.1:8000
- `cd Call360-frontend && npm run dev` → http://127.0.0.1:5173
- Tests:
  - `make test lint typecheck contract-check secret-scan`
  - `npm run lint typecheck test api:check build secret-scan e2e`
- E2E servers run on ports 8001 and 5174 against `call360_test`.

Dev servers may still be running from the review: stop them with `lsof -ti tcp:8000,5173 | xargs kill`.

## 5. Known limitations and security risks

| Item | Risk | Action |
|---|---|---|
| **Development database password rotation (deferred by owner, RR-12)** | The `Call360_db_user` password is weak and was exposed in this session's conversation, command lines and, briefly, a local file. It never reached Git; history was scanned | Deferred at the CP0.2 deployment. When rotating, follow `CP0.2_DEV_DEPLOYMENT.md` step 4 **and step 4b**: `make_env.py --force` deletes the data-protection keys, which must be restored from `~/call360-backups/pre_cp02_20261115_173043/env.post_keys` |
| RR-11 | Development app connects as a superuser | Use a non-superuser app role before any non-synthetic data |
| RR-01 | Audit integrity relies on the database only | External anchoring decision deferred to S5 |
| RR-04 | Cookies on local HTTP lack `Secure`; HTTPS mode untested | Test in the CP0.6 gate |
| RR-05 | In-process rate limiter | Shared store in S5 |
| RR-09 / RR-10 | ASVS matrix is chapter-level; security parameters are provisional | Security owner review |
| Other | Small offline password blocklist; Chromium-only E2E; no Python dependency audit tool; the gitleaks generic rule misses ~3% of unknown key formats (Call360 formats are covered deterministically); 2 known default-rule false positives in BRD and register prose if the specs repo is ever scanned | Track |
| B-1 notes | API-023 handles a replay with 409, not a stored idempotency key; the stage-lock CHECK (`<= 'S0'`) must move in each later stage's migration; seed descriptions mention checkpoint names | Accepted design notes |

## 6. Key references
- **Plan:** `docs/plans/S0_IMPLEMENTATION_PLAN.md`
- **Decisions:** `docs/adr/` (ADR-0003…0008), `docs/spec/APPROVED_EXCEPTIONS.md`
- **Design:**
  - `docs/data/S0_DATA_MODEL.md` (Build column)
  - `docs/security/S0_IDENTITY_ACCESS_DESIGN.md` (§4 tokens, §8 governed lists, §10 schemas and roles)
  - `docs/contracts/S0_API_CATALOGUE.md`
  - `docs/product/S0_SCREEN_SPEC.md`, `docs/product/S0_KPI_DEFINITIONS.md`
- **Security:** `docs/security/THREAT_MODEL_S0.md`, `ASVS_S0_CONTROL_MATRIX.md`
- **Traceability:** `docs/acceptance/S0_TEST_MATRIX.md`
- **Acceptance and evidence:**
  - `docs/acceptance/CP0.0.md`, `CP0.1A.md`, `CP0.1B-1.md`
  - `evidence/CP0.0/`, `evidence/CP0.1A/` (including `defect-corrections/`), `evidence/CP0.1B-1/`
- **UI reference:** `Call360-frontend/docs/design/reference/Call360_Portal_Mockup.html`; deviations in `Call360-frontend/docs/design/DEVIATIONS.md`
- **Validator:** `python3 Call360-specs/scripts/validate_specs.py`. It freezes the BRD and register by SHA-256; never edit those files without an approved requirement change.

## 7. F2 Work Queues and search — ACCEPTED 2026-11-15

**As built (2026-11-15; evidence `docs/acceptance/evidence/F2/`; OpenAPI `1cc23a1b422be5748d74d2dd775e4403868f50c587ce0713bc3f192b834e9dd0`; no migration, head `0008_market_scope`):**
- Backend: `app/domain/register.py` (rows over the F1 `Facts`, so drilldowns reuse the KPI predicates), `app/api/cases.py` (API-035/036/076), `app/api/search.py` (API-070/071), `tests/test_register.py` (22 tests). Overview OPS-01…04/07 now carry typed register drilldowns (OPS-07 numerator only).
- Search: exact / prefix / FUZZY (= contained substring ≥ 4 characters; no edit-distance on identifiers so a near-miss MY reference cannot surface an SG record; no `pg_trgm` installed). Phone and email exact via `contact_method.value_hmac`. Terms are logged and audited (`SEARCH.EXECUTED`, API-070 only) as normalised SHA-256; the uvicorn access log has `q=` replaced by its digest.
- Queues: DUE_TODAY = OPS-02, OVERDUE = OPS-01 overdue, ON_HOLD = OPS-03 (by reason), AWAITING_CALLBACK = OPEN ∧ state `AWAITING_CALLBACK` (owner-approved 2026-11-15).
- Frontend: `/calls`, `/queues`, `/search`, top-bar combobox, Overview drilldown links; DV-12 lifted, DV-14/15 recorded.
- Not in F2 (raise if needed): register grain switch (`attempt`/`session`), facets for channel / FSC / owner / script version, customer-alias and FSC search; Call Detail (F3) and Policy Detail (F4) rows show an explicit F3/F4 state.

## 8. F3 Call Detail — ACCEPTED 2026-11-15

**As built (2026-11-15; evidence `docs/acceptance/evidence/F3/`; OpenAPI `f0f047162ec4e36c60e5815f58fcbff231ab04c561e4e696a2864282585b3739`; no migration):**
- Backend: `app/api/case_detail.py` (API-037…047 under `case.read`, API-063 under `script.read`; every lookup joins the case or script family with the caller's markets; missing/out-of-scope → identical audited 404), schemas in `app/api/schemas.py`, `tests/test_case_detail.py` (16 tests: all 12 golden fixtures, BOLA matrix over 12 routes, T-15 pin, masking, permissions). `app/domain/outcomes.py` gained `applicable_mandatory()` / `question_satisfied()` (refactor of the existing §1.1 logic, no rule change).
- `callable` / `callable_blockers` (API-037) are reported from persisted facts only: active blocking holds, no eligible contact selection, terminal case state. Labelled a data-level pre-check; call-time authority checks are S1.
- Frontend: `src/features/case/CallDetailPage.tsx` (+ tests), links from register, queues, Overview priority/activity and search; back link returns to the originating list with its filters; DV-16.
- Known limits: owner shown as "Unassigned" (no seeded owners; never fabricated); recordings/transcripts NOT_AVAILABLE (S1); review actions S3.
- Owner refinements (delivered with F4): the header shows "Contact pre-check (stored data only)": "Pre-check passed" or "Blocked" with one reason per cause and its evidence ("not an authorisation to call"); `precheckReasons()` merges `HOLD:<X>` and `<X>` blockers. API shape unchanged.

## 9. F4 Policy Explorer and Policy Detail — ACCEPTED 2026-11-15

**As built (2026-11-15; evidence `docs/acceptance/evidence/F4/`; OpenAPI `d8d118b32bed0a5ee7d70a238cbc9984d34b992104435a2bd26f23fedfd750bc`; no migration):**
- Backend: `app/domain/policy_register.py` (policy rows, filters, disjunctive facets, keyset paging; reuses F2 ref matching, HMAC contact search and cursors; case outcome from `load_facts`, effective band = latest FINAL assessment of the latest sale) and `app/api/policies.py`: API-050 `GET /policies`, API-051 `GET /policies/{id}` (header, record provenance and source/as-of per material field, external refs, related cases with outcome and pinned script), API-052 `/parties` (`party.read`; one card per party with role edges incl. ended, masked contact methods incl. ended/suppressed, per-case eligibility evidence incl. superseded), API-053 `/sales`, API-054 `GET /sales/{id}` (sale context, fact snapshots, risk history with `supersedes_id`, cases), API-055 `/history` (record lineage over policy, sales, role edges, snapshots, risk assessments; `field_changes` = NOT_AVAILABLE / `LEDGER_ARRIVES_CP0_4`). Every query filters `market_code = ANY(:markets)`; MY/missing → identical audited 404. `tests/test_policies.py`.
- Frontend: `src/features/policies/PolicyExplorerPage.tsx` (URL filters, facets, KPI tiles from facets, intake buttons disabled CP0.4) and `PolicyDetailPage.tsx` (tabs `sale`, `parties`, `risk`, `script`, `cases`, `source` in `?tab=`; `?sale=` must belong to the policy); `src/features/case/evidence.tsx` shared with Call Detail; links Policy → Call Detail, Call Detail → Policy (`?sale=`), register policy refs → Policy Detail, search policy hits → Policy Detail (`hitTarget` = `route`). DV-17.
- Known limits: no historical role edges exist in the seed (UI supports them); per-field change history waits for CP0.4; FSC display names are synthetic; "Correct field" (ADMIN, CP0.4) and "Request risk override" (S2) disabled.

## 10. F5 SBQ Risk Workbench — ACCEPTED 2026-11-16

**Owner acceptance (2026-11-16):** accepted for local synthetic-data development. Accepted limitations: no risk calculation or override engine; source-vs-rule conflicts are stored-assessment comparisons, not approved resolution decisions; no invented scores, thresholds or values; two SG sales remain unassessed. Next: CP0.4 intake proposal (not authorised).

**As built (2026-11-15; evidence `docs/acceptance/evidence/F5/`; OpenAPI `a4f49784316222b6c5fc43e47a9b71629e3067671cc5ba022c335c7ef77a9ec1`; no migration):**
- Backend: `app/domain/risk_register.py` (stored assessments only; `effective` = latest FINAL of the sale, as `load_facts`; `discrepancy` = the sale's latest FINAL SOURCE_ASSIGNED band ≠ latest FINAL RULE_ASSESSED band; disjunctive facets band/factor/origin/status/rule set/product/channel/FSC/effective/discrepancy; keyset paging; `summary` over the whole SG population with two separate grains: assessments, and sale events by effective band incl. unassessed sales) and `app/api/risk.py`: API-056 `GET /risk-assessments`, API-057 `GET /risk-assessments/{id}` (factors with vocabulary labels, rule-set version incl. checksum and approval status, input hash, provenance, full sale history with supersedes/superseded_by, source-vs-rule comparison, policy/sale/case links), API-058 `GET /risk-factors` (active `risk_factor` and `sbq_risk_band` code lists). Scope through sale → policy `market_code`; MY/missing → identical audited 404. `tests/test_risk.py`. `RiskAssessmentOut.supersedes_id` (added in F4) unchanged.
- Frontend: `src/features/risk/RiskWorkbenchPage.tsx` (+ tests): separation explainer; sale-grain tiles (High/Medium/Low effective, Source ≠ rule) that filter the register; assessment-population bars; factor vocabulary; URL-held filters; drawer `?assessment=` (dialog, Escape/focus) with comparison, factor table, record, history and Policy/Call Detail links. Links in: nav, Overview risk card ("Assessments →", case grain stays on the Overview), Call Detail context risk card, Policy Detail risk tab. DV-18.
- Seed facts: 229 SG assessments (74 rule-assessed, 155 source-assigned; 15 SUPERSEDED UNKNOWN), 195 SG sales (193 with a FINAL assessment, 2 unassessed), 3 conflicting sales (SALE-SG-000167 LOW→HIGH, -000168 and -000169 LOW→MEDIUM). No PROVISIONAL status, no stored score or weights, no MANUAL origin exist in the seed; the UI labels them if they appear.

## 11. CP0.4a Insurance transaction intake — ACCEPTED 2026-11-16

**As built (2026-11-16; evidence `docs/acceptance/evidence/CP0.4a/`; OpenAPI `d3aabc102cbe7a2730fbb166e0515d8284eb882e8e125b83fb9f57c39d49fcd9`; migration `0009_intake` on `call360_test` and `call360`):**
- Backend: `migrations/versions/0009_intake.py` (insert-only `intake_run`, `intake_item`, `field_change`; FK from every provenance table's `intake_item_id`; downgrade refuses once runs exist); `app/domain/intake.py` (guards, validation, conflicts, party resolution, eligibility, holds, single-transaction commit, `describe` outcome); `app/api/intake.py`: API-080 `GET /intake/sources`, API-084 `POST /intake/manual/preview` (persists only an audit event), API-085 `POST /intake/manual` (`Idempotency-Key` required; replay → 200 `replayed`; key reuse → 409), API-082/083 runs. Errors: `INGEST_VALIDATION_FAILED` (field locations and codes, never values), `INGEST_NON_SYNTHETIC_REJECTED`, `INGEST_CONTACT_NOT_SYNTHETIC`, `INGEST_MARKET_NOT_IN_SCOPE`, `INGEST_DUPLICATE_SOURCE_EVENT`, `INGEST_SALE_REF_EXISTS`, `INGEST_POLICY_FIELDS_DIFFER`, `INGEST_DUPLICATE_NEW_BUSINESS`, `IDEMPOTENCY_KEY_REQUIRED`/`_REUSED`. Audit: `INTAKE.PREVIEWED`, `INTAKE.COMMITTED`, `INTAKE.REJECTED`, `INTAKE.REPLAYED`, `CASE.HOLD_PLACED` (payload digest, references and codes only).
- Rules applied (existing only): source-assigned risk stored as supplied (no band/score calculated); every case held `AWAITING_SCRIPT_ASSIGNMENT` (no resolver); eligibility from governed `callable_party_roles` + DB check → `NO_ELIGIBLE_CONTACT` when none; ILP without risk → `RISK_TRIAGE`; `DATA_CONFLICT` not applicable to a new sale; state `VALIDATED`; owner unassigned; due date/priority source-provided (D-41). Existing-policy reuse requires all material fields to match; role changes on an existing policy are corrections (CP0.4b). Product set = the S0-SEED-1 synthetic products; SG currency SGD.
- Seed integrity: the seed content digest now covers seed-authored rows (`created_by = SYSTEM:seed`), so intake rows do not change it and any change to a seeded row still does; development digest `2ead19f3…` still matches its manifest after the demo.
- KPI-14 "Intake runs" is now measured from `intake_run` (ADMIN only); KPI-13 shows `MANUAL` by source type.
- Frontend: no intake screen (CP0.4b). Labels follow the record's source (Overview banner, Policy Detail banner, Call Detail "Synthetic intake case" banner); CP0.4 stage chips now say CP0.4b. `e2e/cp04a-checks.ts`. DV-19.
- Demo: `Call360-backend/scripts/intake_demo.py` (fresh synthetic SG references each run; preview → commit → replay; credentials from env or prompt, never printed). Development records created in the owner demo: `POL-SG-937467` with `SALE-SG-937467` → `CB-2026-10499` and top-up `SALE-SG-937468` → `CB-2026-10500` (runs IR-2026-000001/2).

### Original F2 scope (as authorised)

**Delivers (catalogue rows unchanged, all Singapore-scoped server-side):**
- **API-035 `/cases`:** the case register with search by case ref, policy ref, attempt or session ref. Filters: state, outcome category, effective risk band, overdue, hold reason, product family, ILP and due-date range. Also the dashboard `kpi` + `kpi_set` drilldown, reusing the F1 predicate functions. Sorting and cursor pagination.
- **API-036 `/cases/facets`:** counts computed after scope.
- **API-076 `/work-queues`:** due today, overdue, awaiting callback, and on hold by reason.
- **API-070/071 `/search`, `/search/suggest`:** exact, prefix and fuzzy matching on approved identifiers (case, policy, attempt and session references), plus exact-match phone or email lookup through the HMAC token (`contact_method.value_hmac`; never decrypted). Results show masked values only, and search terms are logged only as hashes.
- **Screens:**
  - `/calls` (Call Explorer) and `/queues` (Work Queues) following the mockup, with the five states and URL-held filters;
  - the top-bar search with suggestions (DV-12 lifted);
  - Dashboard cards, risk segments and priority rows link into the register.
- **Navigation to a case:** register and queue rows open `/cases/:caseId`, which is F3. Until then they show an explicit "available in F3" state rather than a dead link.

**Deferred by the owner:** saved views (API-072…075, `saved_view` table).

**Tests:**
- BE-API-01 (register and grain);
- BE-KPI-02 (drilldown set equality);
- BE-SRCH-01…06 and BE-SRCH-08 (BE-SRCH-07 is saved views, deferred);
- BE-SEC-02 and BE-SRCH-05 (no MY rows, counts, facets or suggestions);
- FE-01;
- E2E-02 (card → register count equality).
- E2E-06 (search → Policy Detail → Call Detail) completes with F3/F4.

**No new migration is expected.** The `case.read`, `queue.read` and `search.use` permissions already exist for ADMIN and USER.

Then: F3 Call Detail → F4 Policy Explorer → F5 SBQ Risk Workbench → CP0.4 intake → CP0.1B-3 → CP0.6.

## 12. CP0.4b Manual Intake portal — ACCEPTED 2026-11-16 (UI portion only)

**As built (2026-11-16; evidence `docs/acceptance/evidence/CP0.4b-UI/`; OpenAPI `9574dbb18d4bbae5a1bc1ed699420ede6c4734c430592770ab52c69606e53b5b`; no migration, head stays `0009_intake`):**

- **Backend:** API-087 `GET /api/v1/intake/reference` (`intake.read`, caller's market) in `app/api/intake.py`, schemas `IntakeReference` and options in `app/api/schemas.py`. Values come from the validator's own sources (`SYNTHETIC_PRODUCTS`, active `fsc_representative`, governed `sbq_risk_band` and `synthetic_contact_ranges`, request-model `Literal`s and the priority bounds). Tests: `test_reference_data_lists_what_the_validator_accepts`, permission inventory (6 intake routes).
- **Frontend:** `src/features/intake/` — `IntakePage` (sources, tabs), `ManualIntake` (form; preview; preview-gated submit with a kept `Idempotency-Key`), `Outcome` (server outcome and links), `IntakeHistory` (runs and run drawer), `model.ts` (payload shaping, SGT↔ISO, server `loc` → field mapping). Route `/intake` (`intake.read`); nav item enabled for ADMIN. Links: Overview "New callback case", Policy Explorer "Manual intake", Policy Detail "Add a sale" (`/intake?policy=…`).
- **Tests:** unit `model.test.ts`, `IntakePage.test.tsx`; Playwright `e2e/cp04b-checks.ts` (called from `overview.spec.ts`; journey timeout 120 s).
- **Deferred:** mock upstream and scheduling, corrections, saved drafts, Admin Integrations.

## 13. F6 Script Studio and Assignment Rules (read-only) — ACCEPTED 2026-11-16

**As built (2026-11-16; evidence `docs/acceptance/evidence/F6/`; OpenAPI `cf31afd86a5630e062cd67d9965b5d3fbf1b7e8af109b45c7ad3108018a31bb6`; no migration):**

- **Backend:** `app/api/scripts.py` — API-060 `GET /scripts` (filters: status, language, effective date, product family, risk band, channel, text; facets; product/band/channel match module *content conditions*, no case is evaluated), API-061 family, API-062 versions, API-064 rule versions with target pin and assigned cases (count plus latest 10), API-065 regulatory references, API-066 controls with in-scope question links. All `script.read`, market-scoped (rules via the target family's market). Fixes in scope: API-063 returned 500 for a DRAFT version (manifest SHA is null until frozen) and now filters regulatory references by market; `ScriptPin` and `ScriptVersionDetail` gained `script_family_id` (additive) for deep links. Tests: `tests/test_scripts.py` (8), permission inventory.
- **Frontend:** `src/features/scripts/` — `ScriptLibraryPage`, `ScriptFamilyPage` (version history, header with manifest, structure navigator, question details with expected-answer policy and controls; regulatory references visually separate), `AssignmentRulesPage` (rule registry with readable predicates, targets and case links; `?rule=` opens one), `shared.tsx`. Nav items enabled; Call Detail "Assigned script" and "Why this script" link to the version and rule. Stage S2 actions visible and disabled.
- **Tests:** unit `ScriptPages.test.tsx`; Playwright `e2e/f6-checks.ts` (both roles; journey Script Library → version → rule → Call Detail → back to the pinned version; a superseded rule's case keeps its version).
- **Not built (later stages):** editing, publishing, assignment evaluation, hold release, voice, LLM question generation, compliance decisions.

## 14. F7 Review Workbench and Voice Studio (read-only) — ACCEPTED 2026-11-16

**As built (2026-11-16; evidence `docs/acceptance/evidence/F7/`; OpenAPI `2b31989b101f4aeacdab396a742a44d3f6a20f8b3adea1a65815c2699d7f7303`; no migration):**

- **Backend:** `app/api/reviews.py` — API-077 `GET /review-queue` (`queue.read`; `queue=AWAITING_REVIEW|ALL`, `q`, `severity`, `status`, `category`, `origin`, `material`, `sort`, `limit`/`offset`; facets; materiality from the governed `finding_materiality_policy`; case SBQ band from the same facts as the case register; evidence from `evidence_refs` → `answer_observation`, `rule_evaluation`, question revision and controls). API-078 `GET /voice/preflight` (`voice.preflight.read`) lists capabilities, all `NOT_AVAILABLE`. Tests: `tests/test_reviews.py` (5), permission inventory.
- **Frontend:** `src/features/reviews/ReviewWorkbenchPage.tsx` (tiles from API counts, queue tabs, filters/sort/paging in the URL, selected-finding detail with Call Detail and Policy Detail links, S3 actions disabled), `src/features/voice/VoiceStudioPage.tsx` (status and capability table, S1 controls disabled, no media access). Nav: every Stage 0 screen now enabled. Tests: unit `ReviewWorkbench.test.tsx`; Playwright `e2e/f7-checks.ts` (both roles).
- **Not built (later stages):** finding adjudication, review decisions and maker-checker, evidence bundles, playback, voice sessions.

## 15. CP0.1B-3 Administration completion — ACCEPTED 2026-11-17

**As built (2026-11-17; evidence `docs/acceptance/evidence/CP0.1B-3/`; OpenAPI `ba7e04f87770866b5d5c80957baddff18a798fdcfc4477785f0511918a137ddc`; migration `0010_password_change_required` on `call360_test` and `call360`; dev seed digest unchanged):**

- **What was missing:** API-007, 009, 011, 013, 014…020, 026 and the Groups, Sessions and System screens (tabs were disabled "Later in Stage 0"); users could only be created by the operator CLI.
- **Backend:** `app/api/admin_access.py` (all the above); `local_credential.must_change_password` + enforcement in `app/security/authz.py` (`require()` → `403 PASSWORD_CHANGE_REQUIRED`; `/me` reports it); `create_local_account` records the reason and the Idempotency-Key digest in `ADMIN.USER_CREATED`; `AUTHENTICATED_ROUTES` adds `/auth/session` and `/me/password`. Audit actions: `ADMIN.USER_CREATED`, `ADMIN.PASSWORD_RESET`, `AUTH.PASSWORD_CHANGED`, `AUTH.PASSWORD_CHANGE_FAILED`, `ADMIN.MEMBERSHIP_ADDED`, `ADMIN.MEMBERSHIP_ENDED`, `ADMIN.GROUP_MAPPINGS_REPLACED`, `ADMIN.SESSION_REVOKED` (passwords never recorded). Tests: `tests/test_admin_access.py` (7), permission inventory.
- **Frontend:** Users (New user, Reset password, one-time password panel), `GroupsPage`, `SessionsPage`, `SystemPage`, `account/PasswordPage` (forced after a one-time password; also in the user menu), `AdminLayout` tabs. Tests: `AdminCompletion.test.tsx`; Playwright `e2e/cp01b3-checks.ts` (create → first sign-in → forced change → portal; groups; revoke; reset; system; USER denial).
- **Deferred, not blocking:** Admin Integrations (API-027) with the CP0.4b remainder; scope administration beyond the enabled market set (multi-market is a later decision, D-39); enterprise SSO (S5).

## 16. CP0.6 Integrated Stage 0 verification — technical verification ACCEPTED 2026-11-17 (governance pending)

- **Added tests only (no business functionality):** `Call360-backend/tests/test_stage0_acceptance.py` (all-route Singapore sweep and identical audited 404s, constraint/reference integrity, immutability and manifest reproduction, audit chain and secret-free audit, BE-SEC-04 injection sweep, seeded-only Malaysian audit references); `Call360-frontend/e2e/cp06-checks.ts` (one transaction through every module; seeded script and finding traceability; E2E-14 controlled empty/error/partial states). Matrix IDs added to existing tests (BE-API-04/05, BE-AUTH-10, BE-KPI-05, BE-SRCH-01/02/06, E2E-07/09/11).
- **Gate:** run twice on freshly reset `call360_test` (`evidence/CP0.6/gate_run_*.txt`); development database never reset (read-only digest and audit checks).
- **CP0.6-F1 resolved 2026-11-17:** `app/audit/scope.py` scopes the operational audit view (API-021, Administration 24 h count) to the caller's markets; out-of-scope business events hidden, access-denied events on out-of-scope records listed with the ID withheld (`scope_redacted`), seed manifest without dataset totals; ledger untouched (evidence `evidence/CP0.6-F1/`).
- **Open (governance):** SEC-008 security review (handoff `docs/security/SEC-008_REVIEW_HANDOFF.md`); approver names and signatures (C-20).

## 17. S1-A full-duplex browser voice POC — ACCEPTED 2026-11-17

Record: `docs/acceptance/S1.md` (D-44 boundaries), evidence `docs/acceptance/evidence/S1-A/`. Migration head
`0011_voice_session_permission` (test and development). OpenAPI `e45244f699ad9da410c8579f1f2f2151b112b1062daecc97cb4a38ff8db77dcd`.
Not started: S1-B…S1-E, S2, S3. Owner real-microphone check passed. Outstanding: Stage 0 governance (SEC-008, approvers).

## 18. S1-B voice-session persistence — IMPLEMENTED AND VERIFIED 2026-11-17 (awaiting owner acceptance)

Record: `docs/acceptance/S1.md` ("S1-B as built"), evidence `docs/acceptance/evidence/S1-B/`. Migration head
`0012_session_event` (test and development). OpenAPI `f057e6dbd6c985c87200569ef6ed081f74a1e3e982c36dc6d54f6e4c4e3e54b3`. Code: `app/voice/store.py`
(lifecycle, ledger, sweep), `app/api/voice.py` (resume, stop, status, list, persisted stream), lifespan recovery and
sweeper in `app/main.py`; frontend `useVoiceSession.ts`, `VoiceSessionTimeline.tsx`, Voice Studio history, Call Detail.
Not started: S1-C, S1-D, S1-E, S2, S3.

## 19. State at the end of the S1-B session (2026-11-17) — superseded by §20

**Status**
- **Stage 0:** every checkpoint and slice accepted; CP0.6 technical verification ACCEPTED. **Governance acceptance
  PENDING:** SEC-008 security review (handoff `docs/security/SEC-008_REVIEW_HANDOFF.md`, reviewer not named, not
  self-certified) and the three named approvers' signatures (`S0.md` → Approvals; names not assigned, C-20). Stage 0
  stays NOT_ACCEPTED until both are complete.
- **S1-A** (full-duplex browser voice, mock provider): **ACCEPTED** 2026-11-17 after the owner's real-microphone test.
  Accepted limitations: mock provider only; WebSocket audio transport (WebRTC planned for S1-E); no recording or
  transcript; no identity verification or compliance evaluation; no real customer calling.
- **S1-B** (session lifecycle and event persistence): **IMPLEMENTED AND VERIFIED** 2026-11-17, awaiting owner acceptance.
- **Next proposed:** S1-C consent-gated recording — **not implemented and not authorised**. Then S1-D (transcript),
  S1-E (GPT-Live behind the provider protocol, WebRTC).

**S1-B in brief** (details in §18 and `docs/acceptance/S1.md` "S1-B as built")
- One browser test session = one `contact_attempt` (BROWSER, CALL360_RUNTIME) plus, on connection, one
  `conversation_session` with guarded pins (published script + manifest, FINAL risk assessment + hash, latest fact
  snapshot + hash, contacted party, masked contact). States: CREATED (live), INTERRUPTED (resumable 30 s), FINALIZED,
  ABORTED; attempt FAILED if never connected. `case_event` gets VOICE_SESSION_STARTED / VOICE_SESSION_ENDED.
- **Migration `0012_session_event`:** insert-only, ordered event log per session (server `seq`; source
  SERVER/CLIENT/SYSTEM; client event ID unique per session so retries are stored and acted on once; client sequence
  and time with `out_of_order`; metadata-only `details` — never audio, transcript or microphone content).
- APIs: `POST /api/v1/voice/sessions`, `POST …/{id}/resume`, `POST …/{id}/stop` (idempotent), `GET …/{id}`,
  `GET /api/v1/voice/sessions?case_id=`; WebSocket `…/{id}/stream`. Startup recovery finalises open sessions
  (BACKEND_RESTART); a 15 s sweeper finalises never-connected (90 s), abandoned (interrupted > 30 s) and orphaned ones.
- Frontend: Voice Studio persisted record and timeline, resume offer after refresh, automatic resume after a network
  drop, case session history; Call Detail shows browser attempts with their timeline.

**Verification (S1-B)**
- Backend **325 passed**; frontend **86 unit passed**; Playwright **20 passed** (incl. 4 real-browser voice tests).
  Lint, types, OpenAPI contract and client drift, build and secret scans clean. Specs validator PASS.
- OpenAPI SHA-256 `f057e6dbd6c985c87200569ef6ed081f74a1e3e982c36dc6d54f6e4c4e3e54b3`.
- Chrome demonstration with a real backend restart: `evidence/S1-B/chrome_demo.txt` (disclosed synthetic microphone).

**Databases**
- `call360` (development) and `call360_test` at Alembic head **`0012_session_event`** (0010 one-time-password flag,
  0011 `voice.session.start` permission, 0012 session event log). Development seed digest `2ead19f36e09bdf3…` still
  matches its manifest; development audit chain verified (2616 events at the last check). The development database was
  never reset; runtime voice sessions on it are synthetic test sessions (e.g. `AT-2026-10048-3`).

**Repositories** (all on `main`, clean and in sync with `origin/main` at the end of this session; commits and pushes
were made by the owner, not by Claude Code)
- `Call360-specs` `e40c3ccc026fe578e4a0628906ff9f14da83faff`
- `Call360-backend` `d98e08ba8f2e0e6a4f71090e7848fa846485e92b`
- `Call360-frontend` `6fd7f5aa76e943ead6de8c33c0a414e0fb2b0b79`

**Local runtime**
- Backend dev server: `cd Call360-backend && make dev` (127.0.0.1:8000; was running as a Claude Code background task
  and stops with the session). Frontend: `cd Call360-frontend && npm run dev` (127.0.0.1:5173). Vite proxies `/api`
  including the voice WebSocket. Playwright runs its own servers on 8001/5174 against `call360_test`
  (`voice` project uses Chromium's fake microphone with `e2e/fixtures/fake-mic-hello.wav`).

**Important limitations (S1-B, awaiting acceptance)**
- Live connections and pending credentials are per process: after a restart, open sessions are finalised, not resumed.
- Resume needs the same signed-in user within 30 s; a refresh asks for microphone permission again.
- Browser timestamps are stored as reported; the server sequence is authoritative.
- Runtime test sessions count as contact attempts in operational metrics.
- Energy-based speech detection relies on browser echo cancellation; headphones give the cleanest interruption test.
- Carried forward: no recording (S1-C), transcript (S1-D) or real provider (S1-E); identity NOT_PERFORMED and
  compliance NOT_EVALUATED for every session; RR-11 (development DB role is a superuser) and RR-12 (weak development
  DB password, rotation deferred).

**Outstanding owner decisions**
1. Accept S1-B (or request changes).
2. Authorise S1-C and decide its consent and test-recording policy, including retention of local recordings.
3. Name the SEC-008 security reviewer and the three Stage 0 approvers (C-20).
4. Before S1-E: approval to use GPT-Live, its API key handling and data handling.
5. Still deferred: CP0.4b remainder (mock upstream, corrections, saved drafts, Admin Integrations), saved views.


## 20. State at the end of the S1-C implementation (2026-11-17) — superseded by §21

**Status**
- **Stage 0:** unchanged — technical verification ACCEPTED; governance acceptance PENDING (SEC-008 reviewer, three
  named approvers, C-20). Never self-certify SEC-008 or invent signatures.
- **S1-A, S1-B:** ACCEPTED 2026-11-17 (S1-B limitations accepted: no connection survives a restart; resume only within
  30 s; no audio or transcript content in S1-B; synthetic-microphone demos are not real-microphone acceptance).
- **S1-C consent-gated recording:** IMPLEMENTED AND VERIFIED 2026-11-17, **awaiting owner acceptance**. Record:
  `docs/acceptance/S1.md` ("S1-C design", "S1-C as built", "S1-C known limitations"); evidence `evidence/S1-C/`.
- **Next proposed:** S1-D transcript and playback — not authorised.

**S1-C in brief**
- Consent per session before Start, default "Do not record", test-only notice `S1C-TEST-1`; stored in the
  insert-only session ledger. Microphone permission is never consent; nothing before the server's `session.ready`
  confirmation can enter a recording.
- Browser records MIC and PROVIDER_PLAYBACK (rendered audio) in 2 s PCM16 chunks with SHA-256; server stores them
  encrypted (AES-256-GCM, separate key) outside the database and repositories with server-generated keys; per
  connection segment manifests; coverage computed (MISSING, UPLOAD_FAILED, DISCONTINUITY, SESSION_INTERRUPTED,
  END_NOT_CONFIRMED, CAPTURE_INTERRUPTED); never backfilled.
- API recording status: NOT_RECORDED / RECORDING / COMPLETE / PARTIAL / FAILED / PURGED, derived from the approved
  `media_status` vocabulary plus coverage. Audio retrieval needs `recording.read` (USER only), audited.
- Browser sessions are labelled TEST_SESSION everywhere; KPI-01/02 disclose them (`test_sessions_in_numerator/
  denominator`); KPI definitions unchanged.

**Verification:** backend 334 passed; frontend 89 unit passed; Playwright 22 passed (6 voice incl. 2 S1-C); lint,
types, OpenAPI contract and client drift, build, secret scans clean; specs validator PASS. OpenAPI SHA-256
`cc52479f8d01be081c600ab9c39bc678ce384d53fc7a429fa123ca3acb5ac0fd`. Chrome demo: `evidence/S1-C/chrome_demo.txt`.

**Databases:** `call360_test` and `call360` (development) at **`0013_recording`**. Development seed digest
`2ead19f3…` MATCH; audit chain verified before the demo (2616 events). Development `.env` gained
`RECORDING_ENCRYPTION_KEY` (backup of the previous file: `~/call360-backups/pre_s1c_20261117_025210/`);
`.env.test` gained its own key. Development demo recordings (synthetic tones) are in `~/.call360/recordings/call360`.

**Repositories:** all three on `main` at the S1-B owner commits (specs `e40c3cc`, backend `d98e08b`, frontend
`6fd7f5a`) with S1-C changes **uncommitted** (commits need owner authorisation).

**Outstanding owner decisions**
1. Accept S1-C (or request changes), including D-45 (test notice and consent model), D-46 (`recording.read` for USER
   only), D-47 (local storage, 168 h local retention), D-48 (test-session label and KPI disclosure).
2. K-5: should test sessions be excluded from attempt KPIs? (business decision; not implemented).
3. Real-microphone check of recording (as done for S1-A).
4. SEC-008 reviewer and Stage 0 approvers (C-20).
5. Before S1-E: GPT-Live approval, API-key and data handling. Still deferred: CP0.4b remainder, saved views.

## 21. State after the S1-C acceptance and S1-D proposal (2026-11-17) — superseded by §22

**Status**
- **Stage 0:** technical verification ACCEPTED; governance acceptance PENDING (SEC-008 reviewer, named approvers,
  C-20). Never self-certify SEC-008 or invent signatures.
- **S1-A, S1-B, S1-C:** ACCEPTED 2026-11-17. S1-C was accepted after the owner's real-microphone recording test.
  Evidence in `evidence/S1-C/` preserved unchanged.
- **Owner decisions:** D-45 test-only consent wording approved (production wording pending, DEC-004); D-46
  `recording.read` for USER, not ADMIN; D-47 encrypted local storage, 168 h retention, development only (DEC-015
  pending); D-48 marked test sessions **excluded** from operational callback KPIs (numerators and denominators),
  still visible in test activity, case history and audit; seeded historical attempts never excluded for being
  synthetic. K-5 is resolved for test sessions by D-48.
- **D-48 correction (implemented, authorised with the acceptance):** `kpis.is_test_attempt` marker (BROWSER +
  CALL360_RUNTIME); KPI-01, KPI-02 (+ trend) and KPI-12 use operational attempts only (KPI-12 ordinals too);
  `exclusions.test_sessions_excluded`, KPI-02 `test_sessions_excluded_count`; `reporting_version` `S0-KPI-3`;
  `docs/product/S0_KPI_DEFINITIONS.md` §3.1. OpenAPI unchanged (`cc52479f…`); no migration. Backend **338 passed**
  (new `tests/test_kpi_test_sessions.py`, updated `test_recording.py` and the BE-KPI-01 SQL oracle); ruff, mypy,
  contract, secret scan clean; frontend 89 unit passed. Evidence `evidence/S1-C/d48_kpi_correction.txt`.
- **S1-D transcript and playback:** PROPOSED, **not authorised**. Scope, data model (`0014_transcript`), APIs, UI,
  tests and decisions D-49…D-53 in `docs/acceptance/S1.md` "S1-D proposal". Key recommendation: a local offline STT
  engine (`faster-whisper`, `small.en`, pinned) behind a `TranscriptionEngine` interface, post-session batch over
  the stored recording; the mock's fixed message is reference text only, never a transcript. Installing the package
  and downloading the model (~480 MB) need owner permission.

**Databases:** `call360_test` and `call360` at `0013_recording` (no change in this session). Development backend
(`make dev`, 127.0.0.1:8000) and frontend (127.0.0.1:5173) were left running.

**Repositories:** all three on `main` at the S1-B owner commits (specs `e40c3cc`, backend `d98e08b`, frontend
`6fd7f5a`); S1-C and the D-48 correction are **uncommitted** (commits need owner authorisation).

**Outstanding owner decisions**
1. Authorise S1-D (`IMPLEMENT S1-D`) and decide D-49 (engine and model, plus download permission), D-50
   (`transcript.sensitive.read` for USER only), D-51 (English only), D-52 (development confidence thresholds),
   D-53 (synchronised two-track player).
2. Commit authorisation for S1-C and the D-48 correction (separate branches per repository).
3. SEC-008 reviewer and Stage 0 approvers (C-20).
4. Before S1-E: GPT-Live approval, API key and data handling. Still deferred: CP0.4b remainder, saved views.

## 22. Current state (2026-11-17, S1-D session) — read this first

**Status**
- Stage 0: technical verification ACCEPTED; governance acceptance PENDING (SEC-008 reviewer, approvers, C-20).
  Never self-certify SEC-008 or invent signatures.
- S1-A, S1-B, S1-C ACCEPTED. **S1-D transcript and playback: IMPLEMENTED AND VERIFIED 2026-11-17, awaiting owner
  acceptance.** Record: `docs/acceptance/S1.md` ("S1-D owner authorisation", "S1-D as built", "S1-D known
  limitations"); evidence `docs/acceptance/evidence/S1-D/`.
- Next: S1-E (GPT-Live) remains deferred and not authorised; S2/S3 not authorised.

**S1-D in brief**
- Local offline faster-whisper 1.2.1 + `Systran/faster-whisper-small.en` @ `d1d751a5…`, model files in
  `~/.call360/models/faster-whisper-small.en` (outside Git; SHA-256 pinned and verified on load). Configured by
  `TRANSCRIPTION_MODEL_DIR` in the gitignored `.env` (development) and `.env.test` — both were given this line.
- Background worker transcribes each finalised consented track separately (speaker from the track), span by span
  (never across gaps); runs are immutable revisions with full provenance; text is AES-GCM encrypted in the recording
  store, never in the database, and purged with the audio. Statuses map to the approved transcript vocabulary;
  never certified (`NOT_REVIEWED`).
- Call Detail: synchronised two-track player (Web Audio, one clock, mute per track, hatched gaps, audited PLAYBACK
  retrieval on demand) and speaker-grouped transcript with uncertainty markers, gap markers and segment-click seek.
- `transcript.sensitive.read` for USER only (D-50); ADMIN sees status and provenance only.

**Verification:** backend 357 passed (incl. 19 transcript/golden); frontend 94 unit; Playwright 23; lint, types,
contract (`e0a02959438fccd6750f89836c749ffa202b338d24580efa9a831b121d52ecea`), secret scans, build clean; specs
validator PASS. Golden dataset: clean-speech WER 3.2 %, timing ≤ 0.52 s, no text from silence/tone/noise. Chrome
demo `evidence/S1-D/chrome_demo.txt`, including one **confident misrecognition with no marker** (AT-2026-10048-11).

**Databases:** `call360_test` and `call360` at **`0014_transcript`**; development seed digest MATCH, audit chain OK
(2634 events before the demo). Demo sessions AT-2026-10048-7…12 exist on CB-2026-10048 (synthetic).

**Repositories:** all three on `main` at the S1-B owner commits (specs `e40c3cc`, backend `d98e08b`, frontend
`6fd7f5a`); S1-C, the D-48 correction and S1-D are **uncommitted**. Backend `pyproject.toml`/`uv.lock` gained
`faster-whisper==1.2.1` (pre-change copies were kept only in a session scratchpad).

**Process note:** never run backend pytest and the Playwright suite at the same time — both use `call360_test` and
pytest resets it (this caused spurious failures once in this session).

**Outstanding owner decisions**
1. Accept S1-D (or request changes); real-microphone transcript check (speak known phrases, compare by ear and eye).
2. Commit authorisation for S1-C, D-48 and S1-D (separate branches per repository).
3. SEC-008 reviewer and Stage 0 approvers (C-20).
4. Before S1-E: GPT-Live approval, API key and data handling. Still deferred: CP0.4b remainder, saved views.
