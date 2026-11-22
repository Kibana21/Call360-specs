# ASG-2A — Several surveys for one application: implementation report

With the ASG-1 acceptance closure (assignment read access) and the development migration `0030`.

**Checkpoint:** ASG-2A, authorised by the owner on 2026-11-22 ("Accept ASG-1 and Implement ASG-2A Multi-Survey
Assignment"), decision register D-246…D-258, OR-2, OR-3.
**Status: BUILT AND TECHNICALLY VERIFIED — presented for the owner's review. Not accepted.**
**Prepared:** 2026-11-22.

**SIMULATION ONLY.** Nothing here assigns a survey to a customer case, starts a call, or makes anything eligible for
one.

**Exclusions held (D-256).** No real customer assignment. No live callbacks. No Genesys or voice integration. No
cross-survey non-answer, refusal, escalation or consent policy. No automatic merging or de-duplication of surveys or
questions. No second rule language and no second execution engine. Script Studio not modified or retired. No
evaluation or findings integration. No destructive data migration. No golden fixture changed.

**Not committed, not pushed.** The three repositories are still at the commits the owner pushed (backend `182f6e5`,
frontend `9f497d5`, specs `755bf00`). SS-03B, its closure, ASG-1 and ASG-2A are all uncommitted working-tree
changes: no commit authorisation has been given for any of them.

**Not claimed.** Not production readiness; not business-user UX acceptance; not screen-reader sign-off; not
Compliance approval of any wording, rule, group or ordering; not a decision on any open policy.

---

## 1. ASG-1 acceptance closure — who may read assignment data (D-247)

ASG-1 is recorded as accepted as TECHNICALLY VERIFIED for single-survey assignment, with the binding as an interim
adapter (D-246).

**The review.** Under ASG-1 `survey.read` opened the assignment policy, which shows the conditions and precedence of
published assignment rules — Script Studio data that otherwise needs `script.read` — and the policy also returned
each rule's script target.

| | ASG-1 as reviewed | Now |
|---|---|---|
| Read the policy, the governed inputs, a binding, a recorded selection | `survey.read` | **`survey.assignment.read`** — a permission of its own, created by migration `0030`, granted to no role |
| Propose / approve / publish a binding; make a selection; start a simulation | the one survey permission | that permission **and** `survey.assignment.read` |
| A rule in the policy | reference, name, market, conditions, priority, specificity, fallback, effective window, **script target** | the same **without the script target**. Never returned: rule author, checker, checksum, drafts, history |
| The Assignment Rules API (`/assignment-rules…`) and `script.*` | unchanged | unchanged — a survey identity still gets `403` there |

Proof (`tests/test_survey_assignment.py`, and in the browser `zz-asg1.persisted.ts`):

* a person holding `survey.read` alone, and one holding read + edit + approve + publish + simulate, each get `403` on
  the policy, the options, a binding, a recorded selection and on making a selection; each refusal is audited as
  `missing permission survey.assignment.read`;
* the permission is held by no role after migration;
* the exact set of fields of a policy rule is asserted;
* in the browser a survey reader has no link to the page, sees "You cannot open the assignment policy" when going
  there directly, and the survey author gets `403` from `/api/v1/assignment-rules`.

In development the permission is granted to the three designated synthetic identities only.

## 2. Development database — migration `0030_survey_assignment`

Evidence: `docs/acceptance/evidence/ASG-2A/dev-migration-0030/`.

| Condition (D-248) | Result |
|---|---|
| 1. Automated test of the downgrade refusal with bindings | `test_zz_migration_0030_goes_down_and_up_empty_and_refuses_while_a_governed_binding_exists`: with one published binding the downgrade raises "governed survey assignment bindings exist"; the binding and its three events are still there; the head is restored |
| 2. Empty-schema upgrade and downgrade | the same test: down removes exactly the four tables, the guard function and the permission; up restores them; every other table is as it was |
| 3. Additive | four tables, their triggers, one function, one permission row. Nothing removed (`dev30_diff.txt`) |
| 4. Verified fresh backup and inventory | 115 tables, 14,934 rows. `_db_backups/call360_dev_before_0030_20261122.dump`, 1,860,459 bytes, SHA-256 `0ab7b34e…9c3aaa5e`, taken with the API server stopped; row counts equal the inventory; full SQL dry run of the restore without error. `_db_backups/RESTORE.md` extended |
| 5. Script Studio and Survey Studio records preserved | 113 of 115 pre-existing tables byte-identical in content; the other two are `alembic_version` and `permission` (42 → 43). Column definitions identical. 4 surveys, 2 survey versions, 4 simulations, 258 callback cases, 11 script versions, 8 assignment-rule versions, 4 rule drafts, 251 script assignments, 24 Voice Lab sessions — unchanged. No foreign key points *into* the new tables from any other table |
| 6. Authorisation and market isolation | the tests of §1 and §8; on the dev server: a survey identity gets `403` from the Assignment Rules API, and an application for another market gets `404` |
| Only the intended migration | `uv run alembic upgrade 0030_survey_assignment`. Revision after: `0030`. **`0031` was not applied**: no group or composite table exists in development |

**Demonstration on the development server** (`dev30_walk.txt`, screens `DEVA01`…`DEVA03`), synthetic data only:

1. Policy read: three published SG rules, none bound.
2. A synthetic application: `SURVEY_NOT_BOUND`, winning rule `SG-SALES-VERIFY v2`, nothing selected.
3. Binding `SG-SALES-VERIFY v2` → `DEV-CHECK-AD5AEA8F` v1.0: proposed by `dev.survey.author`, approved by
   `dev.survey.checker`, published by `dev.survey.publisher`; the proposer could not approve.
4. The same application: `SELECTED`, with the rule, the reason and the survey version; call plan `READY` with its
   fingerprint and modules.
5. Again with the inputs in another order: the same version, decision fingerprint and plan fingerprint.
6. A simulation started from the selection: the SS-03B simulation of that version, linked to the selection.
7. `callback_case`, `contact_attempt`, `conversation_session`, `survey_run`, `answer_observation`,
   `script_assignment`, `script_assignment_rule_version`, `assignment_rule_draft`, `finding`, `media_asset`,
   `transcript_run`, `transcript_segment`: identical row counts before and after.

Nothing was reset, re-seeded or destructively altered. One binding, four selections and one simulation were
**added**. Because a binding now exists, **`0030` can no longer be downgraded**; the ways back are in `RESTORE.md`
(switch the setting off; withdraw the binding; or a full restore).

ASG-2A is **off** in development: `/api/v1/survey-assignment/groups` returns `404` there and the page shows
single-survey assignment only.

## 3. Assessment of the existing design, and the extension chosen

| Existing part | What it does | What ASG-2A needs from it |
|---|---|---|
| `rule_engine.evaluate` | ranks every matching candidate and returns ONE winner or fails closed | nothing changed: it is called once per requirement, with that requirement's rules only |
| `rule_inputs.published_candidates` | loads the published rules of a market | unchanged |
| ASG-1 binding and `assignment.candidates` | re-targets each rule to its bound survey version | unchanged; the decision step was factored into `assignment.decide_candidates` so it can run over a subset. `assignment.select` (ASG-1) calls it with every rule and is otherwise identical |
| Assignment-rule tables | hold rules | not altered; a group member *refers* to a rule version, as a binding does |

**The smallest additive extension:** one new governed artifact, the **requirement group** — a governed, versioned set
of rule versions that compete for one requirement — and nothing else. The semantics were written before any code:
`34_ASG-2A_GROUPING_AND_MATCHING_SEMANTICS.md`.

Two things the assessment found that the owner should know (both recorded as open items):

* **OR-2 — the existing rule validation knows one winner only.** It refuses two rules of equal precedence that can
  both match (`CONFLICT_SAME_TARGET_TIE`). Rules of *different* requirements are meant to match together, so today
  they must be given different priorities to be publishable — although priority means nothing between groups.
  Changing that validation is a change to Script Studio and was not made.
* **OR-3 — the rule language cannot say "replacement" or "CI rider".** Its nine fields are market, callback purpose,
  product family, product, ILP indicator, SBQ risk band, sales channel, premium frequency and contact role. See §7.

## 4. Architecture and data model

```
 synthetic application ──► assignment_inputs ─┐                    facts ─┐
   (one snapshot, one fingerprint;            │                           │
    the two parts are NOT reconciled)         ▼                           │
                              published rule versions  (Assignment Rules, unchanged)
                                        │  re-targeted through
                                        ▼
                              survey bindings          (ASG-1: rule version → survey version)
                                        │  gathered by
                                        ▼
                              requirement groups       (ASG-2A: PRIMARY · ADD_REQUIRED · ALTERNATIVE)
                                        │
              ┌─────────────────────────┼─────────────────────────┐
              ▼                         ▼                         ▼
     rule_engine.evaluate      rule_engine.evaluate      rule_engine.evaluate        ← the existing engine,
      over the PRIMARY          over one ADD_REQUIRED     over one ALTERNATIVE          once per group
      group's rules             group's rules             group's rules
              │                         │                         │
              ▼                         ▼                         ▼
     survey version A          survey version B           survey version C           ← exact, pinned, verified
              │                         │                         │                           │
              ▼                         ▼                         ▼                           ▼
     SS-03B plan of A          SS-03B plan of B           SS-03B plan of C     ← callplan.assemble, once per survey
              └─────────────────────────┼─────────────────────────┘
                                        ▼
                               composite plan  = references to the three plans
                                               + ordering (only if governed)
                                               + cross-survey policy: UNRESOLVED
                                               + composite fingerprint
```

| Table (migration `0031`, all insert-only) | Holds |
|---|---|
| `survey_assignment_group` | code, version, market, kind, name, purpose (at least 10 characters), optional `sequence`, proposer |
| `survey_assignment_group_member` | the exact rule versions of a group version |
| `survey_assignment_group_event` | `PROPOSED → APPROVED \| REJECTED \| WITHDRAWN → PUBLISHED → SUPERSEDED \| WITHDRAWN`; a trigger refuses an approver who proposed and a publisher who proposed or approved |
| `survey_composite_plan` | the application, its fingerprint, the time decided for, the three statuses, the composite document and its fingerprint. `record_class = 'SIMULATION'` by CHECK. A CHECK refuses `READY` or `BLOCKED` unless the selection is `RESOLVED` and the ordering `GOVERNED` or `NOT_APPLICABLE` |
| `survey_composite_plan_member` | each requirement: its group, state and outcome, and — exactly when selected — the survey version, rule version, binding, individual call plan and its fingerprint (CHECK) |

Code: `app/domain/survey/assignment_groups.py` (groups, `select_set`, `ordering_of`, `compose_pure`, `compose`,
`composite`), `app/api/survey_assignment_groups.py` (seven operations). Contract `04_…` §15. Setting
`survey_assignment_groups_enabled`, off by default.

## 5. What a composite decides, and what it refuses to decide

| Decided, deterministically | From |
|---|---|
| which requirement each rule serves | the published group it is a member of |
| whether a requirement is selected, does not apply, or is unresolved | the existing engine over that group's rules |
| which survey version | the winning rule's published binding, pinned by id and fingerprints |
| each survey's own plan | the SS-03B assembler on that version's pinned documents |
| the order | the groups' governed `sequence` — only when every selected group has one and they differ |

| Not decided — reported instead | How it is reported |
|---|---|
| an order nobody governed | `ordering.status = UNRESOLVED` (`ABSENT`, `PARTIAL`, `CONFLICTING`); `order` is null; the surveys are *listed* with a note that the listing is not an order; the composite is not `READY` |
| what happens between surveys (an escalation, a refusal, an incomplete answer, an ending in one) | `cross_survey_policy.status = UNRESOLVED` whenever more than one survey is selected |
| whether the two parts of the application agree | `input_consistency.status = UNVERIFIED`, always |
| a tie | `AMBIGUOUS` for that requirement; the selection is `UNRESOLVED_REQUIREMENT` |
| a configuration that cannot be trusted | `UNRESOLVED_CONFIGURATION` with stable issue codes |
| whether a call may be made | not a field of the composite at all |

No priority between groups, no default order by kind, no exclusion rule, no fallback survey and no continuation rule
was introduced.

## 6. Input consistency — the data an approved mapping would have to settle

A synthetic application is one snapshot with one fingerprint and two parts. Nothing derives one from the other.

| Assignment input (rule language) | Catalog fact that *appears* to describe the same thing | What is not established |
|---|---|---|
| `product_family` (PROTECTION, ILP, ENDOWMENT) | `policy.product_family` (PROTECTION, ILP, ENDOWMENT) | the same codes today, governed in two places; nothing says they must stay equal |
| `selling_channel` (AGENCY, BANCASSURANCE, BROKER, DIRECT) | `sale.channel` (AGENCY, BANCASSURANCE, DIRECT) | the lists differ (`BROKER`); no rule for the difference |
| `is_ilp` | derivable from `policy.product_family = ILP` | a derivation, not an approved one |
| `product_code` | `policy.plan_name` | a code and a display name; no mapping |
| `premium_frequency`, `case_purpose`, `risk_band`, `contact_role`, `market` | none | no fact carries them |
| none | `policy.annual_premium`, `policy.sum_assured`, `policy.is_replacement`, `customer.age_years`, `policy.term_years` | no rule field carries them — so a rule cannot read "replacement" although a fact states it |

**What deriving both from one application snapshot needs** (identified, not built):

1. the authoritative source of each value in a real application — the policy fact snapshot and sale event of intake
   for the product and channel values, the FINAL SBQ assessment for the risk band, the party roles for the contact
   role — with its lineage;
2. one governed, versioned mapping artifact stating, per value, the source field, the allowed transformation and
   what happens when the source is missing or conflicts;
3. the owner's and Compliance's approval of that mapping;
4. a decision on whether rule fields may be *added* for facts that exist only in the catalog (replacement, rider),
   which is a change to the Assignment Rules language.

Until then every composite says `UNVERIFIED`, and the screen shows a standing warning that the two parts are not
reconciled.

## 7. The scenarios, and their stand-ins

The owner's tests speak of a Life application, a Life replacement and a Life application with a CI rider. The rule
language has no field for "replaces a policy" or "has a CI rider" (OR-3), and ASG-2A may neither add a rule field nor
invent a mapping from a fact. The mechanics are therefore proved with **stand-in conditions**, named as such in the
tests and here:

| In the tests | Is expressed as |
|---|---|
| a Life application | `product_family = PROTECTION` |
| "this sale replaces a policy" | `premium_frequency = SINGLE` (stand-in) |
| "has a critical-illness rider" | `selling_channel = BANCASSURANCE` (stand-in) |
| two closing surveys that compete | a rule for every application and a more specific rule for `selling_channel = AGENCY` |

What is proved is real: several requirements, each decided by the existing engine over its own rules, each pinned,
each planned. What is *not* proved is that Call360 can recognise a replacement or a rider from an application —
it cannot, until such attributes are governed.

## 8. Verification — the eighteen demonstrations

Evidence: `docs/acceptance/evidence/ASG-2A/`. Automated tests ran only against the isolated schema `call360_test`.
Rules were made through the existing Assignment Rules API; surveys are golden fixtures published by three people;
bindings and groups went through propose, approve and publish by three people. The scenarios use the stand-ins of §7.

| # | To demonstrate | Result | How |
|---|---|---|---|
| 1 | A Life application selects one primary survey | pass | the `PRIMARY` group selects the Life survey by rule `P-LIFE`; both additional groups are `NOT_APPLICABLE` — stated, not silent; an ILP application gets the ILP survey from the same group |
| 2 | A Life replacement selects the primary plus a required replacement survey | pass | three surveys, order `GOVERNED` (positions 1, 2, 9), `READY`. The same application through the single-survey ASG-1 operation gets the Life survey only, with the replacement rule shown as matching and discarded — the defect this checkpoint removes |
| 3 | A Life application with a CI rider can select an additional CI survey | pass | the `ADD-CI` group selects the CI survey by `R-CI` |
| 4 | Two alternatives resolved by explicit approved precedence | pass | in the `ALTERNATIVE` group both closing rules match an agency application; the agency rule wins on the engine's own specificity; the trace shows only that group's two rules |
| 5 | An ambiguous alternative fails closed | pass | two rules of equal precedence in the group: `AMBIGUOUS`, nothing selected for that requirement, selection `UNRESOLVED_REQUIREMENT`, composite `UNRESOLVED`; the primary is still shown selected. (The tie is produced at the loader: the existing rule validation refuses to publish such rules — OR-2) |
| 6 | A missing input does not silently become FALSE | pass | without the input the replacement group reads: `INPUT_MISSING`, state `UNRESOLVED` — not `NOT_APPLICABLE`; the primary stays selected; the composite is `UNRESOLVED`. A missing *fact* stays `MISSING` in the plan that reads it and that plan is `BLOCKED` |
| 7 | An unbound winning requirement does not disappear | pass | with the replacement rule's binding withdrawn: `SURVEY_NOT_BOUND`, state `UNRESOLVED`, composite `UNRESOLVED` |
| 8 | A superseded survey is never silently replaced | pass | the bound version superseded: `TARGET_NOT_EFFECTIVE`; the trace shows the pinned version and that it is superseded; nothing newer is substituted |
| 9 | All surveys stay pinned to exact immutable versions | pass | each selected survey's version id, binding id, content and manifest fingerprints equal those of its binding and of its recorded call plan |
| 10 | A newer survey publication does not change an existing composite | pass | the recorded composite reads back identical with the same fingerprint, `fingerprint_verified`, every member `plan_intact`, the same version ids — and `recompute_consistent: false` says it would differ if computed now |
| 11 | Individual call-plan fingerprints remain intact | pass | each member's plan fingerprint equals the stored plan's, and equals the fingerprint of a plan generated for that survey **on its own** with the same facts |
| 12 | Composite fingerprints are deterministic | pass | the same application with inputs and facts in another order: a new record, the same composite, application and plan fingerprints; a different application has a different fingerprint |
| 13 | Cross-market and unauthorised references are denied | pass | no assignment-read permission: `403` on groups, composites and proposals; another market: no SG group visible, `404` on an SG composite, on composing for SG, on proposing with an SG rule and on withdrawing an SG group; no CSRF token: `403` |
| 14 | An invalid configuration cannot create a falsely READY composite | pass | no primary group → `UNRESOLVED_CONFIGURATION`; a group without a governed position, or with a conflicting one → ordering `UNRESOLVED`, composite `UNRESOLVED` though every individual plan is `READY`; a second primary group or a rule in two groups is refused at publication; the **database** refuses a row that is `READY` with an unresolved selection or ordering |
| 15 | Existing single-survey ASG-1 results remain unchanged | pass | the ASG-1 selection for the same application before any group and after all of them: the same outcome, and every rule judged the same; all ASG-1 tests pass unchanged |
| 16 | 82 golden runs and 14 golden plans still pass | **82 / 82, 14 / 14** | `assignment_and_golden_tests.txt`; the Python results file is unchanged |
| 17 | FI-1, FI-2, LIB-1, SS-03B and ASG-1 regression suites pass | **20 / 20**, and the ASG-2A journey: **21 / 21** | `playwright_persisted.txt` |
| 18 | No operational case, assignment, callback attempt or finding is created | pass | script assignments, case states and holds have the same fingerprint, and `callback_case`, `contact_attempt`, `conversation_session`, `survey_run`, `script_assignment`, `finding`, `media_asset`, `transcript_run` the same row counts, before and after |

Also proved: proposer, approver and publisher of a group are three different people (service and database trigger);
a group needs a purpose; an additional-required group cannot span two surveys; an alternative group needs two rules;
a new version of a group supersedes the old one and never edits it; groups, members, composites and their members
cannot be updated or deleted; with the setting off none of it exists and ASG-1 is where it was; migration `0031`
goes down and up on an empty schema and refuses to go down while a group exists.

| Check | Result |
|---|---|
| Backend tests | **822 passed, 0 failed** (818 at ASG-1; + 1 migration `0030` round trip and refusal, + 3 ASG-2A) |
| `ruff check`, `ruff format --check`, `mypy` (strict, 111 files) | clean |
| Generated files | OpenAPI matches; canonical fixture documents match; Python engine results match (82 runs, 14 plans) |
| Frontend unit tests | **612 passed** |
| `tsc`, `eslint`, `api:check`, production build | clean |
| Persisted journeys | **21 / 21** (FI-1 6, FI-2 3, LIB-1 5, SS-03B 5, ASG-1 1, ASG-2A 1) |
| Prototype journeys | **13 / 13** |
| Standard journeys | **33 / 33** |
| Specs validator | pass |
| Migration head | `0031_survey_assignment_groups`; development at `0030` |

After the last full backend run one line was added to the ASG-2A test so that it can write the example composites of
§9 on request; that file was run again with the assignment, rule and golden tests (126 passed).

Faults of mine found and corrected on the way: a browser-journey helper waited for an element that did not exist yet;
the page could let a recorded composite, still loading from its link, replace a newer one just computed (fixed in
the page); and I changed the migration head while a background test run was in progress, which invalidated that run
— it was stopped and everything was run again.

## 9. Composite plan examples

`docs/acceptance/evidence/ASG-2A/composite_plan_examples.txt` holds five composites as the server returned them;
`composite_plan_example_life_replacement.json` is one in full. In short:

| Application | Selected | Ordering | `plan_status` |
|---|---|---|---|
| Life | Life survey (primary) · standard closing survey (alternative) | `GOVERNED`: primary, closing | `READY` |
| Life replacement | Life (primary) · replacement (additional required) · closing (alternative) | `GOVERNED`: primary, replacement, closing | `READY` |
| Life with CI rider, CI group without a position | Life · CI · closing | `UNRESOLVED` (`PARTIAL`); `order` null | `UNRESOLVED` |
| Life replacement, premium frequency not known | Life · closing; replacement `UNRESOLVED` (`INPUT_MISSING`) | — | `UNRESOLVED` |
| Life replacement, replacement rule unbound | Life · closing; replacement `UNRESOLVED` (`SURVEY_NOT_BOUND`) | — | `UNRESOLVED` |

The second, abridged:

```
selection_status RESOLVED | ordering_status GOVERNED | plan_status READY
input_consistency: UNVERIFIED
requirements:
   PRIMARY-SG       PRIMARY       SELECTED        rule P-LIFE v1 -> Life survey v1.0         | plan READY
   ADD-REPLACEMENT  ADD_REQUIRED  SELECTED        rule R-REPL v1 -> Replacement survey v1.0  | plan READY
   ADD-CI           ADD_REQUIRED  NOT_APPLICABLE  NO_MATCH
   ALT-CLOSING      ALTERNATIVE   SELECTED        rule C-STD v1  -> Closing survey v1.0      | plan READY
ordering: GOVERNED | order [PRIMARY-SG, ADD-REPLACEMENT, ALT-CLOSING]
cross_survey_policy: UNRESOLVED
members recorded: each SELECTED member names its survey version, rule version, binding and call plan; plan intact
```

Every `READY` above means: the set is settled, the order is governed, each plan can be computed. Whether one survey's
ending lets the next begin is `UNRESOLVED` in all of them.

## 10. The Survey assignment screen

One page, extended; no second product.

| Asked for | On the page |
|---|---|
| The selected primary survey | first card of "Why — each requirement", tagged *Primary survey*; first line of "The required survey journey" |
| Additional required surveys | their cards, tagged *Additional required survey* — *Selected*, or "does not apply to this application" |
| Alternative groups and their selected survey | their cards, tagged *Alternative surveys*, with the rules of the group as the engine judged them |
| Why each matched | the rule, "stands for" the survey version; and, on opening, every rule of the group with each condition met, not met or not known |
| Unresolved or conflicting requirements | the card says *Unresolved* with the reason and the engine's code; configuration issues in a warning panel; the heading says the set is not complete |
| Each survey's published version | linked name and version, with the content fingerprint and "manifest verified" |
| Each survey's individual plan status | "its own plan: can be computed / blocked", items, open points, its fingerprint; links to its full call plan and its simulation |
| A combined overview | "The required survey journey": numbered when the order is governed; a plain list with a warning when it is not; and the statement that what happens between the surveys is not decided |
| Governance of groups | "Requirement groups": each group with kind, purpose, rules and position; propose (a form), approve, publish, withdraw, each offered only to the person who may |

The single-survey selection of ASG-1 stays on the page as "Single-survey selection only".

Screens (`docs/acceptance/evidence/ASG-2A/screens/`): `ASG2A01` no groups: configuration not trusted · `ASG2A02` the
primary group proposed · `ASG2A03` a Life application: the primary survey · `ASG2A04` a Life replacement: primary
plus required · `ASG2A05` with a CI rider: an additional survey, order unresolved · `ASG2A06` alternatives resolved
by precedence · `ASG2A07` a missing input: the requirement unresolved · `ASG10` a survey reader cannot open the
policy.

## 11. API changes

Contract `04_…` §14.4 (amended) and §15. Additive against the committed contract.

| Change | Detail |
|---|---|
| ASG-1 operations | every one now needs `survey.assignment.read` (reads: instead of `survey.read`; writes: in addition) |
| `SurveyAssignmentRule` | `script_target` removed (ASG-1 was never committed or enabled outside tests before this) |
| Seven new operations | `GET /groups`, `POST /groups`, `POST /groups/{id}/decision`, `…/publish`, `…/withdraw`, `POST /composite-plans`, `GET /composite-plans/{id}` |
| Eight new schemas | `SurveyAssignmentGroup…`, `SurveyCompositePlan…` |
| Settings | `survey_assignment_groups_enabled` (off by default) |
| Migrations | `0030` amended before it was applied anywhere but the test schema (the permission); `0031_survey_assignment_groups` new |

OpenAPI: SHA-256 `2b3b0c8e86163df84aa516a1029aed7b4aae64a72ab6eba62cc89f621473e94c`. Against the committed
contract (`88baaf2c…`): 221 → 243 operations, 451 → 475 schemas, none removed, no existing schema changed, one
existing operation changed in its description only (`openapi_additivity.txt`).

## 12. Changed files

Uncommitted, on top of backend `182f6e5`, frontend `9f497d5`, specs `755bf00`. Listed: what changed since the ASG-1
report (`33_…` §8 and `32_…` §10 list the rest).

**Call360-backend**

| File | Change |
|---|---|
| `migrations/versions/0030_survey_assignment.py` | + permission `survey.assignment.read` |
| `migrations/versions/0031_survey_assignment_groups.py` (new) | five insert-only tables and the group-event guard |
| `app/domain/survey/assignment.py` | the decision step factored into `decide_candidates`; the policy no longer returns the script target |
| `app/domain/survey/assignment_groups.py` (new) | groups, selection per group, ordering, composite |
| `app/api/survey_assignments.py` | `survey.assignment.read` on every operation |
| `app/api/survey_assignment_groups.py` (new) | seven operations |
| `app/core/settings.py`, `app/main.py`, `app/domain/catalog.py`, `scripts/export_openapi.py`, `contracts/generated/*` | the setting, the head rule for five optional revisions, the catalog, the contract |
| `scripts/dev_survey_identities.py`, `scripts/e2e_survey_setup.py` | the assignment-read permission for the designated identities |
| `tests/test_survey_assignment_groups.py` (new) | 3 tests (the journey of eighteen demonstrations; setting off; migration `0031`) |
| `tests/test_survey_assignment.py` | read-access tests; migration `0030` downgrade refusal and empty round trip |
| `tests/test_survey_store.py`, `test_survey_lib1.py`, `test_survey_api.py`, `test_survey_simulation.py`, `test_admin_access.py` | head, table, permission and contract counts |
| `.env` (gitignored) | `SURVEY_ASSIGNMENT_ENABLED=true` for local development |

Not touched: `rule_engine.py`, `rule_inputs.py`, `rule_authoring.py`, `script_assignment.py`, the Assignment Rules and
script-assignment APIs, every script table and migration, `execution.py`, `callplan.py`, `wording.py`.

**Call360-frontend**

| File | Change |
|---|---|
| `src/features/surveystudio/persist/AssignmentGroups.tsx` (new) | the groups section and the composite result |
| `src/features/surveystudio/persist/AssignmentPage.tsx`, `assignmentApi.ts` | the permission gate; groups; composite; a recorded result loading from its link can no longer replace a newer one |
| `src/features/surveystudio/persist/PersistedStudioRoot.tsx` | the link is shown only with the permission |
| `src/styles/survey-studio.css` | styles (appended) |
| `src/api/generated/*`, `src/api/openapi.pinned.json`, `src/api/contract.lock.json` | regenerated client |
| `playwright.persisted.config.ts`, `e2e/persisted/zz-asg1.persisted.ts`, `e2e/persisted/zz-asg2a.persisted.ts` (new) | groups on in the persisted test server; read-access checks; the ASG-2A journey |

**Call360-specs**

| File | Change |
|---|---|
| `docs/plans/survey-studio/34_ASG-2A_GROUPING_AND_MATCHING_SEMANTICS.md` (new) | the semantics, written before implementation |
| `docs/plans/survey-studio/35_ASG-2A_IMPLEMENTATION_REPORT.md` (new) | this report |
| `docs/plans/survey-studio/04_SS-01_CANONICAL_CONTRACTS.md` | §14.4 amended, §15 |
| `docs/plans/survey-studio/06_SS-01_DECISION_REGISTER.md` | D-246…D-258, OR-2, OR-3 |
| `docs/plans/survey-studio/README.md`, `docs/plans/SESSION_HANDOFF.md` | index and handoff |
| `docs/acceptance/evidence/ASG-2A/` (new) | evidence |

**Outside the repositories:** `_db_backups/call360_dev_before_0030_20261122.dump`, the extended
`_db_backups/RESTORE.md`, and the development database at `0030` with one synthetic binding.

## 13. Known limitations

1. **Development is at `0030`, not `0031`.** Requirement groups and composite plans run only in the test schema.
2. **The demonstrations use stand-in conditions** for "replacement" and "CI rider" (§7, OR-3).
3. **Complementary rules need different priorities to be publishable** (OR-2), although priority between groups has
   no meaning. A real policy author will find that confusing.
4. **Inputs and facts are not reconciled** (§6). An application can state an ILP product family beside a Protection
   fact and nothing objects.
5. **The ambiguous-alternative case could not be produced with published rules**, because the existing validation
   refuses them; the test produces the tie in the candidates the loader returns. The fail-closed path is the
   engine's own and is exercised.
6. **A group is a set of rule versions.** Publishing a new version of a member rule leaves the group pointing at the
   superseded version until a new version of the group is published; the requirement is then unresolved
   (`MEMBER_NOT_PUBLISHED`), not silently dropped.
7. **An ASG-1 binding outside any group** makes the multi-survey configuration unresolved whenever that rule matches
   or may match the application. That is deliberate, and it means existing bindings must be placed in a group before
   composites resolve.
8. **`READY` requires a governed order** even where an order might not matter to the business. Nothing approved says
   it does not.
9. **Individual simulations only.** From a composite a person can simulate each survey on its own; there is no
   combined run (ASG-2B).
10. **The group form is basic**: it lists published rules as checkboxes and does not explain why a proposal is
    refused beyond the server's message.
11. **No retention or clean-up** of simulation, selection or composite records (OR-1).
12. **Screens verified in Chromium at 1440 px** by automated journeys; no business-user or screen-reader review.
13. Carried forward unchanged: the limitations of `33_…` §9, `32_…` §11 and the LIB-1 UX limitations.
14. **Not my change:** in `Call360-specs`, `docs/acceptance/evidence/LIB-1/screens.zip` is deleted and a `.DS_Store`
    is modified in the working tree.

## 14. Unresolved policy register

| # | Decision nobody has made | Blocks |
|---|---|---|
| 1 | D-NA-1…D-NA-17: silence, refusal, repeats, timeouts, optional blanks, consent refusal | anything beyond simulation |
| 2 | **Cross-survey continuation**: does an escalation, a refusal, an incomplete answer or a terminal outcome in one survey let the next proceed? Is consent asked once or per survey? | ASG-2B |
| 3 | **Ordering**: whether every multi-survey journey needs a governed order, who governs it, and whether kind implies anything | a `READY` composite without explicit positions |
| 4 | **Rule attributes for replacement, riders and other triggers** (OR-3) | real additional-survey requirements |
| 5 | **Rule validation for complementary rules** (OR-2) | a sensible authoring experience for groups |
| 6 | **The mapping between assignment inputs and call-plan facts**, and the source of each in a real application | one reconciled application snapshot |
| 7 | Whether rules should target survey versions natively (changing Script Studio rule tables) | retiring the binding adapter |
| 8 | Whether a `PRIMARY` group with no match can ever be acceptable ("no survey needed") | applications outside every rule |
| 9 | Whether two requirements selecting the same survey are asked twice or once | a combined run |
| 10 | Who may govern groups and bindings: the survey roles (today) or others | role design |
| 11 | Which catalog fields may be spoken; approval of wording | published surveys with customer values |
| 12 | Retention of simulation, selection and composite records (OR-1) | operational readiness |
| 13 | Live-call eligibility and gates G-1…G-8; assigning surveys to real cases | any operational use |
| 14 | Whether the existing SBQ and assignment rules are the approved process (still a working hypothesis) | everything operational |

## 15. Proposed ASG-2B — coordinated simulation: the boundary

**Not authorised. Nothing of it has been started.**

*What ASG-2B would be:* a coordinated **simulation** of the surveys of one composite — a person steps through survey
after survey for one synthetic application and sees one combined record of what was delivered and answered.

*What it can be built from without any new decision:*

* one SS-03B simulation **per selected survey**, each exactly as today, each on its own pinned version, each with its
  own execution identities, evidence and fingerprint;
* a coordinating record that refers to those simulations in the composite's **governed** order.

*Where it must stop until the owner decides — each a named, visible status, never a default:*

| Situation | ASG-2B without a decision |
|---|---|
| a survey ends `COMPLETED` | the next survey may start — **if** the owner confirms that even this is the rule |
| a survey ends with an escalation or any other outcome | `CROSS_SURVEY_POLICY_UNRESOLVED`: the coordinated run stops and says which decision is missing |
| a survey is at `POLICY_UNRESOLVED` (a non-answer) or halts on missing information | the coordinated run stops there, as the single survey does |
| the composite's order is unresolved | no coordinated run can be started |
| two requirements selected the same survey | stops: asked once or twice is undecided |
| consent, opening and closing statements appearing in several surveys | delivered as each survey states; nothing merged or skipped |

*What ASG-2B would not be:* an operational combined call; a merged survey definition; a new executor; a place where
continuation, repetition or consent rules are invented.

*Decisions needed before it:* items 2, 3 and 9 of §14, at least in the form "for simulation, stop at every
non-completed ending".
