# SS-03A — Survey definition foundation: specification

**Requested by:** owner, 2026-11-21, "UC-02 Review and Backend Decision Closure" (D-175).
**Status: SPECIFICATION ONLY — PROPOSED, for the owner's review. NOT AUTHORISED FOR IMPLEMENTATION.** No backend,
database, migration, API or runtime file was changed to produce it. SS-03A must not begin until the owner authorises
it by name.

**Purpose.** The smallest backend that makes a survey definition real: stored, validated, hashed, submitted as an
immutable candidate, approved and published — and nothing that depends on an open business decision.

---

## 0. Boundary

### In scope (the six items the owner named)

1. Canonical versioned graph documents.
2. Immutable drafts, candidates and published content.
3. Content hashes and manifest validation.
4. Server validation.
5. The deterministic condition engine.
6. Minimal FastAPI contracts.

### Out of scope — explicitly

| Excluded | Why | Where it belongs |
|---|---|---|
| Any non-answer behaviour: silence, refusal, repeats, timeouts, disconnection | Gate G-3 is unresolved | A later checkpoint, after the rulings |
| Execution of a survey: the harness, runs, call-plan assembly, simulation on the server | Kept apart so SS-03A stays small | SS-03B (proposed) |
| Live-call controls: gate enforcement, live eligibility, assignment to cases | Policy undecided; operational | Later |
| Telephony, voice, delivery, recordings, Voice Lab | SS-D-17: runtime last | Last |
| Destructive database changes: dropping, renaming, re-seeding, rewriting any existing table or row | AD-2 preconditions not met; needs its own checkpoint | Destructive checkpoint |
| Script Studio removal or modification, in any repository | Not authorised | Retirement checkpoint |
| Changes to any existing endpoint, table, permission or engine | SS-03A is additive | — |
| Survey Studio screens on the real API | Depends on SS-03A | A later frontend checkpoint |
| Assignment rules, findings policy, evaluation configuration, control links | Independently governed artefacts (D-167) | Later |
| Controlled-variable rendering | Needs the allowlist (PB-3) and belongs with plan assembly | SS-03B |

**SS-03A changes no behaviour of the running product.** Its tables are new, its endpoints are new, and both sit
behind a server-side setting that is off by default.

### Decisions SS-03A depends on

It can be built on the **mechanisms** proposed in `25_UC-02_DECISION_CLOSURE.md` §2 without the policy content.

| Needs, before it starts | Does not need |
|---|---|
| Approval of TS-1…TS-23 as amended (`25_…` §1) | The list of permitted spoken fields (PB-3) — stored as a flag, all false |
| Approval of the mechanisms PB-1, PB-2, PB-4, PB-7, PB-9 | The obligation classes (PB-5) — a governed catalog with synthetic entries |
| Approval of the mechanism of PB-5, PB-8, PB-10, PB-12 (fields and catalogs, not their contents) | The outcome list (PB-10, PB-12) — a governed catalog with synthetic entries |
| Approval of the mechanism of PB-6 (a separate permission; most restrictive identity rule) | Who holds Publisher — no production role is granted it |
| | Every non-answer ruling (PB-11 reserves a route key and nothing else) |

---

## 1. Canonical versioned graph documents

### 1.1 Document kinds

Each is a JSON document with a `schema` identifier, validated against that schema, stored whole, and hashed.

| Kind | Identity | Contains |
|---|---|---|
| Option set version | `code`, `version` | Ordered options: `code`, `label`, `exclusive?`, `is_other?`, `other_text?`, `interrupt?` |
| Item version | `code`, `version` | `kind` (`QUESTION` \| `STATEMENT`), `answer_type`, `intent`, option set reference, `selection?`, `text_rule?`, `number_rule?`, `statement_role?`, `lifecycle_role?`, `response_obligation?` |
| Wording version | `item code`, `language`, `wording_version` | `text`, `option_texts?`, `delivery_mode`, `asset?`, `binds_to` (answer type and option codes), approval record |
| Condition version | `code`, `version` | Typed `ast`, `params`, `inputs` |
| Module version | `code`, `revision` | `name`, `kind`, `outcomes[]`, `entry`, `nodes[]`, `edges[]` — the module graph as **one document** (D-162) |
| Survey content | survey id + draft revision, or candidate, or version | `sequence[]` of module instances: module reference, `activation?`, `eligibility?`, `if_ineligible?`, `if_skipped_in_sequence?`, `routes{}` |

The shapes are those of the contract (`04_…` §1–§8) and the fixtures; SS-03A adds no field of its own except those
of `25_…` §1–§2.

### 1.2 Canonical form

One function produces the canonical bytes of any document, and the hash is taken over those bytes:

