# MIG-1 — Script Studio retirement readiness: assessment

**Status: ASSESSMENT ONLY, written 2026-11-23, presented for the owner's review. Nothing here is decided or built.**
Authorisation: the owner's message "Accept LIB-2, Enable Development 0036, and Authorize MIG-1 Assessment" (D-351):
"a documentation, dependency-discovery and architecture assessment checkpoint only. Do not retire Script Studio or
migrate its data."

For MIG-1 **no application code, migration, script table or script record was changed.** The development database was
read (read-only transactions) for the inventory in §1.4. Evidence: `docs/acceptance/evidence/MIG-1/`.
**Synthetic data only.** Every script, wording, rule and control discussed is synthetic and unapproved.

**How this was established.** Two read-only inventories of the code (backend; frontend and specifications), then the
load-bearing claims re-checked in the source by hand, and the development database queried for what actually exists.
File and line references are to the repositories as they stood on 2026-11-23.

---

## 0. The answer in one page

**Can Survey Studio replace Script Studio as the only conversation-authoring platform?** As an *authoring* tool, very
nearly: it is the stronger editor and governance model, and nothing in it depends on Script Studio's screens. **But
Script Studio cannot be retired today, and the reasons are not about the editor.** There are four:

1. **A new assignment rule cannot exist without a published script.** A rule version must target a published script
   version (`rule_authoring.py:437-448`, a NOT NULL foreign key, and a database trigger), and a rule's *market* is
   read from that script's family (`rule_inputs.py:292`, `survey/assignment.py:115, 416`). Survey Studio's own
   assignment is, by the owner's ruling D-246, "an interim adapter" that binds a survey to such a rule. Remove script
   publication and no new rule can ever be written — for surveys either.
2. **Only a script can be assigned to a case.** Every case is created on hold `AWAITING_SCRIPT_ASSIGNMENT`
   (`intake.py:502`); only the script assignment engine releases it; a voice session starts only for a case whose
   assignment points at a `PUBLISHED` script version (`voice/store.py:60`). No survey table references a case, a
   session or an assignment. **Survey Studio has no operational path at all** — it is simulation-only by every
   acceptance on record.
3. **The historical evidence is bound to script records by the database.** In development: 251 script assignments,
   95 sessions, 82 survey runs, 555 question executions, 26 findings (every one tied to an execution), 5 review
   decisions. Sessions and runs carry a foreign key to `script_version` and its manifest fingerprint; each execution
   carries a foreign key to `question_revision`; triggers verify those pins. Those tables cannot go, and the code
   that reads a manifest must stay for the history to remain readable.
4. **Nine capabilities have no equivalent yet, and five need a business decision** (§2): re-prompt limits, what
   happens when a consent or identity step fails, conversational delivery, saved scenarios and batch regression,
   effective dating, evidence-required, and the operational assignment above.

**So the realistic end state is not "delete Script Studio".** It is: Survey Studio is where conversations are designed;
Assignment Rules and Finding Rules are shared services that stand on their own; the script *editor* goes read-only and
then away; and the script *records* that operational history points at stay, readable, for as long as that history
matters.

**One conflict with earlier rulings must be settled first (B-1, §8).** D-156 (AD-2) approved "Re-seed instead of
preserving every legacy development record… No legacy loader, evaluator or conversion path is to be built", and D-154
set the goal to "eventually remove Script Studio completely, including… database structures". This brief asks for a
controlled content migration (MIG-2), historical evidence verification (MIG-3) and preservation of historical and
operational services (MIG-5). Those cannot both stand. This assessment follows the newer brief and does not treat the
older rulings as withdrawn until the owner says so.

**Recommended next checkpoint: SHARED-1** — make Assignment Rules and Finding Rules independent of script authoring
(§9). It is the smallest change that removes the hardest coupling, it is additive, and every later gate needs it.

---

## 1. Inventory of Script Studio

### 1.1 Screens (frontend)

| Route | Component | Permission | Kind |
|---|---|---|---|
| `/scripts` | `features/scripts/ScriptLibraryPage.tsx` | `script.read` | **Authoring UI** — library, filters, create |
| `/scripts/:scriptFamilyId` | `ScriptFamilyPage.tsx`, `ScriptEditor.tsx` | `script.read`; `script.edit` / `.approve` / `.publish` to act | **Authoring UI** — questions, versions, review and publish, compare, history |
| `/assignment-rules`, `/assignment-rules/:ruleCode` | `AssignmentRulesPage.tsx`, `features/rules/*` | `script.read`; edit/approve/publish; `script.assign` for batch | **Shared service UI** |
| `/finding-rules` | `features/findings/FindingRulesPage.tsx` | `script.read`; edit/approve/publish | **Shared service UI** |
| `/simulator` | `features/simulator/*` | `script.read`; `script.simulate` to run | Verification UI on the script engine |
| `/reviews`, `/reviews/cases/:caseId` | `features/reviews/*` | `queue.read`; `review.decide`, `review.approve` | **Operational** |
| `/cases/:caseId` (Call Detail) | `features/case/*` | `case.read` | **Operational** — shows the pinned script, why, results, findings |
| `/voice-studio`, `/voice-lab` | `features/voice*` | voice permissions | Operational / lab — read the pin; import script questions into datasets |

