# UC-02 — Decision-ready contracts, minimal interfaces and implementation-readiness checklist

**Checkpoint:** UC-02 (Contract and Call-Plan Readiness), authorised by the owner on 2026-11-21 ("Accept UC-01 and
Authorize UC-02").
**Status: REVIEWED BY THE OWNER 2026-11-21.** 17 technical decisions recommended for approval; 6 to be amended; the
12 persistence blockers to be ruled. **The outcome, the amended wording and the proposed rulings are in
`25_UC-02_DECISION_CLOSURE.md`, which governs where it differs.** Original status: PROPOSED — presented for the owner's review. Part 1 sorts every remaining decision; Part 2 gives the
minimal authoritative interfaces; Part 3 is the readiness checklist. **Nothing here is implemented on a server, and no
existing engine is re-implemented.**

**Rules kept throughout.** No timeout value, retry limit, consent-refusal behaviour or spoken-data permission is
invented. The no-answer decision register (`17_SS-02C_NO_ANSWER_CONTRACT.md` §10) is preserved unchanged: its 17
decisions and 4 parameters keep their identifiers, their UNRESOLVED status and their "blocks" columns; this document
only says where each one bites.

---

## Part 1 — The remaining decisions, sorted

### 1.1 How to read the tables

Each decision is one of three **kinds**, and may **block** up to three things:

| Kind | Meaning |
|---|---|
| **Technical** | A shape, name, identity or integrity rule with no policy content. Engineering can propose it and the owner can approve it now |
| **Business / Compliance** | Decides what a customer hears, what a call does, or who may approve. Needs the business or Compliance |
| **Voice channel** | Only matters once speech is produced or heard. Can wait until the runtime checkpoint |

| Blocks | Meaning |
|---|---|
| **Persistence** | The definition store's schema cannot be frozen without it |
| **Runtime** | The execution harness cannot be built correctly without it |
| **Real calls** | It can be built behind a parameter or a switch, but no real customer call may happen until it is decided |

### 1.2 Technical schema decisions that can be approved now

None of these contains a policy. Each is already exercised by the prototype and, where marked, by an independent
golden fixture. **Recommendation: approve as a set.**

| No. | Decision | Verified by |
|---|---|---|
| TS-1 | **One item master.** An item is a question or a statement. A node is `QUESTION`, `STATEMENT` or `DECISION`; a `STATEMENT` node places a statement item and nothing else does | Fixtures K1, K2 |
| TS-2 | **Single-route items.** A statement, a number question, an acknowledgement and a free-text question have exactly one route, `AFTER_CAPTURE`, and cannot branch | K2 |
| TS-3 | **Execution identity** is `<module instance>/<node>`. Display labels (Q1, S1, C1) are never identity, are never stored, and are never sorted on | K7 |
| TS-4 | **Delivery mode is an explicit field** of every stored Wording Version: `CONTROLLED_TTS`, `EXACT_AUDIO`, `CONVERSATIONAL`. Storage never leaves it implicit. *Which value is the default for an author is UC-D-1, a business decision* | K6 |
| TS-5 | **Recording asset reference.** `EXACT_AUDIO` requires `asset {id, sha256, approval}`. Without a usable, approved asset the item cannot be delivered: a validation **error**, never a warning | K6 |
| TS-6 | **Controlled variables — mechanism.** `{{field_code}}`, bound to one catalog field; no expression, default or nesting; rendering is a pure function of (text, snapshot); every variable resolves to `PRESENT`, `MISSING`, `INVALID`, `UNKNOWN_VARIABLE` or `MALFORMED`; if any is not `PRESENT` the item is not delivered. *Which fields may be spoken is UC-D-3* | K5, K6 |
| TS-7 | **Value formats are exact.** A whole-number field holding a fraction, or an amount with more than two decimals, is `INVALID` — never rounded or truncated | K5 |
| TS-8 | **Number rule** `{integer, min?, max?, unit?}`; limits inclusive; rejection codes `NUMBER_REQUIRED`, `NUMBER_NOT_WHOLE`, `NUMBER_TOO_LOW`, `NUMBER_TOO_HIGH` | K3 |
| TS-9 | **Acknowledgement answer shape.** `{acknowledged: true}` is the only accepted value. An explicit `false` is rejected with `NON_ANSWER_POLICY_UNRESOLVED` and is not an answer value. *What a call does then is D-NA, a business decision* | K4 |
| TS-10 | **Number and acknowledgement answers are not condition inputs in schema version 1.** A condition may read yes/no and choice answers only. *Whether to add them is UC-D-7* | — |
| TS-11 | **Module graph as one validated, versioned, hashed document** per module version; integrity enforced by the server validator; usage served by a derived index (owner: AD-3 approved) | — |
| TS-12 | **Draft → Candidate → Version** as three entities. Candidate and Version are insert-only | Prototype governance tests |
| TS-13 | **Lifecycle states in the contract**, including `SCHEDULED` and `WITHDRAWN` (owner: AD-13 approved): see Part 2 §2.1. No operational behaviour is attached to them here | — |
| TS-14 | **Separate Publisher permission** and three identity rules enforced independently of permissions: checker ≠ any maker of the candidate; publisher ≠ submitter; holding a permission never satisfies an identity rule (owner: AD-5 approved). *Who holds Publisher, and whether the approver may also publish, is G-4* | Prototype governance tests |
| TS-15 | **Call plan document** and its `READY` / `BLOCKED` rule; open points enumerated, never resolved; stable issue codes | K1, K5, K6, K7, K8 |
| TS-16 | **Plan computability and live-call eligibility are separate results.** A plan never carries an eligibility verdict | Prototype tests |
| TS-17 | **Plan/run consistency.** Every item a run delivers is delivered with exactly the text and values the plan gave for it | All 19 runs of K1–K8 |
| TS-18 | **Validation codes** as stable identifiers (contract §8.4) | K2, K6 |
| TS-19 | **Evaluation and control link shapes** (`EvaluationConfig`, `ControlLink`; methods allowed per item kind; choices matched by code). *Who may set them and how tolerance is approved is UC-D-8* | Prototype contract test |
| TS-20 | **Assignment rule** is its own governed, versioned artefact that targets a survey version, authored through Survey Studio (owner: UC-D-9 approved) | — |
| TS-21 | **Findings policy** is its own governed artefact in the Survey Studio Library, under separate Compliance permissions (owner: UC-D-10 approved) | — |
| TS-22 | **"Survey" terminology for all new APIs**; no destructive renaming of legacy structures yet (owner: AD-14 approved) | — |
| TS-23 | **Single language.** A `language` field exists and is fixed to `en` (owner: AD-12 approved) | — |

### 1.3 Business and Compliance decisions that remain open

| No. | Decision | Blocks persistence | Blocks runtime | Blocks real calls |
|---|---|:-:|:-:|:-:|
| **UC-D-1** | The delivery mode offered by default when an author chooses none | **Yes** — a required field needs a rule | | |
| **UC-D-2** (AD-9) | Conversational delivery: remove it, or restrict it to items Compliance classes as low-risk. Blocked in the prototype | **Yes** — enum membership | **Yes** | **Yes** |
| **UC-D-3a** (AD-8) | **Permitted variable fields**: which application fields may be spoken in wording at all. A customer's name is personal data | **Yes** — a catalog flag | | **Yes** |
| **UC-D-3b** (AD-8) | The policy when a variable has no usable value: block the item (as now), or an approved alternative wording without the variable | | **Yes** | **Yes** |
| **UC-D-4** | The list of statement roles ("Transition" is new); whether a statement may require acknowledgement | **Yes** — enum | | |
| **UC-D-5** | **Lifecycle gates**: what a call does when identity, consent to proceed, recording consent or cloud-processing consent is answered "no", refused or not answered; "policy information only after identity"; "deliver on termination". The existing rules are development assumptions | | **Yes** | **Yes** |
| **UC-D-6** (D-NA-5, D-NA-10) | **Mandatory questions**: whether "mandatory" and "required" are one property; the question classes; where refusal is acceptable | **Yes** — the field's shape | **Yes** | **Yes** |
| **UC-D-7** | **Numeric condition inputs**: may a number (or an acknowledgement) be read by a condition or choose a route, for example a threshold | Additive later — not blocking | | |
| **UC-D-8** | **Evaluation configuration**: who may set it; how a numeric tolerance is approved and referenced; whether it is approved with the question or separately | Partly — approval record | | **Yes** |
| **UC-D-11** (D-NA-8) | **Repeat and clarification wording**: which phrases exist; verbatim or approved alternative; who approves them | Additive later — not blocking | **Yes** | **Yes** |
| G-4a | Who holds the Publisher permission; whether the approver may also publish | **Yes** — role seed and one rule | | **Yes** |
| G-4b | Whether a draft is locked while a candidate is in review (prototype: no) | **Yes** | | |
| G-4c | What "approved wording" is in Call360: who approves, how it is recorded | **Yes** — approval record | | **Yes** |
| G-4d | The escalation-handling workflow after a call ends with Escalate | | | **Yes** |
| G-4e | The stored form of activation, eligibility and the two skip dispositions (confirm as built) | **Yes** | | |
| SS-D-05 | The outcome catalog: the approved list of outcomes and their classes | **Yes** | **Yes** | **Yes** |
| D-NA-1 | The reasons a question is unanswered | | **Yes** — evidence model | **Yes** |
| D-NA-4 | Whether a refusal is confirmed before it is recorded | | **Yes** | **Yes** |
| D-NA-9 | How a non-answer is routed: route key, node policy or survey-level | **Yes** — route contract | **Yes** | **Yes** |
| D-NA-11 | Whether a follow-up queue continues past an unanswered follow-up | | **Yes** | **Yes** |
| D-NA-12 | Refusal or silence on a question with a mandatory-escalation option | | **Yes** | **Yes** |
| D-NA-13 | The catalogued outcome for "no answer obtained" | **Yes** — outcome catalog | **Yes** | **Yes** |
| D-NA-15 | Precedence of disconnection, escalation, non-answer and routing | | **Yes** | **Yes** |
| D-NA-16 | Retention and access for non-answer evidence | | | **Yes** |
| `NA-P-REPEATS-PER-QUESTION`, `NA-P-REPEATS-PER-CALL`, `NA-P-REFUSALS-PER-CALL` | Values. **None is proposed here** | | | **Yes** |
| — | The AIA/SBQ process, still a working hypothesis | | | **Yes** |
| G-1, G-2 | Business-user UX acceptance; screen-reader sign-off | | | Before Survey Studio is on by default |

### 1.4 Voice-channel decisions that can wait

They matter only when speech is produced or heard. None blocks persistence; each blocks the runtime checkpoint or
real calls.

| No. | Decision |
|---|---|
| UC-D-3c (AD-8) | The **spoken form** of amounts, dates, numbers and names — the prototype's formats are written formats |
| TS-5 follow-on | How a recording is produced, approved and attached; variables are impossible in a recording |
| D-NA-2 | Whether a question may change the response window |
| D-NA-3 | Whether unintelligible responses share the silence counter |
| D-NA-6 | How an optional question is left blank on a voice call |
| D-NA-7 | Whether a disconnected run resumes or restarts |
| D-NA-14 | A terminal state for disconnection |
| D-NA-17 | Abandonment on a non-voice channel |
| `NA-P-RESPONSE-WINDOW` | Value. **None is proposed here** |
| D-68 | Cloud-processing consent before audio reaches a cloud provider, as a channel requirement |
| — | What counts as proof that exact wording was delivered (a prompt is not proof) |

### 1.5 The three "blocks" lists

**Blocking backend persistence — decide before the definition store's schema is frozen (12):**
UC-D-1 · UC-D-2 · UC-D-3a · UC-D-4 · UC-D-6 (D-NA-5, D-NA-10) · G-4a · G-4b · G-4c · G-4e · SS-D-05 · D-NA-9 ·
D-NA-13. Plus approval of TS-1…TS-23.

**Blocking runtime execution — decide before the harness executes anything beyond what the fixtures specify (13, plus
three from the voice list):**
UC-D-2 · UC-D-3b · UC-D-5 · UC-D-6 · UC-D-11 · SS-D-05 · D-NA-1 · D-NA-4 · D-NA-9 · D-NA-11 · D-NA-12 · D-NA-13 ·
D-NA-15, and from the voice list D-NA-3, D-NA-7, D-NA-14 when the channel is voice.

**Blocking real calls — everything above, and in addition:** UC-D-3a · UC-D-3c · UC-D-8 · G-4d · D-NA-2 · D-NA-16 ·
D-NA-17 · every `NA-P-…` value · approved wording for every item · approved recordings where used · D-68 · the
AIA/SBQ process · G-1, G-2 · production readiness (G-8).

### 1.6 The six topics the owner named

| Topic | What can be approved now | What stays open | Until then |
|---|---|---|---|
| **Mandatory questions** | That the attribute is declared on the item version and carried into the content document | Its shape and meaning: D-NA-5, D-NA-10 (UC-D-6) | Recorded; no behaviour. Persistence of the field waits |
| **Lifecycle gates** | That a role is declared on a yes/no question; the structural live-eligibility check (D-67) | Every behaviour on "no", refusal or silence (UC-D-5) | A "no" follows the route the author set; nothing else happens |
| **Numeric condition inputs** | TS-10: not in schema version 1 | Whether to add them (UC-D-7) | Not offered; additive later |
| **Permitted variable fields** | TS-6, TS-7: the mechanism and exact formats | Which fields may be spoken (UC-D-3a); missing-value policy (3b); spoken form (3c) | Any catalog field except yes/no facts; a missing value blocks delivery |
| **Repeat wording** | Nothing | UC-D-11, D-NA-8, the three repeat parameters | Shown as unavailable; not in any schema |
| **Evaluation configuration** | TS-19: the shapes | Who sets it, tolerance approval (UC-D-8) | Contract only; every item's configuration is empty |

---

## Part 2 — Minimal authoritative interfaces

Six interfaces. Each lists only what must be authoritative: operations, the facts they return, and the invariants a
caller may rely on. Transport, pagination, storage layout and screens are deliberately absent. **Existing engines keep
their internals**; where an interface is already met by one, that is stated.

### 2.1 Survey definition and immutable publication

```text
apply(survey, expected_revision, operation)        → draft            # one operation of the authoring vocabulary
validate(draft | candidate)                        → findings[]       # stable codes; BLOCKER | WARNING | INFO
submit(survey, note, acknowledgements)             → candidate
decide(candidate, APPROVE | REJECT, comment)       → candidate
publish(candidate, effective_from?)                → version
withdraw(version, reason)                          → version
content(draft | candidate | version)               → content document + sha256
history(survey | module | item | policy)           → events[]
```

| Entity | States | Mutability |
|---|---|---|
| Draft | — | Mutable; one per survey; optimistic concurrency on `expected_revision` |
| Candidate `C-n` | `IN_REVIEW` → `APPROVED` \| `REJECTED` \| `WITHDRAWN` \| `SUPERSEDED` → `PUBLISHED` | Content, manifest and hashes never change; only the status and the decision record are added |
| Version | `SCHEDULED` → `PUBLISHED` → `SUPERSEDED` \| `WITHDRAWN` | Content never changes |

**Invariants.**
1. A candidate is `{id, n, content_sha256, manifest (every pinned item, wording, option set, condition and module
   version), manifest_sha256, submitted_by}`. Approval and publication refer to it by id.
2. Submitting a changed draft creates `C-n+1` and supersedes an open candidate; no approval is carried over. A draft
   made identical to an earlier candidate is not approved.
3. **Identity rules, enforced independently of permissions:** the checker is not a maker of that candidate; the
   publisher is not its submitter. Publishing requires the Publisher permission.
4. Blockers cannot be waived. A warning needs a recorded reason. An undeliverable item is a blocker.
5. A version is created only from an `APPROVED` candidate whose manifest re-verifies at publication.
6. `SCHEDULED` and `WITHDRAWN` are states of the contract. **When a scheduled version takes effect, and what
   withdrawing does to cases already assigned, are not specified here.**
7. Every transition writes an audit event to the existing hash chain.
8. The same interface publishes a module, an assignment rule and a findings policy; each is approved in its own
   candidate. One authoring application does not mean one approval event.

### 2.2 Approved survey assignment

```text
evaluate(case_inputs, at)                          → decision
apply(case, decision, idempotency_key)             → assignment
current(case)                                      → assignment | none
```

`decision = {outcome: SELECTED | NO_MATCH | AMBIGUOUS | INPUT_MISSING | TARGET_NOT_EFFECTIVE | CONTACT_UNRESOLVED,
version?, rule_version?, trace}`.
`assignment = {case, version_id, manifest_sha256, rule_version_id, input_snapshot, input_sha256, assigned_at}`,
insert-only.

**Invariants.** Only published, effective rule versions are evaluated. Every failure fails closed: no lower rule is
tried, nothing is guessed. A case is assigned once; a change is a new assignment that supersedes. **This is the
existing assignment engine and ledger, unchanged in behaviour;** its target becomes a survey version and its
conditions are evaluated by the one condition engine.

### 2.3 Customer application snapshot and typed field binding

```text
catalog()                                          → fields[{code, type, unit?, values?, speakable}]
snapshot(case)                                     → {id, sha256, taken_at, facts{code → value | null}, lineage}
bind(version, snapshot)                            → bindings[{use, field, state, value}]
```

**Invariants.** A snapshot is immutable and hashed. A fact is `PRESENT`, `MISSING` or `INVALID`; **a missing value is
never defaulted** and never read as "no". `use` names the reader: the eligibility of a module instance, or a variable
of an item's wording. `speakable` says whether a field may appear in wording; **its values are UC-D-3a and are not
set here.** The existing fact snapshot already has this grain.

### 2.4 Deterministic call-plan assembly

```text
plan(version | candidate | draft, snapshot)        → plan
eligibility(version, case, channel)                → conditions[{id, state: MET | NOT_MET | NOT_AVAILABLE, detail}]
```

`plan = {source, snapshot_sha256, status: READY | BLOCKED, issues[{code, at}], inputs, modules[{instance, status:
IN | OUT | CONDITIONAL | HALTS}], items{execution_key → {…, text | null, values, certainty}}, open{…}, sha256}`.

**Invariants.**
1. Pure: the same source and snapshot give the same plan and the same hash.
2. `BLOCKED` when any item a call could reach cannot be rendered, or any module cannot be decided and its policy is
   to stop.
3. Open points are enumerated with their alternatives. A plan contains no answer and no chosen path.
4. **`plan` answers only "can a plan be computed". It carries no eligibility.** A plan may be computed from a draft.
5. **`eligibility` is a separate call with separate inputs.** Its conditions are explicit: a published version; an
   approved assignment of that version to the case; approved wording for every item; every item deliverable as
   approved; the mandatory identity, consent-to-proceed and recording-consent gates present; the channel's
   requirements; the no-answer policy decided; and the plan computable. Eligible means every condition is `MET`.
6. Whatever a run delivers, it delivers with exactly the text and values of its plan.

### 2.5 Graph execution

```text
start(plan)                                        → run
next(run)                                          → action | terminal
record_delivery(run, action_id, evidence)          → ok
submit_answer(run, action_id, answer)              → accepted | rejected(code)
state(run)                                         → {asked, delivered, modules, terminal | pending, trace}
```

`action = {action_id, execution_key, kind: DELIVER_STATEMENT | ASK_QUESTION, text, delivery_mode, asset?}`.

**Invariants.** One current action. Forward only; a module is entered at most once; every item instance is delivered
at most once. A stale or wrong `action_id` is rejected; a repeated one is idempotent. A rejected answer is recorded as
a rejection and the same question remains current. Six terminal states, never merged. Escalate is terminal in every
routing mode. Three-valued conditions; missing information is never "no". **There is no non-answer input**: silence,
refusal, repeat and disconnection are reserved and undefined until gate G-3 is decided. The executor never composes
wording. Specified by the 27 golden fixtures (schemas /1–/5). **This is the existing controller's event-sourced core
with its navigation generalised; it is not rebuilt.**

### 2.6 Evaluation and control evidence

```text
evaluate(content, run)                             → results[{execution_key, method, result, expected, observed, inputs_sha256}]
findings(results, policy_version)                  → findings[{finding_key, execution_key, rule, category, severity, controls}]
```

**Invariants.** Results and findings are keyed by execution key, so a question placed twice is evaluated twice. The
same inputs give the same results and the same finding keys; regeneration creates no duplicates. A match is not a
compliance pass; a mismatch is a discrepancy for review, not a finding. A statement is never evaluated. **These are
the existing answer-evaluation and finding engines.** The only changes are their input — `EvaluationConfig` and
`ControlLink` read from the content document, choices matched by code — and the key.

---

## Part 3 — Implementation-readiness checklist

Status: **Ready** · **Ready when decided** · **Not ready**.

### 3.1 Specification and fixtures

| Item | Status |
|---|---|
| Canonical model: surveys, modules, items, wording, conditions, routing | Ready (contract §1–§7) |
| Schemas /1–/4: 19 fixtures, 63 expected runs, four reference interpreters | Ready — unchanged, regenerate byte-for-byte |
| Schema /5: 8 fixtures, 19 expected runs, 14 expected plans, 12 expected validation errors, fifth reference interpreter | Ready (contract §8) |
| Prototype engine reproduces all 27 fixtures | Ready |
| Stable validation and rejection codes | Ready for the UC-01 and UC-02 rules; earlier rules still identified by message — to be coded before the server validator |
| Decisions and activation triggers in the call plan | Specified in prose (§7.6); **not covered by a fixture** |
| Follow-up queues, rules and interruptions together with statements | **Not covered by a fixture** |
| Six minimal interfaces | Proposed (Part 2) |

### 3.2 Decisions

| Item | Status |
|---|---|
| AD-1, AD-2 (in principle), AD-3, AD-5, AD-12, AD-13, AD-14, AD-15, UC-D-9, UC-D-10 | Decided |
| TS-1…TS-23 | Ready when approved (§1.2) |
| The 12 decisions blocking persistence | Not ready (§1.5) |
| The 13 decisions blocking runtime, plus three voice-channel ones | Not ready (§1.5) |
| No-answer register: 17 decisions, 4 parameters | Unresolved, preserved |

### 3.3 Before any destructive change (AD-2) — none started

| Item | Status |
|---|---|
| Inventory of the actual development database | Not ready |
| Protected demonstration records and owner restrictions identified | Not ready |
| Verified backup and a rehearsed restore | Not ready |
| Exact scope of a re-seed stated | Not ready |
| Separate destructive-change checkpoint approved | Not ready |

### 3.4 Before Survey Studio is on by default

| Item | Status |
|---|---|
| Business-user UX acceptance: seven timed usability gates, reviewer walkthroughs | Not ready — no evidence |
| Screen-reader sign-off by a person | Not ready — no evidence |
| Automated accessibility scans | Ready — clean on every prototype screen |

### 3.5 What a first backend checkpoint could start on without waiting

Only the parts no open decision touches:

1. The publication interface (§2.1) for the entities and states of TS-12…TS-14 — except the Publisher role seed and
   draft locking (G-4a, G-4b).
2. The content document and its hash, for every field **except** `mandatory` (UC-D-6) and the `speakable` flag
   (UC-D-3a).
3. The server validator for the coded rules, verified by fixtures /1–/5.
4. The condition engine, verified by fixtures F6, F8, G, H and K8.
5. Plan assembly (§2.4) in simulation, verified by K1, K5, K6, K7 and K8.

**Not startable:** any non-answer behaviour; gate behaviour; repeat wording; conversational delivery; anything that
re-seeds or removes existing data.
