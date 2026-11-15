# ADR-0008: Stage 0 functional boundaries, holds, navigation and synthetic evidence

**Status:** Proposed (CP0.0), 2026-11-15
**Owner decisions applied:**
- D-4: no risk-scoring or script-assignment engine in S0
- D-10: synthetic data, never presented as real completed functionality
- D-11: GPT-Live in S1, Genesys in S6
- C-1: mockup navigation structure with canonical terms
- C-12: separate auditable hold; blocking holds prevent a case from becoming callable
- the owner correction on `is_synthetic`

**Exceptions and extensions:** EXC-003, EXT-001, EXT-002 (`docs/spec/APPROVED_EXCEPTIONS.md`)

## 1. Risk and script assignment are persisted records in S0, not computed (D-4)

- **Risk assessments exist only as stored records:**
  - seeded, with origin `SOURCE_ASSIGNED` or `RULE_ASSESSED`, the latter referencing a seeded **synthetic** `risk_rule_set_version` and a stored factor trace;
  - or supplied by intake, either `SOURCE_ASSIGNED` from the mock source API or `MANUAL` with a reason.
- **No code computes a risk band or score.**
  - RISK-004 ("support seeded source-assigned and local rule-assessed risk") is met by the seeded `RULE_ASSESSED` records and their stored traces.
  - Calculation is RISK-008 (S2).
- **Script assignments exist only as seeded records,** each with its matched/excluded rule trace and input snapshot. SCR-004 and SCR-005 are display-only in S0.
  - No resolver runs at intake.
  - A case created by intake is placed on the `AWAITING_SCRIPT_ASSIGNMENT` blocking hold.
  - The intake preview states "Script routing is not evaluated in Stage 0" (a deviation from POLICY_PARTY_RISK_INTAKE manual-flow step 3).
- **Moved to S2:**
  - T-40 (competing assignment rules hold) needs the engine.
  - T-16 and T-50 (self-approval) need the script workflow. ADMIN-003 is still proven in S0 through the permission model.
- **Score display:**
  - A score is shown only if the stored assessment carries one from its recorded rule-set version, labelled "Synthetic rule set — not AIA-approved".
  - Band, factors, origin and version are always shown.
  - No thresholds are hard-coded. The factor vocabulary comes from versioned code lists (RISK-006).

## 2. Case holds (C-12, EXT-001)

- **Lifecycle states:** the BRD §3.1 `callback_case.state` values are unchanged.
- **Hold record:** a hold is a separate, auditable `case_hold` record (one row per hold placement). Each row has:
  - `hold_reason`;
  - `is_blocking`;
  - `placed_at`/`placed_by`/`placed_reason`;
  - `released_at`/`released_by`/`release_reason`;
  - `source` (`SEED`, `INTAKE`, `SYSTEM`, `MANUAL`).

  Placing or releasing a hold writes an audit event and a `case_event`.
- **S0 hold reasons** come from a versioned code list:

  | Reason | Blocking |
  |---|---|
  | `AWAITING_SCRIPT_ASSIGNMENT` | yes |
  | `AWAITING_SCRIPT_REVIEW` | yes |
  | `RISK_TRIAGE` | yes |
  | `NO_ELIGIBLE_CONTACT` | yes |
  | `DATA_CONFLICT` | yes |
  | `OPERATOR_HOLD` | configurable; seeded non-blocking |

- **Callable:** a case is callable when its state is `READY` or `AWAITING_CALLBACK` **and** it has no active blocking hold.
- **Enforcement:**
  - `callback_case.has_blocking_hold` is maintained in the same transaction as `case_hold` changes.
  - A database check rejects `state IN ('READY','IN_PROGRESS')` while `has_blocking_hold` is true.
  - Services refuse to create contact attempts for non-callable cases (S1 and later).
- **Multiple holds:** several holds may be active at once. The API returns every active hold plus a derived `callable: boolean` and `callable_blockers[]`.

## 3. Navigation (C-1, EXC-003)

The navigation follows the approved HTML mockup's grouped structure and order, with canonical specification terms. The authoritative table is in `docs/product/SCREEN_NAMING_AND_ROUTES.md`; summary:

| Group (mockup) | Items (mockup label → canonical label) |
|---|---|
| WORKSPACE | Overview → **Overview** (page title "Command Centre") · Call Explorer → **Call Explorer** · Policy & Sales → **Policy Explorer** · Risk Assessment → **SBQ Risk Workbench** · Callback Queue → **Work Queues** · (added) **Voice Studio** · Live Monitor → **Live Monitor** (S4, disabled) · (added) **Campaigns** (S4, disabled) |
| GOVERNANCE | Script Studio → **Script Studio** · Assignment Rules → **Assignment Rules** · Compliance Reviews → **Review Workbench** |
| INTELLIGENCE | Universal Search → **Search** · Analytics & Reports → **Analytics** (S4, disabled) |
| PLATFORM | Data Integrations → **Data Intake** · Administration → **Administration** |

Two items are added to the mockup's list:
- **Voice Studio**, because SCREEN_NAMING requires an S0 preflight screen;
- **Campaigns**, because it is a BRD screen staged for S4.

Disabled items are visible, keyboard-focusable, `aria-disabled`, and carry a stage chip. Visiting their route shows a stage notice with no data. **Call Detail** is reached from records; it is not a navigation item.

## 4. Seeded evidence (D-10)

- **Labelling:** seeded sessions, survey runs, question executions, answer observations, rule evaluations and findings carry `record_origin = SYNTHETIC_SEED`. Every UI surface that shows them carries a persistent label: "Seeded synthetic example — not produced by a Call360 voice session or compliance evaluation". KPIs computed over them carry a synthetic badge.
- **Media and transcripts:** none exist. Every session's media and transcript availability is `NOT_AVAILABLE / NO_CAPTURE_BEFORE_S1`, and the player and transcript areas show an explicit unavailable panel with no seek bar (EXT-002). `transcript_segment` is deferred to S1 and `review_decision` to S3; neither is built in S0 (D-19, S0_DATA_MODEL §4.6).
- **Seeded attempts and sessions:** they use `transport = SYNTHETIC`. They don't claim browser or Genesys transport.
- **No later-stage code in S0:** there is no evaluation, review-decision, publish, override or export code.
- **Disabled controls:** later-stage UI controls are disabled with a visible stage chip and an accessible explanation, never inert. Examples:
  - "Stage S1 — Browser voice";
  - "Stage S2 — Script authoring";
  - "Stage S3 — Review decisions";
  - "Stage S4 — Export".

## 5. Voice and Genesys (D-11)

- `GET /api/v1/voice/preflight` returns `NOT_AVAILABLE` with the reason "Browser voice is introduced in Stage S1".
- No provider SDK, key or network call exists in S0.
- Genesys is S6. The attempt and session `transport` enums already reserve `BROWSER` and `GENESYS`, so later adapters need no schema change.

## 6. Synthetic-only data policy (GOV-001; owner correction)

- **No permanent schema constraint:** there is no `CHECK (is_synthetic)`. The schema is compatible with future real data.
- **`DATA_POLICY=SYNTHETIC_ONLY`** is mandatory when `APP_ENV ∈ {local, test}`. Under it:
  1. Intake accepts only `source_type ∈ {SEED, MOCK_API, MANUAL}`. `BULK` and `INTERNAL_API` connectors are not registered.
  2. Every intake payload must declare `is_synthetic = true`. Otherwise it is rejected (`INGEST_NON_SYNTHETIC_REJECTED`) and audited.
  3. Contact values must fall in configured reserved synthetic ranges, for example a non-routable test number prefix. Otherwise they are rejected (`INGEST_CONTACT_NOT_SYNTHETIC`).
  4. The readiness check fails, and the API refuses to serve, if any business row has `is_synthetic = false`.
  5. The UI shows a persistent "Synthetic data — local demo" banner, and login shows "Local demo identity — not SSO".
  6. The mock upstream app is mounted and reachable only in `local`/`test` and requires a service token.
- **Other environments:** the policy for SIT/UAT/production is decided before S4/S5 (DEC-018, DEC-028).

## Consequences

- S0 shows the full policy → risk → script → case → evidence chain on real persisted data, without pretending that later-stage computation or voice exists.
- When S2 adds the engines, they write the same tables. Seeded records remain distinguishable by `source_type`/`record_origin`.
