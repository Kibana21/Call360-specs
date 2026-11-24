# 76 — APPL-X5 readiness assessment: coordinated published-survey execution

**An assessment only. Nothing here is built, and nothing here is authorised.** Date 2026-11-24.
Simulation only; synthetic facts only. No operational application facts, no case, no callback, no Genesys, no live
voice, no real customer.
Earlier framing this builds on: `58_…` (APPL-X5: "a versioned selection-plan interface … each simulated journey
records its selection source: `LEGACY_ASSIGNMENT` or `APPLICABILITY`"), `55_…` §0.3 ("Selection is ready; everything
after selection is not").

Written from a read-only inventory of the code as it stands. Where I state what exists, it was read in the source;
where I propose, it is marked **Proposed**; where a decision is the owner's, it is in §19.

---

## 1. What APPL-X5 is, in one paragraph

Given **one exact published Applicability Policy version** and **one synthetic fact snapshot**, the server
deterministically selects exact published survey versions, then lets a person walk those surveys question by question
in the browser — in the governed order, with branching, every answer type, unknown and incomplete answers, resume and
replay — evaluates the answers, produces findings and an assurance record, and keeps the whole journey as immutable
evidence. No legacy rule, binding or requirement group is read or written. The same runtime is later driven by voice
instead of a browser, without any business rule moving into the voice layer.

## 2. What exists today and can be reused unchanged

| Capability | Where | Reuse |
|---|---|---|
| Applicability evaluator: facts → plan (`status`, `selected[]` in `policy.order` with `position`, `pending`, `excluded`, `needs`, `diagnostics`, `fingerprint`) | `applicability/evaluator.py`, `logic.py`, `analysis.py` | **as is** — must not change |
| Published policy version: frozen `document`, `manifest` (snapshot and definitions), fingerprints, verification | `applicability_policy_version`; `publication.py` (`verify_version`, `_frozen`) | as is; `_frozen` already evaluates from a version's own frozen definitions |
| Exact survey references in a plan: `code`, `version`, `version_id`, content and manifest fingerprints | policy document, validated at save and at publication | as is |
| Single-survey execution engine, pure and deterministic (`call360.survey.execution/1`) | `survey/execution.py` (`execute`, `execute_inputs`) | **as is** |
| Single-survey simulation: create from a published version and facts; answer one question; read state; replay-drift detection | `survey/simulation.py`; tables `survey_simulation`, `survey_simulation_input` (immutable) | **as is** |
| Answer types | YES_NO, SINGLE_SELECT, MULTI_SELECT, FREE_TEXT, NUMERIC, ACKNOWLEDGEMENT, STATEMENT | as is. **No date type exists** |
| Unknown and incomplete | UNKNOWN is never read as false; answer states ANSWERED, ANSWERED_EMPTY, UNANSWERED, DELIVERED, SKIPPED, NOT_REACHED; stable rejection codes; run statuses PENDING, POLICY_UNRESOLVED, TERMINAL; six terminal states | as is |
| Module sequencing and routing | module statuses (activated, skipped false / unknown / prior outcome / by route, halted, not reached); forward-only jumps; mandatory escalation first | as is |
| Control evaluation, policy-scoped evaluation, findings, execution assurance | `control_evaluation.py`, `policy_evaluation.py`, `journey_evaluation.py`, `execution_assurance.py`, `assurance.py` | the **pure** parts as is; the persisted parts key on the legacy coordinator (§3) |

`rule_engine.py`, `answer_evaluation.py` and `finding_engine.py` are not to be edited and X5 does not need to.

## 3. What does not fit, and why

| Gap | Fact in the code | Consequence |
|---|---|---|
| G-1 No way to evaluate **arbitrary facts against a published version** | the only callers of the frozen evaluator are suite runs and impact | X5 needs one small service: version + facts → plan, recorded |
| G-2 The coordinator is **bound to legacy selection** | `survey_coordinated_simulation.composite_plan_id` and step `group_id` are `NOT NULL` references to composite plan and requirement group; `create` takes only a composite id | X5 cannot use that table without a legacy composite. Its sequencing logic is generic but not parameterised |
| G-3 Evaluation and assurance key on the coordinator | `survey_journey_evaluation` and `survey_execution_assurance` have `journey_kind IN ('SINGLE_SURVEY','COORDINATED')` with exactly one of `simulation_id` / `coordinated_id`; `verify_coordination` compares against the composite's selection | an applicability journey has no place to attach |
| G-4 The journey trace is legacy-shaped for selection | reads rule versions and bindings directly | needs an applicability branch for the selection links |
| G-5 **No shared-delivery execution** | the legacy coordinator treats the same survey twice as a blocker; it never de-duplicates | the applicability evaluator already resolves a declared shared delivery to **one** selected entry with an obligation count — X5 must carry that through to evaluation |
| G-6 Cross-survey continuation | the legacy coordinator proceeds only after `COMPLETED`; anything else is `CROSS_SURVEY_POLICY_UNRESOLVED` | this is an unapproved policy, kept as an explicit unresolved state (§19, Q-3) |
| G-7 No voice-neutral runtime interface | voice is audio-level only (`VoiceProvider`); the one question interface (`question_controller.py`) is script-shaped and voice does not import it | X5 defines the interface (§15) |

## 4. Recommended shape — **Proposed**

A **new, separate applicability journey**, beside the legacy coordinator, not inside it:

1. `selection` — a recorded, immutable **selection plan**: published policy version × fact snapshot → plan.
2. `journey` — a recorded coordinated journey over that plan: one existing single-survey simulation per selected
   survey, in the plan's order.
3. Evaluation, findings and assurance attached to the journey through an additive journey kind.
4. A runtime interface (§15) that the browser uses now and voice uses later.

Why not extend the legacy coordinator: it would need its two `NOT NULL` legacy references relaxed and a
selection-source column on accepted tables, and every legacy reader would have to learn the new shape. A separate
journey keeps the legacy path byte-identical and makes "no legacy object" a property of the schema, not of
discipline. Cost: a second, small coordinator (the sequencing is a few dozen lines over existing simulations).

The alternative — one coordinator with a `selection_source` column — is described in §19 (Q-1) for the owner's choice.

## 5. Authoritative published-policy version selection

- A journey names **one `applicability_policy_version` by id**. Nothing resolves "the latest" implicitly; the screen
  offers the current `PUBLISHED` version and each `SUPERSEDED` one, labelled, and the person chooses.
- A `SUPERSEDED` version stays executable **in simulation** (to reproduce an older journey); whether it may be used
  for a *new* journey is the owner's call (Q-2).
- The version is verified (`verify_version`) before use; a version that does not verify cannot start a journey.
- The working draft and candidates are **not** executable in X5. Drafts are tested in the Scenario studio.

## 6. Synthetic application fact snapshot

- Facts are supplied in the applicability library's own vocabulary: the variables and profiles the version pins, with
  a value, `null` (not known) or absent (not provided) — the Scenario studio's fact model.
- Validated against the **version's frozen variable definitions**, not the live library.
- Frozen with a fingerprint at journey creation; `record_class = SYNTHETIC`; the existing real-data detector
  (`LOOKS_LIKE_REAL_DATA`) applies.
- A saved synthetic scenario may be **copied** in as the starting facts (by value, with its origin recorded). The
  journey never depends on the scenario afterwards.
- **Not in X5:** any mapping from a policy, sale, customer or case to these facts. That is APP-1a.

**The survey's own facts.** A survey simulation also takes facts (checked against the Survey Studio catalog by
`check_facts`). These are a different vocabulary from applicability variables. X5 needs a declared, versioned
correspondence, or two separately entered fact sets. This is the one real design question of the checkpoint (Q-4).

