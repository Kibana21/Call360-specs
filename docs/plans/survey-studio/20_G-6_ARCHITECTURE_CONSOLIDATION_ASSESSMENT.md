# G-6 — Architecture consolidation assessment: retiring Script Studio into Survey Studio

**Checkpoint:** G-6 (analysis and specification only), authorised by the owner on 2026-11-21 ("Preserve SS-02
Baseline and Authorize G-6 Architecture Assessment").
**Status: REVIEWED BY THE OWNER 2026-11-21 — direction approved; see §10 for the decisions taken and what they
change in this document.** The body below is kept as presented. Where §10 differs, §10 governs. Original status:
PROPOSED — presented for the owner's review. **Nothing in this document is decided, authorised or
implemented.** No code, schema, API, migration or runtime was changed. Script Studio was not modified. SS-02 was not
reopened. SS-03 was not started. No paid call was made.
**Inspected at:** specs `786a7c0`, backend `7228875` (Alembic head `0026_gpt_live_provider`, OpenAPI
`221985e7…`), frontend `d1cdb03`. All three working trees clean.
**Method:** a read-only inventory of the actual backend and frontend code, plus the existing specifications and
rulings. Where a statement was not verified in code it is marked **UNVERIFIED** (list in §9).

---

## 0. Summary

### 0.1 What the inventory found

1. **"Script Studio" is three different things, and only one of them is redundant.**

   | Layer | What it is | Size today | Redundant once Survey Studio is real? |
   |---|---|---|---|
   | **A. The authoring product** | Script library, script page, form editor; the authoring API | 2 routes, about 1,490 lines of UI; 26 API operations; one 1,999-line service | **Yes — entirely** |
   | **B. The governed content store** | Families, versions, modules, sections, question bank, question revisions, frozen manifests with SHA-256, immutability triggers | 12 core tables | **No.** Every case pin, session pin, run, finding, review, KPI and audit record refers to it |
   | **C. The verification systems around it** | Assignment rules and engine, conversation controller and lifecycle gates, simulation workbench, answer evaluation, finding rules, review | About 71 API operations, 13 services, 27 tables | **No.** Survey Studio has none of these. They are not authoring |

2. **Survey Studio is far ahead on structure and behind on everything a real call needs.** It has routing, follow-up
   queues, conditions, a graph, undo and a better governance model. It has **no** delivery mode, statements, identity
   or consent gates, mandatory flag, expected-answer configuration, control mapping, numeric answers, assignment
   rules, persistence or real approval. Removing Script Studio before those exist would remove capabilities that
   evaluation, findings, review and live eligibility depend on.

3. **Three of the wording features the owner asked about exist in neither product.** Controlled variables in
   wording, clarification and repeat scripts, and multi-language wording are not implemented anywhere. They are new
   work, not migration.

4. **Every downstream consumer reads a frozen content document, not the authoring tables.** The controller,
   evaluation, findings and review all take the manifest-shaped document. That is what makes the consolidation
   tractable: keep that contract, and the authoring tables behind it can change.

5. **All data today is synthetic.** No real customer evidence exists. That makes one radical simplification possible
   that will not be possible later (§5.2, decision AD-2).

### 0.2 Recommendation in one paragraph

Retire layer A completely. Keep layer B's governed core but evolve it into the one Survey Studio definition store,
then rename it, so no "script" product, screen, API or table remains while every historical pin stays valid. Keep
layer C and re-point it at survey versions; it is not part of Script Studio. Add the missing wording and
call-readiness features to Survey Studio as fields and node roles on the existing screens — **no separate Wording
Studio**. Adopt one publication process (draft → immutable candidate → published version) for surveys.

### 0.3 An expectation to correct

**The end state will not be smaller than today in lines of code.** The Script Studio editor is 1,641 lines of
frontend; the Survey Studio prototype is 8,442, and its backend does not exist yet. What becomes smaller is the
number of *things*: one question model instead of two, one condition language instead of three, one execution engine
instead of two, one publication process instead of three. The honest comparison is against running both products,
which is where the project is otherwise heading.

### 0.4 Decisions this document asks for

Fifteen decisions, AD-1 to AD-15, listed in §8. The three that shape everything else:

- **AD-1** — what "remove Script Studio completely" means for the governed store (evolve and rename; or a parallel
  new store with a frozen archive; or a clean cut).
- **AD-2** — whether synthetic development history must be carried through the consolidation or may be re-seeded.
- **AD-15** — the stated amendments to SS-D-01, SS-D-02, SS-D-17 and SS-D-20 (§3.5).

---

## 1. Current architecture (deliverable A)

### 1.1 Features and screens

32 routes are always registered; a 33rd (`/survey-studio/*`, 7 nested routes) only when the prototype setting is on.

| Area | Routes | Frontend folder | Lines (non-test) | What it does |
|---|---|---|---:|---|
| **Script Studio** | `/scripts`, `/scripts/:scriptFamilyId` | `features/scripts/` | 1,487 ¹ | Library with server-side filters; script page with six tabs: Questions / Edit questions, Versions, Review & publish, Compare versions, Change history, Details |
| Assignment Rules | `/assignment-rules`, `/assignment-rules/:ruleCode` | `features/rules/` + one page in `features/scripts/` | 982 | Rule registry, builder, live explain, simulation, maker-checker, batch assignment |
| Simulation Workbench | `/simulator` | `features/simulator/` | 1,419 | Interactive text simulator on the server controller; scenario library; batch and A/B runs; answer evaluation; simulated findings |
| Finding Rules | `/finding-rules` | `features/findings/` | 212 | Versioned finding rule set with maker-checker |
| Review Workbench | `/reviews`, `/reviews/cases/:caseId` | `features/reviews/` | 633 | Findings queue, case dossier, decisions and approvals |
| **Survey Studio (prototype)** | `/survey-studio/*` | `features/surveystudio/` | 8,442 | In memory only; no API call anywhere in the folder |

¹ `features/scripts/` is 1,641 non-test lines including `AssignmentRulesPage.tsx` (154), which belongs to Assignment
Rules.

**What the Script Studio editor actually offers** (form fields present in `ScriptEditor.tsx`): exact customer
wording; intent; category; answer type; delivery mode; evaluation method with operator, expected value, unit,
tolerance and tolerance approval reference; accepted options; maximum re-prompts; lifecycle role; on-failure
behaviour; "discloses policy information"; "deliver on early termination"; mandatory; evidence required; acceptable
variants; unacceptable outcomes; "not applicable when"; "ask only when"; escalation rule reference; control and
regulatory-reference links; reason for change.

**What it does not offer** (verified absent in the UI and the API schema): variables or placeholders in wording;
separate clarification or repeat text; per-language wording; editing effective dates; a schedule, withdraw or retire
action; attaching an audio asset; drag-and-drop; any answer-driven routing; coded options; multi-select.

### 1.2 Question and wording model

Stored in `question_bank_item` (stable `question_code`, intent, category) → `question_revision` (insert-only) →
`question_revision_detail` (lifecycle fields, authored revisions only). Placement is `script_version` →
`script_section` → `script_module` → `module_question`.

| Aspect | As implemented |
|---|---|
| Wording | One text field per revision, `customer_wording`, 10–1,000 characters. **Structure and wording are fused in one immutable row** |
| Wording approval | `content_approval_status`: `SYNTHETIC_UNAPPROVED` or `APPROVED_BY_SC`. Every seeded and authored row is synthetic |
| Answer types | `YES_NO`, `NUMERIC`, `ENUM`, `FREE_TEXT`, `ACKNOWLEDGEMENT`. `ENUM` options are plain label strings with no stable codes |
| Opening and closing statements | **Not separate fields.** They are ordinary items with answer type `ACKNOWLEDGEMENT` and a lifecycle role (`OPENING_STATEMENT`, `DISCLOSURE`, `CLOSING_STATEMENT`). `deliver_on_termination` applies to closing statements |
| Clarification and repeat scripts | **Do not exist as content.** Only the integer `max_reprompts` (0–5). On a re-prompt the controller re-issues the same wording |
| Controlled variables | **Do not exist.** No interpolation, template or variable column or code. Policy facts are used only in conditions and expected-answer checks, never inserted into wording |
| Delivery constraints | `delivery_mode`: `CONVERSATIONAL`, `CONTROLLED_TTS`, `EXACT_AUDIO`. The controller derives `verbatim_required`. **No audio asset can be attached**; validation only warns (SCR-019) |
| Languages | Columns exist; `'en'` is hard-coded on every insert. A placement points at exactly one revision, so there is no multi-language mechanism |
| Routing | **None driven by answers.** Three static predicates (section inclusion, "ask only when", "not applicable when") in a small AND-only language over four policy facts and the risk band, evaluated once before the call |
| Evaluation configuration | Eight methods on the question revision; expected value; policy fact key; tolerance; variants |
| Controls | Version-scoped links (`script_version_control_link`), frozen into the manifest per question |

### 1.3 Approval and versioning

- **States:** `DRAFT`, `SUBMITTED_FOR_REVIEW`, `APPROVED`, `SCHEDULED`, `PUBLISHED`, `SUPERSEDED`, `WITHDRAWN`,
  `ABANDONED`. **`SCHEDULED` and `WITHDRAWN` are never set by any service**; future-dated publication and a withdraw
  action are required by SCR-013 and SCR-016 but are not implemented. Publishing always takes effect immediately.
- **One row plays three roles.** A `script_version` row is the draft, then the submitted candidate, then the
  published version. A returned review sends the same row back to `DRAFT`. This is the mutable-submission behaviour
  the owner replaced in the prototype with immutable candidates (D-143).
- **Maker-checker is real and enforced twice:** in the service (`SELF_REVIEW_DENIED`, `SELF_PUBLISH_DENIED`; a
  "maker" is anyone who created or changed the draft) and in a database CHECK. `script.edit` is held by USER only;
  `script.approve` **and** `script.publish` are both held by SC_CHECKER. That is the arrangement D-144 rejects: a
  checker automatically has publishing rights.
- **Immutability is enforced in the database:** guard triggers on versions, sections, modules and module questions;
  insert-only question revisions; consumers re-verify the manifest SHA-256.
- **Three separate maker-checker implementations exist:** scripts (`script_authoring.py`), assignment rules
  (`rule_authoring.py`) and finding rule sets (`finding_rules.py`). Assignment rules already use the cleaner
  three-part pattern: draft → published version + publication record.

### 1.4 Reusable content

Modules are revisioned and reusable across versions, copy-on-write on first edit; a draft module belongs to exactly
one script version. The question bank is reusable with "add from bank". Controls and regulatory references are a
shared library. There are no reusable conditions, option sets or wording versions.

### 1.5 Backend APIs and services

199 operations in the contract. By router:

| Router | Operations | Layer | Service |
|---|---:|---|---|
| `scripts` (read) | 6 | A | inline SQL |
| `script-studio` (authoring) | 20 | A | `script_authoring.py` (1,999 lines) |
| `assignment-rules` | 15 | C | `rule_authoring.py` (1,100), `rule_engine.py` (563), `rule_inputs.py` (360) |
| `script-assignment` | 3 (+1 in Call Detail) | C | `script_assignment.py` (511) |
| `script-simulation` | 18 | C | `script_simulation.py` (375), `simulation_evaluation.py` (196), `simulation_findings.py` (272) |
| `simulation-workbench` | 14 | C | `simulation_workbench.py` (902), `scenario_runner.py` (574) |
| `finding-rules` | 9 | C | `finding_rules.py` (304), `finding_engine.py` (358) |
| `review-workbench`, `reviews` | 9 | C | `review.py` (1,051), `review_dossier.py` (276) |
| Pure domain modules | — | C | `question_controller.py` (816), `lifecycle.py` (104), `answer_evaluation.py` (579), `outcomes.py` (160) |

`script_authoring.py` is not only authoring. Five functions in it are used by layer C and must survive its removal:
`content_of` (rebuilds the content document), `build_manifest`, `makers`, `link_rows`, `lifecycle_of`. Its importers
include simulation, evaluation, the workbench, review and Call Detail.

There is no ORM model for any script table. Services use raw SQL strings, so table and column names are coupled as
text across about 20 modules. **A rename is therefore a text change in many files, not a model change in one.**

### 1.6 Database tables and relationships

101 tables in the schema. 39 are script-related:

| Group | Tables | Kind |
|---|---:|---|
| Core model: `script_family`, `script_version`, `script_section`, `script_module`, `module_question`, `question_bank_item`, `question_revision`, `question_revision_detail`, `control`, `control_mapping`, `regulatory_reference`, `script_version_control_link` | 12 | Authoring, then immutable |
| Authoring history: `script_change_event` | 1 | Evidence |
| Assignment: rule version, rule draft, rule change event, rule publication, `script_assignment`, `script_assignment_attempt` | 6 | Governed content and evidence |
| Simulation: run, event, scenario, scenario revision, content snapshot, batch, result | 7 | Test assets and simulation evidence |
| Evaluation and finding rules: `simulation_answer_evaluation`, finding rule set version and event, simulated finding set and finding | 5 | Governed content and simulation evidence |
| Operational evidence with a foreign key into the above: `conversation_session`, `survey_run`, `question_execution`, `answer_observation`, `rule_evaluation`, `finding`, `review_decision`, `review_approval` | 8 | **Evidence** |

**No foreign key declares `ON DELETE`**, so every one defaults to refusing the delete, and most evidence tables
forbid deletion by trigger. Five migrations refuse to downgrade when rows exist.

### 1.7 Conversation Controller dependencies

`question_controller.build_plan` takes the **content document**, not database rows. It reads, per item:
`question_code`, revision id, position, wording, answer type, option list, `mandatory`, `delivery_mode`,
`max_reprompts`, `branch_condition`, `not_applicable_predicate`, `lifecycle_role`, `on_failure`,
`discloses_policy_information`, `deliver_on_termination`.

- **Ordering is strictly linear**: stage order, then section position, then question position. There is no "on
  answer X go to Y".
- **Gates are items with a role**, not separate entities: identity, willingness to proceed, recording consent and
  cloud-processing consent. The allowed on-failure behaviours are fixed in `lifecycle.py` and described there as
  synthetic development assumptions, not approved policy.
- **The controller already handles non-answers** — unclear, refused, does not know, not delivered, re-prompt up to
  the limit, then unresolved — as development assumptions. This is existing behaviour that gate G-3 must either
  confirm or replace; it is **not** a decision.
- **The controller is not used by any voice module.** It is driven only by simulation, the scenario runner, review
  (replay) and the fixture builder. The live voice path asks no script questions today.

### 1.8 Evaluation, Findings and Review dependencies

| Consumer | Depends on | How |
|---|---|---|
| Answer evaluation | `expected_answer_policy`, `expected_value`, `policy_fact_key`, variants, per question; keyed by `question_code` | Reads the content document |
| Finding engine and rules | Evaluation results; `controls` per question; rules target a `question_code` or control code **as strings** | Reads the content document |
| Review | Latest run's pinned version; **rebuilds the controller plan from the pinned version**; readiness checks look for identity, consent and recording-consent items in the pinned script | Needs manifest and rows to exist |
| Outcomes and KPIs | `controls_satisfied` reads `script_version.manifest` | **Live read on every computation** |
| Call Detail, Policy Detail, register | Script label, version, manifest hash, "why this script" trace, per-question wording | Live joins through the pins |
| Operational voice | `pins_for` requires an assignment to a `PUBLISHED` version and writes the session pin | Pins version id and checksum |
| Voice Lab | `import_from_script` **copies** wording into lab test cases | Copy, not a pin |

**A gap found in passing.** Owner condition D-67 says a script lacking the mandatory identity, consent and
recording-consent gates is never eligible for a live conversation. `live_eligibility` computes this, but **nothing
enforces it**: neither the assignment engine nor the voice session pin checks it. It has no effect today only because
the live path asks no questions. It must be enforced before it does (§6, checkpoint V-1).

### 1.9 Historical evidence and audit references

| Record | Script identifier it holds | Can the target be dropped? |
|---|---|---|
| `script_assignment` | version id, manifest SHA-256, matched rule version id | No |
| `conversation_session`, `survey_run` | version id, manifest SHA-256 | No |
| `question_execution` | `question_revision_id`; a trigger checks it against the version's manifest | No |
| `finding`, `review_decision`, `review_approval` | via `question_execution` | No |
| Simulation runs, results, evaluations | version id, family id, content SHA; several hold a **full copy** of the plan or content | No |
| `audit_event`, `case_event` | entity type and id as strings | Strings survive, but would dangle |

**Seeded-manifest caveat.** The five seeded versions have manifests that freeze ids and positions but **not the
wording**. Their question text can only be rebuilt from the live rows. The row tables are therefore the sole source
of historical wording for those versions until their content is frozen into a self-contained document (§5.2).

**Development-database state not in any repository.** `SG_LIFECYCLE_DEMO`, `SG_EVALUATION_DEMO` and rule
`S2D1-LIFECYCLE-DEMO` exist only as rows in the development database, created through the API. Two carry owner
conditions (keep unpublished; never edit).

---

## 2. Feature-parity matrix (deliverable B)

Class: **1** already in Survey Studio · **2** small capability to recreate inside Survey Studio · **3** backend or
governance capability to retain and reuse · **4** obsolete, to remove. Several rows need two classes: the mechanism
is retained (3) and a small authoring surface is added (2).

### 2.1 The wording items the owner named

| Capability | Script Studio today | Survey Studio today | Class | What to do |
|---|---|---|:-:|---|
| **Approved customer-facing wording** | One text per question revision; approval status settable only by the S&C path | Text on the question card; only the literal "synthetic, unapproved" | 3 + 2 | Retain the approval status and its rule. Split wording from structure as a **Wording Version** (already proposed, SS-D-02 §7.2). Edit it on the question card |
| **Opening and closing statements** | Acknowledgement items with a lifecycle role; "deliver on early termination" | **None.** Every node is a question | 2 | Add a **Statement** node (delivered, optionally acknowledged) with a role. No new screen |
| **Clarification and repeat scripts** | **None.** Only `max_reprompts`; the same wording is repeated | **None** | 2, new | New capability in both. A small set of approved conversation phrases per survey (§4.6). **Blocked by D-NA-8 and the repeat parameters** |
| **Controlled variables** | **None** | **None** | 2, new | New capability in both. Typed slots bound to the field catalog (§4.4). Needs decision AD-8 |
| **Delivery constraints** | Three delivery modes; no audio asset | **None** | 3 + 2 | Retain the modes and the controller's verbatim rule. Add the field to the Wording Version. Audio asset attachment is new work (SCR-019) |
| **Wording version history** | Question revisions with reason, diff and history, fused with structure | A version number only | 3 + 2 | Retain the insert-only revision store and change events. Show wording history on the question |
| **Maker-checker approval** | Real, enforced in service and database | Simulated; better model (immutable candidates, separate Publisher) | 3, amended | Retain the enforcement. Rebuild the flow on the prototype's model (§3.3) |
| **Historical published scripts** | 5 seeded versions plus development demos; pinned by cases, sessions and runs | Cannot read them | 3 | Never rewritten. Shown read-only inside Survey Studio as linear surveys (§5.2) |

### 2.2 Everything else

| Capability | Script Studio today | Survey Studio today | Class | Note |
|---|---|---|:-:|---|
| Library with search and filters | Server-side, facets | In-memory list | 2 | Needs the backend |
| Create a script / survey | Yes | Yes | 1 | |
| Modules: reuse, copy-on-write | Yes | Yes (derived revisions) | 1 | |
| Question bank reuse | Yes | Yes (shared questions) | 1 | |
| Reorder | Up/down | Drag and buttons | 1 | |
| Static inclusion and applicability predicates | Three shapes, AND only | Typed conditions, AND/OR/NOT, three-valued | 1 | Legacy shapes read as a subset |
| Answer-driven routing, follow-ups, decisions, outcomes | None | Yes | 1 | |
| `NUMERIC` and `ACKNOWLEDGEMENT` answer types | Yes | **No** | 2 | Numeric is needed by two evaluation methods |
| Coded options, multi-select, "Other" | No | Yes | 1 | |
| **Mandatory flag** | Yes | **No** | 2 | Outcomes and KPIs depend on it. **Blocked by D-NA-5 and D-NA-10** |
| **Evaluation configuration** (8 methods, expected value, tolerance, variants) | Yes | **No** | 3 + 2 | Engine retained unchanged; a panel on the question card |
| **Control and regulatory-reference mapping** | Yes | **No** | 3 + 2 | Findings and `controls_satisfied` depend on it |
| **Lifecycle roles and gates** (identity, consent, recording, cloud processing; on-failure) | Yes | **No** | 3 + 2 | Controller rules retained. A role on the node. Live eligibility depends on it |
| "Discloses policy information" | Yes | No | 2 | Enforced by the controller |
| Evidence required | Yes | No | 2 | Consumer UNVERIFIED |
| Escalation rule reference | Stored | No | **4** | No code resolves it (UNVERIFIED — confirm before removal). Superseded by governed escalation routing |
| Maximum re-prompts | Yes | No | 2 | **Blocked by the `NA-P-…` values** |
| Language | Read-only attribute, always `en` | None | 4 for now | Single language. Multi-language is a separate future requirement (AD-12) |
| Validation | Server, 7 errors and 9 warnings | Browser, 9 areas, acknowledgements | 1 → 3 | Server becomes authoritative; the prototype's rules are the specification |
| Version comparison | Server semantic diff | Browser comparison by question identity | 1 → 3 | Same |
| Change history and audit | Insert-only events, hash-chained audit | In-memory list | 3 | Retain |
| Optimistic concurrency | `row_version` | None | 3 | Retain |
| Abandon a draft | Yes | No | 2 | |
| Unmapped-mandatory acknowledgement at approval | Yes | Warning acknowledgement with reasons | 1 | |
| Scheduled publication, withdraw | In the enum, **never used** | No | — | Required by SCR-013/016, not built anywhere. Decision AD-13 |
| Undo/redo, graph view | No | Yes | 1 | |
| `S2Actions` component | Exported, no importer found | — | **4** | Dead code |
| Legacy `/surveys` redirects | Yes | — | **4** | Removed with the routes |

### 2.3 The systems around Script Studio

| Capability | Class | Why it is not redundant |
|---|:-:|---|
| Assignment rules and engine | 3 | They decide **which** version a case gets. Survey Studio has nothing equivalent, and should not. Target changes from script version to survey version |
| Conversation controller and lifecycle | 3, extended | The only deterministic executor on the server. Navigation is generalised from "next in order" to "follow the graph" |
| Interactive simulator (server) | 1 + 3 | Overlaps Survey Studio's simulator, but it alone exercises gates, delivery, non-answers and re-prompts |
| Scenario library, batches, A/B, coverage | 3 + 2 | Survey Studio has synthetic profiles only. Retain the engine; surface it in the Simulate step (AD-10) |
| Answer evaluation | 3 | Unchanged if the content contract is kept |
| Finding rules and engine | 3 | Unchanged. Rules that target a question code need the execution key once a question can be placed twice (D-115) |
| Review Workbench | 3 | Unchanged. Depends on being able to rebuild a plan from any pinned version |
| Voice Lab "Import from Script Studio" | 2 | Becomes "import from a survey version" |
| Voice Lab otherwise, Voice Studio | — | Not touched |

---

## 3. Target architecture (deliverable C)

### 3.1 Principle

**One authoring product, one definition store, one content contract, one engine, one publication process.** The
frozen content document is the boundary: everything that authors writes it, everything that executes or evaluates
reads it.

```text
                       Survey Studio (the only authoring product)
        Library · Compose · Build modules · Simulate · Validate · Review and publish
                                      │  operations
                                      ▼
   ┌───────────────────────── Definition store ─────────────────────────┐
   │ Draft (mutable) ──submit──▶ Candidate C-n (immutable) ──publish──▶ Version │
   │ Library assets: Question · Option Set · Wording · Condition · Module       │
   └────────────────────────────────┬───────────────────────────────────┘
                                    │  frozen content document + SHA-256
        ┌───────────────┬───────────┼────────────┬───────────────┐
        ▼               ▼           ▼            ▼               ▼
   Assignment      Call-plan    Controller   Evaluation →     Review, KPIs,
   rules (which    assembly     (one engine: Findings         Call Detail
   version)        (§4)         sim + runtime)
```

### 3.2 One authoring model

The model is the one accepted in SS-01 and exercised by the prototype and the 19 fixtures, with the additions of §2:

- **Question** (identity) → **Question Version** (answer type, option set, selection and text rules, mandatory class,
  evaluation configuration, control links).
- **Wording Version**, a governed facet of a Question (text, option texts, delivery mode, variables, approval).
- **Option Set Version**, **Condition Version** — reusable, versioned.
- **Module Version** — nodes (Question, **Statement**, Decision), each with an optional **lifecycle role**; routes;
  follow-up plans; outcomes.
- **Survey** → Draft, Candidate, Version — module instances, activation, eligibility, skip dispositions, survey
  routes, **conversation phrases**.

**Proposed simplification of storage (AD-3).** SS-01 proposed eight new relational tables (node, edge, follow-up
plan, survey route, option set, wording version, condition, module review events). The inventory shows no consumer
reads authoring rows: all read the content document. The prototype and the fixtures already treat a module as one
canonical document with a fingerprint. Storing a module graph as **one validated, hashed document per module
version**, with a small derived index for "where is this used", would remove the node, edge, follow-up and route
tables and the code that keeps them consistent. Immutability triggers and hashes apply to the row as they do today.
The cost is that the database no longer enforces graph integrity; the server validator does.

### 3.3 One publication process

| Step | Entity | Rule |
|---|---|---|
| Edit | **Draft** — mutable, one per survey, optimistic concurrency | Authors may keep editing at any time |
| Submit | **Candidate `C-n`** — immutable: content, revision, pinned dependency manifest, SHA-256 | A changed draft submitted again creates `C-n+1` and supersedes an open candidate |
| Review | Decision recorded **on the candidate** | Checker ≠ any maker of that candidate. Blockers cannot be waived; warnings need a reason |
| Publish | **Version** — immutable, created from an approved candidate | Publisher holds a separate permission and ≠ submitter. Manifest re-verified |
| Later | Supersede, withdraw | A new publication event; history is never altered |

This is D-143 and D-144 as accepted in the prototype, on the enforcement the backend already has (service checks,
database CHECK, triggers, hash chain). It replaces today's single row that changes status. Assignment rules already
work this way; finding rule sets nearly do. Converging all three on one implementation is possible later and is
**not** required for retirement (AD-4).

**Wording is approved in the same candidate as structure**, shown as its own section of the review. There is no
second approval chain and no second product.

### 3.4 No separate Wording Studio

SS-01 §7.5 proposed a "Wording & Delivery workspace" as a view inside Survey Studio. The owner's instruction is to
avoid a separate Wording Studio. Proposed instead:

- wording, delivery mode and variables are edited **on the question card**, where the text already is;
- statements are nodes in the module, edited like questions;
- conversation phrases are a short section of the survey's settings;
- **Validate** keeps its existing Wording area; **Review and publish** keeps its existing list of wording to
  approve; both already exist in the prototype.

No new route, no new navigation entry, no second editor of the question master.

### 3.5 Treatment of the existing rulings

Nothing below takes effect unless the owner approves it. Each ruling is quoted from the decision register.

| Ruling | Current wording (condensed) | Proposal | What changes, exactly |
|---|---|---|---|
| **SS-D-01** Extend in place | Reuse the existing script families, versions, question bank, modules, approvals, evaluation, findings, review and runtime wherever compatible; new tables where not; additive only; no historical data rewritten | **RETAIN, with one amendment** | Retained: reuse of the governed core, additive migrations, no rewriting of history. **Amended:** "extend in place" gains an end state — once consumers read only the content contract, legacy authoring structures are removed and the retained tables are renamed (§5). Under AD-2 option (b) the phrase "no historical data is rewritten" would need the owner's explicit exception for synthetic data |
| **SS-D-02** Structure versus wording | Survey Studio owns structure, identities, answers, composition, conditions and routing. Customer-facing wording and delivery remain subject to the **existing approved script governance**. One authoring experience, one approval and publishing chain, one question master | **AMEND** | Retained: one question master; one approval chain; wording is governed; Wording Version and binding rules W-1…W-5; `APPROVED_BY_SC` settable only by the S&C approval path. **Superseded:** the phrase "existing approved script governance" as a *separate system*. The same controls — maker-checker, immutability, hashing, approval status — become part of Survey Studio's publication process. The controls do not weaken; their home changes |
| **SS-D-20** Naming | The product is Survey Studio. The old Script Studio may coexist temporarily during migration. "Wording & Delivery" is the name of the governed capability within Survey Studio | **AMEND** | Retained: the name Survey Studio; coexistence during migration. **Added:** an end condition — Script Studio's label, routes and navigation entry are removed at checkpoint R-1. **Narrowed:** "Wording & Delivery" remains the name of the capability in documents; it is not a screen, workspace or navigation entry. Requires an ADR amending ADR-0010 and superseding ADR-0007 §1, and updates to the screen-naming document and the validator's term list, **at R-1, not before** |
| **SS-D-17** Runtime last | The new graph runtime stays in simulation until operational integration is separately authorised. Existing published scripts and historical execution records remain valid | **RETAIN unchanged** | Call-plan assembly (§4) is built and proven in simulation first. Nothing in this assessment brings runtime forward |
| D-143, D-144 | Immutable candidates; separate Publisher | Retain; implement on the server in §3.3 | Today's role grants give SC_CHECKER both approve and publish; that must change (gate G-4) |
| SS-D-08 (proposed) | Lifecycle gates stay above the graph | Retain as a rule | Gates remain controller-enforced and cannot be relaxed by authoring; the gate *items* become authorable nodes (AD-7) |
| SS-D-04, SS-D-12 (proposed) | Approval subjects; API and vocabulary | Still open | Folded into AD-4 and AD-14 |

---

## 4. Data-to-Call-Plan design (deliverable D)

**Status: design proposal.** Simulation only until runtime is separately authorised (SS-D-17).

### 4.1 The governing rule

**Every customer-facing sentence and every routing step is determined by an approved survey version and recorded
data. The language model chooses neither.** Its role is limited to: turning speech into text; proposing a
structured interpretation of what the customer said, which the controller validates; and speaking the text it is
given. Anything it proposes that the controller cannot validate is treated as a non-answer, never as a guess.

### 4.2 The workflow

| # | Stage | Input | Deterministic step | Output | Fails closed as |
|--:|---|---|---|---|---|
| 1 | **Customer application data** | Intake ledger; policy, sale, party and SBQ records | Take an immutable snapshot with source lineage and a hash | Fact snapshot | — |
| 2 | **Input validation** | Fact snapshot; the governed field catalog | Type, unit, range and completeness per field. Each value becomes `PRESENT`, `MISSING` or `INVALID` — never silently defaulted | Validated input set | `INPUT_INVALID` → triage |
| 3 | **Approved survey selection** | Validated inputs; published, effective assignment rules | The existing assignment engine: priority, specificity, explicit fallback | Assignment: survey version id, manifest hash, input hash, rule trace | `AMBIGUOUS`, `INPUT_MISSING`, `TARGET_NOT_EFFECTIVE`, `CONTACT_UNRESOLVED` → hold |
| 4 | **Customer data binding** | The version's declared inputs (condition parameters, wording variables) | Bind each to a catalog field. Record value, source and state | Binding table | Unbound required variable → per its policy (§4.4) |
| 5 | **Module eligibility evaluation** | Bindings; each module's eligibility condition | Three-valued evaluation. Anything depending on a call answer is **deferred**, not guessed | Per module: `IN`, `OUT` (with reason), or `CONDITIONAL` | `UNKNOWN` → the binding's stated unknown policy |
| 6 | **Personalised call-plan assembly** | Steps 1–5 | Assemble and hash one immutable document | **Call plan** (§4.3) | Plan not built → no call |
| 7 | **Approved spoken wording selection** | The plan's pinned Wording Versions | Render variables deterministically. Select the delivery mode | Per item: exact text or audio asset to deliver | Missing wording or asset → item cannot be delivered → §4.5 |
| 8 | **Dynamic question routing** | The plan; validated answer events | The controller follows the compiled graph: one current action, forward only | Next action; decision trace | Unresolved or invalid answer → non-answer handling (**gate G-3**) |
| 9 | **Evidence and compliance review** | Delivery events, answers, trace | Evaluation → findings → human review (existing) | Run record, findings, decisions | Missing evidence is never success |

### 4.3 Three things that must not be confused

| | **Precomputed call plan** | **Conditional paths not yet resolved** | **Actual spoken dialogue** |
|---|---|---|---|
| When it exists | Before the call | Before the call, inside the plan | During and after the call |
| What it is | An immutable, hashed document | The plan's **open decision points** | The run's event log |
| Contents | Version and manifest hash; fact snapshot hash; bindings; lifecycle gates; modules marked `IN` / `OUT` / `CONDITIONAL`; for resolved modules the items with pinned wording, variables already rendered where values are known | For each point that depends on an answer: the question, the possible answers, and the destination of each. Finite and enumerable, because routing is forward-only and acyclic | Which item was delivered, with which wording version and exact rendered text, by which delivery mode; what the customer said; how it was interpreted; which route was taken and why; the terminal state |
| Who decides | Deterministic assembly from data | Nobody yet — the plan states the alternatives | The controller, from the customer's answers |
| Evidence value | Proves what the call was *permitted* to contain | Proves which alternatives were *approved* | Proves what was *actually* said and answered |
| Can it change mid-call? | No | It only narrows | It only grows |

A reviewer can therefore answer three separate questions: was this call allowed to go the way it did (plan), was
that branch an approved alternative (open decision points), and what in fact happened (dialogue).

**The plan is not a script to be read top to bottom.** It is the resolved part of the survey for this customer plus
an explicit map of what is still open. A fully linear legacy script yields a plan with no open decision points.

### 4.4 Controlled variables (new; decision AD-8)

- A variable is a **named, typed slot** in approved wording, bound to one field of the governed catalog: for example
  the policy name or the premium amount.
- The Wording Version declares its slots; approval covers the text **with** its slots. Free expressions, arithmetic
  and nesting are not allowed.
- Rendering is deterministic and versioned: one stated format per type (currency, date, number, name).
- Evidence records the slot values, their source snapshot and the rendered text.
- **A missing or invalid value is never improvised.** Each slot states its policy: block the item, or use an
  approved alternative wording that has no slot.
- Open: whether slots are allowed in `EXACT_AUDIO` wording (a recording cannot contain one) and how names and amounts
  are to be spoken.

### 4.5 Delivery and proof

| Mode | What may be spoken | Proof of delivery |
|---|---|---|
| `EXACT_AUDIO` | The approved recording only | Playback event for that asset |
| `CONTROLLED_TTS` | The rendered approved text only, synthesised | The text sent for synthesis and the provider's completion event |
| `CONVERSATIONAL` | **To be decided (AD-9).** Today this lets the model phrase the item | A prompt is not proof that wording was spoken (workspace rule). Needs transcript alignment at least |

The owner's requirement that the model must not produce uncontrolled customer-facing wording is not compatible with
`CONVERSATIONAL` as it is defined today. AD-9 asks whether to remove the mode, or restrict it to items explicitly
classed as low-risk by Compliance.

### 4.6 Clarification and repeat scripts (new; blocked by gate G-3)

A call needs sentences that are not questions: "Sorry, could you repeat that?", "Let me ask that again", "One moment
please". Today none is governed; the controller repeats the question and anything else would be the model's own
words.

Proposed: a short, governed set of **conversation phrases** on the survey — repeat, clarify, acknowledge, hold,
cannot-proceed — each an approved Wording Version with a delivery mode, approved in the same candidate. The
controller selects the phrase; the model never composes one. **Which phrases exist, when a question is repeated
verbatim or with an approved alternative, and how many times, are decisions D-NA-8 and the `NA-P-…` parameters.
This document proposes the mechanism and no values.**

---

## 5. Retirement and migration plan (deliverable E)

### 5.1 What can and cannot be removed

| Item | Removable? | Condition |
|---|---|---|
| Script Studio screens, routes, navigation entry | Yes | Survey Studio reaches parity (§2) and can show legacy versions read-only |
| Authoring API (20 operations) and script read API (6) | Yes | No frontend caller remains; deep links redirect |
| `script_authoring.py` authoring functions | Yes | The five shared functions (§1.5) are moved out first |
| Legacy condition evaluator and its three shapes | Yes, for new versions | Kept as a read adapter for legacy manifests |
| Authoring row tables: `script_section`, `module_question`, and module rows used only for drafting | Only after the legacy content is frozen into self-contained documents (§5.2) | Otherwise seeded versions lose their wording |
| `script_version`, `question_revision`, `question_bank_item`, `script_family`, rule versions | **No — not while history is preserved** | Evidence refers to them by foreign key. They are **renamed**, not dropped |
| Assignment, simulation, evaluation, finding and review tables | No | Not part of Script Studio |

### 5.2 Data migration and compatibility

**Step M-a — Freeze legacy content.** For every non-draft legacy version, write the full content document that
`content_of` produces into an immutable archive row, with its SHA-256, **alongside** the original manifest and
hash, which are never regenerated. After this, no historical version depends on authoring rows for its wording.
Gate: for every version, the archived document equals what `content_of` returns today.

**Step M-b — One loader, two manifest schemas.** A legacy linear manifest is loaded as a chain: each section a
module instance, each question a node routed to the next. Legacy semantics are preserved exactly, including "a
missing fact makes a legacy condition false". Gate: every stored simulation run replays to the identical state.

**Step M-c — Optional conversion, never automatic.** "Open as a new survey draft" converts a legacy version into a
draft in the new model (the mapping is in SS-01 §8.4). The author reviews it; it goes through the normal publication
process. Gate: for every existing scenario with complete facts, the converted draft produces the same questions,
order, outcome and evaluation results.

**Step M-d — Re-point consumers to the content contract.** Evaluation, findings, review, KPIs and Call Detail read
through one interface that returns the content document for any version, legacy or new.

**Step M-e — Rename.** Once nothing refers to a legacy authoring structure, rename the retained tables and
permissions from "script" to "survey" vocabulary in one mechanical migration. Foreign keys, data and hashes are
unaffected by a rename; trigger function bodies and the raw SQL strings in about 20 modules must be updated
together.

**The alternative the owner should consider (AD-2).** Everything in the database is synthetic. If synthetic
development history does **not** have to be carried forward, steps M-a to M-c can be replaced by a re-seed on the
new model, and the legacy loader, the legacy evaluator and the conversion path need never be built. That is the
single largest reduction in cost and complexity available, and it exists only until real data arrives. It conflicts
with the instruction to preserve historical execution evidence and with SS-D-01 and SS-D-17 as worded, so it is
presented as a decision, not a recommendation. What it would discard: seeded runs and findings, development demo
scripts, stored simulation runs and scenario results. What it would not touch: Voice Lab data, the audit chain and
anything outside the script tables.

### 5.3 Dependency-aware removal sequence

Each step is safe only after the one before it.

1. **Move shared utilities out of `features/scripts/`.** `ErrorBox`, `Field`, `errorText`, `METHOD_LABEL`, `show`
   and `SyntheticBanner` are imported by 17 files in six other feature folders. Move `AssignmentRulesPage.tsx` to
   the rules folder.
2. **Move the five shared backend functions** out of `script_authoring.py` into a content module.
3. **Freeze legacy content** (M-a).
4. **Re-point consumers** to the content contract (M-d).
5. **Switch assignment rules' target** to survey versions (the column already refers to a version id).
6. **Make Script Studio read-only**: no new drafts. Legacy versions are viewable in Survey Studio.
7. **Redirect** `/scripts…` deep links (hard-coded in Call Detail, the assignment panel, the simulator and rule
   detail) to Survey Studio's read view.
8. **Remove the Script Studio frontend**, its tests and its end-to-end spec.
9. **Remove the authoring API and service**; regenerate the contract and the client.
10. **Remove legacy authoring tables and rename the rest** (M-e) — the only irreversible step.

### 5.4 Historical audit preservation

- Original manifests and their SHA-256 values are never regenerated. A test asserts every stored hash is unchanged
  after each migration.
- Case pins, session pins and run pins resolve to the same version and hash before and after.
- Evaluation results, findings, review decisions and approvals are not recomputed and not re-keyed.
- `audit_event` and `case_event` refer to entities by type and id as text. After a rename, a documented mapping from
  old entity type names to new ones is kept; the events themselves, and the hash chain, are not touched.
- Insert-only change histories are retained with their versions.

### 5.5 Rollback strategy

| Stage | Rollback |
|---|---|
| Steps 1–5 | Ordinary code revert; migrations are additive and reversible |
| Step 6 (read-only) | A setting; turn it back |
| Steps 7–9 | Code revert restores screens, API and service; no data was changed |
| Step 10 (drop and rename) | **No code rollback.** Requires a verified database backup and a rehearsed restore beforehand, and is taken only after at least one full accepted cycle with Script Studio already unused |

Survey Studio stays behind its setting until the owner turns it on by default. At every stage a survey has at most
one open draft, so the two editors never work on the same draft.

### 5.6 Regression test requirements

- **The 19 golden fixtures and 63 expected runs**, executed by the server engine, with results identical to the
  reference interpreters.
- **Manifest hash stability** for every published legacy version, after every migration.
- **Replay** of every stored simulation run to the identical state.
- **Evaluation and finding replay**: recomputing from stored inputs gives the stored results.
- **Backend suite**: 52 test files, 411 test functions; 18 files and about 103 functions are core script tests, and
  12 more files depend on seeded script content. These are **ported to the new model, not deleted**.
- **End-to-end**: 33 standard journeys (9 script-related specs to be ported); the 11 prototype journeys become
  journeys on the real backend; accessibility scans on every new screen.
- **Authorization**: every new endpoint and object, including separate Publisher and the distinct-identity rules.
- **Contract**: generated OpenAPI and client regenerated and checked at every API change.

### 5.7 Expected reduction

Stated against running both products. Figures are from the inventory; "after" figures for parts not yet designed are
not invented.

| Measure | Today | After retirement | Note |
|---|---|---|---|
| Authoring products | 2 (one a prototype) | 1 | |
| Question models | 2 | 1 | |
| Condition languages | 3 (script predicates, assignment-rule predicates, Survey Studio conditions) | 1, plus a read adapter for legacy | Converging assignment rules is optional (AD-11) |
| Execution engines | 2 (server controller; browser simulator) | 1 authoritative | AD-6 |
| Validation, comparison and history implementations | 2 each | 1 each | |
| Publication processes | 3 server + 1 simulated | 1 for surveys; optionally 1 for all (AD-4) | |
| Frontend screens removed | — | 2 routes and 6 tabs; about 1,490 lines plus 253 of tests and a 145-line end-to-end spec | |
| Simulation Workbench | 1 route, 1,419 lines | Folded into the Simulate step, or kept | AD-10 |
| Backend API removed | — | 26 operations (20 authoring, 6 read) | Replaced by Survey Studio operations, likely more than 26 |
| Backend service removed | — | Most of `script_authoring.py` (1,999 lines) and its router (845) | Replaced by a survey authoring service |
| Tables removed | — | 2 to 4 legacy authoring tables with history preserved; all 12 core tables replaced under AD-2 option (b) | 8 new tables proposed in SS-01 fall to about 4 under AD-3 |
| npm dependencies removed | — | **None.** Script features use no dependency of their own | Survey Studio's five are already installed |

### 5.8 Specific risks

| # | Risk | Mitigation |
|--:|---|---|
| R1 | Removing a capability that a downstream system silently depends on | The parity matrix (§2) is the gate; removal step 8 is not taken until every class 2 row is delivered |
| R2 | Seeded versions lose their wording when authoring rows go | Freeze first (M-a), with an equality gate |
| R3 | Rename breaks raw SQL scattered across about 20 modules | One mechanical change with the whole backend suite as the gate; done last |
| R4 | Two engines disagree | One authoritative engine; the 19 fixtures are the contract for both until the second is removed |
| R5 | A second, hidden wording product appears | No route, no navigation entry, no separate editor (§3.4) |
| R6 | Building runtime behaviour on undecided policy | Checkpoints that need gate G-3 or G-4 decisions are marked and cannot start without them (§6) |
| R7 | Live calls using a script without mandatory gates | Enforce live eligibility at assignment and at session creation before any question is asked live (V-1) |
| R8 | Controlled variables weaken exact-wording evidence | Deterministic rendering, recorded values, no improvisation, Compliance decision on exact modes (AD-8) |
| R9 | Development-database demo scripts with owner conditions are lost | Listed in §1.9; the owner decides their fate under AD-2 |
| R10 | Scope growth: consolidating assignment and finding rules at the same time | Kept out of the retirement path (AD-11) |
| R11 | Approving wording inside the survey candidate dilutes S&C sign-off | `APPROVED_BY_SC` remains settable only by the S&C path; wording shown as its own review section; "what is approved wording" is a G-4 decision |

---

## 6. Proposed implementation checkpoints (deliverable F)

Smallest sensible steps, in dependency order. **None is authorised.** Each needs the owner's explicit authorisation
by name. Sizes are relative (S, M, L), not estimates.

| # | Checkpoint | Owner's item | Repos | Size | Produces | Blocked by |
|--:|---|:-:|---|:-:|---|---|
| **D-0** | Decisions | — | none | — | Rulings on AD-1…AD-15 and the gate items below | — |
| **W-1** | Wording and call-readiness contract | 1 | specs | S | Contract and fixtures for statements, lifecycle roles, delivery mode, variables, mandatory class, evaluation configuration, control links, conversation phrases | AD-7, AD-8, AD-9; **D-NA-5, D-NA-8, D-NA-10**; G-4 "what is approved wording" |
| **W-2** | Wording and call-readiness in the Survey Studio screens | 1 | frontend | M | The class 2 rows of §2 on the existing screens, still in memory and behind the setting | W-1 |
| **B-1** | Definition store and publication | 2 | backend | L | Drafts, candidates, versions; library assets; operations API; server validation; real maker-checker and Publisher; the content contract | AD-1, AD-2, AD-3, AD-4, AD-14; G-4 (Publisher rule, draft locking, stored schema); **D-NA-5, D-NA-9, D-NA-10** |
| **B-2** | One engine in simulation | 2 | backend | L | Graph navigation in the controller; the 19 fixtures on the server; legacy loader (unless AD-2 (b)) | B-1; AD-6; **D-NA-1, D-NA-9, D-NA-13, D-NA-14, D-NA-15** |
| **B-3** | Survey Studio on the real API | 2 | frontend + backend | L | Persistence, concurrency, conflict states; prototype journeys on the real backend | B-1, B-2 |
| **M-1** | Freeze legacy content and re-point consumers | 3 | backend | M | M-a, M-d; assignment rules target survey versions; scenario keys | B-1 |
| **M-2** | Legacy read view and conversion | 3 | frontend + backend | M | Legacy versions readable in Survey Studio; optional conversion; Script Studio read-only | M-1, B-3. Not needed under AD-2 (b) |
| **P-1** | Call-plan assembly, in simulation | 4 | backend + frontend | M | Stages 1–7 of §4; the plan document; plan view in Simulate | B-2; AD-8 |
| **R-1** | Retire Script Studio | 5 | all | M | Removal steps 6–10; naming ADR; redirects | W-2, B-3, M-1, M-2, and one accepted cycle with Script Studio unused |
| **V-1** | Runtime and voice delivery | 6 | backend + frontend | L | Operational run writer; delivery evidence; live-eligibility enforcement; voice integration | **All of gate G-3** including real-call decisions and parameter values; G-4 escalation handling; approved wording; separate authorisation under SS-D-17 and the Voice Lab conditions |

**Ordering notes.**
- W-1 and W-2 come first because they are small, they close the largest functional gap, and they let the business
  see a complete authoring product before any backend is built. They add required capabilities; they do not reopen
  SS-02 for optional enhancements. The owner may prefer to fold W-2 into B-3.
- B-1 before B-2 before B-3 keeps the rule from the PRD that no editor is built on a separate simplified model.
- R-1 is deliberately after P-1 is *possible* but does not depend on it.
- V-1 is last (SS-D-17) and has the most blockers.

### 6.1 Which open decisions block which checkpoint

| Decision | Blocks |
|---|---|
| **D-NA-5** question classes; **D-NA-10** mandatory versus required | W-1, B-1 (question schema) |
| **D-NA-8** wording on repeats | W-1 (conversation phrases) |
| **D-NA-9** how a non-answer is routed | B-1 (route contract), B-2 |
| **D-NA-13** outcome for "no answer obtained"; **D-NA-14** terminal state for disconnection; **D-NA-15** precedence | B-2 |
| **D-NA-1** reasons a question is unanswered | B-2 (evidence model), V-1 |
| D-NA-3, 4, 6, 7, 11, 12 | V-1 (they shape runtime behaviour; B-2 can simulate without them only if no non-answer turn is offered) |
| D-NA-2, 16, 17; all `NA-P-…` values | Any real call (V-1 go-live) |
| G-4: who holds Publisher; may the approver publish | B-1 |
| G-4: is a draft locked during review | B-1 |
| G-4: what "approved wording" is in Call360 | W-1, B-1 |
| G-4: escalation-handling workflow | V-1 |
| G-4: stored schema for activation, eligibility and the two skip dispositions | B-1 |
| G-4: the AIA/SBQ process (still a working hypothesis) | V-1 go-live |
| G-1 business-user UX acceptance; G-2 screen-reader sign-off | Turning Survey Studio on by default (before R-1) |

---

## 7. Dependency inventory (consolidated)

| Dependent | Depends on | Kind of dependency | Survives retirement by |
|---|---|---|---|
| Call Detail, Policy Detail, register | Assignment → version → family; manifest; question wording | Live joins | Content contract; renamed tables |
| Outcomes and KPIs | `manifest` of the verifying run | Live read | Content contract |
| Review | Rebuilds the plan from the pinned version; gate items in the content | Function call into `content_of` and the controller | Content contract; legacy loader |
| Answer evaluation, finding engine | Per-question evaluation and control fields | Content document | Unchanged |
| Finding rules | `question_code` strings | String reference | Execution key for repeated placements |
| Assignment rules | `target_script_version_id` | Foreign key | Same column, renamed |
| Simulation workbench | Version id, family id, content snapshots | Foreign keys and copies | Unchanged; copies are self-contained |
| Operational voice | `pins_for`: assignment to a published version | Foreign key | Unchanged; plus live-eligibility enforcement |
| Voice Lab | Wording copied at import | Copy | A small change to the import source |
| 17 frontend files in 6 folders | Form utilities exported from `features/scripts/` | Imports | Move the utilities first |
| Four hard-coded link shapes | `/scripts/{family}?version={id}` | URLs | Redirects |
| 12 backend test files | Seeded script content | Fixtures | Ported seed |

---

## 8. Open decisions for the owner

| # | Decision | Options | Recommendation |
|--:|---|---|---|
| **AD-1** | What "remove Script Studio completely" means for the governed store | (a) Retire the product, screens, API and vocabulary; evolve and then rename the governed core. (b) Build a parallel new store and keep the old one as a frozen archive. (c) Clean cut: new store only | **(a)**. It preserves every pin and hash, reuses the enforcement already built, and ends with no "script" structure. (b) keeps two stores indefinitely. (c) is only possible with AD-2 (b) |
| **AD-2** | Must synthetic development history be carried through? | (a) Yes — freeze, load and optionally convert legacy versions. (b) No — re-seed on the new model before any real data exists | **Owner's call.** (b) is materially cheaper and simpler and is available only now; it contradicts the instruction to preserve historical evidence unless the owner excepts synthetic data explicitly |
| **AD-3** | Storage of a module graph | (a) Relational node, edge, follow-up and route tables (SS-01). (b) One validated, hashed document per module version plus a usage index | **(b)** — matches how every consumer, the prototype and the fixtures already work |
| **AD-4** | Publication pattern | Draft → immutable candidate → version for surveys; later, optionally the same implementation for assignment rules and finding rule sets | Adopt for surveys now; converge the others later, separately |
| **AD-5** | Publisher separation on the server | A separate role, or a separate grant of `publish` no longer bundled with `approve` | Part of gate G-4; needed before B-1 |
| **AD-6** | One engine | (a) Server only. (b) Server authoritative, browser engine kept for instant preview with fixture parity | **(a)** unless simulator latency proves unacceptable in B-2 |
| **AD-7** | Statements and gates in Survey Studio | Statement node and lifecycle role authorable; gate rules remain controller-enforced and not relaxable | Adopt; also close the live-eligibility enforcement gap |
| **AD-8** | Controlled variables | Allow typed slots (§4.4)? In exact modes? Missing-value policy? | Allow in controlled TTS with a mandatory per-slot policy; Compliance to decide for exact audio |
| **AD-9** | `CONVERSATIONAL` delivery | Remove; or restrict to items Compliance classes as low-risk | Compliance decision. Not compatible, as defined today, with "no uncontrolled wording" |
| **AD-10** | Simulation Workbench | Fold the scenario library and batch runs into the Simulate step; or keep a separate screen | Fold in, after B-3 |
| **AD-11** | Assignment Rules and Finding Rules | Stay separate modules, re-pointed; or brought into Survey Studio | **Stay separate.** They are not authoring of a journey |
| **AD-12** | Languages | Single language through consolidation; multi-language later | Single language. No governed language fact exists on a case (D-63) |
| **AD-13** | Scheduled publication and withdraw | Build into the new publication process; or defer | Build the states into B-1's model; the screens can follow. Required by SCR-013 and SCR-016, never implemented |
| **AD-14** | API and table vocabulary | "survey" throughout; timing of the rename | "survey" for all new work; rename retained tables at R-1 |
| **AD-15** | Amend SS-D-01, SS-D-02 and SS-D-20; retain SS-D-17 | As stated in §3.5 | Approve as worded, or return with changes |

Gates G-1 to G-5 and G-7 to G-8 of the SS-02 closure document are unchanged and remain open.

---

## 9. What was and was not verified

**Verified in code** (read directly or spot-checked): the route table; every form field in the Script Studio
editor; the absence of variables, clarification text and answer-driven routing in both the UI and the schema; table
count (101); no `ON DELETE` on any foreign key; the controller is not imported by any voice module; `'en'` is
hard-coded; `SCHEDULED` and `WITHDRAWN` are never set; the Survey Studio folder makes no API call.

**Taken from the inventory at header and label level, not line by line:** rule detail, the simulator, finding rules,
review and Voice Lab screens; the internals of `rule_authoring.py`, most of `review.py`, and `voice/lab.py` beyond
the import function.

**UNVERIFIED:**
- Whether `escalation_rule_ref` and `evidence_required` have any consumer beyond storage and the manifest.
- Whether ADMIN holds `script.read`.
- The current contents of the development database, including the demo scripts and rule (no database was touched).
- Line and test counts are file and `def test_` counts, not collected test items.
- No design in §3 or §4 has been prototyped or tested.

**Not done, by instruction:** no implementation, no deletion, no backend, database or runtime change, no paid call.

---

## 10. Owner decisions of 2026-11-21 ("G-6 Architectural Direction Approved: Unified Survey Studio")

**The governing rule, in the owner's words:** "Do not preserve an existing module merely because other modules
currently depend on it. Preserve necessary business functionality, replace obsolete dependencies, and remove
redundant implementations." The end state is "a genuinely simplified Call360, not a cosmetic renaming of Script
Studio." The long-term objective is "one Survey Studio, one canonical survey model, one approved publication process
and one deterministic execution harness."

| Decision | Ruling | Register |
|---|---|---|
| **AD-1** One canonical store | **APPROVED.** One authoritative Survey Studio definition and publication model. Existing script tables, APIs, service boundaries and UI routes are not automatically entitled to survive; each is to be reused, refactored, replaced or deleted on its merits. No two long-lived content stores, no competing authoring models. Evolve-and-rename or clean replacement may be recommended **per structure**, justified by implementation complexity, data dependencies, rollback and long-term maintainability — not by current imports | D-155 |
| **AD-2** Synthetic development data | **APPROVED IN PRINCIPLE:** re-seed instead of preserving every legacy development record. **Before any destructive implementation:** read and inventory the actual development database; identify protected demonstration records and owner restrictions; produce a verified backup; identify exactly what a re-seed replaces; preserve the accepted SS-02 specifications, fixtures, reference interpreters and evidence; delete nothing until a separate destructive-change checkpoint is approved. Synthetic development records are not production customer evidence | D-156 |
| **AD-15** Previous rulings | **APPROVED:** amend SS-D-01, SS-D-02 and SS-D-20 consistent with complete Script Studio retirement. **SS-D-17 retained:** operational voice and runtime integration remains last. Existing compliance controls keep their strength when their implementation moves | D-157 |
| Target product | Survey Studio is the single authoring application, covering the list in D-158. No separate Wording Studio; no replica of Script Studio's six tabs; inline editing and progressive disclosure | D-158 |
| Other systems | Assignment Rules, Simulation Workbench, Finding Rules and Review Workbench are not assumed to remain separate products. UI responsibilities are assessed by business workflow; appropriate design-time configuration moves into Survey Studio; operational case review, runtime execution and governance enforcement stay separate backend responsibilities where justified; shared engines are preferred to duplicated services | D-159 |

**What this changes in the body of this document.**

- **§0.2, §3.1, §5 (recommendation "evolve then rename").** Superseded as a blanket approach. The disposition is now
  per capability and per structure, in `21_UC-01_CONSOLIDATION_MAP.md`: of the 39 script-related tables, 8 are
  replaced, 2 deleted, 11 refactored and 18 reused.
- **§2 (feature-parity matrix) and §5.3 (removal sequence).** Superseded by `21_…` §3, §5 and §6.
- **§5.2 steps M-a, M-b, M-c (freeze, legacy loader, conversion).** Not built, following AD-2. The preconditions of
  AD-2 replace them.
- **AD-4 (one publication implementation), AD-6 (one engine), AD-10 (Simulation Workbench folded in).** Now follow
  from the owner's objective and D-159; they are carried into `21_…` as the design, still to be confirmed in detail.
- **AD-11 (Assignment Rules and Finding Rules stay separate).** **Withdrawn.** `21_…` §2 reassesses them by workflow.
- **AD-3, AD-5, AD-7, AD-8, AD-9, AD-12, AD-13, AD-14.** Still open; restated with the UC-01 findings in
  `22_UC-01_IMPLEMENTATION_REPORT.md` §8.
- **§3.5 (treatment of rulings).** Approved; the amended wording is in the decision register.
- **§4 (Data-to-Call-Plan).** Unchanged as design; previewed in the prototype by UC-01.

