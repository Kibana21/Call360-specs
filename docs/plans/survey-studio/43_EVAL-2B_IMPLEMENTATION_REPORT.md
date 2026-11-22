# EVAL-2B — Journey execution assurance: implementation report

**Status: BUILT AND TECHNICALLY VERIFIED 2026-11-22, awaiting the owner's review. Not accepted.**
**SIMULATION ONLY.** Nothing here verifies a real call, establishes that a call may be made, or shows that a person
heard any wording. No model judges anything. No control outcome, coverage result or finding is computed here.

Authorisation: the owner's message of 2026-11-22, "Accept EVAL-2A and Implement EVAL-2B Execution Assurance".
Companion documents: `42_…` (assessment, reuse matrix, design), contract `04_…` §19, decision register D-301…D-311.

---

## 1. EVAL-2A acceptance and D-300 reconciliation

EVAL-2A is recorded as accepted, TECHNICALLY VERIFIED, simulation only (D-301) with the ten points of the accepted
design. It is not Compliance approval of any policy, applicability definition, finding severity or live-call
behaviour.

**D-300, one by one** (exact recorded wording in the register, D-302):

| | Subdecision | Status |
|---|---|---|
| a | a policy set with obligations | **Accepted** — points 2 and 5 |
| b | two extra coverage values, `HUMAN_ASSESSMENT_PENDING` and `NOT_REQUIRED` | Vocabulary retained. **Its policy effect is not approved:** whether an answer awaiting a person's assessment keeps coverage from being complete — Compliance |
| c | `EVIDENCED` includes a control that is `NOT_SATISFIED` | **Accepted** — points 7 and 8 |
| d | a mapping entry names the policy requirement; EVAL-1 mappings must be re-proposed | **Accepted** — points 3 and 9 |
| e | `required` is the policy's | **Accepted as architecture** — point 2 |
| f | an evaluation names its policy explicitly | Mechanism retained. **Not approved as policy:** which policy applies to which application is a person's choice today — Business, Compliance |
| g | a superseded or withdrawn revision cannot be evaluated under again | Retained. **Not approved as policy:** whether a journey may be re-evaluated under an earlier policy — Business governance |
| h | an empty expected set is not a supported `SET_MATCH` configuration | **Accepted** — point 10 |
| i | trying out needs `survey.evaluate` | Technical choice, not separately ruled |
| j | setting `survey_control_policy_enabled` | Technical choice, not separately ruled |

**D-291 (d) and (e) remain open for Compliance** (D-303). EVAL-2B does not touch them: it computes no control
outcome, creates no finding, and never reads a survey's own exclusion as "the control does not apply". A test asserts
that the control evaluation's reading of an excluded module is the same before and after assurance.

## 2. Development migration `0034` (authorised; done)

| Safeguard | Result |
|---|---|
| Identity and revision | development schema `call360`, at `0033_survey_control_evaluation` before |
| Inventory | 132 tables, 15,327 rows, 125 triggers, 50 functions, 45 permissions |
| Backup | `_db_backups/call360_dev_before_0034_20261122.dump`, SHA-256 `d7365ca7af8a13c4335d74b724e0d6fd381215bd4fff2cf400728def958c22be`; rows in archive = rows in inventory |
| Recovery | restore dry run clean; `RESTORE.md` has "Rolling 0034 back" |
| Exactly the intended six tables | 132 → 138; added `survey_control_policy`, `survey_control_policy_event`, `survey_evaluation_policy`, `survey_obligation_result`, `survey_obligation_observation`, `survey_obligation_finding`; none removed |
| Existing EVAL-1 records, keys, columns, indexes, triggers | the six EVAL-1 tables were fingerprinted before and after — every row, and every column, constraint, index and trigger: **identical**. 131 of 132 pre-existing tables byte-identical (the other is `alembic_version`); no permission added |
| Existing evaluations | both read after the migration, recompute to their recorded fingerprints, carry no policy and no obligation key |
| Downgrade guard | refuses while a policy or a policy-scoped evaluation exists (both now exist in development) |
| Market authorisation and three-person governance | policy and mappings each proposed, approved and published by three different identities; self-approval and approver-publication refused; an identity without `survey.evaluate` cannot evaluate; no CSRF token → 403 |
| Operational and Script Studio data | counts identical before and after, including assignment rules, script versions, the control register and finding rule sets |
| Enabled in development only | `SURVEY_CONTROL_POLICY_ENABLED=true` in the gitignored `.env` |
| Reset or re-seed | none |

