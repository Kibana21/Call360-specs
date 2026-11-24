# 71 — APPL-X4a acceptance and development enablement

**Date:** 2026-11-24. **Data:** synthetic only. **Simulation only.** **Nothing committed or pushed.**
**Authorisation:** the owner's "APPL-X4a acceptance and development enablement" (2026-11-24): APPL-X4a accepted on
the test schema; controlled enablement of `0040_applicability_scenarios` on local development. APPL-X4b is **not**
authorised for implementation.

---

## 1. Acceptance record

**APPL-X4a IS ACCEPTED as technically verified on the isolated test schema** — the owner's words, D-438.
Not covered by this acceptance: tests with people, screen-reader sign-off, production readiness, policy publication
(none exists).

## 2. Owner rulings recorded

| Ruling | Decision | Where it lands |
|---|---|---|
| Evaluation model (D-439) | Policy supplies variables and conditions; scenario supplies profiles and facts; variable difference reported; profile difference invalidates a gating result; exploratory may show mismatches without qualifying. **A variable mismatch is informational only while the fact is type- and value-valid under the policy's definition; otherwise it must not pass a gating result** | **implemented and tested** (§8.1) |
| Limits (D-440) | 200 / suite, 60 / live evaluation, 100 / page, and the fact, record-size and execution bounds — **configurable, validated safety limits, not capacity guarantees; not to be raised without measured evidence** | `68_…` addendum |
| Q-a (D-441) | No acknowledgement workflow or table for exploratory profile mismatches; gating reconciliation mandatory | `70_…` §4 |
| Q-b (D-442) | **A gating suite whose every expectation began as a result proposal BLOCKS publication**; independent authored expectations required for the material behaviours; provenance kept, shown, never converted | `70_…` §5.2–5.3, deterministic rule |
| Q-c (D-443) | The checker may have authored suite expectations, if not the candidate's submitter | `70_…` §2 |
| Q-d (D-444) | Separate append-only candidate event table; accepted policy-event constraint untouched | `70_…` §9 |
| Q-e (D-445) | No time-to-live; exact fingerprints, verified reproduction, unchanged evidence; the run's date and age shown | `70_…` §5.1 |
| Q-f (D-446) | Prototype endpoints retire only when callers are identified, replaced, parity proven, tests pass, no supported configuration relies on them | `70_…` §12 |

## 3. Preflight (read-only; before any change)

| # | Check | Result |
|---|---|---|
| 1–3 | Database, schema, environment | `Call360_db`, `call360`, `app_env = local`, host `localhost` |
| 4 | Revision | `0039_applicability_policy` |
| 5, 6 | Next migration, parent, heads | one head `0040_applicability_scenarios`, parent `0039_applicability_policy` |
| 7 | Published showcase surveys | five surveys and module `M-100019`, `PUBLISHED` v1 1.0, fingerprints identical to the accepted state |
| 8 | Library | 32 versions (31 `PUBLISHED`, 1 `SUPERSEDED`), digest `75ca7466…7a43acbc`, identical; no open draft or candidate |
| 9 | Saved policies | **one changed since the accepted state — by the owner** (see below) |
| 10 | Roles and permissions | 13 roles, 87 grants (digest `bda6e0cb…83258a10`), 15 group-role mappings — identical; **one group membership added by the owner** (see below) |
| 11 | Objects and conflicts | no APPL-X4a table present; no pending revision other than `0040` |
| 12 | Safe to migrate | development API server stopped |

Inventory before: **147 tables, 18,168 rows**, 151 triggers, 65 functions, 57 permissions.

### 3.1 Differences found at preflight, and why I proceeded

The state was not identical to the one I recorded at the end of the APPL-X3 enablement. Every difference is in the
audit trail under the owner's own sign-in, or is the system's own worker:

| When | Who | What |
|---|---|---|
| 09:13 | `dev.admin` | added to group `LOCAL_DEV_APPL_AUTHOR_SG` (role `DEV_APPL_AUTHOR`), reason "adding this role" |
| 17:23 | `dev.admin` | saved policy `SHOWCASE-DEPENDENCIES` (revision 5 → 6) |
| 17:39 | `dev.admin` | created the survey draft `S-SURVEY-FOR-PA-ACCIDENT-CASS` |
| 07:29–08:47 | retention worker | purged 14 expired recordings and transcripts (`conversation_session`, `session_event`, `media_asset`, `transcript_run`) |

