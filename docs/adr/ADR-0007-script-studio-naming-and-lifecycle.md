# ADR-0007: Script Studio naming and script lifecycle

**Status:** Proposed (CP0.0), 2026-11-15. Owner decisions applied: D-2 (Script Studio UI, `scripts` domain and API), C-4 (lifecycle), C-26 (do not rewrite the BRD; record an explicit exception)
**Amends:** ADR-0002, for the script editor name only. All other ADR-0002 decisions stand: Call360 and **Call Detail**.
**Exceptions recorded:** EXC-001, EXC-002 in `docs/spec/APPROVED_EXCEPTIONS.md`

## Context

The pack used two names for the governed script editor:
- "Survey Studio", with `/surveys` routes and `/api/v1/surveys` endpoints, in ADR-0002, SCREEN_NAMING, API_CONTRACT_POLICY, the execution plan and the BRD;
- "Script Library / Script Studio", with `/scripts` routes, in BRD §4.4, SCRIPT_GOVERNANCE and the mockup.

It also defined four script lifecycle lists:
- BRD §6.2: `DRAFT → VALIDATION_FAILED/VALIDATED → SUBMITTED → APPROVED → PUBLISHED → RETIRED`;
- BRD §4.4 and SCRIPT_GOVERNANCE: `DRAFT → SUBMITTED_FOR_REVIEW → APPROVED → SCHEDULED → PUBLISHED → SUPERSEDED/WITHDRAWN`;
- execution plan S2: `DRAFT → SUBMITTED → APPROVED → PUBLISHED`;
- SUR-006: a "retired" state.

## Decision

### 1. Naming

| Layer | Name |
|---|---|
| UI module, navigation label, page titles, test names | **Script Studio** |
| UI routes | `/scripts`, `/scripts/:scriptFamilyId`, `/scripts/:scriptFamilyId/versions/:scriptVersionId`; assignment rules at `/assignment-rules` |
| Legacy UI routes | `/surveys` → `/scripts`; `/surveys/:id` → `/scripts/:id` (client redirect, kept through S2) |
| API | `/api/v1/scripts…`, `/api/v1/script-versions/{id}`, `/api/v1/script-assignment-rules` |
| Domain and database | `script_family`, `script_version`, `script_section`, `question_bank_item`, `question_revision`, `script_assignment`… |
| Requirement IDs | `SUR-*` IDs unchanged. Their requirements apply to Script Studio |

"Survey run" stays the domain term for one execution of a frozen script version within a session (BRD §2, grain doc). It names an execution record, not a UI module.

### 2. Script version lifecycle

`DRAFT → SUBMITTED_FOR_REVIEW → APPROVED → SCHEDULED → PUBLISHED → SUPERSEDED | WITHDRAWN`

Additional transitions:
- `APPROVED → PUBLISHED` directly, when the effective date is now;
- `SUBMITTED_FOR_REVIEW → DRAFT` (amendment requested);
- `SCHEDULED → WITHDRAWN` (withdrawn before activation).

Rules:
- Only `DRAFT` content is editable. Validation is a draft attribute, `validation_status ∈ {NOT_VALIDATED, VALID, INVALID}`, not a lifecycle state. A draft must be `VALID` to be submitted (S2).
- **Published script versions are immutable** (ADR-0005 §3). Changes create a new version. Rollback is a new publish event.
- `SUPERSEDED` versions are replaced by a later published version for the same scope. `WITHDRAWN` versions cannot be selected for new cases. Both stay viewable, and both stay referenced by historic sessions.
- The BRD §6.2 legacy states map as follows:

  | Legacy state | New treatment |
  |---|---|
  | `VALIDATION_FAILED` | `DRAFT` with `validation_status=INVALID` |
  | `VALIDATED` | `DRAFT` with `validation_status=VALID` |
  | `SUBMITTED` | `SUBMITTED_FOR_REVIEW` |
  | `RETIRED` | `SUPERSEDED` (replaced) or `WITHDRAWN` (pulled) |

- The reviewer or approver must be a different principal from the author. This applies regardless of `ADMIN` membership (S2, T-16, T-50).

### 3. Stage application

- **S0:** the lifecycle is seeded and displayed read-only. There is at least one version in each of `PUBLISHED`, `SUPERSEDED`, `DRAFT` and `WITHDRAWN`. No transition API exists.
- **S2:** transitions, maker-checker, diff and publication are implemented.

## Consequences

- The BRD is not rewritten. EXC-001 and EXC-002 give this ADR precedence over the specific BRD lines named there, and over nothing else.
- The validator enforces the exceptions register: a legacy term outside an allowed file fails.
- `SCREEN_NAMING_AND_ROUTES.md`, `API_CONTRACT_POLICY.md`, `SEARCH_WORKSPACE_AND_POLICY_VIEWS.md`, `SCRIPT_GOVERNANCE_AND_ASSIGNMENT.md` and `MULTI_REPO_ARCHITECTURE.md` are updated to use Script Studio.
- `Call360-frontend/CLAUDE.md` and the workspace `CLAUDE.md` still say "Survey Studio". They are outside `Call360-specs`, so updating them needs separate authorisation (C-24). Until then, this ADR takes precedence.
