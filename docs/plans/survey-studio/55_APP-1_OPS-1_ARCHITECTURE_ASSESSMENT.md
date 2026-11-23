# APP-1 / OPS-1 — Survey Studio as the operational conversation source: architecture assessment

**Status: ASSESSMENT ONLY, prepared 2026-11-23 for the owner's review. Nothing here is decided, authorised or built.**
No application code, migration, intake hold, operational assignment or voice-session behaviour was changed to write
it. Synthetic data only. Authorised by the owner's message of 2026-11-23, "Accept SHARED-1, Enable Development 0037
and Prepare APP-1 / OPS-1", Part E.

Names used here:

* **APP-1** — one authoritative, versioned *application snapshot* that both assignment and control applicability
  read.
* **OPS-1** — the operational path: a selected survey journey linked to a callback case, pinned to conversation
  sessions, with operational evidence, holds, preflight and review.

Every statement about today's behaviour cites the code (`BE` = `Call360-backend`, `FE` = `Call360-frontend`,
`mig` = `BE/migrations/versions`). Companion documents: `51_…` (retirement readiness), `52_…`/`53_…` (SHARED-1),
`23_UC-02_…` §2.3–2.4 (snapshot and eligibility contracts), `35_ASG-2A_…` §6 (field-by-field gap table).

---

## 0. Summary

1. **There is no "application" in the operational data model.** A callback case references one sale event; the
   facts a rule reads come from the latest immutable `policy_fact_snapshot`, the latest FINAL SBQ assessment, the case
   and its eligible contacts. Survey Studio's "synthetic application" is a typed-in pair
   `{assignment_inputs, facts}` with no link to any of these. Lineage between the two is recorded in code as
   `UNVERIFIED`.
2. **The two vocabularies do not line up.** Nine rule fields and eight survey facts overlap on one concept. Three
   survey facts have no source at all (replacement, plan name, age), riders do not exist anywhere, and three rule
   fields are not survey facts.
3. **Selection is ready; everything after selection is not.** The existing engine can already select surveys through
   survey-only rules and governed groups from any input dict. Nothing can record that selection against a case:
   every Survey Studio record is constrained to `record_class = 'SIMULATION'`.
