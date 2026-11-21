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
| **`29_FI-1_IMPLEMENTATION_REPORT.md`** | **FI-1 — BUILT AND TECHNICALLY VERIFIED 2026-11-22, awaiting the owner's review; not accepted; uncommitted.** Survey Studio on the persisted API behind its own setting · one Workspace ↔ documents mapping, lossless on all 27 fixtures · atomic Save, retry without duplication, explicit conflict resolution · server-authoritative validation · access by `survey.read` / `survey.edit` · two additive API operations and the optional `authoring` field (`04_…` §10) · nine acceptance tests and a full-stack journey · git-automation inspection · **FI-2 boundary — PROPOSED, NOT AUTHORISED** |
| `canonical-documents/` | The 27 golden fixtures as canonical documents with server hashes. **Generated** by `Call360-backend/scripts/export_survey_fixture_documents.py`; never edited by hand; the golden fixtures in `fixtures/` remain the source |

Evidence: `docs/acceptance/evidence/SS-02-closure/` (`checks.txt`, `fixture_rule_and_parity_verification.txt`,
`prototype_journeys.txt`, `playwright_standard.txt`, `screens/CL01–CL07` and the re-captured walkthrough). Contract:
`04` §2.2d; fixture `fixtures/J1` (schema /4), `reference_interpreter_v4.py`. `17_…` now marks every decision
UNRESOLVED and says what each blocks. No new dependency.

## SS-03 and later — **not authorised**


SS-00 and SS-01 are documentation only; SS-02A is frontend only. No backend code, database schema, migration or API
contract was changed in any of them; the master BRD and the requirements register are untouched. Every later phase
needs its own explicit authorisation.
