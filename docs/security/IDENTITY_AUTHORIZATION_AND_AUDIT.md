# Call360 — Login, Admin, Authorization, Token Security & Audit

**Version 0.3 · Proposal for Security and IAM review; not a penetration-test attestation.**

## Security goal and caveat

Build controls suitable for independent security review. **No design or implementation can promise that penetration testers will find zero vulnerabilities.** Target OWASP ASVS 5.0 Level 2 as a minimum assessment profile, select higher-assurance controls for sensitive functions, threat-model data flows, and require independent testing before production. Use synthetic records only until enterprise approval.

## Identity model: separate person, login source, group, permission

| Entity | Key fields | Invariant |
|---|---|---|
| `principal` | internal immutable UUID, display name, status, created/disabled timestamps | Not keyed by email/UPN; never recycle ID |
| `identity_binding` | principal_id, provider (`LOCAL`, `ENTRA`, `OKTA`), issuer, immutable external `sub`, status | Unique `(issuer, sub)`; email is not identity key |
| `local_credential` | principal_id, password hash, hash params, reset/lockout fields | Argon2id (or approved equivalent); never store password or reversible secret |
| `group` | group ID, external IdP GUID (optional), name, source and status | External group display name never solely confers access |
| `membership` | principal ID, group ID, provider, provenance, effective dates | Historical attribution survives group changes |
| `role` | canonical app role | ADMIN, USER base roles; optional REVIEWER, SCRIPT_AUTHOR, APPROVER, AUDITOR, etc. |
| `permission` | operation + resource + data scope | `SCRIPT_EDIT`, `SCRIPT_APPROVE`, `RISK_OVERRIDE`, `RECORDING_READ`, `EVIDENCE_EXPORT`, `USER_ADMIN` etc. |
| `role_binding` | principal/role/scope, grant source, effective interval | least privilege; admin not superuser of every protected activity |
| `auth_session` | principal, session_id, created/last_seen, expiry, device/context, revoked_at | server-side session revocation |
| `refresh_token_family` | session_id, family ID, token hash, generation, expiry, revoked, replay marker | one-time use rotation, family revocation on replay |
| `audit_event` | immutable action, principal, source provider, old/new hash/diff, reason, request ID | append-only, independent from current principal display name |

## Local authentication (development/S0)

- Seed **no shared default password and no hard-coded admin user**. A one-time bootstrap creates first admin via documented CLI with secret supplied securely at runtime; disable bootstrap after first use.
- Local login is for synthetic data/development environments only. Credential complexity, breach-password screening and password reset follow approved policy; use Argon2id with audited parameters; non-enumerating authentication errors; rate limits and risk-based lockout/backoff to avoid account enumeration and denial-of-service abuse.
- Provide `/login`, `/logout`, `/session`, and authorized admin user/group/permission management. Admin can disable sessions, review audit events, and request permission changes; privileged changes must be auditable.
- Require secure TLS in deployed environments (allow loopback HTTP for local testing); protect cookies with `HttpOnly`, `Secure` in HTTPS, `SameSite` as approved, host-only path/domain and reasonable lifetime.
- Prefer a server-managed **BFF/session-cookie** pattern for the browser. No refresh token or API key in `localStorage`, `sessionStorage`, URL query parameters, logs or JS globals.

## Access and refresh tokens

- If backend uses stateless access tokens, validate `iss`, `aud`, `exp`, `nbf`, `iat`, `jti`, cryptographic signature, algorithm allowlist and key `kid`; do not accept unsigned tokens or substitute token types. Use approved signing algorithms and key rotation; pin intended audience and issuer. Short-lived access tokens (e.g. 5–15 min **proposed**, not fixed policy).
- Refresh tokens are high-entropy **opaque secrets**, with only server-side hashes stored. Rotate on every redemption, atomically invalidate preceding generation, detect reuse/races and revoke family/session on replay; include device/session binding and absolute+idle expiry (to be approved).
- Implement explicit logout, disable-user revocation, session visibility and termination, password-reset invalidation, stale privileges handling and short authorization cache lifetime. Fail closed if identity data and permissions cannot be validated.
- For cookie-authenticated mutations use anti-CSRF tokens or equivalent robust defense, `Origin`/`Referer` checking and strict CORS; `SameSite` alone is not considered complete CSRF defense. Protect against XSS with content security policy, safe output encoding, trusted dependency policy and no dangerously rendered transcript HTML.
- Rate-limit login, token, search, export, media and administration APIs; prevent refresh storms with concurrency and idempotency protections.

## Future Okta / Microsoft Entra / AD groups

