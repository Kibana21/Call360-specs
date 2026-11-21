# SS-02C · A-5 — When a question is not answered: a decision-ready contract

**Status:** PROPOSED FOR DECISION (prepared 2026-11-21 under the owner's instruction A-5). **Nothing in this document
is approved, specified as final, or built.** It replaces the list of open points in `04` §5.5 with a structure the
business and Compliance can decide against. No telephony, voice or runtime handling of non-answers exists or was
added in this checkpoint.

> **UNRESOLVED — 17 of 17 decisions are open (status reviewed 2026-11-21, SS-02 closure).** No decision in this
> document has been taken by the business or by Compliance, and no parameter has a value. Every `DECISION D-NA-…`
> marker below means **undecided**. Where a table shows a "proposal" or a "proposed default", it is an option put
> forward for a ruling, **not a policy**. §10 lists every decision with its status and which of them block a real
> runtime.

**Two rules for reading it**

1. **No number is proposed.** Every duration and every count is a named parameter (`NA-P-…`) with an owner. The
   contract says *that* a value must exist, *where* it is set and *what it controls* — never what it is.
2. **Where a behaviour needs a business or compliance ruling it is marked `DECISION`** and listed in §10 with who must
   approve it before production. An implementation that meets an undecided point has no defined behaviour and must
   not guess one.

All examples are synthetic. None of the wording is approved AIA or MAS language.

---

## 1. Vocabulary: five different things that are not "an answer"

They are different facts with different evidence. They are never merged into one "no answer" state.

| Term | What happened | Who or what detects it |
|---|---|---|
| **Silence** | The question was delivered and nothing intelligible was received within the allowed time | The channel (a timer) |
| **Unintelligible response** | Something was received but it could not be understood as any permitted answer | The channel or the agent |
| **Explicit refusal** | The customer said they will not answer this question | The channel or the agent, confirmed |
| **Optional blank** | A question that may be left empty was left empty by choice | The answer itself |
| **Disconnection** | The call ended before the question was answered | The channel |

Related but out of scope here, because they belong to the conversation lifecycle above the survey graph (SS-D-08):
the customer asks to be called back; the customer cannot be reached at all; an agent takes over.

**Already decided and unchanged** (`04` §5.4 (d-1)): the four answer-evidence states `ANSWERED`, `ANSWERED_EMPTY`,
`UNANSWERED`, `SKIPPED`. An **optional blank** is already defined: an optional free-text answer left blank is
`UNANSWERED`; a multiple-choice question answered with nothing selected (where the minimum is zero) is
`ANSWERED_EMPTY`. This document does not change either.

---

## 2. Evidence model (proposed)

A question that was asked and not answered keeps the state `UNANSWERED`. What is new is a **reason** and the
**attempts**, so that "left blank by choice" is never confused with "silence" or "refused".

| Field | Values | Notes |
|---|---|---|
| `evidence_state` | `ANSWERED` · `ANSWERED_EMPTY` · `UNANSWERED` · `SKIPPED` | Unchanged |
| `unanswered_reason` | `OPTIONAL_BLANK` · `SILENCE` · `UNINTELLIGIBLE` · `REFUSED` · `DISCONNECTED` | Present only when `UNANSWERED`. `DECISION D-NA-1`: is this the complete list? |
| `attempts[]` | one entry per delivery of the question | See below |
| `resolution` | what the survey did next (§5) | A route key, an outcome, or a lifecycle hand-off |

Each attempt records: its number; the delivery reference (which wording version was delivered, and that it was
delivered); when delivery ended; what was received (nothing / unintelligible / refusal / an answer); when; and, for
voice, the evidence link to the recording segment and transcript span.

`SKIPPED` keeps its meaning — *not asked on this path* — and is never used for a question that was asked.

---

## 3. Per-situation contract

### 3.1 Silence and timeouts
- A **response window** opens when delivery of the question ends and closes after `NA-P-RESPONSE-WINDOW`.
- The window is a **channel** property (voice latency is not a survey author's concern), with at most a per-question
  override class (`DECISION D-NA-2`: may a question lengthen it, for example a long list of options?).
- When the window closes with nothing received, the attempt is recorded as silence and the **repeat policy** (§4)
  applies. Silence is never recorded as an answer and never evaluated as "no".

### 3.2 Unintelligible response
- Recorded as an attempt with what was received. It consumes an attempt in the same way as silence
  (`DECISION D-NA-3`: same counter as silence, or its own?).
- It is never mapped to the nearest option by guesswork. Mapping free speech to option codes is the extraction
  contract's concern, and an unmapped response is `UNINTELLIGIBLE`.

### 3.3 Explicit refusal
- Refusal is **not** an answer and does **not** satisfy a mandatory question.
- `DECISION D-NA-4`: is a refusal repeated back or confirmed once before it is recorded? (A customer who says "I'd
  rather not say" to a verification question may not realise the call cannot continue without it.)
- `DECISION D-NA-5`: for which classes of question is refusal acceptable without ending the survey? Proposed
  classification on the **question definition** (so a placement cannot weaken it, as with mandatory escalation):

| Class (proposed) | Meaning | On refusal |
|---|---|---|
| `REQUIRED` | The survey cannot be meaningful without it (identity, confirmation of purchase) | The configured non-answer outcome (§5) |
| `EXPECTED` | Asked of everyone; a refusal is a finding, not a stop | Recorded; the survey continues by the non-answer route |
| `OPTIONAL` | May be left unanswered | Recorded; continues |

### 3.4 Optional blank answers
- Already defined (§1). No timer, no repeat, no refusal handling: leaving an optional question blank is a completed
  step. The reason `OPTIONAL_BLANK` only makes that explicit in evidence.
- `DECISION D-NA-6`: on a voice call, how does a customer "leave it blank" — by saying so, or by silence? If silence,
  the optional question needs its own rule so that §3.1 does not turn it into repeats.

### 3.5 Call disconnection
- Detected by the channel, not by the survey. The question in progress is recorded `UNANSWERED · DISCONNECTED`;
  every later question on the path has **no evidence state at all** (it was never reached), and is not `SKIPPED`.
- The survey run ends in a **new terminal state** (§6). It is not a module outcome and not a survey outcome chosen by
  routing.
- `DECISION D-NA-7`: is a disconnected run resumable (a later contact attempt continues from the unanswered
  question) or always restarted? This touches the grain in `CANONICAL_GRAIN_AND_RELATIONSHIPS.md` (callback case →
  contact attempts → conversation sessions → survey runs) and must be decided there.

---

## 4. Retry and repeat limits; approved wording on repeats

| Parameter | Controls | Set by (proposed) | Owner |
|---|---|---|---|
| `NA-P-RESPONSE-WINDOW` | How long to wait after delivery | Channel configuration | Business + Voice engineering |
| `NA-P-REPEATS-PER-QUESTION` | How many times one question may be delivered again | Survey-level default, question class may lower it | Business + Compliance |
| `NA-P-REPEATS-PER-CALL` | Total repeats in one call before the call is treated as not workable | Survey level | Business + Compliance |
| `NA-P-REFUSALS-PER-CALL` | Refusals tolerated before the survey ends | Survey level | Compliance |

No value is proposed for any of them.

**Approved wording on repeats.** Customer-facing wording is governed (SS-D-02): what is spoken must be an approved
wording version, and an LLM prompt is not evidence that it was spoken.

| Option | Description | Consequence |
|---|---|---|
| **R-1 Verbatim** | A repeat delivers the same approved wording again | Simplest evidence; may sound mechanical |
| **R-2 Approved alternate** | Each question may carry approved *repeat wordings*, versioned and pinned with the question | Natural; adds wording to approve and to compare between revisions |
| **R-3 Approved preface + verbatim** | A short approved preface ("Let me ask that again.") followed by the same wording | Middle ground; the preface is a governed artefact too |

`DECISION D-NA-8`: which of R-1 / R-2 / R-3. Free rephrasing by a model is **not** offered as an option: it cannot
be evidenced as approved wording. Whatever is chosen, each attempt records the exact wording version delivered.

---

## 5. What the survey does next: routing a non-answer

Today a question's routes are keyed by an answer (`04` §2.1), resolved "specific → ANY → blocked". A non-answer has
no key. Three ways to give it one:

| Option | Description | For | Against |
|---|---|---|---|
| **N-1 Route key** | A new route key on question nodes (`NO_ANSWER`, optionally per reason) with its own destination | Visible in Guided and Graph like any route; validation can require it | Every question gains a route; more to configure |
| **N-2 Node policy** | Each question declares a non-answer policy from a short list (continue by the normal route / end the module with an outcome / end the survey) | Less clutter; a survey-level default covers most questions | Hidden from the graph unless drawn |
| **N-3 Survey-level only** | One survey-wide rule; questions cannot differ | Simplest | Too coarse for `REQUIRED` versus `OPTIONAL` |

`DECISION D-NA-9`: N-1, N-2 or N-3. Whichever is chosen:

- **`ANY` never matches a non-answer.** "Everybody continues" means every *answer* continues.
- **A condition that reads an unanswered question gets UNKNOWN** (already the rule), and applies its own UNKNOWN
  policy. Non-answer is not FALSE.
- **Nothing is defaulted silently.** If the chosen design requires a destination and it is missing, that is a
  validation error; at run time it is an invalid draft, never a guess.

### 5.1 Mandatory questions
A mandatory question (`mandatory: true`) that ends unanswered after the limits **cannot** be followed by the normal
route. It resolves to a governed non-answer outcome (§6). `DECISION D-NA-10`: does "mandatory" mean the `REQUIRED`
class of §3.3, or are they two properties?

### 5.2 Follow-up queues
`DECISION D-NA-11`: when a follow-up in a queue is not answered — does the queue continue with the next follow-up, or
stop? Proposed default for decision: continue, unless the follow-up is `REQUIRED`.

### 5.3 Mandatory escalation
A mandatory escalation is triggered by an **answer**. A non-answer never triggers it and never cancels it:

- If a mandatory-escalation answer was already given, the escalation stands whatever is unanswered afterwards.
- `DECISION D-NA-12`: for a question that *has* a mandatory-escalation option, is a refusal itself a matter for
  escalation or review? (Silence in reply to "Did you agree to this policy?" is not consent.) This is a compliance
  ruling, not a routing default.

---

## 6. Termination and escalation outcomes

The outcome catalog is governed (D-133). A non-answer must not be folded into `COMPLETED`, into an existing
exception, or into `ESCALATE`.

| Need | Proposal for decision |
|---|---|
| A module or survey ended because a required answer could not be obtained | A new catalogued outcome, class `EXCEPTION` — working name `NO_ANSWER_OBTAINED` (`DECISION D-NA-13`: name, class, and whether refusal and silence share it or have one each) |
| The call dropped | A new **terminal state** beside the six of `04` §2.2b — working name `DISCONNECTED` — carrying where it stopped. It is not an outcome anyone routed to (`DECISION D-NA-14`) |
| Refusal or silence on a question that Compliance wants reviewed | Use the existing governed `REVIEW_REQUIRED` halt, or `ESCALATE`, by explicit configuration only (`DECISION D-NA-12`) |

Precedence, extending `04` §2.3 (proposed order for decision — `DECISION D-NA-15`):

1. Disconnection (the call is over; nothing else can be evaluated).
2. A mandatory escalation already triggered by an answer.
3. The non-answer resolution of the current question.
4. Ordinary routing.

---

## 7. Evidence and audit events

Proposed events, each immutable and linked to the survey run, the question instance and the wording version:

| Event | When |
|---|---|
| `QUESTION_DELIVERED` | Each delivery, with the wording version and attempt number |
| `RESPONSE_WINDOW_EXPIRED` | Silence |
| `RESPONSE_UNINTELLIGIBLE` | Something received, not understood |
| `ANSWER_REFUSED` | Explicit refusal (and its confirmation, if D-NA-4 requires one) |
| `QUESTION_REPEATED` | A further delivery, with the repeat wording option used |
| `REPEAT_LIMIT_REACHED` | Per question or per call, naming the parameter |
| `QUESTION_UNANSWERED` | The final state, with `unanswered_reason` and the resolution taken |
| `CALL_DISCONNECTED` | From the channel, with the question in progress |

`DECISION D-NA-16`: retention and access to these events follow the recording and transcript rules
(`IDENTITY_AUTHORIZATION_AND_AUDIT.md`); confirm no separate class is needed.

---

## 8. Voice channel versus non-voice

| Aspect | Voice (browser audio, later Genesys) | Non-voice (a form, a manual capture screen, the prototype simulator) |
|---|---|---|
| Silence | A timer after delivery | No timer by default; an abandoned form is a session matter, not a question matter |
| Unintelligible | Real and frequent | Does not occur: the input is validated instead (`04` §3.4 codes) |
| Refusal | Spoken; needs recognition and possibly confirmation | An explicit control ("Prefer not to answer") — only if the question class allows it |
| Optional blank | Needs a rule (D-NA-6) | Leaving the field empty |
| Disconnection | Channel event | Session expiry or abandonment — `DECISION D-NA-17`: same terminal state, or a different one? |
| Repeats | Re-delivery of approved wording (D-NA-8) | Not applicable; the question stays on screen |
| Evidence | Recording segment + transcript span per attempt | The submitted value and timestamps |

The **survey contract is channel-neutral**: evidence states, reasons, classes, outcomes and routing are the same.
What differs by channel is *detection* and the *parameters*. The channel adapter (`VoiceProvider`, kept replaceable)
reports the five situations of §1; it does not decide what the survey does next.

---

## 9. What validation and the simulator would need (not built)

- Validation: every `REQUIRED` question has a non-answer resolution; every parameter the survey depends on is set;
  no non-answer resolution weakens a mandatory escalation.
- Simulator: a "does not answer" turn with a reason, so that a non-answer journey can be played and compared like any
  other. The prototype deliberately has none: it would be inventing behaviour.
- Golden fixtures (a new schema version) for each decided rule, generated and checked like F, G and H.
- Revision comparison: a change to a question's class, to a repeat wording or to a parameter is a change that needs
  review; repeat wordings need wording approval.

---

## 10. Decisions required: status, approvers, and what each one blocks

**Status of every row: UNRESOLVED.** "Blocks runtime build" = a survey runtime cannot be *implemented* correctly
without it, because it shapes the schema, the outcome catalog, the route contract, the evidence model or the
execution order. "Blocks real calls" = it can be built behind a parameter or a switch, but no real customer call may
take place until it is decided.

| # | Decision | Status | Business | Compliance | Engineering | Blocks runtime build | Blocks real calls |
|---|---|---|:-:|:-:|:-:|:-:|:-:|
| D-NA-1 | The list of reasons a question is unanswered | UNRESOLVED | ● | ● | | **Yes** — evidence model | Yes |
| D-NA-2 | Whether a question may change the response window | UNRESOLVED | ● | | ● | No | Yes |
| D-NA-3 | Whether unintelligible responses share the silence counter | UNRESOLVED | ● | | ● | **Yes** — attempt counting | Yes |
| D-NA-4 | Whether a refusal is confirmed before it is recorded | UNRESOLVED | ● | ● | | **Yes** — turn sequence and evidence | Yes |
| D-NA-5 | Question classes (`REQUIRED` / `EXPECTED` / `OPTIONAL`) and where refusal is acceptable | UNRESOLVED | ● | ● | | **Yes** — question schema | Yes |
| D-NA-6 | How an optional question is left blank on a voice call | UNRESOLVED | ● | | ● | **Yes** — voice turn handling | Yes |
| D-NA-7 | Whether a disconnected run resumes or restarts | UNRESOLVED | ● | ● | ● | **Yes** — run and session grain | Yes |
| D-NA-8 | Wording on repeats: verbatim, approved alternate, or approved preface | UNRESOLVED | ● | ● | | **Yes** — wording schema and delivery evidence | Yes |
| D-NA-9 | How a non-answer is routed: route key, node policy or survey-level | UNRESOLVED | ● | | ● | **Yes** — route contract | Yes |
| D-NA-10 | Whether "mandatory" and `REQUIRED` are the same property | UNRESOLVED | ● | ● | | **Yes** — question schema | Yes |
| D-NA-11 | Whether a follow-up queue continues past an unanswered follow-up | UNRESOLVED | ● | ● | | **Yes** — queue execution | Yes |
| D-NA-12 | Refusal or silence on a question with a mandatory-escalation option | UNRESOLVED | | ● | | **Yes** — escalation rules | Yes |
| D-NA-13 | The catalogued outcome(s) for "no answer obtained" | UNRESOLVED | ● | ● | | **Yes** — outcome catalog | Yes |
| D-NA-14 | A terminal state for disconnection | UNRESOLVED | ● | | ● | **Yes** — terminal states | Yes |
| D-NA-15 | Precedence of disconnection, escalation, non-answer and routing | UNRESOLVED | ● | ● | ● | **Yes** — execution order | Yes |
| D-NA-16 | Retention and access for non-answer evidence | UNRESOLVED | | ● | ● | No | Yes |
| D-NA-17 | Abandonment on a non-voice channel | UNRESOLVED | ● | | ● | No (voice first) | Yes, for that channel |
| NA-P-RESPONSE-WINDOW | Value | NO VALUE SET | ● | ● | ● | No — a parameter | Yes |
| NA-P-REPEATS-PER-QUESTION | Value | NO VALUE SET | ● | ● | | No — a parameter | Yes |
| NA-P-REPEATS-PER-CALL | Value | NO VALUE SET | ● | ● | | No — a parameter | Yes |
| NA-P-REFUSALS-PER-CALL | Value | NO VALUE SET | | ● | | No — a parameter | Yes |

### Decisions that block real runtime implementation

**Fourteen decisions block building the runtime at all:** D-NA-1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 and 15.
Of these, **seven shape contracts that the first backend checkpoint would have to fix** and are therefore needed
before any backend work on the survey runtime: D-NA-1, D-NA-5, D-NA-9, D-NA-10, D-NA-13, D-NA-14, D-NA-15.

**Three decisions and all four parameter values do not block the build but block any real call:** D-NA-2, D-NA-16,
D-NA-17, and every `NA-P-…` value.

Until each is decided, an implementation that meets the situation has **no defined behaviour** and must stop, not
guess. The prototype reflects this: it has no "does not answer" turn, and its validation raises "what happens when a
customer does not answer is not decided yet" on every survey as a warning that can only be acknowledged, never
resolved.