4. **The operational chain is script-shaped at five fixed points:** the intake hold, the assignment record, the
   callable-case test in voice preflight, the session pin (guarded by a database trigger), and the evidence tables
   (a question execution must belong to the pinned script's manifest).
5. **A finding that matters for sequencing:** the voice session does not execute a script today. It plays a fixed
   message; `survey_run` and `question_execution` rows are written only by the seed and a CLI fixture
   (`BE/app/domain/review_fixtures.py`, `BE/app/cli.py:236`). `question_controller.build_plan` is never imported by
   `BE/app/voice/*`. So "replacing Script Studio as the conversation source" is, today, replacing assignment,
   pinning and evidence *shape* — the live controller has yet to be wired for either source.
6. **Recommended next boundary: APP-1 as a read-only, stateless step** (§13). It removes the `UNVERIFIED` lineage
   and writes nothing operational. OPS-1 proper needs Business and Compliance decisions first (§12).

---

## 1. Authoritative application identity and source data

**Today**

| Fact | Evidence |
|---|---|
| No `application` table or entity | searched `mig/0001`–`0037` |
| Sale and policy: `policy`, `sale_event` (unique `sale_ref`; unique `(source_system, source_reference)`), `policy_party_role`, `party`, `fsc_representative` | `mig/0003_party_policy_sale.py:49-200` |
| SBQ: `risk_assessment` per sale event, kind `CALLBACK_SELECTION` | `mig/0004_sbq_risk.py:65-98` |
| Case: `callback_case` references `sale_event_id` only; unique `(sale_event_id, obligation_type, source_request_ref)`; one obligation type, `SALE_VERIFICATION`; market must equal the policy's; identity columns immutable | `mig/0006_case_evidence.py:122-153, 450-459` |
| Intake: manual only; `MOCK_API`, `BULK`, `INTERNAL_API` report `available=False`; every row `MANUAL`, `is_synthetic=true`; product list is a hard-coded tuple | `BE/app/api/intake.py:126-133, 212-242`; `BE/app/domain/intake.py:17-18, 45-50` |

**Assessment.** The natural operational identity of "the application under verification" already exists: it is the
**sale event of a callback case**. Introducing a separate application master would duplicate `sale_event` and create
a second identity to reconcile. The assessment therefore treats *application* as a **derived view of a case's sale**,
not a new source entity.

**What is missing is not an identity but an authority statement:** for each fact, which source field is the
authoritative one. Today that is implicit in `rule_inputs.case_inputs`.

| Option | Description | Trade-off |
|---|---|---|
| A-1 (recommended) | "Application" = the case's sale event; identity = `callback_case.id` + `sale_event.id`; no new master table | no duplicate identity; matches the unique key of a case |
| A-2 | A new `application` entity fed by intake | needed only if one application can span several sale events or policies — a business question (§12, Q-1) |

## 2. One versioned application snapshot for assignment and control applicability

**Today**

* `policy_fact_snapshot` is immutable and hashed: `facts` JSONB, `field_provenance` JSONB, `sha256` UNIQUE,
  insert-only (`mig/0003:185-198, 283`). Intake writes thirteen keys (`BE/app/domain/intake.py:867-881`).
* `rule_inputs.case_inputs` (`BE/app/domain/rule_inputs.py:196-258`) builds the nine rule inputs from: the **latest**
  snapshot by `captured_at`, the **latest FINAL** risk assessment, the case, and the current eligible contact roles.
* Operational assignment already freezes what it read: `script_assignment.input_snapshot`, `input_sha256`,
  `policy_fact_snapshot_id`, `risk_assessment_id` (`mig/0005:230-252`).
* Survey side: `application_sha256` = hash of `{assignment_inputs, facts}` on a composite plan
  (`BE/app/domain/survey/assignment_groups.py:520-522`). `INPUT_CONSISTENCY = UNVERIFIED` (`:48-54`);
  `LINEAGE = UNVERIFIED` (`BE/app/domain/survey/policy_evaluation.py:39-42`).

**Assessment.** Assignment reads *rule inputs*; control applicability and call planning read *survey facts*. Today
they are typed separately, so one application can be described inconsistently (ILP in one, Protection in the other)
and nothing detects it. One snapshot must produce both from the same sources.

Proposed shape (for review, not built):

```text
application_snapshot
  case_id, sale_event_id                       identity (§1)
  policy_fact_snapshot_id + sha256             pinned source
  risk_assessment_id + sha256 (nullable)       pinned source
  contact_selection basis                      eligible roles as read
  mapping_version                              the governed mapping used (below)
  assignment_inputs   {nine rule fields}       exactly what rule_inputs produces today
  facts               {survey fact catalogue}  only facts that HAVE a mapped source
  lineage             per value: source table.column, source record id, derivation
  unmapped            catalogue facts with no source, listed, never defaulted
  sha256              over assignment_inputs + facts  (= today's application_sha256 shape)
  insert-only; a newer source produces a NEW snapshot, never an update
```

Two properties matter:

* The hash is computed over the same structure simulation already hashes, so a simulated journey and an operational
  one for the same values are provably about the same application.
* A fact with no source is reported as `unmapped` and stays UNKNOWN. The engines already treat UNKNOWN as a real
  state and never as "does not match" (`assignment.check_inputs`, `BE/app/domain/survey/assignment.py:283-321`).

**The mapping is a governed artifact, not code.** `35_ASG-2A_…` §6 already lists what one snapshot needs: an
authoritative source per value, a governed versioned mapping, owner and Compliance approval, and a decision on new
rule fields. This assessment agrees and adds: the mapping must be versioned and pinned by every snapshot, like a
finding-rule set is pinned by an evaluation.

## 3. Replacement, rider and other product attributes

| Attribute | Today | Gap |
|---|---|---|
| Replacement | only `sale_event.sale_event_type = 'REPLACEMENT'` (`mig/0003:178`), copied to `facts.sale_event_type` | no replaced-policy link, no flag; survey fact `policy.is_replacement` (`mig/0027:73`) has no source; not a rule field |
| Riders | **absent** — no table, column or fact | needs source data, an intake contract and a definition |
| Sum assured | on `policy`, **not** in the snapshot keys | survey fact `policy.sum_assured` cannot be filled from the snapshot today |
| Annual premium | `premium_amount` + `premium_frequency` | a derivation; what "annual" means for a SINGLE premium is a definition, not arithmetic |
| Term | `premium_term_years` | survey fact is `policy.term_years` — premium term and policy term are different things |
| Plan name | `product_code`, `product_subtype` | no plan-name field |
| Customer age | `party.date_of_birth_year` only | age at which date, and for which party (policyholder or insured) |
| Channel | `selling_channel` includes BROKER | survey fact `sale.channel` has no BROKER value |
| `is_ilp`, `premium_frequency`, SBQ risk band | rule fields | not in the survey fact catalogue (T-4 of `51_…`) |
| Product list | hard-coded synthetic tuple | no governed product list |

**Assessment.** Technically each row is an additive change (a snapshot key, a catalogue entry, an intake field).
None of them can be *defined* technically: what counts as a replacement, which riders matter, and what age means are
Business definitions (§12, Q-2…Q-5). Adding a **rule field** (for example replacement) is an additive change to the
authoritative engine's field list (`BE/app/domain/rule_engine.py:41-51`); it changes no existing decision but it is
an engine-contract change and needs its own authorisation.

## 4. Application fact lineage and data consistency

**Today**

* Every sourced table carries provenance columns (`BE/app/db/ddl.py:54-68`); intake keeps an insert-only ledger
  (`mig/0009_intake.py`).
* Conflicts are **reject-only** (`BE/app/domain/intake.py:255-307`); corrections are not implemented
  ("Corrections arrive in CP0.4b", `:293`); `field_change` is not written; the `DATA_CONFLICT` hold exists but
  intake never places it.
* The snapshot has no `supersedes`; "latest by `captured_at`" is a convention.
* SBQ assessments have a real supersession model (`supersedes_id`, PROVISIONAL → FINAL → SUPERSEDED,
  `mig/0004:151-198`). No write or override endpoint exists; intake writes `SOURCE_ASSIGNED` only.

**Assessment**

| Question | Technical answer | Needs a decision |
|---|---|---|
| Can each value name its source? | Yes — `field_provenance` exists per snapshot key; the application snapshot adds the mapping step | — |
| What if a newer policy snapshot or risk assessment arrives after a journey was selected? | Detectable: the pinned ids differ from the latest | **Policy:** re-select, hold, or continue (Q-6) |
| What if two sources disagree? | Today intake rejects; nothing reconciles | **Policy:** correction workflow (already deferred to CP0.4b) |
| What if a fact a survey needs is unmapped or UNKNOWN? | The engines keep it UNKNOWN; a plan can be `NOT_READY` | **Policy:** hold the case, or call anyway (M-4 of `51_…`) |

Consistency rule proposed: assignment and planning for one journey read **one** snapshot id. A journey whose
selection and plan cite different snapshots is invalid by construction.

## 5. How survey-only rules would select governed surveys for an application

**Today.** The whole selection chain is pure given the database state and an input dict:
`assignment_groups.select_set` runs the existing engine once per published group over that group's rules
(`BE/app/domain/survey/assignment_groups.py:352`), `compose_pure` (`:503`) assembles the composite plan, and
`assignment.candidates` asks the loader for both kinds of rule (`BE/app/domain/survey/assignment.py:328-335`).
SHARED-1 made this independent of any script.

**Assessment.** Nothing in selection needs to change. Operational selection is the same functions called with
`application_snapshot.assignment_inputs` and `.facts` in place of typed values. The fail-closed outcomes already
exist and map naturally onto "do not call":

| Selection outcome | Operational meaning (proposed) |
|---|---|
| resolved, plan READY | a journey can be recorded for the case |
| `PRIMARY_GROUP_MISSING`, `PRIMARY_GROUP_CONFLICT`, `RULE_IN_SEVERAL_GROUPS` | configuration fault — hold for review |
| winner has no published binding | fails closed — hold |
| ambiguous (equal rank) | hold for authorised review (as T-40 does for scripts) |
| input missing / UNKNOWN | hold; never defaulted |
| plan `NOT_READY` (a survey needs a fact that is unknown) | hold, or policy says otherwise (Q-7) |

What is **not** reusable is the record: `survey_assignment_evaluation`, `survey_composite_plan` and the rest carry
`CHECK (record_class = 'SIMULATION')` (`mig/0029`–`0035`). An operational selection must be a **new record**, not a
relaxed check — otherwise a simulation and an operational decision would be indistinguishable in the same table.

## 6. How a selected survey journey could be linked to a case

**Today.** `script_assignment` links a case to one script version with the rule snapshot, trace, inputs and their
hashes; insert-only; "current" means not superseded (`mig/0005:230-252`; `BE/app/domain/script_assignment.py:79-88`).
It never reassigns and refuses terminal case states (`:164-167`).

**Proposed (not built)** — a parallel record, never a column added to `script_assignment`:

```text
survey_journey_assignment            insert-only; record_class = 'OPERATIONAL'
  case_id
  application_snapshot_id + sha256
  selection  (decision, decision_sha256, engine contract)       as recorded for simulation today
  members[]  group, rule version, binding id,
             survey_version_id, content_sha256, manifest_sha256, governed position
  composite fingerprint
  origin (ENGINE / MANUAL_APPROVED), assigned_by, assigned_at, supersedes_id
```

Design points:

* **One conversation source per case.** A case must not hold a current script assignment and a current survey
  journey at once. Proposed: an explicit, immutable `conversation_source` (`SCRIPT` | `SURVEY`) fixed when the first
  assignment is made, enforced by the database.
* **Who decides the source** is the real question. Technically it can be a governed switch per market, per product
  family or per rule; which one is a rollout decision (Q-8).
* **Permission.** Applying a script to a case is `script.assign` (USER only, `mig/0018:29-53`). D-367(d) left this
  unchanged. An operational survey assignment needs its own permission; `script.assign` should not silently cover
  it.
* **Idempotency and replay** should copy `script_assignment_attempt` (`mig/0018:54-85`): an insert-only attempt
  ledger with outcome, hashes, holds placed and released.

## 7. Pinning published survey versions to future conversation sessions

**Today**

* `conversation_session` records `script_version_id`, `script_manifest_sha256`, risk and fact-snapshot pins, and
  `conversation_session_guard` validates and freezes them (`mig/0006:267-300, 592-642`).
* `survey_run` repeats the script pins and must equal the session's (`survey_run_guard`, `mig/0006:645-670`).
* `store.pins_for` takes the latest script assignment whose version is PUBLISHED; without one, session creation
  answers `409 NO_SCRIPT_ASSIGNED` (`BE/app/voice/store.py:52-70`; `BE/app/api/voice.py:393-404`).

**Assessment.** A published survey version already has an exact identity used everywhere in simulation:
`survey_version_id` + `content_sha256` + `manifest_sha256`. Pinning is therefore well defined. The difficulty is
where the pin lives, because the session row and its guard are the most sensitive evidence in the system.

| Option | Description | Assessment |
|---|---|---|
| P-1 | Make the script pins nullable; add survey pins; `CHECK` exactly one family present; extend the guard with a second branch | one session table; touches the guard and every reader of the script pins |
| P-2 (recommended for review) | Keep `conversation_session` script columns as they are for script sessions; add a nullable `survey_journey_assignment_id` + fingerprint, with a `CHECK` that exactly one of the two families is present; per-survey pins live on new survey-run records | historical rows stay valid without rewriting; a journey of several surveys pins once at session level and once per survey |
| P-3 | A separate session table for survey conversations | no shared guard, but duplicates attempts, media and transcript linkage, which are source-neutral today |

Whichever is chosen: **no historical session is rewritten**; existing rows are script sessions by construction. A
journey may contain several surveys, so one session must be able to pin several survey versions in governed order —
a difference from scripts that the review and evidence models inherit (Q-9: one call or several).

This is a change to voice-session creation and is **not** proposed for the next step.

## 8. Operational evidence without overwriting historical Script Studio evidence

**Today** (coupling to scripts in bold)

| Table | Coupling | Mutability |
|---|---|---|
| `contact_attempt`, `session_event`, `media_asset`/`media_chunk`, `transcript_run`/`transcript_segment`, `case_event`, `audit_event` | none | guarded / insert-only |
| `conversation_session`, `survey_run` | **FK `script_version_id` + manifest hash** | pins immutable |
| `question_execution` | **FK `question_revision_id`; the revision must be in the pinned script's manifest** (`mig/0006:673-696`) | frozen when the run is final |
| `answer_observation`, `rule_evaluation` | through the execution | insert-only |
| `finding` | case FK; **nullable** `question_execution_id`; `evidence_refs` JSONB; unique `finding_key` | status and review fields only |
| `review_decision`, `review_approval` | case, finding, `question_execution_id` | insert-only / guarded |

**Assessment**

* The source-neutral half (attempts, session events, media, transcripts, case events, audit) needs **no change**.
* The script-shaped half (`survey_run`, `question_execution`, `answer_observation`, `rule_evaluation`) **cannot hold
  survey evidence**: a survey item is not a question revision and is in no script manifest. Forcing it in would mean
  inventing script rows — a dummy script by another name, which SHARED-1 was built to avoid.
* **Recommended:** parallel operational evidence records for survey execution, keyed to the session and to the
  pinned survey version (item code, item version, placement — the keys `survey_evidence_observation` already uses,
  `mig/0033:158-207`), with `record_class = 'OPERATIONAL'`. Legacy tables keep receiving script evidence only, and
  nothing is back-filled or converted (consistent with B-1, D-357).
* **Findings** are the shared layer. `finding` is keyed to the case; its link to a question execution is already
  nullable. A survey-based finding can be a `finding` row whose `evidence_refs` cite survey evidence, so the Review
  Workbench keeps one list per case. This needs **DEP-FR-1** resolved for question-scoped rules (control-scoped and
  any-question rules already serve both).
* **Simulation evidence has no operational standing.** The `SIMULATION` constraint stays; no simulation record is
  promoted.

## 9. Case holds and voice preflight — new states or new contracts?

**Today**

* Holds are a governed code list: `AWAITING_SCRIPT_ASSIGNMENT`, `AWAITING_SCRIPT_REVIEW`, `RISK_TRIAGE`,
  `NO_ELIGIBLE_CONTACT`, `DATA_CONFLICT` (blocking), `OPERATOR_HOLD` (`BE/app/domain/governed.py:43-50`).
* Intake **always** places `AWAITING_SCRIPT_ASSIGNMENT` (`BE/app/domain/intake.py:502`). A successful script
  assignment releases it; ambiguity places `AWAITING_SCRIPT_REVIEW`
  (`BE/app/domain/script_assignment.py:187-201`).
* Preflight's callable cases require a script assignment with a PUBLISHED version (`BE/app/api/voice.py:169-184`);
  capability `SCRIPT_CONTROLLER` is always `NOT_AVAILABLE` (`:273-279`).
* `23_UC-02_…` §2.4 already separates a *plan* from *eligibility*; the journey trace reports operational eligibility
  as `NOT_ESTABLISHED` always (`BE/app/domain/survey/journey_trace.py:33-36`).

**Assessment**

| Element | New state? | New contract? |
|---|---|---|
| Hold reasons | **Yes, additive.** Reusing `AWAITING_SCRIPT_ASSIGNMENT` for surveys would change the meaning of a governed code already on 258 development cases. Proposed new reasons: awaiting survey assignment; awaiting survey assignment review | the code list is governed — an owner decision |
| Which hold intake places | — | **Yes.** Intake must know the conversation source before it places a hold; that is an intake-contract change (not proposed now) |
| Case states | No. CREATED … CANCELLED describe the case, not the content source | — |
| Preflight response | additive: a capability for the survey plan/controller; `callable_cases` true when the case has a current assignment of **either** source whose pinned content is still published | **Yes**, additive fields; no existing field changes meaning |
| Session creation | a new refusal code beside `NO_SCRIPT_ASSIGNED` (for example no conversation content assigned) | **Yes** |
| Eligibility | the UC-02 contract: plan READY is necessary and not sufficient; eligibility also needs approved content, an approved assignment to the case, no blocking hold, an eligible contact | already written; never implemented operationally |

## 10. Review Workbench and Call Detail with survey-based execution evidence

**Today.** Both read script-specific shapes: `ScriptPin` (`BE/app/api/case_detail.py:115-129`); the survey-run detail
joins `question_revision` and `question_bank_item` (`:932-947`) and reads the script manifest (`:906-918`); review
rebuilds the plan from the pinned script (`BE/app/domain/review.py:207-221`) and checks identity, consent and
recording-consent steps "in the pinned script" (`:330-363`). The frontend links to `/scripts/{family}`
(`FE/src/features/case/CallDetailPage.tsx:195-196, 377`; `FE/src/features/reviews/ReviewCasePage.tsx`). Neither
screen reads any Survey Studio data. The read-only journey trace exists only inside Survey Studio
(`BE/app/domain/survey/journey_trace.py`; `FE/src/features/surveystudio/persist/JourneyPage.tsx`).

**Assessment**

* Present the pinned content as a **discriminated read model**: `conversation_source: SCRIPT | SURVEY`, then either
  today's `ScriptPin`, unchanged, or a journey pin (surveys in governed order, each with version label and
  fingerprints). Existing response fields keep their meaning; survey fields are additive.
