# CP0.2 — Business domain schema and deterministic synthetic seed: acceptance checklist

**Checkpoint status:** **ACCEPTED** 2026-11-15 by the project owner for local synthetic-data development. Deployed to development and verified (2026-11-15). Test-schema implementation verified and accepted. Development schema `call360` migrated to `0007_governed_values` and seeded with S0-SEED-1 on owner authorisation; password rotation explicitly deferred (RR-12). Password rotation remains deferred (RR-12); no real customer data is authorised.
**Scope source:** `docs/plans/S0_IMPLEMENTATION_PLAN.md` (CP0.2).
**Design references:**
- `S0_DATA_MODEL.md` §2.1 (code-list references), §3 (enums), §4.2–§4.5 (tables), §4.6 (migration assignment), §5 (INV-01…14), §6 (seed, digest, governed values, volumes, golden fixtures)
- `ADR-0005` §3–4 (write-once records, transitions, historical pin validity)
- `ADR-0008` §1, §2, §4, §6 (persisted risk and assignment, holds, seeded evidence, synthetic-only policy)
- `S0_IDENTITY_ACCESS_DESIGN.md` §8 (governed lists, callable roles) and §10 (data-protection keys)
- `S0_TEST_MATRIX.md` (BE-DATA-01…13, BE-API-02, SCAN-01)

**Requirements:** CASE-001, CASE-002, SUR-001, PARTY-001…004 (data), POL-001…003, POL-005, POL-006, RISK-001…004, RISK-006, SCR-001, SCR-002, SCR-005, ING-003, REG-001, REG-002, GOV-001 (data), APP-003 (data). No requirement ID, BRD text or register row is changed.

## 1. Decisions recorded (2026-11-15)

The owner approved the CP0.2 architectural direction and authorised specification alignment only. The decisions below refine the approved model; none weakens an approved requirement.

| Ref | Decision | Applied in |
|---|---|---|
| D-29 | Scope. Build exactly the 34 CP0.2 tables (party, policy and sale 8; SBQ risk 3; scripts and regulatory references 12; cases, attempts and evidence 11). `script_assignment_rule_version` is kept for historical traceability. The four deferred tables stay design-only. Migrations `0003`…`0007` are the implementation design; none is authorised to run yet | S0_DATA_MODEL §4.6; plan CP0.2 |
| D-30 | G-1 code references. Market codes are stable text identifiers validated against the market code set. Governed business decisions store the code **and** its code-list version; a composite FK plus a list-membership trigger prevents a code from an unknown value, the wrong list or a non-`ACTIVE` version at insert | S0_DATA_MODEL §2, §2.1, INV-12 |
| D-31 | G-2 supersession. Only `PROVISIONAL → FINAL` and `→ SUPERSEDED` linked to a successor (`supersedes_id`) in the same transaction; historical assessments stay immutable | S0_DATA_MODEL §4.3, INV-13; ADR-0005 §3 |
| D-32 | G-3 historical validity. Session pins are validated against the script version's publication and effective interval at session start; a later `SUPERSEDED` or `WITHDRAWN` status never invalidates a historically valid session. `effective_to` may be set once | S0_DATA_MODEL §4.4, INV-09; ADR-0005 §3–4 |
| D-33 | G-4 digest. The seed digest covers canonical business fields and stable comparison values and excludes randomised ciphertext and operational timestamps. Keyed values make the digest key-dependent, which is documented | S0_DATA_MODEL §6; BE-DATA-02 |
| D-34 | G-5 keys. Separate AES-256-GCM encryption and HMAC-SHA-256 secrets. Generation and installation are authorised only by a later explicit `IMPLEMENT CP0.2`; never printed or committed | S0_IDENTITY_ACCESS_DESIGN §10; THREAT_MODEL RR-02 |
| D-35 | G-6. Question revisions are immutable from insert; corrections create new revisions | S0_DATA_MODEL §4.4; ADR-0005 §3 |
| D-36 | Governed version-1 values approved as **development fixtures, not AIA-approved business rules**: risk bands, risk-factor categories (no numeric thresholds), hold, closure and cancellation reasons, materiality, SLA exemption, callable party roles. A role alone never establishes verified authority or consent; an `AUTHORIZED_CONTACT` is eligible only with recorded, valid authorisation evidence | S0_DATA_MODEL §4.2, §4.5, §6.1, INV-14; S0_IDENTITY_ACCESS_DESIGN §8 |
| D-37 | Synthetic contact data. Non-dialable `SYN-TEL-<market>-NNNNNN` identifiers and `example.invalid` addresses with synthetic provenance; no E.164 number and no real telecommunications destination. A later need for E.164 shapes requires verified reserved test ranges or an approved test-only mechanism with outbound calling disabled | S0_DATA_MODEL §6.1; ADR-0008 §6 |
| D-38 | Seed `S0-SEED-1` with exact volumes (attempt distribution sums to 400 over 250 cases), the twelve golden fixtures (`CB-2026-10482` state `AWAITING_REVIEW`), minimal synthetic enum value sets, and BE-DATA-13 for governed-code integrity | S0_DATA_MODEL §3, §6.2; S0_TEST_MATRIX |
| D-39 | Singapore-only Stage 0 scope (owner, 2026-11-15, at CP0.2 acceptance). All business functionality is Singapore-only. `market_code` is retained in the schema for extensibility. Effective scope = mapped markets ∩ **enabled markets `{SG}`**, so every principal, ADMIN included, sees only `SG` records; `MY` synthetic fixtures stay in the database and are never exposed (list, count, facet, search suggestion or by-ID lookup → `404` + `ACCESS.DENIED_OBJECT`). No multi-country market-permission administration is built in S0. The master BRD and register are unchanged. | S0_IDENTITY_ACCESS_DESIGN §5; ADR-0004 §4; S0_IMPLEMENTATION_PLAN CP0.1B-2; S0_TEST_MATRIX BE-SEC-02; S0_DATA_MODEL §6.2 |

