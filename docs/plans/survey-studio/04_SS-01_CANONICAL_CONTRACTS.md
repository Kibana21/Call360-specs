# SS-01 · Part A — Canonical domain and execution contracts

**Checkpoint:** SS-01 (documentation and design contracts only — no application code, migration or API change).
**Date:** 2026-11-21. **Status:** PROPOSED for owner approval. Authorised by the owner's "Accept SS-00 and Authorize
SS-01" instruction, which also set the direction for SS-D-01, 02, 09, 17 and 20.

This part covers SS-01 deliverables **1–6**. Part B (`05_…`) covers 7–10, Part C (`06_…`) is the decision register
(11), Part D (`07_…`) is the SS-02 prototype plan (12). The eight JSON fixtures in `fixtures/` are the worked examples
of every contract here; each rule below names the fixture that exercises it.

**Normative language.** "Must" marks a rule the validator or the engine enforces. JSON shapes are the *logical*
contract; physical table design is decided in SS-03 and must satisfy these contracts without rewriting history.
All thresholds, wording and outcome names in examples are illustrative.

---

## 1. Domain definitions: Definitions, Versions, Instances

### 1.1 The three kinds of thing

| Kind | Meaning | Mutability | Identified by |
|---|---|---|---|
| **Definition** | A reusable asset's stable identity | Never deleted; may be deprecated | a stable business code |
| **Version** | Immutable content of a definition at a point in time | Immutable once it leaves draft | `code@version` |
| **Instance** | One placement of a version inside a parent version, with bindings that apply only there | Part of the parent version; immutable with it | a code unique within the parent |

A **binding** is instance-level configuration (a route, a parameter value, an UNKNOWN policy). The governing rule:

> **R-1.** An instance edit must never change a definition or a version. Editing shared content always produces a new
> version (or a fork), chosen explicitly by the author.

### 1.2 Entities

| Entity | Kind | Stable code (example) | Owns | Does **not** own |
|---|---|---|---|---|
| Survey | Definition | `S-NEW-BUSINESS` | Identity, purpose, owner | Content |
| Survey Version | Version | `S-NEW-BUSINESS@1.0` | Module instances, sequence, outcome routes, dependency lock, hash | Module internals |
| **Module Instance** | Instance | `mi-suitability` (unique in the survey version) | Entry rule binding, parameters, outcome routes | The module's questions |
| Module | Definition | `M-SUITABILITY` | Identity, kind | — |
| Module Version | Version | `M-SUITABILITY@1` | Entry node, nodes, edges, follow-up plans, outcome list | Question content; what an outcome leads to |
| **Question Instance** (node) | Instance | `n2` (unique in the module version) | Routing mode, edges, follow-up plan, applicability binding, pinned wording version | Wording, answer type, options |
| Decision (node) | Instance | `d1` | Condition binding | The condition's logic |
| Question | Definition | `Q-UNDERSTOOD` | Identity, intent | — |
| Question Version | Version | `Q-UNDERSTOOD@1` | Answer type, option set reference, selection and text validation, mandatory flag, evaluation settings | Customer-facing text; routing |
| Wording Version | Version | `Q-UNDERSTOOD/en/1` | Customer-facing text, delivery mode, option texts, Other prompt, approval state | Structure; routing |
| Option Set | Definition / Version | `OS-MAIN-CONCERN@1` | Option codes, business labels, order, exclusivity, `Other` schema | Customer-facing option text; routes |
| Condition | Definition / Version | `C-HIGH-VALUE@1` | Typed AST, parameter schema, named inputs, field dependencies | Parameter values; UNKNOWN policy |
| **Condition Binding** | Instance | (inline in its owner) | Parameter values, input mapping, UNKNOWN policy | The AST |
| Field | Catalog entry | `policy.annual_premium` | Type, unit, source, sensitivity, availability | — |
| Outcome | Catalog entry | `CLARIFICATION_REQUIRED` | Governed code and meaning | — |
| Test Profile | Definition / Version | `P-ILP-HIGH-PREMIUM@1` | Synthetic field values | — |

### 1.3 Execution identity

| Identity | Form | Stable when |
|---|---|---|
| **Module Instance key** | `{instance}` | For the life of the survey version |
| **Question Instance key** | `{instance}/{node}` — e.g. `mi-risks/n2` | For the life of the survey version |
| **Edge key** | `{instance}/{edge}` — e.g. `mi-suit/e3` | For the life of the survey version |
| **Occurrence** | integer, starts at 1 | Increases only when an instance is re-executed after an authorised Back/Edit (§9 of Part B); never by routing |

> **R-2.** Within one run, a Question Instance is executed at most once per occurrence, and occurrence 2+ exists only
> through Back/Edit supersession. Routing can never cause the same placement to be asked twice (no cycles in P0;
> follow-up queues dedupe; a module instance is entered at most once).

> **R-3.** Codes are never derived from labels. Renaming a label, a module or a question changes no key.

### 1.4 What the existing model already provides (SS-D-01)

Survey = `script_family`; Survey Version = `script_version`; Module Instance = `script_section`; Module Version =
`script_module`; Question / Question Version = `question_bank_item` / `question_revision`; Question Instance =
`module_question`. The compatibility of each pair is proven, with its limits, in Part B §8.

---

## 2. Graph and route contracts

Two graphs, deliberately separate (PRD §10.1): the **survey graph** connects module instances; a **module graph**
connects the nodes inside one module version. Neither is ever flattened into the other for authoring.

### 2.1 Module graph

```json
{
  "code": "M-SUITABILITY", "revision": 1, "kind": "PRODUCT",
  "entry": "n1",
  "outcomes": ["COMPLETED", "CLARIFICATION_REQUIRED"],
  "nodes": [
    {"node": "n1", "type": "QUESTION",
     "question": {"code": "Q-BENEFITS-EXPLAINED", "version": 1, "wording_version": 1},
     "routing": {"mode": "PER_CHOICE", "normal_answer": "YES"}},
    {"node": "d1", "type": "DECISION", "binding": { "…": "see §5" }}
  ],
  "edges": [
    {"edge": "e1", "from": "n1", "on": "YES", "to": {"node": "n2"}},
    {"edge": "e5", "from": "n2", "on": "NO",  "to": {"outcome": "CLARIFICATION_REQUIRED"}}
  ]
}
```

**Nodes.** `QUESTION` (asks one Question Version through one Wording Version) or `DECISION` (evaluates one condition
binding; asks nothing). A node may carry `"role": "FOLLOWUP"` (§4).

**Edges.** `from` a node, `on` a trigger code, `to` exactly one of: `{"node": …}`, `{"outcome": …}`,
`{"return": true}` (follow-up nodes only).

| Source | Allowed `on` codes |
|---|---|
| Yes/No question | `YES`, `NO`, `ANY` |
| Single-select question | any option code of its option set, `ANY` |
| Multi-select question | `ANY` (mode `ALL_TO_NEXT`); none in the other modes — routing is in the node (§3.4, §4) |
| Free-text question | `AFTER_CAPTURE`, `ON_SKIP` (optional questions only) |
| Decision | `MATCH`, `NO_MATCH`, `UNKNOWN` |

**Edge resolution (deterministic).** For trigger code *c* at node *n*:
1. the edge `(n, c)` if it exists;
2. otherwise the edge `(n, ANY)` — the explicit default;
3. otherwise the run is `BLOCKED` with `ROUTE_MISSING`.
There is at most one edge per `(node, on)`; two is a validation error (`AMBIGUOUS_ROUTE`). `ANY` is a real stored edge
("all answers → next" is not a display shortcut — SS-QUE-006, SS-ROU-003).

**Merges.** Any number of edges may target one node. The node exists once (F2: `n2` has two inbound edges; F3:
`n-confirm` has four).

**Outcomes.** Every path from the entry node must end at an edge `to.outcome` naming one of the module's declared
outcomes, each taken from the governed outcome catalog (SS-D-05).

**`normal_answer`.** For a question in `PER_CHOICE` mode, the answer the author designated as the normal path. It is
used only by the insertion rule below and by the guided view's layout; it has no run-time effect.

**Safe insertion (server rule).** Inserting question *X* on edge `A —c→ B`:
`A —c→ X`; `X —normal_answer→ B`; every other answer of *X* is left **without an edge**. Missing edges are validation
errors, so the draft cannot be submitted until the author routes them (SS-ROU-006, SS-AT-007). With mode
`ALL_TO_NEXT`, the single `ANY` edge takes B and nothing is left open.

### 2.2 Survey graph

```json
{
  "code": "S-NEW-BUSINESS", "version_label": "1.0", "language": "en",
  "sequence": ["mi-general", "mi-suitability", "mi-high-value", "mi-replacement", "mi-escalation", "mi-closing"],
  "instances": [
    {"instance": "mi-suitability",
     "module": {"code": "M-SUITABILITY", "revision": 1},
     "entry": {"mode": "RULE", "binding": {"condition": {"code": "C-IS-ILP", "version": 1}, "unknown_policy": "BLOCK"}},
     "routes": [{"on": "COMPLETED", "to": "@CONTINUE"},
                {"on": "CLARIFICATION_REQUIRED", "to": "@CONTINUE"}]}
  ],
  "end": {"survey_outcome": "COMPLETED"}
}
```

**Sequence.** The ordered list of module instances. It is the Lego story the author sees.

**Entry modes** (SS-SUR-005):

| Mode | Activated when | Otherwise recorded as |
|---|---|---|
| `ALWAYS` | Always | — |
| `RULE` | The entry binding evaluates `TRUE` | `SKIPPED_FALSE`; on `UNKNOWN`, by the binding's policy: `BLOCKED_UNKNOWN` (policy `BLOCK`) or `SKIPPED_UNKNOWN` (policy `SKIP_WITH_REASON`) |
| `ON_OUTCOME` | The named earlier instance emitted one of the listed outcomes | `SKIPPED_PRIOR_OUTCOME` (including when that instance did not run) |

`ON_OUTCOME` may only name an instance **earlier** in the sequence, so the value is always available when needed
(SS-AT-032 is a validation error, not a run-time surprise).

**Outcome routes.** For every outcome a module version declares, the instance must have exactly one route:

| `to` | Meaning |
|---|---|
| `"@CONTINUE"` | Go to the next instance in the sequence (after the last one: the survey's `end` outcome) |
| `{"instance": "mi-x"}` | Jump forward to a **later** instance, entering it unconditionally; instances in between are recorded `SKIPPED_BY_ROUTE` |
| `{"survey_outcome": "ESCALATE"}` | Stop the survey with that outcome |

A missing route is a validation error — there is no silent default (SS-SUR-006). Inserting a module instance gives its
normal outcome (`COMPLETED`) the route `@CONTINUE` and leaves every other outcome **unrouted** until reviewed
(SS-SUR-007, UX-STORY-01).

**Module status values** recorded for every instance in every run: `ACTIVATED` (with its outcome), `SKIPPED_FALSE`,
`SKIPPED_UNKNOWN`, `SKIPPED_PRIOR_OUTCOME`, `SKIPPED_BY_ROUTE`, `BLOCKED_UNKNOWN`, `NOT_REACHED`. A skipped module is
never confused with a customer answering "No" (F8, seven runs).

**Sequencing policy (SS-D-06).** "Ordered eligibility": each instance is considered in order and runs if eligible.
Outcome routes are explicit exceptions to that order. Backward routes are invalid (no cycles in P0).

### 2.2a Amendment of 2026-11-21: routing, activation and eligibility (owner decision D-135)

**This amends §2.2. Where it differs, this section governs.** In particular the sentence "Jump forward to a later
instance, **entering it unconditionally**" is **withdrawn**: a jump never bypasses a module's condition.

Three different things decide whether a module instance runs. They are kept apart in the contract, in validation, in
the trace and in the authoring surface:

| Concept | Question it answers | Expressed by |
|---|---|---|
| **Routing / jump** | Which instance is the next **candidate**? | The sequence (the next instance), an outcome route `{"instance": …}`, or a skip disposition `{"instance": …}` |
| **Activation trigger** | **When is an instance selected** at all? | In sequence; by a jump; or — `entry.mode: ON_OUTCOME` — only by a named earlier outcome |
| **Eligibility condition** | **May the candidate execute?** | `entry.mode: RULE` (a condition binding with an explicit UNKNOWN policy). `ALWAYS` = no eligibility condition |

**Rule.** Eligibility is evaluated for every candidate, however it was reached. For a candidate reached by a jump:

| Eligibility | Result |
|---|---|
| TRUE (or no eligibility condition) | The instance executes |
| FALSE | The instance is skipped, recorded `SKIPPED_FALSE`, and the instance's **skip disposition** is followed |
| UNKNOWN, policy `BLOCK` | A **missing-information halt** (§2.2b): the run stops pending review. The instance did not start |
| UNKNOWN, policy `SKIP_WITH_REASON` | The instance is skipped, recorded `SKIPPED_UNKNOWN` ("information missing"), and the skip disposition is followed |
| UNKNOWN, no policy | Validation error `UNKNOWN_POLICY_MISSING` (unchanged: there is no global default) |

**Skip disposition.** A new, optional member of an instance:

```json
{"instance": "mi-specialist", "entry": {"mode": "RULE", "binding": {…, "unknown_policy": "BLOCK"}},
 "if_ineligible": {"survey_outcome": "CLARIFICATION_REQUIRED"},
 "routes": […]}
```

`if_ineligible` says what happens when the instance was reached **by a jump** and is not eligible. Its values are
those of a route: `"@CONTINUE"` (the next instance in sequence is considered, as after a skip in sequence),
`{"instance": …}` (a **later** instance — itself only a candidate, so its eligibility is evaluated in turn), or
`{"survey_outcome": …}`.

- It is **required** — validation error `SKIP_DISPOSITION_MISSING` — on every instance that (a) is the target of a
  jump from an outcome route or from another instance's skip disposition and (b) has an eligibility condition. There
  is **no default**: an executor that meets the gap ends the run as an invalid draft (§2.2b); it never continues.
- It is not consulted when the instance is skipped in sequence: there the next instance is simply considered, as
  before ("ordered eligibility", SS-D-06).
- `{"instance": …}` must name a later instance (`BACKWARD_ROUTE` otherwise).

**No re-entry, no loops.** Every move — sequence, outcome route, skip disposition — goes to a later instance, and each
instance is considered at most once in a run. A candidate that is skipped is not reconsidered.

**Activation by a named earlier outcome is preserved.** `ON_OUTCOME` remains an *activation trigger*: in sequence
the instance is selected only if the named earlier instance emitted one of the listed outcomes
(`SKIPPED_PRIOR_OUTCOME` otherwise). It is not an eligibility condition. **Open point for the owner:** in this
amendment a *jump* to an `ON_OUTCOME` instance activates it (a jump is itself an explicit activation, and such an
instance has no eligibility condition). An instance cannot currently carry both an activation trigger and an
eligibility condition; whether it should is a schema question for SS-03.

**Trace.** Every entry decision records how the instance was reached (`SEQUENCE` or `JUMP`), the eligibility result
and what was read; a skip after a jump records the disposition that was followed. Fixtures G1–G3.

### 2.2b Amendment of 2026-11-21: terminal states of a run (owner decision D-136)

A run ends in exactly one of six states. They are different facts and are **never merged** — not in the engine, not
in evidence, not to satisfy a comparison:

| Terminal state | Meaning | Carries |
|---|---|---|
| `COMPLETED` | Every instance that applied finished and the survey reached its end | `survey_outcome: COMPLETED` |
| `ENDED_WITH_OUTCOME` | A named outcome was routed to end the survey — an exception, or an escalation reached by ordinary routing | `survey_outcome` |
| `MANDATORY_ESCALATION` | The survey ended with an outcome of class `ESCALATION` **because a mandatory-escalation answer was given** | `survey_outcome` |
| `REVIEW_REQUIRED` | A module **ran and ended with** the governed outcome `REVIEW_REQUIRED` (a decision set to stop and flag for review, §5.4 (e)) | `survey_outcome: REVIEW_REQUIRED`, `at` (instance) |
| `MISSING_INFORMATION_HALT` | An instance's **eligibility** was UNKNOWN and its policy is `BLOCK`. The instance never started, so there is **no module outcome** | `reason: ELIGIBILITY_UNKNOWN`, `at` (instance) |
| `DRAFT_INVALID` | The draft is incomplete or invalid at this point (a missing route, condition, policy or skip disposition; a backward route; a loop). **Not a result of a call**: nothing was decided | `reason` (a validation code), `at` |

`REVIEW_REQUIRED` and `MISSING_INFORMATION_HALT` both leave the run *pending review, not completed* (§5.4 (h)), but
they are distinct: one is a module outcome, the other is the absence of one. Module status vocabulary changes
accordingly: `BLOCKED_UNKNOWN` (schema /1) becomes **`HALTED_MISSING_INFORMATION`**.

**Versioned migration of the fixture vocabulary.** The historical fixtures (schema `/1`, F1–F8) are preserved
unchanged. Schema `/2` (G1–G6) uses the vocabulary above. The mapping is one-way, partial and stated once:

| Schema /2 (and the engine) | Schema /1 |
|---|---|
| `terminal.state: MISSING_INFORMATION_HALT`, `at` | `blocked: {"reason": "BLOCKED_UNKNOWN", "at"}` — the only halt /1 could express |
| module status `HALTED_MISSING_INFORMATION` | module status `BLOCKED_UNKNOWN` |
| `terminal.state: DRAFT_INVALID`, `reason` R | `blocked: {"reason": R}` (for example `ROUTE_MISSING`) |
| `COMPLETED`, `ENDED_WITH_OUTCOME`, `MANDATORY_ESCALATION` | `survey_outcome` only — /1 cannot say *why* a survey ended with `ESCALATE` |
| `terminal.state: REVIEW_REQUIRED` | **no equivalent** — /1 has no governed review outcome |

A comparison against a `/1` fixture applies this mapping explicitly, outside the engine; a `/2` comparison applies
none. `/1` remains valid for what it covers (it contains no jump, so D-135 changes none of its expectations).

### 2.2c Amendment of 2026-11-21 (SS-02C): activation and eligibility independent; skip disposition in sequence; mandatory escalation survey-wide (owner decisions D-138 … D-141)

**This amends §2.2a. Where it differs, this section governs.** It resolves the "open point for the owner" of §2.2a.

**(a) An explicit jump is a valid activation (D-138).** A jump selects its target even when the target is normally
activated only after a named outcome and that outcome did not occur. The jump never bypasses eligibility: the
target's eligibility condition is still evaluated, exactly as in §2.2a. The trace of an entry decision states both
facts — how the module was selected, and whether it was eligible.

**(b) Activation and eligibility are two independent members of an instance (D-139).** One field no longer carries
two incompatible meanings:

```json
{"instance": "mi-specialist",
 "activation": {"of": "mi-afford", "outcomes": ["CLARIFICATION_REQUIRED"]},
 "entry": {"mode": "RULE", "binding": {"condition": {…}, "params": {…}, "unknown_policy": "SKIP_WITH_REASON"}},
 "routes": […]}
```

| Member | Meaning | Absent |
|---|---|---|
| `activation` | The **activation trigger**: in sequence the instance is *selected* only if the named earlier instance ended with one of the listed outcomes | Selected in sequence |
| `entry` | The **eligibility condition**: `ALWAYS` = none; `RULE` = a condition binding with an explicit UNKNOWN policy | — (required; `ALWAYS` is the neutral value) |

Evaluation order for a candidate: **(1) activation** — reached in sequence with a trigger that did not fire, the
instance is *not selected* (`SKIPPED_PRIOR_OUTCOME`), its eligibility is **not evaluated**, and the next instance is
considered; reached by a jump, it is selected. **(2) eligibility** — evaluated for every selected instance.

*Backward compatibility.* `entry.mode: ON_OUTCOME` (schemas /1 and /2) is still read and means exactly
`activation` + `entry: ALWAYS`. Nothing written under /1 or /2 changes meaning. New edits write `activation`.
Validation: `activation.of` must be an earlier instance and `outcomes` non-empty (`ACTIVATION_INVALID`).
`REVIEW_REQUIRED` cannot be an activating outcome: it halts the run.

**(c) Skip disposition for a module reached in sequence (D-140).** A second, optional member:

| Member | Applies when | Absent | Values |
|---|---|---|---|
| `if_ineligible` (§2.2a, unchanged) | reached **by a jump** and not eligible | **Validation error** `SKIP_DISPOSITION_MISSING` when a jump can arrive and the instance has an eligibility condition. Never defaulted | `"@CONTINUE"` · `{"instance"}` (later) · `{"survey_outcome"}` |
| `if_skipped_in_sequence` (new) | reached **in sequence** and not eligible | **The next instance is considered** — the normal default, as before | `{"instance"}` (later) · `{"survey_outcome"}` (an approved terminal outcome) |

They are two members, not one, so that a survey written under /2 keeps its meaning: there, `if_ineligible` applied
only after a jump and a module skipped in sequence always continued (fixture G1, run 4). Both dispositions are
forward-only (`BACKWARD_ROUTE`); a target named by either is a jump target and is itself only a candidate. A
disposition whose target instance was removed becomes *undecided* — a validation error — never re-pointed. A
disposition is not used when the instance was not selected at all (activation did not fire).

**(d) A mandatory escalation cannot be overridden by survey-level routing (D-141).** When a module ends because a
mandatory-escalation answer was given (§2.3; single-choice, first-matching-rule or follow-up routing alike):

- the survey **ends** with that module outcome as the survey outcome — in this release the governed `ESCALATE` —
  in terminal state `MANDATORY_ESCALATION`, **whatever** route the instance has for that outcome;
- a survey route for such an outcome that is anything other than `{"survey_outcome": <the same outcome>}` —
  continuing, jumping to a later module, ending as a normal completion or as another outcome, or a review halt — is
  the validation error **`MANDATORY_ESCALATION_OVERRIDDEN`**. Authoring surfaces offer only the governed ending;
- a mandatory answer whose module-level route does not end in an outcome of class `ESCALATION` remains the
  module-level error of §5.4 (g); at run time it is an invalid draft (`MANDATORY_ESCALATION_WEAKENED`).

An *ordinary* route to `ESCALATE` (no mandatory answer) is ordinary routing and may be routed by the survey.
A governed escalation-*handling* workflow (what happens after the call ends with `ESCALATE`) is out of scope and is
not defined here.

**Fixtures (schema `/3`):** H1 (the four activation × eligibility combinations; the earlier shape read unchanged),
H2 (a jump as an activation that never bypasses eligibility), H3 (dispositions in sequence), H4 (mandatory
escalation against two invalid survey mappings, with the expected validation errors). `/3` adds `activation`,
`if_skipped_in_sequence`, `validation.errors` and two trace lines; a `/2` survey means the same under `/3`.

### 2.2d Amendment of 2026-11-21 (SS-02 closure): Escalate is terminal in every routing mode (owner decision D-145)

**This extends §2.2c (d).** That section made a *mandatory* escalation impossible to override. The owner has ruled
that **every** escalation is terminal for the survey, however the module reached it:

- A module outcome of class `ESCALATION` (in this release: `ESCALATE`) **ends the survey with that same outcome** —
  whether the module ended that way because of a mandatory-escalation answer, a single-choice route, a
  first-matching rule, an optional interruption or a decision's route.
- The survey route for such an outcome is **governed**, like `REVIEW_REQUIRED`: it is set to
  `{"survey_outcome": <the same outcome>}` when the outcome appears, and authoring surfaces offer nothing else.
- A survey route for it that says anything else is a validation error — **`ESCALATION_NOT_TERMINAL`**, or
  `MANDATORY_ESCALATION_OVERRIDDEN` when a mandatory answer can produce that outcome — and an executor **never
  follows it**.
- The terminal state still tells the two apart: `MANDATORY_ESCALATION` when a mandatory answer caused it, otherwise
  `ENDED_WITH_OUTCOME` with `survey_outcome: ESCALATE`.
- Unchanged: an outcome that is *not* an escalation may still be routed by the survey to end the call with
  `ESCALATE`; and the two separate skip dispositions of §2.2c (c) are retained exactly as specified there.

**Fixture (schema `/4`):** J1 — three modules end with Escalate without a mandatory answer (single choice, rule,
optional interruption) against three different invalid survey routes. A `/3` survey whose escalation outcomes all
end the call as themselves means the same under `/4`; F, G and H are unchanged.

### 2.3 Selection precedence (PRD §5.5)

1. A lifecycle stop — a gate failure or a reported conversation event (SS-D-08).
2. An interrupt in a multi-select follow-up plan (§4).
3. The node's or instance's specific route.
4. Its explicit default (`ANY`, or the plan's fallback).
5. Otherwise `BLOCKED` — never "completed".

---

## 3. Answer contracts

### 3.1 Common shape

Every submitted answer is validated **before** any routing is resolved, against the pinned Question Version and
Option Set Version. Validation errors are stable codes; a rejected answer records nothing and the current step does
not change.

| Answer type | Submission | Trigger code used for routing |
|---|---|---|
| `YES_NO` | `{"choice": "YES" \| "NO"}` | the choice |
| `SINGLE_SELECT` | `{"choice": "<option code>", "other_text"?: "…"}` | the choice |
| `MULTI_SELECT` | `{"choices": ["<code>", …], "other_text"?: "…"}` | by mode (§3.4) |
| `FREE_TEXT` | `{"text": "…"}` | `AFTER_CAPTURE` (or `ON_SKIP`) |

Besides a typed answer, a response may be one of the existing non-answers — `UNCLEAR`, `REFUSED`, `UNKNOWN` — which
keep today's controller behaviour (re-prompt up to the limit, then unresolved) and never select an answer edge.

### 3.2 Yes/No

Options are the fixed set `YES`, `NO` (`OS-YES-NO`). Modes: `ALL_TO_NEXT` (one `ANY` edge; PRD "BOTH_TO_NEXT") or
`PER_CHOICE` (PRD "INDEPENDENT"); both answers may target the same node. Fixtures F1 (all to next), F2 (per choice).

### 3.3 Single-select

Option Set Version: 2..N options, each `{code, business_label, order, exclusive?, is_other?, other_text?}`; codes are
unique and immutable within the set. Modes:

| Mode (PRD name) | Edges required |
|---|---|
| `ALL_TO_NEXT` | one `ANY` edge |
| `PER_CHOICE` (BY_CHOICE) | one edge per option code |
| `PER_CHOICE_WITH_DEFAULT` (BY_CHOICE_WITH_DEFAULT) | an `ANY` edge plus any number of per-option overrides |

Fixtures F3 (four distinct routes with a four-way merge) and F5 (default plus an `OTHER` override).

### 3.4 Multi-select

`selection: {min, max}` on the Question Version; `exclusive` on options. The full selection is validated and recorded
first, then **routed once** by exactly one mode:

| Mode | Contract |
|---|---|
| `ALL_TO_NEXT` | One `ANY` edge. No follow-ups. |
| `ORDERED_RULES` | `rules: [{priority, when, to}]` plus a mandatory `fallback`. `when` is a set predicate over the selection (`contains`, `contains_all`, `contains_any`, combinable with AND/OR/NOT). Rules are tried in ascending priority; **the first match wins and nothing else runs**. Equal priorities are a validation error. |
| `SEQUENTIAL_FOLLOWUPS` | The follow-up queue of §4. May ask several follow-ups, one at a time, then rejoins once. |

The three modes are never combined on one node, and the author must choose one (PRD §6.6).

**Selection limits are never changed implicitly (owner correction, 2026-11-21, D-130).** `selection` is present only
when an author has set it; absent means "at least one, up to every option that can be combined". No other edit —
adding, deleting or duplicating an option, changing `exclusive` — may alter a stored `selection`. When such an edit
makes the stored limits unsatisfiable (`max` above the number of combinable options, `min` above `max` or above what
can be combined) the validator reports **`SELECTION_LIMITS_UNSATISFIABLE`** as a blocker on the question, the stored
values are kept, and the author must explicitly choose replacement limits (or remove them). Undo of the offending edit
restores the previous valid state. A server-side command that would cause this state is accepted on a draft (it is a
validation finding, not a rejected write), so the author's intent is never silently discarded.

**Mandatory escalation in routing (owner decision, 2026-11-21, D-128).** Mandatory escalation always overrides
ordinary routing. For every allowed selection that contains a mandatory-escalation option, the single destination
that results — in any mode — must be an outcome in the **approved escalation outcome set** (a governed list, not
"any outcome other than Completed"); otherwise `MANDATORY_ESCALATION_BYPASSED` (blocker). In `ORDERED_RULES` this is
checked over the allowed selections, so rule order cannot weaken it.

**`ORDERED_RULES` (confirmed by the owner, D-126).** Explicit priority (the order of `rules`), a required `fallback`,
exactly one winner, no parallel execution. A rule evaluation is never silently skipped: if a rule's predicate cannot
be evaluated (an input it reads is UNKNOWN) evaluation stops and the node's `UNKNOWN` handling applies — the next rule
is **not** tried as if the unknown rule had been false. A selection that fails validation is not routed at all.

### 3.5 `Other — please specify`

`OTHER` is an **option**, not a question type: `{"code": "OTHER", "is_other": true, "other_text": {"required",
"min_length", "max_length"}, "allow_with_others": bool}`.

- The companion text is accepted **only** when the `is_other` option is selected (`OTHER_TEXT_NOT_ALLOWED` otherwise —
  no phantom text evidence, SS-AT-035).
- If `required`, an empty text is rejected (`OTHER_TEXT_REQUIRED`); length bounds give `OTHER_TEXT_TOO_SHORT` /
  `OTHER_TEXT_TOO_LONG`. The selection stays selected in the UI.
- `allow_with_others: false` on a multi-select makes `OTHER` exclusive (`EXCLUSIVE_OPTION_CONFLICT`).
- `OTHER` routes like any option: its own edge, the default, or a follow-up in a queue.
- The text is evidence, never a routing input: no rule, condition or model may branch on its content in P0.
- The prompt shown for the text field belongs to the Wording Version (`other_prompt`).

Fixture F5 (three rejections, the accepted evidence shape, and the default route for a non-Other choice).

### 3.6 Free text

`text: {required, min_length, max_length}` on the Question Version. Stored verbatim (subject to the privacy rules of
Part B §6.4). Routes on `AFTER_CAPTURE`; an optional question left empty routes on `ON_SKIP` if such an edge exists,
otherwise on `AFTER_CAPTURE`. Free text never selects a compliance branch in P0. Fixtures F1 (optional, empty) and F2
(required, minimum length).

### 3.7 Validation error codes (stable)

`CHOICE_REQUIRED`, `UNKNOWN_OPTION`, `DUPLICATE_OPTION`, `TOO_FEW_SELECTED`, `TOO_MANY_SELECTED`,
`EXCLUSIVE_OPTION_CONFLICT`, `OTHER_TEXT_REQUIRED`, `OTHER_TEXT_TOO_SHORT`, `OTHER_TEXT_TOO_LONG`,
`OTHER_TEXT_NOT_ALLOWED`, `TEXT_REQUIRED`, `TEXT_TOO_SHORT`, `TEXT_TOO_LONG`.

---

## 4. Sequential multi-select follow-up queue contract

```json
{"mode": "SEQUENTIAL_FOLLOWUPS",
 "followups":  [{"option": "PREMIUM",  "priority": 10, "nodes": ["n-prem"]},
                {"option": "BENEFITS", "priority": 20, "nodes": ["n-cover"]},
                {"option": "CLAIMS",   "priority": 30, "nodes": ["n-cover"]}],
 "no_followup": ["NONE"],
 "interrupts": [{"option": "CRITICAL_RISK", "priority": 1, "outcome": "ESCALATE"}],
 "order": "PRIORITY_THEN_OPTION_ORDER",
 "dedupe": "ONCE_PER_ANSWER",
 "rejoin": {"node": "n-confirm"},
 "empty_fallback": {"node": "n-confirm"}}
```

### 4.1 Authoring rules (validator)

- Every option of the set must appear in exactly one of `followups`, `no_followup` or `interrupts` — an option with
  no declared behaviour is an error (`FOLLOWUP_MAPPING_MISSING`).
- Follow-up targets are nodes of the **same module** with `"role": "FOLLOWUP"`. A follow-up node's edges may only go
  to `{"return": true}` or to an outcome. It may not be reached by an ordinary edge, and may not itself be a
  `SEQUENTIAL_FOLLOWUPS` question in P0 (no nested queues).
- `rejoin` and `empty_fallback` are mandatory and must be a node that is not a follow-up, or an outcome.
- Priorities within `followups` are unique; within `interrupts` unique.
- P0 follow-up targets are single question nodes; reusable follow-up *sets* are P1 (SS-MOD-013).

### 4.2 Execution (one cursor, never parallel)

1. Validate the selection (§3.4, §3.5). Record the answer.
> **Superseded in part by D-122 (2026-11-21):** three policies — `STOP_ESCALATE`, `RESUME`, `STOP_REJOIN` — and an
> interruption class on each answer option (prohibited / `OPTIONAL` / `MANDATORY`) that limits what a placement may
> choose; a mandatory escalation takes precedence over any other interruption. See the decision register.

2. **Interrupts.** Each interrupt carries an explicit policy (owner decision D-119, 2026-11-21):
   - `STOP` — emit its outcome, run no follow-ups, and trace the items that would have run (`skipped`). If several
     selected options are `STOP` interrupts, the one with the lowest priority number wins.
   - `RESUME` — ask the interrupt's own question first, then continue with the queue in its configured order.
   The policy is always stated on the interrupt; there is no implied default. (SS-01 originally proposed stop only.)
3. **Build the queue.** Take the `followups` entries whose option is selected; order by `priority`, then by the option
   set's declared `order`. Click order and set iteration order never matter.
4. **Dedupe** (`ONCE_PER_ANSWER`): concatenate the entries' nodes, keeping the first occurrence of each node and
   tracing later ones as `deduped`.
5. **Persist** the queue, the cursor (0) and the cause of each item (which option enqueued it) in the run.
6. **Execute serially.** Ask the node at the cursor. When it resolves to `{"return": true}`, advance the cursor.
   If it resolves to an outcome, that outcome ends the module immediately (an approved early exit) and the remaining
   items are traced as `skipped`.
7. **Rejoin exactly once**: after the last item, go to `rejoin`. If the queue was empty, go to `empty_fallback`.

### 4.3 Behaviour under other events

| Event | Behaviour |
|---|---|
| Pause / resume mid-queue | Resume at the stored cursor on the pinned version; nothing is repeated or skipped (SS-AT-044) |
| Back/Edit of the multi-select answer | The old answer and every answer given to its follow-ups are superseded; the queue is rebuilt from the new selection; an audit event records both (SS-AT-043) |
| Back/Edit of a follow-up answer | Only that answer is superseded; the queue and cursor order are unchanged |
| Non-answer (`UNCLEAR`, `REFUSED`) on a follow-up | Existing re-prompt rules; if unresolved, the node's `on_unresolved` policy: `CONTINUE_QUEUE` (default) or a named outcome |
| Lifecycle stop | Ends the run by precedence 1; remaining items traced as not executed |

Fixture F4 exercises steps 2–7: configured order beats click order, two options sharing one follow-up, an interrupt,
the empty queue, and two rejected selections.

---

## 5. Typed condition representation

### 5.1 Condition Version

```json
{"code": "C-ENHANCED-REVIEW", "version": 1,
 "summary": "Age is at least {minimum_age} AND (annual premium is above {premium_threshold} OR risks were not understood)",
 "params": {"minimum_age": {"type": "INTEGER", "unit": "years"},
            "premium_threshold": {"type": "MONEY", "unit": "SGD"}},
 "inputs": {"risk_understood": {"type": "OPTION_CODE", "option_set": {"code": "OS-YES-NO", "version": 1}}},
 "fields": ["customer.age_years", "policy.annual_premium"],
 "ast": {"op": "AND", "args": [
   {"op": "GTE", "left": {"field": "customer.age_years"}, "right": {"param": "minimum_age"}},
   {"op": "OR", "args": [
     {"op": "GT", "left": {"field": "policy.annual_premium"}, "right": {"param": "premium_threshold"}},
     {"op": "EQ", "left": {"input": "risk_understood"}, "right": {"literal": "NO"}}]}]}}
```

**Grammar.** A node is a group — `{"op": "AND" | "OR", "args": [node, …]}` (2+ arguments),
`{"op": "NOT", "arg": node}` — or an atom `{"op": <comparison>, "left": operand, "right": operand}`.

**Operands.** `{"field": "<catalog code>"}`, `{"param": "<name>"}`, `{"input": "<name>"}`, `{"literal": <value>}`.
A condition never names a question, node or module directly: answers and module outcomes enter only through **named
inputs**, mapped by the binding. That is what makes a condition reusable across modules.

**Operators by type.**

| Type | Operators |
|---|---|
| `INTEGER`, `DECIMAL`, `MONEY`, `DATE` | `EQ`, `NEQ`, `GT`, `GTE`, `LT`, `LTE`, `IN` (list) |
| `ENUM`, `OPTION_CODE`, `OUTCOME_CODE`, `STRING` | `EQ`, `NEQ`, `IN` |
| `BOOLEAN` | `EQ`, `NEQ` |
| `OPTION_CODE_SET` (a multi-select answer) | `CONTAINS`, `CONTAINS_ALL`, `CONTAINS_ANY` |
| any | `IS_KNOWN` (the only operator that returns TRUE/FALSE on a non-known operand) |

Type rules are checked at authoring time: both sides must have the same type; `MONEY` must agree in currency and
other quantities in unit; a literal must parse as the type. Money and decimals are compared exactly as decimals,
never as floating point (F6: premium exactly 12,000 against `GT 12,000` is FALSE).

**No executable content.** No SQL, expressions, scripts, model calls or references to other conditions in P0.
Limits: depth ≤ 6, ≤ 50 nodes, list literals ≤ 100 items (SS-NFR-018; values to confirm).

### 5.2 Condition Binding

```json
{"condition": {"code": "C-ENHANCED-REVIEW", "version": 1},
 "params": {"minimum_age": 60, "premium_threshold": 12000},
 "inputs": {"risk_understood": {"answer": {"node": "n1"}}},
 "unknown_policy": "ROUTE_UNKNOWN"}
```

| Binding context | Where | Input sources allowed | UNKNOWN policies allowed |
|---|---|---|---|
| Module entry | `instance.entry` | catalog fields; answers and outcomes of **earlier** instances (`{"answer": {"instance", "node"}}`, `{"module_outcome": {"instance"}}`) | `BLOCK`, `SKIP_WITH_REASON` |
| Internal decision | a `DECISION` node | catalog fields; answers of nodes that **dominate** the decision in the same module | `ROUTE_UNKNOWN` (an `UNKNOWN` edge is then mandatory), `BLOCK` |
| Question applicability | a question node | as internal decision | `ASK` (treat as applicable), `BLOCK` |
| Ordered multi-select rule | `ORDERED_RULES.when` | the selection itself | not applicable (a recorded selection is always known) |

There is **no global default** for UNKNOWN (SS-D-07): a binding without a policy is a validation error.
`SKIP_WITH_REASON` is not allowed on a module that contains a mandatory question.

> **Superseded 2026-11-21 by §5.4 (d) (owner decision D-132):** an answer asked on *some* routes may also be read; the
> paragraph below is kept as the original SS-01 text.

**Availability rule (SS-RUL-011).** An input may reference an answer only if every path to the binding passes through
that question (it dominates the binding). Otherwise the validator reports `DEPENDENCY_NOT_AVAILABLE` with the paths
that miss it. A dominated answer can still be a non-answer at run time; that yields UNKNOWN, handled by the policy.

### 5.3 Evaluation: three values

Operand state: `KNOWN`, `UNKNOWN` (absent, not yet captured, or a non-answer), `NOT_APPLICABLE`, `CONFLICTING`
(sources disagree). Any comparison with a non-`KNOWN` operand is **UNKNOWN**. Groups use Kleene logic:

| | Result |
|---|---|
| `AND` | FALSE if any argument is FALSE; else UNKNOWN if any is UNKNOWN; else TRUE |
| `OR` | TRUE if any argument is TRUE; else UNKNOWN if any is UNKNOWN; else FALSE |
| `NOT` | TRUE↔FALSE; UNKNOWN stays UNKNOWN |

So a missing value produces UNKNOWN **unless a known operand already decides the result** — and is never silently
read as false. Fixture F6 shows all the cases: `FALSE AND UNKNOWN = FALSE`, `TRUE AND (UNKNOWN OR FALSE) = UNKNOWN`,
`TRUE AND (UNKNOWN OR TRUE) = TRUE`; F8 shows the same at module entry with two different policies.

**Determinism.** Evaluation is a pure function of (condition version, binding, snapshot of operand values). The
values used, their sources and the result of every atom are recorded as the explanation tree (Part B §9.3). A later
change to a fact never replays an executed step (PRD §5.4).


### 5.4 Amendments of 2026-11-21 (owner corrections and decisions D-125, D-127, D-129, D-131)

These amend §5.1–§5.3. Where they differ from the text above, **this section governs**.

**(a) Answer inputs are stable, typed references (D-131).** A condition must not depend on any mutable display
text. An input declaration names the answer by identity and type:

```json
"inputs": {"risk_understood": {
   "kind": "ANSWER",
   "question": {"code": "Q-RISKS-UNDERSTOOD", "version": 1},
   "answer_type": "YES_NO",
   "value_type": "OPTION_CODE",
   "scope": "MODULE"}}
```

| Field | Meaning |
|---|---|
| `question.code` | The stable identity of the Question the answer belongs to. Never its wording, intent text or display number |
| `question.version` | The pinned Question Version whose option codes the condition's literals were written against |
| `answer_type` / `value_type` | `YES_NO` and `SINGLE_SELECT` → `OPTION_CODE`; `MULTI_SELECT` → `OPTION_CODE_SET`; free text is not a condition input in P0 |
| `scope` | `MODULE` (a question instance in the same module) or `SURVEY` (an earlier module instance; module entry only) |

Literals compared with an answer are **option codes** (or lists of codes), never labels. The earlier form
`{"type": "OPTION_CODE", "option_set": …}` is superseded: an option set alone does not identify which answer is read.

The binding maps the declaration to a **question instance** by its execution identity (§1.3):
`"inputs": {"risk_understood": {"answer": {"node": "n1"}}}` in a module, `{"answer": {"instance", "node"}}` at survey
scope. Validator rules (all blockers):

| Code | Raised when |
|---|---|
| `INPUT_UNBOUND` | A declared input has no binding, or its bound node no longer exists |
| `INPUT_QUESTION_MISMATCH` | The bound node is a placement of a different Question code than the one declared |
| `INPUT_TYPE_MISMATCH` | The bound Question Version's answer type differs from the declared `answer_type` |
| `INPUT_CODE_UNKNOWN` | The condition compares the input with an option code that the bound Question Version does not have |
| `DEPENDENCY_NOT_AVAILABLE` | The bound question is not asked before the binding on any route (see (d)) |

A bound placement may pin a later Question Version than the one declared, provided none of the rules above fires;
option codes are stable across versions, so renaming an option or rewording the question changes nothing.

**(b) Missing versus empty (D-125, D-131).** For an `OPTION_CODE_SET` input there are three distinct states:
*not answered* (the question was not reached, or the turn ended as a non-answer) → the operand is **UNKNOWN**;
*answered with an empty selection* (only possible when `selection.min` is 0) → a **KNOWN** empty set; *answered* → a
KNOWN set. An unanswered input is never coerced to the empty set. In particular `CONTAINS_NONE` over an unanswered
input is UNKNOWN, not TRUE.

**(c) Set operators (D-125).** For `OPTION_CODE_SET`: `CONTAINS_ANY` (at least one listed code is selected),
`CONTAINS_ALL` (every listed code is selected), `CONTAINS_NONE` (no listed code is selected); the right operand is a
list of option codes. `CONTAINS` (one code) is `CONTAINS_ANY` with a one-item list. The prototype spells these
`INCLUDES_ANY` / `INCLUDES_ALL` / `INCLUDES_NONE`; the canonical names are the ones in this section.

**(d) Availability (decided by the owner, 2026-11-21, D-132). This replaces SS-RUL-011 in §5.2.** A condition on a
`DECISION` node may read an answer from the **same module** when the question

- is asked on **every** route to the decision (*guaranteed*), or
- is asked on **at least one** route to the decision (*possible*).

A condition that reads a question which **cannot** have been executed before the decision — it lies after the decision
on every route, in an unreachable part of the graph, or was removed — is **invalid**: `DEPENDENCY_NOT_AVAILABLE`
(blocker). The authoring surface must show, for each readable answer, whether it is guaranteed or only possible.

Because a *possible* answer may be absent on the executed route, **explicit UNKNOWN handling is mandatory** on every
binding that reads an answer (§5.2: no global default). An answer not collected on the executed route evaluates
**UNKNOWN — never FALSE, and never an empty selection**.

**(d-1) Evidence states (D-132).** The trace of a run records, for every answer a condition read and for every
question of every module that ran, exactly one of:

| State | Meaning | As an operand |
|---|---|---|
| `ANSWERED` | The question was asked and a valid answer recorded | KNOWN |
| `ANSWERED_EMPTY` | Asked, and a valid answer with **no option selected** was recorded (multi-select with `selection.min` 0) | KNOWN, the empty set |
| `UNANSWERED` | Asked, and no answer content was given where none is required (an optional free-text answer left blank), or the turn ended as a non-answer | UNKNOWN |
| `SKIPPED` | **Not asked on the executed route** (a branch not taken, a queue not entered, a module that did not run) | UNKNOWN |

These four are never merged. In particular `SKIPPED` and `UNANSWERED` are different facts about a call, and neither
is `ANSWERED_EMPTY`.

**(e) Stop and flag for review (D-127).** `BLOCK` is a governed result named **`REVIEW_REQUIRED`**: automated
progression halts at that point, the run is **pending authorised review**, and it is **not** completed. On a
`DECISION` node it is carried as the `UNKNOWN` edge to the outcome `REVIEW_REQUIRED`; at module entry it is the
entry binding's policy. `REVIEW_REQUIRED` is not an ordinary routable outcome: it is not offered as a destination for
answers, and a survey cannot route a module's `REVIEW_REQUIRED` to another module or to a different survey outcome —
it always halts the survey with `REVIEW_REQUIRED`. How a reviewer resumes or closes such a run is runtime governance
(a later checkpoint), not part of the survey graph.

**(f) Version upgrades of a shared condition (D-129).** A new Condition Version never propagates. Each consumer
(module entry binding or decision node) is upgraded by an explicit, separately authorised change to that consumer,
recorded with the consumer's own revision; consumers that are not upgraded keep the version they pin.


**(g) Controlled outcome catalog (D-133).** Outcomes are a governed catalog of **stable codes**, each with an explicit
**classification**. No classification is implied by wording or by another classification.

| Class | Meaning | Prototype catalog (synthetic) |
|---|---|---|
| `NORMAL_COMPLETION` | The module or survey finished normally | `COMPLETED` |
| `EXCEPTION` | A named non-normal ending. **Not** an escalation | `CLARIFICATION_REQUIRED`, `CUSTOMER_DECLINED`, `UNABLE_TO_VERIFY` |
| `ESCALATION` | A valid destination for a mandatory escalation (§3.4) | `ESCALATE` — **the only one** |
| `REVIEW_HALT` | Governed halt, (e) above; not author-routable | `REVIEW_REQUIRED` |

`REVIEW_REQUIRED` and the exception outcomes are **not equivalent to escalation**: a mandatory-escalation option that
leads to any of them fails `MANDATORY_ESCALATION_BYPASSED`. The business-approved catalog — its codes, labels and
classifications, and who may change them — is **deferred to production governance approval**; the list above is for
the prototype only.

**(h) Review-required halts (D-134).** `REVIEW_REQUIRED` halts automated progression. The run's status is **pending
review**; it is not completed, and no later module, route or survey outcome is evaluated. **Resume, close and
resolution are not part of the survey graph**: they require a separately authorised review / operations capability
with explicitly permitted transitions and complete audit evidence (who, when, on what basis, with which result). None
of that is specified or built here; the prototype only shows the halt, with synthetic data and no runtime record.


### 5.5 Open requirement: a question that is not answered (recorded 2026-11-21; **not specified, not built**)

> **2026-11-21 (SS-02C, D-142):** the decision-ready contract for this requirement is
> `17_SS-02C_NO_ANSWER_CONTRACT.md`. It supersedes the table below as the working document; the table is kept as the
> original record. Still nothing is specified as final and nothing is built.

Real insurance callbacks need defined behaviour when the customer does not answer a question. **None of the
following is specified by SS-01, implemented in the prototype, or to be assumed by any implementation.** The
prototype has no "no answer" turn; its only related evidence state is `UNANSWERED` for an optional free-text answer
left blank (§5.4 (d-1)).

| # | Requirement to be decided | Why it cannot be invented here |
|---|---|---|
| NA-1 | **Silence / timeout**: how long, measured from what (end of the question's delivery?), and what a timeout is recorded as | Timing belongs to the voice channel and its latency; a compliance view is needed on what counts as "did not answer" |
| NA-2 | **Customer refusal**: an explicit "I prefer not to say" — is it an answer, a non-answer, or its own state? For which questions is refusal acceptable? | Mandatory-disclosure and verification questions are unlikely to tolerate refusal the same way |
| NA-3 | **Retry and repeat limits**: how many re-asks or rephrasings per question and per call; whether a repeat must use the approved wording verbatim | Approved-wording rules (SS-D-02) and customer-experience limits are business decisions |
| NA-4 | **Escalation or termination policy** when the limits are reached: per question, per module, or per survey; to which catalogued outcome | Needs an outcome class in the governed catalog (§5.4 (g)); it must not silently become `COMPLETED`, an exception or an escalation |
| NA-5 | **Explicit evidence** that a question was not answered: attempts, timestamps, the delivery that was made, the reason (silence, refusal, line drop, unintelligible) | Evidence must distinguish "not answered" from `SKIPPED` and from `ANSWERED_EMPTY`; the fourth state `UNANSWERED` exists but its sub-reasons do not |
| NA-6 | **Routing of a non-answer**: a route key (for example `NO_ANSWER`) on question nodes, required or defaulted? What a condition reads (today: UNKNOWN) | A new route key changes the edge contract of §2.1 and the "specific → ANY → blocked" resolution |
| NA-7 | **Interaction with mandatory questions, follow-up queues and mandatory escalation**: can a queue continue past an unanswered follow-up; can a non-answer to a mandatory-escalation question end otherwise | Precedence rules (§2.3) must place non-answers explicitly |
| NA-8 | **Lifecycle events** that look like non-answers but are not (call dropped, customer asks to be called back, agent takeover) | Owned by the conversation lifecycle (SS-D-08), above the survey graph |

**Contract decisions needed before backend implementation (SS-03 / SS-04):** (1) the evidence model for an unanswered
question — states, reasons, attempts; (2) whether non-answer is a route key, a node-level policy or a lifecycle
event, and its place in §2.3; (3) retry limits and who sets them (question, module, survey or channel); (4) the
catalogued outcome(s) for "could not obtain an answer"; (5) what conditions and module eligibility read for a
non-answer; (6) golden fixtures for each. Until then an executor that reaches a question it cannot get an answer to
has **no defined behaviour**, and must not guess one.

---

## 6. Shared-question identity, reuse, versioning and evidence (SS-D-09 as decided)

### 6.1 The rule

> **R-4.** A Question Definition may be placed any number of times: in several modules, in modules used by the same
> survey, and in a module that is itself placed more than once. Every placement is a distinct **Question Instance**
> with its own key `{instance}/{node}`, its own routing and its own evidence. No restriction "once per survey"
> exists. (The SS-00 proposal to restrict this is withdrawn.)

What stays unique: a node code within a module version; an instance code within a survey version. Therefore the
Question Instance key is unique within a survey version by construction — including when the same module version is
placed twice (`mi-a/n2` and `mi-b/n2`).

### 6.2 Versioning and pinning

- A node pins `question {code, version, wording_version}`. Two placements may pin **different** versions of the same
  definition; each is evaluated against the version it pins.
- A new Question Version or Wording Version never reaches a placement by itself. The consumer's draft offers
  `Upgrade` (with impact preview), `Keep pinned` or `Fork` (SS-D-03).
- Changing an option code set or the answer type is a **breaking** structural change: it needs a new Question Version
  and invalidates wording bound to the old structure (Part B §7.3).

### 6.3 Answer evidence

One record per executed Question Instance occurrence:

```json
{"question_instance": "mi-risks/n2", "occurrence": 1,
 "module_instance": "mi-risks", "node": "n2",
 "module": "M-RISKS@1",
 "question": "Q-UNDERSTOOD@1",
 "wording": "Q-UNDERSTOOD/en/1",
 "answer": {"kind": "ANSWER", "answer_type": "YES_NO", "choice": "NO"},
 "supersedes": null,
 "provenance": {"source": "SIMULATION", "actor": "…", "at": "…"},
 "survey": "S-SHARED-QUESTION@1.0", "manifest_sha256": "…"}
```

For choices: `"choice"` or `"choices"`, plus `"other": {"option_code": "OTHER", "text": "…"}` only when the Other
option is selected. Codes and text are separate fields (SS-QUE-025). Fixture F7 shows two records for
`Q-UNDERSTOOD@1` with different instance keys and different answers; F5 shows the Other shape.

### 6.4 How the existing evaluation and findings infrastructure accommodates instances

**Fact (inspected).** Today the answer-evaluation rule map and results are keyed by `question_code`
(`answer_evaluation.py` `rules_of`, results rows), findings are generated per `question_code` with a deterministic
`finding_key` that includes it (`finding_engine.py`), finding rules have scopes `QUESTION` (target = question code),
`CONTROL` and `ANY_QUESTION`, and the authoring validator rejects a duplicate question code in one version. With two
placements of one definition, a map keyed by code would silently keep only one. So the key must be widened — the
engines' *logic* does not need to change.

**Contract: the execution key.**

| Manifest | `execution_key` of a question | Effect |
|---|---|---|
| `/2` (legacy linear) | = `question_code` | Every existing run, evaluation result and `finding_key` is byte-for-byte unchanged |
| `/3` (graph) | = Question Instance key `{instance}/{node}` | Two placements never collide |

`question_code` and the pinned `question_revision` remain on every record as attributes, so everything that reports
or filters by question keeps working.

**Required future extensions (not done in SS-01; scheduled with the phases that need them):**

| Component | Extension | Phase |
|---|---|---|
| Controller state | Item state and action ids keyed by `execution_key` instead of code (`"{execution_key}#{attempt}"`) | SS-04 |
| Answer evaluation | Rule map and result rows keyed by `execution_key`; each result also carries `question_code`, `question_instance`, `module_instance` | SS-04 (simulation) |
| Finding engine | `finding_key` built from `execution_key`; findings carry the instance. One finding per failing **instance**, so the same question failing in two places yields two findings | SS-04 (simulation) |
| Finding rules | Scope `QUESTION` keeps its meaning — it targets the **definition** and applies to every instance of it. `CONTROL` and `ANY_QUESTION` unchanged. An optional scope `QUESTION_INSTANCE` is a later extension, only if a business rule ever needs to treat one placement differently | none needed in P0 |
| Scenario steps and expectations | A step may name a question code when it is unique in the version; when it is not, the instance key is required (validator message says so) | SS-04 |
| Authoring validator | `DUPLICATE_QUESTION` applies to `/2` drafts only; for graph drafts the uniqueness rule is on node codes | SS-03 |
| Operational evidence (`question_execution`, `answer_observation`, `rule_evaluation`) | Additive columns for module instance, node and occurrence. `question_execution.position` is already unique per run and remains the execution order | SS-09 |
| Review readiness and dossier | Read per instance; a lifecycle role must be satisfied by the instance that carries it | SS-09 |

**Guard against unintended repetition (the owner's condition).** R-2 is enforced three ways: the validator rejects
cycles; the queue dedupes; and the engine refuses to issue an action for an instance whose current occurrence is
already resolved (`REPEATED_EXECUTION`, exercised by the reference interpreter).

**Decided by the owner (D-115, 2026-11-21).** Findings are raised **per executed placement**: when one definition
fails in two placements there are two findings, each pointing at exactly one piece of evidence. Each finding has a
stable identifier derived from (run, rule set, rule, question instance, trigger), so generating findings again for
the same run yields the same identifiers and no duplicates. The interface may group related findings (for example by
question definition) for reading; grouping never merges the underlying audit records.

---

## 7. Amendment of 2026-11-21 (UC-01): statements, number and acknowledgement items, wording delivery, controlled variables, call plan

**Authority:** owner decisions D-155…D-160. **Status:** as built in the prototype; items marked *proposed* are
prototype decisions P-13…P-22 awaiting confirmation. Nothing in §1–§6 changes meaning. Schemas `/1`–`/4` and their 19
fixtures are unchanged: none of them contains any element defined here.

### 7.1 One item master; a statement is an item, not a question

The Question definition of §1.2 is generalised to an **Item**. Every item has an identity, versions, a pinned Wording
Version, sharing and reuse exactly as before. Its `answer_type` now takes seven values:

| `answer_type` | What it is | Answer | Routing |
|---|---|---|---|
| `YES_NO`, `SINGLE_SELECT`, `MULTI_SELECT`, `FREE_TEXT` | As §3 | As §3 | As §2 |
| `NUMERIC` | A question answered with a number | `{"number": n}` checked against `number_rule {integer, min?, max?, unit?}` | Exactly one route, `AFTER_CAPTURE` |
| `ACKNOWLEDGEMENT` | A question the customer acknowledges | `{"acknowledged": true}` | Exactly one route, `AFTER_CAPTURE` |
| `STATEMENT` | **Not a question.** Approved wording that is delivered | None | Exactly one route, `AFTER_CAPTURE` |

A node that places an item is `{"id", "type": "QUESTION" | "STATEMENT", "q": {code, version}, "routing"}`.
**Invariant:** `type = STATEMENT` if and only if the item's `answer_type = STATEMENT`; violating it is a validation
error. A statement declares `statement: OPENING | TRANSITION | DISCLOSURE | CLOSING`. The role changes no routing.

Stable rejection codes added to §3.7: `NUMBER_REQUIRED`, `NUMBER_NOT_WHOLE`, `NUMBER_TOO_LOW`, `NUMBER_TOO_HIGH`,
`ACKNOWLEDGEMENT_REQUIRED`. "The customer does not acknowledge" is a **non-answer**, not an answer value; its
handling is §5.5 and undecided.

**Not yet defined (proposed P-20):** reading a `NUMERIC` or `ACKNOWLEDGEMENT` answer in a condition, and routing on
a number.

### 7.2 Declared attributes of a question

`mandatory: boolean` and `role: IDENTITY_CHECK | CONSENT_TO_PROCEED | RECORDING_CONSENT | CLOUD_PROCESSING_CONSENT`
(yes/no questions only) are carried on the item version and into the content document. **They are declarations.**
What an executor does when a mandatory question, an identity check or a consent is not answered, or is answered
"no", is **not specified here**: routing does only what the author routed. The existing lifecycle's on-failure rules
are development assumptions pending a business decision and are neither confirmed nor reproduced by this section.

**Live eligibility (owner condition D-67), structural only:** a survey is structurally eligible for live calls only
if it contains a mandatory `IDENTITY_CHECK`, a mandatory `CONSENT_TO_PROCEED` and a mandatory `RECORDING_CONSENT`.
The check reports; it never makes a survey eligible.

### 7.3 Wording Version: delivery mode

`wording {version, text, approval, delivery}` with `delivery: CONTROLLED_TTS | EXACT_AUDIO | CONVERSATIONAL`.

| Mode | Rule | Validation |
|---|---|---|
| `CONTROLLED_TTS` | Exactly the rendered text is synthesised. *Proposed default when unset (P-16)* | — |
| `EXACT_AUDIO` | An approved recording is played | Warning: no asset can be attached yet. **Error if the wording contains a variable** |
| `CONVERSATIONAL` | Undefined | **Error — blocked** until what an assistant may say in its own words is decided (G-6 AD-9) |

### 7.4 Controlled variables

- **Syntax.** `{{field_code}}` inside the wording text. `field_code` names exactly one field of the governed field
  catalog. No expression, arithmetic, default or nesting.
- **Authoring errors.** `UNKNOWN_VARIABLE`; `TYPE_NOT_ALLOWED` (a yes/no fact has no spoken form); `MALFORMED`.
- **Rendering is a pure function** of (wording text, fact snapshot): one fixed format per type — money as
  `<unit> <grouped digits>[.cc]`; integer as grouped digits; enumerated value as its display form; text as given.
  No locale lookup. *The formats are prototype formats; how a value is to be spoken is undecided (AD-8).*
- **Missing or unusable value.** Each variable resolves to `PRESENT`, `MISSING` or `INVALID`. If any is not
  `PRESENT` the wording **is not delivered**: nothing is defaulted, omitted or improvised. In execution the run ends
  in terminal state `MISSING_INFORMATION_HALT` with reason `WORDING_VALUE_MISSING`.
- **Evidence.** A delivery record per item: `{item_instance, item, wording_version, delivery, text (as rendered),
  values[{variable, value, state}], statement}`.

### 7.5 Execution

A `STATEMENT` node is **delivered**, not asked: it consumes no answer, appears in `deliveries` and never in `asked`,
and continues by its single route. Evidence state `DELIVERED` is added beside `ANSWERED`, `ANSWERED_EMPTY`,
`UNANSWERED`, `SKIPPED`. Loop protection counts every delivered item, statements included. The six terminal states
are unchanged.

### 7.6 Call plan (preview)

`plan(version, facts) → call plan`, a pure function over the same model the executor runs:

```json
{"survey": "...", "status": "READY | BLOCKED", "blockers": ["..."],
 "inputs":  [{"code": "policy.annual_premium", "state": "PRESENT | MISSING | INVALID", "value": "SGD 3,000", "usedBy": ["..."]}],
 "modules": [{"instance": "mi-…", "status": "IN | OUT | CONDITIONAL | HALTS", "why": "...",
              "items": [{"key": "mi-…/n4", "statement": true, "role": "DISCLOSURE", "delivery": "CONTROLLED_TTS",
                         "source": "…{{policy.annual_premium}}…", "text": "…SGD 3,000…", "certainty": "ALWAYS | SOME"}],
              "open":  [{"kind": "ANSWER | CONDITION | OUTCOME", "title": "...", "alternatives": [{"when": "...", "leads": "..."}]}]}],
 "hash": "..."}
```

- A module is `IN` or `OUT` only from application data: eligibility is evaluated three-valued; `UNKNOWN` follows the
  binding's stated policy (`SKIP_WITH_REASON` → `OUT`; `BLOCK` → `HALTS`). A module with an activation trigger is
  `CONDITIONAL`.
- `certainty = ALWAYS` when every path through the module passes through the item; otherwise `SOME`.
- **Open points are enumerated, never resolved.** The plan lists the alternatives at every answer-dependent route,
  every decision and every module ending. It contains no answers and no chosen path.
- `BLOCKED` when any item a call could reach cannot be rendered, or any module `HALTS`.
- **The plan is not the dialogue.** What was delivered and answered exists only in a run (§7.5).

### 7.7 Not specified here — blocked, not invented

Repeat counts; response timeouts; refusal handling; consent and identity gate behaviour; clarification and repeat
wording; conversational wording; the spoken form of variable values; variables in recordings; evaluation and control
configuration (interface contract only, `21_UC-01_CONSOLIDATION_MAP.md` §4).

---

## 8. Amendment of 2026-11-21 (UC-02): schema /5, corrected delivery rules, plan and eligibility kept apart

**Authority:** owner decisions D-161…D-169. **Normative for** fixtures K1–K8 (`call360.survey-studio.fixture/5`) and
`fixtures/reference_interpreter_v5.py`, which was written from this section and §7 and shares no code with the
prototype. Where this section differs from §7, this section governs. Schemas /1–/4 are unchanged.

### 8.1 Corrections to §7

| §7 said | Now |
|---|---|
| `EXACT_AUDIO` without an asset: a warning | **An error, `RECORDING_ASSET_MISSING`.** A recording with no usable, approved asset cannot be delivered, so it blocks. `EXACT_AUDIO` requires `asset {id, sha256, approval}`; no fixture and no prototype item can carry one |
| An acknowledgement not given: `ACKNOWLEDGEMENT_REQUIRED` | An explicit `{"acknowledged": false}` is rejected with **`NON_ANSWER_POLICY_UNRESOLVED`**: blocked as unresolved policy. It is never an answer value, a refusal or a default, and the run stays pending at that question. An absent or other-kind answer remains `ACKNOWLEDGEMENT_REQUIRED` |
| An unfinished variable: an authoring error only | Also **undeliverable at execution**: it resolves to state `MALFORMED` and the item is not delivered. It is never spoken with its braces |
| Money and integer formats | **Exact.** A whole-number field holding a fraction, or an amount with more than two decimal places, is `INVALID`. Nothing is rounded or truncated |
| Display numbers Q1, Q2 … for every item | A statement is labelled **S1, S2 …** and never takes a question number. Labels are for display only: the identity of a step is its node id, and of a placement `<instance>/<node>` |

### 8.2 Item and node rules (K1, K2, K7)

- A node `{node, type: QUESTION | STATEMENT, item {code, version, wording_version}, routing {mode}}` places one item.
- `type = STATEMENT` if and only if the item's `answer_type = STATEMENT`.
- A `STATEMENT`, `NUMERIC`, `ACKNOWLEDGEMENT` or `FREE_TEXT` item has routing mode `ALL_TO_NEXT` and at most one
  outgoing edge, on `AFTER_CAPTURE`.
- A statement is not mandatory and has no question role.
- The same item may be placed any number of times, in one module and across placements of a module. Each placement
  is a separate execution with its own key, delivery record and answer.

### 8.3 Execution (K1, K3, K4, K5, K7, K8)

1. For each module instance in sequence, eligibility is evaluated three-valued from the facts: `TRUE` runs it; `FALSE`
   → `SKIPPED_FALSE`; `UNKNOWN` → `SKIPPED_UNKNOWN` when the policy is `SKIP_WITH_REASON`, otherwise
   `HALTED_MISSING_INFORMATION` and the run ends `MISSING_INFORMATION_HALT` / `ELIGIBILITY_UNKNOWN` at the instance.
2. Before an item is delivered its wording is rendered. If it cannot be, the run ends `MISSING_INFORMATION_HALT` /
   `WORDING_VALUE_MISSING` at the item; the module's status is `RUNNING` (started, no outcome).
3. A statement is delivered and execution continues by its single route. It is recorded in `delivered`, never in
   `asked`, and its evidence state is `DELIVERED`.
4. A question is delivered; each rejected answer is recorded with its code and the question stays current; an
   accepted answer is recorded and the route for it is followed (specific edge, then `ANY`, else `ROUTE_MISSING`).
   With no answer available the run is **pending** at that question: no terminal state.
5. A delivery record is `{key, item, statement, wording_version, delivery_mode, text, values[{variable, value,
   state}]}`. A question's record is written when its answer is accepted.
6. Evidence states at the end of a run, for every item of every module that started: `DELIVERED`, `ANSWERED`,
   `UNANSWERED` (an optional free text left empty), `SKIPPED` (the module ended without reaching it), `NOT_REACHED`
   (the module has no outcome yet).

### 8.4 Validation codes (K2, K6)

`NODE_ITEM_KIND_MISMATCH` · `STATEMENT_NOT_A_QUESTION` · `SINGLE_ROUTE_ITEM_BRANCHES` · `UNKNOWN_VARIABLE` ·
`VARIABLE_TYPE_NOT_ALLOWED` · `VARIABLE_MALFORMED` · `DELIVERY_CONVERSATIONAL_BLOCKED` · `RECORDING_ASSET_MISSING` ·
`RECORDING_WITH_VARIABLE` · `NUMBER_RULE_INVALID`. Each is an error at `<module code>/<node>`, reported in node order
and, within a node, in the order listed here. All block submission; none can be acknowledged.

### 8.5 The call plan (K1, K3–K8)

- `status`: `READY`, or `BLOCKED` when `issues` is not empty.
- `issues[{code, at}]`: `ELIGIBILITY_UNKNOWN` at an instance that `HALTS`; `WORDING_VALUE_MISSING` at an item that
  cannot be rendered.
- `modules[{instance, status}]`: `IN`, `OUT` (not eligible, or unknown and skipped) or `HALTS`. (`CONDITIONAL`, for a
  module with an activation trigger, is specified in §7.6 and is **not covered by a /5 fixture**.)
- `items{key → {statement, role, mandatory, delivery_mode, wording_version, text | null, values, certainty}}` for every
  item of every module that is not `OUT`. `certainty` is `ALWAYS` when every path from the module's entry to any
  ending passes through the item, otherwise `SOME`.
- `open{key → {kind, alternatives[{on, to}]}}`: `ANSWER` at a per-choice question whose answers do not all lead to
  the same place; `OUTCOME` at `<instance>:outcome` for a module with more than one outcome.
- `inputs{field → PRESENT | MISSING | INVALID}`: every field an eligibility condition reads, and every variable of
  the wording of a module that is not `OUT`.
- **Consistency.** For every run, each delivered item's text and values equal the plan's for that key.

### 8.6 Plan computability is not live-call eligibility

`plan` answers one question: can a plan be computed from these data. It may be computed from a draft, and it carries
no statement about use on a call. **Eligibility for an operational callback is a separate result** with explicit
conditions, each `MET`, `NOT_MET` or `NOT_AVAILABLE`:

| Condition | Group |
|---|---|
| A plan can be computed for this application | Plan |
| The plan is built from a published, approved version | Publication |
| Every item uses approved wording | Wording |
| Every item can be delivered as approved (no conversational delivery; every recording has an approved asset) | Wording |
| A mandatory identity check, a mandatory consent to proceed and a mandatory recording consent are **present** (D-67) | Gates |
| What each gate does when the customer says no, refuses or does not answer is approved (D-174) | Policy |
| An approved assignment selects this version for this case | Assignment |
| The requirements of the call channel are met | Channel |
| What a call does when a customer does not answer is decided | Policy |

Eligible means every condition is `MET`. **A gate condition is structural only:** it says the question exists, and is
reported as present or not present. **A gate being present never establishes that its enforcement is approved**: that
is the separate Policy condition above, which stays `NOT_MET` until the business and Compliance rule. What a call does
when the customer answers "no", refuses or does not answer is not specified here or anywhere.

### 8.7 Lifecycle states (owner decision AD-13)

Candidate: `IN_REVIEW`, `APPROVED`, `REJECTED`, `WITHDRAWN`, `SUPERSEDED`, `PUBLISHED`. Version: `SCHEDULED`,
`PUBLISHED`, `SUPERSEDED`, `WITHDRAWN`. `SCHEDULED` and version `WITHDRAWN` are states of the contract only: when a
scheduled version takes effect, and what withdrawal means for cases already assigned, are **not specified**.

### 8.8 Not covered by schema /5

Decisions, follow-up queues, rules, interruptions, jumps and activation triggers in combination with statements,
variables or the plan; any non-answer; repeat and clarification wording; evaluation and control evidence.

### 8.9 Clarifications of 2026-11-21 (owner decisions D-171, D-172) — proposed wording, no fixture changed

The amended wording of TS-2, TS-4, TS-7, TS-9, TS-10 and TS-12 is in `25_UC-02_DECISION_CLOSURE.md` §1.2. In terms of
this contract:

- §8.2: the single-route rule restricts the item node only; a Decision after such an item may read its answer in a
  later schema version.
- §7.3, §8.1: `CONVERSATIONAL` is not a publishable value. A draft may hold it; a candidate may not.
- §7.4, §8.1: every numeric field declares its precision; in schema /5 that is 0 for a whole number and 2 for money.
  A per-field declared precision and its rejection code belong to schema /6.
- §8.1, §8.3: an explicit non-acknowledgement is **evidence** — an observation that the customer did not
  acknowledge — and never a successful acknowledgement. In schema /5 it is the `rejections` entry
  `NON_ANSWER_POLICY_UNRESOLVED`. Its stored record belongs to schema /6.
- §5: version-1 conditions read yes/no and choice answers only; the restriction is explicit and extensible.
- §8.7: lifecycle states are **derived** from an append-only history of decisions; a candidate's content record is
  never updated.

**Schema /6 is reserved, not defined.** It will carry: a per-field `scale`; the `speakable` allowlist and its
validation code; the stored non-acknowledgement observation; a reserved non-answer resolution; the
`NON_ANSWER_EXCEPTION` outcome class. Each needs new fixtures and, for the last three, the corresponding
Business/Compliance rulings. Nothing in schemas /1–/5 changes.

---

## 9. Amendment of 2026-11-22 (SS-03A): the server's canonical documents, hashes, codes and lifecycle

**Authority:** owner decisions D-176…D-187. **Implemented in** `Call360-backend` `app/domain/survey/` (pure),
`migrations/versions/0027_survey_definitions.py` and `app/api/survey_definitions.py`. Schemas /1–/5 and their 27
fixtures are unchanged; the server reads each fixture under the rules of its own schema version.

### 9.1 Canonical form and fingerprints

- **Canonical bytes:** UTF-8; object keys sorted by code point; no insignificant whitespace; arrays in stored order;
  numbers without exponent and without trailing zeros, a whole value written as an integer; `null`, `true`, `false`
  as in JSON. **A value that is not a JSON value is refused, never converted.**
- **Fingerprint:** SHA-256 of the canonical bytes, lower-case hexadecimal.
- The pre-existing `digest.sha256_of` is **not** used for survey documents: it converts unknown types to text and
  may write a float with an exponent. It is unchanged and still serves the manifests it already hashes.

### 9.2 Document kinds and schema identifiers

| Kind | `schema` | Identity |
|---|---|---|
| Option set | `call360.survey.option-set/1` | `code`, `version` |
| Item | `call360.survey.item/1` | `code`, `version` |
| Wording | `call360.survey.wording/1` | `item`, `language` (`en`), `wording_version` |
| Condition | `call360.survey.condition/1` | `code`, `version` |
| Module | `call360.survey.module/1` | `code`, `revision` |
| Survey content | `call360.survey.content/1` | survey `code` |

A reader refuses a schema identifier it does not know (`DOCUMENT_SCHEMA_UNKNOWN`), an unknown field
(`DOCUMENT_FIELD_UNKNOWN`), a missing one (`DOCUMENT_FIELD_MISSING`), an invalid one (`DOCUMENT_FIELD_INVALID`) and
a repeated code (`DOCUMENT_DUPLICATE_CODE`). `delivery_mode` is a required field of a wording (TS-4).
`response_obligation` and `lifecycle_role` are two separate optional fields of an item (PB-5); the first is a code
of a governed catalog.

### 9.3 Manifest

Every asset version a survey content pins, directly or through a module: `{kind, code, version, sha256}`, sorted by
kind, code, version. `manifest_sha256` is the fingerprint of that list; `content_sha256` of the content document.
Verified when a candidate is created (built), decided and published (recomputed from the stored rows): each entry
exists, is frozen, and its stored content hashes to both its stored hash and the manifest's; and the manifest pins
exactly what the content refers to. Any difference is `MANIFEST_MISMATCH`: the action is refused and the refusal is
audited.

### 9.4 Validation code register

67 stable codes; a finding is identified by `code` and `at`, never by message. Each rule records the fixture schema
that introduced it; a fixture is read under the rules of its own version; the server applies all of them.

| Since | Codes |
|---|---|
| /1 (34) | `SURVEY_EMPTY` `MODULE_MISSING` `MODULE_EMPTY` `MODULE_ENTRY_MISSING` `NODE_UNREACHABLE` `MODULE_HAS_CYCLE` `TARGET_NODE_UNKNOWN` `OUTCOME_UNKNOWN` `OUTCOME_NOT_DECLARED` `ITEM_MISSING` `WORDING_MISSING` `WORDING_TEXT_MISSING` `OPTIONS_TOO_FEW` `OPTION_LABEL_MISSING` `ROUTE_MISSING` `REJOIN_MISSING` `DECISION_CONDITION_MISSING` `CONDITION_PARAM_MISSING` `CONDITION_INPUT_UNBOUND` `CONDITION_INPUT_NOT_AVAILABLE` `DECISION_ROUTE_MISSING` `DECISION_UNKNOWN_UNDECIDED` `CONDITION_FIELD_UNKNOWN` `CONDITION_PARAM_UNDECLARED` `CONDITION_OPERATOR_UNKNOWN` `CONDITION_EMPTY_GROUP` `CONDITION_OPERAND_INVALID` `SURVEY_ROUTE_MISSING` `SURVEY_ROUTE_TARGET_UNKNOWN` `SURVEY_ROUTE_BACKWARD` `ELIGIBILITY_CONDITION_MISSING` `UNKNOWN_POLICY_MISSING` `ACTIVATION_SOURCE_INVALID` `ACTIVATION_OUTCOMES_EMPTY` |
| /2 (19) | `SELECTION_LIMITS_INVALID` `RULE_EMPTY` `RULE_ROUTE_MISSING` `FALLBACK_MISSING` `FOLLOWUP_BEHAVIOUR_UNDECLARED` `INTERRUPT_NOT_PERMITTED` `INTERRUPT_OUTCOME_MISSING` `INTERRUPT_RESUME_EMPTY` `INTERRUPT_REJOIN_MISSING` `CONDITION_INPUT_WRONG_ITEM` `CONDITION_INPUT_TYPE_MISMATCH` `CONDITION_INPUT_OPTION_UNKNOWN` `CONDITION_INPUT_UNDECLARED` `CONDITION_INPUT_TYPE_UNSUPPORTED` `CONDITION_OPERATOR_TYPE_MISMATCH` `SKIP_DISPOSITION_MISSING` `SKIP_DISPOSITION_TARGET_UNKNOWN` `SKIP_DISPOSITION_BACKWARD` `MANDATORY_ESCALATION_WEAKENED` |
| /3 (1) | `MANDATORY_ESCALATION_OVERRIDDEN` |
| /4 (1) | `ESCALATION_NOT_TERMINAL` |
| /5 (10) | as §8.4 |
| approved mechanisms, no golden fixture yet (2) | `VARIABLE_NOT_PERMITTED` (default-deny, D-181) · `RESPONSE_OBLIGATION_UNKNOWN` |

`at` is `<module code>/<node>` for a finding in a module, `<instance>` or `<instance>:<outcome>` for one in a
survey (`:@SKIP`, `:@SKIP_SEQ` for the two skip dispositions), and `<code>@<version>` for one in a condition.

**How schemas /1 and /2 state an invalid draft.** They have no `validation` block. Fixture G3 is invalid on purpose
and says so through a run that ends `DRAFT_INVALID` with reason `SKIP_DISPOSITION_MISSING`; the server reports
exactly that code at `mi-specialist:@SKIP`.

### 9.5 Condition engine

As §5, with these points made explicit by the implementation: numeric comparison uses decimals, never floats;
`EQ` / `NEQ` compare numbers as decimals and everything else by identity; `INCLUDES_*` take a selection and a list
of option codes; a malformed condition is an **error** with a stable code (`CONDITION_OPERATOR_UNKNOWN`,
`CONDITION_OPERAND_NOT_NUMERIC`, `CONDITION_EMPTY_GROUP` …), never a three-valued result; every evaluation returns
an explanation tree listing each operand read. Verified against the 32 condition results the fixtures state
explicitly and the 12 eligibility results of fixture K8's plans.

### 9.6 Entities and lifecycle as stored

Draft (mutable, `revision` advances by exactly one) · asset version (`DRAFT` → `FROZEN`, then immutable) · candidate
(insert-only) · version (insert-only) · lifecycle event (append-only). **Status is derived from the newest event of
a subject and is stored nowhere.** Wording approval is a separate append-only row naming the wording's item,
language, version and hash, and the candidate (D-178); the wording row has no approval column.

Candidate events: `SUBMITTED` → `APPROVED` | `REJECTED` | `WITHDRAWN` | `SUPERSEDED`; `APPROVED` → `PUBLISHED` |
`WITHDRAWN` | `SUPERSEDED`. Version events: `PUBLISHED` (or `SCHEDULED` → `PUBLISHED`) → `SUPERSEDED` | `WITHDRAWN`.
`SCHEDULED` and version `WITHDRAWN` are accepted by the schema and are produced by nothing in SS-03A.

Identity rules, enforced by the service and again by a database trigger on the event table: an approver or rejecter
is not the submitter and not a maker; a publisher is not the submitter, not a maker and not the approver. A version
row can be inserted only for a candidate whose newest event is `APPROVED`.

### 9.7 Governed catalogs

`FIELD` (attributes: type, unit, values, `scale`, **`speakable`** — false on every entry), `OUTCOME` (attributes:
`class`, one of `NORMAL_COMPLETION`, `EXCEPTION`, `ESCALATION`, `REVIEW_HALT`, `NON_ANSWER_EXCEPTION`; label) and `RESPONSE_OBLIGATION`. A CHECK constraint admits no approval state
but `SYNTHETIC_UNAPPROVED`. The outcome class `NON_ANSWER_EXCEPTION` is admitted and has no entry. **No structured
non-answer resolution is stored anywhere**: the capability is reserved in this contract and has no field, route key
or behaviour (D-179).

### 9.8 API

Fifteen operations, `26_SS-03A_FOUNDATION_SPECIFICATION.md` §6, under `/api/v1/survey-definitions`,
`/survey-candidates`, `/survey-versions`, `/survey-library`, `/survey-conditions`. The draft operation vocabulary is
`PUT_ASSET`, `REMOVE_ASSET`, `SET_CONTENT`. Error codes: `STALE_DRAFT`, `VALIDATION_BLOCKED`, `DOCUMENT_INVALID`,
`OPERATION_INVALID`, `ASSET_FROZEN`, `ASSET_OWNED_ELSEWHERE`, `MANIFEST_MISMATCH`, `SELF_REVIEW_DENIED`,
`SELF_PUBLISH_DENIED`, `APPROVER_PUBLISH_DENIED`, `NOT_SUBMITTER`, `NOT_APPROVED`, `ALREADY_DECIDED`,
`COMMENT_REQUIRED`, `SURVEY_CODE_TAKEN`, `MARKET_NOT_IN_SCOPE`, `CONDITION_INVALID`, `NOT_FOUND`.

---

## 10. Amendment of 2026-11-22 (FI-1): saving from an editor

**ACCEPTED into the canonical contract by the owner on 2026-11-22 (D-205).** The `authoring` metadata may affect
content hashes; it must never acquire execution semantics, and no routing or wording rule may bypass validation
through it. **Authority:** owner decisions D-196…D-201, D-205. **Implemented in** `Call360-backend` (`app/domain/survey/store.py`,
`documents.py`, `app/api/survey_definitions.py`) and `Call360-frontend`
(`src/features/surveystudio/model/documents.ts`, `persist/`). Every change is additive: no document that exists is
changed, no hash changes, no fixture changes.

### 10.1 Two additional operations (seventeen in all)

| Operation | Permission | Meaning |
|---|---|---|
| `GET /survey-definitions/{id}/draft/documents` | `survey.read` | Everything needed to open the draft: the content document; the full document, state, ownership and server SHA-256 of every asset version the survey owns or its content pins; the survey's name and purpose; the draft revision, when and by whom it was saved; the governed catalogs |
| `POST /survey-definitions/{id}/draft/save` | `survey.edit` | **One Save.** `{expected_revision, operations[1…500]}`. Every operation is applied in order as **one revision**, in one database transaction, or none is. A stale `expected_revision` is `STALE_DRAFT` (409) with `current_revision`, and nothing is written. If any operation is refused the whole save is rolled back and the error names it (`operation_index`). The reply is the complete saved draft in the shape of the read above |

Both are market-scoped like every survey operation, and the save is CSRF-protected and rate-limited. One audit
event `SURVEY.DRAFT_SAVED` records the revision, the number of operations by kind and the assets touched.

**Why.** The fifteen operations of SS-03A change one document per request. A Save of an edited survey touches
several documents (answers, item, wording, module, content), so a client would have had to send several requests,
and a failure between them would have left a partly saved survey. Compensation in the client was rejected (owner
decision D-197).

**Idempotence without a token.** A repeated save carries the old `expected_revision` and is refused as stale. A
client whose reply was lost reads the draft: if it is at the next revision and holds exactly the documents that were
sent, the save had succeeded. Nothing is applied twice.

### 10.2 One additional draft operation

`SET_DETAILS {name, purpose}` — the survey's name (3–160 characters) and purpose (at most 2000). Descriptive only:
neither is part of a hashed document, a candidate or a version. Accepted by the batch save and by the single-operation
endpoint; this adds one sentence to the description of the existing `…/draft/operations` operation in the published
contract and changes nothing else about it.

### 10.3 The optional `authoring` field

ITEM, MODULE and CONDITION documents may carry an optional object `authoring`. It is part of the document and of its
hash. **It has no execution meaning: no validation rule, condition, route or manifest entry reads it.** A document
without it is byte-for-byte what it was; WORDING, OPTION_SET and content documents do not accept it.

| Document | `authoring` keys | Holds |
|---|---|---|
| MODULE | `intent` · `default_entry` · `derived_for` | What the author wrote the module is for; the entry rule recommended when it is placed; the survey a draft revision was derived for |
| CONDITION | `param_labels` · `shared` | The readable label of a parameter, when it differs from its name; `false` when the condition belongs to one placement |
| ITEM | `wording_version` | Only for an item no module places, and only when its wording version differs from its own version: which wording it is edited with |

**Why.** These are things an author types or the editor tracks that the documents had no field for. Without it they
would be lost on reload.

### 10.4 The editor mapping

One module maps the editor's Workspace to and from the six document kinds. Its rules:

- A value equal to its default is not stored: module `kind` `COMMON`; an empty intent; a parameter label equal to
  its name; an option set named `OS-<item code>` at the item's version (in the Workspace). `delivery_mode` is
  always stated in the document (TS-4).
- A question's answers are an option set. Several questions may share one; a question that changes shared answers
  gets its own set and never changes the others'.
- `response_obligation` `MANDATORY` is the editor's "must be answered"; any other code is kept as stored.
- Identities pass through unchanged: item, module, condition, option-set, node, edge, rule and instance codes. The
  execution identity `<instance>/<node>` is therefore the same before and after.
- The editor shows one wording per item version. A draft in which one item version is placed with two wording
  versions is **refused, not opened**, because opening it would lose one.
- A Save sends exactly the documents that differ from the loaded revision. A frozen version is never sent: a change
  is a new version.

**Proof.** `Call360-specs/docs/plans/survey-studio/canonical-documents/` holds the 27 fixtures as canonical
documents with the server's hashes, generated by the backend (kept current by a backend test). The frontend proves,
for each of the 27: documents → Workspace → documents is exact; Workspace → documents → Workspace is exact; node,
edge, instance and execution identities are unchanged.

---

## 11. Amendment of 2026-11-22 (FI-2): review and publication from Survey Studio

**ACCEPTED by the owner on 2026-11-22 (D-213).** **Authority:** owner decisions D-207…D-211, D-213. **Implemented in** `Call360-backend` (`app/domain/survey/store.py`,
`app/api/survey_definitions.py`) and `Call360-frontend` (`src/features/surveystudio/persist/ReviewPages.tsx`).
Additive: no table, no migration, no existing operation or document changes. The lifecycle, identity rules and
manifest verification are those of §9.6 and §9.3, unchanged.

### 11.1 Server-governed warnings and acknowledgements (FI2-D-1)

- Server validation reports findings of severity `BLOCKER` and `WARNING`. **A server `WARNING` is, by definition, one
  that must be acknowledged before submission.** Warnings raised only by the editor are advisory: they are never
  sent, stored or required.
- A warning has a stable `code` and an `at`. The register of server warning codes:

| Code | At | Raised when | Why |
|---|---|---|---|
| `SYNTHETIC_WORDING_UNAPPROVED` | the survey code | The survey pins at least one wording version | Every wording in Call360 is synthetic and unapproved for operational use (D-183). The acknowledgement records that the submitter knows a candidate's review and publication are not Compliance approval of its wording |

- **Submission** (`POST …/candidates`) takes `acknowledgements: [{code, at, reason}]`. It is refused, with nothing
  frozen and nothing created, when:
  - a server warning has no acknowledgement, or its reason is shorter than 10 or longer than 500 characters —
    `ACKNOWLEDGEMENT_REQUIRED`, with the warnings concerned;
  - an acknowledgement names something the server did not raise — `ACKNOWLEDGEMENT_UNKNOWN`;
  - an acknowledgement has no reason text — `ACKNOWLEDGEMENT_INVALID`.
- **What is recorded**, in the immutable candidate row: for each warning `{code, at, message, reason,
  content_sha256, acknowledged_by, acknowledged_by_name}`. `content_sha256` is the candidate's own content
  fingerprint: an acknowledgement belongs to exactly that content and is never carried to another candidate. The
  submission's audit event lists the acknowledged codes.
- A warning never blocks by itself, and acknowledging it makes nothing eligible for a call.

**No business policy is introduced by this.** The one code restates an existing owner decision. Further codes need
their own decision.

### 11.2 Two read operations (nineteen in all)

| Operation | Permission | Returns |
|---|---|---|
| `GET /survey-definitions/{id}/history` | `survey.read` | Every candidate (number, derived status, submitter, when, draft revision, fingerprints, latest event and by whom) and every version (label, derived status, publisher, when, candidate), oldest first; the draft's revision and content fingerprint |
| `GET /survey-candidates/{id}/documents` | `survey.read` | The frozen content; the full document of every pinned version with the fingerprint the manifest pins and whether the stored document still has it; manifest integrity and its problems; the makers by name; the approver; the recorded acknowledgements; the server's validation of exactly this content; the history; and `restrictions` for the reader |

`restrictions` states what the **identity rules** allow the reader — `can_decide`, `can_publish`, `can_withdraw`,
each with the server's reason code (`SELF_REVIEW_DENIED`, `SELF_PUBLISH_DENIED`, `APPROVER_PUBLISH_DENIED`,
`NOT_IN_REVIEW`, `NOT_APPROVED`, `NOT_SUBMITTER`, `NOT_OPEN`). It is information: the decision, withdrawal and
publication operations enforce the same rules whatever is shown, and each needs its permission as well.

Both are market-scoped. Neither changes anything.

### 11.3 Unchanged, restated because reviewers now see it

- A candidate and a version are immutable rows; their status is derived from events.
- "Makers" are everyone who changed the draft before the submission (D-209). They are shown by name on every
  candidate, with what follows from it.
- A changed draft is a new candidate with its own fingerprint and its own acknowledgements. It is in review: no
  approval is inherited. Submitting it supersedes an open earlier candidate; a published one is unaffected.
- The manifest is re-verified at approval and at publication; a mismatch refuses both and is audited.

---

## 12. Amendment of 2026-11-22 (LIB-1): the reusable component library

**Authority:** owner decisions D-215…D-220. **Implemented in** `Call360-backend` (`app/domain/survey/store.py`,
`app/api/survey_definitions.py`, `migrations/versions/0028_survey_library.py`) and `Call360-frontend`
(`src/features/surveystudio/model/library.ts`, `persist/Library.tsx`). There is one definition store and one
authoring model; the library is a READ of the published versions already in it. Behind its own server setting,
`survey_library_enabled` (off by default; needs `survey_definitions_enabled` and migration 0028).

### 12.1 What is reusable (LIB-D-1)

An asset version is **published** when the manifest of a survey version that was published (derived status
`PUBLISHED` or `SUPERSEDED`) pins it. That, and nothing else, makes it reusable by another survey — in the same
market only. A draft, an asset frozen in a candidate that is in review, rejected, withdrawn or superseded, and an
asset of another market are not reusable and are not shown, whoever asks.

The published set is computed from the immutable versions and their candidates' manifests. The derived usage index
is used only for the "used by" counts.

### 12.2 The reference rule (applies with the library on or off)

A survey's content may pin an asset version only if **this survey owns it** (draft or frozen) **or it is published**
(§12.1) in the survey's market.

- On saving a draft (single operation or atomic save): refused with `REFERENCE_NOT_PUBLISHED` (422), naming each
  offending version; nothing is saved.
- In server validation and at submission: the same code as a `BLOCKER`.

A reference is to the exact `{code, version}`. The server never copies, rewrites or upgrades what is referenced.

### 12.3 Who owns an identity, and who issues one (LIB-D-3)

- **A code belongs to the survey that owns its versions.** Another survey may pin a published version of it and may
  derive a copy under a code of its own. It may never add a version to that code: `CODE_OWNED_ELSEWHERE` (409). A
  wording follows its item.
- **With the library on, a code that does not exist yet must have been issued by the server** to this survey for
  this kind, or the new asset is refused: `CODE_NOT_ISSUED` (422). This applies to MODULE, ITEM, CONDITION and
  OPTION_SET, on both save operations.
- **Issuing.** `POST /survey-definitions/{id}/codes` `{requests: [{kind, count}]}`, kinds `MODULE`, `ITEM`,
  `STATEMENT` (an ITEM, by convention), `CONDITION`, `OPTION_SET`; at most 60 codes a request. Codes are
  `M-`, `Q-`, `S-`, `C-`, `OS-` followed by a number from one database sequence starting at 100001.
  - A sequence never returns a number twice — not to concurrent requests, and not after a request that was rolled
    back. A failed operation therefore leaves no code that could be issued again.
  - Every issued code is recorded (`survey_issued_code`: code as primary key, kind, survey, who, when; insert-only).
  - A number whose code any asset already carries is skipped: a historical code is never issued.
- **Nothing historical changes.** Existing codes, versions, references and every golden-fixture identity are as they
  were; the rule only concerns codes that do not exist yet. With the library off, an editor's own codes are accepted
  as before.

### 12.4 Provenance and makers (LIB-D-4)

- A local copy of a published component records its source in `authoring.derived_from`
  `{code, version, sha256?}`. `authoring` is now also accepted on OPTION_SET documents. As before it is part of the
  hash and has no execution meaning.
- A copy made from another survey's component starts at version 1 under its own code.
- The makers of a candidate are, unchanged, the people who changed **that survey's** draft. Pinning a published
  component adds nobody. The people who made the component are not makers of the consuming survey and are not
  restricted from reviewing it.

### 12.5 Newer revisions (LIB-D-5)

When something a content pins has a newer published version, server validation adds a finding
`NEWER_REVISION_PUBLISHED`, severity **`INFO`**, at `KIND:code@version`. It is never a warning to acknowledge, never
a blocker, never changes a candidate's validity, and nothing upgrades a pin.

### 12.6 Reading the library

| Operation | Permission | Returns |
|---|---|---|
| `GET /survey-components?kind=&q=` | `survey.read` | Published versions of one kind (`MODULE`, `ITEM`, `CONDITION`, `OPTION_SET`) in the reader's markets: title, description, category, kind-specific facts, the published survey versions that pin it, "used by" counts, whether it is the latest published version. `q` filters by title, description, code or publishing survey. An `ITEM` is listed with the wording version it is published with |
| `GET /survey-components/{kind}/{code}/{version}` | `survey.read` | One published component complete: its document; every published document it depends on; dependencies that are not published (none, for anything a version pins); its published revisions; usage; `requires.fields`; `derived_from`. 404 when it is not published in the reader's markets |
| `POST /survey-definitions/{id}/codes` | `survey.edit` | §12.3 |

Titles, descriptions and categories are read from the documents (module name, `authoring.intent`, module `kind`,
wording text, answer type, condition name). No catalog value or status is invented.

**Twenty-two operations in all.** Codes added by this amendment: `REFERENCE_NOT_PUBLISHED`,
`CODE_OWNED_ELSEWHERE`, `CODE_NOT_ISSUED`, `NEWER_REVISION_PUBLISHED`.

### 12.7 Settings and migrations

| Setting on | Schema must be at |
|---|---|
| neither | `0026`, `0027` or `0028` |
| `survey_definitions_enabled` | `0027` or `0028` |
| both, i.e. the library | `0028` |

Migration `0028_survey_library` adds one sequence and one insert-only table and changes nothing else. Its downgrade
refuses while any issued code is recorded.


---

## 13. Amendment of 2026-11-22 (SS-03B): Python execution, call-plan assembly and simulation

Authorised by the owner on 2026-11-22 ("Accept LIB-1, Close Security Gap and Authorize SS-03B"), decisions D-222…D-232.
**Simulation only.** Nothing in this section starts, schedules, authorises or makes anything eligible for a customer
call. No operational record is read or written. Additive: nothing in §1–§12 changes, except the behaviour of one
read operation, stated in §13.1.

### 13.1 Correction to `GET /survey-library/{kind}` (LIB-1 security closure) — an intentional behaviour change

| | Before | Now |
|---|---|---|
| What it lists | every frozen version of the kind, in every market, whoever made it | only versions **pinned by a published survey version in the reader's markets** |
| A draft's, an in-review, a rejected or a withdrawn candidate's assets | listed | **never listed** |
| A reader in another market | saw every market's assets | sees nothing of another market |
| Depends on `survey_library_enabled` | no | no — the rule holds with the library setting on or off |

The operation, its path, its permission (`survey.read`) and its response shape are unchanged. `candidates` and
`versions` in each row now both count the published versions that pin the row. The component-library operations of
§12.6 are unchanged. No published asset and no version reference was changed.

### 13.2 The execution engine

`app/domain/survey/execution.py` is the one authoritative execution of a survey definition. It is a pure function of
the resolved documents (`Bundle`), an immutable fact snapshot and the ordered answers supplied so far:

    execute(bundle, facts, supplier) -> run          execute_inputs(bundle, facts, inputs) -> run

It imports no database, clock, network, model or random source. It reuses the existing condition evaluator
(`conditions.evaluate`, three-valued) and document model; it does not replace or extend the operational script runtime
(`app/domain/lifecycle.py` and the script engine), which is untouched. It never writes, completes or rephrases
wording.

A run is `{status, terminal, pending, policy_unresolved, undeliverable, asked, delivered, modules, evidence,
evidence_states, edges, trace, events, rejections}`.

| `status` | Meaning |
|---|---|
| `PENDING` | A question needs an answer. `pending` names it, with its exact sentence and what an answer may be |
| `POLICY_UNRESOLVED` | The last input to the pending question was a non-answer whose handling is an open business decision (D-NA-1…17). **A simulation status, not an outcome.** `terminal` is null; the question is still current |
| `TERMINAL` | The run ended. `terminal.state` is one of `COMPLETED`, `ENDED_WITH_OUTCOME`, `MANDATORY_ESCALATION`, `REVIEW_REQUIRED`, `MISSING_INFORMATION_HALT`, `DRAFT_INVALID` |

Rules, each fixed by the golden fixtures:

* An answer is validated before it is accepted. A rejected answer is recorded as a `REJECT` event with its stable code
  (§3.7) and the same question is asked again; nothing advances.
* A statement is delivered and takes no answer.
* A missing fact makes a condition `UNKNOWN`. `UNKNOWN` is never `FALSE`; a decision without an `UNKNOWN` route, or an
  eligibility without an unknown-policy, stops the run as `DRAFT_INVALID` — it is never treated as "otherwise".
* An item is delivered only as its pinned wording version renders for these facts (§13.3). If it cannot be rendered
  the run halts with `WORDING_VALUE_MISSING` before anything is delivered at that item.
* A "not acknowledged" is refused with `NON_ANSWER_POLICY_UNRESOLVED` and reported as `POLICY_UNRESOLVED`. No repeat
  limit, silence window, timeout or refusal behaviour exists in the engine.
* Event `at` is the position of the event in the run. The location of a stop is `where` on the `END` event and `at`
  inside `terminal`.

### 13.3 Controlled wording values

`app/domain/survey/wording.py`: `render(text, fields, facts) -> {text, values, errors}`. `text` is the exact sentence
or null. Value states: `PRESENT`, `MISSING`, `INVALID`, `UNKNOWN_VARIABLE`, `MALFORMED`, `NOT_PERMITTED` (the catalog
marks the field `speakable: false`). An amount has at most two decimals and a whole-number field holds a whole number:
a value that does not is `INVALID` — never rounded or truncated. Output never depends on locale.

### 13.4 The call plan — schema `call360.survey.call-plan/1`

`app/domain/survey/callplan.py`: `assemble(bundle, facts) -> plan`, pure.

| Field | Content |
|---|---|
| `status` | `READY` or `BLOCKED` — **only** whether a technical plan can be computed from these facts |
| `issues[]` | `{code, at}`; codes `WORDING_VALUE_MISSING`, `ELIGIBILITY_UNKNOWN`, `MODULE_MISSING`, `CONDITION_INVALID`; sorted |
| `inputs[]` | every fact the plan read: `{field, type, state: PRESENT\|MISSING\|INVALID, value, used_by[]}` |
| `modules[]` | `{instance, module, name, status: IN\|OUT\|CONDITIONAL\|HALTS, reason, eligibility, activation, items[], open[]}` |
| `modules[].items[]` | `{key, node, item, statement, answer_type, role, mandatory, delivery_mode, wording_version, source, text, values[], errors[], certainty: ALWAYS\|SOME}` — `text` is the exact deliverable sentence, or null |
| `modules[].open[]` | points still decided during the call: `{key, kind: ANSWER\|CONDITION\|OUTCOME, alternatives[{on, to}]}` |
| `counts` | totals |
| `fingerprint` | SHA-256 of the canonical JSON of the plan without this field |

Module reasons: `NO_CONDITION`, `ELIGIBLE`, `NOT_ELIGIBLE`, `UNKNOWN_SKIPPED`, `UNKNOWN_HALTS`, `ON_OUTCOME`,
`MODULE_MISSING`. The same documents and facts always give the same plan and fingerprint; the order of fact keys is
irrelevant; an empty string is a missing value.

**Plan computability and operational eligibility are separate concerns.** The plan has no field for, and computes
nothing about, whether a call may be made.

### 13.5 Records — migration `0029_survey_simulation`

Three insert-only tables, additive. Each row carries `record_class`, fixed to `SIMULATION` by a CHECK constraint.

| Table | Holds |
|---|---|
| `survey_simulation` | the published version, its content and manifest fingerprints, the immutable facts and their fingerprint, who and when |
| `survey_simulation_input` | every input in order (`seq`), the question it was for, the answer, accepted or refused with the code, the run status and run fingerprint after it |
| `survey_call_plan` | the published version, the facts, the plan document, its status and fingerprint |

They reference only `survey_version`, `survey_definition` and each other. No operational table references them and
they have no column naming a case, attempt, session, recording, transcript, finding, customer or policy. A run is
never stored: it is the deterministic replay of the recorded inputs on the version's own pinned documents, so a
simulation can always be reproduced exactly. Before any execution the version's manifest is verified against the
stored documents; a mismatch is `409 MANIFEST_MISMATCH` and nothing runs.

### 13.6 Five operations (registered only when `survey_simulation_enabled` and `survey_definitions_enabled` are on)

| Operation | Permission | Notes |
|---|---|---|
| `POST /survey-versions/{version_id}/simulations` | **`survey.simulate`** | body `{facts, label}`; `201` with the simulation at its first pending question |
| `POST /survey-simulations/{simulation_id}/inputs` | **`survey.simulate`** | body `{expected_inputs, key, answer}`; one typed input for the current question |
| `GET /survey-simulations/{simulation_id}` | `survey.read` | state and full trace, replayed now; `replay_consistent`, `drift` |
| `POST /survey-versions/{version_id}/call-plans` | **`survey.simulate`** | body `{facts}`; `201` with the recorded plan |
| `GET /survey-call-plans/{plan_id}` | `survey.read` | the recorded plan; `fingerprint_verified`, `recompute_consistent` |

All are market-scoped (outside the caller's markets: `404`). The three `POST`s need the CSRF token, are rate-limited
(`survey_simulation_inputs_per_minute`) and write an audit event (`SURVEY.SIMULATION_CREATED`,
`SURVEY.SIMULATION_INPUT`, `SURVEY.CALL_PLAN_GENERATED`, each naming `record_class: SIMULATION`).

| Error | When |
|---|---|
| `409 VERSION_NOT_PUBLISHED` | the version is not published |
| `409 MANIFEST_MISMATCH` | the version does not match the documents it pins |
| `422 FACT_UNKNOWN` / `FACTS_INVALID` | a fact names a field outside the governed catalog, or is not a scalar |
| `422 ANSWER_INVALID` | an answer has a field the contract does not define, or a value of the wrong shape. Whether a well-formed answer is *valid* is decided by the engine and recorded as a refusal, not as this error |
| `409 STALE_SIMULATION` | `expected_inputs` is not the number of inputs the simulation holds |
| `409 INPUT_NOT_CURRENT` | the input is not for the current question |
| `409 SIMULATION_ENDED` / `SIMULATION_FULL` | the run has ended / holds the maximum of 400 inputs |

**Permission (owner decision D-234, replacing the SS-03B choice of `survey.read`).** The three state-changing
operations need **`survey.simulate`**, a permission of its own created by migration `0029` and granted to no role.
`survey.read` reads survey definitions, and reads a simulation or plan of a version in the reader's markets; it
creates nothing. `survey.read`, `survey.edit`, `survey.approve` and `survey.publish` together do not imply
`survey.simulate`.

| Error | When |
|---|---|
| `409 REPLAY_DRIFT` | an input is given to a simulation that no longer recomputes to its recorded result (§13.9) |

### 13.7 Settings and migrations (replaces the table of §12.7)

| Setting on | Schema must be at |
|---|---|
| none | `0026`, `0027`, `0028` or `0029` |
| `survey_definitions_enabled` | `0027`, `0028` or `0029` |
| + `survey_library_enabled` | `0028` or `0029` |
| + `survey_simulation_enabled` | `0029` |

`0029` downgrades by dropping its three tables: simulation records are not evidence of anything operational.

### 13.8 The editor's engine

The browser engine (`model/sim.ts`, `model/plan.ts`) remains for the in-memory prototype and as a preview of an
unsaved draft. For a saved survey the server is authoritative and is the default on the Simulator and Call plan
screens. The browser engine is run on the same published documents and inputs only to show whether it agrees; a
difference is displayed in full. `Call360-backend/scripts/export_survey_python_results.py` writes what the Python
engine produces for every golden run and plan to `python-results/`, and the frontend test
`persist/serverRun.test.ts` requires the browser engine to agree on all of them.

An interrupt whose `policy` is absent means `STOP_ESCALATE`. The server always read it so; the browser engine now
does too (`policyOf`).

### 13.9 Execution-contract version and replay drift (owner decision D-235)

A run is not stored; it is recomputed from the recorded inputs. So that a historical simulation can never silently
appear unchanged after the engine changes:

* `execution.CONTRACT` (`call360.survey.execution/1`) names the execution contract. It is changed whenever the engine
  may give a different result for the same documents, facts and inputs.
* `survey_simulation.engine_contract` records the contract a simulation was created under, and
  `initial_run_sha256` the fingerprint of its run before any input. Each `survey_simulation_input.run_sha256` is the
  fingerprint of the run after that input.
* On every read the run is recomputed and its fingerprint compared with the recorded one (the last input's, or the
  initial one). If they differ, **or** the recorded contract is not the current one, the simulation's `status` is
  `REPLAY_DRIFT`, `replay_consistent` is false and `drift` states the recorded and current contract, both
  fingerprints and whether the result differs. `run_status` still gives what the engine computes now, labelled as such.
* A drifted simulation takes no further input (`409 REPLAY_DRIFT`). A new simulation is recorded under the current
  contract.
* A call plan is stored in full with `plan_contract` (`call360.survey.call-plan/1`). On reading it is assembled
  again; `recompute_consistent` is false when the result or the contract differs. The recorded plan is what is
  returned.

**Retention.** There is no retention period, expiry or clean-up for simulation, call-plan or assignment-selection
records. This is recorded as an operational-readiness item (OR-1 in the decision register); no period is assumed.

---

## 14. Amendment of 2026-11-22 (ASG-1): survey selection by the existing assignment rules

Authorised by the owner on 2026-11-22 ("SS-03B Acceptance, Simulation Security Closure and ASG-1 Authorization"),
decisions D-236…D-244. **Simulation only.** Nothing in this section assigns a survey to a customer case, and nothing
changes Script Studio. Additive.

### 14.1 What is reused, and the one thing added

| Reused unchanged | From |
|---|---|
| The rule language (`{"all": [{"fact", "equals" \| "in"}, …]}`), its nine fields and their governed values | `rule_engine.FIELDS`, `rule_inputs.options` |
| Rule authoring, validation, maker-checker approval, publication, versioning, supersession, history | `rule_authoring.py`, `/assignment-rules…` |
| Loading published rules as candidates | `rule_inputs.published_candidates` |
| The decision: precedence (priority, then specificity), explicit fallback, fail-closed outcomes, full trace | `rule_engine.evaluate` |

**Contract mismatch (documented before the adapter was written).** A published rule version is bound by a NOT NULL
foreign key to a *script* version, its market is derived through the script family, and database triggers guard that
link. Letting a rule target a survey version *instead* would mean altering Script Studio tables, constraints and
triggers and every query that joins through the script — which the standing boundary "do not modify Script Studio"
forbids. A second mismatch: the rules read nine *assignment inputs*; the survey call plan reads *catalog facts*
(`policy.annual_premium`, …). The two vocabularies overlap in meaning but not in codes or values, and no mapping
between them is approved.

**The adapter.** One new governed artifact, the **survey binding**: *"when this exact published rule version wins,
the survey is this exact published survey version."* Before the engine decides, each candidate is copied with only
its target replaced by its bound survey version (`dataclasses.replace` of `target_id`, `target_label`,
`target_effective`). Conditions, priority, specificity, fallback flag and effective window are the rule's own.
A synthetic application supplies the assignment inputs and the catalog facts side by side; nothing is derived from one
to the other.

### 14.2 The binding

`survey_assignment_binding` (insert-only): the rule version (by id, code and number), the market, the survey version
and definition, the content and manifest fingerprints of that version, a note, who proposed it and when.
`survey_assignment_binding_event` (append-only): `PROPOSED → APPROVED | REJECTED | WITHDRAWN → PUBLISHED →
SUPERSEDED | WITHDRAWN`.

| Rule | Enforced |
|---|---|
| Only a PUBLISHED rule version and the currently PUBLISHED survey version of the same market can be bound; the version's manifest is verified | service, at proposal and again at publication |
| The approver is not the proposer; the publisher is neither the proposer nor the approver | service (`SELF_REVIEW_DENIED`, `SELF_PUBLISH_DENIED`, `APPROVER_PUBLISH_DENIED`, each audited) **and** a database trigger |
| One open binding per rule version | service (`BINDING_OPEN`) |
| Publishing a binding supersedes the earlier published binding of the same rule version, with an event | service |
| A binding is never edited; a different version needs a new binding through all three steps | insert-only triggers |
| A binding is to one rule *version*. A new version of the rule has no binding until one is published for it | by construction |

### 14.3 Selection

`assignment.select(db, market, inputs, at)`:

| Engine outcome | `selection` | Meaning |
|---|---|---|
| `SELECTED` | `MATCHED` | the highest-precedence matching rule; its bound version is selected |
| `SELECTED_BY_FALLBACK` | `MATCHED` | no other rule matched and an explicitly governed fallback rule did; `by_fallback: true` |
| `NO_MATCH` | `NO_MATCH` | nothing matched; nothing selected |
| `AMBIGUOUS`, `AMBIGUOUS_SAME_TARGET` | `AMBIGUOUS` | rules of equal precedence match; held, never chosen arbitrarily |
| `INPUT_MISSING` | `UNKNOWN_INPUT` | an input a rule reads is not known; `missing_inputs` names it. Never read as "does not match" |
| `TARGET_NOT_EFFECTIVE` | `TARGET_UNAVAILABLE` | the winning rule's survey version is not the published one (superseded, withdrawn) or is of another market |
| **`SURVEY_NOT_BOUND`** (added by the adapter) | `TARGET_UNAVAILABLE` | the winning rule has no published binding |

A rule without a binding keeps its full precedence: if it wins, the result is `SURVEY_NOT_BOUND`. It is never skipped
in favour of a lower rule, and no fallback survey is used in its place. A pinned version is never replaced by a newer
one. Assignment inputs must be fields of the rule language with values from their governed lists; `market` is
required and must be one of the caller's; an absent or null input is unknown.

### 14.4 Records and operations (registered only with `survey_assignment_enabled`, simulation and survey definitions on)

`survey_assignment_evaluation` (insert-only, `record_class = 'SIMULATION'` by CHECK): the inputs and facts with their
fingerprint, the time decided for, the engine, the outcome and selection, the whole decision with its trace and its
fingerprint, the rule version, binding and survey version selected, and the call plan. A CHECK ensures a survey
version is recorded exactly when the selection is `MATCHED`. `survey_assignment_simulation` links a selection to the
simulations started from it. Migration `0030_survey_assignment`; its downgrade refuses while a binding exists.

| Operation under `/api/v1/survey-assignment` | Permission |
|---|---|
| `GET /options` — the governed assignment inputs | **`survey.assignment.read`** |
| `GET /policy` — published rules in precedence order with their bindings | **`survey.assignment.read`** |
| `GET /bindings/{id}` | **`survey.assignment.read`** |
| `POST /bindings` — propose | `survey.edit` |
| `POST /bindings/{id}/decision` — approve or reject | `survey.approve` |
| `POST /bindings/{id}/publish` | `survey.publish` |
| `POST /bindings/{id}/withdraw` — an open proposal by its proposer; a published binding by a person who may publish | `survey.assignment.read` + the rule stated |
| `POST /evaluations` — select, verify the manifest, assemble the SS-03B plan, record | `survey.simulate` |
| `GET /evaluations/{id}` — the recorded selection, its plan and simulations; `recompute_consistent` | **`survey.assignment.read`** |
| `POST /evaluations/{id}/simulations` — an SS-03B simulation of the selected version with the same facts | `survey.simulate` |

All market-scoped (`404` outside the caller's markets); every `POST` needs the CSRF token, is rate-limited and
audited (`SURVEY.ASSIGNMENT_BINDING_*`, `SURVEY.ASSIGNMENT_EVALUATED`).

**Reading assignment data is a permission of its own (owner decision D-247, replacing the ASG-1 choice of
`survey.read`).** The policy shows the conditions and precedence of published assignment rules — Script Studio's
data. `survey.assignment.read` (created by migration `0030`, granted to no role) is required by **every** operation
in this section, the state-changing ones included, in addition to the permission shown. `survey.read`, with or without
`survey.edit`, `survey.approve`, `survey.publish` and `survey.simulate`, opens none of it. What is returned is limited
to what the survey assignment experience needs: for a rule, its reference, name, market, conditions in words,
priority, specificity, fallback flag and effective window — **not** its script target, author, checker, checksum,
drafts or history. The Assignment Rules API and the `script.*` permissions are unchanged.

The response of `POST /evaluations` carries the selected version, the matching rule and the full trace, the plan
with its fingerprint, modules, facts read and their states, and open points. **A selection and a plan are not an
assignment of a survey to a case and not eligibility for a call**; the response says so.

### 14.5 Settings and migrations (replaces §13.7)

| Setting on | Schema must be at |
|---|---|
| none | `0026` … `0030` |
| `survey_definitions_enabled` | `0027` … `0030` |
| + `survey_library_enabled` | `0028` … `0030` |
| + `survey_simulation_enabled` | `0029` or `0030` |
| + `survey_assignment_enabled` | `0030` |

---

## 15. Amendment of 2026-11-22 (ASG-2A): several surveys for one application

Authorised by the owner on 2026-11-22 ("Accept ASG-1 and Implement ASG-2A Multi-Survey Assignment"), decisions
D-246…D-257. **Simulation only.** Additive. The semantics were written before implementation in
`34_ASG-2A_GROUPING_AND_MATCHING_SEMANTICS.md`, which is part of this contract; this section is its summary and the
data and API contract.

### 15.1 The model

| Artifact | What it says | Governed by |
|---|---|---|
| Assignment rule version (existing, unchanged) | *when* — conditions, priority, specificity | Assignment Rules: maker, checker |
| Survey binding (ASG-1) | *which survey version* a rule version stands for | three people |
| **Requirement group** (new) | *which requirement* a set of rule versions competes for: `PRIMARY`, `ADD_REQUIRED` or `ALTERNATIVE`, with a stated purpose and an optional governed position | three people |

The engine is called once per published group, over that group's member rules only. Nothing of the engine or the rule
language is changed or copied.

### 15.2 A requirement and the selection

| Group outcome (the engine's) | `state` of the requirement |
|---|---|
| `SELECTED`, `SELECTED_BY_FALLBACK` | `SELECTED` |
| `NO_MATCH` in `ADD_REQUIRED` / `ALTERNATIVE` | `NOT_APPLICABLE` |
| `NO_MATCH` in `PRIMARY`; `AMBIGUOUS`; `AMBIGUOUS_SAME_TARGET`; `INPUT_MISSING`; `TARGET_NOT_EFFECTIVE`; `SURVEY_NOT_BOUND`; or a group whose structure is invalid | `UNRESOLVED` |

Configuration issues (each makes `selection_status = UNRESOLVED_CONFIGURATION`): `PRIMARY_GROUP_MISSING`,
`PRIMARY_GROUP_CONFLICT`, `RULE_IN_SEVERAL_GROUPS`, `GROUP_STRUCTURE_INVALID`, `MEMBER_NOT_PUBLISHED`,
`BOUND_RULE_UNGROUPED` (a rule with a published binding, in no group, that matches or may match the application).
A rule with no binding and no group is a script rule and takes no part.

`selection_status`: `RESOLVED` · `UNRESOLVED_REQUIREMENT` · `UNRESOLVED_CONFIGURATION`.

### 15.3 The composite plan — schema `call360.survey.composite-plan/1`

| Field | Content |
|---|---|
| `application` | `{assignment_inputs, facts, sha256}` — one snapshot, one fingerprint |
| `input_consistency` | always `{status: UNVERIFIED, reason}` until a mapping is approved |
| `policy` | the group versions, rule versions and bindings the result was computed from |
| `configuration_issues[]` | `{code, at, detail}` |
| `requirements[]` | per group: `group{id, code, version, kind, name, purpose, sequence}`, `state`, the engine's `outcome`, `reason`, `winning_rules`, `missing_inputs`, `by_fallback`, the full `trace`, and when selected `selected{rule, rule_version_id, binding_id, survey_version_id, survey_code, version_label, content_sha256, manifest_sha256}` and `plan{status, fingerprint, issues, missing_facts, open_points, modules, items}` |
| `selected[]` | the selected surveys with their reasons and individual plan fingerprints |
| `ordering` | `{status: NOT_APPLICABLE \| GOVERNED \| UNRESOLVED, reason: ABSENT \| PARTIAL \| CONFLICTING, order, listing}` — `order` is null unless governed |
| `cross_survey_policy` | `{status: UNRESOLVED}` whenever more than one survey is selected; `NOT_APPLICABLE` for one |
| `missing_inputs`, `missing_facts` | unions |
| `selection_status`, `plan_status` | `plan_status`: `READY` (selection resolved, ordering governed or not applicable, every individual plan `READY`) · `BLOCKED` (settled, an individual plan blocked) · `UNRESOLVED` |
| `fingerprint` | SHA-256 of the canonical composite without this field |

**Three separate states (owner decision D-261).** Beside the composite, and not part of its fingerprint, every
response carries `states`: `call_plan` (`COMPUTABLE` when `plan_status` is `READY`, `NOT_COMPUTABLE` when `BLOCKED`,
`UNRESOLVED` otherwise); `coordinated_simulation` (`PERMITTED`, or `BLOCKED` with the blocker codes of §16.2);
`operational_call_eligibility` (always `NOT_ESTABLISHED`). None implies another: a computable plan may have a
blocked coordinated simulation, and neither says anything about a real call.

Each selected survey's plan is the SS-03B plan of that version, recorded as its own `survey_call_plan` with its own
fingerprint; the composite refers to it. Nothing is merged, de-duplicated or re-routed. `READY` says nothing about
whether a call may be made or about what happens between surveys.

### 15.4 Records — migration `0031_survey_assignment_groups`

`survey_assignment_group` (code, version, market, kind, name, purpose ≥ 10 characters, sequence),
`survey_assignment_group_member` (exact rule versions), `survey_assignment_group_event` (lifecycle; a trigger refuses
an approver who proposed and a publisher who proposed or approved), `survey_composite_plan`
(`record_class = 'SIMULATION'`; a CHECK refuses `READY` or `BLOCKED` unless the selection is `RESOLVED` and the
ordering `GOVERNED` or `NOT_APPLICABLE`), `survey_composite_plan_member` (a CHECK requires a selected requirement to
name its version, rule, binding and plan, and any other to name none). All insert-only. The downgrade refuses while a
group exists.

### 15.5 Operations (registered only with `survey_assignment_groups_enabled` and everything it needs)

| Operation under `/api/v1/survey-assignment` | Permission (each also needs `survey.assignment.read`) |
|---|---|
| `GET /groups` | — |
| `POST /groups` — propose a version of a group | `survey.edit` |
| `POST /groups/{id}/decision` | `survey.approve` |
| `POST /groups/{id}/publish` — refused if it would give a market a second primary group or put a rule in two groups | `survey.publish` |
| `POST /groups/{id}/withdraw` | proposer, or `survey.publish` for a published group |
| `POST /composite-plans` — select every requirement, plan each selected survey, record | `survey.simulate` |
| `GET /composite-plans/{id}` — as recorded; `recompute_consistent`, and `plan_intact` per member | — |

The ASG-1 operations of §14.4 are unchanged and answer as before.

### 15.6 Settings and migrations (replaces §14.5)

| Setting on | Schema must be at |
|---|---|
| none | `0026` … `0031` |
| `survey_definitions_enabled` | `0027` … `0031` |
| + `survey_library_enabled` | `0028` … `0031` |
| + `survey_simulation_enabled` | `0029` … `0031` |
| + `survey_assignment_enabled` | `0030` or `0031` |
| + `survey_assignment_groups_enabled` | `0031` |

---

## 16. Amendment of 2026-11-22 (ASG-2B): coordinated simulation of the surveys of one composite

Authorised by the owner on 2026-11-22 ("Accept ASG-2A and Authorize ASG-2B Coordinated Simulation"), decisions
D-259…D-269. **Simulation only.** Additive. The continuation rules of §16.3 are authorised **solely for technical
simulation**; they approve nothing about what a real customer call does.

### 16.1 A thin coordinating layer

`app/domain/survey/coordination.py` executes nothing. Each survey of the composite is run by its own SS-03B
simulation (§13), created, advanced and read through the same functions as a single-survey simulation, on its own
published version, with its own inputs, rejected inputs, trace, status, drift detection and run fingerprint. The
coordinator refuses to start, starts a survey, routes an input to the current survey, starts the next survey, and
computes the coordinated state. It merges no graph and removes, shortens or skips no statement or question.

### 16.2 When a coordinated simulation may start

Refused with `409` and the first of these codes; every one that applies is listed in the error details and in the
composite's `states.coordinated_simulation.blockers`. Nothing is recorded.

| Code | When |
|---|---|
| `SELECTION_UNRESOLVED` | the composite's `selection_status` is not `RESOLVED` |
| `NOTHING_SELECTED` | no survey is selected |
| `ORDER_UNRESOLVED` | no complete, unambiguous governed order |
| `PLAN_BLOCKED` | a selected survey's own call plan is `BLOCKED` |
| `DUPLICATE_SURVEY_REQUIREMENT_UNRESOLVED` | two requirements select the same survey version. It is run neither once nor twice (D-258.3) |
| `COMPOSITE_STALE` | the composite would no longer be computed the same |

### 16.3 Continuation — for technical simulation only

| Situation of the current survey | Coordinated `status` | What happens |
|---|---|---|
| `PENDING` | `RUNNING` | the coordinator stays; the next survey has no simulation |
| an invalid answer | `RUNNING` | refused by the survey's own run; the same question stays current |
| `POLICY_UNRESOLVED` | `POLICY_UNRESOLVED` | stops with the survey's own reason; the question stays current |
| `TERMINAL`, state `COMPLETED`, another survey follows | `RUNNING` | the next survey is started; decision `PROCEED`, rule `SIMULATION_ONLY_COMPLETED_PROCEEDS` |
| `TERMINAL`, state `COMPLETED`, the last survey | `ALL_SURVEYS_COMPLETED` | progress only — **not a business outcome** |
| `TERMINAL`, any other state (an escalation, another named outcome, review required, a halt) | `CROSS_SURVEY_POLICY_UNRESOLVED` | stops; no survey is started; decision `STOP` |
| `REPLAY_DRIFT` | `REPLAY_DRIFT` | stops; no input is taken |

The coordinated record has no outcome and no terminal state of its own: none is synthesised.

### 16.4 Records — migration `0032_survey_coordinated_sim`

`survey_coordinated_simulation` (`record_class = 'SIMULATION'` by CHECK): the composite plan, the application and
composite fingerprints, the contract `call360.survey.coordinated-simulation/1`, the governed order.
`survey_coordinated_simulation_step`: each survey that was started — position, group, survey version, individual
simulation (unique), and `started_because` (`FIRST_IN_ORDER` for position 1, `PREVIOUS_COMPLETED` otherwise, by
CHECK). Both insert-only. They reference only the composite plan, the group, the survey version and the individual
simulation; nothing references them. The downgrade drops them.

The state is computed on reading from the steps and the replay of each individual simulation; it is never stored.
`replay_sha256` is the SHA-256 of `{contract, composite_fingerprint, application_sha256, order, status, decisions,
surveys[{group, survey_version_id, state, run_sha256, engine_contract}]}` — no identifier and no time, so the same
composite and the same inputs always give the same value.

### 16.5 Operations (registered only with `survey_coordinated_simulation_enabled` and everything it needs)

| Operation under `/api/v1/survey-assignment` | Permission (each also needs `survey.assignment.read`) |
|---|---|
| `POST /composite-plans/{id}/coordinated-simulations` — start; `201`, or `409` with a code of §16.2 | `survey.simulate` |
| `POST /coordinated-simulations/{id}/inputs` — body `{expected_inputs, key, answer}`: one typed input for the current question of the current survey; `expected_inputs` is the total across the surveys | `survey.simulate` |
| `GET /coordinated-simulations/{id}` | — |

Market-scoped; the two `POST`s need the CSRF token, are rate-limited and audited
(`SURVEY.COORDINATED_SIMULATION_CREATED`, `SURVEY.COORDINATED_SIMULATION_SURVEY_STARTED`, beside the individual
simulations' own events). Errors on input: `409 STALE_SIMULATION`; `409 CROSS_SURVEY_POLICY_UNRESOLVED`,
`ALL_SURVEYS_COMPLETED` or `REPLAY_DRIFT` when the coordinated simulation takes no further input; and the individual
simulation's own errors (`INPUT_NOT_CURRENT`, `ANSWER_INVALID`, …).

The response: `status`, `stop {code, at, reason}`, `decisions[]`, `governed_order`, `surveys[]` (each with its pinned
version and fingerprints, `state` — `COMPLETED`, `CURRENT`, `NOT_STARTED`, `STOPPED`, `DRIFTED` — `started_because`,
`simulation_id`, the individual simulation in full, `run_sha256`, `engine_contract`), `current`, `progress`,
`execution_contracts`, `composite_fingerprint`, `composite_intact`, `application_sha256`, `input_consistency`,
`replay_sha256`, `operational_call_eligibility` (always `NOT_ESTABLISHED`).

The single-survey simulation operations of §13.6 are unchanged.

### 16.6 Settings and migrations (replaces §15.6)

| Setting on | Schema must be at |
|---|---|
| none | `0026` … `0032` |
| `survey_definitions_enabled` | `0027` … `0032` |
| + `survey_library_enabled` | `0028` … `0032` |
| + `survey_simulation_enabled` | `0029` … `0032` |
| + `survey_assignment_enabled` | `0030` … `0032` |
| + `survey_assignment_groups_enabled` | `0031` or `0032` |
| + `survey_coordinated_simulation_enabled` | `0032` |

## 17. Amendment of 2026-11-22 (EVAL-1): journey-level control evaluation of simulations

**Simulation only.** Authorised by the owner on 2026-11-22 (D-275…D-286). Nothing here evaluates a real call, writes
an operational finding, routes a review or gives a case a disposition. The assessment of the existing engines and the
design decisions are in `37_EVAL-1_EXISTING_ENGINE_ASSESSMENT_AND_DESIGN.md`; this section is the contract.

### 17.1 Grain

| Level | Is |
|---|---|
| Application | the synthetic application snapshot of the journey |
| Callback journey | the evaluation-run context: ONE single-survey simulation, or ONE coordinated simulation |
| Survey execution | one SS-03B simulation — an evidence-producing sub-context |
| **Control instance** | **the atomic result: one control of the register in one evaluation** |
| Evidence observation | one placement of one mapped item in one survey execution |

Survey is never the evaluation grain. A single-survey simulation is a journey with one survey execution.

### 17.2 Governed control mapping

One immutable revision per control and market. Lifecycle `PROPOSED → APPROVED | REJECTED | WITHDRAWN → PUBLISHED →
SUPERSEDED | WITHDRAWN`; proposer, approver and publisher are three different people (service and database trigger).

| Field | Rule |
|---|---|
| control | a control of the existing register; the mapping pins a fingerprint of the control row |
| `combination` | `ALL_REQUIRED` — the only value (D-287). Declared by the mapping, not assumed by the engine |
| `applicability` | none (declared for every journey of the market), or a published condition that reads application facts only, with exactly its parameters |
| `entries[]` | exact item `code` and `version` pinned by a published survey version of the market; `evidence_type` `ANSWER` or `DELIVERY`; `required`; optional `survey_code` context; for `ANSWER`, a rule of the existing S3-A language validated by `answer_evaluation.configure` |
| `source` | provenance, at least 10 characters |

Refused: an item or condition that is not published in the market; a statement as answer evidence; a multiple-choice
answer; a rule the existing validator refuses; required evidence that is collect-only; no required evidence; a second
open proposal for the same control. Nothing is inferred from a label.

### 17.3 Evidence adapter (SS-03B evidence → the existing evaluator's inputs)

| Survey evidence | Existing result |
|---|---|
| an accepted answer | by the rule: `MATCH`, `MISMATCH`, `HUMAN_ASSESSMENT_REQUIRED`, `MISSING_EXPECTED_FACT`, `NOT_EVALUATED` |
| asked; an input was refused, or the non-answer policy is unresolved | `UNRESOLVED` (no refusal reason is claimed) |
| waiting for an answer; not reached; not on the path taken; module skipped for missing information; survey not started; the exact revision is in no survey of the journey | `NOT_ASKED` |
| module left out by the survey's own FALSE condition | `NOT_APPLICABLE` |
| multiple-choice answer | `UNSUPPORTED_EVIDENCE` (not passed to the evaluator) |
| delivery evidence | `DELIVERED` / `NOT_DELIVERED` (recorded by the adapter) |

Each observation carries: survey code, version, manifest fingerprint and position; simulation id and run fingerprint;
placement; item code, version and type; the wording as delivered (version, mode, exact text); the evaluator's own
record (rule, answer, expected, explanation); refused inputs; trace event numbers; and a `gap` code when there is no
accepted answer.

### 17.4 Control outcome and processing status

Control outcome, first rule that holds: applicability false → `NOT_APPLICABLE`; no published mapping, changed
control, unsupported combination, unknown applicability or untrusted evidence → `UNRESOLVED`; the same item answered
differently in different places → `REQUIRES_REVIEW`; a required `MISMATCH` → `NOT_SATISFIED`; required evidence
missing → `INSUFFICIENT_EVIDENCE`; required human assessment → `REQUIRES_REVIEW`; every placement of every required
entry `MATCH` or `DELIVERED` → `SATISFIED`.

Processing status of the evaluation: `FAILED_TECHNICALLY` (a survey's simulation no longer recomputes to its record,
or the composite is not intact — no outcome is asserted and no finding generated); `REQUIRES_REVIEW`; `INCOMPLETE`
(the journey did not complete every survey, or a control is `INSUFFICIENT_EVIDENCE` or `UNRESOLVED`); `COMPLETED`.
`COMPLETED` does not mean compliant. `coverage.status` is always `NOT_ASSERTED`.

### 17.5 Findings

`finding_engine.generate`, unchanged, with the market's PUBLISHED finding rule set, once per answer observation of an
`APPLICABLE` control. Category, severity, justification and review flag are the rule set's. A triggering result no
rule covers is listed as not converted. No published rule set → `findings_status: FINDING_RULES_MISSING`. Nothing is
de-duplicated. The operational `finding` table, materiality policy and review routing are not used.

### 17.6 Records — migration `0033_survey_control_evaluation`

Additive: `survey_control_mapping`, `survey_control_mapping_event` (guard trigger), `survey_journey_evaluation`
(`record_class` fixed to `SIMULATION`; exactly one of `simulation_id` / `coordinated_id`; unique per journey and
`input_sha256`), `survey_control_result`, `survey_evidence_observation`, `survey_evaluation_finding`. All insert-only.
References out of the survey tables: `control` and `finding_rule_set_version` only. Permissions
`survey.evaluation.read` and `survey.evaluate`, granted to no role. Downgrade refuses while a mapping exists.

`pins` holds: journey and its replay and application fingerprints; each execution's version, manifest, simulation, run
fingerprint and execution contract; each control's fingerprint; each mapping revision and fingerprint; the finding
rule set version and checksum; the engines. `input_sha256` is its fingerprint: the same journey and the same pins are
the same evaluation (the existing record is returned). Anything changed gives a new record. On reading, an evaluation
is computed again from its pins; a difference is reported as `EVALUATION_DRIFT` with reasons, and what is published
now but was not used is listed. No retention period is set (OR-1).

### 17.7 Operations (registered only with `survey_evaluation_enabled` and simulation)

Prefix `/api/v1/survey-evaluation`.

| Operation | Permissions |
|---|---|
| `GET /controls` | `survey.evaluation.read` |
| `GET /mappings`, `GET /mappings/{id}` | `survey.evaluation.read` |
| `POST /mappings` | + `survey.edit` |
| `POST /mappings/{id}/decision` | + `survey.approve` |
| `POST /mappings/{id}/publish` | + `survey.publish` |
| `POST /mappings/{id}/withdraw` | proposer (open) or `survey.publish` (published) |
| `POST /evaluations` (201 new, 200 existing) | + `survey.evaluate` |
| `GET /evaluations?simulation_id=…` or `?coordinated_simulation_id=…`, `GET /evaluations/{id}` | `survey.evaluation.read` |

Market-scoped; state-changing operations are CSRF-protected, rate-limited and audited
(`SURVEY.CONTROL_MAPPING_*`, `SURVEY.JOURNEY_EVALUATED`).

### 17.8 Settings and migrations (replaces §16.6)

| Setting on | Schema must be at |
|---|---|
| none | `0026` … `0033` |
| `survey_definitions_enabled` | `0027` … `0033` |
| + `survey_library_enabled` | `0028` … `0033` |
| + `survey_simulation_enabled` | `0029` … `0033` |
| + `survey_assignment_enabled` | `0030` … `0033` |
| + `survey_assignment_groups_enabled` | `0031` … `0033` |
| + `survey_coordinated_simulation_enabled` | `0032` or `0033` |
| `survey_simulation_enabled` + `survey_evaluation_enabled` | `0033` |

§16.2 gains one field: `states.coordinated_simulation.available` — whether this server has coordinated simulation
switched on. A start control is offered only when the composite is `PERMITTED` and the server says `available`.

## 18. Amendment of 2026-11-22 (EVAL-2A): governed control policies, applicability and coverage

**Simulation only.** Authorised by the owner on 2026-11-22 (D-293…D-299). The registry assessment and the design are
in `39_EVAL-2A_CONTROL_REGISTRY_ASSESSMENT_AND_POLICY_DESIGN.md`; the migration report in `41_…`. Nothing here decides
what a real application needs, and no insurance obligation is created: a policy is a governed container.

### 18.1 What is added, and what is not touched

The control register (`control`) is not altered. Script Studio, the finding engine and the finding rule sets are not
altered. The EVAL-1 tables are not altered. An evaluation that names no policy is the EVAL-1 evaluation of §17,
written and read exactly as before.

| Artifact | Identity | Says |
|---|---|---|
| Control (existing) | register code and id; pinned by a fingerprint of its row | that a control exists |
| **Control policy** (new) | `(market, code, revision)` | which controls must be assessed, what each is for, when each obligation applies, what evidence each requires |
| Control mapping (§17.2) | `(market, control, revision)` | which exact published survey items supply that evidence, under which rule |
| **Control instance** | `(evaluation, control, obligation)` | the result |

### 18.2 Control policy

Lifecycle and three-person rule as §17.2 (service and database trigger). Immutable once proposed; publishing
supersedes the published revision of the same code; a revision is never deleted.

| Field | Rule |
|---|---|
| `code`, `name`, `market_code`, `owner`, `source` | required |
| `scope_statement` | required, in words |
| `scope` | optional published condition on application facts |
| `completeness` | `DECLARED_COMPLETE` or `PARTIAL` |
| `empty_set_is_complete` | false unless the policy sets it |
| `controls[]` | a control of the register (a policy does not create controls), once; `purpose`; 1–10 obligations |
| obligation | `key`, `title`, `applicability` (none, or a published condition reading application facts only, with exactly its parameters), `combination` = `ALL_REQUIRED`, 1–20 evidence requirements of which at least one is required |
| evidence requirement | `key`, `description`, `evidence_type` `ANSWER` / `DELIVERY`, `required` |

A mapping entry may carry `requirement` (and `obligation`, needed when the control has several): the policy
requirement it supplies.

### 18.3 Applicability

`scope`: `IN_SCOPE`, `OUT_OF_SCOPE`, `UNKNOWN`. Each obligation: `APPLICABLE` (required), `NOT_APPLICABLE`,
`UNKNOWN`, with the facts read and the facts missing. `fingerprint` = SHA-256 over the policy fingerprint, the facts
fingerprint, the scope and every obligation's status. `input_lineage.status` is always `UNVERIFIED`.

### 18.4 Evaluation under a policy

The control instances are the policy's obligations. For each:

| Condition | Outcome | Instance coverage |
|---|---|---|
| evidence not trusted | `UNRESOLVED` | `INTEGRITY_FAILED` |
| the control changed in the register since the policy; combination unsupported | `UNRESOLVED` | `EVALUATION_UNSUPPORTED` |
| applicability false | `NOT_APPLICABLE` | `NOT_REQUIRED` |
| applicability unknown | `UNRESOLVED` | `APPLICABILITY_UNKNOWN` |
| no published mapping; a required requirement with no bound entry; a mapping entry that names no requirement, a requirement the policy does not have, or another evidence type | `UNRESOLVED` | `NOT_MAPPED` |
| otherwise | by §17.4 (D-290) | conflict → `EVIDENCE_CONFLICTING`; no required observation, or one unsupported or not evaluated → `EVALUATION_UNSUPPORTED`; a required gap → `EVIDENCE_MISSING`; required human assessment → `HUMAN_ASSESSMENT_PENDING`; else `EVIDENCED` |

`required` is the policy's. Mapped evidence is always observed and shown, whatever is decided. Findings: §17.5,
for `APPLICABLE`, fully mapped instances.

### 18.5 Coverage of the journey

| Status | When |
|---|---|
| `NOT_ASSERTED` | no policy (`NO_POLICY`, the §17 form); evidence not trusted; policy `PARTIAL`; application out of scope or scope unknown; no obligation applies and the policy does not declare that complete |
| `INCOMPLETE` | otherwise, when an applicability is unknown or a required instance is not `EVIDENCED` |
| `COMPLETE_WITHIN_POLICY_SCOPE` | otherwise |

Complete coverage is a statement about evidence within one policy's declared scope. An `EVIDENCED` instance may be
`NOT_SATISFIED`. `operational_compliance_eligibility.status` is always `NOT_ESTABLISHED`.

### 18.6 `SET_MATCH` (existing answer-evaluation engine, D-299)

For a `MULTI_SELECT` answer. Rule: `mode` ∈ `INCLUDES_ALL`, `INCLUDES_ANY`, `INCLUDES_NONE`, `EQUALS`; `options`: one
or more of the question's published option codes, each once. Refused at configuration: unknown mode, empty expected
set, a duplicate, an option that is not the question's, a question that is not multiple choice.

| Selection as accepted by the survey | Result |
|---|---|
| a list of the question's option codes, each once (any order; may be empty) | `MATCH` or `MISMATCH` by the mode, as sets |
| contains a duplicate, an unknown code, or is not a list of codes | `UNRESOLVED` — not evaluated, never collapsed or repaired |
| rule malformed when it reaches the evaluator | `NOT_EVALUATED` |
| no accepted answer (waiting, refused, not reached) | as §17.3 — never an empty selection |

`normalized_answer` is the selection in the question's own option order. Two selections are the same answer when
equal as sets. `SET_MATCH` is in `ALL_METHODS`; `METHODS` (what Script Studio offers) is unchanged.

### 18.7 Records — migration `0034_survey_control_policy` (purely additive)

New, insert-only: `survey_control_policy`, `survey_control_policy_event` (guard trigger), `survey_evaluation_policy`
(evaluation → policy revision and its fingerprint), `survey_obligation_result` (key `evaluation_id, control_code,
obligation`; outcome, applicability, coverage), `survey_obligation_observation`, `survey_obligation_finding`. No
existing table, column, key, index or trigger is changed. An evaluation under a policy writes its results to the
obligation tables and nothing to the EVAL-1 result tables; which tables an evaluation is read from is said by its own
pins. `pins.policy` holds the policy id, code, revision and fingerprint. Downgrade refuses while a policy or a
policy-scoped evaluation exists.

### 18.8 Operations (registered only with `survey_control_policy_enabled` and evaluation)

Prefix `/api/v1/survey-evaluation`. Reading needs `survey.evaluation.read`.

| Operation | Further permission |
|---|---|
| `GET /builder-options`, `GET /journeys`, `GET /control-policies`, `GET /control-policies/{id}` | — |
| `POST /control-policies` | `survey.edit` |
| `POST /control-policies/{id}/decision` | `survey.approve` |
| `POST /control-policies/{id}/publish` | `survey.publish` |
| `POST /control-policies/{id}/withdraw` | proposer (open) or `survey.publish` (published) |
| `POST /applicability` (nothing recorded) | `survey.evaluate` |
| `POST /evaluations/preview` (nothing recorded) | `survey.evaluate` |

`POST /evaluations` (§17.7) accepts `control_policy_id`: a PUBLISHED revision of the journey's market; refused with
404 when policies are not switched on. Evaluation responses gain `control_policy_id`, `policy`, `applicability` and
`operational_compliance_eligibility`; list entries gain `policy` and `coverage_status`. All additive.

### 18.9 Settings and migrations (adds to §17.8)

| Setting on | Schema must be at |
|---|---|
| every row of §17.8 | … or `0034` |
| `survey_evaluation_enabled` + `survey_control_policy_enabled` | `0034` |

## 19. Amendment of 2026-11-22 (EVAL-2B): execution assurance of simulated journeys

**Simulation only.** Authorised by the owner on 2026-11-22 (D-305…D-310). Assessment and design:
`42_EVAL-2B_EXECUTION_ASSURANCE_ASSESSMENT_AND_DESIGN.md`. Nothing here executes a survey: the authoritative engine's
recorded trace is verified. Nothing here computes a control outcome, coverage or a finding. A simulation does not
show that a person heard any wording.

### 19.1 Contract and grain

`call360.survey.execution-assurance/1`, verifying traces of `call360.survey.execution/1`. The run is of the journey
(§17.1); each survey execution has its own result.

### 19.2 Survey checks

Each check has `check`, `question`, `status` (`PASSED`, `FAILED`, `INCOMPLETE`), `examined`, `findings[]`
(`code`, `text`, `evidence` with placement and event numbers) and notes.

| Check | Finding codes |
|---|---|
| `INTEGRITY` | `REPLAY_DRIFT`, `STEP_FINGERPRINT_DIFFERS` |
| `TRACE_WELL_FORMED` | `MISSING_EVENT`, `DUPLICATE_EVENT`, `EVENTS_OUT_OF_ORDER`, `EVENT_AFTER_END` |
| `DELIVERIES_EXPECTED` | `UNEXPECTED_DELIVERY`, `DELIVERY_ITEM_DIFFERS`, `DUPLICATE_DELIVERY`, `MISSING_RECORDED_DELIVERY`, `DELIVERY_WITHOUT_EVENT` |
| `WORDING_EXACT` | `WORDING_ALTERED`, `DELIVERY_MODE_DIFFERS`, `WORDING_NOT_PINNED` |
| `ANSWERS_AND_REJECTIONS` | `ANSWER_WITHOUT_QUESTION`, `INVALID_ANSWER_ACCEPTED`, `DUPLICATE_ANSWER`, `REJECTION_CODE_DIFFERS`, `REJECTION_NOT_RECORDED`, `ANSWER_NOT_AS_RECORDED` |
| `BRANCHING` | `ROUTE_NOT_IN_VERSION`, `ROUTE_DIFFERS_FROM_VERSION`, `ROUTE_WITHOUT_EVIDENCE`, `ROUTE_NOT_SUPPORTED_BY_ANSWER`, `TRANSITION_UNEXPLAINED`, `EXECUTION_OMISSION` |
| `MODULE_SEQUENCE` | `MODULE_NOT_IN_VERSION`, `MODULE_ORDER_DIFFERS`, `MODULE_STATUS_UNSUPPORTED`, `MISSING_TRANSITION` |
| `TERMINATION` | `UNEXPECTED_TERMINATION`, `MISSING_EVENT` |

A survey result also carries `deliveries[]` (placement, event, kind, item, recorded text, expected text, wording
version, wording fingerprint, delivery mode, `wording` = `EXACT` / `ALTERED` / …, `awaiting_answer`), `exclusions[]`
(every placement not delivered: `class`, `why`, the explaining event, module status), `branches[]`, `rejections[]`,
`ending`, `pending` and counts.

Exclusion classes: `VALID_CONDITIONAL_EXCLUSION`, `EXCLUDED_INFORMATION_MISSING`, `VALID_ROUTING_EXCLUSION`,
`NOT_ON_PATH_TAKEN`, `SURVEY_ENDED_BEFORE`, `NOT_YET_REACHED`, and `OMISSION` — the only one that is a deviation.

### 19.3 Journey checks (coordinated)

| Check | Finding codes |
|---|---|
| `SELECTION_RECORDED` | `COMPOSITE_NOT_INTACT`, `SELECTION_DIFFERS` |
| `GOVERNED_ORDER` | `ORDER_DIFFERS` |
| `NO_BYPASS` | `SURVEY_BYPASSED`, `START_REASON_DIFFERS` |
| `OWN_EVIDENCE` | `EVIDENCE_SHARED`, `EVIDENCE_REFERENCE_DIFFERS` |
| `NO_DEDUPLICATION` | `REQUIREMENT_MISSING`, `DUPLICATE_REQUIREMENT_UNRESOLVED` |

### 19.4 Status

Survey: `INTEGRITY_FAILED` if `INTEGRITY` failed; else `DEVIATION_DETECTED` if any check failed; else `INCOMPLETE` if
the run has not ended; else `VERIFIED`. `NOT_ASSESSABLE` when recorded under another execution contract. A survey not
started is `INCOMPLETE`.

Journey, first that holds: `INTEGRITY_FAILED` (any survey, or `COMPOSITE_NOT_INTACT`); `DEVIATION_DETECTED` (any
survey, or a failed journey check); `NOT_ASSESSABLE`; `INCOMPLETE`; `VERIFIED`.

`operational_call_eligibility.status` is always `NOT_ESTABLISHED`.

### 19.5 Beside a control evaluation

With `evaluation_id` (an evaluation of the same journey, else `409 EVALUATION_OF_ANOTHER_JOURNEY`):
`control_evaluation` (id, result fingerprint, processing status, coverage status, policy, `of_this_evidence`) and
`control_evidence[]` — for each control instance its recorded `outcome` and `coverage`, `execution_evidence`
(`EXECUTION_VERIFIED`, `EXECUTION_INCOMPLETE`, `DEVIATION_IN_EVIDENCE`, `INTEGRITY_FAILED`, `NOT_ASSESSABLE`,
`NO_EXECUTION_EVIDENCE`), `result_is_trustworthy`, and per observation its delivery, the class and reason when not
delivered, and any deviation at that placement. `of_this_evidence: false` makes every result not trustworthy.

### 19.6 Records — migration `0035_survey_execution_assurance` (purely additive)

`survey_execution_assurance` (`record_class` fixed to `SIMULATION`; exactly one of `simulation_id` / `coordinated_id`;
optional `evaluation_id`; `contract`, `pins`, `input_sha256`, `status`, `summary`, `result_sha256`; unique per journey
and `input_sha256`) and `survey_execution_assurance_survey` (key `assurance_id, position`; version, simulation,
status, full detail). Insert-only. No permission added. Downgrade refuses while a result exists.

### 19.7 Operations (registered only with `survey_execution_assurance_enabled` and evaluation)

| Operation | Permissions |
|---|---|
| `POST /api/v1/survey-evaluation/assurance` (201 new, 200 existing) | `survey.evaluation.read` + `survey.evaluate` |
| `GET /api/v1/survey-evaluation/assurance?simulation_id=…` or `?coordinated_simulation_id=…` | `survey.evaluation.read` |
| `GET /api/v1/survey-evaluation/assurance/{id}` | `survey.evaluation.read` |

A read carries `replay` and `current_status` (`ASSURANCE_DRIFT` when it no longer recomputes). Audited as
`SURVEY.EXECUTION_ASSURED`.

### 19.8 Settings and migrations (adds to §18.9)

| Setting on | Schema must be at |
|---|---|
| every row of §18.9 | … or `0035` |
| `survey_evaluation_enabled` + `survey_execution_assurance_enabled` | `0035` |

## 20. Amendment of 2026-11-22 (E2E-1): the provenance of one simulated journey

**Simulation only. Read only.** Authorised by the owner on 2026-11-22 (D-316…D-319). Baseline and acceptance matrix:
`44_E2E-1_BASELINE_INTEGRATION_AND_ACCEPTANCE_MATRIX.md`. This section adds **one read operation and nothing else**:
no table, no migration, no setting, no permission, no engine. It computes no control outcome, coverage, finding or
assurance result; every value it returns is read from the record that owns it (§§12–19).

### 20.1 Contract and operation

`call360.survey.journey-trace/1`.

`GET /api/v1/survey-evaluation/journey-trace` — registered only with execution assurance (§19.7). Needs
`survey.evaluation.read`. Exactly one of `simulation_id`, `coordinated_simulation_id`, `composite_plan_id` (else
`422 JOURNEY_REQUIRED`); optionally `evaluation_id` (default: the journey's latest evaluation) and `assurance_id`
(default: the latest assurance result beside that evaluation). An evaluation or assurance of another journey:
`409 EVALUATION_OF_ANOTHER_JOURNEY` / `ASSURANCE_OF_ANOTHER_JOURNEY`. Market-scoped through the services it reads.

`composite_plan_id` traces an application whose journey never started (`journey.kind` `APPLICATION_ONLY`); it needs
`survey.assignment.read`. Without that permission the five assignment links of any journey are `WITHHELD` and carry
no record.

### 20.2 The chain — fifteen links, in this order

| Step | `key` | Authoritative record | Version | Fingerprint (`sha256`) is of |
|---|---|---|---|---|
| 1 | `APPLICATION` | none of its own: stored on the composite plan or simulation | — | the application's facts (and assignment inputs) |
| 2 | `ASSIGNMENT_INPUTS` | composite plan | — | assignment inputs and call-plan facts together |
| 3 | `RULE_VERSIONS` | assignment rule version (Script Studio tables, read only) — every rule that MATCHED | rule version | the rule version's recorded checksum |
| 4 | `BINDINGS` | survey binding | — | the manifest of the survey version it pins |
| 5 | `REQUIREMENT_GROUPS` | requirement group revision | group version | **none recorded on its own**; covered by the composite fingerprint |
| 6 | `SURVEY_VERSIONS` | published survey version | version label | the version's manifest |
| 7 | `COMPOSITE_PLAN` | composite plan; each survey's call plan | contract | the whole composite; each call plan |
| 8 | `SIMULATIONS` | simulation, one per survey | execution contract | the run after the last recorded input |
| 9 | `COORDINATED_SIMULATION` | coordinated simulation | contract | the coordinated run |
| 10 | `CONTROL_POLICY` | control policy revision | revision | the policy revision |
| 11 | `MAPPINGS` | control mapping revisions pinned by the evaluation | revision | each mapping revision |
| 12 | `EVALUATION` | journey evaluation; finding rule set; control register rows | contract | the evaluation's result; the rule set; each register row as read |
| 13 | `CONTROL_RESULTS` | inside the evaluation record | — | none of their own; covered by the evaluation's result fingerprint |
| 14 | `FINDINGS` | inside the evaluation record | — | each finding's key |
| 15 | `EXECUTION_ASSURANCE` | assurance result | contract | the assurance result |

A link has `step`, `key`, `title`, `status`, `records[]`, `notes[]`. `status`: `RECORDED`, `NOT_RECORDED_YET`,
`NOT_PART_OF_THIS_JOURNEY` (a single survey simulated directly has no assignment), `NONE`, `NONE_SELECTED`,
`WITHHELD`, `NOT_AVAILABLE`. A record has `kind`, `id`, `label`, `version`, `sha256`, `sha256_of`, `source`, `facts`.

### 20.3 Five separate dimensions

`dimensions.completion` (journey status, surveys completed / started, why it stopped), `.satisfaction` (the
evaluation's own counts by outcome; never one overall value), `.coverage` (the evaluation's coverage status and
reason), `.assurance` (the assurance result's current status), `.eligibility` (always `NOT_ESTABLISHED`). None is
derived from another.

### 20.4 Also returned

`questions[]` — the reviewer's seven questions and the links that answer each; `evidence_gaps[]` — the shown
evaluation's own results whose coverage is not `EVIDENCED` / `NOT_REQUIRED` (without a policy: outcome
`INSUFFICIENT_EVIDENCE`, `REQUIRES_REVIEW` or `UNRESOLVED`), with their reasons and observations; `integrity` — for
each record, whether it recomputes to itself now; `open_points[]` — `SYNTHETIC_CONTENT`,
`INPUT_CONSISTENCY_UNVERIFIED`, `CROSS_SURVEY_POLICY_UNRESOLVED`, `POLICY_NAMED_EXPLICITLY`,
`INPUT_LINEAGE_UNVERIFIED`, `NOT_SPOKEN`; `evaluations[]`, `assurances[]` — every one of the journey;
`trace_sha256` — over the kind, id and fingerprint of every record of the chain, in order (computed, not stored).

### 20.5 What it never does

It writes nothing and audits nothing of its own. It does not select a control policy, re-evaluate, re-verify or
re-compose. A changed record is reported under `integrity`, never corrected.

## 21. Amendment of 2026-11-22 (UX-HOME-1): the workspace summary

**Read only.** Authorised by the owner on 2026-11-22 (D-321…D-324). Report: `46_UX-HOME-1_WORKSPACE_REPORT.md`.
This section adds **one read operation and nothing else**: no table, no migration, no setting, no permission. No
evaluation or business-rule meaning is added or changed.

`GET /api/v1/survey-definitions/workspace` — registered with survey definitions (§12). Needs `survey.read`.
Market-scoped: everything is counted in the reader's markets only. It writes nothing, not an audit event.

| Field | Meaning |
|---|---|
| `markets` | the reader's markets |
| `library_enabled` | whether the component library is on; when off, `inventory.components` is `null` and `reused_modules` empty |
| `inventory.surveys` | `total`, `with_a_published_version`, `never_published`, `in_review`, `approved_awaiting_publication` — from the surveys and their derived candidate status |
| `inventory.components` | per kind (`MODULE`, `ITEM`, `CONDITION`, `OPTION_SET`): `components` (distinct codes), `published_revisions`, `pinned_by_more_than_one_survey`; `ITEM` also `questions` and `statements`. Counted from the library's own list (§13): only what a published version pins |
| `recent_drafts[]` | up to six drafts by `saved_at`, newest first; `saved_by_you`, `ever_published` |
| `recent_published[]` | up to six published versions by `published_at`, newest first |
| `awaiting_you[]` | open survey candidates the reader may act on **now**: `action` `DECIDE` when the candidate's own restrictions allow a decision and the reader holds `survey.approve`; `PUBLISH` when they allow publication and the reader holds `survey.publish`. The restrictions are the ones the operations enforce (§12: not the maker; not the approver) |
| `waiting_on_others[]` | open candidates the reader submitted, with `waiting_for` `A_REVIEWER` or `A_PUBLISHER` |
| `reused_modules[]` | latest published revisions of modules pinned by more than one survey, most widely pinned first, at most six. **A count of published pins — not a usage or frequency statistic.** Empty when none is reused |

Nothing here is estimated, scored or ranked by anything but those counts and times.

**Added in UX-HOME-1 + NAV-1 (D-329 f), both read-only and additive:**

| Field | Meaning |
|---|---|
| `surveys[]` on the workspace read | every survey of the reader's markets with what its **current draft** holds: `modules`, `questions`, `statements`, `decisions`, `conditional_entries`, `branching`, `draft_revision`, `saved_at`, `published_at`, `latest_version_label`. Counted from the draft's own documents; nothing is executed |
| `facts.branching` on a `MODULE` in the component library (§13) | true when the module's own document has a decision, a step whose links lead to more than one destination, or rule-ordered, follow-up or interrupting routing. Read from the document; nothing is executed |

## 22. Amendment of 2026-11-22 (LIB-2): a module authored on its own

Authorised by the owner on 2026-11-22 (D-333). Design: `49_LIB-2_ASSESSMENT_AND_ARCHITECTURE.md`. Report:
`50_LIB-2_IMPLEMENTATION_REPORT.md`. **No document format changes**: a standalone module is the module document of
§5, its dependencies the documents of §1–§4, its draft the content document of §8.

### 22.1 The kind of a definition — migration `0036_survey_module_authoring` (one additive column)

`survey_definition.artifact_kind` is `SURVEY` (the default; every definition before LIB-2) or `MODULE`. It never
changes. A `MODULE` definition is the authoring and publication record of one reusable module; its `code` is the
module's code, issued by the server.

A `MODULE` definition is never a survey. It is absent from the list of surveys and from the workspace's counts;
no published version of it can be simulated, given a call plan, bound to an assignment rule, coordinated or
evaluated. The application refuses by not finding it (404); the database refuses a `survey_simulation`,
`survey_call_plan` or `survey_assignment_binding` row that names one.

### 22.2 The frame

The content of a `MODULE` definition's draft is **exactly**:

```json
{"schema": "call360.survey.content/1", "code": "<module code>",
 "sequence": [{"instance": "<name>", "module": {"code": "<module code>", "revision": <n>},
               "routes": {"<outcome>": {"survey_outcome": "<outcome>"}, "…": "…"}}]}
```

one placement, of a revision of the definition's own module that the definition owns, with one route per declared
outcome of that revision, each ending the run as that outcome. No eligibility, activation or skip disposition. Any
other content is refused at save and at submission with `422 MODULE_FRAME_INVALID`. The definition's name and purpose
are taken from the module document (`name`, `authoring.intent`) on every save.

### 22.3 Operations (registered only with `survey_module_authoring_enabled` and the library)

| Operation | Permission | Meaning |
|---|---|---|
| `POST /api/v1/survey-modules` | `survey.edit` | create a standalone module: its issued code, an empty revision 1 and the frame. No survey is created |
| `GET /api/v1/survey-modules` | `survey.read` | the standalone modules of the reader's markets, drafts included |
| `GET /api/v1/survey-modules/{module_id}` | `survey.read` | one; a survey's id is not found here |
| `POST /api/v1/survey-module-tests` | `survey.simulate` (and `survey.read`) | run one module with the Python engine; nothing is recorded |

Everything else — draft documents, save, code issuing, validation, submission, candidate read and documents,
decision, withdrawal, publication, version read, history — is the existing operation of §9–§12, addressed by the
module's id. `GET /survey-versions/{id}` and its content read return a module's publication record too; nothing that
executes, plans, assigns or evaluates does.

`SurveyModuleOut`: `id`, `code`, `name`, `description`, `market_code`, `draft_revision` (the save counter),
`saved_at`, `saved_by_you`, `working_revision`, `working_state` (`DRAFT` | `FROZEN`), `unpublished_changes`, `facts`
(as on a library module), `open_candidate` (`id`, `n`, `status`, `revision`, `submitted_at`, `submitted_by_you`,
`your_action` `DECIDE` | `PUBLISH` | null — the identity rule AND the reader's permission, `waiting_for`
`A_REVIEWER` | `A_PUBLISHER`), `published[]` (`revision`, `version_id`, `version_label`, `status`, `published_at`),
`latest_published_revision`.

### 22.4 The module test

Request: `module_id` (a standalone module — its working draft, or `revision` of it) **or** `code` and `revision` of a
module published in the reader's markets; `facts` (catalog fields, as for a simulation); `inputs` — an ordered list
of `{key, answer}`, at most 200.

The engine is given the frame of that revision, built for the test. It is `execution.execute_inputs`, unchanged.
Returned: `record_class` `MODULE_TEST`; `module` (code, revision, name, fingerprint, state, `source`
`WORKING_DRAFT` | `FROZEN_REVISION` | `PUBLISHED_REVISION`, `published`); `engine_contract`; `frame`; `manifest`
(every exact version executed); `requires.fields` and `fields` (the catalog definition of each fact its conditions
read); `findings`; `testable`; `facts`, `facts_sha256`; `inputs[]` (`seq`, `key`, `answer`, `accepted`,
`rejection_code`, `run_status`); `status` (`PENDING` | `POLICY_UNRESOLVED` | `TERMINAL` | `NOT_TESTABLE`); `run`;
`run_sha256`.

- A module with a validation blocker is `NOT_TESTABLE`: its findings are returned and the engine is not run.
- An input for a question that is not current, or after the end, is refused (`409 INPUT_NOT_CURRENT`).
- An answer the engine rejects is in `inputs` as refused, with its stable code; the same question stays current.
- **Nothing is written** — no simulation, plan, audit event or any other row. The same request always gives the same
  `run` and `run_sha256`.
- A test is not validation for publication, not approval and not eligibility for any call.

### 22.5 The library (adds to §13)

| Field | Meaning |
|---|---|
| `origin` on a component | where this version was written: `definition_id`, `code`, `name`, `artifact_kind` of the definition that owns it |
| `artifact_kind` on each `published_in[]` | `SURVEY`: a survey whose published version pins it. `MODULE`: the standalone module's own publication record |
| `used_by` | counts **surveys** only; a module's own publication record is not a use |

The reuse rule is the one of §13: a version is reusable if and only if a published version pins it. A module
published on its own is pinned by its own publication record.

### 22.6 Settings and migrations (adds to §19.8)

`survey_module_authoring_enabled` — off by default; on only with `survey_library_enabled`; needs migration `0036`.
With it off, a schema at `0035` is accepted and serves everything else unchanged.

## 23. Amendment of 2026-11-23 (SHARED-1): Assignment Rules and Finding Rules on their own

Authorised by the owner on 2026-11-23 (D-360), on the rulings B-1 (D-357) and B-2 (D-358). Design:
`52_SHARED-1_ASSESSMENT_AND_DESIGN.md`. Report: `53_SHARED-1_IMPLEMENTATION_REPORT.md`. **The rule engine, the
condition language, the evaluation engine and the finding engine are unchanged.** No survey document changes.

### 23.1 A rule's own market — migration `0037_shared_rule_services`

`script_assignment_rule_version.market_code` (NOT NULL; a governed market; immutable with the published version).
For a rule written before SHARED-1 it was back-filled from its target script family and verified. For a new rule it
is the draft's market, which is one of the author's authorised markets, chosen when the rule is created. It is never
taken from a survey or from a free field. Every reader takes a rule's market from the rule.

### 23.2 What a rule selects

`target_kind` on `assignment_rule_draft` and `script_assignment_rule_version`, fixed when the rule is created and the
same for every later version:

| `target_kind` | Script target | Assigns a script to a case | Selects a survey |
|---|---|---|---|
| `SCRIPT_VERSION` (default; every rule before SHARED-1) | required, published, same market | yes, as before | through a published survey binding, as before |
| `SURVEY_BINDING` | **absent** — a draft with one is refused (`TARGET_NOT_ALLOWED`) | **never** | through a published survey binding |

`CHECK ((target_kind = 'SCRIPT_VERSION') = (target_script_version_id IS NOT NULL))`.

A `SURVEY_BINDING` rule is excluded from operational script assignment at three levels: the candidate loader returns
script-backed rules unless both kinds are asked for, and only survey selection asks; the simulation of rules over
cases refuses a survey-only draft (`SURVEY_ONLY_NOT_SIMULATED_ON_CASES`); and the database refuses a
`script_assignment` whose matched rule is not script-backed. It is not listed by the script-side
`GET /script-assignment-rules`.

Validation of a `SURVEY_BINDING` draft: the target checks do not apply; it carries the warning `SURVEY_ONLY`; its
conflicts are computed against **every** live rule of its market (the set survey selection evaluates). Validation of
a `SCRIPT_VERSION` draft is unchanged, against script-backed rules only. The manifest and checksum of a script-backed
rule are exactly what they were; those of a survey-only rule add `target_kind` and state no target.

Lifecycle: the existing one — author, a different reviewer, a publisher who is not a maker. Unchanged.

### 23.3 Market consistency of survey bindings and groups

Refused by the application (`MARKET_MISMATCH`, as before) and now also by the database: a survey binding, its rule and
its survey belong to one market; a requirement group holds rules of its own market only; a script-backed rule and its
target script belong to one market.

### 23.4 Operations — no new operation; additive fields

| Field | Where |
|---|---|
| `target_kind` | `RuleCreate` (request; `SURVEY_BINDING` needs the setting), `RuleExplainIn`, `RuleDraftOut`, `RuleVersionOut`, `RuleSummary`, and each rule of `GET /survey-assignment/policy` |
| `market` | `RuleVersionOut` (the rule's own); `RuleSummary.market` is now the rule's own market, not a constant |
| `survey_only_rules` | `GET /assignment-rules/options` — whether this server can create a survey-only rule |

Errors: `409 SURVEY_ONLY_RULES_UNAVAILABLE`, `422 INVALID_TARGET_KIND`, `422 COPY_KIND_MISMATCH`,
`422 TARGET_NOT_ALLOWED`, `422 SURVEY_ONLY_NOT_SIMULATED_ON_CASES`.

### 23.5 Permissions

Eight permissions, created and granted to no role. Each operation accepts either the dedicated permission or the
legacy one:

| Operation | Dedicated | Legacy, still accepted |
|---|---|---|
| assignment rules: registry, options, draft, history, diff, explain | `assignment_rule.read` | `script.read` |
| create, new version, save, validate, submit, abandon | `assignment_rule.edit` | `script.edit` |
| review | `assignment_rule.approve` | `script.approve` |
| publish | `assignment_rule.publish` | `script.publish` |
| finding rule sets: options, list, read | `finding_rule.read` | `script.read` |
| create, save, submit, abandon | `finding_rule.edit` | `script.edit` |
| review | `finding_rule.approve` | `script.approve` |
| publish | `finding_rule.publish` | `script.publish` |

Unchanged and not covered by a dedicated permission: `POST /assignment-rules/simulate` (it reads cases; `script.read`),
`script.assign` (applying a script to a case, the batch run), and every Script Studio operation. No permission implies
another: the survey permissions grant nothing on rules, and a rule permission grants nothing in Script Studio, Survey
Studio or the other rule capability.

### 23.6 Finding rules

No schema change. A rule of scope `QUESTION` still names a script question code; it does not match a survey item, and
no cross-system question identity is defined here (dependency DEP-FR-1).

### 23.7 Settings and migrations (adds to §22.6)

`shared_rule_services_enabled` — off by default; needs migration `0037`. With it off no survey-only rule can be
created; a schema at `0036` is accepted, and a rule's market and kind are read as its script family's market and
`SCRIPT_VERSION`.

### 23.8 Governance as accepted (2026-11-23, D-370, D-372)

SHARED-1 is accepted as technically verified. The lifecycles are retained as they are and differ by capability:

| Capability | People |
|---|---|
| Assignment rule; finding rule set | two — an author, and a different checker who may also publish |
| Survey binding; requirement group; survey, module and library content | three — each step by a different person |

Harmonisation is not decided. A rule's kind is fixed at creation (§23.2); the conflict scope of §23.2 is unchanged
and its consequences are assessed in `54_…` §3 (CK-1…CK-3).

### 23.9 Development (D-375, D-376)

Migration `0037` is applied to local development and `shared_rule_services_enabled` is on there. The dedicated
permissions are held only by four development-only roles (`DEV_RULE_AUTHOR`, `DEV_RULE_CHECKER`,
`DEV_FINDING_AUTHOR`, `DEV_FINDING_CHECKER`). No standing role holds one.

## 24. The governed Applicability library (APPL-X2) — additive, off by default

Full specification: `60_APPL-X2_LIBRARY_ARCHITECTURE_API_AND_MIGRATION.md`. Verified on the test schema only.

### 24.1 What is added

| | |
|---|---|
| Setting | `applicability_library_enabled` (off by default). Needs migration `0038_applicability_library`; with it on, readiness fails closed on an earlier schema; with it off, a schema at `0037` serves everything else |
| Operations | fourteen under the path prefix `/api/v1/applicability` (`60_…` §5). None of the existing operations changed |
| Schemas | twenty-one, all named `Applicability…` |
| Permissions | `applicability.read`, `.edit`, `.approve`, `.publish` — created by the migration, granted to no role, independent of `survey.*` and `script.*` |
| Tables | `applicability_asset`, `applicability_asset_version`, `applicability_asset_dependency`, `applicability_event` |

### 24.2 Contract rules

* Publication needs three different people; refused by the service (403 `SELF_REVIEW_DENIED`,
  `SELF_PUBLISH_DENIED`, `APPROVER_PUBLISH_DENIED`) and by `CHECK` constraints. A refusal is recorded.
* A draft is saved with `expected_revision`; a stale one is refused with 409 `STALE_REVISION` and nothing is
  overwritten.
* A candidate pins exact published versions of its own market; a draft is never a published dependency.
* A published version never changes; a later version of something it pins does not affect it.
* Another market's item answers 404.
* Nothing here selects a survey for a case, assigns anything or permits a call. Applicability policies are not
  stored. Assignment rules, survey bindings and requirement groups are neither read nor written.

### 24.3 Authorization contract of Survey Applicability Studio (owner rulings of 2026-11-24)

| Need | Permission | Note |
|---|---|---|
| read the library | `applicability.read` | |
| draft and submit | `applicability.edit` | |
| approve or return | `applicability.approve` | never one's own submission |
| publish | `applicability.publish` | never as the submitter or the approver |
| **open the screen, read published survey versions, run the evaluator** | **`survey.read`** | **an explicit, read-only dependency of the screen (D-408)** |

`survey.read` is required because the workspace is part of Survey Studio, links requirements to published survey
versions read from Survey Studio, and runs the stateless evaluator behind that permission. It is **declared per
role**. It is never implied by an applicability permission, the migration grants it to nobody, and it is **not given
automatically to any future role**: role provisioning must name it. It gives no right to create, edit, approve,
publish or simulate a survey.

Cross-market (D-402): another market's individual item answers 404; another market's workspace or test answers 403;
nothing about another market's items is disclosed. Locking (D-403): a draft is locked while its candidate is in
review; a return or a withdrawal reopens the same draft and never changes the frozen candidate.

### 24.4 No silent dependency upgrade (D-405)

`POST /applicability/assets/{id}/submit` accepts `pins`: the exact versions the submitter reviewed (as returned by
`validate`). When given, the submission is refused with 409 `PINS_CHANGED` — and nothing is frozen — unless they are
exactly what would be pinned now. The portal always sends them, after showing each version with its fingerprint and
requiring confirmation. A candidate's content fingerprint, manifest fingerprint and pins are shown to the reviewer
before the decision. One schema (`ApplicabilityPinAck`) and one optional field are added; nothing else changed.

## 25. Persistent Applicability Policies (APPL-X3) — additive, off by default

Full specification: `64_APPL-X3_PERSISTENT_POLICIES_ARCHITECTURE_AND_CONTRACTS.md`. Verified on the test schema only.

| | |
|---|---|
| Setting | `applicability_policies_enabled` (off by default; effective only with `applicability_library_enabled`). Needs migration `0039_applicability_policy`; with it off, a schema at `0038` serves everything else |
| Operations | ten under `/api/v1/applicability/policies` (`64_…` §5). None of the existing operations changed |
| Schemas | fifteen, named `ApplicabilityPolicy…` |
| Permissions | none added. `applicability.read` / `applicability.edit`, and `survey.read` on every operation |
| Tables | `applicability_policy`, `applicability_policy_dependency`, `applicability_policy_event` |

Contract rules: a policy is a working draft, saved with `expected_revision` (409 `STALE_REVISION`, nothing
overwritten). Every dependency is recorded at an exact version or draft revision with its fingerprint and is never
moved to a newer one except by an edit of the document. A survey reference must be an exact published Survey Studio
version of the policy's market, with both fingerprints (422 `INVALID_SURVEY_REFERENCE` otherwise). `evaluate` runs
the saved revision; `preview` runs an unsaved document and is marked so; both are refused while a pinned draft has
moved. Another market's policy answers 404. **There is no publication of policies**: no candidate, no approval, no
published version. A selection plan assigns nothing and permits no call.

## 26. APPL-X4a — synthetic scenarios, regression suites and recorded runs (test schema only)

Full specification: `68_APPL-X4a_ARCHITECTURE_AND_CONTRACTS.md`. Built and verified on the isolated test schema; **not
applied to development**; awaiting owner acceptance.

- **Scenario document:** `name`, `description`, `profiles`, `facts` (a value, `null` = not known, absent = not
  provided), `pins`. No customer, policy-number, case or session field exists. `record_class` is `SYNTHETIC`.
- **Scenario snapshot** (`call360.applicability-scenario-snapshot/1`): per variable and profile — asset id, version
  id, version number (or draft revision), content and manifest fingerprints.
- **Expectation:** `status`, `selected [{code, version}]`, `pending`, optional `replaced`, `needs`; `confirmed` must
  be true; `source` AUTHORED or PROPOSED_FROM_RESULT. Never written by the server from a result.
- **Run record** (`call360.applicability-evaluation-run/1`): the policy document, manifest and definitions read; the
  suite as run; per result the scenario as it was, the expectation, the complete plan, the verdict. Immutable;
  re-evaluable from the record alone.
- **Verdicts:** PASSED, FAILED, COULD_NOT_EVALUATE, INVALID_DEFINITION, NO_EXPECTATION. Inability to evaluate never
  passes.
- **Coverage** is requirement- and condition-level, of the scenarios run; `exhaustive` is always false.
- 22 operations under `/api/v1/applicability/{scenarios,suites,runs}`; permissions `applicability.read`,
  `applicability.edit`, `survey.read`; no new permission. Migration `0040_applicability_scenarios`.
- Published Applicability Policies are §27.

## 27. APPL-X4b — governed publication of Applicability Policies (test schema only)

Full specification: `72_APPL-X4b_ARCHITECTURE_AND_CONTRACTS.md`. Built and verified on the isolated test schema; **not
applied to development**; awaiting owner acceptance.

- **Readiness** is computed by the server from the saved revision and one recorded run the author chose. A blocker is
  `{code, message, action, prevents[SUBMISSION|APPROVAL|PUBLICATION], at}`. The newest run is never chosen.
- **Independence:** an expectation with `source = PROPOSED_FROM_RESULT` is never independent evidence and is never
  converted. Every material behaviour needs a passing scenario whose expectation is `AUTHORED`.
- **Expectation authorship:** `stated_by`, `stated_at` — written by the server when stated content changes; never
  accepted from a client.
- **Candidate:** frozen `document`, `manifest` (snapshot and definitions), `evidence`, `candidate_sha256`. Status
  SUBMITTED, APPROVED, RETURNED, WITHDRAWN, PUBLISHED. Submitter, checker and publisher are three different people,
  enforced in the service and by CHECK constraints.
- **Revalidation** at approval and at publication, against the frozen candidate only; by content fingerprint; nothing
  refreshed, substituted or upgraded.
- **Version:** numbered per policy, written from the candidate, immutable; at most one PUBLISHED; the earlier becomes
  SUPERSEDED and stays readable and verifiable.
- **Run target** (`record.target`): `DRAFT` with revision, `CANDIDATE` or `VERSION` with id; required once a candidate
  or version exists (`TARGET_REQUIRED`).
- 13 operations under `/api/v1/applicability`; permissions `applicability.read`, `.edit`, `.approve`, `.publish`,
  with `survey.read`; no new permission. Migration `0041_applicability_publication`.
- A published policy is configuration. Nothing reads it to select a survey for a case, plan a callback or start a
  session.

## 28. APPL-X5a — synthetic journeys over published policy versions (test schema only)

Full specification: `78_APPL-X5a_ARCHITECTURE_AND_CONTRACTS.md`; fact correspondence: `77_…`. Built and verified on
the isolated test schema; **not applied to development**; awaiting owner acceptance.

- **Selection plan** (`call360.applicability-selection-plan/1`): one exact published policy version (id and three
  fingerprints), a synthetic fact snapshot and its fingerprint, the evaluator contract, the evaluator's complete plan
  and its fingerprint, the outcome. `selection_source = APPLICABILITY`; `record_class = SYNTHETIC`. Immutable.
- **Outcomes:** `SURVEYS_SELECTED` (execution may begin), `NO_SURVEY_REQUIRED`, `UNRESOLVED`, `OUT_OF_SCOPE`,
  `SCOPE_UNRESOLVED` (recorded; nothing executes). Not known is never false.
- **Journey:** steps are the selected surveys in the plan's order, each at its pinned published version, each executed
  once by one existing single-survey simulation. A declared shared delivery is one step with several requirements.
- **Continuation:** only after `COMPLETED`. Otherwise `CROSS_SURVEY_POLICY_UNRESOLVED` (surveys waiting) or
  `ENDED_INCOMPLETE` (last survey), with the engine's exact terminal object. No continuation rule exists.
- **Fact correspondence** (`call360.applicability-fact-correspondence/1`): IDENTITY only; source = one published
  variable version by id and fingerprint; target = one catalog field by attribute fingerprint; same type only; chosen
  by the person; frozen in the journey's start record (`call360.applicability-journey-start/1`). Synthetic only; not
  a dependency of any policy.
- **Runtime** (`call360.applicability-journey-runtime/1`): `next → Turn | End`, `submit(item_key, expected_inputs,
  answer, idempotency_key) → Accepted | Rejected`, `state`, `verify`. The server decides the next question; a client
  proposes an answer to exactly the current turn. Optional `interaction` evidence is proposed, never accepted fact.
- 16 operations under `/api/v1/applicability`; permissions `applicability.read`, `survey.read`, `survey.simulate`
  (and `applicability.edit` to save a correspondence); no new permission. Migration `0042_applicability_journey`.
- Nothing here selects a survey for a real case, plans a callback or starts a session.
