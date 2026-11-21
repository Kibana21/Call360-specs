# SS-01 · Part D — SS-02 prototype implementation plan

**Checkpoint:** SS-01 (this document is a plan). **SS-02 is not authorised.** It starts only on the owner's explicit
`IMPLEMENT SS-02` (or a named sub-checkpoint below), after the SS-01 decisions it depends on are approved.

**Purpose of SS-02.** Demonstrate the Survey Studio experience with **real interactions** — clicking, typing,
dragging, keyboard, undo — across the nine screens and ten stories of PRD §18, before any backend work. It is the
first evidence for UX-GATE-12 and the place to change the design cheaply. It is not a set of screenshots and not a
graph editor with a simplified screen in front of it.


> **Note (2026-11-21):** the owner authorised **SS-02A** with a different cut from §8 below: five screens — Home and
> Library, Composer, Entry Condition Drawer, Guided Module Builder, Choice and Follow-up Designer (screens A–E) — as
> one continuous journey, with journeys A–H as evidence. The record of what was built, the evidence, the UX
> self-assessment and the gap list are in `08_SS-02A_PROTOTYPE_REPORT.md`. Remaining for SS-02B / SS-02C: screens
> F (internal conditions), G (graph), H (what-if lab), I (validation and publish) and the gaps listed there.

---

## 1. What SS-02 is and is not

| It is | It is not |
|---|---|
| A working front end inside the existing React application, on sample data | A backend, API, schema or contract change (none) |
| Built on the **SS-01 canonical JSON** and the **SS-01 operation vocabulary**, so Guided and Graph views edit one model | A separate "prototype model" to be thrown away |
| Complete enough to walk all ten stories end to end, with keyboard | Persistent: nothing is saved to the server; a banner says so |
| Hidden unless a front-end build setting is on | Visible in normal builds; existing tests and labels are unaffected with the setting off |
| Evidence for design review and for preparing moderated tests | Proof of persistence, concurrency, scale or server validation — those are SS-03 onward |

**One honest caveat.** The PRD requires simulation to run through the backend's deterministic evaluator. The
prototype has no backend, so it carries a small in-browser engine that implements the SS-01 contracts for the sample
data. It is labelled as a demonstration engine and is **replaced by the server** when SS-04 exists; it is never an
authority and never ships as one.

---

## 2. Dependencies on decisions

| Needed before SS-02 starts | Why |
|---|---|
| SS-D-02 binding contract | The question card shows wording with its approval state |
| SS-D-06, SS-D-07, SS-D-10 | The composer, the rule drawer and the follow-up designer encode these policies |
| SS-D-09 instance contract | Breadcrumbs, merge badges and the trace use instance keys |
| SS-D-18 libraries | Decides how real the drag and graph interactions can be |
| SS-D-20 amendment text | The label "Survey Studio" appears on screen |
| The seven reference screenshots named in PRD §16 | Still not in the repository; without them the design is made from the PRD text alone |

---

## 3. Architecture of the prototype

```text
src/features/surveystudio/            (all new files)
  model/        types for the SS-01 canonical JSON; pure functions only
    operations  apply(model, operation) → {model, inverse}; the SS-01 operation vocabulary
    validate    the SS-01 validation rules needed by the stories → issues with object keys
    engine      demonstration interpreter of the SS-01 execution contracts (sample data only)
    describe    plain-language summaries of conditions and routes
  store/        one in-browser store: current model, undo and redo stacks, save-state simulation, selection
  sample/       the eight SS-01 fixtures plus a richer sample library and seven synthetic profiles
  design/       tokens and the component set (§5)
  screens/      A … I
styles/survey-studio.css              (new; tokens scoped to a `.ss` root so no existing screen changes)
```

- **One model, two editors.** Guided and Graph views both dispatch the same operations to the same store. There is
  no conversion step; switching views keeps selection and scroll (story 08).
- **Undo/redo** applies the recorded inverse operation, restoring the model itself (SS-UXE-019).
- **Save states** are simulated truthfully for design review: `Saving…` → `Saved`, plus a switch in the prototype's
  own toolbar to force `Offline` and `Conflict`, so those states can be reviewed (SS-UXE-021).
- **Routing.** One route subtree `/survey-studio/*` added to `App.tsx` and one navigation entry in `nav.ts`, both
  rendered only when the build setting is on.
- **No new server calls** beyond what the application shell already makes for the signed-in user.

**Files of the nine uncommitted S2-A.2 changes are not touched** (`ScriptEditor.tsx`, `ScriptFamilyPage.tsx`,
`ScriptLibraryPage.tsx`, `ScriptPages.test.tsx`, `shared.tsx`, `app.css`, `DEVIATIONS.md`, `f6-checks.ts`,
`script-studio.spec.ts`). Consequences: styles go in a new stylesheet, and the design-deviation entry for Survey
Studio is recorded in the SS-02 acceptance record until `DEVIATIONS.md` is committed. Committing S2-A.2 first would
remove this constraint.

---

## 4. Libraries (SS-D-18)

