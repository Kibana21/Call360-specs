# APPL-X2 — governed reusable applicability libraries: report and evidence

**Status: BUILT AND VERIFIED ON THE ISOLATED TEST SCHEMA 2026-11-23. Stopped for the owner's review BEFORE any
development migration.** Local development is untouched: still at `0037`, library setting off, no applicability
table, no new identity, no new permission. Nothing is committed.

This is technical verification. It does not establish production readiness, approved insurance rules, operational
call eligibility or verified human usability. No person performed a task and no screen reader was used.

Specification: `60_…`. Acceptance of APPL-X1R and the decisions confirmed with it: D-393 … D-396.
Evidence: `docs/acceptance/evidence/APPL-X2/`.

---

## 1. The primary acceptance criterion

> A business user can create a reusable variable, compose it into an application profile, create a named AND/OR/NOT
> condition, submit it for three-person publication, and reuse its exact published version in the existing Survey
> Applicability Designer. The reusable assets must survive reload, preserve historical versions, enforce market
> isolation and provide a complete audit trail.

| Part | Shown by | Result |
|---|---|---|
| create a reusable variable | browser journey X2.1, step 1 (screenshot 42) | **met** |
| it survives a reload | X2.1: a full page reload, the draft is still there | **met** |
| compose it into an application profile | X2.1, steps 2 and 4 (43, 44, 48) | **met** — and the profile cannot be submitted while the variable is only a draft |
| a named AND / OR / NOT condition | X2.1, step 5 (49): `"Is ILP" and not "NFTF applies" and (Senior applicant is yes or Replacement applies is yes)`, nested, reading two saved conditions and two variables, tested live by the server | **met** |
| three-person publication | X2.1: three browser sessions, three signed-in people; a return with a reason on the way (45, 46, 47, 50) | **met**, enforced by the server and by the table |
| reuse of the exact published version in the Designer | X2.1, step 6 (51): the requirement reads "saved condition · version 1" | **met**; the policy itself stays in the tab, and says so |
| historical versions preserved | X2.1 (profile version 1 kept as "earlier"); backend test on documents, manifests, pins and fingerprints | **met** |
| market isolation | backend tests (two markets, service and table) | **met on the server**; not shown in the browser, where no second-market applicability user exists |
| complete audit trail | X2.1 history panels; backend test of the event sequence and the audit chain, including refusals | **met** |

## 2. Deliverables

| # | Asked | Where |
|---|---|---|
| 1 | APPL-X1R formal acceptance entry | decision register D-393 |
| 2 | Updated owner decisions and contracts | D-394 … D-396; `56_…` §14 stands; `04_…` §24 |
| 3 | APPL-X2 architecture / design | `60_…` §1–6, §8 |
| 4 | Migration specification | `60_…` §7; `Call360-backend/migrations/versions/0038_applicability_library.py` |
| 5–7 | Working persisted Variable Library, Application Profiles, Condition Lab | §4 below; journeys X2.1, X2.2 |
| 8 | Genuine server-side maker / checker / publisher governance | §3 |
| 9 | API and OpenAPI | `60_…` §5; `contracts/generated/openapi.json`, SHA-256 in §7 |
| 10 | Actual browser screenshots | `evidence/APPL-X2/screens/` (§8) |
| 11 | Graph and header refinement evidence | §5 |
| 12 | Security, accessibility, market isolation | §3, §6 |
| 13 | Complete regression | §7 |
| 14 | Data integrity and rollback | `60_…` §7; §7 below |
| 15 | Updated APPL-X3 … X6 roadmap | `58_…` |
| 16 | Decision register, index, hand-off | D-393 … D-400; README; `SESSION_HANDOFF.md` |

## 3. Governance, security and isolation — what the tests prove

`Call360-backend/tests/test_applicability_library.py`, 15 tests on the test schema, with **least-privilege** people:
an author who may only draft and submit, a checker who may only decide, a publisher who may only publish, a reader,
and one person holding all four permissions whom only the identity rules can stop.

