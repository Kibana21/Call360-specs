# Call360 — Stage 0 authentication and authorization design

**Status:** accepted with CP0.0 (2026-11-15); aligned for CP0.1A/CP0.1B on 2026-11-15 (D-21 checkpoint split, D-22 database schemas and roles, D-23 concurrent refresh). Normative for CP0.1A and CP0.1B
**Decision record:** ADR-0004
**Requirements:** IAM-001…011, SEC-002…007, ADMIN-001…004, GOV-002, SEARCH-006, PARTY-005
**Caveat:** local login is for synthetic development data only. This design targets OWASP ASVS 5.0 Level 2 and is intended for independent review. It is not a claim of zero vulnerabilities.

## 1. Components

```text
Browser (React SPA, same origin via Vite proxy)
   │  HttpOnly cookies: access JWT, refresh token;  readable cookie: CSRF token
   ▼
FastAPI ── security.middleware: correlation id → security headers → origin/CSRF check (unsafe methods)
        ── security.authn: verify access JWT → load auth_session (must be active) → load principal (ACTIVE)
        ── security.authz: resolve effective permissions + market scopes (per request, from DB)
        ── route dependency require("<permission>") → 403 if missing
        ── repository(AccessContext) → SQL scope predicates → 404 if object outside scope
        ── audit writer (same transaction)
IdentityProvider protocol: LocalIdentityProvider (S0) │ OidcIdentityProvider (S5, Okta / Entra ID; AD via federation)
```

## 2. Identity provider abstraction

```text
IdentityProvider
  kind -> LOCAL | OIDC_ENTRA | OIDC_OKTA
  authenticate(request) -> ExternalIdentity{issuer, subject, display_name, group_ids[]} | AuthFailure
  (S5) begin_login(redirect) / complete_login(code, state, nonce, pkce_verifier)
```

- **Login result:** `(issuer, subject)` resolves to an `identity_binding` and then a `principal`.
  - The LOCAL provider's issuer is `call360-local`, and its subject is the principal's stable binding ID, not the username.
  - New external identities are created with no group memberships, so least privilege applies (S5).
- **Group sources:**
  - **LOCAL groups:** managed in the admin UI.
  - **External groups:** mapped by **immutable external group ID**, never by display name. Unrecognised groups confer nothing.

## 3. Local credentials and accounts

| Item | S0 design | Default status |
|---|---|---|
| Password hashing | Argon2id, memory 64 MiB, t=3, p=1. Parameters are stored with the hash and rehashed on login if they change | S-3, proposed |
| Password policy | 12 to 128 characters, no composition rules, rejects an offline list of common and breached passwords plus username or display-name derivatives | S-3, proposed |
| Errors | One response for any failed login: `401 AUTH_INVALID_CREDENTIALS`, "Sign-in failed". It is the same for unknown user, wrong password, disabled or locked, and response timing is equalised (a dummy hash is computed for unknown users) | T-51 |
| Throttling and lockout | Per account: 5 failures in 15 min trigger exponential backoff (1, 2, 4… min, capped at 30). Per IP: 20 attempts per minute, then `429 RATE_LIMITED`. The lockout state is persisted in `local_credential` | S-4, proposed |
| Bootstrap | `call360 bootstrap-admin --username <u>` reads the password from TTY (no echo) or a one-shot env var that is unset after use. It refuses if any ACTIVE principal holds ADMIN, writes `SECURITY.BOOTSTRAP_ADMIN_CREATED`, and cannot run when `APP_ENV` is not `local` or `test` without an explicit flag | C-6, decided |
| Developer accounts | Created by an authenticated ADMIN in Administration → Users (sets a one-time password the user must change at first sign-in), or by `call360 create-local-user --group <g>` reading the secret from a gitignored `.env.local`. **No default or shared passwords; nothing in seed, fixtures, docs or git** | C-6, decided |
| Role switching | Not provided. A different role means a different account. The mockup's "Continue as…" buttons are not implemented | C-6, decided |
| Test credentials | Generated randomly per test run and never written to disk outside the test temp directory | C-6, decided |

## 4. Tokens, sessions and CSRF

