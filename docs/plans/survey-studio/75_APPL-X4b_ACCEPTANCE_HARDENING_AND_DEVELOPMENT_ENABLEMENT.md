# 75 — APPL-X4b: acceptance, evidence-integrity hardening and development enablement

Date 2026-11-24. Synthetic data only. Nothing committed.
**Status: hardening done and verified on the test schema. Development enablement COMPLETE: preflight stopped for the
owner (§4), the owner authorised proceeding, migration `0041` applied, publication enabled, one policy published by
three people. Awaiting the owner's review.**

---

## 1. Acceptance record

The owner, 2026-11-24: "**APPL-X4b is ACCEPTED as technically verified on the isolated test schema, subject to the
governance-hardening requirement below.**" Development enablement of `0041_applicability_publication` is authorised
"only after the hardening is implemented and verified on the isolated test schema". APPL-X5 is not to begin. No
commits or pushes.

## 2. Owner rulings recorded (D-459 … D-465)

| Ref | Ruling |
|---|---|
| D-459 | APPL-X4b accepted as technically verified on the test schema, subject to D-460 |
| D-460 | **Evidence integrity.** Once a candidate is submitted, any actual change to a supporting suite or scenario revision invalidates that candidate's evidence, even if the content is restored. Validate fingerprints **and** the exact revision identities the qualifying run recorded, at submission, approval and publication. Historical runs stay immutable and reproducible. The evaluator does not change. A change to the separate working policy draft does not invalidate a candidate. Ineligible evidence needs a new qualifying run and a new candidate; the original candidate and its audit history are preserved |
| D-461 | Development identities: only `dev.applicability.author` (submit), `.checker` (approve), `.publisher` (publish), in separate authenticated browser sessions. No new role, grant or identity |
| D-462 | `dev.admin`: membership not to be changed; not to be used in the publication demonstration; effective permissions recorded; least-privilege review stays open |
| D-463 | `SHOWCASE-REGRESSION` and its three recorded runs are preserved as they are. No provenance rewritten; `PROPOSED_FROM_RESULT` never converted; authorship reconstructed from suite history is labelled as such. The demonstration uses a newly recorded, explicitly targeted run |
| D-464 | The demonstration publishes a **dedicated, clearly named synthetic policy**, not an existing showcase policy. Its identity, market, scope and purpose are recorded before a permanent version is created (§5) |
| D-465 | Preflight per D-453, strictly: any materially unexpected difference from the accepted baseline stops the work for explicit owner authorisation, explained or not |

## 3. Evidence-integrity hardening (D-460)

### 3.1 What changed

One service file, `app/domain/survey/applicability/publication.py`. **No schema change, no migration change, no API
shape change, no evaluator change.** Migration `0040` already records the revisions needed
(`applicability_evaluation_run.suite_revision`, `applicability_evaluation_result.scenario_revision`).

- `_recorded_revisions(run)` — the revision identities the run itself recorded.
- `_revision_drift(run, …)` — compares them with the suite's and each scenario's current revision. A revision
  advances only on a real change (an identical save is refused as `NOTHING_CHANGED`) and never goes back, so a
  differing revision proves the item was edited since the run.
- Called from the readiness gate — therefore at **submission** — as `EVIDENCE_OUT_OF_DATE`, and from `revalidate` —
  therefore at **approval** and **publication** — as `EVIDENCE_CHANGED`. Each blocker carries
  `at.reason = REVISION_ADVANCED`, the revision the run recorded and the revision now, and the message "It was edited
  after the run — putting its content back does not make it the revision that was run".
- New candidates also freeze each scenario's revision in `evidence.scenario_fingerprints[].revision`. The check
  itself reads the run's own rows, so it does not depend on that field.

Unchanged by design: a recorded run still reproduces from its own record; the working policy draft may move on after
submission without affecting the candidate.

### 3.2 Test proof — `test_evidence_edited_and_restored_never_regains_eligibility`

