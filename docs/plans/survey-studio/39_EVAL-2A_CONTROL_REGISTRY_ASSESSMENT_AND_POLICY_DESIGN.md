# EVAL-2A — Control Registry assessment, and the governed control-policy design

**Written before implementation**, as the owner's authorisation of 2026-11-22 requires ("Document the canonical
identity and revision strategy before implementation"). The implementation report is `40_…`.
**Simulation only.** Nothing here decides what a real application needs, and no control or obligation of the
insurance business is created: every control, condition and obligation used is synthetic.

---

## Part 1 — The existing Control Registry, as it is

Sources: migration `0005` (tables `control`, `control_mapping`), the seed, `app/domain/script_authoring.py`,
`finding_rules.py`, the scripts / case-detail / reviews APIs that read it, and the development database (read-only).

| Aspect | Finding |
|---|---|
| Schema | `control`: `id`, `control_code` (unique), `name`, `owner_role`, `content_approval_status`, plus the standard operational and provenance columns (`row_version`, `source_*`, `is_synthetic` …) |
| Content | five rows, all seeded (`SYN-CTRL-01` … `-05`), all `SYNTHETIC_UNAPPROVED`, owner "S&C (proposed)" |
| Purpose or description | **none** — a control is a code and a name |
| Market | **none** — the register is global |
| Lifecycle | **none.** No states, no events, no maker-checker. The row is mutable (`row_version`), and nothing in the application changes it: there is no API or screen that creates or edits a control |
| Revisions | **none.** No trigger protects the row; a change would silently change its meaning everywhere |
| Applicability | **none.** Nothing says when a control applies |
| Question links | `control_mapping`: question-bank item ↔ control, with rationale, optional regulatory reference and a status. All 12 rows are `PROPOSED`; none is `ACTIVE`. The links are copied into frozen script content and shown in Script Studio, Call Detail and the review workbench |
| Other users | finding rules may address a control by code (`CONTROL` scope) |
| Evidence requirement | **none.** What evidence a control needs is nowhere stated except, since EVAL-1, in a survey control mapping |

**Consequences for EVAL-2A.** The register can say *that a control exists* and nothing more. It cannot answer "which
controls must be assessed for this application" or "what evidence does each need", and it cannot be pinned.

## Part 2 — The smallest safe, additive extension

**The register is not replaced, copied or edited.** A control stays the row it is; Script Studio, finding rules, Call
Detail and reviews keep reading it exactly as before. One governed artifact is added beside it:

> A **control policy** is a governed, versioned statement, for one market, of *which controls of the register are in
> its scope, what each is for, when each applies, and what evidence each requires* — independent of any survey
> question.

The EVAL-1 **control mapping** stays what it is — the link from a control to exact published survey items — and gains
one optional thing per entry: the name of the policy's evidence requirement it supplies.

    control (register row, unchanged)
       ▲ referred to by code + id + fingerprint
    control policy revision   WHAT must be assessed, WHEN, and WHAT EVIDENCE is required     (new, EVAL-2A)
       ▲ requirement keys
    control mapping revision  WHICH published survey items supply that evidence, under WHICH rule   (EVAL-1)
       ▲ exact item revisions
    published survey versions

Why a policy *set* rather than a revision per control: the question the owner asks — "which controls must be
assessed" — and the condition for asserting coverage — "its applicable-control set is complete" — are properties of
a **set**. A per-control revision could say when one control applies but never that the list is complete.

## Part 3 — Canonical identity and revision strategy

