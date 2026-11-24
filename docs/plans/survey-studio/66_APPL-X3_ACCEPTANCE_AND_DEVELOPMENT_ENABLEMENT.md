# 66 — APPL-X3 acceptance and development enablement

**Date:** 2026-11-24. **Data:** synthetic only. **Simulation only.** **Nothing committed or pushed.**
**Authorisation:** the owner's "APPL-X3 acceptance, development enablement and APPL-X4 readiness" (2026-11-24):
APPL-X3 accepted on the test schema; controlled application of `0039_applicability_policy` to local development;
enablement and verification only. APPL-X4, operational integration, voice and legacy retirement **not** authorised.

---

## 1. Formal acceptance record (test schema)

**APPL-X3 IS ACCEPTED as technically verified on the isolated test schema** — the owner's words, recorded as D-419.
Scope accepted: documents `64_…` and `65_…`; migration `0039`; ten policy operations; saved gallery and designer.
Not accepted by this record: any test with people, screen-reader sign-off, production readiness, publication of
policies (none exists).

## 2. D-416 reconciliation — the owner's decisions

| Item | Decision | Effect now | Carried to APPL-X4 |
|---|---|---|---|
| D-416(a) one variable version per evaluation | **Accepted** for one policy evaluation | Evaluator behaviour unchanged; `PIN_DIFFERS` stays a diagnostic for drafts and labelled exploratory evaluation | **Publication-blocking semantic conflict**, unless a separately approved, auditable override contract exists. Preferred: explicit reconciliation or a new condition version (`67_…` §2.3) |
| D-416(b) moved draft dependency | **Fail closed accepted** | No earlier content fabricated; latest draft never silently evaluated; `DEPENDENCY_STALE` with previous and current revision; deliberate reconciliation; saved policy preserved until the author acts | This does **not** establish immutable reproducibility for draft assets |
| D-416(c) prototype endpoints | **Retained**, feature-gated, until callers migrate | Nothing removed; one evaluation algorithm | Controlled removal after transition, with regression coverage (`67_…` §4) |
| Scenario profile snapshots | Ruling for APPL-X4 | — | Saved regression scenarios keep exact fact and profile snapshots; ad hoc previews disclose and fingerprint what they resolved (`67_…` §2.1) |
| D-418 intermittent failure | **Retained open** | Cause now established and a fix verified (§8); **not closed by me** | Owner closes |
| Voice Studio reliability | Retained; Voice Studio not modified | untouched | — |

Recorded as D-420.

## 3. Preflight (read-only; before any change)

| # | Check | Result |
|---|---|---|
| 1, 2 | Database / schema | `Call360_db` / `call360` |
| 3 | Environment | `app_env = local`, host `localhost` |
| 4 | Revision | `0038_applicability_library` |
| 5 | Migration heads | exactly one: `0039_applicability_policy` |
| 6 | Parent of `0039` | `0038_applicability_library` |
| 7 | Library | setting on; 32 versions (31 `PUBLISHED`, 1 `SUPERSEDED`); 0 open drafts, 0 open candidates |
| 8 | Library versions | count 32, content digest `75ca74660920aa584923c3a57a43acbc` |
| 9 | Showcase surveys | five surveys and module `M-100019`, all `PUBLISHED` v1 1.0, fingerprints identical to the accepted APPL-X2 state |
| 10 | Roles and grants | 13 roles, 87 grants (digest `bda6e0cb8bd661d182f3ecec83258a10`), 15 group mappings, 13 active principals — identical to the accepted APPL-X2 state |
| 11 | Conflicts | no policy table present; no pending revision other than `0039` |
| 12 | Safe state | development API server stopped before the migration |

Inventory before: **144 tables, 17,945 rows**, 148 triggers, 62 functions, 57 permissions; per-table row count and
content digest recorded in the backup manifest.

## 4. Backup and restore evidence

- File: `_db_backups/call360_dev_before_0039_20261124.dump` (outside every repository), 2,270,298 bytes.
- SHA-256 `fd19bc85e1cef375561db54f1f8fb782ef3b05e9b3a11ed16c7c5722f2612ae4`.
- Archive: 144 tables, 144 table-data entries; **17,945 rows in the archive = 17,945 in the inventory; no
  per-table mismatch**.
