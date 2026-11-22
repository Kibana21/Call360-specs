# Call360 — roadmap of checkpoints

**Updated 2026-11-23, with MIG-1.** This is an index of where each line of work stands and what has been *proposed*
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
| MIG-1 | Script Studio retirement readiness — **assessment only, presented for review** | `51_…` |

None of this is business UX, screen-reader, Compliance or production acceptance.

## Proposed — NOT authorised

| Checkpoint | What | Needs first |
|---|---|---|
| **SHARED-1** *(recommended next)* | Assignment Rules and Finding Rules stand on their own: a rule has its own market and an optional script target; permissions of their own | rulings B-1, B-2 (`51_…` §8) |
| Rulings M-1 … M-5, B-3 … B-7 | re-prompt limits; conversational delivery; lifecycle failure behaviour; unknown policy; which scripts migrate; effective dating and withdrawal; evidence required; read access; approvals; protected records | the owner, Compliance |
| OPS-1 | a survey assigned to a real case — assessment first | SHARED-1; borders VOICE-1 |
| Historical script view | read-only view of a published script version, from Call Detail and Review Workbench | — |
| MIG-2 | controlled content migration | SHARED-1; M-1 … M-5; B-1 |
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
