# UC-01 — Capability-level consolidation map

**Checkpoint:** UC-01 (Unified Survey Studio Foundation), authorised by the owner on 2026-11-21 ("G-6 Architectural
Direction Approved: Unified Survey Studio").
**Status:** the map is a **proposal for review**, built on the owner's decisions AD-1, AD-2 and AD-15 (decision
register D-155…D-159). **Nothing in it has been executed: no Script Studio code, API, table or row was changed or
removed.** It replaces the feature-parity matrix and the removal sequence of `20_…` §2 and §5, which were written
before the owner's direction and preserved too much.

**The governing rule (owner, 2026-11-21):** *Do not preserve an existing module merely because other modules
currently depend on it. Preserve necessary business functionality, replace obsolete dependencies, and remove
redundant implementations.*

So every row below starts from the **business capability**, not from the code that holds it today, and every
disposition is justified by implementation complexity, data dependencies, rollback and long-term maintainability.
A current import is listed as a fact to deal with, never as a reason to keep something.

Dispositions: **REUSE** a genuinely useful primitive as it is · **REFACTOR** into the new survey implementation ·
**REPLACE** with a simpler design · **DELETE** once the dependent functionality has moved.

---

## 1. What the end state is

| | Today | End state |
|---|---|---|
| Authoring products | Script Studio (operational) and Survey Studio (prototype) | **Survey Studio** |
| Navigation entries under Governance | Script Studio · Assignment Rules · Simulation Workbench · Finding Rules · Review Workbench (+ Survey Studio when enabled) | **Survey Studio · Review Workbench** |
| Definition stores | The script tables | **One** survey definition store |
| Question models | 2 | 1 item master (questions and statements) |
| Condition languages | 3 | 1 |
| Publication implementations | 3 on the server, 1 simulated | 1 |
| Execution engines | Server controller (linear) and browser engine (graph) | **One deterministic execution harness** on the server |
| Content read by every engine | Manifest plus live table joins | One frozen content document |

---

## 2. Design-time and operational responsibilities, by business workflow

The owner asked that Assignment Rules, Simulation Workbench, Finding Rules and Review Workbench not be assumed to stay
separate products. Each is assessed by **who does the work, when, and on what**.

| Business workflow | Who · when | Today | Proposed home | Why |
|---|---|---|---|---|
| Design a call journey: modules, questions, statements, routing, conditions, wording | Survey author · before publication | Script Studio; Survey Studio prototype | **Survey Studio** | The product's purpose |
| Decide **which kind of case gets which survey** (conditions, priority, fallback, effective dates) | Survey author and checker · when a version is published or retargeted | Assignment Rules — a separate screen, a second condition editor, a second publication process | **Survey Studio** — an "Assignment" area of a survey, plus one library view of precedence and conflicts across surveys | It is design-time configuration made by the same people at the same moment. It needs the same condition builder and the same approval. A separate product makes an author publish in two places to put one survey into use |
| **Apply** an assignment to a case; preview "why this survey"; batch-assign unassigned cases | Operations user · per case | Buttons on the Assignment Rules screen; a panel on Call Detail | **Case operations** (Call Detail, Work Queues) — not Survey Studio | It acts on live cases and places or releases holds. It is operational, with its own permission (`script.assign`) |
| Try a journey step by step | Author · while designing | Simulation Workbench (server, linear) and Survey Studio simulator (browser, graph) | **Survey Studio → Simulate** | One simulator, on the one harness |
| Keep regression scenarios; run them in batches; compare two versions | Author and checker · before approval | Simulation Workbench | **Survey Studio → Simulate** (saved scenarios, batch runs) | The results belong in the candidate the checker approves. Today they sit in another product |
| Preview what a customer-specific call would contain | Author, checker · before approval | Does not exist | **Survey Studio → Simulate → Call plan preview** (built in UC-01) | |
| Configure how an answer is evaluated and which controls a question evidences | Author, with Compliance · per question | Fields in the Script Studio question form | **Survey Studio**, on the question card | It is part of the question's definition and is approved with it |
| Maintain the library of controls and regulatory references | Compliance · occasionally | Read-only list in Script Studio | **Survey Studio → Library** | A library the questions link to |
| Decide which evaluation outcomes become findings, and their severity | Compliance · per market | Finding Rules — a separate screen and a third publication process | **Survey Studio → Library → "Findings policy"**, with its own permission. **Decision UC-D-10** | Design-time configuration that refers to questions and controls. It is a market-wide policy, not part of one survey, so it stays its **own governed artefact** — but it does not need its own product or its own publication code |
| Evaluate answers, raise findings | System · after a call | Engines | **Backend engines** — unchanged responsibility | Runtime |
| Review a case: dispositions, decisions, approvals | Reviewer and checker · after a call | Review Workbench | **Review Workbench — stays a separate product** | It is operational case work on evidence, by different people, under different permissions. Nothing about it is authoring |
| Execute a call | System · during a call | Controller (simulation only today) | **Backend execution harness** | Runtime (SS-D-17: last) |
| Enforce maker-checker, immutability, permissions, audit | System · always | Services, database constraints and triggers | **Backend** — one publication service, same strength | The owner's condition: controls keep their strength when their implementation moves |

