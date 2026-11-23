# SHARED-1 — Assignment Rules and Finding Rules on their own: assessment, design and data-preservation plan

**Status: written 2026-11-23, BEFORE any schema edit, for the authorised checkpoint SHARED-1 (D-360).** Starting point:
`51_MIG-1_…` §3. Companion: `53_SHARED-1_IMPLEMENTATION_REPORT.md`, contract `04_…` §23, decisions D-356…D-369.
**Synthetic data only.** Not started and not touched: MIG-2, operational case assignment, Script Studio, voice.

---

## 1. Owner rulings this rests on

| | Ruling | Effect here |
|---|---|---|
| B-1 (D-357) | the migration-and-preservation strategy supersedes the conflicting parts of D-154 and D-156; historical script content, foreign keys and readers are preserved; no legacy record is migrated or modified today | SHARED-1 changes **no** existing rule, script, assignment or finding record. The one data change is a back-fill of a new column on existing rule versions |
| B-2 (D-358) | Assignment Rules and Finding Rules are independently governed shared capabilities; they "must not depend on Script Studio authoring permissions, publication or script identity for newly supported survey-only use cases"; "Preserve the existing authoritative engines" | a rule gets a market of its own and may have no script target; both capabilities get permissions of their own; `rule_engine`, `answer_evaluation`, `finding_engine` are not changed |
| D-359 | M-1…M-5 and B-3…B-7 stay open | nothing here sets a re-prompt limit, a delivery rule, a failure behaviour, an unknown policy, a conversion scope, a retention period or an approval equivalence |

## 2. What the code does today (inspected)

### 2.1 Assignment rules

| Fact | Where |
|---|---|
| A published rule version has **no market column**. Its market is its target script's family's | `script_assignment_rule_version` (`0005`); `rule_inputs.published_candidates` l.292; `rule_authoring._version_row` l.159; `api/assignment_rules.py` l.164; `survey/assignment.py` l.115, l.416 |
| A **draft already has a market of its own** (`assignment_rule_draft.market_code`), chosen at creation from the author's markets and checked against the "market" condition | `0017`; `rule_authoring.create_rule`, `analyse` (`MARKET_REQUIRED`, `MARKET_MISMATCH`) |
| A script target is mandatory: `target_script_version_id` NOT NULL on the version; on the draft a CHECK requires it once the draft leaves `DRAFT`; validation raises `NO_TARGET`, `TARGET_NOT_FOUND`, `TARGET_MARKET`, `TARGET_NOT_PUBLISHED`, `TARGET_NOT_YET_EFFECTIVE` | `0005` l.214, `0017` `ck_assignment_rule_draft_frozen`, `rule_authoring.analyse` l.421-460 |
| A published version is immutable except retirement (status and `effective_to`) | trigger `assignment_rule_version_guard` (`0017`) |
| Governance is **two-person**: author ≠ reviewer (CHECK); a maker may neither review nor publish; the reviewer may publish. Permissions `script.edit`, `script.approve`, `script.publish`; reads `script.read` | `rule_authoring.py` docstring; `api/assignment_rules.py` |
| The same loader feeds two consumers: the **operational script assignment engine** (`script_assignment.py` l.152) and **survey selection** (`survey/assignment.py` l.333, l.423), which re-targets each rule to its published survey binding and ignores the script target | as cited |
| The database already refuses a script assignment whose matched rule does not target the assigned version | trigger `script_assignment_check` (`0005`): `r.target_script_version_id = NEW.script_version_id` |
| Conflict analysis compares targets: two rules that can both match, at equal precedence, with different targets, are an error | `rule_engine.conflicts` l.503-520 |
| Simulation of rules runs over synthetic **cases** and reports the script selected | `rule_authoring.simulate` |

### 2.2 Survey bindings and groups

A binding names an exact published rule version and an exact published survey version; it carries its own
`market_code`, taken from the rule; `MARKET_MISMATCH` is raised when the survey's market differs
(`survey/assignment.py:propose`). Requirement-group members are rule versions; composite-plan members record the rule
version that selected each survey. All four carry a foreign key to `script_assignment_rule_version`. None refers to a
script. Composite plans and assignment evaluations are insert-only records holding their own snapshot of rule
references and fingerprints.

