# 69 — APPL-X4a report and evidence

**Built and verified on the isolated test schema, 2026-11-24. Awaiting owner acceptance. Nothing committed.**
Synthetic data only. Simulation only. Local development is untouched: still at `0039_applicability_policy`, no APPL-X4a
table, the scenarios setting off, backend healthy (checked after the build, §9).
Architecture: `68_…`. Next-checkpoint specification: `70_…` (not started).

---

## 1. The final success criterion, part by part

| The owner's criterion | Shown by |
|---|---|
| Create synthetic scenarios from scratch | X4.1 (template), X4.2 (variant, generated combination offered), backend tests |
| Save and reopen after a browser restart | X4.1: browser context closed, new sign-in, identical facts, snapshot, scenario and result fingerprints |
| Organise into regression suites | X4.3: suite created, seven members added, reordered, saved, page reloaded |
| Explicitly define expected outcomes | X4.3: every expectation stated survey by survey on the screen and confirmed; stored `source: AUTHORED` |
| Run against real saved policies | X4.3: recorded run, 7 of 7 passed, against saved policy revision 1 |
| Inspect immutable recorded evidence | X4.6: run reads identically after the policy, a scenario and a profile changed; re-evaluated from its record |
| Which published surveys apply and why | live plan with the path per survey; preview of the published Survey Studio content (X4.1) |
| Distinguish expected from actual; correct failures | X4.4: FAILED with the two exact differences and the requirement links; corrected explicitly; PASSED |
| Understand coverage | X4.3 / X4.8: requirement table, gaps as suggestions, the "not exhaustive" label |
| No legacy assignment object or operational record changed | backend test: across a whole flow the only other table that changes is `audit_event` |

## 2. What was built

- **Backend** (`Call360-backend`): migration `0040_applicability_scenarios`; `app/domain/survey/applicability/scenarios.py`;
  `app/api/applicability_scenarios.py` (22 operations); setting `applicability_scenarios_enabled`; `MIGRATION_HEAD`
  `0040`; `tests/test_applicability_scenarios.py` (11 tests). The evaluator (`logic.py`, `evaluator.py`,
  `analysis.py`) and `policies.py` are **unchanged**; `rule_engine.py`, `answer_evaluation.py`, `finding_engine.py`
  untouched.
- **Frontend** (`Call360-frontend`): `scenarioApi.ts`, `ScenarioStudio.tsx`, `SuiteBuilder.tsx`, `RunHistory.tsx`,
  styles; setting `VITE_APPLICABILITY_SCENARIOS`; a separate Playwright configuration `playwright.scenarios.config.ts`
  with `e2e/scenarios/studio.scn.ts` (10 journeys). With the setting off, step 4 is the accepted in-tab lab,
  unchanged — which is why the accepted applicability journeys run unmodified under their own configuration.
- **OpenAPI**: 22 operations and 35 schemas added, nothing removed.

## 3. Journeys (real browser, real backend, test database)

| Journey | Test | Result |
|---|---|---|
| A save and reopen | X4.1 | pass |
| B variants | X4.2 | pass |
| C suite creation and run | X4.3 | pass |
| D failure explanation | X4.4 | pass |
| E exact dependency pinning | X4.5 | pass |
| F historical evaluation | X4.6 | pass |
| G unknown values | X4.7 | pass |
| H scale | X4.8 | pass |
| I security | X4.9 | pass |
| keyboard, four widths, accessibility | X4.10 | pass (see §8) |
| J regression | §10 | — |

Screens: `docs/acceptance/evidence/APPL-X4a/screens/` (40 files; `01`–`28` follow the journeys, `30-*` are the four
widths).

### 3.1 Details worth reading

- **A.** The template "ILP only" says nothing about riders, and the policy reads them. The first result is therefore
  honestly **unresolved**, with Survey E pending and "Selected riders" named. Giving "no rider" explicitly resolves it.
  The same incompleteness made the first suite run of my own journey fail (5 of 7) until the scenario was completed —
  the studio caught a real gap in a test scenario.
- **B.** One changed fact (NFTF: no → yes): Surveys B and C added; after saving, the server names the two requirements
  that are the reason. Undo, reset to baseline and discard all return to the saved state.
- **D.** After the failing run the stored expectation is still the wrong one (read back through the API): nothing was
  corrected automatically. "Use the current result as a proposal" leaves the member "Proposal — confirm", shows "A
  result is not proof that it is right", and **disables Save** until confirmed. Three runs are on record: passed,
  failed, passed.
