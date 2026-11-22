# EVAL-2A — Governed control applicability and coverage: implementation report

**Status: BUILT AND TECHNICALLY VERIFIED 2026-11-22, awaiting the owner's review. Not accepted. Uncommitted.**
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

{{VERIFICATION}}

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

{{SCREENS}}

This is a technical verification. It is not a business UX sign-off and not a screen-reader sign-off.

## 9. Regression results

{{REGRESSION}}

## 10. State

{{STATE}}

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
| Commits | everything from SS-03B to EVAL-2A is uncommitted | Owner |

## 12. Does EVAL-2A meet its acceptance criteria?

{{VERDICT}}

## 13. Stopped here

EVAL-2B, operational evaluation, voice integration and Script Studio migration were not started. Nothing was
committed or pushed.
