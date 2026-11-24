# 72 — APPL-X4b: governed Applicability Policy publication — architecture and contracts

**As built on the isolated test schema.** Date 2026-11-24. Synthetic data only.
**Authorisation:** the owner's "APPL-X4b — Governed Applicability Policy Publication, Immutable Candidates and
Three-Person Approval" (2026-11-24): implementation **on the isolated test schema only**. Not authorised: migration
`0041` on development, the remaining designer integration (steps 2–4), APPL-X5, APP-1a, OPS-1, VOICE-0, VOICE-1,
Genesys, legacy retirement, commits.
**Specification implemented:** `70_…` with rulings D-441 … D-446, and D-452 … D-456 below.

A published Applicability Policy is a governed configuration artefact. Nothing in this checkpoint selects a survey for
a real case, plans a callback or starts a session.

---

## 1. Decisions recorded with this checkpoint

| Ref | Decision |
|---|---|
| D-452 | APPL-X4a development enablement **accepted**; baseline `0040_applicability_scenarios`. Covers synthetic authoring, testing and recorded evidence; authorises no operational selection or calling |
| D-453 | **Procedural exception recorded.** The APPL-X4a development preflight found changed group membership, a re-saved policy, a survey draft and retention-purged records, and I proceeded because they were explained. Rule for all future migrations: complete preflight before any mutation; compare with the latest accepted baseline; list every unexpected difference; **stop and obtain owner approval for materially unexpected state even when a likely cause is identified**; an explanation is not authorisation; never overwrite, reverse or repair user changes; preserve retention and security audit evidence |
| D-454 | Q-g: the remaining designer integration is a **separate checkpoint**. The read-only saved-scenario picker stays; steps 2–4 are not built here |
| D-455 | Q-h: a suite run **must name its target** once a candidate or a published version exists: the saved draft at its revision, a frozen candidate, or a published version by number — with status and both fingerprints shown. No silent default. Every recorded run identifies its exact target |
| D-456 | One small shared-shell correction authorised: accessible names for the icon-only navigation links and the account button, with an automated test at 390 px and at the breakpoint; no layout change; no other shell change; no claim of full WCAG conformance from automated scans |

## 2. Migration `0041_applicability_publication` (parent `0040_applicability_scenarios`)

Additive: four tables, four guard functions, **no permission**, **no existing object altered** — in particular the
accepted `applicability_policy_event` constraint is untouched (D-444).

| Table | Holds | Integrity |
|---|---|---|
| `applicability_policy_candidate` | the frozen submission: policy, market, number, saved revision, `document`, `manifest` (dependency snapshot **and the definitions**), `evidence` (run identity and fingerprints, suite fingerprint, coverage, independence verdict, provenance table, scenario fingerprints, the version it would replace), `candidate_sha256`; lifecycle columns | FK policy, FK evidence run; guard on insert: same market, status `SUBMITTED`, the evidence run is a run of that policy at that fingerprint; guard on update: **every frozen column immutable**, only the allowed transitions, a recorded decision never rewritten; never deleted; partial unique index: one open candidate per policy |
| | three-person rule | CHECK `decided_by <> submitted_by`; CHECK `published_by` different from both; shape CHECK per status |
| `applicability_policy_candidate_dependency` | the manifest as rows | FK candidate, `applicability_asset`, `applicability_asset_version`, `survey_definition`, `survey_version`; **no shape for a draft**; guard: own market, library version `PUBLISHED` or `SUPERSEDED` at that fingerprint; insert only |
| `applicability_policy_candidate_event` | append-only history: SUBMITTED, APPROVED, RETURNED, WITHDRAWN, PUBLISHED, SUPERSEDED, **REFUSED** | FK candidate; UPDATE / DELETE refused |
| `applicability_policy_version` | a published version | FK policy, FK candidate (unique), FK evidence run; unique (policy, number); partial unique index: **one `PUBLISHED` per policy**; guard on insert: **document, manifest, evidence and fingerprints must equal the candidate's**, and the candidate must be `PUBLISHED`; guard on update: only `PUBLISHED → SUPERSEDED`, nothing else may differ; never deleted |

