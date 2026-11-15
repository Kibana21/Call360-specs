# Call360 — Three-repository architecture and delivery operating model

**Decision ID:** ADR-0001 (proposed for owner approval; topology already chosen by engineering)  
**Version:** 0.2 | **Scope:** Stages S0–S6

## 1. Architecture decision

The product is developed in **three independent Git repositories** with one local parent workspace. They do not use Git submodules, nested `.git` directories or a central monorepo. The specs repo remains authoritative for product language and business acceptance, while API implementation and frontend UI remain independently deployable.

```text
call360/                      # developer-local workspace, not committed
├── Call360-specs/           # business specs, interface policy, ADRs, evidence
├── Call360-backend/         # Python/FastAPI + Postgres + voice/survey/compliance
└── Call360-frontend/        # React SPA + browser WebRTC + typed API client
```

If Claude Code is invoked from the workspace root, it must read **all three** repo instructions and inspect `git status`, current branch and remote in each repo independently. No cross-repo commit or push may be assumed.

## 2. Responsibility boundaries

| Concern | Source of truth | Producer / implementation | Consumer |
|---|---|---|---|
| Requirements / business acceptance | `Call360-specs/docs/spec/` | S&C / product owner | Both code repos |
| Product name, routes, labels | `Call360-specs/docs/product/` | Frontend | Reviewers / E2E |
| Domain concepts & invariants | BRD + ADRs in specs | Backend | Frontend via API |
| API runtime schemas | Backend's generated OpenAPI | Backend | Frontend generated client |
| API policy and planned changes | `Call360-specs/docs/contracts/` | Backend reviews with spec owner | Frontend, QA |
| Database schema/migrations | `Call360-backend/migrations/` | Backend | Backend only |
| Approved script artifacts | DB and versioned backend script publications | Backend + approved maker/checker workflows | Voice / compliance |
| Recording and transcript provenance | Backend evidence services + storage | Backend / media channel | Frontend readonly player |
| Browser audio and UI | `Call360-frontend` | Frontend browser WebRTC | Voice backend/provider |
| Genesys telephony adapter | `Call360-backend` | Backend/media integration (S6) | Same domain contracts |
| Stage results/signoffs | `Call360-specs/docs/acceptance/` | Integrated QA and S&C owner | All repos |

## 3. Change choreography

**A. Requirement change:** create or update requirement ID and stage in `Call360-specs`, record ADR/contract proposal as necessary, open specs PR. Do not silently change business scope in implementation code.

**B. Backend change:** implement endpoint/model/business rule with migrations, auth and tests; generate `contracts/generated/openapi.json` deterministically. Commit backend PR referencing requirement IDs, specs change and compatibility impact. An additive response field is preferable to field removal or renaming.

**C. Frontend change:** update generated TypeScript API client from **backend artifact**, implement real screens, add UI and E2E coverage. Commit frontend PR referencing backend commit/contract digest, not a floating API specification.

**D. Integrated validation:** use checked out known-good commit SHA tuple, run Postgres/migrations/seed, API tests, browser integration, accessibility and Playwright end-to-end. Run OpenAPI/client drift checks; check source labels/route names and audit tests.

**E. Acceptance:** create or update `Call360-specs/docs/acceptance/Sx.md` with exact versions and evidence. Owner signs off only after all stage P0 requirements are met or documented as BLOCKED; release tags are applied independently to each repo using matching stage identifiers.

## 4. Branching and release coordination

- Suggested branches: `feature/s0-cp01-data-model` (backend), `feature/s0-cp03-call-detail` (frontend), `spec/s0-contracts` (specs). Naming may follow AIA engineering standards.
- Changes to different repos are **separate PRs**, not one PR spanning repos. Pin a backend SHA + OpenAPI checksum when preparing frontend integration.
- Tag coordinated releases such as `s0-accepted-2026-11` in each repo after approval, but record actual three SHAs in specs; same tag text does not imply identical Git objects.
- Contract changes require consumer impact review. **Additive deployment order:** backend compatible version first, frontend second. **Breaking:** explicit dual-support/versioning and migration plan; never silently break frontend or external Genesys adapter.
- Stage gate cannot pass when one repo's required PR is unmerged or integration fails. No automatic claim that local branch builds equal production readiness.

## 5. CI responsibilities

