# Call360 Survey Studio — Detailed Product & Functional Requirements

**Document ID:** CALL360-SS-PRD-001  
**Version:** 1.1 — expanded answer types and exceptional UI/UX acceptance standard  
**Date:** 21 November 2026  
**Product:** Call360 · Insurance Callback Platform · Singapore-first  
**Target repositories:** `Call360-specs`, `Call360-backend`, `Call360-frontend`  
**Status:** Draft; no regulatory wording, routing thresholds, service-level targets, or permissions in this document are represented as approved business policy.

**Revision v1.1 (21 Nov 2026):** Adds first-class `Other — please specify` semantics, P0 sequential per-selected-option multi-select follow-ups, expanded question/choice contracts, 20 new golden scenarios, and Section 18 — UX Excellence Standard with 33 explicit UI requirements, nine screen storyboards and twelve UX release gates. All prior baseline requirements remain in force unless amended below.

> **Product intent:** Let a business user build a sophisticated insurance callback journey as easily as assembling Lego blocks—without hiding the power of conditional logic, branching questions, reusable libraries, execution testing, approvals, and complete graphical inspection.

---

## 1. Executive summary

Survey Studio is a business-managed, versioned designer and deterministic runtime specification for surveys conducted during Call360 callback journeys. A **Survey** is assembled from reusable **Modules** (categories or Lego blocks). Each Module contains questions, internal decisions, optional subflows, and named outcomes. **Reusable Conditions** control which Modules execute, which internal paths run, and what happens when a Module exits. A single canonical graph powers both a **Guided Builder** and an **Advanced Graph Editor**; the two interfaces are synchronized and cannot represent different business logic.

A Survey author should be able to assemble a survey in minutes using an existing module library; a Module author should be able to insert a question in any branch with automatic reconnection and compose sequenced follow-ups for selected multi-choice options; a Reviewer should be able to see exactly which route a sample customer takes; and runtime services must execute the approved, immutable graph deterministically, independent of any AI or voice conversational layer.

### 1.1 Non-negotiable product principles

1. **Lego first, graph underneath.** The default interface is a clean Survey Composer showing module cards—not hundreds of question nodes.
2. **Two kinds of conditions, one rule engine.** Survey-level conditions activate or connect modules. Module-level conditions direct questions. Both reuse the same typed rule library.
3. **Questions are reusable assets.** Questions, answer options, conditions, and whole Modules have stable identities and versions.
4. **One source of truth.** Guided editor, graphical editor, simulator, and runtime consume the same canonical graph and compiled snapshot.
5. **Answer richness by default.** Yes/No, single-choice, multi-select, `Other + specify` and typed free text are equally natural to author; multiple selected options can generate an explicitly ordered sequence of follow-ups.
6. **Fast authoring, no dangerous magic.** New questions may inherit the previous *normal* destination, but never receive an invented alternate compliance path. Missing routes are made visible and block publication.
7. **Business meaning is explicit.** Endpoints are named outcomes such as `COMPLETED`, `CLARIFICATION_REQUIRED`, `ESCALATE`, `CUSTOMER_DECLINED`, and `UNABLE_TO_VERIFY`—not merely “the end.”
8. **Safe reuse.** Editing a shared asset does not silently change any published journey; consumers are pinned and upgrades are intentional.
9. **Prove the journey before publishing.** Built-in preview, profile simulations, path analysis, regression testing, graph validation, and maker-checker gates.
10. **Backend authority.** Python controls progression, conditional evaluation, answer validation, and evidence; the UI and eventual voice channel are renderers/executors, not policy decision makers.
11. **Singapore-first.** Initial business functionality and sample reference data target Singapore. Preserve any existing market fields for later extensibility without introducing unnecessary multi-market administration now.

### 1.2 Success measures (proposed targets to validate in usability tests)

| KPI | Proposed target | Measurement |
|---|---:|---|
| Assemble a survey from three existing modules | ≤ 5 minutes | Moderated authoring test |
| Add a Yes/No question to a route and configure both outcomes | ≤ 60 seconds | Moderated authoring test |
| Reuse one approved question in two modules | ≤ 60 seconds | Moderated authoring test |
| Detect incomplete paths before submission for approval | 100% of known invalid-route fixtures | Automated validation suite |
| Trace why each module and question executed | 100% of sampled runs | Simulator + execution trace |
| Ensure a published version is not mutated | 100% of attempted updates rejected | Backend integration tests |
| Resume a paused run on the same exact survey snapshot | 100% of supported resume fixtures | Runtime integration tests |

### 1.3 In scope and out of scope

**In scope (P0):** Survey/module/question/condition libraries; visual Lego assembly; module authoring; Yes/No, single-select multiple choice, multi-select multiple choice, first-class `Other — please specify`, sequential multi-select follow-up queues, free-text questions; conditional routing; typed rule composition; guided and graph editors; simulator using synthetic customer profiles; structural and behavioral validation; lifecycle and approvals; version pinning; runtime API and audit.

**In scope (P1 or later):** General-purpose nested reusable subflows (distinct from P0 multi-select follow-up queues), richer answer types (number/date/scale), bulk authoring, graph comparison/diff, reusable scenario packs, import/export, advanced simulation coverage, localized UI content, specialized analytics.

**Not in this module's initial delivery:** Actual outbound calling/telephony provisioning, speech generation or transcription, agent dialogue policy outside approved survey content, automatic LLM-authored compliance decisions, multi-market user administration, a generic BPMN platform, and unrestricted executable scripting in rules. Integration seams are required, but these products are separate concerns.

---

## 2. Product vocabulary and information architecture

| Term | Definition | Key distinction |
|---|---|---|
| **Survey Definition** | A reusable blueprint for a complete callback questionnaire | Composed of ordered/conditional Module Instances |
| **Survey Version** | Immutable snapshot of the approved Survey blueprint and dependency versions | Required for reproducible execution |
| **Module Definition (Lego block/category)** | Reusable collection of questions, decision nodes, entry/exit ports and internal routes | Designed once, used in many surveys |
| **Module Instance** | Placement of one Module Definition in a specific Survey | Owns survey-specific entry rule, placement, connector routing, and safe parameters |
| **Question Definition** | Reusable question asset with text, answer type/options, metadata and validations | Wording/content reused independently of flow |
| **Question Instance / Node** | A Question Definition placed into a Module graph | Owns context-specific routing and optional overrides |
| **Choice / Answer Option** | Stable coded answer value with business label | E.g. `YES`, `NO`, `BENEFITS`, `PREMIUM`; not label-based IDs |
| **Condition Definition** | Reusable, typed, declarative predicate (`AND`/`OR`/`NOT`) | Can be invoked at survey or module scope |
| **Condition Binding** | Use of a condition with explicit input mapping and parameters | Allows reusable rule with threshold parameters |
| **Decision Node** | A graph step evaluating one Condition Binding | Exposes `MATCH`, `NO_MATCH`, optionally `UNKNOWN` |
| **Module Outcome** | Named result emitted when a Module completes | Drives downstream survey-level routing |
| **Survey Route** | Edge connecting one Module Instance to the next or to a Survey Outcome | May use priority and condition with fallback |
| **Customer Profile** | Synthetic test dataset or live permitted input fields | Profile schema comes from governed field catalog |
| **Survey Run** | A stateful execution of one published Survey Version | Pins all versions, answers, decisions and evidence |
| **Script/Delivery Binding** | Mapping from an approved survey question to approved spoken/display text | Keeps script delivery controlled and distinct from routing |

### 2.1 Three levels: intentionally different UI surfaces

```text
LEVEL A  SURVEY COMPOSER — LEGO CANVAS
  [Start] → [General Verification: Always]
          → [Suitability: Product = ILP]
          → [High Value Review: Premium ≥ threshold OR Sum Assured ≥ threshold]
          → [Policy Replacement: Replacement = Yes]
          → [Closing] → [End]
            | Entry rules + Module Outcome connectors are compact chips.

LEVEL B  MODULE BUILDER — QUESTIONS + INTERNAL DECISIONS
  [Q1: Did adviser explain benefits?]
       YES → [Q2: Understand risks?] → ...
       NO  → [Q3: What needs clarification?] → [Q2] (shared merge)
  [Decision: Age ≥ 60 AND Premium ≥ threshold]
       MATCH → [Q4: Affordability check]
       ELSE  → [Next question]

LEVEL C  CONDITION DRAWER — ON DEMAND
  [ALL]
     Annual Premium  >  12,000
     [ANY]
        Sum Assured  ≥  500,000
        Product Type  =  ILP
   [Save as reusable rule]   [Test values]   [View uses]
```

**UX rule:** Never place the full condition tree on the main Survey Composer or default Module canvas. Show a human-readable, truncated predicate chip such as `IF Premium > 12k AND (...)`; click it to open the rule drawer. Advanced Graph view may render decisions as compact nodes, not expanded AND/OR trees.

---

## 3. User roles, access, ownership, lifecycle

| Role | Allowed actions (subject to existing Call360 RBAC) |
|---|---|
| **Business Author** | Create/edit draft surveys, modules, questions, conditions; simulate; submit for review |
| **Library Curator** | Maintain reusable question/condition/module definitions, tags, status, deprecation and reuse guidance |
| **Reviewer / Compliance Checker** | Inspect graph, diff, coverage and evidence; approve/reject with reason; cannot approve own changes |
| **Publisher / Authorized Admin** | Publish approved immutable versions; retire versions; manage feature permissions and rollout assignment |
| **Operations User** | View approved journey, run trace and versions; cannot alter approved logic |
| **Auditor** | Read history, evidence, approval chain, effective versions and export audit report |
| **Runtime Service** | Read/execute only eligible published versions using service authorization; append runtime events |

**Lifecycle:** `DRAFT → IN_REVIEW → APPROVED → PUBLISHED → RETIRED`, with `REJECTED` returning to a new editable draft/revision. A published version is immutable. Superseding it creates a new version and new approval cycle. A module/question/condition may also be `DEPRECATED`; deprecation blocks *new adoption* according to policy, while historical pinned runs remain reproducible.

**Segregation:** Maker and checker must be different identities. Editing an approved or under-review snapshot must create a new candidate/revision or explicitly return it to Draft; never silently change an approval subject.

---

## 4. End-to-end business storyline (screens and actions)

| Screen | Business user experience | Primary actions | Design reference |
|---|---|---|---|
| **01. Studio Home / Library** | Search reusable Surveys, Modules, Questions, Rules and Profiles in tabs | Search/tag/filter, see consumers, start from template | Module Library screenshot |
| **02. Survey Lego Composer** | Drag or click `+ Add module` from left library; center displays compact module cards, right inspector edits placement | Add/reorder/connect/skip, condition chip, entry/exit routing | Survey Assembly screenshot |
| **03. Entry Rule Drawer** | One selected module shows `Run when` rule, conditions and `ELSE skip` behavior | Select existing rule or compose nested AND/OR | Entry Condition Editor screenshot |
| **04. Module Guided Builder** | Open a module into main linear question path with progressively shown exception branches | Inline add, answer route picker, reorder, collapse, join paths | Module Branching screenshot |
| **05. Internal Rule Drawer** | Select a decision node; edit field rules without expanding the canvas | Condition library, grouped rules, field validation, test values | Internal Condition Editor screenshot |
| **06. Complete Graph** | Auto-layout all module nodes or full module graph, with merge points and named exits | Inspect, click/drag connections, graph controls, layout reset | Prior graph previews |
| **07. Customer Journey Simulator** | Choose synthetic profile, answer sample questions, watch executed path; inspect why branches ran | Step/Back/Reset, what-if, compare profile scenarios | Test Journey screenshot |
| **08. Validation & Review** | Issues and coverage list, diff from published, maker-checker approval and immutable publishing | Resolve, submit, approve/reject, publish | Publishing Review screenshot |

