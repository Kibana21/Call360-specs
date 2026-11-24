# 70 — APPL-X4b implementation specification (for authorisation)

**Checkpoint:** APPL-X4b — Applicability Policy governance: readiness gate, immutable candidates, three-person
publication, published versions.
**Status:** SPECIFICATION, revised 2026-11-24 with the owner's rulings on Q-a … Q-f (D-441 … D-446).
**Nothing here is built. APPL-X4b is NOT authorised.** No migration `0041`, no candidate or publication table, and no
publication control that writes exists.
**Builds on:** `68_…` (scenarios, suites, recorded runs; migration `0040`, on development since 2026-11-24).
**Data:** synthetic only. **No operational execution:** a published policy selects nothing for a real case and no
callback is planned or made from it.

---

## 1. What publication must guarantee

1. The person approving and the person publishing see **exactly** which policy revision, which dependency manifest
   and which passing suite run they act on.
2. Nothing can change underneath them between submission, approval and publication.
3. A candidate never becomes valid merely because expectations were regenerated from its own results. **Human
   confirmation of a result is not independent evidence of correctness.**

## 2. Lifecycle

| State | Entered by | Who | Notes |
|---|---|---|---|
| draft | (APPL-X3) | author | one working draft per policy |
| `SUBMITTED` | submit | author (`applicability.edit`) | freezes a candidate; refused while any blocker exists |
| `RETURNED` | return, with a reason | checker (`applicability.approve`) | the author edits and submits a new candidate |
| `WITHDRAWN` | withdraw | the submitting author | candidate kept |
| `APPROVED` | approve | checker — not the submitter | |
| `PUBLISHED` | publish | publisher (`applicability.publish`) — not the submitter, not the checker | every blocker re-checked |
| `SUPERSEDED` | a later publication | — | kept, readable, verifiable; never deleted |

**Three different identities** for one candidate — submitter, checker, publisher — enforced by the service and by
table CHECK constraints. No one approves or publishes a candidate they submitted. No new permission; no role widened.

**Checker and suite authorship (owner ruling Q-c, D-443).** The checker **may** have authored some or all of the
suite's independently defined expectations, provided they are not the candidate's submitter. Authorship and provenance
of every expectation are shown to checker and publisher. The three-person rule concerns the policy candidate.

## 3. The frozen candidate

Written in one transaction at submit; immutable afterwards:

- the policy document, its `document_sha256`, the saved `draft_revision` it was taken from;
- the dependency **manifest**: every variable, profile, condition and survey version — asset / version id, version
  number, content and manifest fingerprints — and the definitions themselves;
- the **evidence**: the id and `run_sha256` of the qualifying suite run, the suite's `suite_sha256`, the run's
  coverage, the **provenance table** of §5.3, and the run's creation time;
- `candidate_sha256` over all of it; the submitter's acknowledgement of the manifest they were shown.

Approval and publication name the `candidate_sha256` they act on; a mismatch is refused (`MANIFEST_CHANGED`).

## 4. Readiness gate — blockers (all computed server-side, each with the way to clear it)

| # | Blocker | Code |
|---|---|---|
| 1 | A library dependency that was never genuinely published (a draft, an open candidate, withdrawn, missing) | `UNPUBLISHED_DEPENDENCY` |
| 2 | A pinned survey version that is missing, of another market, not `PUBLISHED` / `SUPERSEDED`, or whose fingerprints differ from the pin | `INVALID_SURVEY_REFERENCE` |
| 3 | Any stale dependency | `DEPENDENCY_STALE` |
| 4 | Any evaluator analysis blocker (unreachable, contradictory, replacement cycle, undeclared shared delivery) | the analysis code |
| 5 | **`PIN_DIFFERS`** — a published condition evaluated against another variable version than it was published with | `PIN_DIFFERS` |
| 6 | No publication-gating suite of this policy with a qualifying recorded run (§5.1) | `SUITE_REQUIRED` |
| 7 | The run did not pass, or is not meaningful | `SUITE_FAILED` / `COVERAGE_NOT_MEANINGFUL` |
| 8 | The run is not of this exact revision and manifest, or its suite / scenarios changed since | `EVIDENCE_OUT_OF_DATE` |
| 9 | A gating scenario pins a profile version other than the policy's, or a value incompatible with the policy's variable version | `PROFILE_MISMATCH` / `VARIABLE_VERSION_INCOMPATIBLE` |
| 10 | **Expectations are not independent enough** (§5.2) | `EXPECTATIONS_NOT_INDEPENDENT` / `INDEPENDENT_COVERAGE_REQUIRED` / `BEHAVIOUR_ONLY_RESULT_DERIVED` |
| 11 | Same person in two roles | `SAME_PERSON` |

