# CP0.1A — Core authentication and application shell: acceptance checklist

**Checkpoint status:** **ACCEPTED** by the project owner on 2026-11-15, after manual review of the running application and the authorised defect corrections. CP0.1B and CP0.2 are not started.
**Scope source:** `docs/plans/S0_IMPLEMENTATION_PLAN.md` (CP0.1A). Design references: ADR-0003…0006, `S0_IDENTITY_ACCESS_DESIGN.md` (§3–§8, §10), `S0_DATA_MODEL.md` §4.1 (Build = CP0.1A), `S0_API_CATALOGUE.md` (Build = CP0.1A), `S0_SCREEN_SPEC.md`, `S0_TEST_MATRIX.md`.

## 1. Decisions recorded (owner, 2026-11-15)

| Ref | Decision | Applied in |
|---|---|---|
| D-21 | CP0.1 is split. **CP0.1A** is core authentication and the application shell. **CP0.1B** is administration and configuration, delivered as packages B-1 (configuration, before CP0.2), B-2 (market scope, before CP0.3) and B-3 (administration completion, before CP0.6). CP0.1B is not a blanket prerequisite. Market-scoped authorization must be implemented and tested before any market-scoped record is exposed through an API. CP0.1A must be demonstrated and accepted before CP0.1B or CP0.2. Nothing is removed from Stage 0 | S0_IMPLEMENTATION_PLAN; S0_DATA_MODEL Build column; S0_API_CATALOGUE checkpoint column; S0_TEST_MATRIX; S0.md |
| D-22 | One database, `Call360_db`. Schemas `call360` (development) and `call360_test` (automated tests). The app uses `Call360_db_user`, whose privileges were verified (superuser, RR-11). Tests use a separate least-privilege role `call360_test_user` confined to `call360_test`, with no rights on `call360`, via separate connection configuration. Fail-closed schema guards apply. Automated tests never reset or destroy `call360`. No hard-coded credentials and no Docker PostgreSQL. **No database objects created during specification work.** Amends D-16 | S0_IDENTITY_ACCESS_DESIGN §10; ADR-0003 §1; S0_IMPLEMENTATION_PLAN §1, §4; S0.md |
| D-24 | Test role `call360_test_user` gets an independently generated strong password (≥ 32 random bytes) held only in gitignored `Call360-backend/.env.test`. Before any migration or destructive test reset, the connected database, role and schema are verified. `call360` is never reset by automated tests. `Call360_db_user` superuser status is a local-only risk (RR-11) | S0_IDENTITY_ACCESS_DESIGN §10 |
| D-23 | Concurrent refresh must not invalidate legitimate multi-tab sessions. **Refined at CP0.1A:** a used refresh token never mints any token. A browser-wide Web Locks lock plus a `/me` re-probe avoids duplicate refreshes. A recognised benign duplicate (immediately previous generation, within 10 s of rotation, active family, session and principal) gets a non-token `409 REFRESH_SUPERSEDED`; anything else is reuse and revokes | S0_IDENTITY_ACCESS_DESIGN §4; THREAT_MODEL_S0 TM-04, RR-03; BE-AUTH-10 |

## 2. Scope