## 7. Deterministic survey selection

- `plan = evaluate(frozen workspace of the version, version document, facts, profiles)` — the accepted evaluator,
  called through the existing frozen path. No new selection logic.
- The **selection plan record** stores: version id and its three fingerprints, fact snapshot and fingerprint, the
  complete plan, the plan fingerprint, the evaluator contract. Immutable; re-derivable from the record alone, like a
  recorded run.
- Outcomes and what the journey may do:

| Plan status | Journey |
|---|---|
| `RESOLVED`, surveys selected | may start |
| `RESOLVED`, none selected | recorded as "no survey required"; nothing to execute |
| `UNRESOLVED` (something pending) | **does not start.** The pending requirements and the facts they need are shown. Not known is never treated as "does not apply" |
| `OUT_OF_SCOPE`, `SCOPE_UNRESOLVED` | does not start; recorded |

## 8. Exact published survey-version pins

Each selected entry already carries `version_id` and both fingerprints. Before a simulation is created the journey
checks that the survey version still exists, is in the same market, is `PUBLISHED` or `SUPERSEDED`, and has the
pinned fingerprints — the check publication already performs. A mismatch stops the journey as an integrity failure;
nothing is substituted or upgraded. The single-survey simulation then freezes the survey's own content fingerprints
again, as it does today.

