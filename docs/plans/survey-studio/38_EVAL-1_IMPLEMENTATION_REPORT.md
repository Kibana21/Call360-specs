# EVAL-1 — Journey-level control evaluation: implementation report

**Status: BUILT AND TECHNICALLY VERIFIED 2026-11-22, awaiting the owner's review. Not accepted. Uncommitted.**
**SIMULATION ONLY.** Nothing here evaluates a real call, writes an operational finding, routes a review or gives a
case a disposition. No model judges anything.

Authorisation: the owner's message of 2026-11-22, "Accept ASG-2B and Authorize EVAL-1 Journey-Level Evaluation".
Companion documents: `37_EVAL-1_EXISTING_ENGINE_ASSESSMENT_AND_DESIGN.md` (written before implementation: the
assessment, the reuse matrix and the design decisions); contract `04_…` §17; decision register D-271…D-288, G-E1…G-E7.

---

## 1. ASG-2B technical acceptance record

The owner's words: *"ASG-2B is TECHNICALLY ACCEPTED for simulation-only coordinated multi-survey execution. All
previously accepted golden fixture expectations must remain unchanged."* Recorded as D-271. The D-270 choices are
confirmed (D-272). Every outstanding business policy stays open (D-268 and the table of unresolved policy
boundaries). This is not a business, UX, screen-reader, production or live-call acceptance.

Golden fixtures: unchanged. No fixture file was edited; the 82 expected runs and 14 expected plans pass as before.

## 2. Development migration `0032_survey_coordinated_sim` (Part B)

| Safeguard | Result |
|---|---|
| Database identity and revision | development schema `call360`, at `0031_survey_assignment_groups` before |
| Inventory before | 124 tables, 15,066 rows, 116 triggers, 49 functions, 43 permissions |
| Fresh backup | `_db_backups/call360_dev_before_0032_20261122.dump`, SHA-256 `b4b87cd9549478772ca71549c86a526ecc8818956189833354d66e8347d18b7e` |
| Backup verified | 124 tables with data in the archive; rows in archive = rows in inventory (15,066); no mismatch |
| Recovery | `pg_restore` to SQL dry run clean (124 `CREATE TABLE`, 124 `COPY`, 0 bytes of errors); `_db_backups/RESTORE.md` has a "Rolling 0032 back" section |
| Only the intended revision | `uv run alembic upgrade 0032_survey_coordinated_sim` — `0031` → `0032` |
| Additive | 124 → 126 tables; none removed; 123 of 124 pre-existing tables byte-identical in content (the other is `alembic_version`); column definitions identical; two immutability triggers added; no function, no permission |
| Isolation | the two tables refer to composite plans, groups, survey versions and simulations; nothing refers to them |
| Readiness, permissions, market | ready 200; a checker without `survey.simulate` cannot start (403) and can read (200); composing for another market → 404 |
| Existing data | Script Studio and operational tables identical before and after the walkthrough (258 cases, 251 script assignments, 26 findings, 8 rule versions …); 4 surveys, 2 bindings, 2 groups unchanged |
| Enabled in development only | `SURVEY_COORDINATED_SIMULATION_ENABLED=true` in the gitignored `.env` |
| Not reset, not re-seeded | confirmed |

**Demonstration on development** (synthetic; the additional requirement is the synthetic stand-in group of the 0031
walkthrough):

* **Two-survey journey.** `DEV-PRIMARY → DEV-CHECK-AD5AEA8F`, then `DEV-ADD-SYNTHETIC → S-DEV-FI2-WALKTHROUGH`. An
  empty answer was refused (`CHOICE_REQUIRED`) and survey 2 stayed not started; survey 1 completed, survey 2 started
  (`PREVIOUS_COMPLETED`); ended `ALL_SURVEYS_COMPLETED`. Each survey's own simulation: `SIMULATION`, `COMPLETED`,
  fingerprint equal to the coordinated record's, replay consistent.
* **Replay.** The same inputs in a new coordinated simulation: identical coordinated fingerprint, different record.
* **Blocked scenario.** With the ILP indicator not known, the additional requirement is `INPUT_MISSING`; the three
  states read call plan `UNRESOLVED`, coordinated simulation `BLOCKED [SELECTION_UNRESOLVED]`, operational call
  eligibility `NOT_ESTABLISHED`; starting it → `409 SELECTION_UNRESOLVED`; no record created. The screen offers no
  start control.
