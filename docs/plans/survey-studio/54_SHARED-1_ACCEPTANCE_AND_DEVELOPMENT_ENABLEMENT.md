# SHARED-1 — acceptance, reconciliation and development enablement (migration 0037)

**Status: SHARED-1 ACCEPTED by the owner as TECHNICALLY VERIFIED, 2026-11-23. Development enabled the same day on
the owner's authorisation. This record awaits the owner's review.** Synthetic data only. Uncommitted; nothing staged,
committed or pushed by the assistant.

Authorisation: the owner's message of 2026-11-23, "Accept SHARED-1, Enable Development 0037 and Prepare APP-1 /
OPS-1". Companions: `52_…` (design), `53_…` (implementation report), `55_…` (APP-1 / OPS-1 assessment), contract
`04_…` §23, decisions D-370…D-378. Evidence: `docs/acceptance/evidence/SHARED-1/dev-migration-0037/`.

---

## 1. Acceptance

SHARED-1 is accepted as technically verified for independently governed Assignment Rules and Finding Rules and for
script-independent survey selection (D-370). The eight points the owner asked to be confirmed, each with where it is
shown:

| # | Confirmed | Shown by |
|---|---|---|
| 1 | Assignment rules own their market | all eight development rules: own market = script family's market; database refuses a change (§4, §6 step 9) |
| 2 | Survey-only rules need no published script | two created on development; script families 7 and script versions 11 before and after |
| 3 | Existing script-backed identities, versions and targets intact | 30 record sets identical across the migration; every checksum identical |
| 4 | Survey-only rules never eligible for operational script assignment | the operational loader's rule list identical before and after; the decision for each of 258 cases identical; the database refuses |
| 5 | The existing assignment and finding engines remain authoritative | `rule_engine.py`, `answer_evaluation.py`, `finding_engine.py` not edited; 82 golden runs and 14 plans unchanged |
| 6 | Finding Rules have independent permissions; semantics unchanged | version 2 published on development by dedicated identities with a fingerprint identical to version 1 |
| 7 | Legacy permissions keep working | no role lost a `script.*` permission; `dev.user`, `dev.checker` and `dev.admin` signed in on development and opened Script Studio, Assignment Rules and Finding Rules (§6) |
| 8 | Historical operational and review records unchanged | assignments, cases, sessions, runs, findings, review decisions and approvals identical before and after the demonstration |

Script Studio and the Simulation Workbench remain in the navigation and were not changed.

## 2. D-367 reconciled, choice by choice

None of the ten is a business-policy change; none is treated as approved policy. Each is recorded as a technical
design choice that stands unless the owner revises it.

| | Choice | In the implementation | Against the owner's decisions | Status |
|---|---|---|---|---|
| a | A rule's kind is fixed at creation; versions and copies keep it | draft-kind guard; published versions immutable. On development, changing the kind was refused by the database | consistent with "only in an explicitly supported survey-assignment context" | **Stands (technical)** |
| b | A survey-only draft is conflict-checked against every live rule of its market; a script-backed draft against script-backed rules only | `rule_authoring.analyse` | the owner asked for an assessment and **no change** | **Unchanged; assessed in §3** |
| c | The simulation over cases stays on `script.read` and refuses a survey-only draft | 403 for the dedicated identities on development | consistent with confirmation 4 | **Stands (technical)** |
| d | `script.assign` unchanged; no separate execution permission | unchanged | operational assignment is out of scope; raised again in `55_…` §6 | **Stands; revisit in OPS-1** |
| e | A script-backed rule written without a market takes its script family's | database trigger | the owner's rule for existing rules ("from the authoritative script family"); never applies to a survey-only rule | **Stands (technical)** |
| f | The registry reports each rule's own market | `RuleSummary.market` | a correction of display; no rule's market changed | **Stands (technical)** |
| g | The route inventory reports the legacy permission as "required" and lists both as accepted | `require_any` | transitional by the owner's instruction ("legacy permission compatibility during transition") | **Stands until legacy removal is decided** |
| h | Setting `shared_rule_services_enabled`, independent of the survey settings | `settings.py` | **now on in development** by this authorisation | **Stands** |
| i | Four browser-test identities holding only dedicated permissions, in the test setup | `scripts/e2e_survey_setup.py` | test schema only. Development now has its own four (§5) | **Stands** |
| j | The Assignment Rules and Finding Rules screens were changed; Script Studio's library and editor were not | frontend | within the SHARED-1 authorisation | **Stands** |

