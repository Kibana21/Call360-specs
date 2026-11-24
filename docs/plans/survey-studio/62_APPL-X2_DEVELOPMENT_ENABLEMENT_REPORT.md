# APPL-X2 — development enablement of `0038`: report and evidence

**Status: DONE AND VERIFIED ON LOCAL DEVELOPMENT 2026-11-24, on the owner's authorisation. Stopped for owner
review.** Nothing is committed. APPL-X3 is not started.

Authorisation: "Accept APPL-X2, Enable Development 0038 and Prepare APPL-X3" (2026-11-24), and the owner's answer
of the same day authorising `survey.read` for the three `DEV_APPL_*` roles. Decisions D-401 … D-410.
Evidence: `docs/acceptance/evidence/APPL-X2/development/` (text evidence and 19 screenshots).

This is technical verification on synthetic data. It does not establish operational readiness, approved Compliance
rules or verified human usability.

---

## 1. Final success criterion

> In local development, a user must be able to create and persist variables, profiles and conditions, publish them
> through three genuinely separate identities, and reuse their exact versions in a beautiful Applicability Designer
> linked to real published Survey Studio surveys. No legacy assignment object should be created or changed. No
> operational call behavior should be affected.

| | Result |
|---|---|
| create and persist a variable, a profile, a condition | **done in the development browser** (§8); each survived a reload or a later session |
| three genuinely separate identities | **done**: `dev.applicability.author`, `.checker`, `.publisher`, three browser sessions; 32 of 32 versions in development carry three different people |
| reuse of exact versions in the Designer, linked to real published surveys | **done**: conditions at version 1, Surveys A, B and C at version 1.0 with their published fingerprints; Survey C opened in Survey Studio and returned from |
| no legacy assignment object created or changed | **verified**: assignment rules, bindings, requirement groups, plans and simulations are byte-identical to the preflight (§10) |
| no operational call behaviour affected | **verified**: cases, attempts, sessions, runs, findings byte-identical; nothing in this checkpoint reads or writes them |

## 2. Preflight (Part B1) — all eleven conditions met, nothing changed

| # | Check | Found |
|---|---|---|
| 1–3 | database, schema, environment | `Call360_db`, `call360`, `local`; read-only connection |
| 4 | current revision | `0037_shared_rule_services` |
| 5–6 | intended next migration; unexpected heads | one script head, `0038_applicability_library`, whose parent is `0037` |
| 7 | inventory | 140 tables, 17,160 rows, 144 triggers, 58 functions, 53 permissions |
| 8 | protected-table digests | a content digest of every one of the 140 tables recorded |
| 9 | roles and grants | 10 roles, 78 grants, 12 group-role mappings, 10 active principals |
| 10 | showcase surveys | the five surveys and the shared module published at version 1.0, with the fingerprints recorded in APPL-X1R |
| 11 | safe state | the development API server was stopped before the inventory and stayed stopped until after the migration |

## 3. Backup (Part B2)

| | |
|---|---|
| File | `_db_backups/call360_dev_before_0038_20261124.dump` (outside every repository, mode 600) |
| SHA-256 | `c16debaaf6ad2d7fdd20b81e32bd38cb77ee306b8990aeb0e4eaeaee21a65519` |
| Verified | 140 `TABLE` and 140 `TABLE DATA` entries; rows in the archive equal the inventory table by table (17,160); `pg_restore` to SQL clean |
| Manifest | `call360_dev_before_0038_20261124.manifest.json` beside it: per-table rows and digests |
| Recovery | `_db_backups/RESTORE.md`, section "Rolling 0038 back" |

No reset, no re-seed.

## 4. Migration (Part B3–B4)

`alembic upgrade 0038_applicability_library` — exactly that revision.

