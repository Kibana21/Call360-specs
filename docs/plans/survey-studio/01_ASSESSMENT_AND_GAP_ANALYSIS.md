# SS-00 · Part 1 — Assessment and gap analysis

**Checkpoint:** SS-00 (analysis and design only; no application code, schema or contract was changed).
**Date:** 2026-11-21. **Status:** PROPOSED — awaiting owner review.
**Sources:** `docs/product/survey-studio/PRD_v1.1.md` (authoritative; 191 requirements, 161 of them P0),
`UX_EXCELLENCE_v1.1.md` (its IDs are identical to PRD §18), and a read-only inventory of the three repositories at
specs `941d2c2`, backend `7228875` (Alembic head `0026_gpt_live_provider`, OpenAPI `221985e7…`), frontend `f98d73e`
plus the accepted, uncommitted S2-A.2 layout.

Covers deliverables **A** (capability matrix), **B** (requirement-by-requirement gap analysis), **C** (reuse
unchanged) and **D** (extend, replace, retire). Architecture is in `02_ARCHITECTURE_AND_DECISIONS.md`; the plan is in
`03_IMPLEMENTATION_AND_UI_PLAN.md`.

---

## 0. The finding that shapes everything

**The existing script model already is the PRD's Definition → Version → Instance model. What it lacks is the graph.**

| PRD concept | Already exists as | Evidence |
|---|---|---|
| Survey Definition | `script_family` | migration `0005` |
| Survey Version (immutable, hashed, maker-checker) | `script_version` + manifest SHA-256 + DB guard trigger | `0005`, `0016`; `script_authoring.py` `build_manifest`, `submit`, `review`, `publish` |
| Module Definition / Version | `script_module (code, revision)`, immutable once published | `0005` `script_module_guard` |
| Module Instance (placement + entry rule) | `script_section (version, module, position, inclusion_condition)` | `0005` |
| Question Definition / Version | `question_bank_item` / `question_revision` (fully immutable) | `0005`, `0016` |
| Question Instance (placement) | `module_question (module, question_revision, position, branch_condition)` | `0005` |
| Copy-on-write "create derived version" | `_owned_module`: first edit of a published module creates a new draft revision | `script_authoring.py:607` |
| Version pinning to a case | `script_assignment` (immutable) and the session pin | `0005`, `voice/store.py` |

What does **not** exist anywhere: answer-dependent routing, edges, decision nodes, named module outcomes, connectors
between modules, option sets with stable codes, `Other`, multi-select, reusable conditions, OR / NOT / nesting,
tri-state evaluation inside scripts, follow-up queues, back/edit, pause/resume, undo/redo, a graph view, drag-and-drop.
Today a script is a **flat, linear plan**: applicability is decided once from pre-call facts, and the controller asks
"the next pending question in order" (`question_controller.py` `build_plan`, `_advance`).

**Consequence.** A linear script is a special case of the PRD's graph (every module a chain, every answer "→ next").
Survey Studio can therefore be built by **extending the existing governed model in place** — adding the graph layer —
rather than creating parallel `survey_*` tables and a second engine. That is the central recommendation of SS-00
(decision SS-D-01 in Part 2). It keeps one source of truth, keeps every existing pin, evaluation, finding and review
working, and avoids a data migration of published history.

---

## A. Existing versus proposed capability matrix

Legend: ● exists and is reusable · ◐ partly exists · ○ does not exist.

