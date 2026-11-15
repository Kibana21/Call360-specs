# Call360 specification pack changelog

## v0.4-draft — CP0.0 specification foundation (15 November 2026, pending owner acceptance)

- Added the Stage 0 specification set:
  - ADR-0003…0008 and an ADR index;
  - `APPROVED_EXCEPTIONS.md`;
  - `S0_DATA_MODEL.md` and `S0_IDENTITY_ACCESS_DESIGN.md`;
  - `S0_API_CATALOGUE.md`, `S0_SCREEN_SPEC.md` and `S0_KPI_DEFINITIONS.md`;
  - `THREAT_MODEL_S0.md` and `ASVS_S0_CONTROL_MATRIX.md`;
  - `S0_TEST_MATRIX.md`;
  - `S0_IMPLEMENTATION_PLAN.md`;
  - `CP0.0.md` and `S0.md`.
- Recorded owner decisions:
  - Script Studio naming as explicit exception EXC-001;
  - script lifecycle (EXC-002);
  - mockup navigation structure (EXC-003);
  - auditable blocking holds;
  - per-KPI eligibility, materiality, SLA-exemption and cohort rules;
  - bootstrap and developer credentials;
  - base SHA plus manifest evidence;
  - no permanent `is_synthetic` constraint.
- Updated supporting documents for consistency: naming and routes, search, script governance, API contract policy, canonical grain notes, multi-repo local-development mode, execution-plan overlay, acceptance template.
- Extended `scripts/validate_specs.py` with exception-aware terminology checks and CP0.0 traceability checks. Added `scripts/evidence_manifest.py`.
- **Unchanged:** master BRD, requirements register and requirement counts. 237 requirement IDs and 55 business tests preserved; no requirement wording, stage or priority changed.

## v0.3.1 — Repository capitalization correction

- Corrected exact independent Git repository names to `Call360-specs`, `Call360-backend`, and `Call360-frontend` in documentation, requirement ownership, Claude instructions, specification checks, and installer paths.
- No business requirement scope or identifiers changed from v0.3.

## v0.3 — 15 November 2026

- Retained all 99 prior functional requirements; introduced 138 requirements for party/policy-sale records, SBQ selection-risk, versioned script/expected-answer governance, intake, search, local identity + future SSO, token/session security, regulatory change workflows and application administration. Total: **237 unique requirements**.
- Defined distinct grains for party, policy, sale event, source fact snapshot, risk assessment, callback obligation, script assignment, attempt, session, question/answer evidence and findings.
- Documented SBQ present-day process as an **unverified working hypothesis**, with owner-validation checklist; no AIA internal SOP or MAS-specific exact wording assumed.
- Added dedicated contracts for process, canonical data model, script lifecycle, manual/mock internal API intake, search, identity, authorization and audit.
- Updated S0–S6 milestones, stage checklists, Claude instructions, negative/security tests and expected evidence so the extended scope is implemented intentionally rather than as ungoverned UI placeholders.
- Kept **Call360** for the product and **Call Detail** for the case investigation screen; preserved three independent repository boundaries.

## v0.2 — 15 November 2026

- Renamed product consistently to **Call360**, preserving a distinction from the case investigation UI screen **Call Detail**.
- Replaced legacy “Call 360” screen labels in the master BRD, execution plan, requirement register, prompts, UI acceptance and data/evidence language.
- Replaced monorepo repository layout with three sibling independent Git repos: `Call360-specs`, `Call360-backend`, `Call360-frontend`.
- Added authoritative repo boundaries, cross-repo OpenAPI generation/client drift controls, coordinated PR/CI sequencing, stage gate SHA tuple and test evidence.
- Added **separate `CLAUDE.md` for each repo**, route/name contract, API contract policy, multi-repo operating guide, stage acceptance template and pack installation guidance.
- Preserved all **99 original requirement IDs** and all **30 golden business test scenarios**; added CSV implementing repository/evidence mapping columns.
- Corrected Genesys interface wording to Audio Connector WebSocket; does not change future integration scope.

## v0.1 — 15 November 2026

- Original AIA callback platform master BRD and staged implementation plan.