### 2.3 Operational assignment, holds, voice

Unchanged by design, and inspected to confirm it need not change: `intake.py:502` (hold), `script_assignment.py`
(preview, apply, batch; loads candidates with `ri.published_candidates`), `voice/store.pins_for` (a `PUBLISHED`
script version assignment), `api/script_assignments.py`, `api/scripts.py` l.289 (the script-side list of rules, an
inner join to the target script).

### 2.4 Finding rules

`finding_rule_set_version`: one published and one open version per market; statuses DRAFT → SUBMITTED_FOR_REVIEW →
APPROVED → PUBLISHED → SUPERSEDED / ABANDONED; `rules` JSON with a SHA-256. Reads need `script.read`; create, save,
submit, abandon `script.edit`; review `script.approve`; publish `script.publish` (`api/finding_rules.py`). It has its
own market column and **no reference to a script table**. A rule of scope `QUESTION` names a script `question_code`
as its target — a value, not a foreign key. Survey evaluation reads the published set (`journey_evaluation.py`) and
runs `finding_engine` unchanged.

### 2.5 Permissions and navigation

Permissions are rows of `permission` (`code`, description), granted to roles through `role_permission`; a route asks
for exactly one with `require("code")`. Conventions: lower case, dot-separated (`script.read`,
`survey.assignment.read`). The new survey permissions were "created and granted to NO role" by their migrations.
Frontend: `RequirePermission` on each route in `App.tsx`; `nav.ts` lists Assignment Rules and Finding Rules under
Design & Govern for a holder of `script.read`.

## 3. Design

### 3.1 A rule's own market (AR-1)

`script_assignment_rule_version.market_code` — NOT NULL, validated against the governed market list by the existing
`assert_market_code` trigger, and immutable because the existing version guard already refuses any change except
retirement.

- **Source for a new rule:** the draft's `market_code`, which is itself taken from the author's authorised markets at
  creation and never from a survey or a free field. Publication copies it.
- **Source for an existing rule:** back-filled from its target script family — the authoritative source today — and
  verified row by row inside the migration (§4).
- **A script-backed rule and its target must agree:** a new database trigger refuses a rule version whose market is
  not its target script family's.
- **Readers** take the market from the rule. Nothing reads it through a script any more.

### 3.2 What a rule selects (AR-2) — an explicit scope, not a nullable column

`target_kind` on both the draft and the published version:

| `target_kind` | Meaning | Script target | Operational script assignment | Survey selection |
|---|---|---|---|---|
| `SCRIPT_VERSION` *(default; every existing rule)* | assigns a published script version to a case, and can also be bound to a survey | required | **eligible**, exactly as today | eligible through a published binding, exactly as today |
| `SURVEY_BINDING` | selects a survey only through a governed binding. It names no script | **must be absent** | **never** | eligible through a published binding |

Enforced at four levels, so that no consumer has to "handle NULL":

1. **Schema.** `CHECK ((target_kind = 'SCRIPT_VERSION') = (target_script_version_id IS NOT NULL))` on both tables.
   The kind of a draft never changes after creation (trigger); the kind of a version is immutable with the rest.
2. **Loader.** `rule_inputs.published_candidates(…, kinds=("SCRIPT_VERSION",))` — the default returns script-backed
   rules only. The operational engine, the script-side rule list, rule simulation over cases and the analysis of a
   script-backed draft therefore see **exactly the rules they saw before**. Only survey selection and the analysis of a
   survey-only draft ask for both kinds.
3. **Database guard on the operational record.** A new trigger on `script_assignment` refuses a matched rule that is
   not `SCRIPT_VERSION` ("a survey-only assignment rule can never assign a script to a case"), beside the existing
   check that already implies it.
4. **Validation.** A survey-only draft with a script target is an error (`TARGET_NOT_ALLOWED`); a script-backed draft
   without one keeps `NO_TARGET`. Creating a survey-only rule needs the setting and the migration.

### 3.3 Consumers of the script target — inventory and disposition