- **Superseded is valid (D-431).** A version that was genuinely published stays a valid pin after a newer one
  supersedes it: a visible notice, never silent adoption. Only missing, corrupted, unpublished or wrong-market
  versions block.
- **No `PIN_DIFFERS` override (D-431).** Cleared only by pinning the variable to the version the condition was
  published with, or by publishing a compatible new condition version and adopting it. The evaluator's exploratory
  behaviour is unchanged.
- **No acknowledgement workflow for profile mismatches (owner ruling Q-a, D-441).** No table, no operation. In a
  gating scenario reconciliation is mandatory (blocker 9). Exploratory mismatches stay displayed with exact versions
  and fingerprints and can never satisfy publication coverage.

## 5. The qualifying suite run

### 5.1 Conditions (all must hold)

1. The suite is `PUBLICATION_GATING` and belongs to this policy.
2. Run status `PASSED`.
3. `coverage.meaningful_for_publication` is true (`68_…` §6): a passing resolved positive case, a passing negative
   case, not every result unresolved, no requirement-level gap.
4. The run's `policy_document_sha256` and `policy_snapshot_sha256` equal the candidate's.
5. The suite's `suite_sha256` and every scenario's document and snapshot fingerprints are still what the run recorded.
6. `verify` reproduces the run from its record.
7. The independence rule of §5.2 holds.

Not required: an arbitrary number of scenarios. **No time-to-live (owner ruling Q-e, D-445):** the fingerprints, the
verified reproduction and the unchanged suite and scenarios are the requirement. The run's creation date and its age
are shown to checker and publisher. A later business rule may add explicit freshness.

### 5.2 Independence of expectations (owner ruling Q-b, D-442) — deterministic rule

Each expectation carries `source`: `AUTHORED` (stated by a person from their own understanding) or
`PROPOSED_FROM_RESULT` (first filled from an evaluator result, then confirmed). **Provenance is never converted:**
editing a proposal leaves it `PROPOSED_FROM_RESULT`; an authored expectation is obtained only by clearing it and
stating it anew. (This is how the APPL-X4a editor already behaves.)

Definitions, all read from the qualifying run's recorded plans:

- An **independent passing scenario** — verdict `PASSED` and `expectation.source = AUTHORED`.
- The **material behaviours** of a policy — exactly the requirement-level set used by coverage: for every requirement
  *applies* and *does not apply*; for every requirement that replaces others, *the replacement happened*; for every
  choose-one requirement, *each alternative chosen*; if the policy has a scope, *in scope* and *out of scope*; if it
  declares a shared delivery, *the overlap*.
- A material behaviour is **independently covered** when at least one independent passing scenario exercises it.

The gate **blocks** when any of these is true:

| Code | Condition |
|---|---|
| `EXPECTATIONS_NOT_INDEPENDENT` | every expectation in the suite is `PROPOSED_FROM_RESULT` |
| `INDEPENDENT_COVERAGE_REQUIRED` | there is no independent passing scenario with a resolved result that selects a survey, **or** none in which a requirement does not apply |
| `BEHAVIOUR_ONLY_RESULT_DERIVED` | at least one material behaviour is exercised only by scenarios whose expectation is `PROPOSED_FROM_RESULT`; the response lists each such behaviour and the scenarios concerned |

Not blocking, but listed for the checker: condition-level branches covered only by result-derived expectations.

The same inputs always give the same verdict: the rule reads only the recorded run and the stored suite.

