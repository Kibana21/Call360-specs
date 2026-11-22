# ASG-1 — Survey assignment integration, with the SS-03B security closure and development migration 0029

**Checkpoint:** ASG-1, with the SS-03B simulation-authorisation closure and the development migration `0029`, all
authorised by the owner on 2026-11-22 ("SS-03B Acceptance, Simulation Security Closure and ASG-1 Authorization"),
decision register D-234…D-245 and OR-1.
**Status: BUILT AND TECHNICALLY VERIFIED — presented for the owner's review. Not accepted.**
**Prepared:** 2026-11-22.

**SIMULATION ONLY.** Nothing here assigns a survey to a customer case, starts a call, or makes anything eligible for
one.

**Boundaries held (D-243).** No live customer callback. No Genesys or voice provider. No consent, refusal, timeout or
non-answer policy. Script Studio not modified or retired; no historical script data migrated. No golden fixture
modified. No parallel assignment rules engine and no second rule language. No new authoring application. No actual
survey-to-customer assignment. No new operational outcome or findings behaviour.

**Not committed, not pushed.** The three repositories are still at the commits the owner pushed (backend `182f6e5`,
frontend `9f497d5`, specs `755bf00`). SS-03B, its closure and ASG-1 are all uncommitted working-tree changes: no
commit authorisation has been given for any of them.

**Not claimed.** Not production readiness; not business-user UX acceptance; not screen-reader sign-off; not Compliance
approval of any wording or of any assignment rule; not a decision on any open policy.

---

## 1. SS-03B closure — a permission of its own, and replay that cannot drift silently

SS-03B is recorded as accepted as TECHNICALLY VERIFIED (D-234); its decisions are confirmed (D-237).

### 1.1 `survey.simulate`

| | Before | Now |
|---|---|---|
| Create a simulation, give it an input, generate a call plan | `survey.read` | **`survey.simulate`** |
| Read a simulation or a plan | `survey.read` | `survey.read`, market-scoped |
| Who holds `survey.simulate` | — | no role by migration; in development only `DEV_SURVEY_AUTHOR` (the designated synthetic identity `dev.survey.author`) |

Migration `0029` (not yet applied anywhere but the test schema when this was changed) now creates the permission and
grants it to nobody. All checks are server-side; CSRF, rate limiting and audit are unchanged. The frontend asks the
same question only to explain: a person without the permission sees "You cannot run a simulation" with the reason,
and nothing is requested.

Proof by direct API calls (`tests/test_survey_simulation.py`) and in the browser (`ss03b.persisted.ts`, SS-03B.5):

* a person holding `survey.read`, `survey.edit`, `survey.approve` and `survey.publish` — everything except
  `survey.simulate` — gets `403` on all three state-changing operations and `200` on the two reads;
* an input that such a person tries to give is not recorded;
* each refusal is an `ACCESS.DENIED_FUNCTION` audit event naming `survey.simulate`;
* the permission exists once and no role holds it;
* another market still gets `404`; no session `401`; no CSRF token `403`.

### 1.2 Execution-contract version and drift (D-235)

Contract `04_…` §13.9. Every simulation records the execution contract it was created under
(`call360.survey.execution/1`) and the fingerprint of its run before any input; every input records the fingerprint of
the run after it. On each read the run is recomputed and compared.

| Situation | What a reader sees |
|---|---|
| The recomputed run is the recorded one, under the same contract | `replay_consistent: true` |
| The engine now gives a different result for the same inputs | status **`REPLAY_DRIFT`**, both fingerprints, `result_differs: true`; the screen shows a warning that what is displayed is today's recomputation, not the historical result |
| The contract changed but this run happens to recompute the same | status `REPLAY_DRIFT`, `result_differs: false`, both contract names |
| An input is given to a drifted simulation | `409 REPLAY_DRIFT`; nothing is appended |
| A simulation with no input at all | drift is detected too (the initial fingerprint) |
| A recorded call plan | assembled again on reading; `recompute_consistent: false` if it differs; the recorded plan is what is returned |

