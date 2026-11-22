# SS-03B — Python execution, call-plan assembly and server-backed simulation: implementation report

**Checkpoint:** SS-03B (SS-03B.1, SS-03B.2, SS-03B.3), with the LIB-1 security correction and the development
migration `0028`, all authorised by the owner on 2026-11-22 ("Accept LIB-1, Close Security Gap and Authorize SS-03B"),
decision register D-222…D-233.
**Status: BUILT AND TECHNICALLY VERIFIED — presented for the owner's review. Not accepted.**
**Prepared:** 2026-11-22.

**SIMULATION ONLY.** Nothing built here can start, schedule, authorise or make anything eligible for a customer call.

**Scope held (D-231).** No production calls or live survey execution. No Genesys, Asterisk, GPT Live or Azure Speech.
No consent, timeout, repeat or non-answer business policy. No live-call eligibility. No survey assigned to a real
customer case. No operational findings or dispositions. Script Studio not modified or retired; no legacy data
migrated. Protected development data not reset or re-seeded. No other authoring application. **No golden fixture
expectation was modified.**

**Not committed, not pushed.** All three repositories are at the commits the owner pushed (backend `182f6e5`, frontend
`9f497d5`, specs `755bf00`); everything in this report is uncommitted working-tree change.

**Not claimed.** Not production readiness; not business-user UX acceptance; not screen-reader sign-off; not
Compliance approval of any wording; not a decision on any no-answer, refusal or consent policy.

---

## 1. LIB-1 security closure — `GET /survey-library/{kind}`

LIB-1 is recorded as TECHNICALLY ACCEPTED (D-222). The gap flagged in `31_…` is closed (D-223).

| | Before | Now |
|---|---|---|
| Lists | every frozen version of the kind, every market, whoever made it | only versions pinned by a **published** survey version **in the reader's markets** |
| Draft, in-review, rejected, withdrawn | listed | never listed |
| Another market | visible | nothing |
| With `survey_library_enabled` off | same leak | same rule: it is in the store, not in the library router |

Kept: the path, the permission (`survey.read`), the response shape. **Intentional behaviour change:** the list is
shorter; `candidates` and `versions` in a row now both count the published versions that pin it. Documented in
contract `04_…` §13.1 and in the operation's own description in the OpenAPI.

Evidence, by direct API calls on real PostgreSQL (`tests/test_survey_lib1.py`):

* `test_the_legacy_library_list_shows_only_published_reusable_versions_in_the_readers_market` — a published survey,
  a never-submitted draft, a candidate in review, a rejected one and a withdrawn one are built by one author; for
  every kind the legacy list holds none of the four hidden surveys' codes; the legacy list and the component library
  name exactly the same versions; a person with every permission in another market gets an empty list for every kind;
  a signed-in person without `survey.read` gets `403`; no session gets `401`.
* `test_the_legacy_library_rule_holds_with_the_library_setting_off` — the same on an application with the library
  setting off.
* The existing LIB-1 tests of `GET /survey-components`, `GET /survey-components/{kind}/{code}/{version}` and
  `POST /survey-definitions/{id}/codes` pass unchanged, as do the five LIB-1 browser journeys (§9).

No published asset and no version reference was changed: the correction is one read query.

## 2. Development database — migration `0028_survey_library`

Applied to the local development database only (schema `call360` of `Call360_db` on `localhost`), under the ten
conditions of D-224. Evidence: `docs/acceptance/evidence/SS-03B/dev-migration-0028/`.

