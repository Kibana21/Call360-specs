# EVAL-2A — Migration `0034_survey_control_policy`: compatibility and data-preservation report

**Status of the migration: applied to the isolated test schema only. NOT applied to development; not authorised
there.** Development is at `0033_survey_control_evaluation`.

## 1. What was wrong with the first draft, and what replaced it

The first draft of `0034` (reported on 2026-11-22) was not additive. It

* added `obligation varchar(40) NOT NULL DEFAULT ''` to `survey_control_result`, `survey_evidence_observation` and
  `survey_evaluation_finding`;
* dropped the primary key of `survey_control_result` `(evaluation_id, control_code)` and created
  `(evaluation_id, control_code, obligation)`;
* dropped and re-created the two foreign keys that pointed at that primary key;
* added `control_policy_id` to `survey_journey_evaluation`.

It would have preserved every row, but it restructured tables that hold historical evaluation evidence, and its
downgrade had to restore keys. The owner asked for an additive strategy if a safe one exists. One does, and the
draft was withdrawn before it was applied anywhere but the test schema.

**The migration as it is now changes no existing object.**

## 2. Every DDL operation of `0034`

| # | Operation | Object |
|---|---|---|
| 1 | `CREATE TABLE` | `survey_control_policy` |
| 2 | `CREATE TABLE` | `survey_control_policy_event` |
| 3 | `CREATE FUNCTION` | `survey_control_policy_event_guard()` |
| 4 | `CREATE TRIGGER` | `survey_control_policy_event_guard` on the event table |
| 5 | `CREATE INDEX` | `survey_control_policy_event_p` on the event table |
| 6 | `CREATE TABLE` | `survey_evaluation_policy` — evaluation → policy revision |
| 7 | `CREATE TABLE` | `survey_obligation_result` — key `(evaluation_id, control_code, obligation)` |
| 8 | `CREATE TABLE` | `survey_obligation_observation` |
| 9 | `CREATE TABLE` | `survey_obligation_finding` |
| 10 | `CREATE TRIGGER` ×6 | the immutability trigger on each new table |

**Columns changed on existing tables: none. Keys replaced: none. Indexes changed: none. Triggers changed: none.
Permissions added: none.** There is no `ALTER TABLE` in the migration.

Foreign keys of the new tables point at: `survey_journey_evaluation` (from `survey_evaluation_policy`), `control`,
`survey_control_mapping`, `survey_simulation`, `survey_version`, `finding_rule_set_version`, and each other.
Nothing existing points at them.

## 3. How old and new evaluations coexist

| Evaluation | Written to | Read from | Has an obligation key |
|---|---|---|---|
| EVAL-1, or any evaluation that names no policy | `survey_control_result`, `survey_evidence_observation`, `survey_evaluation_finding` — the same SQL as before | the same tables | no |
| made under a control policy | `survey_evaluation_policy`, `survey_obligation_result`, `_observation`, `_finding` | those tables | yes, never empty (`CHECK length(obligation) >= 1`) |

Both have their row in `survey_journey_evaluation`. Which tables an evaluation is read from is decided by its own
pins (`pins.policy` present or not) — recorded at creation, immutable. An old evaluation needs no default, no
backfill and no interpretation: it simply has no policy and no obligation.

## 4. Tests

`tests/test_survey_control_policy.py::test_zz_migration_0034_is_additive_over_a_database_populated_by_eval1`, on the
isolated PostgreSQL test schema. The schema is first taken to `0033` and populated **by the EVAL-1 server** (the
application with evaluation on and control policies off) through real HTTP: a published survey, two governed
mappings (six lifecycle events), a published finding rule set, two simulations, two evaluations — 10 control results,
6 evidence observations, 2 findings.

A digest is taken of the six EVAL-1 tables: every row exactly as stored, every column (name, type, nullability),
every constraint with its definition, every index with its definition, every trigger.

| Owner's point | What the test does | Result |
|---|---|---|
| 1. Inspect every DDL operation | §2 above; the test asserts the set of tables after the upgrade is the previous set plus exactly the six new ones | pass |
| 2. Upgrade a database populated with EVAL-1 records | upgrade `0033` → `0034` over that data | pass |
| 3. Record identities and associations survive | the digest of all six tables (rows, keys, foreign keys) is identical after the upgrade | pass |
| 4. Stored results, fingerprints, lineage and historical reads stay valid | each evaluation read through the API returns the same `id`, `result_sha256`, `input_sha256`, `pins`, controls, findings, coverage, summary, journey and status as when recorded; `replay.consistent` is true (it recomputes to its record) | pass — on the EVAL-1 server and on the server with policies on |
| 5. Foreign keys, indexes, audit entries, API contracts | constraints, indexes and triggers are in the digest; the audit event count and last sequence are unchanged by the migration and the audit chain verifies; the OpenAPI change is additive (§6) | pass |
| 6. Migration failure and transactional recovery | a table with the name of the migration's LAST table is created first, so the migration fails at its last step. PostgreSQL rolls the whole revision back: the revision is still `0033`, none of the other five tables and no guard function exist, the EVAL-1 digest is identical, and the evaluations read the same. The blocker is removed and the upgrade then succeeds | pass |
| 7. Downgrade on empty and populated schemas | empty `0034` (no policy, no policy-scoped evaluation): down to `0033` and up again, the EVAL-1 digest identical each time. Populated: see 8 | pass |
| 8. No destructive downgrade of immutable evidence | with a published policy and an evaluation made under it, the downgrade raises "governed control policies exist"; the revision stays `0034`; everything is still there and reads the same. The second guard — "evaluations recorded under a control policy exist" — covers a policy-scoped evaluation should its policy check ever be bypassed | pass |
| 9. Old EVAL-1 records with no obligation key | after the upgrade they read with no `obligation` on any control, `control_policy_id` null and coverage in the EVAL-1 form; evaluating the same journey again without a policy returns the same evaluation (200, same id) | pass |
| 10. Which columns and keys changed | none (§2) | — |

After a policy-scoped evaluation is made, the three EVAL-1 result tables hold exactly the rows they held before:
a policy-scoped evaluation writes nothing into them.

Also covered elsewhere: an empty-schema round trip of the whole chain (`test_survey_store.py`), `0033` down and up
with `0034` above it (`test_survey_evaluation.py`), the `0033` guards for a mapping and for a recorded evaluation,
and evaluation with control policies switched off on a `0034` schema (it writes only the EVAL-1 tables).

## 5. What applying it to development would do

Not done and not authorised. If authorised: six empty tables, one function and seven triggers would be added; the
two mappings, two evaluations and all other development data would be untouched; control policies would stay off
until `SURVEY_CONTROL_POLICY_ENABLED` is set. A downgrade would be possible until the first policy is proposed.

## 6. API compatibility

The contract change is additive: 10 new operations; new optional request field `control_policy_id`; new response
fields `control_policy_id`, `policy`, `applicability`, `operational_compliance_eligibility` on an evaluation and
`policy`, `coverage_status` on a list entry. No operation, field or schema was removed or changed in type.