Tested by changing the engine's output and, separately, the contract name, under a published survey
(`test_a_simulation_records_its_execution_contract_and_never_hides_replay_drift`).

### 1.3 Retention (OR-1)

There is no retention period, expiry or clean-up for simulation, call-plan or assignment-selection records. Recorded
as operational-readiness item **OR-1**, open. No period was invented.

## 2. Development database — migration `0029_survey_simulation`

Applied to the local development database only, after the security correction passed. Evidence:
`docs/acceptance/evidence/ASG-1/dev-migration-0029/`.

| Precondition | Result |
|---|---|
| Identity and revision | schema `call360` of `Call360_db` on localhost, revision `0028_survey_library` before |
| Inventory | 112 tables, 14,856 rows (`dev29_before.json`) |
| Fresh backup, verified, with restore procedure | `_db_backups/call360_dev_before_0029_20261122.dump`, 1,839,828 bytes, SHA-256 `eb725102…f373350d`, taken with the API server stopped; every table's row count equals the inventory; full SQL dry run of the restore without error (112 tables, 112 data sets, 102 triggers). Procedure in `_db_backups/RESTORE.md` |
| Additive | three tables and their three insert-only triggers added; one row added to `permission` (`survey.simulate`); nothing removed (`dev29_diff.txt`) |
| Only the intended revision | `uv run alembic upgrade 0029_survey_simulation`. Revision after: `0029`. **`0030` was not applied**: no `survey_assignment_*` table exists in development |
| Existing data intact | 110 of 112 pre-existing tables byte-identical in content; the other two are `alembic_version` (the revision) and `permission` (41 → 42). Column definitions identical. 4 surveys, 2 survey versions, 3 candidates, 6 issued codes, 258 callback cases, 11 script versions, 8 assignment-rule versions, 251 script assignments, 24 Voice Lab sessions, 3,051 audit events — all as before |
| Simulation on in local development only | `SURVEY_SIMULATION_ENABLED=true` added to the gitignored `.env`; no committed configuration changed |
| Permission | granted to `DEV_SURVEY_AUTHOR` by `scripts/dev_survey_identities.py`; the checker and publisher identities keep read + their own |
| Readiness | `/health/ready` 200 |
| Creation, answer, replay, plan | as `dev.survey.author` on published `DEV-CHECK-AD5AEA8F` v1.0: simulation created (`SIMULATION`, contract `/1`, consistent); an empty answer refused as `CHOICE_REQUIRED` with the same question current; five answers to `COMPLETED`; the same inputs in a new simulation give the identical run fingerprint; another person reads it and gets the same fingerprint; call plan `READY`, fingerprint verified, the same fingerprint twice (`dev29_walk.txt`) |
| Read-only identity | `dev.survey.checker` (no `survey.simulate`): create `403`, advance `403`, plan `403`; in the browser, "You cannot run a simulation" |
| No operational record | `callback_case` 258, `contact_attempt` 415, `conversation_session` 95, `survey_run` 82, `answer_observation` 555, `script_assignment` 251, `finding` 26, `media_asset` 18, `transcript_run` 18, `transcript_segment` 47 — identical before and after |
| In the browser | screens `DEVS01`…`DEVS04`: first question, run ended with identical replay and the browser engine agreeing, the server call plan, the read-only refusal |

Nothing was reset, re-seeded or destructively altered. Synthetic simulations and plans were **added**. `0029` can be
rolled back (it drops the three tables and the permission); `0028` still cannot (issued codes exist).

ASG-1 is **off** in development: its routes return `404` there, because `0030` is not authorised for development.

## 3. Step 1 — assessment of the existing Assignment Rules capability

What exists (S2-B and S2-C, accepted):

