# 78 — APPL-X5a: coordinated published-survey execution and the voice-neutral runtime — architecture and contracts

**As built on the isolated test schema.** Date 2026-11-24/25. Synthetic data only; simulation only.
**Authorisation:** the owner's "APPL-X5a — Coordinated Published-Survey Execution and Voice-Neutral Runtime
Foundation": implementation **on the isolated test schema only**. Not authorised: migration `0042` on development,
APPL-X5b, APP-1a, OPS-1, VOICE-0, VOICE-1, Genesys, designer integration steps 2–4, legacy retirement, commits.
Fact-correspondence design decision, written first: `77_…`. Readiness assessment this builds on: `76_…`.

Nothing in this checkpoint selects a survey for a real case, plans a callback, starts a session, or reads or writes an
assignment rule, a survey binding, a requirement group or a composite plan.

---

## 1. Decisions recorded with this checkpoint

| Ref | Decision |
|---|---|
| D-469 | APPL-X4b development enablement **accepted** as technically verified; baseline `0041_applicability_publication`; `GOV-DEMO-ILP-NFTF` version 1 is the accepted governance demonstration artefact |
| D-470 | APPL-X5 split: **X5a** selection, coordinated execution, browser journey, resume and replay, immutable evidence, voice-neutral runtime; **X5b** evaluation, findings, control-policy evaluation, assurance, trace (Q-8) |
| D-471 | Q-1: a **separate applicability journey** beside the legacy coordinator; no legacy foreign key relaxed; no synthetic legacy object created; the accepted single-survey execution and simulation services reused |
| D-472 | Q-2: an explicit synthetic journey against a **superseded** version is allowed with its status, number, the current version and a confirmation shown; never chosen or upgraded silently |
| D-473 | Q-3: a survey ending other than `COMPLETED` never advances; `CROSS_SURVEY_POLICY_UNRESOLVED` where no governed rule exists; the exact terminal reason kept; no skip, retry or escalation invented |
| D-474 | Q-4: two fact vocabularies kept explicit; a small versioned declarative **fact correspondence** — `77_…` |
| D-475 | Q-5: sharing individual questions between surveys is out of scope; a declared shared delivery of a whole survey is in scope |
| D-476 | Q-6: `survey_journey_evaluation` and `survey_execution_assurance` are **not** modified in X5a; the minimal additive X5b design is in `80_…` |
| D-477 | Q-7: existing permissions only — `applicability.read`, `survey.read`, `survey.simulate` to run; evaluation permissions reserved for X5b; no new role or grant in development |
| D-478 | Test identity: one **test-schema-only** identity `e2e.survey.journey` with exactly those three permissions, created by the test setup script alone; no existing role widened (owner-approved after I reported that no test identity held the combination) |

## 2. Migration `0042_applicability_journey` (parent `0041_applicability_publication`)

Additive: five tables, five guard functions, **no permission**, **no existing object altered**. Ten validated foreign
keys, to `applicability_policy`, `applicability_policy_version`, `survey_definition`, `survey_version`,
`survey_simulation` and to its own tables — and to nothing else.

| Table | Holds | Integrity |
|---|---|---|
| `applicability_fact_correspondence` | an immutable, numbered, synthetic declaration (`77_…`) | unique (market, code, number); insert only |
| `applicability_selection_plan` | one selection: policy version id, its three fingerprints, the fact snapshot and its fingerprint, the profiles, the evaluator contract, the complete plan and its fingerprint, the outcome, the origin of the facts | `selection_source` CHECK = `APPLICABILITY`; `record_class` CHECK = `SYNTHETIC`; guard on insert: the version exists exactly as recorded (policy, market, number, fingerprints); never updated or deleted |
| `applicability_journey` | one journey over one plan (unique): status, revision, and — written once, at start — the correspondence used, the start record, the survey facts and their fingerprints | guard on insert: same market and version as its plan, and **the status the plan's outcome allows** (only a resolved selection with surveys is `READY`); on update: identity frozen, one revision at a time, only the allowed transitions, start fields written exactly once; never deleted |
| `applicability_journey_step` | one selected survey at its position: exact version and fingerprints, the requirements it fulfils, obligations, and — once started — its one simulation | unique (journey, position) and **unique (journey, survey)** — a survey is executed at most once per journey; guard: a step is of the journey's market; its simulation must be of exactly its pinned version and fingerprints; `WAITING → RUNNING → ENDED` only; outcome written once; never deleted |
| `applicability_journey_event` | append-only coordination history, with the idempotency key and request fingerprint of a submission | unique (journey, idempotency key); UPDATE / DELETE refused |