## 2. Scope

| Kind | CP0.2 |
|---|---|
| Tables (34) | See S0_DATA_MODEL §4.6 migration assignment: `0003` (8), `0004` (3), `0005` (12), `0006` (11); `0007` adds governed reference data only |
| Endpoints | None. OpenAPI must remain `c71599f73f6bc54dae120e89b6728a41324343bc384726efc9f62a92eaad83a0` |
| Routes | None |
| Schemas | `call360_test` through the guarded harness. Development schema `call360` only after a separate explicit approval within `IMPLEMENT CP0.2` |
| Out of scope | CP0.1B-2 market scope, CP0.1B-3, CP0.3 read APIs, CP0.4 intake, recordings, transcripts, review decisions, voice, the four deferred tables |

## 3. Acceptance criteria

| ID | Criterion | Tests | Result |
|---|---|---|---|
| AC-0.2-01 | Migrations `0003`…`0007` add exactly the 34 approved tables (54 in total at the CP0.2 head); none of the four deferred tables exists; each revision downgrades and re-upgrades; CP0.1A and CP0.1B-1 data are preserved | BE-DATA-01 | PASS — step-down 0007→0002 and step-up with the exact table set at every revision; principals, audit events and code values identical; deferred tables absent; 0007 downgrade refuses while CP0.2 data exists |
| AC-0.2-02 | Two seeds on a freshly reset `call360_test`, with the same keys, give identical content digests (D-33) | BE-DATA-02 | PASS — identical digests across two fresh seeds (`make test-seed`); re-run inserts nothing; digest changes with a different HMAC key (documented key dependence); tampered data is refused |
| AC-0.2-03 | Exact volumes and coverage of S0_DATA_MODEL §6.2, including all 12 golden fixtures | BE-DATA-03, BE-DATA-07 | PASS — 230 / 250 / 250 / 320 / 24 / 400 / 80 / 80 / 24 / 290 / 5; attempts 0×10, 1×135, 2×60, 3×35, 4×10; all 10 states, 6 hold reasons, 5 outcome categories; 12 golden fixtures asserted individually; 20 multi-sale policies with distinct cases |
| AC-0.2-04 | Relationship invariants hold: case → sale → policy → role → party; attempts and sessions; multi-sale policies; contact eligibility and authorisation evidence (INV-01…03, INV-14) | BE-DATA-03, BE-DATA-07 | PASS — DB triggers reject a session on a non-connected attempt, a contacted party outside the policy and an ineligible selection; seed has evidenced and unevidenced authorised contacts, 25+ joint-owner cases |
| AC-0.2-05 | Immutability: snapshots, assignments, published script content, question revisions, pins and contact snapshots reject UPDATE and DELETE; only D-31 and D-32 transitions pass; historical pin validity (INV-04, INV-05, INV-09, INV-13) | BE-DATA-04, BE-DATA-08, BE-DATA-11 | PASS — every write-once table rejects UPDATE/DELETE (SQLSTATE 42501); superseded/withdrawn versions valid inside their interval, drafts and out-of-interval pins rejected; successor-less supersession rejected, including at commit (deferred check); 15 contact changes leave attempt snapshots intact; factor hashes reproduce |
| AC-0.2-06 | Case holds and cancellation rules: a blocking hold prevents `READY`/`IN_PROGRESS`; placement and release write `case_event` and audit events; cancellation fields only on `CANCELLED`, with server-set `cancelled_recorded_at` (INV-06) | BE-DATA-09, BE-DATA-03 | PASS — `has_blocking_hold` derived by trigger and enforced by CHECK; holds placed/released once, never deleted; each placement/release has an audit event and a case event; cancellation fields only on CANCELLED and recorded once; SLA-EX-001 fixtures 10494 (exempt) / 10495 / 10496 (not exempt) verified. `cancelled_recorded_at` is set-once in the database; "server-set" is enforced by the absence of any write API (see §4.1 note 6) |
| AC-0.2-07 | The three risk concepts are structurally separate; provenance is NOT NULL on all **P** tables (INV-07, INV-08) | BE-DATA-05, BE-DATA-06, BE-API-02 | PASS — `kind = CALLBACK_SELECTION` CHECK; suitability only in snapshot facts; finding severity its own enum; provenance NOT NULL on all 31 **P** tables |
| AC-0.2-08 | Governed-code integrity: correct list and version, exact §6.1 version-1 values, market codes validated (INV-12) | BE-DATA-13 | PASS — unknown code (FK), wrong list and non-ACTIVE version (trigger) rejected; pinned codes survive a later activation; unknown market codes rejected; nine lists hold exactly the §6.1 values |
| AC-0.2-09 | Data protection and synthetic-only: names and contact values encrypted with separate keys, HMAC exact-match tokens, masking; contact values match the non-dialable patterns; readiness fails on a non-synthetic row; no secret in any working tree (INV-10) | BE-API-02, BE-DATA-10, SCAN-01 | PASS — AES-256-GCM with row-bound AAD and HMAC-SHA-256 with separate keys; every contact decrypts to a `SYN-TEL-…` or `example.invalid` value (no E.164); HMAC lookup works; `/health/ready` returns 503 with a non-synthetic row; secret scans clean, self-test 13 formats × 50 including both new keys |
| AC-0.2-10 | Outcome derivation per S0_KPI_DEFINITIONS §1: every case has one category; no `VERIFIED_COMPLIANT` case lacks satisfied mandatory controls; `VERIFIED_CONTROL_EVIDENCE_INCOMPLETE` = 0; expected-answer policies stored so YES is not auto-compliant | BE-DATA-03, BE-DATA-12 | PASS — 30 VERIFIED_COMPLIANT (all controls satisfied, e.g. 10497), 8 VERIFIED_WITH_FINDINGS, guard count 0; no ILP case is VERIFIED (mandatory narrative cannot be satisfied in S0); the seed itself refuses to finish if the guard is non-zero |
| AC-0.2-11 | Regression and isolation: all CP0.1A and CP0.1B-1 tests pass; tests touch only `call360_test`; OpenAPI unchanged; specs validator passes | BE-DATA-14, BE-CT-01, SPEC-01 | PASS — 167 backend tests (98 prior, 3 B-1 assertions updated for D-26, 69 new); frontend 30 unit + 14 Playwright (E2E-20 with governed values present); OpenAPI `c71599f7…` unchanged and `api:check` OK; validator PASS; development schema verified untouched |

