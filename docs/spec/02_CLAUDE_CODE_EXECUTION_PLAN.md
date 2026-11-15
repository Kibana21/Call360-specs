# Claude Code Execution Plan — Call360

**Companion to:** `01_MASTER_BRD.md`  
**Version:** 0.3 (v0.3 staging overlay in §B0; CP0.0 overlay below) | **Date:** 15 November 2026  
**Intent:** Use this as a stage-gated build contract for Claude Code. Do not paste the entire BRD as an instruction to implement everything at once.

> **CP0.0 overlay (2026-11-15, pending owner acceptance):** Stage 0 checkpoints, their numbering (CP0.0–CP0.6), deliverables and acceptance are defined in `docs/plans/S0_IMPLEMENTATION_PLAN.md`, which supersedes the S0 checkpoint names in §C and §B0. The mapping is in that plan, §5 (C-28). Architecture defaults in §A2 are confirmed or refined by ADR-0003…0008. "Survey Library"/`/api/v1/surveys` wording below is retained unchanged under exception EXC-001; the UI module is **Script Studio** (ADR-0007). In local development, CI/PR items (§A1.8, §A4.3, §A4.8, §F) are performed as local commands with captured output (MULTI_REPO_ARCHITECTURE §9). No requirement is changed by this overlay.

---

# A. Working agreement for Claude Code

## A1. Mandatory approach

1. Read `01_MASTER_BRD.md`, the relevant stage specification below, and existing repo state before changing files.
2. Output a plan, route map/API contracts, DB migrations and test scenarios **before coding** for each stage. Flag contradictions and explicitly name any proposed deviation.
3. Build vertical, testable slices with real UI → API → Postgres persistence → event/audit history. Do **not** wire buttons to fake timeouts or hard-coded JSON in production routes.
4. Preserve architecture: domain objects are transport-agnostic; browser Live is a channel adapter; later Genesys is a new adapter.
5. Use a separate `mock voice provider` to run CI without network/model credentials; never store production customer data in repository or test fixtures.
6. All P0 requirements in the current stage require test cases with traceable IDs. If blocked, mark `BLOCKED` and state how/why; never quietly degrade.
7. Validate everything locally: migration from clean DB, seed, backend tests, frontend tests, Playwright with real backend, no TypeScript/Python lint/type errors, no secrets.
8. Commit stage checkpoints on feature branches, record acceptance evidence in `docs/acceptance/Sx.md` and obtain owner approval before the next stage.
9. Do not fabricate regulatory requirements, approved AIA script wording, provider capabilities, recording completeness or AI confidence scores.
10. Favor readable, testable code over a complicated agent framework. LangGraph, Pipecat, Asterisk, LiveKit and a new distributed event bus are not prerequisites for S0/S1.

## A2. Architecture defaults (editable only via ADR)

| Concern | Default |
|---|---|
| Repository topology | Three sibling Git repos: `Call360-specs` (specs/contracts/stage gates), `Call360-backend` (FastAPI/Postgres/voice/surveys), `Call360-frontend` (React/Voice Studio/Call Detail) |
| Frontend | React + TypeScript + Vite; React Router; TanStack Query; accessible UI components; theme tokens |
| Styling | Tailwind / chosen component library with cohesive token system; no claim of official AIA brand assets |
| Backend | Python 3.12+; FastAPI + Pydantic v2; SQLAlchemy 2 + Alembic |
| Database | PostgreSQL from S0; local Docker Compose or existing local Postgres, separate test database |
| Blob abstraction | `ObjectStore` interface; filesystem in synthetic local dev, private Azure Blob later |
| Provider | `VoiceProvider` protocol, `MockVoiceProvider`, `GPTLiveBrowserProvider`, future `GenesysMediaAdapter` |
| Client audio | Browser WebRTC primary session; backend sideband for tool execution/events/evidence where applicable |
| Streaming UI | SSE or WebSocket from FastAPI event stream (one design decision); persist first, fan out second |
| Data models | Explicit Case/Attempt/Session/SurveyRun/Answer/RuleEvaluation/Review/Event boundaries |
| Task processing | Simple in-process for S0, durable background jobs (TaskIQ + Redis or equivalent) once S4 warrants them |
| Code quality | Ruff + mypy strictish backend, TS strict, ESLint, pytest, Playwright, OpenAPI type sync |
| Security | Signed/authenticated local demo users; real Entra/SSO only after enterprise design; no open unauthenticated media URL |