| Part | File | Reusable for surveys? |
|---|---|---|
| Rule language, nine governed fields, specificity, explanation in words | `app/domain/rule_engine.py` | **Yes, unchanged.** Pure; knows nothing of scripts except the words in two messages |
| The decision: precedence, explicit fallback, `NO_MATCH`, `AMBIGUOUS`, `INPUT_MISSING`, `TARGET_NOT_EFFECTIVE`, full trace | `rule_engine.evaluate` | **Yes, unchanged.** The target is an opaque id, a label and an "effective" flag |
| Governed input values | `rule_inputs.options` | **Yes, unchanged** |
| Loading published rules as candidates | `rule_inputs.published_candidates` | **Yes, unchanged**, then re-targeted |
| Authoring, validation, conflict analysis, maker-checker, publication, versioning, history, diff, simulation over cases | `rule_authoring.py`, `/assignment-rules…`, the Assignment Rules screens | **Yes, as they are** — rules are still made there |
| Assigning a script version to a case, holds, idempotency, assignment history | `script_assignment.py` | **No, and not touched.** That is operational assignment, which ASG-1 must not do |

**Contract mismatch 1 — the target.** `script_assignment_rule_version.target_script_version_id` is a NOT NULL foreign
key to `script_version`; the rule's market is read through the script family; triggers guard the link; every loader
joins through it. A rule that targets a survey version *instead of* a script version would require altering those
Script Studio tables, constraints, triggers and queries, and the Assignment Rules screens that live with Script
Studio. The boundary "do not modify Script Studio" rules that out.

**Contract mismatch 2 — the inputs.** Rules read nine assignment inputs (`market`, `case_purpose`, `product_family`,
`product_code`, `is_ilp`, `risk_band`, `selling_channel`, `premium_frequency`, `contact_role`). The call plan reads
catalog facts (`policy.annual_premium`, `customer.age_years`, …). No approved mapping connects the two.

**The smallest safe extension.** One governed artifact — a **binding** from an exact published rule version to an
exact published survey version — and an adapter of about twenty lines that hands the existing engine the existing
candidates with only their target replaced. No rule is copied, no condition is re-implemented, no precedence is
re-decided. A synthetic application states both sets of inputs side by side.

What this does **not** achieve, plainly: a rule still names a script version too, because it must. The rule decides
*which rule wins*; the binding says *which survey that rule stands for*. Making a survey version the rule's own target
is a later step that needs the owner's decision to change the Script Studio rule tables (D-245 a).

## 4. Steps 2 and 3 — governed selection, connected to the call plan

`app/domain/survey/assignment.py`, `app/api/survey_assignments.py`, migration `0030_survey_assignment`. Contract
`04_…` §14.

| Requirement | How it is met |
|---|---|
| Only valid published survey versions | a binding can be proposed and published only to the currently PUBLISHED version, manifest verified; at selection the version must still be PUBLISHED |
| Exact immutable version references | the binding stores the version id with its content and manifest fingerprints; it is insert-only |
| Market and authorisation scope | rules are loaded for the application's market only; the market must be the caller's; rule and survey must share it; everything outside the caller's markets is `404` |
| Existing condition semantics | `rule_engine.evaluate` on `rule_inputs.published_candidates` |
| Precedence and matching preserved | a test shows the adapter's candidates equal the originals in every field but the target |
| Matched, no match, ambiguous, unknown input | `MATCHED`, `NO_MATCH`, `AMBIGUOUS`, `UNKNOWN_INPUT`, and `TARGET_UNAVAILABLE` — with the engine's own outcome code kept beside it |
| Never silently a fallback survey | a fallback is only an explicitly governed fallback *rule*, and the result says `SELECTED_BY_FALLBACK`. A winning rule with no survey gives `SURVEY_NOT_BOUND`; no lower rule and no fallback is used instead |
| Never replace a pinned version | a superseded or withdrawn version gives `TARGET_NOT_EFFECTIVE`; nothing newer is substituted |
| Maker, checker, publisher | propose (`survey.edit`), approve (`survey.approve`), publish (`survey.publish`): three different people, enforced by the service and by a database trigger whatever permissions they hold; each refusal audited |
| Explanation | `decision.reason`, `winning_rules`, `missing_inputs`, and a trace line for every rule with each condition's expected and actual value and result |

The call plan: when a version is selected its manifest is verified, the SS-03B assembler computes the plan for the
application's facts, and the selection is recorded with the plan. The response gives the selected version, the
matching rule, the plan fingerprint, the modules included and excluded, every fact read with its state, and the open
points. It states that a plan that can be computed is not eligibility for a call. When nothing is selected, no plan is
made.

