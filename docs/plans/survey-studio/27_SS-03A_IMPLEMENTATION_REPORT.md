# SS-03A — Survey definition foundation: technical implementation report

**Checkpoint:** SS-03A, authorised by the owner on 2026-11-21 ("Approve Decision Closure and Authorize SS-03A"),
decision register D-176…D-187. Built in three internally verified steps: A.1 pure domain, A.2 persistence and
governance, A.3 API and contract.
**Status: BUILT AND TECHNICALLY VERIFIED — presented for the owner's review. Not accepted.**
**Prepared:** 2026-11-22.

**Scope held.** Additive backend only. The development database was **not** migrated, re-seeded, read or written:
every migration and test ran against the isolated test database. No Script Studio table, endpoint, service, screen
or permission was modified or removed. No execution, call-plan assembly, non-answer, refusal, repeat, consent or
timeout behaviour was implemented. No telephony, Genesys, GPT Live or Voice Lab code was touched. No production or
development role was granted a permission. SS-03B was not started. No additional authoring application was
introduced. Synthetic data only. **The SS-03A work is uncommitted; nothing was pushed.**

**Not claimed.** No survey is eligible for a live call. No screen uses the new API. Nothing here is production
ready.

---

## 1. What was built

### A.1 — Pure Python domain (`app/domain/survey/`)

No database, clock, network or model is used by any of these modules.

| Module | Lines | Does |
|---|---:|---|
| `canonical.py` | 89 | Canonical JSON bytes and SHA-256 fingerprints: sorted keys, no whitespace, numbers without exponent or trailing zeros, arrays in order. **Refuses** anything that is not a JSON value |
| `documents.py` | 326 | Six document kinds with schema identifiers and structural contracts; the resolved bundle a survey is validated in; the manifest and its hash |
| `conditions.py` | 269 | The three-valued condition engine with an explanation tree; typed authoring checks; version-1 input types explicitly limited and extensible |
| `validator.py` | 713 | Structural and semantic validation: **67 stable codes**, each recording the fixture schema that introduced it |

**Reuse decision.** The existing `digest.sha256_of` was **not** reused: it converts unknown types to text
(`default=str`) and can write a float with an exponent, so its behaviour does not match the canonical contract. It
is untouched and still serves the manifests it already hashes.

### A.2 — Persistence and governance (`migrations/versions/0027_survey_definitions.py`, `store.py`)

Nine new tables, four trigger functions, four new permissions, three governed catalogs.

| Table | Mutability | Enforced in the database |
|---|---|---|
| `survey_definition` | Name and purpose | Code format; market |
| `survey_draft` | Mutable; one per survey | `revision` advances by exactly one; never deleted |
| `survey_asset_version` | `DRAFT` may change; `FROZEN` never | A frozen row cannot be updated, deleted or unfrozen; identity never changes |
| `survey_candidate` | **Insert-only** | No update, no delete; SHA-256 format |
| `survey_version` | **Insert-only** | Only for a candidate whose history says `APPROVED` |
| `survey_lifecycle_event` | **Append-only** | Legal transitions; **identity rules**; no update, no delete |
| `survey_wording_approval` | **Append-only** | Names item, language, wording version, hash and candidate |
| `survey_asset_usage` | Derived, rebuildable | — |
| `survey_catalog_entry` | Synthetic entries | Approval can only be `SYNTHETIC_UNAPPROVED`; every field has an explicit `speakable`; outcome class from the fixed list |

- **Status is derived, not stored.** Neither `survey_candidate` nor `survey_version` has a status column; a test
  asserts it.
- **Wording approval is separate evidence** (D-178). The wording row has no approval column and is never updated.
  Approving a candidate inserts one row per pinned wording. It records that the wording was reviewed in that
  candidate; it does **not** make synthetic wording approved for operational use.
- **Identity rules are enforced twice**, independently of permissions: in the service, and in a trigger on the event
  table that the service cannot bypass. Approver ≠ submitter and ≠ any maker; publisher ≠ submitter, ≠ any maker
  and ≠ approver (D-182).
- **Catalogs:** 8 synthetic fields, **all `speakable: false`** (D-181); 6 synthetic outcomes; 2 synthetic
  obligation placeholders. The class `NON_ANSWER_EXCEPTION` is accepted by the schema and has **no entry** (D-180).
  **No non-answer resolution is stored anywhere** — no field, no route key (D-179).
- **Permissions** `survey.read`, `survey.edit`, `survey.approve`, `survey.publish` exist and are granted to **no
  role**.

