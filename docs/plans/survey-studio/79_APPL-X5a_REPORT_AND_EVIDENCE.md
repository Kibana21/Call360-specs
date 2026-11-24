# 79 — APPL-X5a report and evidence

**Built and verified on the isolated test schema, 2026-11-24/25. Awaiting owner acceptance. Nothing committed.**
Synthetic data only; simulation only. Local development is untouched: still at `0041_applicability_publication`, no
APPL-X5a table, the journeys setting off, no journey route served (checked, §13).
Design decision written first: `77_…`. Architecture and contracts: `78_…`. APPL-X5b assessment: `80_…`.

---

## 1. The final success criterion, part by part

| The owner's criterion | Shown by |
|---|---|
| A business user selects a genuinely published policy version | X5a.1: chosen explicitly on the screen; fingerprints equal the governance record. The **actual** accepted `GOV-DEMO-ILP-NFTF` version 1 in development selects correctly through the same code, read-only (§3) |
| supplies synthetic facts | X5a.1–7: typed, with "not known" and "not provided" as first-class choices; copy from a saved scenario available |
| obtains the exact applicable published surveys | X5a.1–5: selected surveys in order with the requirement that selects each, pending surveys, facts needed, replacements named |
| completes them in one coordinated browser journey | X5a.1 (one survey), X5a.2 (two, in order), X5a.3 (replacement), X5a.4 (shared delivery), X5a.7 (three, with survey facts) |
| the runtime enforces order, branching, allowed answers, non-answers and cross-survey continuation | X5a.6, X5a.7, X5a.8; backend runtime test |
| the journey survives browser closure and reopens at the correct next question | X5a.7: context closed, new sign-in, same item key and input count |
| selection and execution reproducible from frozen records | `verify` in every journey; backend `verify` checks |
| no legacy selection object or operational record created or modified | backend negative test: only the journey's own tables, its own new simulations and the audit trail change |
| a clean, stable, voice-neutral turn API for VOICE-0 | `78_…` §5; backend runtime test with interaction evidence |

## 2. What was built

- **Backend:** migration `0042_applicability_journey`; `app/domain/survey/applicability/journeys.py`;
  `app/api/applicability_journeys.py` (16 operations); setting `applicability_journeys_enabled`;
  `tests/test_applicability_journeys.py` (10 tests).
- **Not changed:** the evaluator (`logic.py`, `evaluator.py`, `analysis.py`), `policies.py`, `publication.py`,
  `scenarios.py`, the execution engine (`execution.py`), the simulation service (`simulation.py`), the legacy
  coordinator, `rule_engine.py`, `answer_evaluation.py`, `finding_engine.py`. The journey service **calls** the
  evaluator, the publication reader and the simulation service; it edits none of them.
- **Frontend:** `journeyApi.ts`, `Journeys.tsx` (list, new journey, journey page); "Run a journey" in the
  applicability navigation; setting `VITE_APPLICABILITY_JOURNEYS`; Playwright configuration
  `playwright.journeys.config.ts` with `e2e/journeys/journey.jny.ts` (10 journeys).
- **Test identity (D-478):** one line in `scripts/e2e_survey_setup.py`.
- **OpenAPI:** 16 operations and 26 schemas added; nothing removed or changed.

## 3. Real published-policy and survey-version evidence

**The accepted artefact itself, in development, read-only** (`evidence/APPL-X5a/dev-real-version-selection.txt`).
The session was opened read-only; development has no journey table and the setting is off; nothing was written.

| | |
|---|---|
| Policy version | `GOV-DEMO-ILP-NFTF` version 1, `PUBLISHED`; version `8168c61ea62e…`, document `3699c75082aa…`, manifest `a9b917405086…` — the fingerprints of the acceptance record (`75_…` §9), verified against itself before selecting |
| ILP only | selected: Survey A v1 |
| ILP replacement sale | selected: Survey A v1, then Survey D v1 |
| ILP with NFTF | selected: Survey C v1; `r1` and `r2` replaced |
| neither | no survey required |
| NFTF not known | unresolved; A, B and C pending; needs `nftf` |

