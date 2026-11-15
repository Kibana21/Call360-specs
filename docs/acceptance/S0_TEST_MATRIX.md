# Call360 — Stage 0 requirement-to-test matrix

**Status:** CP0.0 draft, 2026-11-15
**Scope:** all 70 Stage 0 requirements in `docs/spec/03_REQUIREMENTS_REGISTER.csv` (69 P0, 1 P1). The register is **not edited**: its `test_id` column stays empty by decision C-27, and this matrix is the traceability source. The validator checks that every S0 requirement appears in §1 and that every test ID referenced anywhere in the CP0.0 documents is defined in §2.

**Scope classes:**
- **F**: delivered in full in S0.
- **P**: delivered as a deliberate S0 subset. The S0 acceptance criterion is met, and the named later stage extends it.
- **D**: display of persisted or seeded data only. Computation or authoring comes in the named later stage (D-4, D-10).

## 1. Requirement matrix

| Requirement | Pri | Class | S0 scope (what is and is not delivered) | CP | Tests |
|---|---|---|---|---|---|
| APP-001 | P0 | F | Authenticated shell; every S0 route reachable from persistent navigation; S4 items visible but disabled with stage chip | CP0.1A, CP0.5 | E2E-01, E2E-17, FE-01 |
| APP-002 | P0 | F | KPIs computed in SQL per `S0_KPI_DEFINITIONS.md`; seed changes move cards and rows together | CP0.3, CP0.5 | BE-KPI-01, BE-KPI-04, BE-KPI-05, BE-KPI-06, E2E-02 |
| APP-003 | P0 | F | Case → attempts → sessions register; golden case with 3 attempts and 1 session | CP0.2, CP0.3, CP0.5 | BE-DATA-03, BE-API-01, E2E-03 |
| APP-004 | P0 | F | Typed KPI drilldown; Explorer applies the identical server predicate | CP0.3, CP0.5 | BE-KPI-02, E2E-02 |
| APP-005 | P0 | F | Search by case ref, attempt/session ref ("call ID") and policy ref; scoped | CP0.3 | BE-SRCH-01, BE-SEC-02, E2E-06 |
| APP-006 | P1 | F | Delivered through SEARCH-004/005: saved views, sortable columns, cursor pagination | CP0.3, CP0.5 | BE-SRCH-04, BE-SRCH-07, E2E-07, E2E-08 |
| CASE-001 | P0 | F | Synthetic customer/party, policy, sale and case model; masked policy context in Call Detail | CP0.2, CP0.5 | BE-DATA-03, BE-API-02, E2E-03 |
| CASE-002 | P0 | F | Immutable fact snapshot pinned per survey run and session; later correction does not change it | CP0.2, CP0.4 | BE-DATA-04, BE-ING-05, E2E-19 |
| SUR-001 | P0 | D | Script entities (family, version, section, module, question revision, branching condition, answer schema) seeded; Script Studio renders the question navigator and metadata read-only. Authoring is S2 | CP0.2, CP0.5 | BE-API-04, E2E-09 |
| GOV-001 | P0 | F | `DATA_POLICY=SYNTHETIC_ONLY` in local/test; non-synthetic intake rejected; readiness fails on non-synthetic rows; mock upstream local-only; no production credentials | CP0.1A, CP0.2, CP0.4 | BE-DATA-10, BE-DATA-14, BE-ING-07, SCAN-01 |
| GOV-002 | P0 | F | Every route declares a permission or is on the public allowlist; unauthenticated requests get 401 | CP0.1A | BE-SEC-01, E2E-01 |
| PARTY-001 | P0 | F | Six party roles on `policy_party_role`; one party, many roles, never duplicated | CP0.2, CP0.5 | BE-DATA-03, E2E-06 |
| PARTY-002 | P0 | F | Stable source party refs (`external_reference`) and independent contact-method IDs | CP0.2 | BE-DATA-03 |
| PARTY-003 | P0 | P | Effective-dated contact methods with preference, language, timezone, consent and suppression flags stored; change inserts a new version; attempt snapshots unaffected. **Not in S0:** suppression enforcement during calling (S4, CASE-006) | CP0.2 | BE-DATA-08 |
| PARTY-004 | P0 | P | Eligibility from governed list `callable_party_roles` plus suppression and missing-contact checks; ineligible gets explicit reason and `NO_ELIGIBLE_CONTACT` blocking hold. **Not in S0:** authority/identity verification at call time (S1, PARTY-006) | CP0.2, CP0.4 | BE-ING-08, BE-DATA-09, E2E-11 |
| PARTY-005 | P0 | F | Masked party and contact cards with role and relationship in Policy Detail and Call Detail | CP0.3, CP0.5 | BE-API-02, BE-SRCH-05, E2E-06 |
| POL-001 | P0 | F | Policy and sale event separate; multi-sale policy (new business plus top-up) | CP0.2 | BE-DATA-07 |
| POL-002 | P0 | F | Typed product family, subtype, ILP, premium amount/currency/frequency/term, sum assured, effective dates | CP0.2, CP0.3 | BE-API-02 |
| POL-003 | P0 | F | Channel, location, campaign and FSC frozen on sale event | CP0.2, CP0.3 | BE-API-02 |
| POL-004 | P0 | F | Policy Detail workspaces with deep links to risk, Sale Context (`?sale=`) and Call Detail | CP0.5 | E2E-06 |
| POL-005 | P0 | F | Provenance NOT NULL; every material field shows source and as-of; intake lineage with payload digest | CP0.2, CP0.4, CP0.5 | BE-DATA-05, BE-ING-03, E2E-06 |
| POL-006 | P0 | F | Fact snapshot frozen at assignment and session; immutable | CP0.2 | BE-DATA-04 |
| POL-007 | P0 | F | Authorised manual entry and correction with reason; `field_change` diff, actor and source | CP0.4 | BE-ING-03, BE-ING-05, E2E-11, E2E-19 |
| RISK-001 | P0 | F | Separate schemas and labels for SBQ selection risk, suitability fact and finding severity | CP0.2, CP0.5 | BE-DATA-06, E2E-06 |
| RISK-002 | P0 | D | Persisted band, date, reason codes, source system and original value displayed | CP0.2, CP0.5 | BE-API-03, E2E-06 |
| RISK-003 | P0 | D | Typed factor values with input snapshot hash and rule-set version; reproducible | CP0.2 | BE-DATA-11 |
| RISK-004 | P0 | D | Seeded `SOURCE_ASSIGNED` and `RULE_ASSESSED` (stored synthetic trace) records, visibly distinguished. **No calculation in S0** (RISK-008, S2) | CP0.2, CP0.5 | BE-API-03, E2E-06 |
| RISK-005 | P0 | D | Risk summary with version and origin on Policy Detail, intake preview and Call Detail | CP0.4, CP0.5 | BE-API-03, E2E-03, E2E-06, E2E-11 |
| RISK-006 | P0 | P | Factor vocabulary and bands as versioned governed code lists; no thresholds in code. **Not in S0:** business-approved editing of the vocabulary (S2) | CP0.1B, CP0.2 | BE-CFG-01, BE-API-03 |
| SCR-001 | P0 | D | Family, version, sections, module question references and immutable manifest seeded; ordered common and ILP questions shown | CP0.2, CP0.5 | BE-DATA-04, BE-API-04, E2E-09 |
| SCR-002 | P0 | D | Expected-answer policy, acceptable variants, policy-fact match and unacceptable outcomes stored and displayed; YES is not universally compliant. Evaluation is S3 | CP0.2, CP0.5 | BE-DATA-12, E2E-09 |
| SCR-003 | P0 | F | Script Studio search and filter by product, risk, channel, status and effective date | CP0.3, CP0.5 | BE-API-04, E2E-09 |
| SCR-004 | P0 | D | Assigned script, exact version, rationale and rule trace in case and Call Detail; historic case keeps its version | CP0.3, CP0.5 | BE-API-04, BE-DATA-04, E2E-03 |
| SCR-005 | P0 | D | Seeded deterministic assignment for ILP: COMMON plus ILP (plus ELEVATED_RISK for the golden case) | CP0.2 | BE-DATA-03, E2E-09 |
| ING-001 | P0 | F | Mock Policy and Risk APIs (separate local app) with versioned deterministic payloads over HTTP | CP0.4 | BE-ING-01, E2E-12 |
| ING-002 | P0 | F | Manual injection through UI and API; new case held `AWAITING_SCRIPT_ASSIGNMENT` | CP0.4 | BE-ING-03, BE-ING-10, E2E-11 |
| ING-003 | P0 | F | `source_type` and `source_reference` mandatory everywhere, including manual | CP0.2, CP0.4 | BE-DATA-05, BE-ING-03 |
| ING-004 | P0 | F | Validation with field details and preview before commit; preview persists nothing | CP0.4 | BE-ING-04, E2E-11 |
| SEARCH-001 | P0 | F | Global search over case, policy, customer alias, FSC and sale event (plus attempt, session and script) | CP0.3, CP0.5 | BE-SRCH-01, E2E-06 |
| SEARCH-002 | P0 | F | Faceted Call Explorer (product, ILP, risk, channel, FSC, owner, status, date, script version); URL-shareable | CP0.3, CP0.5 | BE-SRCH-03, E2E-02, E2E-07 |
| SEARCH-003 | P0 | F | Exact normalised IDs, prefix, controlled fuzzy alias, date ranges; matched-field explanation | CP0.3 | BE-SRCH-02 |
| SEARCH-004 | P0 | F | Per-user saved views without cross-user leakage | CP0.3, CP0.5 | BE-SRCH-07, E2E-08 |
| SEARCH-005 | P0 | F | Deterministic sort and cursor pagination; no duplicates or gaps | CP0.3 | BE-SRCH-04, E2E-07 |
| SEARCH-006 | P0 | F | Scope applied before results, counts, facets and suggestions | CP0.1B, CP0.3 | BE-SRCH-05, BE-KPI-03, BE-SEC-02 |
| SEARCH-007 | P0 | F | Structured empty, error and loading states; every result carries a typed route | CP0.3, CP0.5 | BE-SRCH-06, E2E-14 |
| IAM-001 | P0 | F | Login, logout, session-expired and unauthorized screens; unauthenticated routes redirect; API returns 401 | CP0.1A | BE-AUTH-01, E2E-01 |
| IAM-002 | P0 | F | Local IdP; bootstrap admin plus developer-specific accounts; no committed or default credentials; demo-only banner | CP0.1A | BE-AUTH-09, SCAN-01, E2E-01 |
| IAM-003 | P0 | F | Immutable principal separate from identity binding; actor history preserved | CP0.1A | BE-IAM-01 |
| IAM-004 | P0 | F | Users, roles, permissions, groups, memberships, group-role and group-scope mappings | CP0.1A, CP0.1B | BE-IAM-02, E2E-13 |
| IAM-005 | P0 | F | Backend authorization on every endpoint and object, including media metadata | CP0.1A–CP0.4 | BE-SEC-01, BE-SEC-02, E2E-10 |
| IAM-006 | P0 | F | Short-lived EdDSA access JWT with full claim and algorithm validation | CP0.1A | BE-AUTH-04 |
| IAM-007 | P0 | F | Opaque rotating refresh tokens, HMAC-stored, reuse revokes the family | CP0.1A | BE-AUTH-05, BE-AUTH-10 |
| IAM-008 | P0 | F | HttpOnly cookies plus CSRF; no browser token storage | CP0.1A, CP0.5 | BE-AUTH-07, BE-AUTH-08, FE-02, E2E-15 |
| IAM-009 | P0 | F | Logout, revocation, disable and membership change effective on the next request | CP0.1A, CP0.1B | BE-AUTH-06, E2E-13 |
| IAM-010 | P0 | F | Admin Users & Groups screen; only admin mutates; before/after audited | CP0.1A, CP0.1B, CP0.5 | BE-AUD-04, E2E-13 |
| IAM-011 | P0 | F | Security audit events with actor, session, IP and outcome; no secrets | CP0.1A | BE-AUD-03, BE-AUTH-08 |
| SEC-001 | P0 | F | STRIDE threat model linked to mitigations and tests (`THREAT_MODEL_S0.md`) | CP0.0 | DOC-01 |
| SEC-002 | P0 | F | Strict schemas (unknown fields rejected), bounded inputs, parameterised queries | CP0.1A–CP0.4 | BE-SEC-03, BE-SEC-04 |
| SEC-003 | P0 | F | Default-deny CORS, CSRF, CSP and security headers | CP0.1A | BE-SEC-05, BE-AUTH-07, E2E-15 |
| SEC-004 | P0 | F | Per-route, per-record and per-search-result permission checks; BOLA/IDOR matrix | CP0.3, CP0.4 | BE-SEC-02, BE-SRCH-05 |
| SEC-005 | P0 | F | Signing keys and peppers in local environment only; secret scanning of repos and bundle mandatory | CP0.1A, CP0.5 | SCAN-01, SCAN-02 |
| SEC-006 | P0 | F | Rate limits on login, refresh, writes and search (single-instance limiter, RR-05) | CP0.1A, CP0.3 | BE-AUTH-03, BE-SEC-06 |
| SEC-007 | P0 | F | Append-only audit with hash chain and documented limitations (ADR-0005 §2) | CP0.1A | BE-AUD-01, BE-AUD-02 |
| SEC-008 | P0 | F | ASVS 5.0 L2 control-to-test matrix with remediation owners (`ASVS_S0_CONTROL_MATRIX.md`) | CP0.0, CP0.6 | DOC-02 |
| REG-001 | P0 | P | Seeded read-only regulatory reference register with interpretation status (`NOT_REVIEWED`); a reference never implies a mandatory question. **Not in S0:** editing and change requests (REG-003+, S2) | CP0.2, CP0.5 | BE-API-05, E2E-09 |
| REG-002 | P0 | D | Question ↔ AIA control ↔ optional public reference shown, visually distinct | CP0.2, CP0.5 | BE-API-05, E2E-09 |
| ADMIN-001 | P0 | F | Admin dashboard: users, groups, memberships, sessions, audit events, feature settings | CP0.1A, CP0.1B, CP0.5 | E2E-13 |
| ADMIN-002 | P0 | P | Change history (who, when, old/new, reason, origin) for users, groups, mappings, configuration, policy corrections and intake. Script, rule and risk history is shown from seeded publication records, because they cannot be edited in S0. Integration configuration is not editable in S0 | CP0.1A–CP0.4 | BE-AUD-04, BE-ING-05 |
| ADMIN-003 | P0 | F | Reserved approve, publish, override, recording, export and unmask permissions not grantable to ADMIN | CP0.1A | BE-IAM-03 |
| ADMIN-004 | P0 | F | Versioned code lists and feature flags; historical values resolvable; governed lists read-only | CP0.1B | BE-CFG-01 |

