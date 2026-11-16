# Call360 — Stage 0 implementation plan (CP0.0, CP0.1A, CP0.1B, CP0.2–CP0.6)

**Status:** accepted with CP0.0 (2026-11-15); CP0.1A/CP0.1B split and single-database schema design aligned 2026-11-15 (owner decisions D-21, D-22, D-23; recorded in `docs/acceptance/CP0.1A.md`)
**Process:** strict specification-driven development (workspace `CLAUDE.md` §10). Each checkpoint follows requirements → specification → review → explicit approval (`IMPLEMENT CPx.x`) → implementation → tests → acceptance. Checkpoints are never combined or auto-advanced.
**Supersedes:** the S0 checkpoint numbering in execution plan §C and §B0 (C-28; mapping in §5). It does not change any requirement.
**Withdrawn proposal:** `docs/plans/LOCAL_BUILD_PLAN.md` (an unapproved earlier draft) is no longer present in the repository. Its conflicting decisions are not carried forward (C-21).

## 1. Working rules (local development)

- **Repositories:** three independent local working trees: `Call360-specs`, `Call360-backend`, `Call360-frontend`. There are no GitHub Actions, CI/CD, PR workflows, branch protection, GitHub App credentials or cross-repo automation.
- **Git:** commits, pushes, merges and branches happen only with explicit owner authorisation. Evidence without commits uses the base SHA plus a deterministic file manifest (ADR-0003 §6).
- **Synthetic data only:** `DATA_POLICY=SYNTHETIC_ONLY` (ADR-0008 §6).
- **Database:** one existing database, `Call360_db`, with two schemas: `call360` for application development and `call360_test` for automated tests. The application uses `Call360_db_user`. Tests use a separate least-privilege role confined to `call360_test`, with separate connection configuration and fail-closed guards. **Automated tests never reset or touch `call360`** (D-16 as amended by D-22; S0_IDENTITY_ACCESS_DESIGN §10). No Docker PostgreSQL.
- **Mandatory gates at every implementation checkpoint:**
  - the checkpoint's tests;
  - secret scan (SCAN-01, plus SCAN-02 once a frontend bundle exists);
  - security tests relevant to the checkpoint;
  - `validate_specs.py`.

  A missing tool means the checkpoint is BLOCKED, never "skipped".
- **Scope discipline:** Stage 0 physically builds 59 tables, the 80 catalogued endpoints and the 29 catalogued routes, each in its stated checkpoint. Endpoints in API catalogue §9, and tables marked "not built in S0", remain **documentation only** until their stage is authorised. No placeholder routes or empty tables (D-19, D-20).
- **Specs first:** any implementation finding that contradicts a CP0.0 document stops work and is raised as a specs change.

## 2. Checkpoints

### CP0.0 — Specification foundation *(this checkpoint)*

| Item | Content |
|---|---|
| Repos | Call360-specs only |
| Depends on | Owner authorisation "AUTHORIZE CP0.0 SPEC EDITS" (given 2026-11-15) |
| Deliverables | ADR-0003…0008 and ADR index; `APPROVED_EXCEPTIONS.md`; `S0_DATA_MODEL.md`; `S0_IDENTITY_ACCESS_DESIGN.md`; `S0_API_CATALOGUE.md`; `S0_SCREEN_SPEC.md`; `S0_KPI_DEFINITIONS.md`; `THREAT_MODEL_S0.md`; `ASVS_S0_CONTROL_MATRIX.md`; `S0_TEST_MATRIX.md`; `S0.md` (NOT_STARTED); `CP0.0.md`; this plan; consistency updates to supporting docs; validator extension; evidence manifest tool |
| Acceptance | AC-0.0-01…12 in `docs/acceptance/CP0.0.md` |

### CP0.1A — Core authentication and application shell