| # | Condition | Result |
|---|---|---|
| 1 | Identity and revision confirmed | development schema, revision `0027_survey_definitions` before |
| 2 | Inventory | 111 tables, 14,800 rows (`dev28_before.json`: per-table row counts and content hashes) |
| 3 | Fresh backup, verified, with a restore procedure | `_db_backups/call360_dev_before_0028_20261122.dump`, 1,831,599 bytes, SHA-256 `d46e74d9…4f0017`; verified by table and row counts (111 / 14,800) and a complete SQL dry run of the restore (111 `CREATE TABLE`, 111 `COPY`, 101 `CREATE TRIGGER`; `dev28_restore_dryrun.txt`). `_db_backups/RESTORE.md` has the procedure |
| 4 | Additive | one table, one sequence, one trigger added; nothing else (`dev28_diff.txt`) |
| 5 | Only `0028` applied | revision after: `0028_survey_library`. **`0029` was not applied** |
| 6 | Sequence and table verified | `survey_code_seq` starts at 100001; `survey_issued_code` has its five columns and its insert-only trigger |
| 7 | Existing tables and data intact | 110 of 111 pre-existing tables byte-identical in content; the 111th is `alembic_version` (one row, the revision). Column definitions identical. Protected synthetic records unchanged: 2 surveys, 2 versions, 3 candidates, 13 frozen assets, 258 callback cases, 11 script versions, 24 Voice Lab sessions, 3,035 audit events |
| 8 | Library on in local development only | `SURVEY_LIBRARY_ENABLED=true` added to the gitignored development `.env`; no committed file changed; the test and default configurations are untouched |
| 9 | Readiness and existing permissions | `/health/ready` 200; the three development survey identities hold exactly the permissions they had; existing surveys `DEV-CHECK-AD5AEA8F` (r10, v1.0) and `S-DEV-FI2-WALKTHROUGH` (r1, v1.0) unchanged |
| 10 | Discovery, insertion, copy-on-write with synthetic data | as `dev.survey.author`: found and previewed a published module; pinned it into a new draft `S-DEV-LIB-PIN` (same code, same revision, same fingerprint, not owned); made an edited copy in `S-DEV-LIB-COPY` (server-issued `M-100001` r1 and `Q-100002`, each recording what it was copied from). Screens `DEVL01`…`DEVL03`, record `dev28_walk.txt` |

Nothing was re-seeded, truncated, reset or removed. Two synthetic draft surveys and six issued codes were **added**
by the walkthrough.

**Downgrade is now blocked.** `0028` refuses to downgrade while any issued code is recorded, and six are. The
recovery procedure that remains viable: (a) switch the library off (`SURVEY_LIBRARY_ENABLED=false`) — the schema at
`0028` serves everything else correctly; or (b) a full restore of the verified backup above, which returns the
database to `0027` as it was at the backup and discards what was added since.

After this session the development server also runs the SS-03B code. It is ready at `0028` because
`survey_simulation_enabled` is off there: the five simulation operations do not exist on it (`404`).

## 3. SS-03B.1 — the execution engine

`Call360-backend/app/domain/survey/execution.py`, with `wording.py`. Contract `04_…` §13.2–§13.3.

**Architecture.**

| Layer | File | Knows about |
|---|---|---|
| Pure evaluation | `execution.py`, `wording.py`, `callplan.py`, reusing `conditions.py`, `documents.py`, `validator.py` helpers | documents, facts, answers. No database, clock, network, model or randomness — a test reads the module source to prove it |
| Persistence | `simulation.py` | the three simulation tables and the survey store; nothing operational |
| API | `app/api/survey_simulations.py` | HTTP, permission, market, CSRF, rate limit, audit |
| Transport | none | there is no voice, telephony or model adapter in SS-03B |

One engine. It does not replace, wrap or fork the operational script runtime (`app/domain/lifecycle.py` and the script
engine), which is untouched; it reuses the survey domain's existing three-valued condition evaluator rather than
writing another. It never produces wording: an item is delivered as its pinned wording version renders, or not at
all.

**What it executes:** module sequencing and activation; eligibility with an explicit policy for UNKNOWN; graph
navigation; decision nodes; yes/no and single-choice routing; multi-select answers with ordered, de-duplicated
follow-up queues and interruptions; other/free-text answers; numeric validation; acknowledgements; statements;
first-matching-rule routing; forward-only module jumps; mandatory-escalation precedence; six terminal states;
three-valued conditions; explicit rejection of invalid answers; a complete event trace.

**Golden parity — exact.** `tests/test_survey_execution.py` holds no expected value; it runs each expected run of each
fixture and compares with what the fixture states, in the fixture's own vocabulary.

| Schema | Fixtures | Expected runs | Compared | Pass |
|---|---|---|---|---|
| /1 | F1–F8 | 25 | asked sequence, modules and statuses, survey outcome, halt reason and place, evidence, trace, edges taken | 25 |
| /2 | G1–G6 | 18 | asked, modules, terminal state, routing trace, evidence states | 18 |
| /3 | H1–H4 | 16 | the same, with mandatory-escalation trace lines | 16 |
| /4 | J1 | 4 | the same | 4 |
| /5 | K1–K8 | 19 | asked, every delivery with exact text and values, rejections, modules, terminal, pending question, evidence states | 19 |
| | **27** | **82** | plus all 19 rejected answers, by stable code and in order | **82** |