### Governance — recorded as it is, not changed

| Capability | Lifecycle | People | Enforced by |
|---|---|---|---|
| Assignment Rules | draft → submitted → approved → published | **two**: an author, and a different checker who may also publish | the service; the published row records both people |
| Finding Rules | draft → submitted → approved → published | **two**: an author, and a different checker who may also publish | service |
| Survey bindings and requirement groups | proposed → approved → published | **three**: proposer, approver, publisher, all different | the service (self-approval and publication by the approver refused; shown in §6 step 4) |
| Survey Studio content (surveys, modules, library components) | draft → candidate → approved → published | **three** | the service and database guards of SS-03A |

The owner retains each as it is. A survey journey therefore rests on decisions made under two different regimes: the
rule (two people) and its binding and group (three). Harmonising them is a separate future decision (D-372) and is
listed for Business in `55_…` (Q-15).

### Outstanding gaps retained

| Gap | State |
|---|---|
| **DEP-FR-1** | a finding rule of scope QUESTION names a script question code and does not reach a survey item. On development 2 of 6 rules are question-scoped. Not solved; no identity invented |
| No operational case-to-survey assignment | unchanged; assessed in `55_…` |
| Legacy permission compatibility | every rule operation still accepts `script.*`; removal not done and not scheduled |
| Control Registry maintenance | the control register still has no maintenance of its own |
| OR-2 / OR-3 | the rule-expression and conflict limitations are untouched and open |

## 3. Assessment: do cross-kind conflict checks block survey-only rules unnecessarily?

**The overlap semantics were not altered.** What follows is an assessment of the behaviour as built, with a probe on
development through the stateless explain operation (nothing saved;
`evidence/…/cross_kind_conflict_probe.txt`).

**What blocks.** Of the four conflict kinds, only a tie blocks submission: two rules that can match the same case,
live at the same time, with **equal priority and equal specificity** (`AMBIGUOUS`, or `SAME_TARGET_TIE`). Every
other overlap is information, and a fully shadowed rule is a warning. A survey-only rule and a script-backed rule
never share a target, so a cross-kind tie is always `AMBIGUOUS`.

Observed, against `S2D1-LIFECYCLE-DEMO v1` — script-backed, priority 3, specificity 4, with **no** published survey
binding and in **no** requirement group:

| Survey-only draft | Result |
|---|---|
| same conditions, same priority 3 | **blocked**: `CONFLICT_AMBIGUOUS` |
| same conditions, priority 2 or 5 | not blocked (shadow warning) |
| one more condition, priority 3 | not blocked (overlap, information) |

**Is that block necessary?** It depends on which selection is meant.

| Selection | Does the unbound script-backed rule take part? | Is the block necessary? |
|---|---|---|
| Single-survey selection (ASG-1) | **Yes.** Every published rule takes part with full precedence whether or not it has a binding; an unbound winner fails closed (`BE/app/domain/survey/assignment.py:11, 328-341, 370-378`) | **Yes.** The tie would be a real `AMBIGUOUS` outcome at selection. The check reports it early |
| Grouped selection (ASG-2A, composite plans) | **No.** The engine runs once per group over that group's member rules (`assignment_groups.py:352`) | **No.** A tie with a rule outside the group can never occur at selection, yet authoring blocks it |

**Findings**

* **CK-1 — stricter than grouped selection needs.** For journeys built from requirement groups, the cross-kind check
  blocks a tie that could never happen. The cost is small and always avoidable: change the priority by one, or add a
  condition. But it couples two authoring populations through one priority number space: a survey rule author can be
  blocked by a script rule they cannot read (the dedicated identity cannot open Script Studio).
