# EVAL-1 — Existing evaluation engines: assessment, reuse matrix and design decisions

**Written before implementation**, as the owner's authorisation of 2026-11-22 requires ("Step 1 — Mandatory
existing-engine assessment … before designing new evaluation functionality"). The implementation report is `38_…`.
**Simulation only.** Nothing here evaluates a real call or creates an operational finding.

Sources read for this assessment: `app/domain/answer_evaluation.py`, `finding_engine.py`, `finding_rules.py`,
`simulation_evaluation.py`, `simulation_findings.py`; migrations `0005` (control, control mapping) and `0023`
(finding rule sets, simulation findings); the seeded content; `app/api/finding_rules.py`,
`app/api/simulation_workbench.py`; the frontend `features/simulator` and `features/findings`.

---

## Part 1 — Assessment

### 1. Existing control and evaluation concepts

| Concept | What it is today | Where |
|---|---|---|
| **Control** | a row: `control_code` (unique), `name`, `owner_role`, `content_approval_status`. A label that questions are linked to | table `control` (migration `0005`) |
| **Control mapping** | question-bank item ↔ control, with rationale, optional regulatory reference, status `PROPOSED` / `ACTIVE` / `RETIRED` | table `control_mapping`; copied into frozen script content as `question.controls[]` |
| **Evaluation rule** | lives **inside a script question revision**: `expected_answer_policy` (the method), `expected_value`, `policy_fact_key` | script content; `answer_evaluation.Rule` |
| **Answer evaluation** | one deterministic result per question of one execution | `answer_evaluation.evaluate_one` |
| **Finding rule set** | per market, versioned, governed; each rule: scope (`QUESTION`, `CONTROL`, `ANY_QUESTION`), trigger, category, description, severity with justification, review flag | table `finding_rule_set_version`; `finding_engine`, `finding_rules` |
| **Finding** | an answer-evaluation outcome that a finding rule converts, with a deterministic key | `finding_engine.generate` |
| **Materiality** | a governed code list of severities that make a finding a protected review outcome | `finding_materiality_policy`; used by `review.py` (operational review routing, S3-C) only |

**There is no control-level result anywhere in Call360.** A control is satisfied, unsatisfied or applicable nowhere:
it is a tag on questions and a way for a finding rule to address a group of questions. This is the central finding
of the assessment.

### 2. The current evaluation grain

`(execution, script question)`. One answer-evaluation result per planned question of one run; findings are per
`(execution, finding rule, question, trigger)`. The persisted simulation records (`simulation_answer_evaluation`,
`simulation_finding_set`) are keyed by a **Script Studio simulation run** and a **script version**; the operational
`finding` table by a **callback case** and a **question execution**.

### 3. Input schemas and execution identity requirements

`evaluate_one(rule, status, applicable, skip_reason, answer, unresolved_reason, facts)`:

| Input | Shape | Comes from, today |
|---|---|---|
| `rule` | `Rule(question_code, question_revision_id, revision, method, answer_type, options, expected, fact_key)` | a script question revision |
| `status` | the question controller's final item state: `COMPLETED`, `UNRESOLVED`, `PENDING`, `REQUESTED`, `SKIPPED_BY_CONDITION`, … | `question_controller` |
| `applicable`, `skip_reason` | whether an approved condition excluded the question | the controller's plan |
| `answer` | `{answer_kind: ANSWER\|UNCLEAR\|…, answer_state, value, verbatim}`; `value` is a bool, a number or a choice | the controller's last recorded answer |
| `unresolved_reason` | `REFUSED`, `UNKNOWN`, `RETRY_LIMIT`, `UNCLEAR_ANSWER` | the controller |
| `facts` | `FactSource(kind, ref, sha256, facts)`; fact keys are `premium_term_years`, `premium_amount`, `premium_frequency` | a policy fact snapshot or scenario facts |

Answer types it knows: `YES_NO`, `NUMERIC`, `ENUM`, `FREE_TEXT`, `ACKNOWLEDGEMENT`. Methods: `EXACT_BOOLEAN`,
`ACKNOWLEDGEMENT`, `NUMERIC_COMPARE`, `NUMERIC_MATCH_POLICY_FACT`, `ENUM_MATCH`, `ENUM_MATCH_POLICY_FACT`,
`COLLECT_ONLY`, `NARRATIVE_REVIEW`.

