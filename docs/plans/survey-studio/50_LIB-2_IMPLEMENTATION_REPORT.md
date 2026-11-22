# LIB-2 — Independent reusable modules: implementation report

**Status: ACCEPTED by the owner as TECHNICALLY VERIFIED on 2026-11-22 for simulation-only standalone module
authoring (D-344) — "This is not business UX, screen-reader, Compliance or production acceptance." Migration `0036`
was then applied to development on the owner's authorisation (D-348; §10 below).**
**Synthetic data only.** No published asset was modified; no rule, evaluation, finding, assignment or execution
semantics changed; no golden fixture or expectation was touched. Migration `0036` exists and is tested on the test
schema; **it is not applied to development**, which stays at `0035`. Technical verification is not a business UX
sign-off, a screen-reader sign-off or approval of anything for a call.

Authorisation: the owner's message of 2026-11-22, "Accept UX-HOME-1 + NAV-1 and Implement LIB-2". Companion: `49_…`
(assessment, architecture decisions, contract, migration assessment, unresolved questions), contract `04_…` §22,
decisions D-330…D-343.

---

## 1. The acceptance criterion

> A business user can create a reusable module from scratch, design its complete question flow, test and publish it
> through governance, and use the same published module in multiple surveys — without ever having to create a
> temporary survey solely to author the module.

Met, in one real-browser run against the real backend and database (§4): a module was created from the homepage,
given yes/no, single-choice and multi-select questions, per-answer branches and a condition, saved and reopened,
tested by the Python engine, published by three different people, found in the gallery and the inspector, added to
two surveys that each pin the exact published revision, and superseded by a second revision that changed neither
survey. No survey was created to author it; the two surveys in the run are its consumers.

## 2. Part A — closing UX-HOME-1 + NAV-1

Acceptance recorded (D-330). D-321…D-329 reconciled one by one (D-331 and its table): two choices are superseded by
the owner's rulings, two remain unruled technical limitations, none is a policy question.

| Issue | What changed |
|---|---|
| 1. "Awaiting my action" against "awaiting someone else" | two separate panels. **Waiting for you** — a review or publication the rules and your permissions allow now, each with its button. **Waiting for someone else** — what you submitted, tagged "Not your step", saying whether it needs a reviewer or a publisher. The count tile reads "Surveys in review" with "n awaiting a reviewer · n awaiting a publisher" |
| 2. Create Module must not imply creation | where standalone modules are on, **Create module creates a module**. Where they are off (development today), the same place reads **How modules are made** and opens the explanation. In the gallery the per-kind button reads "How questions / conditions / answer sets are made" |
| 3. Keyboard focus in the inspector drawers | focus moves into the drawer; Tab and Shift+Tab stay inside; Escape closes; focus returns to the card or row that opened it. Module Inspector and Survey overview. Unit-tested and exercised in the browser (40 Tab presses stay inside) |
| 4. 1440, 1280 and 900 px | homepage, Module Builder and module test checked at all three for sideways scroll. The editor's bar (breadcrumb, Save, tools) pushed the page sideways below 1000 px; it now wraps onto a second row |
| 5. Suites after the final stylesheet change | all re-run after the last source change — §6 |

## 3. What was built

### Backend

| | |
|---|---|
| Migration `0036_survey_module_authoring` | one column `survey_definition.artifact_kind` (`SURVEY` default, `MODULE`), a trigger that it never changes, and a database guard refusing a simulation, call plan or assignment binding that names a module |
| Setting | `survey_module_authoring_enabled`, off by default, on only with the library |
| `app/domain/survey/store.py` | `create_module`, `module`, `module_frame`, the frame rule applied at every save and at submission, `origin_of`; surveys and published versions are read by kind; a module's own publication is not counted as a use |
| `app/domain/survey/module_test.py` | the one-module test: frame, validation, `execute_inputs`, nothing written |
| `app/api/survey_modules.py` | four operations (contract §22.3) |
| Unchanged | the validator, the engine, the documents, the lifecycle trigger, every existing operation's behaviour for a survey |

