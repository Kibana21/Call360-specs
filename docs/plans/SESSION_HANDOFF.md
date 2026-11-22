# Call360 — Session handoff

**Last updated:** 2026-11-22, ASG-2A accepted as technically verified (simulation-only mechanics); development database migrated to `0031`; ASG-2B (coordinated multi-survey simulation — SIMULATION ONLY) built and technically verified, awaiting the owner's review; SS-03B, ASG-1, ASG-2A and ASG-2B all UNCOMMITTED; nothing authorised next.
the only current-state section.** §1–§7 are current reference material; §8 onward are historical checkpoint records kept
for traceability.
**Process:** strict specification-driven development (workspace `CLAUDE.md` §10). Never implement without the owner's
explicit authorisation of the named checkpoint; never advance automatically; never commit, push or merge without
authorisation; never mark anything accepted without the owner's explicit words.
**Secrets:** this document contains no passwords, API keys or encryption keys. They live only in gitignored local files
(§4).

## 0. Current state — read this first (2026-11-19)

> **Update 2026-11-22 (UX-HOME-1 + NAV-1) — read this block first; it supersedes the blocks below where they differ.**
> - **The owner committed and pushed everything through the first UX-HOME-1 version** (backend `92aa725`, frontend
>   `ea8a354`, specs `76d70f2`). E2E-1 has no explicit acceptance message on record. The assistant never commits.
> - **UX-HOME-1 + NAV-1 — BUILT AND TECHNICALLY VERIFIED, awaiting the owner's review; NOT accepted; uncommitted.**
>   Documents: `survey-studio/47_…` (assessment and design), `48_…` (report), contract §21, D-321…D-329,
>   `docs/product/SCREEN_NAMING_AND_ROUTES.md` (primary navigation amended to five groups). `46_…` is superseded.
>   - NAV-1: `src/app/nav.ts` (five groups, sub-pages, `placeOf`), `AppShell.tsx`, `src/styles/nav.css`. Every earlier
>     route, label and guard is kept. Script Studio is kept (tag "Legacy"). Do not touch `app.css`, `DEVIATIONS.md`,
>     `f6-checks.ts`, `script-studio.spec.ts`.
>   - Survey Studio (persisted): `persist/Workspace.tsx` (views `?view=surveys|blocks`), `Inspector.tsx`
>     (`?inspect=KIND~code~version`), `SurveyOverview.tsx` (`?survey=CODE`), `RulesExplorer.tsx`
>     (`/survey-studio/rules`), `SimulationHub.tsx` (`/survey-studio/simulation`), `workspaceApi.ts`.
>   - Backend, read-only, NO migration: `GET /api/v1/survey-definitions/workspace` (with `surveys[]`),
>     `facts.branching` on library modules; test `tests/test_survey_workspace.py`. Browser-test setup has a read-only
>     cross-platform identity `e2e.survey.platform`.
>   - Verified: backend 1,009; vitest 624; Playwright persisted 27, prototype 13, standard 33; golden 82 / 14;
>     OpenAPI 271 operations, 512 schemas, SHA-256 `e7aface9…c4e3b20`.
>   - **Independent authoring of building blocks is NOT built** (D-328): it is a design ruling (LIB-D-1), proposed as
>     LIB-2, not authorised. The workspace only says where each kind is made.
>   - Open with the owner: `48_…` §7 (L-1…L-8), D-329 (eight choices), LIB-2, commits.
> - Development database stays at `0035`; nothing was migrated, reset or re-seeded.
> - **Nothing is authorised next.**
>
> **Update 2026-11-22 (E2E-1)**
> - **Accepted by the owner:** EVAL-2B as TECHNICALLY VERIFIED, simulation only (D-312) — not production, Compliance
>   or spoken-delivery acceptance. D-311 reconciled (D-313). **Technical gap TG-1 is recorded and open** (D-314):
>   queued follow-up order from multi-select answers is not verified edge by edge; never claim full branch fidelity.
> - **Development database: `0035_survey_execution_assurance`** (owner-authorised, D-315) — the head. Backup
>   `_db_backups/call360_dev_before_0035_20261122.dump` (SHA-256 `c69245f9…9189524`); `RESTORE.md` "Rolling 0035
>   back". Execution assurance is on in dev; five synthetic assurance results exist, so `0035` cannot be downgraded.
>   **`SG-ILP-HIGH-RISK v2` is still bound to `S-DEV-EVAL-SHARED`; do not change it back or add a binding unasked.**
>   Never run `make migrate`, `make seed`, or reset development.
> - **Commits:** owner's commits are backend `ed3e51b`, frontend `e79c4e0`, specs `c43f4f5`. **EVAL-2B and E2E-1 are
>   uncommitted on top.** The assistant never commits or pushes without authorisation.
> - **E2E-1 — BUILT AND TECHNICALLY VERIFIED, awaiting the owner's review; NOT accepted.** Documents:
>   `survey-studio/44_…` (baseline, handoffs, acceptance matrix), `45_…` (report), contract §20, D-312…D-320.
>   - Added: ONE read-only operation `GET /api/v1/survey-evaluation/journey-trace` (`journey_trace.py`,
>     `app/api/survey_journey_trace.py`; registered with execution assurance; no table, migration, setting or
>     permission), the "Application journeys" page (`persist/JourneyPage.tsx`, routes `/survey-studio/journeys…`),
>     harness `tests/test_zz_e2e1_journey.py`, browser walkthrough `e2e/persisted/zzz-e2e1.persisted.ts`.
>   - The trace computes nothing; five dimensions are kept apart; eligibility is always NOT_ESTABLISHED; the control
>     policy is always NAMED EXPLICITLY; input consistency and lineage stay UNVERIFIED.
>   - Verified: backend 1,008 passed; golden 82 / 14 unchanged; vitest 612; Playwright persisted 26, prototype 13,
>     standard 33; OpenAPI 270 operations, 511 schemas, SHA-256 `dbc7b00b…cdb4edf01`.
>   - Open with the owner: `45_…` §11 (TG-1…TG-7, BP-1…BP-11), D-320 (eight choices), commits, and the proposed
>     next checkpoint (`45_…` §13: DEC-1 decision closure pack recommended; ASSURE-2 as the engineering alternative).
> - **Nothing is authorised next.**
>
> **Update 2026-11-22 (EVAL-2B)**
> - **Accepted by the owner:** EVAL-2A as TECHNICALLY VERIFIED, simulation only (D-301) — not Compliance approval.
>   D-300 reconciled one by one (D-302): (a), (c), (d), (e), (h) accepted; (i), (j) technical; **(b), (f), (g) carry
>   a business or Compliance question and are NOT approved in that respect.** D-291 (d), (e) stay open (D-303).
> - **Development database: `0034_survey_control_policy`** (owner-authorised, D-304). Backup
>   `_db_backups/call360_dev_before_0034_20261122.dump` (SHA-256 `d7365ca7…958c22be`); `RESTORE.md` "Rolling 0034
>   back". Control policies are on in dev. Dev now holds synthetic policy `POL-DEV-SYNTHETIC`, survey
>   `S-DEV-EVAL-SHARED`, mapping revisions 2, and **rule `SG-ILP-HIGH-RISK v2` is re-bound to `S-DEV-EVAL-SHARED`**
>   (the binding to `S-DEV-FI2-WALKTHROUGH` is superseded). `0034` cannot be downgraded there.
>   **Dev is NOT at `0035`; NOT authorised. `make migrate` goes to the head — never run it.**
> - **Commits:** the owner committed and pushed SS-03B … EVAL-2A himself (backend `ed3e51b`, frontend `e79c4e0`,
>   specs `c43f4f5`). **EVAL-2B is uncommitted on top.** The assistant never commits or pushes without authorisation.
> - **EVAL-2B — BUILT AND TECHNICALLY VERIFIED, awaiting the owner's review; NOT accepted.** Documents:
>   `survey-studio/42_…` (assessment and design), `43_…` (report, with the proposed E2E-1 boundary in §11),
>   contract §19, decisions D-301…D-311.
>   - It VERIFIES the trace the authoritative engine records; it executes nothing and computes no control outcome.
>     Eight checks per survey, five per coordinated journey; statuses `VERIFIED`, `INCOMPLETE`,
>     `DEVIATION_DETECTED`, `INTEGRITY_FAILED`, `NOT_ASSESSABLE`; eligibility always `NOT_ESTABLISHED`.
>   - Code: backend `execution_assurance.py` (pure), `assurance.py`, `app/api/survey_execution_assurance.py` (3 ops),
>     migration `0035_survey_execution_assurance` (MIGRATION_HEAD; two insert-only tables; test schema only), setting
>     `survey_execution_assurance_enabled`; frontend `persist/ExecutionAssurance.tsx` inside the Evaluation Workbench;
>     tests `tests/test_survey_execution_assurance.py`; e2e `zz-eval2b`.
>   - A deviation cannot occur naturally: negative tests use TAMPERED copies of real runs, named as such. Never
>     present one as a defect of the executor.
>   - Verified: backend 1,006 collected, none failed; all 82 golden runs raise no finding; vitest 612; Playwright
>     persisted 25, prototype 13, standard 33; OpenAPI 269 operations, 509 schemas, SHA-256 `e1b44eb7…b9a762d5`.
>   - Open with the owner: `43_…` §10 (policy questions), D-311 (eight choices), development migration `0035`,
>     commits, and whether to authorise E2E-1.
> - **Nothing is authorised next.** Do not start E2E-1.
>
> **Update 2026-11-22 (EVAL-2A)**
> - **Accepted by the owner:** EVAL-1 as TECHNICALLY VERIFIED, simulation only (D-289). D-287 `ALL_REQUIRED` approved
>   as a declared technical operator, not an insurance policy (D-290). D-288 reconciled one by one (D-291): (a), (c)
>   accepted; (f) closed; (b), (g) technical, not separately ruled; **(d), (e) NOT approved** (Compliance).
>   `SET_MATCH` approved and built (D-299). **The owner committed and pushed everything himself on 2026-11-22 15:52**
>   (backend `ed3e51b`, frontend `e79c4e0`, specs `c43f4f5`); six specs files changed after that are uncommitted.
>   The assistant still never commits or pushes without authorisation.
> - **Development database: `0033_survey_control_evaluation`** (owner-authorised, D-292). Backup
>   `_db_backups/call360_dev_before_0033_20261122.dump` (SHA-256 `349dbbba…98430918`); `RESTORE.md` "Rolling 0033
>   back". Evaluation is on in dev; the three dev identities hold the evaluation permissions; two synthetic mappings
>   and two evaluations exist, so `0033` cannot be downgraded there. **Dev is NOT at `0034`; NOT authorised.
>   `make migrate` goes to the head — never run it.**
> - **EVAL-2A — BUILT AND TECHNICALLY VERIFIED, awaiting the owner's review; NOT accepted.** Documents:
>   `survey-studio/39_…` (assessment and design), `40_…` (report), `41_…` (migration `0034`), contract §18,
>   decisions D-289…D-300, gaps G-E8…G-E10.
>   - The control register is not altered. A governed **control policy** `(market, code, revision)` lists register
>     controls with purpose, **obligations**, applicability and required evidence. A control instance is
>     `(evaluation, control, obligation)`. Mappings (EVAL-1) name the policy requirement each entry supplies.
>   - **Migration `0034` is PURELY ADDITIVE** (D-298): six new tables, no existing table altered. The first draft
>     (obligation column and key replacement on the EVAL-1 tables) was withdrawn. Policy-scoped results live in
>     `survey_obligation_result` / `_observation` / `_finding`, linked by `survey_evaluation_policy`.
>   - Four statuses kept apart: processing status, control outcome, coverage, operational compliance eligibility
>     (always `NOT_ESTABLISHED`). `COMPLETE_WITHIN_POLICY_SCOPE` is not `SATISFIED`.
>   - Code: backend `control_policy.py`, `policy_evaluation.py`, `app/api/survey_control_policies.py` (10 ops),
>     `SET_MATCH` in `answer_evaluation.py` (`ALL_METHODS`; `METHODS` unchanged for Script Studio), setting
>     `survey_control_policy_enabled`; frontend `persist/ControlBuilder.tsx` at `/survey-studio/controls`,
>     policy-aware `EvaluationWorkbench.tsx`; tests `tests/test_survey_control_policy.py`; e2e `zz-eval2a`.
>   - Verified: backend 917 collected, none failed; golden 82 runs and 14 plans unchanged; vitest 612; Playwright
>     persisted 24, prototype 13, standard 33; OpenAPI 266 operations, 505 schemas, SHA-256 `91ed256e…7806d62c`.
>   - Open with the owner: D-291 (d), (e); D-300 (ten choices); development migration `0034`; commits.
> - **Nothing is authorised next.** Do not start EVAL-2B.
>
> **Update 2026-11-22 (EVAL-1)**
> - **Accepted by the owner:** ASG-2B is TECHNICALLY ACCEPTED for simulation-only coordinated multi-survey execution
>   (D-271); D-270 choices confirmed (D-272). **Everything since LIB-1 is STILL UNCOMMITTED** — SS-03B, its closure,
>   ASG-1, ASG-2A, ASG-2B, EVAL-1 — and no commit authorisation has been given. Never push.
> - **Development database: NOW AT `0032_survey_coordinated_sim`** (D-273). Backup
>   `_db_backups/call360_dev_before_0032_20261122.dump` (SHA-256 `b4b87cd9…47d18b7e`); `RESTORE.md` has "Rolling 0032
>   back". `SURVEY_COORDINATED_SIMULATION_ENABLED=true` is in the gitignored dev `.env`. Dev holds four coordinated
>   simulations (all SIMULATION records). **Development is NOT at `0033` and that is NOT authorised**: EVAL-1 is off
>   there (operations → 404; the simulators say "not switched on"). **`make migrate` goes to the head — never run it.**
> - **D-274 done:** a composite carries `states.coordinated_simulation.available`; the start control is offered only
>   when the composite is PERMITTED and the server has the feature on.
> - **EVAL-1 — BUILT AND TECHNICALLY VERIFIED, awaiting the owner's review; NOT accepted.** Reports
>   `survey-studio/37_…` (assessment and design, written first) and `38_…` (implementation); contract §17;
>   decisions D-271…D-288, gaps G-E1…G-E7.
>   - Grain: journey → survey execution → **control instance** → evidence observation. Survey is never the grain.
>   - Reused unchanged: `answer_evaluation.evaluate_one` / `configure`, `finding_engine.generate`, the finding rule
>     set lifecycle, Survey Studio conditions, the simulation and coordination services. No existing engine or
>     Script Studio file was modified.
>   - New: `control_evaluation.py` (pure), `control_mapping.py`, `journey_evaluation.py`,
>     `app/api/survey_evaluations.py` (10 operations, `/api/v1/survey-evaluation`), migration
>     `0033_survey_control_evaluation` (six insert-only tables; permissions `survey.evaluation.read`,
>     `survey.evaluate`, granted to nobody), setting `survey_evaluation_enabled` (off; needs simulation).
>     Frontend: `persist/evalApi.ts`, `persist/EvaluationWorkbench.tsx`, route
>     `/survey-studio/evaluations/:evaluationId`, entry "Control evaluation" on both simulators.
>   - **D-287 is PROPOSED and needs the owner's ruling:** the control outcome is a new semantic. One combination
>     exists, `ALL_REQUIRED`, and only because each governed mapping declares it. Do not present it as approved.
>   - Coverage is always `NOT_ASSERTED`; mapping authoring has an API and no screen; contradictory evidence is
>     demonstrated at engine level only; all mappings, rules and severities in tests are synthetic fixtures.
>   - Verified: backend 831 collected, 0 failed; 82 golden runs and 14 plans unchanged; vitest 612; Playwright
>     persisted 23, prototype 13, standard 33; OpenAPI 256 operations, 490 schemas, SHA-256 `97a911a9…ed9b5ce5`.
>   - `MIGRATION_HEAD` is `0033_survey_control_evaluation`; the test schema is at head.
> - **Nothing is authorised next.** Open with the owner: D-287, D-288, development migration `0033`, commits.
>
> **Update 2026-11-22 (ASG-2B)**
> - **Accepted by the owner as TECHNICALLY VERIFIED:** ASG-2A — multi-survey assignment and composite call-plan
>   assembly, simulation-only mechanics (D-259); D-258.1/.2/.3 confirmed (D-260). The stand-in "replacement" and "CI
>   rider" conditions are NOT proof of real requirements. **Everything since LIB-1 is STILL UNCOMMITTED** — SS-03B,
>   its closure, ASG-1, ASG-2A, ASG-2B — and no commit authorisation has been given.
> - **Three separate states (D-261, done):** every composite carries `states` — `call_plan`
>   (`COMPUTABLE` / `NOT_COMPUTABLE` / `UNRESOLVED`), `coordinated_simulation` (`PERMITTED` / `BLOCKED` + codes),
>   `operational_call_eligibility` (always `NOT_ESTABLISHED`) — and the screen shows them as three lines. Never
>   present a READY plan as implying either of the other two.
> - **Development database: NOW AT `0031_survey_assignment_groups`** (D-262). Backup
>   `_db_backups/call360_dev_before_0031_20261122.dump` (SHA-256 `53e2de71…eefa29ac6`); `RESTORE.md` extended.
>   `SURVEY_ASSIGNMENT_GROUPS_ENABLED=true` is in the gitignored dev `.env`. In dev: two bindings
>   (`SG-SALES-VERIFY v2` → `DEV-CHECK-AD5AEA8F`; `SG-ILP-HIGH-RISK v2` → `S-DEV-FI2-WALKTHROUGH`) and two groups
>   (`DEV-PRIMARY` position 1; `DEV-ADD-SYNTHETIC` position 2, named as a synthetic stand-in). **`0031` and `0030`
>   can no longer be downgraded. Withdrawing a binding or group does NOT enable a downgrade (tested):** the row
>   stays and the migration refuses. Ways back: switch the setting off, or a full restore.
>   **Development is NOT at `0032`**: ASG-2B is off there (start → 404). **`make migrate` upgrades to the head —
>   never run it without approval;** use `uv run alembic upgrade <revision>`.
> - **ASG-2B — BUILT AND TECHNICALLY VERIFIED, awaiting the owner's review. NOT accepted. SIMULATION ONLY.
>   UNCOMMITTED.** Report `docs/plans/survey-studio/36_ASG-2B_IMPLEMENTATION_REPORT.md`; contract `04_…` §16;
>   decisions D-259…D-270; evidence `docs/acceptance/evidence/ASG-2B/`.
>   - **Design:** `app/domain/survey/coordination.py` is a thin layer over `simulation.create/advance/state`. Each
>     survey of the composite has its own SS-03B simulation; the coordinator stores only which survey it started
>     and why (`survey_coordinated_simulation`, `…_step`), and computes everything else on reading.
>   - **Rules (simulation only):** start refused with a code unless selection `RESOLVED`, order governed, every
>     plan computable, no survey version twice, composite unchanged (`SELECTION_UNRESOLVED`, `ORDER_UNRESOLVED`,
>     `PLAN_BLOCKED`, `DUPLICATE_SURVEY_REQUIREMENT_UNRESOLVED`, `COMPOSITE_STALE`). `COMPLETED` starts the next
>     survey; `PENDING` stays; `POLICY_UNRESOLVED` stops; any other ending → `CROSS_SURVEY_POLICY_UNRESOLVED`.
>     `ALL_SURVEYS_COMPLETED` is progress, not an outcome. Nothing is de-duplicated.
>   - Backend: `app/api/survey_coordinated_simulations.py` (three operations under `/api/v1/survey-assignment`),
>     migration **`0032_survey_coordinated_sim`**, setting **`survey_coordinated_simulation_enabled`** (off by
>     default). OpenAPI `e0add7fc…` (246 operations, 477 schemas; additive). Head rule: `OPTIONAL_REVISIONS` in
>     `app/main.py`, now six optional revisions.
>   - Frontend: `persist/CoordinatedSimulation.tsx` at `/survey-studio/coordinated-simulations/:id`, started from
>     the composite on the Survey assignment page; `AnswerForm` exported from `ServerSimulation.tsx`.
>   - Tests: `tests/test_survey_coordination.py` (resets the schema before and after itself); the browser journey is
>     the SECOND test in `e2e/persisted/zz-asg2a.persisted.ts` and relies on the first one's data.
>   - Verified: backend **825**; frontend **612** unit; persisted journeys **22/22**; prototype **13/13**;
>     standard **33/33**; 82/82 golden runs and 14/14 golden plans; lint, types, OpenAPI, build clean.
> - **Proposed next, NOT authorised:** EVAL-1 — evaluation and findings integration, simulation only; its boundary
>   is `36_…` §15. The existing evaluation and finding code has NOT been assessed yet.
> - **Open items:** OR-1 (retention), OR-2, OR-3, the input mapping, and the policy gaps in `36_…` §14.
> - **Not mine, left alone:** in specs, `docs/acceptance/evidence/LIB-1/screens.zip` deleted and a `.DS_Store`
>   modified in the working tree.
> - **Not authorised:** committing or pushing anything; migrating development to `0032`; EVAL-1; any operational
>   assignment, call, voice provider, consent, cross-survey or non-answer behaviour; Script Studio changes.
>
> **Update 2026-11-22 (ASG-2A) — superseded by the block above where they differ** (in particular: development is at
> `0031`; the migration head is `0032`; composites carry three separate states).
> - **Accepted by the owner as TECHNICALLY VERIFIED:** the SS-03B security closure, development migration `0029`,
>   and **ASG-1 for SINGLE-SURVEY assignment** (D-246). The binding is an interim adapter. **Everything since LIB-1
>   is STILL UNCOMMITTED** — SS-03B, its closure, ASG-1, ASG-2A — and no commit authorisation has been given.
> - **ASG-1 read access (D-247, done):** permission **`survey.assignment.read`** (migration `0030`, granted to no
>   role) is required by EVERY `/api/v1/survey-assignment/*` operation, writes included. `survey.read` opens none of
>   it. The policy no longer returns a rule's script target. In development the three `dev.survey.*` identities
>   hold it; in browser tests author, checker, publisher and simulator do, the reader does not.
> - **Development database: NOW AT `0030_survey_assignment`** (D-248). Backup
>   `_db_backups/call360_dev_before_0030_20261122.dump` (SHA-256 `0ab7b34e…9c3aaa5e`); `RESTORE.md` extended.
>   `SURVEY_ASSIGNMENT_ENABLED=true` is in the gitignored dev `.env`. One synthetic binding is published in dev
>   (`SG-SALES-VERIFY v2` → `DEV-CHECK-AD5AEA8F` v1.0), so **`0030` can no longer be downgraded** (switch the
>   setting off, withdraw the binding, or full restore). The page works at `/survey-studio/assignment` as
>   `dev.survey.author`. **Development is NOT at `0031`**: ASG-2A is off there (`…/groups` → 404).
>   **`make migrate` upgrades to the head — never run it without approval;** use
>   `uv run alembic upgrade <revision>`.
> - **ASG-2A — BUILT AND TECHNICALLY VERIFIED, awaiting the owner's review. NOT accepted. SIMULATION ONLY.
>   UNCOMMITTED.** Semantics (written first) `34_ASG-2A_GROUPING_AND_MATCHING_SEMANTICS.md`; report
>   `35_ASG-2A_IMPLEMENTATION_REPORT.md`; contract `04_…` §15; decisions D-249…D-258, OR-2, OR-3; evidence
>   `docs/acceptance/evidence/ASG-2A/`.
>   - **Design:** a **requirement group** is a governed, versioned set of rule versions that compete for ONE
>     requirement — `PRIMARY`, `ADD_REQUIRED` or `ALTERNATIVE` — with a purpose and an optional governed
>     `sequence`. The existing engine runs once PER GROUP over that group's rules (re-targeted through ASG-1
>     bindings). Each selected survey gets its own SS-03B plan; the composite refers to them. Nothing is merged.
>   - **Never invented, always reported:** ordering (`UNRESOLVED` unless every selected group has a distinct
>     position), cross-survey continuation (`cross_survey_policy: UNRESOLVED` with more than one survey), input
>     consistency (`UNVERIFIED`). `plan_status` is `READY` only when selection is `RESOLVED`, ordering governed and
>     every plan `READY`; the database CHECKs it.
>   - Backend: `app/domain/survey/assignment_groups.py`, `app/api/survey_assignment_groups.py` (seven operations),
>     migration **`0031_survey_assignment_groups`**, setting **`survey_assignment_groups_enabled`** (off by
>     default). `assignment.decide_candidates` is the shared decision step. OpenAPI `2b3b0c8e…` (243 operations,
>     475 schemas; additive). Head rule: `OPTIONAL_REVISIONS` in `app/main.py`, now five optional revisions.
>   - Frontend: `persist/AssignmentGroups.tsx` (groups section, composite result) in the same Survey assignment
>     page; `?composite=<id>` opens a recorded composite.
>   - **Stand-ins (OR-3):** the rule language has no "replacement" or "CI rider" field; tests use premium frequency
>     Single and sales channel Bancassurance. **OR-2:** the existing rule validation refuses equally ranked rules
>     that can both match, so complementary rules need different priorities.
>   - Tests: `tests/test_survey_assignment_groups.py` (resets the schema before and after itself, as the ASG-1 test
>     does); `e2e/persisted/zz-asg2a.persisted.ts` runs after `zz-asg1`.
>   - Verified: backend **822**; frontend **612** unit; persisted journeys **21/21**; prototype **13/13**;
>     standard **33/33**; 82/82 golden runs and 14/14 golden plans; lint, types, OpenAPI, build clean.
> - **Proposed next, NOT authorised:** ASG-2B — coordinated simulation; its boundary is `35_…` §15. EVAL-1 remains
>   proposed in `33_…` §11.
> - **Open items:** OR-1 (retention), OR-2, OR-3, and the unresolved policy register in `35_…` §14.
> - **Lesson for this workspace:** do not change `MIGRATION_HEAD` or add a module that `app/main.py` imports while
>   a test run or the dev server depends on the old state; and never put backticks in an unquoted shell heredoc.
> - **Not mine, left alone:** in specs, `docs/acceptance/evidence/LIB-1/screens.zip` deleted and a `.DS_Store`
>   modified in the working tree.
> - **Not authorised:** committing or pushing anything; migrating development to `0031`; ASG-2B; EVAL-1; any
>   operational assignment, call, voice provider, consent, cross-survey or non-answer behaviour; Script Studio
>   changes.
>
> **Update 2026-11-22 (ASG-1) — superseded by the block above where they differ** (in particular: assignment reads
> need `survey.assignment.read`, not `survey.read`; development is at `0030`; the migration head is `0031`).
> - **SS-03B: ACCEPTED as TECHNICALLY VERIFIED** (D-234; decisions confirmed D-237). Not production readiness.
>   **Still UNCOMMITTED** — the owner has not committed it and has given no commit authorisation.
> - **SS-03B closure (done, uncommitted):**
>   - **`survey.simulate`** — created by migration `0029`, granted to no role. Creating a simulation, giving an input
>     and generating a call plan need it; reading a simulation or plan needs `survey.read`. In development only
>     `DEV_SURVEY_AUTHOR` (`dev.survey.author`) holds it. Browser tests use `e2e.survey.simulator`.
>   - **Execution contract and drift** — `execution.CONTRACT = "call360.survey.execution/1"`; a simulation records
>     its contract and `initial_run_sha256`; on read the run is recomputed, and a difference (or another contract)
>     gives status `REPLAY_DRIFT` and refuses further inputs (`409`). **Change `CONTRACT` whenever the engine's
>     results can change.** Call plans record `plan_contract` and report `recompute_consistent`.
>   - **OR-1 (open):** no retention or clean-up of simulation, plan or selection records. No period was invented.
> - **Development database: NOW AT `0029_survey_simulation`** (D-236, owner-authorised). Backup
>   `_db_backups/call360_dev_before_0029_20261122.dump` (SHA-256 `eb725102…f373350d`); `RESTORE.md` extended.
>   `SURVEY_SIMULATION_ENABLED=true` is in the gitignored dev `.env`. Simulation works on the dev server
>   (`/survey-studio/surveys/DEV-CHECK-AD5AEA8F/simulate` as `dev.survey.author`). `0029` can be downgraded (drops
>   the three tables and the permission); `0028` cannot. **Development is NOT at `0030`**: ASG-1 is off there
>   (`/api/v1/survey-assignment/*` → 404). **`make migrate` upgrades to the head — do not run it without approval;**
>   use `uv run alembic upgrade <revision>` for one revision.
> - **ASG-1 — BUILT AND TECHNICALLY VERIFIED, awaiting the owner's review. NOT accepted. SIMULATION ONLY.
>   UNCOMMITTED.** Report `docs/plans/survey-studio/33_ASG-1_IMPLEMENTATION_REPORT.md`; contract `04_…` §14;
>   decisions D-238…D-245; evidence `docs/acceptance/evidence/ASG-1/`.
>   - **Design:** the existing rule loader (`rule_inputs.published_candidates`) and engine (`rule_engine.evaluate`)
>     are reused unchanged. A rule cannot target a survey version without altering Script Studio tables, so one new
>     governed artifact, the **binding** (published rule version → published survey version), re-targets each
>     candidate before the engine decides. A winning rule with no binding fails closed as `SURVEY_NOT_BOUND`.
>   - Backend: `app/domain/survey/assignment.py`, `app/api/survey_assignments.py` (ten operations under
>     `/api/v1/survey-assignment`), migration **`0030_survey_assignment`** (`survey_assignment_binding`,
>     `…_binding_event` with an identity guard trigger, `…_evaluation` with `record_class = 'SIMULATION'`,
>     `…_simulation`), setting **`survey_assignment_enabled`** (off by default; needs simulation). Head rule:
>     `OPTIONAL_REVISIONS` in `app/main.py`. OpenAPI `38f2034b…` (236 operations, 467 schemas; additive).
>   - Governance of a binding: propose `survey.edit`, approve `survey.approve`, publish `survey.publish` — three
>     different people, enforced by service and database trigger. Select and simulate: `survey.simulate`.
>   - Frontend: `persist/AssignmentPage.tsx` at `/survey-studio/assignment` (linked from the Surveys list);
>     the Simulator opens an existing simulation with `?simulation=<id>&assignment=<evaluation id>`.
>   - Tests: `tests/test_survey_assignment.py` **resets the test schema before and after itself** (it publishes
>     priority-1 rules); `e2e/persisted/zz-asg1.persisted.ts` is named to run **last** (FI-1 expects no surveys).
>   - Verified: backend **818**; frontend **612** unit; persisted journeys **20/20**; prototype **13/13**;
>     standard **33/33**; 82/82 golden runs and 14/14 golden plans; lint, types, OpenAPI, build clean.
> - **Proposed next, NOT authorised:** EVAL-1 — evaluation and findings integration, simulation only (`33_…` §11).
> - **Undecided and untouched:** D-NA-1…17; spoken-field permissions; wording approval; native survey targets for
>   rules; the mapping between assignment inputs and call-plan facts; live-call eligibility (G-1…G-8); assignment of
>   surveys to real cases; OR-1.
> - **Not mine, left alone:** in specs, `docs/acceptance/evidence/LIB-1/screens.zip` deleted and a `.DS_Store`
>   modified in the working tree.
> - **Not authorised:** committing or pushing anything; migrating development to `0030`; any operational
>   assignment, call, voice provider, consent or non-answer behaviour; Script Studio changes; anything after ASG-1.
>
> **Update 2026-11-22 (SS-03B) — superseded by the block above where they differ** (in particular: simulation now
> needs `survey.simulate`, not `survey.read`; development is at `0029`; the migration head is `0030`).
> - **LIB-1: TECHNICALLY ACCEPTED** (D-222), subject to the legacy library-discovery correction — **closed**:
>   `GET /survey-library/{kind}` now lists only versions pinned by a published version in the reader's markets, with
>   the library setting on or off (D-223; contract `04_…` §13.1). LIB-1 was committed and pushed by the owner at 09:02
>   (backend `182f6e5`, frontend `9f497d5`, specs `755bf00`). LIB-1 UX limitations are carried in `32_…` §11.
> - **Development database: NOW AT `0028_survey_library`** (D-224, owner-authorised). Backup
>   `_db_backups/call360_dev_before_0028_20261122.dump` (SHA-256 `d46e74d9…4f0017`), restore steps in
>   `_db_backups/RESTORE.md`. `SURVEY_LIBRARY_ENABLED=true` is in the gitignored dev `.env`. The walkthrough added two
>   synthetic drafts (`S-DEV-LIB-PIN`, `S-DEV-LIB-COPY`) and six issued codes, so **`0028` can no longer be downgraded**;
>   the way back is a full restore, or switching the library off. **Development is NOT at `0029`**; do not run
>   `make migrate` without the owner's approval.
> - **SS-03B — BUILT AND TECHNICALLY VERIFIED, awaiting the owner's review. NOT accepted. SIMULATION ONLY.
>   UNCOMMITTED in all three repositories (no commit authorisation).** Report
>   `docs/plans/survey-studio/32_SS-03B_IMPLEMENTATION_REPORT.md`; contract `04_…` §13; decisions D-222…D-233;
>   evidence `docs/acceptance/evidence/SS-03B/`.
>   - Backend, pure: `app/domain/survey/execution.py` (`execute`, `execute_inputs`; statuses `PENDING`,
>     `POLICY_UNRESOLVED`, `TERMINAL`), `wording.py` (`render`, `format_value`), `callplan.py` (`assemble`; schema
>     `call360.survey.call-plan/1`; fingerprint). **82/82 golden runs, 14/14 golden plans; no fixture changed.**
>   - Backend, records and API: migration **`0029_survey_simulation`** (insert-only `survey_simulation`,
>     `survey_simulation_input`, `survey_call_plan`, each `record_class = 'SIMULATION'` by CHECK; no link to anything
>     operational); `simulation.py` (a run is never stored — inputs are replayed); `app/api/survey_simulations.py`,
>     five operations, `survey.read`, market-scoped, CSRF, rate-limited, audited; setting
>     **`survey_simulation_enabled`** (off by default; needs `survey_definitions_enabled`). Head rule in `app/main.py`
>     `acceptable_migration_heads`: simulation on → `0029`; library on → `0028`/`0029`; survey definitions on →
>     `0027`…`0029`; none → `0026`…`0029`. OpenAPI `5799e44f…` (226 operations, 457 schemas; additive).
>   - Frontend: in persisted mode the Simulator and Call plan screens have a switch — **Published version · Call360
>     server** (default) or **Draft · browser preview**. `persist/simApi.ts`, `serverRun.ts` (comparison and trace
>     wording), `ServerSimulation.tsx`, `ServerCallPlan.tsx`. The browser engine is compared with the server in view.
>     `policyOf` in `model/types.ts`: an interrupt with no policy means `STOP_ESCALATE` (a real difference found by
>     the cross-engine test on F4, corrected).
>   - Generated: `docs/plans/survey-studio/python-results/` by
>     `Call360-backend/scripts/export_survey_python_results.py` (`--check`); read by
>     `persist/serverRun.test.ts`. Regenerate it whenever the engine's output changes.
>   - Verified: backend **814**; frontend **612** unit; persisted journeys **19/19** (14 earlier + 5 SS-03B;
>     simulation ON in that config); prototype **13/13**; standard **33/33**; lint, types, OpenAPI, build clean.
> - **Simulation is OFF on the development server** (dev is at `0028`): the five routes return 404 there and the
>   server panels say so. To enable later, with approval: back up, apply `0029` only, add
>   `SURVEY_SIMULATION_ENABLED=true` to the gitignored `.env`.
> - **Undecided and untouched:** D-NA-1…17 (no-answer, refusal, repeats, timeouts, consent), spoken-field
>   permissions, wording approval, live-call eligibility (G-1…G-8), assignment of surveys to cases.
> - **Not mine, left alone:** in specs, `docs/acceptance/evidence/LIB-1/screens.zip` shows as deleted and a
>   `.DS_Store` as modified in the working tree.
> - **Not authorised:** committing or pushing SS-03B or the LIB-1 correction; migrating development to `0029`; any
>   non-answer or consent behaviour; live eligibility; real calls; Genesys / GPT Live / Azure Speech; Script Studio
>   changes; anything after SS-03B.
>
> **Update 2026-11-22 (LIB-1) — superseded by the block above where they differ.**
> - **FI-2: ACCEPTED as TECHNICALLY VERIFIED — REAL REVIEW AND PUBLICATION** (D-213); limitation D-214 (checker sees
>   frozen content as a table). FI-2 was committed and pushed by the owner at 05:38 (backend `29fec70`, frontend
>   `7570972`, specs `e8920b0`).
> - **Owner decisions LIB-D-1…5 (D-215…D-219)** and **"AUTHORIZE LIB-1"** (D-220).
> - **LIB-1 — BUILT AND TECHNICALLY VERIFIED, awaiting the owner's review. NOT accepted. UNCOMMITTED in all three
>   repositories (no commit authorisation for LIB-1).** Report
>   `docs/plans/survey-studio/31_LIB-1_IMPLEMENTATION_REPORT.md`; contract `04_…` §12; evidence
>   `docs/acceptance/evidence/LIB-1/`.
>   - Backend: migration **`0028_survey_library`** (sequence `survey_code_seq`, insert-only `survey_issued_code`);
>     setting **`survey_library_enabled`** (off by default; needs `survey_definitions_enabled`); `library_router`
>     with `GET /survey-components`, `GET /survey-components/{kind}/{code}/{version}`,
>     `POST /survey-definitions/{id}/codes`. Always on: a draft may only reference its own or PUBLISHED assets
>     (`REFERENCE_NOT_PUBLISHED`); a code belongs to its survey (`CODE_OWNED_ELSEWHERE`). With the library on: new
>     codes must be server-issued (`CODE_NOT_ISSUED`). OpenAPI `88baaf2c…` (221 operations).
>   - Frontend: `model/library.ts` (bring in; replace editor-made codes before a save), `persist/Library.tsx` (the
>     drawer, bar button, newer-revision notice). The accepted Composer, Builder and Graph are untouched.
>   - Verified: backend 688; frontend 513 unit; persisted journeys 14/14 (library ON in that config); prototype
>     13/13; standard 33/33.
> - **Development database: STILL AT `0027`, NOT migrated to `0028`.** The library is therefore OFF in development
>   (`GET /survey-components` → 404) and the dev server stays ready because 0027 is accepted while the library
>   setting is off. **Do not run `make migrate` without the owner's approval.** To enable later: back up, apply
>   `0028` only, add `SURVEY_LIBRARY_ENABLED=true` to the gitignored `.env`.
> - **Test-support change:** `tests/support.py` reset now drops sequences.
> - **Left alone, flagged:** `GET /survey-library/{kind}` (SS-03A) still lists every frozen version by code.
> - **Not authorised:** committing LIB-1, pushing, migrating the development database, SS-03B (proposed in `31_…`
>   §11), any non-answer or consent behaviour, live eligibility, Script Studio changes.

