# SS-03A — Technical acceptance and development enablement

**Owner decision, 2026-11-22 ("SS-03A Technical Acceptance and Development Enablement"), register D-188…D-194.**
SS-03A is **accepted as TECHNICALLY VERIFIED**, subject to reconciling the fixture-regeneration discrepancy (§1).
Local commits and conditional development-environment enablement were approved.
**Status of this document: work done and verified, presented for the owner's review.**
**Prepared:** 2026-11-22.

**Not claimed.** Not production readiness; not business-user UX acceptance; not screen-reader sign-off; not approval
of any wording, catalog entry, non-answer behaviour or live-call eligibility. No survey is eligible for a live call.

**Scope held.** FI-1 was not implemented. SS-03B was not started. No non-answer behaviour or live-call eligibility
was implemented. Script Studio was not modified or removed. Nothing was pushed by me. The development database was
not re-seeded, truncated, renamed or dropped.

---

## 1. Fixture-regeneration discrepancy — reconciled

**The line.** `evidence/SS-03A/fixture_regeneration.txt` ended "fixtures changed in git: 1", while the report said
the fixtures were unchanged.

**The exact entry.** It was `docs/plans/survey-studio/fixtures/__pycache__/` — an **untracked Python cache folder**,
not a fixture. The line counted `git status` entries under the fixtures folder. Reference interpreters v2–v4 import
`reference_interpreter.py`, so Python wrote its bytecode cache beside them during that very run. It held three
`.pyc` files, was never tracked, and I deleted it minutes later, before the report was finished.

**My error.** The wording of the measurement, and not explaining it in the evidence file. No golden expectation was
changed, then or now.

| Check against the accepted baseline | Result |
|---|---|
| Fixture folder, accepted UC-02 baseline `33fdfce` → current HEAD | 0 files differ |
| F, G, H and J fixtures, SS-02 closure baseline `786a7c0` → current HEAD | 0 files differ |
| Working tree against HEAD | 0 entries |
| Fixture files per schema /1…/5 | 8 · 6 · 4 · 1 · 8 = **27** |
| Expected runs per schema /1…/5 | 25 · 18 · 16 · 4 · 19 = **82**; 14 expected plans |
| Regenerated again from the five interpreters, bytecode caching off | 27 of 27 byte-identical; folder clean afterwards |

All 27 fixtures and 82 expected runs retain their accepted meaning. The original evidence line is kept and
annotated; the full reconciliation is `evidence/SS-03A/fixture_reconciliation.txt`.

### Technical debt recorded

| ID | Item | Detail |
|---|---|---|
| TD-SS03A-1 | Pre-existing SQLAlchemy transaction warning | `SAWarning: transaction already deassociated from connection` at `tests/conftest.py:87` (`conn` fixture, last changed 2026-11-17), raised in 7 existing tests: two in `test_assignment_rules`, one each in `test_recording`, `test_script_authoring`, `test_transcript`, two in `test_script_draft_isolation`. The fixture rolls back a transaction the test already ended. No SS-03A test raises it. Tests pass; the warning hides nothing known, but it would mask a real one. Not fixed: outside SS-03A's scope |
| TD-SS03A-2 | Evidence wording | A count of `git status` entries was labelled "fixtures changed". Evidence lines must name what they count |

---

## 2. Commits

**The SS-03A work was already committed and pushed when this review began — not by me.** All three repositories
received a commit at 00:33 on 2026-11-22, message "commit", same author identity as the owner's earlier commits, no
co-author trailer; each remote-tracking reference records "update by push", and `git ls-remote` shows `origin/main`
at exactly those commits. As with the UC-01/UC-02 commits, git cannot show what triggered the push. They also carried
my two earlier local commits (`a867767`, `b2f81df`) to the remote. **Nothing was rewritten, reverted or
force-pushed.**

