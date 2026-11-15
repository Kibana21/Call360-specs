# CP0.1B-1 — Configuration foundation: acceptance checklist

**Checkpoint status:** **ACCEPTED** 2026-11-15 by the project owner, for local development, after manual review of Administration → Configuration. Implemented and verified 2026-11-15. B-2, B-3 and CP0.2 are not started.
**Scope source:** `docs/plans/S0_IMPLEMENTATION_PLAN.md` (CP0.1B-1).
**Design references:**
- `S0_DATA_MODEL.md` §4.1 (Build = CP0.1B)
- `S0_API_CATALOGUE.md` API-022…025
- `S0_IDENTITY_ACCESS_DESIGN.md` §8
- `S0_SCREEN_SPEC.md` (Administration → Configuration)
- `S0_TEST_MATRIX.md` (BE-CFG-01…03, E2E-20)

**Requirements:** ADMIN-004 and RISK-006 (mechanism), ADMIN-002 (configuration history).

## 1. Decisions recorded (2026-11-15)

| Ref | Decision | Applied in |
|---|---|---|
| D-25 | Explicit list classification, derived from the existing §8 rule ("`config.manage` covers only `market` labels, display lists and feature flags"). `market` is non-governed for labels and display attributes only; its code set is fixed because codes become scopes in B-2. The other nine S0 lists are governed and read-only in S0. **This answers the owner's market-test question:** the E2E market-label version test is valid, and the same test also proves that governed lists and market code changes are denied. No governance rule was weakened | S0_IDENTITY_ACCESS_DESIGN §8; API-023 |
| D-26 | B-1 seeds definitions for all ten S0 lists, plus version-1 values for `market` only (`SG`, `MY`, marked synthetic). Governed business values are seeded in CP0.2. Seed operations are idempotent. No AIA-approved thresholds or classifications are invented | Migration `0002_config_foundation` |
| D-27 | Feature-flag registry. Four flags, all disabled and stage-locked: `voice.browser_sessions` (S1), `scripts.authoring` (S2), `reviews.decisions` (S3), `exports.evidence` (S4). None of the features they name is implemented. A flag can be enabled only when its stage gate ≤ the current stage (S0), so none can be enabled in S0. Tests prove successful toggling with a stage-reached fixture flag created **only in `call360_test`** | S0_DATA_MODEL `feature_flag`; API-025 |
| D-28 | Lifecycle mechanics. API-023 inserts a DRAFT version with its values, then in the same transaction supersedes the current ACTIVE version and activates the new one. Optimistic concurrency uses `based_on_version` (code lists) and `If-Match` row version (flags). Database triggers keep ACTIVE and SUPERSEDED versions, their values and flag history immutable | API-023/025; migration 0002 |

## 2. Scope

| Kind | CP0.1B-1 |
|---|---|
| Tables (5) | `code_list`, `code_list_version`, `code_value`, `feature_flag`, `feature_flag_change` (migration `0002_config_foundation`; schemas `call360` and `call360_test`) |
| Endpoints (4) | API-022 `GET /admin/code-lists`, API-023 `POST /admin/code-lists/{code}/versions`, API-024 `GET /admin/feature-flags`, API-025 `PATCH /admin/feature-flags/{code}` |
| Route | `/admin/config` (Administration → Configuration sub-tab enabled) |
| Out of scope | B-2 market scoping, B-3 administration completion, CP0.2 domain tables and governed values, all flagged features |

## 3. Acceptance criteria