| Item | Value | Default status |
|---|---|---|
| Access token | JWT signed with EdDSA (Ed25519). The algorithm allowlist is `EdDSA` only; `none`, HS* and RS* are rejected. Claims: `iss=call360-local-api`, `aud=call360-api`, `sub=<principal_id>`, `sid=<auth_session_id>`, `jti`, `iat`, `nbf`, `exp`, `typ=access`, header `kid` | IAM-006 |
| Access lifetime | 10 min | S-2, proposed |
| Refresh token | 256-bit random, base64url, opaque. Stored as HMAC-SHA-256 with a server-side pepper. One `refresh_token_family` per session | IAM-007 |
| Refresh lifetime | Idle 30 min, absolute 8 h (session-bound) | S-2, proposed |
| Rotation | `POST /api/v1/auth/refresh` atomically marks the presented token used (`UPDATE … WHERE used_at IS NULL`), then issues the next generation | IAM-007 |
| Reuse | Presenting a revoked token, a token whose family or session is revoked or expired, or an already-used token that does **not** meet every benign-concurrency condition below is **reuse**. It revokes the family and the session, writes `SECURITY.REFRESH_REUSE_DETECTED` and returns `401 AUTH_REFRESH_INVALID` | T-52; BE-AUTH-05 |
| Concurrent refresh (D-23, refined at CP0.1A) | **An already-used refresh token never mints an access token or a refresh token.** *Client:* one refresh at a time per browser, using a Web Locks API lock (`c360-refresh`) shared by all tabs. After acquiring the lock, a tab first re-probes `GET /api/v1/me` with the shared cookies. If that succeeds, another tab has already refreshed, and the original request is retried without calling refresh. *Server:* a used token is classified as a **benign concurrent refresh** only if **all** of these hold: (1) it is the generation immediately preceding the family's newest token; (2) its successor was issued no more than `REFRESH_REUSE_GRACE_SECONDS` (default 10, configurable) ago; (3) the family and the session are active and unexpired; (4) the principal is active. A benign duplicate gets `409 REFRESH_SUPERSEDED`, a non-token response with no `Set-Cookie`, telling the client to retry with the current cookies. It writes `AUTH.REFRESH_SUPERSEDED` at debug level, without revocation. Any other used token is reuse (row above). Rotation and classification run under a row lock (`SELECT … FOR UPDATE`) on the family, so two simultaneous redemptions of the same unused token yield exactly one rotation and one `409` | BE-AUTH-10; RR-03 |
| Session | `auth_session` is created at login with a new ID, regenerated on every login (fixation defence). It is checked on **every** authenticated request; a revoked or expired session, or a disabled principal, returns `401 AUTH_SESSION_INVALID` | IAM-009 |
| Cookies | Access cookie `__Host-c360_at` (HttpOnly, Secure, SameSite=Lax, Path=/). Refresh cookie `__Secure-c360_rt` (HttpOnly, Secure, SameSite=Strict, Path=/api/v1/auth/refresh). CSRF cookie `__Host-c360_csrf` (not HttpOnly, Secure, SameSite=Strict). On plain-HTTP loopback only (`APP_ENV=local`), the prefixes and `Secure` are dropped (`c360_at` and so on), and the gate tests both modes | S-5, proposed |
| CSRF | Double-submit: the `X-CSRF-Token` header must equal the CSRF cookie, **and** an HMAC of the value bound to the session ID must verify. Before login, `GET /api/v1/auth/csrf` issues a pre-session token bound to a short-lived nonce. Every unsafe method also requires `Origin` (or `Referer`) in the configured allowlist | SEC-003 |
| Storage rule | No token in `localStorage`, `sessionStorage`, URL, JS globals, logs or error bodies. The SPA never reads the token cookies | IAM-008 |
| Refresh coordination | See "Concurrent refresh" above | RR-03 |
| Signing keys | Ed25519 key pair per environment, generated into a gitignored path. `kid` supports rotation, with old public keys kept until their maximum token lifetime has passed. Production custody (Key Vault) is S5 | S-6, proposed |
| Logout | `POST /api/v1/auth/logout` revokes the session and its refresh family, clears cookies and writes an audit event | IAM-009 |
| Invalidation | Disabling a principal, changing a membership or mapping, or an admin revoking a session takes effect on the next request, because permissions and session are resolved from the database per request (T-54 local adaptation) | IAM-009 |

## 5. Roles, groups and scopes (S0 seed of the access model, not of accounts)

| Group (LOCAL) | Role mapping | Market scope mapping |
|---|---|---|
| `LOCAL_ADMIN` | `ADMIN` | `SG`, `MY` |
| `LOCAL_USER_SG` | `USER` | `SG` |
| `LOCAL_USER_MY` | `USER` | `MY` |

