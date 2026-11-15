# Call360 — Stage 0 threat model (STRIDE)

**Status:** CP0.0 draft, 2026-11-15 · **Requirement:** SEC-001 · **Method:** STRIDE per data flow and asset
**Scope:** the S0 local system: browser SPA, FastAPI API, PostgreSQL, mock upstream API, CLI tools (bootstrap, seed) and the three local repositories. Audio, transcripts from live calls, model providers and Genesys don't exist in S0. Their threats are listed in §5 so later stages inherit them.
**Caveat:** this model supports independent review. It does not certify the absence of vulnerabilities.

## 1. Assets

| Asset | Sensitivity in S0 | Why it matters |
|---|---|---|
| A1 Policy, party and contact data | Synthetic, modelled as PII | The design must protect real PII later (masking, scope, encryption) |
| A2 Credentials, tokens, signing keys, peppers, data keys | High | Account takeover, forged tokens |
| A3 Authorization model (groups, mappings, permissions) | High | Privilege escalation |
| A4 Audit trail | High | Accountability and tamper evidence |
| A5 Script versions, assignments, fact snapshots, risk assessments | High (integrity) | Evidence basis of a verification must not change |
| A6 Seeded evidence (sessions, answers, findings) | Medium (integrity, labelling) | Must not be mistaken for real outcomes |
| A7 Intake pipeline and mock upstream | Medium | Injection of non-synthetic or malformed data |
| A8 Source repositories | High | Secret leakage, supply chain |

## 2. Data flows and trust boundaries

```text
[Browser SPA] --TB1 (HTTP same-origin via proxy; cookies)--> [FastAPI]
[FastAPI] --TB2 (DB connection as Call360_db_user)--> [PostgreSQL Call360_db]
[FastAPI intake] --TB3 (HTTP + service token)--> [Mock upstream :8100]
[Operator CLI: bootstrap/seed/migrate] --TB4 (same login, Call360_db_user)--> [PostgreSQL Call360_db]
[Developer workstation / repos] --TB5--> [Call360-specs | backend | frontend working trees]
```

## 3. Threats, mitigations and verification

Each threat links to a test ID in `docs/acceptance/S0_TEST_MATRIX.md` §2, or to a residual risk in §4.