| Required | Result |
|---|---|
| Draft CRUD; reload | a draft is stored, read back by another person, listed; unknown fields are dropped, never stored |
| Optimistic concurrency | the second save on the same revision is refused (409, who saved, current revision); nothing is overwritten |
| Duplicate identity | refused whatever the letter case; the same code is free for another kind and another market |
| Type validation | no type, enum without values, money without currency, duplicate values, unknown source status, a derived variable that is not yes / no, a yes / no test on money: all blockers |
| Source mapping metadata | stored and published exactly as stated; **NFTF and riders say "not mapped"; nothing is invented**; a derived variable's source is "derived" |
| Profile composition | inherited variables, required / optional, constraints; published profiles pin variables and profiles and hold no copy of a variable |
| Invalid inheritance | unknown parent, itself, an unpublished variable, a required variable it does not carry, two extensions that cannot both hold |
| Dependency cycles | an item cannot depend on itself; a circle between two drafts cannot be submitted; the table makes a published cycle impossible |
| Unpublished dependency | refused at submission, for variables, profiles and conditions |
| Published version immutable | document, manifest, fingerprints, who decided and who published; status only forwards; no delete — refused by the table for twelve direct SQL attempts |
| Three-person governance | self-approval, publication by the submitter and by the approver refused **although they hold the permission**; refused again by `CHECK` constraints; each refusal recorded |
| A change to a shared variable | version 2 of a variable changes no published profile or condition: same rows, same pins, same fingerprints; the item says a newer version exists and does not move |
| Market isolation | another market's item answers 404 on every operation; its workspace and test answer 403; a reference to it is "does not exist in this market"; the table refuses a pin across markets even on a published version |
| Permission denial | no session 401; ADMIN, USER, SC checker and holders of `survey.*` / `script.*` 403; each permission opens only its own operations; a write without the CSRF token refused |
| Audit history | the exact event sequence of a full lifecycle with a return and three refusals; the audit chain holds the same, with outcome `DENIED` for the refusals |
| Deterministic fingerprints | independent of key order; the manifest fingerprint recomputed from its parts |
| Outside-profile facts (D-394) | a given fact outside the profile is read and marked; a registered variable the policy does not read is not evaluated; an arbitrary request field is never a fact; a type-invalid value is `INVALID` |
| Exact reuse | a prototype policy naming version 1 and version 2 of one condition evaluates each exactly as published |
| Showcase library | 26 items published through the governed API by three people; idempotent; a conflict is reported and left alone |
| Migration | `60_…` §7 |

**No standing role gained a permission.** The four permissions are held by no role after the migration (tested).
The test identities exist only in the test schema, through test-only roles.

## 4. The three screens on the persisted library

| | In the tab (APPL-X1R, and development today) | Persisted (`VITE_APPLICABILITY_LIBRARY=1`) |
|---|---|---|
| Where items come from | built-in synthetic example | the server; the example is not loaded |
| Save | implicit | explicit, with the revision it was opened at |
| "Publish" | one click, simulated | submit → another person approves or returns → a third publishes |
| States shown | draft / published | Saving · Draft saved · Unsaved · Not saved, someone else saved first · Submitted · Approved · Returned (with the reason) · Published |
| Concurrent edits | none | refused, with two explicit choices; unsaved work is never replaced by a refresh (X2.2, screenshot 52) |
| History | none | every version with its exact pins and fingerprint; every event with who and when |
| Without permission | — | the library is closed and the screen says so; nothing stands in for it (X2.3, screenshot 53) |

Preserved: type-aware creation, enum and multi-enum values, typed comparisons, money and currency rules, source
status, boolean derived variables, search and filters, where-used, the draft-against-published comparison, inline
creation of a variable or a condition from the Designer without leaving the requirement being edited (journey
X1R.5 still passes, and the variable it creates is now a saved draft).

**The policy and scenario store is unchanged and labelled.** The header says "Draft v1 · in this tab only"; the
designer's button is "Keep draft in this tab" and its state "Draft kept in this tab only"; one control explains
where each kind of thing is kept. No label implies a policy survives a reload.

