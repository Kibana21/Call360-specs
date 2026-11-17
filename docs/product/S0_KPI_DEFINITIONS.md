# Call360 — Stage 0 KPI definitions

**Status:** CP0.0 draft, 2026-11-15; final corrections 2026-11-15 (owner decisions D-17, D-18)
**Basis:** BRD §10 numerators and denominators, owner decisions D-12, K-1…K-4, D-17, D-18; extension EXT-003
**Requirements:** APP-002, APP-004, T-21, T-29 (partial), T-30
**Targets and thresholds:** none. Thresholds belong to DEC-016 and are not set here.

## 1. Case outcome model (D-17)

Every callback case has exactly one **outcome category**, derived from persisted data (no new table). Separately, every case has an **SLA indicator**.

| Outcome category | Definition |
|---|---|
| `VERIFIED_COMPLIANT` | State `VERIFIED` **and** every applicable mandatory verification control is satisfied (§1.1) **and** the case has no finding with status other than `DISMISSED` |
| `VERIFIED_WITH_FINDINGS` | State `VERIFIED` **and** ≥1 finding with status other than `DISMISSED` |
| `NOT_VERIFIED` | State `CLOSED_UNVERIFIED`, reported by closure reason |
| `CANCELLED` | State `CANCELLED`, reported by cancellation reason |
| `OPEN` | Any non-terminal state; reported with its holds |

**Guard: a `VERIFIED` case with no findings whose mandatory controls are not all evidenced is never `VERIFIED_COMPLIANT`.** It is reported as the data-integrity exception `VERIFIED_CONTROL_EVIDENCE_INCOMPLETE`, a separate count that should be zero (BRD §3.1 permits `VERIFIED` only from an evidence-sufficient survey).

**Interpretation rule (D-17):**
- `NOT_VERIFIED`, `CANCELLED` and an SLA breach describe the **callback verification**, never the **insurance sale**. None of them implies that the sale was non-compliant.
- UI labels and API field names use "Not verified", "Cancelled" and "SLA breached". The terms "non-compliant", "failed" and "mis-sold" are never applied to these categories.
- Only reviewed findings, from S3 onwards, can support a conclusion about a sale.

### 1.1 Mandatory verification controls satisfied

The controls are evaluated on the case's verifying survey run: the latest `COMPLETED` run pinned to a `PUBLISHED` script version. For each question revision in that run's frozen manifest with `mandatory = true`:

1. **Applicability.** If its `not_applicable_predicate` evaluates true against the pinned policy fact snapshot, the question is excluded. Otherwise it is **applicable**.
2. **Asked and answered.** Each applicable question must have a `question_execution` with an `answer_observation` whose `answer_state` is not `NOT_ASKED`, `REFUSED` or `UNKNOWN`.
3. **Satisfied according to its `expected_answer_policy`:**

| Expected-answer policy | Satisfied when |
|---|---|
| `EXACT_BOOLEAN`, `NUMERIC_MATCH_POLICY_FACT` | Latest `rule_evaluation.result = MATCH` |
| `ACKNOWLEDGEMENT` | `answer_state = YES` and latest `rule_evaluation.result = MATCH` |
| `COLLECT_ONLY` | Answered (step 2) |
| `NARRATIVE_REVIEW` | A recorded human review disposition. **Not possible in Stage 0**, because review decisions arrive in S3. A case with an applicable mandatory narrative-review question therefore cannot be `VERIFIED_COMPLIANT` in S0, and the seed must not mark one as such |

Rules for the evaluation:
- `UNCLEAR` or `INDETERMINATE` never satisfies a control.
- If there is no verifying run, no control is satisfied.

## 2. Rules common to every KPI