| Introduced | |
|---|---|
| tables | `applicability_asset`, `applicability_asset_version`, `applicability_asset_dependency`, `applicability_event` |
| guards | four functions and their four triggers |
| permissions | `applicability.read`, `.edit`, `.approve`, `.publish` — **held by no role** after the migration |
| nothing else | no table, trigger, function or permission removed or altered |

Of the 140 existing tables, **138 were byte-identical** after the migration; the two that changed are
`alembic_version` (the revision) and `permission` (53 → 57 rows). Roles, grants and group-role mappings were
unchanged. Backend readiness passed at `0038`.

## 5. The library switched on (Part C)

`APPLICABILITY_LIBRARY_ENABLED=true` in the development environment file (name only; no value of that file was
printed) and the frontend started with `VITE_APPLICABILITY_LIBRARY=1`. Verified in the browser: the workspace reads
the persisted library ("Library saved"; the built-in example is not loaded), and one control states the four kinds
of thing separately — variables, profiles and conditions *saved in Call360*; policies and scenarios *in this tab
only*; surveys *published versions read from Survey Studio* (screenshot `dev-01`). After a reload the in-tab policy
was gone and the library items were still there, as the labels say.

## 6. Dedicated identities and permissions (Part D)

`scripts/dev_applicability_identities.py` (idempotent; `--remove` disables them and drops the grants).

| Role (development only) | Person | Permissions |
|---|---|---|
| `DEV_APPL_AUTHOR` | `dev.applicability.author` | `applicability.read`, `applicability.edit`, `survey.read` |
| `DEV_APPL_CHECKER` | `dev.applicability.checker` | `applicability.read`, `applicability.approve`, `survey.read` |
| `DEV_APPL_PUBLISHER` | `dev.applicability.publisher` | `applicability.read`, `applicability.publish`, `survey.read` |

* **The gap, reported before anything was granted.** As first created — with exactly the listed permissions — the
  three people were refused at the Survey Studio route ("Access restricted"): the workspace is part of Survey
  Studio, and the survey picker, the previews and the evaluator need `survey.read`. The existing survey identities
  could open it but not read the library. The owner then authorised `survey.read`, and only that, for these three
  roles (D-408).
* **Before / after.** The three roles did not exist before; nine grants were added in all (78 → 87); **every one of
  the ten earlier roles holds exactly what it held**; no identity beyond the three was created (10 → 13 principals).
  Each change is in the audit trail (`ADMIN.ROLE_PERMISSIONS_SET`, with the reason naming the authorisation).
* **Credentials** are generated by the script and written only to the gitignored
  `Call360-backend/.secrets/dev_survey_accounts.json` (mode 600). None was printed or put in any evidence file.
* **Read-only on Survey Studio — 46 API checks.** Each of the three reads the survey listing, a published version
  and its documents, and runs the evaluator; each is refused (403) creating a survey, saving or changing a draft,
  issuing a code, submitting, approving, publishing, withdrawing and simulating, and reading or creating the legacy
  assignment policy and bindings. Survey Studio's tables were unchanged by the attempts.
  (`survey_read_only_for_applicability_identities.txt`)
* **Separation still enforced after the grant — 39 API checks**, on a fresh synthetic item (`separation_check`):
  the checker and the publisher cannot draft; the author cannot approve; the publisher cannot approve or publish
  before approval (409 `NOT_APPROVED`); the checker cannot publish what they approved; the author cannot publish;
  the draft cannot change during review; a stale save is refused; a published version cannot be written (no such
  operation; 405), re-published or decided again; rejected requests left the database unchanged (digest of every
  asset and version row compared). Unsupported identities — survey authors and publishers, rule and finding-rule
  people, no session — get 403 or 401. (`governance_and_permissions_api.txt`)
* **Market isolation**: creating in, reading the workspace of, or testing against market `MY` answers 403
  `MARKET_NOT_IN_SCOPE`; an item that does not exist for the caller's market answers 404; a reference outside the
  market is a blocker.