**Result for navigation.** Four entries and six routes disappear (Script Studio, Assignment Rules, Simulation
Workbench, Finding Rules). Survey Studio gains no new top-level product: assignment, saved scenarios, the call plan and
the findings policy are areas of screens it already has.

---

## 3. Capability map: current implementation, consumers, replacement interface

### 3.1 Authoring capabilities

| Capability | Current implementation | Current consumers | Replacement interface | Disposition | Justification |
|---|---|---|---|---|---|
| Survey, modules, placement, order | `script_family`, `script_version`, `script_section`, `script_module`, `module_question`; `script_authoring.py`; 20 authoring operations; `ScriptEditor.tsx` | Editor only. Everything else reads the frozen content | Survey Studio operations on a draft; module graph as one validated document (AD-3) | **REPLACE** | The row model is linear: position columns, one question per row, no node that is not a question. Bending it to a graph needs more new tables than replacing it. With re-seeding approved (AD-2) nothing depends on these rows |
| Question identity and version | `question_bank_item`, `question_revision` (insert-only), `question_revision_detail` | Editor; `question_execution` (foreign key); manifest | **Item** (identity) → **Item Version** (structure) → **Wording Version** | **REPLACE**, reusing the insert-only trigger pattern | Structure and wording are fused; choices are labels without codes; uniqueness includes language; a side table holds half the fields. The insert-only idea is right and is kept |
| Statements (opening, disclosure, transition, closing) | Acknowledgement questions with a lifecycle role | Controller, review readiness checks | **Statement node** placing an item of kind STATEMENT (built in UC-01) | **REPLACE** | A statement modelled as a question needs an answer type it does not have |
| Answer types | Five, in a CHECK constraint | Controller, evaluation | Seven item kinds: yes/no, single choice, multiple choice, free text, **number**, **acknowledgement**, **statement** (built in UC-01) | **REFACTOR** | Existing five map directly; `ENUM` becomes single choice with codes |
| Approved wording, version history | `customer_wording` on the revision; change events | Controller (delivers it), Call Detail, review, Voice Lab import | **Wording Version** pinned by the item placement; shown and edited on the card (built in UC-01, in memory) | **REPLACE** | See question identity |
| Delivery mode and exact-wording control | `delivery_mode` on the revision; controller derives `verbatim_required` | Controller | `delivery` on the Wording Version (built in UC-01). Rule retained: exact modes deliver only the approved text | **REFACTOR** | Semantics are right; only the home changes |
| Controlled variables | **Does not exist** | — | `{{field}}` slots bound to the field catalog; deterministic rendering; missing value is an error (built in UC-01) | **NEW** | |
| Clarification and repeat wording | **Does not exist** (only `max_reprompts`) | Controller repeats the same wording | Approved conversation phrases on the survey | **NEW — BLOCKED** | Needs D-NA-8 and the repeat parameters. Shown as unavailable in UC-01 |
| Mandatory question | `mandatory` on the revision | Outcomes, KPIs, review readiness, finding rules | `mandatory` on the Item Version (declared in UC-01) | **REFACTOR** | Its meaning when unanswered is D-NA-5 / D-NA-10 |
| Lifecycle roles and gates | `lifecycle_role`, `on_failure` on the detail row; rules in `lifecycle.py`; enforced in the controller | Controller, review, `live_eligibility` | Role on the item (declared in UC-01); gate rules stay in the harness | **REFACTOR**; gate behaviour **BLOCKED** | The on-failure rules are development assumptions. UC-01 declares roles and reports live eligibility; it implements no gate behaviour |
| Static inclusion and applicability predicates | Three JSON shapes, AND only; `outcomes.condition_holds`, `script_authoring.check_condition` | Controller plan build; KPIs | Typed conditions (eligibility, decisions) | **DELETE** after re-seed | Strictly weaker than the condition engine. With no legacy versions to execute, no adapter is needed |
| Evaluation configuration | Columns on the revision; 8 methods | `answer_evaluation.py` | `EvaluationConfig` on the Item Version — interface contract prepared in UC-01 (`contract.ts`), not authorable yet | **REFACTOR** | Methods kept; choices matched by code instead of label |
| Control and regulatory mapping | `control`, `regulatory_reference`; `control_mapping` (legacy); `script_version_control_link` | Finding engine, `controls_satisfied`, KPIs | `ControlLink` on the Item Version — contract prepared in UC-01 | `control`, `regulatory_reference`: **REUSE**. `control_mapping`: **DELETE**. Version link: **REFACTOR** | The two libraries are clean, independent primitives. `control_mapping` is a seeded concept-level leftover that authoring stopped using at migration 0016 |
| Validation | `script_authoring.validate` (7 errors, 9 warnings) | Submit gate | Server validator specified by the prototype's rules and the fixtures | **REPLACE** | The existing checks are for a linear model |
| Version comparison | `script_authoring.diff` | Review tab | Comparison by item identity | **REPLACE** | Same reason |
| Draft, submit, review, publish | One `script_version` row changing status; guard trigger with a status machine; maker-checker in service and CHECK | Editor; every pin | **Draft → immutable Candidate → Version** (D-143), separate Publisher (D-144) | **REPLACE**, reusing the maker-checker CHECK pattern, the hash function and the audit chain | A row that is a draft, then a candidate, then a version cannot give immutable candidates. Three insert-only entities need no status-machine trigger at all — simpler and stronger |
| Change history | `script_change_event` | History tab; source of "makers" | One definition-event log for surveys, modules, items and policies | **REFACTOR** | Three near-identical event tables exist today |
| Assignment rule authoring | `assignment_rule_draft`, `script_assignment_rule_version`, `assignment_rule_publication`, `assignment_rule_change_event`; `rule_authoring.py` (1,100 lines); 15 operations; `features/rules/` | Assignment engine | Assignment area in Survey Studio; rule conditions in the **one** condition language; published through the **one** publication service | Tables: **REFACTOR**. `rule_authoring.py` publication logic: **REPLACE**. Screens: **DELETE** | The rule model is sound and already uses draft → version. Its own publication code and its own condition editor are the duplication |
| Findings policy authoring | `finding_rule_set_version`, `finding_rule_set_event`; `finding_rules.py`; 9 operations; `features/findings/` | Finding engine | "Findings policy" in the Survey Studio library; published through the one publication service | Tables: **REUSE**. Publication logic: **REPLACE**. Screen: **DELETE** (UC-D-10) | Same pattern: good artefact, duplicated machinery |
| Scenario library, batches, A/B, coverage | `simulation_scenario*`, `simulation_batch`, `simulation_result`; `simulation_workbench.py`, `scenario_runner.py`; 14 operations; `features/simulator/` | Authors, checkers | Saved scenarios and batch runs in Survey Studio → Simulate | Tables: **REFACTOR** (steps keyed by execution key). Screens: **DELETE** | Regression value is real and must be kept; the separate product is not |
| Content snapshot for draft simulation | `simulation_content_snapshot` | Simulation, evaluation | Drafts and candidates are already content-addressed documents | **DELETE** | It exists only because the row model cannot hand a draft to the controller as a document |

