# ASG-2B — Coordinated multi-survey simulation: implementation report

With the ASG-2A acceptance record and the development migration `0031`.

**Checkpoint:** ASG-2B, authorised by the owner on 2026-11-22 ("Accept ASG-2A and Authorize ASG-2B Coordinated
Simulation"), decision register D-259…D-269.
**Status: BUILT AND TECHNICALLY VERIFIED — presented for the owner's review. Not accepted.**
**Prepared:** 2026-11-22.

**SIMULATION ONLY.** Nothing here is, starts, schedules or authorises a customer call, or assigns a survey to a case.

**Exclusions held.** No Genesys, GPT Live or telephony. No actual customer call. No real case assignment. Script
Studio not modified. No second execution engine. No operational findings. No golden expectation changed. No
destructive database migration.

**Business-policy boundaries held.** Not decided here: live cross-survey continuation; consent reuse; whether
repeated questions may be omitted; whether one survey's escalation ends a whole callback; refusal and non-answer
policies; operational outcomes; real callback eligibility. No replacement or rider assignment attribute was invented.
OR-2, OR-3 and the application input mapping stay open.

**Not committed, not pushed.** The three repositories are still at the commits the owner pushed (backend `182f6e5`,
frontend `9f497d5`, specs `755bf00`). SS-03B, its closure, ASG-1, ASG-2A and ASG-2B are all uncommitted
working-tree changes: no commit authorisation has been given for any of them.

**Not claimed.** Not production readiness; not business-user UX acceptance; not screen-reader sign-off; not
Compliance approval of anything; and the stand-in "replacement" and "CI rider" conditions are **not** proof of real
business assignment requirements.

---

## 1. ASG-2A acceptance record

Recorded as D-259: ASG-2A is accepted as **TECHNICALLY VERIFIED — MULTI-SURVEY ASSIGNMENT AND COMPOSITE CALL-PLAN
ASSEMBLY**, for simulation-only mechanics — requirement groups; the existing rule engine once per requirement;
three-person governance of groups; immutable version selection and bindings; one SS-03B plan per selected survey;
deterministic composite fingerprints; explicit unresolved ordering, input consistency and cross-survey policy; the
ASG-1 assignment-read correction and development migration `0030`.

Confirmed (D-260): **D-258.1** a primary requirement with no matching rule is unresolved; **D-258.2** a multi-survey
composite needs an explicit governed order before it is `READY`; **D-258.3** two groups selecting the same published
survey version both remain — neither automatic de-duplication nor double execution is authorised.

Retained open: OR-2, OR-3, the unverified mapping between assignment inputs and call-plan facts, and every
no-answer, refusal, consent and live-call policy.

### 1.1 Unambiguous terminology (D-261)

A composite used to show one status, and "READY" could be read as more than it meant. It now answers three separate
questions, in the API (`states`) and on the screen, each with its own line:

| Question | Values | What it does **not** say |
|---|---|---|
| **Call plan** | `COMPUTABLE` · `NOT_COMPUTABLE` · `UNRESOLVED` | nothing about simulation, nothing about a call |
| **Coordinated simulation** | `PERMITTED` · `BLOCKED` with stable blocker codes | nothing about a call |
| **Operational call eligibility** | always `NOT_ESTABLISHED` | — |

The stored `plan_status` value `READY` is unchanged and is presented as "call plan: computable". A computable plan
with a blocked coordinated simulation is a real, tested case (two requirements selecting the same survey version).
The coordinated-simulation screen repeats that operational call eligibility has not been established.

## 2. Development database — migration `0031_survey_assignment_groups`

Evidence: `docs/acceptance/evidence/ASG-2B/dev-migration-0031/`.

| To verify | Result |
|---|---|
| 1. Identity and revision | schema `call360` of `Call360_db` on localhost, revision `0030_survey_assignment` before |
| 2. Protected-data inventory | 119 tables, 14,988 rows (`dev31_before.json`) |
| 3. Fresh verified backup and restore instructions | `_db_backups/call360_dev_before_0031_20261122.dump`, 1,887,529 bytes, SHA-256 `53e2de71…eefa29ac6`, taken with the API server stopped; every table's row count equals the inventory; full SQL dry run of the restore without error (119 tables, 119 data sets, 110 triggers). `_db_backups/RESTORE.md` extended |
| 4. Additive only | five tables, their triggers and one function added; nothing removed; no permission added (`dev31_diff.txt`) |
| 5. Automated migration-up, empty-down and guarded-downgrade tests | `test_zz_migration_0031_goes_down_and_up_empty_and_refuses_while_a_governed_group_exists` and the corresponding `0030` test; both pass in the full suite |
| 6. Script Studio and Survey Studio data preserved | 118 of 119 pre-existing tables byte-identical in content; the 119th is `alembic_version`. Column definitions identical. 4 surveys, 2 survey versions, 5 simulations, 258 callback cases, 11 script versions, 8 assignment-rule versions, 4 rule drafts, 251 script assignments, 24 Voice Lab sessions — unchanged. No foreign key points into the new tables from elsewhere |
| 7. Development authorisation and market isolation | on the dev server: a survey identity gets `403` from the Assignment Rules API; a read-only identity gets `403` composing; an application for another market gets `404`; the proposer cannot approve their own group |
| Only the intended migration | `uv run alembic upgrade 0031_survey_assignment_groups`. Revision after: `0031`. **`0032` was not applied** |

**What happens when a governed binding or group is withdrawn and a downgrade is attempted — tested, not assumed.**
The tables are insert-only. Withdrawing adds a `WITHDRAWN` event; the binding or group row stays. The migrations
refuse while any such row exists, whatever its state. So **withdrawal does not enable a downgrade**: after
withdrawing, `0030` still refuses with "governed survey assignment bindings exist" and `0031` with "governed survey
assignment groups exist", and nothing is lost. Both are now asserted by automated tests. The ways back are switching
the setting off, or a full restore (`RESTORE.md`).

**Demonstration on the development server** (`dev31_walk.txt`, screens `DEVG01`, `DEVG02`), with **explicitly
labelled synthetic conditions**: the existing demo rule "ILP with a high SBQ risk band" stands in for an additional
requirement; the group's own name and purpose say "SYNTHETIC STAND-IN … Not a business requirement".

1. A second binding (`SG-ILP-HIGH-RISK v2` → `S-DEV-FI2-WALKTHROUGH` v1.0) and two groups (`DEV-PRIMARY`, position 1;
   `DEV-ADD-SYNTHETIC`, position 2), each proposed, approved and published by the three development identities.
2. Synthetic application 1 (ILP, high risk band): two surveys, order governed, each with its own plan; call plan
   `COMPUTABLE`, coordinated simulation `PERMITTED`, operational call eligibility `NOT_ESTABLISHED`; cross-survey
   policy `UNRESOLVED`; input consistency `UNVERIFIED`.
3. Synthetic application 2 (ILP, low risk band): the primary survey only; the additional group `NOT_APPLICABLE`.
4. Application 1 again: the same composite fingerprint, in a new record.
5. Script Studio and operational table counts identical before and after.

Nothing was reset or re-seeded. One binding, two groups and three composites were **added**. Because groups now
exist, **`0031` can no longer be downgraded**.

ASG-2B is **off** in development (`0032` is not authorised there): the composite says a coordinated simulation is
permitted, and starting one answers "not switched on for this server".

## 3. Architecture — a thin coordinating layer

```
 composite plan (ASG-2A, recorded)          the coordinator                    SS-03B, unchanged
 ─────────────────────────────────          ───────────────                    ─────────────────
 selection RESOLVED?  ────────────┐
 order GOVERNED?      ────────────┤  refuse to start, with the code of
 every plan computable? ──────────┤  what is unresolved  (409)
 no survey version twice? ────────┤
 still the recorded composite? ───┘
                                        start survey 1 ───────────────► simulation.create(version 1, facts)
        governed order                                                   └ its own inputs, trace, status,
        [A, B, C]                       input ───────────────────────►  simulation.advance(current, key, answer)
                                                                         └ validity, refusal, drift: the survey's own
                                        A is COMPLETED?  yes ─────────► simulation.create(version 2, facts)
                                                         no  ─────────► stop
                                        state ───────────────────────►  simulation.state(each)  → replayed every time
```

| Reused, unchanged | From |
|---|---|
| the selected surveys, their pinned versions, fingerprints, governed order, blockers | the ASG-2A composite plan |
| execution, validation of answers, exact wording, rejection, `POLICY_UNRESOLVED`, terminal states | `execution.py` through `simulation.py` |
| creating a simulation, giving an input, reading the state, replay-drift detection | `simulation.create`, `simulation.advance`, `simulation.state` — the same functions the single-survey Simulator uses |
| answer shape validation, facts validation, manifest verification | `simulation.check_answer`, `check_facts`, `_version` |

`app/domain/survey/coordination.py` adds only: the refusal to start; starting a survey; routing an input to the
current survey; starting the next survey when the current one is `COMPLETED`; computing the coordinated state. It
contains no execution, no wording, no condition and no routing. A test reads that both surveys produce exactly the
golden run of their fixture.

For each selected survey the coordinator retains — by reference — the published version, the individual simulation
identity, the individual trace, the answers and rejected inputs, the simulation status and the run fingerprint. It
merges no graph.

## 4. The simulation-only continuation rules (D-263)

Authorised solely for technical simulation; each is implemented exactly and tested.

| Rule | Implemented as |
|---|---|
| Begin only when selection and ordering are resolved | `409 SELECTION_UNRESOLVED`, `409 ORDER_UNRESOLVED`; nothing is recorded |
| Run the first survey in the governed order | the first step, `started_because = FIRST_IN_ORDER` (a CHECK ties that value to position 1) |
| A survey that reaches `COMPLETED` lets the next one start | the next step, `started_because = PREVIOUS_COMPLETED`; decision `PROCEED`, rule `SIMULATION_ONLY_COMPLETED_PROCEEDS` |
| A survey that is `PENDING` keeps the coordinator there | status `RUNNING`; the next survey has no simulation at all |
| `POLICY_UNRESOLVED` stops, with the reason | status `POLICY_UNRESOLVED`, `stop` with the survey's own reason; the question stays current; a real acknowledgement afterwards is accepted |
| Any other terminal outcome stops with `CROSS_SURVEY_POLICY_UNRESOLVED` | status and `stop.code`; decision `STOP`; no further survey is started; further input is `409` |
| No completion, escalation or business outcome is synthesised for the composite | the coordinated record has no outcome or terminal field. `ALL_SURVEYS_COMPLETED` is a progress status and the screen says "progress, not an outcome" |
| Two groups selecting the same survey version stop with `DUPLICATE_SURVEY_REQUIREMENT_UNRESOLVED` | refused at the start (`409`), and shown as a blocker on the composite; the survey is run neither once nor twice |
| Unresolved or conflicting order: do not start | `409 ORDER_UNRESOLVED` |
| A blocked individual plan: explain, do not proceed | `409 PLAN_BLOCKED` naming the group and survey; call plan `NOT_COMPUTABLE` |

Also refused: a composite that would no longer be computed the same (`COMPOSITE_STALE`), and one with nothing
selected.

**These rules approve nothing about real customer calls.** The API note, the screen and the contract say so.

## 5. No automatic de-duplication

Each survey is run exactly as published. In the browser journey the Life survey and the replacement survey both
open with "Good day. This is a service call about your policy." and both ask "Can you confirm that you are the
policyholder?" — both are delivered and both are asked, and the consolidated report lists both. A test asserts
that every delivered sentence of each survey equals its golden fixture's, in order: nothing merged, shortened,
skipped or added.

## 6. The coordinated simulation record

Migration `0032_survey_coordinated_sim` (additive; test schema only). Contract `04_…` §16.

| Table (insert-only) | Holds |
|---|---|
| `survey_coordinated_simulation` | the composite plan it runs, the application and composite fingerprints it was started from, the contract (`call360.survey.coordinated-simulation/1`), the governed order, who and when. `record_class = 'SIMULATION'` by CHECK |
| `survey_coordinated_simulation_step` | each survey the coordinator **started**: position, group, survey version, the individual simulation (unique), and why it was started |

Everything else is **computed on reading** from the steps and the replay of each individual simulation — the same
principle as SS-03B, so the record cannot drift from its evidence:

| Required in the record | Where |
|---|---|
| application snapshot fingerprint · composite-plan fingerprint · governed order | stored on the row |
| selected published survey versions | the steps, and the composite the row refers to (verified intact on every read) |
| current survey and current question | `current` — from the current survey's own simulation |
| individual simulation identifiers and run fingerprints | `surveys[].simulation_id`, `surveys[].run_sha256` |
| completed, pending and blocked survey states | `surveys[].state`: `COMPLETED`, `CURRENT`, `NOT_STARTED`, `STOPPED`, `DRIFTED` |
| cross-survey continuation decisions and reasons | `decisions[]` (`PROCEED` / `STOP` with the rule) and `stop` |
| execution contract versions | `surveys[].engine_contract`, `execution_contracts`, `contract` |
| aggregate progress | `progress` |
| stable replay fingerprint | `replay_sha256` — over the composite fingerprint, the order, each survey's version, state and run fingerprint, the status and the decisions; no identifiers or times |

**Replay drift** is the individual simulations' own: if any survey's run no longer recomputes to its record, the
coordinated status is `REPLAY_DRIFT`, that survey is `DRIFTED`, and no further input is taken. **Immutable
references:** the coordinated row pins the composite fingerprint and reports `composite_intact`; each step pins the
simulation, which pins the version with its content and manifest fingerprints.

**Not confusable with operational records:** `record_class` CHECK; insert-only triggers; foreign keys only to the
composite plan, the group, the survey version and the individual simulation; no table refers to them; every response
says `SIMULATION` and "operational call eligibility: not established".

## 7. The Simulator's coordinated mode

Reached from the composite on the Survey assignment page ("Start a coordinated simulation of these surveys", offered
only when it is permitted). The existing single-survey Simulator is unchanged, and each survey's own simulation
opens in it from the coordinated page.

| Asked for | On the page |
|---|---|
| Application and composite-plan summary | the summary block: application and composite fingerprints (linked back to the composite), inputs, that the two parts of the application are not reconciled |
| All required surveys in their governed order | "Surveys, in the governed order": numbered, with kind, version, rule and state |
| Current survey | highlighted in the list; "Survey 2 of 3 · name" above the question |
| Current question and exact wording | "The customer would hear, exactly" — the server's sentence, with the same answer controls as the Simulator |
| Answers captured in each survey | the consolidated report, and each survey's own trace |
| Individual survey completion status | per survey: completed, current, not started, ended without "completed", with its ending |
| Overall progress | "Survey 2 of 3 · 1 completed" and a progress bar |
| Why continuation was permitted or stopped | "Why it went on, or stopped": each boundary in a sentence, marked "simulation rule only"; and the stop reason with its code |
| Individual traces and fingerprints | "Each survey's own trace": version, content fingerprint, run fingerprint, execution contract, the full trace, a link to its own simulation |
| A consolidated simulation report | every item delivered and every answer, survey by survey, refused answers included; repeated statements appear as often as they were delivered |
| Replay | "Replay the same inputs": a new coordinated simulation fed the same inputs; the two coordinated fingerprints are compared |

## 8. Security

| Requirement | How |
|---|---|
| Simulation and assignment permissions | starting and giving an input need `survey.simulate` **and** `survey.assignment.read`; reading needs `survey.assignment.read`. Tested with each one missing |
| Market isolation | every operation is scoped to the caller's markets; another market gets `404` on start, input and read |
| Published-version integrity | each survey's simulation verifies its version's manifest before running, as in SS-03B; the composite must still be the recorded one |
| CSRF and rate limiting | on both state-changing operations |
| Read/write authorisation | a person with every survey permission except `survey.simulate` can read and cannot start or answer |
| SIMULATION-only persistence | §6 |
| Immutable evidence and audit | insert-only tables; `SURVEY.COORDINATED_SIMULATION_CREATED` and `…_SURVEY_STARTED` on the hash chain, beside the individual simulations' own audit events; the chain verifies |
| No operational case, call attempt, survey run or finding | row counts and the Script Studio fingerprint identical before and after |

Residual risk, stated plainly: a person with `survey.simulate` can create coordinated records without limit beyond
the rate limit; there is still no retention or clean-up (OR-1); this was tested, not penetration-tested.

## 9. Verification — the twenty demonstrations

Evidence: `docs/acceptance/evidence/ASG-2B/`. Automated tests ran only against the isolated schema `call360_test`.
The conditions that make an application need several surveys are the stand-ins of ASG-2A.

| # | To demonstrate | Result | How |
|---|---|---|---|
| 1 | One application selects two required surveys in a governed order | pass | composite: primary then additional, order `GOVERNED`; call plan `COMPUTABLE`, coordinated simulation `PERMITTED`, eligibility `NOT_ESTABLISHED` |
| 2 | The coordinator starts Survey A | pass | status `RUNNING`, survey 1 `CURRENT`, survey 2 `NOT_STARTED` with no simulation; the question is A's own sentence |
| 3 | Survey A reaches `COMPLETED` | pass | A's own run ends `COMPLETED` |
| 4 | The simulation proceeds to Survey B | pass | B started `PREVIOUS_COMPLETED`; decision `PROCEED` by `SIMULATION_ONLY_COMPLETED_PROCEEDS` |
| 5 | Survey B reaches `COMPLETED` | pass | status `ALL_SURVEYS_COMPLETED`; the record has no outcome of its own |
| 6 | Both keep their own traces and fingerprints | pass | each survey's simulation read on its own: the same version, run and fingerprint; each run equals its golden fixture's (questions asked and every delivered sentence) |
| 7 | Replaying identical inputs gives an identical coordinated result | pass | a new coordinated simulation with the same inputs: the same `replay_sha256` and run fingerprints, different identifiers; also in the browser |
| 8 | Invalid answers do not advance the current survey | pass | an empty answer in A and each invalid number in B: refused by the survey's own run with its code; the same question stays current |
| 9 | A pending answer does not start the next survey | pass | after one of A's two questions, B still has no simulation |
| 10 | `POLICY_UNRESOLVED` stops the coordinator | pass | "not acknowledged" in the second survey: status and stop code `POLICY_UNRESOLVED`, the question current, nothing ended; an acknowledgement afterwards is accepted |
| 11 | A non-`COMPLETED` terminal outcome stops without invented continuation | pass | A answered "no" → `ENDED_WITH_OUTCOME`: `CROSS_SURVEY_POLICY_UNRESOLVED`, decision `STOP`, B never started (one step row), further input `409` |
| 12 | Duplicate survey selection is explicitly unresolved | pass | two groups selecting one version: call plan `COMPUTABLE` but coordinated simulation `BLOCKED`; start `409 DUPLICATE_SURVEY_REQUIREMENT_UNRESOLVED`; nothing recorded |
| 13 | Missing or conflicting order prevents a coordinated run | pass | `409 ORDER_UNRESOLVED`; an unsettled selection `409 SELECTION_UNRESOLVED`; nothing recorded |
| 14 | Missing application facts remain unresolved or blocked | pass | the survey that needs them has a `BLOCKED` plan with the facts `MISSING`; call plan `NOT_COMPUTABLE`; start `409 PLAN_BLOCKED` naming it |
| 15 | Cross-market and unauthorised operations are denied | pass | §8 |
| 16 | No operational records are created | pass | §8 |
| 17 | Existing single-survey simulation behaviour is unchanged | pass | Survey A simulated alone with the same inputs has the same run fingerprint as inside the coordinated simulation; all SS-03B tests and journeys pass unchanged |
| 18 | 82 golden runs and 14 golden plans still pass | **82 / 82, 14 / 14** | `coordination_assignment_and_golden_tests.txt`; the Python results file is unchanged |
| 19 | FI-1, FI-2, LIB-1, SS-03B, ASG-1 and ASG-2A suites pass | **21 / 21**, and the ASG-2B journey: **22 / 22** | `playwright_persisted.txt` |
| 20 | A real-browser journey demonstrates coordinated simulation and its evidence | pass | `zz-asg2a.persisted.ts`, second journey: three surveys in one journey, compared with the server at every step |

Also proved: a composite that is no longer the recorded one cannot be started; replay drift of one survey is the
coordinator's status; with the setting off none of it exists and requirement groups are where they were; migration
`0032` goes down and up and changes nothing else; a withdrawn binding or group still blocks a downgrade (§2).

| Check | Result |
|---|---|
| Backend tests | **825 passed, 0 failed** (822 at ASG-2A; + 3 ASG-2B) |
| `ruff check`, `ruff format --check`, `mypy` (strict, 113 files) | clean |
| Generated files | OpenAPI matches; canonical fixture documents match; Python engine results match (82 runs, 14 plans) |
| Frontend unit tests | **612 passed** |
| `tsc`, `eslint`, `api:check`, production build | clean |
| Persisted journeys | **22 / 22** (FI-1 6, FI-2 3, LIB-1 5, SS-03B 5, ASG-1 1, ASG-2A 1, ASG-2B 1) |
| Prototype journeys | **13 / 13** |
| Standard journeys | **33 / 33** |
| Specs validator | pass |
| Migration head | `0032_survey_coordinated_sim`; development at `0031` |

After the last full backend run one line was added to the ASG-2B test so that it can write the example records of
§10 on request; that file was run again with the coordination, assignment, simulation, rule and golden tests (142
passed).

## 10. Traces and screens

`coordinated_and_individual_traces.txt`: three coordinated simulations as the server returned them — two surveys
completed; `POLICY_UNRESOLVED`; a non-completed ending — each with every survey's own inputs (refused ones marked)
and event trace, the decisions and the fingerprints; and the three states of four composites whose coordinated
simulation is refused. `coordinated_simulation_example.json` is one record in full.

Screens (`screens/`): `ASG2B01` the three separate states · `ASG2B02` the first survey of three · `ASG2B03` a refused
answer stays on the question · `ASG2B04` the first survey completed, the second started · `ASG2B05` a non-answer
stops the coordinator · `ASG2B06` all three surveys completed, with traces and the consolidated report · `ASG2B07`
replay identical · `ASG2B08` a non-completed ending stops without continuation · `ASG2B09` coordination blocked: no
governed order.

## 11. API contract

Contract `04_…` §16. Additive against the committed contract.

| Change | Detail |
|---|---|
| `SurveyCompositePlanOut` | + `states` (three separate answers, §1.1) |
| Three new operations under `/api/v1/survey-assignment` | `POST /composite-plans/{id}/coordinated-simulations` · `POST /coordinated-simulations/{id}/inputs` · `GET /coordinated-simulations/{id}` |
| Two new schemas | `SurveyCoordinatedSimulationIn`, `SurveyCoordinatedSimulationOut` |
| New error codes | `SELECTION_UNRESOLVED`, `NOTHING_SELECTED`, `ORDER_UNRESOLVED`, `PLAN_BLOCKED`, `DUPLICATE_SURVEY_REQUIREMENT_UNRESOLVED`, `COMPOSITE_STALE` (on start); `CROSS_SURVEY_POLICY_UNRESOLVED`, `ALL_SURVEYS_COMPLETED`, `REPLAY_DRIFT`, `NOTHING_CURRENT` (on input) |
| Settings | `survey_coordinated_simulation_enabled` (off by default; needs requirement groups) |
| Migrations | `0032_survey_coordinated_sim` new |

OpenAPI: SHA-256 `e0add7fcd59e3070c1494209fe1769905b3dbff735f069824fc984bbe2fc3624`. Against the committed contract
(`88baaf2c…`): 221 → 246 operations, 451 → 477 schemas, none removed, no existing schema changed, one existing
operation changed in its description only (`openapi_additivity.txt`). The single-survey simulation operations are
unchanged.

## 12. Changed files

Uncommitted, on top of backend `182f6e5`, frontend `9f497d5`, specs `755bf00`. Listed: what changed since the ASG-2A
report (`35_…` §12, `33_…` §8 and `32_…` §10 list the rest).

**Call360-backend**

| File | Change |
|---|---|
| `migrations/versions/0032_survey_coordinated_sim.py` (new) | two insert-only tables |
| `app/domain/survey/coordination.py` (new) | the coordinating layer |
| `app/api/survey_coordinated_simulations.py` (new) | three operations |
| `app/domain/survey/assignment_groups.py`, `app/api/survey_assignment_groups.py` | `coordination_blockers`, `three_states`; `states` on a composite |
| `app/core/settings.py`, `app/main.py`, `app/domain/catalog.py`, `scripts/export_openapi.py`, `contracts/generated/*` | the setting, the head rule for six optional revisions, the catalog, the contract |
| `tests/test_survey_coordination.py` (new) | 3 tests (the journey of twenty demonstrations; setting off; migration `0032`) |
| `tests/test_survey_assignment.py`, `tests/test_survey_assignment_groups.py` | a withdrawn binding or group still blocks a downgrade |
| `tests/test_survey_store.py`, `test_survey_lib1.py`, `test_survey_api.py`, `test_survey_simulation.py`, `test_admin_access.py` | head, table and contract counts |
| `.env` (gitignored) | `SURVEY_ASSIGNMENT_GROUPS_ENABLED=true` for local development |

Not touched: `execution.py`, `callplan.py`, `wording.py`, `simulation.py`, `app/api/survey_simulations.py`,
`assignment.py`, `rule_engine.py`, `rule_inputs.py`, `rule_authoring.py`, `script_assignment.py`, every script table,
migrations `0001`–`0031`.

**Call360-frontend**

| File | Change |
|---|---|
| `src/features/surveystudio/persist/CoordinatedSimulation.tsx` (new) | the Simulator's coordinated mode |
| `src/features/surveystudio/persist/AssignmentGroups.tsx`, `AssignmentPage.tsx`, `assignmentApi.ts` | the three states; the start button; the client |
| `src/features/surveystudio/persist/ServerSimulation.tsx` | `AnswerForm` exported for reuse (no behaviour change) |
| `src/features/surveystudio/persist/PersistedStudioRoot.tsx` | the route |
| `src/styles/survey-studio.css` | styles (appended) |
| `src/api/generated/*`, `src/api/openapi.pinned.json`, `src/api/contract.lock.json` | regenerated client |
| `playwright.persisted.config.ts`, `e2e/persisted/zz-asg2a.persisted.ts` | coordinated simulation on in the persisted test server; the ASG-2B journey |

**Call360-specs**

| File | Change |
|---|---|
| `docs/plans/survey-studio/36_ASG-2B_IMPLEMENTATION_REPORT.md` (new) | this report |
| `docs/plans/survey-studio/04_SS-01_CANONICAL_CONTRACTS.md` | §15.3 amended (`states`), §16 |
| `docs/plans/survey-studio/06_SS-01_DECISION_REGISTER.md` | D-259…D-269 |
| `docs/plans/survey-studio/README.md`, `docs/plans/SESSION_HANDOFF.md` | index and handoff |
| `docs/acceptance/evidence/ASG-2B/` (new) | evidence |

**Outside the repositories:** `_db_backups/call360_dev_before_0031_20261122.dump`, the extended
`_db_backups/RESTORE.md`, and the development database at `0031` with two synthetic groups.

## 13. Known limitations

1. **Development is at `0031`, not `0032`.** Coordinated simulation runs only in the test schema. In development the
   composite offers the button and the server answers that it is not switched on.
2. **The scenarios use stand-in conditions** (OR-3). They prove the mechanics and nothing about real requirements.
3. **A coordinated simulation only goes forward.** There is no "back" and no editing of an earlier survey's answers;
   a different path needs a new coordinated simulation (replay makes that quick).
4. **"Step" gives the ordinary answer** derived from what the question accepts; it is a tester's convenience.
5. **The same facts are given to every survey.** That follows from one application snapshot; it is not a decision
   that surveys share facts in a real call.
6. **A survey with no question** is started and completed in the same step, so the coordinator can pass through it
   without waiting. Correct by the rule; worth knowing.
7. **Starting is all-or-nothing.** A composite with one blocked plan cannot be partly simulated; each survey can
   still be simulated on its own from the composite.
8. **The coordinated page shows codes** for groups, outcomes and steps, as the Simulator does.
9. **No list of past coordinated simulations**, and no retention or clean-up (OR-1).
10. **Screens verified in Chromium at 1440 px** by automated journeys; no business-user or screen-reader review.
11. Carried forward unchanged: the limitations of `35_…` §13, `33_…` §9, `32_…` §11 and the LIB-1 UX limitations.
12. **Not my change:** in `Call360-specs`, `docs/acceptance/evidence/LIB-1/screens.zip` is deleted and a `.DS_Store`
    is modified in the working tree.

## 14. Policy gaps — unchanged, and each still blocking what it blocked

| # | Not decided | Where the simulation stops because of it |
|---|---|---|
| 1 | Live cross-survey continuation after any ending | `CROSS_SURVEY_POLICY_UNRESOLVED`; and the rule "completed proceeds" is simulation-only |
| 2 | Whether one survey's escalation ends the whole callback | the same |
| 3 | Consent reuse across surveys; whether repeated statements or questions may be omitted | nothing is omitted; every survey runs in full |
| 4 | Refusal, silence, repeats, timeouts (D-NA-1…17) | `POLICY_UNRESOLVED` |
| 5 | Two requirements selecting one survey: once or twice | `DUPLICATE_SURVEY_REQUIREMENT_UNRESOLVED` |
| 6 | Whether every multi-survey journey needs a governed order, and who governs it | `ORDER_UNRESOLVED` |
| 7 | Rule attributes for replacement, riders and other triggers (OR-3) | stand-ins only |
| 8 | Rule validation for complementary rules (OR-2) | complementary rules need different priorities |
| 9 | The mapping between assignment inputs and call-plan facts | `input_consistency: UNVERIFIED` everywhere |
| 10 | Operational outcomes of a multi-survey callback | the coordinated record has none |
| 11 | Real callback eligibility; gates G-1…G-8; assigning surveys to real cases | `NOT_ESTABLISHED` everywhere |
| 12 | Which catalog fields may be spoken; approval of wording | published surveys carry no customer values |
| 13 | Retention of simulation records (OR-1) | — |
| 14 | Whether the existing SBQ and assignment rules are the approved process | everything operational |

## 15. Proposed EVAL-1 — evaluation and findings integration: the boundary

**Not authorised. Nothing of it has been started.**

*What EVAL-1 would be:* after a **simulated** run of a published survey version — single or inside a coordinated
simulation — show the findings its answers would raise, each traced to the question, the answer and the rule that
raised it. Simulation only.

*Step 1 — assessment before any design*, as in ASG-1 and ASG-2A: read the existing `answer_evaluation.py`,
`finding_engine.py`, `finding_rules.py`, `simulation_evaluation.py` and `simulation_findings.py`; state what they
read (script question identities, evaluation rules mapped to questions, controls, materiality policies) and what a
survey run provides (item identities and versions, typed answers, evidence states); **document the mismatch before
writing an adapter**. I have not read that code for this purpose and assert nothing about its shape.

*What it can probably be built from without a new decision:*

* the existing finding-rule engine and its governed rule versions, **reused, not copied**;
* the individual simulation's own evidence (answers by execution identity), unchanged;
* simulated findings recorded as `SIMULATION` records, tied to the simulation — never to a case.

*Where it must stop until the owner decides — each a named status, never a default:*

| Question | Without a decision |
|---|---|
| How a published survey **item** is linked to an evaluation or control (the LIB-1 limitation "evaluation and control metadata are not part of reusable assets") | no link is invented; an item with no governed link is `EVALUATION_NOT_MAPPED`, not "no finding" |
| Which finding rules apply to surveys at all | none applies by default |
| What a `POLICY_UNRESOLVED`, a refused answer or an unreached question means for a finding | `EVALUATION_INCOMPLETE`; never read as compliant or as a finding |
| Findings across the surveys of one coordinated simulation: combined, de-duplicated, or per survey | per survey only; nothing combined |
| Severity, materiality and what a finding leads to | shown as the existing rule states them; no disposition, review task or case is created |

*What EVAL-1 would not be:* operational findings; a review workflow; a compliance verdict on a real call; a second
finding engine; a change to Script Studio or to the finding rules.

*Decisions needed before it:* whether evaluation metadata belongs to the survey item or to a separate governed
mapping (as bindings and groups are), and who governs it.