### 5.3 Provenance shown to the checker and the publisher

Per scenario of the qualifying suite: name; expected outcome; `source`; **who stated or confirmed it and when**; the
scenario revision it was reviewed at; verdict; and, per material behaviour, whether it is independently covered.

**Prerequisite inside APPL-X4b (step X4b-1):** the server stamps `stated_by` and `stated_at` on an expectation
whenever its stated content changes (inside the existing `expectation` JSON — no schema change). For expectations
saved before that, the suite's append-only history already records who saved the suite and which expectations
changed at that revision; the provenance table uses it and says which of the two sources it read.

## 6. Protection between approval and publication

At publish, the service re-checks blockers 1–3, 5, 8, 9 and 10 against the candidate's frozen manifest and the
evidence run's fingerprints, and refuses if:

- any pinned library or survey version is no longer `PUBLISHED` / `SUPERSEDED`, or its fingerprint differs;
- the suite or any scenario of the evidence run has changed (fingerprints);
- the evidence run can no longer be verified from its record;
- `candidate_sha256` differs from the one approved.

The policy's working draft may move on after submission; it does not affect the candidate. Publishing writes the
published version **from the candidate**, never from the current draft.

## 7. Published versions and supersession

- Immutable; numbered per policy; at most one `PUBLISHED` per policy (partial unique index); publishing sets the
  previous one `SUPERSEDED` in the same transaction.
- A published version carries its manifest, definitions and evidence run: it can be evaluated and re-verified
  without the library.
- Nothing is deleted. The migration's downgrade refuses while a candidate or a version exists.

## 8. Impact against published versions

Using APPL-X4a's comparison structure unchanged:

- the gating suite against the **published** version and against the **draft / candidate**, side by side;
- per scenario: survey added, removed, replaced, at another version; newly pending; newly unresolved; now resolved;
  changed condition outcome; changed dependency version; changed fact;
- shown on the readiness page and frozen into the candidate.

## 9. Migration `0041_applicability_publication` (parent `0040`) — reviewed, NOT created

Additive only. **No existing table, column or constraint is altered** (owner ruling Q-d, D-444: a separate
append-only candidate event table; the accepted `applicability_policy_event` CHECK list is left as it is).

| Table | Purpose | Integrity boundary |
|---|---|---|
| `applicability_policy_candidate` | the frozen candidate: document, manifest, evidence reference, `candidate_sha256`, status, three actors | FK policy; FK evidence run (`applicability_evaluation_run`); CHECKs for three distinct people; content immutable after insert (guard: only status and the actor / time columns of its own transition may change) |
| `applicability_policy_candidate_dependency` | the manifest as rows | FK candidate; FK `applicability_asset_version`, `survey_definition`, `survey_version`; guard: same market, version `PUBLISHED` or `SUPERSEDED` |
| `applicability_policy_candidate_event` | append-only history of candidates and versions | FK candidate; UPDATE / DELETE refused |
| `applicability_policy_version` | published versions | FK policy, FK candidate (unique); one `PUBLISHED` per policy; content immutable; only `PUBLISHED → SUPERSEDED` allowed |

Four tables is the smallest shape: the candidate and the version are different things with different lifecycles (a
candidate may be returned or withdrawn and never become a version); the dependency rows give exact, indexed "where
used" and database-enforced "published only"; the event table keeps the accepted one untouched. No acknowledgement
table (Q-a). No permission added. Downgrade refuses while a candidate exists.

Boundaries that stay closed: no foreign key or column towards a case, a sale, a customer, a session, a callback, an
assignment rule, a binding or a group.

## 10. Operations (proposed, under `/api/v1/applicability`)

`GET /policies/{id}/readiness` · `POST /policies/{id}/submit` · `GET /policy-candidates/{id}` ·
`POST /policy-candidates/{id}/withdraw` · `POST …/decision` (approve / return) · `POST …/publish` ·
`GET /policies/{id}/versions` · `GET /policy-versions/{id}` · `POST /policy-versions/{id}/evaluate` ·
`POST /policies/{id}/impact` · `POST /policy-versions/compare`.

