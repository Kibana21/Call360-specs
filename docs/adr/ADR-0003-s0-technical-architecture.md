# ADR-0003: S0 technical architecture and local verification

**Status:** Proposed (CP0.0), 2026-11-15 · **Scope:** S0, and the default for later stages unless amended
**Related:** ADR-0001 (three repositories), execution plan §A2, §D; workspace `CLAUDE.md` §10

## Context

The execution plan §A2 lists architecture defaults "editable only via ADR". The owner has approved:
- the stack: FastAPI/Python/Pydantic, PostgreSQL, React/TypeScript/Vite;
- local development on macOS with three independent repositories;
- no GitHub Actions, CI orchestration or PR workflows during local development.

Stage 0 must still be production-oriented. Real policy data, Okta/AD identity (S5) and Genesys (S6) have to fit later without redesign.

## Decision

### 1. Stack

| Concern | Decision |
|---|---|
| Backend runtime | Python 3.12, FastAPI, Pydantic v2 (request models use `extra="forbid"`), SQLAlchemy 2.x, Alembic, psycopg 3 |
| Database | The owner's existing local PostgreSQL 15 database **`Call360_db`** is used for everything (D-16, amended by D-22). Application tables live in schema `call360`; automated tests use schema `call360_test`, reset only by guarded test commands. Extensions: `pgcrypto`, `pg_trgm`. Detail: S0_IDENTITY_ACCESS_DESIGN §10 |
| DB login | The owner's existing role **`Call360_db_user`** is used for development migrations, seed and the running app (D-16). Automated tests use a separate least-privilege role `call360_test_user`, confined to `call360_test`, with separate `.env.test` configuration (D-22). The connection string lives only in the gitignored `.env` as `DATABASE_URL=postgresql+psycopg://Call360_db_user:<password>@localhost:5432/Call360_db`; the password is never written into specs, code, fixtures or logs. The names are mixed-case, so raw SQL must double-quote them (`"Call360_db"`). No other roles or databases are created |
| Frontend | React 18 + TypeScript (strict) + Vite, React Router, TanStack Query. Design tokens and layout come from the approved HTML mockup. Accessible primitives are chosen in CP0.1A and recorded in the CP0.1A report |
| Process topology (local) | Backend API on `127.0.0.1:8000`. Mock upstream API on `127.0.0.1:8100` (local/test only, ADR-0008). Vite dev server on `127.0.0.1:5173`, proxying `/api` and `/health`, so the browser sees one origin and CORS can stay default-deny |
| Dependency management | Backend: `uv` with `pyproject.toml` and a committed lock file. Frontend: npm with `package-lock.json`. Installation happens only when a checkpoint authorises it |

**Not in S0:**
- event streaming (SSE/WebSocket);
- background job queue;
- object-store implementation;
- GPT-Live and Genesys code.

Interfaces `VoiceProvider` and `ObjectStore` exist only as protocols with a `NotAvailable` implementation (C-25).

### 2. Backend module layout (bounded contexts)

```text
app/
  api/            # routers only: auth, me, dashboard, cases, policies, risk, scripts, regulatory,
                  # search, saved_views, queues, intake, admin, voice, health
  core/           # settings, data policy, errors, correlation ids, logging redaction
  db/             # engine, session, base model, common columns
  security/       # identity provider protocol + local provider, tokens, sessions, csrf, rate limits,
                  # authorization (permissions, AccessContext, scope predicates)
  audit/          # audit writer, hash chain, verification
  domain/
    party/ policy/ risk/ scripts/ callback/ evidence/ findings/ regulatory/ config/
      models.py schemas.py repository.py service.py
  search/         # global search, explorer filters, KPI predicates shared with drilldown
  intake/         # connector protocol, mock connector, manual intake, corrections, validation
  voice/          # VoiceProvider protocol + NotAvailableVoiceProvider (S0)
  storage/        # ObjectStore protocol (no S0 implementation)
mock_upstream/    # separate ASGI app, deterministic synthetic fixtures (local/test only)
migrations/       # Alembic
seed/             # deterministic synthetic seed generator
tests/            # unit, integration (schema call360_test in Call360_db), security, contract
contracts/generated/openapi.json (+ openapi.sha256)
```