There is no standalone question-bank screen: the bank is reached only from inside the script editor. Survey Studio's
code imports nothing from these features; it only links to them (`RulesExplorer.tsx:85, 186, 191`;
`SimulationHub.tsx:69-73`; `AssignmentPage.tsx:118`).

### 1.2 Backend operations

| Router | Authoring | Read | Operational / simulation |
|---|---|---|---|
| `api/script_authoring.py` | create script, new draft, sections and questions (add, edit, remove, reorder), control links, validate, submit, abandon (`script.edit`); review (`script.approve`); publish (`script.publish`) | history, diff, question bank, options | — |
| `api/scripts.py` | — | library, family, versions, recorded rules, regulatory references, controls | — |
| `api/assignment_rules.py` | create, draft, save, validate, submit, abandon; review; publish | registry, draft, history, diff, explain, simulate | — |
| `api/script_assignments.py` | — | preview | apply to a case; batch run (`script.assign`) |
| `api/finding_rules.py` | create, save, submit, abandon; review; publish | options, list, read | — |
| `api/script_simulations.py`, `api/simulation_workbench.py` | scenarios (`script.simulate`) | plans, runs, evaluations, findings | interactive runs, batch runs, evaluation, simulated findings |
| `api/review_workbench.py`, `api/reviews.py` | — | queue, cases, approvals | dispositions, decisions, approvals |
| `api/case_detail.py` | — | case, assignment, findings, session, survey run, **script version** | — |
| `api/voice.py`, `api/voice_lab.py` | — | preflight; script sources | start a session (pins the script); import script questions |

Legacy routers are always registered (`main.py`, `ROUTERS`); survey routers only with their settings.

### 1.3 Database

**Authoring content** (`0005`, `0015`, `0016`, `0020`): `script_family`, `script_version` (manifest and SHA-256,
status, effective dates, author ≠ reviewer), `script_section` (inclusion condition), `script_module`,
`module_question` (branch condition), `question_bank_item`, `question_revision` (insert-only: wording, delivery mode,
answer type, mandatory, evaluation policy, expected value, re-prompts, evidence required…), `question_revision_detail`
(lifecycle role, on-failure, discloses, deliver-on-termination), `script_change_event`,
`script_version_control_link`.

**Shared with Survey Studio**: `script_assignment_rule_version` (+ `assignment_rule_draft`,
`assignment_rule_change_event`, `assignment_rule_publication`), `finding_rule_set_version` (+ `_event`), `control`,
`control_mapping`, `regulatory_reference`.

**Verification records** (not operational evidence, by design): `script_simulation_run`, `script_simulation_event`,
`simulation_scenario`, `simulation_scenario_revision`, `simulation_content_snapshot`, `simulation_batch`,
`simulation_result`, `simulation_answer_evaluation`, `simulation_finding_set`, `simulation_finding`.

**Operational and historical** (`0006`, `0018`, `0024`): `script_assignment`, `script_assignment_attempt`,
`conversation_session`, `survey_run` (the operational run — *not* a Survey Studio table), `question_execution`,
`answer_observation`, `rule_evaluation`, `finding`, `review_decision`, `review_approval`, `case_event`, `audit_event`.

### 1.4 What development actually holds (read 2026-11-23)

| | |
|---|---|
| Script families / versions | 7 / 11 — 4 `PUBLISHED`, 1 `SUPERSEDED`, 1 `WITHDRAWN`, 5 `DRAFT` |
| Versions with operational history | `SALES_VERIFICATION_SG 1.1` (169 cases, 56 sessions, 43 runs), `SALES_VERIFICATION_MY 1.0` (54 / 22 / 22), `SALES_VERIFICATION_SG 1.0` superseded (25 / 15 / 15), `SG_LIFECYCLE_DEMO 1.0` (3 / 2 / 2) |
| Protected by earlier owner restrictions | `SG_LIFECYCLE_DEMO 1.1` (draft), `SG_EVALUATION_DEMO 1.0` (draft), rule `S2D1-LIFECYCLE-DEMO` |
| Question revisions | 39: yes/no 18, acknowledgement 11, free text 4, numeric 4, choice (`ENUM`) 2 |
| Delivery | conversational **28**, controlled TTS 11, exact audio 0 |
| Evaluation method | acknowledgement 11, exact boolean 11, collect only 9, numeric match to a policy fact 4, narrative review 3, choice match to a policy fact 1 |
| Flags | mandatory 36; **re-prompt limit set on all 39**; evidence required 18; acceptable variants 0; unacceptable outcomes 0; escalation reference 0; not-applicable condition 1 |
| Lifecycle roles | opening, identity check (4), disclosure, consent to proceed, recording consent, cloud-processing consent, closing — each with an on-failure behaviour (terminate, continue, continue without recording…) |
| Conditions | 16 of 40 sections have an inclusion condition; **0 of 46** placed questions have a branch condition |
| Assignment rules | 8 versions (4 published); every one targets a script version; 3 survey bindings hang off two of them |
| Script assignments | 251 — 245 seeded, 6 by the engine |
| Finding rule sets | 1 published (SG, 6 rules) |
| Executions | 555, referring to 24 distinct question revisions; 26 findings, all tied to an execution; 5 review decisions |
| Saved scenarios / batches | 4 active scenarios, 3 batches |

### 1.5 Classification