None is a migration conflict; roles and grants themselves are unchanged; the migration is additive. I treated this
as the baseline and recorded it. **For the owner to note:** `dev.admin` now holds the applicability author's
permissions through that membership. I did not add, remove or change any membership, role or grant.

## 4. Backup and restore evidence

- `_db_backups/call360_dev_before_0040_20261124.dump` (outside every repository), 2,314,195 bytes.
- SHA-256 `92a88a246c1d211df485faa1aa3795e954fa01340f4fac2245fb55fcfa0110ce`.
- 147 tables, 147 table-data entries; **18,168 rows in the archive = 18,168 in the inventory; no per-table mismatch**.
- `pg_restore` to SQL dry run: clean.
- Manifest with every table's row count and digest, the grants, library and policy digests:
  `call360_dev_before_0040_20261124.manifest.json` (mode 600).
- Recovery: `_db_backups/RESTORE.md`, "Rolling 0040 back". No reset, truncate or re-seed.

## 5. Migration `0040` — completion

`uv run alembic upgrade 0040_applicability_scenarios`; exit 0; revision `0040_applicability_scenarios`.

| Added | |
|---|---|
| Tables (7) | `applicability_scenario`, `applicability_scenario_dependency`, `applicability_suite`, `applicability_suite_member`, `applicability_scenario_event`, `applicability_evaluation_run`, `applicability_evaluation_result` |
| Guard functions (6) and triggers (7) | scenario / suite guard, dependency, suite member, event, run, result |
| Foreign keys | 14, all validated |
| Indexes | 23 |
| Permissions, role grants | none |

Removed: nothing. Constraints not validated: 0. Disabled triggers in the schema: 0.

**Immediately after:** 146 of 147 existing tables identical in row count and content digest; the one difference is the
revision value in `alembic_version`. Roles, grants, mappings, library versions, showcase surveys and saved policies
identical.

## 6. Feature settings

- Names confirmed in the code before changing anything: backend `applicability_scenarios_enabled`
  (`APPLICABILITY_SCENARIOS_ENABLED`); frontend `VITE_APPLICABILITY_SCENARIOS`.
- Backend `.env`: `APPLICABILITY_SCENARIOS_ENABLED=true` added; library and policies settings kept. Readiness `200`.
- Frontend started with `VITE_SURVEY_STUDIO_PERSISTED=1 VITE_SURVEY_APPLICABILITY=1 VITE_APPLICABILITY_LIBRARY=1
  VITE_APPLICABILITY_POLICIES=1 VITE_APPLICABILITY_SCENARIOS=1`.
- The "where things are kept" panel, asserted in the walk: library **saved in Call360**; policies **saved as working
  drafts — "Publication is not available yet"**; scenarios, suites and runs **saved in Call360**; surveys **published
  versions read from Survey Studio**. A saved policy is labelled "Draft" everywhere; nothing presents it as published.

## 7. Development demonstration (real browser, development database, real sign-ins)

Identities: the existing `dev.applicability.author` and `.checker`, and `dev.survey.author` as a person without
applicability permission. No role or grant changed (digests identical before and after). Created: **six** labelled
synthetic scenarios, **one** suite, **three** recorded runs. No scale data.