A suite run gains a second kind of subject — a candidate or a published version besides a saved draft. The run record
already stores the policy document and manifest, so its shape does not change.

## 11. Audit

Every transition writes the candidate event and `audit_event` with the real signed-in actor, `candidate_sha256`, the
manifest fingerprint, the evidence `run_sha256` and the comment. The approval page and the audit record show the same
three fingerprints.

## 12. Prototype endpoints (owner ruling Q-f, D-446)

An endpoint is retired only when every supported caller is identified, its replacement is in use, parity is proven,
all relevant browser and backend tests pass, and no supported feature-flag configuration relies on it.

| Endpoint | Callers today | Replacement | Can it retire in X4b? |
|---|---|---|---|
| `prototype/evaluate` | in-tab policies (any configuration without saved policies); the designer's quick examples | `policies/{id}/evaluate`, `scenarios/evaluate` | only after the designer integration steps 2–4 (`68_…` addendum) **and** a decision that the in-tab configuration is no longer supported |
| `prototype/analyse` | in-tab policies | `policies/{id}/inspect` | same condition |
| `prototype/condition-test` | Condition Lab | `assets/…/test` exists for saved items; unsaved expressions still use the prototype | needs a replacement for unsaved expressions |
| `prototype/scenarios` | "from a generated combination" in the studio | none yet | needs a persisted-aware generator |

No active functionality is removed to simplify the catalogue. Retirement is the last step of X4b at the earliest, and
may be a checkpoint of its own.

## 13. Acceptance journeys (proposed)

| | |
|---|---|
| A | Readiness lists every blocker in turn, each with the way to clear it |
| B | `PIN_DIFFERS` blocks submit; cleared by aligning the pin; cleared by a new condition version |
| C | No suite; a failing suite; an exploratory suite; an only-unresolved suite; a run of an older revision — each refused |
| D | **Independence:** all expectations proposed from results → blocked; mixed, with a material behaviour covered only by a result-derived expectation → blocked, the behaviour named; re-stated independently → passes the gate; provenance never becomes `AUTHORED` by editing |
| E | A pin to a **superseded** survey or library version is accepted, with a notice |
| F | Submit freezes the candidate; the draft is edited afterwards; the candidate is unchanged |
| G | Three signed-in people; each refused the others' steps; a checker who authored suite expectations may approve; the submitter may not; return and resubmit; withdraw |
| H | Between approval and publication a scenario of the evidence suite is edited: publication refused |
| I | Version 2 supersedes version 1; version 1 still reads and verifies; impact and comparison over the suite; the run's age is shown, and no age blocks |
| J | No case, session, callback, assignment rule, binding or group changed (digest comparison); golden 82 and 14 unchanged |

## 14. Implementation steps (each stops for review only at the end unless the owner says otherwise)

| Step | Content |
|---|---|
| X4b-0 | This specification approved; journeys agreed |
| X4b-1 | Expectation `stated_by` / `stated_at`; provenance table; the independence rule as a pure function with tests |
| X4b-2 | Migration `0041` and domain services on the test schema |
| X4b-3 | Readiness gate and submit; frozen candidate |
| X4b-4 | Decision, return, withdraw, publish; publication-time revalidation; supersession |
| X4b-5 | Runs against candidates and versions; impact and version comparison |
| X4b-6 | Frontend: readiness page, candidate review with provenance, version history |
| X4b-7 | Designer integration steps 2–4, if authorised with it; prototype-endpoint review |
| X4b-8 | Full regression on the test schema; report — **owner review before any development migration** |

## 15. Remaining questions

None of the six earlier questions is open. Two smaller points for the authorisation:

- **Q-g** Should designer integration steps 2–4 (`68_…` addendum) be part of APPL-X4b or a checkpoint of their own?
  (Proposed: their own, so that governance is reviewed on its own.)
- **Q-h** When a published version exists, should the suite's "run and record" default to the draft, or ask?
  (Proposed: ask, and label the subject on the run.)

**Stop.** APPL-X4b is not started.