| Kind | CP0.1A |
|---|---|
| Tables (15) | `identity_provider`, `principal`, `identity_binding`, `local_credential`, `app_group`, `group_membership`, `role`, `permission`, `role_permission`, `group_role_mapping`, `auth_session`, `refresh_token_family`, `refresh_token`, `login_attempt`, `audit_event` |
| Endpoints (10) | API-001 `/health/live`, API-002 `/health/ready`, API-003 `GET /auth/csrf`, API-004 `POST /auth/login`, API-005 `POST /auth/refresh`, API-006 `POST /auth/logout`, API-008 `GET /me`, API-010 `GET /admin/users`, API-012 `PATCH /admin/users/{id}`, API-021 `GET /admin/audit-events` |
| Routes | `/login`, `/session-expired`, `/unauthorized`, `/` (interim session landing), `/admin` (redirect), `/admin/users`, `/admin/audit`. All other navigation items are disabled with their stage label |
| CLIs | `bootstrap-admin`, `create-local-user` (developer-specific secrets from the gitignored `.env.local`), `audit-verify`, `generate-keys` |
| Dependencies to install (only after `IMPLEMENT CP0.1A`) | **Backend (uv):** fastapi, uvicorn, pydantic, pydantic-settings, sqlalchemy, alembic, psycopg, argon2-cffi, pyjwt[crypto], cryptography; dev: pytest, httpx, ruff, mypy. **Frontend (npm):** react, react-dom, react-router-dom, @tanstack/react-query, vite, typescript, @vitejs/plugin-react, openapi-typescript, openapi-fetch, vitest, @testing-library/react, eslint, @playwright/test, @axe-core/playwright. **Tool:** gitleaks (Homebrew) for SCAN-01/02 |

**Deferred to CP0.1B:**
- B-1: `code_list`, `code_list_version`, `code_value`, `feature_flag`, `feature_flag_change`; API-022…025; `/admin/config`.
- B-2: `group_scope_mapping`; scope enforcement.
- B-3: API-007, 009, 011, 013, 014…020, 026; `/admin/groups`, `/admin/sessions`, `/admin/system`.

## 3. Acceptance criteria

| ID | Criterion | Tests | Result |
|---|---|---|---|
| AC-0.1A-01 | The backend (`make dev`) and frontend (`npm run dev`) start locally. `/health/ready` is OK against `Call360_db`/`call360` | BE-DATA-01, manual demo | PASS — `make dev` + `npm run dev`; `/health/ready` → ok via the Vite proxy (smoke test); E2E servers start the same way |
| AC-0.1A-02 | Migrations create exactly the 15 CP0.1A tables in `call360` (development) and in `call360_test` (test role) | BE-DATA-01 | PASS — 15 tables + `alembic_version` in `call360` and in `call360_test` (BE-DATA-01, including downgrade/re-upgrade) |
| AC-0.1A-03 | Schema isolation: the test role has no rights on `call360`; misconfigured connections abort; no automated command resets `call360` | BE-DATA-14 | PASS — BE-DATA-14 (9 cases) plus a direct psql probe: test role denied SELECT/CREATE/DROP on `call360` and CREATE on `public` |
| AC-0.1A-04 | `bootstrap-admin` creates the first admin from a runtime secret, refuses a second run and audits; no default or committed credentials | BE-AUTH-09, SCAN-01 | PASS — BE-AUTH-09; dev `bootstrap-admin` second run refused; secret scans clean |
| AC-0.1A-05 | Login with Argon2id-verified credentials; uniform failure message; account backoff and IP throttling | BE-AUTH-01, 02, 03, E2E-01 | PASS — BE-AUTH-01/02/03, E2E-01 |
| AC-0.1A-06 | Access JWT validation rejects expired, wrong-issuer, wrong-audience, tampered, `alg=none` and wrong-type tokens | BE-AUTH-04 | PASS — 17 token tests (BE-AUTH-04) |
| AC-0.1A-07 | Refresh rotates; reuse revokes the family; concurrent multi-tab refresh does not revoke a legitimate session | BE-AUTH-05, BE-AUTH-10, FE-02 | PASS — BE-AUTH-05, BE-AUTH-10 (a/b/d/e), 16 FE-02 unit tests, E2E multi-tab test |
| AC-0.1A-08 | CSRF and Origin enforced on every unsafe route including login; no tokens in browser storage or URLs; cookies HttpOnly | BE-AUTH-07, 08, E2E-15 | PASS — BE-AUTH-07/08, E2E-15 |
| AC-0.1A-09 | ADMIN reaches Users and Audit. USER gets Unauthorized in the UI and 403 from the API, audited. Every route declares a permission; reserved permissions cannot be granted | BE-SEC-01, BE-IAM-02 (role half), BE-IAM-03, E2E-10 (partial) | PASS — BE-SEC-01 (exact 10-route surface), BE-IAM-02/03, E2E-10 (partial) |
| AC-0.1A-10 | Logout invalidates the session (next call returns 401). Admin disable ends the user's session on the next request, with before/after audit | BE-AUTH-06, BE-AUD-04, E2E-13 (partial) | PASS — BE-AUTH-06, BE-AUD-04, E2E-13 (partial) |
| AC-0.1A-11 | The audit trail is append-only (UPDATE/DELETE rejected) and `audit-verify` passes; security events contain no secrets | BE-AUD-01, 02, 03 | PASS — BE-AUD-01 (UPDATE/DELETE/TRUNCATE), BE-AUD-02 (tamper detected), BE-AUD-03; dev chain verifies |
| AC-0.1A-12 | The shell reproduces the mockup's sidebar groups, header, breadcrumb, user controls and visual identity; the landing shows real `/me` data only; disabled items carry stage labels; title "Call360"; OpenAPI deterministic; `api:check` passes; axe has zero serious violations; secret scans clean; specs validator passes | FE-01, FE-03, FE-04, E2E-18 (partial), BE-CT-01, SCAN-02, SPEC-01 | PASS (automated) — FE-01, FE-03, FE-04/axe at 1280 and 1440 px, E2E-18 (partial), BE-CT-01, SCAN-01/02, SPEC-01. **Visual fidelity confirmed by the owner** after defect corrections UI-1…UI-4 (§4a); deviations DV-01, 02, 10, 11, 12 recorded |

