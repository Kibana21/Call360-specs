# APPL-X2 — the governed Applicability library: architecture, API and migration 0038

**Status: ACCEPTED as technically verified on the test schema (D-401, 2026-11-24). Migration `0038` was then applied
to local development on the owner's authorisation (D-407; report `62_…`).** Uncommitted.

Authorisation: the owner's message of 2026-11-23, "Accept APPL-X1R and Implement APPL-X2: Governed Reusable
Applicability Libraries" (D-393 … D-396). Report and evidence: `61_…`. Decisions it implements: `56_…` §14.

Scope: durable persistence and **server-enforced three-person publication** for variables, application profiles
and reusable conditions. Applicability **policies and scenarios are not stored** (APPL-X3 / X4): they stay in the
browser tab and their approval remains a labelled simulation.

Not used, not read, not written: assignment rules, survey bindings, requirement groups, their tables and their
selection code. The evaluator (`app/domain/survey/applicability/logic.py`, `evaluator.py`, `analysis.py`) is
**unchanged** by this checkpoint.

---

## 1. Schema — four tables, justified

| Table | Holds | Why it is needed |
|---|---|---|
| `applicability_asset` | one reusable thing: market, kind (`VARIABLE` / `PROFILE` / `CONDITION`), code — none of which ever changes — **and its one working draft** (`draft`, `draft_revision`, who saved it, which version it started from) | stable identity and market ownership |
| `applicability_asset_version` | an immutable **candidate** frozen at submission, which becomes a published **version** (`version_no` set at publication). Document, manifest, both fingerprints, the draft revision it was frozen from; who submitted, decided and published | candidates, immutable versions, three identities |
| `applicability_asset_dependency` | the exact published versions a candidate pins | integrity of references by foreign key, and an indexed "where used" |
| `applicability_event` | append-only lifecycle history | audit of the asset itself (the platform audit chain is written as well) |

### 1.1 Is a separate draft table necessary? No.

The proposal named `applicability_asset`, `applicability_asset_version` and `applicability_event`. I reviewed
whether drafts need a table of their own and concluded they do not:

* there is exactly **one** working draft per item (two people editing is handled by optimistic concurrency, not by
  two drafts), so a draft is a 1:1 extension of the asset row;
* a draft is mutable working state with a monotonic `draft_revision`; saving is `UPDATE … WHERE` the expected
  revision under a row lock, which is the whole of optimistic concurrency;
* draft history that matters is kept without a table: every save writes an `applicability_event` and an audit
  record, and what was actually reviewed is the frozen candidate.

A draft table would add a join to every read and a second place for the revision counter, and buy nothing.

### 1.2 Why a dependency table was added to the proposal

The three proposed tables could hold pins inside the manifest JSON only. I added one small table because the owner
asked for database-level integrity and for dependency references:

* a pin is then a **foreign key** to a version row, not text;
* one trigger enforces — whatever the application does — that a pin is on a version that is **already published**,
  of **another** asset, of the **same market**, and is written only at submission. Because a version can only ever
  pin versions published before it, **the published graph cannot contain a cycle**, and no pin can cross a market;
* "where is this used" is an indexed lookup instead of a scan of every manifest.

The manifest still lists the same pins with their fingerprints, so a version is self-describing.

### 1.3 Variables are never copied

A profile's document names variables by code; a condition's expression names variables by code and saved conditions
by code **and version**. No variable definition is stored inside a profile or a condition. What a published version
meant is fixed by its pins: `(kind, code, version_no, version_id, content_sha256)`.

## 2. Integrity enforced by the database

| Rule | Enforced by |
|---|---|
| identity unique per market and kind, whatever the letter case | unique index on `(market_code, kind, lower(code))` |
| market, kind, code, creator never change; an asset is never deleted | `applicability_asset_guard` |
| a draft revision never goes back | `applicability_asset_guard` |
| a version starts as a `SUBMITTED` candidate | `applicability_version_guard` (insert) |
| document, manifest, fingerprints, submitter never change | `applicability_version_guard` (update) |
| who decided and who published never change once set; `version_no` never changes | `applicability_version_guard` |
| only `SUBMITTED → APPROVED / RETURNED / WITHDRAWN`, `APPROVED → PUBLISHED / WITHDRAWN`, `PUBLISHED → SUPERSEDED` | `applicability_version_guard` |
| a version is never deleted | `applicability_version_guard` |
| **the decider is not the submitter** | `CHECK ck_applicability_version_not_self_decided` |
| **the publisher is neither the submitter nor the decider** | `CHECK ck_applicability_version_third_publisher` |
| a published version has a number, a decider and a publisher | two `CHECK`s |
| one open candidate per asset; one current published version per asset | two partial unique indexes |
| a pin is on a published version of another asset of the same market, written at submission only, never changed | `applicability_dependency_guard` |
| history is append-only | `applicability_event_guard` |

