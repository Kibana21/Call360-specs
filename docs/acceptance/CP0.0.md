# CP0.0 — Specification foundation: acceptance record

**Checkpoint status:** **ACCEPTED** by the project owner on 2026-11-15, as the local Call360 development baseline
**Authorisation:** "AUTHORIZE CP0.0 SPEC EDITS" (owner, 2026-11-15). Edits are limited to `Call360-specs`. No application code, database objects, dependency installation, commits or pushes.
**Base revision:** `Call360-specs` `main` @ `17fb5e3`. All changes are uncommitted; the evidence manifest is in `docs/acceptance/evidence/CP0.0/`.
**Unchanged by design:** `docs/spec/01_MASTER_BRD.md`, `docs/spec/03_REQUIREMENTS_REGISTER.csv`, `docs/spec/REQUIREMENT_COUNTS.json` (237 requirement IDs, 55 business tests).

## 1. Owner decisions recorded

| Ref | Decision | Recorded in |
|---|---|---|
| D-1…D-15 | Prior owner decisions of 2026-11-15, for example: D-2 Script Studio / `scripts`; D-4 no risk or assignment engine in S0; D-6 session pins; D-7 access and refresh tokens, revocation, CSRF, RBAC, market scope; D-8 immutability and audit limits; D-9 search and saved views with masking; D-10 synthetic, never presented as real; D-11 GPT-Live S1, Genesys S6; D-12 BRD KPIs; D-13 manual-intake permission for ADMIN; D-14 generated OpenAPI; D-15 mandatory secret scanning and security tests | ADR-0003…0008 |
| C-1 | Follow the approved HTML mockup's navigation structure with canonical specification terminology | ADR-0008 §3; SCREEN_NAMING; EXC-003 |
| C-4 | Lifecycle `DRAFT, SUBMITTED_FOR_REVIEW, APPROVED, SCHEDULED, PUBLISHED, SUPERSEDED, WITHDRAWN`; published versions immutable | ADR-0007; S0_DATA_MODEL §3; EXC-002 |
| C-6 | Secure one-time admin bootstrap and developer-specific credentials; no default passwords or passwordless role switching | ADR-0004; S0_IDENTITY_ACCESS_DESIGN §3 |
| C-12 | Separate, auditable hold; blocking holds prevent a case from becoming callable | ADR-0008 §2; S0_DATA_MODEL `case_hold`; EXT-001 |
| C-23 | Uncommitted evidence = base Git SHA + deterministic manifest of changed and new file hashes | ADR-0003 §6; `scripts/evidence_manifest.py` |
| C-26 | Master BRD not rewritten; Script Studio recorded as an explicit exception; no silent override of other requirements | ADR-0007; `APPROVED_EXCEPTIONS.md` |
| K-1 | Eligible cases defined separately for each KPI, including held and cancelled handling | S0_KPI_DEFINITIONS §1–§2 |
| K-2 | HIGH and CRITICAL provisionally material, with configurable business-approved exceptions | S0_KPI_DEFINITIONS §1 (`finding_materiality_policy`) |
| K-3 | Closed-unverified and cancelled are not compliant verification outcomes; SLA exemptions require an explicit approved rule | S0_KPI_DEFINITIONS §1, KPI-04, KPI-10 |
| K-4 | `due_at` for SLA cohorts; `created_at` for intake cohorts | S0_KPI_DEFINITIONS §1, KPI-13 |
| D-16 | Use the existing database `Call360_db` and the existing login `Call360_db_user` for everything (app, migrations, seed, tests); keep it simple | ADR-0003 §1; ADR-0005 §1–2; S0_IMPLEMENTATION_PLAN; THREAT_MODEL_S0 RR-11 |
| D-17 | Case outcomes `VERIFIED_COMPLIANT`, `VERIFIED_WITH_FINDINGS`, `NOT_VERIFIED`, `CANCELLED`, `OPEN`. SLA breach is a separate timeliness indicator. Verified-compliant requires all applicable mandatory verification controls to be satisfied, not merely the absence of findings. Cancelled or unverified never implies a non-compliant sale | S0_KPI_DEFINITIONS §1–§3 (KPI-04, KPI-10, KPI-15…18) |
| D-18 | SLA exemption `SLA-EX-001` for cancellations recorded before `due_at` with an approved reason and recorded authorisation. Invalid, unauthorised or retrospective cancellations are not exempt. Cancelled cases stay visible. Holds do not pause the SLA clock | S0_KPI_DEFINITIONS §2; S0_DATA_MODEL `callback_case` cancellation fields; seed fixtures `CB-2026-10494…10498` |
| D-19 | Canonical model keeps 63 tables, but Stage 0 physically builds 59. `transcript_segment` deferred to S1 and `review_decision` to S3 (`media_asset` S1 and `risk_override` S2 already deferred). `login_attempt` and `feature_flag_change` retained. Checkpoint headings corrected | S0_DATA_MODEL §4 Build column, §4.6; S0_IMPLEMENTATION_PLAN; ADR-0008 §4; API-045; S0_SCREEN_SPEC |
| D-20 | API catalogue and route specification kept as approved; no API consolidation now; future-stage endpoints documentation-only. ASVS matrix stated to be a design and verification plan, not evidence of certification; security parameters provisional; approver names may remain TBD for local development; no GitHub or CI/CD | S0_API_CATALOGUE §9; S0_IMPLEMENTATION_PLAN §1; ASVS_S0_CONTROL_MATRIX header |
| Correction 1 | Do not hard-code `is_synthetic=true` as a permanent DB constraint; use provenance plus development-environment intake restrictions | ADR-0003 §4; ADR-0008 §6; S0_DATA_MODEL §2 |
| Correction 2 | Keep the design compatible with real policy data, Okta/AD and Genesys | S0_DATA_MODEL §1 (reserved enum values); ADR-0004; ADR-0008 §5 |
| Correction 3 | Validator recognises approved exceptions rather than failing on deliberately unchanged source documents | `scripts/validate_specs.py`; `APPROVED_EXCEPTIONS.md` §2 |