* **CK-2 — an asymmetry in the other direction.** A script-backed draft is checked against script-backed rules only,
  as before SHARED-1. A script-backed rule can therefore be published at equal rank with a live survey-only rule
  without any authoring warning. In single-survey selection that tie surfaces only at selection, where it fails
  closed as `AMBIGUOUS`. Nothing unsafe follows — the engine never chooses — but the author is not told.
* **CK-3 — unbound rules still compete in single-survey selection.** A script-backed rule that nobody has bound to a
  survey can win and make single-survey selection fail closed. That is the accepted ASG-1 behaviour, not something
  SHARED-1 introduced; it is the root of both findings above.

**Options, for the owner — none applied:**

| | Option | Effect |
|---|---|---|
| 1 | Leave as built | safe; occasionally asks for a different priority |
| 2 | Check a survey-only draft only against rules that have a published binding or belong to a group | removes CK-1; changes when a conflict is reported |
| 3 | Check conflicts per requirement group | matches grouped selection exactly; single-survey selection would need its own rule |
| 4 | Also warn a script-backed draft about a tie with a survey-only rule | closes CK-2; adds a warning to Script Studio's rule authoring |
| 5 | Exclude unbound rules from single-survey selection | removes CK-3; **changes ASG-1 selection semantics** |

Options 2, 3 and 5 change overlap semantics and belong with OR-2 / OR-3.

## 4. Development migration 0037

Evidence: `evidence/SHARED-1/dev-migration-0037/migration_before_after.txt`.

| Precondition | Result |
|---|---|
| Database identity | `Call360_db` on localhost:5432, schema `call360`, `APP_ENV=local`, PostgreSQL 15.12 |
| Revision before | `0036_survey_module_authoring` |
| Only intended revision | `0037_shared_rule_services` is the single revision after `0036` and the head |
| Inventory | 140 tables, 16,202 rows; 8 rule versions, 3 publications, 19 change events, 4 drafts; 7 script families, 11 script versions; 251 script assignments; 258 cases; 95 sessions; 82 survey runs; 26 findings; 5 review decisions, 1 review approval; 3 survey bindings, 2 requirement groups; 1 finding rule set |
| Backup | `_db_backups/call360_dev_before_0037_20261123.dump`, taken with the API server stopped; SHA-256 `2d90aa7d0cfe819585c529f25f88081eebdd694cd5bbf75d3b5cbe590d47861c`; every table's row count equals the inventory |
| Recovery procedure | the archive writes out completely as SQL without error; `_db_backups/RESTORE.md` has the 0037 section. Not restored into a database |

Applied as one revision in one transaction: `uv run alembic upgrade 0037_shared_rule_services`.

| # | Verification | Result |
|---|---|---|
| 1 | Every rule keeps identity and version | 8 of 8; the digest of every pre-existing column is identical |
| 2 | Markets back-filled from the script family | SG × 7, MY × 1 |
| 3 | All market values verified | own market = script family's market for all 8 (also verified inside the migration before it could commit) |
| 4 | Published rule checksums unchanged | 8 of 8 |
| 5 | Script targets intact | 8 of 8; script families and versions identical |
| 6 | Assignments and sessions unchanged | 251 assignments, 95 sessions, 82 runs, 258 cases: identical digests |
| 7 | Survey bindings and requirement groups unchanged | identical digests |
| 8 | A survey-only rule cannot assign a script to a case | §6, step 9 |
| 9 | Rule history and publications readable | history of `SG-SALES-VERIFY` read through the API; publications and change events identical |
| 10 | Downgrade guards and recovery | below |

Whole-schema comparison: 136 of 140 tables byte-identical. The four that differ are the revision marker, the two
tables that gained a column, and `permission` (45 → 53). Six triggers and five functions added; none removed.

**Recovery, exercised on development:**

* *Empty round trip before any new content* — `0037` → `0036` → `0037`. After the downgrade every table, trigger,
  function, permission and column was identical to the inventory taken before the migration. After the second
  upgrade everything was identical to the first.