## 4. Evidence

All outputs are in `docs/acceptance/evidence/CP0.2/` from a single run on 2026-11-15; every check exited 0.

| Check | File | Result |
|---|---|---|
| Backend tests | `backend_tests.txt` | **167 passed** |
| Seed determinism (`make test-seed`) | `backend_seed_determinism.txt` | 3 passed (two fresh seeds, identical digest) |
| Lint / format / mypy `--strict` | `backend_lint.txt`, `backend_typecheck.txt` | Clean |
| OpenAPI contract | `backend_contract.txt` | Unchanged `c71599f73f6bc54dae120e89b6728a41324343bc384726efc9f62a92eaad83a0` |
| Secret scans + self-test | `backend_secret_scan.txt` | Repo clean; 13 formats × 50 detected; 0 false positives |
| Seed digest (test schema, test keys) | `backend_seed_digest_test_schema.txt` | `05ce50c78bb08bcfa172e221d9f16974011f0ede91e7a148d4d0669193353529`; key ids recorded in the `SEED.MANIFEST` audit event, never key material |
| Test audit chain | `backend_audit_verify_test.txt` | Verified |
| Frontend `api:check`, unit, Playwright | `frontend_api_check.txt`, `frontend_unit.txt`, `frontend_e2e.txt` | OK; 30 passed; 14 passed |
| Specs validator | `specs_validator.txt` | PASS |
| **Development schema untouched** (read-only) | `dev_schema_untouched_readonly.txt` | `call360` at `0002_config_foundation`, 21 tables, no CP0.2 tables, governed lists empty, 2 principals, audit chain head `289d4029…` identical to the CP0.1B-1 evidence |