| # | Required step | Asserted |
|---|---|---|
| 1 | passing qualifying run | `PASSED`, meaningful for publication |
| 2 | submit | `201`; frozen scenario revisions `[1,1,1,1,1]` |
| 3 | approve | `200` |
| — | (working policy draft edited) | revalidation still empty |
| 4 | change a supporting scenario | content fingerprint differs |
| 5 | restore the content exactly | save accepted |
| 6 | fingerprint matches the original | equal |
| 7 | revision advanced | 1 → 3 |
| 8 | publication still refused | `409 PUBLICATION_BLOCKED`; one detail: `EVIDENCE_CHANGED`, `REVISION_ADVANCED`, run 1, now 3, that scenario |
| 9 | refusal recorded | candidate still `APPROVED`, byte-identical; last event `REFUSED` (step `PUBLICATION`); a `DENIED` audit record; no version |
| — | the old run | still reproduces from its record; **not** accepted for a new submission (`EVIDENCE_OUT_OF_DATE`, submit refused) |
| 10 | new run, new candidate | candidate 2 |
| 11 | three distinct identities | version 1; three different people; its evidence records the scenario at revision 3 |
| — | original candidate | `WITHDRAWN`; events `SUBMITTED, APPROVED, REFUSED, WITHDRAWN`; evidence unchanged |

**Changed-and-restored suite** (same test, part B): the suite is renamed and renamed back — same fingerprint, revision
+2. **Approval** is refused (`EVIDENCE_CHANGED`, `REVISION_ADVANCED`, suite `GATE`), the refusal is recorded, the run is
refused for a new submission, and a new run publishes version 2 with three people.

The earlier test that asserted the opposite ("restored byte for byte is valid again") now asserts the refusal.
Browser journey X4b.4 was changed the same way: after the restore the publisher's screen still shows the problem and
keeps Publish disabled; the author withdraws, records a new explicitly targeted run, submits a new candidate, and
that one is approved and published as version 2.

### 3.3 Regression after the hardening

See §11.

## 4. Development preflight — read-only — stopped, then authorised

Taken 2026-11-24 22:18. Nothing was written to development. Compared with the accepted baseline recorded at the end
of the APPL-X4a enablement (`71_…` §9).

| # | Check | Result |
|---|---|---|
| 1–3 | Database, schema, environment | `Call360_db`, `call360`, `app_env = local`, host `localhost` |
| 4 | Revision | `0040_applicability_scenarios` |
| 5, 6 | Next migration, parent, heads | one head `0041_applicability_publication`, parent `0040_applicability_scenarios` |
| 7 | Tables and objects | 154 tables, 158 triggers, 71 functions, 57 permissions; column and constraint digests identical to the baseline; no table added or removed |
| 8 | Showcase surveys | five surveys and module `M-100019`, `PUBLISHED` v1 1.0, fingerprints identical |
| 9 | Library | 32 versions (31 `PUBLISHED`, 1 `SUPERSEDED`), digest `75ca7466…7a43acbc`, identical; no open draft or candidate |
| 10 | Saved policies | `SHOWCASE-DEPENDENCIES` revision 6, `SHOWCASE-ILP-NFTF` revision 10 — identical (all three digests) |
| 11 | Scenarios and suite | six `SHOW-*` scenarios, suite `SHOWCASE-REGRESSION` revision 4 — identical |
| 12 | Recorded runs | three (passed, failed, passed), identical |
| 13 | Roles, grants, memberships | 13 roles, 87 grants (digest `bda6e0cb…83258a10`), 15 group-role mappings, 14 memberships — identical. `dev.admin` unchanged: `LOCAL_ADMIN` and `LOCAL_DEV_APPL_AUTHOR_SG`; effective applicability permissions `read`, `edit` |
| 14 | Retention-managed state | session, media and transcript tables identical; no purge since the baseline |
| 15 | Conflicting objects | no APPL-X4b table or function present |
| 16 | Safe migration state | the development API server is running; it would be stopped first |

### 4.1 Differences from the accepted baseline

147 of 154 tables are identical in row count and content digest. Seven differ, all from one sign-in:

| When | Who | What | Tables |
|---|---|---|---|
| 20:47:24 | `dev.admin` | signed in | `auth_session`, `login_attempt`, `refresh_token`, `refresh_token_family` +1 each |
| 20:47:54 – 20:50:47 | `dev.admin` | created **15 survey simulations** with **38 simulation inputs** | `survey_simulation` 29 → 44, `survey_simulation_input` 68 → 106 |
| | | the audit records of the above | `audit_event` 3,993 → 4,047 (+54: 1 sign-in, 15 created, 38 inputs) |

I did not make these and I have not looked inside them beyond counts and audit actions. They are in Survey Studio's
simulation tables, which migration `0041` does not touch, and no applicability object, role, grant or membership
changed.

**Per D-453 I am not treating that explanation as authorisation.** No backup, migration, setting or record has been
made in development. The question for the owner is in §4.2.

### 4.2 The owner's decision (2026-11-24)

Asked exactly that. The owner: "I authorize proceeding with APPL-X4b development enablement using the current
development database state as the new accepted baseline. The 15 survey simulations and their 38 inputs created by
dev.admin must be preserved exactly." With conditions, all met below: include them in the inventory and backup; record
identifiers, counts and fingerprints; confirm the other checks remain clean; after migration verify they are
unchanged; never delete, reset, modify or recreate them; stop again on any further materially unexpected difference.
The demonstration policy identity in §5 was confirmed: "Use as planned".

**Re-check immediately before the backup** (development API stopped first): 154 tables, 18,435 rows; no table, object,
role, grant, library, policy or showcase difference from the 22:18 preflight. No further unexpected difference
appeared at any later step.

**The preserved simulations:** 15 simulations, 38 inputs. Whole-table fingerprints: `survey_simulation` 44 rows
`697424ed…7c9ba8ce`; `survey_simulation_input` 106 rows `e164bf84…b8fc0a7b`. Each simulation's identifier, creation
time, row fingerprint, input count and input fingerprint are in the backup manifest and in
`docs/acceptance/evidence/APPL-X4b/development/preserved-simulations-fingerprints.json`.

## 5. Demonstration policy (D-464) — recorded before anything was created

| | |
|---|---|
| Code | `GOV-DEMO-ILP-NFTF` |
| Name | "Governed publication demonstration — ILP and NFTF (synthetic)" |
| Market | `SG` |
| Profile | New business application (published library profile) |
| Scope | none beyond the profile; four requirements: ILP → Survey A; NFTF → Survey B; ILP with NFTF → Survey C replacing A and B; replacement sale → Survey D |
| Dependencies | 16 exact pins: 4 published Survey Studio versions (`S-APPL-DEMO-ILP`, `-NFTF`, `-COMBINED`, `-REPLACEMENT`, v1 1.0), 3 published conditions, 4 published variables, 5 published profiles |
| Scenarios | six new `GOV-*` scenarios |
| Suite | `GOV-DEMO-REGRESSION`, publication-gating |
| Purpose | to show once, in development, that three separate people can submit, approve and publish. Configuration only: nothing reads it to select a survey for a case |
| Permanence | exactly one published version |

How it was made: the policy document was **copied by value** from `SHOWCASE-ILP-NFTF` (which was only read) with its
own name and description. The six scenarios were created through the application's API from the signed-in author's
browser session. The suite was built **on the screen**, and each of the six expected outcomes was stated and confirmed
on the screen by `dev.applicability.author`.

## 6. Backup (before any change)

- `_db_backups/call360_dev_before_0041_20261124.dump` in the workspace parent, outside every repository; mode 600;
  2,407,124 bytes.
- SHA-256 `31fb48f8809c7ff204034ccd49e2e0b9ed81f08a12b98e3d0c5a15e298c3e86a`.
- 154 tables, 154 table-data entries; **18,435 rows in the archive = 18,435 in the inventory; no per-table mismatch**.
- `pg_restore` to SQL: readable, clean.
- Manifest `call360_dev_before_0041_20261124.manifest.json`: every table's row count and content digest; grants,
  library and policy digests; the 15 preserved simulations.