| Class | What |
|---|---|
| **A. Authoring UI and its write paths** — retirable once content can be authored elsewhere | the script library and editor; `api/script_authoring.py` writes; the mutators of `domain/script_authoring.py`; `script_change_event` writes |
| **B. Shared authoritative services** — must remain, whatever happens to the UI | `rule_engine`, `rule_inputs`, `rule_authoring`; `answer_evaluation`; `finding_engine`, `finding_rules`; the rule, finding-rule and control tables; their APIs and screens |
| **C. Operational necessity** — the only path to a real case today | the script assignment engine and its APIs; the hold on intake; the voice pin; Review Workbench; Call Detail |
| **D. Historical records and their readers** — must remain readable | every table of "Operational and historical" above; the script content rows they point at; `script_authoring.content_of`, `build_manifest`, `link_rows`, `makers`; `question_controller.build_plan` (used by review); `outcomes`, `kpis`, the registers |
| **E. Verification on the script engine** | Simulation Workbench, scenarios, batches, script-side evaluation and simulated findings |

---

## 2. Feature parity — Script Studio against Survey Studio

Evidence is the code or contract that shows it, not the name of a screen. "SS" = Survey Studio; "§n" = contract
`04_…`. Counts are from §1.4.

### 2.1 Content and authoring

| # | Capability | Script Studio | Survey Studio | Parity |
|---|---|---|---|---|
| 1 | Reusable modules | `script_module`, reused across versions | modules in the component library; standalone modules (LIB-2) | **FULL** — stronger |
| 2 | Question bank and reuse | `question_bank_item` / insert-only `question_revision`; bank picker in the editor | items and wording versions; library; exact pinning by fingerprint | **FULL** — stronger |
| 3 | Yes/no, free text, numeric, acknowledgement | `answer_type` | `ANSWER_TYPES` (`documents.py`) | **FULL** |
| 4 | Choice from a list | `ENUM`, options in `answer_schema` | `SINGLE_SELECT` with an option set | **FULL** — a transformation, not a loss |
| 5 | Several answers from a list | not supported (`model/contract.ts:81`) | `MULTI_SELECT`, follow-ups, ordered rules | **NOT APPLICABLE** — SS only |
| 6 | Statements (opening, disclosure, transition, closing) | lifecycle-role questions with acknowledgement | `STATEMENT` items with a statement role | **PARTIAL** — different shape; see 14 |
| 7 | Exact customer wording | `customer_wording` | wording versions, frozen and fingerprinted | **FULL** |
| 8 | Delivery mode | conversational, controlled TTS, exact audio | the same three, **but a candidate may not contain conversational** (`DELIVERY_CONVERSATIONAL_BLOCKED`, TS-4) | **REQUIRES BUSINESS DECISION** — 28 of 39 revisions are conversational |
| 9 | Mandatory question | `mandatory` column, enforced by the controller | `response_obligation` — a synthetic placeholder catalog; meaning awaits D-NA-5, D-NA-10 | **PARTIAL** |
| 10 | Re-prompt limit | `max_reprompts`, set on all 39 | none — no retry limit is approved (D-NA-8) | **NOT SUPPORTED · REQUIRES BUSINESS DECISION** |
| 11 | Clarification wording | not in the editor | blocked, shown as unavailable | **NOT APPLICABLE** — neither has it |
| 12 | Section included only when… | `inclusion_condition`, AND-only over five facts and risk band | eligibility condition: AND / OR / NOT, parameters, and an explicit policy for *unknown* | **PARTIAL** — SS is richer, but `is_ilp`, `premium_frequency` and risk band are not in its field catalog, and legacy states no unknown policy |
| 13 | Ask a question only when… | `branch_condition` (0 in use) | decisions and per-answer routes | **FULL** |
| 14 | Lifecycle roles and what happens on failure | role + `on_failure` (terminate, continue without recording…); gates in `lifecycle.py` | four lifecycle roles declared; **no on-failure behaviour**; a refused acknowledgement stops as `POLICY_UNRESOLVED` | **PARTIAL · REQUIRES BUSINESS DECISION** (UC-D-5; consent-refusal behaviour is not to be invented) |
| 15 | "Discloses policy information", "deliver on termination" | flags (1 and 2 in use) | none | **NOT SUPPORTED** |
| 16 | Expected answer and evaluation method per question | `expected_answer_policy`, expected value, policy fact key, tolerance | not on the question: in governed **control mappings** (EVAL-1), evaluated by the same `answer_evaluation` engine | **PARTIAL** — same engine, different owner of the rule |
| 17 | Control and regulatory links | `control_mapping`, per-draft links | control mappings and control policies (to `control`); nothing refers to `regulatory_reference` | **PARTIAL** |
| 18 | Evidence required | flag, 18 in use | none | **NOT SUPPORTED** — its consumer must be confirmed first |
| 19 | Acceptable variants, unacceptable outcomes, escalation reference | fields; **0 in use** | none | **NOT APPLICABLE** on current data; confirm no consumer |
| 20 | Controlled variables in wording | none | governed, default-deny (no field is speakable) | **NOT APPLICABLE** — SS only |
| 21 | Languages | English only | English only (AD-12) | **FULL** |
| 22 | Visual editing | forms and lists | guided builder and live graph | **FULL** — stronger |
| 23 | Library search and filters | server-side, by status, language, product, risk band, channel | workspace search in the browser | **PARTIAL** |

### 2.2 Governance