* Call Detail and the Review Workbench render one of two evidence panels by source. Historical cases render exactly
  as today. The survey panel can reuse the journey-trace components, which already show selection, plan, items
  delivered, answers, controls and findings for one journey.
* Review **actions** (decisions, approvals) are keyed to case and finding and need no new shape — provided findings
  stay one list per case (§8).
* The lifecycle checks (identity, consent, recording consent) are where policy enters: review code assumes those
  steps exist in the script. What stands for them in a survey is M-3 of `51_…`, undecided.
* Screen naming is unchanged: the screen stays **Call Detail**, route `/cases/:caseId`.

## 11. Rollback, feature flags and mixed legacy/new operation

| Concern | Proposal |
|---|---|
| Flags | one setting per step, off by default, each tied to its migration through `acceptable_migration_heads` (`BE/app/main.py:172-188`) — the pattern used for the eleven survey settings |
| Mixed operation | the norm for a long time: the source is fixed per case and immutable; a case finishes on the source it started with; both paths run side by side |
| Switching new cases back | turn the routing switch off: new cases take the script path. Nothing is deleted |
| In-flight survey cases at rollback | they keep their records; whether they are held, completed, or re-assigned to a script is a policy decision (Q-10) |
| Schema rollback | downgrade guards refuse while operational survey records exist — the rule already applied to bindings, groups, mappings and evaluations |
| Historical evidence | never rewritten or converted in either direction (B-1, D-357) |
| Legacy retirement | not implied. Script Studio stays the operational source until an explicit decision; MIG-2 is separate |
| Simulation | stays available and separate; the same engines serve both, with different record classes |

