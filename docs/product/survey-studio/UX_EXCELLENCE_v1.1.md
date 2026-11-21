# Call360 Survey Studio — UI/UX Excellence Specification

**Standalone extract of Section 18 from PRD v1.1 · 21 November 2026**

## 18. UX Excellence Standard — Make Survey Building Delightfully Fast, Clear and Powerful (P0)

### 18.1 Vision: the product should feel like a creative tool, not a workflow administration console

The Survey Studio UI must be treated as a **primary product differentiator**, not a visual wrapper around backend forms. The experience should make a new business author confident in minutes, yet allow an expert to build complex insurance logic without leaving the authoring environment. The intended interaction metaphor is **Lego construction with progressive disclosure**: discover a block, drop it into a journey, customize when it runs, open it, add questions inline, see routing consequences immediately, simulate, and publish with confidence. No business author should need to understand DAGs, ASTs, JSON, SQL, or BPMN to complete ordinary tasks.

The UX is considered complete only when **fast authoring, visual clarity, interaction reliability, explainability and aesthetic finish** pass separate acceptance gates. A graph that happens to render correctly is not sufficient. The default UI must guide users to a complete, valid outcome and prevent accidental changes to approved or reused material.

**North-star experience:** A first-time author chooses a survey purpose, searches a module library, adds three Lego modules, sees each module's short eligibility condition, opens a module, creates a multiple-choice question, picks `All choices → next` or custom routes, optionally chains follow-ups for selected answers, simulates two profiles side by side, resolves validation feedback, and submits for approval—all without a training manual or external drawing tool.

### 18.2 Navigation and information hierarchy

The application shall use a stable, consistent navigation structure with these primary surfaces:

1. **Studio Home:** My drafts, recent edits, assigned reviews, published surveys, and a prominent `Create survey` action.
2. **Reusable Library:** Searchable, filterable catalogs for Surveys, Lego Modules, Questions, Option Sets, Conditions, Test Profiles and reusable Answer Follow-up Sets. Library cards show approval state, version, use count, owner and preview.
3. **Survey Composer:** Large center canvas with a clear Start → modules → End storyline. Left library shelf and right selection inspector; no expanded AND/OR condition trees on the canvas.
4. **Module Builder:** One-click entry from a module card, with **Guided Flow** as default. The normal path reads top-to-bottom; exceptions are progressively revealed. Authors can switch to **Full Graph** without losing scroll, selected item or unsaved changes.
5. **Condition Drawer:** Contextual side drawer/modal only when a rule is explicitly selected. Show a readable sentence first, then grouped AND/OR/NOT editing and a live evaluation area.
6. **Test & Compare:** An always-available `Test journey` action opens a side-by-side customer preview, execution trace, condition explanation and coverage meter; testing must not destroy draft editing state.
7. **Validation & Publish:** A checklist of blockers/warnings, each linked to the exact module/question/rule; readable version diff and maker-checker status.

Breadcrumbs must communicate the hierarchy: `Survey > Module instance > Question / Decision`, and show whether the user is editing a reusable **definition** or an instance-specific **binding**. A persistent draft/published status indicator and precise save state are required on every authoring screen.

### 18.3 Interaction principles (mandatory, testable)