### Frontend

| | |
|---|---|
| Module Builder | `/survey-studio/modules/{code}` — the existing guided builder and graph on the module's own draft; name, one-line description and kind edited in place; Save, Undo, the library drawer (questions, conditions, answer sets) and immediate validation as in a survey; a preview of the library card; "Start revision n+1" on a frozen revision |
| Test | `/survey-studio/modules/{code}/test` — facts the module's conditions read, the exact wording, typed answers, refusals with their code, "Take back the last answer", "Start again", "Replay the same inputs", the execution trace, the wording delivered, the exact versions run. It tests what is **saved**, and says so when there are unsaved changes |
| Test of any published module | `/survey-studio/module-tests/{code}/{revision}`, from the inspector — also for modules written inside surveys |
| Review and publish | the existing review, candidate and version screens under the module's address, with the library card and what publishing does |
| Homepage | Create module (real); "Modules in progress"; the two waiting panels |
| Building blocks | "Create module"; an "In progress — not in the library yet" list; a standalone module's card says "Authored on its own" |
| Module Inspector | provenance of its own ("Authored on its own… not written inside a survey"), governance of its own publication (who submitted, approved, published), the draft or candidate now in progress, consuming surveys without its own record, Test this module, Open in the Module Builder |
| Survey Composer | the published module is in the existing library drawer ("published on its own, release 1.0"), added pinned and locked; the survey author routes its endings; "Edit a copy for this survey" unchanged |

### Not built

A second registry, lifecycle, document format, branching model or engine. A JavaScript engine: the test page shows
only what the Python engine returned. Independent authoring of questions, conditions and answer sets (`49_…` §8).

## 4. The twenty demonstrations

One real-browser run (`e2e/persisted/zzzzz-lib2.persisted.ts`, four serial tests) and the backend tests
(`tests/test_survey_lib2.py`, eleven tests). Screenshots: `docs/acceptance/evidence/LIB-2/`.

| # | Demonstration | Browser | Backend test | Screenshot |
|---|---|---|---|---|
| 1 | Create a module without creating a survey | the list of surveys is unchanged; the module is not in it | `…created_without_a_survey…` | 01, 02 |
| 2 | Yes/No, single-choice and multi-select questions | built in the guided builder | fixtures F3, F4, G5 saved | 04 |
| 3 | Different next questions for different answers | Q1 No → ends; Q2 Cash → a follow-up question | F3 | 04, 05 |
| 4 | A reusable condition | "Annual premium is above 12,000" decides a branch; saved as a condition of its own | G5 | 03 |
| 5 | A valid module exit | three endings; the frame holds one route per ending | frame rule, five refusals | 04 |
| 6 | Save and reopen | saved, page reloaded, same module | read back equal | 06, 07 |
| 7 | Tested by the Python engine | engine contract shown; source "saved draft" | `…tested_by_the_engine…` | 08 |
| 8 | A branching path and an invalid response | Cash and Giro lead to different questions; no answer → `CHOICE_REQUIRED`, same question | the same | 09, 10, 11, 12 |
| 9 | Submit, approve, publish — three identities | author, checker, publisher; three names in the history | three distinct actors in the lifecycle | 13, 16, 17 |
| 10 | Unauthorised publication refused | maker 403; checker cannot publish; every-permission person cannot publish unapproved | self-review, self-publish, approver-publish, no permission | 14, 15 |
| 11 | Opened from the gallery | card "Authored on its own" | library card, `origin` | 18 |
| 12 | Module Inspector | own provenance, governance, six steps, logic graph, keyboard focus | — | 19, 20, 21 |
| 13 | Reused in two surveys | one from the composer's library, one from the inspector | two consumers | 22, 23, 24 |
| 14 | Both pin the exact published revision | manifest entry: code, revision 1, the published fingerprint | the same | 24 |
| 15 | A newer revision changes neither survey | content and manifest fingerprints of both versions unchanged | the same | 26, 27, 28 |
| 16 | Earlier revisions remain accessible | revision 1 inspected, compared with 2, tested | both in the library, both testable | 29 |
| 17 | Market isolation and permissions | another market: not found; a reader: no create, edit, test | 404 / 403 | 30, 31 |
| 18 | Survey-extracted modules still work | written inside a survey, published, inspected ("Published as part of…"), tested | `…inside_a_survey_are_unchanged…` | 32 |
| 19 | No callback, finding or disposition | a module's version cannot be simulated or planned; the list of surveys is unchanged | row counts unchanged; the database refuses a simulation row | — |
| 20 | Golden runs, plans and regressions | — | §6 | — |