> **Update 2026-11-22 (FI-2) — read this block first; it supersedes the blocks below where they differ.**
> - **FI-1: TECHNICALLY ACCEPTED — PERSISTED AUTHORING** (D-204), after the Back/Forward correction
>   (`persist/historyGuard.ts`; `29_…` §12). The batch save, draft-documents read, `SET_DETAILS` and `authoring`
>   metadata are accepted contract (D-205; `04_…` §10). FI-1 as reviewed was committed and pushed by the owner at
>   04:46 (backend `d808d92`, frontend `7141926`, specs `fa01cda`). Local commits by Claude Code, **not pushed**:
>   frontend `63966a9` (correction), specs `f610365` (acceptance record).
> - **Owner decisions FI2-D-1…4 (D-207…D-210)** and **"AUTHORIZE FI-2"** (D-211).
> - **FI-2 — BUILT AND TECHNICALLY VERIFIED, awaiting the owner's review. NOT accepted. UNCOMMITTED in all three
>   repositories (commit authorisation covered FI-1 only).** Report
>   `docs/plans/survey-studio/30_FI-2_IMPLEMENTATION_REPORT.md`; contract `04_…` §11; evidence
>   `docs/acceptance/evidence/FI-2/`.
>   - Backend: server-governed warnings (one code, `SYNTHETIC_WORDING_UNAPPROVED` — Claude Code's choice, needs
>     acceptance) with required acknowledgements at submission; `GET …/history`; `GET …/candidates/{id}/documents`
>     with `restrictions`. No migration. OpenAPI `5b81d44f…` (218 operations).
>     **Submitting without acknowledging now fails** (`ACKNOWLEDGEMENT_REQUIRED`).
>   - Frontend: `persist/ReviewPages.tsx` (review step, candidate, version), `persist/reviewApi.ts`; routes
>     `…/review`, `…/candidates/:id`, `…/versions/:id`.
>   - Verified: backend 674; frontend 505 unit; persisted journeys 9/9; prototype 13/13; standard 33/33.
> - **Development database:** still `0027`. It now holds TWO synthetic surveys with a published version each:
>   `DEV-CHECK-AD5AEA8F` (do not write to it) and `S-DEV-FI2-WALKTHROUGH` (created by the FI-2 walkthrough with the
>   three development identities). Never re-seed or reset.
> - **Editor settings (not changed):** VS Code and Cursor have `git.enableSmartCommit: true`,
>   `git.confirmSync: false`; recommendation in `29_…` §12.4. Always re-check HEADs before reporting git state.
> - **Not authorised:** committing FI-2, pushing, SS-03B, library reuse (LIB-1 proposed in `30_…` §7, decisions
>   LIB-D-1…5), any non-answer or consent behaviour, live eligibility, Script Studio changes.

> **Update 2026-11-22 (FI-1) — read this block first; it supersedes the blocks below where they differ.**
> - **Owner accepted SS-03A development enablement as technically verified** and approved FI-D-1…FI-D-5 with
>   constraints (D-195…D-203), then gave **"AUTHORIZE FI-1"**.
> - **FI-1 — BUILT AND TECHNICALLY VERIFIED, awaiting the owner's review. NOT accepted. UNCOMMITTED in all three
>   repositories — "No commits without separate authorization".** Report:
>   `docs/plans/survey-studio/29_FI-1_IMPLEMENTATION_REPORT.md`; contract `04_…` §10; evidence
>   `docs/acceptance/evidence/FI-1/`.
>   - Frontend: persisted mode behind **`VITE_SURVEY_STUDIO_PERSISTED=1`** (off by default; separate from the
>     prototype setting, which is unchanged). Route guarded by `survey.read`. New `model/documents.ts` (the one
>     Workspace ↔ documents mapping) and `persist/` (Save, conflict, list, server validation). Small persisted-mode
>     branches in `StudioRoot.tsx`, `JourneyNav.tsx`, `ValidationPage.tsx`, `store.tsx`.
>   - Backend: two additive operations (`GET …/draft/documents`, `POST …/draft/save` atomic), draft operation
>     `SET_DETAILS`, optional `authoring` on ITEM/MODULE/CONDITION. No migration. OpenAPI `5a31269b…` (216
>     operations). New scripts `export_survey_fixture_documents.py`, `e2e_survey_setup.py` (test schema only).
>   - Specs: new generated folder `docs/plans/survey-studio/canonical-documents/` (27 files; regenerate with the
>     backend script, never edit).
>   - Verified: backend 668; frontend 505 unit; **persisted journeys 5/5**
>     (`npx playwright test -c playwright.persisted.config.ts`), prototype 13/13, standard 33/33. The three
>     Playwright configurations share ports: never run two at once.
> - **Dev servers:** backend on 8000 (survey setting on). Frontend on 5173 **now in persisted mode**; for the
>   in-memory prototype start it with `VITE_SURVEY_STUDIO_PROTOTYPE=1` alone.
> - **Development database:** unchanged by FI-1 (still `0027`; survey tables identical; only a read-only
>   walkthrough as `dev.survey.author`). Do not write to the synthetic published survey `DEV-CHECK-AD5AEA8F`.
> - **Git:** no hook or automation found (`evidence/FI-1/git_automation.txt`); editors have smart commit on and
>   sync confirmation off. Backend `4ae7875` and specs `cab99e5` are local commits not pushed by Claude Code —
>   re-check HEADs before reporting.
> - **Not authorised:** FI-2 (proposed in `29_…` §10, decisions FI2-D-1…4), SS-03B, any non-answer behaviour,
>   live eligibility, Script Studio changes, development-database migration or re-seed, commits, pushes.