**ADR topics to record:** staging and source of truth, audio recording fidelity and provenance, exact script playback, event stream architecture, evidence integrity, model/provider abstraction, authentication, finalization, retention, Genesys media bridge.

## A3. Three-repository workspace — required structure

The *local workspace* contains three independently versioned repositories. Do not turn it into a monorepo or commit one Git repository inside another.

```text
call360/                              # Local workspace; NOT a Git repo
├── Call360-specs/                   # Git repo A — authoritative product contract
│   ├── CLAUDE.md
│   ├── README.md
│   └── docs/
│       ├── spec/
│       │   ├── 01_MASTER_BRD.md
│       │   ├── 02_CLAUDE_CODE_EXECUTION_PLAN.md
│       │   └── 03_REQUIREMENTS_REGISTER.csv
│       ├── product/SCREEN_NAMING_AND_ROUTES.md
│       ├── engineering/MULTI_REPO_ARCHITECTURE.md
│       ├── contracts/API_CONTRACT_POLICY.md
│       ├── adr/
│       └── acceptance/
├── Call360-backend/                 # Git repo B — executable business rules and APIs
│   ├── CLAUDE.md
│   ├── app/{api,domain,services,voice,compliance,storage,security}/
│   ├── migrations/
│   ├── surveys/
│   ├── tests/
│   └── contracts/generated/openapi.json
└── Call360-frontend/                # Git repo C — browser UI and client
    ├── CLAUDE.md
    ├── src/{app,features,components,api/generated}/
    ├── tests/
    └── e2e/
```

Only `Call360-specs` receives the master BRD. Each of the other repositories gets its **own** `CLAUDE.md` from the distribution pack. These files point back to sibling specs, and do not duplicate the BRD.

## A4. Contract and change-management guardrails

1. `Call360-specs` owns product vocabulary, approved interaction flows, domain definitions, acceptance criteria, and contract *policy*; specs PR precedes scope change.
2. `Call360-backend` owns the **executable OpenAPI** definition. Generate and check in a deterministic `contracts/generated/openapi.json` artifact (or equivalent documented CI artifact). Version additive and breaking changes explicitly; do not manually maintain divergent schemas.
3. `Call360-frontend` generates its client from the checked-in/published backend OpenAPI artifact. Regeneration and no-drift checks belong in CI.
4. Cross-repo feature sequence: specs/ADR → backend endpoint + tests + OpenAPI → frontend typed integration + UI tests → integrated Playwright → stage evidence in specs.
5. Stage acceptance evidence includes exact three repo commit SHA values, contract checksum, migration revision, test commands, reports, open decisions, and owner signoff. An unmerged branch in one repo is not stage acceptance.
6. No direct DB access from the frontend. Auth, scope and idempotency are enforced in backend APIs. No frontend-only business/compliance verdicts.
7. Keep an API backwards-compatibility window and staged deploy order: backend first for additive changes, frontend second. Breaking changes require migration/dual-support plan and explicit approval.
8. Use separate PRs and CI per repo; a locally orchestrated integrated gate is required before signing off S0 and every subsequent stage.

---

# B. UI design brief — brilliant but suitable for Compliance

**Design goal:** Modern, precise, reassuring. The platform should look like an enterprise-grade financial operations product, not a toy chatbot or a generic admin scaffold. Use a restrained palette, generous spacing, thoughtful motion, strong typography and information density controls. Implement both light and dark themes if resources permit, but prioritize one polished theme with accessible contrast and tested behavior. AIA logos and copyrighted brand assets require authorization and must not be invented as official materials.

