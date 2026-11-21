# SS-02A — High-fidelity clickable prototype: build record, evidence and UX self-assessment

**Checkpoint:** SS-02A, authorised by the owner on 2026-11-21 ("SS-01 Acceptance and SS-02A Authorization").
**Status:** IMPLEMENTED AND VERIFIED, awaiting the owner's review of the actual experience. **Not accepted.**
**Scope delivered:** five screens as one authoring journey — Studio Home and Reusable Library, Survey Lego Composer,
Entry Condition Drawer, Guided Module Builder, Choice and Follow-up Designer. SS-02B, SS-02C and all backend work are
not started.

**What it is.** A working front end inside the existing Call360 application, hidden unless a build setting is on,
running on synthetic sample data held in memory. **What it is not.** It saves nothing, calls no Survey Studio API
(none exists), cannot publish, and its previews come from a small demonstration evaluator in the browser that makes
no claim of parity with the Call360 backend. A permanent "Prototype · not saved" tag says so on every screen.

---

## 1. How to open it

The development server that is normally running does not show the prototype. Start one with the setting on:

```text
cd Call360-frontend
VITE_SURVEY_STUDIO_PROTOTYPE=1 npm run dev        # stop the running dev server first: the port is fixed
→ sign in as usual, then Governance › Survey Studio   (http://127.0.0.1:5173/survey-studio)
```

"Reset to the sample library" is under the "Prototype · not saved" tag. Reloading the page also resets it.

---

## 2. What was built

| Area | Files (all new unless marked) |
|---|---|
| Canonical model | `src/features/surveystudio/model/types.ts`, `sample.ts` (synthetic library modelled on fixtures F1–F8), `ops.ts` (the operation vocabulary), `flow.ts` (guided layout and validation computed from the graph), `engine.ts` (demonstration evaluator) |
| Store | `store.tsx` — one in-memory workspace with undo and redo stacks |
| Screens | `StudioRoot.tsx` (routes, top bar), `HomePage.tsx` (A), `ComposerPage.tsx` (B), `EntryRuleDrawer.tsx` (C), `BuilderPage.tsx` (D and E), `ui.tsx` (popover, searchable picker, drawer, segmented control, inline text, tags, glyphs) |
| Style | `src/styles/survey-studio.css` — tokens and components, all scoped under `.ss` |
| Setting and wiring | `flag.ts`, `src/vite-env.d.ts`; **edited:** `src/App.tsx` (one conditional route), `src/app/nav.ts` (`navFor`), `src/app/AppShell.tsx` (navigation and title only when the setting is on), `tsconfig.json` (include the prototype config) |
| Tests | `model/model.test.ts` (18), `Studio.test.tsx` (3), `e2e/prototype/survey-studio.proto.ts` (journeys A–H), `playwright.prototype.config.ts` (a separate configuration, so the standard suite is untouched) |
| Dependencies | **edited:** `package.json`, `package-lock.json` — `@dnd-kit/core` 6.3.1, `@dnd-kit/sortable` 10.0.0, `@dnd-kit/utilities` 3.2.2 (exact versions) |

About 3,800 lines. **Not touched:** the nine pre-existing uncommitted S2-A.2 files, the backend, the database, the
OpenAPI contract (`221985e7…`, unchanged), Voice Lab, Azure GPT-Live, the other Governance modules. Nothing was
staged or committed.

**One model, by construction.** Every edit on every screen is one pure operation `(workspace, arguments) → workspace`
in `ops.ts`. The guided view stores nothing of its own: `flow.ts` derives the normal path, the lanes and the numbering
from nodes and edges each time. The rules of SS-01 are in the operations, not in the components — safe insertion, "a
placement never edits a shared definition", "exceptional outcomes start undecided", option codes fixed at creation.

**Demonstration evaluator.** Three-valued condition evaluation with a plain-language explanation tree, the follow-up
queue (configured order, dedupe, stop interrupt, single rejoin) and answer-set validation. It is cross-checked in unit
tests against the SS-01 fixtures where it implements the same rule: all 7 expected runs of F8 (module entry verdicts)
and all 4 runs and 2 rejections of F4 (queue order).

