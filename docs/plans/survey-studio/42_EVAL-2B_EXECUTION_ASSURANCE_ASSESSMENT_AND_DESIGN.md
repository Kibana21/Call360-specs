# EVAL-2B — Execution assurance: assessment, reuse matrix and design

**The assessment in Part 1 was made by inspection before any table or service was introduced; this note was written
up alongside the implementation, not before it.** The implementation report is `43_…`.
**Simulation only.** Nothing here verifies a real call, and a simulation does not show that a person heard anything.

---

## Part 1 — Assessment: what already exists

| Capability | What it already gives | Where |
|---|---|---|
| SS-03B execution contract and trace | For every run the authoritative engine records an ordered trace: `ENTRY` (module entered or not, with its mode, condition, values read and result), `SAY`, `ASK`, `ANSWER`, `REJECT` (with the refusal code), `ROUTE` (node, edge, via, to), `DECISION` (condition, result, explanation), `QUEUE`, `MODULE_END`, `SURVEY_ROUTE`, `DISPOSITION`, `END`. Plus the list of deliveries with exact text and wording version, module statuses, the ending, the pending question | `execution.py`, contract `call360.survey.execution/1` |
| What a simulation STORES | The pinned version (content and manifest fingerprints), the facts, the execution contract, the fingerprint of the run before any input, and each input with whether it was accepted, its refusal code and **the fingerprint of the run after it**. The trace itself is not stored: it is recomputed from these by the authoritative engine every time the simulation is read | `simulation.py`, migration `0029` |
| Replay and drift | A simulation that no longer recomputes to its recorded fingerprint reads as `REPLAY_DRIFT`; a version whose documents no longer match its manifest is refused | `simulation.drift_of`, `_version` |
| Answer validation | `validate_answer(item, options, answer)` gives the exact refusal code or accepts | `execution.py` |
| Wording rendering | `render(text, fields, facts)` gives the exact delivered text for a pinned wording | `wording.py` |
| ASG-2A composite plan | The governed selection, its order, each survey's plan, a fingerprint, and whether it is still intact | `assignment_groups.py` |
| ASG-2B coordinated simulation | The steps the coordinator recorded (position, group, version, simulation, why it started), each survey's state, the decisions between surveys, the stop reason; start refused for an unresolved selection, order, plan or a duplicated requirement | `coordination.py` |
| EVAL-1 / EVAL-2A | The journey loader (`journey_of`), control outcomes, findings, applicability, coverage; pinning, recompute and drift | `journey_evaluation.py`, `policy_evaluation.py` |
| Existing execution-quality capability in Call360 | None for surveys. Script Studio's simulation workbench evaluates answers and findings of script runs; nothing verifies that a recorded execution followed its pinned plan | — |

### Reuse matrix

| Need of EVAL-2B | Reused, unchanged | New |
|---|---|---|
| The recorded execution and its trace | the SS-03B simulation read (replay by the authoritative engine) | — |
| Replay integrity | `simulation.drift_of` result; the stored per-input fingerprints | checking **every** stored per-input fingerprint, not only the last |
| Exact wording | `wording.render` and the pinned wording documents | the comparison |
| Invalid answers and refusals | `execution.validate_answer` | the comparison of trace, recorded inputs and validator |
| Branches | the pinned module documents (nodes, edges) | verifying each recorded route against them |
| Coordinated journey | ASG-2B's steps, states and reason codes; ASG-2A's recorded selection and intact flag | five journey checks over those records |
| Control outcomes, coverage, findings | EVAL-1 / EVAL-2A evaluation, **read as recorded** | nothing: no outcome is computed |
| Journey, pinning, recompute, drift, permissions | the EVAL-1 pattern and its two permissions | one result record |

### Gap assessment

1. **Nothing verifies a recorded trace against what it pinned.** That is the one new capability.
2. **A stored trace does not exist to be tampered with.** Because the trace is recomputed by the authoritative
   engine, a natural recording cannot deviate from its pinned version: a deviation can come only from a changed
   engine (caught as drift) or from a recording made by something else. The verifier is therefore written over a
   *given* trace, so that the same checks will apply unchanged to a trace that was produced elsewhere — which is what
   a later channel would supply — and its negative cases are tested on tampered copies, named as such.
3. **Per-input fingerprints were recorded and never checked individually.** Now they are.
4. **Decisions are not re-evaluated.** A recorded decision's condition result is shown as recorded. Re-evaluating
   would need the binding of condition inputs to answers, which is the engine's own logic; duplicating it would be a
   second executor.

---

## Part 2 — Design

### D-A. Grain

The assurance run is of the **journey** (the same synthetic journey EVAL-1 evaluates). Each **survey execution** has
its own verification result with its own evidence references. An **assurance check** exists only where a distinct
question is asked (eight per survey, five per coordinated journey).

Five things are never merged: survey completion, control satisfaction, evidence coverage, execution fidelity,
operational call eligibility.

### D-B. Checks of one survey execution

