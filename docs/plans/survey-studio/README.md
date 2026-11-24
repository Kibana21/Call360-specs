# Survey Studio — plans

Planning and design-contract documents for the Governance redesign defined by
`docs/product/survey-studio/PRD_v1.1.md` and `UX_EXCELLENCE_v1.1.md`.

## SS-00 — Assessment and design (ACCEPTED by the owner 2026-11-21 as an assessment and planning checkpoint)

| Document | Contents |
|---|---|
| `01_ASSESSMENT_AND_GAP_ANALYSIS.md` | A capability matrix · B gap analysis of the 191 SS-* requirements · C reuse unchanged · D extend / replace / retire |
| `02_ARCHITECTURE_AND_DECISIONS.md` | E information architecture · F canonical model · G one graph for editors, simulator and runtime · H decision proposals · I migration and coexistence |
| `03_IMPLEMENTATION_AND_UI_PLAN.md` | J phases SS-01…SS-10 · K UI design plan · L risks and recommendations |

**Superseded parts of SS-00** (kept as the historical proposal): `02` §H is replaced by the SS-01 decision register;
`02` §E.1 (a separate "Wording & Delivery" navigation entry at `/scripts`) is replaced by the owner's SS-D-20 ruling —
Wording & Delivery is a capability *inside* Survey Studio; the SS-D-09 restriction in `02` and its mention in `03`
(R4, §L.2) are **rejected** by the owner and replaced by the instance contract in `04` §6.

## SS-01 — Architecture and contract finalisation (ACCEPTED by the owner 2026-11-21, with rulings D-113…D-121)

| Document | Contents (SS-01 deliverable numbers) |
|---|---|
| `04_SS-01_CANONICAL_CONTRACTS.md` | 1 definitions / versions / instances · 2 survey and module graph and route contracts · 3 answer contracts (Yes/No, single, multi, Other, free text) · 4 sequential follow-up queue · 5 typed conditions with AND/OR/NOT and UNKNOWN · 6 shared-question identity, reuse, versioning, evidence |
| `05_SS-01_GOVERNANCE_COMPATIBILITY_EXECUTION.md` | 7 structure versus wording ownership and binding · 8 legacy compatibility proof and transition · 9 simulation and future runtime execution contracts · 10 validation, approval, pinning, immutable publishing · 11 naming amendment proposal (ADR-0007, terminology, tests) and validator state |
| `06_SS-01_DECISION_REGISTER.md` | 11 decisions SS-D-01…SS-D-20 with exact wording, resolution, status and risks, plus SS-D-02a, 09a, 21 |
| `07_SS-02_PROTOTYPE_PLAN.md` | 12 the SS-02 prototype plan: nine screens, ten stories, sub-checkpoints, evidence |
| `fixtures/` | Eight canonical JSON fixtures with 25 expected runs and 7 rejected answers, a README, and the reference interpreter that generates and checks them |

## SS-02A — High-fidelity clickable prototype (IMPLEMENTED AND VERIFIED 2026-11-21, awaiting the owner's review)

| Document | Contents |
|---|---|
| `08_SS-02A_PROTOTYPE_REPORT.md` | How to open it · what was built · dependency assessment · evidence (journeys A–H, 28 screenshots, tests, accessibility scan, regression) · UX self-assessment against PRD §18 · gap list · decisions that affect the prototype |

Evidence: `docs/acceptance/evidence/SS-02A/`. Code: `Call360-frontend/src/features/surveystudio/` behind the build
setting `VITE_SURVEY_STUDIO_PROTOTYPE=1` (off by default). Naming: ADR-0010 (applied 2026-11-21).

## SS-02A.1 — Prototype refinements (ACCEPTED by the owner 2026-11-21 as technically verified; not UX acceptance)

| Document | Contents |
|---|---|
| `10_SS-02A.1_REFINEMENTS_REPORT.md` | Owner decisions D-122…D-124 applied · the seven refinements as built · evidence (refinement and keyboard-only journeys, three widths, accessibility scans, tests, regression) · keyboard map and findings · remaining UX gaps |

Evidence: `docs/acceptance/evidence/SS-02A.1/`. SS-02A itself remains technically verified and not UX-accepted.

## SS-02A.2 — Guided Question Builder UX refinement (ACCEPTED by the owner 2026-11-21 as technically verified and as the visual and interaction baseline; formal UX sign-off pending)

Not the earlier S2-A.2 Script Studio layout checkpoint.

| Document | Contents |
|---|---|
| `11_SS-02A.2_UX_REFINEMENT_REPORT.md` | Simpler default question card · compact interruption authoring (one rule open at a time) · visual hierarchy · modal entry-condition drawer · routing / wording / publication status told apart · evidence (U1–U8 and regenerated sets) · interaction cost before and after · UX assessment and remaining gaps |

Evidence: `docs/acceptance/evidence/SS-02A.2/`. **Survey Studio is not yet UX-accepted.**

