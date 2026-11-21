# SS-01 · Part B — Wording ownership, legacy compatibility, execution, publishing, naming

**Checkpoint:** SS-01 (documentation and design contracts only). **Date:** 2026-11-21. **Status:** PROPOSED for owner
approval. Nothing here has been applied to code, schema, API, ADRs, the approved-exceptions register or tests.

Covers SS-01 deliverables **7** (ownership and binding), **8** (legacy compatibility and transition), **9**
(simulation and future runtime contracts), **10** (validation, approval, pinning, publishing) and the naming proposal
the owner asked for under SS-D-20 (§11). Section numbers continue from Part A.

---

## 7. Survey structure versus approved wording: ownership and binding

### 7.1 Ownership

| Concern | Owner | Carried by |
|---|---|---|
| Which questions exist, their identity and intent | Survey Studio | Question (definition) |
| Answer type, option codes, order, exclusivity, `Other` schema, selection and text validation, mandatory flag, evaluation settings (expected answer, policy fact) | Survey Studio | Question Version, Option Set Version |
| Module composition, routing, follow-up plans, conditions, outcomes | Survey Studio | Module Version, Survey Version |
| **What the customer hears or reads**: question text, option texts, `Other` prompt, clarification text, delivery mode (conversational / controlled TTS / exact audio), exact-audio asset, language | **Wording & Delivery**, under the existing script approval governance | Wording Version |
| Controls and regulatory references a question evidences | Existing control mapping (unchanged) | control links |

"Wording & Delivery" is a governed **capability inside Survey Studio** (owner decision SS-D-20), not a second product
and not a second question master. There is exactly one Question definition per `question_code`; a Wording Version is
a governed facet *of* that question, never a parallel copy.

### 7.2 The Wording Version

```json
{"question": "Q-PURCHASE-REASON", "language": "en", "wording_version": 1,
 "binds_to": {"answer_type": "SINGLE_SELECT", "option_codes": ["PROTECTION", "SAVINGS", "OTHER"]},
 "text": "What was your main reason for buying this policy?",
 "option_texts": {"PROTECTION": "Protection for family", "SAVINGS": "Savings", "OTHER": "Other — please specify"},
 "other_prompt": "Please tell us the reason",
 "delivery_mode": "CONVERSATIONAL",
 "approval": "SYNTHETIC_UNAPPROVED"}
```

- Identity: `{question_code}/{language}/{wording_version}`. Immutable once it leaves draft.
- `binds_to` is the **structural signature** it was written for: the answer type and the exact set of option codes.
- `approval` keeps today's two values and meanings: `SYNTHETIC_UNAPPROVED` and `APPROVED_BY_SC` (D-57). Survey Studio
  can never set `APPROVED_BY_SC`; only the existing S&C approval path can.
- An option's `business_label` (Option Set) is an internal authoring label. What the customer hears for an option is
  `option_texts[code]` in the Wording Version. A missing option text is a validation error.

### 7.3 Binding rules

> **W-1 (pin).** A Question Instance pins `question {code, version, wording_version}`. The published manifest locks
> both with content hashes. Evidence records both (Part A §6.3).

> **W-2 (compatibility).** A Wording Version may be bound to a Question Version only if its `binds_to` signature equals
> that version's signature. A structural change that keeps the signature (for example a text-length limit) may keep
> the wording; a change of answer type or option codes cannot — new wording is required, and its approval starts again.

> **W-3 (no silent wording change).** A published Survey Version keeps the Wording Version it pinned forever. New
> wording reaches a survey only through a new draft that pins it and passes the approval chain.

> **W-4 (no local override).** There is no per-instance wording override. Different wording for one placement means a
> new Wording Version (same question) or a new Question (fork) — both visible in the library with their consumers.

> **W-5 (exactness).** For delivery modes `CONTROLLED_TTS` and `EXACT_AUDIO`, the Wording Version text (and its audio
> asset) is the only text eligible for delivery. A model prompt is never evidence that wording was spoken (workspace
> `CLAUDE.md` §5); delivery evidence is a runtime concern (SS-09).

### 7.4 One approval and publishing chain