### 2.1 Dependencies: assessment before installation

| Package | Version | Licence | Peer requirement | Last published | Advisories |
|---|---|---|---|---|---|
| `@dnd-kit/core` | 6.3.1 | MIT | react, react-dom ≥ 16.8 (project: 18.3) | 2024-12 | none |
| `@dnd-kit/sortable` | 10.0.0 | MIT | react ≥ 16.8, core ^6.3.0 | 2024-12 | none |
| `@dnd-kit/utilities` | 3.2.2 | MIT | react ≥ 16.8 | 2023-11 | none |

Transitive additions: `@dnd-kit/accessibility` 3.1.1 and `tslib` 2.9.1 — five packages in all. `npm audit`: 0
vulnerabilities before and after. Used only for reordering modules and the follow-up queue, each also operable by
keyboard and by move buttons.

**`@xyflow/react` and a layout library were authorised but not installed.** The editable graph is screen G, which is
SS-02C; adding them now would add weight without improving any SS-02A screen. They will be assessed the same way when
SS-02C is authorised.

---

## 3. Evidence

All under `docs/acceptance/evidence/SS-02A/`.

| Check | Result | Evidence |
|---|---|---|
| Journeys A–H in Chromium, prototype setting **on** | **1 continuous session, passed** (about 30 s; 100+ assertions) | `prototype_journeys.txt`, `screens/` (28 screenshots) |
| Automated accessibility scan (axe, WCAG 2.x A/AA rules) on 7 screen states | **0 serious or critical findings.** The first scan found text-contrast failures (muted grey and coloured kind labels on the pale canvas); the two colour tokens were darkened and the scan re-run | `prototype_journeys.txt` |
| Frontend unit tests | **140 passed** (119 existing + 21 new) | `frontend_checks.txt` |
| Lint, type check, API contract check | clean; contract unchanged | `frontend_checks.txt` |
| `npm audit`; secret scan | 0 vulnerabilities; no leaks | `frontend_checks.txt` |
| Standard Playwright suite, setting **off** | see §3.2 | `playwright_standard.txt` |
| Specs validator | PASS (63 checks) after the naming amendment | — |

### 3.1 The journeys and their screenshots

One sign-in, one session, each step a real interaction on the prototype model (`e2e/prototype/survey-studio.proto.ts`).

| Journey | What is demonstrated and asserted | Screenshots |
|---|---|---|
| **A** Three-module survey | Empty states; search-as-you-type; create survey (name, purpose, blank or starter); add modules three ways (first-module button, library shelf, "Add a module here"); Suitability shows `Runs when Product family is ILP`; exceptional outcomes start as "Choose what happens" and the survey reports **2 to fix**; routing them clears the list | A1–A6 |
| Module opening | The approved library module is read-only; "Edit a copy for this survey" creates draft v2 pinned by this survey only | B0 |
| **B** Yes/No, two routes | "+" on a route → Yes / No; the new question inherits the former destination; switching to "Different next questions" keeps it on **Yes** only and leaves **No** as "Choose destination" (**1 to fix**); routing No to an outcome | B1–B3 |
| **C** Five options, dedicated destinations | Five options by typing five lines (Enter keeps focus); stable codes shown; per-option destinations set by picker, including **creating a new question from inside the picker**, an existing question, and two outcomes | C1–C3 |
| **D** Other + specify | One checkbox adds the option `OTHER` with its text rule; its destination starts undecided and is then routed | D1 |
| **E** Multi-select follow-ups | Exclusive option; a follow-up question per selected answer; reorder with accessible buttons (drag also available); explicit inherited rejoin; ticking Benefits then Premium still asks Premium first; an exclusive combination is rejected with the reason | E1–E3 |
| **F** Reuse | A library question placed by search; "Shared question · v1 · used in 2 places"; wording cannot be typed over while routing is freely changed; "Change…" explains definition versus placement and offers a new version for this placement or a separate question; the library still lists v1 | F1–F3 |
| **G** Condition with missing input | Keyboard drag-reorder of a module; build `Annual premium is above 12,000 SGD and (Sum assured is at least 500,000 SGD or Customer age is at least 60 years)` with a nested group; **Apply is blocked until the missing-information policy is chosen**; verdicts for sample values: Does not match → Matches → **Unknown** when the premium is cleared → Does not match when a known FALSE decides | G1–G3 |
| **H** Undo and redo | Remove a module (impact shown) → undo restores the card **and** its draft module and routes → redo → undo; keyboard undo of a move; inside the module, "2 routes lead here", delete with inbound-route impact, undo | H1–H5 |