### 4.1 Surveys and modules are not the same editor

The top-level Survey Composer edits **Module Instances**. It does not directly edit shared module questions. A module card offers **Open module** (to author its draft source), **Inspect version** (read-only approved source), and **Create derived version** (copy-on-write for changes). Survey-specific configuration is limited to the Module Instance's entry condition, parameter values, position, entry mapping and outcome routing.

### 4.2 Guided vs Advanced Graph editing

Both are first-class authoring views and edit the **same saved graph**. Guided view is optimized for fast linear paths, inline Yes/No/multiple-choice routing, and exception groups. Graph view is optimized for heavily branched structures, shared destinations, direct edge creation, zoom/pan/fit, mini-map, search, layout and multi-node editing. Switching views must not produce a conversion step, duplicate questions or data loss.

---

## 5. Functional requirements catalog

**Priorities:** P0 = required for the initial usable production scope; P1 = near-term enhancement; P2 = roadmap. Every requirement has a stable ID and a testable acceptance outcome. Where example rules or thresholds appear, they are illustrative only.

### 5.1 Survey Composer: Lego assembly

| ID | Priority | Requirement | Acceptance criteria |
|---|---|---|---|
| SS-SUR-001 | P0 | Create, clone, rename, archive and version a Survey Definition | Draft appears in studio library with owner, scope, last edited and status |
| SS-SUR-002 | P0 | Add Module Instances from approved, searchable library | Adding a module creates a reference to exact Module Version; does not copy all questions |
| SS-SUR-003 | P0 | Reorder Module Instances via drag/drop and accessible move controls | Sequence changes are saved and Undo can restore previous ordering |
| SS-SUR-004 | P0 | Display module card with name, version, entry rule summary, question count, outcomes, validation status | Main canvas remains readable without exposing internal decision trees |
| SS-SUR-005 | P0 | Define `Always`, `When rule matches`, and `On module outcome` activation modes | Skipped modules are recorded with reason; missing input follows configured unknown policy |
| SS-SUR-006 | P0 | Connect Module Outcomes to next Module, conditional edge, named Survey Outcome or stop | Every emitted outcome resolves deterministically; no silent default if ambiguous |
| SS-SUR-007 | P0 | Auto-connect normal sequence when modules are inserted between existing modules | Original downstream module is preserved; all newly exposed exceptional exits must be reviewed |
| SS-SUR-008 | P0 | Allow module reuse multiple times within/across Surveys, with distinct instance IDs and configuration | Editing one instance's entry rule does not alter the reusable definition or another instance |
| SS-SUR-009 | P0 | Support an `Always` general module and conditional specialized modules in one survey | Simulator can run general + selected conditional modules for same profile |
| SS-SUR-010 | P0 | Provide side panel to set module parameters, entry rule, outcome mappings and dependency version | All edits appear as understandable summary chips on cards |
| SS-SUR-011 | P0 | Prevent deleting a module without showing incoming/outgoing route impact | Author must choose replacement destinations; no silent rerouting |
| SS-SUR-012 | P1 | Provide reusable whole-survey templates and collections of modules | Creating from template pins approved module versions and records source |
| SS-SUR-013 | P1 | Allow grouping/sections on Survey Composer | Groups collapse, expand and preserve execution semantics |
| SS-SUR-014 | P1 | Offer survey-level graphical routing mode, not only a linear sequence | Branching between modules is visible with outcomes and rejoin points |

### 5.2 Module Builder: question flow authoring

| ID | Priority | Requirement | Acceptance criteria |
|---|---|---|---|
| SS-MOD-001 | P0 | Create and version Modules independently of Surveys | A module can be authored/tested without placing it in a survey |
| SS-MOD-002 | P0 | Each module has one entry port, typed internal nodes, and named outcome ports | All reachable paths terminate via a declared outcome (unless explicitly allowed bounded loop policy) |
| SS-MOD-003 | P0 | Guided mode displays normal question sequence with collapsible exceptions | 40-question test module remains navigable without manual graph layout |
| SS-MOD-004 | P0 | Insert a question via `+` on any route, including Yes, No, choice, text completion or decision result | New node points to former destination on configured normal branch; alternate choices remain explicitly unconfigured |
| SS-MOD-005 | P0 | Edit question wording, presentation, required flag and answer validation inline | Changes update view and draft model without changing published versions |
| SS-MOD-006 | P0 | Route any answer to the next sequential question, named question, internal decision, module outcome or supported action | Route picker searchable, shows destination label and impact |
| SS-MOD-007 | P0 | Multiple incoming edges may converge on one shared Question Instance | Shared destination is stored once; UI shows incoming count and route origins |
| SS-MOD-008 | P0 | Branches can be expanded/collapsed, with summary and rejoin indicator | Collapsed branch still shows outcome/destination; never hides validation error |
| SS-MOD-009 | P0 | Permit multiple decision nodes anywhere inside one module | E.g. premium gate at entry, sum assured gate after Q2, age gate before exit |
| SS-MOD-010 | P0 | Provide sequence/route-aware delete, duplicate, move and Undo/Redo | Delete identifies affected edges and requires explicit rewire or cancel |
| SS-MOD-011 | P0 | Support customizable outcome labels and a controlled global outcome code catalog | Published node IDs and outcome codes remain stable in snapshots |
| SS-MOD-012 | P0 | Support direct module simulation independent of full survey | Author can select a profile, supply missing fields and trace complete route |
| SS-MOD-013 | P1 | Allow reusable subflow insertion (question groups) within a module | Subflow can be configured by parameters and exposes named inputs/outputs |
| SS-MOD-014 | P1 | Support conditional visibility/skip policies for individual questions | Skip is explicit and recorded; no implicit “hidden but answered” state |

### 5.3 Questions and answer behavior

| ID | Priority | Requirement | Acceptance criteria |
|---|---|---|---|
| SS-QUE-001 | P0 | Question library with tags, search, owner, domain, status and version | Question reused from exact pinned version with source/usage visible |
| SS-QUE-002 | P0 | Yes/No question with stable `YES`/`NO` codes and editable display text | Yes and No can route independently or both to default NEXT |
| SS-QUE-003 | P0 | Single-choice multiple-choice with 2–N configured options | Each option can route to distinct target or inherit common NEXT; option IDs stable |
| SS-QUE-004 | P0 | Multi-select multiple-choice capture and deterministic sequential follow-up processing | Author chooses `ALL_TO_NEXT`, `ORDERED_RULES`, or `SEQUENTIAL_FOLLOWUPS`; every selection set has a single unambiguous executable path |
| SS-QUE-005 | P0 | Free-flowing text question with length/required validation | Answer saved as text; completion routes to common NEXT or a separately configured deterministic rule |
| SS-QUE-006 | P0 | One-click `All answers → next question` toggle | Creates one explicit default route; switching to per-choice reveals overrides without duplicating nodes |
| SS-QUE-007 | P0 | Per-option route to other question, decision, module outcome or action | Branch routes visible as compact chips and in Complete Graph |
| SS-QUE-008 | P0 | Supports `Mandatory`, `Optional`, `Not applicable` and conditional applicability semantics | Runtime distinguishes skipped, declined, no answer and null/unknown |
| SS-QUE-009 | P0 | Provide question help text, compliant approved wording reference, internal notes and response guidance | Customer-facing vs internal-only fields separated and access-controlled |
| SS-QUE-010 | P0 | Prevent removal or code changes to answer options in use without impact report | Inbound references and scenario expectations shown before version change |
| SS-QUE-011 | P0 | Answer values are typed and validated; selected option uses ID/code, not label | A renamed option label cannot silently change routing behavior |
| SS-QUE-012 | P0 | Preserve answer evidence: raw value, normalized code, provenance, timestamp, actor/source and version | Every accepted response attributable to executed Question Instance |
| SS-QUE-013 | P1 | Numeric/date/scale/file-evidence answer types via extensible registry | Each type supplies a defined validator and supported condition operators |
| SS-QUE-014 | P1 | Multi-language variants linked to same question code and version | Changing display language does not change route key semantics |
| SS-QUE-015 | P1 | Question preview in desktop, tablet and eventual call-agent mode | Same approved meaning, visible help and validation feedback |
| SS-QUE-016 | P0 | First-class `Other — please specify` option for single- and multi-choice | Stable `OTHER` code, conditional text input, typed payload, validation and independent/common routing |
| SS-QUE-017 | P0 | Make the `Other` text mandatory, optional or disabled, with min/max length and privacy rules | Mandatory text prevents answer submission when Other selected; no text field shown otherwise |
| SS-QUE-018 | P0 | Configure `Other` coexistence with other selected options | `OTHER` may be combinable or exclusive; mutual-exclusion rules are enforced consistently |
| SS-QUE-019 | P0 | Multi-select `SEQUENTIAL_FOLLOWUPS` mode: each chosen option may enqueue a question or approved follow-up set | Selected options produce a deterministic deduplicated queue with an explicit merge/rejoin destination |
| SS-QUE-020 | P0 | Queue controls: stable priority/order, duplicate suppression, escalation interrupts and explicit default | Sim trace lists selected options, queue creation, skipped/deduped follow-ups and final rejoin |
| SS-QUE-021 | P0 | Configurable `No concerns` / `None of the above` exclusivity and min/max selections | Invalid combinations rejected at authoring validation and runtime submission |
| SS-QUE-022 | P0 | Question/option preview shows common-next, per-choice and sequential-follow-up routing | Selected choice combination immediately produces a readable next-step preview |
| SS-QUE-023 | P0 | Question versions own the option-set content; module placements own option-specific routing bindings | Reusing a question in two modules does not force the same next-question path |
| SS-QUE-024 | P0 | Multi-select follow-ups support `on_skip`, `not_applicable`, and `stop` policies | No hidden bypass of compulsory safety/escalation outcomes; decisions are audited |
| SS-QUE-025 | P0 | Preserve selected option IDs and optional Other text as distinct answer evidence | Both structured codes and accompanying text are captured with version, actor and timestamp |

