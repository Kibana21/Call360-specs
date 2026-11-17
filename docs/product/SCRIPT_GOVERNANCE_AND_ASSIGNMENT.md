# Call360 — Script Library, Questions, and Script Assignment

**Version 0.3 · Business design contract · Owner: AIA S&C (proposed) · Status: Requires approval.**

> All examples are synthetic. AIA-authoritative scripts, operating rules, regulations, market eligibility and mandatory exact wording must be supplied and reviewed by S&C/Legal before real customer use. A question being sensible is not evidence that MAS mandates it.

## The key business rule

**A call script is a governed, versioned executable business artifact, not a text prompt.** The approved version and its effective-time selection decision must be recoverable for each case and survey run, even after questions are modified or removed from active use. The model provides conversational delivery but cannot change the script requirements.

## Artifacts and ownership

| Artifact | Meaning / responsibility | Identity and immutability |
|---|---|---|
| Question concept | Stable business intention (e.g. ask whether FSC represented AIA) | `question_code`, reusable across script families |
| Question revision | Exact wording, localization, answer schema, help/clarification and evidence rules | Immutable `question_revision_id`; edits create new revision |
| Script module | Reusable named question bundle (COMMON_FSC, NEEDS_ANALYSIS, ILP, HIGH_RISK) | Draft/editable; published revision immutable |
| Script family | Business grouping by product/market/purpose | Stable family ID; many versions |
| Script version | Frozen ordered module composition plus branch and mandatory-question obligations | Published manifest, checksum and signed approval record |
| Assignment rule version | Priority/specificity conditions mapping case attributes to script version | Effective dated; separate from script content version |
| Assignment decision | Chosen manifest for a case with input snapshot, matching and excluded rules | Immutable decision event; reassign creates replacement event |
| Regulatory change request | Links MAS/other guidance to impact analysis and proposed versions | Approval and applicability explicitly recorded |

## Required authoring UX

**Script Studio** (ADR-0007) opens the versioned **Script Library**; users can browse published, draft, scheduled, withdrawn and superseded scripts. A script detail shows modular structure and question counts, applicability, effective dates, language variants, owner, change log and affected cases. Separate tabs: **Questions**, **Routing Rules**, **Expected Answers**, **Review & Publish**, **Version Diff**, **Simulation**.

Question editor requires: stable code, question intention, exact customer wording, delivery mode (`CONVERSATIONAL`/`CONTROLLED_TTS`/`EXACT_AUDIO`), type (`YES_NO`/`NUMERIC`/`ENUM`/`FREE_TEXT`/`ACKNOWLEDGEMENT`), mandatory, localized versions, clarification text, max repetition, skip/conditional rule, expected answer policy, whether evidence is required, prohibited assertions and escalation/rule references. Preserve author, timestamps and revision reason. External URL/document citation is recorded as source metadata, not treated as automatically binding.

**Answer is not only YES/NO**: capture `YES`, `NO`, `UNKNOWN`, `UNCLEAR`, `REFUSED`, `NOT_ASKED`, `NOT_APPLICABLE` and typed values; keep natural-language utterance, extraction metadata and any contradiction. The `expected_answer_policy` may be `EXACT_BOOLEAN`, `NUMERIC_MATCH_POLICY_FACT`, `ACKNOWLEDGEMENT`, `NARRATIVE_REVIEW`, `COLLECT_ONLY`, or approved domain-specific policy. Do not interpret 'expected' as an instruction for the AI to coach the customer to answer YES. Store validation and severity independently.

## Synthetic modular example

1. COMMON_FSC: representative disclosed AIA relationship, was needs/gap analysis discussed, understood reason for recommendation.
2. PROTECTION: coverage term, premium term and protection scope.
3. ILP: review of financial circumstances, premium affordability, investment nature, risk exposure, charges, liquidity and possible surrender implications.
4. ELEVATED_RISK: extra verification and/or manual review per approved risk policy.

These are **topics** for requirements modelling; wording is deliberately not represented as official approved AIA/MAS text.

## Assignment engine decision order

1. Confirm callback case is eligible and respondent is allowed; no eligible contact means HOLD.
2. Resolve authoritative policy/sale snapshot, jurisdiction, product subtype, ILP indicator, channel/location, SBQ selection-risk band, language, case purpose and event time. Unknown essential inputs force triage.
3. Evaluate only **published and effective** script assignment rules. Capture matched rules, excluded rules, precedence, tie-breaks and evaluation version.
4. Compose COMMON module plus product-specific and risk-specific modules in fixed order. Reject duplicate question codes with incompatible revisions; fail safely on missing localized mandatory wording.
5. Create immutable `script_assignment_decision` with published script version ID, manifest checksum, risk-assessment reference, effective timestamp, actor/source and input snapshot.
6. Show the assigned script preview in Policy Detail and Call Detail, including 'why this script'. An operator cannot silently bypass, swap or add questions.
7. On policy/risk updates or regulatory release, run explicit impact analysis. Open cases are flagged for assignment review; prior call sessions keep their frozen script/evidence.

## Assignment rule precedence and specificity (owner decisions 2026-11-17, S2-B)

Recorded on the owner's instruction with the S2-B authorisation. Decisions D-58…D-60 were approved with S2-B; D-61…D-65
(and D-66, S2-A.1) were **approved** on accepting S2-B (2026-11-17), with the D-62 clarification below.