States covered: **empty** (A1, A3, an empty module), **editing** (B–G), **error** (A4/A5 unrouted outcomes, B2
unresolved route, E3 rejected combination, G1 blocked Apply), **success** (A6, F3 "No open issues").

### 3.2 Regression

The standard suite was run after the prototype was complete, with the setting off:
**33 of 33 passed** (5.8 minutes), including the existing tests that assert the "Survey Studio" label is absent.
With the setting off the product is unchanged: no route, no navigation entry, no label. (The scan-driven contrast
change made afterwards is confined to the prototype's own stylesheet, which applies only inside the prototype.)

---

## 4. UX self-assessment

Scored against the PRD §18 requirements that apply to these five screens. **Met** = demonstrated in the prototype and
covered by a journey. **Partly** = present with a stated limit. **Not yet** = belongs to this screen set but not
built. Requirements for screens F–I are listed in §5 as out of SS-02A.

| ID | Requirement (short) | Result | Note |
|---|---|---|---|
| SS-UXE-001 | Lego blocks are the primary metaphor | Met | The composer shows module cards only; no question is rendered there |
| SS-UXE-002 | Create wizard ≤ 3 decisions | Met | Name, optional purpose, blank or starter |
| SS-UXE-003 | Library search with filters | **Partly** | Search-as-you-type on name, intent and kind. No tag, owner, status or reuse filters; no favourites or recents |
| SS-UXE-004 | "+ Add here" between, before and after | Met | Every gap; the normal connection is preserved, exceptional outcomes are flagged |
| SS-UXE-005 | Card shows eligibility, outcomes, version, count | Met | — |
| SS-UXE-006 | Inline insertion on each route | **Partly** | On every normal-path connector and on every answer through its destination picker ("create a new question here"). Not on the rejoin of a follow-up question |
| SS-UXE-007 | Normal sequence / per-option / advanced | **Partly** | "Everybody continues" and "Different next questions". No "advanced rules" (decision nodes are SS-02B) |
| SS-UXE-008 | Option editor: add, rename, reorder, duplicate, exclusive, Other | **Partly** | All except **duplicate** |
| SS-UXE-009 | Multi-select: three modes with example and preview | **Partly** | "Everybody continues" and "Follow-ups for each answer" with a live preview. **"First matching rule" (ORDERED_RULES) is not authorable** |
| SS-UXE-010 | Queue: reorder, dedupe, explicit rejoin | Met | Drag, keyboard and buttons; shared follow-up asked once; rejoin always shown |
| SS-UXE-011 | Collapsed branches keep summary and errors | Met | Lane header shows count, destination and "n to fix" |
| SS-UXE-012 | Merge badge and "view incoming" | Met | "n routes lead here" lists the sources |
| SS-UXE-013 | Searchable route picker with "create question here" | Met | — |
| SS-UXE-014 | Contextual inspector without hiding the journey | **Partly** | The entry-rule drawer overlays the right side and the canvas stays visible; there is no general inspector because everything else is edited on the card |
| SS-UXE-015 | Conditions as short sentences | Met | One chip per card; the tree lives only in the drawer |
| SS-UXE-016 | Use existing / create new / fork is explicit | Met | For modules (edit a copy) and questions (new version for this placement, or a separate question) |
| SS-UXE-019 | Undo/redo restores the canonical state | **Partly** | Whole-model snapshots, so the state restored is exact. Not the server-side inverse operations planned for production; no revision list |
| SS-UXE-020 | Impact before delete | **Partly** | Inbound routes are listed and the author chooses "normal next" or "leave undecided". No arbitrary replacement, no list of affected versions or scenarios |
| SS-UXE-021 | Saving / Saved / Offline / Conflict | **Not yet** | There is nothing to save to. The honest state "Prototype · not saved" is shown instead; the four real states need a server |
| SS-UXE-024 | Keyboard parity | **Partly** | Every drag has keyboard drag and move buttons; pickers have arrow-key navigation; focus is visible; the automated scan is clean. No formal keyboard-only or screen-reader audit |
| SS-UXE-025 | High-signal errors | Met | Each issue says what, where and how to fix, and clicking it focuses the control. No toasts are used for errors |
| SS-UXE-027 | Instructional empty states | Met | No drafts, empty survey, empty module |
| SS-UXE-028 | Consistent visual design system | Met (for these screens) | Spacing, type, radius, elevation, motion and colour tokens; reduced-motion respected |
| SS-UXE-030 | Usability sign-off separate from functional | **Owner's** | Not something a build can evidence |

Against the owner's stated expectations:

| Expectation | Assessment |
|---|---|
| Feels like a creative tool, not an administration console | Dot-grid canvas, spined module cards, large rounded type for names, inline editing, no forms-in-tables. Judgement is the owner's |
| No cramped three-panel form | Two regions at most: a collapsible library shelf and the canvas. The drawer overlays |
| No huge raw condition trees | Never on the canvas; the drawer leads with a sentence |
| No BPMN-style default canvas, no spaghetti connectors | A vertical story; branches are indented lanes with a text "rejoins Qn", not drawn lines |
| No unnecessary modal dialogs | None. Menus, pickers and confirmations are anchored popovers; the drawer is non-modal |
| Simple question creation in few steps | "+" → type → write the text. Two clicks and typing |
| No decorative controls | Every control changes the model. Features not built are absent, not disabled |
| Five-option question is effortless | Type, Enter, five times; one switch for per-option routes; one pick per destination |

---

## 5. Gap list

### 5.1 Inside the SS-02A screens

| # | Gap | Why it matters | Proposed |
|---|---|---|---|
| G1 | No persistence; reload resets (browser storage is forbidden by security rule IAM-008) | A long design session can be lost | Inherent to a prototype; real drafts arrive with the server (SS-03) |
| G2 | Save states Saving / Saved / Offline / Conflict not shown | SS-UXE-021 | With the server; could be simulated in SS-02B if wanted |
| G3 | Undo is snapshot-based, no revision history view | SS-UXE-019, SS-UX-010 | Server-side operation log (SS-03) |
| G4 | Multi-select "First matching rule" mode not authorable | SS-UXE-009, SS-QUE-004 | SS-02B |
| G5 | **Interrupt policy: only "stop" is authorable.** The model carries stop and resume, the evaluator handles both, but the designer offers stop only; "ask first, then continue" is achieved by putting that follow-up first | Owner decision 7 asks for an explicit interrupt/resume policy | **Needs the owner's view**: is a visible stop/resume switch required, or is ordering sufficient? |
| G6 | One follow-up question per answer; follow-ups cannot be multi-select; a follow-up always returns to the queue (no early exit) | SS-QUE-019, SS-01 §4 allows an outcome | SS-02B |
| G7 | Conditions built in the drawer use fixed values; reusable conditions with parameters cannot be created (existing ones can be bound); no prior-answer inputs; no "used by" count | SS-RUL-006, 010, 013 | SS-02B (with the internal condition drawer) |
| G8 | Option sets are part of the question, not a separate library asset; no Option sets or Test profiles tab | PRD §18.2 | SS-02B/C |
| G9 | Library filters, favourites, recents; "duplicate option"; "new blank module"; reuse of a draft question | SS-UXE-003, 008 | SS-02B |
| G10 | Question card has no help text, internal notes, mandatory flag, intent field or min/max selection control | SS-QUE-008, 009, 021 | SS-02B |
| G11 | Delete offers two destinations, not any; affected versions and scenarios not listed | SS-UXE-020, UX-STORY-07 | SS-02B |
| G12 | Module parameters other than rule thresholds; survey sections and outline for long surveys | SS-SUR-010, 013; 25+ modules untested | SS-02B/C |
| G13 | Wording & Delivery workspace; wording shows as a "not approved" tag only | SS-01 §7.5 | SS-02B/C |
| G14 | Accessibility: the automated scan passes on seven states, but there is no formal keyboard-only or screen-reader audit, and layouts were checked only at 1440 px wide (narrower breakpoints exist in the stylesheet, unverified) | SS-UXE-024, UX-GATE-10, SS-UX-013 | Three-width layout check and a keyboard-only walkthrough in SS-02B |
| G15 | No measurement of speed or scale (25+ modules, 40-question module) | UX-GATE-06, SS-NFR-001/002 | SS-02C / SS-10 |
| G16 | `SKIP_WITH_REASON` is offered on any module; the SS-01 rule "not on a module with a mandatory question" is not enforced | SS-D-07 | Enforce when the mandatory flag exists (G10) |
| G17 | The prototype's code and styles are in the main bundle even when the setting is off (they are inert) | Bundle size | Load on demand before any production build |
| G18 | `docs/design/DEVIATIONS.md` has no entry for Survey Studio, because that file is one of the nine uncommitted S2-A.2 files | Project rule: document UI deviations | Add the entry once S2-A.2 is committed |

### 5.2 Outside SS-02A by design

Internal condition (decision) cards and drawer — screen F; Advanced Graph — screen G; What-if Lab with profiles,
trace and coverage — screen H; Validation and Publish dashboard, diff and maker-checker — screen I; stories 08, 09, 10
in full. Story 07 is shown for two inbound routes rather than five.

### 5.3 Cannot be evidenced by a build

Moderated usability sessions and timings (UX-GATE-01 … 07), design and business sign-off (UX-GATE-12, SS-UXE-030).
The seven reference screenshots named in PRD §16 are still not in the repository; nothing was invented from them — the
design follows the PRD text.

---

## 6. Decisions that materially affect what the prototype shows

Flagged as the owner asked. None was changed silently; each is visible in the prototype.

| Decision | What the prototype does | Status |
|---|---|---|
| Sequencing (owner decision 5) | Normal outcome continues; every other outcome starts as "Choose what happens"; a jump is only forward and says "modules in between are skipped" | Decided |
| UNKNOWN (owner decision 6) | A rule cannot be applied without choosing stop or skip; the verdict panel shows Unknown distinctly | Decided |
| Follow-up queues (owner decision 7) | Explicit order, dedupe, stop interrupt, declared rejoin, explained preview | Decided — **see G5 on resume** |
| SS-D-04 approval subjects | Editing a shared module makes a draft copy "for this survey only" (a local draft module). Standalone module approval is not shown | Proposed |
| SS-D-05 outcome catalog | Five codes are offered: Completed, Clarification required, Escalate, Customer declined, Unable to verify | Proposed (illustrative list) |
| SS-D-03 upgrade / keep / fork | "New version for this placement" and "separate question" are shown; the **upgrade** flow for other placements is not | Proposed |
| SS-D-11 permissions | Anyone with `script.read` can open the prototype; there is no author / checker distinction in it | Proposed |
| SS-D-18 libraries | `@dnd-kit` used; graph libraries deferred to SS-02C | Decided, partly exercised |

---

## 7. What the owner is asked to review

1. The experience itself, with the setting on (§1): do the five screens feel like one continuous, fast authoring tool?
2. G5 — is an explicit stop / resume switch on an interrupting answer required?
3. G14 — is the automated accessibility scan enough for this review, with the three-width layout check and a
   keyboard-only walkthrough following in SS-02B?
4. Whether SS-02B should start with the gaps in §5.1 (G4–G13) or with screen F.
5. Commit authorisation, when ready. SS-02A changes are separate from the nine S2-A.2 files and can be committed
   apart from them.