| # | Capability | Script Studio | Survey Studio | Parity |
|---|---|---|---|---|
| 24 | Draft, validation, submission | yes; manifest frozen at submit | yes; immutable candidate, manifest of every pinned version | **FULL** — stronger |
| 25 | Separation of duties | maker ≠ checker (two people; one role holds approve and publish) | maker ≠ approver ≠ publisher (three), enforced by a database trigger | **FULL** — stricter. *An approval given under the two-person rule is not an approval under the three-person rule* |
| 26 | Immutability of what is published | trigger on `script_version` | frozen assets, insert-only candidates and versions | **FULL** |
| 27 | Compare versions; change history | semantic diff; event history | candidate changes; revision comparison; lifecycle history | **FULL** |
| 28 | Effective dating | `effective_from` / `effective_to` on versions and rules; validity checked when pinned | `effective_from` recorded only; nothing takes effect on a date (D-165) | **PARTIAL · REQUIRES BUSINESS DECISION** |
| 29 | Withdrawal | status `WITHDRAWN` exists (1 version) | none; open (P-5) | **NOT SUPPORTED · REQUIRES BUSINESS DECISION** |
| 30 | Acknowledging mandatory questions without a control | at review | acknowledged warnings at submission | **PARTIAL** — a different warning |

### 2.3 Assignment, execution, verification, operations

| # | Capability | Script Studio | Survey Studio | Parity |
|---|---|---|---|---|
| 31 | Assignment rules — authoring | here, and only here | none: it binds surveys to these rules | **NOT SUPPORTED** — by design a shared service; see §3 |
| 32 | Choosing content for an application | one script version per case | a governed binding, requirement groups, a composite plan of several surveys | **PARTIAL** — SS is richer but for **synthetic applications only** |
| 33 | Assigning to a real case; releasing the hold | the script assignment engine | none | **NOT SUPPORTED** |
| 34 | Pinning to a session and a run | `script_assignment` → session → `survey_run` → execution, checked by triggers | none | **NOT SUPPORTED** |
| 35 | Running a live call | neither: the voice session plays a fixed message; the script controller is used by simulation and review only | neither: simulation only | **NOT APPLICABLE** — neither has it |
| 36 | Interactive simulation | on a synthetic case with its facts | on a fact snapshot, by the Python engine; replay and drift detection | **PARTIAL** — different inputs |
| 37 | Saved scenarios, batch runs, version comparison, coverage | Simulation Workbench | none saved; coordinated simulation of one application | **NOT SUPPORTED** |
| 38 | Call-plan preview | none | yes | **NOT APPLICABLE** — SS only |
| 39 | Answer evaluation | per question, on a simulation | per control, on a journey; coverage; control policies | **PARTIAL** — same engine, different grain |
| 40 | Findings from rules | simulated and operational | on evaluations, from the same published rule set | **PARTIAL** — a rule scoped to a `QUESTION` names a script question code, which no survey item carries |
| 41 | Execution assurance | none | yes (EVAL-2B) | **NOT APPLICABLE** — SS only |
| 42 | Review, dispositions, approvals | Review Workbench | none, by ruling: evaluation creates no disposition | **NOT APPLICABLE** — operational, stays separate |
| 43 | Call Detail: script, rationale, results | yes | none | **NOT SUPPORTED** |

**Count, of 43 capabilities:** FULL 12 · PARTIAL 13 · NOT SUPPORTED 9 · NOT APPLICABLE 8 · REQUIRES BUSINESS DECISION
alone 1. Five rows carry a business decision (8, 10, 14, 28, 29); row 12 carries one more for the unknown policy.

---

## 3. Dependency analysis

### 3.1 Diagram

```
                         ┌──────────────────────────── AUTHORING ────────────────────────────┐
                         │  Script Studio (legacy)                 Survey Studio             │
                         │  script_family / script_version         survey_definition (SURVEY │
                         │  section / module / question_revision    | MODULE), assets,       │
                         │        │ PUBLISHED version               candidates, versions     │
                         └────────┼──────────────────────────────────────────┬──────────────┘
                                  │ target (NOT NULL FK, must be published)  │ binding (FK)
                                  ▼                                          ▼
   ┌─────────────────────── SHARED AUTHORITATIVE SERVICES ───────────────────────────────────┐
   │  Assignment Rules: rule_engine · rule_inputs · rule_authoring                            │
   │     script_assignment_rule_version ◄── survey_assignment_binding / _evaluation /         │
   │                                         _group_member / composite_plan_member (4 FKs)    │
   │     market of a rule = market of its target script family                                │
   │  Evaluation: answer_evaluation  ◄── script simulation AND survey control evaluation      │
   │  Findings:   finding_engine · finding_rules · finding_rule_set_version                   │
   │                                  ◄── simulated findings AND survey evaluation (2 FKs)    │
   │  Controls:   control ◄── control_mapping (script) AND survey_control_mapping (3 FKs)     │
   └───────────┬──────────────────────────────────────────────────────────────┬──────────────┘
               │ script assignment engine                                     │ synthetic applications only
               ▼                                                              ▼
   ┌──────── OPERATIONS (real cases) ────────┐                ┌──── SIMULATION & EVALUATION ────┐
   │ callback_case ─ hold AWAITING_SCRIPT_…  │                │ survey_simulation, call plans,  │
   │ script_assignment (version + manifest)  │                │ composite plans, evaluations,   │
   │ conversation_session (pin, trigger)     │                │ assurance, journey trace        │
   │ survey_run (pin = session's)            │                │ (no reference to a case,        │
   │ question_execution → question_revision  │                │  session or assignment)         │
   │ answer / rule_evaluation / finding      │                └─────────────────────────────────┘
   │ review_decision / review_approval       │
   └───────────┬─────────────────────────────┘
               ▼
   Call Detail · Review Workbench · KPIs / outcomes / registers · Voice (pin, preflight) · Voice Lab import
```

