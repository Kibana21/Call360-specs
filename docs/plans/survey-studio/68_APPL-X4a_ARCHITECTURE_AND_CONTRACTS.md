# 68 — APPL-X4a: persistent Scenario Studio, regression suites and recorded evaluation evidence

**Architecture and contracts.** Date 2026-11-24. Synthetic data only. Simulation only.
**Authorisation:** the owner's "APPL-X4a — Persistent Scenario Studio, Regression Suites and Reproducible Evaluation
Evidence" (2026-11-24): implementation **on the isolated test schema only**. Not authorised: applying the migration to
development, APPL-X4b, APP-1a, OPS-1, VOICE-1, legacy retirement, commits.

---

## 1. Owner decisions recorded (D-427 … D-434)

| Ref | Decision | How it is implemented here |
|---|---|---|
| Acceptance | APPL-X3 development enablement accepted; `0039` is the development baseline | D-427 |
| Q-1 | APPL-X4 split: X4a (this) then X4b; separate migrations | `0040_applicability_scenarios` here; `0041_applicability_publication` reserved for X4b (`70_…`) |
| Q-2 | A published policy needs an attached, passing, **meaningful** suite; no arbitrary count; a suite of only unresolved outcomes cannot qualify | coverage report with `meaningful_for_publication` and the reason when it is not (§6) |
| Q-3 | Gating scenarios must reconcile profile versions; exploratory acknowledgement possible in X4b | scenario `purpose` and suite `purpose` in the data model; a gating run marks a mismatch `INVALID_DEFINITION` (§5.3) |
| Q-4 | No `PIN_DIFFERS` override; evaluator's exploratory semantics unchanged | evaluator untouched; blocker specified for X4b |
| Q-5 | A genuinely published version stays usable after it is superseded; notice, no silent adoption | `PUBLISHED` and `SUPERSEDED` versions both valid pins; `NEWER_VERSION` notice; `67_…` corrected |
| Q-6 | Prototype endpoints retire only after every caller has migrated | **not retired**; remaining callers listed in §9 |
| D-418 | Close the reproduced creation race as fixed; original failure not conclusively matched; watch | D-433; the same rule applied here (nothing can be created before its list is read) |

## 2. Concepts

- **Scenario** — one saved synthetic application: profiles, typed facts, and the exact library definitions that give
  those facts their meaning. A fact is a value, `null` (**not known**) or absent (**not provided**) — three states.
- **Variant** — a scenario that names another as its `baseline`. A real saved scenario, not a view.
- **Suite** — an ordered regression dataset **for one policy**. Each member carries the outcome a person **expects**.
- **Run** — immutable evidence of one evaluation of a suite against one saved policy revision.
- **Purpose** — a scenario is `REGRESSION` or `EXPLORATORY`; a suite is `PUBLICATION_GATING` or `EXPLORATORY`. A gating
  suite holds regression scenarios only.

There is no field for a customer, an operational policy number, a case or a session anywhere. `record_class` is always
`SYNTHETIC` (a CHECK constraint).

## 3. Migration `0040_applicability_scenarios` (parent `0039_applicability_policy`)

Additive: seven tables, six guard functions, **no permission**, no existing object altered.

| Table | Holds | Key constraints |
|---|---|---|
| `applicability_scenario` | identity (market, code — immutable), `purpose`, optional `policy_id`, optional `baseline_id`, one working draft (`document`, `snapshot`, both fingerprints, `draft_revision`), `archived_at` | unique (market, lower(code)); FK policy, FK baseline; never deleted; revision monotonic; a changed draft is a new revision |
| `applicability_scenario_dependency` | the snapshot as rows: variable / profile, exact published version **or** draft revision, content and manifest fingerprints | FK `applicability_asset`, FK `applicability_asset_version`; shape CHECK; guard: same market, right kind, version is `PUBLISHED` or `SUPERSEDED` with that number |
| `applicability_suite` | identity, `policy_id` (immutable), `purpose`, document, fingerprint, `draft_revision`, `archived_at` | FK policy; guard: policy of the same market |
| `applicability_suite_member` | scenario, position, `expectation` | FK suite, FK scenario; unique per suite; guard: same market |
| `applicability_scenario_event` | append-only history of scenarios and suites | exactly one of scenario / suite; UPDATE and DELETE refused |
| `applicability_evaluation_run` | the recorded run: suite and policy identities and revisions, policy document / snapshot / evaluator fingerprints, status, counts, `coverage`, the frozen `record`, `record_sha256`, `run_sha256`, idempotency key | FK suite, FK policy; unique (suite, idempotency key); counts CHECK; **INSERT only** |
| `applicability_evaluation_result` | per scenario: the scenario document and snapshot **as they were**, the expectation, the complete plan, verdict, differences, diagnostics | PK (run, position); FK run, FK scenario; **INSERT only**; never more rows than the run recorded |