| Rule | Definition |
|---|---|
| Computation | SQL over persisted rows. No hard-coded or client-side numbers (APP-002) |
| Scope | The caller's market scope ∩ request filters (market, product family, ILP, channel, script version). Scope is applied **before** aggregation (SEARCH-006) |
| Time zone | `Asia/Singapore`. A range `[from, to)` is given in local dates and converted to UTC instants |
| Cohort basis (K-4) | **SLA and obligation cohorts use `callback_case.due_at`. Intake cohorts use `created_at`** of the counted entity. Event-grain KPIs use their own event timestamp, stated per KPI |
| Deduplication | Case KPIs count `DISTINCT callback_case.id`. Attempt KPIs count attempts; run KPIs count runs; finding KPIs count findings. A multi-attempt case is one case (T-21) |
| Held cases (K-1) | Holds **do not pause the SLA clock** and do not remove an obligation (D-18). Held cases stay **in** every case-grain denominator and stay visible in reporting. Every case KPI reports `held_in_denominator` |
| Cancelled cases (K-1, K-3) | `CANCELLED` is its own outcome: neither verified nor evidence of a non-compliant sale (D-17). Cancelled cases are **always visible** (outcome distribution, cancellation rate, operational counts). They are **excluded** from the coverage, contact-exhaustion, verification-rate and not-verified-rate denominators, because no verification is owed after cancellation. For SLA, see the exemption rule below |
| Closed-unverified (K-3) | `CLOSED_UNVERIFIED` is never counted as verified. It is reported as `NOT_VERIFIED` by closure reason, and never as a non-compliant sale |
| SLA exemptions (K-3) | Only through an **approved** rule in the governed code list `kpi_sla_exemption_rule` (each rule carries a predicate, approval reference and effective period). The list is read-only in S0. S0 contains exactly one approved rule, `SLA-EX-001` (D-18, below). Every SLA payload lists `exemptions_applied` with counts per rule |
| `SLA-EX-001` (D-18) | A `CANCELLED` case is exempt from SLA breach **only if all of these hold:** (a) `cancellation_reason` is a value in the governed list `case_cancellation_reason` whose attribute `sla_exempt_eligible = true`; (b) `cancellation_authorized_by` and `cancellation_authorization_ref` are recorded; (c) `cancelled_recorded_at`, the server-recorded time and never client-supplied or backdated, is earlier than `due_at`. A cancellation that fails any condition (invalid reason, missing authorisation, or recorded on or after `due_at`, which is retrospective) gets **no** exemption. It stays in the SLA denominator and counts as breached if not verified by `due_at`. Exempt cases are excluded from the SLA numerator and denominator and reported in `exemptions_applied` |
| Materiality (K-2) | A finding is material when its severity is in the governed list `finding_materiality_policy`. S0 version 1 is `{HIGH, CRITICAL}`, provisional. Business-approved exceptions (categories excluded or included, each with an approval reference) live in the same list. S0 has none and the list is read-only |
| Reopen handling | Reopening is not supported in S0. Every payload states `reopen_handling: "NOT_SUPPORTED_IN_S0"` |
| Synthetic badge | `synthetic_badge: true` when any counted row has `record_origin = SYNTHETIC_SEED` or `is_synthetic = true` |
| Not measurable | `status: NOT_MEASURED`, `value: null`, `stage_note`. Never reported as 0 % or 100 % |
| Drilldown (APP-004, T-30) | Each KPI returns typed routes to Call Explorer: `kpi=<ID>&kpi_set=numerator\|denominator` (and `outcome=` where relevant) plus the same filters and range. The explorer applies **the same server-side predicate function**. Set equality is tested (BE-KPI-02) |

**Payload (API-030), per KPI:**
- `definition_id`, `label`, `grain`;
- `numerator`, `denominator`, `value`, `unit`, `status (MEASURED|NOT_MEASURED)`;
- `cohort_basis`, `range{from,to}`, `time_zone`, `filter_scope{markets,…}`;
- `dedup_rule`, `eligibility_rule`, `exclusions{excluded_cancelled, held_in_denominator, …}`, `exemptions_applied[]`;
- `materiality_policy_version` (where relevant), `reopen_handling`;
- `data_as_of`, `reporting_version: "S0-KPI-3"` (S0-KPI-3 adds the D-48 test-session exclusion, §3.1), `synthetic_badge`;
- `drilldown{numerator, denominator}`.