## 9. Multiple-survey coordination

- Order: `selected[].position`, which is the policy's declared order. No other ordering input.
- One existing simulation per selected survey; step *n+1* starts when step *n* ends.
- **Proposed journey statuses:** `SELECTED`, `RUNNING`, `POLICY_UNRESOLVED` (a survey stopped on an unapproved
  non-answer policy), `CROSS_SURVEY_POLICY_UNRESOLVED` (a survey ended other than `COMPLETED` and there is no
  approved rule for what follows), `ALL_SURVEYS_COMPLETED`, `REPLAY_DRIFT`, `INTEGRITY_FAILED`, `ABANDONED`.
- Replacement is already resolved by the evaluator: a replaced requirement's survey is simply not in `selected`.

## 10. Module and question sequencing, branching, answers

All of it is the existing engine, unchanged, per survey: module eligibility with an explicit unknown policy, routing
per answer or first matching rule, forward-only jumps, mandatory escalation, attempts, delivery mode. X5 adds no
sequencing rule inside a survey.

| Answer | Engine type | Answer keys |
|---|---|---|
| Yes / No | `YES_NO` | `choice` |
| Multiple choice | `SINGLE_SELECT` | `choice`, `other_text` |
| Multi-select | `MULTI_SELECT` | `choices`, `other_text` (limits enforced: `TOO_MANY_SELECTED`, `UNKNOWN_OPTION`) |
| Free text | `FREE_TEXT` | `text` (the text rule applies) |
| Number | `NUMERIC` | `number` (`NUMBER_REQUIRED`, range rule) |
| Acknowledgement, statement | `ACKNOWLEDGEMENT`, `STATEMENT` | `acknowledged` |

A date answer does not exist in the engine. X5 does not add one.

## 11. UNKNOWN and incomplete responses

- The browser must be able to give every non-answer the engine distinguishes: no answer, an empty answer, "does not
  know", refusal to acknowledge. Each is recorded as given; none is mapped to a negative.
- A rejected input (wrong type, unknown option) is recorded with its code and does not advance.
- Where the survey has no approved rule for a non-answer, the survey stops as `POLICY_UNRESOLVED` — an honest state,
  shown as such, with what is missing. X5 invents no fallback.

## 12. Resume and replay

- **Resume:** state is always the replay of recorded inputs. Closing the browser loses nothing; reopening shows the
  next pending question. Optimistic concurrency exists (`expected_inputs`).
- **Replay:** the journey is reproduced from its records: selection plan from version + facts; each survey from its
  inputs. Drift at either level is detected and blocks further input (`REPLAY_DRIFT`), as today per survey.