## 2. Contradiction register (C-1…C-31)

**Status values:**
- `RESOLVED-OWNER`: settled by an owner decision.
- `RESOLVED-ENG`: engineering resolution recorded in an ADR or spec, acknowledged by the owner at CP0.0 acceptance.
- `DEFERRED`: carries an owner and a target.
- `MOOT`: no longer applicable.

| # | Contradiction | Resolution | Reference | Status |
|---|---|---|---|---|
| C-1 | Four different navigation label sets (BRD §4.1, SEARCH doc, SCREEN_NAMING, mockup) | Mockup structure and order, canonical labels; Voice Studio and Campaigns added | ADR-0008 §3, EXC-003 | RESOLVED-OWNER |
| C-2 | Survey Studio / `/surveys` / `/api/v1/surveys` vs Script Studio / `/scripts` | Script Studio; `scripts` API and domain; redirects; `SUR-*` IDs unchanged | ADR-0007, EXC-001 | RESOLVED-OWNER |
| C-3 | "Sale Detail" required at sign-off, but no route | Sale Context workspace at `/policies/:policyId?sale=<id>`, validated to belong to the policy; `GET /sales/{id}` | SCREEN_NAMING; S0_SCREEN_SPEC | RESOLVED-ENG |
| C-4 | Four script lifecycle lists | Approved list; validation is a draft attribute; legacy-state mapping | ADR-0007, EXC-002 | RESOLVED-OWNER |
| C-5 | Identity table and permission naming differs between grain doc and security doc | Security-doc entities; dotted permission codes with alias column | S0_DATA_MODEL §4.1; S0_IDENTITY_ACCESS_DESIGN §6 | RESOLVED-ENG |
| C-6 | Seeded demo accounts (IAM-002) vs "no default password" vs mockup role buttons | Bootstrap plus developer-specific accounts; no role switching | ADR-0004 | RESOLVED-OWNER |
| C-7 | Access/refresh tokens vs BFF session preference | Hybrid: JWT + rotating refresh in HttpOnly cookies + authoritative server session | ADR-0004 | RESOLVED-OWNER |
| C-8 | S0 display requirements vs S2 engines; intake "preview script routing" | No engines; stored records only; intake cases held; preview states routing not evaluated | ADR-0008 §1 | RESOLVED-OWNER |
| C-9 | Market scope needed in S0 but staged S5 | Market scope in S0 (SG, MY); S5 extends | ADR-0004 | RESOLVED-OWNER |
| C-10 | `NOT_AVAILABLE` required, but not in BRD media enum | API availability object; BRD enums unchanged | ADR-0006, EXT-002 | RESOLVED-ENG |
| C-11 | Seeded sessions, answers and findings vs no voice or evaluation in S0 | `record_origin=SYNTHETIC_SEED` with persistent labels | ADR-0008 §4 | RESOLVED-OWNER |
| C-12 | Case lifecycle lacks hold states | Separate auditable `case_hold`; blocking holds; DB check | ADR-0008 §2, EXT-001 | RESOLVED-OWNER |
| C-13 | KPI definitions differ across sources | BRD §10 with per-KPI rules K-1…K-4 | S0_KPI_DEFINITIONS, EXT-003 | RESOLVED-OWNER |
| C-14 | Saved views P1 (APP-006) vs P0 (SEARCH-004) | Implemented fully | S0_TEST_MATRIX | RESOLVED-OWNER |
| C-15 | No permission for manual intake | `intake.manual.submit`, `intake.mock.sync`, `intake.read` for ADMIN | S0_IDENTITY_ACCESS_DESIGN §6 | RESOLVED-OWNER |
| C-16 | Health paths differ | Unversioned public `/health/*`; detail at `/api/v1/admin/system-health` | ADR-0006; API_CONTRACT_POLICY | RESOLVED-ENG |
| C-17 | Mockup numeric risk score vs "no score without approved rule" | Score only if stored with its synthetic rule set | ADR-0008 §1; S0_SCREEN_SPEC DV-03 | RESOLVED-OWNER |
| C-18 | Mockup actions imply finished features | Stage-disabled controls; seeded-outcome wording; deviations DV-01…10 | S0_SCREEN_SPEC §4 | RESOLVED-OWNER |
| C-19 | Editorial: execution plan header says v0.2; CHANGELOG ordering; folder-name case | Header updated; CHANGELOG reordered with v0.4-draft entry; parent folder name documented as not significant | 02 execution plan; CHANGELOG; MULTI_REPO | RESOLVED-ENG |
| C-20 | Register `owner`/`test_id` empty; S0 approvers unnamed | Traceability in S0_TEST_MATRIX (see C-27). **Approver names still required** | S0.md approvals table | DEFERRED (owner; may remain TBD during local development, D-20; needed before final S0 acceptance) |
| C-21 | `LOCAL_BUILD_PLAN.md` conflicted with the specs | The file is no longer present in the repository; nothing carried forward | S0_IMPLEMENTATION_PLAN header | MOOT |
| C-22 | Execution plan, MULTI_REPO §4–5 and S0_TEMPLATE require CI, branches, PRs and "CI job URLs" | Local-development-mode notes; CI duties become local commands with captured output; checks themselves unchanged | MULTI_REPO §9; execution plan overlay; S0_TEMPLATE | RESOLVED-OWNER (workspace `CLAUDE.md` §10) |
| C-23 | Stage evidence needs commit SHAs, but commits are not authorised | Base SHA + deterministic manifest | ADR-0003 §6 | RESOLVED-OWNER |
| C-24 | Workspace `CLAUDE.md` and `Call360-frontend/CLAUDE.md` still say "Survey Studio" | Outside the authorised repository; ADR-0007 takes precedence meanwhile | ADR-0007 consequences | DEFERRED (owner; separate authorisation for those files) |
| C-25 | Execution plan defaults list SSE/WebSocket and TaskIQ; S0 needs neither | Not in S0; first needed S1/S4 | ADR-0003 §1 | RESOLVED-ENG |
| C-26 | BRD keeps "Survey Studio" and the old lifecycle | BRD unchanged; explicit exceptions EXC-001/002 | APPROVED_EXCEPTIONS | RESOLVED-OWNER |
| C-27 | Test traceability would require editing the register's `test_id` column | Register untouched; S0_TEST_MATRIX is the traceability source, validator-enforced | S0_TEST_MATRIX | RESOLVED-ENG |
| C-28 | Execution plan §C names S0 checkpoints CP0.1–CP0.4, and §B0 lists seven different checkpoints, vs CP0.0–CP0.6 | S0_IMPLEMENTATION_PLAN supersedes numbering only; mapping table §5 | S0_IMPLEMENTATION_PLAN §5 | RESOLVED-ENG |
| C-29 | Intake doc and earlier proposal implied a permanent `is_synthetic=true` constraint | Owner correction: provenance plus environment data policy; no permanent CHECK | ADR-0008 §6 | RESOLVED-OWNER |
| C-30 | BRD §7.2 "suggested" table names (`customers`, `policy_snapshots`, `surveys`, `compliance_findings`) vs grain doc names | Grain doc (binding grain contract, BRD §4.4) governs; BRD §7.2 is explicitly "suggested", so no exception is needed | S0_DATA_MODEL header | RESOLVED-ENG |
| C-31 | API path styles differ: intake doc (`/intake/import-runs`, `/policies/{id}/sales`) vs earlier proposal (`/intake/mock-sync`, `/sale-events`) | Intake doc paths adopted | S0_API_CATALOGUE §4, §7 | RESOLVED-ENG |
| C-32 | KPI definitions treated cancelled cases as non-compliant and folded them into the verification-rate denominator, conflicting with the owner clarification that cancelled or unverified callbacks are not non-compliant sales | Outcome model with five categories; SLA as a separate indicator; cancelled excluded from verification denominators; `SLA-EX-001` | S0_KPI_DEFINITIONS | RESOLVED-OWNER |
| C-33 | S0_DATA_MODEL section headings assigned `saved_view` to CP0.1 and the intake tables and `field_change` to CP0.2, contradicting the implementation plan | Per-table Build column; summary §4.6 | S0_DATA_MODEL §4 | RESOLVED-OWNER |