* *Downgrade guard after the demonstration* — refused: "survey-only assignment rules exist; they cannot be expressed
  without the columns". The revision stayed `0037`; all 30 record sets identical before and after the attempt.

`SHARED_RULE_SERVICES_ENABLED=true` was added to the gitignored `.env`; the server reports ready and offers
survey-only rules. Development was not reset or re-seeded.

## 5. Dedicated development permissions

Evidence: `evidence/…/permission_grants.txt`.

**Inspected first.** Six identities existed, all scoped to SG: `dev.admin` (ADMIN, DEV_SURVEY_AUTHOR), `dev.user`
(USER), `dev.checker` (SC_CHECKER), `dev.survey.author`, `dev.survey.checker`, `dev.survey.publisher`. None was
suitable: ADMIN, USER and SC_CHECKER are the standing role shapes the owner excluded, and granting the survey
identities would make a survey author a rule author. Nobody held a dedicated permission.

**Created** by `scripts/dev_rule_identities.py --confirm-development` (new; refuses anywhere but local development;
audited), four identities in market SG, each through its own development-only role and group:

| Identity | Role | Holds exactly |
|---|---|---|
| `dev.rule.author` | `DEV_RULE_AUTHOR` | `assignment_rule.read`, `assignment_rule.edit` |
| `dev.rule.checker` | `DEV_RULE_CHECKER` | `assignment_rule.read`, `assignment_rule.approve`, `assignment_rule.publish` |
| `dev.finding.author` | `DEV_FINDING_AUTHOR` | `finding_rule.read`, `finding_rule.edit` |
| `dev.finding.checker` | `DEV_FINDING_CHECKER` | `finding_rule.read`, `finding_rule.approve`, `finding_rule.publish` |

Ten grants in total. The checker also publishes, as the retained two-person lifecycle has it. No existing role gained
a dedicated permission; no legacy permission was removed. Passwords are in the gitignored
`Call360-backend/.secrets/dev_survey_accounts.json` only. Undo: the same script with `--remove`.

## 6. Development acceptance demonstration

Evidence: `evidence/…/demonstration_thirteen_steps.txt` and eight screenshots in `evidence/…/screens/`. Through the
real API with the dedicated identities; database probes ran in transactions that were always rolled back.

| # | Step | Result |
|---|---|---|
| 1 | Create a survey-only rule without a script | `DEV-S1-PRIMARY` and `DEV-S1-EXTRA`: kind `SURVEY_BINDING`, no target, market SG |
| 2 | Save and validate | saved; no blocking issue; giving one a script refused (`TARGET_NOT_ALLOWED`) |
| 3 | Review and publish under the existing governance | the author's own review and publication refused (403); approved and published by `dev.rule.checker` |
| 4 | Bind to a published survey | → `S-DEV-LIB2-ONE 1.0` and `S-DEV-LIB2-TWO 1.0`, each by three people; proposer's own approval and approver's own publication refused |
| 5 | Add to a governed requirement group | `DEV-PRIMARY` version 2 (adds `DEV-S1-PRIMARY`); new `DEV-S1-EXTRA-GROUP` |
| 6 | Select several surveys for a synthetic application | ILP, direct, annual, low risk: both surveys selected, each by a survey-only rule |
| 7 | Composite call plan | selection RESOLVED, ordering GOVERNED, plan READY, no issue |
| 8 | Coordinated simulation | started; the two surveys in governed order |
| 9 | Operational script assignment ignores the survey-only rules | the operational loader returns the same rules as before; the decision for each of 258 cases is identical (outcome, winning rule, script, both fingerprints); the database refuses a script assignment matched by one, and refuses to give one a script, change its market or its kind |
| 10 | Script-backed rules continue to work | three live script-backed rules with their targets; 258 cases still decided by them (136 / 64 / 3 / 55 by rule) |
| 11 | Finding Rules governed with dedicated permissions | version 2 drafted and submitted by `dev.finding.author`, own review refused, approved and published by `dev.finding.checker`; **rules and fingerprint identical to version 1** |
| 12 | Denied access | each dedicated identity opens only its own capability (403 on the other, on scripts, surveys and cases); a survey author gets 403 on both rule capabilities; an SG identity cannot see the MY rule, cannot create a rule in MY (`MARKET_NOT_IN_SCOPE`), cannot bind it; the database refuses a cross-market binding |
| 13 | Script Studio history and operational data unchanged | script families, script versions, assignments, cases, sessions, runs, findings, review records, contact attempts identical; every earlier rule identical |