- **D-58 Precedence (approved).** Only published rule versions effective at the evaluation time are considered.
  Priority first: a *lower* number wins (1 is highest). On equal priority the rule with the higher specificity wins.
  Equal priority and specificity with different target script versions → `AMBIGUOUS` (no selection; held for
  authorised review). Equal priority and specificity with the *same* target → all tied rules are kept in the trace and
  the decision fails closed (`AMBIGUOUS_SAME_TARGET`, flagged for review), consistent with T-40.
- **D-59 Specificity (approved).** Calculated automatically, never entered or overridden: the number of distinct
  explicitly constrained predicate fields. Unrestricted ("any") fields do not count; several values within one field
  count once; explicitly matching the unassessed SBQ status (`UNASSESSED`) counts as a constraint. An unassessed case
  matches a rule that does not constrain the band, and matches a band condition only when `UNASSESSED` is listed.
- **D-60 Default fallback (approved).** A fallback must be explicitly configured on the rule and approved like any
  rule. It is considered only when no other rule matches and is never used to resolve ambiguity.
- **D-61 Fail closed (approved).** An eligible rule that cannot be evaluated because a case input is missing gives
  `INPUT_MISSING`; a winning rule whose target script version is not published and effective gives
  `TARGET_NOT_EFFECTIVE`. Neither falls through to a lower-precedence rule.
- **D-62 Contact role (approved, clarified).** In *simulation* "Eligible contact role is X or Y" holds when any current
  eligible contact selection of the case has one of the roles (governed list `callable_party_roles`), and the matched
  roles are displayed; two role conditions never make rules disjoint for conflict analysis. In *actual assignment*
  (S2-C) the selected callback contact's role is used; when contact selection is unresolved and affects the script
  choice, assignment fails closed (`CONTACT_UNRESOLVED`) instead of guessing.
- **D-63 Language (approved).** Not offered as a condition: no governed language fact exists on cases, parties or
  contacts and every script version is English. It needs a governed field before it can be a rule condition.
- **D-64 Rule governance roles (approved).** Rules reuse the S2-A script permissions (D-54): `script.edit` (USER)
  authors, `script.approve`/`script.publish` (SC_CHECKER) review and publish, no maker may approve or publish, ADMIN
  holds none.
- **D-65 One live version per rule (approved).** Publishing a new version of a rule requires the checker to confirm
  that it supersedes the live version; a future-dated version keeps the live one effective until it starts.

Condition fields offered (existing governed sources only): market (required, the rule's market), callback purpose,
product family, product, ILP indicator, SBQ sale-selection risk band (incl. `UNASSESSED`), sales channel, premium
frequency and eligible contact role. Rules are stored in the S0 predicate language extended with `in`
(`{"fact": f, "in": [...]}`); no free text, code or expressions are accepted. Simulation evaluates the same pure logic
in a read-only transaction; publishing a rule never reassigns a case (automatic assignment is S2-C).

## Governance state machine

`DRAFT → SUBMITTED_FOR_REVIEW → APPROVED → SCHEDULED → PUBLISHED → SUPERSEDED | WITHDRAWN`

- Author may propose changes and create a draft; reviewer must be a **different user**. Admin group membership alone does not bypass segregation.
- Submitted content is locked pending reviewer decision or amendment request.
- The reviewer sees content and **semantic diff**: added, deleted, reworded questions, expected-answer changes, branch changes, language differences, and rules that became more/less permissive.
- A published script is immutable. 'Delete' means retired from future composition; historical artifacts stay viewable to authorized reviewers. A withdrawn version cannot be selected for new cases, but is retained for audit.
- Effective-dated release must prevent gaps/conflicts by jurisdiction, product and risk scope. Include rollback as **new publish event** rather than altering historical state.
- Any MAS-driven update requires a source reference, effective date, applicability assessment, business impact, Legal/S&C checker and evidence of script regression tests.
- Changes to expected-answer rules or escalation pathways require independent approval just as wording changes do.

## Audit and evidence

At minimum record `actor_id`, `actor_identity_provider`, `actor_external_subject`, `event_time_utc`, `action`, `entity_id`, `old_revision`, `new_revision`, `canonical_diff`, `business_reason`, `approval_id`, `correlation_id`, `source_ip` (when appropriate), `signature/checksum`, and request/source references. Answer provenance records the **spoken** text and whether a question was fully delivered, not only the written script text.

## Acceptance scenarios

- Edited YES/NO question creates new revision; completed calls continue showing old approved text and expected answer.
- Removal of an ILP question from future scripts leaves it in old session evidence and audit views.
- Two assignment rules match with conflicting outcome → `AWAITING_SCRIPT_REVIEW`, never arbitrary choice.
- An admin who drafted a change cannot approve/publish it as the checker.
- A new MAS guidance reference alone cannot automatically edit scripts; S&C/Legal must approve scope and wording.
- Customer says “yes, but my FSC told me I couldn't lose money”; structured yes/no plus contradictory free text raises a separate review concern.
- The voice model cannot mark the question delivered/completed before delivery confirmation and answer validation.

## Suggested API surface (contracts are generated from backend OpenAPI)

`GET /api/v1/scripts`, `GET /api/v1/scripts/{id}/versions`, `POST /api/v1/scripts/{id}/drafts`, `POST /api/v1/question-revisions`, `GET /api/v1/script-versions/{versionId}/diff`, `POST /api/v1/script-versions/{versionId}/submit`, `POST /api/v1/script-versions/{versionId}/review`, `POST /api/v1/script-versions/{versionId}/publish`, `POST /api/v1/script-assignments/preview`, `GET /api/v1/cases/{id}/script-assignment`.

Mutation routes need idempotency keys, optimistic concurrency / `If-Match` where appropriate, object-level auth and audit. Public stage is governed by requirements register; do not implement all endpoints in Stage 0.
