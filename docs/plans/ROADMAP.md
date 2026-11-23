# Call360 — roadmap of checkpoints

**Updated 2026-11-23, with APPL-X1.** This is an index of where each line of work stands and what has been *proposed*
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
| APPL-X1 | Survey Applicability Studio — architecture, evaluator and working prototype; **built, presented for design acceptance**; no migration | `56_…`, `57_…`, `58_…` |

None of this is business UX, screen-reader, Compliance or production acceptance.

## Proposed — NOT authorised

| Checkpoint | What | Needs first |
|---|---|---|
| **APPL-X2** *(next in the applicability programme)* | Variable Library, Profiles and Condition Lab, persisted | acceptance of APPL-X1; rulings AP-1…AP-10 (D-382) |
| APPL-X3 … X6 | policy and designer; scenarios and publication; Survey Studio integration; legacy survey-assignment retirement | each its own authorisation; `58_…` |
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