**Navigational model:**
- Persistent slim left rail with icon + label (collapsible) and global search.
- Top contextual toolbar with environment badge, user/role, search and time filters.
- Content uses modular panels with quiet visual boundaries; no overcrowded 4-column control rooms.
- Clear hierarchy: insight → action → evidence, with a keyboard-accessible breadcrumb back to prior filtered worklist.
- One-click drill-down everywhere. Alert colors only for materially meaningful states.
- Provide progress skeletons, partial-data badges, understandable empty states, failure messages, and small inline help for KPI definitions.

**S0 high-quality UI screens (real data-driven):**
1. **Overview**: KPI strip (callback due, attempted, verified, review pending, critical, SLA breach), 7/30-day trend, compliance disposition breakdown, queue pulse, latest cases, data quality alert list.
2. **Call Explorer**: powerful server-backed table with sortable/filterable columns, search, quick filter chips, saved view stub if not implemented, export button disabled with explanation until implemented; rows open case detail.
3. **Call Detail**: case header, all attempts, transcript player placeholder with explicit `NOT_AVAILABLE` media state, survey question status, JSON result panel, rule findings, audit/event timeline; all sections rendered from DB and linked.
4. **Survey Library**: list of seeded draft/published synthetic surveys with version/status, version detail read-only; Draft editing arrives in S2.
5. **Queues**: review and operational exception table seeded for synthetic demo, working drill-down and assignment concept.
6. **Administration**: demo role/scope display, system health endpoints, synthetic-data banner.
7. **Browser Voice Studio**: attractive preflight screen and disabled/provider-missing state in S0, functioning in S1.

**One-screen success story:** From an Overview card `High-risk callbacks (6)` → click → Call Explorer filtered to 6 → click `CB-DEMO-042` → see 2 attempts → select attempt 2 → play recording (once S1 populated) → select flagged premium term → transcript jumps to 01:34 → see extracted 5 vs policy snapshot 10 → open finding and reviewer trail. **Even at S0, the pre-S1 path must render explicit unavailable artifacts rather than pretending they exist.**

**S0 demo dataset:** at least 250 synthetic cases, 400+ attempts, 80+ completed sample sessions, 4+ survey versions (including retired and draft), 20+ findings, partial/incomplete media examples, diverse outcomes, retry cases, pending reviews, and multiple products/languages clearly marked fictional. Make seed repeatable, predictable and generated without personal data. Dates should cluster around a seed-relative anchor for meaningful trends, using one shared report time zone.

---


## B0. v0.3 staging overlay — authoritative expansion (237 requirements)

This supplement is binding when implementing the original stages below. The expanded business process and security/grain documents are **required reading**, not optional references. Existing stage gates remain binding; this section adds non-negotiable cases.

| Stage | Additions to deliver / prove |
|---|---|
| **S0** | Real locally authenticated UI and backend with synthetic `party`, `policy`, `policy_party_role`, `sale_event`, `risk_assessment`, `callback_case` records; mocked internal API + authorized manual intake; Policy Detail/Sale Detail, risk breakdown and search; permission-protected ADMIN/USER management; actor-attributed audit. No hard-coded/shared credentials. |
| **S1** | Voice session binds to precise sale/case, contact party, frozen policy fact snapshot and provisional/approved script reference. Recording/transcript status explicit. |
| **S2** | Governed modular script/question/expected-answer lifecycle; callback selection risk and investment suitability risk distinct; effective-dated assignment rules across market, ILP/product, SBQ risk, selling channel, contact role/language; no ambiguous fallback; source and change provenance. |
| **S3** | Typed answer observation and free text together; compare against correct policy fact snapshot; risk findings distinct from SBQ selection risk; reviewer can see why script/question chosen. |
| **S4** | Authoritative internal API adapter, incremental sync, bulk/replay, source reconciliations, role/party updates and search indexing/operational SLAs. Browser-first pilot remains possible without outbound telephony. |
| **S5** | Okta/Microsoft Entra OIDC federation and immutable group-ID mapping; test refresh-token replay, access revocation, BOLA, CSRF/XSS, encryption, audit integrity, retention and independent penetration review. No security guarantee is possible. |
| **S6** | Genesys consumes same case/contact/selected-script model and uses its own bidirectional audio transport; outbound contact permission and attempt traceability required. |