**Manifest:** backend base `08c139e` + manifest `d6521aa3…` (37 files: 23 new, 14 modified; `manifest_backend.txt`). Frontend unchanged (base `9f86ce0`). Migration head (test schema) `0007_governed_values`.

**Keys (D-34):** `PII_ENCRYPTION_KEY` and `PII_HMAC_KEY` were generated with `os.urandom(32)` by `scripts/make_data_keys.py` into the gitignored `.env.test` only (values never shown). The script refuses the development `.env` without `--allow-development`. Existing authentication credentials were not regenerated.

### 4.00 Development-schema deployment (2026-11-15)

Authorised as "CP0.2 development-schema deployment", without credential rotation. The runbook was followed except step 4, which was skipped on owner instruction. Evidence: `docs/acceptance/evidence/CP0.2/dev-deployment/`.

| Step | Result |
|---|---|
| Preflight (read-only) | `local / call360 / Call360_db`; head `0002`; 21 tables; 2 principals; audit OK (5 events, head `289d4029…`) |
| Backup | `~/call360-backups/pre_cp02_20261115_173043/` (outside the repositories, mode 700): schema dump (21 table-data entries), `env`, `env.local`, `secrets`, `env.post_keys`, `SHA256SUMS` (verified) |
| Password rotation | **Skipped (owner instruction).** Existing password, connection settings, JWT keys, pepper, CSRF secret and accounts unchanged (`.env` byte-identical to the backup before keys were added). Recorded as RR-12 |
| Data-protection keys | Generated once into the development `.env` only (values never shown) and copied to `env.post_keys`. Key ids `c37d3b1fd02c` / `1ed3fddc7711` (identifiers, not key material) |
| Migrations | `make migrate`: `0002` → `0007_governed_values`, no errors |
| Seed | `make seed CONFIRM=call360`: digest `2ead19f36e09bdf360f193d3d6140f7aa27b6520e599d800e01bd5edfbcfc3de`. The second run reported "Already seeded (no changes)". The digest differs from the test digest by design (D-33, different HMAC key) |
| Validation (`dev_validation.txt`, read-only) | **31/31 PASS.** 54 application tables; 230 policies, 250 sales and cases, 320 parties, 24 FSCs, 400 attempts (0×10, 1×135, 2×60, 3×35, 4×10), 80 sessions and runs, 24 findings, 290 risk assessments, 5 script versions; 12 golden fixtures (10482 sequence, MISMATCH 10 vs 5 and HIGH finding; holds; MY; cancellations; 10497 compliant); outcomes 30 compliant / 8 with findings / 37 not verified / 6 cancelled / 169 open, guard 0; key ids and digest match the seed manifest; 2 principals, market v1 (SG, MY), 4 flags off, 9 governed lists v1 |
| Audit chain | Earlier 5 events unchanged (5th event hash `289d4029…`). Deployment appended 9 activations, 12 hold placements, 2 releases and 1 manifest (29 events). Login checks appended 6 more. **Chain verified: 35 events**, head `fc4f4c8b…` |
| Application | Backend and frontend dev servers restarted; `/health/live` and `/health/ready` OK; frontend HTTP 200 |
| Accounts (`dev_login_and_readiness.txt`) | `dev.admin`: login 200, role ADMIN, admin users and code lists 200 (9 governed lists at v1). `dev.user`: login 200, role USER, admin endpoints 403 |
| Regression | Backend 177 passed; ruff, format, mypy clean; OpenAPI unchanged `c71599f7…`; frontend lint, typecheck, 31 unit, `api:check`, build; Playwright 14/14; secret scans clean in both repos and the bundle; specs validator PASS |
| Code baseline | Unchanged since the UI-fix run: backend `08c139e` + `7442f098…`, frontend `9f86ce0` + `c0fbcc79…` |