**Demonstrations on development (synthetic content only):**

| Asked | Shown |
|---|---|
| a governed synthetic control policy | `POL-DEV-SYNTHETIC` revision 1, declared complete, three people |
| two distinct obligations of one control | `SYN-CTRL-01`: `CLARITY` (an answer) and `OPENING` (a delivery) — two results |
| a mapping to published survey evidence | mapping revision 2 of `SYN-CTRL-01` and `SYN-CTRL-04`, re-proposed with the requirement each entry supplies (revision 1 superseded, not edited) |
| a single-survey evaluation | the development check survey, every answer "yes" |
| one NOT_SATISFIED obligation with complete coverage | `SYN-CTRL-04 / EXPECT-NO` is `NOT_SATISFIED` and `EVIDENCED`; coverage `COMPLETE_WITHIN_POLICY_SCOPE`, 3 of 3 |
| an incomplete-coverage scenario | the same survey unanswered: coverage `INCOMPLETE`, 1 of 3 |
| a coordinated multi-survey evaluation, and a cross-survey conflict | two surveys sharing one published question, answered "yes" and "no": `SYN-CTRL-01 / CLARITY` `REQUIRES_REVIEW`, `EVIDENCE_CONFLICTING`, evidence from two simulations |

To have two development surveys share a question, the walkthrough published a small synthetic survey
(`S-DEV-EVAL-SHARED`) that pins the published recap module of the development check survey, and re-bound the existing
synthetic rule `SG-ILP-HIGH-RISK v2` to it. **That supersedes the binding to `S-DEV-FI2-WALKTHROUGH`** — a survey-side
record; the assignment rule itself is untouched. `RESTORE.md` says how to bind it back.

The three policy-scoped evaluations wrote nothing into the EVAL-1 result tables. Evidence:
`docs/acceptance/evidence/EVAL-2B/dev-migration-0034/`.

**Development is at `0034`, not `0035`.** Execution assurance is off there; its operations do not exist and the
workbench says "Execution assurance is not switched on for this server".

---

## 3. Assessment and reuse (Step 1)

`42_…` Part 1. The authoritative engine already records a full ordered trace of every run. A simulation stores its
pinned version, its inputs and a fingerprint after every input; the trace is recomputed by the engine whenever the
simulation is read. Nothing verified that trace against what it pinned. That verifier is the one new capability.

| Reused unchanged | For |
|---|---|
| the SS-03B simulation read and its drift detection | the recorded execution and replay integrity |
| `execution.validate_answer` | invalid answers and refusals |
| `wording.render` and the pinned wording documents | exact wording |
| the pinned module documents | branches |
| ASG-2A's recorded selection and ASG-2B's steps, states and reason codes | the coordinated journey |
| the EVAL-1 / EVAL-2A evaluation, read as recorded | control outcomes and coverage |
| the EVAL-1 journey loader, pinning pattern and two permissions | the record |

Not modified: the execution engine, the simulation and coordination services, the evaluation engines, the finding
engine, Script Studio.

## 4. What was built

**Backend:** `app/domain/survey/execution_assurance.py` (pure verifier), `assurance.py` (loading, pinning,
recording, drift), `app/api/survey_execution_assurance.py` (three operations), migration
`0035_survey_execution_assurance` (two insert-only tables; test schema only), setting
`survey_execution_assurance_enabled` (off by default; needs evaluation), `tests/test_survey_execution_assurance.py`.

**Frontend:** `persist/ExecutionAssurance.tsx` — a section of the existing Evaluation Workbench, and a line on each
control; `persist/evalApi.ts`; `e2e/persisted/zz-eval2b.persisted.ts`.

### The grain (Step 2)