14 validated foreign keys. Downgrade refuses while a scenario, a suite or a run exists. Used only when
`applicability_scenarios_enabled` is on (and policies and the library are). `MIGRATION_HEAD` is `0040`; a schema at
`0039` is accepted while the setting is off — which is the state of local development.

## 4. Exact snapshots and reproducibility

### 4.1 What a scenario pins

Every variable a fact is given for, and every profile (with everything it extends), at an exact published version, or
at an exact draft revision when not published. The server completes and validates the pins on every save; the stored
document carries them. The snapshot records per dependency: asset id, kind, version id, version number, content
fingerprint, manifest fingerprint. `scenario_fingerprint = sha256(document + snapshot)`.

- A newer published version never changes a saved scenario. It is reported (`NEWER_VERSION`); adoption is an edit of
  the pin — deliberate and undoable.
- A pinned **draft** that has since moved: its earlier content is not kept, so the scenario is reported
  `STALE_DEPENDENCY`, is **not evaluated**, and must be reconciled. Reproducibility is never claimed for it.

### 4.2 The four kinds of evaluation, and how each is labelled

| Kind | `mode` / `policy_source` | `reproducible` |
|---|---|---|
| Saved scenario, saved policy revision, published definitions | `SAVED_SCENARIO` / `SAVED` | true |
| Saved scenario used in a recorded run | recorded; verifiable from the record | per result |
| Unsaved scenario, or unsaved edit of the policy | `EXPLORATORY` and / or `PREVIEW`; the resolved identities and fingerprints are returned | false |
| Stale or invalid dependency | `COULD_NOT_EVALUATE` / `INVALID_DEFINITION`, with the reason; no plan | false |

### 4.3 How a scenario meets a policy

One evaluation uses **the policy's** pinned variables and conditions (D-420: one variable version per evaluation) and
**the scenario's** pinned profiles — profiles describe an application and never decide applicability.

- Variable version differs → `VARIABLE_VERSION_DIFFERS` (information); the policy's definition decides.
- Profile version differs → `PROFILE_VERSION_DIFFERS`; in a publication-gating run the result is `INVALID_DEFINITION`
  ("reconcile"), never a pass; in an exploratory evaluation the scenario's version is read and the difference shown.

### 4.4 What a run freezes

`record`: the policy document, its dependency manifest and **the definitions the evaluator read**; the suite as run
(members, revisions, expectations); the evaluator contract. Each result: the scenario document and snapshot, the
profile definitions read, the expectation, the complete plan. `run_sha256` covers the record, the verdicts, the plan
fingerprints and the coverage.

`verify` re-evaluates a run **from the record alone** — the library is not read — and compares every plan fingerprint
and verdict. This is what "reproducible" means here.

## 5. Expectations, verdicts, runs

### 5.1 Expectations are stated by a person

`{status, selected:[{code, version}], pending:[code], replaced?:[requirement], needs?:[variable], note, source,
confirmed}`.

- `confirmed` must be `true`, or the save is refused (`EXPECTATION_NOT_CONFIRMED`).
- The server never fills an expectation in from a result and never rewrites one when the policy changes.
- "Use the current result as a proposal" is a client convenience: it fills the form **unconfirmed**; saving is blocked
  until the person confirms. `source: PROPOSED_FROM_RESULT` is stored and written to the suite's history, so a later
  reviewer can see which expectations began as a result.
- `reviewed_at_revision` records the scenario revision at which the expectation was last stated; a later change of
  the scenario is flagged `SCENARIO_CHANGED`.

### 5.2 Verdict per scenario

| Verdict | When |
|---|---|
| `PASSED` | status equal; selected surveys equal as a set, each at the expected version; pending equal; stated `replaced` and `needs` hold. A deliberately expected `UNRESOLVED` passes |
| `FAILED` | any difference — each one listed with its kind, text, expected, actual and the requirements involved |
| `COULD_NOT_EVALUATE` | stale dependency, blocked policy, evaluator error |
| `INVALID_DEFINITION` | invalid pin; profile mismatch in a gating suite |
| `NO_EXPECTATION` | nothing stated: it can neither pass nor fail |