`generate(evaluations, content, rules, context)` needs, per evaluation, `question_code`, `result`, `mandatory`, and
the answer and explanation; from `content` only the controls linked to each question; from `context` an
`execution_ref` (it goes into the finding key).

### 4. The lifecycle today

    question controller  →  answer_evaluation.evaluate        (per question: MATCH, MISMATCH, UNRESOLVED, NOT_ASKED,
                                                               MISSING_EXPECTED_FACT, NOT_APPLICABLE, NOT_EVALUATED,
                                                               HUMAN_ASSESSMENT_REQUIRED)
                         →  finding_engine.generate            (triggers → findings by the published rule set;
                                                               a trigger no rule covers is "not converted")
                         →  simulation_finding_set             (Script Studio simulation)  or  finding (operational)
                         →  review routing by materiality      (operational only)

A `MATCH` is never a compliance pass; a `MISMATCH` is "a discrepancy for review, not a breach finding".

### 5. Authoring, approval and versioning

| Artifact | Governance |
|---|---|
| Evaluation rule of a question | part of the script version: maker, checker, publisher; frozen with the script |
| Finding rule set | `DRAFT → SUBMITTED_FOR_REVIEW → APPROVED → PUBLISHED → SUPERSEDED`, maker-checker, one published per market, `rules_sha256` |
| **Control** | a mutable row with `content_approval_status`. **No version, no revision, no lifecycle.** |
| Control mapping (question bank) | a status column; no versioning |

### 6. Reliance on script question identities and case identities

* Evaluation rules are addressed by **script question code and revision**.
* `QUESTION`-scope finding rules address a question by code (pattern `Q-…`); `CONTROL`-scope rules address the
  questions linked to a control in the **script content**.
* The simulation records require a **script simulation run**; the operational ones a **callback case**.
* Nothing in the two pure engines themselves reads a case or a script: they take plain values.

### 7. What can be reused without operational writes

| Component | Pure? | Reusable for journeys | How |
|---|---|---|---|
| `answer_evaluation.evaluate_one` | yes | **yes, unchanged** | called with a `Rule` built from a governed mapping entry and an answer translated from SS-03B evidence |
| `answer_evaluation.configure` | yes | **yes, unchanged** | validates the rule of a mapping entry when it is proposed |
| `answer_evaluation.describe_rule`, `RESULTS`, `ENGINE` | yes | yes | wording and vocabulary |
| `finding_engine.generate` | yes | **yes, unchanged** | called with those evaluations, a control map built from governed mappings, and the market's published rule set |
| `finding_engine.RuleSet`, `finding_rules.published`, `finding_rules.rule_set` | read-only | **yes, unchanged** | the existing governed finding rules, as published |
| `finding_rules.*` authoring, Finding Rules screen | — | used as they are | finding rules are still made there |
| `answer_evaluation.evaluate` | pure, but needs a question controller and script content | no | it walks a script plan |
| `simulation_evaluation`, `simulation_findings` persistence | writes Script Studio simulation tables | no | keyed by script runs |
| `simulation_findings.persist_operational`, `review.py`, materiality routing | operational | **no — must not be used** | operational findings and review are excluded |

### 8. What survey and coordinated-simulation evidence provides

Per survey execution (one SS-03B simulation): the published version with content and manifest fingerprints; every
delivery with item `code@version`, wording version, delivery mode and exact text; every accepted answer with its
typed value; every refused input with its code; evidence states per placement (`ANSWERED`, `ANSWERED_EMPTY`,
`UNANSWERED`, `SKIPPED`, `DELIVERED`, `NOT_REACHED`); module statuses and outcomes; the terminal state; the full
event trace; the run fingerprint, execution contract and replay consistency. A coordinated simulation adds the
governed order, the state of each survey and why the coordinator went on or stopped.

It does **not** provide: an evaluation rule for any item; a link from any item to any control; the three policy
facts the existing fact methods read.

### 9. What is missing