| Journey | Result | Screens (`evidence/APPL-X4a/development/screens/`) |
|---|---|---|
| A persistent scenario | "ILP only — face to face (synthetic)", code `SHOW-ILP-ONLY`, profile New business application, facts from the template plus a sales channel; saved; browser closed; new sign-in; **document, snapshot, scenario and result fingerprints identical**; 9 pinned dependencies; selects A | `02`–`05` |
| B variant | NFTF no → yes on a saved variant: **+ C, − A**; reasons named by the server: "ILP needs Survey A was active and is now replaced", "NFTF needs Survey B … replaced", "ILP with NFTF needs Survey C … now active" | `06`–`08` |
| C suite | Six cases — ILP only → A; NFTF only → B; both → C (explicit replacement in the saved policy); neither → none; NFTF not known → unresolved, A, B, C pending; replacement sale → A + D. **Every expectation stated and confirmed on the screen; stored `source: AUTHORED`.** Saved, reopened, run: 6 of 6 | `09`–`11` |
| D failing expectation | ILP only expected B → **FAILED 5 of 6**: "Expected … B … to be selected; it is not selected · open requirement r2" and "… A … is selected and was not expected · open requirement r1". The stored expectation was still B after the run. Corrected in the editor → PASSED. **Three runs on record: passed, failed, passed** | `12`, `13` |
| E immutable run | After a scenario was edited: run read back byte-identical through the API, same fingerprints on screen, **"Reproduced. 6 of 6"** from the record. With the policy draft then changed (revision 9): the run still shows revision 8 and reproduces; against the current draft **2 scenarios differ** (ILP with NFTF: + A, + B; NFTF not known: + A), with reasons. Nothing recorded by looking. Policy document then restored exactly (revision 10, same document and snapshot fingerprints) | `14`, `15`, `20-E` |
| F read-only and isolation | Checker reads scenarios and the run (`200`); saves, creates, suite save, run → `403`. Author: another market `MARKET_NOT_IN_SCOPE`; unknown `404`; stale `STALE_REVISION`; `PUT` / `DELETE` on a run `405`; a real-looking identity number `LOOKS_LIKE_REAL_DATA`. Person without applicability permission: studio closed, `403` ×3. Nothing changed by any of it | `19`, `20-F`, `21` |
| G Survey Studio | From a recorded result: Survey C previewed at its exact published version → Survey Studio, modules and questions → back to the studio; **an unsaved scenario edit made beforehand was still there** | `16`–`18` |
| Designer route | The designer's "Saved scenarios" picker shows a saved scenario read-only, with the server's result | `22` |

Honest notes:

- Four of the six scenarios were created through the application's API from the signed-in author's browser session,
  not by clicking through the form; two were created through the form. All six are ordinary saved scenarios.
- Journey E changed the showcase policy and put its document back: it is now at revision 10 with the same content
  as revision 8. One scenario (`SHOW-NEITHER`) went to revision 3 and back to its original facts.
- A full page load discards unsaved edits (they live in the tab); in-app navigation keeps them. The save bar says
  "Unsaved changes" throughout.
- Restore controls and scale were exercised in the test environment only, to keep development small.
- Journey F used the checker as the read-only identity; the publisher was not signed in separately (same read-only
  permissions for these operations; covered by the backend tests).

## 8. Changes made after acceptance (all verified on the test schema first)

### 8.1 Variable-version incompatibility (owner ruling)

`scenarios.py`, in one place: when a scenario pins another version of a variable than the policy, the given value is
checked against **the policy's** definition. Another type, another currency or a value not allowed →
`VARIABLE_VERSION_INCOMPATIBLE`; in a gating run the result is `INVALID_DEFINITION`. A compatible difference stays
`VARIABLE_VERSION_DIFFERS` (information) and passes normally. The evaluator is not changed.

Test: a variable gains a value in version 2; a scenario on version 2 with the old value passes a gating suite with
the information notice; a scenario with the new value — valid by its own definition, not by the policy's — is
`INVALID_DEFINITION` **even though "unresolved" was the stated expectation**; the same scenario in an exploratory
suite is evaluated, flagged, and never counts.

### 8.2 Carry-forward