11 validated foreign keys. Downgrade refuses while a candidate exists. Used only when
`applicability_publication_enabled` is on (which requires scenarios, policies and the library). `MIGRATION_HEAD` is
`0041`; a schema at `0040` is accepted while the setting is off — the state of local development.

No foreign key, column or operation reaches a case, a sale, a customer, a session, a callback, an assignment rule, a
survey binding or a requirement group.

## 3. The readiness gate (`publication.readiness`) — one implementation, in Python

Computed from the **saved** revision, its resolved dependencies, the evaluator's own analysis, and **one recorded run
the author chose**. The newest run is never chosen for them. The response lists every blocker; there is no generic
"not ready".

A blocker is `{code, message, action, prevents[], at{}}`: what is wrong, how to clear it, which of submission /
approval / publication it prevents, and what it concerns (requirement, dependency, exact versions).

| # | Code | When |
|---|---|---|
| 1 | `UNPUBLISHED_DEPENDENCY` | a pinned library item is a draft, or names nothing that exists |
| 2 | `INVALID_SURVEY_REFERENCE` | a survey reference does not resolve to a published version at the stated fingerprints |
| 3 | `DEPENDENCY_STALE` | a pinned draft has moved |
| 4 | analysis codes | any evaluator blocker (undeclared shared delivery, replacement cycle, …) |
| 5 | `PIN_DIFFERS` | a published condition evaluated against another variable version than it was published with — **no override** |
| 6 | `SUITE_REQUIRED` | no run chosen, or the chosen run is of an exploratory suite |
| 7 | `SUITE_FAILED`, `COVERAGE_NOT_MEANINGFUL` | the run did not pass; or passed without meaningful coverage |
| 8 | `EVIDENCE_OUT_OF_DATE`, `EVIDENCE_NOT_REPRODUCIBLE` | the run is of another revision or manifest, of a candidate or version rather than the draft; the suite or a scenario changed since **or is at a later revision than the run recorded, even with identical content**; the run does not reproduce from its record |
| 9 | `PROFILE_MISMATCH`, `VARIABLE_VERSION_INCOMPATIBLE` | named from the run's own diagnostics for a gating scenario; reconciliation is mandatory |
| 10 | `EXPECTATIONS_NOT_INDEPENDENT`, `INDEPENDENT_COVERAGE_REQUIRED`, `BEHAVIOUR_ONLY_RESULT_DERIVED` | §4 |
| 11 | `SAME_PERSON` | at a transition, by identity |
| — | `CANDIDATE_OPEN`, `NO_REQUIREMENT`, `ARCHIVED` | housekeeping |

A pin to a **superseded** published version is valid: it produces a notice (`NEWER_VERSION`), never a blocker, and is
never upgraded.

## 4. Independent expectations (D-442) — the deterministic rule as implemented

`publication.independence(policy_document, recorded_results)` reads only the recorded run.

- **Independent passing scenario:** verdict `PASSED` and `expectation.source = AUTHORED`.
- **Material behaviours:** the requirement-level set of the coverage contract — every requirement *applies* and *does
  not apply*; each replacement *happens*; each choose-one alternative *is chosen*; scope *in* and *out*; a declared
  shared delivery *overlaps*.
- Coverage is computed twice with the same accepted function: over all passing results, and over the independent
  passing results only. A material behaviour exercised in the first and missing in the second is covered **only by
  result-derived expectations**.

| Code | Blocks when |
|---|---|
| `EXPECTATIONS_NOT_INDEPENDENT` | every stated expectation is `PROPOSED_FROM_RESULT` |
| `INDEPENDENT_COVERAGE_REQUIRED` | no independent passing scenario with a resolved result selecting a survey; or none in which a requirement does not apply |
| `BEHAVIOUR_ONLY_RESULT_DERIVED` | any material behaviour is covered only by result-derived expectations — each named, with its requirement |