## 5. Evidence

`docs/acceptance/evidence/LIB-2/`: `screens/` (forty-one screenshots of the run, including 1280 and 900 px),
`backend-lib2-tests.txt`, `backend-full.txt`, `playwright-persisted.txt`, `playwright-prototype.txt`,
`playwright-standard.txt`, `frontend-static.txt`, `openapi.txt`.

## 6. Regression — all run after the last source change

| Check | Result |
|---|---|
| Backend suite (`call360_test`) | **1,020 passed, 0 failed** — the 1,009 before and the 11 of `test_survey_lib2.py` |
| Golden fixtures | the 82 expected runs and 14 expected plans pass inside that suite; **no fixture or expectation file is modified** |
| Backend lint, format, types | clean (`ruff`, `mypy` on 127 files) |
| Frontend unit tests | **630 passed** (624 before; the frame, the next revision, the focus handling) |
| Frontend types, lint, build | clean |
| Playwright — persisted | **31 passed** (27 before and the 4 of LIB-2), run twice |
| Playwright — prototype | **13 passed** |
| Playwright — standard | **33 passed** |
| OpenAPI | additive: 275 operations (+4), 521 schemas (+9); the frontend's generated client matches |
| Specs validator | passes |
| Migration `0036` | up from `0035`; down and up on a populated schema with every governed row identical; downgrade refused with a standalone module present |

Order: the three Playwright suites, the unit tests and the build ran after the last frontend source change; the
backend suite ran after the last backend change. The persisted suite was then run once more, unchanged, to produce
the screenshots.

Existing tests changed, and why: the migration head is pinned in seven backend tests (now `0036`); the test that
lists which revision each setting needs gained the new setting; one migration test now expects a refused downgrade
to stop at `0035` after `0036` rolled back cleanly, and ignores the one new column when comparing structure; the
contract pins count four more operations and nine more schemas; the UX-HOME-1 browser journey now expects "Create
module" to open the create form and the inspector to offer the one-module test. **No golden fixture or expectation
was changed.**

## 7. Remaining gaps

| | Gap |
|---|---|
| G-1 | **Questions, conditions and answer sets cannot be authored on their own.** They are written inside a module (which needs no survey) and become reusable when it is published. Proposed LIB-3 (`49_…` §8) |
| G-2 | **A standalone module cannot be started as a copy of an existing module**, and a module written inside a survey cannot be turned into a standalone one. "Start revision n+1" works on a standalone module's own lineage; a survey-owned module's next revision is made in its survey, as before |
| G-3 | **Testing needs `survey.simulate`**, which an author does not hold by being an author (P-1, ruled: it stays so). *Corrected 2026-11-22:* the development author identity already holds it (D-349); this line first said no development identity did |
| G-4 | A test is not recorded: there is no saved history of test runs and no evidence that a module was tested before review (P-2) |
| G-5 | Multi-select follow-ups and rule-ordered routing are available in the builder and covered by the backend tests (fixtures F4, G4 shapes); the browser run configures per-answer branches and a condition, not follow-up queues |
| G-6 | A published module revision cannot be withdrawn or deprecated (P-5) |
| G-7 | The save counter in the editor's bar ("Revision 2") and the module's revision are different numbers and both say "revision" |
| G-8 | The execution trace names steps by their node identity ("step n2"), as the survey simulator does |
| G-9 | Search in the workspace is still in the browser; standalone drafts are found under "In progress", not by search |
| G-10 | No screen-reader test. The focus handling is keyboard-tested only |
| G-11 | Development has not been migrated, so the feature cannot be seen there yet (D-343) |