## 3. KPI catalogue

| ID | KPI | Grain | Cohort | Denominator (eligibility) | Numerator | Notes |
|---|---|---|---|---|---|---|
| KPI-01 | Callback coverage | case | `due_at` ∈ range | Cases due in range, **excluding CANCELLED**; held included | Denominator cases with ≥1 operational contact attempt (§3.1) whose status ≠ `SCHEDULED` | Not the same as connection rate |
| KPI-02 | Connection rate | attempt | attempt `started_at` ∈ range | Operational attempts (§3.1) in a terminal outcome: `NO_ANSWER`, `BUSY`, `WRONG_PARTY`, `FAILED`, `CONNECTED`, `IN_SESSION`, `ENDED` (in-flight excluded) | Attempts `CONNECTED`, `IN_SESSION` or `ENDED` | Attempts of held or cancelled cases included (they happened) |
| KPI-03 | Survey completion | survey run | run `started_at` ∈ range | Runs with status ≠ `NOT_STARTED` | Runs `COMPLETED` | BRD definition (completed / started), not the mockup's completed / connected. Synthetic badge |
| KPI-04 | Verification rate | case | `due_at` ∈ range | Cases due in range, **excluding CANCELLED** (shown separately); held included | Cases `VERIFIED_COMPLIANT` + `VERIFIED_WITH_FINDINGS` | Also returns the two parts separately. Synthetic badge |
| KPI-05 | Contact exhaustion | case | `due_at` ∈ range | Cases due in range, **excluding CANCELLED** | `NOT_VERIFIED` with closure reason `ATTEMPTS_EXHAUSTED` | Not the same as customer refusal |
| KPI-06 | Compliance exception rate | case | survey run `completed_at` ∈ range | Cases with ≥1 `COMPLETED` survey run in range that has ≥1 `rule_evaluation` | Denominator cases with ≥1 **material** finding (K-2) raised from those runs | Concerns flagged for review, not conclusions about a sale. Reports `materiality_policy_version`. Synthetic badge |
| KPI-07 | Critical exception backlog | finding | snapshot at `data_as_of` | — (count) | Findings with severity `CRITICAL` and status `OPEN` or `UNDER_REVIEW`, by age since `raised_at`: 0–2 d, 3–7 d, 8–14 d, >14 d | Synthetic badge |
| KPI-08 | Recording integrity | session | — | — | — | `NOT_MEASURED`: "No recordings are captured before Stage S1" |
| KPI-09 | Transcript integrity | session | — | — | — | `NOT_MEASURED`: "Transcripts are captured from Stage S1" |
| KPI-10 | SLA breach rate | case | `due_at` ∈ range **and** `due_at` < `data_as_of` (matured only) | All matured cases due in range, **including held**, **including CANCELLED unless exempt under `SLA-EX-001`** | Denominator cases without `verified_at` ≤ `due_at` | Timeliness indicator, **not a compliance outcome**. Holds do not pause the clock. Returns breach counts per outcome category |
| KPI-11 | Review turnaround | finding review | `review_closed_at` ∈ range | Findings with both `review_assigned_at` and `review_closed_at` | Median and P90 of `review_closed_at − review_assigned_at` (hours) | Uses timestamps on `finding` (S0 seed). Synthetic badge |
| KPI-12 | Retry conversion | case | `due_at` ∈ range | Cases with ≥2 operational attempts (§3.1) whose status ≠ `SCHEDULED` | Denominator cases whose first `CONNECTED` operational attempt is the 2nd or later operational attempt | Counts the case once |
| KPI-13 | New cases (intake cohort) | case | `created_at` ∈ range | — (count) | Cases created in range, by `source_type` | K-4 intake cohort |
| KPI-14 | Intake runs | intake run | `started_at` ∈ range | — (count) | Runs by status, with received, new, updated and rejected totals | ADMIN only (`intake.read`) |
| KPI-15 | Outcome distribution | case | `due_at` ∈ range | All cases due in range (including CANCELLED, OPEN and held) | Count and share per outcome category: `VERIFIED_COMPLIANT`, `VERIFIED_WITH_FINDINGS`, `NOT_VERIFIED`, `CANCELLED`, `OPEN` | Also returns the `VERIFIED_CONTROL_EVIDENCE_INCOMPLETE` guard count and an SLA-breached count per category. Synthetic badge |
| KPI-16 | Findings rate among verified | case | `due_at` ∈ range | Cases `VERIFIED_COMPLIANT` + `VERIFIED_WITH_FINDINGS` | Cases `VERIFIED_WITH_FINDINGS` | Synthetic badge |
| KPI-17 | Not-verified rate | case | `due_at` ∈ range | Terminal cases due in range, **excluding CANCELLED** and excluding OPEN | Cases `NOT_VERIFIED`, by closure reason | Verification outcome, not a sale-compliance judgement |
| KPI-18 | Cancellation rate | case | `due_at` ∈ range | All cases due in range | Cases `CANCELLED`, by cancellation reason and by exemption eligibility under `SLA-EX-001` | Keeps cancellations visible |