* **No operational records.** Confirmed by counts before and after.

**A correction, kept in the evidence.** My first "blocked" scenario left out the SBQ risk band. The existing rule
engine reads a missing risk band as the governed value `UNASSESSED` (D-59), not as a missing input, so that composite
resolved to the primary survey alone and its one-survey coordinated simulation legitimately started. I replaced it
with the scenario above. One consequence: development now holds **four** coordinated simulations — the journey, its
replay, that one-survey run, and the replay made on the screen for the screenshot — all `SIMULATION` records.

**The start control when the feature is unavailable (D-274).** A composite now carries
`states.coordinated_simulation.available`. The page offers "Start a coordinated simulation" only when the composite
is `PERMITTED` and the server says it is available; otherwise it says coordinated simulation is not switched on for
this server. Tested in `test_survey_assignment_groups.py` and `test_survey_coordination.py`.

Evidence: `docs/acceptance/evidence/EVAL-1/dev-migration-0032/`.

**Development is NOT at `0033`.** EVAL-1 is off there: its operations do not exist, and both simulators show
"Control evaluation is not switched on for this server" instead of a control.

---

## 3. Existing evaluation engines: what was found, and what is reused

Full assessment: `37_…` Part 1. In short:

* The existing grain is **(execution, script question)**. `answer_evaluation` gives one result per question;
  `finding_engine` turns triggering results into findings by a governed, versioned rule set.
* A **control** is a row of a register (code, name, owner role, approval status) that questions are linked to. **No
  control-level result exists anywhere in Call360**, and controls have no revisions and no applicability rules.
* Evaluation rules live inside script question revisions; the persisted records are keyed by script runs or
  callback cases. The two engines themselves are pure and take plain values.

| Existing component | Reused | How |
|---|---|---|
| `answer_evaluation.evaluate_one` | **unchanged** | judges every answer observation |
| `answer_evaluation.configure`, `describe_rule`, result vocabulary, `ENGINE` | **unchanged** | validates and words the rule of a mapping entry |
| `finding_engine.generate`, `RuleSet`, classes, categories, severities | **unchanged** | produces every finding |
| `finding_rules` lifecycle and the Finding Rules screen | **unchanged** | finding rules are still made and published there |
| Survey Studio conditions (three-valued) | **unchanged** | applicability of a control |
| SS-03B simulation and ASG-2B coordination services | **unchanged** | the evidence, replayed on every read |
| `answer_evaluation.evaluate` (walks a script plan) | not usable | needs a script controller |
| `simulation_evaluation` / `simulation_findings` persistence | not usable | keyed by Script Studio runs |
| `persist_operational`, `review.py`, materiality policy | **deliberately not used** | operational |

No file of the existing engines, of Script Studio, or of the finding rules was modified.

## 4. Evaluation grain and data model

Application → **callback journey** (the evaluation run) → **survey execution** (one SS-03B simulation) → **control
instance** (the atomic result) → **evidence observation**. Survey is a filter and a place to look for evidence.

Migration `0033_survey_control_evaluation` — additive, six insert-only tables:

| Table | Holds |
|---|---|
| `survey_control_mapping` | one immutable mapping revision of one control in one market |
| `survey_control_mapping_event` | its lifecycle; a trigger enforces three different people |
| `survey_journey_evaluation` | one evaluation of one journey: `record_class = SIMULATION`, the pins, input and result fingerprints, processing status |
| `survey_control_result` | one control instance: outcome, applicability, reasons, pinned mapping |
| `survey_evidence_observation` | one observation: simulation, survey version, placement, item revision, result, full detail |
| `survey_evaluation_finding` | one finding of the existing engine: rule set version, rule, category, severity, full detail |

The only references out of the survey tables are to `control` and `finding_rule_set_version`. Nothing operational
refers to any of them. Two permissions, granted to no role: `survey.evaluation.read`, `survey.evaluate`.
Setting `survey_evaluation_enabled`, off by default; needs simulation.

## 5. Governed mapping specification

Contract §17.2. A mapping is its own artifact — not part of a question — and:

* names **exact** items (code and version) that a published survey version of the market pins, with the item's
  fingerprint;