## 5. Step 4 — in Survey Studio

One page, **Survey assignment**, reached from the Surveys list. No rule is authored here: the page links to
Assignment Rules for that.

| Asked for | On the page |
|---|---|
| Inspect the published survey version | each bound rule links to the version's page; so does the result |
| Inspect the applicable governed policy | section 1: the published rules in the engine's order, in words, with priority and specificity, and the survey version each stands for — or "No survey bound. If this rule wins, nothing is selected" |
| Bind, with governance | propose (choose a published version), approve, publish, withdraw — each offered only to a person who may do it, and refused by the server otherwise |
| Supply or choose a synthetic application | section 2: one select per governed input, including "not known"; the existing synthetic customers supply the facts |
| Why a survey was or was not selected | section 3: the outcome in a sentence, the engine's reason, the rule and version, what is not known; and "Why — every rule the engine considered" with each condition met, not met or not known |
| Generate the call plan | section 4: computable or blocked, fingerprint, modules, missing facts, open points; a link to the full plan |
| Start a server simulation of the selected version | "Start a simulation of this version" opens the existing Simulator on that simulation |
| Assignment and execution evidence together | the Simulator shows "started from an assignment selection" with a link back; the selection lists the simulations started from it |

The Simulator can now open an existing simulation by its link instead of always creating one.

## 6. Step 5 — verification

Evidence: `docs/acceptance/evidence/ASG-1/`. Automated tests ran only against the isolated schema `call360_test`.

| # | To demonstrate | Result | Where |
|---|---|---|---|
| 1 | Two synthetic applications select different published survey versions by governed rules | pass | API test: rules `ASG-A`, `ASG-B` made through the existing Assignment Rules API, bound by three people; application A → survey A, application B → survey B. Browser journey: screens `ASG04`, `ASG05` |
| 2 | The same inputs select the same version and give the same call-plan fingerprint | pass | a second selection with the inputs in another order: same version, same decision fingerprint, same plan fingerprint, in a new record. Also in the browser |
| 3 | A missing fact does not silently become FALSE | pass | a missing assignment input → `INPUT_MISSING` / `UNKNOWN_INPUT`, both rules `UNKNOWN` (not `NO_MATCH`), nothing selected, no plan. A missing catalog fact → `MISSING` in the plan and the module `UNKNOWN_SKIPPED` / `UNKNOWN_HALTS`. Screens `ASG06`, `ASG07` |
| 4 | Unpublished or withdrawn versions cannot be selected | pass | a withdrawn version → `TARGET_NOT_EFFECTIVE`, the same rule still wins, nothing substituted; binding to it refused `VERSION_NOT_PUBLISHED`; superseded likewise (unit); an unknown version `404` |
| 5 | A cross-market version cannot be selected | pass | a person of another market sees no SG rule, binding, version or selection (`404`), cannot bind or select for SG; a binding whose market is not the application's is not effective (unit); rule and survey of different markets cannot be bound (`MARKET_MISMATCH`) |
| 6 | Ambiguous or unmatched assignments are explicit | pass | `NO_MATCH`, `AMBIGUOUS`, `AMBIGUOUS_SAME_TARGET`, explicit `SELECTED_BY_FALLBACK`, and `SURVEY_NOT_BOUND` where a bound lower rule and a fallback are *not* used instead (`test_matched_no_match_ambiguous_unknown_and_fallback_are_told_apart`); screen `ASG02` |
| 7 | Changing an assignment draft does not modify a published assignment version | pass | a new draft version of rule `ASG-A` (other conditions, other priority) and an open proposal for another binding: the same application still selects the same version with the same decision fingerprint, and the policy's published rules are unchanged. Published rule versions and bindings are immutable in the database |
| 8 | No Script Studio assignment behaviour regresses | pass | the existing `test_assignment_rules.py` and `test_script_assignment.py` pass unchanged, also when run *after* the ASG-1 tests; script assignments, case states and holds have the same fingerprint before and after the ASG-1 journey; binding adds no rule version |
| 9 | 82 golden runs and 14 golden plans still pass | **82 / 82, 14 / 14** | `golden_parity.txt`; the cross-engine test (browser engine vs Python) 96 / 96 |
| 10 | FI-1, FI-2, LIB-1 and SS-03B full-stack journeys pass | **19 / 19**, and the ASG-1 journey: **20 / 20** | `playwright_persisted.txt` |
| 11 | Backend, frontend, API, security, type and lint checks | clean | below |
| 12 | No operational case, attempt or session created | pass | row counts of `callback_case`, `contact_attempt`, `conversation_session`, `survey_run`, `script_assignment`, `finding`, `media_asset`, `transcript_run` identical before and after the ASG-1 journey; the same on development after the 0029 walkthrough |