**S0 checkpoints (extended):** (1) identity/security skeleton + DB/migrations, (2) synthetic policy-sale-party records, (3) SBQ risk inputs, risk/source history and sale/case drill-down, (4) mock API/manual intake with validation and idempotence, (5) global secured search/filtering, (6) premium UI integrated with actual backend, (7) integration/authorization/audit testing and cross-repo acceptance. Later-stage workflow actions must be disabled with a clear planned-stage state, never implemented as inert fake buttons.

**S0 acceptance additions:** login/logout + failed-login throttling; role-based backend authorization and actor audit; searching and opening a policy shows eligible contact, selling context, SBQ risk/rationale, assigned or pending script and linked callback cases; idempotent synthetic mock import; authorized manual corrections preserve source history; wrong-ID and cross-scope access are denied. Security claims may be made only for controls actually tested.

**Test coverage:** original T-01 to T-30 plus new T-31 to T-55 in the master BRD. New test applicability is stage-dependent; no stage gets unconditional approval solely from UI demonstration.

# C. Stage implementation briefs

## STAGE 0 — Product foundation + full UI/back-end skeleton

### Scope and sequence
- **CP0.1 Contracts & schema:** Define state machines and database with migrations, constraints, seed data and consistent IDs. Build authentication scaffolding and fake local roles. Record ADRs. Use test DB.
- **CP0.2 API vertical slices:** Create all-cases search, case detail, attempt/session hierarchy, survey read APIs, dashboard aggregates and timeline/audit views. Derive dashboard metrics with tested SQL definitions; no counting attempts as cases.
- **CP0.3 Premium UI:** Build app shell, overview, explorer, Call Detail, Policy/Sale Detail, SBQ risk view, script library, global search, login and queues. Client code generated from OpenAPI. Design with synthetic visual richness and human-readable statuses.
- **CP0.4 E2E & polish:** Playwright executes navigation and core drilldown against running backend/DB; loading/error/empty/access states; responsive layout; keyboard and contrast check; docs.

### Suggested API slices
`GET /api/v1/dashboard/summary`, `GET /api/v1/cases`, `GET /api/v1/cases/{id}`, `GET /api/v1/cases/{id}/timeline`, `GET /api/v1/cases/{id}/attempts`, `GET /api/v1/sessions/{id}`, `GET /api/v1/surveys`, `GET /api/v1/surveys/{id}/versions`, `GET /api/v1/review-queue`, `GET /health/live`, `GET /health/ready`.

### S0 acceptance
- `S0-A1`: Reproducible one-command environment setup + seed and reset.
- `S0-A2`: Real Postgres, migrations and realistic demo records across all lifecycle states.
- `S0-A3`: Every KPI reconciles to list filtering; aggregate denominator unit tests.
- `S0-A4`: Call Detail shows all attempts, linked session, survey version, sample response and findings.
- `S0-A5`: 10+ Playwright paths: overview/drilldown/search/sort/pagination/session detail/survey detail/role restriction/empty/failure.
- `S0-A6`: No fake functional controls; unfinished actions are disabled with tooltip or hidden.
- `S0-A7`: Screens look coherent at 1440px and 1280px; no clipped text, awkward scroll traps or tiny control hit targets.
- `S0-A8`: All P0 APP/CASE/GOV foundation requirements traceable.

**Do not implement live voice before S0 gate passes.**

## STAGE 1 — Full-duplex browser voice + evidence capture