- **E.** Profile `nftf_extension` v2 published in the test library by three people. The saved scenario keeps v1 with
  identical fingerprints; v2 is offered; adopt → undo (v1, nothing to save) → adopt → save → reload (v2). The policy
  still pins v1: in a gating suite the run is **"Test definition invalid — reconcile"**; in an exploratory suite it is
  evaluated with the scenario's version, flagged, and never counts.
- **F.** After the policy was changed (C replaces A and B), a suite scenario edited, and a profile republished: the
  earlier run's head, results and plans are byte-identical through the API; the screen shows the same fingerprints;
  "Re-evaluate from the record" reproduces 7 of 7. Against the current draft (not recorded): the differences and
  their reasons. A new run is a fourth record; the first is unchanged. Two runs compared: changed fact, added survey,
  replaced requirements.
- **G.** Not known, not provided and invalid are three displayed states; an invalid value is stored for testing,
  reported, and treated as not known — never as "no". The states on screen equal the evaluator's when asked directly.

## 4. Reference showcase (the five real published surveys)

| # | Scenario | Expected and recorded |
|---|---|---|
| 1 | ILP only | A |
| 2 | NFTF only | B |
| 3 | ILP with NFTF | A + B + C |
| 4 | Neither | no survey |
| 5 | ILP, NFTF not known | unresolved; A selected; B and C pending |
| 6 | ILP with NFTF, policy with explicit replacement | C alone (shown as the comparison and the second run of X4.6; backend test) |
| 7 | Replacement sale | A + D |
| 8 | Critical-illness rider | E |
| 9 | Intentionally failing expectation | ILP only expected B → FAILED with both differences |
| 10 | Changed profile dependency | the pinned-profile scenario of journey E |

Every survey reference is an exact published Survey Studio version (id and both fingerprints), fetched from Survey
Studio by the journey's setup. No placeholder catalogue.

## 5. Migration and rollback evidence (test schema, populated)

`test_zz_migration_0040_…`: on a schema holding accounts, a published library, three published surveys and a saved
policy —

1. head `0040`; exactly 7 tables and 6 functions; 14 validated foreign keys;
2. downgrade while empty: all removed; every other table identical in count and content digest; no permission change;
3. forced failure at the last statement: nothing of the migration left behind; other tables identical;
4. upgrade again: identical objects; other tables identical;
5. with a saved scenario: downgrade refused; with a recorded run: refused; the run's fingerprint unchanged and
   `verify` still reproduces it;
6. the audit chain verifies.

The two older migration tests (`0038`, `0039`) were adjusted for the revision now above them (it rolls back first
while empty). No assertion about behaviour was weakened.

Database guards exercised directly (each refused): update or delete a run; update or delete a result; add a result to
a recorded run; delete a scenario or a suite; change a scenario's code; edit history; a cross-market suite member.

## 6. Security and market isolation

- Read-only people (reader, checker, publisher) read, evaluate and compare; every create, save, archive and run is
  `403`. Without `survey.read`, or with only survey permissions: `403` on every operation.
- Missing or wrong CSRF token: `403` on writes and on computations.
- Another market: its scenarios, suites and runs answer `404` on every operation; a scenario of another market
  cannot be evaluated against, or added to a suite of, this market's policy; another market's variable cannot be
  named.
- Stale revision, invalid pin, unknown fact, unconfirmed expectation, oversized suite, bad idempotency key: refused
  with their codes; nothing changed.
- A recorded run: `PUT` / `PATCH` / `DELETE` → `405`.
- The browser journey X4.9 shows the same with real sign-ins, plus two editors (stale save refused, nothing
  overwritten) and a person with no applicability permission (studio closed).

## 7. Performance and scale

Measured in the tests, on this machine, test database:

| Measure | Result |
|---|---|
| Backend: suite of 10 / 50 / 200 scenarios × policy of 100 requirements, run and recorded | 0.17 s / 0.52 s / 2.1 s wall (119 / 360 / 1,495 ms evaluating) |
| Backend: 200-result run verified from its record | reproduced |
| Browser: 120 scenarios created through the API | about 2.0 s |
| Browser: gallery of 120 listed | about 0.45 s; **at most the one open scenario is evaluated** to draw it |
| Browser: suite of 120 × 100 requirements run and recorded | about 2.5 s on screen (about 0.9 s evaluating) |

- Lists page at 50 (at most 100); a run's results page at 50; each full plan is read on its own.
- D-418's lesson applied: nothing can be created until its list is read (asserted in X4.1).
- No timeout was raised to make a test pass.
- **Not measured:** more than 200 scenarios in one suite (refused by design), concurrent runs, a database of
  production size.

## 8. Accessibility and layout

- 1440, 1280, 900 and 390 px: no sideways scrolling of the page on the scenario, suite and run pages.
- Automated scan (WCAG 2.0–2.2 A / AA): **no serious or critical finding inside the Scenario studio.** One real
  finding was found and fixed on the way (contrast of the version label on a selected chip).