**Question routing presets (P0):** `ALL_TO_NEXT`, `PER_CHOICE`, `CONDITION_AFTER_ANSWER`, `SEQUENTIAL_FOLLOWUPS` (multi-select), and `TERMINATE_WITH_OUTCOME`. For Yes/No, independent routes may happen to target the same next question. For single-select, exactly one choice is recorded. For multi-select, the selections form a set and do *not* imply multiple simultaneous navigation paths; use an explicit ordered decision table with first-match priority and a mandatory fallback, **or generate one deterministic sequential follow-up queue** with optional global escalation interruption, stable deduplication, explicit skip policies and a final rejoin destination; a simple all-to-next preset remains available.

**Other option:** `OTHER` is a stable option code, not a new question type. When selected it can expose a required/optional companion text field; the response stores both option code and text. It supports per-choice, common NEXT or sequenced multi-select follow-ups with declared exclusivity.

**Free text:** Free-flowing answers are stored verbatim (subject to privacy controls) and may be marked for manual review. In P0, free text does **not** autonomously trigger a compliance branch through an unapproved LLM interpretation. Any classification-based routing requires an approved, deterministic mapping plus explicit unknown/review handling; AI-generated candidate labels can be treated as untrusted inputs requiring verification.

### 5.4 Conditions, shared rule library and field catalog

| ID | Priority | Requirement | Acceptance criteria |
|---|---|---|---|
| SS-RUL-001 | P0 | Maintain reusable Conditions independent of Module or Survey | Condition has stable ID, version, description, owner, tags, test examples and usage count |
| SS-RUL-002 | P0 | Support nested AND, OR and NOT with arbitrary nesting subject to configurable safe complexity limits | `A AND (B OR C)` and `NOT (D AND E)` serialize, evaluate and round-trip identically |
| SS-RUL-003 | P0 | Use a governed, typed field catalog for customer, policy, sale, case, session and prior answers | Only allowed fields/operators appear in rule picker; no arbitrary SQL/JavaScript/Python input |
| SS-RUL-004 | P0 | Support numeric, string, Boolean, enum, date and set operators appropriate to field type | Numeric comparison rejects invalid string literal and wrong currency/units |
| SS-RUL-005 | P0 | Allow conditions at Module entry, module-to-module connector, internal Decision Node and question applicability | Same rule engine is used across all four binding contexts |
| SS-RUL-006 | P0 | Provide configurable parameters (`premium_threshold`, `sum_assured_threshold`) in reusable rules | Survey-specific parameter binding doesn't modify shared rule definition |
| SS-RUL-007 | P0 | Define `TRUE`, `FALSE`, `UNKNOWN` evaluation outcomes for absent/unreliable values | Unknown has explicit author-selected route or safe stop/review policy; never treated silently as False |
| SS-RUL-008 | P0 | Define deterministic ordering/priority for multiple matching module connectors and decision rules | Overlaps detected or resolved by explicit priority; runtime trace records winner and reasons |
| SS-RUL-009 | P0 | Preview rule using sample values and expose an explainable evaluation tree | Displays each atomic comparison and `TRUE`/`FALSE`/`UNKNOWN`, source value and reference |
| SS-RUL-010 | P0 | Support dependency mapping from prior-answer codes to rule expressions | Rule picker selects question/answer code and checks that answer is available before evaluation |
| SS-RUL-011 | P0 | Prevent rule dependence on future/unanswered questions unless explicit deferred-evaluation policy exists | Validator flags nonavailable dependencies and author can change placement |
| SS-RUL-012 | P0 | Use rule version pinning, dependency impact report and explicit upgrade action | Updating shared rule does not affect deployed/published consumers |
| SS-RUL-013 | P0 | Provide `Select existing rule`, `Create new rule`, `Duplicate as variant` options | Reused rule ID/version visible with number of consumers |
| SS-RUL-014 | P1 | Provide rule templates and friendly natural-language display summaries | UI renders understandable text and keeps the full AST only in drawer |
| SS-RUL-015 | P1 | Support membership, ranges, string patterns, date calculations and combinations of selected answers | All operators have deterministic backend and frontend preview parity tests |
| SS-RUL-016 | P1 | Warn on contradictory, redundant or shadowed rules | E.g. `Age > 65 AND Age < 18` or earlier first-match rule shadowing a later one |

**Rule sources:** Case/policy/customer facts (authorized, normalized and snapshot-aware), runtime answers from earlier questions, derived values from approved deterministic functions, and previous Module Outcomes. Every field has `field_code`, label, type, units/currency, nullability, permitted operators, security classification, provenance, and freshness requirements. Sensitive fields must be masked in previews when not authorized.

**Rule evaluation policies:** Rule nodes are evaluated when execution reaches them, against an explicit state snapshot. Snapshot values are recorded with provenance and calculation version. If an input changes later, already executed steps are **not silently replayed**; an explicit re-evaluation/restart policy and audit event are required. In Survey Composer, an entry condition that depends on a previous Module Outcome is only evaluated after that module has executed. If it is not yet available, the author must either reorder/defer the module or configure an explicit UNKNOWN path. Conditions cannot be used as uncontrolled background global triggers.

### 5.5 Routing semantics, module handoff and error handling

| ID | Priority | Requirement | Acceptance criteria |
|---|---|---|---|
| SS-ROU-001 | P0 | The canonical model is a directed typed graph with stable node IDs, route IDs and outcome codes | Guided and Graph editors render the same IDs and transitions |
| SS-ROU-002 | P0 | Each answer/decision/outcome resolves to **at most one** next execution step | Runtime cannot execute two customer-facing questions simultaneously from one response |
| SS-ROU-003 | P0 | A default sequential NEXT route is explicit and overridable per answer | All-answers-to-NEXT state is visible on card and in underlying graph |
| SS-ROU-004 | P0 | Support merging branches into shared question/decision nodes | Two incoming routes can target one node without creating duplicate definitions or instances |
| SS-ROU-005 | P0 | Support multiple exit ports per module and map each to downstream survey routing | `CLARIFICATION_REQUIRED` can activate Escalation; `COMPLETED` continues normal sequence |
| SS-ROU-006 | P0 | Preserve original downstream route on inline insertion while marking new branches incomplete | Automatic insertion never invents an unreviewed compliance decision |
| SS-ROU-007 | P0 | Explicit handling for route ambiguity, missing destination, missing input and invalid response | Runtime returns structured `BLOCKED/NEEDS_REVIEW`, never falsely records completed |
| SS-ROU-008 | P0 | Reject unbounded graph cycles in initial publishing rules | Structural validator detects cycles; runtime also enforces max steps/visits as defense in depth |
| SS-ROU-009 | P0 | Support safe navigation back/edit prior answer while recording superseded answer/route effects | Recalculation invalidates downstream answers on changed path and writes audit event |
| SS-ROU-010 | P0 | Each executed step emits a machine-readable decision trace | Includes evaluated condition/version/inputs/result, selected transition and skipped candidates |
| SS-ROU-011 | P1 | Support approved, bounded repeat loops with explicit max iterations and exit logic | Only enabled behind validation policy, never by accidental cycle |
| SS-ROU-012 | P1 | Support survey-wide events such as refusal, no-contact, callback reschedule and escalation | Events map to controlled outcomes, not hidden route shortcuts |
| SS-ROU-013 | P0 | Sequential multi-select queue is one controlled execution cursor, not independent parallel paths | Each queued follow-up is issued once, in configured order, then the shared rejoin occurs once |
| SS-ROU-014 | P0 | Define queue behavior on critical answer, escalation, earlier-answer edit, pause/resume and skip | Queue is recomputed or resumed consistently; stale follow-up answers are invalidated with audit |
| SS-ROU-015 | P0 | Validate every queue element, rejoin and priority override before publication | Missing target, ambiguous priority, duplicate collision or nonterminating queue blocks publish |

**Module connection semantics:** A Survey defines the ordered/conditional set of Module Instances and connector edges. For each candidate Module, evaluate its entry predicate when its dependencies are available; emit `ACTIVATED`, `SKIPPED_FALSE`, `DEFERRED_UNKNOWN`, `SKIPPED_PRIOR_OUTCOME`, or `BLOCKED_ERROR` with reason. On completion, consume one named Module Outcome and select the next eligible connector using defined priority and fallback. A module may be positioned several times in a Survey, but each has unique instance identity and recorded execution occurrence.

**Deterministic selection precedence:** (1) explicit event/stop with highest authorized priority; (2) current node's choice-specific/condition-specific configured route; (3) configured default NEXT/fallback route; (4) if none, `BLOCKED` error. For multi-select routing: `ALL_TO_NEXT` evaluates the shared destination; `ORDERED_RULES` evaluates an ordered table against the complete selected-set (first match wins, explicit fallback); `SEQUENTIAL_FOLLOWUPS` builds one deterministic queue in author-defined order, applies deduplication and escalation/stop overrides, executes queued follow-ups serially, then enters one explicit rejoin target. None of these modes spawns parallel customer-question sequences.

### 5.6 First-class UI and authoring experience

| ID | Priority | Requirement | Acceptance criteria |
|---|---|---|---|
| SS-UX-001 | P0 | Studio home has distinct tabs: Surveys, Modules, Questions, Conditions, Test Profiles | Search and filters work independently, with clear object type and version |
| SS-UX-002 | P0 | Survey Composer uses left library, centered Lego canvas, right contextual inspector | Authors can add a module without opening a graph or rule editor |
| SS-UX-003 | P0 | Module Guided Builder has inline add-on-route controls and highlighted normal path | A new Yes/No or multiple-choice branch can be created entirely by click/tap and keyboard |
| SS-UX-004 | P0 | All condition expressions render as compact rule chips until selected | Large AND/OR trees do not clutter Survey or Module canvases |
| SS-UX-005 | P0 | Advanced Graph Editor supports auto-layout, panning, zooming, fit-to-view, search, minimap and direct connections | Editing route in graph changes the same route shown in guided view |
| SS-UX-006 | P0 | Multiple incoming routes have visible merge badges/edge counts | Shared destination is visually identifiable and inspectable |
| SS-UX-007 | P0 | Right inspector displays selected item without losing canvas scroll/selection | Editors can change type/route/condition and see live effect |
| SS-UX-008 | P0 | Human-readable routing summaries show `YES → Q3`, `CHOICE B → Q7`, `ELSE → SKIP MODULE` | No ID-only editing needed for common tasks |
| SS-UX-009 | P0 | Validation errors appear inline on relevant card and in a navigable issues panel | Clicking issue focuses affected card even if branch is collapsed |
| SS-UX-010 | P0 | Autosave drafts with visible save state, Undo/Redo and revision history | Refresh/reopen restores latest successful draft without ambiguity |
| SS-UX-011 | P0 | Confirm destructive changes with route impact previews | No silent deletion of a referenced question, module or rule |
| SS-UX-012 | P0 | Keyboard and accessible controls are available for every drag action | Survey can be authored using keyboard alone; WCAG 2.2 AA target |
| SS-UX-013 | P0 | Responsive layout supports desktop authoring and smaller-screen review | No essential controls clipped; graph supports deliberate horizontal scroll/zoom |
| SS-UX-014 | P1 | Copy/paste, multi-select, duplicate, alignment and bulk operations | Reused blocks are created with correct identities and history |
| SS-UX-015 | P1 | Visual diff between versions shows added/removed/moved nodes and changed rules/routes | Reviewer can inspect before/after logic without comparing raw JSON |
| SS-UX-016 | P1 | Inline context help, examples, progressive disclosure and quick-start templates | Nontechnical author can create a validated simple survey without training in graph syntax |

