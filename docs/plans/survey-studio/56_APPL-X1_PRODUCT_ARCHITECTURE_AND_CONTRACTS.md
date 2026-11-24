# APPL-X1 — Survey Applicability Studio: product architecture and contracts

**Status: PROPOSED DESIGN, prepared 2026-11-23 for the product owner's design acceptance. Not accepted.**
APPL-X1 delivers the architecture, the evaluation contract and a working prototype. It adds **no table and no
migration**, stores nothing, and changes no existing survey, rule, binding, group, plan or operational record.
Synthetic content only: ILP, NFTF, replacement, riders and every survey named here are illustrations, not approved
business meaning, sources or compliance requirements.

Authorisation: the owner's message of 2026-11-23, "Master program: Survey Applicability Studio … Begin with APPL-X1
and stop for product-owner review". Companions: `57_…` (experience specification and evidence), `58_…`
(implementation plan APPL-X2…X6), `55_…` (application facts).

---

## 1. Product vision

Survey Applicability Studio answers one question for the business: **which surveys does this application need, and
why?** The author writes sentences of one shape —

> WHEN these conditions apply, THEN these surveys are required

— tests them against saved example applications, and publishes the whole set as one governed policy.

It is a new, survey-centred product. It does **not** sit on assignment rules, survey bindings or requirement groups,
and none of those words appears in it. What the old design spread over three governed objects and a precedence
contest, the new one states in a single document:

| Old (kept for history, not the foundation) | New |
|---|---|
| a rule with a priority; the highest-ranked rule wins | every requirement whose condition holds contributes; nothing "wins" |
| a binding gives a rule a survey; a group gives it a purpose | a requirement names its surveys directly |
| several surveys need several groups | one requirement can name several surveys |
| combination effects emerge from priority and specificity | combination effects are written down: *replaces*, *choose one* |
| three objects, three approvals | one policy, one review, one publication |

Two dimensions are kept apart everywhere — in the document, the evaluator and the screens:

* **Condition logic** — when something applies: AND, OR, NOT, groups, typed comparisons.
* **Selection behaviour** — what then happens: include, include several, replace, choose one, order.

## 2. Information architecture

Survey Applicability is a first-class workspace inside Survey Studio, at `/survey-studio/applicability`.

```text
Survey Studio
  Home · Surveys · Building blocks · Survey applicability · Test & evaluation
                                      │
        ┌──────────┬──────────┬───────┴──────┬───────────┬──────────────┬─────────────┐
     Overview   Variables   Profiles   Conditions     Policies      Scenarios     Governance
   (dashboard)  (library)  (composer)    (lab)       (designer:     (studio,     (review, publish,
                                                   cards·canvas·     matrix,       impact, history)
                                                      matrix)        impact)
```

One mental model runs along the top of every screen as a stepper that is also the navigation:
**Define facts → Build conditions → Connect surveys → Test scenarios → Approve & publish.**

The seven areas share one workspace state, one selection and one inspector, so context survives a move between them.
A missing variable or condition is created in a drawer over the current screen and the author returns to the exact
place they left (§8 of `57_…`).

*Navigation note.* The five-item Survey Studio navigation the owner proposed renames and regroups entries accepted
under NAV-1. In APPL-X1 only **Survey applicability** is added (behind a build setting); the full regrouping is
proposed for APPL-X5 so the accepted navigation is not changed by a prototype.

## 3. Canonical domain

Five kinds of thing. Each is a small JSON document with a stable code and a version; a published version never
changes.

```text
Variable ──used by──► Profile ──scopes──► Scenario
    │                    │
    └──tested by──► Condition ──referenced by──► Policy ──evaluated for──► Scenario ──► Selection plan
                                                   │
                                                   └── names ──► published survey versions
```

### 3.1 Variable

```json
{ "code": "product_family", "name": "Product family", "description": "…", "category": "Product",
  "type": "ENUM", "values": [{"value": "ILP", "label": "Investment-linked"}],
  "markets": ["SG"],
  "source": {"status": "MAPPED | PROPOSED | UNMAPPED", "system": "…", "field": "…", "note": "…"},
  "owner": "…", "samples": ["ILP"], "derived": null, "version": 1, "status": "PUBLISHED" }
```