| Need | Recommended | If not approved |
|---|---|---|
| Drag-reorder of modules, options and queue items, with keyboard and screen-reader support | `@dnd-kit/core` + `@dnd-kit/sortable` | In-house pointer reorder plus the move-up/down controls (which exist in any case) |
| Graph canvas: pan, zoom, fit, minimap, selectable nodes and edges, connection handles | `@xyflow/react` | In-house SVG, read-only, no minimap |
| Layered automatic layout with merges | `elkjs` or `@dagrejs/dagre` | In-house simple layering |

Versions would be pinned exactly; licences and maintenance status checked before adding. Guided authoring (screens
B–F) does **not** depend on the graph libraries: if they are declined, eight of the nine screens are unaffected and
screen G is delivered read-only.

---

## 5. Design system (first deliverable)

| Tokens | Values |
|---|---|
| Spacing | 4 · 8 · 12 · 16 · 24 · 32 |
| Type | A defined scale for page title, card title, body, caption, chip |
| Shape and depth | Radius steps; three elevation levels (canvas, card, overlay) |
| Colour | The existing palette, with semantic roles: node type, answer state, validation state — each always paired with an icon and a text label |
| Motion | 120–220 ms for expand, insert and reflow; disabled under reduced-motion |
| Targets | Minimum pointer target size; visible focus ring on every interactive element |

**Components:** Lego module card · question card · decision card · outcome pill · route chip and destination picker ·
condition chip · option row · follow-up queue list · branch lane (collapsed and expanded) · merge badge ·
insertion point · inspector · drawer · save-state indicator · issue badge and issues panel · readiness tile ·
trace row · coverage meter · empty states · breadcrumb with a definition / instance badge · "not approved" wording tag.

Layout rule: library shelf (left) and inspector (right) are collapsible; drawers overlay. The canvas never drops
below a readable width — no cramped three-pane form.

---

## 6. The nine screens

| Screen | Prototype content | Real interactions demonstrated |
|---|---|---|
| **A · Studio Home and Library** | `Create survey` (three decisions: name and purpose → template or blank → composer); My drafts, Assigned reviews, Recent, Published; library tabs Surveys · Modules · Questions · Option sets · Conditions · Profiles | Search as you type; filter by type, status, owner, tag; favourite; `Preview` a module without copying; `Add` versus `Fork` |
| **B · Survey Lego Composer** | `START → module cards → END`; each card: name, version, `Run when…` chip, question count, outcome pills, issue count, shared/local badge; outline for long surveys | `+ Add here` at every gap; drag and keyboard reorder; select → inspector; route an outcome from a pill; delete with impact; collapse sections; 25-module sample stays readable |
| **C · Entry Rule Drawer** | "This module runs when…" sentence; `Always` / `Use saved condition` / `Build condition`; typed rows; ALL / ANY / NOT groups; UNKNOWN policy; sample values with `Matches / Does not match / Unknown` | Build a nested rule; change a sample value and see the verdict change; `Apply to this module only` versus `Save as reusable` with an impact note |
| **D · Guided Module Builder** | Numbered normal path; folded exception lanes with `No → Clarification · 3 questions` and `Rejoins Q8`; merge badges; `Add existing question` | `+` on any answer row → question type menu; destination pill → searchable picker with `Create question here`; expand/collapse; `View incoming`; undo/redo |
| **E · Choice and Follow-up Designer** | Option rows (text, code, `Other`, `Exclusive`); `Everybody continues` / `Different next questions` / `Ask a set of follow-ups`; ordered queue, interrupt row, `After follow-ups → Qx`; combination preview | Add, rename, reorder, duplicate options; toggle `Other` and set its text rule; switch mode; drag the queue; tick sample options and watch the preview |
| **F · Internal Condition Drawer** | Decision card `Match / Else / Unknown`; same drawer as C; "available here" list of fields and earlier answers | Bind a prior answer as an input; see an unavailable answer flagged; test the condition |
| **G · Advanced Graph** | Module graph and survey-level module graph; automatic layered layout; merges; edge labels; options summarised on a node | Pan, zoom, fit, minimap, search; select a node → same inspector; change a route by click-to-connect (and by handle if the library is approved); `Back to Guided` |
| **H · What-if Lab** | Panel over the editor: profile, customer questionnaire, trace and coverage | Pick a preset; answer step by step including multi-select and Other; `Back`, `Restart`, `Save scenario`; compare two profiles; `Why?` opens the explanation tree; executed and skipped steps highlighted on the canvas |
| **I · Validation and Publish** | Readiness dashboard by group; change summary since the last approved version; maker-checker panel | Click an issue → focus the exact control, even inside a folded lane; fix it and watch the count fall; `Submit` disabled with the reason stated |

Every screen also has its empty state, loading state and an error state, and shows the breadcrumb, the draft /
published indicator and the save state.

---

## 7. The ten interaction stories — acceptance scripts

Each story is delivered as (a) a scripted Playwright walkthrough on the prototype and (b) a short script the owner can
follow by hand. "Passes" means every listed observation is true.