| Check | Result |
|---|---|
| Backend tests | **818 passed, 0 failed** (814 at SS-03B; + 1 replay drift, + 3 ASG-1) |
| `ruff check`, `ruff format --check`, `mypy` (strict, 109 files) | clean |
| OpenAPI | regenerated and matching: SHA-256 `38f2034b65bf520e0e4b32b8f413bf9c0789b6fac314f7abc8d451ffbf64c74b`. Against the committed contract: 221 → 236 operations, 451 → 467 schemas, none removed, no existing schema changed, one existing operation changed in its description only (`openapi_additivity.txt`) |
| Generated files | canonical fixture documents match; Python engine results match (82 runs, 14 plans) — the engine's output did not change |
| Frontend unit tests | **612 passed** |
| `tsc`, `eslint`, `api:check`, production build | clean |
| Persisted journeys | **20 / 20** (FI-1 6, FI-2 3, LIB-1 5, SS-03B 5, ASG-1 1) |
| Prototype journeys | **13 / 13** |
| Standard journeys | **33 / 33** |
| Specs validator | pass |
| Migration head | `0030_survey_assignment`; development at `0029` |

Screens (`screens/`): `ASG01` the policy with proposed bindings · `ASG02` the winning rule has no survey, nothing
selected · `ASG03` bindings published · `ASG04` application A selects survey A · `ASG05` application B selects survey
B, with the trace and the plan · `ASG06` a missing fact stays missing in the plan · `ASG07` an unknown input selects
nothing · `ASG08` the simulation started from the selection · `ASG09` assignment and execution evidence together ·
`SIM11` a reader cannot simulate.

Three things went wrong on the way and were corrected: the ASG-1 browser journey first ran before the FI-1 journey,
which expects an empty database, so it is now ordered last; the ASG-1 backend test left highest-priority rules
behind that disturbed the existing rule tests when run after it, so it now resets the test schema before and after
itself; and a trace label read "Tied" for rules that could not be decided, which is now "Cannot be decided".

## 7. API changes

Contract `04_…` §13.6, §13.9 and §14. Purely additive against the committed contract.

| Change | Detail |
|---|---|
| Permission of three existing SS-03B operations | `POST …/simulations`, `POST …/inputs`, `POST …/call-plans`: `survey.read` → `survey.simulate` (SS-03B was never committed or enabled outside tests before this) |
| `SurveySimulationOut` | + `engine_contract`, `current_engine_contract`, `initial_run_sha256`, `run_status`, `drift`; `status` may be `REPLAY_DRIFT` |
| `SurveyCallPlanOut` | + `plan_contract`, `current_plan_contract`, `recomputed_fingerprint`, `recompute_consistent` |
| New error | `409 REPLAY_DRIFT` |
| Ten new operations under `/api/v1/survey-assignment` | `options`, `policy`, binding read / propose / decision / publish / withdraw, evaluation create / read, start simulation (§14.4) |
| Ten new schemas | `SurveyAssignment…` |
| Settings | `survey_assignment_enabled` (off by default; needs simulation and survey definitions) |
| Migrations | `0029` amended before it was applied anywhere but the test schema (permission, `engine_contract`, `initial_run_sha256`, `plan_contract`); `0030_survey_assignment` new |

