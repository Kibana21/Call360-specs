# CP0.6 requirement trace (generated from S0_TEST_MATRIX.md against the test code of the two passing gate runs)

Result rules: PASS = every mapped test ID is present in a suite that passed in both gate runs; DEFERRED = owner-approved deferral; PENDING = needs a named human reviewer.

| Requirement | Class | Tests | Result | Located in |
|---|---|---|---|---|
| APP-001 | F | E2E-01, E2E-17, FE-01 | PASS | E2E-01: e2e/auth.spec.ts; E2E-17: e2e/a11y.spec.ts; FE-01: src/App.test.tsx, src/features/OverviewPage.test.tsx |
| APP-002 | F | BE-KPI-01, BE-KPI-04, BE-KPI-05, BE-KPI-06, E2E-02 | PASS | BE-KPI-01: tests/test_dashboard.py; BE-KPI-04: tests/test_dashboard.py; BE-KPI-05: tests/test_domain_seed.py; BE-KPI-06: tests/test_dashboard.py; E2E-02: e2e/f2-checks.ts, e2e/overview.spec.ts |
| APP-003 | F | BE-DATA-03, BE-API-01, E2E-03 | PASS | BE-DATA-03: tests/test_domain_seed.py; BE-API-01: tests/test_case_detail.py, tests/test_register.py; E2E-03: e2e/f3-checks.ts |
| APP-004 | F | BE-KPI-02, E2E-02 | PASS | BE-KPI-02: tests/test_register.py; E2E-02: e2e/f2-checks.ts, e2e/overview.spec.ts |
| APP-005 | F | BE-SRCH-01, BE-SEC-02, E2E-06 | PASS | BE-SRCH-01: tests/test_register.py; BE-SEC-02: tests/test_case_detail.py, tests/test_intake.py; E2E-06: e2e/f4-checks.ts |
| APP-006 | F | BE-SRCH-04, BE-SRCH-07, E2E-07, E2E-08 | PASS (part deferred) | BE-SRCH-04: tests/test_register.py; BE-SRCH-07: saved views (deferred at F2); E2E-07: e2e/f2-checks.ts; E2E-08: saved views (deferred at F2) |
| CASE-001 | F | BE-DATA-03, BE-API-02, E2E-03 | PASS | BE-DATA-03: tests/test_domain_seed.py; BE-API-02: tests/test_policies.py; E2E-03: e2e/f3-checks.ts |
| CASE-002 | F | BE-DATA-04, BE-ING-05, E2E-19 | PASS (part deferred) | BE-DATA-04: tests/test_domain_seed.py; BE-ING-05: CP0.4b remainder (corrections); E2E-19: CP0.4b remainder (corrections) |
| SUR-001 | D | BE-API-04, E2E-09 | PASS | BE-API-04: tests/test_scripts.py; E2E-09: e2e/f6-checks.ts |
| GOV-001 | F | BE-DATA-10, BE-DATA-14, BE-ING-07, SCAN-01 | PASS (part deferred) | BE-DATA-10: tests/test_db_isolation.py, tests/test_domain_seed.py; BE-DATA-14: tests/conftest.py, tests/test_db_isolation.py; BE-ING-07: CP0.4b remainder (mock upstream); SCAN-01: backend secret scan (evidence/CP0.6/backend_secret_scan.txt) |
| GOV-002 | F | BE-SEC-01, E2E-01 | PASS | BE-SEC-01: tests/test_authz_admin.py; E2E-01: e2e/auth.spec.ts |
| PARTY-001 | F | BE-DATA-03, E2E-06 | PASS | BE-DATA-03: tests/test_domain_seed.py; E2E-06: e2e/f4-checks.ts |
| PARTY-002 | F | BE-DATA-03 | PASS | BE-DATA-03: tests/test_domain_seed.py |
| PARTY-003 | P | BE-DATA-08 | PASS | BE-DATA-08: tests/test_domain_cases.py, tests/test_domain_party.py |
| PARTY-004 | P | BE-ING-08, BE-DATA-03, BE-DATA-09, E2E-11 | PASS | BE-ING-08: tests/test_intake.py; BE-DATA-03: tests/test_domain_seed.py; BE-DATA-09: tests/test_domain_cases.py, tests/test_domain_seed.py; E2E-11: e2e/cp04b-checks.ts |
| PARTY-005 | F | BE-API-02, BE-SRCH-05, E2E-06 | PASS | BE-API-02: tests/test_policies.py; BE-SRCH-05: tests/test_register.py; E2E-06: e2e/f4-checks.ts |
| POL-001 | F | BE-DATA-07 | PASS | BE-DATA-07: tests/test_domain_seed.py |
| POL-002 | F | BE-API-02 | PASS | BE-API-02: tests/test_policies.py |
| POL-003 | F | BE-API-02 | PASS | BE-API-02: tests/test_policies.py |
| POL-004 | F | E2E-06 | PASS | E2E-06: e2e/f4-checks.ts |
| POL-005 | F | BE-DATA-05, BE-ING-03, E2E-06 | PASS | BE-DATA-05: tests/test_domain_schema.py; BE-ING-03: tests/test_intake.py; E2E-06: e2e/f4-checks.ts |
| POL-006 | F | BE-DATA-04 | PASS | BE-DATA-04: tests/test_domain_seed.py |
| POL-007 | F | BE-ING-03, BE-ING-05, E2E-11, E2E-19 | PASS (part deferred) | BE-ING-03: tests/test_intake.py; BE-ING-05: CP0.4b remainder (corrections); E2E-11: e2e/cp04b-checks.ts; E2E-19: CP0.4b remainder (corrections) |
| RISK-001 | F | BE-DATA-06, E2E-06 | PASS | BE-DATA-06: tests/test_domain_risk.py, tests/test_domain_seed.py; E2E-06: e2e/f4-checks.ts |
| RISK-002 | D | BE-API-03, E2E-06 | PASS | BE-API-03: tests/test_risk.py; E2E-06: e2e/f4-checks.ts |
| RISK-003 | D | BE-DATA-11 | PASS | BE-DATA-11: tests/test_domain_seed.py |
| RISK-004 | D | BE-API-03, E2E-06 | PASS | BE-API-03: tests/test_risk.py; E2E-06: e2e/f4-checks.ts |
| RISK-005 | D | BE-API-03, E2E-03, E2E-06, E2E-11 | PASS | BE-API-03: tests/test_risk.py; E2E-03: e2e/f3-checks.ts; E2E-06: e2e/f4-checks.ts; E2E-11: e2e/cp04b-checks.ts |
| RISK-006 | P | BE-CFG-01, BE-DATA-13, BE-API-03 | PASS | BE-CFG-01: tests/test_config.py; BE-DATA-13: tests/test_domain_risk.py, tests/test_domain_seed.py; BE-API-03: tests/test_risk.py |
| SCR-001 | D | BE-DATA-04, BE-API-04, E2E-09 | PASS | BE-DATA-04: tests/test_domain_seed.py; BE-API-04: tests/test_scripts.py; E2E-09: e2e/f6-checks.ts |
| SCR-002 | D | BE-DATA-12, E2E-09 | PASS | BE-DATA-12: tests/test_domain_seed.py; E2E-09: e2e/f6-checks.ts |
| SCR-003 | F | BE-API-04, E2E-09 | PASS | BE-API-04: tests/test_scripts.py; E2E-09: e2e/f6-checks.ts |
| SCR-004 | D | BE-API-04, BE-DATA-04, E2E-03 | PASS | BE-API-04: tests/test_scripts.py; BE-DATA-04: tests/test_domain_seed.py; E2E-03: e2e/f3-checks.ts |
| SCR-005 | D | BE-DATA-03, E2E-09 | PASS | BE-DATA-03: tests/test_domain_seed.py; E2E-09: e2e/f6-checks.ts |
| ING-001 | F | BE-ING-01, E2E-12 | DEFERRED | BE-ING-01: CP0.4b remainder (mock upstream); E2E-12: CP0.4b remainder (mock sync) |
| ING-002 | F | BE-ING-03, BE-ING-10, E2E-11 | PASS | BE-ING-03: tests/test_intake.py; BE-ING-10: tests/test_intake.py; E2E-11: e2e/cp04b-checks.ts |
| ING-003 | F | BE-DATA-05, BE-ING-03 | PASS | BE-DATA-05: tests/test_domain_schema.py; BE-ING-03: tests/test_intake.py |
| ING-004 | F | BE-ING-04, E2E-11 | PASS | BE-ING-04: tests/test_intake.py; E2E-11: e2e/cp04b-checks.ts |
| SEARCH-001 | F | BE-SRCH-01, E2E-06 | PASS | BE-SRCH-01: tests/test_register.py; E2E-06: e2e/f4-checks.ts |
| SEARCH-002 | F | BE-SRCH-03, E2E-02, E2E-07 | PASS | BE-SRCH-03: tests/test_register.py; E2E-02: e2e/f2-checks.ts, e2e/overview.spec.ts; E2E-07: e2e/f2-checks.ts |
| SEARCH-003 | F | BE-SRCH-02 | PASS | BE-SRCH-02: tests/test_register.py |
| SEARCH-004 | F | BE-SRCH-07, E2E-08 | DEFERRED | BE-SRCH-07: saved views (deferred at F2); E2E-08: saved views (deferred at F2) |
| SEARCH-005 | F | BE-SRCH-04, E2E-07 | PASS | BE-SRCH-04: tests/test_register.py; E2E-07: e2e/f2-checks.ts |
| SEARCH-006 | F | BE-SRCH-05, BE-KPI-03, BE-SEC-02 | PASS | BE-SRCH-05: tests/test_register.py; BE-KPI-03: tests/test_dashboard.py; BE-SEC-02: tests/test_case_detail.py, tests/test_intake.py |
| SEARCH-007 | F | BE-SRCH-06, E2E-14 | PASS | BE-SRCH-06: tests/test_register.py; E2E-14: e2e/cp06-checks.ts |
| IAM-001 | F | BE-AUTH-01, E2E-01 | PASS | BE-AUTH-01: tests/test_auth.py; E2E-01: e2e/auth.spec.ts |
| IAM-002 | F | BE-AUTH-09, SCAN-01, E2E-01 | PASS | BE-AUTH-09: tests/test_authz_admin.py; SCAN-01: backend secret scan (evidence/CP0.6/backend_secret_scan.txt); E2E-01: e2e/auth.spec.ts |
| IAM-003 | F | BE-IAM-01 | PASS | BE-IAM-01: tests/test_authz_admin.py |
| IAM-004 | F | BE-IAM-02, E2E-13 | PASS | BE-IAM-02: tests/test_authz_admin.py, tests/test_scope.py; E2E-13: e2e/cp01b3-checks.ts, e2e/permissions.spec.ts |
| IAM-005 | F | BE-SEC-01, BE-SEC-02, E2E-10 | PASS | BE-SEC-01: tests/test_authz_admin.py; BE-SEC-02: tests/test_case_detail.py, tests/test_intake.py; E2E-10: e2e/permissions.spec.ts |
| IAM-006 | F | BE-AUTH-04 | PASS | BE-AUTH-04: tests/test_tokens.py |
| IAM-007 | F | BE-AUTH-05, BE-AUTH-10 | PASS | BE-AUTH-05: tests/test_auth.py; BE-AUTH-10: tests/test_auth.py |
| IAM-008 | F | BE-AUTH-07, BE-AUTH-08, FE-02, E2E-15 | PASS | BE-AUTH-07: tests/test_auth.py; BE-AUTH-08: tests/test_auth.py; FE-02: src/api/session.test.ts; E2E-15: e2e/auth.spec.ts |
| IAM-009 | F | BE-AUTH-06, E2E-13 | PASS | BE-AUTH-06: tests/test_admin_access.py, tests/test_auth.py; E2E-13: e2e/cp01b3-checks.ts, e2e/permissions.spec.ts |
| IAM-010 | F | BE-AUD-04, E2E-13 | PASS | BE-AUD-04: tests/test_admin_access.py, tests/test_authz_admin.py; E2E-13: e2e/cp01b3-checks.ts, e2e/permissions.spec.ts |
| IAM-011 | F | BE-AUD-03, BE-AUTH-08 | PASS | BE-AUD-03: tests/test_authz_admin.py; BE-AUTH-08: tests/test_auth.py |
| SEC-001 | F | DOC-01 | PASS | DOC-01: THREAT_MODEL_S0.md (accepted with CP0.0) |
| SEC-002 | F | BE-SEC-03, BE-SEC-04 | PASS | BE-SEC-03: tests/test_authz_admin.py; BE-SEC-04: tests/test_stage0_acceptance.py |
| SEC-003 | F | BE-SEC-05, BE-AUTH-07, E2E-15 | PASS | BE-SEC-05: tests/test_authz_admin.py; BE-AUTH-07: tests/test_auth.py; E2E-15: e2e/auth.spec.ts |
| SEC-004 | F | BE-SEC-02, BE-SRCH-05 | PASS | BE-SEC-02: tests/test_case_detail.py, tests/test_intake.py; BE-SRCH-05: tests/test_register.py |
| SEC-005 | F | SCAN-01, SCAN-02 | PASS | SCAN-01: backend secret scan (evidence/CP0.6/backend_secret_scan.txt); SCAN-02: frontend secret scan incl. bundle (evidence/CP0.6/frontend_checks.txt) |
| SEC-006 | F | BE-AUTH-03, BE-SEC-06 | PASS | BE-AUTH-03: tests/test_auth.py; BE-SEC-06: tests/test_authz_admin.py |
| SEC-007 | F | BE-AUD-01, BE-AUD-02 | PASS | BE-AUD-01: tests/test_audit.py; BE-AUD-02: tests/test_audit.py |
| SEC-008 | F | DOC-02 | PENDING | DOC-02: ASVS_S0_CONTROL_MATRIX.md: requirement-level completion by the security reviewer (handoff docs/security/SEC-008_REVIEW_HANDOFF.md) |
| REG-001 | P | BE-API-05, E2E-09 | PASS | BE-API-05: tests/test_scripts.py; E2E-09: e2e/f6-checks.ts |
| REG-002 | D | BE-API-05, E2E-09 | PASS | BE-API-05: tests/test_scripts.py; E2E-09: e2e/f6-checks.ts |
| ADMIN-001 | F | E2E-13 | PASS | E2E-13: e2e/cp01b3-checks.ts, e2e/permissions.spec.ts |
| ADMIN-002 | P | BE-AUD-04, BE-ING-05 | PASS (part deferred) | BE-AUD-04: tests/test_admin_access.py, tests/test_authz_admin.py; BE-ING-05: CP0.4b remainder (corrections) |
| ADMIN-003 | F | BE-IAM-03 | PASS | BE-IAM-03: tests/test_authz_admin.py |
| ADMIN-004 | F | BE-CFG-01, BE-CFG-02, BE-CFG-03, E2E-20 | PASS | BE-CFG-01: tests/test_config.py; BE-CFG-02: tests/test_config.py; BE-CFG-03: tests/test_config.py; E2E-20: e2e/config.spec.ts |

**Totals (70 requirements):** DEFERRED 2, PASS 62, PASS (part deferred) 5, PENDING 1