**The browser journeys** run on the test schema, where a policy of the same code and the same four requirements is
published through the governed three-person API, over the same five showcase surveys published there through Survey
Studio's governed API. Its identifiers and fingerprints are the test schema's own, not development's — migration
`0042` is not authorised for development, so a recorded journey cannot exist there.

## 4. Journeys A–J (real browser, real backend, test database)

| Journey | Test | Result |
|---|---|---|
| A published policy selection | X5a.1 | pass |
| B single-survey execution | X5a.1 | pass |
| C multiple-survey coordination | X5a.2 | pass |
| D explicit replacement | X5a.3 | pass |
| E shared delivery | X5a.4 | pass |
| F unresolved selection | X5a.5 | pass |
| G incomplete survey | X5a.6, X5a.7 | pass |
| H resume and replay | X5a.7 | pass |
| I invalid and concurrent answers | X5a.8 | pass |
| J no legacy dependency | backend tests; existing suites in §14 | pass |
| superseded version; read-only person; the runner's limits | X5a.9 | pass |
| four widths, keyboard, accessibility | X5a.10 | pass |

Screens: `docs/acceptance/evidence/APPL-X5a/screens/` (`01`–`23` follow the journeys; `30-*` the four widths).

### 4.1 What each shows

- **A, B.** Nothing is preselected: no version, no fact, no preview. With the version chosen and no fact given the
  selection is *unresolved* and names the facts it needs. With ILP, NFTF no, replacement no: "These surveys apply, in
  this order" — Survey A, "Required by ILP needs Survey A", version 1. The recorded journey carries source
  `APPLICABILITY`, class `SYNTHETIC`, and the version's three fingerprints; its one step is Survey A at its pinned
  version id and content fingerprint. The survey reads no survey fact, and the page says so. The first question shows
  the approved wording, "delivered exactly as written", its place ("Survey 1 of 1 · … · question 1"), and Record is
  disabled until something is chosen. Walked through yes/no and free text to "All surveys completed"; `r1`
  satisfied; three answers listed; verified.
- **C.** The facts are **copied by value from a saved scenario** (`GOV-DEMO-ILP-NFTF-REPLACEMENT`), not typed; the
  journey records that origin with the scenario's revision. ILP replacement sale → Survey A then Survey D, in that order. While A runs, D is `WAITING` with no
  simulation. D begins only when A is `COMPLETED`. History: step 1 started, ended; step 2 started, ended. D asks a
  multi-select question.
- **D.** ILP with NFTF → Survey C alone. The selection says "ILP needs Survey A is replaced by ILP with NFTF needs
  Survey C — A … is not run", likewise B. The journey has one step; `r1`, `r2` are `REPLACED` / not required; `r3`
  satisfied.
- **E.** A published policy with a declared shared delivery: one selected entry, "one delivery fulfils each of
  them"; one step with `required_by = [r1, r2]`, 2 obligations; one `STEP_STARTED`; both requirements satisfied by
  step 1 and marked "shared delivery".
- **F.** NFTF "Not known": unresolved; three surveys pending; "NFTF applies" named as needed. Recorded as
  `SELECTION_UNRESOLVED`: no step, no start control, start refused by the API (`NOT_READY`); it still verifies.
- **G.** With A and D selected, the understanding check of Survey A is answered "No": the survey ends with outcome
  `CLARIFICATION_REQUIRED` (`ENDED_WITH_OUTCOME`). The journey is `CROSS_SURVEY_POLICY_UNRESOLVED`: "No governed rule
  says whether the remaining surveys follow, so none was started"; D is `WAITING` with no simulation; the engine's
  exact terminal object is in the journey's end detail; both requirements not satisfied, each with its own reason.
  Separately (X5a.7), a survey fact marked "not known" stops a survey at the module that needs it
  (`MISSING_INFORMATION_HALT`, `ELIGIBILITY_UNKNOWN` at `mi-high-value`) — the **survey's own** governed rule — and
  again nothing follows.