The chain is the existing one — `DRAFT → SUBMITTED_FOR_REVIEW → APPROVED → PUBLISHED`, maker ≠ checker, frozen
manifest and SHA-256, re-check at approval and at publication. Nothing about it is replaced.

| Step | What happens to wording |
|---|---|
| Author creates or edits a question in Survey Studio | Types working text in the same card. This creates a **draft** Wording Version. It has no approval. |
| Submit for review | The candidate manifest freezes structure **and** every pinned Wording Version (text, option texts, delivery mode) under one hash. |
| Checker review | The checker sees structure and wording changes in one diff, with wording changes listed separately ("Wording & Delivery changes"). One decision, with a reason. |
| Publish | Gate adds: every pinned Wording Version is frozen, complete (all option texts present) and in an approval state the environment permits. Today the permitted set is `{SYNTHETIC_UNAPPROVED, APPROVED_BY_SC}` and a synthetic version carries the existing caveat "published for synthetic testing only — not approved compliance wording". |
| Later wording-only change | A new draft Survey (or Module) Version that pins the new Wording Version. Its diff shows only wording. Same chain. |

**Permissions (SS-D-11):** editing wording uses `script.edit`; approving `script.approve`; publishing
`script.publish` — the same identities and separation as today. A separate wording-owner sign-off is **not** proposed
for P0 and is listed as an open decision (SS-D-02a).

### 7.5 The Wording & Delivery workspace (inside Survey Studio)

A view over the same data, not another editor of the question master:

- for a survey or module version: every question instance with the text that will be delivered, its delivery mode,
  language, approval state, and the controls it evidences;
- for a question: its Wording Versions, which is pinned where, and "create new wording version";
- filters: not yet approved, exact-delivery, missing option text, changed since last published version.

### 7.6 Change scenarios

| Change | New version of | Wording effect | Consumers |
|---|---|---|---|
| Fix a typo in question text | Wording | New Wording Version | Unchanged until a draft upgrades |
| Change delivery mode | Wording | New Wording Version | as above |
| Reword an option | Wording | New Wording Version (same codes) | as above |
| Tighten text length | Question | Existing wording still valid (W-2) | as above |
| Add, remove or recode an option | Option Set → Question | **Wording must be redone** for the new signature | Breaking; impact report lists routes and scenarios using the option |
| Change a route | Module | None | New Module Version |
| Change an entry rule | Survey | None | New Survey Version |

### 7.7 Legacy rows

An existing `question_revision` holds structure and wording fused in one immutable row. It is read as "Question
Version *n* with Wording Version 1 fused" and is **never rewritten**. Legacy (`/2`) manifests keep embedding the fused
snapshot exactly as now.

---

## 8. Legacy compatibility and transition

### 8.1 Compatibility proof, pair by pair