Condition-level branches covered only by result-derived expectations are counted and shown, not blocking.

**Provenance is never converted.** The server stores the source it is given and never upgrades one; the editor keeps
`PROPOSED_FROM_RESULT` through any edit — an authored expectation is obtained only by clearing and stating anew.

**Authorship (D-442, part 5.2).** On every suite save the server stamps `stated_by` and `stated_at` on an expectation
whose stated content changed, and only then. The provenance table gives, per scenario: expected outcome, source, who
stated it and when, where that authorship was read from — `SERVER_STAMP`, `SUITE_HISTORY` (an expectation saved
before the stamp existed: the actor of the suite save that last changed it, from the append-only history) or
`UNKNOWN` — and whether the scenario counts as independent. Nobody is invented.

## 5. The candidate and its lifecycle

- **Submit** (`applicability.edit`): the gate must be clear; the author sends the document, manifest and run
  fingerprints they were shown, and a mismatch is refused (`MANIFEST_CHANGED`, `EVIDENCE_CHANGED`,
  `STALE_REVISION`). One transaction writes the candidate, its dependency rows, the event and the audit record.
  The working draft is not touched.
- **Decide** (`applicability.approve`): approve or return (a reason of at least ten characters). Not the submitter.
  The checker names the `candidate_sha256` reviewed. **Approval revalidates** the frozen candidate first.
- **Withdraw** (`applicability.edit`): only the submitter; a submitted or approved candidate; with a reason.
- **Publish** (`applicability.publish`): approved only; not the submitter and not the checker; the publisher confirms
  the fingerprint **and the version number**. Revalidation, then: previous version `SUPERSEDED`, candidate
  `PUBLISHED`, version row inserted **by copying the candidate's own columns** — the draft is not read.
- **Refused transitions are history.** A refused decision or publication (`409`) is rolled back, then recorded in a
  transaction of its own as a `REFUSED` candidate event and a `DENIED` audit record.

**Checker authorship (D-443):** a checker who authored suite expectations may approve, provided they did not submit
the candidate. The provenance table shows who authored what to checker and publisher.

### 5.1 Revalidation (`publication.revalidate`) — at approval and at publication

Against the frozen candidate only; nothing is refreshed, substituted or upgraded:

1. the stored candidate still matches its own fingerprints (`CANDIDATE_CORRUPTED`);
2. every pinned library and survey version still exists, in the same market, `PUBLISHED` or `SUPERSEDED`, at the
   pinned fingerprints (`DEPENDENCY_CHANGED`);
3. the evidence run is the one submitted; the suite's fingerprint and every scenario's document and snapshot
   fingerprints **and revisions** equal what the run recorded (`EVIDENCE_CHANGED`);
4. the run still reproduces from its own record (`EVIDENCE_NOT_REPRODUCIBLE`);
5. the independence rule still holds.

**Evidence is a run of exact revisions (owner ruling D-460; supersedes the earlier content-only comparison).** In
addition to the fingerprints, the suite's revision and every scenario's revision must equal the revision **the
qualifying run itself recorded** (`applicability_evaluation_run.suite_revision`,
`applicability_evaluation_result.scenario_revision`). A revision advances only on a real change and never goes back,
so a suite or scenario that was edited after the run and then restored byte for byte has its old fingerprint and a
newer revision — and is refused (`EVIDENCE_CHANGED`, `at.reason = REVISION_ADVANCED`, with the revision run and the
revision now). The same check applies at readiness and submission (`EVIDENCE_OUT_OF_DATE`). Restoring content never
restores evidence: a new qualifying run and a newly submitted candidate are required, and the original candidate and
its history are kept.

Not affected: the recorded run stays immutable and reproduces from its own record; the working policy draft moving on
after submission does not invalidate a candidate. No schema change was needed — both revisions were already recorded
by migration `0040`. New candidates also carry each scenario's revision in their frozen evidence. A newer passing run
does not rescue a candidate — the candidate names its own run.