> **Update 2026-11-22 (later) — SS-03A accepted and enabled in development. Read this block first; it supersedes
> the SS-03A block below where they differ.**
> - **Owner: "SS-03A is accepted as TECHNICALLY VERIFIED"** (D-188…D-194). Record:
>   `docs/plans/survey-studio/28_SS-03A_ACCEPTANCE_AND_DEVELOPMENT_ENABLEMENT.md`; evidence
>   `docs/acceptance/evidence/SS-03A/` (`fixture_reconciliation.txt`, `dev_enablement/01…06`).
> - **Commits:** the SS-03A work was committed and pushed by the owner at 00:33 (backend `a607ff5`, frontend
>   `abb7726`, specs `3ff4df7`). Local commits by Claude Code after that hold only this checkpoint's additions and
>   are **not pushed** — check `git log origin/main..HEAD` in backend and specs.
> - **The development database IS NOW at `0027_survey_definitions`** (migrated 2026-11-22 after ten preconditions).
>   Backup taken before: `<workspace>/_db_backups/call360_dev_before_0027_20261122.dump` with `RESTORE.md` (outside
>   the repositories; never commit it). Downgrade refuses because a survey definition exists. Still never run
>   `make seed`, and never re-seed, truncate, rename or drop.
> - **`SURVEY_DEFINITIONS_ENABLED=true` in the gitignored development `.env` only.** Code default and test
>   configuration stay off. The dev server on port 8000 serves the 15 survey operations.
> - **Three development-only identities** (`dev.survey.author`, `.checker`, `.publisher`; roles
>   `DEV_SURVEY_AUTHOR/CHECKER/PUBLISHER`; read+edit, read+approve, read+publish; SG). Created by
>   `Call360-backend/scripts/dev_survey_identities.py --confirm-development`; passwords only in the gitignored
>   `.secrets/dev_survey_accounts.json` — **never print them**. ADMIN, USER and SC_CHECKER hold no survey permission.
>   These people hold nothing else and cannot open the rest of the portal (the prototype route needs `script.read`).
> - **Left in the development database by the checks:** synthetic survey `DEV-CHECK-AD5AEA8F` (version 1.0
>   published; candidate 2 withdrawn). It cannot be deleted, by design.
> - **Technical debt:** TD-SS03A-1 pre-existing `SAWarning` at `tests/conftest.py:87` in seven existing tests.
> - **FI-1 (frontend on the persisted API: save, reload, optimistic concurrency, server validation authoritative) is
>   PROPOSED, NOT AUTHORISED** — boundary and decisions FI-D-1…FI-D-5 in `28_…` §5. SS-03B not started.
> - **Not authorised:** FI-1, FI-2, SS-03B, any non-answer behaviour or live-call eligibility, Script Studio
>   changes, pushing.

> **Update 2026-11-22 — SS-03A. Read this block first; it supersedes the older blocks below where they differ.**
> - **Owner message 2026-11-21 "Approve Decision Closure and Authorize SS-03A"** (register D-176…D-187): TS-1…TS-23
>   approved with the six amendments; mechanisms PB-1…PB-12 approved with six clarifications (wording approval is
>   separate append-only evidence; non-answer resolution reserved, no implementation; non-answer outcome class may
>   exist in the schema, no codes; spoken variables default-deny; Publisher independent of Checker, most restrictive
>   identity checks, no role granted; all synthetic content unapproved). No-answer and Compliance decisions stay open.
> - **Local commits made on that authorisation, NOT pushed:** frontend `a867767`, specs `b2f81df` (each one ahead
>   of `origin/main`). The earlier UC-01/UC-02 commits (`c575f76`, `33fdfce`) are on the remote; provenance in
>   `27_…` §10. Nothing rewritten.
> - **SS-03A — Survey definition foundation: BUILT AND TECHNICALLY VERIFIED, awaiting the owner's review. NOT
>   accepted. Backend work UNCOMMITTED (no commit authorisation for it).** Report:
>   `docs/plans/survey-studio/27_SS-03A_IMPLEMENTATION_REPORT.md`; server contract: `04_…` §9; evidence:
>   `docs/acceptance/evidence/SS-03A/`.
>   - Backend (base `7228875`): new `app/domain/survey/` (canonical, documents, conditions, validator, store), new
>     `app/api/survey_definitions.py` (15 operations), new migration **`0027_survey_definitions`** (nine additive
>     tables, no foreign key to or from any existing table), five new test files (146 tests). Small changes in
>     `main.py`, `settings.py`, `health.py`, `admin_access.py`, `cli.py`, `catalog.py`, `export_openapi.py`, one
>     assertion in `tests/test_admin_access.py`; OpenAPI regenerated (`725fee2c…`, +15 operations, +22 schemas, 0
>     changed).
>   - Frontend (base `a867767`): generated client only (3 files). No screen calls the new API.
>   - **Server setting `survey_definitions_enabled` is OFF by default**; with it off the routes do not exist.
>     Permissions `survey.read/edit/approve/publish` are granted to **no role**.
>   - **The development database was NOT migrated and is still at `0026`.** The server accepts `0026` only while
>     the setting is off. **Never run `make migrate` or `make seed`** without the owner's authorisation.
>   - Verified: backend 657 passed (isolated test database), lint, format, strict types, contract check; frontend
>     403 unit, 13/13 prototype journeys, 33/33 standard Playwright; 27 fixtures regenerate byte-identically; specs
>     validator PASS.
> - **Not authorised:** SS-03B, execution, server call-plan assembly, any non-answer/refusal/repeat/consent/timeout
>   policy, voice or telephony, Script Studio changes, development-database migration or re-seed, granting
>   permissions, pushing, committing the SS-03A backend work, connecting Survey Studio screens to the API.
> - **Next, owner's choice:** review SS-03A; then (separately) commit authorisation, and the proposals in `27_…` §8
>   (SS-03B boundary; frontend integration FI-1/FI-2; who holds the four permissions in development).