## 12. Business and Compliance decisions required before activating any operational path

Still open from MIG-1 (D-359), unchanged: **M-1** re-prompt limits; **M-2** conversational delivery; **M-3**
lifecycle steps and what happens when identity, consent or recording consent fails; **M-4** undecidable conditions;
**M-5** which scripts migrate; **B-3** effective dating and withdrawal; **B-4** "evidence required"; **B-5** how long
legacy authoring stays readable; **B-6** standing of two-person approvals; **B-7** protected demonstration records.

New, raised by this assessment:

| | Decision | Owner |
|---|---|---|
| Q-1 | Is an application always exactly one sale event, or can it span several policies or sales? | Business |
| Q-2 | What is a replacement, what is its authoritative source, and is the replaced policy needed? | Business / Compliance |
| Q-3 | Which riders matter for survey selection or control applicability, and their source | Business |
| Q-4 | Definitions: annual premium for a single premium; premium term versus policy term; customer age (whose, at which date) | Business |
| Q-5 | Approval of the mapping from source fields to survey facts, and who owns each fact | Business / Compliance |
| Q-6 | When source data changes after selection: re-select, hold, or continue | Compliance |
| Q-7 | May a call proceed when a survey needs a fact that is unknown | Compliance |
| Q-8 | Rollout unit and order: by market, product family or rule; and who switches it | Business |
| Q-9 | A journey of several surveys: one call or several; the order; what a partly completed journey means for the case outcome | Business / Compliance |
| Q-10 | Treatment of in-flight survey cases if the path is switched off | Compliance |
| Q-11 | Who may assign a survey journey to a case, and whether an approved manual assignment exists | Business |
| Q-12 | What makes survey content callable: every survey, fact and wording is `SYNTHETIC_UNAPPROVED` today, and no fact is speakable | Compliance |
| Q-13 | Reviewer procedure and finding severity for survey-based evidence; DEP-FR-1 (question identity for finding rules) | Compliance |
| Q-14 | Retention and access for survey-based operational evidence | Compliance |
| Q-15 | Whether rule governance (two people) and survey governance (three people) should be harmonised before rules drive real cases | Business |

