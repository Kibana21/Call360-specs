# Call360 — Policy, Party, Sale and SBQ Risk Ingestion

**Version 0.3 · Enterprise interface design proposal · Mock API first, manual entry alternative.**

## Business objective

Give S&C an inspectable, trusted policy-sale dossier *before* a callback. This is not merely a list of customers: it represents policy, sale transaction, related parties, authorized respondent, sales representative, premium, channel/location, source evidence, SBQ callback-selection risk and reason, selection obligation and script assignment.

## Source modes and precedence

| Mode | Stage | Detail |
|---|---|---|
| `MOCK_API` | S0 | Local FastAPI synthetic upstream service accessed over real HTTP through the canonical ingestion service. Deterministic fixtures and source batch IDs. |
| `MANUAL` | S0 | Restricted form wizard to inject synthetic policy/sale/party/risk and show saved record in Policy Explorer; capture identity, fields changed, reason and provenance. |
| `BULK` | S4 | Validated CSV/JSON uploaded through secured job, dry-run preview, dedupe, row-level errors and reconciliation. |
| `INTERNAL_API` | S4+, after approval | Source-specific adapter, authentication, mTLS/OAuth as required, pagination, schema mapping, retries/backoff, watermark and reconciliation jobs. |

**Source of truth rule:** each field includes source system, source record ID, observed timestamp, recorded timestamp, mapping version, confidence/quality status and override history. Never silently treat a manual override as upstream authoritative truth. Configurable precedence requires review; mismatches should go to an exception queue. Maintain an immutable event/raw payload reference with access controls, not unlimited raw PII duplication.

## Primary business context

- `Policy`: policy source reference, product code, product family and subtype/ILP, status, effectivity, premium amount/currency/frequency, sum assured and relevant coverage/premium terms.
- `SaleEvent`: separate from policy; can represent issue, replacement, top-up or other approved sales process. Has sale date, distribution channel and location, FSC reference, proposal references and relationship to original policy.
- `Party`: person/entity record; never equate policyholder, insured, payer and respondent. `PolicyPartyRole` effective-dates each relationship; `ContactMethod` holds masked phone/email, verified channel, preference/consent and suppression state.
- `SBQRiskAssessment`: assessed sale event, status, risk profile/band, input factor values, source-assessed vs rule-calculated, ruleset/version, factors explanation, overrides and checker attribution. **Separate from investment suitability risk tolerance** and post-call finding severity.
- `CallbackCase`: immutable relation to the assessed sale/purpose; eligibility/contact permission, assignment, due date and official risk-to-script mapping decision.

## Intake transaction lifecycle

`RECEIVED → VALIDATING → NORMALIZED → PREVIEWED → ACCEPTED | REJECTED | QUARANTINED → RECONCILED`

1. Validate structure and mandatory relationships before creating operational cases. Reject malformed currency/amounts, missing sale identifiers and invalid role relations.
2. Resolve stable canonical IDs using `(source_system, external_id, entity_type)`. Duplicate/replay detection by upstream idempotency key/source event ID. Record both raw and canonical schema versions.
3. De-duplicate linked parties carefully; never merge solely on matching names or telephone numbers. Require approved strong matching strategy or manual review.
4. Compare imported data to existing fields. Store before/after source facts, effective dates and change reason; flag risk/script impact for open cases.
5. Create or update the appropriate sale/callback eligibility state. Never silently create duplicate verification obligations on repeated imports.
6. Publish reconciliation counts: received, new, updated, unchanged, rejected, quarantined and operator-resolved.

## Manual injection flow

1. Select **Data Intake → New synthetic policy case**. Enter distinct policy and sale fields; optionally choose an existing synthetic party or create one with role and contact method.
2. Choose risk mode: **SOURCE RISK (mocked)** or **MANUAL ASSESSMENT/OVERRIDE**; supply factors and reason, show score/band only where a configured approved rule exists.
3. Preview eligibility and script routing without contacting anybody. Show missing inputs and conflicting rule reasons, including risk version and effective date.
4. Submit with required reason and actor; persist and navigate to `Policy Detail` and linked `Call Detail` if case created.
5. Re-inject same source event and verify idempotency; change risk and observe impact exception, not retroactive overwrite.

## Mock API examples (proposed; generated OpenAPI in backend is authoritative)

`GET /mock-internal/v1/sales?cursor=...` returns synthetic `sale_event` records plus related policy and parties. `GET /mock-internal/v1/sales/{id}/risk` returns synthetic SBQ risk assessment. Production-facing `POST /api/v1/intake/import-runs`, `POST /api/v1/intake/manual`, `GET /api/v1/intake/import-runs/{id}`, `GET /api/v1/policies/{id}`, `GET /api/v1/policies/{id}/sales`, `GET /api/v1/risk-assessments`, `POST /api/v1/risk-assessments/{id}/override-request`.

Never expose unauthenticated mock endpoints in deployed production. Gate routes by environment and capability, and ensure mock records cannot be mistaken for real policy records (`is_synthetic=true`, clear UI banner, separate DB/storage).

## Retry and failure cases

API timeout, invalid signature, stale watermark, missing policy, party-role mismatch, unexpected null, contradictory risk source and schema mismatch must produce explicit `INGEST_*` errors and visible work items with safe replay. Do not log PII payloads. S&C can inspect import status but cannot bypass source reconciliation controls without an attributable decision.