**What could not be shown on development.** Nobody there holds two applicability permissions — by design — so the
*identity* rules (`SELF_REVIEW_DENIED`, `SELF_PUBLISH_DENIED`, `APPROVER_PUBLISH_DENIED`) are not exercised on
development: there, each refusal is by permission. They are proven on the test schema, by a person holding all
four permissions and by the table's own constraints (`61_…` §3). No extra identity was created to show it.

## 7. The synthetic library (Part E)

`scripts/appl_library_setup.py`, inspected first: HTTP only, three signed-in people, reads its definitions from
`appl_library_seed.json`, never overwrites, reports a conflict and leaves it alone.

| Run | Result |
|---|---|
| verify-only, before | 26 missing; nothing written |
| first run | **26 published** (12 variables, 7 profiles, 7 conditions; `high_premium` at version 2 with version 1 kept) |
| verify-only, after | 26 reused; exit 0 |
| second run | 26 reused; **only sign-in and audit rows changed** |

Verified from the rows, not from the script's own report: every content fingerprint and every manifest fingerprint
recomputed and equal; every version submitted, approved and published by three different people; every pin names an
existing version with the same number and fingerprint; no invalid dependency row. NFTF and the riders are published
as "not mapped", replacement as "proposed": nothing was invented. The five showcase surveys and the shared module
are identical to the preflight. Identities and versions: `library_setup_first_run.json`,
`library_identities_and_versions.json`.

The demonstrations then added five clearly synthetic published items: `governance_check`, `separation_check`,
`senior_applicant`, the profile `new_profile` ("Senior applicant extension (synthetic)") and
`senior_ilp_outside_nftf`. A sixth, a variable deliberately left as a draft to show an invalid dependency, was
discarded afterwards. A published item cannot be removed; these are inert.

## 8. Development browser demonstration (Part F) — screenshots `development/screens/dev-01 … dev-17`

Three browser sessions, three signed-in people, against the development database. Zero browser errors.

| | Shown | Screenshot |
|---|---|---|
| F1 | a variable created; saved as a draft; the browser reloaded and the same draft reopened; validated (nothing blocking; what would be frozen shown); submitted; approved by a second person; published by a third; history and fingerprint | 02, 03 |
| F2 | a profile created; a published variable added; a variable that is only a draft detected and blocking submission, then removed; profiles combined, and a combination that cannot hold detected; the exact versions to be frozen shown; published by three people with its pins | 04 – 07 |
| F3 | a named condition with AND, OR and NOT, nested, reading two published conditions and two variables; the live result from the Python evaluator; published by three people; its four exact pins | 08, 09 |
| F4 | a policy on the persisted library: ILP → A, NFTF → B, ILP AND NFTF → C, each an exact published Survey Studio version; all three selected; with NFTF not known, A definite and B, C pending, not resolved; the newly published condition used at its exact version; Survey C previewed, opened in Survey Studio and returned from with the draft intact; C replacing A and B; the graph and the decision matrix | 10 – 17 |
| F5 | by real API requests | §6 |

Honest notes: the walk was run three times, because two steps of my script needed correcting and one real layout
defect was found (below); it resumes from what is already saved, so **F1's intermediate screens (the draft after
reload, the approval, the publication) were captured in the first run and overwritten** — its history screen, which
names the three people, is the one filed. The policies of F4 are in the tab, as labelled.

## 9. Regression (Part H)

Run on 2026-11-24, after the enablement, against the isolated test schema (the suites never touch development).
Outputs: `evidence/APPL-X2/development/regression-*.txt`.