The assurance run is of the journey. Each survey execution has its own result and evidence references. A check
exists only where a distinct question is asked: eight per survey, five per coordinated journey (`42_…` D-B, D-C).

### Status (Step 7)

`INTEGRITY_FAILED` → `DEVIATION_DETECTED` → `NOT_ASSESSABLE` → `INCOMPLETE` → `VERIFIED`, the first that holds.

| | Says |
|---|---|
| `VERIFIED` | the supported checks passed for this recording |
| `INCOMPLETE` | a survey is waiting for an answer, has an unresolved non-answer, or was not started |
| `DEVIATION_DETECTED` | the recording differs from what it pinned |
| `INTEGRITY_FAILED` | replay or a fingerprint failed, or the composite is not intact |
| `NOT_ASSESSABLE` | recorded under an execution contract this assurance contract does not cover |

Technical statuses. A survey that ended without "completed" and passed every check is `VERIFIED`: its ending is
recorded as it happened. Operational call eligibility is `NOT_ESTABLISHED` on every result.

## 5. Verification (Step 10)

`tests/test_survey_execution_assurance.py`, on the isolated test schema. G = every golden run; T = tampered copies
of a real run (pure); S = `…single_survey_journey…` and C = `…coordinated_journey…` (real HTTP and PostgreSQL);
B = the browser journey `e2e/persisted/zz-eval2b.persisted.ts`.

| # | Demonstration | Where | Result |
|---|---|---|---|
| 1 | Complete single-survey execution passes the checks | G, S, B | all eight checks passed; `VERIFIED` |
| 2 | Complete coordinated execution passes | C, B | each survey `VERIFIED`; the five journey checks passed |
| 3 | Correct conditional branching is not a violation | **G: all 82 golden runs, with their refused answers, raise no finding**; S | 79 `VERIFIED`, 3 `INCOMPLETE` (still waiting), 0 deviations; every undelivered placement classified with the event that explains it |
| 4 | Missing required evidence is distinguishable from incorrect execution | S, B | a control with `INSUFFICIENT_EVIDENCE` beside `EXECUTION_VERIFIED`, its item "left out by the survey's own condition"; an omission is a different class and a deviation (T) |
| 5 | An unexpected delivery is detected | T (injected) | `UNEXPECTED_DELIVERY`, with placement and event |
| 6 | Modified recorded wording is detected | T (tampered) | `WORDING_ALTERED`, with the pinned and the recorded text |
| 7 | A missing recorded delivery is detected | T (tampered) | `MISSING_RECORDED_DELIVERY`; a removed event gives `MISSING_EVENT` |
| 8 | Duplicate execution events are detected | T (tampered) | `DUPLICATE_EVENT`, `DUPLICATE_DELIVERY` |
| 9 | Incorrect cross-survey order is detected | T (tampered coordinator records) | `ORDER_DIFFERS` |
| 10 | An unresolved survey does not silently advance | C (real: survey 2 not started, nothing bypassed); T (tampered: `SURVEY_BYPASSED`) | |
| 11 | Invalid customer responses remain rejected | G, S, C, B | refusals recorded with their codes; a refused input never appears as an answer; tampered: `INVALID_ANSWER_ACCEPTED`, `REJECTION_NOT_RECORDED` |
| 12 | A non-completed survey outcome is preserved | G, S, B | `ENDED_WITH_OUTCOME` kept as the ending; `VERIFIED`; "not a fault in the execution" |
| 13 | Replay drift prevents a trustworthy result | T; S (engine altered inside the test) | `INTEGRITY_FAILED`; the earlier result reads `ASSURANCE_DRIFT`; no control result shown as trustworthy |
| 14 | Control satisfaction is not recalculated | S, C, B | outcomes equal the evaluation's, one for one; the evaluation's fingerprint is unchanged afterwards |
| 15 | Cross-survey conflicting answers remain traceable | C, B | `REQUIRES_REVIEW` copied; two evidence lines, two simulations, both `EXECUTION_VERIFIED` and exact wording |
| 16 | A fidelity result never establishes eligibility | T, S, C, B | `NOT_ESTABLISHED` on every result; stated on the screen |
| 17 | Cross-market and unauthorised reads and writes denied | S, B | 403 without each permission, 404 from another market, 403 without CSRF |
| 18 | Historical assurance records reproducible | S | same inputs → same record (200); recomputes; new evidence → a new record, the old one unchanged and marked as drifted |
| 19 | No operational records | S, C | operational table counts identical; `record_class` `SIMULATION`; insert-only |
| 20 | 82 golden runs and 14 plans unchanged | existing tests; G | pass; no fixture modified |
| 21 | Backend, frontend, persisted, prototype, standard suites | §8 | pass |
| 22 | A browser journey with assurance findings and drill-down | B | passes; five screenshots |