| Item | Content |
|---|---|
| Repos | backend, frontend |
| Depends on | CP0.0 accepted; "IMPLEMENT CP0.1A" |
| Requirements | IAM-001, IAM-002, IAM-003, IAM-004 (group→role→permission mechanism), IAM-005, IAM-006, IAM-007, IAM-008, IAM-009, IAM-010 (Users screen: list, enable/disable), IAM-011, SEC-002, SEC-003, SEC-005, SEC-006, SEC-007, GOV-001 (data-policy setting), GOV-002, ADMIN-001 (users and audit), ADMIN-002 (user changes), ADMIN-003, APP-001 (shell) |
| Tables | Migration 0001 creates the 15 tables with Build = CP0.1A in S0_DATA_MODEL §4.1 (nothing else) |
| Endpoints | API-001, 002, 003, 004, 005, 006, 008, 010, 012, 021 (10, Build = CP0.1A in S0_API_CATALOGUE) |
| Routes | `/login`, `/session-expired`, `/unauthorized`, `/` (interim landing: real authenticated-session summary from `/me` until CP0.5), `/admin` (redirects to `/admin/users`), `/admin/users`, `/admin/audit`. Every other navigation item is visible but disabled with its stage label. No global search box yet |
| Backend deliverables | Project setup (`pyproject.toml`, lock file, Makefile targets per ADR-0003 §5); settings, with **separate application and test connection configuration and fail-closed schema guards** (S0_IDENTITY_ACCESS_DESIGN §10); error envelope; correlation ID; security headers; migration 0001; IdentityProvider protocol plus local provider; Argon2id; login, refresh, logout and CSRF; refresh rotation with reuse detection and the concurrent-refresh rule (§4); per-request authorization (group → role → permission); login throttling; rate limits; audit writer with hash chain and `audit-verify`; `bootstrap-admin` and `create-local-user` CLIs; admin users and audit APIs; health; deterministic OpenAPI |
| Frontend deliverables | Vite/TS project; design tokens and CSS ported from the HTML mockup; shell reproducing the mockup's sidebar groups, header, breadcrumb and user controls; login, session-expired and unauthorized screens; interim landing; Users and Audit screens; auth client (CSRF header, single-flight plus cross-tab refresh lock); generated API client, `contract.lock.json`, `api:check`; Playwright smoke run against the real local stack |
| Database setup (owner-run, at implementation) | Create schemas `call360` and `call360_test` and the least-privilege test role (S0_IDENTITY_ACCESS_DESIGN §10). Nothing is created during specification work |
| Acceptance tests | BE-AUTH-01…10, BE-IAM-01, BE-IAM-02 (role half), BE-IAM-03, BE-SEC-01, BE-SEC-03, BE-SEC-05, BE-SEC-06, BE-AUD-01…04, BE-DATA-01 (15 tables), BE-DATA-10 (data-policy setting), BE-DATA-14, BE-CT-01, FE-01…04, E2E-01, E2E-10 (partial: USER denied admin), E2E-13 (partial: disable ends session), E2E-15, E2E-18 (partial: branding), SCAN-01, SCAN-02 |
| Acceptance record | `docs/acceptance/CP0.1A.md` (checklist AC-0.1A-01…12). CP0.1A must be **demonstrated and accepted** before any CP0.1B package or CP0.2 begins |
| Existing state to reconcile first | Backend has only an ignored `.venv/`; no `pyproject.toml` or lock file is present. CP0.1A creates the declared manifest and reviews the venv against it before use |

### CP0.1B — Administration and configuration (three packages, each authorised separately)

CP0.1B builds the 6 tables with Build = CP0.1B (packages B-1 and B-2). It is **not** a blanket prerequisite for CP0.2. Each package is built just before the first downstream work that needs it. Each needs its own authorisation (`IMPLEMENT CP0.1B-1` and so on), its own tests and its own acceptance. All three must be accepted before CP0.6.

