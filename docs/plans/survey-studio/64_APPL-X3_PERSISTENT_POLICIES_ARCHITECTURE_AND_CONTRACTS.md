# APPL-X3 — persistent Applicability Policies: architecture, contracts and migration 0039

**Status: BUILT AND VERIFIED ON THE ISOLATED TEST SCHEMA 2026-11-24. Migration `0039` is NOT applied to local
development and must not be without the owner's separate approval.** Uncommitted.

Authorisation: the owner's message of 2026-11-24, "APPL-X3: persistent Survey Applicability Policies" (D-411 …
D-418). Report and evidence: `65_…`. Builds on `60_…` (library, `0038`) and `56_…` §14 (policy semantics).

Scope: an Applicability Policy is saved in PostgreSQL as a **working draft**, with the exact dependencies it was
saved against. **Publication of policies is not here** (APPL-X4): no candidate, no approval, no published policy
version exists in this schema. Scenarios stay in the browser tab.

Not used, not read, not written: assignment rules, survey bindings, requirement groups, their tables and their
selection code. The evaluator (`logic.py`, `evaluator.py`, `analysis.py`) is **unchanged**.

---

## 1. The policy document — one coherent document

```json
{ "name": "…", "description": "…",
  "profiles": ["new_business"],
  "scope": null,
  "requirements": [ { "id": "r1", "name": "…", "when": {"op":"ref","condition":"is_ilp","version":1},
                      "action": {"kind":"INCLUDE","surveys":[ { "code":"S-APPL-DEMO-ILP","version":1,"label":"1.0",
                        "version_id":"…","definition_id":"…","fingerprint":"…","manifest":"…","market":"SG" } ]},
                      "replaces": [] } ],
  "shared_deliveries": [], "order": ["S-APPL-DEMO-ILP"],
  "pins": [ {"kind":"VARIABLE","code":"product_family","version":1},
            {"kind":"CONDITION","code":"premium_case","draft_revision":2} ] }
```

Market and code are the row's and never change. Conditions, actions, replacement, choose-one, shared deliveries and
delivery order are exactly those of APPL-X1R (`56_…` §3–5, §14). No priority, no first match, no requirement-group
winner, no hidden binding, no second rules engine. The Card Composer, the Graph and the Matrix edit and draw this
one document; none keeps a copy.

## 2. Dependency intent (owner ruling X3-1) — where each exact version lives

| Dependency | Where the exact version is stated |
|---|---|
| a reusable condition (direct, or inside another condition) | in the expression: `{"op":"ref","condition":…,"version":N}` |
| a condition that is still a draft | the reference names the draft's number; `pins` carries its **draft revision** |
| a variable — read directly, through a condition, or through a derived variable | `pins`: a published `version`, or a `draft_revision` |
| a profile of the policy, and every profile it builds on | `pins` |
| a survey | the reference itself: Survey Studio version id, number, content and manifest fingerprints |

`pins` is **part of the document**. That is deliberate: adopting a newer version is then an ordinary edit — visible,
saved with a new revision, recorded in the history, and **undoable** like any other.

**The server completes and validates the pins on every save.** It walks the document, finds everything it reads
(transitively), and for each item takes the pin the document states; an item with no pin yet — one just added —
is pinned at the published version current at that moment, or at its current draft revision if it has never been
published, and the completed list is what is stored and returned. After that, **nothing is ever resolved to "the
latest" again**: not on reload, not on evaluation, not when a newer version is published.

### 2.1 One version of each variable per evaluation