| Item | Done | Test |
|---|---|---|
| 5.2 Restore archived scenarios and suites | "Show archived" in both lists; an archived item opens read-only with who archived, why and the history; Restore needs edit permission and a confirmation | X4.11 (incl. a read-only person: no control, API `403`; an archived suite's run still reads) |
| 5.1 Designer integration | read-only "Saved scenarios" picker in the designer (contract and remaining steps: `68_…` addendum); quick preview untouched | X4.11 (nothing changed or recorded by looking) |
| Unsaved work | scenario and suite edits survive in-app navigation and return | X4.11; development journey G |
| 5.4 Provenance | unchanged and re-checked: "not stated", "Proposal — confirm", "Confirmed", "Now" (live) and "Recorded" are distinct labels; a run never changes an expectation | X4.4; development journey D |

### 8.3 Accessibility of the shared shell — recorded as a real defect, NOT changed

- **Defect:** at widths of 760 px and below, `mockup.css` hides the text of the main navigation links with
  `display: none`, which removes it from the accessibility tree; the links then have no accessible name
  (`link-name`), and the account button likewise (`button-name`). 51 nodes at 390 px. This affects every page of the
  application, not the studio.
- **Smallest safe correction proposed** (not made — it is a shared-shell change outside this authorisation): give
  each navigation link and the account button an `aria-label` equal to its visible label (two components, no layout
  or style change); add one automated scan of the shell at 390 px to the standard browser suite.
- **Consequence stated plainly:** full-application WCAG conformance is **not** claimed while this is open. Inside
  the Scenario studio the automated scan has no serious or critical finding; no screen reader was used.

## 9. Integrity comparison (preflight → after the whole demonstration)

Unchanged: roles, grants and mappings (digests identical); all 32 library versions; the five showcase surveys and
the module; 32 legacy assignment, script, case, session, plan and evaluation tables (row count and content digest);
`SHOWCASE-DEPENDENCIES`.

Changed, all expected:

| Table | Before → after | Why |
|---|---|---|
| `alembic_version` | value | the migration |
| seven APPL-X4a tables | 0 → 6 scenarios, 50 dependency rows, 14 events, 1 suite, 6 members, 3 runs, 18 results | the demonstration |
| `applicability_policy` | 2 → 2 (`SHOWCASE-ILP-NFTF` revision 8 → 10, **same document and snapshot fingerprints**) | journey E, changed and restored |
| `applicability_policy_event` | 14 → 16 | those two saves |
| `audit_event` | 3,961 → 3,992 | sign-ins, the demonstration's writes, the refused attempts |
| `auth_session`, `login_attempt`, `refresh_token`, `refresh_token_family` | +5 each | sign-ins of the walk |

## 10. Regression — one run, on the final source, after development enablement and the last edit

All backend and browser tests ran against the isolated test schema `call360_test`, never development.

| Check | Result |
|---|---|
| Backend suite (evaluator tests, golden 82 survey runs and 14 plans, permissions, markets, migrations) | **1,087 tests; exit 0; no failure or error** |
| Golden fixtures and expectations; evaluator; `policies.py` | not modified |
| Ruff, format check, Mypy (138 source files) | clean |
| OpenAPI regeneration | byte-identical; SHA-256 `50d663987a1c6ac231ee5c090b72b8435566a4b00fbba14805fedab4ddb1a9cc` (unchanged from APPL-X4a) |
| Frontend client check, lint, type check, production build | pass / clean / clean / built |
| Frontend unit tests | **636 passed** |
| Scenario studio browser suite | **11 passed** (10 accepted + X4.11) |
| Applicability browser suite (accepted X1R, X2, X3 journeys) | **26 passed** |
| Persisted / prototype / standard browser suites | **34 / 13 / 33 passed** |
| Specifications validator | pass |
| Development database during the regression | revision `0040`; no table changed except one sign-in (`audit_event`, `auth_session`, `login_attempt`, refresh tokens +1) — not made by the regression, which never touches development |

- **Intermittent failures: none.** D-418 watch: its tests passed; the symptom did not recur.
- The number of backend tests is unchanged (1,087): the incompatibility rule was added to an existing test.
- No timeout was raised; no golden expectation changed.
- The voice timing test passed. That is not a fix; the Voice Studio issue stays open and Voice Studio was not touched.
- Outputs: `docs/acceptance/evidence/APPL-X4a/development/test-output/`.

## 11. Remaining gaps, stated exactly

- **Human usability:** no person performed a task in the Scenario studio. Nothing about ease of use is measured.
- **Accessibility:** automated scan only; no screen reader. The shared-shell defect of §8.3 is open, so
  full-application WCAG conformance is not claimed.
- **Designer:** the live-preview picker still uses in-tab examples; saved scenarios are reachable read-only.
- **Provenance:** who stated an expectation is derivable from the suite's history today; the per-expectation stamp is
  the first step of APPL-X4b (`70_…` §5.3).
- **Limits** are constants in code, validated on every request; they are not deployment settings.
- **Not exercised in a browser:** policy scope and choose-one requirements in suites (the showcase policies have
  neither).
- **Development demonstration** used the checker as the only read-only identity.

## 12. Stop

Development enablement and verification are complete. APPL-X4b is specified (`70_…`) and not started. Not started:
migration `0041`, APPL-X5, APP-1a, OPS-1, VOICE-1, legacy retirement, the shared-shell accessibility change. Nothing
committed or pushed.

