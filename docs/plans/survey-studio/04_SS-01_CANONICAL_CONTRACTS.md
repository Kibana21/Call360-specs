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

**(d) Availability — an open point raised for the owner.** SS-RUL-011 above requires a bound answer to **dominate**
the binding. The SS-02B.1 instruction says an answer not yet collected "evaluates according to the explicit UNKNOWN
policy", and the prototype accordingly allows an answer that is asked on *some* routes to the binding (it is offered
marked "not always asked", and yields UNKNOWN when it was not asked), while still rejecting an answer asked on *no*
route before it. This is **looser than SS-RUL-011 as written**. It has not been decided; see the SS-02B.2 report §6.

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
