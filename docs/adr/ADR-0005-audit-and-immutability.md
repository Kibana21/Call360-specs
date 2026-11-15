# ADR-0005: Append-only audit, immutable records and session pins

**Status:** Proposed (CP0.0), 2026-11-15. Owner decisions applied: D-6 (pin the exact published script version and risk-assessment snapshot to every conversation), D-8 (immutable published scripts, append-only audit, documented limits of database-only audit integrity)
**Requirements:** SEC-007, IAM-011, ADMIN-002, CASE-002, POL-006, SCR-001, SCR-004, RISK-003; tests T-15, T-33, T-55

## Decision

### 1. Audit trail

- **Table:** `audit_event` is a single append-only table. Each row has:
  - `occurred_at` (UTC);
  - an actor reference (`actor_principal_id` or `service_principal`), plus an actor snapshot (`provider`, `issuer`, `subject`, `display_name`);
  - `session_id`, `request_id`, `correlation_id`, `source_ip`;
  - `action` (dotted code, for example `ADMIN.USER_DISABLED`), `entity_type`, `entity_id`, `entity_version`;
  - `outcome` (`SUCCEEDED`, `DENIED` or `FAILED`), `reason`;
  - `before`/`after` as a redacted, field-level JSON diff, or a hash where the value is sensitive;
  - `prev_hash`, `row_hash`.
- **Written in the same database transaction** as the business change it describes. If the audit write fails, the change rolls back.
- **Database protection:**
  - Role separation is **not used** in S0, because the app connects as the single local login `Call360_db_user` (owner decision D-16).
  - A `BEFORE UPDATE OR DELETE` trigger raises an exception.
  - No API offers update or delete.
  - `make audit-verify` recomputes the hash chain (`row_hash = SHA-256(canonical_row ‖ prev_hash)`) and reports the first break.
- **Secrets are never audited:** no passwords, tokens or full contact values. Search queries are recorded as normalised hashes (S-14).
- **Business rows keep their own metadata:** `created_at`, `created_by`, `updated_at`, `updated_by`, `row_version`. These are operational metadata and do not replace audit events.

### 2. Documented limitations of database-only audit integrity (D-8)

These controls establish that history is **internally consistent**. They don't prove it is **authentic**. Specifically:

1. A database superuser or the owner role can disable triggers, rewrite rows and recompute the whole chain. In S0 the application itself connects as a superuser (`Call360_db_user`), so this applies to the running app too, not only to an administrator.
2. Restoring a backup can silently roll history back.
3. The audit trail shares a failure domain with the data it protects.
4. Timestamps come from the application and database clocks, which are trusted rather than independently attested.
5. Events never written (for example, actions taken directly in SQL) are absent rather than detected.

**S0 mitigations:**
- the trigger and the absence of any update or delete API;
- the chain head digest is recorded in checkpoint and stage evidence, so a later rewrite of earlier history is detectable against the recorded digest;
- no runtime path can write the audit table except the audit writer.

**Choice deferred to S5 (owner):**
- WORM or immutable object storage;
- SIEM forwarding;
- periodic signed checkpoints by an external key;
- or a separate audit store.

### 3. Write-once records

Enforcement uses database triggers plus the absence of any update API. A correction always creates a new or superseding row, which references its predecessor.

| Record | Becomes immutable when |
|---|---|
| `script_version` content (manifest, sections, checksum) | Status leaves DRAFT (SUBMITTED_FOR_REVIEW or later). Only lifecycle status and effective dates may change, and only through governed transitions; `effective_to` may be set once and never changed (D-32, CP0.2 alignment) |
| `question_revision` | On insert. A correction or edit always inserts a new revision (D-35, CP0.2 alignment; this replaces the earlier wording "once it is referenced by any non-draft script version") |
| `script_section` | When its script version leaves DRAFT |
| `policy_fact_snapshot` | On insert |
| `risk_assessment` and `risk_factor_result` | When `status = FINAL`. The only later change is `FINAL → SUPERSEDED`, made in the transaction that inserts a successor whose `supersedes_id` references it; `SUPERSEDED` is terminal and the historical assessment stays unchanged (D-31) |
| `script_assignment` | On insert; reassignment inserts a new row with `supersedes_id` |
| `contact_attempt` contact snapshot fields | On insert |
| `conversation_session` pin columns (below) | On insert |
| `audit_event`, `case_event`, `field_change`; `review_decision` (S3) | On insert |

### 4. Session pins (D-6)

Each `conversation_session` stores, at creation and immutably:
- `script_version_id` + `script_manifest_sha256`;
- `risk_assessment_id` + `risk_snapshot_sha256`;
- `policy_fact_snapshot_id` + `policy_fact_snapshot_sha256`;
- `contact_method_snapshot` (masked value, method ID, version) + `contacted_party_id`.

Constraints:
- A database check requires that the pinned script version was published and effective at `session.started_at`, judged against its historical publication and effective interval (`published_at ≤ started_at`, `effective_from ≤ started_at < coalesce(effective_to, ∞)`). A version that is now `SUPERSEDED` or `WITHDRAWN` does not invalidate a session that was valid when it started (D-32, S0_DATA_MODEL INV-09).
- `survey_run` carries the same script pin. The session pin is what the conversation was bound to; the run pin is what executed. In S1 and later they must match unless an approved resume rule says otherwise.

Seeded S0 sessions satisfy the same constraints. They are labelled `SYNTHETIC_SEED` (ADR-0008).

## Consequences

- Historic cases keep showing their original script text, answers and risk basis after any later change (T-15, T-33, SCR-004).
- Audit verification is a routine local command, and the chain head is part of the evidence.
- The limitations above must appear in the residual-risk register. Stage acceptance must not claim tamper-proof audit.