Schema /1 has one halted state where the engine keeps three apart; the mapping is stated in the test
(`in_v1_terms`), as it already is for the browser engine, and nothing is collapsed inside the engine.

Further tests in the same file: the same inputs give the same run, and the engine changes nothing it is given; a run
replayed from its recorded inputs is identical event for event; an input for any question but the current one is
refused and nothing after it is applied; an invalid answer offered three times is refused three times and the same
question stays current; a statement is delivered with no input and is never "asked"; every delivered sentence is a
pinned wording, exactly; a missing fact gives UNKNOWN, names what was missing, and never takes the "otherwise" route;
a non-answer (§5).

## 4. SS-03B.2 — the call plan

`Call360-backend/app/domain/survey/callplan.py`. Schema `call360.survey.call-plan/1`, contract `04_…` §13.4.

Inputs: the documents a published version pins (resolved through its manifest), an immutable fact snapshot, and the
variables declared in the pinned wording. Output: modules IN / OUT / CONDITIONAL / HALTS with the reason and what was
read; every fact read and how it stood; the exact deliverable wording of every item, or that it cannot be delivered;
every point an answer still decides, with its alternatives; stable issue codes; a SHA-256 fingerprint.

**Golden parity — exact: 14 of 14 expected plans** (`tests/test_survey_callplan.py`), comparing status, issues,
input states, module statuses, every item (statement, role, mandatory, delivery mode, wording version, exact text,
values, certainty) and every open point with its alternatives.

| Rule (D-227) | Proof |
|---|---|
| Same inputs, same plan | assembled twice, the second time with the fact keys reversed: equal plan, equal fingerprint. Different applications of K8 have different fingerprints |
| UNKNOWN is never FALSE | with no facts every eligibility is `UNKNOWN` and its module is `HALTS` or `OUT` with reason `UNKNOWN_HALTS` / `UNKNOWN_SKIPPED` — never `NOT_ELIGIBLE` |
| Missing data is not guessed or defaulted | every input is `MISSING` with value null; an empty string is the same as absent (same fingerprint) |
| Numbers never rounded or truncated | `12000.005` as an amount, `0.1 + 0.2`, `35.5` as a whole number: unusable, not rounded. `12000.5` → `SGD 12,000.50`; `35.0` → `35` |
| An undeliverable item blocks the plan | its `text` is null and it is a `WORDING_VALUE_MISSING` issue; nothing is put in its place |
| No uncontrolled delivery | a field the catalog marks not speakable is `NOT_PERMITTED` and is never rendered; the engine has no code path that composes text |
| A plan and a run agree | for every schema /5 run, each delivered sentence equals the plan's sentence for that item |
| A plan is not eligibility | the plan has exactly eight top-level fields, none about calling; a test fails if words such as "eligible for call" appear |

## 5. No-answer and refusal (D-229)

No policy was decided. D-NA-1…D-NA-17 and their parameters remain open exactly as recorded.

| Situation | What the simulation does |
|---|---|
| A question needs an answer and none is given | stays `PENDING`. Nothing times out; there is no clock in the engine |
| An invalid answer | refused with its stable code; recorded as refused; the same question stays current (attempt + 1) |
| "Not acknowledged" | refused with `NON_ANSWER_POLICY_UNRESOLVED`, recorded as an observation, never as an answer |
| An action would need an undecided policy | status **`POLICY_UNRESOLVED`** with `{key, code, reason}`. `terminal` is null. No `END` event. No module outcome. No escalation and no completion is synthesised |
| A real acknowledgement afterwards | accepted: the status was never an ending |

There is no repeat limit, silence window, timeout value or refusal behaviour anywhere in the code (the one bound,
twenty consecutive refused answers supplied in a single call, is a guard against an endless loop of a caller-supplied
function and ends as `DRAFT_INVALID`, not as an outcome; the API gives one input per call and never reaches it).

## 6. SS-03B.3 — the Simulator and Call plan on Python results

No screen was redesigned. Guided Builder, Graph and the Lego Composer are untouched. In persisted mode the existing
**Journey simulator** and **Call plan** screens gain a two-way switch:

* **Published version · Call360 server** (the default) — everything shown is the server's;
* **Draft · browser preview** — the previous behaviour, now labelled as a preview that is not the Call360 engine.

| Required | Where |
|---|---|
| Simulate published versions with synthetic profiles | version picker; the eleven existing synthetic customers; the facts sent are shown |
| Step by step | answer by hand with typed controls, or **Step** (the ordinary answer), **Run to the end**, **Start again** |
| Readable decision and execution trace | "Execution trace": one line per server event, with what each condition read |
| Why a module was included or excluded | the Modules list: status and the reason, from the server's entry event |
| Exact delivered wording | the stage ("The customer would hear, exactly") and "Exact wording delivered" with item, wording version and text |
| Validation and rejection reasons | the stable code and a sentence, on the stage and in the trace; the question does not change |
| Scenario comparison | "Compare with": two customers each run to the end on the server; rows that differ are marked |
| Replay of the same inputs | "Replay the same inputs": a new simulation is fed the recorded inputs and the run fingerprints are compared |
| Call-plan inspection | the Call plan screen: verdict, issues, fingerprint, facts read, modules, exact wording, open points |
| Simulation is not an operational call | a standing note on both screens; "Kind of record: Simulation"; the end card says no case, finding or disposition was created; the plan says it is not permission to call |

**The transition comparison (D-228).** The browser's engine is run on the *same published documents* and the *same
recorded inputs* and compared with the server's run on seven aspects (questions answered, current question and its
sentence, ending, modules, every delivery with its wording, refusals); the plan on five. Agreement is one quiet line.
A difference is a warning panel listing each aspect with the server's and the browser's value, and says the server's
result stands.

**Regression test across both engines:** the backend exports what the Python engine produces for all 82 runs and 14
plans (`python-results/`, with a `--check` for drift); `persist/serverRun.test.ts` runs the browser engine on the
canonical documents and inputs and requires no difference: **82 of 82 runs and 14 of 14 plans agree.**

**One difference was found, investigated and corrected.**

| | |
|---|---|
| Found by | the cross-engine test, fixture F4, run "CRITICAL_RISK interrupts" |
| Symptom | Python ended the module with `ESCALATE` (as the golden fixture expects); the browser engine, given the canonical document, carried on to a follow-up |
| Cause | the document's interrupt has no `policy`. The contract means `STOP_ESCALATE` then (the server's validator and engine read it so). The browser engine read an absent policy as "resume". It passed its own golden test only because that test's fixture loader filled the policy in |
| Reach | only documents that omit the policy — none the editor writes; a document saved through the API could |
| Correction | `policyOf` in `model/types.ts`, used by the browser engine, plan and graph: read as `STOP_ESCALATE`, never written back into the document (the lossless mapping is unchanged) |
| Covered by | the 82-run cross-engine test |

The frontend holds no second set of rules that evolves on its own: the comparison is the guard, and it is in the
unit suite.

## 7. API, records and audit (D-230)

Five operations, contract `04_…` §13.6; OpenAPI regenerated, purely additive (§9). Records: migration
`0029_survey_simulation`, contract §13.5.

| Requirement | How |
|---|---|
| Isolated simulation | `survey_simulation` + `survey_simulation_input`; a run is never stored, only its inputs, replayed on the version's own documents |
| Typed inputs | answer fields of the contract only; an unknown field or wrong shape is `422` and nothing is recorded; validity is the engine's decision and is recorded |
| State and trace | `GET` replays now and returns the whole run, its fingerprint and whether it matches the fingerprint recorded with the last input |
| Immutable version references | each record stores the version id with its content and manifest fingerprints; the manifest is verified against the stored documents before anything runs (`409 MANIFEST_MISMATCH`) |
| Market permissions | every read and write is scoped to the caller's markets; outside them the thing does not exist (`404`) |
| Audit | `SURVEY.SIMULATION_CREATED`, `SURVEY.SIMULATION_INPUT`, `SURVEY.CALL_PLAN_GENERATED` on the one hash chain, each naming `record_class: SIMULATION`; the chain verifies |
| Separate from operational evidence | see below |

**Simulation records cannot be confused with operational evidence** (`tests/test_survey_simulation.py`):

