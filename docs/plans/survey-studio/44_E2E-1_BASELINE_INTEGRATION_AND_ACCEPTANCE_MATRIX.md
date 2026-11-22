# E2E-1 — Baseline, module integration and the acceptance matrix

**The baseline was established by inspection before anything was built (owner's step 1); this document was written
up while the harness and the journey view were being built, not before.** The results are in
`45_E2E-1_IMPLEMENTATION_REPORT.md`.
**Simulation only. Synthetic data only.** E2E-1 is an integration and verification exercise: no new business meaning,
no second engine, no parallel workflow.

---

## 1. Modules, contracts, migrations and settings (SS-03B … EVAL-2B)

| Module | What it owns | Contract | Migration | Setting (all off by default) | Permissions |
|---|---|---|---|---|---|
| Survey definitions (SS-03A, FI-1, FI-2) | drafts, candidates, three-person review, immutable published versions | survey documents `call360.survey/1` | `0027` | `survey_definitions_enabled` | `survey.read/edit/approve/publish` |
| Component library (LIB-1) | published modules, questions, conditions, answer sets, pinned exactly | — | `0028` | `survey_library_enabled` | as above |
| Simulation and call plan (SS-03B) | the authoritative execution engine; a simulation = pinned version + inputs + a fingerprint after every input; call plans | `call360.survey.execution/1` | `0029` | `survey_simulation_enabled` | `survey.simulate` |
| Single-survey assignment (ASG-1) | bindings of published assignment rules to published survey versions | `call360.assignment-engine/1 + survey-binding` | `0030` | `survey_assignment_enabled` | `survey.assignment.read` (+ governance) |
| Requirement groups and composite plans (ASG-2A) | governed groups; one application → several surveys; composite plan with fingerprint | `call360.survey.composite-plan/1` | `0031` | `survey_assignment_groups_enabled` | as above |
| Coordinated simulation (ASG-2B) | a thin coordinator over individual simulations | `call360.survey.coordinated-simulation/1` | `0032` | `survey_coordinated_simulation_enabled` | `survey.simulate` |
| Journey evaluation (EVAL-1) | control mappings; control outcomes; findings by the existing findings engine | `call360.survey.control-evaluation/1` | `0033` | `survey_evaluation_enabled` | `survey.evaluation.read`, `survey.evaluate` |
| Control policies and coverage (EVAL-2A) | governed policies, obligations, applicability, coverage, `SET_MATCH` | `…control-evaluation/2 (policy-scoped)` | `0034` | `survey_control_policy_enabled` | as above |
| Execution assurance (EVAL-2B) | verification of a recorded execution against what it pinned | `call360.survey.execution-assurance/1` | `0035` | `survey_execution_assurance_enabled` | as above |

Not modified by E2E-1, and read only: the answer-evaluation engine (`call360.answer-evaluation/1`), the findings
engine (`call360.finding-engine/1`), the control register, Script Studio and its assignment-rule tables.

**Heads at the start of E2E-1:** code `MIGRATION_HEAD` `0035_survey_execution_assurance`; test schema `0035`;
development `0034` (then `0035` under the owner's authorisation — report §2). **E2E-1 adds no migration.**

## 2. The handoffs between modules — what one module gives the next, and how it is pinned

| # | From → to | Operation | What is handed over | How the receiver pins it |
|---|---|---|---|---|
| H1 | Author → reviewer → publisher | `POST …/survey-definitions/{id}/candidates`, `…/survey-candidates/{id}/decision`, `…/publish` | a frozen candidate | published version: id, label, content and manifest fingerprints |
| H2 | Library → another survey | draft save with a module pinned by code and version | a published module revision | the consumer's manifest pins the exact revision |
| H3 | Assignment rule (Script Studio) → survey binding | `POST …/survey-assignment/bindings` (+ decision, publish) | rule code and version; survey version id | binding row: rule version id, survey version id, content and manifest fingerprints |
| H4 | Bindings → requirement group | `POST …/survey-assignment/groups` (+ decision, publish) | member rules, kind, sequence | group id and version |
| H5 | Application → composite plan | `POST …/survey-assignment/composite-plans` | assignment inputs and call-plan facts | composite: application fingerprint, selection, order, each member's rule version, binding, survey version and call-plan fingerprint; one fingerprint over all |
| H6 | Composite plan → coordinated simulation | `POST …/composite-plans/{id}/coordinated-simulations` | the governed order | composite plan id and fingerprint; refused unless selection resolved, order governed, plan ready |
| H7 | Coordinator → individual simulation | (internal) one simulation per survey; `POST …/coordinated-simulations/{id}/inputs` | the survey version, the facts | step: position, simulation id, why it started; each simulation its own run fingerprint |
| H8 | Journey → evaluation | `POST …/survey-evaluation/evaluations` | journey id; control policy id (named explicitly) | pins: journey replay fingerprint, each execution, policy revision, mapping revisions, control register rows, finding rule set |
| H9 | Evaluation → findings | (internal) the existing findings engine | evaluated observations | findings inside the evaluation record, each with its rule and source observation |
| H10 | Journey (+ evaluation) → assurance | `POST …/survey-evaluation/assurance` | journey id; evaluation id | pins: composite, each execution, contracts, the evaluation and its result fingerprint |
| H11 | Everything → reviewer | `GET …/survey-evaluation/journey-trace` (**new in E2E-1, read-only**) | — | nothing is pinned or stored: it reads H1…H10's records |

Every handoff is by **id and fingerprint**, never by "the current version of". That is what scenario F tests.

## 3. Existing browser journeys that E2E-1 reuses

| Journey (persisted suite) | Covers, in a real browser |
|---|---|
| `fi1` (6), `fi2` (3) | authoring a survey and its modules; submit, approve, publish by three people; refusals of self-review |
| `lib1` (5) | publishing a module, finding and pinning it in another survey, reuse of questions and conditions |
| `ss03b` (5) | step-by-step simulation, refused answers, non-answer as "policy unresolved", call plan |
| `zz-asg1`, `zz-asg2a` (3) | bindings, requirement groups, composite plans, coordinated simulation — through the screens |
| `zz-eval1`, `zz-eval2a` | mappings and a control policy built and governed in the browser; evaluation; cross-survey conflict |
| `zz-eval2b` | execution assurance in the workbench |

E2E-1 adds **one** browser journey that walks one application across these screens and the new journey page; it does
not repeat the module journeys' detailed assertions.

## 4. Acceptance matrix

H = backend harness `tests/test_zz_e2e1_journey.py` (real HTTP, real PostgreSQL, test schema);
B = browser journey `e2e/persisted/zzz-e2e1.persisted.ts`.

### 4.1 The fifteen steps

| # | Step | Module | Handoff | Evidence |
|---|---|---|---|---|
| 1 | Author a reusable survey module and question | definitions, library | H1 | H; B (through the governed API from the author's session); UI authoring: `fi1`, `lib1` |
| 2 | Compose a published survey | definitions, library | H2 | H; B |
| 3 | Distinct identities propose, approve, publish | definitions | H1 | H (self-approval and approver-publication refused); B |
| 4 | Bind the published version to a published assignment rule | ASG-1 | H3 | H; B |
| 5 | Place rules into governed requirement groups | ASG-2A | H4 | H; B |
| 6 | Evaluate one synthetic application to select several surveys | ASG-2A | H5 | H; B |
| 7 | Generate the composite call plan | ASG-2A | H5 | H; B |
| 8 | Verify the exact selected versions, reasons and governed order | ASG-2A | H5 | H; B |
| 9 | Run the coordinated simulation | ASG-2B | H6, H7 | H; B |
| 10 | Record accepted responses, refusals and exact execution evidence | SS-03B | H7 | H; B |
| 11 | Create or select a governed control policy and separately published mappings | EVAL-2A | — | H (created, three people); B (selected) |
| 12 | Evaluate the journey at control-obligation level | EVAL-1/2A | H8 | H; B |
| 13 | Verify coverage and existing governed findings | EVAL-2A, findings engine | H9 | H; B |
| 14 | Run execution assurance | EVAL-2B | H10 | H; B |
| 15 | Display the complete results in the Evaluation Workbench | frontend | H11 | B |

### 4.2 The scenarios

| | Scenario | Expected, in the five dimensions (completion · satisfaction · coverage · assurance · eligibility) |
|---|---|---|
| A | Complete happy path | all completed · every required obligation satisfied · complete within the policy's scope · verified · not established |
| B | Completed journey, one control not satisfied | all completed · one NOT_SATISFIED, finding with its source evidence · complete · verified · not established |
| B′ | A correctly excluded question leaves an evidence gap | all completed · INSUFFICIENT_EVIDENCE · incomplete · verified, the item "left out by the survey's own condition" · not established |
| C | Incomplete: a survey pending | running · evidence missing · incomplete · incomplete · not established; the next survey not started |
| C′ | Incomplete: stopped, policy unresolved | stopped · not satisfied · incomplete · incomplete · not established; no downstream survey started |
| D | Cross-survey conflicting answers | all completed · REQUIRES_REVIEW with both observations · incomplete · verified · not established |
| E | Missing or unknown applicability | (i) a missing rule input leaves the requirement UNRESOLVED and no journey starts; (ii) a missing survey fact blocks the plan; (iii) a missing policy input gives applicability UNKNOWN, never NOT_APPLICABLE |
| F | Historical integrity | after a newer mapping, policy and survey version: earlier evaluation and assurance keep their pins and results and recompute; the composite says it would differ; a new evaluation is a new record; injected engine drift is reported, not hidden |
| G | Security and isolation | three identities at each governance step; reader, missing permission, other market, no CSRF, across the workflow |

No scenario may write an operational callback case, finding or disposition.

## 5. Where stand-ins and unverified mappings are still used

| | What | Status |
|---|---|---|
| S-1 | Assignment inputs have **no replacement or rider attribute**. Tests and walkthroughs use other inputs (premium frequency, selling channel) as stand-ins to make several requirement groups select | **Stand-in.** Not a business rule. No replacement or rider attribute was invented |
| S-2 | Assignment inputs (`product_family`, `selling_channel` …) and catalog facts (`policy.is_replacement`, `customer.age_years` …) are entered separately. Nothing maps one to the other | **Unverified** — every composite says `input_consistency: UNVERIFIED` |
| S-3 | The facts a control policy's conditions read are the facts given to the simulation | **Unverified** — every applicability says `input_lineage: UNVERIFIED` |
| S-4 | The control policy is named by the person who runs the evaluation | **No selection rule exists**, and none was invented |
| S-5 | A later survey starts only after the one before it is COMPLETED | **A rule of the simulation only** (`cross_survey_policy: UNRESOLVED`) |
| S-6 | A non-answer stops a survey as "policy unresolved" | **Fails closed**; no consent, refusal or silence policy was invented |
| S-7 | Every control, obligation, condition, mapping, finding rule and severity | **Synthetic** (`SYNTHETIC_UNAPPROVED` in the register) |

## 6. Technically verified versus awaiting Business / Compliance

| Technically verified (simulation only) | Awaiting Business or Compliance |
|---|---|
| Governance by three people at every stage | Who holds each permission in production |
| Deterministic selection, order and composite plan | The real assignment attributes and requirement groups (S-1) |
| Deterministic execution, replay and drift detection | Live cross-survey continuation, consent reuse, refusal and silence (S-5, S-6) |
| Control outcomes, applicability and coverage under a named policy | Every real control, obligation, applicability condition and mapping (S-7); how a policy is selected (S-4); D-291 d, e; D-302 b, f, g |
| Findings by the existing engine under a published rule set | Real finding rules and severities |
| Execution assurance of a recording | What a deviation leads to; whether a recording is enough for a real channel |
| The provenance chain and its fingerprints | The lineage of inputs to a real application (S-2, S-3) |
| — | Operational call eligibility: **not established by anything here** |