| ID | STRIDE | Flow/asset | Threat | Mitigation (design reference) | Verification |
|---|---|---|---|---|---|
| TM-01 | S | TB1, A2 | Credential stuffing or brute force on `/auth/login` | Argon2id, account backoff, IP throttle, uniform errors (IDENTITY_ACCESS §3) | BE-AUTH-02, BE-AUTH-03 |
| TM-02 | S | TB1, A2 | Username enumeration through messages or timing | Uniform response, dummy hash for unknown users | BE-AUTH-02 |
| TM-03 | S | TB1, A2 | Forged or altered access JWT (alg confusion, `none`, wrong key) | EdDSA-only allowlist, `kid` pinning, `iss`/`aud`/`exp`/`nbf` checks, session lookup | BE-AUTH-04 |
| TM-04 | S | TB1, A2 | Stolen refresh token replayed | Rotation per use, HMAC storage, family revocation on reuse, idle and absolute expiry. A replay of the immediately previous generation within 10 s of rotation gets only a non-token `409` (no token minted); every other replay revokes | BE-AUTH-05, BE-AUTH-10; RR-03 |
| TM-05 | S | TB1 | Session fixation | New session ID per login; cookies set only after authentication | BE-AUTH-01 |
| TM-06 | S | TB4, A3 | Default or shared admin password | No seeded credentials; one-time bootstrap refuses when an admin exists; developer-specific secrets | BE-AUTH-09, SCAN-01 |
| TM-07 | T | TB1 | CSRF on state-changing endpoints | Session-bound double-submit token plus Origin allowlist; SameSite as depth | BE-AUTH-07, E2E-15 |
| TM-08 | T | TB1, A1 | Mass assignment (setting `created_by`, `state`, `is_synthetic`, `market_code` from the client) | Strict Pydantic models with `extra=forbid`; server-set fields not in request schemas | BE-SEC-03 |
| TM-09 | T | TB2, A1 | SQL injection through search or filter parameters | ORM and parameterised queries; bounded lengths; allowlisted sort fields | BE-SEC-04 |
| TM-10 | T | TB2/TB4, A4 | Audit rows altered or deleted | Trigger blocks UPDATE/DELETE; no API path; hash chain; chain head in evidence | BE-AUD-01, BE-AUD-02; RR-01, RR-11 |
| TM-11 | T | A5 | Published script, fact snapshot, risk assessment or session pin edited after the fact | Write-once triggers; no update APIs; superseding rows | BE-DATA-04 |
| TM-12 | T | TB3, A7 | Malicious or malformed upstream payload | Schema validation, idempotency, quarantine status, `INGEST_*` errors, no raw PII logged | BE-ING-01, BE-ING-04 |
| TM-13 | T | TB3, A7 | Non-synthetic data entering a local or test environment | `DATA_POLICY=SYNTHETIC_ONLY`: synthetic flag required, synthetic contact ranges, restricted source types, readiness check | BE-DATA-10, BE-ING-07 |
| TM-14 | T | TB5, A8 | Supply-chain compromise via dependencies | Lock files; dependency audit at each checkpoint (pip-audit, npm audit) | RR-06 |
| TM-15 | R | A4 | User denies an administrative or intake action | Audit in the same transaction, with actor snapshot, reason, before/after, correlation ID | BE-AUD-03, BE-AUD-04 |
| TM-16 | R | A6 | Seeded synthetic outcomes presented or exported as real | `record_origin=SYNTHETIC_SEED`; persistent UI labels; KPI synthetic badge; no export in S0 | E2E-05, BE-KPI-01 |
| TM-17 | I | TB1, A1 | BOLA/IDOR: guessing another market's case or policy ID | Scope predicate in every repository; 404 without existence leak; audit | BE-SEC-02, E2E-10 |
| TM-18 | I | TB1, A1 | Existence inferred from search counts, facets, suggestions or KPIs | Scope applied before aggregation, ranking and suggestion | BE-SRCH-05, BE-KPI-03 |
| TM-19 | I | TB1, A1 | Unmasked PII in responses or highlights | Server-side masking in every serializer; `pii.unmasked` granted to nobody; HMAC exact match for phone | BE-API-02, BE-SRCH-05 |
| TM-20 | I | A2 | Tokens or passwords in logs, URLs or browser storage | HttpOnly cookies; log redaction; no tokens in URLs; frontend never reads token cookies | BE-AUTH-08, E2E-15, FE-02 |
| TM-21 | I | TB5, A8 | Secrets committed to a repository or shipped in the frontend bundle | Secret scan on all three working trees and the built bundle at every checkpoint (mandatory gate) | SCAN-01, SCAN-02 |
| TM-22 | I | TB1 | XSS rendering seeded answer text or user text | React escaping; no `dangerouslySetInnerHTML`; strict CSP; escaped search highlights | BE-SEC-05, FE-01; RR-07 |
| TM-23 | I | TB1 | Search terms containing PII written to logs | Query hashing (S-14) | BE-SRCH-08 |
| TM-24 | I | TB3 | Mock upstream exposed beyond local | Mounted only in local/test, bound to loopback, service token | BE-ING-07 |
| TM-25 | D | TB1 | Resource exhaustion through large pages, long queries or refresh storms | `limit` ≤ 200, bounded query length, rate limits, single-flight refresh | BE-SEC-06, FE-02; RR-05 |
| TM-26 | D | A3 | Lock-out by abusing account lockout | Backoff instead of hard lock, per-IP throttle, admin unlock | BE-AUTH-03 |
| TM-27 | E | TB1, A3 | USER invokes admin, intake or configuration functions | Per-route permission dependency; route inventory test | BE-SEC-01, BE-SEC-02, BE-ING-06 |
| TM-28 | E | A3 | ADMIN self-grants approve, override, recording, export or unmask capability | Reserved permissions not grantable in S0; segregation independent of ADMIN | BE-IAM-03 |
| TM-29 | E | A3 | Stale privileges after disable, membership or mapping change | Per-request permission resolution and session check | BE-AUTH-06, E2E-13 |
| TM-30 | E | A3 | Admin removes the last admin or their own admin rights, leaving the system unmanaged | Last-admin guard (`409 LAST_ADMIN_GUARD`) | BE-AUD-04 |
| TM-31 | T | A5 | Case made callable despite missing script, risk or eligible contact | Blocking holds with DB check; services refuse attempts for non-callable cases | BE-DATA-09, BE-ING-08, BE-ING-10 |
| TM-32 | S/E | TB1 | Open redirect through the session-expired return path | Only validated same-origin relative paths accepted | FE-01 |