> **Update 2026-11-21 — read before the rest of §0.**
> - **S1-E.2B ACCEPTED 2026-11-20** as offline-verified (D-109…D-112 confirmed) and committed by the owner (specs
>   `941d2c2`, backend `7228875`, frontend `f98d73e`). Still open: live Azure validation (owner-run, needs a new
>   single-use authorisation), paid switch **on** in development, purge decision for the LAB-S-00023 microphone
>   transcript, Cost Management comparison, and **rotation of the Azure key that was printed in a session transcript**.
> - **S2-A.2 Script Studio layout ACCEPTED 2026-11-20** (frontend only; record in `acceptance/S2.md`,
>   `evidence/S2-A.2/`). **Uncommitted** in frontend (9 files) and specs.
> - **SS-00 Survey Studio assessment and design ACCEPTED 2026-11-21** as an assessment and planning checkpoint
>   (`docs/plans/survey-studio/01…03`). The owner asked for a substantial Governance redesign per
>   `docs/product/survey-studio/PRD_v1.1.md` (191 requirements, 161 P0) and `UX_EXCELLENCE_v1.1.md`.
> - **Owner rulings 2026-11-21:** SS-D-01 extend in place — approved in principle (no forcing into incompatible tables;
>   additive only; no history rewrite). SS-D-02 — Survey Studio owns structure, identities, answers, composition,
>   conditions and routing; wording and delivery stay under the existing approved script governance; one question
>   master, one approval chain. **SS-D-09 restriction REJECTED** — a Question Definition may be placed many times,
>   also within one survey; each placement is a Question Instance with its own identity and evidence. SS-D-17 runtime
>   last — approved (graph engine stays in simulation). SS-D-20 — the product is **Survey Studio**; Script Studio
>   coexists temporarily; "Wording & Delivery" is a capability within it.
> - **SS-01 Architecture and contract finalisation ACCEPTED 2026-11-21** (`docs/plans/survey-studio/04…07`,
>   `fixtures/`). Owner rulings recorded as **D-113…D-121** in `06_SS-01_DECISION_REGISTER.md`: naming (D-113),
>   Wording Version binding (D-114), findings per executed placement with stable idempotent ids (D-115), libraries
>   (D-116), sequencing (D-117), UNKNOWN policy on every binding (D-118), follow-up queues with an explicit
>   interrupt stop/resume policy (D-119), no wording-owner role in P0 (D-120), material warnings need recorded
>   acknowledgement and blockers cannot be waived (D-121). SS-D-03, 04, 05, 08, 11–16, 19 remain proposals.
> - **Naming amendment APPLIED 2026-11-21 (D-113):** new `docs/adr/ADR-0010-survey-studio-naming.md`; pointer in
>   ADR-0007; EXC-001 amended; "Survey Studio" removed from the validator's prohibited terms with a check that the
>   amendment exists; `SCREEN_NAMING_AND_ROUTES.md` and S0 test matrix E2E-18 updated. **Specs validator: PASS, 63
>   checks.** Uncommitted.
> - **SS-02A high-fidelity clickable prototype IMPLEMENTED AND VERIFIED 2026-11-21, awaiting the owner's review of
>   the actual experience — not accepted.** Frontend only, in `Call360-frontend/src/features/surveystudio/`, behind
>   the build setting `VITE_SURVEY_STUDIO_PROTOTYPE=1` (**off by default**; with it off there is no route, navigation
>   entry or label). Five screens as one journey: Home and Library, Lego Composer, Entry Condition Drawer, Guided
>   Module Builder, Choice and Follow-up Designer. Sample data in memory only (browser storage is forbidden by lint
>   rule IAM-008, so a reload resets it); a demonstration evaluator in the browser, labelled as such. New dependency:
>   `@dnd-kit` (core 6.3.1, sortable 10.0.0, utilities 3.2.2; 0 advisories). `@xyflow/react` authorised but **not
>   installed** (graph is SS-02C). Evidence `docs/acceptance/evidence/SS-02A/`: journeys A–H pass in Chromium with
>   28 screenshots and an axe scan clean on 7 states; 140 unit tests; standard Playwright 33/33 with the setting off;
>   lint, types, contract (`221985e7…` unchanged), audit and secret scan clean. Report, UX self-assessment and gap
>   list: `08_SS-02A_PROTOTYPE_REPORT.md`.
> - **To open the prototype:** stop the running frontend dev server, then
>   `VITE_SURVEY_STUDIO_PROTOTYPE=1 npm run dev` in `Call360-frontend`; Governance › Survey Studio. The evidence run
>   is `npx playwright test -c playwright.prototype.config.ts` (it uses the standard test port, so never at the same
>   time as the standard suite).
> - **Frontend working tree:** the nine S2-A.2 files are still uncommitted and were **not touched**. SS-02A adds
>   new files plus edits to `App.tsx`, `app/nav.ts`, `app/AppShell.tsx`, `tsconfig.json`, `package.json`,
>   `package-lock.json`. Nothing staged or committed. `docs/design/DEVIATIONS.md` has no Survey Studio entry yet
>   because it is one of the nine files.
> - **Owner feedback 2026-11-21 ("SS-02A Refinement and SS-02B Preparation"):** SS-02A is technically verified but
>   **not UX-accepted**; technical results are not UX sign-off. Seven refinements required (explicit interrupt
>   behaviours: stop-and-escalate / handle-then-resume / stop-and-rejoin, the last two only when governed policy
>   permits; Create Blank Module; inline option duplicate and reorder; incomplete branches obvious collapsed and
>   expanded; layouts at 1440, 1280 and narrower; keyboard-only testing; keep "Prototype — not saved", no simulated
>   persistence). SS-02B to be prepared around: internal condition builder, graph editor, profile-based simulator,
>   Guided ↔ Graph parity, first-matching-rule routing, parameterised reusable conditions; no separate graph model.
> - **SS-02A.1 prototype refinements — ACCEPTED by the owner 2026-11-21 as technically verified (not UX
>   acceptance)** (authorised by "AUTHORIZE IMPLEMENT SS-02A.1"; decisions **D-122** interruption governance on the
>   option definition — prohibited / optional / mandatory, with behaviours stop-and-escalate, handle-and-resume,
>   stop-and-go; **D-123** a duplicated option never inherits routing; **D-124** 1024 px minimum width). Built: governed
>   interruption controls; Create Blank Module (composer picker, shelf, Home); option Duplicate + drag / Alt+arrows /
>   menu reorder behind an always-present **More** menu; unresolved-branch signals in folded and collapsed states plus
>   **Next issue** (F8); library overlay below 1200 px; keyboard-only journey; wording that could imply saving removed.
>   Evidence `docs/acceptance/evidence/SS-02A.1/`; report `docs/plans/survey-studio/10_SS-02A.1_REFINEMENTS_REPORT.md`
>   (includes the keyboard map, findings K1–K7 and remaining gaps). 150 frontend unit tests; three prototype journeys
>   pass (`npx playwright test -c playwright.prototype.config.ts`); checks at 1440 / 1280 / 1024 with accessibility
>   scans; contract unchanged; no new dependency. **SS-02A is still not UX-accepted.**
> - **SS-02A.2 (Survey Studio) Guided Question Builder UX refinement IMPLEMENTED AND TECHNICALLY VERIFIED
>   2026-11-21 — awaiting the owner's UX review.** (Not the earlier S2-A.2 Script Studio layout.) Presentation only:
>   no model, operation, evaluator, backend, API or dependency change. Built: simpler default question card (text,
>   type, answers, destinations in one column, one "+", concise "n to fix"); advanced settings behind **Details** (ⓘ),
>   the answer's **More** menu, **Rule** and "Try a combination"; interruption rules open one at a time with badges
>   on the row and "Must escalate" always visible; entry-condition drawer is now a proper modal (backdrop, inert
>   background, focus containment, Escape, focus restoration, `aria-modal`, named and described); the bar says "n to
>   fix" or "Routing complete" and opens **Readiness** with routing structure, wording approval and ready-to-publish
>   as three separate lines (no generic green "ready"). Report `docs/plans/survey-studio/11_SS-02A.2_UX_REFINEMENT_REPORT.md`;
>   evidence `docs/acceptance/evidence/SS-02A.2/` (screens U1–U8 plus regenerated A–H, R, K, W sets). 150 unit tests;
>   three prototype journeys pass; three widths and accessibility scans clean. **Survey Studio is NOT yet
>   UX-accepted.**
> - **Owner 2026-11-21 ("Accept SS-02A.2 and Authorize SS-02B.1"):** SS-02A.2 ACCEPTED as technically verified and as
>   the visual / interaction baseline. Formal UX sign-off still pending (moderated testing, accessibility review, PRD
>   UX gates). No further cosmetic redesign of the question cards unless a specific usability problem is identified.
> - **SS-02B.1 Conditions and Routing Intelligence IMPLEMENTED AND TECHNICALLY VERIFIED 2026-11-21, awaiting the
>   owner's review; uncommitted.** Frontend prototype only, no new dependency. Decision points inside a module
>   (`DECISION` nodes, edges MATCH / NO_MATCH / UNKNOWN, safe insertion: only "otherwise" inherits); one shared
>   condition drawer (`EntryRuleDrawer.tsx` → `RuleDrawer`) for module entry and decisions, with the definition kept
>   apart from the placement binding; named settings (parameters), versions, consumer impact list, "new version for
>   this placement" / "separate condition"; earlier answers as inputs with `availableAnswers` (always / some routes);
>   routing mode `ORDERED_RULES` (first matching rule, required fallback, one winner, shadowed-rule warning,
>   mandatory-escalation check); editable multi-select min/max with inline validation. Sample module
>   `M-AFFORDABILITY` and condition `C-LARGE-COMMITMENT`. Report `docs/plans/survey-studio/12_SS-02B.1_CONDITIONS_AND_ROUTING_REPORT.md`
>   (contract notes and proposals P-1…P-5 need owner decisions before SS-03); evidence `docs/acceptance/evidence/SS-02B.1/`
>   (screens CR1–CR11, W-conditions-*). 166 unit tests (47 prototype; fixture F6 all six runs reproduced); 4 prototype
>   journeys (`e2e/prototype/conditions.proto.ts` is new); standard Playwright 33/33 with the setting off; lint, types,
>   contract (`221985e7…`), audit clean; validator 63 checks PASS. Fixed in passing: the modal drawer made its own
>   contents inert when it was a direct child of the studio root.
> - **Owner 2026-11-21 ("Accept SS-02B.1 and Authorize SS-02B.2"):** SS-02B.1 ACCEPTED as technically verified, subject
>   to two corrections; P-1…P-5 approved → decisions **D-125…D-129**; corrections → **D-130** (selection limits never
>   changed silently) and **D-131** (stable, typed condition references). Recorded in `06` and in `04` §3.4, §5.4.
> - **SS-02B.2 Advanced Graph Builder and Guided/Graph parity IMPLEMENTED AND TECHNICALLY VERIFIED 2026-11-21, awaiting
>   the owner's review; uncommitted.** Frontend prototype only. New pinned dependencies `@xyflow/react` 12.12.1 and
>   `@dagrejs/dagre` 3.1.3 (MIT, audit clean; graph code is lazy-loaded). New files `model/graph.ts` (derived graph,
>   layout, `connectRoute`/`connectProblem`, survey graph), `model/canonical.ts` (fingerprint), `model/large.ts`
>   (40-question sample), `GraphView.tsx`, `model/graph.test.ts`, `e2e/prototype/graph.proto.ts`. Module graph
>   (`?view=graph&node=…` on the builder) and survey graph (`?view=graph&inst=…` on the Composer) both edit through the
>   existing operations; side panel = the step's own Guided card; outline/search in both views; one undo history.
>   Also in this checkpoint: `InputDecl` typed inputs, `INCLUDES_ANY/ALL/NONE`, governed `REVIEW_REQUIRED` outcome,
>   `ESCALATION_OUTCOMES`, no automatic change to `selection`. Report `docs/plans/survey-studio/13_SS-02B.2_GRAPH_BUILDER_REPORT.md`;
>   evidence `docs/acceptance/evidence/SS-02B.2/` (screens GR*, GC*, W-*; `graph_parity_fingerprints.txt`). 183 unit
>   tests (64 prototype, 14 graph/parity); 6 prototype journeys; standard Playwright 33/33 with the setting off; lint,
>   types, contract (`221985e7…`), audit clean; validator 63 checks PASS.
> - **Owner committed on 2026-11-21 14:52** everything up to SS-02B.2 (frontend `b064253`, specs `0f0279b`; backend
>   unchanged `7228875`), including the nine S2-A.2 Script Studio files. They are no longer uncommitted.
> - **Owner review of SS-02B.2:** connections could not be intuitively deleted and redrawn → authorised
>   **SS-02B.2.1 Connection Editing Refinement ONLY**. **IMPLEMENTED AND TECHNICALLY VERIFIED 2026-11-21, awaiting the
>   owner's review; uncommitted** (frontend: `GraphView.tsx`, `BuilderPage.tsx`, `model/graph.ts`, `model/ops.ts`,
>   `model/graph.test.ts`, `styles/survey-studio.css`, `e2e/prototype/graph.proto.ts`, new
>   `e2e/prototype/connections.proto.ts`). One selectable edge per route (merging withdrawn); contextual route toolbar
>   (Change destination / Disconnect route); Delete / Backspace; endpoint drag (`reconnectable: 'target'`);
>   `disconnectRoute` / `disconnectProblem` / `disconnectSurveyRoute`; `setDecisionUnknown({ clear: true })`; broken-route
>   indicator; structure lines (queue order, start, folded branch, interruption, governed halt) explained with the
>   semantic edit. Report `docs/plans/survey-studio/14_SS-02B.2.1_CONNECTION_EDITING_REPORT.md`; evidence in
>   `docs/acceptance/evidence/SS-02B.2/` (`screens/CE*`, `connection_parity_fingerprints.txt`). 187 unit tests; 7
>   prototype journeys; standard Playwright 33/33 with the setting off; lint, types, audit, contract clean; validator PASS.
> - **Owner 2026-11-21 ("Accept SS-02B.2 and Authorize SS-02B.3"):** SS-02B.2 ACCEPTED as technically verified (the
>   message does not mention SS-02B.2.1 separately: built and verified, not explicitly accepted). Open points resolved →
>   **D-132** (a condition may read a same-module answer asked on every or on some prior routes; uncollected = UNKNOWN;
>   evidence states ANSWERED / ANSWERED_EMPTY / UNANSWERED / SKIPPED; impossible reference invalid; replaces SS-RUL-011),
>   **D-133** (controlled outcome catalog with classes; ESCALATE the only escalation outcome; business catalog deferred),
>   **D-134** (REVIEW_REQUIRED halts, pending review, not completed; resume/close need a separate authorised capability).
>   Recorded in `04` §5.4 (d), (d-1), (g), (h) and `06`.
> - **SS-02B.3 Journey Simulator IMPLEMENTED AND TECHNICALLY VERIFIED 2026-11-21, awaiting the owner's review;
>   uncommitted.** Frontend prototype only, no new dependency. New: `model/sim.ts` (pure engine over the canonical model;
>   `simulate`, `simulateInputs`, `validateAnswer` with SS-01 codes, `firstDivergence`), `model/demo.ts` (8 synthetic
>   profiles, `addDemoSurvey`, `playback`), `model/sim.test.ts`, `SimulatorPage.tsx` (route
>   `/survey-studio/surveys/:id/simulate?profile=&compare=`), `e2e/prototype/simulator.proto.ts`; `OUTCOME_CATALOG` in
>   `model/sample.ts`. **All 8 SS-01 fixtures — 25 runs, 7 rejected answers — reproduced through the simulator engine**
>   (`fixture_verification.txt`; fixtures unchanged). Report `docs/plans/survey-studio/15_SS-02B.3_JOURNEY_SIMULATOR_REPORT.md`;
>   evidence `docs/acceptance/evidence/SS-02B.3/` (screens SJ1–SJ10, W-simulator-*). 225 unit tests (106 prototype);
>   8 prototype journeys; standard Playwright 33/33 with the setting off; lint, types, audit, contract clean; validator
>   PASS. Fixed in passing: view parameters (`?view`, `?profile`, `?compare`) are now read from the address, because two
>   quick changes could lose the first.
> - **Owner 2026-11-21 ("Accept SS-02B.3 Technical Verification and Authorize SS-02B.3.1"):** SS-02B.2.1 and SS-02B.3
>   ACCEPTED as technically verified; simulator UI direction = prototype baseline (formal UX acceptance and production
>   readiness pending). Rulings → **D-135** (a jump names the next CANDIDATE and never bypasses eligibility; routing /
>   activation trigger / eligibility are distinct; skip disposition required for a jump target with a condition; no
>   re-entry), **D-136** (six terminal states never merged: COMPLETED, ENDED_WITH_OUTCOME, MANDATORY_ESCALATION,
>   REVIEW_REQUIRED, MISSING_INFORMATION_HALT, DRAFT_INVALID; explicit versioned fixture migration), **D-137** (no-answer
>   behaviour recorded as an open requirement, not built). In `04` §2.2a, §2.2b, §5.5 and `06`.
> - **SS-02B.3.1 Business-rule correctness IMPLEMENTED AND TECHNICALLY VERIFIED 2026-11-21, awaiting the owner's
>   approval; uncommitted.** Frontend prototype + specs only, no new dependency. Model: `Instance.ifIneligible`,
>   `setIfIneligible`, `jumpSources`, `canBeIneligible`; `validateSurvey` adds the `@SKIP` checks; `model/sim.ts` rewritten
>   survey loop (arrival SEQUENCE/JUMP, `DISPOSITION` event, `terminal` with `TerminalState`, module status
>   `HALTED_MISSING_INFORMATION`); survey graph route `@SKIP`; Composer row "Jumped to, but does not apply"; drawer
>   Eligibility / Activation note; demo survey has an 8th module (specialist call, eligible age ≥ 60, reached by a jump)
>   and three new synthetic customers. **Fixtures:** F1–F8 (schema /1) unchanged and byte-identical; new G1–G6 (schema
>   /2, 18 runs, 2 rejected) generated and self-checked by `fixtures/reference_interpreter_v2.py` and reproduced by the
>   simulator; the /2→/1 mapping lives in one function in `model/sim.test.ts`. Report
>   `docs/plans/survey-studio/16_SS-02B.3.1_BUSINESS_RULE_CORRECTNESS_REPORT.md`; evidence
>   `docs/acceptance/evidence/SS-02B.3.1/`. 250 unit tests (131 prototype); 9 prototype journeys (new
>   `e2e/prototype/rules.proto.ts`); standard Playwright 33/33 with the setting off; lint, types, audit, contract clean;
>   validator PASS.
> - **Open for the owner (report 16 §7):** A-1 a jump to an "after an outcome" module activates it — confirm; A-2 a
>   module cannot have both an activation trigger and an eligibility condition (schema, SS-03); A-3 skip disposition only
>   after a jump; A-4 an escalation outcome can still be routed "continue" at survey level; A-5 the no-answer decisions.
> - **Owner 2026-11-21 ("Accept SS-02B.3.1 and Authorize SS-02C"):** SS-02B.3.1 ACCEPTED as technically verified.
>   Rulings **D-138** (a jump is a valid activation, never bypasses eligibility), **D-139** (activation and eligibility are
>   independent instance members; `entry.mode ON_OUTCOME` still read), **D-140** (skip disposition in sequence, default
>   continue; jump target still explicit), **D-141** (a mandatory escalation cannot be overridden by survey routing;
>   `MANDATORY_ESCALATION_OVERRIDDEN`), **D-142** (decision-ready no-answer contract, nothing built). `04` §2.2c, `06`.
> - **SS-02C FINAL PROTOTYPE CHECKPOINT — IMPLEMENTED AND TECHNICALLY VERIFIED 2026-11-21, presented for the owner's
>   end-to-end acceptance review; uncommitted.** Frontend prototype + specs only, no new dependency.
>   Model: `Instance.activation`, `Instance.ifSkippedInSequence`; ops `activationOf`, `eligibilityOf`, `setActivation`,
>   `setEligibility`, `setIfSkippedInSequence`; `flow.mandatoryOutcomes`; `model/governance.ts` (candidate `snapshot` +
>   fingerprint, `lockOf`, `assess` readiness, `standing`, `submit` / `decide` / `publish` / `withdraw`, `seedPublication`,
>   three invented people incl. one with both roles); `model/diff.ts` (`compare` two snapshots); store slice `gov` /
>   `govern` (outside undo). Screens: `JourneyNav.tsx` (six-step strip, role switch), `ValidationPage.tsx`
>   (`…/validate`), `ReviewPage.tsx` (`…/review`, tabs review / compare / history). Demo: `demoBaseline` seeds a labelled
>   simulated v1.0; the specialist-call module now also asks the shared "content to proceed" question.
>   **Fixtures:** new H1–H4 (schema /3, 16 runs) from `fixtures/reference_interpreter_v3.py`; F and G unchanged.
>   Report `docs/plans/survey-studio/18_SS-02C_FINAL_PROTOTYPE_REPORT.md` (includes the acceptance checklist);
>   no-answer contract `17_SS-02C_NO_ANSWER_CONTRACT.md`; evidence `docs/acceptance/evidence/SS-02C/`.
>   305 unit tests (186 prototype); 10 prototype journeys (new `e2e/prototype/governance.proto.ts`); standard Playwright
>   33/33 with the setting off; lint, types, audit, contract clean; validator PASS.
> - **Open for the owner (report 18):** two skip-disposition members instead of one; who may publish; whether an ordinary
>   route to Escalate may continue; editing during review; D-NA-1…17; P-6…P-12. **No moderated usability test or
>   screen-reader session has been run; formal UX sign-off pending.**
> - **Owner 2026-11-21 ("SS-02C Final Closure Corrections"):** SS-02C functional delivery and visual direction ACCEPTED
>   as the baseline; six narrow corrections required before closure → **D-143** immutable submitted candidates (approval
>   binds to candidate ID + revision + pinned manifest; undo never transfers or resurrects an approval), **D-144**
>   separate Publisher permission with identity check, **D-145** Escalate terminal in every routing mode, **D-146** two
>   skip dispositions retained, **D-147** collision-aware Graph menus, **D-148** no-answer decisions marked UNRESOLVED
>   with what each blocks. These supersede P-6 (in part), P-9 and "ordinary Escalate may be routed" of report 18.
> - **SS-02 FINAL CLOSURE CORRECTIONS — IMPLEMENTED AND TECHNICALLY VERIFIED 2026-11-21, presented for the owner's
>   closure decision; uncommitted.** `model/governance.ts`: `Submission` is a frozen candidate (`id` C-n, `n`, `manifest`,
>   `manifestHash`, `wording`), statuses incl. `SUPERSEDED`; `Capability` AUTHOR/CHECKER/PUBLISHER, four invented people;
>   `standing` reads the candidate record (stages DRAFT / IN_REVIEW / REJECTED / APPROVED / PUBLISHED, `draftDiffers`);
>   `decideProblem(g, survey)`, `decide(g, survey, …)`, `publishProblem(g, survey)`, `publish(g, survey, at)` no longer
>   take the workspace. `flow.escalationOutcomes`; validation part `'escalation'`; `ops.addInstance` / `syncOutcomes`
>   set an escalation outcome's route to end the call; `sim` ends the call on any ESCALATION-class outcome.
>   `ui.tsx` Popover: window-anchored, collision-aware placement in graph editors (incl. the transformed route toolbar).
>   Builder/Composer: delayed panel focus no longer steals focus from inside the panel. **Fixture:** J1 (schema /4) from
>   `fixtures/reference_interpreter_v4.py`; F, G, H unchanged. **Closure document:**
>   `docs/plans/survey-studio/19_SS-02_FINAL_PROTOTYPE_CLOSURE.md`; evidence `docs/acceptance/evidence/SS-02-closure/`.
>   314 unit tests (195 prototype); 11 prototype journeys; standard Playwright 33/33 with the setting off; lint, types,
>   audit, contract clean; validator PASS.
> - **Owner 2026-11-21 ("SS-02 Prototype Technical Closure Accepted") — SS-02: TECHNICALLY ACCEPTED — PROTOTYPE
>   (D-149).** All six closure corrections accepted; **the original Survey Studio prototype story is CLOSED for feature
>   development — do not reopen SS-02 for optional enhancements.** This is **not** formal business-user UX acceptance,
>   **not** screen-reader accessibility sign-off, **not** production readiness, **not** approval of the unresolved
>   no-answer policies and **not** authorisation for backend implementation. **Preserve (D-150):** the 19 fixtures / 63
>   expected runs, the regression evidence folders, the UX acceptance matrix (report 18) and the closure documentation.
>   **Open decisions are now explicit future gates (D-151, report 19 §8.2):** G-1 business-user UX acceptance · G-2
>   screen-reader sign-off · G-3 no-answer policy · G-4 governance rules · G-5 remaining SS-01 proposals · G-6
>   architecture assessment · G-7 backend implementation (SS-03) · G-8 production readiness. None is opened; each needs
>   its own explicit owner decision.
> - **Proposed architecture direction — RECORDED ONLY (D-152, report 19 §9); not implemented, not authorised:** Survey
>   Studio becomes the single authoritative journey-authoring experience; essential Script Studio features are rebuilt
>   or incorporated into it; redundant Script Studio functionality is eventually retired after safe migration; the
>   execution harness assembles customer-specific call plans from approved survey definitions and application data;
>   live customer answers dynamically select subsequent approved dialogue. It is an input to the **next assessment**.
>   SS-D-02, SS-D-17 and SS-D-20 stay in force until then. **Do not modify or remove Script Studio.**
> - **SS-02 baseline is COMMITTED (D-153).** The owner asked for it to be committed locally; on inspection it was
>   already committed and level with the remote — specs `786a7c0` (then `b5bae20` at 21:15, `.DS_Store` files only),
>   frontend `d1cdb03` (2026-11-21 21:07), backend
>   unchanged `7228875`. Verified after the fact: 19 fixtures / 63 runs regenerate byte-for-byte, 314 unit tests,
>   types / lint / contract / secret scan clean, Script Studio and backend unaffected. Note: 12 `.DS_Store` files are
>   tracked in specs (harmless; left alone).
> - **G-6 ARCHITECTURE CONSOLIDATION ASSESSMENT — DELIVERED 2026-11-21, PROPOSED, awaiting the owner's review
>   (D-154). Analysis and specification only; nothing implemented; Script Studio untouched.** Document:
>   `docs/plans/survey-studio/20_G-6_ARCHITECTURE_CONSOLIDATION_ASSESSMENT.md`. Findings: "Script Studio" is three
>   layers — (A) the authoring product (2 routes, ~1,490 UI lines, 26 API operations, `script_authoring.py`) which is
>   fully redundant once Survey Studio is real; (B) the governed content store (12 core tables) which every pin, run,
>   finding, review and KPI refers to; (C) assignment, controller, simulation, evaluation, findings, review, which are
>   not authoring and are retained. Survey Studio lacks delivery mode, statements, lifecycle gates, mandatory flag,
>   evaluation configuration, control mapping, numeric answers. Controlled variables, clarification/repeat scripts and
>   multi-language exist in **neither** product. All consumers read the frozen content document, not authoring rows.
>   `live_eligibility` (D-67) is computed but enforced nowhere. Recommendation: retire A; evolve then rename B; keep
>   and re-point C; wording features on the existing screens (no Wording Studio); one publication process draft →
>   immutable candidate → version. **Decisions asked: AD-1…AD-15** (AD-1 meaning of "remove completely"; AD-2 whether
>   synthetic history is carried forward; AD-15 amend SS-D-01/02/20, retain SS-D-17). **Those rulings stay in force
>   until the owner rules.** Proposed checkpoints (none authorised): D-0 decisions · W-1, W-2 wording and
>   call-readiness · B-1, B-2, B-3 backend · M-1, M-2 migration · P-1 call-plan assembly · R-1 retirement · V-1
>   runtime and voice — with the no-answer and governance decisions that block each (`20_…` §6.1).
> - **Owner 2026-11-21 ("G-6 Architectural Direction Approved: Unified Survey Studio").** Governing rule: do not
>   preserve a module merely because others depend on it; preserve business functionality, replace obsolete
>   dependencies, remove redundant implementations. **D-155 (AD-1)** one canonical Survey Studio store and publication
>   model; script tables, APIs, services and routes are reused, refactored, replaced or deleted on their merits.
>   **D-156 (AD-2)** re-seed synthetic development data in principle — **five preconditions before anything
>   destructive** (inventory the real dev database; identify protected demo records; verified backup; state exactly
>   what a re-seed replaces; a separately approved destructive checkpoint). **D-157 (AD-15)** SS-D-01, SS-D-02, SS-D-20
>   amended (wording in the register); **SS-D-17 retained** (runtime last). **D-158** target product list; no Wording
>   Studio; no six-tab replica. **D-159** Assignment Rules, Simulation Workbench, Finding Rules and Review Workbench
>   assessed by business workflow, not assumed separate. Objective: one Survey Studio, one canonical survey model, one
>   approved publication process, one deterministic execution harness.
> - **UC-01 UNIFIED SURVEY STUDIO FOUNDATION — BUILT AND TECHNICALLY VERIFIED 2026-11-21, presented for the owner's
>   review; NOT accepted; uncommitted (D-160).** Frontend prototype and specs only. Built: **Statement nodes** (one
>   item master; node `type: 'STATEMENT'`, item `answerType: 'STATEMENT'`, roles OPENING / TRANSITION / DISCLOSURE /
>   CLOSING, one route); **NUMERIC** (`numberRule`) and **ACKNOWLEDGEMENT** items; **wording and delivery section** on
>   the card (`WordingSection` in `BuilderPage.tsx`, closed by default; `wording.delivery` CONTROLLED_TTS default /
>   EXACT_AUDIO warning / CONVERSATIONAL **blocked**); **controlled variables** `{{field_code}}` (`model/wording.ts`:
>   deterministic `renderWording`, missing value = error; simulator halts `MISSING_INFORMATION_HALT` /
>   `WORDING_VALUE_MISSING`); declared `mandatory` and `role` (no gate behaviour; `liveGates` reports D-67 as INFO);
>   **interface contracts** `model/contract.ts` (`EvaluationConfig`, `ControlLink`, `toContent`, `legacyGaps`);
>   **Call Plan Preview** `model/plan.ts` + `CallPlanPage.tsx` at `surveys/:surveyId/plan` (modules IN / OUT /
>   CONDITIONAL / HALTS, exact wording per customer, open points, one simulated call shown separately); second demo
>   `addReadinessDemo` (button `ss-add-readiness`). Simulator: `SAY` event, `deliveries[]`, evidence state DELIVERED.
>   Documents: `20_…` §10, **`21_UC-01_CONSOLIDATION_MAP.md`** (per-capability disposition; of 39 script tables: 8
>   replaced, 2 deleted, 11 refactored, 18 reused; nav ends as Survey Studio + Review Workbench),
>   **`22_UC-01_IMPLEMENTATION_REPORT.md`**, contract `04_…` §7, register D-155…D-160 + P-13…P-22. Evidence
>   `docs/acceptance/evidence/UC-01/`. **347 unit tests (228 prototype, 33 new); 19 fixtures / 63 runs unchanged and
>   byte-identical; 12/12 prototype journeys; 33/33 standard Playwright; lint, types, audit, contract clean.**
>   **Not done:** no golden fixture / reference interpreter for the new elements (schema /5 recommended before a
>   server engine); no usability or screen-reader evidence; AD-2 preconditions not started (no database read).
> - **Blocked, not invented (report 22 §5):** conversational delivery; variables in recordings; non-acknowledgement;
>   mandatory-unanswered; identity/consent refusal; repeat counts, timeouts, clarification and repeat wording.
> - **Decisions needed before backend (report 22 §8):** AD-2 preconditions; AD-3, AD-5, AD-12, AD-13, AD-14; UC-D-1…
>   UC-D-12 (default delivery, conversational mode, variable policy, statement roles, gate behaviour, mandatory,
>   numbers in conditions, evaluation config, assignment in Survey Studio, findings policy, repeat wording, P-13…P-22);
>   G-3 seven no-answer decisions; G-4 governance; G-1, G-2.
> - **Owner 2026-11-21 ("Accept UC-01 and Authorize UC-02").** **UC-01 ACCEPTED as TECHNICALLY VERIFIED — FRONTEND
>   PROTOTYPE (D-161)**: the new prototype baseline (formal UX acceptance, policy approval, backend and operational
>   readiness pending; do not reopen SS-02). Approved: **AD-3** hashed graph documents with server-enforced integrity
>   (D-162); **AD-5** separate Publisher permission and independent identity rules (D-163); **AD-12** single language
>   (D-164); **AD-13** scheduled publication and withdrawal in lifecycle contracts, no operational behaviour invented
>   (D-165); **AD-14** Survey terminology for new APIs, destructive renaming deferred (D-166); **UC-D-9** assignment
>   rules authored through Survey Studio but independently governed; **UC-D-10** findings policies in the Library under
>   separate Compliance permissions (D-167). "One authoring application does not imply one enormous editor or one
>   approval event for unrelated artifacts."
> - **UC-02 CONTRACT AND CALL-PLAN READINESS — BUILT AND TECHNICALLY VERIFIED 2026-11-21, presented for the owner's
>   review; NOT accepted; uncommitted (D-168).** Specs, fixtures and narrow prototype corrections only.
>   **Fixtures:** schema `/5`, `fixtures/K1…K8*.json` (19 runs, 14 plans, 12 validation errors) from the standalone
>   `fixtures/reference_interpreter_v5.py` (imports nothing from earlier interpreters or the prototype; expected values
>   hand-written); prototype checked by `model/fixtures5.test.ts` — 43/43. Historical 19 fixtures / 63 runs unchanged.
>   Total 27 files, 82 runs. **Prototype corrections:** `RECORDING_ASSET_MISSING` is an ERROR (was a warning);
>   `{acknowledged:false}` → `NON_ANSWER_POLICY_UNRESOLVED`, run stays pending; unfinished variable undeliverable
>   (`MALFORMED`); money > 2 decimals and fractional integers are `INVALID` (no rounding); `SINGLE_ROUTE_ITEM_BRANCHES`,
>   `NODE_ITEM_KIND_MISMATCH`, `STATEMENT_NOT_A_QUESTION` and other stable `Issue.code`s; statement display labels S1,
>   S2 … (`buildFlow`; node ids unchanged; plan and contract sort by reading order, never by label). **Call plan:**
>   `model/plan.ts` now has `issues[{code, at}]`, canonical open points `{on, to}`, and `liveEligibility(ws, survey, sg,
>   plan)` = ten explicit conditions (MET / NOT_MET / NOT_AVAILABLE; never eligible in the prototype);
>   `CallPlanPage.tsx` rebuilt compact (two verdict panels A and B, six counts, three foldable sections; < 1,500 px).
>   **Documents:** `23_UC-02_DECISION_READY_CONTRACTS.md` (TS-1…TS-23 approvable now; 12 decisions block persistence;
>   13 + 3 voice block runtime; six minimal interfaces; readiness checklist), `24_UC-02_IMPLEMENTATION_REPORT.md`,
>   contract `04_…` §8, register D-161…D-169 + P-23…P-29, `fixtures/README.md`. Evidence
>   `docs/acceptance/evidence/UC-02/`. **403 unit tests (284 prototype); 13/13 prototype journeys; standard
>   Playwright 33/33; lint, types, audit, contract clean; validator PASS.**
> - **Still not done:** AD-2 preconditions (no database read, no backup); no usability or screen-reader evidence; /5
>   does not cover decisions, queues, rules, interruptions or activation with statements; pre-UC-01 validation rules
>   have no stable codes; the reference and the prototype share an author (independent in code only).
> - **Decisions the owner is asked for (`23_…` Part 1):** approve TS-1…TS-23 as a set; the 12 persistence blockers
>   (UC-D-1, UC-D-2, UC-D-3a, UC-D-4, UC-D-6 = D-NA-5/10, G-4a, G-4b, G-4c, G-4e, SS-D-05, D-NA-9, D-NA-13); the
>   runtime blockers; confirm P-23…P-29. No-answer register preserved unchanged (17 decisions, 4 parameters, no values).
> - **Owner 2026-11-21 ("UC-02 Review and Backend Decision Closure").** **UC-02 ACCEPTED as technically verified,
>   subject to contract clarifications (D-170)**; UX acceptance, policy approval, live-call eligibility and backend
>   authorisation remain separate. **D-171:** TS-1, 3, 5, 6, 8, 11, 13–23 *recommended* for approval. **D-172:** TS-2,
>   4, 7, 9, 10, 12 to be amended — amended wording PROPOSED in `25_UC-02_DECISION_CLOSURE.md` §1.2 (single-route rule
>   restricts the item node only; conversational not publishable; declared numeric precision, never rounded; explicit
>   non-acknowledgement kept as evidence, never a success; v1 condition-input restriction extensible; lifecycle status
>   derived from append-only history, candidate content never updated). **No fixture changed; new behaviour reserved
>   for schema /6.** **D-173:** twelve persistence rulings PB-1…PB-12 PROPOSED (`25_…` §2), each split into mechanism
>   and policy content. **Not approved and must not be treated as approved:** actual permitted customer fields,
>   refusal handling, consent policy, the outcome catalog, non-answer rules. **D-174:** P-23…P-29 classified (all safe
>   engineering defaults, with named Business/Compliance and voice-channel parts); eligibility UI now has **eleven**
>   conditions — gates read "Present"/"Not present" and `GATE_BEHAVIOUR` is a separate, not-met condition
>   (`model/plan.ts`, `CallPlanPage.tsx`). Re-verified: 403 unit tests, 13/13 prototype journeys.
> - **BASELINE IS IN GIT (D-175).** The owner committed UC-01 and UC-02 at 2026-11-21 23:23: **frontend `c575f76`**
>   (28 files), **specs `33fdfce`** (49 files); both level with `origin/main`; backend unchanged `7228875`. All 27
>   fixtures and five reference interpreters are tracked; they regenerate byte-for-byte (82 runs, 14 plans).
>   **Uncommitted, made after those commits:** frontend 5 files (eligibility clarification: `model/plan.ts`,
>   `CallPlanPage.tsx`, `model/uc02.test.ts`, `e2e/prototype/uc02.proto.ts`, `survey-studio.css`); specs documents 25
>   and 26 (new), register, contract §8.6 and §8.9, status notes in 23 and 24, index, handoff, regenerated UC-02
>   evidence. I made no commit and no push.
> - **SS-03A FOUNDATION SPECIFICATION PREPARED — NOT AUTHORISED:** `26_SS-03A_FOUNDATION_SPECIFICATION.md`. Scope:
>   canonical versioned graph documents; immutable drafts/candidates/versions with append-only lifecycle events;
>   hashes and manifest validation; server validator with stable codes; pure three-valued condition engine; fifteen
>   new `/api/v1/survey-definitions…` operations (the bare plural path is a validator-prohibited term; flagged for an
>   ADR decision, not changed) with four new `survey.*` permissions, behind a server setting off by default.
>   Additive only: new `survey_` tables, no existing table, endpoint or permission changed. Excludes non-answer
>   behaviour, execution, plan assembly, live-call controls, telephony, destructive changes, Script Studio removal.
>   Suggested split SS-03A.1 (pure modules) / .2 (persistence) / .3 (API).
> - **Next step: none authorised. Wait for the owner.** Asked of the owner: commit, or authorise committing, the post-review changes
>   (frontend 5 files; specs documents 25, 26 and updates); final approval of TS-1…TS-23 as amended; approval of the PB mechanisms; then, separately,
>   SS-03A by name. Do not stage, commit or push without authorisation. Script Studio untouched. Development database
>   untouched. SS-03 not started.
> - **Still open (report 19 §3–§5):** all business-user testing (no moderated usability or screen-reader evidence);
>   14 no-answer decisions block the runtime build (7 before any backend work); who holds Publisher and whether the
>   approver may publish; draft locking during review; what "approved wording" is; escalation handling.
> - **Script Studio consolidation is NOT started and NOT authorised.**
> - **SS-03 and all real backend implementation are NOT started and NOT authorised.**
>   demonstration verified against the fixtures; parity with the Python controller is a separate, later checkpoint.
>   Each needs its own explicit authorisation. `@xyflow/react` is still not installed.
> - **SS-02B plan** (internal condition builder, graph editor with `@xyflow/react` 12.12.1 + `@dagrejs/dagre`,
>   simulator, Guided ↔ Graph parity, first-matching-rule routing, parameterised conditions) is in
>   `09_SS-02A_REFINEMENTS_AND_SS-02B_PLAN.md` Part 2 — **proposed, not authorised; must not start until the owner
>   approves the prototype experience.**
> - **Running now:** the frontend dev server on :5173 runs from the assistant session with the prototype setting
>   **on**, at the owner's request, for their review. To return to normal: stop it and `npm run dev`.
> - **Frontend working tree:** nine S2-A.2 files untouched and uncommitted; SS-02A and SS-02A.1 changes uncommitted
>   beside them. Nothing staged.
> - **Next:** the owner's UX review of the refined prototype (report `11` §5). K4 (drawer focus) is closed; K5
>   (question outline) and gaps N1–N7 of report `10` remain. **SS-02B and all backend work are not authorised.**