* every row has `record_class = 'SIMULATION'`, enforced by a CHECK constraint — an insert or update to any other value
  is refused by the database;
* the three tables have foreign keys only to `survey_version`, `survey_definition` and each other, and no table
  outside them refers to them;
* they have no column naming a case, attempt, session, recording, transcript, finding, customer or policy;
* running a simulation and a plan changes the row count of none of the nine operational tables checked
  (`callback_case`, `contact_attempt`, `conversation_session`, `survey_run`, `answer_observation`, `finding`,
  `media_asset`, `transcript_run`, `transcript_segment`);
* rows cannot be updated or deleted (insert-only triggers);
* every response says `record_class: SIMULATION` with a standing note.

## 8. Security evidence

| Check | Result |
|---|---|
| No session | `401` on reads; refused on writes |
| Signed in, no `survey.read` | `403` on all five; an `ACCESS.DENIED_FUNCTION` audit event each |
| Every survey permission, another market | `404` on all five |
| Signed in, no CSRF token | `403` on the three `POST`s |
| After all refused calls | no simulation, input or plan row was written |
| Setting off (the default) | none of the five routes exists; the rest of Survey Studio is unaffected. Simulation alone, without survey definitions, is not on |
| Facts | governed catalog fields only (`422 FACT_UNKNOWN`), scalars only, at most 60 |
| Stale or misplaced input | `409 STALE_SIMULATION`, `409 INPUT_NOT_CURRENT`, `409 SIMULATION_ENDED`; nothing recorded |
| Rate limit | per person, `survey_simulation_inputs_per_minute` |
| Browser storage | none used; the lint rule that forbids it for survey data passes |
| Secrets | none in code, tests, evidence or this report |

Residual risk, stated plainly: `survey.read` is enough to create simulation records, so a reader can add rows (bounded
by the rate limit and 400 inputs per simulation); there is no retention or clean-up of simulation records yet; the
security of these operations was tested, not penetration-tested.

## 9. Verification (the sixteen items of section G)

Evidence: `docs/acceptance/evidence/SS-03B/`. Backend tests ran only against the isolated schema `call360_test`.

| # | Required | Result | Where |
|---|---|---|---|
| 1 | All 82 golden execution runs pass | **82 / 82** | `golden_parity.txt`; `tests/test_survey_execution.py` |
| 2 | All 14 golden call plans pass | **14 / 14** | `golden_parity.txt`; `tests/test_survey_callplan.py` |
| 3 | Identical inputs give identical plans and outcomes | pass | run twice and replayed from recorded inputs for all 82; plans assembled twice with reordered facts; through the API a second simulation has the same run fingerprint and a second plan the same plan fingerprint |
| 4 | Branching and multi-select follow-ups behave correctly | pass | golden F2–F4, G4, G6, H4, J1; cross-engine test |
| 5 | Missing facts remain UNKNOWN | pass | F6, G1, H1, K8; plan test with no facts; browser journey SS-03B.1 and .3 |
| 6 | Invalid answers cannot silently advance | pass | 19 golden rejections; engine and API tests; journey SS-03B.1 |
| 7 | Statements require no answers | pass | K1, K2; engine test |
| 8 | Exact wording remains unchanged | pass | every delivery is a pinned wording; plan and run agree; journey compares the screen with the server's text |
| 9 | No-answer and refusal cases fail closed | pass | `POLICY_UNRESOLVED` engine, API and browser tests (§5) |
| 10 | Execution identities and immutable version pins preserved | pass | K7 (one question, four identities); records store version, content and manifest fingerprints; manifest verified before every run |
| 11 | Simulation records cannot be confused with operational evidence | pass | §7 |
| 12 | Unauthorised access denied | pass | §8; journey SS-03B.5 |
| 13 | All FI-1, FI-2 and LIB-1 full-stack journeys pass | **14 / 14** | `playwright_persisted.txt` (6 + 3 + 5) |
| 14 | All prototype journeys pass | **13 / 13** | `playwright_prototype.txt` |
| 15 | All standard Playwright journeys pass | **33 / 33** | `playwright_standard.txt` |
| 16 | Backend, frontend, type, lint and OpenAPI checks clean | clean | below |