| Missing | Consequence |
|---|---|
| A link from a published survey item to a control and to an evaluation rule | nothing can be evaluated; LIB-1 already recorded "evaluation and control metadata are not part of reusable assets" |
| A control-level outcome and its evidence-combination semantics | "control satisfied" has no approved definition |
| Control applicability rules | which controls apply to an application is nowhere governed |
| Control revisions | a control cannot be pinned by revision |
| An adapter from SS-03B evidence to the answer-evaluation input model | the two speak different vocabularies (§3 vs §8) |
| A mapping from the application's catalog facts to the evaluation fact keys | `…_MATCH_POLICY_FACT` methods cannot be fed |
| Multi-select answers in the evaluation model | no answer type or method for a set of choices |

### 10. Obstacles to a journey-level control evaluation

1. **Control satisfaction is undefined** (§1). Any rule for it is new.
2. **Applicability is ungoverned.** Complete compliance coverage cannot be asserted by anyone today.
3. **Controls are unversioned.**
4. **Finding keys assume one execution and one occurrence of a question.** A journey has several executions and a
   question can occur more than once.
5. **Two fact vocabularies** again (as in ASG-1): evaluation fact keys versus the survey fact catalog.
6. **The existing persisted evaluation is bound to Script Studio runs**, so a journey needs its own records.

---

## Part 2 — Design decisions that follow

### D-A. Grain

| Level | In EVAL-1 |
|---|---|
| Application | the synthetic application snapshot of the journey (its fingerprint) |
| Callback journey | the **evaluation run context**: one single-survey simulation, or one coordinated simulation |
| Survey execution | one SS-03B simulation: an evidence-producing sub-context |
| **Control instance** | **the atomic result grain: one control in one journey evaluation** |
| Evidence observation | one placement of one mapped item in one survey execution: an answer, a delivery, or its absence |

A single-survey simulation is a journey with one survey execution. Nothing is linked to a callback case.

### D-B. The governed control mapping (the missing link, §9)

A new governed artifact, **separate from question definitions**: a versioned mapping **per control**, proposed,
approved and published by three different people, immutable once proposed.

| Field | Meaning |
|---|---|
| control | the control (by id and code) and a **fingerprint of the control row** at proposal — the only "revision" a control has (§5) |
| `combination` | how the control's evidence combines. One value exists: `ALL_REQUIRED` (D-D) |
| `applicability` | none (the governors state it applies to every journey of the market), or a published Survey Studio **condition** with parameters, evaluated three-valued on the application's facts |
| `entries[]` | each: an exact survey **item** `code` and `version`; `evidence_type` `ANSWER` or `DELIVERY`; `required`; an optional context (`survey_code`) so that a reusable question can serve different controls in different surveys; and, for `ANSWER`, an evaluation **rule in the existing S3-A rule language**, validated by `answer_evaluation.configure` |
| `source` | provenance: where the mapping comes from |

No mapping is inferred from labels. An item that no published mapping names is reported as not mapped.

### D-C. The evidence adapter

SS-03B evidence → the existing input model, with no value invented:

| Survey evidence | `status` | `answer` | Existing result it leads to |
|---|---|---|---|
| accepted answer | `COMPLETED` | yes/no → bool; acknowledgement → bool; number; single choice → the code; text | by the rule |
| asked, an input was given and refused, or the non-answer policy is unresolved | `UNRESOLVED`, no reason claimed | none | `UNRESOLVED` — "never treated as a match" |
| the question is waiting and nothing has been said to it | `PENDING` | none | `NOT_ASKED` |
| not reached; not asked on the path taken; module skipped because information was missing; survey not started; the exact item revision is in no survey of the journey | `PENDING` | none | `NOT_ASKED` |
| module excluded by an eligibility condition that was **false** | `SKIPPED_BY_CONDITION` | none | `NOT_APPLICABLE` |
| multi-select answer | — | — | not evaluable: `UNSUPPORTED_EVIDENCE` (§9) |
| statement, `DELIVERY` evidence | not passed to the engine | — | `DELIVERED` / `NOT_DELIVERED`, recorded by the adapter |

A refusal reason is never claimed (`REFUSED` would be a business reading of a non-answer, which is undecided).
`UNKNOWN` never becomes `FALSE`: a module skipped for missing information is `NOT_ASKED`, not `NOT_APPLICABLE`.

### D-D. Control outcome — the one new semantic, and how it is kept honest