**How the negative cases were made (D-310).** The authoritative executor cannot produce a deviation. Cases 5–9 and
part of 10, 11 and 13 are therefore **tampered or injected**: a real run is copied inside the test and altered in one
way, or the coordinator's records are altered, or (13, persisted) the engine's output is altered inside the test.
Each is named so in the test and in the evidence. None is a defect of the executor, and none is shown in the browser:
the "findings" the browser journey shows are what really occurs — a refused answer, a non-completed ending, items
left out by the survey's logic, an unfinished journey.

**Limits.** Decisions and entry conditions are shown as recorded, not re-evaluated. Where follow-up questions are
queued from a multiple-choice answer, their order is not checked edge by edge (stated as a note on the check).
The trace is not stored by the simulation service; assurance verifies the trace the authoritative engine recomputes,
and the stored fingerprints after every input.

## 6. Execution-assurance evidence examples

`docs/acceptance/evidence/EVAL-2B/example_assurance_summary.txt` (readable) and
`example_single_survey_assurance.json` (the full result).

**A real recording** (through the API; one refused answer, then "yes"): `VERIFIED`; all eight checks passed; three
deliveries, each with its event number, wording version, wording fingerprint and exact text; four placements not
delivered, each `VALID_CONDITIONAL_EXCLUSION` with the entry event that explains it; the refusal `CHOICE_REQUIRED` at
its event; three branches. Beside the control evaluation: `SYN-CTRL-01` `SATISFIED` on `EXECUTION_VERIFIED` evidence;
`SYN-CTRL-04` `INSUFFICIENT_EVIDENCE` on `EXECUTION_VERIFIED` evidence — its item was validly left out, so the gap is
one of coverage, not of execution.

**Tampered copies of a real run** (labelled as such):

| Tampering | Result | Finding |
|---|---|---|
| a question's recorded wording extended | `DEVIATION_DETECTED` | `WORDING_ALTERED` with both texts |
| a delivery of something the version does not contain | `DEVIATION_DETECTED` | `UNEXPECTED_DELIVERY`, `MISSING_RECORDED_DELIVERY`, `TRANSITION_UNEXPLAINED` |
| a delivery removed from the record | `DEVIATION_DETECTED` | `MISSING_RECORDED_DELIVERY` |
| an event recorded twice | `DEVIATION_DETECTED` | `DUPLICATE_EVENT`, `DUPLICATE_DELIVERY` |
| replay drift | `INTEGRITY_FAILED` | `REPLAY_DRIFT` |

## 7. Workbench (Step 8)

The Evaluation Workbench gains one section, "Execution assurance", and one line per control. Nothing else moved.

* **Four statements side by side:** evaluation, coverage of required controls, execution assurance, operational call
  eligibility (always "not established").
* **Summary** in a sentence, with what "verified" does not mean.
* **The journey as a whole** (coordinated): the five checks.
* **Each survey's execution**, closed by default: one line with exact-wording deliveries, answers, refusals and how it
  ended. Opened: the eight checks; "expected and recorded, item by item" with the recorded text, the pinned wording
  and version, and for everything not delivered the reason in words; branches and refused answers; technical details
  with fingerprints, the execution contract and a link to the survey's own simulation trace.
* **What differs** — listed only when something does.
* **On each control:** whether the execution behind its result was verified, why something was not delivered, and a
  plain warning when the result rests on evidence that could not be trusted.