| Check | The question | Detects |
|---|---|---|
| `INTEGRITY` | does the recording still recompute to its recorded fingerprints? | replay drift; a per-input fingerprint that differs |
| `TRACE_WELL_FORMED` | is the trace whole? | a missing event, a duplicated event, events out of order, anything after the end |
| `DELIVERIES_EXPECTED` | was everything delivered a part of the pinned version, once? | an unexpected delivery, a delivery of another item or revision, a duplicate delivery, a delivery missing from the record of deliveries or present without an event |
| `WORDING_EXACT` | was every delivery the exact pinned wording? | altered wording, another delivery mode; keeps the wording version and a fingerprint of the pinned wording |
| `ANSWERS_AND_REJECTIONS` | was every accepted answer valid, every invalid one refused and recorded? | an invalid answer accepted, an answer without its question, two answers, a refusal missing or with another code, inputs and trace that disagree |
| `BRANCHING` | does every branch follow an edge of the pinned module, on evidence? | a route on an edge the module lacks or that differs from it, a branch with no answer or delivery to decide it, a branch the recorded answer does not support, a delivery the recorded route did not lead to, a route that led to an item never delivered (omission) |
| `MODULE_SEQUENCE` | were modules entered in the pinned order, with nothing owed left out? | a module out of order, entered twice or not in the version; a module status with no event to support it; a module with no ending |
| `TERMINATION` | did the survey end as its routes say? | an ending that disagrees with the run, "completed" with a module never reached, an outcome no recorded route leads to |

**Valid exclusion or omission.** Every placement of the pinned version that was not delivered is classified, with the
event that explains it:

| Class | Meaning | A deviation? |
|---|---|---|
| `VALID_CONDITIONAL_EXCLUSION` | the module's published entry condition is false | no |
| `EXCLUDED_INFORMATION_MISSING` | the entry condition could not be decided; the published policy skipped or halted | no |
| `VALID_ROUTING_EXCLUSION` | a published route passed over the module, or it is entered only after an outcome that did not occur | no |
| `NOT_ON_PATH_TAKEN` | the recorded answers took another published branch | no |
| `SURVEY_ENDED_BEFORE` | the survey ended first | no |
| `NOT_YET_REACHED` | the simulation has not got there | no |
| `OMISSION` | a recorded route led here and it was never delivered | **yes** |

Whether a control then lacks evidence is a coverage matter (EVAL-2A) and stays there.

### D-C. Checks of a coordinated journey (from ASG-2B's own records)

`SELECTION_RECORDED` (composite intact; the journey's surveys are the recorded selection), `GOVERNED_ORDER` (starts
recorded one after another in the governed order), `NO_BYPASS` (a survey after the first was started only because
the one before it is `COMPLETED`), `OWN_EVIDENCE` (each survey its own simulation), `NO_DEDUPLICATION` (every selected
requirement present; a duplicated requirement is explicitly unresolved).

### D-D. Status

| Status | When | Is |
|---|---|---|
| `INTEGRITY_FAILED` | `INTEGRITY` failed for a survey, or the composite is not intact | first: nothing else is trusted |
| `DEVIATION_DETECTED` | any other check failed | a verified discrepancy |
| `NOT_ASSESSABLE` | a survey was recorded under an execution contract this assurance contract does not cover | |
| `INCOMPLETE` | a survey is waiting for an answer, has an unresolved non-answer, or was not started | not a failure |
| `VERIFIED` | every survey ended and every check passed | the supported checks passed for this recording |

A survey that ended **without** "completed" and whose every check passed is `VERIFIED`: its ending is recorded as it
happened. These are technical statuses. None is a compliance outcome, and `VERIFIED` never establishes operational
call eligibility.

### D-E. Beside the control evaluation

An assurance run may name a control evaluation of the same journey. Its control results are then **copied as
recorded** — outcome and coverage — and each is shown with what was verified about the execution evidence under it:
`EXECUTION_VERIFIED`, `EXECUTION_INCOMPLETE`, `DEVIATION_IN_EVIDENCE`, `INTEGRITY_FAILED`, `NOT_ASSESSABLE`,
`NO_EXECUTION_EVIDENCE`, and `result_is_trustworthy`. When the evidence is no longer what the evaluation was made
from, none of its results is presented as trustworthy. Nothing is evaluated again, and no finding is created:
D-291 (d) and (e) are not touched.

### D-F. Records

Migration `0035_survey_execution_assurance`, purely additive: `survey_execution_assurance` (the run, its pins,
status, fingerprints) and `survey_execution_assurance_survey` (each survey's result in full). Insert-only,
`record_class` `SIMULATION`. Pins: the composite plan and its selected surveys; each survey version with content and
manifest fingerprints; each simulation, its run fingerprint and execution contract and number of inputs; the
assurance contract and the execution contract; the control evaluation and its result fingerprint. The same journey
and the same pins are the same run; anything changed gives a new one. On reading, it is computed again and a
difference is reported as `ASSURANCE_DRIFT`.

### D-G. Not built, and why

| Not built | Reason |
|---|---|
| Re-evaluation of decisions and entry conditions | it would duplicate the executor (gap 4) |
| Any check of speech, audio or a transcript | outside this checkpoint; a simulation proves nothing about what was heard |
| A finding, severity or disposition for a deviation | no governed rule exists for one; a deviation is reported, not classified |
| Storing the trace | the simulation service does not; assurance does not change that |