## 6. Published versions, supersession, verification

- Immutable, numbered per policy; at most one `PUBLISHED`; the earlier one becomes `SUPERSEDED` in the same
  transaction and stays readable.
- `verify_version`: the version's fingerprints, its identity with its candidate, and its evidence run re-evaluated
  from the run's own record — without reading the library.
- `usage`: which published versions pin a library item or a survey, at which version (from the dependency rows).

## 7. Explicit run targets (D-455)

`GET /policies/{id}/run-targets` lists the working draft at its revision, open candidates, and every published
version, each with status and both fingerprints, and `must_choose`.

`POST /suites/{id}/runs` takes `target`. With `must_choose`, a run without one is refused (`TARGET_REQUIRED`); a draft
target at another revision is refused (`STALE_TARGET`). A candidate or version is evaluated from **its own frozen
document and definitions**. The target is written into the immutable run record and returned with every run; a run
recorded before targets existed reads as "the saved draft at that revision". A run of a candidate or a published
version is never evidence for the draft.

No existing table was altered for this: the target lives in the run's `record`.

## 8. Impact (`POST /policies/{id}/impact`)

Two exact targets — draft, candidate, published version — over **one dataset**: the scenarios of a recorded run,
exactly as recorded, evaluated on both sides now. Returns added, removed and re-versioned surveys, newly pending,
newly unresolved, now resolved, the requirements that are the reason, changed requirements, scope and dependency
versions. `reproducible` is false, with the reason, when a side cannot be evaluated. Nothing is recorded.

Used for: candidate against the published version (shown to the checker), version against version, draft against a
published version.

## 9. Operations (13, under `/api/v1/applicability`)

| Operation | Needs |
|---|---|
| `GET /policies/{id}/readiness?run_id=` · `GET /policies/{id}/run-targets` | read |
| `POST /policies/{id}/submit` | edit |
| `GET /policy-candidates` · `GET /policy-candidates/{id}` | read |
| `POST /policy-candidates/{id}/decision` | approve |
| `POST /policy-candidates/{id}/withdraw` | edit |
| `POST /policy-candidates/{id}/publish` | publish |
| `GET /policies/{id}/versions` · `GET /policy-versions/{id}` · `GET /policy-versions/usage` | read |
| `POST /policy-versions/{id}/verify` · `POST /policies/{id}/impact` | read |

Every operation also needs `survey.read`. Market-scoped; CSRF on every write and computation; separate rate limits
for saving and computing; audited with the real signed-in identity. No operation changes or deletes a candidate's
content or a version.

## 10. Frontend

Setting `VITE_APPLICABILITY_PUBLICATION=1` (with the Scenario studio) makes step 5 the real page; without it step 5
is the APPL-X3 readiness page, unchanged.

- **Readiness and submission** — verdict; the saved revision and its fingerprints; the evidence chooser (nothing
  preselected); evidence card with reproduction, age, independence, provenance table and coverage; each blocker with
  what it concerns, the requirement or scenario to open, and how to clear it; notices; exact dependencies; submission
  with an explicit confirmation of the three fingerprints.
- **Candidates and review** — every candidate including returned and withdrawn; the immutable submission (which
  surveys, at which versions); what changes from the published version; the evidence and provenance; revalidation
  state; and only the actions the server allows this person: approve (confirming the fingerprint) or return with a
  reason; publish (confirming fingerprint and version, with the three people named); withdraw. A person who
  submitted or approved is told who must act next. No persona switch exists.
- **Published versions** — current and superseded; the three people; verify; compare with another version.
- **Impact** — any two targets over a chosen recorded run.
- **Suite builder** — the explicit target chooser; **run history** — what each run evaluated.

## 11. Not in this checkpoint

Designer integration steps 2–4; retiring any prototype operation (`70_…` §12 conditions not met); a time-to-live on
evidence; an acknowledgement workflow for mismatches; any operational reading of a published policy.