**Visual language:** Neutral/light enterprise canvas; reusable modules as consistent “Lego” cards with color-coded *type* (general, product, enhanced review, exception) but do not rely on color alone. Condition chips display readable summaries, not raw code. Question nodes show a small answer-type badge, full question, route chips and `+` insertion controls. Graph edges may be color-coded (Yes/No/Other) plus written labels. Keep the visual hierarchy crisp: Survey > Module > Decision > Rule details.

### 5.7 Simulator, profiles, testing and coverage

| ID | Priority | Requirement | Acceptance criteria |
|---|---|---|---|
| SS-SIM-001 | P0 | Run a complete Survey or a single Module in a side-by-side Simulator | Simulation loads the same draft snapshot under edit or chosen published version |
| SS-SIM-002 | P0 | Maintain reusable **synthetic** customer profiles with typed fields | Create, clone, edit, tag, save profile; import with validation; no real PII in demos |
| SS-SIM-003 | P0 | Support profile toggles for product, premium, sum assured, age, replacement, and other catalog fields | Changing profile re-runs eligibility and highlights affected modules/decisions |
| SS-SIM-004 | P0 | Interactive step-by-step answering for Yes/No, choice and free text | Next question, skipped module and final outcome match deterministic graph rules |
| SS-SIM-005 | P0 | Explain all decisions: matched/else/unknown and selected route | Trace shows exact input, rule version, result and why other branch skipped |
| SS-SIM-006 | P0 | Navigate Back, Restart, and fork from any previous step | Simulator supersedes downstream answers and recalculates correctly |
| SS-SIM-007 | P0 | Save scenario with profile, answer sequence, expected modules/questions/outcome | Regression test compares expected vs actual and reports first divergence |
| SS-SIM-008 | P0 | Highlight reached and unreached graph nodes and choices | Simulation map shows visited path and step-by-step execution order |
| SS-SIM-009 | P0 | Show route/condition coverage and list untested reachable branches | Coverage is distinct from correctness; tested routes counted by unique IDs |
| SS-SIM-010 | P0 | Offer explicit missing-data / UNKNOWN simulation | Author sees that survey blocks, defers or takes configured UNKNOWN route |
| SS-SIM-011 | P1 | Batch-run reusable profile/scenario packs with comparison matrix | All scenarios can run unattended in test environment and be exported |
| SS-SIM-012 | P1 | Generate candidate test cases from structural graph and rule boundaries | Boundary values include `threshold-1`, `threshold`, `threshold+1`; author approves assertions |
| SS-SIM-013 | P1 | Visual compare two profile journeys side-by-side | Difference view marks modules/questions/route reasons that changed |
| SS-SIM-014 | P1 | Test shared asset upgrades against pinned consumer snapshots | Failed regression blocks upgrade until resolved or explicitly waived by checker |

**Core synthetic profiles (illustrative):** Standard term-life low premium; ILP with high premium; high sum assured but lower premium; older customer with borderline premium; policy replacement; missing annual premium; multi-select ambiguous response; customer requiring clarification; declined/restricted completion. Thresholds are examples; verified business rules must supply actual values.

### 5.8 Validation, publication and reuse governance

| ID | Priority | Requirement | Acceptance criteria |
|---|---|---|---|
| SS-VAL-001 | P0 | Validate schemas, required content, field types and answer options | Invalid fields or unsupported operators block publish |
| SS-VAL-002 | P0 | Validate reachability, all routes, exits and graph cycles | Disconnected question, broken route or unbounded loop becomes actionable error |
| SS-VAL-003 | P0 | Validate ambiguity/priority for decision tables and module connectors | Conflicting rules cannot silently choose an arbitrary destination |
| SS-VAL-004 | P0 | Validate rule dependencies and handling of UNKNOWN/missing values | Future-answer dependency and absent fallback are reported |
| SS-VAL-005 | P0 | Validate library dependency versions and approved usage state | Cannot publish against unavailable, unapproved or revoked version |
| SS-VAL-006 | P0 | Mark severity (`ERROR`, `WARNING`, `INFO`) and navigate to source | All `ERROR` issues block publication; waiver semantics only for approved warnings |
| SS-VAL-007 | P0 | Run authoritative backend validation prior to approval and publish | Frontend feedback cannot bypass server gate |
| SS-VAL-008 | P0 | Submit immutable candidate manifest with snapshot hash and regression results | Checker sees exact artifact later published |
| SS-VAL-009 | P0 | Maker-checker approval with reason and decision log | Self-approval rejected; changed candidate requires re-approval |
| SS-VAL-010 | P0 | Publish exact pinned dependency tree and activation metadata | Historical SurveyRun can resolve every question/rule as executed |
| SS-VAL-011 | P0 | Generate dependency/usage graph and change-impact warnings for shared assets | Author sees all draft and published consumers before creating new version |
| SS-VAL-012 | P0 | No auto-upgrade of published consumers | New shared version must be explicitly adopted and tested in new survey/module version |
| SS-VAL-013 | P1 | Publish controlled rollout and retired-state policies | Existing runs continue on pinned version; new assignment uses eligible published version |
| SS-VAL-014 | P1 | Review visualization of changed modules/rules/questions and coverage deltas | Reviewer can prioritize changed decision paths |

**Publication condition:** `graph valid AND dependencies approved/pinned AND mandatory content approved AND required tests pass AND maker-checker accepted AND manifest hash unchanged`. Warnings may require policy-defined acknowledgement. Publishing returns an immutable manifest ID and version; any later change creates a new draft.

### 5.9 Runtime, script delivery, audit and integration

| ID | Priority | Requirement | Acceptance criteria |
|---|---|---|---|
| SS-RUN-001 | P0 | Start run using assigned published Survey Version and dependent module/rule/question snapshots | Snapshot IDs/hashes saved before first question |
| SS-RUN-002 | P0 | Advance via Python service API that validates answer and chooses next step | React/voice clients cannot submit arbitrary next-node IDs |
| SS-RUN-003 | P0 | Persist answer, decision result, transition and module outcome as ordered events | Trace reconstructs run including skips and invalid input handling |
| SS-RUN-004 | P0 | Pause/resume/retry idempotently after connectivity loss or interrupted call | Resume on same pinned graph; duplicate request does not duplicate answer/event |
| SS-RUN-005 | P0 | Integrate with existing callback case, attempt/session, approved script and assignment records | Clear ID links for Case → Attempt/Session → SurveyRun → Answer/RuleEvaluation |
| SS-RUN-006 | P0 | Separate routing from spoken wording/voice orchestration | Only approved script wording is eligible for regulated delivery; LLM not routing authority |
| SS-RUN-007 | P0 | Maintain role-sensitive audit log for draft edits, approvals, published snapshots and execution | Audit includes actor, version, timestamp, changed fields and reasons |
| SS-RUN-008 | P0 | Strict authorization and isolation for author/reviewer/runtime read/write APIs | Draft inaccessible to runtime; no cross-scope access to protected data |
| SS-RUN-009 | P0 | Support interruption/abandonment without marking survey completed | Session state captures partial, declined, escalation, unable-to-verify and reschedule outcomes |
| SS-RUN-010 | P0 | Preserve recorded answers and fact sources under correction/supersession policy | Any superseded answer has audit relation; historical decisions remain traceable |
| SS-RUN-011 | P1 | Search and report module coverage, responses, exception rates and reasons | Analytics can join SurveyRun to Case and ModuleInstance/version |
| SS-RUN-012 | P1 | OpenAPI-based integration contracts and event notifications | Other Call360 modules integrate via versioned APIs, not shared database writes |

---

## 6. Detailed answer-type routing semantics

### 6.1 Yes / No

A Yes/No card provides Yes and No ports. Routing mode can be `BOTH_TO_NEXT` or `INDEPENDENT`. Both may target the same node. New cards created by inserting onto an existing edge inherit that edge's previous destination on the author-chosen **normal** answer; the alternative is shown as `Configure destination` until set. All answer routes are stable by `YES` and `NO` codes regardless of displayed wording.

### 6.2 Single-choice multiple choice

Each configured option has an immutable key and label. Author selects `ALL_TO_NEXT` (one destination), `BY_CHOICE` (independent route per option) or `BY_CHOICE_WITH_DEFAULT` (overrides plus fallback for unspecified options). The card collapses to `4 choices · 3 routed to Q5 · 1 to Q9`; expand to edit option destinations. Validation prevents duplicate codes, orphaned route references and a choice without a valid route when no default exists.

**Example:** “Which concern is most important?” → `PREMIUM` → Q-Premium, `BENEFITS` → Q-Benefits, `CLAIMS` → Q-Claims, `NONE` → Normal Next. All branches may rejoin at Q-Confirmation.

### 6.3 Multi-select multiple choice

The customer can choose 0..N allowed choices, honoring `min_selected`, `max_selected` and `exclusive` options (such as `NONE_OF_THE_ABOVE`). `OTHER` is a stable coded choice with a conditional companion text field. The authored choice labels, stable codes, multi-select set and Other text are stored separately. The full selection set is persisted before route evaluation. Because two checked answers may each propose a different route, **route once** using one of these approved modes:

- `ALL_TO_NEXT`: all valid response sets go to one destination.
- `ORDERED_RULES`: evaluation table such as `contains(CRITICAL_RISK)` → Escalate (priority 10), `contains(PREMIUM)` → Q-Premium (priority 20), `contains(BENEFITS)` → Q-Benefits (priority 30), else → NEXT. First match wins; precedence and a fallback must be explicit.
- `SEQUENTIAL_FOLLOWUPS` (**P0**): create a deterministic ordered queue of option-bound follow-up question(s) or approved follow-up sets for *each selected choice*. Order is explicit (author priority or declared option order). Deduplicate shared follow-up IDs according to configured policy, handle escalations/stop before remaining queue items, persist cursor and snapshot, and rejoin exactly once at the configured destination. This is a scoped P0 queue feature, **not** unrestricted nested general-purpose subflows.

### 6.4 Free-text and other open answers

**`Other — please specify` (P0) is a special answer option**, available in single-select and multi-select. On selection, the UI reveals a companion text control with separately configured label, required flag, length bounds, masking/sensitivity, normalized display, optional manual review indicator and `allow_with_other_choices` behavior. It stores `{ option_code: "OTHER", other_text: "..." }` in addition to the complete selected-choice set. An author may route Other to a dedicated follow-up, the common next question, an ordered multi-select follow-up, or a controlled outcome. Text itself must not autonomously create an unapproved compliance decision. Leaving Other unselected must not create phantom text evidence. Removing Other from an approved shared option set is a versioned breaking change requiring consumer impact review.

A free-text question stores a verbatim value and configured constraints (`required`, min/max length, character policy, hints). Its default route is `ON_CAPTURE → NEXT` or `ON_SKIP → defined route` if optional. Optional controlled classification can assign a coded value after human verification; any NLP/LLM suggestion is never itself an authoritative compliance decision in P0.