Nothing of the existing `/assignment-rules…`, `/script-assignments…` or `/cases/{id}/script-assignment…` operations
changed.

## 8. Changed files

Uncommitted, on top of backend `182f6e5`, frontend `9f497d5`, specs `755bf00`. Listed here: what changed since the
SS-03B report (`32_…` §10 lists the rest).

**Call360-backend**

| File | Change |
|---|---|
| `migrations/versions/0029_survey_simulation.py` | + permission `survey.simulate`; + `engine_contract`, `initial_run_sha256`, `plan_contract` |
| `migrations/versions/0030_survey_assignment.py` (new) | four insert-only tables and the binding-event guard |
| `app/domain/survey/execution.py` | + `CONTRACT` (no change to any result) |
| `app/domain/survey/simulation.py`, `app/api/survey_simulations.py` | `survey.simulate`; contract recorded; drift detected and reported; plans re-assembled on reading |
| `app/domain/survey/assignment.py` (new) | bindings, the re-targeting adapter, selection, records |
| `app/api/survey_assignments.py` (new) | ten operations |
| `app/core/settings.py`, `app/main.py`, `app/domain/catalog.py`, `scripts/export_openapi.py`, `contracts/generated/*` | the setting, the head rule for four optional revisions, the catalog, the contract |
| `scripts/dev_survey_identities.py`, `scripts/e2e_survey_setup.py` | `survey.simulate` for the development author; a simulator identity for browser tests |
| `tests/test_survey_assignment.py` (new) | 3 tests |
| `tests/test_survey_simulation.py`, `test_survey_store.py`, `test_survey_lib1.py`, `test_survey_api.py`, `test_admin_access.py` | permission and drift tests; head, table, permission and contract counts |
| `.env` (gitignored) | `SURVEY_SIMULATION_ENABLED=true` for local development |

Not touched: `rule_engine.py`, `rule_inputs.py`, `rule_authoring.py`, `script_assignment.py`,
`app/api/assignment_rules.py`, `app/api/script_assignments.py`, every script table and migration.

**Call360-frontend**

| File | Change |
|---|---|
| `src/features/surveystudio/persist/assignmentApi.ts`, `AssignmentPage.tsx` (new) | the Survey assignment page |
| `src/features/surveystudio/persist/PersistedStudioRoot.tsx` | the route and the link from the Surveys list |
| `src/features/surveystudio/persist/ServerSimulation.tsx`, `ServerCallPlan.tsx`, `SimulatorPage.tsx` | `survey.simulate`; drift warning; opening an existing simulation; the link back to a selection |
| `src/styles/survey-studio.css` | styles (appended) |
| `src/api/generated/schema.d.ts`, `openapi.pinned.json`, `contract.lock.json` | regenerated client |
| `playwright.persisted.config.ts`, `e2e/persisted/ss03b.persisted.ts`, `e2e/persisted/zz-asg1.persisted.ts` (new) | assignment on in the persisted test server; the simulator identity; the ASG-1 journey |

Not touched: `src/features/scripts/*`, `src/features/rules/*`, `src/styles/app.css`, the Composer, Builder and Graph.

**Call360-specs**

| File | Change |
|---|---|
| `docs/plans/survey-studio/33_ASG-1_IMPLEMENTATION_REPORT.md` (new) | this report |
| `docs/plans/survey-studio/04_SS-01_CANONICAL_CONTRACTS.md` | §13.6 amended, §13.9, §14 |
| `docs/plans/survey-studio/06_SS-01_DECISION_REGISTER.md` | D-234…D-245, OR-1 |
| `docs/plans/survey-studio/README.md`, `docs/plans/SESSION_HANDOFF.md` | index and handoff |
| `docs/acceptance/evidence/ASG-1/` (new) | evidence |

No file under `fixtures/`, `canonical-documents/` or `python-results/` changed in this checkpoint.

**Outside the repositories:** `_db_backups/call360_dev_before_0029_20261122.dump`, the extended
`_db_backups/RESTORE.md`, and the development database at `0029` with `survey.simulate` granted to
`DEV_SURVEY_AUTHOR`.