**Summary:** RESOLVED-OWNER 20 · RESOLVED-ENG 10 · DEFERRED 2 (C-20, C-24) · MOOT 1 (C-21) · unclassified 0.

**Business assumptions:** DEC-001…DEC-028 (BRD §14) remain `ASSUMPTION` or `DEFERRED_FOR_OWNER`, as the BRD instructs. None blocks S0.

**Security defaults S-2…S-14** are recorded as *proposed defaults* in S0_IDENTITY_ACCESS_DESIGN. They are subject to security-owner approval (DEC-026, RR-10):
- S-2: token lifetimes;
- S-3: password policy;
- S-4: lockout;
- S-5: cookies;
- S-6: keys;
- S-7: 404/403;
- S-8: masking;
- S-9: corrections share the intake permission;
- S-10: limiter;
- S-11: audit anchoring deferred;
- S-13: contact encryption;
- S-14: search logging.

## 3. Documents created and modified

See §5 and the evidence manifest for hashes.

**Created:**
- `docs/spec/APPROVED_EXCEPTIONS.md`
- `docs/adr/README.md`
- `docs/adr/ADR-0003-s0-technical-architecture.md`
- `docs/adr/ADR-0004-identity-tokens-authorization.md`
- `docs/adr/ADR-0005-audit-and-immutability.md`
- `docs/adr/ADR-0006-api-contract-and-generated-client.md`
- `docs/adr/ADR-0007-script-studio-naming-and-lifecycle.md`
- `docs/adr/ADR-0008-s0-scope-boundaries.md`
- `docs/data/S0_DATA_MODEL.md`
- `docs/security/S0_IDENTITY_ACCESS_DESIGN.md`
- `docs/security/THREAT_MODEL_S0.md`
- `docs/security/ASVS_S0_CONTROL_MATRIX.md`
- `docs/contracts/S0_API_CATALOGUE.md`
- `docs/product/S0_SCREEN_SPEC.md`
- `docs/product/S0_KPI_DEFINITIONS.md`
- `docs/plans/S0_IMPLEMENTATION_PLAN.md`
- `docs/acceptance/S0_TEST_MATRIX.md`
- `docs/acceptance/S0.md`
- `docs/acceptance/CP0.0.md`
- `scripts/evidence_manifest.py`