| Consumer | Today | After |
|---|---|---|
| `rule_inputs.published_candidates` | inner join to the script; market from the family | market from the rule; `kinds` filter, default script-backed; a survey-only candidate carries `target_id = "survey-binding:<code>"`, `target_effective = False` |
| `rule_inputs.draft_candidate` | target optional | same; survey-only as above |
| `rule_authoring._version_row`, `create_rule` (copy), `create_version` | inner join | left join; kind and market from the rule; a copy or new version keeps the kind |
| `rule_authoring.analyse` | target checks; conflicts against live rules | target checks only for script-backed; a survey-only draft is checked against **every** live rule of its market (what survey selection evaluates); a script-backed draft against script-backed rules only — **unchanged** |
| `rule_authoring.manifest`, `publish`, `snapshot_*`, `diff` | `str(target)` | target absent for survey-only; the manifest and checksum of a script-backed rule are **byte-for-byte what they were** (new keys are added only for `SURVEY_BINDING`) |
| `rule_authoring.simulate` (over cases) | needs a target | refuses a survey-only draft with a plain reason: it is evaluated in Survey assignment, against synthetic applications |
| `script_assignment.py` (operational) | all rules in scope | script-backed only, by the loader default — the same set as before |
| `api/assignment_rules.py` registry, draft, history, diff | inner join | left join; `target_kind`, `market` returned; survey-only shows "No script — survey bindings only" |
| `api/scripts.py` `/script-assignment-rules`, family card "rules that target it" | inner join | unchanged: a script-side list of script-backed rules |
| `survey/assignment.py` `_rule_version`, `policy`, `candidates` | market through the script | market from the rule; both kinds |
| `survey/assignment_groups.py`, `journey_trace.py` | join on the rule only | unchanged |
| Triggers `assignment_rule_check`, `script_assignment_check` | compare the target | unchanged; safe with an absent target (verified by test) |
| Seed | inserts script-backed rules | unchanged; the column default and the migration back-fill cover them |

### 3.4 Semantics preserved

`rule_engine` is not edited. Matching, priority, specificity, fallback, fail-closed outcomes, overlap rules,
explanations, published immutability, the two-person lifecycle and its audit are as they were. No new assignment
engine. OR-2 and OR-3 are not touched or resolved. The one new scoping — which rules a consumer loads — is the explicit
`kinds` argument above, deterministic and tested from both sides.

### 3.5 Survey bindings (AR-3)

A binding to a survey-only rule is the existing binding, unchanged in lifecycle (three people). Market consistency is
checked where it already is (`propose`: rule market against survey market) and additionally by a new database trigger
on `survey_assignment_binding`: the binding's market, the rule's market and the survey definition's market must be the
same. A requirement-group member must be a rule of the group's market (application check, existing; database trigger,
new). Historical composite plans, assignment evaluations and coordinated simulations are insert-only and are not
rewritten by a new rule version or binding — verified by fingerprint in the tests.

### 3.6 Finding rules (FR-1)

No schema change: the table has its own market and no script reference. Dedicated permissions only (§3.7). The engine,
the rule schema, published sets, history and identifiers are untouched.

**Question-scoped rules.** A rule of scope `QUESTION` targets a script `question_code`. Survey items carry
server-issued codes (`Q-<n>`), so such a rule cannot match a survey item, and no identity mapping is invented here.
It keeps working for script-based evaluation. Recorded as dependency **DEP-FR-1** for a later checkpoint; rules of
scope `CONTROL` and `ANY_QUESTION` already serve both worlds.

### 3.7 Permission transition (PT-1)

Eight new permissions, in the existing convention, **created and granted to no role**:

| Capability | New permission | Legacy permission that keeps working |
|---|---|---|
| Assignment Rules — read (registry, draft, history, diff, explain, options) | `assignment_rule.read` | `script.read` |
| — create, edit, validate, submit, abandon | `assignment_rule.edit` | `script.edit` |
| — review | `assignment_rule.approve` | `script.approve` |
| — publish | `assignment_rule.publish` | `script.publish` |
| Finding Rules — read | `finding_rule.read` | `script.read` |
| — create, edit, submit, abandon | `finding_rule.edit` | `script.edit` |
| — review | `finding_rule.approve` | `script.approve` |
| — publish | `finding_rule.publish` | `script.publish` |

