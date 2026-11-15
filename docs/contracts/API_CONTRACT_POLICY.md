# Call360 — API contract ownership, generated clients and compatibility

**Contract ID:** CALL360-CONTRACT-001 | **Status:** proposed for S0 ADR acceptance

## Source of truth

`Call360-backend` FastAPI/Pydantic route schemas are the **executable API source of truth**. The backend generates a deterministic `contracts/generated/openapi.json`. The official product **meaning**, supported workflows, field definitions, evidence semantics and compatibility rules live in `Call360-specs` (BRD + this document + ADRs), not as a second competing generated OpenAPI source.

`Call360-frontend` generates its TypeScript client from a **pinned backend artifact**. A locally generated client or manually edited TypeScript interface cannot override backend contracts. Contract checksum is recorded in PR and acceptance evidence.

## Versioned REST contract (initial proposal)

- Prefix: `/api/v1`; authenticated, scoped JSON APIs with standard errors `{code,message,correlation_id,retryable}`.
- `GET /api/v1/dashboard/summary`
- `GET /api/v1/cases?status=&...` (server-side search, filters, page, order)
- `GET /api/v1/cases/{case_id}` (case summary and authorized policy snapshot)
- `GET /api/v1/cases/{case_id}/attempts`
- `GET /api/v1/cases/{case_id}/timeline`
- `GET /api/v1/attempts/{attempt_id}`
- `GET /api/v1/sessions/{session_id}`
- `GET /api/v1/sessions/{session_id}/transcript` (including evidence status)
- `GET /api/v1/sessions/{session_id}/media` (authorized metadata; no public object URLs)
- `GET /api/v1/surveys` and `GET /api/v1/surveys/{survey_id}/versions`
- `GET /api/v1/health/ready` and role/scope demo endpoints as approved
- `POST /api/v1/demo/sessions` from S1, idempotent; provider secrets never exposed

These paths are proposals until executable schemas/tests land. Keep a single owner of definitions and record changes in an ADR. The `/cases/{case_id}` endpoint corresponds to the **Call Detail** React route `/cases/:caseId`; they are not the same URL space.

## Wire contract requirements

- IDs are opaque stable strings; timestamps UTC ISO 8601 with offsets; states are documented enums; missing/unknown evidence is explicitly represented.
- Request and response schemas must be typed and generated. Sensitive fields masked or omitted by server-side authorization, not simply hidden in React.
- Mutations require idempotency key, actor, reason/correlation where relevant. No unapproved side effects or call completion on timeouts.
- Add request trace/correlation IDs and pagination metadata. Report distinct case vs attempt vs session metrics; denominators must not be conflated.
- Audio is not serialized inside generic JSON records; media endpoints return metadata and short-lived, authorized access only.
- Preserve raw provider events separately from normalized business events. Evidence status must not imply the audio was heard just because generated.

## Compatibility and publication

1. Backend PR: generate `openapi.json` from clean app bootstrap and run checksum/stability test.
2. Consumer check: compare current artifact with the frontend's pinned artifact; classify as additive, behavior change or breaking.
3. Additive deploy: backend first with old-client support, frontend next. Breaking change: ADR, versioned endpoint/field support, rollout and rollback plan.
4. Frontend PR: regenerate client deterministically, no manual DTO drift, compile tests and real API E2E.
5. Acceptance: record backend SHA, frontend SHA, specs SHA, OpenAPI SHA-256 and migration revision in `docs/acceptance/Sx.md`.

## Cross-repo contract negative tests

- Invalid/missing credential and object scope cannot access data or media.
- Case with multiple attempts does not double count dashboard KPIs.
- Null/missing recording or transcript produces explicit `NOT_AVAILABLE`/failure states and readable UI.
- Forward-compatible additive fields do not break an older client.
- A changed schema without regenerated frontend types fails CI.
- Post-call late/replayed events do not rewrite source evidence or falsely change final status.