| Package | Content | Must be accepted before |
|---|---|---|
| CP0.1B-1 Configuration foundation | Tables `code_list`, `code_list_version`, `code_value`, `feature_flag`, `feature_flag_change`; API-022…025; route `/admin/config`. Requirements ADMIN-004, RISK-006 (mechanism). Tests BE-CFG-01, FE-01 (config) | CP0.2, whose seed uses the governed code lists |
| CP0.1B-2 Market scope (Singapore-only, D-39) | Table `group_scope_mapping` seeded `LOCAL_ADMIN`→SG, `LOCAL_USER_SG`→SG (no MY mapping); enabled-markets setting `{SG}`; scope resolution in `AccessContext` (mapped ∩ enabled); SQL scope predicates; 404-plus-audit on out-of-scope objects, including `MY` IDs for ADMIN. No scope-administration UI or API (deferred). Requirements IAM-004 (scope half), SEARCH-006 (mechanism). Tests BE-IAM-02 (scope half), BE-SEC-02 (mechanism, against `CB-2026-20001` and other MY fixtures). **Market-scoped authorization must be implemented and tested before any market-scoped business record is exposed through an API** | CP0.3 |
| CP0.1B-3 Administration completion | API-007, 009, 011, 013, 014…020, 026; routes `/admin/groups`, `/admin/sessions`, `/admin/system`. Requirements IAM-010 (groups and membership UI), ADMIN-001 (complete), ADMIN-002 (group and mapping history). Tests BE-AUD-04 (groups and mappings), BE-AUTH-06 (admin session revoke), E2E-13 (complete), FE-01 (admin screens) | CP0.6 |

Until CP0.1B-2 is accepted, a principal has no market scope, so any scoped query fails closed. No business data exists before CP0.2 anyway.

### CP0.2 — Business domain schema and deterministic synthetic seed

| Item | Content |
|---|---|
| Repos | backend |
| Depends on | CP0.1A accepted; CP0.1B-1 accepted; "IMPLEMENT CP0.2" |
| Requirements | CASE-001, CASE-002, SUR-001, PARTY-001…004 (data), POL-001…003, POL-005, POL-006, RISK-001…004, RISK-006, SCR-001, SCR-002, SCR-005, ING-003, REG-001, REG-002, GOV-001 (data), APP-003 (data) |
| Deliverables | Migrations for the 34 tables with Build = CP0.2 (S0_DATA_MODEL §4.6; `transcript_segment`, `media_asset`, `risk_override` and `review_decision` are **not** created), with enums, constraints, immutability triggers, session pins and the hold check; governed code lists seeded; synthetic script families, modules, questions and assignment rules; synthetic risk rule set; seed generator per §6 (`make seed`, deterministic) |
| Migrations (D-29) | `0003_party_policy_sale` (8 tables), `0004_sbq_risk` (3), `0005_scripts_regulatory` (12), `0006_case_evidence` (11), `0007_governed_values` (reference data only); assignment in S0_DATA_MODEL §4.6 |
| Specification basis | Aligned 2026-11-15 (D-29…D-38): code-list references (S0_DATA_MODEL §2.1), transitions and historical pin validity (ADR-0005 §3–4), governed version-1 values and synthetic contact identifiers (S0_DATA_MODEL §6.1), exact seed volumes (§6.2), data-protection keys (S0_IDENTITY_ACCESS_DESIGN §10) |
| Separate approvals inside `IMPLEMENT CP0.2` | (1) Generating and installing the two local data-protection keys (D-34), never printed or committed. (2) Migrating and seeding the development schema `call360`; until then only `call360_test` is migrated and seeded, by the guarded harness |
| Not in CP0.2 | Any API, UI or OpenAPI change; scope resolution (CP0.1B-2); intake (CP0.4); recordings, transcripts, review decisions and voice |
| Acceptance tests | BE-DATA-01…13, BE-API-02 (model level), SCAN-01, plus regression of all CP0.1A and CP0.1B-1 tests |
| Acceptance record | `docs/acceptance/CP0.2.md` (AC-0.2-01…11) |

### Vertical-slice delivery of CP0.3 and CP0.5 (D-40, owner-approved 2026-11-15)

CP0.3 (read APIs) and CP0.5 (screens) are delivered together as vertical slices. Each slice includes:
- the backend APIs, with scope, permissions and tests;
- the regenerated OpenAPI and typed client;
- the screen, following the mockup, with all five states;
- a Playwright run against the real stack.

Each slice needs its own `IMPLEMENT` and its own acceptance. **CP0.4 (intake) follows the slices**, so the earlier "CP0.5 depends on CP0.4" ordering no longer applies. Requirements, data model, API catalogue rows (API-0xx IDs and permissions) and routes are unchanged.