## SS-02B.1 — Conditions and Routing Intelligence (ACCEPTED by the owner 2026-11-21 as technically verified, subject to two corrections made in SS-02B.2)

| Document | Contents |
|---|---|
| `12_SS-02B.1_CONDITIONS_AND_ROUTING_REPORT.md` | Decision points inside a module (matches / otherwise / unknown) · reusable, parameterised, versioned conditions with definition kept apart from placement binding and an impact list · earlier answers as inputs with availability analysis · first-matching-rule routing for multiple choice · editable selection limits · the eight demonstrations · checks · prototype contract notes and proposals P-1…P-5 · gaps |

Evidence: `docs/acceptance/evidence/SS-02B.1/`. Frontend prototype only; no new dependency.

## SS-02B.2 — Advanced Graph Builder and Guided / Graph parity (IMPLEMENTED AND TECHNICALLY VERIFIED 2026-11-21, awaiting the owner's review)

| Document | Contents |
|---|---|
| `13_SS-02B.2_GRAPH_BUILDER_REPORT.md` | The two mandatory corrections (selection limits never changed silently; stable, typed condition references) · decisions D-125…D-131 as applied · module question graph and survey module graph · one model, one set of operations, one undo history · library evaluation · the twelve demonstrations · parity fingerprints · checks · design decisions · points for the owner · gaps |

Evidence: `docs/acceptance/evidence/SS-02B.2/`. Contract amendments: `04` §3.4 and §5.4; decisions: `06` (D-125…D-131).
New pinned dependencies: `@xyflow/react` 12.12.1, `@dagrejs/dagre` 3.1.3.

## SS-02B.2.1 — Graph connection editing (ACCEPTED by the owner 2026-11-21 as technically verified)

| Document | Contents |
|---|---|
| `14_SS-02B.2.1_CONNECTION_EDITING_REPORT.md` | Select, disconnect and redraw connections · incomplete routes shown and validated · governed restrictions and structure lines · one model · keyboard path · the eleven demonstrations · parity fingerprints · checks · gaps |

Evidence is in the SS-02B.2 folder (`screens/CE*`, `connection_parity_fingerprints.txt`). No new dependency.

## SS-02B.3 — Journey Simulator (ACCEPTED by the owner 2026-11-21 as technically verified; UI direction accepted as the prototype baseline)

| Document | Contents |
|---|---|
| `15_SS-02B.3_JOURNEY_SIMULATOR_REPORT.md` | Decisions D-132…D-134 · the simulator screen, engine and explanations · eight synthetic customers and a demonstration survey · golden fixture verification (8 fixtures, 25 runs, 7 rejected answers, all matching) · Guided / Graph journey equivalence · demonstrations and screenshots · checks · gaps |

Evidence: `docs/acceptance/evidence/SS-02B.3/` (`fixture_verification.txt`, `screens/SJ*`). Contract amendments: `04` §5.4
(d), (d-1), (g), (h); decisions: `06` (D-132…D-134). No new dependency.

SS-02B.2 was accepted by the owner on 2026-11-21 as implemented and technically verified.

## SS-02B.3.1 — Business-rule correctness (ACCEPTED by the owner 2026-11-21 as technically verified)

| Document | Contents |
|---|---|
| `16_SS-02B.3.1_BUSINESS_RULE_CORRECTNESS_REPORT.md` | D-135 a jump selects a candidate and never bypasses eligibility; the skip disposition · D-136 six terminal states and the explicit, versioned fixture migration · six new golden fixtures (schema /2) checked by an independent reference and reproduced by the simulator · D-137 the no-answer requirement, recorded not built · verification · points for approval · gaps |

Evidence: `docs/acceptance/evidence/SS-02B.3.1/` (`fixture_verification.txt`, `focused_traces.txt`, `screens/BR*`).
Contract amendments: `04` §2.2a, §2.2b, §5.5; decisions: `06` (D-135…D-137). Fixtures: `fixtures/G1…G6`,
`reference_interpreter_v2.py`; F1–F8 unchanged. No new dependency.

## SS-02C — Final prototype checkpoint (functional delivery and visual direction ACCEPTED by the owner 2026-11-21 as the baseline)

| Document | Contents |
|---|---|
| `18_SS-02C_FINAL_PROTOTYPE_REPORT.md` | Part A rulings A-1…A-5 as built · Part B validation workspace · Part C revision comparison · Part D simulated maker-checker and publishing · Part E one journey, the nine screens and ten stories mapped · Part F evidence · **prototype acceptance checklist against the UX excellence requirements** · points for decision · gaps · walkthrough |
| `17_SS-02C_NO_ANSWER_CONTRACT.md` | Decision-ready contract for unanswered questions: 17 decisions with approvers, named parameters with no values. **Proposed, not approved, nothing built** |

Evidence: `docs/acceptance/evidence/SS-02C/` (`checks.txt`, `fixture_and_rule_verification.txt`, `prototype_journeys.txt`,
`playwright_standard.txt`, `screens/W01–W05, GV01–GV13, BR1–BR6`). Contract: `04` §2.2c; decisions: `06` (D-138…D-142,
P-6…P-12). Fixtures: `fixtures/H1…H4` (schema /3), `reference_interpreter_v3.py`; F1–F8 and G1–G6 unchanged.
No new dependency. All approvals and publications in the prototype are simulated.