### 6.5 Choice-to-sequence behavior

An author must be able to select **“All choices continue to the next question in sequence”** without configuring each route. This compiles to a real default route with explicit graph semantics and stable target—not just a presentation shortcut. Inserting a question between sequential nodes updates that default route while preserving any deliberate per-choice exceptions.

---

### 6.6 Sequential multi-select follow-up semantics (P0)

**Example question:** `Q-CONCERNS: Which areas would you like us to clarify?` Allowed options: `PREMIUM`, `BENEFITS`, `CLAIMS`, `CRITICAL_RISK`, `OTHER` (companion text), and `NONE` (exclusive). For a customer selecting `PREMIUM + BENEFITS + OTHER`, the system must capture all three codes and the Other text first, then create a queue such as `Q-PREMIUM → Q-BENEFITS → Q-OTHER → Q-COMMON-NEXT`. The system asks **one question at a time**. If the customer selects `CRITICAL_RISK`, an explicitly approved `ESCALATE_NOW` override may stop the queue and emit a controlled outcome; it may not be silently deduced by UI convention.

**Queue construction contract (P0):**

1. Validate selected options and Other text, including exclusivity and cardinality, before resolving routing.
2. Apply explicit cross-cutting priority/interrupt rules (if configured); trace the winning rule.
3. For ordinary follow-up selection, map each selected option to zero or more configured follow-up question/group references; reject missing required mappings.
4. Order by explicit `priority` then declared stable `option_order` (or a product-owner-approved alternative), never by unordered set iteration.
5. Deduplicate repeated follow-up instances using an explicit `ONCE_PER_ANSWER` policy or allow `ONCE_PER_OPTION` only when that is reviewed, with resulting execution identity still unique.
6. Execute the resolved list sequentially; if a follow-up itself branches to an early module outcome, honor that approved outcome policy.
7. Persist the queue and cursor in the Survey Run snapshot and include option-to-follow-up causation in trace.
8. On permitted change to the original selected set, invalidate/supersede affected downstream responses, deterministically rebuild queue, and record an audit event.
9. After all queued follow-ups finish, execute exactly one configured `rejoin_target`. A default fallback is mandatory for the empty queue.
10. Validate cycles, unreachable targets, missing routes and hidden future-answer dependencies before publication.

**Separate modes must never be conflated:** `ORDERED_RULES` chooses **one** winning destination when several rules match; `SEQUENTIAL_FOLLOWUPS` may create **several** follow-up questions but executes them in a controlled order before one shared rejoin; `ALL_TO_NEXT` creates no follow-ups. The author must consciously choose a mode, and the UI must preview an example result of that mode.

### 6.7 Option and Other answer evidence shape (illustrative)

```json
{
  "question_code": "POLICY_CONCERNS",
  "question_version": "2.1.0",
  "answer_type": "MULTI_SELECT",
  "selected_option_codes": ["PREMIUM", "BENEFITS", "OTHER"],
  "other_details": {"option_code": "OTHER", "text": "Clarify the waiting period"},
  "routing": {
    "mode": "SEQUENTIAL_FOLLOWUPS",
    "effective_order": ["PREMIUM", "BENEFITS", "OTHER"],
    "followup_queue": ["Q-PREMIUM", "Q-BENEFITS", "Q-OTHER"],
    "queue_cursor": 0,
    "rejoin_target": "Q-COMMON-NEXT",
    "dedupe_policy": "ONCE_PER_ANSWER",
    "global_override": null
  }
}
```

The shape is illustrative and shall be frozen only after Pydantic/JSON Schema contract review. Use stable codes for evaluation, not human-readable labels. Option-specific follow-up mappings belong to the **Question Instance routing binding inside its Module Version**, while the shared Question Version retains wording, response type and allowed options.


## 7. Conditions: outside, inside and between Lego modules

| Scope | What it answers | Example | UI location |
|---|---|---|---|
| **Survey / Module entry** | Should this module run for this case? | `product_type = ILP` | Entry chip on Lego module card |
| **Module internal decision** | Which question should be asked next? | `annual_premium > 12000 AND sum_assured ≥ 500000` | Compact Decision card inside module |
| **Module outcome connector** | Which module follows given result? | If Suitability outcome `CLARIFICATION_REQUIRED`, activate Escalation | Connector/exit inspector on Lego canvas |
| **Question applicability** | Is a specific question applicable now? | `age ≥ 60` | Question inspector / optional applicability chip |
| **Answer-based decision** | What should happen based on prior answer? | `answers.Q3 = NO` | Decision card after question or route rule |

### 7.1 Rule builder design

A condition drawer starts with a simple line editor: **Field | Operator | Value**. Authors can add `AND`, `OR`, `NOT` groups when required. Indentation and labels explain nesting. The drawer shows (a) plain English summary, (b) sample evaluation with profile, (c) version and consumer count, (d) `Save new / Save as reusable / Use existing`, (e) conflicts/UNKNOWN warnings. Rules may call **other versioned rule references** only under explicit dependency resolution and circular-reference prevention.

### 7.2 Rule behavior examples (illustrative)

```text
ENTRY: High Value Review
   ANY of:
      Annual Premium >= 12,000 SGD
      Sum Assured    >= 500,000 SGD
   UNKNOWN => NEEDS_DATA / BLOCK (not False)

INSIDE: Suitability / Decision D2
   ALL of:
      Age >= 60
      ANY of:
         Annual Premium > 12,000 SGD
         Prior Answer (risk_understood) = NO
   MATCH    => Enhanced affordability Q9
   NO_MATCH => Standard Q10
   UNKNOWN  => Review eligibility / obtain missing facts

BETWEEN MODULES:
   IF Suitability outcome = CLARIFICATION_REQUIRED
      => Escalation & Follow-up module
   ELSE => Closing module
```

### 7.3 Rule safety requirements

1. No SQL strings, Python expressions, dynamic eval, arbitrary LLM-generated route logic or ungoverned API calls in predicates.
2. Preserve type, unit, currency and source of each operand; decimal financial comparisons are exact within defined precision.
3. Typed values can be `KNOWN`, `UNKNOWN`, `NOT_APPLICABLE` or `CONFLICTING`; decide policy explicitly rather than coercing to empty/zero/False.
4. Prevent PII from being copied into authoring logs or synthetic scenario templates.
5. Evaluate the same rule using the same version and values identically in simulator and backend.
6. If multiple conditions target a single module, require `ANY`, `ALL` or explicit ordered route policy; do not guess intent.


---

## 8. Proposed canonical data model

### 8.1 Domain entities

**Authoring/catalog tables (suggested):**

| Entity | Core columns / relationships | Key constraints |
|---|---|---|
| `survey_definitions` | `id`, `code`, `name`, `purpose`, `owner`, `status` | Stable definition identity |
| `survey_versions` | `id`, `survey_id`, `version`, `manifest_hash`, `state`, `created_by`, timestamps | Published rows immutable |
| `survey_module_instances` | `id`, `survey_version_id`, `module_version_id`, `position`, `params`, `entry_rule_binding_id` | One definition may have many instances |
| `survey_connections` | `id`, `survey_version_id`, `source_instance_id`, `source_outcome_code`, `target_instance_id`, `condition_binding_id`, `priority`, `fallback` | Unambiguous connector selection |
| `module_definitions` / `module_versions` | `id`, `code`, `name`, `outcomes`, `version`, `status`, `graph_hash` | Independent versioned Lego block |
| `module_nodes` | `id`, `module_version_id`, `node_type`, `question_version_id`, `condition_binding_id`, `display_config` | Unique per-module placement; stable node code |
| `module_edges` | `id`, `module_version_id`, `source_node_id`, `answer_code`/`result_code`, `target_node_id`/`outcome_code`, `priority` | Typed edges; target defined |
| `question_definitions` / `question_versions` | `id`, `code`, `wording`, `type`, `validation`, `approved_script_ref`, `status` | Reusable text/type independent of routing |
| `answer_options` | `question_version_id`, `option_code`, `label`, `display_order`, `exclusive`, `is_other`, `other_text_schema`, `allow_with_others` | Stable code; `OTHER` companion field validated by option schema |
| `question_routing_bindings` | `module_node_id`, `mode`, `default_target`, option/condition overrides, `followup_plan_id` | Module-specific routing separate from shared question content |
| `multi_select_followup_plans` | `question_node_id`, `option_code`, `followup_refs`, `priority`, `dedupe_policy`, `rejoin_target`, `interrupt_policy` | Ordered deterministic queue plan; all targets validated |
| `condition_definitions` / `condition_versions` | `id`, `name`, `ast_json`, `params_schema`, `field_dependencies`, `status` | Typed AST, no executable code |
| `condition_bindings` | `id`, `condition_version_id`, `scope`, `parameters`, `unknown_policy` | Context-specific without editing rule definition |
| `field_catalog` | `field_code`, `source`, `data_type`, `units`, `operators`, `sensitivity`, `availability` | Governed source and type |
| `test_profiles` / `test_scenarios` | synthetic profile values, answer sequence, expected path/outcome, owner, versions | Synthetic-only fixtures by default |
| `approvals` / `audit_events` | candidate hash, maker/checker, decision, reason, event payload | Append-only audit |

**Runtime tables (suggested, aligned with Call360 case/attempt/session domain):** `survey_runs`, `survey_run_module_occurrences`, `survey_answers`, `survey_rule_evaluations`, `survey_transitions`, `survey_run_events`, `survey_run_evidence`, `survey_run_snapshots`. Use existing case/attempt/session IDs as foreign keys rather than creating parallel customer identity models. Every event uses a monotonically ordered sequence or transaction-safe equivalent for audit/replay. A run with an active multi-select follow-up queue additionally persists `selected_option_codes`, `other_text` (if permitted), resolved queue order, queue cursor, rejoin target and causation data in its immutable/pinned execution evidence.

### 8.2 Canonical JSON shape (illustrative, not approved final API schema)

```json
{
  "survey": {"id": "survey-new-business", "version": "3.0.0"},
  "module_instances": [
    {
      "instance_id": "mi-general",
      "module_ref": {"id": "mod-general", "version": "2.1.0"},
      "entry": {"mode": "ALWAYS"},
      "outcome_routes": [{"from": "COMPLETED", "to_module": "mi-suitability"}]
    },
    {
      "instance_id": "mi-suitability",
      "module_ref": {"id": "mod-suitability", "version": "4.0.0"},
      "entry": {
        "mode": "RULE",
        "condition_ref": {"id": "rule-is-ilp", "version": "1.0.0"},
        "unknown_policy": "BLOCK"
      },
      "outcome_routes": [
        {"from": "COMPLETED", "to_module": "mi-closing"},
        {"from": "CLARIFICATION_REQUIRED", "to_module": "mi-escalation"}
      ]
    }
  ],
  "dependency_lock": {
    "modules": ["mod-general@2.1.0", "mod-suitability@4.0.0"],
    "rules": ["rule-is-ilp@1.0.0"]
  }
}
```