### 3.1 Test sessions are not operational attempts (D-48, owner decision 2026-11-17)

A contact attempt with `transport = BROWSER` and `record_origin = CALL360_RUNTIME` is a Call360 browser voice test
session (API `attempt_kind = TEST_SESSION`, mock provider, not a customer contact). Such attempts are excluded from the
numerators **and** denominators of every attempt-based operational callback KPI: KPI-01 (a case covered only by a test
session is not covered; the case itself stays in the denominator because it is due), KPI-02 and its trend, and KPI-12
(ordinals are counted among operational attempts). The KPI payload states `exclusions.test_sessions_excluded = true`
and KPI-02 also returns `test_sessions_excluded_count`. Test sessions stay visible in test activity (Voice Studio),
case history (Call Detail contact history, attempt counts) and audit records. Ordinary seeded historical attempts are
**never** excluded merely because the development database is synthetic. Case-grain KPIs that do not count attempts
(KPI-04/05/10/15–18) are unaffected: a test session cannot change a case outcome.

## 4. Operational counts (Overview cards; not rates)

| ID | Card | Definition |
|---|---|---|
| OPS-01 | Open callback cases | Outcome category `OPEN` |
| OPS-02 | Due today | `OPEN` cases with `due_at` on today's local date (Asia/Singapore) |
| OPS-03 | On hold | `OPEN` cases with ≥1 active hold, by `hold_reason` and blocking flag. The SLA clock is still running |
| OPS-04 | Awaiting review | Cases in state `AWAITING_REVIEW` |
| OPS-05 | Verified cases (range) | KPI-04 numerator, split into compliant and with-findings, with its denominator |
| OPS-06 | High-risk due | `OPEN` cases due in range whose effective SBQ band has attribute `high_priority=true` in the active `sbq_risk_band` list version |
| OPS-07 | Cancelled (range) | KPI-18 numerator, with reasons |

**Mockup card mapping:**
- "Open callback cases" → OPS-01
- "Due today" → OPS-02
- "Survey completion" → KPI-03, relabelled "completed / started"
- "Awaiting review" → OPS-04
- "Verified cases" → OPS-05

The "Risk distribution" panel binds to API-034. The outcome distribution (KPI-15) is shown on the Overview as a breakdown panel.

## 5. Test obligations

| Test | Checks |
|---|---|
| BE-KPI-01 | Each KPI against a hand-computed fixture (held, cancelled, closed-unverified, multi-attempt and cross-market rows) |
| BE-KPI-02 | Drilldown set equality |
| BE-KPI-03 | Scope applied before aggregation |
| BE-KPI-04 | `NOT_MEASURED` KPIs never return a number |
| BE-KPI-05 | Outcome classification, including the mandatory-control rules and the incomplete-evidence guard |
| BE-KPI-06 | `SLA-EX-001`: valid exemption; invalid reason, missing authorisation and cancellation recorded on or after `due_at` all not exempt; held cases not paused |
| E2E-02 | Overview card → Call Explorer count equality |