| Type | Value | Operators |
|---|---|---|
| `BOOLEAN` | true / false | is yes, is no |
| `ENUM` | one of `values` | is, is not, is one of, is none of |
| `MULTI_ENUM` | a set of `values` | includes any of, includes all of, includes none of |
| `NUMBER`, `DECIMAL` | a number, optional `min` / `max` | =, ≠, >, ≥, <, ≤, between |
| `MONEY` | an amount in one declared `currency` | as numbers; never compared across currencies |
| `DATE` | ISO date | on, before, after, between |
| `STRING` | text | is, is not, is one of — nothing looser |
| every type | — | is known, is not known |

A **derived** variable is a boolean whose value is a condition expression over other variables
(`"derived": {"expr": …}`). That is the whole expression language for derivation in contract 0: no arithmetic, no
code. Dependencies are checked for cycles. A variable's `source.status` says honestly whether anything real feeds
it; **no source mapping is invented** — of the seeded variables only those that exist in today's fact snapshot are
marked MAPPED (`55_…` §2–3).

### 3.2 Application profile

```json
{ "code": "ilp_extension", "name": "ILP extension", "extends": ["common"],
  "sections": [{"name": "Investment-linked", "variables": ["is_ilp", "fund_risk_class"]}],
  "required": ["product_family"], "version": 1, "status": "PUBLISHED" }
```

Profiles compose: a profile is its own sections plus everything it `extends`, and an application may use several at
once (Common + ILP + NFTF + Replacement). A profile **references** variables; it never copies their definitions. If
two composed profiles disagree about a variable (one marks it required, the other excludes it) the conflict is
reported, never resolved silently.

### 3.3 Condition

```json
{ "code": "ilp_and_nftf", "name": "ILP with NFTF", "description": "…", "expr": { … }, "version": 1,
  "status": "PUBLISHED" }
```

The expression is a restricted, typed tree — the only "code" a user ever writes:

| Node | Shape |
|---|---|
| all of (AND) | `{"op": "all", "args": [expr, …]}` |
| any of (OR) | `{"op": "any", "args": [expr, …]}` |
| not | `{"op": "not", "arg": expr}` |
| a test | `{"op": "test", "variable": code, "operator": name, "value" \| "values" \| "min"+"max": …}` |
| a saved condition | `{"op": "ref", "condition": code, "version": n}` |

### 3.4 Applicability policy

One document holds the entire configuration that is reviewed and published together.

```json
{ "code": "SG-NEW-BUSINESS", "name": "…", "market": "SG", "description": "…",
  "profiles": ["common", "ilp_extension", "nftf_extension"],
  "scope": null,
  "same_survey": "ONE_DELIVERY | CONFLICT",
  "requirements": [
    { "id": "r1", "name": "ILP needs the ILP survey",
      "when": { expr } ,
      "action": { "kind": "INCLUDE", "surveys": [survey_ref, …] },
      "replaces": [] },
    { "id": "r4", "name": "…", "when": { expr },
      "action": { "kind": "CHOOSE_ONE", "alternatives": [{"survey": survey_ref, "when": expr | null}] },
      "replaces": ["r1", "r2"] } ],
  "order": ["S-A", "S-B", "S-C"],
  "version": 2, "status": "DRAFT" }
```

`survey_ref` = `{code, version, name, fingerprint}` — an exact published survey version. `when: null` means
"always". `scope: null` means the policy covers every application of its market and profiles.

### 3.5 Scenario and selection plan

A **scenario** is a saved synthetic application: `{id, name, description, profiles, facts, suite, golden}` where
`facts` maps variable codes to values. A **selection plan** is what the evaluator returns for one scenario and one
policy (§5). The four are never merged: a policy is what the business configured, a profile says which facts are
relevant, a scenario is one example application, a plan is the result.

### 3.6 What is pinned by a published policy

A published policy revision is self-contained. Its manifest embeds, by exact version and fingerprint: every variable
definition it reads, every profile it names, every saved condition it references (**frozen as the expression it had
at that version**), each survey version with its content fingerprint, the order, the `same_survey` mode and the
evaluator contract. A later version of a variable, condition or survey changes nothing that is already published.

## 4. Three-valued logic

Every expression evaluates to exactly one of **TRUE**, **FALSE**, **UNKNOWN**. Unknown never becomes false.