- `pg_restore` to SQL dry run: clean.
- Manifest: `call360_dev_before_0039_20261124.manifest.json` (mode 600).
- Recovery instructions: `_db_backups/RESTORE.md`, section "Rolling 0039 back".
- No reset, no re-seed.

## 5. Migration `0039` — completion

Applied exactly `uv run alembic upgrade 0039_applicability_policy`; exit 0. Revision now `0039_applicability_policy`.

| Added | |
|---|---|
| Tables | `applicability_policy`, `applicability_policy_dependency`, `applicability_policy_event` |
| Triggers / functions | `applicability_policy_guard`, `applicability_policy_dependency_guard`, `applicability_policy_event_guard` (one each) |
| Indexes | three primary keys; `uq_applicability_policy_identity`, `uq_applicability_policy_dependency`, `ix_applicability_policy_dependency_asset`, `ix_applicability_policy_dependency_survey`, `ix_applicability_policy_event` |
| Foreign keys (all validated) | dependency → `applicability_policy`, `applicability_asset`, `applicability_asset_version`, `survey_definition`, `survey_version`; event → `applicability_policy` |
| Permissions | none |

Removed: nothing. Constraints not validated: 0. Disabled triggers in the schema: 0. No constraint was disabled.

**Immediately after the migration:** 143 of 144 existing tables identical in row count and content digest; the one
difference is `alembic_version` (the revision value — expected). Roles, grants, mappings, library versions and
showcase surveys identical.

## 6. Feature settings

- Backend `.env`: `APPLICABILITY_POLICIES_ENABLED=true` added (value is not a secret); library setting kept on.
  Readiness `200` at head `0039`.
- Frontend development server started with `VITE_SURVEY_STUDIO_PERSISTED=1 VITE_SURVEY_APPLICABILITY=1
  VITE_APPLICABILITY_LIBRARY=1 VITE_APPLICABILITY_POLICIES=1`.
- The workspace's own "what is kept where" panel states, and the walk asserts: library **saved in Call360**;
  policies **saved in Call360 as working drafts**; scenarios **in this tab only**; surveys **published versions read
  from Survey Studio**. Scenarios do not survive a reload; that is APPL-X4.
- Saved policies come from PostgreSQL: the policy was read back in a new browser context and by direct count
  (`applicability_policy` 2 rows, 19 dependency rows, 13 events).

## 7. Development demonstration (real browser, development database)

Identities: the three existing `dev.applicability.*` accounts, signed in with their own credentials (never printed).
No role or grant changed (digest identical before and after). Two clearly labelled synthetic policies exist; **no
20 / 50 / 100-requirement policy was created in development.**

| Journey | Result | Screens (`evidence/APPL-X3/development/screens/`) |
|---|---|---|
| A create and save | Name first; suggested code `ILP-AND-NFTF-APPLICABILITY-SYNTHETIC-SHO` reviewed and replaced by `SHOWCASE-ILP-NFTF`; market SG, scope every application; published condition "Is ILP" v1 → published Survey A 1.0; saved | `dev-x3-02…04` |
| B close and reopen | Browser context closed; new sign-in; same policy from the gallery; document and snapshot fingerprints identical; same result and same policy fingerprint for the same facts | `dev-x3-05, 06`; `run2-03, 04` |
| C multiple surveys | ILP only → A; NFTF only → B; both → A + B + C; neither → none; NFTF unknown → **unresolved**, A selected, B and C pending "NFTF applies" | `dev-x3-07…10` |
| D explicit replacement | Both → C alone (A and B replaced). Both + replacement sale → C + D. ILP only + replacement sale → A + D (nothing replaced) | `dev-x3-11, 12` |
| E cross-product | Survey C previewed at published version 1.0; opened in Survey Studio (modules and questions); returned with the unsaved edit intact; Survey Studio's "where used" shows the policy from the server | `dev-x3-13…15` |
| F concurrent edits | Two signed-in sessions; second save refused (`STALE_REVISION`); both texts shown; nothing overwritten | `dev-x3-16` |
| G dependencies | "High premium" pinned at v1 while v2 is published: offered, not adopted; adopted deliberately; undo restores the identical dependency-set fingerprint; adopted, saved, reloaded at v2. Draft dependency: "Draft contains unpublished dependencies — not ready for publication". Draft changed: `DEPENDENCY_STALE`, **not evaluated**, reconciled deliberately | `run2-11…15` |