### Scope and sequence
- **CP1.1 Session security & connection:** Implement server-created GPT-Live browser session and private sideband/control as permitted by selected API. Confirm API contract from current docs. Browser only gets an authorized SDP response or appropriately scoped ephemeral credential, never raw server key. Provide mock provider and UI.
- **CP1.2 Audio UX:** Start/stop, mic permission, speaker, mute, speaking/listening status, stable interruption handling, session timed state, human readable connection error.
- **CP1.3 Event capture:** Capture client and sideband session lifecycle and transcript events; source event IDs and dedupe; persist before streaming to frontend; session finalizer and fallible states.
- **CP1.4 Recording & provenance:** Implement consent-gated local test recorder that captures both microphone and remote playback, if permitted by browser/track APIs, with chunk upload, manifest, hash, status and partial failures. Explicitly report track capture limitations, clipping, interruption and missing coverage. Do not equate generated audio with played audio. Store model session metadata.
- **CP1.5 Call Detail integration:** Start creates synthetic CallbackCase / ContactAttempt / ConversationSession in DB, visible in active list and later in Call Explorer. Transcript and media player appear on detail; event timeline shows start/stop/interruption/network/finalization.
- **CP1.6 Regression:** Full-duplex manual and automated tests with noise/silence, remote audio playback, interrupted speech, browser refresh and model outage. Guard no-key CI via mock provider.

### Recording engineering constraints
- Browser WebRTC media track may not be identical to the audio ultimately heard; `MediaRecorder`, Web Audio mixing, stream discontinuity and codec support vary by browser/device.
- Store independent track provenance (mic, remote), capture boundaries and manifest. Avoid asserting forensic-grade chain of custody in S1.
- If compliant recording of both tracks fails, mark `CAPTURE_FAILED`, do not manufacture a complete recording, and block final verified outcome under the configured evidence rule.
- Sideband reflected model audio is not definitive played audio: preserve distinction between model output, browser receipt and browser playback telemetry.
- `gpt-live-transcribe` alone does not provide native word timestamps, diarization or confidence. Align transcript events using application timeline with precision markers; improve transcription/reconciliation later.

### S1 acceptance
- `S1-A1`: Browser voice works with natural turn-taking and interruption.
- `S1-A2`: API master key absent from browser and frontend assets.
- `S1-A3`: Every initiated browser session maps to exactly one case/attempt/session group.
- `S1-A4`: Call Detail shows live/final transcript with uncertainty, playable available recording, status and event sequence.
- `S1-A5`: Network failure/stop or upload failure yields incomplete/unavailable evidence and no verified outcome.
- `S1-A6`: Sideband replay and duplicated events do not duplicate tool/business action.
- `S1-A7`: Local tests work without provider key via mock; real provider path documented and manual test evidence recorded.

## STAGE 2 — Survey configuration + constrained voice orchestration

### Scope and sequence
- Build visual survey builder, JSON contract and Pydantic validation; versioned `DRAFT → SUBMITTED → APPROVED → PUBLISHED` transitions with maker-checker.
- Add question types: yes/no/unclear/refused, numeric term, open narrative, scaled response, confirmation, identity, disclosure and read-only policy facts. Support branching, repeats, skip-if (only approved), start/finish and abort.
- Implement backend question state machine with explicit question execution events; Live runtime calls `get_next_permitted_action()` and `submit_customer_answer()` only through authorized backend. Client cannot directly change survey status.
- Implement approved speech modes: `CONVERSATIONAL` for ordinary dialogue; `CONTROLLED_TTS` or `EXACT_AUDIO` for verbatim mandated lines; detect and flag delivery interruption. Do not assume prompt adherence is proof of exact speech.
- Add simulation workbench for synthetic persona testing, approval matrix and published SHA-256 manifest.

### S2 acceptance
- `S2-A1`: Maker can create and validate draft, checker publishes; self-approval denied and audited.
- `S2-A2`: Old call pinned to published version even after later publish.
- `S2-A3`: Every required question has explicit requested/delivered/answered/completed states.
- `S2-A4`: Customer interruption, unclear/refusal, multi-question utterance cannot skip mandatory gates.
- `S2-A5`: High-risk mandatory language is delivered by controlled mode or system explicitly blocks production use.
- `S2-A6`: Question controller is unit-testable without the LLM.

## STAGE 3 — Structured compliance evaluation + human review