```json
{
  "module": {"id": "mod-suitability", "version": "4.0.0"},
  "entry_node_id": "Q1",
  "outcomes": ["COMPLETED", "CLARIFICATION_REQUIRED"],
  "nodes": [
    {"id": "Q1", "type": "QUESTION", "question_ref": "q-benefits@2.0.0"},
    {"id": "Q2", "type": "QUESTION", "question_ref": "q-risks@1.3.0"},
    {"id": "Q3", "type": "QUESTION", "question_ref": "q-clarify@1.0.0"},
    {"id": "D1", "type": "DECISION", "condition_ref": "rule-enhanced-review@1.1.0"}
  ],
  "edges": [
    {"from": "Q1", "on": "YES", "to": "Q2"},
    {"from": "Q1", "on": "NO", "to": "Q3"},
    {"from": "Q3", "on": "AFTER_CAPTURE", "to": "Q2"},
    {"from": "Q2", "on": "YES", "to": "D1"},
    {"from": "Q2", "on": "NO", "outcome": "CLARIFICATION_REQUIRED"},
    {"from": "D1", "on": "MATCH", "outcome": "COMPLETED"},
    {"from": "D1", "on": "NO_MATCH", "outcome": "COMPLETED"},
    {"from": "D1", "on": "UNKNOWN", "outcome": "CLARIFICATION_REQUIRED"}
  ]
}
```

```json
{
  "condition_id": "rule-enhanced-review",
  "version": "1.1.0",
  "ast": {
    "op": "AND",
    "children": [
      {"op": "GTE", "left": {"field": "customer.age"}, "right": {"param": "minimum_age"}},
      {"op": "OR", "children": [
        {"op": "GT", "left": {"field": "policy.annual_premium_sgd"}, "right": {"param": "premium_threshold"}},
        {"op": "EQ", "left": {"field": "answers.risk_understood"}, "right": {"literal": "NO"}}
      ]}
    ]
  },
  "parameters": {"minimum_age": 60, "premium_threshold": 12000},
  "unknown_policy": "ROUTE_UNKNOWN"
}
```

**Additional response/routing illustration — multi-select Other with sequential follow-ups:**

```json
{
  "question_ref": "policy-concerns@2.1.0",
  "options": [
    {"code": "PREMIUM", "label": "Premium affordability"},
    {"code": "BENEFITS", "label": "Product benefits"},
    {"code": "OTHER", "label": "Other — please specify", "is_other": true,
     "other_text_schema": {"required": true, "max_length": 500}},
    {"code": "NONE", "label": "None of the above", "exclusive": true}
  ],
  "module_question_binding": {
    "routing_mode": "SEQUENTIAL_FOLLOWUPS",
    "option_followups": [
      {"option_code": "PREMIUM", "priority": 10, "question_nodes": ["Q-PREMIUM"]},
      {"option_code": "BENEFITS", "priority": 20, "question_nodes": ["Q-BENEFITS"]},
      {"option_code": "OTHER", "priority": 30, "question_nodes": ["Q-OTHER"]}
    ],
    "dedupe": "ONCE_PER_ANSWER",
    "rejoin_target": "Q-CONFIRMATION",
    "empty_selection_fallback": "Q-CONFIRMATION"
  }
}
```

The last condition example is a structural DSL illustration, not a JavaScript/Python expression to execute. Schema validation must enforce permitted operators and field types. Production IDs may use UUID/ULID with separate business-friendly codes.

### 8.3 Relationship and inheritance rules

- **Definition ↔ Version ↔ Instance:** Definition is stable identity. Version is immutable approved content. Instance is placement and context-specific routing/parameters.
- **Question text versus routing:** Shared Question Version owns wording/type/option codes. Module Question Instance owns placement, route choices, applicable context and optional approved presentation binding; modifying routing does not globally rewrite a shared question.
- **Rule definition versus binding:** Reused Condition Version owns the AST and parameter schema. Bindings supply parameters, scope and UNKNOWN behavior; changed bindings do not modify shared rule AST.
- **Dependencies:** Published Survey manifest references exact Module Versions; each Module Version references exact Question/Condition Versions; published manifest includes full transitive dependency lock and content hashes.
- **Draft changes:** Editing a shared draft or creating a new version cannot silently uplift an existing consumer. Provide `Upgrade`, `Keep pinned`, and `Fork` actions with impact preview.
- **Archived and retired:** Retired definitions remain accessible for historical run reconstruction; new placement may be forbidden by policy.

---

## 9. API and service contracts (proposed)

### 9.1 Authoring and library APIs

| API (illustrative REST shape) | Behavior / controls |
|---|---|
| `GET /survey-studio/surveys?status=&tag=&q=` | Search, filter, paginate definitions and versions |
| `POST /survey-studio/surveys` | Create draft survey from blank or template |
| `GET /survey-studio/surveys/{surveyId}/versions/{versionId}` | Return canonical draft/immutable manifest and dependencies |
| `PATCH /survey-studio/drafts/{draftId}` | Optimistic-concurrency JSON patch/save, revision and actor audit |
| `GET /survey-studio/modules` / `POST /survey-studio/modules` | Reusable Module catalog and draft creation |
| `GET /survey-studio/questions` / `POST /survey-studio/questions` | Reusable Question catalog and draft creation |
| `GET /survey-studio/conditions` / `POST /survey-studio/conditions` | Reusable typed Rule catalog and draft creation |
| `GET /survey-studio/fields` | Governed field metadata/operator sets and data source constraints |
| `POST /survey-studio/rules/evaluate` | Non-authoritative preview using synthetic/test context; shares backend evaluator |
| `POST /survey-studio/questions/preview-routing` | Preview selected option set, Other validation, ordered/queued follow-ups and common rejoin without mutating the draft |
| `POST /survey-studio/drafts/{id}/followup-plans/validate` | Verify option mappings, stable queue order, dedupe, stop override, queue termination and destination availability |
| `POST /survey-studio/drafts/{id}/validate` | Server validation with issue IDs, severity, node paths and suggestions |
| `POST /survey-studio/drafts/{id}/simulate` | Simulate profile/answers; return path, condition traces, coverage |
| `POST /survey-studio/drafts/{id}/submit-review` | Freeze candidate hash and lock for maker-checker review |
| `POST /survey-studio/reviews/{id}/decision` | Approve/reject; checker identity required |
| `POST /survey-studio/approved/{id}/publish` | Server validates same candidate hash and atomically publishes |
| `GET /survey-studio/assets/{id}/consumers` | Reuse/impact graph, published and draft consumers |
| `POST /survey-studio/assets/{id}/upgrade-preview` | Diff and affected scenario results before upgrade |

### 9.2 Runtime APIs

| API (illustrative REST shape) | Behavior / controls |
|---|---|
| `POST /survey-runs` | Start from authorized assigned published version with idempotency key |
| `GET /survey-runs/{id}/current-step` | Approved question/action and authorized presentation metadata |
| `POST /survey-runs/{id}/answers` | Validate typed answer; atomically append answer + route decision; return next step |
| `POST /survey-runs/{id}/events` | Controlled refusal, interruption, reschedule and escalation |
| `POST /survey-runs/{id}/pause` / `.../resume` | Persist and resume exact snapshot |
| `GET /survey-runs/{id}/trace` | Ordered step, fact, rule and transition evidence subject to RBAC |
| `GET /survey-runs/{id}/summary` | Outcomes, unresolved items and links to case/review records |

**Common contract requirements:** Strong Pydantic v2 schemas, OpenAPI, auth scopes, `ETag` or revision check on drafts, idempotency key on state mutation, stable error codes (`ROUTE_MISSING`, `INPUT_UNKNOWN`, `AMBIGUOUS_ROUTE`, `VERSION_MISMATCH`, `APPROVAL_REQUIRED`), correlation IDs, rate limits, clear 4xx/5xx semantics and audit events. Business logic must be in backend service layer, not React components.

### 9.3 Example step response

```json
{
  "survey_run_id": "run-123",
  "snapshot_hash": "sha256:example",
  "module_instance_id": "mi-suitability",
  "node_id": "Q2",
  "question": {
    "question_code": "RISK_UNDERSTANDING",
    "answer_type": "YES_NO",
    "text": "Do you understand the key risks and exclusions?",
    "answer_options": [{"code": "YES", "label": "Yes"}, {"code": "NO", "label": "No"}]
  },
  "execution_state": "AWAITING_ANSWER",
  "next_step_authority": "SERVER"
}
```

Do not expose unreachable or restricted future questions to clients that are not authorized to inspect the survey design. Runtime client may show only the current approved customer-facing prompt and permitted options; internal routing details are available through privileged trace APIs, not the general customer-facing channel.

---

## 10. Technical architecture and placement in Call360

```text
Call360-frontend (React + TypeScript)
 ├─ Survey Studio home and reusable asset catalogs
 ├─ Survey Lego Composer (sortable/accessible cards)
 ├─ Guided Module Builder (progressive branching)
 ├─ Advanced Graph Editor (auto-layout, zoom, connectors)
 ├─ Condition Drawer (typed rule AST editor)
 ├─ Simulator / Scenario Manager / Validation & Review
 └─ Generated API client, optimistic drafts, undo/redo
              │ versioned HTTP APIs
              ▼
Call360-backend (FastAPI + Pydantic + PostgreSQL)
 ├─ Library / Version / Dependency services
 ├─ Canonical Graph & Condition AST schemas
 ├─ Authoring Draft / Review / Publishing services
 ├─ Survey Compiler (locked, executable manifest)
 ├─ Deterministic Survey State Machine
 ├─ Rule Evaluator (TRUE / FALSE / UNKNOWN)
 ├─ Static Graph Validator and Test Simulator
 ├─ Case/Attempt/Session/Script binding integration
 └─ Audit, trace, authorization, persistence
              │
              ▼
Existing Call360 case, script, assignment, response and review domain
```

`Call360-specs` owns product requirements, ADRs, canonical JSON schemas, API contracts and scenario golden datasets. `Call360-backend` implements authoring validation, published snapshot compilation, execution, audit and persistence. `Call360-frontend` implements consistent UI editing and visualizations. Pin dependencies and generated clients in CI to avoid frontend/backend contract drift.

### 10.1 Recommended implementation boundaries

- **Canonical graph model:** Treat Survey Module Instances and Module Node graphs as related but distinct layers. A module has internal decision edges; the survey has outcome/eligibility connections. Do not flatten everything into one manually edited canvas.
- **Compiler:** Resolve every referenced approved dependency into an immutable executable manifest, with hashes. Fail on missing or deprecated dependency, invalid route, unresolved parameter, conflicting mapping or unauthorized transition.
- **Evaluator:** Pure typed rule evaluation plus explicit state and provenance. Favor deterministic domain services over free-form prompt logic.
- **Execution:** Durable transaction/state machine per SurveyRun; idempotent step advancement; optimistic concurrency or run lock to prevent double advancement; atomic answer+decision+event commit.
- **Frontend graph:** Maintain stable node/edge IDs; auto-layout as a *view*, not a persisted business rule. Persist optional manual positions separately as layout metadata. Graph layout must handle merges/cross-edges; do not assume tree shape.
- **UI library and graph framework:** Engineering selection is open; any chosen library must support accessibility, typed ports, controlled nodes, undo/redo and layout stabilization. Avoid locking requirements to a specific frontend package.
- **Legacy Script Studio coexistence:** Keep one explicit source of truth for approved wording and script bindings. Survey Studio does not authorize live text changes that bypass existing script approval. Define integration ownership before implementation.
- **Voice readiness without coupling:** A later speech layer (Genesys/voice/LLM) consumes current approved step and submits candidate answers; it cannot determine next node. Current survey implementation must not depend on GPT-Live being enabled.