### 5.3 Run status

`INVALID_DEFINITION` if any result is invalid or has no expectation; else `COULD_NOT_EVALUATE` if any could not be
evaluated; else `FAILED` if any failed; else `PASSED`. Inability to evaluate is never a pass.

### 5.4 Idempotency and bounds

- A run needs a client `idempotency_key`; the same key for the same suite returns the run already recorded
  (`replayed: true`).
- A suite holds at most **200** scenarios; one evaluate call at most **60**; a scenario at most 400 facts; lists page
  at most 100; a run's results page at most 100, and each full plan is read on its own. A record above 48 MB is
  refused (`RUN_TOO_LARGE`).

## 6. Coverage

Read from the plans the evaluator returned — requirement level and condition level:

- per requirement: how often it applied, did not apply, was not known; whether what it replaces was replaced; which
  alternatives were chosen; per condition leaf how often true / false / not known;
- gaps, as suggestions: never applies, never does not apply, replacement not exercised, alternative not chosen, scope
  not exercised, shared survey not exercised, condition branch never true / false / not known.

`meaningful_for_publication` is true only when the suite is publication-gating, **the run passed**, at least one
passing scenario has a resolved result that selects a survey, at least one passing scenario shows a requirement that
does not apply, not every result is unresolved, and no requirement-level gap remains. Otherwise `why_not_meaningful`
says why. `exhaustive` is always `false`, and the label always says that this describes the scenarios run and does not
prove every possible application.

## 7. Operations (22, under `/api/v1/applicability`)

| | Operation | Needs |
|---|---|---|
| Scenarios | `GET /scenarios` (paged; filters policy, text, purpose, baseline, suite, archived) | read |
| | `POST /scenarios` · `GET /scenarios/{id}` · `PUT /scenarios/{id}/draft` · `POST …/archive` · `POST …/restore` | edit (GET: read) |
| | `POST /scenarios/inspect` · `POST /scenarios/evaluate` · `POST /scenarios/compare` | read |
| Suites | `GET /suites` · `POST /suites` · `GET /suites/{id}` · `PUT /suites/{id}/draft` · `POST …/archive` · `POST …/restore` | edit (GET: read) |
| Runs | `POST /suites/{id}/runs` | edit |
| | `GET /runs` · `GET /runs/{id}` (paged results, filter by outcome) · `GET /runs/{id}/results/{position}` | read |
| | `POST /runs/compare` · `POST /runs/{id}/verify` · `POST /runs/{id}/against-current` | read |

Every operation also needs `survey.read`. No new permission, no role change. Market-scoped (another market answers
404). Writes and computations are CSRF-protected; saving and computing have separate rate limits; every write is
audited with the real signed-in identity. There is no operation that changes or deletes a run.

Refusal codes added: `LOOKS_LIKE_REAL_DATA`, `UNKNOWN_REFERENCE`, `INVALID_DEPENDENCY_PIN`, `IN_SUITE`,
`IN_GATING_SUITE`, `EXPLORATORY_IN_GATING_SUITE`, `EXPECTATION_NOT_CONFIRMED`, `INVALID_EXPECTATION`,
`SUITE_TOO_LARGE`, `EMPTY_SUITE`, `INVALID_KEY`, `RUN_TOO_LARGE`, `OTHER_MARKET`.

### 7.1 Comparison (foundation for APPL-X4b)

- two saved scenarios against one saved policy: changed facts, and the selection difference with the requirements
  that are the reason;
- two recorded runs: policy and dependency changes; per scenario changed facts, changed expectation, verdict change,
  surveys added / removed / at another version, newly pending, newly unresolved, now resolved;
- a recorded run against the policy's **current saved draft**: evaluated now, **not recorded**, and labelled so.

Draft-versus-published impact is **not** claimed: no published policy version exists until APPL-X4b. The comparison
structure is the one X4b will reuse.

## 8. Synthetic only

- Structured fields: a fact is accepted only for a variable of the library; unknown document keys are dropped.
- Text fields (names, descriptions, notes, text facts): refused when they look like a national identity number, an
  e-mail address, a policy or account number, or a long digit string (`LOOKS_LIKE_REAL_DATA`). This is a pattern
  check, not proof — the interface also says, on every studio page, never to enter a real detail.