- Each operation accepts **either** permission (`require_any`). An existing user keeps exactly the access they have; a
  user given only the new permissions can govern rules without any Script Studio permission.
- **Not changed:** `script.assign` (apply a script to a case, batch assignment) and rule **simulation over cases**,
  which reads case data — both stay on their existing permissions. No separate "assignment execution" permission is
  introduced: the operational one already is separate.
- **No implication:** `survey.edit` grants nothing here; the new permissions grant nothing in Script Studio or Survey
  Studio. Segregation of duties is the lifecycle's own identity rule, which no permission overrides.
- **Market scope** is the caller's markets on every operation, as today.
- **Later removal** of the legacy alternative is a one-line change per operation plus a grant migration — possible,
  not done now.

### 3.8 Settings and compatibility with a schema behind the head

`shared_rule_services_enabled`, off by default; needs migration `0037`. With it off: no survey-only rule can be
created, and every statement that reads the two new columns does so through `to_jsonb`, falling back to the script
family's market and to `SCRIPT_VERSION` — so the same code runs on a schema at `0036` (development today) exactly as
before. The dedicated permissions simply are not held by anyone until granted.

## 4. Data-preservation plan — migration `0037_shared_rule_services`

| Step | What | Safeguard |
|---|---|---|
| 1 | add `market_code` (nullable) and `target_kind` (default `SCRIPT_VERSION`) to `script_assignment_rule_version`; add `target_kind` to `assignment_rule_draft` | adding a column with a constant default rewrites no row content and fires no row trigger |
| 2 | **back-fill** `market_code` from each rule's target script family | the immutability trigger is disabled for this one statement and re-enabled in the same transaction; only `market_code` is written |
| 3 | **verify** inside the migration: no rule without a market; every rule's market equals its script family's; the number of rules, and the SHA-256 over every pre-existing column of every rule, are the same as before step 1 | any mismatch raises and the whole migration rolls back (DDL is transactional) |
| 4 | `market_code` NOT NULL; market trigger; `target_script_version_id` nullable; the kind/target CHECK on both tables; the relaxed "frozen" CHECK on drafts | the CHECKs are validated against every existing row when added |
| 5 | triggers: rule market = target family market; draft kind never changes; `script_assignment` matched rule must be script-backed; binding market consistency; group-member market consistency | each validated against existing rows by a query in the migration before it is created |
| 6 | the eight permissions, granted to nobody | — |

**Preserved, and proved by test on a populated schema:** every rule's identity, version, predicate, priority, target,
checksum, author and checker; publication rows and change events; every survey binding, group, composite plan and
assignment evaluation; every script assignment, session, run, execution and finding.

**Downgrade** — guarded: refuses while any survey-only rule version or draft exists ("survey-only assignment rules
exist; they cannot be expressed without the columns"), or while a role holds one of the new permissions. Otherwise it
removes the triggers, the columns and the permissions and restores the original constraints; the rule rows return to
exactly what they were.

**Partial failure:** the migration is one transaction; a failure at any step leaves the schema at `0036` with the
immutability trigger enabled (tested by forcing the verification to fail).

**Development:** NOT applied. It stays at `0036` until separately authorised.

## 5. User experience

Navigation is unchanged (Design & Govern → Assignment Rules, Finding Rules), now also shown to a holder of the
dedicated read permission. In Assignment Rules: a new rule asks what it selects — "A script, for cases" or "A survey,
through a binding"; the registry, the rule page and the builder say which, name the market, and for a survey-only
rule replace the script picker with a statement — "This rule assigns no script and can never assign one to a case" —
and a link to Survey bindings and groups. Script Studio and the Simulation Workbench are not changed.

## 6. Not in SHARED-1

Operational assignment of a survey to a case (OPS-1). A cross-system question identity (DEP-FR-1). Controls
maintenance. Removal of any legacy permission, route, table or screen. MIG-2. Voice.