### 10.2 Compile and runtime state machine (illustrative)

```text
DRAFT GRAPH → VALIDATE → REVIEW → APPROVE → COMPILE → PUBLISH
                                                     │
START SURVEY RUN → SNAPSHOT PINNED → EVALUATE MODULE ELIGIBILITY
       → ENTER MODULE → GET CURRENT NODE
       → [DECISION: evaluate rule and route] OR [QUESTION: await valid answer]
       → APPEND ANSWER/EVALUATION/TRANSITION
       → NEXT NODE / MODULE OUTCOME
       → NEXT ELIGIBLE MODULE / SURVEY OUTCOME
       → COMPLETE / CLARIFICATION / ESCALATE / DECLINED / PARTIAL
```

Each step has a machine state (`READY`, `WAITING_FOR_ANSWER`, `BLOCKED_UNKNOWN`, `PAUSED`, `TERMINATED`, etc.). Never conflate a module being skipped with a user answering No, and never mark a SurveyRun complete simply because no next route was configured.

---

## 11. Nonfunctional, security, quality and operational requirements

All numeric thresholds below are **proposed engineering acceptance targets**, not an existing SLO commitment; finalize during architecture review.

| ID | Priority | Requirement | Proposed measurable target |
|---|---|---|---|
| SS-NFR-001 | P0 | Interactive editor responsiveness | Typical card/route edits visually update within 150 ms on supported desktop; backend save asynchronous |
| SS-NFR-002 | P0 | Scale of authoring model | Support at least 50 modules/survey, 150 nodes/module, 1,000 nodes/survey, 5,000 references across shared catalogs without loss of authoring correctness |
| SS-NFR-003 | P0 | Simulator latency | For simple local synthetic profile, p95 evaluation/next-step response ≤ 500 ms in test environment excluding external calls |
| SS-NFR-004 | P0 | Draft save durability | Autosave after 1–3 seconds idle; unsaved status and retry visible; data loss avoided on normal refresh after acknowledged save |
| SS-NFR-005 | P0 | Concurrency | Optimistic version check prevents silent overwrite by second author; meaningful conflict resolution shown |
| SS-NFR-006 | P0 | Reliability | Backend state advances atomically; retries with same idempotency key return same outcome |
| SS-NFR-007 | P0 | Security | Existing Call360 authentication/authorization, least privilege, maker/checker separation, audit logging, protected secrets, service permissions |
| SS-NFR-008 | P0 | Privacy | Avoid real PII in templates and profiles; mask sensitive fields in logs/previews; retention and deletion follow organization policy |
| SS-NFR-009 | P0 | Accessibility | Target WCAG 2.2 AA; keyboard path for drag/drop and ports; screen-reader edge labels; contrast and focus states |
| SS-NFR-010 | P0 | Data integrity | Immutable published versions; full foreign-key/reference checks; hashes and event sequencing for reproducible runs |
| SS-NFR-011 | P0 | Observability | Correlation ID, audit event, route evaluation reason and structured failure metrics for every runtime transition |
| SS-NFR-012 | P0 | Testing | Unit, schema, property-based graph/rule tests, cross-editor round-trip, API integration, persistence and Playwright E2E |
| SS-NFR-013 | P0 | Browser compatibility | Current supported Chrome and Edge desktop; responsive read-only/review on narrower devices; cross-browser smoke tests |
| SS-NFR-014 | P0 | Deployment | DB schema migrations, rollbacks, feature toggles, no migration of active run snapshots without compatibility rules |
| SS-NFR-015 | P1 | Availability | Define business SLO and backup/restore targets before production authorization; no zero-downtime claim without tests |
| SS-NFR-016 | P1 | Performance budget | Incremental graph rendering and virtualization for large catalog lists; full graph view may use lazy groups |
| SS-NFR-017 | P1 | Localization | English-first content and UI; stable answer codes and future language variants |
| SS-NFR-018 | P0 | Input safety | Limit AST depth/node count, text sizes, payload sizes and traversal steps; reject untrusted embedded HTML/script |

**Specific security tests:** An Author cannot publish; a Checker cannot approve own candidate; runtime cannot access Draft; a question from one scoped library cannot leak another scope's protected content; API cannot be tricked into arbitrary node advancement; no real customer profile can be saved to general reusable synthetic fixture collections without authorization and policy controls.

---

## 12. Acceptance scenarios / golden test matrix

These scenarios should become executable golden fixtures in `Call360-specs` and automated frontend/backend tests. All input thresholds are illustrative.

| ID | Scenario / fixture | Expected behavior |
|---|---|---|
| SS-AT-001 | Author creates Survey with General, Suitability and Closing from library | Three Module Instances; each pins approved version; Lego sequence and inspector show rule/outcomes |
| SS-AT-002 | General module `Always`, Suitability eligible only for ILP | Term-life profile skips Suitability with `SKIPPED_FALSE`; general and closing still run |
| SS-AT-003 | Premium > 12,000 OR sum assured ≥ 500,000 entry rule | High-premium/low-sum and low-premium/high-sum each activate same module |
| SS-AT-004 | Premium exactly 12,000 with `>` operator | Threshold rule false; no accidental `≥` interpretation |
| SS-AT-005 | Premium missing | Rule evaluates UNKNOWN; configured block/unknown path executes, not silently false |
| SS-AT-006 | Inside module Q1 Yes→Q2 and No→Q3, Q3→Q2 | Q2 appears once, has two incoming edges, and can be reached from both paths |
| SS-AT-007 | Add Yes/No question between Q1 Yes→Q2 | New normal branch continues to Q2; No is visibly incomplete until routed; publish blocked meanwhile |
| SS-AT-008 | Add single-choice question with four choices all to NEXT | One default target; all four valid choices advance to same next question |
| SS-AT-009 | Map each single choice to distinct question then merge | Correct target for each option; shared merge appears once |
| SS-AT-010 | Multi-select PREMIUM + BENEFITS matches two rules | Explicit priority chooses one route and trace explains conflict resolution |
| SS-AT-011 | Multi-select includes exclusive NONE and another option | Answer rejected with validation explanation |
| SS-AT-012 | Free text with mandatory minimum length | Empty/too-short answer rejected; valid answer saved, next node selected deterministically |
| SS-AT-013 | Compound `Age ≥ 60 AND (Premium > threshold OR Prior Answer = NO)` | Nested group truth table matches expected results incl UNKNOWN |
| SS-AT-014 | Condition depends on answer not yet asked | Validation blocks evaluation/publish unless explicit supported deferral policy exists |
| SS-AT-015 | Suitability emits `CLARIFICATION_REQUIRED` | Escalation module becomes eligible via outcome connection; exact reason in trace |
| SS-AT-016 | Delete shared Q3 with incoming Q1-No and Q2-No | Impact dialog lists both edges; author must explicitly select replacement or cancel |
| SS-AT-017 | Change shared Condition to new version | Published consumers unchanged; draft upgrade preview lists affected surveys/modules |
| SS-AT-018 | Guided route edit then switch Graph and back | Identical node IDs, option routes and semantics across views |
| SS-AT-019 | Create accidental cycle Q2→Q1 | Validator fails; simulator/runner stops via traversal protection |
| SS-AT-020 | Two module connector rules both match at same priority | Validation reports ambiguity unless policy explicitly resolves ordering |
| SS-AT-021 | Maker submits candidate, edits it, checker attempts to approve old hash | Approval rejected or old snapshot remains separate and immutable |
| SS-AT-022 | Maker tries to approve own change | Backend rejects self-approval |
| SS-AT-023 | Published SurveyRun paused after Q5 then resumed after a new library version is published | Original run resumes on its original pinned snapshot |
| SS-AT-024 | Same answer submission retried with same idempotency key | Exactly one answer and one transition recorded |
| SS-AT-025 | Customer changes Q1 answer using authorized Back/Edit flow | Downstream stale responses invalidated/superseded and new path recalculated |
| SS-AT-026 | Simulate two synthetic profiles against same draft | Different reached module/question lists and rule explanations visible |
| SS-AT-027 | Business author without graph expertise builds 10 questions with two branches | Guided authoring succeeds with inline `+`, destination picker and minimal manual connector work |
| SS-AT-028 | Library Question used by two different Module Versions | Same Question Version referenced; each placement has independent routing |
| SS-AT-029 | Runtime client requests arbitrary future question | Backend rejects unauthorized traversal and returns only permitted current step |
| SS-AT-030 | Missing mandatory wording approval/dependency | Publish gate fails, with actionable blocker and dependency reference |
| SS-AT-031 | Complete path coverage simulation does not exercise one choice | Coverage clearly shows untested choice, never claims 100% correctness |
| SS-AT-032 | Eligibility based on previous module outcome not yet available | Author sees unavailable dependency and runtime follows explicit defer/block policy |
| SS-AT-033 | Single-choice Other selected with required detail missing | Inline form rejects submission with specific message; selection remains selected |
| SS-AT-034 | Single-choice Other selected with valid text | Store `OTHER` code + details and execute configured Other-specific route |
| SS-AT-035 | Single-choice Other unselected | No phantom Other text stored or submitted; standard chosen-option route applies |
| SS-AT-036 | Multi-select allows Other alongside Premium | Both option IDs and Other text persist; explicit follow-up plan applies |
| SS-AT-037 | Multi-select exclusive Other setting rejects Other + Premium | Specific exclusivity error; cannot proceed until selection is valid |
| SS-AT-038 | Exclusive None selected alongside Benefits | Runtime rejects invalid set; UI displays actionable explanation |
| SS-AT-039 | Multi-select Premium + Benefits in SEQUENTIAL_FOLLOWUPS | Premium follow-up executes, then Benefits follow-up, then one shared rejoin |
| SS-AT-040 | Multi-select selection order differs from configured follow-up order | Execution follows explicit priority/order rather than click order or hash iteration |
| SS-AT-041 | Multiple option mappings share one follow-up target | Deduplication follows configured policy; no accidental duplicate question |
| SS-AT-042 | Critical Risk selected with Premium + Benefits | Explicit approved escalation override applies and skipped queue items are traced |
| SS-AT-043 | Back/edit original multi-select from Premium + Benefits to Claims only | Stale follow-ups invalidated, revised queue computed, audit evidence preserved |
| SS-AT-044 | Pause/resume halfway through multi-select follow-up queue | Resume on pinned snapshot at exact queue cursor; no repeat/skip |
| SS-AT-045 | Missing rejoin/option follow-up target | Validation blocks publishing and focuses option route |
| SS-AT-046 | All-to-next selected for five-option multi-select | Any valid selection set follows one common route, with no queues |
| SS-AT-047 | ORDERED_RULES Premium + Benefits with both rules true | First configured matching rule wins; no second branch launched |
| SS-AT-048 | Authors configure `Other + specify` inside Guided view and switch Graph | Same option code, text constraint and destination displayed after round trip |
| SS-AT-049 | User builds 3-module survey via Lego UI in moderated session | Meets UX-GATE-01 without authoring a graph manually |
| SS-AT-050 | User composes 5-choice per-option routing in module card | Meets UX-GATE-02; no invalid options or unexpected route rewrites |
| SS-AT-051 | User adds multi-select Other + two sequential follow-ups | Meets UX-GATE-03; simulator shows expected ordered queue and merge |
| SS-AT-052 | Author runs two-profile What-if compare and publishes draft with invalid branch | First divergence explained; review blocked and issue deep link works |

