# SS-00 · Part 3 — Implementation plan, UI design plan, risks

**Checkpoint:** SS-00 (planning only). **Date:** 2026-11-21. **Status:** PROPOSED. No phase below is authorised; each
needs its own explicit `IMPLEMENT SS-nn` after its design is reviewed (workspace `CLAUDE.md` §10).

Covers deliverables **J** (phased plan), **K** (UI design plan) and **L** (risks, unresolved decisions,
recommendations).


> **Note (2026-11-21, SS-01):** the SS-D-09 restriction mentioned in R4 and §L.2 was rejected by the owner; the SS-02
> plan here is detailed in `07_SS-02_PROTOTYPE_PLAN.md` (see `README.md`).

---

## J. Phased implementation plan

### J.1 Sequence at a glance

| Phase | Name | Repos | PRD phase | Produces |
|---|---|---|---|---|
| SS-00 | Assessment and design | specs | — | These three documents (this checkpoint) |
| SS-01 | Decisions and contracts | specs | P0-A (spec part) | ADRs, canonical JSON Schemas, operation vocabulary, golden fixtures |
| SS-02 | High-fidelity UI prototype | frontend | P0-B (design part) | Clickable screens A–I, stories 01–10, design tokens — on fixture data, no backend change |
| SS-03 | Canonical model, condition engine, validator, compiler | backend | P0-A | Tables, operations API, validation, manifest/3 |
| SS-04 | Graph execution in simulation | backend | P0-C (engine part) | Controller navigation, queue, back/edit, pause, trace, profiles, coverage |
| SS-05 | Library and Survey Composer | frontend + backend | P0-B | Screens A, B, C on the real API |
| SS-06 | Guided Module Builder and Choice Designer | frontend | P0-B | Screens D, E, F; undo/redo; autosave states |
| SS-07 | Advanced Graph and What-if Lab | frontend | P0-C | Screens G, H; parity tests |
| SS-08 | Validation, review, publish, reuse governance | backend + frontend | P0-D (governance part) | Screen I; module approval; impact and upgrade; conversion of linear versions |
| SS-09 | Operational runtime integration | backend | P0-D (runtime part) | Runtime API writing operational tables; evaluation, findings, review on graph runs |
| SS-10 | Hardening and UX acceptance | all | release gate | Scale, accessibility, cross-browser, moderated usability evidence, retirement decision |

**Why this order.**
- The prototype (SS-02) comes before backend work because the UX is the stated differentiator and is far cheaper to
  change on fixtures than after APIs exist. It is built on the canonical JSON and operation vocabulary agreed in SS-01,
  so it tests the model as well as the look, and its components carry forward.