| AND | TRUE | FALSE | UNKNOWN |   | OR | TRUE | FALSE | UNKNOWN |   | NOT | |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **TRUE** | TRUE | FALSE | UNKNOWN | | **TRUE** | TRUE | TRUE | TRUE | | TRUE | FALSE |
| **FALSE** | FALSE | FALSE | FALSE | | **FALSE** | TRUE | FALSE | UNKNOWN | | FALSE | TRUE |
| **UNKNOWN** | UNKNOWN | FALSE | UNKNOWN | | **UNKNOWN** | TRUE | UNKNOWN | UNKNOWN | | UNKNOWN | UNKNOWN |

`all` of nothing is TRUE; `any` of nothing is FALSE. Evaluation never short-circuits the **trace**: every branch is
evaluated and recorded, so the explanation can point at the branch responsible.

**Why a test is UNKNOWN** is always recorded, and the four reasons are kept distinct:

| Fact state | Meaning | A test on it |
|---|---|---|
| `KNOWN` | a valid value | TRUE or FALSE |
| `UNKNOWN` | the application says the value is not known | UNKNOWN |
| `NOT_PROVIDED` | the scenario gives no value | UNKNOWN |
| `INVALID` | a value that breaks the variable's type or allowed values | UNKNOWN, with a diagnostic naming the value |
| `UNSUPPORTED` | the variable is not in the scenario's profiles | UNKNOWN, with a diagnostic |

`is known` / `is not known` are the only tests that turn the first three into TRUE or FALSE. An **evaluation error**
(a malformed document) is none of these: it stops the evaluation with status `ERROR` and no plan.

## 5. Selection semantics

### 5.1 Requirement state

Each requirement's condition gives its **state**: `APPLIES` (TRUE), `DOES_NOT_APPLY` (FALSE), `UNRESOLVED`
(UNKNOWN).

### 5.2 Additive by default

Every requirement that applies contributes its surveys. There is no priority and no single winner.

### 5.3 Replacement — explicit, named, and only when the replacer applies

`"replaces": ["r1", "r2"]` on requirement C means: *when C applies, r1 and r2 do not contribute*. Only the named
requirements are affected. A requirement's **outcome**:

| Outcome | When |
|---|---|
| `ACTIVE` | it applies and no active requirement replaces it |
| `REPLACED` | it applies and an active requirement replaces it |
| `PENDING` | it applies, and a requirement that would replace it is unresolved — it may or may not be replaced |
| `UNRESOLVED` | its own condition is unknown |
| `INACTIVE` | it does not apply |

Chains are resolved from the top: a requirement that is itself replaced replaces nothing (if C replaces A and A
replaces B, and all apply, then C and B are active and A is replaced). A replacement cycle, a self-replacement and a
replacement of an unknown requirement are **configuration errors** found by validation; a chain is reported as a
warning so the author sees the consequence.

### 5.4 Choose one

A `CHOOSE_ONE` action lists alternatives, each with its own criterion (`when`, or none for "otherwise"). With the
requirement active:

| Eligible alternatives | Result |
|---|---|
| exactly one TRUE, the rest FALSE | that survey |
| none TRUE, an "otherwise" alternative exists | the "otherwise" survey |
| none TRUE, no "otherwise" | `NO_ALTERNATIVE` — unresolved |
| more than one TRUE | `AMBIGUOUS` — unresolved. **List order never decides** |
| any criterion UNKNOWN while the choice is not already forced | unresolved |

### 5.5 The same survey required more than once

A policy must say what it means, in `same_survey`; there is no default:

| Mode | Meaning |
|---|---|
| `ONE_DELIVERY` | the survey appears once in the plan and **every** requirement that asked for it is recorded as an obligation it satisfies. Nothing is silently dropped: the plan shows all of them |
| `CONFLICT` | the plan is unresolved, naming the requirements, until the author removes the overlap |

Two requirements naming **different versions** of one survey is always a configuration error.

### 5.6 Order

`order` is the governed delivery order of the policy's surveys. It is not a priority and has no effect on which
surveys are selected. The plan lists the selected surveys in that order. A survey a requirement names but the order
omits is a blocking validation error.

### 5.7 Scope and several policies

A policy applies to an application when its `scope` is TRUE. For one application and a set of published policies:
exactly one in scope → that policy; none → `NO_POLICY`; more than one → `MULTIPLE_POLICIES`, unresolved. No policy
is ever chosen silently; composing policies is left for an explicit contract (open decision AP-7).