**Project.** Call360 is a proposed AIA Standards & Compliance platform for policy-sale verification and auditable
callback operations. Three independent Git repositories under `call360/`: `Call360-specs` (requirements, ADRs,
acceptance), `Call360-backend` (FastAPI, PostgreSQL), `Call360-frontend` (React/TypeScript). All data is synthetic and
Singapore-only (D-39). The investigation screen is **Call Detail**; the script editor is **Script Studio** (ADR-0007).

**Where we are**
- **Stage 0:** every checkpoint ACCEPTED; CP0.6 technical verification ACCEPTED. **Stage 0 governance acceptance is
  PENDING** (SEC-008 security review not performed — reviewer not named; three named approvers not assigned, C-20).
  Never self-certify SEC-008 or invent signatures.
- **Stage 1 (browser voice, mock provider):** S1-A, S1-B, S1-C **ACCEPTED**. **S1-D (transcript and playback)
  IMPLEMENTED AND VERIFIED, awaiting the owner's separate acceptance.** **S1-E (GPT-Live) PAUSED.**
- **Stage 2:** **S2-A, S2-A.1, S2-B, S2-C and S2-D ACCEPTED** 2026-11-17 (D-54…D-66 approved; D-62 clarified).
  **S2-D.1 ACCEPTED 2026-11-18** (synthetic lifecycle assumptions approved with conditions D-67…D-69).
  **S2-E Callback Simulation Workbench ACCEPTED 2026-11-18** (conditions: SG_LIFECYCLE_DEMO v1.1 stays an unpublished
  regression draft; generated expectations labelled as generated baselines).
- **Stage 3:** **S3-A, S3-B and S3-C ACCEPTED 2026-11-18** (S3-C: S3-B conflict resolution approved; reviewer-assigned
  severity allowed with justification and shown apart from rule-assigned severity; the four escalation reasons approved;
  D-81…D-86 presented for confirmation).