The service refuses the same things first, with a message for the person; the table is the backstop.

## 3. Lifecycle

```
create ──► DRAFT ──save(expected revision)──► DRAFT ──submit──► SUBMITTED ──approve──► APPROVED ──publish──► PUBLISHED vN
             ▲                                   ▲                  │  │                  │                      │
             │                                   └── return ────────┘  └── withdraw ──────┘                      │
             └─────────────── start a new draft from a published version ◄──────────────────────────────────────┘
```

| Step | Who | Refused when |
|---|---|---|
| create, save, discard, start a draft, submit, withdraw | `applicability.edit` | another market; code taken; stale revision (409 `STALE_REVISION`, with who saved and the current revision); a candidate is open (409 `CANDIDATE_OPEN`); a blocker (422 `NOT_VALID`, with the diagnostics); identical to the published version (409 `NOTHING_CHANGED`) |
| approve / return | `applicability.approve` | the caller submitted it (403 `SELF_REVIEW_DENIED`); a return without a comment of 10 characters |
| publish | `applicability.publish` | the caller submitted it (403 `SELF_PUBLISH_DENIED`) or approved it (403 `APPROVER_PUBLISH_DENIED`); not approved; a pin is no longer exactly what was pinned (409 `DEPENDENCY_CHANGED`) |
| read | `applicability.read` | — |

A refusal by an identity rule is **itself recorded** (`DENIED` event and an audit record with outcome `DENIED`).
While a candidate is open the draft is locked for everyone. Publication assigns the next `version_no`, marks the
previous version `SUPERSEDED` (it stays readable, byte for byte) and clears the draft.

### 3.1 Validation and pinning at submission

For every reference in the draft: the item must exist **in the same market** (`UNKNOWN_REFERENCE` otherwise — an
item of another market does not exist for this one), must not be the item itself (`DEPENDENCY_CYCLE`), and must
have a published version (`UNPUBLISHED_DEPENDENCY`). A variable or a profile is pinned at its latest published
version; a saved condition at the **exact version the expression names**, which must be a published one
(`UNKNOWN_CONDITION_VERSION`). Then the evaluator's own analysis is run on the document (types, allowed values,
currency, derived variables, profile composition and conflicts, expression structure, contradictions) and its
blockers stop the submission. **A draft is therefore never a published dependency.**

### 3.2 Fingerprints

`content_sha256` is the SHA-256 of the canonical JSON of the document (key order does not matter).
`manifest_sha256` is that of `{contract, evaluator, market, kind, code, content_sha256, pins}`. Both are
reproducible from the row and are tested as such.

## 4. Permissions and markets

Four permissions, **created by the migration and granted to no role**: `applicability.read`, `.edit`, `.approve`,
`.publish`. They are independent of `survey.*` and `script.*`: holding every survey permission opens nothing here,
and the reverse. No standing role (ADMIN, USER, SC checker, any survey role) gains anything.

Every read and write is scoped to the caller's markets. An item, candidate or version of another market answers
**404**, not 403: its existence is not disclosed. Creating in, or reading the workspace of, a market the caller is
not in answers 403 `MARKET_NOT_IN_SCOPE`.

## 5. API — fourteen operations under `/api/v1/applicability`

Registered only when `applicability_library_enabled` is on (off by default). Writes are CSRF-protected,
rate-limited and audited.

| Operation | | Permission |
|---|---|---|
| `GET /assets?kind=` | list, with draft, open candidate and published version | read |
| `POST /assets` | create with a first draft | edit |
| `GET /assets/{id}` | detail: every version with its pins, history, where used, diagnostics, newer pins | read |
| `PUT /assets/{id}/draft` | save with `expected_revision` | edit |
| `POST /assets/{id}/draft` | start a draft from a published version | edit |
| `POST /assets/{id}/draft/discard` | discard the draft | edit |
| `POST /assets/{id}/validate` | diagnostics and pins for the saved draft or an unsaved edit; writes nothing | read |
| `POST /assets/{id}/submit` | freeze a candidate; with `pins`, only if they are exactly what would be frozen (409 `PINS_CHANGED` otherwise; D-405) | edit |
| `POST /candidates/{id}/decision` | approve or return | approve |
| `POST /candidates/{id}/publish` | publish | publish |
| `POST /candidates/{id}/withdraw` | the submitter takes it back | edit |
| `GET /versions/{id}` | one candidate or version, as frozen | read |
| `GET /workspace?market_code=&view=` | the library as the evaluator reads it. `published`: published versions only. `authoring`: a draft stands in for its item, marked `DRAFT` | read |
| `POST /test` | TRUE / FALSE / UNKNOWN for an expression and synthetic facts against the **persisted** library, with the trace | read |