### 4.0 Targeted corrections run (2026-11-15)

The owner accepted the test-schema results and authorised two corrections (§4.1 notes 1 and 2, now resolved). Re-run evidence is in `docs/acceptance/evidence/CP0.2/corrections/`; the original evidence above is preserved.

| Check | Result |
|---|---|
| Backend tests | **177 passed** (10 new: key enforcement and governed audit) |
| Seed determinism, digest | 3 passed; digest **unchanged** `05ce50c7…` (audit is outside the content digest) |
| Lint, mypy `--strict`, OpenAPI | Clean; OpenAPI unchanged `c71599f7…`; `api:check` OK |
| Secret scans, validator | Clean (13 formats × 50); PASS |
| Test audit chain | OK, 24 events after a fresh seed (9 governed activations, 12 hold placements, 2 releases, 1 manifest) |
| Development schema | Untouched: `0002`, 21 tables, audit head `289d4029…` |
| Frontend unit | 30 passed |
| **Frontend Playwright** | **FAIL: 12 passed, 2 failed** (`frontend_e2e.txt`) |
| Manifest | backend base `08c139e` + `7442f098…` (38 files); frontend unchanged |

**Open defect (RESOLVED in §4.0b).** FE-04 / E2E-17 layout checks fail at 1280 px (overflow 490 px) and 1440 px (330 px) on Administration → Audit. The audit table (CP0.1A frontend) cannot wrap long unbreakable monospace values. The new governed activation events (`CONFIG.CODE_LIST_VERSION_ACTIVATED`, actor `Service: migration:0007_governed_values`) now appear on its first page, so the Reason and Details columns run off-screen (`test-results/screens/audit-1280.png`). The same action is already produced by the CP0.1B-1 market-label flow, so the defect predates CP0.2. CP0.2 data only exposes it. It is not masked in the backend. **Proposed fix (frontend, needs authorisation):** let the audit-table cells wrap (`overflow-wrap: anywhere` on the action, actor and entity cells) or put the table in a horizontally scrollable region, then re-run FE-04/E2E-17. The development deployment would show the same overflow until fixed.

### 4.0b Audit-table UI fix run (2026-11-15) — open defect RESOLVED

Authorised: "AUDIT-TABLE FRONTEND FIX ONLY". Evidence: `docs/acceptance/evidence/CP0.2/ui-fix/`.

**Root cause:**
- The app shell is a flex row (`.app{display:flex}`), and `.main` kept the default `min-width:auto`.
- It therefore grew to the min-content width of the mockup's `white-space:nowrap` table.
- As a result the existing `.table-wrap{overflow:auto}` never engaged and the page overflowed.

**Fix (frontend, CSS plus class names only):**
- `.main{min-width:0}` restores containment.
- The audit table's Action, Actor and Entity cells wrap long unbroken values (`overflow-wrap:anywhere`). The Action column has `min-width:22ch`, so common actions stay on one line.
- Reason wraps between 22 and 56ch.
- Details-drawer JSON wraps (`white-space:pre-wrap`).
- Text, accessible names, API, records and payloads are unchanged. Nothing is truncated or hidden; the existing 12-character entity-id abbreviation and the full-detail drawer are unchanged.
- Horizontal scrolling remains only as a fallback.
- A `<wbr>` approach was tried and rejected because it altered accessible names.

**Scanner parity:**
- The frontend `.gitleaks.toml` received the same `ENCRYPTION_KEY|HMAC_KEY` rule as the backend.
- Without it, the shared self-test, which gained the two key formats in CP0.2, detected only 49/50 samples in the frontend repo.