| Repository | SS-03A commit (on `origin/main`) | Contents verified |
|---|---|---|
| Call360-backend | `a607ff5` | 23 files: the SS-03A domain, store, API, migration 0027, five test files, regenerated OpenAPI, the six small changes to existing files |
| Call360-frontend | `abb7726` | 3 files: generated client only |
| Call360-specs | `3ff4df7` | 12 files: report 27, contract §9, index, handoff, six evidence files — and `docs/acceptance/evidence/.DS_Store` (a Finder file that was already tracked; binary change, no content of ours) |

No secret, environment file or temporary artefact is in any of them.

**Local commits made by me in this checkpoint** are listed in the completion message with their hashes: they hold
only what this checkpoint added (backend: the development-identity script; specs: this report, the reconciliation,
the enablement evidence, the register and handoff). Not pushed by me.

---

## 3. Development database migration

All ten preconditions passed; the migration was applied.

| # | Precondition | Result |
|--:|---|---|
| 1 | Actual Alembic revision | `0026_gpt_live_provider` (test schema: `0027_survey_definitions`) |
| 2 | Inventory | 102 tables, 14,574 rows, each table's row count and content digest recorded (`01_inventory_before.txt`). Protected synthetic records include 258 callback cases, 237 policies, 11 script versions in 7 families, 24 Voice Lab sessions, 2,984 audit events |
| 3 | Intended database | Database `Call360_db`, schema `call360`, role `Call360_db_user`, `localhost:5432`, `APP_ENV=local`. Not `call360_test`. There is no production database |
| 4 | Verified backup | `pg_dump` of schema `call360`, 1,778,391 bytes, SHA-256 `d75e6fb1…c28029f`. Every table's row count in the archive equals the inventory (102 of 102; 14,574 rows). Restore instructions beside it |
| 5 | Additive | The migration creates 9 tables, 4 functions and 9 triggers and inserts 4 rows into `permission` and 16 catalog rows. It alters, updates or drops nothing existing |
| 6 | Applied 0027 only | `alembic upgrade 0027_survey_definitions` (explicit target), with the API server stopped |
| 7 | New objects | Revision `0027_survey_definitions`; 9 new tables; 4 permissions; catalogs 8 fields (0 speakable), 6 outcomes (0 non-answer), 2 obligations, all `SYNTHETIC_UNAPPROVED`; no role held a survey permission; 0 foreign keys between the new tables and any other |
| 8 | Existing tables intact | 0 removed. **100 of 102 byte-identical in content**; the two that differ are `alembic_version` (the revision) and `permission` (37 → 41 rows). Column definitions of every pre-existing table identical. Script Studio and related tables: 22 of 22 identical |
| 9 | Readiness, setting off and on | Off: live 200, ready 200, survey route 404, 0 survey paths. On: live 200, ready 200, survey route 401 without a session, 15 operations present |
| 10 | Before/after and anomalies | Below |

**The backup was verified by reading it, not by restoring it.** The archive's data was written out and counted
table by table. It was not restored into a database, because that needs a second database or schema and was not
asked for.

**Backup location.** `<workspace>/_db_backups/` — the parent folder, outside all three repositories, mode 700. It is
synthetic data but contains credential hashes and encrypted fields, so it must stay out of the repositories. It is
not backed up anywhere else.

**Rollback.** `alembic downgrade 0026_gpt_live_provider` now **refuses**, by design, because a survey definition
exists (§4). Full restore steps are in `_db_backups/RESTORE.md`.

**Anomalies.** None in the migration. Two things done to make it clean, both reported: the development API server
was stopped for the inventory, backup and migration and restarted afterwards; and two temporary servers ran on ports
8011 and 8012 for the readiness check and were stopped.

---

## 4. Development permissions

**Setting.** `SURVEY_DEFINITIONS_ENABLED=true` was added to the gitignored development `.env` only. The test
configuration and the code default remain off.

**Identities.** Three new synthetic people, each in its own development-only role and group, scoped to SG:

| Username | Role (new, development only) | Permissions |
|---|---|---|
| `dev.survey.author` | `DEV_SURVEY_AUTHOR` | `survey.read`, `survey.edit` |
| `dev.survey.checker` | `DEV_SURVEY_CHECKER` | `survey.read`, `survey.approve` |
| `dev.survey.publisher` | `DEV_SURVEY_PUBLISHER` | `survey.read`, `survey.publish` |

- Created by `Call360-backend/scripts/dev_survey_identities.py`, which refuses anywhere but `APP_ENV=local` on schema
  `call360`, needs an explicit flag, is idempotent, writes audit events and has a `--remove` mode.
- **No migration grants anything, and no existing role was touched:** ADMIN 23, SC_CHECKER 13 and USER 18
  permissions before and after, none of them a survey permission.
- Passwords were generated by the script and written only to the gitignored `.secrets/dev_survey_accounts.json`.
  They were never printed and are in no repository, document or log.

**Checks, on the development database through the real server** (`05_permission_checks.txt`; 27 pass, 0 fail):

| Requirement | Evidence |
|---|---|
| An unauthorised user cannot access the survey APIs | No session: 401. Checker editing a draft, publisher creating a survey, author approving, author publishing, publisher approving, checker publishing: each 403 `FORBIDDEN` |
| Self-approval refused | Service: `SELF_REVIEW_DENIED`. Database: an `APPROVED` event inserted in the author's name is refused by the trigger |
| Self-publication refused | Service: `SELF_PUBLISH_DENIED`. Database: refused by the trigger |
| Approver-publication refused | Service: `APPROVER_PUBLISH_DENIED`. Database: refused by the trigger |
| The legitimate path works | Author submits, checker approves, a third person publishes version 1.0 |
| Stale revision | 409 `STALE_DRAFT`; draft unchanged |
| Audit chain | Verifies |

**Why the identity rules were checked at the service and the database, not over HTTP.** With least-privilege roles
the author has no approve or publish permission, so over HTTP the permission check refuses first (403). The identity
rules only become reachable when one person holds several permissions — which these identities deliberately do not.
They were therefore exercised by calling the service as that person and by inserting the event directly, both
rolled back. Over HTTP with every permission held, they are covered by the test suite on the test database.

**A check I got wrong first.** My first database-level attempt named a column that does not exist, so its three
"refusals" proved nothing. I repeated them correctly, with a positive control showing a legal event is accepted.
The evidence file says so.

**What these checks left in the development database** (all synthetic, all labelled):

| Left behind | Detail |
|---|---|
| One survey definition | `DEV-CHECK-AD5AEA8F`, "Development enablement check (synthetic)", built from fixture K7 |
| Candidates | Candidate 1 published as version 1.0; candidate 2 approved then withdrawn (used for the database checks) |
| Rows | 9 frozen assets, 7 lifecycle events, 6 wording-approval rows, 27 usage rows |
| Identity and audit rows | 3 principals, roles, groups and their mappings; 6 grants; 5 sessions; 37 audit events |

Frozen candidates, versions and events cannot be deleted, by design. So this survey stays, and it is the reason the
downgrade now refuses.

**Whole development schema, before migration → after enablement:** 0 pre-existing tables removed; 86 of 102
identical in content; the 16 that changed gained rows only (identity, session, login, audit, permission tables);
63 of 63 Script Studio, Voice Lab, case, policy, evidence and review tables identical.

**A consequence for FI-1.** These three people hold nothing but survey permissions. They cannot open the rest of the
portal, and today's Survey Studio prototype sits behind `script.read`. FI-1 must decide how its screens are reached
by them — without widening these roles by default (§5, FI-D-1).

---

## 5. FI-1 — proposed next implementation checkpoint

**Not authorised. Not started.**

**Goal.** The existing Survey Studio frontend reads and writes real, persisted survey definitions through the
SS-03A API, in place of its in-memory sample store, for the authoring journey only.

### In scope

