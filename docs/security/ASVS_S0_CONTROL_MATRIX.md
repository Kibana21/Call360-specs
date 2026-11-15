# Call360 — Stage 0 OWASP ASVS 5.0 control-to-test matrix

**Status:** CP0.0 draft, 2026-11-15 · **Requirement:** SEC-008
**Baseline:** OWASP ASVS 5.0 Level 2, plus risk-selected Level 3 controls (marked L3).
**Nature of this document:** this matrix is a **design and verification plan**. It is **not evidence of completed security certification** or of ASVS compliance. A control counts as verified only when its tests have run and passed against the real stack and the result is recorded in `S0.md` (CP0.6). Security parameters (S-2…S-14) and enterprise security settings remain **provisional** until formally validated by the security owner.
**Granularity:** this matrix maps at **chapter level** to Call360 controls and tests. Requirement-level verification against the official ASVS 5.0.0 text, with exact requirement identifiers, must be completed by a named security reviewer before S0 acceptance (residual risk RR-09). This document does not quote ASVS requirement numbers, to avoid misattribution.
**Remediation owners:** roles below. Named individuals are to be assigned at CP0.0 acceptance (C-20).

| ASVS 5.0 chapter | S0 applicability | Call360 controls (design reference) | Tests | Remediation owner | Residual / note |
|---|---|---|---|---|---|
| V1 Encoding and Sanitization | Applicable | Output encoding by React; no raw HTML rendering; parameterised SQL; escaped search highlights | BE-SEC-04, FE-01 | Frontend + backend engineering | RR-07 |
| V2 Validation and Business Logic | Applicable | Strict Pydantic request schemas; bounded inputs; state-machine and hold constraints in the DB; intake validation and preview; idempotency keys | BE-SEC-03, BE-DATA-09, BE-ING-04, BE-ING-02 | Backend engineering | — |
| V3 Web Frontend Security | Applicable | CSP, `frame-ancestors 'none'`, nosniff, referrer policy, cookie attributes; no tokens in storage; validated return paths | BE-SEC-05, E2E-15, FE-02 | Frontend engineering | RR-04 (local HTTP) |
| V4 API and Web Service | Applicable | `/api/v1` versioning; error envelope; method and content-type enforcement; generated OpenAPI; pagination limits | BE-API-07, BE-CT-01, BE-SEC-06 | Backend engineering | — |
| V5 File Handling | Not applicable in S0 | No file upload or download in S0 (bulk import is S4; media is S1) | — | — | Re-assess S1/S4 |
| V6 Authentication | Applicable | Argon2id; password policy; uniform errors; throttling and backoff; bootstrap without default credentials; no role switching | BE-AUTH-01, BE-AUTH-02, BE-AUTH-03, BE-AUTH-09 | Backend engineering | RR-10 (policy approval) |
| V7 Session Management | Applicable | Server-side `auth_session` authoritative; regeneration on login; idle and absolute expiry; logout and admin revocation; disable invalidates | BE-AUTH-05, BE-AUTH-06, E2E-13 | Backend engineering | RR-03 |
| V8 Authorization | Applicable (L3 for segregation) | Route permission inventory; per-object market scope; scope before aggregation; reserved permissions not grantable; last-admin guard | BE-SEC-01, BE-SEC-02, BE-SRCH-05, BE-KPI-03, BE-IAM-03 | Backend engineering | — |
| V9 Self-contained Tokens | Applicable | EdDSA-only allowlist; `kid`; `iss`/`aud`/`exp`/`nbf`/`iat`/`jti`/`typ`; token-type confusion rejected; session check on every use | BE-AUTH-04 | Backend engineering | — |
| V10 OAuth and OIDC | Not applicable in S0 | IdP abstraction only; OIDC in S5 | — | — | Re-assess S5 |
| V11 Cryptography | Applicable | Ed25519 signing; HMAC-SHA-256 refresh storage with pepper; AES-GCM contact encryption; SHA-256 content hashes; keys outside git | BE-AUTH-04, BE-AUTH-05, SCAN-01 | Backend engineering | RR-02 |
| V12 Secure Communication | Partially applicable | Loopback HTTP locally; HTTPS mode with HSTS tested in the gate | E2E-15 | Engineering | RR-04 |
| V13 Configuration | Applicable | Environment-based settings; `DATA_POLICY=SYNTHETIC_ONLY`; mock upstream only in local/test; dependency lock files; secret scanning | BE-DATA-10, BE-ING-07, SCAN-01, SCAN-02 | Backend + frontend engineering | RR-06 |
| V14 Data Protection | Applicable | Server-side masking; `pii.unmasked` not granted; encrypted contact values; no PII in logs; `Cache-Control: no-store` | BE-API-02, BE-SRCH-05, BE-SRCH-08, BE-AUTH-08 | Backend engineering | — |
| V15 Secure Coding and Architecture | Applicable | Layered modules; transport-independent domain; threat model; immutable evidence records; dependency audit | DOC-01, BE-DATA-04 | Engineering lead | RR-06 |
| V16 Security Logging and Error Handling (L3 for audit integrity) | Applicable | Append-only hash-chained audit; security events; correlation IDs; generic errors without stack traces | BE-AUD-01, BE-AUD-02, BE-AUD-03, BE-API-07 | Backend engineering | RR-01 |
| V17 WebRTC | Not applicable in S0 | No media in S0 (S1) | — | — | Re-assess S1 |

## Verification at stage acceptance

- CP0.6 records each test result against this matrix in `docs/acceptance/S0.md`.
- A control area is reported as **verified** only when its tests ran and passed against the real local stack. Otherwise it is reported as **not verified**, with the reason.
- Before S0 acceptance, the security reviewer replaces the chapter-level rows with requirement-level entries, or records explicit deferrals.