| ID | Priority | UX requirement | Observable acceptance / design rule |
|---|---|---|---|
| SS-UXE-001 | P0 | Lego blocks are the primary authoring metaphor | A survey with 20 modules is understandable from module cards without rendering all internal questions |
| SS-UXE-002 | P0 | New-author `Create survey` wizard is at most three contextual decisions | Name/purpose, choose start template or blank, enter Lego Composer; no mandatory technical setup |
| SS-UXE-003 | P0 | Library search supports search-as-you-type, tags, type, owner, status and reuse | Authors find and add an approved module without leaving the composer |
| SS-UXE-004 | P0 | `+ Add here` exists between modules, before first and after last module | Insert auto-preserves the previous normal connection and marks unconfigured exceptional outcomes |
| SS-UXE-005 | P0 | Module card shows at-a-glance eligibility, outcomes, version and count | Card can be understood within three seconds by a reader unfamiliar with JSON |
| SS-UXE-006 | P0 | Inline question insertion exists on each answer/choice/decision route | One click exposes question type menu; prior destination is preserved on designated normal route |
| SS-UXE-007 | P0 | Author chooses `Normal sequence`, `Per-option branches`, or `Advanced rules` on each choice card | Common NEXT requires one selection; advanced rule UI is hidden unless selected |
| SS-UXE-008 | P0 | Option editor supports add, rename, reorder, duplicate, exclusive option, and `Other + specify` | Option actions are visible in context and never require leaving the question card |
| SS-UXE-009 | P0 | Multi-select editor offers `All → next`, `First matching rule`, `Follow-ups for each selected option` | Every mode has a plain-English example and instant routing preview |
| SS-UXE-010 | P0 | Multi-select follow-up queue has drag-reorder, dedupe and explicit rejoin | User sees exactly which follow-ups will execute and in what order |
| SS-UXE-011 | P0 | Collapsed branches show summary, count, target, and validation state | Collapsing never hides a blocking error or unresolved option |
| SS-UXE-012 | P0 | Shared destination/merge shows a visible inbound badge and `View incoming` | All sources that lead to a shared question are inspectable in one click |
| SS-UXE-013 | P0 | Routing picker is searchable and supports `Create question here` | Users can build a branch without searching IDs or drawing an edge |
| SS-UXE-014 | P0 | Contextual inspector edits the selected asset without obscuring the full journey | Canvas stays visible and selection/scroll remain stable after edits |
| SS-UXE-015 | P0 | Conditions display as short human sentences on module/question cards | A full rule tree is never expanded on the primary canvas by default |
| SS-UXE-016 | P0 | `Use existing` / `Create new` / `Fork` distinction is explicit | Editing a reused definition never silently changes another approved consumer |
| SS-UXE-017 | P0 | Interactive what-if test can be launched from any module or question | The simulator focuses the selected step and can supply sample facts/answers |
| SS-UXE-018 | P0 | Simulator highlights executed and skipped steps and explains every decision | `Why did this run?` displays rule, input values, result and selected route |
| SS-UXE-019 | P0 | Undo/Redo covers text, options, route edits and module moves | The previous canonical state, not just its visual rendering, is restored |
| SS-UXE-020 | P0 | Delete/change operations show impact before confirmation | All inbound edges, affected option sets, scenario expectations and reuse impact are visible |
| SS-UXE-021 | P0 | Clear `Saving… / Saved / Offline / Conflict` states | No false `Saved` label before server acknowledgement; conflicts have guided resolution |
| SS-UXE-022 | P0 | Graph view automatically lays out branching and merging and preserves semantics | No line collisions with card text, deterministic fit-to-view, correct edge labels and node identity |
| SS-UXE-023 | P0 | Graph remains usable with many choice ports | Options can collapse into one summary node and expand in inspector; no 20-port spaghetti |
| SS-UXE-024 | P0 | Full keyboard interaction parity with pointer-based operations | Author can add/reorder/connect modules, options and routes with keyboard and screen reader |
| SS-UXE-025 | P0 | High-signal errors, not generic toasts | Each error explains what failed, where, why it matters, and a one-click fix destination |
| SS-UXE-026 | P0 | Side-by-side view allows author to edit and test with context preserved | Test changes never mutate draft/production data until explicitly applied |
| SS-UXE-027 | P0 | Empty states are instructional and actionable | Blank survey presents `Add first module`; blank module presents `Add first question` and example |
| SS-UXE-028 | P0 | Interface has a consistent polished visual design system | Cards, chips, text, icons, spacing, shadows, states and motion follow approved component tokens |
| SS-UXE-029 | P0 | Publish review uses human-readable change summaries | Reviewer can identify changed rule truth, option routing and follow-up queue without raw JSON |
| SS-UXE-030 | P0 | Usability sign-off is separate from functional sign-off | Product owner + design + business representative accept moderated tasks and screenshot/video evidence |
| SS-UXE-031 | P1 | Quick actions and command palette for expert authors | Command search offers add module/question, find rule, jump to broken route |
| SS-UXE-032 | P1 | Flow compare overlay for scenarios | Two profiles show differing modules and questions with a clear explanation of divergence |
| SS-UXE-033 | P1 | Batch question/option import and reusable authoring templates | Bulk operations preserve stable codes, versions and preview validation |