### 3.2 Who depends on what

| Depended on | By | How (evidence) |
|---|---|---|
| **Script definitions and versions** | assignment rules | `target_script_version_id` NOT NULL FK; trigger "target must not be DRAFT"; publish refuses `NO_TARGET`, `TARGET_NOT_PUBLISHED` (`rule_authoring.py:437-448`) |
| | the market of every rule — and so of every **survey** binding | `rule_inputs.py:292`; `survey/assignment.py:115, 416` join rule → script version → script family |
| | voice | a session starts only for a case assigned a `PUBLISHED` version (`voice/store.py:60`); `conversation_session_guard` checks validity and the manifest checksum |
| | Call Detail, Review Workbench, KPIs, registers | read the manifest through `script_authoring.content_of` / `build_manifest`; review builds the plan with `question_controller.build_plan` |
| | Voice Lab | imports script questions into datasets (`voice/lab.py:390-441`) |
| | Simulation Workbench | scenarios, batches and runs carry FKs to script versions |
| **Script assignments** | case intake | every case is held until one exists (`intake.py:502`, `script_assignment.py:38`) |
| | sessions, runs | the pin is copied from the assignment and re-checked by triggers |
| **Script execution events** (`question_execution` and what hangs off it) | findings, review decisions | FKs; every one of the 26 findings is tied to an execution |
| | KPIs and outcomes | `outcomes.py:63-110`, `kpis.py:166-177` |
| **Finding-rule references** | simulated and operational findings | `simulation_findings`, `review` |
| | survey evaluation | `survey_evaluation_finding`, `survey_obligation_finding` FKs; `journey_evaluation.py:26-28` |
| | *a rule of scope `QUESTION`* | names a **script question code** — the one place a finding rule reaches into script content |
| **Control mappings** | script questions (`control_mapping` by question concept) | separate from `survey_control_mapping`, which maps survey items. Both point at the same `control` rows |
| **Operational case records** | Review Workbench, Call Detail, search, dashboards | unchanged by anything here |
| **Review decisions** | `review_decision` → finding, question execution, case (insert-only) | history; must stay readable |
| **Historical audit evidence** | `audit_event` action families `SCRIPT.*` (55), `RULE.*` (21), `FINDING_RULES.*` (10), `SIMULATION.*` (35), `REVIEW*` (6) | no FK; meaningful only while the records they name still exist |

### 3.3 Exactly what breaks if Script Studio authoring, or its APIs, were removed

| # | Contract | Breaks when | Consequence |
|---|---|---|---|
| X-1 | `POST /assignment-rule-drafts/{id}/publish` requires a published `target_script_version_id` | no script can be published any more | rules can only ever target scripts that already exist; a new market or a rule for new content is impossible; **Survey assignment stops growing** |
| X-2 | rule market = target script family's market | the script tables are removed | every rule loses its market; survey bindings, groups and composite plans fail |
| X-3 | four survey FKs to `script_assignment_rule_version` | the rule table is removed or re-keyed | governed bindings and recorded assignment evaluations are orphaned |
| X-4 | `voice/store.pins_for`, `GET /voice/preflight`, `conversation_session_guard` | no case has a published script assignment | no voice session can start |
| X-5 | hold `AWAITING_SCRIPT_ASSIGNMENT` | the script assignment engine is removed | every new case stays on hold for ever |
| X-6 | `GET /cases/{id}`, `/cases/{id}/script-assignment`, `/survey-runs/{id}`, `/script-versions/{id}`, `/sessions/{id}` | script content rows or `script_authoring` readers are removed | Call Detail cannot show what was asked, by which version, or why |
| X-7 | Review Workbench (`review.py` uses `question_controller.build_plan`, `script_authoring`) | those modules are removed | open reviews cannot be worked; history cannot be read |
| X-8 | `survey_run_guard`, `question_execution` guard (revision must be in the pinned manifest) | `script_version` / `question_revision` are dropped | the database refuses; historical rows would be invalid |
| X-9 | finding rule sets and assignment rules are gated by `script.read` / `.edit` / `.approve` / `.publish` | the `script.*` permissions are retired with the editor | nobody can maintain rules that Survey Studio depends on |
| X-10 | `finding_rules` scope `QUESTION` → `question_code` | script questions are no longer authored | such rules can only name questions that already exist |
| X-11 | `control` has no authoring of its own; links are made in the script editor (`PUT …/questions/{code}/controls`) | the editor goes | controls can still be read by Survey Studio, but nothing maintains the register |
| X-12 | `/voice-lab/script-sources`, `import-script` | script reads are removed | Voice Lab loses its question source |
| X-13 | the generated OpenAPI client | any operation is removed | a breaking contract change under `API_CONTRACT_POLICY.md`; the frontend build fails until regenerated |
| X-14 | tests | — | survey tests build rules with legacy helpers (`test_survey_assignment.py:32-33`), publish finding rules through `finding_rules`; four persisted browser journeys create rules through the legacy API against `SALES_VERIFICATION_SG v1.1`; `f6`, `f7`, `cp06` and nine `*.spec.ts` files cover the legacy screens |
| X-15 | navigation and guards | `script.read` is retired | Assignment Rules, Finding Rules and Simulation Workbench disappear from the sidebar; the prototype Survey Studio route is guarded by `script.read` |