| # | Item |
|--:|---|
| 1 | Survey list and open, from `GET /survey-definitions` and `/draft` |
| 2 | Create a survey |
| 3 | **Save:** edits made in the Lego Composer, Guided Builder and Graph are written as draft operations (`PUT_ASSET`, `REMOVE_ASSET`, `SET_CONTENT`) with `expected_revision` |
| 4 | **Reload:** closing and reopening the browser shows the saved draft |
| 5 | **Optimistic concurrency:** on `STALE_DRAFT` the user's unsaved changes are kept, the newer server draft is shown beside them, and the user chooses; nothing is overwritten silently |
| 6 | **Server validation is authoritative:** Validate shows the server's findings by code and location; the browser's own checks become immediate hints and can never make a draft submittable |
| 7 | One mapping, in one module, between the prototype's `Workspace` and the six canonical documents, proven by round-trip tests on all 27 fixtures |
| 8 | Save, loading, empty, error, unauthorised and conflict states; keyboard and screen-reader behaviour preserved |
| 9 | Synthetic surveys and data only |

### Preserved unchanged

The accepted Lego Composer, Guided Builder and Graph — layout, interaction and visual baseline. The canonical
document model and its hashes. The 27 fixtures. The simulator and call plan, which keep running in the browser on
the loaded draft, labelled as a prototype evaluation.

### Out of scope

| Excluded | Belongs to |
|---|---|
| Submit, review, approve, withdraw, publish on real candidates | FI-2 (proposed) |
| Server execution, simulation or call-plan assembly | SS-03B |
| Any non-answer, refusal, repeat, consent or timeout behaviour; live-call eligibility | Business and Compliance rulings |
| Assignment of surveys to cases; voice; telephony | Later stages |
| Any change to Script Studio; any data migration from it | A separate, destructive-change checkpoint |
| A second authoring model, store or editor | Never |
| New server operations | Only if FI-D-2 is ruled that way, as a named backend change |

### Decisions needed before FI-1 can start

| ID | Decision | Recommendation |
|---|---|---|
| FI-D-1 | How the three development identities reach Survey Studio, given the prototype route requires `script.read` and they hold only survey permissions | Gate the Survey Studio route and navigation entry on `survey.read` when the persisted mode is on. Do not add `script.read` to the survey roles |
| FI-D-2 | Whether the editor keeps composing whole documents (as the API expects today) or the server gains fine-grained operations | Keep document-level operations for FI-1: no backend change, and the mapping stays in one place. Revisit only if measured save sizes or conflicts make it necessary |
| FI-D-3 | When a save happens | Explicit Save plus a visible "unsaved changes" state. No silent autosave in FI-1: each save is an audited revision |
| FI-D-4 | The build setting | Keep `VITE_SURVEY_STUDIO_PROTOTYPE` off by default; add a separate setting for the persisted mode so the accepted in-memory prototype and its 13 journeys remain runnable unchanged |
| FI-D-5 | Browser storage for unsaved work | None (lint rule IAM-008 stands). Unsaved changes live in memory and are protected by a leave-page warning |

### Acceptance tests proposed

1. Create, edit in each of the three views, save, reload: the draft is identical, document for document, hash for hash.
2. Two sessions edit the same draft: the second save gets `STALE_DRAFT`; neither user's work is lost; the resolved save succeeds.
3. A draft with a blocker shows the server's code and location, and cannot be marked ready by anything in the browser.
4. All 27 fixtures round-trip Workspace → documents → Workspace without loss.
5. A person without `survey.edit` can read and cannot save; a person outside the market sees nothing.
6. With both settings off, the product is exactly as today: 33 of 33 standard Playwright tests, and the 13 prototype journeys with the prototype setting on.
7. No frontend code decides a validation outcome that the server contradicts.

### Risks

- The prototype model and the canonical documents were designed together but have only been mapped inside the
  backend tests. The mapping (item 7) is the real work and the main risk.
- Document-level saves send whole documents. Fine at the fixtures' size; unmeasured beyond it.
- Server validation has blockers only; the prototype's warnings and information items have no server counterpart
  yet, so FI-1 shows two sources and must label them.