Authorisation, with real sign-ins: checker save / create / archive → `403`; author in market MY →
`MARKET_NOT_IN_SCOPE`; unknown policy → `404`; stale revision → `STALE_REVISION`; wrong survey fingerprint →
`INVALID_SURVEY_REFERENCE`; invalid pin → `INVALID_DEPENDENCY_PIN`; a Survey Studio author without applicability
permission → `403`. The policy was unchanged by all of them. Checker sees it read-only (`dev-x3-17`).

Honest notes:

- **The dependency-demonstration policy was created through the API**, not the designer: the designer offers only
  the current published version of a condition, and showing "newer version offered" needed a reference to the
  existing earlier version 1. No library fixture was published for it.
- **One library item was created in development**: the draft condition `draft_example`, to show draft-dependency
  behaviour. Its draft was discarded afterwards. **An empty item shell remains** (no draft, no version); the governed
  API has no delete. It is not referenced by anything.
- **The first walk stopped on my script's error**, not on the product: it waited for "ready" in the session of a
  Survey Studio author who is correctly refused. Kept as `dev-x3-18-walk-script-error-…png`. The second run resumed
  on the saved policy, which is why journeys C and D have screenshots from run 1 only.
- Restoring an archived policy was exercised in the test environment only, to keep development to two policies.
- Journey F used the one identity that may edit, in two browser sessions; a second editing identity would need a
  grant, and none is authorised.

## 8. UX items

### 8.1 Graph visibility — a real defect, corrected

Confirmed from the screenshot: at 1440 × 900 the canvas began about 585 px down the page, so the selected node and
its neighbourhood sat at the bottom edge of the window. The earlier test asserted only that nodes were inside the
canvas element, which itself extended below the window.

Correction (`DesignerCanvas.tsx`): when the person focuses something (a selection or a search), and any focused
node is outside the window, the page scrolls so the whole canvas sits just under the fixed header. Zoom is not
changed; reduced-motion is respected.

Test (`saved-policies.appl.ts`, at 20, 50 and 100 requirements): the selected node, every node of its
neighbourhood, and the whole canvas must lie between the bottom of the fixed header and the bottom of the browser
window, **without scrolling**, at zoom ≥ 0.6. Before / after: `92-BEFORE-…png`, `92-AFTER-…png`.

### 8.2 Restore an archived policy

Gallery section "Archived policies": each shows who archived it, when, the reason, and its full history. Restore is
offered only with edit permission and asks for confirmation. Journey added to X3.8 (archive with reason → listed →
confirm → back in the gallery → history shows Archived and Restored). Screen `96-…png`.

### 8.3 Editor clarity