**Totals (validator-checked):**
- **F: 55**
- **P: 5** (PARTY-003, PARTY-004, RISK-006, REG-001, ADMIN-002)
- **D: 10** (SUR-001, RISK-002, RISK-003, RISK-004, RISK-005, SCR-001, SCR-002, SCR-004, SCR-005, REG-002)
- **Total: 70**

No S0 requirement is BLOCKED.

## 2. Test catalogue

| Test ID | Type | Repo | Verifies | Business tests |
|---|---|---|---|---|
| BE-AUTH-01 | API integration | backend | Login sets cookies; new session ID per login; unauthenticated → 401 | T-51 |
| BE-AUTH-02 | API integration | backend | Uniform failure response and timing (unknown user, wrong password, disabled, locked) | T-51 |
| BE-AUTH-03 | API integration | backend | Account backoff and IP throttle; 429 handling | T-51 |
| BE-AUTH-04 | unit + API | backend | Expired, not-yet-valid, wrong `iss`, wrong `aud`, bad signature, `alg=none`, HS256 substitution, unknown `kid`, refresh token presented as access all rejected | T-53 |
| BE-AUTH-05 | API integration | backend | Refresh rotation; reuse revokes family and session; audit event | T-52 |
| BE-AUTH-06 | API integration | backend | Logout, admin revoke, disable principal, membership/mapping change take effect on next request | T-54 (local) |
| BE-AUTH-07 | API integration | backend | Missing or mismatched CSRF and foreign `Origin` rejected on every unsafe route, including login | — |
| BE-AUTH-08 | API + log capture | backend | No token, password or cookie values in logs or response bodies | T-48 |
| BE-AUTH-09 | CLI integration | backend | Bootstrap refuses second run; no default credentials exist after migrate + seed | — |
| BE-AUTH-10 | API integration | backend | Concurrent refresh: (a) the previous generation presented within the grace window returns `409 REFRESH_SUPERSEDED` with **no** `Set-Cookie`, mints no token and leaves the session usable; (b) the same token after the window, (c) a token two or more generations old, and (d) a duplicate after logout are each reuse, revoking the family and session; (e) two simultaneous redemptions of one unused token produce exactly one rotation | T-52 |
| BE-IAM-01 | unit + DB | backend | Principal ≠ binding; binding change preserves audit actor history | — |
| BE-IAM-02 | API integration | backend | Group → role mappings (CP0.1A) and group → market-scope mappings (CP0.1B-2); unrecognised group grants nothing; no scope means scoped queries fail closed | — |
| BE-IAM-03 | unit + API | backend | Reserved permissions cannot be granted; ADMIN lacks them | T-50 (model only) |
| BE-SEC-01 | route inventory | backend | Every route declares a permission or is on the public allowlist | — |
| BE-SEC-02 | BOLA matrix | backend | For each object endpoint: other-market ID → 404 + `ACCESS.DENIED_OBJECT`; USER on admin/intake → 403 | T-46, T-49 |
| BE-SEC-03 | API | backend | Unknown fields, oversize strings and arrays rejected; mass assignment of `created_by`, `state`, `is_synthetic` impossible | — |
| BE-SEC-04 | API | backend | SQL/LIKE/regex injection payloads in search and filters are parameterised and bounded | T-48 |
| BE-SEC-05 | API | backend | CSP and security headers present; no CORS allow-origin | — |
| BE-SEC-06 | API | backend | Rate limits on refresh, search, writes and intake | — |
| BE-AUD-01 | DB | backend | Trigger rejects UPDATE and DELETE on `audit_event`; no API offers either | T-55 |
| BE-AUD-02 | unit + DB | backend | `audit-verify` passes on clean data and reports first break after tamper | T-55 |
| BE-AUD-03 | API | backend | Security events recorded with required metadata and without secrets | — |
| BE-AUD-04 | API | backend | Admin changes record before/after, reason, actor and correlation ID | — |
| BE-CFG-01 | API + DB | backend | New code-list version keeps old values resolvable; governed lists read-only; stage-gated flags cannot be enabled | — |
| BE-DATA-01 | migration | backend | Migrate from empty to head; downgrade 1; re-upgrade. At each checkpoint's head, the schema contains exactly the tables whose Build column is at or before that checkpoint (59 at the end of S0); the four deferred tables do not exist | — |
| BE-DATA-02 | seed | backend | Seed twice on a freshly reset schema gives identical content digest | — |
| BE-DATA-03 | seed invariants | backend | Volumes, golden fixtures, role edges, attempt/session linkage (INV-01, INV-03) | T-21 |
| BE-DATA-04 | DB | backend | Immutable records reject UPDATE/DELETE; pinned version was PUBLISHED at session start (INV-04, INV-09); superseded version still referenced | T-15, T-33 |
| BE-DATA-05 | DB | backend | Provenance NOT NULL on all **P** tables (INV-07) | T-36 |
| BE-DATA-06 | DB + API | backend | Three risk concepts in separate structures and labels (INV-08) | — |
| BE-DATA-07 | DB | backend | Policy with several sale events has distinct cases | T-31 |
| BE-DATA-08 | DB | backend | Contact change creates a new version; attempt snapshot unchanged (INV-05) | T-38 |
| BE-DATA-09 | DB | backend | Blocking hold prevents READY or IN_PROGRESS; hold placement and release audited (INV-06) | T-35 |
| BE-DATA-10 | config + DB | backend | `SYNTHETIC_ONLY` readiness fails with a non-synthetic row; non-synthetic intake rejected (INV-10) | — |
| BE-DATA-11 | unit | backend | Stored factor values reproduce `input_snapshot_sha256` | — |
| BE-DATA-14 | config + DB | backend | Schema isolation: the test role cannot read, write, truncate, alter or drop anything in `call360`; the test harness and Alembic refuse to run if the schema is not `call360_test`, the role is the application role or a superuser, or the role has any privilege on `call360`; reset commands only ever target `call360_test` | — |
| BE-DATA-12 | seed + API | backend | Question set includes each expected-answer policy; a YES answer to an acknowledgement or narrative question is not auto-compliant | T-44 (data) |
| BE-API-01 | API | backend | Case, attempt and session reads for the golden case | T-21 |
| BE-API-02 | API | backend | Policy, sale and party reads, typed fields, masking | T-32 (display) |
| BE-API-03 | API | backend | Risk reads with origin, version and provenance | T-34 (data) |
| BE-API-04 | API | backend | Script library filters, version detail, assignment trace | T-39 (display) |
| BE-API-05 | API | backend | Regulatory register and control mappings are distinct | — |
| BE-API-06 | API | backend | Media and transcript availability objects are both `NOT_AVAILABLE / NO_CAPTURE_BEFORE_S1` | — |
| BE-API-07 | API | backend | Error envelope, correlation ID header, typed codes | — |
| BE-KPI-01 | SQL vs fixture | backend | Every KPI against a hand-computed fixture, including held, cancelled, closed-unverified and multi-attempt rows | T-21, T-29 (KPI part) |
| BE-KPI-02 | API | backend | Drilldown set equality for numerator and denominator | T-30 |
| BE-KPI-03 | API | backend | Scope applied before aggregation | T-46 |
| BE-KPI-04 | API | backend | `NOT_MEASURED` KPIs never return a number | — |
| BE-KPI-05 | SQL vs fixture | backend | Outcome classification: mandatory-control satisfaction per expected-answer policy; narrative-review questions block `VERIFIED_COMPLIANT` in S0; `VERIFIED_CONTROL_EVIDENCE_INCOMPLETE` guard; labels never say non-compliant | T-29 (KPI part) |
| BE-KPI-06 | SQL vs fixture | backend | `SLA-EX-001`: valid exemption (`CB-2026-10494`); missing authorisation (`CB-2026-10495`) and retrospective cancellation (`CB-2026-10496`) not exempt; held case past due counted as breached (`CB-2026-10498`) | — |
| BE-SRCH-01 | API | backend | Each entity type findable from one query | T-47 |
| BE-SRCH-02 | API | backend | Ranking exact > prefix > fuzzy, with matched field | — |
| BE-SRCH-03 | API | backend | Facet combination and URL-serialisable filters | — |
| BE-SRCH-04 | API | backend | Cursor stability with concurrent inserts; no duplicates or gaps | — |
| BE-SRCH-05 | API | backend | Restricted user: zero rows, counts, facets or suggestions for other-market policy or phone refs | T-46, T-47 |
| BE-SRCH-06 | API | backend | Every hit carries a typed route | — |
| BE-SRCH-07 | API | backend | Saved views owner-only; another user's view ID → 404 | — |
| BE-SRCH-08 | log capture | backend | Search terms logged only as hashes | T-48 |
| BE-ING-01 | contract | backend | Mock upstream payloads deterministic, versioned and synthetic | — |
| BE-ING-02 | API | backend | Mock import replay is idempotent; no duplicate cases | T-37 |
| BE-ING-03 | API | backend | Manual commit creates `MANUAL` records with actor, reason, source; duplicate source event rejected | T-36 |
| BE-ING-04 | API | backend | Invalid role, product, currency or amount rejected with field details; preview persists nothing | — |
| BE-ING-05 | API | backend | Correction writes `field_change` and audit; fact snapshots and old evidence unchanged; open-case impact flag | T-33 |
| BE-ING-06 | API | backend | USER → 403 on all intake routes, audited | T-49 |
| BE-ING-07 | config | backend | Mock upstream not mounted and intake sources absent outside local/test | — |
| BE-ING-08 | API | backend | Ineligible contact (role, suppression, missing) gets explicit reason and `NO_ELIGIBLE_CONTACT` hold | T-32 (partial) |
| BE-ING-09 | API | backend | Source vs existing risk mismatch keeps both and holds; ILP with missing risk gets `RISK_TRIAGE` | T-34 (data), T-35 |
| BE-ING-10 | API | backend | Intake-created case gets `AWAITING_SCRIPT_ASSIGNMENT`; routing reported as not evaluated | — |
| BE-CT-01 | contract | backend | OpenAPI regenerates byte-identically; SHA-256 recorded | — |
| FE-01 | component | frontend | Loading, empty, error, partial and forbidden states for every data region | — |
| FE-02 | unit | frontend | Auth client: single-flight and cross-tab refresh, CSRF header, never touches token storage | — |
| FE-03 | contract | frontend | `api:check`: no generated-code drift; pinned artifact equals backend artifact | — |
| FE-04 | a11y | frontend | axe on every screen: zero serious or critical | — |
| SCAN-01 | secret scan | all three | No secrets in any repository working tree (including untracked files) | — |
| SCAN-02 | bundle scan | frontend | No key or token patterns in the built bundle | — |
| E2E-01 | Playwright (real stack) | frontend | Unauthenticated redirect; login; logout; demo-only banner; no role-switch control | T-51 |
| E2E-02 | Playwright | frontend | Overview card → Call Explorer with equal count for each KPI card | T-30 |
| E2E-03 | Playwright | frontend | `CB-2026-10482`: 3 attempts, 1 session, pinned script and rationale; refresh and back keep filters | T-21, T-39 |
| E2E-04 | Playwright | frontend | `?attempt=&session=` deep link focuses; mismatched IDs show an error | — |
| E2E-05 | Playwright | frontend | Recording `NOT_AVAILABLE` panel; later-stage controls disabled with reason | — |
| E2E-06 | Playwright | frontend | Search → Policy Detail (parties, sale, risk with provenance, script assignment) → Call Detail | T-47 |
| E2E-07 | Playwright | frontend | Sort and cursor pagination with no duplicate or missing rows | — |
| E2E-08 | Playwright | frontend | Saved view round-trip; another user cannot see it | — |
| E2E-09 | Playwright | frontend | Script Studio: published vs draft; ILP version shows COMMON + ILP; expected-answer policy; control vs regulatory source | T-15, T-39 |
| E2E-10 | Playwright | frontend | USER denied Administration and Data Intake (UI and API); other-market case URL → not found; audit shows denial | T-46, T-49 |
| E2E-11 | Playwright | frontend | Manual intake: invalid → errors; valid → preview → commit → Policy Detail and held Call Detail; replay rejected or idempotent | T-36 |
| E2E-12 | Playwright | frontend | Mock sync twice; second run reports unchanged; no duplicate cases | T-37 |
| E2E-13 | Playwright | frontend | Admin disables a user → that user's next request fails; membership change; audit before/after | T-54 (local) |
| E2E-14 | Playwright | frontend | Empty, error and partial states using controlled backend conditions | — |
| E2E-15 | Playwright | frontend | No tokens in `localStorage`, `sessionStorage` or URL; cookies HttpOnly; cross-site POST without CSRF rejected | — |
| E2E-16 | Playwright | frontend | Voice Studio preflight `NOT_AVAILABLE`; no microphone prompt | — |
| E2E-17 | Playwright | frontend | axe, keyboard-only path through main flow, 1280 and 1440 px layouts | — |
| E2E-18 | Playwright | frontend | Title "Call360"; Call Detail heading and breadcrumb; "Script Studio" label; no "Call 360" or "Survey Studio" label anywhere | — |
| E2E-19 | Playwright | frontend | Admin corrects a policy premium; history shows diff, actor and reason; the earlier session's snapshot value is unchanged | T-33 |
| DOC-01 | document review | specs | Threat model complete; every threat has a mitigation and a test ID or residual risk | — |
| DOC-02 | document review | specs | ASVS matrix complete; every control area has tests or a residual risk and an owner | — |
| SPEC-01 | validator | specs | `scripts/validate_specs.py` passes (existing and CP0.0 checks) | — |