| Capability | Today | Survey Studio v1.1 | Gap |
|---|---|---|---|
| Versioned, immutable, hashed publications | ● script versions, modules, question revisions; DB triggers | Same, for surveys, modules, questions, conditions | ◐ conditions and option sets are not entities yet |
| Maker-checker with reasons, self-approval denied | ● scripts, assignment rules, finding rules, reviews | Same | ● reuse; ◐ modules cannot be approved on their own |
| Append-only audit with hash chain | ● `audit_event` chain + `script_change_event` | Same | ● reuse |
| RBAC and Singapore-only scope | ● `script.read/edit/approve/publish/simulate/assign`; `ENABLED_MARKETS={"SG"}` | PRD names 7 roles | ● reuse; role mapping is a decision (SS-D-11) |
| Reusable modules | ◐ modules are reusable across versions, but a draft module belongs to one version | Independent module library with own lifecycle | ◐ |
| Reusable questions | ● question bank with revisions; "add from bank" in the editor | Same, plus tags, owner, usage | ◐ metadata and usage view |
| Answer types | ◐ YES_NO, NUMERIC, ENUM, FREE_TEXT, ACKNOWLEDGEMENT | + single-select with codes, multi-select, `Other`, exclusivity, min/max | ◐ ENUM has labels only (no stable codes) |
| Conditions | ◐ three shapes, AND only, pre-call facts only, false on missing | Typed AST, AND/OR/NOT nesting, parameters, TRUE/FALSE/UNKNOWN, prior answers | ○ mostly new (tri-state exists only in the assignment rule engine) |
| Field catalog | ◐ `rule_inputs` (9 fields) and 4 script facts | Governed typed catalog incl. age, premium, sum assured, replacement, prior answers, module outcomes | ◐ facts exist in `0003` tables; catalog is new |
| Module entry rules | ● `script_section.inclusion_condition` | Always / rule / on prior outcome, with UNKNOWN policy | ◐ |
| Routing inside a module | ○ linear order only | Per-answer edges, merges, decisions, outcomes | ○ |
| Routing between modules | ○ fixed order | Outcome connectors with priority and fallback | ○ |
| Multi-select follow-up queue | ○ | P0 | ○ |
| Deterministic runtime | ● pure event-sourced controller; lifecycle gates; re-prompts; idempotent action ids | Graph cursor, queue, back/edit, pause/resume, decision trace | ◐ strong base, navigation is linear |
| Conversation lifecycle and gates (identity, consent, disclosure) | ● S2-D.1 | Not specified by the PRD, but must be preserved | ● keep (SS-D-08) |
| Simulator | ● interactive text simulator, scenario library with revisions, batches, A/B, first-divergence, coverage | Profile-driven what-if, path highlight, route coverage, compare, explain | ◐ engine reusable; coverage is per question, not per route |
| Static validation | ● 7 error and 9 warning codes, server-side | Reachability, cycles, ambiguity, dependencies, queues | ◐ framework reusable, graph checks new |
| Semantic diff | ● sections and questions | + routes, rules, option order, queue order | ◐ |
| Answer evaluation, findings, review | ● S3-A/B/C | Out of Survey Studio scope (PRD open question 14) | ● reuse unchanged; contract in §C |
| Assignment of a version to a case | ● S2-B/C | Unchanged (PRD open question 12) | ● reuse unchanged |
| Operational run records | ◐ `survey_run`, `question_execution`, `answer_observation`, `rule_evaluation` tables exist but only seed and fixtures write them | Runtime API writes them | ◐ no live writer yet |
| Authoring UI | ◐ form-based editor, up/down reorder, immediate save, tabs | Lego composer, guided builder, choice designer, drawers, graph, undo/redo, autosave states | ○ essentially new |
| Frontend libraries | React, react-router, react-query only | Needs drag-and-drop and graph capability | ○ no DnD, graph, state or component library |
| Design tokens | ◐ colour variables only | Spacing, type, radius, elevation, motion tokens | ○ |
| Accessibility tooling | ● axe in Playwright; layout checks at three widths | WCAG 2.2 AA, keyboard parity | ● reuse harness |

---

## B. Requirement-by-requirement gap analysis

Status: **E** = met by existing functionality · **P** = partly met, extension needed · **N** = new.
"Phase" refers to the plan in Part 3 (SS-03 … SS-10). P1/P2 items are listed for completeness and are **not** planned
for the first release unless the owner re-prioritises.

### B.1 Survey Composer (SS-SUR)