- **Checkpoints:** groups and group → role mappings are built in CP0.1A. Group → market-scope mappings and their enforcement are built in **CP0.1B-2**, which must be accepted before CP0.3 exposes any market-scoped record. Until then a principal has no market scope, so scoped queries fail closed.
- **Effective permissions** are the union over active memberships → mappings → roles → permissions.
- **Effective scope** is the union of mapped markets. A principal with no mapped market sees no business records.
- **External groups (S5)** map onto the same tables by external group ID.

## 6. Permission catalogue and matrix

Codes are dotted lowercase. `Alias` maps to the security doc's names (C-5).

| Permission | Alias | ADMIN | USER | Notes |
|---|---|---|---|---|
| `dashboard.read` | — | ✓ | ✓ | KPIs scoped to the caller's markets |
| `case.read` | — | ✓ | ✓ | Cases, attempts, sessions, survey runs, answers, findings (read), case timeline |
| `policy.read` | — | ✓ | ✓ | Policies, sale events, fact snapshots, FSC |
| `party.read` | — | ✓ | ✓ | **Masked** party and contact data only |
| `risk.read` | — | ✓ | ✓ | Risk assessments, factors, rule-set metadata |
| `script.read` | — | ✓ | ✓ | Script Studio, assignment rules, regulatory references, controls |
| `search.use` | — | ✓ | ✓ | Global search, explorer facets |
| `saved_view.manage_own` | — | ✓ | ✓ | Own views only |
| `queue.read` | — | ✓ | ✓ | Work Queues, Review Workbench lists |
| `voice.preflight.read` | — | ✓ | ✓ | Returns NOT_AVAILABLE in S0 |
| `intake.read` | — | ✓ | — | Intake sources and runs |
| `intake.mock.sync` | — | ✓ | — | Trigger a mock upstream import run |
| `intake.manual.submit` | — | ✓ | — | Manual injection **and** POL-007 corrections (D-13; S-9 proposed) |
| `admin.users.read` | — | ✓ | — | Users, bindings, memberships |
| `admin.users.manage` | `USER_ADMIN` | ✓ | — | Create, enable or disable users; reset local password |
| `admin.groups.manage` | `USER_ADMIN` | ✓ | — | Memberships; group-role and group-scope mappings |
| `admin.sessions.manage` | — | ✓ | — | View and revoke sessions |
| `audit.read` | — | ✓ | — | Audit event search |
| `config.read` | — | ✓ | — | Code lists, feature flags |
| `config.manage` | — | ✓ | — | New code-list versions; flag changes (not approval-governed lists, see §8) |
| `system.health.read` | — | ✓ | — | `/api/v1/admin/system-health` |
| `script.edit` | `SCRIPT_EDIT` | — | — | **Reserved**, S2 |
| `script.approve` / `script.publish` | `SCRIPT_APPROVE` | — | — | **Reserved**, S2; never granted to ADMIN by default |
| `risk.override.request` / `risk.override.approve` | `RISK_OVERRIDE` | — | — | **Reserved**, S2 |
| `recording.read`, `transcript.sensitive.read` | `RECORDING_READ` | — | — | **Reserved**, S1/S3 |
| `review.decide` | — | — | — | **Reserved**, S3 |
| `evidence.export` | `EVIDENCE_EXPORT` | — | — | **Reserved**, S3/S4 |
| `pii.unmasked` | — | — | — | **Reserved**, S5; granted to nobody in S0 (S-8) |

Reserved permissions exist in the `permission` table with `reserved = true`. The service layer refuses to grant them in S0 (BE-IAM-03, ADMIN-003).

## 7. Enforcement rules

1. **Route inventory:** every route declares `require(<permission>)` or appears in the public allowlist.
   - The public allowlist is `/health/live`, `/health/ready`, `POST /api/v1/auth/login`, `GET /api/v1/auth/csrf` and `POST /api/v1/auth/refresh`; refresh is authenticated by the refresh cookie.
   - A test enumerates the FastAPI routes and fails on any undeclared route (BE-SEC-01, GOV-002).
2. **Object scope:** repositories accept `AccessContext{principal_id, permissions, markets}` and add the scope predicate (`market_code = ANY(:markets)`) to every query, including counts, facets, KPI aggregates, search suggestions and existence checks.
   - **Parties** are in scope when they hold a role on an in-scope policy.
   - **Scripts and regulatory references** are in scope when their `market_code` is in scope or is `ALL`.