### 3.2 Engines and operational capabilities

| Capability | Current implementation | Current consumers | Replacement interface | Disposition | Justification |
|---|---|---|---|---|---|
| Deterministic execution | `question_controller.py` — pure, event-sourced, linear | Simulation, scenario runner, review replay | **The one execution harness**: the same event-sourced core, navigation generalised to the graph, specified by the 19 fixtures | **REFACTOR** | The core (pure, event-sourced, idempotent action ids, gates) is a genuinely useful primitive. Its navigation is twenty lines of "next in order" |
| Browser simulation engine | `model/sim.ts` in the prototype | Prototype simulator and call plan | The harness, called from Survey Studio | **DELETE** when the harness exists | Until then it is the executable specification. Two engines is the duplication the owner wants gone |
| Call-plan assembly | **Does not exist** | — | Harness function: application data + version → plan document (design `20_…` §4; previewed in UC-01) | **NEW** | |
| Assignment decision | `rule_engine.py` (pure), `script_assignment.py`; `script_assignment`, `script_assignment_attempt` | Call Detail, voice session pin, policy views | Unchanged logic; target is a survey version; conditions evaluated by the one condition engine | **REUSE** (engine, ledger); condition evaluation **REFACTOR** | The pin (version id + manifest hash + input hash + trace) is exactly the right primitive |
| Answer evaluation | `answer_evaluation.py` (pure) | Simulation, review | Reads `EvaluationConfig` from the content document; choices by code | **REUSE** | Pure and already document-driven |
| Findings generation | `finding_engine.py` (pure) | Simulation, review | Reads `ControlLink` and results; keyed by execution key (D-115) | **REUSE** | Same |
| Simulation run records | `script_simulation_run`, `script_simulation_event`, `simulation_answer_evaluation`, `simulation_finding_set`, `simulation_finding` | Simulator | Same records, written by the harness | **REUSE** | Owner condition D-80 keeps simulation and operational records isolated, so they stay separate from the operational tables |
| Operational evidence | `conversation_session`, `survey_run`, `question_execution`, `answer_observation`, `rule_evaluation`, `finding`, `review_decision`, `review_approval` | Call Detail, review, KPIs | Same tables; `question_execution` points at an item version and carries the execution key and the delivery record | **REUSE** | Correct grain; no live writer exists yet |
| Case outcome and KPIs | `outcomes.py` reads `script_version.manifest` on every computation | Overview, Call Detail, policies | Content interface: `content_for(version)` | **REFACTOR** | A live read of another module's table is the kind of obsolete dependency to replace |
| Review | `review.py` rebuilds a plan through `script_authoring.content_of` | Review Workbench | Content interface + harness replay | **REFACTOR** the dependency; product stays | |
| Voice session pin | `voice/store.pins_for` | Voice Studio | Pin to a survey version; **enforce live eligibility** | **REFACTOR** | D-67 is computed and enforced nowhere today |
| Voice Lab import | `lab.import_from_script` copies wording | Voice Lab | Import from a survey version | **REFACTOR** (small) | A copy, not a dependency |
| Audit | `audit_event` hash chain; `write_audit` | Everything | Unchanged | **REUSE** | |
| Canonical hashing, immutability helpers | `digest.sha256_of`; `forbid_change_trigger` | Everything | Unchanged | **REUSE** | |