| ID | Pri | Status | Existing basis / what is missing | Phase |
|---|---|---|---|---|
| SS-SUR-001 | P0 | P | `script_family`/`script_version` create, version, abandon. Missing: clone, rename, archive, owner, last-edited | SS-05 |
| SS-SUR-002 | P0 | P | `add_section` references an exact published module revision (no copy). Missing: searchable library shelf | SS-05 |
| SS-SUR-003 | P0 | P | Reorder endpoint exists (up/down). Missing: drag, undo | SS-05 |
| SS-SUR-004 | P0 | N | Module card with rule summary, outcomes, validation status | SS-05 |
| SS-SUR-005 | P0 | P | `inclusion_condition` = "when rule matches". Missing: on-outcome mode, skip reasons, UNKNOWN policy | SS-03/04 |
| SS-SUR-006 | P0 | N | Outcome connectors (new `survey_connection`) | SS-03 |
| SS-SUR-007 | P0 | N | Auto-connect on insert; flag new exceptional exits | SS-03/05 |
| SS-SUR-008 | P0 | P | Instances already distinct per version. **Constraint:** the same question code may run once per run today (`DUPLICATE_QUESTION`; evaluation keys on `question_code`) — see SS-D-09 | SS-03 |
| SS-SUR-009 | P0 | P | COMMON + conditional sections exist | SS-05 |
| SS-SUR-010 | P0 | N | Inspector for parameters, entry rule, outcome mapping, pinned version | SS-05 |
| SS-SUR-011 | P0 | N | Delete with route impact | SS-05 |
| SS-SUR-012/013/014 | P1 | N | Templates, groups, survey-level graph | later |

### B.2 Module Builder (SS-MOD)

| ID | Pri | Status | Existing basis / what is missing | Phase |
|---|---|---|---|---|
| SS-MOD-001 | P0 | P | Modules are versioned, but a draft module is locked to one script version (`script_draft_module_lock`). Missing: standalone module drafts and approval | SS-03/08 |
| SS-MOD-002 | P0 | N | Entry port, typed nodes, outcome ports | SS-03 |
| SS-MOD-003 | P0 | N | Guided view with collapsible exceptions | SS-06 |
| SS-MOD-004 | P0 | N | Insert on any route with inherited normal destination | SS-03/06 |
| SS-MOD-005 | P0 | P | Inline question edit exists (creates a new question revision; published untouched) | SS-06 |
| SS-MOD-006 | P0 | N | Route picker | SS-06 |
| SS-MOD-007 | P0 | N | Merges (several edges into one node) | SS-03 |
| SS-MOD-008 | P0 | N | Expand/collapse with summary | SS-06 |
| SS-MOD-009 | P0 | N | Decision nodes | SS-03 |
| SS-MOD-010 | P0 | P | Delete and move exist with confirmation. Missing: route-aware impact, duplicate, undo/redo | SS-03/06 |
| SS-MOD-011 | P0 | N | Outcome catalog (termination reasons exist and map onto it) | SS-03 |
| SS-MOD-012 | P0 | P | Version-test simulation of a draft exists; module-only simulation is new | SS-04 |
| SS-MOD-013/014 | P1 | N / P | Subflows; per-question skip (today `branch_condition`) | later |

### B.3 Questions and answers (SS-QUE)

| ID | Pri | Status | Existing basis / what is missing | Phase |
|---|---|---|---|---|
| SS-QUE-001 | P0 | P | Question bank, stable `question_code`, revisions, category. Missing: tags, owner, usage view | SS-05 |
| SS-QUE-002 | P0 | P | YES_NO exists with `answer_state` YES/NO. Missing: routing | SS-03 |
| SS-QUE-003 | P0 | P | ENUM exists as a label list. Missing: stable option codes, per-option routes | SS-03 |
| SS-QUE-004 | P0 | N | Multi-select and its three modes | SS-03/04 |
| SS-QUE-005 | P0 | P | FREE_TEXT exists. Missing: length rules, routing | SS-03 |
| SS-QUE-006 | P0 | N | "All answers → next" as a real default edge | SS-03 |
| SS-QUE-007 | P0 | N | Per-option routes | SS-03 |
| SS-QUE-008 | P0 | P | `mandatory`, `not_applicable_predicate`, answer states UNKNOWN/UNCLEAR/REFUSED/NOT_ASKED/NOT_APPLICABLE exist | SS-03 |
| SS-QUE-009 | P0 | P | Intent, wording, controls exist. Missing: help text, internal notes, response guidance, field-level access | SS-03 |
| SS-QUE-010 | P0 | N | Impact report before option changes | SS-08 |
| SS-QUE-011 | P0 | P | Typed validation exists per answer type; option codes new | SS-03 |
| SS-QUE-012 | P0 | P | `answer_observation` (immutable, typed value, verbatim, provenance, supersedes) exists | SS-09 |
| SS-QUE-013/014/015 | P1 | P / N | NUMERIC exists; date/scale/file, languages, previews | later |
| SS-QUE-016…018 | P0 | N | `Other — please specify` | SS-03 |
| SS-QUE-019/020 | P0 | N | Sequential follow-ups and queue controls | SS-03/04 |
| SS-QUE-021 | P0 | N | Exclusive options, min/max | SS-03 |
| SS-QUE-022 | P0 | N | Routing preview | SS-04/06 |
| SS-QUE-023 | P0 | P | Split already matches: `question_revision` owns content, `module_question` owns placement | SS-03 |
| SS-QUE-024 | P0 | N | Queue skip / not-applicable / stop policies | SS-04 |
| SS-QUE-025 | P0 | P | `answer_observation.typed_value` (JSONB) can carry codes and Other text | SS-09 |

