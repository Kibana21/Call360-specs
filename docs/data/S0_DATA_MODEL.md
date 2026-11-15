# Call360 — Stage 0 canonical data model

**Status:** CP0.0 draft, 2026-11-15. Normative for CP0.1A and CP0.1B (identity, audit, config), CP0.2 (business domain) and later Stage 0 checkpoints per the Build column
**Derives from:** `CANONICAL_GRAIN_AND_RELATIONSHIPS.md` (authoritative on grain and invariants), BRD §2–§3 and §4.4, ADR-0003…0008
**Physical names** may be refined during implementation, but grain, keys, relationships, enums and immutability rules may not change without a specs change.

## 1. Principles

1. **Policy-sale-centric, distinct grains.** Party ≠ policy ≠ sale event ≠ risk assessment ≠ callback case ≠ contact attempt ≠ conversation session ≠ survey run ≠ question execution ≠ answer observation ≠ finding ≠ review decision. Never collapse them into a single "call" row.
2. **Three risk concepts stay separate:**
   - SBQ callback-selection risk is `risk_assessment` (kind `CALLBACK_SELECTION`).
   - Customer investment suitability / risk tolerance is a **sourced fact** inside `policy_fact_snapshot.facts.suitability` and is never a `risk_assessment`.
   - Compliance finding severity is `finding.severity`, with its own enum.
3. **History is never overwritten.** Corrections create superseding rows, `field_change` rows and audit events (ADR-0005).
4. **Every case, policy and party is market-scoped** through `market_code`, which drives authorization (ADR-0004).
5. **Compatible with the future.** Real data, OIDC identities, browser and Genesys transports, and bulk and internal-API intake all fit these tables without breaking changes. The values are reserved now and enabled in their stages.

## 2. Common columns

| Group | Columns | Applies to |
|---|---|---|
| Identity | `id uuid PK`; human reference where listed (`*_ref text UNIQUE`) | all tables |
| Operational metadata | `created_at`, `created_by` (principal id, or `SYSTEM:<component>`), `updated_at`, `updated_by`, `row_version int` (optimistic concurrency), `correlation_id` | all mutable tables; insert-only tables have `created_*` only |
| Provenance | `source_type` (enum below, NOT NULL), `source_system` NOT NULL, `source_reference` NOT NULL, `source_observed_at`, `recorded_at` NOT NULL, `mapping_version`, `intake_item_id` (nullable FK) | all business entity tables marked **P** in §4 |
| Data classification | `is_synthetic boolean NOT NULL` with no CHECK constraint. Synthetic-only operation is enforced by `DATA_POLICY=SYNTHETIC_ONLY` (ADR-0008 §6) | all business entity tables marked **P** |
| Evidence origin | `record_origin` ∈ `SYNTHETIC_SEED`, `CALL360_RUNTIME` | evidence/outcome tables marked **E** in §4 |
| Scope | `market_code` (FK `code_value` in list `market`) | policy, party (derived), sale_event (via policy), callback_case, script_family, regulatory_reference |

## 3. Enumerations

Values in *italics* are reserved for later stages. A database enum or check accepts them; S0 code never produces them.