## 8. State

| | |
|---|---|
| Development database | `0035`, unchanged. Not migrated, reset or re-seeded. With the setting off, the development server runs this code unchanged against it |
| Repositories | uncommitted on top of the owner's own commits of UX-HOME-1 + NAV-1, made while this checkpoint was in progress (backend `725ceaa`, frontend `03df023`, specs `e8dc06b`). Nothing was staged, committed or pushed by the assistant |
| OpenAPI | SHA-256 `be340238b2b21bee61eebbbebae5e1e7b283329fa38197f758e3e896c236ea4f`; 275 operations, 521 schemas |
| To enable in development | the owner's authorisation is needed for: a backup, `0036` as one revision, `SURVEY_MODULE_AUTHORING_ENABLED=true`, and a decision on P-1 |

## 9. Stopped here for review

Nothing further is authorised. Open with the owner: D-338 (the wording of LIB-D-1), D-341 (P-1…P-8), D-342 (ten
choices), D-343 (development enablement), LIB-3.

## 10. Development enablement — 2026-11-22, after acceptance (D-348)

| Step | Result |
|---|---|
| Identity | database `Call360_db`, schema `call360`, PostgreSQL 15.12, revision `0035`; the only pending revision was `0036` |
| Inventory | 140 tables, 15,889 rows; 5 definitions, 5 drafts, 21 asset versions, 4 candidates, 3 versions, 15 lifecycle events, 43 dependency rows, 25 simulations, 19 call plans, 3 bindings — each with a SHA-256 digest |
| Backup | `call360_dev_before_0036_20261122.dump`, SHA-256 `a2e1b122de0ba46fbce897bf61a226d635275523749b3d695fc1efd38b6e8035`; 140 tables and 15,889 rows equal to the inventory; restore-to-SQL dry run clean |
| Migration | `0036` only. 138 of 140 tables byte-identical; the two that differ are the revision marker and `survey_definition` (the new column). Every governed digest identical. All five definitions `SURVEY`. Four triggers and two functions added; no permission |
| Round trip | `0036` → `0035` → `0036` with no module present: every table returned to exactly what it was |
| Existing behaviour | all 25 recorded simulations replayed to their recorded run; all 19 call plans reassembled to their recorded fingerprint; bindings and groups unchanged (`SG-ILP-HIGH-RISK v2` → `S-DEV-EVAL-SHARED` untouched) |
| Guards | a simulation, a call plan and an assignment binding naming a module, and any change of kind, are each refused by the database (tried in rolled-back transactions) |
| Protected data | no script, question, rule, finding, review, case, transcript, policy or party table changed. Outside the survey authoring tables only sign-in and audit rows were added |
| Setting | `SURVEY_MODULE_AUTHORING_ENABLED=true` in the gitignored `.env`; server restarted; ready |
| Permissions | none granted or changed (D-349) |
| Demonstration | the twelve steps in a real browser with `dev.survey.author`, `dev.survey.checker`, `dev.survey.publisher`: module `M-100007`, two published revisions; consumers `S-DEV-LIB2-ONE` and `S-DEV-LIB2-TWO`, each pinning revision 1 by fingerprint and unchanged after revision 2 |
| Guarded downgrade | with the module present, `alembic downgrade 0035…` refuses ("standalone modules exist"); the schema stayed at `0036` |
| Not done | no reset, no re-seed, no change to any binding, group, policy or mapping |

Evidence: `docs/acceptance/evidence/LIB-2/dev-migration-0036/` (four text files, twelve screenshots). Recovery:
`_db_backups/RESTORE.md`, "Rolling 0036 back".

