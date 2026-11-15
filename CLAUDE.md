# Claude Code instructions — Call360-specs

**Product name: Call360. Investigation screen: Call Detail. Current stage: S0.**

This is the authoritative **specification** Git repository, one of three independent sibling repos. The other two are `../Call360-backend` and `../Call360-frontend`. Before planning or changing code, read:

1. `docs/spec/01_MASTER_BRD.md` and `docs/spec/02_CLAUDE_CODE_EXECUTION_PLAN.md`;
2. `docs/product/SCREEN_NAMING_AND_ROUTES.md`;
3. `docs/engineering/MULTI_REPO_ARCHITECTURE.md` and `docs/contracts/API_CONTRACT_POLICY.md`;
4. the applicable stage and acceptance record in `docs/acceptance/`.

## Rules

- Do not create `frontend/` or `backend/` directories in this repo. Do not nest repositories or copy application source into the specs repo.
- Preserve all requirement IDs and their test traceability. Update the BRD, register, stage plan and acceptance criteria together for approved requirement changes.
- Only the application is labelled **Call360**. The case investigation screen and its test selectors are labelled **Call Detail**. The canonical route is `/cases/:caseId`.
- Proposed AIA scripts, legal obligations, retention policies, and compliance outcomes must never be presented as already approved. Use only synthetic demo data.
- Do not implement beyond the currently approved stage. Before coding, propose ADRs, contracts, UI route map, data model, linked test matrix and cross-repo checkpoints.
- API OpenAPI is produced from FastAPI in the **backend** repo; specs owns policy for versioning and schema interpretation, not a conflicting hand-maintained executable API definition.
- All stage evidence belongs in `docs/acceptance/Sx.md`, with exact specs/backend/frontend SHAs, OpenAPI checksum, DB migration, test outputs and open risks.
- Never claim a stage has passed without integrated Playwright against actual backend/Postgres and the named AIA owner’s signoff.
- When running Claude Code from the workspace parent, verify `.git` identity, branch and `git status` in **each** repo before any commit. Never make a cross-repo atomic-commit assumption.

**Initial task:** Use Prompt 1 in `docs/spec/02_CLAUDE_CODE_EXECUTION_PLAN.md`, starting with S0 architecture and implementation checkpoints.

## v0.3 expansion — mandatory context

**v0.3 expansion (237 requirements, 55 business tests):** Read `Call360-specs/docs/process/SBQ_AS_IS_TO_BE_AND_DECISIONS.md`, `docs/data/CANONICAL_GRAIN_AND_RELATIONSHIPS.md`, `docs/product/SCRIPT_GOVERNANCE_AND_ASSIGNMENT.md`, `docs/product/SEARCH_WORKSPACE_AND_POLICY_VIEWS.md`, `docs/integrations/POLICY_PARTY_RISK_INTAKE.md`, and `docs/security/IDENTITY_AUTHORIZATION_AND_AUDIT.md` (paths relative to specs repository; use `../Call360-specs` from implementation repos). The existing AIA SBQ workflow is a working hypothesis, not an approved SOP. Keep sale-selection risk distinct from customer investment risk tolerance and compliance finding severity.

At S0 build persistent synthetic policy/sale/risk/party data, mock and manual intake, accessible secured search and local login with ADMIN/USER role mapping; enforce server-side access and audit from the start. Do not implement Genesys, real customer interfaces or real call scripts before approval. Never promise zero security defects.