The existing engine has no control outcome (§1). The owner's conceptual outcomes are produced as follows; the
existing answer-evaluation vocabulary is kept on every observation, unchanged.

| Control outcome | When |
|---|---|
| `NOT_APPLICABLE` | the mapping's applicability condition is `FALSE` |
| `UNRESOLVED` | applicability is `UNKNOWN`; or the control has no published mapping; or the mapping's combination is not one this version supports; or it has no evaluable required evidence |
| `REQUIRES_REVIEW` (1) | the same mapped item gave different answers in different places (**evidence conflict** — nothing reconciles it, so no answer is chosen) |
| `NOT_SATISFIED` | combination `ALL_REQUIRED`, no conflict, and a required observation is `MISMATCH` |
| `INSUFFICIENT_EVIDENCE` | otherwise, when a required observation is `UNRESOLVED`, `NOT_ASKED`, `MISSING_EXPECTED_FACT`, `NOT_APPLICABLE` (the survey's own condition left the module out — that does not make the control unnecessary), not delivered, or of a kind the evaluator has no method for |
| `REQUIRES_REVIEW` (2) | otherwise, when a required observation is `HUMAN_ASSESSMENT_REQUIRED` |
| `SATISFIED` | combination `ALL_REQUIRED` and **every placement of every required entry** is `MATCH` or delivered |

The rows are tried in this order; the first that holds decides. Every reason is listed whatever the outcome.

`ALL_REQUIRED` is the only combination, and it is **declared in the governed mapping** by the three people who
publish it — it is not a default of the engine. A mapping with any other value gives `UNRESOLVED`. This is a new
semantic and is presented to the owner as such (decision D-287 in the register, proposed).

A `SATISFIED` control is not a compliance verdict: observations are still "matches", exactly as the existing engine
says.

### D-E. Applicable controls and coverage

The universe is every control of the register. For each, a result is produced — nothing is left out because no
question refers to it. A control without a published mapping is `UNRESOLVED` with reason `MAPPING_MISSING`.
Because no authoritative applicability policy exists (§9), every evaluation carries
`coverage: NOT_ASSERTED` with the reason; it never claims complete compliance coverage.

### D-F. Findings

`finding_engine.generate` with the market's **published** finding rule set, once per observation, with
`execution_ref` = the survey execution, the placement, the control and the mapping entry — so keys stay unique across
surveys, repeated placements and controls, and nothing is de-duplicated (§10.4). Findings are generated only for a
control that is `APPLICABLE`: not while applicability is unknown, and not when the evidence could not be trusted. `CONTROL`-scope rules see the controls of an item through the
governed mappings. Severity and review flags are the rule set's. No published rule set → findings are
`FINDING_RULES_MISSING`, not zero. Materiality and review routing are operational and are not applied.

### D-G. Processing status — kept apart from survey completion and from control outcomes

| Status | When |
|---|---|
| `FAILED_TECHNICALLY` | the evidence cannot be trusted: a survey's run no longer recomputes to its record, or the journey's composite is no longer intact. No control outcome is asserted |
| `REQUIRES_REVIEW` | some control requires review |
| `INCOMPLETE` | the journey has not completed every survey, or some control is `INSUFFICIENT_EVIDENCE` or `UNRESOLVED` |
| `COMPLETED` | every control has a deterministic outcome. It does not mean compliant |

### D-H. Records

Isolated `SIMULATION` records, insert-only: the evaluation run with its pins (mapping revisions, finding rule set
version and checksum, engines, execution contracts, evidence fingerprints) and its fingerprint; one row per control
instance; one per evidence observation; one per finding. A changed mapping or rule set gives a new evaluation with
different pins; a historical one is never rewritten. On reading, an evaluation is computed again from its pins and
the current evidence, and a difference is reported.

### D-I. Not built, and why

| Not built | Reason |
|---|---|
| `…_MATCH_POLICY_FACT` methods on journeys | no approved mapping from catalog facts to evaluation fact keys; such an entry evaluates to `MISSING_EXPECTED_FACT` |
| Multi-select evaluation | no method exists for it |
| Other combinations (any-of, thresholds, scoring) | not approved; no scoring of any kind |
| Materiality, review tasks, dispositions | operational |
| A control register editor or control versioning | the register is existing data; versioning it is a decision for its owner |
