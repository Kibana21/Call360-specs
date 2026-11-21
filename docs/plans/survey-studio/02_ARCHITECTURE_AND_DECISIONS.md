# SS-00 · Part 2 — Architecture, canonical model and decision proposals

**Checkpoint:** SS-00 (design only). **Date:** 2026-11-21. **Status:** PROPOSED — every decision below needs the
owner's confirmation before it becomes an ADR. Nothing here is implemented.

Covers deliverables **E** (information architecture), **F** (canonical model), **G** (one graph, four consumers),
**H** (decision proposals for the PRD's open questions) and **I** (migration and coexistence).


> **Note (2026-11-21, SS-01):** §H is superseded by `06_SS-01_DECISION_REGISTER.md`; §E.1's separate "Wording &
> Delivery" navigation entry and the SS-D-09 restriction are superseded by the owner's rulings (see `README.md`).

---

## E. Information architecture and navigation

### E.1 Navigation

Current Governance group: Script Studio · Assignment Rules · Simulation Workbench · Finding Rules · Review Workbench.

Proposed (during coexistence):

```text
GOVERNANCE
  Survey Studio        /survey-studio          NEW — home, library, composer, builder, test, review
  Wording & Delivery   /scripts                the present Script Studio, re-scoped (see SS-D-02)
  Assignment Rules     /assignment-rules       unchanged
  Simulation Workbench /simulator              unchanged; regression packs and batch runs
  Finding Rules        /finding-rules          unchanged
  Review Workbench     /reviews                unchanged
```

"Survey Studio" appears only when the feature flag is on (SS-D-13). The label of `/scripts` changes only if the owner
approves SS-D-02; until then it stays "Script Studio".

### E.2 Route map (proposed)

| Route | Surface (PRD screen) | Notes |
|---|---|---|
| `/survey-studio` | Studio Home (A) | My drafts, recent, assigned reviews, published, `Create survey` |
| `/survey-studio/library?type=surveys\|modules\|questions\|option-sets\|conditions\|profiles` | Reusable Library (A) | One screen, tabs in the URL |
| `/survey-studio/surveys/:surveyId?version=` | Survey Lego Composer (B) + Entry Rule Drawer (C) | Drawer state in `?rule=` so it is linkable |
| `/survey-studio/modules/:moduleCode?rev=&view=guided\|graph&node=` | Guided Module Builder (D), Choice & Follow-up Designer (E), Internal Condition Drawer (F), Advanced Graph (G) | One route, two views of one model; selection kept in the URL |
| `/survey-studio/surveys/:surveyId/graph` | Survey-level module graph (G) | Read-first; editing P1 (SS-SUR-014) |
| `…?test=1&profile=` on composer and builder | Simulator / What-if Lab (H) | Side panel over the editor, not a separate page, so context is preserved (SS-UXE-026) |
| `/survey-studio/surveys/:surveyId/review?version=` | Validation & Publish (I) | Readiness dashboard, diff, maker-checker |

Breadcrumb on every authoring screen: `Survey › Module instance › Question / Decision`, with a badge that says whether
the user is editing a **reusable definition** or an **instance binding**, plus draft/published status and save state.

### E.3 What happens to today's screens

| Today | In the new IA |
|---|---|
| Script Studio library (one card per script, S2-A.2) | Its content moves to the Survey Studio library "Surveys" tab; `/scripts` keeps working for linear versions |
| Script page tabs: Questions · Versions · Review & publish · Compare · History · Details | Same six concerns reappear in Survey Studio (Composer, Versions, Review, Compare, History, Details); the S2-A.2 layout is the pattern they follow |
| Text simulator, scenario library, test runs | Stay in Simulation Workbench; Survey Studio's Test panel is a new front end on the same backend |

---

## F. Canonical model

### F.1 Principle

One model, stored once, in the existing governed tables plus additive graph tables. **Definition** = stable identity.
**Version** = immutable content. **Instance** = a placement with its own bindings. A linear script is the degenerate
graph in which every answer goes to the next node.

### F.2 Entity map

| PRD entity | Storage (★ = new, additive) | Owns |
|---|---|---|
| Survey Definition | `script_family` (+ owner, purpose text, archived flag) | Identity |
| Survey Version | `script_version` (manifest schema `/3`) | The set of module instances, connectors, dependency lock, hash |
| Module Instance | `script_section` + ★ `instance_code`, `entry_mode`, `entry_binding_id`, `params` | Placement, entry rule, parameters |
| Survey Route | ★ `survey_connection` (version, source instance, outcome code, target instance or survey outcome, condition binding, priority, is_fallback) | What follows each module outcome |
| Module Definition / Version | `script_module (code, revision)` + ★ `entry_node_id`, `outcomes` | The internal graph |
| Node | ★ `module_node` (module, `node_code`, `node_type` QUESTION \| DECISION, FK to `module_question` or condition binding, guided order hint, optional layout) | A step in the module |
| Question Instance | `module_question` (kept; one per QUESTION node) + ★ `routing_mode`, `normal_answer_code`, `applicability_binding_id` | Placement and routing bindings |
| Edge | ★ `module_edge` (module, source node, `on_code`, target node **or** outcome code, priority, is_default) | One transition |
| Follow-up plan | ★ `followup_plan` + `followup_item` (question node, option code, target nodes, priority, dedupe, rejoin target, empty-selection fallback, interrupt policy) | The multi-select queue |
| Question Definition / Version | `question_bank_item` / `question_revision` (+ ★ help text, internal notes, text validation, selection rules) | Wording, type, options, validation |
| Option Set / Option | ★ `option_set` / `option_set_version` / `answer_option` (code, label, order, exclusive, is_other, other_text_schema, allow_with_others) | Stable coded choices; reusable across questions |
| Condition Definition / Version | ★ `condition_definition` / `condition_version` (typed AST, parameter schema, field dependencies) | The predicate |
| Condition Binding | ★ `condition_binding` (condition version, scope, parameter values, unknown policy) | Use of a predicate in one place |
| Field Catalog | ★ `field_catalog` (field code, source, type, unit/currency, operators, sensitivity, availability) | What a condition may read |
| Outcome Catalog | ★ `outcome_code` (governed list) | Named module and survey outcomes |
| Test Profile | ★ `test_profile` (+ revisions) ; scenarios stay in `simulation_scenario*` | Synthetic inputs |
| Draft operation log | ★ `draft_operation` (draft, seq, operation, inverse, actor) | Undo/redo and revision history |
| Approvals, audit | `script_change_event`, `audit_event` (kept) | Decisions and evidence |

`on_code` values on an edge: `YES`, `NO`, an option code, `ANY` (the explicit "all answers → next" default),
`AFTER_CAPTURE`, `ON_SKIP` for questions; `MATCH`, `NO_MATCH`, `UNKNOWN` for decisions.

### F.3 Definitions versus instance bindings

| Lives in the **definition** (shared; changing it means a new version) | Lives in the **instance** (local to one placement) |
|---|---|
| Question wording, answer type, option codes and labels, `Other` schema, validation | Where the question sits, its routing mode, each option's destination, follow-up plan, applicability rule |
| Condition AST and parameter schema | Parameter values, scope, UNKNOWN policy |
| Module internal graph and its outcome list | Entry rule, parameters, what each outcome leads to in this survey |
| Option set contents | Which options have special routes in this module |

Rule enforced by the server: **an instance edit can never write to a definition** (PRD anti-pattern "saving a local
override by modifying a global definition"). Editing shared content offers three explicit choices — `Use existing`,
`Create new version`, `Fork` — the second and third being today's copy-on-write (`_owned_module`, `_insert_revision`).

### F.4 Stable identity

- Codes are stable and business-readable (`question_code`, `module.code`, `node_code`, `option_code`,
  `instance_code`, `condition_code`); database ids are UUIDs as today.
- Edges, bindings and evidence reference **codes within a pinned version**, never labels. Renaming a label cannot
  change routing (SS-QUE-011).
- Guided order and graph layout are **view hints**, stored apart from edges; they never affect execution.

### F.5 Published artefact

Publishing compiles the draft into `script_version.manifest` (schema `/3`), hashed with the existing `sha256_of`:

```text
manifest/3
  survey            family code, version label, language
  module_instances  [instance_code, module code@revision, entry binding, params]
  connections       [source instance, outcome, target, binding, priority, fallback]
  modules           {code@revision: entry node, outcomes, nodes[], edges[], follow-up plans}
  questions         {question_code@revision: full snapshot incl. options, controls}   ← same fields as /2
  conditions        {condition_code@version: AST, params}
  bindings          {id: condition ref, parameter values, unknown policy}
  dependency_lock   every referenced version with its content hash
  sections          the /2-compatible flattened view (for evaluation, findings, review, Voice Lab import)
```

The `/2`-compatible `sections` view is what keeps the existing consumers working without change.

---

## G. One canonical graph, four consumers

```text
                    ┌──────────────────────── draft graph (tables in §F) ───────────────────────┐
  Guided Editor ──┐ │                                                                           │
                  ├─┤  POST …/drafts/{id}/ops   typed operations, atomic, row-versioned,        │
  Advanced Graph ─┘ │  server-validated, inverse recorded  →  new revision + changed nodes +    │
                    │  issues                                                                   │
                    └───────────────┬───────────────────────────────────────────┬───────────────┘
                                    │ compile (same function)                   │ validate (same function)
                                    ▼                                           ▼
                           executable manifest/3                         issues with node paths
                                    │
              ┌─────────────────────┴─────────────────────┐
              ▼                                           ▼
   Simulator (draft or published,              Runtime (published and assigned only,
   simulation tables, synthetic profiles)      operational tables)
              └───────────── one controller, one condition engine ─────────────┘
```

### G.1 Editors

- Both views read the same draft through one read API and change it through **one operations endpoint**. Neither
  holds a private model, so there is nothing to convert and nothing to drift (SS-ROU-001, SS-AT-018, UX-GATE-09).
- Operations are business-level and typed: `add_module_instance`, `move_module_instance`, `set_entry_rule`,
  `connect_outcome`, `insert_question_on_edge`, `set_routing_mode`, `set_route`, `add_option`, `set_followup_plan`,
  `add_decision`, `delete_node {rewire}`, … The server applies each atomically and returns the new `row_version`.
- **Safe insertion is a server rule, not a UI habit:** `insert_question_on_edge` re-points the old edge to the new
  node, gives the new node's *normal* answer the old destination, and creates the other answers **unrouted**; unrouted
  answers are validation errors that block submission (SS-ROU-006, SS-AT-007).
- **Undo/redo** replays the recorded inverse operations on the server, so the canonical state is restored, not a
  picture of it (SS-UXE-019). The same log is the revision history (SS-UX-010).
- **Save state** is driven by acknowledgements: `Saving…` while an operation is in flight, `Saved` only after the
  server answers, `Offline` on network failure with retry, `Conflict` on `STALE_DRAFT` (SS-UXE-021).
- Graph layout is computed in the browser from nodes and edges (layered layout); manual positions, if any, are stored
  as layout metadata only.

### G.2 Compiler and validator

Pure functions over the draft graph, used by the editor (issues), the simulator (run a draft), submission (freeze the
candidate) and publication (re-check the hash). Checks: schema and types; every answer has exactly one resolution;
reachability; every path ends in a declared outcome; cycles; ambiguous priorities; condition operands available at the
point of use; UNKNOWN handled; queue targets, order, dedupe and termination; dependency versions approved and pinned;
lifecycle rules that exist today (identity gate, stage order).

### G.3 Runtime: one engine

`question_controller` stays the single deterministic engine. Today it is pure, event-sourced, LLM-free, rejects stale
or arbitrary actions and enforces the lifecycle gates; those properties are kept. What changes is **navigation**:

| Today (linear plan) | Extended (compiled graph) |
|---|---|
| Applicability decided once at plan build | Module entry evaluated when the survey reaches the instance; node applicability when reached |
| `_advance`: next pending item in order | Follow the edge selected by the answer / decision result; then the connector selected by the module outcome |
| Conditions: true/false | Tri-state with explicit UNKNOWN route or `BLOCKED_UNKNOWN` |
| — | Follow-up queue: one cursor, built deterministically, executed serially, one rejoin |
| — | Back/edit: `ANSWER_SUPERSEDED` event, downstream answers invalidated, path recomputed |
| — | `PAUSED` / `RESUMED` events on the same pinned manifest |
| Events per item | + `DECISION_EVALUATED`, `ROUTE_SELECTED`, `MODULE_ACTIVATED/SKIPPED/OUTCOME`, `QUEUE_BUILT`, … (the decision trace) |

Selection precedence is the PRD's: (1) lifecycle event or gate stop, (2) the node's specific route, (3) its default
route, (4) otherwise `BLOCKED` — never a silent completion.

A `/2` manifest is compiled to the same in-memory graph as a chain, so there is one execution path. Proof obligation
before any graph feature is switched on: **every stored simulation event log replays to the identical state and the
existing controller, lifecycle, scenario, evaluation, findings and review tests pass unchanged.**

### G.4 Condition engine

One typed, pure evaluator returning `TRUE | FALSE | UNKNOWN` with an explanation tree (each atom: field, source value,
operator, operand, result). Operands: catalog fields, parameters, literals, prior answers, prior module outcomes.
No strings of code, no `eval`. Limits on depth, node count and list sizes (SS-NFR-018). Decimal comparison for money,
with currency and unit checked at authoring time.

It generalises the tri-state logic that already exists in `rule_engine` (PASS / FAIL / UNKNOWN). **The assignment rule
engine is not rewritten**; it keeps its own evaluator. Converging the two is a possible later clean-up, proposed only
if the owner asks.

### G.5 Simulator

Same compiled manifest, same controller, same condition engine as runtime; only the store differs
(`script_simulation_*` instead of operational tables) and inputs come from a synthetic profile. Additions: module-only
runs, back/fork, UNKNOWN injection, route and choice coverage by unique edge id, "why" explanations taken straight
from the decision trace, and comparison of two profiles using the existing first-divergence logic.

---

## H. Decision proposals

Numbered `SS-D-nn` (proposed) so they do not collide with the project decision log, which currently ends at D-112.
On approval they would be recorded as new ADRs (the next free numbers after ADR-0009) and given D-numbers. PRD §15 question numbers are in brackets.

### SS-D-01 Extend the governed script model in place; do not create parallel `survey_*` tables
**Proposal.** Survey = `script_family`, Survey Version = `script_version`, Module Instance = `script_section`, Module
Version = `script_module`, Question = question bank; add the graph tables of §F.
**Why.** The structures already match; every downstream pin, evaluation, finding, review, recording and audit record
keeps its foreign keys; no history migration; no second source of truth.
**Cost.** Table names say "script" while the product says "survey" (handled by API and UI naming, SS-D-12).
**Alternative rejected.** New `survey_*` tables beside the script tables: cleaner names, but two masters for
questions and versions, a mapping layer for assignment and review, and a migration of published history.

### SS-D-02 Ownership: Survey Studio owns structure; approved wording stays under the existing script approval [§15 Q1, Q8]
**Proposal.**
- **Survey Studio** is the only place to author *what is asked and where it leads*: modules, question definitions
  (type, options, validation), routing, conditions, outcomes.
- **Customer-facing wording and delivery** (`customer_wording`, `delivery_mode`, exact-audio assets, clarifications)
  remain fields of the immutable `question_revision`, with the existing `content_approval_status`. The present Script
  Studio screen is re-scoped to this concern ("Wording & Delivery"): it shows, per published survey version, the
  wording and delivery mode that will be spoken, the controls and regulatory references it evidences, and its approval
  state.
- **One approval chain, unchanged semantics:** a survey version is published only through the existing
  DRAFT → SUBMITTED_FOR_REVIEW → APPROVED → PUBLISHED maker-checker, and the publication gate adds "every pinned
  question revision's wording is in a permitted approval state". Today every revision is `SYNTHETIC_UNAPPROVED`
  (D-57), so publication continues to mean "published for synthetic testing only".
- An author can type wording when creating a question in Survey Studio (otherwise the tool is unusable), but that
  wording is a **draft question revision** and carries no approval until the chain approves it. Survey Studio cannot
  change the wording of an approved revision; it can only create a new revision (fork), which needs approval again.
**Open for the owner.** Whether wording approval should later become a separate sign-off by a wording owner distinct
from the routing checker. Not proposed for P0.

### SS-D-03 Shared-asset reuse: pin by default, upgrade explicitly, fork instead of local override [§15 Q2]
**Proposal.** Consumers always pin exact versions. A new version of a shared question, option set, condition or
module never reaches a consumer by itself; the consumer's draft offers `Upgrade` (with impact preview and scenario
re-run), `Keep pinned` or `Fork`. **No per-instance wording override** — fork a new question revision instead. This is
the behaviour the code already has for modules and questions.

### SS-D-04 What gets its own approval in P0
**Proposal.** Two approval subjects in P0: **Module Version** (standalone, so a library module can be approved once
and reused) and **Survey Version**. Questions, option sets and conditions are approved as part of the first module or
survey candidate that pins them (the frozen manifest covers their content and hashes); after that they show as
approved in the library. A survey draft may still contain a **local draft module** (today's behaviour), approved with
the survey.
**Why.** Independent approval queues for four more asset types add workflow without adding control in P0.
**Change required.** Relax `script_draft_module_lock` additively so a draft module may be standalone.

### SS-D-05 Outcome catalog [§15 Q3]
**Proposal.** A governed list of outcome codes; authors pick from it and may set a display label per module, but
cannot invent codes. Initial list (to confirm): `COMPLETED`, `CLARIFICATION_REQUIRED`, `ESCALATE`,
`CUSTOMER_DECLINED`, `UNABLE_TO_VERIFY`, `RESCHEDULE`, `INCOMPLETE`. Existing termination reasons map onto these;
their detailed reason codes are kept.

### SS-D-06 Module sequencing: ordered eligibility plus explicit outcome connectors [§15 Q4]
**Proposal.** Default behaviour is today's: modules are considered in declared order and each runs if its entry rule
matches ("all eligible blocks in an ordered plan"). An outcome connector overrides the default for that outcome only
(for example `CLARIFICATION_REQUIRED → Escalation`). Where several connectors could apply, explicit priority and a
mandatory fallback; equal priorities are a validation error. The composer shows which mode applies on each card.

### SS-D-07 UNKNOWN policy [§15 Q5]
**Proposal.** No global default. Every binding must choose one of: `ROUTE_UNKNOWN` (an explicit edge), `BLOCK`
(run stops as `BLOCKED_UNKNOWN`, needs review), `SKIP_WITH_REASON` (only for optional, non-mandatory modules).
A binding without a choice is a validation error. Existing `/2` versions keep their current "missing is false"
behaviour, because changing it would alter published logic.

### SS-D-08 Conversation lifecycle and gates stay above the graph
**Proposal.** Opening, identity, disclosure, consent and closing remain controller-level rules (S2-D.1): stage order
is validated, policy-disclosing questions stay blocked until identity is confirmed, gate failures terminate with their
reason, and closing statements marked for delivery on termination are still delivered. In the composer these are
ordinary Lego modules of the corresponding kind; their gate behaviour is not editable as routing.
**Why.** They are accepted compliance controls; the PRD does not specify them and must not weaken them.

### SS-D-09 A question code executes at most once per run in P0 (partial re-scope of SS-SUR-008)
**Proposal.** A module may be reused in any number of surveys. Within **one** survey, the validator rejects a
composition in which the same question code could be asked twice. Full same-survey repetition comes later with
occurrence-keyed evaluation.
**Why.** Answer evaluation, findings and review are keyed by `question_code`; lifting the limit means changing those
engines, which the preservation rules say needs a demonstrated need.
**This is a re-scope of a P0 acceptance criterion and needs the owner's explicit agreement.**

### SS-D-10 Multi-select policies [§15 Q6] and loops [§15 Q7]
**Proposal.** All three modes in P0. Defaults: order by explicit priority, then declared option order; dedupe
`ONCE_PER_ANSWER`; an interrupt option stops the queue and emits its configured outcome (no resume in P0); empty
selection takes the mandatory fallback; editing the original answer rebuilds the queue and supersedes stale follow-up
answers. Follow-up targets are single question nodes in P0 (reusable follow-up *sets* are P1, matching SS-MOD-013).
Cycles are rejected at validation and capped at run time; bounded loops are P1.

### SS-D-11 Roles and permissions [§15 Q11]
**Proposal.** No new roles in P0; map PRD roles to existing permissions, as D-64 did for rule roles:

| PRD role | Existing permission(s) | Held by |
|---|---|---|
| Business Author, Library Curator | `script.edit` | USER |
| Reviewer / Compliance Checker | `script.approve` | SC_CHECKER |
| Publisher | `script.publish` | SC_CHECKER |
| Simulation | `script.simulate` | USER, SC_CHECKER |
| Operations, Auditor | `script.read` (+ existing audit permissions) | as today |
| Runtime Service | decided in SS-09 | — |

Any author may create reusable conditions and questions; they become "approved" only through SS-D-04.

### SS-D-12 Naming, API and contract
**Proposal.** New routes under `/api/v1/survey-studio/…` generated into the same OpenAPI; existing `/scripts…` routes
and their consumers unchanged. UI says "Survey", "Module", "Question", "Condition"; storage keeps `script_*` names.
ADR-0007 (Script Studio naming and lifecycle) would be amended, not replaced — **subject to SS-D-20**, because
that ADR currently prohibits the "Survey Studio" label.

### SS-D-13 Feature flag and rollback
**Proposal.** A server setting `SURVEY_STUDIO_ENABLED` (off by default) hides the routes and navigation; every
migration is additive with a tested downgrade; no existing column is dropped or repurposed. Turning the flag off
returns the product to today's behaviour at any phase.

### SS-D-14 Assignment and pinning [§15 Q12]
**Proposal.** Unchanged. Assignment rules target a `script_version`; the case pin (`script_assignment`) and the
session pin record the version and manifest hash at the same moments as today. A graph version is assignable exactly
like a linear one. Running or historical sessions never move to a new version.

### SS-D-15 Simulator data [§15 Q9]
**Proposal.** Synthetic profiles only. No replay of real cases; revisit only with a separate decision.

### SS-D-16 Scope of the first release [§15 Q10, Q13, Q14]
**Proposal.** Size targets as in SS-NFR-002 (to be measured, not promised). No import/export in P0. Findings and the
review of customer evidence stay in the existing Finding Rules and Review Workbench.

### SS-D-17 Runtime writes to operational tables are a separate, later authorisation
**Proposal.** Phases up to and including publication run entirely on simulation tables, as S3-A and S3-B did (D-75,
D-80). Writing real `survey_run` / `answer_observation` rows (PRD P0-D "runtime") is its own phase (SS-09) with its
own authorisation, because no live writer exists today and the owner has deferred controller-to-voice integration.

### SS-D-18 Frontend libraries (decision deferred to the phase that needs them)
**Position.** Composer and guided builder need accessible drag-reorder; the graph view needs pan/zoom, minimap, edge
routing and a layered layout. Building these by hand is possible for reorder, costly and risky for an editable graph.
**Candidates to evaluate when authorised:** `@dnd-kit` for reorder; `@xyflow/react` (React Flow) with `elkjs` or
`dagre` for the graph. **No dependency is added in SS-00, SS-01 or the prototype** unless the owner approves it then.

### SS-D-19 Requirements register
**Proposal.** The 191 SS-* requirements stay in the PRD as their own namespace and are **referenced** from the master
register by one linking entry per group, rather than copied in. The master BRD and register are checksum-frozen by the
validator; any edit needs the owner's explicit specification-edit authorisation. Existing SUR-002/008/010/012 and
SCR-008/009/010/012 are the parents the SS-* requirements refine.

### SS-D-20 The product name "Survey Studio" reverses owner decision D-2 / ADR-0007
**Fact.** On 2026-11-15 the owner decided (D-2; ADR-0007; exception EXC-001 in `docs/spec/APPROVED_EXCEPTIONS.md`)
that the module is called **Script Studio**, that `/surveys…` paths are only redirects to `/scripts…`, and that
"Survey Studio" must not be used as a UI label. The specs validator enforces the terminology rule, and the S0 test
matrix (E2E-18) asserts that the label does not appear. The new PRD is titled and written around "Survey Studio".
**Effect today.** With the PRD files and these plans in the repository, the validator's terminology check fails
(60 of 62 checks passed before this fix; 61 after removing an ADR reference in these plans — the remaining failure is
this one). SS-00 did **not** edit `APPROVED_EXCEPTIONS.md`, ADR-0007 or the test matrix.
**Options.** (a) Reverse D-2: "Survey Studio" becomes the approved name for the new authoring product; amend ADR-0007
and EXC-001, add the PRD and plan paths to the approved list, update the negative-label test, and decide the label of
the existing `/scripts` screen (SS-D-02). (b) Keep D-2: the new product ships under the "Script Studio" name and the
PRD is treated as its requirements under a different title; only the PRD and plan files are registered as references.
**Recommendation.** (a) — the PRD's vocabulary (survey, module, question) is the user's mental model and the frontend
`CLAUDE.md` already lists "Survey Studio" as a screen — but it is the owner's earlier decision to reverse, so it must
be explicit.

---

## I. Migration and coexistence

### I.1 Guarantees

| Item | Guarantee | Mechanism |
|---|---|---|
| Published script versions and modules | Never rewritten | Existing guard triggers; new columns are nullable or defaulted; manifests are not regenerated |
| Question revisions | Never rewritten | `forbid_change` trigger; richer fields live in sibling rows or new revisions |
| Case and session pins | Unchanged | Still `script_version_id` + manifest SHA; `/2` manifests stay executable |
| Simulation runs, scenarios, batches | Remain valid and replayable | Replay test over stored event logs is a gate for the controller change |
| Evaluations, findings, reviews | Unchanged | Contract in Part 1 §C kept; engines not modified |
| Recordings, transcripts, Voice Lab data | Untouched | No table or code in `app/voice` is changed |
| Audit chain | Continues | Only new event names are added |
| Singapore-only, RBAC | Unchanged | Same scope filter and permissions on every new route |

### I.2 Coexistence model

- **Two manifest schemas, one engine.** `/2` (linear) and `/3` (graph) are both executable for as long as any pin
  references them — that is, indefinitely.
- **Linear versions stay linear.** Nothing converts them automatically. A family can get a graph version through an
  explicit, reviewable action, "Open in Survey Studio as a new draft": each section becomes a module instance with its
  entry rule, each module a chain with `ANY → next` edges, conditions translated to the new AST. The conversion is
  lossless because linear is a subset; a test proves that the converted draft produces the same plan and outcomes as
  the original for every existing scenario. The result is a normal draft that goes through maker-checker.
- **Both editors during transition.** The old editor continues for linear drafts until the owner retires it (Part 1
  §D.3). A family has one open draft at a time (D-56), so the two editors never edit the same draft.

### I.3 Schema change approach

- Additive migrations after `0026`, each with a downgrade tested on a clean database and on the seeded test schema.
- New tables get the same immutability and child-guard triggers as their parents.
- The development schema is migrated only with the owner's approval, as for earlier checkpoints.
- No seed data is deleted. New synthetic seed (sample modules, conditions, profiles for the storyboard) is added
  alongside, clearly labelled synthetic.

### I.4 Rollback points

Each phase ends at a point where the flag can be switched off and, if needed, that phase's migrations downgraded
without touching earlier data (Part 3 §J).