- No foreign key, column or operation reaches a case, a sale, a customer, a session or an assignment object.

## 9. Frontend

Setting `VITE_APPLICABILITY_SCENARIOS=1` (with saved policies) makes step 4 the persisted **Scenario studio**; without
it step 4 is the accepted in-tab lab, unchanged.

- **Scenarios** — paged, searchable list; guided creation (blank, from a profile, from a template, a copy, a variant,
  a generated combination; name before the permanent code; purpose); editor with a save bar, undo / redo, type-aware
  facts defaulting to *only the facts this policy reads*, the pinned dependencies with adopt / accept, the live result
  from the server labelled saved-and-reproducible or exploratory, survey path and published-survey preview, variant
  comparison, add to a suite, history, archive.
- **Regression suites** — cards with last result; builder with ordered members, expected against actual, explicit
  expectation editor, proposals that must be confirmed, run and record, coverage with suggestions, clone, compare
  with another suite, history.
- **Recorded runs** — history; a run as recorded with its fingerprints; expected and actual per scenario; full
  recorded result; re-evaluate from the record; compare with another run or with the current draft.

**Prototype operations still called (Q-6, not retired):** `prototype/scenarios` (generated combinations),
`prototype/condition-test` (Condition Lab), `prototype/analyse` and `prototype/evaluate` (in-tab policies, i.e. any
environment without saved policies, and the designer's quick examples).

**Known limitation, stated in the interface:** the designer's live-preview picker still uses in-tab example
applications; saved scenarios live in the studio. The "where things are kept" panel says so.

## 10. Not in this checkpoint

Policy candidates, approval, published policy versions, supersession, publication blockers (`70_…`); any operational
reading of a policy; restoring an archived scenario or suite from the screen (the API has it); a second variable
version inside one evaluation.

## Addendum 2026-11-24 — owner rulings at acceptance (D-438 … D-446) and development enablement

- **Accepted** as technically verified on the test schema (D-438); **applied to local development** (`71_…`).
- **Evaluation model confirmed (D-439), with one tightening now implemented.** A variable-version difference stays
  informational **only while the value given is type-valid and value-valid under the policy's pinned definition**.
  Another type, another currency, or a value the policy's definition does not allow is `VARIABLE_VERSION_INCOMPATIBLE`:
  shown everywhere, and in a publication-gating run the result is `INVALID_DEFINITION` — never a pass, even when
  "unresolved" was the expected outcome. Regression test added (`test_what_cannot_be_evaluated_never_passes`).
- **Limits are safety limits, not capacity guarantees (D-440).** 200 scenarios a suite; 60 scenarios a live
  evaluation request; 100 items a page; 400 facts and 20 profiles a scenario; 48 MB a run record. They are constants
  validated on every request (`scenarios.py`), each refused with its own code. They were chosen from the measurements
  in `69_…` §7 and are **not to be raised without measured evidence**. Making them deployment settings is a small
  change that has not been asked for.
- **Carry-forward implemented in the frontend, no API change:**
  - archived scenarios and suites are listed on request and restored from the screen, with who archived, why, the
    history and a confirmation (existing restore operations);
  - the designer has a read-only "Saved scenarios" picker: a saved scenario's facts and the server's result for it,
    labelled saved or preview; the quick in-tab examples are unchanged;
  - unsaved edits of a scenario or a suite are kept while moving around the product in the same tab, and the save bar
    still says they are not saved.
- OpenAPI unchanged by these additions.

### Designer integration contract (for APPL-X4b's integration work)

| Step | What | Status |
|---|---|---|
| 1 | Read-only look at a saved scenario from the designer (`POST /scenarios/evaluate` with `scenario_id`, and `policy_document` while the policy has unsaved edits) | **done** |
| 2 | The live-preview picker lists saved scenarios of the policy beside the quick examples, clearly grouped | proposed |
| 3 | Requirement and survey inspectors ("in the saved scenarios") read saved scenarios | proposed |
| 4 | Quick examples become optional starting points that are saved as scenarios; `prototype/evaluate` then has no caller in a saved-policy configuration | proposed; precondition of retiring that endpoint (D-446) |

Steps 2–4 change accepted designer behaviour and journeys, so they are left for a reviewed checkpoint.