| ID | Criterion | Tests | Result |
|---|---|---|---|
| AC-0.1B1-01 | Migration 0002 adds exactly the 5 tables to both schemas; CP0.1A data preserved; downgrade works; seed idempotent | BE-CFG-03, BE-DATA-01 | PASS — BE-CFG-03 (identity counts identical across downgrade to 0001 and upgrade; seed re-run inserts nothing); BE-DATA-01 (20 tables at head). Development `call360` migrated with identical identity counts and audit-chain digest before and after |
| AC-0.1B1-02 | Version lifecycle DRAFT → ACTIVE → SUPERSEDED; atomic activation; immutable non-draft versions and values; historical values resolvable | BE-CFG-01 | PASS — BE-CFG-01: atomic supersede and activate, a single ACTIVE version per list, historical values via API and `values_of`; database refuses tampering with ACTIVE content, status rollback, deletion and a second ACTIVE |
| AC-0.1B1-03 | Governed lists cannot be versioned (403, audited); market code set is fixed; stale concurrency is rejected | BE-CFG-01, E2E-20 | PASS — all 9 governed lists return 403 and are audited; market add/remove code returns 422; stale `based_on_version` returns 409 (BE-CFG-01, E2E-20) |
| AC-0.1B1-04 | Stage-locked flags cannot be enabled through the API or UI; history is insert-only | BE-CFG-02, E2E-20 | PASS — 4 seeded flags return 422 STAGE_GATED and are audited; the DB CHECK refuses enablement; the UI button is disabled and explained; fixture S0 flag toggles; history is append-only (BE-CFG-02, E2E-20) |
| AC-0.1B1-05 | `config.read` and `config.manage` enforced server-side (USER 403); every change requires a reason and writes an audit event with actor and before/after | BE-CFG-01, BE-CFG-02, BE-SEC-01 | PASS — USER 403 on all four endpoints (BE-CFG-01/02, E2E-20); route inventory covers 14 operations (BE-SEC-01); reason required; audit actor, reason and before/after verified |
| AC-0.1B1-06 | The Configuration screen shows lists, active and historical versions, governed indicators, permitted actions and flags, with loading, empty, error and forbidden states; accessible at 1280 and 1440 px | FE-01, E2E-20, FE-04 | PASS — 5 component tests (FE-01); E2E-20; axe zero serious or critical on the screen and the drawer at 1280 and 1440 px |
| AC-0.1B1-07 | OpenAPI regenerated and pinned; `api:check` passes; all CP0.1A regression tests pass; secret scans clean; validator passes | BE-CT-01, FE-03, SCAN-01/02, SPEC-01 | PASS — OpenAPI `c71599f7…` pinned, `api:check` OK; all CP0.1A tests pass (98 backend, 30 unit, 14 E2E); secret scans and self-test clean; validator PASS |

## 4. Evidence

All outputs are in `docs/acceptance/evidence/CP0.1B-1/`, from a single run on 2026-11-15 in which all 16 checks exited 0.

| Check | Result |
|---|---|
| Backend tests | **98 passed**, including 25 new B-1 tests |
| Frontend unit and component tests | **30 passed**, including 5 new |
| Playwright against the real stack | **14 passed**, including E2E-20 and two Configuration accessibility checks; stable across two consecutive runs |
| Lint (ruff), mypy `--strict`, ESLint, tsc | Clean |
| OpenAPI contract | SHA-256 `c71599f73f6bc54dae120e89b6728a41324343bc384726efc9f62a92eaad83a0` |
| Secret scans | Self-test 11 formats × 50 detected; 0 false positives; repos and bundle clean |
| npm audit | 0 vulnerabilities |
| Development audit chain | Verified (unchanged; tests never touch `call360`) |
| Specs validator | PASS |

**Manifests (uncommitted changes on top of the owner's commits):**
- backend base `cc57961` + manifest `aba0f8ce…` (14 files);
- frontend base `9ee9f3c` + manifest `b4ae8a72…` (11 files).

**Development database (schema `call360`):**
- migrated to `0002_config_foundation`, now 21 tables including `alembic_version`;
- 10 list definitions (1 non-governed, 9 governed);
- `market` v1 ACTIVE, `SG`/`MY` with `{"synthetic": true}`;
- 4 flags, all off and stage-locked;
- identity data and audit chain unchanged.

**Implementation notes:**
- **Idempotent replays:** API-023 relies on `based_on_version` rather than a stored `Idempotency-Key`. A replayed request returns `409 CONFLICT_STALE_VERSION` and never creates a duplicate version.
- **Stage lock in the database:** a CHECK constraint `NOT enabled OR stage_gate <= 'S0'` enforces the lock. Each later stage's migration moves that boundary.
- **Contrast fix:** in-page stage chips now use the DV-11 grey, found by the new accessibility test.
- **Seed wording:** list descriptions are seed text and mention checkpoint names (for example "CP0.1B-2"). This is visible to administrators only.

## 5. Acceptance

| Role | Name | Date | Decision |
|---|---|---|---|
| Project owner | Project owner (name to be recorded, C-20) | 2026-11-15 | **ACCEPTED** for local development: implementation, acceptance evidence, UI and regression results. Evidence and hashes in §4 are preserved unchanged. Working trees re-verified against both manifests on 2026-11-15 before acceptance (all 25 file hashes match). Not yet committed; commit SHAs are recorded once commits are authorised |
