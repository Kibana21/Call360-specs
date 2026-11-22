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