**Full-stack browser tests proving the persisted Simulator uses real Python results: 5 / 5** (`e2e/persisted/ss03b.persisted.ts`;
the persisted suite is 19 / 19 in all). In each, what the screen shows is compared with what the server returned for
that simulation or plan: the sentence, the current question, the refusal code, every module status, the number of
trace lines, every delivered sentence, the terminal state, the plan status and fingerprint. SS-03B.4 hands the browser
engine an altered document and shows the difference panel appear while the screen keeps the server's sentence.

| Check | Result |
|---|---|
| Backend tests | **814 passed, 0 failed** (688 at LIB-1; + 2 legacy-library security, 92 execution, 20 call plan, 12 simulation API) |
| `ruff check`, `ruff format --check`, `mypy` (strict, 107 files) | clean |
| OpenAPI | regenerated and matching: SHA-256 `5799e44faef0bc510a506a8f6033194fe6e84b8e72f08b1f2b533e59baf1bd1f` (was `88baaf2c…`). 221 → 226 operations, 451 → 457 schemas; none removed; no existing schema changed; one existing operation changed in its description only (`openapi_additivity.txt`) |
| Generated files | canonical fixture documents match; Python engine results match (27 files, 82 runs, 14 plans) |
| Frontend unit tests | **612 passed** (513 at LIB-1; + 99: 82 runs and 14 plans across both engines, and 3 on reporting differences) |
| `tsc`, `eslint`, `api:check`, production build | clean |
| Specs validator | pass |
| Migration | head `0029_survey_simulation`; upgrade, downgrade and the 0028 refusal are exercised in the test schema |
| Development database | read-only check after all work: revision `0028_survey_library`, 112 tables, no simulation table, simulation setting off (`dev_database_after_ss03b.txt`) |

Screens (`screens/`): `SIM01` first question on the server · `SIM02` an invalid answer refused · `SIM03` a finished run
with trace and modules · `SIM04` replay identical · `SIM05` a missing fact halts · `SIM06` two customers compared ·
`SIM07` policy unresolved · `SIM08`, `SIM09` the server's call plan · `SIM10` a difference shown. Execution traces and
a call plan as text: `execution_trace_examples.txt`.

One journey failed on its first run because of an error in the new test script (it clicked "Run to the end" after the
run had already ended on that fixture). The script was corrected; no product code changed for it.

## 10. Changed files

Uncommitted, on top of backend `182f6e5`, frontend `9f497d5`, specs `755bf00`.

**Call360-backend**

| File | Change |
|---|---|
| `app/domain/survey/store.py`, `app/api/survey_definitions.py` | LIB-1 security correction: `library()` lists published, market-scoped versions only |
| `app/domain/survey/execution.py` (new) | the execution engine |
| `app/domain/survey/wording.py` (new) | controlled wording values |
| `app/domain/survey/callplan.py` (new) | the call plan |
| `app/domain/survey/simulation.py` (new) | simulation and plan records; replay |
| `app/api/survey_simulations.py` (new) | the five operations |
| `migrations/versions/0029_survey_simulation.py` (new) | three insert-only tables |
| `app/core/settings.py`, `app/main.py`, `app/domain/catalog.py` | the setting; the head rule for three optional revisions; the table catalog |
| `scripts/export_openapi.py`, `contracts/generated/openapi.json`, `.sha256` | the contract |
| `scripts/export_survey_python_results.py` (new) | Python results for the cross-engine test |
| `tests/test_survey_execution.py`, `test_survey_callplan.py`, `test_survey_simulation.py` (new) | 92 + 20 + 12 tests |
| `tests/test_survey_lib1.py`, `test_survey_store.py`, `test_survey_api.py`, `test_admin_access.py` | two security tests; head and contract counts |
| `.env` (gitignored, not in the repository) | `SURVEY_LIBRARY_ENABLED=true` for local development |

**Call360-frontend**

| File | Change |
|---|---|
| `src/features/surveystudio/persist/simApi.ts`, `serverRun.ts`, `ServerSimulation.tsx`, `ServerCallPlan.tsx` (new) | the client, the comparison and trace wording, the two server panels |
| `src/features/surveystudio/persist/serverRun.test.ts` (new) | cross-engine test |
| `src/features/surveystudio/SimulatorPage.tsx`, `CallPlanPage.tsx` | the server / draft switch in persisted mode; nothing changes in the prototype |
| `src/features/surveystudio/model/types.ts`, `sim.ts`, `plan.ts`, `graph.ts` | `policyOf` (§6) |
| `src/styles/survey-studio.css` | styles for the server panels (appended) |
| `src/api/generated/schema.d.ts`, `openapi.pinned.json`, `contract.lock.json` | regenerated client |
| `playwright.persisted.config.ts`, `e2e/persisted/ss03b.persisted.ts` (new) | simulation on in the persisted test server; five journeys |