Downgrade refuses while a selection plan or a correspondence exists. Used only when `applicability_journeys_enabled`
is on (which requires publication **and** survey simulation). `MIGRATION_HEAD` is `0042`; a schema at `0041` is
accepted while the setting is off — the state of local development.

**Expected writes to accepted tables:** a journey creates new rows in `survey_simulation` and
`survey_simulation_input` through the accepted simulation service — one simulation per selected survey, labelled
"Applicability journey ‹id› · step ‹n› · ‹survey›" and referenced by its step. Rows that existed before are never
touched (those tables' own guards refuse it; a test proves an older simulation is byte-identical afterwards).

## 3. Authoritative selection

- The person names **one `applicability_policy_version` id**. A working draft id is not found. Nothing resolves "the
  latest".
- The version is **verified against itself** (`verify_version`) before anything is selected; an unverifiable version
  selects nothing (`VERSION_NOT_VERIFIED`).
- Read from the version alone: its frozen document, its frozen manifest with the definitions of every variable,
  profile and condition, its exact survey references and fingerprints.
- Application facts are checked against the **frozen variable definitions**: an unknown fact, a derived fact, or a
  value invalid under its definition is refused (`FACT_UNKNOWN`, `FACT_DERIVED`, `FACT_INVALID`); text that looks
  like real data is refused (`LOOKS_LIKE_REAL_DATA`). `null` is "not known"; absent is "not provided".
- The plan is the accepted evaluator's, called through the existing frozen path. **No other selection logic exists**
  in this checkpoint.

| Plan | Outcome | Journey status | Execution |
|---|---|---|---|
| resolved, surveys selected | `SURVEYS_SELECTED` | `READY` | may begin |
| resolved, none selected | `NO_SURVEY_REQUIRED` | `NO_SURVEY_REQUIRED` | none; recorded |
| something pending | `UNRESOLVED` | `SELECTION_UNRESOLVED` | none; the pending surveys and the facts needed are shown |
| out of scope | `OUT_OF_SCOPE` | `OUT_OF_SCOPE` | none |
| scope undecided | `SCOPE_UNRESOLVED` | `SCOPE_UNRESOLVED` | none |

Not known never becomes false: with `nftf` not known, the surveys that depend on it are **pending**, the fact is
named, and no survey — not even one that is definitely required — is started.

`POST /journeys/selection-preview` returns the same plan and records nothing.

## 4. The coordinator (`journeys.py`) — thin by construction

- Steps are the plan's `selected` entries in `position` order, created with the journey: exact version, fingerprints,
  `required_by`, obligations. Before a step is created, and again before it starts, the survey version must still
  resolve to exactly what the policy version pinned (`SURVEY_VERSION_INVALID`); nothing is substituted or upgraded.
- **Start** freezes the survey facts (§6) and creates the first step's simulation with the accepted
  `simulation.create`.
- **After every accepted or rejected input** the coordinator looks at the current simulation. If it has ended:
  the step's outcome and terminal detail are recorded; then
  - `COMPLETED` and a step is waiting → that step starts;
  - `COMPLETED` and none is waiting → `ALL_SURVEYS_COMPLETED`;
  - anything else and a step is waiting → **`CROSS_SURVEY_POLICY_UNRESOLVED`**; the waiting steps stay unstarted;
  - anything else on the last step → `ENDED_INCOMPLETE`.
  The journey's `end_detail` keeps the step, the survey, the exact terminal object of the engine and the surveys not
  started.
- A survey never executes twice; an unselected survey has no step and therefore no simulation; a replaced
  requirement's survey is simply not in `selected`.
- **Shared delivery:** one step with several `required_by`. Completed → every one of them `SATISFIED`; otherwise
  every one `NOT_SATISFIED`. Nothing is shared at question level.
- A non-answer whose handling is undecided (`acknowledged = false`) leaves the survey — and so the journey — open
  with `condition = POLICY_UNRESOLVED`. Nothing is assumed; the question stays current.
- `REPLAY_DRIFT` of any step's simulation is reported as the journey's `condition`; the runtime offers no turn.

Journey statuses stored: `READY`, `RUNNING`, `ALL_SURVEYS_COMPLETED`, `CROSS_SURVEY_POLICY_UNRESOLVED`,
`ENDED_INCOMPLETE`, `ABANDONED`, and the four selection outcomes. Conditions derived on read: `POLICY_UNRESOLVED`,
`REPLAY_DRIFT`.

## 5. The voice-neutral runtime contract (`call360.applicability-journey-runtime/1`)

| Contract | Operation |
|---|---|
| `next(journey) → Turn | End` | `GET /journeys/{id}/turn` |
| `submit(journey, item_key, expected_inputs, answer, idempotency_key) → Accepted | Rejected` | `POST /journeys/{id}/answers` |
| `state(journey) → JourneyState` | `GET /journeys/{id}` |
| `verify(journey) → VerificationResult` | `POST /journeys/{id}/verify` |

**Turn**

| Field | Meaning |
|---|---|
| `journey_id`, `step`, `steps` | identities and position |
| `survey` | code, name, version number and label, version id, content fingerprint |
| `item_key` | the identity of this turn (`‹step›:‹module instance›/‹node›`) |
| `item`, `module`, `question_no`, `attempt` | the item and its wording version; where it is; how many times it was asked |
| `prompt.text` | the approved wording as the engine rendered it; never rewritten by a client |
| `prompt.delivery_mode`, `prompt.exact_wording_required` | `CONTROLLED_TTS` / `EXACT_AUDIO` require exact wording |
| `expects.answer_type` | `YES_NO`, `SINGLE_SELECT`, `MULTI_SELECT`, `FREE_TEXT`, `NUMERIC`, `ACKNOWLEDGEMENT` (a `STATEMENT` is delivered by the engine and takes no turn) |
| `expects.options[]` | `code`, `label`, `is_other`, `exclusive`, `other_text` rule |
| `expects.selection`, `number_rule`, `text_rule` | multi-select limits; numeric and free-text validation |
| `allowed_non_answers[]` | exactly the non-answers the engine distinguishes for this question: `NOT_ACKNOWLEDGED`, `EMPTY_TEXT` (optional text), `NONE_SELECTED` (a multi-select with minimum 0) |
| `policy_unresolved` | set when the last response was a non-answer with no decided handling |
| `expected_inputs`, `turn_token` | the concurrency token: the number of inputs the journey holds; the journey revision |

**Submit.** `answer` is `{choice | choices | text | other_text | number | acknowledged}` or `{non_answer: kind}`.

| Situation | Result |
|---|---|
| valid for the current turn | `ACCEPTED`; persisted before anything advances |
| the engine rejects it (wrong option, too many, bad number …) | `REJECTED` with the engine's stable code; recorded as a refused input; the same turn stays, `attempt` + 1 |
| a non-answer the turn does not allow | `REJECTED`, `NON_ANSWER_NOT_ALLOWED`; recorded; not given to the engine |
| `expected_inputs` is not the journey's | `409 STALE_TURN`; nothing advances; the refusal is recorded |
| `item_key` is not the current turn — another question, another survey, a later one | `409 INPUT_NOT_CURRENT`; recorded |
| the journey is not running | `409 JOURNEY_NOT_RUNNING`; recorded |
| the same idempotency key and the same request again | the first result, `replayed: true`; nothing recorded again |
| the same key with a different request | `409 IDEMPOTENCY_KEY_REUSED` |
| not an answer object | `422` |

The server decides the next question. A client never decides eligibility, branch, order, replacement or completion.

**Future voice compatibility.** A submission may carry `interaction`: `transcript_ref`, `recognition_confidence`,
`proposed_answer`, `clarification_required`, `delivery_evidence_ref`. It is stored with the submission's event as
**proposed interaction evidence**; the accepted answer is only ever the one the engine validated.
`clarification_required: true` records a refused submission (`CLARIFICATION_REQUIRED`) and leaves the turn current.
There is no speech streaming, speech-to-text, text-to-speech, prompt or telephony in this checkpoint.

## 6. Application facts and survey facts

As decided in `77_…` and implemented without deviation:

- `POST /journeys/{id}/survey-facts` shows, for a chosen correspondence (or none) and the typed facts: every entry and
  whether it applies and why not; every survey field a selected survey **reads** (from the accepted call-plan
  analysis of each pinned survey), its value and origin; what is missing; any conflict. It records nothing.
- `POST /journeys/{id}/start` refuses `SURVEY_FACTS_REQUIRED` and `SURVEY_FACT_CONFLICT`, and otherwise freezes the
  start record: correspondence document, entries, per-field origin (`CORRESPONDENCE`, `TYPED`, `MARKED_NOT_KNOWN`),
  the typed input, the survey fact snapshot and its fingerprint.
- The one survey fact snapshot is given to every simulation of the journey.

## 7. Persistence, resume, replay, verification

- An accepted answer is an immutable `survey_simulation_input` row, written in the same transaction as the
  coordination event and the journey's revision. The browser holds nothing.
- State is always the replay of the recorded inputs by the accepted engine. A new sign-in reconstructs the journey.
- **`verify`** reproduces the journey from its records and writes nothing:

| Check | What is reproduced |
|---|---|
| `POLICY_VERSION` | the published version verifies against itself and is the one the selection recorded |
| `FACT_SNAPSHOT` | the application facts match their fingerprint |
| `SELECTION_REPRODUCED` | evaluating the recorded facts against the immutable version gives exactly the recorded plan |
| `STEPS_ARE_THE_SELECTION` | the steps are the selected surveys: same versions, order and requirements; nothing added or left out |
| `START_RECORD`, `CORRESPONDENCE_FROZEN`, `SURVEY_FACTS_REPRODUCED` | re-applying the frozen correspondence and typed facts gives exactly the survey facts used |
| `SURVEY_REPRODUCED` (per step) | the simulation replays from its inputs to the recorded result, at the pinned version, with the journey's survey facts |
| `STEP_OUTCOME` (per ended step) | the recorded outcome is what the replay ends as |
| `HISTORY_CONSISTENT` | one history entry per recorded input |
| `COORDINATION` | a survey started only after every earlier one completed, in order |
| `COMPLETION` | for a completed journey, every selected survey completed |

The selection is re-evaluated from `applicability_policy_version`, which is immutable and whose fingerprints are
checked against the plan's; the library is not consulted for what a definition is.

## 8. Operations (16, under `/api/v1/applicability`)

| Operation | Needs (besides `survey.read`) |
|---|---|
| `GET /journey-policy-versions` · `GET /journey-policy-versions/{id}` | `applicability.read` |
| `POST /journeys/selection-preview` | `applicability.read` |
| `POST /journeys` | `applicability.read` + `survey.simulate` |
| `GET /journeys` · `GET /journeys/{id}` · `GET /journeys/{id}/turn` | `applicability.read` |
| `POST /journeys/{id}/survey-facts` | `applicability.read` |
| `POST /journeys/{id}/start` · `POST /journeys/{id}/answers` · `POST /journeys/{id}/abandon` | `applicability.read` + `survey.simulate` |
| `POST /journeys/{id}/verify` | `applicability.read` |
| `GET /fact-correspondences` · `GET /fact-correspondences/catalog` · `GET /fact-correspondences/{id}` | `applicability.read` |
| `POST /fact-correspondences` | `applicability.read` + `applicability.edit` |

Market-scoped; CSRF on every write and computation; rate-limited (writes, and separately inputs); audited with the
signed-in identity. No operation changes a selection plan, a recorded input or a correspondence version.

## 9. Frontend

Setting `VITE_APPLICABILITY_JOURNEYS=1` (with publication) adds "Run a journey" to the applicability navigation.

- **Synthetic journeys** — the list.
- **New synthetic journey** — choose a published version (current and superseded labelled; a superseded one needs an
  explicit confirmation); give application facts with "not known" and "not provided" as first-class choices, or copy
  them by value from a saved scenario; the server's selection, live: selected surveys in order with the requirement
  that selects each, pending surveys, the facts needed, replacements named.
- **Journey** — a progress rail (surveys, modules, requirements) beside one question at a time: the approved wording,
  controls for exactly the answer type, the allowed non-answers, the server's validation message with its code. Then
  the completion summary, the recorded selection, the frozen survey facts and their origin, every answer, the
  verification with its checks, and the history.

There is no survey engine, no selection logic and no persona switch in the browser.

## 10. Not in this checkpoint

Journey evaluation, findings, control-policy evaluation, execution assurance and the end-to-end trace (APPL-X5b,
`80_…`); any date answer type; question-level sharing; any continuation rule after an incomplete survey; a
governance workflow for fact correspondences; operational application facts; voice.