"Compatible" means the existing table's keys, constraints, guards and meaning can carry the new concept without
bending it. Where they cannot, a **new table** is proposed rather than forcing the fit (owner's condition on SS-D-01).
Sources: migrations `0005`, `0015`, `0016`, `0020`; `script_authoring.py`.

| New concept | Existing | Compatible? | Evidence | Gap → resolution |
|---|---|---|---|---|
| Survey (definition) | `script_family` | **Yes** | Unique `code`, market trigger, purpose | Owner, archived flag → additive columns |
| Survey Version | `script_version` | **Yes** | Immutable outside draft (guard trigger); `manifest` + SHA-256; maker ≠ checker in service and CHECK; `supersedes_id`; one open draft per family (D-56) | Manifest schema `/3`; no column semantics change |
| Lifecycle | script statuses | **Yes, by mapping** | `SUBMITTED_FOR_REVIEW` = PRD "In review"; `SUPERSEDED`/`WITHDRAWN` = "Retired"; "Rejected" = review returns to `DRAFT` with reason; `ABANDONED` kept | No status is added or renamed |
| Module Instance | `script_section` | **Yes** | `(version, module, position)`, unique position = sequence | Stable `instance_code`, entry mode, entry binding, parameters, outcome routes → additive columns plus a **new** `survey_route` table. `inclusion_condition` stays for `/2` only |
| Module Version | `script_module (code, revision)` | **Mostly** | Immutable after draft; copy-on-write on first edit | **Incompatibility:** `script_draft_module_lock` ties a draft module to exactly one script version, and module status has no review states. Standalone module approval (SS-D-04) therefore needs an additive relaxation of the lock and a **new** module review/event table — not an overloading of script events |
| Node | `module_question` | **Only for question nodes** | `(module, question_revision, position, branch_condition)` | **Incompatibility:** a Decision node has no question; a node needs a stable code independent of position. → **New** `module_node` table is the node master; `module_question` remains the question placement it points to (and remains the whole story for `/2`) |
| Edge, follow-up plan | — | **No equivalent** | — | **New** tables |
| Question (definition) | `question_bank_item` | **Yes** | Unique `question_code`; intent, category | Tags, owner → additive |
| Question Version | `question_revision` | **Partly** | Fully immutable; revision number; answer type; mandatory; evaluation fields | **Incompatibilities:** (a) wording fused with structure; (b) choices are a list of label strings (`answer_schema.enum`) with no stable codes, exclusivity or `Other`; (c) uniqueness includes `language`, a wording concern. → **New** Option Set and Wording Version tables; a `question_revision` row is the structural version for `/3`; legacy rows untouched |
| Answer types | `YES_NO, NUMERIC, ENUM, FREE_TEXT, ACKNOWLEDGEMENT` | **Extend** | CHECK constraint is widened by migration, as `0022` did for policies | Add `SINGLE_SELECT`, `MULTI_SELECT`. `ENUM` stays valid for legacy; `NUMERIC` and `ACKNOWLEDGEMENT` remain usable as nodes routed `ALL_TO_NEXT` |
| Condition | three JSON shapes on section / question | **No (as an entity)** | AND only, pre-call facts only, false on missing | **New** condition tables. Legacy shapes stay where they are for `/2` |
| Dependency lock | manifest `/2` embeds module and question snapshots | **Yes, extended** | `build_manifest`, `sha256_of` | `/3` adds conditions, option sets, wording, routes and per-dependency hashes |
| Case pin | `script_assignment` (immutable) | **Yes, unchanged** | Pins version + manifest SHA + inputs | — |
| Session pin | `conversation_session` | **Yes, unchanged** | Pins the assigned published version | — |
| Simulation run | `script_simulation_run/event` | **Yes** | Plan JSON and event payloads are JSONB; pins manifest SHA | New event kinds; no column change expected |
| Scenario | `simulation_scenario*` | **Yes, extended** | Steps keyed by question code | Steps may use the instance key (Part A §6.4) |
| Evaluation result | `simulation_answer_evaluation.results` (JSONB) | **Yes** | Rows carry `question_code` | Add `execution_key` and instance attributes to new results; old rows unchanged |
| Operational evidence | `survey_run`, `question_execution`, `answer_observation`, `rule_evaluation` | **Yes, extended later** | Position unique per run; immutable observations with `supersedes_id` | Additive instance columns at SS-09 |

**Net:** seven existing structures are reused as they are or with additive columns; six concepts get new tables
(node, edge, follow-up plan, survey route, option set, wording version, condition, and module review events).
No existing column changes meaning.

### 8.2 Historical records: what is guaranteed

| Record | Guarantee |
|---|---|
| Published `/2` versions, their manifests and hashes | Never regenerated; a test asserts the stored SHA-256 of every published manifest is unchanged after each migration |
| Case and session pins | Still resolve to the same version and manifest |
| Stored simulation runs | Replay to the identical state on the extended controller (gate for SS-04) |
| Evaluation results, findings, reviews, decisions | Not recomputed, not re-keyed |
| Recordings, transcripts, Voice Lab data, audit chain | Not touched |

### 8.3 Two manifest schemas, one engine

`/2` (linear) and `/3` (graph) both remain executable indefinitely. A `/2` manifest is loaded into the same in-memory
graph as a chain: each section is a module instance with entry mode derived from `inclusion_condition`, each module a
chain of nodes with `ANY` edges, `execution_key = question_code`. **Legacy evaluation semantics are preserved for
`/2`**, including "a missing fact makes a legacy condition false" — tri-state applies only to `/3`.

### 8.4 Converting a linear version (explicit, optional, reviewable)

"Open in Survey Studio as a new draft" creates a `/3` draft from a published `/2` version:

| Legacy | Becomes |
|---|---|
| Section | Module instance, same order; `instance_code` generated once and then stable |
| `inclusion_condition` | Entry rule binding on a generated condition (`{fact, equals}` → `EQ`; `risk_band_in` → `IN`; `all` → `AND`) |
| Module | Module version with a chain: each question node `ALL_TO_NEXT`, last node → `COMPLETED` |
| `branch_condition` / `not_applicable_predicate` | Applicability binding on the node |
| `ENUM` labels | A new Option Set with generated codes shown to the author for confirmation |
| Fused wording | Wording Version pinned from the legacy row |

**One deliberate behavioural difference**, surfaced to the author rather than hidden: a legacy condition with a
missing fact is *false* (module skipped); a converted binding must state an UNKNOWN policy. The converter proposes
`BLOCK` and lists every binding for review. The equivalence gate therefore reads: *for every existing scenario with
complete facts, the converted draft produces the same asked questions, order, outcome and evaluation results*; any
scenario with missing facts is reported with its before/after behaviour.

### 8.5 Transition stages

| Stage | State | Trigger |
|---|---|---|
| T0 | Today. Script Studio only | — |
| T1 | Survey Studio prototype visible behind a flag; nothing persisted | SS-02 |
| T2 | Survey Studio authoring and simulation on real data; Script Studio unchanged for linear versions | SS-03 … SS-07 |
| T3 | Graph versions can be published and assigned; conversion available | SS-08 |
| T4 | New linear drafts disabled; Script Studio becomes read-only history | Owner decision after SS-08 |
| T5 | Script Studio navigation entry removed; `/scripts…` deep links redirect into Survey Studio's read view | Owner decision after SS-10 |

At every stage a family has at most one open draft, so the two editors never work on the same draft.

---

## 9. Deterministic simulation and future runtime execution contracts

Per SS-D-17 (approved), the graph engine runs **in simulation only** until operational integration is separately
authorised. The contracts below are the same for both; only the store, the input source and the permissions differ.

### 9.1 Determinism statement

> **X-1.** The state of a run is a pure function of (pinned manifest, pinned input snapshot, ordered event log).
> No clock, random value, model output or external call takes part in choosing the next step.

> **X-2.** The client never names the next node. It submits an answer to the **current action**; the server validates,
> appends events atomically and returns the next action.

### 9.2 Run lifecycle

```text
NOT_STARTED → IN_PROGRESS ⇄ PAUSED
IN_PROGRESS → COMPLETED(survey outcome)
            → TERMINATED(reason)        lifecycle gate or reported event
            → BLOCKED(reason, at)        ROUTE_MISSING · AMBIGUOUS_ROUTE · BLOCKED_UNKNOWN · TRAVERSAL_LIMIT
            → ABANDONED
```

`BLOCKED` is not completion: it is an explicit state needing review (SS-ROU-007). Existing outcomes and termination
reasons are kept and mapped to the outcome catalog (SS-D-05).

**Start.** Pins: survey version, manifest SHA-256, fact snapshot (profile in simulation), risk assessment where used.
Emits `STARTED` with those pins — as the controller does today.

**Step states of the current action:** `AWAITING_DELIVERY`, `AWAITING_ANSWER`, `REPROMPT` (existing), plus
`BLOCKED`. Decisions and module entry evaluations are never client-visible steps; they are resolved inside the
transition that follows an answer.

### 9.3 Step contract (logical)

Current step returned to an authoring or runtime client:

```json
{"run": "…", "manifest_sha256": "…", "status": "IN_PROGRESS",
 "action": {"action_id": "mi-risks/n2#1", "kind": "ASK",
            "module_instance": "mi-risks", "question_instance": "mi-risks/n2", "occurrence": 1,
            "question": {"code": "Q-UNDERSTOOD", "version": 1, "answer_type": "YES_NO"},
            "wording": {"ref": "Q-UNDERSTOOD/en/1", "text": "…", "delivery_mode": "CONVERSATIONAL",
                        "options": [{"code": "YES", "text": "Yes"}, {"code": "NO", "text": "No"}]}},
 "next_step_authority": "SERVER"}
```

Answer submission: `{action_id, idempotency_key, answer | non_answer}`.

| Case | Result |
|---|---|
| Valid answer to the current action | Events appended in one transaction; next action returned |
| Same `idempotency_key` and same payload again | The original result, no new event (SS-AT-024) |
| Same action, different payload | `ACTION_ALREADY_RESOLVED` (existing behaviour) |
| `action_id` that is not current | `STALE_ACTION` (existing) — this is also what rejects "jump to a future question" (SS-AT-029) |
| Invalid answer | A validation code from Part A §3.7; nothing recorded; action unchanged |

A general runtime client receives only the current approved prompt and permitted options. Routing detail is available
only through the trace, to authorised roles.

### 9.4 Event log (the decision trace)

Existing controller events are kept. New kinds, each with a monotonically increasing sequence number:

| Event | Payload (essentials) |
|---|---|
| `MODULE_ENTRY_EVALUATED` | instance, entry mode, binding, result, policy applied, **explanation tree** |
| `MODULE_ACTIVATED` / `MODULE_SKIPPED` | instance, status (`SKIPPED_FALSE`, …), reason |
| `ANSWER_RECORDED` | the evidence record of Part A §6.3 |
| `DECISION_EVALUATED` | question instance of the decision, binding, result, explanation tree |
| `ROUTE_SELECTED` | from, trigger code, edge key chosen, rule used (specific / default), candidates not chosen |
| `QUEUE_BUILT` | source instance, selected options, ordered items with the option that caused each, deduped, skipped |
| `QUEUE_ADVANCED` / `QUEUE_INTERRUPTED` | cursor; interrupt option and outcome |
| `MODULE_OUTCOME` | instance, outcome, route taken |
| `ANSWER_SUPERSEDED` | superseded evidence, reason, actor, invalidated downstream instances |
| `PAUSED` / `RESUMED` | actor, reason |
| `RUN_BLOCKED` | reason, location |

**Explanation tree** (for every condition evaluation):

```json
{"condition": "C-ENHANCED-REVIEW@1", "result": "UNKNOWN",
 "tree": {"op": "AND", "result": "UNKNOWN", "args": [
   {"op": "GTE", "result": "TRUE",
    "left": {"field": "customer.age_years", "state": "KNOWN", "value": 65, "source": "profile P-…@1"},
    "right": {"param": "minimum_age", "value": 60}},
   {"op": "OR", "result": "UNKNOWN", "args": [
     {"op": "GT", "result": "UNKNOWN",
      "left": {"field": "policy.annual_premium", "state": "UNKNOWN"}, "right": {"param": "premium_threshold", "value": 12000}},
     {"op": "EQ", "result": "FALSE",
      "left": {"input": "risk_understood", "state": "KNOWN", "value": "YES", "source": "mi-enh/n1#1"},
      "right": {"literal": "NO"}}]}]}}
```

This one structure answers every "Why did this run? / Why was this skipped?" in the simulator (SS-SIM-005,
SS-UXE-018) and is the audit evidence at run time (SS-ROU-010). Sensitive values are masked for roles without access.

### 9.5 Back / Edit

Allowed only where the channel policy permits it (always in simulation). Editing the answer of instance *I*:

1. Append `ANSWER_SUPERSEDED` for *I* (occurrence *k*).
2. Mark as superseded every answer recorded after *I* whose instance is no longer on the path, **and** every answer
   that depended on *I*: its follow-up queue, any decision whose binding read *I*, and everything downstream of a
   route that changes. Answers on an unchanged path that did not depend on *I* are kept.
3. Record the new answer as occurrence *k+1*; recompute the path from *I*.
4. Module outcomes and entry evaluations after *I* are re-evaluated and re-traced; earlier events are never deleted.

P0 simplification (to confirm, SS-D-10): if the changed answer alters the route at all, every later answer in that
module instance and in later instances is superseded and must be re-collected. It is conservative and easy to explain.

### 9.6 Pause / Resume

`PAUSED` freezes the cursor (including a queue cursor). `RESUMED` continues on the **pinned** manifest even if newer
versions have been published since (SS-AT-023, 044). No state lives outside the event log.

### 9.7 Defences

Traversal cap (steps per run, visits per instance) as a second line behind cycle validation; row lock + replay per
operation (existing); optimistic check on the event sequence; bounded payload sizes.

### 9.8 Simulation versus future runtime

| | Simulation (authorised path, SS-04) | Operational runtime (deferred, SS-09) |
|---|---|---|
| Version | Any draft or published version; a single module | Published **and** assigned versions only |
| Inputs | Synthetic profile | Case fact snapshot and risk assessment |
| Store | `script_simulation_*` | `survey_run`, `question_execution`, `answer_observation`, `rule_evaluation` |
| Back/Edit, fork, UNKNOWN injection | Yes | By channel policy; no injection |
| Permissions | `script.simulate` | Runtime service identity (to be defined) |
| Lifecycle gates | Simulated | Enforced |

### 9.9 Coverage (defined, so it is never mistaken for correctness)

Counted by unique key across a set of runs: edges taken, option codes chosen, decision results seen
(`MATCH`/`NO_MATCH`/`UNKNOWN`), module statuses seen, follow-up plans exercised (queued / interrupted / empty).
The report lists what was **not** exercised and never states that a survey is "correct" (SS-SIM-009, SS-AT-031).

---

## 10. Validation, approval, dependency pinning and immutable publishing

### 10.1 Validation rules

Server-side, authoritative, on the exact saved revision. Every issue has a stable code, a severity, the keys of the
affected object and a suggested fix. `ERROR` blocks submission. Grouped as the readiness dashboard shows them
(PRD screen I). Existing codes are kept; new ones are marked ★.

| Group | Codes (illustrative list, to be completed in SS-03) |
|---|---|
| Content | `INVALID_QUESTION`, `EMPTY_SECTION`, `NO_SECTIONS`, ★`OPTION_SET_INVALID` (duplicate code, < 2 options, two `Other`), ★`OTHER_SCHEMA_MISSING`, ★`WORDING_MISSING`, ★`OPTION_TEXT_MISSING`, ★`WORDING_SIGNATURE_MISMATCH`, `EXACT_AUDIO_ASSET` (warning) |
| Routing | ★`ROUTE_MISSING`, ★`AMBIGUOUS_ROUTE`, ★`UNREACHABLE_NODE`, ★`NO_PATH_TO_OUTCOME`, ★`CYCLE_DETECTED`, ★`OUTCOME_UNDECLARED`, ★`OUTCOME_ROUTE_MISSING`, ★`BACKWARD_ROUTE`, ★`FOLLOWUP_MAPPING_MISSING`, ★`FOLLOWUP_TARGET_INVALID`, ★`REJOIN_MISSING`, ★`DUPLICATE_PRIORITY`, ★`RULE_FALLBACK_MISSING` |
| Conditions | `INVALID_CONDITION`, ★`TYPE_MISMATCH`, ★`UNIT_MISMATCH`, ★`UNKNOWN_POLICY_MISSING`, ★`UNKNOWN_EDGE_MISSING`, ★`DEPENDENCY_NOT_AVAILABLE`, ★`PARAMETER_UNBOUND`, ★`INPUT_UNMAPPED`, ★`COMPLEXITY_LIMIT` |
| Lifecycle (existing rules, unchanged) | `ROLE_STAGE_MISMATCH`, `IDENTITY_GATE_REQUIRED`, `STAGE_ORDER`, `LIFECYCLE_INCOMPLETE`, `NO_LIFECYCLE` |
| Reuse dependencies | ★`DEPENDENCY_NOT_APPROVED`, ★`DEPENDENCY_DEPRECATED` (warning for existing pins, error for new adoption), ★`DEPENDENCY_STALE` (info: a newer version exists) |
| Scenario coverage | ★`REQUIRED_SCENARIO_FAILED` (error), ★`BRANCH_UNTESTED` (warning) |
| Controls | `NO_CONTROL`, `MANDATORY_COLLECT_ONLY`, `NO_MANDATORY` (existing warnings) |

Severity policy: warnings that the existing chain already requires the checker to acknowledge (unmapped mandatory
questions) keep that behaviour; which new warnings need acknowledgement is decision SS-D-21 (Part C).

### 10.2 Approval subjects and states (SS-D-04)

Two approval subjects in P0, both on the existing chain: **Module Version** and **Survey Version**. Questions, option
sets, wording and conditions are approved **as contents of the first candidate that pins them**; their library status
is derived:

| Derived library status | Meaning |
|---|---|
| `DRAFT` | Exists only in drafts |
| `IN_REVIEW` | Pinned by a submitted candidate |
| `APPROVED` | Pinned by an approved or published version |
| `DEPRECATED` | Marked by a curator action with a reason; cannot be newly adopted; existing pins keep working |

A survey draft may pin (a) published module versions and (b) local draft modules, which are approved and published
with the survey as today. It may not pin a module that is in another author's unapproved draft.

### 10.3 Candidate, manifest and hash

On submission the server validates, runs the required scenarios, then freezes the candidate:

```text
manifest/3  (hashed with the existing canonical SHA-256)
  survey            code, version label, language
  sequence, instances[] (entry binding, params, routes), end outcome
  modules{}         code@revision → entry, outcomes, nodes[], edges[], follow-up plans
  questions{}       code@version → structural snapshot (same field names as /2)
  option_sets{}     code@version → options
  wordings{}        code/lang/version → text, option texts, delivery mode, approval
  conditions{}      code@version → params, inputs, AST
  dependency_lock[] every dependency with its own content SHA-256
  regression        scenario set, results, coverage summary at the time of freezing
  sections[]        /2-compatible flattened view with execution_key on each question
```

- The checker reviews **this** artefact; approval and publication each recompute the hash and refuse on mismatch
  (existing behaviour; SS-AT-021).
- Any edit after submission returns the version to `DRAFT` and voids the submission (existing behaviour).

### 10.4 Publication condition

`validation has no ERROR` **and** `every dependency approved and locked` **and** `wording gate passed (§7.4)` **and**
`required scenarios pass` **and** `checker ≠ any maker` **and** `hash unchanged since approval`. Publication is atomic
and returns the version and manifest SHA-256. Superseding an earlier version remains an explicit checker choice
(D-55).

### 10.5 Immutability, enforced in three places

1. Service: only `DRAFT` with a matching `row_version` is editable (`STALE_DRAFT` otherwise).
2. Database: guard triggers on versions, modules and their children; `forbid_change` on immutable rows — extended to
   every new table.
3. Evidence: every run, evaluation and finding stores the manifest SHA-256 it used.

### 10.6 Reuse governance

- **Consumers view** for every asset: drafts and published versions that pin it, with counts.
- **Upgrade** in a consumer's draft: shows the diff between pinned and new version, the routes and scenarios
  affected, re-runs the consumer's scenarios, and only then applies. **Keep pinned** does nothing. **Fork** creates a
  new definition with a new code.
- **No auto-upgrade, ever** (SS-VAL-012).
- **Breaking changes** (option codes, answer type, a module's outcome list, a condition's parameter or input schema)
  are flagged as such and cannot be applied by upgrade without resolving every affected route or binding.

---

## 11. Naming: "Survey Studio" (SS-D-20 as decided) — proposed amendment

> **Applied 2026-11-21 (owner decision D-113).** The amendment below was approved and applied as ADR-0010, with the
> EXC-001, validator, naming-document and E2E-18 changes. §11.5 describes the validator state *before* that; the
> validator now passes all 63 checks. Two differences from the proposal: the Survey Studio route is described in a
> note below the Stage 0 route table rather than inside it (that table is checked against the Stage 0 screen
> specification), and `SCRIPT_GOVERNANCE_AND_ASSIGNMENT.md` was not edited (it was not among the files the owner
> named). The existing frontend tests did not need to change: they stay valid with the setting off, and a new test
> covers the setting on.

The owner has decided: the new authoring product is **Survey Studio**; the old Script Studio may coexist during
migration; **Wording & Delivery** names the governed capability within Survey Studio. This reverses the naming part
of D-2 / ADR-0007 §1. The changes below are **proposed for explicit approval**; none has been made.

### 11.1 Proposed ADR (text to be adopted as a new ADR amending ADR-0007 §1)

> **Title.** Survey Studio naming; Script Studio as a transitional name.
> **Amends.** ADR-0007 §1 (naming) only. ADR-0007 §2 (script version lifecycle) and §3 are unchanged.
> **Supersedes.** Exception EXC-001 for the product name; EXC-001 continues to apply to the legacy survey UI and
> API paths it names, which remain unused.
> **Decision.**
> 1. The governed authoring product is **Survey Studio**: navigation label, page titles, breadcrumbs, accessible
>    names and test names.
> 2. **Script Studio** remains the label of the existing linear script screens for the transition period only, shown
>    as "Script Studio (legacy)" once Survey Studio is visible, and is removed at transition stage T5.
> 3. **Wording & Delivery** is the name of the capability inside Survey Studio that governs customer-facing wording
>    and delivery modes.
> 4. UI routes: `/survey-studio…`. Existing `/scripts…` routes keep working. `/surveys…` stays a legacy redirect.
> 5. API: new routes under `/api/v1/survey-studio/…`; existing `/api/v1/scripts…` and `/api/v1/script-versions…`
>    unchanged. The legacy survey API path named in EXC-001 remains prohibited.
> 6. Domain and database names (`script_family`, `script_version`, `survey_run`, …) are unchanged. UI vocabulary:
>    Survey, Module, Question, Option, Condition, Outcome.
> 7. `SUR-*` and `SCR-*` requirement IDs are unchanged; `SS-*` IDs live in the Survey Studio PRD.

### 11.2 Specification files that would change

| File | Change |
|---|---|
| `docs/adr/` | Add the new ADR; add a status line to ADR-0007 pointing to it |
| `docs/spec/APPROVED_EXCEPTIONS.md` | EXC-001: narrow to the `/surveys` paths; note the product-name reversal with the decision reference |
| `scripts/validate_specs.py` | Remove `"Survey Studio"` from `PROHIBITED_TERMS` (the path terms stay) — a one-line change to the specs validator |
| `docs/product/SCREEN_NAMING_AND_ROUTES.md` | Rows 14, 29, 55 and rule 7: Survey Studio as the module; Script Studio as legacy; add Wording & Delivery; routes |
| `docs/acceptance/S0_TEST_MATRIX.md` | E2E-18: assert "Survey Studio" present once enabled; keep the existing prohibition of the spaced product name |
| `docs/product/SCRIPT_GOVERNANCE_AND_ASSIGNMENT.md` | Pointer to the Survey Studio contracts for structure; wording governance text unchanged |
| Master BRD, requirements register | **No change** (checksum-frozen) |
| `CLAUDE.md` files | Workspace and frontend already say "Survey Studio"; no change needed. Backend: none |

### 11.3 Tests that would change (frontend, when the label first appears — SS-02)

| Test | Today | Proposed |
|---|---|---|
| `e2e/auth.spec.ts:78` | asserts page text does not contain "Survey Studio" | keep the assertion on the spaced product name; remove the "Survey Studio" one |
| `src/App.test.tsx:62` | asserts the body contains neither the spaced product name nor "Survey Studio" | keep the spaced-product-name assertion; with the flag off, "Survey Studio" absent; with it on, the navigation link present |
| New | — | navigation shows "Survey Studio" only when the feature flag is on |

### 11.4 Order of application

1. Owner approves §11.1–11.3 (this checkpoint's decision list).
2. Specs changes of §11.2 are applied as one authorised specification edit. **Only then does the specs validator pass
   again.**
3. Frontend test changes of §11.3 are made in SS-02, in the same change that first shows the label.

### 11.5 Current validator state (reported separately, as requested)

`scripts/validate_specs.py`: requirements pack **PASS**; CP0.0 checks **61 of 62 pass**. The one failure is the
terminology check: "Survey Studio" appears in the owner's two PRD files and in the SS-00 / SS-01 plan files and
`SESSION_HANDOFF.md`, none of which is on the approved list. It is a known, expected consequence of SS-D-20 and will
clear at step 2 above. No other terminology conflict exists: none of the other four prohibited terms (the spaced
product name, the two legacy survey paths and the legacy lifecycle string) appears in any new file.