## 9. Known limitations

1. **Development is at `0029`, not `0030`.** ASG-1 runs only in the test schema. In development the Survey assignment
   page reports that assignment is not available.
2. **A rule still names a script version** (§3). Binding is an adapter, not native survey targeting.
3. **Every input a published rule reads must be known**, or the existing engine answers `INPUT_MISSING` — even when
   the rule that reads it would have lost. That is the engine's accepted fail-closed rule (D-61), kept as it is.
4. **The development and test rule sets were written for scripts.** A seeded rule that outranks a bound rule and has
   no binding makes the selection `SURVEY_NOT_BOUND`. That is correct, and it means a real policy needs every
   reachable rule bound.
5. **Assignment inputs and call-plan facts are entered separately** and can disagree (an "ILP" product family beside
   a "Protection" fact). Nothing checks one against the other, because no mapping is approved.
6. **A binding is to one rule version.** Publishing a new version of a rule leaves it unbound until a new binding is
   published.
7. **The page lists published versions by asking each survey for its history** — fine for a handful of surveys, not
   for hundreds.
8. **The downgrade refusal of `0030`** (while a binding exists) is not covered by an automated test; the empty
   downgrade and upgrade are.
9. **Reading the policy needs only `survey.read`**, so a person without `script.read` can read the published rules of
   their market on this page (D-245 e).
10. **No retention or clean-up** of simulation, plan or selection records (OR-1).
11. **Screens verified in Chromium at 1440 px** by automated journeys; no business-user or screen-reader review.
12. Carried forward unchanged: the SS-03B limitations of `32_…` §11 and the LIB-1 UX limitations.
13. **Not my change:** in `Call360-specs`, `docs/acceptance/evidence/LIB-1/screens.zip` is deleted and a `.DS_Store`
    is modified in the working tree.

## 10. Unresolved business and Compliance decisions

| | Decision | Needed for |
|---|---|---|
| 1 | D-NA-1…D-NA-17: silence, refusal, repeats, timeouts, optional blanks, consent refusal | anything beyond simulation |
| 2 | Which catalog fields may be spoken; approval of wording | published surveys with customer values |
| 3 | Whether assignment rules should target survey versions natively, which means changing the Script Studio rule tables | retiring the binding adapter |
| 4 | The mapping, if any, between assignment inputs and call-plan facts, and the source of each in a real application | assigning from real data |
| 5 | Whether a superseded survey version stays selectable until re-bound, or must be re-bound first (today: must be re-bound) | operating a policy across survey releases |
| 6 | Who may bind: the survey roles (today) or the script roles; and whether reading the policy needs `script.read` | role design |
| 7 | Retention of simulation and selection records (OR-1) | operational readiness |
| 8 | Live-call eligibility and gates G-1…G-8; assigning surveys to real cases | any operational use |
| 9 | Whether the existing SBQ and assignment rules are the approved process (still a working hypothesis) | everything operational |

## 11. Proposed next checkpoint — not authorised

**EVAL-1 — Evaluation and findings integration, simulation only.** Connect a completed *simulated* run of a published
survey version to the existing answer-evaluation and finding-rule capabilities, so that a simulation ends with the
findings its answers would raise, each traced to the question, the answer and the rule.

1. *Assessment first*, as in ASG-1: inspect `answer_evaluation.py`, `finding_engine.py`, `finding_rules.py`,
   `simulation_evaluation.py` and `simulation_findings.py`; state what they read (script question identities, control
   mappings) and what a survey run provides (item identities, evidence states); document the mismatch before any
   adapter.
2. *The smallest governed link* between a published survey item and the control or finding rule that reads it —
   which is also the LIB-1 limitation "evaluation and control metadata are not part of reusable assets".
3. *Simulated findings* recorded as simulation records, never as operational findings; no disposition, no review
   task, no case.
4. *In the Simulator*: the findings a run would raise, beside the trace.

It would need decisions the owner has not made: whether evaluation metadata belongs to the survey item or to a
separate governed mapping, and which finding rules apply to surveys. Nothing of it has been started.