- `_db_backups/RESTORE.md`: new section "Rolling 0041 back". No reset, truncate or re-seed.

## 7. Migration `0041` — completion

`uv run alembic upgrade 0041_applicability_publication`; revision now `0041_applicability_publication` (head).

| Added | |
|---|---|
| Tables (4) | `applicability_policy_candidate`, `…_candidate_dependency`, `…_candidate_event`, `applicability_policy_version` |
| Guard functions (4), triggers (4), all enabled | candidate, dependency, event, version |
| Three-person identity | CHECK `ck_applicability_candidate_checker`, `ck_applicability_candidate_publisher`, `ck_applicability_candidate_shape` — validated |
| One open candidate per policy; one published version per policy | partial unique indexes `uq_applicability_candidate_open`, `uq_applicability_policy_published` |
| Foreign keys | all validated; schema-wide constraints not validated: 0; disabled triggers: 0 |
| Permissions, roles, grants | none added: 57 permissions, 13 roles, grants digest `bda6e0cb…83258a10`, 14 memberships — identical |

Removed or altered: nothing. **Immediately after:** 153 of 154 existing tables identical in row count and content
digest; the one difference is the value in `alembic_version`. The four new tables empty. The 15 simulations and 38
inputs identical. Immutability, transitions and append-only behaviour of the guards are proven by the test-schema
migration test (`73_…` §7) and were exercised for real in §9.

## 8. Feature settings

- Names confirmed in the code first: backend `applicability_publication_enabled`
  (`APPLICABILITY_PUBLICATION_ENABLED`); frontend `VITE_APPLICABILITY_PUBLICATION`.
- Backend `.env`: `APPLICABILITY_PUBLICATION_ENABLED=true` added; library, policies and scenarios settings kept.
  `/health/ready` → `200`.
- Frontend started with the five earlier settings plus `VITE_APPLICABILITY_PUBLICATION=1`.
- Authorisation: a publication route without sign-in → `401`; with the wrong role → `403` (§9, F).

## 9. Development demonstration — real browser, development database, three separate sign-ins

Identities: `dev.applicability.author`, `dev.applicability.checker`, `dev.applicability.publisher`, each in its own
browser session. **`dev.admin` was not used** (no audit record by it since the baseline). No role, grant or
membership changed. Screens: `docs/acceptance/evidence/APPL-X4b/development/screens/` (15).

| Journey | Result | Screens |
|---|---|---|
| Setup | policy, six scenarios, gating suite; six expectations stated on the screen; stored `AUTHORED`, each with the server's author stamp | `01` |
| A readiness | With no evidence chosen: **Not ready**, blocker `SUITE_REQUIRED`, nothing preselected. After the author chose the explicitly targeted run (`DRAFT`, revision 1; passed 6 of 6): ready; revision 1; 16 pinned dependencies; 6 of 6 expectations independently authored; coverage meaningful; run fingerprint shown | `02`, `03` |
| B author submits | Fingerprints confirmed on the screen, then submitted. Candidate 1's document, manifest and evidence fingerprints equal what was shown. `PUT` / `PATCH` / `DELETE` on it → `405`. The working draft was then edited (revision 2): the candidate did not change | `04` |
| C checker approves | A separate session: frozen candidate, the four survey selections, evidence, six provenance rows; approved by its fingerprint. The checker's own attempt to publish → `403`; no publish control shown | `05`, `06` |
| F evidence edited **and restored** | Scenario `GOV-NEITHER` edited and put back exactly: fingerprint `03848af6…` → `6892cc80…` → `03848af6…` (identical to the original); revision 1 → 3. The publisher's screen shows the problem and keeps Publish disabled; the API answers `409 PUBLICATION_BLOCKED` / `EVIDENCE_CHANGED` / `REVISION_ADVANCED` (run revision 1, now 3). Candidate unchanged; refusal in its history; no version. The author withdrew it with a reason. The old run offered again as evidence → `EVIDENCE_OUT_OF_DATE` | `07`, `08`, `09` |
| B, C again | A **new** explicitly targeted run (`DRAFT`, revision 2; passed 6 of 6) → candidate 2 → approved by the checker | `10`, `11` |
| D publisher publishes | A third session: "Revalidated just now", confirms fingerprint and "version 1", publishes | `12`, `13` |
| E published version | Version 1 `PUBLISHED`. Document equals candidate 2's; the working draft, edited again afterwards (revision 3), is different. Manifest and evidence-run fingerprints shown. Submitted by Dev Applicability Author, approved by Dev Applicability Checker, published by Dev Applicability Publisher — three distinct people. **Verified from the frozen record: fingerprints intact, identical to its candidate, evidence reproduced 6 of 6.** After publication the suite builder asks for a run target and a run without one is refused (`TARGET_REQUIRED`) | `14`, `15` |