## 5. Targeted UX fixes

### 5.1 Graph focus — a confirmed defect, fixed

The 100-requirement focused screenshot of APPL-X1R showed an almost empty canvas. **It was a defect, not an
intended state.** Cause: the whole policy was laid out first (a plane thousands of pixels tall) and then most of
it was hidden, so the few nodes of a neighbourhood stayed scattered across that plane; and the view was not
re-fitted when the selection changed through "Go to a requirement".

Fix (`DesignerCanvas.tsx`): only what is shown is laid out; after every change of what is shown the view is fitted
(twice, so a slow first paint cannot leave the old position), and if even the smallest zoom cannot hold everything
the selection itself is centred.

Browser assertions (journey X2.6, at 20, 50 and 100 requirements), measured from the DOM:

| Assertion | 20 | 50 | 100 |
|---|---|---|---|
| overview: every node inside the canvas viewport | yes | yes | yes |
| "Go to a requirement": the selected node inside the viewport | yes | yes | yes |
| … and its whole neighbourhood inside the viewport, at 0.45 zoom or more | yes | yes | yes |
| (measured zoom for that neighbourhood beside the open inspector) | about 0.5 | about 0.5 | about 0.5 |
| a survey's neighbourhood: the selected survey inside the viewport | yes | yes | yes |
| … and all of it inside the viewport | yes | not asserted | not asserted |
| search: hits brought into view | yes | yes | yes |

Honest limits: a requirement's neighbourhood is five columns wide and fits beside the open inspector at about half
size — readable, not comfortable. A survey's neighbourhood in the 100-requirement example is twenty requirements
tall; the selection is in view and the rest is reached by zooming or scrolling the canvas. Screenshots 57, 58.

### 5.2 Header density

| Before (APPL-X1R, 1440) | Now |
|---|---|
| policy switch · "Prototype · nothing is saved" · "N published in Survey Studio" · Undo · Redo (labelled) · "Acting as Maya · Maker" · "Search or jump to… ⌘K" | policy switch **with its state beside it** ("Draft v1 · in this tab only") · one status control · undo / redo as two icons · "Maya · Maker" · "Search ⌘K" |

The two status chips became one control that opens to say where variables, profiles and conditions are kept, where
policies and scenarios are kept, and what is read from Survey Studio, with "Read again from Call360". Asserted in
X2.7: at most four controls, one line, under seventy characters. Screenshots 40, 59.

### 5.3 Other fixes made on the way

* Nested condition lines were too narrow to read: the move-up / move-down tools reserved a column at every level
  of nesting. They now float over the line's corner.
* A result that did not decide the outcome was faded below a readable contrast; it is now marked by its outline.
* A saved document comes back from the database with its keys reordered; the lab compared text and believed a
  just-saved condition was still changed. Comparisons are now independent of key order.

### 5.4 Interactions — first automated coverage

| | Journey X2.5 |
|---|---|
| requirement order by keyboard | "move down" with Enter, "move up" with Space |
| delivery order by keyboard | Enter on "later" |
| delivery order by dragging | one row dropped on another |
| requirement order by dragging | by the grip; then undone |
| palette to requirement | a saved condition dragged onto a card joins its condition |

### 5.5 Adopting a newer published survey version

Journey X2.4, on an isolated fixture survey `S-APPL-TEST-ADOPT` published through Survey Studio's governed API by
three people (`scripts/appl_fixture_survey.py`); **the showcase surveys were not touched**. With the policy open,
Survey Studio publishes version 2: the reference stays on 1.0 with the same fingerprint; "Version 2.0 is now
published. This requirement stays on 1.0 until you adopt it." is offered; adopting moves it to 2.0 with a different
fingerprint; undo returns it to 1.0. Screenshots 54, 55. A superseded survey version keeps its content and is
marked `SUPERSEDED` by Survey Studio.

## 6. Integration preserved