### B.4 Conditions and field catalog (SS-RUL)

| ID | Pri | Status | Existing basis / what is missing | Phase |
|---|---|---|---|---|
| SS-RUL-001 | P0 | N | Reusable condition entity | SS-03 |
| SS-RUL-002 | P0 | N | AND/OR/NOT nesting (today AND only, no nesting) | SS-03 |
| SS-RUL-003 | P0 | P | Allow-listed facts exist in two places (`CONDITION_FACTS`, `rule_inputs`). Missing: one governed typed catalog incl. prior answers | SS-03 |
| SS-RUL-004 | P0 | P | Equality and set membership exist. Missing: numeric, date, unit/currency checks | SS-03 |
| SS-RUL-005 | P0 | P | Same condition shape is already used for section, question and not-applicable bindings | SS-03 |
| SS-RUL-006 | P0 | N | Parameters and bindings | SS-03 |
| SS-RUL-007 | P0 | P | PASS/FAIL/UNKNOWN exists in `rule_engine` (assignment). Script conditions treat missing as false — must change for new versions only | SS-03 |
| SS-RUL-008 | P0 | P | Priority, computed specificity, ambiguity detection exist for assignment rules; pattern reusable | SS-03 |
| SS-RUL-009 | P0 | P | Rule trace and explain exist for assignment rules (`/assignment-rules/explain`) | SS-03/06 |
| SS-RUL-010/011 | P0 | N | Prior-answer operands; availability validation | SS-03 |
| SS-RUL-012 | P0 | N | Version pinning and upgrade for conditions | SS-08 |
| SS-RUL-013 | P0 | N | Select / create / duplicate | SS-06 |
| SS-RUL-014/015/016 | P1 | P / N | Plain-language summaries exist (`describeCondition`); templates, date maths, contradiction warnings | later (summaries are needed in P0 for SS-UXE-015) |

### B.5 Routing (SS-ROU)

| ID | Pri | Status | Existing basis / what is missing | Phase |
|---|---|---|---|---|
| SS-ROU-001…007 | P0 | N | Typed graph, single next step, explicit default, merges, exits, safe insertion, structured BLOCKED. The controller's rule "one current action at a time" already holds | SS-03/04 |
| SS-ROU-008 | P0 | N | Cycle rejection + traversal cap | SS-03/04 |
| SS-ROU-009 | P0 | P | No back/edit in the controller; `answer_observation.supersedes_id` exists | SS-04 |
| SS-ROU-010 | P0 | P | Controller events and the assignment rule trace are the pattern; decision trace per step is new | SS-04 |
| SS-ROU-011 | P1 | N | Bounded loops | later |
| SS-ROU-012 | P1 | **E** | Survey-wide events already exist (`lifecycle.EVENTS`, `report(event)` terminates with a reason) | — |
| SS-ROU-013…015 | P0 | N | Queue cursor, queue behaviour, queue validation | SS-03/04 |

### B.6 UI (SS-UX and SS-UXE)

All 13 P0 SS-UX and 30 P0 SS-UXE requirements are **N** from a UI standpoint, with these reusable pieces:
immediate server save with `expected_row_version` (basis for SS-UX-010 / SS-UXE-021, but there is no conflict UI and no
undo), inline validation issues from the server (SS-UX-009), confirm-on-remove (SS-UX-011), axe and three-width layout
checks (SS-UX-012/013, SS-UXE-024), semantic diff panel (SS-UX-015 P1), `describeCondition` (SS-UX-004, SS-UXE-015).
Phases SS-02 (prototype), SS-05, SS-06, SS-07, SS-08, SS-10. **SS-UXE-030 and UX-GATE-01…07 and 12 need moderated
sessions with real people and recorded sign-off; they cannot be evidenced by automated tests alone** (see Part 3 §L).