**Negative controls (F), all refused:**

| Attempt | Answer |
|---|---|
| author approves own candidate | `403` |
| publisher approves | `403` |
| checker submits | `403` |
| publisher publishes before approval | `NOT_APPROVED` |
| checker approves with an invalid fingerprint | `MANIFEST_CHANGED` |
| checker publishes what they approved | `403` |
| publisher publishes with an invalid fingerprint · a wrong version number | `MANIFEST_CHANGED` · `VERSION_CHANGED` |
| author publishes | `403` |
| changed-and-restored scenario revision | `EVIDENCE_CHANGED` / `REVISION_ADVANCED` |
| another market | `MARKET_NOT_IN_SCOPE`; unknown version `404` |
| change or delete a published version | `405`, `405` |

Histories as recorded: candidate 1 — `SUBMITTED, REFUSED, REFUSED, APPROVED, REFUSED, WITHDRAWN`; candidate 2 —
`SUBMITTED, APPROVED, REFUSED, REFUSED, PUBLISHED`. Five refused transitions are in the security audit as `DENIED`.

**Shown on the test schema only, not repeated in development** (to avoid extra permanent records, as instructed):

| Control | Where |
|---|---|
| a superseded published dependency stays valid when intact (notice `NEWER_VERSION`, never upgraded) | backend `test_every_readiness_blocker_is_named_with_its_remedy` §4.2 |
| missing or unpublished dependency; changed draft dependency | same test; browser X4b.3 |
| `PIN_DIFFERS`, no override | same test; browser X4b.3 |
| all expectations result-derived; one behaviour only result-derived | same test; browser X4b.3 |
| changed-and-restored **suite** | `test_evidence_edited_and_restored_never_regains_eligibility` part B |
| supersession by a version 2; impact between versions | browser X4b.4, X4b.5 |

**Existing records, read only:** `SHOWCASE-DEPENDENCIES` readiness → `SUITE_REQUIRED`. `SHOWCASE-ILP-NFTF` with its
historical passing run → `EVIDENCE_OUT_OF_DATE` (a scenario has moved since); its six expectations read `AUTHORED`
with authorship **reconstructed from suite history** (`SUITE_HISTORY`, shown as such) — nothing was rewritten or
converted.

Honest notes:

- The two qualifying runs were recorded through the application's API from the author's signed-in session, with an
  explicit `DRAFT` target: before any candidate or version exists the suite builder does not show the target chooser
  (it appears once one exists — screen `15`).
- The negative controls are API requests made from each person's own signed-in browser session, plus the screens
  noted.
- My demonstration script stopped twice on its own reporting lines (not product faults) and was resumed from the
  recorded state; nothing was repeated or undone.
- One scenario of the demonstration (`GOV-NEITHER`) is at revision 3 with its original content; the working draft of
  the policy is at revision 3 and differs from the published version by its description only. Both deliberate.

## 10. Integrity comparison (pre-migration baseline → after the whole demonstration)

