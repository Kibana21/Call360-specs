# 67 — APPL-X4 readiness assessment

**Checkpoint proposed:** APPL-X4 — Persistent Scenario Studio, Applicability Policy Governance and Publication.
**Status:** ASSESSMENT — superseded in detail by `68_…` (APPL-X4a, built on the test schema) and `70_…` (APPL-X4b readiness
specification), following the owner's rulings D-428 … D-432. Kept for traceability.
**Date:** 2026-11-24. **Baseline:** development at `0039_applicability_policy`, APPL-X3 accepted (D-419).
**Data:** synthetic only. **Simulation only:** no operational case, session, contact attempt or call is selected,
planned or changed by anything in this checkpoint.

---

## 1. What exists today, and the gap

| Area | Today (APPL-X3) | Gap APPL-X4 closes |
|---|---|---|
| Variables, profiles, conditions | Governed, three-person, immutable published versions (`0038`) | none |
| Applicability Policy | One saved working draft per policy; exact pins; snapshot (`0039`) | no candidate, no approval, no published version |
| Scenarios | In the browser tab only; lost on reload | not persisted, not versioned, no suites |
| Evaluation | Server evaluates a saved revision or an unsaved preview; result not stored | no recorded synthetic evaluation, no draft-versus-published impact |
| `PIN_DIFFERS` | A diagnostic on a draft (D-416(a)) | must block publication (owner ruling) |
| Profile mismatch | Reported | must be resolved or acknowledged under governance |

## 2. Proposed scope (the owner's nineteen points, grouped)

### 2.1 Scenario Studio (points 1–3)

- **Scenario**: a named synthetic application — a set of fact values, optionally built on a pinned profile version.
  One working draft and `draft_revision`, like a policy. Market-scoped. Synthetic by construction: the document
  accepts only variables of the library; no customer or policy identifier field exists.
- **Scenario suite**: an ordered set of scenarios with, per scenario, an **expected outcome** (plan status and the
  selected survey versions). A suite is the regression dataset for a policy.
- **Exact snapshots (owner ruling)**: a saved scenario stores the *resolved* definition of every variable and
  profile it relies on — version number and content fingerprint — in the same form as a policy's dependency rows.
  A newly published profile version never changes a saved scenario; adoption is a deliberate, undoable edit, exactly
  as for a policy (X3-1).
- **Ad hoc previews** may resolve the current published profile, and must then return the exact resolved versions
  and one fingerprint over them, and label the result as not reproducible from a saved scenario.

### 2.2 Policy governance and publication (points 5–9, 12–14, 17)

- **Candidate**: `submit` freezes the working draft into an immutable candidate row: document, dependency manifest
  (every variable, profile, condition and survey version with content fingerprints), manifest fingerprint, and the
  suite results it was submitted with.
- **Three people**: author ≠ checker ≠ publisher, enforced in the service and by table CHECK constraints, reusing
  the APPL-X2 pattern. Withdraw, reject (with reason), approve, publish.
- **Published version**: immutable; numbered per policy; at most one `PUBLISHED` per policy; publishing supersedes
  the previous one (kept, never deleted, status `SUPERSEDED`).
- **Publication blockers** (server-side, all must be absent):
  1. any dependency that is not an approved **published** version (no drafts, no candidates) — point 12;
  2. a pinned Survey Studio version that was never genuinely published (missing, of another market, or whose
     fingerprint differs from the pin) — point 17. **Corrected per owner ruling Q-5 (D-431): a version that is
     `SUPERSEDED` was genuinely published and remains a valid pin, with a notice; it is not a blocker;**
  3. any `DEPENDENCY_STALE`;
  4. any evaluator `error`-level analysis finding (unreachable, contradictory, replacement cycle);
  5. **`PIN_DIFFERS`** — see 2.3;
  6. an unresolved **profile mismatch** — see 2.4;
  7. no attached suite, or a suite scenario whose expected outcome fails against the candidate;
  8. a draft that changed after the suite run (`draft_revision` or manifest fingerprint differs).
- **Audit** (point 14): append-only event rows plus `audit_event` for every transition, with actor, revision,
  manifest fingerprint and comment.

### 2.3 The `PIN_DIFFERS` rule (point 10; owner ruling D-416(a))

A published condition C v*n* was published against variable X v*a*. A policy that references C v*n* and pins X v*b*
(*b* ≠ *a*) is evaluating C with a meaning its approvers did not see.

- Draft authoring and labelled exploratory evaluation: unchanged — diagnostic `PIN_DIFFERS`.
- **Submission and publication: blocked.** The two reconciliations offered, both deliberate and undoable:
  (i) pin X to the version C was published with, where every other use in the policy allows it;
  (ii) publish a new version of C against X v*b* in the library, then adopt it.