| | |
|---|---|
| The five showcase surveys and the shared module | not modified by any code or test of this checkpoint. In development they are as published in APPL-X1R (nothing ran against development) |
| Real published surveys in the picker; no fake catalogue | unchanged; journeys X1R.1 – X1R.3 pass |
| Navigation both ways, exact version previews | journeys X1R.2, X1R.8, X1R.9 pass |
| The APPL-X1R demonstration journeys | all nine pass, now on the persisted library |
| Evaluator | not changed. Its 21 tests are unchanged |

## 7. Regression

Run on 2026-11-23 / 24 against the isolated test schema. Outputs: `docs/acceptance/evidence/APPL-X2/`.

| Check | Result |
|---|---|
| Backend suite | **1,065 passed, 0 failed** — 1,049 before, plus 15 of the library and 1 of the fixture survey |
| Golden fixtures | the 82 expected runs and 14 expected plans pass; **no fixture or expectation file is modified** |
| Evaluator tests | the 21 tests of `test_survey_applicability.py` pass **unchanged**; the evaluator was not edited |
| Backend lint, format, types | clean (`ruff` on 277 files, `mypy` on 134) |
| OpenAPI | 14 operations and 21 schemas added, nothing else changed; SHA-256 `a3d162c282c1d67ba82530424a97210730c734d99d69bcc35c6186b793663d17`; the frontend client matches |
| Frontend unit tests | **636 passed** |
| Frontend types, lint, build | clean |
| Playwright — applicability | **16 passed**: the nine APPL-X1R journeys and X2.1 – X2.7 |
| Playwright — persisted | **34 passed**, unchanged |
| Playwright — prototype | **13 passed**, unchanged |
| Playwright — standard | **33 passed**, unchanged (the voice test passed in this run) |
| Accessibility | no serious or critical violation (axe, WCAG 2.2 AA rules) on the screens of APPL-X1R and on a variable with its history, the "where things are kept" control, a profile and a condition. Not a screen-reader test |
| Widths | no sideways overflow at 1280, 900 and 390 on the three library screens and on the screens of APPL-X1R |
| Specs validators | pass |
| Development | read-only check after everything: schema `call360` at `0037_shared_rule_services`, 0 applicability tables, 0 applicability permissions, library setting off; the development backend answers ready |

Honest notes on the runs:

* **Existing tests changed, and why.** Moving the head to `0038` required it: the tests that name the head
  revision (in nine files) now name `0038`; the contract-size test counts the 14 operations and 21 schemas; and the older
  migration tests (in eight files) that compare the set of tables after a downgrade now subtract the four applicability tables
  (`tests/support.py::APPLICABILITY_TABLES`), because `0038` sits above the revision each of them tests. One of
  them (SHARED-1) also learned that an empty `0038` rolls back before `0037` refuses. No assertion about behaviour
  was weakened. The table catalogue (`app/domain/catalog.py`) lists the four tables.
* **The first full backend run had 20 failures**, all of that kind: the expectations above had not been updated,
  and one failing migration test left the test schema at an earlier revision, which made the tests after it fail
  too. After the updates the suite passed whole.
* **Order of runs.** The backend suite, the persisted, prototype and standard browser suites ran before my last two
  frontend edits (the title size and the wording of the conflict message — one stylesheet rule scoped to
  applicability classes and one file of the applicability feature). The applicability suite, the unit tests, types,
  lint and build were run again after them.
* The applicability journey X1R.5 creates a variable inside the Designer; with the library on it is now saved as a
  draft in the test schema. The journeys run in one fixed order against one schema and depend on it.
* An `npx esbuild` call fetched the bundler from the public registry to export the showcase definitions from the
  frontend's example into `scripts/appl_library_seed.json`. Nothing was added to either project's dependencies.

## 8. Screenshots (`evidence/APPL-X2/screens/`)

Taken in the isolated test environment by the browser journeys.