- **H.** Three surveys: one that reads survey facts, one of numbers, one acknowledgement. The survey-facts step says
  3 facts are missing and Start is disabled; nothing is applied by default. The person **chooses** the
  correspondence: `replacement → policy.is_replacement` "carried over: no". A different typed value is a conflict
  ("Nothing is replaced") and Start stays disabled until it is undone. Age typed; premium typed. After start the
  frozen record shows each fact's origin (`CORRESPONDENCE`, `TYPED`). In the numbers survey `0` is refused
  (`NUMBER_TOO_LOW`) and `2.5` (`NUMBER_NOT_WHOLE`); the same question stays, attempt 1 then 2. **The browser context
  is closed; a new browser signs in; the journey opens at the same item key with the same input count**, Survey 1
  shown completed, the accepted answer listed and the two refused ones counted. "Not acknowledged" is recorded and
  the page says the business has not decided what follows; nothing is assumed; acknowledging completes the journey.
  Verified, including the survey facts reproduced from the frozen correspondence.
- **I.** Thirteen refusals from the signed-in session, none advancing the journey (§6), then two browser sessions on
  one journey: the second, a moment stale, is told so and shown the current question. Exactly one answer per
  question is on record; the refusals are in the history. A too-wide multi-select and a duplicated option are refused.
  The journey is abandoned with a reason and stays readable.
- **Superseded.** Version 2 is published; version 1 shows "superseded". Choosing it shows "Version 1 is superseded.
  Version 2 is the published one … it is never upgraded"; Record is disabled, and the API refuses
  (`SUPERSEDED_NOT_CONFIRMED`), until the explicit confirmation. The journey records version 1, superseded, current 2.

## 5. Question and answer validation

| Answer type | Exercised in | Rejections shown |
|---|---|---|
| YES_NO | browser A, C, D; backend | `UNKNOWN_OPTION`, `CHOICE_REQUIRED` |
| SINGLE_SELECT | browser D (Survey C) | — |
| MULTI_SELECT | browser C, D, I | `UNKNOWN_OPTION`, `DUPLICATE_OPTION` |
| FREE_TEXT | browser A, C | — |
| NUMERIC | browser H; backend | `NUMBER_TOO_LOW`, `NUMBER_TOO_HIGH`, `NUMBER_NOT_WHOLE`, `NUMBER_REQUIRED` |
| ACKNOWLEDGEMENT | browser H; backend | `NON_ANSWER_POLICY_UNRESOLVED` (not acknowledged) |
| STATEMENT | delivered by the engine within every showcase survey; takes no turn | — |

A rejected answer is recorded as refused, with its code; the same question stays current with the attempt number
raised. `other_text` is supported by the runtime and the screen (the turn says which option takes it); **no published
synthetic survey in the test data has such an option, so it was not exercised end to end**. `TOO_MANY_SELECTED` is the
engine's own and is covered by the accepted engine tests; the journeys here exercised unknown and duplicated options.

## 6. Refusals that never advance a journey (X5a.8 and backend)

| Attempt | Answer |
|---|---|
| an option that does not exist | `UNKNOWN_OPTION` |
| a stale input count | `409 STALE_TURN` |
| a stale item key · a question of the next survey · skipping ahead | `409 INPUT_NOT_CURRENT` |
| a non-answer the question does not allow | `NON_ANSWER_NOT_ALLOWED` |
| no CSRF token | `403` |
| a person without `survey.simulate` | `403` |
| a policy version that does not exist · a working draft id | `404` |
| a fact the version does not read · an invalid value | `FACT_UNKNOWN` · `FACT_INVALID` |
| the same idempotency key and request | the first result, `replayed: true`, nothing recorded again |
| the same key, another answer | `409 IDEMPOTENCY_KEY_REUSED` |
| two sessions answering the same turn | one accepted; the other `409 STALE_TURN` |
| any answer after the journey ended | `409 JOURNEY_NOT_RUNNING` |
| a survey reference that no longer resolves (service level) | `SURVEY_VERSION_INVALID` |
| another market | `404` on every journey operation; empty lists |