## 3. Business test (T-xx) applicability in Stage 0

| Applicability | Tests |
|---|---|
| **S0, full** | T-21, T-30, T-31, T-33, T-36, T-37, T-38, T-46, T-47, T-48, T-49, T-51, T-52, T-53, T-55 |
| **S0, adapted or partial (stated)** | T-15 (seeded superseded version still referenced; no publishing in S0) · T-32 (explicit contact selection and history; authority check at call time is S1) · T-34 (both values preserved and conflict held; no calculated risk in S0) · T-35 (missing ILP risk gets `RISK_TRIAGE` hold, no script assigned) · T-39 (seeded selection trace displayed; resolution is S2) · T-54 (local group membership removal; external IdP is S5) · T-29 (KPI treatment only: closed-unverified never counted as verified; closure workflow is S3/S4) · T-44 (data model only: YES with narrative stored as separate fields; evaluation is S3) |
| **Deferred** | T-16, T-50 → S2 (maker-checker workflow; S0 proves ADMIN lacks approve permission via BE-IAM-03) · T-40 → S2 (assignment engine, ADR-0008 §1) · T-41, T-42, T-43, T-45 → S2 · T-18 → S1/S3 (no media exists in S0; media-metadata scope covered by BE-SEC-02) · T-01…T-14, T-17, T-19, T-20, T-22…T-28 → S1–S6 per BRD stage |
