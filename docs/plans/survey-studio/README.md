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

## SS-02B.3 — proposed, **not authorised**

| Document | Contents |
|---|---|
| `09_SS-02A_REFINEMENTS_AND_SS-02B_PLAN.md` | Part 1: the SS-02A.1 proposal (now implemented, with the owner's changes — see `10`) · Part 2: SS-02B plan — internal condition builder, graph editor, simulator, Guided ↔ Graph parity, first-matching-rule routing, parameterised conditions; how identities, branches and undo/redo are preserved; dependency checks · risks · four questions |

SS-00 and SS-01 are documentation only; SS-02A is frontend only. No backend code, database schema, migration or API
contract was changed in any of them; the master BRD and the requirements register are untouched. Every later phase
needs its own explicit authorisation.