- **Reported, not fixed, outside this checkpoint:** at 390 px the application's outer shell has icon-only navigation
  links and an account button without accessible names (`link-name`, `button-name`). They are in the shared shell, not
  in the studio.
- Keyboard: a fact changed, a scenario saved, a member reordered and an expectation form opened and entered.
- **Not done:** no person performed a task; no screen reader was used.

## 9. Defects found and fixed while building

| Found by | Defect | Fix |
|---|---|---|
| X4.2 | "Discard changes" left the editor on "Reading…" when the saved revision was unchanged | the editor is set from what was re-read, always |
| screenshot | a failed run still showed "Meaningful for publication" | a run that did not pass is never meaningful; reason stated |
| screenshot | new style name collided with an existing one (odd oval border) | renamed |
| X4.10 | phone-width overflow on suite and run pages (long survey names, a long verdict label, the compare selector) | wrapping and shrinking rules |
| X4.10 | contrast on a selected chip's version label | fixed |
| backend suite | schema name `ApplicabilityEvent` collided with APPL-X2's | renamed `ApplicabilityScenarioEvent` |
| my own test | a variable named like the function's loop variable hid the "run passed" argument | renamed |

Development after the build: revision `0039_applicability_policy`; 0 APPL-X4a tables; scenarios setting off; no
scenario route served; readiness `200`.

## 10. Regression — one run, on the final source, after the last edit (journey J)

All backend and browser tests ran against the isolated test schema `call360_test`, never development.

| Check | Result |
|---|---|
| Backend suite (evaluator tests, golden 82 survey runs and 14 plans, permissions, markets, migrations included) | **1,087 tests; exit 0; no failure or error** |
| Golden fixtures and expectations | not modified |
| Evaluator (`logic.py`, `evaluator.py`, `analysis.py`), `policies.py` | not modified |
| Ruff, format check, Mypy (138 source files) | clean |
| OpenAPI regeneration | byte-identical; SHA-256 `50d663987a1c6ac231ee5c090b72b8435566a4b00fbba14805fedab4ddb1a9cc` |
| Frontend client check against that OpenAPI | pass |
| Frontend lint / type check / production build | clean / clean / built |
| Frontend unit tests | **636 passed** (42 files) |
| Scenario studio browser suite (new) | **10 passed** |
| Applicability browser suite (accepted X1R, X2, X3 journeys; scenarios setting off) | **26 passed** |
| Persisted browser suite | **34 passed** |
| Prototype browser suite | **13 passed** |
| Standard browser suite | **33 passed** |
| Specifications validator | pass |
| Development database | revision `0039`; 0 APPL-X4a tables; unchanged |

- **Intermittent failures in this run: none.** The D-418 watch: its two tests passed; the symptom did not recur.
- **The first full backend run during the build failed** in 15 tests, honestly recorded: two older migration tests
  and one settings test needed the new revision above them accounted for, and one failure left the test schema
  below the head so that the new module's tests failed after it; one was a real schema-name collision in the
  contract. All were corrected at the cause; the final run above is clean.
- Older tests changed: head pins and contract counts (+22 operations, +35 schemas); the `0038` / `0039` migration
  tests (the revision above rolls back first while empty; the table lists exclude the new tables); one `TRUNCATE`
  in a test fixture gained `CASCADE` because of the new foreign keys. No behavioural assertion was weakened; no
  golden expectation and no timeout was changed.
- The voice timing test passed. That is not a fix; Voice Studio was not touched.
- The backend log has no summary line; the result is the exit code 0 with no `FAILED` or `ERROR` line.
- Outputs: `docs/acceptance/evidence/APPL-X4a/test-output/`.

## 11. Not tested, or weak

- No person performed a task; no screen reader was used.
- Scenario and suite creation by people at scale was not observed; the scale data was created through the API.
- Restoring an archived scenario or suite has no screen control (API only), and is covered by backend tests only.
- The designer's live-preview picker is not yet fed by saved scenarios (`68_…` §9).
- The pattern check for real-looking identifiers is a safeguard, not a guarantee.
- Out-of-scope and scope-unresolved expectations, choose-one alternatives and shared-delivery overlaps are covered by
  the coverage code and its rules, but the showcase policy has no scope and no choose-one requirement, so those
  branches were not exercised in a browser journey.
- Nothing was run on development.

## 12. Stop

APPL-X4a is built and verified on the isolated test schema only. Not started: the `0040` development migration,
APPL-X4b, APP-1a, OPS-1, VOICE-1, legacy retirement. Nothing committed or pushed.