| Enum | Values | Source |
|---|---|---|
| `source_type` | `SEED`, `MOCK_API`, `MANUAL`, *`BULK`*, *`INTERNAL_API`* | Intake doc; BRD §4.4 |
| `party_kind` | `PERSON`, `ORGANIZATION` | Grain doc |
| `party_role` | `OWNER`, `INSURED`, `PAYER`, `PROPOSER`, `BENEFICIARY`, `AUTHORIZED_CONTACT` | PARTY-001 |
| `contact_channel` | `PHONE`, `EMAIL` | PARTY-003 |
| `sale_event_type` | `NEW_BUSINESS`, `REPLACEMENT`, `TOP_UP`, `OTHER_APPROVED` | Intake doc; POL-001 |
| `premium_frequency` | `SINGLE`, `MONTHLY`, `QUARTERLY`, `HALF_YEARLY`, `ANNUAL` | POL-002 |
| `risk_kind` | `CALLBACK_SELECTION` (the only value) | Grain doc |
| `risk_origin` | `SOURCE_ASSIGNED`, `RULE_ASSESSED`, `MANUAL` | RISK-004; intake doc |
| `risk_assessment_status` | `PROVISIONAL`, `FINAL`, `SUPERSEDED` | Grain doc constraint 7 |
| `risk_band` | from versioned code list `sbq_risk_band` (synthetic: `LOW`, `MEDIUM`, `HIGH`, `UNKNOWN`) | RISK-006 (not hard-coded) |
| `case_state` | `CREATED`, `VALIDATED`, `READY`, `IN_PROGRESS`, `AWAITING_CALLBACK`, `AWAITING_REVIEW`, `ESCALATED`, `VERIFIED`, `CLOSED_UNVERIFIED`, `CANCELLED` | BRD §3.1 (unchanged) |
| `case_closure_reason` | code list `case_closure_reason` (synthetic seed: `ATTEMPTS_EXHAUSTED`, `CUSTOMER_REFUSED`, `INELIGIBLE`, `UNABLE_TO_VERIFY`, `UNRESOLVED_MATERIAL_EXCEPTION`, `POLICY_CANCELLED`, `DUPLICATE_OBLIGATION`) | BRD §3.1; values pending DEC-008 |
| `hold_reason` | code list `case_hold_reason`: `AWAITING_SCRIPT_ASSIGNMENT`, `AWAITING_SCRIPT_REVIEW`, `RISK_TRIAGE`, `NO_ELIGIBLE_CONTACT`, `DATA_CONFLICT` (all blocking), `OPERATOR_HOLD` (blocking configurable) | C-12; ADR-0008 §2 |
| `attempt_status` | `SCHEDULED`, `INITIATED`, `CONNECTING`, `NO_ANSWER`, `BUSY`, `WRONG_PARTY`, `FAILED`, `CONNECTED`, `IN_SESSION`, `ENDED` | BRD §3.2 |
| `transport` | `SYNTHETIC` (seed only), *`BROWSER`* (S1), *`GENESYS`* (S6) | ADR-0008 §4–5 |
| `attempt_direction` | `OUTBOUND`, *`INBOUND`* | BRD §3.2 |
| `session_state` | `CREATED`, `CONSENT_PENDING`, `IDENTITY_PENDING`, `SURVEY_ACTIVE`, `PAUSED`, `INTERRUPTED`, `ESCALATING`, `COMPLETED`, `ABORTED`, `FINALIZING`, `FINALIZED` | BRD §3.3 |
| `media_status` | `NOT_REQUIRED`, `CAPTURE_PENDING`, `CAPTURING`, `UPLOADING`, `AVAILABLE`, `FAILED`, `REDACTED`, `PURGED`, `HELD` | BRD §3.3 (unchanged) |
| `transcript_status` | `PENDING`, `PARTIAL`, `FINALIZED`, `QUALITY_FLAGGED`, `CORRECTED_BY_ADDENDUM`, `UNAVAILABLE` | BRD §3.3 |
| `evidence_availability` (API only, derived) | `AVAILABLE`, `NOT_AVAILABLE`, `FAILED`, `RESTRICTED` | EXT-002; ADR-0006 |
| `survey_run_status` | `NOT_STARTED`, `IN_PROGRESS`, `PAUSED`, `COMPLETED`, `INCOMPLETE`, `ABORTED` | BRD §3.3 |
| `review_status` | `NOT_REQUIRED`, `PENDING`, `ASSIGNED`, `IN_REVIEW`, `RETURNED`, `APPROVED`, `REJECTED`, `CLOSED` | BRD §3.3 |
| `script_version_status` | `DRAFT`, `SUBMITTED_FOR_REVIEW`, `APPROVED`, `SCHEDULED`, `PUBLISHED`, `SUPERSEDED`, `WITHDRAWN` | C-4; ADR-0007 |
| `validation_status` | `NOT_VALIDATED`, `VALID`, `INVALID` | ADR-0007 |
| `script_module_kind` | `COMMON`, `PRODUCT`, `RISK`, `LANGUAGE` | Grain doc `script_section` |
| `delivery_mode` | `CONVERSATIONAL`, `CONTROLLED_TTS`, `EXACT_AUDIO` | BRD §6.1 |
| `answer_type` | `YES_NO`, `NUMERIC`, `ENUM`, `FREE_TEXT`, `ACKNOWLEDGEMENT` | SCRIPT_GOVERNANCE |
| `expected_answer_policy` | `EXACT_BOOLEAN`, `NUMERIC_MATCH_POLICY_FACT`, `ACKNOWLEDGEMENT`, `NARRATIVE_REVIEW`, `COLLECT_ONLY` | SCR-002; SCRIPT_GOVERNANCE |
| `answer_state` | `YES`, `NO`, `UNKNOWN`, `UNCLEAR`, `REFUSED`, `NOT_ASKED`, `NOT_APPLICABLE` | BRD §4.4 |
| `content_approval_status` | `SYNTHETIC_UNAPPROVED`, *`APPROVED_BY_SC`* | D-10; DEC-002 |
| `rule_result` | `MATCH`, `MISMATCH`, `INDETERMINATE`, `NOT_EVALUATED` | BRD §5.5 |
| `finding_severity` | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` (distinct from `risk_band`) | RISK-001 |
| `finding_status` | `OPEN`, `UNDER_REVIEW`, `CONFIRMED`, `DISMISSED`, `CLOSED` | BRD §5.7 |
| `regulatory_interpretation_status` | `NOT_REVIEWED`, `UNDER_REVIEW`, *`INTERPRETED_APPROVED`*, *`NOT_APPLICABLE`* | REG-001 |
| `intake_run_status` | `RECEIVED`, `VALIDATING`, `NORMALIZED`, `PREVIEWED`, `ACCEPTED`, `REJECTED`, `QUARANTINED`, `RECONCILED` | Intake doc |
| `identity_provider_kind` | `LOCAL`, *`OIDC_ENTRA`*, *`OIDC_OKTA`* | ADR-0004 |
| `principal_status` | `ACTIVE`, `DISABLED` | IAM-009 |
| `audit_outcome` | `SUCCEEDED`, `DENIED`, `FAILED` | ADR-0005 |

## 4. Table catalogue

**Build** = the checkpoint that physically creates the table. Tables marked "not built in S0" are part of the canonical model only. They get no migration in Stage 0, and API fields that would read them report `NOT_AVAILABLE` (owner decision D-19). Stage 0 builds **59** of the 63 tables. CP0.1 is split into CP0.1A and CP0.1B (D-21); the schema and role layout is in S0_IDENTITY_ACCESS_DESIGN §10 (D-22).

Column flags: **P** = provenance and `is_synthetic` common columns apply; **E** = `record_origin` applies; **I** = immutable after insert (trigger-guarded); **IF** = immutable once finalised or published. The "Grain-doc mapping" column names the entity in `CANONICAL_GRAIN_AND_RELATIONSHIPS.md`, or explains why a table is new.

### 4.1 Identity, access, audit and configuration

| Table | Grain (one row per) | Grain-doc mapping | Key columns and constraints | Flags | Build |
|---|---|---|---|---|---|
| `identity_provider` | configured IdP | `identity_provider` | `kind`, `issuer` UNIQUE, `status`, metadata (no secrets) | — | CP0.1A |
| `principal` | durable internal staff identity | `user_account` (renamed per security doc, C-5) | `display_name`, `status`, `disabled_at`, `disabled_by`; never recycled | — | CP0.1A |
| `identity_binding` | provider identity linked to a principal | `user_account.provider_subject` (split out, C-5) | `principal_id`, `identity_provider_id`, `subject`; UNIQUE (`identity_provider_id`, `subject`); `username` (LOCAL only, unique case-insensitive) | — | CP0.1A |
| `local_credential` | local password credential | NEW: security doc `local_credential` | `principal_id` UNIQUE, `password_hash` (Argon2id encoded), `hash_params`, `password_changed_at`, `failed_count`, `locked_until` | — | CP0.1A |
| `app_group` | group (local or external) | `group_mapping` source groups (security doc `group`) | `identity_provider_id`, `external_group_id` (nullable for LOCAL), `name`, `status` | — | CP0.1A |
| `group_membership` | principal ∈ group over an interval | NEW: security doc `membership` | `principal_id`, `group_id`, `valid_from`, `valid_to`, `provenance`; history retained | — | CP0.1A |
| `role` | canonical app role | `user_role_assignment.role` | `code` UNIQUE (`ADMIN`, `USER`; reserved `REVIEWER`, `SCRIPT_AUTHOR`, `APPROVER`, `AUDITOR`) | — | CP0.1A |
| `permission` | atomic permission | `permission` | `code` UNIQUE (dotted), `alias` (security-doc name), `reserved boolean` | — | CP0.1A |
| `role_permission` | permission granted to role | `role_permission` | UNIQUE (`role_id`, `permission_id`); reserved permissions cannot be granted in S0 (service check) | — | CP0.1A |
| `group_role_mapping` | group → role mapping version | `group_mapping` | `group_id`, `role_id`, `effective_from`, `effective_to`, `approved_by`; audited | — | CP0.1A |
| `group_scope_mapping` | group → market scope | NEW: scope half of `group_mapping` (D-7) | `group_id`, `market_code`, effective dates; audited | — | CP0.1B |
| `auth_session` | authenticated session | `auth_session` | `principal_id`, `created_at`, `last_seen_at`, `idle_expires_at`, `absolute_expires_at`, `revoked_at`, `revoked_reason`, `user_agent_hash`, `ip` | — | CP0.1A |
| `refresh_token_family` | rotating refresh family | `refresh_token_family` | `session_id`, `revoked_at`, `revoked_reason` | — | CP0.1A |
| `refresh_token` | one issued refresh token | `refresh_token_record` | `family_id`, `generation`, `token_hmac` UNIQUE, `issued_at`, `expires_at`, `used_at`, `reuse_detected_at` | — | CP0.1A |
| `login_attempt` | one login attempt | NEW: throttling and IAM-011 | `username_hash`, `ip`, `occurred_at`, `outcome` (no password, no raw username) | I | CP0.1A |
| `audit_event` | one meaningful action | `audit_event` | ADR-0005 §1 columns; `prev_hash`, `row_hash` | I | CP0.1A |
| `saved_view` | one user's saved filter view | NEW: SEARCH-004 | `owner_principal_id`, `name`, `view_type` (`CALL_EXPLORER`, `POLICY_EXPLORER`, `RISK_WORKBENCH`), `filter_json` (schema-validated), `sort`; UNIQUE (`owner_principal_id`, `view_type`, `name`) | — | CP0.3 |
| `code_list` | one value list | NEW: ADMIN-004 / RISK-006 | `code` UNIQUE (for example `market`, `sbq_risk_band`, `risk_factor`, `case_hold_reason`, `case_closure_reason`, `finding_materiality_policy`, `kpi_sla_exemption_rule`, `case_cancellation_reason`, `callable_party_roles`, `synthetic_contact_ranges`) | — | CP0.1B |
| `code_list_version` | one immutable version of a list | NEW: ADMIN-004 | `code_list_id`, `version`, `effective_from`, `status` (`DRAFT`, `ACTIVE`, `SUPERSEDED`), `change_reason` | IF | CP0.1B |
| `code_value` | one value in a list version | NEW: ADMIN-004 | `code_list_version_id`, `code`, `label`, `attributes jsonb`, `sort_order` | IF | CP0.1B |
| `feature_flag` | one feature toggle | NEW: ADMIN-004 | `code` UNIQUE, `enabled`, `description`, `stage_gate` | — | CP0.1B |
| `feature_flag_change` | one flag change | NEW: ADMIN-004 | `feature_flag_id`, `old`, `new`, `reason`, `changed_by` | I | CP0.1B |

### 4.2 Party, policy and sale

| Table | Grain (one row per) | Grain-doc mapping | Key columns and constraints | Flags | Build |
|---|---|---|---|---|---|
| `party` | real-world person or organisation | `party` | `party_ref` UNIQUE, `kind`, `display_alias` (pseudonymous, searchable), `name_ciphertext`, `masked_name`, `date_of_birth_year` (synthetic only), `personal_data_class`; never keyed by name or phone | P | CP0.2 |
| `contact_method` | effective-dated reachable method | `contact_method` | `party_id`, `channel`, `value_ciphertext` (AES-GCM), `value_hmac` (exact-match token), `masked_value`, `is_verified`, `preference_rank`, `language`, `timezone`, `consent_status`, `suppressed`, `valid_from`, `valid_to`; a change inserts a new row and closes the old one | P | CP0.2 |
| `policy` | issued policy or proposal identity | `policy` | `policy_ref` UNIQUE, `market_code`, `product_code`, `product_family`, `product_subtype`, `is_ilp`, `status`, `premium_amount`, `currency`, `premium_frequency`, `premium_term_years`, `sum_assured`, `sum_assured_currency`, `effective_from`, `effective_to` | P | CP0.2 |
| `policy_party_role` | role of a party on a policy | `policy_party_role` | `policy_id`, `party_id`, `role`, `valid_from`, `valid_to`; UNIQUE (`policy_id`, `party_id`, `role`, `valid_from`) | P | CP0.2 |
| `fsc_representative` | sales representative (FSC) | NEW: FSC reference on `sale_event` normalised (POL-003) | `fsc_ref` UNIQUE, `display_name` (synthetic), `channel`, `status` | P | CP0.2 |
| `sale_event` | distribution/sales transaction | `sale_event` | `sale_ref` UNIQUE, `policy_id`, `sale_event_type`, `sold_at`, `fsc_id` (FK, frozen at sale), `selling_channel`, `selling_location`, `campaign_code`, `proposal_ref`, `product_snapshot jsonb`, `premium_amount`, `currency`; UNIQUE (`source_system`, `source_reference`) | P | CP0.2 |
| `policy_fact_snapshot` | immutable fact set used for a decision | `policy_fact_snapshot` | `policy_id`, `sale_event_id`, `captured_at`, `schema_version`, `facts jsonb` (including `suitability`, sourced), `field_provenance jsonb`, `sha256` UNIQUE | P, I | CP0.2 |
| `external_reference` | external identifier of an entity | `external_reference` | `source_system`, `object_type`, `external_id`, `entity_id`; UNIQUE (`source_system`, `object_type`, `external_id`) | I | CP0.2 |
| `field_change` | one attributable field change (correction or import update) | NEW: POL-005/POL-007 diff ledger | `entity_type`, `entity_id`, `field`, `old_value_redacted`, `new_value_redacted`, `source_type`, `reason`, `changed_by`, `intake_item_id` | I | CP0.4 |
| `intake_run` | one manual, mock or batch ingestion attempt | `intake_run` | `source_type`, `source_system`, `status`, `started_at`, `finished_at`, `requested_by`, `idempotency_key`, counts (`received`, `new`, `updated`, `unchanged`, `rejected`, `quarantined`), `payload_digest` | — | CP0.4 |
| `intake_item` | one source record within a run | NEW: per-record lineage (intake doc lifecycle) | `intake_run_id`, `source_event_id`, `entity_type`, `status`, `errors jsonb`, `payload_digest`, `raw_payload_ref` (S0: hash only, no raw PII) | I | CP0.4 |

### 4.3 SBQ callback-selection risk

| Table | Grain (one row per) | Grain-doc mapping | Key columns and constraints | Flags | Build |
|---|---|---|---|---|---|
| `risk_rule_set_version` | one published rule-set version (synthetic, seeded) | `risk_rule_set_version` | `code`, `version`, `effective_from`, `effective_to`, `checksum`, `status`, `content_approval_status = SYNTHETIC_UNAPPROVED`, `author_ref`, `checker_ref` | P, I | CP0.2 |
| `risk_assessment` | one decision for a sale event at a time | `risk_assessment` | `sale_event_id`, `kind = CALLBACK_SELECTION`, `origin`, `status`, `band_code` (code list), `score` (nullable; only with `rule_set_version_id`), `reason_codes[]`, `explanation`, `source_original_value`, `rule_set_version_id` (required when `RULE_ASSESSED`), `assessed_at`, `valid_at`, `input_snapshot_sha256`, `supersedes_id` | P, IF | CP0.2 |
| `risk_factor_result` | one evaluated factor in one assessment | `risk_factor_result` | `assessment_id`, `factor_code` (code list `risk_factor`), `value_type`, `value`, `source`, `matched_rule_id`, `weight` (nullable), `result` | P, IF | CP0.2 |
| `risk_override` | one requested or approved risk exception | `risk_override` | defined now, **not used in S0** (override workflow is S2) | — | S2 (not built in S0) |

Effective risk: the most recent `FINAL` assessment for the sale event, unless the case pins a specific one. A `SOURCE_ASSIGNED` band and a `RULE_ASSESSED` band are both kept (grain constraint 7). When they differ, the case gets a `DATA_CONFLICT` or `RISK_TRIAGE` hold (T-34, data level).

### 4.4 Scripts, questions and regulatory references

| Table | Grain (one row per) | Grain-doc mapping | Key columns and constraints | Flags | Build |
|---|---|---|---|---|---|
| `script_family` | logical questionnaire family | `script_family` | `code` UNIQUE, `name`, `market_code`, `purpose`, `description` | P | CP0.2 |
| `script_module` | reusable named question bundle revision | NEW: SCRIPT_GOVERNANCE "script module" | `code` (`COMMON_SALES_CONDUCT`, `PROTECTION`, `ILP`, `ELEVATED_RISK`), `revision`, `kind`, `status` | P, IF | CP0.2 |
| `script_version` | immutable questionnaire build | `script_version` | `script_family_id`, `version_label`, `status` (`script_version_status`), `validation_status`, `language`, `effective_from`, `effective_to`, `manifest jsonb` (compiled ordered modules and question revisions), `manifest_sha256`, `author_ref`, `reviewer_ref`, `published_at`, `content_approval_status`, `supersedes_id` | P, IF | CP0.2 |
| `script_section` | ordered module inclusion in a script version | `script_section` | `script_version_id`, `script_module_id`, `order`, `inclusion_condition jsonb`; UNIQUE (`script_version_id`, `order`) | P, IF | CP0.2 |
| `question_bank_item` | stable semantic question identity | `question_bank_item` | `question_code` UNIQUE, `intent`, `category` | P | CP0.2 |
| `question_revision` | exact wording and answer-schema revision | `question_revision` | `question_bank_item_id`, `revision`, `language`, `customer_wording`, `delivery_mode`, `answer_type`, `answer_schema jsonb`, `mandatory`, `expected_answer_policy`, `expected_value jsonb`, `acceptable_variants jsonb`, `policy_fact_key` (for `NUMERIC_MATCH_POLICY_FACT`), `unacceptable_outcomes jsonb`, `not_applicable_predicate jsonb`, `evidence_required`, `escalation_rule_ref`, `max_reprompts`, `content_approval_status = SYNTHETIC_UNAPPROVED` | P, I | CP0.2 |
| `module_question` | question revision placed in a module revision | NEW: join (module ↔ question revision) | `script_module_id`, `question_revision_id`, `order`, `branch_condition jsonb` | P, IF | CP0.2 |
| `script_assignment_rule_version` | effective-dated assignment rule version (seeded, read-only in S0) | `script_assignment_rule_version` | `rule_code`, `version`, `predicate jsonb` (market, product subtype, ILP, risk band, channel, language), `priority`, `specificity`, `target_script_version_id`, `effective_from`, `effective_to`, `status`, `checksum`, `author_ref`, `checker_ref` | P, I | CP0.2 |
| `script_assignment` | script decision for a case | `script_assignment` | `callback_case_id`, `script_version_id`, `script_manifest_sha256`, `risk_assessment_id`, `policy_fact_snapshot_id`, `matched_rule_version_id`, `rule_trace jsonb` (matched, excluded, precedence), `input_snapshot jsonb` + `input_sha256`, `origin` (`SEED`; S2 adds `ENGINE`, `MANUAL_APPROVED`), `assigned_at`, `assigned_by`, `supersedes_id` | P, I | CP0.2 |
| `regulatory_reference` | public regulatory document version | `regulatory_reference` | `issuer`, `jurisdiction`, `title`, `document_version`, `url`, `published_on`, `interpretation_status` | P | CP0.2 |
| `control` | internal AIA control (synthetic) | `control_mapping` (control half) | `control_code`, `name`, `owner_role`, `content_approval_status` | P | CP0.2 |
| `control_mapping` | link question ↔ control ↔ optional regulatory reference | `control_mapping` | `question_bank_item_id`, `control_id`, `regulatory_reference_id` (nullable), `rationale`, `status` | P | CP0.2 |

### 4.5 Callback case, attempts, sessions and evidence

| Table | Grain (one row per) | Grain-doc mapping | Key columns and constraints | Flags | Build |
|---|---|---|---|---|---|
| `callback_case` | verification obligation for a sale and purpose | `callback_case` | `case_ref` UNIQUE, `sale_event_id`, `obligation_type`, `source_request_ref`, `market_code`, `state`, `closure_reason`, `priority`, `owner_principal_id`, `due_at`, `verified_at`, `closed_at`, `cancellation_reason` (code list `case_cancellation_reason`), `cancelled_recorded_at` (server-set, never client-supplied), `cancellation_authorized_by`, `cancellation_authorization_ref`, `has_blocking_hold`; CHECK: cancellation fields set only when `state = 'CANCELLED'`; UNIQUE (`sale_event_id`, `obligation_type`, `source_request_ref`); CHECK NOT (`has_blocking_hold` AND `state IN ('READY','IN_PROGRESS')`) | P | CP0.2 |
| `case_hold` | one hold placement on a case | NEW: EXT-001 / C-12 | `callback_case_id`, `hold_reason`, `is_blocking`, `placed_at`, `placed_by`, `placed_reason`, `source`, `released_at`, `released_by`, `release_reason`; partial UNIQUE (`callback_case_id`, `hold_reason`) WHERE `released_at IS NULL` | — (insert; release fields set once) | CP0.2 |
| `case_contact_selection` | contact eligibility decision for a case | `case_contact_selection` | `callback_case_id`, `party_id`, `policy_party_role_id`, `contact_method_id`, `eligible`, `ineligibility_reason`, `rule_basis` (code list `callable_party_roles` version), `decided_at`, `decided_by`, `supersedes_id` | P, I | CP0.2 |
| `contact_attempt` | one contact attempt | `contact_attempt` | `attempt_ref` UNIQUE, `callback_case_id`, `sequence`, `transport`, `direction`, `status`, `contacted_party_id`, `contact_method_id`, `contact_snapshot jsonb` (masked value, method version), `scheduled_at`, `started_at`, `ended_at`, `failure_reason`; UNIQUE (`callback_case_id`, `sequence`) | P, E; snapshot I | CP0.2 |
| `conversation_session` | one connected media interaction | `conversation_session` | `session_ref` UNIQUE, `contact_attempt_id`, `state`, `transport`, `external_session_ref`, `started_at`, `ended_at`, pins per ADR-0005 §4 (`script_version_id`, `script_manifest_sha256`, `risk_assessment_id`, `risk_snapshot_sha256`, `policy_fact_snapshot_id`, `policy_fact_snapshot_sha256`, `contacted_party_id`, `contact_method_snapshot`), `media_status`, `transcript_status` | P, E; pins I | CP0.2 |
| `survey_run` | one execution of a frozen script version in a session | `survey_run` | `session_id`, `script_version_id`, `script_manifest_sha256`, `policy_fact_snapshot_id`, `status`, `started_at`, `completed_at`; partial UNIQUE (`session_id`) WHERE status active (grain constraint 3) | P, E; pins I | CP0.2 |
| `question_execution` | one asked occurrence of a question | `question_execution` | `survey_run_id`, `question_revision_id`, `order`, `delivery_status`, `retries`, `skip_reason`, `event_range jsonb` | P, E, IF | CP0.2 |
| `answer_observation` | one raw, extracted or human-updated representation | `answer_observation` | `question_execution_id`, `answer_state`, `typed_value jsonb`, `verbatim_text_redacted`, `transcript_segment_ids[]`, `extraction_engine`, `extraction_version`, `created_by`, `supersedes_id` | P, E, I | CP0.2 |
| `rule_evaluation` | one deterministic comparison result | NEW: BRD §2 `RuleEvaluation` (grain doc folds this into findings) | `question_execution_id`, `rule_ref`, `rule_version`, `expected jsonb`, `observed jsonb`, `result`, `evaluated_at` | P, E, I | CP0.2 |
| `transcript_segment` | one source-revisioned utterance segment | `transcript_segment` | `session_id`, `revision`, `speaker`, `start_ms`, `end_ms`, `time_uncertain`, `text_redacted`, `checksum`. Deferred to S1; in S0 transcripts are `NOT_AVAILABLE` and `answer_observation.transcript_segment_ids` is empty | P, E, I | S1 (not built in S0) |
| `media_asset` | one stored media artifact | `media_asset` | defined; **no rows in S0** | P, E | S1 (not built in S0) |
| `finding` | one flagged potential concern | `finding` | `finding_ref` UNIQUE, `callback_case_id`, `question_execution_id` (nullable), `category`, `severity`, `status`, `evidence_refs jsonb`, `origin`, `raised_at`, `review_assigned_at`, `review_closed_at`, `assigned_reviewer_id` | P, E | CP0.2 |
| `review_decision` | one immutable reviewer or checker action | `review_decision` | `finding_id` or `callback_case_id`, `actor_ref`, `from_status`, `to_status`, `reason`, `decided_at`, `checker_ref`. Deferred to S3; S0 findings carry only status and review timestamps | P, E, I | S3 (not built in S0) |
| `case_event` | one business timeline event | NEW: BRD §2 timeline / `CaseEvent` | `callback_case_id`, `event_type`, `occurred_at`, `actor_ref`, `related_entity_type`, `related_entity_id`, `summary` | I | CP0.2 |

`compliance_rule_version`, `search_projection`, `outbox_events`, campaigns, model configurations and evaluation tables are not part of this catalogue. They are added in their stages without changing the tables above.

### 4.6 Physical build summary (D-19)

| Checkpoint | Tables | Count |
|---|---|---|
| CP0.1A | Identity, sessions, tokens, groups, roles, permissions, throttling, audit (§4.1) | 15 |
| CP0.1B | `group_scope_mapping` (package CP0.1B-2); code lists and feature flags (package CP0.1B-1) | 6 |
| CP0.2 | Party, policy and sale (except intake and `field_change`); risk (except `risk_override`); scripts; callback and evidence (except `transcript_segment`, `media_asset`, `review_decision`) | 34 |
| CP0.3 | `saved_view` | 1 |
| CP0.4 | `intake_run`, `intake_item`, `field_change` | 3 |
| **Stage 0 total** | | **59** |
| Not built in S0 | `transcript_segment`, `media_asset` (S1) · `risk_override` (S2) · `review_decision` (S3) | 4 |

## 5. Key relationships and invariants (test-backed)

| # | Invariant | Test |
|---|---|---|
| INV-01 | `callback_case → sale_event → policy → policy_party_role → party` resolves for every case | BE-DATA-03 |
| INV-02 | One policy can have many sale events, and each sale event can have its own case (T-31) | BE-DATA-07 |
| INV-03 | Every attempt belongs to exactly one case. Only `CONNECTED`, `IN_SESSION` or `ENDED` attempts have sessions | BE-DATA-03 |
| INV-04 | Session pins, `script_assignment`, the policy fact snapshot and published script content reject UPDATE and DELETE | BE-DATA-04 |
| INV-05 | A contact-method change never alters an existing attempt `contact_snapshot` (T-38) | BE-DATA-08 |
| INV-06 | A blocking hold prevents `READY` or `IN_PROGRESS` | BE-DATA-09 |
| INV-07 | Provenance columns are NOT NULL on every **P** table | BE-DATA-05 |
| INV-08 | `risk_assessment.kind = CALLBACK_SELECTION`. Suitability exists only in snapshot facts. Finding severity uses its own enum | BE-DATA-06 |
| INV-09 | A pinned script version was `PUBLISHED` and effective at `session.started_at` | BE-DATA-04 |
| INV-10 | Under `SYNTHETIC_ONLY`, no business row has `is_synthetic = false` (readiness check) | BE-DATA-10 |
| INV-11 | The factor values stored on an assessment reproduce `input_snapshot_sha256` | BE-DATA-11 |

## 6. Deterministic synthetic seed specification (implemented in CP0.2)

- **Determinism:**
  - generator RNG seed `360`;
  - anchor date `2026-11-15` (Asia/Singapore), overridable by `SEED_ANCHOR`;
  - seed version `S0-SEED-1`, recorded in a `seed_manifest` audit event.

  Two runs on a freshly reset schema in `Call360_db` produce identical content digests (BE-DATA-02).
- **Minimum volumes:**
  - 250 callback cases, 400 contact attempts, 80 conversation sessions with survey runs;
  - 4 or more script versions, covering `PUBLISHED`, `SUPERSEDED`, `DRAFT` and `WITHDRAWN`;
  - 20 or more findings across all severities;
  - 2 synthetic markets, `SG` and `MY`;
  - 3 or more product families, including ILP and protection.
- **Coverage:**
  - every `case_state` and every hold reason;
  - joint policies with multiple eligible contacts (T-32);
  - multi-sale policies: new business plus a top-up (T-31);
  - contact-method changes after an attempt (T-38);
  - source-assigned and rule-assessed risk pairs, including at least one conflicting pair (T-34);
  - an ILP sale with missing risk on a `RISK_TRIAGE` hold (T-35);
  - cases with 1, 2 and 3 or more attempts;
  - sessions in `COMPLETED`, `INTERRUPTED` and `ABORTED`;
  - every outcome category (S0_KPI_DEFINITIONS §1), including `VERIFIED_COMPLIANT` cases whose mandatory controls are all satisfied, and no `VERIFIED_COMPLIANT` case with an applicable mandatory `NARRATIVE_REVIEW` question;
  - a superseded script version still referenced by an old session (T-15).
- **Golden fixtures (stable references used by tests):**

  | Reference | Content |
  |---|---|
  | `CB-2026-10482` | SG, ILP, effective band HIGH (`RULE_ASSESSED`, synthetic rule set). Script `COMMON_SALES_CONDUCT + ILP + ELEVATED_RISK` (seeded assignment with trace). Attempts `NO_ANSWER → BUSY → CONNECTED`, with one session and a `COMPLETED` survey run. A premium-term answer of 5 against a snapshot value of 10 gives a `MISMATCH` rule evaluation and a HIGH finding |
  | `CB-2026-10483` | Two attempts, no session |
  | `CB-2026-20001` | MY market; used for cross-market denial |
  | `CB-2026-10490` | `AWAITING_SCRIPT_ASSIGNMENT` hold |
  | `CB-2026-10491` | `NO_ELIGIBLE_CONTACT` hold (the only contact is suppressed) |
  | `CB-2026-10492` | `RISK_TRIAGE` hold (ILP, missing risk) |
  | `CB-2026-10493` | `CLOSED_UNVERIFIED` with closure reason `ATTEMPTS_EXHAUSTED` |
  | `CB-2026-10494` | `CANCELLED` before `due_at` with an exempt-eligible reason and recorded authorisation (exempt under `SLA-EX-001`) |
  | `CB-2026-10495` | `CANCELLED` before `due_at` without recorded authorisation (not exempt) |
  | `CB-2026-10496` | `CANCELLED` with `cancelled_recorded_at` after `due_at` (retrospective; not exempt) |
  | `CB-2026-10497` | `VERIFIED_COMPLIANT`: all mandatory controls satisfied, no findings |
  | `CB-2026-10498` | `RISK_TRIAGE` hold past `due_at` (the hold does not pause SLA; counted as breached) |

- **Synthetic content:**
  - names follow the "Example Policyholder NNN" pattern;
  - phone numbers come from the configured reserved synthetic range;
  - every script and question has `content_approval_status = SYNTHETIC_UNAPPROVED`, with wording that is clearly illustrative and not AIA or MAS language;
  - every evidence row has `record_origin = SYNTHETIC_SEED`.
- **No credentials:** the seed creates no principals and no credentials (C-6).