- **Proposed** `verify` for a journey: re-derive the selection plan and every survey run from the records alone and
  compare fingerprints — the pattern of recorded runs and published versions.

## 13. Shared-delivery semantics

- Meaning, as already governed: one delivery of a survey satisfies each requirement listed in the policy's declared
  `shared_deliveries` entry. The evaluator returns one selected entry with `required_by` (several) and `obligations`.
- X5: that survey is **executed once**. Its completion counts for every requirement in `required_by`; its failure to
  complete leaves every one of them unsatisfied. The journey record keeps the requirement → step mapping.
- An undeclared overlap never reaches X5: it is a blocker at policy publication (`DUPLICATE_SURVEY`).
- **Not** in scope: sharing individual *questions* across different surveys. Nothing governs that today (Q-5).

## 14. Completion, evaluation, findings, assurance, evidence

- **Completion** is per requirement and per journey: every selected survey `COMPLETED` → `ALL_SURVEYS_COMPLETED`;
  otherwise the journey states exactly which requirement is unsatisfied and why.
- **Answer evaluation and findings:** the existing survey adapters (`control_evaluation`, `policy_evaluation`,
  `journey_evaluation`) operate on simulations' evidence under a control policy, with `ALL_REQUIRED` (D-287).
  **Proposed:** an additive journey kind `APPLICABILITY` on `survey_journey_evaluation` and
  `survey_execution_assurance`, referencing the new journey. This **alters two CHECK constraints on accepted
  tables** — it needs the owner's explicit approval (Q-6). The alternative is parallel tables, at the cost of
  duplicated readers.
- **Assurance:** `verify_survey` is reusable per step. `verify_coordination` compares against a legacy composite;
  X5 needs the equivalent comparison against the selection plan: every selected survey executed, at the pinned
  version, once, in order, nothing extra.
- **Immutable journey evidence:** selection plan, fact snapshot, steps, each simulation's inputs, evaluation,
  findings, assurance — all insert-only, fingerprinted, linked. `selection_source = APPLICABILITY` recorded on the
  journey.
- **Journey trace:** an applicability branch showing policy version → facts → plan → surveys → simulations →
  evaluation → findings → assurance. Read-only, as now. Eligibility stays `NOT_ESTABLISHED`.

Everything a finding says remains synthetic and illustrative: no control, obligation or mapping here is approved
compliance policy.

## 15. Voice-neutral question / answer runtime interface — **Proposed contract**

The runtime exposes turns, not screens and not audio. The browser simulation is its first client; a VOICE-0 adapter
would be its second.

```text
next(journey) -> Turn | End
  Turn: { journey_id, step, survey {code, version}, item_key, attempt,
          prompt { text, delivery_mode, exact_wording_required },
          expects { answer_type, options[], selection {min,max}, number_rule, text_rule },
          allowed_non_answers[] }
  End:  { status, per_requirement[], unresolved[] }

submit(journey, item_key, expected_inputs, Answer) -> Accepted | Rejected
  Answer:   { choice | choices | text | other_text | number | acknowledged } | { non_answer: kind }
  Rejected: { code, message }            # the turn is asked again; nothing advanced

state(journey)   -> the same, derived by replay
```

Rules that keep deterministic business logic out of a future LLM voice layer:

1. **The server decides the next turn.** A client never chooses, reorders, skips or invents a question.
2. **The server decides whether an answer is acceptable**, against `expects`. A client only proposes a structured
   answer.
3. **A voice layer's only judgement is transcription into the offered structure** — which option was said, which
   number. It is given `options` and must return one of them or a non-answer. It is recorded as a *proposal* with
   its own evidence (transcript span, confidence), separate from the accepted answer.
4. **Low confidence is a non-answer or a re-ask decided by server rules**, never a guess promoted to an answer.
5. **Mandatory wording** is delivered as given (`exact_wording_required`); that it was spoken verbatim needs
   controlled delivery evidence — an LLM prompt is not proof.