## SS-02 — Final prototype closure (six corrections IMPLEMENTED AND TECHNICALLY VERIFIED 2026-11-21, presented for the owner's closure decision)

| Document | Contents |
|---|---|
| **`19_SS-02_FINAL_PROTOTYPE_CLOSURE.md`** | **The single closure document. Status: TECHNICALLY ACCEPTED — PROTOTYPE (D-149); SS-02 closed for feature development.** Future gates G-1…G-8 (§8) · proposed architecture direction, recorded only (§9) · The six corrections (D-143…D-148) · what is complete · what requires business-user testing · what is deferred to the backend · which decisions block operational implementation · final evidence and the corrected interactions |
| **`20_G-6_ARCHITECTURE_CONSOLIDATION_ASSESSMENT.md`** | **G-6 assessment — reviewed by the owner 2026-11-21; direction approved (AD-1, AD-2, AD-15). §10 records the decisions and governs where it differs.** Script Studio inventory from the actual code (screens, wording model, approval, APIs, services, tables, controller, evaluation/findings/review, evidence) · feature-parity matrix (four classes) · target architecture and treatment of SS-D-01/02/17/20 · Data-to-Call-Plan design · retirement and migration plan · proposed checkpoints with blocking decisions · decisions AD-1…AD-15 |
| **`21_UC-01_CONSOLIDATION_MAP.md`** | **Capability-level consolidation map (proposal).** Responsibilities by business workflow · every capability with its current implementation, consumers, replacement interface and disposition (reuse / refactor / replace / delete) · four replacement interfaces · updated retirement matrix · retirement sequence under re-seeding · one line per data structure |
| **`22_UC-01_IMPLEMENTATION_REPORT.md`** | **UC-01 — ACCEPTED 2026-11-21 as TECHNICALLY VERIFIED — FRONTEND PROTOTYPE (D-161); the new prototype baseline.** Corrected in part by UC-02 (`24_…` §4). Statement nodes · number and acknowledgement questions · wording and delivery on the card · controlled variables · interface contracts · call plan preview and walkthrough · what is blocked · evidence · exact remaining decisions before backend |
| **`23_UC-02_DECISION_READY_CONTRACTS.md`** | **Decision-ready contracts (proposal).** Every remaining decision sorted: 23 technical schema decisions approvable now · business and Compliance decisions open · voice-channel decisions that can wait · what blocks persistence, runtime and real calls · six minimal authoritative interfaces · implementation-readiness checklist |
| **`24_UC-02_IMPLEMENTATION_REPORT.md`** | **UC-02 — ACCEPTED 2026-11-21 as technically verified, subject to contract clarifications (D-170).** Schema /5 fixtures K1–K8 and an independent Python reference · plan computability separated from live-call eligibility · a recording without an asset blocks · compact call plan · evidence |
| **`25_UC-02_DECISION_CLOSURE.md`** | **Review outcome and decision closure (rulings PROPOSED).** 17 technical decisions recommended; amended wording for TS-2, 4, 7, 9, 10, 12 · twelve persistence rulings PB-1…PB-12 with dependency impacts, mechanism separated from policy content · P-23…P-29 verbatim and classified · gate presence is not approved enforcement · **UC-01 and UC-02 are not committed** |
| **`26_SS-03A_FOUNDATION_SPECIFICATION.md`** | **SS-03A specification — APPROVED AND AUTHORISED 2026-11-21 (D-186), with clarifications D-178…D-183.** Canonical versioned graph documents · immutable drafts, candidates and versions · hashes and manifest validation · server validation · deterministic condition engine · fifteen minimal API operations · exclusions · acceptance tests |
| **`27_SS-03A_IMPLEMENTATION_REPORT.md`** | **SS-03A — ACCEPTED 2026-11-22 as TECHNICALLY VERIFIED (D-188).** Pure Python domain (canonical JSON and hashes, six document kinds, 67 validation codes, three-valued conditions) · migration `0027_survey_definitions` (nine additive tables, append-only lifecycle, identity rules in the database, synthetic default-deny catalogs) · fifteen API operations behind a server setting that is off by default · permissions matrix · fixture, migration, immutability and concurrency evidence · changed-file inventory · commit provenance · proposed SS-03B and frontend-integration boundary. Server contract: `04_…` §9 |
| **`28_SS-03A_ACCEPTANCE_AND_DEVELOPMENT_ENABLEMENT.md`** | **Acceptance record and development enablement (2026-11-22) — ACCEPTED as technically verified (D-195).** Fixture-regeneration line reconciled (an untracked cache folder, not a fixture) · technical debt TD-SS03A-1, -2 · commit state and provenance · development database migrated to `0027` after ten preconditions, with verified backup · three development-only survey identities and the permission and identity checks · **FI-1 boundary — PROPOSED, NOT AUTHORISED**, with decisions FI-D-1…FI-D-5 |
| **`29_FI-1_IMPLEMENTATION_REPORT.md`** | **FI-1 — TECHNICALLY ACCEPTED — PERSISTED AUTHORING (D-204, 2026-11-22), after the Back-navigation correction (§12).** Survey Studio on the persisted API behind its own setting · one Workspace ↔ documents mapping, lossless on all 27 fixtures · atomic Save, retry without duplication, explicit conflict resolution · server-authoritative validation · access by `survey.read` / `survey.edit` · two additive API operations and the optional `authoring` field (`04_…` §10) · nine acceptance tests and a full-stack journey · git-automation inspection · **FI-2 boundary — PROPOSED, NOT AUTHORISED** |
| **`30_FI-2_IMPLEMENTATION_REPORT.md`** | **FI-2 — ACCEPTED 2026-11-22 as TECHNICALLY VERIFIED — REAL REVIEW AND PUBLICATION (D-213).** Real review and publication on the immutable candidates of the API: author submits with server validation and acknowledged server-governed warnings; checker inspects the frozen content and approves or sends back; publisher creates an immutable version · two additive read operations and the warning mechanism (`04_…` §11) · ten demonstrations, three full-stack journeys · walkthrough on the development database with the three development identities · **library boundary LIB-1 — PROPOSED, NOT AUTHORISED** |
| **`31_LIB-1_IMPLEMENTATION_REPORT.md`** | **LIB-1 — TECHNICALLY ACCEPTED 2026-11-22 (D-222), subject to the legacy library-discovery security correction, which is closed in `32_…` §1.** The reusable component library inside Survey Studio: one selector for published modules, questions, conditions and answer sets · discovery only of what a published version pins · add (pinned, locked) and edit-a-copy (own identity, provenance) · newer revisions as information only · server-issued asset codes (migration `0028`, additive; development database not migrated) · the published-only reference rule · sixteen verifications, five full-stack journeys · contract `04_…` §12 · **SS-03B boundary — PROPOSED, NOT AUTHORISED** |
| **`32_SS-03B_IMPLEMENTATION_REPORT.md`** | **SS-03B — ACCEPTED 2026-11-22 as TECHNICALLY VERIFIED (D-234), simulation only; its authorisation gap is closed in `33_…` §1 (`survey.simulate`, replay drift). Uncommitted.** LIB-1 security closure (`GET /survey-library/{kind}`) · development migration `0028` evidence · the authoritative Python execution engine (82/82 golden runs) · deterministic call-plan assembly (14/14 golden plans) · isolated simulation and call-plan records (migration `0029`, additive, test schema only; development NOT migrated) · five operations behind `survey_simulation_enabled` · the Simulator and Call plan screens on real Python results, with the browser engine compared in full view · `POLICY_UNRESOLVED` for non-answers. Contract `04_…` §13; decisions D-222…D-233 |
| **`33_ASG-1_IMPLEMENTATION_REPORT.md`** | **ASG-1 — ACCEPTED 2026-11-22 as TECHNICALLY VERIFIED for SINGLE-SURVEY assignment (D-246); the binding is an interim adapter. Its read access is closed in `35_…` §1. Uncommitted. SIMULATION ONLY.** SS-03B closure: the `survey.simulate` permission; execution-contract version and replay drift (`REPLAY_DRIFT`); retention recorded as OR-1 · development migration `0029` evidence (development NOT at `0030`) · assessment of the existing Assignment Rules capability and the two contract mismatches · the governed survey **binding** and the re-targeting adapter over the unchanged rule loader and engine · selection → manifest check → SS-03B call plan → simulation for synthetic applications · the Survey assignment page · proposed next: EVAL-1. Contract `04_…` §13.9, §14; decisions D-234…D-245 |
| **`34_ASG-2A_GROUPING_AND_MATCHING_SEMANTICS.md`** | **The semantics of requirement groups, written before implementation (D-250).** What a group is; `PRIMARY`, `ADD_REQUIRED`, `ALTERNATIVE`; matching within a group by the existing engine; the configuration checks that fail closed; the selection; ordering only where governed; the composite plan; what stays unresolved |
| **`35_ASG-2A_IMPLEMENTATION_REPORT.md`** | **ASG-2A — ACCEPTED 2026-11-22 as TECHNICALLY VERIFIED — MULTI-SURVEY ASSIGNMENT AND COMPOSITE CALL-PLAN ASSEMBLY (D-259), simulation-only mechanics; the stand-in demonstrations are not proof of real requirements. Uncommitted.** ASG-1 closure: the `survey.assignment.read` permission · development migration `0030` evidence (development NOT at `0031`) · requirement groups and the engine once per group · composite plans from individual SS-03B plans · ordering, cross-survey policy and input consistency reported as unresolved, never invented · the eighteen demonstrations · stand-ins for "replacement" and "CI rider" (OR-3) · the unresolved policy register · the proposed ASG-2B boundary. Contract `04_…` §15; decisions D-246…D-258, OR-2, OR-3 |
| **`36_ASG-2B_IMPLEMENTATION_REPORT.md`** | **ASG-2B — TECHNICALLY ACCEPTED by the owner 2026-11-22 for simulation-only coordinated multi-survey execution (D-271); uncommitted. SIMULATION ONLY.** The ASG-2A acceptance record and the three separate states (call plan computable · coordinated simulation permitted or blocked · operational call eligibility not established) · development migration `0031` evidence, including that withdrawal does not enable a downgrade (development NOT at `0032`) · the thin coordinating layer over individual SS-03B simulations · the simulation-only continuation rules · no de-duplication · the coordinated record and its replay fingerprint · the Simulator's coordinated mode · the twenty demonstrations · policy gaps · the proposed EVAL-1 boundary. Contract `04_…` §16; decisions D-259…D-270 |
| **`37_EVAL-1_EXISTING_ENGINE_ASSESSMENT_AND_DESIGN.md`** | **EVAL-1 — written BEFORE implementation.** The mandatory assessment of the existing evaluation and finding engines (ten items), the reuse matrix, and the design decisions: grain, governed control mapping, evidence adapter, control outcome, processing status, records |
| **`38_EVAL-1_IMPLEMENTATION_REPORT.md`** | **EVAL-1 — ACCEPTED by the owner 2026-11-22 as TECHNICALLY VERIFIED, simulation only (D-289); D-287 approved with restrictions (D-290); uncommitted.** ASG-2B acceptance record; development migration `0032` evidence; journey-level control evaluation reusing the existing answer evaluator and finding engine; governed control mappings; Evaluation Workbench; 21 demonstrations; gaps G-E1…G-E7; D-287 proposed for the owner's ruling |
| **`39_EVAL-2A_CONTROL_REGISTRY_ASSESSMENT_AND_POLICY_DESIGN.md`** | **EVAL-2A — written BEFORE implementation.** The existing Control Registry as it is; the smallest additive extension (a governed control policy beside the register); canonical identity and revision strategy; applicability; coverage semantics; answer types |
| **`40_EVAL-2A_IMPLEMENTATION_REPORT.md`** | **EVAL-2A — ACCEPTED by the owner 2026-11-22 as TECHNICALLY VERIFIED, simulation only (D-301); not Compliance approval. D-300 reconciled in D-302.** EVAL-1 closure and the seven-way D-288 reconciliation; development migration `0033` evidence; governed control policies, obligations, applicability and coverage; `SET_MATCH`; the Controls and evidence builder; verification, regressions, what remains unapproved |
| **`41_EVAL-2A_MIGRATION_0034_COMPATIBILITY_REPORT.md`** | **Migration `0034` — purely additive; applied to development 2026-11-22 under the owner's authorisation (D-304).** Every DDL operation; how EVAL-1 and policy-scoped evaluations coexist; the test over a schema populated by EVAL-1, with forced failure, recovery and guarded downgrade |
| **`42_EVAL-2B_EXECUTION_ASSURANCE_ASSESSMENT_AND_DESIGN.md`** | **EVAL-2B — assessment, reuse matrix and design.** What the execution engine, simulation, composite plan, coordinator and evaluations already record; the one gap (nothing verifies a recorded trace against what it pinned); the eight survey checks, five journey checks, exclusion classes and status model |
| **`43_EVAL-2B_IMPLEMENTATION_REPORT.md`** | **EVAL-2B — ACCEPTED by the owner 2026-11-22 as TECHNICALLY VERIFIED, simulation only (D-312); not production, Compliance or spoken-delivery acceptance. D-311 reconciled in D-313; gap TG-1 in D-314.** EVAL-2A acceptance and the ten-way D-300 reconciliation; development migration `0034` evidence; execution assurance inside the Evaluation Workbench; 22 demonstrations (negative cases on tampered recordings, named as such); outstanding policy questions; the proposed E2E-1 boundary |
| **`44_E2E-1_BASELINE_INTEGRATION_AND_ACCEPTANCE_MATRIX.md`** | **E2E-1 — baseline.** The nine modules with contracts, migrations, settings and permissions; the eleven handoffs and how each is pinned; reused browser journeys; the acceptance matrix (fifteen steps, scenarios A–G); where stand-ins and unverified mappings are used; technically verified versus awaiting Business / Compliance |
| **`45_E2E-1_IMPLEMENTATION_REPORT.md`** | **E2E-1 — BUILT AND TECHNICALLY VERIFIED 2026-11-22, awaiting the owner's review; not accepted; uncommitted. SIMULATION ONLY.** EVAL-2B acceptance and the D-311 reconciliation; development migration `0035`; one read-only journey trace and the "Application journeys" page; scenarios A–G; provenance; technical gaps TG-1…TG-7 versus business policies BP-1…BP-11; the proposed next checkpoint |
| **`46_UX-HOME-1_WORKSPACE_REPORT.md`** | UX-HOME-1, first version — **superseded** by 47 and 48. Kept for the first workspace design and the owner's mid-checkpoint review (three views; where a building block is made) |
| **`47_UX-HOME-1_NAV-1_ASSESSMENT_AND_DESIGN.md`** | **UX-HOME-1 + NAV-1 — assessment and design.** Existing navigation and routes; overlapping screens; which modules stay authoritative; available library metadata; existing and missing read APIs; limitations; the five-group information architecture, the inspector and the rules explorer |
| **`48_UX-HOME-1_NAV-1_IMPLEMENTATION_REPORT.md`** | **UX-HOME-1 + NAV-1 — ACCEPTED as technically verified 2026-11-22 (D-330; not business UX or screen-reader acceptance).** Consolidated sidebar and breadcrumbs; Survey Studio workspace, building-blocks gallery, Module Inspector, surveys explorer with overview, rules explorer, Simulation & Evaluation page; the 26 browser journeys; limitations L-1…L-8; no migration, no semantic change |
| **`49_LIB-2_ASSESSMENT_AND_ARCHITECTURE.md`** | **LIB-2 — assessment, architecture decisions and contract.** What LIB-1 left; the three decisions proposed with D-328 and their resolution; options; AD-L2-1…8 (a standalone module is a definition of kind MODULE; the fixed frame; one governance; never a survey; testing is a replay that records nothing); lifecycle and authoring contract; migration `0036` assessment; unresolved questions P-1…P-8; staged extension for questions, conditions and answer sets (LIB-3, not authorised) |
| **`50_LIB-2_IMPLEMENTATION_REPORT.md`** | **LIB-2 — ACCEPTED as technically verified 2026-11-22 (D-344; simulation-only; not business UX, screen-reader, Compliance or production acceptance). Development migrated to `0036` on the owner's authorisation (§10, D-348).** Part A: UX-HOME-1 + NAV-1 closed, five UX issues. Standalone Module Builder, one-module test by the Python engine, three-person publication, gallery, inspector and composer reuse; the twenty demonstrations; regression; gaps G-1…G-11.  |
| **`51_MIG-1_SCRIPT_STUDIO_RETIREMENT_READINESS.md`** | **MIG-1 — assessment, ACCEPTED by the owner 2026-11-23 (D-356); B-1 and B-2 ruled (D-357, D-358); the other decisions open (D-359).** Inventory of Script Studio (screens, operations, tables, what development holds); 43-row parity matrix against Survey Studio; dependency diagram and the fifteen contracts that would break; migration feasibility and mapping; historical preservation, rollback and dual running; gates MIG-2 … MIG-5; technical blockers T-1 … T-11; business blockers B-1 … B-7 and M-1 … M-5; target architecture; recommended next checkpoint SHARED-1. Roadmap: `docs/plans/ROADMAP.md` |
| **`52_SHARED-1_ASSESSMENT_AND_DESIGN.md`** | **SHARED-1 — assessment, design and data-preservation plan**, written before the schema was edited. What the rule and finding-rule code does today; a rule's own market (AR-1); the explicit kind of a rule (AR-2) and the disposition of every consumer of the script target; preserved semantics; bindings; finding rules and DEP-FR-1; the permission transition; migration `0037` step by step |
| **`53_SHARED-1_IMPLEMENTATION_REPORT.md`** | **SHARED-1 — ACCEPTED by the owner as technically verified 2026-11-23 (D-370).** A survey-only rule governed with dedicated permissions, bound, grouped, composite plan and coordinated simulation with no dummy script; operational assignment and history identical; Finding Rules on their own permissions; the twenty demonstrations; migration and rollback evidence; regression; gaps. Migration `0037` applied to development afterwards (see `54_…`) |
| **`54_SHARED-1_ACCEPTANCE_AND_DEVELOPMENT_ENABLEMENT.md`** | **SHARED-1 acceptance; D-367 reconciled choice by choice; governance differences documented; cross-kind conflict assessment (CK-1…CK-3, semantics unchanged); development migration `0037` with before/after, round trip and guard evidence; the four dedicated development identities and their ten grants; the thirteen-step development demonstration; regression.** Awaiting review |
| **`55_APP-1_OPS-1_ARCHITECTURE_ASSESSMENT.md`** | **APP-1 / OPS-1 — ASSESSMENT ONLY, presented for review 2026-11-23; nothing decided or built.** Application identity and snapshot; the two vocabularies and their gaps (replacement, riders); lineage; selection by survey-only rules; linking a journey to a case; session pins; operational evidence beside the legacy evidence; holds and preflight; Review Workbench and Call Detail; rollback and mixed operation; fifteen Business / Compliance questions; technical versus policy; proposed boundary APP-1a |
| **`56_APPL-X1_PRODUCT_ARCHITECTURE_AND_CONTRACTS.md`** | **Survey Applicability Studio — PROPOSED DESIGN for owner acceptance.** Vision; information architecture; the five documents (variable, profile, condition, policy, scenario); the expression tree; three-valued logic with truth tables; selection semantics (additive, replacement, choose one, same survey, order, scope); the evaluator and its output; fact contract; governance; proposed persistence (eight tables); coexistence and retirement; API; decisions AP-1…AP-10 |
| **`57_APPL-X1_EXPERIENCE_SPECIFICATION_AND_EVIDENCE.md`** | **APPL-X1 — accepted as a technically verified prototype and direction (D-386); superseded in part by `59_…`.** Design system; the seven screens; three views of one policy; narrow screens; the fifty acceptance demonstrations with what is shown, partly shown and not shown; the UX targets and which were measured (none that needs people); critique and refinement; regression |
| **`58_APPL-X2_TO_X6_IMPLEMENTATION_PLAN.md`** | **PROPOSED, nothing authorised.** Entry conditions; APPL-X2 library, profiles and conditions persisted; X3 policy and designer; X4 scenarios, impact and three-person publication; X5 integration through a selection-plan interface; X6 legacy survey-assignment retirement; risks |
| **`59_APPL-X1R_REFINEMENT_REAL_SURVEY_SHOWCASE_AND_EVIDENCE.md`** | **APPL-X1R — ACCEPTED as the product-design baseline and technically verified prototype (D-393).** The eight absolute criteria; rulings AP-1…AP-10 as implemented; the real showcase (one module and five surveys published through Survey Studio's governed API, with database evidence); applicability on real published versions (catalogue, exact reference, picker, preview, navigation both ways); the refined gallery, card composer, canvas and scenario lab; showcase journeys A–G; usability (nothing measured with people); critique; regression |
| **`60_APPL-X2_LIBRARY_ARCHITECTURE_API_AND_MIGRATION.md`** | **APPL-X2 — specification.** The four tables and why (no draft table; a dependency table added); integrity enforced by the database; lifecycle, validation and pinning; permissions and markets; the fourteen operations; how the persisted library meets the evaluator; migration `0038` with its tests and the procedure for development (**not applied**); frontend integration |
| **`61_APPL-X2_REPORT_AND_EVIDENCE.md`** | **APPL-X2 — ACCEPTED as technically verified on the test schema (D-401).** The primary criterion part by part; what the tests prove; the three screens on the persisted library; the graph-focus defect and its fix, the quieter header, keyboard and drag coverage, deliberate adoption of a newer survey version; the voice flake's cause; regression; critique; what the owner is asked to decide |
| **`62_APPL-X2_DEVELOPMENT_ENABLEMENT_REPORT.md`** | **APPL-X2 on local development — ACCEPTED (D-411).** Preflight, verified backup, migration `0038`, the three dedicated identities and the `survey.read` ruling, the synthetic library through the governed API with idempotency, the browser demonstration with three signed-in people, API evidence of permissions, governance and market isolation, regression, and the comparison of every table with the preflight |
| **`63_APPL-X3_READINESS_ASSESSMENT.md`** | **APPL-X3 (persistent Applicability Policies) — ASSESSMENT ONLY; not started, not authorised.** What is reused unchanged, the proposed scope, what stays for APPL-X4, six decisions needed first, risks |
| **`64_APPL-X3_PERSISTENT_POLICIES_ARCHITECTURE_AND_CONTRACTS.md`** | **APPL-X3 — specification.** The policy document; where each exact dependency version lives; the dependency snapshot and what happens when a dependency moves; the three tables and their foreign keys; the ten operations; what became of the prototype operations; frontend; migration `0039` with its tests and the procedure for development (**not applied**) |
| **`65_APPL-X3_REPORT_AND_EVIDENCE.md`** | **APPL-X3 — ACCEPTED as technically verified on the test schema (D-419).** The final criterion part by part; stop conditions; rulings as implemented; what the tests prove; browser journeys A to I; carried UX items; regression; what remains untested |
| **`66_APPL-X3_ACCEPTANCE_AND_DEVELOPMENT_ENABLEMENT.md`** | **APPL-X3 — acceptance record and development enablement (2026-11-24).** D-416 rulings; preflight; backup; migration `0039` on development; settings; journeys A–G in the development browser; graph-visibility correction; restore control; D-418 cause and measurements; integrity comparison; regression. |
| **`67_APPL-X4_READINESS_ASSESSMENT.md`** | **APPL-X4 — ASSESSMENT ONLY, not authorised.** Persistent scenarios and suites, policy candidates and three-person publication, blockers (`PIN_DIFFERS`), proposed `0040`, operations, journeys, roadmap, questions for the owner. |
| **`68_APPL-X4a_ARCHITECTURE_AND_CONTRACTS.md`** | **APPL-X4a — architecture and contracts.** Owner decisions Q-1…Q-6; scenarios, variants, suites, runs; migration `0040`; exact snapshots and what "reproducible" means; expectations and verdicts; coverage; the 22 operations; synthetic-only safeguards. |
| **`69_APPL-X4a_REPORT_AND_EVIDENCE.md`** | **APPL-X4a — ACCEPTED as technically verified on the test schema (D-438).** Journeys A–J, showcase, migration and rollback, security, scale measurements, regression, what is not tested. |
| **`70_APPL-X4b_READINESS_SPECIFICATION.md`** | **APPL-X4b — IMPLEMENTATION SPECIFICATION, revised with the owner's rulings (D-441…D-446); not authorised, not started.** Readiness gate and blockers, deterministic independence rule for expectations, provenance, frozen candidate, three people, published versions, supersession, impact, reviewed `0041` (not created). |
| **`71_APPL-X4a_ACCEPTANCE_AND_DEVELOPMENT_ENABLEMENT.md`** | **APPL-X4a — acceptance record and development enablement (2026-11-24).** Owner rulings; preflight (with the differences found); backup; migration `0040` on development; settings; journeys A–G in the development browser; the incompatibility rule; restore controls; designer route; shell accessibility defect; integrity comparison; regression. |
| **`72_APPL-X4b_ARCHITECTURE_AND_CONTRACTS.md`** | **APPL-X4b — architecture and contracts, as built on the test schema.** Decisions D-452…D-456; migration `0041`; readiness gate and blocker codes; independence rule and provenance; candidate lifecycle and revalidation; versions; explicit run targets; impact; 13 operations; screens. |
| **`73_APPL-X4b_REPORT_AND_EVIDENCE.md`** | **APPL-X4b — ACCEPTED as technically verified on the test schema (D-459), subject to the hardening in `75_…`.** Journeys A–H, three-person evidence at three levels, migration evidence, shell accessibility correction, `dev.admin` access review, regression. |
| **`74_APPL-X4b_DEVELOPMENT_ENABLEMENT_READINESS.md`** | **APPL-X4b — what applying `0041` to development would involve. A readiness report only; NOT authorised.** |
| **`75_APPL-X4b_ACCEPTANCE_HARDENING_AND_DEVELOPMENT_ENABLEMENT.md`** | **APPL-X4b — acceptance record, evidence-integrity hardening (edited-and-restored evidence never regains eligibility) with its test proof, and the development preflight — stopped for the owner, then authorised and completed. ACCEPTED (D-469).** Intended demonstration policy `GOV-DEMO-ILP-NFTF`. |
| **`76_APPL-X5_READINESS_ASSESSMENT.md`** | **APPL-X5 — readiness assessment only; NOT authorised.** What exists and is reusable, the gaps, a proposed separate applicability journey, shared delivery, resume and replay, a voice-neutral runtime interface, eight owner questions. |
| **`77_APPL-X5a_FACT_CORRESPONDENCE_DESIGN_DECISION.md`** | **APPL-X5a — the design decision the owner asked for first:** application facts and survey facts as two vocabularies; an IDENTITY-only, exactly pinned, synthetic correspondence in one new table; no accepted table changed. |
| **`78_APPL-X5a_ARCHITECTURE_AND_CONTRACTS.md`** | **APPL-X5a — architecture and contracts, as built on the test schema.** Decisions D-469…D-478; migration `0042`; authoritative selection; the thin coordinator; the voice-neutral runtime contract; persistence, resume, verification; 16 operations; screens. |
| **`79_APPL-X5a_REPORT_AND_EVIDENCE.md`** | **APPL-X5a — BUILT and technically verified on the test schema; awaiting owner acceptance.** Journeys A–J, validation, resume and replay, shared delivery, cross-survey behaviour, security, integrity, regression. |
| **`80_APPL-X5b_READINESS_ASSESSMENT.md`** | **APPL-X5b — readiness assessment only; NOT authorised.** Evaluation source, control-policy pinning, per-requirement and shared-delivery evaluation, assurance against the selection plan, a backward-compatible journey-kind extension, the trace, six owner questions. |
| `canonical-documents/` | The 27 golden fixtures as canonical documents with server hashes. **Generated** by `Call360-backend/scripts/export_survey_fixture_documents.py`; never edited by hand; the golden fixtures in `fixtures/` remain the source |
| `python-results/` | What the authoritative Python engine produces for each of the 82 expected runs and 14 expected plans. **Generated** by `Call360-backend/scripts/export_survey_python_results.py` (`--check` detects drift); never edited by hand; **not an expectation** — the golden fixtures in `fixtures/` remain the only expectations. Read by the frontend's cross-engine test |

Evidence: `docs/acceptance/evidence/SS-02-closure/` (`checks.txt`, `fixture_rule_and_parity_verification.txt`,
`prototype_journeys.txt`, `playwright_standard.txt`, `screens/CL01–CL07` and the re-captured walkthrough). Contract:
`04` §2.2d; fixture `fixtures/J1` (schema /4), `reference_interpreter_v4.py`. `17_…` now marks every decision
UNRESOLVED and says what each blocks. No new dependency.

## SS-03 and later — **not authorised**


SS-00 and SS-01 are documentation only; SS-02A is frontend only. No backend code, database schema, migration or API
contract was changed in any of them; the master BRD and the requirements register are untouched. Every later phase
needs its own explicit authorisation.