**Specs CI:** validate Markdown references, unique requirement IDs, CSV/BRD consistency, naming (“Call Detail”), stage matrix, and evidence template completeness. Add these checks in S0.

**Backend CI:** Ruff/mypy/pytest; clean Alembic migration from empty test DB; deterministic synthetic seed; OpenAPI generation determinism/diff; auth/unauthorized tests; secret/dependency scan; test provider independent of external API.

**Frontend CI:** TypeScript strict/ESLint/unit tests; accessibility checks; generated client no-drift vs pinned OpenAPI artifact; build and secret scan. Do not accept fake data in production routes.

**Integration CI or local reproducible gate:** clone/checkout exact three SHAs, start Postgres & FastAPI and Vite/static frontend, run real-backend Playwright, verify KPI-to-case drilldown, Call Detail history, idempotency and explicit evidence states. Store logs/reports/contract checksum and environment in specs acceptance.

## 6. Stage implementation ownership

| Stage | Specs | Backend | Frontend |
|---|---|---|---|
| S0 | BRD/ADRs/contracts/test matrix | Domain schema, initial endpoints, real data seed, auth | Polished navigation, Overview, Call Explorer, **Call Detail**, surveys read-only |
| S1 | Recording/session acceptance | Secure voice session, sideband, media events/manifests | Browser mic/WebRTC, streaming transcript, playback/error UI |
| S2 | Script governance criteria | Versioned scripts, state machine, approval, controlled audio mode | Script Studio, simulator, question progress |
| S3 | Compliance/review criteria | Answer schemas, rules, findings, review audit, exports | Evidence player, Review Workbench, structured output view |
| S4 | KPI/operations definitions | Intake, queue/campaign/jobs/metrics/monitor streams | Live Monitor, dashboards, campaigns and analytics |
| S5 | Security/privacy approvals | Entra, ABAC, retention, evaluated models | Permission-driven UI, protected evidence/export UX |
| S6 | Genesys acceptance/ADR | Genesys Audio Connector media adapter, call events | Minimal additional UI; existing **Call Detail** remains |

## 7. Minimal Stage 0 integrated test trace

A seeded case with 3 contact attempts (no answer → busy → connected) must appear as **one case** in Overview and Call Explorer, with **three attempts** and the single linked session in **Call Detail**. Refresh and deep links must work. API authorization must deny cross-scope access; the detail page must show unavailable recording as `NOT_AVAILABLE`, not silently present a fake recording. The test records the exact SHA tuple and OpenAPI digest. Repeat on a newly created database.

## 8. Guardrails and unresolved decisions

- Confirm company-hosted Git, CI runners, security controls and branch protection; this plan is an engineering proposal, not evidence of AIA authorization.
- No real policyholder information, call audio or secrets in repositories, AI assistant context, screenshots or test fixtures.
- No production launch or real outbound dialing without AIA Legal/Privacy/S&C/InfoSec approval and Genesys licensing/configuration verification.
- The canonical OpenAPI producer is backend; the specs repository should **not** maintain a competing hand-edited copy of executable schemas.
- If a repo is missing locally or inaccessible, log the blockage; do not silently create a substitute repository with the same name.

## 9. Local development mode (owner decision, CP0.0, 2026-11-15)

During local development, the owner has suspended §4 (branching and release coordination) and §5 (CI responsibilities) as **mechanisms**. Their **checks are not suspended**:

- No GitHub Actions, CI/CD, PR workflows, branch protection, GitHub App credentials or cross-repository automation are created.
- Every check listed in §5 runs as a documented local command, and the captured output is the evidence. This covers specs validation, lint and types, tests, migration from empty, seed determinism, OpenAPI determinism and drift, generated-client parity, secret scanning and security suites. See ADR-0003 §5 and `docs/plans/S0_IMPLEMENTATION_PLAN.md` §4.
- Commits, pushes, merges and branches happen only on explicit owner authorisation. Without commits, evidence records the base SHA plus a deterministic file manifest (ADR-0003 §6). §3 step E and §7 "SHA tuple" are read accordingly.
- The parent workspace directory's name and capitalisation (`call360/` in §1, `Call360/` on disk) are not significant, because it is not a repository.
- When company-hosted Git and CI are confirmed (§8), these local commands become the CI jobs unchanged.
