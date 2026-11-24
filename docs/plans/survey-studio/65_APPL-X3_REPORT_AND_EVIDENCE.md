# APPL-X3 — persistent Applicability Policies: report and evidence

**Status: BUILT AND VERIFIED ON THE ISOLATED TEST SCHEMA 2026-11-24. Stopped for product-owner acceptance.**
Local development is untouched: still at `0038`, policies setting off, no policy table. Nothing is committed.
APPL-X4, APP-1a, OPS-1, VOICE-1 and legacy retirement were not started.

Technical verification on synthetic data. It does not establish operational readiness, approved Compliance rules
or verified human usability: no person performed a task and no screen reader was used.

Specification: `64_…`. Decisions: D-411 … D-418. Evidence: `docs/acceptance/evidence/APPL-X3/`.

---

## 1. Final acceptance criterion

> A business user must be able to create an Applicability Policy with real published Survey Studio surveys, save
> it, close the browser, reopen it later, edit the same policy, and obtain exactly the same deterministic selection
> results from the same frozen dependency and fact snapshots.

| | Shown by | Result |
|---|---|---|
| create a policy with real published surveys | journey X3.1: named, coded, a published condition → Survey A | **met** |
| save it | X3.1: "Draft saved · revision 2" | **met** |
| close the browser, reopen later | X3.1: the browser context is closed; a new one signs in; the gallery lists it with its history; the designer shows the same requirement, the same pinned survey version | **met** |
| edit the same policy | X3.1: two more requirements added and saved; X3.2: replacement | **met** |
| exactly the same results from the same snapshots | X3.1: the policy fingerprint of the saved revision is identical after a reload and in another person's session; backend: the saved evaluation equals the evaluator's own output plan for plan, and repeats byte for byte | **met** |
| intuitive, consistent with Survey Studio | the Card Composer is unchanged; one save bar; not measured with people | **built; not measured** |
| no legacy rule, binding or group created or modified | nothing in this code reads or writes them; test-schema digests of every non-policy table unchanged by the migration and by saving policies (audit trail apart) | **met** |

## 2. Stop conditions (Part 18) — none occurred

| Condition | Checked | |
|---|---|---|
| test database not at the expected migration | `0038_applicability_library` before starting | clear |
| the migration would alter protected legacy tables | it alters no existing table; every other table byte-identical after up, down, failed up, up | clear |
| a dependency cannot be pinned reproducibly | published versions: yes, by id and fingerprint. **Draft revisions: only while they do not move** — an earlier draft text is not kept, so a moved draft is reported and evaluation refused rather than reproduced (`64_…` §3.1). I judged this within the ruling ("report that its intended revision is stale and require reconciliation"), not a stop; it is the first thing I would ask the owner to confirm (D-416(b)) | **see note** |
| the persisted evaluator disagrees with the existing one | tested directly: every plan of the saved evaluation equals `evaluator.evaluate` on the same workspace and document; fingerprints equal | clear |
| a feature needs unapproved Compliance policy | none | clear |
| operational case or voice changes needed | none | clear |

## 3. Owner rulings — as implemented

| | Ruling | Implemented |
|---|---|---|
| X3-1 | exact dependency versions, never the latest; adoption deliberate and undoable; a changed draft reported and reconciled | `64_…` §2–3. Journeys X3.3, X3.4; backend tests |
| X3-2 | do not redesign the library lifecycle; the policy keeps its own intent | the library is unchanged; the policy's pins are its own |
| X3-3 | `survey.read` + `applicability.read / edit`; no new permission; no role widened | no permission added by `0039`; every policy operation requires both families |
| X3-4 | persisted endpoints authoritative; remove redundant prototype operations only once all callers moved | saved policies use `evaluate`, `preview`, `inspect`. **Nothing was removed**: the in-tab mode (local development) still calls all four (`64_…` §6) |
| X3-5 | patterns stay; choosing one creates a genuine saved draft; no simulated published policy in the database | patterns, copies and the scale examples create saved drafts; nothing is seeded; no "published" policy exists anywhere |
| X3-6 | a name before a permanent code; suggestion; review; uniqueness; market-scoped; says it is immutable | policies and profiles. Journey X3.1 |

## 4. What the tests prove

`Call360-backend/tests/test_applicability_policies.py`, 9 tests on the test schema.

