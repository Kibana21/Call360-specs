# EVAL-2A — Governed control applicability and coverage: implementation report

**Status: BUILT AND TECHNICALLY VERIFIED 2026-11-22, awaiting the owner's review. Not accepted.** The code was
committed and pushed by the owner during this work (see §10); that is not an acceptance.
**SIMULATION ONLY.** Nothing here evaluates a real call or a real application, writes an operational finding, or
establishes compliance. No model judges anything. Every control, obligation, condition, mapping, finding rule and
severity used is synthetic.

Authorisations: the owner's messages of 2026-11-22, "Accept EVAL-1, Enable Development and Authorize EVAL-2A" and
"Complete and Verify EVAL-2A Before Acceptance".
Companion documents: `39_…` (registry assessment and design, written before implementation), `41_…` (migration
`0034` compatibility and data preservation), contract `04_…` §18, decision register D-289…D-300, G-E8…G-E10.

---

## 1. EVAL-1 closure

| | Recorded as |
|---|---|
| EVAL-1 accepted as TECHNICALLY VERIFIED, simulation only | D-289. Not an approval of insurance compliance rules or operational evaluation |
| D-287 `ALL_REQUIRED` | D-290: approved as an explicitly declared deterministic operator for simulation and technical evaluation; not a universal insurance compliance policy. Implemented as ruled, with a 27-row truth table |
| D-288, seven subdecisions | D-291 and the reconciliation table in the register |

**D-288, one by one:**

| | Subdecision | Status |
|---|---|---|
| a | separate evaluation permissions | **Accepted** (named by the owner) |
| b | mapping governance reuses the survey edit / approve / publish permissions | Retained as a technical choice; not separately ruled. Who governs controls in the business: open |
| c | an evaluation is recomputed from its pins on every read | **Accepted** (follows from immutable, traceable, drift-aware records) |
| d | findings only for applicable controls | **NOT approved** — an interpretation with policy effect. Needs Compliance |
| e | a module left out by the survey's own condition leaves the control with insufficient evidence | Consistent with the approved rule 3; the underlying question is **NOT approved**. Needs Compliance |
| f | mapping authoring had no screen | **Closed** by the Controls and evidence builder |
| g | evaluation needs simulation only | Retained as a technical choice; not separately ruled |

## 2. Development migration `0033` (authorised; done)

| Safeguard | Result |
|---|---|
| Identity and revision | development schema `call360`, at `0032_survey_coordinated_sim` before |
| Inventory | 126 tables, 15,185 rows, 118 triggers, 49 functions, 43 permissions |
| Backup | `_db_backups/call360_dev_before_0033_20261122.dump`, SHA-256 `349dbbbaefee14f51264d232a0f90c67d22ec402ead0a8ac9fb9a0d598430918`; rows in archive = rows in inventory |
| Recovery | restore dry run clean; `RESTORE.md` has "Rolling 0033 back — recorded evaluations are not destroyed" |
| Additive | 126 → 132 tables; none removed; 124 of 126 pre-existing tables byte-identical (the others: `alembic_version`, and `permission`, which gains two rows); column definitions identical |
| Empty-schema up and down | tested (`test_zz_migration_0033_…`) |
| Downgrade guard | refuses with a published mapping, and — added for this — with any recorded evaluation; both tested |
| Permissions | the two new permissions are held only by the three synthetic development identities (author: read and evaluate; checker and publisher: read) |
| Enabled in development only | `SURVEY_EVALUATION_ENABLED=true` in the gitignored `.env` |
| Demonstration | two synthetic mappings governed by three people; one single-survey and one coordinated-journey evaluation, with findings from the existing synthetic rule set of development |
| Operational, Script Studio, control register, finding rules | unchanged (counted before and after) |
| Reset or re-seed | none |

Because development now holds two mappings and two evaluations, `0033` can no longer be downgraded there; the ways
back are switching the setting off or a full restore. Evidence: `docs/acceptance/evidence/EVAL-2A/dev-migration-0033/`.

## 3. The existing Control Registry (assessment)

`39_…` Part 1. In short: a control is a code, a name, an owner role and an approval status. Five rows, all seeded
and `SYNTHETIC_UNAPPROVED`. No market, no purpose, no lifecycle, no revisions, no applicability, no evidence
requirement, and no API or screen that changes it. Its question links are all `PROPOSED`.

**The register is not replaced, copied or edited.** EVAL-2A adds beside it one governed artifact, the control
policy.

## 4. What was built

    control (register, unchanged)
    control policy revision    WHAT must be assessed, WHEN, with WHAT EVIDENCE        new
    control mapping revision   WHICH published survey items supply it, under WHICH rule    EVAL-1
    published survey versions