### Scope and sequence
- Schema-constrained structured extraction from transcript or provider event; preserve original utterance, model version, extraction state and the schema validation result.
- Deterministic compliance rules compare customer response to immutable policy snapshot; include `PASS`, `FAIL`, `UNCLEAR`, `NOT_ASKED`, `NOT_APPLICABLE`, evidence `MISSING` statuses.
- Material findings and contradiction flags with risk/priority, review queue, assignment, reviewer decisions, two-person approval when applicable, audit history.
- Call Detail synchronized transcript/audio clickthrough; question-by-question evidence, typed output, policies and reasons. Export controlled evidence bundle with media, JSON and checksums.
- Decision manager separates survey completed, evidence complete, compliance verified and case closed.

### S3 acceptance
- `S3-A1`: Wrong term example 5 vs 10 fails and cannot be verified.
- `S3-A2`: `UNKNOWN`, silence, refusal and technical failure never count as PASS.
- `S3-A3`: Reviewer can jump directly to evidence; missing asset leads explicit warning.
- `S3-A4`: AI evaluation, deterministic rule and human review stored independently.
- `S3-A5`: Protected finding disposition requires distinct maker/checker; original retained.
- `S3-A6`: Event replay reconstructs final compliance decision and its rule versions.

## STAGE 4 — Campaign, all-call operations, monitoring & analytics

### Scope and sequence
- Implement secure batch/API case intake, schema check, customer suppression and idempotent dedupe. Provide campaign records, cohorts and product-specific script version assignment.
- Work queues, owners, reminders, callback schedules, escalation clocks, retry limits and terminal disposition. For browser-only pilot, operators start scheduled synthetic sessions; real outbound dialer waits until S6.
- Live Monitor shows active browser sessions and provider state with real session event stream; delayed/failing/stuck sessions and recording finalization queues.
- Analytics: coverage, connection, attempts per case, complete vs verified, refusal, material findings, age, SLA and playback/transcript integrity; metric drill-down and daily reconciliation.
- Durable async jobs for finalization, post-call evaluation, exports and notifications, with retry policies/dead-letter/alerting and dedupe. Choose job framework only after load/operational needs are clear.

### S4 acceptance
- `S4-A1`: Validated intake creates unique cases; repeated import safe.
- `S4-A2`: All attempts remain in Call Detail and global reports, including no-answer attempts.
- `S4-A3`: Live status and stale heartbeat handled accurately.
- `S4-A4`: Daily KPI SQL reconcilable to case IDs, no double counting across attempts.
- `S4-A5`: Failed async operations surface in work queues with retry and alert, no silent loss.

## STAGE 5 — Enterprise authorization, privacy and readiness

### Scope and sequence
- Entra SSO, least privilege and market/product ABAC; separate access permissions for audio, case content, export, consent override and approval. Access-events audited.
- Azure-approved production storage, private objects, encryption, Key Vault, secure config and purpose-limited data paths; retention/legal hold and approved purge workflow.
- Model eval and golden suites with quality gates, fairness/accessibility and multilingual risk tests; drift and false-negative tracking. Document potential use of AI personal data under current legal and privacy advice.
- CI/CD gates, infrastructure-as-code, security scan, threat model, DR and backup verification, observability, rate limit/load tests, incident playbooks and approvals.

### S5 acceptance
- `S5-A1`: Cross-market/role unauthorized audio/API access denied and logged.
- `S5-A2`: No uncontrolled model provider/customer data processing.
- `S5-A3`: Legal hold prevents deletion; retention and export trail is verifiable.
- `S5-A4`: Recovery rehearsed from backups with evidence checksum reconciliation.
- `S5-A5`: Failed critical eval disallows model/script promotion.
- `S5-A6`: Formal owner signoffs and launch checklist complete.

## STAGE 6 — Genesys Cloud outbound and audio adapter

### Prerequisite decisions
- Confirm existing AIA product: **Genesys Cloud CX vs Genesys Engage**; org entitlement, Audio Connector availability and related commercial/licensing/configuration limits.
- Validate audio codecs, Audio Connector WebSocket protocol, latency budgets, authentication/mTLS/headers, customer data transfer, call-routing, DTMF, call recording ownership and telephone recording consent/notice obligations.