| Required | Result |
|---|---|
| saved and reopened | the document and snapshot are identical in a new session and for another person; unknown fields are not stored |
| optimistic concurrency | a stale save is refused with who saved and the current revision; table digests unchanged |
| duplicate identity | code taken, whatever the case, per market |
| deterministic evaluation | the five cases (ILP only, NFTF only, both, neither, NFTF unknown); the same run twice is equal; **equal to the evaluator's own result**; replacement saved and re-evaluated; an unsaved what-if is marked `PREVIEW`, compared with the saved draft, and saves nothing |
| pins never move | after version 2 of a condition and of a variable are published: same document, same snapshot, same result, same fingerprint; both offered; adopting the condition does not adopt the variable; `PIN_DIFFERS` reported; adoption reverted restores the exact snapshot |
| draft dependency | allowed; reported per requirement; "not ready for publication"; a changed draft → `DEPENDENCY_STALE`, as a preview too; reconciled by moving the pin; a draft since published is reported, not silently read |
| invalid references | a survey version that does not exist, a wrong content or manifest fingerprint, a wrong number, a wrong code; a variable or condition version never published; a reference with no version; a draft revision that never existed — all refused, nothing written |
| market isolation | another market's policy: 404 on six operations (read, save, evaluate, preview, inspect, archive), in both directions; its library and its surveys are not usable; usage discloses nothing |
| transactional consistency | a failure forced after the rows are written leaves nothing; rows equal the stored snapshot after every save |
| database constraints | fourteen direct SQL attempts refused: identity, revision, deletion, history, edited dependency rows, references that name nothing (foreign keys), wrong kind, another market, a malformed row |
| published assets immutable | digests of every library version and every Survey Studio version unchanged by all of the above |
| permissions | no session 401; survey-only and applicability-without-survey people 403; only an editor who also reads surveys may create or save; CSRF |
| archive | needs a reason and the current revision; out of the gallery; restorable; never deleted |
| migration | `64_…` §8 |

## 5. Browser journeys — `e2e/applicability/saved-policies.appl.ts`

Real browser, real backend, test database, real signed-in people. Screenshots `evidence/APPL-X3/screens/70 – 95`.

| Journey | What is shown | Screens |
|---|---|---|
| A — blank persisted policy | sign in; create; name, then a suggested code that is reviewed and changed; a duplicate code refused; a requirement with a published condition and published Survey A; save; **the browser is closed**; a new session signs in; the gallery lists it with its history; reopened exactly as saved | 70 – 74 |
| B — joined ILP / NFTF | ILP → A, NFTF → B, ILP AND NFTF → C on the real showcase versions; saved; the five cases evaluated by the server; exact versions and fingerprints in the dependency panel; the same fingerprint after a reload and for another person; the matrix and the graph on the same saved document | 75 – 79 |
| C — explicit replacement | C replaces A and B; saved, reloaded, evaluated; and undo after a save marks the draft unsaved without pretending the save was reversed | 80 |
| D — reusable dependency changes | a condition published as version 1, used by a policy; version 2 published by three people; the policy reopened: version 1 pinned, same fingerprint, version 2 offered on the dependency and on the requirement; adopted; the manifest fingerprint changes; undone; adopted again and saved; reloaded | 81, 82 |
| E — draft dependency | a draft condition in a saved policy; reloaded: "Draft contains unpublished dependencies — not ready for publication"; the readiness page offers no submission; the condition's draft changed: "changed", **not evaluated**; reconciled and saved | 83 – 85 |
| F — concurrency | two signed-in people; the second save refused; who, which revision, what differs; their own text still on screen; "load theirs", and the other way round "save mine as the next revision" | 86 |
| G — cross-product navigation | from a saved policy with an unsaved edit: preview of the published survey, opened in Survey Studio (its modules), back to the same policy with the edit intact; Survey Studio's "where used" lists the saved policy from Call360 | 87 – 89 |
| H — security | read only for a person who may not edit; saved policies closed without the permissions; by direct requests: forbidden writes, a stale revision, an invalid survey version, an invalid pin, another market, an unknown id — and the policy unchanged afterwards | 90, 91 |
| I — scale and accessibility | 20, 50 and 100 requirements saved and reloaded; graph focus inside the viewport **at 0.6 zoom or more**; a 140-character name readable in full; the Condition Lab's focused mode; keyboard reordering; four widths; accessibility scan | 92 – 95 |

The nine APPL-X1R journeys and the seven APPL-X2 journeys were re-run **on saved policies** and pass, with these
steps changed because their subject no longer exists: the seeded "published (simulated)" showcase policy; the
simulated draft-against-published impact; the simulated approval page; the "in this tab only" labels of policies.

## 6. Carried-forward UX items (Part 12)

| | |
|---|---|
| 1 long titles | the designer's title grows instead of being cut; the full name is in the gallery, the switcher and a tooltip. Tested with 140 characters |
| 2 name before code | policies and profiles (§3, X3-6) |
| 3 nested Condition Lab | a focused mode: the builder alone at full width, the live test beneath it (screenshot 94) |
| 4 large graph neighbourhoods | a neighbourhood of a large policy no longer draws the two book-end nodes ("the application", "the selection"): four columns instead of six, so it fits at 0.6 zoom or more beside the open inspector (was about 0.5). The blank-canvas defect did not return: the assertions of APPL-X2 still pass |
| 5 identity and persona | with saved policies the persona switch is gone; the header names the signed-in person |
| 6 one product | the policy's save bar is the library item's bar; the same words, the same conflict choices |
| 7 scenarios | "In this tab only" in the header's status control and on the scenario screens |

## 7. Regression

Run on 2026-11-24 against the isolated test schema. Outputs: `docs/acceptance/evidence/APPL-X3/`.