---

## 4. Replacement interfaces

Four interfaces replace every dependency on Script Studio's tables and services.

**4.1 Content interface.** `content_for(version) → content document`: one frozen, hashed document per published
version, candidate or draft. Per placed item it carries `execution_key`, `question_code`, `version`,
`wording_version`, `item_type`, `answer_type`, `options` (codes and labels), `number_rule`, `customer_wording`,
`variables`, `delivery_mode`, `verbatim_required`, `mandatory`, `lifecycle_role`, `evaluation`, `controls`.
The prototype produces this projection from the canonical model (`model/contract.ts`, `toContent`) and lists what
today's engines could not read (`legacyGaps`). **Consumers:** harness, evaluation, findings, review, KPIs, Call
Detail, Voice Lab import. **Replaces:** `script_authoring.content_of`, `build_manifest`, `link_rows`,
`lifecycle_of`; every live join to `question_revision`; every read of `script_version.manifest`.

**4.2 Publication interface.** `submit(draft) → candidate`, `decide(candidate)`, `publish(candidate) → version`,
`history(artefact)`, for any governed artefact (survey, module, findings policy, assignment rule). **Replaces:**
the publication halves of `script_authoring.py`, `rule_authoring.py` and `finding_rules.py`, and three event tables.

**4.3 Condition interface.** `evaluate(condition, bindings, facts, answers) → TRUE | FALSE | UNKNOWN + explanation`.
**Consumers:** module eligibility, decisions, assignment rules. **Replaces:** `outcomes.condition_holds`,
`script_authoring.check_condition`, the assignment predicate evaluator, and two frontend condition editors.

