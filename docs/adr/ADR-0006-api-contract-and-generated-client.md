# ADR-0006: API contract ownership, conventions and generated client

**Status:** Proposed (CP0.0), 2026-11-15. Owner decision D-14 applied (three repositories, generated OpenAPI)
**Related:** `docs/contracts/API_CONTRACT_POLICY.md` (policy), `docs/contracts/S0_API_CATALOGUE.md` (S0 endpoint catalogue)

## Decision

1. **Executable source of truth:** the FastAPI routes and Pydantic models in `Call360-backend`.
   - `make openapi` boots the app with fixed settings and writes `contracts/generated/openapi.json`, with sorted keys, stable `operationId = <tag>_<action>` and a semver `info.version`.
   - It also writes `contracts/generated/openapi.sha256`.
   - Regenerating from a clean checkout must produce byte-identical output (`make contract-check`).

2. **Specs role:** specs owns meaning, policy and the **descriptive** S0 catalogue. It never holds a second executable OpenAPI file. When the implementation and the catalogue differ, the difference is raised, not silently resolved.

3. **Frontend consumption:**
   - `Call360-frontend` pins a copy of the artifact at `src/api/openapi.pinned.json`, together with `src/api/contract.lock.json` = `{backend_base_sha, backend_manifest_sha256|null, openapi_sha256}`.
   - `npm run api:generate` produces types and client.
   - `npm run api:check` fails on any of:
     - generated-code drift;
     - pinned-file hash ≠ lock;
     - pinned file ≠ `../Call360-backend/contracts/generated/openapi.json`, when the sibling repo is present.
   - Hand-written DTO types for API payloads are prohibited.

4. **Wire conventions (all S0 endpoints):**
   - **Prefix:** `/api/v1`. Unauthenticated, unversioned `/health/live` and `/health/ready` reveal no internal detail. Details sit at `GET /api/v1/admin/system-health` (C-16).
   - **Error envelope:** `{code, message, correlation_id, retryable, details?}`. `details` holds field-level validation errors only. The response carries an `X-Correlation-ID` header.
   - **Lists:** `{items, page: {next_cursor, limit, sort}, total: {value, as_of} | null}`.
     - Cursor (keyset) pagination with a deterministic tiebreak on `id`.
     - `total` is returned only when it is computed over the caller's scope.
     - `limit` ≤ 200.
   - **Strict request models:** unknown fields are rejected (`422 VALIDATION_FAILED`). String and array lengths are bounded.
   - **Mutations:**
     - `X-CSRF-Token` header and `Origin` check;
     - `Idempotency-Key` on creates and intake;
     - `reason` on material changes;
     - `If-Match: <row_version>` on edits. A mismatch returns `409 CONFLICT_ROW_VERSION`.
   - **IDs and times:** IDs are opaque strings; timestamps are ISO 8601 UTC with offset; enums are documented.
   - **Masking:** sensitive fields are masked or omitted by the server according to the caller's permissions. The client never receives a value it then hides.
   - **Evidence availability (C-10):** media and transcript payloads include `availability: {status: AVAILABLE|NOT_AVAILABLE|FAILED|RESTRICTED, reason_code, stage_note}`. The persisted BRD §3.3 enums are unchanged. In S0 every session's media and transcript is `NOT_AVAILABLE / NO_CAPTURE_BEFORE_S1`.
   - **Typed navigation:** search and KPI drilldown results carry `route: {name, params, query}` instead of client-constructed URLs.

5. **Change rule:**
   - **Additive changes:** backend first, then the frontend re-pins.
   - **Breaking changes** (removal, rename, type narrowing, enum value removal, auth tightening that alters a success path) need an ADR, dual support or a versioned field, and owner approval.
   - The OpenAPI SHA-256 is recorded in every checkpoint report and in `S0.md`.

## Consequences

- The frontend cannot drift silently. Contract changes are visible as checksum changes in evidence.
- Mock upstream endpoints (`/mock-internal/v1/...`) belong to a separate application and a separate OpenAPI document. They are not part of the product contract.
