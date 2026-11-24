# 70 — APPL-X4b readiness specification

**Checkpoint proposed:** APPL-X4b — Applicability Policy governance: readiness gate, immutable candidates,
three-person publication, published versions.
**Status:** SPECIFICATION FOR REVIEW. **Nothing here is built. APPL-X4b is NOT authorised**, and by the owner's ruling
is not started until APPL-X4a is accepted.
**Date:** 2026-11-24. **Builds on:** `68_…` (scenarios, suites, recorded runs; migration `0040`).
**Data:** synthetic only. **No operational execution:** a published policy selects nothing for a real case.

---

## 1. What publication must guarantee

A person approving or publishing sees **exactly** which policy revision, which dependency manifest and which passing
suite run they are approving, and nothing can change underneath them between review and publication.

A candidate never becomes valid merely because its expectations were regenerated from its own results.

## 2. Lifecycle

| State | Entered by | Who | Notes |
|---|---|---|---|
| draft | (APPL-X3) | author | one working draft per policy |
| `SUBMITTED` | submit | author (`applicability.edit`) | freezes a candidate; refused while any blocker exists |
| `RETURNED` | return, with a reason | checker (`applicability.approve`) | the author edits and submits a new candidate |
| withdrawn | withdraw | the submitting author | candidate kept, marked withdrawn |
| `APPROVED` | approve | checker — not the author | |
| `PUBLISHED` | publish | publisher (`applicability.publish`) — not the author, not the checker | re-checks every blocker |
| `SUPERSEDED` | a later publication | — | kept, readable, never deleted |

Three different identities, enforced in the service and by table CHECK constraints
(`submitted_by <> decided_by`, `published_by` different from both). No new permission; no role is widened.

## 3. The frozen candidate

Written in one transaction at submit; immutable afterwards:

- the policy document, its `document_sha256`, the saved `draft_revision` it was taken from;
- the dependency **manifest**: every variable, profile, condition and survey version with asset / version id, version
  number, content and manifest fingerprints — and the definitions themselves;
- the **evidence**: the id and `run_sha256` of the recorded suite run that qualifies it, with the suite's
  `suite_sha256` and the run's coverage;
- `candidate_sha256` over all of it; the acknowledgement by the submitter of the manifest shown to them (as APPL-X2's
  `PINS_CHANGED`).

Approval and publication name the `candidate_sha256` they act on; a mismatch is refused (`MANIFEST_CHANGED`).

## 4. Readiness gate — blockers (all computed server-side)

| # | Blocker | Code |
|---|---|---|
| 1 | A library dependency that is not a genuinely published version (a draft, a candidate, withdrawn) | `UNPUBLISHED_DEPENDENCY` |
| 2 | A pinned survey version that is not `PUBLISHED` or `SUPERSEDED`, is missing, of another market, or whose fingerprints differ from the pin | `INVALID_SURVEY_REFERENCE` |
| 3 | Any stale dependency | `DEPENDENCY_STALE` |
| 4 | Any evaluator analysis blocker (unreachable, contradictory, replacement cycle, undeclared shared delivery) | the analysis code |
| 5 | **`PIN_DIFFERS`**: a published condition evaluated against another variable version than it was published with | `PIN_DIFFERS` |
| 6 | No publication-gating suite of this policy with a recorded run that qualifies (§5) | `SUITE_REQUIRED` |
| 7 | The qualifying run did not pass, or is not meaningful | `SUITE_FAILED` / `COVERAGE_NOT_MEANINGFUL` |
| 8 | The qualifying run is not of this exact revision and manifest | `EVIDENCE_OUT_OF_DATE` |
| 9 | A scenario of the qualifying suite pins a profile version other than the policy's | `PROFILE_MISMATCH` |
| 10 | Same person in two roles | `SAME_PERSON` |

**Superseded is valid (owner ruling Q-5).** A version that was genuinely published remains a valid pin after a newer
one supersedes it. It produces a visible notice — "version *n* is now published; nothing changes until you adopt it" —
and is never adopted silently. Only missing, corrupted, unpublished or wrong-market versions block.

**No override in APPL-X4b** for blocker 5 (owner ruling Q-4). The two ways to clear it: pin the variable to the version
the condition was published with; or publish a compatible new condition version and adopt it. The evaluator's
exploratory behaviour is not changed.

## 5. The qualifying suite run

A recorded run (`68_…` §4.4) qualifies a candidate only if **all** hold:

1. the suite is `PUBLICATION_GATING` and belongs to this policy;
2. run status `PASSED`;
3. `coverage.meaningful_for_publication` is true — which already requires a passing resolved positive case, a passing
   negative case, not every result unresolved, and no requirement-level gap;
4. `policy_document_sha256` and `policy_snapshot_sha256` of the run equal the candidate's;
5. the suite's `suite_sha256` and every scenario's `scenario_document_sha256` / `scenario_snapshot_sha256` are still
   what the run recorded — a suite or scenario edited after the run invalidates it as evidence;
6. `verify` reproduces the run from its record.

Not required: an arbitrary number of scenarios. Reported, not blocking: condition-level gaps, listed for the checker.