**Unchanged:** 138 of 154 existing tables, identical in row count and content digest — including every legacy
assignment, script, case, callback, session, call-plan, composite-plan, coordinated-simulation, evaluation, finding
and review table (59 checked, none changed apart from sign-in sessions). The 15 preserved simulations and all 44
simulations and 106 inputs: identical fingerprints. Roles, grants, group-role mappings and 14 memberships: identical.
All 32 library versions and the five showcase surveys with the module: identical. `SHOWCASE-ILP-NFTF` (revision 10)
and `SHOWCASE-DEPENDENCIES` (revision 6): identical. The six `SHOW-*` scenarios, `SHOWCASE-REGRESSION` (revision 4)
and its three runs (`1765a066…`, `d482a39d…`, `fbd6b5da…`): not written — no event on any of them since the baseline.

**Changed, all expected:**

| Table | Before → after | Why |
|---|---|---|
| `alembic_version` | value | the migration |
| `applicability_policy_candidate` / `_dependency` / `_event` / `applicability_policy_version` | 0 → 2 / 32 / 11 / 1 | two candidates (one withdrawn, one published), one version |
| `applicability_policy`, `_dependency`, `_event` | 2 → 3, 24 → 40, 16 → 19 | the new policy and its three saves |
| `applicability_scenario`, `_dependency`, `_event` | 6 → 12, 50 → 98, 14 → 24 | six new scenarios; the edit and restore |
| `applicability_suite`, `_member` | 1 → 2, 6 → 12 | the new suite |
| `applicability_evaluation_run`, `_result` | 3 → 5, 18 → 30 | the two new runs |
| `audit_event` | 4,047 → 4,087 | 25 by the author, 7 by the checker, 8 by the publisher; none by anyone else |
| `auth_session`, `login_attempt`, `refresh_token`, `refresh_token_family` | +9 each | the sign-ins of the demonstration (resumed twice) and of two read-only looks as the author |

No case, sale, customer, callback, session, plan, assignment rule, binding, requirement group or script record was
created or changed.

## 11. Regression

One run, on the final source (the hardened code; no source change after it), 2026-11-24. Test schema; the browser
suites one at a time.

| Check | Result |
|---|---|
| Backend suite — includes the evaluator tests, security and market-isolation tests, migration tests, the golden 82 survey runs and 14 plans | **1096 passed**, 0 failed |
| ruff · ruff format · mypy (140 files) | clean |
| OpenAPI | regeneration changes nothing; SHA-256 `078ad52f8eded9bbc389b28edd029f961ce234494d984c46d9347fc6c75a259d` — unchanged by the hardening |
| Frontend contract check · lint · types · unit (636) · production build | pass |
| Playwright publication | 7 passed |
| Playwright scenarios | 11 passed |
| Playwright applicability | 26 passed |
| Playwright persisted | 34 passed |
| Playwright prototype | 13 passed |
| Playwright standard (with the shell accessibility test) | 34 passed |
| Specs validator | pass |
| Golden fixtures and expectations | no file changed |
| Evaluator (`logic.py`, `evaluator.py`, `analysis.py`), `policies.py`, `rule_engine.py`, `answer_evaluation.py`, `finding_engine.py` | not modified |
| Development database integrity | §10 |

- **X3.8 (canvas of 100 on screen):** passed in this run and in the previous full run; it failed once earlier today
  with no change to that screen. Still **under watch, not closed**.
- **Voice Studio timing defect:** open; the voice tests passing here does not close it.
- No test weakened, no timeout raised, no golden expectation changed. Two tests were **changed on purpose** to assert
  the owner's new rule in place of the old behaviour (the backend restore assertion and browser journey X4b.4), and
  one test was added.
- Logs: `docs/acceptance/evidence/APPL-X4b/test-output/hardened/`.

## 12. Open items

- `dev.admin` least-privilege review (D-462): open. Effective applicability permissions `read`, `edit`.
- X3.8 canvas-visibility test: under watch (§11).
- Voice Studio timing defect: open, untouched.
- Not measured or claimed: usability targets that need people; screen-reader testing; WCAG conformance.
- APPL-X5 readiness assessment: `76_…`. Not authorised; nothing built.