- UTF-8; object keys sorted by code point; no insignificant whitespace; arrays in their stored order (array order is
  always meaningful: option order, node order, sequence);
- numbers written without exponent and without trailing zeros; integers as integers; **no floating-point
  arithmetic on a stored number** — decimal values are held and compared as decimals;
- absent optional fields are absent, never `null`; a field at its default is written, not omitted, except where the
  contract says the absent form is canonical;
- the existing `app/domain/digest.py` `sha256_of` is reused if, and only if, a test proves it produces these bytes
  for every fixture; otherwise a new function is written beside it and the old one is left untouched.

### 1.3 Versioning rules

- A version is never changed after it leaves draft. A change is a new version.
- The schema identifier of a document is part of the document. A reader refuses a schema it does not know.
- Schema version 1 restricts condition inputs to yes/no and choice answers (TS-10); the restriction is checked, with
  an explicit error, and is written so that a later version can lift it.

---

## 2. Immutable drafts, candidates and published content

### 2.1 Entities

| Entity | Mutability | Holds |
|---|---|---|
| **Survey** | Name, purpose, owner may change | Identity only |
| **Draft** | Mutable; exactly one per survey; `revision` increases by one per accepted operation | The working survey content, and the working copies of any draft assets it owns |
| **Asset version** (item, wording, option set, condition, module) | Insert-only once not draft | One document, its hash, its state `DRAFT` \| `FROZEN` |
| **Candidate** | **Insert-only.** No column is ever updated | `id`, `n`, survey, content document, manifest, `content_sha256`, `manifest_sha256`, `submitted_by`, `submitted_at`, note, acknowledgements |
| **Version** | **Insert-only** | `id`, survey, `label`, the candidate it was made from, `effective_from?` |
| **Lifecycle event** | **Append-only** | `subject` (candidate or version), `event`, `actor`, `at`, `reason`, details |

### 2.2 Lifecycle as history (TS-12, amended)

Status is derived from the events of a subject, never stored as an updated column.

| Subject | Events |
|---|---|
| Candidate | `SUBMITTED` → `APPROVED` \| `REJECTED` \| `WITHDRAWN` \| `SUPERSEDED` → `PUBLISHED` |
| Version | `SCHEDULED?` → `PUBLISHED` → `SUPERSEDED` \| `WITHDRAWN` |

`SCHEDULED` and version `WITHDRAWN` are accepted as events and reported as states. **SS-03A attaches no behaviour to
them**: nothing takes effect on a date, and withdrawing changes nothing else (D-165).

### 2.3 Rules

1. Submitting freezes every draft asset the content pins, builds the manifest, and inserts a candidate. The draft
   stays editable (PB-7).
2. Submitting again creates the next candidate and appends `SUPERSEDED` to an open one. No approval is carried over.
3. A draft made identical to an earlier candidate is not approved: approval belongs to a candidate id.
4. **Identity rules**, checked on every decision and publication, independently of permissions: the approver is not
   a maker of the candidate; the publisher is not its submitter; and, until ruled otherwise, the publisher is not its
   approver (PB-6).
5. A blocker cannot be acknowledged. A warning needs a recorded reason. Acknowledgements are part of the candidate.
6. A candidate containing conversational delivery, or a recording without an approved asset, cannot be created
   (TS-4, TS-5).
7. Every decision writes one lifecycle event **and** one event on the existing audit hash chain.

### 2.4 Storage (additive only)

- New tables with a `survey_` prefix. **No existing table is altered, read for migration, renamed or dropped.** No
  foreign key points at a script table.
- Insert-only and append-only tables use the existing `forbid_change_trigger` helper; the draft uses the existing
  `row_version` convention.
- One additive Alembic revision, with a working downgrade while the tables are empty.
- A derived **usage index** — which candidate or version pins which asset version — is rebuilt from manifests and is
  never the source of truth (D-162).
- The governed catalogs of `25_…` §2 (response obligation, outcomes, the `speakable` flag) are created with
  synthetic entries only, clearly marked.

---

## 3. Content hashes and manifest validation

- **Asset hash:** SHA-256 of the canonical bytes of an asset version.
- **Manifest:** the list of every asset version a survey content pins, directly or through a module — `{kind, code,
  version, sha256}` — sorted by kind, code, version.
- **Manifest hash:** SHA-256 of the canonical bytes of the manifest. **Content hash:** SHA-256 of the canonical
  bytes of the survey content document.
- **Verified at three moments:** on submission (built), on decision and on publication (recomputed from the stored
  rows and compared). A difference is `MANIFEST_MISMATCH` and the action is refused.
- **Completeness:** every reference in the content resolves to exactly one manifest entry; every manifest entry is
  referenced. Missing or surplus entries are errors.
- A published version's hashes are never recomputed into the record: they are only ever compared.

