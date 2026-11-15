## v0.3.1 — Repository capitalization correction

- Corrected exact independent Git repository names to `Call360-specs`, `Call360-backend`, and `Call360-frontend` in documentation, requirement ownership, Claude instructions, specification checks, and installer paths.
- No business requirement scope or identifiers changed from v0.3.

# Call360 specification pack changelog

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