Each `409` is also written to the journey's history as `SUBMISSION_REFUSED`.

## 7. Resume and replay

- Accepted answers are immutable `survey_simulation_input` rows; the browser holds nothing; state is the replay.
- Resume shown in the browser (X5a.7) and in the backend test (a second session continues the journey).
- `verify` reproduces selection, survey facts and every survey from the records (`78_…` §7): true for completed,
  unresolved, incomplete and abandoned journeys alike.

## 8. Shared delivery and cross-survey behaviour

| Case | Result |
|---|---|
| shared survey completed | one simulation; every requirement `SATISFIED`, same step |
| shared survey not completed | every requirement `NOT_SATISFIED`; none half-counted |
| a survey ends other than completed, others waiting | `CROSS_SURVEY_POLICY_UNRESOLVED`; the others never start; exact terminal kept |
| the last survey ends other than completed | `ENDED_INCOMPLETE` |
| a non-answer with no decided handling | the question stays open; `POLICY_UNRESOLVED`; nothing assumed |

No continuation, skip, retry or escalation rule exists anywhere in the coordinator.

## 9. Fact correspondence (`77_…`)

Backend test `test_fact_correspondence_is_identity_only_exact_and_frozen_in_the_journey` and browser X5a.7:

- refused: a rule other than `IDENTITY`; different types; an unknown field; a name instead of a version id; an
  unpublished or unknown source; a definition that differs on either side; a repeated target; an empty document;
- saved versions are immutable (UPDATE and DELETE refused by the database); a change is a new numbered version;
- nothing applies unless the person chooses it; a carried known value is never replaced — a different typed value is
  a conflict, and a typed "not known" does not erase it;
- an entry whose source is another version of the fact than the policy pins does not apply
  (`SOURCE_DEFINITION_DIFFERS`), and the fact is then required in the Survey Facts editor;
- the journey freezes the whole document and each field's origin; verification reproduces the survey facts;
- the published policy version and its manifest are untouched by any of it, and still verify.

## 10. Security and market isolation

- **Each of the three permissions is necessary** (backend): a person missing any one of `applicability.read`,
  `survey.read`, `survey.simulate` cannot create a journey; a person missing `survey.simulate` cannot start, answer
  or abandon one, and reads everything.
- **The journey runner holds exactly its three permissions** (browser X5a.9 and backend): saving a policy, saving a
  correspondence, submitting, approving, publishing and evaluating are all `403`.
- **The test identity** exists only in the test setup script; neither development identity script knows it; the
  setup refuses any configuration but the test one (tested); no existing test role's permissions changed (asserted).
- Another market: nothing listed, everything `404`. CSRF on every write. Real-looking data refused in facts and labels.

## 11. Database integrity

- **Migration `0042`** (`test_zz_migration_0042_…`), on a schema with a published library, published surveys and a
  published policy version: exactly 5 tables and 5 functions; 10 validated foreign keys; still 4 applicability
  permissions; downgrade while empty removes exactly those and changes nothing else; a forced failure at the last
  statement leaves nothing behind; upgrade again is identical; with a recorded selection the downgrade is refused;
  the audit chain verifies.
- **Guards, tried directly:** changing or deleting a selection plan, its source, a journey's identity, its status
  out of order, a step's survey, a step's outcome out of order, an event; deleting any of them; changing or deleting
  a correspondence version; rewriting a recorded simulation input — all refused.
