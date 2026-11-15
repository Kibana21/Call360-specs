# Call360 — Session handoff

**Written:** 2026-11-15, at the end of a Claude Code session.
**Updated:** 2026-11-15, after owner acceptance of CP0.1B-1.
**Authorization:** CP0.2 **specification review and planning only** (2026-11-15). No implementation, migration, reset, spec alignment, commit or push is authorised. The next step waits for an explicit owner instruction.
**Process:** strict specification-driven development (workspace `CLAUDE.md` §10). Each checkpoint is implemented and accepted before the next one starts. Checkpoints never advance automatically.
**Secrets:** this document contains none. Credentials live only in gitignored local files (§4).

## 1. Checkpoint status

| Checkpoint | Status | Record |
|---|---|---|
| CP0.0 Specification foundation | **ACCEPTED** 2026-11-15 | `docs/acceptance/CP0.0.md` |
| CP0.1A Core authentication and application shell | **ACCEPTED** 2026-11-15 (after UI-1…4 and scanner corrections) | `docs/acceptance/CP0.1A.md` |
| CP0.1B-1 Configuration foundation | **ACCEPTED** 2026-11-15 (local development; uncommitted) | `docs/acceptance/CP0.1B-1.md` |
| CP0.1B-2 Market scope | NOT_STARTED | — |
| CP0.1B-3 Administration completion | NOT_STARTED | — |
| CP0.2 Domain schema and seed | NOT_STARTED — specification review and planning authorised; proposal presented for owner review | `docs/plans/S0_IMPLEMENTATION_PLAN.md` |
| CP0.3 … CP0.6 | NOT_STARTED | `docs/plans/S0_IMPLEMENTATION_PLAN.md` |

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

## 3. Latest verification (2026-11-15; `docs/acceptance/evidence/CP0.1B-1/`)
All 16 checks exited 0:

| Check | Result |
|---|---|
| Backend tests | **98 passed** |
| Frontend unit and component tests | **30 passed** |
| **Playwright** against the real stack | **14 passed** (twice consecutively); axe zero serious/critical at 1280 and 1440 px |
| ruff, mypy `--strict`, ESLint, tsc, build | Clean |
| Secret scans (gitleaks 8.30.1 with Call360 rules) | Self-test 11 formats × 50 = 50/50; 0 false positives; repos and frontend bundle clean |
| npm audit | 0 vulnerabilities |
| Dev audit chain | Verified |
| Specs validator | PASS (237 requirements, 55 business tests, 62 CP0.0 checks, 100 test IDs) |

OpenAPI SHA-256: `c71599f73f6bc54dae120e89b6728a41324343bc384726efc9f62a92eaad83a0`.

## 4. Repositories and environment

| Repo | HEAD (owner commit, pushed to `origin/main`) | Uncommitted work |
|---|---|---|
| Call360-specs | `a08b7b6` | CP0.1A acceptance and defect-correction evidence; B-1 spec alignment (access design §8 D-25, API catalogue API-022…025, data model, test matrix); `CP0.1B-1.md`; `S0.md`; B-1 evidence; this handoff |
| Call360-backend | `cc57961` | All B-1 code: `app/config/`, `app/api/admin_config.py`, migration 0002, `tests/test_config.py`, schemas, OpenAPI artifact, `pyproject.toml` ruff entry |
| Call360-frontend | `9ee9f3c` | B-1 UI: `ConfigPage.tsx` and tests, `e2e/config.spec.ts`, route and tab, regenerated client and pin, CSS contrast fix |

Everything up to the CP0.1A defect corrections is committed by the owner. B-1 is accepted but **uncommitted**; committing it needs owner authorisation. On 2026-11-15 the working trees were re-verified against both B-1 manifests (all hashes match).

**Database:** local PostgreSQL 15, database `Call360_db`.

| Schema | Owner / login role | Migration head | Notes |
|---|---|---|---|
| `call360` (development) | `Call360_db_user` (**superuser**, RR-11) | `0002_config_foundation` | 21 tables. Accounts: `dev.admin` (ADMIN), `dev.user` (USER) |
| `call360_test` (automated tests) | `call360_test_user` (no superuser; no access to `call360`) | `0002_config_foundation` | Reset only by the guarded test harness and E2E setup |

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
| **Development database password rotation (outstanding)** | The `Call360_db_user` password is weak and was exposed in this session's conversation, command lines and, briefly, a local file. It never reached Git; history was scanned | **Owner should rotate.** Procedure: in your own terminal, run `psql … \password "Call360_db_user"` (no echo), then `uv run python scripts/make_env.py --force` (rewrites `.env`; signs sessions out), restart `make dev`, check `/health/ready`, run `make secret-scan`, and clear any shell or psql history containing the old value |
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

## 7. Next checkpoints (none authorised)
1. ~~Owner acceptance of CP0.1B-1~~ — done 2026-11-15. Owner review of the CP0.2 specification proposal is pending (then spec alignment, then `IMPLEMENT CP0.2`).
2. **CP0.1B-2 Market scope.**
   - *Depends on:* B-1 accepted (the `market` list).
   - *Delivers:* `group_scope_mapping`; scope resolution in `AccessContext` (currently empty, so scoped queries fail closed); SQL scope predicates; 404 plus audit for out-of-scope objects; tests BE-IAM-02 (scope half) and BE-SEC-02 against fixtures.
   - *Must be accepted before CP0.3* exposes any market-scoped record.
3. **CP0.1B-3 Administration completion.**
   - *Depends on:* CP0.1A only. It may run at any time, but must be accepted before CP0.6.
   - *Delivers:* API-007, 009, 011, 013, 014…020, 026; screens `/admin/groups`, `/admin/sessions`, `/admin/system`.
4. **CP0.2 Business data model and deterministic seed.**
   - *Depends on:* CP0.1A and CP0.1B-1 accepted.
   - *Delivers:* 34 tables with Build = CP0.2 (party, policy, sale, risk, scripts, callback, evidence; `transcript_segment`, `media_asset`, `risk_override` and `review_decision` are **not** built); governed code-list values (synthetic, not AIA-approved); deterministic seed (≥ 250 cases, golden fixtures `CB-2026-10482…10498`); tests BE-DATA-01…12.
5. **Later:** CP0.3 (read APIs, KPIs, search; needs B-2), CP0.4 (intake), CP0.5 (S0 screens), CP0.6 (integrated gate and S0 acceptance).