Screenshots (real browser, isolated test database): `docs/acceptance/evidence/EVAL-2B/screens/`.

| File | Shows |
|---|---|
| `EVAL2B01-assurance-beside-evaluation-coverage-and-eligibility.png` | the four statements side by side; journey and survey results |
| `EVAL2B02-expected-versus-recorded-exact-wording-and-branches.png` | eight checks, item-by-item expected and recorded wording, branches |
| `EVAL2B03-conflict-unchanged-beside-verified-executions.png` | the conflict as the control evaluation found it, on verified execution evidence |
| `EVAL2B04-refused-answer-and-non-completed-ending-preserved.png` | a refused answer and an ending without "completed", neither a fault |
| `EVAL2B05-unfinished-journey-assurance-incomplete.png` | an unfinished journey: incomplete, not failed |

No deviation appears in a screenshot: the authoritative executor cannot produce one, and a tampered recording is not
put into a browser journey as if it were real. Technical verification only; not a UX or screen-reader sign-off.

## 8. Security, integrity and regression results

| Check | Result |
|---|---|
| Full backend suite (`call360_test` only) | **1,006 collected; no failure or error reported** (917 before) |
| 82 golden execution runs, 14 golden call plans | pass; fixture files unmodified. The 82 runs are additionally verified one by one by the new verifier |
| Frontend unit suite | 612 passed |
| Persisted browser suite | **25 passed** (24 + the EVAL-2B journey) |
| Prototype / standard browser suites | 13 / 33 passed |
| `ruff check`, `ruff format --check`, `mypy app` | clean (123 source files) |
| `tsc`, `eslint`, production build | clean |
| OpenAPI | 269 operations, 509 schemas; additive against the contract before this series and against the last committed one. SHA-256 `e1b44eb77e22831ccd35034ff44f2fb5c003ed73c9b07e6365b6e62fb9a762d5` |
| Specs validator | passes |
| Migration `0035` | additive (no other table's columns or constraints change — compared before and after); down and up on an empty schema; downgrade refused while a result exists |

The backend run prints no totals line (the project runs pytest quietly); it was run with failure reporting on and
printed no failed or errored test; the count is from collection.

**Security.** No new permission: reading needs `survey.evaluation.read`, verifying `survey.evaluate` as well; each is
tested separately; another market gets 404 and empty lists; the write needs a CSRF token and is rate-limited and
audited (`SURVEY.EXECUTION_ASSURED`); the audit chain verifies. **Integrity.** Records are insert-only (`UPDATE` and
`DELETE` refused by the database); each pins what it was computed from and is recomputed on every read. No security
defect is known; that is not a claim that none exists.

Tests changed that existed before: the eight structural tests that pin the migration head, the set of survey tables
and the contract size, to state `0035`, two new tables and the new counts. No expectation of behaviour and no golden
fixture was changed.

Evidence: `docs/acceptance/evidence/EVAL-2B/`.

## 9. State

| | State |
|---|---|
| **Development database** | **`0034_survey_control_policy`** (owner-authorised). No `0035` object |
| **Test schema** | `0035_survey_execution_assurance` (head) |
| On in development | survey definitions, library, simulation, assignment, requirement groups, coordinated simulation, evaluation, **control policies** |
| Off in development | **execution assurance** (needs `0035`, not authorised): operations answer 404; the workbench says it is not switched on |
| On in the browser test suite | all of the above, and execution assurance |
| Development content | synthetic policy `POL-DEV-SYNTHETIC`; mapping revisions 2; survey `S-DEV-EVAL-SHARED`; rule `SG-ILP-HIGH-RISK v2` now bound to it; five evaluations (two EVAL-1, three under the policy) |
| `Call360-backend` | `main` at `ed3e51b` (the owner's commit); EVAL-2B is uncommitted on top (20 files) |
| `Call360-frontend` | `main` at `e79c4e0` (the owner's commit); EVAL-2B uncommitted (9 files) |
| `Call360-specs` | `main` at `c43f4f5` (the owner's commit); later documents and evidence uncommitted |
| Commits by the assistant | none |

## 10. Outstanding policy questions, exactly

| | Question | Who |
|---|---|---|
| D-291 d | are findings wanted while a control's applicability is unknown? | Compliance |
| D-291 e | can a survey's own exclusion ever make a control not applicable? | Compliance |
| D-291 b | is control governance held by other people than survey governance? | Business governance |
| D-302 b | does an answer awaiting a person's assessment keep coverage from being complete? | Compliance |
| D-302 f | which control policy applies to which application — who or what chooses it? | Business, Compliance |
| D-302 g | may a journey be re-evaluated under a policy revision that is no longer published? | Business governance |
| D-311 | the eight EVAL-2B choices, among them: a survey that ended without "completed" is `VERIFIED`; a deviation produces no finding or severity | Owner |
| new | what should happen when assurance finds a deviation or an integrity failure — who is told, what is blocked? Today it is reported and nothing else | Business, Compliance |
| new | is "verified against the recording" enough for a channel where the trace is produced outside the authoritative engine, or must delivery be evidenced separately? | Compliance, Engineering |
| G-E1…G-E10, OR-1…OR-3, input mapping | as recorded | — |
| — | every control, obligation, condition, mapping, rule and severity is synthetic | Compliance |

## 11. Proposed E2E-1 acceptance boundary (a proposal; nothing is authorised)

**Purpose.** One reviewable, end-to-end synthetic journey through everything accepted so far, as a single acceptance
exercise — not new capability.

**Inside the boundary:**

1. Author, review and publish a survey in Survey Studio (three people), reusing a library component.
2. Bind it to a published assignment rule and place it in a requirement group; compose a plan for a synthetic
   application.
3. Run the coordinated simulation to its end.
4. Govern a control policy and its mappings (three people each).
5. Evaluate the journey under the policy; read outcomes, coverage and findings.
6. Verify the execution; read assurance beside the evaluation.
7. Show, for that one journey, every identity and fingerprint from application to assurance result, and that each
   record recomputes.
8. On development, with every migration through `0035` applied under the established safeguards (which needs the
   owner's authorisation of `0035` first).

**Acceptance would require:** the journey completed by distinct synthetic identities with no step done through a
back door; each of the five statements (completion, satisfaction, coverage, fidelity, eligibility) shown separately
and correctly; operational tables unchanged; all suites and the 82 runs and 14 plans passing; a written trace of the
journey's identities.

**Outside the boundary:** live or recorded customer calls; Genesys, voice or transcripts; operational findings,
dispositions or eligibility; real applications; any Compliance approval; Script Studio migration; resolving any open
policy question above.

## 12. Does EVAL-2B meet its acceptance criteria?

**Technically, yes — with the limits stated in §5. Acceptance is the owner's.**

| Criterion | Met? |
|---|---|
| No second execution engine | yes — the recorded trace is verified; only the simulation service's own replay runs |
| No duplicated evaluation or finding rules | yes — outcomes and coverage are copied as recorded; no finding is created |
| Journey as the assurance context, per-survey results and evidence references | yes |
| Sequence fidelity: expected and delivered items, branches and their evidence, transitions, missing or duplicated events, invalid answers, unexpected termination, replay | yes; decisions shown as recorded, not re-evaluated |
| Valid exclusion told apart from omission; coverage kept separate | yes |
| Wording fidelity with version, fingerprint and evidence reference; no claim about what was heard | yes |
| Coordinated journey verified from ASG-2B's own evidence and reason codes | yes |
| Attached to the existing evaluation view; untrusted evidence never presented as trustworthy | yes |
| A deterministic, documented status model; `VERIFIED` never implies eligibility | yes |
| Simulation-only, immutable, reproducible, pinned | yes — migration `0035`, test schema only |
| The 22 demonstrations | yes; negative cases on tampered recordings, named as such |
| D-291 (d), (e) left open | yes |

Not met because not decidable or not done here: development is not migrated to `0035` (not authorised), so assurance
cannot be used in development; a deviation leads to no finding or action (no governed rule exists); the open
questions of §10.

## 13. Stopped here

E2E-1 was not started. I committed and pushed nothing.