**Expectations taken from results.** Each expectation records `source`. The readiness page and the candidate show, per
scenario, whether the expectation was authored or first proposed from a result and then confirmed, and by whom. A
suite in which **every** expectation was proposed from a result is flagged prominently for the checker; whether that
should block is an owner decision (Q-b).

## 6. Protection between approval and publication

At publish, the service re-checks blockers 1–3, 5 and 8 against the candidate's frozen manifest and the evidence run's
fingerprints, and refuses if:

- any pinned library or survey version is no longer `PUBLISHED` / `SUPERSEDED`, or its fingerprint differs;
- the evidence run can no longer be verified from its record;
- `candidate_sha256` differs from the one approved.

The policy's working draft may move on after submission; it does not affect the candidate. Publishing writes the
published version from the **candidate**, never from the current draft.

## 7. Published versions and supersession

- `applicability_policy_version`: immutable; numbered per policy; partial unique index — at most one `PUBLISHED` per
  policy; publishing sets the previous one `SUPERSEDED` in the same transaction.
- A published version carries its manifest, definitions and evidence run, so it can be evaluated and re-verified
  without the library.
- Nothing is deleted. Downgrade of the migration refuses while a candidate or version exists.

## 8. Draft-versus-published impact

Now real, using X4a's comparison structure unchanged:

- the gating suite run against the **published** version and against the **draft**, side by side;
- per scenario: survey added, removed, replaced, at another version; newly pending; newly unresolved; now resolved;
  changed condition outcome; changed dependency version; changed fact;
- shown on the readiness page and frozen into the candidate.

## 9. Migration `0041_applicability_publication` (parent `0040`), additive

| Table | Purpose |
|---|---|
| `applicability_policy_candidate` | frozen candidate, status, three actors, CHECKs for distinct people, `candidate_sha256` |
| `applicability_policy_candidate_dependency` | manifest rows; FK `applicability_asset_version`, `survey_version`; trigger: published or superseded only |
| `applicability_policy_version` | published versions; one `PUBLISHED` per policy; FK candidate, FK evidence run |
| `applicability_policy_acknowledgement` *(only if Q-a is yes)* | audited exploratory acknowledgement of a profile mismatch |

Events reuse `applicability_policy_event` with new event names (its CHECK list is extended — **the one alteration of
an existing object**, to be confirmed; the alternative is a separate event table, as `0039` did). No permission added.

## 10. Operations (proposed)

`GET /policies/{id}/readiness` · `POST /policies/{id}/submit` · `POST /policy-candidates/{id}/withdraw` ·
`POST …/decision` (approve / return) · `POST …/publish` · `GET /policy-candidates/{id}` ·
`GET /policies/{id}/versions` · `GET /policy-versions/{id}` · `POST /policy-versions/{id}/evaluate` ·
`POST /policies/{id}/impact` · `POST /policy-versions/compare`.

A suite run gains a second subject: a published version or a candidate, besides a saved draft (the run table already
records the policy document and manifest, so the record shape does not change).

## 11. Audit

Every transition: append-only policy event and `audit_event`, with actor, `candidate_sha256`, manifest fingerprint,
evidence `run_sha256`, comment. The approval page and the audit record show the same three fingerprints.

## 12. Acceptance journeys (proposed)

| | |
|---|---|
| A | Readiness lists every blocker in turn, each with the way to clear it |
| B | `PIN_DIFFERS` blocks submit; cleared by aligning the pin; cleared by a new condition version |
| C | No suite, a failing suite, an exploratory suite, an only-unresolved suite, a suite run of an older revision — each refused |
| D | A pin to a **superseded** survey or library version is accepted, with a notice |
| E | Submit freezes the candidate; the draft is edited afterwards; the candidate is unchanged |
| F | Author, checker, publisher — three signed-in people; each refused the others' steps; return and resubmit; withdraw |
| G | Between approval and publication a scenario of the evidence suite is edited: publication refused |
| H | Version 2 supersedes version 1; version 1 still reads and verifies; impact and comparison over the suite |
| I | A suite whose expectations were all proposed from results is shown as such to the checker |
| J | No case, session, assignment rule, binding or group changed (digest comparison); golden 82 and 14 unchanged |

## 13. Questions for the owner

- **Q-a** Exploratory acknowledgement of a profile mismatch (Q-3 allows it): build it in X4b, or leave exploratory
  mismatches simply reported, as X4a does?
- **Q-b** A suite whose every expectation began as a proposal from a result: flag only (proposed), or block?
- **Q-c** May the checker be the person who authored the suite's expectations? (Proposed: yes, but not the policy's
  submitter — the three-person rule is about the policy candidate.)
- **Q-d** Extend the CHECK list of `applicability_policy_event`, or add a separate candidate event table?
- **Q-e** Should publication require the evidence run to be no older than some period, or is "same revision, same
  fingerprints" sufficient? (Proposed: fingerprints are sufficient.)
- **Q-f** Retirement of the prototype operations: still proposed as the last step, after the designer's quick
  examples move to saved scenarios (`68_…` §9).

**Stop.** APPL-X4b is not started.