**4.4 Execution interface.** `plan(version, application data) → call plan`; `start`, `act`, `state` for a run.
**Consumers:** Survey Studio simulate, scenario runner, review replay, later the runtime. **Replaces:** the
controller's public surface, `script_simulation.py`'s content loading, and the browser engine.

**Evaluation and control contracts prepared in UC-01** (types only; the engines are not replaced):

```text
EvaluationConfig { method, expected_boolean?, operator?, value?, policy_fact_key?, unit?, tolerance?,
                   tolerance_reference?, accepted_options? }         // accepted_options are option CODES
ControlLink      { control_code, regulatory_reference?, rationale }
methods allowed  yes/no → EXACT_BOOLEAN | COLLECT_ONLY        acknowledgement → ACKNOWLEDGEMENT | COLLECT_ONLY
                 number → NUMERIC_COMPARE | NUMERIC_MATCH_POLICY_FACT | COLLECT_ONLY
                 single choice → ENUM_MATCH | ENUM_MATCH_POLICY_FACT | COLLECT_ONLY
                 multiple choice → COLLECT_ONLY               free text → NARRATIVE_REVIEW | COLLECT_ONLY
                 statement → never evaluated
```

---

## 5. Capability retirement matrix (updated)

Status after UC-01. "In Survey Studio" means in the prototype, in memory, behind the setting.

| Script Studio capability | In Survey Studio after UC-01? | Retirement blocker |
|---|---|---|
| Create a script; modules; reorder; reuse | Yes | Backend |
| Yes/no, choice, free text questions | Yes | Backend |
| Numeric question | **Yes — UC-01** | Backend |
| Acknowledgement | **Yes — UC-01** | Backend |
| Opening, disclosure and closing statements | **Yes — UC-01**, as Statement nodes, plus Transition | Backend; confirm the role list (UC-D-4) |
| Exact customer wording | Yes | Backend; "what is approved wording" (G-4) |
| Wording version shown on the card | **Yes — UC-01** | History view needs the backend |
| Delivery mode | **Yes — UC-01** (default and conversational mode: UC-D-1, UC-D-2) | Backend; audio asset attachment |
| Mandatory flag | **Declared — UC-01** | D-NA-5, D-NA-10 |
| Lifecycle role | **Declared — UC-01**; live eligibility reported | Gate behaviour (UC-D-5) |
| On-failure behaviour; "discloses policy information"; "deliver on termination" | **No** | UC-D-5; identity-before-disclosure rule |
| Maximum re-prompts | **No — blocked** | `NA-P-…` values, D-NA-8 |
| Evaluation method and rule | **Contract only — UC-01** | Backend; UC-D-8 |
| Control and regulatory links | **Contract only — UC-01** | Backend |
| Acceptable variants, unacceptable outcomes, evidence required | No | Confirm they have a consumer (UNVERIFIED in G-6) |
| Escalation rule reference | No — proposed for deletion | Confirm no consumer |
| Section inclusion, "ask only when", "not applicable when" | Superseded by conditions | — |
| Validate, submit, review, publish, abandon | Simulated, stronger model | Backend; Publisher rule (G-4) |
| Compare versions; change history | Yes (in memory) | Backend |
| Library filters and search | No | Backend |
| Assignment rules | **No** | UC-D-9; backend |
| Interactive simulation | Yes; statements, numbers and acknowledgements **added in UC-01** | Non-answers (G-3) |
| Scenario library and batch runs | No — synthetic customers only | Backend |
| Call plan preview | **Yes — UC-01** (new; Script Studio never had it) | — |
| Controlled variables | **Yes — UC-01** (new) | UC-D-3 |
| Clarification and repeat wording | **Blocked — shown as unavailable** | D-NA-8 |
| Findings policy | No | UC-D-10; backend |