### A.3 — API and contract (`app/api/survey_definitions.py`)

Fifteen operations under `/api/v1/survey-definitions`, `/survey-candidates`, `/survey-versions`, `/survey-library`
and `/survey-conditions`. The retired legacy path was not reactivated; a test asserts it.

- **Off by default.** The server setting `survey_definitions_enabled` is false unless set. With it off the routes
  are not registered: the product is exactly as before.
- **Additive contract.** 199 → 214 operations; 405 → 427 schemas; **0 existing operations or schemas changed or
  removed**. OpenAPI SHA-256 `221985e7…` → `725fee2c…`. The frontend client was regenerated and its drift check
  passes. No screen calls the new operations.

---

## 2. API contract and permissions matrix

| # | Method and path (under `/api/v1`) | Permission | Changes state | Object rule |
|--:|---|---|:-:|---|
| 1 | `POST /survey-definitions` | `survey.edit` | Yes | Caller's market includes the survey's |
| 2 | `GET /survey-definitions` | `survey.read` | | Only surveys in the caller's markets |
| 3 | `GET /survey-definitions/{id}` | `survey.read` | | Outside the caller's markets → 404 |
| 4 | `GET /survey-definitions/{id}/draft` | `survey.read` | | Same |
| 5 | `POST /survey-definitions/{id}/draft/operations` | `survey.edit` | Yes | Same; `expected_revision` must be current |
| 6 | `POST /survey-definitions/{id}/draft/validate` | `survey.edit` | No (stores nothing) | Same |
| 7 | `POST /survey-definitions/{id}/candidates` | `survey.edit` | Yes | Same; no blocker |
| 8 | `GET /survey-candidates/{id}` | `survey.read` | | Market |
| 9 | `POST /survey-candidates/{id}/decision` | `survey.approve` | Yes | **Not a maker of the candidate** |
| 10 | `POST /survey-candidates/{id}/withdraw` | `survey.edit` | Yes | **Only its submitter** |
| 11 | `POST /survey-candidates/{id}/publish` | `survey.publish` | Yes | **Not a maker; not the approver** |
| 12 | `GET /survey-versions/{id}` | `survey.read` | | Market |
| 13 | `GET /survey-versions/{id}/content` | `survey.read` | | Market |
| 14 | `GET /survey-library/{kind}` | `survey.read` | | Frozen assets only |
| 15 | `POST /survey-conditions/evaluate` | `survey.read` | No (stores nothing) | — |

Every operation requires exactly one permission. Every `POST` verifies the session-bound CSRF token and a
per-person rate limit. Every state change writes an audit event; every identity or manifest refusal writes a
`DENIED` audit event that survives the rollback.

| Role | `survey.read` | `survey.edit` | `survey.approve` | `survey.publish` |
|---|:-:|:-:|:-:|:-:|
| USER | — | — | — | — |
| SC_CHECKER | — | — | — | — |
| ADMIN | — | — | — | — |

**No role holds any of them.** Until a governance ruling grants them, nobody can call these operations outside the
tests, which grant them per person at the authentication dependency on top of a real session.

**Draft operations.** `PUT_ASSET`, `REMOVE_ASSET`, `SET_CONTENT` — document-level. The prototype's fine-grained
editing operations (insert a question, change a route) are **not** server operations in SS-03A: an editor composes a
document and puts it. That is a decision for the frontend-integration checkpoint (§8).

**Error codes.** `STALE_DRAFT` · `VALIDATION_BLOCKED` · `DOCUMENT_INVALID` · `OPERATION_INVALID` · `ASSET_FROZEN` ·
`ASSET_OWNED_ELSEWHERE` · `MANIFEST_MISMATCH` · `SELF_REVIEW_DENIED` · `SELF_PUBLISH_DENIED` ·
`APPROVER_PUBLISH_DENIED` · `NOT_SUBMITTER` · `NOT_APPROVED` · `ALREADY_DECIDED` · `COMMENT_REQUIRED` ·
`SURVEY_CODE_TAKEN` · `MARKET_NOT_IN_SCOPE` · `CONDITION_INVALID` · `NOT_FOUND`.

---

## 3. Fixture verification

All 27 golden fixtures and their 82 expected runs are present and unchanged; a backend test asserts the counts per
schema (8 / 6 / 4 / 1 / 8 files; 25 / 18 / 16 / 4 / 19 runs; 14 plans).

