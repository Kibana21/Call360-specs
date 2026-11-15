# Stage acceptance evidence

This directory is the authoritative record of stage results across the **three** Call360 repos. Create `S0.md` from `S0_TEMPLATE.md` and use a similar structure for `S1.md`–`S6.md`. A template is not an acceptance statement.

Each acceptance record must state: owner approval, date, linked requirement IDs, implementation scope, architecture/contract changes, exact specs/backend/frontend commits, OpenAPI SHA-256, database migration revision, environment, test commands, local test-run and E2E output references (no CI in local development; see MULTI_REPO_ARCHITECTURE §9), unresolved defects and explicit go/no-go. Do not mark a gate PASS merely because UI screenshots were produced.


Checkpoint records (`CP0.0.md`, `CP0.1A.md`, `CP0.1B-1.md` … `CP0.1B-3.md`, then `CP0.2.md` … `CP0.6.md`) hold each checkpoint's decisions, acceptance criteria and evidence; raw outputs go under `evidence/<checkpoint>/`. `S0_TEST_MATRIX.md` is the S0 requirement-to-test traceability source (the register's `test_id` column is intentionally left empty, decision C-27). Uncommitted evidence uses the base Git SHA plus `scripts/evidence_manifest.py` output (ADR-0003 §6).