- **No override is proposed in APPL-X4.** The ruling allows one only under "a separately approved, auditable
  override contract"; none exists, so none is built. The evaluator itself is not changed.

### 2.4 Profile mismatch (point 11)

Where a policy and a pinned scenario use different versions of the same profile: the suite run reports it per
scenario. Before submission it is either reconciled (adopt one version) or **acknowledged** — a recorded statement by
the author naming both versions, stored in the candidate manifest and shown to checker and publisher. Proposed
default: reconciliation required for scenarios with an expected outcome; acknowledgement allowed only for scenarios
marked exploratory. **Owner decision needed (Q-3).**

### 2.5 Impact analysis, recorded evaluations, comparison (points 4, 15, 16)

- **Recorded synthetic evaluation**: running a suite against a saved revision, a candidate or a published version
  stores an immutable record — subject, exact manifest fingerprint, scenario snapshot fingerprints, evaluator
  fingerprint, per-scenario plan and explanation. Clearly typed `SYNTHETIC`; no foreign key to any case table.
- **Draft-versus-published impact**: the same suite run against the draft and against the current published
  version, with the difference per scenario (surveys added, removed, replaced, newly pending).
- **Version comparison**: any two published versions or a version and the draft — document difference, manifest
  difference, and result difference over a chosen suite. Uses the existing `evaluator.compare`.

### 2.6 Boundaries (points 18, 19)

- No read or write of assignment rules, bindings or groups; none of those words in the interface.
- No operational integration: no case, sale, session, contact attempt, call plan or voice path reads a published
  Applicability Policy. A published policy is a governed artefact with no consumer until a later, separately
  authorised checkpoint (APP-1a / OPS-1).

## 3. Migration needs — proposed `0040_applicability_governance`

Additive only; no existing table altered. Proposed tables (final shape to be fixed in the APPL-X4 specification):

| Table | Purpose |
|---|---|
| `applicability_policy_version` | candidates and published versions: document, manifest, both fingerprints, status, author / checker / publisher, CHECK three distinct people; partial unique index one `PUBLISHED` per policy |
| `applicability_policy_version_dependency` | frozen dependency rows; foreign keys to `applicability_asset_version`, `survey_version`; **published only** enforced by trigger |
| `applicability_scenario` | working draft, `draft_revision`, snapshot of resolved definitions |
| `applicability_scenario_dependency` | exact variable / profile versions a scenario relies on |
| `applicability_suite`, `applicability_suite_member` | ordered scenarios with expected outcomes |
| `applicability_evaluation_run`, `applicability_evaluation_result` | immutable recorded synthetic evaluations |

- Immutability guards on versions, version dependencies and evaluation records; append-only events reuse
  `applicability_policy_event` (new event names) and add scenario / suite events.
- **Permissions:** the four existing ones suffice — `applicability.read`, `.edit` (author; scenarios and suites),
  `.approve` (checker), `.publish` (publisher). **No new permission is proposed and no role is widened.** The three
  development identities already hold exactly these.
- Downgrade refuses while a candidate, version or evaluation record exists (as `0038`, `0039` do).
- A second migration is **not** expected. If scenario persistence and publication are split into two checkpoints
  (Q-1), the tables split cleanly at the scenario / suite boundary.

## 4. API contracts (proposed, under `/api/v1/applicability`)

| Group | Operations |
|---|---|
| Scenarios | list, create, get, save draft, archive, restore, adopt dependency versions |
| Suites | list, create, get, save (members, expected outcomes), archive, restore |
| Runs | run suite against {saved revision, candidate, published version}; get run; list runs for a policy; impact (draft versus published) |
| Policy governance | readiness (all blockers, computed server-side); submit (acknowledged manifest, as APPL-X2 `PINS_CHANGED`); withdraw; decide (approve / reject); publish; list versions; get version; compare |

- Every operation keeps `survey.read` plus the applicability permission, market scope, CSRF, optimistic
  concurrency and the split rate-limit buckets of APPL-X3.
- New refusal codes: `PUBLICATION_BLOCKED` (with the list), `PIN_DIFFERS` (as a blocker), `UNPUBLISHED_DEPENDENCY`,
  `PROFILE_MISMATCH`, `SUITE_REQUIRED`, `SUITE_FAILED`, `MANIFEST_CHANGED`, `SAME_PERSON`.
- **Prototype endpoints (D-416(c)):** scenario persistence removes the last tab-only callers. Removal of the four
  `survey-applicability/prototype/*` operations is proposed as the **final** step of APPL-X4, after a caller audit
  and with regression coverage; one evaluation algorithm throughout (the existing evaluator, unchanged).