| Story | Steps | Observations |
|---|---|---|
| **01** Add Suitability after General | In the composer, press `+` after General Verification; pick Suitability | Card inserted in place; General's `Completed` still leads onward through the new card; chip reads `Run when: Product is ILP`; a note shows the new module's unrouted exceptional outcome; undo removes it and restores the original connection |
| **02** Five-choice single-select | Open Suitability; `+` on a route; choose single-select; enter five options | Card shows `5 options · All → Q…`; switching to `Different next questions` reveals five destination pills in the same card; no edge was drawn by hand |
| **03** Add `Other — please specify` | Toggle `Other` on the option list | An `OTHER` row appears with its text rule (required, length) and its own destination; code is fixed as `OTHER`; the preview shows the text box only when Other is chosen |
| **04** Premium + Benefits | On a multi-select, choose `Ask a set of follow-ups`; map two options; tick both in the preview | Preview reads `Premium clarification → Benefits clarification → Q8`; changing click order does not change it; one rejoin |
| **05** Premium + Critical Risk | Mark Critical Risk as an interrupt with outcome Escalate; tick both in the preview | Preview reads `Critical risk → Escalate · 1 follow-up skipped`; the simulator trace shows the same |
| **06** Compound entry rule | Build `Premium > 12,000 AND Sum assured ≥ 500,000` | The card still shows one chip; the drawer shows the three verdicts for sample values, including Unknown when a value is cleared |
| **07** Delete a question with five inbound routes | Delete it | Impact dialog lists the five sources and the versions affected; the author must pick a replacement destination or cancel; cancel changes nothing |
| **08** Guided → Graph → Guided | Change two routes, switch views twice | The same nodes, routes and selection in both views; no conversion message; undo still works across the switch |
| **09** Two profiles | Run "Term life, low premium" and "ILP, high premium" side by side | Different executed and skipped modules are highlighted; `Why?` on a skipped module shows the rule, the input values and the result |
| **10** Submit an invalid draft | Leave one answer unrouted; open Validation | Blockers grouped by area; clicking one focuses the unrouted answer; `Submit` is disabled and says why |

---

## 8. Sub-checkpoints

Each is separately demonstrable and can be authorised on its own.

| Sub-checkpoint | Contents | Stories | Exit |
|---|---|---|---|
| **SS-02a** Foundation and composer | Design tokens and components; model, operations, store, undo/redo; screens A, B, C | 01, 06 | Owner walk-through of A–C; keyboard-only assembly of a three-module survey |
| **SS-02b** Guided builder | Screens D, E, F; safe insertion; route picker; option editor; follow-up designer | 02, 03, 04, 05, 07 | Owner walk-through; each story's script passes |
| **SS-02c** Graph, What-if Lab, Validation | Screens G, H, I; demonstration engine; trace and coverage; readiness | 08, 09, 10 | All ten stories pass; parity check Guided = Graph on the eight fixtures |

---

## 9. Verification and evidence

| Check | How |
|---|---|
| Existing product unaffected | With the build setting **off**: all current unit tests and all 33 Playwright journeys pass unchanged, including the tests that assert the label is absent |
| Stories | Ten scripted Playwright walkthroughs with the setting **on** (a separate Playwright project, so the standard run is untouched) |
| One model | For each of the eight fixtures: the same edit made in Guided and in Graph produces an identical model; undo returns the identical model |
| Contracts | The demonstration engine reproduces every expected run of the eight SS-01 fixtures (25 runs, 7 rejected answers) |
| Accessibility | axe on all nine screens at three widths; keyboard-only walk of stories 01–04 and 10; focus order and names reviewed |
| Unit tests | Operations and their inverses; validation rules; plain-language summaries |
| Evidence pack | Screenshots of screens A–I, short recordings of the ten stories, the owner's walk-through notes, a list of design changes made in response |
| Hygiene | Lint, type check, contract check (unchanged contract), secret scan; no paid call; no backend change |

**Prepared for the owner, not performed by the build:** task scripts and a results sheet for moderated sessions
(UX-GATE-01 … 07). Those sessions and the design / business sign-off (SS-UXE-030, UX-GATE-12) are the owner's to run.

---

## 10. Risks specific to SS-02

| Risk | Mitigation |
|---|---|
| A polished prototype is mistaken for a finished product | Permanent "Prototype — sample data, nothing is saved" banner; SS-02 acceptance record states what is not proven |
| The demonstration engine drifts from the future server engine | It is tested only against the SS-01 fixtures, which become the server's golden tests; it is deleted from the simulator path in SS-07 |
| Graph screen quality depends on a library decision | Decide SS-D-18 first; guided screens do not depend on it |
| Label tests and the specs validator | Setting off by default keeps existing tests green; the naming amendment (Part B §11) should be applied before or with SS-02a |
| Design made without the reference screenshots | Ask for them before SS-02a; otherwise record that the design follows the PRD text only |
| Scope creep into persistence | SS-02 has no server calls by definition; anything needing the server waits for SS-03 |

---

## 11. What carries forward into the real implementation

Design tokens and components; screen layouts; the operation vocabulary (which becomes the server's operations API in
SS-03); the model types (to be generated from the server contract once it exists); the story walkthroughs (re-pointed
at the real API); the plain-language summaries. What does not: the in-browser store's persistence stand-in and the
demonstration engine.