Nothing redesigned. Saved-versus-preview labelling was already in place and is asserted in development
(`dev-x3-03`: an unsaved edit is a labelled preview; `dev-x3-12`: "Saved revision 4 · evaluated by Call360 from
exactly what it pins").

Seen, not changed: in the gallery, a one-requirement card stretches to its neighbour's height and shows an empty
tinted block (`run2-16`).

### 8.4 D-418 — cause established, fix verified, **left open for the owner**

**Cause.** The gallery offered "create" before the list of saved policies had arrived. A code suggested then could
already be taken; the server refused with `409 CODE_TAKEN`; the refusal was shown only as a passing notice and the
designer never opened. In the suite this happens when a second 20-requirement policy is created right after a
navigation, while the list is still loading — a timing race, hence intermittent.

**Reproduced deterministically before any fix** (`zz-d418.appl.ts`): with the list delayed by three seconds, the
button was enabled, the server answered `409 CODE_TAKEN`, and the designer did not open — the original symptom.

**Fix.** Creation, patterns, scale examples and duplicate are disabled, with the reason, until the saved policies
are loaded; a refused creation states why and re-reads the list. **No timeout was raised.**

**Verified** by the same reproduction: button disabled while loading; creation answered `201` with a free code; no
`409`; designer opened.

Limits of this claim: the original failure occurred once and left no trace I can match to this cause with
certainty; the reproduction matches its symptom exactly. Per the owner's ruling it stays **open** until closed by
the owner.

**Measurements** (test environment, the suite's populated gallery of 19 policies including 100-requirement ones):

| Action | Requests | Slowest |
|---|---|---|
| Gallery load (before) | list ×2; each policy read ×1–2, **27 reads for 19 policies** | 98 ms |
| Gallery load (after) | list ×1; each policy read exactly once, without inspection; **no inspect / evaluate / preview** | — |
| Open one policy | no list, no other policy read; inspect ×1, evaluate ×2 | 130 ms |
| Save one policy | save ×1; that policy re-read ×1; no list | 210 ms |

A second defect found by the measurement: the gallery was read twice on load (two triggers); now one read at a
time. Both properties are asserted by the test.

## 9. Historical data integrity (preflight → after the whole demonstration)

Unchanged: roles, grants and group mappings (digests identical); all 32 library versions (digest identical); the
five showcase surveys and the module; every Script Studio, legacy assignment (rules, bindings, groups), case,
session, plan and evaluation table (row count and content digest identical).

Changed, all expected:

| Table | Before → after | Why |
|---|---|---|
| `alembic_version` | 1 → 1 (value) | the migration |
| `applicability_policy` / `_dependency` / `_event` | 0 → 2 / 19 / 13 | the two showcase policies |
| `applicability_asset` | 32 → 33 | `draft_example` shell |
| `applicability_event` | 135 → 138 | created, draft saved, draft discarded |
| `audit_event` | 3,895 → 3,950 | 17 sign-ins, 23 access refusals (the authorisation checks and probes), 13 policy and 3 library actions |
| `auth_session`, `login_attempt`, `refresh_token`, `refresh_token_family` | +16 each | sign-ins of the walk and probes |

## 10. Regression — one run, on the final source, after the last edit

All backend and browser tests run against the isolated test schema `call360_test`, never development.

| Check | Result |
|---|---|
| Backend suite (includes the evaluator tests, golden 82 survey runs and 14 plans, permission and market-isolation tests) | **1,075 passed**, 0 failed |
| Golden fixtures and expectations | not modified |
| Ruff / Mypy (136 source files) | clean / clean |
| OpenAPI regeneration | byte-identical; SHA-256 `13eb5190b264ab0c405e97334238832162c8206b7b2c226ac70b636e27412766` (unchanged from APPL-X3) |
| Frontend client check against that OpenAPI | pass |
| Frontend lint / type check / production build | clean / clean / built |
| Frontend unit tests | **636 passed** (42 files) |
| Applicability browser suite | **26 passed** (24 earlier + 2 new D-418 tests) |
| Persisted browser suite | **34 passed** |
| Prototype browser suite | **13 passed** |
| Standard browser suite | **33 passed** |
| Specifications validator | pass |
| Development database during the regression | no table changed; revision `0039` |

- No test was weakened; no timeout was raised; no golden expectation changed. Tests changed: the graph test gained
  the on-screen assertions; X3.8 gained the archive / restore steps; `zz-d418.appl.ts` is new.
- **Intermittent failures in this run: none.** During development of the new measurement test one run failed
  because the gallery really was read twice — a defect, fixed (§8.4), not a flake.
- The voice timing test passed in this run. That is not a fix; Voice Studio was not touched.
- The backend log has no summary line captured; the count is the 1,075 pass marks with no failure or error mark and
  exit code 0.
- Outputs: `docs/acceptance/evidence/APPL-X3/development/test-output/`; inventories (before, after migration,
  final): `…/development/x3dev_*.json`.

## 11. Not tested, or weak

- No person performed a task; no screen reader was used.
- Journey F in development used one identity in two sessions.
- Restore, scale policies and adopt-newer-survey-version were exercised in the test environment only.
- Variable / profile adoption in the browser is still exercised for conditions only (D-418 list).
- The original D-418 failure cannot be proven to be the race now fixed.

## 12. Stop

Development enablement and verification are complete. APPL-X4 (`67_…`) is an assessment only. Not started: APPL-X4,
APP-1a, OPS-1, VOICE-1, legacy retirement. Nothing committed or pushed.