**What the demonstration left in development** (all named as synthetic):

* Rules `DEV-S1-PRIMARY v1`, `DEV-S1-EXTRA v1`; two bindings; `DEV-PRIMARY` version 2; `DEV-S1-EXTRA-GROUP`; one
  composite plan, one evaluation, one coordinated simulation; finding rule set version 2 (identical rules).
* One behavioural consequence: a synthetic application that is ILP, sold direct, paid yearly and low risk now gets
  `S-DEV-LIB2-ONE` as its primary survey where it used to get `DEV-CHECK-…` through `SG-SALES-VERIFY`. Recorded
  plans are not rewritten. The protected binding `SG-ILP-HIGH-RISK v2` → `S-DEV-EVAL-SHARED` is untouched.
* These records make a downgrade to `0036` refuse, by design.

**Limitations, stated plainly**

* **Legacy sign-in on development** was first shown only indirectly, because the assistant did not hold those
  passwords. The owner then supplied them for this check (used once, not stored, not printed). Signed in as
  `dev.user`, `dev.checker` and `dev.admin`: each opens Script Studio, Assignment Rules and Finding Rules (200); the
  script-side rule list holds the seven script-backed rule versions and no survey-only rule; the simulation of the
  live rules over cases returns 203 cases, all SELECTED, 0 changed, and names no survey-only rule; three case
  previews name none; a legacy checker and the admin cannot create a rule (403); legacy identities still cannot open
  Survey Studio (403).
* **No identity of another market exists in development.** Cross-market denial was shown from the SG side and at the
  database. An identity scoped to MY is exercised in the test schema's browser journeys.
* The demonstration was run through the API; the screenshots show the resulting screens. The create-in-the-browser
  journey is the one in the persisted suite.

## 7. Regression

Run on 2026-11-23 against the isolated test schema, after the last change of this checkpoint (the two backend
scripts). Outputs: `evidence/SHARED-1/dev-migration-0037/regression-*.txt`.

| Check | Result |
|---|---|
| Backend suite | **1,024 passed, 0 failed** |
| Golden fixtures | the 82 expected runs and 14 expected plans pass inside that suite; no fixture or expectation file is modified |
| Backend lint, format, types | clean (`ruff` on 262 files, `mypy` on 127) |
| OpenAPI | matches the committed contract, SHA-256 `2f98a3f9…6074a4a8`; unchanged by this checkpoint; the frontend client matches |
| Frontend unit tests | **630 passed** |
| Frontend types, lint, build | clean |
| Playwright — persisted | **34 passed** |
| Playwright — prototype | **13 passed** |
| Playwright — standard | **33 passed** |
| Specs validator | passes |
| Development after enablement | server ready; the operational decision for each of 258 cases identical before and after |

## 8. State

| | |
|---|---|
| Development database | `0037_shared_rule_services` (head); `SHARED_RULE_SERVICES_ENABLED=true`; ten development identities |
| Code changed in this checkpoint | backend `scripts/dev_rule_identities.py` (new) and an optional audit-reason argument in `scripts/dev_survey_identities.py`. No application, schema, engine or frontend change |
| Repositories | uncommitted; nothing staged, committed or pushed by the assistant |
| Not started | MIG-2, Script Studio retirement, operational survey assignment, voice, Genesys |

## 9. Stopped here for review

Open with the owner: the cross-kind options of §3; governance harmonisation (D-372); and the proposed next boundary,
APP-1a, in `55_…` §13. Nothing is authorised next.