---

## 4. Server validation

One validator, run on a draft or a candidate, returning findings with **stable codes** — never matched by message.

| Area | Rules | Verified by |
|---|---|---|
| Structure | Entry exists; every node reachable; no cycle; every path ends | F, G fixtures; prototype tests |
| Routing | Every answer has a destination; one route per answer; edge resolution "specific, then `ANY`"; single-route items (TS-2) | F1–F5, K2 |
| Items and nodes | Node and item kinds agree; a statement is not mandatory and has no question role; number rule consistent | K2 |
| Conditions | Typed operands; parameters bound; inputs available on every path or with a stated UNKNOWN policy; version-1 input types only | F6, F8, G |
| Survey | Activation and eligibility independent; skip dispositions; forward-only routes | G, H |
| Escalation | A mandatory escalation ends with an escalation outcome; Escalate is terminal in every routing mode | H, J1 |
| Wording | Unknown, unusable or unfinished variable; conversational delivery; recording without an asset; recording with a variable | K6 |
| Dependencies | Every pinned version exists and is frozen; manifest complete | New tests |

**Work this item includes.** Rules that predate UC-01 are identified in the prototype by their message. SS-03A
assigns each a stable code and records the list in the contract before the validator is written. The codes already
fixed by fixtures (`04_…` §8.4, and `ESCALATION_NOT_TERMINAL`, `MANDATORY_ESCALATION_OVERRIDDEN`) are kept as they
are.

Severity is `BLOCKER`, `WARNING` or `INFO`. The validator decides nothing about live eligibility.

---

## 5. The deterministic condition engine

A pure function: `evaluate(condition version, binding, facts, answers) → TRUE | FALSE | UNKNOWN` with an explanation
tree.

- **Operators:** `AND`, `OR`, `NOT`; `EQ`, `NEQ`, `GT`, `GTE`, `LT`, `LTE`; `INCLUDES_ANY`, `INCLUDES_ALL`,
  `INCLUDES_NONE` on a multiple-choice answer.
- **Operands:** a catalog field; a named parameter supplied by the binding; a named earlier answer; a literal.
  Literals compared with answers are option codes, never labels.
- **Three values.** A missing fact or an unanswered question is `UNKNOWN`, never `FALSE`. An answered
  multiple-choice question with nothing selected is a known empty selection. `AND` and `OR` short-circuit on a known
  deciding operand.
- **UNKNOWN is never resolved by the engine.** The binding's stated policy says what the caller does with it; the
  engine only reports it.
- **Decimals, not floats**, for every numeric comparison.
- **No expression language, no code, no free text.** The AST is the whole language.
- **Extensible by construction (TS-10):** an input's answer type is declared; an unsupported type is an explicit
  error.
- **Verified by** F6, F8, G1–G6, H1–H4 and K8, run as backend tests against the same JSON files.

It is written as a new pure module. The existing assignment-rule evaluator and the legacy script predicates are
**not** changed or replaced in SS-03A.

---

## 6. Minimal FastAPI contracts

All under `/api/v1`, with "survey" vocabulary (D-166).

> **A naming conflict the owner should know about.** The natural collection path for a survey would be the plural of
> "survey" directly under `/api/v1`. That exact path, and the same path with `GET`, are on the specs validator's
> list of **prohibited terms**: they were the legacy names retired by ADR-0007 in favour of the script routes. D-166
> asks for Survey terminology in new APIs but does not lift that prohibition, and the naming rules may only be
> changed explicitly, by an ADR. **This specification therefore uses `/survey-definitions`**, which is unambiguous
> and breaks no rule. If the owner prefers the shorter path, that is a naming decision needing an ADR amendment and
> a change to the validator's list — it is not made here. Authorization by `require(permission)` on every route and
object; CSRF and rate limiting as for existing write routes; market scope `SG`. **Fifteen operations.**

| Method and path | Permission | Does |
|---|---|---|
| `POST /survey-definitions` | `survey.edit` | Create a survey and its empty draft |
| `GET /survey-definitions` | `survey.read` | List surveys with derived status |
| `GET /survey-definitions/{id}` | `survey.read` | One survey: draft revision, open candidate, latest version |
| `GET /survey-definitions/{id}/draft` | `survey.read` | The draft content document and its revision |
| `POST /survey-definitions/{id}/draft/operations` | `survey.edit` | Apply one authoring operation; body carries `expected_revision`; a stale revision is refused with `STALE_DRAFT` |
| `POST /survey-definitions/{id}/draft/validate` | `survey.edit` | Findings for the draft |
| `POST /survey-definitions/{id}/candidates` | `survey.edit` | Submit: freeze, build the manifest, insert a candidate |
| `GET /survey-candidates/{id}` | `survey.read` | Candidate: content, manifest, hashes, derived status, history |
| `POST /survey-candidates/{id}/decision` | `survey.approve` | Approve or reject, with comment |
| `POST /survey-candidates/{id}/withdraw` | `survey.edit` | Withdraw an open candidate (its submitter) |
| `POST /survey-candidates/{id}/publish` | `survey.publish` | Publish an approved candidate; optional `effective_from` recorded only |
| `GET /survey-versions/{id}` | `survey.read` | Version, its hashes and history |
| `GET /survey-versions/{id}/content` | `survey.read` | The published content document |
| `GET /survey-library/{kind}` | `survey.read` | Frozen asset versions of one kind, with where each is used |
| `POST /survey-conditions/evaluate` | `survey.read` | Evaluate one condition against supplied facts and answers; returns the three-valued result and its explanation. Read-only; writes nothing |