| | |
|---|---|
| 40, 59 | the header at 1440; where things are kept |
| 41 | Variable Library on the persisted, published showcase library, with versions and history |
| 42 | a new variable saved as a draft, after a reload |
| 43, 44 | a profile with an unsaved change; saved, and blocked by the unpublished variable |
| 45, 46, 47 | submitted (the author cannot approve); returned with a reason; published by three people |
| 48 | profile version 2 pinning the variable's exact version; version 1 kept |
| 49, 50 | Condition Lab: AND / OR / NOT saved as a draft; published with its exact pins |
| 51 | the Designer reusing the published condition; the policy "in this tab only" |
| 52 | two people on one draft: refused, nothing overwritten |
| 53 | the library closed to a person without the permissions |
| 54, 55 | a newer survey version offered, not applied; adopted and undone |
| 56 | ordering by keyboard and by dragging |
| 57, 58 | graph focus at 20, 50 and 100 requirements |
| 60 | the library at phone width |
| 01 – 37 | the APPL-X1R journeys, re-taken on the persisted library |

## 9. The voice timing flake of APPL-X1R

`e2e/voice.spec.ts`, "S1-B persistence", failed once in the APPL-X1R regression: the stored session record still
read "Live" after Stop. **Cause established by reading the code; not reproduced, and not fixed** — it is in Voice
Studio, outside this checkpoint.

`src/features/voice/VoiceSessionTimeline.tsx`: when a session stops being live the component schedules **one**
final re-read 400 ms later. The effect that schedules it depends on the query object, which is a new object
whenever the query's state changes. If the last two-second poll completes inside those 400 ms, the effect is
cleaned up — cancelling the timer — and runs again with "was live" already false, so it schedules nothing. Polling
has stopped, so the record stays on the last polled state, "Live", until the page is reloaded. Whether a run hits
it depends on where Stop falls in the two-second polling cycle, which is why it is intermittent.

Proposed fix, for a separately authorised change: keep the timer in a ref (or depend on the stable `refetch`, not
on the query object), or keep polling until the stored status is no longer live. **Retained as an open reliability
issue (D-399).** In this checkpoint's regression the test passed (once; that proves nothing about an intermittent fault).

## 10. Critique and open points

* **Two "saves" in one workspace.** Library items are saved in Call360; policies are kept in the tab. The labels are
  truthful, but the difference is a real cognitive cost until APPL-X3 removes it.
* **Draft items in a policy.** A policy draft may read a draft variable or condition (needed to design before
  publishing). The designer does not yet mark such a requirement, and the simulated policy submission does not block
  on it. This belongs with real policy governance (APPL-X4); recorded as D-398.
* **The 100-requirement example shows "20 to fix".** That is correct under AP-2: the generated example lets several
  requirements select one survey without a shared-delivery statement. It demonstrates that validation scales; it is
  not a tidy showcase. The generator was not changed.
* **Market isolation is not shown in the browser**, only on the server.
* **Profiles are edited in place** and saved with one button; there is no per-field undo against the server, only
  the tab's undo.
* **Editable titles were drawn at body size since APPL-X1** (a Survey Studio rule for inputs outranked them). Found from the screenshots of this checkpoint and fixed.
* **The condition builder is still cramped** in the three-column lab at 1440 when groups are nested twice.
* Refresh after someone else acts is on returning to the tab or by "Read again"; there is no live push.

## 11. Not done, and not authorised

`0038` is not applied to development. No development identity was created and no development permission granted.
The showcase library was not published in development. No policy or scenario persistence. No operational
assignment, voice integration, Script Studio change or legacy retirement. APPL-X3, APP-1a, OPS-1 and VOICE-1 were
not started. No commit, no push.

## 12. What the owner is asked to decide

1. Review and acceptance of APPL-X2 on the test schema.
2. Whether to authorise, for **local development only**: applying `0038` (after a verified backup), switching the
   library on, creating three development identities that each hold only their part of the applicability
   permissions, and publishing the showcase library through the governed API (`60_…` §7.1). Until then the
   persisted library can be seen only in the test environment and in the screenshots.
3. The choices in D-397 and the open points D-398 … D-400.