| Check | Result |
|---|---|
| Backend suite | **1,075 passed, 0 failed** (1,066 before, plus the 9 policy tests) |
| Golden 82 runs and 14 plans | pass; **no fixture or expectation file is modified** |
| Evaluator tests | the 21 of `test_survey_applicability.py` pass unchanged; the evaluator was not edited |
| Ruff (282 files), Mypy (136 files) | clean |
| OpenAPI | 10 operations and 15 schemas added, nothing else changed; SHA-256 `13eb5190b264ab0c405e97334238832162c8206b7b2c226ac70b636e27412766`; the frontend client matches |
| Frontend unit tests | **636 passed** |
| Frontend lint, types, production build | clean |
| Applicability browser suite | **24 passed**: X1R.1 – 9, X2.1 – 7, X3.1 – 8 |
| Persisted / prototype / standard browser suites | **34 / 13 / 33 passed** |
| Accessibility | no serious or critical violation (axe, WCAG 2.2 AA rules) on the designer with its dependency panel, the readiness page, the gallery and the create dialog, and on the screens of APPL-X1R and APPL-X2. Not a screen-reader test |
| Widths | no sideways overflow at 1440, 1280, 900 and 390 on the gallery, a saved policy and its readiness page |
| Specifications validators | pass |
| Development | read-only check at the end: `0038_applicability_library`, 0 policy tables, policies setting off, library on; the backend answers ready |

**Failures on the way, and what each was.** Nothing was hidden and no assertion was weakened to pass.

1. **First full backend run: 11 failures, 3 causes.** The `0038` migration test had to learn that an empty `0039`
   rolls back before `0038` refuses (it then left the schema at `0038`, which made the eight policy tests after it
   fail too); the contract-size test counts the new operations and schemas; and the test that nothing outside Survey
   Studio references its tables now states the one new reference (D-417). Expectations updated; no behaviour
   assertion weakened.
2. **A real performance defect, found by running the three journey files back to back.** Creating or saving a
   policy re-read *every* saved policy, and each read ran the whole server-side inspection — slow once the
   100-requirement examples existed, so the designer did not open in time. My first hypothesis (the request limit)
   was **wrong**: I added a guard that fails a journey if any request is refused as too frequent, and none was.
   Fixed properly: a read runs the inspection only when asked (`?inspection=false`), and a save re-reads only the
   policy that was saved. I also separated the limit for saving from the limit for inspecting and previewing, which
   is right on its own but was not the cause.
3. **One intermittent failure, cause NOT established.** After that fix, one full run failed once at X2.6: after
   "20 requirements" was clicked in the gallery, the designer did not open within 15 seconds. Three later full or
   partial runs passed (16 of 16, then 24 of 24 twice), with timing capture that logged no policy request slower
   than four seconds. I could not reproduce it and do not know its cause. **It is open, not fixed** (D-418).
4. The voice timing test passed. As ruled (D-406), that is not a fix; nothing in Voice Studio was touched.

**Order of runs.** The persisted, prototype and standard browser suites ran before the last two changes (the light
policy read and the separate limits — policy API and applicability frontend only, which those suites do not load).
The backend suite, static checks, unit tests, build and the applicability suite were run again afterwards.

**Existing tests changed in this checkpoint:** the head-revision and contract-size pins; the older migration tests'
table lists; the foreign-key test (D-417); and, in the earlier browser journeys, the steps whose subject no longer
exists with saved policies (§5). The limiter split and `?inspection=false` are additions to APPL-X3's own API.

## 8. What remains untested or weak

* **No person and no screen reader.** Every usability statement is mechanical.
* **A pinned draft is reproducible only while it does not move** (§2). This is the one place where "the same frozen
  dependency snapshot" is refused rather than reproduced.
* **Policy evaluation on the Scenarios page with a profile the policy does not pin** reads that profile at its
  published version, as scenario input; it is not part of the policy's snapshot.
* **Adoption of a newer variable or profile version** is tested through the API and built in the panel; the browser
  journey exercises it for a condition only.
* **"Restore" of an archived policy** exists in the API and is tested there; the gallery has no control for it yet.
* **The compare view** still compares what two policies say, not what they select.
* **Scale**: 100 requirements save and reload as one document; no limit on the number of policies or on concurrent
  editors was tested.
* **Development**: nothing was run there. Its frontend still shows policies in the tab.
* A mistake of mine during the work: on this case-insensitive filesystem I created a file whose name differed only
  by case from the existing gallery file and overwrote it. It was uncommitted. I restored it from the session
  record of the command that had created it and verified all 120 lines against a listing taken an hour earlier.
  Nothing was lost; the new file has a distinct name.

## 9. For the owner

1. Acceptance of APPL-X3 on the test schema.
2. D-416: (a) one version of each variable per evaluation, with `PIN_DIFFERS` reported; (b) a moved draft pin is
   refused, not reproduced; (c) no prototype operation removed yet.
3. Whether to authorise `0039` on local development (`64_…` §8.1). No identity or permission change is needed.

Nothing further is authorised.