| Check | Result |
|---|---|
| Every document of every fixture meets its structural contract and hashes stably | 27 of 27 fixtures |
| Server validation matches each fixture's expectation, under the rules of its own schema version | **27 of 27** |
| — K2, K6: six expected codes each, in order | exact |
| — H4: `MANDATORY_ESCALATION_OVERRIDDEN` ×2; J1: `ESCALATION_NOT_TERMINAL` ×3 | exact |
| — G3 (invalid on purpose): `SKIP_DISPOSITION_MISSING` at `mi-specialist:@SKIP` | exact |
| — every other fixture | no finding |
| Condition results the fixtures state explicitly (9 decision results, 23 eligibility results) | **32 of 32** |
| Eligibility from application data against every expected plan (K8: 12 evaluations) | all |

**What "parity" covers in SS-03A.** Documents, validation and condition evaluation. The fixtures' expected **runs**
and **plans** as a whole — what is asked, delivered and routed — belong to execution and plan assembly, which SS-03A
excludes. They remain verified by the five Python reference interpreters and the prototype engine.

**First-run result, reported as it happened.** 26 of 27 on validation and every condition result. The one
difference was fixture G3: it is invalid on purpose, the validator was right, and my test had assumed every fixture
without a `validation` block was valid. Schemas /1 and /2 state an invalid draft through a run that ends
`DRAFT_INVALID`; the test now reads that.

---

## 4. Database migration and rollback evidence

Isolated test database only (`call360_test`, least-privilege test role).

| Step | Result |
|---|---|
| Upgrade `0026_gpt_live_provider` → `0027_survey_definitions` | 9 tables, 4 functions, 4 permissions, 16 catalog entries created |
| Downgrade `0027` → `0026` | All 9 tables, 4 functions and 4 permissions removed; **every other table still present and identical in name set** |
| Upgrade again | Identical state |
| Downgrade while a survey definition exists | **Refused**: "survey definitions exist; downgrade would lose them and their approval history" |
| The project's own round-trip test over every revision | Passes with revision 0027 registered |
| Foreign keys between `survey_*` tables and any other table | **None, in either direction** |

**The development database.** No migration, seed or SQL was run against it in this checkpoint, so it remains at
`0026` (by construction; I did not query it to confirm). To keep it working, the server
accepts a schema one revision behind **only while the survey setting is off**, because revision 0027 only adds
tables nothing uses in that case. Measured on the running development server after the change: liveness 200,
readiness 200, survey route 404. With the setting on, the schema must be at 0027 or readiness fails closed.

**The revision name.** First written as `0027_survey_definition_foundation` (33 characters); Alembic's version
column holds 32. Renamed `0027_survey_definitions` before any run succeeded.

---

## 5. Security, immutability and concurrency evidence

Each row is a test that passes. "Database" means the assertion is made by attempting the change with SQL, not by
calling the service.