**Layering:** routers → services → repositories → models. Routers hold no business rules. Repositories receive an `AccessContext` and apply scope predicates in SQL. Domain services don't depend on transport, so browser voice (S1) and Genesys (S6) become adapters.

### 3. Identifiers, time and money

- **Internal primary keys:** UUID (v7 preferred for index locality; v4 acceptable). They are opaque, never reused, and never derived from policy numbers, names or phone numbers.
- **Human references:** separate unique columns per entity type, for example:
  - case `CB-2026-10482`
  - attempt `ATT-2026-000123`
  - session `SES-2026-000045`
  - script version `SV-COMMON-ILP-3.1`

  External source identifiers live in `external_reference` (`source_system`, `object_type`, `external_id`).
- **Timestamps:** `timestamptz` stored in UTC. The reporting time zone is `Asia/Singapore` and is declared in every KPI payload. Source time zone and contact-window local times are kept where relevant.
- **Money:** `numeric(18,2)` plus an ISO 4217 `currency` column. No floats.

### 4. Data policy (owner correction to the CP0.0 proposal)

- Business rows carry explicit provenance: `source_type`, `source_system`, `source_reference`, `source_observed_at`, `recorded_at`, `mapping_version`.
- They also carry an `is_synthetic boolean NOT NULL`.
- There is **no permanent database CHECK** forcing `is_synthetic = true`. That would make the schema incompatible with future real data.
- Synthetic-only operation is enforced as an **environment policy**: `DATA_POLICY=SYNTHETIC_ONLY`, the default and only allowed value when `APP_ENV ∈ {local, test}` (ADR-0008 §6).

### 5. Local verification instead of CI

There is no CI infrastructure in local development. Each repository documents commands that produce captured output, and that output is the evidence.

| Repo | Commands (names from execution plan §D) |
|---|---|
| Call360-backend | `make setup`, `make migrate`, `make seed`, `make dev`, `make test`, `make lint`, `make typecheck`, `make openapi`, `make contract-check`, `make audit-verify`, `make secret-scan` |
| Call360-frontend | `npm run dev`, `npm run build`, `npm run lint`, `npm run typecheck`, `npm run test`, `npm run api:generate`, `npm run api:check`, `npm run e2e`, `npm run secret-scan` (repo plus built bundle) |
| Call360-specs | `python3 scripts/validate_specs.py`, `python3 scripts/evidence_manifest.py <repo>` |

- **Secret scanning and security test suites are mandatory gates** at every checkpoint. They run locally; running them locally does not weaken them.
- A missing scanner binary means the checkpoint is BLOCKED, not skipped.

### 6. Evidence without commits (owner decision C-23)

Commits require explicit authorisation, so a checkpoint's evidence records two things:
1. the repository's base Git SHA (`git rev-parse HEAD`);
2. a deterministic manifest produced by `scripts/evidence_manifest.py`. It lists every changed or new file as `status<TAB>sha256<TAB>path`: paths are repo-relative and POSIX, entries are sorted by path, and the status is one of `M`, `A`, `D`, `??`. A SHA-256 over the canonical manifest text completes it.

When the owner authorises a commit, the commit SHA replaces the manifest as the primary reference. The manifest is kept as history.

## Alternatives considered

- **Async SQLAlchemy:** not required for the S0 load. The CP0.1A implementation chooses sync or async and records it, with no contract impact.
- **Docker Compose Postgres:** permitted, but not required, because a local Postgres already exists.
- **Elasticsearch for search:** rejected for S0 (see SEARCH_WORKSPACE, "avoid premature Elasticsearch").
- **CI pipelines:** out of scope by owner instruction. Local commands provide the same checks.

## Consequences

- Each repository is independently runnable and verifiable.
- The integrated gate (CP0.6) orchestrates the three working trees locally against a freshly reset schema.
- Wherever the stage documents say "fresh" or "newly created database" (for example MULTI_REPO §7, S0 acceptance), this means: the guarded test harness drops and recreates the `call360_test` schema in `Call360_db`, then migrates and seeds. No new database is created, and automated commands never reset `call360` (D-16, D-22).
- Evidence is reproducible from the base SHA plus the file manifest.
- Moving to company CI later reuses the same commands.