- **No legacy or operational effect** (`test_nothing_legacy_or_operational_…`): across a complete three-survey
  journey, the only tables that change outside the journey's own are `survey_simulation`,
  `survey_simulation_input` (the journey's new, labelled, step-referenced simulations) and `audit_event`. Every
  assignment, composite, coordinated, binding, group, script, case, callback, conversation, evaluation, assurance
  and finding table is byte-identical. A simulation that existed before is byte-identical. The journey tables'
  foreign keys reach only applicability, survey-definition, survey-version and simulation tables. The journey service
  imports no assignment, coordination, rule-engine, evaluation, assurance, finding, question-controller or voice
  module.
- **Stated references added to the older isolation tests** (they list every permitted reference explicitly):
  `applicability_journey_step → survey_definition`, `→ survey_version`, `→ survey_simulation`.

## 12. Defects found and fixed while building

| Found by | Defect | Fix |
|---|---|---|
| contract export | I applied the CSRF marker as a dependency instead of as the decorator the codebase uses | corrected on all eight write operations |
| first backend run | a turn field typed as text was a yes/no flag | corrected in the schema |
| browser X5a.7 | after a conflicting survey fact was typed, the "Carried over" choice disappeared, so the conflict could not be undone on the screen | the carried value stays on offer |
| browser X5a.8 | the "this journey moved on elsewhere" notice vanished when the page re-read the journey | the notice is kept by the page |
| browser X5a.10 | a scrollable table could not take keyboard focus at phone width | made a focusable, named region |
| screenshot | the policy-authoring header ("Draft · saved", undo, redo, another policy's name) showed beside a journey of a published version | hidden on journey routes only |
| my own review | the browser guessed which option takes free text from its code | the server's turn now says so for every option |
| older tests | four tests that list every table and every permitted cross-reference needed the new ones stated | stated, with the reason |

## 13. Development — untouched

Revision `0041_applicability_publication`; 0 APPL-X5a tables; `applicability_journeys_enabled` false;
`/health/ready` 200; `/api/v1/applicability/journeys` 404. No identity, role, grant or membership created or changed.
The only access to development in this checkpoint was read-only (§3 and one earlier read of the catalogue and the
published version's shape).

## 14. Regression

One run, on the final source, 2026-11-25. Test schema; the browser suites one at a time.

| Check | Result |
|---|---|
| Backend suite — includes the published-policy verification tests, the evaluator tests, the single-survey execution and simulation tests, the legacy coordinator tests (unchanged), security and market-isolation tests, every migration test, the golden 82 survey runs and 14 plans | **1106 passed**, 0 failed |
| ruff · ruff format · mypy (142 files) | clean |
| OpenAPI | regeneration changes nothing; SHA-256 `6a643d9dfd1591899b15a6d3cf1e463bcace22574198c7a751fe92121aa7444f` |
| Frontend contract check · lint · types · unit (636) · production build | pass |
| Playwright journeys (APPL-X5a, new) | 10 passed |
| Playwright publication (APPL-X4b) | 7 passed |
| Playwright scenarios (APPL-X4a) | 11 passed |
| Playwright applicability | 26 passed |
| Playwright persisted | 34 passed |
| Playwright prototype | 13 passed |
| Playwright standard | 34 passed |
| Specs validator | pass |
| Golden fixtures and expectations | no file changed |
| Evaluator, `policies.py`, execution engine, simulation service, legacy coordinator, `rule_engine.py`, `answer_evaluation.py`, `finding_engine.py`, `question_controller.py` | not modified by this checkpoint |

- **Older tests adjusted, no behavioural assertion weakened:** the pinned migration head and operation and schema
  counts; the "each setting demands its own migration" chain (one revision longer, with three new assertions for
  journeys); the four older applicability migration tests, for the revision now above them; and four tests that list
  every table and every permitted cross-reference, where the new tables and the three new references are stated
  (§11).
- **X3.8 (canvas of 100 on screen):** passed in this run. It failed once on 2026-11-24 with no change to that
  screen. Still **under watch, not closed**.
- **Voice Studio timing defect:** open; the voice tests passing here does not close it.
- No timeout raised; no golden expectation changed.
- Logs: `docs/acceptance/evidence/APPL-X5a/test-output/`.

## 15. Not done, not measured, not claimed

- Migration `0042` on development; any journey in development.
- APPL-X5b: evaluation, findings, assurance, trace (`80_…`).
- `other_text` end to end; a date answer; question-level sharing; any continuation rule.
- Usability with people; screen-reader testing; WCAG conformance. The accessibility checks are automated scans and
  keyboard walks.
- Voice of any kind. The runtime carries no audio, provider or transport.