- **Voice Lab:** **S1-E.1 ACCEPTED 2026-11-18**. **S1-E.2 GPT-Live provider adapter ACCEPTED 2026-11-18 as
  IMPLEMENTED AND OFFLINE-VERIFIED; live-provider validation PENDING.** D-81…D-94 approved (D-87…D-94 subject to the
  superseding paid-access, termination and reconciliation requirements of D-98/D-99); D-95…D-102 presented for
  confirmation. Retained: 168 h retention, separate spending-authorisation and execution roles, conservative
  reservations for unconfirmed termination, paid batch experiments disabled. **Live smoke-test preflight complete
  (2026-11-18, all pass offline)** — `S1.md` "S1-E.2 live smoke-test preflight". **No GPT-Live connection has ever been
  made; paid expenditure USD 0.** The owner will personally run the first session ("S1-E.2 first live smoke test —
  exact procedure" in `S1.md`); the assistant must not initiate any paid call or claim live validation before the owner
  has run and reviewed it.
- **Azure OpenAI (owner's provider, preferred):** **S1-E.2A ACCEPTED 2026-11-18 as offline-verified** (committed by
  the owner: specs `549448b`, backend `4ae0fb6`, frontend `cf2d621`; ADR-0009 and D-103…D-108 presented verbatim,
  confirmation pending; `S1.md` S1-E.2A incl. the Azure configuration runbook). Providers:
  `AZURE_OPENAI_GPT_LIVE` (preferred), `OPENAI_GPT_LIVE`, `GPT_LIVE_MOCK` (Azure profile default), mocks; `GPT_LIVE`
  legacy alias. Azure price unknown → Azure fails closed until the owner configures a verified price.

- **First live Azure session LAB-S-00023 (owner-run, 2026-11-18):** connection, confirmed close, usage 31 s,
  reconciled USD 0.0259 (owner-entered USD 0.05/min) — **audio not validated**: the owner heard one word (the model
  waits for the caller; background voices kept the VAD "speaking"; unbounded suppression dropped every reply).
  Non-synthetic background speech reached Azure and the dev MIC transcript (purge = owner decision). Paid switch was
  left **on** in dev. The dev backend on :8000 runs from the assistant session with the owner's Azure LIVE `.env`.
- **S1-E.2B (`IMPLEMENT S1-E.2B`, 2026-11-19): IMPLEMENTED AND OFFLINE-VERIFIED, awaiting acceptance, uncommitted** —
  opening instruction (D-109), bounded suppression `VOICE_LAB_SUPPRESS_MAX_S` 1.5 s (D-110), wait-for-caller mock with
  `[mock:greet]` / `[mock:talk-over]` (D-111), quiet-room note (D-112). Backend 511, unit 117, Playwright 33; OpenAPI `221985e7…`; no
  migration; `S1.md` "S1-E.2B", `evidence/S1-E.2B/`. A further live Azure session needs separate authorisation.

**Development priorities (owner's sequence)** — each step needs its own explicit authorisation:
0. S1-E.2B acceptance, then (if authorised) one owner-run Azure session with an opening instruction in a quiet room; the first live test should use **Azure OpenAI** (configure resource, deployment, credential
   and verified price per `S1.md` "Configuring an existing Azure OpenAI resource"), then the same smoke-test procedure.
1. Owner runs the first live smoke test (procedure in `S1.md`: dedicated OpenAI project with a USD 1 project hard limit,
   key only in the owner's shell environment, dev.admin authorises once, dev.user starts one ≤ 120 s session ≤
   USD 0.10), then reviews `uv run call360 voicelab-report --session LAB-S-…` and the Voice Lab evidence.
2. Confirm D-95…D-102. Outstanding acceptance: live-provider validation (after the test), S1-D, Stage 0 governance,
   SEC-008. Do NOT start operational controller integration or expand Voice Lab.
3. Git (2026-11-18 22:40 SGT): specs `main` at `99ad480` (S1-E.2 records committed by the owner) + this preflight's
   documentation, uncommitted; backend `main` at `fd2cd5a` + preflight changes uncommitted (`app/api/voice_lab.py`,
   `app/cli.py`, `app/core/settings.py`, `app/voice/gpt_live.py`, `app/voice/gpt_live_mock.py`, `app/voice/lab.py`,
   new `tests/test_gpt_live_preflight.py`); frontend `main` at `8d256e9` + preflight changes uncommitted
   (`src/features/voice/useVoiceSession.ts`, `src/features/voicelab/shared.tsx`, new
   `src/features/voice/playable.test.ts`). No commit or push without authorisation.
3. Resume GPT-Live integration (S1-E) last — as a conversational interface to the S2-D controller, which keeps control.

**S1-E.2A Azure OpenAI support (2026-11-18, offline-verified).** `app/voice/live_providers.py` (endpoint, auth
headers, wire rate, model per provider; Entra token provider; resampling); Azure settings `VOICE_LAB_AZURE_*` (all off
by default); mock server serves `/openai/v1/live/sessions` (+ `/attach`) at 16/24 kHz; non-secret `PROVIDER_ENDPOINT`
trace event. Backend **503**, unit **116**, Playwright **33**; OpenAPI `550e7423…`; no migration; evidence
`evidence/S1-E.2A/`. Gotchas: `azure-identity` is not installed (Entra mode fails closed locally); `store` is not sent
to Azure.

**S1-E.2 live smoke-test preflight (2026-11-18).** Hardened: the provider transport logger is pinned to INFO with an
authorisation-redaction filter (the `websockets` client logs request headers at DEBUG); in `APP_ENV=test` only
loopback hosts are reachable (the official endpoint is refused); `VOICE_LAB_START_TIMEOUT_S` (10 s, 2–30) bounds
connect + `session.started`; recordings label the provider track as audio *sent*, not played; browser `playable()`
helper. New read-only `call360 voicelab-report --session LAB-S-…`; mock marker `[mock:nostart]`. Backend **498**, unit
**116**, Playwright **33**; evidence `evidence/S1-E.2/preflight.txt`.

**S1-E.2 GPT-Live adapter (ACCEPTED as offline-verified; live validation pending).**
- **Backend** `app/voice/gpt_live.py` (adapter, URL guard, deterministic delegation, sideband close),
  `app/voice/gpt_live_mock.py` + CLI `call360 gpt-live-mock --port N` (loopback test double, fault markers
  `[mock:noclose|drop|error|expire=N|silent|delegate]` in the system prompt), paid gates and settlement in
  `app/voice/lab.py`, endpoints `/voice-lab/paid-switch`, `/paid-authorisations[/{id}/revoke]`,
  `/sessions/{id}/resolve-usage|provider-close`, `/trials/{id}/assessments`. Migration `0026_gpt_live_provider`.
- **Config** (all default off): `VOICE_LAB_GPT_LIVE_MODE` (DISABLED|LIVE), `VOICE_LAB_OPENAI_API_KEY` (backend only),
  `VOICE_LAB_GPT_LIVE_URL` (official host; loopback only in tests), `VOICE_LAB_GPT_LIVE_MOCK_URL` (loopback; enables
  provider GPT_LIVE_MOCK), `VOICE_LAB_CLOSE_TIMEOUT_S`.
- **Verification**: backend **494**, unit **115**, Playwright **33** (Playwright starts the mock on 8766); OpenAPI
  `c8b2b05778751be98ecb09ff48a977e64a972136c2d53f1e72d4e5f14bdb18e9`; evidence `evidence/S1-E.2/`.
- **Dev state**: default configuration (mode DISABLED, no key, no mock URL); paid switch off; no authorisations;
  LAB-S-00020 (confirmed) and LAB-S-00021 (resolved via sideband) are GPT_LIVE_MOCK sessions.
- **Gotchas**: Starlette re-cancels every await in a cancelled WebSocket handler — settle in a detached task; GPT-Live
  has no output-done/turn events (inferred client-side); trace detail keys must not be named `source`.

**S1-E.1 Voice Lab (ACCEPTED 2026-11-18).**
- **Backend** `app/voice/lab_cost.py` (providers MOCK / MOCK_METERED / GPT_LIVE-disabled, rate cards, limits,
  reservations under a per-class advisory lock), `app/voice/lab_eval.py` (pure evaluation `call360.voicelab-eval/1`),
  `app/voice/lab.py` (prompts, datasets, import, sessions, server recording, transcription, mock experiments, recovery),
  `app/api/voice_lab.py` (`/api/v1/voice-lab/*`, WebSocket `/voice-lab/sessions/{id}/stream`). Migration
  `0025_voice_lab` (15 `lab_*` tables; CHECKs forbid paid / retries / schedules / PAID rows; `voicelab.use` → USER +
  SC_CHECKER, `voicelab.manage` → ADMIN).
- **Frontend** `/voice-lab` (`src/features/voicelab/`), `useVoiceSession(adapter)` (DV-31).
- **Verification**: backend **486**, unit **115**, Playwright **33**; OpenAPI
  `3ac93e843d32fc447825ca54c47a2e55b91b01dfcb4616a54461ceb420d6ec7a`; evidence `evidence/S1-E.1/` (incl. `zero_spend.txt`).
- **Dev demo state**: LAB-P-0001…0003, LAB-D-0001 (4 cases), LAB-E-0001…0003, LAB-S-00001 (recorded); one SIMULATED
  reservation (USD 0.16 reserved, 0.018 reconciled); emergency stop released.
- **Gotchas**: experiments run in a background thread (tests set `app.state.voicelab_inline`); the Voice Lab
  Playwright spec runs in the `voice` project (fake microphone); lab budgets accumulate per Singapore day.

**S3-C (ACCEPTED 2026-11-18).**
- **Review service** `app/domain/review.py` (dispositions, case actions, readiness, maker-checker approvals, insert-only
  `review_decision`, idempotency keys, row-version checks), dossier `review_dossier.py`, API `app/api/review_workbench.py`
  (`/review/*`), fixtures `review_fixtures.py` + `call360 review-fixture --case … --answers '{…}' --confirm-synthetic`.
- **Migration** `0024_review_resolution` (review_approval, review_decision; `review.decide` → USER + SC_CHECKER,
  `review.approve` → SC_CHECKER). **UI**: Review Workbench tabs (Findings / Cases to review / Approvals) and
  `/reviews/cases/:caseId` (DV-30).
- **Verification**: backend **476**, unit **113**, Playwright **32**; OpenAPI
  `75bc2f3206990337e5c1a31eff38096d676aa0b5f4f62c48cbc2bc0950166f2b`; evidence `evidence/S3-C/`.
- **Dev demo state**: CB-2026-10505 VERIFIED (RVA-0001 maker dev.user → checker dev.checker); CB-2026-10506 ESCALATED
  (FND-ENG-00001 confirmed, FND-RVW-00001 open). Both are intake-created (seed digest MATCH).
- **Gotchas**: reviewing seeded cases changes the seed digest (use intake cases for demos); the Playwright suite is near
  the 20 logins/IP/min limit — `workbench-review.spec.ts` waits 61 s at its end.

**S3-B (ACCEPTED 2026-11-18).**
- **Engine** `app/domain/finding_engine.py` (pure; `call360.finding-engine/1`): evaluation outcome → finding via
  governed rules (scope question / control / any, trigger, category, severity + justification, review); fixed classes
  (customer discrepancy, missing evidence, system-data issue, human assessment); uncovered outcomes "not converted";
  deterministic `finding_key`.
- **Configuration**: `finding_rules.py` + `app/api/finding_rules.py`, tables `finding_rule_set_version` / `_event`
  (maker-checker with script.edit / script.approve / script.publish; immutable published). UI **Finding Rules**
  `/finding-rules` (DV-29).
- **Simulation**: `simulation_findings.py`; `POST/GET /script-simulations/{run}/evaluations/{eval}/findings`,
  `GET …/finding-sets/{id}`; insert-only `simulation_finding_set` / `simulation_finding` (unique keys). Scenario
  expectations gain `findings`; batch runs accept `finding_rule_set_version_id`. `persist_operational` (synthetic
  fixtures only, no API).
- **Migration** `0023_compliance_findings`. **Verification**: backend **474**, unit **111**, Playwright **31**; OpenAPI
  `4c0e3c641d87fa08eb7100c792e1d1d78ac77c13b1e8b97069e72d949d18bc29`; evidence `evidence/S3-B/`.
- **Dev demo state**: SG finding rules v1 PUBLISHED (6 synthetic rules); FGS-0001 (CB-2026-10066 discrepancy run, 1 HIGH
  finding via SYN-CTRL-04), FGS-0002 (correct run, no findings), FGS-0003 (SG_EVALUATION_DEMO run, 3 findings). No
  operational finding written. EVL-0003 (run SIM-2026-10504-0008, Demo Operations User, 08:31) predates this work.

**S3-A (ACCEPTED 2026-11-18).**
- **Engine** `app/domain/answer_evaluation.py` (pure; `call360.answer-evaluation/1`): methods = expected-answer
  policies plus `NUMERIC_COMPARE`, `ENUM_MATCH`, `ENUM_MATCH_POLICY_FACT`; results MATCH / MISMATCH / UNRESOLVED /
  NOT_ASKED / MISSING_EXPECTED_FACT / NOT_APPLICABLE / NOT_EVALUATED / HUMAN_ASSESSMENT_REQUIRED. MATCH is not a
  compliance pass; MISMATCH is not a finding.
- **Rules** live in `question_revision.expected_value` JSON + `policy_fact_key` (no new columns on seeded tables);
  validated by `answer_evaluation.configure` from `script_authoring.normalise_question`. Script Studio "Evaluation
  method" + "Evaluation rule" fieldset.
- **Evidence**: interactive runs → insert-only `simulation_answer_evaluation` (`app/domain/simulation_evaluation.py`,
  `POST/GET /script-simulations/{id}/evaluations`, replay on read); scenarios → `simulation_result.actual.evaluations`.
  Scenario expectations gain `evaluations` and `basis` (INDEPENDENT / GENERATED_BASELINE). Operational
  `rule_evaluation` is never written in S3-A.
- **Migration** `0022_answer_evaluation` (CHECK constraints widened on `question_revision`; new table).
- **Verification**: backend **455**, unit **108**, Playwright **30**; OpenAPI
  `18c0b42394b866670de48f9dc4d531aaf06ba621b3810e20b48907564d259580`; evidence `evidence/S3-A/`.
- **Dev demo state**: draft family **SG_EVALUATION_DEMO v1.0** (unpublished; keep or abandon); runs
  SIM-2026-10504-0006 (completed, EVL-0001: 2 mismatches) and -0007 (incomplete, EVL-0002: 2 unresolved); SCN-0004
  (generated baseline) and BAT-0003 (passed). CB-2026-10504 unchanged; SG_LIFECYCLE_DEMO v1.1 untouched.
- **Gotcha**: the Playwright suite runs close to the local login limit (20 / IP / minute); keep login-heavy new specs
  late in alphabetical order (`simulation-evaluation.spec.ts`).

**S2-E (ACCEPTED 2026-11-18).**
- **Workbench** `/simulator` (nav "Simulation Workbench"; DV-27) has three tabs:
  - Interactive simulator: pinned script or any draft / published version on any synthetic case (VERSION_TEST mode,
    isolated content snapshot, no assignment), plus "Save as scenario".
  - Scenario library: structured steps and expectations, dry run, "use actual as expectations", insert-only revisions,
    copy / archive, batch run.
  - Test runs and coverage: explained pass / fail / execution error / invalid, a stale flag, structural coverage, and a
    two-version comparison.
- **One engine**: `app/domain/scenario_runner.py` drives the existing controller. The service is
  `app/domain/simulation_workbench.py`; the API is `app/api/simulation_workbench.py`.
- **Migration** `0021_simulation_workbench`: scenario, insert-only revision / snapshot / batch / result tables, and the
  run mode VERSION_TEST.
- **Verification**: backend **416**, unit **106**, Playwright **29**; OpenAPI
  `df53e258606a81030b711815b9b62992f2dac4c7319e95c0e10ec763060e2121`. Record in `S2.md` "S2-E as built"; evidence in
  `evidence/S2-E/`.
- **Dev demo state**:
  - draft **SG_LIFECYCLE_DEMO v1.1** is open (recording refusal terminates; keep, submit or abandon);
  - scenarios SCN-0001…0003 (on v1.0);
  - BAT-0001 (3 passed) and BAT-0002 (v1.0 vs v1.1: the recording scenario fails on B, explained);
  - CB-2026-10504 has a VERSION_TEST run (terminated); its case, assignment, holds and attempts are unchanged.

**S2-D.1 (ACCEPTED 2026-11-18; conditions D-67 live eligibility, D-68 cloud consent before any cloud audio, D-69 demo
rule kept).**
- **Lifecycle model**: `app/domain/lifecycle.py` defines stages in a fixed system order (opening → identity →
  disclosure → consent → verification → closing), item roles, and the permitted on-failure behaviours. The
  system-enforced minimums cannot be relaxed. Every rule is a synthetic assumption, recorded in
  `SCRIPT_GOVERNANCE_AND_ASSIGNMENT.md` "Conversation lifecycle (S2-D.1)".
- **Script Studio** configures lifecycle sections and items: role, on-failure behaviour, the policy-disclosure flag and
  deliver-on-termination. It reuses versioning and maker-checker, and validation checks lifecycle rules. Published
  versions are unchanged.
- **Controller** (`question_controller.py`, engine `/2`) enforces:
  - an identity gate, with policy-disclosing items withheld until identity is confirmed;
  - willingness to proceed, recording consent and cloud processing as separate gates;
  - mandatory disclosure delivery;
  - the conversation events wrong person, callback requested, declined to continue and interrupted;
  - termination, with only termination-closing statements afterwards.
- **Reporting**: mandatory completion is reported separately from the gates. Identity and consent outcomes are labelled
  simulated, and compliance is not evaluated.
- **API and UI**: `POST /script-simulations/{id}/event`, plus a Text Simulator lifecycle panel and controls (DV-26).
- **Migration** `0020_conversation_lifecycle` (side-table columns; the seed digest is unchanged).
- **Verification**: backend **399**, unit **104**, Playwright **28**; OpenAPI
  `c0bbbbd7d5a8de20aa12b77671ffb9679bcde1a9bc8dbfab62c522fa712d2bfe`. Record in `S2.md` "S2-D.1 as built"; evidence in
  `evidence/S2-D.1/`.
- **Dev demo** (governed APIs):
  - new family `SG_LIFECYCLE_DEMO` v1.0 (PUBLISHED; authored by dev.user, approved and published by dev.checker);
  - rule `S2D1-LIFECYCLE-DEMO` v1 (PUBLISHED, priority 3: SG · protection · bancassurance · annual — withdraw via Rule
    Studio if not wanted);
  - case CB-2026-10504 (intake, engine-assigned) with SIM runs COMPLETED, TERMINATED (identity failed) and TERMINATED
    (declined to proceed); no attempts, state VALIDATED.

**S2-D (ACCEPTED 2026-11-17).** Pure, event-sourced, provider-independent question
controller `app/domain/question_controller.py` (plan from the pinned script + fact snapshot + SBQ band; approved
conditions only; fixed order; states requested → presented → answered → completed / clarification → re-prompt
(approved `max_reprompts`) → unresolved / skipped-by-condition; typed answers; duplicate / stale-action / bypass
refusal; COMPLETED only when every applicable mandatory question is completed). Text Simulator `/simulator` (Governance
nav; Call Detail "Start text simulation"). Simulation records only (`script_simulation_run`, insert-only
`script_simulation_event`); no operational evidence, holds, states or KPIs. Permission `script.simulate` (USER,
SC_CHECKER). Migration `0019_script_simulation`. Code `app/domain/{question_controller,script_simulation}.py`,
`app/api/script_simulations.py`, `src/features/simulator/`; tests `tests/test_{question_controller,script_simulation}.py`,
`e2e/text-simulator.spec.ts`. Verification: backend **389**, unit **102**, Playwright **27**; OpenAPI
`447a41b22c44a6e369609ac8a78d07bbe57f2d8e07a6c3cb330d0d0b7fdc4f7e`. Record `S2.md` "S2-D as built"; evidence
`evidence/S2-D/`.

**S2-C (ACCEPTED 2026-11-17).** Deterministic assignment reusing the S2-B pure matcher with
selected-contact evaluation (D-62 clarified): Call Detail "Script assignment" card (read-only preview → confirm →
apply; pinned script, rule, explanation, failure reasons, holds, attempt history), batch "Assign scripts to unassigned
cases" on Assignment Rules. Apply pins an immutable ENGINE `script_assignment`, releases `AWAITING_SCRIPT_ASSIGNMENT`
(and an engine-placed `AWAITING_SCRIPT_REVIEW`), keeps all other holds, never changes the case state, never reassigns,
idempotent by key; ambiguity places `AWAITING_SCRIPT_REVIEW`. Permission `script.assign` (USER). Migration
`0018_script_assignment_engine` (`script_assignment_attempt` ledger). Code `app/domain/script_assignment.py`,
`app/api/script_assignments.py`, `src/features/case/ScriptAssignmentPanel.tsx`, `src/features/rules/AssignmentBatch.tsx`;
tests `tests/test_script_assignment.py`, `e2e/script-assignment.spec.ts`. Verification: backend **381**, unit **101**,
Playwright **26**; OpenAPI `283300f0fa1f7c1158953f10db2efda07ca8fdd2048d767e97219f6139727470`. Record `S2.md` "S2-C as
built"; evidence `evidence/S2-C/`.

**S2-A.1 (ACCEPTED 2026-11-17).** Draft-scoped control links (`script_version_control_link`),
per-revision intent/category (`question_revision_detail`), question-bank reuse = latest published revision only,
audited Abandon Draft (DRAFT → ABANDONED, makers only, nothing deleted), checker must acknowledge each mandatory
question without a mapped control, "Synthetic · not production-approved" labelling. Migration
`0016_script_draft_isolation`. Record `S2.md` "S2-A.1 as built".

**S2-B (ACCEPTED 2026-11-17).** Visual rule builder (approved fields and governed values only;
calculated specificity; published targets; effective dates; explicit fallback), server explanations and validation,
conflict analysis, side-effect-free simulation (READ ONLY transaction) with per-case traces, maker-checker lifecycle
with explicit supersede, immutable published rule versions, version comparison, change history, abandon, copy.
Owner-approved precedence D-58…D-60 recorded in `docs/product/SCRIPT_GOVERNANCE_AND_ASSIGNMENT.md`; D-61…D-65
proposed. Pure engine `app/domain/rule_engine.py`; loaders `rule_inputs.py`; lifecycle `rule_authoring.py`; API
`app/api/assignment_rules.py`; migration `0017_assignment_rule_authoring`; frontend `src/features/rules/` and
`src/features/scripts/AssignmentRulesPage.tsx`; E2E `e2e/assignment-rules.spec.ts`. Verification: backend **377**,
frontend unit **99**, Playwright **25** passed; OpenAPI `d50a5a43dbcda109f34cfaf6fa3f07c048de1ca04aecaa11e377845ab9ef82cb`.
Chrome demo recorded in `evidence/S2-B/chrome_demo.txt`. Record `S2.md`; evidence `evidence/S2-B/`.

**S1-D — Transcript and playback (awaiting acceptance).** Local faster-whisper 1.2.1 small.en transcription; see
`S1.md` and `evidence/S1-D/`. Outstanding: the owner's real-microphone transcript check and acceptance.

**Databases (local PostgreSQL 15, database `Call360_db`).** Both schemas at Alembic head
**`0026_gpt_live_provider`**: `call360` (development, never reset; backup before 0026
`~/call360-backups/pre_s1e2_20261118_135642/` — seed digest MATCH and audit chain OK after the S1-E.2 demo, 2923 events;
backup before 0025
`~/call360-backups/pre_s1e1_20261118_123841/` — seed digest MATCH and audit chain OK after the S1-E.1 demo, 2909 events;
backup before 0024
`~/call360-backups/pre_s3c_20261118_094108/` — seed digest MATCH and audit chain OK after the S3-C demo, 2874 events;
backup before 0023
`~/call360-backups/pre_s3b_20261118_084828/` — seed digest MATCH and audit chain OK after the S3-B demo, 2855 events;
backup before 0022
`~/call360-backups/pre_s3a_20261118_081100/` — seed digest MATCH and audit chain OK after the S3-A demo, 2830 events,
249 assignments; backup before 0021
`~/call360-backups/pre_s2e_20261117_172518/` — seed digest MATCH and audit chain OK after the S2-E demo, 2800 events;
backup before 0020
`~/call360-backups/pre_s2d1_20261117_163141/` — seed digest MATCH and audit chain OK after the S2-D.1 demo, 2789 events,
249 assignments; backups before 0016/0017
`~/call360-backups/pre_s2b_20261117_141600/`, before 0018 `pre_s2c_20261117_150940/`, before 0019
`pre_s2d_20261117_153706/`; seed digest `2ead19f36e09bdf3…` MATCH and audit chain OK after the S2-D demo, 2749 events;
the 245 historical assignments unchanged plus 3 engine assignments) and `call360_test` (reset by the test harness and E2E
setup only). Development content beyond the seed: 12 runtime browser test sessions on CB-2026-10048; script families
`SALES_VERIFICATION_SG_PROTECT` v1.0 (PUBLISHED) and `SALES_VERIFICATION_SG_PROTECT1` v1.0 (empty DRAFT); rules
`SG-ILP-HIGH-RISK` v1 (SUPERSEDED) and v2 (PUBLISHED, priority 4, ILP + High/Medium → SALES_VERIFICATION_SG v1.1) and
draft `SG-ILP-PROTECT-CONFLICT` v1 (ABANDONED, conflict demo); S2-C demo cases CB-2026-10501 (assigned
SALES_VERIFICATION_SG v1.1 by SG-SALES-VERIFY v2) and CB-2026-10502 (ambiguous attempt recorded, then — on the owner's
instruction after the conflict was resolved — assigned v1.1 by SG-ILP-HIGH-RISK v2 via the API, both script holds
released, ambiguous attempt and audit preserved); labelled demo rule `S2C-DEMO-LEGACY-CONFLICT` v1 (directly inserted,
WITHDRAWN); S2-D demo case CB-2026-10503 (ILP High, assigned v1.1) with simulation SIM-2026-10503-0001 (COMPLETED, 53
events; no attempts, state VALIDATED); S2-D.1 demo content as listed above (CB-2026-10504). No historical case was
reassigned.

**Git (all three on `main`, in sync with `origin/main` at the owner's last commits; remote `github.com/Kibana21/…`).**
The owner's commits `fd075f9` / `84ffb2b` / `044235d` include work through S2-C. **Uncommitted: S2-D and S2-D.1** (as of
2026-11-18):

| Repo | HEAD | Uncommitted (S2-D + S2-D.1 + S2-E; commits need owner authorisation; S2-E adds the files listed in `S2.md` "S2-E as built") |
|---|---|---|
| Call360-specs | `fd075f9` | `docs/acceptance/S2.md`, this handoff, `docs/product/SCRIPT_GOVERNANCE_AND_ASSIGNMENT.md`; new `evidence/S2-D/`, `evidence/S2-D.1/`, `evidence/S2-C/cb_2026_10502_resolution.txt` |
| Call360-backend | `84ffb2b` | new migrations 0019–0020, `app/api/script_simulations.py`, `app/domain/{lifecycle,question_controller,script_simulation}.py`, tests `test_{question_controller,script_simulation,conversation_lifecycle,lifecycle_authoring}.py`; modified `app/api/{case_detail,schemas,script_authoring}.py`, `app/domain/{catalog,script_authoring}.py`, `app/main.py`, OpenAPI artifacts, `tests/test_{admin_access,authz_admin,stage0_acceptance}.py` |
| Call360-frontend | `044235d` | new `src/features/simulator/`, `e2e/{text-simulator,conversation-lifecycle}.spec.ts`; modified `src/App.tsx`, `src/app/nav.ts`, `ScriptAssignmentPanel.tsx`, `ScriptEditor.tsx`, `ScriptFamilyPage.tsx`, `ScriptPages.test.tsx`, pinned OpenAPI, contract lock, generated schema, `docs/design/DEVIATIONS.md` (DV-25, DV-26) |

Superseded table (state at the S2-D session, before the owner's commits):

| Repo | HEAD | Uncommitted then |
|---|---|---|
| Call360-specs | `bd0b348` | `docs/acceptance/S2.md`, `evidence/S2-A/`, `evidence/S2-B/`, `evidence/S2-C/`, `evidence/S2-D/` (new); `S1.md`, this handoff, `docs/product/SCRIPT_GOVERNANCE_AND_ASSIGNMENT.md` |
| Call360-backend | `92ba5ee` | new migrations 0015–0019, `app/api/{script_authoring,assignment_rules,script_assignments,script_simulations}.py`, `app/domain/{script_authoring,rule_engine,rule_inputs,rule_authoring,script_assignment,question_controller,script_simulation}.py`, tests `test_{script_authoring,script_draft_isolation,rule_engine,assignment_rules,script_assignment,question_controller,script_simulation}.py`; modified `tests/test_stage0_acceptance.py`; modified `app/domain/intake.py`, `tests/test_intake.py`; modified `app/api/{case_detail,schemas,scripts}.py`, `app/audit/scope.py`, `app/cli.py`, `app/core/settings.py`, `app/domain/{catalog,seed}.py`, `app/main.py`, `app/security/scope.py`, OpenAPI artifacts, `scripts/e2e_setup.py`, 7 test files |
| Call360-frontend | `417daac` | new `src/features/rules/`, `src/features/scripts/ScriptEditor.tsx`, `src/features/case/ScriptAssignmentPanel.tsx`, `src/features/simulator/`, `e2e/{script-studio,assignment-rules,script-assignment,text-simulator}.spec.ts`; modified `src/app/nav.ts`; modified Call Detail and its tests, intake outcome, `e2e/cp04a-checks.ts`; modified Script Studio and Assignment Rules pages, `App.tsx`, `AppShell.tsx`, tests, `e2e/{f6-checks,cp06-checks,helpers}.ts`, pinned OpenAPI, contract lock, generated schema, `docs/design/DEVIATIONS.md` (DV-24) |

**Running services at handover** (may stop when this Claude Code session ends — restart with §4 commands): backend
development server on 127.0.0.1:8000, frontend Vite server on 127.0.0.1:5173, PostgreSQL on 5432. Playwright starts its
own servers on 8001/5174.

**Outstanding owner decisions and approvals (none of these is approved):**
1. Accept S2-E (or request refinements). Decide the dev draft `SG_LIFECYCLE_DEMO` v1.1 (keep / submit / abandon) and,
   later, withdrawal of `S2D1-LIFECYCLE-DEMO` (D-69).
2. Accept S1-D (after the real-microphone transcript check).
3. Authorise commits (separate per repository) for S2-D, S2-D.1 and S2-E.
4. Authorise S2-E; then S1-E.
5. Before S1-E: approval to use GPT-Live, API-key handling and data-handling terms.
6. Stage 0 governance: name the SEC-008 security reviewer and complete the review; name the three Stage 0 approvers
   (C-20). Stage 0 stays NOT_ACCEPTED until both.
7. Production policies still open: approved consent wording (DEC-004), recording/transcript retention (DEC-015).
8. Security debts: rotate the development database password (RR-12) and use a non-superuser application role
   (RR-11) before any non-synthetic data.
9. Deferred, not authorised: CP0.4b remainder (mock upstream, scheduling, corrections, saved drafts, Admin
   Integrations), saved views.

**How to resume:** read this §0, then `docs/acceptance/S2.md` and `S1.md`; check `git status` in all three repos;
run the verification commands in §4 (backend tests and Playwright **never at the same time** — both use
`call360_test`); wait for the owner's next explicit instruction.

## 1. Checkpoint status

| Checkpoint | Status | Record |
|---|---|---|
| CP0.0 Specification foundation | **ACCEPTED** 2026-11-15 | `docs/acceptance/CP0.0.md` |
| CP0.1A Core authentication and application shell | **ACCEPTED** 2026-11-15 | `docs/acceptance/CP0.1A.md` |
| CP0.1B-1 Configuration foundation | **ACCEPTED** 2026-11-15 | `docs/acceptance/CP0.1B-1.md` |
| CP0.1B-2 Market scope → **F0** (Singapore-only, D-39) | **ACCEPTED** 2026-11-15 | `docs/acceptance/S0.md`, `evidence/F0-F1/` |
| **F1** Overview | **ACCEPTED** 2026-11-15 (limitations accepted) | `evidence/F0-F1/` |
| CP0.2 Domain schema and seed | **ACCEPTED** 2026-11-15 (RR-12 deferred; D-39) | `docs/acceptance/CP0.2.md` |
| **F2** Work Queues and search | **ACCEPTED** 2026-11-15 | §9, `evidence/F2/` |
| **F3** Call Detail | **ACCEPTED** 2026-11-15 | §10, `evidence/F3/` |
| **F4** Policy Explorer | **ACCEPTED** 2026-11-15 | §11, `evidence/F4/` |
| **F5** SBQ Risk Workbench | **ACCEPTED** 2026-11-16 | §12, `evidence/F5/` |
| **CP0.4a** Insurance transaction intake | **ACCEPTED** 2026-11-16 | §13, `evidence/CP0.4a/` |
| **CP0.4b-UI** Manual Intake portal | **ACCEPTED** 2026-11-16 (UI portion only) | §14, `evidence/CP0.4b-UI/` |
| **F6** Script Studio and Assignment Rules (read-only) | **ACCEPTED** 2026-11-16 | §15, `evidence/F6/` |
| **F7** Review Workbench and Voice Studio (read-only) | **ACCEPTED** 2026-11-16 | §16, `evidence/F7/` |
| **CP0.1B-3** Administration completion | **ACCEPTED** 2026-11-17 | §17, `evidence/CP0.1B-3/` |
| **CP0.6** Integrated Stage 0 verification | **ACCEPTED (technical)** 2026-11-17; Stage 0 governance PENDING | §18, `S0.md`, `evidence/CP0.6/`, `evidence/CP0.6-F1/` |
| CP0.4b remainder | NOT_STARTED (deferred) | `docs/plans/S0_IMPLEMENTATION_PLAN.md` |
| **S1-A** Full-duplex browser voice POC (mock provider) | **ACCEPTED** 2026-11-17 | §19, `S1.md`, `evidence/S1-A/` |
| **S1-B** Session lifecycle and event persistence | **ACCEPTED** 2026-11-17 (limitations accepted) | §19, `S1.md`, `evidence/S1-B/` |
| **S1-C** Consent-gated recording | **ACCEPTED** 2026-11-17 (D-45…D-48 decided; D-48 KPI correction implemented) | §19, `S1.md`, `evidence/S1-C/` |
| S1-D Transcript and playback | **IMPLEMENTED AND VERIFIED**, awaiting owner acceptance (D-49…D-53 approved) | §0, §19, `S1.md`, `evidence/S1-D/` |
| S1-E Real provider (GPT-Live) live validation | **NOT STARTED** — adapter offline-verified (S1-E.2); first paid smoke test needs separate authorisation | `S1.md` |
| S2-A Editable Script Studio | **ACCEPTED** 2026-11-17 (D-54…D-57 approved subject to S2-A.1) | `S2.md`, `evidence/S2-A/` |
| S2-A.1 Owner refinements | **ACCEPTED** 2026-11-17 | `S2.md`, `evidence/S2-B/` |
| S2-B Editable Assignment Rules | **ACCEPTED** 2026-11-17 (D-58…D-66 approved; D-62 clarified) | `S2.md`, `evidence/S2-B/` |
| S2-C Deterministic Script Assignment | **ACCEPTED** 2026-11-17 | `S2.md`, `evidence/S2-C/` |
| S2-D Deterministic Question Controller | **ACCEPTED** 2026-11-17 | `S2.md`, `evidence/S2-D/` |
| S2-D.1 Conversation Lifecycle and Control Gates | **ACCEPTED** 2026-11-18 (conditions D-67…D-69) | `S2.md`, `evidence/S2-D.1/` |
| S2-E Callback Simulation Workbench | **ACCEPTED** 2026-11-18 (generated-baseline and v1.1-draft conditions) | `S2.md`, `evidence/S2-E/` |
| S3-A Deterministic Answer Evaluation Engine | **ACCEPTED** 2026-11-18 (D-70…D-75 approved) | `S3.md`, `evidence/S3-A/` |
| S3-B Deterministic Compliance Findings Engine | **ACCEPTED** 2026-11-18 (D-70…D-80 approved with conditions) | `S3.md`, `evidence/S3-B/` |
| S3-C Human Review and Case Resolution | **ACCEPTED** 2026-11-18 (D-81…D-86 presented for confirmation) | `S3.md`, `evidence/S3-C/` |
| S1-E.1 Voice Lab Foundation | **ACCEPTED** 2026-11-18 (D-87…D-94 presented for confirmation) | `S1.md`, `evidence/S1-E.1/` |
| S1-E.2 GPT-Live provider adapter | **ACCEPTED** 2026-11-18 as offline-verified; live-provider validation **PENDING** (preflight complete; owner runs the smoke test) | `S1.md`, `evidence/S1-E.2/` |
| S2-E Text-based callback simulation | NOT_STARTED, not authorised (owner's planned sequence) | `S2.md` |
| Stage 0 governance acceptance | **PENDING** (SEC-008 review, named approvers C-20) | `S0.md`, `docs/security/SEC-008_REVIEW_HANDOFF.md` |

## 2. Verification history (latest first)

| Checkpoint | Backend | Frontend unit | Playwright | OpenAPI SHA-256 | Migration head | Evidence |
|---|---|---|---|---|---|---|
| ASG-2B (+ ASG-2A acceptance, three states) | 825 | 612 | 33 standard · 13 prototype · 22 persisted | `e0add7fcd59e3070c1494209fe1769905b3dbff735f069824fc984bbe2fc3624` | `0032_survey_coordinated_sim` (dev at `0031`) | `evidence/ASG-2B/` |
| ASG-2A (+ ASG-1 read closure) | 822 | 612 | 33 standard · 13 prototype · 21 persisted | `2b3b0c8e86163df84aa516a1029aed7b4aae64a72ab6eba62cc89f621473e94c` | `0031_survey_assignment_groups` (dev at `0030`) | `evidence/ASG-2A/` |
| ASG-1 (+ SS-03B closure) | 818 | 612 | 33 standard · 13 prototype · 20 persisted | `38f2034b65bf520e0e4b32b8f413bf9c0789b6fac314f7abc8d451ffbf64c74b` | `0030_survey_assignment` (dev at `0029`) | `evidence/ASG-1/` |
| SS-03B (+ LIB-1 security closure) | 814 | 612 | 33 standard · 13 prototype · 19 persisted | `5799e44faef0bc510a506a8f6033194fe6e84b8e72f08b1f2b533e59baf1bd1f` | `0029_survey_simulation` (dev at `0028`) | `evidence/SS-03B/` |
| S1-E.2A | 503 | 116 | 33 | `550e742339df5297c946b7add019de5dd67ac028c9fc51609d9e7492b92c972d` | `0026_gpt_live_provider` | `evidence/S1-E.2A/` |
| S1-E.2 preflight | 498 | 116 | 33 | `c8b2b05778751be98ecb09ff48a977e64a972136c2d53f1e72d4e5f14bdb18e9` | `0026_gpt_live_provider` | `evidence/S1-E.2/preflight.txt` |
| S1-E.2 | 494 | 115 | 33 | `c8b2b05778751be98ecb09ff48a977e64a972136c2d53f1e72d4e5f14bdb18e9` | `0026_gpt_live_provider` | `evidence/S1-E.2/` |
| S1-E.1 | 486 | 115 | 33 | `3ac93e843d32fc447825ca54c47a2e55b91b01dfcb4616a54461ceb420d6ec7a` | `0025_voice_lab` | `evidence/S1-E.1/` |
| S3-C | 476 | 113 | 32 | `75bc2f3206990337e5c1a31eff38096d676aa0b5f4f62c48cbc2bc0950166f2b` | `0024_review_resolution` | `evidence/S3-C/` |
| S3-B | 474 | 111 | 31 | `4c0e3c641d87fa08eb7100c792e1d1d78ac77c13b1e8b97069e72d949d18bc29` | `0023_compliance_findings` | `evidence/S3-B/` |
| S3-A | 455 | 108 | 30 | `18c0b42394b866670de48f9dc4d531aaf06ba621b3810e20b48907564d259580` | `0022_answer_evaluation` | `evidence/S3-A/` |
| S2-E | 416 | 106 | 29 | `df53e258606a81030b711815b9b62992f2dac4c7319e95c0e10ec763060e2121` | `0021_simulation_workbench` | `evidence/S2-E/` |
| S2-D.1 | 399 | 104 | 28 | `c0bbbbd7d5a8de20aa12b77671ffb9679bcde1a9bc8dbfab62c522fa712d2bfe` | `0020_conversation_lifecycle` | `evidence/S2-D.1/` |
| S2-D | 389 | 102 | 27 | `447a41b22c44a6e369609ac8a78d07bbe57f2d8e07a6c3cb330d0d0b7fdc4f7e` | `0019_script_simulation` | `evidence/S2-D/` |
| S2-C | 381 | 101 | 26 | `283300f0fa1f7c1158953f10db2efda07ca8fdd2048d767e97219f6139727470` | `0018_script_assignment_engine` | `evidence/S2-C/` |
| S2-A.1 + S2-B | 377 | 99 | 25 | `d50a5a43dbcda109f34cfaf6fa3f07c048de1ca04aecaa11e377845ab9ef82cb` | `0017_assignment_rule_authoring` | `evidence/S2-B/` |
| S2-A | 363 | 96 | 24 | `d35e791e04be538bd6d0d99e224133319d3f45e038035e7fcaa172eef8bf0ea8` | `0015_script_authoring` | `evidence/S2-A/` |
| S1-D | 357 | 94 | 23 | `e0a02959438fccd6750f89836c749ffa202b338d24580efa9a831b121d52ecea` | `0014_transcript` | `evidence/S1-D/` |
| D-48 correction | 338 | 89 | — | `cc52479f…` (unchanged) | `0013_recording` | `evidence/S1-C/d48_kpi_correction.txt` |
| S1-C | 334 | 89 | 22 | `cc52479f8d01be081c600ab9c39bc678ce384d53fc7a429fa123ca3acb5ac0fd` | `0013_recording` | `evidence/S1-C/` |
| S1-B | 325 | 86 | 20 | `f057e6dbd6c985c87200569ef6ed081f74a1e3e982c36dc6d54f6e4c4e3e54b3` | `0012_session_event` | `evidence/S1-B/` |
| S1-A | — | — | — | `e45244f699ad9da410c8579f1f2f2151b112b1062daecc97cb4a38ff8db77dcd` | `0011_voice_session_permission` | `evidence/S1-A/` |
| F0/F1 (S0) | 193 | 35 | 16 | `5da1f16d98b2adc2dbbbb1e78fe15566f8a0fd1f933cef9d445413976c205724` | `0008_market_scope` | `evidence/F0-F1/` |

Later S0 checkpoints (F2…CP0.6) record their numbers in their sections below and in `S0.md`.

## 3. Development environment

- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2, Alembic, `uv` (`.venv` in `Call360-backend`). Dependencies include
  `faster-whisper==1.2.1` (S1-D; pulls `huggingface-hub`, which also installs `httpx2` — Starlette's TestClient now
  uses it, test-only effect).
- **Frontend:** React/TypeScript, Vite, TanStack Query, `openapi-fetch` with types generated from the backend OpenAPI
  (`npm run api:generate` / `api:check`), Vitest, Playwright (Chromium; `voice` project uses a fake microphone file).
- **Voice:** mock provider only (keyless, fixed synthetic message); WebSocket audio transport; consent-gated
  encrypted recording; local offline transcription. No GPT-Live, no Genesys, no real customers.

## 4. Repositories, databases, local files and commands

**Database:** local PostgreSQL 15, database `Call360_db`.

| Schema | Login role | Head | Notes |
|---|---|---|---|
| `call360` (development) | `Call360_db_user` (superuser, RR-11) | `0021_simulation_workbench` | S0-SEED-1 (195 SG cases visible, 55 MY hidden); never reset; seed digest `2ead19f3…` MATCH; runtime test sessions and demo scripts listed in §0 |
| `call360_test` | `call360_test_user` (no superuser, no access to `call360`) | `0021_simulation_workbench` | reset and seeded by pytest and `scripts/e2e_setup.py` only |

**Development accounts** (passwords only in `Call360-backend/.env.local`): `dev.admin` (Demo Administrator,
LOCAL_ADMIN), `dev.user` (Demo Operations User, LOCAL_USER_SG — script author), `dev.checker` (Dev S&C Checker,
LOCAL_SC_CHECKER_SG — script approver/publisher, created 2026-11-17 with `call360 create-local-user`). E2E accounts
(random passwords, `Call360-frontend/e2e/.auth/accounts.json`): `e2e.admin`, `e2e.user`, `e2e.victim`, `e2e.tabs`,
`e2e.checker`.

**Local files (gitignored or outside the repositories; never commit, never print secret values):**

| Path | Holds |
|---|---|
| `Call360-backend/.env` | development DB URL and secrets; PII keys; `RECORDING_ENCRYPTION_KEY`; `TRANSCRIPTION_MODEL_DIR` |
| `Call360-backend/.env.test` | test role credentials and keys; `TRANSCRIPTION_MODEL_DIR` |
| `Call360-backend/.env.local` | development account passwords (`DEV_ADMIN_*`, `DEV_USER_*`, `DEV_CHECKER_*`) |
| `Call360-backend/.secrets/` | Ed25519 signing keys |
| `Call360-frontend/e2e/.auth/` | E2E accounts |
| `~/.call360/recordings/<schema>/` | encrypted recordings and transcript text objects (168 h local retention) |
| `~/.call360/models/faster-whisper-small.en/` | transcription model files (≈464 MB, SHA-256 pinned in `app/voice/transcript.py`) |
| `~/call360-backups/` | `pre_cp02_20261115_173043/` (includes `env.post_keys`, the only other copy of the development data-protection keys), `pre_f0_20261115_181045/`, `pre_s1c_20261117_025210/`, `pre_s2b_20261117_141600/` (pg_dump of schema `call360` before 0016/0017), `pre_s2c_20261117_150940/` (before 0018), `pre_s2d_20261117_153706/` (before 0019), `pre_s2d1_20261117_163141/` (before 0020), `pre_s2e_20261117_172518/` (before 0021), `pre_s3a_20261118_081100/` (before 0022), `pre_s3b_20261118_084828/` (before 0023), `pre_s3c_20261118_094108/` (before 0024), `pre_s1e1_20261118_123841/` (before 0025), `pre_s1e2_20261118_135642/` (before 0026) |

**Commands**
- Backend dev: `cd Call360-backend && make dev` → http://127.0.0.1:8000 (applies nothing; migrate with `make migrate`).
- Frontend dev: `cd Call360-frontend && npm run dev` → http://127.0.0.1:5173 (Vite proxies `/api`, incl. WebSocket).
- Backend checks: `make lint typecheck test contract-check secret-scan` (tests use `.env.test`).
- Frontend checks: `npm run typecheck && npm run lint && npm test && npm run api:check && npm run build && npm run secret-scan`; E2E `npx playwright test` (servers on 8001/5174 against `call360_test`).
- Specs: `python3 Call360-specs/scripts/validate_specs.py` (freezes BRD and register by SHA-256).
- Development integrity checks: `.venv/bin/call360 audit-verify`; seed digest via `app.domain.digest.content_digest`
  compared with the latest `SEED.MANIFEST` audit event (see `evidence/S2-A/dev_migration.txt`).
- Stop dev servers: `lsof -ti tcp:8000,5173 | xargs kill`.

## 5. Security and governance status, known risks

| Item | Status / risk | Action |
|---|---|---|
| Stage 0 governance | SEC-008 review not done; approvers not named (C-20) | Owner to name reviewer and approvers; never self-certify |
| RR-12 | Weak development DB password (exposed in an earlier session; never in Git) | Rotation deferred by the owner; follow `CP0.2_DEV_DEPLOYMENT.md` step 4 and 4b (restore data-protection keys from the backup) |
| RR-11 | Development app connects as a superuser | Non-superuser application role before any non-synthetic data |
| RR-01 | Audit integrity relies on the database only | External anchoring decision S5 |
| RR-04 / RR-05 / RR-09 / RR-10 | Local HTTP cookies without `Secure`; in-process rate limiter; chapter-level ASVS matrix; provisional parameters | Security owner review |
| Recording / transcript keys | Local keys, no rotation; data on the developer machine; transcript text shares the recording key | Production key management with S5 |
| Consent and retention | Test-only consent notice `S1C-TEST-1` (D-45); 168 h local retention (D-47) | Production wording DEC-004 and retention DEC-015 pending |
| Transcription accuracy | Best-effort; confident misrecognitions occur unmarked; accuracy measured only on 12 synthetic clips | S3 review controls; owner real-microphone check |
| Script governance (S2-A) | `SC_CHECKER` is a synthetic local role; ADMIN can manage group memberships | Enterprise SSO roles (S5); D-54 confirmation |
| Tooling | Chromium-only E2E; gitleaks generic rule gaps (Call360 formats covered; public model checksums allowed inline) | Track |

## 6. Key references

- **Specs:** `docs/spec/01_MASTER_BRD.md`, `02_CLAUDE_CODE_EXECUTION_PLAN.md`, `03_REQUIREMENTS_REGISTER.csv`;
  `docs/product/SCRIPT_GOVERNANCE_AND_ASSIGNMENT.md`, `S0_KPI_DEFINITIONS.md` (§3.1 D-48), `S0_SCREEN_SPEC.md`;
  `docs/data/CANONICAL_GRAIN_AND_RELATIONSHIPS.md`, `S0_DATA_MODEL.md`;
  `docs/security/IDENTITY_AUTHORIZATION_AND_AUDIT.md`, `S0_IDENTITY_ACCESS_DESIGN.md`, `THREAT_MODEL_S0.md`,
  `ASVS_S0_CONTROL_MATRIX.md`, `SEC-008_REVIEW_HANDOFF.md`; ADRs `docs/adr/ADR-0001…0008` (ADR-0007 Script Studio
  lifecycle); `docs/spec/APPROVED_EXCEPTIONS.md`.
- **Acceptance records:** `docs/acceptance/S0.md` (Stage 0, CP0.6), `CP0.0.md`, `CP0.1A.md`, `CP0.1B-1.md`,
  `CP0.2.md`, `S1.md` (S1-A…S1-D, decisions D-44…D-53), `S2.md` (S2-A, D-54…D-57, planned sequence),
  `S0_TEST_MATRIX.md`.
- **Evidence:** `docs/acceptance/evidence/<checkpoint>/` (F0-F1, F2…F7, CP0.4a, CP0.4b-UI, CP0.1B-3, CP0.6, CP0.6-F1,
  S1-A, S1-B, S1-C, S1-D, S2-A).
- **UI reference:** `Call360-frontend/docs/design/reference/Call360_Portal_Mockup.html`; deviations
  `Call360-frontend/docs/design/DEVIATIONS.md`.

## 7. Working notes for the next session

- S2-B tests and E2E commit rules into `call360_test`; tests that depend on precedence must use priorities that win over
  rules published by earlier tests (the schema is not reset between tests), and E2E checks must not assume "the first
  published rule" has assigned cases.
- The rule engine (`app/domain/rule_engine.py`) is pure; S2-C uses it via `app/domain/script_assignment.py`.
- `tests/test_script_assignment.py` resets and reseeds `call360_test` before and after itself (it withdraws the seeded
  catch-all rule and inserts legacy conflict rows). An existing API-039 owns `GET /cases/{id}/script-assignment`; the
  S2-C endpoints are `…/script-assignment/preview` and `…/script-assignment/apply`.
- The question controller (`app/domain/question_controller.py`) is pure and event-sourced: a voice provider (S1-E)
  should only call `record_delivery` / `submit_answer` / `request_clarification` against the current `action_id`;
  it never chooses questions. The Stage 0 all-route sweep needs a parameter entry for any new list route with a
  required query parameter (`tests/test_stage0_acceptance.py`).
- Chrome demos: a short-lived helper on 127.0.0.1:5199 can hand gitignored dev credentials to the login form (see
  `evidence/S2-B/chrome_demo.txt`); stop it afterwards.

- Never run backend pytest and Playwright concurrently: both use `call360_test` and pytest resets it.
- S2-A tests add authored script families to the test schema; the S0 script tests address the seeded family by code.
- Seed digest covers seeded (`SYSTEM:seed`) business rows only; authored and runtime rows do not change it, but
  altering seeded rows (e.g. superseding seeded `SALES_VERIFICATION_SG` v1.1) would.
- New groups must also be added to the `create-local-user` CLI choices (`app/cli.py`).
- The E2E suite is near the 20 logins/min IP limit; reuse sign-ins.
- Use bash (not zsh) for evidence scripts with word splitting; gitleaks flags 64-hex constants (mark public checksums
  with `# gitleaks:allow`).
- Chrome demonstrations sign in with the gitignored local credentials; never repeat them in chat or documents.

## 8. Stage 0 foundations as built (historical, CP0.1A and CP0.1B-1)

**CP0.1A (accepted)**
- **Backend:**
  - local login with Argon2id passwords;
  - EdDSA access JWTs (10 min) in HttpOnly cookies;
  - rotating refresh tokens stored as HMACs, with reuse detection. A benign multi-tab duplicate gets a `409 REFRESH_SUPERSEDED` and no token is minted;
  - server-side sessions, CSRF plus Origin checks, login throttling;
  - group → role → permission authorization resolved on every request;
  - hash-chained, append-only audit;
  - `bootstrap-admin` and `create-local-user` CLIs.
- **API:** 10 endpoints: health ×2, csrf, login, refresh, logout, `/me`, `GET/PATCH /admin/users`, `GET /admin/audit-events`.
- **Frontend:** a React shell reproducing the mockup (grouped sidebar; unbuilt items disabled with clock or "S4" indicators). Screens:
  - login, session expired, unauthorized;
  - a landing page showing real session data;
  - ADMIN Users (enable/disable with reason);
  - ADMIN Audit.

**CP0.1B-1 (accepted 2026-11-15)**
- **Tables (migration `0002_config_foundation`):** `code_list`, `code_list_version` (DRAFT → ACTIVE → SUPERSEDED, trigger-enforced, one ACTIVE per list), `code_value` (immutable unless its version is DRAFT), `feature_flag` (database CHECK stage lock), `feature_flag_change` (append-only).
- **APIs:**

  | ID | Endpoint |
  |---|---|
  | API-022 | `GET /admin/code-lists` (with full version history) |
  | API-023 | `POST /admin/code-lists/{code}/versions` (`based_on_version` + reason; atomic supersede/activate) |
  | API-024 | `GET /admin/feature-flags` |
  | API-025 | `PATCH /admin/feature-flags/{code}` (If-Match + reason) |

- **Seed (idempotent):** ten list definitions.
  - `market` is non-governed: labels editable, code set fixed (D-25).
  - Nine governed and read-only: `sbq_risk_band`, `risk_factor`, `case_hold_reason`, `case_closure_reason`, `case_cancellation_reason`, `finding_materiality_policy`, `kpi_sla_exemption_rule`, `callable_party_roles`, `synthetic_contact_ranges`.
  - `market` v1: `SG`, `MY`, marked synthetic.
  - Governed values are deliberately empty; CP0.2 seeds them.
  - Four flags, all off and stage-locked: `voice.browser_sessions` S1, `scripts.authoring` S2, `reviews.decisions` S3, `exports.evidence` S4.
- **UI:** Administration → Configuration:
  - lists with governance badges;
  - a version-history drawer;
  - a market label "New version" form;
  - flags with disabled, explained toggles for locked stages.

## 9. F2 Work Queues and search — ACCEPTED 2026-11-15

**As built (2026-11-15; evidence `docs/acceptance/evidence/F2/`; OpenAPI `1cc23a1b422be5748d74d2dd775e4403868f50c587ce0713bc3f192b834e9dd0`; no migration, head `0008_market_scope`):**
- Backend: `app/domain/register.py` (rows over the F1 `Facts`, so drilldowns reuse the KPI predicates), `app/api/cases.py` (API-035/036/076), `app/api/search.py` (API-070/071), `tests/test_register.py` (22 tests). Overview OPS-01…04/07 now carry typed register drilldowns (OPS-07 numerator only).
- Search: exact / prefix / FUZZY (= contained substring ≥ 4 characters; no edit-distance on identifiers so a near-miss MY reference cannot surface an SG record; no `pg_trgm` installed). Phone and email exact via `contact_method.value_hmac`. Terms are logged and audited (`SEARCH.EXECUTED`, API-070 only) as normalised SHA-256; the uvicorn access log has `q=` replaced by its digest.
- Queues: DUE_TODAY = OPS-02, OVERDUE = OPS-01 overdue, ON_HOLD = OPS-03 (by reason), AWAITING_CALLBACK = OPEN ∧ state `AWAITING_CALLBACK` (owner-approved 2026-11-15).
- Frontend: `/calls`, `/queues`, `/search`, top-bar combobox, Overview drilldown links; DV-12 lifted, DV-14/15 recorded.
- Not in F2 (raise if needed): register grain switch (`attempt`/`session`), facets for channel / FSC / owner / script version, customer-alias and FSC search; Call Detail (F3) and Policy Detail (F4) rows show an explicit F3/F4 state.

## 10. F3 Call Detail — ACCEPTED 2026-11-15

**As built (2026-11-15; evidence `docs/acceptance/evidence/F3/`; OpenAPI `f0f047162ec4e36c60e5815f58fcbff231ab04c561e4e696a2864282585b3739`; no migration):**
- Backend: `app/api/case_detail.py` (API-037…047 under `case.read`, API-063 under `script.read`; every lookup joins the case or script family with the caller's markets; missing/out-of-scope → identical audited 404), schemas in `app/api/schemas.py`, `tests/test_case_detail.py` (16 tests: all 12 golden fixtures, BOLA matrix over 12 routes, T-15 pin, masking, permissions). `app/domain/outcomes.py` gained `applicable_mandatory()` / `question_satisfied()` (refactor of the existing §1.1 logic, no rule change).
- `callable` / `callable_blockers` (API-037) are reported from persisted facts only: active blocking holds, no eligible contact selection, terminal case state. Labelled a data-level pre-check; call-time authority checks are S1.
- Frontend: `src/features/case/CallDetailPage.tsx` (+ tests), links from register, queues, Overview priority/activity and search; back link returns to the originating list with its filters; DV-16.
- Known limits: owner shown as "Unassigned" (no seeded owners; never fabricated); recordings/transcripts NOT_AVAILABLE (S1); review actions S3.
- Owner refinements (delivered with F4): the header shows "Contact pre-check (stored data only)": "Pre-check passed" or "Blocked" with one reason per cause and its evidence ("not an authorisation to call"); `precheckReasons()` merges `HOLD:<X>` and `<X>` blockers. API shape unchanged.

## 11. F4 Policy Explorer and Policy Detail — ACCEPTED 2026-11-15

**As built (2026-11-15; evidence `docs/acceptance/evidence/F4/`; OpenAPI `d8d118b32bed0a5ee7d70a238cbc9984d34b992104435a2bd26f23fedfd750bc`; no migration):**
- Backend: `app/domain/policy_register.py` (policy rows, filters, disjunctive facets, keyset paging; reuses F2 ref matching, HMAC contact search and cursors; case outcome from `load_facts`, effective band = latest FINAL assessment of the latest sale) and `app/api/policies.py`: API-050 `GET /policies`, API-051 `GET /policies/{id}` (header, record provenance and source/as-of per material field, external refs, related cases with outcome and pinned script), API-052 `/parties` (`party.read`; one card per party with role edges incl. ended, masked contact methods incl. ended/suppressed, per-case eligibility evidence incl. superseded), API-053 `/sales`, API-054 `GET /sales/{id}` (sale context, fact snapshots, risk history with `supersedes_id`, cases), API-055 `/history` (record lineage over policy, sales, role edges, snapshots, risk assessments; `field_changes` = NOT_AVAILABLE / `LEDGER_ARRIVES_CP0_4`). Every query filters `market_code = ANY(:markets)`; MY/missing → identical audited 404. `tests/test_policies.py`.
- Frontend: `src/features/policies/PolicyExplorerPage.tsx` (URL filters, facets, KPI tiles from facets, intake buttons disabled CP0.4) and `PolicyDetailPage.tsx` (tabs `sale`, `parties`, `risk`, `script`, `cases`, `source` in `?tab=`; `?sale=` must belong to the policy); `src/features/case/evidence.tsx` shared with Call Detail; links Policy → Call Detail, Call Detail → Policy (`?sale=`), register policy refs → Policy Detail, search policy hits → Policy Detail (`hitTarget` = `route`). DV-17.
- Known limits: no historical role edges exist in the seed (UI supports them); per-field change history waits for CP0.4; FSC display names are synthetic; "Correct field" (ADMIN, CP0.4) and "Request risk override" (S2) disabled.

## 12. F5 SBQ Risk Workbench — ACCEPTED 2026-11-16

**Owner acceptance (2026-11-16):** accepted for local synthetic-data development. Accepted limitations: no risk calculation or override engine; source-vs-rule conflicts are stored-assessment comparisons, not approved resolution decisions; no invented scores, thresholds or values; two SG sales remain unassessed. Next: CP0.4 intake proposal (not authorised).

**As built (2026-11-15; evidence `docs/acceptance/evidence/F5/`; OpenAPI `a4f49784316222b6c5fc43e47a9b71629e3067671cc5ba022c335c7ef77a9ec1`; no migration):**
- Backend: `app/domain/risk_register.py` (stored assessments only; `effective` = latest FINAL of the sale, as `load_facts`; `discrepancy` = the sale's latest FINAL SOURCE_ASSIGNED band ≠ latest FINAL RULE_ASSESSED band; disjunctive facets band/factor/origin/status/rule set/product/channel/FSC/effective/discrepancy; keyset paging; `summary` over the whole SG population with two separate grains: assessments, and sale events by effective band incl. unassessed sales) and `app/api/risk.py`: API-056 `GET /risk-assessments`, API-057 `GET /risk-assessments/{id}` (factors with vocabulary labels, rule-set version incl. checksum and approval status, input hash, provenance, full sale history with supersedes/superseded_by, source-vs-rule comparison, policy/sale/case links), API-058 `GET /risk-factors` (active `risk_factor` and `sbq_risk_band` code lists). Scope through sale → policy `market_code`; MY/missing → identical audited 404. `tests/test_risk.py`. `RiskAssessmentOut.supersedes_id` (added in F4) unchanged.
- Frontend: `src/features/risk/RiskWorkbenchPage.tsx` (+ tests): separation explainer; sale-grain tiles (High/Medium/Low effective, Source ≠ rule) that filter the register; assessment-population bars; factor vocabulary; URL-held filters; drawer `?assessment=` (dialog, Escape/focus) with comparison, factor table, record, history and Policy/Call Detail links. Links in: nav, Overview risk card ("Assessments →", case grain stays on the Overview), Call Detail context risk card, Policy Detail risk tab. DV-18.
- Seed facts: 229 SG assessments (74 rule-assessed, 155 source-assigned; 15 SUPERSEDED UNKNOWN), 195 SG sales (193 with a FINAL assessment, 2 unassessed), 3 conflicting sales (SALE-SG-000167 LOW→HIGH, -000168 and -000169 LOW→MEDIUM). No PROVISIONAL status, no stored score or weights, no MANUAL origin exist in the seed; the UI labels them if they appear.

## 13. CP0.4a Insurance transaction intake — ACCEPTED 2026-11-16

**As built (2026-11-16; evidence `docs/acceptance/evidence/CP0.4a/`; OpenAPI `d3aabc102cbe7a2730fbb166e0515d8284eb882e8e125b83fb9f57c39d49fcd9`; migration `0009_intake` on `call360_test` and `call360`):**
- Backend: `migrations/versions/0009_intake.py` (insert-only `intake_run`, `intake_item`, `field_change`; FK from every provenance table's `intake_item_id`; downgrade refuses once runs exist); `app/domain/intake.py` (guards, validation, conflicts, party resolution, eligibility, holds, single-transaction commit, `describe` outcome); `app/api/intake.py`: API-080 `GET /intake/sources`, API-084 `POST /intake/manual/preview` (persists only an audit event), API-085 `POST /intake/manual` (`Idempotency-Key` required; replay → 200 `replayed`; key reuse → 409), API-082/083 runs. Errors: `INGEST_VALIDATION_FAILED` (field locations and codes, never values), `INGEST_NON_SYNTHETIC_REJECTED`, `INGEST_CONTACT_NOT_SYNTHETIC`, `INGEST_MARKET_NOT_IN_SCOPE`, `INGEST_DUPLICATE_SOURCE_EVENT`, `INGEST_SALE_REF_EXISTS`, `INGEST_POLICY_FIELDS_DIFFER`, `INGEST_DUPLICATE_NEW_BUSINESS`, `IDEMPOTENCY_KEY_REQUIRED`/`_REUSED`. Audit: `INTAKE.PREVIEWED`, `INTAKE.COMMITTED`, `INTAKE.REJECTED`, `INTAKE.REPLAYED`, `CASE.HOLD_PLACED` (payload digest, references and codes only).
- Rules applied (existing only): source-assigned risk stored as supplied (no band/score calculated); every case held `AWAITING_SCRIPT_ASSIGNMENT` (no resolver); eligibility from governed `callable_party_roles` + DB check → `NO_ELIGIBLE_CONTACT` when none; ILP without risk → `RISK_TRIAGE`; `DATA_CONFLICT` not applicable to a new sale; state `VALIDATED`; owner unassigned; due date/priority source-provided (D-41). Existing-policy reuse requires all material fields to match; role changes on an existing policy are corrections (CP0.4b). Product set = the S0-SEED-1 synthetic products; SG currency SGD.
- Seed integrity: the seed content digest now covers seed-authored rows (`created_by = SYSTEM:seed`), so intake rows do not change it and any change to a seeded row still does; development digest `2ead19f3…` still matches its manifest after the demo.
- KPI-14 "Intake runs" is now measured from `intake_run` (ADMIN only); KPI-13 shows `MANUAL` by source type.
- Frontend: no intake screen (CP0.4b). Labels follow the record's source (Overview banner, Policy Detail banner, Call Detail "Synthetic intake case" banner); CP0.4 stage chips now say CP0.4b. `e2e/cp04a-checks.ts`. DV-19.
- Demo: `Call360-backend/scripts/intake_demo.py` (fresh synthetic SG references each run; preview → commit → replay; credentials from env or prompt, never printed). Development records created in the owner demo: `POL-SG-937467` with `SALE-SG-937467` → `CB-2026-10499` and top-up `SALE-SG-937468` → `CB-2026-10500` (runs IR-2026-000001/2).

### Original F2 scope (as authorised)

**Delivers (catalogue rows unchanged, all Singapore-scoped server-side):**
- **API-035 `/cases`:** the case register with search by case ref, policy ref, attempt or session ref. Filters: state, outcome category, effective risk band, overdue, hold reason, product family, ILP and due-date range. Also the dashboard `kpi` + `kpi_set` drilldown, reusing the F1 predicate functions. Sorting and cursor pagination.
- **API-036 `/cases/facets`:** counts computed after scope.
- **API-076 `/work-queues`:** due today, overdue, awaiting callback, and on hold by reason.
- **API-070/071 `/search`, `/search/suggest`:** exact, prefix and fuzzy matching on approved identifiers (case, policy, attempt and session references), plus exact-match phone or email lookup through the HMAC token (`contact_method.value_hmac`; never decrypted). Results show masked values only, and search terms are logged only as hashes.
- **Screens:**
  - `/calls` (Call Explorer) and `/queues` (Work Queues) following the mockup, with the five states and URL-held filters;
  - the top-bar search with suggestions (DV-12 lifted);
  - Dashboard cards, risk segments and priority rows link into the register.
- **Navigation to a case:** register and queue rows open `/cases/:caseId`, which is F3. Until then they show an explicit "available in F3" state rather than a dead link.

**Deferred by the owner:** saved views (API-072…075, `saved_view` table).

**Tests:**
- BE-API-01 (register and grain);
- BE-KPI-02 (drilldown set equality);
- BE-SRCH-01…06 and BE-SRCH-08 (BE-SRCH-07 is saved views, deferred);
- BE-SEC-02 and BE-SRCH-05 (no MY rows, counts, facets or suggestions);
- FE-01;
- E2E-02 (card → register count equality).
- E2E-06 (search → Policy Detail → Call Detail) completes with F3/F4.

**No new migration is expected.** The `case.read`, `queue.read` and `search.use` permissions already exist for ADMIN and USER.

Then: F3 Call Detail → F4 Policy Explorer → F5 SBQ Risk Workbench → CP0.4 intake → CP0.1B-3 → CP0.6.

## 14. CP0.4b Manual Intake portal — ACCEPTED 2026-11-16 (UI portion only)

**As built (2026-11-16; evidence `docs/acceptance/evidence/CP0.4b-UI/`; OpenAPI `9574dbb18d4bbae5a1bc1ed699420ede6c4734c430592770ab52c69606e53b5b`; no migration, head stays `0009_intake`):**

- **Backend:** API-087 `GET /api/v1/intake/reference` (`intake.read`, caller's market) in `app/api/intake.py`, schemas `IntakeReference` and options in `app/api/schemas.py`. Values come from the validator's own sources (`SYNTHETIC_PRODUCTS`, active `fsc_representative`, governed `sbq_risk_band` and `synthetic_contact_ranges`, request-model `Literal`s and the priority bounds). Tests: `test_reference_data_lists_what_the_validator_accepts`, permission inventory (6 intake routes).
- **Frontend:** `src/features/intake/` — `IntakePage` (sources, tabs), `ManualIntake` (form; preview; preview-gated submit with a kept `Idempotency-Key`), `Outcome` (server outcome and links), `IntakeHistory` (runs and run drawer), `model.ts` (payload shaping, SGT↔ISO, server `loc` → field mapping). Route `/intake` (`intake.read`); nav item enabled for ADMIN. Links: Overview "New callback case", Policy Explorer "Manual intake", Policy Detail "Add a sale" (`/intake?policy=…`).
- **Tests:** unit `model.test.ts`, `IntakePage.test.tsx`; Playwright `e2e/cp04b-checks.ts` (called from `overview.spec.ts`; journey timeout 120 s).
- **Deferred:** mock upstream and scheduling, corrections, saved drafts, Admin Integrations.

## 15. F6 Script Studio and Assignment Rules (read-only) — ACCEPTED 2026-11-16

**As built (2026-11-16; evidence `docs/acceptance/evidence/F6/`; OpenAPI `cf31afd86a5630e062cd67d9965b5d3fbf1b7e8af109b45c7ad3108018a31bb6`; no migration):**

- **Backend:** `app/api/scripts.py` — API-060 `GET /scripts` (filters: status, language, effective date, product family, risk band, channel, text; facets; product/band/channel match module *content conditions*, no case is evaluated), API-061 family, API-062 versions, API-064 rule versions with target pin and assigned cases (count plus latest 10), API-065 regulatory references, API-066 controls with in-scope question links. All `script.read`, market-scoped (rules via the target family's market). Fixes in scope: API-063 returned 500 for a DRAFT version (manifest SHA is null until frozen) and now filters regulatory references by market; `ScriptPin` and `ScriptVersionDetail` gained `script_family_id` (additive) for deep links. Tests: `tests/test_scripts.py` (8), permission inventory.
- **Frontend:** `src/features/scripts/` — `ScriptLibraryPage`, `ScriptFamilyPage` (version history, header with manifest, structure navigator, question details with expected-answer policy and controls; regulatory references visually separate), `AssignmentRulesPage` (rule registry with readable predicates, targets and case links; `?rule=` opens one), `shared.tsx`. Nav items enabled; Call Detail "Assigned script" and "Why this script" link to the version and rule. Stage S2 actions visible and disabled.
- **Tests:** unit `ScriptPages.test.tsx`; Playwright `e2e/f6-checks.ts` (both roles; journey Script Library → version → rule → Call Detail → back to the pinned version; a superseded rule's case keeps its version).
- **Not built (later stages):** editing, publishing, assignment evaluation, hold release, voice, LLM question generation, compliance decisions.

## 16. F7 Review Workbench and Voice Studio (read-only) — ACCEPTED 2026-11-16

**As built (2026-11-16; evidence `docs/acceptance/evidence/F7/`; OpenAPI `2b31989b101f4aeacdab396a742a44d3f6a20f8b3adea1a65815c2699d7f7303`; no migration):**

- **Backend:** `app/api/reviews.py` — API-077 `GET /review-queue` (`queue.read`; `queue=AWAITING_REVIEW|ALL`, `q`, `severity`, `status`, `category`, `origin`, `material`, `sort`, `limit`/`offset`; facets; materiality from the governed `finding_materiality_policy`; case SBQ band from the same facts as the case register; evidence from `evidence_refs` → `answer_observation`, `rule_evaluation`, question revision and controls). API-078 `GET /voice/preflight` (`voice.preflight.read`) lists capabilities, all `NOT_AVAILABLE`. Tests: `tests/test_reviews.py` (5), permission inventory.
- **Frontend:** `src/features/reviews/ReviewWorkbenchPage.tsx` (tiles from API counts, queue tabs, filters/sort/paging in the URL, selected-finding detail with Call Detail and Policy Detail links, S3 actions disabled), `src/features/voice/VoiceStudioPage.tsx` (status and capability table, S1 controls disabled, no media access). Nav: every Stage 0 screen now enabled. Tests: unit `ReviewWorkbench.test.tsx`; Playwright `e2e/f7-checks.ts` (both roles).
- **Not built (later stages):** finding adjudication, review decisions and maker-checker, evidence bundles, playback, voice sessions.

## 17. CP0.1B-3 Administration completion — ACCEPTED 2026-11-17

**As built (2026-11-17; evidence `docs/acceptance/evidence/CP0.1B-3/`; OpenAPI `ba7e04f87770866b5d5c80957baddff18a798fdcfc4477785f0511918a137ddc`; migration `0010_password_change_required` on `call360_test` and `call360`; dev seed digest unchanged):**

- **What was missing:** API-007, 009, 011, 013, 014…020, 026 and the Groups, Sessions and System screens (tabs were disabled "Later in Stage 0"); users could only be created by the operator CLI.
- **Backend:** `app/api/admin_access.py` (all the above); `local_credential.must_change_password` + enforcement in `app/security/authz.py` (`require()` → `403 PASSWORD_CHANGE_REQUIRED`; `/me` reports it); `create_local_account` records the reason and the Idempotency-Key digest in `ADMIN.USER_CREATED`; `AUTHENTICATED_ROUTES` adds `/auth/session` and `/me/password`. Audit actions: `ADMIN.USER_CREATED`, `ADMIN.PASSWORD_RESET`, `AUTH.PASSWORD_CHANGED`, `AUTH.PASSWORD_CHANGE_FAILED`, `ADMIN.MEMBERSHIP_ADDED`, `ADMIN.MEMBERSHIP_ENDED`, `ADMIN.GROUP_MAPPINGS_REPLACED`, `ADMIN.SESSION_REVOKED` (passwords never recorded). Tests: `tests/test_admin_access.py` (7), permission inventory.
- **Frontend:** Users (New user, Reset password, one-time password panel), `GroupsPage`, `SessionsPage`, `SystemPage`, `account/PasswordPage` (forced after a one-time password; also in the user menu), `AdminLayout` tabs. Tests: `AdminCompletion.test.tsx`; Playwright `e2e/cp01b3-checks.ts` (create → first sign-in → forced change → portal; groups; revoke; reset; system; USER denial).
- **Deferred, not blocking:** Admin Integrations (API-027) with the CP0.4b remainder; scope administration beyond the enabled market set (multi-market is a later decision, D-39); enterprise SSO (S5).

## 18. CP0.6 Integrated Stage 0 verification — technical verification ACCEPTED 2026-11-17 (governance pending)

- **Added tests only (no business functionality):** `Call360-backend/tests/test_stage0_acceptance.py` (all-route Singapore sweep and identical audited 404s, constraint/reference integrity, immutability and manifest reproduction, audit chain and secret-free audit, BE-SEC-04 injection sweep, seeded-only Malaysian audit references); `Call360-frontend/e2e/cp06-checks.ts` (one transaction through every module; seeded script and finding traceability; E2E-14 controlled empty/error/partial states). Matrix IDs added to existing tests (BE-API-04/05, BE-AUTH-10, BE-KPI-05, BE-SRCH-01/02/06, E2E-07/09/11).
- **Gate:** run twice on freshly reset `call360_test` (`evidence/CP0.6/gate_run_*.txt`); development database never reset (read-only digest and audit checks).
- **CP0.6-F1 resolved 2026-11-17:** `app/audit/scope.py` scopes the operational audit view (API-021, Administration 24 h count) to the caller's markets; out-of-scope business events hidden, access-denied events on out-of-scope records listed with the ID withheld (`scope_redacted`), seed manifest without dataset totals; ledger untouched (evidence `evidence/CP0.6-F1/`).
- **Open (governance):** SEC-008 security review (handoff `docs/security/SEC-008_REVIEW_HANDOFF.md`); approver names and signatures (C-20).

## 19. Stage 1 and S2-A slice log (historical summaries; current state is §0)

| Slice | Outcome | Migration | Record |
|---|---|---|---|
| S1-A Full-duplex browser voice POC (mock provider, WebSocket, barge-in; D-44 boundaries) | ACCEPTED 2026-11-17 after the owner's real-microphone test | `0011_voice_session_permission` | `S1.md` "S1-A", `evidence/S1-A/` |
| S1-B Session lifecycle and insert-only event ledger (resume within 30 s, sweeper, startup recovery) | ACCEPTED 2026-11-17; limitations accepted (no connection survives a restart; resume within 30 s; no audio/transcript content; synthetic-microphone demos are not real-microphone acceptance) | `0012_session_event` | `S1.md` "S1-B as built / owner acceptance", `evidence/S1-B/` |
| S1-C Consent-gated encrypted recording (two tracks, chunk manifests, coverage, `recording.read` USER only) | ACCEPTED 2026-11-17 after the owner's real-microphone test; D-45 test-only consent wording, D-46 `recording.read` USER not ADMIN, D-47 168 h local retention (development only), D-48 test sessions excluded from operational KPIs (implemented, `S0-KPI-3`) | `0013_recording` | `S1.md` "S1-C …", `evidence/S1-C/` |
| S1-D Local transcription and synchronised playback (D-49…D-53 approved with `IMPLEMENT S1-D`) | IMPLEMENTED AND VERIFIED; awaiting owner acceptance | `0014_transcript` | `S1.md` "S1-D …", `evidence/S1-D/` |
| S1-E GPT-Live | PAUSED by the owner (resume last) | — | `S1.md` |
| S2-A Editable Script Studio (D-54…D-57) | ACCEPTED 2026-11-17 (subject to S2-A.1); uncommitted | `0015_script_authoring` | `S2.md`, `evidence/S2-A/` |
| S2-A.1 Owner refinements (draft isolation, Abandon Draft, acknowledgement, labelling) | ACCEPTED 2026-11-17; uncommitted | `0016_script_draft_isolation` | `S2.md`, `evidence/S2-B/` |
| S2-B Editable Assignment Rules (D-58…D-66 approved) | ACCEPTED 2026-11-17; uncommitted | `0017_assignment_rule_authoring` | `S2.md`, `evidence/S2-B/` |
| S2-C Deterministic Script Assignment | ACCEPTED 2026-11-17; uncommitted | `0018_script_assignment_engine` | `S2.md`, `evidence/S2-C/` |
| S2-D Deterministic Question Controller + Text Simulator | ACCEPTED 2026-11-17; uncommitted | `0019_script_simulation` | `S2.md`, `evidence/S2-D/` |
| S2-D.1 Conversation Lifecycle and Control Gates | ACCEPTED 2026-11-18; uncommitted | `0020_conversation_lifecycle` | `S2.md`, `evidence/S2-D.1/` |
| S2-E Callback Simulation Workbench | IMPLEMENTED AND VERIFIED 2026-11-18; awaiting owner acceptance; uncommitted | `0021_simulation_workbench` | `S2.md`, `evidence/S2-E/` |

Earlier per-session snapshots (previously §19–§23) were removed from this handoff because their status lines and
"outstanding decisions" lists are superseded; their content is preserved in `S1.md`, `S2.md`, the evidence folders and
Git history (`git log -p docs/plans/SESSION_HANDOFF.md`).