### 3.4 Authoritative services that must remain after the legacy UI is retired

`rule_engine`, `rule_inputs`, `rule_authoring` and their tables and API · `answer_evaluation` · `finding_engine`,
`finding_rules` and their table and API · `control`, `control_mapping`, `regulatory_reference` · the script
assignment engine and `script_assignment*` **until an operational replacement exists** · every operational and
historical table · the read side of `script_authoring` (`content_of`, `build_manifest`, `link_rows`, `makers`) and
`question_controller.build_plan` · `outcomes`, `kpis`, the registers · Review Workbench · Call Detail.

---

## 4. Migration feasibility

**Can the published scripts be represented by Survey Studio's canonical documents without changing their business
meaning?** *Structurally yes. Semantically, not without five decisions.* Nothing was converted; this is analysis.

### 4.1 Mapping

| Script side | Survey side | Transformation | Meaning preserved? |
|---|---|---|---|
| `script_family` | a survey definition | code and name carry over (the code pattern allows it) | yes |
| `script_version` (label `1.1`) | a published survey version (label `n.0`, generated) | **labels cannot be kept** — a mapping record is needed | yes, with the mapping |
| `script_section` → `script_module` (code, revision) | a placement of a module revision | a linear module becomes nodes joined "everybody continues"; one ending, `COMPLETED` | yes |
| module code (`COMMON_SALES_CONDUCT`) | module code `M-<n>` | **with the library on, codes are issued by the server** — the old code survives only as provenance | identity changes; needs a mapping record |
| `question_bank_item` + `question_revision` n | item version n + wording version n | one-to-one; the question code becomes `Q-<n>` (same remark) | yes |
| answer type `ENUM` + `answer_schema` | `SINGLE_SELECT` + an option set | options become an answer set with codes | yes |
| lifecycle-role acknowledgement (opening, disclosure, closing) | `STATEMENT` with a statement role — *or* an acknowledgement item | a choice: a statement takes no answer; today's rows expect an acknowledgement | **decision M-3** |
| `inclusion_condition` | a condition asset + an eligibility binding | AND-only → AND group; **`unknown_policy` has no source** | **decision M-4**; and three facts are not in the survey field catalog |
| `not_applicable_predicate` (1) | a decision node | — | yes |
| `mandatory` | `response_obligation: MANDATORY` | the catalog entry is a synthetic placeholder | **not until D-NA-5 / D-NA-10** |
| `max_reprompts` (39) | — | dropped | **no — decision M-1** |
| delivery `CONVERSATIONAL` (28) | not publishable | must become controlled TTS, or stay unpublished | **no — decision M-2** |
| `on_failure`, discloses, deliver-on-termination | — | `TERMINATE` could be a route to an outcome, but *which* outcome is policy | **no — decision M-3** |
| `expected_answer_policy`, expected value, policy fact, tolerance | a control-mapping entry per control | from a property of the question to a governed mapping; needs a control for each | meaning kept only where a control exists |
| `evidence_required` (18) | — | dropped | **unknown — its consumer must be confirmed** |
| `control_mapping` (question → control) | `survey_control_mapping` | re-proposed and re-approved in Survey Studio | yes, after approval |
| approval of the script version | — | **cannot be carried**: two-person approval ≠ three-person. Migrated content is a new draft that three people must take through review | governance is re-done, not inherited |

### 4.2 What does not transfer at all

- **Assignment references.** 251 assignments, and the four published rules, name script versions. A migrated survey
  is a different record with a different fingerprint. Nothing can be re-pointed without rewriting evidence — and
  evidence is not rewritten. Old cases stay on their scripts.
- **Evaluation and findings compatibility.** The engines are shared, so results are comparable in kind; but a finding
  rule scoped to a script question code does not reach a survey item, and an evaluation rule moves from the question
  to a control mapping. Equivalence must be *demonstrated* per script (MIG-3), not assumed.
- **Executions.** 555 executions point at 24 question revisions. They stay where they are.

### 4.3 Historical preservation

The rule is the one the specifications already state (`SCRIPT_GOVERNANCE_AND_ASSIGNMENT.md`, "the key business rule"):
*the approved version and its selection decision must be recoverable for each case and run, even after questions are
modified or removed.* Therefore:

1. No operational or historical table is dropped, renamed or re-keyed by any gate below.
2. The script content rows that history points at are **retained read-only**, whatever happens to the editor.
3. A migrated survey records where it came from (`authoring.derived_from` already exists for this) and a mapping
   table records old identity → new identity. Neither replaces the original.
4. Fingerprints of the retained rows are taken before and after every gate (the method used for `0036`, §10 of
   `50_…`).

### 4.4 Rollback and dual running

- **Dual running is unavoidable** between MIG-2 and MIG-5: old cases on scripts, new content in surveys. It is safe
  because the two stores do not write to each other; the risk is confusion, not corruption — hence the "Legacy" tag,
  and a single place (Assignment Rules) deciding which one a new application gets.