- The engine (SS-03, SS-04) comes before the real editors, as the PRD requires ("do not implement a Guided Editor with
  a separate simplified tree schema").
- Operational runtime (SS-09) is last and separately authorised (SS-D-17).

### J.2 Phase detail

Every phase has the same **standing regression gate**: all existing backend tests (511 today), frontend unit tests
(119) and Playwright journeys (33) pass; lint, type checks, contract check and secret scan are clean; the specs
validator passes; Voice Lab tests are untouched and green; no paid provider call is made.

#### SS-01 — Decisions and contracts (specs only)
- **Scope.** Record the approved SS-D decisions as new ADRs (the next free numbers after ADR-0009); JSON Schemas for survey, module, question, option set,
  condition AST, binding, follow-up plan, manifest/3 and the decision trace; the operation vocabulary; the field
  catalog v1 (which existing facts are exposed: product family, ILP flag, channel, premium amount, frequency and term,
  sum assured, age from date of birth, replacement indicator, risk band — each checked against `0003`/`0004` tables);
  outcome catalog; the 52 golden scenarios (SS-AT-001…052) as fixture files; traceability table SS-* → phase → test.
- **Gate.** Owner signs the schemas and the decision list. Fixtures validate against the schemas.
- **Rollback.** Documents only.

#### SS-02 — High-fidelity UI prototype (frontend only)
- **Scope.** Screens A–I and stories UX-STORY-01…10 as a clickable prototype inside the existing React app, behind a
  prototype-only route, driven by an in-browser store that holds the SS-01 canonical JSON and applies the SS-01
  operations. Design tokens and the component set of §K.2. No backend, API, schema or contract change.
- **Gate.** Owner walk-through of the ten stories; written feedback against the seven baseline screenshots (if the
  owner supplies them — see §L.2); axe clean; keyboard walk-through of stories 01–04. Decision on libraries (SS-D-18)
  taken here if the owner wants drag and a live graph in the prototype.
- **Rollback.** Remove the prototype route; nothing else depends on it.
- **Honest limit.** A prototype shows interaction quality; it does not prove persistence, concurrency or scale.

#### SS-03 — Canonical model, condition engine, validator, compiler (backend)
- **Scope.** Additive migrations for the §F tables; condition engine with explanation tree; operations endpoint with
  inverse recording; validator and compiler; manifest/3; read APIs for the libraries; feature flag.
- **Requirements.** SS-ROU-001…008, 013, 015; SS-RUL-001…013; SS-QUE-002…011, 016…021, 023; SS-MOD-001, 002, 004,
  007, 009…011; SS-SUR-005…008; SS-VAL-001…007; SS-NFR-010, 014, 018.
- **Gate.** Golden graph and condition fixtures pass (truth tables incl. UNKNOWN, boundary values, cycles, ambiguity,
  future-answer dependency, queue validation); property-based tests on the validator (random graphs never crash, a
  valid graph always compiles, compile is deterministic); migration up/down on a clean database; OpenAPI regenerated
  and the frontend client check passes; existing published manifests hash to the same SHA as before.
- **Rollback.** Flag off; downgrade the phase's migrations (new tables only).

#### SS-04 — Graph execution in simulation (backend)
- **Scope.** Controller navigation over the compiled graph; follow-up queue; back/edit with supersession;
  pause/resume; decision trace; module-only runs; synthetic profiles; route and choice coverage; routing preview;
  UNKNOWN simulation.
- **Requirements.** SS-ROU-002, 009, 010, 013, 014; SS-QUE-004, 019, 020, 022, 024; SS-SIM-001…007, 009, 010;
  SS-MOD-012; SS-RUN-002, 004 (simulation form).
- **Gate.** **Replay equivalence:** every stored simulation event log and every existing scenario yields the
  identical state, outcome and evaluation as before the change. All runtime golden scenarios pass in simulation
  (SS-AT-002…006, 008…015, 019, 020, 023…026, 029, 033…047). p95 step time measured against SS-NFR-003.
- **Rollback.** Flag off; `/2` execution path is unchanged by construction and proven by the replay test.

#### SS-05 — Library and Survey Composer (frontend + small backend)
- **Scope.** Studio home, library tabs, create-survey wizard, composer with module cards, `+ Add here`, reorder
  (drag and keyboard), inspector, entry-rule drawer, outcome connectors, delete with impact.
- **Requirements.** SS-SUR-001…011; SS-UX-001, 002, 004, 007, 008, 011, 012; SS-UXE-001…005, 014…016, 020, 027, 028.
- **Gate.** Playwright journeys for SS-AT-001, 002, 049 (scripted form); keyboard-only assembly of a 3-module survey;
  axe clean at three widths; a 25-module fixture stays navigable.

#### SS-06 — Guided Module Builder and Choice Designer (frontend)
- **Scope.** Guided flow, inline insertion, route picker with "create question here", collapsible branches with
  summaries, merge badges, option editor, `Other`, routing-mode control, follow-up queue editor with preview,
  decision cards, condition drawer, undo/redo, save states, conflict handling.
- **Requirements.** SS-MOD-003…010; SS-QUE-006, 007, 016…022; SS-UX-003, 005 (guided half), 006, 009, 010;
  SS-UXE-006…013, 017, 019, 021, 025.
- **Gate.** Playwright for SS-AT-006…009, 016, 027, 033…041, 045, 046, 048 (guided half), 050, 051; undo/redo restores
  the server state exactly; interrupted-save scenarios lose nothing (UX-GATE-11); 40-question module fixture navigable.

#### SS-07 — Advanced Graph and What-if Lab (frontend)
- **Scope.** Module graph and survey-level module graph with automatic layout, pan/zoom/fit, minimap, search, option
  summarising, click-to-connect and direct connection; simulator panel with profile picker, questionnaire, trace,
  coverage, back/restart/fork, save scenario, compare two profiles.
- **Requirements.** SS-UX-005, 006; SS-UXE-018, 022, 023, 026; SS-SIM-004…010 (UI); SS-ROU-001.
- **Gate.** **Parity:** for every golden fixture, an edit made in Guided equals the same edit made in Graph (same
  operations, same resulting model) and the simulator path equals the backend path (UX-GATE-09, SS-AT-018, 048);
  SS-AT-026, 031, 052.

#### SS-08 — Validation, review, publish, reuse governance (backend + frontend)
- **Scope.** Readiness dashboard grouped by area with deep links; candidate freeze including regression results;
  maker-checker for module versions and survey versions; diff over routes, rules, options and queue order;
  consumer/impact graph; upgrade / keep pinned / fork; conversion of a linear version into a graph draft.
- **Requirements.** SS-VAL-001…012; SS-QUE-010; SS-RUL-012; SS-UXE-029; SS-AT-017, 021, 022, 028, 030.
- **Gate.** Self-approval and stale-hash approval rejected; published versions cannot be changed (attempts fail at
  service and database level); converted linear version reproduces the original's outcomes on all scenarios; a graph
  version can be assigned by an existing assignment rule and pinned to a case.
- **Decision point.** Owner decides whether new linear drafts are still allowed.

#### SS-09 — Operational runtime integration (backend; separately authorised)
- **Scope.** Runtime API (start, current step, answer with idempotency key, event, pause/resume, trace, summary) on
  published and assigned versions; writes `survey_run`, `question_execution`, `answer_observation`,
  `rule_evaluation` (+ additive columns for node, option codes, Other text, transitions); evaluation, findings and
  review exercised on graph runs.
- **Requirements.** SS-RUN-001…010; SS-QUE-012, 025; SS-AT-023, 024, 025, 029, 043, 044.
- **Gate.** Idempotent retry records exactly one answer; resume uses the pinned snapshot after a newer publication;
  arbitrary node advancement rejected; a draft is not reachable by the runtime; Review Workbench shows a graph run
  correctly without code change in the review engine.
- **Explicitly out.** Any voice or GPT-Live coupling. The channel is operator-entered or synthetic text.

#### SS-10 — Hardening and UX acceptance
- **Scope.** Small / medium / large fixtures (3, 10, 50 modules; ≥ 1,000 nodes); performance recordings; accessibility
  audit and keyboard-only full journey; Edge smoke; moderated usability sessions for UX-GATE-01…07; evidence pack for
  UX-GATE-12; decision on retiring the old editor.
- **Gate.** PRD §14 definition of done; owner + design + business sign-off (SS-UXE-030).

### J.3 Rollback summary

| After phase | To return to today's behaviour |
|---|---|
| SS-01, SS-02 | Nothing to undo in data; remove the prototype route |
| SS-03 … SS-08 | Set the flag off. Optional: downgrade that phase's additive migrations. Linear scripts were never touched |
| SS-09 | Flag off stops new graph runs; recorded runs remain as evidence and stay readable |

### J.4 Size (indicative, not a commitment)

By count of new P0 requirements: SS-03 and SS-06 are the two largest phases; SS-04 carries the highest regression risk
(the controller); SS-07 carries the highest technical uncertainty (graph editing). Each of SS-03…SS-09 is larger than
any checkpoint delivered so far and should be split into sub-checkpoints when its design is presented.

---

## K. UI design plan

### K.1 Principles the design is held to

1. Lego cards first; the graph is one click away, never the default.
2. One thing per screen region: library shelf (left), story canvas (centre), inspector (right, collapsible). The
   inspector and drawers overlay or dock; they never squeeze the canvas below a readable width. No cramped three-pane
   form.
3. Progressive disclosure: a card shows a sentence; detail appears on selection; rule trees only in the drawer.
4. Every common action is a click or a keystroke on the thing itself: `+` on a route, a destination pill, a mode
   switch. Drawing an edge is never required.
5. Nothing important is conveyed by colour alone; every chip has a text label and an icon.
6. The interface never says more than the server knows: `Saved` after acknowledgement, `Ready` only after server
   validation of that exact revision.

### K.2 Design system (to be built in SS-02)

- **Tokens** (new; today only colours exist): spacing 4/8/12/16/24/32; type scale; radius; elevation; motion
  120–220 ms with reduced-motion support; semantic colours reusing the existing palette. Scoped to Survey Studio so
  existing screens do not shift.
- **Components:** Lego module card; question card; decision card; outcome pill; route chip and destination picker;
  condition chip; option row; follow-up queue list; branch lane (collapsed/expanded); merge badge; insertion point;
  inspector panel; drawer; save-state indicator; issue badge and issues panel; readiness tile; trace row; coverage
  meter; empty states; breadcrumb with definition/instance badge.

### K.3 The nine storyboard screens

| Screen | Layout | Key behaviours | Reuses |
|---|---|---|---|
| **A · Studio Home and Library** | Home: `Create survey` hero, My drafts, Assigned reviews, Recent, Published. Library: tabs Surveys · Modules · Questions · Option sets · Conditions · Profiles; tiles with intent, version, status, counts, outcome badges, use count | Search-as-you-type, filters, favourites/recents, `Preview` without copying, `Add` vs `Fork` visibly different | S2-A.2 family cards; question bank and controls APIs |
| **B · Survey Lego Composer** | Vertical story `START → cards → END`, shelf left, inspector right, outline for long surveys | `+ Add here` between every pair; drag or keyboard reorder; `Run when…` chip; outcome pills with small labelled connectors; shared vs local badge; issue count on each card; sections collapse for 25+ | — |
| **C · Entry Rule Drawer** | Right drawer over the composer | Starts with "This module runs when…" sentence; modes `Always` / `Use saved condition` / `Build condition`; typed Field · Operator · Value rows; ALL/ANY/NOT groups; sample inputs with `Matches / Does not match / Unknown`; `Apply to this module only` vs `Save as reusable` with impact note | — |
| **D · Guided Module Builder** | Numbered normal path top-to-bottom; exception lanes folded at the side with `No → Clarification · 3 questions` and `Rejoins Q8` | `+` on every answer row; destination pills; merge badge with `View incoming`; `Add existing question`; view switch `Guided / Graph` keeping selection and scroll | Question bank; inline edit behaviour of the current editor |
| **E · Choice and Follow-up Designer** | Inside the question card on expansion | Option rows (label, code, `Other`, `Exclusive`); segmented control `Everybody continues` / `Different next questions` / `Ask a set of follow-ups`; ordered follow-up queue with drag and keyboard reorder, dedupe, interrupt, explicit `After follow-ups → Qx`; live preview such as `Premium + Benefits → Q-Premium → Q-Benefits → Q8` | — |
| **F · Internal Condition Drawer** | Same drawer component as C | Decision card shows `Match / Else / Unknown`; lists fields available at this point and whether needed answers have been collected; `Test this condition` | — |
| **G · Advanced Graph** | Full-width canvas; two scopes (survey modules; one module's nodes), never all questions of all modules by default | Auto layout, pan/zoom/fit, minimap, search, collapse, options summarised on a node, click-to-connect and handles, `Back to Guided` | — |
| **H · What-if Lab** | Panel over the editor: profile (left), customer questionnaire (centre), trace and coverage (right); collapses to two columns on narrower screens | Presets; `Step · Back · Restart · Save scenario · Compare profiles · Jump to first divergence · Explain path`; highlights executed and skipped steps on the canvas behind | Text simulator, scenario library, first-divergence, coverage |
| **I · Validation and Publish** | Readiness dashboard: Content · Routing · Conditions · Reuse dependencies · Scenario coverage · Accessibility · Approval | Each issue links to the exact control and returns; human-readable change summary since the last approved version; maker-checker panel; publish disabled until the server confirms | Review & publish panel, diff, history, validation issues |

### K.4 The ten priority stories — what the design must show

| Story | Design response | Engine rule behind it |
|---|---|---|
| 01 Add Suitability after General | Drop on `+`; connector redraws; card shows `Run when: Product is ILP`; amber note "2 outcomes not yet connected" | `add_module_instance` preserves the normal connection; unconnected exceptional outcomes are issues |
| 02 Five-choice single-select | Card appears inline, collapsed summary `5 options · All → Q8`; one switch to per-option pills | Default `ANY` edge; per-option edges override |
| 03 Add `Other — please specify` | One toggle adds the `OTHER` row with companion-text settings (required, length) and its route | `OTHER` is an option code with a text schema |
| 04 Premium + Benefits | Preview strip shows the two follow-ups in order and one rejoin | Queue built by priority then option order, deduped, single rejoin |
| 05 Premium + Critical Risk | Interrupt row at the top of the queue; preview shows "Critical risk → Escalate; 1 follow-up skipped" | Interrupt precedes the queue; skipped items traced |
| 06 Compound entry rule | Canvas keeps one chip `Premium > 12,000 AND Sum assured ≥ 500,000`; drawer explains true / false / unknown | Tri-state evaluator with explanation tree |
| 07 Delete a question with five inbound routes | Impact dialog lists the five sources and affected versions; choose a replacement destination or cancel | `delete_node` requires an explicit rewire |
| 08 Guided → Graph → Guided | Same selection, same routes, no "converting" step | One model, one operations endpoint |
| 09 Two profiles | Side-by-side lists of executed and skipped modules; `Why?` opens the rule evaluation | Decision trace; first-divergence |
| 10 Submit an invalid draft | Grouped blockers with one-click focus; `Submit` disabled with the reason stated | Server validation of the saved revision |

### K.5 Accessibility and responsiveness

- Every drag has a keyboard equivalent (move up/down, "connect to…" picker); graph nodes and edges have text
  descriptions; focus is never lost on reflow.
- Desktop-first authoring (1280 px and wider); at narrower widths the shelf and inspector become drawers and the
  product is review-oriented.
- Checked with the existing axe and three-width layout harness, extended with keyboard-only journeys.

### K.6 Evidence the UX standard requires

Automated tests can evidence UX-GATE-08, 09, 10 (partly), 11. **UX-GATE-01…07 and 12, and SS-UXE-030, require
moderated sessions with business users, timings and recorded sign-off.** These are owner-run activities; the plan
provides the task scripts, fixtures and a results template, but cannot produce the results.

---

## L. Risks, unresolved decisions and recommendations

### L.1 Risks

| # | Risk | Likelihood / impact | Mitigation |
|---|---|---|---|
| R1 | **Scope.** 161 P0 requirements, of which about 87 are new and 64 are extensions; larger than everything built for Governance so far | High / High | Phases with independent gates; sub-checkpoints; the owner may promote a "first usable slice" (SS-05 + SS-06 on Yes/No and single-select) before multi-select queues |
| R2 | **Controller regression.** Changing navigation in the accepted deterministic controller could alter existing behaviour | Medium / High | Linear plans run through the same code as a chain; replay-equivalence gate over all stored event logs and scenarios before any graph feature is enabled; feature flag |
| R3 | **Two engines by accident.** Pressure to "just add a graph runner" beside the controller | Medium / High | SS-D-01 and §G.3 forbid it; reviewed at SS-04 design |
| R4 | **Evaluation keyed by question code** limits same-survey module reuse | Certain / Medium | SS-D-09 re-scope, to be confirmed; occurrence-keyed evaluation later |
| R5 | **Wording approval ambiguity** between Survey Studio and Script Studio | Medium / High | SS-D-02; publication gate on wording state; no change to approval semantics |
| R6 | **UX gates need people.** Moderated tests, design sign-off and a business representative are outside what can be automated | Certain / High for sign-off | Plan task scripts early (SS-02); owner nominates participants; treat sign-off as a separate gate |
| R7 | **Graph editor complexity** (layout with merges, many ports, accessibility) | Medium / Medium | Guided view is the primary editor and must be complete without the graph; library evaluation in SS-02/SS-07; read-only graph first, editing second |
| R8 | **New dependencies** (drag, graph, layout) add supply-chain and bundle weight | Medium / Low | Decide per phase with versions pinned; none before approval |
| R9 | **Performance at 1,000 nodes** is unmeasured | Medium / Medium | Large fixture in SS-03; measurements, not promises, in SS-10 |
| R10 | **Field catalog reality.** Illustrative PRD fields (age, sum assured, replacement) exist in the synthetic data model, but their quality, units and nullability must be checked field by field | Medium / Medium | Field-by-field verification is part of SS-01 |
| R11 | **Frozen master documents.** The BRD and register are checksum-locked | Certain / Low | SS-D-19; explicit authorisation for any edit |
| R15 | **Name conflict with an approved decision.** "Survey Studio" is a prohibited label under D-2 / ADR-0007 | Certain / Low | SS-D-20: the owner reverses or keeps D-2; then ADR-0007, the approved-exceptions register and the negative-label test are updated together |
| R12 | **Parallel open items.** S1-E.2B live validation, the paid switch, the leaked-key rotation and uncommitted S2-A.2 are still open | Certain / Low–Medium | Close or park them explicitly before SS-01 (see §L.3) |
| R13 | **Undo/redo and concurrency.** Server-side inverse operations must be exact, including across validation side effects | Medium / Medium | Property tests: apply then undo returns the identical canonical hash |
| R14 | **Screen-reader usability of a visual builder** | Medium / Medium | Guided view is a structured list by nature; graph gets a text outline alternative |

### L.2 Unresolved — needs the owner

1. **SS-D-01** extend in place (recommended) versus new `survey_*` tables.
2. **SS-D-02** ownership of wording and the fate of the "Script Studio" label.
3. **SS-D-04** approval subjects in P0 (module and survey only).
4. **SS-D-09** the once-per-run limit — a re-scope of SS-SUR-008.
5. **SS-D-11** no new roles in P0.
6. **SS-D-17** runtime writes as a separate later phase.
7. **SS-D-05/06/07/10** the policy defaults (outcome list, sequencing, UNKNOWN, queue).
8. **SS-D-19** how SS-* requirements relate to the master register.
9. **Baseline screenshots.** PRD §16 names seven prototype screenshots (`Call360_Lego_*.png`). They are **not** in the
   repository — `docs/product/survey-studio/reference/` holds only `PRD_v1.1.docx`. Please add them (or confirm the
   images embedded in the .docx are the reference) before SS-02.
10. **Who signs UX acceptance** (product owner, design, business representative) and who takes part in moderated
    tests.
11. **Whether the prototype (SS-02) may use drag-and-drop and graph libraries**, or must be dependency-free.
12. **SS-D-20 — the name itself.** Owner decision D-2 and ADR-0007 (2026-11-15) fixed the module name as "Script
    Studio" and prohibit "Survey Studio" as a UI label; the specs validator enforces this and an end-to-end test
    asserts the label is absent. The new PRD reverses that. **Until this is decided the specs validator fails one
    terminology check** (see Part 2 SS-D-20).

### L.3 Recommendations

1. **Approve SS-D-01, SS-D-02, SS-D-08 and SS-D-13 first.** They decide everything else.
2. **Authorise SS-01 next, then SS-02.** Both are low-risk: documents, then a frontend-only prototype on fixtures.
3. **Do not authorise SS-03 until the prototype has been walked through**; the operation vocabulary and the model
   will be better for it.
4. **Keep Governance stable meanwhile.** No changes to Assignment Rules, Finding Rules, Review Workbench, Voice Lab.
5. **Housekeeping before starting:** commit the accepted S2-A.2 and S1-E.2B acceptance records; rotate the Azure key;
   switch the paid switch off; decide on the LAB-S-00023 microphone transcript. None of these blocks SS-01, but they
   should not stay open under a programme this size.
6. **Treat UX sign-off as its own gate with named people**, as the PRD requires; a working build is not acceptance.
