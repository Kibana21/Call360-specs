# 77 — APPL-X5a design decision: application facts and survey facts

Date 2026-11-24. Written before implementation, as the owner's ruling Q-4 requires.
**It needs no change to any accepted table.** One new table; everything else lives in the journey's own records.
Synthetic execution only. A correspondence here is **not** an approved operational data mapping.

---

## 1. The two vocabularies, as they exist

| | Application facts | Survey facts |
|---|---|---|
| What they are | values of **applicability variables** from the governed library | values of **fields** of Survey Studio's governed catalog |
| Identity | variable code + published version (version id, content fingerprint) | field code + its catalog attributes (the catalog is not versioned) |
| Examples in the synthetic data | `product_family` (ENUM), `replacement` (BOOLEAN), `annual_premium` (MONEY, SGD), `customer_age`, `sales_channel` | `policy.product_family` (ENUM), `policy.is_replacement` (BOOLEAN), `policy.annual_premium` (MONEY, SGD), `customer.age_years`, `sale.channel` |
| Read by | the applicability evaluator, to select surveys | the survey execution engine, for module eligibility, routing and wording |
| Checked by | the frozen variable definitions of the published policy version | `check_facts` against the catalog |

The names differ, and where they look alike that proves nothing. They stay two separately labelled sets everywhere:
in the API, in the records and on the screen.

## 2. The correspondence — a small declarative document

A **fact correspondence** is a named, numbered, immutable document: a list of entries, each saying "this application
fact, at this exact definition, is the same fact as this survey field, at this exact definition".

```text
{ name, description,
  entries: [ { source: { variable, version, version_id, content_sha256 },
               target: { field, attributes_sha256 },
               rule: "IDENTITY" } ] }
```

- **Only one rule exists: `IDENTITY`** — the value is carried over unchanged. There is no expression, no formula, no
  lookup table, no code, and no place to put one.
- **Identities are explicit and exact.** The source is one published variable version, pinned by id and content
  fingerprint. The target is one catalog field, pinned by the fingerprint of its attributes. Nothing is matched by
  name; an entry is typed in by a person, field by field.
- **Compatibility is validated when the correspondence is saved**, and it is refused otherwise:

  | Source type | Target type | Also required |
  |---|---|---|
  | BOOLEAN | BOOLEAN | — |
  | ENUM | ENUM | every source value is, literally, a target value |
  | INTEGER | INTEGER | — |
  | MONEY | MONEY | the same currency / unit |
  | TEXT | TEXT | — |
  | anything else, or a derived variable | — | refused |

- One target field may have at most one entry; one source may feed several targets.

## 3. Applying it to a journey

The person **chooses** a correspondence version when starting a journey, or chooses none. Nothing is applied by
default. For each entry:

| Situation | Result |
|---|---|
| the policy version pins exactly that variable version, and the field's attributes are exactly those pinned | **applies** |
| the policy version pins another version of the variable, or does not use it | does not apply — `SOURCE_DEFINITION_DIFFERS` / `SOURCE_NOT_IN_POLICY` |
| the catalog field has changed since the correspondence was written | does not apply — `TARGET_DEFINITION_DIFFERS` |

For an entry that applies:

| Application fact | Survey fact |
|---|---|
| a value | the same value, unchanged |
| not known (`null`) | not known (`null`) — never false, never a default |
| not provided (absent) | not provided (absent) |
| a value that is invalid under the variable's definition | not carried; reported |

**A known value is never replaced by an unverified one.** The person may also type survey facts directly in the
separately labelled Survey Facts editor:

- typed value equal to the carried value → accepted;
- typed value **different** from a carried known value → the start is refused (`SURVEY_FACT_CONFLICT`); the person
  must resolve it;
- typed known value where the application fact is not known → the typed value stands, recorded as typed.

**Required survey facts.** Every catalog field that a selected survey actually reads (eligibility, routing or
wording) must be addressed before the journey starts: carried by an applied entry, or typed, or explicitly marked
"not known". A field left unaddressed refuses the start (`SURVEY_FACTS_REQUIRED`) and names the field and the survey
that reads it. What the engine then does with a not-known fact is the survey's own governed unknown policy — the
coordinator adds nothing.

## 4. What is frozen in the journey

The journey's start record stores, and fingerprints:

- the correspondence document used (the whole document, with its id, number and fingerprint), or "none";
- per entry: applied or not, and why not;
- per survey field: the value, where it came from (`CORRESPONDENCE` with the entry, `TYPED`, `MARKED_NOT_KNOWN`), and
  the source value;
- the resulting survey fact snapshot and its fingerprint — the exact snapshot given to every survey simulation of
  the journey.

Verification re-applies the frozen document to the frozen application facts and must reproduce the same snapshot.

## 5. Storage

One new table, in migration `0042` (test schema only):

`applicability_fact_correspondence` — `id`, `market_code`, `code`, `version_no`, `document`, `document_sha256`,
`record_class` (always `SYNTHETIC`), `created_by`, `created_at`; unique (market, code, number); insert only — a
change is a new numbered version; never updated, never deleted.

- **Separate from the policy.** A correspondence is not a dependency of an Applicability Policy and is not in any
  publication manifest. Publishing, superseding or verifying a policy never reads it. It cannot change what a
  published policy means: selection is computed before, and without, any correspondence.
- **Not governed by three-person publication in X5a.** It is a synthetic execution aid, created by a person holding
  `applicability.edit`, labelled synthetic and unapproved on every screen. Whether an operational mapping needs its
  own governance is a question for APP-1a, not decided here.
- **No accepted table is altered.** Survey facts are passed to the existing simulation service exactly as it already
  accepts them.

## 6. Not in scope

Any mapping from a policy, sale, customer or case to either vocabulary (APP-1a); conversions, units arithmetic,
date handling, derived targets; applying a correspondence automatically.