**Modified (consistency only; no requirement change):**
- `docs/product/SCREEN_NAMING_AND_ROUTES.md`
- `docs/product/SEARCH_WORKSPACE_AND_POLICY_VIEWS.md`
- `docs/product/SCRIPT_GOVERNANCE_AND_ASSIGNMENT.md`
- `docs/contracts/API_CONTRACT_POLICY.md`
- `docs/data/CANONICAL_GRAIN_AND_RELATIONSHIPS.md`
- `docs/engineering/MULTI_REPO_ARCHITECTURE.md`
- `docs/spec/02_CLAUDE_CODE_EXECUTION_PLAN.md` (header and CP0.0 overlay note only)
- `docs/acceptance/S0_TEMPLATE.md`
- `docs/acceptance/README.md`
- `docs/adr/ADR-0002-product-and-detail-terminology.md` (amendment note only)
- `CHANGELOG.md`
- `scripts/validate_specs.py`

## 4. CP0.0 acceptance criteria

| ID | Criterion | Evidence | Result |
|---|---|---|---|
| AC-0.0-01 | All 70 S0 requirements have a scope class, a target checkpoint and at least one defined test ID | S0_TEST_MATRIX §1–§2; validator check `S0 matrix` | PASS — 70/70 rows; F 55, P 5, D 10; 95 tests defined |
| AC-0.0-02 | C-1…C-31 each RESOLVED, DEFERRED (with owner and target) or MOOT; none unclassified | §2; validator check `contradiction register` | PASS — 33 entries; 20 owner, 10 engineering, 2 deferred, 1 moot; 0 unclassified |
| AC-0.0-03 | Data model defines every table with grain, keys, constraints, flags and grain-doc mapping; enums; immutability; seed specification | S0_DATA_MODEL; validator check `data model mapping` | PASS — 63 canonical tables mapped, each with a Build checkpoint; 59 built in S0, 4 deferred; lifecycle enum check passes |
| AC-0.0-04 | API catalogue gives every endpoint a method, path, permission, scope, response, errors and checkpoint | S0_API_CATALOGUE; validator check `API catalogue` | PASS — 80 endpoints; every permission exists in the matrix |
| AC-0.0-05 | Screen spec gives every route its data sources, states, actions, stage-disabled actions, mockup reference and deviations; route set equals SCREEN_NAMING | S0_SCREEN_SPEC; validator check `route parity` | PASS — 29 routes; parity with SCREEN_NAMING; all API references resolve |
| AC-0.0-06 | KPI definitions give numerator, denominator, eligibility (held/cancelled), exclusions, cohort, time zone and drilldown for every KPI, applying K-1…K-4 | S0_KPI_DEFINITIONS; validator check `KPI catalogue` | PASS — 18 KPIs + 7 operational counts; all 12 BRD §10 KPIs covered; K-1…K-4, D-17 outcome model and D-18 `SLA-EX-001` present |
| AC-0.0-07 | Permission matrix covers every endpoint and both roles; ADMIN lacks approve, override, recording, export and unmask | S0_IDENTITY_ACCESS_DESIGN §6; catalogue permissions exist in matrix (validator) | PASS — validator confirms no reserved permission is marked for ADMIN |
| AC-0.0-08 | Threat model and ASVS matrix: every threat or control links to a defined test ID or a residual risk | THREAT_MODEL_S0; ASVS_S0_CONTROL_MATRIX; validator check `security traceability` | PASS — 32 threats and 17 ASVS chapters traced. The ASVS matrix is a design and verification plan, not certification evidence; requirement-level verification is pending a security reviewer (RR-09) |
| AC-0.0-09 | BRD, register and requirement counts unchanged; 237 IDs and 55 business tests preserved | `git diff --stat` on those files is empty; validator baseline checks | PASS — empty diff; frozen SHA-256 baselines and ID-set digest match |
| AC-0.0-10 | Extended validator passes, including exception-aware terminology checks | `docs/acceptance/evidence/CP0.0/validate_specs.txt` | PASS — exit 0; 10 negative mutation tests each fail as expected (see §5) |
| AC-0.0-11 | ADR index matches ADR files | Validator check `ADR index` | PASS — 8 ADR files = 8 index entries |
| AC-0.0-12 | Owner acceptance recorded | §6 | **ACCEPTED** — project owner, 2026-11-15; evidence `docs/acceptance/evidence/CP0.0/` (validator PASS run 2026-11-15T05:47:53Z; manifest SHA-256 `6c8269abbabb90101a900ca7c922f2d750cc040d547cefa4c2748eab0d8ded03`) |