| Verification item (owner's list) | Evidence |
|---|---|
| 4. Frozen candidates, versions, assets and events cannot be modified or deleted | Database: `UPDATE` and `DELETE` refused on a frozen asset (content, state, deletion), a candidate (note, content, hash, deletion), a lifecycle event, a version and a wording approval |
| 5. Approval and publication enforce independent permission and identity rules | Service and HTTP: a person holding **all four** permissions cannot approve or publish their own candidate; the approver cannot publish. Database: the same events inserted directly are refused by the trigger; a version row for an unapproved candidate is refused |
| — each permission opens only its own operations | HTTP: with exactly one permission, the other operations return 403 |
| — no role holds a permission | HTTP: USER, SC_CHECKER and ADMIN get 403 on all 15; each refusal audited |
| — no session | HTTP: 401 on all 15 |
| — CSRF | HTTP: a write without the token is refused |
| — market scope | HTTP: a fully permitted person scoped to another market gets 404 and an empty list |
| 6. A stale draft revision is rejected without changing data | Service and HTTP: `STALE_DRAFT`; draft row, content, timestamp and asset table unchanged. Database: a revision that does not advance by exactly one is refused |
| 7. Tampering with a manifest is detected | Four forged candidates (a pinned hash changed; the manifest hash changed; the content changed; an entry removed): each refused with `MANIFEST_MISMATCH`, each refusal audited, none approved. The untouched candidate still verifies |
| 8. Audit integrity | Every transition present in order; the hash chain verifies |
| Supersession | A changed draft supersedes an open candidate; the old approval cannot be used; a draft identical to an approved candidate is not approved |
| Default-deny for speech | A draft whose wording uses a customer field cannot be submitted: `VARIABLE_NOT_PERMITTED` |
| 12. No live-call workflow becomes enabled | With the setting on, exactly the 15 operations are added; none concerns voice, calls, sessions, runs, plans or assignment; every existing route is unchanged |

---

## 6. Verification summary

| Check | Result |
|---|---|
| SS-03A.1 tests (pure domain, fixture parity) | 114 passed |
| SS-03A.2 tests (persistence and governance) | 19 passed |
| SS-03A.3 tests (API and contract) | 13 passed |
| Whole backend suite, after A.1 | 625 passed, 0 failed |
| Whole backend suite, final (after A.2 and A.3) | **657 passed, 0 failed** (511 existing + 146 new) |
| Backend lint, format, strict type check | clean |
| OpenAPI | additive: +15 operations, +22 schemas, 0 changed, 0 removed |
| Frontend type check, lint, unit tests | 0 errors; 0 problems; 403 passed |
| Frontend prototype journeys | 13 of 13 passed |
| Frontend standard Playwright suite (real backend, test database) | 33 of 33 passed |
| Golden fixtures regenerated from their five interpreters | 27 files, byte-identical |

Evidence: `docs/acceptance/evidence/SS-03A/` — `backend_tests.txt`, `survey_tests_by_name.txt`,
`migration_and_rollback.txt`, `fixture_regeneration.txt`, `openapi_additivity.txt`, `frontend_checks.txt`.

**Regression after each step.** After A.1: the whole backend suite (625 passed). After A.2 and A.3: one whole-suite
run covering both (657 passed) — the A.2 step on its own was verified by its own tests plus the A.1 tests (133
passed), not by a separate whole-suite run. One intermediate whole-suite run failed a single test, the
contract-drift check, because I regenerated the contract while that run was in progress; the clean rerun is the
result reported.

---

## 7. Things the owner should know

1. **One existing test expectation was changed.** `tests/test_admin_access.py` asserted the migration head by name;
   it now names `0027_survey_definitions`. No other existing test was altered.
2. **Four existing files have small changes** to carry the setting and the head rule: `app/main.py`,
   `app/api/health.py`, `app/api/admin_access.py`, `app/cli.py`. Behaviour for a schema at the head is unchanged.
3. **The published contract documents routes the default server does not serve.** The export script turns the
   setting on so the client is typed for the new operations. Stated in the script and here.
4. **A real defect was caught by the additivity check.** Three of my response-model names (`FindingOut`,
   `PublishIn`, `SubmitIn`) collided with existing ones, and the generator silently renamed the **existing**
   schemas. I renamed mine with a `Survey` prefix; a test now fails on any such collision.
5. **Two CHECK constraints let a missing value through** as first written (`NULL` satisfies a CHECK). Found by the
   test that tries to store a field without `speakable`; fixed before the suite passed.
6. **The validator is a port of the prototype's rules.** Its agreement with the prototype is proven for what the
   fixtures cover. Rules the fixtures do not exercise (for example interruption policies) are ported by reading, not
   by comparison.
7. **Server validation has blockers only.** The prototype's warnings and information items (a newer approved version
   exists; no stated purpose; the standing no-answer warning; coverage) are not on the server, so there is nothing
   yet for an acknowledgement to refer to. The candidate stores acknowledgements as given.
8. **"Makers" is conservative:** everyone who ever changed the draft, not only those who changed it since the last
   submission.
9. **A draft asset belongs to one survey until it is frozen.** Two surveys cannot edit the same unfrozen version.
10. **Nobody can use the API yet**, by design: no role holds a permission and the setting is off.

---

## 8. Proposed boundary: SS-03B and frontend integration

**Not authorised. Proposals for the owner.**

### SS-03B — execution in simulation (backend)

| In | Out |
|---|---|
| The deterministic execution harness on the server: graph navigation, follow-up queues, rules, decisions, statements, typed answers — specified by all 82 expected runs | Any non-answer behaviour |
| Wording rendering and controlled variables (the mechanism; no field allowlisted) | Any field authorised for speech |
| Call-plan assembly from a version and a fact snapshot — specified by the 14 expected plans | Assignment of surveys to cases |
| Simulation runs recorded apart from operational evidence (owner condition D-80) | Operational runs, delivery, voice |
| The remaining validation severities (warnings, information) and acknowledgements | Live eligibility as a decision |

Blocked until ruled: D-NA-1, D-NA-9, D-NA-13, D-NA-14, D-NA-15, the outcome catalog, gate behaviour.