### Scope and sequence
- A separate Genesys server-side media adapter bridges bidirectional WebSocket telephony audio to the chosen voice runtime. No browser WebRTC reuse assumption.
- Genesys outbound campaigns/Architect route into bot, pass correlation IDs, answer-machine/no-answer events, handoff requests and output statuses. Prefer provider-sourced call IDs and event reconciliation.
- Preserve backend survey API, approved script artifacts, answer schema, compliance rules and Call Detail; add telephony recording and audio integrity policies.
- Controlled human transfer using Genesys-supported routing. Browser handoff is a simulated escalation, not a real telephone transfer.
- Test duplicate callbacks, failed transfer, simultaneous sessions, disconnections, delayed provider events and reconciliation with Genesys call disposition.

### S6 acceptance
- `S6-A1`: Real sandbox outbound flow completes with bidirectional speech and interruptions.
- `S6-A2`: No changes necessary to domain survey rules/validation for transport change.
- `S6-A3`: Genesys call IDs link to existing case/attempt/session and recording correctly.
- `S6-A4`: Transfer to human, refusal, no-answer and reconnect map to distinct case outcomes.
- `S6-A5`: Regulatory/operational call retention and media provenance reviewed and approved.

---

# D. Commands and test entrypoints (per repository)

Do **not** invent a top-level root Makefile across all three repos. Each repo has its own repeatable commands; a workspace integration script may orchestrate all three without owning their code.

**`Call360-backend`**: `make setup`, `make db-up`, `make migrate`, `make seed`, `make dev`, `make test`, `make lint`, `make typecheck`, `make openapi`, `make contract-check`. The actual Makefile/scripts must implement and document these before claiming they work.

**`Call360-frontend`**: `npm install`, `npm run dev`, `npm run build`, `npm run lint`, `npm run typecheck`, `npm run test`, `npm run api:generate`, `npm run api:check`, `npm run e2e`. Add scripts with correct implementation, not placeholders.

**`Call360-specs`**: `python scripts/validate_specs.py` (to be added in S0) checks requirement IDs/counts, terminology, traceability and CSV/BRD agreement; docs/acceptance carries integrated results. Do not depend on runtime secrets.

**Workspace integration gate**: run local Postgres/test DB + backend + frontend in separate processes and execute Playwright against real API, without live provider credentials. Publish exact backend/frontend/specs SHA tuple and the OpenAPI SHA-256. `make reset-demo` only if verified to operate on synthetic local/test data; never on prod.

---

# E. Stage-by-stage prompts to issue to Claude Code

## Prompt 1 — Plan a three-repository S0 delivery

> We are building **Call360** across three sibling Git repositories: `Call360-specs`, `Call360-backend`, and `Call360-frontend`. First read `Call360-specs/CLAUDE.md`, `Call360-specs/docs/spec/01_MASTER_BRD.md`, `Call360-specs/docs/spec/02_CLAUDE_CODE_EXECUTION_PLAN.md`, `Call360-specs/docs/engineering/MULTI_REPO_ARCHITECTURE.md`, and the corresponding backend/frontend `CLAUDE.md` files. Do **Stage 0 only**. The product is **Call360**; the investigation screen is **Call Detail** at `/cases/:caseId`. Produce (a) ADRs and domain schema, (b) FastAPI endpoints and OpenAPI ownership strategy, (c) UI sitemap and design system, (d) cross-repo CP0.1–CP0.4 checkpoints, (e) requirement-to-test coverage, and (f) a reproducible integrated gate with exact repo commit SHAs. Document artifacts/acceptance in `Call360-specs`, implement API/DB in backend and UI in frontend. Do not create a monorepo, do not implement Stage 1, and do not use real customer data. First present the plan, then implement checkpoint by checkpoint and record test evidence.

## Prompt 2 — Polish Stage 0 UI without changing business scope