3. **Response semantics (S-7, proposed):**
   - A missing function permission returns `403 FORBIDDEN`, audited as `ACCESS.DENIED_FUNCTION`.
   - An object that doesn't exist or is out of scope returns `404 NOT_FOUND`, with an identical body; the out-of-scope case is audited as `ACCESS.DENIED_OBJECT`.
4. **Masking (S-8, proposed):** the server masks names (`E. P****** 042`), phone numbers (`+65 •••• 0142`), email and dates of birth in **every** response, including search highlights and exports.
   - Search over parties uses the pseudonymous `display_alias` and the `masked_name`.
   - An exact phone match uses the `value_hmac` token only: no fuzzy matching, and the full value is never returned.
5. **Rate limits (SEC-006):**

   | Target | Limit |
   |---|---|
   | Login | §3 |
   | Refresh | 30 per minute per session |
   | Search and explorer | 60 per minute per principal |
   | Unsafe methods | 30 per minute per principal |
   | Intake | 10 per minute per principal |

   The limiter is in-process and single-instance (S-10, a known limitation; RR-05).
6. **Logging:**
   - Structured logs carry the correlation ID and never include tokens, passwords, cookies, full contact values or raw search terms; search terms are logged as a normalised SHA-256 (S-14).
   - Request bodies are not logged for auth or intake routes.
7. **Security headers:**
   - `Content-Security-Policy: default-src 'self'; frame-ancestors 'none'; object-src 'none'; base-uri 'self'`;
   - `X-Content-Type-Options: nosniff`, `Referrer-Policy: same-origin`, `Permissions-Policy` (microphone denied in S0), `Cache-Control: no-store` on API responses;
   - HSTS when served over HTTPS;
   - CORS: no `Access-Control-Allow-Origin` (same-origin only).

## 8. Auditable administration (IAM-010, ADMIN-001…004)

| Admin capability | Permission | Audit action |
|---|---|---|
| List and view users, bindings, memberships | `admin.users.read` | `ADMIN.USERS_VIEWED` (sampled; denials always) |
| Create local user; enable or disable; reset local password | `admin.users.manage` | `ADMIN.USER_CREATED`, `ADMIN.USER_ENABLED`, `ADMIN.USER_DISABLED`, `ADMIN.PASSWORD_RESET`. Disabling revokes all sessions |
| Add or remove a group membership | `admin.groups.manage` | `ADMIN.MEMBERSHIP_ADDED`, `ADMIN.MEMBERSHIP_REMOVED` (before/after, reason) |
| Change a group-role or group-scope mapping | `admin.groups.manage` | `ADMIN.GROUP_MAPPING_CHANGED`. An admin cannot remove the last ADMIN mapping, or their own ADMIN membership, without a second admin (lock-out guard) |
| View or revoke sessions | `admin.sessions.manage` | `ADMIN.SESSION_REVOKED` |
| Search audit events | `audit.read` | (read, not audited per row) |
| New code-list version; feature-flag change | `config.manage` | `CONFIG.CODE_LIST_VERSION_ACTIVATED`, `CONFIG.FLAG_CHANGED` |

Some code lists are business-approval governed: `finding_materiality_policy`, `kpi_sla_exemption_rule`, `sbq_risk_band`, `risk_factor` and `callable_party_roles`. In S0 they are **seeded and read-only**, because changing them needs business approval that S0 cannot record. `config.manage` covers only `market` labels, display lists and feature flags.

**Security events (IAM-011):**

| Action | Records |
|---|---|
| `AUTH.LOGIN_SUCCEEDED`, `AUTH.LOGIN_FAILED` | Username hash, IP, outcome |
| `AUTH.LOCKOUT_APPLIED` | — |
| `AUTH.LOGOUT` | — |
| `AUTH.REFRESH_ROTATED` | Counter only; not a full event per rotation |
| `SECURITY.REFRESH_REUSE_DETECTED`, `AUTH.SESSION_REVOKED` | — |
| `ACCESS.DENIED_FUNCTION`, `ACCESS.DENIED_OBJECT`, `SECURITY.CSRF_REJECTED` | — |
| `SECURITY.BOOTSTRAP_ADMIN_CREATED`, `INGEST.NON_SYNTHETIC_REJECTED` | — |