## 13. What can be built technically, and what needs approved customer-call policy

| Step | Purely technical | Needs approved policy first |
|---|---|---|
| Derive rule inputs and mapped survey facts for a case, read-only | **Yes** | the mapping itself is synthetic until Q-5 |
| Show what the governed rules would select for a real (synthetic) case, storing nothing | **Yes** | — |
| A governed, versioned mapping artifact with its own lifecycle | **Yes** | its content: Q-2…Q-5 |
| Persisted application snapshot | Yes | Q-1, Q-6 |
| New source fields (replacement link, riders, sum assured in the snapshot) | Yes, with an intake-contract change | Q-2…Q-4 |
| Operational journey assignment record | Yes | Q-8, Q-11 |
| New hold reasons; intake places a different hold | Yes | Q-8; the hold code list is governed |
| Preflight and session pin for surveys | Yes | Q-9, Q-12, M-3 |
| Operational survey evidence and findings | Yes | Q-13, Q-14, DEP-FR-1, M-1…M-4 |
| Review Workbench and Call Detail panels | Yes | Q-13, M-3 |
| A live controller speaking survey items | Yes (VOICE-1) | M-1, M-2, M-3, Q-12 and everything above |

### Proposed next implementation boundary — APP-1a, read-only application view

**In scope (proposed, not authorised):**