6. Routing, eligibility, evaluation, findings and assurance never run in, or take instructions from, the voice layer.
7. The interface carries no audio, no provider type and no transport. `VoiceProvider` stays replaceable beside it.

X5 would build this interface and its browser client only. No voice code.

## 16. Full browser simulation — journeys to demonstrate

A. Choose a published policy version; enter synthetic facts; see the plan with its reasons.
B. One survey selected; walk it; every answer type; complete.
C. Several surveys in the governed order; one replaced by a combined survey.
D. A declared shared delivery: one execution, several requirements satisfied.
E. Unknown fact → selection unresolved → journey does not start, with what is needed.
F. Non-answers and rejected inputs; `POLICY_UNRESOLVED`; a survey ending other than completed.
G. Close and reopen mid-survey; resume; replay; verify.
H. Evaluation, findings, assurance; journey trace end to end.
I. Negative: no rule, binding, group, composite plan, case or session created or changed; every existing journey and
   the golden 82 runs and 14 plans unchanged.
J. Two people's journeys isolated by market and permission.

## 17. Data model sketch — **Proposed**, one additive migration (`0042`, not created)

| Table | Holds |
|---|---|
| `applicability_selection_plan` | policy version, fact snapshot and fingerprint, plan, plan fingerprint, contract; immutable |
| `applicability_journey` | selection plan, status, `selection_source`, `record_class`; only status transitions allowed |
| `applicability_journey_step` | position, survey version and fingerprints, `required_by`, simulation id, outcome; insert plus outcome once |
| `applicability_journey_event` | append-only history |

Plus, if Q-6 is approved, the two CHECK changes. No new permission is proposed: `applicability.read` to see,
`survey.simulate` to run, `survey.evaluate` to evaluate — to be confirmed (Q-7).

## 18. Risks

| Risk | Mitigation |
|---|---|
| Two fact vocabularies (applicability variables, survey facts) drift apart | a declared, versioned correspondence, or explicit double entry; decide before building (Q-4) |
| A second coordinator diverges from the legacy one | it is thin; both call the same single-survey service; legacy stays untouched until its retirement is separately authorised |
| A simulated journey is mistaken for an operational one | `record_class`, labels on every screen, no case or session reference in the schema |
| Cross-survey continuation rule invented by the software | keep `CROSS_SURVEY_POLICY_UNRESOLVED` until Business decides |
| Voice later pushes logic into prompts | the interface in §15 and its seven rules are the acceptance criteria for VOICE-0 |

## 19. Decisions needed before APPL-X5 can be specified

| # | Question | My recommendation |
|---|---|---|
| Q-1 | Separate applicability journey, or extend the legacy coordinator with a selection source | separate (§4) |
| Q-2 | May a **superseded** policy version start a new simulated journey | yes in simulation, clearly labelled; never by default |
| Q-3 | What happens after a survey ends other than completed | stay unresolved; no rule invented |
| Q-4 | How applicability facts relate to a survey's own facts | a small declared correspondence owned by the policy author, versioned and frozen in the journey; needs a short design step of its own |
| Q-5 | Question-level sharing across different surveys | out of scope |
| Q-6 | Alter the journey-kind CHECK on the two accepted evaluation tables, or use parallel tables | alter, additively, with explicit approval |
| Q-7 | Permissions for running an applicability journey | reuse existing; no new grant |
| Q-8 | Is evaluation under a control policy part of X5, or a following checkpoint | split: X5a selection + execution + evidence; X5b evaluation, findings, assurance, trace |

## 20. Not part of APPL-X5

Operational application facts (APP-1a), a survey assigned to a real case (OPS-1), VOICE-0 and VOICE-1, Genesys,
designer integration steps 2–4, retirement of legacy assignment, any real customer.
