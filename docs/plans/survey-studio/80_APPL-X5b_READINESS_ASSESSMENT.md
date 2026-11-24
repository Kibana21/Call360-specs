# 80 — APPL-X5b readiness assessment: journey evaluation, findings, assurance and evidence trace

**An assessment only. Nothing here is built and nothing here is authorised. No X5b migration exists.**
Date 2026-11-25. Simulation only; synthetic data only. Builds on APPL-X5a as built (`78_…`).

Every control, obligation, mapping and finding rule in the test data is synthetic. Nothing an evaluation says is a
compliance conclusion; eligibility stays `NOT_ESTABLISHED` throughout.

---

## 1. What X5b is

For a synthetic applicability journey of X5a: evaluate the recorded answers under one exact control policy, produce
findings, check that what was executed is what the frozen selection plan required, and show the whole chain — policy
version, facts, plan, surveys, answers, evaluation, findings, assurance — as one read-only trace.

## 2. What exists and how it is shaped

| Piece | Where | Shape | Reusable for an applicability journey |
|---|---|---|---|
| Control evaluation (pure) | `control_evaluation.py` — `adapt`, `observe`, `evaluate_journey`; `ALL_REQUIRED` (D-287); outcomes SATISFIED … REQUIRES_REVIEW | works on the evidence of survey runs under mappings | **yes, unchanged** — it reads simulation evidence, not selection |
| Policy-scoped evaluation (pure) | `policy_evaluation.py` — `determine`, `evaluate_under_policy`, coverage | one exact control-policy revision | **yes, unchanged** |
| Answer evaluation, finding engine | `answer_evaluation.py`, `finding_engine.py` | script-shaped inputs (a `question_controller`), used through the survey adapters | used only through the adapters; **not to be edited**, and no need to |
| Journey evaluation (persisted) | `journey_evaluation.py` — `journey_of(simulation_id, coordinated_id)`, `create(…, policy_id=)` | table `survey_journey_evaluation` with CHECK `journey_kind IN ('SINGLE_SURVEY','COORDINATED')` and exactly one of `simulation_id` / `coordinated_id` | **needs a third way to name its subject** |
| Results and findings | `survey_control_result`, `survey_evidence_observation`, `survey_evaluation_finding`, `survey_obligation_*` | hang off the evaluation | yes, unchanged |
| Execution assurance (pure) | `execution_assurance.py` — `verify_survey`, `verify_coordination`, `assure_journey`; statuses VERIFIED … NOT_ASSESSABLE | `verify_survey` is per simulation; `verify_coordination` compares against a **legacy composite plan's** selection | `verify_survey` yes; `verify_coordination` needs an equivalent over the selection plan |
| Assurance records | `survey_execution_assurance`, `survey_execution_assurance_survey` | the same `journey_kind` CHECK | **needs the same extension** |
| Journey trace | `journey_trace.py`, read-only, no table | selection links read rule versions and bindings directly | needs an applicability branch |

## 3. Exact evaluation source

An X5b evaluation names, and records the fingerprints of:

1. the **applicability journey** (id, status, revision at evaluation);
2. its **selection plan** (plan fingerprint, policy version id and fingerprints, fact fingerprint);
3. its **start record** (survey-fact fingerprint, correspondence);
4. each step's **simulation** with its last run fingerprint and input count;
5. the journey's **verification result** at that moment.

A journey that does not verify is not evaluated (`NOT_ASSESSABLE`), and says why. A journey still running may be
evaluated only if the owner wants interim evaluation (Q-b3); otherwise evaluation is of an ended journey — including
one that ended unresolved, which is evaluable evidence in its own right.

## 4. Control-policy version pinning

- The evaluation names **one exact control-policy revision**, chosen explicitly; never "the latest".
- The policy, its mappings and its rules are frozen in the evaluation record, as EVAL-2A already does.
- A control policy is a different artefact from an Applicability Policy; neither pins the other. Which control policy
  applies to which applicability policy is **not modelled** and is not invented here (Q-b4).

## 5. Per-requirement completion and shared delivery

X5a already states, per requirement, `SATISFIED`, `NOT_SATISFIED` or `NOT_REQUIRED`, with the reason. X5b adds the
evaluation view of the same structure:

| Requirement | Evaluation |
|---|---|
| selected, survey completed | the survey's control results count for this requirement |
| selected through a **shared delivery** | the **same** simulation's results count for each requirement it was declared for; they are computed once and referenced, never duplicated or re-asked |
| selected, survey not completed | `INSUFFICIENT_EVIDENCE` for what the survey would have collected; the exact terminal reason carried from the journey |
| selected, survey not started (cross-survey unresolved) | `INSUFFICIENT_EVIDENCE`, reason "not started: no governed continuation" |
| replaced | not evaluated; the replacing requirement is |
| not applicable | `NOT_APPLICABLE` |

An obligation count greater than one never multiplies findings.

## 6. Findings