### B.7 Simulator (SS-SIM)

| ID | Pri | Status | Existing basis / what is missing | Phase |
|---|---|---|---|---|
| SS-SIM-001 | P0 | P | VERSION_TEST simulates any draft or published version from a content snapshot; module-only is new | SS-04 |
| SS-SIM-002/003 | P0 | P | Scenario facts are hand-entered and limited to ~7 fields. Missing: reusable typed profiles over the full catalog | SS-04/07 |
| SS-SIM-004 | P0 | P | Interactive step-by-step exists for current answer types | SS-04/07 |
| SS-SIM-005 | P0 | P | Lifecycle and plan explanations exist; per-decision explanation new | SS-04/07 |
| SS-SIM-006 | P0 | N | Back, restart, fork | SS-04 |
| SS-SIM-007 | P0 | **E** | Scenario library with expectations, regression runs, plain-language first divergence | — (extend expectations with modules/outcomes) |
| SS-SIM-008 | P0 | N | Path highlight on the graph | SS-07 |
| SS-SIM-009 | P0 | P | Coverage exists per question, module and lifecycle path; route/choice coverage new | SS-04/07 |
| SS-SIM-010 | P0 | N | UNKNOWN simulation | SS-04 |
| SS-SIM-011 | P1 | **E** | Batch runs (≤ 50 scenarios) with A/B comparison already exist | — |
| SS-SIM-012/013/014 | P1 | N / P | Boundary generation; side-by-side compare (story 09 needs a P0 form of it); upgrade regression | later / SS-07 |

### B.8 Validation and publication (SS-VAL)

| ID | Pri | Status | Existing basis / what is missing | Phase |
|---|---|---|---|---|
| SS-VAL-001 | P0 | P | `normalise_question`, `check_condition`, typed validation exist | SS-03 |
| SS-VAL-002…004 | P0 | N | Reachability, cycles, ambiguity, dependency/UNKNOWN checks | SS-03 |
| SS-VAL-005 | P0 | P | DB guard: publish requires every module published | SS-08 |
| SS-VAL-006 | P0 | P | ERROR/WARNING severities with codes exist; INFO and navigation targets new | SS-03 |
| SS-VAL-007 | P0 | **E** | Server validation gates submit; UI cannot bypass | — |
| SS-VAL-008 | P0 | P | Submit freezes manifest + SHA-256; checker re-check on approve and publish. Missing: regression results in the candidate | SS-08 |
| SS-VAL-009 | P0 | **E** | Maker ≠ checker in service and DB; changed candidate returns to draft | — |
| SS-VAL-010 | P0 | P | Manifest pins module revisions and question revisions; conditions and option sets to add | SS-08 |
| SS-VAL-011 | P0 | P | `rules_targeting`, `cases_assigned`, control usage exist; asset consumer graph new | SS-08 |
| SS-VAL-012 | P0 | **E** | Published versions never change; a new draft starts from published | — |
| SS-VAL-013/014 | P1 | P | SCHEDULED status exists in the enum, unused | later |

### B.9 Runtime (SS-RUN)

| ID | Pri | Status | Existing basis / what is missing | Phase |
|---|---|---|---|---|
| SS-RUN-001 | P0 | P | Plan, manifest SHA, fact snapshot and risk assessment are pinned at simulation start; `survey_run` has the columns | SS-09 |
| SS-RUN-002 | P0 | **E** | The backend decides every next action; stale or wrong action ids are rejected | — |
| SS-RUN-003 | P0 | P | Ordered events exist for simulations; operational tables have no live writer | SS-09 |
| SS-RUN-004 | P0 | P | Idempotent action ids, row lock + replay; pause/resume new (`PAUSED` exists in the `survey_run` enum) | SS-04/09 |
| SS-RUN-005 | P0 | P | Case → attempt → session → `survey_run` → `question_execution` → `answer_observation` → `rule_evaluation` FKs exist | SS-09 |
| SS-RUN-006 | P0 | **E** | Controller is pure and has no LLM; Voice Lab is explicitly decoupled; delivery modes exist | — |
| SS-RUN-007 | P0 | **E** | Hash-chained audit and change events | — (extend action names) |
| SS-RUN-008 | P0 | P | Permission checks and market scope on every route; runtime service identity is new | SS-09 |
| SS-RUN-009 | P0 | **E** | Outcomes COMPLETED / INCOMPLETE / TERMINATED / ABANDONED with reasons | — (map to outcome catalog) |
| SS-RUN-010 | P0 | P | `answer_observation` immutable with `supersedes_id` | SS-09 |
| SS-RUN-011/012 | P1 | P | — | later |