### Frontend integration (frontend, after SS-03A is accepted)

| Step | Contents |
|---|---|
| FI-1 | Survey Studio reads and writes drafts through the API; conflict handling on `STALE_DRAFT`; the prototype's in-memory store becomes a client of the server |
| FI-2 | Review and publish on the real candidates; server validation shown in Validate |
| Decision needed first | Whether the server gains fine-grained editing operations, or the editor keeps composing documents (as now) |
| Decision needed first | Who holds the four permissions in development, so that anyone can use it |

### Before either

1. Commit SS-03A (owner's authorisation).
2. If the owner wants it in the development environment: authorise migrating the development database (additive,
   with a backup first) and turning the setting on.
3. Business-user UX acceptance and screen-reader sign-off remain open and are not affected by SS-03A.

---

## 9. Changed-file inventory

### Call360-backend (base `7228875`; uncommitted)

**New (13 files):**

| File | Lines |
|---|---:|
| `app/domain/survey/__init__.py` | 9 |
| `app/domain/survey/canonical.py` | 89 |
| `app/domain/survey/conditions.py` | 269 |
| `app/domain/survey/documents.py` | 326 |
| `app/domain/survey/validator.py` | 713 |
| `app/domain/survey/store.py` | 640 |
| `app/api/survey_definitions.py` | 622 |
| `migrations/versions/0027_survey_definitions.py` | 425 |
| `tests/` — `test_survey_domain.py`, `test_survey_store.py`, `test_survey_api.py`, `survey_fixtures.py`, `survey_support.py` | 1,748 |

**Changed (10 files):**

| File | Change |
|---|---|
| `app/main.py` | New head constant; the head-compatibility rule; the router registered only when the setting is on |
| `app/core/settings.py` | `survey_definitions_enabled` (default false), `survey_writes_per_minute` |
| `app/api/health.py` | Readiness uses the accepted heads |
| `app/api/admin_access.py` | System-health migration check uses the accepted heads and says why |
| `app/cli.py` | Two head checks use the accepted heads |
| `app/domain/catalog.py` | Revision 0027 and its nine tables registered for the round-trip test |
| `scripts/export_openapi.py` | The exported contract includes the survey operations |
| `contracts/generated/openapi.json`, `openapi.sha256` | Regenerated |
| `tests/test_admin_access.py` | One assertion: the head's name |

**Not changed:** every Script Studio module, router, table and test; every voice module; every existing migration.

### Call360-frontend (base `a867767`; uncommitted)

Generated files only: `src/api/generated/schema.d.ts`, `src/api/openapi.pinned.json`, `src/api/contract.lock.json`.
No screen, model or test changed.

### Call360-specs (base `b2f81df`; uncommitted)

`04_…` (§9 added), `26_…` (status line only), `27_…` (this report), `README.md` (index), `SESSION_HANDOFF.md`,
`docs/acceptance/evidence/SS-03A/` (six files). The decisions D-176…D-187 were already recorded in `06_…` and
committed in `b2f81df`.

---

## 10. Commits and provenance (owner's Part B)

**Local commits made on the owner's authorisation, not pushed:**

| Repository | Commit | Contents |
|---|---|---|
| Call360-frontend | `a867767` | The eligibility clarification: 5 Survey Studio files |
| Call360-specs | `b2f81df` | Decision closure, SS-03A specification, register D-170…D-187, contract §8.6 and §8.9, regenerated UC-02 evidence: 16 files |

Staged changes were reviewed before each commit: only the intended files; no `.DS_Store`, no environment file, no
temporary artefact; secret scan clean.

**Provenance of the earlier UC-01/UC-02 commits** (`c575f76` frontend, `33fdfce` specs, both 2026-11-21 23:23):

- The commit message is "commit", as on every earlier commit by the owner; the author identity is the same as the
  preceding commits; there is no co-author trailer.
- The local reflog records each as an ordinary `commit`, and the remote-tracking reference records "update by push"
  for each — as it does for the two commits before them.
- `git ls-remote` confirms `origin/main` is at exactly those commits.
- **I did not create or push them**: I ran no `git commit` or `git push` before the two commits in the table above,
  and I have never pushed.
- They were made from this machine by the same identity as the owner's earlier commits. What triggered the push —
  a habit, a tool or an editor action — cannot be determined from git.

Nothing was rewritten, reverted or force-pushed. **The two local commits above are ahead of the remote by one each
and have not been pushed.**