| Check | Result |
|---|---|
| Backend suite | **1,066 passed, 0 failed** (1,065 at acceptance, plus the test of the D-405 change) |
| Golden 82 runs and 14 plans | pass; **no fixture or expectation file is modified** |
| Ruff (278 files), Mypy (134 files) | clean |
| OpenAPI | consistent; SHA-256 `429af28cb110eda9b66fdc2d00afd7250c68375b53a48d0e4371bad51470aaa8` (one optional field and one schema added for D-405); the frontend client matches |
| Frontend unit tests | **636 passed** |
| Frontend lint, types, production build | clean |
| Applicability browser journeys | **16 passed** (the nine of APPL-X1R and X2.1 – X2.7, now including the frozen-versions step) |
| Existing browser suites | persisted **34**, prototype **13**, standard **33** — all passed |
| Specifications validators | pass |
| Development data integrity | §10 |
| Permissions and governance on development | §6: 39 and 46 API checks, all as expected |
| Cross-product Survey Studio integration | journeys X1R.1, X1R.2, X1R.8, X1R.9 in the test environment; Survey C opened and returned from on development (§8) |

Honest notes:

* **No failure occurred in this regression, and no test was weakened.** The one existing test changed is the
  contract-size test, which now counts 22 applicability schemas instead of 21.
* **The voice timing test passed. That is not a fix** (D-406): nothing in Voice Studio was changed, and the defect
  is intermittent by its nature. It stays open.
* One stylesheet rule (the "Combine with…" list) was added while the full run was in progress. The applicability
  suite, the unit tests, types, lint and build were run again afterwards on the final code; the persisted, prototype
  and standard suites, which do not load that stylesheet's screens, were not.
* The suites ran while the development servers were up on their own ports; the two environments share nothing.

## 10. Historical data integrity — final comparison with the preflight

Taken after everything above. Row count and content digest of every table, before and after.

| Group | Tables identical | Rows |
|---|---|---|
| Script Studio (families, versions, modules, questions, revisions) | 6 of 6 | 137 |
| Survey Studio published content | 8 of 8 | 708 |
| Legacy assignment rules and script assignments | 5 of 5 | 303 |
| Survey bindings | 2 of 2 | 21 |
| Requirement groups | 3 of 3 | 22 |
| Historical plans and simulations | 9 of 9 | 153 |
| Operational cases, attempts, sessions, runs, findings | 8 of 8 | 3,126 |
| **All existing tables** | **124 of 140** | |

The 16 that differ are identity, sign-in, audit and migration bookkeeping only: `alembic_version`, `permission`,
`role`, `role_permission`, `app_group`, `group_membership`, `group_role_mapping`, `group_scope_mapping`,
`principal`, `identity_binding`, `local_credential`, `auth_session`, `login_attempt`, `refresh_token`,
`refresh_token_family`, `audit_event`. (`development_enablement_0038.txt`)

## 11. Changes made to the accepted code in this checkpoint

| Change | Why |
|---|---|
| `submit` accepts the reviewed `pins`; 409 `PINS_CHANGED` if they are not what would be frozen. The submit step shows the exact versions and fingerprints and requires confirmation; the reviewer sees what a candidate froze | owner ruling A4 (D-405) |
| `scripts/dev_applicability_identities.py` | Part D |
| `appl_library_setup.py` acknowledges its pins | follows from A4 |
| one stylesheet rule: a list opened inside the profile result panel is as wide as its row | a real defect found on development: "Combine with…" was cut off when a profile name was long |

Nothing else changed. The evaluator was not edited. Voice Studio was not touched.

## 12. Carried forward, not done

Nested Condition Lab readability; graph neighbourhood legibility at 100 requirements; testing with people;
screen-reader testing; the saved-library / in-tab-policy distinction (truthfully labelled, removed by APPL-X3);
marking draft dependencies in the Designer (D-404, APPL-X3); the code given to a new profile before it is named
(D-410); the Voice Session Timeline defect (D-406).

## 13. For the owner

1. Review of the development enablement.
2. The APPL-X3 readiness assessment, `63_…`, and its six questions.
3. The proposals of D-397 that were not ruled, (e) to (j), stay open.

Nothing further is authorised. APPL-X3, APP-1a, OPS-1, VOICE-1 and legacy retirement were not started.
