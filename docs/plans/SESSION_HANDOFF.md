# Call360 — Session handoff

**Last updated:** 2026-11-18, end of the S2-E session (Claude Code). **Read §0 first; it is
the only current-state section.** §1–§7 are current reference material; §8 onward are historical checkpoint records kept
for traceability.
**Process:** strict specification-driven development (workspace `CLAUDE.md` §10). Never implement without the owner's
explicit authorisation of the named checkpoint; never advance automatically; never commit, push or merge without
authorisation; never mark anything accepted without the owner's explicit words.
**Secrets:** this document contains no passwords, API keys or encryption keys. They live only in gitignored local files
(§4).

## 0. Current state — read this first (2026-11-19)

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