- Implement an `IdentityProvider` adapter today; S5 adds OIDC Authorization Code with PKCE, issuer metadata/JWKS validation, exact redirect URI, `state` and `nonce`, and back-channel/signed logout where required.
- Map **immutable provider group IDs** to canonical `ADMIN` and `USER` roles via a reviewed mapping configuration. New identities receive least privilege; unrecognized groups confer no permissions. Avoid role grants based solely on mutable user email or free-form group names.
- Active Directory may be federated through Entra ID or another approved OIDC broker. Do not assume traditional AD provides OIDC directly.
- Group synchronisation handles removal/deprovisioning, stale claims, group overage and access recertification; privilege drops revoke/revalidate sessions promptly. One person can have multiple identity bindings but one canonical principal after verified linking.
- App-level resource scopes (market, product line, case ownership, recording privilege) and segregation-of-duty permission checks remain authoritative after SSO.

## Permission matrix (baseline, owner-approved before release)

| Operation | USER | ADMIN | S&C checker / approved capability |
|---|---|---|---|
| Search authorized policies/cases | Scoped | Scoped | Scoped |
| View masked party information | Yes | Yes | Yes |
| Play full recording / view sensitive answers | Explicit grant | Explicit grant | Explicit grant |
| Create script draft | `SCRIPT_EDIT` | Only if separately granted | Optional |
| Publish script/rule | No by default | No by default | Independent `SCRIPT_APPROVE` + second-user rule |
| Override SBQ risk | No | No by default | `RISK_OVERRIDE` and approved reason/checker |
| Administer identities/groups | No | `USER_ADMIN` | No by default |
| Change audit/retention/crypto policy | No | Dual-controlled privilege | As approved |
| Export raw evidence | No by default | No by default | Scoped `EVIDENCE_EXPORT`, purpose and audit |

**Never grant unrestricted unmasked PII or automatic maker-checker bypass simply because the user belongs to the `ADMIN` group.** All permissions are enforced on the backend, including search queries, detail IDs, recording signed URLs, export and aggregate counts.

## Audit and platform protection

- Store attributable, append-only business and admin events with UTC timestamp, actor principal + external issuer/sub snapshot, action, entity ID/version, before/after diff or redacted hash, reason, correlation/request ID and outcome. Include failed admin attempts and denied sensitive access.
- Prevent editing/deleting historical events through normal application roles; isolate audit writers; use integrity chains/immutable storage and independent backups as approved. Retain accurate prior actor identity after group removal and external ID changes.
- Media stored in private object storage, encrypted in transit and at rest. Signed access must be short-lived, scoped to exact asset and purpose, audited, and checked before issuance. Do not provide raw unprotected object URLs.
- No real customer details/credentials in analytics, debug logs, test fixtures, telemetry, provider prompts without approval. Use redaction, separation of duties, retention jobs, legal hold and controlled export.
- Protect APIs against OWASP API risks: BOLA/IDOR, broken function authorization, mass assignment, injection, overfetching, resource exhaustion, SSRF and insecure external API trust.
- Operational controls: dependency lockfiles and SBOM, SAST/SCA/secret scan, migration safety, TLS and header checks, authenticated penetration test and retest, abuse-rate tests, restore/DR and incident response runbook.

## Security acceptance / negative tests

1. USER cannot invoke admin routes, approve self-authored scripts, override SBQ risk or receive another market's policy by guessing IDs.
2. Token reuse after refresh rotation revokes the family; logout and deactivation invalidate active sessions; expired, wrong-audience and wrong-issuer tokens are denied.
3. CSRF cross-site write is rejected; cookies not exposed to JS; no tokens in storage/logs/URLs.
4. External group role changes or identity disablement take effect under approved latency bound, including when prior JWT remains technically valid.
5. Masking applies to global search, exports, counts, media playback and API detail responses, not merely the UI.
6. An ADMIN who authored a script cannot self-approve; audit writer cannot silently rewrite history.
7. Brute force, resource exhaustion, input injection and large uploads produce controlled response with audit and monitoring.

## Stage responsibilities

- **S0**: local synthetic-only login; basic ADMIN/USER role mapping; server-side session + access checks; audit trail; permission-protected admin UI; secure bootstrap; key rotation-friendly abstraction.
- **S2**: operation-specific S&C maker/checker and script/risk permissions; immutable approval history.
- **S3**: evidence and recording privilege, scoped export, reviewer separation and access audit.
- **S5**: real OIDC + PKCE Okta/Entra, tested group ID mapping/deprovisioning, pen test, key rotation, retention, DR, enterprise operational readiness.
