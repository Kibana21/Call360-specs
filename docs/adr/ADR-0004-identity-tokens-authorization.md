# ADR-0004: Identity provider abstraction, tokens, sessions and authorization

**Status:** Proposed (CP0.0), 2026-11-15. Owner decisions applied: D-7 (access and refresh tokens, revocation, CSRF, RBAC, market scope), C-6 (secure bootstrap, developer-specific credentials, no default passwords, no passwordless role switching), D-13 (manual-intake permission for ADMIN)
**Detailed design:** `docs/security/S0_IDENTITY_ACCESS_DESIGN.md` (normative for CP0.1A and CP0.1B)
**Requirements:** IAM-001…011, SEC-003, SEC-004, SEC-006, SEC-007, ADMIN-003, GOV-002, SEARCH-006

## Context

The register requires several controls at once:
- short-lived access tokens (IAM-006);
- rotating opaque refresh tokens with reuse detection (IAM-007);
- HttpOnly cookies with CSRF protection (IAM-008);
- immediate revocation (IAM-009).

The security doc prefers a server-managed BFF/session-cookie pattern. Okta and Microsoft Entra ID / AD must be addable in S5 without changing principals, permissions or audit history.

## Decision

1. **The identity model separates person, login identity and credential:**
   - `principal` is the immutable internal subject.
   - `identity_binding` is unique per issuer and subject: `(provider, issuer, subject)`.
   - `local_credential` exists only for the LOCAL provider.

   Email is never an identity key. The `IdentityProvider` protocol has a `LocalIdentityProvider` in S0. An `OidcIdentityProvider` (Authorization Code + PKCE, JWKS, `state`/`nonce`) is added in S5 behind the same protocol.

2. **Hybrid token/session model:**
   - The browser holds a short-lived signed **access JWT** (EdDSA/Ed25519 only, ~10 min) in an HttpOnly cookie.
   - It also holds an **opaque refresh token** (256-bit) in an HttpOnly cookie scoped to the refresh path. Only an HMAC of the refresh token is stored. It rotates on every use, and reuse revokes the token family and the session.
   - A server-side `auth_session` is **authoritative**. Every request validates the JWT *and* checks that the session is active. That makes logout, disablement, membership change and admin revocation effective on the next request.

3. **CSRF:** a session-bound double-submit token (`X-CSRF-Token` header) plus an `Origin` allowlist on every unsafe method, including login. SameSite is defence in depth, not the control.

4. **Authorization:** group → role (base `ADMIN`, `USER`) → fine-grained dotted permissions. Group → market-scope mappings provide object scope (`SG`, `MY` synthetic markets). Every route declares a permission (or appears in an explicit public allowlist). Every repository query applies scope predicates **before** results, counts, facets or suggestions.

5. **Response semantics:**
   - A missing function permission returns **403**.
   - An object outside the caller's scope, or one that doesn't exist, returns **404**. Both cases are audited.

6. **Segregation:** ADMIN does not hold reserved permissions: `script.edit`, `script.approve`, `script.publish`, `risk.override.*`, `recording.read`, `evidence.export`, `pii.unmasked`, `review.decide`. In S0 nobody holds them. Maker-checker separation therefore exists in the model before S2 introduces those workflows.

7. **Accounts (C-6):**
   - `call360 bootstrap-admin` creates the first administrator from a secret supplied at runtime. It refuses to run if an active admin exists, and its use is audited.
   - Developer accounts are created by an authenticated admin, or by a CLI reading developer-specific secrets from a gitignored `.env.local`.
   - There are no default passwords and no seeded credentials. The mockup's passwordless role switching is not implemented.
   - Automated tests generate random credentials per run.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Server session cookie only, no JWT/refresh | Simpler, but it doesn't meet IAM-006 and IAM-007 as registered. Owner decision D-7 requires the token lifecycle |
| Stateless JWT only | Cannot meet IAM-009 immediate revocation, or T-54, without a server check |
| Tokens in `localStorage` | Prohibited by IAM-008 |
| Roles stored on the user record | Prevents future mapping of IdP group IDs (IAM-004). Rejected, along with the withdrawn `LOCAL_BUILD_PLAN.md` |
| Defer market scope to S5 | Breaks SEARCH-006 and T-46 in S0. Owner decision D-7 keeps it in S0 |

## Consequences

- There are two validations per request: JWT, then a session lookup. That cost is acceptable for S0 and can be cached later within an approved bound.
- Refresh races between tabs could look like reuse. The frontend must serialise refresh (single flight with a cross-tab lock). The residual risk is recorded (THREAT_MODEL_S0, RR-03).
- S5 adds OIDC and immutable IdP group-ID mappings into the same `app_group` and `group_role_mapping` tables. Existing audit actor history is unaffected.