## 5. Integration dependencies

- **Survey Studio**: read-only; published `survey_version` rows by foreign key. No Survey Studio change.
- **Applicability library** (`0038`): read-only for policies; unchanged lifecycle (X3-2).
- **Evaluator** (`logic.py`, `evaluator.py`, `analysis.py`): reused unchanged. `rule_engine.py`,
  `answer_evaluation.py`, `finding_engine.py` not touched.
- **Frontend**: Scenario lab moves from the tab store to the server (same pattern as `policyService.tsx`); the
  readiness page becomes the real submit / review / publish page; the persona switch stays removed.
- **Identities**: the three existing development identities; a fourth person is not needed.
- **Not dependencies:** legacy assignment objects, cases, voice, Genesys.

## 6. Acceptance tests (proposed)

Backend (test schema): three-person rule by service and by constraint; each of the eight blockers refuses with its
code; `PIN_DIFFERS` blocks submit and publish and both reconciliations clear it; published-only dependency trigger;
immutability of versions and records; supersession keeps history; scenario snapshot unchanged when a newer profile
version is published; adopt / undo on a scenario; market isolation; permission matrix; downgrade refusal; evaluator
parity (recorded result equals the evaluator's own output); golden 82 runs and 14 plans unmodified.

Browser journeys:

| | Journey |
|---|---|
| A | Save scenarios, close the browser, reopen: same scenarios, same fingerprints |
| B | Build a suite with expected outcomes; run it against the saved policy |
| C | A newer profile version is published: the saved scenario does not change; adopt deliberately; undo |
| D | Submit is blocked by each blocker in turn, with the reason and the way to clear it |
| E | `PIN_DIFFERS`: blocked; reconcile by pin; reconcile by a new condition version |
| F | Author submits, checker approves, publisher publishes — three signed-in people; each refused the others' step |
| G | Version 2 supersedes version 1; version 1 still readable; compare and impact over the suite |
| H | Recorded evaluation reopened later: identical |
| I | Read-only, unauthorised and other-market refusals |
| J | No legacy assignment table and no case table changed (digest comparison) |

Not claimed in advance: tasks performed by people, and screen-reader sign-off.

## 7. Proposed implementation roadmap

| Step | Content | Stop |
|---|---|---|
| X4-0 | Specification: document shapes, `0040`, operation list, blocker table, journeys | owner approval of the specification |
| X4-1 | Migration `0040` and domain services, test schema only | — |
| X4-2 | Scenario and suite persistence, snapshots, adoption; scenario lab on the server | — |
| X4-3 | Recorded runs, impact, comparison | — |
| X4-4 | Candidates, three-person lifecycle, blockers including `PIN_DIFFERS` and profile mismatch | — |
| X4-5 | Frontend governance page, version history, comparison | — |
| X4-6 | Prototype-operation removal after caller audit | — |
| X4-7 | Full regression on the test schema; report | **owner review before any development migration** |

Development migration `0040` and enablement would be a separate authorisation, as for `0038` and `0039`.

## 8. Risks and open items carried in

- **D-418 residue**: the creation race is established and fixed (document `66_…` §8); it stays open until the owner
  closes it. Voice Studio reliability issue (D-399 / D-406) open and untouched.
- An empty library item `draft_example` (no draft, no version) remains in development from the dependency
  demonstration; harmless, cannot be deleted through the governed API. APPL-X4 does not depend on it.
- Scenario documents will hold only synthetic fact values, but free-text names and notes exist: the specification
  should state that no real customer data may be entered, and the interface should say so.
- Suite size and run time: recorded results for large suites need a size limit and pagination from the start.

## 9. Questions for the owner

- **Q-1** One checkpoint, or two (X4a scenarios / suites / recorded runs; X4b governance and publication)? Two is the
  lower-risk reading: X4b's blockers depend on X4a's suites.
- **Q-2** Is an attached, passing suite mandatory for publication (proposed: yes), and is there a minimum size?
- **Q-3** Profile mismatch: reconciliation only, or governed acknowledgement for exploratory scenarios (proposed)?
- **Q-4** Confirm no `PIN_DIFFERS` override in APPL-X4.
- **Q-5** May a publisher publish a candidate whose pinned dependency has since been superseded by a newer
  published version (proposed: yes, with a visible notice — the pin is exact and still valid)?
- **Q-6** Confirm removal of the prototype operations as the last step of APPL-X4.

**Stop.** APPL-X4 is not started. No specification file beyond this assessment has been written.