> Using all three sibling repos and Stage 0 acceptance criteria, make the **Overview, Call Explorer, and Call Detail** screens enterprise-grade and fully operational with a real FastAPI/PostgreSQL backend. The Call Detail view is case-centric, shows every contact attempt and session, and preserves source filters. Seed >=250 deterministic synthetic cases with full scenario coverage. Use typed generated API client; no hard-coded KPI counters or fake actions. Verify keyboard accessibility, responsive desktop layout, error/empty/permission states and Playwright integrated E2E. Record coordinated repo SHAs and evidence in `Call360-specs/docs/acceptance/S0.md`. Stay in Stage 0.

## Prompt 3 — Stage 1 browser voice + evidence

> Implement **Stage 1 only** in the backend and frontend repos, consulting the specs. Use currently documented GPT-Live browser WebRTC and authorized backend sideband patterns (verify the current API before coding). Provider secrets remain server-side. Start creates or associates a synthetic case, attempt and conversation session. Support mic permission, continuous listening, interruption, mute/end, transcript, recording states, event dedupe, gaps, failures and honest recording provenance. Use `MockVoiceProvider` for CI without an API key; do not claim server output proves audio heard. Surface all results in **Call Detail**. Commit API artifact/version and regenerate the frontend client. Sign off only after cross-repo gate.

## Prompt 4 — Stage 2 survey governance

> Implement **Stage 2 only**. Create survey drafts, validators, simulator, maker-checker approval/publish, immutable pinned script versions, and backend-owned deterministic question progression. The voice model cannot independently mark required questions complete or speak invented mandatory disclosures; exact approved wording uses controlled playback with interruption-aware delivery records. Run negative tests for refusal, ambiguity, off-script attempts, interruptions and skipped questions. Show question evidence within **Call Detail**. Preserve cross-repo contract/test coordination.

## Prompt 5 — Stage 3 compliance and review

> Implement **Stage 3 only**. Add typed answer extraction, evidence pointers, policy snapshot comparisons, deterministic rules, immutable evaluations, findings, reviewer workflow, maker-checker and controlled addenda. An extracted answer is not a compliance determination. Wrong premium term, uncertain response, missing required media, failed identity or unresolved material finding cannot produce VERIFIED. Implement synchronized recording/transcript in **Call Detail** and evidence package export with checksums. Add integrated negative tests, signed-off requirements and repo SHA evidence.

## Prompt 6 — Stages 4, 5, 6 (one stage per invocation)

> Before each stage, read accepted previous-stage evidence in `Call360-specs`, propose schema/API/contract diffs and risks, then implement **only the requested stage**. S4 = intake/campaign/retry/work queues/live monitoring/analytics; S5 = authorization/privacy/evaluation/production controls; S6 = Genesys only after product/Audio Connector entitlement validation. Each stage must preserve backend survey and compliance logic, **Call Detail** history, and independent Git repositories. Never combine stages or declare PASS without recorded integrated evidence.

---

# F. PR and review checklist

- [ ] Stage/requirement IDs on ticket and PR
- [ ] Migration forward and rollback documented
- [ ] API and generated frontend types consistent
- [ ] Domain state transitions and edge cases covered
- [ ] Permission tests cover unauthorized access
- [ ] UI real and interactive; no fake controls
- [ ] Synthetic data only in tests and screenshots
- [ ] Every call outcome links to an evidence/evaluation trail
- [ ] Recorded/transcript gaps shown honestly
- [ ] No hardcoded model, script or compliance decision in frontend
- [ ] No secret or unredacted private data in logs/screenshots
- [ ] Unit/integration/e2e tests pass; exact commands logged
- [ ] S&C product owner accepts stage gate, open decisions listed

---

# G. No-go triggers

Stop and notify owner if any of the following is observed: a secret enters the browser or repo; any fake compliance pass; a mandatory question bypass; recording without approved gate; real customer data reaches an unapproved model/provider; unverifiable media is presented as complete; raw evidence overwritten; unauthorized audio access; maker approving own controlled change; unknown provider action presented as completed; or use of production Genesys routing without sandbox approval.

**Next action:** Install the updated pack into the existing three sibling repositories, commit `Call360-specs` documentation first, then ask Claude Code to run Prompt 1 from the workspace directory. Do not build S0–S6 in one run.