### 5.8 Plan status

| Status | Meaning |
|---|---|
| `RESOLVED` | every requirement is decided; the ordered list is final (it may be empty: "no survey required") |
| `UNRESOLVED` | something is unknown, pending, ambiguous or in conflict. The plan still separates what is **definitely selected** from what is **pending**, and says exactly which facts would settle it |
| `OUT_OF_SCOPE`, `SCOPE_UNRESOLVED` | the policy's scope is false / unknown |
| `ERROR` | the document could not be evaluated |

A plan is a **synthetic selection result**. It grants nothing: no eligibility, no assignment, no call.

## 6. The evaluator

`Call360-backend/app/domain/survey/applicability/` — pure Python, no database, no clock, no randomness, no model.

```text
typed facts + policy document (+ the variables, profiles and conditions it uses)
      └────────► evaluate ────────► selection plan + trace + diagnostics + fingerprints
```

* One implementation. The authoring preview, the Condition Lab, Scenario Studio, the matrix, impact comparison and
  — later — integrated selection all call it. **The browser computes no applicability**; it draws what the evaluator
  returns. (The browser does compose plain-English sentences for an expression; that is wording, not evaluation.)
* It is narrow on purpose: typed facts in, survey selection out. It is not a general rules platform.
* Contract identifier `call360.survey-applicability/0` — a prototype contract until APPL-X1 is accepted.

**Output** for one scenario: policy identity, version and fingerprint; fact states with reasons and a facts
fingerprint; plan status; every requirement with state, outcome, the full condition trace, what replaced it and its
surveys; `selected` (ordered, each with the requirements that required it), `pending`, `excluded` (with the reason:
not applicable, replaced, alternative not chosen); diagnostics; a sentence-by-sentence explanation; and an output
fingerprint. The same input always gives the same bytes.

**Static analysis** (no scenario needed) reports, as blockers or warnings: unknown variables, conditions and
requirements; operator or value not valid for the type; cycles among conditions, derived variables and replacements;
a survey missing from the order; different versions of one survey; an empty requirement; and — where the variables
involved are few enough to enumerate exhaustively — a condition that can never be true, one that is always true, a
requirement that can never apply, alternatives that can be eligible together, and requirements that are exact
duplicates. Where enumeration would be too large the analysis says "not checked", never "fine".

**Scenario generation** enumerates the variables a policy actually reads (each boolean and enum value plus unknown;
each numeric threshold at, below and above) and returns one scenario per distinct **result signature**, with a
statement of what was covered and what was not.

## 7. Application facts (aligned with `55_…`)

The evaluator's input is the typed fact interface proposed for APP-1:

```json
{ "variable": "product_family", "state": "KNOWN", "value": "ILP", "type": "ENUM",
  "source": {"record": "policy_fact_snapshot:…", "field": "facts.product_family", "mapping_version": 1},
  "as_of": "…", "lineage": "…" }
```

with one hash over the whole snapshot. In APPL-X1 facts come only from scenarios (source `SCENARIO`). The same shape
is what Survey execution, control applicability and journey evaluation would read. Today's nine operational rule
inputs can be **projected** into it for compatibility; they do not define the variable library. Replacement, rider
and NFTF have no source today and none is invented: their variables are marked `UNMAPPED`.

## 8. Governance (proposed for APPL-X4)

| Artifact | Lifecycle | People |
|---|---|---|
| Applicability policy | draft → validated → submitted (immutable candidate with manifest and fingerprint) → approved or returned → published → superseded | **three**: maker, checker, publisher, all different |
| Variable, profile, condition | draft → published version; a change makes a **new version** | proposed: maker and a different checker (AP-3) |

* A policy pins exact versions (§3.6), so publishing a new version of a variable or condition changes no published
  policy. Policies that pin the older version are listed as *can adopt* — an explicit, reviewed act.
* A candidate cannot be submitted with a blocking diagnostic. Its review shows the manifest, the full comparison
  with the published version and the result change for every saved scenario.
* Permissions proposed: `applicability.read / edit / approve / publish` (and `…library.edit / approve` if AP-3 is
  accepted) — separate from `survey.*`, `assignment_rule.*` and `script.*`. Authoring implies neither approval nor
  publication. Market isolation as everywhere else.