| Thing | Identity | Revision |
|---|---|---|
| Control | `control_code` (the register's own unique code) and row `id` | none exists. A policy pins the **fingerprint of the register row** at proposal (code, name, owner role, approval status). A control changed afterwards is reported (`CONTROL_CHANGED_SINCE_POLICY`), never silently re-read |
| Control policy | `(market, code)` | `revision` 1, 2, 3 … Each revision is an immutable row with a fingerprint of its whole content. Lifecycle `PROPOSED → APPROVED \| REJECTED \| WITHDRAWN → PUBLISHED → SUPERSEDED \| WITHDRAWN`; three different people (service and database trigger). Publishing a revision supersedes the published revision of the same code |
| Obligation | `(control_code, obligation key)` within one policy revision | belongs to the policy revision |
| Evidence requirement | `(control_code, obligation key, requirement key)` within one policy revision | belongs to the policy revision |
| Control mapping | `(market, control_code)` | as in EVAL-1: immutable revisions, three people |
| **Control instance** (result) | **(evaluation, control code, obligation key)**, where the evaluation pins the journey, the policy revision and the mapping revisions | never revised: a new evaluation is a new record |

"Effective version" is the exact published revision an evaluation names and pins. There is no effective date in
EVAL-2A: nothing approved says when a policy takes or loses effect, and an evaluation of a simulation names its
policy revision explicitly.

## Part 4 — The control policy document

| Field | Meaning |
|---|---|
| `code`, `name`, `market_code` | identity |
| `scope_statement` | in words, what the policy covers. Required |
| `scope` | optional published condition on application facts: whether an application is inside the policy's scope at all. Three-valued |
| `completeness` | `DECLARED_COMPLETE` — the three people who publish it state that, within its scope, its list of controls is the complete list to assess — or `PARTIAL` |
| `empty_set_is_complete` | `false` unless the policy expressly says that an application to which none of its controls applies is fully covered |
| `owner`, `source` | who answers for it; where it comes from |
| `controls[]` | each: the register control (code, id, fingerprint), `purpose`, `description`, and one or more **obligations** |
| obligation | `key`, `title`, `applicability` (none = every application in scope, or a published condition with its parameters), `combination` (`ALL_REQUIRED`), and `evidence[]` |
| evidence requirement | `key`, `description`, `evidence_type` (`ANSWER` / `DELIVERY`), `required` |

A policy says nothing about survey questions. Conditions are the existing Survey Studio published conditions,
evaluated by the existing three-valued evaluator; only conditions that read application facts (not answers) are
accepted.

**Why obligations.** One control can stand for more than one thing to verify — for different kinds of application,
with different evidence. Each obligation is its own result. Evidence from several surveys for the *same* obligation
is one result; two obligations of the same control are two.

## Part 5 — Applicability

For one application snapshot (the journey's facts) and one policy revision:

| Step | Result |
|---|---|
| policy `scope` | `IN_SCOPE` (true, or no condition), `OUT_OF_SCOPE` (false), `UNKNOWN` |
| each obligation | `APPLICABLE` — required (condition true, or none), `NOT_APPLICABLE` (false), `UNKNOWN` — with the facts read and the facts missing |
| fingerprint | SHA-256 over the policy revision fingerprint, the application facts fingerprint and every obligation's status |

`UNKNOWN` is never read as "does not apply". The application's facts are catalog facts supplied to the simulation;
nothing maps assignment-rule inputs or evaluation policy facts to them, so every determination carries
`input_lineage: UNVERIFIED`.

## Part 6 — Evaluation under a policy

The control instances are the policy's obligations (not "whatever happened to be mapped"). For each `APPLICABLE` one:

1. the control's published mapping supplies entries bound to this obligation's requirement keys;
2. a required requirement with no bound entry is **not mapped**;
3. an entry bound to a requirement the policy does not have, or with another evidence type, is **inconsistent**;
4. `required` is the policy's, not the mapping's;
5. the bound entries are observed and combined exactly as in EVAL-1 (D-287).

An evaluation that names no policy behaves exactly as in EVAL-1.

## Part 7 — Coverage

Four things, never merged:

| | Values |
|---|---|
| Processing status | `COMPLETED`, `INCOMPLETE`, `REQUIRES_REVIEW`, `FAILED_TECHNICALLY` |
| Control outcome | `SATISFIED`, `NOT_SATISFIED`, `INSUFFICIENT_EVIDENCE`, `NOT_APPLICABLE`, `UNRESOLVED`, `REQUIRES_REVIEW` |
| **Coverage of each control instance** | below |
| Operational compliance eligibility | always `NOT_ESTABLISHED` |

| Instance coverage | When |
|---|---|
| `EVIDENCED` | required, mapped, and every required piece of evidence has a deterministic result — whether the control is satisfied or not |
| `EVIDENCE_MISSING` | required, mapped, evidence missing |
| `NOT_MAPPED` | required, and no published mapping, a required requirement with no entry, or an inconsistent mapping |
| `APPLICABILITY_UNKNOWN` | applicability could not be decided |
| `EVIDENCE_CONFLICTING` | the same item answered differently |
| `EVALUATION_UNSUPPORTED` | the combination or the kind of evidence has no evaluation |
| `HUMAN_ASSESSMENT_PENDING` | evidence exists and needs a person's assessment (one value more than the owner's list: it is none of the others) |
| `INTEGRITY_FAILED` | the journey's evidence or replay could not be trusted |
| `NOT_REQUIRED` | not applicable |

Coverage of the journey:

| Journey coverage | When |
|---|---|
| `COMPLETE_WITHIN_POLICY_SCOPE` | a policy is named, it is `DECLARED_COMPLETE`, the application is `IN_SCOPE`, the evidence is trusted, no instance is `APPLICABILITY_UNKNOWN`, and every `REQUIRED` instance is `EVIDENCED`. With no required instance at all: only if the policy says `empty_set_is_complete` |
| `INCOMPLETE` | the same preconditions, and some required instance is not `EVIDENCED` or some applicability is unknown |
| `NOT_ASSERTED` | anything else, with the reason: `NO_POLICY`, `POLICY_PARTIAL`, `OUT_OF_POLICY_SCOPE`, `POLICY_SCOPE_UNKNOWN`, `EVIDENCE_NOT_TRUSTED`, `EMPTY_APPLICABLE_SET` |

Complete coverage says: *within this policy's declared scope, every control it requires has trustworthy evaluation
evidence.* It does not say the controls are satisfied, and it is never inferred from every survey question having
been answered.

## Part 8 — Answer types (Step 8)

| Survey Studio type | Existing evaluator | In EVAL-2A |
|---|---|---|
| Yes/No | `EXACT_BOOLEAN` | supported (EVAL-1) |
| Acknowledgement | `ACKNOWLEDGEMENT` | supported (EVAL-1) |
| Numeric | `NUMERIC_COMPARE`; `NUMERIC_MATCH_POLICY_FACT` needs policy facts (G-E4) | supported; fact-based gives `MISSING_EXPECTED_FACT` |
| Single choice | `ENUM_MATCH` (accepted options); `ENUM_MATCH_POLICY_FACT` needs policy facts | supported — verified in EVAL-2A |
| Free text | `NARRATIVE_REVIEW` → `HUMAN_ASSESSMENT_REQUIRED`; `COLLECT_ONLY` | supported: it is never judged automatically |
| Statement | no answer; delivery evidence | supported (EVAL-1) |
| **Multiple choice** | **no method exists** | **not evaluated.** A new operator is needed and is PROPOSED below, not built |

**Update after the owner's decision of 2026-11-22 (D-299):** `SET_MATCH` was approved and is built in the existing
`answer_evaluation.py`, with exactly the four modes proposed here. Multiple choice is now evaluated; the row above
describes the state when this note was written. Contract §18.6 has the exact semantics.

**Update on storage (D-298):** the first draft of migration `0034` put the obligation key on the EVAL-1 result tables.
That was withdrawn. Policy-scoped results are stored in their own new tables and the EVAL-1 tables are not altered;
see `41_EVAL-2A_MIGRATION_0034_COMPATIBILITY_REPORT.md`.