### 12.1 Mandatory scenario sets before first controlled release

- At least one **small** survey (3 modules), one **medium** survey (10 modules, 80 nodes), and one **large** survey (50 modules, at least 1,000 nodes across instances).
- Each supported answer type with default NEXT, explicit branch, shared merge, and invalid/missing data. Include single/multi-choice `OTHER` typed text, exclusive combinations, priority route selection and sequential follow-up queues.
- Nested AND/OR/NOT conditions, unknown values, currency precision and threshold boundaries.
- Reuse/upgrade impact testing, permission/approval denial paths, persistence after refresh, and pause/resume on pinned snapshot.
- Accessibility keyboard journey for assembling modules and editing question routes without drag-and-drop.

---

## 13. Proposed delivery phases and acceptance gates

| Phase | Scope | Exit gate |
|---|---|---|
| **P0-A · Canonical model and libraries** | Entity schemas, typed AST, version/dependency model, backend validation, Survey/Module/Question/Condition catalogs | Contract schemas signed off; Golden fixtures for graph and conditions pass |
| **P0-B · Guided Lego authoring** | Survey Composer, module Guided Builder, first-class Other options, P0 sequential multi-select follow-ups, inline insertion, safe deletion, condition drawer, polished visual interaction system | Business user assembles, edits and validates a representative survey with no graph expertise; UX-GATE-01/02/03 evidenced |
| **P0-C · Graph + simulator** | Full graph rendering/editing, synthetic profiles, step-by-step simulation, sequential follow-up queue trace, explainable decisions, scenario save/replay | Guided↔Graph parity, simulator queue fixtures, route coverage and recovery pass; UX-GATE-09 evidenced |
| **P0-D · Governance and runtime** | Approval, immutability, compilation, Case/Attempt/Session and Script bindings, audit, idempotent progression | Maker-checker, snapshot pinning, resume and production security gates pass |
| **P1 · Power-user and productivity** | Batch scenarios, diff/compare, partial loop policy, subflows, bulk edit, expanded answer types and metrics | Performance and usability targets achieved; dependency upgrade workflows validated |

**Recommended implementation order:** build and test the canonical graph/condition engine and version model first, then both UI editors on top of the same API. Do not implement a Guided Editor with a separate simplified tree schema and retrofit a graph later; that creates incompatible business logic and unsafe conversions.

---

## 14. Definition of done (production gate)

A requirement is done only when its API/schema is versioned, backend behavior is tested, frontend behavior is accessible, failure paths are covered, instrumentation/audit is present, business acceptance is demonstrated, and documentation is updated. The Survey Studio initial release requires:

- All P0 requirements resolved or formally re-scoped by owner with traceable decision.
- All P0 golden scenarios passing in CI and evidence captured.
- No blocker in server-side schema, graph, condition or dependency validation.
- Guided and Advanced Graph parity confirmed on merge/branch/condition fixtures.
- Profile simulator reproduces backend evaluator decisions and can explain each executed/skipped step.
- Shared asset version changes cannot silently alter published versions or active runs.
- Maker-checker, runtime permissions, privacy controls and audit trail reviewed and accepted.
- Explicit sign-off for script/wording approval integration and customer-facing delivery constraints.
- Operational recovery, idempotency, concurrency and rollback/retirement tests completed.
- Usability testing confirms nontechnical authors can build representative flows quickly, including single/multi-choice Other and sequential multi-select follow-ups, with Section 18 UX gates evidenced and approved.

---

## 15. Open design decisions (owner / architecture to resolve)

These are decisions requiring an explicit ADR or signed product choice, rather than hidden assumptions:

1. **Survey Studio versus existing Script Studio ownership:** Is Survey Studio the authoritative content and branching editor with Script Studio supplying approved presentation/voice text, or does Script Studio retain question content authority? Recommend canonical Survey Studio routing, explicit Script Delivery Binding and one approval chain; no duplicate uncontrolled question masters.
2. **Shared Question upgrades:** Default to version pinning; decide whether question text may be locally overridden per Module Instance. Recommend “fork version” rather than silent local override for regulated customer wording.
3. **Module outcome catalog:** Confirm standard exit codes and whether Survey designers can add custom outcomes without compliance approval. Recommend governed codes plus custom draft labels mapped to allowed codes.
4. **Multiple module conditions:** Choose `first matching connector by explicit priority` versus `all eligible blocks in ordered plan`; default can be ordered eligibility with explicit override routing. The user must see which one applies.
5. **Rule UNKNOWN policy:** Specify when to block, ask for missing data, defer, or route to manual review; avoid global UNKNOWN-as-FALSE.
6. **Multi-select follow-up behavior (updated v1.1):** P0 supports both first-match priority routing and an explicit per-selected-option sequential follow-up queue, plus common NEXT. Remaining sign-off decisions: ordering default, dedupe policy, escalation interrupt/resume, authoring permissions and optional follow-up group reuse. These are policy parameters, not permission to remove P0 capability.
7. **Loop policy:** P0 reject cycles and enforce traversal caps; P1 consider bounded repeats only if proven business need.
8. **Mandatory wording and channel variance:** Define approved text ownership for web/agent/voice delivery and evidence expectations.
9. **Simulator data rules:** Synthetic-only by default; define whether authorized masked real-case replay is permitted in a separate controlled environment.
10. **Scope, scale and SLO:** Confirm expected largest graph, concurrent editors/runs and measured performance targets.
11. **Rule authoring permissions:** Determine whether only Curators can create global reusable rules, while Authors may bind parameters or create personal draft rules.
12. **Publish assignment:** Define the exact point at which a survey version is selected/pinned to a Call360 callback Case/Attempt relative to existing assignment rules.
13. **Imports/exports:** Confirm whether Markdown/CSV/JSON import is needed before P1, and the governance process for imported regulated wording.
14. **Branch analytics and review:** Define whether customer follow-up/evidence workbench is in scope of Survey Studio or handled exclusively by existing compliance/review modules.

---

## 16. Visual design references from the prior prototype screenshots

The following user-reviewed prototype screenshots are *design references*, not formal approved UI requirements. Section 18 makes the expected UX quality, interaction behavior, storyboard and release gates explicit. Translate their visual intent into a consistent component system; improve rather than reproduce visual defects.

| Reference file | Screen role | Preserve / evolve |
|---|---|---|
| `Call360_Lego_01_Module_Library.png` | Library and reusable Lego catalog | Reusable cards, add flow, search and status; add dependency/version clarity |
| `Call360_Lego_Survey_Assembly.png` | Primary Lego Survey Composer | Compact module blocks with visible eligibility chips and intuitive ordering |
| `Call360_Lego_03_Entry_Condition_Editor.png` | Survey-level module entry rule | Nested conditions in drawer; human-readable chip stays on main card |
| `Call360_Lego_Module_Branching.png` | Inside module / guided question flow | Main sequential path, inline add, expanded exception paths, shared merge indicators |
| `Call360_Lego_05_Inside_Module_Condition_Editor.png` | Internal decision-rule editor | Clear grouped AND/OR controls, test value preview and branch summaries |
| `Call360_Lego_Test_Journey.png` | Profile-based simulation | Customer inputs, active module route, question responses and execution trace |
| `Call360_Lego_07_Publishing_Review.png` | Validation and publication | Readiness gates, actionable issues, approval status and immutable version indicator |

### 16.1 UX acceptance checklist derived from the screenshots

- Users can assemble a 5-module survey from library without opening a condition AST or a question graph.
- Every module card immediately explains **when** it runs, which Module Version it uses, and its exit outcomes.
- Opening a module reveals a simple Guided Flow by default, not a sprawling graph.
- An author inserts a question with **one click on an answer branch**; route continuity is automatic but unconfigured alternatives remain visible.
- Yes/No, multiple-choice and free-text answer cards use consistent interaction patterns and labels.
- A question or rule with multiple consumers shows its **reuse status and impact** before it is changed.
- Selecting any condition reveals a compact in-context drawer with typed fields, AND/OR groups and a sample evaluation.
- Advanced Graph View is a true, editable alternate representation of the same underlying model.
- Simulator displays a **why** explanation for every activated/skipped module and every branch decision.
- Approval workflow sees exact content versions, graph validation and scenario results, never a different reconstructed draft.

---

## 17. Suggested initial epic breakdown for engineering

| Epic | Suggested requirement groups | Principal ownership |
|---|---|---|
| `SS-EPIC-01` Canonical Graph and Rule Contract | SS-ROU, SS-RUL, schema, migrations | `Call360-specs` + `Call360-backend` |
| `SS-EPIC-02` Reusable Libraries and Versioning | SS-SUR, SS-MOD, SS-QUE, dependency impact | Backend + Frontend |
| `SS-EPIC-03` Lego Composer | SS-SUR, SS-UX | Frontend |
| `SS-EPIC-04` Guided Module and Question Editor | SS-MOD, SS-QUE, SS-UX | Frontend + Backend |
| `SS-EPIC-05` Condition Builder | SS-RUL, rule test and previews | Frontend + Backend |
| `SS-EPIC-06` Advanced Graph Editor | SS-UX, canonical parity and layout | Frontend |
| `SS-EPIC-07` Simulator and Golden Tests | SS-SIM, test fixtures, coverage | Specs + Backend + Frontend |
| `SS-EPIC-08` Approval, Compile, Publish | SS-VAL, immutability, diff and approval | Backend + Frontend |
| `SS-EPIC-09` Runtime and Call360 Integration | SS-RUN, case/session/script binding and trace | Backend |
| `SS-EPIC-10` Security, Accessibility, Performance | SS-NFR and release gate | Cross-functional |

### Final design rule

**Users assemble Surveys from Lego Modules, author Module journeys through guided progressive questions, open an on-demand rule drawer only for complex conditions, switch to a full graph when needed, then validate and simulate against reusable profiles before publishing an immutable version.** Reusability of Modules, Questions, Conditions and Test Profiles is a first-class domain capability—not a copy/paste UI convenience.

---

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