OpenAPI: 14 operations and 22 schemas added (21 with APPL-X2, one for the acknowledged pins of D-405); nothing existing changed.

## 6. How the persisted library meets the evaluator

`GET /workspace` returns `{variables, profiles, conditions}` in exactly the shape the evaluator already reads; a
condition carries every earlier published version in `history`, so a reference to version 1 keeps meaning
version 1 after version 2 is published. The in-memory policy of the prototype is evaluated against it by the
existing stateless operations. No evaluation happens in the browser.

**Facts (D-394).** A fact is read only for a *registered* variable, only when the policy (or the expression) reads
it, after its type and allowed values are checked; a fact from outside the stated profiles is read and marked
`outside_profiles`. Any other field of a request is never a fact. This was already the evaluator's behaviour; it is
now covered by tests against the persisted library.

## 7. Migration `0038_applicability_library`

One additive revision after `0037_shared_rule_services`: four tables, three indexes besides the keys, four
functions and triggers, four permission rows. **No existing table, column, row, trigger or permission is altered.**

| Tested on a populated test schema | Result |
|---|---|
| upgrade | the listed objects, nothing else |
| downgrade while empty | removes exactly those objects; every other table is byte-identical (row count and content digest of every non-applicability table) |
| forced partial failure | a colliding permission row makes the **last** statement fail after every table, index, function and trigger was created: everything is rolled back, the revision stays `0037` |
| upgrade again | identical objects; every other table byte-identical |
| downgrade with governed content | **refused** ("applicability library items exist"); nothing lost |
| downgrade while a role holds one of the permissions | refused by the same guard as `0037` |
| existing protected-record fingerprints | unchanged: a survey published before the migration has the same content and manifest fingerprints after down, failed up and up |
| start-up | with the library off, a schema at `0037` is still accepted; with it on, readiness fails closed unless the schema holds `0038` |

### 7.1 Applying it to development (authorised and done on 2026-11-24 — `62_…`)

1. Preflight: database, schema and revision (`0037` expected); inventory of tables and rows.
2. Backup with `pg_dump`, SHA-256, row-for-row check, restore-to-SQL dry run — as for `0037`.
3. `alembic upgrade 0038_applicability_library` on schema `call360` only.
4. Verify: four tables, four permissions held by no role, every other table's digest unchanged.
5. Only then, and only if separately approved: `APPLICABILITY_LIBRARY_ENABLED=true`, dedicated development
   identities holding the applicability permissions, and the showcase library through
   `scripts/appl_library_setup.py`. All three were authorised and done (D-407 … D-409).

Recovery: while the library is empty, `alembic downgrade 0037_shared_rule_services`. Once it holds governed
content the downgrade refuses, and the way back is the full restore from the backup.

## 8. Frontend integration

Build setting `VITE_APPLICABILITY_LIBRARY=1`. Without it (as in local development today) the three library screens
behave exactly as in APPL-X1R, in the tab.

With it, `src/features/applicability/library.tsx` is the only code that talks to the library API:

* the tab's copy of variables, profiles and conditions is **what the server returned**; the built-in example is
  not loaded at all;
* an item changed in the tab is compared with what is saved and shown as **Unsaved**; saving sends the revision it
  was opened at; a refusal shows who saved first and offers two explicit choices — load theirs, or save mine as the
  next revision. Nothing is overwritten silently, and unsaved work in the tab is never replaced by a refresh;
* each item shows one bar: Saving · Draft saved · Unsaved · Not saved (someone else saved first) · Submitted ·
  Approved · Returned (with the reason) · Published, with the actions the **signed-in** person may take, the
  blockers, every version with its exact pins and fingerprint, and the history;
* a variable or a condition created from inside the Applicability Designer is saved as a draft at once and the
  person stays in the requirement they were editing;
* a new reference to a saved condition names its **published** version, never a work-in-progress draft.

The policy and scenario store is unchanged and every label that concerns it says "in this tab only".
