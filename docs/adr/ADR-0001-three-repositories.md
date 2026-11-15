# ADR-0001: Three independent Call360 repositories

**Status:** Project structure selected by requester; pending internal AIA architecture approval  
**Date:** 2026-11-15  
**Scope:** S0–S6

## Context

Call360 requires independently changeable product contracts, Python domain APIs, and React UI. The original v0.1 pack incorrectly assumed a single Git repository. The requester created `Call360-specs`, `Call360-backend` and `Call360-frontend` separately.

## Decision

Maintain three sibling independent Git repositories: specs is authoritative for product/business rules and stage acceptance; backend owns persistence/domain logic/FastAPI and executable OpenAPI; frontend owns React/browser transport and its API client generated from the backend OpenAPI artifact. Keep the shared workspace directory outside Git. Use linked PRs and SHA-pinned integrated tests. Never assume a multi-repository atomic commit.

## Consequences

**Benefits:** clear ownership, autonomous build/deployment, contract clarity, explicit signoffs and controlled Genesys extension.  
**Costs:** coordination of API rollout, version pinning, cross-repo E2E infrastructure, and synchronizing release records.  
**Controls:** backend API compatibility gates, generated frontend client, contract checksum, integrated Playwright against real backend/Postgres, cross-repo stage acceptance SHA tuple.

## Alternatives rejected

- Single combined monorepo: contrary to existing three-repository decision.
- Copying full BRD into each repository: would create conflicting source versions.
- Hand-maintaining DTOs in frontend: schema drift risk.

Refer to `docs/engineering/MULTI_REPO_ARCHITECTURE.md` and `docs/contracts/API_CONTRACT_POLICY.md`.