* In the APPL-X1 prototype the lifecycle is **simulated** in the browser and is labelled so; nothing is recorded.

## 9. Proposed persistence (APPL-X2…X4 — not built)

Documents are versioned JSON, as surveys already are. That keeps the number of tables small and makes a published
revision reproducible from its own row.

| Table | Holds |
|---|---|
| `applicability_asset` + `applicability_asset_version` | variables, profiles and conditions: kind, code, market; version, document, sha256, state, maker, checker. Insert-only versions |
| `applicability_policy`, `applicability_policy_draft` | identity and market; the working document with optimistic concurrency |
| `applicability_policy_candidate` | the immutable submitted document, manifest, fingerprints, makers |
| `applicability_policy_version` | the published candidate and its version number |
| `applicability_event` | lifecycle and decision history for all of the above |
| `applicability_scenario` | saved scenarios and suites, with facts and the golden flag |
| `applicability_evaluation` | recorded selection plans: `record_class = 'SIMULATION'`, policy version, facts hash, output hash |

Eight tables. Requirements and actions are **not** tables: they live inside the policy document, which is what is
reviewed. Nothing references `script_assignment_rule_version`, `survey_assignment_binding` or
`survey_assignment_group`.

## 10. Coexistence and retirement

* The new domain reads **published survey versions** and nothing else from the existing schema. It writes nothing
  into rules, bindings, groups, composite plans or any operational table, directly or through a compatibility layer.
* Legacy survey assignment (rules + bindings + groups) keeps working and keeps its history. During coexistence a
  synthetic journey is selected by **one** source, stated on the record: `LEGACY_ASSIGNMENT` or `APPLICABILITY`.
* Downstream consumers (coordinated simulation, evaluation, findings, assurance, Application Journeys) are adapted
  in APPL-X5 through a versioned **selection-plan interface**, not by translating a plan into bindings and groups.
* Retirement of legacy survey-assignment authoring is APPL-X6, a separate checkpoint with its own acceptance.
  Historical tables are kept and readable. **Script Studio's operational assignment is a different thing and is not
  touched by this programme.**

## 11. API (APPL-X1: four stateless operations, behind a setting)

Registered only when `survey_applicability_prototype_enabled` is on; they need `survey.read`, read nothing but the
request, and write nothing.

| Operation | Purpose |
|---|---|
| `POST /api/v1/survey-applicability/prototype/evaluate` | one policy (and optionally a second, for comparison) against a list of scenarios |
| `POST …/prototype/condition-test` | one expression against one set of facts, with the trace |
| `POST …/prototype/analyse` | static diagnostics for a workspace and a policy |
| `POST …/prototype/scenarios` | generated scenarios and a coverage statement |

From APPL-X2 the same evaluator is called by persisted operations and these prototype operations are removed.

## 12. Security, accessibility, scale

* **Security** — no user-supplied code is ever executed: the expression tree is validated node by node against a
  closed set of operators. Requests are size-bounded (variables, nodes, scenarios, enumeration). Standard
  authentication, CSRF and rate limiting apply. No operational data is read.
* **Accessibility** — every drag has a keyboard equivalent; the canvas has a list alternative; state is never
  carried by colour alone; focus is managed in drawers and the command palette; targets are WCAG 2.2 AA. A
  screen-reader test is not claimed.
* **Scale** — libraries are searched and filtered, never shown as one long dropdown; the canvas opens focused on one
  requirement, condition or survey when the policy is large; the matrix is generated by result signature, not by raw
  combination.

## 13. Decisions this design needs from the owner

| | Decision | Proposed |
|---|---|---|
| AP-1 | Replacement chains: does a replaced requirement still replace others? | No (§5.3) |
| AP-2 | The same survey required more than once | the policy must choose `ONE_DELIVERY` or `CONFLICT`; no default (§5.5) |
| AP-3 | Governance of variables, profiles and conditions | two people; policies three |
| AP-4 | Derived variables | boolean, defined by a condition expression only, in contract 0 |
| AP-5 | Money across currencies | never compared; a different currency is INVALID |
| AP-6 | An unresolved plan still lists what is definitely selected | yes, clearly separated from pending |
| AP-7 | Several policies in scope for one application | unresolved; no composition contract yet |
| AP-8 | "Choose one" with no eligible alternative and no "otherwise" | unresolved |
| AP-9 | Survey Studio's five-item navigation | add the one entry now; regroup in APPL-X5 |
| AP-10 | Permissions separate from `survey.*` | yes |