### 18.4 Mandatory storyboard and screen-level specifications

**Screen A — Studio Library / Workspace.** Prioritize a compelling `Create survey` action and an exceptionally usable catalog. Each Lego module tile shows name, plain-English intent, version, status, question count, outcome badges and `Add`. Support favorites, recents, search/filter and `Preview module` without creating a copy. `Reuse` must be visually distinct from `Duplicate/Fork`. Suggested content: General Verification, Suitability, High Value Review, Replacement and Closing. Use the supplied `Call360_Lego_01_Module_Library.png` as a starting reference, but modernize navigation, density and state handling.

**Screen B — Survey Lego Composer.** The central artifact must read like an assembled product, not a BPMN editor. Show `START` then 4–6 large Lego module cards and `END`, with prominent inline insertion points. Every card contains a concise `Run when: Always / ILP / Premium > …` chip; any module outcome branches display small labeled connections (`Completed`, `Clarification Required`, `Declined`). Author can reorder by drag or keyboard and can select an existing reusable entry condition from a dropdown. Show when a module is an approved shared reference versus a local draft or instance binding. The canvas should accommodate 25+ blocks by collapsing sections, zooming and a navigable outline; never force huge horizontal panning for ordinary sequential journeys.

**Screen C — Entry Condition Drawer.** Click a single rule chip to open a contextual panel. Begin with `This module runs when…` and a plain-language rule summary, not an empty programming expression box. Show `Always`, `Use saved condition`, and `Build condition` modes. `Build` supports nested `ALL`/`ANY`/`NOT`, typed fields, units and operators. Show sample customer inputs and a `Matches / Does not match / Unknown` verdict. `Save as reusable condition` is separate from `Apply only to this module instance`; version/impact warnings are mandatory.

**Screen D — Guided Module Builder.** This is the primary high-value creation screen. The normal route displays a clear numbered question story; each answer row has a destination pill and `+` insertion control. Alternate paths appear as folded side lanes with a semantic label (`No → Clarification · 3 questions`) and a `Rejoins Q8` badge. A multi-choice card initially occupies the same visual area as a Yes/No card: a compact `5 options · All → Q8` summary until expanded. Reusable question search and one-click `Add existing` remain in context. One node can have any number of inbound routes; it must not be cloned merely to appear in a branch. Use `Call360_Lego_Module_Branching.png` as visual reference.

**Screen E — Choice & Follow-up Designer.** When author adds a single-choice or multi-select question, show editable answer rows with option label, code, `Other` and `Exclusive` switches. A routing-mode segmented control offers three simple choices: `Everybody continues`, `Different next questions`, `Ask a set of follow-ups`. For single-select, each option may lead to a dedicated next question. For multi-select, the third mode opens a **sequential follow-up queue**. Show an ordered card for each selected option, a default/fallback, a global escalation override and an explicit `After follow-ups → Qx` join. Display a preview of combinations, for example `Premium + Benefits → Premium clarification → Benefits clarification → Q8`. Highlight incompatible exclusive selections and missing Other text. A short animation can illustrate a rejoin, but motion never conveys the only explanation.

**Screen F — Internal Condition Drawer.** A module can have multiple gates: entry premium/sum assured, a midflow age check, a post-answer condition. Each appears as a small decision card with `Match`, `Else`, and `Unknown`; selecting it reveals the same reusable rule editor as Screen C. Show which fields exist at this point, whether required previous answers have already been collected, and a `Test this condition` panel. Do not encourage authors to place raw condition trees directly between question cards.

**Screen G — Advanced Graph.** A graph is **an alternate synchronized editor**, not a second data model. Provide automatic hierarchical layout, merge/junction indicators, conditional edge labels, pan/zoom, minimap, collapse group, search, fit selection and `Back to Guided` controls. Include both Survey-level Module Graph and inside-Module Question Graph, clearly scoped so dozens of questions from many modules are never dumped into one all-survey view by default. Offer direct connection handles for power users but always retain click-to-connect; all edits use canonical IDs and backend validation. Respect declared ordering and accessible route descriptions.