Generated by the accepted finding rules through the existing survey adapter, per simulation, with deterministic
finding keys. The applicability journey adds context only: journey, step, requirement(s). A finding from a shared
delivery lists every requirement it bears on. No new finding class is proposed.

## 7. Assurance against the frozen selection plan

The equivalent of `verify_coordination`, over applicability records — a pure function:

- every selected survey has exactly one step, at the pinned version and fingerprints;
- no step exists for a survey that was not selected, was replaced or was pending;
- the order is the plan's;
- a step started only after every earlier one completed;
- a shared delivery is one execution;
- each step's `verify_survey` holds;
- the journey's own verification holds.

Most of this is already what X5a's `verify` checks; X5b records it as an assurance record with the existing statuses,
so the two must be one implementation, not two (the X5a function becomes the single source).

## 8. Can the journey-kind extension be backward compatible? — yes

Two accepted tables carry `CHECK (journey_kind IN ('SINGLE_SURVEY','COORDINATED'))` and "exactly one of
`simulation_id`, `coordinated_id`".

**Proposed minimal additive migration (`0043`, not created):**

| Change | On | Effect on existing rows |
|---|---|---|
| add nullable `applicability_journey_id uuid REFERENCES applicability_journey` | `survey_journey_evaluation`, `survey_execution_assurance` | none: `NULL` for every existing row |
| replace the kind CHECK by one that also allows `'APPLICABILITY'` | both | none: every existing value is still allowed |
| replace the "exactly one" CHECK by "exactly one of three", tied to the kind | both | none: every existing row has exactly one of the two old columns and `NULL` in the new |
| extend the two insert guards, if they name the kinds | both | none |

- No existing column changes type or nullability; no existing row is rewritten; the meaning of `SINGLE_SURVEY` and
  `COORDINATED` rows is untouched.
- A downgrade is possible while no `APPLICABILITY` row exists and refused otherwise.
- Replacing a CHECK takes a brief exclusive lock and a table scan; trivial at this size, to be stated at enablement.
- Every reader that switches on `journey_kind` must be reviewed: unknown kinds must be handled explicitly, not fall
  into a default branch. This is the real work of the change, and is listed for the X5b specification.

**Alternative:** parallel tables for applicability evaluations. No accepted table is touched; every reader, screen and
test of evaluation is duplicated or generalised. Recommended only if the owner does not want accepted constraints
replaced.

This is a change to accepted tables and needs the owner's explicit approval before any specification is final (Q-b1).

## 9. Immutable evaluation and finding evidence

Unchanged from EVAL-1/2: an evaluation, its results, observations and findings are insert-only and fingerprinted; a
re-evaluation is a new record. X5b adds the source fingerprints of §3 to the evaluation record, so an evaluation can
be shown to be of exactly one state of exactly one journey.

## 10. End-to-end applicability journey trace

Read-only, as now, with an applicability branch — no rule version, binding, group or composite plan in it:

`published Applicability Policy version` → `synthetic application facts` → `selection plan (selected, pending,
replaced, shared)` → `fact correspondence and survey facts` → `survey versions` → `steps and simulations` → `answers`
→ `control policy` → `evaluation, control results` → `findings` → `execution assurance`.

- `selection_source` shown on every trace: `APPLICABILITY` here, `LEGACY_ASSIGNMENT` for the existing kinds.
- **Eligibility: `NOT_ESTABLISHED`, explicitly, on every trace** — nothing in a simulation establishes that a real
  application is eligible for anything.

## 11. Negative regression against legacy coordination

To be proven in X5b, as in X5a:

- every existing `SINGLE_SURVEY` and `COORDINATED` evaluation, assurance record and trace reads and verifies exactly
  as before the migration (digests of every existing row unchanged);
- the legacy coordinator's tests pass unchanged;
- an applicability evaluation creates no rule, binding, group, composite plan or coordinated simulation;
- the golden 82 runs and 14 plans unchanged;
- the three engines that must not be edited are not edited.

## 12. Decisions needed before APPL-X5b can be specified

| # | Question | My recommendation |
|---|---|---|
| Q-b1 | Extend the two accepted tables additively (§8), or use parallel tables | extend, with explicit approval |
| Q-b2 | Permissions | reuse `survey.evaluation.read` and `survey.evaluate` with the journey's read permissions; no new grant. A test identity holding the combination will be needed — to be approved, as in X5a |
| Q-b3 | May a journey that is still running be evaluated | no: ended journeys only, including unresolved ones |
| Q-b4 | Which control policy applies to a journey | chosen explicitly by the person each time; no association modelled |
| Q-b5 | Is an unresolved or abandoned journey evaluated | yes — as insufficient evidence with its exact reasons; never as a pass |
| Q-b6 | One evaluation per journey, or many | many, each immutable, each naming its control-policy revision |

## 13. Not part of APPL-X5b

Operational application facts (APP-1a), a survey for a real case (OPS-1), VOICE-0 and VOICE-1, Genesys, designer
integration steps 2–4, legacy retirement, any approved compliance meaning for a synthetic finding.