None of these is a compliance policy. What a business condition *means* (what NFTF is, when a replacement survey is
required) is not decided anywhere in this design.

## 14. Amendment of 2026-11-23 (APPL-X1R): owner rulings and the published-survey reference

APPL-X1 is accepted as a technically verified prototype and architectural direction. The owner ruled AP-1…AP-10
(D-387); where this section differs from §3–§5 and §13 above, **this section governs**.

### 14.1 Replacement (AP-1) — replaces §5.3's chain rule

A requirement's `replaces` names its **final** targets. A chain — a replaced requirement that itself replaces
something — is not allowed: validation reports `REPLACEMENT_CHAIN` as a blocker on the requirement, and the
evaluator refuses to evaluate such a policy. Cycles, self-replacement and unknown targets are blockers as before.
Nothing transitive is ever applied.

### 14.2 The same survey required more than once (AP-2) — replaces §3.4's `same_survey` and §5.5

`same_survey` is removed. A policy may carry explicit statements instead:

```json
"shared_deliveries": [ { "survey": "S-…", "requirements": ["r1", "r2"], "note": "…" } ]
```

meaning *one delivery of this survey satisfies exactly these requirements*. When several active requirements select
one survey: if a statement covers **all** of them, the survey appears once with every requirement recorded
(`SURVEY_SHARED_DELIVERY`); otherwise the plan is unresolved (`DUPLICATE_SURVEY`), naming those requirements. A
statement never extends to a requirement it does not name. Validation finds reachable collisions by enumeration and
blocks them. Different versions of one survey are always an error.

### 14.3 Governance (AP-3) — replaces the second row of §8

Published **variable, profile, condition and policy** versions all need three different identities: maker, checker,
publisher. Drafting and synthetic scenario testing need none. Until persistence is authorised this lifecycle is a
labelled simulation; only Survey Studio's publication is server-enforced.

### 14.4 Choose one (AP-8) — replaces the "otherwise" of §5.4

An alternative is `{survey, when, fallback?}`. It needs a criterion or `fallback: true`; one with neither is
incomplete (`MISSING_CRITERION`, blocker) and is never chosen. At most one fallback. No fallback and nothing eligible
is unresolved.

### 14.5 Profiles and scope

Profiles organise the variables that describe an application. They **never** decide whether a policy applies, and a
policy's profiles do not enter evaluation. A policy applies exactly when its explicit `scope` is true. A fact given
from outside an application's own profiles is read and marked `outside_profiles`; where a profile narrows a value, a
value outside it is invalid.

### 14.6 Confirmed as proposed

AP-4 (boolean derived variables only), AP-5 (no currency conversion), AP-6 (definite and pending shown separately;
an unresolved plan is not execution-ready), AP-7 (several policies in scope stay unresolved), AP-9 (navigation
unchanged until APPL-X5), AP-10 (independent permissions, market isolation, role separation; nothing widened).

### 14.7 The published-survey reference

```json
{ "code": "S-APPL-DEMO-ILP", "version": 1, "label": "1.0", "name": "…",
  "version_id": "<survey_version.id>", "definition_id": "<survey_definition.id>",
  "fingerprint": "<content_sha256>", "manifest": "<manifest_sha256>", "market": "SG" }
```

Read-only integration, established in APPL-X1R and to be reused unchanged by APPL-X3:

| Need | Existing operation |
|---|---|
| surveys with a published version | `GET /survey-definitions` (`latest_version_id`) |
| the version's identity and fingerprints | `GET /survey-versions/{id}` (must be `PUBLISHED`) |
| its modules, questions, wording, options, routes | `GET /survey-candidates/{candidate_id}/documents` |
| who submitted, approved, published | the `history` of the candidate and the version |

A reference is never moved to a newer version implicitly; adopting one is an explicit edit. A reference Survey
Studio does not list is `SURVEY_NOT_PINNED` — a blocker — and nothing is substituted. A published policy's manifest
pins: variable, profile and condition versions; the policy definition; the evaluator contract; each survey version
with content and manifest fingerprints; the delivery order; the shared deliveries.

