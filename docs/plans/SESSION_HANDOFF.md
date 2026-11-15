# Call360 — Session handoff

**Written:** 2026-11-15, at the end of a Claude Code session.
**Updated:** 2026-11-15, after owner acceptance of CP0.1B-1.
**Authorization:** F0 + F1 ACCEPTED. F2 **ACCEPTED** 2026-11-15. F3 Call Detail (`IMPLEMENT F3`) **implemented and verified 2026-11-15, awaiting owner acceptance**. Vertical slices approved (D-40). Not authorised: F2–F5, saved views, intake, B-3, commits, pushes. No real customer data.
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
| CP0.1B-3 Administration completion | NOT_STARTED | — |
| CP0.2 Domain schema and seed | **ACCEPTED** 2026-11-15 (local synthetic-data development; deployed to `call360` at `0007`); password rotation deferred (RR-12); Singapore-only scope decision D-39 recorded | `docs/acceptance/CP0.2.md` |
| **F3** Call Detail | **IMPLEMENTED AND VERIFIED** 2026-11-15, awaiting owner acceptance | §8 below, `evidence/F3/` |
| **F2** Work Queues and search | **ACCEPTED** 2026-11-15 (AWAITING_CALLBACK queue definition approved; saved views, register grain modes, nonessential search filters deferred) | §7 below, `evidence/F2/` |
| F3–F5, CP0.4, CP0.1B-3, CP0.6 | NOT_STARTED (vertical slices, D-40) | `docs/plans/S0_IMPLEMENTATION_PLAN.md` |

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

## 9. F4 Policy Explorer and Policy Detail — implemented and verified (awaiting acceptance)

**As built (2026-11-15; evidence `docs/acceptance/evidence/F4/`; OpenAPI `d8d118b32bed0a5ee7d70a238cbc9984d34b992104435a2bd26f23fedfd750bc`; no migration):**
- Backend: `app/domain/policy_register.py` (policy rows, filters, disjunctive facets, keyset paging; reuses F2 ref matching, HMAC contact search and cursors; case outcome from `load_facts`, effective band = latest FINAL assessment of the latest sale) and `app/api/policies.py`: API-050 `GET /policies`, API-051 `GET /policies/{id}` (header, record provenance and source/as-of per material field, external refs, related cases with outcome and pinned script), API-052 `/parties` (`party.read`; one card per party with role edges incl. ended, masked contact methods incl. ended/suppressed, per-case eligibility evidence incl. superseded), API-053 `/sales`, API-054 `GET /sales/{id}` (sale context, fact snapshots, risk history with `supersedes_id`, cases), API-055 `/history` (record lineage over policy, sales, role edges, snapshots, risk assessments; `field_changes` = NOT_AVAILABLE / `LEDGER_ARRIVES_CP0_4`). Every query filters `market_code = ANY(:markets)`; MY/missing → identical audited 404. `tests/test_policies.py`.
- Frontend: `src/features/policies/PolicyExplorerPage.tsx` (URL filters, facets, KPI tiles from facets, intake buttons disabled CP0.4) and `PolicyDetailPage.tsx` (tabs `sale`, `parties`, `risk`, `script`, `cases`, `source` in `?tab=`; `?sale=` must belong to the policy); `src/features/case/evidence.tsx` shared with Call Detail; links Policy → Call Detail, Call Detail → Policy (`?sale=`), register policy refs → Policy Detail, search policy hits → Policy Detail (`hitTarget` = `route`). DV-17.
- Known limits: no historical role edges exist in the seed (UI supports them); per-field change history waits for CP0.4; FSC display names are synthetic; "Correct field" (ADMIN, CP0.4) and "Request risk override" (S2) disabled.

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