**Screen H — Simulator / What-if Lab.** Profile picker at left, customer-visible questionnaire in center, execution trace and coverage at right. Synthetic customer presets should include typical, high-premium, high-sum-assured, missing data, older customer, policy replacement and edge boundaries. Show current module, question number, selected choices and Other response, follow-up queue, rule decisions, skip reasons, module outcomes and pinned versions. Offer `Step`, `Back`, `Restart`, `Save scenario`, `Compare profiles`, `Jump to first divergence`, and `Explain path`; run simulations through the same deterministic backend evaluator used at runtime.

**Screen I — Validation & Publish.** Replace an undifferentiated technical error log with a grouped **readiness dashboard**: `Content`, `Routing`, `Conditions`, `Reuse dependencies`, `Scenario coverage`, `Accessibility`, `Approval`. Every issue points to the affected node/route and preserves navigation back to the screen. Publishing cannot proceed if an option has no legal destination, a follow-up queue cannot terminate, Other is required but undefined, a shared version is stale/unapproved, or a test fixture has failed. Show what has changed since the last approved version, including choice codes, option order, alternative routes and priority order.

### 18.5 Visual design system and micro-interactions

- **Design language:** premium but restrained enterprise design. Use a bright, spacious canvas, purposeful typography, precise alignments, clear negative space and subtle depth. Avoid a cramped three-panel form and excessive multicolor decoration. Colors communicate node type and response state, never decoration alone.
- **Component tokens:** defined spacing scale (4/8/12/16/24/32), corner radius, type hierarchy, neutral surfaces, interactive borders, elevation and accessible semantic colors. Consistent card width and minimum touch target across Survey/Module/Graph editors. Use accessible text labels in addition to colored yes/no chips.
- **Lego cards:** recognizable shape and iconography for module type, not literal toy bricks. Make scanning a 20-module survey simple; show concise visible outputs and only expand detail when selected.
- **Question cards:** number + type + complete text + answer summary + destination, no more; option authoring happens inline on expansion. Every branch has one clearly visible `+` to grow it. Provide keyboard shortcuts as optional enhancements, not requirements for operation.
- **Condition summaries:** convert a rule to readable sentence and a compact filter chip. Surface large nested expressions as a breadcrumb-like summary plus `+N more conditions`, editable only in the rule drawer.
- **Motion:** restrained 120–220 ms transitions for expansion/reflow, with reduced-motion support. Reflow must not move the selected card out of sight or confuse keyboard focus.
- **Validation signals:** route-level actionable messages and issue count on the outer module card. No blanket green `ready` status if the backend has not validated that draft revision.
- **Feedback and confidence:** acknowledge insertion, save, reuse and branch rejoin immediately; show skeleton/loading only for true wait states; never disguise network failure as a success.
- **Responsive behavior:** desktop-first authoring, narrow-screen review, inspector drawer as needed; avoid hiding critical route choices under horizontal scrolling or clipped chips.
- **Documentation:** short inline examples, contextual `Why this path?`, starter templates, first-run coach marks and an undoable tour. Keep heavy reference documentation out of the main authoring canvas.

### 18.6 Priority interaction stories (design review walkthrough)