**Script Studio cannot be retired yet.** The remaining blockers are the backend, the assignment area, and the
policy-dependent items listed in `22_…` §8.

---

## 6. Retirement sequence under the approved direction

The sequence in `20_…` §5.3 assumed legacy history was carried forward. With re-seeding approved in principle (AD-2)
it shortens. **Nothing here is authorised; the destructive step needs its own checkpoint.**

1. **Preconditions of AD-2, all before any destructive change:** read and inventory the actual development database;
   identify protected demonstration records and owner restrictions (`SG_LIFECYCLE_DEMO` v1.1 unpublished regression
   draft, `SG_EVALUATION_DEMO` v1.0 unpublished testing draft, rule `S2D1-LIFECYCLE-DEMO`); produce a verified
   backup; state exactly what a re-seed replaces. **Not done in UC-01 — no database was read or touched.**
2. Build the definition store, the publication service, the condition engine and the harness beside the existing
   code (additive).
3. Port the seed and the tests to the new model; re-point evaluation, findings, review, KPIs, Call Detail, the voice
   pin and Voice Lab import to the four interfaces.
4. Move assignment, saved scenarios and the findings policy into Survey Studio.
5. Turn Survey Studio on by default after business-user UX acceptance (G-1) and screen-reader sign-off (G-2).
6. **Destructive checkpoint, separately approved:** re-seed; remove the Script Studio screens, routes, API, services
   and tables; remove the Assignment Rules, Simulation Workbench and Finding Rules screens.

**No legacy loader, no legacy evaluator and no conversion path are built.** That is the main saving from AD-2.

**Rollback.** Steps 2–5 are additive and reversible by code revert and a setting. Step 6 is reversible only from the
verified backup of step 1, which is why that backup and a rehearsed restore are preconditions, not afterthoughts.

**What must survive every step:** the accepted SS-02 specifications, the 19 fixtures and 63 expected runs, the
reference interpreters and the evidence folders. They live in the specs repository and no step touches them.

---

## 7. Data structures: one line each

| Structure | Disposition | Reason in one line |
|---|---|---|
| `script_family`, `script_version` | REPLACE | One row cannot be draft, immutable candidate and version |
| `script_section`, `script_module`, `module_question` | REPLACE | Linear rows; a graph needs a different shape |
| `question_bank_item`, `question_revision`, `question_revision_detail` | REPLACE | Wording fused with structure; labels without codes |
| `script_version_control_link` | REFACTOR | Becomes the item version's control links |
| `control_mapping` | DELETE | Legacy, unused by authoring since migration 0016 |
| `control`, `regulatory_reference` | REUSE | Clean independent libraries |
| `script_change_event`, `assignment_rule_change_event`, `finding_rule_set_event` | REFACTOR into one | Three copies of one idea |
| `assignment_rule_draft`, `script_assignment_rule_version`, `assignment_rule_publication` | REFACTOR | Sound model; target and conditions change |
| `script_assignment`, `script_assignment_attempt` | REUSE (renamed) | The right immutable pin and ledger |
| `simulation_scenario`, `simulation_scenario_revision`, `simulation_batch`, `simulation_result` | REFACTOR | Keep regression assets; key by execution key |
| `simulation_content_snapshot` | DELETE | Redundant once drafts are documents |
| `script_simulation_run`, `script_simulation_event`, `simulation_answer_evaluation`, `simulation_finding_set`, `simulation_finding` | REUSE | Isolation of simulation records is an owner condition |
| `finding_rule_set_version` | REUSE | Sound governed artefact |
| `conversation_session`, `survey_run`, `question_execution`, `answer_observation`, `rule_evaluation`, `finding`, `review_decision`, `review_approval` | REUSE | Correct evidence grain |
| `audit_event`, `case_event` | REUSE | Untouched |

Of the 39 script-related tables: **8 replaced, 2 deleted, 11 refactored (the three event tables into one), 18
reused.** None of the 18 reused tables is an authoring table.