| Check | Result |
|---|---|
| Playwright (real stack, `call360_test`) | **14 passed**, including FE-04/E2E-17 at 1280 and 1440 px |
| Frontend unit | **31 passed** (new `AuditPage.test.tsx`) |
| Frontend lint, typecheck, build | Clean |
| OpenAPI | `api:check` OK and `make contract-check` OK: `c71599f7…` unchanged |
| Secret scans | Frontend repo + bundle clean, self-test 13 × 50; backend clean, 13 × 50 |
| Backend | **177 passed**; ruff, format, mypy clean |
| Specs validator | PASS |
| Development schema | Untouched: `0002`, audit head `289d4029…` |
| Manifests | backend `08c139e` + `7442f098…` (38 files, unchanged since the corrections run); frontend `9f86ce0` + `c0fbcc79…` (4 files: `AuditPage.tsx`, `AuditPage.test.tsx`, `app.css`, `.gitleaks.toml`) |
| Screens | `ui-fix/screens/audit-1280.png`, `audit-1440.png` |

### 4.1 Implementation notes and deviations (for owner review)

1. **Keys — RESOLVED by targeted correction (2026-11-15).** Settings validate the keys whenever present and always require them for tests. Wherever the CP0.2 domain exists in the connected schema, startup refuses (`DataProtectionUnavailable`), `/health/ready` returns 503 and the seed refuses if either key is missing. A pre-CP0.2 schema (development at 0002) still runs without keys. S0_IDENTITY_ACCESS_DESIGN §10 updated. Tests: `test_domain_controls.py` (startup, readiness, seed, pre-CP0.2 schema, settings).
2. **Migration 0007 audit — RESOLVED by targeted correction (2026-11-15).** Each governed activation writes one `CONFIG.CODE_LIST_VERSION_ACTIVATED` event (service actor `migration:0007_governed_values`, version id, reference-data version, reason, values). The bootstrap is idempotent: it writes only when the version's latest lifecycle event is not an activation. The development-only downgrade writes `CONFIG.CODE_LIST_VERSION_REMOVED` first, so a round trip appends removal + re-activation and never duplicates. CP0.1A/B-1 round-trip tests now assert append-only audit (earlier events byte-identical by sequence and hash; only these lifecycle events appended). S0_DATA_MODEL §4.6 and S0_IDENTITY_ACCESS_DESIGN §8 updated. The seed still writes `CASE.HOLD_PLACED` / `CASE.HOLD_RELEASED` and one `SEED.MANIFEST` event.
3. **Session attempt status.** Attempts that carry a session end as `CONNECTED`, matching golden fixture 10482 (`NO_ANSWER → BUSY → CONNECTED`).
4. **Seeded media status.** Seeded sessions use `media_status = NOT_REQUIRED` and `transcript_status = UNAVAILABLE` (no capture exists before S1); the API will derive `NOT_AVAILABLE / NO_CAPTURE_BEFORE_S1` (ADR-0008 §4).
5. **Stricter lifecycle.** Script versions and modules can only be inserted as `DRAFT` and must walk the ADR-0007 lifecycle; a version leaves DRAFT only with a validated manifest and published modules; retiring a published version sets `effective_to`. Answer observations carry a stage-lock CHECK (`transcript_segment_ids` empty) that S1 lifts.
6. **`cancelled_recorded_at`.** The database enforces set-once; "never client-supplied" is enforced by the absence of any write API in CP0.2. CP0.3/CP0.4 write paths must set it from server time.
7. **Downgrade below 0007** refuses while any CP0.2 row exists (development-only safety; removing referenced reference data would orphan history).
8. **Content counts.** 13 question bank items (spec: "about 12"); 2 synthetic placeholder regulatory references (`NOT_REVIEWED`, no real document named); 5 synthetic controls.
9. **Models.** The seed and tests use Core tables reflected from the migrations (single schema source). ORM models arrive with the CP0.3 read APIs.
10. **Readiness.** `/health/ready` now also fails when any business row is non-synthetic (INV-10). A development server still on `0002` reports `not_ready` (migration head mismatch) until the development deployment.
11. **CP0.1B-1 tests.** Three assertions that encoded "governed lists are empty until CP0.2" (D-26) were updated to the version-1 values; all other CP0.1B-1 tests are unchanged and pass.

**Open business items (unchanged):** DEC-008 (closure reasons, marked `pending: DEC-008` on each value), approval of every synthetic governed value before any real use, approver names (C-20).

## 5. Acceptance

| Role | Name | Date | Decision |
|---|---|---|---|
| Project owner | Project owner (name to be recorded, C-20) | 2026-11-15 | **ACCEPTED**: CP0.2 Business Domain Foundation for local synthetic-data development. All implementation and test evidence preserved (`evidence/CP0.2/`, `corrections/`, `ui-fix/`, `dev-deployment/`). Scope decision D-39 (Singapore-only) recorded at acceptance |