## 4. Evidence

All outputs are in `docs/acceptance/evidence/CP0.1A/`, from a single run on 2026-11-15 in which all 16 checks exited 0.

| Check | Result |
|---|---|
| Backend lint (ruff), typecheck (mypy `--strict`) | Clean |
| Backend tests | **73 passed**: unit, integration and security, against `call360_test` as `call360_test_user` |
| OpenAPI determinism and contract | Matches; SHA-256 `f6ce8c890c4f846f6121cb7e6770cd68f5b43256bacfdf5d208c23b2a6d129e1` |
| Frontend lint, typecheck, `api:check`, build | Clean; built `index.html` carries a strict CSP |
| Frontend unit and component tests | **25 passed** |
| Playwright against the real FastAPI, PostgreSQL and Vite stack | **9 passed**, including axe (zero serious or critical) at 1280 and 1440 px |
| Secret scans (gitleaks 8.30.1) | Clean: backend 54 committable files; frontend committable files plus the `dist/` bundle |
| `npm audit` | 0 vulnerabilities (after upgrading to patched Vite 8, Vitest 4 and React Router 7; `minimatch` override for the lint toolchain) |
| Development audit chain | Verified |
| Specs validator | PASS |
| Manifests | Backend base `cdcd175` + manifest `4942e73a…`; frontend base `34bc704` + manifest `fa73f7e8…` |

**Database objects created (D-22):**
- schema `call360` (owner `Call360_db_user`);
- schema `call360_test` (owner `call360_test_user`);
- role `call360_test_user` (LOGIN, no superuser, no CREATEDB/CREATEROLE, CONNECT only, `search_path=call360_test`);
- 15 tables plus `alembic_version` in each schema;
- development accounts `dev.admin` (ADMIN, via bootstrap) and `dev.user` (USER), with credentials in gitignored `Call360-backend/.env.local`.

**Implementation notes:**
- Additive contract change: `AuditEventOut.actor_service`.
- Additive error codes: `IF_MATCH_REQUIRED` (428) and `REFRESH_SUPERSEDED` (409).
- Self-disable is rejected with `LAST_ADMIN_GUARD`.
- `POST /auth/logout` without a valid session simply clears cookies (idempotent).
- In-repo design deviations: `Call360-frontend/docs/design/DEVIATIONS.md`.