Each event carries the actor or session (when known), IP, user-agent hash, correlation ID and outcome, and never secrets.

## 9. Future SSO compatibility checklist (S5)

- Add `OidcIdentityProvider` with discovery, JWKS caching and rotation, exact redirect URI, `state`, `nonce`, PKCE and issuer/audience pinning.
- Map external group IDs through `app_group.external_group_id` and `group_role_mapping`, and handle group overage and removal. Privilege drops take effect on the next request (per-request resolution) or within an approved cache bound.
- Link more than one binding to one principal only after verified linking. The audit actor snapshot keeps the prior issuer and subject.
- Local login is disabled by configuration outside `local` and `test`.

## 10. Database schemas, roles and connection safety (D-22)

One existing local PostgreSQL database, **`Call360_db`**, holds everything. No second database is created and Docker PostgreSQL is not required. Names are mixed-case, so raw SQL double-quotes them.

| Item | Development (application) | Automated tests |
|---|---|---|
| Schema | `call360` | `call360_test` |
| Login role | `Call360_db_user` (existing). Verified 2026-11-15 to be a **superuser** with CREATEDB and CREATEROLE. It is accepted for local development (RR-11) and is used only by the running app and developer commands | `call360_test_user`, a **new** least-privilege role created by the owner at CP0.1A implementation time. It is not created during specification work. The existing role `Call360_user` (purpose unknown) is not used |
| Configuration | `.env`: `APP_DATABASE_URL`, `APP_DB_SCHEMA=call360` | `.env.test`: `TEST_DATABASE_URL`, `TEST_DB_SCHEMA=call360_test` |
| Credentials | Only in gitignored env files. Never in source, specs, fixtures, logs or the frontend bundle | Same; a separate, independently generated password (≥ 32 random bytes) written only to gitignored `.env.test` by the setup script, never printed |
| Migrations | `make migrate` (app config) | Run by the test harness with the test configuration before each test session |
| Reset | **No automated reset.** The developer may run an interactive `make dev-reset` that requires typing `call360` to confirm. Tests, the gate and CI-like scripts can never invoke it | The test harness drops and recreates objects **only** in `call360_test`, after the guards below pass |

**Test role privileges.** The SQL is applied once by the owner using `Call360_db_user`:

| Grant | Effect |
|---|---|
| `LOGIN`, `NOSUPERUSER`, `NOCREATEDB`, `NOCREATEROLE`, `NOINHERIT`, `NOBYPASSRLS` | No elevated rights |
| `CONNECT` on `Call360_db` | Can connect, nothing more |
| Owner of schema `call360_test` (create, alter and drop only inside it) | Can run migrations in its own schema |
| **No** `USAGE` on schema `call360` and no privileges on any of its objects | Cannot read, modify, truncate, alter or drop application data |
| `REVOKE CREATE ON SCHEMA public FROM PUBLIC` (and from the test role) | No stray objects |
| Role default `search_path = call360_test` in `Call360_db` | Unqualified names resolve to the test schema |

**Fail-closed guards.** These are implemented in CP0.1A and tested by BE-DATA-14.

1. Every SQLAlchemy model uses a schema-qualified `MetaData(schema=<configured schema>)`. Each connection sets `search_path` to exactly that schema.
2. Settings refuse to load if:
   - the schema is not in `{call360, call360_test}`;
   - `APP_ENV=test` with a schema other than `call360_test`;
   - a non-test environment uses `call360_test`;
   - the app and test URLs are identical.
3. Before **any** migration (development or test), Alembic `env.py` verifies the connected database, the role and the schema, takes the target schema from settings, keeps its version table in that schema, and refuses to run if the connected `current_database()` is not the expected `Call360_db` or the schema check fails.
4. Before the test harness creates or drops anything, it asserts:
   - schema = `call360_test`;
   - `current_user` ≠ the application role;
   - `rolsuper` is false;
   - `has_schema_privilege(current_user, 'call360', 'USAGE')` is false.

   If any check fails, the whole test session aborts before touching the database.
5. Destructive helpers accept no schema argument. They are hard-wired to `call360_test` and re-check the guards at call time.
6. Startup readiness (`/health/ready`) verifies the expected database, schema and migration head, and returns 503 on mismatch.

**Residual risk:** the development app connects as a superuser (RR-11). Before any non-synthetic data, replace `Call360_db_user` with a non-superuser application role confined to `call360`.