1. A versioned **mapping** from the existing fact snapshot and risk assessment to (a) the nine rule inputs — exactly
   as `rule_inputs.case_inputs` produces them today — and (b) the survey facts that have a real source. Marked
   synthetic and unapproved. Facts without a source are listed as unmapped; none is invented.
2. A **stateless** derivation of the application view for one case: values, per-value lineage, the hash, the unmapped
   list. Nothing is stored.
3. A read-only **"what would be selected"** preview for that case, using the existing selection and composition
   functions unchanged, shown inside Survey Studio only and labelled simulation.
4. Tests that the derived rule inputs are identical to what operational script assignment reads today for every
   case, so the two can never drift.

**Out of scope:** any persisted snapshot or assignment; any change to intake, holds, `script_assignment`, voice
preflight, session creation, evidence tables, the Review Workbench or Call Detail; any new rule field; any new source
field; any migration unless a mapping table is wanted (it can start as a governed constant, like the first control
register).

**Why this boundary:** it turns `INPUT_CONSISTENCY` and `LINEAGE` from `UNVERIFIED` into something checkable, it
exposes exactly which business definitions are missing using real synthetic cases, and it writes nothing
operational — so it needs no customer-call policy. Every later step depends on it.

**Not recommended as the next step:** an operational journey assignment (even a "shadow" one). It would create
case-linked records before Q-8 and Q-11 are answered, and it would need the conversation-source rule of §6.

## 14. What this assessment did not do

* It changed no code, schema, intake hold, assignment or voice-session behaviour.
* It did not inspect the GPT-Live provider path or Voice Lab.
* Development contents were not re-counted for it; the inventories in `51_…` §1.4 and in
  `evidence/SHARED-1/dev-migration-0037/` are the current ones.
* It proposes names and shapes for discussion. None is a contract until a design is authorised.