- **Rollback** of MIG-2 and MIG-3 is a setting and a code revert: nothing legacy is changed. MIG-4 is a permission
  change, reversible. MIG-5 removes screens and routes, reversible by a code revert as long as no table is touched —
  which is why no gate touches one.

---

## 5. Retirement gates

Every gate: additive or reversible; evidence in `docs/acceptance/evidence/`; stops for the owner's review.

### MIG-2 — Controlled content migration

| | |
|---|---|
| **Enter when** | decisions M-1…M-5 and B-1 are ruled; SHARED-1 is accepted (a rule can exist without a script); the mapping specification is approved |
| **Does** | for each published script the owner names: produce the equivalent survey as a **draft**, with provenance and an identity-mapping record; three people review and publish it like any survey. Scripts are not changed |
| **Regression** | full backend, golden runs and plans unchanged, the three browser suites; the legacy suites untouched and green |
| **Security** | migration runs as a named actor with `survey.edit`; it can neither approve nor publish what it made; market scope preserved; audit event per migrated artifact |
| **Business acceptance** | the owner signs each migrated survey as *meaning the same* as its script, with the listed differences (M-1…M-3) acknowledged in writing |
| **Compatibility** | no API removed; no script table written |
| **Recovery** | discard the drafts (never published) or supersede the published survey; the script is still there |

### MIG-3 — Behavioural parity and historical evidence verification

| | |
|---|---|
| **Enter when** | MIG-2 accepted for the scripts in scope |
| **Does** | for each migrated pair: the same synthetic applications through both engines; compare what is asked, in what order, what is refused, how it ends, what is evaluated and which findings result; **differences are listed, never reconciled silently**. Separately: every retained historical row re-read and its fingerprint compared with the pre-migration inventory; Call Detail and Review Workbench opened on historical cases |
| **Regression** | as MIG-2, plus the parity suite itself, kept as a permanent test |
| **Security** | read-only on operational data; no real customer data (there is none) |
| **Business acceptance** | Compliance accepts each remaining difference or it blocks |
| **Compatibility** | none removed |
| **Recovery** | nothing to recover: it changes nothing |

### MIG-4 — Legacy authoring becomes read-only

| | |
|---|---|
| **Enter when** | MIG-3 accepted; **an operational path for surveys exists** (OPS-1, §9) or the owner rules that no new case needs one; assignment rules and finding rules have their own permissions (SHARED-1); nothing in flight in script review |
| **Does** | script create, edit, submit, review and publish are refused (a setting, then the removal of `script.edit` / `.approve` / `.publish` from script authoring only); the library, versions, compare and history stay readable; rules and finding rules stay fully editable under their own permissions |
| **Regression** | the legacy read journeys; a new test that every script write is refused; survey assignment end to end |
| **Security** | permission change recorded; no escalation through the new permissions; the read role cannot write by any route |
| **Business acceptance** | the owner names who keeps read access and for how long |
| **Compatibility** | write operations remain in the contract, answering 403/409, until MIG-5 |
| **Recovery** | switch the setting back; re-grant |

### MIG-5 — Retire the Script Studio UI

| | |
|---|---|
| **Enter when** | MIG-4 has been in force for a period the owner sets with no need to write a script; a read-only **historical script view** exists (§6) and is reached from Call Detail and Review Workbench; ADR-0010's condition is met ("removed when the owner retires those screens") |
| **Does** | remove the Script Studio library and editor screens, their routes and navigation entry; `/scripts…` deep links redirect to the historical view; remove the *write* operations of `api/script_authoring.py` from the contract. **Keeps:** every table; `script_authoring`'s read functions; the script assignment engine for as long as any case depends on it; Assignment Rules, Finding Rules, Review Workbench, Call Detail |
| **Regression** | full suites; the historical view on every case with history; deep-link redirects; the specs validator and the route table updated together |
| **Security** | the historical view is read-only by construction and scoped like Call Detail |
| **Business acceptance** | owner and Compliance sign that history is complete and readable |
| **Compatibility** | a declared breaking change of the API contract, versioned per `API_CONTRACT_POLICY.md` |
| **Recovery** | code revert restores the screens; no data was touched. **Deleting tables or engines is not part of MIG-5 and would need its own destructive-change checkpoint** |

---

## 6. Recommended target architecture

| Area | Role | What it is built on |
|---|---|---|
| **Survey Studio** | the one place conversations are designed: modules, questions, conditions, answer sets, surveys; draft → three-person review → immutable publication; the component library | as built (SS-03A … LIB-2) |
| **Assignment Rules** | a shared authoritative service: which content an application gets. A rule stands on its own — its own market, its own permissions — and *names what it selects through a binding*, a script version today, a survey version tomorrow | `rule_engine`, `rule_authoring`; SHARED-1 removes the mandatory script target |
| **Finding Rules** | a shared authoritative service: what becomes a finding, at what severity. Its own permissions. A rule reaches content through a control or "any question"; a rule scoped to one question names an identity that both stores can resolve | `finding_engine`, `finding_rules` |
| **Controls** | a register with an owner and a way to maintain it, not a by-product of the script editor | `control`; a small maintenance screen is missing today |
| **Simulation & Evaluation** | the integrated verification workspace: module test, survey simulation, coordinated journeys, control evaluation, execution assurance, the journey trace — and, to replace the workbench, saved scenarios and batch regression | as built, plus the gap of row 37 |
| **Review Workbench** | operational review of real cases. Separate, unchanged, never merged with the evaluation of simulations | as built |
| **Historical script evidence** | a **read-only script view**: a script version exactly as it was published — sections, wording, rules, manifest fingerprint, who approved it — opened from Call Detail and Review Workbench. No editing, no list to browse for authoring | the existing read operations (`GET /script-versions/{id}`, history, diff) and readers |