| Slice | Content (catalogue IDs, routes) | Status |
|---|---|---|
| F0 | CP0.1B-2 reduced by D-39: `group_scope_mapping` (migration `0008_market_scope`) seeded with SG only; enabled markets `{SG}`; scope resolution; uniform audited 404 | **Accepted** 2026-11-15 |
| F1 | Overview: API-030…034; route `/` | **Accepted** 2026-11-15 |
| F2 | Work Queues and search: API-076, 035/036, 070/071; `/queues`, `/calls`; Dashboard click-through. **Saved views (API-072…075, `saved_view`) deferred by owner** | **Accepted** 2026-11-15 |
| F3 | Call Detail: API-037…047, 063; `/cases/:caseId` | **Accepted** 2026-11-15 (presentation refinements delivered with F4) |
| F4 | Policy Explorer and Detail: API-050…055; `/policies`, `/policies/:id` | **Accepted** 2026-11-15 |
| F5 | SBQ Risk Workbench: API-056…058; `/risk-assessments` | **Accepted** 2026-11-16 (limitations accepted) |
| CP0.4a | Manual transaction intake: API-080, API-082…085; migration `0009_intake` | Implemented and verified 2026-11-16; awaiting owner acceptance |

### CP0.3 — Read APIs, KPIs, search, saved views, queues

| Item | Content |
|---|---|
| Repos | backend |
| Depends on | CP0.2 accepted; CP0.1B-2 accepted; "IMPLEMENT CP0.3" |
| Requirements | APP-002, APP-004, APP-005, APP-006, PARTY-005, POL-002, POL-003, RISK-002, RISK-005, SCR-003, SCR-004, SEARCH-001…007, SEC-004, IAM-005 |
| Deliverables | `saved_view` table (Build = CP0.3); API-030…078 per catalogue; KPI predicates shared between KPIs and the explorer; masking serializers; search with ranking and matched field; saved views; queues; voice preflight; OpenAPI regenerated and checksum recorded |
| Acceptance tests | BE-API-01…07, BE-KPI-01…04, BE-SRCH-01…08, BE-SEC-02, BE-SEC-04, BE-SEC-06, BE-CT-01, SCAN-01 |

### CP0.4 — Intake: mock API and manual, plus corrections

**Split by the owner on 2026-11-16 (D-41).** **CP0.4a** (implemented 2026-11-16, awaiting acceptance): API-080, API-082…085, migration `0009_intake` (`intake_run`, `intake_item`, `field_change` + `intake_item_id` foreign keys), manual API intake with preview, validation, idempotency, holds and portal integration; tests BE-ING-02, -03, -04, -06, -08, -09 (ILP without risk; a source-vs-existing mismatch cannot occur for a new sale), -10, BE-SEC-02 (intake). **CP0.4b** (not started): mock upstream ASGI app and import runs (API-081, API-090…092), corrections (API-086, writes `field_change`), frontend Data Intake screen and Admin Integrations, import scheduling; tests BE-ING-01, -05, -07, FE-01 (Data Intake), E2E-11, E2E-12, E2E-19. The original table below is the combined scope.

| Item | Content |
|---|---|
| Repos | backend, frontend (Data Intake screen) |
| Depends on | CP0.3 accepted; "IMPLEMENT CP0.4" |
| Requirements | ING-001…004, POL-007, PARTY-004 (intake eligibility), RISK-005 (intake preview), GOV-001 (intake guard), ADMIN-002 (corrections and intake history) |
| Deliverables | `intake_run`, `intake_item` and `field_change` tables (Build = CP0.4); mock upstream ASGI app with fixtures (API-090…092); connector protocol; import runs (API-080…083); manual preview and commit (API-084, API-085); corrections (API-086); holds on intake-created cases; frontend Data Intake screen and Admin Integrations |
| Acceptance tests | BE-ING-01…10, BE-SEC-02 (intake rows), FE-01 (Data Intake), SCAN-01, SCAN-02 |

### CP0.5 — Stage 0 screens on real APIs