**Permissions.** `survey.read`, `survey.edit`, `survey.approve`, `survey.publish` are four **new** permissions.
`survey.publish` is never granted with `survey.approve`. For local synthetic development they are granted to
clearly named development roles only; **no production role mapping is defined by SS-03A** (PB-6 is a business
ruling). The existing `script.*` permissions are untouched.

**Errors** are stable codes: `STALE_DRAFT`, `VALIDATION_BLOCKED`, `MANIFEST_MISMATCH`, `SELF_REVIEW_DENIED`,
`SELF_PUBLISH_DENIED`, `APPROVER_PUBLISH_DENIED`, `NOT_APPROVED`, `ALREADY_DECIDED`, `UNKNOWN_SCHEMA`.

**Contract.** The backend regenerates OpenAPI; the change is additive only. The frontend client is regenerated in
the same checkpoint so the drift check stays green, but **no screen calls these endpoints in SS-03A**.

**Setting.** A server-side setting, off by default, registers the routes. With it off the product is exactly as it
is today.

---

## 7. Acceptance tests for SS-03A

| # | Test | Passes when |
|--:|---|---|
| 1 | Canonical bytes | The same document always gives the same bytes; key order and whitespace do not change the hash; array order does |
| 2 | Fixture documents | Every library and survey document of the 27 fixtures validates against its schema and hashes stably |
| 3 | Validator against fixtures | K2 and K6 give exactly their expected codes; J1 gives its three; valid fixtures give none |
| 4 | Condition engine against fixtures | Every condition evaluation implied by F6, F8, G, H and K8 gives the expected value |
| 5 | Immutability | An update or delete of a candidate, a version, a frozen asset or a lifecycle event is refused by the database |
| 6 | Manifest | A tampered asset is detected at decision and at publication |
| 7 | Identity rules | A maker cannot approve; a submitter cannot publish; an approver cannot publish; holding all permissions does not help |
| 8 | Supersession | Submitting a changed draft supersedes an open candidate; an old approval cannot be used; an identical draft is not approved |
| 9 | Concurrency | A stale `expected_revision` is refused and changes nothing |
| 10 | Authorization | Every route refuses a user without its permission; every object check holds |
| 11 | Audit | Every transition appears on the hash chain; the chain verifies |
| 12 | Additivity | The existing backend suite passes unchanged; no existing table, endpoint or permission differs; OpenAPI diff is additions only |
| 13 | Migration | Applies and reverses on the isolated test database |
| 14 | Setting off | With the setting off no survey route is registered |

Synthetic data only. Tests run against the isolated test database. **The development database is not migrated,
re-seeded or otherwise touched by SS-03A's tests.**

---

## 8. Risks and notes for the authorisation

| Risk | Handling |
|---|---|
| Applying the additive migration to the development database | Not part of the tests. If the owner wants it applied, it is a separate, explicit step with a backup first, as on earlier checkpoints |
| Two definition stores while Script Studio still exists | Accepted for the transition (D-155: no two **long-lived** stores). SS-03A's tables are unused by the product until a later checkpoint |
| A second hashing function | Avoided if `sha256_of` is proven to match; otherwise the new one is confined to survey documents |
| Catalogs with synthetic entries mistaken for approved policy | Entries carry the existing "synthetic, unapproved" marking; nothing can be published for live use from them |
| Scope growth into execution | Runs, plan assembly and variable rendering are named as SS-03B and excluded here |

### Suggested split, if the owner wants smaller steps

| Step | Contents | Touches the database |
|---|---|:-:|
| SS-03A.1 | Canonical documents, hashing, schemas, validator, condition engine — pure modules and tests | No |
| SS-03A.2 | Tables, immutability, publication service, manifest verification | Test database only |
| SS-03A.3 | The fifteen operations, permissions, OpenAPI, client regeneration | Test database only |

**SS-03A is not started. It requires the owner's explicit authorisation by name.**