* says for each whether its evidence is an **answer** (with a rule of the existing rule language) or a **delivery**,
  whether it is **required**, and optionally the survey it counts in (so a reusable question can serve different
  controls in different surveys);
* pins the control by a fingerprint of its register row;
* declares how the evidence **combines** (`ALL_REQUIRED`, the only value) and optionally a published **condition**
  for when the control applies;
* records its **source**;
* is proposed, approved and published by **three different people**, refused by the service and by a database
  trigger otherwise; a published revision cannot be edited, only superseded or withdrawn.

Fifteen kinds of invalid proposal are refused with stable codes (tested). Nothing is inferred from a label.
**Mapping authoring has an API and no screen** (D-288 f).

## 6. What was built

**Backend**

| File | Purpose |
|---|---|
| `migrations/versions/0033_survey_control_evaluation.py` | the six tables, the guard, two permissions |
| `app/domain/survey/control_evaluation.py` | pure: placements, evidence adapter, applicability, control outcome, findings call, result and fingerprint |
| `app/domain/survey/control_mapping.py` | mapping governance |
| `app/domain/survey/journey_evaluation.py` | loads the journey through the simulation services, pins, records, recomputes, reports drift |
| `app/api/survey_evaluations.py` | ten operations under `/api/v1/survey-evaluation` |
| `app/api/survey_assignment_groups.py` | `states.coordinated_simulation.available` (D-274) |
| `app/core/settings.py`, `app/main.py`, `app/domain/catalog.py`, `scripts/export_openapi.py` | setting, head `0033`, acceptable heads, table catalog, contract export |
| `scripts/e2e_survey_setup.py`, `scripts/e2e_eval_setup.py` | test-schema identities and setup for the browser journey |
| `tests/test_survey_evaluation.py` | six tests (below) |

Existing tests changed, each only to state a fact about the new head or the new tables: `test_survey_store.py`,
`test_survey_lib1.py`, `test_survey_api.py`, `test_admin_access.py`, `test_survey_assignment.py`,
`test_survey_assignment_groups.py`, `test_survey_coordination.py`, `test_survey_simulation.py`. No expectation about
behaviour was changed and no golden fixture was touched.

**Frontend**

| File | Purpose |
|---|---|
| `persist/evalApi.ts` | generated-client calls |
| `persist/EvaluationWorkbench.tsx` | the workbench page and the "Control evaluation" entry shown on both simulators |
| `persist/PersistedStudioRoot.tsx` | route `/survey-studio/evaluations/:evaluationId` |
| `persist/CoordinatedSimulation.tsx`, `persist/ServerSimulation.tsx` | the entry |
| `persist/AssignmentGroups.tsx` | start control unavailable when the feature is off (D-274) |
| `styles/survey-studio.css` | appended `.ss-ev-*` |
| `e2e/persisted/zz-eval1.persisted.ts`, `playwright.persisted.config.ts` | the browser journey |

Script Studio files were not touched.

## 7. How an evaluation is decided

Contract §17.3–§17.5. The points that matter most:

* **The existing vocabulary is kept.** Every answer observation carries the existing evaluator's own record —
  `MATCH`, `MISMATCH`, `UNRESOLVED`, `NOT_ASKED`, `MISSING_EXPECTED_FACT`, `NOT_APPLICABLE`,
  `HUMAN_ASSESSMENT_REQUIRED` — with its rule text, expected value and explanation.
* **Mapping to the owner's conceptual outcomes:**

  | Conceptual outcome | Produced as | From |
  |---|---|---|
  | SATISFIED | `SATISFIED` | every placement of every required entry is `MATCH` or delivered |
  | NOT_SATISFIED | `NOT_SATISFIED` | a required `MISMATCH`, no conflict |
  | INSUFFICIENT_EVIDENCE | `INSUFFICIENT_EVIDENCE` | required evidence `UNRESOLVED`, `NOT_ASKED`, `MISSING_EXPECTED_FACT`, excluded by the survey, not delivered or not evaluable |
  | NOT_APPLICABLE | `NOT_APPLICABLE` | the governed applicability condition is false |
  | UNRESOLVED / REQUIRES_REVIEW | `UNRESOLVED` | no mapping, unknown applicability, changed control, unsupported combination, untrusted evidence |
  | | `REQUIRES_REVIEW` | conflicting answers to the same item; an answer for human assessment |

