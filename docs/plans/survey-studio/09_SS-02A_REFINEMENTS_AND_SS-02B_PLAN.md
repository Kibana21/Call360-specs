# SS-02A refinements and SS-02B plan — proposal

**Date:** 2026-11-21. **Status:** PROPOSED. **No code was changed to produce this document.**
Requested by the owner in "SS-02A Refinement and SS-02B Preparation". The owner is reviewing SS-02A as a business
author; **SS-02A's technical results are not UX sign-off**, and SS-02A is not accepted.

**What needs a decision before any work starts**
1. Approve (or amend) the seven SS-02A refinements in Part 1 and say when they may be implemented. Proposed name:
   **SS-02A.1**. They are small, frontend-only, and independent of SS-02B.
2. Approve the SS-02B plan in Part 2. **SS-02B implementation does not start until the owner has approved the
   prototype experience**, as instructed.
3. Four questions in §4.


> **Note (2026-11-21, later):** Part 1 was authorised and implemented as **SS-02A.1** with the owner's decisions
> D-122 (interruption governance: prohibited / optional / mandatory, three behaviours), D-123 (a duplicate does **not**
> inherit routing — the proposal below to copy the destination is withdrawn) and D-124 (1024 px minimum). The record is
> `10_SS-02A.1_REFINEMENTS_REPORT.md`. **Part 2 (SS-02B) remains a proposal and is not authorised.**

---

## Part 1 — SS-02A refinements (proposed checkpoint SS-02A.1)

### R1 Multi-select interruption: three explicit behaviours

Today the prototype lets an answer "stop the follow-ups" with an outcome, and nothing else. Proposed: an
interrupting answer always states one of three behaviours, in plain words, on the answer row.

| Behaviour (label in the designer) | What happens | Needs |
|---|---|---|
| **Stop and escalate** | The queue is not run. The module ends with the chosen outcome. Skipped follow-ups are listed in the preview | An outcome other than "Completed" |
| **Handle this first, then continue** | The interrupt's own question(s) are asked first; then the remaining queue runs in its configured order; then the normal rejoin | One or more interrupt questions; **permitted by the governed policy** |
| **Stop and go to…** | The queue is not run. The customer continues at an explicitly chosen destination (which may differ from the normal rejoin) | A destination; **permitted by the governed policy** |

**Where "the governed policy permits" is decided — proposal (new decision SS-D-22).** Permission belongs to the
**answer option in the question's definition**, not to the placement, because it is a statement about what that
answer means:

| Interrupt class on the option | Behaviours a placement may choose |
|---|---|
| *(none)* — an ordinary answer | Cannot interrupt |
| `MUST_ESCALATE` | Stop and escalate only |
| `MAY_INTERRUPT` | Any of the three |

- For a **shared** question the class is fixed by its approved definition; the designer shows the behaviours that are
  not permitted as unavailable, with the reason ("This answer must escalate — set by the shared question").
- For a **draft** question the author sets the class with one control ("This answer can interrupt the follow-ups").
- In the sample library, "I did not agree to this policy" is `MUST_ESCALATE`.

**Model.** `Interrupt { option, policy: STOP_ESCALATE | RESUME | STOP_REJOIN, outcome?, nodes?, rejoin? }` and
`Option.interrupt?: 'MUST_ESCALATE' | 'MAY_INTERRUPT'`. The existing `STOP` value becomes `STOP_ESCALATE`.
**Several interrupts selected at once:** `STOP_ESCALATE` wins over `STOP_REJOIN`, which wins over `RESUME`; ties by
the option order. The preview names the winner and why.
**Validation (blocks submission):** behaviour not permitted by the option's class; missing outcome, question or
destination; a stop-and-go destination that is a follow-up question.
**Evidence:** preview cases for each behaviour, a refused combination, and the "not permitted" state.

### R2 Create Blank Module

Three entry points, one small inline form (name · kind · one-line purpose), no dialog:

| Where | Result |
|---|---|
| Composer: "Add a module here" picker → **Create a blank module** | A draft module is created, placed at that position, and opened with the "Add the first question" state |
| Composer: library shelf → **New module** | Same, added at the end |
| Home: Library › Modules → **New module** | A standalone draft, opened in the builder; listed under a new "Your draft modules" |

A blank module is a **draft, shown as "Draft · not in the shared library"**. It never appears as approved. The
operation already exists in the model (`createModule`); this adds the interface and one operation that creates and
places in a single undoable step.

### R3 Answer options: duplicate and reorder inline

- **Duplicate** on each option row: a new option directly below, label "… (copy)" selected for typing, a **new stable
  code**, the same exclusivity. Its routing is **copied** (same destination or same follow-up) and the acknowledgement
  says so — "Duplicated 'Premium' with its destination" — so nothing is invented and nothing is hidden. *(Alternative:
  leave the copy's destination undecided. See §4, question 2.)*
- **Reorder** by a drag handle on the row (pointer and keyboard), by the existing up/down buttons, and by
  `Alt+↑ / Alt+↓` when the option text has focus. Order changes never change codes or routes.
- The row tools become visible on hover **and** whenever the row has keyboard focus, and are always visible on touch.
- "Other — please specify" stays last and cannot be duplicated.

### R4 Incomplete branches obvious, collapsed and expanded

| Place | Today | Proposed |
|---|---|---|
| Expanded answer row | Amber row, "Choose destination", "Not routed yet" | Keep; add an amber left edge to the whole card |
| Collapsed question | Summary line with "n to fix" | The undecided answers are **named**: "No → not decided · Other → not decided"; amber left edge; the card cannot look finished |
| Collapsed lane | "n to fix" in the header | Add the first problem in words, and an amber dashed lane line |
| A branch that ends nowhere | "The normal path stops here" only at the end of the main path | The same marker at the end of **every** lane that does not reach a question or an outcome |
| Connector | Solid grey line | **Dashed amber** where the path is broken |
| Module card in the composer | "n to fix inside" tag | Add an amber left edge; undecided outcomes keep their dashed pill |
| Top bar | "n to fix" opens a list | Add **Next issue** (and a keyboard shortcut): jumps to the next problem, opening any folded lane on the way |
| Follow-up designer | Undecided answer flagged on its row | Also flagged in "Order of follow-ups", so the queue can never look complete when an answer is undeclared |

Rule kept: folding never hides a blocker. Amber is always paired with an icon and words.

### R5 Layout at 1440, 1280 and narrower desktop widths

- **Widths checked:** 1440, 1280 and **1024** (proposed narrowest supported authoring width; §4, question 3), plus
  the project's existing 820 check as review-only.
- **Method:** each of the seven screen states at each width — screenshot, no horizontal page overflow, no clipped
  control, accessibility scan. Same harness as the rest of Call360.
- **Expected changes:** below about 1200 the library shelf becomes an overlay opened by a button, so the canvas keeps
  its width; the follow-up designer's two columns stack; the top bar keeps one row by shortening the acknowledgement
  first; the condition drawer narrows and its sample fields stack; long destination pills truncate with a full-text
  tooltip. Only 1440 has been checked so far, so some of these are predictions to be confirmed.

### R6 Keyboard-only testing of the main journeys

- **Scripted, with no mouse actions at all:** A (create a three-module survey and reorder), B (Yes/No with two
  routes), C (five options with destinations), E (follow-ups: order, rejoin, try a combination), and an undo/redo.
- **Checks:** every action reachable in a sensible tab order; visible focus at every step; focus moves to the new
  question after an insert and back to the trigger after a menu closes; Escape closes the top-most layer only; the
  drawer keeps focus inside while open and returns it on close; nothing is operable by hover alone.
- **Deliverables:** the scripted journeys, a keyboard map (the keys for each action), and a findings table with fixes.
- **Limit, stated plainly:** this proves keyboard operability. It is not a screen-reader audit, which needs a person
  with assistive technology.

### R7 "Prototype — not saved" stays; no simulated persistence

Confirmed. The tag stays on every screen and no "Saved" state will be shown or simulated. The earlier suggestion to
simulate Saving / Saved / Offline / Conflict in the prototype (report gap G2) is **withdrawn**; those states will be
designed against the real server later.

### Verification for SS-02A.1

Unit tests for the new operations and rules; the A–H journeys extended (interrupt behaviours, blank module, option
duplicate and reorder, next-issue); keyboard-only journeys; seven states × three widths with accessibility scans;
the standard suite with the setting off; lint, types, contract unchanged, audit, secret scan.

---

## Part 2 — SS-02B plan

**Scope (owner's list):** Internal Condition Builder · Advanced Graph Editor · Profile-based Journey Simulator ·
Guided ↔ Graph canonical state parity · first-matching-rule multi-select routing · parameterised reusable conditions.
**Not in SS-02B:** backend persistence, production runtime, migrations, APIs, the Validation and Publish dashboard.
Still frontend-only, sample data, behind the same setting, off by default.

### 2.1 One model — how identities, branches and undo/redo are preserved

**There is no graph data model.** The graph is drawn from the same `Module { nodes, edges, routing }` the guided view
reads, and it changes that model only through the same operations.

```text
                     Workspace (canonical: modules, nodes, edges, routing, conditions…)
                          ▲                                   │
   operations (ops.ts) ───┘                                   ├─ buildFlow()   → Guided view      (derived, stores nothing)
   setEdge · insertQuestion · deleteNode · setMode · …        ├─ toGraph()     → Graph view       (derived, stores nothing)
          ▲                         ▲                         └─ run()         → Simulator        (derived, stores nothing)
   Guided handlers            Graph handlers
```

| Concern | Rule in SS-02B |
|---|---|
| **Node identity** | A node keeps its id (`n4`, `d1`) for its life. Neither view ever renumbers, recreates or clones a node. The labels "Q3", "Q1a" are *display numbers* derived from the current routes and may change when routes change; the graph shows both |
| **Edge identity** | An edge keeps its id. Connecting in the graph calls `setEdge(from, on, to)` — the same call the destination picker makes. Each answer is its own connection point, so an edge always belongs to exactly one answer |
| **Branches and merges** | A merge is several edges into one node in both views. The graph never duplicates a shared destination; the guided view shows it once with "n routes lead here" |
| **Follow-up queues** | Drawn as a group attached to their question with numbered order and one rejoin edge. Order is the array order in the model; the graph cannot express an order the model does not have |
| **Layout** | Positions are computed by the layout library on every change. Any manual nudging is **view state**: not in the model, not in undo, lost on reload. Layout never affects behaviour |
| **Undo / redo** | One history for the workspace, shared by both views. An edit made in the graph is undone from the guided view and the reverse. Selection, zoom, pan, folded lanes, the open drawer and the simulator session are **not** in the history. After an undo, a selection that no longer exists is cleared |
| **Simulator** | A run reads the workspace as it was when the run started. If the model changes, the run is marked **out of date** and offers Restart; it never continues silently on a changed model |
| **Shared versus placement** | Unchanged: routing is the placement's; wording, options and a shared condition's logic are the definition's. The graph offers no way round this |

**Parity is tested, not asserted:** for every sample module and every SS-01 fixture, a script performs the same edit
through the guided handlers and through the graph handlers and requires the two resulting workspaces to be identical;
and a browser journey edits in one view, switches, and undoes in the other.

### 2.2 Internal Condition Builder

- A **Decision** is a node of a new type in the existing node list (`{ id: 'd1', type: 'DECISION', binding }`) with
  edges on `MATCH`, `NO_MATCH` and, when chosen, `UNKNOWN`. The type was anticipated in SS-01 and in the prototype's
  types.
- **Insert** through the same "+" menu: "Add a condition". Safe insertion applies: the former destination goes to
  **Otherwise**; **Matches** starts undecided; the missing-information behaviour must be chosen (an `UNKNOWN` route, or
  stop for review).
- **Guided view:** a compact decision card — one sentence, three rows `Matches → … / Otherwise → … / Unknown → …` —
  and the "Matches" path as a lane, exactly like an answer.
- **The drawer is the same component as the entry-rule drawer**, plus "What is known here": catalog fields, and the
  answers to earlier questions that every route to this point passes through. An answer that might not have been
  asked is listed as unavailable, with the routes that miss it.
- **Earlier answers as inputs:** "the answer to Q2 is No", "the answer to Q4 includes Premium".

### 2.3 Parameterised reusable conditions

- In the builder, any value can be turned into a **named setting** ("Premium threshold"). Saving to the library keeps
  the settings as the condition's parameters.
- Using a saved condition asks for the settings' values **for this placement only**; the chip reads with the values
  filled in.
- A saved condition shows "used in n places". Changing its logic follows the same choice as a shared question:
  **new version for this placement** or **a separate condition**. Other placements keep their version.
- Applies equally to module entry rules and internal decisions — one condition library.

### 2.4 First-matching-rule multi-select routing

- Third mode on a multiple-choice question: **"First matching rule"**, beside "Everybody continues" and "Follow-ups
  for each answer".
- An ordered list: `If the answer includes [any of | all of | none of] [options] → destination`, reorderable by drag,
  keyboard and buttons, then a mandatory **Otherwise → destination**.
- "Try a combination" shows which rule wins and names the rules that also matched but lost.
- Validation: missing "Otherwise"; a rule with no options or no destination; a rule that can never win because an
  earlier rule always matches first (warning).
- The three modes stay mutually exclusive per question, as SS-01 requires.

### 2.5 Advanced Graph Editor

- **Two scopes, never one giant canvas:** a module's questions and decisions; and the survey's modules with their
  outcome routes. The survey graph is read-and-navigate in SS-02B (editing module routes stays on the cards).
- **Module graph, editable:** automatic layered layout top-to-bottom with merges; pan, zoom, fit, minimap, search;
  select a node to edit it in the same card used by the guided view, shown beside the canvas; connect by dragging
  from an answer's handle **or** by the same destination picker (click-to-connect, keyboard-operable); delete with
  the same impact check.
- **No spaghetti:** a question with many answers shows them as rows inside one node; answers sharing a destination
  share one bundled edge with a count; follow-ups are a grouped block; undecided answers have an amber stub instead
  of an edge.
- **Text alternative:** an outline list of nodes and their routes, kept in step with the canvas, for keyboard and
  screen-reader use.
- **`Guided | Graph` switch** in the builder keeps the selected node and scrolls it into view.

### 2.6 Profile-based Journey Simulator

- **Test profiles** as a library tab: seven synthetic presets (standard term life; ILP high premium; high sum assured
  low premium; older customer near a threshold; policy replacement; missing premium; needs clarification). Editable
  copies; a field can be set to "missing".
- **Run a survey or one module** in a side panel over the editor: the customer's question, the answer controls for
  every type including Other text, **Next**, **Back** (supersedes the later answers), **Restart**.
- **Trace:** each step with a "Why?" — the condition sentence, the values used, the result, the route taken, queue
  built, follow-ups skipped or asked once, module activated or skipped and the reason, blocked for missing data.
- **Highlight** on both views: asked, skipped, not reached.
- **Compare two profiles** side by side with the first point where they differ.
- **Coverage** as counts of routes, answers and condition results exercised — worded so it cannot be read as
  "correct".
- **Honesty:** a browser demonstration evaluator, labelled on the panel. Its check is strict: it must reproduce **all
  25 expected runs and 7 rejections of the eight SS-01 fixtures** (it reproduces F4 and F8 today).

### 2.7 Dependencies — checked, not installed

Assessed in a throwaway folder outside the repositories; the project's `package.json` was not touched.

| Package | Version checked | Licence | Requires | Adds | Advisories | Assessment |
|---|---|---|---|---|---|---|
| `@xyflow/react` | 13.0.2 (latest) | MIT | React ≥ 18 (project 18.3) | `@xyflow/system`, `zustand`, `classcat`, `react-compiler-runtime`, six small `d3-*` packages | 0 | **Suitable, but not this version.** 13.0.0 came out five days before this check, with three releases in two days. Recommend the mature line **12.12.1** (2026-11-02), exact pin, re-checked the same way before installing |
| `@dagrejs/dagre` | 3.1.3 | MIT | — | `@dagrejs/graphlib` | 0 | **Recommended layout library.** Small, layered layout with merges, runs in the page |
| `elkjs` | 0.12.1 | EPL-2.0 or GPL-3.0-or-later | — | none | 0 | **Not recommended.** Copyleft licence needing legal review, about 8 MB, normally run in a web worker, which the product's content-security policy would need to allow |

Together about 22 packages. `zustand` arrives as an internal dependency of the graph library; the prototype's own
state stays in its existing store. The graph is loaded only when the Graph view is opened.
**Fallback if the graph library is declined at install time:** a read-only graph drawn with the layout library alone;
parity and the simulator are unaffected.

### 2.8 Sub-checkpoints

| Sub-checkpoint | Contents | Exit |
|---|---|---|
| **SS-02B.1** Conditions and rules | Decision nodes; internal condition drawer; earlier answers as inputs; parameterised reusable conditions; first-matching-rule mode | Owner walkthrough; unit tests incl. fixture F6 (condition with UNKNOWN); journeys for a decision with three routes and an ordered-rule question |
| **SS-02B.2** Graph and parity | Module graph editor; survey graph (read); view switch; outline alternative | Parity script green on all sample modules and fixtures; journey: edit in Graph, see it in Guided, undo from Guided |
| **SS-02B.3** Simulator | Profiles; step, back, restart; trace with "Why?"; highlight; compare; coverage | All 25 fixture runs reproduced; journey: two profiles take visibly different paths |

Each ends with the same evidence set as SS-02A: journeys with screenshots, unit tests, accessibility scan at three
widths, keyboard checks for what it adds, the standard suite with the setting off, and a self-assessment with gaps.

### 2.9 Preservation

Setting off by default; the nine S2-A.2 files untouched; no change to Voice Lab, Azure GPT-Live, Assignment Rules,
Finding Rules, Review Workbench or seeded synthetic cases; no backend, database or API change; no paid call; no commit
or push without authorisation.

---

## 3. Risks

| Risk | Mitigation |
|---|---|
| The graph becomes the "real" editor and the guided view a façade | The guided view is finished first; the graph gets no capability the guided view lacks; parity script is a gate |
| Display numbers (Q3, Q1a) shift as routes change and confuse authors | Stable node code visible on demand; "what changed" acknowledgement after each edit; raise with the owner if it confuses in review |
| Graph accessibility | Outline alternative; every graph action also available by picker and keyboard |
| A brand-new major version of the graph library | Pin the mature line; exact versions; re-check at install |
| The demonstration evaluator is mistaken for the engine | Label on the panel; fixture reproduction is its only claim |
| SS-02B is large | Three sub-checkpoints, each separately reviewable |
| Interrupt permission placed on the option definition may not match how the business thinks about it | Decision SS-D-22 put to the owner before R1 is built |

---

## 4. Questions for the owner

1. **Interrupt permission (SS-D-22):** is it right that the *answer option's definition* says whether it must
   escalate or may interrupt, with each placement choosing only among what is permitted?
2. **Duplicating an option:** copy its destination (proposed), or leave the copy's destination undecided?
3. **Narrowest supported authoring width:** 1024 px (proposed)?
4. **Sequence:** implement the SS-02A refinements now as SS-02A.1 so the experience under review is the refined one,
   then decide on SS-02B — or review first and batch the refinements with further feedback?