A published condition records which variable versions it was published against. A policy evaluates **one** version
of each variable — its own pin — because one evaluation has one definition of a fact. When the two differ, the
policy says so (`PIN_DIFFERS`: "condition C version 1 was published reading X version 1; this policy evaluates X at
version 2"). It is information, not an error; the policy's pin is the stated intent. Recorded as D-416(a).

## 3. The dependency snapshot (Part 5)

Stored with the draft (`snapshot`, with its SHA-256), and mirrored as rows:

| For a published library item | For a draft library item | For a survey |
|---|---|---|
| asset id · kind · code | asset id · kind · code | definition id · code · market |
| version id · version number | draft revision | version id · version number · label |
| content fingerprint · manifest fingerprint | content fingerprint of that revision · `state: DRAFT` | content fingerprint · manifest fingerprint |

The snapshot holds identities and fingerprints only — nothing that changes by itself — so the same document always
gives the same snapshot and the same `snapshot_sha256`.

### 3.1 When something a policy depends on moves

| What happened | What the policy shows | Evaluation of the saved draft |
|---|---|---|
| a newer **published** version exists | "version N available", on the dependency and on each requirement that uses it; **Adopt** | unchanged: still the pinned version, same fingerprint |
| a pinned **draft** was edited | "changed since saved": revision pinned, revision now; **Review done: accept revision N** | **refused** (`DEPENDENCY_STALE`) until reconciled |
| a pinned draft was **published** | "changed since saved … version N is published"; **Use published version N** | refused until reconciled — a draft pin is never silently read as the published version |
| a dependency is a draft | "unpublished"; the policy reads **"Draft contains unpublished dependencies — not ready for publication"** | allowed: a draft can be designed with |
| a pin names something that does not exist | — | the save is refused (422 `INVALID_DEPENDENCY_PIN`) |

A draft revision that has moved cannot be evaluated "as it was": a library draft is mutable working state and its
earlier text is not kept. So the server does not pretend: it refuses, says what changed, and the person reconciles
deliberately. The policy's stored document and snapshot do not change until they do.

### 3.2 Three kinds of evaluation, kept apart

| | What is evaluated | Marked |
|---|---|---|
| **Saved-draft evaluation** — `POST …/evaluate` | the stored revision, from exactly its snapshot | `source: SAVED`, revision, document and snapshot fingerprints |
| **Authoring preview** — `POST …/preview` | an unsaved document sent by the browser, resolved the same way | `source: PREVIEW`; never a result of the saved policy |
| Published-policy evaluation | — | does not exist yet (APPL-X4) |

Both use the same resolution and the one Python evaluator. The designer shows which one is on screen.

## 4. Schema — three tables (review of the proposal)

| Table | Holds |
|---|---|
| `applicability_policy` | identity (market, code — immutable), the one working draft (`document`, `snapshot`, both fingerprints, `draft_revision`, who saved), `archived_at` |
| `applicability_policy_dependency` | the snapshot as rows, each a **foreign key** |
| `applicability_policy_event` | append-only editing history |

**No separate draft table**, for the reason accepted in APPL-X2: one working draft per policy, a monotonic
revision, `UPDATE … WHERE` the expected revision under a row lock.

**A dedicated event table**, not an extension of `applicability_event`: that table's `asset_id` is `NOT NULL` and
its guard was accepted with `0038`; extending it would alter an accepted table. Three small columns of difference
do not justify that.

**No permission is added** (ruling X3-3).

### 4.1 Foreign keys — every reference has one

| Reference | Foreign key |
|---|---|
| library item | `asset_id → applicability_asset` |
| published library version | `asset_version_id → applicability_asset_version` |
| survey | `survey_definition_id → survey_definition` |
| published survey version | `survey_version_id → survey_version` |

Survey Studio's tables are in the same database and schema, so the cross-domain reference **is** constrained by a
foreign key; nothing had to be left to the server alone. It is the one stated reference from outside into Survey
Studio's tables: a reference only — no survey table, column, trigger or row is changed, and Survey Studio does not
depend on it. What a foreign key cannot say is enforced twice more: by a trigger on the dependency table (same
market as the policy; a survey, not a standalone module; the version belongs to that survey; a pinned library
version is a published version of that item and of that kind) and by the service on save (status `PUBLISHED` or
`SUPERSEDED`, code, version number and **both fingerprints** equal to Survey Studio's own).

A **superseded** survey version stays valid and reproducible: it is referenced by id, its content never changes,
and it is never replaced by the current one.

### 4.2 The document and its rows cannot diverge

A save computes the snapshot from the document and writes, in **one transaction**: the document, the snapshot, the
revision, the dependency rows (deleted and re-inserted from that same snapshot), the history event and the audit
record. Tested: a failure forced after the rows are written leaves no part behind; and `consistent()` proves the
rows equal the stored snapshot after every kind of save.

### 4.3 Integrity enforced by the database

| Rule | Enforced by |
|---|---|
| code unique per market, whatever the case | unique index on `(market_code, lower(code))` |
| market, code, creator never change; a policy is never deleted | `applicability_policy_guard` |
| the revision never goes back; a changed document is a new revision | `applicability_policy_guard` |
| a dependency row is a version **or** a draft revision **or** a survey, never a mixture | `CHECK ck_applicability_policy_dependency_shape` |
| references stay in the policy's market, of the right kind, on published versions | `applicability_policy_dependency_guard`, and the four foreign keys |
| a dependency row is replaced with its draft, never edited | `applicability_policy_dependency_guard` |
| history is append-only | `applicability_policy_event_guard` |

## 5. API — ten operations under `/api/v1/applicability/policies`

Registered only when `applicability_policies_enabled` **and** the library are on (off by default; needs `0039`).
Every operation needs `survey.read` as well (an explicit, read-only dependency: a policy names published surveys).

| Operation | | Permission |
|---|---|---|
| `GET` (list; `?archived=`) | saved policies of the caller's markets | read |
| `POST` | create a saved draft: blank, from a pattern, or a copy (`origin` recorded) | edit |
| `GET /usage?kind=&code=` | which saved policies depend on a library item or a survey, and at which version | read |
| `GET /{id}` | document, snapshot, history, and the inspection unless `?inspection=false` (the inspection runs the evaluator's whole analysis; the gallery reads documents only) | read |
| `PUT /{id}/draft` | save with `expected_revision` | edit |
| `POST /{id}/archive` · `/restore` | out of the gallery, with a reason; never deleted | edit |
| `POST /{id}/inspect` | pins, dependencies and their state, diagnostics per requirement, readiness — for the saved draft or an unsaved document; writes nothing | read |
| `POST /{id}/evaluate` | the SAVED revision for synthetic scenarios | read |
| `POST /{id}/preview` | an unsaved document for synthetic scenarios; optionally compared with the saved draft | read |

Refusals: 401 without a session; 403 without the permissions, and for another market on create
(`MARKET_NOT_IN_SCOPE`); **404 for another market's policy** on every operation; 409 `STALE_REVISION` (with who
saved and the current revision), `CODE_TAKEN`, `NOTHING_CHANGED`, `ARCHIVED`; 422 `INVALID_SURVEY_REFERENCE`,
`INVALID_DEPENDENCY_PIN`, `INVALID_CODE`, `NAME_REQUIRED`. Writes are CSRF-protected, rate-limited and audited; saving and computing (`inspect`, `evaluate`, `preview`) are limited separately, so live previews cannot use up the allowance to save. No
operation executes anything supplied by the user: a document is data, read by the evaluator.

OpenAPI: 10 operations and 15 schemas added; nothing existing changed.

## 6. Prototype operations (ruling X3-4)

| Operation | With saved policies | Decision |
|---|---|---|
| `…/prototype/evaluate` | **not used for a saved policy**: `evaluate` and `preview` replace it | kept for the in-tab mode |
| `…/prototype/analyse` | **not used for a saved policy**: `inspect` replaces it; still used for the library-wide check on the Profiles page | kept |
| `…/prototype/condition-test` | still used by the live test in the requirement editor and the Condition Lab (a stateless what-if on unsaved edits) | kept |
| `…/prototype/scenarios` | still used: scenarios are not saved; it is given the workspace the policy pins | kept, as ruled |

**None was removed in this checkpoint, and that is a finding, not an oversight.** The ruling allows removal "only
after confirming all frontend callers use their persisted equivalents". They do not yet: local development still
runs policies in the tab (its `0039` is not authorised), and the in-tab mode calls all four. All four stay behind
`survey_applicability_prototype_enabled`. Removal of `analyse` and `evaluate` becomes possible when saved policies
are the only mode. Recorded as D-416(c).

## 7. Frontend

Build setting `VITE_APPLICABILITY_POLICIES=1` (it requires the library setting). Without it — as in local
development today — policies behave exactly as before, in the tab.

* `policyService.tsx` is the only code that reads and writes saved policies; `policyStore.ts` holds what the server
  has, so the evaluation calls can tell the saved revision from an unsaved edit.
* **One document, one store.** The designer still edits the tab's document through the same `update` as before,
  so cards, graph and matrix are unchanged and undo / redo work as they did. No second state model was added.
* **"Unsaved" is computed**, never remembered: it is whether the tab's document differs from the saved one. An undo
  after a save therefore shows the draft as unsaved again; nothing pretends the save was reversed.
* **Save states**: Unsaved changes · Saving · Draft saved (revision, who, when) · Save failed · Not saved — someone
  else saved first (with what differs, and two explicit choices; nothing is merged) · Read only. Dependency changed
  is shown on the dependency panel and on the evaluation.
* **Dependencies** panel in the designer and on the readiness page: every dependency at its exact version with its
  fingerprint, its state, which requirements use it, and the deliberate actions. Per-requirement flags on the
  cards, in the matrix and in the inspector.
* **Gallery** on saved policies: blank, pattern, copy; search; market filter; saved state; history; archive with a
  reason; compare.
* **A name before a code** (ruling X3-6), for policies and for profiles: the name, a suggested code that can be
  changed, uniqueness in the market, and the statement that the code is permanent.
* **No simulated publication of a saved policy.** The persona switch is not shown; the signed-in person is. The
  "Approve and publish" page becomes a readiness page that submits nothing.

## 8. Migration `0039_applicability_policy`

One additive revision after `0038`: three tables, five indexes besides the keys, three functions and triggers.
**No existing table, column, row, trigger or permission is altered**, and no permission is added.

Tested on a populated test schema (seed data, accounts, a published survey, a published library):

| | Result |
|---|---|
| upgrade | the listed objects, nothing else |
| downgrade while empty | removes exactly those; every other table byte-identical |
| forced partial failure at the last statement | everything rolled back; revision stays `0038` |
| upgrade again | identical objects; every other table byte-identical |
| downgrade with a saved policy | **refused** ("applicability policies exist"); nothing lost |
| published library versions and Survey Studio versions | digests identical through all of it |
| start-up | with policies off, a schema at `0038` is accepted; with them on, readiness fails closed below `0039` |

### 8.1 Applying it to development — NOT done, NOT authorised

Same procedure as `0038` (`62_…` §2–4): preflight, verified backup, `alembic upgrade 0039_applicability_policy`,
comparison of every table with the preflight; then `APPLICABILITY_POLICIES_ENABLED=true` and the frontend setting.
No identity or permission change is needed: the three development identities already hold what policy authoring
needs (the author: `applicability.read`, `applicability.edit`, `survey.read`).

## Addendum 2026-11-24 — after acceptance and development enablement (D-419…D-426)

- **Applied to development** (`66_…`): schema at `0039`, saved policies on.
- **Owner rulings (D-420):** `PIN_DIFFERS` remains a draft diagnostic here and becomes a publication blocker in
  APPL-X4; `DEPENDENCY_STALE` fail-closed behaviour is the accepted contract and does not make draft assets
  reproducible; prototype operations stay feature-gated until their callers migrate.
- **Client contract additions, no API change:**
  - the gallery lists once and reads each policy once with `?inspection=false`; opening or saving one policy reads
    no other policy (asserted by test);
  - nothing can be created until the saved policies are loaded; `CODE_TAKEN` is stated to the person and the list
    is re-read;
  - archived policies are listed with `?archived=true` and restored through the existing `POST /{id}/restore`
    after a confirmation, with edit permission;
  - on a focus the designer's canvas is brought wholly inside the browser window; zoom is unchanged.
- OpenAPI unchanged by these additions.