* **Nothing is manufactured.** A refused input is "asked, no accepted answer" with the refusal codes listed and no
  reason claimed. A module skipped because information was missing is `NOT_ASKED`, never `NOT_APPLICABLE`.
* **Nothing is reconciled.** The same item answered differently in two places keeps both observations and both
  findings; the control requires review.
* **The control outcome is the one new semantic** (D-287, proposed for the owner's ruling).

## 8. The 21 demonstrations

Backend tests run on the isolated test schema (`call360_test`) through real HTTP and PostgreSQL. S = `…single_survey…`,
C = `…coordinated_journey…`, G = `…mapping_is_governed…`, P = `…engine_never_reconciles…` (pure engine), in `tests/test_survey_evaluation.py`.

| # | Demonstration | Where | Result |
|---|---|---|---|
| 1 | Single-survey simulation evaluated against a governed control | S | K8: `SYN-CTRL-01` `SATISFIED` from an answer (`MATCH`) and a delivery; journey kind `SINGLE_SURVEY` |
| 2 | Two-survey coordinated simulation, one journey-level evaluation | C; browser (three surveys) | one evaluation, `COORDINATED`, pins the coordinated replay fingerprint |
| 3 | Independent evidence per survey | C | each observation names its own survey version, simulation and run fingerprint |
| 4 | One control using evidence from two surveys | C; browser | `SYN-CTRL-01`: K1 yes/no answer and K3 number → `SATISFIED` |
| 5 | Control not duplicated | C | five control instances, one per control |
| 6 | Control unsatisfied although both surveys complete | C; browser | both `COMPLETED`; `SYN-CTRL-01` `NOT_SATISFIED` |
| 7 | Required unanswered question: no automatic pass | S | waiting → `NOT_ASKED`; refused input → `UNRESOLVED`; control `INSUFFICIENT_EVIDENCE` |
| 8 | Unreached required question is an evidence gap | S | `NOT_ASKED` (`NOT_REACHED`) → `INSUFFICIENT_EVIDENCE` |
| 9 | Unmapped required control reported | S; browser | `SYN-CTRL-05` `UNRESOLVED` `MAPPING_MISSING`; listed under coverage |
| 10 | Unknown applicability is not NOT_APPLICABLE | S | age missing → applicability `UNKNOWN` → `UNRESOLVED`; module skipped for missing information → `NOT_ASKED` |
| 11 | Contradictory evidence not silently reconciled | **P (engine level)** | same item answered yes and no → `REQUIRES_REVIEW`, both observations and the finding kept |
| 12 | Existing finding rules reused | S, C | findings by `finding_engine.generate` from a rule set published through its existing lifecycle |
| 13 | Every finding traceable to rule revision and evidence | S, C; browser | rule code, rule set version and checksum, simulation, placement, item revision, answer or missing evidence |
| 14 | Identical inputs → identical results | S, P; browser | same evaluation returned (200), same fingerprints, no new record |
| 15 | Re-evaluating with changed rules creates a distinct result | S | new rule set → new evaluation; old one unchanged, still recomputes from its pins, and says `FINDING_RULES_REVISED`; likewise a revised mapping |
| 16 | No operational finding or case disposition | S, C | operational table counts identical; `record_class` `SIMULATION`; tables insert-only |
| 17 | Cross-market and unauthorised access refused | C; browser | 403 without each permission; 404 and empty lists from another market; 403 without CSRF |
| 18 | No new LLM evaluator | P | the three modules import only the deterministic domain; engines recorded on every evaluation |
| 19 | 82 golden runs and 14 plans unchanged | existing tests | pass; no fixture file modified |
| 20 | Persisted, prototype and standard suites pass | Playwright | 23, 13, 33 |
| 21 | Real-browser journey of control evaluation and drill-down | `e2e/persisted/zz-eval1.persisted.ts` | passes; six screenshots |

**Stated limits of these demonstrations.** #11 is shown at engine level only: a governed journey with the same item
in two surveys needs a reused library question, which the test fixtures do not have, and the coordinator refuses the
same survey version twice. In the browser journey the third control's evidence was left out by the survey's own
condition (`NOT_APPLICABLE` → `INSUFFICIENT_EVIDENCE`), so the "missing evidence" finding is shown in the backend
tests, not on a screenshot. Also tested: mapping governance and its fifteen refusals, the database trigger, a
withdrawn mapping, a journey whose evidence cannot be trusted (`FAILED_TECHNICALLY`), a non-answer with unresolved
policy (`INSUFFICIENT_EVIDENCE`, never `NOT_SATISFIED`), evaluation drift after new evidence, the feature switched
off, and migration `0033` down and up.

## 9. Example evaluations and evidence-linked findings

Recorded on the test schema; full JSON and a readable summary are in `docs/acceptance/evidence/EVAL-1/`
(`example_single_survey_evaluation.json`, `example_coordinated_journey_evaluation.json`,
`example_evaluations_summary.txt`).

**Coordinated journey, two surveys, both completed — processing `INCOMPLETE`, coverage `NOT_ASSERTED`:**

| Control | Outcome | Evidence |
|---|---|---|
| `SYN-CTRL-01` (mapping revision 2) | `NOT_SATISFIED` | survey 1 `mi-call/n2` `MATCH` "Answered yes; expected yes"; survey 2 `mi-numbers/n1` `MISMATCH` "Answered 1 count; expected at least 18 count from the approved value" |
| `SYN-CTRL-02`, `-03` | `UNRESOLVED` | applicability unknown: the application carries no fact their conditions read; their items are in no survey of the journey |
| `SYN-CTRL-04` | `INSUFFICIENT_EVIDENCE` | its item is in no survey of this journey |
| `SYN-CTRL-05` | `UNRESOLVED` | no published mapping |

Finding: rule `FR-EVAL-MISMATCH` in "SG finding rules v1" — customer discrepancy / fact mismatch / severity from the
rule set — control `SYN-CTRL-01`, survey 2's own simulation, placement `mi-numbers/n1`, answer 1; "not a breach
determination". A second finding (`FR-EVAL-NOT-ASKED`, missing evidence) for `SYN-CTRL-04`, with no answer.

**Single-survey journey (identity not confirmed; survey ended with an outcome):** `SYN-CTRL-01` `NOT_SATISFIED`
(answer `MISMATCH`, statement `DELIVERED`); `-02`, `-03` `NOT_APPLICABLE` (conditions false); `-04`
`INSUFFICIENT_EVIDENCE` (question not reached); `-05` `UNRESOLVED`.

All rules, severities and mappings above are test fixtures.

## 10. Evaluation Workbench

`/survey-studio/evaluations/:evaluationId`, opened from "Control evaluation" on a simulation or a coordinated
simulation. It uses the existing Survey Studio layout and components.

* **Summary:** journey kind and surveys completed; the processing status with what it does and does not mean;
  applicable controls; controls by outcome; findings; "complete coverage is not asserted".
* **The journey:** each survey with its own ending, version, manifest and run fingerprints, and a link to its own
  simulation. "A survey's ending is its own. It does not decide any control."
* **Filters:** control outcome; the survey the evidence comes from; with or without findings.
* **Controls:** one row per control; opening it shows the meaning of the outcome, the reasons with their codes,
  applicability, the governed mapping revision, and the evidence table — survey and placement, item revision, exact
  wording delivered, answer, governed rule, result, the gap in plain words, and a link to the trace events.
* **Findings:** each with its explanation, rule and rule set, where the severity comes from, the evidence and the
  captured answer or "no answer — the evidence is missing"; results no rule covers; a clear statement when no rule
  set is published.
* **Mapping and coverage gaps:** controls with no mapping, with unknown applicability, and items no mapping names.
* **Integrity:** record class, evidence trusted, recomputes to this record, fingerprints, engines, pinned mapping
  revisions and rule set, what is published now but was not used, and every evaluation of the journey.

Screenshots (real browser, isolated test database): `docs/acceptance/evidence/EVAL-1/screens/`.

| File | Shows |
|---|---|
| `EVAL01-unfinished-journey-nothing-is-assumed.png` | a journey evaluated before any answer: nothing satisfied |
| `EVAL02-journey-evaluation-summary.png` | three surveys completed; evaluation incomplete; counts; coverage not asserted |
| `EVAL03-one-control-evidence-from-two-surveys.png` | one control, two observations from surveys 1 and 3, with wording, answer, rule, result |
| `EVAL04-not-satisfied-with-evidence-linked-finding.png` | a mismatch and its finding with rule, rule set and severity source |
| `EVAL05-gaps-and-findings.png` | evidence gap, unmapped control, findings, coverage gaps, integrity |
| `EVAL06-single-survey-journey-same-model.png` | the same model for one survey; the other survey's evidence does not exist |

This is a technical verification. It is not a business UX sign-off and not a screen-reader sign-off.

## 11. Regression and security evidence

| Check | Result |
|---|---|
| Backend tests (`call360_test` only) | **831 collected, 0 failed** (825 before + 6) |
| Golden parity | 82 runs and 14 plans pass; no fixture modified |
| `ruff check`, `ruff format --check`, `mypy app` | clean (117 source files) |
| OpenAPI | 256 operations (246 + 10), 490 schemas (477 + 13); SHA-256 `97a911a983cf045c1bb68e9541822e0889f1de47e9babbe791976bf5ed9b5ce5`; additive |
| Frontend `tsc`, `eslint`, build | clean |
| Vitest | 612 passed |
| Playwright persisted | **23 passed** (22 + the EVAL-1 journey) |
| Playwright prototype | 13 passed |
| Playwright standard | 33 passed |
| Specs validator | passes |

Evidence files: `docs/acceptance/evidence/EVAL-1/backend_checks.txt`, `frontend_checks.txt`,
`playwright_prototype.txt`, `playwright_standard.txt`. The full backend run printed no summary line (the project runs
pytest quietly); the count is from collection and the result from the exit code and the absence of any failure line.

**Security.** Two permissions of their own, granted to no role; reading and evaluating are separate, and evaluating
needs both; every other survey permission opens nothing; other markets get 404 and empty lists; mapping proposals
for a market out of scope are refused; state changes need a CSRF token and are rate-limited and audited; denials are
audited; the audit chain verifies. The evaluation shows control names and finding-rule text and severity, which is
why reading it is a permission of its own rather than `survey.read`. No security defect is known; that is not a
claim that none exists.

## 12. Outstanding policy and data-model gaps

| | Gap | Effect today |
|---|---|---|
| D-287 / G-E1 | What "control satisfied" means, and how evidence combines | one declared combination, proposed for ruling |
| G-E2 | The control register has no revisions or lifecycle | a mapping pins a fingerprint; a changed control is reported |
| G-E3 | No governed applicability policy | coverage is never asserted |
| G-E4 | No mapping from catalog facts to evaluation policy facts | fact-based rules give `MISSING_EXPECTED_FACT` |
| G-E5 | No method for a multiple-choice answer | not evaluable |
| G-E6 | No finding trigger for an undelivered statement, an unmapped control or a conflict | reported, no finding |
| G-E7 | Non-answer reasons | never claimed |
| OR-1 | Retention | none set |
| OR-2, OR-3, input mapping | as before | unchanged |
| — | Every control, mapping, rule and severity used in the tests is synthetic | proves the mechanism, not a business mapping |
| — | The control register and finding rules are `SYNTHETIC_UNAPPROVED` | nothing here is approved compliance content |

## 13. State of the repositories and databases

| | State |
|---|---|
| `Call360-backend` | `main` at `182f6e5`, 43 changed or new files, nothing ahead of the remote |
| `Call360-frontend` | `main` at `9f497d5`, 27 changed or new files, nothing ahead |
| `Call360-specs` | `main` at `755bf00`, uncommitted documents and evidence, nothing ahead |
| Uncommitted checkpoints | SS-03B and its closure, ASG-1 and its closure, ASG-2A, ASG-2B, EVAL-1 — **no commit authorisation exists** |
| Development database | **`0032_survey_coordinated_sim`**; no `0033` table or permission; evaluation operations answer 404; server ready |
| Test schema | `0033_survey_control_evaluation` (head) |
| Development identities | unchanged; they do not hold the evaluation permissions (those exist only at `0033`) |

## 14. Stopped here

Nothing is authorised next. Nothing was committed or pushed. Development was not migrated beyond `0032`.

Questions for the owner:

1. **D-287** — is `ALL_REQUIRED`, declared per mapping, an acceptable first meaning of a control outcome, or should
   control evaluation wait for an approved definition?
2. **D-288** — the seven choices listed there.
3. Whether to authorise development migration `0033` (not requested; not done).
4. Commit authorisation for the accumulated checkpoints (SS-03B … EVAL-1), which are all still uncommitted.