## 4. Residual risks (accepted for S0, owner visibility required)

| ID | Residual risk | Why accepted in S0 | Owner / revisit |
|---|---|---|---|
| RR-01 | Database-only audit integrity can be defeated by a DB superuser or owner, or by a backup restore (ADR-0005 §2) | Synthetic data; chain head recorded in evidence | Security owner (TBD); S5 anchoring decision |
| RR-02 | Contact-value and name encryption and the exact-match HMAC use separate local development keys stored on the workstation (S-13, D-34) | Synthetic data; exercises the code path | Security owner (TBD); S5 key management |
| RR-03 | (a) An attacker replaying a stolen previous-generation token within the 10 s window is not detected as reuse, but gains nothing: no token is issued. (b) Concurrent refreshes from different browsers or devices sharing a session beyond the window still revoke | (a) No credential is minted; the window is configurable. (b) Fails safe; the cross-tab lock removes same-browser races | Engineering; review with S1 telemetry |
| RR-04 | Local plain-HTTP loopback mode drops `Secure` and `__Host-` cookie attributes | Loopback only; the gate also tests HTTPS mode | Engineering; removed outside local |
| RR-05 | In-process rate limiter is single-instance and resets on restart | S0 runs one instance | Engineering; shared store in S5 (S-10) |
| RR-06 | Dependency vulnerabilities between checkpoints; no automated CI scanning by owner decision | Audit run at each checkpoint locally | Engineering; enterprise CI later |
| RR-07 | Frontend dependencies could introduce DOM XSS sinks | Lint rule bans `dangerouslySetInnerHTML`; CSP | Engineering |
| RR-08 | No penetration test, SAST tool or DAST in S0 | Not proportionate for local synthetic S0 | Security owner; required before production (S5) |
| RR-09 | ASVS mapping is chapter-level until a security reviewer completes requirement-level verification (ASVS matrix) | Mapping requires the official ASVS 5.0.0 text and a reviewer | Security owner (TBD); before S0 acceptance |
| RR-11 | The development app and migrations connect as `Call360_db_user`, which is a PostgreSQL superuser (automated tests use the least-privilege `call360_test_user`, D-22). An application bug such as SQL injection would therefore have full database rights, and DB-level protections (triggers) can be bypassed by the app's own login | Owner decision D-16: local synthetic data, simplicity. TM-09 mitigations (parameterised queries) still apply | Owner; before any non-synthetic data, use a non-superuser login |
| RR-12 | The development database password (`Call360_db_user`) is weak and was exposed in an earlier session's conversation and command lines (never in Git). Rotation was **explicitly deferred by the owner** at the CP0.2 development deployment (2026-11-15) | Local synthetic data only; the database listens on localhost | Owner; before any non-synthetic data or shared environment. Procedure: `CP0.2_DEV_DEPLOYMENT.md` step 4 (with step 4b to preserve the data-protection keys) |
| RR-10 | Security default parameters S-2…S-14 are proposed defaults pending security-owner approval (DEC-026) | Reasonable, standards-aligned defaults | Security owner; at CP0.0 acceptance |

## 5. Threats inherited by later stages (not mitigated in S0)

| Stage | Threats to model before implementation |
|---|---|
| S1 | Provider key exposure in browser; WebRTC/media hijack; recording tampering; replayed provider events; microphone permission abuse; transcript injection into the UI |
| S2 | Self-approval of scripts; unreviewed wording changes; assignment-rule manipulation; ambiguous fallback scripts |
| S3 | Evidence export leakage; reviewer silently editing evidence; model output treated as verdict |
| S4 | Bulk import poisoning; internal API trust; SSRF through connector configuration; queue starvation |
| S5 | OIDC misconfiguration (redirect URI, `state`/`nonce`, issuer); group overage and stale claims; key custody |
| S6 | Genesys webhook spoofing and replay; telephony fraud; media bridge exposure |