### B.10 Non-functional (SS-NFR)

| ID | Pri | Status | Note |
|---|---|---|---|
| SS-NFR-001, 002, 003 | P0 | N | Editor responsiveness, scale (50 modules, 1,000 nodes), simulator latency: no baseline measured yet; needs fixtures and measurements (SS-10) |
| SS-NFR-004 | P0 | P | Immediate save exists; idle autosave with visible state is new |
| SS-NFR-005 | P0 | P | `expected_row_version` → 409 `STALE_DRAFT`; conflict resolution UI new |
| SS-NFR-006 | P0 | P | Row lock + replay; idempotency keys on apply/assign routes |
| SS-NFR-007 | P0 | **E** | Existing auth, RBAC, maker-checker, audit |
| SS-NFR-008 | P0 | P | Synthetic-only data today; masking rules for previews new |
| SS-NFR-009 | P0 | P | axe checks in place; keyboard alternatives for drag and graph ports new |
| SS-NFR-010 | P0 | **E** | Immutability triggers, FKs, hashes (extend to new tables) |
| SS-NFR-011 | P0 | P | Correlation ids and audit exist; per-transition reasons new |
| SS-NFR-012 | P0 | P | 511 backend, 119 unit, 33 Playwright tests; property-based and round-trip tests new |
| SS-NFR-013 | P0 | P | Chromium only today; Edge smoke new |
| SS-NFR-014 | P0 | P | Linear Alembic chain with downgrade; feature toggle new |
| SS-NFR-018 | P0 | P | Length caps exist; AST depth, node and traversal caps new |
| SS-NFR-015/016/017 | P1 | — | later |

### B.11 Totals (P0 only)

| Group | P0 | E | P | N |
|---|---:|---:|---:|---:|
| SS-SUR | 11 | 0 | 6 | 5 |
| SS-MOD | 12 | 0 | 4 | 8 |
| SS-QUE | 22 | 0 | 10 | 12 |
| SS-RUL | 13 | 0 | 6 | 7 |
| SS-ROU | 13 | 0 | 2 | 11 |
| SS-UX | 13 | 0 | 5 | 8 |
| SS-UXE | 30 | 0 | 3 | 27 |
| SS-SIM | 10 | 1 | 6 | 3 |
| SS-VAL | 12 | 3 | 6 | 3 |
| SS-RUN | 10 | 4 | 6 | 0 |
| SS-NFR | 15 | 2 | 10 | 3 |
| **Total** | **161** | **10** | **64** | **87** |

Reading: governance, publication and runtime authority are largely in place (the "P" items there are extensions); the
graph, the richer answer model, the condition engine and almost the whole authoring UI are new.

---

## C. Reusable unchanged

These are kept as they are. Survey Studio integrates with them; it does not replace or rewrite them.

| Area | What | Why it can stay |
|---|---|---|
| Identity, RBAC, CSRF, rate limiting, market scope | `app/security/*`, `require(permission)`, `ENABLED_MARKETS={"SG"}` | New routes use the same guards |
| Audit | `app/audit/chain.py` hash chain; `script_change_event` | New actions are new event names |
| Canonical hashing | `app/domain/digest.py` `sha256_of` (canonical JSON) | Same function hashes the new manifest |
| DB immutability helpers | `forbid_change_trigger`, guard triggers, `operational()` `row_version` | Applied to the new tables |
| Assignment rules and assignment engine | `rule_engine`, `rule_authoring`, `script_assignment`, their APIs and screens | They select **which version** a case gets; that question is unchanged. Pins stay `script_version_id` + manifest SHA |
| Answer evaluation | `answer_evaluation.py` (8 methods) | Consumes question content + per-question status/answer, keyed by `question_code` — the new runtime will present the same shape (contract below) |
| Finding rules and engine | `finding_rules`, `finding_engine` | Consume evaluation results + controls |
| Review Workbench | `review`, `review_dossier` and screens | Read `survey_run`, `question_execution`, `answer_observation`, `rule_evaluation` |
| Conversation lifecycle | `lifecycle.py` stages, roles, gates, events, termination reasons | Kept as cross-cutting rules above the graph (SS-D-08) |
| Scenario library and batches | `simulation_workbench`, `scenario_runner.compare`, first-divergence, A/B | Extended with new expectation kinds, not replaced |
| Voice Lab and GPT-Live | `app/voice/*` | No dependency on the controller; only `import_from_script` reads question rows (read-only, unaffected) |
| Question bank read API, controls, regulatory references | `/question-bank`, `/controls`, `/regulatory-references` | Become library sources |
| Test harness | pytest suite, vitest, Playwright on the real backend, axe, layout checks | Regression gate for every phase |

