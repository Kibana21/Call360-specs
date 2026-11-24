# Call360 — roadmap of checkpoints

**Updated 2026-11-24, with APPL-X4a accepted and enabled on development.** This is an index of where each line of work stands and what has been *proposed*
next. It authorises nothing: a checkpoint is implemented only on the owner's explicit authorisation of that named
checkpoint (workspace `CLAUDE.md` §10). The current state in detail is `docs/plans/SESSION_HANDOFF.md` §0; every
decision is in `docs/plans/survey-studio/06_SS-01_DECISION_REGISTER.md`.

## Done — accepted as technically verified (simulation-only where it concerns surveys)

| Checkpoint | What | Document |
|---|---|---|
| SS-03A, FI-1, FI-2 | survey definitions, persisted authoring, three-person review and publication | `survey-studio/26_…` onward |
| LIB-1 | the reusable component library, server-issued identities | `30_…`, `31_…` |
| SS-03B | simulation and call plans by the Python engine | `32_…`, `33_…` |
| ASG-1, ASG-2A, ASG-2B | survey assignment by binding to assignment rules; requirement groups; coordinated simulation | `34_…` – `38_…` |
| EVAL-1, EVAL-2A, EVAL-2B | control evaluation, control policies and coverage, execution assurance | `39_…` – `43_…` |
| E2E-1 | the provenance trace of one simulated journey | `44_…`, `45_…` |
| UX-HOME-1 + NAV-1 | the workspace, explorers, inspector, five-group navigation | `47_…`, `48_…` |
| LIB-2 | modules authored on their own; development at migration `0036` | `49_…`, `50_…` |
| MIG-1 | Script Studio retirement readiness — assessment, **accepted** (D-356); B-1 and B-2 ruled (D-357, D-358) | `51_…` |
| SHARED-1 | Assignment Rules and Finding Rules on their own — **accepted as technically verified** (D-370); development at `0037` with the setting on and four dedicated identities | `52_…`, `53_…`, `54_…` |
| APP-1 / OPS-1 | architecture assessment — **assessment only, presented for review** | `55_…` |
| APPL-X1 | Survey Applicability Studio — architecture, evaluator and prototype; **accepted as a technically verified prototype and direction** (D-386) | `56_…`, `57_…` |
| APPL-X1R | UX refinement, rulings AP-1…AP-10, and the showcase on **real published Survey Studio surveys**; **accepted as the product-design baseline and technically verified prototype** (D-393) | `59_…`, `56_…` §14 |
| APPL-X2 | Governed applicability library — persisted variables, profiles and reusable conditions with server-enforced three-person publication; migration `0038`; **ACCEPTED as technically verified (D-401); enabled on local development 2026-11-24 (D-407 … D-409); awaiting review of the enablement** | `60_…`, `61_…`, `62_…` |
| APPL-X3 | Persistent Applicability Policies — saved working drafts with their exact dependency snapshot; migration `0039`; **ACCEPTED as technically verified on the test schema (D-419); `0039` applied to local development and saved policies enabled 2026-11-24 (D-421, D-422); enablement ACCEPTED (D-427)** | `64_…`, `65_…`, `66_…` |
| APPL-X4a | Persistent Scenario studio — saved synthetic scenarios and variants, regression suites with explicit expectations, immutable recorded runs, coverage, comparison; migration `0040`; **ACCEPTED as technically verified on the test schema (D-438); `0040` applied to local development and the Scenario studio enabled 2026-11-24 (D-447, D-449); awaiting review of the enablement** | `68_…`, `69_…`, `71_…` |

None of this is business UX, screen-reader, Compliance or production acceptance.

## Proposed — NOT authorised

| Checkpoint | What | Needs first |
|---|---|---|
| **APPL-X4b** *(next in the applicability programme)* | Applicability Policy governance and publication: readiness gate, frozen candidate, mandatory passing and meaningful suite, `PIN_DIFFERS` blocking, three people, published versions, supersession, draft-versus-published impact; proposed additive migration `0041` | review of the APPL-X4a enablement; the owner's authorisation; Q-a…Q-f are ruled (D-441…D-446), Q-g and Q-h open; **specification only**, `70_…` |
| APPL-X5 … X6 | Survey Studio integration; legacy survey-assignment retirement | each its own authorisation; `58_…` |
| **APP-1a** *(follows the applicability fact contract)* | a read-only, stateless application view for a case (rule inputs and mapped survey facts with lineage) and a selection preview; writes nothing operational | the owner's authorisation; `55_…` §13 |
| Governance harmonisation | rules (two people) versus bindings and content (three) | a Business decision (D-372) |
| Cross-kind conflict scope | CK-1…CK-3, with OR-2 / OR-3 | an owner decision (D-374) |
| DEP-FR-1 | an identity for question-scoped finding rules that both stores resolve | a design; not invented in SHARED-1 |
| Rulings M-1 … M-5, B-3 … B-7 | re-prompt limits; conversational delivery; lifecycle failure behaviour; unknown policy; which scripts migrate; effective dating and withdrawal; evidence required; read access; approvals; protected records | the owner, Compliance |
| OPS-1 *(the next blocker of retirement)* | a survey assigned to a real case — assessment first | borders VOICE-1 |
| Historical script view | read-only view of a published script version, from Call Detail and Review Workbench | — |
| MIG-2 | controlled content migration (a narrow one-time adapter is permissible, D-357) | M-1 … M-5 ruled; not started |
| MIG-3 | behavioural parity and historical evidence verification | MIG-2 |
| MIG-4 | legacy script authoring read-only | MIG-3; OPS-1 or a ruling; SHARED-1 |
| MIG-5 | retire the Script Studio UI; keep the tables, the readers and the shared services | MIG-4; the historical view |
| LIB-3 | questions, conditions and answer sets authored on their own | retained as a proposal (D-350) |
| Scenario library and batch regression for surveys | replaces the Simulation Workbench's saved scenarios, batches, comparison and coverage | — |
| Controls register maintenance | an owner and a screen for `control` | — |
| Server-side search for the workspace | — | — |
| DEC-1, ASSURE-2 | from `45_…` §13 | — |
| VOICE-1 | voice integration | explicitly not begun |

## Standing gates (from SS-02 closure, D-151) still open

G-1 business-user UX acceptance · G-2 screen-reader sign-off · G-3 non-answer policy · G-4 governance rules ·
G-8 production readiness.