| Story | Business-user action | UX expected result |
|---|---|---|
| UX-STORY-01 | Add Suitability Lego after General Verification | Connector adjusts automatically; author sees eligibility chip and exceptional outcome warnings |
| UX-STORY-02 | Open Suitability and add a 5-choice single-select question | Question appears inline; author chooses one common NEXT or per-option destinations in one card |
| UX-STORY-03 | Add `Other — please specify` | Inline conditional text editor is generated; validation and route toggles visible; stable `OTHER` code preserved |
| UX-STORY-04 | Select Premium + Benefits on a multi-select question | Preview shows both follow-ups in controlled order with one shared rejoin; no duplicated question or simultaneous paths |
| UX-STORY-05 | Select Premium + Critical Risk | Explicit escalation/interrupt policy applies; trace shows whether queue is skipped or resumed |
| UX-STORY-06 | Set entry rule to Premium > 12,000 AND Sum Assured ≥ 500,000 | Canvas still shows one readable rule chip; rule drawer explains true/false/unknown outcomes |
| UX-STORY-07 | Delete a reused question with five inbound routes | Impact view identifies five sources and impacted versions; author explicitly rewires or cancels |
| UX-STORY-08 | Switch Guided → Graph → Guided after changing two routes | All edits, node identities, selection and version state remain consistent |
| UX-STORY-09 | Simulate two customer profiles | Executed/skipped Lego modules and exact branching differ visibly; `Why?` explains the rule evaluation |
| UX-STORY-10 | Submit invalid draft for publishing | Specific blocking issues are grouped and navigable, with next actions; publish button remains disabled |

### 18.7 UX performance and release acceptance gates

The following are **product acceptance targets**, subject to baseline testing on the supported desktop environment, rather than guaranteed current performance:

| ID | Measure | P0 acceptance target |
|---|---|---|
| UX-GATE-01 | First-time author completes a 3-module survey using approved Lego library | Median ≤ 5 minutes, ≥ 90% task completion without facilitator intervention |
| UX-GATE-02 | Add single-select with five distinct option routes | Median ≤ 2 minutes after creating choices; no graph drawing required |
| UX-GATE-03 | Add multi-select with `Other` and two sequential option-specific follow-ups | Median ≤ 3 minutes; all routes explicitly configured and validated |
| UX-GATE-04 | Add a Yes/No question into an existing branch | Median ≤ 60 seconds including both routes; no silent alternate destination |
| UX-GATE-05 | Understand which of six Lego modules executes for a named synthetic profile | ≥ 90% of test authors answer correctly without opening the condition AST |
| UX-GATE-06 | Navigate a complex module (40 questions, 10 exception paths) | Find an assigned question/route in ≤ 20 seconds median using search/outline |
| UX-GATE-07 | Understand a 5-incoming-edge merge | ≥ 90% of participants correctly identify rejoin behavior after a one-minute walkthrough |
| UX-GATE-08 | Incomplete-branch error discovery and repair | 100% of blocker fixtures shown on owning card and in issues panel; link focuses offending control |
| UX-GATE-09 | Guided/Graph/Simulator parity | 100% of golden fixtures yield matching canonical structure and evaluated path |
| UX-GATE-10 | Inclusive access | Keyboard-only full authoring journey, screen-reader label verification and WCAG 2.2 AA target passed |
| UX-GATE-11 | Structural authoring resilience | No unsaved draft loss after supported interrupted save/retry scenarios; all failures visible |
| UX-GATE-12 | UI quality evidence | Approved design system, high-fidelity key screen set, desktop prototype, moderated tests and recorded sign-off |

**Mandatory review evidence:** high-fidelity screen set (A–I), clickable prototype for at least Stories 01–10, user-testing notes with completion/time/error observations, accessibility audit, before/after feedback on the supplied seven baseline screenshots, performance recordings for a medium and large survey, and signed business/design/engineering acceptance. Product owner may not mark UI acceptance as met based only on CSS screenshots or a working graph canvas.

### 18.8 Anti-patterns explicitly prohibited

- Rendering the entire survey's question-and-condition graph on the primary Lego canvas.
- Requiring drag connections for common choice routing; users must be able to select destinations directly.
- Showing condition ASTs or raw JSON as the default business-author interface.
- Duplicating a shared question when two routes converge, or silently cloning approved reusable text.
- Sending multi-select responses down more than one simultaneous runtime branch without an explicit, sequential queue model.
- Treating `Other` as a bare free-text option without stable option ID, validation, provenance and documented routing.
- Inserting a new question and inventing No/Else routing without visible author confirmation.
- Saving a local/instance routing override by modifying a global reusable question or condition definition.
- Silent rerouting/deletion or silent upgrades of published dependency versions.
- Using color alone to convey status, hiding validation blockers in folded branches or relying exclusively on toasts for errors.
- Claiming a survey is ready without evaluating the exact server-saved revision and published dependency lock.