## 5. Validation evidence

Filled from the local run. Raw outputs are in `docs/acceptance/evidence/CP0.0/`.

| Check | Command | Result |
|---|---|---|
| Specification validator | `python3 -I scripts/validate_specs.py` | **PASS**: baseline (237 requirements, 55 tests) + 31 CP0.0 checks. `evidence/CP0.0/validate_specs.txt` |
| Validator negative tests | Mutated scratch copies: legacy term in new doc; BRD byte change; register edit; S0 row removed; undefined test ID; route drift; unclassified contradiction; reserved permission granted to ADMIN; ADR missing from index; unknown endpoint permission | **10/10 detected** (exit 1 with the specific message). Scratch copies deleted afterwards |
| Unchanged source documents | `git diff --stat HEAD -- docs/spec/01_MASTER_BRD.md docs/spec/03_REQUIREMENTS_REGISTER.csv docs/spec/REQUIREMENT_COUNTS.json` | **Empty diff**; SHA-256 values equal the frozen baselines. `evidence/CP0.0/unchanged_sources.txt` |
| File manifest (C-23) | `python3 scripts/evidence_manifest.py . --exclude docs/acceptance/evidence/` | Base SHA `17fb5e3…` + per-file SHA-256 + manifest SHA-256. `evidence/CP0.0/manifest.txt` |
| Secret scan | Regex pattern scan of the whole working tree, including untracked files | **No matches.** Limitation: no dedicated scanner (gitleaks/detect-secrets/trufflehog) is installed, and installing one was not authorised, so this is a weaker substitute. A dedicated scanner is a mandatory prerequisite for CP0.1 (ADR-0003 §5). `evidence/CP0.0/secret_scan.txt` |

## 6. Owner acceptance

| Role | Name | Date | Decision |
|---|---|---|---|
| Project owner (local development baseline) | Project owner | 2026-11-15 | **ACCEPTED** — "I ACCEPT CP0.0 — SPECIFICATION FOUNDATION for the local Call360 development baseline". Evidence: `docs/acceptance/evidence/CP0.0/` (manifest SHA-256 `6c8269ab…8ded03`; this acceptance-record edit was made after that manifest) |
| Product Owner / S&C (proposed) | TBD (C-20) | — | PENDING (not required for local development, D-20) |
| Engineering Lead | TBD (C-20) | — | PENDING |
| Security / Privacy | TBD (C-20) | — | PENDING (also S-2…S-14, RR-09) |

CP0.0 acceptance does **not** authorise CP0.1. CP0.1 requires "IMPLEMENT CP0.1".