**The contract the new runtime must keep** (so evaluation, findings and review need no change):
1. A frozen content document with `sections[].questions[]`, each carrying `question_code`, `question_revision_id`,
   `revision`, `answer_type`, `answer_schema`, `expected_answer_policy`, `expected_value`, `policy_fact_key`,
   `mandatory`, lifecycle fields and `controls[]`.
2. A per-question view after the run: `applicable`, `skip_reason`, `status`, `answer {answer_kind, answer_state,
   value, verbatim}`.
3. Operational rows in `survey_run`, `question_execution`, `answer_observation`, `rule_evaluation` with their current
   meanings.
4. One execution per `question_code` per run (until SS-D-09 is revisited).

A question the route never reaches is reported as not applicable with a new skip reason (`ROUTE_NOT_TAKEN`), which the
evaluation already treats as "not applicable".

---

## D. Extend, replace or retire

### D.1 Extend (additive; existing behaviour for existing data unchanged)

| Component | Extension |
|---|---|
| `script_family`, `script_version`, `script_section`, `script_module`, `module_question`, `question_revision` | Graph and answer-model columns and sibling tables (Part 2 §F). Published rows are never rewritten |
| Manifest | New schema `call360.script-manifest/3` for graph versions; `/2` stays valid and executable |
| `question_controller` | Navigation generalised from "next pending in order" to "follow the compiled graph"; adds queue, back/edit, pause/resume, decision trace. Linear plans keep running through the same class (Part 2 §G) |
| `script_authoring` validation and diff | New graph, queue, dependency and ambiguity checks; diff over routes, rules and options |
| Simulation run, scenario, coverage | Profiles over the field catalog; module-only runs; route and choice coverage; back/fork |
| Answer types | `SINGLE_SELECT` (ENUM becomes its label-only legacy form), `MULTI_SELECT`, option rows with stable codes, `Other`, exclusivity |
| Permissions | Reuse the six `script.*` permissions; any new role is a decision (SS-D-11) |
| Frontend shared pieces | `Field`, `ErrorBox`, `errorText`, badges, cards, `describeCondition` |

### D.2 Replace (new implementation supersedes an old one, with coexistence)

| Old | New | Coexistence |
|---|---|---|
| Script conditions: three shapes, AND only, false on missing (`outcomes.condition_holds`, `check_condition`) | One typed condition engine (AST, tri-state, parameters) | Old shapes are read as a subset of the new AST for new graph versions; `/2` manifests keep the old evaluator bit-for-bit |
| Two unrelated frontend condition editors (`ConditionEditor` in `ScriptEditor.tsx`, `ConditionRow` in `RuleBuilder.tsx`) | One condition drawer | Assignment Rules keeps its editor until the owner asks to converge (not in scope) |
| Script Studio editor (`ScriptEditor.tsx` draft editor) as the place to author questions and order | Survey Studio composer + guided builder | Script Studio stays for linear versions and becomes the wording-and-delivery surface (SS-D-02) |
| Hand-entered scenario facts | Reusable synthetic profiles | Existing scenarios stay valid |

### D.3 Retire (only after acceptance of the replacing phase, never by deleting data)

| Item | When |
|---|---|
| Creating **new** linear drafts in the old editor | After SS-08 is accepted and the owner confirms. Existing linear versions stay readable, executable and pinned forever |
| Old draft editor code paths | After SS-10, by owner decision |
| Nothing else | No table, row, published version, evaluation, finding, recording, transcript or audit record is deleted or rewritten at any phase |

### D.4 Not touched at all

Voice Lab, GPT-Live adapters, Azure configuration, spend safeguards, Voice Studio, intake, policy/risk workbenches,
administration, search, Finding Rules, Review Workbench, Assignment Rules.