| Item | Content |
|---|---|
| Repos | frontend |
| Depends on | CP0.4 accepted (OpenAPI pinned at the CP0.4 checksum); "IMPLEMENT CP0.5" |
| Requirements | APP-001, APP-003, APP-004, CASE-001, POL-004, RISK-001, SCR-001…004, SEARCH-002, SEARCH-004, SEARCH-007, SUR-001, IAM-008 (UI), IAM-010 (UI), ADMIN-001 (UI), REG-001, REG-002 (UI) |
| Deliverables | Every screen in S0_SCREEN_SPEC §2 with five states, stage-disabled controls and seeded-evidence labels; `docs/design/DEVIATIONS.md` (DV-01…DV-10) |
| Acceptance tests | FE-01, FE-03, FE-04, SCAN-02, plus a preview run of E2E-01…19 against the local stack (recorded but not yet the gate) |

### CP0.6 — Integrated verification and Stage 0 acceptance record

| Item | Content |
|---|---|
| Repos | frontend (Playwright suite), specs (`S0.md`) |
| Depends on | CP0.1A, CP0.1B-1…3 and CP0.2–CP0.5 accepted; "IMPLEMENT CP0.6" |
| Deliverables | Playwright E2E-01…19 against the real FastAPI, PostgreSQL and mock upstream; a local gate procedure run **twice, each on a freshly reset `call360_test` schema** (the gate backend runs with the test configuration; `call360` is never reset); `S0.md` completed with base SHAs or commit SHAs, file manifests, OpenAPI SHA-256, Alembic head, seed version, audit chain-head digest, test outputs and residual risks; ASVS matrix completed to requirement level by the security reviewer |
| Acceptance | All E2E and backend suites pass in both runs; secret scans clean. `S0.md` stays **NOT_ACCEPTED** until the named approvers sign |

## 3. Dependency graph

```text
CP0.0 ──► CP0.1A ──► CP0.1B-1 ──► CP0.2 ──► CP0.1B-2 ──► CP0.3 ──► CP0.4 ──► CP0.5 ──► CP0.1B-3* ──► CP0.6
            (shell, login, Users/Audit)                              (Data Intake UI in CP0.4)
* CP0.1B-3 may run at any point after CP0.1A; it must be accepted before CP0.6.
```

Strictly sequential. No two checkpoints or packages are implemented together, and each is accepted before the next starts.

## 4. Local verification procedure (per checkpoint)

1. `python3 Call360-specs/scripts/validate_specs.py` → PASS.
2. Backend:
   - `make lint typecheck test`;
   - from CP0.1A: `make openapi contract-check audit-verify`; `make test` runs against `call360_test` through the test role only;
   - from CP0.2: `make test-seed`, which resets **only** `call360_test` (guarded), then migrates and seeds twice, comparing digests. The development schema `call360` is migrated and seeded by the developer with `make migrate seed` and is never reset by automated commands.
3. Frontend: `npm run lint typecheck test api:check build`.
4. Secret scan: run the scanner over every working tree, including untracked files, and over `dist/`.
5. From CP0.5: `npm run e2e` against the running stack.
6. Evidence:
   - `git -C <repo> rev-parse HEAD` and `python3 Call360-specs/scripts/evidence_manifest.py <repo>` for each affected repository;
   - command outputs saved under `Call360-specs/docs/acceptance/evidence/<CP>/`, which is synthetic and contains no secrets.

## 5. Mapping from the execution plan's S0 checkpoint names (C-28)

| Execution plan §C | Execution plan §B0 (extended) | This plan |
|---|---|---|
| CP0.1 Contracts & schema | (1) identity/security skeleton + DB/migrations; (2) policy-sale-party records; (3) SBQ risk inputs | CP0.0 (contracts), CP0.1A (identity and DB) and CP0.1B (administration and configuration), CP0.2 (domain and risk records) |
| CP0.2 API vertical slices | (5) secured search | CP0.3 |
| — | (4) mock API / manual intake | CP0.4 |
| CP0.3 Premium UI | (6) premium UI on the real backend | CP0.5 (shell in CP0.1A) |
| CP0.4 E2E & polish | (7) integration, authorization and audit testing; acceptance | CP0.6 |
