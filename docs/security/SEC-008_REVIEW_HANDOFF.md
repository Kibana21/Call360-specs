# SEC-008 — Stage 0 security review handoff

**Status:** PENDING the designated security reviewer (name not yet assigned, C-20). Prepared 2026-11-17 after CP0.6
technical verification. **This is not a certification.** Engineering has not self-certified any ASVS requirement;
only the reviewer can complete SEC-008.

## 1. What needs review

`ASVS_S0_CONTROL_MATRIX.md` maps OWASP ASVS 5.0 Level 2 (plus selected L3) to Stage 0 controls **at chapter level**.
SEC-008 requires the reviewer to verify it **at requirement level** against the official ASVS 5.0.0 text, assign
PASS / FAIL / N/A per requirement with evidence, and name remediation owners. Chapters not applicable in Stage 0:
V5 File Handling, V10 OAuth/OIDC, V17 WebRTC (re-assess in S1/S4/S5).

## 2. Existing evidence (local, synthetic data, real FastAPI + PostgreSQL)

| Area (ASVS) | Automated evidence | Where |
|---|---|---|
| V1 Encoding, V2 Validation | Parameterised SQL; injection payloads in every search and filter inert (BE-SEC-04, BE-SEC-03); strict request schemas; intake validation, preview and idempotency (BE-ING-02/04) | `tests/test_stage0_acceptance.py`, `test_authz_admin.py`, `test_intake.py` |
| V3 Frontend | Security headers and CSP (BE-SEC-05); no tokens in browser storage, validated return paths (FE-02) | `test_authz_admin.py`, `src/api/session.test.ts` |
| V4 API | Generated OpenAPI with drift check (BE-CT-01); error envelope with correlation ID (exercised throughout; not separately tagged BE-API-07); page limits (BE-SEC-06) | `test_contract.py`, `evidence/CP0.6/backend_static.txt` |
| V6 Authentication | Argon2id, password policy, uniform errors, backoff and IP throttle, bootstrap without defaults (BE-AUTH-01/02/03/09); one-time password must be changed before any permissioned action (CP0.1B-3) | `test_auth.py`, `test_admin_access.py` |
| V7 Sessions | Rotation and reuse detection, concurrent-refresh handling (BE-AUTH-05/10); logout, admin revoke, disable, password reset effective next request (BE-AUTH-06, E2E-13) | `test_auth.py`, `test_admin_access.py`, `e2e/cp01b3-checks.ts` |
| V8 Authorization | Every route declares access (BE-SEC-01); Singapore-only object scope with identical audited 404s across every route (BE-SEC-02); reserved permissions not grantable, last-admin and self-demotion guards (BE-IAM-03) | `test_authz_admin.py`, `test_stage0_acceptance.py`, `test_admin_access.py` |
| V9, V11 Tokens and crypto | EdDSA-only JWT with full claim checks (BE-AUTH-04); HMAC-stored refresh tokens; AES-GCM contact encryption with HMAC lookup tokens | `test_tokens.py`, `test_auth.py`, `test_register.py` |
| V13 Configuration | `DATA_POLICY=SYNTHETIC_ONLY` and readiness guard (BE-DATA-10); secret scans of both repositories and the frontend bundle (SCAN-01/02); `npm audit --omit=dev`: 0 vulnerabilities (2026-11-17) | `test_db_isolation.py`, `evidence/CP0.6*/` |
| V14 Data protection | Server-side masking; contact values encrypted; search terms logged only as hashes (BE-SRCH-08); no secret or personal value in responses, audit events or the development server log | `test_register.py`, `test_stage0_acceptance.py`, `evidence/CP0.6/dev_log_scan.txt` |
| V16 Logging | Append-only hash-chained audit, DB triggers block update/delete, chain verified in test and development (BE-AUD-01…04); operational audit view scoped to Singapore with the full ledger retained (CP0.6-F1) | `test_audit.py`, `test_stage0_acceptance.py`, `evidence/CP0.6/dev_database.txt` |

Gate: two runs on freshly reset `call360_test`, 313 backend + 16 Playwright each, plus CP0.6-F1 rerun
(`evidence/CP0.6/gate_run_*.txt`, `evidence/CP0.6-F1/checks.txt`).

## 3. Controls requiring manual verification by the reviewer

1. Requirement-level ASVS 5.0.0 mapping (RR-09) — the core of SEC-008.
2. Security default parameters S-2…S-14 (token lifetimes, lockout, rate limits, cookie modes) — approval (RR-10).
3. HTTPS mode cookie attributes and HSTS (E2E-15) on a TLS deployment; local runs use loopback HTTP (RR-04).
4. Python dependency audit (`pip-audit` is not installed locally; not run) and a repeat `npm audit` (RR-06).
5. CSP and header review in a browser against the built bundle; DOM XSS sink review of dependencies (RR-07).
6. Key custody: local development keys for signing, encryption and HMAC (RR-02); production custody is S5.
7. No penetration test, SAST or DAST was performed in Stage 0 (RR-08) — decide whether any is required before S1 pilots.

## 4. Known findings and gaps (not fixed in Stage 0)

- **RR-11:** the development application connects as a PostgreSQL superuser (tests use a least-privilege role).
- **RR-12:** the development database password is weak and was exposed in an earlier session; rotation deferred by the owner.
- **RR-01:** database-only audit integrity can be defeated by a database owner or a backup restore.
- **RR-05:** single-instance in-memory rate limiter.
- **Audit scope (resolved, CP0.6-F1):** the operational audit view now follows the Singapore-only policy; the complete
  ledger, including Malaysian-fixture events, is retained and verified but has no separate investigator view in S0.
- No vulnerability is claimed absent; only the controls above were tested.

## 5. Outstanding approval

| Role | Name | Decision | Date |
|---|---|---|---|
| Security reviewer (SEC-008) | TBD | PENDING | — |