**Known limitations and residual risks:**
- **RR-11:** the development app connects as a superuser.
- **RR-05:** in-process rate limiter.
- **RR-01:** audit integrity relies on the database only.
- **RR-04:** loopback HTTP cookies without `Secure`; HTTPS-mode cookies are not yet exercised (CP0.6 gate).
- The password blocklist is a small offline list, not a breached-password corpus.
- E2E runs on Chromium only.
- No Python dependency audit tool (for example pip-audit) is installed.
- During setup, a failing `CREATE ROLE` printed two generated, never-used test-role passwords to the local console. Neither was ever applied: the role did not exist until the corrected run, which generated a new password and printed nothing. All engines now use `hide_parameters=True`.
- One early planted-secret probe was not detected for an unexplained reason. Five subsequent realistic probes were all detected.

## 4a. Owner-review defect corrections (authorised 2026-11-15)

| Item | Correction | Verification |
|---|---|---|
| UI-1 | Sidebar section-heading spacing restored to the mockup's rule (20 px; 6 px for the first) | Playwright checks computed padding at 1280 and 1440 px |
| UI-2 | Compact right-aligned stage indicators (clock icon = later in Stage 0; "S4" chip); no truncated labels; full stage text in the tooltip and for screen readers | Playwright asserts no clipped labels |
| UI-3 | Role badges: ADMIN purple, USER grey (Users and landing page) | Playwright class check |
| UI-4 | Sign in label centred between icon and chevron | Playwright geometry check (≤ 2 px) |
| UI-5 | No change; keyboard reachability verified at a 560 px viewport height | Playwright Tab-order check |
| Scanner | Call360-specific gitleaks rules (PostgreSQL credential URLs; pepper, CSRF, password and token assignments) plus a synthetic-fixture self-test that runs before every scan | 11 formats × 50 samples detected 50/50 in both repos; 0 false positives on placeholders and ordinary code |

**Regression evidence** is in `docs/acceptance/evidence/CP0.1A/defect-corrections/`. All 16 checks exited 0:

| Check | Result |
|---|---|
| Backend tests | 73 passed |
| Frontend unit tests | 25 passed |
| Playwright | 11 passed |
| Lint, types, contract, build | Clean |
| Secret scans (repos and bundle) | Clean |
| npm audit | 0 vulnerabilities |
| Audit chain, validator | PASS |

**Final state at acceptance** (per ADR-0003 §6, the owner's commits replace the manifests as the primary reference):
- **Backend:** commit `cc57961`, working tree clean.
- **Frontend:** commit `9ee9f3c`, working tree clean.
- **Specs:** commit `a08b7b6`, plus this uncommitted acceptance-record update.
- The owner committed and pushed all three to `origin/main` at 2026-11-15 15:12 +08:00.
- **OpenAPI SHA-256:** `f6ce8c890c4f846f6121cb7e6770cd68f5b43256bacfdf5d208c23b2a6d129e1`.
- **Migration head:** `0001_identity_foundation`.
- **History scan at acceptance:** gitleaks over the committed history of all three repos, with the Call360 rules.
  - No credential and no secret file was ever tracked.
  - No literal development database URL appears in any commit.
  - Only known false positives were found: BRD and register prose, and the public OpenAPI checksum.

**Credential exposure note:** while developing the self-test, a scanner fixture briefly contained a literal connection string with the development database password. It was caught by the new rule and replaced before the owner's 15:12 commit (verified: absent from all commits). Rotating that password is recommended (owner action; not performed).

**Residual risks unchanged:** RR-01, RR-04, RR-05, RR-11 and the limitations listed in §4. Default gitleaks rules give 2 known false positives on prose in the frozen BRD and register, relevant if specs scanning is added later.

## 5. Acceptance

| Role | Name | Date | Decision |
|---|---|---|---|
| Project owner | Project owner | 2026-11-15 | **ACCEPTED** — "I ACCEPT CP0.1A — Core Authentication and Application Shell" (manual review of the running application; evidence §4, §4a) |