| | |
|---|---|
| Control policy | one immutable revision per market and code; scope statement and optional scope condition; declared complete or partial; for each register control its purpose and one or more **obligations**; each obligation has an applicability condition, the combination `ALL_REQUIRED`, and evidence requirements. Three different people propose, approve and publish (service and database trigger) |
| Applicability | for a synthetic application: each obligation is required, not applicable or unknown, with the facts read and the facts missing; a deterministic fingerprint; lineage labelled unverified |
| Evaluation under a policy | the control instances are the policy's obligations — not whatever happened to be mapped. Evidence is observed and combined exactly as in EVAL-1 |
| Coverage | for each instance and for the journey; separate from the evaluation's processing status, from each control's outcome, and from operational compliance eligibility (always not established) |
| `SET_MATCH` | a multiple-choice answer compared as a set, in the existing answer evaluator |
| Controls and evidence builder | `/survey-studio/controls`: the register, policies and mappings; drafting, trying out, proposing, approving and publishing, without writing JSON |

**Backend:** migration `0034_survey_control_policy` (purely additive; test schema only);
`app/domain/survey/control_policy.py`, `policy_evaluation.py` (pure); `journey_evaluation.py` and
`control_mapping.py` extended; `app/domain/answer_evaluation.py` gains `SET_MATCH` (the only change to an existing
engine, on the owner's decision); `app/api/survey_control_policies.py` (10 operations); setting
`survey_control_policy_enabled`, off by default. **Frontend:** `persist/ControlBuilder.tsx`, policy-aware
`persist/EvaluationWorkbench.tsx`, `persist/evalApi.ts`. Script Studio files and the finding engine were not touched,
and Script Studio's list of expected-answer policies is unchanged (tested).

## 5. Coverage semantics

Contract §18.4–§18.5; truth tables in `tests/test_survey_control_policy.py` (14 instance rows, 14 journey rows).

| Instance coverage | Meaning |
|---|---|
| `EVIDENCED` | required, mapped, and every required piece of evidence has a deterministic result |
| `EVIDENCE_MISSING` | required and mapped; required evidence is missing |
| `NOT_MAPPED` | required; no governed mapping supplies its evidence, or the mapping is inconsistent with the policy |
| `APPLICABILITY_UNKNOWN` | whether it applies could not be decided |
| `EVIDENCE_CONFLICTING` | the same question was answered differently |
| `EVALUATION_UNSUPPORTED` | no evaluation exists for the evidence or the combination |
| `HUMAN_ASSESSMENT_PENDING` | evidence exists and needs a person |
| `INTEGRITY_FAILED` | the evidence or replay could not be trusted |
| `NOT_REQUIRED` | not applicable |

**`COMPLETE_WITHIN_POLICY_SCOPE` and `SATISFIED` are different statements.**

| | Says | About |
|---|---|---|
| `SATISFIED` | this obligation's required evidence all matched its governed rule | one control instance |
| `COMPLETE_WITHIN_POLICY_SCOPE` | every obligation the policy requires for this application has trustworthy, evaluable evidence | the journey, inside one policy's declared scope |

Coverage can be complete while a control is `NOT_SATISFIED` — tested at engine level and through persisted
simulations (a revised mapping turns a control `NOT_SATISFIED` and coverage stays complete). Coverage is asserted
only under a policy that is declared complete, for an application inside its scope, with trusted evidence and no
unknown applicability; a partial policy never asserts it; an application to which nothing applies is not "covered"
unless the policy expressly says so; and it is never inferred from every question having been answered (a test
answers every question of a completed survey and gets `INCOMPLETE`).

**A synthetic `DECLARED_COMPLETE` policy claims nothing wider than itself.** The result names the register controls
outside the policy; the explanation says "within this policy's declared scope … not a statement that they are
satisfied"; the policy screen says "It is not an approved compliance policy, and being complete under it says nothing
about regulatory coverage"; operational compliance eligibility is `NOT_ESTABLISHED` on every evaluation.

## 6. `SET_MATCH`

Contract §18.6. Built in `answer_evaluation.py` as approved (D-299).

| Requirement | How |
|---|---|
| modes | `INCLUDES_ALL`, `INCLUDES_ANY`, `INCLUDES_NONE`, `EQUALS` |
| option codes validated against the published option set | expected options at configuration (by the existing `configure`); submitted options by the survey engine (`UNKNOWN_OPTION`) and again by the evaluator |
| order-independent | compared as sets; the normalised answer is in the question's own option order; two selections in different orders are the same answer |
| duplicates | defined and enforced: a duplicate in the expected set is refused; a submitted duplicate is refused by the survey (`DUPLICATE_OPTION`), and a selection with one that reached the evaluator is `UNRESOLVED` — never collapsed |
| explicit empty selection | an accepted empty selection is an answer and is evaluated; whether a question permits one is the question's own rule |
| unanswered and rejected | `NOT_ASKED` and `UNRESOLVED` with the refusal codes — never an empty selection |
| unsupported configurations | refused at configuration with the reason; a malformed rule that reaches the evaluator gives `NOT_EVALUATED` |
| tests | 20-row truth table; configuration tests; adapter tests; a persisted-simulation test |

One limit: the published multiple-choice fixture requires at least one choice, so an **accepted** empty selection is
tested at engine level; through persisted simulations the empty selection is shown being refused by the survey
(`TOO_FEW_SELECTED`) and staying distinct from an answer. `SET_MATCH` is not shown in the browser journey.

## 7. Verification

Backend tests run on the isolated test schema (`call360_test`), through real HTTP and PostgreSQL unless marked
pure. P = `tests/test_survey_control_policy.py`, E = `tests/test_survey_evaluation.py`, B = the browser journey
`e2e/persisted/zz-eval2a.persisted.ts`.

| The owner's point (§5 of the second message; numbers from Step 9 of the first) | Where | Result |
|---|---|---|
| Three-person control-policy governance (1, 2) | P `…is_governed_and_a_journey…`; B (each step in the browser by a different person) | self-approval, self-publication and approver-publication refused by the service; the database trigger refuses a forged event; three distinct people recorded |
| Market isolation and authorisation of reads and mutations (16) | P; B | each permission checked separately; another market gets 404 and empty lists; no CSRF token → 403; denials audited; audit chain verifies |
| Immutability, publication, supersession, withdrawal | P `…is_governed…`, `…history_survives…` | `UPDATE` and `DELETE` refused by the database; revision 2 supersedes revision 1; a withdrawn revision stays as a record and cannot be evaluated under |
| Publication and review-history retrieval | P; B | history returned by the single read and by the list (the list omitted it in the first build; fixed and tested) |
| Policy-scope and obligation applicability, including UNKNOWN (3, 4) | P pure and HTTP; B | required / not applicable / unknown from application facts; missing inputs named; scope `OUT_OF_SCOPE` and `UNKNOWN`; fingerprint stable |
| One control, several obligations, not collapsed (9) | P pure and HTTP | `SYN-CTRL-01` with obligations `IDENTITY` and `OPENING` gives two results, each with its own evidence; two rows stored |
| One obligation evidenced by several surveys (8) | P `…two_surveys_give_one_control_instance…`; B | one instance, two observations, two simulations |
| Contradictory answers from two persisted published surveys (10) | the same test; B | two different published surveys pin one published question revision; answered 20 and 30; `REQUIRES_REVIEW`, coverage `EVIDENCE_CONFLICTING`; both observations and both execution identities kept; neither answer chosen |
| Coverage from the declared policy scope, not from mapped items (5, 6, 7) | P pure and HTTP | a required control nobody mapped is found from the policy; every question answered and the survey completed, coverage `INCOMPLETE`; a `PARTIAL` policy never asserts completeness |
| Missing required evidence and its governed finding | P; B | `INSUFFICIENT_EVIDENCE` / `EVIDENCE_MISSING`; the finding comes from the existing rule set and says the evidence is missing |
| Missing or inconsistent mappings | P pure | no mapping; a required requirement unmapped; an entry bound to nothing, to a requirement the policy lacks, or with another evidence type — all `NOT_MAPPED`, with the reason |
| Untrusted evidence and replay drift | P pure; P `…history_survives…` (persisted) | `FAILED_TECHNICALLY`, every instance `INTEGRITY_FAILED`, coverage `NOT_ASSERTED`, no finding; a recorded evaluation reads as `EVALUATION_DRIFT` and its record is not rewritten |
| Historical evaluations unchanged after mapping or policy revisions (15) | P `…is_governed…`, `…history_survives…` | old evaluations keep their fingerprint, recompute from what they pinned, and say what is published now that they did not use |
| Browser mapping authoring, trial, approval, publication (12) | B | built from a published question in the builder; the trial shows the conflict before anything is proposed and records nothing; three people |
| Multi-select `SET_MATCH` | P truth table (20), configuration, adapter, and `…through_persisted_simulations` | §6 |
| Complete coverage is not satisfaction | P pure and `…history_survives…` | coverage `COMPLETE_WITHIN_POLICY_SCOPE` with a control `NOT_SATISFIED` |
| A `DECLARED_COMPLETE` synthetic policy implies nothing wider | P `…history_survives…`; B | §5 |
| The Evaluation Workbench shows all evidence and coverage gaps (11) | B | coverage, evaluation status and eligibility shown separately; both responses on one control; missing inputs named |
| The existing engines stay authoritative; no unapproved severity or disposition (13, 14) | P, E | engines recorded on every evaluation; the finding engine is called only under its governed rules — one finding for the mismatch, none for the conflict |
| No operational evaluation, finding or case (17) | P, E | operational table counts identical; `record_class` `SIMULATION` |
| Existing single- and multi-survey evaluations (18) | E; `zz-eval1` | pass unchanged in behaviour |

**Limits of these demonstrations.** `SET_MATCH` is not in the browser journey. An accepted empty selection is tested
at engine level only (§6). The persisted drift test changes the execution engine's output inside the test; drift of a
journey under a policy by any other cause is covered at engine level.

## 8. The Controls and evidence builder

`/survey-studio/controls`, linked from the Survey Studio home and from the Evaluation Workbench.

| The owner asked that the screen communicate | Where |
|---|---|
| what the control requires | the control page lists every policy that requires it: purpose, each obligation in a sentence, the evidence needed |
| which obligations are applicable | "Try it on an invented application": required, not applicable or unknown for each obligation, with what is not known |
| which questions provide evidence | the mapping builder: for each piece of required evidence, the published question or statement, how its answer is judged, and the surveys it is asked in |
| why evidence is insufficient or conflicting | the trial and the workbench give the reason in a sentence for each control; "not mapped" is marked on the requirement |
| what the trial demonstrates | stated above the trial: how the answers already recorded in one journey would be judged — not that the mapping is right for every journey; nothing recorded |
| what is approved versus synthetic | "Synthetic — not approved content" on each control; "Synthetic, for simulations only … not an approved compliance policy" on each policy |
| which governance action is available now | one "what happens next" line on every policy and open mapping: who must act, and whether it is you |

Density: names lead; control codes, obligation and evidence keys, combination codes, reason codes and fingerprints
are in closed "Technical details". Not changed: the layout and components are the existing Survey Studio ones. The
policy form still asks for a short reference key for each obligation and each piece of evidence.

Screenshots (real browser, isolated test database): `docs/acceptance/evidence/EVAL-2A/screens/`.

| File | Shows |
|---|---|
| `EVAL2A01-invalid-policy-says-why.png` | a proposal refused, with what is wrong and where |
| `EVAL2A02-policy-builder-tested-on-an-invented-application.png` | the policy form, a governed applicability condition, and required / not applicable / unknown for an invented application |
| `EVAL2A03-policy-published-by-a-third-person.png` | the published policy in words, what is synthetic, what happens next, the three-person review |
| `EVAL2A04-mapping-builder-trial-shows-the-conflict.png` | the mapping builder, the implication of a shared question, and a trial showing the conflict |
| `EVAL2A05-coverage-separate-from-outcome-and-eligibility.png` | the workbench: evaluation status, coverage and eligibility as three statements |
| `EVAL2A06-one-control-two-surveys-conflicting-answers.png` | one control instance, two surveys, answers 20 and 30 |
| `EVAL2A07-required-control-missing-evidence-and-finding.png` | a required control with missing evidence and its finding |

This is a technical verification. It is not a business UX sign-off and not a screen-reader sign-off.

## 9. Regression results

| Check | Result |
|---|---|
| Full backend suite (`call360_test` only) | **917 collected; no failure or error reported** (831 before) |
| 82 golden execution runs | pass; fixture files unmodified |
| 14 golden call plans | pass; fixture files unmodified |
| Frontend unit suite | 612 passed |
| Persisted browser suite | **24 passed** (23 + the EVAL-2A journey) |
| Prototype browser suite | 13 passed |
| Standard browser suite | 33 passed |
| `ruff check`, `ruff format --check`, `mypy app` | clean (120 source files) |
| `tsc`, `eslint`, production build | clean |
| OpenAPI additivity | 266 operations, 505 schemas; against the contract committed before this series (backend `182f6e5`): no operation, schema or property removed, no property changed, no existing property newly required, no parameter changed. SHA-256 `91ed256edb81ccec6124a5db25bc4223c7da06854e8a4fa5926433847806d62c` |
| Specs validator | passes |
| Migration up and guarded downgrade | `41_…` §4; `0033` and `0034` guards tested |

How the backend result was read: the project runs pytest quietly and prints no totals line. The run was made with
failure reporting on and printed no failed or errored test; the count is from collection.

Failures met on the way, and their causes (none was resolved by changing an expectation of behaviour):

* Eight structural tests pin the migration head, the set of survey tables and the contract size. They were updated
  to state the new head, the six new tables and the new counts.
* Two of my own earlier tests asserted that multiple choice is unsupported. With `SET_MATCH` approved, they now use
  an answer kind that has no method.
* Two browser tests located a control by "its `summary`"; the new "Technical details" expander made that ambiguous.
  The locator now names the control's own summary.
* One new test took the schema reset after a database session had opened and waited on its own lock; the fixture
  order was corrected.
* No golden fixture, and no golden expectation, was modified.

Evidence: `docs/acceptance/evidence/EVAL-2A/` (`backend_checks.txt`, `frontend_checks.txt`, `openapi_additivity.txt`,
`playwright_persisted.txt`, `playwright_prototype.txt`, `playwright_standard.txt`, `specs_validator.txt`,
`dev-migration-0033/`, `screens/`).

## 10. State

| | State |
|---|---|
| **Development database** | **`0033_survey_control_evaluation`.** No `0034` object. Two synthetic mappings, two evaluations (both still read and recompute identically under the EVAL-2A code — checked read-only) |
| **Test schema** | `0034_survey_control_policy` (head) |
| Features on in development | survey definitions, library, simulation, assignment, requirement groups, coordinated simulation, **evaluation** |
| Features off in development | **control policies** (`survey_control_policy_enabled`): the operations answer 404; the builder shows the register and mappings and says policies are not switched on; the workbench offers no policy choice |
| Features on in the browser test suite | all of the above, and control policies |
| Development identities | author: evaluation read and evaluate; checker, publisher: evaluation read. No other role holds them |
| `Call360-backend` | `main` at `ed3e51b` — **committed and pushed by the owner** on 2026-11-22 15:52 while this work was in progress; working tree clean; it contains everything of SS-03B … EVAL-2A as verified here |
| `Call360-frontend` | `main` at `e79c4e0` — committed and pushed by the owner at the same time; working tree clean |
| `Call360-specs` | `main` at `c43f4f5` — committed and pushed by the owner; six files changed after that commit are uncommitted (this report, the README index, the session handoff and three evidence files) |
| Commits by the assistant | none. Nothing was committed or pushed by me |

## 11. What remains unapproved

| | Open | Who |
|---|---|---|
| D-291 d | whether findings are wanted while a control's applicability is unknown | Compliance |
| D-291 e | whether a survey's own exclusion can make a control not applicable | Compliance |
| D-291 b | whether control governance is held by other people than survey governance | Business governance |
| D-300 | the ten EVAL-2A choices, among them: a policy set with obligations; the two extra coverage values; an EVAL-1 mapping must be re-proposed to count under a policy | Owner |
| G-E1…G-E7 | as recorded in EVAL-1 (G-E5, multiple choice, is closed by `SET_MATCH`) | — |
| G-E8 | effective dating of control policies | Business governance |
| G-E9 | a policy's scope beyond a statement and one condition | Business, Compliance |
| G-E10 | every control, obligation, condition, mapping and rule is synthetic | Compliance |
| OR-1, OR-2, OR-3, input mapping | unchanged | — |
| Development migration `0034` | not requested, not done | Owner |
| Commits | the owner committed the code himself; six specs files changed since are uncommitted | Owner |

## 12. Does EVAL-2A meet its acceptance criteria?

**Technically, yes — with the limits stated here. Acceptance is the owner's.**

| Criterion | Met? |
|---|---|
| The existing Control Registry stays authoritative | yes — not altered |
| Governed, market-scoped policy revisions define the applicable controls and their obligations | yes |
| Survey evidence mappings stay separately governed | yes |
| One journey evaluation uses evidence from several surveys; one control has several obligation instances | yes |
| Coverage, control satisfaction, evaluation processing and operational eligibility are separate | yes |
| Simulation only | yes |
| Historical evaluation evidence is not compromised | yes — `0034` alters no existing table; verified over a populated schema, with a forced failure |
| `SET_MATCH` as authorised | yes; not shown in the browser |
| EVAL-1 decision closure, all seven D-288 subdecisions | recorded; two remain unapproved by design |
| All regressions | pass |
| Business-user interface | builder retained and clarified; not a UX sign-off |

Not met, because not done or not decidable here: development is not migrated to `0034` (not authorised), so control
policies cannot be used in development yet; the two D-288 interpretations (d, e) and the ten D-300 choices await
decisions; every policy, obligation and mapping is synthetic.

## 13. Stopped here

EVAL-2B, operational evaluation, voice integration and Script Studio migration were not started. I committed and
pushed nothing.