Not touched: `src/features/scripts/*`, `src/styles/app.css`, `BuilderPage.tsx`, `ComposerPage.tsx`, `GraphView.tsx`,
the standard and prototype journeys.

**Call360-specs**

| File | Change |
|---|---|
| `docs/plans/survey-studio/32_SS-03B_IMPLEMENTATION_REPORT.md` (new) | this report |
| `docs/plans/survey-studio/04_SS-01_CANONICAL_CONTRACTS.md` | §13 |
| `docs/plans/survey-studio/06_SS-01_DECISION_REGISTER.md` | D-222…D-233 |
| `docs/plans/survey-studio/README.md`, `docs/plans/SESSION_HANDOFF.md` | index and handoff |
| `docs/plans/survey-studio/python-results/` (new, generated) | 27 files |
| `docs/acceptance/evidence/SS-03B/` (new) | evidence |

No file under `docs/plans/survey-studio/fixtures/` or `canonical-documents/` changed.

**Outside the repositories:** `_db_backups/call360_dev_before_0028_20261122.dump` and the extended
`_db_backups/RESTORE.md`; the development database at `0028`.

## 11. Known limitations and unresolved decisions

**Carried from LIB-1 (D-222), unchanged:** imported standalone assets that are not placed do not persist; no separate
category or purpose filter controls; some condition previews show stored rule syntax; evaluation and control metadata
are not part of reusable assets.

**SS-03B limitations.**

1. **The development database is at `0028`, not `0029`.** Simulation is therefore off in development and the new
   screens show "not available on this server" there. Enabling it needs the owner's approval of migration `0029` on
   development (additive; three tables) and `SURVEY_SIMULATION_ENABLED=true` in the local `.env`.
2. **Published versions cannot contain wording variables today** (default-deny on spoken fields), so on the server the
   value-rendering paths are proven by the golden fixtures and unit tests, not yet by a published survey. In the API
   and browser tests the one variable of fixture K8 is replaced by plain words to make it publishable, as LIB-1 did.
3. **The server simulates published versions only.** An unsaved or unpublished draft is previewed by the browser
   engine, labelled as a preview. Server simulation of a draft would be a further, additive step.
4. **"Step" and "Run to the end" give the ordinary answer** (yes; the first plain option; a short remark; a number
   within the limits; acknowledged). The scripted answers of the prototype's synthetic customers are keyed by the
   prototype's question codes and do not apply to server-issued codes; the customer's *facts* do apply.
5. **The trace shows codes** for outcomes, options and steps (for example `ESCALATE`, `n2`), not business labels, and
   a multi-select follow-up queue shows step identifiers.
6. **No retention policy** for simulation records; no list of past simulations in the screen.
7. **Screens verified in Chromium at 1440 px** by automated journeys; no business-user or screen-reader review.
8. **Not my change:** in `Call360-specs`, `docs/acceptance/evidence/LIB-1/screens.zip` is deleted and a `.DS_Store`
   is modified in the working tree. I did not make or revert either.

**Unresolved, and deliberately not decided here.** D-NA-1…D-NA-17 (silence, refusal, repeats, timeouts, optional
blanks, consent refusal); which fields may be spoken; approval of any wording; live-call eligibility and the gates
G-1…G-8; assignment of surveys to cases; outcome codes for non-answers.

**Choices I made that the owner may want to revise (D-233):** `survey.read` as the permission; migration `0029` and
`survey_simulation_enabled`; storing inputs and replaying rather than storing runs; the API checking only the shape of
an answer; keeping the browser preview for drafts; exporting Python results to `python-results/`.

## 12. What is proposed next — not authorised

Nothing follows automatically. Candidates for the owner to choose from: (a) accept SS-03B and authorise commits;
(b) migration `0029` on development; (c) the no-answer decisions D-NA-1…17, which gate any further execution work;
(d) server simulation of drafts; (e) the LIB-1 UX limitations.