One store for new content, as AD-1 intended — but the old store is *retired into read-only*, not deleted, because
operational history points at it. No second migration engine and no second evaluation engine: migration is authoring
through the existing survey operations; parity is checked with the two existing engines.

---

## 7. Technical blockers

| | Blocker | Removed by |
|---|---|---|
| T-1 | a rule must target a published script; a rule's market comes from that script | SHARED-1 |
| T-2 | rules and finding rules are governed by `script.*` permissions | SHARED-1 |
| T-3 | no operational path from a survey to a case, a session or a run | OPS-1 — which touches the voice pin, so it borders VOICE-1 |
| T-4 | three condition facts used by scripts (`is_ilp`, `premium_frequency`, risk band) are not in the survey field catalog | a catalog decision (synthetic today) |
| T-5 | a finding rule scoped to a question names a script question code | an identity both stores resolve, or re-scoping the rules to controls |
| T-6 | saved scenarios, batch regression, version comparison and coverage exist only on the script engine | a Simulation & Evaluation increment |
| T-7 | the control register has no maintenance of its own | a small controls screen |
| T-8 | module and question codes are issued by the server: legacy codes cannot be kept | an identity-mapping record (MIG-2) |
| T-9 | no read-only historical script view exists | built before MIG-5 |
| T-10 | survey tests and four browser journeys create rules through the legacy path | follows SHARED-1 |
| T-11 | workspace search runs in the browser; the script library's is server-side | a server search |

## 8. Business blockers — decisions only the owner or Compliance can make

| | Decision | Why it blocks |
|---|---|---|
| **B-1** | **Does this brief supersede D-156 (AD-2: "Re-seed… No legacy loader, evaluator or conversion path is to be built") and the "database structures" part of D-154?** | they contradict a controlled migration and the preservation of historical services. Nothing in MIG-2 … MIG-5 can start until one of them gives way. *This assessment assumes the newer brief, and says so* |
| B-2 | D-159 said not to assume Assignment Rules and Finding Rules remain separate products; this brief makes them shared authoritative services. Confirm | it fixes the target architecture |
| M-1 | Re-prompt limits: all 39 script questions carry one; surveys have none and no value is approved (D-NA-8) | migrating without it changes behaviour |
| M-2 | Conversational delivery: 28 of 39 revisions; a survey candidate may not contain it (TS-4) | they must be re-classified, or left unmigrated |
| M-3 | Lifecycle steps: are opening, disclosure and closing statements or acknowledgements; and what happens when identity, consent or recording consent fails (UC-D-5) | consent-refusal behaviour is not to be invented |
| M-4 | When a section's condition cannot be decided for lack of information: scripts say nothing; a survey must say | the survey validator blocks without it |
| M-5 | Which scripts are migrated at all — the four with history, only the current one, or none (author new surveys instead) | sets the scope of MIG-2 |
| B-3 | Effective dating and withdrawal of published content (rows 28, 29; P-5) | scripts have both; surveys have neither |
| B-4 | "Evidence required" (18 questions): what consumes it, and is it still wanted | unknown consumer |
| B-5 | How long legacy authoring stays readable, and for whom (MIG-4, MIG-5) | sets the gates' exit |
| B-6 | Whether an approval given under the two-person rule has any standing for migrated content | this assessment says no: three people re-approve |
| B-7 | The protected demonstration records (`SG_LIFECYCLE_DEMO 1.1`, `SG_EVALUATION_DEMO 1.0`, rule `S2D1-LIFECYCLE-DEMO`): do the restrictions still hold | they were to be left alone |

## 9. Recommended next checkpoint

**SHARED-1 — Assignment Rules and Finding Rules stand on their own.** Assessment and design first, then an additive
change:

1. A rule version carries its **own market**, and its script target becomes **optional** (a rule that selects only
   through a survey binding needs none). Existing rules are unchanged; their market is back-filled from their target.
2. Assignment rules and finding rules get permissions of their own; the `script.*` permissions keep working, so no
   existing role loses anything.
3. Survey assignment reads the rule's market from the rule, not through a script.
4. The survey tests and browser journeys create rules without a script.

Why this first: it removes T-1, T-2 and T-10; it is additive and reversible; it changes no business rule (the same
engine, the same precedence); and both a migration and a retirement are impossible without it. It needs B-1 and B-2
ruled, and nothing else.

Then, each its own authorised checkpoint: the rulings M-1 … M-5; **OPS-1** (a survey assigned to a real case —
assessment only at first, because it touches the voice pin and so the edge of VOICE-1); the read-only historical
script view; then MIG-2.

**Not recommended next:** a converter (the decisions are open), any deletion, VOICE-1, LIB-3.

## 10. Not done, deliberately

No converter. No script, rule, finding rule, control, case or review record changed. No screen, route, permission or
navigation entry changed. No migration. Script Studio is exactly as it was. VOICE-1 and LIB-3 not begun.
